/** Compatibility adapter from legacy project routes to the typed stage model. */
import { useLocation, useNavigate } from 'react-router-dom';
import {
  PROJECT_STAGES,
  stageIsReachable,
  type ProjectStage,
} from '../../app/navigation';
import { useImportedBeamsStore } from '../../store/importedBeamsStore';
import {
  StageNavigation,
  type WorkbenchStage,
} from '../workbench/StageNavigation';

const LEGACY_STAGE_ROUTES: Record<ProjectStage, string> = {
  import: '/import',
  review: '/editor',
  design: '/batch',
  results: '/dashboard',
};

function stageForPath(pathname: string): ProjectStage | null {
  const legacy = Object.entries(LEGACY_STAGE_ROUTES).find(([, path]) => path === pathname);
  if (legacy) return legacy[0] as ProjectStage;
  const canonical = PROJECT_STAGES.find((stage) => pathname.endsWith(`/${stage.id}`));
  return canonical?.id ?? null;
}

export function WorkflowBreadcrumb() {
  const navigate = useNavigate();
  const location = useLocation();
  const { beams } = useImportedBeamsStore();
  const currentStage = stageForPath(location.pathname);
  const currentOrder = PROJECT_STAGES.find((stage) => stage.id === currentStage)?.order ?? -1;
  const completed = new Set<ProjectStage>();

  if (beams.length > 0) completed.add('import');
  if (currentOrder > 1) completed.add('review');
  if (beams.some((beam) => beam.ast_required !== undefined)) completed.add('design');

  const stages: WorkbenchStage[] = PROJECT_STAGES.map((stage) => {
    const isCurrent = stage.id === currentStage;
    const isComplete = completed.has(stage.id) && !isCurrent;
    const isAvailable = stageIsReachable(stage.id, completed);
    const state = isCurrent
      ? 'current'
      : isComplete
        ? 'complete'
        : isAvailable
          ? 'available'
          : 'locked';

    return {
      id: stage.id,
      label: stage.label,
      state,
      description: state === 'locked' ? `Complete ${stage.requires ?? 'the prior stage'} first` : undefined,
      onSelect: state === 'locked'
        ? undefined
        : () => navigate(LEGACY_STAGE_ROUTES[stage.id]),
    };
  });

  return <StageNavigation stages={stages} ariaLabel="Project stages" />;
}
