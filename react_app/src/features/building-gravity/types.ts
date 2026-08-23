export type GravityOverallStatus =
  | 'BLOCKED'
  | 'ERROR'
  | 'NOT_EVALUATED'
  | 'STALE'
  | 'PASS'
  | 'FAIL'
  | 'HOLD';

export interface GravityResultEnvelope {
  overall_status: GravityOverallStatus;
  qualified_review_required: boolean;
  review_status: 'QUALIFIED_REVIEW_REQUIRED' | 'REVIEWED_ACCEPTED' | 'REVIEWED_REJECTED';
  issues: Array<{ code: string; path: string; message: string }>;
}

export interface GravityAction {
  action_id: string;
  component_id: string;
  kind: 'SLAB' | 'BEAM' | 'COLUMN' | 'FOOTING';
  combination_id: 'SERVICE_DL_LL' | 'ULS_1_5_DL_LL';
  area_load_kn_m2: number | null;
  line_load_kn_m: number | null;
  moment_knm: number | null;
  shear_kn: number | null;
  axial_kn: number | null;
}

export interface GravityComponentResult {
  component_id: string;
  kind: 'SLAB' | 'BEAM' | 'COLUMN' | 'FOOTING';
  canonical_function: string;
  result_envelope: GravityResultEnvelope;
  result: Record<string, unknown> | null;
}

export interface GravityWorkflowResult {
  schema_version: 'gravity-workflow-result/v1';
  model_hash: string;
  load_model_hash: string;
  ledger_hash: string;
  workflow_result_hash: string;
  actions: GravityAction[];
  components: GravityComponentResult[];
  result_envelope: GravityResultEnvelope;
  limitations: string[];
}

export interface GravityCalculationBook {
  schema_version: 'gravity-calculation-book/v1';
  workflow_result_hash: string;
  reconciliation: {
    all_balanced: boolean;
    boundary_count: number;
    maximum_absolute_residual_kn: number;
    balance_tolerance_kn: number;
    accepted_entry_count: number;
    blocked_entry_count: number;
  };
  approved_exclusions: Array<{ category: string; reason: string }>;
  limitations: string[];
  issues: Array<{ code: string; path: string; message: string }>;
  review_disposition: 'QUALIFIED_REVIEW_REQUIRED';
}

export interface GravityWorkflowRunBundle {
  schema_version: 'gravity-workflow-run-bundle/v1';
  workflow_result: GravityWorkflowResult;
  calculation_book: GravityCalculationBook;
}

export interface GravityWorkflowDefinition {
  schema_version: 'gravity-workflow-definition/v1';
  capability_id: 'building.gravity.dead-live.v1';
  title: string;
  summary: string;
  accepted_topology: string[];
  component_adapters: Record<string, string>;
  product_surfaces: Record<string, string>;
  example_request: Record<string, unknown>;
  exclusions: string[];
  qualified_review_required: true;
}
