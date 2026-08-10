"""Typed transport models for canonical IS 456 capability discovery."""

from __future__ import annotations

from pydantic import BaseModel


class IS456FieldAliasModel(BaseModel):
    """One intentional compatibility spelling."""

    name: str
    deprecated_since: str | None
    remove_in: str | None = None


class IS456FieldContractModel(BaseModel):
    """Units and domain of one canonical public quantity."""

    canonical_name: str
    quantity: str
    unit: str
    required: bool
    finite_physical_domain: str
    legacy_aliases: list[IS456FieldAliasModel]


class IS456StatusContractModel(BaseModel):
    """Meaning and limits of one public status field."""

    canonical_name: str
    meaning: str
    limitations: list[str]


class IS456WorkflowContractModel(BaseModel):
    """Semantic contract for a supported public workflow."""

    workflow: str
    element: str
    fields: list[IS456FieldContractModel]
    statuses: list[IS456StatusContractModel]
    limitations: list[str]


class IS456AdapterContractModel(BaseModel):
    """Semantic contract for a supported transport boundary."""

    adapter: str
    fields: list[IS456FieldContractModel]
    statuses: list[IS456StatusContractModel]
    limitations: list[str]


class IS456SemanticContractModel(BaseModel):
    """Units, aliases, statuses, and limitations for supported routes."""

    workflows: list[IS456WorkflowContractModel]
    adapters: list[IS456AdapterContractModel]


class IS456CapabilityModel(BaseModel):
    """One supported capability plus its held boundary."""

    capability_id: str
    element: str
    public_workflows: list[str]
    supported_case: str
    held_cases: list[str]
    qualified_review_required: bool


class IS456CapabilityDocumentModel(BaseModel):
    """Versioned capability discovery document shared by all public surfaces."""

    schema_version: str
    code_edition: str
    capabilities: list[IS456CapabilityModel]
    semantic_contract: IS456SemanticContractModel
