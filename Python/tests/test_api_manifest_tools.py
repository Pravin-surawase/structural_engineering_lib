"""Regression tests for the single canonical public API manifest."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

_SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "validate_api_contracts.py"
)
_SPEC = importlib.util.spec_from_file_location("validate_api_contracts", _SCRIPT_PATH)
assert _SPEC is not None and _SPEC.loader is not None
validate_api_contracts = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = validate_api_contracts
_SPEC.loader.exec_module(validate_api_contracts)


def _result(signature: str = "(value: 'float') -> 'float'"):
    function = validate_api_contracts.APIFunction(
        name="example",
        signature=signature,
        parameters={},
        return_type="float",
        docstring=None,
        is_fastapi_compatible=True,
        issues=[],
    )
    return validate_api_contracts.SchemaValidationResult(
        total_functions=1,
        compatible_count=1,
        incompatible_count=0,
        missing_types=0,
        functions=[function],
        issues=[],
    )


def test_manifest_comparison_reads_symbols_shape(tmp_path, monkeypatch) -> None:
    manifest = tmp_path / "api-manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "symbols": [
                    {
                        "name": "example",
                        "kind": "function",
                        "signature": "(value: 'float') -> 'float'",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validate_api_contracts, "MANIFEST_PATH", manifest)

    assert validate_api_contracts._compare_with_manifest(_result()) == []


def test_manifest_comparison_fails_closed_for_missing_symbol(
    tmp_path, monkeypatch
) -> None:
    manifest = tmp_path / "api-manifest.json"
    manifest.write_text(json.dumps({"symbols": []}), encoding="utf-8")
    monkeypatch.setattr(validate_api_contracts, "MANIFEST_PATH", manifest)

    issues = validate_api_contracts._compare_with_manifest(_result())

    assert issues == ["Functions in API but not in manifest: ['example']"]


def test_manifest_comparison_fails_closed_for_signature_drift(
    tmp_path, monkeypatch
) -> None:
    manifest = tmp_path / "api-manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "symbols": [
                    {
                        "name": "example",
                        "kind": "function",
                        "signature": "() -> 'float'",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(validate_api_contracts, "MANIFEST_PATH", manifest)

    issues = validate_api_contracts._compare_with_manifest(_result())

    assert issues == ["Function signatures differ from manifest: ['example']"]


def test_schema_manifest_mode_exits_nonzero_on_manifest_issue(
    monkeypatch,
) -> None:
    result = _result()
    monkeypatch.setattr(validate_api_contracts, "_validate_api_schema", lambda: result)
    monkeypatch.setattr(validate_api_contracts, "_print_schema_report", lambda *_: None)
    monkeypatch.setattr(
        validate_api_contracts,
        "_compare_with_manifest",
        lambda _: ["deliberate missing symbol"],
    )

    assert validate_api_contracts.validate_schema(manifest=True) == 1


def test_openapi_contract_loader_uses_canonical_raw_snapshot(
    tmp_path, monkeypatch
) -> None:
    baseline = tmp_path / "openapi_baseline.json"
    raw_schema = {
        "info": {"version": "0.23.0"},
        "paths": {"/health": {"get": {"responses": {"200": {}}}}},
        "components": {"schemas": {}},
    }
    baseline.write_text(json.dumps(raw_schema), encoding="utf-8")
    monkeypatch.setattr(validate_api_contracts, "BASELINE_PATH", baseline)

    loaded = validate_api_contracts.load_baseline()

    assert loaded is not None
    assert loaded["version"] == "0.23.0"
    assert set(loaded["endpoints"]) == {"/health"}
