# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for core types and error dataclasses.

Covers: core/errors.py (DesignError, Severity, pre-defined codes),
        core/data_types.py (enums, TypedDicts, dataclasses),
        core/types.py (re-export shim).
"""

import pytest

from structural_lib.core.data_types import (
    BeamType,
    DesignSectionType,
    ExposureClass,
    FlexureResult,
    LoadDefinition,
    LoadType,
    SupportCondition,
)
from structural_lib.core.errors import (
    E_FLEXURE_001,
    E_INPUT_001,
    E_INPUT_002,
    E_INPUT_006,
    DesignError,
    Severity,
    make_error,
)

# ---------------------------------------------------------------------------
# DesignError dataclass tests
# ---------------------------------------------------------------------------


class TestDesignError:
    """Tests for the DesignError structured error dataclass."""

    def test_create_with_required_fields(self):
        """DesignError can be created with required fields only."""
        err = DesignError(code="E_TEST_001", severity=Severity.ERROR, message="Test")
        assert err.code == "E_TEST_001"
        assert err.severity == Severity.ERROR
        assert err.message == "Test"
        assert err.field is None
        assert err.hint is None
        assert err.clause is None

    def test_create_with_all_fields(self):
        """DesignError can be created with all optional fields."""
        err = DesignError(
            code="E_TEST_002",
            severity=Severity.WARNING,
            message="Check dimension",
            field="b_mm",
            hint="Increase width",
            clause="Cl. 26.5.1.1",
        )
        assert err.field == "b_mm"
        assert err.hint == "Increase width"
        assert err.clause == "Cl. 26.5.1.1"

    def test_frozen_immutability(self):
        """DesignError is frozen (immutable)."""
        err = DesignError(code="E_TEST_001", severity=Severity.ERROR, message="Test")
        with pytest.raises(AttributeError):
            err.code = "MODIFIED"

    def test_to_dict_required_only(self):
        """to_dict includes code, severity, message."""
        err = DesignError(code="E_TEST_001", severity=Severity.ERROR, message="Test")
        d = err.to_dict()
        assert d["code"] == "E_TEST_001"
        assert d["severity"] == "error"
        assert d["message"] == "Test"
        assert "field" not in d
        assert "hint" not in d

    def test_to_dict_includes_optional_fields(self):
        """to_dict includes optional fields when present."""
        err = DesignError(
            code="E_TEST_001",
            severity=Severity.ERROR,
            message="Test",
            field="b",
            hint="Fix it",
            clause="Cl. 38.1",
        )
        d = err.to_dict()
        assert d["field"] == "b"
        assert d["hint"] == "Fix it"
        assert d["clause"] == "Cl. 38.1"


class TestSeverityEnum:
    """Tests for the Severity enum."""

    def test_severity_values(self):
        """All severity levels have correct string values."""
        assert Severity.ERROR.value == "error"
        assert Severity.WARNING.value == "warning"
        assert Severity.INFO.value == "info"

    def test_severity_is_str_enum(self):
        """Severity members are strings."""
        assert isinstance(Severity.ERROR, str)
        assert Severity.ERROR == "error"


class TestPreDefinedErrors:
    """Tests for pre-defined error constants."""

    def test_e_input_001(self):
        """E_INPUT_001 is correctly defined."""
        assert E_INPUT_001.code == "E_INPUT_001"
        assert E_INPUT_001.severity == Severity.ERROR
        assert E_INPUT_001.field == "b"

    def test_e_input_002(self):
        """E_INPUT_002 targets field 'd'."""
        assert E_INPUT_002.field == "d"

    def test_e_flexure_001(self):
        """E_FLEXURE_001 references IS 456 clause."""
        assert E_FLEXURE_001.clause == "Cl. 38.1"
        assert "Mu" in E_FLEXURE_001.message

    def test_e_input_006_moment(self):
        """E_INPUT_006 validates moment >= 0."""
        assert E_INPUT_006.field == "Mu"

    def test_predefined_are_frozen(self):
        """Pre-defined error constants are immutable."""
        with pytest.raises(AttributeError):
            E_INPUT_001.message = "tampered"


class TestMakeError:
    """Tests for the make_error factory function."""

    def test_make_error_creates_design_error(self):
        """make_error produces a valid DesignError."""
        err = make_error("E_CUSTOM_001", Severity.WARNING, "Custom warning")
        assert isinstance(err, DesignError)
        assert err.code == "E_CUSTOM_001"
        assert err.severity == Severity.WARNING

    def test_make_error_with_optional_fields(self):
        """make_error passes through optional fields."""
        err = make_error(
            "E_CUSTOM_002",
            Severity.ERROR,
            "Bad input",
            field="fck",
            hint="Use M20-M80",
            clause="Table 2",
        )
        assert err.field == "fck"
        assert err.hint == "Use M20-M80"


# ---------------------------------------------------------------------------
# Data types tests
# ---------------------------------------------------------------------------


class TestDataTypeEnums:
    """Tests for enums in data_types module."""

    def test_beam_type_values(self):
        """BeamType enum has expected members."""
        assert BeamType.RECTANGULAR.value == 1
        assert BeamType.FLANGED_T.value == 2
        assert BeamType.FLANGED_L.value == 3

    def test_design_section_type(self):
        """DesignSectionType enum has expected members."""
        assert DesignSectionType.UNDER_REINFORCED.value == 1
        assert DesignSectionType.BALANCED.value == 2
        assert DesignSectionType.OVER_REINFORCED.value == 3

    def test_support_condition(self):
        """SupportCondition enum has expected members."""
        assert hasattr(SupportCondition, "CANTILEVER")
        assert hasattr(SupportCondition, "SIMPLY_SUPPORTED")
        assert hasattr(SupportCondition, "CONTINUOUS")

    def test_exposure_class(self):
        """ExposureClass enum has expected members."""
        assert hasattr(ExposureClass, "MILD")
        assert hasattr(ExposureClass, "MODERATE")
        assert hasattr(ExposureClass, "SEVERE")
        assert hasattr(ExposureClass, "VERY_SEVERE")

    def test_load_type(self):
        """LoadType enum has expected members."""
        assert hasattr(LoadType, "UDL")
        assert hasattr(LoadType, "POINT")
        assert hasattr(LoadType, "TRIANGULAR")
        assert hasattr(LoadType, "MOMENT")


class TestFlexureResult:
    """Tests for FlexureResult dataclass."""

    def test_create_flexure_result(self):
        """FlexureResult can be instantiated with required fields."""
        r = FlexureResult(
            Mu_lim=150.0,
            Ast_required=1200.0,
            pt_provided=0.89,
            section_type=DesignSectionType.UNDER_REINFORCED,
            xu=120.0,
            xu_max=200.0,
            is_safe=True,
        )
        assert r.Mu_lim == 150.0
        assert r.is_safe is True
        assert r.Asc_required == 0.0
        assert r.errors == []


class TestLoadDefinition:
    """Tests for LoadDefinition dataclass."""

    def test_udl_load(self):
        """UDL load defaults position to 0."""
        ld = LoadDefinition(load_type=LoadType.UDL, magnitude=20.0)
        assert ld.load_type == LoadType.UDL
        assert ld.magnitude == 20.0
        assert ld.position_mm == 0.0

    def test_point_load(self):
        """Point load with explicit position."""
        ld = LoadDefinition(
            load_type=LoadType.POINT, magnitude=50.0, position_mm=3000.0
        )
        assert ld.position_mm == 3000.0
        assert ld.end_position_mm is None


class TestTypesShim:
    """Tests for the types.py backward-compat shim."""

    def test_shim_imports_match_data_types(self):
        """types.py re-exports the same objects as data_types.py."""
        from structural_lib.core.data_types import BeamGeometry as BG_orig
        from structural_lib.types import BeamGeometry as BG_shim

        assert BG_shim is BG_orig

    def test_shim_re_exports_multiple_names(self):
        """types.py re-exports multiple names from core.types."""
        import structural_lib.types as types_mod

        # Verify key names are accessible
        assert hasattr(types_mod, "BeamGeometry")
        assert hasattr(types_mod, "FlexureResult")
        assert hasattr(types_mod, "ShearResult")
        assert hasattr(types_mod, "BeamType")
