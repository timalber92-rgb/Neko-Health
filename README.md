# HealthGuard

> **From Predictive Maintenance to Preventive Healthcare**
>
> Applying 6 years of industrial ML experience to cardiovascular disease prevention

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Backend Tests](https://github.com/TimAlbert92/Neko-Health/actions/workflows/backend-tests.yml/badge.svg)](https://github.com/TimAlbert92/Neko-Health/actions/workflows/backend-tests.yml)
[![Frontend Tests](https://github.com/TimAlbert92/Neko-Health/actions/workflows/frontend-tests.yml/badge.svg)](https://github.com/TimAlbert92/Neko-Health/actions/workflows/frontend-tests.yml)
[![CI/CD Pipeline](https://github.com/TimAlbert92/Neko-Health/actions/workflows/ci.yml/badge.svg)](https://github.com/TimAlbert92/Neko-Health/actions/workflows/ci.yml)
[![CodeQL](https://github.com/TimAlbert92/Neko-Health/actions/workflows/codeql.yml/badge.svg)](https://github.com/TimAlbert92/Neko-Health/actions/workflows/codeql.yml)

## Overview

**HealthGuard** is a full-stack machine learning application that demonstrates how predictive maintenance principles can be applied to preventive healthcare. Just as industrial ML predicts equipment failures 30 days in advance, HealthGuard predicts cardiovascular disease risk years ahead and recommends optimal intervention strategies.

This project was developed as a portfolio piece for a Senior Data Scientist application at **Neko Health**, showcasing:
- **Predictive ML**: Random Forest classifier for cardiovascular disease risk prediction (89% accuracy, 94.5% ROC-AUC)
- **Prescriptive RL**: Q-Learning agent for personalized intervention optimization
- **Full-Stack Implementation**: FastAPI backend + React dashboard with interactive visualization

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Architecture](#architecture)
- [Features](#features)
- [Technical Approach](#technical-approach)
  - [Why Random Forest?](#why-random-forest)
  - [Why Q-Learning?](#why-q-learning)
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
│   (Port 3000)    │   REST   │   (Port 8000)    │          │   (.pkl files)   │
│                  │   API    │                  │          │                  │
└──────────────────┘          └──────────────────┘          └──────────────────┘
        │                              │                              │
        │                              │                              │
    ┌───▼────┐                  ┌──────▼──────┐              ┌────────▼────────┐
    │ Patient│                  │  Pydantic   │              │  Risk Predictor │
    │  Form  │                  │  Validation │              │ RandomForest    │
    │        │                  │             │              │  (100 trees)    │
    │13 Input│                  │  4 Endpoints│              │                 │
    │ Fields │                  │             │              │  89% Accuracy   │
    └───┬────┘                  └──────┬──────┘              │  94.5% ROC-AUC  │
        │                              │                     │                 │
    ┌───▼────┐                  ┌──────▼──────┐              └─────────────────┘
    │  Risk  │                  │   /predict  │
    │Display │                  │  /recommend │              ┌─────────────────┐
    │        │                  │  /simulate  │              │ RL Agent        │
    │ Gauge  │                  │   /health   │              │ Q-Learning      │
    │+ Chart │                  │             │              │                 │
    └───┬────┘                  └─────────────┘              │ 263 States      │
        │                                                    │ 5 Actions       │
    ┌───▼────┐                                               │ 0.719 Reward    │
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
3. **Normalization**: StandardScaler normalizes features (fitted during training)
4. **Risk Prediction**: Random Forest predicts disease probability → risk score (0-100%)
5. **RL Recommendation**: Q-Learning agent recommends optimal intervention strategy
6. **Simulation**: User can simulate different interventions to see expected outcomes
7. **Visualization**: Results displayed with risk gauge, feature importance, and comparison charts

---

## Features

### 1. Risk Prediction
- **Binary classification**: Disease vs. No Disease
- **Risk score**: 0-100% probability with risk categorization (Low/Medium/High)
- **Feature importance**: Identifies which biomarkers contribute most to risk
- **Model**: Random Forest with 100 trees, trained on 303 patients

### 2. Intervention Recommendation
- **5 intervention strategies**:
  - **Monitor Only**: Quarterly checkups, no active treatment
  - **Lifestyle Intervention**: Diet + exercise program (5-10% improvement)
  - **Single Medication**: Statin or beta-blocker (10-15% improvement)
  - **Combination Therapy**: Medication + lifestyle (15-20% improvement)
  - **Intensive Treatment**: Multiple medications + intensive lifestyle (20-25% improvement)
- **Optimization**: Balances risk reduction, treatment cost, and quality of life
- **Transparency**: Shows Q-values for all actions to explain agent's decision

### 3. Interactive Dashboard
- **Patient Form**: 13 clinical inputs with validation and example presets
- **Risk Display**: Circular gauge with color-coded risk levels
- **Feature Importance Chart**: Bar chart showing top 5 risk factors
- **Recommendation Panel**: AI-recommended intervention with explanation
- **Simulation**: Compare different interventions side-by-side
- **Metrics Comparison**: Visualize expected changes in blood pressure, cholesterol, etc.

---

## Technical Approach

### Why Random Forest?

**Interpretability** is critical in healthcare applications. While deep learning models might achieve marginally better accuracy, Random Forest provides:

1. **Feature Importance Out-of-the-Box**: Clinicians can see which biomarkers drive predictions (e.g., thalassemia test, number of colored vessels, chest pain type)
2. **Robustness with Small Data**: With only 303 patients, Random Forest is more stable than neural networks
3. **No Need for Feature Engineering**: Handles non-linear relationships and feature interactions automatically
4. **Clinical Validation**: Easier to validate with medical professionals when model logic is transparent

**Hyperparameters** (tuned to prevent overfitting):
- `n_estimators=100`: Sufficient trees for stable predictions
- `max_depth=10`: Limits tree depth to prevent memorization
- `min_samples_split=5`: Requires 5 samples to split a node
- `class_weight='balanced'`: Handles class imbalance in training data

### Why Q-Learning?

**Sample efficiency** is paramount with limited patient data. Q-Learning offers:

1. **Tabular Approach**: No neural network overhead, works well with small datasets
2. **Interpretability**: Q-values can be inspected to understand why an action was chosen
3. **Off-Policy Learning**: Learns from simulated patient trajectories without requiring real longitudinal data
4. **Explainability**: Medical professionals can audit the reward function and state transitions

**State Space** (5 features, 5 bins each = 3,125 possible states):
- Age, Blood Pressure, Cholesterol, Max Heart Rate, ST Depression
- Discretized using quantile binning for balanced state distribution

**Reward Function**:
```python
reward = risk_reduction - (action_cost * 0.1) - (action² * 0.05)
```
- **Maximize** risk reduction
- **Penalize** expensive treatments (linear cost)
- **Penalize** intensive treatments (quadratic QoL penalty to discourage over-treatment)

**Training**:
- 10,000 episodes of simulated patient trajectories
- Epsilon-greedy exploration (ε=0.1)
- Learning rate α=0.1, discount factor γ=0.95
- Converged to 263 unique states, final average reward 0.719

### Model Performance

#### Risk Predictor (Random Forest)
| Metric         | Validation Set | Test Set  |
|----------------|----------------|-----------|
| **ROC-AUC**    | 0.861          | **0.945** |
| **Accuracy**   | 82.6%          | **89.1%** |
| **Precision**  | 0.853          | 0.896     |
| **Recall**     | 0.829          | 0.872     |
| **F1 Score**   | 0.841          | **0.884** |

**Cross-Validation**: 81.5% ± 5.2% (5-fold stratified)

**Top 3 Risk Factors**:
1. **Thalassemia** (thal): 16.6% importance
2. **Major Vessels Colored** (ca): 14.3% importance
3. **Chest Pain Type** (cp): 12.3% importance

#### RL Agent (Q-Learning)
| Metric                | Value        |
|-----------------------|--------------|
| **Training Episodes** | 10,000       |
| **States Explored**   | 263          |
| **Final Avg Reward**  | 0.719        |
| **Convergence**       | Episode 6000 |

**Reward Progression**: 0.121 → 0.459 → 0.537 → 0.616 → 0.630 → 0.719

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

# Train models (if not already trained)
python -m ml.risk_predictor  # Trains risk predictor
python -m ml.rl_agent        # Trains RL agent

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

See [QUICKSTART.md](QUICKSTART.md) for detailed setup or [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for production deployment.

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

# Get RL recommendation
response = requests.post("http://localhost:8000/api/recommend", json=patient)
print(response.json())
# {
#   "action": 3,
#   "action_name": "Combination Therapy",
#   "description": "Medication plus supervised lifestyle program",
#   "expected_risk_reduction": 26.2,
#   ...
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
│   │   ├── risk_predictor.py    # Random Forest classifier
│   │   └── rl_agent.py          # Q-Learning agent
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

### Q: Why Q-Learning over Deep RL (DQN, PPO)?

**A**: Sample efficiency. With limited patient data, tabular Q-learning is more data-efficient than deep RL. It's also easier to debug and explain—critical for healthcare applications where we need to audit the agent's decision-making process.

### Q: How realistic is the RL simulation?

**A**: This is a **proof-of-concept**. The reward function and intervention effects are simplified approximations based on clinical literature. Real deployment would require:
- Clinical validation with medical professionals
- Longitudinal patient data to learn true intervention effects
- FDA/regulatory approval for medical decision support
- Integration with electronic health records (EHR)

### Q: Why 5 intervention actions?

**A**: Balance between granularity and learnability. More actions would require more data to learn effectively. These 5 capture the main clinical decision points: monitoring intensity, lifestyle vs. medication, single vs. combination therapy.

### Q: Why not use the full 13 features for RL state space?

**A**: Curse of dimensionality. With 13 features × 5 bins = 1.2 billion possible states, the Q-table would be too sparse to learn effectively. The 5 selected features (age, BP, cholesterol, max HR, ST depression) are the most clinically relevant and actionable.

---

## Future Work

### Short-Term Improvements
- [ ] **Hyperparameter tuning** with GridSearchCV for Random Forest
- [ ] **Deep RL exploration** (DQN, PPO) if more data becomes available
- [ ] **Multi-objective optimization** (Pareto frontier for cost vs. risk reduction)
- [ ] **A/B testing framework** to compare RL recommendations vs. clinical guidelines
- [ ] **Model explainability** with SHAP values for individual predictions

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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and contribution guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built for demonstrating ML expertise in preventive healthcare**
