# SPDX-License-Identifier: MIT
"""Focused truth-table tests for supplied rectangular-beam reinforcement."""

from __future__ import annotations

import pytest

import structural_lib
from structural_lib.services.beam_reinforcement import (
    BeamReinforcementSelectionConstraintsV1,
    LongitudinalBarLayersV1,
    SuppliedBeamReinforcementV1,
    evaluate_supplied_beam_reinforcement_v1,
)


def _selection() -> BeamReinforcementSelectionConstraintsV1:
    return BeamReinforcementSelectionConstraintsV1(
        permitted_diameters_mm=(12.0, 16.0, 20.0),
        maximum_layers=2,
        maximum_bars_per_layer=8,
        nominal_max_aggregate_size_mm=20,
        effective_depth_tolerance_mm=5,
        objective="min_area",
        source_reference="Reviewed test bar-selection constraints",
    )


def _supplied(*, tension_count: int = 4) -> SuppliedBeamReinforcementV1:
    return SuppliedBeamReinforcementV1(
        tension=LongitudinalBarLayersV1(
            diameter_mm=16,
            bars_per_layer=(tension_count,),
        ),
        compression_or_hanger=LongitudinalBarLayersV1(
            diameter_mm=12,
            bars_per_layer=(2,),
        ),
        bar_type="deformed",
        has_standard_bend_at_start=True,
        has_standard_bend_at_end=True,
        source_reference="Reviewed test bar schedule B1",
    )


def _evaluate(**overrides: object):
    values: dict[str, object] = {
        "ast_required_mm2": 700.0,
        "asc_required_mm2": 0.0,
        "b_mm": 300.0,
        "D_mm": 500.0,
        "d_design_mm": 459.0,
        "d_dash_design_mm": None,
        "cover_mm": 25.0,
        "stirrup_dia_mm": 8.0,
        "fck_nmm2": 25.0,
        "fy_nmm2": 415.0,
        "vu_kn": 60.0,
        "support_width_start_mm": 1600.0,
        "support_width_end_mm": 1600.0,
        "support_width_source_reference": "Reviewed square supports C1 and C2",
        "selection": _selection(),
        "supplied": _supplied(),
    }
    values.update(overrides)
    return evaluate_supplied_beam_reinforcement_v1(**values)  # type: ignore[arg-type]


def test_package_root_exports_supplied_reinforcement_contract() -> None:
    assert structural_lib.evaluate_supplied_beam_reinforcement_v1 is (
        evaluate_supplied_beam_reinforcement_v1
    )
    assert structural_lib.GravityBeamReinforcementBasisV1.__name__ == (
        "GravityBeamReinforcementBasisV1"
    )


def test_missing_supplied_bars_holds_but_retains_preliminary_recommendation() -> None:
    result = _evaluate(supplied=None)

    assert result.status == "HOLD"
    assert result.recommended_tension is not None
    assert result.recommended_tension["status"] == (
        "PRELIMINARY_RECOMMENDATION_NOT_SUPPLIED_DETAILING"
    )
    assert result.issues[0]["code"] == "BEAM_SUPPLIED_REINFORCEMENT_NOT_SUPPLIED"


def test_complete_supplied_arrangement_can_reach_bounded_pass() -> None:
    result = _evaluate()

    assert result.status == "PASS"
    assert result.supplied_tension is not None
    assert result.checks["effective_depth"]["is_adequate"] is True
    assert result.checks["start_anchorage"]["is_adequate"] is True
    assert result.checks["end_anchorage"]["is_adequate"] is True


def test_inadequate_supplied_area_fails_without_changing_required_demand() -> None:
    result = _evaluate(ast_required_mm2=900.0)

    assert result.status == "FAIL"
    assert result.ast_required_mm2 == 900.0
    assert result.issues[0]["code"] == ("BEAM_TENSION_REINFORCEMENT_AREA_INSUFFICIENT")


def test_clear_spacing_failure_is_detected_from_center_spacing() -> None:
    result = _evaluate(b_mm=180.0)

    assert result.status == "FAIL"
    assert result.checks["tension_spacing"]["is_adequate"] is False
    assert any(
        issue["code"] == "BEAM_TENSION_BAR_SPACING_INADEQUATE"
        for issue in result.issues
    )


def test_effective_depth_mismatch_fails() -> None:
    result = _evaluate(d_design_mm=440.0)

    assert result.status == "FAIL"
    assert any(
        issue["code"] == "BEAM_SUPPLIED_EFFECTIVE_DEPTH_MISMATCH"
        for issue in result.issues
    )


def test_missing_support_width_basis_holds_after_other_checks() -> None:
    result = _evaluate(
        support_width_start_mm=None,
        support_width_end_mm=None,
        support_width_source_reference=None,
    )

    assert result.status == "HOLD"
    assert any(
        issue["code"] == "BEAM_SUPPORT_WIDTH_BASIS_NOT_SUPPLIED"
        for issue in result.issues
    )


def test_missing_compression_depth_basis_holds_doubly_reinforced_case() -> None:
    result = _evaluate(asc_required_mm2=100.0, d_dash_design_mm=None)

    assert result.status == "HOLD"
    assert any(
        issue["code"] == "BEAM_COMPRESSION_DEPTH_BASIS_NOT_SUPPLIED"
        for issue in result.issues
    )


def test_layer_contract_requires_one_vertical_spacing_between_layers() -> None:
    with pytest.raises(ValueError, match="one value between layers"):
        LongitudinalBarLayersV1(
            diameter_mm=16,
            bars_per_layer=(2, 2),
        )


def test_direct_service_layer_contract_rejects_mutable_lists() -> None:
    with pytest.raises(ValueError, match="immutable tuples"):
        LongitudinalBarLayersV1(
            diameter_mm=16,
            bars_per_layer=[2],  # type: ignore[arg-type]
        )
