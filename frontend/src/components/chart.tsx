import type { ReactNode } from "react";

/** Shared chart theme so every Recharts chart matches the console look. */
export const CHART = {
  amber: "#f2a33c",
  ok: "#3fb98c",
  full: "#e5564e",
  axis: "#6e8087",
  grid: "#2a363d",
  fontMono: "var(--font-mono)",
};

export const axisProps = {
  stroke: CHART.axis,
  tick: { fill: CHART.axis, fontSize: 11, fontFamily: CHART.fontMono },
  tickLine: false,
  axisLine: { stroke: CHART.grid },
} as const;

/** Dark console tooltip for all charts. */
export function ChartTooltip({
  active,
  payload,
  label,
  unit = "",
  labelFormatter,
}: {
  active?: boolean;
  payload?: { name: string; value: number; color: string }[];
  label?: string | number;
  unit?: string;
  labelFormatter?: (label: string | number) => string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="panel !rounded-sm border-line-bright px-3 py-2 text-xs shadow-lg">
      {label !== undefined && (
        <div className="eyebrow mb-1.5">{labelFormatter ? labelFormatter(label) : label}</div>
      )}
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2 py-0.5">
          <span className="h-2 w-2 rounded-full" style={{ backgroundColor: p.color }} />
          <span className="text-text-mid">{p.name}</span>
          <span className="tnum ml-auto font-medium text-text-hi">
            {typeof p.value === "number" ? p.value.toLocaleString("id-ID", { maximumFractionDigits: 2 }) : p.value}
            {unit}
          </span>
        </div>
      ))}
    </div>
  );
}

/** A titled frame around a chart with consistent spacing. */
export function ChartFrame({ children, height = 320 }: { children: ReactNode; height?: number }) {
  return <div style={{ width: "100%", height }}>{children}</div>;
}
