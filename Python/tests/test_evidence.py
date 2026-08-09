"""Focused tests for the supported IS 456 beam evidence envelope."""

from __future__ import annotations

import json

import pytest

from structural_lib.services.evidence import build_beam_evidence_envelope
from structural_lib.services.report import ReportData, export_html, export_json


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
