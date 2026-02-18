import streamlit as st
import joblib
import numpy as np
import pandas as pd
from database import init_db, insert_prediction, get_stats, get_daily_trend

# ---------------- INITIALIZE DATABASE ----------------
init_db()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="FraudGuard AI", page_icon="💳", layout="wide")

# ---------------- CUSTOM DARK STYLE ----------------
st.markdown("""
<style>
.stApp {background-color: #0E1117; color: white;}
div.stButton > button {
    background-color: #FF4B4B;
    color: white;
    border-radius: 6px;
    height: 3em;
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
st.sidebar.title("FraudGuard AI")
menu = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "🔍 Single Prediction", "📂 Bulk Upload", "ℹ Model Info", "🚪 Logout"]
)

# ---------------- LOGOUT ----------------
if menu == "🚪 Logout":
    st.session_state.authenticated = False
    st.experimental_rerun()

# ================= DASHBOARD =================
if menu == "📊 Dashboard":
    st.title("📊 Fraud Detection Dashboard")

    # Get stats from database
    total, high_risk = get_stats()

    # Metrics Row
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Predictions", total)

    with col2:
        st.metric("High Risk Transactions", high_risk)

    with col3:
        if total > 0:
            fraud_rate = (high_risk / total) * 100
            st.metric("Fraud Rate %", f"{fraud_rate:.2f}%")
        else:
            st.metric("Fraud Rate %", "0%")

    # ---------------- DAILY TREND CHART ----------------
    st.subheader("📈 Daily Fraud Trend (Last 14 Days)")

    try:
        rows = get_daily_trend(14)

        if rows:
            df_trend = pd.DataFrame(
                rows,
                columns=["Date", "Total Transactions", "High Risk Transactions"]
            )

            df_trend["Fraud Rate %"] = (
                df_trend["High Risk Transactions"]
                / df_trend["Total Transactions"]
            ) * 100

            st.write("### Transactions Trend")
            st.line_chart(
                df_trend.set_index("Date")[
                    ["Total Transactions", "High Risk Transactions"]
                ]
            )

            st.write("### Fraud Rate Trend")
            st.line_chart(
                df_trend.set_index("Date")[["Fraud Rate %"]]
            )

        else:
            st.info("No prediction data available yet.")

    except Exception as e:
        st.warning("Trend chart will appear after database setup.")
    
# ================= SINGLE PREDICTION =================
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
        value = st.number_input(name, value=0.0)
        input_data.append(value)

    if st.button("Predict Transaction"):
        input_array = np.array([input_data])
        prediction = model.predict(input_array)
        probability = model.predict_proba(input_array)

        fraud_prob = probability[0][1] * 100

        if prediction[0] == 1:
            risk_label = "HIGH"
            st.error("🔴 HIGH RISK TRANSACTION DETECTED")
        else:
            risk_label = "LOW"
            st.success("🟢 LOW RISK TRANSACTION")

        st.progress(int(fraud_prob))
        st.write(f"Fraud Probability: {fraud_prob:.2f}%")

        # Save to database
        insert_prediction(risk_label, fraud_prob)

# ================= BULK UPLOAD =================
elif menu == "📂 Bulk Upload":
    st.title("📂 Bulk Fraud Detection")

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        predictions = model.predict(data)

        data["Risk_Level"] = ["HIGH" if p == 1 else "LOW" for p in predictions]

        fraud_count = sum(predictions)
        total = len(predictions)
        fraud_percent = (fraud_count / total) * 100

        st.write(data.head())

        st.markdown("### 📊 Summary")
        st.write(f"Total Transactions: {total}")
        st.write(f"High Risk Transactions: {fraud_count}")
        st.write(f"Fraud Percentage: {fraud_percent:.2f}%")

# ================= MODEL INFO =================
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
