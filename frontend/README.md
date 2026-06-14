# Dispatch — Dashboard React

Antarmuka React + Tailwind untuk Sistem Prediksi Volume Sampah. **Berdampingan** dengan
dashboard Streamlit (tidak menggantikannya) dan mengambil semua data lewat REST API FastAPI.

## Prasyarat

- Node.js 18+ dan npm
- Backend FastAPI berjalan (lihat root project):

  ```bash
  # dari root project
  venv/Scripts/activate           # Windows
  uvicorn api.main:app --reload   # API di http://localhost:8000
  ```

## Menjalankan (mode pengembangan)

```bash
cd frontend
npm install        # sekali saja
npm run dev        # http://localhost:5173
```

Saat dev, request ke `/api/*` otomatis di-proxy ke `http://localhost:8000`
(diatur di `vite.config.ts`), jadi tidak ada masalah CORS.

## Build produksi

```bash
npm run build      # output ke dist/
npm run preview    # pratinjau hasil build
```

Untuk produksi, arahkan ke backend lewat env var (browser memanggil URL ini langsung):

```bash
# frontend/.env.production
VITE_API_BASE=https://api.contoh.go.id
```

Tanpa `VITE_API_BASE`, klien memakai `/api` (cocok untuk proxy/reverse-proxy).

## Catatan integrasi backend

Dashboard ini memakai endpoint **read-only** yang ditambahkan ke `api/main.py`
(tidak mengubah logika ML):

| Endpoint | Kegunaan |
|----------|----------|
| `GET /health` | Indikator koneksi & status model di status bar |
| `GET /stats/overview` | Statistik utama + tren 90 hari + fitur terbaru (prediksi cepat) |
| `GET /stats/analysis` | Distribusi, rata-rata per hari, tren bulanan, korelasi |
| `GET /model/performance` | Metrik, feature importance, perbandingan model, laporan |
| `GET /model/*.png` | Gambar laporan evaluasi |
| `POST /predict/{daily,weekly,monthly}` | Prediksi (halaman Prediksi & Dashboard) |
| `POST /export/prediction` | Unduh Excel/PDF |
| `GET /iot/bin-readings/latest` | Data smart bin (halaman IoT) |

`ALLOWED_ORIGINS` di backend sudah menyertakan origin Vite (`5173`/`4173`) secara default.

## Arah desain

"Dispatch Board" — konsol operasi depo: dasar slate-teal gelap, aksen amber sinyal,
warna status isi (rendah/sedang/tinggi/penuh) yang fungsional. Tipografi Space Grotesk +
IBM Plex Sans + IBM Plex Mono. Elemen khas: **Capacity Gauge** (meteran isi vertikal)
yang dipakai ulang di halaman IoT dan Prediksi.

## Struktur

```
frontend/src/
  components/   Layout, Panel, CapacityGauge (signature), StatusPill, chart, states
  lib/          api.ts (klien + tipe), useAsync.ts, format.ts
  pages/        Dashboard, DataAnalysis, Prediction, SmartBinIot, ModelPerformance, About
  index.css     token desain Tailwind v4 (@theme) + base + animasi
```
