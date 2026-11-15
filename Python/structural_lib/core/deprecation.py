# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       deprecation
Description:  Deprecation utilities for marking deprecated functions and dataclass fields.
"""

from __future__ import annotations

import warnings
from collections.abc import Callable
from functools import wraps
from inspect import Parameter, Signature
from typing import Any, TypeVar, cast

F = TypeVar("F", bound=Callable)

__all__ = ["deprecated", "deprecated_field"]


def deprecated(
    version: str,
    remove_version: str,
    alternative: str | None = None,
    reason: str | None = None,
) -> Callable[[F], F]:
    """
    Mark a function or user-defined class as deprecated.

    Emits a DeprecationWarning on a function call or direct class construction.
    A decorated class keeps its identity.
    Use only when the owner has approved a real replacement and removal version.

    Parameters
    ----------
    version : str
        Version when deprecation was introduced (e.g., "0.14.0")
    remove_version : str
        Owner-approved version when the feature will be removed.
    alternative : str, optional
        Recommended replacement (e.g., "api.design_beam_is456")
    reason : str, optional
        Explanation of why the feature was deprecated

    Returns
    -------
    Callable
        Decorated function or the original class with a construction warning.

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
    - Metadata stored in __deprecated__ for introspection

    See Also
    --------
    deprecated_field : For deprecating dataclass fields
    """

    def decorator(func: F) -> F:
        def warning_message() -> str:
            message = (
                f"{func.__name__} is deprecated since v{version} "
                f"and will be removed in v{remove_version}."
            )
            if alternative:
                message += f" Use {alternative} instead."
            if reason:
                message += f" Reason: {reason}"
            return message

        metadata = {
            "version": version,
            "remove_version": remove_version,
            "alternative": alternative,
            "reason": reason,
        }

        if isinstance(func, type):
            original_new = func.__new__
            # With the default allocator the initializer owns the signature.
            signature_source = (
                cast(Any, func).__init__
                if original_new is object.__new__
                else original_new
            )

            @wraps(signature_source)
            def new(cls: type, /, *args: Any, **kwargs: Any) -> Any:
                if cls is func:
                    warnings.warn(warning_message(), DeprecationWarning, stacklevel=2)
                if original_new is not object.__new__:
                    return original_new(cls, *args, **kwargs)
                if cast(Any, cls).__init__ is object.__init__ and (args or kwargs):
                    raise TypeError(f"{cls.__name__}() takes no arguments")
                return object.__new__(cls)

            if signature_source is object.__init__:
                new.__signature__ = Signature(  # type: ignore[attr-defined]
                    [Parameter("cls", Parameter.POSITIONAL_ONLY)]
                )
            func.__new__ = staticmethod(new)  # type: ignore
            func.__deprecated__ = metadata  # type: ignore[attr-defined]
            return func

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            warnings.warn(warning_message(), DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        wrapper.__deprecated__ = metadata  # type: ignore
        return wrapper  # type: ignore

    return decorator


def deprecated_field(
    dataclass_name: str,
    field_name: str,
    version: str,
    remove_version: str,
    alternative: str | None = None,
    *,
    stacklevel: int = 3,
) -> None:
    """
    Emit deprecation warning for a dataclass field.

    Call this when constructing a record with a deprecated field.
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
    stacklevel : int, optional
        Warning depth. Use 4 in __post_init__ with a generated constructor.

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
    ...                 "0.14.0", "1.0.0", "errors", stacklevel=4
    ...             )

    Notes
    -----
    - The generated __init__ adds a frame between __post_init__ and its caller.
    - Only warn if field is actually used (check before calling)
    - Requires the same owner-approved replacement/removal evidence as @deprecated

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

    warnings.warn(message, DeprecationWarning, stacklevel=stacklevel)
