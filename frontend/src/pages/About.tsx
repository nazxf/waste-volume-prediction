import {
  CloudRain,
  CalendarDays,
  Users,
  PartyPopper,
  TrendingUp,
  Wallet,
  Recycle,
  Building2,
} from "lucide-react";
import { Panel } from "../components/Panel";

const DRIVERS = [
  { icon: CloudRain, label: "Cuaca", desc: "Suhu, curah hujan, kelembaban" },
  { icon: CalendarDays, label: "Kalender", desc: "Hari kerja, akhir pekan, libur" },
  { icon: Users, label: "Penduduk", desc: "Kepadatan per km²" },
  { icon: PartyPopper, label: "Event", desc: "Tingkat kegiatan khusus (0-5)" },
];

const BENEFITS = [
  { icon: TrendingUp, title: "Efisiensi Operasional", desc: "Optimasi jumlah armada berdasarkan prediksi akurat." },
  { icon: Wallet, title: "Penghematan Biaya", desc: "Mengurangi biaya operasional dari armada yang tidak optimal." },
  { icon: CalendarDays, title: "Perencanaan Strategis", desc: "Data untuk perencanaan pengangkutan jangka panjang." },
  { icon: Recycle, title: "Lingkungan Bersih", desc: "Pengangkutan tepat waktu mencegah penumpukan sampah." },
];

const STACK: [string, string][] = [
  ["Backend ML", "Python, Scikit-Learn, XGBoost"],
  ["Data", "Pandas, NumPy"],
  ["API", "FastAPI, Uvicorn"],
  ["Dashboard", "React, Tailwind, Recharts"],
  ["IoT", "ESP32, HC-SR04, SQLite"],
  ["Model", "Joblib (RF / XGBoost / Ensemble)"],
];

export default function About() {
  return (
    <div className="space-y-6">
      <section className="panel rise p-6 md:p-8">
        <div className="eyebrow">Latar Belakang</div>
        <h2 className="mt-3 max-w-2xl text-2xl font-semibold leading-snug text-text-hi">
          Mengubah volume sampah yang fluktuatif menjadi rencana pengangkutan yang pasti.
        </h2>
        <p className="mt-3 max-w-2xl text-sm leading-relaxed text-text-mid">
          Volume sampah harian sangat bervariasi tergantung cuaca, kalender, kepadatan penduduk, dan event kota.
          Sistem ini memakai Machine Learning untuk memprediksi volume harian, mingguan, dan bulanan, lalu
          menerjemahkannya menjadi rekomendasi armada agar pengangkutan tidak berlebih maupun kurang.
        </p>
      </section>

      <Panel eyebrow="Faktor Prediksi" title="Apa yang Dipelajari Model">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {DRIVERS.map((d) => {
            const Icon = d.icon;
            return (
              <div key={d.label} className="rounded-sm border border-line bg-ink-900/50 p-4">
                <Icon size={20} className="text-amber" />
                <div className="mt-3 text-sm font-semibold text-text-hi">{d.label}</div>
                <p className="mt-1 text-xs text-text-lo">{d.desc}</p>
              </div>
            );
          })}
        </div>
      </Panel>

      <div className="grid gap-6 lg:grid-cols-2">
        <Panel eyebrow="Manfaat" title="Dampak bagi Operasi Kota">
          <ul className="space-y-4">
            {BENEFITS.map((b) => {
              const Icon = b.icon;
              return (
                <li key={b.title} className="flex gap-3">
                  <span className="mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-sm bg-ink-600">
                    <Icon size={16} className="text-amber" />
                  </span>
                  <div>
                    <div className="text-sm font-semibold text-text-hi">{b.title}</div>
                    <p className="mt-0.5 text-xs text-text-mid">{b.desc}</p>
                  </div>
                </li>
              );
            })}
          </ul>
        </Panel>

        <div className="space-y-6">
          <Panel eyebrow="Pengguna" title="Untuk Siapa">
            <div className="flex flex-wrap gap-2">
              {["Dinas Lingkungan Hidup", "Tim Smart City", "Pengelola Sampah", "Perencana Kota"].map((u) => (
                <span key={u} className="inline-flex items-center gap-1.5 rounded-sm border border-line bg-ink-900/50 px-3 py-1.5 text-xs text-text-mid">
                  <Building2 size={13} className="text-amber" />
                  {u}
                </span>
              ))}
            </div>
          </Panel>

          <Panel eyebrow="Teknologi" title="Stack">
            <dl className="divide-y divide-line text-sm">
              {STACK.map(([k, v]) => (
                <div key={k} className="flex items-center justify-between gap-4 py-2.5">
                  <dt className="text-text-lo">{k}</dt>
                  <dd className="text-right text-text-hi">{v}</dd>
                </div>
              ))}
            </dl>
          </Panel>
        </div>
      </div>

      <Panel eyebrow="Catatan" title="Batasan & Pengembangan">
        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <div className="eyebrow mb-2">Batasan</div>
            <ul className="list-inside list-disc space-y-1.5 text-sm text-text-mid">
              <li>Prediksi berbasis pola historis; kondisi ekstrem mungkin kurang akurat.</li>
              <li>Perlu data historis memadai untuk performa optimal.</li>
              <li>Perlu retraining berkala dengan data terbaru.</li>
            </ul>
          </div>
          <div>
            <div className="eyebrow mb-2">Pengembangan Lanjutan</div>
            <ul className="list-inside list-disc space-y-1.5 text-sm text-text-mid">
              <li>Integrasi sensor IoT di TPS dengan model prediksi.</li>
              <li>Real-time tracking & optimasi rute armada.</li>
              <li>Prediksi jenis sampah (organik, anorganik, B3).</li>
            </ul>
          </div>
        </div>
      </Panel>
    </div>
  );
}
