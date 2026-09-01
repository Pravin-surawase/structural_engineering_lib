# SPDX-License-Identifier: MIT
"""Focused contract tests for the truthful supplied-beam V2 check."""

from __future__ import annotations

from copy import deepcopy

import pytest

from structural_lib.core.errors import InputContractError
from structural_lib.design.is456 import beam


def _payload() -> dict[str, object]:
    return {
        "schema_version": "beam-supplied-check/v2",
        "correlation_id": "REQ-B1-ULS-1",
        "identity": {"member_id": "B1", "story": "L1", "case_id": "ULS-1"},
        "section": {
            "b_mm": 300.0,
            "D_mm": 500.0,
            "effective_depth_basis": {
                "clear_cover_mm": 40.0,
                "stirrup_diameter_mm": 8.0,
                "tension_bar_diameter_mm": 20.0,
            },
        },
        "materials": {
            "fck_nmm2": 25.0,
            "fy_nmm2": 500.0,
            "fy_transverse_nmm2": 415.0,
        },
        "actions": {
            "mu_knm": 100.0,
            "vu_kn": 60.0,
            "primary_tension_face": "BOTTOM",
        },
        "reinforcement": {
            "clear_cover_mm": 40.0,
            "tension": {
                "diameter_mm": 20.0,
                "bars_per_layer": [4],
            },
            "compression_or_hanger": {
                "diameter_mm": 12.0,
                "bars_per_layer": [2],
            },
            "stirrup_diameter_mm": 8.0,
            "stirrup_legs": 2,
            "stirrup_spacing_mm": 150.0,
            "bar_type": "deformed",
            "has_standard_bend_at_start": True,
            "has_standard_bend_at_end": True,
            "source_reference": "Reviewed schedule B1-R1",
        },
        "selection": {
            "permitted_diameters_mm": [12.0, 16.0, 20.0, 25.0],
            "maximum_layers": 2,
            "maximum_bars_per_layer": 8,
            "nominal_max_aggregate_size_mm": 20.0,
            "effective_depth_tolerance_mm": 1.0,
            "objective": "min_area",
            "source_reference": "Reviewed project bar catalogue P1",
        },
        "support": {
            "start_width_mm": 5000.0,
            "end_width_mm": 5000.0,
            "source_reference": "Reviewed supports C1 and C2",
        },
        "source_provenance": "Reviewed supplied reinforcement schedule",
    }


def _check(payload: dict[str, object] | None = None):
    request = beam.load_supplied_check(payload or _payload())
    return beam.check_supplied(request)


def test_complete_depth_basis_500_40_8_20_resolves_to_442_mm() -> None:
    result = _check()

    assert result.effective_depth_resolution["source"] == "DERIVED"
    assert result.effective_depth_resolution["d_mm"] == pytest.approx(442.0)
    assert result.longitudinal.checks["effective_depth"]["is_adequate"] is True
    assert result.correlation_id == "REQ-B1-ULS-1"
    assert result.result_envelope.result_identity is not None


def test_omitting_explicit_depth_and_complete_basis_fails_before_calculation() -> None:
    payload = _payload()
    section = payload["section"]
    assert isinstance(section, dict)
    section.pop("effective_depth_basis")

    with pytest.raises(InputContractError) as exc_info:
        beam.load_supplied_check(payload)

    assert any(
        "effective_depth_basis" in issue.message for issue in exc_info.value.issues
    )


def test_support_omission_returns_typed_hold_without_mapping_to_pass() -> None:
    payload = _payload()
    payload["support"] = None

    result = _check(payload)

    assert result.status == "HOLD"
    assert result.result_envelope.engineering_status.value == "HOLD"
    assert result.result_envelope.overall_status.value == "HOLD"
    assert any(
        issue["code"] == "BEAM_SUPPORT_WIDTH_BASIS_NOT_SUPPLIED"
        for issue in result.longitudinal.issues
    )


def test_supplied_stirrup_spacing_changes_the_shear_result() -> None:
    close = _payload()
    close_actions = close["actions"]
    assert isinstance(close_actions, dict)
    close_actions["vu_kn"] = 200.0
    close_reinforcement = close["reinforcement"]
    assert isinstance(close_reinforcement, dict)
    close_reinforcement["stirrup_spacing_mm"] = 75.0

    wide = deepcopy(close)
    wide_reinforcement = wide["reinforcement"]
    assert isinstance(wide_reinforcement, dict)
    wide_reinforcement["stirrup_spacing_mm"] = 300.0

    close_result = _check(close)
    wide_result = _check(wide)

    assert close_result.shear.status == "PASS"
    assert wide_result.shear.status == "FAIL"
    assert close_result.shear.provided_stirrup_capacity_kn > (
        wide_result.shear.provided_stirrup_capacity_kn
    )
    assert any(
        issue["code"] == "BEAM_STIRRUP_SPACING_INADEQUATE"
        for issue in wide_result.shear.issues
    )


def test_supplied_compression_steel_changes_the_flexural_result() -> None:
    insufficient = _payload()
    actions = insufficient["actions"]
    reinforcement = insufficient["reinforcement"]
    assert isinstance(actions, dict)
    assert isinstance(reinforcement, dict)
    actions["mu_knm"] = 240.0
    tension = reinforcement["tension"]
    assert isinstance(tension, dict)
    tension["bars_per_layer"] = [5]

    sufficient = deepcopy(insufficient)
    sufficient_reinforcement = sufficient["reinforcement"]
    assert isinstance(sufficient_reinforcement, dict)
    compression = sufficient_reinforcement["compression_or_hanger"]
    assert isinstance(compression, dict)
    compression["bars_per_layer"] = [3]

    insufficient_result = _check(insufficient)
    sufficient_result = _check(sufficient)

    assert insufficient_result.longitudinal.status == "FAIL"
    assert sufficient_result.longitudinal.status == "PASS"
    assert (
        insufficient_result.longitudinal.checks["compression_area"]["is_adequate"]
        is False
    )
    assert (
        sufficient_result.longitudinal.checks["compression_area"]["is_adequate"] is True
    )


def test_incompatible_legacy_flat_payload_is_rejected_explicitly() -> None:
    with pytest.raises(InputContractError):
        beam.load_supplied_check(
            {
                "width": 300,
                "depth": 500,
                "moment": 100,
                "shear": 60,
                "ast_provided": 1256,
                "asc_provided": 0,
                "stirrup_area": 100.5,
                "stirrup_spacing": 150,
                "fck": 25,
                "fy": 500,
                "clear_cover": 40,
                "effective_depth": 442,
            }
        )


def test_check_supplied_rejects_non_v2_request_at_public_facade() -> None:
    with pytest.raises(InputContractError) as exc_info:
        beam.check_supplied({"schema_version": "beam-supplied-check/v2"})  # type: ignore[arg-type]

    assert exc_info.value.issues[0].code == "INPUT_TYPE_INVALID"
    assert exc_info.value.issues[0].path == "request"
