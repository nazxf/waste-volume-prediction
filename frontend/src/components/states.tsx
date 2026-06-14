import type { ReactNode } from "react";
import { AlertTriangle, Loader2, Inbox } from "lucide-react";

export function Loading({ label = "Memuat data…" }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 py-16 text-text-lo">
      <Loader2 size={18} className="animate-spin text-amber" />
      <span className="eyebrow">{label}</span>
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="panel flex flex-col items-start gap-3 border-l-2 p-6" style={{ borderLeftColor: "var(--color-full)" }}>
      <div className="flex items-center gap-2" style={{ color: "var(--color-full)" }}>
        <AlertTriangle size={18} />
        <span className="eyebrow" style={{ color: "var(--color-full)" }}>Gagal Memuat</span>
      </div>
      <p className="text-sm text-text-mid">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-1 rounded-sm border border-line-bright px-3 py-1.5 text-xs font-medium text-text-hi transition-colors hover:bg-ink-700"
        >
          Coba lagi
        </button>
      )}
    </div>
  );
}

export function EmptyState({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="panel flex flex-col items-center gap-3 px-6 py-12 text-center">
      <Inbox size={28} className="text-text-lo" />
      <h3 className="font-display text-base font-semibold text-text-hi">{title}</h3>
      {children && <div className="max-w-md text-sm text-text-lo">{children}</div>}
    </div>
  );
}
