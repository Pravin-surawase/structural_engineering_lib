# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Versioned, transport-neutral catalogue for approved application workflows."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Literal, cast

from structural_lib.services.capabilities import (
    IS456_CODE_EDITION,
    get_supported_is456_semantic_contract,
)

__all__ = [
    "CATALOG_SCHEMA_VERSION",
    "CATALOG_VERSION",
    "CatalogField",
    "CatalogValidationError",
    "UnsupportedCatalogVersionError",
    "WorkflowCapability",
    "WorkflowCatalog",
    "get_workflow_catalog",
    "get_workflow_catalog_document",
    "migrate_workflow_catalog_document",
    "serialize_workflow_catalog",
    "validate_catalog",
    "validate_example_input",
]

CATALOG_SCHEMA_VERSION = "1.0"
CATALOG_VERSION = "1.0.0"
_COMPATIBLE_VERSIONS = ("1.0", CATALOG_VERSION)
_APPROVED_ADAPTERS = frozenset({"fastapi.design_beam.v1"})
_APPROVED_REQUEST_SCHEMAS = frozenset({"fastapi.BeamDesignRequest.v1"})
_APPROVED_RESULT_SCHEMAS = frozenset({"fastapi.BeamDesignResponse.v1"})

JsonScalar = str | int | float | bool | None


class CatalogValidationError(ValueError):
    """Raised when catalogue identity or semantic references are invalid."""


class UnsupportedCatalogVersionError(CatalogValidationError):
    """Raised when a caller requests a breaking or unknown catalogue version."""


@dataclass(frozen=True)
class CatalogField:
    """Curated presentation binding for one canonical semantic field."""

    field_id: str
    transport_name: str
    semantic_ref: str
    label: str
    group: str
    widget: Literal["number", "select"]
    unit: str
    required: bool
    default: JsonScalar
    minimum: float | None = None
    maximum: float | None = None
    choices: tuple[JsonScalar, ...] = ()


@dataclass(frozen=True)
class CatalogExample:
    """Deterministic named example represented without mutable mappings."""

    name: str
    values: tuple[tuple[str, JsonScalar], ...]


@dataclass(frozen=True)
class WorkflowCapability:
    """One approved application capability and its non-executable bindings."""

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
    fields: tuple[CatalogField, ...]
    prerequisites: tuple[str, ...]
    next_actions: tuple[str, ...]
    visualization_affordances: tuple[str, ...]
    examples: tuple[CatalogExample, ...]
    limitations: tuple[str, ...]
    qualified_review_required: bool


@dataclass(frozen=True)
class WorkflowCatalog:
    """Immutable catalogue root."""

    schema_version: str
    catalog_version: str
    code_edition: str
    compatible_versions: tuple[str, ...]
    capabilities: tuple[WorkflowCapability, ...]


_BEAM_FIELDS = (
    CatalogField(
        "b_mm",
        "width",
        "workflows.design_beam_is456.fields.b_mm",
        "Width",
        "Dimensions",
        "number",
        "mm",
        True,
        300.0,
        150.0,
        2000.0,
    ),
    CatalogField(
        "D_mm",
        "depth",
        "workflows.design_beam_is456.fields.D_mm",
        "Depth",
        "Dimensions",
        "number",
        "mm",
        True,
        500.0,
        250.0,
        3000.0,
    ),
    CatalogField(
        "mu_knm",
        "moment",
        "workflows.design_beam_is456.fields.mu_knm",
        "Moment (Mu)",
        "Design forces",
        "number",
        "kN m",
        True,
        150.0,
        0.0,
        2000.0,
    ),
    CatalogField(
        "vu_kn",
        "shear",
        "workflows.design_beam_is456.fields.vu_kn",
        "Shear (Vu)",
        "Design forces",
        "number",
        "kN",
        True,
        75.0,
        0.0,
        1000.0,
    ),
    CatalogField(
        "fck_nmm2",
        "fck",
        "workflows.design_beam_is456.fields.fck_nmm2",
        "Concrete",
        "Materials",
        "select",
        "N/mm2",
        True,
        25.0,
        choices=(20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0),
    ),
    CatalogField(
        "fy_nmm2",
        "fy",
        "workflows.design_beam_is456.fields.fy_nmm2",
        "Steel",
        "Materials",
        "select",
        "N/mm2",
        True,
        500.0,
        choices=(415.0, 500.0, 550.0),
    ),
)

_CATALOG = WorkflowCatalog(
    schema_version=CATALOG_SCHEMA_VERSION,
    catalog_version=CATALOG_VERSION,
    code_edition=IS456_CODE_EDITION,
    compatible_versions=_COMPATIBLE_VERSIONS,
    capabilities=(
        WorkflowCapability(
            capability_id="is456.beam.design",
            capability_version="1.0.0",
            element="beam",
            title="IS 456 beam design",
            summary="Design one rectangular reinforced-concrete beam for the declared flexure and shear inputs.",
            semantic_workflow_id="design_beam_is456",
            service_adapter_id="fastapi.design_beam.v1",
            request_schema_id="fastapi.BeamDesignRequest.v1",
            result_schema_id="fastapi.BeamDesignResponse.v1",
            status_semantic_ref="workflows.design_beam_is456.statuses.is_ok",
            fields=_BEAM_FIELDS,
            prerequisites=(
                "Factored bending moment and shear are supplied in the declared units.",
                "The member is within the route-specific rectangular beam scope.",
            ),
            next_actions=(
                "Inspect governing utilization and reinforcement demand.",
                "Continue to detailing/export only while the result revision is current.",
            ),
            visualization_affordances=(
                "beam_section",
                "reinforcement_detail",
                "status_utilization",
            ),
            examples=(
                CatalogExample(
                    name="maintained-safe-beam",
                    values=(
                        ("width", 300.0),
                        ("depth", 500.0),
                        ("moment", 150.0),
                        ("shear", 75.0),
                        ("fck", 25.0),
                        ("fy", 500.0),
                    ),
                ),
            ),
            limitations=(
                "Torsion is a separate explicit workflow.",
                "The result is software evidence and requires qualified engineering review.",
            ),
            qualified_review_required=True,
        ),
    ),
)


def _semantic_reference_set() -> set[str]:
    contract = get_supported_is456_semantic_contract()
    references: set[str] = set()
    for workflow in contract.workflows:
        for field in workflow.fields:
            references.add(
                f"workflows.{workflow.workflow}.fields.{field.canonical_name}"
            )
        for status in workflow.statuses:
            references.add(
                f"workflows.{workflow.workflow}.statuses.{status.canonical_name}"
            )
    return references


def validate_example_input(
    capability: WorkflowCapability, values: dict[str, JsonScalar]
) -> None:
    """Validate one example/request mapping against curated field constraints."""
    fields = {field.transport_name: field for field in capability.fields}
    unknown = sorted(set(values) - set(fields))
    if unknown:
        raise CatalogValidationError(f"Unknown example fields: {', '.join(unknown)}")
    missing = sorted(
        name
        for name, field in fields.items()
        if field.required and name not in values and field.default is None
    )
    if missing:
        raise CatalogValidationError(f"Missing required fields: {', '.join(missing)}")
    for name, value in values.items():
        field = fields[name]
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise CatalogValidationError(f"{name} must be numeric")
        numeric = float(value)
        if field.minimum is not None and numeric < field.minimum:
            raise CatalogValidationError(f"{name} is below its minimum")
        if field.maximum is not None and numeric > field.maximum:
            raise CatalogValidationError(f"{name} exceeds its maximum")
        if field.choices and value not in field.choices:
            raise CatalogValidationError(f"{name} is not an approved choice")


def validate_catalog(catalog: WorkflowCatalog) -> WorkflowCatalog:
    """Fail closed on duplicate IDs, invented schemas/adapters, or stale semantics."""
    if catalog.schema_version != CATALOG_SCHEMA_VERSION:
        raise CatalogValidationError("Unsupported catalogue schema version")
    if catalog.catalog_version != CATALOG_VERSION:
        raise CatalogValidationError("Catalogue version is not current")

    capability_ids = [item.capability_id for item in catalog.capabilities]
    if len(capability_ids) != len(set(capability_ids)):
        raise CatalogValidationError("Duplicate capability_id")

    semantic_references = _semantic_reference_set()
    for capability in catalog.capabilities:
        if capability.service_adapter_id not in _APPROVED_ADAPTERS:
            raise CatalogValidationError("Unknown service adapter ID")
        if capability.request_schema_id not in _APPROVED_REQUEST_SCHEMAS:
            raise CatalogValidationError("Unknown request schema ID")
        if capability.result_schema_id not in _APPROVED_RESULT_SCHEMAS:
            raise CatalogValidationError("Unknown result schema ID")
        if capability.status_semantic_ref not in semantic_references:
            raise CatalogValidationError("Unknown status semantic reference")

        field_ids = [field.field_id for field in capability.fields]
        transport_names = [field.transport_name for field in capability.fields]
        if len(field_ids) != len(set(field_ids)):
            raise CatalogValidationError("Duplicate field_id")
        if len(transport_names) != len(set(transport_names)):
            raise CatalogValidationError("Duplicate transport field")
        for field in capability.fields:
            if field.semantic_ref not in semantic_references:
                raise CatalogValidationError(
                    f"Unknown semantic reference: {field.semantic_ref}"
                )
            if field.choices and field.default not in field.choices:
                raise CatalogValidationError(
                    f"Default for {field.transport_name} is not an approved choice"
                )
        for example in capability.examples:
            validate_example_input(capability, dict(example.values))
    return catalog


def get_workflow_catalog() -> WorkflowCatalog:
    """Return the validated immutable application catalogue."""
    return validate_catalog(_CATALOG)


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def get_workflow_catalog_document(version: str | None = None) -> dict[str, Any]:
    """Return the deterministic JSON-native catalogue for a compatible version."""
    requested = version or CATALOG_VERSION
    if requested not in _COMPATIBLE_VERSIONS:
        raise UnsupportedCatalogVersionError(
            f"Unsupported catalogue version '{requested}'; supported: "
            + ", ".join(_COMPATIBLE_VERSIONS)
        )
    return cast(dict[str, Any], _json_ready(asdict(get_workflow_catalog())))


def migrate_workflow_catalog_document(document: dict[str, Any]) -> dict[str, Any]:
    """Migrate the additive 1.0 fixture and reject unknown/breaking versions."""
    migrated = cast(dict[str, Any], json.loads(json.dumps(document)))
    version = migrated.get("catalog_version", migrated.pop("version", None))
    if version not in _COMPATIBLE_VERSIONS:
        raise UnsupportedCatalogVersionError(
            f"Cannot migrate catalogue version '{version}' to {CATALOG_VERSION}"
        )
    migrated["catalog_version"] = CATALOG_VERSION
    migrated["schema_version"] = CATALOG_SCHEMA_VERSION
    migrated["compatible_versions"] = list(_COMPATIBLE_VERSIONS)
    return migrated


def serialize_workflow_catalog(version: str | None = None) -> str:
    """Serialize with stable ordering and separators for identity checks."""
    return json.dumps(
        get_workflow_catalog_document(version),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
