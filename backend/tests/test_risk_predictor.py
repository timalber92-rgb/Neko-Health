"""
Unit tests for RiskPredictor (Random Forest classifier)

Tests cover:
- Model initialization
- Training and validation
- Prediction functionality
- Feature importance extraction
- Model persistence (save/load)
"""

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ml.risk_predictor import RiskPredictor


@pytest.fixture
def sample_data():
    """
    Create sample training data for testing.
    """
    np.random.seed(42)
    n_samples = 100

    # Create synthetic patient data
    data = {
        "age": np.random.uniform(30, 80, n_samples),
        "sex": np.random.randint(0, 2, n_samples),
        "cp": np.random.randint(1, 5, n_samples),
        "trestbps": np.random.uniform(90, 200, n_samples),
        "chol": np.random.uniform(100, 400, n_samples),
        "fbs": np.random.randint(0, 2, n_samples),
        "restecg": np.random.randint(0, 3, n_samples),
        "thalach": np.random.uniform(60, 200, n_samples),
        "exang": np.random.randint(0, 2, n_samples),
        "oldpeak": np.random.uniform(0, 6, n_samples),
        "slope": np.random.randint(1, 4, n_samples),
        "ca": np.random.randint(0, 4, n_samples),
        "thal": np.random.choice([3, 6, 7], n_samples),
        "target": np.random.randint(0, 2, n_samples),
    }

    df = pd.DataFrame(data)

    # Normalize features (simple min-max for testing)
    features = df.drop("target", axis=1)
    target = df["target"]

    features_normalized = (features - features.min()) / (features.max() - features.min())

    return features_normalized, target


@pytest.fixture
def trained_predictor(sample_data):
    """
    Create a trained RiskPredictor for testing.
    """
    X, y = sample_data

    # Split into train and validation sets
    split_idx = int(len(X) * 0.8)
    X_train, X_val = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_val = y.iloc[:split_idx], y.iloc[split_idx:]

    predictor = RiskPredictor(n_estimators=10, random_state=42)  # Fewer trees for speed
    predictor.train(X_train, y_train, X_val, y_val)

    return predictor


class TestRiskPredictorInitialization:
    """Test model initialization"""

    def test_init_default_parameters(self):
        """Test initialization with default parameters"""
        predictor = RiskPredictor()
        assert predictor.n_estimators == 100
        assert predictor.random_state == 42
        assert predictor.model is not None
        assert predictor.feature_names is None

    def test_init_custom_parameters(self):
        """Test initialization with custom parameters"""
        predictor = RiskPredictor(n_estimators=50, random_state=123)
        assert predictor.n_estimators == 50
        assert predictor.random_state == 123

    def test_model_hyperparameters(self):
        """Test that model has correct hyperparameters"""
        predictor = RiskPredictor()
        assert predictor.model.max_depth == 10
        assert predictor.model.min_samples_split == 5
        assert predictor.model.min_samples_leaf == 2
        assert predictor.model.class_weight == "balanced"


class TestRiskPredictorTraining:
    """Test model training"""

    def test_train_basic(self, sample_data):
        """Test basic training workflow"""
        X, y = sample_data
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_val = y.iloc[:split_idx], y.iloc[split_idx:]

        predictor = RiskPredictor(n_estimators=10, random_state=42)
        metrics = predictor.train(X_train, y_train, X_val, y_val)

        # Check that metrics are returned
        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1" in metrics
        assert "roc_auc" in metrics
        assert "cv_accuracy_mean" in metrics
        assert "cv_accuracy_std" in metrics

        # Check that metrics are reasonable
        assert 0 <= metrics["accuracy"] <= 1
        assert 0 <= metrics["roc_auc"] <= 1

        # Check that feature names are stored
        assert predictor.feature_names is not None
        assert len(predictor.feature_names) == 13

    def test_train_mismatched_lengths(self, sample_data):
        """Test that training fails with mismatched data lengths"""
        X, y = sample_data
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train = y.iloc[:split_idx]

        predictor = RiskPredictor()

        # Mismatch training data
        with pytest.raises(ValueError, match="must have same length"):
            predictor.train(X_train.iloc[:-5], y_train, X_val, y.iloc[split_idx:])

    def test_feature_names_stored(self, trained_predictor):
        """Test that feature names are stored after training"""
        assert trained_predictor.feature_names is not None
        assert len(trained_predictor.feature_names) == 13
        assert "age" in trained_predictor.feature_names
        assert "trestbps" in trained_predictor.feature_names


class TestRiskPredictorPrediction:
    """Test prediction functionality"""

    def test_predict_single_patient(self, trained_predictor, sample_data):
        """Test prediction on a single patient"""
        X, _ = sample_data
        patient = X.iloc[[0]]

        result = trained_predictor.predict(patient)

        # Check result structure
        assert "risk_score" in result
        assert "has_disease" in result
        assert "classification" in result
        assert "probability" in result
        assert "feature_importance" in result

        # Check value ranges
        assert 0 <= result["risk_score"] <= 100
        assert 0 <= result["probability"] <= 1
        assert isinstance(result["has_disease"], bool)
        assert result["classification"] in ["Low Risk", "Medium Risk", "High Risk"]

        # Check feature importance
        assert isinstance(result["feature_importance"], dict)
        assert len(result["feature_importance"]) == 13

    def test_predict_risk_classification(self, trained_predictor, sample_data):
        """Test risk classification thresholds"""
        X, _ = sample_data

        # We can't control the exact risk score, but we can check the logic
        # by testing the classification mapping
        patient = X.iloc[[0]]
        result = trained_predictor.predict(patient)

        if result["risk_score"] < 30:
            assert result["classification"] == "Low Risk"
        elif result["risk_score"] < 70:
            assert result["classification"] == "Medium Risk"
        else:
            assert result["classification"] == "High Risk"

    def test_predict_before_training(self, sample_data):
        """Test that prediction fails before training"""
        predictor = RiskPredictor()
        X, _ = sample_data
        patient = X.iloc[[0]]

        with pytest.raises(ValueError, match="not been trained"):
            predictor.predict(patient)

    def test_predict_feature_mismatch(self, trained_predictor, sample_data):
        """Test that prediction fails with wrong features"""
        X, _ = sample_data

        # Create data with wrong columns
        wrong_patient = X.iloc[[0]].rename(columns={"age": "wrong_feature"})

        with pytest.raises(ValueError, match="Feature mismatch"):
            trained_predictor.predict(wrong_patient)


class TestRiskPredictorEvaluation:
    """Test model evaluation"""

    def test_evaluate(self, trained_predictor, sample_data):
        """Test model evaluation on test set"""
        X, y = sample_data

        # Use last 20% as test set
        test_idx = int(len(X) * 0.8)
        X_test = X.iloc[test_idx:]
        y_test = y.iloc[test_idx:]

        metrics = trained_predictor.evaluate(X_test, y_test)

        # Check metrics are returned
        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1" in metrics
        assert "roc_auc" in metrics

        # Check metrics are in valid range
        assert 0 <= metrics["accuracy"] <= 1
        assert 0 <= metrics["roc_auc"] <= 1

    def test_evaluate_before_training(self, sample_data):
        """Test that evaluation fails before training"""
        predictor = RiskPredictor()
        X, y = sample_data

        with pytest.raises(ValueError, match="not been trained"):
            predictor.evaluate(X, y)

    def test_evaluate_mismatched_lengths(self, trained_predictor, sample_data):
        """Test that evaluation fails with mismatched data lengths"""
        X, y = sample_data

        with pytest.raises(ValueError, match="must have same length"):
            trained_predictor.evaluate(X, y.iloc[:-5])


class TestRiskPredictorFeatureImportance:
    """Test feature importance extraction"""

    def test_get_feature_importance(self, trained_predictor):
        """Test feature importance extraction"""
        importance_df = trained_predictor.get_feature_importance()

        # Check structure
        assert isinstance(importance_df, pd.DataFrame)
        assert "feature" in importance_df.columns
        assert "importance" in importance_df.columns

        # Check that we have all features
        assert len(importance_df) == 13

        # Check that importances are positive and sum to ~1
        assert (importance_df["importance"] >= 0).all()
        assert 0.9 < importance_df["importance"].sum() <= 1.1  # Allow some floating point error

        # Check that features are sorted by importance
        assert importance_df["importance"].is_monotonic_decreasing

    def test_feature_importance_before_training(self):
        """Test that feature importance fails before training"""
        predictor = RiskPredictor()

        with pytest.raises(ValueError, match="not been trained"):
            predictor.get_feature_importance()


class TestRiskPredictorPersistence:
    """Test model save/load functionality"""

    def test_save_and_load(self, trained_predictor, sample_data):
        """Test saving and loading model"""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = Path(tmpdir) / "test_model.pkl"

            # Save model
            trained_predictor.save(model_path)
            assert model_path.exists()

            # Load model into new instance
            new_predictor = RiskPredictor()
            new_predictor.load(model_path)

            # Check that parameters are restored
            assert new_predictor.n_estimators == trained_predictor.n_estimators
            assert new_predictor.random_state == trained_predictor.random_state
            assert new_predictor.feature_names == trained_predictor.feature_names

            # Check that predictions match
            X, _ = sample_data
            patient = X.iloc[[0]]

            result_original = trained_predictor.predict(patient)
            result_loaded = new_predictor.predict(patient)

            assert result_original["risk_score"] == result_loaded["risk_score"]
            assert result_original["has_disease"] == result_loaded["has_disease"]

    def test_save_before_training(self):
        """Test that save fails before training"""
        predictor = RiskPredictor()

        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = Path(tmpdir) / "test_model.pkl"

            with pytest.raises(ValueError, match="not been trained"):
                predictor.save(model_path)

    def test_load_nonexistent_file(self):
        """Test that load fails with non-existent file"""
        predictor = RiskPredictor()

        with pytest.raises(FileNotFoundError):
            predictor.load(Path("/nonexistent/path.pkl"))


class TestRiskPredictorEdgeCases:
    """Test edge cases and error handling"""

    def test_prediction_consistency(self, trained_predictor, sample_data):
        """Test that predictions are consistent (deterministic)"""
        X, _ = sample_data
        patient = X.iloc[[0]]

        result1 = trained_predictor.predict(patient)
        result2 = trained_predictor.predict(patient)

        assert result1["risk_score"] == result2["risk_score"]
        assert result1["has_disease"] == result2["has_disease"]

    def test_multiple_predictions(self, trained_predictor, sample_data):
        """Test predicting on multiple patients sequentially"""
        X, _ = sample_data

        results = []
        for i in range(5):
            patient = X.iloc[[i]]
            result = trained_predictor.predict(patient)
            results.append(result)

        # Check that we got 5 different predictions
        assert len(results) == 5

        # Results should vary (very unlikely to be all identical)
        risk_scores = [r["risk_score"] for r in results]
        assert len(set(risk_scores)) > 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
