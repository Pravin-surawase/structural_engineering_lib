"""
Tests for error sanitization utilities (TASK-796).

Validates that sanitize_error() and sanitize_error_string() strip
file paths, backslash paths, and tracebacks from API error messages
(CWE-209 prevention).
"""

from fastapi_app.error_utils import sanitize_error, sanitize_error_string

# =============================================================================
# sanitize_error_string — pure string sanitization
# =============================================================================


class TestSanitizeErrorString:
    """Tests for sanitize_error_string()."""

    def test_normal_message_passes_through(self):
        msg = "Invalid beam width: must be positive"
        assert sanitize_error_string(msg, "beam design") == msg

    def test_strips_unix_file_path(self):
        msg = "Error in /Users/foo/bar.py line 42: division by zero"
        result = sanitize_error_string(msg, "beam design")
        assert "/Users" not in result
        assert "bar.py" not in result
        assert "Reference:" in result

    def test_strips_backslash_path(self):
        msg = r"Failed at C:\Users\dev\project\module.py"
        result = sanitize_error_string(msg, "column design")
        assert "C:" not in result
        assert "module.py" not in result
        assert "Reference:" in result

    def test_strips_traceback_keyword(self):
        msg = "Traceback (most recent call last): some error"
        result = sanitize_error_string(msg, "shear check")
        assert "Traceback" not in result
        assert "Reference:" in result

    def test_context_appears_in_sanitized_output(self):
        msg = "/some/internal/path.py failed"
        result = sanitize_error_string(msg, "anchorage check")
        assert "anchorage check" in result

    def test_empty_string_passes_through(self):
        assert sanitize_error_string("", "test") == ""

    def test_message_with_only_slashes_in_units_stripped(self):
        """A message containing '/' (e.g. N/mm²) gets stripped since '/' triggers the guard."""
        msg = "Stress exceeds 0.45 N/mm² limit"
        result = sanitize_error_string(msg, "design")
        # The '/' in 'N/mm²' triggers sanitization — this is the safe-by-default behavior
        assert "Reference:" in result

    def test_reference_id_format(self):
        """Sanitized messages include an 8-char hex reference ID."""
        msg = "/some/path error"
        result = sanitize_error_string(msg, "test")
        # Format: "Error during test. Reference: <8hex>"
        parts = result.split("Reference: ")
        assert len(parts) == 2
        ref_id = parts[1]
        assert len(ref_id) == 8
        assert all(c in "0123456789abcdef" for c in ref_id)


# =============================================================================
# sanitize_error — exception-based sanitization
# =============================================================================


class TestSanitizeError:
    """Tests for sanitize_error()."""

    def test_value_error_safe_message_preserved(self):
        e = ValueError("Width must be positive")
        result = sanitize_error(e, "beam design")
        assert result == "Width must be positive"

    def test_value_error_with_path_stripped(self):
        e = ValueError("Error in /usr/local/lib/python3.12/module.py")
        result = sanitize_error(e, "design")
        assert "/usr" not in result
        assert "Reference:" in result

    def test_type_error_safe_message_preserved(self):
        e = TypeError("Expected float, got str")
        result = sanitize_error(e, "validation")
        assert result == "Expected float, got str"

    def test_generic_exception_returns_internal_error(self):
        e = RuntimeError("Unexpected internal state")
        result = sanitize_error(e, "column design")
        assert "Internal error" in result
        assert "column design" in result
        assert "Reference:" in result

    def test_generic_exception_hides_original_message(self):
        e = RuntimeError("segfault at 0xdeadbeef in /opt/lib/core.so")
        result = sanitize_error(e, "operation")
        assert "segfault" not in result
        assert "0xdeadbeef" not in result

    def test_value_error_with_backslash_stripped(self):
        e = ValueError(r"File C:\temp\data.csv not found")
        result = sanitize_error(e, "import")
        assert "C:" not in result
        assert "Reference:" in result

    def test_value_error_with_traceback_stripped(self):
        e = ValueError("Traceback (most recent call last): ...")
        result = sanitize_error(e, "check")
        assert "Traceback" not in result
        assert "Reference:" in result
