"""Focused regressions for the IS 456 function-quality checker."""

from __future__ import annotations

import ast
from pathlib import Path

import scripts.check_function_quality as quality_checker
from pytest import MonkeyPatch
from scripts.check_function_quality import FunctionChecker


def test_checker_accepts_current_unit_names_objects_and_sample_counts() -> None:
    tree = ast.parse('''
@clause("38.1")
def sample(
    *,
    fck_nmm2: float,
    reinforcement: object,
    footing_input: object,
    theta_deg: float,
    n_depths: int,
) -> object:
    """Return one sample."""
    _validate_inputs()
    return object()
''')
    function = tree.body[0]
    assert isinstance(function, ast.FunctionDef)

    checks = {check.check_num: check for check in FunctionChecker(function).check_all()}

    assert 1 not in checks
    assert checks[9].passed is True
    assert checks[11].passed is True


def test_checker_accepts_case_insensitive_units_and_semantic_parameters() -> None:
    tree = ast.parse('''
@clause("38.1")
def sample(
    *,
    force_kn: float,
    moment_knm: float,
    pressure_kPa: float,
    enabled: bool,
    design_input: BeamInput,
    item_count: int,
    stress_ratio: float,
    strain: float,
) -> float:
    """Return one sample."""
    return force_kn + moment_knm + pressure_kPa
''')
    function = tree.body[0]
    assert isinstance(function, ast.FunctionDef)

    checks = {check.check_num: check for check in FunctionChecker(function).check_all()}

    assert checks[9].passed is True


def test_checker_keeps_ambiguous_numeric_names_as_failures() -> None:
    tree = ast.parse('''
@clause("38.1")
def sample(ambiguous: float) -> float:
    """Return one sample."""
    return ambiguous
''')
    function = tree.body[0]
    assert isinstance(function, ast.FunctionDef)

    checks = {check.check_num: check for check in FunctionChecker(function).check_all()}

    assert checks[9].passed is False
    assert checks[9].message == "Params missing unit suffix: ambiguous"


def test_exact_float_equality_requires_module_bound_review() -> None:
    tree = ast.parse('''
@clause("38.1")
def sample(value: float) -> bool:
    """Return whether the value is exactly zero."""
    return value == 0.0
''')
    function = tree.body[0]
    assert isinstance(function, ast.FunctionDef)

    checks = {check.check_num: check for check in FunctionChecker(function).check_all()}

    assert checks[5].passed is False
    assert "without module-bound review" in checks[5].message


def test_module_filter_ignores_matching_parent_worktree_name(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    is456_dir = tmp_path / "structural_engineering_lib-column-pmm-completion" / "is456"
    pmm_module = is456_dir / "column" / "pmm.py"
    other_module = is456_dir / "beam" / "flexure.py"
    pmm_module.parent.mkdir(parents=True)
    other_module.parent.mkdir(parents=True)
    pmm_module.write_text(
        '@clause("38.1")\ndef pmm_sample():\n    return 1\n', encoding="utf-8"
    )
    other_module.write_text(
        '@clause("38.1")\ndef flexure_sample():\n    return 1\n', encoding="utf-8"
    )
    monkeypatch.setattr(quality_checker, "IS456_DIR", is456_dir)

    reports = quality_checker.scan_all_modules("pmm")

    assert set(reports) == {"column/pmm.py"}


def test_current_clause_inventory_has_no_unreviewed_quality_failures() -> None:
    reports = quality_checker.scan_all_modules()
    flattened = [
        report for module_reports in reports.values() for report in module_reports
    ]

    assert flattened
    assert all(not report.has_failures for report in flattened)
    reviewed_float_functions = {
        f"{report.module}:{report.name}"
        for report in flattened
        if any(check.check_num == 5 and check.message for check in report.checks)
    }
    assert reviewed_float_functions == set(
        quality_checker.EXACT_FLOAT_COMPARISON_CONTRACTS
    )
