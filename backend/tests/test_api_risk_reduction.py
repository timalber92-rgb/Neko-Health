"""
Quick test to verify that the API returns correct risk reduction values.
"""

import requests

API_URL = "http://localhost:8000"

# Moderate risk patient
moderate_patient = {
    "age": 55.0,
    "sex": 1,
    "cp": 2,
    "trestbps": 145.0,
    "chol": 240.0,
    "fbs": 0,
    "restecg": 0,
    "thalach": 145.0,
    "exang": 0,
    "oldpeak": 1.5,
    "slope": 2,
    "ca": 1,
    "thal": 6,
}

print("=" * 80)
print("Testing API Risk Reduction Values")
print("=" * 80)
print()
print("Patient Profile: Moderate Risk")
print(f"BP: {moderate_patient['trestbps']} mmHg")
print(f"Cholesterol: {moderate_patient['chol']} mg/dL")
print()

# Test each intervention
interventions = ["Monitor Only", "Lifestyle Intervention", "Single Medication", "Combination Therapy", "Intensive Treatment"]

print(
    f"{'Intervention':<25} | {'Current Risk':>12} | {'Expected Risk':>13} | {'Reduction':>10} | {'BP Change':>10} | {'Chol Change':>12}"
)
print("-" * 110)

for action_id, intervention_name in enumerate(interventions):
    # Simulate this intervention
    simulation_request = {"patient": moderate_patient, "action": action_id}

    try:
        response = requests.post(
            f"{API_URL}/api/simulate", json=simulation_request, headers={"Content-Type": "application/json"}, timeout=10
        )

        if response.status_code == 200:
            result = response.json()

            current_risk = result["current_risk"]
            expected_risk = result["expected_risk"]
            risk_reduction = result["risk_reduction"]

            current_bp = result["current_metrics"]["trestbps"]
            expected_bp = result["optimized_metrics"]["trestbps"]
            bp_change = current_bp - expected_bp

            current_chol = result["current_metrics"]["chol"]
            expected_chol = result["optimized_metrics"]["chol"]
            chol_change = current_chol - expected_chol

            print(
                f"{intervention_name:<25} | {current_risk:>11.1f}% | {expected_risk:>12.1f}% | {risk_reduction:>9.1f}% | {bp_change:>9.1f} | {chol_change:>11.1f}"
            )

            # Check for issues
            if action_id == 3:  # Combination Therapy
                if risk_reduction < 5.0:
                    print(f"  ⚠️  WARNING: Combination therapy shows only {risk_reduction:.1f}% reduction (expected >5%)")
                else:
                    print(f"  ✅ OK: {risk_reduction:.1f}% reduction is reasonable")

        else:
            print(f"{intervention_name:<25} | ERROR: Status {response.status_code}")
            print(f"  Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print(f"{intervention_name:<25} | ERROR: Cannot connect to API (is it running?)")
        print()
        print("Please start the API with:")
        print("  cd backend && uvicorn api.main:app --reload")
        break
    except Exception as e:
        print(f"{intervention_name:<25} | ERROR: {str(e)}")

print()
print("=" * 80)
