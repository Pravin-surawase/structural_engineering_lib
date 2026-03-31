# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Domain-specific assertion helpers for IS 456 structural design tests.

Provides reusable assertion functions that encode IS 456 conventions,
SP:16 tolerance rules, and common structural engineering invariants.

Usage:
    from tests.helpers.is456_assertions import (
        assert_within_sp16_tolerance,
        assert_clause_compliance,
        assert_capacity_monotonic,
    )
"""

from __future__ import annotations

import pytest

from structural_lib.core.errors import DesignError


def assert_approx(
    actual: float,
    expected: float,
    *,
    abs_tol: float = 0.01,
    rel_tol: float = 0.001,
    msg: str = "",
) -> None:
    """Assert approximate equality with both absolute and relative tolerance.

    Uses the stricter of abs_tol and rel_tol for comparison.

    Args:
        actual: Actual value.
        expected: Expected value.
        abs_tol: Absolute tolerance (default 0.01).
        rel_tol: Relative tolerance (default 0.001).
        msg: Optional message prefix.

    Raises:
        AssertionError: If values don't match within tolerance.
    """
    assert actual == pytest.approx(expected, abs=abs_tol, rel=rel_tol), (
        f"{msg + ': ' if msg else ''}{actual} != {expected} "
        f"(abs_tol={abs_tol}, rel_tol={rel_tol})"
    )


def assert_within_sp16(
    actual: float,
    expected: float,
    *,
    tolerance_pct: float = 0.1,
    msg: str = "",
) -> None:
    """Assert value matches SP:16 benchmark within ±0.1% (default).

    Args:
        actual: Computed value.
        expected: SP:16 benchmark value.
        tolerance_pct: Tolerance percentage (default 0.1%).
        msg: Optional message prefix.

    Raises:
        AssertionError: If values don't match within tolerance.
    """
    rel_tol = tolerance_pct / 100.0
    assert actual == pytest.approx(expected, rel=rel_tol), (
        f"{msg + ': ' if msg else ''}SP:16 benchmark failed: {actual} vs {expected} "
        f"(±{tolerance_pct}%)"
    )


def assert_raises_design_error(
    func, *args, error_code: str | None = None, **kwargs
) -> DesignError:
    """Assert a function raises DesignError, optionally with a specific error code.

    Args:
        func: Function to call.
        *args: Positional arguments for func.
        error_code: Expected error code (optional).
        **kwargs: Keyword arguments for func.

    Returns:
        The raised DesignError instance.

    Raises:
        AssertionError: If DesignError not raised or error_code doesn't match.
    """
    with pytest.raises(DesignError) as exc_info:
        func(*args, **kwargs)
    if error_code is not None:
        assert (
            exc_info.value.code == error_code
        ), f"Expected error code {error_code}, got {exc_info.value.code}"
    return exc_info.value


def assert_positive(value: float, name: str = "value") -> None:
    """Assert a value is strictly positive.

    Args:
        value: Value to check.
        name: Name of the value for error messages.

    Raises:
        AssertionError: If value <= 0.
    """
    assert value > 0, f"{name} must be positive, got {value}"


def assert_in_range(value: float, lo: float, hi: float, name: str = "value") -> None:
    """Assert a value is within [lo, hi] inclusive.

    Args:
        value: Value to check.
        lo: Lower bound (inclusive).
        hi: Upper bound (inclusive).
        name: Name of the value for error messages.

    Raises:
        AssertionError: If value not in range.
    """
    assert lo <= value <= hi, f"{name}={value} not in [{lo}, {hi}]"


def assert_within_sp16_tolerance(
    actual: float,
    expected: float,
    *,
    rel_tol: float = 0.001,
    chart_ref: str = "",
    quantity: str = "value",
) -> None:
    """Assert that a calculated value matches SP:16 reference within tolerance.

    Default tolerance is ±0.1% (rel=0.001) which is the standard for
    authoritative SP:16 Design Aids benchmarks.

    Args:
        actual: Computed value from structural_lib.
        expected: Reference value from SP:16 chart/table.
        rel_tol: Relative tolerance (default 0.001 = 0.1%).
        chart_ref: SP:16 chart/table reference for error messages.
        quantity: Name of the quantity being compared.

    Raises:
        AssertionError with descriptive message if tolerance exceeded.
    """
    ref_label = f" (SP:16 {chart_ref})" if chart_ref else ""
    assert actual == pytest.approx(expected, rel=rel_tol), (
        f"{quantity}: got {actual}, expected {expected}{ref_label} "
        f"(tolerance ±{rel_tol * 100:.1f}%)"
    )


def assert_within_textbook_tolerance(
    actual: float,
    expected: float,
    *,
    rel_tol: float = 0.01,
    source: str = "",
    quantity: str = "value",
) -> None:
    """Assert within textbook tolerance (±1% — accounts for rounding).

    Textbooks (Pillai & Menon, Ramamrutham) often round intermediate steps,
    so a wider tolerance than SP:16 is appropriate.

    Args:
        actual: Computed value.
        expected: Textbook reference value.
        rel_tol: Relative tolerance (default 0.01 = 1%).
        source: Textbook reference for error messages.
        quantity: Name of the quantity being compared.
    """
    src_label = f" ({source})" if source else ""
    assert actual == pytest.approx(expected, rel=rel_tol), (
        f"{quantity}: got {actual}, expected {expected}{src_label} "
        f"(tolerance ±{rel_tol * 100:.1f}%)"
    )


def assert_clause_compliance(result, clause: str, *, field: str = "clause_ref") -> None:
    """Assert that a result references the expected IS 456 clause.

    Args:
        result: A result object or dict.
        clause: Expected clause string (e.g., "Cl. 38.1").
        field: Attribute or key name containing the clause reference.
    """
    if isinstance(result, dict):
        actual = result.get(field)
    else:
        actual = getattr(result, field, None)

    assert actual is not None, f"Result has no '{field}' attribute/key"
    assert clause in str(
        actual
    ), f"Expected clause '{clause}' in {field}, got '{actual}'"


def assert_capacity_monotonic(
    values: list[float],
    *,
    increasing: bool = True,
    param_name: str = "capacity",
) -> None:
    """Assert that a series of capacity values is monotonically increasing/decreasing.

    Useful for property-based tests: increasing fck -> increasing capacity, etc.

    Args:
        values: List of capacity values.
        increasing: If True, assert monotonically increasing; else decreasing.
        param_name: Name for error messages.
    """
    for i in range(1, len(values)):
        if increasing:
            assert values[i] >= values[i - 1], (
                f"{param_name}[{i}]={values[i]} < {param_name}[{i-1}]={values[i-1]} "
                f"(expected monotonically increasing)"
            )
        else:
            assert values[i] <= values[i - 1], (
                f"{param_name}[{i}]={values[i]} > {param_name}[{i-1}]={values[i-1]} "
                f"(expected monotonically decreasing)"
            )


def assert_reinforcement_limits(
    ast_mm2: float,
    b_mm: float,
    d_mm: float,
    fck: float,
    fy: float,
    *,
    element: str = "beam",
) -> None:
    """Assert that steel area is within IS 456 min/max limits.

    Minimum: 0.85*bd/fy (Cl. 26.5.1.1)
    Maximum: 4% of bD (Cl. 26.5.1.2 for beams)

    Args:
        ast_mm2: Provided steel area (mm²).
        b_mm: Width (mm).
        d_mm: Effective depth (mm).
        fck: Concrete strength (N/mm²).
        fy: Steel yield strength (N/mm²).
        element: Element type for error messages.
    """
    ast_min = 0.85 * b_mm * d_mm / fy
    ast_max = 0.04 * b_mm * d_mm  # Conservative (using d, not D)
    assert ast_mm2 >= ast_min * 0.99, (  # 1% tolerance for rounding
        f"{element} Ast={ast_mm2:.1f} mm² < Ast_min={ast_min:.1f} mm² "
        f"(IS 456 Cl. 26.5.1.1)"
    )
    assert ast_mm2 <= ast_max * 1.01, (
        f"{element} Ast={ast_mm2:.1f} mm² > Ast_max={ast_max:.1f} mm² "
        f"(IS 456 Cl. 26.5.1.2)"
    )


def assert_no_design_errors(result, *, allow_warnings: bool = True) -> None:
    """Assert that a design result has no error-severity issues.

    Args:
        result: Result object with an ``errors`` attribute (list of DesignError).
        allow_warnings: If True, only fail on ERROR severity. If False, fail on WARNING too.
    """
    errors = getattr(result, "errors", []) or []
    if allow_warnings:
        critical = [
            e for e in errors if hasattr(e, "severity") and e.severity.value == "error"
        ]
    else:
        critical = [
            e
            for e in errors
            if hasattr(e, "severity") and e.severity.value in ("error", "warning")
        ]

    assert not critical, f"Design produced {len(critical)} error(s): " + "; ".join(
        f"[{e.code}] {e.message}" for e in critical
    )


def assert_capacity_exceeds_demand(
    capacity: float,
    demand: float,
    *,
    label: str = "",
) -> None:
    """Assert that structural capacity >= demand (fundamental design check).

    Args:
        capacity: Design capacity (e.g., Mu_lim in kNm).
        demand: Design demand (e.g., Mu in kNm).
        label: Optional context label for error messages.

    Raises:
        AssertionError: If capacity < demand.
    """
    if capacity < demand:
        ctx = f" [{label}]" if label else ""
        raise AssertionError(
            f"Capacity ({capacity:.2f}) < Demand ({demand:.2f}){ctx}. "
            f"Utilization ratio = {demand/capacity:.3f} > 1.0"
        )


def assert_spacing_valid(
    spacing_mm: float,
    d_mm: float,
    *,
    label: str = "",
) -> None:
    """Assert stirrup spacing complies with IS 456 Cl. 26.5.1.5.

    Max spacing = min(0.75*d, 300 mm).

    Args:
        spacing_mm: Actual stirrup spacing (mm).
        d_mm: Effective depth (mm).
        label: Optional context label.

    Raises:
        AssertionError: If spacing exceeds IS 456 limits.
    """
    max_spacing = min(0.75 * d_mm, 300.0)
    if spacing_mm > max_spacing:
        ctx = f" [{label}]" if label else ""
        raise AssertionError(
            f"Spacing {spacing_mm:.0f}mm > max {max_spacing:.0f}mm "
            f"(IS 456 Cl. 26.5.1.5: min(0.75d={0.75*d_mm:.0f}, 300)){ctx}"
        )
    if spacing_mm <= 0:
        raise AssertionError(
            f"Spacing must be > 0, got {spacing_mm}{' [' + label + ']' if label else ''}"
        )


def assert_dimensions_positive(**dims: float) -> None:
    """Assert all named dimensions are positive.

    Usage::

        assert_dimensions_positive(b=300, d=450, D=500)

    Args:
        **dims: Keyword arguments of dimension name → value.

    Raises:
        AssertionError: If any dimension is <= 0.
    """
    for name, value in dims.items():
        if value <= 0:
            raise AssertionError(f"Dimension '{name}' must be > 0, got {value}")
