# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Property-based tests for the flexure module using Hypothesis.

These tests verify mathematical invariants that should ALWAYS hold:
1. Non-negativity: Mu_lim, Ast >= 0 for valid inputs
2. Monotonicity: More depth → more capacity; more moment → more steel
3. Bounds: xu <= xu_max for under-reinforced sections
4. Consistency: Results make physical sense

Uses Hypothesis for automated edge case discovery.
"""

from hypothesis import assume, given

from structural_lib import flexure, materials
from tests.property.strategies import (
    beam_section,
    beam_width,
    concrete_grade,
    effective_depth,
    flexure_inputs,
    steel_grade,
)


class TestMuLimProperties:
    """Property tests for calculate_mu_lim function."""

    @given(b=beam_width(), d=effective_depth(), fck=concrete_grade(), fy=steel_grade())
    def test_mu_lim_always_positive(
        self, b: float, d: float, fck: int, fy: int
    ) -> None:
        """Mu_lim should always be positive for valid inputs."""
        mu_lim = flexure.calculate_mu_lim(b, d, float(fck), float(fy))
        assert mu_lim > 0, f"Mu_lim should be positive, got {mu_lim}"

    @given(b=beam_width(), d=effective_depth(), fck=concrete_grade(), fy=steel_grade())
    def test_mu_lim_proportional_to_b(
        self, b: float, d: float, fck: int, fy: int
    ) -> None:
        """Mu_lim should double when width doubles (linear in b)."""
        mu_lim_1 = flexure.calculate_mu_lim(b, d, float(fck), float(fy))
        mu_lim_2 = flexure.calculate_mu_lim(2 * b, d, float(fck), float(fy))
        # Allow 0.1% tolerance for floating point
        assert (
            abs(mu_lim_2 - 2 * mu_lim_1) < 0.001 * mu_lim_1
        ), f"Mu_lim should be linear in b: {mu_lim_2} != 2 * {mu_lim_1}"

    @given(b=beam_width(), d=effective_depth(), fck=concrete_grade(), fy=steel_grade())
    def test_mu_lim_quadratic_in_d(self, b: float, d: float, fck: int, fy: int) -> None:
        """Mu_lim should quadruple when depth doubles (quadratic in d)."""
        # Ensure doubled depth is still in valid range
        assume(d <= 850)  # So 2*d <= 1700
        mu_lim_1 = flexure.calculate_mu_lim(b, d, float(fck), float(fy))
        mu_lim_2 = flexure.calculate_mu_lim(b, 2 * d, float(fck), float(fy))
        # Allow 0.1% tolerance for floating point
        assert (
            abs(mu_lim_2 - 4 * mu_lim_1) < 0.001 * mu_lim_1
        ), f"Mu_lim should be quadratic in d: {mu_lim_2} != 4 * {mu_lim_1}"

    @given(b=beam_width(), d=effective_depth(), fck=concrete_grade(), fy=steel_grade())
    def test_mu_lim_proportional_to_fck(
        self, b: float, d: float, fck: int, fy: int
    ) -> None:
        """Mu_lim should double when fck doubles (linear in fck)."""
        # Use continuous fck values for this test
        fck_val = float(fck)
        assume(fck_val <= 40)  # So 2*fck <= 80 (valid range)
        mu_lim_1 = flexure.calculate_mu_lim(b, d, fck_val, float(fy))
        mu_lim_2 = flexure.calculate_mu_lim(b, d, 2 * fck_val, float(fy))
        # Allow 0.1% tolerance
        assert (
            abs(mu_lim_2 - 2 * mu_lim_1) < 0.001 * mu_lim_1
        ), f"Mu_lim should be linear in fck: {mu_lim_2} != 2 * {mu_lim_1}"

    @given(b=beam_width(), d=effective_depth(), fck=concrete_grade())
    def test_mu_lim_decreases_with_fy(self, b: float, d: float, fck: int) -> None:
        """Mu_lim should decrease as fy increases (xu_max/d decreases)."""
        mu_lim_415 = flexure.calculate_mu_lim(b, d, float(fck), 415.0)
        mu_lim_500 = flexure.calculate_mu_lim(b, d, float(fck), 500.0)
        assert (
            mu_lim_500 < mu_lim_415
        ), f"Mu_lim should decrease with fy: {mu_lim_500} >= {mu_lim_415}"


class TestAstRequiredProperties:
    """Property tests for calculate_ast_required function."""

    @given(inputs=flexure_inputs())
    def test_ast_always_non_negative(self, inputs: dict) -> None:
        """Required steel area should always be non-negative."""
        b, d, fck, fy = inputs["b"], inputs["d"], inputs["fck"], inputs["fy"]
        mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)
        mu = inputs["mu_ratio"] * mu_lim

        ast = flexure.calculate_ast_required(b, d, mu, fck, fy)
        assert ast >= 0, f"Ast should be non-negative, got {ast}"

    @given(section=beam_section(), fck=concrete_grade(), fy=steel_grade())
    def test_ast_monotonic_with_moment(self, section: dict, fck: int, fy: int) -> None:
        """More moment should require more steel (monotonic)."""
        b, d = section["b"], section["d"]
        mu_lim = flexure.calculate_mu_lim(b, d, float(fck), float(fy))

        # Test at 30%, 50%, 70% of Mu_lim
        mu_low = 0.3 * mu_lim
        mu_mid = 0.5 * mu_lim
        mu_high = 0.7 * mu_lim

        ast_low = flexure.calculate_ast_required(b, d, mu_low, float(fck), float(fy))
        ast_mid = flexure.calculate_ast_required(b, d, mu_mid, float(fck), float(fy))
        ast_high = flexure.calculate_ast_required(b, d, mu_high, float(fck), float(fy))

        assert (
            ast_low < ast_mid < ast_high
        ), f"Ast should be monotonic: {ast_low} < {ast_mid} < {ast_high}"


class TestSinglyReinforcedDesign:
    """Property tests for design_singly_reinforced function."""

    @given(inputs=flexure_inputs())
    def test_design_returns_valid_result(self, inputs: dict) -> None:
        """Design should return a structurally valid result."""
        b, d, D = inputs["b"], inputs["d"], inputs["D"]
        fck, fy = inputs["fck"], inputs["fy"]
        mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)
        mu = inputs["mu_ratio"] * mu_lim

        result = flexure.design_singly_reinforced(b, d, D, mu, fck, fy)
        # Result should always have positive Ast
        assert (
            result.ast_required > 0
        ), f"Ast should be positive, got {result.ast_required}"
        # If design is safe, it means no ERROR severity issues
        # Note: Some edge cases (high fck + low fy) can hit max steel even for Mu < Mu_lim

    @given(inputs=flexure_inputs())
    def test_xu_within_limit_for_under_reinforced(self, inputs: dict) -> None:
        """Neutral axis depth xu should be <= xu_max for under-reinforced."""
        b, d, D = inputs["b"], inputs["d"], inputs["D"]
        fck, fy = inputs["fck"], inputs["fy"]
        mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)
        mu = inputs["mu_ratio"] * mu_lim

        result = flexure.design_singly_reinforced(b, d, D, mu, fck, fy)
        assert (
            result.xu <= result.xu_max + 0.01
        ), f"xu ({result.xu}) should be <= xu_max ({result.xu_max})"

    @given(inputs=flexure_inputs())
    def test_ast_required_positive(self, inputs: dict) -> None:
        """Design should always require some steel (>= minimum)."""
        b, d, D = inputs["b"], inputs["d"], inputs["D"]
        fck, fy = inputs["fck"], inputs["fy"]
        mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)
        mu = inputs["mu_ratio"] * mu_lim

        result = flexure.design_singly_reinforced(b, d, D, mu, fck, fy)
        assert (
            result.ast_required > 0
        ), f"Ast should be positive, got {result.ast_required}"

    @given(inputs=flexure_inputs())
    def test_pt_provided_is_positive(self, inputs: dict) -> None:
        """Steel percentage should always be positive."""
        b, d, D = inputs["b"], inputs["d"], inputs["D"]
        fck, fy = inputs["fck"], inputs["fy"]
        mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)
        mu = inputs["mu_ratio"] * mu_lim

        result = flexure.design_singly_reinforced(b, d, D, mu, fck, fy)
        # pt should always be positive for any design
        assert (
            result.pt_provided > 0
        ), f"pt should be positive, got {result.pt_provided}%"


class TestXuMaxDProperties:
    """Property tests for xu_max/d ratio from materials module."""

    @given(fy=steel_grade())
    def test_xu_max_d_in_valid_range(self, fy: int) -> None:
        """xu_max/d ratio should be between 0 and 1."""
        xu_max_d = materials.get_xu_max_d(float(fy))
        assert 0 < xu_max_d < 1, f"xu_max/d should be in (0, 1), got {xu_max_d}"

    def test_xu_max_d_decreases_with_fy(self) -> None:
        """xu_max/d should decrease as fy increases (ductility)."""
        xu_max_250 = materials.get_xu_max_d(250.0)
        xu_max_415 = materials.get_xu_max_d(415.0)
        xu_max_500 = materials.get_xu_max_d(500.0)
        xu_max_550 = materials.get_xu_max_d(550.0)

        assert xu_max_250 > xu_max_415 > xu_max_500 > xu_max_550, (
            f"xu_max/d should decrease with fy: "
            f"{xu_max_250} > {xu_max_415} > {xu_max_500} > {xu_max_550}"
        )
