import type { BatchResult } from '../hooks/useBatchDesign';
import type { BeamCSVRow } from '../types/csv';
import { memberIdentity, recordCanExport } from './identity';
import type {
  EvidenceRecord,
  JsonValue,
  WorkspaceSnapshotV1,
} from './types';

function jsonClone(value: unknown): JsonValue {
  return JSON.parse(JSON.stringify(value)) as JsonValue;
}

function settledRecord(
  pending: EvidenceRecord,
  values: Pick<
    EvidenceRecord,
    | 'lifecycle'
    | 'runId'
    | 'calculationIdentity'
    | 'libraryVersion'
    | 'decision'
    | 'supportStatus'
    | 'data'
    | 'error'
  >,
  settledAt = new Date().toISOString(),
): EvidenceRecord {
  return { ...pending, ...values, settledAt };
}

export function completedBatchRecord(
  pending: EvidenceRecord,
  result: BatchResult,
  runId: string,
  settledAt?: string,
): EvidenceRecord {
  const evidence = result.evidence;
  if (!evidence) {
    return settledRecord(
      pending,
      {
        lifecycle: 'unsupported',
        runId,
        calculationIdentity: null,
        libraryVersion: null,
        decision: 'HOLD',
        supportStatus: 'HELD',
        data: null,
        error: {
          code: 'EVIDENCE_MISSING',
          message: 'The batch result did not include a traceable evidence identity.',
        },
      },
      settledAt,
    );
  }

  return settledRecord(
    pending,
    {
      lifecycle: evidence.support_status === 'SUPPORTED' ? 'current' : 'unsupported',
      runId,
      calculationIdentity: evidence.calculation_identity,
      libraryVersion: evidence.library_version,
      decision: evidence.status,
      supportStatus: evidence.support_status,
      data: jsonClone(result),
      error: null,
    },
    settledAt ?? evidence.generated_at,
  );
}

export function failedBatchRecord(
  pending: EvidenceRecord,
  runId: string,
  code: string,
  message: string,
  lifecycle: 'error' | 'not_evaluated' = 'error',
  settledAt?: string,
): EvidenceRecord {
  return settledRecord(
    pending,
    {
      lifecycle,
      runId,
      calculationIdentity: null,
      libraryVersion: null,
      decision: 'HOLD',
      supportStatus: 'HELD',
      data: null,
      error: { code, message },
    },
    settledAt,
  );
}

export interface ProjectExportReadiness {
  eligible: boolean;
  eligibleCount: number;
  heldMemberIds: string[];
}

export function projectExportReadiness(
  snapshot: WorkspaceSnapshotV1 | null,
  memberIds?: Iterable<string>,
): ProjectExportReadiness {
  if (!snapshot) return { eligible: false, eligibleCount: 0, heldMemberIds: [] };
  const includedIds = memberIds ? new Set(memberIds) : null;
  const members = includedIds
    ? snapshot.members.filter((member) => includedIds.has(member.memberId))
    : snapshot.members;
  const heldMemberIds = members
    .filter((member) => !recordCanExport(member.result, memberIdentity(snapshot, member)))
    .map((member) => member.memberId);
  return {
    eligible: members.length > 0 && heldMemberIds.length === 0,
    eligibleCount: members.length - heldMemberIds.length,
    heldMemberIds,
  };
}

export function currentBatchResult(
  snapshot: WorkspaceSnapshotV1,
  memberId: string,
): BatchResult | null {
  const member = snapshot.members.find((candidate) => candidate.memberId === memberId);
  if (!member || member.result?.lifecycle !== 'current' || member.result.data === null) {
    return null;
  }
  const data = member.result.data;
  if (
    data === null
    || typeof data !== 'object'
    || Array.isArray(data)
    || typeof data.beam_id !== 'string'
    || typeof data.design_succeeded !== 'boolean'
    || typeof data.is_safe !== 'boolean'
    || (data.status !== 'PASS' && data.status !== 'FAIL')
  ) {
    return null;
  }
  return data as unknown as BatchResult;
}

function deriveBarLayout(astRequired: number): { count: number; dia: number } {
  const diameters = [12, 16, 20, 25, 32];
  for (const dia of diameters) {
    const area = Math.PI * dia * dia / 4;
    const count = Math.max(2, Math.ceil(astRequired / area));
    if (count <= 8) return { count, dia };
  }
  return { count: Math.max(2, Math.ceil(astRequired / (Math.PI * 16 * 16))), dia: 32 };
}

export function applyBatchResultToBeam(
  beam: BeamCSVRow,
  result: BatchResult,
): BeamCSVRow {
  const astRequired = result.flexure?.ast_required ?? 0;
  const layout = deriveBarLayout(astRequired);
  const designPassed = result.design_succeeded && result.is_safe && result.status === 'PASS';
  return {
    ...beam,
    ast_required: astRequired,
    asc_required: result.flexure?.asc_required ?? 0,
    stirrup_spacing: result.shear?.stirrup_spacing,
    stirrup_diameter: beam.stirrup_diameter ?? 8,
    bar_count: layout.count,
    bar_diameter: layout.dia,
    ast_provided: layout.count * Math.PI * (layout.dia / 2) ** 2,
    utilization: result.utilization_ratio,
    is_valid: designPassed,
    status: designPassed ? 'pass' : 'fail',
    remarks: result.error ? [result.error] : result.failed_checks,
  };
}
