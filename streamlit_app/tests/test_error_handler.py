"""
Tests for Error Handler
=========================

Comprehensive unit tests for error handling utilities.

Test Coverage:
- Error message creation functions
- Validation functions
- Error display functions
- Decorator functionality
- Edge cases

Author: STREAMLIT UI SPECIALIST (Agent 6)
Phase: STREAMLIT-IMPL-009
"""

import pytest
from utils.error_handler import (
    ErrorSeverity,
    ErrorMessage,
    create_dimension_error,
    create_material_error,
    create_load_error,
    create_design_failure_error,
    create_compliance_error,
    create_convergence_error,
    create_input_validation_error,
    create_generic_error,
    validate_dimension_range,
    validate_material_grades,
    validate_load_value,
    validate_beam_inputs,
)


# =============================================================================
# Test Error Message Creation
# =============================================================================

class TestDimensionErrors:
    """Test dimension error message creation"""

    def test_dimension_too_small(self):
        """Test error message for dimension below minimum"""
        error = create_dimension_error("Width", 150, 200, 1000, "mm")

        assert error.severity == ErrorSeverity.ERROR
        assert "Width" in error.title
        assert "150" in error.message
        assert "200" in error.message
        assert len(error.fix_suggestions) >= 2
        assert any("increase" in s.lower() for s in error.fix_suggestions)

    def test_dimension_too_large(self):
        """Test error message for dimension above maximum"""
        error = create_dimension_error("Span", 15000, 1000, 12000, "mm")

        assert error.severity == ErrorSeverity.ERROR
        assert "Span" in error.title
        assert "15000" in error.message or "15,000" in error.message
        assert "12000" in error.message or "12,000" in error.message
        assert len(error.fix_suggestions) >= 2
        assert any("reduce" in s.lower() for s in error.fix_suggestions)

    def test_dimension_error_formatting(self):
        """Test number formatting in error messages"""
        error = create_dimension_error("Depth", 5000, 250, 2000, "mm")

        # Check that numbers are formatted with commas
        assert "5,000" in error.message or "5000" in error.message
        assert error.technical_details is not None


class TestMaterialErrors:
    """Test material error message creation"""

    def test_invalid_concrete_grade(self):
        """Test error for invalid concrete grade"""
        error = create_material_error(27, 500)  # M27 is not standard

        assert error.severity == ErrorSeverity.ERROR
        assert "Material" in error.title
        assert "27" in error.message
        assert len(error.fix_suggestions) >= 2
        assert error.clause_reference is not None

    def test_invalid_steel_grade(self):
        """Test error for invalid steel grade"""
        error = create_material_error(25, 450)  # Fe450 is not standard

        assert error.severity == ErrorSeverity.ERROR
        assert "450" in error.message
        assert any("Fe500" in s for s in error.fix_suggestions)

    def test_both_materials_invalid(self):
        """Test error when both materials are invalid"""
        error = create_material_error(27, 450)

        assert "27" in error.message
        assert "450" in error.message
        assert len(error.fix_suggestions) >= 2


class TestLoadErrors:
    """Test load error message creation"""

    def test_excessive_moment(self):
        """Test error for excessive moment"""
        error = create_load_error("Moment", 5500, 5000, "kNm")

        assert error.severity == ErrorSeverity.ERROR
        assert "Moment" in error.title
        assert "5500" in error.message or "5,500" in error.message
        assert len(error.fix_suggestions) >= 3

    def test_negative_shear(self):
        """Test error for negative shear (invalid)"""
        error = create_load_error("Shear", -50, 3000, "kN")

        assert error.severity == ErrorSeverity.ERROR
        assert "Shear" in error.title


class TestDesignFailureErrors:
    """Test design failure error messages"""

    def test_design_failure_with_capacity(self):
        """Test design failure with capacity/demand values"""
        error = create_design_failure_error(
            reason="Moment capacity insufficient",
            capacity=100.5,
            demand=120.0,
            clause="Cl. 38.1"
        )

        assert error.severity == ErrorSeverity.ERROR
        assert "100.5" in error.message
        assert "120.0" in error.message
        assert error.clause_reference == "Cl. 38.1"
        assert len(error.fix_suggestions) >= 3

    def test_design_failure_without_capacity(self):
        """Test design failure without capacity values"""
        error = create_design_failure_error(reason="Over-reinforced section")

        assert error.severity == ErrorSeverity.ERROR
        assert "Over-reinforced" in error.message
        assert error.clause_reference is None


class TestComplianceErrors:
    """Test IS 456 compliance error messages"""

    def test_compliance_failure_deficit(self):
        """Test compliance error showing deficit"""
        error = create_compliance_error(
            clause="26.5.1.1",
            requirement="Minimum reinforcement",
            provided=450,
            required=500,
            unit="mm²"
        )

        assert error.severity == ErrorSeverity.ERROR
        assert "26.5.1.1" in error.title
        assert "450" in error.message
        assert "500" in error.message
        assert "-50" in error.message or "50" in error.message  # Deficit
        assert error.clause_reference is not None

    def test_compliance_error_percentage(self):
        """Test that deficit percentage is calculated"""
        error = create_compliance_error(
            clause="26.3.3",
            requirement="Maximum spacing",
            provided=200,
            required=180,
            unit="mm"
        )

        # Should show percentage over limit
        assert "%" in error.message


class TestConvergenceErrors:
    """Test convergence error messages"""

    def test_convergence_failure(self):
        """Test convergence failure error"""
        error = create_convergence_error(iterations=100, tolerance=0.001)

        assert error.severity == ErrorSeverity.ERROR
        assert "100" in error.message
        assert "0.001" in error.message
        assert len(error.fix_suggestions) >= 3
        assert any("depth" in s.lower() for s in error.fix_suggestions)


class TestInputValidationErrors:
    """Test input validation error messages"""

    def test_input_validation_error(self):
        """Test input validation error creation"""
        error = create_input_validation_error(
            field_name="Span Length",
            error_details="Must be a positive number"
        )

        assert error.severity == ErrorSeverity.WARNING
        assert "Span Length" in error.title
        assert "positive number" in error.message
        assert len(error.fix_suggestions) >= 2


class TestGenericErrors:
    """Test generic error message creation"""

    def test_generic_error_from_exception(self):
        """Test creating generic error from exception"""
        try:
            raise ValueError("Test error message")
        except ValueError as e:
            error = create_generic_error(e)

        assert error.severity == ErrorSeverity.CRITICAL
        assert "Unexpected" in error.title
        assert error.technical_details is not None
        assert "ValueError" in error.technical_details

    def test_generic_error_different_exception_types(self):
        """Test generic error with different exception types"""
        exceptions = [
            ValueError("value error"),
            KeyError("key error"),
            TypeError("type error"),
            RuntimeError("runtime error")
        ]

        for exc in exceptions:
            error = create_generic_error(exc)
            assert error.severity == ErrorSeverity.CRITICAL
            assert type(exc).__name__ in error.technical_details


# =============================================================================
# Test Validation Functions
# =============================================================================

class TestDimensionValidation:
    """Test dimension validation functions"""

    def test_valid_dimension(self):
        """Test validation passes for valid dimension"""
        error = validate_dimension_range(5000, 1000, 12000, "Span", "mm")
        assert error is None

    def test_dimension_below_minimum(self):
        """Test validation fails for dimension below minimum"""
        error = validate_dimension_range(500, 1000, 12000, "Span", "mm")
        assert error is not None
        assert error.severity == ErrorSeverity.ERROR
        assert "500" in error.message

    def test_dimension_above_maximum(self):
        """Test validation fails for dimension above maximum"""
        error = validate_dimension_range(15000, 1000, 12000, "Span", "mm")
        assert error is not None
        assert error.severity == ErrorSeverity.ERROR
        assert "15000" in error.message or "15,000" in error.message

    def test_dimension_at_boundary(self):
        """Test validation at exact boundaries"""
        # At minimum - should pass
        error = validate_dimension_range(1000, 1000, 12000, "Span", "mm")
        assert error is None

        # At maximum - should pass
        error = validate_dimension_range(12000, 1000, 12000, "Span", "mm")
        assert error is None


class TestMaterialValidation:
    """Test material validation functions"""

    def test_valid_materials(self):
        """Test validation passes for valid materials"""
        valid_combinations = [
            (25, 500),  # M25, Fe500 (most common)
            (30, 415),  # M30, Fe415
            (20, 250),  # M20, Fe250
            (40, 500),  # M40, Fe500
        ]

        for fck, fy in valid_combinations:
            error = validate_material_grades(fck, fy)
            assert error is None, f"Valid combination ({fck}, {fy}) failed validation"

    def test_invalid_concrete(self):
        """Test validation fails for invalid concrete grade"""
        error = validate_material_grades(27, 500)  # M27 not standard
        assert error is not None
        assert error.severity == ErrorSeverity.ERROR

    def test_invalid_steel(self):
        """Test validation fails for invalid steel grade"""
        error = validate_material_grades(25, 450)  # Fe450 not standard
        assert error is not None
        assert error.severity == ErrorSeverity.ERROR

    def test_both_invalid(self):
        """Test validation fails when both materials invalid"""
        error = validate_material_grades(27, 450)
        assert error is not None
        assert "27" in error.message
        assert "450" in error.message


class TestLoadValidation:
    """Test load validation functions"""

    def test_valid_load(self):
        """Test validation passes for valid load"""
        error = validate_load_value(120, "Moment", 1.0, 5000, "kNm")
        assert error is None

    def test_load_below_minimum(self):
        """Test validation fails for load below minimum"""
        error = validate_load_value(0.5, "Moment", 1.0, 5000, "kNm")
        assert error is not None
        assert error.severity == ErrorSeverity.ERROR

    def test_load_above_maximum(self):
        """Test validation fails for load above maximum"""
        error = validate_load_value(6000, "Moment", 1.0, 5000, "kNm")
        assert error is not None
        assert error.severity == ErrorSeverity.ERROR

    def test_zero_load(self):
        """Test validation for zero load"""
        error = validate_load_value(0, "Moment", 0.0, 5000, "kNm")
        assert error is None  # Should pass if min=0

        error = validate_load_value(0, "Moment", 1.0, 5000, "kNm")
        assert error is not None  # Should fail if min>0


class TestBeamInputValidation:
    """Test comprehensive beam input validation"""

    def test_all_valid_inputs(self):
        """Test validation passes for all valid inputs"""
        errors = validate_beam_inputs(
            span_mm=5000,
            b_mm=300,
            d_mm=450,
            D_mm=500,
            fck_mpa=25,
            fy_mpa=500,
            mu_knm=120,
            vu_kn=80
        )
        assert len(errors) == 0

    def test_invalid_span(self):
        """Test validation catches invalid span"""
        errors = validate_beam_inputs(
            span_mm=500,  # Too small
            b_mm=300,
            d_mm=450,
            D_mm=500,
            fck_mpa=25,
            fy_mpa=500,
            mu_knm=120,
            vu_kn=80
        )
        assert len(errors) >= 1
        assert any("Span" in e.title for e in errors)

    def test_invalid_width(self):
        """Test validation catches invalid width"""
        errors = validate_beam_inputs(
            span_mm=5000,
            b_mm=100,  # Too small
            d_mm=450,
            D_mm=500,
            fck_mpa=25,
            fy_mpa=500,
            mu_knm=120,
            vu_kn=80
        )
        assert len(errors) >= 1
        assert any("Width" in e.title for e in errors)

    def test_depth_relationship_violation(self):
        """Test validation catches d >= D"""
        errors = validate_beam_inputs(
            span_mm=5000,
            b_mm=300,
            d_mm=500,  # Equal to D
            D_mm=500,
            fck_mpa=25,
            fy_mpa=500,
            mu_knm=120,
            vu_kn=80
        )
        assert len(errors) >= 1
        assert any("depth" in e.title.lower() for e in errors)

    def test_invalid_materials(self):
        """Test validation catches invalid materials"""
        errors = validate_beam_inputs(
            span_mm=5000,
            b_mm=300,
            d_mm=450,
            D_mm=500,
            fck_mpa=27,  # Invalid
            fy_mpa=450,  # Invalid
            mu_knm=120,
            vu_kn=80
        )
        assert len(errors) >= 1
        assert any("Material" in e.title for e in errors)

    def test_multiple_errors(self):
        """Test validation catches multiple errors"""
        errors = validate_beam_inputs(
            span_mm=500,      # Invalid (too small)
            b_mm=50,          # Invalid (too small)
            d_mm=100,         # Invalid (too small)
            D_mm=50,          # Invalid (too small, also d > D)
            fck_mpa=27,       # Invalid
            fy_mpa=450,       # Invalid
            mu_knm=0.5,       # Invalid (too small)
            vu_kn=0.1         # Invalid (too small)
        )
        # Should have multiple errors
        assert len(errors) >= 5

    def test_boundary_values(self):
        """Test validation at boundary values"""
        # Minimum valid values
        errors = validate_beam_inputs(
            span_mm=1000,   # Minimum
            b_mm=150,       # Minimum
            d_mm=200,       # Minimum
            D_mm=250,       # Minimum
            fck_mpa=15,     # Minimum standard grade
            fy_mpa=250,     # Minimum standard grade
            mu_knm=1.0,     # Minimum
            vu_kn=0.5       # Minimum
        )
        assert len(errors) == 0

        # Maximum valid values
        errors = validate_beam_inputs(
            span_mm=15000,  # Maximum
            b_mm=1000,      # Maximum
            d_mm=2000,      # Maximum
            D_mm=2500,      # Maximum
            fck_mpa=50,     # Maximum standard grade
            fy_mpa=550,     # Maximum standard grade
            mu_knm=5000,    # Maximum
            vu_kn=3000      # Maximum
        )
        assert len(errors) == 0


# =============================================================================
# Test Error Message Structure
# =============================================================================

class TestErrorMessageStructure:
    """Test ErrorMessage dataclass structure"""

    def test_error_message_creation(self):
        """Test creating ErrorMessage object"""
        error = ErrorMessage(
            severity=ErrorSeverity.ERROR,
            title="Test Error",
            message="This is a test error message",
            fix_suggestions=["Fix 1", "Fix 2"],
            technical_details="Technical details here",
            clause_reference="Cl. 26.1"
        )

        assert error.severity == ErrorSeverity.ERROR
        assert error.title == "Test Error"
        assert error.message == "This is a test error message"
        assert len(error.fix_suggestions) == 2
        assert error.technical_details == "Technical details here"
        assert error.clause_reference == "Cl. 26.1"

    def test_error_message_optional_fields(self):
        """Test ErrorMessage with optional fields omitted"""
        error = ErrorMessage(
            severity=ErrorSeverity.WARNING,
            title="Test Warning",
            message="Warning message",
            fix_suggestions=[]
        )

        assert error.technical_details is None
        assert error.clause_reference is None


# =============================================================================
# Test Edge Cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases and special scenarios"""

    def test_very_large_numbers(self):
        """Test error messages with very large numbers"""
        error = create_dimension_error("Span", 999999, 1000, 12000, "mm")
        assert error is not None
        # Should handle large numbers gracefully

    def test_very_small_numbers(self):
        """Test error messages with very small numbers"""
        error = create_dimension_error("Width", 0.001, 150, 1000, "mm")
        assert error is not None

    def test_zero_values(self):
        """Test handling of zero values"""
        errors = validate_beam_inputs(
            span_mm=0,
            b_mm=0,
            d_mm=0,
            D_mm=0,
            fck_mpa=0,
            fy_mpa=0,
            mu_knm=0,
            vu_kn=0
        )
        # Should have many errors for zero values
        assert len(errors) >= 5

    def test_negative_values(self):
        """Test handling of negative values"""
        errors = validate_beam_inputs(
            span_mm=-5000,
            b_mm=-300,
            d_mm=-450,
            D_mm=-500,
            fck_mpa=-25,
            fy_mpa=-500,
            mu_knm=-120,
            vu_kn=-80
        )
        # Should have many errors for negative values
        assert len(errors) >= 5

    def test_none_values_handling(self):
        """Test that None values are handled (should raise TypeError)"""
        with pytest.raises(TypeError):
            validate_beam_inputs(
                span_mm=None,
                b_mm=300,
                d_mm=450,
                D_mm=500,
                fck_mpa=25,
                fy_mpa=500,
                mu_knm=120,
                vu_kn=80
            )


# =============================================================================
# Test Integration
# =============================================================================

class TestIntegration:
    """Integration tests for error handler"""

    def test_full_validation_workflow(self):
        """Test complete validation workflow"""
        # Start with invalid inputs
        errors = validate_beam_inputs(
            span_mm=500,    # Too small
            b_mm=100,       # Too small
            d_mm=150,       # Too small
            D_mm=200,
            fck_mpa=27,     # Invalid
            fy_mpa=450,     # Invalid
            mu_knm=0.5,     # Too small
            vu_kn=0.1       # Too small
        )

        # Should have multiple errors
        assert len(errors) > 0

        # All errors should have required fields
        for error in errors:
            assert isinstance(error, ErrorMessage)
            assert error.severity is not None
            assert error.title is not None
            assert error.message is not None
            assert isinstance(error.fix_suggestions, list)

    def test_error_message_completeness(self):
        """Test that all error types have complete information"""
        error_creators = [
            lambda: create_dimension_error("Width", 100, 150, 1000, "mm"),
            lambda: create_material_error(27, 450),
            lambda: create_load_error("Moment", 6000, 5000, "kNm"),
            lambda: create_design_failure_error("Test failure"),
            lambda: create_compliance_error("26.5.1.1", "Test", 100, 150, "mm"),
            lambda: create_convergence_error(100, 0.001),
            lambda: create_input_validation_error("Test", "error"),
        ]

        for creator in error_creators:
            error = creator()
            assert error.severity is not None
            assert len(error.title) > 0
            assert len(error.message) > 0
            assert len(error.fix_suggestions) >= 1


# =============================================================================
# Performance Tests
# =============================================================================

class TestPerformance:
    """Test performance of error handling functions"""

    def test_validation_performance(self):
        """Test that validation is fast"""
        import time

        start = time.time()
        for _ in range(1000):
            validate_beam_inputs(
                5000, 300, 450, 500, 25, 500, 120, 80
            )
        elapsed = time.time() - start

        # Should complete 1000 validations in under 0.5 seconds
        assert elapsed < 0.5

    def test_error_creation_performance(self):
        """Test that error creation is fast"""
        import time

        start = time.time()
        for _ in range(1000):
            create_dimension_error("Test", 100, 150, 1000, "mm")
        elapsed = time.time() - start

        # Should create 1000 errors in under 0.1 seconds
        assert elapsed < 0.1


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
