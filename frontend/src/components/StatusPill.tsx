import { STATUS_COLOR, STATUS_LABEL, type FillStatus } from "../lib/format";

/** Small colored status chip for a bin fill status. */
export function StatusPill({ status, size = "md" }: { status: FillStatus; size?: "sm" | "md" }) {
  const color = STATUS_COLOR[status];
  const pad = size === "sm" ? "px-2 py-0.5 text-[0.65rem]" : "px-2.5 py-1 text-xs";
  return (
    <span
      className={`tnum inline-flex items-center gap-1.5 rounded-sm font-medium tracking-wide ${pad}`}
      style={{ color, backgroundColor: `${color}1f`, border: `1px solid ${color}40` }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: color }} />
      {STATUS_LABEL[status]}
    </span>
  );
}
