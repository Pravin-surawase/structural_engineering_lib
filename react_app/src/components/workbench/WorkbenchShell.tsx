import type { ReactNode } from 'react';

export interface WorkbenchShellProps {
  header: ReactNode;
  children: ReactNode;
  inspector?: ReactNode;
  tray?: ReactNode;
  className?: string;
}

/**
 * Structural layout only. Route, selection, and status ownership stay with the
 * consuming workbench flow.
 */
export function WorkbenchShell({
  header,
  children,
  inspector,
  tray,
  className = '',
}: WorkbenchShellProps) {
  return (
    <section className={`min-h-dvh bg-zinc-950 text-zinc-100 ${className}`}>
      {header}
      <div className="grid min-h-0 grid-cols-1 xl:grid-cols-[minmax(0,1fr)_22rem]">
        <section className="min-w-0" aria-label="Workbench content">
          {children}
        </section>
        {inspector ? (
          <aside
            aria-label="Selected item inspector"
            className="min-w-0 border-t border-white/10 bg-zinc-900/50 xl:border-t-0 xl:border-l"
          >
            {inspector}
          </aside>
        ) : null}
      </div>
      {tray ? (
        <section
          aria-label="Workbench results and actions"
          className="border-t border-white/10 bg-zinc-950/95"
        >
          {tray}
        </section>
      ) : null}
    </section>
  );
}
