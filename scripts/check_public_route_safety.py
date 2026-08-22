#!/usr/bin/env python3
"""Run the frozen adversarial regressions for maintained public safety routes."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

PYTHON_TARGETS = (
    "Python/tests/unit/test_input_validation.py::test_flexure_design_singly_reinforced_rejects_non_finite_inputs",
    "Python/tests/unit/test_input_validation.py::test_shear_design_rejects_non_finite_inputs",
    "Python/tests/unit/test_compliance_validation.py::test_public_compliance_report_rejects_empty_cases",
    "Python/tests/unit/test_compliance_validation.py::test_compliance_case_rejects_non_finite_actions_before_calculation",
    "Python/tests/unit/test_compliance_validation.py::test_compliance_case_rejects_nonpositive_supplied_shear_steel",
    "Python/tests/test_is456_common.py::TestBeamFiniteNumericBoundary::test_design_rejects_unsupported_material_and_shear_domains",
    "Python/tests/codes/is456/column/test_uniaxial.py::TestUniaxialErrors::test_unrounded_utilization_controls_safety_at_display_boundary",
    "Python/tests/test_column_return_types.py::test_unified_column_rejects_infinite_moment_before_minimum_amplification",
    "Python/tests/test_column_return_types.py::test_unified_column_uses_current_uniaxial_safety_key",
    "Python/tests/test_column_return_types.py::test_unified_column_rejects_out_of_domain_reinforcement",
    "Python/tests/test_footing_api.py::test_unknown_provenance_origins_are_rejected",
    "Python/tests/codes/is456/slab/test_extended_workflows.py::test_complete_one_way_capacity_miss_returns_structured_fail",
    "Python/tests/codes/is456/slab/test_extended_workflows.py::test_complete_two_way_capacity_miss_returns_structured_fail",
    "Python/tests/unit/test_generic_csv_adapter.py::TestGenericCSVAdapterLoadForces::test_rejects_malformed_force_instead_of_coercing_zero",
    "Python/tests/test_boq.py::TestAggregateProjectBOQ::test_rejects_invalid_cost_domains",
    "Python/tests/test_evidence.py::test_unbounded_derived_utilization_is_a_structured_supported_failure",
)

FASTAPI_TARGETS = (
    "fastapi_app/tests/test_insights_dashboard.py::TestProjectBOQ::test_project_boq_rejects_negative_rates",
    "fastapi_app/tests/test_insights_dashboard.py::TestProjectBOQ::test_project_boq_rejects_non_positive_concrete_grade",
    "fastapi_app/tests/test_library_core.py::test_one_way_slab_capacity_miss_serializes_engineering_fail",
    "fastapi_app/tests/test_library_core.py::test_two_way_slab_capacity_miss_serializes_engineering_fail",
)


def _run_group(name: str, targets: tuple[str, ...], config: str | None = None) -> int:
    command = [sys.executable, "-m", "pytest"]
    if config is not None:
        command.extend(("-c", config))
    command.extend((*targets, "-q", "--tb=short"))

    try:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        print(f"ERROR: {name} timed out after 120 seconds", file=sys.stderr)
        return 1

    if result.stdout.strip():
        print(result.stdout.rstrip())
    if result.stderr.strip():
        print(result.stderr.rstrip(), file=sys.stderr)
    if result.returncode != 0:
        print(f"ERROR: {name} failed with exit {result.returncode}", file=sys.stderr)
        return 1

    return 0


def main() -> int:
    """Return zero only when every frozen Python and FastAPI regression passes."""

    groups = (
        ("Python public-route safety regressions", PYTHON_TARGETS, None),
        (
            "FastAPI public-route safety regressions",
            FASTAPI_TARGETS,
            "fastapi_app/pytest.ini",
        ),
    )
    for name, targets, config in groups:
        if _run_group(name, targets, config) != 0:
            return 1

    print(
        "Public-route safety gate passed "
        f"({len(PYTHON_TARGETS)} Python targets, "
        f"{len(FASTAPI_TARGETS)} FastAPI targets)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
