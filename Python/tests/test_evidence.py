"""Focused tests for the supported IS 456 beam evidence envelope."""

from __future__ import annotations

import json

import pytest

from structural_lib.services.evidence import (
    BEAM_EVIDENCE_SCHEMA_VERSION,
    build_beam_evidence_envelope,
)
from structural_lib.services.report import ReportData, export_html, export_json
from structural_lib.services.source_identity import (
    AmendmentApplicability,
    ControlledSourceBasisV1,
)


def _beam_inputs(moment: float = 120.0) -> dict[str, float | str]:
    return {
        "units": "IS456",
        "case_id": "CASE-1",
        "mu_knm": moment,
        "vu_kn": 80.0,
        "b_mm": 300.0,
        "D_mm": 500.0,
        "d_mm": 457.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 500.0,
        "d_dash_mm": 43.0,
        "asv_mm2": 100.0,
    }


def _evidence(inputs: dict[str, float | str], *, is_ok: bool = True) -> dict:
    return build_beam_evidence_envelope(
        inputs=inputs,
        is_ok=is_ok,
        governing_utilization=0.8,
        utilizations={"shear": 0.4, "flexure": 0.8},
        generated_at="2026-08-10T00:00:00+00:00",
    )


def test_beam_evidence_hash_uses_normalized_consumed_inputs() -> None:
    inputs = _beam_inputs()
    reordered_with_presentation_fields = {
        "label": "presentation-only",
        "fy_nmm2": 500,
        "D_mm": 500,
        "mu_knm": 120,
        "units": "IS456",
        "d_mm": 457,
        "asv_mm2": 100,
        "fck_nmm2": 25,
        "b_mm": 300,
        "case_id": "CASE-1",
        "vu_kn": 80,
        "d_dash_mm": 43,
    }

    evidence = _evidence(inputs)
    reordered = _evidence(reordered_with_presentation_fields)

    assert evidence["normalized_input_hash"] == reordered["normalized_input_hash"]
    assert evidence["calculation_identity"] == reordered["calculation_identity"]
    assert evidence["governing_check"] == "flexure"
    assert evidence["margin"] == pytest.approx(0.2)


def test_beam_evidence_hash_changes_for_relevant_input() -> None:
    baseline = _evidence(_beam_inputs())
    changed = _evidence(_beam_inputs(moment=121.0))

    assert baseline["normalized_input_hash"] != changed["normalized_input_hash"]
    assert baseline["calculation_identity"] != changed["calculation_identity"]


def test_beam_evidence_v2_binds_torsion_and_enabled_serviceability() -> None:
    baseline = _beam_inputs()
    torsion = {
        **baseline,
        "tu_knm": 12.0,
        "cover_mm": 25.0,
        "stirrup_dia_mm": 8.0,
    }
    service = {
        **baseline,
        "include_serviceability": True,
        "deflection_params": {
            "span_mm": 5000.0,
            "d_mm": 457.0,
            "support_condition": "SS",
        },
        "crack_width_params": {
            "exposure_class": "moderate",
            "acr_mm": 45.0,
            "cmin_mm": 25.0,
            "h_mm": 500.0,
            "x_mm": 150.0,
            "fs_service_nmm2": 180.0,
            "es_nmm2": 200000.0,
        },
    }

    base_evidence = _evidence(baseline)
    torsion_evidence = _evidence(torsion)
    service_evidence = _evidence(service)

    assert base_evidence["artifact_schema_version"] == BEAM_EVIDENCE_SCHEMA_VERSION
    assert BEAM_EVIDENCE_SCHEMA_VERSION == "3.0"
    assert (
        torsion_evidence["normalized_input_hash"]
        != base_evidence["normalized_input_hash"]
    )
    assert (
        service_evidence["normalized_input_hash"]
        != base_evidence["normalized_input_hash"]
    )


def test_disabled_serviceability_drafts_do_not_change_identity() -> None:
    baseline = _beam_inputs()
    with_unused_drafts = {
        **baseline,
        "include_serviceability": False,
        "deflection_params": {"span_mm": 9999.0},
        "crack_width_params": {"acr_mm": 999.0},
    }

    assert (
        _evidence(baseline)["normalized_input_hash"]
        == _evidence(with_unused_drafts)["normalized_input_hash"]
    )


def test_metadata_only_change_is_recorded_without_changing_arithmetic_identity() -> (
    None
):
    first = build_beam_evidence_envelope(
        inputs=_beam_inputs(),
        is_ok=True,
        governing_utilization=0.8,
        source_metadata={"artifact_sha256": "a" * 64, "note": "first"},
        generated_at="2026-08-10T00:00:00+00:00",
    )
    second = build_beam_evidence_envelope(
        inputs=_beam_inputs(),
        is_ok=True,
        governing_utilization=0.8,
        source_metadata={"artifact_sha256": "a" * 64, "note": "second"},
        generated_at="2026-08-10T00:00:00+00:00",
    )

    assert first["normalized_input_hash"] == second["normalized_input_hash"]
    assert first["calculation_identity"] == second["calculation_identity"]
    assert first["provenance_hash"] != second["provenance_hash"]
    assert first["replay_receipt_hash"] != second["replay_receipt_hash"]


def test_unknown_amendment_applicability_forces_hold() -> None:
    unknown = ControlledSourceBasisV1(
        route_id="design_beam_is456",
        source_ids=("unresolved",),
        amendment_identity="unresolved",
        amendment_applicability=AmendmentApplicability.UNKNOWN,
        applicability_review_id=None,
    )
    evidence = build_beam_evidence_envelope(
        inputs=_beam_inputs(),
        is_ok=True,
        governing_utilization=0.8,
        source_basis=unknown,
        generated_at="2026-08-10T00:00:00+00:00",
    )

    assert evidence["amendment_applicability"] == "UNKNOWN"
    assert evidence["support_status"] == "HELD"
    assert evidence["status"] == "HOLD"
    assert evidence["exact_utilization"] is None


def test_held_beam_evidence_does_not_present_a_pass_or_fail() -> None:
    evidence = build_beam_evidence_envelope(
        inputs=_beam_inputs(),
        is_ok=False,
        governing_utilization=1.2,
        supported=False,
        generated_at="2026-08-10T00:00:00+00:00",
    )

    assert evidence["support_status"] == "HELD"
    assert evidence["status"] == "HOLD"
    assert evidence["exact_utilization"] is None
    assert evidence["margin"] is None


def test_beam_report_exports_evidence_without_approval_claim() -> None:
    evidence = _evidence(_beam_inputs())
    data = ReportData(
        job_id="B1",
        code="IS456",
        units="IS456",
        beam={"b_mm": 300.0, "D_mm": 500.0, "d_mm": 457.0},
        cases=[],
        results={},
        is_ok=True,
        governing_utilization=0.8,
        evidence=evidence,
    )

    json_payload = json.loads(export_json(data))
    html_payload = export_html(data)

    assert json_payload["evidence"] == evidence
    assert "Evidence Identity" in html_payload
    assert "not professional design approval" in html_payload
