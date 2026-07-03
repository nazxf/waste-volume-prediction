import { useEffect, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import {
  Gauge,
  Info,
  LayoutDashboard,
  LineChart,
  MoreHorizontal,
  Settings,
  Sparkles,
  Trash2,
  Truck,
  X,
} from "lucide-react";
import { api } from "../lib/api";

const NAV = [
  { to: "/", label: "Dashboard", code: "01", icon: LayoutDashboard, end: true },
  { to: "/analisis", label: "Analisis Data", code: "02", icon: LineChart },
  { to: "/prediksi", label: "Prediksi", code: "03", icon: Sparkles },
  { to: "/smart-bin", label: "Smart Bin IoT", code: "04", icon: Trash2 },
  { to: "/model", label: "Performa Model", code: "05", icon: Gauge },
  { to: "/tentang", label: "Tentang", code: "06", icon: Info },
  { to: "/settings", label: "Settings", code: "07", icon: Settings },
];

const MOBILE_PRIMARY = ["/", "/prediksi", "/smart-bin", "/model"];

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
        .then((health) => {
          if (!alive) return;
          setOk(true);
          setModelLoaded(health.model_loaded);
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
  const [mobileMoreOpen, setMobileMoreOpen] = useState(false);
  const active = NAV.find((item) =>
    item.end ? location.pathname === item.to : location.pathname.startsWith(item.to),
  );

  const statusColor = ok === null ? "var(--color-text-lo)" : ok ? "var(--color-ok)" : "var(--color-full)";
  const statusText = ok === null ? "Menghubungkan" : ok ? "Terhubung" : "Terputus";
  const primaryMobileNav = NAV.filter((item) => MOBILE_PRIMARY.includes(item.to));
  const secondaryMobileNav = NAV.filter((item) => !MOBILE_PRIMARY.includes(item.to));

  useEffect(() => {
    setMobileMoreOpen(false);
  }, [location.pathname]);

  return (
    <div className="relative z-10 flex min-h-screen bg-ink-950">
      <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-line bg-surface-2 md:flex">
        <div className="flex items-center gap-3 border-b border-line px-5 py-5">
          <div className="grid h-9 w-9 place-items-center rounded-md bg-amber text-ink-950">
            <Truck size={18} strokeWidth={2.4} />
          </div>
          <div className="leading-tight">
            <div className="text-sm font-bold text-text-hi">DISPATCH</div>
            <div className="mt-0.5 text-xs text-text-lo">Waste Ops Console</div>
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
                    "group flex items-center gap-3 rounded-md border px-3 py-2.5 text-sm transition-colors",
                    isActive
                      ? "border-line-bright bg-surface-3 text-text-hi"
                      : "border-transparent text-text-mid hover:bg-surface-3 hover:text-text-hi",
                  ].join(" ")
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon size={17} strokeWidth={2} className={isActive ? "text-amber" : "text-text-lo"} />
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
              <span className="relative inline-flex h-2 w-2 rounded-full" style={{ backgroundColor: statusColor }} />
            </span>
            <span className="text-xs font-semibold" style={{ color: statusColor }}>{statusText}</span>
          </div>
          <p className="mt-2 text-xs text-text-lo">
            Model ML:{" "}
            <span style={{ color: modelLoaded ? "var(--color-ok)" : "var(--color-warn)" }}>
              {modelLoaded ? "aktif" : "belum dimuat"}
            </span>
          </p>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex items-center justify-between gap-4 border-b border-line bg-ink-950/90 px-5 py-3 backdrop-blur md:px-8">
          <div className="flex items-center gap-3">
            <span className="tnum hidden text-xs text-text-lo sm:inline">{active?.code ?? "--"}</span>
            <span className="hidden h-4 w-px bg-line sm:inline-block" />
            <h1 className="text-base font-semibold text-text-hi sm:text-lg">
              {active?.label ?? "Dashboard"}
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden text-right sm:block">
              <div className="tnum text-sm text-text-hi">
                {now.toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
              </div>
              <div className="text-xs text-text-lo">
                {now.toLocaleDateString("id-ID", { weekday: "long", day: "2-digit", month: "short" })}
              </div>
            </div>
            <span className="grid h-2.5 w-2.5 place-items-center rounded-full md:hidden" style={{ backgroundColor: statusColor }} />
          </div>
        </header>

        <main className="flex-1 px-5 pb-24 pt-6 md:px-8 md:py-8">
          <Outlet />
        </main>

        <footer className="border-t border-line px-5 py-4 text-xs text-text-lo md:px-8">
          <span className="tnum">Copyright {new Date().getFullYear()}</span> Sistem Prediksi Volume Sampah.
        </footer>
      </div>

      {mobileMoreOpen && (
        <div className="fixed inset-x-3 bottom-20 z-40 rounded-lg border border-line bg-surface-2 p-3 shadow-2xl md:hidden">
          <div className="mb-2 flex items-center justify-between px-1">
            <span className="text-sm font-semibold text-text-hi">Navigasi lainnya</span>
            <button
              type="button"
              onClick={() => setMobileMoreOpen(false)}
              className="grid h-8 w-8 place-items-center rounded-md text-text-lo hover:bg-surface-3 hover:text-text-hi"
              aria-label="Tutup navigasi lainnya"
            >
              <X size={16} />
            </button>
          </div>
          <div className="grid gap-1">
            {secondaryMobileNav.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  className={({ isActive }) =>
                    [
                      "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium",
                      isActive ? "bg-surface-3 text-text-hi" : "text-text-mid hover:bg-surface-3 hover:text-text-hi",
                    ].join(" ")
                  }
                >
                  <Icon size={17} />
                  {item.label}
                </NavLink>
              );
            })}
          </div>
        </div>
      )}

      <nav className="fixed inset-x-0 bottom-0 z-30 border-t border-line bg-ink-950/95 px-2 pb-2 pt-1.5 backdrop-blur md:hidden">
        <div className="grid grid-cols-5 gap-1">
          {primaryMobileNav.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  [
                    "flex min-h-14 flex-col items-center justify-center gap-1 rounded-md px-1 text-[0.68rem] font-medium",
                    isActive ? "bg-surface-3 text-amber" : "text-text-lo",
                  ].join(" ")
                }
              >
                <Icon size={18} />
                <span className="max-w-full truncate">{item.label.replace("Smart Bin IoT", "Smart Bin")}</span>
              </NavLink>
            );
          })}
          <button
            type="button"
            onClick={() => setMobileMoreOpen((open) => !open)}
            className={[
              "flex min-h-14 flex-col items-center justify-center gap-1 rounded-md px-1 text-[0.68rem] font-medium",
              mobileMoreOpen || secondaryMobileNav.some((item) => location.pathname.startsWith(item.to))
                ? "bg-surface-3 text-amber"
                : "text-text-lo",
            ].join(" ")}
            aria-expanded={mobileMoreOpen}
          >
            <MoreHorizontal size={18} />
            <span>Lainnya</span>
          </button>
        </div>
      </nav>
    </div>
  );
}
