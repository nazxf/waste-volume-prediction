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
import { Trophy } from "lucide-react";
import { api, assetUrl } from "../lib/api";
import { useAsync } from "../lib/useAsync";
import { fmt } from "../lib/format";
import { Panel } from "../components/Panel";
import { ChartTooltip, CHART, axisProps } from "../components/chart";
import { Loading, ErrorState, EmptyState } from "../components/states";

export default function ModelPerformance() {
  const { data, loading, error, reload } = useAsync(() => api.modelPerformance(), []);

  if (loading) return <Loading />;
  if (error || !data) return <ErrorState message={error ?? "Data tidak tersedia"} onRetry={reload} />;
  if (!data.available)
    return <EmptyState title="Performa model belum tersedia">Jalankan pelatihan model terlebih dahulu.</EmptyState>;

  const metrics = (data.metadata.test_metrics ?? {}) as Record<string, number>;
  const bestName = String(data.metadata.best_model_name ?? "—");
  const trainedAt = data.metadata.trained_at ? String(data.metadata.trained_at) : null;

  return (
    <div className="space-y-6">
      {/* Best model headline */}
      <section className="panel rise flex flex-wrap items-center justify-between gap-4 p-6">
        <div>
          <div className="eyebrow">Model Terbaik</div>
          <div className="mt-2 flex items-center gap-2">
            <Trophy size={22} className="text-amber" />
            <span className="font-display text-3xl font-bold text-text-hi">{bestName}</span>
          </div>
          {trainedAt && <p className="tnum mt-1 text-xs text-text-lo">Dilatih: {trainedAt}</p>}
        </div>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <Metric label="R²" value={metrics.R2 !== undefined ? fmt(metrics.R2, 4) : "—"} highlight />
          <Metric label="RMSE" value={metrics.RMSE !== undefined ? fmt(metrics.RMSE, 2) : "—"} unit="ton" />
          <Metric label="MAE" value={metrics.MAE !== undefined ? fmt(metrics.MAE, 2) : "—"} unit="ton" />
          <Metric label="MAPE" value={metrics.MAPE !== undefined ? `${fmt(metrics.MAPE, 2)}%` : "—"} />
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Feature importance */}
        {data.feature_importance.length > 0 && (
          <Panel eyebrow="Penggerak Prediksi" title="Feature Importance">
            <div style={{ width: "100%", height: 360 }}>
              <ResponsiveContainer>
                <BarChart
                  data={data.feature_importance}
                  layout="vertical"
                  margin={{ top: 4, right: 16, bottom: 4, left: 8 }}
                >
                  <CartesianGrid stroke={CHART.grid} horizontal={false} />
                  <XAxis type="number" {...axisProps} />
                  <YAxis type="category" dataKey="feature" {...axisProps} width={120} />
                  <Tooltip content={<ChartTooltip />} cursor={{ fill: "#ffffff08" }} />
                  <Bar dataKey="importance" name="Importance" radius={[0, 2, 2, 0]}>
                    {data.feature_importance.map((_, i) => (
                      <Cell key={i} fill={i === 0 ? CHART.amber : "#3a4b54"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Panel>
        )}

        {/* Model comparison */}
        {data.model_comparison.length > 0 && (
          <Panel eyebrow="Evaluasi" title="Perbandingan Model">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-line text-left">
                  {["Model", "MAE", "RMSE", "R²", "MAPE"].map((h) => (
                    <th key={h} className="eyebrow pb-2 pr-3 font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.model_comparison.map((m) => (
                  <tr key={m.model} className="border-b border-line/50 last:border-0">
                    <td className="py-2.5 pr-3">
                      <span className="flex items-center gap-1.5 text-text-hi">
                        {m.is_best && <Trophy size={13} className="text-amber" />}
                        {m.model}
                      </span>
                    </td>
                    <td className="tnum py-2.5 pr-3 text-text-mid">{fmt(m.mae, 2)}</td>
                    <td className="tnum py-2.5 pr-3 text-text-mid">{fmt(m.rmse, 2)}</td>
                    <td className="tnum py-2.5 pr-3" style={{ color: m.is_best ? "var(--color-amber)" : "var(--color-text-mid)" }}>
                      {fmt(m.r2, 4)}
                    </td>
                    <td className="tnum py-2.5 pr-3 text-text-mid">{fmt(m.mape, 2)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Panel>
        )}
      </div>

      {/* Report images */}
      <div className="grid gap-6 lg:grid-cols-2">
        {data.has_feature_importance_image && (
          <Panel eyebrow="Visual" title="Feature Importance (Report)">
            <img src={assetUrl("/model/feature-importance.png")} alt="Feature importance" className="w-full rounded-sm border border-line" />
          </Panel>
        )}
        {data.has_prediction_comparison_image && (
          <Panel eyebrow="Visual" title="Perbandingan Prediksi">
            <img src={assetUrl("/model/prediction-comparison.png")} alt="Prediction comparison" className="w-full rounded-sm border border-line" />
          </Panel>
        )}
      </div>

      {/* Raw report */}
      {data.report_markdown && (
        <Panel eyebrow="Dokumen" title="Laporan Evaluasi">
          <pre className="max-h-96 overflow-auto whitespace-pre-wrap rounded-sm bg-ink-900 p-4 text-xs leading-relaxed text-text-mid">
            {data.report_markdown}
          </pre>
        </Panel>
      )}
    </div>
  );
}

function Metric({ label, value, unit, highlight }: { label: string; value: string; unit?: string; highlight?: boolean }) {
  return (
    <div className="rounded-sm border border-line bg-ink-900/60 px-3 py-2.5">
      <div className="eyebrow !text-[0.6rem]">{label}</div>
      <div
        className="tnum mt-1 font-display text-xl font-semibold"
        style={{ color: highlight ? "var(--color-amber)" : "var(--color-text-hi)" }}
      >
        {value}
        {unit && <span className="ml-1 text-xs font-normal text-text-lo">{unit}</span>}
      </div>
    </div>
  );
}
