# Tests

Comprehensive test suite for the HealthGuard backend.

## Test Structure

- `test_*.py` - Test modules
- `conftest.py` - Pytest fixtures and configuration
- `fixtures/` - Test fixtures and expected values

## Running Tests

Run all tests:
```bash
cd backend
pytest
```

Run specific test categories:
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Exclude slow tests
pytest -m "not slow"
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html --cov-report=term
```

## Test Categories

### Unit Tests
- `test_risk_predictor.py` - Risk prediction model tests
- `test_guideline_recommender.py` - Recommendation logic tests
- `test_security.py` - Security and authentication tests

### Integration Tests
- `test_api.py` - API endpoint tests
- `test_integration.py` - Full workflow integration tests
- `test_end_to_end_scenarios.py` - End-to-end scenario tests

### Specific Feature Tests
- `test_interventions.py` - Intervention application tests
- `test_intervention_simulation.py` - Intervention simulation tests
- `test_explanations.py` - SHAP explanation tests
- `test_risk_reduction_patterns.py` - Risk reduction pattern tests

## Test Fixtures

Test fixtures are defined in `conftest.py` and `fixtures/`:
- Sample patient data
- Expected risk reduction values
- Mock API clients

## Coverage

Current test coverage reports are available in `htmlcov/` after running tests with `--cov-report=html`.
