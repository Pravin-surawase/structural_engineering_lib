"""Numeric safety utilities for structural calculations.

Provides safe arithmetic operations and comparison functions to prevent
division-by-zero errors and floating-point comparison issues in
structural design calculations.
"""

import math

# Threshold below which a denominator is considered zero for division safety
ZERO_THRESHOLD: float = 1e-12


def safe_divide(
    numerator: float,
    denominator: float,
    default: float = 0.0,
) -> float:
    """Safely divide two numbers, returning default if denominator is near zero.

    In structural engineering, silently returning a default on division-by-zero
    can mask errors. Callers should choose *default* deliberately --- e.g. use
    ``float('inf')`` or raise an exception upstream when a zero denominator
    indicates a real problem.

    Args:
        numerator: Dividend.
        denominator: Divisor.
        default: Value returned when |denominator| < ZERO_THRESHOLD.

    Returns:
        numerator / denominator, or *default* if denominator is near zero.
    """
    if abs(denominator) < ZERO_THRESHOLD:
        return default
    return numerator / denominator


def approx_equal(
    a: float,
    b: float,
    rel_tol: float = 1e-9,
    abs_tol: float = 0.0,
) -> bool:
    """Check whether two floats are approximately equal.

    Thin wrapper around :func:`math.isclose` with project-standard defaults.

    Args:
        a: First value.
        b: Second value.
        rel_tol: Maximum relative tolerance (default 1e-9).
        abs_tol: Maximum absolute tolerance (default 0.0).

    Returns:
        True if ``a`` and ``b`` are within the specified tolerances.
    """
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp *value* to the inclusive range [min_val, max_val].

    Args:
        value: The value to clamp.
        min_val: Lower bound (inclusive).
        max_val: Upper bound (inclusive).

    Returns:
        Clamped value.

    Raises:
        ValueError: If min_val > max_val.
    """
    if min_val > max_val:
        raise ValueError(f"min_val ({min_val}) must be <= max_val ({max_val})")
    return max(min_val, min(value, max_val))
