import { act, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom';
import { LegacyRouteRedirect, ProjectStageRoute } from '../RouteGuards';
import { useDesignStore } from '../../store/designStore';
import { useWorkspaceStore } from '../../workspace/workspaceStore';

function LocationProbe() {
  const location = useLocation();
  return <p>{`${location.pathname}${location.search}`}</p>;
}

function renderLegacy(path: string, legacyPath: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path={legacyPath} element={<LegacyRouteRedirect legacyPath={legacyPath} />} />
        <Route path="*" element={<LocationProbe />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('route cutover guards', () => {
  beforeEach(() => {
    useDesignStore.getState().reset();
    useWorkspaceStore.getState().reset();
  });

  it('redirects legacy quick/import routes and preserves query state', () => {
    const design = renderLegacy('/design', '/design');
    expect(screen.getByText('/workbench/quick')).toBeInTheDocument();
    design.unmount();

    renderLegacy('/import?sample=true', '/import');
    expect(screen.getByText('/workbench/projects/new?sample=true')).toBeInTheDocument();
  });

  it('explains why an empty legacy result cannot be restored', () => {
    renderLegacy('/design/results?source=bookmark', '/design/results');
    expect(
      screen.getByText('/workbench/quick?source=bookmark&recovery=result-required'),
    ).toBeInTheDocument();
  });

  it('recovers a project route without identity and maps one with identity', () => {
    useWorkspaceStore.getState().setLoadState('ready');
    const missing = renderLegacy('/editor', '/editor');
    expect(screen.getByText('/workbench?recovery=project-required')).toBeInTheDocument();
    missing.unmount();

    useWorkspaceStore.getState().createProject('project 01', 'Project 01');
    renderLegacy('/editor', '/editor');
    expect(screen.getByText('/workbench/projects/project%2001/review')).toBeInTheDocument();
  });

  it('waits for initial persistence hydration before deciding a project route', () => {
    render(
      <MemoryRouter initialEntries={['/workbench/projects/project-1/review']}>
        <Routes>
          <Route
            path="/workbench/projects/:projectId/review"
            element={<ProjectStageRoute stage="review"><p>Review</p></ProjectStageRoute>}
          />
          <Route path="*" element={<LocationProbe />} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByRole('status')).toHaveTextContent('Restoring project');

    act(() => {
      useWorkspaceStore.getState().createProject('project-1', 'Project 1');
      useWorkspaceStore.getState().setStage('review');
    });
    expect(screen.getByText('Review')).toBeInTheDocument();
  });

  it('rejects a mismatched project and a stage beyond durable progress', () => {
    useWorkspaceStore.getState().createProject('project-1', 'Project 1');
    const mismatch = render(
      <MemoryRouter initialEntries={['/workbench/projects/project-2/review']}>
        <Routes>
          <Route
            path="/workbench/projects/:projectId/review"
            element={<ProjectStageRoute stage="review"><p>Review</p></ProjectStageRoute>}
          />
          <Route path="*" element={<LocationProbe />} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText('/workbench?recovery=project-required')).toBeInTheDocument();
    mismatch.unmount();

    render(
      <MemoryRouter initialEntries={['/workbench/projects/project-1/results']}>
        <Routes>
          <Route
            path="/workbench/projects/:projectId/results"
            element={<ProjectStageRoute stage="results"><p>Results</p></ProjectStageRoute>}
          />
          <Route path="*" element={<LocationProbe />} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText('/workbench/projects/project-1/import')).toBeInTheDocument();
  });
});
