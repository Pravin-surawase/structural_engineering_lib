"""Focused gates for the catalogue-derived beam tool manifest."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from structural_lib.services.tool_manifest import (
    ToolManifestError,
    get_tool_manifest_document,
    serialize_tool_manifest,
    validate_tool_input,
)
from structural_lib.services.workflow_catalog import (
    CatalogValidationError,
    get_workflow_catalog,
)

SAFE_INPUTS = {
    "width": 300.0,
    "depth": 500.0,
    "moment": 150.0,
    "shear": 75.0,
    "fck": 25.0,
    "fy": 500.0,
}
REPO_ROOT = Path(__file__).resolve().parents[2]


def test_manifest_is_deterministic_and_catalogue_derived() -> None:
    manifest = get_tool_manifest_document()
    tool = manifest["tools"][0]
    capability = get_workflow_catalog().capabilities[0]

    assert serialize_tool_manifest() == serialize_tool_manifest()
    assert json.loads(serialize_tool_manifest()) == manifest
    assert tool["capability_id"] == capability.capability_id
    assert tool["input_schema_id"] == capability.request_schema_id
    assert list(tool["input_schema"]["properties"]) == [
        field.transport_name for field in capability.fields
    ]


def test_manifest_preserves_units_limitations_and_review_boundary() -> None:
    tool = get_tool_manifest_document()["tools"][0]
    capability = get_workflow_catalog().capabilities[0]

    assert [
        schema["x-unit"] for schema in tool["input_schema"]["properties"].values()
    ] == [field.unit for field in capability.fields]
    assert tool["limitations"] == list(capability.limitations)
    assert tool["review_boundary"]["qualified_review_required"] is True
    assert tool["execution"]["enabled_by_default"] is False

    properties = tool["input_schema"]["properties"]
    assert "default" not in properties["effective_depth"]
    assert properties["clear_cover"]["default"] == 25.0


def test_manifest_schema_and_catalogue_validate_the_same_input() -> None:
    schema = get_tool_manifest_document()["tools"][0]["input_schema"]
    Draft202012Validator(schema).validate(SAFE_INPUTS)
    assert validate_tool_input("is456.beam.design", SAFE_INPUTS) == SAFE_INPUTS

    invalid = {**SAFE_INPUTS, "invented": 1.0}
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(invalid)
    with pytest.raises(CatalogValidationError, match="Unknown example fields"):
        validate_tool_input("is456.beam.design", invalid)

    missing_required = {
        name: value for name, value in SAFE_INPUTS.items() if name != "width"
    }
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(missing_required)
    with pytest.raises(CatalogValidationError, match="Missing required fields"):
        validate_tool_input("is456.beam.design", missing_required)


def test_unknown_capability_fails_closed() -> None:
    with pytest.raises(ToolManifestError, match="Unknown capability"):
        get_tool_manifest_document(("is456.column.design",))


def test_committed_artifact_check_detects_byte_drift(tmp_path) -> None:
    artifact = tmp_path / "beam-tool-manifest.json"
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "generate_beam_tool_manifest.py"),
        "--out",
        str(artifact),
        "--check",
    ]
    written = subprocess.run([*command, "--write"], check=False)
    assert written.returncode == 0

    artifact.write_text("{}\n", encoding="utf-8")
    stale = subprocess.run(command, check=False)
    assert stale.returncode == 1
