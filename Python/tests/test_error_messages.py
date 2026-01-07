# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for error message templates."""

import pytest

from structural_lib import error_messages


class TestDimensionTemplates:
    """Tests for dimension error message templates."""

    def test_dimension_too_small(self):
        """Test dimension too small template."""
        msg = error_messages.dimension_too_small("width", 150, 200, "Cl. 26.5.1.1")
        assert "Width 150mm" in msg
        assert "below minimum 200mm" in msg
        assert "Cl. 26.5.1.1" in msg
        assert "Increase width to at least 200mm" in msg

    def test_dimension_too_small_without_clause(self):
        """Test dimension too small without clause reference."""
        msg = error_messages.dimension_too_small("depth", 100, 150)
        assert "Depth 100mm" in msg
        assert "below minimum 150mm" in msg
        assert "Cl." not in msg

    def test_dimension_too_large(self):
        """Test dimension too large template."""
        msg = error_messages.dimension_too_large("spacing", 500, 300, "Cl. 26.5.1.6")
        assert "Spacing 500mm" in msg
        assert "exceeds maximum 300mm" in msg
        assert "Reduce spacing to at most 300mm" in msg

    def test_dimension_negative(self):
        """Test negative dimension template."""
        msg = error_messages.dimension_negative("cover", -10)
        assert "Cover -10mm" in msg
        assert "cannot be negative" in msg
        assert "Provide a positive value" in msg

    def test_dimension_relationship_invalid(self):
        """Test dimension relationship template."""
        msg = error_messages.dimension_relationship_invalid(
            "overall depth D", 400, "effective depth d", 450, "must be greater than"
        )
        assert "overall depth D 400mm" in msg
        assert "effective depth d 450mm" in msg
        assert "must be greater than" in msg


class TestMaterialTemplates:
    """Tests for material error message templates."""

    def test_material_grade_invalid(self):
        """Test invalid material grade template."""
        msg = error_messages.material_grade_invalid(
            "concrete", 35, [20, 25, 30, 40, 45, 50]
        )
        assert "Concrete grade 35MPa" in msg
        assert "not a standard grade" in msg
        assert "[20, 25, 30, 40, 45, 50]" in msg
        assert "Table 2" in msg

    def test_material_property_out_of_range_both_bounds(self):
        """Test material property out of range with both bounds."""
        msg = error_messages.material_property_out_of_range(
            "yield strength", 600, 250, 550, "MPa"
        )
        assert "Yield strength 600MPa" in msg
        assert "out of valid range" in msg
        assert "(250-550MPa)" in msg

    def test_material_property_out_of_range_min_only(self):
        """Test material property out of range with minimum only."""
        msg = error_messages.material_property_out_of_range(
            "modulus", 5000, min_value=20000, unit="MPa"
        )
        assert "Modulus 5000MPa" in msg
        assert "(minimum 20000MPa)" in msg

    def test_material_property_out_of_range_max_only(self):
        """Test material property out of range with maximum only."""
        msg = error_messages.material_property_out_of_range(
            "slump", 200, max_value=150, unit="mm"
        )
        assert "Slump 200mm" in msg
        assert "(maximum 150mm)" in msg


class TestDesignConstraintTemplates:
    """Tests for design constraint error message templates."""

    def test_capacity_exceeded(self):
        """Test capacity exceeded template."""
        msg = error_messages.capacity_exceeded(
            "Moment Mu",
            250,
            "Mu,lim",
            200,
            [
                "Increase section depth",
                "Use compression reinforcement",
                "Increase concrete grade",
            ],
            "Cl. 38.1",
        )
        assert "Moment Mu 250kN·m" in msg
        assert "exceeds section capacity Mu,lim 200kN·m" in msg
        assert "Cl. 38.1" in msg
        assert "(1) Increase section depth" in msg
        assert "(2) Use compression reinforcement" in msg
        assert "(3) Increase concrete grade" in msg

    def test_capacity_exceeded_no_suggestions(self):
        """Test capacity exceeded without suggestions."""
        msg = error_messages.capacity_exceeded("Shear Vu", 150, "Vu,max", 120, [])
        assert "Shear Vu 150kN·m" in msg
        assert "exceeds section capacity Vu,max 120kN·m" in msg
        assert "Options" not in msg

    def test_reinforcement_spacing_insufficient(self):
        """Test reinforcement spacing insufficient template."""
        msg = error_messages.reinforcement_spacing_insufficient(
            230, 280, 4, 20, "Cl. 26.3"
        )
        assert "Cannot fit 4-#20mm bars" in msg
        assert "available width 230mm" in msg
        assert "requires 280mm" in msg
        assert "Cl. 26.3" in msg
        assert "(1) Reduce bar count" in msg
        assert "(2) Use smaller diameter" in msg
        assert "(3) Increase section width" in msg


class TestComplianceTemplates:
    """Tests for compliance error message templates."""

    def test_minimum_reinforcement_not_met(self):
        """Test minimum reinforcement template."""
        msg = error_messages.minimum_reinforcement_not_met(
            950, 1100, "tension steel", "Cl. 26.5.1.1"
        )
        assert "Tension steel 950mm²" in msg
        assert "below minimum 1100mm²" in msg
        assert "Cl. 26.5.1.1" in msg
        assert "Increase reinforcement" in msg

    def test_maximum_reinforcement_exceeded(self):
        """Test maximum reinforcement template."""
        msg = error_messages.maximum_reinforcement_exceeded(
            5000, 4000, "tension steel", "Cl. 26.5.1.2"
        )
        assert "Tension steel 5000mm²" in msg
        assert "exceeds maximum 4000mm²" in msg
        assert "Cl. 26.5.1.2" in msg
        assert "Reduce reinforcement or increase section size" in msg

    def test_spacing_limit_exceeded(self):
        """Test spacing limit exceeded template."""
        msg = error_messages.spacing_limit_exceeded(450, 300, "stirrup", "Cl. 26.5.1.6")
        assert "Stirrup spacing 450mm" in msg
        assert "exceeds maximum 300mm" in msg
        assert "Cl. 26.5.1.6" in msg
        assert "Reduce spacing" in msg


class TestCalculationTemplates:
    """Tests for calculation error message templates."""

    def test_convergence_failed(self):
        """Test convergence failed template."""
        msg = error_messages.convergence_failed(
            "neutral axis iteration", 100, 0.001, 0.015
        )
        assert "Neutral axis iteration" in msg
        assert "did not converge" in msg
        assert "100 iterations" in msg
        assert "tolerance=0.001" in msg
        assert "current error=0.015" in msg
        assert "Check input values" in msg

    def test_convergence_failed_without_current_error(self):
        """Test convergence failed without current error."""
        msg = error_messages.convergence_failed("iteration", 50, 0.01)
        assert "50 iterations" in msg
        assert "tolerance=0.01" in msg
        assert "current error" not in msg

    def test_numerical_instability(self):
        """Test numerical instability template."""
        msg = error_messages.numerical_instability(
            "division", "xu", "denominator too close to zero"
        )
        assert "Numerical instability in division" in msg
        assert "xu" in msg
        assert "denominator too close to zero" in msg
        assert "Check input values" in msg


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_format_value_with_unit(self):
        """Test value formatting with unit."""
        result = error_messages.format_value_with_unit(123.456, "mm", 2)
        assert result == "123.46mm"

    def test_format_value_with_unit_default_precision(self):
        """Test value formatting with default precision."""
        result = error_messages.format_value_with_unit(123.456, "MPa")
        assert result == "123.46MPa"

    def test_format_list_empty(self):
        """Test format_list with empty list."""
        result = error_messages.format_list([])
        assert result == ""

    def test_format_list_single_item(self):
        """Test format_list with single item."""
        result = error_messages.format_list([20])
        assert result == "20"

    def test_format_list_two_items(self):
        """Test format_list with two items."""
        result = error_messages.format_list([20, 25])
        assert result == "20 or 25"

    def test_format_list_multiple_items(self):
        """Test format_list with multiple items."""
        result = error_messages.format_list([20, 25, 30, 35])
        assert result == "20, 25, 30, or 35"

    def test_format_list_with_and(self):
        """Test format_list with 'and' conjunction."""
        result = error_messages.format_list(
            ["check dimensions", "verify materials"], "and"
        )
        assert result == "check dimensions and verify materials"


class TestRealWorldExamples:
    """Tests demonstrating real-world usage."""

    def test_beam_width_validation(self):
        """Test typical beam width validation error."""
        b_mm = 150
        msg = error_messages.dimension_too_small(
            "beam width", b_mm, 200, "Cl. 26.5.1.1"
        )

        assert "Beam width 150mm" in msg
        assert "below minimum 200mm" in msg
        assert "Increase beam width to at least 200mm" in msg

    def test_concrete_grade_validation(self):
        """Test typical concrete grade validation error."""
        msg = error_messages.material_grade_invalid(
            "concrete", 35, [20, 25, 30, 40, 45, 50]
        )

        assert "35MPa" in msg
        assert "not a standard grade" in msg

    def test_moment_capacity_exceeded(self):
        """Test typical moment capacity exceeded error."""
        msg = error_messages.capacity_exceeded(
            "Moment Mu",
            250.5,
            "Mu,lim",
            200.2,
            ["Increase depth", "Add compression steel"],
            "Cl. 38.1",
        )

        assert "250.5kN·m" in msg
        assert "200.2kN·m" in msg
        assert "(1) Increase depth" in msg
        assert "(2) Add compression steel" in msg

    def test_minimum_steel_violation(self):
        """Test typical minimum steel violation."""
        msg = error_messages.minimum_reinforcement_not_met(
            850.0, 1100.0, "tension steel", "Cl. 26.5.1.1"
        )

        assert "850.0mm²" in msg
        assert "1100.0mm²" in msg
        assert "Increase reinforcement" in msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
