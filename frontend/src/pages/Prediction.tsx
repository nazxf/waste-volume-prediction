import { useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Sparkles, Truck, FileSpreadsheet, FileText, TriangleAlert, ShieldCheck } from "lucide-react";
import {
  api,
  downloadExport,
  type DailyPrediction,
  type PredictionInput,
  type RangePrediction,
} from "../lib/api";
import { fmt, fmtInt } from "../lib/format";
import { Panel } from "../components/Panel";
import { CapacityGauge } from "../components/CapacityGauge";
import { ChartTooltip, CHART, axisProps } from "../components/chart";

const DEFAULTS: PredictionInput = {
  date: new Date().toISOString().slice(0, 10),
  temperature: 29.5,
  rainfall: 10,
  humidity: 75,
  holiday: 0,
  weekend: 0,
  population_density: 9000,
  event_level: 1,
};

interface Result {
  daily: DailyPrediction;
  weekly: RangePrediction;
  monthly: RangePrediction;
}

export default function Prediction() {
  const [input, setInput] = useState<PredictionInput>(DEFAULTS);
  const [result, setResult] = useState<Result | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState<string | null>(null);

  const set = <K extends keyof PredictionInput>(key: K, value: PredictionInput[K]) =>
    setInput((prev) => ({ ...prev, [key]: value }));

  async function runPrediction() {
    setLoading(true);
    setError(null);
    try {
      const [daily, weekly, monthly] = await Promise.all([
        api.predictDaily(input),
        api.predictWeekly(input),
        api.predictMonthly(input),
      ]);
      setResult({ daily, weekly, monthly });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Prediksi gagal");
    } finally {
      setLoading(false);
    }
  }

  async function doExport(horizon: "weekly" | "monthly", format: "excel" | "pdf") {
    const key = `${horizon}-${format}`;
    setExporting(key);
    try {
      await downloadExport(input, horizon, format);
    } catch {
      setError("Export gagal. Coba lagi.");
    } finally {
      setExporting(null);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[340px_1fr]">
      {/* Input form */}
      <div className="space-y-4">
        <Panel eyebrow="Parameter" title="Input Prediksi">
          <div className="space-y-5">
            <Field label="Tanggal">
              <input
                type="date"
                value={input.date}
                onChange={(e) => set("date", e.target.value)}
                className="w-full rounded-sm border border-line bg-ink-900 px-3 py-2 text-sm text-text-hi focus:border-amber"
              />
            </Field>

            <Slider label="Suhu" unit="°C" min={24} max={35} step={0.5} value={input.temperature} onChange={(v) => set("temperature", v)} />
            <Slider label="Curah Hujan" unit="mm" min={0} max={120} step={1} value={input.rainfall} onChange={(v) => set("rainfall", v)} />
            <Slider label="Kelembaban" unit="%" min={55} max={95} step={1} value={input.humidity} onChange={(v) => set("humidity", v)} />
            <Slider label="Tingkat Event" unit="" min={0} max={5} step={1} value={input.event_level} onChange={(v) => set("event_level", v)} />

            <Field label="Kepadatan Penduduk (jiwa/km²)">
              <input
                type="number"
                min={3000}
                max={15000}
                step={100}
                value={input.population_density}
                onChange={(e) => set("population_density", Number(e.target.value))}
                className="tnum w-full rounded-sm border border-line bg-ink-900 px-3 py-2 text-sm text-text-hi focus:border-amber"
              />
            </Field>

            <div className="grid grid-cols-2 gap-3">
              <Toggle label="Hari Libur" value={input.holiday} onChange={(v) => set("holiday", v)} />
              <Toggle label="Akhir Pekan" value={input.weekend} onChange={(v) => set("weekend", v)} />
            </div>

            <button
              onClick={runPrediction}
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-sm bg-amber px-4 py-3 text-sm font-semibold text-ink-900 transition-colors hover:bg-amber-deep disabled:opacity-60"
            >
              <Sparkles size={16} />
              {loading ? "Memproses…" : "Prediksi Sekarang"}
            </button>
            {error && <p className="text-xs" style={{ color: "var(--color-full)" }}>{error}</p>}
          </div>
        </Panel>
      </div>

      {/* Results */}
      <div className="space-y-6">
        {!result ? (
          <Panel eyebrow="Hasil" title="Menunggu Prediksi">
            <p className="text-sm text-text-lo">
              Atur parameter di kiri lalu jalankan prediksi. Hasil harian, mingguan, dan bulanan beserta rekomendasi
              armada akan muncul di sini.
            </p>
          </Panel>
        ) : (
          <ResultView result={result} input={input} exporting={exporting} onExport={doExport} />
        )}
      </div>
    </div>
  );
}

function ResultView({
  result,
  input,
  exporting,
  onExport,
}: {
  result: Result;
  input: PredictionInput;
  exporting: string | null;
  onExport: (h: "weekly" | "monthly", f: "excel" | "pdf") => void;
}) {
  const { daily, weekly, monthly } = result;
  const fleet = daily.fleet_recommendation;
  const anomaly = daily.anomaly;

  const breakdown = weekly.daily_predictions.map((d) => ({
    label: `${d.day_name.slice(0, 3)} ${d.date.slice(8)}/${d.date.slice(5, 7)}`,
    volume: d.predicted_volume,
  }));
  const maxVol = Math.max(...breakdown.map((b) => b.volume));

  return (
    <>
      {/* Horizon cards + fleet gauge */}
      <div className="grid gap-4 md:grid-cols-3">
        <HorizonCard
          title="Harian"
          total={daily.predicted_waste_volume}
          ci={daily.confidence_interval}
          accent
        />
        <HorizonCard
          title="Mingguan · 7 hari"
          total={weekly.total_volume}
          avg={weekly.average_daily}
          ci={weekly.confidence_interval}
        />
        <HorizonCard
          title="Bulanan · 30 hari"
          total={monthly.total_volume}
          avg={monthly.average_daily}
          ci={monthly.confidence_interval}
        />
      </div>

      {/* Anomaly + Fleet */}
      <div className="grid gap-4 md:grid-cols-2">
        <Panel eyebrow="Deteksi" title="Status Anomali">
          <div
            className="flex items-start gap-3 rounded-sm border p-4"
            style={{
              borderColor: anomaly.is_anomaly ? "var(--color-warn)40" : "var(--color-ok)40",
              backgroundColor: anomaly.is_anomaly ? "var(--color-warn)14" : "var(--color-ok)10",
            }}
          >
            {anomaly.is_anomaly ? (
              <TriangleAlert size={20} style={{ color: "var(--color-warn)" }} className="mt-0.5 shrink-0" />
            ) : (
              <ShieldCheck size={20} style={{ color: "var(--color-ok)" }} className="mt-0.5 shrink-0" />
            )}
            <div>
              <div
                className="text-sm font-semibold"
                style={{ color: anomaly.is_anomaly ? "var(--color-warn)" : "var(--color-ok)" }}
              >
                {anomaly.is_anomaly ? "Input Tidak Biasa" : "Input Normal"}
              </div>
              <p className="mt-1 text-xs text-text-mid">{anomaly.message}</p>
              {anomaly.score !== null && (
                <p className="tnum mt-1 text-xs text-text-lo">Skor: {anomaly.score}</p>
              )}
            </div>
          </div>
        </Panel>

        <Panel eyebrow="Logistik" title="Rekomendasi Armada">
          <div className="flex items-center gap-5">
            <CapacityGauge
              percent={fleet.utilization_rate}
              readout={fmt(fleet.utilization_rate, 0)}
              unit="%"
              color={CHART.amber}
              height={150}
            />
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2 text-text-mid">
                <Truck size={15} className="text-amber" />
                <span className="tnum font-semibold text-text-hi">{fleet.trucks_needed}</span> truk dibutuhkan
              </li>
              <li className="text-text-mid">
                Kapasitas/truk <span className="tnum text-text-hi">{fmt(fleet.truck_capacity, 0)}</span> ton
              </li>
              <li className="text-text-mid">
                Total kapasitas <span className="tnum text-text-hi">{fmtInt(fleet.total_capacity)}</span> ton
              </li>
            </ul>
          </div>
        </Panel>
      </div>

      {/* Weekly breakdown */}
      <Panel eyebrow="Rincian · 7 Hari" title="Prediksi Harian Mingguan">
        <div style={{ width: "100%", height: 300 }}>
          <ResponsiveContainer>
            <BarChart data={breakdown} margin={{ top: 16, right: 8, bottom: 0, left: -12 }}>
              <CartesianGrid stroke={CHART.grid} vertical={false} />
              <XAxis dataKey="label" {...axisProps} interval={0} angle={-12} textAnchor="end" height={50} />
              <YAxis {...axisProps} width={48} />
              <Tooltip content={<ChartTooltip unit=" ton" />} cursor={{ fill: "#ffffff08" }} />
              <Bar dataKey="volume" name="Volume" radius={[2, 2, 0, 0]}>
                {breakdown.map((b, i) => (
                  <Cell key={i} fill={b.volume === maxVol ? CHART.amber : "#3a4b54"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Panel>

      {/* Export */}
      <Panel eyebrow="Unduh" title="Export Prediksi">
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <ExportButton icon={FileSpreadsheet} label="Mingguan · Excel" busy={exporting === "weekly-excel"} onClick={() => onExport("weekly", "excel")} />
          <ExportButton icon={FileText} label="Mingguan · PDF" busy={exporting === "weekly-pdf"} onClick={() => onExport("weekly", "pdf")} />
          <ExportButton icon={FileSpreadsheet} label="Bulanan · Excel" busy={exporting === "monthly-excel"} onClick={() => onExport("monthly", "excel")} />
          <ExportButton icon={FileText} label="Bulanan · PDF" busy={exporting === "monthly-pdf"} onClick={() => onExport("monthly", "pdf")} />
        </div>
        <p className="mt-3 text-xs text-text-lo">Untuk tanggal mulai {input.date}.</p>
      </Panel>
    </>
  );
}

/* ---------- small form + result building blocks ---------- */

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="eyebrow mb-1.5 block">{label}</span>
      {children}
    </label>
  );
}

function Slider({
  label,
  unit,
  min,
  max,
  step,
  value,
  onChange,
}: {
  label: string;
  unit: string;
  min: number;
  max: number;
  step: number;
  value: number;
  onChange: (v: number) => void;
}) {
  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between">
        <span className="eyebrow">{label}</span>
        <span className="tnum text-sm text-text-hi">
          {value}
          <span className="ml-0.5 text-text-lo">{unit}</span>
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-amber"
      />
    </div>
  );
}

function Toggle({ label, value, onChange }: { label: string; value: number; onChange: (v: number) => void }) {
  const on = value === 1;
  return (
    <div>
      <span className="eyebrow mb-1.5 block">{label}</span>
      <button
        type="button"
        onClick={() => onChange(on ? 0 : 1)}
        className="flex w-full items-center justify-between rounded-sm border border-line bg-ink-900 px-3 py-2 text-sm transition-colors hover:border-line-bright"
      >
        <span className={on ? "text-amber" : "text-text-lo"}>{on ? "Ya" : "Tidak"}</span>
        <span
          className="relative h-4 w-7 rounded-full transition-colors"
          style={{ backgroundColor: on ? "var(--color-amber)" : "var(--color-line-bright)" }}
        >
          <span
            className="absolute top-0.5 h-3 w-3 rounded-full bg-ink-900 transition-all"
            style={{ left: on ? "0.875rem" : "0.125rem" }}
          />
        </span>
      </button>
    </div>
  );
}

function HorizonCard({
  title,
  total,
  avg,
  ci,
  accent,
}: {
  title: string;
  total: number;
  avg?: number;
  ci: { lower_bound: number; upper_bound: number };
  accent?: boolean;
}) {
  return (
    <div className="panel relative overflow-hidden p-5">
      <div
        className="absolute left-0 top-0 h-full w-[3px]"
        style={{ backgroundColor: accent ? "var(--color-amber)" : "var(--color-line-bright)" }}
      />
      <div className="eyebrow">{title}</div>
      <div className="tnum mt-2 font-display text-3xl font-semibold text-text-hi">
        {fmt(total)}
        <span className="ml-1 text-sm font-normal text-text-lo">ton</span>
      </div>
      {avg !== undefined && <p className="tnum mt-1 text-xs text-text-lo">Rata-rata {fmt(avg)} ton/hari</p>}
      <p className="tnum mt-2 text-xs text-text-mid">
        95% CI {fmt(ci.lower_bound)}–{fmt(ci.upper_bound)}
      </p>
    </div>
  );
}

function ExportButton({
  icon: Icon,
  label,
  busy,
  onClick,
}: {
  icon: typeof FileText;
  label: string;
  busy: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      disabled={busy}
      className="flex items-center justify-center gap-2 rounded-sm border border-line-bright px-3 py-2.5 text-xs font-medium text-text-hi transition-colors hover:bg-ink-700 disabled:opacity-60"
    >
      <Icon size={15} className="text-amber" />
      {busy ? "Mengunduh…" : label}
    </button>
  );
}
