# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for exception hierarchy in errors module."""

import pytest

from structural_lib.errors import (
    CalculationError,
    ComplianceError,
    ConfigurationError,
    DesignConstraintError,
    DimensionError,
    LoadError,
    MaterialError,
    StructuralLibError,
    ValidationError,
)


class TestExceptionHierarchy:
    """Tests for exception hierarchy structure."""

    def test_base_exception(self):
        """Test StructuralLibError base exception."""
        exc = StructuralLibError("Test message")
        assert str(exc) == "Test message"
        assert exc.message == "Test message"
        assert exc.details == {}
        assert exc.suggestion is None
        assert exc.clause_ref is None

    def test_base_exception_with_all_fields(self):
        """Test StructuralLibError with all optional fields."""
        exc = StructuralLibError(
            "Beam width too small",
            details={"b_mm": 150, "minimum": 200},
            suggestion="Increase beam width to at least 200mm",
            clause_ref="Cl. 26.5.1.1",
        )
        result = str(exc)
        assert "Beam width too small" in result
        assert "Cl. 26.5.1.1" in result
        assert "Increase beam width" in result
        assert "b_mm=150" in result
        assert "minimum=200" in result

    def test_validation_error(self):
        """Test ValidationError inherits from StructuralLibError."""
        exc = ValidationError("Invalid dimension")
        assert isinstance(exc, StructuralLibError)
        assert isinstance(exc, Exception)

    def test_design_constraint_error(self):
        """Test DesignConstraintError inherits from StructuralLibError."""
        exc = DesignConstraintError("Capacity exceeded")
        assert isinstance(exc, StructuralLibError)
        assert isinstance(exc, Exception)

    def test_compliance_error(self):
        """Test ComplianceError inherits from StructuralLibError."""
        exc = ComplianceError("Minimum steel not met")
        assert isinstance(exc, StructuralLibError)
        assert isinstance(exc, Exception)

    def test_configuration_error(self):
        """Test ConfigurationError inherits from StructuralLibError."""
        exc = ConfigurationError("Invalid setup")
        assert isinstance(exc, StructuralLibError)
        assert isinstance(exc, Exception)

    def test_calculation_error(self):
        """Test CalculationError inherits from StructuralLibError."""
        exc = CalculationError("Convergence failed")
        assert isinstance(exc, StructuralLibError)
        assert isinstance(exc, Exception)

    def test_dimension_error(self):
        """Test DimensionError inherits from ValidationError."""
        exc = DimensionError("Width too small")
        assert isinstance(exc, ValidationError)
        assert isinstance(exc, StructuralLibError)
        assert isinstance(exc, Exception)

    def test_material_error(self):
        """Test MaterialError inherits from ValidationError."""
        exc = MaterialError("Invalid grade")
        assert isinstance(exc, ValidationError)
        assert isinstance(exc, StructuralLibError)
        assert isinstance(exc, Exception)

    def test_load_error(self):
        """Test LoadError inherits from ValidationError."""
        exc = LoadError("Negative load")
        assert isinstance(exc, ValidationError)
        assert isinstance(exc, StructuralLibError)
        assert isinstance(exc, Exception)


class TestExceptionCatching:
    """Tests for catching exceptions at different levels."""

    def test_catch_specific_exception(self):
        """Test catching specific exception type."""
        with pytest.raises(DimensionError) as exc_info:
            raise DimensionError("Width too small")
        assert "Width too small" in str(exc_info.value)

    def test_catch_validation_error(self):
        """Test catching ValidationError catches all validation exceptions."""
        # DimensionError should be catchable as ValidationError
        with pytest.raises(ValidationError):
            raise DimensionError("Width too small")

        # MaterialError should be catchable as ValidationError
        with pytest.raises(ValidationError):
            raise MaterialError("Invalid grade")

        # LoadError should be catchable as ValidationError
        with pytest.raises(ValidationError):
            raise LoadError("Negative load")

    def test_catch_structural_lib_error(self):
        """Test catching StructuralLibError catches all library exceptions."""
        # All level 1 exceptions
        with pytest.raises(StructuralLibError):
            raise ValidationError("Test")

        with pytest.raises(StructuralLibError):
            raise DesignConstraintError("Test")

        with pytest.raises(StructuralLibError):
            raise ComplianceError("Test")

        with pytest.raises(StructuralLibError):
            raise ConfigurationError("Test")

        with pytest.raises(StructuralLibError):
            raise CalculationError("Test")

        # All level 2 exceptions
        with pytest.raises(StructuralLibError):
            raise DimensionError("Test")

        with pytest.raises(StructuralLibError):
            raise MaterialError("Test")

        with pytest.raises(StructuralLibError):
            raise LoadError("Test")


class TestExceptionUsageExamples:
    """Tests demonstrating proper exception usage."""

    def test_dimension_error_example(self):
        """Test typical dimension error with details."""
        b_mm = 150
        minimum = 200

        with pytest.raises(DimensionError) as exc_info:
            raise DimensionError(
                f"Beam width b={b_mm}mm is below minimum {minimum}mm",
                details={"b_mm": b_mm, "minimum": minimum},
                suggestion="Increase beam width to at least 200mm",
                clause_ref="Cl. 26.5.1.1",
            )

        exc = exc_info.value
        assert "150mm" in str(exc)
        assert "200mm" in str(exc)
        assert "Cl. 26.5.1.1" in str(exc)
        assert exc.details["b_mm"] == 150
        assert exc.details["minimum"] == 200

    def test_design_constraint_error_example(self):
        """Test typical design constraint error."""
        mu_knm = 250
        mu_lim_knm = 200

        with pytest.raises(DesignConstraintError) as exc_info:
            raise DesignConstraintError(
                f"Moment Mu={mu_knm} kN·m exceeds section capacity Mu,lim={mu_lim_knm} kN·m",
                details={"mu_knm": mu_knm, "mu_lim_knm": mu_lim_knm},
                suggestion="Increase section depth or use compression reinforcement",
                clause_ref="Cl. 38.1",
            )

        exc = exc_info.value
        assert "250" in str(exc)
        assert "200" in str(exc)
        assert "Increase section depth" in str(exc)

    def test_compliance_error_example(self):
        """Test typical compliance error."""
        pt_actual = 0.12
        pt_min = 0.20

        with pytest.raises(ComplianceError) as exc_info:
            raise ComplianceError(
                f"Steel ratio pt={pt_actual:.2f}% is below minimum {pt_min:.2f}%",
                details={"pt_actual": pt_actual, "pt_min": pt_min},
                suggestion="Increase reinforcement to meet minimum steel requirements",
                clause_ref="Cl. 26.5.1.1",
            )

        exc = exc_info.value
        assert "0.12" in str(exc)
        assert "0.20" in str(exc)
        assert "Cl. 26.5.1.1" in str(exc)

    def test_calculation_error_example(self):
        """Test typical calculation error."""
        with pytest.raises(CalculationError) as exc_info:
            raise CalculationError(
                "Iterative solution did not converge after 100 iterations",
                details={"iterations": 100, "tolerance": 0.001},
                suggestion="Check input values or increase iteration limit",
            )

        exc = exc_info.value
        assert "100" in str(exc)
        assert "converge" in str(exc)


class TestMultiLevelCatching:
    """Tests for catching exceptions at multiple levels."""

    def test_catch_at_appropriate_level(self):
        """Test that exceptions can be caught at the appropriate specificity level."""

        def validate_dimensions(b_mm: float) -> None:
            if b_mm < 200:
                raise DimensionError(
                    f"Width {b_mm}mm < 200mm minimum",
                    details={"b_mm": b_mm},
                )

        # Can catch specifically
        with pytest.raises(DimensionError):
            validate_dimensions(150)

        # Can catch as ValidationError
        with pytest.raises(ValidationError):
            validate_dimensions(150)

        # Can catch as StructuralLibError
        with pytest.raises(StructuralLibError):
            validate_dimensions(150)

    def test_exception_filtering(self):
        """Test filtering exceptions by type."""
        errors = []

        def collect_errors(func):
            try:
                func()
            except ValidationError as e:
                errors.append(("validation", e))
            except DesignConstraintError as e:
                errors.append(("design", e))
            except StructuralLibError as e:
                errors.append(("other", e))

        # Validation error
        collect_errors(lambda: (_ for _ in ()).throw(DimensionError("Test1")))
        assert errors[-1][0] == "validation"

        # Design error
        collect_errors(lambda: (_ for _ in ()).throw(DesignConstraintError("Test2")))
        assert errors[-1][0] == "design"

        # Other error
        collect_errors(lambda: (_ for _ in ()).throw(CalculationError("Test3")))
        assert errors[-1][0] == "other"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
