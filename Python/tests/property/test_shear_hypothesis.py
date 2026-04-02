# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Property-based tests for the shear module using Hypothesis.

These tests verify mathematical invariants that should ALWAYS hold:
1. Non-negativity: tv, tc, tc_max >= 0 for valid inputs
2. Bounds: tc <= tc_max always
3. Monotonicity: tc increases with pt (up to limit)
4. Consistency: Results make physical sense

Uses Hypothesis for automated edge case discovery.
"""

from hypothesis import assume, given

from structural_lib import shear, tables
from tests.property.strategies import (
    beam_section,
    beam_width,
    concrete_grade,
    effective_depth,
    shear_inputs,
    shear_kn,
    steel_grade,
    steel_percentage_table,
)


class TestTvProperties:
    """Property tests for calculate_tv (nominal shear stress)."""

    @given(vu=shear_kn(), b=beam_width(), d=effective_depth())
    def test_tv_always_non_negative(self, vu: float, b: float, d: float) -> None:
        """Nominal shear stress should always be non-negative."""
        tv = shear.calculate_tv(vu, b, d)
        assert tv >= 0, f"tv should be non-negative, got {tv}"

    @given(vu=shear_kn(), b=beam_width(), d=effective_depth())
    def test_tv_linear_in_vu(self, vu: float, b: float, d: float) -> None:
        """tv should double when Vu doubles (linear relationship)."""
        tv_1 = shear.calculate_tv(vu, b, d)
        tv_2 = shear.calculate_tv(2 * vu, b, d)
        assert (
            abs(tv_2 - 2 * tv_1) < 0.001 * tv_1
        ), f"tv should be linear in Vu: {tv_2} != 2 * {tv_1}"

    @given(vu=shear_kn(), b=beam_width(), d=effective_depth())
    def test_tv_inverse_with_area(self, vu: float, b: float, d: float) -> None:
        """tv should halve when area doubles."""
        assume(b <= 500)  # Ensure 2*b is in valid range
        tv_1 = shear.calculate_tv(vu, b, d)
        tv_2 = shear.calculate_tv(vu, 2 * b, d)
        assert (
            abs(tv_2 - 0.5 * tv_1) < 0.001 * tv_1
        ), f"tv should be inversely proportional to b: {tv_2} != 0.5 * {tv_1}"


class TestTcProperties:
    """Property tests for tc (concrete shear strength from Table 19)."""

    @given(fck=concrete_grade(), pt=steel_percentage_table())
    def test_tc_always_positive(self, fck: int, pt: float) -> None:
        """Concrete shear strength tc should always be positive."""
        tc = tables.get_tc_value(fck, pt)
        assert tc > 0, f"tc should be positive, got {tc}"

    @given(fck=concrete_grade())
    def test_tc_increases_with_pt(self, fck: int) -> None:
        """tc should increase with reinforcement percentage."""
        tc_low = tables.get_tc_value(fck, 0.25)
        tc_mid = tables.get_tc_value(fck, 1.0)
        tc_high = tables.get_tc_value(fck, 2.0)

        # tc should increase (or stay same at upper bound)
        assert (
            tc_low <= tc_mid <= tc_high
        ), f"tc should increase with pt: {tc_low} <= {tc_mid} <= {tc_high}"

    @given(pt=steel_percentage_table())
    def test_tc_increases_with_fck(self, pt: float) -> None:
        """tc should increase with concrete grade."""
        tc_20 = tables.get_tc_value(20, pt)
        tc_25 = tables.get_tc_value(25, pt)
        tc_30 = tables.get_tc_value(30, pt)

        # tc should increase with fck
        assert (
            tc_20 <= tc_25 <= tc_30
        ), f"tc should increase with fck: {tc_20} <= {tc_25} <= {tc_30}"


class TestTcMaxProperties:
    """Property tests for tc_max (maximum shear stress from Table 20)."""

    @given(fck=concrete_grade())
    def test_tc_max_always_positive(self, fck: int) -> None:
        """Maximum shear stress tc_max should always be positive."""
        tc_max = tables.get_tc_max_value(fck)
        assert tc_max > 0, f"tc_max should be positive, got {tc_max}"

    def test_tc_max_increases_with_fck(self) -> None:
        """tc_max should increase with concrete grade."""
        tc_max_20 = tables.get_tc_max_value(20)
        tc_max_25 = tables.get_tc_max_value(25)
        tc_max_30 = tables.get_tc_max_value(30)
        tc_max_40 = tables.get_tc_max_value(40)

        assert tc_max_20 < tc_max_25 < tc_max_30 < tc_max_40, (
            f"tc_max should increase with fck: "
            f"{tc_max_20} < {tc_max_25} < {tc_max_30} < {tc_max_40}"
        )

    @given(fck=concrete_grade(), pt=steel_percentage_table())
    def test_tc_never_exceeds_tc_max(self, fck: int, pt: float) -> None:
        """tc should never exceed tc_max for any pt value."""
        tc = tables.get_tc_value(fck, pt)
        tc_max = tables.get_tc_max_value(fck)

        assert tc <= tc_max, f"tc ({tc}) should not exceed tc_max ({tc_max})"


class TestShearDesign:
    """Property tests for design_shear function."""

    @given(inputs=shear_inputs())
    def test_design_returns_non_negative_values(self, inputs: dict) -> None:
        """All output values should be non-negative."""
        result = shear.design_shear(
            vu_kn=inputs["vu_kn"],
            b=inputs["b"],
            d=inputs["d"],
            fck=inputs["fck"],
            fy=inputs["fy"],
            asv=inputs["asv"],
            pt=inputs["pt"],
        )

        assert result.tv >= 0, f"tv should be non-negative, got {result.tv}"
        assert result.tc >= 0, f"tc should be non-negative, got {result.tc}"
        assert result.tc_max >= 0, f"tc_max should be non-negative, got {result.tc_max}"
        assert (
            result.spacing >= 0
        ), f"spacing should be non-negative, got {result.spacing}"

    @given(inputs=shear_inputs())
    def test_tc_within_tc_max(self, inputs: dict) -> None:
        """tc should always be <= tc_max in design results."""
        result = shear.design_shear(
            vu_kn=inputs["vu_kn"],
            b=inputs["b"],
            d=inputs["d"],
            fck=inputs["fck"],
            fy=inputs["fy"],
            asv=inputs["asv"],
            pt=inputs["pt"],
        )

        assert (
            result.tc <= result.tc_max
        ), f"tc ({result.tc}) should not exceed tc_max ({result.tc_max})"

    @given(inputs=shear_inputs())
    def test_tv_formula_consistency(self, inputs: dict) -> None:
        """tv from design_shear should match calculate_tv."""
        result = shear.design_shear(
            vu_kn=inputs["vu_kn"],
            b=inputs["b"],
            d=inputs["d"],
            fck=inputs["fck"],
            fy=inputs["fy"],
            asv=inputs["asv"],
            pt=inputs["pt"],
        )

        expected_tv = shear.calculate_tv(inputs["vu_kn"], inputs["b"], inputs["d"])
        assert (
            abs(result.tv - expected_tv) < 0.001
        ), f"tv should match calculate_tv: {result.tv} != {expected_tv}"

    @given(section=beam_section(), fck=concrete_grade(), fy=steel_grade())
    def test_low_shear_is_safe(self, section: dict, fck: int, fy: int) -> None:
        """Very low shear should always be safe."""
        b, d = section["b"], section["d"]
        # Use very low shear (10 kN) which should be < tc * b * d
        result = shear.design_shear(
            vu_kn=10.0,
            b=b,
            d=d,
            fck=float(fck),
            fy=float(fy),
            asv=100.0,  # 2-legged 8mm
            pt=1.0,
        )

        # For low shear, tv should be very small
        assert result.tv < 0.5, f"tv for 10kN should be small, got {result.tv}"
