import { describe, expect, it, vi } from 'vitest';
import { FakeIndexedDbFactory } from './fakeIndexedDb';
import { WorkspaceAutosaveCoordinator } from '../autosave';
import {
  createIndexedDbWorkspacePersistence,
  WorkspaceConflictError,
} from '../persistence';
import { WORKSPACE_SCHEMA_VERSION, type WorkspaceSnapshotV1 } from '../types';

function snapshot(projectRevision: number): WorkspaceSnapshotV1 {
  return {
    schemaVersion: WORKSPACE_SCHEMA_VERSION,
    projectId: 'project-1',
    projectName: 'Project 1',
    projectRevision,
    members: [],
    selectedStage: 'review',
    selectedMemberId: null,
    selectedFloor: null,
    dirty: true,
    saveState: 'dirty',
    createdAt: '2026-08-10T00:00:00.000Z',
    updatedAt: `2026-08-10T00:0${projectRevision}:00.000Z`,
    savedAt: null,
    migrationOrigin: null,
  };
}

describe('workspace autosave coordinator', () => {
  it('coalesces queued snapshots and saves only the latest revision', async () => {
    const factory = new FakeIndexedDbFactory();
    const persistence = createIndexedDbWorkspacePersistence(factory as unknown as IDBFactory);
    const onStateChange = vi.fn();
    const coordinator = new WorkspaceAutosaveCoordinator(
      persistence,
      60_000,
      { onStateChange },
    );
    coordinator.prime('project-1', null);
    coordinator.schedule(snapshot(1));
    coordinator.schedule(snapshot(2));

    await coordinator.flush();

    await expect(persistence.load('project-1')).resolves.toMatchObject({
      projectRevision: 2,
    });
    expect(onStateChange.mock.calls.map(([state]) => state)).toEqual(['saving', 'saved']);
    coordinator.dispose();
  });

  it('blocks autosave after a newer external revision notice', async () => {
    const factory = new FakeIndexedDbFactory();
    const persistence = createIndexedDbWorkspacePersistence(factory as unknown as IDBFactory);
    await persistence.save(snapshot(1), { expectedProjectRevision: null });
    const onStateChange = vi.fn();
    const coordinator = new WorkspaceAutosaveCoordinator(
      persistence,
      60_000,
      { onStateChange },
    );
    coordinator.prime('project-1', 1);
    coordinator.noteExternalRevision({
      type: 'workspace-revision',
      sourceId: 'tab-2',
      projectId: 'project-1',
      projectRevision: 2,
      updatedAt: '2026-08-10T00:02:00.000Z',
    });
    coordinator.schedule(snapshot(2));

    await expect(coordinator.flush()).rejects.toBeInstanceOf(WorkspaceConflictError);
    await expect(persistence.load('project-1')).resolves.toMatchObject({
      projectRevision: 1,
    });
    expect(onStateChange.mock.calls.map(([state]) => state)).toEqual(['conflict']);
    coordinator.dispose();
  });
});
