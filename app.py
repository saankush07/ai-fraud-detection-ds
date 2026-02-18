import os
import requests
import streamlit as st
import numpy as np
import pandas as pd

from database import init_db, get_stats, get_daily_trend

# ---------------- INIT DB (for dashboard stats/trends) ----------------
init_db()

# ---------------- CONFIG ----------------
st.set_page_config(page_title="FraudGuard AI", page_icon="💳", layout="wide")

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# ---------------- CUSTOM DARK STYLE ----------------
st.markdown("""
<style>
.stApp {background-color: #0E1117; color: white;}
section[data-testid="stSidebar"] {background-color: #161A25;}
div.stButton > button {
    background-color: #FF4B4B;
    color: white;
    border-radius: 10px;
    height: 3em;
    font-weight: 600;
}
.metric-card {
    background-color: #1C1F2B;
    padding: 18px;
    border-radius: 14px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.05);
}
small.muted {color: rgba(255,255,255,0.65);}
hr {border-top: 1px solid rgba(255,255,255,0.08);}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN SYSTEM ----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login_screen():
    st.title("🔐 FraudGuard AI Login")
    st.write("Enter credentials to access the SaaS dashboard.")
    user = st.text_input("Username", placeholder="Ankush")
    pwd = st.text_input("Password", type="password", placeholder="Ankush@123")

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Login"):
            if user == "Ankush" and pwd == "Ankush@123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")

    with col2:
        st.markdown("<small class='muted'>Demo credentials: Ankush / Ankush@123</small>", unsafe_allow_html=True)

if not st.session_state.authenticated:
    login_screen()
    st.stop()

# ---------------- SIDEBAR NAV ----------------
st.sidebar.title("FraudGuard AI")
menu = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "🔍 Single Prediction", "📂 Bulk Upload", "ℹ Model Info", "🚪 Logout"]
)

if menu == "🚪 Logout":
    st.session_state.authenticated = False
    st.rerun()

# ---------------- SHARED: Feature Names ----------------
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

# ================= DASHBOARD =================
if menu == "📊 Dashboard":
    st.title("📊 Fraud Detection Dashboard")

    total, high_risk = get_stats()

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

    st.markdown("---")

    st.subheader("📈 Daily Fraud Trend (Last 14 Days)")
    try:
        rows = get_daily_trend(14)

        if rows:
            df_trend = pd.DataFrame(
                rows,
                columns=["Date", "Total Transactions", "High Risk Transactions"]
            )
            df_trend["Fraud Rate %"] = (
                df_trend["High Risk Transactions"] / df_trend["Total Transactions"]
            ) * 100

            st.write("### Transactions Trend")
            st.line_chart(df_trend.set_index("Date")[["Total Transactions", "High Risk Transactions"]])

            st.write("### Fraud Rate Trend")
            st.line_chart(df_trend.set_index("Date")[["Fraud Rate %"]])
        else:
            st.info("No prediction data yet. Make some predictions first.")

    except Exception as e:
        st.warning("Trend charts will appear after DB is ready. If using Supabase, ensure DATABASE_URL is set in Streamlit Secrets.")
        st.write(str(e))

# ================= SINGLE PREDICTION =================
elif menu == "🔍 Single Prediction":
    st.title("🔍 Single Transaction Prediction")
    st.write("Enter transaction risk parameters and predict fraud probability (via FastAPI backend).")

    input_data = []

    # Premium layout: split inputs into 2 columns
    colA, colB = st.columns(2)
    for i, name in enumerate(feature_names):
        with (colA if i % 2 == 0 else colB):
            val = st.number_input(name, value=0.0, format="%.6f")
            input_data.append(val)

    st.markdown("---")

    if st.button("Predict Transaction"):
        payload = {"features": input_data}

        try:
            res = requests.post(f"{API_URL}/predict", json=payload, timeout=30)
            res.raise_for_status()
            result = res.json()

            risk_label = result["risk_label"]
            fraud_prob = float(result["fraud_probability"])

            if risk_label == "HIGH":
                st.error("🔴 HIGH RISK TRANSACTION DETECTED")
            else:
                st.success("🟢 LOW RISK TRANSACTION")

            st.progress(min(100, int(fraud_prob)))
            st.write(f"Fraud Probability: {fraud_prob:.2f}%")

        except Exception as e:
            st.error(f"API Connection/Error: {e}")
            st.info("Make sure FastAPI is running: python -m uvicorn backend.main:app --reload")

# ================= BULK UPLOAD =================
elif menu == "📂 Bulk Upload":
    st.title("📂 Bulk Fraud Detection")
    st.write("Upload a CSV with 29 feature columns (same order as model input).")

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        st.write("Preview:")
        st.dataframe(df.head())

        if df.shape[1] != 29:
            st.error("CSV must have exactly 29 columns (feature inputs).")
        else:
            if st.button("Run Bulk Prediction"):
                preds = []
                probs = []

                progress = st.progress(0)
                total_rows = len(df)

                for idx in range(total_rows):
                    features = df.iloc[idx].astype(float).tolist()
                    payload = {"features": features}

                    try:
                        res = requests.post(f"{API_URL}/predict", json=payload, timeout=30)
                        res.raise_for_status()
                        out = res.json()

                        preds.append(out["risk_label"])
                        probs.append(float(out["fraud_probability"]))

                    except Exception as e:
                        preds.append("ERROR")
                        probs.append(np.nan)

                    progress.progress(int(((idx + 1) / total_rows) * 100))

                df["Risk_Label"] = preds
                df["Fraud_Probability_%"] = probs

                st.success("Bulk predictions completed ✅")
                st.dataframe(df.head(20))

                high_count = (df["Risk_Label"] == "HIGH").sum()
                st.markdown("### 📊 Summary")
                st.write(f"Total Rows: {total_rows}")
                st.write(f"High Risk: {high_count}")
                st.write(f"High Risk %: {(high_count / total_rows) * 100:.2f}%")

# ================= MODEL INFO =================
elif menu == "ℹ Model Info":
    st.title("ℹ Model Information")

    st.markdown("""
- **Algorithm:** Random Forest Classifier  
- **Imbalance Handling:** SMOTE  
- **Input Features:** 29 engineered risk parameters (mapped from PCA components)  
- **Serving Layer:** FastAPI (`/predict`)  
- **Frontend:** Streamlit SaaS UI  
- **Database:** SQLite (local) / PostgreSQL (Supabase)  
- **Developer:** Ankush (B.Tech CSE)  
""")

    st.markdown("---")
    st.write("API Endpoint:")
    st.code(f"{API_URL}/predict")

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("© 2026 FraudGuard AI | SaaS Style Fraud Detection System")
