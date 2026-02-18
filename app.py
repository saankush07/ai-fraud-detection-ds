import streamlit as st
import joblib
import numpy as np
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Fraud Detection Pro", page_icon="💳", layout="wide")

# ---------------- DARK THEME STYLE ----------------
st.markdown("""
<style>
body {background-color: #0E1117;}
.stApp {background-color: #0E1117; color: white;}
div.stButton > button {
    background-color: #FF4B4B;
    color: white;
    border-radius: 8px;
    height: 3em;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIMPLE LOGIN ----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login():
    st.title("🔐 Secure Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "Ankush" and password == "Ankush@123":
            st.session_state.authenticated = True
        else:
            st.error("Invalid Credentials")

if not st.session_state.authenticated:
    login()
    st.stop()

# ---------------- LOAD MODEL ----------------
model = joblib.load("fraud_model.pkl")

st.title("💳 AI Fraud Detection System - Pro Version")
st.markdown("Real-time fraud detection using Random Forest + SMOTE")

# ---------------- FEATURE NAMES ----------------
feature_names = [
    "Transaction Pattern Score",
    "Spending Behavior Index",
    "Velocity Risk Score",
    "Anomaly Detection Value",
    "Merchant Risk Indicator",
    "Location Deviation Score",
    "Card Usage Variation",
    "Time Pattern Irregularity",
    "Transaction Frequency Index",
    "Amount Deviation Metric",
    "Behavior Drift Score",
    "Purchase Risk Gradient",
    "Customer Trust Index",
    "Payment Irregularity Score",
    "Fraud Probability Signal",
    "Risk Amplification Index",
    "Suspicious Activity Scale",
    "Chargeback Risk Metric",
    "Transaction Entropy Value",
    "Behavioral Variance Score",
    "High Risk Pattern Marker",
    "Digital Footprint Score",
    "Device Risk Indicator",
    "Geo Risk Deviation",
    "Authorization Risk Index",
    "Cardholder Consistency Score",
    "Financial Stability Metric",
    "Spending Shift Indicator",
    "Composite Risk Score"
]

# ---------------- SIDEBAR INPUT ----------------
st.sidebar.header("Enter Transaction Details")

input_data = []
for name in feature_names:
    value = st.sidebar.number_input(name, value=0.0)
    input_data.append(value)

# ---------------- PREDICTION ----------------
col1, col2 = st.columns(2)

with col1:
    if st.button("🔍 Predict Transaction"):
        input_array = np.array([input_data])
        prediction = model.predict(input_array)
        probability = model.predict_proba(input_array)

        fraud_prob = probability[0][1] * 100

        if prediction[0] == 1:
            st.error("⚠ FRAUDULENT TRANSACTION DETECTED")
        else:
            st.success("✅ LEGITIMATE TRANSACTION")

        st.progress(int(fraud_prob))
        st.write(f"Fraud Probability: {fraud_prob:.2f}%")

with col2:
    if st.button("🎲 Random Test"):
        random_data = np.random.randn(29)
        input_array = np.array([random_data])
        prediction = model.predict(input_array)

        if prediction[0] == 1:
            st.error("⚠ Fraudulent (Random Test)")
        else:
            st.success("✅ Legitimate (Random Test)")

# ---------------- CSV UPLOAD ----------------
st.markdown("---")
st.subheader("📊 Bulk Fraud Detection (Upload CSV)")

uploaded_file = st.file_uploader("Upload transaction dataset (CSV)", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    predictions = model.predict(data)
    data["Fraud_Prediction"] = predictions
    st.write(data.head())

    fraud_count = sum(predictions)
    st.write(f"⚠ Total Fraud Transactions Detected: {fraud_count}")

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("🚀 Developed by Ankush | AI Fraud Detection Pro System")
