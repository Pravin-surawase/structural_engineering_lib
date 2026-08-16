"""INDIA-2-FOUNDATION-STRAP-A benchmark and boundary tests."""

from __future__ import annotations

import math
from dataclasses import FrozenInstanceError

import pytest

from structural_lib.codes.is456.strap_footing import (
    StrapFootingActionInput,
    StrapFootingAnalysisInput,
    StrapFootingAnalysisMethod,
    StrapFootingApprovalInput,
    StrapFootingContractError,
    StrapFootingGeometryInput,
    StrapFootingPressureModel,
    StrapFootingTensionFace,
    analyze_property_line_strap_footing,
    resolve_property_line_strap_geometry,
)
from structural_lib.codes.is456.traceability import get_clause_refs


def _geometry(**overrides: object) -> StrapFootingGeometryInput:
    values: dict[str, object] = {
        "exterior_footing_length_mm": 2400.0,
        "exterior_footing_width_mm": 2500.0,
        "exterior_footing_depth_mm": 700.0,
        "interior_footing_length_mm": 2500.0,
        "interior_footing_width_mm": 3200.0,
        "interior_footing_depth_mm": 700.0,
        "exterior_column_side_mm": 500.0,
        "interior_column_side_mm": 500.0,
        "exterior_column_center_x_mm": 400.0,
        "interior_column_center_x_mm": 6400.0,
        "strap_width_mm": 500.0,
        "strap_overall_depth_mm": 950.0,
        "strap_effective_depth_mm": 850.0,
        "footing_count": 2,
        "column_count": 2,
        "footings_rectangular": True,
        "footings_parallel": True,
        "footings_constant_depth": True,
        "columns_square": True,
        "columns_and_strap_share_centerline": True,
        "interior_column_centered_on_footing": True,
        "strap_straight_and_prismatic": True,
        "strap_centered_across_footings": True,
        "foundation_on_soil": True,
        "strap_soil_contact": False,
        "openings_present": False,
        "pedestals_present": False,
        "analysis_method": StrapFootingAnalysisMethod.RIGID_EQUAL_PRESSURE,
        "pressure_model": StrapFootingPressureModel.EQUAL_UNIFORM_NET,
        "geometry_basis_reference": "INDIA-2-STRAP-HAND-01-GEOMETRY",
        "rigidity_basis_reference": "INDIA-2-STRAP-HAND-01-RIGIDITY",
        "strap_isolation_basis_reference": "INDIA-2-STRAP-HAND-01-ISOLATION",
    }
    values.update(overrides)
    return StrapFootingGeometryInput(**values)  # type: ignore[arg-type]


def _actions(**overrides: object) -> StrapFootingActionInput:
    values: dict[str, object] = {
        "service_exterior_column_load_kn": 1025.5625,
        "service_interior_column_load_kn": 1741.4375,
        "factored_exterior_column_load_kn": 1538.34375,
        "factored_interior_column_load_kn": 2612.15625,
        "service_clear_strap_line_load_kn_per_m": 12.0,
        "factored_clear_strap_line_load_kn_per_m": 18.0,
        "service_exterior_footing_carrier_kn_per_m2": 20.0,
        "service_interior_footing_carrier_kn_per_m2": 20.0,
        "factored_exterior_footing_carrier_kn_per_m2": 30.0,
        "factored_interior_footing_carrier_kn_per_m2": 30.0,
        "allowable_gross_bearing_pressure_kn_per_m2": 250.0,
        "load_combination_approved": True,
        "bearing_and_settlement_approved": True,
        "equal_uniform_pressure_approved": True,
        "footing_carrier_basis_approved": True,
        "strap_line_load_basis_approved": True,
        "load_pattern_compatible": True,
        "column_moments_present": False,
        "horizontal_actions_present": False,
        "uplift_or_load_reversal_present": False,
        "independently_factored_or_patterned_actions_present": False,
        "load_basis_reference": "INDIA-2-STRAP-HAND-01-LOAD",
        "bearing_settlement_basis_reference": "INDIA-2-STRAP-HAND-01-GEOTECH",
        "footing_carrier_basis_reference": "INDIA-2-STRAP-HAND-01-CARRIER",
        "strap_line_load_basis_reference": "INDIA-2-STRAP-HAND-01-LINE-LOAD",
        "load_pattern_basis_reference": "INDIA-2-STRAP-HAND-01-PATTERN",
    }
    values.update(overrides)
    return StrapFootingActionInput(**values)  # type: ignore[arg-type]


def _approvals(**overrides: object) -> StrapFootingApprovalInput:
    values: dict[str, object] = {
        "exterior_footing_design_verified": True,
        "interior_footing_design_verified": True,
        "column_and_strap_transfer_verified": True,
        "footing_reinforcement_and_anchorage_verified": True,
        "supporting_areas_verified": True,
        "construction_clearances_verified": True,
        "exterior_footing_verification_reference": "EXT-FOOTING-01",
        "interior_footing_verification_reference": "INT-FOOTING-01",
        "transfer_verification_reference": "TRANSFER-01",
        "construction_verification_reference": "CONSTRUCTION-01",
    }
    values.update(overrides)
    return StrapFootingApprovalInput(**values)  # type: ignore[arg-type]


def _input(**overrides: object) -> StrapFootingAnalysisInput:
    values: dict[str, object] = {
        "geometry": _geometry(),
        "actions": _actions(),
        "approvals": _approvals(),
    }
    values.update(overrides)
    return StrapFootingAnalysisInput(**values)  # type: ignore[arg-type]


def test_frozen_geometry_is_resolved_exactly() -> None:
    result = resolve_property_line_strap_geometry(_geometry())

    assert result.exterior_footing_area_m2 == pytest.approx(6.0)
    assert result.interior_footing_area_m2 == pytest.approx(8.0)
    assert result.exterior_footing_centroid_x_mm == pytest.approx(1200.0)
    assert result.interior_footing_centroid_x_mm == pytest.approx(6400.0)
    assert result.exterior_column_eccentricity_mm == pytest.approx(800.0)
    assert result.reaction_spacing_mm == pytest.approx(5200.0)
    assert result.clear_strap_start_x_mm == pytest.approx(2400.0)
    assert result.clear_strap_end_x_mm == pytest.approx(5150.0)
    assert result.clear_strap_length_mm == pytest.approx(2750.0)
    assert result.clear_strap_centroid_x_mm == pytest.approx(3775.0)
    assert result.clear_span_to_overall_depth_ratio == pytest.approx(2750.0 / 950.0)
    assert result.rigid_equal_pressure_eligible is True


def test_frozen_reactions_bearing_and_equilibrium_are_exact() -> None:
    result = analyze_property_line_strap_footing(_input())

    assert result.service.exterior_reaction_kn == pytest.approx(1200.0)
    assert result.service.interior_reaction_kn == pytest.approx(1600.0)
    assert result.service.exterior_net_pressure_kn_per_m2 == pytest.approx(200.0)
    assert result.service.interior_net_pressure_kn_per_m2 == pytest.approx(200.0)
    assert result.service.exterior_gross_pressure_kn_per_m2 == pytest.approx(220.0)
    assert result.service.interior_gross_pressure_kn_per_m2 == pytest.approx(220.0)
    assert result.exterior_service_bearing_utilization == pytest.approx(0.88)
    assert result.interior_service_bearing_utilization == pytest.approx(0.88)
    assert result.gross_service_bearing_within_allowable is True
    assert result.factored.exterior_reaction_kn == pytest.approx(1800.0)
    assert result.factored.interior_reaction_kn == pytest.approx(2400.0)
    assert result.factored.exterior_net_pressure_kn_per_m2 == pytest.approx(300.0)
    assert result.factored.interior_net_pressure_kn_per_m2 == pytest.approx(300.0)
    assert result.common_factored_multiplier == pytest.approx(1.5)
    assert result.service.vertical_equilibrium_residual_kn == pytest.approx(0.0)
    assert result.service.moment_equilibrium_residual_kn_m == pytest.approx(0.0)
    assert result.factored.vertical_equilibrium_residual_kn == pytest.approx(0.0)
    assert result.factored.moment_equilibrium_residual_kn_m == pytest.approx(0.0)


def test_frozen_clear_strap_actions_are_exact() -> None:
    result = analyze_property_line_strap_footing(_input())

    assert result.service_clear_strap.exterior_face_shear_kn == pytest.approx(174.4375)
    assert result.service_clear_strap.exterior_face_moment_kn_m == pytest.approx(
        -611.125
    )
    assert result.service_clear_strap.interior_face_shear_kn == pytest.approx(141.4375)
    assert result.service_clear_strap.interior_face_moment_kn_m == pytest.approx(
        -176.796875
    )
    assert result.factored_clear_strap.governing_shear_demand_kn == pytest.approx(
        261.65625
    )
    assert result.factored_clear_strap.governing_moment_demand_kn_m == pytest.approx(
        916.6875
    )
    assert result.factored_clear_strap.governing_moment_x_mm == pytest.approx(2400.0)
    assert (
        result.factored_clear_strap.governing_tension_face
        is StrapFootingTensionFace.TOP
    )


def test_zero_strap_load_reduces_to_source_reaction_equations() -> None:
    q1 = 1200.0 / (1.0 + 0.8 / 5.2)
    q2 = 2800.0 - q1
    actions = _actions(
        service_exterior_column_load_kn=q1,
        service_interior_column_load_kn=q2,
        factored_exterior_column_load_kn=1.5 * q1,
        factored_interior_column_load_kn=1.5 * q2,
        service_clear_strap_line_load_kn_per_m=0.0,
        factored_clear_strap_line_load_kn_per_m=0.0,
    )
    result = analyze_property_line_strap_footing(_input(actions=actions))

    expected_r1 = q1 * (1.0 + 0.8 / 5.2)
    expected_r2 = q2 - q1 * 0.8 / 5.2
    assert result.service.exterior_reaction_kn == pytest.approx(expected_r1)
    assert result.service.interior_reaction_kn == pytest.approx(expected_r2)


def test_valid_bearing_failure_is_reported() -> None:
    result = analyze_property_line_strap_footing(
        _input(actions=_actions(allowable_gross_bearing_pressure_kn_per_m2=210.0))
    )
    assert result.gross_service_bearing_within_allowable is False


def test_pressure_mismatch_fails_closed() -> None:
    with pytest.raises(StrapFootingContractError, match="net footing pressures"):
        analyze_property_line_strap_footing(
            _input(geometry=_geometry(exterior_footing_width_mm=2400.0))
        )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("exterior_footing_length_mm", 0.0),
        ("interior_footing_width_mm", math.inf),
        ("strap_overall_depth_mm", math.nan),
        ("strap_effective_depth_mm", -1.0),
        ("exterior_column_side_mm", True),
        ("interior_column_center_x_mm", "6400"),
    ),
)
def test_invalid_geometry_scalars_fail_closed(field: str, value: object) -> None:
    with pytest.raises(StrapFootingContractError, match=field):
        _geometry(**{field: value})


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("footing_count", 3),
        ("column_count", 3),
        ("footings_rectangular", False),
        ("columns_square", False),
        ("interior_column_centered_on_footing", False),
        ("strap_straight_and_prismatic", False),
        ("foundation_on_soil", False),
        ("strap_soil_contact", True),
        ("openings_present", True),
        ("pedestals_present", True),
        ("analysis_method", "elastic"),
        ("pressure_model", "linear"),
    ),
)
def test_each_geometry_scope_carrier_fails_closed(field: str, value: object) -> None:
    with pytest.raises(StrapFootingContractError, match=field):
        _geometry(**{field: value})


def test_geometry_boundaries_fail_closed() -> None:
    with pytest.raises(StrapFootingContractError, match="at least 150"):
        _geometry(exterior_footing_depth_mm=149.0)
    with pytest.raises(StrapFootingContractError, match="less than strap_overall"):
        _geometry(strap_effective_depth_mm=950.0)
    with pytest.raises(StrapFootingContractError, match="complete exterior column"):
        _geometry(exterior_column_center_x_mm=200.0)
    with pytest.raises(StrapFootingContractError, match="property-line edge"):
        _geometry(exterior_column_center_x_mm=1300.0)
    with pytest.raises(StrapFootingContractError, match="positive clear separation"):
        _geometry(interior_column_center_x_mm=3600.0)
    with pytest.raises(StrapFootingContractError, match="span-to-overall-depth"):
        _geometry(strap_overall_depth_mm=1100.0)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("service_exterior_column_load_kn", 0.0),
        ("factored_interior_column_load_kn", math.inf),
        ("service_clear_strap_line_load_kn_per_m", math.nan),
        ("factored_exterior_footing_carrier_kn_per_m2", -1.0),
        ("allowable_gross_bearing_pressure_kn_per_m2", True),
    ),
)
def test_invalid_action_scalars_fail_closed(field: str, value: object) -> None:
    with pytest.raises(StrapFootingContractError, match=field):
        _actions(**{field: value})


def test_action_factor_boundaries_fail_closed() -> None:
    with pytest.raises(StrapFootingContractError, match="must not be less"):
        _actions(factored_exterior_column_load_kn=1000.0)
    with pytest.raises(StrapFootingContractError, match="common multiplier"):
        _actions(factored_interior_column_load_kn=2600.0)
    with pytest.raises(StrapFootingContractError, match="zero service"):
        _actions(
            service_clear_strap_line_load_kn_per_m=0.0,
            factored_clear_strap_line_load_kn_per_m=1.0,
        )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("load_combination_approved", False),
        ("bearing_and_settlement_approved", False),
        ("equal_uniform_pressure_approved", False),
        ("load_pattern_compatible", False),
        ("column_moments_present", True),
        ("horizontal_actions_present", True),
        ("uplift_or_load_reversal_present", True),
        ("independently_factored_or_patterned_actions_present", True),
    ),
)
def test_each_action_scope_carrier_fails_closed(field: str, value: object) -> None:
    with pytest.raises(StrapFootingContractError, match=field):
        _actions(**{field: value})


def test_external_approvals_and_references_are_required() -> None:
    with pytest.raises(StrapFootingContractError, match="supporting_areas_verified"):
        _approvals(supporting_areas_verified=False)
    with pytest.raises(
        StrapFootingContractError, match="transfer_verification_reference"
    ):
        _approvals(transfer_verification_reference=" ")
    with pytest.raises(StrapFootingContractError, match="geometry_basis_reference"):
        _geometry(geometry_basis_reference=" ")
    with pytest.raises(StrapFootingContractError, match="load_basis_reference"):
        _actions(load_basis_reference=" ")


def test_wrong_typed_inputs_fail_closed() -> None:
    with pytest.raises(StrapFootingContractError, match="geometry"):
        StrapFootingAnalysisInput(  # type: ignore[arg-type]
            geometry=object(), actions=_actions(), approvals=_approvals()
        )
    with pytest.raises(StrapFootingContractError, match="geometry"):
        resolve_property_line_strap_geometry(object())  # type: ignore[arg-type]
    with pytest.raises(StrapFootingContractError, match="footing_input"):
        analyze_property_line_strap_footing(object())  # type: ignore[arg-type]


def test_results_are_frozen_deterministic_and_source_bound() -> None:
    first = analyze_property_line_strap_footing(_input())
    second = analyze_property_line_strap_footing(_input())
    assert first == second
    assert first.source_refs[:5] == (
        "IS 456:2000 Cl. 34.1, 34.1.2, 34.2.3.1",
        "IS456-2000-A5",
        "IS456-AMD6-2024",
        "NPTEL-AFE-C3-STRAP Section 3.6.1 and Fig. 3.2",
        "INDIA-2-STRAP-HAND-01",
    )
    with pytest.raises(FrozenInstanceError):
        first.common_factored_multiplier = 1.0  # type: ignore[misc]


def test_clause_registration_is_exact() -> None:
    assert get_clause_refs(resolve_property_line_strap_geometry) == ["34.1", "34.1.2"]
    assert get_clause_refs(analyze_property_line_strap_footing) == [
        "34.1",
        "34.2.3.1",
    ]
