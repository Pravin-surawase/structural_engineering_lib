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
    flat_slab = next(
        item for item in is456["capability_families"] if item["family"] == "flat_slab"
    )
    assert flat_slab["scope_status"] == "HELD"


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
    assert is13920["registration_summary"]["registration_only_references"] > 0
    assert any(
        item["reference"] == "7.4.8"
        and item["registration_status"] == "REGISTRATION_ONLY"
        for item in is13920["references"]
    )


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
    assert section["supported"] == 9
    assert section["held"] == 12
    assert section["pct"] == 43
    assert section["informational"] is True
    assert report["overall_pct"] is None
    assert "capability scope" in report["overall_scope"]
    assert "not whole-standard completeness" in section["claim_boundary"]

    default_report = _run_json("parity_dashboard.py", "--json")
    assert default_report["overall_pct"] == 100
