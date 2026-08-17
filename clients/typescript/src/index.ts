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
  clear_cover?: number;
  stirrup_dia_mm?: number;
  main_bar_dia_mm?: number;
  effective_depth?: number;
}

export interface APIResponse<T> {
  success: true;
  data: T;
  clause_refs?: Record<string, string>;
}

export interface ProblemResponse {
  success: false;
  data: null;
  error: {
    schema_version: 'structural-problem/v1';
    code: string;
    message: string;
    details?: unknown;
    request_id?: string;
  };
}

export interface FlexureResult {
  ast_required: number;
  ast_min: number;
  ast_max: number;
  xu: number;
  xu_max: number;
  is_under_reinforced: boolean;
  moment_capacity: number;
  asc_required: number;
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
  effective_depth_used?: number;
  effective_depth_basis: {
    contract_version: 'effective-depth-basis/v1';
    source: 'EXPLICIT' | 'DERIVED';
    D_mm: number;
    d_mm: number;
    effective_depth_basis: Record<string, number> | null;
  };
  result_envelope: {
    schema_version: 'structural-result-envelope/v2';
    intake_status: 'VALID' | 'PARTIAL' | 'BLOCKED';
    calculation_status: 'NOT_EVALUATED' | 'COMPLETED' | 'ERROR';
    engineering_status: 'NOT_EVALUATED' | 'PASS' | 'FAIL' | 'HOLD';
    review_status: 'QUALIFIED_REVIEW_REQUIRED' | 'REVIEWED_ACCEPTED' | 'REVIEWED_REJECTED';
    qualified_review_required: boolean;
    freshness_status: 'CURRENT' | 'STALE';
    serviceability_escalation: string | null;
    overall_status: 'BLOCKED' | 'ERROR' | 'NOT_EVALUATED' | 'STALE' | 'PASS' | 'FAIL' | 'HOLD';
    result_identity: Record<string, string | null> | null;
    issues: Array<{ code: string; path: string; message: string }>;
  };
  warnings?: string[];
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
}

export interface GeometryResult {
  success: boolean;
  message: string;
  components: Array<Record<string, unknown>>;
  bounding_box: Record<string, number>;
  center: number[];
  suggested_camera_distance: number;
  total_vertices: number;
  total_faces: number;
  stl_base64?: string | null;
  gltf_json?: Record<string, unknown> | null;
  warnings?: string[];
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
  async designBeam(params: BeamDesignRequest): Promise<BeamDesignResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/design/beam`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      const problem = await response.json() as ProblemResponse;
      throw new Error(
        `Design failed: ${problem.error?.code ?? response.status}: ${problem.error?.message ?? 'Request failed'}`,
      );
    }

    const envelope = await response.json() as APIResponse<BeamDesignResponse>;
    return envelope.data;
  }

  /**
   * Calculate beam geometry metrics.
   */
  async calculateGeometry(
    width: number,
    depth: number,
    length: number,
  ): Promise<GeometryResult> {
    const response = await fetch(`${this.baseUrl}/api/v1/geometry/beam/3d`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ width, depth, length }),
    });

    if (!response.ok) {
      const problem = await response.json() as ProblemResponse;
      throw new Error(
        `Geometry calculation failed: ${problem.error?.code ?? response.status}: ${problem.error?.message ?? 'Request failed'}`,
      );
    }

    const envelope = await response.json() as APIResponse<GeometryResult>;
    return envelope.data;
  }
}

export default StructuralDesignClient;
