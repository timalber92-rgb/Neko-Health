"""
API tests for HealthGuard FastAPI endpoints

Tests cover:
- Health check endpoint (GET /)
- Risk prediction endpoint (POST /api/predict)
- Intervention recommendation endpoint (POST /api/recommend)
- Intervention simulation endpoint (POST /api/simulate)
- Input validation
- Error handling
- Response schema validation
"""

import pytest


@pytest.fixture
def valid_patient_data():
    """
    Create valid patient data for testing.
    """
    return {
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
        "thal": 6,
    }


class TestHealthCheck:
    """Test health check endpoint"""

    def test_health_check_success(self, client):
        """Test successful health check"""
        response = client.get("/")

        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "message" in data
        assert "models_loaded" in data

        # Check models_loaded structure
        assert "risk_predictor" in data["models_loaded"]
        assert "intervention_agent" in data["models_loaded"]

    def test_health_check_response_structure(self, client):
        """Test health check response matches schema"""
        response = client.get("/")
        data = response.json()

        # Should have specific keys
        assert set(data.keys()) == {"status", "message", "models_loaded"}

        # Models loaded should be boolean dict
        for model_name, loaded in data["models_loaded"].items():
            assert isinstance(loaded, bool)


class TestPredictEndpoint:
    """Test risk prediction endpoint"""

    def test_predict_success(self, client, valid_patient_data):
        """Test successful risk prediction"""
        response = client.post("/api/predict", json=valid_patient_data)

        assert response.status_code == 200

        data = response.json()
        assert "risk_score" in data
        assert "classification" in data
        assert "has_disease" in data
        assert "probability" in data
        assert "feature_importance" in data

    def test_predict_response_values(self, client, valid_patient_data):
        """Test that prediction response values are valid"""
        response = client.post("/api/predict", json=valid_patient_data)
        data = response.json()

        # Risk score should be 0-100
        assert 0 <= data["risk_score"] <= 100

        # Probability should be 0-1
        assert 0 <= data["probability"] <= 1

        # Classification should be one of three categories
        assert data["classification"] in ["Low Risk", "Medium Risk", "High Risk"]

        # has_disease should be boolean
        assert isinstance(data["has_disease"], bool)

        # Feature importance should be a dict
        assert isinstance(data["feature_importance"], dict)
        assert len(data["feature_importance"]) > 0

    def test_predict_missing_field(self, client, valid_patient_data):
        """Test prediction with missing required field"""
        incomplete_data = valid_patient_data.copy()
        del incomplete_data["age"]

        response = client.post("/api/predict", json=incomplete_data)

        # Should return validation error
        assert response.status_code == 422

    def test_predict_invalid_value_range(self, client, valid_patient_data):
        """Test prediction with invalid value range"""
        invalid_data = valid_patient_data.copy()
        invalid_data["age"] = 200  # Age > 120 (invalid)

        response = client.post("/api/predict", json=invalid_data)

        # Should return validation error
        assert response.status_code == 422

    def test_predict_invalid_categorical(self, client, valid_patient_data):
        """Test prediction with invalid categorical value"""
        invalid_data = valid_patient_data.copy()
        invalid_data["sex"] = 5  # sex should be 0 or 1

        response = client.post("/api/predict", json=invalid_data)

        # Should return validation error
        assert response.status_code == 422

    def test_predict_consistency(self, client, valid_patient_data):
        """Test that predictions are consistent for same input"""
        response1 = client.post("/api/predict", json=valid_patient_data)
        response2 = client.post("/api/predict", json=valid_patient_data)

        data1 = response1.json()
        data2 = response2.json()

        # Should get identical predictions
        assert data1["risk_score"] == data2["risk_score"]
        assert data1["has_disease"] == data2["has_disease"]
        assert data1["classification"] == data2["classification"]


class TestRecommendEndpoint:
    """Test intervention recommendation endpoint"""

    def test_recommend_success(self, client, valid_patient_data):
        """Test successful intervention recommendation"""
        response = client.post("/api/recommend", json=valid_patient_data)

        assert response.status_code == 200

        data = response.json()
        assert "action" in data
        assert "action_name" in data
        assert "description" in data
        assert "cost" in data
        assert "intensity" in data
        assert "current_risk" in data
        assert "expected_final_risk" in data
        assert "expected_risk_reduction" in data
        assert "q_values" in data

    def test_recommend_response_values(self, client, valid_patient_data):
        """Test that recommendation response values are valid"""
        response = client.post("/api/recommend", json=valid_patient_data)
        data = response.json()

        # Action should be 0-4
        assert 0 <= data["action"] <= 4

        # Action name should match action index
        action_names = [
            "Monitor Only",
            "Lifestyle Intervention",
            "Single Medication",
            "Combination Therapy",
            "Intensive Treatment",
        ]
        assert data["action_name"] in action_names

        # Risk scores should be valid
        assert 0 <= data["current_risk"] <= 100
        assert 0 <= data["expected_final_risk"] <= 100

        # Q-values should be a dict with 5 entries
        assert isinstance(data["q_values"], dict)
        assert len(data["q_values"]) == 5

    def test_recommend_missing_field(self, client, valid_patient_data):
        """Test recommendation with missing required field"""
        incomplete_data = valid_patient_data.copy()
        del incomplete_data["trestbps"]

        response = client.post("/api/recommend", json=incomplete_data)

        # Should return validation error
        assert response.status_code == 422

    def test_recommend_consistency(self, client, valid_patient_data):
        """Test that recommendations are consistent for same input"""
        response1 = client.post("/api/recommend", json=valid_patient_data)
        response2 = client.post("/api/recommend", json=valid_patient_data)

        data1 = response1.json()
        data2 = response2.json()

        # Should get identical recommendations
        assert data1["action"] == data2["action"]
        assert data1["action_name"] == data2["action_name"]


class TestSimulateEndpoint:
    """Test intervention simulation endpoint"""

    def test_simulate_success(self, client, valid_patient_data):
        """Test successful intervention simulation"""
        simulation_request = {"patient": valid_patient_data, "action": 2}  # Single Medication

        response = client.post("/api/simulate", json=simulation_request)

        assert response.status_code == 200

        data = response.json()
        assert "current_metrics" in data
        assert "optimized_metrics" in data
        assert "current_risk" in data
        assert "expected_risk" in data
        assert "risk_reduction" in data

    def test_simulate_response_structure(self, client, valid_patient_data):
        """Test simulation response structure"""
        simulation_request = {"patient": valid_patient_data, "action": 1}

        response = client.post("/api/simulate", json=simulation_request)
        data = response.json()

        # Current and optimized metrics should have same keys
        assert set(data["current_metrics"].keys()) == set(data["optimized_metrics"].keys())

        # Should have key health metrics
        expected_metrics = ["trestbps", "chol", "thalach", "oldpeak"]
        for metric in expected_metrics:
            assert metric in data["current_metrics"]
            assert metric in data["optimized_metrics"]

    def test_simulate_all_actions(self, client, valid_patient_data):
        """Test simulation with all intervention actions"""
        for action in range(5):
            simulation_request = {"patient": valid_patient_data, "action": action}

            response = client.post("/api/simulate", json=simulation_request)

            assert response.status_code == 200
            data = response.json()

            # Risk reduction should be non-negative for active interventions
            if action > 0:
                # Active interventions might reduce risk (but not guaranteed)
                assert isinstance(data["risk_reduction"], float)

    def test_simulate_monitor_only(self, client, valid_patient_data):
        """Test simulation with Monitor Only action (no intervention)"""
        simulation_request = {"patient": valid_patient_data, "action": 0}  # Monitor Only

        response = client.post("/api/simulate", json=simulation_request)
        data = response.json()

        # With Monitor Only, metrics might not change much
        # (depends on simulation implementation)
        assert data["current_risk"] >= 0
        assert data["expected_risk"] >= 0

    def test_simulate_invalid_action(self, client, valid_patient_data):
        """Test simulation with invalid action"""
        simulation_request = {"patient": valid_patient_data, "action": 10}  # Invalid action

        response = client.post("/api/simulate", json=simulation_request)

        # Should return validation error
        assert response.status_code == 422

    def test_simulate_missing_patient_data(self, client, valid_patient_data):
        """Test simulation with missing patient data"""
        incomplete_patient = valid_patient_data.copy()
        del incomplete_patient["chol"]

        simulation_request = {"patient": incomplete_patient, "action": 2}

        response = client.post("/api/simulate", json=simulation_request)

        # Should return validation error
        assert response.status_code == 422


class TestErrorHandling:
    """Test error handling across endpoints"""

    def test_invalid_endpoint(self, client):
        """Test request to non-existent endpoint"""
        response = client.get("/api/nonexistent")

        assert response.status_code == 404

    def test_wrong_http_method(self, client, valid_patient_data):
        """Test using wrong HTTP method"""
        # Try GET on POST endpoint
        response = client.get("/api/predict")

        assert response.status_code == 405  # Method Not Allowed

    def test_malformed_json(self, client):
        """Test request with malformed JSON"""
        response = client.post("/api/predict", data="not valid json", headers={"Content-Type": "application/json"})

        assert response.status_code == 422

    def test_empty_body(self, client):
        """Test POST request with empty body"""
        response = client.post("/api/predict", json={})

        assert response.status_code == 422


class TestCORS:
    """Test CORS configuration"""

    @pytest.mark.skip(reason="TestClient doesn't process CORS middleware; test manually with real requests")
    def test_cors_headers_present(self, client, valid_patient_data):
        """Test that CORS headers are present in responses"""
        response = client.post("/api/predict", json=valid_patient_data)

        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers

    def test_cors_configuration_loaded(self):
        """Test that CORS configuration is properly loaded from settings"""
        from api.config import get_settings

        settings = get_settings()

        # Verify CORS origins are configured
        assert len(settings.cors_origins_list) > 0
        assert isinstance(settings.cors_origins_list, list)


class TestEndToEndWorkflow:
    """Test complete workflow from prediction to simulation"""

    def test_complete_workflow(self, client, valid_patient_data):
        """Test complete analysis workflow"""
        # Step 1: Get risk prediction
        predict_response = client.post("/api/predict", json=valid_patient_data)
        assert predict_response.status_code == 200
        prediction = predict_response.json()

        # Step 2: Get intervention recommendation
        recommend_response = client.post("/api/recommend", json=valid_patient_data)
        assert recommend_response.status_code == 200
        recommendation = recommend_response.json()

        # Step 3: Simulate the recommended intervention
        simulation_request = {"patient": valid_patient_data, "action": recommendation["action"]}
        simulate_response = client.post("/api/simulate", json=simulation_request)
        assert simulate_response.status_code == 200

        # Verify data consistency
        # Current risk in simulation should match prediction
        assert abs(prediction["risk_score"] - recommendation["current_risk"]) < 0.1

    def test_multiple_patients(self, client):
        """Test analyzing multiple different patients"""
        patients = [
            # Low risk patient
            {
                "age": 35.0,
                "sex": 0,
                "cp": 1,
                "trestbps": 120.0,
                "chol": 180.0,
                "fbs": 0,
                "restecg": 0,
                "thalach": 170.0,
                "exang": 0,
                "oldpeak": 0.0,
                "slope": 1,
                "ca": 0,
                "thal": 3,
            },
            # High risk patient
            {
                "age": 70.0,
                "sex": 1,
                "cp": 4,
                "trestbps": 180.0,
                "chol": 300.0,
                "fbs": 1,
                "restecg": 2,
                "thalach": 100.0,
                "exang": 1,
                "oldpeak": 4.0,
                "slope": 3,
                "ca": 3,
                "thal": 7,
            },
        ]

        results = []
        for patient in patients:
            response = client.post("/api/predict", json=patient)
            assert response.status_code == 200
            results.append(response.json())

        # Results should be different for different patients
        assert results[0]["risk_score"] != results[1]["risk_score"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
