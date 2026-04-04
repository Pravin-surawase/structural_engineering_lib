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
        """Default n_points=50 gives 51 or 52 envelope points.

        The extra point occurs when a (Pu_0, 0) cap point is appended
        because no swept point naturally coincides with Pu_0.
        """
        result = pm_interaction_curve(**STD)
        assert len(result.points) in (51, 52)

    def test_num_points_custom(self):
        """Custom n_points gives n_points+1 or n_points+2 points.

        +1 from the Pu_0 cap point appended when the last swept point
        doesn't coincide with (Pu_0, 0).
        """
        result = pm_interaction_curve(**STD, n_points=30)
        assert len(result.points) in (31, 32)

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
        assert len(d["points"]) in (51, 52)

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
        assert len(result.points) in (11, 12)
        assert result.Pu_0_kN > 0.0
        assert result.Mu_0_kNm > 0.0

    def test_fine_points(self):
        """n_points=200 (fine) — more points, Pu_0 identical (analytical)."""
        result_coarse = pm_interaction_curve(**STD, n_points=20)
        result_fine = pm_interaction_curve(**STD, n_points=200)
        assert len(result_fine.points) in (201, 202)
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
        """n_points < 10 -> ValueError."""
        with pytest.raises(ValueError):
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
        """Direct _pm_envelope_point call matches result.Pu_bal, Mu_bal.

        IS 456 Cl 38.1: xu_bal uses eps_sy = fy/(1.15*Es) + 0.002 for HYSD bars.
        """
        result = pm_interaction_curve(**STD, n_points=50)
        d_eff = 500.0 - 50.0
        e_s = 2e5
        # IS 456 Cl 38.1: HYSD bars (fy > 250) include 0.002 inelastic strain
        eps_sy = 415.0 / (1.15 * e_s) + 0.002
        xu_bal = d_eff * 0.0035 / (0.0035 + eps_sy)
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
        """len(points) in (n+1, n+2) for any valid n_points.

        n+2 when the Pu_0 cap point is appended because the last swept
        point doesn't naturally coincide with (Pu_0, 0).
        """
        result = pm_interaction_curve(**STD, n_points=n)
        assert len(result.points) in (n + 1, n + 2)

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


# =============================================================================
# 7. New Tests — Math Fix Validation
# =============================================================================


class TestPMInteractionMathFixes:
    """Tests validating the corrected math formulas.

    These tests verify:
    1. xu=D continuity (SP:16 Table I matches standard formula at boundary)
    2. xu_bal includes 0.002 inelastic strain for HYSD bars (IS 456 Cl 38.1)
    3. Pu_0 cap: no envelope point exceeds Pu_0 (IS 456 Cl 39.3)
    """

    def test_xu_d_continuity(self):
        """xu=D boundary: standard and SP:16 formulas give continuous results.

        At xu=D, the standard formula (xu <= D) and SP:16 Table I (xu > D)
        should produce Pu and Mu values within 1% of each other.
        IS 456 Cl 38.1 + SP:16 Table I continuity requirement.
        """
        D = 500.0
        delta = 0.01  # 0.01 mm offset from boundary
        Asc_half = 1500.0  # half of 3000

        pu_below, mu_below = _pm_envelope_point(
            xu=D - delta,
            b_mm=300.0,
            D_mm=D,
            fck=25.0,
            fy=415.0,
            Asc_half_mm2=Asc_half,
            d_prime_mm=50.0,
        )
        pu_above, mu_above = _pm_envelope_point(
            xu=D + delta,
            b_mm=300.0,
            D_mm=D,
            fck=25.0,
            fy=415.0,
            Asc_half_mm2=Asc_half,
            d_prime_mm=50.0,
        )

        # Pu and Mu should be within 1% at the xu=D boundary
        assert pu_below == pytest.approx(
            pu_above, rel=0.01
        ), f"Pu discontinuity at xu=D: below={pu_below:.2f}, above={pu_above:.2f}"
        assert abs(mu_below) == pytest.approx(
            abs(mu_above), rel=0.01
        ), f"Mu discontinuity at xu=D: below={mu_below:.2f}, above={mu_above:.2f}"

    def test_xu_bal_fe415_matches_is456(self):
        """xu_bal/d for Fe 415 ≈ 0.48 per IS 456 Cl 38.1.

        IS 456 Cl 38.1: For HYSD bars, yield strain includes 0.002
        inelastic component: eps_sy = fy/(1.15*Es) + 0.002
        For Fe 415: eps_sy = 415/(1.15*200000) + 0.002 = 0.003804
        xu_bal/d = 0.0035 / (0.0035 + 0.003804) = 0.479
        """
        Es = 2e5
        d_eff = 450.0  # D=500, d'=50
        eps_sy = 415.0 / (1.15 * Es) + 0.002  # HYSD inelastic strain
        xu_bal = d_eff * 0.0035 / (0.0035 + eps_sy)
        xu_bal_ratio = xu_bal / d_eff

        # IS 456 Table: xu_bal/d ≈ 0.48 for Fe 415 (with 0.002 inelastic)
        assert xu_bal_ratio == pytest.approx(
            0.48, abs=0.01
        ), f"xu_bal/d = {xu_bal_ratio:.4f}, expected ~0.48 for Fe 415"

        # Verify via pm_interaction_curve balanced point
        result = pm_interaction_curve(**STD)
        # Pu_bal should correspond to xu_bal ≈ 0.48*d
        assert result.Pu_bal_kN > 0
        assert result.Mu_bal_kNm > 0
        # The balanced point from the curve should match direct calculation
        pu_direct, mu_direct = _pm_envelope_point(
            xu_bal,
            300.0,
            500.0,
            25.0,
            415.0,
            1500.0,
            50.0,
        )
        assert pu_direct == pytest.approx(result.Pu_bal_kN, rel=1e-6)

    def test_xu_bal_fe250_no_inelastic_strain(self):
        """xu_bal for Fe 250 (mild steel) has NO 0.002 inelastic component.

        IS 456 Cl 38.1: Only HYSD bars (fy > 250) include inelastic strain.
        For Fe 250: eps_sy = 250/(1.15*200000) = 0.001087
        xu_bal/d = 0.0035 / (0.0035 + 0.001087) = 0.763
        """
        result = pm_interaction_curve(
            b_mm=300.0,
            D_mm=500.0,
            fck=25.0,
            fy=250.0,
            Asc_mm2=3000.0,
            d_prime_mm=50.0,
        )
        d_eff = 450.0
        Es = 2e5
        eps_sy_fe250 = 250.0 / (1.15 * Es)  # No 0.002 for mild steel
        xu_bal_expected = d_eff * 0.0035 / (0.0035 + eps_sy_fe250)

        pu_direct, _ = _pm_envelope_point(
            xu_bal_expected,
            300.0,
            500.0,
            25.0,
            250.0,
            1500.0,
            50.0,
        )
        assert pu_direct == pytest.approx(result.Pu_bal_kN, rel=1e-6)

    def test_pu_0_cap_no_point_exceeds_pu_0(self):
        """No envelope point should have Pu > Pu_0.

        IS 456 Cl 39.3: The maximum axial load on a compression member
        is limited by Pu_0 = 0.4*fck*Ac + 0.67*fy*Asc.
        Points exceeding this are capped to (Pu_0, 0).
        """
        result = pm_interaction_curve(**STD, n_points=100)
        for pu, _mu in result.points:
            assert (
                pu <= result.Pu_0_kN + 1e-6
            ), f"Envelope point Pu={pu:.2f} exceeds Pu_0={result.Pu_0_kN:.2f}"

    def test_pu_0_cap_last_point_is_pu_0(self):
        """Last envelope point should be (Pu_0, 0) — pure compression.

        The Pu_0 cap ensures the envelope terminates at the
        analytically computed Cl 39.3 pure axial capacity.
        """
        result = pm_interaction_curve(**STD)
        last_pu, last_mu = result.points[-1]
        assert last_pu == pytest.approx(result.Pu_0_kN, rel=1e-6)
        assert last_mu == pytest.approx(0.0, abs=1e-6)

    @given(
        fck=st.sampled_from([20.0, 25.0, 30.0, 40.0]),
        fy=st.sampled_from([250.0, 415.0, 500.0]),
    )
    @settings(max_examples=20, deadline=None)
    def test_pu_0_cap_holds_for_all_materials(self, fck, fy):
        """Property: no envelope point exceeds Pu_0 for any material combo."""
        result = pm_interaction_curve(
            b_mm=300.0,
            D_mm=500.0,
            fck=fck,
            fy=fy,
            Asc_mm2=3000.0,
            d_prime_mm=50.0,
        )
        for pu, _mu in result.points:
            assert pu <= result.Pu_0_kN + 1e-6
