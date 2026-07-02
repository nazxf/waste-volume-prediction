import sys
from pathlib import Path

import matplotlib

sys.path.append(str(Path(__file__).parent.parent / "src"))

from export import export_predictions_to_excel, export_predictions_to_pdf


SUMMARY = {
    "prediction_type": "weekly",
    "start_date": "2025-01-15",
    "end_date": "2025-01-21",
    "total_volume": 700.0,
    "average_daily": 100.0,
}

DAILY_PREDICTIONS = [
    {
        "date": "2025-01-15",
        "day_name": "Wednesday",
        "predicted_volume": 100.0,
        "confidence_interval": {
            "confidence": 0.95,
            "lower_bound": 95.0,
            "upper_bound": 105.0,
            "margin_of_error": 5.0,
        },
        "anomaly": {
            "is_anomaly": False,
            "score": 0.1234,
            "message": "Input is within normal training patterns",
        },
    }
]


def test_prediction_exports_generate_valid_binary_files():
    excel = export_predictions_to_excel(SUMMARY, DAILY_PREDICTIONS)
    pdf = export_predictions_to_pdf(SUMMARY, DAILY_PREDICTIONS)

    assert excel.startswith(b"PK")
    assert pdf.startswith(b"%PDF")
    assert len(excel) > 1000
    assert len(pdf) > 1000


def test_pdf_export_uses_non_gui_matplotlib_backend():
    assert matplotlib.get_backend().lower() == "agg"
