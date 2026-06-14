import { STATUS_COLOR, fillStatus } from "../lib/format";

/**
 * CapacityGauge — the dashboard's signature element.
 *
 * A vertical "tank" that fills from the bottom to represent how full something
 * is: a smart bin's level, or predicted volume against fleet capacity. The fill
 * height animates on change and the color follows fill-status semantics unless
 * overridden. This single motif ties the whole console together: everything
 * here is about how full something is.
 */
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
      {/* Scale */}
      <div className="flex flex-col justify-between py-[2px]" style={{ height }}>
        {ticks.map((t) => (
          <span key={t} className="tnum text-[0.6rem] leading-none text-text-lo">
            {t}
          </span>
        ))}
      </div>

      {/* Tank */}
      <div
        className="relative w-16 overflow-hidden rounded-sm border border-line-bright bg-ink-900"
        style={{ height }}
      >
        {/* gridlines */}
        {ticks.slice(1, -1).map((t) => (
          <span
            key={t}
            className="absolute left-0 w-full border-t border-line"
            style={{ bottom: `${t}%` }}
          />
        ))}
        {/* fill */}
        <div
          className="absolute bottom-0 left-0 w-full transition-[height] duration-700 ease-out"
          style={{
            height: `${clamped}%`,
            background: `linear-gradient(to top, ${fillColor}, ${fillColor}cc)`,
            boxShadow: `0 0 24px ${fillColor}55`,
          }}
        >
          {/* liquid surface line */}
          <span
            className="absolute left-0 top-0 h-[2px] w-full"
            style={{ backgroundColor: fillColor, opacity: 0.9 }}
          />
          {pulse && (
            <span
              className="absolute left-0 top-0 h-[2px] w-full animate-pulse"
              style={{ backgroundColor: "#fff", opacity: 0.5 }}
            />
          )}
        </div>
      </div>

      {/* Readout */}
      <div className="flex flex-col justify-center">
        <div className="flex items-baseline gap-1">
          <span className="tnum font-display text-2xl font-semibold leading-none" style={{ color: fillColor }}>
            {readout}
          </span>
          {unit && <span className="text-xs text-text-lo">{unit}</span>}
        </div>
        {caption && <p className="mt-1.5 max-w-[10rem] text-xs leading-snug text-text-lo">{caption}</p>}
      </div>
    </div>
  );
}
