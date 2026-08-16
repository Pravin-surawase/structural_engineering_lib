"""INDIA-2-FLAT-C flexure, provided-bar, and serviceability tests."""

from __future__ import annotations

from dataclasses import replace

import pytest

from structural_lib.codes.is456.flat_slab import (
    FlatSlabAnalysisMethod,
    FlatSlabContractError,
    FlatSlabDetailingInput,
    FlatSlabDirectionDetailingInput,
    FlatSlabGravityLoad,
    FlatSlabGridGeometry,
    FlatSlabMaterial,
    FlatSlabPanelInput,
    FlatSlabPanelLocation,
    design_regular_interior_flat_slab_reinforcement,
)
from structural_lib.codes.is456.slab.detailing import ProvidedSlabBars
from structural_lib.codes.is456.slab.serviceability import SlabServiceabilityStatus
from structural_lib.codes.is456.traceability import get_clause_refs


def _panel(*, effective_depth_mm: float = 260.0) -> FlatSlabPanelInput:
    return FlatSlabPanelInput(
        geometry=FlatSlabGridGeometry(
            centre_to_centre_span_x_mm=6000.0,
            centre_to_centre_span_y_mm=6000.0,
            continuous_span_count_x=3,
            continuous_span_count_y=3,
            column_width_x_mm=500.0,
            column_width_y_mm=500.0,
            overall_depth_mm=300.0,
            conservative_effective_depth_mm=effective_depth_mm,
            analysis_method=FlatSlabAnalysisMethod.DIRECT_DESIGN,
            panel_location=FlatSlabPanelLocation.INTERIOR,
            all_spans_equal_x=True,
            all_spans_equal_y=True,
            columns_offset_from_grid=False,
            solid_slab=True,
            drop_present=False,
            column_head_present=False,
            marginal_beam_or_wall_present=False,
            openings_present=False,
            geometry_basis_reference="INDIA-2-FLAT-HAND-01-GEOMETRY",
        ),
        material=FlatSlabMaterial(
            concrete_grade_nmm2=30.0,
            steel_grade_nmm2=500.0,
            uncoated_deformed_bars=True,
            material_basis_reference="INDIA-2-FLAT-HAND-01-MATERIAL",
        ),
        gravity_load=FlatSlabGravityLoad(
            service_dead_load_kn_per_m2=9.0,
            service_live_load_kn_per_m2=4.0,
            factored_uniform_load_kn_per_m2=19.5,
            self_weight_included=True,
            identical_full_loading_on_represented_panels=True,
            patterned_loading_required=False,
            unbalanced_or_lateral_moment_transfer_present=False,
            load_combination_approved=True,
            load_basis_reference="INDIA-2-FLAT-HAND-01-LOAD",
        ),
    )


def _direction_bars() -> FlatSlabDirectionDetailingInput:
    return FlatSlabDirectionDetailingInput(
        column_strip_negative_bars=ProvidedSlabBars(12.0, 160.0),
        column_strip_positive_bars=ProvidedSlabBars(10.0, 200.0),
        middle_strip_negative_bars=ProvidedSlabBars(10.0, 200.0),
        middle_strip_positive_bars=ProvidedSlabBars(10.0, 200.0),
        support_top_extension_from_face_mm=1650.0,
    )


def _design_input(
    *,
    panel: FlatSlabPanelInput | None = None,
    x: FlatSlabDirectionDetailingInput | None = None,
    y: FlatSlabDirectionDetailingInput | None = None,
    **overrides: object,
) -> FlatSlabDetailingInput:
    values: dict[str, object] = {
        "panel": panel or _panel(),
        "x": x or _direction_bars(),
        "y": y or _direction_bars(),
        "straight_bars_only": True,
        "all_bottom_bars_continuous": True,
        "splices_present": False,
        "detailing_basis_reference": "INDIA-2-FLAT-HAND-01-DETAILING",
        "serviceability_acceptance_reference": ("INDIA-2-FLAT-G0-REVIEWED-SPAN-DEPTH"),
        "serviceability_acceptance_acknowledged": True,
    }
    values.update(overrides)
    return FlatSlabDetailingInput(**values)  # type: ignore[arg-type]


def test_frozen_flexural_steel_and_provided_bars_in_both_directions() -> None:
    result = design_regular_interior_flat_slab_reinforcement(_design_input())

    for direction in (result.x, result.y):
        expected = (
            (direction.column_strip_negative, 1993.0759957303314, 664.3586652434438),
            (direction.column_strip_positive, 836.6242926576455, 278.8747642192152),
            (direction.middle_strip_negative, 644.6542577836997, 214.88475259456656),
            (direction.middle_strip_positive, 554.2927518310106, 184.76425061033687),
        )
        for region, total_ast, ast_per_m in expected:
            assert region.ast_required_total_mm2 == pytest.approx(total_ast)
            assert region.ast_required_mm2_per_m == pytest.approx(ast_per_m)
            assert region.provided_check.minimum_required_mm2_per_m == pytest.approx(
                360.0
            )
            assert region.flat_slab_maximum_spacing_mm == pytest.approx(600.0)
            assert region.is_adequate is True
        assert direction.column_strip_negative.provided_check.provided_mm2_per_m == (
            pytest.approx(706.8583470577034)
        )
        for region in (
            direction.column_strip_positive,
            direction.middle_strip_negative,
            direction.middle_strip_positive,
        ):
            assert region.provided_check.governing_required_mm2_per_m == pytest.approx(
                360.0
            )
            assert region.provided_check.provided_mm2_per_m == pytest.approx(
                392.69908169872417
            )
        assert direction.required_support_top_extension_from_face_mm == pytest.approx(
            1650.0
        )
        assert direction.support_top_extension_passed is True
        assert direction.is_adequate is True
    assert result.is_reinforcement_and_detailing_adequate is True


def test_reviewed_no_drop_span_depth_benchmark_and_held_checks() -> None:
    result = design_regular_interior_flat_slab_reinforcement(_design_input())

    for serviceability in (result.x_serviceability, result.y_serviceability):
        assert serviceability.actual_span_depth_ratio == pytest.approx(6000.0 / 260.0)
        assert serviceability.reviewed_modified_span_depth_limit == pytest.approx(23.4)
        assert serviceability.utilization == pytest.approx(0.9861932938856016)
        assert serviceability.status is (
            SlabServiceabilityStatus.SATISFIED_WITH_REVIEWED_LIMIT
        )
        assert serviceability.verified_by_library is False
    assert result.is_span_depth_satisfied is True
    assert result.direct_deflection_status.startswith("held_requires")
    assert result.crack_width_status.startswith("held_requires")


def test_inadequate_provided_area_spacing_and_extension_return_false() -> None:
    bars = _direction_bars()
    inadequate = replace(
        bars,
        column_strip_negative_bars=ProvidedSlabBars(12.0, 200.0),
        column_strip_positive_bars=ProvidedSlabBars(10.0, 350.0),
        support_top_extension_from_face_mm=1649.0,
    )
    result = design_regular_interior_flat_slab_reinforcement(
        _design_input(x=inadequate)
    )

    assert result.x.column_strip_negative.provided_check.area_passed is False
    assert result.x.column_strip_positive.provided_check.spacing_passed is False
    assert result.x.column_strip_positive.flat_slab_spacing_passed is True
    assert result.x.support_top_extension_passed is False
    assert result.x.is_adequate is False
    assert result.is_reinforcement_and_detailing_adequate is False


def test_span_depth_exceedance_is_reported_without_claiming_direct_deflection() -> None:
    result = design_regular_interior_flat_slab_reinforcement(
        _design_input(panel=_panel(effective_depth_mm=200.0))
    )

    assert result.x_serviceability.actual_span_depth_ratio == pytest.approx(30.0)
    assert result.x_serviceability.status is SlabServiceabilityStatus.LIMIT_EXCEEDED
    assert result.is_span_depth_satisfied is False
    assert result.direct_deflection_status.startswith("held_requires")


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("straight_bars_only", False),
        ("all_bottom_bars_continuous", False),
        ("splices_present", True),
        ("serviceability_acceptance_acknowledged", False),
        ("detailing_basis_reference", " "),
        ("serviceability_acceptance_reference", " "),
    ),
)
def test_held_detailing_or_review_boundaries_fail_closed(
    field: str, value: object
) -> None:
    with pytest.raises(FlatSlabContractError, match=field):
        _design_input(**{field: value})


def test_clause_and_source_provenance_is_exact() -> None:
    refs = get_clause_refs(design_regular_interior_flat_slab_reinforcement)
    assert refs == [
        "23.2.1",
        "26.3.3",
        "26.5.2.1",
        "31.2.1",
        "31.7.1",
        "31.7.2",
        "31.7.3",
        "Figure 16",
        "38.1",
    ]
    result = design_regular_interior_flat_slab_reinforcement(_design_input())
    assert result.source_refs[0].startswith("IS 456:2000 Cl. 23.2.1")
    assert "IS456-2000-A6" in result.source_refs
    assert "INDIA-2-FLAT-HAND-01-DETAILING" in result.source_refs
    assert "INDIA-2-FLAT-G0-REVIEWED-SPAN-DEPTH" in result.source_refs


def test_non_detailing_input_fails_closed() -> None:
    with pytest.raises(FlatSlabContractError, match="FlatSlabDetailingInput"):
        design_regular_interior_flat_slab_reinforcement(object())  # type: ignore[arg-type]
