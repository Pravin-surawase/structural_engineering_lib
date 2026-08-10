import {
  WorkspaceConflictError,
  type WorkspacePersistence,
} from './persistence';
import type { WorkspaceRevisionNotice } from './sync';
import type { WorkspaceSnapshotV1 } from './types';

export type WorkspaceAutosaveState = 'saving' | 'saved' | 'error' | 'conflict';

export interface WorkspaceAutosaveCallbacks {
  onStateChange?: (
    state: WorkspaceAutosaveState,
    snapshot: WorkspaceSnapshotV1,
    error?: unknown,
  ) => void;
}

/**
 * Debounces durable saves while keeping the persisted revision explicit.
 * Live integration must prime each project before scheduling its first save.
 */
export class WorkspaceAutosaveCoordinator {
  private readonly persistence: WorkspacePersistence;
  private readonly delayMs: number;
  private readonly callbacks: WorkspaceAutosaveCallbacks;
  private readonly persistedRevisions = new Map<string, number | null>();
  private readonly externalRevisions = new Map<string, number>();
  private queued: WorkspaceSnapshotV1 | null = null;
  private timer: ReturnType<typeof setTimeout> | null = null;
  private activeFlush: Promise<void> | null = null;

  constructor(
    persistence: WorkspacePersistence,
    delayMs = 500,
    callbacks: WorkspaceAutosaveCallbacks = {},
  ) {
    this.persistence = persistence;
    this.delayMs = delayMs;
    this.callbacks = callbacks;
  }

  prime(projectId: string, persistedRevision: number | null): void {
    if (!projectId.trim()) throw new Error('A project ID is required for autosave.');
    if (persistedRevision !== null && (!Number.isInteger(persistedRevision) || persistedRevision < 1)) {
      throw new Error('Persisted project revision must be a positive integer or null.');
    }
    this.persistedRevisions.set(projectId, persistedRevision);
    this.externalRevisions.delete(projectId);
  }

  schedule(snapshot: WorkspaceSnapshotV1): void {
    if (!this.persistedRevisions.has(snapshot.projectId)) {
      throw new Error('Autosave must be primed with the persisted project revision.');
    }
    this.queued = structuredClone(snapshot);
    if (this.timer !== null) clearTimeout(this.timer);
    this.timer = setTimeout(() => {
      this.timer = null;
      void this.flush().catch(() => undefined);
    }, this.delayMs);
  }

  noteExternalRevision(notice: WorkspaceRevisionNotice): void {
    if (!this.persistedRevisions.has(notice.projectId)) return;
    const persistedRevision = this.persistedRevisions.get(notice.projectId) ?? 0;
    if (notice.projectRevision > persistedRevision) {
      this.externalRevisions.set(notice.projectId, notice.projectRevision);
    }
  }

  flush(): Promise<void> {
    if (this.timer !== null) {
      clearTimeout(this.timer);
      this.timer = null;
    }
    if (this.activeFlush) return this.activeFlush;
    this.activeFlush = this.flushQueued().finally(() => {
      this.activeFlush = null;
    });
    return this.activeFlush;
  }

  dispose(): void {
    if (this.timer !== null) clearTimeout(this.timer);
    this.timer = null;
    this.queued = null;
  }

  private async flushQueued(): Promise<void> {
    while (this.queued) {
      const snapshot = this.queued;
      this.queued = null;
      const expectedRevision = this.persistedRevisions.get(snapshot.projectId);
      const externalRevision = this.externalRevisions.get(snapshot.projectId);
      if (externalRevision !== undefined) {
        const error = new WorkspaceConflictError(
          snapshot.projectId,
          expectedRevision,
          externalRevision,
        );
        this.callbacks.onStateChange?.('conflict', snapshot, error);
        throw error;
      }

      this.callbacks.onStateChange?.('saving', snapshot);
      try {
        await this.persistence.save(snapshot, {
          expectedProjectRevision: expectedRevision,
        });
        this.persistedRevisions.set(snapshot.projectId, snapshot.projectRevision);
        this.callbacks.onStateChange?.('saved', snapshot);
      } catch (error) {
        this.callbacks.onStateChange?.(
          error instanceof WorkspaceConflictError ? 'conflict' : 'error',
          snapshot,
          error,
        );
        throw error;
      }
    }
  }
}
