import { describe, expect, it, vi } from 'vitest';
import { designConcentricIsolatedFooting } from '../client';
import type { ConcentricIsolatedFootingRequest } from '../types';

const request: ConcentricIsolatedFootingRequest = {
  case_id: 'C1-FOOTING-001', service_axial_load_kN: 900, service_load_combination_id: 'SLS-01', service_load_basis: 'includes_footing_self_weight_and_overburden', service_load_origin: 'provided', factored_axial_load_kN: 1350, factored_load_combination_id: 'ULS-01', allowable_soil_pressure_kPa: 200, allowable_soil_pressure_source_reference: 'GEOTECH-APPROVAL-001', allowable_soil_pressure_origin: 'verified', allowable_soil_pressure_is_externally_approved: true, footing_type: 'ISOLATED_SQUARE', column_L_mm: 400, column_B_mm: 400, minimum_overall_thickness_mm: 350, maximum_overall_thickness_mm: 700, thickness_increment_mm: 25, effective_depth_offset_L_mm: 75, effective_depth_offset_B_mm: 75, footing_concrete_fck_nmm2: 25, column_concrete_fck_nmm2: 25, steel_fy_nmm2: 500, effective_supporting_area_A1_mm2: 640000, effective_supporting_area_basis: 'largest_frustum_1v_2h', effective_supporting_area_origin: 'provided', effective_supporting_area_is_approved: true, dowel_count: 8, dowel_diameter_mm: 16, column_longitudinal_bar_diameter_mm: 16, available_dowel_development_length_into_footing_mm: 600, available_dowel_development_length_into_column_mm: 500,
};

describe('designConcentricIsolatedFooting', () => {
  it('posts the exact request and unwraps the API envelope', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({ success: true, data: { case_id: request.case_id, status: 'PASS' }, error: null }), { status: 200, headers: { 'Content-Type': 'application/json' } }));
    await expect(designConcentricIsolatedFooting(request)).resolves.toMatchObject({ case_id: 'C1-FOOTING-001', status: 'PASS' });
    expect(fetchMock).toHaveBeenCalledWith(expect.stringMatching(/\/api\/v1\/design\/footing\/isolated\/concentric$/), expect.objectContaining({ method: 'POST', body: JSON.stringify(request) }));
  });

  it('fails closed for a bad envelope or transport response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({ success: false, data: null, error: { code: 'REQUEST_VALIDATION_ERROR', message: 'Request validation failed', details: [] } }), { status: 422 }));
    await expect(designConcentricIsolatedFooting(request)).rejects.toThrow('Request validation failed');
  });
});
