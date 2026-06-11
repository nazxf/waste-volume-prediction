# User Manual
## Sistem Prediksi Volume Sampah Kota

---

## Daftar Isi

1. [Pendahuluan](#1-pendahuluan)
2. [Instalasi Sistem](#2-instalasi-sistem)
3. [Menjalankan Training Model](#3-menjalankan-training-model)
4. [Menggunakan Dashboard](#4-menggunakan-dashboard)
5. [Menggunakan REST API](#5-menggunakan-rest-api)
6. [Troubleshooting](#6-troubleshooting)
7. [FAQ](#7-faq)

---

## 1. Pendahuluan

### 1.1 Tentang Sistem
Sistem Prediksi Volume Sampah adalah aplikasi berbasis Machine Learning yang dirancang untuk memprediksi volume sampah harian, mingguan, dan bulanan di wilayah perkotaan. Sistem ini membantu mengoptimalkan operasional pengangkutan sampah dan mengurangi biaya operasional.

### 1.2 Fitur Utama
- ✅ Prediksi volume sampah harian, mingguan, dan bulanan
- ✅ Rekomendasi jumlah armada optimal
- ✅ Dashboard interaktif untuk visualisasi data
- ✅ REST API untuk integrasi sistem
- ✅ Analisis data historis
- ✅ Laporan evaluasi model

### 1.3 Persyaratan Sistem
- **Sistem Operasi**: Windows 10/11, Ubuntu 20.04+, atau macOS 11+
- **Python**: Versi 3.11 atau lebih tinggi
- **RAM**: Minimal 4GB (Rekomendasi: 8GB)
- **Storage**: Minimal 10GB ruang kosong
- **Browser**: Chrome 90+, Firefox 88+, atau Safari 14+
- **Internet**: Untuk instalasi dependencies

---

## 2. Instalasi Sistem

### 2.1 Instalasi Python

**Windows:**
1. Download Python dari https://www.python.org/downloads/
2. Jalankan installer
3. ✅ Centang "Add Python to PATH"
4. Klik "Install Now"
5. Verifikasi instalasi:
   ```cmd
   python --version
   ```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
python3.11 --version
```

**macOS:**
```bash
brew install python@3.11
python3.11 --version
```

### 2.2 Download Project

**Opsi 1: Clone dari Git (jika tersedia)**
```bash
git clone <repository-url>
cd waste-volume-prediction
```

**Opsi 2: Extract dari ZIP**
1. Extract file `waste-volume-prediction.zip`
2. Buka terminal/command prompt
3. Navigate ke folder:
   ```bash
   cd waste-volume-prediction
   ```

### 2.3 Membuat Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3.11 -m venv venv
source venv/bin/activate
```

Setelah aktivasi, prompt akan berubah menjadi:
```
(venv) C:\Users\...\waste-volume-prediction>
```

### 2.4 Instalasi Dependencies

Dengan virtual environment aktif, jalankan:

```bash
pip install -r requirements.txt
```

Proses instalasi akan mengunduh dan menginstall semua library yang diperlukan:
- pandas, numpy (data processing)
- scikit-learn, xgboost (machine learning)
- matplotlib, seaborn (visualization)
- streamlit (dashboard)
- fastapi, uvicorn (API server)

**Waktu instalasi**: ±5-10 menit tergantung kecepatan internet

### 2.5 Verifikasi Instalasi

Cek apakah semua dependencies terinstall:
```bash
pip list
```

Anda harus melihat semua packages dari requirements.txt terinstall.

---

## 3. Menjalankan Training Model

### 3.1 Generate Dataset dan Training Model

**Langkah 1: Jalankan Training Script**

```bash
python src/train_model.py
```

**Proses yang terjadi:**
1. ✅ Cek keberadaan dataset
2. ✅ Generate dataset sintetis jika belum ada (5 tahun data: 2020-2024)
3. ✅ Preprocessing data (feature engineering, train-test split)
4. ✅ Training Random Forest model
5. ✅ Training XGBoost model
6. ✅ Evaluasi dan perbandingan model
7. ✅ Simpan model terbaik
8. ✅ Generate laporan evaluasi
9. ✅ Generate visualisasi feature importance

**Waktu eksekusi**: ±3-5 menit

**Output yang dihasilkan:**
```
models/
├── random_forest.pkl          # Model Random Forest
├── xgboost.pkl               # Model XGBoost
├── best_model.pkl            # Model terbaik
└── feature_columns.pkl       # Metadata fitur

reports/
├── evaluation_report.md      # Laporan evaluasi
├── feature_importance.png    # Chart feature importance
└── prediction_comparison.png # Chart perbandingan prediksi
```

### 3.2 Membaca Hasil Training

Setelah training selesai, terminal akan menampilkan:

```
============================================================
TRAINING COMPLETED SUCCESSFULLY!
============================================================

📊 Best Model: XGBoost
   RMSE: 3.2456 tons
   R²: 0.9234
   MAPE: 4.12%

💾 Models saved to: D:\project\waste-volume-prediction\models
📈 Reports saved to: D:\project\waste-volume-prediction\reports

✅ You can now run the dashboard:
   streamlit run dashboard/app.py

✅ Or start the API server:
   uvicorn api.main:app --reload
============================================================
```

### 3.3 Retraining Model

Model perlu di-retrain secara berkala (setiap 3-6 bulan) dengan data terbaru untuk menjaga akurasi.

**Langkah retraining:**
1. Update file `data/raw/waste_dataset.csv` dengan data baru
2. Jalankan kembali training script:
   ```bash
   python src/train_model.py
   ```
3. Model lama akan di-overwrite dengan model baru

---

## 4. Menggunakan Dashboard

### 4.1 Menjalankan Dashboard

**Pastikan virtual environment aktif**, kemudian jalankan:

```bash
streamlit run dashboard/app.py
```

Dashboard akan otomatis terbuka di browser pada:
```
http://localhost:8501
```

Jika tidak terbuka otomatis, buka browser dan ketik URL di atas.

### 4.2 Navigasi Dashboard

Dashboard memiliki 5 halaman utama yang dapat diakses melalui sidebar:

#### 🏠 Dashboard Utama
Halaman overview dengan:
- **Statistik Utama**: Rata-rata volume, total data, volume max/min
- **Prediksi Cepat**: Prediksi harian, mingguan, bulanan berdasarkan data terbaru
- **Rekomendasi Armada**: Jumlah truk yang direkomendasikan
- **Tren Volume**: Grafik volume sampah 90 hari terakhir

#### 📊 Analisis Data
Halaman untuk eksplorasi data dengan:
- **Preview Dataset**: Tampilan 20 baris pertama dataset
- **Statistik Deskriptif**: Mean, median, std, min, max untuk setiap kolom
- **Distribusi Volume**: Histogram distribusi volume sampah
- **Volume per Hari**: Bar chart rata-rata volume per hari (Senin-Minggu)
- **Tren Bulanan**: Line chart rata-rata volume per bulan
- **Heatmap Korelasi**: Korelasi antar variabel

#### 🔮 Prediksi Volume Sampah
Halaman untuk membuat prediksi custom dengan:

**Form Input:**
1. **Tanggal**: Pilih tanggal untuk prediksi
2. **Suhu (°C)**: 24-35°C (slider)
3. **Curah Hujan (mm)**: 0-120mm (slider)
4. **Kelembaban (%)**: 55-95% (slider)
5. **Hari Libur**: Ya/Tidak (dropdown)
6. **Akhir Pekan**: Ya/Tidak (dropdown)
7. **Kepadatan Penduduk**: 3000-15000 jiwa/km² (number input)
8. **Tingkat Event**: 0-5 (slider)

**Cara Menggunakan:**
1. Isi semua parameter sesuai kondisi yang ingin diprediksi
2. Klik tombol **"🚀 Prediksi Sekarang"**
3. Sistem akan menampilkan:
   - Prediksi harian (dalam ton)
   - Prediksi mingguan total (7 hari)
   - Prediksi bulanan total (30 hari)
   - Rekomendasi jumlah armada
   - Chart breakdown prediksi mingguan

**Contoh Penggunaan:**
```
Tanggal: 2025-06-15
Suhu: 30°C
Curah Hujan: 10mm
Kelembaban: 75%
Hari Libur: Tidak
Akhir Pekan: Ya (Sabtu)
Kepadatan Penduduk: 9500
Tingkat Event: 2

→ Hasil:
  Prediksi Harian: 85.23 ton
  Prediksi Mingguan: 567.89 ton
  Prediksi Bulanan: 2,435.67 ton
  Rekomendasi: 11 truk (utilisasi 96.9%)
```

#### ⚡ Performa Model
Halaman untuk melihat evaluasi model:
- **Laporan Evaluasi**: Metrik lengkap (MAE, RMSE, R², MAPE)
- **Feature Importance**: Chart fitur mana yang paling berpengaruh
- **Perbandingan Prediksi**: Scatter plot actual vs predicted

#### ℹ️ Tentang Sistem
Halaman informasi lengkap tentang sistem, teknologi, dan manfaat.

### 4.3 Tips Penggunaan Dashboard

**💡 Best Practices:**
1. **Prediksi Reguler**: Lakukan prediksi setiap malam untuk hari besok
2. **Analisis Trend**: Gunakan halaman Analisis Data untuk memahami pola
3. **Validasi Prediksi**: Bandingkan prediksi dengan actual untuk monitoring akurasi
4. **Export Data**: Screenshot atau print laporan untuk dokumentasi

**⚠️ Catatan Penting:**
- Dashboard hanya bisa diakses saat script streamlit berjalan
- Jangan tutup terminal/command prompt saat menggunakan dashboard
- Untuk stop dashboard: Tekan `Ctrl+C` di terminal

---

## 5. Menggunakan REST API

### 5.1 Menjalankan API Server

**Di terminal baru** (biarkan dashboard tetap jalan jika diperlukan):

```bash
uvicorn api.main:app --reload
```

API server akan berjalan di:
```
http://localhost:8000
```

**API Documentation** otomatis tersedia di:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 5.2 Endpoint API

#### GET /
**Deskripsi**: Informasi API  
**Response**:
```json
{
  "api_name": "Waste Volume Prediction API",
  "version": "1.0.0",
  "status": "operational"
}
```

#### GET /health
**Deskripsi**: Health check  
**Response**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "message": "API is running and model is loaded"
}
```

#### POST /predict/daily
**Deskripsi**: Prediksi harian  
**Request Body**:
```json
{
  "date": "2025-06-15",
  "temperature": 30.5,
  "rainfall": 5.0,
  "humidity": 75.0,
  "holiday": 0,
  "weekend": 1,
  "population_density": 9500.0,
  "event_level": 2
}
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

#### POST /predict/weekly
**Deskripsi**: Prediksi mingguan (7 hari)  
**Request Body**: Sama seperti daily  
**Response**:
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
    ...
  ]
}
```

#### POST /predict/monthly
**Deskripsi**: Prediksi bulanan (30 hari)  
**Request Body**: Sama seperti daily  
**Response**: Sama seperti weekly, tapi 30 hari

### 5.3 Contoh Pemanggilan API

#### Menggunakan cURL (Command Line)

**Windows (PowerShell):**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/predict/daily" -Method POST -Body (@{
    date = "2025-06-15"
    temperature = 30.5
    rainfall = 5.0
    humidity = 75.0
    holiday = 0
    weekend = 1
    population_density = 9500.0
    event_level = 2
} | ConvertTo-Json) -ContentType "application/json"
```

**Linux/macOS:**
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

#### Menggunakan Python

```python
import requests

url = "http://localhost:8000/predict/daily"
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

response = requests.post(url, json=data)
print(response.json())
```

#### Menggunakan JavaScript (Node.js)

```javascript
const axios = require('axios');

const data = {
  date: "2025-06-15",
  temperature: 30.5,
  rainfall: 5.0,
  humidity: 75.0,
  holiday: 0,
  weekend: 1,
  population_density: 9500.0,
  event_level: 2
};

axios.post('http://localhost:8000/predict/daily', data)
  .then(response => console.log(response.data))
  .catch(error => console.error(error));
```

---

## 6. Troubleshooting

### 6.1 Masalah Instalasi

**Problem**: `pip install -r requirements.txt` gagal

**Solusi**:
1. Pastikan virtual environment aktif
2. Update pip:
   ```bash
   python -m pip install --upgrade pip
   ```
3. Install dependencies satu per satu jika ada yang gagal:
   ```bash
   pip install pandas numpy scikit-learn xgboost matplotlib seaborn streamlit fastapi uvicorn joblib pydantic
   ```

**Problem**: Python version tidak sesuai

**Solusi**:
```bash
# Cek versi Python
python --version

# Jika < 3.11, install Python 3.11+
# Windows: Download dari python.org
# Linux: sudo apt install python3.11
# macOS: brew install python@3.11
```

### 6.2 Masalah Training

**Problem**: `FileNotFoundError: Dataset not found`

**Solusi**: Script seharusnya otomatis generate dataset. Jika masih error:
```bash
python src/data_generator.py
```

**Problem**: Training sangat lambat

**Solusi**:
1. Pastikan RAM cukup (minimal 4GB)
2. Tutup aplikasi lain
3. Reduce dataset size (edit parameter di data_generator.py)

**Problem**: Model accuracy rendah (R² < 0.80)

**Solusi**:
1. Cek kualitas data (no missing values, realistic values)
2. Increase training data (tambah tahun di data generator)
3. Tune hyperparameters di train_model.py

### 6.3 Masalah Dashboard

**Problem**: Dashboard tidak terbuka

**Solusi**:
1. Cek terminal, ada error message?
2. Pastikan port 8501 tidak digunakan aplikasi lain
3. Coba buka manual: http://localhost:8501
4. Ganti port:
   ```bash
   streamlit run dashboard/app.py --server.port 8502
   ```

**Problem**: "Model not found" di dashboard

**Solusi**: Jalankan training terlebih dahulu:
```bash
python src/train_model.py
```

**Problem**: Chart tidak muncul

**Solusi**:
1. Clear browser cache
2. Refresh halaman (F5)
3. Cek console browser (F12) untuk error

### 6.4 Masalah API

**Problem**: API tidak bisa diakses

**Solusi**:
1. Pastikan uvicorn running di terminal
2. Cek port 8000 tidak digunakan
3. Test dengan browser: http://localhost:8000

**Problem**: API returns 503 "Model not loaded"

**Solusi**: Train model terlebih dahulu:
```bash
python src/train_model.py
```

**Problem**: API returns 400 "Bad Request"

**Solusi**: Cek request body Anda, pastikan:
- Semua field required ada
- Tipe data sesuai (float untuk temperature, int untuk holiday)
- Values dalam range valid
- Date format YYYY-MM-DD

### 6.5 Masalah Umum

**Problem**: `ModuleNotFoundError: No module named 'xxx'`

**Solusi**:
1. Pastikan virtual environment aktif
2. Install module yang missing:
   ```bash
   pip install xxx
   ```

**Problem**: Permission denied

**Solusi**:
- Windows: Run command prompt as Administrator
- Linux/macOS: Gunakan sudo atau fix permissions:
  ```bash
  chmod -R 755 waste-volume-prediction/
  ```

**Problem**: Out of memory

**Solusi**:
1. Tutup aplikasi lain
2. Reduce data size
3. Upgrade RAM jika memungkinkan

---

## 7. FAQ

### 7.1 Pertanyaan Umum

**Q: Berapa lama waktu training model?**  
A: ±3-5 menit untuk dataset 5 tahun. Tergantung spesifikasi komputer.

**Q: Apakah bisa mengganti dataset dengan data real?**  
A: Ya! Replace file `data/raw/waste_dataset.csv` dengan data Anda. Pastikan format dan kolom sesuai.

**Q: Berapa sering model perlu di-retrain?**  
A: Disarankan setiap 3-6 bulan dengan data terbaru untuk menjaga akurasi.

**Q: Bagaimana menjalankan automated retraining?**  
A: Jalankan `python src/retrain.py --reason scheduled`. Jika memakai CSV baru, gunakan `python src/retrain.py --data-path path/to/waste_dataset.csv --reason new-data`.

**Q: Apakah bisa prediksi lebih dari 30 hari?**  
A: Bisa dimodifikasi di `src/predict.py`, tapi akurasi akan menurun untuk periode yang lebih panjang.

**Q: Bagaimana cara export hasil prediksi?**  
A: Di halaman prediksi dashboard, gunakan tombol Weekly/Monthly Excel atau PDF. Untuk export programmatic, gunakan endpoint `/export/prediction`.

### 7.2 Pertanyaan Teknis

**Q: Algoritma apa yang digunakan?**  
A: Random Forest, XGBoost, dan ensemble voting. Sistem otomatis memilih model terbaik berdasarkan RMSE.

**Q: Apa itu feature importance?**  
A: Ranking fitur yang paling berpengaruh terhadap prediksi. Contoh: population_density mungkin paling penting.

**Q: Bagaimana cara mengintegrasikan dengan sistem existing?**  
A: Gunakan REST API. Sistem Anda bisa call endpoint /predict/daily dengan HTTP POST.

**Q: Apakah support multi-region?**  
A: Ya, train model terpisah untuk setiap region dengan data region tersebut.

**Q: Bagaimana cara menambah fitur baru?**  
A: Edit `src/preprocess.py` untuk feature engineering dan `src/train_model.py` untuk training.

### 7.3 Pertanyaan Bisnis

**Q: Berapa tingkat akurasi sistem?**  
A: Target R² ≥ 0.85 dan MAPE ≤ 10%. Actual tergantung kualitas data.

**Q: Berapa penghematan biaya yang bisa dicapai?**  
A: Estimasi 20-30% dari biaya operasional transportasi melalui optimasi armada.

**Q: Apakah perlu koneksi internet untuk operasional?**  
A: Tidak, setelah instalasi sistem bisa jalan offline. Internet hanya untuk instalasi dependencies.

**Q: Berapa biaya lisensi?**  
A: Sistem ini open source, tidak ada biaya lisensi. Semua library yang digunakan gratis.

---

## 8. Kontak Support

Untuk bantuan lebih lanjut:
- **Email**: support@wastepredict.com
- **Documentation**: Lihat folder `docs/`
- **Issue Tracker**: [GitHub Issues]

---

**User Manual Version**: 1.0  
**Last Updated**: 10 Juni 2026  
**Next Review**: Quarterly

---

**Tips Terakhir:**
- 💾 Backup data dan model secara berkala
- 📊 Monitor performa model dengan data real
- 🔄 Update sistem secara reguler
- 📚 Baca dokumentasi lengkap untuk fitur advanced

**Selamat menggunakan Sistem Prediksi Volume Sampah!** 🎉
