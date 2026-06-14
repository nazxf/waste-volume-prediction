import { useMemo } from "react";
import { Link } from "react-router-dom";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Truck, ArrowRight } from "lucide-react";
import { api, type PredictionInput } from "../lib/api";
import { useAsync } from "../lib/useAsync";
import { fmt, fmtInt } from "../lib/format";
import { Panel, StatReadout } from "../components/Panel";
import { CapacityGauge } from "../components/CapacityGauge";
import { ChartTooltip, CHART, axisProps } from "../components/chart";
import { Loading, ErrorState } from "../components/states";

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
  if (overview.error || !overview.data)
    return <ErrorState message={overview.error ?? "Data tidak tersedia"} onRetry={overview.reload} />;

  const o = overview.data;
  const daily = quick.data?.daily;
  const fleet = daily?.fleet_recommendation;

  return (
    <div className="space-y-6">
      {/* Hero: the city's daily load, framed as a live gauge */}
      <section className="panel rise relative overflow-hidden p-6 md:p-8">
        <div className="grid gap-8 md:grid-cols-[1fr_auto] md:items-center">
          <div>
            <div className="eyebrow">Beban Harian Kota · Prediksi Hari Ini</div>
            <div className="mt-3 flex flex-wrap items-end gap-x-4 gap-y-1">
              <span className="tnum font-display text-6xl font-bold leading-none text-text-hi md:text-7xl">
                {daily ? fmt(daily.predicted_waste_volume) : "—"}
              </span>
              <span className="pb-1 text-xl text-text-lo">ton</span>
            </div>
            {daily && (
              <p className="mt-3 max-w-md text-sm text-text-mid">
                Selisih{" "}
                <span
                  className="tnum"
                  style={{
                    color:
                      daily.predicted_waste_volume >= o.average_daily
                        ? "var(--color-high)"
                        : "var(--color-ok)",
                  }}
                >
                  {fmt(daily.predicted_waste_volume - o.average_daily)} ton
                </span>{" "}
                dari rata-rata historis {fmt(o.average_daily)} ton/hari. Selang 95%:{" "}
                <span className="tnum text-text-hi">
                  {fmt(daily.confidence_interval.lower_bound)}–{fmt(daily.confidence_interval.upper_bound)}
                </span>{" "}
                ton.
              </p>
            )}
            {fleet && (
              <div className="mt-5 inline-flex items-center gap-3 rounded-sm border border-line bg-ink-900/60 px-4 py-2.5">
                <Truck size={18} className="text-amber" />
                <span className="text-sm text-text-mid">
                  Rekomendasi armada{" "}
                  <span className="tnum font-semibold text-text-hi">{fleet.trucks_needed} truk</span> · utilisasi{" "}
                  <span className="tnum text-text-hi">{fmt(fleet.utilization_rate)}%</span>
                </span>
              </div>
            )}
          </div>

          {/* Signature gauge: predicted load vs today's fleet capacity */}
          {daily && fleet && (
            <div className="md:pl-8 md:[border-left:1px_solid_var(--color-line)]">
              <CapacityGauge
                percent={fleet.utilization_rate}
                readout={fmt(fleet.utilization_rate, 0)}
                unit="%"
                color={CHART.amber}
                height={200}
                caption={`${fmt(daily.predicted_waste_volume)} ton dari kapasitas ${fmtInt(fleet.total_capacity)} ton`}
              />
            </div>
          )}
        </div>
      </section>

      {/* Headline stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatReadout label="Rata-rata Harian" value={fmt(o.average_daily)} unit="ton" accent />
        <StatReadout label="Volume Maksimum" value={fmt(o.max_volume)} unit="ton" />
        <StatReadout label="Volume Minimum" value={fmt(o.min_volume)} unit="ton" />
        <StatReadout label="Total Hari Tercatat" value={fmtInt(o.total_days)} unit="hari" />
      </div>

      {/* Quick horizon forecasts */}
      <div className="grid gap-4 md:grid-cols-3">
        <ForecastCard label="Hari Ini" value={daily?.predicted_waste_volume} loading={quick.loading} />
        <ForecastCard label="7 Hari" value={quick.data?.weekly.total_volume} loading={quick.loading} />
        <ForecastCard label="30 Hari" value={quick.data?.monthly.total_volume} loading={quick.loading} />
      </div>

      {/* Trend */}
      <Panel
        eyebrow="Historis · 90 Hari Terakhir"
        title="Tren Volume Sampah"
        action={
          <Link
            to="/prediksi"
            className="inline-flex items-center gap-1.5 text-xs font-medium text-amber hover:underline"
          >
            Buat prediksi <ArrowRight size={14} />
          </Link>
        }
      >
        <div style={{ width: "100%", height: 320 }}>
          <ResponsiveContainer>
            <AreaChart data={o.trend} margin={{ top: 8, right: 8, bottom: 0, left: -12 }}>
              <defs>
                <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={CHART.amber} stopOpacity={0.35} />
                  <stop offset="100%" stopColor={CHART.amber} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke={CHART.grid} vertical={false} />
              <XAxis
                dataKey="date"
                {...axisProps}
                minTickGap={48}
                tickFormatter={(d: string) => d.slice(5)}
              />
              <YAxis {...axisProps} width={48} />
              <Tooltip
                content={<ChartTooltip unit=" ton" />}
                cursor={{ stroke: CHART.amber, strokeOpacity: 0.4 }}
              />
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
    </div>
  );
}

function ForecastCard({ label, value, loading }: { label: string; value?: number; loading: boolean }) {
  return (
    <div className="panel flex items-center justify-between p-5">
      <div>
        <div className="eyebrow">Prediksi · {label}</div>
        <div className="tnum mt-2 font-display text-2xl font-semibold text-text-hi">
          {loading ? "···" : value !== undefined ? fmt(value) : "—"}
          <span className="ml-1 text-sm font-normal text-text-lo">ton</span>
        </div>
      </div>
    </div>
  );
}
