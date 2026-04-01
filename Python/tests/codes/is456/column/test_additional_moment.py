# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tests for IS 456 Cl 39.7.1 — Additional moment due to slenderness.

Function under test:
    - calculate_additional_moment (Cl. 39.7.1)

Formulae:
    eadd_x = lex² / (2000 × D)
    eadd_y = ley² / (2000 × b)
    Max = Pu × eadd_x / 1000  (kN·m)
    May = Pu × eadd_y / 1000  (kN·m)
    k = (Puz - Pu) / (Puz - Pb), clamped to [0, 1.0]
    Max_reduced = k × Max, May_reduced = k × May

Test types per function-quality-pipeline Step 4:
    1. Unit tests (happy path) — 5 tests
    2. Edge-case / boundary tests — 5 tests
    3. Degenerate / error tests — 4 tests
    4. Textbook benchmark tests (±1%) — 2 tests
    5. k-factor tests — 4 tests
    6. Hypothesis property-based tests — 4 tests
"""

from __future__ import annotations

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from structural_lib.codes.is456.column.slenderness import calculate_additional_moment
from structural_lib.core.data_types import AdditionalMomentResult
from structural_lib.core.errors import DimensionError

# ---------------------------------------------------------------------------
# Standard test section (reused across multiple test classes)
# M25, Fe415, 2400 mm² steel, d'=50mm
# ---------------------------------------------------------------------------
STD = {"fck": 25, "fy": 415, "Asc_mm2": 2400, "d_prime_mm": 50}


# =============================================================================
# 1. Unit Tests — Happy Path
# =============================================================================


class TestAdditionalMomentHappyPath:
    """Unit tests — happy path for calculate_additional_moment."""

    def test_standard_300x450_slender_both(self):
        """IS 456 Cl 39.7.1: 300×450, slender both axes.

        eadd_x = 6000² / (2000 × 450) = 36000000 / 900000 = 40.0 mm
        Max = 1500 × 40.0 / 1000 = 60.0 kN·m
        eadd_y = 4500² / (2000 × 300) = 20250000 / 600000 = 33.75 mm
        May = 1500 × 33.75 / 1000 = 50.625 kN·m
        """
        result = calculate_additional_moment(
            Pu_kN=1500,
            b_mm=300,
            D_mm=450,
            lex_mm=6000,
            ley_mm=4500,
            **STD,
        )
        assert isinstance(result, AdditionalMomentResult)
        assert result.eadd_x_mm == pytest.approx(40.0, rel=0.001)
        assert result.Max_kNm == pytest.approx(60.0, rel=0.001)
        assert result.eadd_y_mm == pytest.approx(33.75, rel=0.001)
        assert result.May_kNm == pytest.approx(50.625, rel=0.001)
        assert result.is_slender_x is True
        assert result.is_slender_y is True

    def test_square_400x400(self):
        """IS 456 Cl 39.7.1: 400×400, slender both axes (square section).

        eadd_x = eadd_y = 6000² / (2000 × 400) = 36000000 / 800000 = 45.0 mm
        Max = May = 800 × 45.0 / 1000 = 36.0 kN·m
        """
        result = calculate_additional_moment(
            Pu_kN=800,
            b_mm=400,
            D_mm=400,
            lex_mm=6000,
            ley_mm=6000,
            **STD,
        )
        assert result.eadd_x_mm == pytest.approx(45.0, rel=0.001)
        assert result.eadd_y_mm == pytest.approx(45.0, rel=0.001)
        assert result.Max_kNm == pytest.approx(36.0, rel=0.001)
        assert result.May_kNm == pytest.approx(36.0, rel=0.001)

    def test_rectangular_300x600(self):
        """IS 456 Cl 39.7.1: 300×600, slender both axes (deep rectangular).

        eadd_x = 9000² / (2000 × 600) = 81000000 / 1200000 = 67.5 mm
        Max = 1200 × 67.5 / 1000 = 81.0 kN·m
        eadd_y = 4500² / (2000 × 300) = 20250000 / 600000 = 33.75 mm
        May = 1200 × 33.75 / 1000 = 40.5 kN·m
        """
        result = calculate_additional_moment(
            Pu_kN=1200,
            b_mm=300,
            D_mm=600,
            lex_mm=9000,
            ley_mm=4500,
            **STD,
        )
        assert result.eadd_x_mm == pytest.approx(67.5, rel=0.001)
        assert result.Max_kNm == pytest.approx(81.0, rel=0.001)
        assert result.eadd_y_mm == pytest.approx(33.75, rel=0.001)
        assert result.May_kNm == pytest.approx(40.5, rel=0.001)

    def test_result_has_clause_ref(self):
        """IS 456 Cl 39.7.1: clause_ref field."""
        result = calculate_additional_moment(
            Pu_kN=1500,
            b_mm=300,
            D_mm=450,
            lex_mm=6000,
            ley_mm=4500,
            **STD,
        )
        assert result.clause_ref == "Cl. 39.7.1"

    def test_result_to_dict_and_summary(self):
        """Result has to_dict() and summary() methods."""
        result = calculate_additional_moment(
            Pu_kN=1500,
            b_mm=300,
            D_mm=450,
            lex_mm=6000,
            ley_mm=4500,
            **STD,
        )
        d = result.to_dict()
        assert isinstance(d, dict)
        assert "eadd_x_mm" in d
        assert "Max_kNm" in d
        assert "k" in d

        s = result.summary()
        assert isinstance(s, str)
        assert len(s) > 0


# =============================================================================
# 2. Edge Case Tests
# =============================================================================


class TestAdditionalMomentEdgeCases:
    """Edge cases and boundary conditions for slenderness additional moment."""

    def test_short_column_both_axes(self):
        """Short column both axes (lex/D < 12 and ley/b < 12) -> Ma = 0.

        lex/D = 4950/450 = 11 < 12 -> short
        ley/b = 3000/300 = 10 < 12 -> short
        """
        result = calculate_additional_moment(
            Pu_kN=1500,
            b_mm=300,
            D_mm=450,
            lex_mm=4950,  # lex/D = 4950/450 = 11
            ley_mm=3000,  # ley/b = 3000/300 = 10
            **STD,
        )
        assert result.is_slender_x is False
        assert result.is_slender_y is False
        assert result.Max_kNm == pytest.approx(0.0, abs=1e-9)
        assert result.May_kNm == pytest.approx(0.0, abs=1e-9)

    def test_boundary_le_d_exactly_12(self):
        """IS 456 Cl 25.1.2: lex/D = 12.0 exactly -> slender (strict <).

        lex = 12 × 450 = 5400 mm, lex/D = 12.0
        eadd_x = 5400² / (2000 × 450) = 29160000 / 900000 = 32.4 mm
        """
        result = calculate_additional_moment(
            Pu_kN=1000,
            b_mm=300,
            D_mm=450,
            lex_mm=5400,  # lex/D = 5400/450 = 12.0 exactly
            ley_mm=3000,  # ley/b = 10 -> short
            **STD,
        )
        assert result.is_slender_x is True
        assert result.eadd_x_mm == pytest.approx(32.4, rel=0.001)
        assert result.Max_kNm > 0.0

    def test_one_axis_slender_other_short(self):
        """Slender about x-axis only: lex/D = 15 (slender), ley/b = 10 (short).

        lex = 15 × 450 = 6750, ley = 10 × 300 = 3000
        eadd_x = 6750² / (2000 × 450) = 45562500 / 900000 = 50.625 mm
        Max = 1000 × 50.625 / 1000 = 50.625 kN·m
        May = 0 (short axis)
        """
        result = calculate_additional_moment(
            Pu_kN=1000,
            b_mm=300,
            D_mm=450,
            lex_mm=6750,  # lex/D = 15
            ley_mm=3000,  # ley/b = 10 (short)
            **STD,
        )
        assert result.is_slender_x is True
        assert result.is_slender_y is False
        assert result.Max_kNm > 0.0
        assert result.May_kNm == pytest.approx(0.0, abs=1e-9)

    def test_high_slenderness_le_d_50(self):
        """Very high slenderness ratio lex/D = 50 -> large additional moment.

        lex = 50 × 450 = 22500 mm
        eadd_x = 22500² / (2000 × 450) = 506250000 / 900000 = 562.5 mm
        """
        result = calculate_additional_moment(
            Pu_kN=500,
            b_mm=300,
            D_mm=450,
            lex_mm=22500,  # lex/D = 50
            ley_mm=3000,  # short
            **STD,
        )
        assert result.eadd_x_mm == pytest.approx(562.5, rel=0.001)
        assert result.slenderness_ratio_x == pytest.approx(50.0, rel=0.001)
        # Should have warning about approaching IS 456 limit
        assert any(
            "slenderness" in w.lower() or "limit" in w.lower() for w in result.warnings
        )

    def test_max_slenderness_le_d_60_warning(self):
        """lex/D = 60 exceeds IS 456 practical limit -> warning.

        IS 456 Cl 25.3.1: le/D should not exceed 60 for unbraced columns.
        """
        result = calculate_additional_moment(
            Pu_kN=500,
            b_mm=300,
            D_mm=450,
            lex_mm=27000,  # lex/D = 60
            ley_mm=3000,
            **STD,
        )
        assert result.slenderness_ratio_x == pytest.approx(60.0, rel=0.001)
        assert any(
            "slenderness" in w.lower() or "exceed" in w.lower() or "limit" in w.lower()
            for w in result.warnings
        )


# =============================================================================
# 3. Degenerate / Error Tests
# =============================================================================


class TestAdditionalMomentDegenerate:
    """Degenerate inputs and error handling."""

    def test_pu_zero_gives_zero_moment(self):
        """Degenerate: Pu=0 -> Max=0, May=0 (Ma is proportional to Pu).

        eadd is still computed, but Ma = Pu × eadd / 1000 = 0.
        """
        result = calculate_additional_moment(
            Pu_kN=0,
            b_mm=300,
            D_mm=450,
            lex_mm=6000,
            ley_mm=4500,
            **STD,
        )
        assert result.Max_kNm == pytest.approx(0.0, abs=1e-9)
        assert result.May_kNm == pytest.approx(0.0, abs=1e-9)
        assert result.Max_reduced_kNm == pytest.approx(0.0, abs=1e-9)
        assert result.May_reduced_kNm == pytest.approx(0.0, abs=1e-9)

    def test_negative_pu_raises(self):
        """Negative axial load -> DimensionError."""
        with pytest.raises(DimensionError):
            calculate_additional_moment(
                Pu_kN=-100,
                b_mm=300,
                D_mm=450,
                lex_mm=6000,
                ley_mm=4500,
                **STD,
            )

    def test_zero_d_raises(self):
        """D_mm = 0 -> DimensionError (division by zero in formula)."""
        with pytest.raises(DimensionError):
            calculate_additional_moment(
                Pu_kN=1000,
                b_mm=300,
                D_mm=0,
                lex_mm=6000,
                ley_mm=4500,
                **STD,
            )

    def test_zero_le_raises(self):
        """lex_mm = 0 -> DimensionError (invalid effective length)."""
        with pytest.raises(DimensionError):
            calculate_additional_moment(
                Pu_kN=1000,
                b_mm=300,
                D_mm=450,
                lex_mm=0,
                ley_mm=4500,
                **STD,
            )


# =============================================================================
# 4. Textbook Benchmarks (±1%)
# =============================================================================


class TestAdditionalMomentBenchmarks:
    """Textbook benchmark tests — verify against published worked examples."""

    def test_pillai_menon_slender(self):
        """Benchmark: Pillai & Menon, 3rd Ed.

        Section: 300×450, Pu=1500 kN, lex=7200 mm
        eadd_x = 7200² / (2000 × 450) = 51840000 / 900000 = 57.6 mm
        Max = 1500 × 57.6 / 1000 = 86.4 kN·m
        """
        result = calculate_additional_moment(
            Pu_kN=1500,
            b_mm=300,
            D_mm=450,
            lex_mm=7200,
            ley_mm=3000,  # short axis
            **STD,
        )
        assert result.eadd_x_mm == pytest.approx(57.6, rel=0.01)
        assert result.Max_kNm == pytest.approx(86.4, rel=0.01)

    def test_ramamrutham_long_col(self):
        """Benchmark: Ramamrutham, 17th Ed.

        Section: 300×400, Pu=800 kN, lex=6400 mm
        eadd_x = 6400² / (2000 × 400) = 40960000 / 800000 = 51.2 mm
        Max = 800 × 51.2 / 1000 = 40.96 kN·m
        """
        result = calculate_additional_moment(
            Pu_kN=800,
            b_mm=300,
            D_mm=400,
            lex_mm=6400,
            ley_mm=3000,  # short axis
            **STD,
        )
        assert result.eadd_x_mm == pytest.approx(51.2, rel=0.01)
        assert result.Max_kNm == pytest.approx(40.96, rel=0.01)


# =============================================================================
# 5. k-Factor Tests
# =============================================================================


class TestAdditionalMomentKFactor:
    """Tests for k-factor computation and reduced moment.

    k = (Puz - Pu) / (Puz - Pb), clamped to [0, 1.0]
    Puz = (0.45 × fck × Ac + 0.75 × fy × Asc) / 1000
    """

    def test_k_factor_below_one(self):
        """k < 1.0 when Pu is between Pb and Puz."""
        result = calculate_additional_moment(
            Pu_kN=1500,
            b_mm=300,
            D_mm=450,
            lex_mm=6000,
            ley_mm=4500,
            **STD,
        )
        assert (
            0.0 < result.k < 1.0
        ), f"Expected 0 < k < 1 for Pu between Pb and Puz, got k={result.k}"
        assert result.Max_reduced_kNm < result.Max_kNm
        assert result.May_reduced_kNm < result.May_kNm

    def test_k_factor_clamped_at_one(self):
        """k = 1.0 when Pu < Pb (tension-controlled, no reduction).

        Use very low Pu so Pu < Pb.
        """
        result = calculate_additional_moment(
            Pu_kN=50,  # Very low load — below balanced load Pb
            b_mm=300,
            D_mm=450,
            lex_mm=6000,
            ley_mm=4500,
            **STD,
        )
        assert result.k == pytest.approx(
            1.0, rel=0.001
        ), f"Expected k=1.0 (clamped) for Pu < Pb, got k={result.k}"
        # Reduced moments equal unreduced when k=1
        assert result.Max_reduced_kNm == pytest.approx(result.Max_kNm, rel=0.001)
        assert result.May_reduced_kNm == pytest.approx(result.May_kNm, rel=0.001)

    def test_k_factor_near_zero(self):
        """k near 0 when Pu is close to Puz.

        Puz = (0.45 × 25 × Ac + 0.75 × 415 × 2400) / 1000
        Ac = 300×450 - 2400 = 132600 mm²
        Puz = (0.45×25×132600 + 0.75×415×2400) / 1000
            = (1491750 + 747000) / 1000 = 2238.75 kN
        Use Pu very close to Puz.
        """
        result = calculate_additional_moment(
            Pu_kN=2200,  # Close to Puz = 2238.75 kN
            b_mm=300,
            D_mm=450,
            lex_mm=6000,
            ley_mm=4500,
            **STD,
        )
        assert (
            result.k < 0.1
        ), f"Expected k near 0 for Pu close to Puz, got k={result.k}"
        # Reduced moments should be near zero
        assert result.Max_reduced_kNm < result.Max_kNm * 0.1

    def test_reduced_moment_equals_k_times_ma(self):
        """Max_reduced = k × Max (exact relationship)."""
        result = calculate_additional_moment(
            Pu_kN=1200,
            b_mm=300,
            D_mm=450,
            lex_mm=6000,
            ley_mm=4500,
            **STD,
        )
        assert result.Max_reduced_kNm == pytest.approx(
            result.k * result.Max_kNm, rel=1e-9
        )
        assert result.May_reduced_kNm == pytest.approx(
            result.k * result.May_kNm, rel=1e-9
        )


# =============================================================================
# 6. Hypothesis Property-Based Tests
# =============================================================================


class TestAdditionalMomentProperties:
    """Hypothesis property-based tests for calculate_additional_moment."""

    @given(
        le=st.floats(min_value=5500, max_value=20000),
    )
    @settings(max_examples=50)
    def test_monotonicity_ma_with_le(self, le):  # noqa: N802
        """Monotonicity: Increasing lex -> increasing Max.

        Ma = Pu × le² / (2000 × D × 1000).
        Since Ma is proportional to le², Ma must strictly increase with le.
        """
        D = 450.0
        assume(le / D >= 12.0)  # Slender only
        assume((le + 500) / D >= 12.0)

        r1 = calculate_additional_moment(
            Pu_kN=1000,
            b_mm=300,
            D_mm=D,
            lex_mm=le,
            ley_mm=3000,
            **STD,
        )
        r2 = calculate_additional_moment(
            Pu_kN=1000,
            b_mm=300,
            D_mm=D,
            lex_mm=le + 500,
            ley_mm=3000,
            **STD,
        )
        assert r2.Max_kNm >= r1.Max_kNm, (
            f"Max should increase with le: le={le} -> Max={r1.Max_kNm}, "
            f"le={le+500} -> Max={r2.Max_kNm}"
        )

    @given(
        Pu=st.floats(min_value=100, max_value=2000),
    )
    @settings(max_examples=50)
    def test_monotonicity_ma_with_pu(self, Pu):  # noqa: N803
        """Monotonicity: Increasing Pu -> increasing Max (Ma proportional to Pu)."""
        r1 = calculate_additional_moment(
            Pu_kN=Pu,
            b_mm=300,
            D_mm=450,
            lex_mm=6000,
            ley_mm=4500,
            **STD,
        )
        r2 = calculate_additional_moment(
            Pu_kN=Pu + 100,
            b_mm=300,
            D_mm=450,
            lex_mm=6000,
            ley_mm=4500,
            **STD,
        )
        assert r2.Max_kNm >= r1.Max_kNm, (
            f"Max should increase with Pu: Pu={Pu} -> Max={r1.Max_kNm}, "
            f"Pu={Pu+100} -> Max={r2.Max_kNm}"
        )

    @given(
        Pu=st.floats(min_value=100, max_value=1500),
    )
    @settings(max_examples=50)
    def test_linearity_in_pu(self, Pu):  # noqa: N803
        """Linearity: Ma(2×Pu) == 2×Ma(Pu) — exact proportionality.

        Max = Pu × eadd / 1000, so Max is exactly linear in Pu.
        """
        r1 = calculate_additional_moment(
            Pu_kN=Pu,
            b_mm=300,
            D_mm=450,
            lex_mm=6000,
            ley_mm=4500,
            **STD,
        )
        r2 = calculate_additional_moment(
            Pu_kN=2 * Pu,
            b_mm=300,
            D_mm=450,
            lex_mm=6000,
            ley_mm=4500,
            **STD,
        )
        assert r2.Max_kNm == pytest.approx(2 * r1.Max_kNm, rel=1e-9), (
            f"Max should be linear in Pu: Ma({Pu})={r1.Max_kNm}, "
            f"Ma({2*Pu})={r2.Max_kNm}, expected {2*r1.Max_kNm}"
        )

    @given(
        le_factor=st.floats(min_value=1.0, max_value=3.0),
    )
    @settings(max_examples=50)
    def test_quadratic_in_slenderness(self, le_factor):
        """Quadratic: Ma(2×le) / Ma(le) == 4.0.

        eadd = le² / (2000 × D), so Ma is proportional to le².
        """
        le_base = 6000.0
        le1 = le_base * le_factor
        le2 = le_base * le_factor * 2.0
        D = 450.0

        assume(le1 / D >= 12.0)  # Both must be slender
        assume(le2 / D >= 12.0)

        r1 = calculate_additional_moment(
            Pu_kN=1000,
            b_mm=300,
            D_mm=D,
            lex_mm=le1,
            ley_mm=3000,
            **STD,
        )
        r2 = calculate_additional_moment(
            Pu_kN=1000,
            b_mm=300,
            D_mm=D,
            lex_mm=le2,
            ley_mm=3000,
            **STD,
        )
        if r1.Max_kNm > 0:
            ratio = r2.Max_kNm / r1.Max_kNm
            assert ratio == pytest.approx(
                4.0, rel=1e-6
            ), f"Ma should be quadratic in le: ratio={ratio}, expected 4.0"
