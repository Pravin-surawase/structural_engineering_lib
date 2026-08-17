import type { StructuralResultEnvelope } from '../../api/client';
import type { CatalogBeamValues } from '../catalog/types';

export interface WorkflowStepDefinition {
  step_id: 'input' | 'validate' | 'design' | 'review' | 'export';
  handler_id: string;
  position: number;
}

export interface WorkflowBinding {
  source: string;
  target: string;
  unit_contract: string;
}

export interface WorkflowDefinition {
  schema_version: '1.0';
  workflow_id: 'is456.beam.review';
  workflow_version: '1.1.0';
  title: string;
  capability_id: 'is456.beam.design';
  steps: WorkflowStepDefinition[];
  bindings: WorkflowBinding[];
  limits: {
    max_steps: 5;
    max_definition_bytes: 16384;
    max_input_bytes: 32768;
    max_output_bytes: 262144;
    max_timeout_ms: 2000;
    max_concurrency: 1;
    max_project_members: 1;
    max_batch_items: 1;
    max_cached_runs: 128;
  };
}

export interface WorkflowValidationResult {
  valid: true;
  workflow_id: 'is456.beam.review';
  normalized_definition: WorkflowDefinition;
  normalized_inputs: CatalogBeamValues;
}

export interface WorkflowStepResult {
  step_id: string;
  status: string;
  reason?: string | null;
  output?: Record<string, unknown> | null;
}

export interface WorkflowRunResult {
  run_id: string;
  workflow_id: 'is456.beam.review';
  status: 'COMPLETED' | 'REVIEW_REQUIRED' | 'UNSAFE' | 'CANCELLED' | 'TIMED_OUT';
  steps: WorkflowStepResult[];
  export: Record<string, unknown> | null;
  audit: { review_stop: string | null };
  result_envelope: StructuralResultEnvelope;
  definition_hash: string;
  input_hash: string;
  idempotent_replay: boolean;
}

export interface WorkflowDraft {
  schema_version: '2.0';
  definition: WorkflowDefinition;
  inputs: CatalogBeamValues;
  review_acknowledged: boolean;
}
