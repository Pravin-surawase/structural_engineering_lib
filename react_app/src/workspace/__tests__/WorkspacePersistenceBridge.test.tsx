import { render, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { WorkspacePersistenceBridge } from '../WorkspacePersistenceBridge';
import { createIndexedDbWorkspacePersistence } from '../persistence';
import type { WorkspaceRevisionNotice } from '../sync';
import { useWorkspaceStore } from '../workspaceStore';
import { FakeIndexedDbFactory } from './fakeIndexedDb';

describe('WorkspacePersistenceBridge', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.mocked(localStorage.getItem).mockReset();
    vi.mocked(localStorage.setItem).mockReset();
    vi.mocked(localStorage.removeItem).mockReset();
    useWorkspaceStore.getState().reset();
  });

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

  it('restores the last saved project from the small local preference pointer', async () => {
    const factory = new FakeIndexedDbFactory();
    const persistence = createIndexedDbWorkspacePersistence(
      factory as unknown as IDBFactory,
    );
    useWorkspaceStore.getState().createProject(
      'project-restore',
      'Restored Project',
      '2026-08-10T00:00:00.000Z',
    );
    const snapshot = useWorkspaceStore.getState().snapshot!;
    await persistence.save(snapshot, { expectedProjectRevision: null });
    useWorkspaceStore.getState().reset();
    vi.mocked(localStorage.getItem).mockReturnValue('project-restore');
    await expect(persistence.load('project-restore')).resolves.toMatchObject({
      projectId: 'project-restore',
    });

    render(
      <WorkspacePersistenceBridge
        autosaveDelayMs={0}
        createPersistence={() => persistence}
        createRevisionSync={() => ({ announce: vi.fn(), close: vi.fn() })}
      />,
    );

    await waitFor(() => {
      expect(useWorkspaceStore.getState().snapshot?.projectId).toBe('project-restore');
    });
    expect(useWorkspaceStore.getState().loadState).toBe('ready');
  });
});
