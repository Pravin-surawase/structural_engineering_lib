import { ArrowRight, Boxes, Calculator, ShieldCheck, Workflow } from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { projectStagePath } from '../../app/navigation';
import { WorkbenchHeader } from '../workbench/WorkbenchHeader';
import { WorkbenchPanel } from '../workbench/WorkbenchPanel';
import { WorkbenchShell } from '../workbench/WorkbenchShell';
import { useWorkspaceStore } from '../../workspace/workspaceStore';
import { WORKFLOW_RUNNER_ENABLED } from '../../features/automation/config';

export interface WorkbenchHomePageProps {
  initialView?: 'workbench' | 'projects';
}

export function WorkbenchHomePage({
  initialView = 'workbench',
}: WorkbenchHomePageProps) {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const workspace = useWorkspaceStore((state) => state.snapshot);
  const loadState = useWorkspaceStore((state) => state.loadState);
  const loadError = useWorkspaceStore((state) => state.loadError);
  const title = initialView === 'projects' ? 'Projects' : 'Structural workbench';

  return (
    <WorkbenchShell
      className="pt-14"
      header={(
        <WorkbenchHeader
          title={title}
          projectName="IS 456 reinforced-concrete design"
          primaryAction={(
            <button
              type="button"
              onClick={() => navigate('/workbench/projects/new')}
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-500"
            >
              New project
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </button>
          )}
        />
      )}
    >
      <div className="mx-auto grid max-w-5xl gap-4 p-4 pb-24 sm:p-6 md:grid-cols-2 md:pb-8">
        {searchParams.get('recovery') === 'project-required' ? (
          <div className="rounded-xl border border-amber-400/30 bg-amber-400/10 p-4 text-sm text-amber-100 md:col-span-2" role="alert">
            Open an existing project or import a new one before using that project stage.
          </div>
        ) : null}
        {workspace ? (
          <WorkbenchPanel
            title="Continue project"
            description={`${workspace.projectName} · ${workspace.members.length} members · ${workspace.selectedStage}`}
            className="md:col-span-2"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="text-sm text-zinc-400">
                Revision {workspace.projectRevision} · {workspace.saveState === 'clean' ? 'saved locally' : workspace.saveState}
              </p>
              <button
                type="button"
                onClick={() => navigate(projectStagePath(workspace.projectId, workspace.selectedStage))}
                className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500"
              >
                Resume project
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
          </WorkbenchPanel>
        ) : loadState === 'loading' ? (
          <div className="rounded-xl border border-white/10 bg-zinc-900/60 p-4 text-sm text-zinc-400 md:col-span-2" role="status">
            Restoring the last local project…
          </div>
        ) : loadState === 'error' && loadError ? (
          <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-200 md:col-span-2" role="alert">
            Saved project needs recovery: {loadError}
          </div>
        ) : null}

        <WorkbenchPanel
          title="Isolated footing"
          description="Centred square or rectangular footing with maintained server evidence."
        >
          <div className="flex items-start gap-3">
            <span className="rounded-xl bg-amber-500/10 p-2.5 text-amber-300">
              <Calculator className="h-5 w-5" aria-hidden="true" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="text-sm leading-6 text-zinc-400">
                Keep service and factored loads, soil approval, structural checks,
                reinforcement detailing and review status visibly separate.
              </p>
              <button
                type="button"
                onClick={() => navigate('/workbench/footing/isolated/concentric')}
                className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-amber-300 hover:text-amber-200"
              >
                Open isolated footing
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
          </div>
        </WorkbenchPanel>

        <WorkbenchPanel
          title="Quick beam"
          description="One focused calculation without creating a project."
        >
          <div className="flex items-start gap-3">
            <span className="rounded-xl bg-blue-500/10 p-2.5 text-blue-300">
              <Calculator className="h-5 w-5" aria-hidden="true" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="text-sm leading-6 text-zinc-400">
                Enter beam inputs, inspect checks and 3D detail, then export only
                when the result is current and supported.
              </p>
              <button
                type="button"
                onClick={() => navigate('/workbench/quick')}
                className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-blue-300 hover:text-blue-200"
              >
                Open quick beam
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
          </div>
        </WorkbenchPanel>

        {WORKFLOW_RUNNER_ENABLED ? (
          <WorkbenchPanel
            title="Beam workflow"
            description="Build and run the one approved development workflow."
          >
            <div className="flex items-start gap-3">
              <span className="rounded-xl bg-cyan-500/10 p-2.5 text-cyan-300">
                <Workflow className="h-5 w-5" aria-hidden="true" />
              </span>
              <div className="min-w-0 flex-1">
                <p className="text-sm leading-6 text-zinc-400">
                  Ordered input, validation, beam design, review stop and evidence
                  export with fixed handlers and bounded execution.
                </p>
                <button
                  type="button"
                  onClick={() => navigate('/workbench/automation')}
                  className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-cyan-300 hover:text-cyan-200"
                >
                  Open workflow
                  <ArrowRight className="h-4 w-4" aria-hidden="true" />
                </button>
              </div>
            </div>
          </WorkbenchPanel>
        ) : null}

        <WorkbenchPanel
          title="Project workflow"
          description="Import, review, design and resolve in context."
        >
          <div className="flex items-start gap-3">
            <span className="rounded-xl bg-violet-500/10 p-2.5 text-violet-300">
              <Boxes className="h-5 w-5" aria-hidden="true" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="text-sm leading-6 text-zinc-400">
                Start with CSV, ETABS/SAFE, or the maintained sample. Full project
                resume appears here only after a durable snapshot exists.
              </p>
              <button
                type="button"
                onClick={() => navigate('/workbench/projects/new')}
                className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-violet-300 hover:text-violet-200"
              >
                Start project
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
          </div>
        </WorkbenchPanel>

        <div className="flex gap-3 rounded-xl border border-emerald-400/20 bg-emerald-400/[0.05] p-4 md:col-span-2">
          <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-emerald-300" aria-hidden="true" />
          <p className="text-xs leading-5 text-emerald-100/80">
            Supported scope and evidence status remain visible throughout the
            workflow. Software results do not replace qualified engineering review.
          </p>
        </div>
      </div>
    </WorkbenchShell>
  );
}
