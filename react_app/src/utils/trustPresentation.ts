import type { BeamDesignResponse } from '../api/client';

export type TrustStatus = 'PASS' | 'FAIL' | 'HOLD';

export interface TrustPresentation {
  status: TrustStatus;
  exactUtilization: number;
  margin: number;
  governingCheck: string;
  calculationIdentity: string | null;
  inputHash: string | null;
  canExport: boolean;
}

function hasText(value: unknown): value is string {
  return typeof value === 'string' && value.trim().length > 0;
}

export function isBeamResultExportable(result: BeamDesignResponse): boolean {
  return getTrustPresentation(result).canExport;
}

/** Keep decision logic on exact values while presenting enough precision to audit it. */
export function getTrustPresentation(result: BeamDesignResponse): TrustPresentation {
  const evidence = result.evidence;
  const envelope = result.result_envelope;
  const identity = envelope.result_identity;
  const exactUtilization = evidence?.exact_utilization ?? result.utilization_ratio;
  const margin = evidence?.margin ?? 1 - exactUtilization;
  const hasIdentity = Boolean(
    evidence
    && evidence.support_status === 'SUPPORTED'
    && (evidence.status === 'PASS' || evidence.status === 'FAIL')
    && Number.isFinite(evidence.exact_utilization)
    && Number.isFinite(evidence.margin)
    && hasText(identity?.library_version)
    && hasText(identity?.input_hash)
    && hasText(identity?.calculation_identity)
    && identity?.input_hash === evidence.normalized_input_hash
    && identity?.calculation_identity === evidence.calculation_identity,
  );
  const hasHold =
    (result.holds?.length ?? 0) > 0
    || (envelope.overall_status !== 'PASS' && envelope.overall_status !== 'FAIL');
  const outcomeMatches =
    evidence?.status === envelope.engineering_status
    && envelope.overall_status === envelope.engineering_status
    && envelope.engineering_status === (result.success ? 'PASS' : 'FAIL');
  const status: TrustStatus = hasIdentity && !hasHold && outcomeMatches
    ? envelope.engineering_status as 'PASS' | 'FAIL'
    : 'HOLD';
  const canExport =
    status === 'PASS'
    && result.success
    && exactUtilization <= 1
    && hasIdentity
    && !hasHold;

  return {
    status,
    exactUtilization,
    margin,
    governingCheck: evidence?.governing_check ?? 'combined_compliance',
    calculationIdentity: evidence?.calculation_identity ?? null,
    inputHash: evidence?.normalized_input_hash ?? null,
    canExport,
  };
}

export function formatRatio(value: number): string {
  return value.toFixed(6);
}

export function formatPercent(value: number): string {
  return `${(value * 100).toFixed(3)}%`;
}

export function formatSignedRatio(value: number): string {
  return `${value >= 0 ? '+' : ''}${value.toFixed(6)}`;
}
