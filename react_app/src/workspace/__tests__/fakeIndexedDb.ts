type Listener = () => void;

class FakeEventTarget {
  private readonly listeners = new Map<string, Set<Listener>>();

  addEventListener(type: string, listener: EventListenerOrEventListenerObject): void {
    const callback = typeof listener === 'function'
      ? () => listener(new Event(type))
      : () => listener.handleEvent(new Event(type));
    const listeners = this.listeners.get(type) ?? new Set<Listener>();
    listeners.add(callback);
    this.listeners.set(type, listeners);
  }

  protected emit(type: string): void {
    for (const listener of this.listeners.get(type) ?? []) listener();
  }
}

class FakeRequest<T> extends FakeEventTarget {
  result!: T;
  error: DOMException | null = null;

  succeed(result: T): void {
    this.result = result;
    this.emit('success');
  }

  fail(error: DOMException): void {
    this.error = error;
    this.emit('error');
  }
}

class FakeTransaction extends FakeEventTarget {
  error: DOMException | null = null;
  private pending = 0;
  private completionScheduled = false;
  readonly store: FakeObjectStore;

  constructor(
    records: Map<string, unknown>,
    shouldFailWrite: () => DOMException | null,
  ) {
    super();
    this.store = new FakeObjectStore(this, records, shouldFailWrite);
  }

  objectStore(): IDBObjectStore {
    return this.store as unknown as IDBObjectStore;
  }

  run<T>(operation: () => T): IDBRequest<T> {
    this.pending += 1;
    const request = new FakeRequest<T>();
    queueMicrotask(() => {
      try {
        request.succeed(operation());
      } catch (error) {
        this.error = error instanceof DOMException
          ? error
          : new DOMException('IndexedDB operation failed.', 'UnknownError');
        request.fail(this.error);
        this.emit('error');
        this.emit('abort');
      } finally {
        this.pending -= 1;
        this.scheduleCompletion();
      }
    });
    return request as unknown as IDBRequest<T>;
  }

  abort(): void {
    this.error = new DOMException('Transaction aborted.', 'AbortError');
    this.emit('abort');
  }

  private scheduleCompletion(): void {
    if (this.completionScheduled || this.error) return;
    this.completionScheduled = true;
    setTimeout(() => {
      this.completionScheduled = false;
      if (this.pending === 0 && !this.error) this.emit('complete');
    }, 0);
  }
}

class FakeObjectStore {
  private readonly transaction: FakeTransaction;
  private readonly records: Map<string, unknown>;
  private readonly shouldFailWrite: () => DOMException | null;

  constructor(
    transaction: FakeTransaction,
    records: Map<string, unknown>,
    shouldFailWrite: () => DOMException | null,
  ) {
    this.transaction = transaction;
    this.records = records;
    this.shouldFailWrite = shouldFailWrite;
  }

  get(key: IDBValidKey): IDBRequest<unknown> {
    return this.transaction.run(() => this.records.get(String(key)));
  }

  getAll(): IDBRequest<unknown[]> {
    return this.transaction.run(() => [...this.records.values()]);
  }

  put(value: unknown): IDBRequest<IDBValidKey> {
    return this.transaction.run<IDBValidKey>(() => {
      const failure = this.shouldFailWrite();
      if (failure) throw failure;
      const projectId = (value as { projectId?: unknown }).projectId;
      if (typeof projectId !== 'string') {
        throw new DOMException('Missing projectId key.', 'DataError');
      }
      this.records.set(projectId, structuredClone(value));
      return projectId;
    });
  }

  delete(key: IDBValidKey): IDBRequest<undefined> {
    return this.transaction.run(() => {
      const failure = this.shouldFailWrite();
      if (failure) throw failure;
      this.records.delete(String(key));
      return undefined;
    });
  }

  clear(): IDBRequest<undefined> {
    return this.transaction.run(() => {
      const failure = this.shouldFailWrite();
      if (failure) throw failure;
      this.records.clear();
      return undefined;
    });
  }
}

class FakeDatabase {
  private readonly records = new Map<string, unknown>();
  private hasProjectStore = false;
  private readonly shouldFailWrite: () => DOMException | null;

  constructor(shouldFailWrite: () => DOMException | null) {
    this.shouldFailWrite = shouldFailWrite;
  }

  readonly objectStoreNames = {
    contains: (name: string) => name === 'projects' && this.hasProjectStore,
  };

  createObjectStore(name: string): IDBObjectStore {
    if (name !== 'projects') throw new DOMException('Unknown store.', 'NotFoundError');
    this.hasProjectStore = true;
    return {} as IDBObjectStore;
  }

  transaction(name: string): IDBTransaction {
    if (name !== 'projects' || !this.hasProjectStore) {
      throw new DOMException('Unknown store.', 'NotFoundError');
    }
    return new FakeTransaction(this.records, this.shouldFailWrite) as unknown as IDBTransaction;
  }

  seed(projectId: string, value: unknown): void {
    this.records.set(projectId, structuredClone(value));
  }

  read(projectId: string): unknown {
    return structuredClone(this.records.get(projectId));
  }
}

class FakeOpenRequest extends FakeRequest<IDBDatabase> {
  emitForUpgrade(): void {
    this.emit('upgradeneeded');
  }
}

export class FakeIndexedDbFactory {
  private failure: DOMException | null = null;
  private readonly database = new FakeDatabase(() => {
    const failure = this.failure;
    this.failure = null;
    return failure;
  });

  open(): IDBOpenDBRequest {
    const request = new FakeOpenRequest();
    queueMicrotask(() => {
      request.result = this.database as unknown as IDBDatabase;
      request.emitForUpgrade();
      request.succeed(this.database as unknown as IDBDatabase);
    });
    return request as unknown as IDBOpenDBRequest;
  }

  failNextWrite(name: string = 'QuotaExceededError'): void {
    this.failure = new DOMException('Synthetic storage failure.', name);
  }

  seed(projectId: string, value: unknown): void {
    this.database.seed(projectId, value);
  }

  read(projectId: string): unknown {
    return this.database.read(projectId);
  }
}
