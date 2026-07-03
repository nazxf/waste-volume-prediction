"""ESP32 smart-bin telemetry endpoints."""
import logging
from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException

from .. import pathing  # noqa: F401
from ..config import Settings
from ..dependencies import require_iot_api_key
from ..schemas import BinReadingRequest, BinReadingResponse

from iot_storage import get_latest_bin_reading, get_latest_readings, save_bin_reading


logger = logging.getLogger("waste_api")


def create_router(settings: Settings) -> APIRouter:
    router = APIRouter(prefix="/iot", tags=["iot"])

    def require_key_dependency(x_api_key: str = Header(default=None)):
        return require_iot_api_key(settings, x_api_key)

    @router.post("/bin-reading", response_model=BinReadingResponse, dependencies=[Depends(require_key_dependency)])
    async def create_bin_reading(reading: BinReadingRequest):
        """Store one ESP32 smart-bin fill-level reading."""
        try:
            return save_bin_reading(
                bin_id=reading.bin_id,
                device_id=reading.device_id,
                fill_level=reading.fill_level,
            )
        except Exception:
            logger.exception("Failed to save bin reading")
            raise HTTPException(status_code=500, detail="Failed to save bin reading")

    @router.get("/bin-readings/latest", response_model=List[BinReadingResponse])
    async def latest_bin_readings(limit: int = 20):
        """Return newest ESP32 smart-bin readings across all bins."""
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="limit must be between 1 and 100")

        try:
            return get_latest_readings(limit=limit)
        except Exception:
            logger.exception("Failed to load bin readings")
            raise HTTPException(status_code=500, detail="Failed to load bin readings")

    @router.get("/bin/{bin_id}/latest", response_model=BinReadingResponse)
    async def latest_bin_reading(bin_id: str):
        """Return the newest ESP32 smart-bin reading for one bin."""
        try:
            reading = get_latest_bin_reading(bin_id=bin_id)
        except Exception:
            logger.exception("Failed to load bin reading for bin_id=%s", bin_id)
            raise HTTPException(status_code=500, detail="Failed to load bin reading")

        if reading is None:
            raise HTTPException(status_code=404, detail=f"No readings found for bin_id '{bin_id}'")

        return reading

    return router
