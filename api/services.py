"""Application service helpers that keep route handlers thin."""
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Tuple

from fastapi.responses import StreamingResponse

from . import pathing  # noqa: F401
from .dependencies import PredictorState

from export import export_predictions_to_excel, export_predictions_to_pdf
from iot_storage import DEFAULT_DB_PATH, init_iot_db


DATASET_PATH = Path(__file__).parent.parent / "data" / "raw" / "waste_dataset.csv"


def build_daily_response(predictor: Any, input_data: Any) -> Dict[str, Any]:
    prediction = predictor.predict_daily_with_details(input_data.model_dump())
    return {
        "prediction_type": "daily",
        "date": input_data.date,
        "predicted_waste_volume": prediction["predicted_waste_volume"],
        "unit": "tons",
        "confidence_interval": prediction["confidence_interval"],
        "anomaly": prediction["anomaly"],
        "fleet_recommendation": prediction["fleet_recommendation"],
    }


def build_range_response(predictor: Any, input_data: Any, horizon: str) -> Dict[str, Any]:
    input_dict = input_data.model_dump()
    result = predictor.predict_weekly(input_dict) if horizon == "weekly" else predictor.predict_monthly(input_dict)
    daily_predictions = result["daily_predictions"]
    return {
        "prediction_type": horizon,
        "start_date": input_data.date,
        "end_date": daily_predictions[-1]["date"],
        "total_volume": result["total_volume"],
        "average_daily": result["average_daily"],
        "unit": "tons",
        "confidence_interval": result["confidence_interval"],
        "daily_predictions": daily_predictions,
    }


def build_export_payload(predictor: Any, request: Any) -> Tuple[Dict[str, Any], list]:
    input_dict = request.model_dump()
    horizon = input_dict.pop("horizon")
    input_dict.pop("file_format")

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
        return summary, daily_predictions

    result = predictor.predict_weekly(input_dict) if horizon == "weekly" else predictor.predict_monthly(input_dict)
    daily_predictions = result["daily_predictions"]
    summary = {
        "prediction_type": horizon,
        "start_date": request.date,
        "end_date": daily_predictions[-1]["date"],
        "total_volume": result["total_volume"],
        "average_daily": result["average_daily"],
    }
    return summary, daily_predictions


def build_export_response(predictor: Any, request: Any) -> StreamingResponse:
    summary, daily_predictions = build_export_payload(predictor, request)
    horizon = request.horizon
    file_format = request.file_format
    filename = f"waste_prediction_{horizon}.{'xlsx' if file_format == 'excel' else 'pdf'}"

    if file_format == "excel":
        data = export_predictions_to_excel(summary, daily_predictions)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        data = export_predictions_to_pdf(summary, daily_predictions)
        media_type = "application/pdf"

    return StreamingResponse(
        BytesIO(data),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def run_health_checks(state: PredictorState) -> Dict[str, Any]:
    checks = {
        "model_loaded": state.loaded,
        "dataset_available": DATASET_PATH.exists(),
        "sqlite_writable": False,
        "pdf_export_available": False,
    }

    try:
        init_iot_db(DEFAULT_DB_PATH)
        checks["sqlite_writable"] = True
    except Exception as exc:
        checks["sqlite_error"] = str(exc)

    try:
        export_predictions_to_pdf(
            {"prediction_type": "health", "total_volume": 1.0, "average_daily": 1.0},
            [{"date": "2025-01-01", "day_name": "Wednesday", "predicted_volume": 1.0}],
        )
        checks["pdf_export_available"] = True
    except Exception as exc:
        checks["pdf_export_error"] = str(exc)

    return checks
