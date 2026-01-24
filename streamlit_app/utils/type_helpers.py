# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Type conversion utilities for safe value handling.

Provides safe casting functions that handle None, invalid types,
and edge cases gracefully.

Created: 2026-01-24 (Session 70 - UI Duplication Fix)
"""

from __future__ import annotations

from typing import Optional, TypeVar, Union

T = TypeVar("T")


def safe_int(value: Union[str, int, float, None], default: int = 0) -> int:
    """Safely cast value to int with fallback.

    Args:
        value: Value to convert (str, int, float, or None)
        default: Fallback value if conversion fails

    Returns:
        Integer value or default

    Examples:
        >>> safe_int("123")
        123
        >>> safe_int(None, default=0)
        0
        >>> safe_int("invalid")
        0
    """
    try:
        return int(value)  # type: ignore
    except (TypeError, ValueError):
        return default


def safe_float(value: Union[str, int, float, None], default: float = 0.0) -> float:
    """Safely cast value to float with fallback.

    Args:
        value: Value to convert (str, int, float, or None)
        default: Fallback value if conversion fails

    Returns:
        Float value or default

    Examples:
        >>> safe_float("3.14")
        3.14
        >>> safe_float(None)
        0.0
    """
    try:
        return float(value)  # type: ignore
    except (TypeError, ValueError):
        return default


def safe_str(value: Optional[object], default: str = "") -> str:
    """Safely convert value to string with fallback.

    Args:
        value: Value to convert
        default: Fallback if value is None

    Returns:
        String representation or default
    """
    if value is None:
        return default
    return str(value)
