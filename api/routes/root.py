"""Root and health endpoints."""
from typing import Any, Dict

from fastapi import APIRouter

from ..dependencies import PredictorState
from ..schemas import HealthResponse
from ..services import run_health_checks


def create_router(state: PredictorState) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_model=Dict[str, Any])
    async def root():
        """Root endpoint with API information."""
        return {
            "api_name": "Waste Volume Prediction API",
            "version": "1.0.0",
            "description": "REST API for predicting waste volume using Machine Learning",
            "endpoints": {
                "health": "/health",
                "docs": "/docs",
                "daily_prediction": "/predict/daily",
                "weekly_prediction": "/predict/weekly",
                "monthly_prediction": "/predict/monthly",
                "anomaly_detection": "/detect/anomaly",
                "notifications": "/notifications/prediction-alert",
                "prediction_export": "/export/prediction",
                "iot_ingest": "/iot/bin-reading",
                "iot_latest": "/iot/bin-readings/latest",
                "iot_bin_latest": "/iot/bin/{bin_id}/latest",
            },
            "status": "operational" if state.loaded else "model_not_loaded",
        }

    @router.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint."""
        checks = run_health_checks(state)
        healthy = all([
            checks["model_loaded"],
            checks["dataset_available"],
            checks["sqlite_writable"],
            checks["pdf_export_available"],
        ])

        if healthy:
            return {
                "status": "healthy",
                "model_loaded": True,
                "message": "API is running and production dependencies are available",
                "checks": checks,
            }

        return {
            "status": "unhealthy",
            "model_loaded": state.loaded,
            "message": f"Health check failed: {state.error if not state.loaded else 'one or more runtime checks failed'}",
            "checks": checks,
        }

    return router
