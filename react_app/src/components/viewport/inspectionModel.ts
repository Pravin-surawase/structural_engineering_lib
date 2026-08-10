import { memberIdentity, recordIsCurrent } from '../../workspace/identity';
import type { WorkspaceMember, WorkspaceSnapshotV1 } from '../../workspace/types';

export type ViewportMemberStatus =
  | 'pass'
  | 'fail'
  | 'hold'
  | 'pending'
  | 'stale'
  | 'error'
  | 'not_evaluated';

export interface ViewportMemberInspection {
  memberId: string;
  label: string;
  story: string;
  frameType: string;
  status: ViewportMemberStatus;
  utilization: number | null;
}

export const VIEWPORT_STATUS_STYLE: Record<
  ViewportMemberStatus,
  { label: string; color: string }
> = {
  pass: { label: 'PASS', color: '#22c55e' },
  fail: { label: 'FAIL', color: '#ef4444' },
  hold: { label: 'HOLD / unsupported', color: '#f59e0b' },
  pending: { label: 'Designing', color: '#3b82f6' },
  stale: { label: 'Stale after edit', color: '#a78bfa' },
  error: { label: 'Error', color: '#fb7185' },
  not_evaluated: { label: 'Not evaluated', color: '#94a3b8' },
};

function currentUtilization(member: WorkspaceMember): number | null {
  const data = member.result?.data;
  if (data === null || typeof data !== 'object' || Array.isArray(data)) return null;
  const value = data.utilization_ratio;
  return typeof value === 'number' && Number.isFinite(value) ? value : null;
}

function statusForMember(
  snapshot: WorkspaceSnapshotV1,
  member: WorkspaceMember,
): ViewportMemberStatus {
  const record = member.result;
  if (!record || record.lifecycle === 'not_evaluated') return 'not_evaluated';
  if (record.lifecycle === 'pending') return 'pending';
  if (record.lifecycle === 'stale') return 'stale';
  if (record.lifecycle === 'error') return 'error';
  if (record.lifecycle === 'unsupported' || record.decision === 'HOLD') return 'hold';
  if (!recordIsCurrent(record, memberIdentity(snapshot, member))) return 'stale';
  return record.decision === 'PASS' ? 'pass' : 'fail';
}

export function buildViewportInspection(
  snapshot: WorkspaceSnapshotV1 | null,
): ViewportMemberInspection[] {
  if (!snapshot) return [];
  return snapshot.members.map((member) => {
    const status = statusForMember(snapshot, member);
    return {
      memberId: member.memberId,
      label: member.label,
      story: member.story ?? 'Unknown',
      frameType: member.frameType,
      status,
      utilization: status === 'pass' || status === 'fail' ? currentUtilization(member) : null,
    };
  });
}

export function viewportStatusCounts(inspection: readonly ViewportMemberInspection[]) {
  return inspection.reduce<Record<ViewportMemberStatus, number>>((counts, member) => {
    counts[member.status] += 1;
    return counts;
  }, { pass: 0, fail: 0, hold: 0, pending: 0, stale: 0, error: 0, not_evaluated: 0 });
}
