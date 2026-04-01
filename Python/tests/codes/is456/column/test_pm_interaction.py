# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tests for IS 456 Cl 39.5 — P-M interaction curve generation.

Function under test:
    - pm_interaction_curve (Cl. 39.5)

Test types per function-quality-pipeline Step 4:
    1. Unit tests (happy path) — 13 tests
    2. Edge-case / boundary tests — 5 tests
    3. Degenerate / error tests — 8 tests
    4. SP:16 benchmark tests (±0.5%) — 4 tests
    5. Cross-check / consistency tests — 4 tests
    6. Hypothesis property-based tests — 3 tests
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from structural_lib.codes.is456.column.axial import short_axial_capacity
from structural_lib.codes.is456.column.uniaxial import (
    _pm_envelope_point,
    pm_interaction_curve,
)
from structural_lib.core.data_types import PMInteractionResult
from structural_lib.core.errors import DimensionError, MaterialError

# ---------------------------------------------------------------------------
# Standard test section (reused across multiple test classes)
# 300x500mm, M25, Fe415, 2% steel, d'=50mm
# ---------------------------------------------------------------------------
STD = {
    "b_mm": 300.0,
    "D_mm": 500.0,
    "fck": 25.0,
    "fy": 415.0,
    "Asc_mm2": 3000.0,  # 2% of 300*500=150000 -> 3000 mm2
    "d_prime_mm": 50.0,
}


# =============================================================================
# 1. Unit Tests — Happy Path
# =============================================================================


class TestPMInteractionCurveUnit:
    """Unit tests — happy path for pm_interaction_curve."""

    def test_return_type(self):
        """Return type is PMInteractionResult."""
        result = pm_interaction_curve(**STD)
        assert isinstance(result, PMInteractionResult)

    def test_frozen_dataclass(self):
        """Result is frozen (immutable)."""
        result = pm_interaction_curve(**STD)
        with pytest.raises(AttributeError):
            result.Pu_0_kN = 999.0  # type: ignore[misc]

    def test_num_points_default(self):
        """Default n_points=50 gives 51 envelope points."""
        result = pm_interaction_curve(**STD)
        assert len(result.points) == 51

    def test_num_points_custom(self):
        """Custom n_points gives n_points+1 envelope points."""
        result = pm_interaction_curve(**STD, n_points=30)
        assert len(result.points) == 31

    def test_pu_0_positive(self):
        """Pu_0_kN (pure axial capacity) > 0."""
        result = pm_interaction_curve(**STD)
        assert result.Pu_0_kN > 0.0

    def test_mu_0_positive(self):
        """Mu_0_kNm (pure bending capacity) > 0."""
        result = pm_interaction_curve(**STD)
        assert result.Mu_0_kNm > 0.0

    def test_balanced_point_between_zero_and_pu0(self):
        """Balanced Pu_bal should be: 0 < Pu_bal < Pu_0."""
        result = pm_interaction_curve(**STD)
        assert result.Pu_bal_kN > 0.0
        assert result.Pu_bal_kN < result.Pu_0_kN

    def test_balanced_moment_positive(self):
        """Mu_bal_kNm should be > 0."""
        result = pm_interaction_curve(**STD)
        assert result.Mu_bal_kNm > 0.0

    def test_to_dict(self):
        """to_dict() returns valid dict with expected keys."""
        result = pm_interaction_curve(**STD)
        d = result.to_dict()
        assert isinstance(d, dict)
        assert "points" in d
        assert "Pu_0_kN" in d
        assert "Mu_0_kNm" in d
        assert "Pu_bal_kN" in d
        assert "warnings" in d
        assert isinstance(d["points"], list)
        assert len(d["points"]) == 51

    def test_to_dict_point_structure(self):
        """Each point in to_dict has Pu_kN and Mu_kNm keys."""
        result = pm_interaction_curve(**STD)
        d = result.to_dict()
        for pt in d["points"]:
            assert "Pu_kN" in pt
            assert "Mu_kNm" in pt

    def test_summary_string(self):
        """summary() returns string containing 'P-M Curve'."""
        result = pm_interaction_curve(**STD)
        s = result.summary()
        assert isinstance(s, str)
        assert "P-M Curve" in s

    def test_clause_ref(self):
        """Clause reference should be 'Cl. 39.5'."""
        result = pm_interaction_curve(**STD)
        assert result.clause_ref == "Cl. 39.5"

    def test_echoed_inputs(self):
        """Echoed inputs match what was passed."""
        result = pm_interaction_curve(**STD)
        assert result.fck == 25.0
        assert result.fy == 415.0
        assert result.b_mm == 300.0
        assert result.D_mm == 500.0
        assert result.Asc_mm2 == 3000.0
        assert result.d_prime_mm == 50.0

    def test_different_section(self):
        """Different section: 200x300, M30, Fe500, d'=40mm."""
        result = pm_interaction_curve(
            b_mm=200.0,
            D_mm=300.0,
            fck=30.0,
            fy=500.0,
            Asc_mm2=1200.0,
            d_prime_mm=40.0,
        )
        assert isinstance(result, PMInteractionResult)
        assert result.Pu_0_kN > 0.0
        assert result.Mu_0_kNm > 0.0


# =============================================================================
# 2. Edge Case Tests
# =============================================================================


class TestPMInteractionCurveEdge:
    """Edge cases and boundary conditions."""

    def test_minimum_steel_ratio(self):
        """~0.8% steel: Asc = 0.008 * b * D — valid curve."""
        asc_min = 0.008 * 300.0 * 500.0  # 1200 mm2
        result = pm_interaction_curve(
            b_mm=300.0,
            D_mm=500.0,
            fck=25.0,
            fy=415.0,
            Asc_mm2=asc_min,
            d_prime_mm=50.0,
        )
        assert isinstance(result, PMInteractionResult)
        assert result.Pu_0_kN > 0.0

    def test_maximum_steel_ratio(self):
        """4% steel: Asc = 0.04 * b * D — higher capacity than 2%."""
        asc_max = 0.04 * 300.0 * 500.0  # 6000 mm2
        result = pm_interaction_curve(
            b_mm=300.0,
            D_mm=500.0,
            fck=25.0,
            fy=415.0,
            Asc_mm2=asc_max,
            d_prime_mm=50.0,
        )
        assert isinstance(result, PMInteractionResult)
        result_std = pm_interaction_curve(**STD)
        assert result.Pu_0_kN > result_std.Pu_0_kN

    def test_coarse_points(self):
        """n_points=10 (coarse) — still valid curve."""
        result = pm_interaction_curve(**STD, n_points=10)
        assert len(result.points) == 11
        assert result.Pu_0_kN > 0.0
        assert result.Mu_0_kNm > 0.0

    def test_fine_points(self):
        """n_points=200 (fine) — more points, Pu_0 identical (analytical)."""
        result_coarse = pm_interaction_curve(**STD, n_points=20)
        result_fine = pm_interaction_curve(**STD, n_points=200)
        assert len(result_fine.points) == 201
        # Pu_0 is computed analytically, so must be identical
        assert result_fine.Pu_0_kN == pytest.approx(result_coarse.Pu_0_kN, rel=1e-10)

    def test_high_strength_concrete(self):
        """fck=80 N/mm2 — much higher capacity than M25."""
        result = pm_interaction_curve(
            b_mm=300.0,
            D_mm=500.0,
            fck=80.0,
            fy=415.0,
            Asc_mm2=3000.0,
            d_prime_mm=50.0,
        )
        assert result.Pu_0_kN > 0.0
        result_m25 = pm_interaction_curve(**STD)
        assert result.Pu_0_kN > result_m25.Pu_0_kN


# =============================================================================
# 3. Degenerate / Error Tests
# =============================================================================


class TestPMInteractionCurveErrors:
    """Degenerate inputs and error cases."""

    def test_b_mm_zero(self):
        """b_mm=0 -> DimensionError."""
        with pytest.raises(DimensionError):
            pm_interaction_curve(
                b_mm=0.0,
                D_mm=500.0,
                fck=25.0,
                fy=415.0,
                Asc_mm2=3000.0,
                d_prime_mm=50.0,
            )

    def test_b_mm_negative(self):
        """b_mm < 0 -> DimensionError."""
        with pytest.raises(DimensionError):
            pm_interaction_curve(
                b_mm=-100.0,
                D_mm=500.0,
                fck=25.0,
                fy=415.0,
                Asc_mm2=3000.0,
                d_prime_mm=50.0,
            )

    def test_d_mm_zero(self):
        """D_mm=0 -> DimensionError."""
        with pytest.raises(DimensionError):
            pm_interaction_curve(
                b_mm=300.0,
                D_mm=0.0,
                fck=25.0,
                fy=415.0,
                Asc_mm2=3000.0,
                d_prime_mm=50.0,
            )

    def test_fck_zero(self):
        """fck=0 -> MaterialError."""
        with pytest.raises(MaterialError):
            pm_interaction_curve(
                b_mm=300.0,
                D_mm=500.0,
                fck=0.0,
                fy=415.0,
                Asc_mm2=3000.0,
                d_prime_mm=50.0,
            )

    def test_fy_negative(self):
        """fy < 0 -> MaterialError."""
        with pytest.raises(MaterialError):
            pm_interaction_curve(
                b_mm=300.0,
                D_mm=500.0,
                fck=25.0,
                fy=-415.0,
                Asc_mm2=3000.0,
                d_prime_mm=50.0,
            )

    def test_d_prime_exceeds_half_d(self):
        """d_prime_mm >= D/2 -> DimensionError."""
        with pytest.raises(DimensionError):
            pm_interaction_curve(
                b_mm=300.0,
                D_mm=500.0,
                fck=25.0,
                fy=415.0,
                Asc_mm2=3000.0,
                d_prime_mm=250.0,
            )

    def test_n_points_too_small(self):
        """n_points < 10 -> DimensionError."""
        with pytest.raises(DimensionError):
            pm_interaction_curve(**STD, n_points=5)

    def test_asc_zero(self):
        """Asc_mm2=0 -> DimensionError."""
        with pytest.raises(DimensionError):
            pm_interaction_curve(
                b_mm=300.0,
                D_mm=500.0,
                fck=25.0,
                fy=415.0,
                Asc_mm2=0.0,
                d_prime_mm=50.0,
            )


# =============================================================================
# 4. SP:16 Benchmark Tests
# =============================================================================


class TestPMInteractionCurveBenchmark:
    """Benchmark tests against IS 456 / SP:16 values.

    Sources:
        IS 456:2000, Cl. 39.3 (pure axial formula)
        SP:16:1980, Table I (stress-block coefficients)
    """

    @pytest.mark.golden
    def test_pu_0_matches_cl_39_3(self):
        """GOLDEN: Pu_0 matches IS 456 Cl 39.3 formula.

        IS 456 Cl 39.3: Pu = 0.4 * fck * Ac + 0.67 * fy * Asc
        Section: 300x500, M25, Fe415, Asc=3000 mm2
        Ac = 150000 - 3000 = 147000 mm2
        Pu_0 = (0.4 * 25 * 147000 + 0.67 * 415 * 3000) / 1000
             = (1470000 + 834150) / 1000 = 2304.15 kN
        """
        result = pm_interaction_curve(**STD)
        expected_pu_0 = (0.4 * 25 * (150000 - 3000) + 0.67 * 415 * 3000) / 1000.0
        assert result.Pu_0_kN == pytest.approx(expected_pu_0, rel=0.005)

    @pytest.mark.golden
    def test_pu_0_cross_validates_with_axial(self):
        """GOLDEN: Pu_0 matches short_axial_capacity() within +/-0.1%.

        Source: IS 456:2000, Cl. 39.3
        Both functions implement the same formula, so results must match.
        """
        result = pm_interaction_curve(**STD)
        axial_result = short_axial_capacity(
            fck=25.0,
            fy=415.0,
            Ag_mm2=150000.0,
            Asc_mm2=3000.0,
        )
        assert result.Pu_0_kN == pytest.approx(axial_result.Pu_kN, rel=0.001)

    def test_balanced_point_reasonable_for_fe415(self):
        """Balanced Pu should be between 0 and Pu_0, moment > 100 kNm.

        IS 456 Cl 38.1: xu_bal/d_eff = 0.0035 / (0.0035 + fy/(1.15*Es))
        For Fe415: xu_bal/d_eff = 0.66, d_eff=450 -> xu_bal ~ 297 mm
        """
        result = pm_interaction_curve(**STD)
        assert 0 < result.Pu_bal_kN < result.Pu_0_kN
        assert result.Mu_bal_kNm > 100.0

    def test_larger_cover_reduces_balanced_moment(self):
        """SP:16: d'/D=0.15 (d'=75mm) -> less moment than d'/D=0.10.

        Larger d'/D means shorter lever arm, so Mu_bal decreases.
        """
        result_015 = pm_interaction_curve(
            b_mm=300.0,
            D_mm=500.0,
            fck=25.0,
            fy=415.0,
            Asc_mm2=3000.0,
            d_prime_mm=75.0,
        )
        result_010 = pm_interaction_curve(**STD)
        assert result_015.Mu_bal_kNm > 0.0
        assert result_015.Mu_bal_kNm < result_010.Mu_bal_kNm


# =============================================================================
# 5. Consistency Tests
# =============================================================================


class TestPMInteractionCurveConsistency:
    """Cross-check and consistency tests."""

    def test_all_moments_non_negative(self):
        """All moments should be non-negative (absolute values used)."""
        result = pm_interaction_curve(**STD)
        assert all(m >= 0 for _, m in result.points)

    def test_pu_increases_along_sweep(self):
        """Pu should generally increase from first to last point.

        The sweep goes from xu=0.01*D to xu=3*D. Low xu -> low Pu,
        high xu -> high Pu (entire section in compression).
        """
        result = pm_interaction_curve(**STD, n_points=100)
        first_pu = result.points[0][0]
        last_pu = result.points[-1][0]
        assert last_pu > first_pu

    def test_max_moment_near_balanced_region(self):
        """Max moment on curve should be close to Mu_bal.

        The balanced point typically has the highest moment.
        Allow 15% tolerance since the sweep may not hit exact balanced xu.
        """
        result = pm_interaction_curve(**STD, n_points=100)
        max_moment = max(m for _, m in result.points)
        assert result.Mu_bal_kNm == pytest.approx(max_moment, rel=0.15)

    def test_envelope_point_matches_balanced(self):
        """Direct _pm_envelope_point call matches result.Pu_bal, Mu_bal."""
        result = pm_interaction_curve(**STD, n_points=50)
        d_eff = 500.0 - 50.0
        e_s = 2e5
        xu_bal = d_eff * 0.0035 / (0.0035 + 415.0 / (1.15 * e_s))
        pu, mu = _pm_envelope_point(
            xu_bal,
            300.0,
            500.0,
            25.0,
            415.0,
            1500.0,
            50.0,
        )
        assert abs(mu) == pytest.approx(result.Mu_bal_kNm, rel=1e-6)
        assert pu == pytest.approx(result.Pu_bal_kN, rel=1e-6)


# =============================================================================
# 6. Hypothesis Property-Based Tests
# =============================================================================


class TestPMInteractionCurveHypothesis:
    """Property-based tests using Hypothesis."""

    @given(
        fck=st.sampled_from([20.0, 25.0, 30.0, 35.0, 40.0]),
        fy=st.sampled_from([250.0, 415.0, 500.0]),
        b=st.floats(min_value=200.0, max_value=800.0),
        D=st.floats(min_value=300.0, max_value=1000.0),
    )
    @settings(max_examples=30, deadline=None)
    def test_pu_0_and_mu_0_always_positive(self, fck, fy, b, D):
        """For any valid inputs: Pu_0 > 0 and Mu_0 > 0."""
        d_prime = 50.0
        if d_prime >= D / 2.0:
            return  # skip invalid geometry
        asc = 0.02 * b * D  # 2% steel
        result = pm_interaction_curve(
            b_mm=b,
            D_mm=D,
            fck=fck,
            fy=fy,
            Asc_mm2=asc,
            d_prime_mm=d_prime,
        )
        assert result.Pu_0_kN > 0.0
        assert result.Mu_0_kNm > 0.0

    @given(
        n=st.integers(min_value=10, max_value=150),
    )
    @settings(max_examples=15, deadline=None)
    def test_num_points_matches(self, n):
        """len(points) == n_points + 1 for any valid n_points."""
        result = pm_interaction_curve(**STD, n_points=n)
        assert len(result.points) == n + 1

    @given(
        fck=st.sampled_from([20.0, 25.0, 30.0, 40.0]),
        fy=st.sampled_from([250.0, 415.0, 500.0]),
    )
    @settings(max_examples=20, deadline=None)
    def test_pu_bal_less_than_pu_0(self, fck, fy):
        """Pu_bal < Pu_0 for any valid material combination."""
        result = pm_interaction_curve(
            b_mm=300.0,
            D_mm=500.0,
            fck=fck,
            fy=fy,
            Asc_mm2=3000.0,
            d_prime_mm=50.0,
        )
        assert result.Pu_bal_kN < result.Pu_0_kN
