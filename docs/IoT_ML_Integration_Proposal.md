# Proposal: Integrasi Data IoT Smart Bin ke Model Prediksi ML

> **Status:** Usulan / bahan diskusi (belum dikerjakan)
> **Dibuat:** 2026-06-14
> **Konteks:** Saat ini sistem IoT smart bin (ESP32) dan model prediksi volume sampah (ML) berjalan **terpisah**. Dokumen ini membahas opsi menggabungkan keduanya ("Pilihan B").

---

## 1. Ringkasan untuk Pengambil Keputusan

Saat ini ada dua sistem dalam satu proyek yang **tidak saling terhubung**:

- **Sistem A — Prediksi ML:** menebak volume sampah (ton) dari cuaca, kalender, kepadatan penduduk, dan event level.
- **Sistem B — Smart Bin IoT:** sensor ESP32 melaporkan level penuh tempat sampah (%), ditampilkan di dashboard untuk monitoring.

Data sensor (Sistem B) **tidak pernah dipakai** sebagai masukan ke model prediksi (Sistem A). Artinya, walau 50 tempat sampah melaporkan "penuh", prediksi volume tidak berubah sama sekali.

**Proposal ini:** memakai data sensor IoT untuk membuat prediksi lebih akurat dan responsif terhadap kondisi lapangan nyata.

**Rekomendasi tim teknis:** kerjakan **setelah** monitoring IoT dasar (Pilihan A) berjalan stabil dan data sensor terkumpul beberapa minggu. Integrasi ini **butuh data historis sensor** yang saat ini belum ada.

---

## 2. Analogi Sederhana

| | Tanpa integrasi (sekarang) | Dengan integrasi (proposal) |
|---|---|---|
| Perumpamaan | CCTV: hanya melihat keadaan sekarang | CCTV yang juga bisa meramal dari pola yang dilihat |
| Contoh | Prediksi tetap 80 ton walau semua bin penuh sejak pagi | Sistem melihat "semua bin penuh sejak pagi" lalu koreksi prediksi jadi ~90 ton |

---

## 3. Manfaat yang Diharapkan

1. **Prediksi lebih akurat** — model belajar dari kondisi nyata di lapangan, bukan hanya faktor cuaca/kalender.
2. **Koreksi real-time** — prediksi bisa disesuaikan ketika pola pengisian bin menyimpang dari biasanya (mis. ada keramaian tak terduga).
3. **Validasi model** — data fill-level aktual bisa dipakai mengukur apakah prediksi ML benar di dunia nyata (saat ini model hanya diuji pada data sintetis).
4. **Deteksi dini** — lonjakan fill-level mendadak bisa jadi sinyal awal volume tinggi sebelum truk dikerahkan.

---

## 4. Apa yang Dibutuhkan (Prasyarat)

Integrasi ini **tidak bisa langsung** karena memerlukan:

1. **Data sensor historis** — minimal beberapa minggu pengumpulan data fill-level nyata dari bin yang beroperasi. Database `data/iot_readings.db` saat ini masih kosong / hanya data demo.
2. **Cakupan sensor yang representatif** — idealnya sensor terpasang di sejumlah titik yang mewakili area, bukan hanya 1-2 bin demo.
3. **Konsistensi data** — sensor harus terkalibrasi & andal (lihat catatan kualitas data di bawah), karena data sampah yang buruk akan menurunkan kualitas model ("garbage in, garbage out").
4. **Label yang bisa dipertanggungjawabkan** — perlu cara menghubungkan agregat fill-level dengan volume sampah aktual (mis. data timbangan truk) agar model bisa belajar hubungan yang benar.

---

## 5. Pendekatan Teknis (Opsi)

Ada beberapa cara menggabungkan, dari yang paling sederhana ke paling kompleks:

### Opsi 5.1 — Fitur tambahan (paling sederhana, direkomendasikan untuk awal)
Tambahkan ringkasan harian data sensor sebagai **fitur baru** ke model yang sudah ada. Contoh fitur:
- `avg_fill_level_today` — rata-rata level penuh semua bin hari ini
- `pct_bins_full` — persentase bin berstatus `full`
- `fill_rate` — seberapa cepat bin terisi (delta per jam)

Lalu latih ulang model dengan fitur tambahan ini. **Perubahan kecil** pada `preprocess.py` dan `predict.py`.

> Catatan: fitur ini hanya tersedia untuk prediksi **hari ini / jangka sangat pendek**, karena untuk prediksi masa depan kita belum tahu fill-level masa depan.

### Opsi 5.2 — Model koreksi (post-processing)
Biarkan model ML utama seperti sekarang, lalu tambahkan **lapisan koreksi** yang menyesuaikan hasil prediksi berdasarkan deviasi fill-level aktual vs ekspektasi. Lebih fleksibel, tidak mengubah model inti.

### Opsi 5.3 — Model deret waktu nowcasting (paling kompleks)
Bangun model terpisah yang khusus memakai aliran data sensor real-time untuk "nowcasting" (estimasi kondisi saat ini & beberapa jam ke depan). Memerlukan arsitektur & data yang jauh lebih besar.

---

## 6. Rencana Bertahap yang Disarankan

```
Tahap 1 (SEKARANG)   : Jalankan monitoring IoT dasar (Pilihan A).
                       Sensor -> API -> SQLite -> Dashboard. Kumpulkan data.

Tahap 2 (2-4 minggu)  : Akumulasi data fill-level nyata dari bin operasional.
                       Pastikan sensor andal & terkalibrasi.

Tahap 3 (analisis)    : Cek apakah ada korelasi antara agregat fill-level
                       dan volume sampah aktual. Kalau tidak ada korelasi,
                       integrasi tidak akan membantu - berhenti di sini.

Tahap 4 (integrasi)   : Implementasi Opsi 5.1 (fitur tambahan) lebih dulu.
                       Latih ulang, bandingkan akurasi dengan/tanpa fitur IoT.

Tahap 5 (evaluasi)    : Kalau terbukti meningkatkan akurasi, lanjut.
                       Kalau tidak, pertimbangkan Opsi 5.2 atau hentikan.
```

---

## 7. Risiko & Pertimbangan

- **Belum tentu meningkatkan akurasi.** Perlu dibuktikan dengan data (Tahap 3). Jangan investasi besar sebelum ada bukti korelasi.
- **Ketergantungan pada keandalan sensor.** Kalau sensor sering rusak/offline, fitur IoT justru bisa menurunkan kualitas prediksi.
- **Masalah cakupan.** 1-2 bin demo tidak mewakili volume sampah seluruh kota. Integrasi bermakna butuh cakupan sensor yang luas.
- **Kebutuhan "ground truth".** Untuk melatih model dengan benar, idealnya ada data volume sampah aktual (timbangan) sebagai pembanding, bukan hanya estimasi.
- **Kompleksitas operasional.** Sistem yang saling terhubung lebih sulit dirawat & di-debug dibanding dua sistem terpisah.

---

## 8. Keputusan yang Sudah Diambil

- **2026-06-14:** Untuk uji coba pertama, dipilih **Pilihan A** (IoT sebagai monitoring terpisah). Integrasi IoT↔ML (Pilihan B / dokumen ini) **ditunda** untuk dibahas kemudian dengan senior.

---

## 9. Pertanyaan untuk Diskusi dengan Senior

1. Apakah tujuan utamanya akurasi prediksi, atau cukup monitoring operasional?
2. Apakah tersedia/akan tersedia data volume sampah aktual (timbangan truk) sebagai pembanding?
3. Berapa banyak bin yang realistis dipasang sensor dalam 6-12 bulan ke depan?
4. Apakah ada anggaran/waktu untuk fase analisis (Tahap 3) sebelum investasi integrasi?
5. Mana yang lebih prioritas: integrasi IoT↔ML, atau dulukan fitur lain di roadmap (GPS truk, optimasi rute)?

---

*Dokumen ini bahan diskusi, bukan komitmen implementasi. Detail teknis dapat berubah setelah analisis data nyata.*
