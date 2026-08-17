import { describe, expect, it } from 'vitest';
import { parseWorkflowCatalog } from '../validation';

function field(
  fieldId: string,
  transportName: string,
  defaultValue: number | null,
) {
  return {
    field_id: fieldId,
    transport_name: transportName,
    semantic_ref: `workflows.design_beam_is456.fields.${fieldId}`,
    label: fieldId,
    group: 'Inputs',
    widget: 'number',
    unit: 'mm',
    required: fieldId === 'b_mm' || fieldId === 'D_mm' || fieldId === 'mu_knm',
    default: defaultValue,
    minimum: 0,
    maximum: 3000,
    choices: [],
  };
}

const VALID_CATALOG = {
  schema_version: '1.0',
  catalog_version: '1.2.0',
  code_edition: 'IS 456:2000',
  compatible_versions: ['1.0', '1.0.0', '1.1.0', '1.2.0'],
  capabilities: [{
    capability_id: 'is456.beam.design',
    capability_version: '1.2.0',
    element: 'beam',
    title: 'Beam design',
    summary: 'One beam',
    semantic_workflow_id: 'design_beam_is456',
    service_adapter_id: 'fastapi.design_beam.v1',
    request_schema_id: 'fastapi.BeamDesignRequest.v1',
    result_schema_id: 'fastapi.BeamDesignResponse.v2',
    status_semantic_ref: 'workflows.design_beam_is456.statuses.result_envelope.engineering_status',
    fields: [
      field('b_mm', 'width', 300),
      field('d_mm', 'effective_depth', null),
      field('D_mm', 'depth', 500),
      field('clear_cover_mm', 'clear_cover', 25),
      field('stirrup_dia_mm', 'stirrup_dia_mm', 8),
      field('main_bar_dia_mm', 'main_bar_dia_mm', 20),
      field('mu_knm', 'moment', 150),
      field('vu_kn', 'shear', 75),
      field('fck_nmm2', 'fck', 25),
      field('fy_nmm2', 'fy', 500),
    ],
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
    expect(parseWorkflowCatalog(VALID_CATALOG).capabilities[0].fields[1].default).toBeNull();
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
    expect(() => parseWorkflowCatalog({
      ...VALID_CATALOG,
      capabilities: [{
        ...capability,
        fields: capability.fields.slice(0, -1),
      }],
    })).toThrow('Catalogue field registry is incomplete');
    expect(() => parseWorkflowCatalog({
      ...VALID_CATALOG,
      capabilities: [{ ...capability, qualified_review_required: false }],
    })).toThrow('qualified-review boundary');
  });
});
