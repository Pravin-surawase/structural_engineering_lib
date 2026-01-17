"""
Unit Tests for Validation Utilities
====================================

Tests for utils/validation.py module.

Test Coverage:
- validate_dimension() - Range checking
- validate_materials() - Material compatibility
- format_error_message() - Error formatting

Author: STREAMLIT UI SPECIALIST (Agent 6)
Phase: STREAMLIT-FIX-001 Enhancement
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.validation import (
    validate_dimension,
    validate_materials,
    format_error_message,
)


class TestDimensionValidation:
    """Test dimension validation logic"""

    def test_valid_dimension_in_range(self):
        """Test valid dimension passes validation"""
        is_valid, error = validate_dimension(
            300.0, min_val=100.0, max_val=1000.0, name="Width"
        )
        assert is_valid is True
        assert error == ""

    def test_dimension_below_minimum(self):
        """Test dimension below minimum fails"""
        is_valid, error = validate_dimension(
            50.0, min_val=100.0, max_val=1000.0, name="Width"
        )
        assert is_valid is False
        assert "width" in error.lower() or "100" in error

    def test_dimension_above_maximum(self):
        """Test dimension above maximum fails"""
        is_valid, error = validate_dimension(
            1500.0, min_val=100.0, max_val=1000.0, name="Width"
        )
        assert is_valid is False
        assert "width" in error.lower() or "1000" in error

    def test_dimension_at_boundaries(self):
        """Test dimension at exact boundaries"""
        # At minimum
        is_valid, error = validate_dimension(
            100.0, min_val=100.0, max_val=1000.0, name="Width"
        )
        assert is_valid is True

        # At maximum
        is_valid, error = validate_dimension(
            1000.0, min_val=100.0, max_val=1000.0, name="Width"
        )
        assert is_valid is True

    def test_negative_dimension_rejected(self):
        """Test negative dimensions are rejected"""
        is_valid, error = validate_dimension(
            -100.0, min_val=0.0, max_val=1000.0, name="Width"
        )
        assert is_valid is False

    def test_zero_dimension_handling(self):
        """Test zero dimension handling"""
        # Zero may be valid if min is 0
        is_valid, error = validate_dimension(
            0.0, min_val=0.0, max_val=1000.0, name="Width"
        )
        assert is_valid is True


class TestMaterialValidation:
    """Test material validation logic"""

    def test_valid_material_combination(self):
        """Test valid concrete and steel combination"""
        is_valid, error = validate_materials(fck=25.0, fy=500.0)
        assert is_valid is True
        assert error == ""

    def test_typical_concrete_grades(self):
        """Test typical concrete grades"""
        for fck in [20, 25, 30, 35, 40]:
            is_valid, error = validate_materials(fck=float(fck), fy=500.0)
            assert is_valid is True

    def test_typical_steel_grades(self):
        """Test typical steel grades"""
        for fy in [415, 500, 550]:
            is_valid, error = validate_materials(fck=25.0, fy=float(fy))
            assert is_valid is True

    def test_high_strength_combinations(self):
        """Test high strength material combinations"""
        is_valid, error = validate_materials(fck=60.0, fy=550.0)
        assert is_valid is True


class TestErrorFormatting:
    """Test error message formatting"""

    def test_format_dimension_error(self):
        """Test dimension error formatting"""
        msg = format_error_message("DIMENSION", "Width must be >= 100mm")
        assert "dimension" in msg.lower()
        assert "width" in msg.lower()

    def test_format_material_error(self):
        """Test material error formatting"""
        msg = format_error_message("MATERIAL", "Invalid concrete grade")
        assert "material" in msg.lower()
        assert "concrete" in msg.lower()

    def test_format_load_error(self):
        """Test load error formatting"""
        msg = format_error_message("LOAD", "Moment cannot be negative")
        assert "load" in msg.lower()
        assert "moment" in msg.lower()

    def test_format_design_error(self):
        """Test design error formatting"""
        msg = format_error_message("DESIGN", "Reinforcement insufficient")
        assert "design" in msg.lower()
        assert "reinforcement" in msg.lower()

    def test_format_unknown_error(self):
        """Test unknown error type formatting"""
        msg = format_error_message("UNKNOWN", "Something went wrong")
        assert "something went wrong" in msg.lower()

    def test_error_message_has_icon(self):
        """Test error messages include icons"""
        msg = format_error_message("DIMENSION", "Test error")
        # Should have some kind of emoji/icon
        assert any(char in msg for char in ["❌", "⚠️", "🚫"])


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_very_small_dimensions(self):
        """Test very small positive dimensions"""
        is_valid, error = validate_dimension(
            0.001, min_val=0.0, max_val=1.0, name="Test"
        )
        assert is_valid is True

    def test_very_large_dimensions(self):
        """Test very large dimensions"""
        is_valid, error = validate_dimension(
            10000.0, min_val=0.0, max_val=100000.0, name="Test"
        )
        assert is_valid is True

    def test_equal_min_max_boundary(self):
        """Test when min equals max"""
        is_valid, error = validate_dimension(
            100.0, min_val=100.0, max_val=100.0, name="Test"
        )
        assert is_valid is True

    def test_dimension_validation_precision(self):
        """Test floating point precision handling"""
        # Test values very close to boundaries
        is_valid, error = validate_dimension(
            100.0001, min_val=100.0, max_val=1000.0, name="Test"
        )
        assert is_valid is True

        is_valid, error = validate_dimension(
            999.9999, min_val=100.0, max_val=1000.0, name="Test"
        )
        assert is_valid is True


class TestValidationConsistency:
    """Test validation behaves consistently"""

    def test_same_input_same_output(self):
        """Test validation is deterministic"""
        for _ in range(10):
            is_valid1, error1 = validate_dimension(
                300.0, min_val=100.0, max_val=1000.0, name="Width"
            )
            is_valid2, error2 = validate_dimension(
                300.0, min_val=100.0, max_val=1000.0, name="Width"
            )
            assert is_valid1 == is_valid2
            assert error1 == error2

    def test_material_validation_consistent(self):
        """Test material validation is consistent"""
        for _ in range(10):
            is_valid1, error1 = validate_materials(fck=25.0, fy=500.0)
            is_valid2, error2 = validate_materials(fck=25.0, fy=500.0)
            assert is_valid1 == is_valid2
            assert error1 == error2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
