/**
 * WorkflowHint - Contextual workflow guidance banner
 *
 * Displays dismissible hints for user guidance on key pages.
 * Dismissal state persists in localStorage.
 */
import { useState } from 'react';
import { X, Info, ArrowRight } from 'lucide-react';
import { cn } from '../../lib/utils';

export interface WorkflowHintProps {
  /** Current step number */
  stepNumber: number;
  /** Total number of steps */
  totalSteps: number;
  /** Title of the current step */
  title: string;
  /** Detailed description/guidance */
  description: string;
  /** localStorage key for dismiss persistence */
  storageKey: string;
  /** Optional additional action/hint */
  nextAction?: string;
  /** Optional className for customization */
  className?: string;
}

export function WorkflowHint({
  stepNumber,
  totalSteps,
  title,
  description,
  storageKey,
  nextAction,
  className,
}: WorkflowHintProps) {
  const [dismissed, setDismissed] = useState(() => {
    return localStorage.getItem(storageKey) === 'true';
  });

  const handleDismiss = () => {
    localStorage.setItem(storageKey, 'true');
    setDismissed(true);
  };

  if (dismissed) return null;

  return (
    <div
      className={cn(
        'relative flex items-start gap-3 px-4 py-3 rounded-lg border',
        'bg-blue-500/10 border-blue-500/30 text-blue-100',
        'animate-in fade-in slide-in-from-top-2 duration-300',
        className
      )}
      role="status"
      aria-live="polite"
    >
      {/* Icon */}
      <Info className="w-4 h-4 mt-0.5 flex-shrink-0 text-blue-400" aria-hidden="true" />

      {/* Content */}
      <div className="flex-1 min-w-0">
        {/* Header: Step X of Y + Title */}
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-semibold text-blue-300">
            Step {stepNumber} of {totalSteps}
          </span>
          <span className="text-xs text-blue-400/60">•</span>
          <span className="text-sm font-medium text-blue-50">{title}</span>
        </div>

        {/* Description */}
        <p className="text-xs text-blue-200/80 leading-relaxed">{description}</p>

        {/* Next Action (optional) */}
        {nextAction && (
          <div className="flex items-center gap-1.5 mt-2 text-xs text-blue-300">
            <ArrowRight className="w-3 h-3" aria-hidden="true" />
            <span>{nextAction}</span>
          </div>
        )}
      </div>

      {/* Dismiss button */}
      <button
        onClick={handleDismiss}
        className="flex-shrink-0 p-1 rounded hover:bg-blue-500/20 transition-colors group"
        aria-label="Dismiss hint"
        title="Dismiss this hint (won't show again)"
      >
        <X className="w-3.5 h-3.5 text-blue-400/60 group-hover:text-blue-300" />
      </button>
    </div>
  );
}
