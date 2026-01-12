# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       utilities
Description:  Helper functions (Interpolation, Rounding, Validation, Deprecation)
"""

from __future__ import annotations

import warnings
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable)


def linear_interp(x: float, x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Linear Interpolation: y = y1 + (x - x1) * (y2 - y1) / (x2 - x1)
    """
    if (x2 - x1) == 0:
        return y1
    return y1 + (x - x1) * (y2 - y1) / (x2 - x1)


def round_to(value: float, digits: int) -> float:
    """
    Standard rounding function
    """
    return round(value, digits)


def mm_to_m(value_mm: float) -> float:
    """Convert millimeters to meters.

    Args:
        value_mm: Value in millimeters.

    Returns:
        Value in meters.

    Example:
        >>> mm_to_m(1500)
        1.5
    """
    return value_mm / 1000.0


def m_to_mm(value_m: float) -> float:
    """Convert meters to millimeters.

    Args:
        value_m: Value in meters.

    Returns:
        Value in millimeters.

    Example:
        >>> m_to_mm(1.5)
        1500.0
    """
    return value_m * 1000.0


def deprecated(
    version: str,
    remove_version: str,
    alternative: str | None = None,
    reason: str | None = None,
) -> Callable[[F], F]:
    """
    Mark a function or class as deprecated.

    Emits a DeprecationWarning when the decorated function is called.
    Follows the project deprecation policy: minimum 1 minor version before removal.

    Parameters
    ----------
    version : str
        Version when deprecation was introduced (e.g., "0.14.0")
    remove_version : str
        Version when feature will be removed (e.g., "1.0.0")
    alternative : str, optional
        Recommended replacement (e.g., "api.design_beam_is456")
    reason : str, optional
        Explanation of why the feature was deprecated

    Returns
    -------
    Callable
        Decorated function that emits deprecation warning

    Examples
    --------
    >>> @deprecated("0.14.0", "1.0.0", "api.design_beam_is456")
    ... def design_beam_old(b, d, fck, fy):
    ...     return design_beam_is456(b, d, fck, fy)

    >>> @deprecated("0.14.0", "1.0.0", reason="Replaced by structured error handling")
    ... def get_error_message():
    ...     pass

    Notes
    -----
    - DeprecationWarning is silenced by default in Python
    - Users can enable with: python -W default::DeprecationWarning
    - Or in code: warnings.simplefilter("default", DeprecationWarning)
    - Metadata stored in wrapper.__deprecated__ for introspection

    See Also
    --------
    deprecated_field : For deprecating dataclass fields
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            message = (
                f"{func.__name__} is deprecated since v{version} "
                f"and will be removed in v{remove_version}."
            )
            if alternative:
                message += f" Use {alternative} instead."
            if reason:
                message += f" Reason: {reason}"

            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        # Store metadata for introspection/testing
        wrapper.__deprecated__ = {  # type: ignore
            "version": version,
            "remove_version": remove_version,
            "alternative": alternative,
            "reason": reason,
        }

        return wrapper  # type: ignore

    return decorator


def deprecated_field(
    dataclass_name: str,
    field_name: str,
    version: str,
    remove_version: str,
    alternative: str | None = None,
) -> None:
    """
    Emit deprecation warning for a dataclass field.

    Call this in __post_init__ when a deprecated field is accessed.
    Used to warn about fields that will be removed in future versions.

    Parameters
    ----------
    dataclass_name : str
        Name of the dataclass (e.g., "FlexureResult")
    field_name : str
        Name of the deprecated field (e.g., "error_message")
    version : str
        Version when deprecation was introduced (e.g., "0.14.0")
    remove_version : str
        Version when field will be removed (e.g., "1.0.0")
    alternative : str, optional
        Recommended replacement field (e.g., "errors")

    Examples
    --------
    >>> @dataclass
    ... class FlexureResult:
    ...     error_message: str = ""  # Deprecated
    ...     errors: List[DesignError] = field(default_factory=list)
    ...
    ...     def __post_init__(self):
    ...         if self.error_message:
    ...             deprecated_field(
    ...                 "FlexureResult", "error_message",
    ...                 "0.14.0", "1.0.0", "errors"
    ...             )

    Notes
    -----
    - stacklevel=3 accounts for: this function → __post_init__ → user code
    - Only warn if field is actually used (check before calling)
    - Follows same policy as @deprecated decorator

    See Also
    --------
    deprecated : For deprecating functions and classes
    """
    message = (
        f"{dataclass_name}.{field_name} is deprecated since v{version} "
        f"and will be removed in v{remove_version}."
    )
    if alternative:
        message += f" Use {dataclass_name}.{alternative} instead."

    warnings.warn(message, DeprecationWarning, stacklevel=3)


__all__ = [
    "linear_interp",
    "round_to",
    "mm_to_m",
    "m_to_mm",
    "deprecated",
    "deprecated_field",
]
