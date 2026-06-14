import type { ReactNode } from "react";

/** A console panel with hairline border and optional mono eyebrow header. */
export function Panel({
  eyebrow,
  title,
  action,
  children,
  className = "",
  style,
}: {
  eyebrow?: string;
  title?: ReactNode;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
  style?: React.CSSProperties;
}) {
  return (
    <section className={`panel p-5 ${className}`} style={style}>
      {(eyebrow || title || action) && (
        <header className="mb-4 flex items-start justify-between gap-4">
          <div>
            {eyebrow && <div className="eyebrow mb-1">{eyebrow}</div>}
            {title && <h2 className="font-display text-lg font-semibold text-text-hi">{title}</h2>}
          </div>
          {action}
        </header>
      )}
      {children}
    </section>
  );
}

/** Big telemetry readout: a number with a small unit and label. */
export function StatReadout({
  label,
  value,
  unit,
  delta,
  accent,
}: {
  label: string;
  value: string;
  unit?: string;
  delta?: { value: string; positive: boolean };
  accent?: boolean;
}) {
  return (
    <div className="panel relative overflow-hidden p-5">
      <div
        className="absolute left-0 top-0 h-full w-[3px]"
        style={{ backgroundColor: accent ? "var(--color-amber)" : "var(--color-line-bright)" }}
      />
      <div className="eyebrow">{label}</div>
      <div className="mt-3 flex items-baseline gap-1.5">
        <span className="tnum font-display text-3xl font-semibold leading-none text-text-hi">{value}</span>
        {unit && <span className="text-sm text-text-lo">{unit}</span>}
      </div>
      {delta && (
        <div
          className="tnum mt-2 text-xs"
          style={{ color: delta.positive ? "var(--color-ok)" : "var(--color-high)" }}
        >
          {delta.positive ? "▲" : "▼"} {delta.value} vs rata-rata
        </div>
      )}
    </div>
  );
}
