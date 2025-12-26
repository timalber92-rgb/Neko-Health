"""
Guideline-Based Intervention Recommender for HealthGuard

This module implements a clinical guideline-based intervention selector that replaces
the RL-based approach. It provides reliable, explainable recommendations appropriate
for medical applications with limited training data.

The recommender uses evidence-based clinical guidelines to recommend interventions
based on cardiovascular disease risk scores and specific patient risk factors.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Action definitions (intervention strategies) - same as RL agent for API compatibility
ACTIONS = {
    0: {
        "name": "Monitor Only",
        "description": "Quarterly checkups with no active intervention",
        "cost": "Low ($)",
        "intensity": "Minimal",
    },
    1: {
        "name": "Lifestyle Intervention",
        "description": "Diet and exercise program with regular monitoring",
        "cost": "Low ($$)",
        "intensity": "Moderate",
    },
    2: {
        "name": "Single Medication",
        "description": "Single medication (e.g., statin or beta-blocker)",
        "cost": "Medium ($$$)",
        "intensity": "Moderate",
    },
    3: {
        "name": "Combination Therapy",
        "description": "Medication plus supervised lifestyle program",
        "cost": "High ($$$$)",
        "intensity": "High",
    },
    4: {
        "name": "Intensive Treatment",
        "description": "Multiple medications with intensive lifestyle management",
        "cost": "Very High ($$$$$)",
        "intensity": "Very High",
    },
}

# Clinical risk thresholds (aligned with ACC/AHA guidelines)
RISK_THRESHOLDS = {
    "very_low": 15.0,  # <15% = very low risk
    "low": 30.0,  # 15-30% = low risk
    "medium": 50.0,  # 30-50% = medium risk
    "high": 70.0,  # 50-70% = high risk
    # ≥70% = very high risk
}

# Risk factor definitions for escalation logic
SEVERE_RISK_FACTORS = {
    "trestbps": 160,  # Severe hypertension (Stage 2)
    "chol": 280,  # Very high cholesterol
    "oldpeak": 2.0,  # Significant ST depression
}

MODERATE_RISK_FACTORS = {
    "trestbps": 140,  # Moderate hypertension (Stage 1)
    "chol": 240,  # High cholesterol
    "oldpeak": 1.0,  # Moderate ST depression
}


class GuidelineRecommender:
    """
    Guideline-based intervention recommender for cardiovascular disease.

    This recommender uses clinical guidelines and risk stratification to recommend
    appropriate interventions. It provides transparent, explainable recommendations
    based on established medical evidence.

    Key features:
    - Risk-stratified recommendations based on ACC/AHA guidelines
    - Risk factor escalation logic (multiple severe factors → higher treatment)
    - Explainable rationale for each recommendation
    - Edge case handling (e.g., low risk but severe individual factors)
    - No training required - purely rule-based
    """

    def __init__(self):
        """Initialize the guideline-based recommender."""
        logger.info("Initialized GuidelineRecommender (rule-based, no training required)")

    def _count_risk_factors(
        self, patient_data: pd.DataFrame, denormalized_data: Optional[pd.DataFrame] = None
    ) -> Dict[str, int]:
        """
        Count severe and moderate risk factors for escalation logic.

        Args:
            patient_data: Normalized patient data
            denormalized_data: Optional raw patient data for accurate threshold checking

        Returns:
            Dictionary with counts of severe and moderate risk factors
        """
        # Use denormalized data if available for accurate threshold checking
        data_to_check = denormalized_data if denormalized_data is not None else patient_data

        severe_count = 0
        moderate_count = 0
        risk_factor_details = []

        # Check blood pressure
        if "trestbps" in data_to_check.columns:
            bp = float(data_to_check["trestbps"].iloc[0])
            if bp >= SEVERE_RISK_FACTORS["trestbps"]:
                severe_count += 1
                risk_factor_details.append(f"severe hypertension (BP: {bp:.0f} mmHg)")
            elif bp >= MODERATE_RISK_FACTORS["trestbps"]:
                moderate_count += 1
                risk_factor_details.append(f"moderate hypertension (BP: {bp:.0f} mmHg)")

        # Check cholesterol
        if "chol" in data_to_check.columns:
            chol = float(data_to_check["chol"].iloc[0])
            if chol >= SEVERE_RISK_FACTORS["chol"]:
                severe_count += 1
                risk_factor_details.append(f"very high cholesterol ({chol:.0f} mg/dL)")
            elif chol >= MODERATE_RISK_FACTORS["chol"]:
                moderate_count += 1
                risk_factor_details.append(f"high cholesterol ({chol:.0f} mg/dL)")

        # Check ST depression (oldpeak)
        if "oldpeak" in data_to_check.columns:
            oldpeak = float(data_to_check["oldpeak"].iloc[0])
            if oldpeak >= SEVERE_RISK_FACTORS["oldpeak"]:
                severe_count += 1
                risk_factor_details.append(f"significant ST depression ({oldpeak:.1f})")
            elif oldpeak >= MODERATE_RISK_FACTORS["oldpeak"]:
                moderate_count += 1
                risk_factor_details.append(f"moderate ST depression ({oldpeak:.1f})")

        # Check exercise-induced angina
        if "exang" in data_to_check.columns and float(data_to_check["exang"].iloc[0]) == 1:
            moderate_count += 1
            risk_factor_details.append("exercise-induced angina")

        # Check number of major vessels colored by fluoroscopy
        if "ca" in data_to_check.columns:
            ca = int(data_to_check["ca"].iloc[0])
            if ca >= 3:
                severe_count += 1
                risk_factor_details.append(f"multiple vessel disease ({ca} vessels)")
            elif ca >= 1:
                moderate_count += 1
                risk_factor_details.append(f"vessel disease ({ca} vessel{'s' if ca > 1 else ''})")

        return {
            "severe": severe_count,
            "moderate": moderate_count,
            "details": risk_factor_details,
        }

    def _get_base_recommendation(self, risk_score: float) -> int:
        """
        Get base recommendation based on risk score thresholds.

        Args:
            risk_score: Predicted cardiovascular disease risk (0-100%)

        Returns:
            Base action index (0-4)
        """
        if risk_score < RISK_THRESHOLDS["very_low"]:
            return 0  # Monitor Only
        elif risk_score < RISK_THRESHOLDS["low"]:
            return 1  # Lifestyle Intervention
        elif risk_score < RISK_THRESHOLDS["medium"]:
            return 2  # Single Medication
        elif risk_score < RISK_THRESHOLDS["high"]:
            return 3  # Combination Therapy
        else:
            return 4  # Intensive Treatment

    def _apply_escalation_logic(
        self, base_action: int, risk_score: float, risk_factors: Dict[str, int]
    ) -> tuple[int, List[str]]:
        """
        Apply risk factor escalation logic to adjust base recommendation.

        Edge cases handled:
        - Multiple severe risk factors → escalate treatment even if base risk is lower
        - Single severe factor at borderline risk → consider escalation
        - Very low risk with no risk factors → confirm monitoring is appropriate

        Args:
            base_action: Base recommendation from risk score
            risk_score: Current risk score
            risk_factors: Dictionary with severe/moderate risk factor counts

        Returns:
            Tuple of (final_action, escalation_reasons)
        """
        final_action = base_action
        escalation_reasons = []

        # Edge case 1: Multiple severe risk factors
        if risk_factors["severe"] >= 2:
            if base_action < 3:
                final_action = 3  # Escalate to combination therapy
                escalation_reasons.append(
                    f"Multiple severe risk factors ({risk_factors['severe']}) warrant combination therapy"
                )

        # Edge case 2: Single severe factor + moderate factors at borderline risk
        elif risk_factors["severe"] >= 1 and risk_factors["moderate"] >= 2:
            if base_action < 2 and risk_score >= 20:
                final_action = 2  # Escalate to single medication
                escalation_reasons.append("Severe risk factor combined with multiple moderate factors warrants medication")

        # Edge case 3: High risk (≥50%) should never be just monitoring
        if risk_score >= 50 and final_action == 0:
            final_action = 3  # At least combination therapy
            escalation_reasons.append(f"High risk ({risk_score:.1f}%) requires active intervention")

        # Edge case 4: Very high risk (≥70%) should be intensive or combination
        if risk_score >= 70 and final_action < 3:
            final_action = 4  # Intensive treatment
            escalation_reasons.append(f"Very high risk ({risk_score:.1f}%) requires intensive treatment")

        # Edge case 5: Borderline cases - if risk is near threshold, consider risk factors
        if 25 <= risk_score < 35 and base_action == 1:  # Near low/medium boundary
            if risk_factors["severe"] >= 1 or risk_factors["moderate"] >= 3:
                final_action = 2  # Escalate to medication
                escalation_reasons.append("Borderline risk with significant risk factors warrants medication")

        return final_action, escalation_reasons

    def _generate_rationale(
        self,
        risk_score: float,
        action: int,
        base_action: int,
        risk_factors: Dict[str, int],
        escalation_reasons: List[str],
        patient_data: Optional[pd.DataFrame] = None,
    ) -> str:
        """
        Generate human-readable clinical rationale for the recommendation.

        Args:
            risk_score: Patient's risk score
            action: Final recommended action
            base_action: Initial recommendation before escalation
            risk_factors: Risk factor counts and details
            escalation_reasons: Reasons for any escalation
            patient_data: Optional patient data for enhanced reasoning

        Returns:
            Clinical rationale string
        """
        rationale_parts = []

        # Risk classification
        if risk_score < RISK_THRESHOLDS["very_low"]:
            risk_class = "very low"
        elif risk_score < RISK_THRESHOLDS["low"]:
            risk_class = "low"
        elif risk_score < RISK_THRESHOLDS["medium"]:
            risk_class = "medium"
        elif risk_score < RISK_THRESHOLDS["high"]:
            risk_class = "high"
        else:
            risk_class = "very high"

        rationale_parts.append(f"Patient has {risk_class} cardiovascular disease risk ({risk_score:.1f}%).")

        # Risk factors
        if risk_factors["severe"] > 0 or risk_factors["moderate"] > 0:
            factor_desc = []
            if risk_factors["severe"] > 0:
                factor_desc.append(f"{risk_factors['severe']} severe")
            if risk_factors["moderate"] > 0:
                factor_desc.append(f"{risk_factors['moderate']} moderate")
            rationale_parts.append(f"Identified {' and '.join(factor_desc)} risk factor(s).")

            if risk_factors["details"]:
                rationale_parts.append(f"Specific factors: {', '.join(risk_factors['details'])}.")

        # Check for structural heart disease indicators (if patient data available)
        has_structural_disease = False
        if patient_data is not None:
            # Check for thalassemia defect or multi-vessel disease
            if "thal" in patient_data.columns:
                thal = int(patient_data["thal"].iloc[0])
                if thal in [6, 7]:  # Fixed or reversible defect
                    has_structural_disease = True
            if "ca" in patient_data.columns:
                ca = int(patient_data["ca"].iloc[0])
                if ca >= 2:  # Multiple diseased vessels
                    has_structural_disease = True

        # Base recommendation
        action_name = ACTIONS[action]["name"]
        rationale_parts.append(f"Recommended intervention: {action_name}.")

        # Escalation rationale
        if escalation_reasons:
            rationale_parts.append("Escalation applied: " + " ".join(escalation_reasons))
        elif action == base_action:
            # Standard guideline-based recommendation with enhanced reasoning
            if action == 0:
                rationale_parts.append(
                    "Continue monitoring with regular checkups. "
                    "No active intervention needed for low-risk patients with optimal metrics."
                )
            elif action == 1:
                rationale_parts.append(
                    "Lifestyle modifications (diet, exercise, stress management) can effectively reduce modifiable risk factors. "
                    "Recommended as first-line intervention for low-to-moderate risk."
                )
            elif action == 2:
                rationale_parts.append(
                    "Single medication therapy (e.g., statin or ACE inhibitor) is guideline-recommended for this risk level. "
                    "Targets elevated blood pressure and cholesterol to reduce cardiovascular events."
                )
            elif action == 3:
                rationale_parts.append(
                    "Combination therapy (medication + supervised lifestyle program) is guideline-recommended for high risk. "
                    "Provides comprehensive risk reduction by addressing multiple modifiable factors simultaneously."
                )
            elif action == 4:
                rationale_parts.append(
                    "Intensive treatment with multiple medications and lifestyle management is warranted for very high risk. "
                    "Maximal intervention to reduce modifiable risk factors and prevent cardiovascular events."
                )

        # Add note about structural disease limitations
        if has_structural_disease and action >= 2:
            rationale_parts.append(
                "Note: This patient has structural heart disease (vessel disease or thalassemia defects) "
                "which cannot be fully reversed by medication or lifestyle changes. "
                "The recommended treatment focuses on managing modifiable risk factors to slow disease progression."
            )

        return " ".join(rationale_parts)

    def recommend(
        self, patient_data: pd.DataFrame, risk_predictor, denormalized_data: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Recommend optimal intervention for a patient using clinical guidelines.

        Args:
            patient_data: Patient features (raw values - no normalization needed)
            risk_predictor: Trained RiskPredictor to estimate risk scores
            denormalized_data: Optional raw patient data for accurate threshold checking (defaults to patient_data if not provided)

        Returns:
            Dictionary containing:
                - action: Recommended action index (0-4)
                - action_name: Human-readable action name
                - description: Detailed action description
                - cost: Estimated cost level
                - intensity: Treatment intensity
                - expected_risk_reduction: Estimated reduction in risk score
                - current_risk: Current risk score
                - expected_final_risk: Expected risk after intervention
                - rationale: Clinical reasoning for the recommendation
                - risk_factors: Details of identified risk factors
        """
        # Use denormalized_data if provided, otherwise use patient_data
        data_for_thresholds = denormalized_data if denormalized_data is not None else patient_data

        # Get current risk prediction
        current_prediction = risk_predictor.predict(patient_data)
        current_risk = current_prediction["risk_score"]

        # Count risk factors using raw patient data
        risk_factors = self._count_risk_factors(patient_data, data_for_thresholds)

        # Get base recommendation from risk score
        base_action = self._get_base_recommendation(current_risk)

        # Apply escalation logic for edge cases
        action, escalation_reasons = self._apply_escalation_logic(base_action, current_risk, risk_factors)

        # Get action information
        action_info = ACTIONS[action]

        # Generate clinical rationale
        rationale = self._generate_rationale(
            current_risk, action, base_action, risk_factors, escalation_reasons, patient_data=data_for_thresholds
        )

        # Estimate expected outcome (using intervention simulation)
        from ml.intervention_utils import apply_intervention_effects

        # Apply intervention effects to raw data
        modified_data = apply_intervention_effects(patient_data.copy(), action)

        # Get new risk prediction (no scaling needed)
        next_prediction = risk_predictor.predict(modified_data)

        expected_risk_raw = next_prediction["risk_score"]

        # Apply monotonicity safeguard: interventions should never increase risk
        # This prevents paradoxical outcomes from model artifacts with extreme cases
        if action > 0 and expected_risk_raw > current_risk:
            # If intervention would increase risk, cap it at current risk
            expected_risk = float(current_risk)
            logger.warning(
                f"Monotonicity correction applied: Action {action} predicted "
                f"risk increase {current_risk:.1f}% → {expected_risk_raw:.1f}%, "
                f"capped at {expected_risk:.1f}%"
            )
        else:
            expected_risk = float(expected_risk_raw)

        recommendation = {
            "action": int(action),
            "action_name": action_info["name"],
            "description": action_info["description"],
            "cost": action_info["cost"],
            "intensity": action_info["intensity"],
            "current_risk": float(current_risk),
            "expected_final_risk": float(expected_risk),
            "expected_risk_reduction": float(current_risk - expected_risk),
            "rationale": rationale,
            "risk_factors": {
                "severe_count": risk_factors["severe"],
                "moderate_count": risk_factors["moderate"],
                "details": risk_factors["details"],
            },
        }

        logger.info(
            f"Recommendation: {action_info['name']} (risk {current_risk:.1f}% → {expected_risk:.1f}%) - {rationale[:100]}..."
        )

        return recommendation

    def save(self, path: Path) -> None:
        """
        Save recommender configuration to disk.

        Note: This is a no-op for guideline-based recommender since there are no
        learned parameters. Included for API compatibility with RL agent.

        Args:
            path: Path to save the recommender (will create empty marker file)
        """
        import json

        config = {
            "type": "guideline_recommender",
            "version": "1.0",
            "risk_thresholds": RISK_THRESHOLDS,
            "note": "No training required - purely rule-based",
        }

        with open(path, "w") as f:
            json.dump(config, f, indent=2)

        logger.info(f"Guideline recommender configuration saved to {path}")

    def load(self, path: Path) -> None:
        """
        Load recommender configuration from disk.

        Note: This is a no-op for guideline-based recommender since there are no
        learned parameters. Included for API compatibility with RL agent.

        Args:
            path: Path to saved recommender file
        """
        import json

        if not path.exists():
            logger.warning(f"Recommender file not found: {path}. Using default configuration.")
            return

        try:
            # Try to load as JSON (guideline recommender format)
            with open(path, "r") as f:
                config = json.load(f)

            logger.info(f"Guideline recommender configuration loaded from {path}")
            logger.info(f"Type: {config.get('type')}, Version: {config.get('version')}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            # File exists but is not JSON (likely old RL agent pickle file)
            logger.info(
                f"File at {path} is not a guideline recommender configuration (likely RL agent). "
                "Using default guideline recommender configuration."
            )


def main():
    """
    Main function for testing the guideline-based recommender.

    Demonstrates the complete workflow:
    1. Load risk predictor model
    2. Load training data
    3. Test recommendations on sample patients
    4. Compare with different risk profiles
    """
    import sys
    from pathlib import Path

    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from data.load import load_processed_data
    from ml.risk_predictor import RiskPredictor

    logger.info("=" * 80)
    logger.info("HealthGuard - Guideline-Based Intervention Recommender")
    logger.info("=" * 80)

    # Load data
    logger.info("\n[1/4] Loading processed data and risk predictor...")
    train_df, val_df, test_df = load_processed_data()

    # Load trained risk predictor
    model_path = Path(__file__).parent.parent / "models" / "risk_predictor.pkl"
    if not model_path.exists():
        logger.error(f"Risk predictor not found at {model_path}")
        logger.error("Please train the risk predictor first: python -m ml.risk_predictor")
        return

    predictor = RiskPredictor()
    predictor.load(model_path)
    logger.info("Loaded trained risk predictor")

    # Initialize recommender
    logger.info("\n[2/4] Initializing guideline-based recommender...")
    recommender = GuidelineRecommender()

    # Test on sample patients with different risk profiles
    logger.info("\n[3/4] Testing recommendations on sample patients...")
    test_features = test_df.drop("target", axis=1, errors="ignore")

    # Get risk predictions for all test patients to find diverse examples
    test_risks = []
    for i in range(len(test_features)):
        patient = test_features.iloc[[i]]
        risk_pred = predictor.predict(patient)
        test_risks.append((i, risk_pred["risk_score"]))

    # Sort by risk score and pick diverse examples
    test_risks.sort(key=lambda x: x[1])
    sample_indices = [
        test_risks[0][0],  # Lowest risk
        test_risks[len(test_risks) // 4][0],  # 25th percentile
        test_risks[len(test_risks) // 2][0],  # Median
        test_risks[3 * len(test_risks) // 4][0],  # 75th percentile
        test_risks[-1][0],  # Highest risk
    ]

    for idx in sample_indices:
        logger.info(f"\n--- Patient {idx+1} ---")
        patient = test_features.iloc[[idx]]

        # Get risk prediction
        risk_pred = predictor.predict(patient)
        logger.info(f"Current Risk: {risk_pred['risk_score']:.1f}% ({risk_pred['classification']})")

        # Get guideline-based recommendation
        recommendation = recommender.recommend(patient, predictor)
        logger.info(f"Recommended Intervention: {recommendation['action_name']}")
        logger.info(f"Expected Risk Reduction: {recommendation['expected_risk_reduction']:.1f}%")
        logger.info(f"Cost: {recommendation['cost']}, Intensity: {recommendation['intensity']}")
        logger.info(f"Rationale: {recommendation['rationale']}")

    # Save recommender configuration
    logger.info("\n[4/4] Saving recommender configuration...")
    recommender_dir = Path(__file__).parent.parent / "models"
    recommender_dir.mkdir(exist_ok=True)
    recommender_path = recommender_dir / "guideline_recommender.json"
    recommender.save(recommender_path)

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TESTING SUMMARY")
    logger.info("=" * 80)
    logger.info("Guideline-based recommender is ready to use!")
    logger.info("Key features:")
    logger.info("  - No training required (rule-based)")
    logger.info("  - Explainable recommendations based on clinical guidelines")
    logger.info("  - Edge case handling with risk factor escalation")
    logger.info("  - API-compatible with existing RL agent")
    logger.info(f"\nConfiguration saved to: {recommender_path}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
