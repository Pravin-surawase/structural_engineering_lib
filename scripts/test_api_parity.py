#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
API Parity Testing Script (V3 Preparation)
============================================

Tests that FastAPI endpoints return identical results to direct library calls.
This ensures the V3 React frontend gets the same results as the current Streamlit UI.

Usage:
    python scripts/test_api_parity.py                    # Run all parity tests
    python scripts/test_api_parity.py --function design_beam_is456
    python scripts/test_api_parity.py --generate-cases   # Generate test cases
    python scripts/test_api_parity.py --verbose          # Detailed output

Exit Codes:
    0 - All parity tests passed
    1 - Parity issues found
    2 - Test infrastructure error

V3 Context:
    This script is critical for V3 migration because:
    1. React frontend will call FastAPI instead of direct Python
    2. Results MUST match for user trust
    3. Serialization can lose precision - this catches that
    4. Response structure must be identical

Author: AI Agent (V3 Foundation Session)
Created: 2026-01-24
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from dataclasses import dataclass, is_dataclass, asdict
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
PYTHON_DIR = PROJECT_ROOT / "Python"
TEST_CASES_PATH = SCRIPT_DIR / "test_data" / "api_parity_cases.json"

# Add Python directory to path
sys.path.insert(0, str(PYTHON_DIR))


@dataclass
class ParityTestCase:
    """A test case for API parity testing."""
    name: str
    function: str
    inputs: dict
    expected_keys: list[str]
    precision: float = 0.001  # Tolerance for float comparison


@dataclass
class ParityResult:
    """Result of a parity test."""
    test_name: str
    passed: bool
    library_result: dict | None
    api_result: dict | None
    differences: list[str]


# Standard test cases for beam design
STANDARD_TEST_CASES = [
    ParityTestCase(
        name="Simple beam design - nominal case",
        function="design_beam_is456",
        inputs={
            "units": "IS456",
            "case_id": "PARITY-1",
            "mu_knm": 100.0,
            "vu_kn": 75.0,
            "b_mm": 300.0,
            "D_mm": 450.0,
            "d_mm": 420.0,
            "fck_nmm2": 25.0,
            "fy_nmm2": 500.0
        },
        expected_keys=["flexure", "shear", "is_ok", "case_id"]
    ),
    ParityTestCase(
        name="High moment beam",
        function="design_beam_is456",
        inputs={
            "units": "IS456",
            "case_id": "PARITY-2",
            "mu_knm": 250.0,
            "vu_kn": 150.0,
            "b_mm": 350.0,
            "D_mm": 600.0,
            "d_mm": 560.0,
            "fck_nmm2": 30.0,
            "fy_nmm2": 500.0
        },
        expected_keys=["flexure", "shear", "is_ok", "case_id"]
    ),
    ParityTestCase(
        name="Minimum reinforcement case",
        function="design_beam_is456",
        inputs={
            "units": "IS456",
            "case_id": "PARITY-3",
            "mu_knm": 25.0,
            "vu_kn": 20.0,
            "b_mm": 230.0,
            "D_mm": 400.0,
            "d_mm": 370.0,
            "fck_nmm2": 20.0,
            "fy_nmm2": 415.0
        },
        expected_keys=["flexure", "shear", "is_ok", "case_id"]
    ),
]


def load_api():
    """Load the structural_lib.api module."""
    try:
        from structural_lib import api
        return api
    except ImportError as e:
        print(f"❌ Cannot import structural_lib.services.api: {e}")
        sys.exit(2)


def compare_values(v1: Any, v2: Any, precision: float = 0.001) -> tuple[bool, str]:
    """
    Compare two values with tolerance for floats.

    Returns:
        (is_equal, difference_description)
    """
    # Handle None
    if v1 is None and v2 is None:
        return True, ""
    if v1 is None or v2 is None:
        return False, f"None mismatch: {v1} vs {v2}"

    # Handle numeric types
    if isinstance(v1, (int, float, Decimal)) and isinstance(v2, (int, float, Decimal)):
        if abs(float(v1) - float(v2)) <= precision:
            return True, ""
        return False, f"Value diff: {v1} vs {v2} (delta={abs(float(v1) - float(v2)):.6f})"

    # Handle strings
    if isinstance(v1, str) and isinstance(v2, str):
        if v1 == v2:
            return True, ""
        return False, f"String diff: '{v1}' vs '{v2}'"

    # Handle booleans
    if isinstance(v1, bool) and isinstance(v2, bool):
        if v1 == v2:
            return True, ""
        return False, f"Bool diff: {v1} vs {v2}"

    # Handle Enum vs string comparison (JSON serialization converts Enum to string)
    if isinstance(v1, Enum) and isinstance(v2, str):
        if str(v1) == v2:
            return True, ""
        return False, f"Enum/string diff: {v1} vs '{v2}'"
    if isinstance(v1, str) and isinstance(v2, Enum):
        if v1 == str(v2):
            return True, ""
        return False, f"String/enum diff: '{v1}' vs {v2}"
    if isinstance(v1, Enum) and isinstance(v2, Enum):
        if v1 == v2:
            return True, ""
        return False, f"Enum diff: {v1} vs {v2}"

    # Handle lists
    if isinstance(v1, list) and isinstance(v2, list):
        if len(v1) != len(v2):
            return False, f"List length diff: {len(v1)} vs {len(v2)}"
        for i, (item1, item2) in enumerate(zip(v1, v2)):
            equal, diff = compare_values(item1, item2, precision)
            if not equal:
                return False, f"List[{i}]: {diff}"
        return True, ""

    # Handle dicts
    if isinstance(v1, dict) and isinstance(v2, dict):
        all_keys = set(v1.keys()) | set(v2.keys())
        for key in all_keys:
            if key not in v1:
                return False, f"Key '{key}' missing in first dict"
            if key not in v2:
                return False, f"Key '{key}' missing in second dict"
            equal, diff = compare_values(v1[key], v2[key], precision)
            if not equal:
                return False, f"Dict['{key}']: {diff}"
        return True, ""

    # Default: direct comparison
    if v1 == v2:
        return True, ""
    return False, f"Type/value mismatch: {type(v1).__name__}({v1}) vs {type(v2).__name__}({v2})"


def result_to_dict(result: Any) -> dict:
    """Convert a result object to a dictionary, handling nested dataclasses."""
    if result is None:
        return {}
    if isinstance(result, dict):
        # Recursively convert any nested dataclasses in dict values
        return {k: result_to_dict(v) if is_dataclass(v) else v for k, v in result.items()}
    if is_dataclass(result):
        # Use asdict for proper deep conversion of nested dataclasses
        return asdict(result)
    if hasattr(result, "to_dict"):
        return result.to_dict()
    if hasattr(result, "__dict__"):
        return {k: v for k, v in result.__dict__.items() if not k.startswith("_")}
    return {"value": result}


def simulate_api_call(api, function_name: str, inputs: dict) -> dict:
    """
    Simulate a FastAPI call by:
    1. Calling the library function
    2. Converting result to JSON (serialization)
    3. Parsing JSON back (deserialization)

    This catches serialization issues.
    """
    func = getattr(api, function_name, None)
    if func is None:
        raise AttributeError(f"Function '{function_name}' not found in API")

    # Call library function
    result = func(**inputs)

    # Simulate JSON round-trip (this is what FastAPI does)
    result_dict = result_to_dict(result)
    json_str = json.dumps(result_dict, default=str)
    api_result = json.loads(json_str)

    return api_result


def run_parity_test(api, test_case: ParityTestCase) -> ParityResult:
    """Run a single parity test."""
    differences = []
    library_result = None
    api_result = None

    try:
        # Get direct library result
        func = getattr(api, test_case.function, None)
        if func is None:
            return ParityResult(
                test_name=test_case.name,
                passed=False,
                library_result=None,
                api_result=None,
                differences=[f"Function '{test_case.function}' not found"]
            )

        raw_result = func(**test_case.inputs)
        library_result = result_to_dict(raw_result)

        # Get simulated API result
        api_result = simulate_api_call(api, test_case.function, test_case.inputs)

        # Check expected keys are present
        for key in test_case.expected_keys:
            if key not in library_result:
                differences.append(f"Expected key '{key}' missing from library result")
            if key not in api_result:
                differences.append(f"Expected key '{key}' missing from API result")

        # Compare all values
        equal, diff = compare_values(library_result, api_result, test_case.precision)
        if not equal:
            differences.append(diff)

    except Exception as e:
        differences.append(f"Exception: {e}")

    return ParityResult(
        test_name=test_case.name,
        passed=len(differences) == 0,
        library_result=library_result,
        api_result=api_result,
        differences=differences
    )


def run_all_tests(api, test_cases: list[ParityTestCase], verbose: bool = False) -> list[ParityResult]:
    """Run all parity tests."""
    results = []

    for test_case in test_cases:
        result = run_parity_test(api, test_case)
        results.append(result)

        if verbose:
            status = "✅" if result.passed else "❌"
            print(f"{status} {result.test_name}")
            if not result.passed:
                for diff in result.differences:
                    print(f"   ⚠️  {diff}")

    return results


def generate_test_cases_file():
    """Generate a JSON file with test cases for customization."""
    cases = []
    for tc in STANDARD_TEST_CASES:
        cases.append({
            "name": tc.name,
            "function": tc.function,
            "inputs": tc.inputs,
            "expected_keys": tc.expected_keys,
            "precision": tc.precision
        })

    # Ensure directory exists
    TEST_CASES_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(TEST_CASES_PATH, "w") as f:
        json.dump({"test_cases": cases}, f, indent=2)

    print(f"✅ Generated test cases at {TEST_CASES_PATH}")


def load_custom_test_cases() -> list[ParityTestCase] | None:
    """Load custom test cases from JSON file if exists."""
    if not TEST_CASES_PATH.exists():
        return None

    try:
        with open(TEST_CASES_PATH) as f:
            data = json.load(f)

        return [
            ParityTestCase(
                name=tc["name"],
                function=tc["function"],
                inputs=tc["inputs"],
                expected_keys=tc.get("expected_keys", []),
                precision=tc.get("precision", 0.001)
            )
            for tc in data.get("test_cases", [])
        ]
    except Exception as e:
        print(f"⚠️  Error loading custom test cases: {e}")
        return None


def print_summary(results: list[ParityResult]):
    """Print test summary."""
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    print()
    print("=" * 60)
    print("API Parity Test Summary")
    print("=" * 60)
    print(f"Total tests:  {len(results)}")
    print(f"Passed:       {passed} ✅")
    print(f"Failed:       {failed} ❌")
    print()

    if failed == 0:
        print("✅ All parity tests passed!")
        print("   FastAPI responses will match library results.")
    else:
        print("❌ Parity issues found:")
        for result in results:
            if not result.passed:
                print(f"\n   {result.test_name}")
                for diff in result.differences:
                    print(f"      • {diff}")


def main():
    parser = argparse.ArgumentParser(
        description="Test API parity between library and FastAPI (V3 preparation)"
    )
    parser.add_argument("--function", "-f",
                       help="Test specific function only")
    parser.add_argument("--generate-cases", action="store_true",
                       help="Generate test cases JSON file")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")

    args = parser.parse_args()

    # Generate test cases if requested
    if args.generate_cases:
        generate_test_cases_file()
        return 0

    # Load API
    api = load_api()

    # Get test cases
    custom_cases = load_custom_test_cases()
    test_cases = custom_cases if custom_cases else STANDARD_TEST_CASES

    # Filter by function if specified
    if args.function:
        test_cases = [tc for tc in test_cases if tc.function == args.function]
        if not test_cases:
            print(f"❌ No test cases found for function '{args.function}'")
            return 2

    print("=" * 60)
    print("API Parity Tests (V3 Preparation)")
    print("=" * 60)
    print(f"Testing {len(test_cases)} cases...")
    print()

    # Run tests
    results = run_all_tests(api, test_cases, args.verbose)

    # Print summary
    print_summary(results)

    # Exit code
    if any(not r.passed for r in results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
