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
from structural_lib.core.data_types import (
    ComplianceCaseResult,
    ComplianceReport,
    FlexureResult,
    ShearResult,
)

# =============================================================================
# Frozen API Contracts (DO NOT CHANGE without major version bump)
# =============================================================================

# NOTE: These contracts test the MOST CRITICAL public APIs.
# Adding new optional parameters is OK. Removing/renaming breaks user code.

API_CONTRACTS = {
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
}

DATACLASS_CONTRACTS = {
    "FlexureResult": [
        "mu_lim",
        "ast_required",
        "pt_provided",
        "section_type",
        "xu",
        "xu_max",
        "is_safe",
        "asc_required",
        "errors",
    ],
    "ShearResult": [
        "tv",
        "tc",
        "tc_max",
        "vus",
        "spacing",
        "is_safe",
        "errors",
    ],
    "ComplianceCaseResult": [
        "case_id",
        "mu_knm",
        "vu_kn",
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
    """
    for func_name, contract in API_CONTRACTS.items():
        func = getattr(api, func_name)
        hints = get_type_hints(func)

        assert "return" in hints, (
            f"❌ {func_name}() missing return type annotation\n"
            f"Public APIs must have explicit return types for contract stability."
        )

        # Return type name check (simplified)
        return_type = hints["return"]
        type_name = getattr(return_type, "__name__", str(return_type))
        expected = contract["return_type"]

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
            f"This makes the function inaccessible via 'from structural_lib.api import *'.\n"
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
