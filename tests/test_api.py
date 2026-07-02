import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient

from api import main


client = TestClient(main.app)

VALID_INPUT = {
    "date": "2025-01-15",
    "temperature": 30.5,
    "rainfall": 5.0,
    "humidity": 75.0,
    "holiday": 0,
    "weekend": 0,
    "population_density": 9500.0,
    "event_level": 1,
}


class DummyPredictor:
    def predict_daily_with_details(self, input_data):
        return {
            "predicted_waste_volume": 100.0,
            "confidence_interval": {
                "confidence": 0.95,
                "lower_bound": 95.0,
                "upper_bound": 105.0,
                "margin_of_error": 5.0,
            },
            "anomaly": {
                "is_anomaly": False,
                "score": 0.1,
                "message": "ok",
            },
            "fleet_recommendation": {
                "trucks_needed": 13,
                "truck_capacity": 8.0,
                "total_capacity": 104.0,
                "utilization_rate": 96.15,
            },
        }

    def predict_weekly(self, input_data):
        return {
            "total_volume": 700.0,
            "average_daily": 100.0,
            "confidence_interval": {
                "confidence": 0.95,
                "lower_bound": 650.0,
                "upper_bound": 750.0,
                "margin_of_error": 50.0,
            },
            "daily_predictions": [
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
                        "score": 0.1,
                        "message": "ok",
                    },
                }
            ],
        }

    def predict_monthly(self, input_data):
        result = self.predict_weekly(input_data)
        result["total_volume"] = 3000.0
        return result


def test_root_and_health_endpoints_respond():
    root = client.get("/")
    health = client.get("/health")

    assert root.status_code == 200
    assert root.json()["endpoints"]["daily_prediction"] == "/predict/daily"
    assert health.status_code == 200
    assert "model_loaded" in health.json()
    assert "checks" in health.json()


def test_rate_limit_returns_429(monkeypatch):
    monkeypatch.setattr(main, "RATE_LIMIT_PER_MINUTE", 1)
    main._rate_limit_window.clear()

    first = client.get("/")
    second = client.get("/")

    assert first.status_code == 200
    assert second.status_code == 429


def test_rate_limit_uses_forwarded_client_ip(monkeypatch):
    monkeypatch.setattr(main, "RATE_LIMIT_PER_MINUTE", 1)
    main._rate_limit_window.clear()

    first = client.get("/", headers={"X-Forwarded-For": "203.0.113.10"})
    second = client.get("/", headers={"X-Forwarded-For": "203.0.113.11"})

    assert first.status_code == 200
    assert second.status_code == 200


def test_health_is_exempt_from_rate_limit(monkeypatch):
    monkeypatch.setattr(main, "RATE_LIMIT_PER_MINUTE", 1)
    main._rate_limit_window.clear()

    assert client.get("/health").status_code == 200
    assert client.get("/health").status_code == 200


def test_prediction_input_validation_rejects_bad_values():
    response = client.post("/predict/daily", json={**VALID_INPUT, "temperature": 99})

    assert response.status_code == 422


def test_notification_rejects_unsupported_channels():
    response = client.post(
        "/notifications/prediction-alert",
        json={**VALID_INPUT, "threshold": 100.0, "channels": ["email", "whatsapp"]},
    )

    assert response.status_code == 422


def test_iot_ingest_requires_api_key_when_configured(monkeypatch):
    monkeypatch.setattr(main, "IOT_API_KEY", "secret")

    missing_key = client.post(
        "/iot/bin-reading",
        json={"bin_id": "TPS-001", "fill_level": 50, "device_id": "ESP32-001"},
    )
    wrong_key = client.post(
        "/iot/bin-reading",
        headers={"X-API-Key": "wrong"},
        json={"bin_id": "TPS-001", "fill_level": 50, "device_id": "ESP32-001"},
    )

    assert missing_key.status_code == 401
    assert wrong_key.status_code == 401


def test_iot_ingest_accepts_valid_api_key(monkeypatch):
    monkeypatch.setattr(main, "IOT_API_KEY", "secret")
    monkeypatch.setattr(
        main,
        "save_bin_reading",
        lambda bin_id, device_id, fill_level: {
            "id": 1,
            "bin_id": bin_id,
            "device_id": device_id,
            "fill_level": fill_level,
            "status": "medium",
            "created_at": "2026-07-02T00:00:00Z",
        },
    )

    response = client.post(
        "/iot/bin-reading",
        headers={"X-API-Key": "secret"},
        json={"bin_id": "TPS-001", "fill_level": 50, "device_id": "ESP32-001"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "medium"


def test_iot_latest_limit_validation():
    response = client.get("/iot/bin-readings/latest?limit=101")

    assert response.status_code == 400


def test_export_endpoint_returns_pdf_with_dummy_predictor(monkeypatch):
    monkeypatch.setattr(main, "PREDICTOR_LOADED", True)
    monkeypatch.setattr(main, "predictor", DummyPredictor())

    response = client.post(
        "/export/prediction",
        json={**VALID_INPUT, "horizon": "weekly", "file_format": "pdf"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
