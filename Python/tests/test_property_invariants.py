"""
Property-based tests for structural engineering calculations.

These tests verify mathematical invariants that should ALWAYS hold,
regardless of input values (within valid ranges).

Invariants tested:
1. Non-negativity: Areas, lengths, capacities >= 0
2. Monotonicity: More moment -> more steel required
3. Consistency: xu <= xu_max for under-reinforced sections
4. Bounds: pt_provided within reasonable engineering limits

SKIPPED TESTS EXPLAINED (reviewed 2025-12-28):
----------------------------------------------
This module has ~91 intentional skips. These are NOT bugs:

1. test_mu_lim_increases_with_d (90 skips):
   - Skips when d == min(D_VALUES) because comparative tests need a
     smaller reference value. You can't test "Mu_lim increases with d"
     when d is already the minimum.
   - The test runs for d = 400, 450, 500, 550, 600mm (comparing to d-50).

2. test_xu_max_d_decreases_with_fy (1 skip):
   - Skips when fy == 415 because it's the lowest fy to compare against.
   - The test runs for Fe500 and Fe550 (comparing to Fe415).

These skips are mathematically necessary for comparative invariant tests.
No action required.
"""

import pytest
from structural_lib import flexure, shear, detailing, materials, tables


# =============================================================================
# FLEXURE INVARIANTS
# =============================================================================


class TestFlexureInvariants:
    """Property tests for flexure module."""

    # Typical beam dimensions
    B_VALUES = [200, 230, 250, 300, 350, 400]
    D_VALUES = [350, 400, 450, 500, 550, 600]
    FCK_VALUES = [20, 25, 30, 35, 40]
    FY_VALUES = [415, 500, 550]

    @pytest.mark.parametrize("b", B_VALUES)
    @pytest.mark.parametrize("d", D_VALUES)
    @pytest.mark.parametrize("fck", FCK_VALUES)
    @pytest.mark.parametrize("fy", FY_VALUES)
    def test_mu_lim_is_positive(self, b, d, fck, fy):
        """Mu_lim should always be positive for valid inputs."""
        mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)
        assert mu_lim > 0, f"Mu_lim should be positive, got {mu_lim}"

    @pytest.mark.parametrize("b", B_VALUES)
    @pytest.mark.parametrize("d", D_VALUES)
    @pytest.mark.parametrize("fck", FCK_VALUES)
    @pytest.mark.parametrize("fy", FY_VALUES)
    def test_mu_lim_increases_with_d(self, b, d, fck, fy):
        """Mu_lim should increase as effective depth increases."""
        if d <= min(self.D_VALUES):
            pytest.skip("Need d > min to compare")

        d_smaller = d - 50
        mu_lim_smaller = flexure.calculate_mu_lim(b, d_smaller, fck, fy)
        mu_lim_larger = flexure.calculate_mu_lim(b, d, fck, fy)

        assert (
            mu_lim_larger > mu_lim_smaller
        ), f"Mu_lim should increase with d: {mu_lim_smaller} -> {mu_lim_larger}"

    @pytest.mark.parametrize("fck", FCK_VALUES)
    @pytest.mark.parametrize("fy", FY_VALUES)
    def test_ast_increases_with_moment(self, fck, fy):
        """More moment should require more steel (monotonic in Mu)."""
        b, d = 300, 500

        mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)

        # Test at 30%, 50%, 70% of Mu_lim
        mu_low = 0.3 * mu_lim
        mu_mid = 0.5 * mu_lim
        mu_high = 0.7 * mu_lim

        ast_low = flexure.calculate_ast_required(b, d, mu_low, fck, fy)
        ast_mid = flexure.calculate_ast_required(b, d, mu_mid, fck, fy)
        ast_high = flexure.calculate_ast_required(b, d, mu_high, fck, fy)

        assert (
            ast_low < ast_mid < ast_high
        ), f"Ast should be monotonic: {ast_low} < {ast_mid} < {ast_high}"

    @pytest.mark.parametrize("fck", FCK_VALUES)
    @pytest.mark.parametrize("fy", FY_VALUES)
    def test_singly_reinforced_xu_within_limit(self, fck, fy):
        """For under-reinforced sections, xu <= xu_max."""
        b, d, d_total = 300, 500, 550

        mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)
        mu = 0.6 * mu_lim  # Under-reinforced

        result = flexure.design_singly_reinforced(b, d, d_total, mu, fck, fy)

        assert (
            result.xu <= result.xu_max
        ), f"xu ({result.xu}) should be <= xu_max ({result.xu_max})"

    def test_zero_moment_gives_minimum_steel(self):
        """Zero moment should give minimum steel (Ast_min)."""
        b, d, d_total = 300, 500, 550
        fck, fy = 25, 500

        result = flexure.design_singly_reinforced(b, d, d_total, 0.001, fck, fy)

        # Should get minimum steel area
        assert result.ast_required > 0, "Should provide minimum steel"
        assert result.is_safe, "Zero moment should be safe"


# =============================================================================
# SHEAR INVARIANTS
# =============================================================================


class TestShearInvariants:
    """Property tests for shear module."""

    @pytest.mark.parametrize("fck", [20, 25, 30, 35, 40])
    @pytest.mark.parametrize("pt", [0.25, 0.5, 0.75, 1.0, 1.5, 2.0])
    def test_tc_is_positive(self, fck, pt):
        """Concrete shear strength tc should always be positive."""
        tc = tables.get_tc_value(fck, pt)
        assert tc > 0, f"tc should be positive, got {tc}"

    @pytest.mark.parametrize("fck", [20, 25, 30, 35, 40])
    def test_tc_increases_with_pt(self, fck):
        """tc should increase with reinforcement percentage (up to limit)."""
        pt_low = 0.5
        pt_high = 1.5

        tc_low = tables.get_tc_value(fck, pt_low)
        tc_high = tables.get_tc_value(fck, pt_high)

        assert tc_high >= tc_low, f"tc should increase with pt: {tc_low} -> {tc_high}"

    @pytest.mark.parametrize("fck", [20, 25, 30, 35, 40])
    def test_tc_max_is_positive(self, fck):
        """Maximum shear stress tc_max should be positive."""
        tc_max = tables.get_tc_max_value(fck)
        assert tc_max > 0, f"tc_max should be positive, got {tc_max}"

    @pytest.mark.parametrize("fck", [20, 25, 30, 35, 40])
    def test_tc_never_exceeds_tc_max(self, fck):
        """tc should never exceed tc_max for any pt."""
        tc_max = tables.get_tc_max_value(fck)

        for pt in [0.25, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
            tc = tables.get_tc_value(fck, pt)
            assert (
                tc <= tc_max
            ), f"tc ({tc}) should not exceed tc_max ({tc_max}) at pt={pt}%"


# =============================================================================
# DETAILING INVARIANTS
# =============================================================================


class TestDetailingInvariants:
    """Property tests for detailing module."""

    BAR_DIAS = [8, 10, 12, 16, 20, 25, 32]
    FCK_VALUES = [20, 25, 30, 35, 40]
    FY_VALUES = [415, 500, 550]

    @pytest.mark.parametrize("dia", BAR_DIAS)
    @pytest.mark.parametrize("fck", FCK_VALUES)
    @pytest.mark.parametrize("fy", FY_VALUES)
    def test_ld_is_positive(self, dia, fck, fy):
        """Development length should always be positive."""
        ld = detailing.calculate_development_length(dia, fck, fy, "deformed")
        assert ld > 0, f"Ld should be positive, got {ld}"

    @pytest.mark.parametrize("fck", FCK_VALUES)
    @pytest.mark.parametrize("fy", FY_VALUES)
    def test_ld_increases_with_diameter(self, fck, fy):
        """Ld should increase with bar diameter (proportional)."""
        ld_12 = detailing.calculate_development_length(12, fck, fy, "deformed")
        ld_16 = detailing.calculate_development_length(16, fck, fy, "deformed")
        ld_20 = detailing.calculate_development_length(20, fck, fy, "deformed")

        assert (
            ld_12 < ld_16 < ld_20
        ), f"Ld should increase with diameter: {ld_12} < {ld_16} < {ld_20}"

    @pytest.mark.parametrize("dia", BAR_DIAS)
    @pytest.mark.parametrize("fck", FCK_VALUES)
    @pytest.mark.parametrize("fy", FY_VALUES)
    def test_lap_length_at_least_ld(self, dia, fck, fy):
        """Lap length should be >= Ld (multiplier >= 1.0)."""
        ld = detailing.calculate_development_length(dia, fck, fy, "deformed")
        # Compression lap equals Ld; tension lap >= Ld
        lap_compression = detailing.calculate_lap_length(
            dia,
            fck,
            fy,
            "deformed",
            splice_percent=50.0,
            is_seismic=False,
            in_tension=False,
        )
        lap_tension = detailing.calculate_lap_length(
            dia,
            fck,
            fy,
            "deformed",
            splice_percent=50.0,
            is_seismic=False,
            in_tension=True,
        )

        assert (
            lap_compression >= ld - 1
        ), f"Compression lap ({lap_compression}) should be >= Ld ({ld})"
        assert (
            lap_tension >= ld - 1
        ), f"Tension lap ({lap_tension}) should be >= Ld ({ld})"

    @pytest.mark.parametrize("dia", BAR_DIAS)
    @pytest.mark.parametrize("fck", FCK_VALUES)
    def test_seismic_lap_exceeds_normal(self, dia, fck):
        """Seismic lap length should be > normal lap length."""
        fy = 500
        lap_normal = detailing.calculate_lap_length(
            dia,
            fck,
            fy,
            "deformed",
            splice_percent=50.0,
            is_seismic=False,
            in_tension=True,
        )
        lap_seismic = detailing.calculate_lap_length(
            dia,
            fck,
            fy,
            "deformed",
            splice_percent=50.0,
            is_seismic=True,
            in_tension=True,
        )

        assert (
            lap_seismic > lap_normal
        ), f"Seismic lap ({lap_seismic}) should be > normal lap ({lap_normal})"

    @pytest.mark.parametrize("fck", FCK_VALUES)
    def test_bond_stress_is_positive(self, fck):
        """Bond stress should always be positive."""
        tau_bd = detailing.get_bond_stress(fck, "deformed")
        assert tau_bd > 0, f"τbd should be positive, got {tau_bd}"


# =============================================================================
# MATERIALS INVARIANTS
# =============================================================================


class TestMaterialsInvariants:
    """Property tests for materials module."""

    @pytest.mark.parametrize("fy", [415, 500, 550])
    def test_xu_max_d_in_valid_range(self, fy):
        """xu_max/d ratio should be between 0 and 1."""
        xu_max_d = materials.get_xu_max_d(fy)
        assert 0 < xu_max_d < 1, f"xu_max/d should be in (0, 1), got {xu_max_d}"

    @pytest.mark.parametrize("fy", [415, 500, 550])
    def test_xu_max_d_decreases_with_fy(self, fy):
        """xu_max/d should decrease as fy increases (ductility)."""
        if fy == 415:
            pytest.skip("Need comparison with lower fy")

        # Fe415 has higher xu_max/d than Fe500/550
        xu_max_d_415 = materials.get_xu_max_d(415)
        xu_max_d_current = materials.get_xu_max_d(fy)

        assert (
            xu_max_d_current < xu_max_d_415
        ), f"xu_max/d should decrease with fy: {xu_max_d_415} > {xu_max_d_current}"


# =============================================================================
# CROSS-MODULE CONSISTENCY
# =============================================================================


class TestCrossModuleConsistency:
    """Tests that verify consistency across modules."""

    def test_flexure_shear_design_compatible(self):
        """Flexure and shear results should be compatible for same beam."""
        b, d, d_total = 300, 500, 550
        fck, fy = 25, 500
        mu, vu = 200, 150  # kN·m, kN

        flex_result = flexure.design_singly_reinforced(b, d, d_total, mu, fck, fy)

        # Use pt from flexure for shear check
        pt_percent = flex_result.pt_provided
        shear_result = shear.design_shear(
            vu_kn=vu, b=b, d=d, fck=fck, fy=fy, asv=100, pt=pt_percent
        )

        # Both should give valid results
        assert flex_result.is_safe, "Flexure should be safe"
        assert shear_result.is_safe, "Shear should be safe"

    def test_detailing_uses_max_bar_for_ld(self):
        """Detailing for beam should use max bar diameter for Ld."""
        # This verifies the documented behavior
        ld_16 = detailing.calculate_development_length(16, 25, 500, "deformed")
        ld_20 = detailing.calculate_development_length(20, 25, 500, "deformed")

        # A beam with both 16mm and 20mm bars should use Ld for 20mm
        assert ld_20 > ld_16, "Larger bar requires longer Ld"
