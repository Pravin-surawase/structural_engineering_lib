/**
 * DashboardPage — Batch design analytics after CSV import + design.
 *
 * Layout: BentoGrid with export buttons in the header.
 * Cards: Pass rate · Utilization · Pass/Fail bar · Critical beams · Materials · By story
 */
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  BarChart3, CheckCircle, AlertCircle, ArrowLeft,
  Loader2, AlertTriangle, Download, FileText, Package,
} from "lucide-react";
import { useImportedBeamsStore } from "../../store/importedBeamsStore";
import { useDashboardInsights, useProjectBOQ } from "../../hooks/useInsights";
import { useExportBuildingSummary } from "../../hooks/useExport";
import { BentoGrid, BentoCard, BentoCardHeader } from "../ui/BentoGrid";
import { ProjectBOQPanel } from "../design/ProjectBOQPanel";
import type { DashboardData, StoryStats } from "../../hooks/useInsights";
import { WorkflowBreadcrumb } from "../ui/WorkflowBreadcrumb";
import { calculateSteelWeightKg } from "../../utils/quantities";
import {
  currentBatchResult,
  projectExportReadiness,
} from "../../workspace/resultRecords";
import type { WorkspaceSnapshotV1 } from "../../workspace/types";
import { useWorkspaceStore } from "../../workspace/workspaceStore";

function getEnvelopeMu(beam: ReturnType<typeof useImportedBeamsStore.getState>['beams'][number]): number {
  return Math.max(
    Math.abs(beam.Mu_start ?? 0),
    Math.abs(beam.Mu_mid ?? 0),
    Math.abs(beam.Mu_end ?? 0),
    Math.abs(beam.mu_envelope ?? 0),
  );
}

function getEnvelopeVu(beam: ReturnType<typeof useImportedBeamsStore.getState>['beams'][number]): number {
  return Math.max(
    Math.abs(beam.Vu_start ?? 0),
    Math.abs(beam.Vu_end ?? 0),
    Math.abs(beam.vu_envelope ?? 0),
  );
}

function projectExportRows(
  snapshot: WorkspaceSnapshotV1,
  beams: ReturnType<typeof useImportedBeamsStore.getState>['beams'],
) {
  return snapshot.members.flatMap((member) => {
    const beam = beams.find((candidate) => (candidate.source_id ?? candidate.id) === member.memberId);
    const result = currentBatchResult(snapshot, member.memberId);
    if (!beam || !result) return [];
    return [{
      beam_id: member.sourceId,
      story: beam.story ?? '',
      width: beam.b,
      depth: beam.D,
      span_length: beam.span,
      fck: beam.fck ?? 25,
      fy: beam.fy ?? 500,
      moment: getEnvelopeMu(beam),
      shear: getEnvelopeVu(beam),
      ast_required: result.flexure?.ast_required ?? 0,
      ast_provided: beam.ast_provided ?? 0,
      asc_required: result.flexure?.asc_required ?? 0,
      bar_count: beam.bar_count,
      bar_diameter: beam.bar_diameter,
      stirrup_diameter: beam.stirrup_diameter ?? 8,
      stirrup_spacing: result.shear?.stirrup_spacing,
      utilization: result.utilization_ratio ?? 0,
      is_safe: result.status === 'PASS' && result.is_safe,
      status: result.status,
    }];
  });
}

export function DashboardPage() {
  const navigate = useNavigate();
  const { beams, restoreFromWorkspace } = useImportedBeamsStore();
  const workspaceSnapshot = useWorkspaceStore((state) => state.snapshot);
  const dashboard = useDashboardInsights();
  const boq = useProjectBOQ();

  const { mutate: exportBuilding, isPending: exportPending } = useExportBuildingSummary();
  const exportReadiness = projectExportReadiness(workspaceSnapshot);

  useEffect(() => {
    if (beams.length === 0 && workspaceSnapshot?.members.length) {
      restoreFromWorkspace(workspaceSnapshot);
    }
  }, [beams.length, restoreFromWorkspace, workspaceSnapshot]);

  // Auto-fetch dashboard when beams are available
  useEffect(() => {
    if (beams.length === 0 || !workspaceSnapshot) return;
    const results = workspaceSnapshot.members.map((member) => {
      const beam = beams.find((candidate) => (candidate.source_id ?? candidate.id) === member.memberId);
      const result = currentBatchResult(workspaceSnapshot, member.memberId);
      return {
        beam_id: member.sourceId,
        story: member.story ?? "Unknown",
        is_valid: result?.status === 'PASS' && result.is_safe,
        utilization: result?.utilization_ratio ?? 0,
        ast_provided: beam?.ast_provided ?? 0,
        b_mm: beam?.b ?? 0,
        D_mm: beam?.D ?? 0,
        span_mm: beam?.span ?? 0,
        warnings: member.result?.error ? [member.result.error.message] : [],
      };
    });
    dashboard.mutate({ results });

    // Trigger BOQ calculation
    const boqBeams = beams.map((b) => ({
      beam_id: b.id,
      story: b.story ?? "Unknown",
      b_mm: b.b,
      D_mm: b.D,
      span_mm: b.span,
      fck: b.fck ?? 25,
      steel_weight_kg: calculateSteelWeightKg(b.ast_provided ?? 0, b.span),
    }));
    const first = beams[0];
    const dataset = first?.dataset_id && first.dataset_version && first.dataset_sha256
      ? {
          dataset_id: first.dataset_id,
          dataset_version: first.dataset_version,
          dataset_sha256: first.dataset_sha256,
        }
      : undefined;
    boq.mutate({ beams: boqBeams, dataset });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [beams, workspaceSnapshot]);

  const heldBeamCount = exportReadiness.heldMemberIds.length;
  const exportsHeld = !exportReadiness.eligible;

  const handleProjectExport = (format: 'html' | 'pdf' | 'csv') => {
    const snapshot = useWorkspaceStore.getState().snapshot;
    if (!snapshot || !projectExportReadiness(snapshot).eligible) return;
    exportBuilding({
      project_name: snapshot.projectName,
      beams: projectExportRows(snapshot, useImportedBeamsStore.getState().beams),
      format,
    });
  };

  if (beams.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-screen pt-14 gap-4">
        <BarChart3 className="w-12 h-12 text-white/10" />
        <p className="text-zinc-500 text-sm">No beams imported. Import CSV first.</p>
        <button
          onClick={() => navigate("/import")}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm rounded-lg transition-colors"
        >
          Go to Import
        </button>
      </div>
    );
  }

  return (
    <div className="h-screen pt-14 overflow-y-auto bg-zinc-950">
      {/* Workflow Breadcrumb */}
      <WorkflowBreadcrumb />

      <div className="max-w-6xl mx-auto px-6 py-6 space-y-6">

        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <button onClick={() => navigate(-1)} className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
              <ArrowLeft className="w-4 h-4 text-white/60" />
            </button>
            <div>
              <h1 className="text-lg font-bold text-white">Design Dashboard</h1>
              <p className="text-xs text-zinc-400">{beams.length} beams · IS 456:2000</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <ExportBtn
              label="Project HTML" icon={<FileText className="w-3.5 h-3.5" />}
              loading={exportPending}
              disabled={exportsHeld}
              onClick={() => handleProjectExport('html')}
            />
            <ExportBtn
              label="Project CSV" icon={<Download className="w-3.5 h-3.5" />}
              loading={exportPending}
              disabled={exportsHeld}
              onClick={() => handleProjectExport('csv')}
            />
            {exportsHeld ? (
              <span className="text-[10px] text-amber-400" role="status">
                Exports held: {heldBeamCount} stale, FAIL, HOLD, or not evaluated
              </span>
            ) : null}
          </div>
        </div>

        {dashboard.isPending ? (
          <div className="flex items-center justify-center py-20 gap-3">
            <Loader2 className="w-6 h-6 text-blue-400 animate-spin" />
            <span className="text-zinc-400">Generating dashboard…</span>
          </div>
        ) : dashboard.error ? (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <span className="text-sm text-red-400">Dashboard unavailable — API may be offline</span>
          </div>
        ) : dashboard.data ? (
          <DashboardContent data={dashboard.data} />
        ) : null}

        {/* Project BOQ Panel */}
        <BentoGrid className="auto-rows-auto">
          <BentoCard colSpan={12} variant="default">
            <BentoCardHeader
              title="Project BOQ"
              icon={<Package className="w-4 h-4" />}
              badge={boq.data ? `${boq.data.total_beams} beams` : undefined}
            />
            <ProjectBOQPanel
              data={boq.data ?? null}
              isLoading={boq.isPending}
              error={boq.error?.message ?? null}
            />
          </BentoCard>
        </BentoGrid>
      </div>
    </div>
  );
}

function DashboardContent({ data }: { data: DashboardData }) {
  const passColor = data.pass_rate >= 90 ? "text-emerald-400" : data.pass_rate >= 70 ? "text-amber-400" : "text-rose-400";
  const utilColor = data.avg_utilization <= 0.85 ? "text-emerald-400" : "text-amber-400";

  return (
    <BentoGrid className="auto-rows-auto">

      {/* Pass Rate */}
      <BentoCard colSpan={3} variant="default">
        <BentoCardHeader
          title="Pass Rate"
          icon={<CheckCircle className="w-4 h-4" />}
          badge={data.pass_rate >= 90 ? "Good" : data.pass_rate >= 70 ? "Review" : "Critical"}
        />
        <p className={`text-4xl font-bold tabular-nums mt-1 ${passColor}`}>
          {data.pass_rate.toFixed(0)}%
        </p>
        <p className="text-xs text-zinc-400 mt-1">
          {data.passed} passed &middot; {data.failed} failed &middot; {data.total_beams} total
        </p>
      </BentoCard>

      {/* Avg Utilization */}
      <BentoCard colSpan={3} variant="default">
        <BentoCardHeader title="Avg Utilization" icon={<BarChart3 className="w-4 h-4" />} />
        <p className={`text-4xl font-bold tabular-nums mt-1 ${utilColor}`}>
          {(data.avg_utilization * 100).toFixed(3)}%
        </p>
        <div className="mt-2 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${utilColor.replace("text-", "bg-")}`}
            style={{ width: `${Math.min(data.avg_utilization * 100, 100)}%` }}
          />
        </div>
        <p className="text-[10px] text-zinc-500 mt-1 font-mono">
          avg ratio {data.avg_utilization.toFixed(6)} · max {(data.max_utilization * 100).toFixed(3)}% ({data.max_utilization.toFixed(6)})
        </p>
      </BentoCard>

      {/* Pass / Fail visual bar */}
      <BentoCard colSpan={6} variant="glass">
        <BentoCardHeader title="Pass / Fail" />
        <div className="flex h-6 rounded-xl overflow-hidden bg-white/5 mt-2">
          {data.passed > 0 && (
            <div
              className="bg-emerald-500/60 flex items-center justify-center text-[10px] text-emerald-300 font-medium transition-all"
              style={{ width: `${data.pass_rate}%` }}
            >
              {data.pass_rate >= 20 && `${data.passed}`}
            </div>
          )}
          {data.failed > 0 && (
            <div
              className="bg-rose-500/60 flex items-center justify-center text-[10px] text-rose-300 font-medium transition-all"
              style={{ width: `${(data.failed / data.total_beams) * 100}%` }}
            >
              {(data.failed / data.total_beams) >= 0.15 && `${data.failed}`}
            </div>
          )}
        </div>
        <div className="flex justify-between mt-2 text-[10px] text-zinc-400">
          <span className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-emerald-500/60" />{data.passed} passed
          </span>
          <span className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-rose-500/60" />{data.failed} failed
          </span>
        </div>
        {data.warnings_count > 0 && (
          <p className="text-[10px] text-amber-400/60 mt-2">
            {data.warnings_count} warnings across all beams
          </p>
        )}
      </BentoCard>

      {/* Critical Beams */}
      {data.critical_beams.length > 0 && (
        <BentoCard colSpan={8} variant="elevated" glow>
          <BentoCardHeader
            title="Critical Beams"
            icon={<AlertTriangle className="w-4 h-4 text-rose-400" />}
            badge={`${data.critical_beams.length}`}
          />
          <div className="flex flex-wrap gap-1.5 mt-1">
            {data.critical_beams.map((id) => (
              <span
                key={id}
                className="px-2 py-0.5 text-[10px] text-rose-400/80 bg-rose-500/10 rounded-md border border-rose-500/20"
              >
                {id}
              </span>
            ))}
          </div>
        </BentoCard>
      )}

      {/* Steel + Concrete totals */}
      <BentoCard colSpan={data.critical_beams.length > 0 ? 4 : 6} variant="default">
        <BentoCardHeader title="Materials" icon={<BarChart3 className="w-4 h-4" />} />
        <div className="grid grid-cols-2 gap-3 mt-1">
          <div>
            <p className="text-[9px] text-zinc-500 uppercase tracking-wider">Steel</p>
            <p className="text-xl font-bold text-blue-400 tabular-nums">
              {data.total_steel_kg.toLocaleString("en-IN", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}
              <span className="text-xs text-zinc-500 ml-1">kg</span>
            </p>
          </div>
          <div>
            <p className="text-[9px] text-zinc-500 uppercase tracking-wider">Concrete</p>
            <p className="text-xl font-bold text-blue-400 tabular-nums">
              {data.total_concrete_m3.toFixed(1)}
              <span className="text-xs text-zinc-500 ml-1">m³</span>
            </p>
          </div>
        </div>
      </BentoCard>

      {/* By Story */}
      {Object.keys(data.by_story).length > 0 && (
        <BentoCard colSpan={12} variant="default">
          <BentoCardHeader title="By Story" />
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
            {Object.entries(data.by_story).map(([story, stats]: [string, StoryStats]) => {
              const pct = (stats.passed / stats.total) * 100;
              const storyColor = pct >= 90 ? "bg-emerald-500/50" : pct >= 70 ? "bg-amber-500/50" : "bg-rose-500/50";
              return (
                <div key={story} className="flex items-center gap-2.5 p-2 rounded-lg bg-white/[0.02]">
                  <span className="text-xs text-white/60 w-16 truncate font-medium">{story}</span>
                  <div className="flex-1 h-2 rounded-full overflow-hidden bg-white/5">
                    <div className={storyColor} style={{ width: `${pct}%`, height: "100%" }} />
                  </div>
                  <span className="text-[10px] text-white/35 tabular-nums w-10 text-right shrink-0">
                    {stats.passed}/{stats.total}
                  </span>
                </div>
              );
            })}
          </div>
        </BentoCard>
      )}

    </BentoGrid>
  );
}

function ExportBtn({
  label, icon, loading, disabled = false, onClick,
}: {
  label: string;
  icon: React.ReactNode;
  loading: boolean;
  disabled?: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      disabled={loading || disabled}
      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg
        bg-white/5 border border-white/8 text-xs text-white/60
        hover:bg-white/10 hover:text-white/90 hover:border-white/15
        transition-all disabled:opacity-40 disabled:cursor-not-allowed"
    >
      {loading
        ? <div className="w-3.5 h-3.5 rounded-full border border-white/30 border-t-white/70 animate-spin" />
        : icon
      }
      {label}
    </button>
  );
}
