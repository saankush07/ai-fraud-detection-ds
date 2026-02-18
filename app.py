import streamlit as st
import joblib
import numpy as np
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="FraudGuard AI", page_icon="💳", layout="wide")

# ---------------- CUSTOM DARK STYLE ----------------
st.markdown("""
<style>
.stApp {background-color: #0E1117; color: white;}
.sidebar .sidebar-content {background-color: #161A25;}
div.stButton > button {
    background-color: #FF4B4B;
    color: white;
    border-radius: 6px;
    height: 3em;
}
.metric-card {
    background-color: #1C1F2B;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN SYSTEM ----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login():
    st.title("🔐 FraudGuard AI Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "Ankush" and pwd == "Ankush@123":
            st.session_state.authenticated = True
        else:
            st.error("Invalid credentials")

if not st.session_state.authenticated:
    login()
    st.stop()

# ---------------- LOAD MODEL ----------------
model = joblib.load("fraud_model.pkl")

# ---------------- SIDEBAR NAVIGATION ----------------
st.sidebar.title("Transaction Risk Parameters")
menu = st.sidebar.radio("Navigation", 
                        ["📊 Dashboard", "🔍 Single Prediction", 
                         "📂 Bulk Upload", "ℹ Model Info", "🚪 Logout"])

if menu == "🚪 Logout":
    st.session_state.authenticated = False
    st.experimental_rerun()

# ---------------- DASHBOARD ----------------
if menu == "📊 Dashboard":
    st.title("📊 Fraud Detection Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="metric-card"><h3>Total Transactions</h3><h2>10,000+</h2></div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card"><h3>Fraud Detection Accuracy</h3><h2>99%</h2></div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card"><h3>Model Type</h3><h2>Random Forest</h2></div>', unsafe_allow_html=True)

# ---------------- SINGLE PREDICTION ----------------
elif menu == "🔍 Single Prediction":
    st.title("🔍 Single Transaction Prediction")

    feature_names = [
    "Transaction Velocity Score",
    "Spending Pattern Deviation",
    "Merchant Risk Index",
    "Geolocation Variance Score",
    "Device Risk Fingerprint",
    "Authorization Anomaly Score",
    "Card Usage Irregularity",
    "Time-Based Risk Signal",
    "High-Value Transaction Marker",
    "Behavioral Drift Index",
    "Historical Fraud Correlation",
    "Chargeback Exposure Score",
    "Customer Trust Rating",
    "Purchase Frequency Risk",
    "Account Stability Indicator",
    "Payment Channel Risk",
    "Digital Footprint Strength",
    "Cross-Border Activity Score",
    "Suspicious Activity Probability",
    "Financial Consistency Metric",
    "Transaction Entropy Index",
    "Adaptive Risk Gradient",
    "Cardholder Behavior Variance",
    "AML Compliance Indicator",
    "Fraud Pattern Similarity Score",
    "Identity Verification Risk",
    "Network Risk Exposure",
    "Transaction Confidence Score",
    "Composite Fraud Risk Index"
]


    input_data = []
    for name in feature_names:
        val = st.number_input(name, value=0.0)
        input_data.append(val)

    if st.button("Predict Transaction"):
        input_array = np.array([input_data])
        prediction = model.predict(input_array)
        probability = model.predict_proba(input_array)

        fraud_prob = probability[0][1] * 100

        if prediction[0] == 1:
            st.error("⚠ Fraudulent Transaction")
        else:
            st.success("✅ Legitimate Transaction")

        st.progress(int(fraud_prob))
        st.write(f"Fraud Probability: {fraud_prob:.2f}%")

# ---------------- BULK UPLOAD ----------------
elif menu == "📂 Bulk Upload":
    st.title("📂 Bulk Fraud Detection")

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        predictions = model.predict(data)
        data["Fraud_Prediction"] = predictions

        fraud_count = sum(predictions)
        total = len(predictions)
        fraud_percent = (fraud_count / total) * 100

        st.write(data.head())

        st.markdown("### 📊 Summary")
        st.write(f"Total Transactions: {total}")
        st.write(f"Fraudulent Transactions: {fraud_count}")
        st.write(f"Fraud Percentage: {fraud_percent:.2f}%")

# ---------------- MODEL INFO ----------------
elif menu == "ℹ Model Info":
    st.title("ℹ Model Information")

    st.write("• Algorithm: Random Forest Classifier")
    st.write("• Imbalance Handling: SMOTE")
    st.write("• Features: PCA Transformed Components")
    st.write("• Deployment: Streamlit Cloud")
    st.write("• Developer: Ankush (B.Tech CSE)")

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("© 2026 FraudGuard AI | SaaS Style Fraud Detection System")
