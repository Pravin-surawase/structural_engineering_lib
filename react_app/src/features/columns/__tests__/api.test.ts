import { afterEach, describe, expect, it, vi } from 'vitest';
import { reviewRectangularColumn } from '../api';
import { DEFAULT_COLUMN_REVIEW_INPUTS } from '../defaults';

const DETAILING = {
  b_mm: 300,
  D_mm: 450,
  Ag_mm2: 135000,
  num_bars: 8,
  bar_dia_mm: 20,
  Asc_provided_mm2: 2513.27,
  steel_ratio: 0.018617,
  min_steel_ok: true,
  max_steel_ok: true,
  min_bars_ok: true,
  min_bar_dia_ok: true,
  bar_spacing_mm: 145,
  bar_spacing_ok: true,
  tie_dia_mm: 8,
  tie_dia_required_mm: 6,
  tie_spacing_mm: 300,
  max_tie_spacing_mm: 300,
  tie_spacing_ok: true,
  cross_ties_needed: false,
  is_valid: true,
  clause_ref: 'Cl. 26.5.3',
  warnings: [],
};

const DESIGN = {
  Pu_kN: 800,
  Mux_applied_kNm: 120,
  Muy_applied_kNm: 40,
  Mux_design_kNm: 120,
  Muy_design_kNm: 40,
  Mux_min_kNm: 20.8,
  Muy_min_kNm: 16,
  Ma_x_kNm: null,
  Ma_y_kNm: null,
  is_safe: true,
  classification: 'SHORT',
  classification_x: 'SHORT',
  classification_y: 'SHORT',
  le_x_mm: 1950,
  le_y_mm: 1950,
  slenderness_x: 4.333,
  slenderness_y: 6.5,
  emin_x_mm: 26,
  emin_y_mm: 20,
  governing_check: 'biaxial',
  checks: { biaxial: { interaction_ratio: 0.7, is_safe: true } },
  clause_refs: ['Cl. 25.2', 'Cl. 25.1.2', 'Cl. 25.4', 'Cl. 39.6'],
  warnings: [],
};

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('reviewRectangularColumn', () => {
  it('uses server-computed provided steel area in the unified adequacy request', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ success: true, data: DETAILING }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ success: true, data: DESIGN }), { status: 200 }));
    vi.stubGlobal('fetch', fetchMock);

    const result = await reviewRectangularColumn(DEFAULT_COLUMN_REVIEW_INPUTS);

    expect(result.detailing.Asc_provided_mm2).toBe(2513.27);
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(fetchMock.mock.calls[0][0]).toContain('/api/v1/design/column/detailing');
    expect(fetchMock.mock.calls[1][0]).toContain('/api/v1/design/column');
    const designRequest = JSON.parse(String(fetchMock.mock.calls[1][1]?.body));
    expect(designRequest.Asc_mm2).toBe(2513.27);
    expect(designRequest.is_circular).toBeUndefined();
  });
});
