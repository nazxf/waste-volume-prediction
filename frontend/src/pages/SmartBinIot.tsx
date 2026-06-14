import { useMemo } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { RefreshCw, Cpu } from "lucide-react";
import { api, type BinReading } from "../lib/api";
import { useAsync } from "../lib/useAsync";
import { fillStatus, formatTimestamp, STATUS_COLOR, fmt } from "../lib/format";
import { Panel } from "../components/Panel";
import { CapacityGauge } from "../components/CapacityGauge";
import { StatusPill } from "../components/StatusPill";
import { ChartTooltip, CHART, axisProps } from "../components/chart";
import { Loading, ErrorState, EmptyState } from "../components/states";

const SERIES_COLORS = ["#f2a33c", "#3fb98c", "#5aa9e6", "#e5564e", "#c084fc", "#f2c14e"];

export default function SmartBinIot() {
  const { data, loading, error, reload } = useAsync(() => api.latestReadings(50), []);

  // Latest reading per bin (data arrives newest-first).
  const latestPerBin = useMemo(() => {
    const map = new Map<string, BinReading>();
    for (const r of data ?? []) if (!map.has(r.bin_id)) map.set(r.bin_id, r);
    return [...map.values()];
  }, [data]);

  // Time series grouped into chart rows keyed by timestamp, one column per bin.
  const { series, bins } = useMemo(() => {
    const rows = [...(data ?? [])].sort(
      (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    );
    const binIds = [...new Set(rows.map((r) => r.bin_id))];
    const byTime = new Map<string, Record<string, number | string>>();
    for (const r of rows) {
      const t = r.created_at;
      if (!byTime.has(t)) byTime.set(t, { t });
      byTime.get(t)![r.bin_id] = r.fill_level;
    }
    return { series: [...byTime.values()], bins: binIds };
  }, [data]);

  if (loading) return <Loading label="Memuat data ESP32…" />;
  if (error) return <ErrorState message={error} onRetry={reload} />;

  const refreshAction = (
    <button
      onClick={reload}
      className="inline-flex items-center gap-1.5 rounded-sm border border-line-bright px-3 py-1.5 text-xs font-medium text-text-hi transition-colors hover:bg-ink-700"
    >
      <RefreshCw size={13} /> Refresh
    </button>
  );

  if (!data || data.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex justify-end">{refreshAction}</div>
        <EmptyState title="Belum ada data ESP32">
          Kirim pembacaan ke endpoint <code className="tnum text-amber">/iot/bin-reading</code> terlebih dahulu.
          Setelah perangkat mengirim data, level tiap bin akan tampil di sini secara langsung.
        </EmptyState>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <p className="eyebrow">{latestPerBin.length} bin aktif · {data.length} pembacaan terakhir</p>
        {refreshAction}
      </div>

      {/* One gauge per bin — the signature element as a live bin wall */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {latestPerBin.map((bin) => {
          const status = fillStatus(bin.fill_level);
          return (
            <Panel key={bin.bin_id} className="!p-5">
              <div className="mb-4 flex items-start justify-between">
                <div>
                  <div className="font-display text-base font-semibold text-text-hi">{bin.bin_id}</div>
                  <div className="mt-1 flex items-center gap-1.5 text-xs text-text-lo">
                    <Cpu size={12} /> <span className="tnum">{bin.device_id}</span>
                  </div>
                </div>
                <StatusPill status={status} />
              </div>
              <CapacityGauge
                percent={bin.fill_level}
                readout={fmt(bin.fill_level, 1)}
                unit="%"
                height={170}
                pulse={status === "full"}
                caption={`Update ${formatTimestamp(bin.created_at)}`}
              />
            </Panel>
          );
        })}
      </div>

      {/* Trend */}
      <Panel eyebrow="Telemetri" title="Tren Fill Level">
        <div style={{ width: "100%", height: 340 }}>
          <ResponsiveContainer>
            <LineChart data={series} margin={{ top: 8, right: 8, bottom: 0, left: -12 }}>
              <CartesianGrid stroke={CHART.grid} vertical={false} />
              <XAxis
                dataKey="t"
                {...axisProps}
                minTickGap={40}
                tickFormatter={(t: string) => new Date(t).toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" })}
              />
              <YAxis {...axisProps} width={40} domain={[0, 100]} />
              <Tooltip
                content={<ChartTooltip unit="%" labelFormatter={(t) => formatTimestamp(String(t))} />}
                cursor={{ stroke: CHART.amber, strokeOpacity: 0.4 }}
              />
              <Legend wrapperStyle={{ fontSize: 11, fontFamily: CHART.fontMono, color: CHART.axis }} />
              {bins.map((id, i) => (
                <Line
                  key={id}
                  type="monotone"
                  dataKey={id}
                  name={id}
                  stroke={SERIES_COLORS[i % SERIES_COLORS.length]}
                  strokeWidth={2}
                  dot={{ r: 2 }}
                  connectNulls
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Panel>

      {/* Table */}
      <Panel eyebrow="Log" title="Data Terbaru">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-line text-left">
                {["Waktu", "Bin", "Device", "Fill", "Status"].map((h) => (
                  <th key={h} className="eyebrow pb-2 pr-4 font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((r) => (
                <tr key={r.id} className="border-b border-line/50 last:border-0">
                  <td className="tnum py-2.5 pr-4 text-text-mid">{formatTimestamp(r.created_at)}</td>
                  <td className="py-2.5 pr-4 text-text-hi">{r.bin_id}</td>
                  <td className="tnum py-2.5 pr-4 text-text-lo">{r.device_id}</td>
                  <td className="py-2.5 pr-4">
                    <span className="tnum" style={{ color: STATUS_COLOR[fillStatus(r.fill_level)] }}>
                      {fmt(r.fill_level, 1)}%
                    </span>
                  </td>
                  <td className="py-2.5 pr-4">
                    <StatusPill status={fillStatus(r.fill_level)} size="sm" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  );
}
