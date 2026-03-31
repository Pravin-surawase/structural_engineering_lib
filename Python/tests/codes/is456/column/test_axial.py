# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tests for column axial capacity and classification per IS 456:2000.

Functions under test:
    - classify_column (Cl. 25.1.2)
    - min_eccentricity (Cl. 25.4)
    - short_axial_capacity (Cl. 39.3)

Test types per function-quality-pipeline Step 4:
    1. Unit tests (happy path)
    2. Boundary tests
    3. Edge-case / degenerate tests
    4. SP:16 benchmark tests (+/-0.1%)
    5. Textbook verification tests
    6. Property-based tests (Hypothesis)
"""

from __future__ import annotations

import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from structural_lib.codes.is456.column.axial import (
    classify_column,
    min_eccentricity,
    short_axial_capacity,
)
from structural_lib.core.data_types import ColumnAxialResult, ColumnClassification
from structural_lib.core.errors import DimensionError, MaterialError

# =============================================================================
# 1. classify_column -- IS 456 Cl 25.1.2
# =============================================================================


class TestClassifyColumn:
    """Tests for column classification per IS 456 Cl 25.1.2.

    IS 456 Cl 25.1.2: A compression member is classified as short when
    the ratio le/D < 12 (strict less-than). At le/D = 12 exactly, the
    column is SLENDER.
    """

    # ----- 1a. Unit tests (happy path) -----

    def test_short_column_typical(self):
        """Standard short column: le=3000, D=300, ratio=10, SHORT."""
        assert classify_column(le_mm=3000, D_mm=300) == ColumnClassification.SHORT

    def test_slender_column_typical(self):
        """Standard slender column: le=6000, D=300, ratio=20, SLENDER."""
        assert classify_column(le_mm=6000, D_mm=300) == ColumnClassification.SLENDER

    def test_short_column_square(self):
        """Square column: le=4000, D=400, ratio=10, SHORT."""
        assert classify_column(le_mm=4000, D_mm=400) == ColumnClassification.SHORT

    def test_slender_column_high_ratio(self):
        """High slenderness: le=8000, D=300, ratio=26.67, SLENDER."""
        assert classify_column(le_mm=8000, D_mm=300) == ColumnClassification.SLENDER

    # ----- 1b. Boundary tests -----

    def test_boundary_just_below_12(self):
        """le/D = 11.99 -> SHORT (strict less-than)."""
        assert classify_column(le_mm=3597, D_mm=300) == ColumnClassification.SHORT

    def test_boundary_exactly_12(self):
        """le/D = 12.0 exactly -> SLENDER (strict less-than, not <=)."""
        assert classify_column(le_mm=3600, D_mm=300) == ColumnClassification.SLENDER

    def test_boundary_just_above_12(self):
        """le/D = 12.01 -> SLENDER."""
        assert classify_column(le_mm=3603, D_mm=300) == ColumnClassification.SLENDER

    def test_boundary_very_small_epsilon_below(self):
        """le/D = 12 - epsilon -> SHORT."""
        D = 1000.0
        le = 12.0 * D - 0.001
        assert classify_column(le_mm=le, D_mm=D) == ColumnClassification.SHORT

    def test_boundary_ratio_1(self):
        """le/D = 1 -> SHORT (well within)."""
        assert classify_column(le_mm=300, D_mm=300) == ColumnClassification.SHORT

    # ----- 1c. Edge-case / error tests -----

    def test_le_zero_raises(self):
        """le_mm = 0 -> DimensionError."""
        with pytest.raises(DimensionError):
            classify_column(le_mm=0, D_mm=300)

    def test_le_negative_raises(self):
        """le_mm < 0 -> DimensionError."""
        with pytest.raises(DimensionError):
            classify_column(le_mm=-100, D_mm=300)

    def test_D_zero_raises(self):
        """D_mm = 0 -> DimensionError."""
        with pytest.raises(DimensionError):
            classify_column(le_mm=3000, D_mm=0)

    def test_D_negative_raises(self):
        """D_mm < 0 -> DimensionError."""
        with pytest.raises(DimensionError):
            classify_column(le_mm=3000, D_mm=-100)

    def test_very_large_slenderness(self):
        """le=100000, D=300, ratio=333.3 -> SLENDER (exceeds max=60 warning)."""
        result = classify_column(le_mm=100000, D_mm=300)
        assert result == ColumnClassification.SLENDER

    def test_very_small_D(self):
        """D=1mm (unrealistic but valid), le=100/1=100 -> SLENDER."""
        result = classify_column(le_mm=100, D_mm=1)
        assert result == ColumnClassification.SLENDER

    # ----- 1d. SP:16 benchmark tests -----

    @pytest.mark.parametrize(
        "le_mm, D_mm, expected",
        [
            (3000, 300, ColumnClassification.SHORT),
            (4800, 400, ColumnClassification.SLENDER),
            (4000, 400, ColumnClassification.SHORT),
            (8000, 300, ColumnClassification.SLENDER),
            (7200, 300, ColumnClassification.SLENDER),
        ],
        ids=[
            "SP16-ratio10-SHORT",
            "SP16-ratio12-boundary-SLENDER",
            "SP16-ratio10-400x400-SHORT",
            "SP16-ratio26.67-SLENDER",
            "SP16-ratio24-SLENDER",
        ],
    )
    def test_sp16_benchmarks(self, le_mm, D_mm, expected):
        """SP:16 benchmark: classification results.

        Source: IS 456:2000, Cl 25.1.2 / SP:16 Design Aids
        """
        assert classify_column(le_mm=le_mm, D_mm=D_mm) == expected

    # ----- 1e. Property-based tests (Hypothesis) -----

    @given(
        le=st.floats(min_value=1, max_value=100_000),
        D=st.floats(min_value=1, max_value=5000),
    )
    @settings(max_examples=200)
    def test_returns_valid_enum(self, le, D):
        """Property: classify_column always returns a valid ColumnClassification."""
        result = classify_column(le_mm=le, D_mm=D)
        assert result in (ColumnClassification.SHORT, ColumnClassification.SLENDER)

    @given(D=st.floats(min_value=100, max_value=2000))
    @settings(max_examples=100)
    def test_monotonicity_increasing_le(self, D):
        """Monotonicity: if le increases (D fixed), SHORT->SLENDER, never reverse."""
        le_short = D * 5
        le_slender = D * 15
        assert classify_column(le_mm=le_short, D_mm=D) == ColumnClassification.SHORT
        assert classify_column(le_mm=le_slender, D_mm=D) == ColumnClassification.SLENDER

    @given(le=st.floats(min_value=1000, max_value=50_000))
    @settings(max_examples=100)
    def test_monotonicity_increasing_D(self, le):
        """Monotonicity: if D increases (le fixed), SLENDER->SHORT, never reverse."""
        D_large = le / 5
        D_small = le / 15
        assert classify_column(le_mm=le, D_mm=D_large) == ColumnClassification.SHORT
        assert classify_column(le_mm=le, D_mm=D_small) == ColumnClassification.SLENDER


# =============================================================================
# 2. min_eccentricity -- IS 456 Cl 25.4
# =============================================================================


class TestMinEccentricity:
    """Tests for minimum eccentricity per IS 456 Cl 25.4.

    IS 456 Cl 25.4: e_min = max(l/500 + D/30, 20) mm
    where l = unsupported length, D = lateral dimension.
    The result is always >= 20 mm.
    """

    # ----- 2a. Unit tests (happy path) -----

    def test_typical_above_floor(self):
        """l=6000, D=300: max(12+10, 20) = 22.0 mm."""
        result = min_eccentricity(l_unsupported_mm=6000, D_mm=300)
        assert result == pytest.approx(22.0, abs=0.01)

    def test_typical_large_column(self):
        """l=4500, D=500: max(9+16.67, 20) = 25.67 mm."""
        result = min_eccentricity(l_unsupported_mm=4500, D_mm=500)
        assert result == pytest.approx(25.667, abs=0.01)

    def test_floor_governs(self):
        """l=3000, D=400: max(6+13.33, 20) = 20.0 mm (floor governs)."""
        result = min_eccentricity(l_unsupported_mm=3000, D_mm=400)
        assert result == pytest.approx(20.0, abs=0.01)

    # ----- 2b. Boundary tests -----

    def test_exactly_at_floor(self):
        """l=5000, D=300: 10+10=20 exactly -> 20.0 mm."""
        result = min_eccentricity(l_unsupported_mm=5000, D_mm=300)
        assert result == pytest.approx(20.0, abs=0.001)

    def test_just_below_floor(self):
        """l=2000, D=300: max(4+10, 20) = max(14, 20) = 20.0 mm."""
        result = min_eccentricity(l_unsupported_mm=2000, D_mm=300)
        assert result == pytest.approx(20.0, abs=0.01)

    def test_just_above_floor(self):
        """l=5500, D=300: max(11+10, 20) = max(21, 20) = 21.0 mm."""
        result = min_eccentricity(l_unsupported_mm=5500, D_mm=300)
        assert result == pytest.approx(21.0, abs=0.01)

    def test_large_column_large_span(self):
        """l=10000, D=600: max(20+20, 20) = 40.0 mm."""
        result = min_eccentricity(l_unsupported_mm=10000, D_mm=600)
        assert result == pytest.approx(40.0, abs=0.01)

    # ----- 2c. Edge-case / error tests -----

    def test_l_zero_raises(self):
        """l_unsupported_mm = 0 -> DimensionError."""
        with pytest.raises(DimensionError):
            min_eccentricity(l_unsupported_mm=0, D_mm=300)

    def test_l_negative_raises(self):
        """l_unsupported_mm < 0 -> DimensionError."""
        with pytest.raises(DimensionError):
            min_eccentricity(l_unsupported_mm=-1000, D_mm=300)

    def test_D_zero_raises(self):
        """D_mm = 0 -> DimensionError."""
        with pytest.raises(DimensionError):
            min_eccentricity(l_unsupported_mm=3000, D_mm=0)

    def test_D_negative_raises(self):
        """D_mm < 0 -> DimensionError."""
        with pytest.raises(DimensionError):
            min_eccentricity(l_unsupported_mm=3000, D_mm=-100)

    def test_very_small_inputs(self):
        """l=1, D=1: max(0.002+0.033, 20) = 20 mm (floor governs)."""
        result = min_eccentricity(l_unsupported_mm=1, D_mm=1)
        assert result == pytest.approx(20.0, abs=0.01)

    def test_very_large_inputs(self):
        """l=100000, D=2000: max(200+66.67, 20) = 266.67 mm."""
        result = min_eccentricity(l_unsupported_mm=100000, D_mm=2000)
        assert result == pytest.approx(266.667, abs=0.01)

    # ----- 2d. SP:16 benchmark tests -----

    @pytest.mark.parametrize(
        "l_mm, D_mm, expected_mm",
        [
            (3000, 400, 20.0),
            (6000, 300, 22.0),
            (4500, 500, 25.667),
            (2400, 230, 20.0),
            (10000, 600, 40.0),
        ],
        ids=[
            "SP16-floor-governs",
            "SP16-calc-governs-22mm",
            "SP16-calc-governs-25.67mm",
            "SP16-floor-governs-slim",
            "SP16-large-column-40mm",
        ],
    )
    def test_sp16_benchmarks(self, l_mm, D_mm, expected_mm):
        """SP:16 benchmark: minimum eccentricity.

        Source: IS 456:2000, Cl 25.4
        Tolerance: +/-0.1%
        """
        result = min_eccentricity(l_unsupported_mm=l_mm, D_mm=D_mm)
        assert result == pytest.approx(expected_mm, rel=0.001)

    # ----- 2e. Property-based tests (Hypothesis) -----

    @given(
        l=st.floats(min_value=1, max_value=100_000),
        D=st.floats(min_value=1, max_value=5000),
    )
    @settings(max_examples=200)
    def test_always_at_least_20mm(self, l, D):
        """Property: e_min is always >= 20 mm per IS 456 Cl 25.4."""
        result = min_eccentricity(l_unsupported_mm=l, D_mm=D)
        assert result >= 20.0

    @given(
        D=st.floats(min_value=100, max_value=2000),
        l1=st.floats(min_value=1, max_value=50_000),
    )
    @settings(max_examples=200)
    def test_monotonically_increases_with_l(self, D, l1):
        """Monotonicity: e_min non-decreasing with l (D fixed)."""
        l2 = l1 + 500
        e1 = min_eccentricity(l_unsupported_mm=l1, D_mm=D)
        e2 = min_eccentricity(l_unsupported_mm=l2, D_mm=D)
        assert e2 >= e1

    @given(
        l=st.floats(min_value=1, max_value=50_000),
        D1=st.floats(min_value=100, max_value=2000),
    )
    @settings(max_examples=200)
    def test_monotonically_increases_with_D(self, l, D1):
        """Monotonicity: e_min non-decreasing with D (l fixed)."""
        D2 = D1 + 100
        e1 = min_eccentricity(l_unsupported_mm=l, D_mm=D1)
        e2 = min_eccentricity(l_unsupported_mm=l, D_mm=D2)
        assert e2 >= e1

    @given(
        l=st.floats(min_value=1, max_value=100_000),
        D=st.floats(min_value=1, max_value=5000),
    )
    @settings(max_examples=100)
    def test_matches_formula(self, l, D):
        """Property: result matches max(l/500 + D/30, 20)."""
        result = min_eccentricity(l_unsupported_mm=l, D_mm=D)
        expected = max(l / 500.0 + D / 30.0, 20.0)
        assert result == pytest.approx(expected, rel=1e-9)


# =============================================================================
# 3. short_axial_capacity -- IS 456 Cl 39.3
# =============================================================================


class TestShortAxialCapacity:
    """Tests for short column axial capacity per IS 456 Cl 39.3.

    IS 456 Cl 39.3: Pu = 0.4 * fck * Ac + 0.67 * fy * Asc
    where Ac = Ag - Asc.
    Result is in kN.
    """

    # ----- 3a. Unit tests (happy path) -----

    def test_typical_300x400_column(self):
        """300x400 column, M25/Fe415, 3-No.32 bars."""
        Asc = 3 * math.pi / 4 * 32**2
        result = short_axial_capacity(fck=25, fy=415, Ag_mm2=120000, Asc_mm2=Asc)
        assert isinstance(result, ColumnAxialResult)
        assert result.Pu_kN > 0
        assert result.classification == ColumnClassification.SHORT

    def test_typical_300x300_column(self):
        """300x300 column, M20/Fe415, 4-No.20 bars."""
        Asc = 4 * math.pi / 4 * 20**2
        result = short_axial_capacity(fck=20, fy=415, Ag_mm2=90000, Asc_mm2=Asc)
        assert isinstance(result, ColumnAxialResult)
        assert result.Pu_kN > 0
        assert result.fck == 20
        assert result.fy == 415

    def test_result_fields(self):
        """Verify all result fields are populated correctly."""
        result = short_axial_capacity(fck=25, fy=415, Ag_mm2=90000, Asc_mm2=1800)
        assert result.fck == 25
        assert result.fy == 415
        assert result.Ag_mm2 == 90000
        assert result.Asc_mm2 == 1800
        assert result.Ac_mm2 == pytest.approx(90000 - 1800)
        assert result.steel_ratio == pytest.approx(1800 / 90000)
        assert result.classification == ColumnClassification.SHORT
        assert result.is_safe is True

    # ----- 3b. Boundary tests -----

    def test_zero_steel(self):
        """Degenerate: Asc = 0 (pure concrete).

        Pu = 0.4 * 25 * 90000 = 900000 N = 900 kN.
        Should produce warning about steel ratio below minimum.
        """
        result = short_axial_capacity(fck=25, fy=415, Ag_mm2=90000, Asc_mm2=0)
        assert result.Pu_kN == pytest.approx(900.0, rel=0.001)
        assert result.steel_ratio == 0.0
        assert any("below minimum" in w for w in result.warnings)

    def test_steel_at_minimum_ratio(self):
        """Asc/Ag = 0.8% -- at minimum limit."""
        Ag = 90000
        Asc = 0.008 * Ag
        result = short_axial_capacity(fck=25, fy=415, Ag_mm2=Ag, Asc_mm2=Asc)
        assert result.steel_ratio == pytest.approx(0.008, rel=1e-9)

    def test_steel_at_maximum_ratio(self):
        """Asc/Ag = 4% -- at maximum limit."""
        Ag = 90000
        Asc = 0.04 * Ag
        result = short_axial_capacity(fck=25, fy=415, Ag_mm2=Ag, Asc_mm2=Asc)
        assert result.steel_ratio == pytest.approx(0.04, rel=1e-9)

    def test_steel_above_maximum_ratio(self):
        """Asc/Ag = 5% -- above maximum, should warn."""
        Ag = 90000
        Asc = 0.05 * Ag
        result = short_axial_capacity(fck=25, fy=415, Ag_mm2=Ag, Asc_mm2=Asc)
        assert any("exceeds maximum" in w for w in result.warnings)

    def test_steel_below_minimum_ratio(self):
        """Asc/Ag = 0.5% -- below minimum, should warn."""
        Ag = 90000
        Asc = 0.005 * Ag
        result = short_axial_capacity(fck=25, fy=415, Ag_mm2=Ag, Asc_mm2=Asc)
        assert any("below minimum" in w for w in result.warnings)

    def test_steel_equals_gross_area(self):
        """Degenerate: Asc = Ag -> Ac = 0 (all steel, no concrete).

        Pu = 0.67 * 415 * 90000 / 1000 kN.
        """
        result = short_axial_capacity(fck=25, fy=415, Ag_mm2=90000, Asc_mm2=90000)
        expected_Pu_kN = 0.67 * 415 * 90000 / 1000
        assert result.Pu_kN == pytest.approx(expected_Pu_kN, rel=0.001)
        assert result.Ac_mm2 == pytest.approx(0.0)

    # ----- 3c. Edge-case / error tests -----

    def test_fck_zero_raises(self):
        """fck = 0 -> MaterialError."""
        with pytest.raises(MaterialError):
            short_axial_capacity(fck=0, fy=415, Ag_mm2=90000, Asc_mm2=1800)

    def test_fck_negative_raises(self):
        """fck < 0 -> MaterialError."""
        with pytest.raises(MaterialError):
            short_axial_capacity(fck=-25, fy=415, Ag_mm2=90000, Asc_mm2=1800)

    def test_fy_zero_raises(self):
        """fy = 0 -> MaterialError."""
        with pytest.raises(MaterialError):
            short_axial_capacity(fck=25, fy=0, Ag_mm2=90000, Asc_mm2=1800)

    def test_fy_negative_raises(self):
        """fy < 0 -> MaterialError."""
        with pytest.raises(MaterialError):
            short_axial_capacity(fck=25, fy=-415, Ag_mm2=90000, Asc_mm2=1800)

    def test_Ag_zero_raises(self):
        """Ag = 0 -> DimensionError."""
        with pytest.raises(DimensionError):
            short_axial_capacity(fck=25, fy=415, Ag_mm2=0, Asc_mm2=0)

    def test_Ag_negative_raises(self):
        """Ag < 0 -> DimensionError."""
        with pytest.raises(DimensionError):
            short_axial_capacity(fck=25, fy=415, Ag_mm2=-90000, Asc_mm2=0)

    def test_Asc_negative_raises(self):
        """Asc < 0 -> DimensionError."""
        with pytest.raises(DimensionError):
            short_axial_capacity(fck=25, fy=415, Ag_mm2=90000, Asc_mm2=-100)

    def test_Asc_exceeds_Ag_raises(self):
        """Asc > Ag -> DimensionError."""
        with pytest.raises(DimensionError):
            short_axial_capacity(fck=25, fy=415, Ag_mm2=90000, Asc_mm2=90001)

    def test_high_fck_warning(self):
        """fck > 60 -> warning about HPC outside IS 456 scope."""
        result = short_axial_capacity(fck=80, fy=415, Ag_mm2=90000, Asc_mm2=1800)
        assert any("exceeds IS 456 scope" in w for w in result.warnings)

    def test_fck_exactly_60_no_hpc_warning(self):
        """fck = 60 -> no HPC warning (within scope)."""
        result = short_axial_capacity(fck=60, fy=415, Ag_mm2=90000, Asc_mm2=1800)
        assert not any("exceeds IS 456 scope" in w for w in result.warnings)

    # ----- 3d. SP:16 benchmark tests (+/-0.1%) -----

    @pytest.mark.parametrize(
        "fck, fy, Ag_mm2, Asc_mm2, expected_Pu_kN",
        [
            (25, 415, 120000, 2412.74, 1846.64),
            (20, 415, 90000, 1256.64, 1059.41),
            (30, 500, 160000, 4825.49, 3478.63),
        ],
        ids=[
            "SP16-300x400-M25-Fe415",
            "SP16-300x300-M20-Fe415",
            "SP16-400x400-M30-Fe500",
        ],
    )
    def test_sp16_benchmarks(self, fck, fy, Ag_mm2, Asc_mm2, expected_Pu_kN):
        """SP:16 benchmark: short column axial capacity.

        Source: IS 456:2000, Cl 39.3 / SP:16 Design Aids, Chart 27
        Tolerance: +/-0.1%

        Benchmark 1: 300x400 M25/Fe415, 3-No.32 (Asc=2412.74)
            Pu = 0.4*25*(120000-2412.74) + 0.67*415*2412.74 = 1846.64 kN
        Benchmark 2: 300x300 M20/Fe415, 4-No.20 (Asc=1256.64)
            Pu = 0.4*20*(90000-1256.64) + 0.67*415*1256.64 = 1059.41 kN
        Benchmark 3: 400x400 M30/Fe500, 6-No.32 (Asc=4825.49)
            Pu = 0.4*30*(160000-4825.49) + 0.67*500*4825.49 = 3478.63 kN
        """
        result = short_axial_capacity(fck=fck, fy=fy, Ag_mm2=Ag_mm2, Asc_mm2=Asc_mm2)
        assert result.Pu_kN == pytest.approx(expected_Pu_kN, rel=0.001)

    # ----- 3e. Textbook verification tests -----

    def test_textbook_pure_concrete(self):
        """Textbook: pure concrete column (Asc=0).

        300x300, M25: Pu = 0.4 * 25 * 90000 = 900,000 N = 900 kN
        Source: Direct IS 456 Cl 39.3 formula
        """
        result = short_axial_capacity(fck=25, fy=415, Ag_mm2=90000, Asc_mm2=0)
        assert result.Pu_kN == pytest.approx(900.0, rel=0.001)

    def test_textbook_hand_calculation(self):
        """Textbook: 300x500 column, M25/Fe415, Asc=2000 mm2.

        Ac = 150000 - 2000 = 148000
        Concrete: 0.4 * 25 * 148000 = 1,480,000 N
        Steel: 0.67 * 415 * 2000 = 556,100 N
        Pu = 2,036,100 N = 2036.10 kN
        """
        result = short_axial_capacity(fck=25, fy=415, Ag_mm2=150000, Asc_mm2=2000)
        assert result.Pu_kN == pytest.approx(2036.10, rel=0.001)

    def test_textbook_m30_fe500(self):
        """Textbook: 400x400 column, M30/Fe500, Asc=3200 mm2.

        Ac = 160000 - 3200 = 156800
        Concrete: 0.4 * 30 * 156800 = 1,881,600 N
        Steel: 0.67 * 500 * 3200 = 1,072,000 N
        Pu = 2,953,600 N = 2953.60 kN
        """
        result = short_axial_capacity(fck=30, fy=500, Ag_mm2=160000, Asc_mm2=3200)
        assert result.Pu_kN == pytest.approx(2953.60, rel=0.001)

    # ----- 3f. Property-based tests (Hypothesis) -----

    @given(
        fck=st.sampled_from([20, 25, 30, 35, 40]),
        fy=st.sampled_from([415, 500]),
        Ag=st.floats(min_value=10000, max_value=500000),
        ratio=st.floats(min_value=0.001, max_value=0.04),
    )
    @settings(max_examples=200)
    def test_Pu_always_positive(self, fck, fy, Ag, ratio):
        """Property: Pu is always > 0 for valid inputs."""
        Asc = ratio * Ag
        result = short_axial_capacity(fck=fck, fy=fy, Ag_mm2=Ag, Asc_mm2=Asc)
        assert result.Pu_kN > 0

    @given(
        fy=st.sampled_from([415, 500]),
        Ag=st.floats(min_value=40000, max_value=300000),
        ratio=st.floats(min_value=0.01, max_value=0.03),
    )
    @settings(max_examples=200)
    def test_Pu_increases_with_fck(self, fy, Ag, ratio):
        """Monotonicity: higher fck -> higher Pu (fy, Ag, Asc constant)."""
        Asc = ratio * Ag
        r1 = short_axial_capacity(fck=25, fy=fy, Ag_mm2=Ag, Asc_mm2=Asc)
        r2 = short_axial_capacity(fck=30, fy=fy, Ag_mm2=Ag, Asc_mm2=Asc)
        assert r2.Pu_kN >= r1.Pu_kN

    @given(
        fck=st.sampled_from([20, 25, 30]),
        Ag=st.floats(min_value=40000, max_value=300000),
        ratio=st.floats(min_value=0.01, max_value=0.03),
    )
    @settings(max_examples=200)
    def test_Pu_increases_with_fy(self, fck, Ag, ratio):
        """Monotonicity: higher fy -> higher Pu (fck, Ag, Asc constant)."""
        Asc = ratio * Ag
        r1 = short_axial_capacity(fck=fck, fy=415, Ag_mm2=Ag, Asc_mm2=Asc)
        r2 = short_axial_capacity(fck=fck, fy=500, Ag_mm2=Ag, Asc_mm2=Asc)
        assert r2.Pu_kN >= r1.Pu_kN

    @given(
        fck=st.sampled_from([20, 25, 30]),
        fy=st.sampled_from([415, 500]),
        ratio=st.floats(min_value=0.01, max_value=0.03),
    )
    @settings(max_examples=200)
    def test_Pu_increases_with_Ag(self, fck, fy, ratio):
        """Monotonicity: higher Ag (same steel ratio) -> higher Pu."""
        Ag1 = 90000
        Ag2 = 160000
        r1 = short_axial_capacity(fck=fck, fy=fy, Ag_mm2=Ag1, Asc_mm2=ratio * Ag1)
        r2 = short_axial_capacity(fck=fck, fy=fy, Ag_mm2=Ag2, Asc_mm2=ratio * Ag2)
        assert r2.Pu_kN >= r1.Pu_kN

    @given(
        fck=st.sampled_from([20, 25, 30]),
        fy=st.sampled_from([415, 500]),
        Ag=st.floats(min_value=40000, max_value=300000),
        ratio=st.floats(min_value=0.005, max_value=0.04),
    )
    @settings(max_examples=200)
    def test_matches_formula(self, fck, fy, Ag, ratio):
        """Property: result matches Pu = 0.4*fck*Ac + 0.67*fy*Asc exactly."""
        Asc = ratio * Ag
        result = short_axial_capacity(fck=fck, fy=fy, Ag_mm2=Ag, Asc_mm2=Asc)
        Ac = Ag - Asc
        expected_kN = (0.4 * fck * Ac + 0.67 * fy * Asc) / 1000.0
        assert result.Pu_kN == pytest.approx(expected_kN, rel=1e-9)
