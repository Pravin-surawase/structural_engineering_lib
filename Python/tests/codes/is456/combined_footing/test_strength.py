"""INDIA-2-COMBINED-B strength, detailing, and transfer tests."""

from __future__ import annotations

import math
from dataclasses import FrozenInstanceError

import pytest

from structural_lib.codes.is456.combined_footing import (
    CombinedFootingActionInput,
    CombinedFootingAnalysisMethod,
    CombinedFootingContractError,
    CombinedFootingDesignDisposition,
    CombinedFootingDesignInput,
    CombinedFootingGeometryInput,
    CombinedFootingInput,
    CombinedFootingMaterialInput,
    CombinedFootingPressureModel,
    CombinedFootingReinforcementInput,
    CombinedFootingSupportingAreaBasis,
    CombinedFootingTransferInput,
    check_symmetric_combined_footing_strength,
)
from structural_lib.codes.is456.traceability import get_clause_refs


def _geometry(**overrides: object) -> CombinedFootingGeometryInput:
    values: dict[str, object] = {
        "footing_length_mm": 6000.0,
        "footing_width_mm": 2500.0,
        "overall_depth_mm": 850.0,
        "effective_depth_mm": 750.0,
        "column_side_mm": 500.0,
        "left_column_center_x_mm": 1000.0,
        "right_column_center_x_mm": 5000.0,
        "column_count": 2,
        "columns_identical": True,
        "columns_square": True,
        "columns_centered_across_width": True,
        "foundation_on_soil": True,
        "constant_depth": True,
        "openings_present": False,
        "pedestals_present": False,
        "analysis_method": CombinedFootingAnalysisMethod.CONVENTIONAL_RIGID,
        "pressure_model": CombinedFootingPressureModel.UNIFORM,
        "rigid_footing_verified": True,
        "rigidity_basis_reference": "INDIA-2-COMBINED-HAND-01-RIGIDITY",
        "geometry_basis_reference": "INDIA-2-COMBINED-HAND-01-GEOMETRY",
    }
    values.update(overrides)
    return CombinedFootingGeometryInput(**values)  # type: ignore[arg-type]


def _actions(**overrides: object) -> CombinedFootingActionInput:
    values: dict[str, object] = {
        "service_axial_load_each_kn": 900.0,
        "factored_axial_load_each_kn": 1350.0,
        "service_uniform_carrier_kn_per_m2": 25.0,
        "factored_uniform_carrier_kn_per_m2": 37.5,
        "allowable_gross_bearing_pressure_kn_per_m2": 150.0,
        "load_combination_approved": True,
        "bearing_and_settlement_approved": True,
        "pressure_uniformity_approved": True,
        "distributed_carrier_cancellation_approved": True,
        "column_moments_present": False,
        "horizontal_actions_present": False,
        "uplift_or_load_reversal_present": False,
        "load_basis_reference": "INDIA-2-COMBINED-HAND-01-LOAD",
        "bearing_settlement_basis_reference": "INDIA-2-COMBINED-HAND-01-BEARING",
        "cancellation_basis_reference": "INDIA-2-COMBINED-HAND-01-CANCELLATION",
    }
    values.update(overrides)
    return CombinedFootingActionInput(**values)  # type: ignore[arg-type]


def _material(**overrides: object) -> CombinedFootingMaterialInput:
    values: dict[str, object] = {
        "footing_concrete_grade_nmm2": 30.0,
        "column_concrete_grade_nmm2": 30.0,
        "steel_grade_nmm2": 500.0,
        "uncoated_deformed_bars": True,
        "material_basis_reference": "INDIA-2-COMBINED-HAND-01-MATERIAL",
    }
    values.update(overrides)
    return CombinedFootingMaterialInput(**values)  # type: ignore[arg-type]


def _reinforcement(**overrides: object) -> CombinedFootingReinforcementInput:
    values: dict[str, object] = {
        "top_longitudinal_diameter_mm": 16.0,
        "top_longitudinal_spacing_mm": 190.0,
        "bottom_longitudinal_diameter_mm": 16.0,
        "bottom_longitudinal_spacing_mm": 190.0,
        "transverse_diameter_mm": 12.0,
        "transverse_spacing_mm": 110.0,
        "nominal_cover_mm": 50.0,
        "aggregate_size_mm": 20.0,
        "available_top_longitudinal_anchorage_each_end_mm": 800.0,
        "available_bottom_longitudinal_anchorage_each_end_mm": 800.0,
        "available_transverse_anchorage_each_edge_mm": 800.0,
        "straight_uncoated_deformed_bars": True,
        "effective_depth_basis_approved": True,
        "reinforcement_schedule_approved": True,
        "detailing_basis_reference": "INDIA-2-COMBINED-HAND-01-DETAILING",
    }
    values.update(overrides)
    return CombinedFootingReinforcementInput(**values)  # type: ignore[arg-type]


def _transfer(**overrides: object) -> CombinedFootingTransferInput:
    values: dict[str, object] = {
        "effective_supporting_area_each_mm2": 250000.0,
        "effective_supporting_area_basis": (
            CombinedFootingSupportingAreaBasis.LARGEST_FRUSTUM_1V_2H
        ),
        "effective_supporting_area_approved": True,
        "dowel_count_each": 4,
        "dowel_diameter_mm": 20.0,
        "column_longitudinal_bar_diameter_mm": 20.0,
        "available_dowel_development_into_footing_mm": 800.0,
        "available_dowel_development_into_column_mm": 800.0,
        "uncoated_deformed_dowels": True,
        "transfer_basis_reference": "INDIA-2-COMBINED-HAND-01-TRANSFER",
    }
    values.update(overrides)
    return CombinedFootingTransferInput(**values)  # type: ignore[arg-type]


def _design_input(**overrides: object) -> CombinedFootingDesignInput:
    values: dict[str, object] = {
        "analysis": CombinedFootingInput(_geometry(), _actions()),
        "material": _material(),
        "reinforcement": _reinforcement(),
        "transfer": _transfer(),
    }
    values.update(overrides)
    return CombinedFootingDesignInput(**values)  # type: ignore[arg-type]


def test_frozen_benchmark_passes_with_review_boundary() -> None:
    result = check_symmetric_combined_footing_strength(_design_input())

    assert result.disposition is CombinedFootingDesignDisposition.PASS
    assert result.is_safe_within_supported_scope is True
    assert result.qualified_review_required is True
    assert result.complete_engineering_approval is False
    assert result.reasons == (
        "Every represented service, strength and detailing check passes.",
    )


def test_exact_stress_block_minimum_and_provided_steel_benchmark() -> None:
    result = check_symmetric_combined_footing_strength(_design_input())
    top = result.top_longitudinal_flexure
    bottom = result.bottom_longitudinal_flexure
    transverse = result.transverse_flexure

    assert top.factored_moment_kn_m == pytest.approx(675.0)
    assert top.flexural_steel_required_mm2 == pytest.approx(2109.099057848993)
    assert top.minimum_steel_required_mm2 == pytest.approx(2550.0)
    assert top.governing_steel_required_mm2 == pytest.approx(2550.0)
    assert top.provided_steel_area_mm2 == pytest.approx(2645.551708286142)
    assert bottom.factored_moment_kn_m == pytest.approx(126.5625)
    assert bottom.flexural_steel_required_mm2 == pytest.approx(389.298381400156)
    assert bottom.minimum_steel_required_mm2 == pytest.approx(2550.0)
    assert bottom.provided_steel_area_mm2 == pytest.approx(2645.551708286142)
    assert transverse.factored_moment_kn_m == pytest.approx(90.0)
    assert transverse.flexural_steel_required_mm2 == pytest.approx(277.600242815144)
    assert transverse.minimum_steel_required_mm2 == pytest.approx(1020.0)
    assert transverse.provided_steel_area_mm2 == pytest.approx(1028.157595720296)
    assert all(item.is_safe for item in (top, bottom, transverse))


def test_spacing_cover_and_tension_anchorage_benchmark() -> None:
    result = check_symmetric_combined_footing_strength(_design_input())

    for item in (
        result.top_longitudinal_flexure,
        result.bottom_longitudinal_flexure,
        result.transverse_flexure,
    ):
        assert item.maximum_bar_spacing_mm == pytest.approx(300.0)
        assert item.minimum_nominal_cover_mm == pytest.approx(50.0)
        assert item.nominal_cover_is_safe is True
        assert item.bar_diameter_is_safe is True
        assert item.bar_spacing_is_safe is True
        assert item.clear_spacing_is_safe is True
        assert item.anchorage_is_safe is True
    assert result.top_longitudinal_flexure.required_tension_development_length_mm == (
        pytest.approx(725.0)
    )
    assert (
        result.bottom_longitudinal_flexure.required_tension_development_length_mm
        == (pytest.approx(725.0))
    )
    assert result.transverse_flexure.required_tension_development_length_mm == (
        pytest.approx(543.75)
    )


def test_frozen_longitudinal_and_transverse_one_way_shear() -> None:
    result = check_symmetric_combined_footing_strength(_design_input())
    left_outer, left_inner, right_inner, right_outer = result.longitudinal_one_way_shear

    assert left_outer.factored_shear_demand_kn == pytest.approx(0.0)
    assert right_outer.factored_shear_demand_kn == pytest.approx(0.0)
    for item in (left_inner, right_inner):
        assert item.factored_shear_demand_kn == pytest.approx(450.0)
        assert item.tension_reinforcement_percent == pytest.approx(0.141096091108594)
        assert item.table_19_lookup_reinforcement_percent == pytest.approx(0.15)
        assert item.nominal_shear_stress_nmm2 == pytest.approx(0.24)
        assert item.concrete_design_shear_strength_nmm2 == pytest.approx(0.29)
        assert item.utilization == pytest.approx(0.827586206896552)
        assert item.is_safe_without_shear_reinforcement is True
    transverse = result.transverse_one_way_shear
    assert transverse.factored_shear_demand_kn == pytest.approx(45.0)
    assert transverse.table_19_lookup_reinforcement_percent == pytest.approx(0.15)
    assert transverse.nominal_shear_stress_nmm2 == pytest.approx(0.06)
    assert transverse.concrete_design_shear_strength_nmm2 == pytest.approx(0.29)
    assert transverse.utilization == pytest.approx(0.206896551724138)


def test_frozen_concrete_only_punching_at_both_columns() -> None:
    result = check_symmetric_combined_footing_strength(_design_input())

    assert tuple(item.column for item in result.punching) == ("left", "right")
    for item in result.punching:
        assert item.critical_enclosed_area_m2 == pytest.approx(1.5625)
        assert item.critical_perimeter_mm == pytest.approx(5000.0)
        assert item.factored_punching_shear_kn == pytest.approx(1068.75)
        assert item.nominal_punching_stress_nmm2 == pytest.approx(0.285)
        assert item.size_factor_ks == pytest.approx(1.0)
        assert item.concrete_capacity_nmm2 == pytest.approx(1.369306393762915)
        assert item.utilization == pytest.approx(0.208134571851963)
        assert item.is_safe_without_punching_reinforcement is True


def test_frozen_bearing_dowels_and_compression_development() -> None:
    result = check_symmetric_combined_footing_strength(_design_input())

    for item in result.load_transfer:
        assert item.actual_bearing_stress_nmm2 == pytest.approx(5.4)
        assert item.bearing_enhancement_factor == pytest.approx(1.0)
        assert item.governing_concrete_bearing_capacity_kn == pytest.approx(3375.0)
        assert item.minimum_transfer_steel_area_mm2 == pytest.approx(1250.0)
        assert item.required_transfer_steel_area_mm2 == pytest.approx(1250.0)
        assert item.provided_transfer_steel_area_mm2 == pytest.approx(1256.637061435917)
        assert item.footing_compression_design_bond_stress_nmm2 == pytest.approx(3.0)
        assert item.column_compression_design_bond_stress_nmm2 == pytest.approx(3.0)
        assert item.required_development_into_footing_mm == pytest.approx(725.0)
        assert item.required_development_into_column_mm == pytest.approx(725.0)
        assert item.is_safe is True


@pytest.mark.parametrize(
    ("reinforcement", "field_name"),
    (
        (
            _reinforcement(top_longitudinal_spacing_mm=250.0),
            "reinforcement_area_is_safe",
        ),
        (_reinforcement(transverse_spacing_mm=400.0), "bar_spacing_is_safe"),
        (_reinforcement(nominal_cover_mm=49.0), "nominal_cover_is_safe"),
        (
            _reinforcement(available_top_longitudinal_anchorage_each_end_mm=724.0),
            "anchorage_is_safe",
        ),
    ),
)
def test_valid_inadequate_reinforcement_or_detailing_returns_fail(
    reinforcement: CombinedFootingReinforcementInput,
    field_name: str,
) -> None:
    result = check_symmetric_combined_footing_strength(
        _design_input(reinforcement=reinforcement)
    )

    assert result.disposition is CombinedFootingDesignDisposition.FAIL
    relevant = (
        result.top_longitudinal_flexure,
        result.bottom_longitudinal_flexure,
        result.transverse_flexure,
    )
    assert any(getattr(item, field_name) is False for item in relevant)


def test_valid_service_bearing_exceedance_returns_fail() -> None:
    analysis = CombinedFootingInput(
        _geometry(),
        _actions(allowable_gross_bearing_pressure_kn_per_m2=140.0),
    )
    result = check_symmetric_combined_footing_strength(_design_input(analysis=analysis))

    assert result.disposition is CombinedFootingDesignDisposition.FAIL
    assert result.actions.gross_service_bearing_within_allowable is False
    assert "Approved gross service bearing pressure is exceeded." in result.reasons


def test_valid_one_way_shear_exceedance_returns_fail() -> None:
    analysis = CombinedFootingInput(
        _geometry(),
        _actions(
            service_axial_load_each_kn=1200.0,
            factored_axial_load_each_kn=1800.0,
            allowable_gross_bearing_pressure_kn_per_m2=200.0,
        ),
    )
    result = check_symmetric_combined_footing_strength(_design_input(analysis=analysis))

    assert result.disposition is CombinedFootingDesignDisposition.FAIL
    assert result.longitudinal_one_way_shear[1].nominal_shear_stress_nmm2 == (
        pytest.approx(0.32)
    )
    assert (
        result.longitudinal_one_way_shear[1].is_safe_without_shear_reinforcement
        is False
    )


def test_valid_punching_and_singly_reinforced_capacity_exceedance_returns_fail() -> (
    None
):
    analysis = CombinedFootingInput(
        _geometry(),
        _actions(
            service_axial_load_each_kn=8000.0,
            factored_axial_load_each_kn=12000.0,
            allowable_gross_bearing_pressure_kn_per_m2=1200.0,
        ),
    )
    result = check_symmetric_combined_footing_strength(_design_input(analysis=analysis))

    assert result.disposition is CombinedFootingDesignDisposition.FAIL
    assert result.punching[0].is_safe_without_punching_reinforcement is False
    assert result.top_longitudinal_flexure.singly_reinforced_capacity_is_sufficient is (
        False
    )
    assert result.top_longitudinal_flexure.flexural_steel_required_mm2 is None
    assert result.top_longitudinal_flexure.governing_steel_required_mm2 is None


@pytest.mark.parametrize(
    ("transfer", "field_name"),
    (
        (_transfer(dowel_count_each=3), "bar_count_is_safe"),
        (_transfer(dowel_diameter_mm=25.0), "dowel_diameter_is_safe"),
        (
            _transfer(available_dowel_development_into_footing_mm=700.0),
            "footing_development_is_safe",
        ),
        (
            _transfer(available_dowel_development_into_column_mm=700.0),
            "column_development_is_safe",
        ),
    ),
)
def test_valid_inadequate_transfer_provision_returns_fail(
    transfer: CombinedFootingTransferInput,
    field_name: str,
) -> None:
    result = check_symmetric_combined_footing_strength(_design_input(transfer=transfer))

    assert result.disposition is CombinedFootingDesignDisposition.FAIL
    assert all(getattr(item, field_name) is False for item in result.load_transfer)


@pytest.mark.parametrize(
    ("factory", "message"),
    (
        (lambda: _material(footing_concrete_grade_nmm2=45.0), "footing_concrete"),
        (lambda: _material(steel_grade_nmm2=550.0), "steel_grade"),
        (lambda: _material(uncoated_deformed_bars=False), "uncoated_deformed_bars"),
        (
            lambda: _reinforcement(reinforcement_schedule_approved=False),
            "reinforcement_schedule_approved",
        ),
        (
            lambda: _transfer(effective_supporting_area_basis="full_plan"),
            "effective_supporting_area_basis",
        ),
        (lambda: _transfer(dowel_count_each=0), "dowel_count_each"),
        (
            lambda: _transfer(column_longitudinal_bar_diameter_mm=40.0),
            "Clause 34.4.4",
        ),
    ),
)
def test_out_of_domain_material_and_approval_inputs_fail_closed(
    factory: object,
    message: str,
) -> None:
    with pytest.raises(CombinedFootingContractError, match=message):
        factory()  # type: ignore[operator]


def test_effective_supporting_area_smaller_than_column_fails_closed() -> None:
    with pytest.raises(
        CombinedFootingContractError,
        match="effective_supporting_area_each_mm2",
    ):
        check_symmetric_combined_footing_strength(
            _design_input(
                transfer=_transfer(effective_supporting_area_each_mm2=249999.0)
            )
        )


def test_wrong_top_level_type_fails_closed() -> None:
    with pytest.raises(CombinedFootingContractError, match="footing_input"):
        check_symmetric_combined_footing_strength("not-an-input")  # type: ignore[arg-type]


def test_result_is_frozen_deterministic_and_finite() -> None:
    first = check_symmetric_combined_footing_strength(_design_input())
    second = check_symmetric_combined_footing_strength(_design_input())

    assert first == second
    with pytest.raises(FrozenInstanceError):
        first.disposition = CombinedFootingDesignDisposition.FAIL  # type: ignore[misc]
    numeric_values = (
        first.top_longitudinal_flexure.flexural_steel_required_mm2,
        first.longitudinal_one_way_shear[1].utilization,
        first.punching[0].utilization,
        first.load_transfer[0].required_development_into_footing_mm,
    )
    assert all(value is not None and math.isfinite(value) for value in numeric_values)


def test_clause_and_source_traceability_are_explicit() -> None:
    refs = get_clause_refs(check_symmetric_combined_footing_strength)
    result = check_symmetric_combined_footing_strength(_design_input())

    assert refs == [
        "26.2.1",
        "26.2.1.1",
        "26.3.2",
        "26.3.3",
        "26.4.2.2",
        "26.5.2.1",
        "26.5.2.2",
        "31.6.1",
        "31.6.2.1",
        "31.6.3.1",
        "34.1",
        "34.2.3.1",
        "34.2.4.1",
        "34.2.4.3",
        "34.3",
        "34.4",
        "34.4.1",
        "34.4.2",
        "34.4.3",
        "34.5.1",
        "38.1",
        "G-1.1",
        "40.1",
        "40.2",
    ]
    assert result.source_refs[0].startswith("IS456-2000-A5:sha256:")
    assert result.source_refs[1].startswith("IS456-AMD6-2024:sha256:")
    assert "INDIA-2-COMBINED-HAND-01" in result.source_refs
    assert any("Qualified engineering review" in item for item in result.limitations)
