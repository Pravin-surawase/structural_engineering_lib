export type CatalogScalar = string | number | boolean | null;

export type CatalogBeamTransportName =
  | 'width'
  | 'depth'
  | 'moment'
  | 'shear'
  | 'fck'
  | 'fy';

export interface CatalogField {
  field_id: string;
  transport_name: CatalogBeamTransportName;
  semantic_ref: string;
  label: string;
  group: string;
  widget: 'number' | 'select';
  unit: string;
  required: boolean;
  default: CatalogScalar;
  minimum: number | null;
  maximum: number | null;
  choices: CatalogScalar[];
}

export interface CatalogExample {
  name: string;
  values: Array<[string, CatalogScalar]>;
}

export interface WorkflowCapability {
  capability_id: 'is456.beam.design';
  capability_version: '1.1.0';
  element: 'beam';
  title: string;
  summary: string;
  semantic_workflow_id: 'design_beam_is456';
  service_adapter_id: 'fastapi.design_beam.v1';
  request_schema_id: 'fastapi.BeamDesignRequest.v1';
  result_schema_id: 'fastapi.BeamDesignResponse.v1';
  status_semantic_ref: string;
  fields: CatalogField[];
  prerequisites: string[];
  next_actions: string[];
  visualization_affordances: string[];
  examples: CatalogExample[];
  limitations: string[];
  qualified_review_required: boolean;
}

export interface WorkflowCatalog {
  schema_version: '1.0';
  catalog_version: '1.1.0';
  code_edition: 'IS 456:2000';
  compatible_versions: string[];
  capabilities: WorkflowCapability[];
}

export type CatalogBeamValues = Record<CatalogBeamTransportName, number>;
