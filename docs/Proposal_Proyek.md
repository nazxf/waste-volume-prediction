# Proposal Proyek
## Sistem Prediksi Volume Sampah Kota Menggunakan Machine Learning

---

## 1. Judul Proyek

**Sistem Prediksi Volume Sampah Kota Menggunakan Algoritma Random Forest dan XGBoost untuk Optimasi Pengangkutan Sampah**

---

## 2. Latar Belakang

Pengelolaan sampah merupakan salah satu tantangan terbesar yang dihadapi kota-kota besar di Indonesia. Volume sampah yang dihasilkan setiap harinya sangat bervariasi dan dipengaruhi oleh berbagai faktor seperti cuaca, hari libur, kepadatan penduduk, dan event khusus. Ketidakpastian ini menyebabkan kesulitan dalam perencanaan pengangkutan sampah yang efisien.

Permasalahan yang sering terjadi:
- **Kelebihan armada** pada hari dengan volume sampah rendah, menyebabkan pemborosan biaya operasional
- **Kekurangan armada** pada hari dengan volume sampah tinggi, menyebabkan penumpukan sampah
- **Ketidakpastian perencanaan** membuat sulit untuk melakukan optimasi rute dan jadwal pengangkutan
- **Dampak lingkungan** dari sampah yang tidak terangkut tepat waktu

---

## 3. Permasalahan Industri

### 3.1 Tantangan Operasional
- Volume sampah harian yang tidak dapat diprediksi dengan akurat
- Kesulitan menentukan jumlah armada optimal untuk setiap hari
- Biaya operasional tinggi akibat deployment armada yang tidak efisien
- Keterlambatan pengangkutan pada periode volume tinggi

### 3.2 Dampak Finansial
- Biaya bahan bakar yang tidak efisien
- Biaya tenaga kerja yang tidak optimal
- Potensi denda dari pemerintah akibat pelayanan yang buruk
- Kehilangan reputasi perusahaan

### 3.3 Dampak Sosial dan Lingkungan
- Penumpukan sampah di TPS (Tempat Pembuangan Sementara)
- Pencemaran lingkungan dan bau tidak sedap
- Risiko kesehatan masyarakat
- Keluhan warga terhadap pelayanan

---

## 4. Tujuan Proyek

### 4.1 Tujuan Utama
Membangun sistem prediksi volume sampah berbasis Machine Learning yang dapat memprediksi volume sampah harian, mingguan, dan bulanan dengan akurasi tinggi untuk mendukung pengambilan keputusan operasional.

### 4.2 Tujuan Spesifik
1. Mengembangkan model prediksi dengan akurasi minimal 85% (R² ≥ 0.85)
2. Memberikan rekomendasi jumlah armada optimal berdasarkan prediksi volume
3. Menyediakan dashboard interaktif untuk monitoring dan analisis
4. Menyediakan REST API untuk integrasi dengan sistem lain
5. Mengurangi biaya operasional hingga 20-30% melalui optimasi armada

---

## 5. Solusi Artificial Intelligence

### 5.1 Pendekatan Machine Learning
Sistem ini menggunakan **algoritma ensemble learning** dengan dua model utama:

1. **Random Forest Regressor**
   - Algoritma berbasis pohon keputusan ensemble
   - Robust terhadap outliers dan noise
   - Dapat menangani fitur non-linear
   - Parameter: 200 estimators, max_depth=12

2. **XGBoost Regressor**
   - Gradient boosting framework yang powerful
   - Performa tinggi dan training yang cepat
   - Built-in regularization untuk menghindari overfitting
   - Parameter: 300 estimators, learning_rate=0.05

### 5.2 Fitur Input Model
Model memprediksi berdasarkan fitur-fitur berikut:
- **Cuaca**: Temperature, rainfall, humidity
- **Kalender**: Day, month, year, day_of_week, week_of_year
- **Status hari**: Holiday, weekend, is_month_start, is_month_end
- **Demografi**: Population density
- **Event**: Event level (0-5)

### 5.3 Output Model
- Prediksi volume sampah dalam ton
- Rekomendasi jumlah armada (truk)
- Tingkat utilisasi armada
- Confidence interval prediksi

---

## 6. Manfaat Sistem

### 6.1 Manfaat Operasional
✅ **Efisiensi Armada**: Deployment armada yang tepat sesuai kebutuhan  
✅ **Optimasi Rute**: Perencanaan rute berdasarkan prediksi volume  
✅ **Scheduling Optimal**: Penjadwalan yang lebih akurat  
✅ **Monitoring Real-time**: Dashboard untuk monitoring volume sampah

### 6.2 Manfaat Finansial
💰 **Penghematan Biaya Operasional**: 20-30% dari biaya transportasi  
💰 **Efisiensi Bahan Bakar**: Penggunaan armada yang tepat  
💰 **Optimasi SDM**: Alokasi tenaga kerja yang lebih baik  
💰 **ROI Positif**: Estimasi payback period 6-12 bulan

### 6.3 Manfaat Lingkungan dan Sosial
🌱 **Lingkungan Bersih**: Pengangkutan tepat waktu mencegah penumpukan  
🌱 **Kesehatan Masyarakat**: Mengurangi risiko penyakit dari sampah  
🌱 **Kepuasan Warga**: Pelayanan yang lebih baik  
🌱 **Smart City**: Kontribusi terhadap visi kota cerdas

---

## 7. Target Pengguna

### 7.1 Pengguna Primer
- **Dinas Lingkungan Hidup Kota/Kabupaten**
  - Perencanaan dan monitoring operasional
  - Pengambilan keputusan strategis
  
- **Perusahaan Pengelola Sampah**
  - Optimasi armada dan rute
  - Efisiensi operasional

### 7.2 Pengguna Sekunder
- **Tim Smart City**
  - Integrasi dengan platform smart city
  - Analisis data kota
  
- **Tim Perencanaan Kota**
  - Data untuk perencanaan infrastruktur
  - Proyeksi kebutuhan masa depan

---

## 8. Batasan Sistem

### 8.1 Batasan Teknis
- Memerlukan data historis minimal 1 tahun untuk training optimal
- Prediksi didasarkan pada pola historis, mungkin kurang akurat untuk kondisi ekstrem yang belum pernah terjadi
- Memerlukan retraining berkala (3-6 bulan) dengan data terbaru
- Akurasi prediksi menurun untuk periode lebih dari 30 hari

### 8.2 Batasan Fungsional
- Sistem tidak memprediksi jenis sampah (organik, anorganik, B3)
- Tidak termasuk optimasi rute pengangkutan (dapat dikembangkan fase 2)
- Tidak terintegrasi dengan IoT sensors (dapat dikembangkan fase 2)

---

## 9. Metodologi Pengembangan

### 9.1 Fase 1: Data Collection & Preparation (2 minggu)
- Pengumpulan data historis volume sampah
- Data cuaca dari BMKG
- Data kalender dan hari libur
- Data demografi dari BPS
- Cleaning dan preprocessing data

### 9.2 Fase 2: Model Development (3 minggu)
- Exploratory Data Analysis (EDA)
- Feature engineering
- Model training dan tuning
- Model evaluation dan selection
- Cross-validation

### 9.3 Fase 3: System Development (3 minggu)
- Dashboard development (Streamlit)
- REST API development (FastAPI)
- Integration testing
- Documentation

### 9.4 Fase 4: Deployment & Testing (2 minggu)
- User acceptance testing (UAT)
- Performance testing
- Deployment ke production
- User training

### 9.5 Fase 5: Monitoring & Maintenance (Ongoing)
- Model monitoring
- Retraining berkala
- System maintenance
- Feature enhancement

---

## 10. Spesifikasi Teknis

### 10.1 Technology Stack
- **Backend**: Python 3.11
- **ML Framework**: Scikit-Learn, XGBoost
- **Data Processing**: Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Dashboard**: Streamlit
- **API**: FastAPI, Uvicorn
- **Model Storage**: Joblib

### 10.2 Infrastructure Requirements
- **Server**: Minimal 4 CPU cores, 8GB RAM
- **Storage**: 50GB untuk data dan model
- **OS**: Linux/Windows Server
- **Python**: Version 3.11 atau lebih tinggi

---

## 11. Estimasi Biaya dan Waktu

### 11.1 Timeline
- **Total Durasi**: 10 minggu (2.5 bulan)
- **Fase Development**: 8 minggu
- **Fase Testing & Deployment**: 2 minggu

### 11.2 Resources
- **Data Scientist**: 1 orang (full-time)
- **Backend Developer**: 1 orang (full-time)
- **DevOps Engineer**: 1 orang (part-time)
- **UI/UX Designer**: 1 orang (part-time)

---

## 12. Metrik Keberhasilan

### 12.1 Technical Metrics
- **Model Accuracy**: R² Score ≥ 0.85
- **Prediction Error**: MAPE ≤ 10%
- **API Response Time**: < 200ms
- **System Uptime**: ≥ 99%

### 12.2 Business Metrics
- **Cost Reduction**: 20-30% biaya operasional
- **Fleet Utilization**: ≥ 85%
- **On-time Collection**: ≥ 95%
- **User Satisfaction**: ≥ 4/5 rating

---

## 13. Risiko dan Mitigasi

| Risiko | Dampak | Probabilitas | Mitigasi |
|--------|--------|--------------|----------|
| Data historis tidak lengkap | High | Medium | Gunakan data sintetis + real data minimal 6 bulan |
| Model overfitting | Medium | Medium | Cross-validation dan regularization |
| API downtime | High | Low | Load balancing dan failover mechanism |
| User resistance | Medium | Medium | Training dan change management |

---

## 14. Kesimpulan

Sistem Prediksi Volume Sampah menggunakan Machine Learning merupakan solusi inovatif untuk mengatasi tantangan pengelolaan sampah kota. Dengan memanfaatkan algoritma Random Forest dan XGBoost, sistem ini dapat memberikan prediksi akurat yang mendukung optimasi operasional, penghematan biaya, dan peningkatan kualitas layanan.

Investasi dalam sistem ini diharapkan memberikan ROI positif dalam waktu 6-12 bulan melalui efisiensi operasional dan penghematan biaya. Selain manfaat finansial, sistem ini juga berkontribusi terhadap lingkungan yang lebih bersih dan kesehatan masyarakat yang lebih baik.

---

## 15. Rekomendasi

1. **Segera dimulai**: Proyek ini sangat relevan dengan kebutuhan operasional saat ini
2. **Pilot project**: Mulai dengan satu wilayah sebagai proof of concept
3. **Skalabilitas**: Design sistem yang dapat di-scale untuk wilayah lebih luas
4. **Integrasi**: Rencanakan integrasi dengan sistem existing
5. **Continuous improvement**: Lakukan monitoring dan improvement berkelanjutan

---

**Diajukan oleh**: Tim Data Science & Engineering  
**Tanggal**: 10 Juni 2026  
**Status**: Proposal untuk Persetujuan
