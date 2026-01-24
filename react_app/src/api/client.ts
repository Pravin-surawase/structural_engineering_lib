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

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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

export default {
  checkHealth,
  designBeam,
  generateBeamGeometry,
  calculateGeometry,
};
