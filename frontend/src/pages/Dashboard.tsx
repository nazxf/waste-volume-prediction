import { useMemo } from "react";
import { Link } from "react-router-dom";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { AlertTriangle, ArrowRight, CalendarDays, CheckCircle2, Truck } from "lucide-react";
import { api, type PredictionInput } from "../lib/api";
import { useAsync } from "../lib/useAsync";
import { fmt, fmtInt } from "../lib/format";
import { Panel, StatReadout } from "../components/Panel";
import { CapacityGauge } from "../components/CapacityGauge";
import { ChartTooltip, CHART, axisProps, referenceLineProps } from "../components/chart";
import { Loading, ErrorState } from "../components/states";
import { MetricCard } from "../components/ui";

export default function Dashboard() {
  const overview = useAsync(() => api.overview(90), []);

  const quickInput: PredictionInput | null = useMemo(() => {
    if (!overview.data) return null;
    return {
      date: new Date().toISOString().slice(0, 10),
      ...overview.data.latest_features,
    };
  }, [overview.data]);

  const quick = useAsync(async () => {
    if (!quickInput) return null;
    const [daily, weekly, monthly] = await Promise.all([
      api.predictDaily(quickInput),
      api.predictWeekly(quickInput),
      api.predictMonthly(quickInput),
    ]);
    return { daily, weekly, monthly };
  }, [quickInput]);

  if (overview.loading) return <Loading />;
  if (overview.error || !overview.data) {
    return <ErrorState message={overview.error ?? "Data tidak tersedia"} onRetry={overview.reload} />;
  }

  const data = overview.data;
  const daily = quick.data?.daily;
  const fleet = daily?.fleet_recommendation;
  const delta = daily ? daily.predicted_waste_volume - data.average_daily : null;
  const utilization = fleet?.utilization_rate ?? 0;
  const risk =
    !daily || !fleet
      ? null
      : daily.anomaly.is_anomaly || utilization >= 95
        ? {
            label: "Butuh perhatian",
            tone: "warning",
            color: "var(--color-warn)",
            summary: "Volume atau utilisasi armada mendekati batas operasional.",
          }
        : {
            label: "Terkendali",
            tone: "success",
            color: "var(--color-ok)",
            summary: "Prediksi hari ini masih berada dalam kapasitas armada.",
          };
  const actionItems = [
    fleet ? `Siapkan ${fleet.trucks_needed} truk untuk rute hari ini.` : "Menunggu prediksi armada.",
    utilization >= 90 ? "Cadangkan armada tambahan sebelum jam puncak." : "Gunakan rencana armada normal.",
    daily?.anomaly.is_anomaly ? "Review input karena pola terdeteksi tidak biasa." : "Lanjutkan monitoring kondisi kota.",
  ];

  return (
    <div className="space-y-6">
      <section className="panel rise p-6">
        <div className="grid gap-6 xl:grid-cols-[1fr_300px] xl:items-center">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <div className="text-xs font-medium text-text-lo">Ringkasan operasional hari ini</div>
              {risk && (
                <span
                  className="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium"
                  style={{ borderColor: `${risk.color}66`, color: risk.color }}
                >
                  {risk.tone === "warning" ? <AlertTriangle size={13} /> : <CheckCircle2 size={13} />}
                  {risk.label}
                </span>
              )}
            </div>
            <div className="mt-5 grid gap-4 md:grid-cols-3">
              <MetricCard
                label="Volume hari ini"
                value={daily ? fmt(daily.predicted_waste_volume) : "--"}
                unit="ton"
                accent
                helper={
                  daily && delta !== null
                    ? `${delta >= 0 ? "Di atas" : "Di bawah"} rata-rata ${fmt(Math.abs(delta))} ton`
                    : "Mengambil prediksi"
                }
              />
              <MetricCard
                label="Armada"
                value={fleet ? fmtInt(fleet.trucks_needed) : "--"}
                unit="truk"
                helper={fleet ? `Utilisasi ${fmt(fleet.utilization_rate)}%` : "Belum tersedia"}
              />
              <MetricCard
                label="Horizon 7 hari"
                value={quick.data?.weekly ? fmt(quick.data.weekly.total_volume) : "--"}
                unit="ton"
                helper={quick.data?.weekly ? `Rata-rata ${fmt(quick.data.weekly.average_daily)} ton/hari` : "Menghitung"}
              />
            </div>
            {risk && <p className="mt-4 max-w-2xl text-sm text-text-mid">{risk.summary}</p>}
            <div className="mt-5 grid gap-2 text-sm text-text-mid md:grid-cols-3">
              {actionItems.map((item, index) => (
                <div key={item} className="rounded-md border border-line bg-surface-1 p-3">
                  <div className="mb-1 text-xs font-medium text-text-lo">Tindakan {index + 1}</div>
                  {item}
                </div>
              ))}
            </div>
          </div>

          {daily && fleet && (
            <div className="rounded-md border border-line bg-surface-1 p-4">
              <CapacityGauge
                percent={fleet.utilization_rate}
                readout={fmt(fleet.utilization_rate, 0)}
                unit="%"
                color={CHART.amber}
                height={180}
                caption={`${fmt(daily.predicted_waste_volume)} ton dari kapasitas ${fmtInt(fleet.total_capacity)} ton`}
              />
            </div>
          )}
        </div>
      </section>

      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        <Panel
          eyebrow="Historis, 90 hari terakhir"
          title="Tren volume sampah"
          action={
            <Link to="/prediksi" className="inline-flex items-center gap-1.5 text-sm font-medium text-amber hover:underline">
              Buat prediksi <ArrowRight size={14} />
            </Link>
          }
        >
          <div style={{ width: "100%", height: 320 }}>
            <ResponsiveContainer>
              <AreaChart data={data.trend} margin={{ top: 8, right: 8, bottom: 0, left: -12 }}>
                <defs>
                  <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={CHART.amber} stopOpacity={0.26} />
                    <stop offset="100%" stopColor={CHART.amber} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke={CHART.grid} vertical={false} />
                <XAxis
                  dataKey="date"
                  {...axisProps}
                  minTickGap={48}
                  tickFormatter={(date: string) => date.slice(5)}
                />
                <YAxis {...axisProps} width={48} />
                <ReferenceLine
                  y={data.average_daily}
                  {...referenceLineProps}
                  label={{ value: "Rata-rata", fill: CHART.axis, fontSize: 11, position: "insideTopRight" }}
                />
                <Tooltip content={<ChartTooltip unit=" ton" />} cursor={{ stroke: CHART.amber, strokeOpacity: 0.4 }} />
                <Area
                  type="monotone"
                  dataKey="waste_volume"
                  name="Volume"
                  stroke={CHART.amber}
                  strokeWidth={2}
                  fill="url(#trendFill)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel eyebrow="Rencana" title="Kapasitas dan jadwal">
          <div className="space-y-3 text-sm">
            <div className="flex items-start gap-3 rounded-md border border-line bg-surface-1 p-3">
              <Truck size={17} className="mt-0.5 text-amber" />
              <div>
                <div className="font-medium text-text-hi">Dispatch armada</div>
                <p className="mt-1 text-text-mid">
                  {fleet ? `${fleet.trucks_needed} truk, kapasitas total ${fmtInt(fleet.total_capacity)} ton.` : "Menunggu hasil prediksi."}
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3 rounded-md border border-line bg-surface-1 p-3">
              <CalendarDays size={17} className="mt-0.5 text-amber" />
              <div>
                <div className="font-medium text-text-hi">Periode data</div>
                <p className="mt-1 text-text-mid">
                  {data.date_start} sampai {data.date_end}, total {fmtInt(data.total_days)} hari.
                </p>
              </div>
            </div>
          </div>
        </Panel>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatReadout label="Rata-rata harian" value={fmt(data.average_daily)} unit="ton" accent />
        <StatReadout label="Volume maksimum" value={fmt(data.max_volume)} unit="ton" />
        <StatReadout label="Volume minimum" value={fmt(data.min_volume)} unit="ton" />
        <StatReadout label="Total hari tercatat" value={fmtInt(data.total_days)} unit="hari" />
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <ForecastCard label="Hari ini" value={daily?.predicted_waste_volume} loading={quick.loading} />
        <ForecastCard label="7 hari" value={quick.data?.weekly.total_volume} loading={quick.loading} />
        <ForecastCard label="30 hari" value={quick.data?.monthly.total_volume} loading={quick.loading} />
      </div>

    </div>
  );
}

function ForecastCard({ label, value, loading }: { label: string; value?: number; loading: boolean }) {
  return (
    <MetricCard
      label={`Prediksi, ${label}`}
      value={loading ? "..." : value !== undefined ? fmt(value) : "--"}
      unit="ton"
    />
  );
}
