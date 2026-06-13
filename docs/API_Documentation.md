# API Documentation
## Waste Volume Prediction REST API

---

## Base Information

**Base URL**: `http://localhost:8000`  
**API Version**: 1.0.0  
**Content-Type**: `application/json`  
**Authentication**: None (can be added in future versions)

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Endpoints](#endpoints)
3. [Request & Response Examples](#request--response-examples)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Code Examples](#code-examples)

---

## Getting Started

### Starting the API Server

```bash
# Make sure you're in the project directory
cd waste-volume-prediction

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Start the API server
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`

### Interactive Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to test the API directly from your browser.

---

## Endpoints

### 1. Root Endpoint

Get basic API information.

**Endpoint**: `GET /`

**Response**: `200 OK`

```json
{
  "api_name": "Waste Volume Prediction API",
  "version": "1.0.0",
  "description": "REST API for predicting waste volume using Machine Learning",
  "endpoints": {
    "health": "/health",
    "docs": "/docs",
    "daily_prediction": "/predict/daily",
    "weekly_prediction": "/predict/weekly",
    "monthly_prediction": "/predict/monthly",
    "iot_ingest": "/iot/bin-reading",
    "iot_latest": "/iot/bin-readings/latest",
    "iot_bin_latest": "/iot/bin/{bin_id}/latest"
  },
  "status": "operational"
}
```

---

### 2. Health Check

Check API and model status.

**Endpoint**: `GET /health`

**Response**: `200 OK`

```json
{
  "status": "healthy",
  "model_loaded": true,
  "message": "API is running and model is loaded"
}
```

**Response when model not loaded**: `200 OK`

```json
{
  "status": "unhealthy",
  "model_loaded": false,
  "message": "Model not loaded: [error details]"
}
```

---

### 3. Daily Prediction

Predict waste volume for a single day.

**Endpoint**: `POST /predict/daily`

**Request Body**:

| Field | Type | Required | Range | Description |
|-------|------|----------|-------|-------------|
| date | string | Yes | YYYY-MM-DD | Date for prediction |
| temperature | float | Yes | 24.0 - 35.0 | Temperature in Celsius |
| rainfall | float | Yes | 0.0 - 120.0 | Rainfall in mm |
| humidity | float | Yes | 55.0 - 95.0 | Humidity percentage |
| holiday | integer | Yes | 0 or 1 | Holiday flag (0=No, 1=Yes) |
| weekend | integer | Yes | 0 or 1 | Weekend flag (0=No, 1=Yes) |
| population_density | float | Yes | 3000.0 - 15000.0 | Population per km² |
| event_level | integer | Yes | 0 - 5 | Event intensity level |

**Response**: `200 OK`

```json
{
  "prediction_type": "daily",
  "date": "2025-06-15",
  "predicted_waste_volume": 85.23,
  "unit": "tons",
  "fleet_recommendation": {
    "trucks_needed": 11,
    "truck_capacity": 8.0,
    "total_capacity": 88.0,
    "utilization_rate": 96.85
  }
}
```

**Error Response**: `400 Bad Request`

```json
{
  "detail": [
    {
      "loc": ["body", "temperature"],
      "msg": "ensure this value is less than or equal to 35.0",
      "type": "value_error.number.not_le"
    }
  ]
}
```

**Error Response**: `503 Service Unavailable`

```json
{
  "detail": "Model not loaded. Please train the model first by running: python src/train_model.py"
}
```

---

### 4. Weekly Prediction

Predict total waste volume for 7 consecutive days.

**Endpoint**: `POST /predict/weekly`

**Request Body**: Same as `/predict/daily` (starting date)

**Response**: `200 OK`

```json
{
  "prediction_type": "weekly",
  "start_date": "2025-06-15",
  "end_date": "2025-06-21",
  "total_volume": 567.89,
  "average_daily": 81.13,
  "unit": "tons",
  "daily_predictions": [
    {
      "date": "2025-06-15",
      "day_name": "Sunday",
      "predicted_volume": 85.23
    },
    {
      "date": "2025-06-16",
      "day_name": "Monday",
      "predicted_volume": 78.45
    },
    {
      "date": "2025-06-17",
      "day_name": "Tuesday",
      "predicted_volume": 79.12
    },
    {
      "date": "2025-06-18",
      "day_name": "Wednesday",
      "predicted_volume": 80.34
    },
    {
      "date": "2025-06-19",
      "day_name": "Thursday",
      "predicted_volume": 79.87
    },
    {
      "date": "2025-06-20",
      "day_name": "Friday",
      "predicted_volume": 81.56
    },
    {
      "date": "2025-06-21",
      "day_name": "Saturday",
      "predicted_volume": 83.32
    }
  ]
}
```

---

### 5. Monthly Prediction

Predict total waste volume for 30 consecutive days.

**Endpoint**: `POST /predict/monthly`

**Request Body**: Same as `/predict/daily` (starting date)

**Response**: `200 OK`

```json
{
  "prediction_type": "monthly",
  "start_date": "2025-06-15",
  "end_date": "2025-07-14",
  "total_volume": 2435.67,
  "average_daily": 81.19,
  "unit": "tons",
  "daily_predictions": [
    {
      "date": "2025-06-15",
      "day_name": "Sunday",
      "predicted_volume": 85.23
    },
    // ... 28 more days
    {
      "date": "2025-07-14",
      "day_name": "Monday",
      "predicted_volume": 78.92
    }
  ]
}
```

---

### 6. ESP32 Smart Bin Reading

Store one ESP32 smart-bin fill-level reading.

**Endpoint**: `POST /iot/bin-reading`

**Request Body**:

| Field | Type | Required | Range | Description |
|-------|------|----------|-------|-------------|
| bin_id | string | Yes | 1 - 80 chars | Smart bin identifier |
| fill_level | float | Yes | 0.0 - 100.0 | Bin fill percentage |
| device_id | string | Yes | 1 - 80 chars | ESP32 device identifier |

**Response**: `200 OK`

```json
{
  "id": 1,
  "bin_id": "TPS-001",
  "device_id": "ESP32-001",
  "fill_level": 72.5,
  "status": "high",
  "created_at": "2026-06-13T02:16:00Z"
}
```

---

### 7. Latest Smart Bin Readings

Return recent ESP32 smart-bin readings.

**Endpoint**: `GET /iot/bin-readings/latest`

Optional query parameter:

| Field | Type | Default | Range | Description |
|-------|------|---------|-------|-------------|
| limit | integer | 20 | 1 - 100 | Maximum readings to return |

**Endpoint**: `GET /iot/bin/{bin_id}/latest`

Returns the newest reading for a single smart bin, or `404 Not Found` if the bin has no readings.

---

## Request & Response Examples

### Example 1: Simple Daily Prediction

**Request**:
```bash
curl -X POST "http://localhost:8000/predict/daily" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-06-15",
    "temperature": 30.5,
    "rainfall": 5.0,
    "humidity": 75.0,
    "holiday": 0,
    "weekend": 1,
    "population_density": 9500.0,
    "event_level": 2
  }'
```

**Response**:
```json
{
  "prediction_type": "daily",
  "date": "2025-06-15",
  "predicted_waste_volume": 85.23,
  "unit": "tons",
  "fleet_recommendation": {
    "trucks_needed": 11,
    "truck_capacity": 8.0,
    "total_capacity": 88.0,
    "utilization_rate": 96.85
  }
}
```

### Example 2: Holiday Prediction

**Request**:
```bash
curl -X POST "http://localhost:8000/predict/daily" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-08-17",
    "temperature": 31.0,
    "rainfall": 0.0,
    "humidity": 70.0,
    "holiday": 1,
    "weekend": 0,
    "population_density": 10000.0,
    "event_level": 5
  }'
```

**Response**:
```json
{
  "prediction_type": "daily",
  "date": "2025-08-17",
  "predicted_waste_volume": 112.45,
  "unit": "tons",
  "fleet_recommendation": {
    "trucks_needed": 15,
    "truck_capacity": 8.0,
    "total_capacity": 120.0,
    "utilization_rate": 93.71
  }
}
```

### Example 3: Rainy Day Prediction

**Request**:
```bash
curl -X POST "http://localhost:8000/predict/daily" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-12-25",
    "temperature": 26.5,
    "rainfall": 85.0,
    "humidity": 90.0,
    "holiday": 1,
    "weekend": 0,
    "population_density": 9000.0,
    "event_level": 3
  }'
```

**Response**:
```json
{
  "prediction_type": "daily",
  "date": "2025-12-25",
  "predicted_waste_volume": 95.67,
  "unit": "tons",
  "fleet_recommendation": {
    "trucks_needed": 12,
    "truck_capacity": 8.0,
    "total_capacity": 96.0,
    "utilization_rate": 99.66
  }
}
```

---

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "detail": "Error message or list of validation errors"
}
```

### HTTP Status Codes

| Status Code | Meaning | When It Occurs |
|-------------|---------|----------------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid input parameters |
| 404 | Not Found | Endpoint doesn't exist |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Model not loaded |

### Common Validation Errors

**Invalid Date Format**:
```json
{
  "detail": [
    {
      "loc": ["body", "date"],
      "msg": "Date must be in YYYY-MM-DD format",
      "type": "value_error"
    }
  ]
}
```

**Value Out of Range**:
```json
{
  "detail": [
    {
      "loc": ["body", "temperature"],
      "msg": "ensure this value is greater than or equal to 24.0",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

**Missing Required Field**:
```json
{
  "detail": [
    {
      "loc": ["body", "humidity"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Rate Limiting

Currently, the API does not implement rate limiting. For production deployment, consider adding:

- Rate limiting middleware
- Authentication/API keys
- Request throttling

**Recommended Configuration** (for future implementation):
- 100 requests per minute per IP
- 1000 requests per hour per API key

---

## Code Examples

### Python with requests

```python
import requests
import json

# API configuration
API_BASE_URL = "http://localhost:8000"

def predict_daily(date, temperature, rainfall, humidity, 
                  holiday, weekend, population_density, event_level):
    """
    Make daily waste volume prediction
    """
    endpoint = f"{API_BASE_URL}/predict/daily"
    
    payload = {
        "date": date,
        "temperature": temperature,
        "rainfall": rainfall,
        "humidity": humidity,
        "holiday": holiday,
        "weekend": weekend,
        "population_density": population_density,
        "event_level": event_level
    }
    
    try:
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()  # Raise exception for bad status
        
        result = response.json()
        print(f"Predicted volume: {result['predicted_waste_volume']} tons")
        print(f"Trucks needed: {result['fleet_recommendation']['trucks_needed']}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Example usage
if __name__ == "__main__":
    result = predict_daily(
        date="2025-06-15",
        temperature=30.5,
        rainfall=5.0,
        humidity=75.0,
        holiday=0,
        weekend=1,
        population_density=9500.0,
        event_level=2
    )
```

### JavaScript (Node.js) with axios

```javascript
const axios = require('axios');

const API_BASE_URL = 'http://localhost:8000';

async function predictDaily(params) {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/predict/daily`,
      params
    );
    
    const result = response.data;
    console.log(`Predicted volume: ${result.predicted_waste_volume} tons`);
    console.log(`Trucks needed: ${result.fleet_recommendation.trucks_needed}`);
    
    return result;
    
  } catch (error) {
    if (error.response) {
      // Server responded with error
      console.error('Error:', error.response.data.detail);
    } else {
      // Request failed
      console.error('Error:', error.message);
    }
    return null;
  }
}

// Example usage
const params = {
  date: "2025-06-15",
  temperature: 30.5,
  rainfall: 5.0,
  humidity: 75.0,
  holiday: 0,
  weekend: 1,
  population_density: 9500.0,
  event_level: 2
};

predictDaily(params);
```

### Python with aiohttp (Async)

```python
import aiohttp
import asyncio

API_BASE_URL = "http://localhost:8000"

async def predict_daily_async(session, params):
    """
    Make async daily prediction
    """
    endpoint = f"{API_BASE_URL}/predict/daily"
    
    async with session.post(endpoint, json=params) as response:
        if response.status == 200:
            result = await response.json()
            return result
        else:
            error = await response.text()
            print(f"Error: {error}")
            return None

async def batch_predict(predictions):
    """
    Make multiple predictions concurrently
    """
    async with aiohttp.ClientSession() as session:
        tasks = [
            predict_daily_async(session, params) 
            for params in predictions
        ]
        results = await asyncio.gather(*tasks)
        return results

# Example usage
if __name__ == "__main__":
    predictions = [
        {
            "date": "2025-06-15",
            "temperature": 30.5,
            "rainfall": 5.0,
            "humidity": 75.0,
            "holiday": 0,
            "weekend": 1,
            "population_density": 9500.0,
            "event_level": 2
        },
        {
            "date": "2025-06-16",
            "temperature": 31.0,
            "rainfall": 0.0,
            "humidity": 70.0,
            "holiday": 0,
            "weekend": 0,
            "population_density": 9500.0,
            "event_level": 1
        }
    ]
    
    results = asyncio.run(batch_predict(predictions))
    for result in results:
        if result:
            print(f"Date: {result['date']}, Volume: {result['predicted_waste_volume']} tons")
```

### C# with HttpClient

```csharp
using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

public class WastePredictionClient
{
    private readonly HttpClient _httpClient;
    private const string ApiBaseUrl = "http://localhost:8000";

    public WastePredictionClient()
    {
        _httpClient = new HttpClient();
    }

    public async Task<PredictionResult> PredictDaily(PredictionRequest request)
    {
        var json = JsonSerializer.Serialize(request);
        var content = new StringContent(json, Encoding.UTF8, "application/json");
        
        try
        {
            var response = await _httpClient.PostAsync(
                $"{ApiBaseUrl}/predict/daily", 
                content
            );
            
            response.EnsureSuccessStatusCode();
            
            var responseJson = await response.Content.ReadAsStringAsync();
            var result = JsonSerializer.Deserialize<PredictionResult>(responseJson);
            
            return result;
        }
        catch (HttpRequestException ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
            return null;
        }
    }
}

public class PredictionRequest
{
    public string Date { get; set; }
    public double Temperature { get; set; }
    public double Rainfall { get; set; }
    public double Humidity { get; set; }
    public int Holiday { get; set; }
    public int Weekend { get; set; }
    public double PopulationDensity { get; set; }
    public int EventLevel { get; set; }
}

public class PredictionResult
{
    public string PredictionType { get; set; }
    public string Date { get; set; }
    public double PredictedWasteVolume { get; set; }
    public string Unit { get; set; }
    public FleetRecommendation FleetRecommendation { get; set; }
}

public class FleetRecommendation
{
    public int TrucksNeeded { get; set; }
    public double TruckCapacity { get; set; }
    public double TotalCapacity { get; set; }
    public double UtilizationRate { get; set; }
}

// Example usage
var client = new WastePredictionClient();
var request = new PredictionRequest
{
    Date = "2025-06-15",
    Temperature = 30.5,
    Rainfall = 5.0,
    Humidity = 75.0,
    Holiday = 0,
    Weekend = 1,
    PopulationDensity = 9500.0,
    EventLevel = 2
};

var result = await client.PredictDaily(request);
Console.WriteLine($"Predicted volume: {result.PredictedWasteVolume} tons");
```

---

## Best Practices

### 1. Error Handling
Always handle API errors gracefully:
```python
try:
    response = requests.post(url, json=data)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e}")
except requests.exceptions.ConnectionError:
    print("Connection error: Cannot reach API server")
except requests.exceptions.Timeout:
    print("Timeout error: Request took too long")
```

### 2. Input Validation
Validate inputs before sending to API:
```python
def validate_inputs(date, temperature, rainfall, humidity, 
                    holiday, weekend, population_density, event_level):
    errors = []
    
    # Validate ranges
    if not (24.0 <= temperature <= 35.0):
        errors.append("Temperature must be between 24 and 35")
    
    if not (0.0 <= rainfall <= 120.0):
        errors.append("Rainfall must be between 0 and 120")
    
    # ... more validations
    
    return errors
```

### 3. Retry Logic
Implement retry for transient failures:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1))
def predict_with_retry(params):
    response = requests.post(API_URL, json=params)
    response.raise_for_status()
    return response.json()
```

### 4. Caching
Cache predictions for identical inputs:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def predict_cached(date, temperature, rainfall, humidity,
                   holiday, weekend, population_density, event_level):
    # Make API call
    pass
```

---

## Testing the API

### Using Swagger UI

1. Navigate to http://localhost:8000/docs
2. Click on the endpoint you want to test
3. Click "Try it out"
4. Fill in the request body
5. Click "Execute"
6. View the response

### Using Postman

1. Create new request
2. Set method to POST
3. Enter URL: `http://localhost:8000/predict/daily`
4. Go to Body tab
5. Select "raw" and "JSON"
6. Paste request JSON
7. Click "Send"

### Using Python Script

Create `test_api.py`:
```python
import requests

def test_api():
    # Test health check
    response = requests.get("http://localhost:8000/health")
    print("Health check:", response.json())
    
    # Test prediction
    data = {
        "date": "2025-06-15",
        "temperature": 30.5,
        "rainfall": 5.0,
        "humidity": 75.0,
        "holiday": 0,
        "weekend": 1,
        "population_density": 9500.0,
        "event_level": 2
    }
    
    response = requests.post("http://localhost:8000/predict/daily", json=data)
    print("Prediction:", response.json())

if __name__ == "__main__":
    test_api()
```

Run: `python test_api.py`

---

## Security Considerations

### For Production Deployment

1. **Enable HTTPS**: Use SSL/TLS certificates
2. **Add Authentication**: Implement API keys or OAuth
3. **Rate Limiting**: Prevent abuse
4. **Input Sanitization**: Validate all inputs
5. **CORS Configuration**: Restrict allowed origins
6. **Logging**: Log all requests for audit
7. **Error Messages**: Don't expose sensitive information

---

## Changelog

### Version 1.0.0 (2026-06-10)
- Initial release
- Daily, weekly, and monthly prediction endpoints
- Health check endpoint
- Auto-generated documentation

---

## Support

For API support:
- **Email**: api-support@wastepredict.com
- **Documentation**: http://localhost:8000/docs
- **Issues**: Report via GitHub Issues

---

## Phase 2 API Addendum

The API now returns Phase 2 prediction metadata in addition to the original
daily, weekly, and monthly prediction payloads.

### Enhanced Prediction Responses

`POST /predict/daily`, `POST /predict/weekly`, and `POST /predict/monthly`
include:

- `confidence_interval`: lower bound, upper bound, confidence level, and margin of error
- `anomaly`: outlier flag, anomaly score, and explanation
- `fleet_recommendation`: daily truck recommendation for daily predictions

### Anomaly Detection

```http
POST /detect/anomaly
```

Request body matches `/predict/daily`. Example response:

```json
{
  "is_anomaly": false,
  "score": 0.0951,
  "message": "Input is within normal training patterns"
}
```

### Prediction Notifications

```http
POST /notifications/prediction-alert
```

Additional request fields:

```json
{
  "threshold": 100.0,
  "channels": ["email", "sms"],
  "dry_run": true
}
```

Real email sending uses `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`,
`SMTP_PASSWORD`, `SMTP_FROM`, and `NOTIFICATION_RECIPIENTS`. Real SMS sending
uses `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`, and
`SMS_RECIPIENTS`. If credentials are missing or `dry_run` is true, the endpoint
returns a preview result without sending.

### Prediction Export

```http
POST /export/prediction
```

Additional request fields:

```json
{
  "horizon": "weekly",
  "file_format": "excel"
}
```

Supported horizons: `daily`, `weekly`, `monthly`.
Supported formats: `excel`, `pdf`.

### Automated Retraining

Run the retraining helper from the project root:

```bash
python src/retrain.py --reason scheduled
```

To retrain with a replacement CSV:

```bash
python src/retrain.py --data-path path/to/waste_dataset.csv --reason new-data
```

Retraining appends status entries to `reports/retraining_log.csv`.

---

**API Documentation Version**: 1.0  
**Last Updated**: 10 Juni 2026  
**Maintainer**: Development Team
