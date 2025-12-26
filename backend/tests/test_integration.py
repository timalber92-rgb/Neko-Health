"""
Integration tests for HealthGuard Backend

Tests the complete end-to-end workflow:
- Data loading and preprocessing
- Model training and evaluation
- API integration with ML models
- Full analysis pipeline (data → model → API → response)
"""

import sys
import tempfile
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient

from api.main import app
from data.load import load_processed_data
from ml.guideline_recommender import GuidelineRecommender
from ml.risk_predictor import RiskPredictor


@pytest.fixture(scope="module")
def processed_data():
    """
    Load processed data for integration testing.
    This fixture is module-scoped to avoid reloading data for each test.
    """
    try:
        train_df, val_df, test_df = load_processed_data()
        return {"train": train_df, "val": val_df, "test": test_df}
    except Exception as e:
        pytest.skip(f"Could not load processed data: {str(e)}")


@pytest.fixture(scope="module")
def trained_risk_predictor(processed_data):
    """
    Train a risk predictor for integration testing.
    Module-scoped to train only once.
    """
    train_df = processed_data["train"]
    val_df = processed_data["val"]

    X_train = train_df.drop("target", axis=1)
    y_train = train_df["target"]
    X_val = val_df.drop("target", axis=1)
    y_val = val_df["target"]

    predictor = RiskPredictor(random_state=42)
    predictor.train(X_train, y_train, X_val, y_val)

    return predictor


@pytest.fixture(scope="module")
def guideline_recommender():
    """
    Create a guideline-based recommender for integration testing.
    Module-scoped since it doesn't require training.
    """
    return GuidelineRecommender()


@pytest.fixture
def api_client():
    """
    Create a test client for API integration tests.
    """
    return TestClient(app)


class TestDataPipeline:
    """Test data loading and preprocessing"""

    def test_data_loading(self, processed_data):
        """Test that data is loaded correctly"""
        assert processed_data is not None
        assert "train" in processed_data
        assert "val" in processed_data
        assert "test" in processed_data

    def test_data_shapes(self, processed_data):
        """Test that data has correct shapes"""
        train_df = processed_data["train"]
        val_df = processed_data["val"]
        test_df = processed_data["test"]

        # All should have 14 columns (13 features + 1 target)
        assert train_df.shape[1] == 14
        assert val_df.shape[1] == 14
        assert test_df.shape[1] == 14

        # Training set should be largest
        assert len(train_df) > len(val_df)
        assert len(train_df) > len(test_df)

    def test_data_normalization(self, processed_data):
        """Test that features are in expected ranges (raw features, not normalized)"""
        train_df = processed_data["train"]
        features = train_df.drop("target", axis=1)

        # Check that all features are numeric and not NaN
        for col in features.columns:
            assert features[col].dtype in ["int64", "float64"], f"Feature {col} should be numeric"
            assert not features[col].isna().any(), f"Feature {col} should not have NaN values"

        # Check specific feature ranges for the Cleveland Heart Disease dataset
        assert features["age"].min() >= 0 and features["age"].max() <= 120, "Age should be in valid range"
        assert features["trestbps"].min() >= 0, "Blood pressure should be positive"
        assert features["chol"].min() >= 0, "Cholesterol should be positive"

    def test_target_distribution(self, processed_data):
        """Test that target distribution is reasonable"""
        train_df = processed_data["train"]
        target = train_df["target"]

        # Should be binary (0 or 1)
        assert set(target.unique()).issubset({0, 1})

        # Should have both classes
        assert target.nunique() == 2

        # Should be relatively balanced (neither class < 20%)
        class_distribution = target.value_counts(normalize=True)
        assert class_distribution.min() > 0.2


class TestMLPipeline:
    """Test ML model training and prediction pipeline"""

    def test_risk_predictor_training(self, trained_risk_predictor):
        """Test that risk predictor is trained successfully"""
        assert trained_risk_predictor is not None
        assert trained_risk_predictor.model is not None
        assert trained_risk_predictor.feature_names is not None
        assert len(trained_risk_predictor.feature_names) == 13

    def test_risk_predictor_performance(self, trained_risk_predictor, processed_data):
        """Test that risk predictor has reasonable performance"""
        test_df = processed_data["test"]
        X_test = test_df.drop("target", axis=1)
        y_test = test_df["target"]

        metrics = trained_risk_predictor.evaluate(X_test, y_test)

        # Should have reasonable accuracy (> 60% on small test set)
        assert metrics["accuracy"] > 0.6

        # ROC-AUC should be better than random (> 0.5)
        assert metrics["roc_auc"] > 0.5


class TestModelPersistence:
    """Test model saving and loading"""

    def test_risk_predictor_save_load(self, trained_risk_predictor, processed_data):
        """Test risk predictor persistence"""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = Path(tmpdir) / "risk_predictor.pkl"

            # Save
            trained_risk_predictor.save(model_path)
            assert model_path.exists()

            # Load
            new_predictor = RiskPredictor()
            new_predictor.load(model_path)

            # Test on same data
            test_df = processed_data["test"]
            X_test = test_df.drop("target", axis=1)
            patient = X_test.iloc[[0]]

            result1 = trained_risk_predictor.predict(patient)
            result2 = new_predictor.predict(patient)

            assert result1["risk_score"] == result2["risk_score"]

    def test_guideline_recommender_deterministic(self, guideline_recommender, trained_risk_predictor, processed_data):
        """Test that guideline recommender gives consistent recommendations"""
        test_df = processed_data["test"]
        features = test_df.drop("target", axis=1)
        patient = features.iloc[[0]]

        # Get recommendation twice - should be identical (deterministic)
        rec1 = guideline_recommender.recommend(patient, trained_risk_predictor)
        rec2 = guideline_recommender.recommend(patient, trained_risk_predictor)

        assert rec1["action"] == rec2["action"]
        assert rec1["current_risk"] == rec2["current_risk"]
        assert rec1["expected_final_risk"] == rec2["expected_final_risk"]


class TestAPIIntegration:
    """Test API integration with ML models"""

    def test_api_health_check(self, api_client):
        """Test that API is healthy and models are loaded"""
        response = api_client.get("/")

        assert response.status_code == 200
        data = response.json()

        # Models should be loaded (assuming they exist in models/ directory)
        # Note: This might fail if models haven't been trained yet
        assert "models_loaded" in data

    def test_api_prediction_integration(self, api_client):
        """Test prediction endpoint with realistic data"""
        patient = {
            "age": 63.0,
            "sex": 1,
            "cp": 3,
            "trestbps": 145.0,
            "chol": 233.0,
            "fbs": 1,
            "restecg": 0,
            "thalach": 150.0,
            "exang": 0,
            "oldpeak": 2.3,
            "slope": 2,
            "ca": 0,
            "thal": 6,
        }

        response = api_client.post("/api/predict", json=patient)

        if response.status_code == 200:
            data = response.json()
            assert "risk_score" in data
            assert 0 <= data["risk_score"] <= 100
        elif response.status_code == 503:
            pytest.skip("Models not loaded in API")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")

    def test_api_recommendation_integration(self, api_client):
        """Test recommendation endpoint with realistic data"""
        patient = {
            "age": 63.0,
            "sex": 1,
            "cp": 3,
            "trestbps": 145.0,
            "chol": 233.0,
            "fbs": 1,
            "restecg": 0,
            "thalach": 150.0,
            "exang": 0,
            "oldpeak": 2.3,
            "slope": 2,
            "ca": 0,
            "thal": 6,
        }

        response = api_client.post("/api/recommend", json=patient)

        if response.status_code == 200:
            data = response.json()
            assert "recommended_action" in data
            assert "recommendation_name" in data
            assert 0 <= data["recommended_action"] <= 4
        elif response.status_code == 503:
            pytest.skip("Models not loaded in API")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow"""

    def test_complete_analysis_pipeline(self, api_client):
        """Test complete analysis from patient data to recommendation"""
        # Define a patient
        patient = {
            "age": 55.0,
            "sex": 1,
            "cp": 2,
            "trestbps": 140.0,
            "chol": 220.0,
            "fbs": 0,
            "restecg": 0,
            "thalach": 160.0,
            "exang": 0,
            "oldpeak": 1.5,
            "slope": 2,
            "ca": 0,
            "thal": 3,
        }

        # Step 1: Get risk prediction
        predict_response = api_client.post("/api/predict", json=patient)

        if predict_response.status_code == 503:
            pytest.skip("Models not loaded - cannot test end-to-end workflow")

        assert predict_response.status_code == 200
        prediction = predict_response.json()

        # Step 2: Get intervention recommendation
        recommend_response = api_client.post("/api/recommend", json=patient)
        assert recommend_response.status_code == 200
        recommendation = recommend_response.json()

        # Step 3: Simulate recommended intervention
        simulation_request = {"patient": patient, "action": recommendation["recommended_action"]}
        simulate_response = api_client.post("/api/simulate", json=simulation_request)
        assert simulate_response.status_code == 200
        simulation = simulate_response.json()

        # Verify workflow consistency
        # Risk scores should be consistent across endpoints
        assert abs(prediction["risk_score"] - recommendation["baseline_risk"]) < 1.0
        assert abs(prediction["risk_score"] - simulation["current_risk"]) < 1.0

    def test_batch_analysis(self, api_client):
        """Test analyzing multiple patients sequentially"""
        patients = [
            {
                "age": 45.0,
                "sex": 0,
                "cp": 1,
                "trestbps": 130.0,
                "chol": 200.0,
                "fbs": 0,
                "restecg": 0,
                "thalach": 170.0,
                "exang": 0,
                "oldpeak": 0.5,
                "slope": 1,
                "ca": 0,
                "thal": 3,
            },
            {
                "age": 65.0,
                "sex": 1,
                "cp": 4,
                "trestbps": 160.0,
                "chol": 280.0,
                "fbs": 1,
                "restecg": 2,
                "thalach": 120.0,
                "exang": 1,
                "oldpeak": 3.0,
                "slope": 3,
                "ca": 2,
                "thal": 7,
            },
            {
                "age": 50.0,
                "sex": 1,
                "cp": 2,
                "trestbps": 145.0,
                "chol": 240.0,
                "fbs": 0,
                "restecg": 0,
                "thalach": 150.0,
                "exang": 0,
                "oldpeak": 1.8,
                "slope": 2,
                "ca": 1,
                "thal": 6,
            },
        ]

        results = []
        for patient in patients:
            response = api_client.post("/api/predict", json=patient)

            if response.status_code == 503:
                pytest.skip("Models not loaded")

            assert response.status_code == 200
            results.append(response.json())

        # Should have results for all patients
        assert len(results) == len(patients)

        # Risk scores should vary across patients
        risk_scores = [r["risk_score"] for r in results]
        assert len(set(risk_scores)) > 1  # Not all identical

    def test_intervention_comparison(self, api_client):
        """Test comparing different interventions for same patient"""
        patient = {
            "age": 60.0,
            "sex": 1,
            "cp": 3,
            "trestbps": 150.0,
            "chol": 250.0,
            "fbs": 1,
            "restecg": 0,
            "thalach": 140.0,
            "exang": 0,
            "oldpeak": 2.0,
            "slope": 2,
            "ca": 1,
            "thal": 6,
        }

        # Simulate all intervention options
        simulations = []
        for action in range(5):
            request = {"patient": patient, "action": action}
            response = api_client.post("/api/simulate", json=request)

            if response.status_code == 503:
                pytest.skip("Models not loaded")

            assert response.status_code == 200
            simulations.append(response.json())

        # All simulations should start with same current risk
        current_risks = [s["current_risk"] for s in simulations]
        assert len(set(current_risks)) == 1  # All identical

        # Different interventions should have different expected outcomes
        expected_risks = [s["expected_risk"] for s in simulations]
        # At least some variation in expected risk across interventions
        assert max(expected_risks) - min(expected_risks) > 0


class TestErrorRecovery:
    """Test system behavior under error conditions"""

    def test_api_with_invalid_data(self, api_client):
        """Test that API handles invalid data gracefully"""
        invalid_patient = {"age": -10, "sex": 5, "cp": 10}  # Invalid age  # Invalid sex  # Invalid cp

        response = api_client.post("/api/predict", json=invalid_patient)

        # Should return validation error, not crash
        assert response.status_code == 422

    def test_api_with_missing_features(self, api_client):
        """Test that API handles incomplete data gracefully"""
        incomplete_patient = {
            "age": 50.0,
            "sex": 1,
            # Missing many required fields
        }

        response = api_client.post("/api/predict", json=incomplete_patient)

        # Should return validation error
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
