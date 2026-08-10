import { describe, expect, it } from 'vitest';
import {
  GLOBAL_DESTINATIONS,
  LEGACY_ROUTE_DECISIONS,
  PROJECT_STAGES,
  projectStagePath,
  resolveLegacyDestination,
  stageIsReachable,
} from '../navigation';

describe('workbench navigation contract', () => {
  it('keeps one compact global destination source', () => {
    expect(GLOBAL_DESTINATIONS.map((destination) => destination.id)).toEqual([
      'workbench',
      'projects',
    ]);
    expect(new Set(GLOBAL_DESTINATIONS.map((destination) => destination.path)).size).toBe(2);
  });

  it('keeps project stages ordered with explicit prerequisites', () => {
    expect(PROJECT_STAGES.map((stage) => stage.id)).toEqual([
      'import',
      'review',
      'design',
      'results',
    ]);
    expect(stageIsReachable('import', new Set())).toBe(true);
    expect(stageIsReachable('review', new Set())).toBe(false);
    expect(stageIsReachable('review', new Set(['import']))).toBe(true);
    expect(stageIsReachable('results', new Set(['import', 'review']))).toBe(false);
    expect(stageIsReachable('results', new Set(['design']))).toBe(false);
    expect(stageIsReachable('results', new Set(['import', 'review', 'design']))).toBe(true);
  });

  it('builds encoded project paths and fails closed without identity', () => {
    expect(projectStagePath('project 01', 'review')).toBe(
      '/workbench/projects/project%2001/review',
    );
    expect(() => projectStagePath('  ', 'review')).toThrow(/project ID is required/i);
  });

  it('maps every legacy route and recovers when a project is missing', () => {
    expect(LEGACY_ROUTE_DECISIONS).toHaveLength(7);
    expect(resolveLegacyDestination('/design')).toBe('/workbench/quick');
    expect(resolveLegacyDestination('/editor')).toBe(
      '/workbench?recovery=project-required',
    );
    expect(resolveLegacyDestination('/editor', 'sample')).toBe(
      '/workbench/projects/sample/review',
    );
    expect(resolveLegacyDestination('/unknown')).toBeNull();
  });
});
