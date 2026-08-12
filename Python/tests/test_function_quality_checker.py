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

    assert checks[9].passed is True
    assert checks[11].passed is True


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
