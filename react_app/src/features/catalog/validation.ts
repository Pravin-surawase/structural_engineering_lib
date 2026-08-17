import type {
  CatalogBeamTransportName,
  CatalogField,
  WorkflowCapability,
  WorkflowCatalog,
} from './types';

const SUPPORTED_FIELD_IDS = new Set([
  'b_mm',
  'D_mm',
  'd_mm',
  'clear_cover_mm',
  'stirrup_dia_mm',
  'main_bar_dia_mm',
  'mu_knm',
  'vu_kn',
  'fck_nmm2',
  'fy_nmm2',
]);
const SUPPORTED_TRANSPORT_NAMES = new Set<CatalogBeamTransportName>([
  'width',
  'depth',
  'effective_depth',
  'clear_cover',
  'stirrup_dia_mm',
  'main_bar_dia_mm',
  'moment',
  'shear',
  'fck',
  'fy',
]);

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function requireString(record: Record<string, unknown>, key: string): string {
  const value = record[key];
  if (typeof value !== 'string' || value.length === 0) {
    throw new Error(`Catalogue field '${key}' must be non-empty text`);
  }
  return value;
}

function requireStringArray(record: Record<string, unknown>, key: string): string[] {
  const value = record[key];
  if (!Array.isArray(value) || value.some((item) => typeof item !== 'string')) {
    throw new Error(`Catalogue field '${key}' must be a text array`);
  }
  return value;
}

function parseField(value: unknown): CatalogField {
  if (!isRecord(value)) throw new Error('Catalogue field must be an object');
  const fieldId = requireString(value, 'field_id');
  const transportName = requireString(value, 'transport_name');
  const widget = requireString(value, 'widget');
  if (!SUPPORTED_FIELD_IDS.has(fieldId)) {
    throw new Error(`Unsupported catalogue field '${fieldId}'`);
  }
  if (!SUPPORTED_TRANSPORT_NAMES.has(transportName as CatalogBeamTransportName)) {
    throw new Error(`Unsupported transport field '${transportName}'`);
  }
  if (widget !== 'number' && widget !== 'select') {
    throw new Error(`Unsupported widget '${widget}' for '${fieldId}'`);
  }
  const defaultValue = value.default;
  if (defaultValue !== null && typeof defaultValue !== 'number') {
    throw new Error(`Catalogue default for '${fieldId}' must be numeric or null`);
  }
  const choices = value.choices;
  if (!Array.isArray(choices)) {
    throw new Error(`Catalogue choices for '${fieldId}' must be an array`);
  }
  const minimum = value.minimum;
  const maximum = value.maximum;
  if (minimum !== null && typeof minimum !== 'number') {
    throw new Error(`Catalogue minimum for '${fieldId}' is invalid`);
  }
  if (maximum !== null && typeof maximum !== 'number') {
    throw new Error(`Catalogue maximum for '${fieldId}' is invalid`);
  }
  if (typeof value.required !== 'boolean') {
    throw new Error(`Catalogue required flag for '${fieldId}' is invalid`);
  }
  return {
    field_id: fieldId,
    transport_name: transportName as CatalogBeamTransportName,
    semantic_ref: requireString(value, 'semantic_ref'),
    label: requireString(value, 'label'),
    group: requireString(value, 'group'),
    widget,
    unit: requireString(value, 'unit'),
    required: value.required,
    default: defaultValue,
    minimum,
    maximum,
    choices: choices as CatalogField['choices'],
  };
}

function parseCapability(value: unknown): WorkflowCapability {
  if (!isRecord(value)) throw new Error('Catalogue capability must be an object');
  if (value.capability_id !== 'is456.beam.design') {
    throw new Error(`Unsupported capability '${String(value.capability_id)}'`);
  }
  if (value.element !== 'beam') {
    throw new Error(`Unsupported catalogue element '${String(value.element)}'`);
  }
  if (value.capability_version !== '1.2.0') {
    throw new Error(`Unsupported capability version '${String(value.capability_version)}'`);
  }
  if (value.semantic_workflow_id !== 'design_beam_is456') {
    throw new Error('Catalogue semantic workflow does not match the approved beam adapter');
  }
  if (
    value.service_adapter_id !== 'fastapi.design_beam.v1' ||
    value.request_schema_id !== 'fastapi.BeamDesignRequest.v1' ||
    value.result_schema_id !== 'fastapi.BeamDesignResponse.v2'
  ) {
    throw new Error('Catalogue references an unapproved transport contract');
  }
  if (!Array.isArray(value.fields)) throw new Error('Catalogue fields must be an array');
  const fields = value.fields.map(parseField);
  if (new Set(fields.map((field) => field.transport_name)).size !== fields.length) {
    throw new Error('Catalogue contains duplicate transport fields');
  }
  const fieldIds = new Set(fields.map((field) => field.field_id));
  if (
    fieldIds.size !== SUPPORTED_FIELD_IDS.size
    || [...SUPPORTED_FIELD_IDS].some((fieldId) => !fieldIds.has(fieldId))
  ) {
    throw new Error('Catalogue field registry is incomplete');
  }
  if (
    value.status_semantic_ref
    !== 'workflows.design_beam_is456.statuses.result_envelope.engineering_status'
  ) {
    throw new Error('Catalogue status does not use the canonical result envelope');
  }
  if (value.qualified_review_required !== true) {
    throw new Error('Catalogue must preserve the qualified-review boundary');
  }
  return {
    capability_id: value.capability_id,
    capability_version: value.capability_version,
    element: 'beam',
    title: requireString(value, 'title'),
    summary: requireString(value, 'summary'),
    semantic_workflow_id: value.semantic_workflow_id,
    service_adapter_id: value.service_adapter_id,
    request_schema_id: value.request_schema_id,
    result_schema_id: value.result_schema_id,
    status_semantic_ref: value.status_semantic_ref,
    fields,
    prerequisites: requireStringArray(value, 'prerequisites'),
    next_actions: requireStringArray(value, 'next_actions'),
    visualization_affordances: requireStringArray(value, 'visualization_affordances'),
    examples: Array.isArray(value.examples) ? value.examples as WorkflowCapability['examples'] : [],
    limitations: requireStringArray(value, 'limitations'),
    qualified_review_required: true,
  };
}

export function parseWorkflowCatalog(value: unknown): WorkflowCatalog {
  if (!isRecord(value)) throw new Error('Workflow catalogue response must be an object');
  if (value.schema_version !== '1.0') {
    throw new Error(`Unsupported catalogue schema '${String(value.schema_version)}'`);
  }
  if (value.catalog_version !== '1.2.0') {
    throw new Error(`Unsupported catalogue version '${String(value.catalog_version)}'`);
  }
  if (value.code_edition !== 'IS 456:2000') {
    throw new Error(`Unsupported code edition '${String(value.code_edition)}'`);
  }
  if (!Array.isArray(value.capabilities) || value.capabilities.length !== 1) {
    throw new Error('The beam slice requires exactly one approved capability');
  }
  return {
    schema_version: value.schema_version,
    catalog_version: value.catalog_version,
    code_edition: value.code_edition,
    compatible_versions: requireStringArray(value, 'compatible_versions'),
    capabilities: value.capabilities.map(parseCapability),
  };
}
