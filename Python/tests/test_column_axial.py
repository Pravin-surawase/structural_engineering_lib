# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for column axial module — effective_length() per IS 456 Table 28.

TASK-636: Comprehensive 6-type test coverage for effective_length().

References:
    IS 456:2000 Cl. 25.2, Table 28
"""

from __future__ import annotations

import pytest

from structural_lib.codes.is456.column.axial import (
    classify_column,
    effective_length,
)
from structural_lib.core.data_types import (
    ColumnClassification,
    EndCondition,
)
from structural_lib.core.errors import DimensionError

# ===========================================================================
# 1. Unit tests — All 7 end conditions, l=3000mm, recommended ratios
# ===========================================================================

# IS 456 Table 28 — recommended le/l ratios
_TABLE_28_RECOMMENDED = [
    (EndCondition.FIXED_FIXED, 0.65, 1950.0),
    (EndCondition.FIXED_HINGED, 0.80, 2400.0),
    (EndCondition.FIXED_FIXED_SWAY, 1.20, 3600.0),
    (EndCondition.FIXED_FREE, 2.00, 6000.0),
    (EndCondition.HINGED_HINGED, 1.00, 3000.0),
    (EndCondition.FIXED_PARTIAL, 1.50, 4500.0),
    (EndCondition.HINGED_PARTIAL, 2.00, 6000.0),
]


class TestEffectiveLengthRecommended:
    """Unit tests: effective_length with recommended values (default). IS 456 Table 28."""

    @pytest.mark.parametrize(
        "end_condition, ratio, expected_le",
        _TABLE_28_RECOMMENDED,
        ids=[ec.name for ec, _, _ in _TABLE_28_RECOMMENDED],
    )
    def test_all_7_end_conditions(self, end_condition, ratio, expected_le):
        """IS 456 Table 28: le = ratio x l for all 7 cases."""
        result = effective_length(3000.0, end_condition)
        assert result == pytest.approx(expected_le)

    def test_fixed_fixed_ratio(self):
        """IS 456 Table 28 Case 1: FIXED_FIXED recommended le/l = 0.65."""
        le = effective_length(3000.0, EndCondition.FIXED_FIXED)
        assert le / 3000.0 == pytest.approx(0.65)

    def test_fixed_free_cantilever(self):
        """IS 456 Table 28 Case 4: FIXED_FREE (cantilever) le/l = 2.00."""
        le = effective_length(5000.0, EndCondition.FIXED_FREE)
        assert le == pytest.approx(10000.0)

    def test_hinged_hinged_identity(self):
        """IS 456 Table 28 Case 5: HINGED_HINGED le/l = 1.00 (le = l)."""
        le = effective_length(4000.0, EndCondition.HINGED_HINGED)
        assert le == pytest.approx(4000.0)


# ===========================================================================
# 2. Theoretical mode — use_theoretical=True
# ===========================================================================

_TABLE_28_THEORETICAL = [
    # (end_condition, expected_ratio, expected_le_for_l3000)
    (EndCondition.FIXED_FIXED, 0.50, 1500.0),
    (EndCondition.FIXED_HINGED, 0.70, 2100.0),
    (EndCondition.FIXED_FIXED_SWAY, 1.00, 3000.0),
    (EndCondition.FIXED_FREE, 2.00, 6000.0),
    (EndCondition.HINGED_HINGED, 1.00, 3000.0),
    # Cases 6 & 7 fall back to recommended (no theoretical value)
    (EndCondition.FIXED_PARTIAL, 1.50, 4500.0),
    (EndCondition.HINGED_PARTIAL, 2.00, 6000.0),
]


class TestEffectiveLengthTheoretical:
    """Tests for use_theoretical=True mode. IS 456 Table 28."""

    @pytest.mark.parametrize(
        "end_condition, ratio, expected_le",
        _TABLE_28_THEORETICAL,
        ids=[ec.name for ec, _, _ in _TABLE_28_THEORETICAL],
    )
    def test_all_7_end_conditions_theoretical(self, end_condition, ratio, expected_le):
        """IS 456 Table 28 theoretical: all 7 cases."""
        result = effective_length(3000.0, end_condition, use_theoretical=True)
        assert result == pytest.approx(expected_le)

    def test_fixed_fixed_theoretical_lower_than_recommended(self):
        """Theoretical FIXED_FIXED (0.50) < recommended (0.65)."""
        le_theo = effective_length(
            3000.0, EndCondition.FIXED_FIXED, use_theoretical=True
        )
        le_rec = effective_length(
            3000.0, EndCondition.FIXED_FIXED, use_theoretical=False
        )
        assert le_theo < le_rec

    def test_fixed_partial_fallback_to_recommended(self):
        """Cases 6 & 7: no theoretical value -> fall back to recommended."""
        le_theo = effective_length(
            3000.0, EndCondition.FIXED_PARTIAL, use_theoretical=True
        )
        le_rec = effective_length(
            3000.0, EndCondition.FIXED_PARTIAL, use_theoretical=False
        )
        assert le_theo == pytest.approx(le_rec)

    def test_hinged_partial_fallback_to_recommended(self):
        """Case 7: no theoretical value -> fall back to recommended."""
        le_theo = effective_length(
            3000.0, EndCondition.HINGED_PARTIAL, use_theoretical=True
        )
        le_rec = effective_length(
            3000.0, EndCondition.HINGED_PARTIAL, use_theoretical=False
        )
        assert le_theo == pytest.approx(le_rec)


# ===========================================================================
# 3. Edge cases — very short and very tall columns
# ===========================================================================


class TestEffectiveLengthEdgeCases:
    """Edge cases for effective_length."""

    def test_very_short_column(self):
        """Edge: l=100mm, FIXED_FIXED -> 65mm."""
        le = effective_length(100.0, EndCondition.FIXED_FIXED)
        assert le == pytest.approx(65.0)

    def test_very_tall_column(self):
        """Edge: l=30000mm, FIXED_FREE -> 60000mm."""
        le = effective_length(30000.0, EndCondition.FIXED_FREE)
        assert le == pytest.approx(60000.0)

    def test_very_small_positive_length(self):
        """Edge: tiny positive length should still work."""
        le = effective_length(0.001, EndCondition.HINGED_HINGED)
        assert le == pytest.approx(0.001)

    def test_large_length_fixed_fixed_sway(self):
        """Edge: l=20000mm, FIXED_FIXED_SWAY -> 24000mm."""
        le = effective_length(20000.0, EndCondition.FIXED_FIXED_SWAY)
        assert le == pytest.approx(24000.0)


# ===========================================================================
# 4. Degenerate cases — l_mm=0 and l_mm<0 raise DimensionError
# ===========================================================================


class TestEffectiveLengthDegenerate:
    """Degenerate inputs for effective_length."""

    def test_zero_length_raises_dimension_error(self):
        """Degenerate: l_mm=0 -> DimensionError."""
        with pytest.raises(DimensionError, match="must be > 0"):
            effective_length(0.0, EndCondition.FIXED_FIXED)

    def test_negative_length_raises_dimension_error(self):
        """Degenerate: l_mm<0 -> DimensionError."""
        with pytest.raises(DimensionError, match="must be > 0"):
            effective_length(-1000.0, EndCondition.FIXED_HINGED)

    def test_large_negative_raises(self):
        """Degenerate: very large negative."""
        with pytest.raises(DimensionError):
            effective_length(-99999.0, EndCondition.HINGED_HINGED)


# ===========================================================================
# 5. Integration — effective_length feeds into classify_column
# ===========================================================================


class TestEffectiveLengthIntegration:
    """Integration: effective_length -> classify_column."""

    def test_fixed_fixed_3000mm_is_short(self):
        """Integration: le=1950mm, D=400mm -> ratio=4.875 < 12 -> SHORT.
        IS 456 Cl 25.1.2
        """
        le = effective_length(3000.0, EndCondition.FIXED_FIXED)
        assert le == pytest.approx(1950.0)
        result = classify_column(le, 400.0)
        assert result == ColumnClassification.SHORT

    def test_fixed_free_3000mm_is_slender(self):
        """Integration: le=6000mm, D=300mm -> ratio=20 >= 12 -> SLENDER."""
        le = effective_length(3000.0, EndCondition.FIXED_FREE)
        assert le == pytest.approx(6000.0)
        result = classify_column(le, 300.0)
        assert result == ColumnClassification.SLENDER

    def test_hinged_hinged_3000mm_boundary(self):
        """Integration: le=3000mm, D=250mm -> ratio=12.0 -> SLENDER (strict <12)."""
        le = effective_length(3000.0, EndCondition.HINGED_HINGED)
        assert le == pytest.approx(3000.0)
        result = classify_column(le, 250.0)
        assert result == ColumnClassification.SLENDER

    def test_fixed_hinged_short_column(self):
        """Integration: le=2400mm, D=500mm -> ratio=4.8 < 12 -> SHORT."""
        le = effective_length(3000.0, EndCondition.FIXED_HINGED)
        assert le == pytest.approx(2400.0)
        result = classify_column(le, 500.0)
        assert result == ColumnClassification.SHORT


# ===========================================================================
# 6. Parametrize — comprehensive parametric test
# ===========================================================================


class TestEffectiveLengthParametrize:
    """Parametrized tests combining length, end condition, and mode."""

    @pytest.mark.parametrize("l_mm", [1000, 3000, 5000, 10000])
    @pytest.mark.parametrize(
        "end_condition, ratio",
        [
            (EndCondition.FIXED_FIXED, 0.65),
            (EndCondition.FIXED_HINGED, 0.80),
            (EndCondition.FIXED_FIXED_SWAY, 1.20),
            (EndCondition.FIXED_FREE, 2.00),
            (EndCondition.HINGED_HINGED, 1.00),
            (EndCondition.FIXED_PARTIAL, 1.50),
            (EndCondition.HINGED_PARTIAL, 2.00),
        ],
    )
    def test_le_equals_ratio_times_l(self, l_mm, end_condition, ratio):
        """IS 456 Table 28: le = ratio x l for all combinations."""
        le = effective_length(l_mm, end_condition)
        assert le == pytest.approx(ratio * l_mm)

    @pytest.mark.parametrize(
        "end_condition",
        list(EndCondition),
    )
    def test_effective_length_always_positive(self, end_condition):
        """Effective length must always be positive for positive input."""
        le = effective_length(3000.0, end_condition)
        assert le > 0.0

    @pytest.mark.parametrize(
        "end_condition, theo_ratio, rec_ratio",
        [
            (EndCondition.FIXED_FIXED, 0.50, 0.65),
            (EndCondition.FIXED_HINGED, 0.70, 0.80),
            (EndCondition.FIXED_FIXED_SWAY, 1.00, 1.20),
        ],
    )
    def test_theoretical_le_recommended(self, end_condition, theo_ratio, rec_ratio):
        """Theoretical value <= recommended value for cases 1-3."""
        le_theo = effective_length(3000.0, end_condition, use_theoretical=True)
        le_rec = effective_length(3000.0, end_condition, use_theoretical=False)
        assert le_theo <= le_rec
        assert le_theo == pytest.approx(theo_ratio * 3000.0)
        assert le_rec == pytest.approx(rec_ratio * 3000.0)
