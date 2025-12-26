#!/usr/bin/env python
"""Test the new explanation feature"""
import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def moderate_risk():
    """Moderate risk patient data"""
    return {
        "age": 55,
        "sex": 1,
        "cp": 3,
        "trestbps": 150,
        "chol": 250,
        "fbs": 0,
        "restecg": 0,
        "thalach": 135,
        "exang": 0,
        "oldpeak": 1.5,
        "slope": 2,
        "ca": 1,
        "thal": 3,
    }


@pytest.fixture
def high_risk():
    """High risk patient data"""
    return {
        "age": 65,
        "sex": 1,
        "cp": 4,
        "trestbps": 170,
        "chol": 300,
        "fbs": 1,
        "restecg": 1,
        "thalach": 110,
        "exang": 1,
        "oldpeak": 3.0,
        "slope": 2,
        "ca": 2,
        "thal": 7,
    }


def test_moderate_risk_single_medication(client, moderate_risk):
    """Test explanation for moderate risk patient with single medication"""
    response = client.post("/api/simulate", json={"patient": moderate_risk, "action": 2})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"

    data = response.json()
    assert "current_risk" in data
    assert "expected_risk" in data
    assert "risk_reduction" in data
    assert "explanation" in data
    assert "feature_importance" in data
    assert "modifiable_features" in data

    # Verify explanation is a non-empty string
    assert isinstance(data["explanation"], str)
    assert len(data["explanation"]) > 0

    # Verify feature importance is a dict
    assert isinstance(data["feature_importance"], dict)
    assert len(data["feature_importance"]) > 0


def test_high_risk_single_medication(client, high_risk):
    """Test explanation for high risk patient with single medication"""
    response = client.post("/api/simulate", json={"patient": high_risk, "action": 2})
    assert response.status_code == 200

    data = response.json()
    assert "current_risk" in data
    assert "expected_risk" in data
    assert "risk_reduction" in data
    assert "explanation" in data
    assert "feature_importance" in data


def test_high_risk_intensive_treatment(client, high_risk):
    """Test explanation for high risk patient with intensive treatment"""
    response = client.post("/api/simulate", json={"patient": high_risk, "action": 4})
    assert response.status_code == 200

    data = response.json()
    assert "current_risk" in data
    assert "expected_risk" in data
    assert "risk_reduction" in data
    assert "explanation" in data
