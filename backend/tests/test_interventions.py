#!/usr/bin/env python
"""Quick test script to examine intervention effects"""
import sys

sys.path.insert(0, "/workspace/backend")

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

moderate_risk_patient = {
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

print("=== MODERATE RISK PATIENT ===")
print("Starting metrics: BP=150, Chol=250")
print()

action_names = ["Monitor Only", "Lifestyle", "Single Med", "Combo Therapy", "Intensive"]

for action in range(5):
    response = client.post("/api/simulate", json={"patient": moderate_risk_patient, "action": action})
    if response.status_code != 200:
        print(f"Error for action {action}: {response.status_code}")
        print(response.json())
        continue
    data = response.json()

    print(f"{action_names[action]}:")
    print(
        f'  BP: {data["current_metrics"]["trestbps"]:.1f} → {data["optimized_metrics"]["trestbps"]:.1f} (Δ{data["current_metrics"]["trestbps"] - data["optimized_metrics"]["trestbps"]:.1f})'
    )
    print(
        f'  Chol: {data["current_metrics"]["chol"]:.1f} → {data["optimized_metrics"]["chol"]:.1f} (Δ{data["current_metrics"]["chol"] - data["optimized_metrics"]["chol"]:.1f})'
    )
    print(f'  Risk: {data["current_risk"]:.1f}% → {data["expected_risk"]:.1f}% (Δ{data["risk_reduction"]:.1f}%)')
    print()
