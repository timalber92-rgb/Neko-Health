# Intervention System Guide

Complete guide to the intervention recommendation system in HealthGuard.

## Overview

HealthGuard uses a **guideline-based recommendation system** following ACC/AHA cardiovascular disease prevention guidelines. The system provides risk-stratified treatment recommendations with detailed clinical rationale.

## Table of Contents

- [Intervention Levels](#intervention-levels)
- [Risk Stratification](#risk-stratification)
- [Risk Factor Analysis](#risk-factor-analysis)
- [Expected Outcomes](#expected-outcomes)
- [Clinical Validation](#clinical-validation)

---

## Intervention Levels

### 1. Monitor Only
**Risk Level**: < 15%
**Description**: Quarterly checkups with basic monitoring

**Components**:
- Blood pressure checks every 3 months
- Cholesterol panel annually
- Lifestyle counseling
- No active pharmacological treatment

**Expected Effects**:
- Blood pressure: No significant change
- Cholesterol: No significant change
- Risk reduction: 0-2%

**Appropriate For**:
- Healthy patients with optimal metrics
- Young patients without risk factors
- Patients with controlled conditions

---

### 2. Lifestyle Intervention
**Risk Level**: 15-30%
**Description**: Supervised diet and exercise program

**Components**:
- **Diet**: Mediterranean diet, DASH principles
  - Reduce sodium to <2,300 mg/day
  - Increase fruits, vegetables, whole grains
  - Limit saturated fat to <7% of calories
- **Exercise**: 150 minutes/week moderate activity
  - 30 minutes, 5 days/week
  - Aerobic exercise (walking, cycling, swimming)
- **Monitoring**: Monthly checkups for 6 months

**Expected Effects**:
- Blood pressure: -5 to -10 mmHg reduction
- Cholesterol: -10 to -15 mg/dL reduction
- Weight loss: 5-10% body weight
- Risk reduction: 5-10%

**Evidence Base**:
- DASH diet reduces BP by 5-11 mmHg (NEJM 2001)
- Exercise reduces CVD risk by 20-30% (Circulation 2015)

---

### 3. Single Medication
**Risk Level**: 30-50%
**Description**: Statin OR beta-blocker monotherapy

**Medication Options**:
- **Statin** (primary): Atorvastatin 10-20mg daily
  - Targets cholesterol ≥200 mg/dL
  - Expected LDL reduction: 30-40%
- **Beta-blocker**: Metoprolol 50-100mg daily
  - Targets BP ≥140/90 mmHg
  - Expected BP reduction: 10-15 mmHg
- **ACE Inhibitor**: Lisinopril 10-20mg daily
  - Alternative for BP control
  - Expected BP reduction: 10-12 mmHg

**Expected Effects**:
- Blood pressure: -10 to -15 mmHg (if beta-blocker)
- Cholesterol: -30 to -40 mg/dL (if statin)
- Risk reduction: 10-15%

**Monitoring**:
- Liver function tests (for statins)
- Blood pressure monitoring
- Lipid panel at 6 weeks

---

### 4. Combination Therapy
**Risk Level**: 50-70%
**Description**: Medication + supervised lifestyle program

**Components**:
- **Medications**: Statin + Beta-blocker OR ACE inhibitor
  - Addresses multiple risk factors simultaneously
  - Synergistic effects on BP and lipids
- **Lifestyle**: Same as Intervention #2
  - Diet modification
  - Exercise program
  - Weight management

**Expected Effects**:
- Blood pressure: -15 to -20 mmHg
- Cholesterol: -40 to -50 mg/dL
- Risk reduction: 15-20%

**Advantages**:
- Targets multiple pathways
- Greater risk reduction than monotherapy
- Evidence-based in high-risk patients

---

### 5. Intensive Treatment
**Risk Level**: ≥ 70%
**Description**: Multiple medications + intensive lifestyle modification

**Components**:
- **Medications** (multi-drug regimen):
  - High-dose statin (Atorvastatin 40-80mg)
  - Beta-blocker (Metoprolol 100-200mg)
  - ACE inhibitor (Lisinopril 20-40mg)
  - Aspirin 81mg (if no contraindications)
  - Consider ezetimibe if LDL goal not met
- **Intensive Lifestyle**:
  - Registered dietitian consultation
  - Cardiac rehabilitation program
  - Weekly monitoring for 3 months
  - Smoking cessation (if applicable)
  - Stress management

**Expected Effects**:
- Blood pressure: -20 to -30 mmHg
- Cholesterol: -50 to -70 mg/dL
- Risk reduction: 20-30%

**Monitoring**:
- Weekly BP checks initially
- Monthly labs (liver, kidney function)
- Side effect monitoring (muscle pain, fatigue)
- Medication adherence counseling

**Escalation Criteria**:
- Very high baseline risk (≥70%)
- Multiple severe risk factors
- Prior cardiovascular events
- Diabetes with complications

---

## Risk Stratification

The system uses risk-based treatment escalation:

| Risk Score | Risk Tier        | Recommended Action     |
|-----------|------------------|------------------------|
| < 15%     | Low              | Monitor Only           |
| 15-30%    | Moderate         | Lifestyle Intervention |
| 30-50%    | High             | Single Medication      |
| 50-70%    | Very High        | Combination Therapy    |
| ≥ 70%     | Critical         | Intensive Treatment    |

### Escalation Rules

Treatment may be escalated based on severe risk factors:

**Severe Risk Factors** (auto-escalate):
- Systolic BP ≥ 160 mmHg
- Total cholesterol ≥ 280 mg/dL
- ST depression ≥ 2.0 mm
- 3+ major vessels with disease
- Reversible defect on stress test

**Multiple Moderate Factors** (consider escalation):
- 2+ factors in borderline high range
- Young patient (<50) with elevated risk
- Strong family history + risk factors

---

## Risk Factor Analysis

The system identifies and categorizes risk factors:

### Severe Risk Factors
- **Hypertension**: BP ≥ 160 mmHg
- **Severe Hyperlipidemia**: Cholesterol ≥ 280 mg/dL
- **Significant ST Depression**: ≥ 2.0 mm
- **Multi-vessel Disease**: ≥ 3 major vessels
- **Cardiac Abnormality**: Reversible defect

### Moderate Risk Factors
- **Elevated BP**: 140-159 mmHg
- **High Cholesterol**: 240-279 mg/dL
- **Moderate ST Depression**: 1.0-1.9 mm
- **Vessel Disease**: 1-2 major vessels
- **Exercise Angina**: Present

### Risk Factor Reporting

Each recommendation includes:
```json
{
  "severe_count": 2,
  "moderate_count": 1,
  "details": [
    "severe hypertension (BP: 165 mmHg)",
    "high cholesterol (252 mg/dL)",
    "1 diseased vessel"
  ]
}
```

---

## Expected Outcomes

### Risk Reduction by Intervention

| Intervention          | Expected Reduction | Clinical Evidence              |
|----------------------|--------------------|---------------------------------|
| Monitor Only         | 0-2%               | Natural variation              |
| Lifestyle            | 5-10%              | DASH, Mediterranean diet trials|
| Single Medication    | 10-15%             | Statin trials (4S, WOSCOPS)    |
| Combination Therapy  | 15-20%             | ASCOT-LLA, HOPE                |
| Intensive Treatment  | 20-30%             | PROVE-IT, TNT                  |

### Time Course

- **Initial effects**: 4-6 weeks (medications)
- **Full benefit**: 3-6 months (lifestyle + medications)
- **Long-term**: Sustained over years with adherence

### Diminishing Returns

- **Healthy patients**: Minimal benefit from intensive treatment
- **High-risk patients**: Maximum absolute risk reduction
- **Cost-benefit**: Increases with baseline risk

---

## Clinical Validation

### Test Coverage

- 18 tests for risk reduction patterns
- 24 tests for guideline-based recommendations
- 73 end-to-end scenario tests
- 100% pass rate

### Validation Scenarios

1. **Monotonicity**: Risk increases with age, BP, cholesterol
2. **Patient Journeys**: Complete workflows for low/moderate/high risk
3. **Intervention Effects**: Verify expected metric changes
4. **Edge Cases**: Very young, very old, extreme values
5. **Consistency**: Same input → same recommendation

### Known Limitations

This is a **proof-of-concept system**. Real deployment requires:

- [ ] Clinical validation with medical professionals
- [ ] IRB approval for human subjects research
- [ ] FDA clearance for clinical decision support
- [ ] Integration with electronic health records
- [ ] Longitudinal outcome tracking
- [ ] Pharmacist review of medications
- [ ] Patient-specific contraindication checking

---

## References

### Guidelines
- 2019 ACC/AHA Guideline on Primary Prevention of CVD
- 2018 ACC/AHA/AACVPR/AAPA Guidelines on Cardiac Rehabilitation
- 2017 ACC/AHA/AAPA Guideline for High Blood Pressure

### Evidence Base
- DASH-Sodium Trial (NEJM 2001)
- Scandinavian Simvastatin Survival Study (Lancet 1994)
- ASCOT-LLA Trial (Lancet 2003)
- HOPE Study (NEJM 2000)
- Mediterranean Diet Studies (NEJM 2013)

---

## API Usage

```python
import requests

# Get recommendation
response = requests.post("http://localhost:8000/api/recommend", json={
    "age": 55, "sex": 1, "cp": 2, "trestbps": 145,
    "chol": 240, "fbs": 0, "restecg": 0, "thalach": 145,
    "exang": 0, "oldpeak": 1.5, "slope": 2, "ca": 1, "thal": 6
})

recommendation = response.json()
print(f"Action: {recommendation['action_name']}")
print(f"Risk Reduction: {recommendation['expected_risk_reduction']}%")
print(f"Rationale: {recommendation['rationale']}")
print(f"Risk Factors: {recommendation['risk_factors']}")
```

---

**For more details**:
- Implementation: `backend/ml/guideline_recommender.py`
- Tests: `backend/tests/test_risk_reduction_patterns.py`
- Analysis scripts: `backend/scripts/analyze_*.py`
