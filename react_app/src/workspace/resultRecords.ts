import type { BatchResult, CheckedWorkbenchLayout } from '../hooks/useBatchDesign';
import { batchGoverningUtilization } from '../api/client';
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

function unsupportedIdentityRecord(
  pending: EvidenceRecord,
  runId: string,
  code: string,
  message: string,
  settledAt?: string,
): EvidenceRecord {
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
      error: { code, message },
    },
    settledAt,
  );
}

export function completedBatchRecord(
  pending: EvidenceRecord,
  result: BatchResult,
  runId: string,
  settledAt?: string,
): EvidenceRecord {
  const evidence = result.evidence;
  if (!evidence) {
    return unsupportedIdentityRecord(
      pending,
      runId,
      'EVIDENCE_MISSING',
      'The batch result did not include a traceable evidence identity.',
      settledAt,
    );
  }
  const envelope = result.result_envelope;
  const identity = envelope?.result_identity;
  if (!envelope || !identity) {
    return unsupportedIdentityRecord(
      pending,
      runId,
      'RESULT_ENVELOPE_MISSING',
      'The batch result did not include its canonical result identity.',
      settledAt,
    );
  }
  if (
    envelope.overall_status !== result.status
    || envelope.overall_status !== evidence.status
  ) {
    return unsupportedIdentityRecord(
      pending,
      runId,
      'RESULT_STATUS_MISMATCH',
      'The batch status and canonical result envelope do not agree.',
      settledAt,
    );
  }
  if (
    identity.contract_version !== 'canonical-beam-result/v1'
    || identity.input_hash !== evidence.normalized_input_hash
    || identity.calculation_identity !== evidence.calculation_identity
    || identity.library_version !== evidence.library_version
  ) {
    return unsupportedIdentityRecord(
      pending,
      runId,
      'RESULT_IDENTITY_MISMATCH',
      'The result envelope and evidence identity do not agree.',
      settledAt,
    );
  }

  return settledRecord(
    pending,
    {
      lifecycle: evidence.support_status === 'SUPPORTED' ? 'current' : 'unsupported',
      runId,
      calculationIdentity: identity.calculation_identity,
      libraryVersion: identity.library_version,
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

export function currentWorkbenchLayout(
  snapshot: WorkspaceSnapshotV1 | null,
  memberId: string,
): CheckedWorkbenchLayout | null {
  const member = snapshot?.members.find((item) => item.memberId === memberId);
  if (!snapshot || !member || !recordCanExport(member.result, memberIdentity(snapshot, member))) {
    return null;
  }
  const layout = currentBatchResult(snapshot, memberId)?.workbench;
  return layout?.status === 'PASS'
    && layout.checked_request?.identity?.member_id === memberId
    && /^[a-f0-9]{64}$/.test(layout.checked_layout_id)
    ? layout
    : null;
}

export function applyBatchResultToBeam(
  beam: BeamCSVRow,
  result: BatchResult,
): BeamCSVRow {
  const checked = result.workbench?.status === 'PASS' ? result.workbench : undefined;
  const mid = checked?.zones.find((zone) => zone.zone === 'mid');
  const designPassed = result.design_succeeded && result.is_safe && result.status === 'PASS';
  const held = result.workbench?.status === 'HOLD';
  return {
    ...beam,
    ast_required: checked?.ast_required_mm2 ?? result.flexure?.ast_required ?? 0,
    asc_required: checked?.asc_required_mm2 ?? result.flexure?.asc_required ?? 0,
    stirrup_spacing: mid?.stirrup.spacing_mm,
    stirrup_diameter: mid?.stirrup.diameter_mm,
    bar_count: mid?.tension.count,
    bar_diameter: mid?.tension.diameter_mm,
    ast_provided: mid?.tension.area_mm2,
    utilization: checked?.utilization ?? batchGoverningUtilization(result) ?? undefined,
    is_valid: designPassed && !held,
    status: held ? 'warning' : designPassed ? 'pass' : 'fail',
    remarks: result.workbench?.status === 'HOLD' ? [result.workbench.reason]
      : result.error ? [result.error] : result.failed_checks,
  };
}
