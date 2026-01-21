"""
Error boundary decorators for cost optimizer.

Provides safe error handling that prevents crashes and provides user-friendly feedback.
"""

import functools
import logging
from typing import Any, Callable, TypeVar, Optional
import streamlit as st

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def error_boundary(
    fallback_value: Any = None, show_error: bool = True, log_error: bool = True
) -> Callable[[F], F]:
    """
    Decorator that catches exceptions and provides safe fallback.

    Args:
        fallback_value: Value to return if error occurs
        show_error: Whether to show error message to user
        log_error: Whether to log error details

    Returns:
        Decorated function with error handling

    Example:
        @error_boundary(fallback_value=[], show_error=True)
        def risky_function():
            return 1 / 0  # Would crash

        result = risky_function()  # Returns [], shows error to user
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ZeroDivisionError as e:
                if log_error:
                    logger.error(f"Division by zero in {func.__name__}: {e}")
                if show_error:
                    st.error(
                        f"❌ Calculation error in {func.__name__}: division by zero"
                    )
                return fallback_value
            except KeyError as e:
                if log_error:
                    logger.error(f"Missing key in {func.__name__}: {e}")
                if show_error:
                    st.error(f"❌ Missing required data in {func.__name__}: {e}")
                return fallback_value
            except ValueError as e:
                if log_error:
                    logger.error(f"Invalid value in {func.__name__}: {e}")
                if show_error:
                    st.error(f"❌ Invalid input in {func.__name__}: {e}")
                return fallback_value
            except TypeError as e:
                if log_error:
                    logger.error(f"Type error in {func.__name__}: {e}")
                if show_error:
                    st.error(f"❌ Data type error in {func.__name__}")
                return fallback_value
            except Exception as e:
                if log_error:
                    logger.exception(f"Unexpected error in {func.__name__}")
                if show_error:
                    st.error(
                        f"❌ Unexpected error in {func.__name__}: {type(e).__name__}"
                    )
                    # Don't show full traceback to users for security
                return fallback_value

        return wrapper

    return decorator


def monitor_performance(threshold_seconds: float = 1.0) -> Callable[[F], F]:
    """
    Decorator that monitors function performance and logs slow operations.

    Args:
        threshold_seconds: Time threshold to trigger warning log

    Returns:
        Decorated function with performance monitoring

    Example:
        @monitor_performance(threshold_seconds=2.0)
        def slow_function():
            time.sleep(3)  # Would trigger warning
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time

            start = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start

                if duration > threshold_seconds:
                    logger.warning(
                        f"{func.__name__} took {duration:.2f}s "
                        f"(threshold: {threshold_seconds}s)"
                    )

                return result
            except Exception as e:
                duration = time.time() - start
                logger.error(f"{func.__name__} failed after {duration:.2f}s: {e}")
                raise

        return wrapper

    return decorator


def require_session_state(*keys: str) -> Callable[[F], F]:
    """
    Decorator that validates session state keys exist before running function.

    Args:
        *keys: Session state keys that must exist

    Returns:
        Decorated function with session state validation

    Raises:
        KeyError: If required session state key is missing

    Example:
        @require_session_state("beam_inputs", "design_results")
        def use_results():
            return st.session_state.design_results
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            missing = [key for key in keys if key not in st.session_state]
            if missing:
                error_msg = (
                    f"{func.__name__} requires session state keys: {', '.join(missing)}"
                )
                logger.error(error_msg)
                st.error(f"❌ {error_msg}")
                raise KeyError(error_msg)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_inputs(validator_func: Callable) -> Callable[[F], F]:
    """
    Decorator that validates function inputs using a validator function.

    Args:
        validator_func: Function that validates inputs and returns ValidationResult

    Returns:
        Decorated function with input validation

    Example:
        @validate_inputs(validate_beam_inputs)
        def process_beam(inputs: dict):
            # inputs are guaranteed valid here
            pass
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Assume first positional arg or 'inputs' kwarg is what needs validation
            inputs = args[0] if args else kwargs.get("inputs")

            if inputs is not None:
                result = validator_func(inputs)
                if not result.is_valid:
                    logger.error(
                        f"Validation failed for {func.__name__}: {result.errors}"
                    )
                    for error in result.errors:
                        st.error(f"❌ {error}")
                    raise ValueError(f"Input validation failed: {result.errors}")

            return func(*args, **kwargs)

        return wrapper

    return decorator


class SafeSessionState:
    """
    Type-safe wrapper for session state access.

    Provides .get() with defaults and validation.

    Example:
        safe_state = SafeSessionState()
        inputs = safe_state.get_dict("beam_inputs", default={})
        count = safe_state.get_int("run_count", default=0)
    """

    def __init__(self):
        self.state = st.session_state

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from session state with default."""
        return self.state.get(key, default)

    def get_dict(self, key: str, default: Optional[dict] = None) -> dict:
        """Get dict from session state, ensuring it's actually a dict."""
        value = self.state.get(key, default)
        if value is None:
            return default or {}
        if not isinstance(value, dict):
            logger.warning(
                f"Session state key '{key}' is not a dict (got {type(value).__name__})"
            )
            return default or {}
        return value

    def get_list(self, key: str, default: Optional[list] = None) -> list:
        """Get list from session state, ensuring it's actually a list."""
        value = self.state.get(key, default)
        if value is None:
            return default or []
        if not isinstance(value, list):
            logger.warning(
                f"Session state key '{key}' is not a list (got {type(value).__name__})"
            )
            return default or []
        return value

    def get_int(self, key: str, default: int = 0) -> int:
        """Get int from session state, with type coercion."""
        value = self.state.get(key, default)
        try:
            return int(value)
        except (TypeError, ValueError):
            logger.warning(f"Session state key '{key}' is not an int (got {value})")
            return default

    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get float from session state, with type coercion."""
        value = self.state.get(key, default)
        try:
            return float(value)
        except (TypeError, ValueError):
            logger.warning(f"Session state key '{key}' is not a float (got {value})")
            return default

    def set(self, key: str, value: Any):
        """Set value in session state."""
        self.state[key] = value

    def exists(self, key: str) -> bool:
        """Check if key exists in session state."""
        return key in self.state

    def clear(self, key: str):
        """Remove key from session state if it exists."""
        if key in self.state:
            del self.state[key]
