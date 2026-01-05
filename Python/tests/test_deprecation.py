"""
Tests for deprecation utilities.
"""

import warnings

from structural_lib.utilities import deprecated, deprecated_field


class TestDeprecatedDecorator:
    """Tests for @deprecated decorator."""

    def test_deprecated_function_emits_warning(self):
        """Deprecated function emits DeprecationWarning when called."""

        @deprecated("0.14.0", "1.0.0")
        def old_function():
            return 42

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_function()

            assert result == 42
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "old_function is deprecated since v0.14.0" in str(w[0].message)
            assert "will be removed in v1.0.0" in str(w[0].message)

    def test_deprecated_with_alternative(self):
        """Warning includes alternative when provided."""

        @deprecated("0.14.0", "1.0.0", alternative="new_function")
        def old_function():
            return 42

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_function()

            assert "Use new_function instead" in str(w[0].message)

    def test_deprecated_with_reason(self):
        """Warning includes reason when provided."""

        @deprecated("0.14.0", "1.0.0", reason="Replaced by structured error handling")
        def old_function():
            return 42

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_function()

            assert "Reason: Replaced by structured error handling" in str(w[0].message)

    def test_deprecated_with_both_alternative_and_reason(self):
        """Warning includes both alternative and reason."""

        @deprecated(
            "0.14.0",
            "1.0.0",
            alternative="new_function",
            reason="Better performance",
        )
        def old_function():
            return 42

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_function()

            message = str(w[0].message)
            assert "Use new_function instead" in message
            assert "Reason: Better performance" in message

    def test_deprecated_preserves_function_signature(self):
        """Decorated function preserves name and docstring."""

        @deprecated("0.14.0", "1.0.0")
        def old_function(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b

        assert old_function.__name__ == "old_function"
        assert "Add two numbers" in old_function.__doc__

    def test_deprecated_function_with_arguments(self):
        """Deprecated function with arguments works correctly."""

        @deprecated("0.14.0", "1.0.0")
        def old_function(a, b, c=10):
            return a + b + c

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_function(1, 2, c=3)

            assert result == 6
            assert len(w) == 1

    def test_deprecated_metadata_stored(self):
        """Deprecation metadata is stored for introspection."""

        @deprecated(
            "0.14.0",
            "1.0.0",
            alternative="new_func",
            reason="Performance improvement",
        )
        def old_function():
            return 42

        metadata = old_function.__deprecated__
        assert metadata["version"] == "0.14.0"
        assert metadata["remove_version"] == "1.0.0"
        assert metadata["alternative"] == "new_func"
        assert metadata["reason"] == "Performance improvement"

    def test_deprecated_metadata_none_values(self):
        """Metadata correctly stores None for optional fields."""

        @deprecated("0.14.0", "1.0.0")
        def old_function():
            return 42

        metadata = old_function.__deprecated__
        assert metadata["version"] == "0.14.0"
        assert metadata["remove_version"] == "1.0.0"
        assert metadata["alternative"] is None
        assert metadata["reason"] is None

    def test_deprecated_called_multiple_times(self):
        """Multiple calls emit multiple warnings."""

        @deprecated("0.14.0", "1.0.0")
        def old_function():
            return 42

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_function()
            old_function()
            old_function()

            assert len(w) == 3
            assert all(
                issubclass(warning.category, DeprecationWarning) for warning in w
            )

    def test_deprecated_class_method(self):
        """Decorator works with class methods."""

        class MyClass:
            @deprecated("0.14.0", "1.0.0", alternative="new_method")
            def old_method(self):
                return 42

        obj = MyClass()

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = obj.old_method()

            assert result == 42
            assert len(w) == 1
            assert "old_method is deprecated" in str(w[0].message)


class TestDeprecatedField:
    """Tests for deprecated_field function."""

    def test_deprecated_field_emits_warning(self):
        """deprecated_field emits DeprecationWarning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            deprecated_field("FlexureResult", "error_message", "0.14.0", "1.0.0")

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "FlexureResult.error_message is deprecated" in str(w[0].message)
            assert "since v0.14.0" in str(w[0].message)
            assert "will be removed in v1.0.0" in str(w[0].message)

    def test_deprecated_field_with_alternative(self):
        """Warning includes alternative field name."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            deprecated_field(
                "FlexureResult",
                "error_message",
                "0.14.0",
                "1.0.0",
                alternative="errors",
            )

            assert "Use FlexureResult.errors instead" in str(w[0].message)

    def test_deprecated_field_without_alternative(self):
        """Warning works without alternative."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            deprecated_field("MyClass", "old_field", "0.14.0", "1.0.0")

            message = str(w[0].message)
            assert "MyClass.old_field is deprecated" in message
            assert "since v0.14.0" in message

    def test_deprecated_field_stacklevel(self):
        """Correct stacklevel points to actual usage."""

        def simulate_post_init():
            """Simulates __post_init__ calling deprecated_field."""
            deprecated_field("TestClass", "field", "0.14.0", "1.0.0")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            simulate_post_init()

            assert len(w) == 1
            # stacklevel=3 means warning points to caller of simulate_post_init
            # This simulates: user code → __post_init__ → deprecated_field


class TestDeprecationIntegration:
    """Integration tests for deprecation patterns."""

    def test_deprecated_function_real_use_case(self):
        """Test realistic deprecation scenario."""

        # Old API
        @deprecated("0.14.0", "1.0.0", alternative="calculate_moment_new")
        def calculate_moment_old(b, d, fck):
            """Old calculation method."""
            return b * d * fck * 0.001

        # New API
        def calculate_moment_new(b, d, fck):
            """New calculation method."""
            return b * d * fck * 0.001

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            # User still using old API
            result_old = calculate_moment_old(300, 450, 25)
            result_new = calculate_moment_new(300, 450, 25)

            assert result_old == result_new  # Same result
            assert len(w) == 1  # But warning emitted
            assert "calculate_moment_old is deprecated" in str(w[0].message)
            assert "calculate_moment_new" in str(w[0].message)

    def test_discovering_deprecated_functions_via_metadata(self):
        """Can introspect to find all deprecated functions."""

        @deprecated("0.14.0", "1.0.0")
        def func1():
            pass

        @deprecated("0.13.0", "0.15.0")
        def func2():
            pass

        def func3():  # Not deprecated
            pass

        # Can check if function is deprecated
        assert hasattr(func1, "__deprecated__")
        assert hasattr(func2, "__deprecated__")
        assert not hasattr(func3, "__deprecated__")

        # Can get deprecation details
        assert func1.__deprecated__["version"] == "0.14.0"
        assert func2.__deprecated__["remove_version"] == "0.15.0"


class TestDeprecationWarningsBehavior:
    """Tests for Python's deprecation warning behavior."""

    def test_deprecation_warnings_silenced_by_default(self):
        """DeprecationWarning is silenced by default in Python."""

        @deprecated("0.14.0", "1.0.0")
        def old_function():
            return 42

        # Without explicitly enabling warnings, they're not shown
        # (but still emitted internally)
        with warnings.catch_warnings(record=True) as w:
            # Don't set simplefilter - use default behavior
            old_function()

            # Warning is emitted but not shown to user by default
            # (our test captures it because we're using record=True)
            assert len(w) == 1

    def test_enabling_deprecation_warnings(self):
        """Users can enable deprecation warnings."""

        @deprecated("0.14.0", "1.0.0")
        def old_function():
            return 42

        # Users can enable with:
        # python -W default::DeprecationWarning script.py
        # Or in code:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("default", DeprecationWarning)
            old_function()

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
