export type ColumnClassification = 'SHORT' | 'SLENDER';
export type ColumnReviewDecision = 'PASS' | 'FAIL' | 'HOLD';

export type ColumnEndCondition =
  | 'FIXED_FIXED'
  | 'FIXED_HINGED'
  | 'FIXED_FIXED_SWAY'
  | 'FIXED_FREE'
  | 'HINGED_HINGED'
  | 'FIXED_PARTIAL'
  | 'HINGED_PARTIAL';

export interface ColumnReviewInputs {
  member_label: string;
  Pu_kN: number;
  Mux_kNm: number;
  Muy_kNm: number;
  b_mm: number;
  D_mm: number;
  l_mm: number;
  end_condition: ColumnEndCondition;
  fck_nmm2: number;
  fy_nmm2: number;
  d_prime_mm: number;
  l_unsupported_mm: number;
  braced: boolean;
  M1x_kNm: number | null;
  M2x_kNm: number | null;
  M1y_kNm: number | null;
  M2y_kNm: number | null;
  cover_mm: number;
  num_bars: number;
  bar_dia_mm: number;
  tie_dia_mm: number;
  at_lap_section: boolean;
}

export interface ColumnDesignResponse {
  Pu_kN: number;
  Mux_applied_kNm: number;
  Muy_applied_kNm: number;
  Mux_design_kNm: number;
  Muy_design_kNm: number;
  Mux_min_kNm: number;
  Muy_min_kNm: number;
  Ma_x_kNm: number | null;
  Ma_y_kNm: number | null;
  is_safe: boolean;
  classification: ColumnClassification;
  classification_x: ColumnClassification;
  classification_y: ColumnClassification;
  le_x_mm: number;
  le_y_mm: number;
  slenderness_x: number;
  slenderness_y: number;
  emin_x_mm: number;
  emin_y_mm: number;
  governing_check: string;
  checks: Record<string, Record<string, unknown>>;
  clause_refs: string[];
  warnings: string[];
}

export interface ColumnDetailingResponse {
  b_mm: number;
  D_mm: number;
  Ag_mm2: number;
  num_bars: number;
  bar_dia_mm: number;
  Asc_provided_mm2: number;
  steel_ratio: number;
  min_steel_ok: boolean;
  max_steel_ok: boolean;
  min_bars_ok: boolean;
  min_bar_dia_ok: boolean;
  bar_spacing_mm: number;
  bar_spacing_ok: boolean;
  tie_dia_mm: number;
  tie_dia_required_mm: number;
  tie_spacing_mm: number;
  max_tie_spacing_mm: number;
  tie_spacing_ok: boolean;
  cross_ties_needed: boolean;
  is_valid: boolean;
  clause_ref: string;
  warnings: string[];
}

export interface ColumnReviewBundle {
  design: ColumnDesignResponse;
  detailing: ColumnDetailingResponse;
}

export interface ColumnRevisionIdentity {
  request_id: string;
  input_hash: string;
  input_revision: number;
  calculated_at: string;
}

export interface ColumnReviewRecord extends ColumnReviewBundle {
  inputs: ColumnReviewInputs;
  decision: ColumnReviewDecision;
  revision: ColumnRevisionIdentity;
}
