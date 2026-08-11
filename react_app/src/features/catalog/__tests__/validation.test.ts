import { describe, expect, it } from 'vitest';
import { parseWorkflowCatalog } from '../validation';

const VALID_CATALOG = {
  schema_version: '1.0',
  catalog_version: '1.1.0',
  code_edition: 'IS 456:2000',
  compatible_versions: ['1.0', '1.0.0', '1.1.0'],
  capabilities: [{
    capability_id: 'is456.beam.design',
    capability_version: '1.1.0',
    element: 'beam',
    title: 'Beam design',
    summary: 'One beam',
    semantic_workflow_id: 'design_beam_is456',
    service_adapter_id: 'fastapi.design_beam.v1',
    request_schema_id: 'fastapi.BeamDesignRequest.v1',
    result_schema_id: 'fastapi.BeamDesignResponse.v1',
    status_semantic_ref: 'workflows.design_beam_is456.statuses.is_ok',
    fields: [{
      field_id: 'b_mm',
      transport_name: 'width',
      semantic_ref: 'workflows.design_beam_is456.fields.b_mm',
      label: 'Width',
      group: 'Dimensions',
      widget: 'number',
      unit: 'mm',
      required: true,
      default: 300,
      minimum: 150,
      maximum: 2000,
      choices: [],
    }],
    prerequisites: [],
    next_actions: [],
    visualization_affordances: [],
    examples: [],
    limitations: ['Qualified review required.'],
    qualified_review_required: true,
  }],
};

describe('parseWorkflowCatalog', () => {
  it('accepts the approved version and field registry', () => {
    expect(parseWorkflowCatalog(VALID_CATALOG).capabilities[0].fields[0].transport_name).toBe('width');
  });

  it('fails visibly on unknown versions and fields', () => {
    expect(() => parseWorkflowCatalog({ ...VALID_CATALOG, catalog_version: '2.0.0' }))
      .toThrow("Unsupported catalogue version '2.0.0'");
    const capability = VALID_CATALOG.capabilities[0];
    const invalid = {
      ...VALID_CATALOG,
      capabilities: [{
        ...capability,
        fields: [{ ...capability.fields[0], field_id: 'invented' }],
      }],
    };
    expect(() => parseWorkflowCatalog(invalid)).toThrow("Unsupported catalogue field 'invented'");
  });
});
