import { describe, expect, it } from 'vitest';
import { FakeIndexedDbFactory } from './fakeIndexedDb';
import {
  createIndexedDbWorkspacePersistence,
  migrateWorkspaceSnapshot,
  parseWorkspaceSnapshot,
  serializeWorkspaceSnapshot,
  WorkspaceConflictError,
  WorkspacePersistenceError,
  WorkspaceRecoveryRequiredError,
  WorkspaceSchemaVersionError,
} from '../persistence';
import {
  WORKSPACE_SCHEMA_VERSION,
  type EvidenceRecord,
  type PersistedWorkspaceRecord,
  type WorkspaceSnapshotV1,
} from '../types';

function makeSnapshot(
  projectRevision = 1,
  overrides: Partial<WorkspaceSnapshotV1> = {},
): WorkspaceSnapshotV1 {
  return {
    schemaVersion: WORKSPACE_SCHEMA_VERSION,
    projectId: 'project-1',
    projectName: 'Project 1',
    projectRevision,
    members: [],
    selectedStage: 'import',
    selectedMemberId: null,
    selectedFloor: null,
    dirty: true,
    saveState: 'dirty',
    createdAt: '2026-08-10T00:00:00.000Z',
    updatedAt: `2026-08-10T00:0${projectRevision}:00.000Z`,
    savedAt: null,
    migrationOrigin: null,
    ...overrides,
  };
}

function persistenceWithFactory() {
  const factory = new FakeIndexedDbFactory();
  return {
    factory,
    persistence: createIndexedDbWorkspacePersistence(factory as unknown as IDBFactory),
  };
}

function pendingResult(projectRevision: number): EvidenceRecord {
  return {
    projectId: 'project-1',
    memberId: 'ETABS-101',
    inputHash: 'hash-1',
    inputRevision: 1,
    memberRevision: 1,
    projectRevision,
    lifecycle: 'pending',
    requestId: 'request-1',
    runId: null,
    calculationIdentity: null,
    libraryVersion: null,
    decision: null,
    supportStatus: 'HELD',
    data: null,
    error: null,
    createdAt: '2026-08-10T00:01:30.000Z',
    settledAt: null,
  };
}

describe('portable workspace persistence contract', () => {
  it('passes through V1 and round-trips a valid versioned snapshot', () => {
    const snapshot = makeSnapshot();
    expect(migrateWorkspaceSnapshot(snapshot)).toBe(snapshot);
    expect(parseWorkspaceSnapshot(serializeWorkspaceSnapshot(snapshot))).toEqual({
      ...snapshot,
      dirty: false,
      saveState: 'clean',
      savedAt: snapshot.updatedAt,
    });
  });

  it('fails closed on unknown schemas and malformed members', () => {
    expect(() => parseWorkspaceSnapshot(JSON.stringify({
      ...makeSnapshot(),
      schemaVersion: 2,
    }))).toThrow(WorkspaceSchemaVersionError);

    expect(() => parseWorkspaceSnapshot(JSON.stringify({
      ...makeSnapshot(),
      members: [{ memberId: 'beam-1' }],
    }))).toThrow(WorkspacePersistenceError);
  });

  it('reports invalid JSON without returning a partial project', () => {
    expect(() => parseWorkspaceSnapshot('{not-json')).toThrow(/not valid JSON/i);
  });

  it('rejects non-stale evidence bound to another project revision', () => {
    const projectRevision = 2;
    const record = { ...pendingResult(projectRevision), lifecycle: 'not_evaluated' as const };
    const snapshot = makeSnapshot(projectRevision, {
      members: [{
        memberId: 'ETABS-101', sourceId: 'ETABS-101', label: 'B1', story: 'GF',
        frameType: 'beam', inputHash: 'hash-1', inputRevision: 1, memberRevision: 1,
        inputs: { widthMm: 300 }, result: { ...record, projectRevision: 1 },
        geometry: null, alternatives: null, metrics: null,
      }],
    });

    expect(() => migrateWorkspaceSnapshot(snapshot)).toThrow(WorkspacePersistenceError);
  });
});

describe('IndexedDB workspace persistence', () => {
  it('saves and loads through the transaction path', async () => {
    const { persistence } = persistenceWithFactory();
    await persistence.save(makeSnapshot(), {
      expectedProjectRevision: null,
      savedAt: '2026-08-10T00:02:00.000Z',
    });

    await expect(persistence.load('project-1')).resolves.toMatchObject({
      projectRevision: 1,
      dirty: false,
      saveState: 'clean',
      savedAt: '2026-08-10T00:02:00.000Z',
    });
  });

  it('normalizes pending evidence so reload cannot resume it as active truth', async () => {
    const { persistence } = persistenceWithFactory();
    const projectRevision = 2;
    const snapshot = makeSnapshot(projectRevision, {
      members: [{
        memberId: 'ETABS-101',
        sourceId: 'ETABS-101',
        label: 'B1',
        story: 'GF',
        frameType: 'beam',
        inputHash: 'hash-1',
        inputRevision: 1,
        memberRevision: 1,
        inputs: { widthMm: 300 },
        result: pendingResult(projectRevision),
        geometry: null,
        alternatives: null,
        metrics: null,
      }],
      selectedMemberId: 'ETABS-101',
    });

    await persistence.save(snapshot, { expectedProjectRevision: null });
    const loaded = await persistence.load('project-1');

    expect(loaded?.members[0].result).toMatchObject({
      lifecycle: 'not_evaluated',
      supportStatus: 'HELD',
      data: null,
      settledAt: null,
    });
    expect(snapshot.members[0].result?.lifecycle).toBe('pending');
  });

  it('retains last-known-good and requires explicit recovery from corrupt current data', async () => {
    const { factory, persistence } = persistenceWithFactory();
    await persistence.save(makeSnapshot(1), { expectedProjectRevision: null });
    await persistence.save(makeSnapshot(2), { expectedProjectRevision: 1 });

    const record = factory.read('project-1') as PersistedWorkspaceRecord;
    factory.seed('project-1', {
      ...record,
      current: { ...record.current, schemaVersion: 99 },
    });

    await expect(persistence.load('project-1')).rejects.toBeInstanceOf(
      WorkspaceRecoveryRequiredError,
    );
    await expect(persistence.loadLastKnownGood('project-1')).resolves.toMatchObject({
      projectRevision: 1,
    });
    await expect(persistence.recoverLastKnownGood('project-1')).resolves.toMatchObject({
      projectRevision: 1,
    });
    await expect(persistence.load('project-1')).resolves.toMatchObject({
      projectRevision: 1,
    });
  });

  it('rejects revision conflicts without overwriting the newer record', async () => {
    const { persistence } = persistenceWithFactory();
    await persistence.save(makeSnapshot(1), { expectedProjectRevision: null });
    await persistence.save(makeSnapshot(2), { expectedProjectRevision: 1 });

    await expect(
      persistence.save(makeSnapshot(3), { expectedProjectRevision: 1 }),
    ).rejects.toBeInstanceOf(WorkspaceConflictError);
    await expect(persistence.load('project-1')).resolves.toMatchObject({
      projectRevision: 2,
    });
  });

  it('surfaces quota failures and preserves the prior durable snapshot', async () => {
    const { factory, persistence } = persistenceWithFactory();
    await persistence.save(makeSnapshot(1), { expectedProjectRevision: null });
    factory.failNextWrite();

    await expect(
      persistence.save(makeSnapshot(2), { expectedProjectRevision: 1 }),
    ).rejects.toThrow(/previous last-known-good snapshot was retained/i);
    await expect(persistence.load('project-1')).resolves.toMatchObject({
      projectRevision: 1,
    });
  });

  it('deletes one project and explicitly clears all projects', async () => {
    const { persistence } = persistenceWithFactory();
    await persistence.save(makeSnapshot(1), { expectedProjectRevision: null });
    await persistence.save(makeSnapshot(1, {
      projectId: 'project-2',
      projectName: 'Project 2',
    }), { expectedProjectRevision: null });

    await expect(persistence.delete('project-1')).resolves.toBe(true);
    await expect(persistence.delete('project-1')).resolves.toBe(false);
    await expect(persistence.load('project-2')).resolves.not.toBeNull();

    await persistence.clear();
    await expect(persistence.list()).resolves.toEqual([]);
  });
});
