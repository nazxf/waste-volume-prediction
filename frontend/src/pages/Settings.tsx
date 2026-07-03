import { Activity, Bell, Database, KeyRound, RefreshCw, ShieldCheck, SlidersHorizontal } from "lucide-react";
import { api } from "../lib/api";
import { useAsync } from "../lib/useAsync";
import { formatTimestamp } from "../lib/format";
import { Panel } from "../components/Panel";
import { Loading, ErrorState } from "../components/states";
import { Alert, Button, MetricCard } from "../components/ui";

export default function Settings() {
  const info = useAsync(() => api.info(), []);
  const health = useAsync(() => api.health(), []);
  const model = useAsync(() => api.modelPerformance(), []);
  const readings = useAsync(() => api.latestReadings(5), []);

  const loading = info.loading || health.loading || model.loading || readings.loading;
  const error = info.error || health.error || model.error || readings.error;

  function reloadAll() {
    info.reload();
    health.reload();
    model.reload();
    readings.reload();
  }

  if (loading) return <Loading label="Memuat pengaturan..." />;
  if (error) return <ErrorState message={error} onRetry={reloadAll} />;

  const checks = health.data?.checks ?? {};
  const metadata = model.data?.metadata ?? {};
  const trainedAt = metadata.trained_at ? String(metadata.trained_at) : "Belum tersedia";
  const bestModel = metadata.best_model_name ? String(metadata.best_model_name) : "Belum tersedia";
  const latestReading = readings.data?.[0];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-medium text-text-lo">Konfigurasi</p>
          <h2 className="mt-1 text-2xl font-semibold text-text-hi">Settings</h2>
        </div>
        <Button onClick={reloadAll} icon={RefreshCw}>Refresh status</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="API" value={health.data?.status ?? "--"} helper={info.data?.version ? `Versi ${info.data.version}` : "Versi tidak tersedia"} accent={health.data?.status === "healthy"} />
        <MetricCard label="Model ML" value={health.data?.model_loaded ? "Aktif" : "Tidak aktif"} helper={bestModel} />
        <MetricCard label="Dataset" value={checks.dataset_available ? "Tersedia" : "Tidak ada"} helper="data/raw/waste_dataset.csv" />
        <MetricCard label="IoT terakhir" value={latestReading ? latestReading.bin_id : "--"} helper={latestReading ? formatTimestamp(latestReading.created_at) : "Belum ada data"} />
      </div>

      <Panel eyebrow="Runtime" title="Status layanan">
        <div className="grid gap-3 md:grid-cols-2">
          <StatusRow icon={Activity} label="API health" value={health.data?.message ?? "--"} ok={health.data?.status === "healthy"} />
          <StatusRow icon={Database} label="SQLite writable" value={String(Boolean(checks.sqlite_writable))} ok={Boolean(checks.sqlite_writable)} />
          <StatusRow icon={Database} label="Dataset available" value={String(Boolean(checks.dataset_available))} ok={Boolean(checks.dataset_available)} />
          <StatusRow icon={ShieldCheck} label="PDF export available" value={String(Boolean(checks.pdf_export_available))} ok={Boolean(checks.pdf_export_available)} />
        </div>
      </Panel>

      <div className="grid gap-6 lg:grid-cols-2">
        <Panel eyebrow="Model" title="Informasi model">
          <div className="space-y-3 text-sm">
            <KeyValue label="Model terbaik" value={bestModel} />
            <KeyValue label="Waktu training" value={trainedAt} />
            <KeyValue label="Report tersedia" value={model.data?.available ? "Ya" : "Tidak"} />
            <KeyValue label="Feature importance" value={model.data?.feature_importance.length ? `${model.data.feature_importance.length} fitur` : "Tidak tersedia"} />
          </div>
        </Panel>

        <Panel eyebrow="Integrasi" title="IoT dan notifikasi">
          <div className="space-y-4">
            <Alert tone="info" icon={KeyRound} title="API key IoT">
              <p>Perangkat ESP32 memakai header X-API-Key saat IOT_API_KEY disetel di backend.</p>
            </Alert>
            <Alert tone="info" icon={Bell} title="Channel notifikasi">
              <p>Backend mendukung channel email dan SMS untuk workflow notifikasi prediksi.</p>
            </Alert>
          </div>
        </Panel>
      </div>

      <Panel eyebrow="Endpoint" title="Daftar endpoint API">
        <div className="grid gap-2 md:grid-cols-2">
          {Object.entries(info.data?.endpoints ?? {}).map(([name, path]) => (
            <div key={name} className="rounded-md border border-line bg-surface-1 p-3">
              <div className="text-xs font-medium text-text-lo">{name}</div>
              <div className="tnum mt-1 text-sm text-text-hi">{path}</div>
            </div>
          ))}
        </div>
      </Panel>

      <Panel eyebrow="Preferensi" title="Pengaturan operasional">
        <div className="grid gap-3 md:grid-cols-3">
          <Preference icon={SlidersHorizontal} label="Default export" value="Excel dan PDF" />
          <Preference icon={Bell} label="Alert threshold" value="Diatur per request" />
          <Preference icon={Database} label="Data source" value="Dataset lokal + SQLite IoT" />
        </div>
      </Panel>
    </div>
  );
}

function StatusRow({
  icon: Icon,
  label,
  value,
  ok,
}: {
  icon: typeof Activity;
  label: string;
  value: string;
  ok: boolean;
}) {
  return (
    <div className="flex items-start gap-3 rounded-md border border-line bg-surface-1 p-3">
      <Icon size={17} className="mt-0.5" style={{ color: ok ? "var(--color-ok)" : "var(--color-warn)" }} />
      <div>
        <div className="text-sm font-medium text-text-hi">{label}</div>
        <div className="mt-1 text-xs text-text-mid">{value}</div>
      </div>
    </div>
  );
}

function KeyValue({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between gap-3 border-b border-line/60 pb-2 last:border-0 last:pb-0">
      <span className="text-text-lo">{label}</span>
      <span className="text-right text-text-hi">{value}</span>
    </div>
  );
}

function Preference({ icon: Icon, label, value }: { icon: typeof SlidersHorizontal; label: string; value: string }) {
  return (
    <div className="rounded-md border border-line bg-surface-1 p-4">
      <Icon size={18} className="text-amber" />
      <div className="mt-3 text-sm font-medium text-text-hi">{label}</div>
      <div className="mt-1 text-xs text-text-lo">{value}</div>
    </div>
  );
}
