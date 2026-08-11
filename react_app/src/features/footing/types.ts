export type FootingPlanType = 'ISOLATED_SQUARE' | 'ISOLATED_RECTANGULAR';
export type FootingStatus = 'PASS' | 'FAIL' | 'HOLD';
export type CalculationStatus = 'PASS' | 'FAIL' | 'NOT_EVALUATED';
export type FootingDirection = 'L' | 'B';

export interface ConcentricIsolatedFootingRequest {
  case_id: string;
  service_axial_load_kN: number;
  service_load_combination_id: string;
  service_load_basis: 'includes_footing_self_weight_and_overburden';
  factored_axial_load_kN: number;
  factored_load_combination_id: string;
  allowable_soil_pressure_kPa: number;
  allowable_soil_pressure_source_reference: string;
  allowable_soil_pressure_is_externally_approved: true;
  footing_type: FootingPlanType;
  column_L_mm: number;
  column_B_mm: number;
  minimum_overall_thickness_mm: number;
  maximum_overall_thickness_mm: number;
  thickness_increment_mm: number;
  effective_depth_offset_L_mm: number;
  effective_depth_offset_B_mm: number;
  footing_concrete_fck_nmm2: number;
  column_concrete_fck_nmm2: number;
  steel_fy_nmm2: number;
  effective_supporting_area_A1_mm2: number;
  effective_supporting_area_basis: 'largest_frustum_1v_2h';
  effective_supporting_area_is_approved: true;
  dowel_count: number;
  dowel_diameter_mm: number;
  column_longitudinal_bar_diameter_mm: number;
  available_dowel_development_length_into_footing_mm: number;
  available_dowel_development_length_into_column_mm: number;
  dowel_bar_type?: 'deformed' | 'plain';
  nominal_cover_mm?: number;
  cover_exposure_basis?: string;
  cover_exposure_basis_is_approved?: boolean;
  nominal_max_aggregate_size_mm?: number;
  lower_bottom_bar_direction?: FootingDirection;
  upper_bottom_bar_direction?: FootingDirection;
  permitted_bottom_bar_diameters_mm?: number[];
  footing_bottom_bar_type?: 'deformed' | 'plain';
}

export interface FootingBearing {
  L_mm: number;
  B_mm: number;
  q_max_kPa: number;
  q_min_kPa: number;
  q_safe_kPa: number;
  pressure_type: string;
  utilization_ratio: number;
  is_safe: boolean;
  clause_ref: string;
  warnings: string[];
}

export interface FootingFlexure {
  Mu_L_kNm: number;
  Ast_L_mm2: number;
  pt_L_percent: number;
  cantilever_L_mm: number;
  Mu_B_kNm: number;
  Ast_B_mm2: number;
  pt_B_percent: number;
  cantilever_B_mm: number;
  d_mm: number;
  is_safe: boolean;
  central_band_fraction: number;
  clause_ref: string;
  warnings: string[];
}

export interface FootingOneWayShear {
  tau_v_nmm2: number;
  tau_c_nmm2: number;
  Vu_kN: number;
  d_mm: number;
  critical_section_mm: number;
  utilization_ratio: number;
  is_safe: boolean;
  governing_direction: string;
  clause_ref: string;
  warnings: string[];
}

export interface FootingPunching {
  tau_v_nmm2: number;
  tau_c_nmm2: number;
  perimeter_mm: number;
  Vu_punch_kN: number;
  d_mm: number;
  beta_c: number;
  ks: number;
  utilization_ratio: number;
  is_safe: boolean;
  clause_ref: string;
  warnings: string[];
}

export interface FootingDepthCandidate {
  overall_thickness_mm: number;
  effective_depth_L_mm: number;
  effective_depth_B_mm: number;
  structural_status: FootingStatus;
  one_way_shear_utilization: number | null;
  punching_shear_utilization: number | null;
  reasons: string[];
}

export interface FootingReinforcementDemand {
  direction: FootingDirection;
  effective_depth_mm: number;
  moment_kNm: number;
  required_steel_area_mm2: number;
  required_steel_percent: number;
  central_band_fraction: number | null;
  required_steel_basis: string;
  provided_steel_area_mm2: number | null;
  provided_steel_percent: number | null;
  detailing_status: FootingStatus;
}

export interface FootingReinforcementZone {
  zone: 'full_width' | 'central_band' | 'outer_band_each';
  width_mm: number;
  required_area_mm2: number;
  provided_area_mm2: number;
  bar_count: number;
  spacing_mm: number;
  clear_spacing_mm: number;
}

export interface FootingDirectionDetail {
  direction: FootingDirection;
  layer: 'lower' | 'upper';
  layout: 'uniform' | 'central_band';
  diameter_mm: number;
  physical_effective_depth_mm: number;
  analysis_effective_depth_mm: number;
  Mu_kNm: number;
  flexure_result_area_mm2: number;
  analysis_screening_area_mm2: number;
  minimum_area_mm2: number;
  required_area_mm2: number;
  provided_area_mm2: number;
  bar_count: number;
  spacing_mm: number;
  clear_spacing_mm: number;
  max_spacing_mm: number;
  minimum_clear_spacing_mm: number;
  max_diameter_mm: number;
  development_length_mm: number;
  development_length_unrounded_mm: number;
  straight_anchorage_available_each_end_mm: number;
  straight_bar_length_mm: number;
  zones: FootingReinforcementZone[];
}

export interface FootingDowelSchedule {
  bar_count: number;
  diameter_mm: number;
  required_area_mm2: number;
  provided_area_mm2: number;
  required_development_length_into_footing_mm: number;
  available_development_length_into_footing_mm: number;
  required_development_length_into_supported_member_mm: number;
  available_development_length_into_supported_member_mm: number;
  is_safe: boolean;
  source_ids: string[];
}

export interface FootingLoadTransfer {
  source_ids: string[];
  source_notes: string[];
  clause_refs: string[];
  supported_case: string;
  exclusions: string[];
  units: Record<string, string>;
  limits: Record<string, number | string>;
  Pu_kN: number;
  loaded_area_A2_mm2: number;
  effective_supporting_area_A1_mm2: number;
  effective_supporting_area_basis: string;
  bearing_enhancement_factor: number;
  actual_bearing_stress_nmm2: number;
  supported_concrete_bearing_capacity_kN: number;
  supporting_concrete_bearing_capacity_kN: number;
  governing_concrete_member: string;
  governing_concrete_bearing_capacity_kN: number;
  concrete_bearing_without_transfer_is_safe: boolean;
  excess_force_kN: number;
  excess_transfer_steel_area_mm2: number;
  minimum_transfer_steel_area_mm2: number;
  required_transfer_steel_area_mm2: number;
  provided_transfer_steel_area_mm2: number;
  transfer_steel_capacity_kN: number;
  minimum_bar_count: number;
  provided_bar_count: number;
  maximum_dowel_diameter_mm: number;
  provided_dowel_diameter_mm: number;
  supporting_concrete_design_bond_stress_nmm2: number;
  supported_concrete_design_bond_stress_nmm2: number;
  required_dowel_development_length_into_footing_mm: number;
  required_dowel_development_length_into_supported_member_mm: number;
  available_dowel_development_length_into_footing_mm: number;
  available_dowel_development_length_into_supported_member_mm: number;
  reinforcement_area_is_safe: boolean;
  bar_count_is_safe: boolean;
  dowel_diameter_is_safe: boolean;
  footing_development_length_is_safe: boolean;
  supported_member_development_length_is_safe: boolean;
  development_lengths_are_safe: boolean;
  is_safe: boolean;
  reasons: string[];
}

export interface FootingDetailing {
  status: FootingStatus;
  qualified_review_required: boolean;
  reasons: string[];
  contract_version: string;
  supported_case: string;
  exclusions: string[];
  units: Record<string, string>;
  source_ids: string[];
  clause_refs: string[];
  lower_direction: FootingDirection;
  upper_direction: FootingDirection;
  lower: FootingDirectionDetail | null;
  upper: FootingDirectionDetail | null;
  actual_provided_pt_percent: Record<string, number>;
  final_one_way_shear: FootingOneWayShear | null;
  dowel_schedule_link: FootingDowelSchedule;
  accepted_load_transfer: FootingLoadTransfer;
}

export interface FootingProvenance {
  schema_version: string;
  code_edition: string;
  units: Record<string, string>;
  service_load_combination_id: string;
  service_load_basis: string;
  factored_load_combination_id: string;
  allowable_soil_pressure_source_reference: string;
  allowable_soil_pressure_role: string;
  loaded_area_A2_basis: string;
  effective_supporting_area_basis: string;
  core_function_ids: string[];
  clause_bases: Record<string, string>;
  source_ids: string[];
  qualified_review_requirement: string;
}

export interface ConcentricIsolatedFootingResponse {
  case_id: string;
  status: FootingStatus;
  calculation_status: CalculationStatus;
  detailing_status: FootingStatus;
  detailing_hold_reason: string | null;
  qualified_review_required: boolean;
  supported_case: string;
  exclusions: string[];
  service_axial_load_kN: number;
  factored_axial_load_kN: number;
  selected_overall_thickness_mm: number | null;
  selected_effective_depth_L_mm: number | null;
  selected_effective_depth_B_mm: number | null;
  depth_candidates: FootingDepthCandidate[];
  bearing: FootingBearing;
  flexure: FootingFlexure | null;
  one_way_shear: FootingOneWayShear | null;
  one_way_shear_basis:
    | 'not_evaluated'
    | 'required_pt_screening'
    | 'actual_provided_pt_final';
  one_way_shear_screening: FootingOneWayShear | null;
  screening_pt_passed_to_one_way_shear_percent: Record<string, number>;
  punching: FootingPunching | null;
  load_transfer: FootingLoadTransfer;
  detailing: FootingDetailing | null;
  reinforcement_demands: FootingReinforcementDemand[];
  pt_passed_to_one_way_shear_percent: Record<string, number>;
  failed_checks: string[];
  hold_reasons: string[];
  provenance: FootingProvenance;
}

export interface ApiEnvelope<T> {
  success: boolean;
  data: T | null;
  error?: string | {
    code: string;
    message: string;
    details: unknown;
  };
}
