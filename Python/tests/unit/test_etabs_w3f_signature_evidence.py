"""Portable consistency of the installed W3F signature/semantic evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _evidence() -> dict:
    return json.loads(
        (
            ROOT / "docs/verification/etabs-w3f-installed-signature-evidence.json"
        ).read_text(encoding="utf-8")
    )


def test_exact_accepted_contracts_and_installed_sources() -> None:
    evidence = _evidence()
    repair = json.loads(
        (
            ROOT / "docs/verification/etabs-w3f-spring-readback-repair-evidence.json"
        ).read_text(encoding="utf-8")
    )
    assert (
        hashlib.sha256(
            (
                ROOT / "docs/verification/etabs-w3f-installed-signature-evidence.json"
            ).read_bytes()
        ).hexdigest()
        == repair["contract_bindings"]["historical_signature_receipt_sha256"]
    )
    assert (
        evidence["source"]["accepted_contract_merge"]
        == "c84c62d063eaf45fe4ea4e71926d3d6caef7a48b"
    )
    assert (
        evidence["source"]["accepted_contract_tree"]
        == "06bbd1a9959249e800f71be7dea9e85c5eda333a"
    )
    for path, key in (
        ("Python/structural_lib/core/analysis_contracts.py", "accepted_core_sha256"),
        (
            "Python/structural_lib/services/contracts/etabs_w3.py",
            "accepted_service_contract_sha256",
        ),
    ):
        binding = repair["contract_bindings"]["successor_sources"][path]
        assert binding["predecessor_sha256"] == evidence["source"][key]
        assert (
            hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
            == binding["current_sha256"]
        )
    assert evidence["host"]["etabs_executable_version"] == "23.3.1.4563"
    assert evidence["host"]["comtypes"] == "1.4.16"


def test_matrix_counts_derive_from_com_out_flags_not_argument_guessing() -> None:
    evidence = _evidence()
    operations = {item["operation"]: item for item in evidence["operations"]}
    assert len(operations) == len(evidence["operations"]) == 38
    for operation in operations.values():
        outputs = [
            p["name"] for p in operation["com_parameters"] if "out" in p["flags"]
        ]
        assert outputs == operation["decoded_output_order"]
        assert len(outputs) == operation["decoded_output_count"]
        assert operation["verdict"] == "STATIC_SIGNATURE_PROVED"
    insertion = operations["cFrameObj.GetInsertionPoint_1"]
    assert insertion["decoded_output_order"] == [
        "CardinalPoint",
        "Mirror2",
        "Mirror3",
        "StiffTransform",
        "Offset1",
        "Offset2",
        "CSys",
        "pRetVal",
    ]
    for name in ("cAnalysisResults.JointDispl", "cAnalysisResults.JointReact"):
        assert operations[name]["decoded_output_count"] == 13


def test_semantic_guards_and_evidence_levels_cannot_claim_live_or_calibration() -> None:
    evidence = _evidence()
    guards = {item["id"] for item in evidence["required_guards"]}
    assert {
        "INSERTION_POINT_1",
        "JOINT_LOCAL_RESULTS",
        "NO_ABSENT_SPRING_ZERO",
        "NO_UNPROVED_COUPLED_MATRIX",
        "NO_UNPROVED_JOINT_LOAD_STEP",
        "EXACT_UNITS_AND_SCOPE",
        "NO_PARTIAL_RESULT_GROUPS",
        "CURRENT_COMPLETE_STATE",
    } <= guards
    assert evidence["operation_summary"]["live_calls_proved"] == 0
    for key in (
        "new_com_object",
        "live_sapmodel_call",
        "model_saved_or_modified",
        "analysis_or_design",
        "excel_opened_or_written",
        "generated_vendor_source_tracked",
        "professional_approval",
    ):
        assert evidence["scope"][key] is False
    assert any("HELD_NOT_SUPPORTED" in value for value in evidence["limitations"])
