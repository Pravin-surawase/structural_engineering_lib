/**
 * DashboardPage — Batch design analytics after CSV import + design.
 *
 * Current member results, export readiness, and project quantities.
 */
import { useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  BarChart3, AlertCircle, ArrowLeft, Loader2, Download, FileText,
} from "lucide-react";
import { useImportedBeamsStore } from "../../store/importedBeamsStore";
import { useDashboardInsights, useProjectBOQ } from "../../hooks/useInsights";
import { useExportBuildingSummary } from "../../hooks/useExport";
import { WorkbenchPanel } from "../workbench/WorkbenchPanel";
import { ProjectBOQPanel } from "../design/ProjectBOQPanel";
import type { BeamResult, DashboardData } from "../../hooks/useInsights";
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
      <div className="flex h-full flex-col items-center justify-center gap-4 bg-paper px-6 pt-14 text-center">
        <div className="rounded-2xl border border-ink/10 bg-white p-5 shadow-sm">
          <BarChart3 className="mx-auto h-10 w-10 text-cobalt" />
        </div>
        <div>
          <h1 className="text-xl font-semibold text-ink">Start with project data</h1>
          <p className="mt-1 text-sm text-ink/65">No beams imported. Import CSV first.</p>
        </div>
        <button
          onClick={() => navigate(importPath)}
          className="rounded-xl bg-cobalt px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-cobalt-hover"
        >
          Go to Import
        </button>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto bg-paper pt-14 text-ink [--focus-color:var(--color-cobalt)]">
      {/* Workflow Breadcrumb */}
      <WorkflowBreadcrumb />

      <div className="mx-auto max-w-6xl space-y-6 px-4 py-6 sm:px-6">

        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <button onClick={() => navigate(-1)} aria-label="Back" className="rounded-lg border border-ink/10 bg-white p-2 text-ink/65 shadow-sm transition-colors hover:text-ink">
              <ArrowLeft className="h-4 w-4" />
            </button>
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-ink">Project results</h1>
              <p className="mt-1 text-xs text-ink/75">{beams.length} {beams.length === 1 ? 'beam' : 'beams'} · IS 456:2000</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 rounded-xl border border-ink/10 bg-white/75 p-2 shadow-sm">
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
              <span className="px-1 text-[10px] font-medium text-amber-800" role="status">
                Exports held: {heldBeamCount} stale, FAIL, HOLD, or not evaluated
              </span>
            ) : null}
          </div>
        </div>

        {(!currentDashboard || currentDashboard.isPending) ? (
          <div className="flex items-center justify-center gap-3 rounded-2xl border border-ink/10 bg-white py-20 shadow-sm">
            <Loader2 className="h-6 w-6 animate-spin text-cobalt" />
            <span className="text-ink/65">Generating dashboard…</span>
          </div>
        ) : currentDashboard.error ? (
          <div className="flex items-center gap-3 rounded-2xl border border-rose-300 bg-rose-50 p-4">
            <AlertCircle className="h-5 w-5 text-rose-700" />
            <span className="text-sm text-rose-800">Dashboard unavailable — API may be offline</span>
          </div>
        ) : currentDashboard.data ? (
          <DashboardContent data={currentDashboard.data} scheduleCount={inputs?.scheduleCount ?? 0} />
        ) : null}

        <WorkbenchPanel
          title="Project BOQ"
          description={currentBOQ?.data ? `${currentBOQ.data.total_beams} beams` : undefined}
          className="text-zinc-100 [--focus-color:#6e9cfa]"
        >
          {inputs?.boq ? (
            <ProjectBOQPanel
              data={currentBOQ?.data ?? null}
              isLoading={!currentBOQ || currentBOQ.isPending}
              error={currentBOQ?.error?.message ?? null}
            />
          ) : (
            <p className="text-sm text-amber-200" role="status">
              BOQ held until all beams have a current checked schedule weight.
            </p>
          )}
        </WorkbenchPanel>
      </div>
    </div>
  );
}

function DashboardContent({ data, scheduleCount }: { data: DashboardData; scheduleCount: number }) {
  return (
    <div className="space-y-5 text-zinc-100 [--focus-color:#6e9cfa]">
      <div className="grid gap-4 md:grid-cols-3">
        <WorkbenchPanel title="Checked pass rate">
          <p className="font-mono text-3xl font-semibold text-white">{data.pass_rate.toFixed(0)}%</p>
          <p className="mt-2 text-sm text-zinc-300">
            Strength checks: {data.strength_passed} passed · {data.strength_failed} failed
          </p>
        </WorkbenchPanel>

        <WorkbenchPanel title="Average utilization">
          <p className="font-mono text-3xl font-semibold text-white">{formatPercent(data.avg_utilization)}</p>
          <p className="mt-2 text-sm text-zinc-300">
            Average ratio {formatRatio(data.avg_utilization)} · Maximum {formatPercent(data.max_utilization)} ({formatRatio(data.max_utilization)})
          </p>
        </WorkbenchPanel>

        <WorkbenchPanel title="Member status">
          <dl className="grid grid-cols-3 gap-2 text-sm">
            <div><dt className="text-zinc-300">Passed</dt><dd className="font-mono text-xl text-emerald-200">{data.passed}</dd></div>
            <div><dt className="text-zinc-300">Failed</dt><dd className="font-mono text-xl text-rose-200">{data.failed}</dd></div>
            <div><dt className="text-zinc-300">Held</dt><dd className="font-mono text-xl text-amber-200">{data.held}</dd></div>
          </dl>
          {data.total_beams > 0 ? (
            <div className="mt-3 flex h-1.5 overflow-hidden rounded-full bg-zinc-800" aria-hidden="true">
              <span className="bg-emerald-400" style={{ width: `${data.passed / data.total_beams * 100}%` }} />
              <span className="bg-rose-400" style={{ width: `${data.failed / data.total_beams * 100}%` }} />
              <span className="bg-amber-400" style={{ width: `${data.held / data.total_beams * 100}%` }} />
            </div>
          ) : null}
          {data.warnings_count > 0 ? (
            <p className="mt-2 text-sm text-amber-200">{data.warnings_count} {data.warnings_count === 1 ? 'warning' : 'warnings'}</p>
          ) : null}
        </WorkbenchPanel>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {data.critical_beams.length > 0 ? (
          <WorkbenchPanel title="Critical beams">
            <ul className="flex flex-wrap gap-2">
              {data.critical_beams.map((id) => (
                <li key={id} className="max-w-full break-all rounded-sm border border-rose-400/30 px-2 py-1 text-xs text-rose-200">{id}</li>
              ))}
            </ul>
          </WorkbenchPanel>
        ) : null}

        <WorkbenchPanel title="Materials">
          <dl className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <dt className="text-zinc-300">Checked schedule steel</dt>
              <dd className="font-mono text-lg text-white">
                {scheduleCount
                  ? `${data.total_steel_kg.toLocaleString("en-IN", { minimumFractionDigits: 1, maximumFractionDigits: 1 })} kg`
                  : '—'}
              </dd>
              <dd className="text-xs text-zinc-400">{scheduleCount} of {data.total_beams} beams</dd>
            </div>
            <div>
              <dt className="text-zinc-300">Concrete</dt>
              <dd className="font-mono text-lg text-white">{data.total_concrete_m3.toFixed(1)} m³</dd>
            </div>
          </dl>
        </WorkbenchPanel>
      </div>

      {Object.keys(data.by_story).length > 0 ? (
        <WorkbenchPanel title="Pass counts by story">
          <dl className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {Object.entries(data.by_story).map(([story, stats]) => (
              <div key={story} className="flex min-w-0 justify-between gap-3 rounded-sm border border-zinc-700 p-2 text-sm">
                <dt className="min-w-0 break-words text-zinc-200">{story}</dt>
                <dd className="shrink-0 font-mono text-zinc-300">{stats.passed}/{stats.total}</dd>
              </div>
            ))}
          </dl>
        </WorkbenchPanel>
      ) : null}
    </div>
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
      className="flex items-center gap-1.5 rounded-lg border border-ink/15 bg-paper px-3 py-1.5 text-xs font-semibold text-ink/70
        transition-colors hover:border-cobalt/30 hover:bg-cobalt/5 hover:text-cobalt
        disabled:cursor-not-allowed disabled:opacity-40"
    >
      {loading
        ? <div className="h-3.5 w-3.5 animate-spin rounded-full border border-ink/30 border-t-ink/70" />
        : icon
      }
      {label}
    </button>
  );
}
