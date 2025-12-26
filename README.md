# HealthGuard

> **From Predictive Maintenance to Preventive Healthcare**
>
> Applying 6 years of industrial ML experience to cardiovascular disease prevention

## 📊 Status Badges

### Technology Stack
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

### Build & Test Status
[![Backend Tests](https://github.com/timalber92-rgb/Neko-Health/actions/workflows/backend-tests.yml/badge.svg?branch=main)](https://github.com/timalber92-rgb/Neko-Health/actions/workflows/backend-tests.yml)
[![Frontend Tests](https://github.com/timalber92-rgb/Neko-Health/actions/workflows/frontend-tests.yml/badge.svg?branch=main)](https://github.com/timalber92-rgb/Neko-Health/actions/workflows/frontend-tests.yml)
[![CI/CD Pipeline](https://github.com/timalber92-rgb/Neko-Health/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/timalber92-rgb/Neko-Health/actions/workflows/ci.yml)

### Security & Quality
[![CodeQL](https://github.com/timalber92-rgb/Neko-Health/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/timalber92-rgb/Neko-Health/actions/workflows/codeql.yml)
[![Security Audit](https://github.com/timalber92-rgb/Neko-Health/actions/workflows/security-audit.yml/badge.svg?branch=main)](https://github.com/timalber92-rgb/Neko-Health/actions/workflows/security-audit.yml)
[![Dependency Updates](https://github.com/timalber92-rgb/Neko-Health/actions/workflows/dependency-update.yml/badge.svg?branch=main)](https://github.com/timalber92-rgb/Neko-Health/actions/workflows/dependency-update.yml)

## Overview

**HealthGuard** is a full-stack machine learning application that demonstrates how predictive maintenance principles can be applied to preventive healthcare. Just as industrial ML predicts equipment failures 30 days in advance, HealthGuard predicts cardiovascular disease risk years ahead and recommends optimal intervention strategies.

This project was developed as a portfolio piece for a Senior Data Scientist application at **Neko Health**, showcasing:
- **Predictive ML**: Logistic Regression classifier with automatic feature scaling (82.6% accuracy, 93.9% ROC-AUC)
- **Clinical Decision Support**: Guideline-based intervention recommendations following ACC/AHA standards
- **Full-Stack Implementation**: FastAPI backend + React dashboard with interactive visualization

> **Recent Updates**:
> - Integrated StandardScaler into model for automatic feature normalization
> - Migrated from Q-Learning to guideline-based recommendations for improved clinical validity
>
> See [docs/CHANGELOG.md](docs/CHANGELOG.md) for details.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Architecture](#architecture)
- [Features](#features)
- [Technical Approach](#technical-approach)
  - [Why Logistic Regression?](#why-logistic-regression)
  - [Feature Scaling](#feature-scaling)
  - [Why Guideline-Based Recommendations?](#why-guideline-based-recommendations)
  - [Model Performance](#model-performance)
- [Installation](#installation)
  - [DevContainer Setup (Recommended)](#devcontainer-setup-recommended)
  - [Manual Setup](#manual-setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Technical Decisions](#technical-decisions)
- [Future Work](#future-work)
- [Connection to Neko Health](#connection-to-neko-health)
- [Dataset](#dataset)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Problem Statement

Cardiovascular disease (CVD) is the **leading cause of death globally**, accounting for 17.9 million deaths per year (WHO, 2021). Early detection and preventive intervention can significantly reduce mortality and improve quality of life.

**The Challenge**:
- Traditional risk assessment is reactive, often detecting disease after symptoms appear
- Clinical decision-making relies on general guidelines, not personalized intervention strategies
- Healthcare systems lack tools to optimize the balance between treatment effectiveness, cost, and patient quality of life

**HealthGuard's Solution**:
- **Predict** cardiovascular disease risk using machine learning on clinical biomarkers
- **Prescribe** personalized intervention strategies using reinforcement learning
- **Visualize** risk factors and expected outcomes through an interactive dashboard

This mirrors the **predictive maintenance workflow** in industrial settings:
1. **Predict** equipment failure before it happens
2. **Prescribe** optimal maintenance strategy (repair now vs. monitor vs. replace)
3. **Optimize** for cost, downtime, and safety

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        HEALTHGUARD SYSTEM                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐          ┌──────────────────┐          ┌──────────────────┐
│                  │          │                  │          │                  │
│  React Frontend  │  ◄───►   │  FastAPI Backend │  ◄───►   │   ML Models      │
│   (Port 5173)    │   REST   │   (Port 8000)    │          │   (.pkl files)   │
│                  │   API    │                  │          │                  │
└──────────────────┘          └──────────────────┘          └──────────────────┘
        │                              │                              │
        │                              │                              │
    ┌───▼────┐                  ┌──────▼──────┐              ┌────────▼────────┐
    │ Patient│                  │  Pydantic   │              │  Risk Predictor │
    │  Form  │                  │  Validation │              │  LogisticReg    │
    │        │                  │             │              │ + StandardScaler│
    │13 Input│                  │  4 Endpoints│              │                 │
    │ Fields │                  │             │              │  82.6% Accuracy │
    └───┬────┘                  └──────┬──────┘              │  93.9% ROC-AUC  │
        │                              │                     │                 │
    ┌───▼────┐                  ┌──────▼──────┐              └─────────────────┘
    │  Risk  │                  │   /predict  │
    │Display │                  │  /recommend │              ┌─────────────────┐
    │        │                  │  /simulate  │              │ Guideline-Based │
    │ Gauge  │                  │   /health   │              │ Recommender     │
    │+ Chart │                  │             │              │                 │
    └───┬────┘                  └─────────────┘              │ ACC/AHA Rules   │
        │                                                    │ Risk-Stratified │
    ┌───▼────┐                                               │ Deterministic   │
    │ Recom- │                                               │                 │
    │mendaton│                                               └─────────────────┘
    │ Panel  │
    │        │
    │Simulate│
    │ Button │
    └────────┘
```

**Data Flow**:
1. **User Input**: 13 clinical features entered via React form
2. **API Request**: POST to `/api/predict` and `/api/recommend`
3. **Automatic Scaling**: Model applies StandardScaler internally (embedded in model file)
4. **Risk Prediction**: Logistic Regression predicts disease probability → risk score (0-100%)
5. **Guideline Recommendation**: ACC/AHA rule-based system recommends optimal intervention
6. **Simulation**: User can simulate different interventions to see expected outcomes
7. **Visualization**: Results displayed with risk gauge, feature importance, and comparison charts

---

## Features

### 1. Risk Prediction
- **Binary classification**: Disease vs. No Disease
- **Risk score**: 0-100% probability with risk categorization (Low/Medium/High)
- **Feature importance**: Identifies which biomarkers contribute most to risk
- **Model**: Logistic Regression with embedded StandardScaler, trained on 303 patients
- **Automatic scaling**: Raw patient data is scaled internally before prediction

### 2. Intervention Recommendation
- **5 intervention strategies**:
  - **Monitor Only**: Quarterly checkups, no active treatment
  - **Lifestyle Intervention**: Diet + exercise program (5-10% improvement)
  - **Single Medication**: Statin or beta-blocker (10-15% improvement)
  - **Combination Therapy**: Medication + lifestyle (15-20% improvement)
  - **Intensive Treatment**: Multiple medications + intensive lifestyle (20-25% improvement)
- **Guideline-Based Logic**: Risk-stratified recommendations following ACC/AHA guidelines
- **Explainability**: Detailed clinical rationale with identified risk factors for every recommendation

### 3. Interactive Dashboard
- **Patient Form**: 13 clinical inputs with validation and example presets
- **Risk Display**: Circular gauge with color-coded risk levels
- **Feature Importance Chart**: Bar chart showing top 5 risk factors
- **Recommendation Panel**: AI-recommended intervention with explanation
- **Simulation**: Compare different interventions side-by-side
- **Metrics Comparison**: Visualize expected changes in blood pressure, cholesterol, etc.

---

## Technical Approach

### Why Logistic Regression?

**Simplicity and interpretability** are critical in healthcare applications. Logistic Regression provides:

1. **Coefficient Interpretability**: Each feature's contribution to risk is clear and quantifiable
2. **Probabilistic Outputs**: Natural probability estimates for risk scores (0-100%)
3. **Fast Inference**: Predictions in <10ms, suitable for real-time applications
4. **Clinical Validation**: Linear models are well-understood in medical research
5. **Regulatory Compliance**: Simpler to explain to regulatory bodies (FDA, medical boards)

**Hyperparameters**:
- `max_iter=2000`: Ensures convergence with scaled features
- `class_weight='balanced'`: Handles class imbalance in training data
- `solver='lbfgs'`: Efficient for small to medium datasets
- `random_state=42`: Reproducible results

### Feature Scaling

**StandardScaler is critical** for Logistic Regression performance:

- **Why needed**: Logistic Regression is sensitive to feature magnitudes (age=60, cholesterol=200, etc.)
- **Without scaling**: Model performs poorly (ROC-AUC ~0.50, essentially random)
- **With scaling**: Model achieves 93.9% ROC-AUC and 82.6% accuracy
- **Implementation**: Scaler is embedded in model file and applied automatically during prediction
- **User experience**: API and tests pass raw features - scaling happens transparently

### Why Guideline-Based Recommendations?

**Clinical validity** and **explainability** are critical for healthcare applications. The guideline-based approach offers:

1. **No Training Required**: Purely rule-based using ACC/AHA cardiovascular disease guidelines
2. **Explainability**: Every recommendation includes detailed clinical rationale
3. **Risk Factor Identification**: Automatically identifies and highlights severe/moderate risk factors
4. **Deterministic**: Consistent recommendations for the same input
5. **Clinical Validity**: Based on evidence-based medical guidelines

**Risk Stratification**:
- **<15% risk**: Monitor Only
- **15-30% risk**: Lifestyle Intervention
- **30-50% risk**: Single Medication
- **50-70% risk**: Combination Therapy
- **≥70% risk**: Intensive Treatment

**Risk Factor Escalation**:
- Identifies severe risk factors (BP ≥160, Cholesterol ≥280, ST depression ≥2.0)
- Escalates treatment when multiple severe factors present
- Never recommends monitoring-only for high-risk patients (≥50%)

**Advantages over RL**:
- Works immediately without training data
- Transparent decision-making process
- Suitable for medical/regulatory compliance
- No "unseen state" problem
- 20% faster, 95% less memory

### Model Performance

#### Risk Predictor (Logistic Regression + StandardScaler)
| Metric         | Validation Set | Test Set  |
|----------------|----------------|-----------|
| **ROC-AUC**    | 0.871          | **0.939** |
| **Accuracy**   | 80.4%          | **82.6%** |
| **Precision**  | 0.833          | 0.760     |
| **Recall**     | 0.714          | 0.905     |
| **F1 Score**   | 0.769          | **0.826** |

**Cross-Validation**: 83.8% ± 6.0% (5-fold stratified)

**Top 5 Risk Factors** (absolute coefficient values):
1. **Major Vessels Colored** (ca): 22.2% importance
2. **Sex** (male): 12.6% importance
3. **Thalassemia** (thal): 11.5% importance
4. **Chest Pain Type** (cp): 11.0% importance
5. **ST Slope** (slope): 8.2% importance

#### Guideline Recommender
| Metric                     | Value        |
|----------------------------|--------------|
| **Training Required**      | None         |
| **Response Time**          | ~40ms        |
| **Memory Footprint**       | <10MB        |
| **Test Coverage**          | 24 tests     |
| **Deterministic**          | Yes          |

**Validation**: 15 end-to-end scenario tests covering risk monotonicity, complete patient journey, and edge cases

---

## Installation

### DevContainer Setup (Recommended)

This project includes a DevContainer configuration for VSCode with all dependencies pre-installed.

1. **Prerequisites**:
   - [Docker](https://www.docker.com/get-started)
   - [VSCode](https://code.visualstudio.com/)
   - [Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

2. **Open in Container**:
   ```bash
   # Clone repository
   git clone <repository-url>
   cd healthguard

   # Open in VSCode
   code .

   # VSCode: Press F1 → "Dev Containers: Reopen in Container"
   # Wait for container to build (~2-3 minutes first time)
   ```

3. **Container includes**:
   - Python 3.11 with all backend dependencies
   - Node.js 18 with all frontend dependencies
   - Pre-trained ML models (if committed to repo)

### Manual Setup

#### Backend Setup

```bash
# Navigate to backend directory
cd healthguard/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Train risk predictor (if not already trained)
python -m ml.risk_predictor  # Trains Random Forest model
# Note: Guideline recommender requires no training

# Start API server
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at [http://localhost:8000](http://localhost:8000)

API documentation at [http://localhost:8000/docs](http://localhost:8000/docs)

#### Frontend Setup

```bash
# Navigate to frontend directory
cd healthguard/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at [http://localhost:3000](http://localhost:3000)

---

## 🚀 Quick Start

```bash
# Terminal 1: Start backend
cd backend
python -m uvicorn api.main:app --reload

# Terminal 2: Start frontend (in new terminal)
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) to use the application.

See [QUICKSTART.md](QUICKSTART.md) for detailed setup or [DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md) for production deployment.

---

## Security

This project follows security best practices:

- **API Key Authentication**: All production endpoints require valid API keys
- **CORS Protection**: Configured for specific frontend domains only
- **Rate Limiting**: Prevents abuse with configurable request limits
- **Secret Management**: Environment variables for all sensitive data
- **Dependency Scanning**: Automated security updates via Dependabot
- **Secret Scanning**: GitHub alerts for accidentally committed secrets

For deployment and security configuration:
- [DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md) - Quick production deployment guide (30 minutes)
- [SECURITY_DEPLOYMENT.md](SECURITY_DEPLOYMENT.md) - Comprehensive security documentation

Security features:
- GitHub Dependabot enabled for automatic dependency updates
- GitHub Secret Scanning enabled
- CodeQL analysis via GitHub Actions
- API key rotation procedures documented
- OWASP Top 10 coverage

---

## Usage

### 1. Start Backend and Frontend

```bash
# Terminal 1: Backend
cd healthguard/backend
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend
cd healthguard/frontend
npm run dev
```

### 2. Access Dashboard

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 3. Analyze a Patient

1. **Load Example**: Click "Moderate Risk Patient" or "High Risk Patient" for pre-filled data
2. **Enter Data**: Or manually enter 13 clinical features
3. **Analyze**: Click "Analyze Risk" button
4. **View Results**:
   - Risk score with circular gauge
   - Feature importance chart (what drives the risk?)
   - AI-recommended intervention
   - Expected risk reduction
5. **Simulate**: Click different intervention cards to compare strategies

### 4. API Usage (Programmatic)

```python
import requests

# Example patient data
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
    "thal": 6
}

# Predict risk
response = requests.post("http://localhost:8000/api/predict", json=patient)
print(response.json())
# {
#   "risk_score": 78.5,
#   "classification": "High Risk",
#   "has_disease": true,
#   "probability": 0.785,
#   "feature_importance": {"thal": 0.166, "ca": 0.143, ...}
# }

# Get guideline-based recommendation
response = requests.post("http://localhost:8000/api/recommend", json=patient)
print(response.json())
# {
#   "action": 3,
#   "action_name": "Combination Therapy",
#   "description": "Medication plus supervised lifestyle program",
#   "expected_risk_reduction": 26.2,
#   "rationale": "Patient has high cardiovascular disease risk (78.5%)...",
#   "risk_factors": {
#     "severe_count": 2,
#     "moderate_count": 1,
#     "details": ["severe hypertension (BP: 145 mmHg)", ...]
#   }
# }
```

---

## Project Structure

```
healthguard/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application (4 endpoints)
│   │   └── models.py            # Pydantic schemas (7 models)
│   ├── data/
│   │   ├── __init__.py
│   │   ├── load.py              # Data pipeline (download, clean, preprocess)
│   │   ├── raw/                 # Downloaded UCI dataset
│   │   └── processed/           # Preprocessed train/val/test splits
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── risk_predictor.py          # Random Forest classifier
│   │   ├── guideline_recommender.py   # Guideline-based recommender (active)
│   │   ├── rl_agent.py                # Q-Learning agent (legacy)
│   │   └── intervention_utils.py      # Shared intervention effects
│   ├── models/
│   │   ├── risk_predictor.pkl   # Trained Random Forest model
│   │   └── intervention_agent.pkl  # Trained Q-table
│   ├── tests/                   # Unit and integration tests
│   │   ├── __init__.py
│   │   ├── test_risk_predictor.py
│   │   ├── test_rl_agent.py
│   │   ├── test_api.py
│   │   └── test_integration.py
│   ├── requirements.txt         # Production dependencies
│   └── requirements-dev.txt     # Development dependencies (pytest, etc.)
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── PatientForm.jsx           # 13-field clinical form
│   │   │   ├── RiskDisplay.jsx           # Risk gauge + feature chart
│   │   │   └── RecommendationPanel.jsx   # RL recommendations + simulation
│   │   ├── api/
│   │   │   └── client.js                 # Axios API client
│   │   ├── App.jsx                       # Main application
│   │   └── main.jsx                      # Entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── docs/
│   ├── DEPLOYMENT_GUIDE.md              # Production deployment guide
│   ├── SECURITY_SETUP.md                 # Security configuration
│   ├── PHASE1_SECURITY_IMPLEMENTATION.md # Security implementation details
│   ├── IMPLEMENTATION_PLAN.md            # Detailed implementation plan
│   └── REFACTORING_ANALYSIS.md          # Future improvements
│
├── .devcontainer/
│   └── devcontainer.json        # VSCode DevContainer config
│
├── .gitignore
├── docker-compose.yml            # Local development setup
├── docker-compose.prod.yml       # Production Docker setup
├── Dockerfile                    # Docker container config
├── render.yaml                   # Render.com deployment config
├── vercel.json                   # Vercel deployment config
├── test_staging.sh               # Automated testing script
├── README.md                     # This file
└── QUICKSTART.md                 # Quick start guide
```

---

## Technical Decisions

### Q: Why Random Forest over Neural Networks?

**A**: Healthcare requires interpretability. Random Forest provides feature importance out-of-the-box, allowing doctors to understand which factors drive risk predictions. With only 303 samples, RF is also more robust than deep learning and less prone to overfitting.

### Q: Why Guideline-Based over Reinforcement Learning?

**A**: Clinical validity and explainability. Guideline-based recommendations are transparent, deterministic, and based on established medical evidence (ACC/AHA guidelines). This is more appropriate for healthcare than learned policies from limited data. Every recommendation includes detailed clinical rationale that can be audited by medical professionals.

### Q: How realistic are the intervention simulations?

**A**: This is a **proof-of-concept**. The intervention effects are based on clinical literature but simplified. Real deployment would require:
- Clinical validation with medical professionals
- Longitudinal patient data to validate intervention effects
- FDA/regulatory approval for medical decision support
- Integration with electronic health records (EHR)

### Q: Why 5 intervention actions?

**A**: Balance between clinical granularity and practical decision points. These 5 actions capture the main clinical escalation pathway: monitoring → lifestyle → medication → combination → intensive treatment, which aligns with standard cardiovascular disease management protocols.

---

## Future Work

### Short-Term Improvements
- [ ] **Hyperparameter tuning** with GridSearchCV for Random Forest
- [ ] **Configurable risk thresholds** via JSON configuration file
- [ ] **SHAP values** for individual prediction explainability
- [ ] **Reference citations** linking intervention effects to source studies
- [ ] **Time-based simulation** showing 6-month and 1-year outcomes

### Long-Term Vision
- [ ] **Clinical validation** with real patients and medical professionals
- [ ] **Larger datasets**: Train on MIMIC-III, UK Biobank, or All of Us Research Program
- [ ] **Continuous monitoring**: Integrate with wearable devices (Apple Watch, Fitbit) for real-time risk updates
- [ ] **Longitudinal predictions**: Predict risk at 1, 5, 10 years instead of binary classification
- [ ] **Personalized intervention effects**: Learn individual treatment response from patient history
- [ ] **Multi-disease models**: Extend to diabetes, stroke, kidney disease, etc.

### Scaling to Neko Health

This proof-of-concept demonstrates capabilities that could scale to **Neko Health's vision**:

1. **Comprehensive Health Scans**: Neko's 100+ biomarker scans provide much richer input than 13 features
2. **Continuous Monitoring**: RL agent could update recommendations as new data arrives
3. **Preventive Care**: Shift from reactive treatment to proactive intervention
4. **Personalization**: Optimize interventions for individual patient preferences and constraints
5. **Population Health**: Aggregate insights to identify high-risk cohorts for targeted outreach

---

## Connection to Neko Health

Neko Health is revolutionizing preventive care with comprehensive, technology-enabled health scans. HealthGuard aligns with this vision by demonstrating:

### 1. Predictive Analytics
- **Neko**: Measures 100+ biomarkers in a 30-minute scan
- **HealthGuard**: Shows how ML can extract actionable insights from biomarker data
- **Synergy**: More features → better predictions, but same interpretable ML approach

### 2. Preventive Intervention
- **Neko**: Detects health issues before symptoms appear
- **HealthGuard**: Recommends optimal preventive strategies using RL
- **Synergy**: Early detection + optimal intervention = maximum impact

### 3. Personalization
- **Neko**: Tailored health insights for each individual
- **HealthGuard**: Personalized recommendations balancing effectiveness, cost, and QoL
- **Synergy**: RL agents can learn individual treatment responses over time

### 4. Technology-First Approach
- **Neko**: Full-body scanners, biomarker panels, digital health records
- **HealthGuard**: ML models, interactive dashboards, API-driven architecture
- **Synergy**: Both leverage technology to scale healthcare beyond traditional constraints

### 5. From Maintenance to Medicine

My 6 years in industrial ML taught me how to:
- **Predict failures** before they happen (equipment → human health)
- **Optimize interventions** balancing cost and effectiveness (maintenance → treatment)
- **Scale ML systems** to production (factories → hospitals)

HealthGuard demonstrates that these skills transfer directly to healthcare, where the stakes are even higher and the impact even greater.

---

## Dataset

**UCI Heart Disease Dataset**
- **Source**: [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/heart+disease)
- **Size**: 303 patients from Cleveland Clinic
- **Features**: 13 clinical and diagnostic features
- **Target**: Binary classification (disease vs. no disease)

**Features**:
- `age`: Age in years
- `sex`: Sex (1 = male, 0 = female)
- `cp`: Chest pain type (1-4)
- `trestbps`: Resting blood pressure (mm Hg)
- `chol`: Serum cholesterol (mg/dl)
- `fbs`: Fasting blood sugar > 120 mg/dl
- `restecg`: Resting ECG results (0-2)
- `thalach`: Maximum heart rate achieved
- `exang`: Exercise induced angina (1 = yes, 0 = no)
- `oldpeak`: ST depression induced by exercise
- `slope`: Slope of peak exercise ST segment (1-3)
- `ca`: Number of major vessels colored by fluoroscopy (0-3)
- `thal`: Thalassemia (3 = normal, 6 = fixed defect, 7 = reversible defect)

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Data Citation

UCI Heart Disease Dataset:
```bibtex
@misc{uci_heart_disease,
  author = {Detrano, R. and Janosi, A. and Steinbrunn, W. and Pfisterer, M. and Schmid, J.},
  title = {Heart Disease Dataset},
  year = {1988},
  publisher = {UCI Machine Learning Repository},
  url = {https://archive.ics.uci.edu/ml/datasets/heart+disease}
}
```

---

## Documentation

Additional documentation is available in the [docs/](docs/) directory:

### General Documentation
- **[CHANGELOG.md](docs/CHANGELOG.md)**: Recent updates and migration history
- **[QUICKSTART.md](QUICKSTART.md)**: Quick start guide for local development
- **[DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)**: Production deployment instructions

### Security & Deployment
- **[DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md)**: 30-minute production deployment guide
- **[SECURITY_DEPLOYMENT.md](SECURITY_DEPLOYMENT.md)**: Comprehensive security documentation
- **[SECURITY_SETUP.md](docs/SECURITY_SETUP.md)**: Security configuration and best practices

### Risk Reduction Analysis
- **[SUMMARY.md](docs/SUMMARY.md)**: Overview of intervention system validation and expected risk reduction values
- **[INTERVENTION_DEFINITIONS.md](docs/INTERVENTION_DEFINITIONS.md)**: Complete definitions of all 5 intervention levels
- **[EXPECTED_RISK_REDUCTION_TABLE.md](docs/EXPECTED_RISK_REDUCTION_TABLE.md)**: Reference tables with expected risk reduction values
- **[RISK_REDUCTION_ANALYSIS.md](docs/RISK_REDUCTION_ANALYSIS.md)**: Detailed clinical analysis and validation

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and contribution guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built for demonstrating ML expertise in preventive healthcare**
