"""
Tests for error schema compliance.

Verifies that structured errors follow the schema defined in docs/reference/error-schema.md.
"""

import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from structural_lib.errors import (
    DesignError,
    Severity,
    E_INPUT_001,
    E_INPUT_010,
    E_INPUT_011,
    E_INPUT_012,
    E_INPUT_013,
    E_INPUT_014,
    E_INPUT_015,
    E_INPUT_016,
    E_FLEXURE_001,
    E_SHEAR_001,
    E_DUCTILE_001,
    make_error,
)
from structural_lib.flexure import design_singly_reinforced
from structural_lib.shear import design_shear
from structural_lib.ductile import check_beam_ductility


class TestDesignErrorDataclass:
    """Test DesignError dataclass structure."""

    def test_required_fields(self):
        """Test that required fields are enforced."""
        error = DesignError(
            code="E_TEST_001",
            severity=Severity.ERROR,
            message="Test error",
        )
        assert error.code == "E_TEST_001"
        assert error.severity == Severity.ERROR
        assert error.message == "Test error"

    def test_frozen_immutable(self):
        """Test that DesignError is immutable (frozen dataclass)."""
        error = DesignError(
            code="E_TEST_001",
            severity=Severity.ERROR,
            message="Test error",
        )
        # Attempting to modify should raise FrozenInstanceError
        with pytest.raises(Exception):  # FrozenInstanceError is subclass of Exception
            error.code = "E_TEST_002"

    def test_optional_fields_default_none(self):
        """Test that optional fields default to None."""
        error = DesignError(
            code="E_TEST_001",
            severity=Severity.ERROR,
            message="Test error",
        )
        assert error.field is None
        assert error.hint is None
        assert error.clause is None

    def test_optional_fields_set(self):
        """Test that optional fields can be set."""
        error = DesignError(
            code="E_TEST_001",
            severity=Severity.ERROR,
            message="Test error",
            field="b",
            hint="Check the value",
            clause="Cl. 26.5.1.1",
        )
        assert error.field == "b"
        assert error.hint == "Check the value"
        assert error.clause == "Cl. 26.5.1.1"

    def test_to_dict(self):
        """Test JSON serialization."""
        error = DesignError(
            code="E_TEST_001",
            severity=Severity.ERROR,
            message="Test error",
            field="b",
            hint="Check the value",
            clause="Cl. 26.5.1.1",
        )
        result = error.to_dict()
        assert result["code"] == "E_TEST_001"
        assert result["severity"] == "error"
        assert result["message"] == "Test error"
        assert result["field"] == "b"
        assert result["hint"] == "Check the value"
        assert result["clause"] == "Cl. 26.5.1.1"

    def test_to_dict_optional_fields_excluded(self):
        """Test that None optional fields are excluded from dict."""
        error = DesignError(
            code="E_TEST_001",
            severity=Severity.ERROR,
            message="Test error",
        )
        result = error.to_dict()
        assert "field" not in result
        assert "hint" not in result
        assert "clause" not in result


class TestSeverityEnum:
    """Test Severity enum values."""

    def test_error_value(self):
        assert Severity.ERROR.value == "error"

    def test_warning_value(self):
        assert Severity.WARNING.value == "warning"

    def test_info_value(self):
        assert Severity.INFO.value == "info"


class TestPredefinedErrors:
    """Test predefined error constants have correct structure."""

    def test_input_error_001(self):
        assert E_INPUT_001.code == "E_INPUT_001"
        assert E_INPUT_001.severity == Severity.ERROR
        assert E_INPUT_001.field == "b"
        assert E_INPUT_001.hint is not None

    def test_input_error_010(self):
        assert E_INPUT_010.code == "E_INPUT_010"
        assert E_INPUT_010.severity == Severity.ERROR
        assert E_INPUT_010.field == "d_dash"

    def test_input_error_011(self):
        assert E_INPUT_011.code == "E_INPUT_011"
        assert E_INPUT_011.severity == Severity.ERROR
        assert E_INPUT_011.field == "min_long_bar_dia"

    def test_input_error_012(self):
        assert E_INPUT_012.code == "E_INPUT_012"
        assert E_INPUT_012.severity == Severity.ERROR
        assert E_INPUT_012.field == "bw"

    def test_input_error_013(self):
        assert E_INPUT_013.code == "E_INPUT_013"
        assert E_INPUT_013.severity == Severity.ERROR
        assert E_INPUT_013.field == "bf"

    def test_input_error_014(self):
        assert E_INPUT_014.code == "E_INPUT_014"
        assert E_INPUT_014.severity == Severity.ERROR
        assert E_INPUT_014.field == "Df"

    def test_input_error_015(self):
        assert E_INPUT_015.code == "E_INPUT_015"
        assert E_INPUT_015.severity == Severity.ERROR
        assert E_INPUT_015.field == "bf"

    def test_input_error_016(self):
        assert E_INPUT_016.code == "E_INPUT_016"
        assert E_INPUT_016.severity == Severity.ERROR
        assert E_INPUT_016.field == "Df"

    def test_flexure_error_001(self):
        assert E_FLEXURE_001.code == "E_FLEXURE_001"
        assert E_FLEXURE_001.severity == Severity.ERROR
        assert E_FLEXURE_001.clause == "Cl. 38.1"

    def test_shear_error_001(self):
        assert E_SHEAR_001.code == "E_SHEAR_001"
        assert E_SHEAR_001.severity == Severity.ERROR
        assert E_SHEAR_001.clause == "Cl. 40.2.3"

    def test_ductile_error_001(self):
        assert E_DUCTILE_001.code == "E_DUCTILE_001"
        assert E_DUCTILE_001.severity == Severity.ERROR
        assert "IS 13920" in E_DUCTILE_001.clause


class TestMakeErrorFactory:
    """Test make_error factory function."""

    def test_make_error_creates_design_error(self):
        error = make_error(
            code="E_CUSTOM_001",
            severity=Severity.WARNING,
            message="Custom warning",
        )
        assert isinstance(error, DesignError)
        assert error.code == "E_CUSTOM_001"
        assert error.severity == Severity.WARNING


class TestFlexureErrorsIntegration:
    """Test that flexure functions return structured errors."""

    def test_invalid_b_returns_error(self):
        result = design_singly_reinforced(
            b=0, d=450, d_total=500, mu_knm=100, fck=25, fy=415
        )
        assert result.is_safe is False
        assert len(result.errors) >= 1
        assert any(e.code == "E_INPUT_001" for e in result.errors)
        # Check dynamic error message only mentions 'b'
        assert "b" in result.error_message
        assert "d_total" not in result.error_message

    def test_invalid_d_returns_error(self):
        result = design_singly_reinforced(
            b=230, d=0, d_total=500, mu_knm=100, fck=25, fy=415
        )
        assert result.is_safe is False
        assert any(e.code == "E_INPUT_002" for e in result.errors)

    def test_invalid_d_total_zero_returns_error(self):
        """Test that d_total <= 0 returns E_INPUT_003a (not E_INPUT_003)."""
        result = design_singly_reinforced(
            b=230, d=450, d_total=0, mu_knm=100, fck=25, fy=415
        )
        assert result.is_safe is False
        assert any(e.code == "E_INPUT_003a" for e in result.errors)

    def test_d_total_less_than_d_returns_error(self):
        result = design_singly_reinforced(
            b=230, d=450, d_total=400, mu_knm=100, fck=25, fy=415
        )
        assert result.is_safe is False
        assert any(e.code == "E_INPUT_003" for e in result.errors)

    def test_mu_exceeds_mu_lim_returns_error(self):
        result = design_singly_reinforced(
            b=230, d=450, d_total=500, mu_knm=500, fck=25, fy=415
        )
        assert result.is_safe is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "E_FLEXURE_001"
        assert result.errors[0].clause == "Cl. 38.1"

    def test_valid_design_no_errors(self):
        result = design_singly_reinforced(
            b=230, d=450, d_total=500, mu_knm=100, fck=25, fy=415
        )
        assert result.is_safe is True
        assert len(result.errors) == 0


class TestShearErrorsIntegration:
    """Test that shear functions return structured errors."""

    def test_invalid_b_returns_error(self):
        result = design_shear(vu_kn=50, b=0, d=450, fck=25, fy=415, asv=157, pt=0.5)
        assert result.is_safe is False
        assert any(e.code == "E_INPUT_001" for e in result.errors)

    def test_invalid_asv_returns_error(self):
        result = design_shear(vu_kn=50, b=230, d=450, fck=25, fy=415, asv=0, pt=0.5)
        assert result.is_safe is False
        assert any(e.code == "E_INPUT_008" for e in result.errors)

    def test_tv_exceeds_tc_max_returns_error(self):
        # Very high shear force to exceed tc_max
        result = design_shear(vu_kn=500, b=150, d=250, fck=20, fy=415, asv=157, pt=0.5)
        assert result.is_safe is False
        assert any(e.code == "E_SHEAR_001" for e in result.errors)

    def test_valid_shear_design(self):
        result = design_shear(vu_kn=50, b=230, d=450, fck=25, fy=415, asv=157, pt=0.5)
        assert result.is_safe is True


class TestDuctileErrorsIntegration:
    """Test that ductile functions return structured errors."""

    def test_width_less_than_200_returns_error(self):
        result = check_beam_ductility(
            b=150, D=450, d=400, fck=25, fy=415, min_long_bar_dia=12
        )
        assert result.is_geometry_valid is False
        assert len(result.errors) >= 1
        assert any(e.code == "E_DUCTILE_001" for e in result.errors)

    def test_width_depth_ratio_less_than_0_3_returns_error(self):
        result = check_beam_ductility(
            b=200, D=700, d=650, fck=25, fy=415, min_long_bar_dia=12
        )
        assert result.is_geometry_valid is False
        assert any(e.code == "E_DUCTILE_002" for e in result.errors)

    def test_valid_ductile_design(self):
        result = check_beam_ductility(
            b=230, D=450, d=400, fck=25, fy=415, min_long_bar_dia=12
        )
        assert result.is_geometry_valid is True
        assert len(result.errors) == 0


class TestErrorCodePrefixes:
    """Verify error code naming conventions per docs/reference/error-schema.md."""

    def test_input_error_prefix(self):
        assert E_INPUT_001.code.startswith("E_INPUT_")

    def test_flexure_error_prefix(self):
        assert E_FLEXURE_001.code.startswith("E_FLEXURE_")

    def test_shear_error_prefix(self):
        assert E_SHEAR_001.code.startswith("E_SHEAR_")

    def test_ductile_error_prefix(self):
        assert E_DUCTILE_001.code.startswith("E_DUCTILE_")
