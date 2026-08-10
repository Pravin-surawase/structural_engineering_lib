import { describe, expect, it } from 'vitest';
import {
  parseWorkspaceSnapshot,
  serializeWorkspaceSnapshot,
  WorkspacePersistenceError,
} from '../persistence';
import {
  WORKSPACE_SCHEMA_VERSION,
  type WorkspaceSnapshotV1,
} from '../types';

const snapshot: WorkspaceSnapshotV1 = {
  schemaVersion: WORKSPACE_SCHEMA_VERSION,
  projectId: 'project-1',
  projectName: 'Project 1',
  projectRevision: 1,
  members: [],
  selectedStage: 'import',
  selectedMemberId: null,
  selectedFloor: null,
  dirty: false,
  saveState: 'clean',
  createdAt: '2026-08-10T00:00:00.000Z',
  updatedAt: '2026-08-10T00:00:00.000Z',
  savedAt: '2026-08-10T00:00:00.000Z',
  migrationOrigin: null,
};

describe('portable workspace persistence contract', () => {
  it('round-trips a valid versioned snapshot', () => {
    expect(parseWorkspaceSnapshot(serializeWorkspaceSnapshot(snapshot))).toEqual(snapshot);
  });

  it('fails closed on unknown schemas and malformed members', () => {
    expect(() => parseWorkspaceSnapshot(JSON.stringify({
      ...snapshot,
      schemaVersion: 2,
    }))).toThrow(WorkspacePersistenceError);

    expect(() => parseWorkspaceSnapshot(JSON.stringify({
      ...snapshot,
      members: [{ memberId: 'beam-1' }],
    }))).toThrow(WorkspacePersistenceError);
  });

  it('reports invalid JSON without returning a partial project', () => {
    expect(() => parseWorkspaceSnapshot('{not-json')).toThrow(
      /not valid JSON/i,
    );
  });
});
