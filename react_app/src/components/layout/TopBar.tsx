/**
 * TopBar - Compact navigation bar with logo, nav links, breadcrumbs, and settings.
 */
import { useState } from "react";
import { useLocation, Link } from "react-router-dom";
import { Settings, ChevronRight } from "lucide-react";
import { motion } from "framer-motion";
import { useImportedBeamsStore } from "../../store/importedBeamsStore";
import { useDesignStore } from "../../store/designStore";
import { SettingsPanel } from "./SettingsPanel";

const routeLabels: Record<string, string> = {
  "/": "Home",
  "/start": "Get Started",
  "/design": "Beam Design",
  "/design/results": "Design Results",
  "/import": "Batch Import",
  "/editor": "Building Editor",
  "/dashboard": "Dashboard",
  "/batch": "Batch Design",
  "/settings": "Settings",
};

const navLinks = [
  { path: "/design", label: "Design" },
  { path: "/import", label: "Import" },
  { path: "/batch", label: "Batch" },
  { path: "/editor", label: "Editor" },
  { path: "/dashboard", label: "Dashboard" },
];

export function TopBar() {
  const location = useLocation();
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // Get context for badges
  const beams = useImportedBeamsStore((state) => state.beams);
  const designResult = useDesignStore((state) => state.result);

  const beamCount = beams.length;
  const hasDesignResults = designResult !== null;

  // Don't show on home page
  if (location.pathname === "/") return null;

  // Build breadcrumb segments
  const segments = location.pathname.split("/").filter(Boolean);
  const breadcrumbs = segments.map((_, i) => {
    const path = "/" + segments.slice(0, i + 1).join("/");
    return { path, label: routeLabels[path] || segments[i] };
  });

  return (
    <motion.header
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed top-0 left-0 right-0 z-40 h-14 flex items-center justify-between px-6 bg-zinc-950/80 backdrop-blur-xl border-b border-white/5"
    >
      {/* Left: Logo + Nav links */}
      <div className="flex items-center gap-4">
        <Link
          to="/"
          className="flex items-center gap-2 text-white/80 hover:text-white transition-colors"
        >
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <span className="text-sm font-semibold hidden sm:block">StructLib</span>
        </Link>

        {/* Separator */}
        <div className="hidden md:block w-px h-5 bg-white/10" />

        {/* Nav links */}
        <nav aria-label="Main navigation" className="hidden md:flex items-center gap-1">
          {navLinks.map(link => {
            const isActive = location.pathname === link.path ||
              (link.path === "/design" && location.pathname.startsWith("/design"));

            // Determine badge content
            let badge: React.ReactNode = null;
            if (link.path === "/editor" && beamCount > 0) {
              badge = (
                <span
                  className="ml-1.5 px-1.5 py-0.5 text-[10px] font-semibold rounded bg-zinc-700 text-white tabular-nums"
                  aria-label={`${beamCount} beams imported`}
                >
                  {beamCount}
                </span>
              );
            } else if (link.path === "/dashboard" && hasDesignResults) {
              badge = (
                <span
                  className="ml-1.5 w-1.5 h-1.5 rounded-full bg-green-400"
                  aria-label="Design results available"
                />
              );
            }

            return (
              <Link
                key={link.path}
                to={link.path}
                className={`px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors flex items-center ${
                  isActive
                    ? "bg-white/10 text-white"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-white/5"
                }`}
              >
                {link.label}
                {badge}
              </Link>
            );
          })}
        </nav>

        {/* Mobile: breadcrumbs */}
        <div className="flex md:hidden items-center gap-1 text-sm">
          {breadcrumbs.map((crumb, i) => (
            <div key={crumb.path} className="flex items-center gap-1">
              <ChevronRight className="w-3.5 h-3.5 text-zinc-500" aria-hidden="true" />
              {i === breadcrumbs.length - 1 ? (
                <span className="text-white/60">{crumb.label}</span>
              ) : (
                <Link
                  to={crumb.path}
                  className="text-zinc-400 hover:text-zinc-200 transition-colors"
                >
                  {crumb.label}
                </Link>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Right: Settings */}
      <button
        aria-label="Settings"
        onClick={() => setIsSettingsOpen(true)}
        className="p-2 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-white/5 transition-colors"
      >
        <Settings className="w-4.5 h-4.5" />
      </button>

      {/* Settings Panel */}
      <SettingsPanel isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
    </motion.header>
  );
}
