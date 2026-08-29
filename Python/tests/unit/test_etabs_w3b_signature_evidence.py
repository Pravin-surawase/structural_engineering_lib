"""Portable checks for the W3B installed ETABS signature evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
EVIDENCE_PATH = (
    REPO_ROOT
    / "docs"
    / "verification"
    / "etabs-w3b-installed-getter-signature-evidence.json"
)

EXPECTED_OPERATIONS = {
    "LoadPatterns.GetNameList",
    "LoadPatterns.GetLoadType",
    "LoadPatterns.GetSelfWTMultiplier",
    "LoadCases.GetNameList",
    "LoadCases.GetTypeOAPI",
    "LoadCases.GetTypeOAPI_1",
    "LoadCases.StaticLinear.GetLoads",
    "LoadCases.StaticLinear.GetInitialCase",
    "RespCombo.GetNameList",
    "RespCombo.GetTypeOAPI",
    "RespCombo.GetCaseList",
    "Analyze.GetCaseStatus",
    "Results.Setup.GetCaseSelectedForOutput",
    "Results.Setup.GetComboSelectedForOutput",
    "Results.FrameForce",
}


def _load_evidence() -> dict[str, Any]:
    return json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))


def test_w3b_evidence_is_bound_to_accepted_w3a_contracts() -> None:
    evidence = _load_evidence()

    assert evidence["verdict"] == "STATIC_COMPATIBILITY_PROVED_WITH_GUARDS"
    assert evidence["source"]["accepted_w3a_merge_commit"] == (
        "b7351bb5a3269e4281ba7b34c780e45d2599749b"
    )
    assert evidence["source"]["accepted_w3a_tree"] == (
        "b895008b4f4d3212b6d1e1fe28894e07efc2c7df"
    )

    assert evidence["source"]["accepted_w3a_contracts"] == [
        {
            "path": "Python/structural_lib/core/analysis_contracts.py",
            "byte_count": 17840,
            "sha256": "f264cafb114d1d7b4b7a8af529adc87224ad079483e186c6f461ec05165a12fc",
        },
        {
            "path": "Python/structural_lib/services/contracts/etabs_w3.py",
            "byte_count": 41957,
            "sha256": "cb6b880f90cf00fe39f89f3d9b7d1b22404393b5576be00b8a61de1870b029bd",
        },
    ]


def test_w3b_matrix_is_exact_and_every_installed_signature_is_proved() -> None:
    evidence = _load_evidence()
    operations = evidence["operations"]

    assert {operation["operation"] for operation in operations} == EXPECTED_OPERATIONS
    assert len(operations) == 15
    assert all(operation["managed_signature"] for operation in operations)
    assert all(operation["python_shape"] for operation in operations)
    assert all(
        "generated-raw-wrapper" in operation["source_ids"] for operation in operations
    )
    assert all(operation["verdict"].startswith("PROVED") for operation in operations)
    assert evidence["operation_summary"] == {
        "total": 15,
        "static_signatures_proved": 15,
        "missing_symbols": 0,
        "version_drift": 0,
        "static_blockers": 0,
        "required_fail_closed_guards": 2,
    }


def test_w3b_requires_both_fail_closed_w3c_guards() -> None:
    evidence = _load_evidence()
    guards = {guard["guard_id"]: guard for guard in evidence["required_w3c_guards"]}

    assert set(guards) == {"USE_GETTYPEOAPI_1", "BLOCK_NONBLANK_INITIAL_CASE"}
    assert "exactly 0 or 1" in guards["USE_GETTYPEOAPI_1"]["requirement"]
    assert (
        "nonblank initial-case" in guards["BLOCK_NONBLANK_INITIAL_CASE"]["requirement"]
    )


def test_w3b_scope_makes_no_live_or_professional_claim() -> None:
    evidence = _load_evidence()
    scope = evidence["scope"]

    assert scope["static_installed_metadata_only"] is True
    for key, value in scope.items():
        if key != "static_installed_metadata_only":
            assert value is False, key
    assert (
        evidence["post_inspection_identity"]["etabs_process_not_interacted_with"]
        is True
    )
    assert any("HELD_NOT_SUPPORTED" in item for item in evidence["limitations"])
    assert any("professional" in item for item in evidence["limitations"])
