import { useId, type ReactNode } from 'react';

export interface WorkbenchPanelProps {
  title: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
  tone?: 'ink' | 'paper';
  className?: string;
}

export function WorkbenchPanel({
  title,
  description,
  actions,
  children,
  tone = 'ink',
  className = '',
}: WorkbenchPanelProps) {
  const headingId = useId();
  const isPaper = tone === 'paper';
  return (
    <section className={`min-w-0 rounded-sm border ${isPaper ? 'border-ink/20 bg-white text-ink [--focus-color:var(--color-cobalt)] [color-scheme:light]' : 'border-zinc-700 bg-zinc-900 text-zinc-100 [--focus-color:#6e9cfa] [color-scheme:dark]'} ${className}`} aria-labelledby={headingId}>
      <div className={`flex flex-wrap items-start justify-between gap-3 border-b px-4 py-3 ${isPaper ? 'border-ink/20' : 'border-zinc-700'}`}>
        <div className="min-w-0">
          <h2 id={headingId} className="text-sm font-semibold">{title}</h2>
          {description ? <p className={`mt-1 text-xs ${isPaper ? 'text-ink/75' : 'text-zinc-300'}`}>{description}</p> : null}
        </div>
        {actions ? <div className="shrink-0">{actions}</div> : null}
      </div>
      <div className="p-4">{children}</div>
    </section>
  );
}
