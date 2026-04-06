"""
Contract tests - ensure API signatures never break accidentally.

These tests are CRITICAL: they prevent breaking changes from reaching users.
If a test here fails, it means you're about to break existing code.

WHEN A TEST FAILS:
1. Is this an intentional breaking change? → Bump major version (v0.x → v1.0)
2. Can you make it additive instead? → Add new parameter with default value
3. Is it a bug fix? → Update contract + add migration note to CHANGELOG

See: docs/research/backward-compatibility-strategy.md
"""

from __future__ import annotations

import inspect
from dataclasses import fields
from typing import get_type_hints

import pytest

from structural_lib import api
from structural_lib.codes.is456.beam.torsion import TorsionResult
from structural_lib.core.data_types import (
    BearingPressureCheckResult,
    ColumnAxialResult,
    ColumnBiaxialResult,
    ColumnUniaxialResult,
    ComplianceCaseResult,
    ComplianceReport,
    FlexureResult,
    FootingFlexureResult,
    FootingOneWayShearResult,
    FootingPunchingResult,
    PMInteractionResult,
    ShearResult,
)

# =============================================================================
# Frozen API Contracts (DO NOT CHANGE without major version bump)
# =============================================================================

# NOTE: These contracts test the MOST CRITICAL public APIs.
# Adding new optional parameters is OK. Removing/renaming breaks user code.

API_CONTRACTS = {
    # ── Beam contracts ─────────────────────────────────────────────────
    "design_beam_is456": {
        "required_params": [
            "units",
            "mu_knm",
            "vu_kn",
            "b_mm",
            "D_mm",
            "d_mm",
            "fck_nmm2",
            "fy_nmm2",
        ],
        "return_type": "ComplianceCaseResult",
    },
    "check_beam_is456": {
        "required_params": [
            "units",
            "cases",
            "b_mm",
            "D_mm",
            "d_mm",
            "fck_nmm2",
            "fy_nmm2",
        ],
        "return_type": "ComplianceReport",
    },
    # Note: detail_beam_is456, optimize_beam_cost, suggest_beam_design_improvements
    # have Dict return types currently. When they stabilize to dataclasses,
    # add them to this contract test.
    # ── Column contracts (IS 456 Cl 39) ────────────────────────────────
    "calculate_effective_length_is456": {
        "required_params": [
            "l_mm",
            "end_condition",
        ],
        "return_type": "dict",
    },
    "classify_column_is456": {
        "required_params": [
            "le_mm",
            "D_mm",
        ],
        "return_type": "str",
    },
    "min_eccentricity_is456": {
        "required_params": [
            "l_unsupported_mm",
            "D_mm",
        ],
        "return_type": "float",
    },
    "design_column_axial_is456": {
        "required_params": [
            "fck",
            "fy",
            "Ag_mm2",
            "Asc_mm2",
        ],
        "return_type": "ColumnAxialResult",
    },
    "design_short_column_uniaxial_is456": {
        "required_params": [
            "Pu_kN",
            "Mu_kNm",
            "b_mm",
            "D_mm",
            "le_mm",
            "fck",
            "fy",
            "Asc_mm2",
            "d_prime_mm",
        ],
        "return_type": "ColumnUniaxialResult",
    },
    "pm_interaction_curve_is456": {
        "required_params": [
            "b_mm",
            "D_mm",
            "fck",
            "fy",
            "Asc_mm2",
            "d_prime_mm",
        ],
        "return_type": "PMInteractionResult",
    },
    "biaxial_bending_check_is456": {
        "required_params": [
            "Pu_kN",
            "Mux_kNm",
            "Muy_kNm",
            "b_mm",
            "D_mm",
            "le_mm",
            "fck",
            "fy",
            "Asc_mm2",
            "d_prime_mm",
        ],
        "return_type": "ColumnBiaxialResult",
    },
    # ── Footing contracts (IS 456 Cl 34) ───────────────────────────────
    "check_bearing_pressure": {
        "required_params": [
            "Pu_kN",
            "fck",
            "column_b_mm",
            "column_D_mm",
            "footing_B_mm",
            "footing_L_mm",
        ],
        "return_type": "BearingPressureCheckResult",
    },
    "footing_flexure": {
        "required_params": [
            "Pu_kN",
            "L_mm",
            "B_mm",
            "d_mm",
            "a_mm",
            "b_mm",
            "fck",
            "fy",
        ],
        "return_type": "FootingFlexureResult",
    },
    "footing_one_way_shear": {
        "required_params": [
            "Pu_kN",
            "L_mm",
            "B_mm",
            "d_mm",
            "a_mm",
            "b_mm",
            "fck",
        ],
        "return_type": "FootingOneWayShearResult",
    },
    "footing_punching_shear": {
        "required_params": [
            "Pu_kN",
            "L_mm",
            "B_mm",
            "d_mm",
            "a_mm",
            "b_mm",
            "fck",
        ],
        "return_type": "FootingPunchingResult",
    },
    # ── Torsion contract (IS 456 Cl 41) ────────────────────────────────
    "design_torsion": {
        "required_params": [
            "tu_knm",
            "vu_kn",
            "mu_knm",
            "b",
            "D",
            "d",
            "fck",
            "fy",
            "cover",
        ],
        "return_type": "TorsionResult",
    },
}

DATACLASS_CONTRACTS = {
    # ── Beam result types ──────────────────────────────────────────────
    "FlexureResult": [
        "Mu_lim",
        "Ast_required",
        "pt_provided",
        "section_type",
        "xu",
        "xu_max",
        "is_safe",
        "Asc_required",
        "errors",
    ],
    "ShearResult": [
        "tau_v",
        "tau_c",
        "tau_c_max",
        "Vus",
        "spacing",
        "is_safe",
        "errors",
    ],
    "ComplianceCaseResult": [
        "case_id",
        "Mu_knm",
        "Vu_kn",
        "flexure",
        "shear",
        "is_ok",
        "governing_utilization",
        "utilizations",
        "failed_checks",
    ],
    "ComplianceReport": [
        "is_ok",
        "governing_case_id",
        "governing_utilization",
        "cases",
        "summary",
    ],
    # Note: BeamDetailingResult, SuggestionReport fields may evolve.
    # Add them when their structure stabilizes.
    # ── Column result types (IS 456 Cl 39) ─────────────────────────────
    "ColumnAxialResult": [
        "Pu_kN",
        "fck",
        "fy",
        "Ag_mm2",
        "Asc_mm2",
        "Ac_mm2",
        "steel_ratio",
        "classification",
        "is_safe",
        "warnings",
        "errors",
    ],
    "ColumnUniaxialResult": [
        "Pu_kN",
        "Mu_kNm",
        "Pu_cap_kN",
        "Mu_cap_kNm",
        "utilization_ratio",
        "eccentricity_mm",
        "e_min_mm",
        "is_safe",
        "classification",
        "governing_check",
        "clause_ref",
        "warnings",
    ],
    "PMInteractionResult": [
        "points",
        "Pu_0_kN",
        "Mu_0_kNm",
        "Pu_bal_kN",
        "Mu_bal_kNm",
        "fck",
        "fy",
        "b_mm",
        "D_mm",
        "Asc_mm2",
        "d_prime_mm",
        "clause_ref",
        "warnings",
    ],
    "ColumnBiaxialResult": [
        "Pu_kN",
        "Mux_kNm",
        "Muy_kNm",
        "Mux1_kNm",
        "Muy1_kNm",
        "Puz_kN",
        "alpha_n",
        "interaction_ratio",
        "is_safe",
        "classification",
        "clause_ref",
        "warnings",
    ],
    # ── Footing result types (IS 456 Cl 34) ────────────────────────────
    "BearingPressureCheckResult": [
        "actual_stress_mpa",
        "permissible_stress_mpa",
        "enhancement_factor",
        "utilization_ratio",
        "is_safe",
        "A1_mm2",
        "A2_mm2",
        "Pu_kN",
        "clause_ref",
    ],
    "FootingFlexureResult": [
        "Mu_L_kNm",
        "Ast_L_mm2",
        "pt_L_percent",
        "cantilever_L_mm",
        "Mu_B_kNm",
        "Ast_B_mm2",
        "pt_B_percent",
        "cantilever_B_mm",
        "d_mm",
        "is_safe",
        "central_band_fraction",
        "clause_ref",
        "warnings",
    ],
    "FootingOneWayShearResult": [
        "tau_v_nmm2",
        "tau_c_nmm2",
        "Vu_kN",
        "d_mm",
        "critical_section_mm",
        "utilization_ratio",
        "is_safe",
        "governing_direction",
        "clause_ref",
        "warnings",
    ],
    "FootingPunchingResult": [
        "tau_v_nmm2",
        "tau_c_nmm2",
        "perimeter_mm",
        "Vu_punch_kN",
        "d_mm",
        "beta_c",
        "ks",
        "utilization_ratio",
        "is_safe",
        "clause_ref",
        "warnings",
    ],
    # ── Torsion result type (IS 456 Cl 41) ─────────────────────────────
    "TorsionResult": [
        "Tu_knm",
        "Vu_kn",
        "Mu_knm",
        "Ve_kn",
        "Me_knm",
        "tau_ve",
        "tau_c",
        "tau_c_max",
        "Asv_torsion",
        "Asv_shear",
        "Asv_total",
        "stirrup_spacing",
        "Al_torsion",
        "is_safe",
        "requires_closed_stirrups",
        "errors",
    ],
}


# =============================================================================
# Contract Tests
# =============================================================================


@pytest.mark.contract
def test_api_function_signatures():
    """Ensure API function signatures haven't changed.

    This test verifies that all required parameters still exist and haven't
    become optional (which would be a breaking change for positional calls).
    """
    for func_name, contract in API_CONTRACTS.items():
        func = getattr(api, func_name)
        sig = inspect.signature(func)

        # Check required parameters exist
        param_names = list(sig.parameters.keys())
        for required in contract["required_params"]:
            assert required in param_names, (
                f"❌ BREAKING CHANGE: {func_name}() missing required param '{required}'\n"
                f"This will break existing user code that calls {func_name}({required}=...)."
            )

        # Check no required params were made optional
        # (new optional params are OK, changing required → optional is breaking)
        for param_name in contract["required_params"]:
            param = sig.parameters[param_name]
            assert param.default == inspect.Parameter.empty, (
                f"❌ BREAKING CHANGE: {func_name}('{param_name}') is now optional\n"
                f"This changes the function contract.\n"
                f"Fix: Keep the parameter required, or bump major version."
            )


@pytest.mark.contract
def test_api_return_types():
    """Ensure API return types haven't changed.

    Changes to return types break type checkers and user code that depends
    on specific attributes or methods.

    Functions that return built-in types (dict, str, float) are checked
    separately since they don't carry type annotations in the same way.
    """
    BUILTIN_RETURN_TYPES = {"dict", "str", "float", "int", "bool"}

    for func_name, contract in API_CONTRACTS.items():
        expected = contract["return_type"]

        # Skip built-in return types — they can't be verified from annotations
        # reliably (some functions lack return annotations for builtins)
        if expected in BUILTIN_RETURN_TYPES:
            continue

        func = getattr(api, func_name)
        hints = get_type_hints(func)

        assert "return" in hints, (
            f"❌ {func_name}() missing return type annotation\n"
            f"Public APIs must have explicit return types for contract stability."
        )

        # Return type name check (simplified)
        return_type = hints["return"]
        type_name = getattr(return_type, "__name__", str(return_type))

        assert expected in type_name or expected in str(return_type), (
            f"❌ BREAKING CHANGE: {func_name}() return type changed\n"
            f"Expected: {expected}, Got: {type_name}\n"
            f"Fix: Revert the return type, or bump major version."
        )


@pytest.mark.contract
def test_dataclass_fields_stable():
    """Ensure dataclass fields haven't been removed.

    Removing fields breaks user code that accesses them. Adding fields with
    defaults is OK (non-breaking).
    """
    dataclasses = {
        "FlexureResult": FlexureResult,
        "ShearResult": ShearResult,
        "ComplianceCaseResult": ComplianceCaseResult,
        "ComplianceReport": ComplianceReport,
        "ColumnAxialResult": ColumnAxialResult,
        "ColumnUniaxialResult": ColumnUniaxialResult,
        "PMInteractionResult": PMInteractionResult,
        "ColumnBiaxialResult": ColumnBiaxialResult,
        "BearingPressureCheckResult": BearingPressureCheckResult,
        "FootingFlexureResult": FootingFlexureResult,
        "FootingOneWayShearResult": FootingOneWayShearResult,
        "FootingPunchingResult": FootingPunchingResult,
        "TorsionResult": TorsionResult,
    }

    for class_name, expected_fields in DATACLASS_CONTRACTS.items():
        cls = dataclasses[class_name]
        actual_fields = {f.name for f in fields(cls)}

        for field_name in expected_fields:
            assert field_name in actual_fields, (
                f"❌ BREAKING CHANGE: {class_name}.{field_name} field removed\n"
                f"User code expecting this field will break.\n"
                f"Fix: Restore the field, or bump major version and document migration."
            )


# =============================================================================
# Column API Contract Tests (IS 456 Cl 39)
# =============================================================================


@pytest.mark.contract
def test_column_effective_length_contract():
    """Verify calculate_effective_length_is456 returns expected dict keys."""
    result = api.calculate_effective_length_is456(
        l_mm=3000.0, end_condition="FIXED_FIXED"
    )
    assert isinstance(result, dict)
    expected_keys = {"le_mm", "ratio", "end_condition", "method"}
    assert expected_keys.issubset(
        result.keys()
    ), f"Missing keys: {expected_keys - result.keys()}"
    assert isinstance(result["le_mm"], float)
    assert isinstance(result["ratio"], float)


@pytest.mark.contract
def test_column_classify_contract():
    """Verify classify_column_is456 returns a string classification."""
    result = api.classify_column_is456(le_mm=3000.0, D_mm=300.0)
    assert isinstance(result, str)
    assert result in ("SHORT", "SLENDER")


@pytest.mark.contract
def test_column_min_eccentricity_contract():
    """Verify min_eccentricity_is456 returns a float >= 20mm."""
    result = api.min_eccentricity_is456(l_unsupported_mm=3000.0, D_mm=300.0)
    assert isinstance(result, float)
    assert result >= 20.0  # IS 456 Cl 25.4 minimum


@pytest.mark.contract
def test_column_axial_contract():
    """Verify design_column_axial_is456 returns ColumnAxialResult with expected fields."""
    result = api.design_column_axial_is456(
        fck=25.0, fy=415.0, Ag_mm2=90000.0, Asc_mm2=1800.0
    )
    assert isinstance(result, ColumnAxialResult)
    assert hasattr(result, "Pu_kN")
    assert hasattr(result, "steel_ratio")
    assert hasattr(result, "is_safe")


@pytest.mark.contract
def test_column_uniaxial_contract():
    """Verify design_short_column_uniaxial_is456 returns ColumnUniaxialResult."""
    result = api.design_short_column_uniaxial_is456(
        Pu_kN=1200.0,
        Mu_kNm=150.0,
        b_mm=300.0,
        D_mm=450.0,
        le_mm=3000.0,
        fck=25.0,
        fy=415.0,
        Asc_mm2=2700.0,
        d_prime_mm=50.0,
    )
    assert isinstance(result, ColumnUniaxialResult)
    assert hasattr(result, "utilization_ratio")
    assert hasattr(result, "is_safe")
    assert hasattr(result, "classification")


@pytest.mark.contract
def test_column_pm_curve_contract():
    """Verify pm_interaction_curve_is456 returns PMInteractionResult."""
    result = api.pm_interaction_curve_is456(
        b_mm=300.0,
        D_mm=450.0,
        fck=25.0,
        fy=415.0,
        Asc_mm2=2700.0,
        d_prime_mm=50.0,
    )
    assert isinstance(result, PMInteractionResult)
    assert hasattr(result, "points")
    assert hasattr(result, "Pu_0_kN")
    assert hasattr(result, "Mu_bal_kNm")
    assert len(result.points) > 0


@pytest.mark.contract
def test_column_biaxial_contract():
    """Verify biaxial_bending_check_is456 returns ColumnBiaxialResult."""
    result = api.biaxial_bending_check_is456(
        Pu_kN=1200.0,
        Mux_kNm=80.0,
        Muy_kNm=60.0,
        b_mm=300.0,
        D_mm=450.0,
        le_mm=3000.0,
        fck=25.0,
        fy=415.0,
        Asc_mm2=2700.0,
        d_prime_mm=50.0,
    )
    assert isinstance(result, ColumnBiaxialResult)
    assert hasattr(result, "interaction_ratio")
    assert hasattr(result, "alpha_n")
    assert hasattr(result, "is_safe")


# =============================================================================
# Footing API Contract Tests (IS 456 Cl 34)
# =============================================================================


@pytest.mark.contract
def test_footing_bearing_pressure_contract():
    """Verify check_bearing_pressure returns BearingPressureCheckResult."""
    result = api.check_bearing_pressure(
        Pu_kN=1000.0,
        fck=25.0,
        column_b_mm=300.0,
        column_D_mm=300.0,
        footing_B_mm=1500.0,
        footing_L_mm=1500.0,
    )
    assert isinstance(result, BearingPressureCheckResult)
    assert hasattr(result, "actual_stress_mpa")
    assert hasattr(result, "permissible_stress_mpa")
    assert hasattr(result, "is_safe")
    assert hasattr(result, "utilization_ratio")


@pytest.mark.contract
def test_footing_flexure_contract():
    """Verify footing_flexure returns FootingFlexureResult."""
    result = api.footing_flexure(
        Pu_kN=1000.0,
        L_mm=1500.0,
        B_mm=1500.0,
        d_mm=400.0,
        a_mm=300.0,
        b_mm=300.0,
        fck=25.0,
        fy=415.0,
    )
    assert isinstance(result, FootingFlexureResult)
    assert hasattr(result, "Mu_L_kNm")
    assert hasattr(result, "Ast_L_mm2")
    assert hasattr(result, "Mu_B_kNm")
    assert hasattr(result, "Ast_B_mm2")
    assert hasattr(result, "is_safe")


@pytest.mark.contract
def test_footing_one_way_shear_contract():
    """Verify footing_one_way_shear returns FootingOneWayShearResult."""
    result = api.footing_one_way_shear(
        Pu_kN=1000.0,
        L_mm=1500.0,
        B_mm=1500.0,
        d_mm=400.0,
        a_mm=300.0,
        b_mm=300.0,
        fck=25.0,
    )
    assert isinstance(result, FootingOneWayShearResult)
    assert hasattr(result, "tau_v_nmm2")
    assert hasattr(result, "tau_c_nmm2")
    assert hasattr(result, "is_safe")
    assert hasattr(result, "governing_direction")


@pytest.mark.contract
def test_footing_punching_shear_contract():
    """Verify footing_punching_shear returns FootingPunchingResult."""
    result = api.footing_punching_shear(
        Pu_kN=1000.0,
        L_mm=1500.0,
        B_mm=1500.0,
        d_mm=400.0,
        a_mm=300.0,
        b_mm=300.0,
        fck=25.0,
    )
    assert isinstance(result, FootingPunchingResult)
    assert hasattr(result, "tau_v_nmm2")
    assert hasattr(result, "tau_c_nmm2")
    assert hasattr(result, "perimeter_mm")
    assert hasattr(result, "beta_c")
    assert hasattr(result, "is_safe")


# =============================================================================
# Torsion API Contract Tests (IS 456 Cl 41)
# =============================================================================


@pytest.mark.contract
def test_torsion_design_contract():
    """Verify design_torsion returns TorsionResult with expected fields."""
    result = api.design_torsion(
        tu_knm=10.0,
        vu_kn=100.0,
        mu_knm=80.0,
        b=300.0,
        D=500.0,
        d=450.0,
        fck=25.0,
        fy=415.0,
        cover=30.0,
    )
    assert isinstance(result, TorsionResult)
    assert hasattr(result, "Tu_knm")
    assert hasattr(result, "Ve_kn")
    assert hasattr(result, "Me_knm")
    assert hasattr(result, "Asv_total")
    assert hasattr(result, "Al_torsion")
    assert hasattr(result, "is_safe")
    assert result.requires_closed_stirrups is True  # Always True for torsion


@pytest.mark.contract
def test_schema_version_tracked():
    """Ensure schema version is bumped when JSON schemas change.

    The SCHEMA_VERSION constant allows clients to detect incompatible
    job.json or design_results.json formats.
    """
    from structural_lib import beam_pipeline

    assert hasattr(beam_pipeline, "SCHEMA_VERSION"), (
        "❌ CRITICAL: SCHEMA_VERSION constant removed\n"
        "This constant is used by clients to detect format changes."
    )

    version = beam_pipeline.SCHEMA_VERSION
    assert isinstance(version, int), "SCHEMA_VERSION must be an int"
    assert version >= 1, "SCHEMA_VERSION must be >= 1"


@pytest.mark.contract
def test_public_api_completeness():
    """Ensure all exported functions are documented in __all__.

    This prevents accidental breaking changes when reorganizing modules.
    """
    expected_exports = {
        "get_library_version",
        "validate_job_spec",
        "validate_design_results",
        "compute_detailing",
        "compute_bbs",
        "export_bbs",
        "compute_dxf",
        "compute_report",
        "compute_critical",
        "check_beam_ductility",
        "check_deflection_span_depth",
        "check_crack_width",
        "check_compliance_report",
        "design_beam_is456",
        "check_beam_is456",
        "detail_beam_is456",
        "optimize_beam_cost",
        "suggest_beam_design_improvements",
    }

    actual_exports = set(api.__all__)

    # Check no exports were removed
    for name in expected_exports:
        assert name in actual_exports, (
            f"❌ BREAKING CHANGE: '{name}' removed from api.__all__\n"
            f"This makes the function inaccessible via 'from structural_lib.services.api import *'.\n"
            f"Fix: Restore the export, or bump major version."
        )


@pytest.mark.contract
def test_units_parameter_backwards_compatible():
    """Ensure 'units' parameter still accepts all historical values.

    The library contract promises to accept 'IS456', 'IS 456', 'IS-456', etc.
    """
    from structural_lib import beam_pipeline

    # Historical units aliases that must continue to work
    historical_units = ["IS456", "IS 456", "is456"]

    for units_value in historical_units:
        try:
            beam_pipeline.validate_units(units_value)
        except ValueError:
            pytest.fail(
                f"❌ BREAKING CHANGE: Units value '{units_value}' no longer accepted\n"
                f"This breaks existing job.json files and user code.\n"
                f"Fix: Restore support for this units alias."
            )


# =============================================================================
# Usage as Standalone Script (for pre-commit hook)
# =============================================================================

if __name__ == "__main__":
    # Run contract tests standalone (for pre-commit hook)
    import sys

    pytest_args = [__file__, "-v", "-m", "contract", "--tb=short"]
    exit_code = pytest.main(pytest_args)
    sys.exit(exit_code)
