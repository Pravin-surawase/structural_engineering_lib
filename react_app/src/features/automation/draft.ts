import type { CatalogBeamValues } from '../catalog/types';
import type { WorkflowDefinition, WorkflowDraft } from './types';

export const WORKFLOW_DRAFT_STORAGE_KEY = 'uix.beam-workflow-draft.v1';

const INPUT_NAMES = ['width', 'depth', 'moment', 'shear', 'fck', 'fy'] as const;

export function serializeWorkflowDraft(draft: WorkflowDraft): string {
  return JSON.stringify(draft);
}

export function parseWorkflowDraft(value: string): WorkflowDraft {
  const parsed = JSON.parse(value) as unknown;
  if (!parsed || typeof parsed !== 'object') throw new Error('Saved workflow must be an object');
  const record = parsed as Record<string, unknown>;
  if (record.schema_version !== '1.0') throw new Error('Saved workflow version is unsupported');
  const definition = record.definition as WorkflowDefinition | undefined;
  if (!definition || definition.workflow_id !== 'is456.beam.review') {
    throw new Error('Saved workflow identity is invalid');
  }
  const rawInputs = record.inputs;
  if (!rawInputs || typeof rawInputs !== 'object') throw new Error('Saved workflow inputs are invalid');
  const inputRecord = rawInputs as Record<string, unknown>;
  if (INPUT_NAMES.some((name) => typeof inputRecord[name] !== 'number')) {
    throw new Error('Saved workflow inputs are incomplete');
  }
  return {
    schema_version: '1.0',
    definition,
    inputs: Object.fromEntries(
      INPUT_NAMES.map((name) => [name, inputRecord[name] as number]),
    ) as CatalogBeamValues,
    review_acknowledged: record.review_acknowledged === true,
  };
}
