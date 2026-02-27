/**
 * TopBar - Minimal navigation bar with logo, breadcrumbs, and settings.
 */
import { useLocation, useNavigate, Link } from "react-router-dom";
import { Settings, ChevronRight } from "lucide-react";
import { motion } from "framer-motion";

const routeLabels: Record<string, string> = {
  "/": "Home",
  "/start": "Get Started",
  "/design": "Beam Design",
  "/design/results": "Design Results",
  "/import": "Batch Import",
  "/editor": "Building Editor",
  "/dashboard": "Dashboard",
  "/settings": "Settings",
};

export function TopBar() {
  const location = useLocation();
  const navigate = useNavigate();

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
      {/* Left: Logo + Breadcrumbs */}
      <div className="flex items-center gap-3">
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

        {breadcrumbs.length > 0 && (
          <div className="flex items-center gap-1 text-sm">
            {breadcrumbs.map((crumb, i) => (
              <div key={crumb.path} className="flex items-center gap-1">
                <ChevronRight className="w-3.5 h-3.5 text-white/30" />
                {i === breadcrumbs.length - 1 ? (
                  <span className="text-white/60">{crumb.label}</span>
                ) : (
                  <Link
                    to={crumb.path}
                    className="text-white/40 hover:text-white/70 transition-colors"
                  >
                    {crumb.label}
                  </Link>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Right: Settings */}
      <button
        onClick={() => navigate("/settings")}
        className="p-2 rounded-lg text-white/40 hover:text-white/70 hover:bg-white/5 transition-colors"
      >
        <Settings className="w-4.5 h-4.5" />
      </button>
    </motion.header>
  );
}
