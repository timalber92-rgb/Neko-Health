"""
Expected risk reduction values for different patient profiles and interventions.

This module defines the EXPECTED VALUES that our intervention system should produce.
These values are used in tests to validate that the system behaves correctly.

Values are based on clinical analysis and represent:
1. Diminishing returns for healthy patients (already optimal)
2. Progressive benefit for moderate-risk patients (modifiable factors)
3. Limited benefit for high-risk patients with structural factors

All values are derived from actual ML model predictions with the standard patient profiles.
"""

# Expected risk reduction table
# Format: {patient_profile: {intervention: {metric: value}}}

EXPECTED_RISK_REDUCTIONS = {
    "healthy": {
        "baseline_risk": 5.7,  # Low risk (already healthy)
        "interventions": {
            0: {  # Monitor Only
                "name": "Monitor Only",
                "new_risk": 5.7,
                "risk_reduction_absolute": 0.0,
                "risk_reduction_relative": 0.0,
                "bp_change": 0.0,
                "chol_change": 0.0,
                "thalach_change": 0.0,
                "oldpeak_change": 0.0,
                "cost": "Low ($)",
                "justified": True,
                "rationale": "Healthy patients need only monitoring",
            },
            1: {  # Lifestyle Intervention
                "name": "Lifestyle Intervention",
                "new_risk": 5.7,
                "risk_reduction_absolute": 0.0,
                "risk_reduction_relative": 0.0,
                "bp_change": 0.0,
                "chol_change": 0.0,
                "thalach_change": 0.0,
                "oldpeak_change": 0.0,
                "cost": "Low ($$)",
                "justified": True,
                "rationale": "No harm, promotes healthy habits",
            },
            2: {  # Single Medication
                "name": "Single Medication",
                "new_risk": 5.7,
                "risk_reduction_absolute": 0.0,
                "risk_reduction_relative": 0.0,
                "bp_change": 0.0,
                "chol_change": 0.0,
                "thalach_change": 0.0,
                "oldpeak_change": 0.0,
                "cost": "Medium ($$$)",
                "justified": False,
                "rationale": "No benefit, potential side effects",
            },
            3: {  # Combination Therapy
                "name": "Combination Therapy",
                "new_risk": 5.7,
                "risk_reduction_absolute": 0.0,
                "risk_reduction_relative": 0.0,
                "bp_change": 0.0,
                "chol_change": 0.0,
                "thalach_change": 0.0,
                "oldpeak_change": 0.0,
                "cost": "High ($$$$)",
                "justified": False,
                "rationale": "No benefit, potential side effects, high cost",
            },
            4: {  # Intensive Treatment
                "name": "Intensive Treatment",
                "new_risk": 5.7,
                "risk_reduction_absolute": 0.0,
                "risk_reduction_relative": 0.0,
                "bp_change": 0.0,
                "chol_change": 0.0,
                "thalach_change": 0.0,
                "oldpeak_change": 0.0,
                "cost": "Very High ($$$$$)",
                "justified": False,
                "rationale": "No benefit, over-treatment, high cost and burden",
            },
        },
    },
    "moderate_risk": {
        "baseline_risk": 67.7,  # Medium risk (modifiable factors)
        "interventions": {
            0: {  # Monitor Only
                "name": "Monitor Only",
                "new_risk": 67.7,
                "risk_reduction_absolute": 0.0,
                "risk_reduction_relative": 0.0,
                "bp_change": 0.0,
                "chol_change": 0.0,
                "thalach_change": 0.0,
                "oldpeak_change": 0.0,
                "cost": "Low ($)",
                "justified": False,
                "rationale": "Patient needs intervention, not just monitoring",
            },
            1: {  # Lifestyle Intervention
                "name": "Lifestyle Intervention",
                "new_risk": 63.5,
                "risk_reduction_absolute": 4.2,
                "risk_reduction_relative": 6.2,
                "bp_change": 7.2,
                "chol_change": 24.0,
                "thalach_change": 2.2,
                "oldpeak_change": 0.08,
                "cost": "Low ($$)",
                "justified": True,
                "rationale": "Good cost-benefit for first-line treatment",
            },
            2: {  # Single Medication
                "name": "Single Medication",
                "new_risk": 62.8,
                "risk_reduction_absolute": 5.0,
                "risk_reduction_relative": 7.3,
                "bp_change": 14.5,
                "chol_change": 36.0,
                "thalach_change": 0.0,
                "oldpeak_change": 0.12,
                "cost": "Medium ($$$)",
                "justified": True,
                "rationale": "Meaningful benefit for moderate cost",
            },
            3: {  # Combination Therapy
                "name": "Combination Therapy",
                "new_risk": 59.7,
                "risk_reduction_absolute": 8.0,
                "risk_reduction_relative": 11.8,
                "bp_change": 21.8,
                "chol_change": 48.0,
                "thalach_change": 3.5,
                "oldpeak_change": 0.15,
                "cost": "High ($$$$)",
                "justified": True,
                "rationale": "Excellent benefit justifies higher cost",
            },
            4: {  # Intensive Treatment
                "name": "Intensive Treatment",
                "new_risk": 55.1,
                "risk_reduction_absolute": 12.7,
                "risk_reduction_relative": 18.7,
                "bp_change": 29.0,
                "chol_change": 60.0,
                "thalach_change": 4.3,
                "oldpeak_change": 0.30,
                "cost": "Very High ($$$$$)",
                "justified": True,
                "rationale": "BEST cost-benefit ratio - most appropriate use case",
            },
        },
    },
    "high_risk": {
        "baseline_risk": 93.6,  # High risk (structural factors dominate)
        "interventions": {
            0: {  # Monitor Only
                "name": "Monitor Only",
                "new_risk": 93.6,
                "risk_reduction_absolute": 0.0,
                "risk_reduction_relative": 0.0,
                "bp_change": 0.0,
                "chol_change": 0.0,
                "thalach_change": 0.0,
                "oldpeak_change": 0.0,
                "cost": "Low ($)",
                "justified": False,
                "rationale": "High-risk patient needs intervention",
            },
            1: {  # Lifestyle Intervention
                "name": "Lifestyle Intervention",
                "new_risk": 89.2,
                "risk_reduction_absolute": 4.4,
                "risk_reduction_relative": 4.7,
                "bp_change": 13.5,
                "chol_change": 30.0,
                "thalach_change": 5.0,
                "oldpeak_change": 0.30,
                "cost": "Low ($$)",
                "justified": True,
                "rationale": "Low cost, modest benefit, worth trying",
            },
            2: {  # Single Medication
                "name": "Single Medication",
                "new_risk": 91.4,
                "risk_reduction_absolute": 2.3,
                "risk_reduction_relative": 2.4,
                "bp_change": 27.0,
                "chol_change": 45.0,
                "thalach_change": 0.0,
                "oldpeak_change": 0.48,
                "cost": "Medium ($$$)",
                "justified": True,
                "rationale": "Large metric changes, limited risk reduction (structural factors)",
            },
            3: {  # Combination Therapy
                "name": "Combination Therapy",
                "new_risk": 90.3,
                "risk_reduction_absolute": 3.3,
                "risk_reduction_relative": 3.5,
                "bp_change": 40.5,
                "chol_change": 60.0,
                "thalach_change": 8.0,
                "oldpeak_change": 0.60,
                "cost": "High ($$$$)",
                "justified": True,
                "rationale": "Modest benefit, patient may value quality of life improvements",
            },
            4: {  # Intensive Treatment
                "name": "Intensive Treatment",
                "new_risk": 87.5,
                "risk_reduction_absolute": 6.1,
                "risk_reduction_relative": 6.5,
                "bp_change": 54.0,
                "chol_change": 75.0,
                "thalach_change": 10.0,
                "oldpeak_change": 1.20,
                "cost": "Very High ($$$$$)",
                "justified": "case_by_case",
                "rationale": "Large metric improvements, but limited risk reduction due to structural factors (3 diseased vessels, thalassemia). May be justified for symptom management and QoL.",
            },
        },
    },
}


def get_expected_value(patient_profile: str, intervention: int, metric: str) -> float:
    """
    Get expected value for a specific patient profile, intervention, and metric.

    Args:
        patient_profile: "healthy", "moderate_risk", or "high_risk"
        intervention: 0-4 (action index)
        metric: Metric name (e.g., "risk_reduction_absolute", "bp_change")

    Returns:
        Expected value for the metric

    Raises:
        KeyError: If patient_profile, intervention, or metric not found
    """
    return EXPECTED_RISK_REDUCTIONS[patient_profile]["interventions"][intervention][metric]


def get_baseline_risk(patient_profile: str) -> float:
    """
    Get baseline risk for a patient profile.

    Args:
        patient_profile: "healthy", "moderate_risk", or "high_risk"

    Returns:
        Baseline risk percentage (0-100)
    """
    return EXPECTED_RISK_REDUCTIONS[patient_profile]["baseline_risk"]


def format_comparison_table() -> str:
    """
    Generate a formatted comparison table of all expected values.

    Returns:
        Markdown-formatted table string
    """
    lines = []
    lines.append("# Complete Risk Reduction Reference Table\n")
    lines.append("## Expected Values by Patient Profile and Intervention\n")

    for profile_name, profile_data in EXPECTED_RISK_REDUCTIONS.items():
        lines.append(f"\n### {profile_name.replace('_', ' ').title()}")
        lines.append(f"**Baseline Risk**: {profile_data['baseline_risk']}%\n")
        lines.append(
            "| Intervention | New Risk | Absolute ΔRisk | Relative ΔRisk | ΔBP (mmHg) | ΔChol (mg/dL) | Cost | Justified |"
        )
        lines.append("|---|---|---|---|---|---|---|---|")

        for action_id in range(5):
            intervention = profile_data["interventions"][action_id]
            lines.append(
                f"| {intervention['name']} | "
                f"{intervention['new_risk']:.1f}% | "
                f"{intervention['risk_reduction_absolute']:.1f}% | "
                f"{intervention['risk_reduction_relative']:.1f}% | "
                f"{intervention['bp_change']:.1f} | "
                f"{intervention['chol_change']:.1f} | "
                f"{intervention['cost']} | "
                f"{'✅' if intervention['justified'] is True else '⚠️' if intervention['justified'] == 'case_by_case' else '❌'} |"
            )

        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    print(format_comparison_table())
