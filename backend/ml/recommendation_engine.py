"""
Personalized Intervention Recommendation Engine

This module provides intelligent intervention recommendations based on:
- Patient's baseline risk level
- Magnitude of potential risk reduction
- Cost-benefit analysis
- Clinical guidelines
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class InterventionRecommender:
    """
    Recommends optimal interventions based on patient risk profile.
    """

    # Intervention definitions with clinical context
    INTERVENTIONS = {
        1: {
            "name": "Lifestyle Modifications",
            "description": "Diet, exercise, stress management",
            "cost": "Low",
            "side_effects": "Minimal",
            "monitoring": "Self-monitoring",
        },
        2: {
            "name": "Single Medication",
            "description": "BP medication OR statin therapy",
            "cost": "Low-Moderate",
            "side_effects": "Low",
            "monitoring": "Quarterly check-ups",
        },
        3: {
            "name": "Combination Therapy",
            "description": "BP medication AND statin therapy",
            "cost": "Moderate",
            "side_effects": "Moderate",
            "monitoring": "Monthly check-ups initially",
        },
        4: {
            "name": "Intensive Treatment",
            "description": "Multi-drug therapy with close monitoring",
            "cost": "High",
            "side_effects": "Higher risk",
            "monitoring": "Frequent monitoring required",
        },
    }

    @staticmethod
    def recommend_intervention(baseline_risk: float, intervention_results: Dict[int, Dict[str, float]]) -> Dict:
        """
        Recommend the most appropriate intervention based on risk level and outcomes.

        Args:
            baseline_risk: Patient's current cardiovascular risk (0-100%)
            intervention_results: Dict mapping action_id -> {
                'new_risk': float,
                'risk_reduction': float,
                'pct_reduction': float
            }

        Returns:
            Dict containing:
                - recommended_action: int (action ID)
                - recommendation_name: str
                - rationale: str (why this intervention is recommended)
                - alternative: int (alternative action ID)
                - all_options: List of all intervention options with outcomes
        """

        # Primary recommendation based on risk tier
        if baseline_risk >= 70:
            # HIGH RISK: Aggressive intervention needed
            primary = 4
            alternative = 3
            rationale = (
                f"Your cardiovascular risk is very high ({baseline_risk:.1f}%). "
                f"Intensive treatment is recommended to achieve maximum risk reduction. "
                f"This typically involves multiple medications and close medical monitoring."
            )

        elif baseline_risk >= 50:
            # MEDIUM-HIGH RISK: Substantial intervention warranted
            primary = 3
            alternative = 4
            rationale = (
                f"Your cardiovascular risk is elevated ({baseline_risk:.1f}%). "
                f"Combination therapy (BP medication + statin) offers a good balance "
                f"of effectiveness and tolerability for your risk level."
            )

        elif baseline_risk >= 30:
            # MEDIUM RISK: Moderate intervention
            primary = 3
            alternative = 2
            rationale = (
                f"Your cardiovascular risk is moderate ({baseline_risk:.1f}%). "
                f"Combination therapy is recommended, though your doctor may start with "
                f"single medication depending on your BP and cholesterol levels."
            )

        elif baseline_risk >= 15:
            # LOW-MEDIUM RISK: Conservative approach
            primary = 2
            alternative = 3
            rationale = (
                f"Your cardiovascular risk is low-moderate ({baseline_risk:.1f}%). "
                f"Single medication (either BP medication or statin) combined with "
                f"lifestyle changes is typically sufficient."
            )

        else:
            # LOW RISK: Prevention focus
            primary = 1
            alternative = 2
            rationale = (
                f"Your cardiovascular risk is low ({baseline_risk:.1f}%). "
                f"Focus on maintaining healthy lifestyle habits. Medication may not be "
                f"necessary unless you have other risk factors."
            )

        # Build comprehensive options list
        all_options = []
        for action_id in sorted(intervention_results.keys()):
            result = intervention_results[action_id]
            intervention_info = InterventionRecommender.INTERVENTIONS[action_id]

            option = {
                "action_id": action_id,
                "name": intervention_info["name"],
                "description": intervention_info["description"],
                "new_risk": result["new_risk"],
                "risk_reduction": result["risk_reduction"],
                "pct_reduction": result["pct_reduction"],
                "cost": intervention_info["cost"],
                "side_effects": intervention_info["side_effects"],
                "monitoring": intervention_info["monitoring"],
                "is_recommended": action_id == primary,
                "is_alternative": action_id == alternative,
            }
            all_options.append(option)

        primary_info = InterventionRecommender.INTERVENTIONS[primary]

        return {
            "recommended_action": primary,
            "recommendation_name": primary_info["name"],
            "recommendation_description": primary_info["description"],
            "rationale": rationale,
            "alternative_action": alternative,
            "alternative_name": InterventionRecommender.INTERVENTIONS[alternative]["name"],
            "all_options": all_options,
            "baseline_risk": baseline_risk,
            "risk_tier": InterventionRecommender._get_risk_tier(baseline_risk),
        }

    @staticmethod
    def _get_risk_tier(risk: float) -> str:
        """Classify risk into tiers."""
        if risk >= 70:
            return "Very High Risk"
        elif risk >= 50:
            return "High Risk"
        elif risk >= 30:
            return "Moderate Risk"
        elif risk >= 15:
            return "Low-Moderate Risk"
        else:
            return "Low Risk"

    @staticmethod
    def get_intervention_details(action_id: int) -> Dict:
        """Get detailed information about a specific intervention."""
        if action_id not in InterventionRecommender.INTERVENTIONS:
            raise ValueError(f"Invalid action_id: {action_id}")

        return InterventionRecommender.INTERVENTIONS[action_id]
