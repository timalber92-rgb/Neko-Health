# Machine Learning Module

Core ML components for risk prediction and intervention recommendations.

## Components

### risk_predictor.py
Logistic Regression model for cardiovascular disease risk prediction.

**Features:**
- Binary classification (disease/no disease)
- Probability estimates for risk assessment
- Feature importance analysis
- SHAP-based explanations

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
- `risk_predictor.pkl` - Trained logistic regression model

## Training

To retrain the model:
```bash
cd backend
python -c "from ml.risk_predictor import RiskPredictor; rp = RiskPredictor(); rp.train(); rp.save('models/risk_predictor.pkl')"
```
