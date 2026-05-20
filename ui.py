import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def setup_page():
    st.set_page_config(
        page_title="DiabetesAI Pro",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* Global Styles */
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Inter', sans-serif;
        }

        /* Main container with glassmorphism */
        .main-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        }

        /* Hero Section */
        .hero-section {
            text-align: center;
            padding: 3rem 1rem;
            background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
            border-radius: 25px;
            margin-bottom: 2rem;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255,255,255,0.2);
        }

        .hero-title {
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .hero-subtitle {
            font-size: 1.3rem;
            color: rgba(255,255,255,0.8);
            font-weight: 400;
            margin-bottom: 1rem;
        }

        .hero-badge {
            display: inline-block;
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 0.5rem 1.5rem;
            border-radius: 25px;
            font-weight: 600;
            font-size: 0.9rem;
            box-shadow: 0 4px 15px rgba(238, 90, 36, 0.4);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        /* Sidebar Styling */
        .css-1d391kg {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.2);
        }

        /* Input Styling */
        .stNumberInput > div > div > input {
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            color: white !important;
            backdrop-filter: blur(10px);
        }

        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            color: white !important;
            backdrop-filter: blur(10px);
        }

        /* Input placeholder styling */
        .stTextInput > div > div > input::placeholder {
            color: rgba(255, 255, 255, 0.6) !important;
        }

        .stNumberInput > div > div > input::placeholder {
            color: rgba(255, 255, 255, 0.6) !important;
        }

        /* Input focus styling */
        .stTextInput > div > div > input:focus {
            background: rgba(255, 255, 255, 0.2);
            border: 2px solid rgba(255, 255, 255, 0.5);
            color: white !important;
            box-shadow: 0 0 0 0.2rem rgba(255, 255, 255, 0.25);
        }

        .stNumberInput > div > div > input:focus {
            background: rgba(255, 255, 255, 0.2);
            border: 2px solid rgba(255, 255, 255, 0.5);
            color: white !important;
            box-shadow: 0 0 0 0.2rem rgba(255, 255, 255, 0.25);
        }

        /* Risk Cards */
        .risk-card-high {
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 2rem;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(255, 107, 107, 0.4);
            transform: translateY(-5px);
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.2);
            animation: slideInRight 0.8s ease-out;
        }

        .risk-card-low {
            background: linear-gradient(135deg, #51cf66, #40c057);
            color: white;
            padding: 2rem;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(81, 207, 102, 0.4);
            transform: translateY(-5px);
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.2);
            animation: slideInRight 0.8s ease-out;
        }

        @keyframes slideInRight {
            from { opacity: 0; transform: translateX(50px); }
            to { opacity: 1; transform: translateX(0); }
        }

        .risk-score {
            font-size: 3rem;
            font-weight: 700;
            margin: 1rem 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .risk-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }

        .risk-subtitle {
            font-size: 1rem;
            opacity: 0.9;
            margin-bottom: 1.5rem;
        }

        /* Stats Cards */
        .stat-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
            margin-bottom: 1rem;
        }

        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }

        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: white;
            margin-bottom: 0.5rem;
        }

        .stat-label {
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.7);
            font-weight: 500;
        }

        /* Button Styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 15px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            width: 100%;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }

        /* Charts Container */
        .chart-container {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(15px);
            border-radius: 20px;
            padding: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin: 1rem 0;
        }

        /* Data Table Styling */
        .dataframe {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        /* Sidebar Header */
        .sidebar-header {
            background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.05) 100%);
            border-radius: 15px;
            padding: 1rem;
            text-align: center;
            margin-bottom: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        /* Loading Animation */
        .loading-spinner {
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Metrics Styling */
        .metric-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(15px);
            border-radius: 15px;
            padding: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            text-align: center;
        }

        /* Custom Alert Boxes */
        .success-alert {
            background: linear-gradient(135deg, #51cf66, #40c057);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .error-alert {
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .info-alert {
            background: linear-gradient(135deg, #74c0fc, #339af0);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        /* Feature highlights */
        .feature-badge {
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 500;
            margin: 0.2rem;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        /* Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


def create_hero_section():
    """Create an impressive hero section"""
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🏥 DiabetesAI Pro</h1>
        <p class="hero-subtitle">Advanced Machine Learning Risk Assessment Platform</p>
        <div class="hero-badge">✨ AI-Powered • Real-time Analysis • Professional Grade</div>
        <br><br>
        <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
            <span class="feature-badge">🤖 ML Predictions</span>
            <span class="feature-badge">📊 Real-time Analytics</span>
            <span class="feature-badge">☁️ Cloud Storage</span>
            <span class="feature-badge">📱 Responsive Design</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_risk_visualization(probability):
    """Create a beautiful risk visualization chart"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=probability,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Diabetes Risk Score",
               'font': {'color': 'white', 'size': 20}},
        number={'font': {'color': 'white', 'size': 30}},
        gauge={
            'axis': {'range': [None, 100], 'tickcolor': 'white', 'tickfont': {'color': 'white'}},
            'bar': {'color': "#667eea"},
            'bgcolor': "rgba(255,255,255,0.1)",
            'borderwidth': 2,
            'bordercolor': "white",
            'steps': [
                {'range': [0, 25], 'color': 'rgba(81, 207, 102, 0.3)'},
                {'range': [25, 50], 'color': 'rgba(255, 193, 7, 0.3)'},
                {'range': [50, 75], 'color': 'rgba(255, 152, 0, 0.3)'},
                {'range': [75, 100], 'color': 'rgba(255, 107, 107, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 50
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white', 'family': 'Inter'},
        height=300
    )

    return fig


def create_feature_importance_chart():
    """Create a sorted chart showing feature importance"""
    features = ['Glucose', 'BMI', 'Age', 'Pregnancies', 'Blood Pressure',
                'Insulin', 'Pedigree', 'Skin Thickness']
    importance = [0.25, 0.20, 0.15, 0.12, 0.10, 0.08, 0.06, 0.04]

    data = pd.DataFrame({'Feature': features, 'Importance': importance})
    data = data.sort_values(by='Importance', ascending=True)

    fig = px.bar(
        data,
        x='Importance',
        y='Feature',
        orientation='h',
        title="Feature Importance in Diabetes Prediction"
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white', 'family': 'Inter'},
        title={'x': 0.5, 'font': {'color': 'white', 'size': 16}},
        xaxis={'tickfont': {'color': 'white'}},
        yaxis={'tickfont': {'color': 'white'}},
        height=400
    )

    return fig


def create_stats_cards(logs_df):
    """Create beautiful statistics cards"""
    if logs_df.empty:
        total_predictions = 0
        high_risk_count = 0
        avg_age = 0
        avg_bmi = 0
    else:
        total_predictions = len(logs_df)
        high_risk_count = len(logs_df[logs_df['prediction'] == 'Positive'])
        try:
            avg_age = logs_df['age'].astype(float).mean()
            avg_bmi = logs_df['bmi'].astype(float).mean()
        except Exception:
            avg_age = 0
            avg_bmi = 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{total_predictions}</div>
            <div class="stat-label">Total Assessments</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{high_risk_count}</div>
            <div class="stat-label">High Risk Cases</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{avg_age:.1f}</div>
            <div class="stat-label">Average Age</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{avg_bmi:.1f}</div>
            <div class="stat-label">Average BMI</div>
        </div>
        """, unsafe_allow_html=True)


def render_footer():
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; color: rgba(255,255,255,0.6);">
        <p><strong>DiabetesAI Pro</strong> - Advanced Machine Learning Risk Assessment Platform</p>
        <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2);">
            <p style="font-size: 0.9rem; color: rgba(255,255,255,0.8);">
                © 2026 <strong>Sanchita</strong> | Chitkara University
            </p>
            <p style="font-size: 0.7rem; color: rgba(255,255,255,0.5); margin-top: 0.5rem;">
                Developed with ❤️ using Streamlit & Machine Learning
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
