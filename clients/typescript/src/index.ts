/**
 * Structural Design API Client
 *
 * Auto-generated TypeScript client for the FastAPI structural design API.
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
  ast_provided: number;
  is_safe: boolean;
  utilization_ratio: number;
}

export interface DesignResult {
  status: 'PASS' | 'FAIL';
  flexure: FlexureResult;
  shear?: Record<string, unknown>;
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

export class StructuralDesignClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  /**
   * Check API health status.
   */
  async health(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Design a reinforced concrete beam.
   */
  async designBeam(params: BeamDesignRequest): Promise<DesignResult> {
    const response = await fetch(`${this.baseUrl}/api/v1/design/beam`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(`Design failed: ${error.detail || response.status}`);
    }

    return response.json();
  }

  /**
   * Calculate beam geometry metrics.
   */
  async calculateGeometry(
    width: number,
    depth: number,
    length: number,
  ): Promise<GeometryResult> {
    const params = new URLSearchParams({
      width: String(width),
      depth: String(depth),
      length: String(length),
    });

    const response = await fetch(`${this.baseUrl}/api/v1/geometry/beam?${params}`);

    if (!response.ok) {
      throw new Error(`Geometry calculation failed: ${response.status}`);
    }

    return response.json();
  }
}

export default StructuralDesignClient;
