import { useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { CheckCircle2, FileSpreadsheet, FileText, ShieldCheck, Sparkles, TriangleAlert, Truck } from "lucide-react";
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
import { ChartTooltip, CHART, axisProps, referenceLineProps } from "../components/chart";
import { Alert, Button, Field, MetricCard, Slider, TextInput, Toggle } from "../components/ui";

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
    <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
      <div className="space-y-4">
        <WorkflowSteps hasResult={Boolean(result)} loading={loading} />
        <Panel eyebrow="Parameter" title="Input Prediksi">
          <div className="space-y-5">
            <Field label="Tanggal">
              <TextInput
                type="date"
                value={input.date}
                onChange={(event) => set("date", event.target.value)}
              />
            </Field>

            <div className="space-y-4 rounded-md border border-line bg-surface-1 p-4">
              <div className="text-sm font-semibold text-text-hi">Cuaca</div>
              <Slider label="Suhu" unit="C" min={24} max={35} step={0.5} value={input.temperature} onChange={(value) => set("temperature", value)} />
              <Slider label="Curah hujan" unit="mm" min={0} max={120} step={1} value={input.rainfall} onChange={(value) => set("rainfall", value)} />
              <Slider label="Kelembaban" unit="%" min={55} max={95} step={1} value={input.humidity} onChange={(value) => set("humidity", value)} />
            </div>

            <div className="space-y-4 rounded-md border border-line bg-surface-1 p-4">
              <div className="text-sm font-semibold text-text-hi">Kondisi kota</div>
              <Slider label="Tingkat event" min={0} max={5} step={1} value={input.event_level} onChange={(value) => set("event_level", value)} />
              <Field label="Kepadatan penduduk" hint="jiwa per km2">
                <TextInput
                  type="number"
                  min={3000}
                  max={15000}
                  step={100}
                  value={input.population_density}
                  onChange={(event) => set("population_density", Number(event.target.value))}
                  className="tnum"
                />
              </Field>
              <div className="grid grid-cols-2 gap-3">
                <Toggle label="Hari libur" value={input.holiday === 1} onChange={(value) => set("holiday", value ? 1 : 0)} />
                <Toggle label="Akhir pekan" value={input.weekend === 1} onChange={(value) => set("weekend", value ? 1 : 0)} />
              </div>
            </div>

            <Button
              onClick={runPrediction}
              loading={loading}
              icon={Sparkles}
              variant="primary"
              className="w-full"
            >
              Prediksi sekarang
            </Button>
            {error && <p className="text-sm" style={{ color: "var(--color-full)" }}>{error}</p>}
          </div>
        </Panel>
      </div>

      <div className="space-y-6">
        {!result ? (
          <Panel eyebrow="Hasil" title="Menunggu prediksi">
            <p className="text-sm text-text-lo">
              Atur parameter lalu jalankan prediksi. Hasil harian, mingguan, bulanan, dan rekomendasi armada akan tampil di sini.
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
  onExport: (horizon: "weekly" | "monthly", format: "excel" | "pdf") => void;
}) {
  const { daily, weekly, monthly } = result;
  const fleet = daily.fleet_recommendation;
  const anomaly = daily.anomaly;
  const decisionTone = anomaly.is_anomaly || fleet.utilization_rate >= 95 ? "warning" : "success";
  const decisionTitle =
    decisionTone === "warning" ? "Review sebelum dispatch" : "Rencana siap digunakan";
  const decisionMessage =
    decisionTone === "warning"
      ? "Prediksi memiliki sinyal risiko. Periksa input dan siapkan opsi armada cadangan."
      : "Prediksi dan kapasitas armada berada dalam kondisi operasional yang layak.";
  const breakdown = weekly.daily_predictions.map((day) => ({
    label: `${day.day_name.slice(0, 3)} ${day.date.slice(8)}/${day.date.slice(5, 7)}`,
    volume: day.predicted_volume,
  }));
  const maxVol = Math.max(...breakdown.map((item) => item.volume));
  const weeklyAverage = weekly.average_daily;

  return (
    <>
      <Panel eyebrow="Keputusan" title="Ringkasan dispatch">
        <div className="grid gap-4 lg:grid-cols-[1fr_260px]">
          <Alert
            tone={decisionTone}
            icon={decisionTone === "warning" ? TriangleAlert : CheckCircle2}
            title={decisionTitle}
          >
            <p>{decisionMessage}</p>
            <p className="mt-2">
              Gunakan <span className="tnum text-text-hi">{fleet.trucks_needed}</span> truk untuk estimasi{" "}
              <span className="tnum text-text-hi">{fmt(daily.predicted_waste_volume)}</span> ton hari ini.
            </p>
          </Alert>
          <div className="rounded-md border border-line bg-surface-1 p-4 text-sm">
            <div className="text-xs font-medium text-text-lo">Rentang keyakinan</div>
            <div className="tnum mt-2 text-xl font-semibold text-text-hi">
              {fmt(daily.confidence_interval.lower_bound)}-{fmt(daily.confidence_interval.upper_bound)} ton
            </div>
            <p className="mt-2 text-text-mid">Margin {fmt(daily.confidence_interval.margin_of_error)} ton.</p>
          </div>
        </div>
      </Panel>

      <div className="grid gap-4 md:grid-cols-3">
        <HorizonCard title="Harian" total={daily.predicted_waste_volume} ci={daily.confidence_interval} accent />
        <HorizonCard title="Mingguan, 7 hari" total={weekly.total_volume} avg={weekly.average_daily} ci={weekly.confidence_interval} />
        <HorizonCard title="Bulanan, 30 hari" total={monthly.total_volume} avg={monthly.average_daily} ci={monthly.confidence_interval} />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Panel eyebrow="Deteksi" title="Status anomali">
          <Alert
            tone={anomaly.is_anomaly ? "warning" : "success"}
            icon={anomaly.is_anomaly ? TriangleAlert : ShieldCheck}
            title={anomaly.is_anomaly ? "Input tidak biasa" : "Input normal"}
          >
            <p>{anomaly.message}</p>
            {anomaly.score !== null && <p className="tnum mt-1 text-xs text-text-lo">Skor: {anomaly.score}</p>}
          </Alert>
        </Panel>

        <Panel eyebrow="Logistik" title="Rekomendasi armada">
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

      <Panel eyebrow="Rincian, 7 hari" title="Prediksi harian mingguan">
        <div style={{ width: "100%", height: 300 }}>
          <ResponsiveContainer>
            <BarChart data={breakdown} margin={{ top: 16, right: 8, bottom: 0, left: -12 }}>
              <CartesianGrid stroke={CHART.grid} vertical={false} />
              <XAxis dataKey="label" {...axisProps} interval={0} angle={-12} textAnchor="end" height={50} />
              <YAxis {...axisProps} width={48} />
              <ReferenceLine
                y={weeklyAverage}
                {...referenceLineProps}
                label={{ value: "Rata-rata", fill: CHART.axis, fontSize: 11, position: "insideTopRight" }}
              />
              <Tooltip content={<ChartTooltip unit=" ton" />} cursor={{ fill: "#ffffff08" }} />
              <Bar dataKey="volume" name="Volume" radius={[3, 3, 0, 0]}>
                {breakdown.map((item, index) => (
                  <Cell key={index} fill={item.volume === maxVol ? CHART.primary : CHART.neutral} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Panel>

      <Panel eyebrow="Unduh" title="Export prediksi">
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <ExportButton icon={FileSpreadsheet} label="Mingguan Excel" busy={exporting === "weekly-excel"} onClick={() => onExport("weekly", "excel")} />
          <ExportButton icon={FileText} label="Mingguan PDF" busy={exporting === "weekly-pdf"} onClick={() => onExport("weekly", "pdf")} />
          <ExportButton icon={FileSpreadsheet} label="Bulanan Excel" busy={exporting === "monthly-excel"} onClick={() => onExport("monthly", "excel")} />
          <ExportButton icon={FileText} label="Bulanan PDF" busy={exporting === "monthly-pdf"} onClick={() => onExport("monthly", "pdf")} />
        </div>
        <p className="mt-3 text-xs text-text-lo">Untuk tanggal mulai {input.date}.</p>
      </Panel>
    </>
  );
}

function WorkflowSteps({ hasResult, loading }: { hasResult: boolean; loading: boolean }) {
  const steps = [
    { label: "Input parameter", done: true },
    { label: "Jalankan prediksi", done: hasResult || loading },
    { label: "Review rekomendasi", done: hasResult },
    { label: "Export laporan", done: false },
  ];

  return (
    <Panel eyebrow="Workflow" title="Alur prediksi">
      <div className="space-y-2">
        {steps.map((step, index) => (
          <div key={step.label} className="flex items-center gap-3 rounded-md border border-line bg-surface-1 px-3 py-2">
            <span
              className="grid h-6 w-6 shrink-0 place-items-center rounded-full border text-xs font-semibold"
              style={{
                borderColor: step.done ? "var(--color-ok)" : "var(--color-line-bright)",
                color: step.done ? "var(--color-ok)" : "var(--color-text-lo)",
              }}
            >
              {step.done ? <CheckCircle2 size={14} /> : index + 1}
            </span>
            <span className={step.done ? "text-sm text-text-hi" : "text-sm text-text-mid"}>{step.label}</span>
          </div>
        ))}
      </div>
    </Panel>
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
    <MetricCard
      label={title}
      value={fmt(total)}
      unit="ton"
      accent={accent}
      helper={
        <div className="space-y-1">
          {avg !== undefined && <p className="tnum">Rata-rata {fmt(avg)} ton/hari</p>}
          <p className="tnum">95% CI {fmt(ci.lower_bound)}-{fmt(ci.upper_bound)}</p>
        </div>
      }
    />
  );
}

function ExportButton({
  icon,
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
    <Button onClick={onClick} loading={busy} icon={icon} className="w-full">
      {label}
    </Button>
  );
}
