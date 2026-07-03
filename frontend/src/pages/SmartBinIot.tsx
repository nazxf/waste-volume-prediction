import { useMemo, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Cpu, RefreshCw, SlidersHorizontal } from "lucide-react";
import { api, type BinReading } from "../lib/api";
import { useAsync } from "../lib/useAsync";
import { fillStatus, formatTimestamp, STATUS_COLOR, fmt, type FillStatus } from "../lib/format";
import { Panel } from "../components/Panel";
import { CapacityGauge } from "../components/CapacityGauge";
import { StatusPill } from "../components/StatusPill";
import { ChartTooltip, CHART, axisProps, referenceLineProps } from "../components/chart";
import { Loading, ErrorState, EmptyState } from "../components/states";
import { Button, MetricCard } from "../components/ui";

const SERIES_COLORS = ["#f2a33c", "#3fb98c", "#5aa9e6", "#e5564e", "#c084fc", "#f2c14e"];
const STATUS_OPTIONS: Array<FillStatus | "all"> = ["all", "full", "high", "medium", "low"];

type SortMode = "priority" | "fill_desc" | "recent";

export default function SmartBinIot() {
  const { data, loading, error, reload } = useAsync(() => api.latestReadings(50), []);
  const [statusFilter, setStatusFilter] = useState<FillStatus | "all">("all");
  const [sortMode, setSortMode] = useState<SortMode>("priority");

  const latestPerBin = useMemo(() => {
    const map = new Map<string, BinReading>();
    for (const reading of data ?? []) {
      if (!map.has(reading.bin_id)) map.set(reading.bin_id, reading);
    }
    return [...map.values()];
  }, [data]);

  const filteredBins = useMemo(() => {
    const priorityRank: Record<FillStatus, number> = { full: 4, high: 3, medium: 2, low: 1 };
    return latestPerBin
      .filter((bin) => statusFilter === "all" || fillStatus(bin.fill_level) === statusFilter)
      .sort((a, b) => {
        if (sortMode === "recent") {
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        }
        if (sortMode === "fill_desc") {
          return b.fill_level - a.fill_level;
        }
        const statusDelta = priorityRank[fillStatus(b.fill_level)] - priorityRank[fillStatus(a.fill_level)];
        return statusDelta || b.fill_level - a.fill_level;
      });
  }, [latestPerBin, sortMode, statusFilter]);

  const statusCounts = useMemo(() => {
    const counts: Record<FillStatus, number> = { low: 0, medium: 0, high: 0, full: 0 };
    for (const bin of latestPerBin) counts[fillStatus(bin.fill_level)] += 1;
    return counts;
  }, [latestPerBin]);

  const priorityBins = useMemo(
    () => filteredBins.filter((bin) => ["full", "high"].includes(fillStatus(bin.fill_level))).slice(0, 6),
    [filteredBins],
  );

  const { series, bins } = useMemo(() => {
    const rows = [...(data ?? [])].sort(
      (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    );
    const binIds = [...new Set(rows.map((reading) => reading.bin_id))];
    const byTime = new Map<string, Record<string, number | string>>();
    for (const reading of rows) {
      const timestamp = reading.created_at;
      if (!byTime.has(timestamp)) byTime.set(timestamp, { t: timestamp });
      byTime.get(timestamp)![reading.bin_id] = reading.fill_level;
    }
    return { series: [...byTime.values()], bins: binIds };
  }, [data]);

  if (loading) return <Loading label="Memuat data ESP32..." />;
  if (error) return <ErrorState message={error} onRetry={reload} />;

  const refreshAction = (
    <Button onClick={reload} icon={RefreshCw}>
      Refresh
    </Button>
  );

  if (!data || data.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex justify-end">{refreshAction}</div>
        <EmptyState title="Belum ada data ESP32">
          Kirim pembacaan ke endpoint <code className="tnum text-amber">/iot/bin-reading</code> terlebih dahulu.
          Setelah perangkat mengirim data, level tiap bin akan tampil di sini.
        </EmptyState>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-text-mid">
          <span className="font-medium text-text-hi">{latestPerBin.length}</span> bin aktif, {data.length} pembacaan terakhir
        </p>
        {refreshAction}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Penuh" value={String(statusCounts.full)} unit="bin" helper="Prioritas angkut" accent />
        <MetricCard label="Tinggi" value={String(statusCounts.high)} unit="bin" helper="Perlu dijadwalkan" />
        <MetricCard label="Sedang" value={String(statusCounts.medium)} unit="bin" helper="Monitor berkala" />
        <MetricCard label="Rendah" value={String(statusCounts.low)} unit="bin" helper="Tidak mendesak" />
      </div>

      <Panel eyebrow="Kontrol" title="Filter dan prioritas">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex flex-wrap gap-2">
            {STATUS_OPTIONS.map((status) => (
              <button
                key={status}
                type="button"
                onClick={() => setStatusFilter(status)}
                className={[
                  "rounded-md border px-3 py-2 text-sm font-medium transition-colors",
                  statusFilter === status
                    ? "border-amber bg-amber text-ink-950"
                    : "border-line bg-surface-1 text-text-mid hover:border-line-bright hover:text-text-hi",
                ].join(" ")}
              >
                {status === "all" ? "Semua" : status}
              </button>
            ))}
          </div>

          <label className="flex items-center gap-2 text-sm text-text-mid">
            <SlidersHorizontal size={16} className="text-text-lo" />
            Urutkan
            <select
              value={sortMode}
              onChange={(event) => setSortMode(event.target.value as SortMode)}
              className="rounded-md border border-line bg-surface-1 px-3 py-2 text-sm text-text-hi"
            >
              <option value="priority">Prioritas status</option>
              <option value="fill_desc">Fill tertinggi</option>
              <option value="recent">Update terbaru</option>
            </select>
          </label>
        </div>
      </Panel>

      {priorityBins.length > 0 && (
        <Panel eyebrow="Antrean" title="Bin perlu tindakan">
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {priorityBins.map((bin) => (
              <div key={bin.bin_id} className="rounded-md border border-line bg-surface-1 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="font-semibold text-text-hi">{bin.bin_id}</div>
                    <div className="mt-1 text-xs text-text-lo">Update {formatTimestamp(bin.created_at)}</div>
                  </div>
                  <StatusPill status={fillStatus(bin.fill_level)} size="sm" />
                </div>
                <div className="tnum mt-3 text-2xl font-semibold" style={{ color: STATUS_COLOR[fillStatus(bin.fill_level)] }}>
                  {fmt(bin.fill_level, 1)}%
                </div>
              </div>
            ))}
          </div>
        </Panel>
      )}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {filteredBins.map((bin) => {
          const status = fillStatus(bin.fill_level);
          return (
            <Panel key={bin.bin_id} className="!p-5">
              <div className="mb-4 flex items-start justify-between">
                <div>
                  <div className="text-base font-semibold text-text-hi">{bin.bin_id}</div>
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

      {filteredBins.length === 0 && (
        <EmptyState title="Tidak ada bin pada filter ini">
          Ubah filter status untuk melihat bin lain.
        </EmptyState>
      )}

      <Panel eyebrow="Telemetri" title="Tren fill level">
        <div style={{ width: "100%", height: 340 }}>
          <ResponsiveContainer>
            <LineChart data={series} margin={{ top: 8, right: 8, bottom: 0, left: -12 }}>
              <CartesianGrid stroke={CHART.grid} vertical={false} />
              <XAxis
                dataKey="t"
                {...axisProps}
                minTickGap={40}
                tickFormatter={(timestamp: string) =>
                  new Date(timestamp).toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" })
                }
              />
              <YAxis {...axisProps} width={40} domain={[0, 100]} />
              <ReferenceLine
                y={90}
                stroke={CHART.full}
                strokeDasharray="4 4"
                strokeOpacity={0.8}
                label={{ value: "Penuh", fill: CHART.full, fontSize: 11, position: "insideTopRight" }}
              />
              <ReferenceLine
                y={70}
                {...referenceLineProps}
                label={{ value: "Tinggi", fill: CHART.axis, fontSize: 11, position: "insideRight" }}
              />
              <Tooltip
                content={<ChartTooltip unit="%" labelFormatter={(timestamp) => formatTimestamp(String(timestamp))} />}
                cursor={{ stroke: CHART.amber, strokeOpacity: 0.4 }}
              />
              <Legend wrapperStyle={{ fontSize: 11, fontFamily: CHART.fontMono, color: CHART.axis }} />
              {bins.map((id, index) => (
                <Line
                  key={id}
                  type="monotone"
                  dataKey={id}
                  name={id}
                  stroke={SERIES_COLORS[index % SERIES_COLORS.length]}
                  strokeWidth={2}
                  dot={{ r: 2 }}
                  connectNulls
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Panel>

      <Panel eyebrow="Log" title="Data terbaru">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-line text-left">
                {["Waktu", "Bin", "Device", "Fill", "Status"].map((heading) => (
                  <th key={heading} className="pb-2 pr-4 text-xs font-medium text-text-lo">{heading}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((reading) => (
                <tr key={reading.id} className="border-b border-line/50 last:border-0">
                  <td className="tnum py-2.5 pr-4 text-text-mid">{formatTimestamp(reading.created_at)}</td>
                  <td className="py-2.5 pr-4 text-text-hi">{reading.bin_id}</td>
                  <td className="tnum py-2.5 pr-4 text-text-lo">{reading.device_id}</td>
                  <td className="py-2.5 pr-4">
                    <span className="tnum" style={{ color: STATUS_COLOR[fillStatus(reading.fill_level)] }}>
                      {fmt(reading.fill_level, 1)}%
                    </span>
                  </td>
                  <td className="py-2.5 pr-4">
                    <StatusPill status={fillStatus(reading.fill_level)} size="sm" />
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
