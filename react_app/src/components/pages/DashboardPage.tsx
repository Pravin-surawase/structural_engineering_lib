/**
 * DashboardPage — Batch design analytics after CSV import + design.
 *
 * Shows pass/fail overview, utilization distribution, per-story breakdown,
 * critical beams, and material quantities. Powered by useDashboardInsights hook.
 */
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { BarChart3, CheckCircle, AlertCircle, ArrowLeft, Loader2, AlertTriangle } from "lucide-react";
import { useImportedBeamsStore } from "../../store/importedBeamsStore";
import { useDashboardInsights } from "../../hooks/useInsights";
import type { DashboardData, StoryStats } from "../../hooks/useInsights";

export function DashboardPage() {
  const navigate = useNavigate();
  const { beams } = useImportedBeamsStore();
  const dashboard = useDashboardInsights();

  // Auto-fetch dashboard when beams are available
  useEffect(() => {
    if (beams.length === 0) return;
    const results = beams.map((b) => ({
      beam_id: b.id,
      story: b.story ?? "Unknown",
      is_valid: true,
      utilization: 0,
      ast_provided: 0,
      b_mm: b.b,
      D_mm: b.D,
      span_mm: b.span,
      warnings: [],
    }));
    dashboard.mutate({ results });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [beams]);

  if (beams.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-screen pt-14 gap-4">
        <BarChart3 className="w-12 h-12 text-white/10" />
        <p className="text-white/30 text-sm">No beams imported. Import CSV first.</p>
        <button
          onClick={() => navigate("/import")}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm rounded-lg"
        >
          Go to Import
        </button>
      </div>
    );
  }

  return (
    <div className="h-screen pt-14 overflow-y-auto bg-zinc-950">
      <div className="max-w-5xl mx-auto px-6 py-6 space-y-6">
        {/* Header */}
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="p-2 rounded-lg bg-white/5 hover:bg-white/10">
            <ArrowLeft className="w-4 h-4 text-white/60" />
          </button>
          <div>
            <h1 className="text-lg font-bold text-white">Design Dashboard</h1>
            <p className="text-xs text-white/40">{beams.length} beams imported</p>
          </div>
        </div>

        {dashboard.isPending ? (
          <div className="flex items-center justify-center py-20 gap-3">
            <Loader2 className="w-6 h-6 text-blue-400 animate-spin" />
            <span className="text-white/40">Generating dashboard...</span>
          </div>
        ) : dashboard.error ? (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <span className="text-sm text-red-400">Dashboard unavailable — API may be offline</span>
          </div>
        ) : dashboard.data ? (
          <DashboardContent data={dashboard.data} />
        ) : null}
      </div>
    </div>
  );
}

function DashboardContent({ data }: { data: DashboardData }) {
  return (
    <div className="space-y-5">
      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-3">
        <SummaryCard label="Pass Rate" value={`${data.pass_rate.toFixed(0)}%`} sub={`${data.passed}/${data.total_beams}`} color={data.pass_rate >= 90 ? "green" : data.pass_rate >= 70 ? "yellow" : "red"} />
        <SummaryCard label="Avg Utilization" value={`${(data.avg_utilization * 100).toFixed(0)}%`} sub={`max ${(data.max_utilization * 100).toFixed(0)}%`} color={data.avg_utilization <= 0.85 ? "green" : "yellow"} />
        <SummaryCard label="Steel" value={`${data.total_steel_kg.toFixed(0)} kg`} sub="total reinforcement" color="blue" />
        <SummaryCard label="Concrete" value={`${data.total_concrete_m3.toFixed(1)} m³`} sub="total volume" color="blue" />
      </div>

      {/* Pass / Fail bar */}
      <div className="p-4 rounded-xl bg-white/[0.03] border border-white/8">
        <h3 className="text-xs font-semibold text-white/60 uppercase tracking-wider mb-3">Pass / Fail</h3>
        <div className="flex h-4 rounded-full overflow-hidden bg-white/5">
          {data.passed > 0 && (
            <div className="bg-green-500/60 transition-all" style={{ width: `${data.pass_rate}%` }} />
          )}
          {data.failed > 0 && (
            <div className="bg-red-500/60 transition-all" style={{ width: `${((data.failed / data.total_beams) * 100)}%` }} />
          )}
        </div>
        <div className="flex justify-between mt-2 text-[10px] text-white/40">
          <span className="flex items-center gap-1"><CheckCircle className="w-3 h-3 text-green-400" />{data.passed} passed</span>
          <span className="flex items-center gap-1"><AlertCircle className="w-3 h-3 text-red-400" />{data.failed} failed</span>
        </div>
      </div>

      {/* By Story */}
      {Object.keys(data.by_story).length > 0 && (
        <div className="p-4 rounded-xl bg-white/[0.03] border border-white/8">
          <h3 className="text-xs font-semibold text-white/60 uppercase tracking-wider mb-3">By Story</h3>
          <div className="space-y-2">
            {Object.entries(data.by_story).map(([story, stats]: [string, StoryStats]) => (
              <div key={story} className="flex items-center gap-3">
                <span className="text-xs text-white/60 w-20 truncate">{story}</span>
                <div className="flex-1 flex h-2.5 rounded-full overflow-hidden bg-white/5">
                  <div className="bg-green-500/50" style={{ width: `${(stats.passed / stats.total) * 100}%` }} />
                  <div className="bg-red-500/50" style={{ width: `${(stats.failed / stats.total) * 100}%` }} />
                </div>
                <span className="text-[10px] text-white/40 w-14 text-right">{stats.passed}/{stats.total}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Critical Beams */}
      {data.critical_beams.length > 0 && (
        <div className="p-4 rounded-xl bg-red-500/5 border border-red-500/20">
          <h3 className="text-xs font-semibold text-red-400/80 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5" />
            Critical Beams ({data.critical_beams.length})
          </h3>
          <div className="flex flex-wrap gap-1.5">
            {data.critical_beams.map((id) => (
              <span key={id} className="px-2 py-1 text-[10px] text-red-400/80 bg-red-500/10 rounded-md border border-red-500/20">
                {id}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Warnings */}
      {data.warnings_count > 0 && (
        <div className="p-3 rounded-lg bg-yellow-500/5 border border-yellow-500/20">
          <span className="text-xs text-yellow-400/80">{data.warnings_count} total warnings across all beams</span>
        </div>
      )}
    </div>
  );
}

function SummaryCard({ label, value, sub, color }: { label: string; value: string; sub: string; color: "green" | "yellow" | "red" | "blue" }) {
  const border = {
    green: "border-green-500/20",
    yellow: "border-yellow-500/20",
    red: "border-red-500/20",
    blue: "border-blue-500/20",
  }[color];
  const text = {
    green: "text-green-400",
    yellow: "text-yellow-400",
    red: "text-red-400",
    blue: "text-blue-400",
  }[color];
  return (
    <div className={`p-4 rounded-xl bg-white/[0.03] border ${border}`}>
      <p className="text-[10px] font-semibold text-white/50 uppercase tracking-wider mb-1">{label}</p>
      <p className={`text-xl font-bold ${text}`}>{value}</p>
      <p className="text-[10px] text-white/30 mt-0.5">{sub}</p>
    </div>
  );
}
