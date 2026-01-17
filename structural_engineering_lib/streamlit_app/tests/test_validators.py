"""
Tests for Input Validators
===========================

Comprehensive tests for utils/validators.py input validation functions.

Author: STREAMLIT UI SPECIALIST (Agent 6)
Status: ✅ IMPL-004 Part 2 Tests
Created: 2026-01-09
"""

import pytest
from streamlit_app.utils.validators import (
    ValidationResult,
    validate_beam_inputs,
    validate_material_inputs,
    validate_loading_inputs,
    sanitize_numeric_input,
    validate_reinforcement_inputs,
)


class TestBeamInputValidation:
    """Tests for beam geometry validation"""

    def test_valid_beam_inputs(self):
        """Test that valid inputs pass validation"""
        result = validate_beam_inputs(
            span_mm=5000,
            width_mm=300,
            depth_mm=500,
            cover_mm=30,
        )
        assert result.is_valid
        assert len(result.errors) == 0

    def test_span_too_small(self):
        """Test span below minimum"""
        result = validate_beam_inputs(
            span_mm=500,  # <1000mm
            width_mm=300,
            depth_mm=500,
            cover_mm=30,
        )
        # Small span triggers warning, not error (valid but unusual)
        assert result.is_valid
        assert len(result.warnings) > 0
        assert any("short span" in warn.lower() for warn in result.warnings)

    def test_width_below_is456_minimum(self):
        """Test width below IS 456 minimum (150mm)"""
        result = validate_beam_inputs(
            span_mm=5000,
            width_mm=100,  # <150mm
            depth_mm=500,
            cover_mm=30,
        )
        assert not result.is_valid
        assert any("150mm" in err and "26.5.1.1" in err for err in result.errors)

    def test_depth_too_shallow(self):
        """Test depth below practical minimum"""
        result = validate_beam_inputs(
            span_mm=5000,
            width_mm=300,
            depth_mm=150,  # <200mm
            cover_mm=30,
        )
        assert not result.is_valid
        assert any("200mm" in err for err in result.errors)

    def test_excessive_span_depth_ratio(self):
        """Test span/depth ratio exceeds limit"""
        result = validate_beam_inputs(
            span_mm=10000,
            width_mm=300,
            depth_mm=300,  # Span/d = 33 > 30
            cover_mm=30,
        )
        assert not result.is_valid
        assert any("Span/Depth ratio" in err for err in result.errors)
        assert result.suggestion is not None

    def test_low_depth_width_ratio_warning(self):
        """Test warning for low d/b ratio"""
        result = validate_beam_inputs(
            span_mm=5000,
            width_mm=500,
            depth_mm=400,  # d/b = 0.8 < 1.0
            cover_mm=30,
        )
        # May still be valid, but should have warning
        assert len(result.warnings) > 0
        assert any("ratio" in warn.lower() for warn in result.warnings)

    def test_insufficient_cover(self):
        """Test cover below IS 456 minimum"""
        result = validate_beam_inputs(
            span_mm=5000,
            width_mm=300,
            depth_mm=500,
            cover_mm=15,  # <20mm
        )
        assert not result.is_valid
        assert any("20mm" in err and "26.4.2" in err for err in result.errors)

    def test_excessive_cover_warning(self):
        """Test warning for very large cover"""
        result = validate_beam_inputs(
            span_mm=5000,
            width_mm=300,
            depth_mm=500,
            cover_mm=100,  # >75mm
        )
        assert len(result.warnings) > 0
        assert any("cover" in warn.lower() for warn in result.warnings)


class TestMaterialInputValidation:
    """Tests for material properties validation"""

    def test_valid_material_grades(self):
        """Test standard material grades"""
        result = validate_material_inputs(fck=25, fy=415)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_concrete_below_minimum(self):
        """Test concrete grade below M15"""
        result = validate_material_inputs(fck=10, fy=415)
        assert not result.is_valid
        assert any("M15" in err for err in result.errors)

    def test_concrete_above_is456_range(self):
        """Test concrete grade above M50"""
        result = validate_material_inputs(fck=60, fy=415)
        assert not result.is_valid
        assert any(
            "M50" in err or "high-strength" in err.lower() for err in result.errors
        )

    def test_steel_below_minimum(self):
        """Test steel grade below Fe 250"""
        result = validate_material_inputs(fck=25, fy=200)
        assert not result.is_valid
        assert any("Fe 250" in err for err in result.errors)

    def test_steel_above_is456_range(self):
        """Test steel grade above Fe 550"""
        result = validate_material_inputs(fck=25, fy=600)
        assert not result.is_valid
        assert any("550" in err for err in result.errors)

    def test_non_standard_concrete_grade_warning(self):
        """Test warning for non-standard concrete grade"""
        result = validate_material_inputs(fck=27, fy=415)
        # Should be valid but with warning
        assert result.is_valid
        assert len(result.warnings) > 0
        assert any("not a standard grade" in warn for warn in result.warnings)

    def test_non_standard_steel_grade_warning(self):
        """Test warning for non-standard steel grade"""
        result = validate_material_inputs(fck=25, fy=450)
        assert result.is_valid
        assert len(result.warnings) > 0


class TestLoadingInputValidation:
    """Tests for loading validation"""

    def test_valid_loading(self):
        """Test typical loading values"""
        result = validate_loading_inputs(
            dead_load_kn_m=20.0,
            live_load_kn_m=15.0,
        )
        assert result.is_valid
        assert len(result.errors) == 0

    def test_negative_dead_load(self):
        """Test negative dead load rejected"""
        result = validate_loading_inputs(
            dead_load_kn_m=-10.0,
            live_load_kn_m=15.0,
        )
        assert not result.is_valid
        assert any("negative" in err.lower() for err in result.errors)

    def test_negative_live_load(self):
        """Test negative live load rejected"""
        result = validate_loading_inputs(
            dead_load_kn_m=20.0,
            live_load_kn_m=-5.0,
        )
        assert not result.is_valid

    def test_zero_dead_load_warning(self):
        """Test zero dead load triggers warning"""
        result = validate_loading_inputs(
            dead_load_kn_m=0.0,
            live_load_kn_m=15.0,
        )
        assert result.is_valid  # Not an error, but warning
        assert len(result.warnings) > 0

    def test_excessive_total_load_warning(self):
        """Test very high total load triggers warning"""
        result = validate_loading_inputs(
            dead_load_kn_m=800.0,
            live_load_kn_m=300.0,  # Total > 1000
        )
        assert len(result.warnings) > 0
        assert any("Total load" in warn or "1000" in warn for warn in result.warnings)

    def test_unusual_dl_ll_ratio_warning(self):
        """Test unusual DL/LL ratio triggers warning"""
        result = validate_loading_inputs(
            dead_load_kn_m=50.0,
            live_load_kn_m=5.0,  # Ratio = 10 > 5
        )
        assert len(result.warnings) > 0
        assert any("ratio" in warn.lower() for warn in result.warnings)


class TestNumericInputSanitization:
    """Tests for numeric input sanitization"""

    def test_valid_numeric_string(self):
        """Test valid numeric string converted correctly"""
        value, error = sanitize_numeric_input("5000", 0, 10000, 3000, "span")
        assert value == 5000.0
        assert error is None

    def test_invalid_string_uses_default(self):
        """Test invalid string falls back to default"""
        value, error = sanitize_numeric_input("invalid", 0, 10000, 3000, "span")
        assert value == 3000.0
        assert error is not None
        assert "Invalid" in error

    def test_value_below_minimum_clamped(self):
        """Test value below minimum is clamped"""
        value, error = sanitize_numeric_input(-500, 0, 10000, 3000, "span")
        assert value == 0.0
        assert error is not None
        assert "below minimum" in error

    def test_value_above_maximum_clamped(self):
        """Test value above maximum is clamped"""
        value, error = sanitize_numeric_input(15000, 0, 10000, 3000, "span")
        assert value == 10000.0
        assert error is not None
        assert "exceeds maximum" in error

    def test_value_within_range(self):
        """Test value within range passes through"""
        value, error = sanitize_numeric_input(5000, 0, 10000, 3000, "span")
        assert value == 5000.0
        assert error is None

    def test_float_conversion(self):
        """Test float string converted correctly"""
        value, error = sanitize_numeric_input("250.5", 0, 1000, 500, "width")
        assert value == 250.5
        assert error is None

    def test_none_value_uses_default(self):
        """Test None value falls back to default"""
        value, error = sanitize_numeric_input(None, 0, 1000, 500, "width")
        assert value == 500.0
        assert error is not None


class TestReinforcementInputValidation:
    """Tests for reinforcement details validation"""

    def test_valid_reinforcement(self):
        """Test valid reinforcement details"""
        result = validate_reinforcement_inputs(
            main_bar_dia=16,
            num_bars=4,
            stirrup_dia=8,
            stirrup_spacing=150.0,
        )
        assert result.is_valid
        assert len(result.errors) == 0

    def test_non_standard_bar_size(self):
        """Test non-standard bar size rejected"""
        result = validate_reinforcement_inputs(
            main_bar_dia=15,  # Not standard
            num_bars=4,
            stirrup_dia=8,
            stirrup_spacing=150.0,
        )
        assert not result.is_valid
        assert any("not standard" in err for err in result.errors)

    def test_too_few_bars(self):
        """Test minimum 2 bars required"""
        result = validate_reinforcement_inputs(
            main_bar_dia=16,
            num_bars=1,  # <2
            stirrup_dia=8,
            stirrup_spacing=150.0,
        )
        assert not result.is_valid
        assert any("Minimum 2 bars" in err for err in result.errors)

    def test_excessive_stirrup_spacing(self):
        """Test stirrup spacing > 300mm triggers warning"""
        result = validate_reinforcement_inputs(
            main_bar_dia=16,
            num_bars=4,
            stirrup_dia=8,
            stirrup_spacing=350.0,  # >300mm
        )
        assert len(result.warnings) > 0
        assert any("300mm" in warn for warn in result.warnings)

    def test_minimum_stirrup_spacing(self):
        """Test stirrup spacing < 75mm rejected"""
        result = validate_reinforcement_inputs(
            main_bar_dia=16,
            num_bars=4,
            stirrup_dia=8,
            stirrup_spacing=50.0,  # <75mm
        )
        assert not result.is_valid
        assert any("75mm" in err for err in result.errors)

    def test_small_main_bar_warning(self):
        """Test main bars < 12mm triggers warning"""
        result = validate_reinforcement_inputs(
            main_bar_dia=10,  # <12mm
            num_bars=4,
            stirrup_dia=8,
            stirrup_spacing=150.0,
        )
        # Valid but should warn
        assert len(result.warnings) > 0
        assert any("12mm" in warn for warn in result.warnings)
