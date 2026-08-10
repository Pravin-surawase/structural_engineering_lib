export type WorkbenchStageState = 'complete' | 'current' | 'available' | 'locked';

export interface WorkbenchStage {
  id: string;
  label: string;
  state: WorkbenchStageState;
  description?: string;
  onSelect?: () => void;
}

export interface StageNavigationProps {
  stages: readonly WorkbenchStage[];
  ariaLabel?: string;
}

const STATE_CLASS: Record<WorkbenchStageState, string> = {
  complete: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200',
  current: 'border-blue-400 bg-blue-500/15 text-blue-100',
  available: 'border-white/15 bg-white/5 text-zinc-200 hover:bg-white/10',
  locked: 'border-white/10 bg-zinc-900 text-zinc-500',
};

/** Renders supplied stages only; it deliberately has no route knowledge. */
export function StageNavigation({ stages, ariaLabel = 'Workbench stages' }: StageNavigationProps) {
  return (
    <nav aria-label={ariaLabel} className="overflow-x-auto border-b border-white/10 bg-zinc-950 px-4 sm:px-6">
      <ol className="mx-auto flex min-w-max max-w-screen-2xl gap-2 py-2">
        {stages.map((stage, index) => {
          const locked = stage.state === 'locked';
          const current = stage.state === 'current';
          return (
            <li key={stage.id}>
              <button
                type="button"
                disabled={locked || !stage.onSelect}
                onClick={stage.onSelect}
                aria-current={current ? 'step' : undefined}
                aria-describedby={stage.description ? `${stage.id}-description` : undefined}
                className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-left text-sm font-medium transition-colors disabled:cursor-not-allowed ${STATE_CLASS[stage.state]}`}
              >
                <span aria-hidden="true" className="text-xs tabular-nums">{index + 1}</span>
                <span>{stage.label}</span>
              </button>
              {stage.description ? (
                <span id={`${stage.id}-description`} className="sr-only">{stage.description}</span>
              ) : null}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
