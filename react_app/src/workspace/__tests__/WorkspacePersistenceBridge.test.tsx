import { render, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { WorkspacePersistenceBridge } from '../WorkspacePersistenceBridge';
import { createIndexedDbWorkspacePersistence } from '../persistence';
import type { WorkspaceRevisionNotice } from '../sync';
import { useWorkspaceStore } from '../workspaceStore';
import { FakeIndexedDbFactory } from './fakeIndexedDb';

describe('WorkspacePersistenceBridge', () => {
  beforeEach(() => useWorkspaceStore.getState().reset());

  it('persists a dirty project and reports a newer external revision', async () => {
    const factory = new FakeIndexedDbFactory();
    const persistence = createIndexedDbWorkspacePersistence(
      factory as unknown as IDBFactory,
    );
    const announce = vi.fn();
    const receiveExternalRevision = vi.fn<(notice: WorkspaceRevisionNotice) => void>();
    useWorkspaceStore.getState().createProject(
      'project-1',
      'Project 1',
      '2026-08-10T00:00:00.000Z',
    );

    render(
      <WorkspacePersistenceBridge
        autosaveDelayMs={0}
        createPersistence={() => persistence}
        createRevisionSync={(_sourceId, onExternal) => {
          receiveExternalRevision.mockImplementation(onExternal);
          return { announce, close: vi.fn() };
        }}
      />,
    );

    await waitFor(() => {
      expect(useWorkspaceStore.getState().snapshot?.saveState).toBe('clean');
    });
    await expect(persistence.load('project-1')).resolves.toMatchObject({
      projectRevision: 1,
      dirty: false,
      saveState: 'clean',
    });
    expect(announce).toHaveBeenCalledOnce();

    receiveExternalRevision({
      type: 'workspace-revision',
      sourceId: 'other-tab',
      projectId: 'project-1',
      projectRevision: 2,
      updatedAt: '2026-08-10T00:01:00.000Z',
    });
    expect(useWorkspaceStore.getState().snapshot?.saveState).toBe('error');
  });
});
