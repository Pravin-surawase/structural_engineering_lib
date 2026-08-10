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

/** Keep decision logic on exact values while presenting enough precision to audit it. */
export function getTrustPresentation(result: BeamDesignResponse): TrustPresentation {
  const evidence = result.evidence;
  const exactUtilization = evidence?.exact_utilization ?? result.utilization_ratio;
  const margin = evidence?.margin ?? 1 - exactUtilization;
  const evidenceStatus = evidence?.status;
  const status: TrustStatus = evidenceStatus
    ?? (result.success && exactUtilization <= 1 ? 'PASS' : 'FAIL');
  const canExport =
    status === 'PASS'
    && result.success
    && exactUtilization <= 1
    && evidence?.support_status !== 'HELD';

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
