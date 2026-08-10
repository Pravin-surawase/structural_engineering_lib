"""Focused contract tests for the one-beam application workflow catalogue."""

from __future__ import annotations

from dataclasses import replace

import pytest

from structural_lib.services.workflow_catalog import (
    CATALOG_VERSION,
    CatalogValidationError,
    UnsupportedCatalogVersionError,
    WorkflowCatalog,
    get_workflow_catalog,
    get_workflow_catalog_document,
    migrate_workflow_catalog_document,
    serialize_workflow_catalog,
    validate_catalog,
    validate_example_input,
)


def test_catalog_is_deterministic_and_semantically_bound() -> None:
    catalog = get_workflow_catalog()
    capability = catalog.capabilities[0]

    assert catalog.catalog_version == CATALOG_VERSION
    assert capability.capability_id == "is456.beam.design"
    assert capability.semantic_workflow_id == "design_beam_is456"
    assert capability.qualified_review_required is True
    assert serialize_workflow_catalog() == serialize_workflow_catalog("1.0")


def test_catalog_rejects_duplicate_and_unknown_registry_ids() -> None:
    catalog = get_workflow_catalog()
    duplicate = WorkflowCatalog(
        schema_version=catalog.schema_version,
        catalog_version=catalog.catalog_version,
        code_edition=catalog.code_edition,
        compatible_versions=catalog.compatible_versions,
        capabilities=(catalog.capabilities[0], catalog.capabilities[0]),
    )
    with pytest.raises(CatalogValidationError, match="Duplicate capability_id"):
        validate_catalog(duplicate)

    invented = replace(
        catalog,
        capabilities=(
            replace(catalog.capabilities[0], service_adapter_id="os.system"),
        ),
    )
    with pytest.raises(CatalogValidationError, match="Unknown service adapter"):
        validate_catalog(invented)


def test_catalog_rejects_unknown_semantics_and_example_fields() -> None:
    catalog = get_workflow_catalog()
    capability = catalog.capabilities[0]
    stale_field = replace(
        capability.fields[0],
        semantic_ref="workflows.design_beam_is456.fields.invented",
    )
    stale = replace(capability, fields=(stale_field, *capability.fields[1:]))

    with pytest.raises(CatalogValidationError, match="Unknown semantic reference"):
        validate_catalog(replace(catalog, capabilities=(stale,)))
    with pytest.raises(CatalogValidationError, match="Unknown example fields"):
        validate_example_input(capability, {"invented": 1.0})


def test_additive_fixture_migrates_and_breaking_version_fails() -> None:
    legacy = get_workflow_catalog_document()
    legacy["version"] = "1.0"
    legacy.pop("catalog_version")

    migrated = migrate_workflow_catalog_document(legacy)
    assert migrated["catalog_version"] == CATALOG_VERSION
    assert migrated == get_workflow_catalog_document()

    with pytest.raises(UnsupportedCatalogVersionError, match="Unsupported"):
        get_workflow_catalog_document("2.0.0")
