"""Model report endpoints."""
import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from .. import pathing  # noqa: F401

from model_report import FEATURE_IMPORTANCE_IMG, PREDICTION_COMPARISON_IMG, get_model_performance


logger = logging.getLogger("waste_api")
router = APIRouter(prefix="/model", tags=["model"])


@router.get("/performance", response_model=Dict[str, Any])
async def model_performance():
    """Evaluation report, parsed tables, and Phase 2 metadata."""
    try:
        return get_model_performance()
    except Exception:
        logger.exception("Failed to load model performance")
        raise HTTPException(status_code=500, detail="Failed to load model performance")


@router.get("/feature-importance.png")
async def model_feature_importance_image():
    """Serve the feature importance chart image."""
    if not FEATURE_IMPORTANCE_IMG.exists():
        raise HTTPException(status_code=404, detail="Feature importance image not available")
    return FileResponse(FEATURE_IMPORTANCE_IMG, media_type="image/png")


@router.get("/prediction-comparison.png")
async def model_prediction_comparison_image():
    """Serve the prediction comparison chart image."""
    if not PREDICTION_COMPARISON_IMG.exists():
        raise HTTPException(status_code=404, detail="Prediction comparison image not available")
    return FileResponse(PREDICTION_COMPARISON_IMG, media_type="image/png")
