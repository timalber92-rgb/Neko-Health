# HealthGuard - Implementation Plan

## PROJECT OVERVIEW

Portfolio project demonstrating how predictive maintenance principles (from 6 years in industrial ML) apply to preventive healthcare. This is for a Senior Data Scientist application at Neko Health.

**Core Innovation:**
- **Predictive Model**: Random Forest to predict cardiovascular disease risk
- **Prescriptive Model**: Q-Learning RL agent to optimize intervention strategies
- **Full-Stack Demo**: React dashboard showing risk scores + AI-recommended interventions

**Target Narrative:**
"I've spent 6 years predicting when equipment will fail 30 days before it happens. Now I'm applying the same principles to human health - predicting cardiovascular events years in advance and optimizing interventions to prevent them."

---

## DATASET

**UCI Heart Disease Dataset**
- **Source**: https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data
- **Size**: 303 patients, 14 features
- **Target**: Presence of heart disease (0 = no disease, 1-4 = disease severity)
- **Features**:
  - age: Age in years
  - sex: Sex (1 = male; 0 = female)
  - cp: Chest pain type (1-4)
  - trestbps: Resting blood pressure (mm Hg)
  - chol: Serum cholesterol (mg/dl)
  - fbs: Fasting blood sugar > 120 mg/dl (1 = true; 0 = false)
  - restecg: Resting ECG results (0-2)
  - thalach: Maximum heart rate achieved
  - exang: Exercise induced angina (1 = yes; 0 = no)
  - oldpeak: ST depression induced by exercise
  - slope: Slope of peak exercise ST segment (1-3)
  - ca: Number of major vessels colored by fluoroscopy (0-3)
  - thal: Thalassemia (3 = normal; 6 = fixed defect; 7 = reversible defect)
  - target: Diagnosis of heart disease (0 = no, 1-4 = yes)

---

## TECH STACK

### Backend (Python 3.11+)
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
scikit-learn==1.4.0
pandas==2.2.0
numpy==1.26.3
pydantic==2.5.3
python-multipart==0.0.6
joblib==1.3.2
matplotlib==3.8.2
seaborn==0.13.1
```

### Frontend (React 18)
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "recharts": "^2.10.3",
  "axios": "^1.6.5",
  "tailwindcss": "^3.4.1"
}
```

### Development Environment
- DevContainer with Python 3.11 and Node.js 18
- Docker Compose for consistent development
- VSCode extensions for Python and React

---

## ML APPROACH

### 1. Risk Prediction Model
- **Algorithm**: RandomForestClassifier (n_estimators=100)
- **Justification**: Interpretable, handles non-linear relationships, provides feature importance
- **Output**: Binary classification (disease/no disease) + probability score (0-100% risk)
- **Metrics**: Accuracy, Precision, Recall, F1, ROC-AUC

### 2. RL Intervention Agent
- **Algorithm**: Q-Learning (tabular, epsilon-greedy)
- **State Space**: Discretized health metrics [age_bin, bp_bin, chol_bin, glucose_bin, ecg_status]
- **Action Space**: 5 intervention strategies
  - 0: **Monitor Only** (quarterly checkups)
  - 1: **Lifestyle Intervention** (diet, exercise program)
  - 2: **Single Medication** (e.g., statin or beta-blocker)
  - 3: **Combination Therapy** (medication + lifestyle)
  - 4: **Intensive Treatment** (multiple medications + intensive lifestyle)
- **Reward Function**:
```python
reward = -risk_score - (intervention_cost * 0.1) + (quality_of_life_factor * 0.2)
```
- **Training**: Simulated patient trajectories based on historical data
- **Evaluation**: Off-policy evaluation comparing RL vs. standard clinical guidelines

---

## IMPLEMENTATION PHASES

### ✅ PHASE 1: DATA PIPELINE & RISK MODEL [COMPLETED]

#### ✅ File 1: backend/data/load.py [COMPLETED]
**Status**: Implemented and tested successfully

**Implementation**:
- `download_data()` - Downloads UCI data from URL, saves to raw/
- `clean_data(df)` - Handles missing values (median imputation), converts types
- `preprocess_data(df)` - Normalizes features, creates train/val/test splits (70/15/15)
- `load_processed_data()` - Loads pre-processed data for model training
- `run_pipeline()` - Main execution orchestrator
- Comprehensive logging, type hints, docstrings

**Results**:
- 303 patients processed
- 6 missing values imputed (4 in 'ca', 2 in 'thal')
- Binary classification target created
- Stratified splits: 211 train / 46 val / 46 test
- StandardScaler fitted on training data only

---

#### ✅ File 2: backend/ml/risk_predictor.py [COMPLETED]
**Status**: Implemented, trained, and tested successfully

**Implementation**:
- `RiskPredictor` class with full Random Forest implementation
- 5-fold stratified cross-validation during training
- Comprehensive evaluation metrics (accuracy, precision, recall, F1, ROC-AUC)
- Feature importance extraction and ranking
- Risk score calculation (0-100%) with risk classification
- Model persistence (save/load) using joblib
- Type hints and comprehensive docstrings

**Results**:
- **Validation ROC-AUC: 0.861**
- **Test ROC-AUC: 0.945** ⭐
- **Test Accuracy: 89.1%**
- **Test F1 Score: 0.884**
- Cross-validation: 81.5% ± 5.2%
- Top features: thal (0.166), ca (0.143), cp (0.123)
- Model saved to: `backend/models/risk_predictor.pkl`

**Key Decisions**:
- Used stratified CV due to small dataset (303 samples)
- Implemented max_depth=10, min_samples_split=5 to prevent overfitting
- Used class_weight='balanced' for class imbalance
- Feature importance returned as dict for API compatibility

---

#### ✅ File 3: backend/requirements.txt [COMPLETED]

**Requirements**:
- RiskPredictor class with train() and predict() methods
- RandomForestClassifier implementation
- Cross-validation during training
- Calculate risk score (0-100%) from prediction probability
- Extract and rank feature importances
- Save/load model using joblib
- Evaluation metrics: accuracy, precision, recall, F1, ROC-AUC
- Type hints and comprehensive docstrings

**Implementation Details**:
```python
class RiskPredictor:
    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        """Initialize Random Forest classifier"""

    def train(self, X_train: pd.DataFrame, y_train: pd.Series,
              X_val: pd.DataFrame, y_val: pd.Series) -> Dict[str, float]:
        """Train model with cross-validation, return metrics"""

    def predict(self, patient_data: pd.DataFrame) -> Dict[str, Any]:
        """Predict risk score and return classification + feature importance"""

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
        """Evaluate model on test set"""

    def save(self, path: Path) -> None:
        """Save model to disk"""

    def load(self, path: Path) -> None:
        """Load model from disk"""

    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance rankings"""
```

---

#### ⏳ File 3: backend/requirements.txt [COMPLETED]
Already created with all dependencies.

---

### ✅ PHASE 2: RL AGENT [COMPLETED]

#### ✅ File: backend/ml/rl_agent.py [COMPLETED]
**Status**: Implemented, trained, and tested successfully

**Implementation**:
- `InterventionAgent` class with full Q-Learning implementation
- State space: 5 features (age, trestbps, chol, thalach, oldpeak) discretized into 5 bins
- Action space: 5 interventions (Monitor Only → Intensive Treatment)
- Epsilon-greedy exploration (epsilon=0.1)
- Learning rate alpha=0.1, discount factor gamma=0.95
- Reward function: risk_reduction - cost_penalty - qol_penalty
- Quantile-based binning for balanced state distribution
- Intervention simulation with realistic effect sizes
- Q-table persistence (save/load) using pickle
- Type hints and comprehensive docstrings

**Actions Defined**:
0. **Monitor Only**: Quarterly checkups, no intervention
1. **Lifestyle Intervention**: Diet/exercise program (5-10% improvement)
2. **Single Medication**: Statin or beta-blocker (10-15% improvement)
3. **Combination Therapy**: Medication + lifestyle (15-20% improvement)
4. **Intensive Treatment**: Multiple medications + intensive lifestyle (20-25% improvement)

**Results**:
- **10,000 training episodes completed**
- **263 unique states explored**
- **Final average reward: 0.719**
- Reward progression: 0.121 → 0.459 → 0.537 → 0.616 → 0.630
- Average Q-value change converged to ~0.06
- Agent saved to: `backend/models/intervention_agent.pkl`

**Key Decisions**:
- Used 5 features (not all 13) to avoid curse of dimensionality
- Quantile binning instead of uniform for better coverage
- Quadratic QoL penalty (action²) to discourage over-treatment
- Simulated interventions based on clinical literature ranges

---

### ✅ PHASE 3: FASTAPI BACKEND [COMPLETED]

#### ✅ File 1: backend/api/models.py [COMPLETED]
**Status**: Implemented and tested successfully

**Implementation**:
All Pydantic models with comprehensive validation and examples:

- `PatientInput`: 13 clinical features with range validation
- `RiskPrediction`: Risk score, classification, probability, feature importance
- `InterventionRecommendation`: Action, description, cost, intensity, expected outcomes, Q-values
- `SimulationRequest`: Patient data + action to simulate
- `HealthStatus`: Current vs optimized metrics with risk comparison
- `ErrorResponse`: Standardized error format
- `HealthCheckResponse`: API status and model availability

**Features**:
- Field validation (e.g., age: 0-120, ca: 0-3)
- Comprehensive field descriptions for auto-generated docs
- Example data in schema for OpenAPI documentation
- Type safety with Pydantic v2

---

#### ✅ File 2: backend/api/main.py [COMPLETED]
**Status**: Implemented and tested successfully

**Endpoints Implemented**:
- `GET /` - Health check (tests: ✅ returns healthy status)
- `POST /api/predict` - Risk prediction (tests: ✅ returns 37% risk, Medium Risk)
- `POST /api/recommend` - RL recommendation (tests: ✅ returns Monitor Only)
- `POST /api/simulate` - Intervention simulation (tests: ✅ returns metric changes)

**Features**:
- Async lifespan management for model loading
- Global exception handler with logging
- CORS middleware (allow all origins for development)
- Automatic StandardScaler normalization
- Comprehensive error handling with HTTP status codes
- Models loaded once on startup (efficient)
- Logging for all predictions and recommendations

**API Documentation**:
- Auto-generated OpenAPI docs at `/docs`
- ReDoc documentation at `/redoc`
- All endpoints have type-safe request/response models

**Tested**:
```bash
# All endpoints working correctly
curl http://localhost:8000/  # ✅ healthy
curl -X POST http://localhost:8000/api/predict  # ✅ 37.2% risk
curl -X POST http://localhost:8000/api/recommend  # ✅ Monitor Only
curl -X POST http://localhost:8000/api/simulate  # ✅ metric simulation
```

---

### ⏳ PHASE 4: REACT FRONTEND

#### File 1: frontend/package.json
Dependencies: react, react-dom, vite, axios, recharts, tailwindcss

#### File 2: frontend/src/components/PatientForm.jsx
- Form with inputs for all 13 patient features
- Input validation
- Tooltips explaining each field
- Submit button triggering API call
- Loading state during prediction

#### File 3: frontend/src/components/RiskDisplay.jsx
- Circular gauge showing risk score (0-100%)
- Color coding: green (<30%), yellow (30-70%), red (>70%)
- Risk classification label
- Feature importance bar chart (top 5 factors)

#### File 4: frontend/src/components/RecommendationPanel.jsx
- Display RL-recommended intervention
- Explanation of why this intervention was chosen
- Expected outcomes (projected risk reduction)
- Comparison table: current metrics vs. optimized metrics
- Action buttons to simulate different interventions

#### File 5: frontend/src/api/client.js
Axios client with functions:
- predictRisk(patientData)
- getRecommendation(patientData)
- simulateIntervention(patientData, action)

#### File 6: frontend/src/App.jsx
- Layout with header ("HealthGuard - Predictive Health Monitoring")
- PatientForm component
- Conditional rendering of RiskDisplay and RecommendationPanel
- State management for patient data and predictions

---

### ⏳ PHASE 5: DOCUMENTATION

#### README.md

**Sections**:
1. **Project Overview** - Predictive maintenance → preventive healthcare narrative
2. **Problem Statement** - Why this matters (cardiovascular disease statistics)
3. **Technical Approach**
   - Architecture diagram (ASCII art is fine)
   - Why Random Forest (interpretability for healthcare)
   - Why Q-Learning (sample efficiency, explainability)
4. **Features**
   - Risk prediction with feature importance
   - RL-based intervention optimization
   - Interactive web dashboard
5. **Installation & Usage**
   - DevContainer setup (recommended)
   - Manual setup (backend + frontend)
   - Running the application
6. **Results**
   - Model performance metrics
   - Example predictions
   - RL agent evaluation
7. **Technical Decisions**
   - Why not deep learning? (limited data, interpretability requirements)
   - Why not more complex RL? (sample efficiency, debugging ease)
8. **Future Work**
   - Clinical validation with real patients
   - Larger datasets (MIMIC-III)
   - Deep RL (PPO, SAC) with more data
   - Multi-objective optimization
   - Integration with wearable devices
9. **Connection to Neko Health**
   - How this scales to continuous monitoring
   - Potential for real-time risk updates
10. **License & Citations**

---

## KEY TECHNICAL DECISIONS

**Q: Why Random Forest over Neural Networks?**
A: "Healthcare requires interpretability. Random Forest provides feature importance out-of-the-box, allowing doctors to understand which factors drive risk predictions. With only 303 samples, RF is also more robust than deep learning."

**Q: Why Q-Learning over Deep RL (DQN, PPO)?**
A: "Sample efficiency. With limited patient data, tabular Q-learning is more data-efficient than deep RL. It's also easier to debug and explain - critical for healthcare applications."

**Q: How realistic is the RL simulation?**
A: "This is a proof-of-concept. The reward function and state transitions are simplified approximations. Real deployment would require clinical validation, longitudinal patient data, and collaboration with medical professionals."

**Q: Why 5 intervention actions?**
A: "Balance between granularity and learnability. More actions would require more data. These 5 capture the main clinical decision points: monitoring intensity, lifestyle vs. medication, single vs. combination therapy."

---

## PROGRESS TRACKING

### ✅ Completed
- [x] **Phase 1: Data Pipeline & Risk Model** - COMPLETE
  - [x] Project structure created
  - [x] DevContainer setup (Python 3.11 + Node.js 18)
  - [x] .gitignore configuration
  - [x] backend/requirements.txt
  - [x] backend/data/load.py - Data pipeline (303 patients, stratified splits)
  - [x] backend/ml/risk_predictor.py - Random Forest (89% accuracy, 94.5% ROC-AUC)
  - [x] Model saved to backend/models/risk_predictor.pkl

- [x] **Phase 2: RL Agent** - COMPLETE
  - [x] backend/ml/rl_agent.py - Q-Learning agent (263 states, 0.719 reward)
  - [x] Agent saved to backend/models/intervention_agent.pkl

- [x] **Phase 3: FastAPI Backend** - COMPLETE
  - [x] backend/api/models.py - Pydantic schemas with validation
  - [x] backend/api/main.py - FastAPI endpoints (all 4 tested ✅)

### ⏳ In Progress
- [ ] **Phase 4: React Frontend** - NEXT
  - [ ] frontend/package.json setup
  - [ ] frontend/src/components/PatientForm.jsx
  - [ ] frontend/src/components/RiskDisplay.jsx
  - [ ] frontend/src/components/RecommendationPanel.jsx
  - [ ] frontend/src/api/client.js
  - [ ] frontend/src/App.jsx

### 🔜 Pending
- [ ] **Phase 5: Documentation**
  - [ ] README.md - Comprehensive documentation
  - [ ] Model performance visualizations
  - [ ] Architecture diagrams
  - [ ] Deployment guide

---

## QUICK START (Next Session)

1. **Open in DevContainer** (recommended):
   ```bash
   # VSCode: Reopen in Container
   # Already set up and working ✅
   ```

2. **Verify Backend is Working**:
   ```bash
   cd healthguard/backend

   # Test trained models
   python -m ml.risk_predictor  # Should show 89% accuracy
   python -m ml.rl_agent        # Should show 263 states explored

   # Start API server
   python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
   # Open http://localhost:8000/docs for Swagger UI
   ```

3. **Current State**:
   - ✅ Backend fully implemented and tested
   - ✅ ML models trained and saved (risk_predictor.pkl, intervention_agent.pkl)
   - ✅ FastAPI server working with 4 endpoints
   - 🎯 **NEXT**: Implement React frontend (Phase 4)

4. **Resume with Phase 4 - React Frontend**:
   ```bash
   cd healthguard/frontend
   # Initialize React app with Vite
   # Implement PatientForm, RiskDisplay, RecommendationPanel components
   ```

---

## CONTACT & APPLICATION

**Target Role**: Senior Data Scientist at Neko Health
**Portfolio Goal**: Demonstrate ML expertise transitioning from industrial predictive maintenance to preventive healthcare
**Key Differentiator**: 6 years of production ML experience applied to a novel healthcare domain
