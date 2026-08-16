"""INDIA-2-FOUNDATION-STRAP-B strength and detailing tests."""

from __future__ import annotations

import math
from dataclasses import FrozenInstanceError

import pytest

from structural_lib.codes.is456.strap_footing import (
    StrapFootingDesignDisposition,
    StrapFootingDesignInput,
    StrapFootingMaterialInput,
    StrapFootingReinforcementInput,
    StrapFootingTensionFace,
    check_property_line_strap_footing_strength,
)
from structural_lib.codes.is456.strap_footing.models import StrapFootingContractError
from structural_lib.codes.is456.traceability import get_clause_info, get_clause_refs

from .test_analysis import _actions, _input


def _material(**overrides: object) -> StrapFootingMaterialInput:
    values: dict[str, object] = {
        "strap_concrete_grade_nmm2": 30.0,
        "steel_grade_nmm2": 500.0,
        "uncoated_deformed_bars": True,
        "material_basis_reference": "INDIA-2-STRAP-HAND-01-MATERIAL",
    }
    values.update(overrides)
    return StrapFootingMaterialInput(**values)  # type: ignore[arg-type]


def _reinforcement(**overrides: object) -> StrapFootingReinforcementInput:
    values: dict[str, object] = {
        "top_bar_count": 6,
        "top_bar_diameter_mm": 25.0,
        "bottom_bar_count": 4,
        "bottom_bar_diameter_mm": 16.0,
        "side_face_bar_count_each_face": 4,
        "side_face_bar_diameter_mm": 12.0,
        "side_face_vertical_spacing_mm": 250.0,
        "stirrup_leg_count": 2,
        "stirrup_diameter_mm": 10.0,
        "stirrup_spacing_mm": 250.0,
        "nominal_cover_mm": 50.0,
        "required_nominal_cover_mm": 50.0,
        "maximum_aggregate_size_mm": 20.0,
        "available_top_anchorage_exterior_mm": 1200.0,
        "available_top_anchorage_interior_mm": 1200.0,
        "available_bottom_anchorage_exterior_mm": 1200.0,
        "available_bottom_anchorage_interior_mm": 1200.0,
        "vertical_closed_stirrups": True,
        "straight_anchorage": True,
        "bars_bundled": False,
        "bars_spliced": False,
        "bars_curtailed": False,
        "reinforcement_schedule_approved": True,
        "effective_depth_basis_approved": True,
        "durability_cover_basis_approved": True,
        "detailing_basis_reference": "INDIA-2-STRAP-HAND-01-DETAILING",
        "durability_basis_reference": "INDIA-2-STRAP-HAND-01-DURABILITY",
    }
    values.update(overrides)
    return StrapFootingReinforcementInput(**values)  # type: ignore[arg-type]


def _design_input(**overrides: object) -> StrapFootingDesignInput:
    values: dict[str, object] = {
        "analysis": _input(),
        "material": _material(),
        "reinforcement": _reinforcement(),
    }
    values.update(overrides)
    return StrapFootingDesignInput(**values)  # type: ignore[arg-type]


def test_frozen_benchmark_passes_with_review_boundary() -> None:
    result = check_property_line_strap_footing_strength(_design_input())

    assert result.disposition is StrapFootingDesignDisposition.PASS
    assert result.is_safe_within_supported_scope is True
    assert result.qualified_review_required is True
    assert result.complete_engineering_approval is False
    assert result.reasons == (
        "Every represented service, strength and detailing check passes.",
    )


def test_exact_stress_block_and_longitudinal_steel_benchmark() -> None:
    result = check_property_line_strap_footing_strength(_design_input()).flexure

    assert result.governing_tension_face is StrapFootingTensionFace.TOP
    assert result.factored_moment_demand_kn_m == pytest.approx(916.6875)
    assert result.limiting_singly_reinforced_moment_kn_m == pytest.approx(1447.955892)
    assert result.exact_flexural_steel_required_mm2 == pytest.approx(2788.774499810215)
    assert result.exact_neutral_axis_depth_mm == pytest.approx(224.651279151378)
    assert result.beam_minimum_steel_required_mm2 == pytest.approx(722.5)
    assert result.top_steel_required_mm2 == pytest.approx(2788.774499810215)
    assert result.bottom_steel_required_mm2 == pytest.approx(722.5)
    assert result.top_steel_provided_mm2 == pytest.approx(2945.243112740431)
    assert result.bottom_steel_provided_mm2 == pytest.approx(804.247719318987)
    assert result.top_moment_capacity_kn_m == pytest.approx(961.337320139164)
    assert result.top_area_is_safe is True
    assert result.bottom_area_is_safe is True


def test_clear_spacing_cover_and_anchorage_benchmark() -> None:
    result = check_property_line_strap_footing_strength(_design_input()).flexure

    assert result.top_clear_spacing_mm == pytest.approx(46.0)
    assert result.bottom_clear_spacing_mm == pytest.approx(105.333333333333)
    assert result.minimum_top_clear_spacing_mm == pytest.approx(25.0)
    assert result.nominal_cover_is_safe is True
    assert result.tension_design_bond_stress_nmm2 == pytest.approx(2.4)
    assert result.top_development_length_required_mm == pytest.approx(1132.8125)
    assert result.bottom_development_length_required_mm == pytest.approx(725.0)
    assert result.top_anchorage_is_safe is True
    assert result.bottom_anchorage_is_safe is True


def test_side_face_reinforcement_benchmark() -> None:
    result = check_property_line_strap_footing_strength(_design_input()).side_face

    assert result.required is True
    assert result.required_total_area_mm2 == pytest.approx(475.0)
    assert result.required_area_each_face_mm2 == pytest.approx(237.5)
    assert result.provided_area_each_face_mm2 == pytest.approx(452.38934211693)
    assert result.provided_total_area_mm2 == pytest.approx(904.77868423386)
    assert result.maximum_vertical_spacing_mm == pytest.approx(300.0)
    assert result.is_safe is True


def test_table_shear_and_vertical_stirrup_benchmark() -> None:
    result = check_property_line_strap_footing_strength(_design_input()).shear

    assert result.factored_shear_demand_kn == pytest.approx(261.65625)
    assert result.tension_reinforcement_percent == pytest.approx(0.692998379468337)
    assert result.nominal_shear_stress_nmm2 == pytest.approx(0.615661764705882)
    assert result.concrete_design_shear_strength_nmm2 == pytest.approx(
        0.569479416608601
    )
    assert result.maximum_design_shear_stress_nmm2 == pytest.approx(3.5)
    assert result.stirrup_carried_shear_required_kn == pytest.approx(19.6274979428445)
    assert result.stirrup_area_provided_mm2 == pytest.approx(157.07963267949)
    assert result.minimum_stirrup_area_at_provided_spacing_mm2 == pytest.approx(
        114.942528735632
    )
    assert result.stirrup_shear_capacity_provided_kn == pytest.approx(232.320776807564)
    assert result.maximum_stirrup_spacing_mm == pytest.approx(300.0)
    assert result.is_safe is True


@pytest.mark.parametrize(
    ("reinforcement", "field"),
    (
        (_reinforcement(top_bar_count=5), "top_area_is_safe"),
        (_reinforcement(bottom_bar_count=3), "bottom_area_is_safe"),
        (_reinforcement(nominal_cover_mm=49.0), "nominal_cover_is_safe"),
        (
            _reinforcement(available_top_anchorage_exterior_mm=1132.0),
            "top_anchorage_is_safe",
        ),
        (
            _reinforcement(available_bottom_anchorage_interior_mm=724.0),
            "bottom_anchorage_is_safe",
        ),
    ),
)
def test_valid_inadequate_flexure_or_detailing_returns_fail(
    reinforcement: StrapFootingReinforcementInput,
    field: str,
) -> None:
    result = check_property_line_strap_footing_strength(
        _design_input(reinforcement=reinforcement)
    )

    assert result.disposition is StrapFootingDesignDisposition.FAIL
    assert getattr(result.flexure, field) is False


@pytest.mark.parametrize(
    ("reinforcement", "field"),
    (
        (_reinforcement(side_face_bar_count_each_face=2), "area_is_safe"),
        (_reinforcement(side_face_vertical_spacing_mm=301.0), "spacing_is_safe"),
    ),
)
def test_valid_inadequate_side_face_provision_returns_fail(
    reinforcement: StrapFootingReinforcementInput,
    field: str,
) -> None:
    result = check_property_line_strap_footing_strength(
        _design_input(reinforcement=reinforcement)
    )

    assert result.disposition is StrapFootingDesignDisposition.FAIL
    assert getattr(result.side_face, field) is False


@pytest.mark.parametrize(
    ("reinforcement", "field"),
    (
        (_reinforcement(stirrup_diameter_mm=8.0), "minimum_stirrup_area_is_safe"),
        (_reinforcement(stirrup_spacing_mm=301.0), "stirrup_spacing_is_safe"),
    ),
)
def test_valid_inadequate_shear_provision_returns_fail(
    reinforcement: StrapFootingReinforcementInput,
    field: str,
) -> None:
    result = check_property_line_strap_footing_strength(
        _design_input(reinforcement=reinforcement)
    )

    assert result.disposition is StrapFootingDesignDisposition.FAIL
    assert getattr(result.shear, field) is False


def test_valid_service_bearing_failure_composes_to_fail() -> None:
    result = check_property_line_strap_footing_strength(
        _design_input(
            analysis=_input(
                actions=_actions(allowable_gross_bearing_pressure_kn_per_m2=210.0)
            )
        )
    )

    assert result.disposition is StrapFootingDesignDisposition.FAIL
    assert result.actions.gross_service_bearing_within_allowable is False


def test_valid_singly_reinforced_capacity_exceedance_returns_fail() -> None:
    actions = _actions(
        service_exterior_column_load_kn=2051.125,
        service_interior_column_load_kn=3482.875,
        factored_exterior_column_load_kn=3076.6875,
        factored_interior_column_load_kn=5224.3125,
        service_clear_strap_line_load_kn_per_m=24.0,
        factored_clear_strap_line_load_kn_per_m=36.0,
        allowable_gross_bearing_pressure_kn_per_m2=500.0,
    )
    result = check_property_line_strap_footing_strength(
        _design_input(analysis=_input(actions=actions))
    )

    assert result.disposition is StrapFootingDesignDisposition.FAIL
    assert result.flexure.singly_reinforced_capacity_is_sufficient is False
    assert result.flexure.exact_flexural_steel_required_mm2 is None


@pytest.mark.parametrize(
    ("factory", "message"),
    (
        (lambda: _material(strap_concrete_grade_nmm2=45.0), "strap_concrete"),
        (lambda: _material(steel_grade_nmm2=550.0), "steel_grade"),
        (lambda: _material(uncoated_deformed_bars=False), "uncoated_deformed_bars"),
        (lambda: _reinforcement(vertical_closed_stirrups=False), "vertical_closed"),
        (lambda: _reinforcement(bars_bundled=True), "bars_bundled"),
        (
            lambda: _reinforcement(reinforcement_schedule_approved=False),
            "reinforcement_schedule_approved",
        ),
        (lambda: _reinforcement(top_bar_count=True), "top_bar_count"),
        (lambda: _reinforcement(stirrup_diameter_mm=math.inf), "stirrup_diameter"),
    ),
)
def test_out_of_domain_material_and_layout_fail_closed(
    factory: object, message: str
) -> None:
    with pytest.raises(StrapFootingContractError, match=message):
        factory()  # type: ignore[operator]


def test_wrong_top_level_types_fail_closed() -> None:
    with pytest.raises(StrapFootingContractError, match="analysis"):
        StrapFootingDesignInput(  # type: ignore[arg-type]
            analysis=object(), material=_material(), reinforcement=_reinforcement()
        )
    with pytest.raises(StrapFootingContractError, match="footing_input"):
        check_property_line_strap_footing_strength(object())  # type: ignore[arg-type]


def test_result_is_frozen_deterministic_and_finite() -> None:
    first = check_property_line_strap_footing_strength(_design_input())
    second = check_property_line_strap_footing_strength(_design_input())

    assert first == second
    with pytest.raises(FrozenInstanceError):
        first.disposition = StrapFootingDesignDisposition.FAIL  # type: ignore[misc]
    assert all(
        math.isfinite(value)
        for value in (
            first.flexure.exact_flexural_steel_required_mm2,
            first.shear.nominal_shear_stress_nmm2,
            first.side_face.provided_total_area_mm2,
        )
        if value is not None
    )


def test_clause_and_source_traceability_are_exact() -> None:
    refs = get_clause_refs(check_property_line_strap_footing_strength)
    result = check_property_line_strap_footing_strength(_design_input())

    assert refs == [
        "26.2.1",
        "26.2.1.1",
        "26.3.2",
        "26.4",
        "26.5.1.1",
        "26.5.1.3",
        "26.5.1.5",
        "26.5.1.6",
        "38.1",
        "G-1.1",
        "40.1",
        "40.2",
        "40.4",
    ]
    assert result.source_refs[0].startswith("IS456-2000-A5:sha256:")
    assert result.source_refs[1].startswith("IS456-AMD6-2024:sha256:")
    assert "INDIA-2-STRAP-HAND-01" in result.source_refs
    assert any("Qualified engineering review" in item for item in result.limitations)


def test_cover_and_beam_minimum_metadata_are_semantically_correct() -> None:
    cover = get_clause_info("26.4")
    minimum = get_clause_info("26.5.1.1")

    assert cover is not None
    assert cover["title"] == "Nominal Cover to Reinforcement"
    assert minimum is not None
    assert minimum["title"] == "Minimum Tension Reinforcement in Beams"
    assert minimum["category"] == "detailing"
