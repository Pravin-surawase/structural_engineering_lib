"""Regression tests for nested element completeness discovery."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "check_new_element_completeness.py"
)
SPEC = importlib.util.spec_from_file_location(
    "check_new_element_completeness", SCRIPT_PATH
)
assert SPEC is not None and SPEC.loader is not None
checker = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = checker
SPEC.loader.exec_module(checker)


def test_nested_staircase_test_package_is_discovered() -> None:
    result = checker.check_tests("staircase", verbose=True)

    assert result["test_functions"] >= 19
    assert any(path.endswith("staircase/test_design.py") for path in result["files"])
    assert any(
        path.endswith("staircase/test_geometry_actions.py") for path in result["files"]
    )


def test_code_or_service_layer_staircase_result_type_is_discovered() -> None:
    result = checker.check_types("staircase", verbose=True)

    assert result["result_type"] is True
    assert any(path.endswith("services/staircase_api.py") for path in result["files"])


def test_reexported_staircase_public_api_is_discovered() -> None:
    result = checker.check_api("staircase", verbose=True)

    assert result["has_api"] is True
    assert "design_straight_flight_staircase_is456" in result["function_names"]
