#!/usr/bin/env python3
"""
Train the RiskPredictor model with proper feature scaling.

This script:
1. Loads processed data
2. Scales features using StandardScaler
3. Trains Logistic Regression model
4. Evaluates on validation and test sets
5. Saves both model and scaler
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging

from sklearn.preprocessing import StandardScaler

from data.load import load_processed_data
from ml.risk_predictor import RiskPredictor

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 80)
    logger.info("HealthGuard - Risk Predictor Training with Feature Scaling")
    logger.info("=" * 80)

    # Load data
    logger.info("\n[1/6] Loading processed data...")
    train_df, val_df, test_df = load_processed_data()

    # Separate features and targets
    X_train = train_df.drop("target", axis=1)
    y_train = train_df["target"]
    X_val = val_df.drop("target", axis=1)
    y_val = val_df["target"]
    X_test = test_df.drop("target", axis=1)
    y_test = test_df["target"]

    logger.info(f"Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")

    # Create and fit scaler
    logger.info("\n[2/6] Creating and fitting StandardScaler...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    logger.info("Feature scaling applied:")
    logger.info(f"  Scaler means: {scaler.mean_[:3]}... (showing first 3)")
    logger.info(f"  Scaler stds:  {scaler.scale_[:3]}... (showing first 3)")

    # Convert back to DataFrames to preserve column names
    import pandas as pd

    X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)
    X_val_scaled = pd.DataFrame(X_val_scaled, columns=X_val.columns, index=X_val.index)
    X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns, index=X_test.index)

    # Initialize predictor
    logger.info("\n[3/6] Initializing Logistic Regression predictor...")
    predictor = RiskPredictor(random_state=42)
    # Attach scaler to predictor so it's saved with the model
    predictor.scaler = scaler

    # Train model
    logger.info("\n[4/6] Training model with cross-validation...")
    val_metrics = predictor.train(X_train_scaled, y_train, X_val_scaled, y_val)

    # Evaluate on test set
    logger.info("\n[5/6] Evaluating on test set...")
    test_metrics = predictor.evaluate(X_test_scaled, y_test)

    # Display feature importance
    logger.info("\n[6/6] Feature Importance Analysis...")
    predictor.get_feature_importance()  # Logs feature importance internally

    # Save model (scaler is now included in the model)
    model_dir = Path(__file__).parent.parent / "models"
    model_dir.mkdir(exist_ok=True)

    model_path = model_dir / "risk_predictor.pkl"

    predictor.save(model_path)
    logger.info("Model saved with embedded scaler")

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TRAINING SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Validation ROC-AUC: {val_metrics['roc_auc']:.4f}")
    logger.info(f"Test ROC-AUC: {test_metrics['roc_auc']:.4f}")
    logger.info(f"Test Accuracy: {test_metrics['accuracy']:.4f}")
    logger.info(f"Test F1 Score: {test_metrics['f1']:.4f}")
    logger.info(f"\nModel saved to: {model_path} (with embedded scaler)")
    logger.info("=" * 80)

    # Verify age coefficient is positive (increases with age)
    logger.info("\n" + "=" * 80)
    logger.info("MODEL COEFFICIENT ANALYSIS")
    logger.info("=" * 80)
    coeffs = predictor.model.coef_[0]
    age_coeff = coeffs[0]  # age is the first feature
    logger.info(f"Age coefficient: {age_coeff:.4f}")
    logger.info(f"Age coefficient sign: {'POSITIVE (correct)' if age_coeff > 0 else 'NEGATIVE (problematic)'}")
    logger.info("\nAll coefficients:")
    for feature, coeff in zip(predictor.feature_names, coeffs):
        logger.info(f"  {feature:12s}: {coeff:8.4f}")
    logger.info("=" * 80)

    # Demo prediction
    logger.info("\n[DEMO] Sample Predictions:")
    logger.info("Testing age effect with two similar patients differing only in age...")

    # Create two test patients
    young_patient = X_test_scaled.iloc[[0]].copy()
    old_patient = young_patient.copy()

    # Only change age (using scaled values)
    young_age_scaled = (35 - scaler.mean_[0]) / scaler.scale_[0]
    old_age_scaled = (70 - scaler.mean_[0]) / scaler.scale_[0]

    young_patient.iloc[0, 0] = young_age_scaled  # age column
    old_patient.iloc[0, 0] = old_age_scaled  # age column

    young_pred = predictor.predict(young_patient)
    old_pred = predictor.predict(old_patient)

    logger.info(f"\nYoung patient (age 35): {young_pred['risk_score']:.2f}%")
    logger.info(f"Old patient (age 70):   {old_pred['risk_score']:.2f}%")
    logger.info(
        f"Age effect check: {'✓ PASS - older has higher risk' if old_pred['risk_score'] > young_pred['risk_score'] else '✗ FAIL - younger has higher risk'}"
    )


if __name__ == "__main__":
    main()
