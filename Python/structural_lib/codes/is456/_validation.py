# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Private scalar validation shared by lower-level IS 456 helpers."""

from __future__ import annotations

import math
from numbers import Real


def require_finite_real(name: str, value: object) -> float:
    """Reject invalid scalars and return the finite real as a float."""
    if (
        isinstance(value, bool)
        or not isinstance(value, Real)
        or not math.isfinite(value)
    ):
        raise ValueError(f"{name} must be finite and real, got {value!r}")
    return float(value)


def require_range(
    name: str,
    value: object,
    *,
    minimum: float,
    maximum: float,
) -> float:
    """Require and return a finite real inside one inclusive domain."""
    numeric = require_finite_real(name, value)
    if not minimum <= numeric <= maximum:
        if numeric <= 0:
            raise ValueError(
                f"{name} must be positive and between {minimum:g} and "
                f"{maximum:g}, got {value!r}"
            )
        raise ValueError(
            f"{name} must be between {minimum:g} and {maximum:g}, got {value!r}"
        )
    return numeric
