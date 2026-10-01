# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Property-based tests for the serviceability module using Hypothesis.

Tests verify mathematical invariants for IS 456 serviceability checks:
1. Deflection span/depth: monotonicity with depth, result consistency
2. Crack width: non-negativity, monotonicity with strain
3. Effective moment of inertia: bounded between Icr and Igross
4. Gross moment of inertia: exact formula, always positive
5. Level B deflection: total >= short-term, monotonicity with moment
"""

from hypothesis import assume, given, settings
from hypothesis import strategies as st
from structural_lib import serviceability

from tests.property.strategies import (
    beam_section,
    beam_width,
    concrete_grade,
    total_depth,
)


class TestDeflectionSpanDepthProperties:
    """Property tests for check_deflection_span_depth."""

    @settings(max_examples=50)
    @given(
        span=st.floats(
            min_value=2000.0, max_value=12000.0, allow_nan=False, allow_infinity=False
        ),
        d=st.floats(
            min_value=200.0, max_value=1500.0, allow_nan=False, allow_infinity=False
        ),
    )
    def test_larger_depth_more_likely_to_pass(self, span: float, d: float) -> None:
        """Monotonicity: larger effective depth → L/d ratio decreases → more likely to pass."""
        assume(d <= 750)  # So 2*d <= 1500
        r1 = serviceability.check_deflection_span_depth(span_mm=span, d_mm=d)
        r2 = serviceability.check_deflection_span_depth(span_mm=span, d_mm=2 * d)
        # If it passes with smaller d, it must pass with larger d
        if r1.is_ok:
            assert r2.is_ok, (
                f"Passed with d={d} but failed with d={2 * d}; "
                f"L/d1={r1.computed['ld_ratio']:.3f}, L/d2={r2.computed['ld_ratio']:.3f}"
            )

    @settings(max_examples=50)
    @given(
        span=st.floats(
            min_value=1000.0, max_value=12000.0, allow_nan=False, allow_infinity=False
        ),
        d=st.floats(
            min_value=200.0, max_value=1700.0, allow_nan=False, allow_infinity=False
        ),
    )
    def test_result_consistency(self, span: float, d: float) -> None:
        """Consistency: is_ok == (actual_Ld <= allowable_Ld)."""
        result = serviceability.check_deflection_span_depth(span_mm=span, d_mm=d)
        expected_ok = result.computed["ld_ratio"] <= result.computed["allowable_ld"]
        assert result.is_ok == expected_ok, (
            f"is_ok={result.is_ok} but ld_ratio={result.computed['ld_ratio']:.3f} "
            f"vs allowable={result.computed['allowable_ld']:.3f}"
        )


class TestCrackWidthProperties:
    """Property tests for check_crack_width."""

    @settings(max_examples=50)
    @given(
        acr=st.floats(
            min_value=30.0, max_value=200.0, allow_nan=False, allow_infinity=False
        ),
        cmin=st.floats(
            min_value=25.0, max_value=75.0, allow_nan=False, allow_infinity=False
        ),
        h=st.floats(
            min_value=300.0, max_value=1800.0, allow_nan=False, allow_infinity=False
        ),
        x=st.floats(
            min_value=50.0, max_value=600.0, allow_nan=False, allow_infinity=False
        ),
        epsilon_m=st.floats(
            min_value=1e-5, max_value=2e-3, allow_nan=False, allow_infinity=False
        ),
    )
    def test_wcr_non_negative(
        self, acr: float, cmin: float, h: float, x: float, epsilon_m: float
    ) -> None:
        """Crack width wcr always >= 0 for valid inputs."""
        assume(h > x)
        assume(acr > cmin)
        # Ensure positive denominator: 1 + 2*(acr-cmin)/(h-x) > 0
        denom = 1.0 + 2.0 * (acr - cmin) / (h - x)
        assume(denom > 0)

        result = serviceability.check_crack_width(
            acr_mm=acr,
            cmin_mm=cmin,
            h_mm=h,
            x_mm=x,
            epsilon_m=epsilon_m,
        )
        assert (
            result.computed["wcr_mm"] >= 0
        ), f"wcr should be non-negative, got {result.computed['wcr_mm']}"

    @settings(max_examples=50)
    @given(
        acr=st.floats(
            min_value=40.0, max_value=150.0, allow_nan=False, allow_infinity=False
        ),
        cmin=st.floats(
            min_value=25.0, max_value=50.0, allow_nan=False, allow_infinity=False
        ),
        h=st.floats(
            min_value=400.0, max_value=1200.0, allow_nan=False, allow_infinity=False
        ),
        x=st.floats(
            min_value=50.0, max_value=300.0, allow_nan=False, allow_infinity=False
        ),
        eps1=st.floats(
            min_value=1e-5, max_value=1e-3, allow_nan=False, allow_infinity=False
        ),
    )
    def test_wcr_monotonic_with_epsilon(
        self, acr: float, cmin: float, h: float, x: float, eps1: float
    ) -> None:
        """Monotonicity: higher epsilon_m → larger crack width."""
        assume(h > x + 50)
        assume(acr > cmin)
        denom = 1.0 + 2.0 * (acr - cmin) / (h - x)
        assume(denom > 0)
        eps2 = eps1 + 1e-4  # Strictly larger strain

        r1 = serviceability.check_crack_width(
            acr_mm=acr,
            cmin_mm=cmin,
            h_mm=h,
            x_mm=x,
            epsilon_m=eps1,
        )
        r2 = serviceability.check_crack_width(
            acr_mm=acr,
            cmin_mm=cmin,
            h_mm=h,
            x_mm=x,
            epsilon_m=eps2,
        )
        assert r2.computed["wcr_mm"] > r1.computed["wcr_mm"], (
            f"wcr should increase with epsilon_m: "
            f"wcr({eps1})={r1.computed['wcr_mm']:.6f} >= wcr({eps2})={r2.computed['wcr_mm']:.6f}"
        )


def _cracked_rectangle_inputs(b_mm: float, D_mm: float, x_over_d: float) -> dict:
    """Elastic rectangle: choose Ast from b*x²/2 = n*Ast*(d-x), n=8.

    M25 has Ec=25000 and Es=200000 N/mm². These are geometry/empirical
    inertia properties, not service-stress or construction approval.
    """
    d_mm = 0.9 * D_mm
    x_mm = x_over_d * d_mm
    n_ast_mm2 = b_mm * x_mm**2 / (2 * (d_mm - x_mm))
    igross = b_mm * D_mm**3 / 12
    icr = b_mm * x_mm**3 / 3 + n_ast_mm2 * (d_mm - x_mm) ** 2
    return {
        "igross_mm4": igross,
        "icr_mm4": icr,
        "d_mm": d_mm,
        "x_mm": x_mm,
        "mcr_knm": 3.5 * igross / (D_mm / 2) / 1e6,
    }


class TestEffectiveMomentOfInertiaProperties:
    """Property tests for calculate_effective_moment_of_inertia."""

    @settings(max_examples=50)
    @given(
        b_mm=beam_width(),
        D_mm=total_depth(),
        x_over_d=st.floats(
            min_value=0.16, max_value=0.45, allow_nan=False, allow_infinity=False
        ),
        ma_mcr_ratio=st.floats(
            min_value=1.1, max_value=10.0, allow_nan=False, allow_infinity=False
        ),
    )
    def test_bounded_between_icr_and_igross(
        self, b_mm: float, D_mm: float, x_over_d: float, ma_mcr_ratio: float
    ) -> None:
        """Ieff should be bounded: Icr <= Ieff <= Igross."""
        section = _cracked_rectangle_inputs(b_mm, D_mm, x_over_d)
        igross, icr = section["igross_mm4"], section["icr_mm4"]
        ma = section["mcr_knm"] * ma_mcr_ratio  # Ma > Mcr → cracked

        ieff = serviceability.calculate_effective_moment_of_inertia(
            ma_knm=ma,
            **section,
        )
        assert ieff >= icr - 1e-6, f"Ieff={ieff} < Icr={icr}"
        assert ieff <= igross + 1e-6, f"Ieff={ieff} > Igross={igross}"

    @settings(max_examples=50)
    @given(
        b_mm=beam_width(),
        D_mm=total_depth(),
        x_over_d=st.floats(
            min_value=0.16, max_value=0.45, allow_nan=False, allow_infinity=False
        ),
    )
    def test_decreases_as_ma_mcr_increases(
        self, b_mm: float, D_mm: float, x_over_d: float
    ) -> None:
        """Monotonicity: as Ma/Mcr increases, Ieff decreases toward Icr."""
        section = _cracked_rectangle_inputs(b_mm, D_mm, x_over_d)
        ma1 = section["mcr_knm"] * 1.5
        ma2 = section["mcr_knm"] * 3.0  # Larger Ma/Mcr ratio

        ieff1 = serviceability.calculate_effective_moment_of_inertia(
            ma_knm=ma1,
            **section,
        )
        ieff2 = serviceability.calculate_effective_moment_of_inertia(
            ma_knm=ma2,
            **section,
        )
        assert (
            ieff2 <= ieff1 + 1e-6
        ), f"Ieff should decrease with Ma/Mcr: Ieff(1.5)={ieff1} < Ieff(3.0)={ieff2}"


class TestGrossMomentOfInertiaProperties:
    """Property tests for calculate_gross_moment_of_inertia."""

    @settings(max_examples=50)
    @given(b=beam_width(), D=total_depth())
    def test_exact_formula(self, b: float, D: float) -> None:
        """Igross must equal b * D^3 / 12 exactly."""
        igross = serviceability.calculate_gross_moment_of_inertia(b_mm=b, D_mm=D)
        expected = b * D**3 / 12
        assert abs(igross - expected) < 1e-3, f"Igross={igross} != b*D^3/12={expected}"

    @settings(max_examples=50)
    @given(b=beam_width(), D=total_depth())
    def test_always_positive(self, b: float, D: float) -> None:
        """Igross should always be positive for valid dimensions."""
        igross = serviceability.calculate_gross_moment_of_inertia(b_mm=b, D_mm=D)
        assert igross > 0, f"Igross should be positive, got {igross}"


class TestDeflectionLevelBProperties:
    """Property tests for check_deflection_level_b."""

    @settings(max_examples=50)
    @given(section=beam_section(), fck=concrete_grade())
    def test_total_geq_short_term(self, section: dict, fck: int) -> None:
        """Total deflection >= short-term deflection (long-term adds, never subtracts)."""
        b, D, d = section["b"], section["D"], section["d"]
        span = d * 15  # Typical span/depth ~ 15
        # Ensure reasonable steel area: pt ~ 0.8%
        ast = 0.008 * b * d
        ma = 50.0  # Moderate service moment

        result = serviceability.check_deflection_level_b(
            b_mm=b,
            D_mm=D,
            d_mm=d,
            span_mm=span,
            ma_service_knm=ma,
            ast_mm2=ast,
            fck_nmm2=float(fck),
        )
        if result.delta_total_mm is not None and result.delta_short_mm is not None:
            assert (
                result.delta_total_mm >= result.delta_short_mm - 1e-9
            ), f"Total {result.delta_total_mm} < short-term {result.delta_short_mm}"

    @settings(max_examples=50)
    @given(section=beam_section(), fck=concrete_grade())
    def test_higher_moment_larger_deflection(self, section: dict, fck: int) -> None:
        """Monotonicity: higher service moment → larger total deflection."""
        b, D, d = section["b"], section["D"], section["d"]
        span = d * 15
        ast = 0.008 * b * d
        ma1 = 30.0
        ma2 = 80.0

        r1 = serviceability.check_deflection_level_b(
            b_mm=b,
            D_mm=D,
            d_mm=d,
            span_mm=span,
            ma_service_knm=ma1,
            ast_mm2=ast,
            fck_nmm2=float(fck),
        )
        r2 = serviceability.check_deflection_level_b(
            b_mm=b,
            D_mm=D,
            d_mm=d,
            span_mm=span,
            ma_service_knm=ma2,
            ast_mm2=ast,
            fck_nmm2=float(fck),
        )
        if (
            r1.delta_total_mm is not None
            and r2.delta_total_mm is not None
            and r1.delta_total_mm > 0
        ):
            assert r2.delta_total_mm >= r1.delta_total_mm - 1e-9, (
                f"Deflection should increase: δ({ma1})={r1.delta_total_mm:.4f} "
                f"> δ({ma2})={r2.delta_total_mm:.4f}"
            )
