import type { ReactNode } from "react";

/** Shared chart theme so every Recharts chart uses the same semantic vocabulary. */
export const CHART = {
  primary: "#f2a33c",
  amber: "#f2a33c",
  neutral: "#4a5d65",
  info: "#5aa9e6",
  ok: "#3fb98c",
  warn: "#f2c14e",
  high: "#f08a3c",
  full: "#e5564e",
  axis: "#718187",
  grid: "#26343a",
  threshold: "#f2c14e",
  font: "var(--font-sans)",
  fontMono: "var(--font-mono)",
};

export const axisProps = {
  stroke: CHART.axis,
  tick: { fill: CHART.axis, fontSize: 11, fontFamily: CHART.font },
  tickLine: false,
  axisLine: { stroke: CHART.grid },
} as const;

export const referenceLineProps = {
  stroke: CHART.threshold,
  strokeDasharray: "4 4",
  strokeOpacity: 0.8,
} as const;

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
    <div className="panel !rounded-md border-line-bright px-3 py-2 text-xs shadow-lg">
      {label !== undefined && (
        <div className="mb-1.5 text-xs font-medium text-text-lo">
          {labelFormatter ? labelFormatter(label) : label}
        </div>
      )}
      {payload.map((point, index) => (
        <div key={index} className="flex items-center gap-2 py-0.5">
          <span className="h-2 w-2 rounded-full" style={{ backgroundColor: point.color }} />
          <span className="text-text-mid">{point.name}</span>
          <span className="tnum ml-auto font-medium text-text-hi">
            {typeof point.value === "number"
              ? point.value.toLocaleString("id-ID", { maximumFractionDigits: 2 })
              : point.value}
            {unit}
          </span>
        </div>
      ))}
    </div>
  );
}

export function ChartFrame({ children, height = 320 }: { children: ReactNode; height?: number }) {
  return <div style={{ width: "100%", height }}>{children}</div>;
}
