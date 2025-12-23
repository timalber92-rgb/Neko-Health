"""
Risk Prediction Module for HealthGuard

This module implements the RandomForest-based cardiovascular disease risk
predictor. It provides functionality for training, evaluation, and inference
with comprehensive metrics and feature importance analysis.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix
)
from sklearn.model_selection import cross_val_score

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RiskPredictor:
    """
    Random Forest classifier for cardiovascular disease risk prediction.

    This predictor provides:
    - Binary classification (disease/no disease)
    - Probability-based risk scores (0-100%)
    - Feature importance rankings
    - Comprehensive evaluation metrics

    Attributes:
        model: RandomForestClassifier instance
        n_estimators: Number of trees in the forest
        random_state: Random seed for reproducibility
        feature_names: List of feature names from training data
    """

    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        """
        Initialize Random Forest classifier.

        Args:
            n_estimators: Number of trees in the random forest (default: 100)
            random_state: Random seed for reproducibility (default: 42)
        """
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            max_depth=10,  # Prevent overfitting on small dataset
            min_samples_split=5,  # Require at least 5 samples to split
            min_samples_leaf=2,  # Require at least 2 samples in leaf
            class_weight='balanced'  # Handle class imbalance
        )
        self.feature_names: Optional[list] = None
        logger.info(
            f"Initialized RiskPredictor with {n_estimators} estimators, "
            f"random_state={random_state}"
        )

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series
    ) -> Dict[str, float]:
        """
        Train the Random Forest model with cross-validation.

        Performs 5-fold stratified cross-validation on the training set,
        then trains the final model and evaluates on the validation set.

        Args:
            X_train: Training features (normalized)
            y_train: Training labels (0=no disease, 1=disease)
            X_val: Validation features (normalized)
            y_val: Validation labels

        Returns:
            Dictionary containing validation metrics:
                - accuracy: Overall accuracy
                - precision: Precision score
                - recall: Recall score (sensitivity)
                - f1: F1 score (harmonic mean of precision and recall)
                - roc_auc: Area under the ROC curve
                - cv_accuracy_mean: Mean cross-validation accuracy
                - cv_accuracy_std: Std dev of cross-validation accuracy

        Raises:
            ValueError: If input shapes are mismatched or data is invalid
        """
        logger.info("Starting model training")

        # Validate inputs
        if len(X_train) != len(y_train):
            raise ValueError(
                f"X_train ({len(X_train)}) and y_train ({len(y_train)}) "
                f"must have same length"
            )
        if len(X_val) != len(y_val):
            raise ValueError(
                f"X_val ({len(X_val)}) and y_val ({len(y_val)}) "
                f"must have same length"
            )

        # Store feature names for later use
        self.feature_names = list(X_train.columns)
        logger.info(f"Training on {len(self.feature_names)} features")

        # Perform 5-fold cross-validation on training set
        logger.info("Performing 5-fold cross-validation...")
        cv_scores = cross_val_score(
            self.model,
            X_train,
            y_train,
            cv=5,
            scoring='accuracy',
            n_jobs=-1  # Use all available cores
        )
        cv_mean = cv_scores.mean()
        cv_std = cv_scores.std()
        logger.info(
            f"Cross-validation accuracy: {cv_mean:.4f} (+/- {cv_std:.4f})"
        )

        # Train final model on full training set
        logger.info("Training final model on full training set...")
        self.model.fit(X_train, y_train)

        # Evaluate on validation set
        logger.info("Evaluating on validation set...")
        y_pred = self.model.predict(X_val)
        y_pred_proba = self.model.predict_proba(X_val)[:, 1]

        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_val, y_pred),
            'precision': precision_score(y_val, y_pred, zero_division=0),
            'recall': recall_score(y_val, y_pred, zero_division=0),
            'f1': f1_score(y_val, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_val, y_pred_proba),
            'cv_accuracy_mean': cv_mean,
            'cv_accuracy_std': cv_std
        }

        # Log detailed results
        logger.info("Validation Metrics:")
        for metric_name, value in metrics.items():
            logger.info(f"  {metric_name}: {value:.4f}")

        logger.info("\nClassification Report:")
        logger.info("\n" + classification_report(y_val, y_pred, target_names=['No Disease', 'Disease']))

        logger.info("\nConfusion Matrix:")
        cm = confusion_matrix(y_val, y_pred)
        logger.info(f"\n{cm}")
        logger.info(f"TN={cm[0,0]}, FP={cm[0,1]}, FN={cm[1,0]}, TP={cm[1,1]}")

        logger.info("Training complete")
        return metrics

    def predict(self, patient_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Predict cardiovascular disease risk for patient(s).

        Returns both classification and probability-based risk score,
        along with feature importance for interpretability.

        Args:
            patient_data: DataFrame with patient features (must be normalized
                         using the same scaler as training data)

        Returns:
            Dictionary containing:
                - risk_score: Risk percentage (0-100%)
                - has_disease: Boolean prediction (True if disease predicted)
                - classification: Risk category ("Low", "Medium", or "High")
                - probability: Raw probability of disease (0-1)
                - feature_importance: Dict mapping features to importance scores

        Raises:
            ValueError: If model hasn't been trained or features don't match
            RuntimeError: If prediction fails
        """
        if self.model is None or not hasattr(self.model, 'classes_'):
            raise ValueError(
                "Model has not been trained yet. Call train() first."
            )

        if self.feature_names is None:
            raise ValueError("Feature names not set. Model may not be trained properly.")

        # Validate feature names match
        if list(patient_data.columns) != self.feature_names:
            raise ValueError(
                f"Feature mismatch. Expected {self.feature_names}, "
                f"got {list(patient_data.columns)}"
            )

        try:
            # Get prediction and probability
            prediction = self.model.predict(patient_data)[0]
            proba = self.model.predict_proba(patient_data)[0]
            disease_proba = proba[1]  # Probability of class 1 (disease)

            # Convert to risk score (0-100%)
            risk_score = disease_proba * 100

            # Classify risk level
            if risk_score < 30:
                risk_class = "Low Risk"
            elif risk_score < 70:
                risk_class = "Medium Risk"
            else:
                risk_class = "High Risk"

            # Get feature importance for this prediction
            feature_importance = self.get_feature_importance()

            # Convert feature importance to dict (feature -> importance)
            importance_dict = dict(zip(
                feature_importance['feature'].tolist(),
                feature_importance['importance'].tolist()
            ))

            result = {
                'risk_score': float(risk_score),
                'has_disease': bool(prediction),
                'classification': risk_class,
                'probability': float(disease_proba),
                'feature_importance': importance_dict
            }

            logger.info(
                f"Prediction: {risk_class} ({risk_score:.1f}%), "
                f"Disease: {bool(prediction)}"
            )

            return result

        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise RuntimeError(f"Prediction failed: {str(e)}") from e

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
        """
        Evaluate model on test set.

        Provides comprehensive performance metrics on held-out test data.

        Args:
            X_test: Test features (normalized)
            y_test: Test labels

        Returns:
            Dictionary containing test metrics:
                - accuracy: Overall accuracy
                - precision: Precision score
                - recall: Recall score (sensitivity)
                - f1: F1 score
                - roc_auc: Area under the ROC curve

        Raises:
            ValueError: If model hasn't been trained or data is invalid
        """
        if self.model is None or not hasattr(self.model, 'classes_'):
            raise ValueError(
                "Model has not been trained yet. Call train() first."
            )

        if len(X_test) != len(y_test):
            raise ValueError(
                f"X_test ({len(X_test)}) and y_test ({len(y_test)}) "
                f"must have same length"
            )

        logger.info(f"Evaluating on test set ({len(X_test)} samples)...")

        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]

        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1': f1_score(y_test, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_test, y_pred_proba)
        }

        logger.info("Test Set Metrics:")
        for metric_name, value in metrics.items():
            logger.info(f"  {metric_name}: {value:.4f}")

        logger.info("\nTest Set Classification Report:")
        logger.info("\n" + classification_report(y_test, y_pred, target_names=['No Disease', 'Disease']))

        logger.info("\nTest Set Confusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        logger.info(f"\n{cm}")
        logger.info(f"TN={cm[0,0]}, FP={cm[0,1]}, FN={cm[1,0]}, TP={cm[1,1]}")

        return metrics

    def get_feature_importance(self) -> pd.DataFrame:
        """
        Get feature importance rankings from the trained model.

        Feature importance indicates which patient attributes contribute
        most to the risk prediction. Higher values = more important.

        Returns:
            DataFrame with columns ['feature', 'importance'], sorted by
            importance in descending order

        Raises:
            ValueError: If model hasn't been trained
        """
        if self.model is None or not hasattr(self.model, 'feature_importances_'):
            raise ValueError(
                "Model has not been trained yet. Call train() first."
            )

        if self.feature_names is None:
            raise ValueError("Feature names not set. Model may not be trained properly.")

        # Get importance scores from Random Forest
        importances = self.model.feature_importances_

        # Create DataFrame and sort by importance
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)

        logger.info("Feature Importance (top 5):")
        for idx, row in importance_df.head(5).iterrows():
            logger.info(f"  {row['feature']}: {row['importance']:.4f}")

        return importance_df

    def save(self, path: Path) -> None:
        """
        Save trained model to disk.

        Saves both the RandomForest model and feature names for later use.

        Args:
            path: Path to save the model file (.pkl)

        Raises:
            ValueError: If model hasn't been trained
            IOError: If file cannot be written
        """
        if self.model is None or not hasattr(self.model, 'classes_'):
            raise ValueError(
                "Model has not been trained yet. Call train() first."
            )

        try:
            # Save model and metadata
            model_data = {
                'model': self.model,
                'feature_names': self.feature_names,
                'n_estimators': self.n_estimators,
                'random_state': self.random_state
            }

            joblib.dump(model_data, path)
            logger.info(f"Model saved to {path}")

        except Exception as e:
            logger.error(f"Failed to save model: {str(e)}")
            raise IOError(f"Failed to save model: {str(e)}") from e

    def load(self, path: Path) -> None:
        """
        Load trained model from disk.

        Loads a previously saved model and restores all metadata.

        Args:
            path: Path to the saved model file (.pkl)

        Raises:
            FileNotFoundError: If model file doesn't exist
            IOError: If file cannot be read or is corrupted
        """
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")

        try:
            # Load model and metadata
            model_data = joblib.load(path)

            self.model = model_data['model']
            self.feature_names = model_data['feature_names']
            self.n_estimators = model_data['n_estimators']
            self.random_state = model_data['random_state']

            logger.info(f"Model loaded from {path}")
            logger.info(f"Features: {len(self.feature_names)}")

        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise IOError(f"Failed to load model: {str(e)}") from e


def main():
    """
    Main function for training and testing the risk predictor.

    This demonstrates the complete workflow:
    1. Load processed data
    2. Train model with cross-validation
    3. Evaluate on validation and test sets
    4. Display feature importance
    5. Save trained model
    """
    from pathlib import Path
    import sys

    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from data.load import load_processed_data

    logger.info("="*80)
    logger.info("HealthGuard - Risk Predictor Training")
    logger.info("="*80)

    # Load data
    logger.info("\n[1/5] Loading processed data...")
    train_df, val_df, test_df, scaler = load_processed_data()

    # Separate features and targets
    X_train = train_df.drop('target', axis=1)
    y_train = train_df['target']
    X_val = val_df.drop('target', axis=1)
    y_val = val_df['target']
    X_test = test_df.drop('target', axis=1)
    y_test = test_df['target']

    logger.info(f"Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")

    # Initialize predictor
    logger.info("\n[2/5] Initializing Random Forest predictor...")
    predictor = RiskPredictor(n_estimators=100, random_state=42)

    # Train model
    logger.info("\n[3/5] Training model with cross-validation...")
    val_metrics = predictor.train(X_train, y_train, X_val, y_val)

    # Evaluate on test set
    logger.info("\n[4/5] Evaluating on test set...")
    test_metrics = predictor.evaluate(X_test, y_test)

    # Display feature importance
    logger.info("\n[5/5] Feature Importance Analysis...")
    importance_df = predictor.get_feature_importance()

    # Save model
    model_dir = Path(__file__).parent.parent / "models"
    model_dir.mkdir(exist_ok=True)
    model_path = model_dir / "risk_predictor.pkl"
    predictor.save(model_path)

    # Summary
    logger.info("\n" + "="*80)
    logger.info("TRAINING SUMMARY")
    logger.info("="*80)
    logger.info(f"Validation ROC-AUC: {val_metrics['roc_auc']:.4f}")
    logger.info(f"Test ROC-AUC: {test_metrics['roc_auc']:.4f}")
    logger.info(f"Test Accuracy: {test_metrics['accuracy']:.4f}")
    logger.info(f"Test F1 Score: {test_metrics['f1']:.4f}")
    logger.info(f"\nModel saved to: {model_path}")
    logger.info("="*80)

    # Demo prediction
    logger.info("\n[DEMO] Sample Prediction:")
    logger.info("Testing on first patient from test set...")
    sample_patient = X_test.iloc[[0]]
    actual_label = y_test.iloc[0]

    prediction = predictor.predict(sample_patient)
    logger.info(f"Actual: {'Disease' if actual_label == 1 else 'No Disease'}")
    logger.info(f"Predicted: {prediction['classification']}")
    logger.info(f"Risk Score: {prediction['risk_score']:.1f}%")
    logger.info(f"Top 3 Risk Factors:")
    importance_dict = prediction['feature_importance']
    for i, (feature, importance) in enumerate(list(importance_dict.items())[:3], 1):
        logger.info(f"  {i}. {feature}: {importance:.4f}")


if __name__ == "__main__":
    main()
