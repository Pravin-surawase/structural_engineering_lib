"""WP10-01 host-free analysis-snapshot contract and parity fixtures."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path

import pytest

from structural_lib.analysis_snapshot import (
    canonical_analysis_snapshot_json,
    parse_analysis_snapshot_json,
    parse_etabs_import_request_json,
)

ROOT = Path(__file__).resolve().parents[3]
FIXTURE_PATH = (
    ROOT / "contracts" / "structural-engineering" / "conformance" / "wp10-vectors.json"
)
FIXTURE = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _mutate(document: dict[str, object], mutations: list[dict[str, object]]) -> None:
    for mutation in mutations:
        parts = str(mutation["path"]).lstrip("/").split("/")
        target: object = document
        for part in parts[:-1]:
            target = target[int(part)] if isinstance(target, list) else target[part]
        leaf = parts[-1]
        if mutation["operation"] == "remove":
            if isinstance(target, list):
                target.pop(int(leaf))
            else:
                del target[leaf]
        elif isinstance(target, list):
            target[int(leaf)] = mutation["value"]
        else:
            target[leaf] = mutation["value"]


def test_request_contract_retains_explicit_scope_and_optional_evidence() -> None:
    request = parse_etabs_import_request_json(json.dumps(FIXTURE["valid_request"]))

    assert request.operation_semantic_id == "etabs.beam_snapshot.import/v1"
    assert request.scope.members.member_ids == ("member-b1",)
    assert request.scope.result_selection_ids == ("selection-uls",)
    assert request.source_expectation.process_identity.value is not None
    assert request.source_expectation.model_file_sha256.value is not None


def test_request_contract_rejects_invalid_sha_and_empty_explicit_scope() -> None:
    invalid_sha = copy.deepcopy(FIXTURE["valid_request"])
    invalid_sha["source_expectation"]["model_file_sha256"]["value"] = "bad"
    empty_explicit = copy.deepcopy(FIXTURE["valid_request"])
    empty_explicit["scope"]["members"]["member_ids"] = []

    with pytest.raises(ValueError):
        parse_etabs_import_request_json(json.dumps(invalid_sha))
    with pytest.raises(ValueError):
        parse_etabs_import_request_json(json.dumps(empty_explicit))


def test_valid_snapshot_is_complete_current_and_canonically_stable() -> None:
    expected = FIXTURE["expected"]
    result = parse_analysis_snapshot_json(json.dumps(FIXTURE["valid_snapshot"]))

    assert result.operation_state.value == expected["states"]["operation_state"]
    assert result.execution == expected["states"]["execution"]
    assert result.applicability == expected["states"]["applicability"]
    assert result.engineering == expected["states"]["engineering"]
    assert result.completeness == expected["states"]["completeness"]
    assert result.freshness == expected["states"]["freshness"]
    assert result.approval == expected["states"]["approval"]
    assert result.snapshot is not None
    assert result.snapshot.snapshot_id == expected["snapshot_id"]
    assert result.snapshot.raw_capture.raw_capture_id == expected["raw_capture_id"]

    canonical = canonical_analysis_snapshot_json(result.snapshot).encode("utf-8")
    assert len(canonical) == expected["canonical_json_byte_count"]
    assert hashlib.sha256(canonical).hexdigest() == expected["canonical_json_sha256"]
    replay = parse_analysis_snapshot_json(canonical)
    assert replay.snapshot == result.snapshot


@pytest.mark.parametrize("kind", ["duplicate_key", "non_finite"])
def test_invalid_json_transport_is_rejected(kind: str) -> None:
    payload = json.dumps(FIXTURE["valid_snapshot"], separators=(",", ":"))
    if kind == "duplicate_key":
        payload = '{"schema_version":"duplicate",' + payload[1:]
    else:
        payload = payload.replace('"p":-12000', '"p":NaN', 1)

    result = parse_analysis_snapshot_json(payload)

    assert result.operation_state.value == "preflight_rejected"
    assert result.execution == "rejected_input"
    assert result.diagnostics[0].code == "INPUT.SCHEMA"


@pytest.mark.parametrize(
    "vector",
    FIXTURE["invalid_vectors"],
    ids=[item["id"] for item in FIXTURE["invalid_vectors"]],
)
def test_invalid_snapshot_vectors_fail_closed(vector: dict[str, object]) -> None:
    document = copy.deepcopy(FIXTURE["valid_snapshot"])
    _mutate(document, vector["mutations"])

    result = parse_analysis_snapshot_json(json.dumps(document))

    assert result.snapshot is None
    assert result.operation_state.value == vector["expected"]["operation_state"]
    assert result.execution == vector["expected"]["execution"]
    assert result.diagnostics[0].code == vector["expected"]["diagnostic"]


def test_python_contract_modules_have_only_host_free_imports() -> None:
    forbidden_roots = {"comtypes", "pythoncom", "win32com", "xlwings"}
    paths = (
        ROOT / "Python" / "structural_lib" / "core" / "analysis_snapshot.py",
        ROOT / "Python" / "structural_lib" / "services" / "analysis_snapshot.py",
        ROOT / "Python" / "structural_lib" / "analysis_snapshot.py",
    )
    imported_roots: set[str] = set()
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(name.name.split(".")[0] for name in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".")[0])

    assert imported_roots.isdisjoint(forbidden_roots)
