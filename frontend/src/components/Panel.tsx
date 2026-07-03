import type { ReactNode } from "react";
import { MetricCard } from "./ui";

/** Quiet product panel with hairline border and optional header. */
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
            {eyebrow && <div className="mb-1 text-xs font-medium text-text-lo">{eyebrow}</div>}
            {title && <h2 className="text-base font-semibold text-text-hi">{title}</h2>}
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
    <MetricCard
      label={label}
      value={value}
      unit={unit}
      accent={accent}
      helper={
        delta && (
          <span className="tnum" style={{ color: delta.positive ? "var(--color-ok)" : "var(--color-high)" }}>
            {delta.positive ? "Naik" : "Turun"} {delta.value} vs rata-rata
          </span>
        )
      }
    />
  );
}
