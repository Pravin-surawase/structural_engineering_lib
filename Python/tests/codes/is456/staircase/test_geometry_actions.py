"""INDIA-2B benchmark and fail-closed staircase action tests."""

from __future__ import annotations

import math

import pytest

from structural_lib.codes.is456.staircase import (
    StaircaseContractError,
    StairSpanDirection,
    StairSupportCase,
    StraightFlightActionInput,
    StraightFlightLoads,
    StraightFlightStairGeometry,
    analyze_straight_flight_actions,
    resolve_straight_flight_geometry,
)


def _benchmark_geometry(**overrides: object) -> StraightFlightStairGeometry:
    values: dict[str, object] = {
        "lower_landing_effective_length_mm": 750.0,
        "going_mm": 2700.0,
        "upper_landing_effective_length_mm": 1650.0,
        "flight_width_mm": 1500.0,
        "riser_mm": 160.0,
        "tread_mm": 270.0,
        "waist_thickness_mm": 250.0,
        "landing_thickness_mm": 200.0,
    }
    values.update(overrides)
    return StraightFlightStairGeometry(**values)  # type: ignore[arg-type]


def _benchmark_input(**load_overrides: object) -> StraightFlightActionInput:
    values: dict[str, object] = {
        "lower_landing_superimposed_service_load_kn_per_m2": 6.0,
        "flight_superimposed_service_load_kn_per_m2": 6.0,
        "upper_landing_superimposed_service_load_kn_per_m2": 6.0,
        "lower_landing_load_share": 0.5,
        "upper_landing_load_share": 1.0,
        "concrete_unit_weight_kn_per_m3": 25.0,
        "ultimate_load_factor": 1.5,
        "load_basis_reference": "NPTEL-M9L20-EX9.1",
    }
    values.update(load_overrides)
    return StraightFlightActionInput(
        geometry=_benchmark_geometry(),
        loads=StraightFlightLoads(**values),  # type: ignore[arg-type]
    )


def test_nptel_example_9_1_geometry_and_load_benchmark() -> None:
    result = analyze_straight_flight_actions(_benchmark_input())

    assert result.geometry.effective_span_mm == pytest.approx(5100.0)
    assert result.geometry.inclined_step_length_mm == pytest.approx(313.85, abs=0.02)
    assert result.geometry.slope_factor == pytest.approx(
        math.hypot(160.0, 270.0) / 270.0
    )
    assert result.waist_self_weight_kn_per_m2 == pytest.approx(7.265, abs=0.002)
    assert result.step_self_weight_kn_per_m2 == pytest.approx(2.0, abs=0.001)
    assert result.flight_factored_load_kn_per_m2 == pytest.approx(22.9, abs=0.02)


def test_nptel_example_9_1_piecewise_action_benchmark() -> None:
    result = analyze_straight_flight_actions(_benchmark_input())

    assert result.total_factored_load_kn == pytest.approx(142.86, abs=0.03)
    assert result.lower_support_reaction_kn == pytest.approx(69.76, abs=0.03)
    assert result.upper_support_reaction_kn == pytest.approx(73.10, abs=0.03)
    assert result.maximum_moment_location_mm == pytest.approx(2510.0, abs=10.0)
    assert result.maximum_factored_moment_knm == pytest.approx(102.08, abs=0.05)
    assert result.segment_boundary_moments_knm[1] == pytest.approx(86.92, abs=0.05)
    assert result.equilibrium_residual_kn == pytest.approx(0.0, abs=1e-12)


def test_unrounded_actions_retain_full_width_and_per_metre_identity() -> None:
    result = analyze_straight_flight_actions(_benchmark_input())

    assert result.maximum_factored_moment_knm_per_m * 1.5 == pytest.approx(
        result.maximum_factored_moment_knm
    )
    assert result.maximum_factored_shear_kn_per_m * 1.5 == pytest.approx(
        result.maximum_factored_shear_kn
    )
    assert result.load_generation_status == "not_generated_caller_supplied_actions"
    assert result.source_refs[-1] == "NPTEL-M9L20-EX9.1"


@pytest.mark.parametrize(
    ("field", "value"),
    (("tread_mm", 0.0), ("going_mm", -1.0), ("waist_thickness_mm", math.inf)),
)
def test_invalid_geometry_fails_closed(field: str, value: float) -> None:
    with pytest.raises(StaircaseContractError, match=field):
        _benchmark_geometry(**{field: value})


def test_unsupported_span_and_support_models_fail_closed() -> None:
    with pytest.raises(StaircaseContractError, match="span_direction"):
        _benchmark_geometry(span_direction=StairSpanDirection.TRANSVERSE)
    with pytest.raises(StaircaseContractError, match="support_case"):
        _benchmark_geometry(
            support_case=StairSupportCase.BEAMS_AT_TOP_AND_BOTTOM_RISERS
        )
    with pytest.raises(StaircaseContractError, match="has_stringer_beams"):
        _benchmark_geometry(has_stringer_beams=True)


def test_landing_share_above_one_fails_closed() -> None:
    with pytest.raises(StaircaseContractError, match="must not exceed 1.0"):
        _benchmark_input(lower_landing_load_share=1.01)


def test_zero_superimposed_actions_preserve_positive_self_weight_analysis() -> None:
    result = analyze_straight_flight_actions(
        _benchmark_input(
            lower_landing_superimposed_service_load_kn_per_m2=0.0,
            flight_superimposed_service_load_kn_per_m2=0.0,
            upper_landing_superimposed_service_load_kn_per_m2=0.0,
        )
    )
    assert result.total_factored_load_kn > 0.0
    assert result.maximum_factored_moment_knm > 0.0


def test_geometry_resolver_rejects_wrong_type() -> None:
    with pytest.raises(StaircaseContractError, match="StraightFlightStairGeometry"):
        resolve_straight_flight_geometry(object())  # type: ignore[arg-type]
