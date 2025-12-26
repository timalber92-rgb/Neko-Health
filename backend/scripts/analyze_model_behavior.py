#!/usr/bin/env python
"""Analyze how the ML model actually responds to interventions"""
import sys

sys.path.insert(0, "/workspace/backend")

import pickle

# Load model and scaler
from pathlib import Path

import pandas as pd

from ml.intervention_utils import apply_intervention_effects
from ml.risk_predictor import RiskPredictor

predictor = RiskPredictor()
predictor.load(Path("/workspace/backend/models/risk_predictor.pkl"))

from joblib import load as joblib_load

scaler = joblib_load("/workspace/backend/data/processed/scaler.pkl")


def analyze_patient(name, patient_data):
    print(f"\n{'='*60}")
    print(f"{name}")
    print(f"{'='*60}")

    # Create DataFrame
    patient_df = pd.DataFrame([patient_data])
    patient_normalized = pd.DataFrame(scaler.transform(patient_df), columns=patient_df.columns)

    # Get baseline risk
    baseline_pred = predictor.predict(patient_normalized)
    print(f"Baseline Risk: {baseline_pred['risk_score']:.1f}%")
    print(
        f"Baseline Metrics: BP={patient_data['trestbps']}, Chol={patient_data['chol']}, Thalach={patient_data['thalach']}, Oldpeak={patient_data['oldpeak']}"
    )
    print()

    action_names = ["Monitor", "Lifestyle", "Single Med", "Combo", "Intensive"]

    for action in range(5):
        # Apply intervention
        modified_raw = apply_intervention_effects(patient_df.copy(), action)
        modified_normalized = pd.DataFrame(scaler.transform(modified_raw), columns=modified_raw.columns)

        # Get new risk
        new_pred = predictor.predict(modified_normalized)

        # Calculate changes
        bp_change = patient_data["trestbps"] - modified_raw["trestbps"].iloc[0]
        chol_change = patient_data["chol"] - modified_raw["chol"].iloc[0]
        risk_change = baseline_pred["risk_score"] - new_pred["risk_score"]

        print(
            f"{action_names[action]:15} | BP: Δ{bp_change:5.1f} | Chol: Δ{chol_change:5.1f} | Risk: {baseline_pred['risk_score']:.1f}% → {new_pred['risk_score']:.1f}% (Δ{risk_change:5.1f}%)"
        )


# Test different patient profiles
moderate_risk = {
    "age": 55,
    "sex": 1,
    "cp": 3,
    "trestbps": 150,
    "chol": 250,
    "fbs": 0,
    "restecg": 0,
    "thalach": 135,
    "exang": 0,
    "oldpeak": 1.5,
    "slope": 2,
    "ca": 1,
    "thal": 3,
}

high_risk = {
    "age": 65,
    "sex": 1,
    "cp": 4,
    "trestbps": 170,
    "chol": 300,
    "fbs": 1,
    "restecg": 1,
    "thalach": 110,
    "exang": 1,
    "oldpeak": 3.0,
    "slope": 2,
    "ca": 2,
    "thal": 7,
}

healthy = {
    "age": 45,
    "sex": 1,
    "cp": 1,
    "trestbps": 110,
    "chol": 180,
    "fbs": 0,
    "restecg": 0,
    "thalach": 160,
    "exang": 0,
    "oldpeak": 0.0,
    "slope": 1,
    "ca": 0,
    "thal": 3,
}

analyze_patient("HEALTHY PATIENT (BP=110, Chol=180)", healthy)
analyze_patient("MODERATE RISK PATIENT (BP=150, Chol=250)", moderate_risk)
analyze_patient("HIGH RISK PATIENT (BP=170, Chol=300)", high_risk)

print(f"\n{'='*60}")
print("KEY INSIGHTS")
print(f"{'='*60}")
print("The ML model's risk predictions are based on:")
print("Top features: thal (16.6%), ca (14.3%), cp (12.3%), oldpeak (10.7%), thalach (9.1%)")
print()
print("BP and Cholesterol have LOWER feature importance!")
print("This means reducing BP/Chol may not significantly reduce risk if")
print("other high-importance features (thal, ca, cp, oldpeak) remain poor.")
