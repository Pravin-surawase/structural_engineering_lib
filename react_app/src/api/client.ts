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

export interface GeometryResult {
  volume: number;
  surface_area: number;
  weight: number;
}

export interface Beam3DGeometry {
  width: number;
  depth: number;
  length: number;
  main_bars?: {
    diameter: number;
    positions: [number, number, number][];
  };
  stirrups?: {
    spacing: number;
    diameter: number;
  };
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
 * Calculate beam geometry metrics.
 */
export async function calculateGeometry(
  width: number,
  depth: number,
  length: number
): Promise<GeometryResult> {
  const params = new URLSearchParams({
    width: String(width),
    depth: String(depth),
    length: String(length),
  });

  const response = await fetch(`${API_BASE_URL}/api/v1/geometry/beam?${params}`);

  if (!response.ok) {
    throw new Error(`Geometry calculation failed: ${response.status}`);
  }

  return response.json();
}

export default {
  checkHealth,
  designBeam,
  calculateGeometry,
};
