import { describe, expect, it } from 'vitest';
import { parseWorkflowDraft, serializeWorkflowDraft } from '../draft';
import type { WorkflowDraft } from '../types';

const DRAFT: WorkflowDraft = {
  schema_version: '2.0',
  definition: {
    schema_version: '1.0',
    workflow_id: 'is456.beam.review',
    workflow_version: '1.1.0',
    title: 'Beam workflow',
    capability_id: 'is456.beam.design',
    steps: [],
    bindings: [],
    limits: {
      max_steps: 5,
      max_definition_bytes: 16384,
      max_input_bytes: 32768,
      max_output_bytes: 262144,
      max_timeout_ms: 2000,
      max_concurrency: 1,
      max_project_members: 1,
      max_batch_items: 1,
      max_cached_runs: 128,
    },
  },
  inputs: {
    width: 300,
    depth: 500,
    clear_cover: 25,
    stirrup_dia_mm: 8,
    main_bar_dia_mm: 20,
    moment: 150,
    shear: 75,
    fck: 25,
    fy: 500,
  },
  review_acknowledged: false,
};

describe('workflow draft', () => {
  it('round trips deterministically', () => {
    const encoded = serializeWorkflowDraft(DRAFT);
    expect(parseWorkflowDraft(encoded)).toEqual(DRAFT);
    expect(serializeWorkflowDraft(parseWorkflowDraft(encoded))).toBe(encoded);
  });

  it('fails closed on corrupt identity and incomplete inputs', () => {
    expect(() => parseWorkflowDraft('{"schema_version":"1.0"}')).toThrow('unsupported');
    expect(() => parseWorkflowDraft(JSON.stringify({
      ...DRAFT,
      definition: { ...DRAFT.definition, workflow_version: '1.0.0' },
    }))).toThrow('identity is invalid');
    expect(() => parseWorkflowDraft(JSON.stringify({ ...DRAFT, inputs: { width: 300 } })))
      .toThrow('incomplete');
  });
});
