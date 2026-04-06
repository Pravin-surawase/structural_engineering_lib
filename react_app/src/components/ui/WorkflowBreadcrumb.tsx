/**
 * WorkflowBreadcrumb - Horizontal step indicator for batch workflow
 *
 * Shows the 4-step batch workflow journey: Import → Editor → Batch Design → Dashboard
 * Highlights current step, shows completed steps with checkmarks.
 * Completed steps are clickable for navigation.
 */
import { useNavigate, useLocation } from 'react-router-dom';
import { Check } from 'lucide-react';
import { motion } from 'framer-motion';
import { useImportedBeamsStore } from '../../store/importedBeamsStore';
import { cn } from '../../lib/utils';

interface Step {
  id: string;
  label: string;
  route: string;
}

const WORKFLOW_STEPS: Step[] = [
  { id: 'import', label: 'Import', route: '/import' },
  { id: 'editor', label: 'Editor', route: '/editor' },
  { id: 'batch', label: 'Batch Design', route: '/batch' },
  { id: 'dashboard', label: 'Dashboard', route: '/dashboard' },
];

export function WorkflowBreadcrumb() {
  const navigate = useNavigate();
  const location = useLocation();
  const { beams } = useImportedBeamsStore();

  // Determine current step index from route
  const currentStepIndex = WORKFLOW_STEPS.findIndex(
    (step) => step.route === location.pathname
  );

  // Step completion logic
  const isStepComplete = (stepIndex: number): boolean => {
    if (stepIndex === 0) {
      // Import: complete when beams.length > 0
      return beams.length > 0;
    }
    if (stepIndex === 1) {
      // Editor: complete when on editor or later (batch/dashboard)
      return currentStepIndex >= 1;
    }
    if (stepIndex === 2) {
      // Batch Design: complete when any beam has results
      return beams.some((b) => b.ast_required !== undefined);
    }
    if (stepIndex === 3) {
      // Dashboard: final step, complete when reached
      return currentStepIndex >= 3;
    }
    return false;
  };

  const handleStepClick = (stepIndex: number, route: string) => {
    // Only allow navigation to completed steps or current step
    if (stepIndex <= currentStepIndex || isStepComplete(stepIndex)) {
      navigate(route);
    }
  };

  return (
    <div className="w-full px-6 py-4 bg-zinc-900/50 border-b border-zinc-800">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between relative">
          {/* Background connecting line */}
          <div className="absolute top-4 left-0 right-0 h-px bg-zinc-700 -z-10" />

          {WORKFLOW_STEPS.map((step, index) => {
            const isCurrent = index === currentStepIndex;
            const isComplete = isStepComplete(index);
            const isClickable = index <= currentStepIndex || isComplete;
            const isPast = index < currentStepIndex;

            return (
              <motion.div
                key={step.id}
                className="flex flex-col items-center gap-2 flex-1 relative"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                {/* Step circle */}
                <button
                  onClick={() => handleStepClick(index, step.route)}
                  disabled={!isClickable}
                  className={cn(
                    'relative w-8 h-8 rounded-full flex items-center justify-center',
                    'transition-all duration-200 ring-4 ring-zinc-900/50',
                    isCurrent && 'bg-blue-500 text-white scale-110',
                    !isCurrent && isComplete && 'bg-green-600 text-white',
                    !isCurrent && !isComplete && 'bg-zinc-700 text-zinc-400',
                    isClickable && 'cursor-pointer hover:scale-105',
                    !isClickable && 'cursor-not-allowed opacity-50'
                  )}
                  aria-current={isCurrent ? 'step' : undefined}
                  aria-label={`${step.label}${isCurrent ? ' (current)' : ''}${isComplete ? ' (complete)' : ''}`}
                >
                  {isComplete && !isCurrent ? (
                    <Check className="w-4 h-4" strokeWidth={3} />
                  ) : (
                    <span className="text-sm font-semibold">{index + 1}</span>
                  )}

                  {/* Pulse animation for current step */}
                  {isCurrent && (
                    <motion.span
                      className="absolute inset-0 rounded-full bg-blue-500"
                      initial={{ scale: 1, opacity: 0.5 }}
                      animate={{ scale: 1.3, opacity: 0 }}
                      transition={{ repeat: Infinity, duration: 1.5 }}
                    />
                  )}
                </button>

                {/* Step label */}
                <span
                  className={cn(
                    'text-xs font-medium text-center whitespace-nowrap transition-colors',
                    isCurrent && 'text-blue-400',
                    !isCurrent && isComplete && 'text-green-400',
                    !isCurrent && !isComplete && 'text-zinc-500'
                  )}
                >
                  {step.label}
                </span>

                {/* Progress line between steps */}
                {index < WORKFLOW_STEPS.length - 1 && (
                  <div
                    className={cn(
                      'absolute top-4 left-1/2 w-full h-px transition-colors duration-300',
                      isPast ? 'bg-green-500' : 'bg-zinc-700'
                    )}
                    style={{ transform: 'translateY(-50%)' }}
                  />
                )}
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
