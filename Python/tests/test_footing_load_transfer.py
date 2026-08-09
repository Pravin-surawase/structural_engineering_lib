# SPDX-License-Identifier: MIT
"""Focused independent arithmetic checks for IS 456 Cl. 34.4 load transfer."""

from __future__ import annotations

import math

import pytest

from structural_lib.codes.is456.footing.load_transfer import (
    AMENDMENT_6_SOURCE_ID,
    IS456_CONSOLIDATED_SOURCE_ID,
    check_isolated_footing_load_transfer,
)
from structural_lib.core.errors import ValidationError


def _benchmark_kwargs(**overrides: object) -> dict[str, object]:
    """Project-authored benchmark; arithmetic is asserted below independently."""
    values: dict[str, object] = {
        "Pu_kN": 3_000.0,
        "loaded_area_A2_mm2": 400.0 * 400.0,
        "effective_supporting_area_A1_mm2": 640_000.0,
        "effective_supporting_area_basis": "largest_frustum_1v_2h",
        "effective_supporting_area_is_approved": True,
        "supporting_concrete_fck_nmm2": 20.0,
        "supported_concrete_fck_nmm2": 25.0,
        "steel_fy_nmm2": 415.0,
        "dowel_count": 8,
        "dowel_diameter_mm": 25.0,
        "column_longitudinal_bar_diameter_mm": 32.0,
        "available_dowel_development_length_into_footing_mm": 1_176.0,
        "available_dowel_development_length_into_supported_member_mm": 1_010.0,
    }
    values.update(overrides)
    return values


def test_project_benchmark_governing_capacity_transfer_steel_and_development_length():
    """3000 kN, 400x400, approved A1=640000, M20/M25, 8-25 dowels."""
    result = check_isolated_footing_load_transfer(**_benchmark_kwargs())

    # Independent arithmetic: 0.45*25*160000 = 1800 kN; footing is 2880 kN.
    assert result.actual_bearing_stress_nmm2 == pytest.approx(18.75)
    assert result.bearing_enhancement_factor == pytest.approx(2.0)
    assert result.supported_concrete_bearing_capacity_kN == pytest.approx(1_800.0)
    assert result.supporting_concrete_bearing_capacity_kN == pytest.approx(2_880.0)
    assert result.governing_concrete_member == "supported_column_or_pedestal"
    assert result.governing_concrete_bearing_capacity_kN == pytest.approx(1_800.0)
    assert result.excess_force_kN == pytest.approx(1_200.0)

    # 1200000/(0.87*415) = 3323.64 mm2; 8*pi*25^2/4 = 3926.99 mm2.
    assert result.excess_transfer_steel_area_mm2 == pytest.approx(
        1_200_000 / (0.87 * 415)
    )
    assert result.minimum_transfer_steel_area_mm2 == pytest.approx(800.0)
    assert result.required_transfer_steel_area_mm2 == pytest.approx(
        1_200_000 / (0.87 * 415)
    )
    assert result.provided_transfer_steel_area_mm2 == pytest.approx(
        8 * math.pi * 25**2 / 4
    )

    # M20 deformed tau_bd=1.92: Ld=25*(0.87*415)/(4*1.92)=1175.293 mm.
    assert result.supporting_concrete_design_bond_stress_nmm2 == pytest.approx(1.92)
    assert result.supported_concrete_design_bond_stress_nmm2 == pytest.approx(2.24)
    assert result.required_dowel_development_length_into_footing_mm == pytest.approx(
        1_175.293
    )
    assert (
        result.required_dowel_development_length_into_supported_member_mm
        == pytest.approx(25 * (0.87 * 415) / (4 * 2.24))
    )
    assert result.development_lengths_are_safe is True
    assert result.is_safe is True
    assert result.source_ids == (IS456_CONSOLIDATED_SOURCE_ID, AMENDMENT_6_SOURCE_ID)
    assert (
        result.source_notes[1]
        == "Supplied Amendment 6 has no footing load-transfer change."
    )
    assert result.units["stress"] == "N/mm2"
    assert result.limits["maximum_bearing_enhancement_factor"] == 2.0


def test_effective_a1_requires_explicit_approved_frustum_basis():
    with pytest.raises(
        ValidationError, match="full footing plan area cannot be assumed"
    ):
        check_isolated_footing_load_transfer(
            **_benchmark_kwargs(effective_supporting_area_is_approved=False)
        )
    with pytest.raises(ValidationError, match="1V:2H"):
        check_isolated_footing_load_transfer(
            **_benchmark_kwargs(effective_supporting_area_basis="footing_plan")
        )


def test_enhancement_is_capped_and_underprovided_dowels_fail_transfer_check():
    result = check_isolated_footing_load_transfer(
        **_benchmark_kwargs(
            effective_supporting_area_A1_mm2=1_600_000.0,
            dowel_count=4,
            dowel_diameter_mm=20.0,
            available_dowel_development_length_into_footing_mm=2_000.0,
        )
    )
    assert result.bearing_enhancement_factor == pytest.approx(2.0)
    assert result.reinforcement_area_is_safe is False
    assert result.bar_count_is_safe is True
    assert result.is_safe is False


def test_dowel_diameter_and_development_length_boundaries_are_reported():
    too_large = check_isolated_footing_load_transfer(
        **_benchmark_kwargs(
            dowel_diameter_mm=36.0,
            available_dowel_development_length_into_footing_mm=2_000.0,
        )
    )
    assert too_large.maximum_dowel_diameter_mm == pytest.approx(35.0)
    assert too_large.dowel_diameter_is_safe is False
    assert too_large.is_safe is False

    short_embedment = check_isolated_footing_load_transfer(
        **_benchmark_kwargs(available_dowel_development_length_into_footing_mm=1_175.28)
    )
    assert short_embedment.footing_development_length_is_safe is False
    assert short_embedment.development_lengths_are_safe is False
    assert short_embedment.is_safe is False

    short_supported_embedment = check_isolated_footing_load_transfer(
        **_benchmark_kwargs(
            available_dowel_development_length_into_supported_member_mm=1_007.0
        )
    )
    assert (
        short_supported_embedment.supported_member_development_length_is_safe is False
    )
    assert short_supported_embedment.development_lengths_are_safe is False
    assert short_supported_embedment.is_safe is False


def test_special_large_column_bar_dowel_case_fails_closed():
    with pytest.raises(ValidationError, match="over 36 mm"):
        check_isolated_footing_load_transfer(
            **_benchmark_kwargs(column_longitudinal_bar_diameter_mm=40.0)
        )
