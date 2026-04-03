# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tests for IS 456 Cl 26.5.3 — Column detailing checks.

Functions under test:
    - check_longitudinal_limits (Cl 26.5.3.1a)
    - get_min_bar_count (Cl 26.5.3.1b)
    - check_min_bar_diameter (Cl 26.5.3.1b)
    - calculate_tie_diameter (Cl 26.5.3.2a)
    - calculate_tie_spacing (Cl 26.5.3.2b)
    - check_bar_spacing (Cl 26.5.3.1c)
    - needs_cross_ties (Cl 26.5.3.2c)
    - create_column_detailing (Cl 26.5.3)

Test types per function-quality-pipeline Step 4:
    1. Unit tests (happy path) — 8 tests
    2. Edge-case / boundary tests — 6 tests
    3. Degenerate / error tests — 6 tests
    4. IS 456 / SP:16 benchmark tests — 3 tests
    5. Cross-tie tests — 3 tests
    6. Orchestrator integration tests — 3 tests
"""

from __future__ import annotations

import math

import pytest

from structural_lib.codes.is456.column.detailing import (
    calculate_tie_diameter,
    calculate_tie_spacing,
    check_bar_spacing,
    check_longitudinal_limits,
    check_min_bar_diameter,
    create_column_detailing,
    get_min_bar_count,
    needs_cross_ties,
)
from structural_lib.core.data_types import ColumnDetailingResult
from structural_lib.core.errors import DimensionError

# =============================================================================
# 1. Unit Tests — Happy Path (8 tests)
# =============================================================================


class TestUnitHappyPath:
    """Unit tests — happy path for column detailing functions."""

    def test_rectangular_standard_300x500_4x20(self):
        """300×500mm, 4-T20: tie_dia=6mm (20/4=5→6), spacing=min(300,320,300)=300mm.

        IS 456 Cl 26.5.3.2(a): tie_dia >= 20/4 = 5mm → round to 6mm standard
        IS 456 Cl 26.5.3.2(b): spacing <= min(300, 16×20=320, 300) = 300mm
        """
        result = create_column_detailing(
            b_mm=300.0,
            D_mm=500.0,
            cover_mm=40.0,
            fck=25.0,
            fy=415.0,
            num_bars=4,
            bar_dia_mm=20.0,
        )
        assert result.tie_dia_mm == 6.0
        assert result.max_tie_spacing_mm == pytest.approx(300.0)
        # Asc = 4×π/4×20² = 1256.6mm², Ag = 150000mm², ratio = 0.838% > 0.8% → valid
        assert result.is_valid is True

    def test_rectangular_large_400x600_8x25(self):
        """400×600mm, 8-T25: tie_dia=8mm (25/4=6.25→8), spacing=min(400,400,300)=300mm.

        IS 456 Cl 26.5.3.2(a): tie_dia >= 25/4 = 6.25mm → round to 8mm standard
        IS 456 Cl 26.5.3.2(b): spacing <= min(400, 16×25=400, 300) = 300mm
        """
        result = create_column_detailing(
            b_mm=400.0,
            D_mm=600.0,
            cover_mm=40.0,
            fck=25.0,
            fy=415.0,
            num_bars=8,
            bar_dia_mm=25.0,
        )
        assert result.tie_dia_mm == 8.0
        assert result.max_tie_spacing_mm == pytest.approx(300.0)

    def test_circular_column_450_6x16(self):
        """Circular 450mm, 6-T16: min 6 bars OK, tie_dia=6mm.

        IS 456 Cl 26.5.3.1(b): circular requires min 6 bars
        IS 456 Cl 26.5.3.2(a): 16/4 = 4mm → round to 6mm standard
        """
        result = create_column_detailing(
            b_mm=450.0,
            D_mm=450.0,
            cover_mm=40.0,
            fck=25.0,
            fy=415.0,
            num_bars=6,
            bar_dia_mm=16.0,
            is_circular=True,
        )
        assert result.min_bars_ok is True
        assert result.tie_dia_mm == 6.0
        # Circular Ag = π/4 × 450² ≈ 159043.1
        assert result.Ag_mm2 == pytest.approx(math.pi / 4 * 450**2, rel=0.01)

    def test_result_type(self):
        """Return type is ColumnDetailingResult with correct clause_ref."""
        result = create_column_detailing(
            b_mm=300.0,
            D_mm=300.0,
            cover_mm=40.0,
            fck=25.0,
            fy=415.0,
            num_bars=4,
            bar_dia_mm=16.0,
        )
        assert isinstance(result, ColumnDetailingResult)
        assert result.clause_ref == "Cl. 26.5.3"

    def test_auto_tie_diameter(self):
        """Omitting tie_dia_mm auto-computes per Cl 26.5.3.2(a)."""
        result = create_column_detailing(
            b_mm=300.0,
            D_mm=300.0,
            cover_mm=40.0,
            fck=25.0,
            fy=415.0,
            num_bars=4,
            bar_dia_mm=20.0,
        )
        # 20/4 = 5 → rounds to 6mm
        assert result.tie_dia_mm == result.tie_dia_required_mm
        assert result.tie_dia_mm == 6.0

    def test_steel_ratio_computed_correctly(self):
        """Steel ratio = Asc / Ag; Asc = n × π/4 × dia²."""
        result = create_column_detailing(
            b_mm=300.0,
            D_mm=500.0,
            cover_mm=40.0,
            fck=25.0,
            fy=415.0,
            num_bars=8,
            bar_dia_mm=20.0,
        )
        expected_asc = 8 * math.pi / 4 * 20.0**2  # 2513.27 mm²
        expected_ag = 300 * 500  # 150000 mm²
        expected_ratio = expected_asc / expected_ag  # 0.01676
        assert result.Asc_provided_mm2 == pytest.approx(expected_asc, rel=0.001)
        assert result.steel_ratio == pytest.approx(expected_ratio, rel=0.001)

    def test_small_bar_tie_spacing(self):
        """4-T12 in 400mm wide column: spacing = min(400, 16×12=192, 300) = 192mm.

        IS 456 Cl 26.5.3.2(b): 16 × smallest bar dia governs
        """
        spacing = calculate_tie_spacing(
            b_mm=400.0, D_mm=400.0, smallest_long_bar_dia_mm=12.0
        )
        assert spacing == pytest.approx(192.0)

    def test_all_checks_pass(self):
        """A well-designed column passes all checks (is_valid=True, no warnings).

        300×300mm, 4-T20: Asc = 1256.6mm², Ag = 90000mm², ratio = 1.4% → ok
        """
        result = create_column_detailing(
            b_mm=300.0,
            D_mm=300.0,
            cover_mm=40.0,
            fck=25.0,
            fy=415.0,
            num_bars=4,
            bar_dia_mm=20.0,
        )
        assert result.is_valid is True
        assert result.min_steel_ok is True
        assert result.max_steel_ok is True
        assert result.min_bars_ok is True
        assert result.min_bar_dia_ok is True
        assert result.bar_spacing_ok is True
        assert result.tie_spacing_ok is True
        assert len(result.warnings) == 0


# =============================================================================
# 2. Edge / Boundary Tests (6 tests)
# =============================================================================


class TestEdgeBoundary:
    """Edge-case and boundary tests per IS 456 Cl 26.5.3 limits."""

    def test_steel_ratio_exactly_0_8_pct(self):
        """Steel ratio exactly at 0.8% minimum → min_steel_ok=True.

        IS 456 Cl 26.5.3.1(a): 0.8% is the lower bound (inclusive).
        """
        Ag = 100_000.0  # e.g. 200×500
        Asc = 0.008 * Ag  # 800 mm²
        ratio, is_min_ok, is_max_ok, warnings = check_longitudinal_limits(Ag, Asc)
        assert ratio == pytest.approx(0.008)
        assert is_min_ok is True
        assert is_max_ok is True
        assert len(warnings) == 0

    def test_steel_ratio_exactly_4_pct(self):
        """Steel ratio exactly at 4% maximum → max_steel_ok=True (not at lap).

        IS 456 Cl 26.5.3.1(a): 4% is the upper bound (inclusive).
        """
        Ag = 100_000.0
        Asc = 0.04 * Ag  # 4000 mm²
        ratio, is_min_ok, is_max_ok, warnings = check_longitudinal_limits(Ag, Asc)
        assert ratio == pytest.approx(0.04)
        assert is_min_ok is True
        assert is_max_ok is True

    def test_steel_ratio_exactly_6_pct_at_lap(self):
        """At lap section, ratio=6% is acceptable.

        IS 456 Cl 26.5.3.1(a): at lap sections, max is 6%.
        """
        Ag = 100_000.0
        Asc = 0.06 * Ag  # 6000 mm²
        ratio, is_min_ok, is_max_ok, warnings = check_longitudinal_limits(
            Ag,
            Asc,
            at_lap_section=True,
        )
        assert ratio == pytest.approx(0.06)
        assert is_max_ok is True

    def test_bar_dia_exactly_12mm(self):
        """12mm bar passes the minimum diameter check.

        IS 456 Cl 26.5.3.1(b): minimum diameter = 12mm.
        """
        assert check_min_bar_diameter(12.0) is True
        assert check_min_bar_diameter(11.9) is False

    def test_tie_dia_exactly_quarter_24mm(self):
        """24mm bar: 24/4 = 6mm exactly → rounds to 6mm standard.

        IS 456 Cl 26.5.3.2(a): tie_dia >= max(bar/4, 6mm).
        """
        result = calculate_tie_diameter(24.0)
        assert result == 6.0

    def test_4_bars_rectangular_boundary(self):
        """Exactly 4 bars in rectangular column → min bar count OK.

        IS 456 Cl 26.5.3.1(b): minimum 4 bars for rectangular.
        """
        assert get_min_bar_count(is_circular=False) == 4
        result = create_column_detailing(
            b_mm=300.0,
            D_mm=300.0,
            cover_mm=40.0,
            fck=25.0,
            fy=415.0,
            num_bars=4,
            bar_dia_mm=20.0,
        )
        assert result.min_bars_ok is True


# =============================================================================
# 3. Degenerate / Error Tests (6 tests)
# =============================================================================


class TestDegenerateError:
    """Degenerate and error case tests."""

    def test_steel_below_minimum(self):
        """Ratio < 0.8% → min_steel_ok=False + warning.

        IS 456 Cl 26.5.3.1(a): below 0.8% not permitted.
        """
        Ag = 100_000.0
        Asc = 0.005 * Ag  # 0.5% — below 0.8%
        ratio, is_min_ok, is_max_ok, warnings = check_longitudinal_limits(Ag, Asc)
        assert is_min_ok is False
        assert any("below minimum" in w for w in warnings)

    def test_steel_above_4pct_not_at_lap(self):
        """Ratio > 4% without lap section → max_steel_ok=False.

        IS 456 Cl 26.5.3.1(a): 4% max away from laps.
        """
        Ag = 100_000.0
        Asc = 0.05 * Ag  # 5% — above 4%
        ratio, is_min_ok, is_max_ok, warnings = check_longitudinal_limits(
            Ag,
            Asc,
            at_lap_section=False,
        )
        assert is_max_ok is False
        assert any("exceeds maximum" in w for w in warnings)

    def test_steel_between_4_6pct_at_lap(self):
        """At lap section, 5% ratio: warn but max_steel_ok=True.

        IS 456 Cl 26.5.3.1(a): 4-6% allowed at laps with a warning.
        """
        Ag = 100_000.0
        Asc = 0.05 * Ag  # 5% — between 4% and 6%
        ratio, is_min_ok, is_max_ok, warnings = check_longitudinal_limits(
            Ag,
            Asc,
            at_lap_section=True,
        )
        assert is_max_ok is True
        assert any("within lap section limit" in w for w in warnings)

    def test_bar_count_below_min_rectangular(self):
        """3 bars in rectangular column → min_bars_ok=False.

        IS 456 Cl 26.5.3.1(b): min 4 bars for rectangular.
        """
        result = create_column_detailing(
            b_mm=300.0,
            D_mm=300.0,
            cover_mm=40.0,
            fck=25.0,
            fy=415.0,
            num_bars=3,
            bar_dia_mm=20.0,
        )
        assert result.min_bars_ok is False
        assert any("below minimum" in w for w in result.warnings)

    def test_bar_count_below_min_circular(self):
        """5 bars in circular column → min_bars_ok=False.

        IS 456 Cl 26.5.3.1(b): min 6 bars for circular.
        """
        result = create_column_detailing(
            b_mm=400.0,
            D_mm=400.0,
            cover_mm=40.0,
            fck=25.0,
            fy=415.0,
            num_bars=5,
            bar_dia_mm=16.0,
            is_circular=True,
        )
        assert result.min_bars_ok is False

    def test_invalid_inputs_raise_dimension_error(self):
        """Invalid dimensions raise DimensionError.

        Zero/negative column dimensions must be rejected.
        """
        with pytest.raises(DimensionError):
            create_column_detailing(
                b_mm=0.0,
                D_mm=300.0,
                cover_mm=40.0,
                fck=25.0,
                fy=415.0,
                num_bars=4,
                bar_dia_mm=16.0,
            )

        with pytest.raises(DimensionError):
            create_column_detailing(
                b_mm=300.0,
                D_mm=-1.0,
                cover_mm=40.0,
                fck=25.0,
                fy=415.0,
                num_bars=4,
                bar_dia_mm=16.0,
            )

        with pytest.raises(DimensionError):
            create_column_detailing(
                b_mm=300.0,
                D_mm=300.0,
                cover_mm=40.0,
                fck=25.0,
                fy=415.0,
                num_bars=4,
                bar_dia_mm=0.0,
            )

        with pytest.raises(DimensionError):
            check_longitudinal_limits(Ag_mm2=0.0, Asc_mm2=100.0)

        with pytest.raises(DimensionError):
            check_longitudinal_limits(Ag_mm2=100.0, Asc_mm2=-10.0)

        with pytest.raises(DimensionError):
            calculate_tie_diameter(0.0)

        with pytest.raises(DimensionError):
            calculate_tie_spacing(b_mm=0.0, D_mm=300.0, smallest_long_bar_dia_mm=12.0)


# =============================================================================
# 4. IS 456 / SP:16 Benchmark Tests (3 tests)
# =============================================================================


class TestIS456Benchmark:
    """IS 456 Cl 26.5.3 formula verification tests."""

    def test_tie_spacing_formula_300x300_16mm(self):
        """300×300, T16 bars: min(300, 16×16=256, 300) = 256mm.

        IS 456 Cl 26.5.3.2(b): spacing = min(least dim, 16×dia, 300).
        """
        spacing = calculate_tie_spacing(
            b_mm=300.0, D_mm=300.0, smallest_long_bar_dia_mm=16.0
        )
        assert spacing == pytest.approx(256.0)

    def test_tie_spacing_formula_250x600_20mm(self):
        """250×600, T20 bars: min(250, 16×20=320, 300) = 250mm.

        IS 456 Cl 26.5.3.2(b): least lateral dimension governs.
        """
        spacing = calculate_tie_spacing(
            b_mm=250.0, D_mm=600.0, smallest_long_bar_dia_mm=20.0
        )
        assert spacing == pytest.approx(250.0)

    @pytest.mark.parametrize(
        "long_dia, expected_tie_dia",
        [
            (16.0, 6.0),  # 16/4=4 → max(4,6)=6 → std 6
            (20.0, 6.0),  # 20/4=5 → max(5,6)=6 → std 6
            (25.0, 8.0),  # 25/4=6.25 → max(6.25,6)=6.25 → std 8
            (32.0, 8.0),  # 32/4=8 → max(8,6)=8 → std 8
            (36.0, 10.0),  # 36/4=9 → max(9,6)=9 → std 10
        ],
        ids=["T16→6", "T20→6", "T25→8", "T32→8", "T36→10"],
    )
    def test_tie_diameter_formula_various(self, long_dia, expected_tie_dia):
        """Tie diameter = ceil_to_std(max(bar_dia/4, 6mm)).

        IS 456 Cl 26.5.3.2(a): lateral tie diameter formula.
        """
        result = calculate_tie_diameter(long_dia)
        assert result == pytest.approx(expected_tie_dia)


# =============================================================================
# 5. Cross-Tie Tests (3 tests)
# =============================================================================


class TestCrossTies:
    """Cross-tie requirement tests per IS 456 Cl 26.5.3.2(c)."""

    def test_cross_ties_not_needed_300x300(self):
        """300×300, 4-T16, cover=40: face = 300 - 80 - 16 = 204mm < 300mm → no cross-ties.

        IS 456 Cl 26.5.3.2(c): threshold is 2 × 150mm = 300mm.
        """
        result = needs_cross_ties(
            b_mm=300.0,
            D_mm=300.0,
            cover_mm=40.0,
            bar_dia_mm=16.0,
            num_bars=6,
        )
        # face_b = 300 - 80 - 16 = 204mm < 300 → False
        assert result is False

    def test_cross_ties_needed_large_column(self):
        """500×500, 8-T20, cover=40: face = 500 - 80 - 20 = 400mm > 300mm → cross-ties.

        IS 456 Cl 26.5.3.2(c): intermediate bars > 150mm from restrained bar.
        """
        result = needs_cross_ties(
            b_mm=500.0,
            D_mm=500.0,
            cover_mm=40.0,
            bar_dia_mm=20.0,
            num_bars=8,
        )
        assert result is True

    def test_cross_ties_4_bars_always_false(self):
        """4 bars → all corner bars are restrained → no cross-ties regardless of size.

        IS 456 Cl 26.5.3.2(c): corner bars are always restrained by tie bends.
        """
        # Even with a large column, 4 bars = all at corners
        result = needs_cross_ties(
            b_mm=800.0,
            D_mm=800.0,
            cover_mm=40.0,
            bar_dia_mm=32.0,
            num_bars=4,
        )
        assert result is False


# =============================================================================
# 6. Orchestrator Integration Tests (3 tests)
# =============================================================================


class TestCreateColumnDetailing:
    """Integration tests for create_column_detailing orchestrator."""

    def test_create_detailing_valid_column(self):
        """Full pipeline: 300×300, 4-T20 → valid column, all checks pass.

        Asc = 4 × π/4 × 20² = 1256.6mm², Ag = 90000mm², ratio = 1.4%
        """
        result = create_column_detailing(
            b_mm=300.0,
            D_mm=300.0,
            cover_mm=40.0,
            fck=25.0,
            fy=415.0,
            num_bars=4,
            bar_dia_mm=20.0,
        )
        assert isinstance(result, ColumnDetailingResult)
        assert result.is_valid is True
        assert result.b_mm == 300.0
        assert result.D_mm == 300.0
        assert result.Ag_mm2 == pytest.approx(90000.0)
        assert result.num_bars == 4
        assert result.bar_dia_mm == 20.0
        assert result.tie_dia_mm == 6.0
        assert result.tie_spacing_ok is True
        assert result.cross_ties_needed is False
        # Verify to_dict and summary methods
        d = result.to_dict()
        assert isinstance(d, dict)
        assert "is_valid" in d
        s = result.summary()
        assert "VALID" in s

    def test_create_detailing_invalid_column(self):
        """Column with multiple violations → is_valid=False.

        300×500, 3-T10: too few bars, bar dia < 12mm, steel ratio < 0.8%
        """
        result = create_column_detailing(
            b_mm=300.0,
            D_mm=500.0,
            cover_mm=40.0,
            fck=25.0,
            fy=415.0,
            num_bars=3,
            bar_dia_mm=10.0,
        )
        assert result.is_valid is False
        assert result.min_bars_ok is False
        assert result.min_bar_dia_ok is False
        assert result.min_steel_ok is False
        assert len(result.warnings) >= 3
        s = result.summary()
        assert "INVALID" in s

    def test_create_detailing_circular(self):
        """Circular column: is_circular=True, Ag = π/4 × D².

        450mm circular, 6-T20: Asc = 6 × π/4 × 20² = 1884.96mm²
        Ag = π/4 × 450² = 159043.1mm², ratio = 1.185%
        """
        result = create_column_detailing(
            b_mm=450.0,
            D_mm=450.0,
            cover_mm=40.0,
            fck=25.0,
            fy=415.0,
            num_bars=6,
            bar_dia_mm=20.0,
            is_circular=True,
        )
        expected_ag = math.pi / 4 * 450**2
        expected_asc = 6 * math.pi / 4 * 20**2
        assert result.Ag_mm2 == pytest.approx(expected_ag, rel=0.001)
        assert result.Asc_provided_mm2 == pytest.approx(expected_asc, rel=0.001)
        assert result.min_bars_ok is True  # 6 >= 6 for circular
        assert result.min_steel_ok is True  # ~1.19% > 0.8%


# =============================================================================
# 7. Additional helper function tests
# =============================================================================


class TestHelperFunctions:
    """Direct tests for individual helper functions."""

    def test_get_min_bar_count_rectangular(self):
        """Rectangular column requires minimum 4 bars."""
        assert get_min_bar_count(is_circular=False) == 4

    def test_get_min_bar_count_circular(self):
        """Circular column requires minimum 6 bars."""
        assert get_min_bar_count(is_circular=True) == 6

    def test_check_min_bar_diameter_passes(self):
        """Bar diameters >= 12mm pass."""
        assert check_min_bar_diameter(12.0) is True
        assert check_min_bar_diameter(16.0) is True
        assert check_min_bar_diameter(20.0) is True

    def test_check_min_bar_diameter_fails(self):
        """Bar diameters < 12mm fail."""
        assert check_min_bar_diameter(10.0) is False
        assert check_min_bar_diameter(8.0) is False

    def test_check_bar_spacing_circular(self):
        """Circular bar spacing: arc spacing for 6 bars around 450mm circle."""
        spacing, ok, warnings = check_bar_spacing(
            b_mm=450.0,
            D_mm=450.0,
            cover_mm=40.0,
            bar_dia_mm=16.0,
            num_bars=6,
            is_circular=True,
        )
        # Effective dia = 450 - 80 - 16 = 354mm
        # Circumference = π × 354 ≈ 1112.1mm
        # Clear spacing = (1112.1 - 6 × 16) / 6 ≈ 169.3mm
        assert spacing == pytest.approx(169.3, abs=1.0)
        assert ok is True

    def test_check_bar_spacing_dimension_error(self):
        """Invalid dimensions raise DimensionError."""
        with pytest.raises(DimensionError):
            check_bar_spacing(
                b_mm=0.0,
                D_mm=300.0,
                cover_mm=40.0,
                bar_dia_mm=16.0,
                num_bars=4,
            )

    def test_frozen_result(self):
        """ColumnDetailingResult is immutable (frozen dataclass)."""
        result = create_column_detailing(
            b_mm=300.0,
            D_mm=300.0,
            cover_mm=40.0,
            fck=25.0,
            fy=415.0,
            num_bars=4,
            bar_dia_mm=20.0,
        )
        with pytest.raises(AttributeError):
            result.b_mm = 999.0  # type: ignore[misc]
