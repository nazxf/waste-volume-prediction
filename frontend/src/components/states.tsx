import type { ReactNode } from "react";
import { AlertTriangle, Loader2, Inbox } from "lucide-react";
import { Button } from "./ui";

export function Loading({ label = "Memuat data..." }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 py-16 text-text-lo">
      <Loader2 size={18} className="animate-spin text-amber" />
      <span className="text-sm font-medium text-text-lo">{label}</span>
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="panel flex flex-col items-start gap-3 border-full/50 p-6">
      <div className="flex items-center gap-2" style={{ color: "var(--color-full)" }}>
        <AlertTriangle size={18} />
        <span className="text-sm font-semibold" style={{ color: "var(--color-full)" }}>Gagal Memuat</span>
      </div>
      <p className="text-sm text-text-mid">{message}</p>
      {onRetry && <Button onClick={onRetry}>Coba lagi</Button>}
    </div>
  );
}

export function EmptyState({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="panel flex flex-col items-center gap-3 px-6 py-12 text-center">
      <Inbox size={28} className="text-text-lo" />
      <h3 className="text-base font-semibold text-text-hi">{title}</h3>
      {children && <div className="max-w-md text-sm text-text-lo">{children}</div>}
    </div>
  );
}
