# Documentation Index

Complete documentation for the HealthGuard cardiovascular disease risk prediction system.

## Quick Navigation

### 🚀 Getting Started
- **[Main README](../README.md)** - Project overview, features, and quick start
- **[Quick Start Guide](../QUICKSTART.md)** - Get running in 5 minutes
- **[Contributing Guidelines](../CONTRIBUTING.md)** - Development setup and workflow

### 🏥 Clinical & Medical
- **[INTERVENTIONS.md](INTERVENTIONS.md)** - ⭐ **NEW** Complete intervention system guide
  - All 5 intervention levels explained
  - Risk stratification logic
  - Expected outcomes and evidence base
  - Clinical validation details

### 🔧 Technical Documentation
- **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)** - Detailed architecture (17KB)
- **[REFACTORING_ANALYSIS.md](REFACTORING_ANALYSIS.md)** - Code quality analysis (9KB)
- **[CHANGELOG.md](CHANGELOG.md)** - Recent updates and migrations

### 🚢 Deployment & Operations
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Production deployment (Render/Vercel) (12KB)
- **[SECURITY_SETUP.md](SECURITY_SETUP.md)** - Security configuration (12KB)
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions (7KB)

### 📊 Risk & Intervention Analysis (Legacy - See INTERVENTIONS.md)
- **[SUMMARY.md](SUMMARY.md)** - Validation overview (7KB)
- **[EXPECTED_RISK_REDUCTION_TABLE.md](EXPECTED_RISK_REDUCTION_TABLE.md)** - Reference tables (2KB)
- **[RISK_REDUCTION_ANALYSIS.md](RISK_REDUCTION_ANALYSIS.md)** - Detailed analysis (12KB)
- **[INTERVENTION_DEFINITIONS.md](INTERVENTION_DEFINITIONS.md)** - Intervention specs (9KB)

---

## Documentation by Use Case

### "I want to understand how the system works"
1. Start: [Main README](../README.md) - Overview and features
2. Deep dive: [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Architecture details
3. Clinical: [INTERVENTIONS.md](INTERVENTIONS.md) - How recommendations work

### "I want to deploy to production"
1. Start: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Step-by-step deployment
2. Secure: [SECURITY_SETUP.md](SECURITY_SETUP.md) - Security configuration
3. Debug: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - If issues arise

### "I want to contribute code"
1. Start: [Contributing Guidelines](../CONTRIBUTING.md) - Development setup
2. Reference: [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Architecture
3. Improve: [REFACTORING_ANALYSIS.md](REFACTORING_ANALYSIS.md) - Known issues

### "I want to understand the ML models"
1. Overview: [Main README § Technical Approach](../README.md#technical-approach)
2. Code: [backend/ml/README.md](../backend/ml/README.md) - ML module docs
3. Training: [backend/scripts/train_model_with_scaling.py](../backend/scripts/train_model_with_scaling.py)

### "I want to validate the intervention system"
1. Guide: [INTERVENTIONS.md](INTERVENTIONS.md) - Complete system documentation
2. Tests: [backend/tests/test_risk_reduction_patterns.py](../backend/tests/test_risk_reduction_patterns.py)
3. Analysis: [backend/scripts/analyze_risk_reduction.py](../backend/scripts/analyze_risk_reduction.py)

---

## Recent Updates (December 2025)

### NEW: Consolidated Intervention Documentation
- Created **[INTERVENTIONS.md](INTERVENTIONS.md)** - single source of truth for interventions
- Combines content from 4 separate docs into one cohesive guide
- Includes clinical evidence, expected outcomes, and validation details

### Model Updates
- **Logistic Regression** now uses embedded StandardScaler
- Feature scaling applied automatically during prediction
- Improved performance: 93.9% ROC-AUC on test set
- Updated all docs to reflect current model (was Random Forest)

### Documentation Streamlining
- Main README reduced and updated
- Module-level READMEs enhanced
- Created this navigation guide

---

## File Sizes Reference

| File | Size | Purpose |
|------|------|---------|
| INTERVENTIONS.md | ~11KB | ⭐ **NEW** Complete intervention guide |
| IMPLEMENTATION_PLAN.md | 17KB | Detailed architecture |
| DEPLOYMENT_GUIDE.md | 12KB | Production deployment |
| SECURITY_SETUP.md | 12KB | Security setup |
| RISK_REDUCTION_ANALYSIS.md | 12KB | Detailed risk analysis (legacy) |
| REFACTORING_ANALYSIS.md | 9KB | Code quality analysis |
| INTERVENTION_DEFINITIONS.md | 9KB | Intervention specs (legacy) |
| SUMMARY.md | 7KB | Validation summary (legacy) |
| TROUBLESHOOTING.md | 7KB | Common issues |
| CHANGELOG.md | 4KB | Recent changes |
| EXPECTED_RISK_REDUCTION_TABLE.md | 2KB | Reference tables (legacy) |

**Total documentation**: ~120KB across 14 files

---

## Contributing to Documentation

When updating docs:
1. Update [INTERVENTIONS.md](INTERVENTIONS.md) for clinical/intervention changes
2. Update [Main README](../README.md) for high-level changes
3. Update [CHANGELOG.md](CHANGELOG.md) with date and description
4. Update this file if adding new documentation

**Documentation standards**:
- Use clear headings and table of contents
- Include code examples where applicable
- Link between related documents
- Keep technical accuracy paramount
- Update file size reference if adding large docs
