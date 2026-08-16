"""Project-mode column input and shared result truth."""

from __future__ import annotations

import pytest

from structural_lib.services.column_api import design_column_is456

_BASE = {
    "Pu_kN": 800.0,
    "Mux_kNm": 120.0,
    "Muy_kNm": 40.0,
    "b_mm": 300.0,
    "D_mm": 450.0,
    "l_mm": 3000.0,
    "end_condition": "FIXED_FIXED",
    "Asc_mm2": 2400.0,
}


@pytest.mark.parametrize("field", ["fck_nmm2", "fy_nmm2"])
def test_project_column_materials_are_required(field: str) -> None:
    payload = {**_BASE, "fck_nmm2": 25.0, "fy_nmm2": 415.0}
    del payload[field]

    with pytest.raises(TypeError, match=f"requires '{field}'"):
        design_column_is456(**payload)


def test_column_result_uses_shared_qualified_review_envelope() -> None:
    result = design_column_is456(
        **_BASE,
        fck_nmm2=25.0,
        fy_nmm2=415.0,
    )

    assert result["qualified_review_required"] is True
    assert result["review_status"] == "QUALIFIED_REVIEW_REQUIRED"
    assert result["result_envelope"] == {
        "schema_version": "structural-result-envelope/v1",
        "intake_status": "VALID",
        "calculation_status": "COMPLETED",
        "engineering_status": "PASS" if result["is_safe"] else "FAIL",
        "review_status": "QUALIFIED_REVIEW_REQUIRED",
        "qualified_review_required": True,
        "serviceability_escalation": None,
        "overall_status": "PASS" if result["is_safe"] else "FAIL",
    }
