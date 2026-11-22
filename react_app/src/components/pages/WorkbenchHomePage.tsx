import { ArrowRight, Boxes, Calculator, Layers3, ShieldCheck, Workflow } from 'lucide-react';
import type { ReactNode } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { projectStagePath } from '../../app/navigation';
import { WorkbenchHeader } from '../workbench/WorkbenchHeader';
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
      className="bg-paper pt-14 text-ink [--focus-color:var(--color-cobalt)] [color-scheme:light]"
      header={(
        <WorkbenchHeader
          title={title}
          projectName="IS 456 reinforced-concrete workbench"
          primaryAction={(
            <button
              type="button"
              onClick={() => navigate('/workbench/projects/new')}
              className="inline-flex min-h-10 items-center justify-center gap-2 rounded-sm bg-cobalt px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-cobalt-hover"
            >
              New project
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </button>
          )}
        />
      )}
    >
      <div className="mx-auto max-w-6xl p-4 sm:p-6">
        {searchParams.get('recovery') === 'project-required' ? (
          <div className="mb-5 border border-amber-700/30 bg-amber-100/60 p-4 text-sm text-ink" role="alert">
            Open an existing project or import a new one before using that project stage.
          </div>
        ) : null}
        {workspace ? (
          <section className="mb-6 border border-ink/20 bg-white p-4 shadow-[4px_4px_0_0_rgba(23,36,53,0.12)]" aria-labelledby="continue-project-title">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="font-mono text-xs font-semibold uppercase tracking-wider text-cobalt">Saved workspace</p>
                <h2 id="continue-project-title" className="mt-1 text-lg font-semibold">Continue {workspace.projectName}</h2>
                <p className="mt-1 text-sm text-ink/70">{workspace.members.length} members · {workspace.selectedStage} · revision {workspace.projectRevision} · {workspace.saveState === 'clean' ? 'saved locally' : workspace.saveState}</p>
              </div>
              <button
                type="button"
                onClick={() => navigate(projectStagePath(workspace.projectId, workspace.selectedStage))}
                className="inline-flex min-h-10 items-center gap-2 rounded-sm bg-cobalt px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-cobalt-hover"
              >
                Resume project
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
          </section>
        ) : loadState === 'loading' ? (
          <div className="mb-6 border border-ink/15 bg-white p-4 text-sm text-ink/75" role="status">
            Restoring the last local project…
          </div>
        ) : loadState === 'error' && loadError ? (
          <div className="mb-6 border border-rose-700/30 bg-rose-50 p-4 text-sm text-rose-900" role="alert">
            Saved project needs recovery: {loadError}
          </div>
        ) : null}

        <section className="border-b border-ink/20 pb-6" aria-label="Quick design and project import">
          <div className="grid gap-px border border-ink/20 bg-ink sm:grid-cols-2">
            <button type="button" onClick={() => navigate('/workbench/quick')} className="group min-h-40 bg-white p-5 text-left transition-colors hover:bg-cobalt hover:text-white">
              <Calculator className="h-6 w-6 text-cobalt group-hover:text-white" aria-hidden="true" />
              <span className="mt-4 block text-lg font-semibold">Quick beam</span>
              <span className="mt-1 block max-w-sm text-sm leading-6 text-ink/75 group-hover:text-white/85">Check one beam and inspect the governing result.</span>
              <span className="mt-4 inline-flex items-center gap-2 text-sm font-semibold">Open quick beam <ArrowRight className="h-4 w-4" aria-hidden="true" /></span>
            </button>
            <button type="button" onClick={() => navigate('/workbench/projects/new')} className="group min-h-40 bg-ink p-5 text-left text-white transition-colors hover:bg-cobalt">
              <Boxes className="h-6 w-6 text-paper" aria-hidden="true" />
              <span className="mt-4 block text-lg font-semibold">Projects</span>
              <span className="mt-1 block max-w-sm text-sm leading-6 text-white/75">Import and review multiple beams in a local project.</span>
              <span className="mt-4 inline-flex items-center gap-2 text-sm font-semibold">Start project <ArrowRight className="h-4 w-4" aria-hidden="true" /></span>
            </button>
          </div>
        </section>

        <section className="py-6" aria-labelledby="calculators-title">
          <h2 id="calculators-title" className="text-xl font-semibold">More design tools</h2>
          <div className="mt-4 grid border-l border-t border-ink/20 sm:grid-cols-2 lg:grid-cols-4">
            <DirectoryItem icon={<Layers3 className="h-5 w-5" />} title="Solid slabs" detail="One-way and common two-way slab checks." action="Open slab workbench" onClick={() => navigate('/workbench/slabs')} />
            <DirectoryItem icon={<ShieldCheck className="h-5 w-5" />} title="Column review" detail="Supplied rectangular tied-column section." action="Open column review" onClick={() => navigate('/workbench/columns/rectangular')} />
            <DirectoryItem icon={<Calculator className="h-5 w-5" />} title="Isolated footing" detail="Centred square or rectangular footing." action="Open isolated footing" onClick={() => navigate('/workbench/footing/isolated/concentric')} />
            <DirectoryItem icon={<Layers3 className="h-5 w-5" />} title="Building gravity" detail="Dead/live path and calculation book." action="Open gravity review" onClick={() => navigate('/workbench/building-gravity/v1')} />
            {WORKFLOW_RUNNER_ENABLED ? <DirectoryItem icon={<Workflow className="h-5 w-5" />} title="Beam workflow" detail="Approved development workflow." action="Open workflow" onClick={() => navigate('/workbench/automation')} /> : null}
          </div>
        </section>

        <div className="flex gap-3 border-t border-ink/20 py-5">
          <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-cobalt" aria-hidden="true" />
          <p className="max-w-3xl text-xs leading-5 text-ink/75">
            Engineering use requires review by a qualified structural engineer.
          </p>
        </div>
      </div>
    </WorkbenchShell>
  );
}

function DirectoryItem({
  icon,
  title,
  detail,
  action,
  onClick,
}: {
  icon: ReactNode;
  title: string;
  detail: string;
  action: string;
  onClick: () => void;
}) {
  return (
    <button type="button" onClick={onClick} className="group min-h-40 border-b border-r border-ink/20 bg-white p-4 text-left transition-colors hover:bg-paper">
      <span className="text-cobalt" aria-hidden="true">{icon}</span>
      <span className="mt-5 block font-semibold text-ink">{title}</span>
      <span className="mt-1 block text-sm leading-5 text-ink/70">{detail}</span>
      <span className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-cobalt group-hover:underline">{action} <ArrowRight className="h-4 w-4" aria-hidden="true" /></span>
    </button>
  );
}
