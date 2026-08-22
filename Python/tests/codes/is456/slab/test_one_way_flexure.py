# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Exact P7 tests for the solid simply supported one-way slab flexure slice."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from structural_lib.codes.is456.slab.models import (
    SlabCapacityFailureResult,
    SlabContractError,
    SolidRectangularSlabGeometry,
)
from structural_lib.codes.is456.slab.one_way import (
    OneWaySlabFlexureInput,
    OneWaySlabFlexureStatus,
    design_simply_supported_one_way_slab_flexure,
)
from structural_lib.codes.is456.traceability import get_clause_refs
from structural_lib.core.result_contract import (
    CalculationStatus,
    EngineeringStatus,
    IntakeStatus,
)


def _benchmark_input() -> OneWaySlabFlexureInput:
    return OneWaySlabFlexureInput(
        geometry=SolidRectangularSlabGeometry(
            span_a_effective_mm=3000,
            span_b_effective_mm=7500,
            thickness_mm=150,
            strip_width_mm=1000,
        ),
        d_mm=125,
        factored_area_load_kn_per_m2=10,
        fck_n_per_mm2=20,
        fy_n_per_mm2=415,
    )


def test_independent_benchmark_moment_and_quadratic_stress_block_ast() -> None:
    """Hand calculation: 10*1*3^2/8 = 11.25 kN m and Ast = 260.727 mm2."""
    result = design_simply_supported_one_way_slab_flexure(_benchmark_input())

    assert result.line_load_kn_per_m == pytest.approx(10.0, abs=1e-12)
    assert result.factored_moment_knm == pytest.approx(11.25, abs=1e-12)
    # Solving 0.87*415*Ast*(125 - 0.42*xu) = 11.25e6 N mm and
    # xu = 0.87*415*Ast/(0.36*20*1000) gives this smaller physical root.
    assert result.ast_required_mm2 == pytest.approx(260.7266304, abs=1e-7)
    assert result.neutral_axis_depth_mm == pytest.approx(13.0743542, abs=1e-7)
    assert result.limiting_moment_knm == pytest.approx(43.1136, abs=1e-10)


def test_missing_strip_width_means_one_metre_design_strip() -> None:
    design_input = OneWaySlabFlexureInput(
        geometry=SolidRectangularSlabGeometry(3000, 7500, 150),
        d_mm=125,
        factored_area_load_kn_per_m2=10,
        fck_n_per_mm2=20,
        fy_n_per_mm2=415,
    )

    result = design_simply_supported_one_way_slab_flexure(design_input)

    assert result.design_strip_width_mm == 1000.0
    assert result.line_load_kn_per_m == 10.0


def test_explicit_strip_width_scales_line_load_and_moment() -> None:
    design_input = OneWaySlabFlexureInput(
        geometry=SolidRectangularSlabGeometry(3000, 7500, 150, 500),
        d_mm=125,
        factored_area_load_kn_per_m2=10,
        fck_n_per_mm2=20,
        fy_n_per_mm2=415,
    )

    result = design_simply_supported_one_way_slab_flexure(design_input)

    assert result.line_load_kn_per_m == pytest.approx(5.0)
    assert result.factored_moment_knm == pytest.approx(5.625)


def test_result_records_checks_sources_and_p8_holds() -> None:
    result = design_simply_supported_one_way_slab_flexure(_benchmark_input())

    assert result.status is OneWaySlabFlexureStatus.FLEXURE_ONLY_PENDING_P8
    assert [check.check_id for check in result.governing_checks] == [
        "P7-ONE-WAY-01",
        "P7-DEPTH-01",
        "P7-MU-01",
    ]
    assert any("minimum reinforcement" in limit.lower() for limit in result.limitations)
    assert any("shear" in limit.lower() for limit in result.limitations)
    assert any("964e2705" in source for source in result.source_refs)
    assert any("4fc24999" in source for source in result.source_refs)
    assert get_clause_refs(design_simply_supported_one_way_slab_flexure) == [
        "24.1",
        "38.1",
    ]


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"d_mm": 150}, "less than"),
        ({"d_mm": 0}, "positive"),
        ({"factored_area_load_kn_per_m2": float("inf")}, "finite"),
        ({"fck_n_per_mm2": 15}, "20 to 80"),
        ({"fck_n_per_mm2": 90}, "20 to 80"),
        ({"fy_n_per_mm2": 400}, "supported grades"),
    ],
)
def test_invalid_depth_load_or_material_domain_fails_closed(
    kwargs: dict[str, float], message: str
) -> None:
    values: dict[str, object] = {
        "geometry": SolidRectangularSlabGeometry(3000, 7500, 150),
        "d_mm": 125,
        "factored_area_load_kn_per_m2": 10,
        "fck_n_per_mm2": 20,
        "fy_n_per_mm2": 415,
    }
    values.update(kwargs)

    with pytest.raises(SlabContractError, match=message):
        OneWaySlabFlexureInput(**values)  # type: ignore[arg-type]


def test_non_one_way_geometry_fails_closed() -> None:
    design_input = OneWaySlabFlexureInput(
        geometry=SolidRectangularSlabGeometry(3000, 6000, 150),
        d_mm=125,
        factored_area_load_kn_per_m2=10,
        fck_n_per_mm2=20,
        fy_n_per_mm2=415,
    )

    with pytest.raises(SlabContractError, match="Ly/Lx greater than 2.0"):
        design_simply_supported_one_way_slab_flexure(design_input)


def test_over_capacity_demand_fails_closed() -> None:
    design_input = OneWaySlabFlexureInput(
        geometry=SolidRectangularSlabGeometry(3000, 7500, 150),
        d_mm=125,
        factored_area_load_kn_per_m2=40,
        fck_n_per_mm2=20,
        fy_n_per_mm2=415,
    )

    result = design_simply_supported_one_way_slab_flexure(design_input)

    assert isinstance(result, SlabCapacityFailureResult)
    assert result.factored_moment_knm == pytest.approx(45.0)
    assert result.limiting_moment_knm == pytest.approx(43.113, abs=0.001)
    assert result.utilization_ratio > 1.0
    assert result.status is EngineeringStatus.FAIL
    assert result.result_envelope.intake_status is IntakeStatus.VALID
    assert result.result_envelope.calculation_status is CalculationStatus.COMPLETED
    assert result.result_envelope.engineering_status is EngineeringStatus.FAIL
    assert result.result_envelope.issues[0].code == ("SLAB_FLEXURE_CAPACITY_EXCEEDED")


def test_input_and_result_are_frozen() -> None:
    design_input = _benchmark_input()
    result = design_simply_supported_one_way_slab_flexure(design_input)

    with pytest.raises(FrozenInstanceError):
        design_input.d_mm = 100  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.ast_required_mm2 = 300  # type: ignore[misc]
