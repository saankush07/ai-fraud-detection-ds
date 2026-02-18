import streamlit as st
import joblib
import numpy as np

# Load trained model
model = joblib.load("fraud_model.pkl")

st.title("💳 AI Fraud Detection System")

st.write("Enter transaction features (29 features required)")

input_data = []

for i in range(29):
    value = st.number_input(f"Feature V{i+1}", value=0.0)
    input_data.append(value)

if st.button("Predict"):
    input_array = np.array([input_data])
    prediction = model.predict(input_array)

    if prediction[0] == 1:
        st.error("⚠ Fraudulent Transaction Detected!")
    else:
        st.success("✅ Legitimate Transaction")
