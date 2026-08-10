import { useEffect, useRef, useState } from 'react';
import { WorkspaceAutosaveCoordinator } from './autosave';
import {
  createIndexedDbWorkspacePersistence,
  type WorkspacePersistence,
} from './persistence';
import {
  createWorkspaceRevisionSync,
  type WorkspaceRevisionSync,
} from './sync';
import type { WorkspaceSnapshotV1 } from './types';
import { useWorkspaceStore } from './workspaceStore';

interface WorkspaceRuntime {
  autosave: WorkspaceAutosaveCoordinator;
  persistence: WorkspacePersistence;
}

export const LAST_WORKSPACE_PROJECT_KEY = 'structlib-workbench-last-project';

function readLastProjectId(): string | null {
  try {
    return localStorage.getItem(LAST_WORKSPACE_PROJECT_KEY);
  } catch {
    return null;
  }
}

function writeLastProjectId(projectId: string | null): void {
  try {
    if (projectId) localStorage.setItem(LAST_WORKSPACE_PROJECT_KEY, projectId);
    else localStorage.removeItem(LAST_WORKSPACE_PROJECT_KEY);
  } catch {
    // IndexedDB remains authoritative; the pointer is only a small preference.
  }
}

export interface WorkspacePersistenceBridgeProps {
  autosaveDelayMs?: number;
  createPersistence?: () => WorkspacePersistence;
  createRevisionSync?: typeof createWorkspaceRevisionSync;
}

function currentSnapshotMatches(snapshot: WorkspaceSnapshotV1): boolean {
  const current = useWorkspaceStore.getState().snapshot;
  return Boolean(
    current
    && current.projectId === snapshot.projectId
    && current.projectRevision === snapshot.projectRevision,
  );
}

/** Connects the revisioned workspace store to durable local persistence. */
export function WorkspacePersistenceBridge({
  autosaveDelayMs = 500,
  createPersistence = createIndexedDbWorkspacePersistence,
  createRevisionSync = createWorkspaceRevisionSync,
}: WorkspacePersistenceBridgeProps = {}) {
  const snapshot = useWorkspaceStore((state) => state.snapshot);
  const [runtime, setRuntime] = useState<WorkspaceRuntime | null>(null);
  const syncRef = useRef<WorkspaceRevisionSync | null>(null);
  const persistenceFactoryRef = useRef(createPersistence);
  const revisionSyncFactoryRef = useRef(createRevisionSync);

  useEffect(() => {
    let active = true;
    let autosave: WorkspaceAutosaveCoordinator | null = null;
    try {
      const persistence = persistenceFactoryRef.current();
      autosave = new WorkspaceAutosaveCoordinator(
        persistence,
        autosaveDelayMs,
        {
          onStateChange(state, savedSnapshot) {
            if (!currentSnapshotMatches(savedSnapshot)) return;
            const store = useWorkspaceStore.getState();
            if (state === 'saving') store.setSaveState('saving');
            if (state === 'saved') {
              store.markSaved(savedSnapshot.updatedAt);
              writeLastProjectId(savedSnapshot.projectId);
              syncRef.current?.announce(savedSnapshot);
            }
            if (state === 'error' || state === 'conflict') {
              store.setSaveState('error');
            }
          },
        },
      );
      if (active) setRuntime({ autosave, persistence });

      const workspaceStore = useWorkspaceStore.getState();
      if (workspaceStore.snapshot) {
        workspaceStore.setLoadState('ready');
      } else {
        workspaceStore.setLoadState('loading');
        const lastProjectId = readLastProjectId();
        if (!lastProjectId) {
          workspaceStore.setLoadState('ready');
        } else {
          void persistence.load(lastProjectId)
            .then((loaded) => {
              if (!active) return;
              if (!loaded) {
                writeLastProjectId(null);
                useWorkspaceStore.getState().setLoadState('ready');
                return;
              }
              useWorkspaceStore.getState().loadSnapshot(loaded);
            })
            .catch((error: unknown) => {
              if (!active) return;
              useWorkspaceStore.getState().setLoadState(
                'error',
                error instanceof Error ? error.message : 'Saved project could not be restored.',
              );
            });
        }
      }
    } catch (error) {
      const store = useWorkspaceStore.getState();
      store.setSaveState('error');
      store.setLoadState(
        'error',
        error instanceof Error ? error.message : 'Project storage could not be initialized.',
      );
    }

    return () => {
      active = false;
      autosave?.dispose();
      syncRef.current?.close();
      syncRef.current = null;
    };
  }, [autosaveDelayMs]);

  useEffect(() => {
    if (snapshot?.projectId) writeLastProjectId(snapshot.projectId);
  }, [snapshot?.projectId]);

  useEffect(() => {
    syncRef.current?.close();
    syncRef.current = null;
    const current = useWorkspaceStore.getState().snapshot;
    if (!runtime || !current || current.projectId !== snapshot?.projectId) return;

    runtime.autosave.prime(
      current.projectId,
      current.savedAt === null ? null : current.projectRevision,
    );
    try {
      syncRef.current = revisionSyncFactoryRef.current(
        crypto.randomUUID(),
        (notice) => {
          runtime.autosave.noteExternalRevision(notice);
          const current = useWorkspaceStore.getState().snapshot;
          if (current?.projectId === notice.projectId) {
            useWorkspaceStore.getState().setSaveState('error');
          }
        },
      );
    } catch {
      useWorkspaceStore.getState().setSaveState('error');
    }

    return () => {
      syncRef.current?.close();
      syncRef.current = null;
    };
  }, [runtime, snapshot?.projectId, snapshot?.savedAt]);

  useEffect(() => {
    if (
      !runtime
      || !snapshot
      || !snapshot.dirty
      || snapshot.saveState !== 'dirty'
    ) {
      return;
    }
    runtime.autosave.schedule(snapshot);
  }, [runtime, snapshot]);

  return null;
}
