/**
 * API Response Fixtures
 *
 * Realistic response shapes matching all 12 FastAPI routers.
 * Single source of truth for test data — keeps tests DRY and contracts clear.
 */

// ── Health ────────────────────────────────────────────────────────────
export const healthResponse = {
  status: 'healthy',
  version: '0.19.1',
  timestamp: '2026-03-25T10:00:00Z',
  uptime_seconds: 3600,
};

export const readyResponse = {
  ready: true,
  checks: { library: true, memory: true },
};

export const infoResponse = {
  python_version: '3.11.6',
  platform: 'darwin',
  api_version: '0.19.1',
};

// ── Design ────────────────────────────────────────────────────────────
export const designRequest = {
  width: 300,
  depth: 500,
  moment: 150,
  shear: 75,
  fck: 25,
  fy: 500,
  clear_cover: 25,
};

export const designResponse = {
  success: true,
  flexure: {
    ast_required: 850.5,
    moment_capacity: 165.2,
    xu_d_ratio: 0.42,
    is_under_reinforced: true,
  },
  shear: {
    tau_v: 0.65,
    tau_c: 0.48,
    asv_required: 0.45,
    stirrup_spacing: 150,
    is_adequate: true,
  },
  ast_total: 850.5,
  utilization_ratio: 0.87,
  warnings: [],
};

export const checkResponse = {
  is_adequate: true,
  moment_capacity: 165.2,
  shear_capacity: 90.5,
  moment_utilization: 0.91,
  shear_utilization: 0.83,
};

export const limitsResponse = {
  concrete: { min_fck: 15, max_fck: 80 },
  steel: { grades: [250, 415, 500, 550] },
  reinforcement: { min_percentage: 0.12, max_percentage: 4.0 },
  clear_cover: { min: 20, max: 75 },
};

// ── Detailing ─────────────────────────────────────────────────────────
export const detailingRequest = {
  width: 300,
  depth: 500,
  ast_required: 850,
  asc_required: 0,
  asv_required: 0.5,
  fck: 25,
  fy: 500,
  clear_cover: 25,
  preferred_bar_dia: [16, 20],
  max_layers: 2,
};

export const detailingResponse = {
  success: true,
  tension_bars: { count: 3, diameter: 20, layers: 1, area_provided: 942.5 },
  ast_provided: 942.5,
  compression_bars: null,
  stirrups: { diameter: 8, spacing: 150, legs: 2 },
};

export const barAreasResponse = {
  bars: {
    T8: { diameter_mm: 8, area_mm2: 50.3 },
    T10: { diameter_mm: 10, area_mm2: 78.5 },
    T12: { diameter_mm: 12, area_mm2: 113.1 },
    T16: { diameter_mm: 16, area_mm2: 201.1 },
    T20: { diameter_mm: 20, area_mm2: 314.2 },
    T25: { diameter_mm: 25, area_mm2: 490.9 },
    T32: { diameter_mm: 32, area_mm2: 804.2 },
  },
};

export const developmentLengthResponse = {
  bar_diameter: 16,
  ld: 752,
  fck: 25,
  fy: 500,
  bar_type: 'deformed',
};

// ── Import ────────────────────────────────────────────────────────────
export const sampleDataResponse = {
  beams: [
    { id: 'B1', story: 'GF', b: 300, D: 500, span: 5000, fck: 25, fy: 500 },
    { id: 'B2', story: '1F', b: 250, D: 450, span: 4500, fck: 25, fy: 500 },
  ],
  format: 'generic',
};

export const importFormatsResponse = {
  formats: ['generic', 'etabs', 'safe', 'staad'],
  default: 'generic',
};

// ── Geometry ──────────────────────────────────────────────────────────
export const geometryResponse = {
  success: true,
  components: [
    { name: 'beam_body', vertices: [[0, 0, 0]], faces: [[0, 1, 2]], color: '#808080' },
  ],
  bounding_box: { min: [0, 0, 0], max: [300, 500, 3000] },
  center: [150, 250, 1500],
  total_vertices: 8,
  total_faces: 12,
};

export const materialsResponse = {
  concrete: { color: '#C0C0C0', density: 2400 },
  steel: { color: '#4A90D9', density: 7850 },
};

// ── Optimization ──────────────────────────────────────────────────────
export const optimizationResponse = {
  success: true,
  optimal: {
    width: 300,
    depth: 550,
    cost_breakdown: { concrete: 1200, steel: 800, formwork: 600, total: 2600 },
    ast_required: 720,
    utilization: 0.82,
  },
  alternatives: [],
};

export const costRatesResponse = {
  materials: {
    concrete: { cost_per_m3: 6000, unit: 'INR/m³' },
    steel: { cost_per_kg: 60, unit: 'INR/kg' },
    formwork: { cost_per_m2: 400, unit: 'INR/m²' },
  },
};

// ── Analysis ──────────────────────────────────────────────────────────
export const analysisResponse = {
  success: true,
  design_summary: { moment_capacity: 165, shear_capacity: 90, utilization: 0.87 },
  all_checks_passed: true,
  suggestions: [],
};

export const codeClausesResponse = {
  flexure: { clause: '38.1', title: 'Limit State of Collapse: Flexure' },
  shear: { clause: '40', title: 'Limit State of Collapse: Shear' },
  detailing: { clause: '26', title: 'Requirements Governing Reinforcement' },
};

// ── Insights ──────────────────────────────────────────────────────────
export const dashboardRequest = {
  results: [
    { beam_id: 'B1', story: 'GF', is_valid: true, utilization: 0.87, ast_provided: 942, b_mm: 300, D_mm: 500, span_mm: 5000, warnings: [] },
    { beam_id: 'B2', story: 'GF', is_valid: false, utilization: 1.15, ast_provided: 628, b_mm: 250, D_mm: 450, span_mm: 4500, warnings: ['Over-reinforced'] },
  ],
};

export const dashboardResponse = {
  success: true,
  message: '2 beams analyzed',
  total_beams: 2,
  passed: 1,
  failed: 1,
  pass_rate: 50.0,
  warnings_count: 1,
  avg_utilization: 1.01,
  max_utilization: 1.15,
  min_utilization: 0.87,
  total_steel_kg: 12.5,
  total_concrete_m3: 0.45,
  critical_beams: ['B2'],
  by_story: { GF: { total: 2, passed: 1, failed: 1 } },
};

export const codeChecksResponse = {
  passed: true,
  checks: [
    { name: 'Flexure', clause: 'Cl. 38.1', passed: true, value: 0.87, limit: 1.0, utilization: 0.87 },
    { name: 'Shear', clause: 'Cl. 40', passed: true, value: 0.65, limit: 1.0, utilization: 0.65 },
  ],
  critical_failures: [],
  warnings: [],
  utilization: 0.87,
  governing_check: 'Flexure',
};

export const rebarSuggestResponse = {
  suggestions: [
    {
      title: '3T20 bottom',
      description: 'Optimal bar configuration for flexure',
      impact: 'MEDIUM',
      savings_percent: 8,
      bar_count: 3,
      bar_diameter: 20,
      ast_provided: 942.5,
      rationale: 'Reduces steel by matching required Ast closely',
    },
  ],
};

// ── Rebar ─────────────────────────────────────────────────────────────
export const rebarValidateResponse = {
  valid: true,
  ast_provided: 942.5,
  ast_required: 850,
  utilization: 0.90,
  warnings: [],
};

export const rebarApplyResponse = {
  success: true,
  config: { tension: { count: 3, diameter: 20, area: 942.5 } },
};

// ── Export ─────────────────────────────────────────────────────────────
// Export endpoints return file blobs, not JSON — tested differently

// ── Streaming ─────────────────────────────────────────────────────────
// SSE endpoints are tested via EventSource pattern (see useBatchDesign tests)
