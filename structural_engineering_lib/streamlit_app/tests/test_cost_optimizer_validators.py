"""
Tests for cost optimizer validation helpers.
"""

import pytest
import math
from streamlit_app.utils.cost_optimizer_validators import (
    validate_beam_inputs,
    validate_design_result,
    safe_divide,
    safe_format_currency,
    safe_format_percent,
    ValidationResult,
)


class TestBeamInputsValidation:
    """Test beam inputs validation."""

    def test_valid_inputs(self):
        """Test validation passes for valid inputs."""
        inputs = {
            "mu_knm": 120.0,
            "vu_kn": 80.0,
            "b_mm": 300.0,
            "D_mm": 500.0,
            "d_mm": 450.0,
            "span_mm": 5000.0,
            "fck_nmm2": 25.0,
            "fy_nmm2": 500.0,
        }

        result = validate_beam_inputs(inputs)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_missing_required_key(self):
        """Test validation fails for missing keys."""
        inputs = {
            "mu_knm": 120.0,
            # Missing vu_kn
            "b_mm": 300.0,
        }

        result = validate_beam_inputs(inputs)
        assert not result.is_valid
        assert any("Missing required parameter" in e for e in result.errors)

    def test_negative_moment(self):
        """Test validation fails for negative moment."""
        inputs = {
            "mu_knm": -10.0,  # Invalid
            "vu_kn": 80.0,
            "b_mm": 300.0,
            "D_mm": 500.0,
            "d_mm": 450.0,
            "span_mm": 5000.0,
            "fck_nmm2": 25.0,
            "fy_nmm2": 500.0,
        }

        result = validate_beam_inputs(inputs)
        assert not result.is_valid
        assert any("Moment must be positive" in e for e in result.errors)

    def test_d_greater_than_D(self):
        """Test validation fails when d >= D."""
        inputs = {
            "mu_knm": 120.0,
            "vu_kn": 80.0,
            "b_mm": 300.0,
            "D_mm": 500.0,
            "d_mm": 500.0,  # Equal to D - invalid!
            "span_mm": 5000.0,
            "fck_nmm2": 25.0,
            "fy_nmm2": 500.0,
        }

        result = validate_beam_inputs(inputs)
        assert not result.is_valid
        assert any("must be less than total depth" in e for e in result.errors)

    def test_span_to_depth_too_small(self):
        """Test validation fails for unrealistic span/depth ratio."""
        inputs = {
            "mu_knm": 120.0,
            "vu_kn": 80.0,
            "b_mm": 300.0,
            "D_mm": 1000.0,  # Very deep
            "d_mm": 950.0,
            "span_mm": 2000.0,  # Short span -> L/D = 2
            "fck_nmm2": 25.0,
            "fy_nmm2": 500.0,
        }

        result = validate_beam_inputs(inputs)
        assert not result.is_valid
        assert any("Span/depth ratio" in e and "too small" in e for e in result.errors)

    def test_nan_values(self):
        """Test validation fails for NaN values."""
        inputs = {
            "mu_knm": float("nan"),
            "vu_kn": 80.0,
            "b_mm": 300.0,
            "D_mm": 500.0,
            "d_mm": 450.0,
            "span_mm": 5000.0,
            "fck_nmm2": 25.0,
            "fy_nmm2": 500.0,
        }

        result = validate_beam_inputs(inputs)
        assert not result.is_valid
        assert any("NaN or Inf" in e for e in result.errors)

    def test_string_values(self):
        """Test validation fails for string values."""
        inputs = {
            "mu_knm": "120",  # String instead of number
            "vu_kn": 80.0,
            "b_mm": 300.0,
            "D_mm": 500.0,
            "d_mm": 450.0,
            "span_mm": 5000.0,
            "fck_nmm2": 25.0,
            "fy_nmm2": 500.0,
        }

        result = validate_beam_inputs(inputs)
        assert not result.is_valid
        assert any("must be numeric" in e for e in result.errors)


class TestDesignResultValidation:
    """Test design result validation."""

    def test_valid_design_result(self):
        """Test validation passes for valid design result."""
        result = {
            "design": {
                "flexure": {
                    "tension_steel": {
                        "num": 3,
                        "dia": 20,
                        "area": 942.0,
                    },
                    "_bar_alternatives": [
                        {"num": 4, "dia": 16, "area": 804.0},
                        {"num": 2, "dia": 25, "area": 982.0},
                    ],
                }
            }
        }

        validation = validate_design_result(result)
        assert validation.is_valid
        assert len(validation.errors) == 0

    def test_missing_design_key(self):
        """Test validation fails when design key missing."""
        result = {"flexure": {}}  # No 'design' wrapper

        validation = validate_design_result(result)
        assert not validation.is_valid
        assert any("missing 'design' key" in e for e in validation.errors)

    def test_missing_flexure_key(self):
        """Test validation fails when flexure key missing."""
        result = {
            "design": {
                # No 'flexure' key
            }
        }

        validation = validate_design_result(result)
        assert not validation.is_valid
        assert any("missing 'flexure' analysis" in e for e in validation.errors)

    def test_empty_alternatives(self):
        """Test validation fails for empty alternatives list."""
        result = {
            "design": {
                "flexure": {
                    "tension_steel": {"num": 3, "dia": 20, "area": 942.0},
                    "_bar_alternatives": [],  # Empty!
                }
            }
        }

        validation = validate_design_result(result)
        assert not validation.is_valid
        assert any("empty list" in e for e in validation.errors)

    def test_wrong_type(self):
        """Test validation fails for wrong types."""
        result = "not a dict"

        validation = validate_design_result(result)
        assert not validation.is_valid
        assert any("must be dict" in e for e in validation.errors)


class TestSafeDivide:
    """Test safe division."""

    def test_normal_division(self):
        """Test normal division works."""
        result = safe_divide(10, 2)
        assert result == 5.0

    def test_zero_denominator(self):
        """Test zero denominator returns default."""
        result = safe_divide(10, 0, default=0.0)
        assert result == 0.0

    def test_zero_denominator_nan_default(self):
        """Test zero denominator can return NaN."""
        result = safe_divide(10, 0, default=float("nan"))
        assert math.isnan(result)

    def test_nan_denominator(self):
        """Test NaN denominator returns default."""
        result = safe_divide(10, float("nan"), default=0.0)
        assert result == 0.0

    def test_inf_denominator(self):
        """Test Inf denominator returns default."""
        result = safe_divide(10, float("inf"), default=0.0)
        assert result == 0.0

    def test_result_is_nan(self):
        """Test result NaN returns default."""
        # 0/0 = NaN
        result = safe_divide(0, 0, default=0.0)
        assert result == 0.0


class TestSafeFormatCurrency:
    """Test safe currency formatting."""

    def test_normal_value(self):
        """Test normal value formatting."""
        assert safe_format_currency(1234.56) == "₹1,235"

    def test_negative_value(self):
        """Test negative value formatting."""
        assert safe_format_currency(-1234.56) == "-₹1,235"

    def test_zero(self):
        """Test zero formatting."""
        assert safe_format_currency(0) == "₹0"

    def test_nan(self):
        """Test NaN returns N/A."""
        assert safe_format_currency(float("nan")) == "N/A"

    def test_inf(self):
        """Test Inf returns N/A."""
        assert safe_format_currency(float("inf")) == "N/A"

    def test_string(self):
        """Test string returns Invalid."""
        assert safe_format_currency("1234") == "Invalid"

    def test_none(self):
        """Test None returns Invalid."""
        assert safe_format_currency(None) == "Invalid"


class TestSafeFormatPercent:
    """Test safe percentage formatting."""

    def test_normal_value(self):
        """Test normal value formatting."""
        assert safe_format_percent(0.4523) == "45.23%"

    def test_zero(self):
        """Test zero formatting."""
        assert safe_format_percent(0) == "0.00%"

    def test_one(self):
        """Test 100% formatting."""
        assert safe_format_percent(1.0) == "100.00%"

    def test_nan(self):
        """Test NaN returns N/A."""
        assert safe_format_percent(float("nan")) == "N/A"

    def test_inf(self):
        """Test Inf returns N/A."""
        assert safe_format_percent(float("inf")) == "N/A"

    def test_string(self):
        """Test string returns Invalid."""
        assert safe_format_percent("45%") == "Invalid"


class TestValidationResult:
    """Test ValidationResult class."""

    def test_bool_conversion_valid(self):
        """Test ValidationResult with is_valid=True is truthy."""
        result = ValidationResult(True, [])
        assert bool(result) is True
        assert result  # Directly as bool

    def test_bool_conversion_invalid(self):
        """Test ValidationResult with is_valid=False is falsy."""
        result = ValidationResult(False, ["error1", "error2"])
        assert bool(result) is False
        assert not result  # Directly as bool

    def test_errors_list(self):
        """Test errors list is accessible."""
        errors = ["error1", "error2"]
        result = ValidationResult(False, errors)
        assert result.errors == errors
        assert len(result.errors) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
