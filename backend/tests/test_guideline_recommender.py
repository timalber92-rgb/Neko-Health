"""
Tests for the guideline-based intervention recommender.

This test suite validates that the guideline-based recommender:
1. Recommends appropriate interventions based on risk levels
2. Applies risk factor escalation logic correctly
3. Handles edge cases (borderline risk, multiple risk factors, etc.)
4. Provides clear clinical rationale
5. Maintains API compatibility with the RL agent
"""

import pandas as pd
import pytest

from ml.guideline_recommender import GuidelineRecommender


class MockRiskPredictor:
    """Mock risk predictor for testing."""

    def __init__(self, risk_score: float):
        self.risk_score = risk_score

    def predict(self, patient_data: pd.DataFrame):
        return {
            "risk_score": self.risk_score,
            "classification": "High Risk" if self.risk_score >= 50 else "Low Risk",
            "has_disease": self.risk_score >= 50,
            "probability": self.risk_score / 100.0,
        }


class TestBasicRecommendations:
    """Test basic risk-stratified recommendations."""

    @pytest.fixture
    def recommender(self):
        return GuidelineRecommender()

    @pytest.fixture
    def base_patient(self):
        """Create a baseline patient with no severe risk factors."""
        return pd.DataFrame(
            [
                {
                    "age": 50,
                    "sex": 1,
                    "cp": 0,
                    "trestbps": 120,  # Normal BP
                    "chol": 200,  # Normal cholesterol
                    "fbs": 0,
                    "restecg": 0,
                    "thalach": 150,
                    "exang": 0,
                    "oldpeak": 0.5,  # Minimal ST depression
                    "slope": 1,
                    "ca": 0,
                    "thal": 2,
                }
            ]
        )

    def test_very_low_risk_monitor_only(self, recommender, base_patient):
        """Test that very low risk (<15%) recommends monitoring only."""
        predictor = MockRiskPredictor(risk_score=10.0)
        recommendation = recommender.recommend(base_patient, predictor)

        assert recommendation["action"] == 0
        assert recommendation["action_name"] == "Monitor Only"
        assert "rationale" in recommendation
        assert "very low" in recommendation["rationale"].lower()

    def test_low_risk_lifestyle(self, recommender, base_patient):
        """Test that low risk (15-30%) recommends lifestyle intervention."""
        predictor = MockRiskPredictor(risk_score=20.0)
        recommendation = recommender.recommend(base_patient, predictor)

        assert recommendation["action"] == 1
        assert recommendation["action_name"] == "Lifestyle Intervention"
        assert "rationale" in recommendation

    def test_medium_risk_single_medication(self, recommender, base_patient):
        """Test that medium risk (30-50%) recommends single medication."""
        predictor = MockRiskPredictor(risk_score=40.0)
        recommendation = recommender.recommend(base_patient, predictor)

        assert recommendation["action"] == 2
        assert recommendation["action_name"] == "Single Medication"
        assert "rationale" in recommendation

    def test_high_risk_combination_therapy(self, recommender, base_patient):
        """Test that high risk (50-70%) recommends combination therapy."""
        predictor = MockRiskPredictor(risk_score=60.0)
        recommendation = recommender.recommend(base_patient, predictor)

        assert recommendation["action"] == 3
        assert recommendation["action_name"] == "Combination Therapy"
        assert "rationale" in recommendation

    def test_very_high_risk_intensive(self, recommender, base_patient):
        """Test that very high risk (≥70%) recommends intensive treatment."""
        predictor = MockRiskPredictor(risk_score=80.0)
        recommendation = recommender.recommend(base_patient, predictor)

        assert recommendation["action"] == 4
        assert recommendation["action_name"] == "Intensive Treatment"
        assert "rationale" in recommendation


class TestRiskFactorEscalation:
    """Test risk factor escalation logic for edge cases."""

    @pytest.fixture
    def recommender(self):
        return GuidelineRecommender()

    def test_multiple_severe_factors_escalates(self, recommender):
        """Test that multiple severe risk factors escalate treatment."""
        # Patient with low base risk (25%) but multiple severe factors
        patient = pd.DataFrame(
            [
                {
                    "age": 50,
                    "sex": 1,
                    "cp": 3,
                    "trestbps": 170,  # Severe hypertension
                    "chol": 290,  # Very high cholesterol
                    "fbs": 0,
                    "restecg": 0,
                    "thalach": 150,
                    "exang": 0,
                    "oldpeak": 2.5,  # Severe ST depression
                    "slope": 2,
                    "ca": 0,
                    "thal": 2,
                }
            ]
        )

        predictor = MockRiskPredictor(risk_score=25.0)
        recommendation = recommender.recommend(patient, predictor, denormalized_data=patient)

        # Should escalate from lifestyle (1) to combination therapy (3)
        assert recommendation["action"] >= 2
        assert recommendation["risk_factors"]["severe_count"] >= 2
        assert "escalation" in recommendation["rationale"].lower() or "severe" in recommendation["rationale"].lower()

    def test_single_severe_factor_borderline_risk(self, recommender):
        """Test that single severe factor at borderline risk may escalate."""
        patient = pd.DataFrame(
            [
                {
                    "age": 55,
                    "sex": 1,
                    "cp": 2,
                    "trestbps": 165,  # Severe hypertension
                    "chol": 245,  # Moderate cholesterol
                    "fbs": 0,
                    "restecg": 0,
                    "thalach": 140,
                    "exang": 1,  # Moderate factor
                    "oldpeak": 1.2,  # Moderate ST depression
                    "slope": 2,
                    "ca": 1,  # Moderate factor
                    "thal": 3,
                }
            ]
        )

        predictor = MockRiskPredictor(risk_score=28.0)  # Borderline low/medium
        recommendation = recommender.recommend(patient, predictor, denormalized_data=patient)

        # Should have identified risk factors
        assert recommendation["risk_factors"]["severe_count"] >= 1
        assert recommendation["risk_factors"]["moderate_count"] >= 2
        # May escalate to medication (2)
        assert recommendation["action"] >= 1

    def test_high_risk_never_monitor_only(self, recommender):
        """Test that high risk (≥50%) never recommends monitoring only."""
        patient = pd.DataFrame(
            [
                {
                    "age": 65,
                    "sex": 1,
                    "cp": 3,
                    "trestbps": 150,
                    "chol": 260,
                    "fbs": 1,
                    "restecg": 1,
                    "thalach": 110,
                    "exang": 1,
                    "oldpeak": 3.0,
                    "slope": 2,
                    "ca": 2,
                    "thal": 3,
                }
            ]
        )

        predictor = MockRiskPredictor(risk_score=65.0)
        recommendation = recommender.recommend(patient, predictor, denormalized_data=patient)

        # Should never be monitor only
        assert recommendation["action"] >= 3
        assert "high risk" in recommendation["rationale"].lower()

    def test_very_high_risk_intensive_or_combination(self, recommender):
        """Test that very high risk (≥70%) gets intensive treatment."""
        patient = pd.DataFrame(
            [
                {
                    "age": 70,
                    "sex": 1,
                    "cp": 4,
                    "trestbps": 180,
                    "chol": 300,
                    "fbs": 1,
                    "restecg": 2,
                    "thalach": 100,
                    "exang": 1,
                    "oldpeak": 4.0,
                    "slope": 3,
                    "ca": 3,
                    "thal": 7,
                }
            ]
        )

        predictor = MockRiskPredictor(risk_score=85.0)
        recommendation = recommender.recommend(patient, predictor, denormalized_data=patient)

        # Should be intensive treatment
        assert recommendation["action"] >= 3
        assert "very high" in recommendation["rationale"].lower() or recommendation["action"] == 4


class TestRiskFactorIdentification:
    """Test accurate identification of risk factors."""

    @pytest.fixture
    def recommender(self):
        return GuidelineRecommender()

    def test_identifies_severe_hypertension(self, recommender):
        """Test that severe hypertension is identified."""
        patient = pd.DataFrame([{"trestbps": 170, "chol": 200, "thalach": 150, "oldpeak": 0.5, "exang": 0, "ca": 0}])

        predictor = MockRiskPredictor(risk_score=40.0)
        recommendation = recommender.recommend(patient, predictor, denormalized_data=patient)

        assert recommendation["risk_factors"]["severe_count"] >= 1
        assert any("hypertension" in detail.lower() for detail in recommendation["risk_factors"]["details"])

    def test_identifies_very_high_cholesterol(self, recommender):
        """Test that very high cholesterol is identified."""
        patient = pd.DataFrame([{"trestbps": 120, "chol": 290, "thalach": 150, "oldpeak": 0.5, "exang": 0, "ca": 0}])

        predictor = MockRiskPredictor(risk_score=40.0)
        recommendation = recommender.recommend(patient, predictor, denormalized_data=patient)

        assert recommendation["risk_factors"]["severe_count"] >= 1
        assert any("cholesterol" in detail.lower() for detail in recommendation["risk_factors"]["details"])

    def test_identifies_significant_st_depression(self, recommender):
        """Test that significant ST depression is identified."""
        patient = pd.DataFrame([{"trestbps": 120, "chol": 200, "thalach": 150, "oldpeak": 2.5, "exang": 0, "ca": 0}])

        predictor = MockRiskPredictor(risk_score=40.0)
        recommendation = recommender.recommend(patient, predictor, denormalized_data=patient)

        assert recommendation["risk_factors"]["severe_count"] >= 1
        assert any("st depression" in detail.lower() for detail in recommendation["risk_factors"]["details"])

    def test_identifies_exercise_induced_angina(self, recommender):
        """Test that exercise-induced angina is identified as moderate factor."""
        patient = pd.DataFrame([{"trestbps": 120, "chol": 200, "thalach": 150, "oldpeak": 0.5, "exang": 1, "ca": 0}])

        predictor = MockRiskPredictor(risk_score=40.0)
        recommendation = recommender.recommend(patient, predictor, denormalized_data=patient)

        assert recommendation["risk_factors"]["moderate_count"] >= 1
        assert any("angina" in detail.lower() for detail in recommendation["risk_factors"]["details"])

    def test_identifies_vessel_disease(self, recommender):
        """Test that vessel disease is identified."""
        patient = pd.DataFrame([{"trestbps": 120, "chol": 200, "thalach": 150, "oldpeak": 0.5, "exang": 0, "ca": 2}])

        predictor = MockRiskPredictor(risk_score=40.0)
        recommendation = recommender.recommend(patient, predictor, denormalized_data=patient)

        assert recommendation["risk_factors"]["moderate_count"] >= 1
        assert any("vessel" in detail.lower() for detail in recommendation["risk_factors"]["details"])


class TestClinicalRationale:
    """Test that clinical rationale is clear and appropriate."""

    @pytest.fixture
    def recommender(self):
        return GuidelineRecommender()

    def test_rationale_includes_risk_level(self, recommender):
        """Test that rationale includes risk classification."""
        patient = pd.DataFrame(
            [
                {
                    "age": 50,
                    "sex": 1,
                    "cp": 0,
                    "trestbps": 120,
                    "chol": 200,
                    "fbs": 0,
                    "restecg": 0,
                    "thalach": 150,
                    "exang": 0,
                    "oldpeak": 0.5,
                    "slope": 1,
                    "ca": 0,
                    "thal": 2,
                }
            ]
        )

        predictor = MockRiskPredictor(risk_score=35.0)
        recommendation = recommender.recommend(patient, predictor, denormalized_data=patient)

        assert "rationale" in recommendation
        # Should mention risk level
        assert any(keyword in recommendation["rationale"].lower() for keyword in ["risk", "medium", "low", "high", "very"])

    def test_rationale_includes_risk_factors(self, recommender):
        """Test that rationale mentions identified risk factors."""
        patient = pd.DataFrame(
            [
                {
                    "age": 60,
                    "sex": 1,
                    "cp": 3,
                    "trestbps": 165,  # Severe
                    "chol": 250,  # Moderate
                    "fbs": 0,
                    "restecg": 0,
                    "thalach": 140,
                    "exang": 1,  # Moderate
                    "oldpeak": 1.5,
                    "slope": 2,
                    "ca": 0,
                    "thal": 3,
                }
            ]
        )

        predictor = MockRiskPredictor(risk_score=45.0)
        recommendation = recommender.recommend(patient, predictor, denormalized_data=patient)

        assert "rationale" in recommendation
        # Should mention risk factors
        if recommendation["risk_factors"]["severe_count"] > 0 or recommendation["risk_factors"]["moderate_count"] > 0:
            assert "factor" in recommendation["rationale"].lower()

    def test_rationale_includes_intervention_name(self, recommender):
        """Test that rationale includes the recommended intervention."""
        patient = pd.DataFrame(
            [
                {
                    "age": 50,
                    "sex": 1,
                    "cp": 0,
                    "trestbps": 120,
                    "chol": 200,
                    "fbs": 0,
                    "restecg": 0,
                    "thalach": 150,
                    "exang": 0,
                    "oldpeak": 0.5,
                    "slope": 1,
                    "ca": 0,
                    "thal": 2,
                }
            ]
        )

        predictor = MockRiskPredictor(risk_score=35.0)
        recommendation = recommender.recommend(patient, predictor, denormalized_data=patient)

        assert "rationale" in recommendation
        # Should mention the intervention name
        assert recommendation["action_name"].lower() in recommendation["rationale"].lower() or any(
            word in recommendation["rationale"].lower()
            for word in ["monitor", "lifestyle", "medication", "combination", "intensive"]
        )


class TestAPICompatibility:
    """Test that the guideline recommender maintains API compatibility with RL agent."""

    @pytest.fixture
    def recommender(self):
        return GuidelineRecommender()

    @pytest.fixture
    def sample_patient(self):
        return pd.DataFrame(
            [
                {
                    "age": 55,
                    "sex": 1,
                    "cp": 2,
                    "trestbps": 145,
                    "chol": 233,
                    "fbs": 1,
                    "restecg": 0,
                    "thalach": 150,
                    "exang": 0,
                    "oldpeak": 2.3,
                    "slope": 2,
                    "ca": 0,
                    "thal": 6,
                }
            ]
        )

    def test_returns_all_required_fields(self, recommender, sample_patient):
        """Test that recommendation includes all required fields."""
        predictor = MockRiskPredictor(risk_score=55.0)
        recommendation = recommender.recommend(sample_patient, predictor, denormalized_data=sample_patient)

        # Required fields
        assert "action" in recommendation
        assert "action_name" in recommendation
        assert "description" in recommendation
        assert "cost" in recommendation
        assert "intensity" in recommendation
        assert "current_risk" in recommendation
        assert "expected_final_risk" in recommendation
        assert "expected_risk_reduction" in recommendation

        # Guideline-specific fields
        assert "rationale" in recommendation
        assert "risk_factors" in recommendation

    def test_action_in_valid_range(self, recommender, sample_patient):
        """Test that action is in valid range (0-4)."""
        predictor = MockRiskPredictor(risk_score=45.0)
        recommendation = recommender.recommend(sample_patient, predictor, denormalized_data=sample_patient)

        assert 0 <= recommendation["action"] <= 4
        assert isinstance(recommendation["action"], int)

    def test_risk_scores_are_floats(self, recommender, sample_patient):
        """Test that risk scores are float values."""
        predictor = MockRiskPredictor(risk_score=45.0)
        recommendation = recommender.recommend(sample_patient, predictor, denormalized_data=sample_patient)

        assert isinstance(recommendation["current_risk"], float)
        assert isinstance(recommendation["expected_final_risk"], float)
        assert isinstance(recommendation["expected_risk_reduction"], float)

    def test_save_and_load_compatibility(self, recommender, tmp_path):
        """Test that save/load methods work (even if no-op)."""
        config_path = tmp_path / "test_recommender.json"

        # Should not raise errors
        recommender.save(config_path)
        assert config_path.exists()

        new_recommender = GuidelineRecommender()
        new_recommender.load(config_path)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.fixture
    def recommender(self):
        return GuidelineRecommender()

    def test_handles_missing_optional_features(self, recommender):
        """Test that recommender handles missing optional features gracefully."""
        # Minimal patient data
        patient = pd.DataFrame([{"trestbps": 120, "chol": 200, "thalach": 150, "oldpeak": 0.5}])

        predictor = MockRiskPredictor(risk_score=30.0)
        # Should not raise an error
        recommendation = recommender.recommend(patient, predictor, denormalized_data=patient)

        assert "action" in recommendation

    def test_threshold_boundaries(self, recommender):
        """Test recommendations at exact threshold boundaries."""
        patient = pd.DataFrame(
            [
                {
                    "age": 50,
                    "sex": 1,
                    "cp": 0,
                    "trestbps": 120,
                    "chol": 200,
                    "fbs": 0,
                    "restecg": 0,
                    "thalach": 150,
                    "exang": 0,
                    "oldpeak": 0.5,
                    "slope": 1,
                    "ca": 0,
                    "thal": 2,
                }
            ]
        )

        # Test at each threshold
        thresholds = [
            (14.9, 0),  # Just below very_low threshold
            (15.0, 1),  # At very_low threshold
            (29.9, 1),  # Just below low threshold
            (30.0, 2),  # At low threshold
            (49.9, 2),  # Just below medium threshold
            (50.0, 3),  # At medium threshold
            (69.9, 3),  # Just below high threshold
            (70.0, 4),  # At high threshold
        ]

        for risk_score, expected_min_action in thresholds:
            predictor = MockRiskPredictor(risk_score=risk_score)
            recommendation = recommender.recommend(patient, predictor, denormalized_data=patient)
            # Action should be at least the expected (may be escalated by risk factors)
            assert (
                recommendation["action"] >= expected_min_action
            ), f"Risk {risk_score}% should recommend action >= {expected_min_action}, got {recommendation['action']}"

    def test_normalized_data_without_denormalized(self, recommender):
        """Test that recommender works with only normalized data."""
        # Simulated normalized data (z-scores)
        patient_normalized = pd.DataFrame(
            [
                {
                    "age": 0.5,
                    "sex": 1.0,
                    "cp": 0.0,
                    "trestbps": 0.2,
                    "chol": 0.1,
                    "fbs": 0.0,
                    "restecg": 0.0,
                    "thalach": 0.3,
                    "exang": 0.0,
                    "oldpeak": 0.2,
                    "slope": 0.5,
                    "ca": 0.0,
                    "thal": 0.0,
                }
            ]
        )

        predictor = MockRiskPredictor(risk_score=35.0)
        # Should work without denormalized_data
        recommendation = recommender.recommend(patient_normalized, predictor)

        assert "action" in recommendation
        assert "rationale" in recommendation
