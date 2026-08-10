import {
  WORKSPACE_SCHEMA_VERSION,
  isWorkspaceSnapshotV1,
  type PersistedWorkspaceRecord,
  type WorkspaceProjectSummary,
  type WorkspaceSnapshotV1,
} from './types';

const DATABASE_NAME = 'structlib-workbench';
const DATABASE_VERSION = 1;
const PROJECT_STORE = 'projects';

export interface WorkspaceSaveOptions {
  expectedProjectRevision?: number | null;
  savedAt?: string;
}

export class WorkspacePersistenceError extends Error {
  constructor(message: string, options?: ErrorOptions) {
    super(message, options);
    this.name = 'WorkspacePersistenceError';
  }
}

export class WorkspaceRecoveryRequiredError extends WorkspacePersistenceError {
  readonly projectId: string;

  constructor(projectId: string) {
    super(
      'The latest saved project is unreadable. A last-known-good snapshot is available for explicit recovery.',
    );
    this.name = 'WorkspaceRecoveryRequiredError';
    this.projectId = projectId;
  }
}

export class WorkspaceSchemaVersionError extends WorkspacePersistenceError {
  readonly schemaVersion: unknown;

  constructor(schemaVersion: unknown) {
    super(`Unsupported workspace schema version: ${String(schemaVersion)}.`);
    this.name = 'WorkspaceSchemaVersionError';
    this.schemaVersion = schemaVersion;
  }
}

export class WorkspaceConflictError extends WorkspacePersistenceError {
  readonly projectId: string;
  readonly expectedProjectRevision: number | null | undefined;
  readonly actualProjectRevision: number | null;

  constructor(
    projectId: string,
    expectedProjectRevision: number | null | undefined,
    actualProjectRevision: number | null,
  ) {
    super('Project save was rejected because a newer external revision exists.');
    this.name = 'WorkspaceConflictError';
    this.projectId = projectId;
    this.expectedProjectRevision = expectedProjectRevision;
    this.actualProjectRevision = actualProjectRevision;
  }
}

export interface WorkspacePersistence {
  save(snapshot: WorkspaceSnapshotV1, options?: WorkspaceSaveOptions): Promise<void>;
  load(projectId: string): Promise<WorkspaceSnapshotV1 | null>;
  loadLastKnownGood(projectId: string): Promise<WorkspaceSnapshotV1 | null>;
  recoverLastKnownGood(projectId: string): Promise<WorkspaceSnapshotV1>;
  list(): Promise<WorkspaceProjectSummary[]>;
  delete(projectId: string): Promise<boolean>;
  clear(): Promise<void>;
}

function requestResult<T>(request: IDBRequest<T>): Promise<T> {
  return new Promise((resolve, reject) => {
    request.addEventListener('success', () => resolve(request.result), { once: true });
    request.addEventListener(
      'error',
      () => reject(request.error ?? new Error('IndexedDB request failed.')),
      { once: true },
    );
  });
}

function transactionComplete(transaction: IDBTransaction): Promise<void> {
  return new Promise((resolve, reject) => {
    transaction.addEventListener('complete', () => resolve(), { once: true });
    transaction.addEventListener(
      'abort',
      () => reject(transaction.error ?? new Error('IndexedDB transaction aborted.')),
      { once: true },
    );
    transaction.addEventListener(
      'error',
      () => reject(transaction.error ?? new Error('IndexedDB transaction failed.')),
      { once: true },
    );
  });
}

function trackedTransactionCompletion(transaction: IDBTransaction): Promise<void> {
  const completed = transactionComplete(transaction);
  void completed.catch(() => undefined);
  return completed;
}

function openDatabase(factory: IDBFactory): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = factory.open(DATABASE_NAME, DATABASE_VERSION);
    request.addEventListener(
      'upgradeneeded',
      () => {
        const database = request.result;
        if (!database.objectStoreNames.contains(PROJECT_STORE)) {
          database.createObjectStore(PROJECT_STORE, { keyPath: 'projectId' });
        }
      },
      { once: true },
    );
    request.addEventListener('success', () => resolve(request.result), { once: true });
    request.addEventListener(
      'error',
      () => reject(request.error ?? new Error('Unable to open project storage.')),
      { once: true },
    );
  });
}

function requireValidSnapshot(value: unknown, label: string): WorkspaceSnapshotV1 {
  if (!isWorkspaceSnapshotV1(value)) {
    throw new WorkspacePersistenceError(
      `${label} is missing, corrupt, or uses an unsupported schema version.`,
    );
  }
  return value;
}

function schemaVersionOf(value: unknown): unknown {
  return value !== null && typeof value === 'object' && 'schemaVersion' in value
    ? value.schemaVersion
    : undefined;
}

/** Explicit migration boundary. V1 passes through; unknown versions fail closed. */
export function migrateWorkspaceSnapshot(value: unknown): WorkspaceSnapshotV1 {
  const schemaVersion = schemaVersionOf(value);
  if (schemaVersion !== WORKSPACE_SCHEMA_VERSION) {
    throw new WorkspaceSchemaVersionError(schemaVersion);
  }
  return requireValidSnapshot(value, 'Project snapshot');
}

function normalizePendingRecord(record: WorkspaceSnapshotV1['members'][number]['result']) {
  if (record?.lifecycle !== 'pending') return record;
  return {
    ...record,
    lifecycle: 'not_evaluated' as const,
    runId: null,
    calculationIdentity: null,
    libraryVersion: null,
    decision: null,
    supportStatus: 'HELD' as const,
    data: null,
    error: null,
    settledAt: null,
  };
}

/** Convert transient in-memory state into truth that is safe to resume. */
export function normalizeWorkspaceSnapshotForPersistence(
  snapshot: WorkspaceSnapshotV1,
  savedAt = snapshot.updatedAt,
): WorkspaceSnapshotV1 {
  const validSnapshot = migrateWorkspaceSnapshot(snapshot);
  const normalized: WorkspaceSnapshotV1 = {
    ...validSnapshot,
    members: validSnapshot.members.map((member) => ({
      ...member,
      inputs: structuredClone(member.inputs),
      result: normalizePendingRecord(member.result),
      geometry: normalizePendingRecord(member.geometry),
      alternatives: normalizePendingRecord(member.alternatives),
      metrics: normalizePendingRecord(member.metrics),
    })),
    dirty: false,
    saveState: 'clean',
    savedAt,
  };
  return requireValidSnapshot(normalized, 'Normalized project snapshot');
}

function tryMigrateSnapshot(value: unknown): WorkspaceSnapshotV1 | null {
  try {
    return migrateWorkspaceSnapshot(value);
  } catch {
    return null;
  }
}

function existingCurrentOrRecovery(
  projectId: string,
  record: PersistedWorkspaceRecord | undefined,
): WorkspaceSnapshotV1 | null {
  if (!record) return null;
  const current = tryMigrateSnapshot(record.current);
  if (current) return current;
  if (tryMigrateSnapshot(record.lastKnownGood)) {
    throw new WorkspaceRecoveryRequiredError(projectId);
  }
  throw new WorkspacePersistenceError(
    'The saved project and its last-known-good snapshot are unreadable.',
  );
}

function assertNoRevisionConflict(
  incoming: WorkspaceSnapshotV1,
  existing: WorkspaceSnapshotV1 | null,
  options: WorkspaceSaveOptions,
): void {
  if ('expectedProjectRevision' in options) {
    const actualRevision = existing?.projectRevision ?? null;
    if (options.expectedProjectRevision !== actualRevision) {
      throw new WorkspaceConflictError(
        incoming.projectId,
        options.expectedProjectRevision,
        actualRevision,
      );
    }
    return;
  }
  if (
    existing
    && (
      existing.projectRevision > incoming.projectRevision
      || (
        existing.projectRevision === incoming.projectRevision
        && existing.updatedAt > incoming.updatedAt
      )
    )
  ) {
    throw new WorkspaceConflictError(
      incoming.projectId,
      undefined,
      existing.projectRevision,
    );
  }
}

export function createIndexedDbWorkspacePersistence(
  suppliedFactory?: IDBFactory,
): WorkspacePersistence {
  const factory = suppliedFactory ?? globalThis.indexedDB;
  if (!factory) {
    throw new WorkspacePersistenceError(
      'IndexedDB is unavailable. Export the project snapshot before leaving this page.',
    );
  }

  const databasePromise = openDatabase(factory).catch((error: unknown) => {
    throw new WorkspacePersistenceError('Unable to initialize project storage.', {
      cause: error,
    });
  });

  return {
    async save(snapshot, options = {}) {
      try {
        const validSnapshot = normalizeWorkspaceSnapshotForPersistence(
          snapshot,
          options.savedAt ?? snapshot.updatedAt,
        );
        const database = await databasePromise;
        const transaction = database.transaction(PROJECT_STORE, 'readwrite');
        const completed = trackedTransactionCompletion(transaction);
        const store = transaction.objectStore(PROJECT_STORE);
        const existing = await requestResult(
          store.get(validSnapshot.projectId) as IDBRequest<PersistedWorkspaceRecord | undefined>,
        );
        const existingCurrent = existingCurrentOrRecovery(validSnapshot.projectId, existing);
        assertNoRevisionConflict(validSnapshot, existingCurrent, options);
        const priorGood = existingCurrent
          ?? tryMigrateSnapshot(existing?.lastKnownGood)
          ?? validSnapshot;
        const record: PersistedWorkspaceRecord = {
          projectId: validSnapshot.projectId,
          current: validSnapshot,
          lastKnownGood: priorGood,
          updatedAt: validSnapshot.updatedAt,
        };
        await requestResult(store.put(record));
        await completed;
      } catch (error) {
        if (error instanceof WorkspacePersistenceError) throw error;
        throw new WorkspacePersistenceError(
          'Project save failed. The previous last-known-good snapshot was retained.',
          { cause: error },
        );
      }
    },

    async load(projectId) {
      const database = await databasePromise;
      const transaction = database.transaction(PROJECT_STORE, 'readonly');
      const completed = trackedTransactionCompletion(transaction);
      const request = transaction.objectStore(PROJECT_STORE).get(projectId);
      const record = await requestResult(
        request as IDBRequest<PersistedWorkspaceRecord | undefined>,
      );
      await completed;
      if (!record) return null;
      return existingCurrentOrRecovery(projectId, record);
    },

    async loadLastKnownGood(projectId) {
      const database = await databasePromise;
      const transaction = database.transaction(PROJECT_STORE, 'readonly');
      const completed = trackedTransactionCompletion(transaction);
      const request = transaction.objectStore(PROJECT_STORE).get(projectId);
      const record = await requestResult(
        request as IDBRequest<PersistedWorkspaceRecord | undefined>,
      );
      await completed;
      if (!record) return null;
      return migrateWorkspaceSnapshot(record.lastKnownGood);
    },

    async recoverLastKnownGood(projectId) {
      try {
        const database = await databasePromise;
        const transaction = database.transaction(PROJECT_STORE, 'readwrite');
        const completed = trackedTransactionCompletion(transaction);
        const store = transaction.objectStore(PROJECT_STORE);
        const record = await requestResult(
          store.get(projectId) as IDBRequest<PersistedWorkspaceRecord | undefined>,
        );
        if (!record) {
          throw new WorkspacePersistenceError('No saved project exists to recover.');
        }
        if (tryMigrateSnapshot(record.current)) {
          throw new WorkspacePersistenceError(
            'The current project is valid and does not require recovery.',
          );
        }
        const recovered = normalizeWorkspaceSnapshotForPersistence(
          migrateWorkspaceSnapshot(record.lastKnownGood),
        );
        const recoveredRecord: PersistedWorkspaceRecord = {
          projectId,
          current: recovered,
          lastKnownGood: recovered,
          updatedAt: recovered.updatedAt,
        };
        await requestResult(store.put(recoveredRecord));
        await completed;
        return recovered;
      } catch (error) {
        if (error instanceof WorkspacePersistenceError) throw error;
        throw new WorkspacePersistenceError('Project recovery failed.', { cause: error });
      }
    },

    async list() {
      const database = await databasePromise;
      const transaction = database.transaction(PROJECT_STORE, 'readonly');
      const completed = trackedTransactionCompletion(transaction);
      const records = await requestResult(
        transaction.objectStore(PROJECT_STORE).getAll() as IDBRequest<
          PersistedWorkspaceRecord[]
        >,
      );
      await completed;
      return records
        .map((record) => tryMigrateSnapshot(record.current))
        .filter((current): current is WorkspaceSnapshotV1 => current !== null)
        .map((current) => ({
          projectId: current.projectId,
          projectName: current.projectName,
          selectedStage: current.selectedStage,
          projectRevision: current.projectRevision,
          updatedAt: current.updatedAt,
          saveState: current.saveState,
        }))
        .sort((left, right) => right.updatedAt.localeCompare(left.updatedAt));
    },

    async delete(projectId) {
      try {
        const database = await databasePromise;
        const transaction = database.transaction(PROJECT_STORE, 'readwrite');
        const completed = trackedTransactionCompletion(transaction);
        const store = transaction.objectStore(PROJECT_STORE);
        const existing = await requestResult(store.get(projectId));
        if (existing === undefined) {
          await completed;
          return false;
        }
        await requestResult(store.delete(projectId));
        await completed;
        return true;
      } catch (error) {
        if (error instanceof WorkspacePersistenceError) throw error;
        throw new WorkspacePersistenceError('Project delete failed.', { cause: error });
      }
    },

    async clear() {
      try {
        const database = await databasePromise;
        const transaction = database.transaction(PROJECT_STORE, 'readwrite');
        const completed = trackedTransactionCompletion(transaction);
        await requestResult(transaction.objectStore(PROJECT_STORE).clear());
        await completed;
      } catch (error) {
        if (error instanceof WorkspacePersistenceError) throw error;
        throw new WorkspacePersistenceError('Project storage clear failed.', { cause: error });
      }
    },
  };
}

export function serializeWorkspaceSnapshot(snapshot: WorkspaceSnapshotV1): string {
  return JSON.stringify(normalizeWorkspaceSnapshotForPersistence(snapshot));
}

export function parseWorkspaceSnapshot(serialized: string): WorkspaceSnapshotV1 {
  let parsed: unknown;
  try {
    parsed = JSON.parse(serialized);
  } catch (error) {
    throw new WorkspacePersistenceError('Project snapshot is not valid JSON.', {
      cause: error,
    });
  }
  return normalizeWorkspaceSnapshotForPersistence(migrateWorkspaceSnapshot(parsed));
}
