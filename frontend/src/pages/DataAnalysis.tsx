import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../lib/api";
import { useAsync } from "../lib/useAsync";
import { fmt } from "../lib/format";
import { Panel } from "../components/Panel";
import { ChartTooltip, CHART, axisProps } from "../components/chart";
import { Loading, ErrorState } from "../components/states";

/** Diverging color for a correlation value in [-1, 1]: teal (−) → amber (+). */
function corrColor(v: number): string {
  const mag = Math.min(1, Math.abs(v));
  const base = v >= 0 ? "242, 163, 60" : "63, 185, 140";
  return `rgba(${base}, ${(0.12 + mag * 0.8).toFixed(2)})`;
}

const COL_LABEL: Record<string, string> = {
  temperature: "Suhu",
  rainfall: "Hujan",
  humidity: "Lembab",
  holiday: "Libur",
  weekend: "Akhir Pekan",
  population_density: "Penduduk",
  event_level: "Event",
  waste_volume: "Volume",
};

export default function DataAnalysis() {
  const { data, loading, error, reload } = useAsync(() => api.analysis(), []);

  if (loading) return <Loading />;
  if (error || !data) return <ErrorState message={error ?? "Data tidak tersedia"} onRetry={reload} />;

  const dist = data.distribution.map((d) => ({
    mid: ((d.bin_start + d.bin_end) / 2).toFixed(0),
    count: d.count,
  }));
  const cols = data.correlation.columns;

  return (
    <div className="space-y-6">
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Distribution */}
        <Panel eyebrow="Sebaran" title="Distribusi Volume Sampah">
          <div style={{ width: "100%", height: 300 }}>
            <ResponsiveContainer>
              <BarChart data={dist} margin={{ top: 8, right: 8, bottom: 0, left: -16 }}>
                <CartesianGrid stroke={CHART.grid} vertical={false} />
                <XAxis dataKey="mid" {...axisProps} minTickGap={24} />
                <YAxis {...axisProps} width={44} />
                <Tooltip
                  content={<ChartTooltip labelFormatter={(l) => `≈ ${l} ton`} />}
                  cursor={{ fill: "#ffffff08" }}
                />
                <Bar dataKey="count" name="Frekuensi" fill={CHART.amber} radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        {/* By weekday */}
        <Panel eyebrow="Pola Mingguan" title="Rata-rata per Hari">
          <div style={{ width: "100%", height: 300 }}>
            <ResponsiveContainer>
              <BarChart data={data.by_weekday} margin={{ top: 8, right: 8, bottom: 0, left: -16 }}>
                <CartesianGrid stroke={CHART.grid} vertical={false} />
                <XAxis dataKey="day" {...axisProps} tickFormatter={(d: string) => d.slice(0, 3)} />
                <YAxis {...axisProps} width={44} />
                <Tooltip content={<ChartTooltip unit=" ton" />} cursor={{ fill: "#ffffff08" }} />
                <Bar dataKey="average" name="Rata-rata" radius={[2, 2, 0, 0]}>
                  {data.by_weekday.map((d, i) => {
                    const max = Math.max(...data.by_weekday.map((x) => x.average));
                    return <Cell key={i} fill={d.average === max ? CHART.amber : "#3a4b54"} />;
                  })}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      {/* Monthly trend */}
      <Panel eyebrow="Time Series" title="Tren Rata-rata Bulanan">
        <div style={{ width: "100%", height: 300 }}>
          <ResponsiveContainer>
            <LineChart data={data.monthly} margin={{ top: 8, right: 8, bottom: 0, left: -12 }}>
              <CartesianGrid stroke={CHART.grid} vertical={false} />
              <XAxis dataKey="month" {...axisProps} minTickGap={48} />
              <YAxis {...axisProps} width={48} />
              <Tooltip content={<ChartTooltip unit=" ton" />} cursor={{ stroke: CHART.amber, strokeOpacity: 0.4 }} />
              <Line type="monotone" dataKey="average" name="Rata-rata" stroke={CHART.amber} strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Panel>

      {/* Correlation heatmap */}
      <Panel eyebrow="Hubungan Antar Variabel" title="Matriks Korelasi">
        <div className="overflow-x-auto">
          <table className="border-collapse">
            <thead>
              <tr>
                <th className="p-1" />
                {cols.map((c) => (
                  <th key={c} className="eyebrow whitespace-nowrap px-1.5 py-1 !text-[0.6rem]" style={{ writingMode: "vertical-rl" }}>
                    {COL_LABEL[c] ?? c}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.correlation.matrix.map((row, i) => (
                <tr key={i}>
                  <td className="eyebrow whitespace-nowrap pr-2 !text-[0.6rem]">{COL_LABEL[cols[i]] ?? cols[i]}</td>
                  {row.map((v, j) => (
                    <td key={j} className="p-0.5">
                      <div
                        className="tnum grid h-9 w-12 place-items-center rounded-sm text-[0.65rem]"
                        style={{ backgroundColor: corrColor(v), color: Math.abs(v) > 0.55 ? "#0e1417" : "var(--color-text-mid)" }}
                        title={`${cols[i]} ↔ ${cols[j]}: ${v}`}
                      >
                        {v.toFixed(2)}
                      </div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-3 text-xs text-text-lo">
          <span style={{ color: CHART.amber }}>Amber</span> = korelasi positif,{" "}
          <span style={{ color: CHART.ok }}>teal</span> = negatif. Semakin pekat, semakin kuat.
        </p>
      </Panel>

      {/* Sample preview */}
      <Panel eyebrow="Preview" title="Cuplikan Dataset">
        <div className="max-h-80 overflow-auto">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-ink-800">
              <tr className="border-b border-line text-left">
                {Object.keys(data.sample_rows[0] ?? {}).map((k) => (
                  <th key={k} className="eyebrow whitespace-nowrap px-2 pb-2 font-medium">{k}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.sample_rows.map((row, i) => (
                <tr key={i} className="border-b border-line/40 last:border-0">
                  {Object.values(row).map((v, j) => (
                    <td key={j} className="tnum whitespace-nowrap px-2 py-1.5 text-text-mid">
                      {typeof v === "number" ? fmt(v, 2) : String(v)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  );
}
