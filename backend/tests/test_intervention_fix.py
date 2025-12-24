"""
Tests for the intervention fix that prevents paradoxical risk increases.

This test suite validates that the fix for healthy patient intervention
paradox works correctly by ensuring:
1. Healthy patients with optimal metrics see minimal/no changes
2. Unhealthy patients receive appropriate therapeutic effects
3. State-dependent interventions are applied correctly
"""

import pytest
import pandas as pd
from ml.intervention_utils import apply_intervention_effects


class TestHealthyPatientInterventions:
    """Test that healthy patients don't get paradoxical risk increases"""

    @pytest.fixture
    def healthy_patient(self):
        """Create a healthy patient with optimal metrics"""
        return pd.DataFrame(
            [
                {
                    "age": 45,
                    "sex": 1,
                    "cp": 0,
                    "trestbps": 110,  # Optimal blood pressure
                    "chol": 180,  # Optimal cholesterol
                    "fbs": 0,
                    "restecg": 0,
                    "thalach": 160,  # Good max heart rate
                    "exang": 0,
                    "oldpeak": 0.0,  # No ST depression
                    "slope": 1,
                    "ca": 0,
                    "thal": 2,
                }
            ]
        )

    def test_lifestyle_intervention_minimal_changes(self, healthy_patient):
        """Test that lifestyle intervention makes minimal changes to healthy patient"""
        modified = apply_intervention_effects(healthy_patient, action=1)

        # For healthy patients with optimal metrics, changes should be minimal or none
        assert modified["trestbps"].iloc[0] == pytest.approx(
            healthy_patient["trestbps"].iloc[0], abs=1
        )
        assert modified["chol"].iloc[0] == pytest.approx(
            healthy_patient["chol"].iloc[0], abs=1
        )
        assert modified["thalach"].iloc[0] == pytest.approx(
            healthy_patient["thalach"].iloc[0], abs=1
        )

    def test_monitor_only_no_changes(self, healthy_patient):
        """Test that monitor only action makes no changes"""
        modified = apply_intervention_effects(healthy_patient, action=0)

        # Should be identical
        pd.testing.assert_frame_equal(modified, healthy_patient)

    def test_all_actions_preserve_healthy_metrics(self, healthy_patient):
        """Test that all interventions preserve healthy metrics"""
        for action in range(5):
            modified = apply_intervention_effects(healthy_patient, action=action)

            # Metrics should stay within healthy ranges
            assert 90 <= modified["trestbps"].iloc[0] <= 140
            assert 120 <= modified["chol"].iloc[0] <= 220
            assert 140 <= modified["thalach"].iloc[0] <= 220
            assert 0.0 <= modified["oldpeak"].iloc[0] <= 1.0


class TestUnhealthyPatientInterventions:
    """Test that unhealthy patients receive appropriate therapeutic effects"""

    @pytest.fixture
    def unhealthy_patient(self):
        """Create an unhealthy patient with elevated risk factors"""
        return pd.DataFrame(
            [
                {
                    "age": 60,
                    "sex": 1,
                    "cp": 3,
                    "trestbps": 160,  # High blood pressure
                    "chol": 280,  # High cholesterol
                    "fbs": 1,
                    "restecg": 1,
                    "thalach": 120,  # Low max heart rate
                    "exang": 1,
                    "oldpeak": 2.5,  # Significant ST depression
                    "slope": 2,
                    "ca": 2,
                    "thal": 3,
                }
            ]
        )

    def test_lifestyle_intervention_reduces_risk_factors(self, unhealthy_patient):
        """Test that lifestyle intervention reduces BP and cholesterol"""
        modified = apply_intervention_effects(unhealthy_patient, action=1)

        # Should see reductions in risk factors
        assert modified["trestbps"].iloc[0] < unhealthy_patient["trestbps"].iloc[0]
        assert modified["chol"].iloc[0] < unhealthy_patient["chol"].iloc[0]
        assert modified["thalach"].iloc[0] >= unhealthy_patient["thalach"].iloc[0]

    def test_intensive_treatment_stronger_effects(self, unhealthy_patient):
        """Test that intensive treatment has stronger effects than lifestyle"""
        lifestyle = apply_intervention_effects(unhealthy_patient, action=1)
        intensive = apply_intervention_effects(unhealthy_patient, action=4)

        # Intensive should have greater reductions
        bp_reduction_lifestyle = (
            unhealthy_patient["trestbps"].iloc[0] - lifestyle["trestbps"].iloc[0]
        )
        bp_reduction_intensive = (
            unhealthy_patient["trestbps"].iloc[0] - intensive["trestbps"].iloc[0]
        )

        chol_reduction_lifestyle = (
            unhealthy_patient["chol"].iloc[0] - lifestyle["chol"].iloc[0]
        )
        chol_reduction_intensive = (
            unhealthy_patient["chol"].iloc[0] - intensive["chol"].iloc[0]
        )

        assert bp_reduction_intensive > bp_reduction_lifestyle
        assert chol_reduction_intensive > chol_reduction_lifestyle

    def test_all_actions_respect_bounds(self, unhealthy_patient):
        """Test that all interventions respect clinical bounds"""
        for action in range(5):
            modified = apply_intervention_effects(unhealthy_patient, action=action)

            # Check bounds
            assert 90 <= modified["trestbps"].iloc[0] <= 200
            assert 120 <= modified["chol"].iloc[0] <= 400
            assert 60 <= modified["thalach"].iloc[0] <= 220
            assert 0.0 <= modified["oldpeak"].iloc[0] <= 6.0


class TestNormalizedDataSupport:
    """Test that the system correctly handles normalized (z-score) data"""

    @pytest.fixture
    def normalized_patient(self):
        """Create normalized patient data (as used by RL agent)"""
        return pd.DataFrame(
            [
                {
                    "age": 0.5,
                    "sex": 1.0,
                    "cp": 0.75,
                    "trestbps": 0.6,
                    "chol": 0.55,
                    "fbs": 1.0,
                    "restecg": 0.5,
                    "thalach": 0.7,
                    "exang": 0.0,
                    "oldpeak": 0.4,
                    "slope": 0.66,
                    "ca": 0.0,
                    "thal": 0.5,
                }
            ]
        )

    def test_detects_normalized_data(self, normalized_patient):
        """Test that normalized data is detected correctly"""
        # Should apply simple percentage reductions for normalized data
        modified = apply_intervention_effects(normalized_patient, action=1)

        # Should see percentage-based changes
        assert modified["trestbps"].iloc[0] < normalized_patient["trestbps"].iloc[0]
        assert modified["chol"].iloc[0] < normalized_patient["chol"].iloc[0]

    def test_normalized_lifestyle_intervention(self, normalized_patient):
        """Test lifestyle intervention on normalized data"""
        modified = apply_intervention_effects(normalized_patient, action=1)

        # Check expected percentage reductions
        expected_bp = normalized_patient["trestbps"].iloc[0] * 0.95
        expected_chol = normalized_patient["chol"].iloc[0] * 0.90
        expected_thalach = normalized_patient["thalach"].iloc[0] * 1.05

        assert modified["trestbps"].iloc[0] == pytest.approx(expected_bp, rel=0.01)
        assert modified["chol"].iloc[0] == pytest.approx(expected_chol, rel=0.01)
        assert modified["thalach"].iloc[0] == pytest.approx(expected_thalach, rel=0.01)


class TestStateDependentEffects:
    """Test that intervention effects adapt to patient state"""

    def test_optimal_bp_gets_minimal_reduction(self):
        """Test that optimal BP (110) gets minimal reduction"""
        patient = pd.DataFrame([{"trestbps": 110, "chol": 200, "thalach": 150}])
        modified = apply_intervention_effects(patient, action=1)

        # Should see minimal or no change
        assert modified["trestbps"].iloc[0] == pytest.approx(110, abs=1)

    def test_high_bp_gets_full_reduction(self):
        """Test that high BP (170) gets full reduction"""
        patient = pd.DataFrame(
            [
                {
                    "trestbps": 170,
                    "chol": 200,
                    "thalach": 150,
                    "oldpeak": 0.0,
                    "age": 50,
                    "sex": 1,
                    "cp": 0,
                    "fbs": 0,
                    "restecg": 0,
                    "exang": 0,
                    "slope": 1,
                    "ca": 0,
                    "thal": 2,
                }
            ]
        )
        modified = apply_intervention_effects(patient, action=1)

        # Should see significant reduction (at least 5mmHg)
        reduction = patient["trestbps"].iloc[0] - modified["trestbps"].iloc[0]
        assert reduction >= 5

    def test_very_high_bp_gets_enhanced_reduction(self):
        """Test that very high BP gets enhanced reduction"""
        patient = pd.DataFrame(
            [
                {
                    "trestbps": 190,
                    "chol": 200,
                    "thalach": 150,
                    "oldpeak": 0.0,
                    "age": 50,
                    "sex": 1,
                    "cp": 0,
                    "fbs": 0,
                    "restecg": 0,
                    "exang": 0,
                    "slope": 1,
                    "ca": 0,
                    "thal": 2,
                }
            ]
        )
        modified_lifestyle = apply_intervention_effects(patient, action=1)

        # Very high BP should get enhanced reduction
        reduction = patient["trestbps"].iloc[0] - modified_lifestyle["trestbps"].iloc[0]
        assert reduction >= 8
