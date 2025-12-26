# Documentation

This folder contains comprehensive documentation about the HealthGuard intervention system and risk reduction analysis.

## Files

### [SUMMARY.md](SUMMARY.md)
Quick overview of the risk reduction analysis, key findings, and validation results. **Start here** for a high-level understanding.

### [INTERVENTION_DEFINITIONS.md](INTERVENTION_DEFINITIONS.md)
Complete definitions of all 5 intervention levels (0-4), including:
- Specific treatments and medications
- Cost levels
- Intensity ratings
- When each intervention is appropriate

### [EXPECTED_RISK_REDUCTION_TABLE.md](EXPECTED_RISK_REDUCTION_TABLE.md)
Reference tables showing expected risk reduction values for different patient risk levels:
- Healthy patients (low risk)
- Moderate-risk patients
- High-risk patients with structural factors

### [RISK_REDUCTION_ANALYSIS.md](RISK_REDUCTION_ANALYSIS.md)
Detailed clinical analysis including:
- Why diminishing returns occur for healthy patients
- Why structural factors limit benefits for high-risk patients
- Cost-benefit analysis for intensive treatment
- Clinical interpretations and validation

## Key Findings

✅ **The system correctly implements:**
- Diminishing returns for already-healthy patients (no over-treatment)
- Progressive benefit for moderate-risk patients (best cost-benefit)
- Realistic limitations for high-risk patients (structural factors dominate)
- Risk monotonicity (interventions never increase risk)

✅ **Expected values for moderate-risk patient:**
- Combination Therapy: **8.0% risk reduction**
- Intensive Treatment: **12.7% risk reduction**

## Validation

All patterns are tested and validated in:
- `backend/tests/test_risk_reduction_patterns.py` - Automated tests (18/18 passing)
- `backend/tests/test_api_risk_reduction.py` - API integration tests
- `backend/tests/analyze_risk_reduction.py` - Analysis script to generate values

Run tests:
```bash
cd backend
pytest tests/test_risk_reduction_patterns.py -v
```
