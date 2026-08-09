# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Exact P10 tests for qualified external-coefficient two-way slab flexure."""

from __future__ import annotations

from dataclasses import replace

import pytest

from structural_lib.codes.is456.slab.external_coefficients import (
    record_external_two_way_slab_coefficients,
)
from structural_lib.codes.is456.slab.models import (
    SlabContractError,
    SolidRectangularSlabGeometry,
)
from structural_lib.codes.is456.slab.two_way import (
    SUPPORTED_INTERIOR_SOLID_RECTANGULAR_FOUR_EDGES_CONTINUOUS_SUPPORT_CASE_ID,
    TwoWaySlabCornerTorsionStatus,
    TwoWaySlabFlexureInput,
    TwoWaySlabFlexureStatus,
    design_supported_interior_two_way_slab_flexure,
)


def _input(**overrides: object) -> TwoWaySlabFlexureInput:
    record = record_external_two_way_slab_coefficients(
        geometry=SolidRectangularSlabGeometry(4000, 6000, 180, 1000),
        support_case_id=(
            SUPPORTED_INTERIOR_SOLID_RECTANGULAR_FOUR_EDGES_CONTINUOUS_SUPPORT_CASE_ID
        ),
        alpha_x=0.08,
        alpha_y=0.06,
        coefficient_source_reference="qualified-external-sheet:table-row-14",
        coefficient_source_is_approved=True,
    )
    values: dict[str, object] = {
        "coefficient_record": record,
        "qualified_coefficient_acceptance_reference": "engineer-review:2026-08-09:two-way-panel-1",
        "qualified_coefficient_acceptance_acknowledged": True,
        "is_interior_solid_rectangular_panel": True,
        "all_four_edges_continuous": True,
        "factored_area_load_kn_per_m2": 10,
        "d_x_mm": 150,
        "d_y_mm": 140,
        "fck_n_per_mm2": 20,
        "fy_n_per_mm2": 415,
    }
    values.update(overrides)
    return TwoWaySlabFlexureInput(**values)  # type: ignore[arg-type]


def test_independent_benchmark_moments_and_quadratic_stress_block_steel() -> None:
    """Hand moments: .08*10*4^2=12.8 and .06*10*4^2=9.6 kN m."""
    result = design_supported_interior_two_way_slab_flexure(_input())

    assert result.line_load_kn_per_m == pytest.approx(10.0, abs=1e-12)
    assert result.x_direction.factored_moment_knm == pytest.approx(12.8, abs=1e-12)
    assert result.y_direction.factored_moment_knm == pytest.approx(9.6, abs=1e-12)
    # Smaller roots of the exact P7 rectangular stress-block quadratics.
    assert result.x_direction.ast_required_mm2 == pytest.approx(244.7591, abs=1e-4)
    assert result.y_direction.ast_required_mm2 == pytest.approx(195.6828, abs=1e-4)
    assert result.x_direction.neutral_axis_depth_mm == pytest.approx(12.2737, abs=1e-4)
    assert result.y_direction.neutral_axis_depth_mm == pytest.approx(9.8127, abs=1e-4)


def test_result_retains_acceptance_provenance_explicit_torsion_state_and_p11_hold() -> (
    None
):
    result = design_supported_interior_two_way_slab_flexure(_input())

    assert result.coefficient_source_is_approved is True
    assert result.qualified_coefficient_acceptance_acknowledged is True
    assert result.qualified_coefficient_acceptance_reference.startswith(
        "engineer-review:"
    )
    assert result.corner_torsion_status is (
        TwoWaySlabCornerTorsionStatus.NOT_REQUIRED_FOR_SUPPORTED_INTERIOR_PANEL
    )
    assert result.status is TwoWaySlabFlexureStatus.FLEXURE_ONLY_PENDING_P11
    assert result.is_supported is True
    assert "P11 dependency" in result.p11_dependency
    assert any("does not look up" in exclusion for exclusion in result.exclusions)
    assert ("factored_moment", "kN m") in result.units


@pytest.mark.parametrize(
    ("field_name", "value", "message"),
    [
        ("qualified_coefficient_acceptance_reference", "", "non-blank"),
        ("qualified_coefficient_acceptance_acknowledged", False, "explicitly True"),
        ("qualified_coefficient_acceptance_acknowledged", 1, "explicitly True"),
        ("is_interior_solid_rectangular_panel", False, "explicitly True"),
        ("all_four_edges_continuous", False, "explicitly True"),
    ],
)
def test_unaccepted_or_unsupported_configuration_fails_closed(
    field_name: str, value: object, message: str
) -> None:
    with pytest.raises(SlabContractError, match=message):
        _input(**{field_name: value})


def test_mismatched_support_case_fails_closed() -> None:
    record = record_external_two_way_slab_coefficients(
        geometry=SolidRectangularSlabGeometry(4000, 6000, 180),
        support_case_id="another-supported-case",
        alpha_x=0.08,
        alpha_y=0.06,
        coefficient_source_reference="qualified-external-sheet:table-row-14",
        coefficient_source_is_approved=True,
    )
    with pytest.raises(
        SlabContractError, match="exact interior continuous support_case_id"
    ):
        _input(coefficient_record=record)


def test_one_way_record_is_rejected_before_p10_input_can_be_built() -> None:
    with pytest.raises(SlabContractError, match="classified as two_way"):
        record_external_two_way_slab_coefficients(
            geometry=SolidRectangularSlabGeometry(3000, 6001, 180),
            support_case_id=(
                SUPPORTED_INTERIOR_SOLID_RECTANGULAR_FOUR_EDGES_CONTINUOUS_SUPPORT_CASE_ID
            ),
            alpha_x=0.08,
            alpha_y=0.06,
            coefficient_source_reference="qualified-external-sheet:table-row-14",
            coefficient_source_is_approved=True,
        )


def test_over_capacity_demand_fails_closed() -> None:
    with pytest.raises(SlabContractError, match="singly reinforced"):
        design_supported_interior_two_way_slab_flexure(
            _input(factored_area_load_kn_per_m2=100)
        )


def test_explicit_strip_width_scales_the_per_strip_moments() -> None:
    base = _input()
    narrow_record = replace(
        base.coefficient_record,
        geometry=SolidRectangularSlabGeometry(4000, 6000, 180, 500),
    )
    result = design_supported_interior_two_way_slab_flexure(
        _input(coefficient_record=narrow_record)
    )
    assert result.line_load_kn_per_m == pytest.approx(5.0)
    assert result.x_direction.factored_moment_knm == pytest.approx(6.4)
