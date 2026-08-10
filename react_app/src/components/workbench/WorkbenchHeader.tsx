import type { ReactNode } from 'react';
import type { SaveState } from '../../workspace/types';

export interface WorkbenchHeaderProps {
  title: string;
  projectName?: string;
  saveState?: SaveState;
  secondaryActions?: ReactNode;
  primaryAction?: ReactNode;
  children?: ReactNode;
}

const SAVE_STATE_LABEL: Record<SaveState, string> = {
  clean: 'Saved',
  saving: 'Saving',
  dirty: 'Unsaved changes',
  error: 'Save needs attention',
};

const SAVE_STATE_CLASS: Record<SaveState, string> = {
  clean: 'text-emerald-300',
  saving: 'text-blue-300',
  dirty: 'text-amber-300',
  error: 'text-rose-300',
};

/** A header with one intentional primary-action slot. */
export function WorkbenchHeader({
  title,
  projectName,
  saveState,
  secondaryActions,
  primaryAction,
  children,
}: WorkbenchHeaderProps) {
  return (
    <header className="border-b border-white/10 bg-zinc-950/95 px-4 py-3 sm:px-6">
      <div className="mx-auto flex max-w-screen-2xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0">
          {projectName ? <p className="truncate text-xs text-zinc-400">{projectName}</p> : null}
          <h1 className="truncate text-lg font-semibold text-white">{title}</h1>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {saveState ? (
            <span
              className={`text-xs font-medium ${SAVE_STATE_CLASS[saveState]}`}
              role="status"
            >
              {SAVE_STATE_LABEL[saveState]}
            </span>
          ) : null}
          {children}
          {secondaryActions ? <div className="flex items-center gap-2">{secondaryActions}</div> : null}
          {primaryAction ? (
            <div className="w-full [&>a]:w-full [&>button]:w-full sm:w-auto sm:[&>a]:w-auto sm:[&>button]:w-auto">
              {primaryAction}
            </div>
          ) : null}
        </div>
      </div>
    </header>
  );
}
