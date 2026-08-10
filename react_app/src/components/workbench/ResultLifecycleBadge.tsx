import type { ReactNode } from 'react';
import { AlertTriangle, CheckCircle2, CircleDashed, Clock3, FileWarning, ShieldX } from 'lucide-react';
import type { ResultLifecycle } from '../../workspace/types';

export interface ResultLifecycleBadgeProps {
  lifecycle: ResultLifecycle;
  className?: string;
}

interface LifecyclePresentation {
  label: string;
  icon: ReactNode;
  className: string;
}

const LIFECYCLE_PRESENTATION: Record<ResultLifecycle, LifecyclePresentation> = {
  current: { label: 'Current result', icon: <CheckCircle2 aria-hidden="true" className="h-3.5 w-3.5" />, className: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200' },
  stale: { label: 'Stale result', icon: <Clock3 aria-hidden="true" className="h-3.5 w-3.5" />, className: 'border-amber-500/40 bg-amber-500/10 text-amber-200' },
  pending: { label: 'Result pending', icon: <CircleDashed aria-hidden="true" className="h-3.5 w-3.5" />, className: 'border-blue-500/40 bg-blue-500/10 text-blue-200' },
  error: { label: 'Result error', icon: <AlertTriangle aria-hidden="true" className="h-3.5 w-3.5" />, className: 'border-rose-500/40 bg-rose-500/10 text-rose-200' },
  unsupported: { label: 'Unsupported case', icon: <ShieldX aria-hidden="true" className="h-3.5 w-3.5" />, className: 'border-violet-500/40 bg-violet-500/10 text-violet-200' },
  not_evaluated: { label: 'Not evaluated', icon: <FileWarning aria-hidden="true" className="h-3.5 w-3.5" />, className: 'border-zinc-500/50 bg-zinc-500/10 text-zinc-200' },
};

/** Presentation-only lifecycle marker. Callers supply the authoritative lifecycle. */
export function ResultLifecycleBadge({ lifecycle, className = '' }: ResultLifecycleBadgeProps) {
  const presentation = LIFECYCLE_PRESENTATION[lifecycle];
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium ${presentation.className} ${className}`} role="status">
      {presentation.icon}
      {presentation.label}
    </span>
  );
}
