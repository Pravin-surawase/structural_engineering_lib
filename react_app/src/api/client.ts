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
  shear: number;
  torsion?: number;
  fck: number;
  fy: number;
  clear_cover: number;
  stirrup_dia_mm: number;
  main_bar_dia_mm: number;
  effective_depth?: number;
  include_serviceability?: boolean;
  span_mm?: number;
  support_condition?: string;
  crack_width_params?: Partial<BeamCrackWidthParams>;
}

export interface BeamCrackWidthParams {
  exposure_class: 'mild' | 'moderate' | 'severe' | 'very_severe';
  limit_mm?: number;
  acr_mm: number;
  cmin_mm: number;
  h_mm: number;
  x_mm: number;
  epsilon_m?: number;
  fs_service_nmm2?: number;
  es_nmm2?: number;
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
  asv_required_unit: 'mm²/mm';
  stirrup_spacing: number;
  sv_max: number;
  shear_capacity: number;
}

export interface DeflectionCheckResult {
  is_ok: boolean;
  span_depth_actual: number | null;
  span_depth_allowable: number | null;
  remarks: string;
}

export interface CrackWidthCheckResult {
  is_ok: boolean;
  crack_width_mm: number | null;
  crack_width_limit_mm: number | null;
  remarks: string;
}

export interface CombinedBeamActions {
  mu_knm: number;
  vu_kn: number;
  tu_knm: number;
  me_knm: number;
  ve_kn: number;
}

export interface IntegratedTorsionResult {
  source: 'IS 456:2000';
  is_safe: boolean;
  tau_ve: number;
  tau_c: number;
  tau_c_max: number;
  asv_torsion: number;
  asv_shear: number;
  asv_total: number;
  stirrup_spacing: number;
  al_torsion: number;
  requires_closed_stirrups: boolean;
  errors: Array<Record<string, unknown>>;
  clause_refs: Record<string, string>;
}

export interface StructuralResultEnvelope {
  schema_version: 'structural-result-envelope/v2';
  intake_status: 'VALID' | 'PARTIAL' | 'BLOCKED';
  calculation_status: 'NOT_EVALUATED' | 'COMPLETED' | 'ERROR';
  engineering_status: 'NOT_EVALUATED' | 'PASS' | 'FAIL' | 'HOLD';
  review_status: 'QUALIFIED_REVIEW_REQUIRED' | 'REVIEWED_ACCEPTED' | 'REVIEWED_REJECTED';
  qualified_review_required: boolean;
  freshness_status: 'CURRENT' | 'STALE';
  serviceability_escalation: string | null;
  overall_status: 'BLOCKED' | 'ERROR' | 'NOT_EVALUATED' | 'STALE' | 'PASS' | 'FAIL' | 'HOLD';
  issues: Array<{ code: string; path: string; message: string }>;
  result_identity: {
    contract_version: string;
    library_version: string;
    input_hash: string | null;
    calculation_identity: string | null;
    artifact_sha256: string | null;
  } | null;
}

export interface EffectiveDepthResolution {
  contract_version: 'effective-depth-basis/v1';
  source: 'EXPLICIT' | 'DERIVED';
  D_mm: number;
  d_mm: number;
  effective_depth_basis: {
    clear_cover_mm: number;
    stirrup_diameter_mm: number;
    tension_bar_diameter_mm: number;
  } | { centroid_cover_mm: number } | null;
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
  effective_depth_basis?: EffectiveDepthResolution;
  result_envelope: StructuralResultEnvelope;
  deflection_check?: DeflectionCheckResult | null;
  crack_width_check?: CrackWidthCheckResult | null;
  combined_actions?: CombinedBeamActions | null;
  torsion?: IntegratedTorsionResult | null;
  holds?: string[];
  warnings?: string[];
  evidence?: EvidenceEnvelope | null;
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
  effective_depth_resolution: EffectiveDepthResolution;
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
  result_envelope: StructuralResultEnvelope;
  limitations: string[];
}

export interface EvidenceEnvelope {
  artifact_schema: string;
  artifact_schema_version: string;
  library_version: string;
  library_content_identity: string;
  code_edition: string;
  code_amendment_identity: string;
  amendment_applicability: string;
  amendment_applicability_review_id: string | null;
  controlled_source_ids: string[];
  controlled_source_basis_hash: string;
  capability_id: string;
  support_status: 'SUPPORTED' | 'HELD';
  unit_system: string;
  explicit_units: Record<string, string>;
  normalized_input_hash: string;
  provenance_hash: string;
  source_metadata: Record<string, unknown>;
  calculation_identity: string;
  replay_receipt: Record<string, unknown>;
  replay_receipt_hash: string;
  governing_check: string;
  exact_utilization: number | null;
  margin: number | null;
  status: 'PASS' | 'FAIL' | 'HOLD';
  generated_at: string;
  qualified_review_required: boolean;
  qualified_review_requirement: string;
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

export interface RequestOptions {
  signal?: AbortSignal;
}

/**
 * Unwrap FastAPI's standard response envelope.
 * All /api/v1/* endpoints return: {"success": true, "data": <actual payload>}
 * This extracts the inner payload so callers get the type they expect.
 */
function unwrapResponse<T>(json: unknown): T {
  if (
    json !== null &&
    typeof json === 'object' &&
    'data' in json &&
    'success' in json
  ) {
    return (json as { data: T }).data;
  }
  // Return as-is for endpoints that don't wrap (e.g., /health)
  return json as T;
}

export { unwrapResponse };

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function hasFiniteNumberFields(
  value: Record<string, unknown>,
  fields: readonly string[],
): boolean {
  return fields.every(
    (field) => typeof value[field] === 'number' && Number.isFinite(value[field]),
  );
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === 'string');
}

function isIssueArray(value: unknown, requirePath: boolean): boolean {
  return Array.isArray(value) && value.every(
    (issue) => isRecord(issue)
      && typeof issue.code === 'string'
      && typeof issue.message === 'string'
      && (!requirePath || typeof issue.path === 'string'),
  );
}

function isStringMap(value: unknown, nullableValues = false): boolean {
  return isRecord(value) && Object.values(value).every(
    (item) => typeof item === 'string' || (nullableValues && item === null),
  );
}

export function parseStructuralResultEnvelope(
  value: unknown,
): StructuralResultEnvelope {
  if (!isRecord(value) || value.schema_version !== 'structural-result-envelope/v2') {
    throw new Error('Structural result envelope is missing or unsupported');
  }
  const validIntake = ['VALID', 'PARTIAL', 'BLOCKED'].includes(String(value.intake_status));
  const validCalculation = ['NOT_EVALUATED', 'COMPLETED', 'ERROR'].includes(
    String(value.calculation_status),
  );
  const validEngineering = ['NOT_EVALUATED', 'PASS', 'FAIL', 'HOLD'].includes(
    String(value.engineering_status),
  );
  const validReview = [
    'QUALIFIED_REVIEW_REQUIRED',
    'REVIEWED_ACCEPTED',
    'REVIEWED_REJECTED',
  ].includes(String(value.review_status));
  const validFreshness = ['CURRENT', 'STALE'].includes(String(value.freshness_status));
  const validOverall = [
    'BLOCKED',
    'ERROR',
    'NOT_EVALUATED',
    'STALE',
    'PASS',
    'FAIL',
    'HOLD',
  ].includes(String(value.overall_status));
  const identity = value.result_identity;
  const validIdentity = identity === null || (
    isRecord(identity)
    && typeof identity.contract_version === 'string'
    && typeof identity.library_version === 'string'
    && (identity.input_hash === null || typeof identity.input_hash === 'string')
    && (
      identity.calculation_identity === null
      || typeof identity.calculation_identity === 'string'
    )
    && (identity.artifact_sha256 === null || typeof identity.artifact_sha256 === 'string')
  );
  if (
    !validIntake
    || !validCalculation
    || !validEngineering
    || !validReview
    || !validFreshness
    || !validOverall
    || !Array.isArray(value.issues)
    || value.issues.some(
      (issue) => !isRecord(issue)
        || typeof issue.code !== 'string'
        || typeof issue.path !== 'string'
        || typeof issue.message !== 'string',
    )
    || !validIdentity
    || typeof value.qualified_review_required !== 'boolean'
    || (
      value.serviceability_escalation !== null
      && typeof value.serviceability_escalation !== 'string'
    )
  ) {
    throw new Error('Structural result envelope has invalid canonical status fields');
  }
  const expectedOverall = value.intake_status === 'BLOCKED'
    ? 'BLOCKED'
    : value.calculation_status === 'ERROR'
      ? 'ERROR'
      : value.freshness_status === 'STALE'
        ? 'STALE'
        : value.intake_status === 'PARTIAL'
          ? 'HOLD'
          : value.calculation_status === 'NOT_EVALUATED'
            ? 'NOT_EVALUATED'
            : value.engineering_status === 'PASS'
              ? 'PASS'
              : value.engineering_status === 'FAIL'
                ? 'FAIL'
                : 'HOLD';
  const reviewRequiresQualification = value.review_status === 'QUALIFIED_REVIEW_REQUIRED';
  if (
    value.overall_status !== expectedOverall
    || value.qualified_review_required !== reviewRequiresQualification
  ) {
    throw new Error('Structural result envelope has contradictory canonical status fields');
  }
  return value as unknown as StructuralResultEnvelope;
}

function parseBeamDesignResponse(value: unknown): BeamDesignResponse {
  if (!isRecord(value)) throw new Error('Beam design response must be an object');
  const depth = value.effective_depth_basis;
  const depthBasis = isRecord(depth) ? depth.effective_depth_basis : null;
  const validDerivedBasis = isRecord(depthBasis)
    && typeof depthBasis.clear_cover_mm === 'number'
    && Number.isFinite(depthBasis.clear_cover_mm)
    && depthBasis.clear_cover_mm > 0
    && typeof depthBasis.stirrup_diameter_mm === 'number'
    && Number.isFinite(depthBasis.stirrup_diameter_mm)
    && depthBasis.stirrup_diameter_mm > 0
    && typeof depthBasis.tension_bar_diameter_mm === 'number'
    && Number.isFinite(depthBasis.tension_bar_diameter_mm)
    && depthBasis.tension_bar_diameter_mm > 0;
  if (
    !isRecord(depth)
    || depth.contract_version !== 'effective-depth-basis/v1'
    || (depth.source !== 'EXPLICIT' && depth.source !== 'DERIVED')
    || typeof depth.d_mm !== 'number'
    || !Number.isFinite(depth.d_mm)
    || typeof depth.D_mm !== 'number'
    || !Number.isFinite(depth.D_mm)
    || depth.d_mm <= 0
    || depth.D_mm <= depth.d_mm
    || (depth.source === 'EXPLICIT' && depthBasis !== null)
    || (depth.source === 'DERIVED' && !validDerivedBasis)
    || (
      typeof value.effective_depth_used === 'number'
      && value.effective_depth_used !== depth.d_mm
    )
  ) {
    throw new Error('Beam design response has no valid effective-depth record');
  }
  return {
    ...value,
    effective_depth_basis: depth,
    result_envelope: parseStructuralResultEnvelope(value.result_envelope),
  } as unknown as BeamDesignResponse;
}

export function parseBeamSuppliedCheckResult(
  value: unknown,
): BeamSuppliedCheckResultV2 {
  const request = isRecord(value) && isRecord(value.request) ? value.request : null;
  const requestIdentity = request && isRecord(request.identity) ? request.identity : null;
  const requestSection = request && isRecord(request.section) ? request.section : null;
  const requestActions = request && isRecord(request.actions) ? request.actions : null;
  const identity = isRecord(value) && isRecord(value.identity) ? value.identity : null;
  const depth = isRecord(value) && isRecord(value.effective_depth_resolution)
    ? value.effective_depth_resolution
    : null;
  const longitudinal = isRecord(value) && isRecord(value.longitudinal)
    ? value.longitudinal
    : null;
  const shear = isRecord(value) && isRecord(value.shear) ? value.shear : null;
  if (
    !isRecord(value)
    || value.schema_version !== 'beam-supplied-check-result/v2'
    || typeof value.correlation_id !== 'string'
    || !['PASS', 'FAIL', 'HOLD', 'ERROR'].includes(String(value.status))
    || request === null
    || request.schema_version !== 'beam-supplied-check/v2'
    || request.correlation_id !== value.correlation_id
    || requestIdentity === null
    || !['member_id', 'story', 'case_id'].every(
      (field) => typeof requestIdentity[field] === 'string',
    )
    || requestSection === null
    || !hasFiniteNumberFields(requestSection, ['b_mm', 'D_mm'])
    || !isRecord(request.materials)
    || !hasFiniteNumberFields(
      request.materials,
      ['fck_nmm2', 'fy_nmm2', 'fy_transverse_nmm2'],
    )
    || requestActions === null
    || !hasFiniteNumberFields(requestActions, ['mu_knm', 'vu_kn'])
    || !['TOP', 'BOTTOM'].includes(String(requestActions.primary_tension_face))
    || !isRecord(request.reinforcement)
    || !isRecord(request.selection)
    || identity === null
    || !['member_id', 'story', 'case_id'].every(
      (field) => identity[field] === requestIdentity[field],
    )
    || value.primary_tension_face !== requestActions.primary_tension_face
    || depth === null
    || depth.contract_version !== 'effective-depth-basis/v1'
    || !['EXPLICIT', 'DERIVED'].includes(String(depth.source))
    || !hasFiniteNumberFields(depth, ['D_mm', 'd_mm'])
    || depth.D_mm !== requestSection.D_mm
    || (depth.effective_depth_basis !== null && !isRecord(depth.effective_depth_basis))
    || typeof value.d_dash_used_mm !== 'number'
    || !Number.isFinite(value.d_dash_used_mm)
    || longitudinal === null
    || longitudinal.schema_version !== 'beam-reinforcement-evaluation/v1'
    || !['PASS', 'FAIL', 'HOLD'].includes(String(longitudinal.status))
    || !hasFiniteNumberFields(longitudinal, ['ast_required_mm2', 'asc_required_mm2'])
    || !isRecord(longitudinal.checks)
    || !isIssueArray(longitudinal.issues, false)
    || !isStringMap(longitudinal.clause_refs)
    || !isStringMap(longitudinal.provenance, true)
    || !isStringArray(longitudinal.limitations)
    || longitudinal.qualified_review_required !== true
    || shear === null
    || shear.schema_version !== 'beam-supplied-shear-check/v2'
    || !['PASS', 'FAIL'].includes(String(shear.status))
    || !hasFiniteNumberFields(shear, [
      'required_Vus_kn',
      'concrete_capacity_kn',
      'provided_stirrup_capacity_kn',
      'total_capacity_kn',
      'provided_asv_mm2',
      'provided_spacing_mm',
      'maximum_permitted_spacing_mm',
      'utilization',
    ])
    || !['spacing_is_adequate', 'capacity_is_adequate', 'section_shear_is_adequate']
      .every((field) => typeof shear[field] === 'boolean')
    || !isIssueArray(shear.issues, true)
    || !isStringMap(shear.clause_refs)
    || !isStringArray(value.limitations)
  ) {
    throw new Error('Supplied beam check result is missing or incompatible');
  }
  const resultEnvelope = parseStructuralResultEnvelope(value.result_envelope);
  if (
    value.status !== 'ERROR'
    && resultEnvelope.engineering_status !== value.status
  ) {
    throw new Error('Supplied beam check has contradictory terminal status');
  }
  if (
    (value.status === 'PASS'
      && (longitudinal.status !== 'PASS' || shear.status !== 'PASS'))
    || (value.status === 'FAIL'
      && longitudinal.status !== 'FAIL' && shear.status !== 'FAIL')
    || (value.status === 'HOLD' && longitudinal.status !== 'HOLD')
  ) {
    throw new Error('Supplied beam check has contradictory component status');
  }
  return {
    ...value,
    result_envelope: resultEnvelope,
  } as unknown as BeamSuppliedCheckResultV2;
}

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
export function designBeam(params: BeamDesignRequest): Promise<BeamDesignResponse>;
export function designBeam(
  params: BeamDesignRequest,
  options: RequestOptions,
): Promise<BeamDesignResponse>;
export async function designBeam(
  params: BeamDesignRequest,
  options?: RequestOptions,
): Promise<BeamDesignResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/design/beam`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
    ...(options?.signal ? { signal: options.signal } : {}),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    const code = error?.error?.code ?? response.status;
    const message = error?.error?.message ?? error?.detail ?? response.status;
    throw new Error(`Design failed: ${code}: ${message}`);
  }

  const payload = unwrapResponse<unknown>(await response.json());
  return parseBeamDesignResponse(payload);
}

export function checkSuppliedBeam(
  request: BeamSuppliedCheckRequestV2,
): Promise<BeamSuppliedCheckResultV2>;
export function checkSuppliedBeam(
  request: BeamSuppliedCheckRequestV2,
  options: RequestOptions,
): Promise<BeamSuppliedCheckResultV2>;
export async function checkSuppliedBeam(
  request: BeamSuppliedCheckRequestV2,
  options?: RequestOptions,
): Promise<BeamSuppliedCheckResultV2> {
  const response = await fetch(`${API_BASE_URL}/api/v1/design/beam/check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
    ...(options?.signal ? { signal: options.signal } : {}),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    const code = error?.error?.code ?? response.status;
    const message = error?.error?.message ?? error?.detail ?? response.status;
    throw new Error(`Supplied beam check failed: ${code}: ${message}`);
  }
  return parseBeamSuppliedCheckResult(
    unwrapResponse<unknown>(await response.json()),
  );
}

/**
 * Generate 3D beam geometry for visualization.
 */
export async function generateBeamGeometry(
  request: Geometry3DRequest,
  options?: RequestOptions,
): Promise<Geometry3DResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/geometry/beam/3d`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
    ...(options?.signal ? { signal: options.signal } : {}),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Geometry generation failed: ${error.detail || response.status}`);
  }

  return response.json().then(unwrapResponse<Geometry3DResponse>);
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
  source_id: string;
  story: string;
  width_mm: number;
  depth_mm: number;
  span_mm: number;
  mu_knm: number;
  vu_kn: number;
  fck_mpa: number;
  fy_mpa: number;
  cover_mm: number;
  source_metadata: Record<string, unknown>;
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
  dataset: SampleDatasetEvidence;
}

export interface SampleDatasetEvidence {
  dataset_id: string;
  dataset_version: string;
  dataset_sha256: string;
  hash_algorithm: string;
  source_files: string[];
  beam_count: number;
}

export async function loadSampleData(): Promise<SampleDataResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/import/sample`);
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(`Sample data load failed: ${error.detail || response.status}`);
  }
  return response.json().then(unwrapResponse<SampleDataResponse>);
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

  return response.json().then(unwrapResponse<TorsionDesignResponse>);
}

// =============================================================================
// Load Analysis Types
// =============================================================================

export interface LoadItem {
  load_type: 'udl' | 'point';
  magnitude: number;
  position_mm?: number;
  end_position_mm?: number;
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

  return response.json().then(unwrapResponse<LoadAnalysisResponse>);
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
  flexural_utilization: number;
  shear_utilization: number;
  stirrup_utilization: number;
  shear_tau_v_nmm2: number;
  shear_tau_c_nmm2: number;
  shear_tau_c_max_nmm2: number;
  stirrup_spacing_mm: number;
  shear_reinforcement_area_mm2: number;
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
  asv_mm2?: number;
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
  limitations: string[];
}

/**
 * Find Pareto-optimal flexure-and-shear-feasible beam designs.
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

  return response.json().then(unwrapResponse<ParetoResponse>);
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
