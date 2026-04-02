# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for IS 456 Cl 39.7 long (slender) column design.

Tests cover:
- Short column bypass (both axes le/D < 12)
- Slender on single axis and both axes
- Braced vs unbraced initial moment calculation
- Design moment lower bound (>= M2)
- k-factor calculation and clamping
- Slenderness boundary conditions
- Input validation (DimensionError, MaterialError)
- Result structure (fields, to_dict, summary)
- Hand-calculated benchmark

References:
    IS 456:2000, Cl. 39.7, 39.7.1, 39.7.1.1, 25.1.2, 25.3.1
    SP:16:1980 Design Aids
"""

from __future__ import annotations

import pytest

from structural_lib.codes.is456.column.long_column import design_long_column
from structural_lib.core.data_types import (
    ColumnClassification,
    LongColumnResult,
)
from structural_lib.core.errors import DimensionError

# ============================================================================
# Common parameters for reuse
# ============================================================================
# 300×500mm, M25/Fe415, 2% steel, d'=50mm
_BASE = dict(
    b_mm=300,
    D_mm=500,
    fck=25,
    fy=415,
    Asc_mm2=3000,
    d_prime_mm=50,
)


# ============================================================================
# Unit tests — basic functionality
# ============================================================================
class TestShortColumnBypass:
    """Test 1: Both axes short (le/D < 12) — no additional moment."""

    def test_short_column_bypass(self):
        """IS 456 Cl 25.1.2: le/D < 12 on both axes → SHORT, no Ma.

        le_x/D = 3000/500 = 6.0 < 12 → SHORT
        le_y/b = 2400/300 = 8.0 < 12 → SHORT
        → eadd_x = eadd_y = 0, Max = May = 0
        """
        result = design_long_column(
            Pu_kN=1000,
            M1x_kNm=50,
            M2x_kNm=80,
            M1y_kNm=30,
            M2y_kNm=50,
            lex_mm=3000,
            ley_mm=2400,
            **_BASE,
        )
        assert isinstance(result, LongColumnResult)
        assert result.is_slender_x is False
        assert result.is_slender_y is False
        assert result.classification_x == ColumnClassification.SHORT
        assert result.classification_y == ColumnClassification.SHORT
        assert result.eadd_x_mm == pytest.approx(0.0)
        assert result.eadd_y_mm == pytest.approx(0.0)
        assert result.Max_kNm == pytest.approx(0.0)
        assert result.May_kNm == pytest.approx(0.0)
        assert any("short" in w.lower() for w in result.warnings)


class TestSlenderSingleAxis:
    """Tests 2-3: Slender on one axis only."""

    def test_slender_x_only(self):
        """IS 456 Cl 39.7: le_x/D = 6000/500 = 12.0 → SLENDER on x.
        le_y/b = 3000/300 = 10.0 → SHORT on y.
        → eadd_x > 0, eadd_y = 0, Max > 0, May = 0.
        """
        result = design_long_column(
            Pu_kN=1200,
            M1x_kNm=50,
            M2x_kNm=100,
            M1y_kNm=30,
            M2y_kNm=60,
            lex_mm=6000,
            ley_mm=3000,
            **_BASE,
        )
        assert result.is_slender_x is True
        assert result.is_slender_y is False
        assert result.eadd_x_mm > 0
        assert result.eadd_y_mm == pytest.approx(0.0)
        assert result.Max_kNm > 0
        assert result.May_kNm == pytest.approx(0.0)

    def test_slender_y_only(self):
        """IS 456 Cl 39.7: le_x/D = 5500/500 = 11.0 → SHORT on x.
        le_y/b = 3600/300 = 12.0 → SLENDER on y.
        → eadd_x = 0, eadd_y > 0, Max = 0, May > 0.
        """
        result = design_long_column(
            Pu_kN=1200,
            M1x_kNm=50,
            M2x_kNm=100,
            M1y_kNm=30,
            M2y_kNm=60,
            lex_mm=5500,
            ley_mm=3600,
            **_BASE,
        )
        assert result.is_slender_x is False
        assert result.is_slender_y is True
        assert result.eadd_x_mm == pytest.approx(0.0)
        assert result.eadd_y_mm > 0
        assert result.Max_kNm == pytest.approx(0.0)
        assert result.May_kNm > 0


class TestSlenderBothAxes:
    """Test 4: Slender on both axes with biaxial check."""

    def test_slender_both_axes(self):
        """IS 456 Cl 39.7: Slender on both axes.
        le_x/D = 7000/500 = 14.0 → SLENDER on x.
        le_y/b = 4200/300 = 14.0 → SLENDER on y.
        → eadd_x > 0, eadd_y > 0, biaxial governing check expected.
        """
        result = design_long_column(
            Pu_kN=800,
            M1x_kNm=50,
            M2x_kNm=100,
            M1y_kNm=30,
            M2y_kNm=60,
            lex_mm=7000,
            ley_mm=4200,
            **_BASE,
        )
        assert result.is_slender_x is True
        assert result.is_slender_y is True
        assert result.eadd_x_mm > 0
        assert result.eadd_y_mm > 0
        assert result.Max_kNm > 0
        assert result.May_kNm > 0
        assert result.governing_check == "biaxial"


class TestInitialMomentBraced:
    """Test 5: Braced column initial moment calculation.

    IS 456 Cl 39.7.1 (braced): Mi = max(0.4*M1 + 0.6*M2, 0.4*M2)
    """

    def test_braced_initial_moment(self):
        """IS 456 Cl 39.7.1: braced single curvature.
        M1x=50, M2x=100:
        Mi_x = max(0.4×50 + 0.6×100, 0.4×100) = max(80, 40) = 80 kNm
        Verify Mux_design >= Mi_x + Ma_reduced (which >= M2x=100).
        """
        result = design_long_column(
            Pu_kN=1000,
            M1x_kNm=50,
            M2x_kNm=100,
            M1y_kNm=0,
            M2y_kNm=0,
            lex_mm=6500,
            ley_mm=2000,
            braced=True,
            **_BASE,
        )
        assert result.braced is True
        # Design moment must be at least M2x
        assert result.Mux_design_kNm >= 100.0


class TestInitialMomentUnbraced:
    """Test 6: Unbraced column — Mi = M2."""

    def test_unbraced_initial_moment(self):
        """IS 456 Cl 39.7.1 (unbraced): Mi = M2.
        Unbraced column: Mux_design >= M2x + Ma_reduced >= M2x.
        """
        result = design_long_column(
            Pu_kN=1000,
            M1x_kNm=50,
            M2x_kNm=100,
            M1y_kNm=0,
            M2y_kNm=0,
            lex_mm=6500,
            ley_mm=2000,
            braced=False,
            **_BASE,
        )
        assert result.braced is False
        # Unbraced: Mi_x = M2x = 100, so Mux_design >= 100 + Ma_reduced
        assert result.Mux_design_kNm >= 100.0


class TestDesignMomentLowerBound:
    """Test 7: M_design >= M2 always (lower bound)."""

    def test_design_moment_lower_bound(self):
        """IS 456 Cl 39.7: Lower bound — M_design >= M2.
        Even when Mi + Ma_reduced < M2, M_design is clamped to M2.
        """
        result = design_long_column(
            Pu_kN=500,
            M1x_kNm=-80,  # Double curvature → Mi may be small
            M2x_kNm=120,
            M1y_kNm=-50,
            M2y_kNm=80,
            lex_mm=6000,
            ley_mm=3600,
            braced=True,
            **_BASE,
        )
        # IS 456 Cl 39.7: M_design >= M2 always
        assert result.Mux_design_kNm >= 120.0
        assert result.Muy_design_kNm >= 80.0


class TestPureAxialSlender:
    """Test 8: Pu > 0, all moments zero → governed by Ma."""

    def test_pure_axial_slender(self):
        """IS 456 Cl 39.7: Slender column with no end moments.
        Ma = Pu × eadd > 0 when slender.
        """
        result = design_long_column(
            Pu_kN=1200,
            M1x_kNm=0,
            M2x_kNm=0,
            M1y_kNm=0,
            M2y_kNm=0,
            lex_mm=7000,
            ley_mm=4200,
            **_BASE,
        )
        # Additional moment should be the governing source
        assert result.Max_kNm > 0
        assert result.May_kNm > 0
        # Design moment >= 0 (the M2 lower bound is 0 here)
        assert result.Mux_design_kNm >= 0
        assert result.Muy_design_kNm >= 0


class TestKFactor:
    """Test 9: k-factor stays in [0, 1]."""

    def test_k_factor_clamped(self):
        """IS 456 Cl 39.7.1.1: k = (Puz - Pu) / (Puz - Pb) ∈ [0, 1]."""
        result = design_long_column(
            Pu_kN=800,
            M1x_kNm=50,
            M2x_kNm=100,
            M1y_kNm=30,
            M2y_kNm=60,
            lex_mm=7000,
            ley_mm=4200,
            **_BASE,
        )
        assert 0.0 <= result.k <= 1.0


# ============================================================================
# Edge cases
# ============================================================================
class TestSlendernessBoundary:
    """Tests 10-11: le/D boundary at 12."""

    def test_slenderness_boundary_11_99(self):
        """IS 456 Cl 25.1.2: le/D = 5995/500 ≈ 11.99 → SHORT (< 12)."""
        result = design_long_column(
            Pu_kN=1000,
            M1x_kNm=50,
            M2x_kNm=80,
            M1y_kNm=30,
            M2y_kNm=50,
            lex_mm=5995,  # 5995/500 = 11.99 < 12
            ley_mm=2000,
            **_BASE,
        )
        assert result.is_slender_x is False
        assert result.classification_x == ColumnClassification.SHORT
        assert result.eadd_x_mm == pytest.approx(0.0)

    def test_slenderness_boundary_12_0(self):
        """IS 456 Cl 25.1.2: le/D = 6000/500 = 12.0 → SLENDER (>= 12)."""
        result = design_long_column(
            Pu_kN=1000,
            M1x_kNm=50,
            M2x_kNm=80,
            M1y_kNm=30,
            M2y_kNm=50,
            lex_mm=6000,  # 6000/500 = 12.0 >= 12
            ley_mm=2000,
            **_BASE,
        )
        assert result.is_slender_x is True
        assert result.classification_x == ColumnClassification.SLENDER
        assert result.eadd_x_mm > 0


class TestPuExceedsPuz:
    """Test 12: Pu > Puz → k=0, unsafe warning."""

    def test_pu_exceeds_puz(self):
        """IS 456 Cl 39.7.1.1: When Pu > Puz, k set to 0.
        Use a very high Pu and low cross-section.
        Puz for 300×500 M25/Fe415 Asc=3000 ≈ 2231 kN.
        """
        result = design_long_column(
            Pu_kN=3000,  # Exceeds Puz
            M1x_kNm=50,
            M2x_kNm=100,
            M1y_kNm=30,
            M2y_kNm=60,
            lex_mm=7000,
            ley_mm=4200,
            **_BASE,
        )
        assert result.k == pytest.approx(0.0)
        assert any(
            "exceeds" in w.lower() or "overloaded" in w.lower() for w in result.warnings
        )


class TestPuZeroNoAdditionalMoment:
    """Test 13: Pu=0 → Ma=0 (no additional moment regardless of slenderness)."""

    def test_pu_zero_no_additional_moment(self):
        """IS 456 Cl 39.7.1: Ma = Pu × eadd = 0 × eadd = 0."""
        result = design_long_column(
            Pu_kN=0,
            M1x_kNm=50,
            M2x_kNm=100,
            M1y_kNm=30,
            M2y_kNm=60,
            lex_mm=7000,
            ley_mm=4200,
            **_BASE,
        )
        # eadd > 0 because column IS slender, but Ma = 0 × eadd = 0
        assert result.Max_kNm == pytest.approx(0.0)
        assert result.May_kNm == pytest.approx(0.0)


class TestDoubleCurvature:
    """Test 14: Opposite sign M1 and M2 (double curvature reduces Mi for braced)."""

    def test_double_curvature(self):
        """IS 456 Cl 39.7.1 (braced): double curvature bending.
        M1x = -60, M2x = 100 (opposite signs → double curvature).
        Mi_x = max(0.4×(-60) + 0.6×100, 0.4×100) = max(-24+60, 40) = max(36, 40) = 40
        vs single curvature M1x=+60: Mi_x = max(24+60, 40) = max(84, 40) = 84
        Double curvature yields lower Mi.
        """
        result_double = design_long_column(
            Pu_kN=800,
            M1x_kNm=-60,  # Opposite sign → double curvature
            M2x_kNm=100,
            M1y_kNm=0,
            M2y_kNm=0,
            lex_mm=7000,
            ley_mm=2000,
            braced=True,
            **_BASE,
        )
        result_single = design_long_column(
            Pu_kN=800,
            M1x_kNm=60,  # Same sign → single curvature
            M2x_kNm=100,
            M1y_kNm=0,
            M2y_kNm=0,
            lex_mm=7000,
            ley_mm=2000,
            braced=True,
            **_BASE,
        )
        # Double curvature has lower or equal design moment than single curvature
        # (but both are >= M2 = 100 due to lower bound)
        assert result_double.Mux_design_kNm >= 100.0
        assert result_single.Mux_design_kNm >= result_double.Mux_design_kNm


# ============================================================================
# Validation tests — invalid inputs
# ============================================================================
class TestInputValidation:
    """Tests 15-18: Input validation raises appropriate errors."""

    def test_negative_pu_raises(self):
        """IS 456 Cl 39.7: Pu must be >= 0 (compression)."""
        with pytest.raises(DimensionError, match="Pu_kN"):
            design_long_column(
                Pu_kN=-100,
                M1x_kNm=50,
                M2x_kNm=80,
                M1y_kNm=30,
                M2y_kNm=50,
                lex_mm=6000,
                ley_mm=3000,
                **_BASE,
            )

    def test_zero_b_raises(self):
        """IS 456 Cl 39.7: b_mm must be > 0."""
        with pytest.raises(DimensionError, match="b_mm"):
            design_long_column(
                Pu_kN=1000,
                M1x_kNm=50,
                M2x_kNm=80,
                M1y_kNm=30,
                M2y_kNm=50,
                b_mm=0,
                D_mm=500,
                lex_mm=6000,
                ley_mm=3000,
                fck=25,
                fy=415,
                Asc_mm2=3000,
                d_prime_mm=50,
            )

    def test_zero_D_raises(self):
        """IS 456 Cl 39.7: D_mm must be > 0."""
        with pytest.raises(DimensionError, match="D_mm"):
            design_long_column(
                Pu_kN=1000,
                M1x_kNm=50,
                M2x_kNm=80,
                M1y_kNm=30,
                M2y_kNm=50,
                b_mm=300,
                D_mm=0,
                lex_mm=6000,
                ley_mm=3000,
                fck=25,
                fy=415,
                Asc_mm2=3000,
                d_prime_mm=50,
            )

    def test_slenderness_exceeds_60_raises(self):
        """IS 456 Cl 25.3.1: le/D > 60 → DimensionError.
        le_x/D = 31000/500 = 62 > 60.
        """
        with pytest.raises(DimensionError, match="25.3.1"):
            design_long_column(
                Pu_kN=1000,
                M1x_kNm=50,
                M2x_kNm=80,
                M1y_kNm=30,
                M2y_kNm=50,
                lex_mm=31000,  # 31000/500 = 62 > 60
                ley_mm=3000,
                **_BASE,
            )

    def test_zero_steel_raises(self):
        """IS 456 Cl 39.7: Asc_mm2 must be > 0."""
        with pytest.raises(DimensionError, match="Asc_mm2"):
            design_long_column(
                Pu_kN=1000,
                M1x_kNm=50,
                M2x_kNm=80,
                M1y_kNm=30,
                M2y_kNm=50,
                b_mm=300,
                D_mm=500,
                lex_mm=6000,
                ley_mm=3000,
                fck=25,
                fy=415,
                Asc_mm2=0,
                d_prime_mm=50,
            )


# ============================================================================
# Result structure tests
# ============================================================================
class TestResultStructure:
    """Tests 19-21: Result fields, to_dict, summary."""

    @pytest.fixture
    def result(self) -> LongColumnResult:
        """Standard result for structure tests."""
        return design_long_column(
            Pu_kN=1000,
            M1x_kNm=50,
            M2x_kNm=100,
            M1y_kNm=30,
            M2y_kNm=60,
            lex_mm=7000,
            ley_mm=4200,
            **_BASE,
        )

    def test_result_fields(self, result: LongColumnResult):
        """Verify all LongColumnResult fields are present."""
        expected_fields = {
            "Pu_kN",
            "Mux_design_kNm",
            "Muy_design_kNm",
            "is_safe",
            "classification_x",
            "classification_y",
            "is_slender_x",
            "is_slender_y",
            "eadd_x_mm",
            "eadd_y_mm",
            "Max_kNm",
            "May_kNm",
            "k",
            "Max_reduced_kNm",
            "May_reduced_kNm",
            "interaction_ratio",
            "governing_check",
            "Puz_kN",
            "Pb_kN",
            "b_mm",
            "D_mm",
            "lex_mm",
            "ley_mm",
            "braced",
            "clause_ref",
            "warnings",
        }
        for field in expected_fields:
            assert hasattr(result, field), f"Missing field: {field}"

    def test_result_to_dict(self, result: LongColumnResult):
        """to_dict() must return a dict with all expected keys."""
        d = result.to_dict()
        assert isinstance(d, dict)
        assert "Pu_kN" in d
        assert "Mux_design_kNm" in d
        assert "is_safe" in d
        assert "interaction_ratio" in d
        assert "k" in d
        assert "governing_check" in d
        assert "clause_ref" in d
        # ColumnClassification should be serialized as string
        assert isinstance(d["classification_x"], str)

    def test_result_summary(self, result: LongColumnResult):
        """summary() must return a string with SAFE/UNSAFE and key values."""
        s = result.summary()
        assert isinstance(s, str)
        assert "SAFE" in s or "UNSAFE" in s
        assert "Pu=" in s
        assert "Mux_des=" in s
        assert "k=" in s


# ============================================================================
# Hand-calculated benchmark
# ============================================================================
class TestBenchmarkBracedSlender:
    """Test 22: Hand-calculated benchmark for braced slender column.

    300×500mm, M25/Fe415, 2% steel (3000mm²), d'=50mm
    le_x = 6000mm → le/D = 12.0 → SLENDER
    le_y = 3600mm → le/b = 12.0 → SLENDER
    Pu = 1200kN, M2x = 100kNm, M1x = 50kNm (braced, single curvature)
    M2y = 60kNm, M1y = 30kNm

    eadd_x = 6000² / (2000 × 500) = 36 mm
    Ma_x = 1200 × 36 / 1000 = 43.2 kNm

    eadd_y = 3600² / (2000 × 300) = 21.6 mm
    Ma_y = 1200 × 21.6 / 1000 = 25.92 kNm

    Braced Mi_x = max(0.4×50 + 0.6×100, 0.4×100) = max(80, 40) = 80 kNm
    Braced Mi_y = max(0.4×30 + 0.6×60, 0.4×60) = max(48, 24) = 48 kNm

    References:
        IS 456:2000, Cl. 39.7.1
    """

    def test_benchmark_braced_slender(self):
        """Verify against hand-calculated additional eccentricity and moment."""
        result = design_long_column(
            Pu_kN=1200,
            M1x_kNm=50,
            M2x_kNm=100,
            M1y_kNm=30,
            M2y_kNm=60,
            lex_mm=6000,
            ley_mm=3600,
            braced=True,
            **_BASE,
        )
        assert isinstance(result, LongColumnResult)

        # Both axes slender (le/D = 12.0, le/b = 12.0)
        assert result.is_slender_x is True
        assert result.is_slender_y is True

        # IS 456 Cl 39.7.1: eadd = le² / (2000 × D)
        # eadd_x = 6000² / (2000 × 500) = 36000000 / 1000000 = 36 mm
        assert result.eadd_x_mm == pytest.approx(36.0, rel=0.01)

        # eadd_y = 3600² / (2000 × 300) = 12960000 / 600000 = 21.6 mm
        assert result.eadd_y_mm == pytest.approx(21.6, rel=0.01)

        # IS 456 Cl 39.7.1: Ma = Pu × eadd (before k reduction)
        # Max = 1200 × 36 / 1000 = 43.2 kNm
        assert result.Max_kNm == pytest.approx(43.2, rel=0.01)

        # May = 1200 × 21.6 / 1000 = 25.92 kNm
        assert result.May_kNm == pytest.approx(25.92, rel=0.01)

        # k should be in [0, 1]
        assert 0.0 <= result.k <= 1.0

        # IS 456 Cl 39.7: M_design >= M2 (lower bound)
        assert result.Mux_design_kNm >= 100.0
        assert result.Muy_design_kNm >= 60.0

        # Design moment should be positive
        assert result.Mux_design_kNm > 0
        assert result.Muy_design_kNm > 0

        # Puz should be positive and reasonable
        assert result.Puz_kN > 0

        # Biaxial check since both axes have moments
        assert result.governing_check == "biaxial"
