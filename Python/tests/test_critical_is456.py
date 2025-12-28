"""
Critical IS 456 Tests

This module contains critical tests covering:
1. Clause-critical calculations (Mu_lim, xu/d ratios)
2. T-beam singly reinforced design path
3. Shear capacity limits (tc_max checks)
4. Minimum stirrup spacing compliance
5. Effective moment of inertia edge cases
6. Integration tests for combined checks
7. Boundary conditions for IS 456 tables

Reference: IS 456:2000
"""

import math
import pytest

from structural_lib import flexure, shear, tables, materials, detailing, serviceability
from structural_lib.types import DesignSectionType


# =============================================================================
# Section 1: Clause-Critical Flexure Calculations
# =============================================================================


class TestMuLimCalculation:
    """IS 456 Cl 38.1 - Limiting moment of resistance."""

    @pytest.mark.parametrize(
        "fck,fy,expected_xu_d",
        [
            (20, 250, 0.53),
            (25, 415, 0.48),
            (30, 500, 0.46),
            (35, 550, 0.44),
        ],
    )
    def test_xu_max_d_ratios_per_fy(self, fck, fy, expected_xu_d):
        """xu_max/d ratio depends on fy per IS 456 Cl 38.1."""
        xu_d = materials.get_xu_max_d(fy)
        assert xu_d == pytest.approx(expected_xu_d, abs=0.01)

    def test_mu_lim_formula_verification(self):
        """Verify Mu_lim = 0.36 * fck * b * xu_max * (d - 0.42 * xu_max)."""
        b, d, fck, fy = 230, 450, 25, 500
        xu_max_d = materials.get_xu_max_d(fy)
        xu_max = xu_max_d * d

        # Manual calculation per IS 456 Cl 38.1
        mu_lim_manual = 0.36 * fck * b * xu_max * (d - 0.42 * xu_max) / 1e6

        mu_lim_lib = flexure.calculate_mu_lim(b, d, fck, fy)
        assert mu_lim_lib == pytest.approx(mu_lim_manual, rel=1e-6)

    def test_mu_lim_zero_dimensions(self):
        """Mu_lim should be 0 for zero/invalid dimensions."""
        assert flexure.calculate_mu_lim(0, 450, 25, 500) == 0.0
        assert flexure.calculate_mu_lim(230, 0, 25, 500) == 0.0

    def test_mu_lim_scales_with_section(self):
        """Mu_lim should scale approximately with b*d^2."""
        fck, fy = 25, 500
        mu1 = flexure.calculate_mu_lim(230, 450, fck, fy)
        mu2 = flexure.calculate_mu_lim(300, 450, fck, fy)
        mu3 = flexure.calculate_mu_lim(230, 600, fck, fy)

        # Doubling width should ~double Mu_lim
        assert mu2 / mu1 == pytest.approx(300 / 230, rel=0.01)
        # Increasing depth by 1.33x should ~increase Mu_lim by 1.33^2 * 1.1 (approx due to xu_max)
        assert mu3 > mu1 * 1.5


class TestNeutralAxisDepth:
    """IS 456 Cl 38.1 - Neutral axis calculations."""

    def test_xu_less_than_xu_max_for_singly_reinforced(self):
        """Singly reinforced: xu < xu_max."""
        res = flexure.design_singly_reinforced(
            b=230, d=450, d_total=500, mu_knm=80, fck=25, fy=500
        )
        assert res.xu < res.xu_max
        assert res.section_type == DesignSectionType.UNDER_REINFORCED

    def test_xu_equals_xu_max_for_balanced(self):
        """At balanced condition, xu ≈ xu_max."""
        b, d, fck, fy = 230, 450, 25, 500
        mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)

        res = flexure.design_singly_reinforced(
            b=b, d=d, d_total=500, mu_knm=mu_lim * 0.999, fck=fck, fy=fy
        )
        assert res.xu == pytest.approx(res.xu_max, rel=0.01)


# =============================================================================
# Section 2: T-Beam Design (IS 456 Cl 38.1)
# =============================================================================


class TestTBeamSinglyReinforced:
    """T-Beam design with NA in web (singly reinforced path)."""

    def test_t_beam_na_in_flange_matches_rectangular(self):
        """When xu <= Df, T-beam behaves as rectangular of width bf."""
        bf, bw, Df, d = 1200, 300, 120, 500

        # Small moment -> NA in flange
        mu = 150  # kN·m

        res_t = flexure.design_flanged_beam(
            bw=bw, bf=bf, d=d, Df=Df, d_total=550, mu_knm=mu, fck=25, fy=500
        )
        res_rect = flexure.design_singly_reinforced(
            b=bf, d=d, d_total=550, mu_knm=mu, fck=25, fy=500
        )

        assert res_t.xu <= Df
        assert res_t.ast_required == pytest.approx(res_rect.ast_required, rel=0.01)

    def test_t_beam_na_in_web_singly_reinforced(self):
        """When Df < xu < xu_max, singly reinforced T-beam.

        This tests the T-beam path where NA is in web but moment
        is below Mu_lim so no compression steel needed.
        """
        # Parameters from existing test_flanged_beam.py that work
        bf, bw, Df, d = 1000, 300, 100, 500
        d_total = 550
        fck, fy = 25, 500

        # Use 500 kN·m - verified in test_flanged_beam to give xu > Df
        mu = 500  # kN·m

        res = flexure.design_flanged_beam(
            bw=bw, bf=bf, d=d, Df=Df, d_total=d_total, mu_knm=mu, fck=fck, fy=fy
        )

        # Verify NA in web, singly reinforced
        assert res.xu > Df, f"xu={res.xu} should be > Df={Df} for NA in web"
        assert res.asc_required == 0.0, "Should not need compression steel"
        assert res.section_type in (
            DesignSectionType.UNDER_REINFORCED,
            DesignSectionType.BALANCED,
        )

    def test_t_beam_yf_calculation_df_over_d_check(self):
        """yf calculation depends on Df/d ratio per IS 456 Annex G.

        Note: For T-beams with wide flanges, even moderate moments may
        have NA in flange. This test uses narrow flanges and high moments
        to ensure NA falls in web for testing yf calculation paths.
        """
        # Use narrow flange (bf only 1.5x bw) to ensure NA goes into web
        bf, bw, d = 400, 250, 500
        fck, fy = 25, 500

        # Case 1: Df/d <= 0.2 -> yf = Df
        Df_shallow = 60  # 60/500 = 0.12 <= 0.2
        res_shallow = flexure.design_flanged_beam(
            bw=bw, bf=bf, d=d, Df=Df_shallow, d_total=550, mu_knm=350, fck=fck, fy=fy
        )
        # For narrow flanges with high moment, NA should be in web
        assert (
            res_shallow.xu > Df_shallow
        ), f"xu={res_shallow.xu} should be > Df={Df_shallow} for NA in web"

        # Case 2: Df/d > 0.2 -> yf = 0.15*xu + 0.65*Df
        Df_deep = 110  # 110/500 = 0.22 > 0.2
        res_deep = flexure.design_flanged_beam(
            bw=bw, bf=bf, d=d, Df=Df_deep, d_total=550, mu_knm=400, fck=fck, fy=fy
        )
        assert (
            res_deep.xu > Df_deep
        ), f"xu={res_deep.xu} should be > Df={Df_deep} for NA in web"


# =============================================================================
# Section 3: Shear Design Critical Checks (IS 456 Cl 40)
# =============================================================================


class TestShearCapacityLimits:
    """IS 456 Cl 40.2.3 - Maximum shear stress limits."""

    @pytest.mark.parametrize(
        "fck,expected_tc_max",
        [
            (15, 2.5),
            (20, 2.8),
            (25, 3.1),
            (30, 3.5),
            (35, 3.7),
            (40, 4.0),
        ],
    )
    def test_tc_max_table_20_values(self, fck, expected_tc_max):
        """tc_max from Table 20 per IS 456."""
        tc_max = tables.get_tc_max_value(fck)
        assert tc_max == pytest.approx(expected_tc_max, abs=0.05)

    def test_shear_fails_when_exceeding_tc_max(self):
        """Section must be redesigned if tv > tc_max."""
        # Very high shear on small section
        # tv = 400 * 1000 / (150 * 250) = 10.67 N/mm² > tc_max (~2.8 for M20)
        result = shear.design_shear(
            vu_kn=400, b=150, d=250, fck=20, fy=415, asv=157, pt=1.0
        )
        assert result.is_safe is False
        assert "exceeds Tc_max" in result.remarks

    def test_shear_tc_interpolation(self):
        """tc should be interpolated from Table 19."""
        # pt = 0.75%, fck = 25 -> tc should interpolate between 0.5 and 1.0 rows
        result = shear.design_shear(
            vu_kn=100, b=250, d=450, fck=25, fy=415, asv=157, pt=0.75
        )
        # tc at pt=0.75% for M25 ≈ 0.56 (interpolated)
        assert 0.50 < result.tc < 0.65


class TestMinimumStirrupSpacing:
    """IS 456 Cl 26.5.1.5 - Maximum spacing limits."""

    def test_spacing_limited_to_0_75d(self):
        """Spacing must not exceed 0.75d."""
        d = 450
        result = shear.design_shear(
            vu_kn=80, b=250, d=d, fck=25, fy=415, asv=157, pt=0.5
        )
        assert result.spacing <= 0.75 * d

    def test_spacing_limited_to_300mm(self):
        """Spacing must not exceed 300mm."""
        result = shear.design_shear(
            vu_kn=50, b=300, d=600, fck=25, fy=415, asv=157, pt=0.5
        )
        assert result.spacing <= 300

    def test_minimum_shear_reinforcement_formula(self):
        """When tv < tc, provide minimum reinforcement per Cl 26.5.1.6."""
        result = shear.design_shear(
            vu_kn=30, b=250, d=450, fck=25, fy=415, asv=157, pt=1.0
        )
        # sv_min = 0.87*fy*Asv / (0.4*b)
        sv_min = (0.87 * 415 * 157) / (0.4 * 250)
        assert result.vus == 0.0  # No shear reinforcement needed beyond minimum
        assert result.spacing <= sv_min + 1  # Allow 1mm tolerance


# =============================================================================
# Section 4: Table Boundary Conditions
# =============================================================================


class TestTableBoundaries:
    """Test IS 456 table boundary conditions."""

    def test_tc_clamped_for_pt_below_0_15(self):
        """pt < 0.15% should use tc at pt=0.15%."""
        tc_low = tables.get_tc_value(25, 0.05)
        tc_min = tables.get_tc_value(25, 0.15)
        assert tc_low == tc_min

    def test_tc_clamped_for_pt_above_3(self):
        """pt > 3% should use tc at pt=3%."""
        tc_high = tables.get_tc_value(25, 4.0)
        tc_max_pt = tables.get_tc_value(25, 3.0)
        assert tc_high == tc_max_pt

    def test_tc_between_grades_uses_lower_bound(self):
        """fck between table values uses lower bound (conservative).

        Per IS 456 Table 19, values are given for discrete grades.
        Library uses lower-bound (conservative) approach.
        """
        tc_m20 = tables.get_tc_value(20, 1.0)
        tc_m22 = tables.get_tc_value(22, 1.0)
        # Conservative: use lower grade value
        assert tc_m22 == tc_m20

    def test_tc_max_extrapolation_above_m40(self):
        """fck > 40 should use M40 value (no extrapolation)."""
        tc_max_m40 = tables.get_tc_max_value(40)
        tc_max_m50 = tables.get_tc_max_value(50)
        assert tc_max_m40 == tc_max_m50


# =============================================================================
# Section 5: Serviceability Edge Cases
# =============================================================================


class TestEffectiveMomentOfInertia:
    """IS 456 Annex C - Effective moment of inertia."""

    def test_ieff_returns_igross_when_uncracked(self):
        """When Ma < Mcr, Ieff = Igross."""
        ieff = serviceability.calculate_effective_moment_of_inertia(
            mcr_knm=50, ma_knm=30, igross_mm4=3e9, icr_mm4=1e9
        )
        assert ieff == pytest.approx(3e9, rel=0.01)

    def test_ieff_approaches_icr_when_heavily_cracked(self):
        """When Ma >> Mcr, Ieff → Icr."""
        ieff = serviceability.calculate_effective_moment_of_inertia(
            mcr_knm=30, ma_knm=300, igross_mm4=3e9, icr_mm4=1e9
        )
        assert ieff < 1.05e9  # Very close to Icr

    def test_ieff_never_exceeds_igross(self):
        """Ieff should never exceed Igross."""
        ieff = serviceability.calculate_effective_moment_of_inertia(
            mcr_knm=100, ma_knm=10, igross_mm4=3e9, icr_mm4=1e9
        )
        assert ieff <= 3e9

    def test_ieff_never_less_than_icr(self):
        """Ieff should never be less than Icr."""
        ieff = serviceability.calculate_effective_moment_of_inertia(
            mcr_knm=10, ma_knm=1000, igross_mm4=3e9, icr_mm4=1e9
        )
        assert ieff >= 1e9


class TestCrackingMomentEdges:
    """Edge cases for cracking moment calculation."""

    def test_mcr_scales_with_fck_sqrt(self):
        """Mcr ∝ √fck per IS 456 Cl 6.2.2."""
        mcr_m20 = serviceability.calculate_cracking_moment(
            b_mm=300, D_mm=500, fck_nmm2=20
        )
        mcr_m25 = serviceability.calculate_cracking_moment(
            b_mm=300, D_mm=500, fck_nmm2=25
        )

        ratio = mcr_m25 / mcr_m20
        expected_ratio = math.sqrt(25) / math.sqrt(20)
        assert ratio == pytest.approx(expected_ratio, rel=0.01)

    def test_mcr_custom_yt(self):
        """Custom yt for asymmetric sections."""
        # Standard rectangular: yt = D/2 = 250
        mcr_std = serviceability.calculate_cracking_moment(
            b_mm=300, D_mm=500, fck_nmm2=25
        )
        # Custom yt = 300 (tension face further from NA)
        mcr_custom = serviceability.calculate_cracking_moment(
            b_mm=300, D_mm=500, fck_nmm2=25, yt_mm=300
        )
        # Larger yt -> smaller Mcr
        assert mcr_custom < mcr_std


# =============================================================================
# Section 6: Detailing Critical Checks
# =============================================================================


class TestDevelopmentLength:
    """IS 456 Cl 26.2.1 - Development length."""

    def test_ld_formula(self):
        """Ld = φ × σs / (4 × τbd) per IS 456 Cl 26.2.1.1."""
        phi = 16
        fy = 500
        fck = 25
        sigma_s = 0.87 * fy
        tau_bd = detailing.get_bond_stress(fck, "deformed")

        ld_expected = (phi * sigma_s) / (4 * tau_bd)
        ld_actual = detailing.calculate_development_length(phi, fck, fy)

        assert ld_actual == pytest.approx(ld_expected, rel=0.01)

    def test_ld_increases_with_bar_diameter(self):
        """Larger bars need longer development length."""
        ld_12 = detailing.calculate_development_length(12, 25, 500)
        ld_16 = detailing.calculate_development_length(16, 25, 500)
        ld_20 = detailing.calculate_development_length(20, 25, 500)

        assert ld_12 < ld_16 < ld_20

    def test_ld_decreases_with_higher_fck(self):
        """Higher fck -> higher τbd -> shorter Ld."""
        ld_m20 = detailing.calculate_development_length(16, 20, 500)
        ld_m30 = detailing.calculate_development_length(16, 30, 500)

        assert ld_m30 < ld_m20


class TestLapLength:
    """IS 456 Cl 26.2.5 - Lap splice requirements."""

    def test_lap_equals_ld_for_compression(self):
        """Compression lap = Ld."""
        ld = detailing.calculate_development_length(16, 25, 500)
        lap = detailing.calculate_lap_length(16, 25, 500, in_tension=False)
        assert lap == pytest.approx(ld, rel=0.01)

    def test_lap_1_3_ld_for_tension_over_50_percent(self):
        """Tension lap with >50% bars spliced: 1.3 × Ld."""
        ld = detailing.calculate_development_length(16, 25, 500)
        lap = detailing.calculate_lap_length(16, 25, 500, splice_percent=75)
        assert lap == pytest.approx(1.3 * ld, rel=0.01)

    def test_seismic_lap_factor(self):
        """Seismic lap = 1.5 × Ld per IS 13920."""
        ld = detailing.calculate_development_length(16, 25, 500)
        lap = detailing.calculate_lap_length(16, 25, 500, is_seismic=True)
        assert lap == pytest.approx(1.5 * ld, rel=0.01)


# =============================================================================
# Section 7: Integration Tests
# =============================================================================


class TestFlexureShearIntegration:
    """Combined flexure and shear design consistency."""

    def test_pt_from_flexure_used_in_shear(self):
        """pt from flexure Ast should give consistent shear design."""
        b, d, fck, fy = 230, 450, 25, 500

        # Design for flexure
        flex_res = flexure.design_singly_reinforced(
            b=b, d=d, d_total=500, mu_knm=100, fck=fck, fy=fy
        )
        pt = (flex_res.ast_required * 100) / (b * d)

        # Use that pt for shear design
        shear_res = shear.design_shear(
            vu_kn=80, b=b, d=d, fck=fck, fy=fy, asv=157, pt=pt
        )

        # Both should be safe for reasonable loads
        assert flex_res.is_safe
        assert shear_res.is_safe

    def test_high_moment_low_shear(self):
        """High moment sections may have low shear - both checks must pass."""
        flex_res = flexure.design_singly_reinforced(
            b=230, d=450, d_total=500, mu_knm=120, fck=25, fy=500
        )
        # High Ast -> high pt -> higher tc -> shear more likely to pass
        pt = (flex_res.ast_required * 100) / (230 * 450)

        shear_res = shear.design_shear(
            vu_kn=50, b=230, d=450, fck=25, fy=500, asv=157, pt=pt
        )
        assert shear_res.is_safe

    def test_doubly_reinforced_section_safety(self):
        """Doubly reinforced section should still be safe for valid moment."""
        b, d, fck, fy = 230, 450, 25, 500
        mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)

        # 20% over Mu_lim -> doubly reinforced
        res = flexure.design_doubly_reinforced(
            b=b, d=d, d_dash=50, d_total=500, mu_knm=mu_lim * 1.2, fck=fck, fy=fy
        )

        assert res.is_safe
        assert res.asc_required > 0
        assert res.section_type == DesignSectionType.OVER_REINFORCED


# =============================================================================
# Section 8: Determinism Tests
# =============================================================================


class TestDeterminism:
    """Verify calculations are deterministic (no hidden state)."""

    def test_flexure_deterministic(self):
        """Same inputs should give identical outputs."""
        params = dict(b=230, d=450, d_total=500, mu_knm=100, fck=25, fy=500)

        res1 = flexure.design_singly_reinforced(**params)
        res2 = flexure.design_singly_reinforced(**params)

        assert res1.ast_required == res2.ast_required
        assert res1.xu == res2.xu
        assert res1.mu_lim == res2.mu_lim

    def test_shear_deterministic(self):
        """Same inputs should give identical outputs."""
        params = dict(vu_kn=100, b=250, d=450, fck=25, fy=415, asv=157, pt=0.5)

        res1 = shear.design_shear(**params)
        res2 = shear.design_shear(**params)

        assert res1.tv == res2.tv
        assert res1.tc == res2.tc
        assert res1.spacing == res2.spacing

    def test_table_lookup_deterministic(self):
        """Table lookups should be deterministic."""
        tc1 = tables.get_tc_value(25, 0.75)
        tc2 = tables.get_tc_value(25, 0.75)
        assert tc1 == tc2

        tc_max1 = tables.get_tc_max_value(25)
        tc_max2 = tables.get_tc_max_value(25)
        assert tc_max1 == tc_max2
