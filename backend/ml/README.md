# Machine Learning Module

Core ML components for risk prediction and intervention recommendations.

## Components

### risk_predictor.py
Logistic Regression model for cardiovascular disease risk prediction with embedded StandardScaler.

**Features:**
- Binary classification (disease/no disease)
- Automatic feature scaling (StandardScaler embedded in model)
- Probability estimates for risk assessment (0-100% risk score)
- Feature importance analysis (coefficient-based)
- Fast inference (<10ms per prediction)

**Key Implementation Details:**
- Accepts raw, unscaled patient features
- Applies StandardScaler internally before prediction
- Scaler is saved/loaded with model for consistency
- No separate scaler file management needed

### intervention_utils.py
Utilities for applying intervention effects to patient features.

**Interventions:**
- Medication (BP/cholesterol reduction)
- Lifestyle changes (exercise, diet)
- Combination therapy

### guideline_recommender.py
Risk-stratified intervention recommendation engine.

**Risk Tiers:**
- Low Risk (0-20%)
- Moderate Risk (20-40%)
- High Risk (40-60%)
- Very High Risk (60%+)

### recommendation_engine.py
Orchestrates risk prediction and personalized recommendations.

## Model Files

Trained models are stored in `backend/models/`:
- `risk_predictor.pkl` - Trained Logistic Regression model with embedded StandardScaler

## Training

To retrain the model with proper feature scaling:
```bash
cd backend
python scripts/train_model_with_scaling.py
```

This script:
1. Loads and preprocesses data
2. Applies StandardScaler to features
3. Trains Logistic Regression model
4. Embeds scaler in model file
5. Evaluates performance
6. Saves model to `models/risk_predictor.pkl`

**Performance**: 82.6% accuracy, 93.9% ROC-AUC on test set
