"""INDIA-0 truth-manifest and reporting contract tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from structural_lib.services.capabilities import get_supported_is456_capabilities

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from _lib.indian_code_manifest import (  # noqa: E402
    MANIFEST_PATH,
    build_manifest,
    render_manifest,
)

STATUS_SEMANTICS_EVIDENCE = (
    REPO_ROOT / "docs/verification/lib-pro-009-is13920-status-semantics.json"
)


def _standard(manifest: dict, namespace: str) -> dict:
    return next(
        item for item in manifest["standards"] if item["namespace"] == namespace
    )


def _run_json(script: str, *arguments: str) -> dict:
    completed = subprocess.run(
        [sys.executable, str(SCRIPTS_ROOT / script), *arguments],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def test_committed_manifest_is_deterministic_and_current() -> None:
    assert MANIFEST_PATH.read_text(encoding="utf-8") == render_manifest()


def test_manifest_uses_closed_namespaced_statuses_without_unknowns() -> None:
    manifest = build_manifest()
    namespaces = [item["namespace"] for item in manifest["standards"]]
    assert namespaces == ["IS456:2000", "IS13920:2016", "IS875", "IS1893"]
    assert len(namespaces) == len(set(namespaces))

    allowed_scope = set(manifest["status_vocabularies"]["scope_status"])
    allowed_implementation = set(
        manifest["status_vocabularies"]["implementation_status"]
    )
    allowed_registration = set(manifest["status_vocabularies"]["registration_status"])
    for standard in manifest["standards"]:
        for family in standard["capability_families"]:
            assert family["scope_status"] in allowed_scope
            assert family["implementation_status"] in allowed_implementation
            assert family["qualified_review_required"] is True
        for reference in standard["references"]:
            assert reference["registration_status"] in allowed_registration

    assert "UNKNOWN" not in render_manifest(manifest)


def test_pile_cap_g0_hold_is_machine_visible() -> None:
    manifest = build_manifest()
    is456 = _standard(manifest, "IS456:2000")
    pile_cap = next(
        item for item in is456["capability_families"] if item["family"] == "pile_cap"
    )

    assert pile_cap["scope_status"] == "HELD"
    assert pile_cap["implementation_status"] == "NOT_IMPLEMENTED"
    assert pile_cap["workflows"] == []
    assert any(
        "controlled companion source" in item for item in pile_cap["limitations"]
    )
    assert pile_cap["evidence"] == [
        "docs/verification/india-2-foundation-pile-cap-g0-hold-evidence.md"
    ]


def test_raft_g0_hold_is_machine_visible() -> None:
    manifest = build_manifest()
    is456 = _standard(manifest, "IS456:2000")
    raft = next(
        item
        for item in is456["capability_families"]
        if item["family"] == "raft_foundation"
    )

    assert raft["scope_status"] == "HELD"
    assert raft["implementation_status"] == "NOT_IMPLEMENTED"
    assert raft["workflows"] == []
    assert any("controlled IS 2950 source" in item for item in raft["limitations"])
    assert raft["evidence"] == [
        "docs/verification/india-2-foundation-raft-g0-hold-evidence.md"
    ]


def test_is456_supported_families_are_generated_from_runtime_registry() -> None:
    manifest = build_manifest()
    is456 = _standard(manifest, "IS456:2000")
    generated_supported = {
        item["family"]: item
        for item in is456["capability_families"]
        if item["scope_status"] == "SUPPORTED"
    }
    runtime = {item.element: item for item in get_supported_is456_capabilities()}

    assert generated_supported.keys() == runtime.keys()
    for family, capability in runtime.items():
        assert generated_supported[family]["workflows"] == list(
            capability.public_workflows
        )
        assert generated_supported[family]["limitations"] == list(capability.held_cases)

    assert generated_supported["solid_slab"]["implementation_status"] == (
        "IMPLEMENTED_BOUNDED"
    )
    assert generated_supported["stair"]["workflows"] == [
        "design_straight_flight_staircase_is456"
    ]
    assert generated_supported["wall"]["workflows"] == ["design_braced_wall_is456"]
    assert generated_supported["deep_beam"]["workflows"] == [
        "design_simply_supported_deep_beam_is456"
    ]
    assert generated_supported["flat_slab"]["workflows"] == [
        "design_regular_interior_flat_slab_is456"
    ]


def test_combined_footing_supported_truth_tracks_publication_chain() -> None:
    manifest = build_manifest()
    is456 = _standard(manifest, "IS456:2000")
    combined = next(
        item
        for item in is456["capability_families"]
        if item["family"] == "combined_footing"
    )

    assert combined["scope_status"] == "SUPPORTED"
    assert combined["implementation_status"] == "IMPLEMENTED_BOUNDED"
    assert combined["workflows"] == ["design_symmetric_combined_footing_is456"]
    assert "two identical square columns" in combined["claim"]
    assert "soil-structure-interaction" in " ".join(combined["limitations"])
    assert "india-2-foundation-combined-c-public-workflow-evidence.md" in " ".join(
        combined["evidence"]
    )
    assert "india-2-foundation-combined-d-publication-evidence.md" in " ".join(
        combined["evidence"]
    )
    assert "india-2-foundation-combined-family-acceptance-evidence.md" in " ".join(
        combined["evidence"]
    )


def test_strap_footing_supported_truth_tracks_publication_chain() -> None:
    manifest = build_manifest()
    is456 = _standard(manifest, "IS456:2000")
    strap = next(
        item
        for item in is456["capability_families"]
        if item["family"] == "strap_footing"
    )

    assert strap["scope_status"] == "SUPPORTED"
    assert strap["implementation_status"] == "IMPLEMENTED_BOUNDED"
    assert strap["workflows"] == ["design_property_line_strap_footing_is456"]
    assert "no-soil-contact strap" in strap["claim"]
    assert "soil-structure interaction" in " ".join(strap["limitations"])
    assert "india-2-foundation-strap-c-public-workflow-evidence.md" in " ".join(
        strap["evidence"]
    )
    assert "india-2-foundation-strap-d-publication-evidence.md" in " ".join(
        strap["evidence"]
    )
    assert "india-2-foundation-strap-family-acceptance-evidence.md" in " ".join(
        strap["evidence"]
    )


def test_is456_and_is13920_registration_cannot_cross_match() -> None:
    manifest = build_manifest()
    is456 = _standard(manifest, "IS456:2000")
    is13920 = _standard(manifest, "IS13920:2016")

    assert all(
        item["reference_id"].startswith("IS456:2000:") for item in is456["references"]
    )
    assert all(
        item["reference_id"].startswith("IS13920:2016:")
        for item in is13920["references"]
    )
    assert is456["registration_summary"]["registration_only_references"] == 0
    assert is13920["registration_summary"]["registration_only_references"] == 0
    assert any(
        item["reference"] == "7.2.1" and item["registration_status"] == "REGISTERED"
        for item in is13920["references"]
    )
    assert all(
        item["registration_status"] == "METADATA_ONLY"
        for item in is13920["references"]
        if item["reference"] in {"7.2.1.1", "7.2.1.2", "7.2.1.3"}
    )


def test_is13920_supported_truth_tracks_repaired_bounded_contracts() -> None:
    manifest = build_manifest()
    is13920 = _standard(manifest, "IS13920:2016")
    families = {item["family"]: item for item in is13920["capability_families"]}

    assert is13920["status"] == "SUPPORTED_SUBSET"
    assert is13920["capability_summary"] == {
        "supported_families": 3,
        "held_families": 2,
        "total_declared_families": 5,
        "supported_pct": 60.0,
    }

    beam = families["beam_detailing_checks"]
    assert beam["implementation_status"] == "IMPLEMENTED_BOUNDED"
    assert "not evaluated" in " ".join(beam["limitations"]).lower()

    column = families["column_detailing_checks"]
    assert column["implementation_status"] == "IMPLEMENTED_BOUNDED"
    column_limitations = " ".join(column["limitations"])
    assert "caller" in column_limitations
    assert "no cover or core geometry is inferred" in column_limitations
    assert "not evaluated" in column_limitations.lower()

    joint = families["beam_column_joint_scwb_check"]
    assert joint["implementation_status"] == "IMPLEMENTED_BOUNDED"
    joint_truth = " ".join([joint["claim"], *joint["limitations"]])
    assert "one principal plane and one shaking direction" in joint_truth
    assert "1.4 times" in joint_truth
    assert "factored axial loads" in joint_truth
    assert "INTERIOR, EXTERIOR_LEFT, and EXTERIOR_RIGHT" in joint_truth
    assert "roof joints are waived" in joint_truth
    assert "flat-slab systems are excluded" in joint_truth

    for family in (beam, column, joint):
        assert family["qualified_review_required"] is True
        assert (
            "docs/verification/india-3-is13920-m0-evidence.json" in family["evidence"]
        )
        assert (
            "docs/verification/lib-pro-009-is13920-status-semantics.json"
            in family["evidence"]
        )

    for held_family in ("wall_detailing", "foundation_detailing"):
        held = families[held_family]
        assert held["scope_status"] == "HELD"
        assert held["implementation_status"] == "NOT_IMPLEMENTED"
        assert held["workflows"] == []


def test_is13920_evidence_separates_replay_from_engineering_disposition() -> None:
    evidence = json.loads(STATUS_SEMANTICS_EVIDENCE.read_text(encoding="utf-8"))
    cases = {item["family"]: item for item in evidence["cases"]}

    assert evidence["schema_version"] == "engineering-evidence-status/v1"
    assert evidence["historical_m0_evidence"]["mutated"] is False
    assert set(cases) == {
        "beam_detailing_checks",
        "column_detailing_checks",
        "beam_column_joint_scwb_check",
    }
    assert all(item["benchmark_replay_status"] == "PASS" for item in cases.values())
    assert all(item["calculation_status"] == "COMPLETED" for item in cases.values())
    assert all(
        item["review_status"] == "QUALIFIED_REVIEW_REQUIRED" for item in cases.values()
    )
    assert cases["beam_detailing_checks"]["engineering_status"] == "NOT_EVALUATED"
    assert cases["column_detailing_checks"]["engineering_status"] == "PASS"
    assert cases["beam_column_joint_scwb_check"]["engineering_status"] == "FAIL"
    assert cases["beam_column_joint_scwb_check"]["is_satisfied"] is False
    assert evidence["professional_approval"] is False
    assert evidence["release_authorized"] is False


def test_clause_checker_reports_registration_not_implementation() -> None:
    report = _run_json("check_clause_coverage.py", "--standard", "IS13920", "--json")
    assert report["report_kind"] == "STANDARD_REFERENCE_DECORATOR_REGISTRATION"
    assert report["standards"][0]["namespace"] == "IS13920:2016"
    assert "implemented" not in report["summary"]
    assert "does not prove implementation" in report["claim_boundary"]


def test_parity_dashboard_consumes_declared_capability_families() -> None:
    report = _run_json("parity_dashboard.py", "--section", "capabilities", "--json")
    section = report["sections"][0]
    assert section["metric_kind"] == "DECLARED_CAPABILITY_FAMILY_COVERAGE"
    assert section["supported"] == 13
    assert section["held"] == 8
    assert section["pct"] == 62
    assert section["informational"] is True
    assert report["overall_pct"] is None
    assert "capability scope" in report["overall_scope"]
    assert "not whole-standard completeness" in section["claim_boundary"]

    default_report = _run_json("parity_dashboard.py", "--json")
    assert default_report["overall_pct"] == 100
