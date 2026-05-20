import os
import time
import tempfile
import logging
from datetime import datetime
from pathlib import Path
from functools import lru_cache

import pandas as pd
import numpy as np
import joblib
from huggingface_hub import HfApi, hf_hub_download, create_repo

logger = logging.getLogger(__name__)

MODEL_DIR = Path("models")
MODEL_FILE = MODEL_DIR / "diabetes.sav"
SCALER_FILE = MODEL_DIR / "scaler.sav"
MEDIANS_FILE = MODEL_DIR / "medians.sav"

HF_USERNAME = "LovnishVerma"
DATASET_REPO = f"{HF_USERNAME}/diabetes-logs"
HF_TOKEN = os.getenv("HF_TOKEN")


def ensure_dataset_repo():
    try:
        create_repo(DATASET_REPO, token=HF_TOKEN, private=False,
                    repo_type="dataset", exist_ok=True)
        api = HfApi()
        api.upload_file(
            path_or_fileobj="# Diabetes Risk Assessment Logs\nAuto-updated by Streamlit app.".encode(),
            path_in_repo="README.md",
            repo_id=DATASET_REPO,
            token=HF_TOKEN,
            repo_type="dataset",
        )
    except Exception as e:
        logger.info(f"ensure_dataset_repo: {e}")


def fetch_remote_logs_via_api(retries: int = 1, delay: float = 0.5) -> pd.DataFrame:
    if HF_TOKEN:
        for attempt in range(retries):
            try:
                local = hf_hub_download(
                    repo_id=DATASET_REPO,
                    filename="audit_log.csv",
                    repo_type="dataset",
                    token=HF_TOKEN,
                )
                return pd.read_csv(local, dtype=str)
            except Exception as e:
                time.sleep(delay)

    try:
        url = f"https://huggingface.co/datasets/{DATASET_REPO}/raw/main/audit_log.csv"
        return pd.read_csv(url, dtype=str)
    except Exception:
        return pd.DataFrame()


def upload_merged_logs(tmp_csv_path: str):
    if not HF_TOKEN:
        raise RuntimeError(
            "HF_TOKEN is not set — cannot upload logs to Hugging Face.")

    api = HfApi()
    api.upload_file(
        path_or_fileobj=str(tmp_csv_path),
        path_in_repo="audit_log.csv",
        repo_id=DATASET_REPO,
        repo_type="dataset",
        token=HF_TOKEN,
        commit_message=f"Update audit_log {datetime.utcnow().isoformat()}",
        create_pr=False,
    )


@lru_cache(maxsize=1)
def load_resources():
    try:
        model = joblib.load(MODEL_FILE)
        scaler = joblib.load(SCALER_FILE)
        medians = joblib.load(MEDIANS_FILE)
        required = {"Pregnancies", "Glucose", "BloodPressure",
                    "SkinThickness", "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"}
        if not required.issubset(set(medians.keys())):
            raise ValueError("medians object missing required keys")
        return model, scaler, medians
    except Exception:
        return None, None, None


def validate_inputs(pregnancies, glucose, bloodpressure, skinthickness, insulin, bmi, diabetespedigree, age):
    errors = []
    if not (0 < glucose <= 300):
        errors.append("Glucose must be 1–300 mg/dL.")
    if not (0 < bloodpressure <= 200):
        errors.append("Blood pressure must be 1–200 mmHg.")
    if not (0 < bmi <= 70):
        errors.append("BMI must be 1–70.")
    if not (0 < age <= 120):
        errors.append("Age must be 1–120.")
    if pregnancies > 20:
        errors.append("Pregnancies cannot exceed 20.")
    if age < 15 and pregnancies > 0:
        errors.append("Age too low for pregnancies.")
    return errors


def predict_diabetes(model, scaler, medians, pregnancies, glucose, bloodpressure, skinthickness, insulin, bmi, diabetespedigree, age):
    df = pd.DataFrame([{
        "Pregnancies": pregnancies,
        "Glucose": glucose,
        "BloodPressure": bloodpressure,
        "SkinThickness": skinthickness,
        "Insulin": insulin,
        "BMI": bmi,
        "DiabetesPedigreeFunction": diabetespedigree,
        "Age": age
    }])

    zero_cols = ["Glucose", "BloodPressure", "SkinThickness", "Insulin", "BMI"]
    df[zero_cols] = df[zero_cols].replace(0, np.nan)
    df = df.fillna(medians)
    scaled = scaler.transform(df)
    pred = model.predict(scaled)[0]
    prob = model.predict_proba(scaled)[0][1] * 100
    return bool(pred), float(prob)


def log_prediction_remote_only(name: str, inputs: dict, prediction: bool, probability: float):
    logs = fetch_remote_logs_via_api(retries=2, delay=0.3)
    new_row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "name": name or "Anonymous",
        "pregnancies": inputs.get("pregnancies"),
        "glucose": inputs.get("glucose"),
        "bloodpressure": inputs.get("bloodpressure"),
        "skinthickness": inputs.get("skinthickness"),
        "insulin": inputs.get("insulin"),
        "bmi": inputs.get("bmi"),
        "diabetespedigree": inputs.get("diabetespedigree"),
        "age": inputs.get("age"),
        "prediction": "Positive" if prediction else "Negative",
        "probability": f"{probability:.1f}%",
        "region": "India",
    }
    merged = pd.concat([logs, pd.DataFrame([new_row])], ignore_index=True) if not logs.empty else pd.DataFrame([new_row])
    with tempfile.NamedTemporaryFile(mode="w", suffix='.csv', delete=False) as tmpf:
        tmp_path = Path(tmpf.name)
        merged.to_csv(tmp_path, index=False)

    if HF_TOKEN:
        upload_merged_logs(tmp_path)

    try:
        tmp_path.unlink()
    except Exception:
        pass
