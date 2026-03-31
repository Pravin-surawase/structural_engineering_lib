"""
Dedicated unit tests for shear module.

Tests cover:
- calculate_tv: nominal shear stress calculation
- design_shear: full shear design per IS 456
- enhanced_shear_strength: IS 456 Cl 40.3 near supports

Reference: IS 456:2000 Clause 40
"""

import pytest

from structural_lib import shear
from structural_lib.codes.is456.beam.shear import enhanced_shear_strength
from structural_lib.core.errors import DimensionError


def _has_error_with_code(errors, code: str) -> bool:
    """Check if errors list contains an error with the given code."""
    return any(e.code == code for e in errors)


def _has_error_with_message(errors, message_substring: str) -> bool:
    """Check if errors list contains an error with the given message substring."""
    return any(message_substring.lower() in e.message.lower() for e in errors)


def _get_error_messages(errors) -> list[str]:
    """Extract all error messages from errors list."""
    return [e.message for e in errors]


class TestCalculateTv:
    """Tests for calculate_tv function."""

    def test_basic_calculation(self):
        """Verify nominal shear stress formula: tv = Vu*1000 / (b*d)."""
        # Vu = 100 kN, b = 250 mm, d = 450 mm
        # tv = 100 * 1000 / (250 * 450) = 0.889 N/mm²
        tv = shear.calculate_tv(vu_kn=100.0, b=250.0, d=450.0)
        assert tv == pytest.approx(0.8889, rel=1e-3)

    def test_zero_dimensions_raises_error(self):
        """Zero b or d should raise DimensionError (no silent failures)."""
        with pytest.raises(DimensionError, match="beam width b"):
            shear.calculate_tv(vu_kn=100.0, b=0.0, d=450.0)
        with pytest.raises(DimensionError, match="effective depth d"):
            shear.calculate_tv(vu_kn=100.0, b=250.0, d=0.0)

    def test_negative_shear_uses_absolute(self):
        """Negative shear should use absolute value."""
        tv_pos = shear.calculate_tv(vu_kn=100.0, b=250.0, d=450.0)
        tv_neg = shear.calculate_tv(vu_kn=-100.0, b=250.0, d=450.0)
        assert tv_pos == tv_neg

    def test_zero_shear_returns_zero(self):
        """Zero shear force gives zero stress."""
        assert shear.calculate_tv(vu_kn=0.0, b=250.0, d=450.0) == 0.0


class TestDesignShear:
    """Tests for design_shear function."""

    def test_invalid_dimensions_returns_unsafe(self):
        """Zero or negative b/d should return unsafe result."""
        result = shear.design_shear(
            vu_kn=100.0, b=0.0, d=450.0, fck=25.0, fy=415.0, asv=157.0, pt=0.5
        )
        assert result.is_safe is False
        assert _has_error_with_message(result.errors, "b must be > 0")

        result = shear.design_shear(
            vu_kn=100.0, b=250.0, d=-100.0, fck=25.0, fy=415.0, asv=157.0, pt=0.5
        )
        assert result.is_safe is False

    def test_invalid_material_returns_unsafe(self):
        """Zero or negative fck/fy should return unsafe result."""
        result = shear.design_shear(
            vu_kn=100.0, b=250.0, d=450.0, fck=0.0, fy=415.0, asv=157.0, pt=0.5
        )
        assert result.is_safe is False
        assert _has_error_with_message(result.errors, "fck must be > 0")

    def test_invalid_asv_returns_unsafe(self):
        """Zero or negative Asv should return unsafe result."""
        result = shear.design_shear(
            vu_kn=100.0, b=250.0, d=450.0, fck=25.0, fy=415.0, asv=0.0, pt=0.5
        )
        assert result.is_safe is False
        assert _has_error_with_message(result.errors, "asv must be > 0")

    def test_negative_pt_returns_unsafe(self):
        """Negative pt should return unsafe result."""
        result = shear.design_shear(
            vu_kn=100.0, b=250.0, d=450.0, fck=25.0, fy=415.0, asv=157.0, pt=-0.5
        )
        assert result.is_safe is False
        assert _has_error_with_message(result.errors, "pt must be >= 0")

    def test_exceeds_tc_max_returns_unsafe(self):
        """Shear stress exceeding tc_max should return unsafe."""
        # Very high shear, small section
        result = shear.design_shear(
            vu_kn=500.0, b=150.0, d=200.0, fck=20.0, fy=415.0, asv=157.0, pt=1.0
        )
        assert result.is_safe is False
        assert _has_error_with_message(
            result.errors, "exceeds tc_max"
        ) or _has_error_with_code(result.errors, "E_SHEAR_001")

    def test_nominal_shear_less_than_tc(self):
        """Low shear stress < tc: minimum reinforcement required."""
        # Small shear force
        result = shear.design_shear(
            vu_kn=20.0, b=250.0, d=450.0, fck=25.0, fy=415.0, asv=157.0, pt=1.0
        )
        assert result.is_safe is True
        assert result.vus == 0.0
        # Check for minimum shear reinforcement info in errors list
        assert _has_error_with_message(
            result.errors, "minimum"
        ) or _has_error_with_code(result.errors, "E_SHEAR_003")

    def test_shear_reinforcement_required(self):
        """Higher shear stress > tc: stirrup design required."""
        result = shear.design_shear(
            vu_kn=150.0, b=250.0, d=450.0, fck=25.0, fy=415.0, asv=157.0, pt=0.5
        )
        assert result.is_safe is True
        assert result.vus > 0.0
        # When reinforcement is required and provided, design is safe
        # No specific error message needed when design succeeds

    def test_tc_value_lookup(self):
        """Verify tc is looked up from Table 19."""
        result = shear.design_shear(
            vu_kn=100.0, b=250.0, d=450.0, fck=25.0, fy=415.0, asv=157.0, pt=0.5
        )
        # For M25, pt=0.5%, tc ≈ 0.49 N/mm² (from Table 19)
        assert result.tc == pytest.approx(0.49, rel=0.05)

    def test_tc_max_value_lookup(self):
        """Verify tc_max is looked up from Table 20."""
        result = shear.design_shear(
            vu_kn=100.0, b=250.0, d=450.0, fck=25.0, fy=415.0, asv=157.0, pt=0.5
        )
        # For M25, tc_max = 3.1 N/mm² (from Table 20)
        assert result.tc_max == pytest.approx(3.1, rel=0.02)

    def test_spacing_within_limits(self):
        """Spacing should not exceed 0.75d or 300mm."""
        result = shear.design_shear(
            vu_kn=100.0, b=250.0, d=450.0, fck=25.0, fy=415.0, asv=157.0, pt=0.5
        )
        assert result.spacing <= 0.75 * 450.0
        assert result.spacing <= 300.0

    def test_result_contains_all_fields(self):
        """Verify ShearResult has all expected fields."""
        result = shear.design_shear(
            vu_kn=100.0, b=250.0, d=450.0, fck=25.0, fy=415.0, asv=157.0, pt=0.5
        )
        assert hasattr(result, "tv")
        assert hasattr(result, "tc")
        assert hasattr(result, "tc_max")
        assert hasattr(result, "vus")
        assert hasattr(result, "spacing")
        assert hasattr(result, "is_safe")
        assert hasattr(result, "errors")  # New structured errors field
        assert hasattr(result, "remarks")  # Deprecated, kept for backward compat

    def test_symmetric_positive_negative_shear(self):
        """Positive and negative shear should give same design."""
        result_pos = shear.design_shear(
            vu_kn=100.0, b=250.0, d=450.0, fck=25.0, fy=415.0, asv=157.0, pt=0.5
        )
        result_neg = shear.design_shear(
            vu_kn=-100.0, b=250.0, d=450.0, fck=25.0, fy=415.0, asv=157.0, pt=0.5
        )
        assert result_pos.tv == result_neg.tv
        assert result_pos.spacing == result_neg.spacing

    def test_higher_pt_gives_higher_tc(self):
        """Higher steel percentage should give higher tc."""
        result_low_pt = shear.design_shear(
            vu_kn=100.0, b=250.0, d=450.0, fck=25.0, fy=415.0, asv=157.0, pt=0.25
        )
        result_high_pt = shear.design_shear(
            vu_kn=100.0, b=250.0, d=450.0, fck=25.0, fy=415.0, asv=157.0, pt=1.5
        )
        assert result_high_pt.tc > result_low_pt.tc

    def test_higher_fck_gives_higher_tc_max(self):
        """Higher concrete grade should give higher tc_max."""
        result_m20 = shear.design_shear(
            vu_kn=100.0, b=250.0, d=450.0, fck=20.0, fy=415.0, asv=157.0, pt=0.5
        )
        result_m40 = shear.design_shear(
            vu_kn=100.0, b=250.0, d=450.0, fck=40.0, fy=415.0, asv=157.0, pt=0.5
        )
        assert result_m40.tc_max > result_m20.tc_max


class TestShearEdgeCases:
    """Edge case tests for shear module."""

    def test_zero_shear_force(self):
        """Zero shear force should still be safe (minimum reinforcement)."""
        result = shear.design_shear(
            vu_kn=0.0, b=250.0, d=450.0, fck=25.0, fy=415.0, asv=157.0, pt=0.5
        )
        assert result.is_safe is True
        assert result.tv == 0.0

    def test_very_small_shear(self):
        """Very small shear should be safe."""
        result = shear.design_shear(
            vu_kn=0.001, b=250.0, d=450.0, fck=25.0, fy=415.0, asv=157.0, pt=0.5
        )
        assert result.is_safe is True

    def test_boundary_at_tc_max(self):
        """Shear stress exactly at tc_max boundary."""
        # For M25, tc_max = 3.1 N/mm²
        # tv = 3.1 => Vu = 3.1 * 250 * 450 / 1000 = 348.75 kN
        result_at = shear.design_shear(
            vu_kn=348.0, b=250.0, d=450.0, fck=25.0, fy=415.0, asv=157.0, pt=0.5
        )
        result_above = shear.design_shear(
            vu_kn=360.0, b=250.0, d=450.0, fck=25.0, fy=415.0, asv=157.0, pt=0.5
        )
        assert result_at.is_safe is True
        assert result_above.is_safe is False

    def test_various_concrete_grades(self):
        """Test with different concrete grades."""
        grades = [20, 25, 30, 35, 40]
        for fck in grades:
            result = shear.design_shear(
                vu_kn=100.0,
                b=250.0,
                d=450.0,
                fck=float(fck),
                fy=415.0,
                asv=157.0,
                pt=0.5,
            )
            assert result.tc_max > 0.0
            assert result.tc > 0.0


class TestPracticalSpacingRounding:
    """Tests for round_to_practical_spacing function.

    Stirrup spacings should be rounded to standard construction values
    for practical site implementation.
    """

    def test_round_down_basic(self):
        """Test rounding down to nearest standard spacing."""
        # 241mm should round down to 225mm
        assert shear.round_to_practical_spacing(241.3) == 225.0
        # 187mm should round down to 175mm
        assert shear.round_to_practical_spacing(187.5) == 175.0
        # 160mm should round down to 150mm
        assert shear.round_to_practical_spacing(160.0) == 150.0

    def test_exact_standard_values_unchanged(self):
        """Exact standard values should remain unchanged."""
        standard_values = [75, 100, 125, 150, 175, 200, 225, 250, 275, 300]
        for val in standard_values:
            assert shear.round_to_practical_spacing(float(val)) == float(val)

    def test_round_to_nearest_option(self):
        """Test rounding to nearest (not just down)."""
        # 238mm is closer to 250 than 225
        assert shear.round_to_practical_spacing(238.0, round_down=False) == 250.0
        # 187mm is closer to 175 than 200
        assert shear.round_to_practical_spacing(187.0, round_down=False) == 175.0

    def test_values_below_minimum(self):
        """Values below 75mm should return 75mm (minimum)."""
        assert shear.round_to_practical_spacing(50.0) == 75.0
        assert shear.round_to_practical_spacing(30.0) == 75.0

    def test_values_above_maximum(self):
        """Values above 300mm should return 300mm (maximum per code)."""
        assert shear.round_to_practical_spacing(350.0) == 300.0
        assert shear.round_to_practical_spacing(500.0) == 300.0

    def test_zero_and_negative_values(self):
        """Zero and negative values should return 0."""
        assert shear.round_to_practical_spacing(0.0) == 0.0
        assert shear.round_to_practical_spacing(-100.0) == 0.0

    def test_design_shear_uses_practical_spacing(self):
        """Verify design_shear returns practical spacing values."""
        result = shear.design_shear(
            vu_kn=100.0, b=250.0, d=450.0, fck=25.0, fy=415.0, asv=157.0, pt=0.5
        )
        # Spacing should be one of the standard values
        standard_values = [75, 100, 125, 150, 175, 200, 225, 250, 275, 300]
        assert result.spacing in standard_values or result.spacing == 0.0


class TestSelectStirrupDiameter:
    """Tests for select_stirrup_diameter function (added 2026-01-15)."""

    def test_light_shear_narrow_beam(self):
        """Light shear with narrow beam should use 6mm or 8mm."""
        # Small shear force, narrow beam
        dia = shear.select_stirrup_diameter(
            vu_kn=30, b_mm=200, d_mm=350, fck=25, main_bar_dia=12
        )
        assert dia in [6, 8]

    def test_normal_shear_standard_beam(self):
        """Normal shear with standard beam should use 8mm."""
        # Typical residential beam
        dia = shear.select_stirrup_diameter(
            vu_kn=80, b_mm=300, d_mm=450, fck=25, main_bar_dia=16
        )
        assert dia == 8

    def test_moderate_shear_large_beam(self):
        """Moderate shear with large beam should use 10mm."""
        dia = shear.select_stirrup_diameter(
            vu_kn=150, b_mm=400, d_mm=600, fck=30, main_bar_dia=20
        )
        assert dia == 10

    def test_high_shear_large_beam(self):
        """High shear (tv >= 1.5) with large beam should use 12mm.

        For 500x800 beam, tv >= 1.5 requires vu_kn >= 600 kN.
        tv = 600*1000/(500*800) = 1.5 N/mm²
        """
        dia = shear.select_stirrup_diameter(
            vu_kn=650, b_mm=500, d_mm=800, fck=30, main_bar_dia=25
        )
        assert dia == 12

    def test_minimum_dia_from_main_bar(self):
        """Stirrup should be at least main_bar_dia/4."""
        # 32mm main bar -> min stirrup = 8mm
        dia = shear.select_stirrup_diameter(
            vu_kn=50, b_mm=300, d_mm=450, fck=25, main_bar_dia=32
        )
        assert dia >= 8  # 32/4 = 8

    def test_returns_standard_sizes_only(self):
        """Should return only standard sizes: 6, 8, 10, 12."""
        standard_sizes = shear.STANDARD_STIRRUP_DIAMETERS

        for vu in [30, 80, 150, 300]:
            for b in [200, 300, 400, 500]:
                dia = shear.select_stirrup_diameter(
                    vu_kn=vu, b_mm=b, d_mm=450, fck=25, main_bar_dia=16
                )
                assert (
                    dia in standard_sizes
                ), f"Got {dia} which is not in {standard_sizes}"

    def test_zero_dimensions_returns_default(self):
        """Zero dimensions should return safe default (8mm)."""
        dia = shear.select_stirrup_diameter(
            vu_kn=100, b_mm=0, d_mm=450, fck=25, main_bar_dia=16
        )
        assert dia == 8

        dia = shear.select_stirrup_diameter(
            vu_kn=100, b_mm=300, d_mm=0, fck=25, main_bar_dia=16
        )
        assert dia == 8

    def test_increasing_shear_increases_diameter(self):
        """Higher shear should generally result in larger stirrup diameter."""
        # Same beam, increasing shear
        dia_low = shear.select_stirrup_diameter(
            vu_kn=30, b_mm=400, d_mm=600, fck=25, main_bar_dia=16
        )
        dia_high = shear.select_stirrup_diameter(
            vu_kn=400, b_mm=400, d_mm=600, fck=25, main_bar_dia=16
        )
        assert dia_high >= dia_low


class TestSelectStirrupDiameterNumLegs:
    """Tests for num_legs parameter in select_stirrup_diameter.

    Multi-leg stirrups reduce effective shear stress, allowing smaller diameters.
    Formula: effective_tv = tv * (2.0 / num_legs) when num_legs > 2.
    """

    def test_num_legs_4_reduces_diameter(self):
        """With 4 legs, effective_tv halves, allowing smaller diameter."""
        # High shear case that needs 10mm with 2 legs
        dia_2legs = shear.select_stirrup_diameter(
            vu_kn=150, b_mm=400, d_mm=600, fck=30, main_bar_dia=20, num_legs=2
        )
        dia_4legs = shear.select_stirrup_diameter(
            vu_kn=150, b_mm=400, d_mm=600, fck=30, main_bar_dia=20, num_legs=4
        )
        # 4 legs should allow smaller diameter
        assert dia_4legs < dia_2legs

    def test_num_legs_6_reduces_further(self):
        """With 6 legs, effective_tv is 1/3, reducing diameter further."""
        dia_2legs = shear.select_stirrup_diameter(
            vu_kn=650, b_mm=500, d_mm=800, fck=30, main_bar_dia=20, num_legs=2
        )
        dia_6legs = shear.select_stirrup_diameter(
            vu_kn=650, b_mm=500, d_mm=800, fck=30, main_bar_dia=20, num_legs=6
        )
        # 6 legs should give smaller diameter than 2 legs
        assert dia_6legs < dia_2legs

    def test_num_legs_2_is_default(self):
        """num_legs=2 should match default behavior (no num_legs specified)."""
        dia_explicit = shear.select_stirrup_diameter(
            vu_kn=80, b_mm=300, d_mm=450, fck=25, main_bar_dia=16, num_legs=2
        )
        dia_default = shear.select_stirrup_diameter(
            vu_kn=80, b_mm=300, d_mm=450, fck=25, main_bar_dia=16
        )
        assert dia_explicit == dia_default

    def test_num_legs_does_not_go_below_min_dia(self):
        """Even with many legs, diameter respects main_bar_dia/4 minimum."""
        # main_bar_dia=32 means minimum stirrup diameter = 8mm
        # Low shear + 6 legs should not go below 8mm
        dia = shear.select_stirrup_diameter(
            vu_kn=30, b_mm=200, d_mm=350, fck=25, main_bar_dia=32, num_legs=6
        )
        assert dia >= 8  # main_bar_dia/4 = 32/4 = 8


class TestDesignShearSteelGrades:
    """Tests for different steel grades (fy values) in design_shear.

    Higher fy allows larger spacing (fewer stirrups needed).
    Fe 250: fy=250, Fe 415: fy=415, Fe 500: fy=500.
    """

    def test_fe250_gives_smaller_spacing(self):
        """Fe 250 steel (lower fy) needs smaller spacing than Fe 415."""
        result_fe250 = shear.design_shear(
            vu_kn=100, b=250, d=450, fck=25, fy=250, asv=157, pt=0.5
        )
        result_fe415 = shear.design_shear(
            vu_kn=100, b=250, d=450, fck=25, fy=415, asv=157, pt=0.5
        )
        # Lower grade steel needs more closely spaced stirrups
        assert result_fe250.spacing <= result_fe415.spacing

    def test_fe500_gives_larger_spacing(self):
        """Fe 500 steel (higher fy) allows larger spacing than Fe 415."""
        result_fe415 = shear.design_shear(
            vu_kn=100, b=250, d=450, fck=25, fy=415, asv=157, pt=0.5
        )
        result_fe500 = shear.design_shear(
            vu_kn=100, b=250, d=450, fck=25, fy=500, asv=157, pt=0.5
        )
        # Higher grade steel allows wider spacing
        assert result_fe500.spacing >= result_fe415.spacing

    def test_fe250_still_safe(self):
        """Design with Fe 250 should still be safe."""
        result = shear.design_shear(
            vu_kn=80, b=250, d=450, fck=25, fy=250, asv=157, pt=0.5
        )
        assert result.is_safe is True


class TestDesignShearHandCalculated:
    """Hand-calculated verification tests for design_shear formulas.

    Validates the spacing calculation logic against manual calculations.
    """

    def test_spacing_formula_minimum_reinforcement(self):
        """When tv < tc, spacing uses minimum reinforcement formula.

        Formula: spacing = (0.87 * fy * asv) / (0.4 * b)
        Limited by min(spacing_calc, 0.75*d, 300)
        """
        # Low shear case: tv < tc (minimum reinforcement)
        # tv = 20000/(250*450) = 0.178 N/mm²
        # tc for M25, pt=1.0 ≈ 0.62 N/mm² (from IS 456 Table 19)
        # tv < tc, so minimum reinforcement applies
        # spacing_calc = (0.87*415*157)/(0.4*250) = 566.6mm
        # Limited by 0.75*450=337.5mm and 300mm → 300mm
        result = shear.design_shear(
            vu_kn=20, b=250, d=450, fck=25, fy=415, asv=157, pt=1.0
        )
        # Rounded down to practical spacing
        assert result.spacing == pytest.approx(300, abs=1)
        assert result.is_safe is True

    def test_spacing_formula_designed_reinforcement(self):
        """When tv > tc, spacing uses designed reinforcement formula.

        Formula: spacing = (0.87 * fy * asv * d) / (vus * 1000)
        where vus = Vu - tc*b*d
        """
        # High shear case: tv > tc
        # tv = 150000/(250*450) = 1.333 N/mm²
        # tc for M25, pt=0.5% ≈ 0.49 N/mm² (from IS 456 Table 19)
        # vus = (150000 - 0.49*250*450)/1000 = 94.875 kN
        # spacing_calc = (0.87*415*157*450)/94875 = 268.98mm
        # Limited by 0.75*450=337.5mm and 300mm → 268.98mm
        # Rounded down to 250mm (practical spacing)
        result = shear.design_shear(
            vu_kn=150, b=250, d=450, fck=25, fy=415, asv=157, pt=0.5
        )
        assert result.spacing == pytest.approx(250, abs=5)
        assert result.is_safe is True


class TestCalculateTvEdgeCases:
    """Additional edge cases for calculate_tv function."""

    def test_negative_dimensions_b_raises(self):
        """Negative width b should raise DimensionError."""
        with pytest.raises(DimensionError, match="beam width b"):
            shear.calculate_tv(vu_kn=100, b=-100, d=450)

    def test_negative_dimensions_d_raises(self):
        """Negative depth d should raise DimensionError."""
        with pytest.raises(DimensionError, match="effective depth d"):
            shear.calculate_tv(vu_kn=100, b=250, d=-100)

    def test_very_large_section(self):
        """Very large beam sections should work correctly."""
        # b=2000mm, d=3000mm, Vu=100kN
        # tv = 100*1000/(2000*3000) = 0.0167 N/mm²
        tv = shear.calculate_tv(vu_kn=100, b=2000, d=3000)
        assert tv == pytest.approx(0.0167, rel=0.01)

    def test_very_small_section(self):
        """Very small beam sections should work correctly."""
        # b=100mm, d=150mm, Vu=100kN
        # tv = 100*1000/(100*150) = 6.667 N/mm²
        tv = shear.calculate_tv(vu_kn=100, b=100, d=150)
        assert tv == pytest.approx(6.667, rel=0.01)


class TestDesignShearExtremePt:
    """Tests for extreme steel percentage (pt) values in design_shear.

    pt affects tc (permissible shear stress) from IS 456 Table 19.
    pt range: 0.15% (minimum) to 3.0% (maximum).
    """

    def test_very_low_pt(self):
        """Very low pt (0.15%) should still work."""
        result = shear.design_shear(
            vu_kn=100, b=250, d=450, fck=25, fy=415, asv=157, pt=0.15
        )
        # Should work, tc will be at minimum from table
        assert result.spacing > 0
        assert isinstance(result.is_safe, bool)

    def test_very_high_pt(self):
        """Very high pt (3.0%) gives higher tc than low pt."""
        result_low = shear.design_shear(
            vu_kn=100, b=250, d=450, fck=25, fy=415, asv=157, pt=0.15
        )
        result_high = shear.design_shear(
            vu_kn=100, b=250, d=450, fck=25, fy=415, asv=157, pt=3.0
        )
        # Higher pt → higher tc → potentially larger spacing
        assert result_high.spacing >= result_low.spacing

    def test_pt_zero_still_works(self):
        """pt=0 should return valid result (minimum tc from table)."""
        result = shear.design_shear(
            vu_kn=100, b=250, d=450, fck=25, fy=415, asv=157, pt=0.0
        )
        # Should use minimum tc value from IS 456 Table 19
        assert result.spacing > 0
        assert isinstance(result.is_safe, bool)


class TestDesignShearExtremeBeamSizes:
    """Tests with extreme beam dimensions.

    Validates spacing limits for very deep, very wide, and minimal beams.
    """

    def test_very_deep_beam(self):
        """Very deep beam: spacing respects 0.75*d limit but also 300mm max."""
        # b=250mm, d=2000mm (deep beam)
        # 0.75*d = 1500mm, but 300mm limit applies first
        result = shear.design_shear(
            vu_kn=100, b=250, d=2000, fck=25, fy=415, asv=157, pt=0.5
        )
        # Spacing cannot exceed 300mm (IS 456 Cl 26.5.1.5)
        assert result.spacing <= 300

    def test_very_wide_beam(self):
        """Very wide beam should have lower tv and be safe."""
        # b=1000mm, d=450mm (wide beam)
        result = shear.design_shear(
            vu_kn=100, b=1000, d=450, fck=25, fy=415, asv=157, pt=0.5
        )
        # Wide beam → lower tv → should be safe
        assert result.is_safe is True
        assert result.spacing > 0

    def test_minimal_beam(self):
        """Minimal beam dimensions should still work."""
        # b=150mm, d=200mm (small beam)
        result = shear.design_shear(
            vu_kn=50, b=150, d=200, fck=20, fy=415, asv=100, pt=0.5
        )
        # Should return valid result
        assert result.spacing > 0
        assert isinstance(result.is_safe, bool)


class TestEnhancedShearStrength:
    """Tests for enhanced_shear_strength (IS 456 Cl 40.3).

    When a concentrated load acts within 2d of a support face,
    τc may be enhanced: τc' = (2d/av) × τc, capped at τc,max.
    """

    # ── Benchmark cases (hand-verified) ──────────────────────────

    def test_case1_m25(self):
        """IS 456 Cl 40.3: M25, pt=0.50%, d=450mm, av=300mm.
        τc(M25, 0.50%) = 0.49, factor=2×450/300=3.0, τc'=1.47.
        """
        tc_prime = enhanced_shear_strength(fck=25, pt=0.50, d_mm=450, av_mm=300)
        assert tc_prime == pytest.approx(1.47, abs=0.02)

    def test_case2_m30(self):
        """IS 456 Cl 40.3: M30, pt=1.00%, d=500mm, av=400mm.
        τc(M30, 1.00%) = 0.66, factor=2×500/400=2.5, τc'=1.65.
        """
        tc_prime = enhanced_shear_strength(fck=30, pt=1.00, d_mm=500, av_mm=400)
        assert tc_prime == pytest.approx(1.65, abs=0.02)

    def test_case3_m20(self):
        """IS 456 Cl 40.3: M20, pt=0.25%, d=400mm, av=200mm.
        τc(M20, 0.25%) = 0.36, factor=2×400/200=4.0, τc'=1.44.
        """
        tc_prime = enhanced_shear_strength(fck=20, pt=0.25, d_mm=400, av_mm=200)
        assert tc_prime == pytest.approx(1.44, abs=0.02)

    def test_case4_m15(self):
        """IS 456 Cl 40.3: M15, pt=0.15%, d=300mm, av=100mm.
        τc(M15, 0.15%) = 0.28, factor=2×300/100=6.0, τc'=1.68.
        """
        tc_prime = enhanced_shear_strength(fck=15, pt=0.15, d_mm=300, av_mm=100)
        assert tc_prime == pytest.approx(1.68, abs=0.02)

    def test_case5_capped(self):
        """IS 456 Cl 40.3: M15, pt=2.00%, d=300mm, av=80mm — capped at τc,max.
        τc(M15, 2.00%) = 0.71, factor=2×300/80=7.5, τc'=5.325 → capped at 2.5.
        """
        tc_prime = enhanced_shear_strength(fck=15, pt=2.00, d_mm=300, av_mm=80)
        assert tc_prime == pytest.approx(2.50, abs=0.02)

    # ── Boundary cases ───────────────────────────────────────────

    def test_av_equals_2d(self):
        """av = 2d → factor = 1.0, returns base τc (no enhancement)."""
        tc_prime = enhanced_shear_strength(fck=25, pt=0.50, d_mm=450, av_mm=900)
        # Base τc for M25, pt=0.50% = 0.49
        assert tc_prime == pytest.approx(0.49, abs=0.02)

    def test_av_greater_than_2d(self):
        """av > 2d → no enhancement, returns base τc."""
        tc_prime = enhanced_shear_strength(fck=25, pt=0.50, d_mm=450, av_mm=1350)
        assert tc_prime == pytest.approx(0.49, abs=0.02)

    def test_av_equals_d(self):
        """av = d → factor = 2.0, returns 2×τc."""
        tc_prime = enhanced_shear_strength(fck=25, pt=0.50, d_mm=450, av_mm=450)
        # 2 × 0.49 = 0.98
        assert tc_prime == pytest.approx(0.98, abs=0.02)

    # ── Error cases ──────────────────────────────────────────────

    def test_av_zero_raises(self):
        """av_mm = 0 should raise DimensionError."""
        with pytest.raises(DimensionError):
            enhanced_shear_strength(fck=25, pt=0.50, d_mm=450, av_mm=0)

    def test_av_negative_raises(self):
        """av_mm < 0 should raise DimensionError."""
        with pytest.raises(DimensionError):
            enhanced_shear_strength(fck=25, pt=0.50, d_mm=450, av_mm=-100)

    def test_d_zero_raises(self):
        """d_mm = 0 should raise DimensionError."""
        with pytest.raises(DimensionError):
            enhanced_shear_strength(fck=25, pt=0.50, d_mm=0, av_mm=300)

    def test_d_negative_raises(self):
        """d_mm < 0 should raise DimensionError."""
        with pytest.raises(DimensionError):
            enhanced_shear_strength(fck=25, pt=0.50, d_mm=-450, av_mm=300)

    # ── Integration with design_shear ────────────────────────────

    def test_design_shear_without_av(self):
        """Existing design_shear call without av_mm works unchanged."""
        result = shear.design_shear(
            vu_kn=100, b=250, d=450, fck=25, fy=415, asv=157, pt=0.5
        )
        assert result.is_safe is True
        assert result.tc == pytest.approx(0.49, rel=0.05)

    def test_design_shear_with_av(self):
        """Passing av_mm enhances τc, which should increase spacing or keep safe."""
        result_no_av = shear.design_shear(
            vu_kn=100, b=250, d=450, fck=25, fy=415, asv=157, pt=0.5
        )
        result_with_av = shear.design_shear(
            vu_kn=100, b=250, d=450, fck=25, fy=415, asv=157, pt=0.5, av_mm=300
        )
        # Enhanced τc means concrete carries more shear → less stirrup demand
        assert result_with_av.tc > result_no_av.tc
        assert result_with_av.spacing >= result_no_av.spacing
