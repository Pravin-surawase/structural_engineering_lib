"""Typed transport models for the application workflow catalogue."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class CatalogFieldModel(BaseModel):
    field_id: str
    transport_name: str
    semantic_ref: str
    label: str
    group: str
    widget: Literal["number", "select"]
    unit: str
    required: bool
    default: str | int | float | bool | None
    minimum: float | None = None
    maximum: float | None = None
    choices: list[str | int | float | bool | None]


class CatalogExampleModel(BaseModel):
    name: str
    values: list[tuple[str, str | int | float | bool | None]]


class WorkflowCapabilityModel(BaseModel):
    capability_id: str
    capability_version: str
    element: str
    title: str
    summary: str
    semantic_workflow_id: str
    service_adapter_id: str
    request_schema_id: str
    result_schema_id: str
    status_semantic_ref: str
    fields: list[CatalogFieldModel]
    prerequisites: list[str]
    next_actions: list[str]
    visualization_affordances: list[str]
    examples: list[CatalogExampleModel]
    limitations: list[str]
    qualified_review_required: bool


class ComponentCapabilityModel(BaseModel):
    element: str
    public_workflows: list[str]
    supported_case: str
    held_cases: list[str]
    qualified_review_required: bool


class ComposedWorkflowCapabilityModel(BaseModel):
    capability_id: str
    capability_version: str
    title: str
    summary: str
    component_capability_ids: list[str]
    python_entrypoint: str
    request_schema_id: str
    result_schema_id: str
    example_id: str
    product_surfaces: list[tuple[str, str]]
    limitations: list[str]
    tool_eligible: bool
    qualified_review_required: bool


class WorkflowCatalogDocumentModel(BaseModel):
    schema_version: str
    catalog_version: str
    code_edition: str
    compatible_versions: list[str]
    capabilities: list[WorkflowCapabilityModel]
    component_capabilities: list[ComponentCapabilityModel]
    composed_workflows: list[ComposedWorkflowCapabilityModel]
