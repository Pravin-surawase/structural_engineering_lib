import {
  isWorkspaceSnapshotV1,
  type PersistedWorkspaceRecord,
  type WorkspaceProjectSummary,
  type WorkspaceSnapshotV1,
} from './types';

const DATABASE_NAME = 'structlib-workbench';
const DATABASE_VERSION = 1;
const PROJECT_STORE = 'projects';

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

export interface WorkspacePersistence {
  save(snapshot: WorkspaceSnapshotV1): Promise<void>;
  load(projectId: string): Promise<WorkspaceSnapshotV1 | null>;
  loadLastKnownGood(projectId: string): Promise<WorkspaceSnapshotV1 | null>;
  list(): Promise<WorkspaceProjectSummary[]>;
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

function requireValidSnapshot(
  value: unknown,
  label: string,
): WorkspaceSnapshotV1 {
  if (!isWorkspaceSnapshotV1(value)) {
    throw new WorkspacePersistenceError(
      `${label} is missing, corrupt, or uses an unsupported schema version.`,
    );
  }
  return value;
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
    async save(snapshot) {
      try {
        const validSnapshot = requireValidSnapshot(snapshot, 'Project snapshot');
        const database = await databasePromise;
        const transaction = database.transaction(PROJECT_STORE, 'readwrite');
        const store = transaction.objectStore(PROJECT_STORE);
        const existing = await requestResult(
          store.get(validSnapshot.projectId) as IDBRequest<PersistedWorkspaceRecord | undefined>,
        );
        const record: PersistedWorkspaceRecord = {
          projectId: validSnapshot.projectId,
          current: validSnapshot,
          lastKnownGood: existing?.current && isWorkspaceSnapshotV1(existing.current)
            ? existing.current
            : validSnapshot,
          updatedAt: validSnapshot.updatedAt,
        };
        store.put(record);
        await transactionComplete(transaction);
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
      const request = transaction.objectStore(PROJECT_STORE).get(projectId);
      const record = await requestResult(
        request as IDBRequest<PersistedWorkspaceRecord | undefined>,
      );
      await transactionComplete(transaction);
      if (!record) return null;
      if (isWorkspaceSnapshotV1(record.current)) return record.current;
      if (isWorkspaceSnapshotV1(record.lastKnownGood)) {
        throw new WorkspaceRecoveryRequiredError(projectId);
      }
      throw new WorkspacePersistenceError(
        'The saved project and its last-known-good snapshot are unreadable.',
      );
    },

    async loadLastKnownGood(projectId) {
      const database = await databasePromise;
      const transaction = database.transaction(PROJECT_STORE, 'readonly');
      const request = transaction.objectStore(PROJECT_STORE).get(projectId);
      const record = await requestResult(
        request as IDBRequest<PersistedWorkspaceRecord | undefined>,
      );
      await transactionComplete(transaction);
      if (!record) return null;
      return requireValidSnapshot(record.lastKnownGood, 'Last-known-good snapshot');
    },

    async list() {
      const database = await databasePromise;
      const transaction = database.transaction(PROJECT_STORE, 'readonly');
      const records = await requestResult(
        transaction.objectStore(PROJECT_STORE).getAll() as IDBRequest<
          PersistedWorkspaceRecord[]
        >,
      );
      await transactionComplete(transaction);
      return records
        .filter((record) => isWorkspaceSnapshotV1(record.current))
        .map(({ current }) => ({
          projectId: current.projectId,
          projectName: current.projectName,
          selectedStage: current.selectedStage,
          projectRevision: current.projectRevision,
          updatedAt: current.updatedAt,
          saveState: current.saveState,
        }))
        .sort((left, right) => right.updatedAt.localeCompare(left.updatedAt));
    },
  };
}

export function serializeWorkspaceSnapshot(snapshot: WorkspaceSnapshotV1): string {
  return JSON.stringify(requireValidSnapshot(snapshot, 'Project snapshot'));
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
  return requireValidSnapshot(parsed, 'Project snapshot');
}
