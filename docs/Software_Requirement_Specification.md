# Software Requirement Specification (SRS)
## Sistem Prediksi Volume Sampah Kota

---

## 1. Pendahuluan

### 1.1 Tujuan Dokumen
Dokumen ini mendeskripsikan spesifikasi kebutuhan perangkat lunak untuk Sistem Prediksi Volume Sampah Kota. Dokumen ini ditujukan untuk developer, tester, project manager, dan stakeholder untuk memahami kebutuhan sistem secara teknis.

### 1.2 Ruang Lingkup Produk
**Nama Produk**: Waste Volume Prediction System  
**Versi**: 1.0.0  
**Deskripsi**: Sistem berbasis Machine Learning untuk memprediksi volume sampah harian, mingguan, dan bulanan menggunakan algoritma Random Forest dan XGBoost.

### 1.3 Definisi dan Akronim
- **ML**: Machine Learning
- **API**: Application Programming Interface
- **MAE**: Mean Absolute Error
- **RMSE**: Root Mean Squared Error
- **R²**: R-squared Score
- **MAPE**: Mean Absolute Percentage Error
- **TPS**: Tempat Pembuangan Sementara
- **REST**: Representational State Transfer

### 1.4 Referensi
- Business Requirement Document v1.0
- Proposal Proyek
- Architecture Document v1.0

---

## 2. Deskripsi Umum Sistem

### 2.1 Perspektif Produk
Sistem ini merupakan standalone application yang dapat diintegrasikan dengan sistem existing melalui REST API. Sistem terdiri dari:
- Machine Learning model untuk prediksi
- Web dashboard untuk visualisasi dan interaksi
- REST API untuk integrasi programmatic
- Data storage untuk data historis

### 2.2 Fungsi Produk
1. Prediksi volume sampah harian
2. Prediksi volume sampah mingguan (7 hari)
3. Prediksi volume sampah bulanan (30 hari)
4. Rekomendasi jumlah armada optimal
5. Visualisasi data historis dan trend
6. Analisis korelasi faktor-faktor yang mempengaruhi volume
7. Reporting dan export data
8. REST API untuk integrasi

### 2.3 Karakteristik Pengguna

| User Type | Expertise | Access Level | Frequency |
|-----------|-----------|--------------|-----------|
| Admin | High | Full access | Daily |
| Manager | Medium | Read/predict | Daily |
| Operator | Low | Limited read | Daily |
| API Consumer | High | API only | On-demand |

### 2.4 Batasan Operasional
- Sistem memerlukan koneksi internet untuk akses
- Prediksi memerlukan input parameter lengkap
- Model perlu di-retrain setiap 3-6 bulan
- Data historis minimal 1 tahun untuk akurasi optimal

### 2.5 Asumsi dan Dependensi
- Data historis tersedia dan valid
- Server infrastructure tersedia
- Python 3.11+ terinstall
- User memiliki web browser modern
- Network connectivity stabil

---

## 3. Kebutuhan Fungsional

### FR-01: Data Generation
**Priority**: Critical  
**Description**: Sistem dapat generate dataset sintetis untuk testing dan development

**Input**:
- Start date (YYYY-MM-DD)
- End date (YYYY-MM-DD)
- Output path (optional)

**Process**:
1. Generate date range
2. Generate realistic weather data (temperature, rainfall, humidity)
3. Calculate holiday and weekend flags
4. Generate population density with growth trend
5. Generate event levels
6. Calculate waste volume based on all factors with realistic patterns

**Output**:
- CSV file dengan kolom: date, temperature, rainfall, humidity, holiday, weekend, population_density, event_level, waste_volume

**Acceptance Criteria**:
- ✅ Generate 5 years data (2020-2024) dalam < 30 detik
- ✅ Data memiliki pola realistis (weekend > weekday, holiday > normal)
- ✅ No missing values
- ✅ All values within valid ranges

---

### FR-02: Data Preprocessing
**Priority**: Critical  
**Description**: Sistem melakukan preprocessing data sebelum training

**Input**:
- Raw CSV dataset

**Process**:
1. Load dataset
2. Validate required columns
3. Handle missing values
4. Convert date to datetime
5. Extract date features (day, month, year, day_of_week, week_of_year, is_month_start, is_month_end)
6. Split features and target
7. Train-test split (80:20)

**Output**:
- X_train, X_test, y_train, y_test
- Feature names list
- Scaler (optional)

**Acceptance Criteria**:
- ✅ All required columns validated
- ✅ Missing values handled properly
- ✅ Date features extracted correctly
- ✅ Train-test split maintains temporal order
- ✅ No data leakage

---

### FR-03: Model Training
**Priority**: Critical  
**Description**: Sistem melatih model Random Forest dan XGBoost

**Input**:
- Preprocessed training data

**Process**:
1. Train Random Forest with parameters:
   - n_estimators=200
   - max_depth=12
   - random_state=42
   - n_jobs=-1

2. Train XGBoost with parameters:
   - n_estimators=300
   - learning_rate=0.05
   - max_depth=6
   - subsample=0.8
   - colsample_bytree=0.8
   - random_state=42

3. Evaluate both models on test set
4. Compare performance (MAE, RMSE, R², MAPE)
5. Select best model based on RMSE
6. Save all models and metadata

**Output**:
- random_forest.pkl
- xgboost.pkl
- best_model.pkl
- feature_columns.pkl
- evaluation_report.md
- feature_importance.png
- prediction_comparison.png

**Acceptance Criteria**:
- ✅ Training completes without errors
- ✅ Best model R² ≥ 0.85
- ✅ MAPE ≤ 10%
- ✅ All artifacts saved successfully
- ✅ Report generated with metrics

---

### FR-04: Model Evaluation
**Priority**: High  
**Description**: Sistem mengevaluasi performa model

**Metrics**:
1. **MAE** (Mean Absolute Error)
   - Lower is better
   - Interpretasi: rata-rata kesalahan dalam ton

2. **RMSE** (Root Mean Squared Error)
   - Lower is better
   - Penalti lebih besar untuk error besar
   - Digunakan untuk memilih best model

3. **R²** (R-squared)
   - Range: 0-1, higher is better
   - Target: ≥ 0.85
   - Interpretasi: proporsi varians yang dijelaskan

4. **MAPE** (Mean Absolute Percentage Error)
   - Lower is better
   - Target: ≤ 10%
   - Interpretasi: rata-rata error dalam persentase

**Acceptance Criteria**:
- ✅ All metrics calculated correctly
- ✅ Comparison between models clear
- ✅ Best model selected based on RMSE
- ✅ Detailed report generated

---

### FR-05: Daily Prediction
**Priority**: Critical  
**Description**: Prediksi volume sampah untuk satu hari

**Input**:
```json
{
  "date": "2025-01-15",
  "temperature": 30.5,
  "rainfall": 5.0,
  "humidity": 75.0,
  "holiday": 0,
  "weekend": 0,
  "population_density": 9500.0,
  "event_level": 1
}
```

**Process**:
1. Load best model
2. Extract date features from date
3. Prepare feature vector
4. Make prediction
5. Return predicted volume

**Output**:
```json
{
  "predicted_volume": 76.45
}
```

**Acceptance Criteria**:
- ✅ Prediction time < 100ms
- ✅ Input validation performed
- ✅ Error handling for invalid inputs
- ✅ Result rounded to 2 decimal places

---

### FR-06: Weekly Prediction
**Priority**: High  
**Description**: Prediksi total volume sampah untuk 7 hari consecutive

**Input**: Same as FR-05 (starting date)

**Process**:
1. Generate 7 days from start date
2. For each day:
   - Update weekend flag based on day
   - Predict volume
   - Store daily prediction
3. Calculate total and average

**Output**:
```json
{
  "total_volume": 535.20,
  "average_daily": 76.46,
  "daily_predictions": [
    {"date": "2025-01-15", "day_name": "Wednesday", "predicted_volume": 76.45},
    ...
  ]
}
```

**Acceptance Criteria**:
- ✅ Exactly 7 days predicted
- ✅ Weekend flag updated automatically
- ✅ Total equals sum of daily predictions
- ✅ Average calculated correctly

---

### FR-07: Monthly Prediction
**Priority**: High  
**Description**: Prediksi total volume sampah untuk 30 hari consecutive

**Input**: Same as FR-05 (starting date)

**Process**: Similar to FR-06 but for 30 days

**Output**: Similar to FR-06

**Acceptance Criteria**:
- ✅ Exactly 30 days predicted
- ✅ Weekend flag updated automatically
- ✅ Calculations correct

---

### FR-08: Fleet Recommendation
**Priority**: High  
**Description**: Rekomendasi jumlah truk berdasarkan prediksi volume

**Input**:
- predicted_volume (tons)
- truck_capacity (default: 8 tons)

**Process**:
1. Calculate trucks_needed = ceil(predicted_volume / truck_capacity)
2. Calculate total_capacity = trucks_needed × truck_capacity
3. Calculate utilization_rate = (predicted_volume / total_capacity) × 100

**Output**:
```json
{
  "trucks_needed": 10,
  "truck_capacity": 8.0,
  "total_capacity": 80.0,
  "utilization_rate": 95.56
}
```

**Acceptance Criteria**:
- ✅ Trucks rounded up to nearest integer
- ✅ Utilization rate calculated correctly
- ✅ Never recommend 0 trucks

---

### FR-09: Dashboard - Main Page
**Priority**: High  
**Description**: Dashboard utama dengan overview dan quick metrics

**Components**:
1. Header with system title
2. Key metrics cards:
   - Rata-rata volume harian
   - Total data harian
   - Volume maksimum
   - Volume minimum
3. Quick predictions (daily, weekly, monthly)
4. Fleet recommendation
5. Trend chart (last 90 days)

**Acceptance Criteria**:
- ✅ All metrics displayed correctly
- ✅ Charts interactive
- ✅ Load time < 3 seconds
- ✅ Responsive design

---

### FR-10: Dashboard - Data Analysis
**Priority**: Medium  
**Description**: Halaman analisis data dengan visualisasi lengkap

**Components**:
1. Dataset preview (first 20 rows)
2. Descriptive statistics table
3. Distribution histogram
4. Volume by day of week bar chart
5. Monthly trend line chart
6. Correlation heatmap

**Acceptance Criteria**:
- ✅ All charts render correctly
- ✅ Statistics accurate
- ✅ Interactive visualizations

---

### FR-11: Dashboard - Prediction Form
**Priority**: Critical  
**Description**: Form input untuk melakukan prediksi custom

**Input Fields**:
- Date picker (tanggal)
- Slider: Temperature (24-35°C)
- Slider: Rainfall (0-120mm)
- Slider: Humidity (55-95%)
- Selectbox: Holiday (Ya/Tidak)
- Selectbox: Weekend (Ya/Tidak)
- Number input: Population density (3000-15000)
- Slider: Event level (0-5)

**Output Display**:
- Daily prediction metric card
- Weekly prediction metric card
- Monthly prediction metric card
- Fleet recommendation box
- Weekly breakdown chart

**Acceptance Criteria**:
- ✅ All inputs validated
- ✅ Default values realistic
- ✅ Prediction triggered by button
- ✅ Results displayed clearly
- ✅ Error messages for invalid inputs

---

### FR-12: Dashboard - Model Performance
**Priority**: Medium  
**Description**: Halaman menampilkan performa model

**Components**:
1. Evaluation report (from Markdown)
2. Feature importance chart
3. Prediction comparison chart

**Acceptance Criteria**:
- ✅ Report formatted correctly
- ✅ Charts displayed if available
- ✅ Warning message if reports not available

---

### FR-13: Dashboard - About System
**Priority**: Low  
**Description**: Halaman informasi tentang sistem

**Content**:
- Latar belakang
- Permasalahan industri
- Solusi AI
- Manfaat sistem
- Target pengguna
- Teknologi
- Batasan sistem
- Pengembangan lanjutan

**Acceptance Criteria**:
- ✅ Content comprehensive
- ✅ Well-formatted markdown
- ✅ Easy to read

---

### FR-14: REST API - Health Check
**Priority**: High  
**Description**: Endpoint untuk mengecek status API dan model

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "message": "API is running and model is loaded"
}
```

**Acceptance Criteria**:
- ✅ Always returns 200 status code
- ✅ Indicates model loaded status
- ✅ Response time < 50ms

---

### FR-15: REST API - Daily Prediction
**Priority**: Critical  
**Description**: Endpoint untuk prediksi harian

**Endpoint**: `POST /predict/daily`

**Request Body**: (See FR-05)

**Response**: (See FR-05 + fleet_recommendation)

**Acceptance Criteria**:
- ✅ Input validation with proper error messages
- ✅ Response time < 200ms
- ✅ Returns 200 for success, 4xx for bad input, 5xx for server error

---

### FR-16: REST API - Weekly Prediction
**Priority**: High  
**Description**: Endpoint untuk prediksi mingguan

**Endpoint**: `POST /predict/weekly`

**Request/Response**: See FR-06

**Acceptance Criteria**: Same as FR-15

---

### FR-17: REST API - Monthly Prediction
**Priority**: High  
**Description**: Endpoint untuk prediksi bulanan

**Endpoint**: `POST /predict/monthly`

**Request/Response**: See FR-07

**Acceptance Criteria**: Same as FR-15

---

## 4. Kebutuhan Non-Fungsional

### NFR-01: Performance
**Requirement**: Sistem harus memiliki performa yang baik
- API response time < 200ms (p95)
- Dashboard load time < 3 seconds
- Model training time < 10 minutes untuk 5 years data
- Prediction time < 100ms per sample

**Measurement**: Load testing dengan 100 concurrent users

---

### NFR-02: Scalability
**Requirement**: Sistem harus dapat di-scale
- Support hingga 10 years historical data
- Support 100 concurrent API requests
- Horizontal scaling capability
- Efficient memory usage (< 2GB for model inference)

---

### NFR-03: Reliability
**Requirement**: Sistem harus reliable
- System uptime ≥ 99%
- Graceful error handling
- Automatic retry for transient errors
- Data backup mechanism

---

### NFR-04: Usability
**Requirement**: Sistem harus user-friendly
- Intuitive UI/UX
- Indonesian language support
- Clear error messages
- Help text and tooltips
- Responsive design (desktop, tablet)
- Minimal training required (< 2 hours)

---

### NFR-05: Maintainability
**Requirement**: Sistem harus mudah di-maintain
- Modular code structure
- Comprehensive documentation
- Logging for debugging
- Version control (Git)
- Automated testing capability
- Clear coding standards (PEP8)

---

### NFR-06: Portability
**Requirement**: Sistem harus portable
- Cross-platform (Windows, Linux, macOS)
- Docker containerization support
- Environment-specific configuration
- Dependency management (requirements.txt)

---

### NFR-07: Security
**Requirement**: Sistem harus secure
- Input validation and sanitization
- SQL injection prevention (if database used)
- HTTPS support
- Rate limiting for API
- Error messages tidak expose sensitive info

---

## 5. Antarmuka Sistem

### 5.1 User Interface
- **Technology**: Streamlit
- **Style**: Clean, modern, professional
- **Colors**: Blue (#1f77b4) as primary
- **Typography**: Sans-serif, readable
- **Layout**: Sidebar navigation + main content area

### 5.2 API Interface
- **Protocol**: HTTP/HTTPS
- **Format**: JSON
- **Authentication**: None (can be added later)
- **Documentation**: Auto-generated (FastAPI Swagger)
- **Versioning**: URL-based (/v1/...)

### 5.3 Hardware Interface
- **Minimum**:
  - CPU: 2 cores
  - RAM: 4GB
  - Storage: 10GB
- **Recommended**:
  - CPU: 4 cores
  - RAM: 8GB
  - Storage: 50GB

### 5.4 Software Interface
- **OS**: Windows 10/11, Ubuntu 20.04+, macOS 11+
- **Python**: 3.11+
- **Browser**: Chrome 90+, Firefox 88+, Safari 14+
- **External APIs**: None (optional: weather API, calendar API)

---

## 6. Use Cases

### UC-01: Train New Model
**Actor**: Admin  
**Precondition**: Dataset available  
**Main Flow**:
1. Admin navigates to project directory
2. Admin runs `python src/train_model.py`
3. System generates dataset if not exists
4. System preprocesses data
5. System trains Random Forest model
6. System trains XGBoost model
7. System evaluates and compares models
8. System saves best model
9. System generates reports

**Postcondition**: Models saved, reports generated

---

### UC-02: Make Daily Prediction (Dashboard)
**Actor**: Manager  
**Precondition**: Model trained  
**Main Flow**:
1. Manager opens dashboard
2. Manager navigates to "Prediksi Volume Sampah"
3. Manager inputs parameters via form
4. Manager clicks "Prediksi Sekarang"
5. System validates inputs
6. System makes prediction
7. System displays results and fleet recommendation

**Postcondition**: Prediction displayed

---

### UC-03: Make Prediction via API
**Actor**: External System  
**Precondition**: Model trained, API running  
**Main Flow**:
1. System sends POST request to /predict/daily
2. API validates request body
3. API makes prediction
4. API returns JSON response

**Postcondition**: Prediction returned

---

### UC-04: Analyze Historical Data
**Actor**: Analyst  
**Precondition**: Dataset loaded  
**Main Flow**:
1. Analyst opens dashboard
2. Analyst navigates to "Analisis Data"
3. System displays dataset preview
4. System displays descriptive statistics
5. System displays various charts
6. Analyst interprets visualizations

**Postcondition**: Insights gained

---

## 7. Constraints

### 7.1 Regulatory Constraints
- Must comply with data privacy regulations
- Must follow government standards for smart city

### 7.2 Technical Constraints
- Python 3.11+ required
- Limited to regression models (no classification)
- Requires historical data

### 7.3 Business Constraints
- Budget limitations
- Timeline: 3 months
- Resource availability

---

## 8. Acceptance Criteria

### 8.1 Functional Acceptance
- ✅ All critical features implemented and working
- ✅ Model accuracy meets target (R² ≥ 0.85, MAPE ≤ 10%)
- ✅ API all endpoints working correctly
- ✅ Dashboard all pages functional

### 8.2 Non-Functional Acceptance
- ✅ Performance targets met
- ✅ System stable (no crashes)
- ✅ Code quality meets standards
- ✅ Documentation complete

### 8.3 User Acceptance
- ✅ UAT completed successfully
- ✅ User feedback positive
- ✅ Training completed
- ✅ Users can perform tasks independently

---

## 9. Appendices

### 9.1 Data Dictionary

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| date | string | YYYY-MM-DD | Date of observation |
| temperature | float | 24-35 | Temperature in Celsius |
| rainfall | float | 0-120 | Rainfall in mm |
| humidity | float | 55-95 | Humidity percentage |
| holiday | int | 0-1 | Holiday flag (0=No, 1=Yes) |
| weekend | int | 0-1 | Weekend flag (0=No, 1=Yes) |
| population_density | float | 3000-15000 | People per km² |
| event_level | int | 0-5 | Event intensity level |
| waste_volume | float | > 0 | Waste volume in tons (target) |

### 9.2 Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 400 | Bad Request | Invalid input parameters |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Model not loaded |

---

**Document Version**: 1.0  
**Author**: Software Engineering Team  
**Date**: 10 Juni 2026  
**Status**: Approved
