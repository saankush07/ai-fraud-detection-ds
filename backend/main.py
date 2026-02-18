from fastapi import FastAPI
from pydantic import BaseModel, Field
import numpy as np
import joblib

from database import init_db, insert_prediction

app = FastAPI(title="FraudGuard AI API", version="1.0")

# Initialize DB and load model
init_db()
model = joblib.load("fraud_model.pkl")


class PredictRequest(BaseModel):
    features: list[float] = Field(..., min_items=29, max_items=29)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(req: PredictRequest):
    X = np.array([req.features], dtype=float)

    pred = int(model.predict(X)[0])
    proba = float(model.predict_proba(X)[0][1]) * 100.0

    risk = "HIGH" if pred == 1 else "LOW"
    insert_prediction(risk, proba)

    return {
        "prediction": pred,
        "risk_label": risk,
        "fraud_probability": proba
    }
