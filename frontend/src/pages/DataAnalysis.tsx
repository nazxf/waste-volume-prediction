import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../lib/api";
import { useAsync } from "../lib/useAsync";
import { fmt } from "../lib/format";
import { Panel } from "../components/Panel";
import { ChartTooltip, CHART, axisProps, referenceLineProps } from "../components/chart";
import { Loading, ErrorState } from "../components/states";

function corrColor(value: number): string {
  const magnitude = Math.min(1, Math.abs(value));
  const base = value >= 0 ? "242, 163, 60" : "63, 185, 140";
  return `rgba(${base}, ${(0.12 + magnitude * 0.8).toFixed(2)})`;
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

  const dist = data.distribution.map((item) => ({
    mid: ((item.bin_start + item.bin_end) / 2).toFixed(0),
    count: item.count,
  }));
  const cols = data.correlation.columns;
  const weekdayAverage =
    data.by_weekday.reduce((total, item) => total + item.average, 0) / Math.max(1, data.by_weekday.length);
  const monthlyAverage =
    data.monthly.reduce((total, item) => total + item.average, 0) / Math.max(1, data.monthly.length);
  const maxWeekday = Math.max(...data.by_weekday.map((item) => item.average));

  return (
    <div className="space-y-6">
      <div className="grid gap-6 lg:grid-cols-2">
        <Panel eyebrow="Sebaran" title="Distribusi volume sampah">
          <div style={{ width: "100%", height: 300 }}>
            <ResponsiveContainer>
              <BarChart data={dist} margin={{ top: 8, right: 8, bottom: 0, left: -16 }}>
                <CartesianGrid stroke={CHART.grid} vertical={false} />
                <XAxis dataKey="mid" {...axisProps} minTickGap={24} />
                <YAxis {...axisProps} width={44} />
                <Tooltip content={<ChartTooltip labelFormatter={(label) => `Sekitar ${label} ton`} />} cursor={{ fill: "#ffffff08" }} />
                <Bar dataKey="count" name="Frekuensi" fill={CHART.primary} radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel eyebrow="Pola mingguan" title="Rata-rata per hari">
          <div style={{ width: "100%", height: 300 }}>
            <ResponsiveContainer>
              <BarChart data={data.by_weekday} margin={{ top: 8, right: 8, bottom: 0, left: -16 }}>
                <CartesianGrid stroke={CHART.grid} vertical={false} />
                <XAxis dataKey="day" {...axisProps} tickFormatter={(day: string) => day.slice(0, 3)} />
                <YAxis {...axisProps} width={44} />
                <ReferenceLine
                  y={weekdayAverage}
                  {...referenceLineProps}
                  label={{ value: "Rata-rata", fill: CHART.axis, fontSize: 11, position: "insideTopRight" }}
                />
                <Tooltip content={<ChartTooltip unit=" ton" />} cursor={{ fill: "#ffffff08" }} />
                <Bar dataKey="average" name="Rata-rata" radius={[3, 3, 0, 0]}>
                  {data.by_weekday.map((item, index) => (
                    <Cell key={index} fill={item.average === maxWeekday ? CHART.primary : CHART.neutral} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </div>

      <Panel eyebrow="Time series" title="Tren rata-rata bulanan">
        <div style={{ width: "100%", height: 300 }}>
          <ResponsiveContainer>
            <LineChart data={data.monthly} margin={{ top: 8, right: 8, bottom: 0, left: -12 }}>
              <CartesianGrid stroke={CHART.grid} vertical={false} />
              <XAxis dataKey="month" {...axisProps} minTickGap={48} />
              <YAxis {...axisProps} width={48} />
              <ReferenceLine
                y={monthlyAverage}
                {...referenceLineProps}
                label={{ value: "Rata-rata", fill: CHART.axis, fontSize: 11, position: "insideTopRight" }}
              />
              <Tooltip content={<ChartTooltip unit=" ton" />} cursor={{ stroke: CHART.primary, strokeOpacity: 0.4 }} />
              <Line type="monotone" dataKey="average" name="Rata-rata" stroke={CHART.primary} strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Panel>

      <Panel eyebrow="Hubungan antar variabel" title="Matriks korelasi">
        <div className="overflow-x-auto">
          <table className="border-collapse">
            <thead>
              <tr>
                <th className="p-1" />
                {cols.map((col) => (
                  <th key={col} className="whitespace-nowrap px-1.5 py-1 text-xs font-medium text-text-lo" style={{ writingMode: "vertical-rl" }}>
                    {COL_LABEL[col] ?? col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.correlation.matrix.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  <td className="whitespace-nowrap pr-2 text-xs font-medium text-text-lo">{COL_LABEL[cols[rowIndex]] ?? cols[rowIndex]}</td>
                  {row.map((value, colIndex) => (
                    <td key={colIndex} className="p-0.5">
                      <div
                        className="tnum grid h-9 w-12 place-items-center rounded-md text-[0.65rem]"
                        style={{ backgroundColor: corrColor(value), color: Math.abs(value) > 0.55 ? "#0b1113" : "var(--color-text-mid)" }}
                        title={`${cols[rowIndex]} to ${cols[colIndex]}: ${value}`}
                      >
                        {value.toFixed(2)}
                      </div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-3 text-xs text-text-lo">
          <span style={{ color: CHART.primary }}>Amber</span> = korelasi positif,{" "}
          <span style={{ color: CHART.ok }}>hijau</span> = negatif. Semakin pekat, semakin kuat.
        </p>
      </Panel>

      <Panel eyebrow="Preview" title="Cuplikan dataset">
        <div className="max-h-80 overflow-auto">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-surface-2">
              <tr className="border-b border-line text-left">
                {Object.keys(data.sample_rows[0] ?? {}).map((key) => (
                  <th key={key} className="whitespace-nowrap px-2 pb-2 text-xs font-medium text-text-lo">{key}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.sample_rows.map((row, rowIndex) => (
                <tr key={rowIndex} className="border-b border-line/40 last:border-0">
                  {Object.values(row).map((value, colIndex) => (
                    <td key={colIndex} className="tnum whitespace-nowrap px-2 py-1.5 text-text-mid">
                      {typeof value === "number" ? fmt(value, 2) : String(value)}
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
