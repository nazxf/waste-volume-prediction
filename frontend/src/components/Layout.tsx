import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  LineChart,
  Sparkles,
  Trash2,
  Gauge,
  Info,
  Truck,
} from "lucide-react";
import { api } from "../lib/api";

const NAV = [
  { to: "/", label: "Dashboard", code: "01", icon: LayoutDashboard, end: true },
  { to: "/analisis", label: "Analisis Data", code: "02", icon: LineChart },
  { to: "/prediksi", label: "Prediksi", code: "03", icon: Sparkles },
  { to: "/smart-bin", label: "Smart Bin IoT", code: "04", icon: Trash2 },
  { to: "/model", label: "Performa Model", code: "05", icon: Gauge },
  { to: "/tentang", label: "Tentang", code: "06", icon: Info },
];

function useClock() {
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);
  return now;
}

function useHealth() {
  const [ok, setOk] = useState<boolean | null>(null);
  const [modelLoaded, setModelLoaded] = useState(false);
  useEffect(() => {
    let alive = true;
    const ping = () =>
      api
        .health()
        .then((h) => {
          if (!alive) return;
          setOk(true);
          setModelLoaded(h.model_loaded);
        })
        .catch(() => alive && setOk(false));
    ping();
    const id = setInterval(ping, 15000);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);
  return { ok, modelLoaded };
}

export default function Layout() {
  const now = useClock();
  const { ok, modelLoaded } = useHealth();
  const location = useLocation();
  const active = NAV.find((n) => (n.end ? location.pathname === n.to : location.pathname.startsWith(n.to)));

  const statusColor = ok === null ? "var(--color-text-lo)" : ok ? "var(--color-ok)" : "var(--color-full)";
  const statusText = ok === null ? "MENGHUBUNGKAN" : ok ? "TERHUBUNG" : "TERPUTUS";

  return (
    <div className="relative z-10 flex min-h-screen">
      {/* Left rail */}
      <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-line bg-ink-800/80 backdrop-blur md:flex">
        <div className="flex items-center gap-3 border-b border-line px-5 py-5">
          <div className="grid h-9 w-9 place-items-center rounded-sm bg-amber text-ink-900">
            <Truck size={18} strokeWidth={2.4} />
          </div>
          <div className="leading-tight">
            <div className="font-display text-sm font-bold tracking-tight text-text-hi">DISPATCH</div>
            <div className="eyebrow !text-[0.6rem]">Waste Ops Console</div>
          </div>
        </div>

        <nav className="flex flex-1 flex-col gap-1 p-3">
          {NAV.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  [
                    "group relative flex items-center gap-3 rounded-sm px-3 py-2.5 text-sm transition-colors",
                    isActive
                      ? "bg-ink-600 text-text-hi"
                      : "text-text-mid hover:bg-ink-700 hover:text-text-hi",
                  ].join(" ")
                }
              >
                {({ isActive }) => (
                  <>
                    <span
                      className="absolute left-0 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-r bg-amber transition-opacity"
                      style={{ opacity: isActive ? 1 : 0 }}
                    />
                    <Icon size={17} strokeWidth={2} className={isActive ? "text-amber" : ""} />
                    <span className="flex-1 font-medium">{item.label}</span>
                    <span className="tnum text-[0.65rem] text-text-lo">{item.code}</span>
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>

        <div className="border-t border-line p-4">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              {ok && (
                <span
                  className="absolute inline-flex h-full w-full animate-ping rounded-full opacity-60"
                  style={{ backgroundColor: statusColor }}
                />
              )}
              <span className="relative inline-flex h-2 w-2 rounded-full" style={{ backgroundColor: statusColor }} />
            </span>
            <span className="eyebrow" style={{ color: statusColor }}>{statusText}</span>
          </div>
          <p className="mt-2 text-[0.7rem] text-text-lo">
            Model ML:{" "}
            <span style={{ color: modelLoaded ? "var(--color-ok)" : "var(--color-warn)" }}>
              {modelLoaded ? "aktif" : "belum dimuat"}
            </span>
          </p>
        </div>
      </aside>

      {/* Main column */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Top status bar */}
        <header className="sticky top-0 z-20 flex items-center justify-between gap-4 border-b border-line bg-ink-900/85 px-5 py-3 backdrop-blur md:px-8">
          <div className="flex items-center gap-3">
            <span className="eyebrow hidden sm:inline">{active?.code ?? "—"}</span>
            <span className="hidden h-4 w-px bg-line sm:inline-block" />
            <h1 className="font-display text-base font-semibold text-text-hi sm:text-lg">
              {active?.label ?? "Dashboard"}
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden text-right sm:block">
              <div className="tnum text-sm text-text-hi">
                {now.toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
              </div>
              <div className="eyebrow !text-[0.6rem]">
                {now.toLocaleDateString("id-ID", { weekday: "long", day: "2-digit", month: "short" })}
              </div>
            </div>
            <span
              className="grid h-2.5 w-2.5 place-items-center rounded-full md:hidden"
              style={{ backgroundColor: statusColor }}
            />
          </div>
        </header>

        {/* Mobile nav */}
        <nav className="flex gap-1 overflow-x-auto border-b border-line bg-ink-800 px-3 py-2 md:hidden">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                [
                  "whitespace-nowrap rounded-sm px-3 py-1.5 text-xs font-medium",
                  isActive ? "bg-amber text-ink-900" : "text-text-mid",
                ].join(" ")
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <main className="flex-1 px-5 py-6 md:px-8 md:py-8">
          <Outlet />
        </main>

        <footer className="border-t border-line px-5 py-4 text-[0.7rem] text-text-lo md:px-8">
          <span className="tnum">© {new Date().getFullYear()}</span> Sistem Prediksi Volume Sampah ·
          Antarmuka React berdampingan dengan dashboard Streamlit.
        </footer>
      </div>
    </div>
  );
}
