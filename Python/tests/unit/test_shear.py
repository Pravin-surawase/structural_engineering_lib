"""
Dedicated unit tests for shear module.

Tests cover:
- calculate_tv: nominal shear stress calculation
- design_shear: full shear design per IS 456

Reference: IS 456:2000 Clause 40
"""

import pytest

from structural_lib import shear
from structural_lib.errors import DimensionError


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
