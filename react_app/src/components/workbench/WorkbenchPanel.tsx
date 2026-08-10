import { useId, type ReactNode } from 'react';

export interface WorkbenchPanelProps {
  title: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
}

export function WorkbenchPanel({
  title,
  description,
  actions,
  children,
  className = '',
}: WorkbenchPanelProps) {
  const headingId = useId();
  return (
    <section className={`rounded-xl border border-white/10 bg-zinc-900/60 ${className}`} aria-labelledby={headingId}>
      <div className="flex items-start justify-between gap-3 border-b border-white/10 px-4 py-3">
        <div className="min-w-0">
          <h2 id={headingId} className="text-sm font-semibold text-white">{title}</h2>
          {description ? <p className="mt-1 text-xs text-zinc-400">{description}</p> : null}
        </div>
        {actions ? <div className="shrink-0">{actions}</div> : null}
      </div>
      <div className="p-4">{children}</div>
    </section>
  );
}
