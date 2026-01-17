# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Hypothesis property-based tests for slenderness module.

Tests cover:
- Slenderness ratio is always positive for valid inputs
- Slenderness check is consistent with ratio calculation
- All beam types have defined limits
- Monotonicity: increasing span increases slenderness ratio
"""

from __future__ import annotations

from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

from structural_lib.codes.is456.slenderness import (
    BeamType,
    calculate_slenderness_ratio,
    check_beam_slenderness,
    get_slenderness_limit,
)

# =============================================================================
# Strategies for Slenderness Testing
# =============================================================================


@st.composite
def beam_width_realistic(draw: st.DrawFn) -> float:
    """Generate realistic beam widths (150-600mm)."""
    return draw(st.floats(min_value=150.0, max_value=600.0, allow_nan=False))


@st.composite
def beam_depth_realistic(draw: st.DrawFn) -> float:
    """Generate realistic beam depths (300-1200mm)."""
    return draw(st.floats(min_value=300.0, max_value=1200.0, allow_nan=False))


@st.composite
def effective_length_realistic(draw: st.DrawFn) -> float:
    """Generate realistic effective lengths (2000-25000mm)."""
    return draw(st.floats(min_value=2000.0, max_value=25000.0, allow_nan=False))


@st.composite
def beam_type_strategy(draw: st.DrawFn) -> BeamType:
    """Generate a random BeamType."""
    return draw(st.sampled_from(list(BeamType)))


# =============================================================================
# Property Tests: calculate_slenderness_ratio
# =============================================================================


class TestSlendernessRatioProperties:
    """Property tests for calculate_slenderness_ratio."""

    @given(
        l_eff=st.floats(min_value=0.1, max_value=100000.0, allow_nan=False),
        b=st.floats(min_value=0.1, max_value=10000.0, allow_nan=False),
    )
    @settings(suppress_health_check=[HealthCheck.filter_too_much])
    def test_ratio_always_positive(self, l_eff: float, b: float) -> None:
        """Slenderness ratio is always positive for positive inputs."""
        assume(l_eff > 0)
        assume(b > 0)
        ratio = calculate_slenderness_ratio(l_eff, b)
        assert ratio > 0

    @given(
        l_eff=st.floats(min_value=100.0, max_value=50000.0, allow_nan=False),
        b=st.floats(min_value=100.0, max_value=1000.0, allow_nan=False),
    )
    def test_ratio_equals_division(self, l_eff: float, b: float) -> None:
        """Slenderness ratio equals l_eff / b exactly."""
        assume(b > 0)
        ratio = calculate_slenderness_ratio(l_eff, b)
        expected = l_eff / b
        assert abs(ratio - expected) < 1e-10

    @given(
        l1=st.floats(min_value=1000.0, max_value=10000.0, allow_nan=False),
        l2=st.floats(min_value=1000.0, max_value=10000.0, allow_nan=False),
        b=st.floats(min_value=100.0, max_value=1000.0, allow_nan=False),
    )
    def test_monotonicity_with_length(self, l1: float, l2: float, b: float) -> None:
        """Increasing length increases slenderness ratio."""
        assume(b > 0)
        assume(l1 != l2)

        r1 = calculate_slenderness_ratio(l1, b)
        r2 = calculate_slenderness_ratio(l2, b)

        if l1 < l2:
            assert r1 < r2
        else:
            assert r1 > r2

    @given(
        l_eff=st.floats(min_value=1000.0, max_value=10000.0, allow_nan=False),
        b1=st.floats(min_value=100.0, max_value=500.0, allow_nan=False),
        b2=st.floats(min_value=100.0, max_value=500.0, allow_nan=False),
    )
    def test_inverse_with_width(self, l_eff: float, b1: float, b2: float) -> None:
        """Increasing width decreases slenderness ratio."""
        assume(b1 > 0 and b2 > 0)
        # Use a minimum difference to avoid floating-point near-equality issues
        assume(abs(b1 - b2) > 0.01)

        r1 = calculate_slenderness_ratio(l_eff, b1)
        r2 = calculate_slenderness_ratio(l_eff, b2)

        if b1 < b2:
            assert r1 > r2  # Smaller width → larger ratio
        else:
            assert r1 < r2


# =============================================================================
# Property Tests: get_slenderness_limit
# =============================================================================


class TestSlendernessLimitProperties:
    """Property tests for get_slenderness_limit."""

    @given(beam_type=beam_type_strategy())
    def test_all_beam_types_have_limit(self, beam_type: BeamType) -> None:
        """All beam types have a defined slenderness limit."""
        limit = get_slenderness_limit(beam_type)
        assert limit > 0
        assert isinstance(limit, float)

    @given(beam_type=beam_type_strategy())
    def test_limit_reasonable_range(self, beam_type: BeamType) -> None:
        """Slenderness limits are in reasonable engineering range (10-100)."""
        limit = get_slenderness_limit(beam_type)
        assert 10 <= limit <= 100

    def test_cantilever_stricter_than_simply_supported(self) -> None:
        """Cantilever limit is stricter than simply supported."""
        cant_limit = get_slenderness_limit(BeamType.CANTILEVER)
        ss_limit = get_slenderness_limit(BeamType.SIMPLY_SUPPORTED)
        assert cant_limit < ss_limit


# =============================================================================
# Property Tests: check_beam_slenderness
# =============================================================================


class TestBeamSlendernessCheckProperties:
    """Property tests for check_beam_slenderness."""

    @given(
        b=beam_width_realistic(),
        d=beam_depth_realistic(),
        l_eff=effective_length_realistic(),
        beam_type=beam_type_strategy(),
    )
    @settings(max_examples=100)
    def test_result_has_required_fields(
        self, b: float, d: float, l_eff: float, beam_type: BeamType
    ) -> None:
        """Result always has required fields for valid inputs."""
        result = check_beam_slenderness(
            b_mm=b,
            d_mm=d,
            l_eff_mm=l_eff,
            beam_type=beam_type,
        )
        assert hasattr(result, "is_ok")
        assert hasattr(result, "is_slender")
        assert hasattr(result, "slenderness_ratio")
        assert hasattr(result, "slenderness_limit")
        assert hasattr(result, "utilization")
        assert hasattr(result, "remarks")

    @given(
        b=beam_width_realistic(),
        d=beam_depth_realistic(),
        l_eff=effective_length_realistic(),
        beam_type=beam_type_strategy(),
    )
    @settings(max_examples=100)
    def test_utilization_consistent_with_status(
        self, b: float, d: float, l_eff: float, beam_type: BeamType
    ) -> None:
        """Utilization > 1 implies slenderness check fails (barring D/b issues)."""
        result = check_beam_slenderness(
            b_mm=b,
            d_mm=d,
            l_eff_mm=l_eff,
            beam_type=beam_type,
        )
        # If slenderness utilization > 1 and no D/b issue, should fail
        if result.utilization > 1.0 and result.depth_to_width_ratio <= 6.0:
            assert result.is_ok is False

    @given(
        b=beam_width_realistic(),
        d=beam_depth_realistic(),
        l_eff=effective_length_realistic(),
        beam_type=beam_type_strategy(),
    )
    @settings(max_examples=100)
    def test_ratio_matches_calculation(
        self, b: float, d: float, l_eff: float, beam_type: BeamType
    ) -> None:
        """Slenderness ratio in result matches direct calculation."""
        result = check_beam_slenderness(
            b_mm=b,
            d_mm=d,
            l_eff_mm=l_eff,
            beam_type=beam_type,
        )
        expected_ratio = l_eff / b
        # Allow for rounding (result is rounded to 2 decimal places)
        assert abs(result.slenderness_ratio - expected_ratio) < 0.1

    @given(
        b=beam_width_realistic(),
        d=beam_depth_realistic(),
        l_eff=effective_length_realistic(),
        beam_type=beam_type_strategy(),
    )
    @settings(max_examples=100)
    def test_limit_matches_beam_type(
        self, b: float, d: float, l_eff: float, beam_type: BeamType
    ) -> None:
        """Slenderness limit in result matches beam type."""
        result = check_beam_slenderness(
            b_mm=b,
            d_mm=d,
            l_eff_mm=l_eff,
            beam_type=beam_type,
        )
        expected_limit = get_slenderness_limit(beam_type)
        assert result.slenderness_limit == expected_limit

    @given(
        b=beam_width_realistic(),
        d=beam_depth_realistic(),
        l_eff=effective_length_realistic(),
        beam_type=beam_type_strategy(),
    )
    @settings(max_examples=100)
    def test_depth_width_ratio_correct(
        self, b: float, d: float, l_eff: float, beam_type: BeamType
    ) -> None:
        """Depth-to-width ratio is calculated correctly."""
        result = check_beam_slenderness(
            b_mm=b,
            d_mm=d,
            l_eff_mm=l_eff,
            beam_type=beam_type,
        )
        expected_dw = d / b
        assert abs(result.depth_to_width_ratio - expected_dw) < 0.1

    @given(
        b=beam_width_realistic(),
        d=beam_depth_realistic(),
        l_eff=effective_length_realistic(),
    )
    @settings(max_examples=50)
    def test_lateral_restraint_allows_deep_beams(
        self, b: float, d: float, l_eff: float
    ) -> None:
        """Laterally restrained beams don't fail on D/b ratio alone."""
        # Force a deep beam scenario
        narrow_b = 150.0
        deep_d = 900.0  # D/b = 6

        result = check_beam_slenderness(
            b_mm=narrow_b,
            d_mm=deep_d,
            l_eff_mm=6000.0,  # Short span to avoid slenderness failure
            beam_type=BeamType.SIMPLY_SUPPORTED,
            has_lateral_restraint=True,
        )
        # With lateral restraint and short span, should pass
        # (slenderness = 6000/150 = 40 < 60)
        assert result.is_ok is True

    @given(
        b=st.floats(min_value=-1000.0, max_value=0.0),
        d=beam_depth_realistic(),
        l_eff=effective_length_realistic(),
    )
    @settings(max_examples=25)
    def test_invalid_width_returns_error(
        self, b: float, d: float, l_eff: float
    ) -> None:
        """Invalid width (zero or negative) returns error result."""
        result = check_beam_slenderness(
            b_mm=b,
            d_mm=d,
            l_eff_mm=l_eff,
        )
        assert result.is_ok is False
        assert len(result.errors) > 0


# =============================================================================
# Property Tests: Consistency and Invariants
# =============================================================================


class TestSlendernessInvariants:
    """Invariant tests for slenderness module."""

    @given(
        b=beam_width_realistic(),
        d=beam_depth_realistic(),
        l_eff=effective_length_realistic(),
    )
    @settings(max_examples=100)
    def test_utilization_formula(self, b: float, d: float, l_eff: float) -> None:
        """Utilization = ratio / limit for all valid inputs."""
        result = check_beam_slenderness(
            b_mm=b,
            d_mm=d,
            l_eff_mm=l_eff,
            beam_type=BeamType.SIMPLY_SUPPORTED,
        )
        expected_utilization = result.slenderness_ratio / result.slenderness_limit
        assert abs(result.utilization - expected_utilization) < 0.01

    @given(
        b=beam_width_realistic(),
        d=beam_depth_realistic(),
        l_eff=st.floats(min_value=1000.0, max_value=5000.0, allow_nan=False),
    )
    @settings(max_examples=50)
    def test_short_span_generally_ok(self, b: float, d: float, l_eff: float) -> None:
        """Short spans with reasonable proportions generally pass."""
        assume(d / b <= 4.0)  # Reasonable depth/width ratio

        result = check_beam_slenderness(
            b_mm=b,
            d_mm=d,
            l_eff_mm=l_eff,
            beam_type=BeamType.SIMPLY_SUPPORTED,
        )
        # For short spans with good proportions, should usually pass
        # (slenderness would be at most 5000/150 ≈ 33 < 60)
        if l_eff / b <= 60.0:
            assert result.is_ok is True
