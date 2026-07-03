"""Dataset statistics endpoints."""
import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from .. import pathing  # noqa: F401

from dataset_stats import DatasetNotFoundError, get_analysis, get_overview


logger = logging.getLogger("waste_api")
router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview", response_model=Dict[str, Any])
async def stats_overview(trend_days: int = 90):
    """Headline dataset metrics and a recent waste-volume trend."""
    if trend_days < 1 or trend_days > 730:
        raise HTTPException(status_code=400, detail="trend_days must be between 1 and 730")
    try:
        return get_overview(trend_days=trend_days)
    except DatasetNotFoundError:
        raise HTTPException(status_code=503, detail="Dataset not available. Train the model first.")
    except Exception:
        logger.exception("Failed to build stats overview")
        raise HTTPException(status_code=500, detail="Failed to load dataset overview")


@router.get("/analysis", response_model=Dict[str, Any])
async def stats_analysis():
    """Distribution, weekday averages, monthly trend, and correlation matrix."""
    try:
        return get_analysis()
    except DatasetNotFoundError:
        raise HTTPException(status_code=503, detail="Dataset not available. Train the model first.")
    except Exception:
        logger.exception("Failed to build stats analysis")
        raise HTTPException(status_code=500, detail="Failed to load dataset analysis")
