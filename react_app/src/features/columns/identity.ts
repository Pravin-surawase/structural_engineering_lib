import type { ColumnReviewInputs, ColumnReviewRecord } from './types';

function normalizedInputText(inputs: ColumnReviewInputs): string {
  return [
    inputs.member_label.trim(),
    inputs.Pu_kN,
    inputs.Mux_kNm,
    inputs.Muy_kNm,
    inputs.b_mm,
    inputs.D_mm,
    inputs.l_mm,
    inputs.end_condition,
    inputs.fck_nmm2,
    inputs.fy_nmm2,
    inputs.d_prime_mm,
    inputs.l_unsupported_mm,
    inputs.braced,
    inputs.M1x_kNm ?? '',
    inputs.M2x_kNm ?? '',
    inputs.M1y_kNm ?? '',
    inputs.M2y_kNm ?? '',
    inputs.cover_mm,
    inputs.num_bars,
    inputs.bar_dia_mm,
    inputs.tie_dia_mm,
    inputs.at_lap_section,
  ].join('|');
}

/** Deterministic non-cryptographic identity for detecting stale local results. */
export function columnInputHash(inputs: ColumnReviewInputs): string {
  const value = normalizedInputText(inputs);
  let hash = 2166136261;
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return `column-v1-${(hash >>> 0).toString(16).padStart(8, '0')}`;
}

export function columnReviewIsCurrent(
  record: ColumnReviewRecord | null,
  inputHash: string,
  inputRevision: number,
): boolean {
  return Boolean(
    record
    && record.revision.input_hash === inputHash
    && record.revision.input_revision === inputRevision,
  );
}

export function columnReviewCanExport(
  record: ColumnReviewRecord | null,
  inputHash: string,
  inputRevision: number,
): boolean {
  return Boolean(
    columnReviewIsCurrent(record, inputHash, inputRevision)
    && record?.decision === 'PASS'
    && record.design.is_safe
    && record.detailing.is_valid,
  );
}
