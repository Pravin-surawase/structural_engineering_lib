export type ProjectStage = 'import' | 'review' | 'design' | 'results';

export interface GlobalDestination {
  id: 'workbench' | 'projects';
  label: string;
  path: string;
}

export interface ProjectStageDefinition {
  id: ProjectStage;
  label: string;
  order: number;
  requires: ProjectStage | null;
}

export interface LegacyRouteDecision {
  legacyPath: string;
  destination: string;
  requiresProject: boolean;
  requiresSettledRun: boolean;
}

export type GlobalDestinationId = GlobalDestination['id'];

export const GLOBAL_DESTINATIONS: readonly GlobalDestination[] = [
  { id: 'workbench', label: 'Workbench', path: '/workbench' },
  { id: 'projects', label: 'Projects', path: '/workbench/projects' },
] as const;

export const PROJECT_STAGES: readonly ProjectStageDefinition[] = [
  { id: 'import', label: 'Import', order: 0, requires: null },
  { id: 'review', label: 'Review', order: 1, requires: 'import' },
  { id: 'design', label: 'Design', order: 2, requires: 'review' },
  { id: 'results', label: 'Results', order: 3, requires: 'design' },
] as const;

export const LEGACY_ROUTE_DECISIONS: readonly LegacyRouteDecision[] = [
  {
    legacyPath: '/start',
    destination: '/workbench',
    requiresProject: false,
    requiresSettledRun: false,
  },
  {
    legacyPath: '/design',
    destination: '/workbench/quick',
    requiresProject: false,
    requiresSettledRun: false,
  },
  {
    legacyPath: '/design/results',
    destination: '/workbench/quick',
    requiresProject: false,
    requiresSettledRun: true,
  },
  {
    legacyPath: '/import',
    destination: '/workbench/projects/new',
    requiresProject: false,
    requiresSettledRun: false,
  },
  {
    legacyPath: '/editor',
    destination: '/workbench/projects/:projectId/review',
    requiresProject: true,
    requiresSettledRun: false,
  },
  {
    legacyPath: '/batch',
    destination: '/workbench/projects/:projectId/design',
    requiresProject: true,
    requiresSettledRun: false,
  },
  {
    legacyPath: '/dashboard',
    destination: '/workbench/projects/:projectId/results',
    requiresProject: true,
    requiresSettledRun: true,
  },
] as const;

export function projectStagePath(projectId: string, stage: ProjectStage): string {
  const normalizedId = projectId.trim();
  if (!normalizedId) {
    throw new Error('A project ID is required to build a project-stage route.');
  }
  return `/workbench/projects/${encodeURIComponent(normalizedId)}/${stage}`;
}

export function stageIsReachable(
  stage: ProjectStage,
  completedStages: ReadonlySet<ProjectStage>,
): boolean {
  const definition = PROJECT_STAGES.find((candidate) => candidate.id === stage);
  if (!definition) return false;
  return PROJECT_STAGES
    .filter((candidate) => candidate.order < definition.order)
    .every((candidate) => completedStages.has(candidate.id));
}

export function resolveLegacyDestination(
  legacyPath: string,
  projectId?: string | null,
): string | null {
  const decision = LEGACY_ROUTE_DECISIONS.find((candidate) => candidate.legacyPath === legacyPath);
  if (!decision) return null;
  if (!decision.requiresProject) return decision.destination;
  if (!projectId?.trim()) return '/workbench?recovery=project-required';
  return decision.destination.replace(':projectId', encodeURIComponent(projectId.trim()));
}

export function activeGlobalDestination(pathname: string): GlobalDestinationId | null {
  if (
    pathname.startsWith('/workbench/projects')
    || ['/import', '/editor', '/batch', '/dashboard'].includes(pathname)
  ) {
    return 'projects';
  }
  if (
    pathname === '/workbench'
    || pathname.startsWith('/workbench/quick')
    || pathname === '/start'
    || pathname.startsWith('/design')
  ) {
    return 'workbench';
  }
  return null;
}
