import type { CatalogBeamValues } from '../catalog/types';
import type { WorkflowDefinition, WorkflowDraft } from './types';

export const WORKFLOW_DRAFT_STORAGE_KEY = 'uix.beam-workflow-draft.v2';

const REQUIRED_INPUT_NAMES = [
  'width',
  'depth',
  'clear_cover',
  'stirrup_dia_mm',
  'main_bar_dia_mm',
  'moment',
  'shear',
  'fck',
  'fy',
] as const;

export function serializeWorkflowDraft(draft: WorkflowDraft): string {
  return JSON.stringify(draft);
}

export function parseWorkflowDraft(value: string): WorkflowDraft {
  const parsed = JSON.parse(value) as unknown;
  if (!parsed || typeof parsed !== 'object') throw new Error('Saved workflow must be an object');
  const record = parsed as Record<string, unknown>;
  if (record.schema_version !== '2.0') throw new Error('Saved workflow version is unsupported');
  const definition = record.definition as WorkflowDefinition | undefined;
  if (
    !definition
    || definition.workflow_id !== 'is456.beam.review'
    || definition.workflow_version !== '1.1.0'
  ) {
    throw new Error('Saved workflow identity is invalid');
  }
  const rawInputs = record.inputs;
  if (!rawInputs || typeof rawInputs !== 'object') throw new Error('Saved workflow inputs are invalid');
  const inputRecord = rawInputs as Record<string, unknown>;
  if (REQUIRED_INPUT_NAMES.some((name) => typeof inputRecord[name] !== 'number')) {
    throw new Error('Saved workflow inputs are incomplete');
  }
  if ('effective_depth' in inputRecord && typeof inputRecord.effective_depth !== 'number') {
    throw new Error('Saved workflow effective depth is invalid');
  }
  const inputs: CatalogBeamValues = {
    width: inputRecord.width as number,
    depth: inputRecord.depth as number,
    clear_cover: inputRecord.clear_cover as number,
    stirrup_dia_mm: inputRecord.stirrup_dia_mm as number,
    main_bar_dia_mm: inputRecord.main_bar_dia_mm as number,
    moment: inputRecord.moment as number,
    shear: inputRecord.shear as number,
    fck: inputRecord.fck as number,
    fy: inputRecord.fy as number,
  };
  if (typeof inputRecord.effective_depth === 'number') {
    inputs.effective_depth = inputRecord.effective_depth;
  }
  return {
    schema_version: '2.0',
    definition,
    inputs,
    review_acknowledged: record.review_acknowledged === true,
  };
}
