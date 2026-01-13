# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Property-based tests for the ductile detailing module using Hypothesis.

These tests verify IS 13920:2016 ductile detailing requirements:
1. Geometry checks: b >= 200mm, b/D >= 0.3
2. Steel limits: min_pt and max_pt in valid ranges
3. Confinement spacing: proper calculation based on d and bar diameter
4. Consistency: Valid geometry should pass all checks

Uses Hypothesis for automated edge case discovery.
"""

import math

from hypothesis import assume, given

from structural_lib.codes.is456 import ductile
from tests.property.strategies import (
    bar_diameter,
    beam_width_ductile,
    beam_width_narrow,
    concrete_grade,
    ductile_inputs,
    effective_depth,
    steel_grade,
    total_depth,
)


class TestGeometryCheck:
    """Property tests for check_geometry function."""

    @given(b=beam_width_ductile(), D=total_depth())
    def test_valid_geometry_passes(self, b: float, D: float) -> None:
        """Valid geometry (b >= 200, b/D >= 0.3) should pass."""
        # Only test when geometry is actually valid
        assume(b >= 200)
        assume(D > 0)
        assume(b / D >= 0.3)

        is_valid, msg, errors = ductile.check_geometry(b, D)
        assert is_valid, f"Valid geometry should pass: b={b}, D={D}, msg={msg}"
        assert len(errors) == 0, f"No errors for valid geometry, got {errors}"

    @given(b=beam_width_narrow(), D=total_depth())
    def test_narrow_beam_fails(self, b: float, D: float) -> None:
        """Beam with b < 200mm should fail (IS 13920 Cl 6.1.1)."""
        # beam_width_narrow generates 100-199.9mm (always < 200)

        is_valid, msg, errors = ductile.check_geometry(b, D)
        assert not is_valid, f"b < 200 should fail: b={b}"
        assert "200" in msg, "Message should mention 200mm limit"

    @given(b=beam_width_ductile())
    def test_wrong_aspect_ratio_fails(self, b: float) -> None:
        """Beam with b/D < 0.3 should fail (IS 13920 Cl 6.1.2)."""
        # Create D that violates b/D >= 0.3 (i.e., D > b/0.3)
        D = b / 0.2  # This ensures b/D = 0.2 < 0.3

        is_valid, msg, errors = ductile.check_geometry(b, D)
        assert not is_valid, f"b/D < 0.3 should fail: b={b}, D={D}, ratio={b/D:.2f}"
        assert "0.3" in msg or "ratio" in msg.lower(), "Message should mention ratio"


class TestMinSteelPercentage:
    """Property tests for get_min_tension_steel_percentage."""

    @given(fck=concrete_grade(), fy=steel_grade())
    def test_min_pt_always_positive(self, fck: int, fy: int) -> None:
        """Minimum steel percentage should always be positive."""
        min_pt = ductile.get_min_tension_steel_percentage(float(fck), float(fy))
        assert min_pt > 0, f"min_pt should be positive, got {min_pt}"

    @given(fck=concrete_grade(), fy=steel_grade())
    def test_min_pt_in_reasonable_range(self, fck: int, fy: int) -> None:
        """Minimum steel percentage should be in engineering range (0.1-1%)."""
        min_pt = ductile.get_min_tension_steel_percentage(float(fck), float(fy))
        # Formula: 0.24 * sqrt(fck) / fy * 100
        # For fck=15, fy=550: 0.24 * 3.87 / 550 * 100 = 0.17%
        # For fck=80, fy=250: 0.24 * 8.94 / 250 * 100 = 0.86%
        assert 0.1 < min_pt < 1.0, f"min_pt should be in (0.1, 1.0)%, got {min_pt}"

    @given(fy=steel_grade())
    def test_min_pt_increases_with_fck(self, fy: int) -> None:
        """min_pt should increase with concrete grade (sqrt(fck) factor)."""
        min_pt_20 = ductile.get_min_tension_steel_percentage(20.0, float(fy))
        min_pt_40 = ductile.get_min_tension_steel_percentage(40.0, float(fy))
        min_pt_60 = ductile.get_min_tension_steel_percentage(60.0, float(fy))

        assert (
            min_pt_20 < min_pt_40 < min_pt_60
        ), f"min_pt should increase with fck: {min_pt_20} < {min_pt_40} < {min_pt_60}"

    @given(fck=concrete_grade())
    def test_min_pt_decreases_with_fy(self, fck: int) -> None:
        """min_pt should decrease with steel grade (1/fy factor)."""
        min_pt_250 = ductile.get_min_tension_steel_percentage(float(fck), 250.0)
        min_pt_415 = ductile.get_min_tension_steel_percentage(float(fck), 415.0)
        min_pt_500 = ductile.get_min_tension_steel_percentage(float(fck), 500.0)

        assert (
            min_pt_250 > min_pt_415 > min_pt_500
        ), f"min_pt should decrease with fy: {min_pt_250} > {min_pt_415} > {min_pt_500}"

    @given(fck=concrete_grade(), fy=steel_grade())
    def test_min_pt_formula_correct(self, fck: int, fy: int) -> None:
        """Verify the formula: rho_min = 0.24 * sqrt(fck) / fy * 100."""
        min_pt = ductile.get_min_tension_steel_percentage(float(fck), float(fy))
        expected = 0.24 * math.sqrt(float(fck)) / float(fy) * 100
        assert (
            abs(min_pt - expected) < 0.0001
        ), f"Formula mismatch: {min_pt} != {expected}"


class TestMaxSteelPercentage:
    """Property tests for get_max_tension_steel_percentage."""

    def test_max_pt_is_2_5_percent(self) -> None:
        """Maximum steel percentage is fixed at 2.5% per IS 13920 Cl 6.2.2."""
        max_pt = ductile.get_max_tension_steel_percentage()
        assert max_pt == 2.5, f"max_pt should be 2.5%, got {max_pt}"


class TestConfinementSpacing:
    """Property tests for calculate_confinement_spacing."""

    @given(d=effective_depth(), dia=bar_diameter())
    def test_spacing_always_positive(self, d: float, dia: int) -> None:
        """Confinement spacing should always be positive."""
        spacing = ductile.calculate_confinement_spacing(d, float(dia))
        assert spacing > 0, f"Spacing should be positive, got {spacing}"

    @given(d=effective_depth(), dia=bar_diameter())
    def test_spacing_never_exceeds_100mm(self, d: float, dia: int) -> None:
        """Confinement spacing should never exceed 100mm (IS 13920 Cl 6.3.5)."""
        spacing = ductile.calculate_confinement_spacing(d, float(dia))
        assert spacing <= 100, f"Spacing should be <= 100mm, got {spacing}"

    @given(d=effective_depth(), dia=bar_diameter())
    def test_spacing_never_exceeds_d_over_4(self, d: float, dia: int) -> None:
        """Confinement spacing should never exceed d/4 (IS 13920 Cl 6.3.5)."""
        spacing = ductile.calculate_confinement_spacing(d, float(dia))
        assert spacing <= d / 4 + 0.01, f"Spacing {spacing} should be <= d/4 = {d/4}"

    @given(d=effective_depth(), dia=bar_diameter())
    def test_spacing_never_exceeds_8_times_dia(self, d: float, dia: int) -> None:
        """Confinement spacing should never exceed 8 * bar diameter."""
        spacing = ductile.calculate_confinement_spacing(d, float(dia))
        assert (
            spacing <= 8 * dia + 0.01
        ), f"Spacing {spacing} should be <= 8*{dia} = {8*dia}"

    @given(d=effective_depth(), dia=bar_diameter())
    def test_spacing_is_minimum_of_three_criteria(self, d: float, dia: int) -> None:
        """Spacing should be exactly min(d/4, 8*dia, 100)."""
        spacing = ductile.calculate_confinement_spacing(d, float(dia))
        expected = min(d / 4, 8 * float(dia), 100.0)
        assert (
            abs(spacing - expected) < 0.01
        ), f"Spacing {spacing} != min({d/4}, {8*dia}, 100) = {expected}"


class TestBeamDuctility:
    """Property tests for check_beam_ductility function."""

    @given(inputs=ductile_inputs())
    def test_valid_inputs_return_valid_geometry(self, inputs: dict) -> None:
        """Valid ductile beam inputs should pass geometry check."""
        result = ductile.check_beam_ductility(
            b=inputs["b"],
            D=inputs["D"],
            d=inputs["d"],
            fck=inputs["fck"],
            fy=inputs["fy"],
            min_long_bar_dia=inputs["min_bar_dia"],
        )

        assert result.is_geometry_valid, (
            f"Valid ductile beam should pass: b={inputs['b']}, D={inputs['D']}, "
            f"ratio={inputs['b']/inputs['D']:.2f}, errors={result.errors}"
        )

    @given(inputs=ductile_inputs())
    def test_min_pt_less_than_max_pt(self, inputs: dict) -> None:
        """min_pt should always be less than max_pt."""
        result = ductile.check_beam_ductility(
            b=inputs["b"],
            D=inputs["D"],
            d=inputs["d"],
            fck=inputs["fck"],
            fy=inputs["fy"],
            min_long_bar_dia=inputs["min_bar_dia"],
        )

        if result.is_geometry_valid:
            assert (
                result.min_pt < result.max_pt
            ), f"min_pt ({result.min_pt}) should be < max_pt ({result.max_pt})"

    @given(inputs=ductile_inputs())
    def test_confinement_spacing_valid(self, inputs: dict) -> None:
        """Confinement spacing should be in valid range."""
        result = ductile.check_beam_ductility(
            b=inputs["b"],
            D=inputs["D"],
            d=inputs["d"],
            fck=inputs["fck"],
            fy=inputs["fy"],
            min_long_bar_dia=inputs["min_bar_dia"],
        )

        if result.is_geometry_valid:
            assert (
                0 < result.confinement_spacing <= 100
            ), f"Confinement spacing should be in (0, 100]mm, got {result.confinement_spacing}"
