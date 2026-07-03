"""Shared dependency helpers and runtime service state."""
from dataclasses import dataclass
from typing import Any, Optional

from fastapi import Header, HTTPException

from . import pathing  # noqa: F401
from .config import Settings


MODEL_NOT_LOADED_DETAIL = "Model not loaded. Please train the model first by running: python src/train_model.py"


@dataclass
class PredictorState:
    predictor: Optional[Any]
    loaded: bool
    error: str = ""


def load_predictor_state() -> PredictorState:
    try:
        from predict import WasteVolumePredictor

        return PredictorState(predictor=WasteVolumePredictor(), loaded=True)
    except FileNotFoundError as exc:
        return PredictorState(predictor=None, loaded=False, error=str(exc))
    except Exception as exc:
        return PredictorState(predictor=None, loaded=False, error=f"Failed to load model: {exc}")


def get_predictor(state: PredictorState) -> Any:
    if not state.loaded or state.predictor is None:
        raise HTTPException(status_code=503, detail=MODEL_NOT_LOADED_DETAIL)
    return state.predictor


def require_iot_api_key(settings: Settings, x_api_key: Optional[str] = Header(default=None)) -> None:
    """Validate the X-API-Key header against IOT_API_KEY when configured."""
    if not settings.iot_api_key:
        return
    if x_api_key != settings.iot_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
