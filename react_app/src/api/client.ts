/**
 * Structural Design API Client
 *
 * TypeScript client for the FastAPI structural design API.
 * Based on clients/typescript/src/index.ts
 */

export interface BeamDesignRequest {
  width: number;
  depth: number;
  moment: number;
  shear?: number;
  fck: number;
  fy: number;
}

export interface FlexureResult {
  ast_required: number;
  ast_min: number;
  ast_max: number;
  xu: number;
  xu_max: number;
  is_under_reinforced: boolean;
  moment_capacity: number;
  asc_required?: number;
}

export interface ShearResult {
  tau_v: number;
  tau_c: number;
  tau_c_max: number;
  asv_required: number;
  stirrup_spacing: number;
  sv_max: number;
  shear_capacity: number;
}

export interface BeamDesignResponse {
  success: boolean;
  message: string;
  flexure: FlexureResult;
  shear?: ShearResult;
  ast_total: number;
  asc_total: number;
  utilization_ratio: number;
  warnings?: string[];
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
}

export interface Geometry3DRequest {
  width: number;
  depth: number;
  length: number;
  tension_bars?: Array<Record<string, unknown>>;
  compression_bars?: Array<Record<string, unknown>>;
  stirrup_diameter?: number;
  stirrup_spacing?: number;
  clear_cover?: number;
  include_rebars?: boolean;
  include_stirrups?: boolean;
  mesh_resolution?: 'low' | 'medium' | 'high';
  output_format?: 'vertices_faces' | 'stl' | 'gltf';
}

export interface MeshData {
  vertices: number[][];
  faces: number[][];
  normals?: number[][] | null;
}

export interface GeometryComponent {
  name: string;
  type: string;
  mesh: MeshData;
  color: number[];
  material_hint?: string;
}

export interface BoundingBox {
  min_x: number;
  max_x: number;
  min_y: number;
  max_y: number;
  min_z: number;
  max_z: number;
}

export interface Geometry3DResponse {
  success: boolean;
  message: string;
  components: GeometryComponent[];
  bounding_box: BoundingBox;
  center: number[];
  suggested_camera_distance: number;
  total_vertices: number;
  total_faces: number;
  stl_base64?: string | null;
  gltf_json?: Record<string, unknown> | null;
  warnings?: string[];
}

import { API_BASE_URL } from '../config';

/**
 * Check API health status.
 */
export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }
  return response.json();
}

/**
 * Design a reinforced concrete beam.
 */
export async function designBeam(
  params: BeamDesignRequest
): Promise<BeamDesignResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/design/beam`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Design failed: ${error.detail || response.status}`);
  }

  return response.json();
}

/**
 * Generate 3D beam geometry for visualization.
 */
export async function generateBeamGeometry(
  request: Geometry3DRequest
): Promise<Geometry3DResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/geometry/beam/3d`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Geometry generation failed: ${error.detail || response.status}`);
  }

  return response.json();
}

export async function calculateGeometry(
  width: number,
  depth: number,
  length: number
): Promise<Geometry3DResponse> {
  return generateBeamGeometry({ width, depth, length });
}

/**
 * Point in 3D space (meters, from ETABS/structural model).
 */
export interface Point3D {
  x: number;
  y: number;
  z: number;
}

/**
 * Load sample beam data for demo/testing.
 * Returns 153 beams from ETABS export with 3D positions.
 */
export interface SampleBeam {
  id: string;
  story: string;
  width_mm: number;
  depth_mm: number;
  span_mm: number;
  mu_knm: number;
  vu_kn: number;
  fck_mpa: number;
  fy_mpa: number;
  cover_mm: number;
  point1: Point3D;  // 3D start position
  point2: Point3D;  // 3D end position
}

export interface SampleDataResponse {
  success: boolean;
  message: string;
  beam_count: number;
  beams: SampleBeam[];
  format_detected: string;
  warnings: string[];
}

export async function loadSampleData(): Promise<SampleDataResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/import/sample`);
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Sample data load failed: ${error.detail || response.status}`);
  }
  return response.json();
}

// =============================================================================
// Torsion Design
// =============================================================================

export interface TorsionDesignRequest {
  width: number;
  depth: number;
  torsion: number;
  moment: number;
  shear?: number;
  fck?: number;
  fy?: number;
  clear_cover?: number;
  stirrup_dia?: number;
  pt?: number;
  effective_depth?: number;
}

export interface TorsionDesignResponse {
  success: boolean;
  message: string;
  tu_knm: number;
  vu_kn: number;
  mu_knm: number;
  ve_kn: number;
  me_knm: number;
  tv_equiv: number;
  tc: number;
  tc_max: number;
  asv_torsion: number;
  asv_shear: number;
  asv_total: number;
  stirrup_spacing: number;
  al_torsion: number;
  is_safe: boolean;
  requires_closed_stirrups: boolean;
  warnings?: string[];
}

/**
 * Design beam for combined torsion + shear + bending (IS 456 Cl 41).
 */
export async function designBeamTorsion(
  params: TorsionDesignRequest
): Promise<TorsionDesignResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/design/beam/torsion`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Torsion design failed: ${error.detail || response.status}`);
  }

  return response.json();
}

// =============================================================================
// Load Analysis Types
// =============================================================================

export interface LoadItem {
  load_type: 'udl' | 'point';
  magnitude: number;
  position_mm?: number;
}

export interface LoadAnalysisRequest {
  span_mm: number;
  support_condition: 'simply_supported' | 'cantilever';
  loads: LoadItem[];
  num_points?: number;
}

export interface CriticalPoint {
  position_mm: number;
  point_type: string;
  bm_knm: number;
  sf_kn: number;
}

export interface LoadAnalysisResponse {
  span_mm: number;
  support_condition: string;
  positions_mm: number[];
  bmd_knm: number[];
  sfd_kn: number[];
  max_bm_knm: number;
  min_bm_knm: number;
  max_sf_kn: number;
  min_sf_kn: number;
  critical_points: CriticalPoint[];
}

/**
 * Compute BMD/SFD for a beam with given loads.
 */
export async function analyzeLoads(
  params: LoadAnalysisRequest
): Promise<LoadAnalysisResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analysis/loads/simple`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Load analysis failed: ${error.detail || response.status}`);
  }

  return response.json();
}

// =============================================================================
// Pareto Optimization
// =============================================================================

export interface ParetoCandidateResponse {
  b_mm: number;
  D_mm: number;
  d_mm: number;
  fck_nmm2: number;
  fy_nmm2: number;
  ast_required: number;
  ast_provided: number;
  bar_config: string;
  cost: number;
  steel_weight_kg: number;
  utilization: number;
  is_safe: boolean;
  governing_clauses: string[];
  rank: number;
  crowding_distance: number;
}

export interface ParetoRequest {
  span_mm: number;
  mu_knm: number;
  vu_kn: number;
  objectives?: string[];
  cover_mm?: number;
  max_candidates?: number;
}

export interface ParetoResponse {
  pareto_front: ParetoCandidateResponse[];
  pareto_count: number;
  total_candidates: number;
  objectives_used: string[];
  computation_time_sec: number;
  best_by_cost: ParetoCandidateResponse | null;
  best_by_utilization: ParetoCandidateResponse | null;
  best_by_weight: ParetoCandidateResponse | null;
}

/**
 * Find Pareto-optimal beam designs balancing cost, weight, and utilization.
 */
export async function optimizeParetoFront(
  params: ParetoRequest
): Promise<ParetoResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/optimization/beam/pareto`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Pareto optimization failed: ${error.detail || response.status}`);
  }

  return response.json();
}

export default {
  checkHealth,
  designBeam,
  designBeamTorsion,
  analyzeLoads,
  generateBeamGeometry,
  calculateGeometry,
  loadSampleData,
  optimizeParetoFront,
};
