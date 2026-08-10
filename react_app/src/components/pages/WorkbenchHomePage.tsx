import { ArrowRight, Boxes, Calculator, ShieldCheck } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { WorkbenchHeader } from '../workbench/WorkbenchHeader';
import { WorkbenchPanel } from '../workbench/WorkbenchPanel';
import { WorkbenchShell } from '../workbench/WorkbenchShell';

export interface WorkbenchHomePageProps {
  initialView?: 'workbench' | 'projects';
}

export function WorkbenchHomePage({
  initialView = 'workbench',
}: WorkbenchHomePageProps) {
  const navigate = useNavigate();
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
