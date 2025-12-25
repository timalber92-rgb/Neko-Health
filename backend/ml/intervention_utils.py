"""
Utility functions for applying interventions to patient health metrics.

This module provides smart intervention logic that:
- Applies state-dependent effects based on current patient metrics
- Enforces physiologically meaningful bounds
- Prevents normalization paradoxes for healthy patients
"""

from typing import Dict

import pandas as pd

# Clinical bounds for health metrics (based on medical guidelines)
METRIC_BOUNDS = {
    "trestbps": {"min": 90, "max": 200, "optimal": 110, "target": 130},  # Optimal: <120, Target: <130
    "chol": {"min": 120, "max": 400, "optimal": 180, "target": 220},  # Optimal: <200, Target: <240
    "thalach": {"min": 60, "max": 220, "optimal": 160, "target": 140},  # Higher is better for max HR
    "oldpeak": {"min": 0.0, "max": 6.0, "optimal": 0.0, "target": 0.5},  # Lower is better (no ST depression)
}


def calculate_adaptive_reduction(current_value: float, base_reduction: float, metric_name: str) -> float:
    """
    Calculate state-dependent intervention effect.

    For metrics that should be reduced (BP, cholesterol, oldpeak):
    - If already optimal or better: minimal/no reduction
    - If moderately elevated: apply base reduction
    - If highly elevated: apply stronger reduction

    For metrics that should be increased (max heart rate):
    - If already optimal or better: minimal/no increase
    - If moderately low: apply base increase
    - If very low: apply stronger increase

    Args:
        current_value: Current metric value
        base_reduction: Base reduction factor (e.g., 0.95 for 5% reduction)
        metric_name: Name of the metric being modified

    Returns:
        Adaptive reduction factor to apply
    """
    bounds = METRIC_BOUNDS.get(metric_name)
    if not bounds:
        return base_reduction

    optimal = bounds["optimal"]
    target = bounds["target"]
    max_val = bounds["max"]

    # For metrics that should be reduced (BP, cholesterol, oldpeak)
    if metric_name in ["trestbps", "chol", "oldpeak"]:
        if current_value <= optimal:
            # Already at or below optimal - no reduction needed
            return 1.0
        elif current_value <= target:
            # Between optimal and target - minimal reduction
            reduction_strength = 0.3  # Only 30% of base reduction
            return 1.0 - (1.0 - base_reduction) * reduction_strength
        elif current_value <= (target + (max_val - target) * 0.5):
            # Moderately elevated - apply base reduction
            return base_reduction
        else:
            # Highly elevated - apply stronger reduction
            reduction_strength = 1.5  # 150% of base reduction
            stronger_reduction = 1.0 - (1.0 - base_reduction) * reduction_strength
            return max(stronger_reduction, base_reduction * 0.8)  # Cap at 20% reduction

    # For metrics that should be increased (max heart rate)
    elif metric_name == "thalach":
        if current_value >= optimal:
            # Already at or above optimal - no increase needed
            return 1.0
        elif current_value >= target:
            # Between target and optimal - minimal increase
            increase_strength = 0.3  # Only 30% of base increase
            return 1.0 + (base_reduction - 1.0) * increase_strength
        else:
            # Below target - apply base increase
            return base_reduction

    return base_reduction


def apply_simple_intervention_effects(patient_data: pd.DataFrame, action: int) -> pd.DataFrame:
    """
    Apply simple percentage-based intervention effects for normalized data.

    This is used during RL agent training when working with normalized data.
    Uses fixed percentage reductions without bounds checking.

    Args:
        patient_data: DataFrame with normalized patient metrics
        action: Intervention action (0-4)

    Returns:
        Modified patient data with simple intervention effects
    """
    modified_data = patient_data.copy()

    if action == 0:  # Monitor Only
        pass
    elif action == 1:  # Lifestyle Intervention
        modified_data["trestbps"] *= 0.95  # 5% BP reduction
        modified_data["chol"] *= 0.90  # 10% cholesterol reduction
        modified_data["thalach"] *= 1.05  # 5% improved max HR
        if "exang" in modified_data.columns and modified_data["exang"].iloc[0] == 1:
            modified_data["exang"] = 0 if hash(str(modified_data.index[0])) % 5 > 0 else 1  # 80% success
    elif action == 2:  # Single Medication
        modified_data["trestbps"] *= 0.90  # 10% BP reduction
        modified_data["chol"] *= 0.85  # 15% cholesterol reduction
        if "exang" in modified_data.columns and modified_data["exang"].iloc[0] == 1:
            modified_data["exang"] = 0 if hash(str(modified_data.index[0])) % 10 > 2 else 1  # 70% success
    elif action == 3:  # Combination Therapy
        modified_data["trestbps"] *= 0.85  # 15% BP reduction
        modified_data["chol"] *= 0.80  # 20% cholesterol reduction
        modified_data["thalach"] *= 1.08  # 8% improved max HR
        modified_data["oldpeak"] *= 0.90  # 10% reduced ST depression
        if "exang" in modified_data.columns and modified_data["exang"].iloc[0] == 1:
            modified_data["exang"] = 0 if hash(str(modified_data.index[0])) % 2 == 0 else 1  # 50% success
    elif action == 4:  # Intensive Treatment
        modified_data["trestbps"] *= 0.80  # 20% BP reduction
        modified_data["chol"] *= 0.75  # 25% cholesterol reduction
        modified_data["thalach"] *= 1.10  # 10% improved max HR
        modified_data["oldpeak"] *= 0.80  # 20% reduced ST depression
        if "exang" in modified_data.columns and modified_data["exang"].iloc[0] == 1:
            modified_data["exang"] = 0 if hash(str(modified_data.index[0])) % 10 > 6 else 1  # 30% success (70% cure)

    return modified_data


def is_normalized_data(patient_data: pd.DataFrame) -> bool:
    """
    Check if patient data is normalized (StandardScaler output) or raw values.

    Normalized data will have most values between -3 and 3 (z-scores),
    while raw data will have physiologically meaningful ranges.

    Args:
        patient_data: DataFrame with patient metrics

    Returns:
        True if data appears to be normalized, False if raw values
    """
    # Check blood pressure - raw values are typically 90-200
    if "trestbps" in patient_data.columns:
        bp_value = float(patient_data["trestbps"].iloc[0])
        # If BP is in normalized range (typically -3 to 3), it's normalized data
        if abs(bp_value) < 10:
            return True
    return False


def apply_intervention_effects(patient_data: pd.DataFrame, action: int) -> pd.DataFrame:
    """
    Apply intervention effects to patient data with smart bounds checking.

    This function replaces the fixed percentage reductions with adaptive
    logic that considers current patient state and enforces clinical bounds.

    Handles both raw and normalized data automatically.

    Args:
        patient_data: DataFrame with patient metrics (raw or normalized values)
        action: Intervention action (0=Monitor, 1=Lifestyle, 2=Single Med,
                3=Combo Therapy, 4=Intensive)

    Returns:
        Modified patient data with intervention effects applied
    """
    modified_data = patient_data.copy()

    if action == 0:  # Monitor Only
        return modified_data

    # If data is normalized, use simple percentage reductions
    # (for RL agent training with normalized data)
    if is_normalized_data(patient_data):
        return apply_simple_intervention_effects(patient_data, action)

    # Define base intervention effects for each action
    # Note: exang is binary (0=no, 1=yes exercise-induced angina)
    # Interventions can reduce likelihood of exercise-induced angina
    intervention_effects = {
        1: {  # Lifestyle Intervention
            "trestbps": 0.95,  # 5% reduction
            "chol": 0.90,  # 10% reduction
            "thalach": 1.05,  # 5% increase
            "oldpeak": 0.95,  # 5% reduction (lifestyle improves ECG)
            "exang": 0.80,  # 20% reduction in exercise-induced angina probability
        },
        2: {  # Single Medication
            "trestbps": 0.90,  # 10% reduction
            "chol": 0.85,  # 15% reduction
            "thalach": 1.0,  # No change
            "oldpeak": 0.92,  # 8% reduction (meds improve cardiac function)
            "exang": 0.70,  # 30% reduction in exercise-induced angina
        },
        3: {  # Combination Therapy
            "trestbps": 0.85,  # 15% reduction
            "chol": 0.80,  # 20% reduction
            "thalach": 1.08,  # 8% increase
            "oldpeak": 0.90,  # 10% reduction
            "exang": 0.50,  # 50% reduction in exercise-induced angina
        },
        4: {  # Intensive Treatment
            "trestbps": 0.80,  # 20% reduction
            "chol": 0.75,  # 25% reduction
            "thalach": 1.10,  # 10% increase
            "oldpeak": 0.80,  # 20% reduction
            "exang": 0.30,  # 70% reduction in exercise-induced angina
        },
    }

    if action not in intervention_effects:
        return modified_data

    effects = intervention_effects[action]

    # Apply adaptive effects for each metric
    for metric_name, base_factor in effects.items():
        if metric_name not in modified_data.columns:
            continue

        current_value = float(modified_data[metric_name].iloc[0])

        # Special handling for binary features like exang
        if metric_name == "exang":
            # exang is binary: 1 = has exercise-induced angina, 0 = doesn't
            # If patient has angina (1), intervention can reduce it
            if current_value == 1:
                # Use base_factor as probability of successful treatment
                # e.g., 0.30 means 70% chance of eliminating angina
                import random

                random.seed(int(modified_data.index[0]))  # Deterministic based on patient
                if random.random() > base_factor:
                    modified_data[metric_name] = 0
            # If no angina (0), keep it at 0
            continue

        # Calculate adaptive reduction based on current state
        adaptive_factor = calculate_adaptive_reduction(current_value, base_factor, metric_name)

        # Apply the adaptive factor
        new_value = current_value * adaptive_factor

        # Enforce clinical bounds
        bounds = METRIC_BOUNDS.get(metric_name)
        if bounds:
            new_value = max(bounds["min"], min(bounds["max"], new_value))

        modified_data[metric_name] = new_value

    return modified_data


def ensure_risk_monotonicity(
    current_risk: float, new_risk: float, current_metrics: Dict[str, float], optimized_metrics: Dict[str, float], action: int
) -> tuple[float, Dict[str, float]]:
    """
    Ensure that interventions never paradoxically increase risk.

    If an intervention would increase risk (except for monitor-only),
    this function caps the risk at the current level but still shows
    the improved metrics to demonstrate the intervention's effects.

    Args:
        current_risk: Current risk score (0-100)
        new_risk: Predicted risk after intervention
        current_metrics: Original patient metrics
        optimized_metrics: Modified metrics after intervention
        action: Intervention action applied (0=monitor, 1-4=interventions)

    Returns:
        Tuple of (final_risk, final_metrics) with monotonicity enforced
    """
    # For monitor-only (action 0), always return the current state unchanged
    if action == 0:
        return current_risk, current_metrics

    # For all interventions (actions 1-4), never allow risk to increase
    # This prevents paradoxical outcomes where improving BP/cholesterol increases risk
    # due to model artifacts or training data biases
    # However, we ALWAYS show the optimized metrics to demonstrate intervention effects
    if new_risk > current_risk:
        # Cap risk at current level but show improved metrics
        return current_risk, optimized_metrics

    # If intervention successfully reduces risk, use the optimized metrics
    return new_risk, optimized_metrics
