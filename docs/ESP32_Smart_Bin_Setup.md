# ESP32 Smart Bin Local Demo

Panduan ini menjelaskan cara memakai ESP32 sebagai sensor smart bin untuk demo lokal. ESP32 mengirim data level sampah ke FastAPI, data disimpan di SQLite, lalu dashboard Streamlit menampilkan status terbaru.

![Workflow ESP32 Smart Bin](assets/esp32-smart-bin-workflow.png)

## Komponen

| Komponen | Estimasi Harga |
|----------|----------------|
| ESP32 DevKit | Rp 70rb |
| Sensor ultrasonik HC-SR04 | Rp 25rb |
| Kabel jumper + breadboard | Rp 30rb |
| Adaptor USB atau powerbank | Rp 80rb |
| **Estimasi total** | **Rp 205rb** |

Harga hanya estimasi untuk prototipe lokal dan bisa berubah tergantung toko atau kualitas komponen.

## Alur Kerja

1. Sensor membaca level sampah.
2. ESP32 mengirim HTTP POST ke FastAPI.
3. FastAPI menerima dan memvalidasi data.
4. SQLite menyimpan riwayat pembacaan.
5. Dashboard Streamlit menampilkan fill level, status, tren, dan tabel data terbaru.
6. Petugas memakai status `low`, `medium`, `high`, atau `full` untuk mengambil tindakan.

## Menjalankan Backend

Aktifkan virtual environment, lalu jalankan API:

```powershell
.\venv\Scripts\activate
uvicorn api.main:app --reload
```

API berjalan di:

```text
http://localhost:8000
```

Jika ESP32 berada di Wi-Fi yang sama, gunakan IP laptop/server, bukan `localhost`. Contoh:

```text
http://192.168.1.100:8000/iot/bin-reading
```

## Keamanan: API Key (opsional tapi disarankan)

Endpoint ingest `POST /iot/bin-reading` bisa dilindungi dengan API key. Set environment variable `IOT_API_KEY` di server sebelum menjalankan API:

```powershell
# Windows (cmd)
set IOT_API_KEY=ganti-dengan-kunci-rahasia
# Linux/macOS
export IOT_API_KEY=ganti-dengan-kunci-rahasia
```

Jika `IOT_API_KEY` di-set, setiap permintaan harus menyertakan header `X-API-Key` dengan nilai yang sama; jika tidak, server menolak dengan `401`. Jika `IOT_API_KEY` tidak di-set (default), pengecekan dilewati agar demo lokal tetap mudah. Pada firmware, isi konstanta `API_KEY` dengan nilai yang sama.

## Test Manual Tanpa ESP32

Kirim data contoh (tanpa API key):

```powershell
curl -X POST http://localhost:8000/iot/bin-reading `
  -H "Content-Type: application/json" `
  -d "{\"bin_id\":\"TPS-001\",\"fill_level\":72.5,\"device_id\":\"ESP32-001\"}"
```

Dengan API key aktif, tambahkan header:

```powershell
curl -X POST http://localhost:8000/iot/bin-reading `
  -H "Content-Type: application/json" `
  -H "X-API-Key: ganti-dengan-kunci-rahasia" `
  -d "{\"bin_id\":\"TPS-001\",\"fill_level\":72.5,\"device_id\":\"ESP32-001\"}"
```

Cek data terbaru:

```powershell
curl http://localhost:8000/iot/bin-readings/latest
```

Cek data terbaru untuk satu bin:

```powershell
curl http://localhost:8000/iot/bin/TPS-001/latest
```

## Dashboard

Jalankan dashboard:

```powershell
streamlit run dashboard/app.py
```

Buka halaman **Smart Bin IoT** untuk melihat:

- bin terbaru
- fill level
- status warna
- device ID
- tren fill level
- tabel riwayat pembacaan

## Firmware ESP32

Firmware demo tersedia di:

```text
firmware/esp32_smart_bin_demo/esp32_smart_bin_demo.ino
```

Sebelum upload ke ESP32, ubah nilai berikut:

```cpp
const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL = "http://192.168.1.100:8000/iot/bin-reading";
const char* API_KEY = "";  // kosongkan jika server tanpa IOT_API_KEY
```

Firmware sudah membaca sensor **HC-SR04 nyata** (bukan simulasi lagi), menyaring noise dengan median beberapa sampel, dan menyimpan pembacaan ke buffer lalu mengirim ulang otomatis jika WiFi sempat putus.

### Wiring HC-SR04

| Pin HC-SR04 | ESP32 |
|-------------|-------|
| VCC | 5V (VIN) |
| GND | GND |
| TRIG | GPIO 5 |
| ECHO | GPIO 18 (pakai voltage divider: ECHO 5V → 3.3V) |

> ⚠️ Pin ECHO mengeluarkan 5V, sedangkan ESP32 hanya aman di 3.3V. Gunakan pembagi tegangan (mis. resistor 1kΩ + 2kΩ) agar pin ESP32 tidak rusak.

### Kalibrasi bin

Sesuaikan dua konstanta dengan tempat sampahmu agar konversi jarak → persen akurat:

```cpp
const float BIN_HEIGHT_CM = 100.0;     // tinggi dalam bin (sensor ke dasar)
const float SENSOR_OFFSET_CM = 4.0;    // zona mati tepat di bawah sensor = 100% penuh
```

Logika: jarak besar = bin kosong (fill rendah), jarak kecil = bin penuh (fill tinggi). Ukur tinggi bin yang sebenarnya dan isi `BIN_HEIGHT_CM`.

## Status

Mapping status:

| Fill Level | Status |
|------------|--------|
| 0 - 39.9% | `low` |
| 40 - 69.9% | `medium` |
| 70 - 89.9% | `high` |
| 90 - 100% | `full` |

## Catatan Lokal Demo

- Endpoint ingest bisa dilindungi API key via `IOT_API_KEY` (lihat bagian Keamanan). Tanpa key, endpoint terbuka — gunakan hanya di jaringan lokal.
- Endpoint baca (`GET`) masih terbuka untuk kemudahan monitoring.
- Database runtime tersimpan di `data/iot_readings.db` (WAL mode) dan diabaikan oleh Git.
- Penulisan konkuren dari banyak ESP32 sudah diuji aman (lihat `tests/test_iot_concurrency.py`).
- Fitur ini belum mengubah model ML; ini menambahkan monitoring smart bin real-time di samping sistem prediksi. Rencana menggabungkan ke ML dibahas di `IoT_ML_Integration_Proposal.md`.
