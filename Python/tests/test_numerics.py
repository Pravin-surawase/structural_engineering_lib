"""Tests for structural_lib.core.numerics - safe arithmetic utilities.

Covers safe_divide, approx_equal, clamp, and ZERO_THRESHOLD.
Related: TASK-611
"""

from __future__ import annotations

import pytest

from structural_lib.core.numerics import (
    ZERO_THRESHOLD,
    approx_equal,
    clamp,
    safe_divide,
)

# ---------------------------------------------------------------------------
# safe_divide
# ---------------------------------------------------------------------------


class TestSafeDivide:
    """Tests for safe_divide()."""

    def test_normal_division(self):
        assert safe_divide(10, 2) == 5.0

    def test_division_by_zero_returns_default(self):
        assert safe_divide(10, 0) == 0.0

    def test_division_by_near_zero_returns_default(self):
        """Denominator below ZERO_THRESHOLD should return default."""
        assert safe_divide(10, 1e-15) == 0.0

    def test_custom_default(self):
        assert safe_divide(10, 0, default=float("inf")) == float("inf")

    def test_zero_numerator(self):
        assert safe_divide(0, 5) == 0.0

    def test_both_zero(self):
        assert safe_divide(0, 0) == 0.0

    def test_negative_numerator(self):
        assert safe_divide(-10, 2) == -5.0

    def test_negative_denominator_near_zero(self):
        """Negative near-zero denominator should also return default."""
        assert safe_divide(10, -1e-15) == 0.0

    def test_denominator_exactly_at_threshold(self):
        """abs(ZERO_THRESHOLD) is NOT < ZERO_THRESHOLD, so normal division."""
        result = safe_divide(10, ZERO_THRESHOLD)
        assert result == 10 / ZERO_THRESHOLD

    def test_large_values(self):
        assert safe_divide(1e18, 1e9) == pytest.approx(1e9)


# ---------------------------------------------------------------------------
# approx_equal
# ---------------------------------------------------------------------------


class TestApproxEqual:
    """Tests for approx_equal()."""

    def test_exactly_equal(self):
        assert approx_equal(1.0, 1.0) is True

    def test_close_within_default_tolerance(self):
        assert approx_equal(1.0, 1.0 + 1e-10) is True

    def test_not_close(self):
        assert approx_equal(1.0, 1.1) is False

    def test_custom_rel_tol(self):
        assert approx_equal(1.0, 1.05, rel_tol=0.1) is True

    def test_zero_comparison_default_tol(self):
        """math.isclose with default abs_tol=0 treats 0.0 vs tiny as not close."""
        assert approx_equal(0.0, 1e-15) is False

    def test_zero_comparison_with_abs_tol(self):
        assert approx_equal(0.0, 1e-15, abs_tol=1e-12) is True

    def test_negative_close(self):
        assert approx_equal(-1.0, -1.0 - 1e-10) is True


# ---------------------------------------------------------------------------
# clamp
# ---------------------------------------------------------------------------


class TestClamp:
    """Tests for clamp()."""

    def test_within_range(self):
        assert clamp(5, 0, 10) == 5

    def test_below_range(self):
        assert clamp(-5, 0, 10) == 0

    def test_above_range(self):
        assert clamp(15, 0, 10) == 10

    def test_at_lower_boundary(self):
        assert clamp(0, 0, 10) == 0

    def test_at_upper_boundary(self):
        assert clamp(10, 0, 10) == 10

    def test_invalid_range_raises(self):
        with pytest.raises(ValueError, match="min_val.*must be <= max_val"):
            clamp(5, 10, 0)

    def test_single_point_range(self):
        assert clamp(5, 5, 5) == 5

    def test_single_point_range_value_outside(self):
        assert clamp(3, 5, 5) == 5


# ---------------------------------------------------------------------------
# ZERO_THRESHOLD
# ---------------------------------------------------------------------------


class TestZeroThreshold:
    """Verify ZERO_THRESHOLD constant."""

    def test_value(self):
        assert ZERO_THRESHOLD == 1e-12
