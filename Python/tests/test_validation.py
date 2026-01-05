"""
Tests for validation utilities module.
"""

from structural_lib import validation
from structural_lib.errors import (
    E_INPUT_001,
    E_INPUT_002,
    E_INPUT_003,
    E_INPUT_004,
    E_INPUT_005,
    E_INPUT_013,
    E_INPUT_014,
    E_INPUT_015,
    E_INPUT_003a,
)


class TestValidateDimensions:
    """Tests for validate_dimensions()."""

    def test_valid_dimensions(self):
        """Valid dimensions return no errors."""
        errors = validation.validate_dimensions(b=300, d=450, D=500)
        assert errors == []

    def test_negative_b(self):
        """Negative b returns E_INPUT_001."""
        errors = validation.validate_dimensions(b=-300, d=450, D=500)
        assert E_INPUT_001 in errors

    def test_zero_b(self):
        """Zero b returns E_INPUT_001."""
        errors = validation.validate_dimensions(b=0, d=450, D=500)
        assert E_INPUT_001 in errors

    def test_negative_d(self):
        """Negative d returns E_INPUT_002."""
        errors = validation.validate_dimensions(b=300, d=-450, D=500)
        assert E_INPUT_002 in errors

    def test_zero_d(self):
        """Zero d returns E_INPUT_002."""
        errors = validation.validate_dimensions(b=300, d=0, D=500)
        assert E_INPUT_002 in errors

    def test_negative_D(self):
        """Negative D returns E_INPUT_003a."""
        errors = validation.validate_dimensions(b=300, d=450, D=-500)
        assert E_INPUT_003a in errors

    def test_zero_D(self):
        """Zero D returns E_INPUT_003a."""
        errors = validation.validate_dimensions(b=300, d=450, D=0)
        assert E_INPUT_003a in errors

    def test_d_greater_than_D(self):
        """d >= D returns E_INPUT_003."""
        errors = validation.validate_dimensions(b=300, d=500, D=450)
        assert E_INPUT_003 in errors

    def test_d_equal_to_D(self):
        """d == D returns E_INPUT_003."""
        errors = validation.validate_dimensions(b=300, d=500, D=500)
        assert E_INPUT_003 in errors

    def test_d_equal_to_D_allowed(self):
        """d == D is allowed when require_d_less_than_D=False."""
        errors = validation.validate_dimensions(
            b=300, d=500, D=500, require_d_less_than_D=False
        )
        # Should still have errors for other invalid inputs, but not E_INPUT_003
        assert E_INPUT_003 not in errors

    def test_multiple_errors(self):
        """Multiple invalid inputs return multiple errors."""
        errors = validation.validate_dimensions(b=-300, d=-450, D=-500)
        assert len(errors) == 3
        assert E_INPUT_001 in errors
        assert E_INPUT_002 in errors
        assert E_INPUT_003a in errors


class TestValidateMaterials:
    """Tests for validate_materials()."""

    def test_valid_materials(self):
        """Valid material properties return no errors."""
        errors = validation.validate_materials(fck=25, fy=500)
        assert errors == []

    def test_negative_fck(self):
        """Negative fck returns E_INPUT_004."""
        errors = validation.validate_materials(fck=-25, fy=500)
        assert E_INPUT_004 in errors

    def test_zero_fck(self):
        """Zero fck returns E_INPUT_004."""
        errors = validation.validate_materials(fck=0, fy=500)
        assert E_INPUT_004 in errors

    def test_negative_fy(self):
        """Negative fy returns E_INPUT_005."""
        errors = validation.validate_materials(fck=25, fy=-500)
        assert E_INPUT_005 in errors

    def test_zero_fy(self):
        """Zero fy returns E_INPUT_005."""
        errors = validation.validate_materials(fck=25, fy=0)
        assert E_INPUT_005 in errors

    def test_multiple_errors(self):
        """Both invalid returns two errors."""
        errors = validation.validate_materials(fck=-25, fy=-500)
        assert len(errors) == 2
        assert E_INPUT_004 in errors
        assert E_INPUT_005 in errors


class TestValidatePositive:
    """Tests for validate_positive()."""

    def test_valid_value(self):
        """Positive value returns no errors."""
        error_map = {"mu_knm": E_INPUT_001}
        errors = validation.validate_positive(100.0, "mu_knm", error_map)
        assert errors == []

    def test_zero_value(self):
        """Zero value returns error."""
        error_map = {"mu_knm": E_INPUT_001}
        errors = validation.validate_positive(0.0, "mu_knm", error_map)
        assert len(errors) == 1
        assert errors[0] == E_INPUT_001

    def test_negative_value(self):
        """Negative value returns error."""
        error_map = {"mu_knm": E_INPUT_001}
        errors = validation.validate_positive(-10.0, "mu_knm", error_map)
        assert len(errors) == 1

    def test_field_not_in_map(self):
        """Field not in map returns generic error."""
        error_map = {"other_field": E_INPUT_001}
        errors = validation.validate_positive(-10.0, "unknown_field", error_map)
        assert len(errors) == 1
        assert errors[0].code == "E_INPUT_GENERIC"
        assert errors[0].field == "unknown_field"


class TestValidateRange:
    """Tests for validate_range()."""

    def test_value_in_range(self):
        """Value within range returns no errors."""
        errors = validation.validate_range(2.5, 0.0, 4.0, "pt", E_INPUT_002)
        assert errors == []

    def test_value_at_min(self):
        """Value at minimum boundary is valid."""
        errors = validation.validate_range(0.0, 0.0, 4.0, "pt", E_INPUT_002)
        assert errors == []

    def test_value_at_max(self):
        """Value at maximum boundary is valid."""
        errors = validation.validate_range(4.0, 0.0, 4.0, "pt", E_INPUT_002)
        assert errors == []

    def test_value_below_min(self):
        """Value below minimum returns error."""
        errors = validation.validate_range(-0.1, 0.0, 4.0, "pt", E_INPUT_002)
        assert len(errors) == 1
        assert errors[0] == E_INPUT_002

    def test_value_above_max(self):
        """Value above maximum returns error."""
        errors = validation.validate_range(4.1, 0.0, 4.0, "pt", E_INPUT_002)
        assert len(errors) == 1
        assert errors[0] == E_INPUT_002


class TestValidateGeometryRelationship:
    """Tests for validate_geometry_relationship()."""

    def test_valid_geometry(self):
        """Valid geometry relationship returns no errors."""
        errors = validation.validate_geometry_relationship(d=450, D=500, cover=40)
        assert errors == []

    def test_negative_d(self):
        """Negative d returns error."""
        errors = validation.validate_geometry_relationship(d=-450, D=500, cover=40)
        assert E_INPUT_002 in errors

    def test_negative_D(self):
        """Negative D returns error."""
        errors = validation.validate_geometry_relationship(d=450, D=-500, cover=40)
        assert E_INPUT_003a in errors

    def test_negative_cover(self):
        """Negative cover returns error."""
        errors = validation.validate_geometry_relationship(d=450, D=500, cover=-40)
        assert E_INPUT_015 in errors

    def test_d_too_large_for_D(self):
        """d too large relative to D and cover returns error."""
        errors = validation.validate_geometry_relationship(d=490, D=500, cover=40)
        assert E_INPUT_003 in errors


class TestValidateStirrupParameters:
    """Tests for validate_stirrup_parameters()."""

    def test_valid_stirrups(self):
        """Valid stirrup parameters return no errors."""
        errors = validation.validate_stirrup_parameters(asv_mm2=100, spacing_mm=150)
        assert errors == []

    def test_negative_asv(self):
        """Negative asv returns error."""
        errors = validation.validate_stirrup_parameters(asv_mm2=-100, spacing_mm=150)
        assert E_INPUT_013 in errors

    def test_zero_asv(self):
        """Zero asv returns error."""
        errors = validation.validate_stirrup_parameters(asv_mm2=0, spacing_mm=150)
        assert E_INPUT_013 in errors

    def test_negative_spacing(self):
        """Negative spacing returns error."""
        errors = validation.validate_stirrup_parameters(asv_mm2=100, spacing_mm=-150)
        assert E_INPUT_014 in errors

    def test_zero_spacing(self):
        """Zero spacing returns error."""
        errors = validation.validate_stirrup_parameters(asv_mm2=100, spacing_mm=0)
        assert E_INPUT_014 in errors

    def test_multiple_errors(self):
        """Both invalid returns two errors."""
        errors = validation.validate_stirrup_parameters(asv_mm2=-100, spacing_mm=-150)
        assert len(errors) == 2
        assert E_INPUT_013 in errors
        assert E_INPUT_014 in errors


class TestValidateAllPositive:
    """Tests for validate_all_positive()."""

    def test_all_valid(self):
        """All positive values return no errors."""
        errors = validation.validate_all_positive(b=300, d=450, D=500, fck=25, fy=500)
        assert errors == []

    def test_one_invalid(self):
        """One invalid value returns one error."""
        errors = validation.validate_all_positive(b=300, d=450, D=500, fck=-25, fy=500)
        assert len(errors) == 1
        assert errors[0].field == "fck"
        assert errors[0].code == "E_INPUT_GENERIC"

    def test_multiple_invalid(self):
        """Multiple invalid values return multiple errors."""
        errors = validation.validate_all_positive(b=-300, d=0, D=500, fck=-25, fy=500)
        assert len(errors) == 3
        field_names = {err.field for err in errors}
        assert field_names == {"b", "d", "fck"}

    def test_empty_kwargs(self):
        """No arguments return no errors."""
        errors = validation.validate_all_positive()
        assert errors == []
