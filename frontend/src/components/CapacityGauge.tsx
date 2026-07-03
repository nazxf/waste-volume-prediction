import { STATUS_COLOR, fillStatus } from "../lib/format";

export function CapacityGauge({
  percent,
  readout,
  unit,
  caption,
  color,
  height = 220,
  pulse = false,
}: {
  percent: number;
  readout: string;
  unit?: string;
  caption?: string;
  color?: string;
  height?: number;
  pulse?: boolean;
}) {
  const clamped = Math.max(0, Math.min(100, percent));
  const fillColor = color ?? STATUS_COLOR[fillStatus(clamped)];
  const ticks = [100, 80, 60, 40, 20, 0];

  return (
    <div className="flex items-stretch gap-3">
      <div className="flex flex-col justify-between py-[2px]" style={{ height }}>
        {ticks.map((tick) => (
          <span key={tick} className="tnum text-[0.6rem] leading-none text-text-lo">
            {tick}
          </span>
        ))}
      </div>

      <div className="relative w-16 overflow-hidden rounded-md border border-line-bright bg-surface-1" style={{ height }}>
        {ticks.slice(1, -1).map((tick) => (
          <span key={tick} className="absolute left-0 w-full border-t border-line" style={{ bottom: `${tick}%` }} />
        ))}
        <div
          className="absolute bottom-0 left-0 w-full transition-[height] duration-700 ease-out"
          style={{
            height: `${clamped}%`,
            background: `linear-gradient(to top, ${fillColor}, ${fillColor}cc)`,
            boxShadow: `0 0 18px ${fillColor}40`,
          }}
        >
          <span className="absolute left-0 top-0 h-[2px] w-full" style={{ backgroundColor: fillColor, opacity: 0.9 }} />
          {pulse && <span className="absolute left-0 top-0 h-[2px] w-full animate-pulse bg-text-hi opacity-50" />}
        </div>
      </div>

      <div className="flex flex-col justify-center">
        <div className="flex items-baseline gap-1">
          <span className="tnum text-2xl font-semibold leading-none" style={{ color: fillColor }}>
            {readout}
          </span>
          {unit && <span className="text-xs text-text-lo">{unit}</span>}
        </div>
        {caption && <p className="mt-1.5 max-w-[10rem] text-xs leading-snug text-text-lo">{caption}</p>}
      </div>
    </div>
  );
}
