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

  useEffect(() => {
    let active = true;
    let autosave: WorkspaceAutosaveCoordinator | null = null;
    try {
      const persistence = createPersistence();
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
              syncRef.current?.announce(savedSnapshot);
            }
            if (state === 'error' || state === 'conflict') {
              store.setSaveState('error');
            }
          },
        },
      );
      if (active) setRuntime({ autosave, persistence });
    } catch {
      useWorkspaceStore.getState().setSaveState('error');
    }

    return () => {
      active = false;
      autosave?.dispose();
      syncRef.current?.close();
      syncRef.current = null;
    };
  }, [autosaveDelayMs, createPersistence]);

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
      syncRef.current = createRevisionSync(
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
  }, [createRevisionSync, runtime, snapshot?.projectId, snapshot?.savedAt]);

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
