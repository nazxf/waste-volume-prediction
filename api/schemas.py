"""Pydantic request and response schemas."""
from datetime import datetime
from typing import Any, Dict, List, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PredictionInput(BaseModel):
    """Input schema for prediction."""

    date: str = Field(..., description="Date in YYYY-MM-DD format", json_schema_extra={"example": "2025-01-15"})
    temperature: float = Field(..., ge=24.0, le=35.0, description="Temperature in Celsius", json_schema_extra={"example": 30.5})
    rainfall: float = Field(..., ge=0.0, le=120.0, description="Rainfall in mm", json_schema_extra={"example": 5.0})
    humidity: float = Field(..., ge=55.0, le=95.0, description="Humidity percentage", json_schema_extra={"example": 75.0})
    holiday: int = Field(..., ge=0, le=1, description="Holiday flag (0=No, 1=Yes)", json_schema_extra={"example": 0})
    weekend: int = Field(..., ge=0, le=1, description="Weekend flag (0=No, 1=Yes)", json_schema_extra={"example": 0})
    population_density: float = Field(..., ge=3000.0, le=15000.0, description="Population density (people/km2)", json_schema_extra={"example": 9500.0})
    event_level: int = Field(..., ge=0, le=5, description="Event level (0-5)", json_schema_extra={"example": 1})

    @field_validator("date")
    @classmethod
    def validate_date(cls, value):
        """Validate date format."""
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")


class DailyPredictionResponse(BaseModel):
    """Response schema for daily prediction."""

    prediction_type: str = "daily"
    date: str
    predicted_waste_volume: float
    unit: str = "tons"
    confidence_interval: Dict[str, float]
    anomaly: Dict[str, Any]
    fleet_recommendation: Dict[str, Union[int, float]]


class WeeklyPredictionResponse(BaseModel):
    """Response schema for weekly prediction."""

    prediction_type: str = "weekly"
    start_date: str
    end_date: str
    total_volume: float
    average_daily: float
    unit: str = "tons"
    confidence_interval: Dict[str, float]
    daily_predictions: List[Dict]


class MonthlyPredictionResponse(BaseModel):
    """Response schema for monthly prediction."""

    prediction_type: str = "monthly"
    start_date: str
    end_date: str
    total_volume: float
    average_daily: float
    unit: str = "tons"
    confidence_interval: Dict[str, float]
    daily_predictions: List[Dict]


class HealthResponse(BaseModel):
    """Health check response."""

    model_config = ConfigDict(protected_namespaces=())

    status: str
    model_loaded: bool
    message: str
    checks: Dict[str, Any] = Field(default_factory=dict)


class NotificationRequest(PredictionInput):
    """Request schema for notification checks."""

    threshold: float = Field(..., ge=0.0, description="Alert threshold in tons", json_schema_extra={"example": 100.0})
    channels: List[str] = Field(default_factory=lambda: ["email"], description="Notification channels: email and/or sms")
    dry_run: bool = Field(default=True, description="Return notification preview without sending")

    @field_validator("channels")
    @classmethod
    def validate_channels(cls, value):
        """Reject unsupported notification channels instead of silently ignoring them."""
        allowed_channels = {"email", "sms"}
        normalized = [channel.strip().lower() for channel in value]
        invalid_channels = sorted(set(normalized) - allowed_channels)
        if invalid_channels:
            raise ValueError(f"Unsupported notification channel(s): {', '.join(invalid_channels)}")
        if not normalized:
            raise ValueError("At least one notification channel is required")
        return normalized


class ExportPredictionRequest(PredictionInput):
    """Request schema for prediction export."""

    horizon: str = Field(default="weekly", pattern="^(daily|weekly|monthly)$", description="Prediction horizon")
    file_format: str = Field(default="excel", pattern="^(excel|pdf)$", description="Export format")


class BinReadingRequest(BaseModel):
    """Input schema for ESP32 smart-bin readings."""

    bin_id: str = Field(..., min_length=1, max_length=80, description="Smart bin identifier", json_schema_extra={"example": "TPS-001"})
    fill_level: float = Field(..., ge=0.0, le=100.0, description="Bin fill level percentage", json_schema_extra={"example": 72.5})
    device_id: str = Field(..., min_length=1, max_length=80, description="ESP32 device identifier", json_schema_extra={"example": "ESP32-001"})

    @field_validator("bin_id", "device_id")
    @classmethod
    def validate_required_text(cls, value):
        """Reject blank identifiers after trimming whitespace."""
        if not value.strip():
            raise ValueError("Value cannot be blank")
        return value.strip()


class BinReadingResponse(BaseModel):
    """Response schema for stored smart-bin readings."""

    id: int
    bin_id: str
    device_id: str
    fill_level: float
    status: str
    created_at: str
