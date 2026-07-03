import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import { Loader2 } from "lucide-react";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";

const BUTTON_VARIANTS: Record<ButtonVariant, string> = {
  primary: "border-amber bg-amber text-ink-950 hover:border-amber-deep hover:bg-amber-deep",
  secondary: "border-line-bright bg-surface-2 text-text-hi hover:bg-surface-3",
  ghost: "border-transparent bg-transparent text-text-mid hover:bg-surface-2 hover:text-text-hi",
  danger: "border-full/50 bg-full/10 text-full hover:bg-full/15",
};

export function Button({
  children,
  icon: Icon,
  loading = false,
  variant = "secondary",
  className = "",
  disabled,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  icon?: LucideIcon;
  loading?: boolean;
  variant?: ButtonVariant;
}) {
  const BusyIcon = loading ? Loader2 : Icon;
  return (
    <button
      {...props}
      disabled={disabled || loading}
      className={[
        "inline-flex min-h-9 items-center justify-center gap-2 rounded-md border px-3 py-2 text-sm font-medium",
        "transition-colors disabled:cursor-not-allowed disabled:opacity-55",
        BUTTON_VARIANTS[variant],
        className,
      ].join(" ")}
    >
      {BusyIcon && <BusyIcon size={16} className={loading ? "animate-spin" : ""} />}
      {children}
    </button>
  );
}

export function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-xs font-medium text-text-mid">{label}</span>
      {children}
      {hint && <span className="mt-1 block text-xs text-text-lo">{hint}</span>}
    </label>
  );
}

export function TextInput(props: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className={[
        "w-full rounded-md border border-line bg-surface-1 px-3 py-2 text-sm text-text-hi",
        "transition-colors placeholder:text-text-lo hover:border-line-bright focus:border-amber",
        props.className ?? "",
      ].join(" ")}
    />
  );
}

export function Slider({
  label,
  unit,
  min,
  max,
  step,
  value,
  onChange,
}: {
  label: string;
  unit?: string;
  min: number;
  max: number;
  step: number;
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-3">
        <span className="text-xs font-medium text-text-mid">{label}</span>
        <span className="tnum text-sm text-text-hi">
          {value}
          {unit && <span className="ml-0.5 text-text-lo">{unit}</span>}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
        className="w-full accent-amber"
      />
    </div>
  );
}

export function Toggle({
  label,
  value,
  onChange,
}: {
  label: string;
  value: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onChange(!value)}
      className="flex w-full items-center justify-between rounded-md border border-line bg-surface-1 px-3 py-2 text-sm transition-colors hover:border-line-bright"
      aria-pressed={value}
    >
      <span className={value ? "text-text-hi" : "text-text-lo"}>{label}</span>
      <span
        className="relative h-5 w-9 rounded-full transition-colors"
        style={{ backgroundColor: value ? "var(--color-amber)" : "var(--color-line-bright)" }}
      >
        <span
          className="absolute top-0.5 h-4 w-4 rounded-full bg-ink-950 transition-all"
          style={{ left: value ? "1.125rem" : "0.125rem" }}
        />
      </span>
    </button>
  );
}

export function Alert({
  tone = "info",
  icon: Icon,
  title,
  children,
}: {
  tone?: "info" | "success" | "warning" | "danger";
  icon?: LucideIcon;
  title: string;
  children?: ReactNode;
}) {
  const color = {
    info: "var(--color-info)",
    success: "var(--color-ok)",
    warning: "var(--color-warn)",
    danger: "var(--color-full)",
  }[tone];

  return (
    <div className="rounded-md border bg-surface-1 p-4" style={{ borderColor: `${color}66` }}>
      <div className="flex items-start gap-3">
        {Icon && <Icon size={18} className="mt-0.5 shrink-0" style={{ color }} />}
        <div>
          <div className="text-sm font-semibold" style={{ color }}>{title}</div>
          {children && <div className="mt-1 text-sm text-text-mid">{children}</div>}
        </div>
      </div>
    </div>
  );
}

export function MetricCard({
  label,
  value,
  unit,
  helper,
  accent = false,
}: {
  label: string;
  value: string;
  unit?: string;
  helper?: ReactNode;
  accent?: boolean;
}) {
  return (
    <div className={`panel p-5 ${accent ? "border-amber/60 bg-amber/5" : ""}`}>
      <div className="text-xs font-medium text-text-lo">{label}</div>
      <div className="mt-2 flex items-baseline gap-1.5">
        <span className="tnum text-3xl font-semibold leading-none text-text-hi">{value}</span>
        {unit && <span className="text-sm text-text-lo">{unit}</span>}
      </div>
      {helper && <div className="mt-2 text-xs text-text-mid">{helper}</div>}
    </div>
  );
}
