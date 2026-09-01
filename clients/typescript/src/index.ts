/**
 * Structural Design API Client
 *
 * Auto-generated TypeScript client for the FastAPI structural design API.
 */

export const API_VERSION = '0.24.0' as const;

export interface BeamDesignRequest {
  width: number;
  depth: number;
  moment: number;
  shear: number;
  fck: number;
  fy: number;
  clear_cover: number;
  stirrup_dia_mm: number;
  main_bar_dia_mm: number;
  effective_depth?: number;
}

export interface CanonicalBeamDesignRequestV1 {
  schema_version?: 'beam-design-input/v1';
  identity: { member_id: string; story: string; case_id: string };
  section: {
    span_mm?: number;
    b_mm: number;
    D_mm: number;
    d_mm?: number;
    effective_depth_basis?: {
      clear_cover_mm: number;
      stirrup_diameter_mm: number;
      tension_bar_diameter_mm: number;
    };
  };
  materials: { fck_nmm2: number; fy_nmm2: number };
  actions: { mu_knm: number; vu_kn: number; tu_knm?: number; primary_tension_face?: "TOP" | "BOTTOM" };
  calculation_basis: {
    d_dash_mm: number;
    asv_mm2: number;
    pt_percent?: number;
    ast_mm2_for_shear?: number;
  };
  detailing?: CanonicalBeamDetailingOptionsV1;
  serviceability?: Record<string, unknown>;
  source_provenance?: string;
}

export interface CanonicalBeamDetailingOptionsV1 {
  standard: 'IS456' | 'IS13920';
  clear_cover_mm: number;
  tension_bar_diameter_mm: 8 | 10 | 12 | 16 | 20 | 25 | 32;
  compression_bar_diameter_mm: 8 | 10 | 12 | 16 | 20 | 25 | 32;
  side_face_bar_diameter_mm?: 8 | 10 | 12 | 16 | 20 | 25 | 32;
  nominal_top_steel_ratio: number;
  stirrup_diameter_mm: number;
  stirrup_legs: number;
  stirrup_spacing_support_mm: number;
  stirrup_spacing_mid_mm: number;
}

export interface CanonicalBeamDesignResponseV1 {
  schema_version: 'beam-design-result/v1';
  identity: CanonicalBeamDesignRequestV1['identity'];
  request: CanonicalBeamDesignRequestV1;
  envelope: BeamDesignResponse['result_envelope'];
  calculation: Record<string, unknown>;
  limitations: string[];
  assumptions: string[];
  provenance: string[];
}

export interface BeamBarLayersV2 {
  diameter_mm: number;
  bars_per_layer: number[];
  vertical_center_spacings_mm?: number[];
}

export interface BeamSuppliedCheckRequestV2 {
  schema_version?: 'beam-supplied-check/v2';
  correlation_id: string;
  identity: { member_id: string; story: string; case_id: string };
  section: {
    b_mm: number;
    D_mm: number;
    d_mm?: number;
    effective_depth_basis?:
      | {
          clear_cover_mm: number;
          stirrup_diameter_mm: number;
          tension_bar_diameter_mm: number;
        }
      | { centroid_cover_mm: number };
  };
  materials: {
    fck_nmm2: number;
    fy_nmm2: number;
    fy_transverse_nmm2: number;
  };
  actions: {
    mu_knm: number;
    vu_kn: number;
    primary_tension_face: 'TOP' | 'BOTTOM';
  };
  reinforcement: {
    clear_cover_mm: number;
    tension: BeamBarLayersV2;
    compression_or_hanger: BeamBarLayersV2;
    stirrup_diameter_mm: number;
    stirrup_legs: number;
    stirrup_spacing_mm: number;
    bar_type: 'deformed' | 'plain';
    has_standard_bend_at_start: boolean;
    has_standard_bend_at_end: boolean;
    source_reference: string;
  };
  selection: {
    permitted_diameters_mm: number[];
    maximum_layers: number;
    maximum_bars_per_layer: number;
    nominal_max_aggregate_size_mm: number;
    effective_depth_tolerance_mm: number;
    objective: 'min_area' | 'min_bar_count' | 'max_spacing';
    source_reference: string;
  };
  support?: {
    start_width_mm: number;
    end_width_mm: number;
    source_reference: string;
  } | null;
  source_provenance?: string;
}

export interface BeamSuppliedCheckResultV2 {
  schema_version: 'beam-supplied-check-result/v2';
  correlation_id: string;
  status: 'PASS' | 'FAIL' | 'HOLD' | 'ERROR';
  identity: BeamSuppliedCheckRequestV2['identity'];
  primary_tension_face: 'TOP' | 'BOTTOM';
  request: BeamSuppliedCheckRequestV2;
  effective_depth_resolution: {
    contract_version: 'effective-depth-basis/v1';
    source: 'EXPLICIT' | 'DERIVED';
    D_mm: number;
    d_mm: number;
    effective_depth_basis: Record<string, number> | null;
  };
  d_dash_used_mm: number;
  longitudinal: {
    schema_version: 'beam-reinforcement-evaluation/v1';
    status: 'PASS' | 'FAIL' | 'HOLD';
    ast_required_mm2: number;
    asc_required_mm2: number;
    checks: Record<string, unknown>;
    issues: Array<{ code: string; message: string }>;
    limitations: string[];
  } & Record<string, unknown>;
  shear: {
    schema_version: 'beam-supplied-shear-check/v2';
    status: 'PASS' | 'FAIL';
    required_Vus_kn: number;
    provided_asv_mm2: number;
    provided_spacing_mm: number;
    maximum_permitted_spacing_mm: number;
    spacing_is_adequate: boolean;
    capacity_is_adequate: boolean;
    section_shear_is_adequate: boolean;
    issues: Array<{ code: string; path: string; message: string }>;
  } & Record<string, unknown>;
  result_envelope: BeamDesignResponse['result_envelope'];
  limitations: string[];
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

  /** Run the canonical v2 nested beam contract. */
  async designBeamV2(
    request: CanonicalBeamDesignRequestV1,
  ): Promise<CanonicalBeamDesignResponseV1> {
    const response = await fetch(`${this.baseUrl}/api/v2/design/beam`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      const problem = await response.json() as ProblemResponse;
      throw new Error(
        `Canonical design failed: ${problem.error?.code ?? response.status}: ${problem.error?.message ?? 'Request failed'}`,
      );
    }
    return response.json() as Promise<CanonicalBeamDesignResponseV1>;
  }

  /** Check one exact supplied reinforcement schedule with the V2 contract. */
  async checkSuppliedBeam(
    request: BeamSuppliedCheckRequestV2,
  ): Promise<BeamSuppliedCheckResultV2> {
    const response = await fetch(`${this.baseUrl}/api/v1/design/beam/check`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      const problem = await response.json() as ProblemResponse;
      throw new Error(
        `Supplied beam check failed: ${problem.error?.code ?? response.status}: ${problem.error?.message ?? 'Request failed'}`,
      );
    }
    const envelope = await response.json() as APIResponse<BeamSuppliedCheckResultV2>;
    if (envelope.data.schema_version !== 'beam-supplied-check-result/v2') {
      throw new Error('Supplied beam check returned an incompatible result');
    }
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
