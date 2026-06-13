"""
FastAPI REST API for Waste Volume Prediction System
Provides endpoints for daily, weekly, and monthly predictions
"""
import sys
from pathlib import Path
from io import BytesIO

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Any, Dict, List, Union
from datetime import datetime
from iot_storage import get_latest_bin_reading, get_latest_readings, save_bin_reading

# Import predictor
try:
    from export import export_predictions_to_excel, export_predictions_to_pdf
    from notifications import send_prediction_notifications
    from predict import WasteVolumePredictor
    predictor = WasteVolumePredictor()
    PREDICTOR_LOADED = True
except FileNotFoundError as e:
    PREDICTOR_LOADED = False
    PREDICTOR_ERROR = str(e)
except Exception as e:
    PREDICTOR_LOADED = False
    PREDICTOR_ERROR = f"Failed to load model: {e}"


# Create FastAPI app
app = FastAPI(
    title="Waste Volume Prediction API",
    description="REST API for predicting waste volume using Machine Learning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class PredictionInput(BaseModel):
    """Input schema for prediction"""
    date: str = Field(..., description="Date in YYYY-MM-DD format", example="2025-01-15")
    temperature: float = Field(..., ge=24.0, le=35.0, description="Temperature in Celsius", example=30.5)
    rainfall: float = Field(..., ge=0.0, le=120.0, description="Rainfall in mm", example=5.0)
    humidity: float = Field(..., ge=55.0, le=95.0, description="Humidity percentage", example=75.0)
    holiday: int = Field(..., ge=0, le=1, description="Holiday flag (0=No, 1=Yes)", example=0)
    weekend: int = Field(..., ge=0, le=1, description="Weekend flag (0=No, 1=Yes)", example=0)
    population_density: float = Field(..., ge=3000.0, le=15000.0, description="Population density (people/km2)", example=9500.0)
    event_level: int = Field(..., ge=0, le=5, description="Event level (0-5)", example=1)
    
    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        """Validate date format"""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")


class DailyPredictionResponse(BaseModel):
    """Response schema for daily prediction"""
    prediction_type: str = "daily"
    date: str
    predicted_waste_volume: float
    unit: str = "tons"
    confidence_interval: Dict[str, float]
    anomaly: Dict[str, Any]
    fleet_recommendation: Dict[str, Union[int, float]]


class WeeklyPredictionResponse(BaseModel):
    """Response schema for weekly prediction"""
    prediction_type: str = "weekly"
    start_date: str
    end_date: str
    total_volume: float
    average_daily: float
    unit: str = "tons"
    confidence_interval: Dict[str, float]
    daily_predictions: List[Dict]


class MonthlyPredictionResponse(BaseModel):
    """Response schema for monthly prediction"""
    prediction_type: str = "monthly"
    start_date: str
    end_date: str
    total_volume: float
    average_daily: float
    unit: str = "tons"
    confidence_interval: Dict[str, float]
    daily_predictions: List[Dict]


class HealthResponse(BaseModel):
    """Health check response"""
    model_config = ConfigDict(protected_namespaces=())

    status: str
    model_loaded: bool
    message: str


class NotificationRequest(PredictionInput):
    """Request schema for notification checks"""
    threshold: float = Field(..., ge=0.0, description="Alert threshold in tons", example=100.0)
    channels: List[str] = Field(default=["email"], description="Notification channels: email and/or sms")
    dry_run: bool = Field(default=True, description="Return notification preview without sending")


class ExportPredictionRequest(PredictionInput):
    """Request schema for prediction export"""
    horizon: str = Field(default="weekly", pattern="^(daily|weekly|monthly)$", description="Prediction horizon")
    file_format: str = Field(default="excel", pattern="^(excel|pdf)$", description="Export format")


class BinReadingRequest(BaseModel):
    """Input schema for ESP32 smart-bin readings."""
    bin_id: str = Field(..., min_length=1, max_length=80, description="Smart bin identifier", example="TPS-001")
    fill_level: float = Field(..., ge=0.0, le=100.0, description="Bin fill level percentage", example=72.5)
    device_id: str = Field(..., min_length=1, max_length=80, description="ESP32 device identifier", example="ESP32-001")

    @field_validator("bin_id", "device_id")
    @classmethod
    def validate_required_text(cls, v):
        """Reject blank identifiers after trimming whitespace."""
        if not v.strip():
            raise ValueError("Value cannot be blank")
        return v.strip()


class BinReadingResponse(BaseModel):
    """Response schema for stored smart-bin readings."""
    id: int
    bin_id: str
    device_id: str
    fill_level: float
    status: str
    created_at: str


# Endpoints
@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information"""
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
            "iot_bin_latest": "/iot/bin/{bin_id}/latest"
        },
        "status": "operational" if PREDICTOR_LOADED else "model_not_loaded"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    if PREDICTOR_LOADED:
        return {
            "status": "healthy",
            "model_loaded": True,
            "message": "API is running and model is loaded"
        }
    else:
        return {
            "status": "unhealthy",
            "model_loaded": False,
            "message": f"Model not loaded: {PREDICTOR_ERROR}"
        }


@app.post("/iot/bin-reading", response_model=BinReadingResponse)
async def create_bin_reading(reading: BinReadingRequest):
    """Store one ESP32 smart-bin fill-level reading."""
    try:
        return save_bin_reading(
            bin_id=reading.bin_id,
            device_id=reading.device_id,
            fill_level=reading.fill_level,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save bin reading: {str(e)}")


@app.get("/iot/bin-readings/latest", response_model=List[BinReadingResponse])
async def latest_bin_readings(limit: int = 20):
    """Return newest ESP32 smart-bin readings across all bins."""
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 100")

    try:
        return get_latest_readings(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load bin readings: {str(e)}")


@app.get("/iot/bin/{bin_id}/latest", response_model=BinReadingResponse)
async def latest_bin_reading(bin_id: str):
    """Return the newest ESP32 smart-bin reading for one bin."""
    try:
        reading = get_latest_bin_reading(bin_id=bin_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load bin reading: {str(e)}")

    if reading is None:
        raise HTTPException(status_code=404, detail=f"No readings found for bin_id '{bin_id}'")

    return reading


@app.post("/predict/daily", response_model=DailyPredictionResponse)
async def predict_daily(input_data: PredictionInput):
    """
    Predict waste volume for a single day
    
    Args:
        input_data: Input parameters for prediction
    
    Returns:
        Daily prediction with fleet recommendation
    
    Raises:
        HTTPException: If model is not loaded or prediction fails
    """
    if not PREDICTOR_LOADED:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please train the model first by running: python src/train_model.py"
        )
    
    try:
        # Convert to dictionary
        input_dict = input_data.model_dump()
        
        # Make prediction with Phase 2 details
        prediction = predictor.predict_daily_with_details(input_dict)
        
        return {
            "prediction_type": "daily",
            "date": input_data.date,
            "predicted_waste_volume": prediction["predicted_waste_volume"],
            "unit": "tons",
            "confidence_interval": prediction["confidence_interval"],
            "anomaly": prediction["anomaly"],
            "fleet_recommendation": prediction["fleet_recommendation"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/weekly", response_model=WeeklyPredictionResponse)
async def predict_weekly(input_data: PredictionInput):
    """
    Predict waste volume for 7 consecutive days
    
    Args:
        input_data: Input parameters for prediction (start date)
    
    Returns:
        Weekly prediction with daily breakdown
    
    Raises:
        HTTPException: If model is not loaded or prediction fails
    """
    if not PREDICTOR_LOADED:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please train the model first by running: python src/train_model.py"
        )
    
    try:
        # Convert to dictionary
        input_dict = input_data.model_dump()
        
        # Make prediction
        weekly_result = predictor.predict_weekly(input_dict)
        
        # Get end date from last prediction
        end_date = weekly_result['daily_predictions'][-1]['date']
        
        return {
            "prediction_type": "weekly",
            "start_date": input_data.date,
            "end_date": end_date,
            "total_volume": weekly_result['total_volume'],
            "average_daily": weekly_result['average_daily'],
            "unit": "tons",
            "confidence_interval": weekly_result["confidence_interval"],
            "daily_predictions": weekly_result['daily_predictions']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/monthly", response_model=MonthlyPredictionResponse)
async def predict_monthly(input_data: PredictionInput):
    """
    Predict waste volume for 30 consecutive days
    
    Args:
        input_data: Input parameters for prediction (start date)
    
    Returns:
        Monthly prediction with daily breakdown
    
    Raises:
        HTTPException: If model is not loaded or prediction fails
    """
    if not PREDICTOR_LOADED:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please train the model first by running: python src/train_model.py"
        )
    
    try:
        # Convert to dictionary
        input_dict = input_data.model_dump()
        
        # Make prediction
        monthly_result = predictor.predict_monthly(input_dict)
        
        # Get end date from last prediction
        end_date = monthly_result['daily_predictions'][-1]['date']
        
        return {
            "prediction_type": "monthly",
            "start_date": input_data.date,
            "end_date": end_date,
            "total_volume": monthly_result['total_volume'],
            "average_daily": monthly_result['average_daily'],
            "unit": "tons",
            "confidence_interval": monthly_result["confidence_interval"],
            "daily_predictions": monthly_result['daily_predictions']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/detect/anomaly", response_model=Dict[str, Any])
async def detect_anomaly(input_data: PredictionInput):
    """Detect whether a prediction input is anomalous."""
    if not PREDICTOR_LOADED:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please train the model first by running: python src/train_model.py"
        )

    try:
        input_dict = input_data.model_dump()
        return predictor.detect_anomaly(input_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")


@app.post("/notifications/prediction-alert", response_model=Dict[str, Any])
async def prediction_alert(request: NotificationRequest):
    """Send or preview prediction threshold notifications."""
    if not PREDICTOR_LOADED:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please train the model first by running: python src/train_model.py"
        )

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
                "message": "Prediction is below threshold; no notification sent."
            }]

        return {
            "triggered": triggered,
            "prediction": prediction,
            "notifications": notification_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Notification workflow failed: {str(e)}")


@app.post("/export/prediction")
async def export_prediction(request: ExportPredictionRequest):
    """Export daily, weekly, or monthly predictions to Excel or PDF."""
    if not PREDICTOR_LOADED:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please train the model first by running: python src/train_model.py"
        )

    try:
        input_dict = request.model_dump()
        horizon = input_dict.pop("horizon")
        file_format = input_dict.pop("file_format")

        if horizon == "daily":
            prediction = predictor.predict_daily_with_details(input_dict)
            daily_predictions = [{
                "date": request.date,
                "day_name": datetime.strptime(request.date, "%Y-%m-%d").strftime("%A"),
                "predicted_volume": prediction["predicted_waste_volume"],
                "confidence_interval": prediction["confidence_interval"],
                "anomaly": prediction["anomaly"],
            }]
            summary = {
                "prediction_type": "daily",
                "start_date": request.date,
                "end_date": request.date,
                "total_volume": prediction["predicted_waste_volume"],
                "average_daily": prediction["predicted_waste_volume"],
            }
        elif horizon == "weekly":
            result = predictor.predict_weekly(input_dict)
            daily_predictions = result["daily_predictions"]
            summary = {
                "prediction_type": "weekly",
                "start_date": request.date,
                "end_date": daily_predictions[-1]["date"],
                "total_volume": result["total_volume"],
                "average_daily": result["average_daily"],
            }
        else:
            result = predictor.predict_monthly(input_dict)
            daily_predictions = result["daily_predictions"]
            summary = {
                "prediction_type": "monthly",
                "start_date": request.date,
                "end_date": daily_predictions[-1]["date"],
                "total_volume": result["total_volume"],
                "average_daily": result["average_daily"],
            }

        filename = f"waste_prediction_{horizon}.{ 'xlsx' if file_format == 'excel' else 'pdf' }"

        if file_format == "excel":
            data = export_predictions_to_excel(summary, daily_predictions)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            data = export_predictions_to_pdf(summary, daily_predictions)
            media_type = "application/pdf"

        return StreamingResponse(
            BytesIO(data),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


# Run with: uvicorn api.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
