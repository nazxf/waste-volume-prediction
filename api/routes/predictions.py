"""Prediction, anomaly, notification, and export endpoints."""
import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from .. import pathing  # noqa: F401
from ..dependencies import PredictorState, get_predictor
from ..schemas import (
    DailyPredictionResponse,
    ExportPredictionRequest,
    MonthlyPredictionResponse,
    NotificationRequest,
    PredictionInput,
    WeeklyPredictionResponse,
)
from ..services import build_daily_response, build_export_response, build_range_response

from notifications import send_prediction_notifications


logger = logging.getLogger("waste_api")


def create_router(state: PredictorState) -> APIRouter:
    router = APIRouter(tags=["predictions"])

    @router.post("/predict/daily", response_model=DailyPredictionResponse)
    async def predict_daily(input_data: PredictionInput):
        """Predict waste volume for a single day."""
        predictor = get_predictor(state)
        try:
            return build_daily_response(predictor, input_data)
        except Exception:
            logger.exception("Daily prediction failed")
            raise HTTPException(status_code=500, detail="Prediction failed")

    @router.post("/predict/weekly", response_model=WeeklyPredictionResponse)
    async def predict_weekly(input_data: PredictionInput):
        """Predict waste volume for 7 consecutive days."""
        predictor = get_predictor(state)
        try:
            return build_range_response(predictor, input_data, "weekly")
        except Exception:
            logger.exception("Weekly prediction failed")
            raise HTTPException(status_code=500, detail="Prediction failed")

    @router.post("/predict/monthly", response_model=MonthlyPredictionResponse)
    async def predict_monthly(input_data: PredictionInput):
        """Predict waste volume for 30 consecutive days."""
        predictor = get_predictor(state)
        try:
            return build_range_response(predictor, input_data, "monthly")
        except Exception:
            logger.exception("Monthly prediction failed")
            raise HTTPException(status_code=500, detail="Prediction failed")

    @router.post("/detect/anomaly", response_model=Dict[str, Any])
    async def detect_anomaly(input_data: PredictionInput):
        """Detect whether a prediction input is anomalous."""
        predictor = get_predictor(state)
        try:
            return predictor.detect_anomaly(input_data.model_dump())
        except Exception:
            logger.exception("Anomaly detection failed")
            raise HTTPException(status_code=500, detail="Anomaly detection failed")

    @router.post("/notifications/prediction-alert", response_model=Dict[str, Any])
    async def prediction_alert(request: NotificationRequest):
        """Send or preview prediction threshold notifications."""
        predictor = get_predictor(state)
        try:
            input_dict = request.model_dump()
            for key in ["threshold", "channels", "dry_run"]:
                input_dict.pop(key, None)

            prediction = predictor.predict_daily_with_details(input_dict)
            predicted_volume = prediction["predicted_waste_volume"]
            triggered = predicted_volume >= request.threshold

            if triggered:
                notification_results = send_prediction_notifications(
                    predicted_volume=predicted_volume,
                    threshold=request.threshold,
                    date=request.date,
                    fleet_recommendation=prediction["fleet_recommendation"],
                    channels=request.channels,
                    dry_run=request.dry_run,
                )
            else:
                notification_results = [{
                    "channel": "none",
                    "sent": False,
                    "dry_run": True,
                    "message": "Prediction is below threshold; no notification sent.",
                }]

            return {
                "triggered": triggered,
                "prediction": prediction,
                "notifications": notification_results,
            }
        except Exception:
            logger.exception("Notification workflow failed")
            raise HTTPException(status_code=500, detail="Notification workflow failed")

    @router.post("/export/prediction")
    async def export_prediction(request: ExportPredictionRequest):
        """Export daily, weekly, or monthly predictions to Excel or PDF."""
        predictor = get_predictor(state)
        try:
            return build_export_response(predictor, request)
        except Exception:
            logger.exception("Export failed")
            raise HTTPException(status_code=500, detail="Export failed")

    return router
