"""INDIA-2-FLAT-D centred interior-column punching tests."""

from __future__ import annotations

from dataclasses import replace

import pytest

from structural_lib.codes.is456.flat_slab import (
    FlatSlabAnalysisMethod,
    FlatSlabContractError,
    FlatSlabGravityLoad,
    FlatSlabGridGeometry,
    FlatSlabMaterial,
    FlatSlabPanelInput,
    FlatSlabPanelLocation,
    FlatSlabPunchingInput,
    FlatSlabPunchingStatus,
    check_regular_interior_flat_slab_punching,
)
from structural_lib.codes.is456.traceability import get_clause_refs


def _panel(
    *,
    dead_load: float = 9.0,
    live_load: float = 4.0,
    factored_load: float = 19.5,
) -> FlatSlabPanelInput:
    return FlatSlabPanelInput(
        geometry=FlatSlabGridGeometry(
            centre_to_centre_span_x_mm=6000.0,
            centre_to_centre_span_y_mm=6000.0,
            continuous_span_count_x=3,
            continuous_span_count_y=3,
            column_width_x_mm=500.0,
            column_width_y_mm=500.0,
            overall_depth_mm=300.0,
            conservative_effective_depth_mm=260.0,
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
            service_dead_load_kn_per_m2=dead_load,
            service_live_load_kn_per_m2=live_load,
            factored_uniform_load_kn_per_m2=factored_load,
            self_weight_included=True,
            identical_full_loading_on_represented_panels=True,
            patterned_loading_required=False,
            unbalanced_or_lateral_moment_transfer_present=False,
            load_combination_approved=True,
            load_basis_reference="INDIA-2-FLAT-HAND-01-LOAD",
        ),
    )


def _input(
    panel: FlatSlabPanelInput | None = None,
    **overrides: object,
) -> FlatSlabPunchingInput:
    selected_panel = panel or _panel()
    expected_reaction = (
        selected_panel.gravity_load.factored_uniform_load_kn_per_m2 * 6.0 * 6.0
    )
    values: dict[str, object] = {
        "panel": selected_panel,
        "factored_support_reaction_kn": expected_reaction,
        "centred_concentric_reaction": True,
        "full_critical_perimeter_available": True,
        "no_punching_reinforcement_provided": True,
        "qualified_review_required": True,
        "support_reaction_basis_reference": "INDIA-2-FLAT-HAND-01-REACTION",
        "punching_basis_reference": "INDIA-2-FLAT-HAND-01-PUNCHING",
    }
    values.update(overrides)
    return FlatSlabPunchingInput(**values)  # type: ignore[arg-type]


def test_frozen_centred_interior_column_punching_benchmark() -> None:
    result = check_regular_interior_flat_slab_punching(_input())

    assert result.expected_uniform_tributary_reaction_kn == pytest.approx(702.0)
    assert result.critical_section_side_x_mm == pytest.approx(760.0)
    assert result.critical_section_side_y_mm == pytest.approx(760.0)
    assert result.critical_perimeter_mm == pytest.approx(3040.0)
    assert result.critical_enclosed_area_mm2 == pytest.approx(577600.0)
    assert result.factored_load_inside_critical_section_kn == pytest.approx(11.2632)
    assert result.punching_shear_force_kn == pytest.approx(690.7368)
    assert result.nominal_punching_stress_n_per_mm2 == pytest.approx(0.8739078947368422)
    assert result.column_aspect_ratio_beta_c == pytest.approx(1.0)
    assert result.size_factor_ks == pytest.approx(1.0)
    assert result.basic_concrete_shear_strength_n_per_mm2 == pytest.approx(
        1.3693063937629153
    )
    assert result.no_reinforcement_capacity_n_per_mm2 == pytest.approx(
        1.3693063937629153
    )
    assert result.mandatory_redesign_boundary_n_per_mm2 == pytest.approx(
        2.053959590644373
    )
    assert result.no_reinforcement_utilization == pytest.approx(0.6382120901359107)
    assert result.status is (FlatSlabPunchingStatus.SAFE_WITHOUT_PUNCHING_REINFORCEMENT)
    assert result.is_adequate_without_punching_reinforcement is True


def test_no_reinforcement_limit_exceedance_fails_bounded_route() -> None:
    panel = _panel(dead_load=16.0, live_load=5.0, factored_load=31.5)
    result = check_regular_interior_flat_slab_punching(_input(panel))

    assert result.nominal_punching_stress_n_per_mm2 > (
        result.no_reinforcement_capacity_n_per_mm2
    )
    assert result.nominal_punching_stress_n_per_mm2 < (
        result.mandatory_redesign_boundary_n_per_mm2
    )
    assert result.status is (
        FlatSlabPunchingStatus.PUNCHING_REINFORCEMENT_OR_REDESIGN_REQUIRED
    )
    assert result.is_adequate_without_punching_reinforcement is False


def test_mandatory_redesign_boundary_is_distinguished() -> None:
    panel = _panel(dead_load=30.0, live_load=15.0, factored_load=67.5)
    result = check_regular_interior_flat_slab_punching(_input(panel))

    assert result.nominal_punching_stress_n_per_mm2 > (
        result.mandatory_redesign_boundary_n_per_mm2
    )
    assert result.status is FlatSlabPunchingStatus.REDESIGN_REQUIRED
    assert result.is_adequate_without_punching_reinforcement is False


def test_support_reaction_must_match_frozen_tributary_basis() -> None:
    with pytest.raises(FlatSlabContractError, match="uniform tributary reaction"):
        check_regular_interior_flat_slab_punching(
            _input(factored_support_reaction_kn=701.0)
        )


@pytest.mark.parametrize(
    "field",
    (
        "centred_concentric_reaction",
        "full_critical_perimeter_available",
        "no_punching_reinforcement_provided",
        "qualified_review_required",
    ),
)
def test_held_punching_boundaries_fail_closed(field: str) -> None:
    with pytest.raises(FlatSlabContractError, match=field):
        _input(**{field: False})


@pytest.mark.parametrize(
    "field",
    ("support_reaction_basis_reference", "punching_basis_reference"),
)
def test_missing_punching_provenance_fails_closed(field: str) -> None:
    with pytest.raises(FlatSlabContractError, match=field):
        _input(**{field: " "})


def test_clause_source_and_held_case_provenance_is_exact() -> None:
    refs = get_clause_refs(check_regular_interior_flat_slab_punching)
    assert refs == ["31.6.1", "31.6.2.1", "31.6.3.1", "31.6.3.2"]
    result = check_regular_interior_flat_slab_punching(_input())
    assert result.source_refs[:3] == (
        "IS 456:2000 Cl. 31.6.1, 31.6.2.1, 31.6.3.1, 31.6.3.2",
        "IS456-2000-A6",
        "INDIA-2-FLAT-G0-CENTRED-INTERIOR-PUNCHING-BOUNDARY",
    )
    assert "INDIA-2-FLAT-HAND-01-REACTION" in result.source_refs
    assert "INDIA-2-FLAT-HAND-01-PUNCHING" in result.source_refs
    assert any("No unbalanced moment transfer" in item for item in result.limitations)
    assert any("neither selected nor designed" in item for item in result.limitations)


def test_non_punching_input_fails_closed() -> None:
    with pytest.raises(FlatSlabContractError, match="FlatSlabPunchingInput"):
        check_regular_interior_flat_slab_punching(object())  # type: ignore[arg-type]


def test_punching_contract_is_immutable() -> None:
    punching_input = _input()
    with pytest.raises(AttributeError):
        punching_input.factored_support_reaction_kn = 1.0  # type: ignore[misc]
    result = check_regular_interior_flat_slab_punching(punching_input)
    with pytest.raises(AttributeError):
        result.status = FlatSlabPunchingStatus.REDESIGN_REQUIRED  # type: ignore[misc]


def test_panel_contract_still_rejects_moment_transfer() -> None:
    panel = _panel()
    with pytest.raises(FlatSlabContractError, match="moment_transfer"):
        replace(
            panel,
            gravity_load=replace(
                panel.gravity_load,
                unbalanced_or_lateral_moment_transfer_present=True,
            ),
        )
