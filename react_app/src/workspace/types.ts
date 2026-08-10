import type { ProjectStage } from '../app/navigation';

export const WORKSPACE_SCHEMA_VERSION = 1 as const;

export type JsonPrimitive = string | number | boolean | null;
export type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue };

export type ResultLifecycle =
  | 'current'
  | 'stale'
  | 'pending'
  | 'error'
  | 'unsupported'
  | 'not_evaluated';

export type EvidenceDecision = 'PASS' | 'FAIL' | 'HOLD';
export type SupportStatus = 'SUPPORTED' | 'HELD';
export type SaveState = 'clean' | 'dirty' | 'saving' | 'error';

export interface RevisionIdentity {
  projectId: string;
  memberId: string;
  inputHash: string;
  inputRevision: number;
  memberRevision: number;
  projectRevision: number;
}

export interface RecordError {
  code: string;
  message: string;
}

export interface EvidenceRecord<TData extends JsonValue = JsonValue>
  extends RevisionIdentity {
  lifecycle: ResultLifecycle;
  requestId: string;
  runId: string | null;
  calculationIdentity: string | null;
  libraryVersion: string | null;
  decision: EvidenceDecision | null;
  supportStatus: SupportStatus;
  data: TData | null;
  error: RecordError | null;
  createdAt: string;
  settledAt: string | null;
}

export interface WorkspaceMember {
  memberId: string;
  sourceId: string;
  label: string;
  story: string | null;
  frameType: string;
  inputHash: string;
  inputRevision: number;
  memberRevision: number;
  inputs: { [key: string]: JsonValue };
  result: EvidenceRecord | null;
  geometry: EvidenceRecord | null;
  alternatives: EvidenceRecord | null;
  metrics: EvidenceRecord | null;
}

export interface WorkspaceSnapshotV1 {
  schemaVersion: typeof WORKSPACE_SCHEMA_VERSION;
  projectId: string;
  projectName: string;
  projectRevision: number;
  members: WorkspaceMember[];
  selectedStage: ProjectStage;
  selectedMemberId: string | null;
  selectedFloor: string | null;
  dirty: boolean;
  saveState: SaveState;
  createdAt: string;
  updatedAt: string;
  savedAt: string | null;
  migrationOrigin: string | null;
}

export interface PersistedWorkspaceRecord {
  projectId: string;
  current: WorkspaceSnapshotV1;
  lastKnownGood: WorkspaceSnapshotV1;
  updatedAt: string;
}

export interface WorkspaceProjectSummary {
  projectId: string;
  projectName: string;
  selectedStage: ProjectStage;
  projectRevision: number;
  updatedAt: string;
  saveState: SaveState;
}

const PROJECT_STAGES = new Set<ProjectStage>(['import', 'review', 'design', 'results']);
const SAVE_STATES = new Set<SaveState>(['clean', 'dirty', 'saving', 'error']);
const LIFECYCLES = new Set<ResultLifecycle>([
  'current',
  'stale',
  'pending',
  'error',
  'unsupported',
  'not_evaluated',
]);

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function isJsonValue(value: unknown): value is JsonValue {
  if (
    value === null
    || typeof value === 'string'
    || typeof value === 'boolean'
    || (typeof value === 'number' && Number.isFinite(value))
  ) {
    return true;
  }
  if (Array.isArray(value)) return value.every(isJsonValue);
  return isRecord(value) && Object.values(value).every(isJsonValue);
}

function isPositiveRevision(value: unknown): value is number {
  return Number.isInteger(value) && Number(value) > 0;
}

function isEvidenceRecord(value: unknown): value is EvidenceRecord {
  if (!isRecord(value)) return false;
  const error = value.error;
  return (
    typeof value.projectId === 'string'
    && value.projectId.length > 0
    && typeof value.memberId === 'string'
    && value.memberId.length > 0
    && typeof value.inputHash === 'string'
    && value.inputHash.length > 0
    && isPositiveRevision(value.inputRevision)
    && isPositiveRevision(value.memberRevision)
    && isPositiveRevision(value.projectRevision)
    && typeof value.lifecycle === 'string'
    && LIFECYCLES.has(value.lifecycle as ResultLifecycle)
    && typeof value.requestId === 'string'
    && value.requestId.length > 0
    && (value.runId === null || typeof value.runId === 'string')
    && (value.calculationIdentity === null || typeof value.calculationIdentity === 'string')
    && (value.libraryVersion === null || typeof value.libraryVersion === 'string')
    && (value.decision === null || value.decision === 'PASS' || value.decision === 'FAIL' || value.decision === 'HOLD')
    && (value.supportStatus === 'SUPPORTED' || value.supportStatus === 'HELD')
    && (value.data === null || isJsonValue(value.data))
    && (
      error === null
      || (
        isRecord(error)
        && typeof error.code === 'string'
        && typeof error.message === 'string'
      )
    )
    && typeof value.createdAt === 'string'
    && (value.settledAt === null || typeof value.settledAt === 'string')
  );
}

function isWorkspaceMember(value: unknown): value is WorkspaceMember {
  if (!isRecord(value)) return false;
  return (
    typeof value.memberId === 'string'
    && value.memberId.length > 0
    && typeof value.sourceId === 'string'
    && value.sourceId.length > 0
    && typeof value.label === 'string'
    && value.label.length > 0
    && (value.story === null || typeof value.story === 'string')
    && typeof value.frameType === 'string'
    && value.frameType.length > 0
    && typeof value.inputHash === 'string'
    && value.inputHash.length > 0
    && isPositiveRevision(value.inputRevision)
    && isPositiveRevision(value.memberRevision)
    && isJsonValue(value.inputs)
    && isRecord(value.inputs)
    && ['result', 'geometry', 'alternatives', 'metrics'].every((key) => (
      value[key] === null || isEvidenceRecord(value[key])
    ))
  );
}

function nonStaleRecordMatchesMember(
  record: EvidenceRecord | null,
  projectId: string,
  projectRevision: number,
  member: WorkspaceMember,
): boolean {
  if (!record || record.lifecycle === 'stale') return true;
  return (
    record.projectId === projectId
    && record.projectRevision === projectRevision
    && record.memberId === member.memberId
    && record.inputHash === member.inputHash
    && record.inputRevision === member.inputRevision
    && record.memberRevision === member.memberRevision
  );
}

export function isWorkspaceSnapshotV1(value: unknown): value is WorkspaceSnapshotV1 {
  if (!isRecord(value)) return false;
  const candidate = value as Partial<WorkspaceSnapshotV1>;
  const members = candidate.members;
  if (!Array.isArray(members) || !members.every(isWorkspaceMember)) return false;
  const memberIds = members.map((member) => member.memberId);
  const projectId = candidate.projectId;
  const projectRevision = candidate.projectRevision;
  const hasConsistentNonStaleRecords = typeof projectId === 'string'
    && isPositiveRevision(projectRevision)
    && members.every((member) => (
      nonStaleRecordMatchesMember(member.result, projectId, projectRevision, member)
      && nonStaleRecordMatchesMember(member.geometry, projectId, projectRevision, member)
      && nonStaleRecordMatchesMember(member.alternatives, projectId, projectRevision, member)
      && nonStaleRecordMatchesMember(member.metrics, projectId, projectRevision, member)
    ));
  return (
    candidate.schemaVersion === WORKSPACE_SCHEMA_VERSION
    && typeof candidate.projectId === 'string'
    && candidate.projectId.length > 0
    && typeof candidate.projectName === 'string'
    && candidate.projectName.length > 0
    && isPositiveRevision(candidate.projectRevision)
    && new Set(memberIds).size === memberIds.length
    && hasConsistentNonStaleRecords
    && typeof candidate.selectedStage === 'string'
    && PROJECT_STAGES.has(candidate.selectedStage as ProjectStage)
    && (
      candidate.selectedMemberId === null
      || (
        typeof candidate.selectedMemberId === 'string'
        && memberIds.includes(candidate.selectedMemberId)
      )
    )
    && (candidate.selectedFloor === null || typeof candidate.selectedFloor === 'string')
    && typeof candidate.dirty === 'boolean'
    && typeof candidate.saveState === 'string'
    && SAVE_STATES.has(candidate.saveState as SaveState)
    && typeof candidate.createdAt === 'string'
    && typeof candidate.updatedAt === 'string'
    && (candidate.savedAt === null || typeof candidate.savedAt === 'string')
    && (candidate.migrationOrigin === null || typeof candidate.migrationOrigin === 'string')
  );
}
