"""
Pydantic Models for HealthGuard API

This module defines the request/response schemas for the FastAPI backend.
All models use Pydantic for automatic validation and serialization.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PatientInput(BaseModel):
    """
    Request model for patient data input.

    Contains all 13 clinical features required for risk prediction.
    All fields are validated for appropriate ranges.
    """

    age: float = Field(..., ge=0, le=120, description="Age in years")
    sex: int = Field(..., ge=0, le=1, description="Sex (1 = male, 0 = female)")
    cp: int = Field(..., ge=1, le=4, description="Chest pain type (1-4)")
    trestbps: float = Field(..., ge=50, le=250, description="Resting blood pressure (mm Hg)")
    chol: float = Field(..., ge=100, le=600, description="Serum cholesterol (mg/dl)")
    fbs: int = Field(..., ge=0, le=1, description="Fasting blood sugar > 120 mg/dl (1 = true, 0 = false)")
    restecg: int = Field(..., ge=0, le=2, description="Resting ECG results (0-2)")
    thalach: float = Field(..., ge=50, le=250, description="Maximum heart rate achieved")
    exang: int = Field(..., ge=0, le=1, description="Exercise induced angina (1 = yes, 0 = no)")
    oldpeak: float = Field(..., ge=0, le=10, description="ST depression induced by exercise")
    slope: int = Field(..., ge=1, le=3, description="Slope of peak exercise ST segment (1-3)")
    ca: int = Field(..., ge=0, le=3, description="Number of major vessels colored by fluoroscopy (0-3)")
    thal: int = Field(..., ge=3, le=7, description="Thalassemia (3 = normal, 6 = fixed defect, 7 = reversible defect)")

    model_config = {
        "json_schema_extra": {
            "example": {
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
        }
    }


class RiskPrediction(BaseModel):
    """
    Response model for risk prediction.

    Contains the predicted risk score, classification, and feature importance
    to help interpret the model's decision.
    """

    risk_score: float = Field(..., description="Risk percentage (0-100%)")
    classification: str = Field(..., description="Risk category: 'Low Risk', 'Medium Risk', or 'High Risk'")
    has_disease: bool = Field(..., description="Binary prediction: True if disease predicted, False otherwise")
    probability: float = Field(..., description="Raw probability of disease (0-1)")
    feature_importance: Dict[str, float] = Field(..., description="Feature importance scores from Random Forest")

    model_config = {
        "json_schema_extra": {
            "example": {
                "risk_score": 78.5,
                "classification": "High Risk",
                "has_disease": True,
                "probability": 0.785,
                "feature_importance": {"thal": 0.166, "ca": 0.143, "cp": 0.123, "oldpeak": 0.108, "thalach": 0.091},
            }
        }
    }


class RiskFactorDetails(BaseModel):
    """Risk factor details for intervention recommendation."""

    severe_count: int = Field(..., description="Number of severe risk factors")
    moderate_count: int = Field(..., description="Number of moderate risk factors")
    details: List[str] = Field(..., description="List of specific risk factors identified")


class InterventionRecommendation(BaseModel):
    """
    Response model for guideline-based intervention recommendation.

    Contains the recommended action, explanation, and expected outcomes
    to guide clinical decision-making.
    """

    action: int = Field(..., ge=0, le=4, description="Recommended action index (0-4)")
    action_name: str = Field(..., description="Human-readable action name")
    description: str = Field(..., description="Detailed description of the intervention")
    cost: str = Field(..., description="Estimated cost level")
    intensity: str = Field(..., description="Treatment intensity level")
    current_risk: float = Field(..., description="Current risk score (%)")
    expected_final_risk: float = Field(..., description="Expected risk after intervention (%)")
    expected_risk_reduction: float = Field(..., description="Expected reduction in risk (%)")
    rationale: Optional[str] = Field(None, description="Clinical rationale for the recommendation")
    risk_factors: Optional[RiskFactorDetails] = Field(None, description="Identified risk factors")
    q_values: Optional[Dict[str, float]] = Field(None, description="Q-values for all actions (RL agent only)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "action": 3,
                "action_name": "Combination Therapy",
                "description": "Medication plus supervised lifestyle program",
                "cost": "High ($$$$)",
                "intensity": "High",
                "current_risk": 78.5,
                "expected_final_risk": 52.3,
                "expected_risk_reduction": 26.2,
                "rationale": "Patient has high cardiovascular disease risk (78.5%). Identified 1 severe and 2 moderate risk factor(s). Specific factors: severe hypertension (BP: 160 mmHg), high cholesterol (233 mg/dL), exercise-induced angina. Recommended intervention: Combination Therapy. Combination therapy (medication + lifestyle) is guideline-recommended for high risk.",
                "risk_factors": {
                    "severe_count": 1,
                    "moderate_count": 2,
                    "details": [
                        "severe hypertension (BP: 160 mmHg)",
                        "high cholesterol (233 mg/dL)",
                        "exercise-induced angina",
                    ],
                },
                "q_values": None,
            }
        }
    }


class SimulationRequest(BaseModel):
    """
    Request model for intervention simulation.

    Allows users to simulate the effect of a specific intervention
    on a patient's health metrics.
    """

    patient: PatientInput = Field(..., description="Patient clinical data")
    action: int = Field(..., ge=0, le=4, description="Intervention action to simulate (0-4)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "patient": {
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
                },
                "action": 3,
            }
        }
    }


class HealthStatus(BaseModel):
    """
    Response model for intervention simulation.

    Shows current vs. optimized health metrics and expected risk reduction.
    """

    current_metrics: Dict[str, float] = Field(..., description="Current patient health metrics")
    optimized_metrics: Dict[str, float] = Field(..., description="Expected metrics after intervention")
    current_risk: float = Field(..., description="Current risk score (%)")
    expected_risk: float = Field(..., description="Expected risk after intervention (%)")
    risk_reduction: float = Field(..., description="Expected risk reduction (%)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "current_metrics": {"trestbps": 145.0, "chol": 233.0, "thalach": 150.0, "oldpeak": 2.3},
                "optimized_metrics": {"trestbps": 123.3, "chol": 186.4, "thalach": 162.0, "oldpeak": 2.07},
                "current_risk": 78.5,
                "expected_risk": 52.3,
                "risk_reduction": 26.2,
            }
        }
    }


class ErrorResponse(BaseModel):
    """
    Response model for error messages.
    """

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

    model_config = {"json_schema_extra": {"example": {"error": "Prediction failed", "detail": "Model not loaded properly"}}}


class HealthCheckResponse(BaseModel):
    """
    Response model for health check endpoint.
    """

    status: str = Field(..., description="API status")
    message: str = Field(..., description="Status message")
    models_loaded: Dict[str, bool] = Field(..., description="Status of loaded ML models")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "message": "HealthGuard API is running",
                "models_loaded": {"risk_predictor": True, "intervention_agent": True},
            }
        }
    }
