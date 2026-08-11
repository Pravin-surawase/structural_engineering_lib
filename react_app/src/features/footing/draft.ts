import type {
  ConcentricIsolatedFootingRequest,
  FootingDirection,
} from './types';

export type FootingDraft = Omit<
  ConcentricIsolatedFootingRequest,
  | 'allowable_soil_pressure_is_externally_approved'
  | 'effective_supporting_area_is_approved'
> & {
  soil_pressure_approved: boolean;
  a1_basis_approved: boolean;
  detailing_enabled: boolean;
};

const DETAILING_DEFAULTS = {
  nominal_cover_mm: 50,
  cover_exposure_basis: 'approved severe footing schedule',
  cover_exposure_basis_is_approved: false,
  nominal_max_aggregate_size_mm: 20,
  lower_bottom_bar_direction: 'L' as FootingDirection,
  upper_bottom_bar_direction: 'B' as FootingDirection,
  permitted_bottom_bar_diameters_mm: [12, 16, 20, 25, 32],
  footing_bottom_bar_type: 'deformed' as const,
};

export const INITIAL_FOOTING_DRAFT: FootingDraft = {
  case_id: 'FOOT-C1-SQ-001',
  service_axial_load_kN: 800,
  service_load_combination_id: 'SLS-GRAVITY-01',
  service_load_basis: 'includes_footing_self_weight_and_overburden',
  factored_axial_load_kN: 1200,
  factored_load_combination_id: 'ULS-GRAVITY-01',
  allowable_soil_pressure_kPa: 200,
  allowable_soil_pressure_source_reference: 'GEO-REPORT-001',
  footing_type: 'ISOLATED_SQUARE',
  column_L_mm: 400,
  column_B_mm: 400,
  minimum_overall_thickness_mm: 500,
  maximum_overall_thickness_mm: 500,
  thickness_increment_mm: 50,
  effective_depth_offset_L_mm: 100,
  effective_depth_offset_B_mm: 100,
  footing_concrete_fck_nmm2: 25,
  column_concrete_fck_nmm2: 25,
  steel_fy_nmm2: 415,
  effective_supporting_area_A1_mm2: 640000,
  effective_supporting_area_basis: 'largest_frustum_1v_2h',
  dowel_count: 4,
  dowel_diameter_mm: 20,
  column_longitudinal_bar_diameter_mm: 20,
  available_dowel_development_length_into_footing_mm: 1000,
  available_dowel_development_length_into_column_mm: 1000,
  dowel_bar_type: 'deformed',
  soil_pressure_approved: false,
  a1_basis_approved: false,
  detailing_enabled: false,
};

const REQUIRED_TEXT_FIELDS = [
  'case_id',
  'service_load_combination_id',
  'factored_load_combination_id',
  'allowable_soil_pressure_source_reference',
] as const;

const POSITIVE_NUMBER_FIELDS = [
  'service_axial_load_kN',
  'factored_axial_load_kN',
  'allowable_soil_pressure_kPa',
  'column_L_mm',
  'column_B_mm',
  'minimum_overall_thickness_mm',
  'maximum_overall_thickness_mm',
  'thickness_increment_mm',
  'effective_depth_offset_L_mm',
  'effective_depth_offset_B_mm',
  'footing_concrete_fck_nmm2',
  'column_concrete_fck_nmm2',
  'steel_fy_nmm2',
  'effective_supporting_area_A1_mm2',
  'dowel_count',
  'dowel_diameter_mm',
  'column_longitudinal_bar_diameter_mm',
  'available_dowel_development_length_into_footing_mm',
  'available_dowel_development_length_into_column_mm',
] as const;

export function updateFootingDraft(
  draft: FootingDraft,
  key: keyof FootingDraft,
  value: FootingDraft[keyof FootingDraft],
): FootingDraft {
  const next = { ...draft, [key]: value } as FootingDraft;

  if (
    key === 'column_L_mm'
    && draft.footing_type === 'ISOLATED_SQUARE'
    && typeof value === 'number'
  ) {
    next.column_B_mm = value;
  }
  if (key === 'footing_type' && value === 'ISOLATED_SQUARE') {
    next.column_B_mm = draft.column_L_mm;
  }
  if (key === 'detailing_enabled' && value === true) {
    Object.assign(next, DETAILING_DEFAULTS);
  }
  return next;
}

export function validateFootingDraft(draft: FootingDraft): string[] {
  const issues: string[] = [];

  for (const key of REQUIRED_TEXT_FIELDS) {
    if (!draft[key].trim()) issues.push(`${key} is required.`);
  }
  for (const key of POSITIVE_NUMBER_FIELDS) {
    const value = draft[key];
    if (!Number.isFinite(value) || value <= 0) {
      issues.push(`${key} must be a positive finite number.`);
    }
  }
  if (draft.minimum_overall_thickness_mm < 150) {
    issues.push('Minimum overall thickness must be at least 150 mm.');
  }
  if (draft.maximum_overall_thickness_mm < draft.minimum_overall_thickness_mm) {
    issues.push('Maximum overall thickness must not be below the minimum.');
  }
  if (!Number.isInteger(draft.dowel_count)) {
    issues.push('Dowel count must be a whole number.');
  }
  if (
    draft.footing_type === 'ISOLATED_SQUARE'
    && draft.column_L_mm !== draft.column_B_mm
  ) {
    issues.push('Square footing mode requires equal column L and B dimensions.');
  }
  if (!draft.soil_pressure_approved) {
    issues.push('External allowable-soil-pressure approval is required.');
  }
  if (!draft.a1_basis_approved) {
    issues.push('Effective supporting area A1 approval is required.');
  }

  if (draft.detailing_enabled) {
    if (!draft.cover_exposure_basis_is_approved) {
      issues.push('The detailing cover/exposure basis must be approved.');
    }
    if (!draft.cover_exposure_basis?.trim()) {
      issues.push('The detailing cover/exposure basis is required.');
    }
    if (!Number.isFinite(draft.nominal_cover_mm) || (draft.nominal_cover_mm ?? 0) <= 0) {
      issues.push('Nominal cover must be a positive finite number.');
    }
    if (
      !Number.isFinite(draft.nominal_max_aggregate_size_mm)
      || (draft.nominal_max_aggregate_size_mm ?? 0) <= 0
    ) {
      issues.push('Nominal maximum aggregate size must be a positive finite number.');
    }
    if (draft.lower_bottom_bar_direction === draft.upper_bottom_bar_direction) {
      issues.push('Lower and upper bottom-bar directions must be different.');
    }
    const diameters = draft.permitted_bottom_bar_diameters_mm ?? [];
    if (
      diameters.length === 0
      || diameters.some((diameter) => !Number.isInteger(diameter) || diameter <= 0)
    ) {
      issues.push('Permitted bottom-bar diameters must be positive whole numbers.');
    }
  }

  return issues;
}

export function createFootingRequest(
  draft: FootingDraft,
): ConcentricIsolatedFootingRequest | null {
  if (validateFootingDraft(draft).length > 0) return null;

  const {
    soil_pressure_approved: _soilPressureApproved,
    a1_basis_approved: _a1BasisApproved,
    detailing_enabled: detailingEnabled,
    ...base
  } = draft;
  const required = {
    ...base,
    allowable_soil_pressure_is_externally_approved: true as const,
    effective_supporting_area_is_approved: true as const,
  };
  if (!detailingEnabled) {
    const {
      nominal_cover_mm: _nominalCover,
      cover_exposure_basis: _coverBasis,
      cover_exposure_basis_is_approved: _coverApproved,
      nominal_max_aggregate_size_mm: _aggregateSize,
      lower_bottom_bar_direction: _lowerDirection,
      upper_bottom_bar_direction: _upperDirection,
      permitted_bottom_bar_diameters_mm: _diameters,
      footing_bottom_bar_type: _barType,
      ...withoutDetailing
    } = required;
    return withoutDetailing;
  }
  return required;
}
