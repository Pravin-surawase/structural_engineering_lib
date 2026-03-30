/**
 * HubPage — Smart landing page with quick actions and last session context.
 * Replaces ModeSelectPage as the /start route.
 */
import { useNavigate } from "react-router-dom";
import { useMemo, useEffect } from "react";
import { useImportedBeamsStore } from "../../store/importedBeamsStore";

const LS_KEY = "structlib_last_session";

interface LastSession {
  projectName: string;
  beamCount: number;
  passRate: number;
  timestamp: number;
}

function saveSession(data: LastSession) {
  try {
    localStorage.setItem(LS_KEY, JSON.stringify(data));
  } catch { /* quota exceeded — ignore */ }
}

function loadSession(): LastSession | null {
  try {
    const raw = localStorage.getItem(LS_KEY);
    return raw ? (JSON.parse(raw) as LastSession) : null;
  } catch {
    return null;
  }
}

function timeAgo(ts: number): string {
  const diff = Date.now() - ts;
  const mins = Math.floor(diff / 60_000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins} min ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs} hr ago`;
  const days = Math.floor(hrs / 24);
  return `${days} day${days > 1 ? "s" : ""} ago`;
}

export function HubPage() {
  const navigate = useNavigate();
  const beams = useImportedBeamsStore((s) => s.beams);

  // Derive live stats from store
  const { beamCount, passRate } = useMemo(() => {
    const count = beams.length;
    if (count === 0) return { beamCount: 0, passRate: 0 };
    const passed = beams.filter((b) => b.status === "pass").length;
    const designed = beams.filter((b) => b.status === "pass" || b.status === "fail" || b.status === "warning").length;
    const rate = designed > 0 ? Math.round((passed / designed) * 100) : 0;
    return { beamCount: count, passRate: rate };
  }, [beams]);

  // Persist session whenever beams change
  useEffect(() => {
    if (beamCount > 0) {
      const name = beams[0]?.story ? `Project · ${beams[0].story}` : "Untitled Project";
      saveSession({ projectName: name, beamCount, passRate, timestamp: Date.now() });
    }
  }, [beams, beamCount, passRate]);

  const lastSession = useMemo(() => {
    // Prefer live store data; fall back to localStorage
    if (beamCount > 0) {
      const name = beams[0]?.story ? `Project · ${beams[0].story}` : "Untitled Project";
      return { projectName: name, beamCount, passRate, timestamp: Date.now() } as LastSession;
    }
    return loadSession();
  }, [beams, beamCount, passRate]);

  const quickActions = [
    { emoji: "🔧", label: "New Beam Design", to: "/design" },
    { emoji: "📁", label: "Import CSV / ETABS", to: "/import" },
    { emoji: "📊", label: "Open Dashboard", to: "/dashboard" },
  ] as const;

  const badges = ["IS 456:2000", "Live 3D", "BBS / DXF", "ETABS / SAFE"] as const;

  return (
    <div className="h-screen w-screen bg-zinc-950 flex flex-col items-center justify-center px-6 pt-14">
      {/* Header */}
      <h1 className="text-3xl md:text-4xl font-bold text-white mb-10 tracking-tight">
        StructLib
      </h1>

      <div className="flex flex-col md:flex-row gap-6 w-full max-w-3xl">
        {/* Quick Actions */}
        <div className="flex-1 rounded-2xl border border-white/10 bg-white/[0.03] p-6">
          <h2 className="text-sm font-semibold text-white/50 uppercase tracking-wider mb-4">
            Quick Actions
          </h2>
          <div className="flex flex-col gap-3">
            {quickActions.map((a) => (
              <button
                key={a.to}
                onClick={() => navigate(a.to)}
                className="flex items-center justify-between w-full px-4 py-3 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/5 hover:border-white/15 text-white/80 hover:text-white transition-colors text-sm"
              >
                <span>
                  <span className="mr-2">{a.emoji}</span>
                  {a.label}
                </span>
                <span className="text-white/30">→</span>
              </button>
            ))}
          </div>
        </div>

        {/* Last Session / Welcome */}
        <div className="w-full md:w-72 rounded-2xl border border-white/10 bg-white/[0.03] p-6 flex flex-col justify-between">
          {lastSession ? (
            <>
              <div>
                <h2 className="text-sm font-semibold text-white/50 uppercase tracking-wider mb-4">
                  Last Session
                </h2>
                <p className="text-lg font-medium text-white truncate">
                  {lastSession.projectName}
                </p>
                <p className="text-sm text-white/40 mt-1">
                  {lastSession.beamCount} beam{lastSession.beamCount !== 1 ? "s" : ""} ·{" "}
                  {lastSession.passRate}% pass · {timeAgo(lastSession.timestamp)}
                </p>
              </div>
              <button
                onClick={() => navigate("/editor")}
                className="mt-4 w-full px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition-colors"
              >
                Resume Project →
              </button>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <p className="text-white/70 text-sm font-medium mb-1">Welcome!</p>
              <p className="text-white/30 text-xs leading-relaxed">
                Design RC beams to IS&nbsp;456:2000. Start by designing a single beam or importing
                a CSV batch.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Feature badges */}
      <div className="flex flex-wrap justify-center gap-3 mt-10">
        {badges.map((b) => (
          <span
            key={b}
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/[0.04] border border-white/10 text-xs text-white/50"
          >
            <span className="text-green-400">✓</span> {b}
          </span>
        ))}
      </div>
    </div>
  );
}
