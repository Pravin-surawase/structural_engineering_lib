"""
Tests for validation utilities module.
"""

from structural_lib import validation
from structural_lib.core.errors import (
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


class TestValidateCover:
    """Tests for validate_cover()."""

    def test_valid_cover(self):
        """Valid cover returns no errors."""
        errors = validation.validate_cover(cover=30, D=500, min_cover=25)
        assert errors == []

    def test_negative_cover(self):
        """Negative cover returns error."""
        errors = validation.validate_cover(cover=-30, D=500)
        assert len(errors) >= 1
        assert any(err.code == "E_INPUT_015" for err in errors)

    def test_zero_cover(self):
        """Zero cover returns error."""
        errors = validation.validate_cover(cover=0, D=500)
        assert len(errors) >= 1

    def test_cover_exceeds_depth(self):
        """Cover >= D returns error."""
        errors = validation.validate_cover(cover=500, D=500)
        assert len(errors) >= 1
        assert any("TOO_LARGE" in err.code for err in errors)

    def test_cover_below_minimum(self):
        """Cover < min_cover returns warning."""
        errors = validation.validate_cover(cover=20, D=500, min_cover=25)
        assert len(errors) == 1
        assert errors[0].code == "E_INPUT_COVER_MIN"
        assert errors[0].severity.value == "warning"

    def test_cover_at_minimum(self):
        """Cover == min_cover is valid."""
        errors = validation.validate_cover(cover=25, D=500, min_cover=25)
        assert errors == []


class TestValidateLoads:
    """Tests for validate_loads()."""

    def test_valid_loads(self):
        """Positive loads return no errors."""
        errors = validation.validate_loads(mu=120, vu=80)
        assert errors == []

    def test_negative_moment_not_allowed(self):
        """Negative moment returns error by default."""
        errors = validation.validate_loads(mu=-120, vu=80)
        assert len(errors) >= 1
        assert any("MU_NEGATIVE" in err.code for err in errors)

    def test_negative_shear_not_allowed(self):
        """Negative shear returns error by default."""
        errors = validation.validate_loads(mu=120, vu=-80)
        assert len(errors) >= 1
        assert any("VU_NEGATIVE" in err.code for err in errors)

    def test_negative_allowed(self):
        """Negative loads allowed with flag."""
        errors = validation.validate_loads(mu=-120, vu=-80, allow_negative=True)
        # Should not have NEGATIVE errors, only check unreasonable magnitudes
        assert not any("NEGATIVE" in err.code for err in errors)

    def test_unreasonable_moment(self):
        """Very large moment returns warning."""
        errors = validation.validate_loads(mu=15000, vu=80, allow_negative=True)
        assert len(errors) >= 1
        assert any("UNREASONABLE" in err.code for err in errors)
        assert any(err.severity.value == "warning" for err in errors)

    def test_unreasonable_shear(self):
        """Very large shear returns warning."""
        errors = validation.validate_loads(mu=120, vu=6000, allow_negative=True)
        assert len(errors) >= 1
        assert any("UNREASONABLE" in err.code for err in errors)


class TestValidateMaterialGrades:
    """Tests for validate_material_grades()."""

    def test_standard_grades(self):
        """Standard IS 456 grades return no errors."""
        errors = validation.validate_material_grades(fck=25, fy=415)
        assert errors == []

    def test_all_standard_fck(self):
        """All standard fck grades are valid."""
        for fck in [15, 20, 25, 30, 35, 40, 45, 50]:
            errors = validation.validate_material_grades(fck=fck, fy=415)
            assert not any("FCK_INVALID" in err.code for err in errors)

    def test_all_standard_fy(self):
        """All standard fy grades are valid."""
        for fy in [250, 415, 500]:
            errors = validation.validate_material_grades(fck=25, fy=fy)
            assert not any("FY_INVALID" in err.code for err in errors)

    def test_non_standard_fck(self):
        """Non-standard fck returns warning."""
        errors = validation.validate_material_grades(fck=27, fy=415)
        assert len(errors) == 1
        assert errors[0].code == "E_INPUT_FCK_INVALID"
        assert errors[0].severity.value == "warning"

    def test_non_standard_fy(self):
        """Non-standard fy returns warning."""
        errors = validation.validate_material_grades(fck=25, fy=450)
        assert len(errors) == 1
        assert errors[0].code == "E_INPUT_FY_INVALID"
        assert errors[0].severity.value == "warning"

    def test_both_non_standard(self):
        """Both non-standard return two warnings."""
        errors = validation.validate_material_grades(fck=27, fy=450)
        assert len(errors) == 2


class TestValidateReinforcement:
    """Tests for validate_reinforcement()."""

    def test_valid_reinforcement(self):
        """Ast within limits returns no errors."""
        errors = validation.validate_reinforcement(ast=1200, ast_min=850, ast_max=3000)
        assert errors == []

    def test_negative_ast(self):
        """Negative ast returns error."""
        errors = validation.validate_reinforcement(ast=-1200, ast_min=850, ast_max=3000)
        assert len(errors) >= 1
        assert any("NEGATIVE" in err.code for err in errors)

    def test_ast_below_minimum(self):
        """Ast < ast_min returns error."""
        errors = validation.validate_reinforcement(ast=700, ast_min=850, ast_max=3000)
        assert len(errors) == 1
        assert errors[0].code == "E_INPUT_AST_BELOW_MIN"
        assert errors[0].severity.value == "error"

    def test_ast_at_minimum(self):
        """Ast == ast_min is valid."""
        errors = validation.validate_reinforcement(ast=850, ast_min=850, ast_max=3000)
        assert errors == []

    def test_ast_above_maximum(self):
        """Ast > ast_max returns error."""
        errors = validation.validate_reinforcement(ast=3500, ast_min=850, ast_max=3000)
        assert len(errors) == 1
        assert errors[0].code == "E_INPUT_AST_ABOVE_MAX"
        assert errors[0].severity.value == "error"

    def test_ast_at_maximum(self):
        """Ast == ast_max is valid."""
        errors = validation.validate_reinforcement(ast=3000, ast_min=850, ast_max=3000)
        assert errors == []

    def test_custom_field_name(self):
        """Custom field name appears in errors."""
        errors = validation.validate_reinforcement(
            ast=-1200, ast_min=850, ast_max=3000, field_name="ast_compression"
        )
        assert len(errors) >= 1
        assert errors[0].field == "ast_compression"


class TestValidateSpan:
    """Tests for validate_span()."""

    def test_valid_span(self):
        """Reasonable span returns no errors."""
        errors = validation.validate_span(span=5000)
        assert errors == []

    def test_negative_span(self):
        """Negative span returns error."""
        errors = validation.validate_span(span=-5000)
        assert len(errors) >= 1
        assert any("POSITIVE" in err.code for err in errors)

    def test_zero_span(self):
        """Zero span returns error."""
        errors = validation.validate_span(span=0)
        assert len(errors) >= 1

    def test_span_too_small(self):
        """Very small span returns warning."""
        errors = validation.validate_span(span=500, min_span=1000)
        assert len(errors) == 1
        assert errors[0].code == "E_INPUT_SPAN_TOO_SMALL"
        assert errors[0].severity.value == "warning"

    def test_span_at_minimum(self):
        """Span == min_span is valid."""
        errors = validation.validate_span(span=1000, min_span=1000)
        assert errors == []

    def test_span_too_large(self):
        """Very large span returns warning."""
        errors = validation.validate_span(span=35000, max_span=30000)
        assert len(errors) == 1
        assert errors[0].code == "E_INPUT_SPAN_TOO_LARGE"
        assert errors[0].severity.value == "warning"

    def test_span_at_maximum(self):
        """Span == max_span is valid."""
        errors = validation.validate_span(span=30000, max_span=30000)
        assert errors == []


class TestValidateBeamInputs:
    """Tests for validate_beam_inputs() composite validator."""

    def test_all_valid(self):
        """All valid inputs return no errors."""
        errors = validation.validate_beam_inputs(
            b=300, d=450, D=500, cover=25, fck=25, fy=415, mu=120, vu=80
        )
        # May have warnings for grade validation, but no errors
        assert not any(err.severity.value == "error" for err in errors)

    def test_with_span(self):
        """Span validation included when provided."""
        errors = validation.validate_beam_inputs(
            b=300, d=450, D=500, cover=25, fck=25, fy=415, mu=120, vu=80, span=5000
        )
        # Should validate span too
        assert not any(err.severity.value == "error" for err in errors)

    def test_multiple_errors(self):
        """Multiple invalid inputs return multiple errors."""
        errors = validation.validate_beam_inputs(
            b=-300, d=-450, D=500, cover=-25, fck=25, fy=415, mu=-120, vu=80
        )
        # Should have errors for b, d, cover, mu
        error_codes = [err.code for err in errors]
        assert len(error_codes) >= 4

    def test_negative_loads_allowed(self):
        """Negative loads allowed with flag."""
        errors = validation.validate_beam_inputs(
            b=300,
            d=450,
            D=500,
            cover=25,
            fck=25,
            fy=415,
            mu=-120,
            vu=-80,
            allow_negative_loads=True,
        )
        # Should not have NEGATIVE errors
        assert not any("NEGATIVE" in err.code for err in errors)

    def test_aggregates_all_validators(self):
        """Composite validator runs all individual validators."""
        errors = validation.validate_beam_inputs(
            b=0, d=0, D=0, cover=0, fck=27, fy=450, mu=0, vu=0, span=0
        )
        # Should have errors from multiple validators
        assert len(errors) >= 7  # Multiple sources of errors
