import type { ReactNode } from 'react';
import { Navigate, useLocation, useParams } from 'react-router-dom';
import {
  PROJECT_STAGES,
  projectStagePath,
  resolveLegacyDestination,
  type ProjectStage,
} from './navigation';
import { useDesignStore } from '../store/designStore';
import { useWorkspaceStore } from '../workspace/workspaceStore';

export function LegacyRouteRedirect({ legacyPath }: { legacyPath: string }) {
  const location = useLocation();
  const projectId = useWorkspaceStore((state) => state.snapshot?.projectId);
  const resultLifecycle = useDesignStore((state) => state.resultLifecycle);
  const destination = resolveLegacyDestination(legacyPath, projectId) ?? '/workbench';
  const search = new URLSearchParams(location.search);
  if (legacyPath === '/design/results' && resultLifecycle !== 'current') {
    search.set('recovery', 'result-required');
  }
  const query = search.toString();
  return <Navigate to={`${destination}${query ? `?${query}` : ''}`} replace />;
}

export function ProjectStageRoute({
  stage,
  children,
}: {
  stage: ProjectStage;
  children: ReactNode;
}) {
  const { projectId } = useParams<{ projectId: string }>();
  const snapshot = useWorkspaceStore((state) => state.snapshot);
  const loadState = useWorkspaceStore((state) => state.loadState);

  if (loadState === 'loading') {
    return <p className="p-6 text-sm text-zinc-400" role="status">Restoring project…</p>;
  }
  if (!projectId || !snapshot || snapshot.projectId !== projectId) {
    return <Navigate to="/workbench?recovery=project-required" replace />;
  }
  const requestedOrder = PROJECT_STAGES.find((item) => item.id === stage)?.order ?? 0;
  const currentOrder = PROJECT_STAGES.find(
    (item) => item.id === snapshot.selectedStage,
  )?.order ?? 0;
  if (requestedOrder > currentOrder) {
    return <Navigate to={projectStagePath(snapshot.projectId, snapshot.selectedStage)} replace />;
  }
  return children;
}
