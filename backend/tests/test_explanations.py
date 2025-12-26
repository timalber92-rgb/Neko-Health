#!/usr/bin/env python
"""Test the new explanation feature"""
import sys

sys.path.insert(0, "/workspace/backend")

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

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

print("\n" + "=" * 80)
print("MODERATE RISK PATIENT - SINGLE MEDICATION")
print("=" * 80)
response = client.post("/api/simulate", json={"patient": moderate_risk, "action": 2})
if response.status_code != 200:
    print(f"Error: {response.status_code}")
    print(response.json())
    sys.exit(1)
data = response.json()
print(f"Risk: {data['current_risk']:.1f}% → {data['expected_risk']:.1f}% (Δ{data['risk_reduction']:.1f}%)")
print(f"\nExplanation:\n{data['explanation']}")
print(f"\nTop Risk Factors: {list(data['feature_importance'].keys())[:5]}")
print(f"Modifiable Features: {data['modifiable_features']}")

print("\n" + "=" * 80)
print("HIGH RISK PATIENT - SINGLE MEDICATION")
print("=" * 80)
response = client.post("/api/simulate", json={"patient": high_risk, "action": 2})
data = response.json()
print(f"Risk: {data['current_risk']:.1f}% → {data['expected_risk']:.1f}% (Δ{data['risk_reduction']:.1f}%)")
print(f"\nExplanation:\n{data['explanation']}")
print(f"\nTop Risk Factors: {list(data['feature_importance'].keys())[:5]}")

print("\n" + "=" * 80)
print("HIGH RISK PATIENT - INTENSIVE TREATMENT")
print("=" * 80)
response = client.post("/api/simulate", json={"patient": high_risk, "action": 4})
data = response.json()
print(f"Risk: {data['current_risk']:.1f}% → {data['expected_risk']:.1f}% (Δ{data['risk_reduction']:.1f}%)")
print(f"\nExplanation:\n{data['explanation']}")
