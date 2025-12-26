"""
Analyze risk reduction for different patient risk profiles.

This script creates a comprehensive table showing:
1. How interventions affect healthy, moderate, and high-risk patients
2. The diminishing returns for healthy patients
3. Whether intensive treatment makes sense for each risk level
"""

import os
import sys

import pandas as pd

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from api.main import app
from ml.intervention_utils import apply_intervention_effects


def create_patient_profiles():
    """Create three patient profiles: healthy, moderate risk, and high risk."""

    # Healthy patient - optimal metrics
    healthy = {
        "age": 35.0,
        "sex": 0,
        "cp": 1,  # Typical angina (least severe)
        "trestbps": 110.0,  # Optimal BP
        "chol": 180.0,  # Optimal cholesterol
        "fbs": 0,
        "restecg": 0,
        "thalach": 170.0,  # Good max heart rate
        "exang": 0,  # No exercise-induced angina
        "oldpeak": 0.0,  # No ST depression
        "slope": 1,
        "ca": 0,  # No diseased vessels
        "thal": 3,  # Normal
    }

    # Moderate risk patient - some elevated metrics
    moderate = {
        "age": 55.0,
        "sex": 1,
        "cp": 2,  # Atypical angina
        "trestbps": 145.0,  # Moderately elevated BP
        "chol": 240.0,  # Moderately high cholesterol
        "fbs": 0,
        "restecg": 0,
        "thalach": 145.0,  # Moderate max heart rate
        "exang": 0,
        "oldpeak": 1.5,  # Moderate ST depression
        "slope": 2,
        "ca": 1,  # One diseased vessel
        "thal": 6,  # Fixed defect
    }

    # High risk patient - multiple severe risk factors
    high_risk = {
        "age": 70.0,
        "sex": 1,
        "cp": 4,  # Asymptomatic (most severe)
        "trestbps": 180.0,  # Severe hypertension
        "chol": 300.0,  # High cholesterol
        "fbs": 1,
        "restecg": 2,
        "thalach": 100.0,  # Low max heart rate
        "exang": 1,  # Exercise-induced angina
        "oldpeak": 4.0,  # Severe ST depression
        "slope": 3,
        "ca": 3,  # Three diseased vessels
        "thal": 7,  # Reversible defect
    }

    return {"Healthy": healthy, "Moderate Risk": moderate, "High Risk": high_risk}


def get_risk_prediction(patient_data, predictor, scaler):
    """Get risk prediction for a patient."""
    import joblib

    patient_df = pd.DataFrame([patient_data])

    # Normalize the data using the scaler
    patient_normalized = pd.DataFrame(scaler.transform(patient_df), columns=patient_df.columns)

    # Get prediction (returns a dict)
    prediction = predictor.predict(patient_normalized)
    risk_score = prediction["risk_score"]

    return risk_score


def analyze_intervention_effects(patient_data, action, predictor, scaler):
    """Analyze the effect of an intervention on a patient."""
    # Get current risk
    current_risk = get_risk_prediction(patient_data, predictor, scaler)

    # Apply intervention
    patient_df = pd.DataFrame([patient_data])
    modified_df = apply_intervention_effects(patient_df, action)
    modified_data = modified_df.iloc[0].to_dict()

    # Get new risk
    new_risk = get_risk_prediction(modified_data, predictor, scaler)

    # Calculate reduction
    risk_reduction = current_risk - new_risk
    risk_reduction_pct = (risk_reduction / current_risk * 100) if current_risk > 0 else 0

    # Calculate metric changes
    bp_change = patient_data["trestbps"] - modified_data["trestbps"]
    chol_change = patient_data["chol"] - modified_data["chol"]
    thalach_change = modified_data["thalach"] - patient_data["thalach"]
    oldpeak_change = patient_data["oldpeak"] - modified_data["oldpeak"]

    return {
        "current_risk": current_risk,
        "new_risk": new_risk,
        "risk_reduction": risk_reduction,
        "risk_reduction_pct": risk_reduction_pct,
        "bp_change": bp_change,
        "chol_change": chol_change,
        "thalach_change": thalach_change,
        "oldpeak_change": oldpeak_change,
        "modified_data": modified_data,
    }


def create_analysis_table():
    """Create comprehensive analysis table."""
    import joblib

    from api.config import get_settings
    from ml.risk_predictor import RiskPredictor

    # Load models
    settings = get_settings()
    predictor = RiskPredictor()
    predictor.load(settings.risk_predictor_path)
    scaler = joblib.load(settings.scaler_path)

    # Get patient profiles
    profiles = create_patient_profiles()

    # Action names
    action_names = [
        "Monitor Only",
        "Lifestyle Intervention",
        "Single Medication",
        "Combination Therapy",
        "Intensive Treatment",
    ]

    # Create results table
    results = []

    for profile_name, patient_data in profiles.items():
        for action in range(5):
            analysis = analyze_intervention_effects(patient_data, action, predictor, scaler)

            results.append(
                {
                    "Patient Profile": profile_name,
                    "Intervention": action_names[action],
                    "Current Risk (%)": f"{analysis['current_risk']:.1f}",
                    "New Risk (%)": f"{analysis['new_risk']:.1f}",
                    "Absolute Reduction (%)": f"{analysis['risk_reduction']:.1f}",
                    "Relative Reduction (%)": f"{analysis['risk_reduction_pct']:.1f}",
                    "BP Change (mmHg)": f"{analysis['bp_change']:.1f}",
                    "Chol Change (mg/dL)": f"{analysis['chol_change']:.1f}",
                    "Max HR Change (bpm)": f"{analysis['thalach_change']:.1f}",
                    "ST Depression Change": f"{analysis['oldpeak_change']:.2f}",
                }
            )

    df = pd.DataFrame(results)
    return df


def main():
    """Run the analysis and print results."""
    print("=" * 100)
    print("RISK REDUCTION ANALYSIS: Healthy vs Moderate vs High Risk Patients")
    print("=" * 100)
    print()
    print("This analysis examines whether interventions have appropriate effects across")
    print("different patient risk profiles, checking for:")
    print("1. Diminishing returns for healthy patients (already at optimal metrics)")
    print("2. Moderate effects for moderate-risk patients")
    print("3. Stronger effects for high-risk patients (more room for improvement)")
    print("4. Whether intensive treatment is justified across risk levels")
    print()

    # Create and display table
    df = create_analysis_table()

    # Display full table
    print("\n" + "=" * 100)
    print("FULL ANALYSIS TABLE")
    print("=" * 100)
    print(df.to_string(index=False))

    # Summary by patient profile
    print("\n" + "=" * 100)
    print("SUMMARY BY PATIENT PROFILE")
    print("=" * 100)

    for profile in ["Healthy", "Moderate Risk", "High Risk"]:
        profile_data = df[df["Patient Profile"] == profile]
        print(f"\n{profile} Patient:")
        print("-" * 50)
        for _, row in profile_data.iterrows():
            print(
                f"  {row['Intervention']:25s} | Risk: {row['Current Risk (%)']} → {row['New Risk (%)']} "
                f"| Reduction: {row['Absolute Reduction (%)']}% (relative: {row['Relative Reduction (%)']}%)"
            )

    # Analysis
    print("\n" + "=" * 100)
    print("INTERPRETATION & VALIDATION")
    print("=" * 100)

    healthy_data = df[df["Patient Profile"] == "Healthy"]
    moderate_data = df[df["Patient Profile"] == "Moderate Risk"]
    high_data = df[df["Patient Profile"] == "High Risk"]

    print("\n1. DIMINISHING RETURNS FOR HEALTHY PATIENTS:")
    print("-" * 50)
    healthy_intensive = healthy_data[healthy_data["Intervention"] == "Intensive Treatment"].iloc[0]
    print(f"   Healthy patient baseline risk: {healthy_intensive['Current Risk (%)']}%")
    print(f"   Risk reduction with Intensive Treatment: {healthy_intensive['Absolute Reduction (%)']}%")
    print(
        f"   Metric changes: BP {healthy_intensive['BP Change (mmHg)']} mmHg, "
        f"Chol {healthy_intensive['Chol Change (mg/dL)']} mg/dL"
    )

    if float(healthy_intensive["BP Change (mmHg)"]) < 5:
        print("   ✓ APPROPRIATE: Minimal BP change (already optimal)")
    else:
        print("   ⚠ WARNING: Large BP change despite optimal baseline")

    print("\n2. MODERATE RISK PATIENTS:")
    print("-" * 50)
    moderate_intensive = moderate_data[moderate_data["Intervention"] == "Intensive Treatment"].iloc[0]
    print(f"   Moderate patient baseline risk: {moderate_intensive['Current Risk (%)']}%")
    print(f"   Risk reduction with Intensive Treatment: {moderate_intensive['Absolute Reduction (%)']}%")
    print(
        f"   Metric changes: BP {moderate_intensive['BP Change (mmHg)']} mmHg, "
        f"Chol {moderate_intensive['Chol Change (mg/dL)']} mg/dL"
    )

    print("\n3. HIGH RISK PATIENTS:")
    print("-" * 50)
    high_intensive = high_data[high_data["Intervention"] == "Intensive Treatment"].iloc[0]
    print(f"   High-risk patient baseline risk: {high_intensive['Current Risk (%)']}%")
    print(f"   Risk reduction with Intensive Treatment: {high_intensive['Absolute Reduction (%)']}%")
    print(
        f"   Metric changes: BP {high_intensive['BP Change (mmHg)']} mmHg, "
        f"Chol {high_intensive['Chol Change (mg/dL)']} mg/dL"
    )

    if float(high_intensive["BP Change (mmHg)"]) > float(healthy_intensive["BP Change (mmHg)"]):
        print("   ✓ APPROPRIATE: Larger metric improvements than healthy patients")
    else:
        print("   ⚠ WARNING: Similar or smaller changes than healthy patients")

    print("\n4. COST-BENEFIT ANALYSIS:")
    print("-" * 50)
    print("   Intensive Treatment costs are HIGH ($$$$)")
    print("   Is it justified?")

    healthy_benefit = float(healthy_intensive["Absolute Reduction (%)"])
    moderate_benefit = float(moderate_intensive["Absolute Reduction (%)"])
    high_benefit = float(high_intensive["Absolute Reduction (%)"])

    print(f"\n   Healthy patient:       {healthy_benefit:.1f}% risk reduction")
    print(f"   Moderate-risk patient: {moderate_benefit:.1f}% risk reduction")
    print(f"   High-risk patient:     {high_benefit:.1f}% risk reduction")

    if high_benefit > moderate_benefit > healthy_benefit:
        print("\n   ✓ APPROPRIATE: Diminishing returns pattern observed")
        print("     Higher-risk patients benefit more from intensive treatment")
    else:
        print("\n   ⚠ NEEDS REVIEW: Risk reduction pattern may not follow expected diminishing returns")

    print("\n" + "=" * 100)
    print()


if __name__ == "__main__":
    main()
