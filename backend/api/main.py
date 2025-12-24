"""
FastAPI Backend for HealthGuard

This module provides REST API endpoints for cardiovascular disease risk
prediction and intervention recommendation using ML models.
"""

import logging
from pathlib import Path
from typing import Dict
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import joblib

from api.models import (
    PatientInput,
    RiskPrediction,
    InterventionRecommendation,
    SimulationRequest,
    HealthStatus,
    ErrorResponse,
    HealthCheckResponse
)
from api.config import get_settings, Settings
from api.auth import verify_api_key
from api.rate_limit import RateLimitMiddleware
from ml.risk_predictor import RiskPredictor
from ml.rl_agent import InterventionAgent

# Global model instances
risk_predictor: RiskPredictor = None
intervention_agent: InterventionAgent = None
scaler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI.
    Loads ML models on startup and cleans up on shutdown.
    """
    global risk_predictor, intervention_agent, scaler

    settings = get_settings()

    # Configure logging based on settings
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=settings.log_format
    )
    logger = logging.getLogger(__name__)

    logger.info(f"Starting HealthGuard API in {settings.environment} mode...")

    # Load models
    try:
        # Load risk predictor
        if settings.risk_predictor_path.exists():
            risk_predictor = RiskPredictor()
            risk_predictor.load(settings.risk_predictor_path)
            logger.info(f"Loaded risk predictor model from {settings.risk_predictor_path}")
        else:
            logger.warning(f"Risk predictor not found at {settings.risk_predictor_path}")

        # Load intervention agent
        if settings.intervention_agent_path.exists():
            intervention_agent = InterventionAgent()
            intervention_agent.load(settings.intervention_agent_path)
            logger.info(f"Loaded intervention agent from {settings.intervention_agent_path}")
        else:
            logger.warning(f"Intervention agent not found at {settings.intervention_agent_path}")

        # Load scaler
        if settings.scaler_path.exists():
            scaler = joblib.load(settings.scaler_path)
            logger.info(f"Loaded StandardScaler from {settings.scaler_path}")
        else:
            logger.warning(f"Scaler not found at {settings.scaler_path}")

        # Log security configuration
        if settings.api_key_enabled:
            logger.info(f"API key authentication: ENABLED ({len(settings.api_keys_list)} keys configured)")
        else:
            logger.warning("API key authentication: DISABLED (not recommended for production)")

        if settings.rate_limit_enabled:
            logger.info(f"Rate limiting: ENABLED ({settings.rate_limit_requests} requests/min)")
        else:
            logger.warning("Rate limiting: DISABLED")

        logger.info(f"CORS origins: {settings.cors_origins_list}")
        logger.info("HealthGuard API ready")

    except Exception as e:
        logger.error(f"Failed to load models: {str(e)}")
        raise

    yield

    # Cleanup
    logger.info("Shutting down HealthGuard API...")


# Initialize settings
settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan,
    debug=settings.debug
)

# Add rate limiting middleware (before CORS)
app.add_middleware(RateLimitMiddleware)

# Configure CORS for frontend with environment-based origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods.split(",") if settings.cors_allow_methods != "*" else ["*"],
    allow_headers=settings.cors_allow_headers.split(",") if settings.cors_allow_headers != "*" else ["*"],
)

# Initialize logger
logger = logging.getLogger(__name__)


def normalize_patient_data(patient: PatientInput) -> pd.DataFrame:
    """
    Convert patient input to normalized DataFrame for model inference.

    Args:
        patient: PatientInput model with patient data

    Returns:
        Normalized DataFrame ready for model prediction

    Raises:
        HTTPException: If scaler is not loaded
    """
    if scaler is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Data scaler not loaded"
        )

    # Convert to DataFrame
    patient_dict = patient.model_dump()
    patient_df = pd.DataFrame([patient_dict])

    # Normalize using the same scaler from training
    patient_normalized = pd.DataFrame(
        scaler.transform(patient_df),
        columns=patient_df.columns
    )

    return patient_normalized


@app.get("/", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint to verify API status and model availability.

    Returns:
        HealthCheckResponse with API status and loaded models
    """
    models_status = {
        "risk_predictor": risk_predictor is not None,
        "intervention_agent": intervention_agent is not None
    }

    return HealthCheckResponse(
        status="healthy" if all(models_status.values()) else "degraded",
        message="HealthGuard API is running",
        models_loaded=models_status
    )


@app.post("/api/predict", response_model=RiskPrediction, dependencies=[Depends(verify_api_key)])
async def predict_risk(patient: PatientInput):
    """
    Predict cardiovascular disease risk for a patient.

    This endpoint uses the trained Random Forest classifier to predict
    the probability of cardiovascular disease and returns a risk score
    with feature importance for interpretability.

    Args:
        patient: Patient clinical data (13 features)

    Returns:
        RiskPrediction with risk score, classification, and feature importance

    Raises:
        HTTPException: If model is not loaded or prediction fails
    """
    if risk_predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Risk predictor model not loaded"
        )

    try:
        # Normalize patient data
        patient_normalized = normalize_patient_data(patient)

        # Make prediction
        prediction = risk_predictor.predict(patient_normalized)

        logger.info(
            f"Prediction: {prediction['classification']} "
            f"({prediction['risk_score']:.1f}%)"
        )

        return RiskPrediction(**prediction)

    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@app.post("/api/recommend", response_model=InterventionRecommendation, dependencies=[Depends(verify_api_key)])
async def recommend_intervention(patient: PatientInput):
    """
    Get RL-based intervention recommendation for a patient.

    This endpoint uses the trained Q-learning agent to recommend the
    optimal intervention strategy considering risk reduction, cost,
    and quality of life.

    Args:
        patient: Patient clinical data (13 features)

    Returns:
        InterventionRecommendation with action, explanation, and expected outcomes

    Raises:
        HTTPException: If models are not loaded or recommendation fails
    """
    if risk_predictor is None or intervention_agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Models not loaded"
        )

    try:
        # Normalize patient data
        patient_normalized = normalize_patient_data(patient)

        # Get recommendation
        recommendation = intervention_agent.recommend(
            patient_normalized,
            risk_predictor
        )

        logger.info(
            f"Recommendation: {recommendation['action_name']} "
            f"(risk reduction: {recommendation['expected_risk_reduction']:.1f}%)"
        )

        return InterventionRecommendation(**recommendation)

    except Exception as e:
        logger.error(f"Recommendation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation failed: {str(e)}"
        )


@app.post("/api/simulate", response_model=HealthStatus, dependencies=[Depends(verify_api_key)])
async def simulate_intervention(request: SimulationRequest):
    """
    Simulate the effect of a specific intervention on patient metrics.

    Allows users to explore what-if scenarios by simulating different
    intervention strategies and seeing the expected impact on health
    metrics and risk score.

    Args:
        request: SimulationRequest with patient data and action to simulate

    Returns:
        HealthStatus with current vs. optimized metrics and risk reduction

    Raises:
        HTTPException: If models are not loaded or simulation fails
    """
    if risk_predictor is None or intervention_agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Models not loaded"
        )

    try:
        # Convert patient data to DataFrame (raw values)
        patient_dict = request.patient.model_dump()
        patient_df = pd.DataFrame([patient_dict])

        # Normalize for model prediction
        patient_normalized = normalize_patient_data(request.patient)

        # Get current risk
        current_prediction = risk_predictor.predict(patient_normalized)
        current_risk = current_prediction['risk_score']

        # Apply intervention effects to RAW values (not normalized)
        modified_raw = patient_df.copy()

        if request.action == 0:  # Monitor Only
            # No change in metrics
            pass
        elif request.action == 1:  # Lifestyle Intervention
            # Modest improvements in modifiable factors
            modified_raw['trestbps'] *= 0.95  # 5% BP reduction
            modified_raw['chol'] *= 0.90  # 10% cholesterol reduction
            modified_raw['thalach'] *= 1.05  # 5% improved max HR
        elif request.action == 2:  # Single Medication
            # Target specific risk factors
            modified_raw['trestbps'] *= 0.90  # 10% BP reduction
            modified_raw['chol'] *= 0.85  # 15% cholesterol reduction
        elif request.action == 3:  # Combination Therapy
            # Synergistic effects
            modified_raw['trestbps'] *= 0.85  # 15% BP reduction
            modified_raw['chol'] *= 0.80  # 20% cholesterol reduction
            modified_raw['thalach'] *= 1.08  # 8% improved max HR
            modified_raw['oldpeak'] *= 0.90  # 10% reduced ST depression
        elif request.action == 4:  # Intensive Treatment
            # Maximum intervention effects
            modified_raw['trestbps'] *= 0.80  # 20% BP reduction
            modified_raw['chol'] *= 0.75  # 25% cholesterol reduction
            modified_raw['thalach'] *= 1.10  # 10% improved max HR
            modified_raw['oldpeak'] *= 0.80  # 20% reduced ST depression

        # Normalize modified data for prediction
        modified_normalized = pd.DataFrame(
            scaler.transform(modified_raw),
            columns=modified_raw.columns
        )

        # Get new risk from modified data
        new_prediction = risk_predictor.predict(modified_normalized)
        new_risk = new_prediction['risk_score']

        # Extract key metrics for comparison (RAW VALUES)
        current_metrics = {
            'trestbps': float(patient_df['trestbps'].iloc[0]),
            'chol': float(patient_df['chol'].iloc[0]),
            'thalach': float(patient_df['thalach'].iloc[0]),
            'oldpeak': float(patient_df['oldpeak'].iloc[0])
        }

        optimized_metrics = {
            'trestbps': float(modified_raw['trestbps'].iloc[0]),
            'chol': float(modified_raw['chol'].iloc[0]),
            'thalach': float(modified_raw['thalach'].iloc[0]),
            'oldpeak': float(modified_raw['oldpeak'].iloc[0])
        }

        result = HealthStatus(
            current_metrics=current_metrics,
            optimized_metrics=optimized_metrics,
            current_risk=current_risk,
            expected_risk=new_risk,
            risk_reduction=current_risk - new_risk
        )

        logger.info(
            f"Simulation: Action {request.action}, "
            f"Risk {current_risk:.1f}% → {new_risk:.1f}%"
        )

        return result

    except Exception as e:
        logger.error(f"Simulation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation failed: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.

    Returns:
        JSONResponse with error details
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
