"""
FastAPI Backend for HealthGuard

This module provides REST API endpoints for cardiovascular disease risk
prediction and intervention recommendation using ML models.
"""

import logging
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.auth import verify_api_key
from api.config import get_settings
from api.models import (
    HealthCheckResponse,
    HealthStatus,
    PatientInput,
    PersonalizedRecommendation,
    RiskPrediction,
    SimulationRequest,
)
from api.rate_limit import RateLimitMiddleware
from ml.intervention_utils import (
    apply_intervention_effects,
    ensure_risk_monotonicity,
    generate_intervention_explanation,
    get_modifiable_features,
)
from ml.recommendation_engine import InterventionRecommender
from ml.risk_predictor import RiskPredictor

# Global model instances
risk_predictor: RiskPredictor = None
# Scaler removed - Logistic Regression works with raw features


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI.
    Loads ML models on startup and cleans up on shutdown.
    """
    global risk_predictor

    settings = get_settings()

    # Configure logging based on settings
    logging.basicConfig(level=getattr(logging, settings.log_level.upper()), format=settings.log_format)
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

        # Intervention recommendations now use InterventionRecommender (no model loading required)
        logger.info("Using InterventionRecommender for personalized recommendations")

        # Scaler no longer needed - Logistic Regression works with raw features
        logger.info("Using raw features (no scaling needed for Logistic Regression)")

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
    debug=settings.debug,
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


def patient_to_dataframe(patient: PatientInput) -> pd.DataFrame:
    """
    Convert patient input to DataFrame for model inference.

    Args:
        patient: PatientInput model with patient data

    Returns:
        DataFrame with raw features ready for prediction (no scaling needed)
    """
    # Convert to DataFrame with raw values - Random Forest doesn't need scaling
    patient_dict = patient.model_dump()
    patient_df = pd.DataFrame([patient_dict])
    return patient_df


@app.get("/", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint to verify API status and model availability.

    Returns:
        HealthCheckResponse with API status and loaded models
    """
    models_status = {
        "risk_predictor": risk_predictor is not None,
        "recommendation_engine": True,  # InterventionRecommender is stateless, always available
    }

    return HealthCheckResponse(
        status="healthy" if all(models_status.values()) else "degraded",
        message="HealthGuard API is running",
        models_loaded=models_status,
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
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Risk predictor model not loaded")

    try:
        # Normalize patient data
        patient_normalized = patient_to_dataframe(patient)

        # Make prediction
        prediction = risk_predictor.predict(patient_normalized)

        logger.info("Prediction: %s (%.1f%%)", prediction["classification"], prediction["risk_score"])

        return RiskPrediction(**prediction)

    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Prediction failed: {str(e)}")


@app.post("/api/recommend", response_model=PersonalizedRecommendation, dependencies=[Depends(verify_api_key)])
async def recommend_intervention(patient: PatientInput):
    """
    Get personalized intervention recommendation for a patient.

    This endpoint provides intelligent, risk-stratified recommendations based on:
    - Patient's baseline cardiovascular risk level
    - Expected outcomes for each intervention option
    - Cost-benefit analysis
    - Clinical guidelines

    The recommendation engine analyzes all intervention options and provides:
    - Primary recommendation optimized for the patient's risk tier
    - Alternative recommendation for consideration
    - Complete comparison of all intervention options with expected outcomes

    Args:
        patient: Patient clinical data (13 features)

    Returns:
        PersonalizedRecommendation with primary recommendation, alternative,
        and detailed comparison of all intervention options

    Raises:
        HTTPException: If model is not loaded or recommendation fails
    """
    if risk_predictor is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Risk predictor model not loaded")

    try:
        # Convert patient data to DataFrame
        patient_df = patient_to_dataframe(patient)

        # Get baseline risk
        baseline_prediction = risk_predictor.predict(patient_df)
        baseline_risk = baseline_prediction["risk_score"]

        # Calculate outcomes for all intervention options
        intervention_results = {}
        for action_id in [1, 2, 3, 4]:
            # Apply intervention effects
            modified_df = apply_intervention_effects(patient_df.copy(), action_id)

            # Get new risk
            new_prediction = risk_predictor.predict(modified_df)
            new_risk = new_prediction["risk_score"]

            # Calculate reductions
            risk_reduction = baseline_risk - new_risk
            pct_reduction = (risk_reduction / baseline_risk * 100) if baseline_risk > 0 else 0

            intervention_results[action_id] = {
                "new_risk": new_risk,
                "risk_reduction": risk_reduction,
                "pct_reduction": pct_reduction,
            }

        # Get personalized recommendation
        recommendation = InterventionRecommender.recommend_intervention(
            baseline_risk=baseline_risk, intervention_results=intervention_results
        )

        logger.info(
            "Recommendation: %s (Baseline: %.1f%%, Tier: %s)",
            recommendation["recommendation_name"],
            baseline_risk,
            recommendation["risk_tier"],
        )

        return PersonalizedRecommendation(**recommendation)

    except Exception as e:
        logger.error(f"Recommendation failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Recommendation failed: {str(e)}")


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
    if risk_predictor is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Models not loaded")

    try:
        # Convert patient data to DataFrame (raw values - no scaling needed)
        patient_df = patient_to_dataframe(request.patient)

        # Get current risk
        current_prediction = risk_predictor.predict(patient_df)
        current_risk = current_prediction["risk_score"]

        # Apply intervention effects to raw values
        # Using smart intervention logic with bounds checking
        modified_df = apply_intervention_effects(patient_df.copy(), request.action)

        # Get new risk from modified data (no scaling needed)
        new_prediction = risk_predictor.predict(modified_df)
        new_risk = new_prediction["risk_score"]

        # Extract key metrics for comparison (RAW VALUES)
        current_metrics = {
            "trestbps": float(patient_df["trestbps"].iloc[0]),
            "chol": float(patient_df["chol"].iloc[0]),
            "thalach": float(patient_df["thalach"].iloc[0]),
            "oldpeak": float(patient_df["oldpeak"].iloc[0]),
        }

        optimized_metrics = {
            "trestbps": float(modified_df["trestbps"].iloc[0]),
            "chol": float(modified_df["chol"].iloc[0]),
            "thalach": float(modified_df["thalach"].iloc[0]),
            "oldpeak": float(modified_df["oldpeak"].iloc[0]),
        }

        # Apply risk monotonicity safeguard to prevent paradoxical risk increases
        final_risk, final_metrics = ensure_risk_monotonicity(
            current_risk, new_risk, current_metrics, optimized_metrics, request.action
        )

        # Calculate risk reduction
        risk_reduction = current_risk - final_risk

        # Get feature importance from the current prediction
        feature_importance = current_prediction.get("feature_importance", {})

        # Generate explanation for why risk changed (or didn't)
        explanation = generate_intervention_explanation(
            current_metrics, final_metrics, risk_reduction, feature_importance, request.action
        )

        # Get list of modifiable features
        modifiable_features = get_modifiable_features()

        result = HealthStatus(
            current_metrics=current_metrics,
            optimized_metrics=final_metrics,
            current_risk=current_risk,
            expected_risk=final_risk,
            risk_reduction=risk_reduction,
            explanation=explanation,
            feature_importance=feature_importance,
            modifiable_features=modifiable_features,
        )

        safe_action = str(request.action).replace("\r", "").replace("\n", "")
        logger.info("Simulation: Action %s, Risk %.1f%% → %.1f%%", safe_action, current_risk, final_risk)

        return result

    except Exception as e:
        logger.error(f"Simulation failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Simulation failed: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.

    Returns:
        JSONResponse with error details
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
