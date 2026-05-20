"""
Professional Diabetes Risk Assessment App
- Modern glassmorphism UI design
- Animated components and smooth transitions
- Professional dashboard layout
- Interactive visualizations
- Advanced styling and custom components
"""

import time
import logging
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from backend import (
    ensure_dataset_repo,
    fetch_remote_logs_via_api,
    load_resources,
    validate_inputs,
    predict_diabetes,
    log_prediction_remote_only,
)
from ui import (
    setup_page,
    create_hero_section,
    create_risk_visualization,
    create_feature_importance_chart,
    create_stats_cards,
    render_footer,
)

# -----------------------
# Configuration & Logging
# -----------------------
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
def main():
    # Initialize session state
    if "repo_setup" not in st.session_state:
        ensure_dataset_repo()
        st.session_state.repo_setup = True

    if "show_results" not in st.session_state:
        st.session_state.show_results = False

    setup_page()

    # Hero Section
    create_hero_section()

    # Load model resources
    model, scaler, medians = load_resources()
    if model is None:
        st.markdown("""
        <div class="error-alert">
            <h3>⚠️ Model Resources Not Found</h3>
            <p>Please ensure model files are properly loaded in the models directory.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # Load and display statistics
    logs_df = fetch_remote_logs_via_api(retries=2, delay=0.3)

    # Statistics Dashboard
    st.markdown("## 📊 Analytics Dashboard")
    create_stats_cards(logs_df)

    # Main Layout
    col1, col2 = st.columns([1, 2])

    # Sidebar Input Panel
    with col1:
        st.markdown("""
        <div class="sidebar-header">
            <h2 style="color: white; margin: 0;">🏥 Patient Assessment</h2>
            <p style="color: rgba(255,255,255,0.7); margin: 0.5rem 0 0 0;">Enter patient information below</p>
        </div>
        """, unsafe_allow_html=True)

        # Input Form
        with st.form("assessment_form", clear_on_submit=False):
            name = st.text_input(
                "👤 Patient Name", placeholder="Enter patient name (optional)")

            st.markdown("#### 📋 Medical Information")
            pregnancies = st.number_input(
                "🤱 Number of Pregnancies", 0, 20, value=0)
            glucose = st.number_input(
                "🍭 Glucose Level (mg/dL)", 0, 300, value=120)
            bloodpressure = st.number_input(
                "🩺 Blood Pressure (mmHg)", 0, 200, value=80)
            skinthickness = st.number_input(
                "📏 Skin Thickness (mm)", 0, 100, value=20)
            insulin = st.number_input(
                "💉 Insulin Level (μU/mL)", 0, 500, value=0)
            bmi = st.number_input("⚖️ BMI", 0.0, 70.0,
                                  value=25.0, format="%.1f")
            diabetespedigree = st.number_input(
                "🧬 Diabetes Pedigree Function", 0.0, 3.0, value=0.5, format="%.3f")
            age = st.number_input("🎂 Age (years)", 1, 120, value=30)

            submitted = st.form_submit_button(
                "🔬 Analyze Risk", use_container_width=True)

            if submitted:
                inputs = {
                    "pregnancies": pregnancies, "glucose": glucose, "bloodpressure": bloodpressure,
                    "skinthickness": skinthickness, "insulin": insulin, "bmi": bmi,
                    "diabetespedigree": diabetespedigree, "age": age
                }

                # Validate inputs
                errors = validate_inputs(**inputs)
                if errors:
                    st.markdown("""
                    <div class="error-alert">
                        <h4>❌ Input Validation Errors</h4>
                    """, unsafe_allow_html=True)
                    for error in errors:
                        st.write(f"• {error}")
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    # Show loading animation
                    with st.spinner("🔄 Analyzing patient data..."):
                        time.sleep(1)  # Simulate processing time
                        pred, prob = predict_diabetes(
                            model, scaler, medians, **inputs)

                        if pred is not None:
                            # Log the prediction
                            log_prediction_remote_only(
                                name, inputs, pred, prob)
                            st.session_state.show_results = True
                            st.session_state.last_prediction = {
                                "pred": pred, "prob": prob, "name": name}

    # Results Panel
    with col2:
        if st.session_state.show_results and "last_prediction" in st.session_state:
            result = st.session_state.last_prediction
            pred, prob, patient_name = result["pred"], result["prob"], result["name"]

            # Risk Assessment Card
            risk_class = "risk-card-high" if pred else "risk-card-low"
            risk_icon = "🚨" if pred else "✅"
            risk_text = "High Diabetes Risk" if pred else "Low Diabetes Risk"
            risk_color = "#ff6b6b" if pred else "#51cf66"

            st.markdown(f"""
            <div class="{risk_class}">
                <h2 class="risk-title">{risk_icon} {risk_text}</h2>
                <div class="risk-score">{prob:.1f}%</div>
                <p class="risk-subtitle">Patient: {patient_name or 'Anonymous'}</p>
                <p style="font-size: 0.9rem; opacity: 0.8;">
                    Assessment completed on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Risk Visualization
            st.markdown("#### 📈 Risk Analysis")
            st.markdown('<div class="chart-container">',
                        unsafe_allow_html=True)
            fig = create_risk_visualization(prob)
            st.plotly_chart(fig, use_container_width=True,
                            config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

            # Recommendations
            st.markdown("#### 💡 Clinical Recommendations")
            if pred:
                st.markdown("""
                <div class="error-alert">
                    <h4>⚠️ High Risk - Immediate Action Recommended</h4>
                    <ul style="margin: 1rem 0;">
                        <li>Schedule appointment with healthcare provider immediately</li>
                        <li>Consider HbA1c and fasting glucose tests</li>
                        <li>Implement lifestyle modifications (diet & exercise)</li>
                        <li>Monitor blood glucose levels regularly</li>
                        <li>Consider diabetes education programs</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="success-alert">
                    <h4>✅ Low Risk - Preventive Care Recommended</h4>
                    <ul style="margin: 1rem 0;">
                        <li>Maintain healthy lifestyle habits</li>
                        <li>Regular health screenings as recommended</li>
                        <li>Continue balanced diet and regular exercise</li>
                        <li>Annual diabetes screening</li>
                        <li>Monitor weight and blood pressure</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

        else:
            # Default dashboard view
            st.markdown("#### 🎯 AI-Powered Risk Assessment")
            st.markdown("""
            <div class="info-alert">
                <h4>🔬 Advanced Machine Learning Analysis</h4>
                <p>Our state-of-the-art machine learning model analyzes multiple health parameters to provide accurate diabetes risk predictions. Enter patient information in the form to begin assessment.</p>
            </div>
            """, unsafe_allow_html=True)

            # Feature Importance Chart
            st.markdown("#### 📊 Model Feature Importance")
            st.markdown('<div class="chart-container">',
                        unsafe_allow_html=True)
            fig_importance = create_feature_importance_chart()
            st.plotly_chart(fig_importance, use_container_width=True, config={
                            'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

    # Analytics Section
    st.markdown("---")
    st.markdown("## 📈 Recent Assessments & Analytics")

    if not logs_df.empty:
        # Recent predictions table with enhanced styling
        st.markdown("#### 🕒 Latest Predictions")

        # Process logs for better display
        display_logs = logs_df.sort_values(
            "timestamp", ascending=False).head(10).copy()

        # Add risk level column
        display_logs['Risk Level'] = display_logs['prediction'].apply(
            lambda x: '🚨 High Risk' if x == 'Positive' else '✅ Low Risk'
        )

        # Reorder columns for better presentation
        display_columns = ['timestamp', 'name', 'age',
                           'bmi', 'glucose', 'Risk Level', 'probability']
        display_logs_subset = display_logs[display_columns].copy()

        # Rename columns for better readability
        display_logs_subset.columns = [
            'Timestamp', 'Patient', 'Age', 'BMI', 'Glucose', 'Risk Level', 'Probability']

        st.dataframe(
            display_logs_subset,
            use_container_width=True,
            height=400
        )


# Analytics Charts
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📊 Risk Distribution")
            if len(logs_df) > 0:
                risk_counts = logs_df['prediction'].value_counts()
                fig_pie = px.pie(
                    values=risk_counts.values,
                    names=['Low Risk' if x ==
                           'Negative' else 'High Risk' for x in risk_counts.index],
                    color_discrete_sequence=['#51cf66', '#ff6b6b'],
                    title="Risk Assessment Distribution"
                )
                fig_pie.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': 'white', 'family': 'Inter'},
                    title={'font': {'color': 'white', 'size': 16}}
                )
                st.plotly_chart(fig_pie, use_container_width=True,
                                config={'displayModeBar': False})


        with col2:
            st.markdown("#### 📈 Age vs Risk Analysis")
            if len(logs_df) > 5:  # Only show if we have enough data
                try:
                    # Convert age to numeric and create age groups
                    logs_df_clean = logs_df.copy()
                    logs_df_clean['age_numeric'] = pd.to_numeric(
                        logs_df_clean['age'], errors='coerce')
                    # Convert probability column - handle both string and numeric formats

                    def clean_probability(prob_str):
                        try:
                            if isinstance(prob_str, str):
                                # Remove '%' symbol if present and convert to float
                                return float(prob_str.replace('%', ''))
                            else:
                                return float(prob_str)
                        except (ValueError, TypeError):
                            return None
                    logs_df_clean['prob_numeric'] = logs_df_clean['probability'].apply(
                        clean_probability)
                    # Remove rows with missing age or probability data
                    logs_df_clean = logs_df_clean.dropna(
                        subset=['age_numeric', 'prob_numeric'])
                    if len(logs_df_clean) > 0:
                        fig_scatter = px.scatter(
                            logs_df_clean,
                            x='age_numeric',
                            y='prob_numeric',
                            color='prediction',
                            color_discrete_map={
                                'Negative': '#51cf66', 'Positive': '#ff6b6b'},
                            title="Age vs Diabetes Risk Probability",
                            labels={
                                'age_numeric': 'Age (years)',
                                'prob_numeric': 'Risk Probability (%)',
                                'prediction': 'Risk Level'
                            },
                            hover_data={
                                'age_numeric': ':.0f',
                                'prob_numeric': ':.1f',
                                'prediction': True
                            }
                        )
                        fig_scatter.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font={'color': 'white', 'family': 'Inter'},
                            title={'font': {'color': 'white',
                                            'size': 16}, 'x': 0.5},
                            xaxis={
                                'title': {'font': {'color': 'white'}},
                                'tickfont': {'color': 'white'},
                                'gridcolor': 'rgba(255,255,255,0.1)',
                                'showgrid': True
                            },
                            yaxis={
                                'title': {'font': {'color': 'white'}},
                                'tickfont': {'color': 'white'},
                                'gridcolor': 'rgba(255,255,255,0.1)',
                                'showgrid': True,
                                # Set y-axis range from 0 to 100%
                                'range': [0, 100]
                            },
                            legend={
                                'font': {'color': 'white'},
                                'bgcolor': 'rgba(255,255,255,0.1)',
                                'bordercolor': 'rgba(255,255,255,0.2)',
                                'borderwidth': 1
                            },
                            height=400
                        )
                        # Add trend line for better visualization
                        try:
                            trend_fig = px.scatter(
                                logs_df_clean,
                                x='age_numeric',
                                y='prob_numeric',
                                trendline="lowess",
                                color_discrete_sequence=[
                                    'rgba(255,255,255,0.3)']
                            )
                            # Add only the trend line traces
                            for trace in trend_fig.data:
                                if trace.mode == 'lines':  # Only add trendline, not scatter points
                                    fig_scatter.add_trace(trace)
                        except:
                            pass  # Skip trend line if it fails
                        st.plotly_chart(fig_scatter, use_container_width=True, config={
                                        'displayModeBar': False})
                    else:
                        st.info(
                            "📊 No valid age and probability data found for analysis.")
                except Exception as e:
                    st.error(f"📊 Error creating age analysis: {str(e)}")
                    # Show debug information to help troubleshoot
                    if not logs_df.empty:
                        st.write("Sample data for debugging:")
                        st.write(logs_df[['age', 'probability']].head())
            else:
                st.info(
                    "📊 Age analysis will be available with more data points (need at least 6 records).")

        # Advanced Analytics
        if len(logs_df) > 20:
            st.markdown("#### 🔍 Advanced Analytics")

            col1, col2, col3 = st.columns(3)

            try:
                # Calculate advanced metrics
                logs_df['age_numeric'] = pd.to_numeric(
                    logs_df['age'], errors='coerce')
                logs_df['bmi_numeric'] = pd.to_numeric(
                    logs_df['bmi'], errors='coerce')
                logs_df['glucose_numeric'] = pd.to_numeric(
                    logs_df['glucose'], errors='coerce')

                high_risk_avg_age = logs_df[logs_df['prediction']
                                            == 'Positive']['age_numeric'].mean()
                low_risk_avg_age = logs_df[logs_df['prediction']
                                           == 'Negative']['age_numeric'].mean()

                high_risk_avg_bmi = logs_df[logs_df['prediction']
                                            == 'Positive']['bmi_numeric'].mean()
                low_risk_avg_bmi = logs_df[logs_df['prediction']
                                           == 'Negative']['bmi_numeric'].mean()

                high_risk_avg_glucose = logs_df[logs_df['prediction']
                                                == 'Positive']['glucose_numeric'].mean()
                low_risk_avg_glucose = logs_df[logs_df['prediction']
                                               == 'Negative']['glucose_numeric'].mean()

                with col1:
                    st.markdown(f"""
                    <div class="metric-container">
                        <h4 style="color: white; margin-bottom: 1rem;">👥 Age Analysis</h4>
                        <p style="color: #ff6b6b;">High Risk Avg: {high_risk_avg_age:.1f} years</p>
                        <p style="color: #51cf66;">Low Risk Avg: {low_risk_avg_age:.1f} years</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="metric-container">
                        <h4 style="color: white; margin-bottom: 1rem;">⚖️ BMI Analysis</h4>
                        <p style="color: #ff6b6b;">High Risk Avg: {high_risk_avg_bmi:.1f}</p>
                        <p style="color: #51cf66;">Low Risk Avg: {low_risk_avg_bmi:.1f}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                    <div class="metric-container">
                        <h4 style="color: white; margin-bottom: 1rem;">🍭 Glucose Analysis</h4>
                        <p style="color: #ff6b6b;">High Risk Avg: {high_risk_avg_glucose:.1f} mg/dL</p>
                        <p style="color: #51cf66;">Low Risk Avg: {low_risk_avg_glucose:.1f} mg/dL</p>
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                pass

    else:
        st.markdown("""
        <div class="info-alert">
            <h4>📊 No Assessment Data Available</h4>
            <p>Complete your first risk assessment to see analytics and trends. The system will automatically track and analyze prediction patterns over time.</p>
        </div>
        """, unsafe_allow_html=True)

    render_footer()


if __name__ == "__main__":
    main()
