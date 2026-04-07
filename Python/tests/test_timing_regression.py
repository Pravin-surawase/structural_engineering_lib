# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Regression tests for Windows-compatible timing.

These tests ensure we use time.perf_counter() (nanosecond resolution on all platforms)
instead of time.time() (~15ms resolution on Windows) for elapsed time measurement.

Regression: GitHub Actions Windows CI failures — assert 0.0 > 0
"""

from __future__ import annotations

import ast
import pathlib

import pytest

# Files that MUST use time.perf_counter() for elapsed timing (not time.time())
TIMING_FILES = [
    "structural_lib/research/research_design_companion.py",
    "structural_lib/insights/smart_designer.py",
    "structural_lib/insights/design_suggestions.py",
    "structural_lib/services/optimization.py",
    "structural_lib/services/multi_objective_optimizer.py",
    "structural_lib/research/research_generative_design.py",
    "structural_lib/insights/precheck.py",
]


def _find_time_calls(filepath: pathlib.Path) -> dict:
    """Parse a Python file and find time.time() vs time.perf_counter() calls."""
    source = filepath.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(filepath))

    time_time_lines: list[int] = []
    perf_counter_lines: list[int] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            # Match time.time()
            if (
                isinstance(func, ast.Attribute)
                and func.attr == "time"
                and isinstance(func.value, ast.Name)
                and func.value.id == "time"
            ):
                time_time_lines.append(node.lineno)
            # Match time.perf_counter()
            elif (
                isinstance(func, ast.Attribute)
                and func.attr == "perf_counter"
                and isinstance(func.value, ast.Name)
                and func.value.id == "time"
            ):
                perf_counter_lines.append(node.lineno)

    return {"time_time": time_time_lines, "perf_counter": perf_counter_lines}


@pytest.mark.parametrize("relpath", TIMING_FILES)
def test_no_time_time_in_timing_files(relpath: str):
    """Ensure timing files use time.perf_counter(), not time.time().

    time.time() has ~15ms resolution on Windows, causing 0.0 elapsed times.
    time.perf_counter() has nanosecond resolution on all platforms.

    Regression: Windows CI failures in test_computation_time_recorded and
    test_smart_designer_metadata (assert 0.0 > 0).
    """
    lib_root = pathlib.Path(__file__).parent.parent / relpath
    if not lib_root.exists():
        pytest.skip(f"{relpath} not found")

    calls = _find_time_calls(lib_root)

    assert not calls["time_time"], (
        f"{relpath} uses time.time() at line(s) {calls['time_time']}. "
        f"Use time.perf_counter() instead for elapsed time measurement. "
        f"time.time() has ~15ms resolution on Windows."
    )
    assert calls["perf_counter"], (
        f"{relpath} should use time.perf_counter() for elapsed timing "
        f"but no calls found."
    )
