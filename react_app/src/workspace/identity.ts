import type {
  EvidenceRecord,
  JsonValue,
  RevisionIdentity,
  WorkspaceMember,
  WorkspaceSnapshotV1,
} from './types';

export function recordMatchesIdentity(
  record: EvidenceRecord | null,
  identity: RevisionIdentity,
): boolean {
  return Boolean(
    record
    && record.projectId === identity.projectId
    && record.memberId === identity.memberId
    && record.inputHash === identity.inputHash
    && record.inputRevision === identity.inputRevision
    && record.memberRevision === identity.memberRevision
    && record.projectRevision === identity.projectRevision,
  );
}

export function recordIsCurrent(
  record: EvidenceRecord | null,
  identity: RevisionIdentity,
): boolean {
  return record?.lifecycle === 'current' && recordMatchesIdentity(record, identity);
}

export function recordCanExport(
  record: EvidenceRecord | null,
  identity: RevisionIdentity,
): boolean {
  return Boolean(
    recordIsCurrent(record, identity)
    && record?.decision === 'PASS'
    && record.supportStatus === 'SUPPORTED'
    && record.data !== null
    && record.calculationIdentity !== null
    && record.libraryVersion !== null
    && record.settledAt !== null,
  );
}

export function memberIdentity(
  snapshot: WorkspaceSnapshotV1,
  member: WorkspaceMember,
): RevisionIdentity {
  return {
    projectId: snapshot.projectId,
    memberId: member.memberId,
    inputHash: member.inputHash,
    inputRevision: member.inputRevision,
    memberRevision: member.memberRevision,
    projectRevision: snapshot.projectRevision,
  };
}

export function staleRecord(record: EvidenceRecord | null): EvidenceRecord | null {
  if (!record || record.lifecycle === 'stale') return record;
  return {
    ...record,
    lifecycle: 'stale',
  };
}

export function invalidateMemberRecords(member: WorkspaceMember): WorkspaceMember {
  return {
    ...member,
    result: staleRecord(member.result),
    geometry: staleRecord(member.geometry),
    alternatives: staleRecord(member.alternatives),
    metrics: staleRecord(member.metrics),
  };
}

export function pendingRecord<TData extends JsonValue>(
  identity: RevisionIdentity,
  requestId: string,
  createdAt: string,
): EvidenceRecord<TData> {
  return {
    ...identity,
    lifecycle: 'pending',
    requestId,
    runId: null,
    calculationIdentity: null,
    libraryVersion: null,
    decision: null,
    supportStatus: 'HELD',
    data: null,
    error: null,
    createdAt,
    settledAt: null,
  };
}
