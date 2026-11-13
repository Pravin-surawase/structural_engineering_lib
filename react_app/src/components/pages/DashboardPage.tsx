/**
 * DashboardPage — Batch design analytics after CSV import + design.
 *
 * Layout: BentoGrid with export buttons in the header.
 * Cards: Pass rate · Utilization · Pass/Fail bar · Critical beams · Materials · By story
 */
import { useEffect, useMemo } from "react";
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
import type { BeamResult, DashboardData, StoryStats } from "../../hooks/useInsights";
import { WorkflowBreadcrumb } from "../ui/WorkflowBreadcrumb";
import {
  checkedProjectMembers,
  currentBatchResult,
  currentWorkbenchLayout,
  projectExportReadiness,
} from "../../workspace/resultRecords";
import type { WorkspaceSnapshotV1 } from "../../workspace/types";
import type { BeamCSVRow } from "../../types/csv";
import { useWorkspaceStore } from "../../workspace/workspaceStore";
import { projectStagePath } from "../../app/navigation";
import { batchGoverningUtilization } from "../../api/client";
import { formatPercent, formatRatio } from "../../utils/trustPresentation";

function dashboardInputs(snapshot: WorkspaceSnapshotV1, beams: BeamCSVRow[]) {
  const byMemberId = new Map(beams.map((beam) => [beam.source_id ?? beam.id, beam]));
  const results: BeamResult[] = snapshot.members.map((member) => {
    const beam = byMemberId.get(member.memberId);
    const result = currentBatchResult(snapshot, member.memberId);
    const layout = currentWorkbenchLayout(snapshot, member.memberId);
    const mid = layout?.zones.find((zone) => zone.zone === 'mid');
    const strengthStatus = result?.status === 'FAIL' ? 'FAIL'
      : result?.status === 'PASS' && result.is_safe ? 'PASS' : 'HOLD';
    const warnings = result?.workbench?.status === 'HOLD'
      ? [result.workbench.reason]
      : member.result?.error ? [member.result.error.message] : [];
    return {
      beam_id: member.memberId,
      story: member.story ?? "Unknown",
      is_valid: strengthStatus === 'PASS' && Boolean(layout),
      strength_status: strengthStatus,
      layout_status: layout ? 'PASS' : 'HOLD',
      utilization: layout?.utilization ?? (result ? batchGoverningUtilization(result) : null),
      ast_provided: mid?.tension.area_mm2 ?? 0,
      checked_steel_weight_kg: layout?.schedule_steel_weight_kg,
      b_mm: beam?.b ?? 0,
      D_mm: beam?.D ?? 0,
      span_mm: beam?.span ?? 0,
      warnings,
    };
  });
  const boqBeams = results.flatMap((result) => {
    const beam = byMemberId.get(result.beam_id);
    if (!beam || result.checked_steel_weight_kg === undefined) return [];
    return [{
      beam_id: result.beam_id,
      story: result.story,
      b_mm: result.b_mm,
      D_mm: result.D_mm,
      span_mm: result.span_mm,
      fck: beam.fck ?? 25,
      steel_weight_kg: result.checked_steel_weight_kg,
    }];
  });
  const first = beams[0];
  const dataset = first?.dataset_id && first.dataset_version && first.dataset_sha256
    ? { dataset_id: first.dataset_id, dataset_version: first.dataset_version, dataset_sha256: first.dataset_sha256 }
    : undefined;
  return {
    dashboard: { results },
    boq: boqBeams.length === results.length && results.length > 0
      ? { beams: boqBeams, dataset, project_name: snapshot.projectName }
      : null,
    scheduleCount: boqBeams.length,
  };
}

export function DashboardPage() {
  const navigate = useNavigate();
  const workspaceProjectId = useWorkspaceStore((state) => state.snapshot?.projectId);
  const importPath = workspaceProjectId
    ? projectStagePath(workspaceProjectId, "import")
    : "/workbench/projects/new";
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

  const inputs = useMemo(
    () => beams.length && workspaceSnapshot ? dashboardInputs(workspaceSnapshot, beams) : null,
    [beams, workspaceSnapshot],
  );
  const { mutate: refreshDashboard } = dashboard;
  const { mutate: refreshBOQ } = boq;
  useEffect(() => {
    if (!inputs?.dashboard.results.length) return;
    refreshDashboard(inputs.dashboard);
    if (inputs.boq) refreshBOQ(inputs.boq);
  }, [inputs, refreshDashboard, refreshBOQ]);
  const currentDashboard = dashboard.variables === inputs?.dashboard ? dashboard : null;
  const currentBOQ = inputs?.boq && boq.variables === inputs.boq ? boq : null;

  const heldBeamCount = exportReadiness.heldMemberIds.length;
  const exportsHeld = !exportReadiness.eligible;

  const handleProjectExport = (format: 'html' | 'pdf' | 'csv') => {
    const snapshot = useWorkspaceStore.getState().snapshot;
    const checkedBeams = snapshot && checkedProjectMembers(snapshot);
    if (!snapshot || !checkedBeams) return;
    exportBuilding({ project_name: snapshot.projectName, checked_beams: checkedBeams, format });
  };

  if (beams.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-screen pt-14 gap-4">
        <BarChart3 className="w-12 h-12 text-white/10" />
        <p className="text-zinc-500 text-sm">No beams imported. Import CSV first.</p>
        <button
          onClick={() => navigate(importPath)}
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

        {(!currentDashboard || currentDashboard.isPending) ? (
          <div className="flex items-center justify-center py-20 gap-3">
            <Loader2 className="w-6 h-6 text-blue-400 animate-spin" />
            <span className="text-zinc-400">Generating dashboard…</span>
          </div>
        ) : currentDashboard.error ? (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <span className="text-sm text-red-400">Dashboard unavailable — API may be offline</span>
          </div>
        ) : currentDashboard.data ? (
          <DashboardContent data={currentDashboard.data} scheduleCount={inputs?.scheduleCount ?? 0} />
        ) : null}

        {/* Project BOQ Panel */}
        <BentoGrid className="auto-rows-auto">
          <BentoCard colSpan={12} variant="default">
            <BentoCardHeader
              title="Project BOQ"
              icon={<Package className="w-4 h-4" />}
              badge={currentBOQ?.data ? `${currentBOQ.data.total_beams} beams` : undefined}
            />
            {inputs?.boq ? (
              <ProjectBOQPanel
                data={currentBOQ?.data ?? null}
                isLoading={!currentBOQ || currentBOQ.isPending}
                error={currentBOQ?.error?.message ?? null}
              />
            ) : (
              <p className="text-xs text-amber-400" role="status">
                BOQ held until all beams have a current checked schedule weight.
              </p>
            )}
          </BentoCard>
        </BentoGrid>
      </div>
    </div>
  );
}

function DashboardContent({ data, scheduleCount }: { data: DashboardData; scheduleCount: number }) {
  const passColor = data.pass_rate >= 90 ? "text-emerald-400" : data.pass_rate >= 70 ? "text-amber-400" : "text-rose-400";
  const utilColor = data.avg_utilization !== null && data.avg_utilization <= 0.85 ? "text-emerald-400" : "text-amber-400";

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
          {data.passed} passed &middot; {data.failed} failed &middot; {data.held} held
        </p>
        <p className="text-xs text-zinc-400 mt-1">
          Strength checks: {data.strength_passed} passed &middot; {data.strength_failed} failed
        </p>
      </BentoCard>

      {/* Avg Utilization */}
      <BentoCard colSpan={3} variant="default">
        <BentoCardHeader title="Avg Utilization" icon={<BarChart3 className="w-4 h-4" />} />
        <p className={`text-4xl font-bold tabular-nums mt-1 ${utilColor}`}>
          {formatPercent(data.avg_utilization)}
        </p>
        <div className="mt-2 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full ${utilColor.replace("text-", "bg-")}`}
            style={{ width: `${Math.min((data.avg_utilization ?? 0) * 100, 100)}%` }}
          />
        </div>
        <p className="text-[10px] text-zinc-500 mt-1 font-mono">
          avg ratio {formatRatio(data.avg_utilization)} · max {formatPercent(data.max_utilization)} ({formatRatio(data.max_utilization)})
        </p>
      </BentoCard>

      {/* Pass / Fail visual bar */}
      <BentoCard colSpan={6} variant="glass">
        <BentoCardHeader title="Member status" />
        <div className="flex h-6 rounded-xl overflow-hidden bg-white/5 mt-2">
          {data.passed > 0 && (
            <div
              className="bg-emerald-500/60 flex items-center justify-center text-[10px] text-emerald-300 font-medium transition-all"
              style={{ width: `${data.pass_rate}%` }}
            >
              {data.pass_rate >= 20 && `${data.passed}`}
            </div>
          )}
          {data.held > 0 && (
            <div className="bg-amber-500/60" style={{ width: `${(data.held / data.total_beams) * 100}%` }} />
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
          <span className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-amber-500/60" />{data.held} held
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
            <p className="text-[9px] text-zinc-500 uppercase tracking-wider">Checked schedule steel</p>
            <p className="text-xl font-bold text-blue-400 tabular-nums">
              {scheduleCount
                ? `${data.total_steel_kg.toLocaleString("en-IN", { minimumFractionDigits: 1, maximumFractionDigits: 1 })} kg`
                : '—'}
            </p>
            <p className="text-[10px] text-zinc-400">{scheduleCount} of {data.total_beams} beams</p>
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
