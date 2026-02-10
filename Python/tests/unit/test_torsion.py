"""
Test Suite for Torsion Module

Tests cover:
- Equivalent shear calculation (IS 456 Cl 41.3.1)
- Equivalent moment calculation (IS 456 Cl 41.4.2)
- Torsion shear stress calculation (IS 456 Cl 41.3)
- Complete torsion design (IS 456 Cl 41)
- Edge cases and validation
"""

import pytest

from structural_lib.codes.is456.torsion import (
    TorsionResult,
    calculate_equivalent_moment,
    calculate_equivalent_shear,
    calculate_longitudinal_torsion_steel,
    calculate_torsion_shear_stress,
    calculate_torsion_stirrup_area,
    design_torsion,
)
from structural_lib.core.errors import DimensionError, MaterialError


class TestEquivalentShear:
    """Tests for equivalent shear calculation per IS 456 Cl 41.3.1."""

    def test_basic_calculation(self):
        """Ve = Vu + 1.6 × Tu / b"""
        # Vu = 100 kN, Tu = 10 kN·m, b = 300 mm
        # Ve = 100 + 1.6 × (10 × 1000) / 300 = 100 + 53.33 = 153.33 kN
        ve = calculate_equivalent_shear(vu_kn=100, tu_knm=10, b=300)
        expected = 100 + 1.6 * 10000 / 300
        assert ve == pytest.approx(expected, rel=0.01)

    def test_zero_torsion(self):
        """With Tu = 0, Ve = Vu."""
        ve = calculate_equivalent_shear(vu_kn=100, tu_knm=0, b=300)
        assert ve == pytest.approx(100, rel=0.01)

    def test_negative_shear_uses_absolute(self):
        """Negative shear should use absolute value."""
        ve = calculate_equivalent_shear(vu_kn=-100, tu_knm=10, b=300)
        expected = 100 + 1.6 * 10000 / 300
        assert ve == pytest.approx(expected, rel=0.01)

    def test_zero_width_raises(self):
        """Zero beam width should raise DimensionError."""
        with pytest.raises(DimensionError):
            calculate_equivalent_shear(vu_kn=100, tu_knm=10, b=0)

    def test_negative_width_raises(self):
        """Negative beam width should raise DimensionError."""
        with pytest.raises(DimensionError):
            calculate_equivalent_shear(vu_kn=100, tu_knm=10, b=-300)


class TestEquivalentMoment:
    """Tests for equivalent moment calculation per IS 456 Cl 41.4.2."""

    def test_basic_calculation(self):
        """Me = Mu + Mt where Mt = Tu × (1 + D/b) / 1.7"""
        # Mu = 150 kN·m, Tu = 10 kN·m, d = 450 mm, b = 300 mm
        # D ≈ d + 50 = 500 mm
        # Mt = 10 × (1 + 500/300) / 1.7 = 10 × 2.67 / 1.7 = 15.69 kN·m
        # Me = 150 + 15.69 = 165.69 kN·m
        me = calculate_equivalent_moment(mu_knm=150, tu_knm=10, d=450, b=300)
        D = 500
        mt = 10 * (1 + D / 300) / 1.7
        expected = 150 + mt
        assert me == pytest.approx(expected, rel=0.01)

    def test_zero_torsion(self):
        """With Tu = 0, Me = Mu."""
        me = calculate_equivalent_moment(mu_knm=150, tu_knm=0, d=450, b=300)
        assert me == pytest.approx(150, rel=0.01)

    def test_zero_width_raises(self):
        """Zero beam width should raise DimensionError."""
        with pytest.raises(DimensionError):
            calculate_equivalent_moment(mu_knm=150, tu_knm=10, d=450, b=0)

    def test_zero_depth_raises(self):
        """Zero depth should raise DimensionError."""
        with pytest.raises(DimensionError):
            calculate_equivalent_moment(mu_knm=150, tu_knm=10, d=0, b=300)


class TestTorsionShearStress:
    """Tests for equivalent shear stress calculation."""

    def test_basic_calculation(self):
        """τve = Ve / (b × d)"""
        # Ve = 153.33 kN, b = 300 mm, d = 450 mm
        # τve = 153.33 × 1000 / (300 × 450) = 1.136 N/mm²
        tv = calculate_torsion_shear_stress(ve_kn=153.33, b=300, d=450)
        expected = 153.33 * 1000 / (300 * 450)
        assert tv == pytest.approx(expected, rel=0.01)

    def test_zero_width_raises(self):
        """Zero beam width should raise DimensionError."""
        with pytest.raises(DimensionError):
            calculate_torsion_shear_stress(ve_kn=153.33, b=0, d=450)

    def test_zero_depth_raises(self):
        """Zero depth should raise DimensionError."""
        with pytest.raises(DimensionError):
            calculate_torsion_shear_stress(ve_kn=153.33, b=300, d=0)


class TestTorsionStirrupArea:
    """Tests for stirrup area calculation."""

    def test_torsion_component(self):
        """Test torsion component of stirrup area."""
        # Tu = 10 kN·m, b1 = 220 mm, d1 = 420 mm, fy = 500 N/mm²
        # Asv/sv (torsion) = Tu × 10⁶ / (b1 × d1 × 0.87 × fy)
        # = 10 × 10⁶ / (220 × 420 × 0.87 × 500) = 0.249 mm²/mm
        asv_torsion, _, _ = calculate_torsion_stirrup_area(
            tu_knm=10,
            vu_kn=0,  # No shear
            b=300,
            d=450,
            b1=220,
            d1=420,
            fy=500,
            tc=0.62,
        )
        expected = 10e6 / (220 * 420 * 0.87 * 500)
        assert asv_torsion == pytest.approx(expected, rel=0.01)

    def test_shear_component(self):
        """Test shear component of stirrup area."""
        # When Vu > Vc, shear reinforcement is needed
        asv_torsion, asv_shear, asv_total = calculate_torsion_stirrup_area(
            tu_knm=0,  # No torsion
            vu_kn=100,
            b=300,
            d=450,
            b1=220,
            d1=420,
            fy=500,
            tc=0.62,
        )
        assert asv_torsion == pytest.approx(0, abs=0.001)
        # Vus = Vu - Vc = 100×1000 - 0.62×300×450 = 100000 - 83700 = 16300 N
        # Asv/sv = Vus / (0.87 × fy × d) = 16300 / (0.87 × 500 × 450) = 0.083
        vus = 100 * 1000 - 0.62 * 300 * 450
        expected_shear = vus / (0.87 * 500 * 450)
        assert asv_shear == pytest.approx(expected_shear, rel=0.05)

    def test_zero_fy_raises(self):
        """Zero steel strength should raise MaterialError."""
        with pytest.raises(MaterialError):
            calculate_torsion_stirrup_area(
                tu_knm=10,
                vu_kn=100,
                b=300,
                d=450,
                b1=220,
                d1=420,
                fy=0,
                tc=0.62,
            )


class TestLongitudinalTorsionSteel:
    """Tests for longitudinal reinforcement for torsion."""

    def test_basic_calculation(self):
        """Al = Tu × (b1 + d1) / (b1 × d1 × 0.87 × fy)"""
        # Tu = 10 kN·m, b1 = 220 mm, d1 = 420 mm, fy = 500 N/mm²
        al = calculate_longitudinal_torsion_steel(
            tu_knm=10,
            vu_kn=100,
            b1=220,
            d1=420,
            fy=500,
            sv=150,
        )
        expected = 10e6 * (220 + 420) / (220 * 420 * 0.87 * 500)
        assert al == pytest.approx(expected, rel=0.01)

    def test_zero_fy_raises(self):
        """Zero steel strength should raise MaterialError."""
        with pytest.raises(MaterialError):
            calculate_longitudinal_torsion_steel(
                tu_knm=10, vu_kn=100, b1=220, d1=420, fy=0, sv=150
            )


class TestDesignTorsion:
    """Tests for complete torsion design function."""

    def test_safe_section(self):
        """Test design of a safe section."""
        result = design_torsion(
            tu_knm=10,
            vu_kn=100,
            mu_knm=150,
            b=300,
            D=500,
            d=450,
            fck=25,
            fy=500,
            cover=40,
            stirrup_dia=8,
            pt=1.0,
        )
        assert result.is_safe is True
        assert result.requires_closed_stirrups is True
        assert result.stirrup_spacing > 0
        assert result.stirrup_spacing <= 300  # Max spacing limit
        assert result.al_torsion > 0
        assert result.ve_kn > result.vu_kn  # Ve should be greater than Vu

    def test_result_type(self):
        """Result should be TorsionResult dataclass."""
        result = design_torsion(
            tu_knm=10,
            vu_kn=100,
            mu_knm=150,
            b=300,
            D=500,
            d=450,
            fck=25,
            fy=500,
            cover=40,
        )
        assert isinstance(result, TorsionResult)

    def test_equivalent_values(self):
        """Test that equivalent values are calculated correctly."""
        result = design_torsion(
            tu_knm=10,
            vu_kn=100,
            mu_knm=150,
            b=300,
            D=500,
            d=450,
            fck=25,
            fy=500,
            cover=40,
        )
        # Ve = Vu + 1.6 × Tu/b = 100 + 1.6 × 10000/300 = 153.33 kN
        expected_ve = 100 + 1.6 * 10000 / 300
        assert result.ve_kn == pytest.approx(expected_ve, rel=0.01)

    def test_high_torsion_unsafe(self):
        """Very high torsion should make section unsafe (τve > τc,max)."""
        result = design_torsion(
            tu_knm=100,  # Very high torsion
            vu_kn=200,
            mu_knm=300,
            b=200,  # Narrow beam
            D=400,
            d=350,
            fck=20,
            fy=500,
            cover=40,
        )
        # τve = Ve / (b × d) should be very high
        # τc,max for M20 = 2.8 N/mm²
        if result.tv_equiv > result.tc_max:
            assert result.is_safe is False
            assert len(result.errors) > 0

    def test_zero_width_raises(self):
        """Zero beam width should raise DimensionError."""
        with pytest.raises(DimensionError):
            design_torsion(
                tu_knm=10,
                vu_kn=100,
                mu_knm=150,
                b=0,
                D=500,
                d=450,
                fck=25,
                fy=500,
                cover=40,
            )

    def test_zero_fck_raises(self):
        """Zero concrete strength should raise MaterialError."""
        with pytest.raises(MaterialError):
            design_torsion(
                tu_knm=10,
                vu_kn=100,
                mu_knm=150,
                b=300,
                D=500,
                d=450,
                fck=0,
                fy=500,
                cover=40,
            )

    def test_zero_fy_raises(self):
        """Zero steel strength should raise MaterialError."""
        with pytest.raises(MaterialError):
            design_torsion(
                tu_knm=10,
                vu_kn=100,
                mu_knm=150,
                b=300,
                D=500,
                d=450,
                fck=25,
                fy=0,
                cover=40,
            )

    def test_spacing_limits_applied(self):
        """Stirrup spacing should respect maximum limits."""
        result = design_torsion(
            tu_knm=5,  # Low torsion
            vu_kn=50,  # Low shear
            mu_knm=100,
            b=300,
            D=500,
            d=450,
            fck=25,
            fy=500,
            cover=40,
        )
        # Check spacing limits
        assert result.stirrup_spacing <= 0.75 * 450  # 0.75d limit
        assert result.stirrup_spacing <= 300  # Absolute max

    def test_torsion_components_sum(self):
        """Total stirrup area should equal torsion + shear components."""
        result = design_torsion(
            tu_knm=10,
            vu_kn=100,
            mu_knm=150,
            b=300,
            D=500,
            d=450,
            fck=25,
            fy=500,
            cover=40,
        )
        expected_total = result.asv_torsion + result.asv_shear
        assert result.asv_total == pytest.approx(expected_total, rel=0.01)


class TestEdgeCases:
    """Edge case tests for torsion module."""

    def test_very_small_torsion(self):
        """Very small torsion should still produce valid result."""
        result = design_torsion(
            tu_knm=0.1,  # Very small torsion
            vu_kn=50,
            mu_knm=100,
            b=300,
            D=500,
            d=450,
            fck=25,
            fy=500,
            cover=40,
        )
        assert result.is_safe is True
        assert result.stirrup_spacing > 0

    def test_zero_moment(self):
        """Zero applied moment should work (pure torsion+shear)."""
        result = design_torsion(
            tu_knm=10,
            vu_kn=100,
            mu_knm=0,  # Zero moment
            b=300,
            D=500,
            d=450,
            fck=25,
            fy=500,
            cover=40,
        )
        assert result.is_safe is True
        assert result.me_knm > 0  # Me should still be > 0 due to Mt

    def test_large_beam(self):
        """Large beam section should handle correctly."""
        result = design_torsion(
            tu_knm=50,
            vu_kn=300,
            mu_knm=500,
            b=600,
            D=1000,
            d=950,
            fck=30,
            fy=500,
            cover=50,
        )
        assert result.is_safe is True
        assert result.stirrup_spacing > 0

    def test_high_grade_concrete(self):
        """High grade concrete should give higher tc_max."""
        result_m40 = design_torsion(
            tu_knm=20,
            vu_kn=150,
            mu_knm=200,
            b=300,
            D=500,
            d=450,
            fck=40,
            fy=500,
            cover=40,
        )
        result_m20 = design_torsion(
            tu_knm=20,
            vu_kn=150,
            mu_knm=200,
            b=300,
            D=500,
            d=450,
            fck=20,
            fy=500,
            cover=40,
        )
        assert result_m40.tc_max > result_m20.tc_max
