# HealthGuard Project Structure

This document provides an overview of the HealthGuard project organization.

## Directory Structure

```
healthguard/
├── 📁 .devcontainer/          # VSCode DevContainer configuration
│   ├── Dockerfile
│   ├── devcontainer.json
│   └── docker-compose.yml
│
├── 📁 backend/                 # Python FastAPI backend
│   ├── api/                   # REST API endpoints
│   │   ├── main.py           # FastAPI app & routes
│   │   ├── models.py         # Pydantic schemas
│   │   └── config.py         # Configuration management
│   ├── ml/                    # Machine learning models
│   │   ├── risk_predictor.py # Random Forest classifier
│   │   └── rl_agent.py       # Q-Learning agent
│   ├── data/                  # Data processing pipeline
│   │   ├── load.py           # Data loading utilities
│   │   ├── raw/              # Raw UCI dataset
│   │   └── processed/        # Preprocessed datasets
│   ├── models/                # Trained model files (.pkl)
│   ├── tests/                 # Unit & integration tests
│   ├── requirements.txt       # Production dependencies
│   └── requirements-dev.txt   # Development dependencies
│
├── 📁 frontend/                # React + Vite frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── PatientForm.jsx
│   │   │   ├── RiskDisplay.jsx
│   │   │   └── RecommendationPanel.jsx
│   │   ├── api/
│   │   │   └── client.js     # Axios API client
│   │   ├── App.jsx           # Main application
│   │   └── main.jsx          # Entry point
│   ├── public/               # Static assets
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── 📁 docs/                    # Documentation
│   ├── DEPLOYMENT_GUIDE.md           # Production deployment
│   ├── SECURITY_SETUP.md             # Security configuration
│   ├── PHASE1_SECURITY_IMPLEMENTATION.md
│   ├── IMPLEMENTATION_PLAN.md        # Development plan
│   └── REFACTORING_ANALYSIS.md       # Future improvements
│
├── 📄 README.md                # Main project documentation
├── 📄 QUICKSTART.md            # Quick start guide
├── 📄 CONTRIBUTING.md          # Contribution guidelines
├── 📄 LICENSE                  # MIT License
│
├── 🐳 Dockerfile               # Docker container configuration
├── 🐳 docker-compose.yml       # Local development setup
├── 🐳 docker-compose.prod.yml  # Production setup
│
├── ☁️ render.yaml              # Render.com deployment config
├── ☁️ vercel.json              # Vercel deployment config
│
└── 🧪 test_staging.sh          # Automated testing script
```

## Documentation Guide

### For Getting Started
- **[README.md](../README.md)** - Start here! Complete project overview
- **[QUICKSTART.md](../QUICKSTART.md)** - Get running in 5 minutes

### For Development
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - How to contribute
- **[docs/IMPLEMENTATION_PLAN.md](../docs/IMPLEMENTATION_PLAN.md)** - Development plan
- **[docs/REFACTORING_ANALYSIS.md](../docs/REFACTORING_ANALYSIS.md)** - Future improvements

### For Deployment
- **[docs/DEPLOYMENT_GUIDE.md](../docs/DEPLOYMENT_GUIDE.md)** - Production deployment
- **[docs/SECURITY_SETUP.md](../docs/SECURITY_SETUP.md)** - Security configuration

## Key Files

### Configuration Files
- **`.env`** files - Environment variables (not in git)
- **`render.yaml`** - Backend deployment configuration
- **`vercel.json`** - Frontend deployment configuration
- **`vite.config.js`** - Frontend build configuration

### Entry Points
- **Backend**: `backend/api/main.py`
- **Frontend**: `frontend/src/main.jsx`

### Model Files
- **`backend/models/risk_predictor.pkl`** - Trained Random Forest model
- **`backend/models/intervention_agent.pkl`** - Trained Q-Learning agent
- **`backend/data/processed/scaler.pkl`** - Feature scaler

## Tech Stack

### Backend
- **Framework**: FastAPI 0.109
- **Language**: Python 3.11+
- **ML Libraries**: scikit-learn, numpy, pandas
- **API**: REST with Pydantic validation
- **Security**: API key auth, CORS, rate limiting

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite 5
- **UI**: Tailwind CSS, Victory Charts
- **State**: React Hooks
- **HTTP Client**: Axios

### DevOps
- **Containerization**: Docker
- **CI/CD**: GitHub Actions (planned)
- **Backend Hosting**: Render.com
- **Frontend Hosting**: Vercel
- **Development**: VSCode DevContainer

## Environment Files

```
.env                    # Active environment (not in git)
.env.example           # Template with example values
.env.staging           # Staging environment template
.env.production        # Production environment template
```

## Testing

```bash
# Backend tests
cd backend
pytest                          # Run all tests
pytest --cov                    # With coverage
pytest tests/test_api.py        # Specific test file

# Frontend tests
cd frontend
npm test                        # Run tests
npm run test:coverage           # With coverage
```

## Common Commands

```bash
# Development
cd backend && python -m uvicorn api.main:app --reload  # Backend
cd frontend && npm run dev                              # Frontend

# Testing
./test_staging.sh                                       # Integration tests

# Deployment
git push origin main                                    # Auto-deploy via CI/CD

# Docker
docker-compose up                                       # Local development
docker-compose -f docker-compose.prod.yml up           # Production
```

## Port Configuration

- **Backend API**: `8000`
- **Frontend Dev**: `5173` (Vite default)
- **Frontend Prod**: `80` (via reverse proxy)

## Git Workflow

1. Clone repository
2. Create feature branch
3. Make changes
4. Run tests
5. Commit with descriptive message
6. Push to GitHub
7. Create pull request
8. Merge after review

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.
