#!/usr/bin/env python3
"""
Tests for Enhanced Streamlit Issue Scanner

Ensures the scanner itself works correctly (meta-testing).
Per research: "No test suite FOR the scanner itself" was a gap.

Author: Agent 6 (Continuing Implementation)
Task: Scanner Enhancement (Solution 1 from research)
"""

import ast
import sys
import pytest
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from check_streamlit_issues import EnhancedIssueDetector


def scan_code(code: str) -> list:
    """Helper to scan code and return issues."""
    try:
        tree = ast.parse(code)
        detector = EnhancedIssueDetector("test.py")
        detector.visit(tree)
        return detector.issues
    except SyntaxError as e:
        return [(e.lineno, "ERROR", f"Syntax error: {e.msg}")]


def has_issue_type(issues: list, error_type: str) -> bool:
    """Check if issues contain specific error type."""
    return any(error_type.lower() in issue[2].lower() for issue in issues)


def get_severity_count(issues: list, severity: str) -> int:
    """Count issues of specific severity."""
    return sum(1 for issue in issues if issue[1] == severity)


# =============================================================================
# TypeError Detection Tests
# =============================================================================


class TestTypeErrorDetection:
    """Test TypeError detection (CRITICAL from research)."""

    def test_catches_hash_list(self):
        """Verify scanner catches hash([1,2,3])."""
        code = "key = hash([1, 2, 3])"
        issues = scan_code(code)
        assert has_issue_type(issues, "TypeError")
        assert has_issue_type(issues, "unhashable")
        assert get_severity_count(issues, "CRITICAL") >= 1

    def test_catches_hash_dict(self):
        """Verify scanner catches hash({...})."""
        code = "key = hash({'a': 1})"
        issues = scan_code(code)
        assert has_issue_type(issues, "TypeError")
        assert get_severity_count(issues, "CRITICAL") >= 1

    def test_catches_hash_set(self):
        """Verify scanner catches hash({1, 2, 3})."""
        code = "key = hash({1, 2, 3})"
        issues = scan_code(code)
        assert has_issue_type(issues, "TypeError")

    def test_catches_hash_frozenset_dict_items(self):
        """Verify scanner catches risky frozenset(dict.items()) pattern."""
        code = "key = hash(frozenset(kwargs.items()))"
        issues = scan_code(code)
        assert has_issue_type(issues, "TypeError")
        # Should be HIGH severity (risky but not guaranteed to fail)
        assert get_severity_count(issues, "HIGH") >= 1

    def test_allows_hash_tuple(self):
        """Verify scanner allows hash(tuple(...))."""
        code = "key = hash(tuple([1, 2, 3]))"
        issues = scan_code(code)
        # Should not flag TypeError
        assert not has_issue_type(issues, "TypeError")

    def test_allows_hash_string(self):
        """Verify scanner allows hash('string')."""
        code = "key = hash('my_string')"
        issues = scan_code(code)
        assert not has_issue_type(issues, "TypeError")

    def test_allows_hash_int(self):
        """Verify scanner allows hash(42)."""
        code = "key = hash(42)"
        issues = scan_code(code)
        assert not has_issue_type(issues, "TypeError")


# =============================================================================
# IndexError Detection Tests
# =============================================================================


class TestIndexErrorDetection:
    """Test IndexError detection (NEW from research)."""

    def test_catches_unchecked_list_access(self):
        """Verify scanner catches list[5] without bounds check."""
        code = """
items = [1, 2, 3]
value = items[5]  # No bounds check!
"""
        issues = scan_code(code)
        assert has_issue_type(issues, "IndexError")
        # Should be MEDIUM severity
        assert get_severity_count(issues, "MEDIUM") >= 1

    def test_catches_constant_index(self):
        """Verify scanner flags constant index access."""
        code = """
data = get_data()
first = data[0]  # Could be empty!
"""
        issues = scan_code(code)
        assert has_issue_type(issues, "IndexError")

    def test_allows_checked_list_access(self):
        """Verify scanner allows validated access."""
        code = """
items = [1, 2, 3]
if len(items) > 5:
    value = items[5]
"""
        issues = scan_code(code)
        # Should not flag IndexError for checked access
        # (may still have other issues, but not IndexError)
        index_errors = [i for i in issues if "IndexError" in i[2]]
        assert len(index_errors) == 0

    def test_allows_enumerate(self):
        """Verify scanner allows enumerate access."""
        code = """
for idx, item in enumerate(items):
    print(idx, item)
"""
        issues = scan_code(code)
        # Should not flag any index errors
        assert not has_issue_type(issues, "IndexError")


# =============================================================================
# Phase 9: Fixed-Size Container Detection Tests
# =============================================================================


class TestPhase9FixedSizeContainers:
    """Test Phase 9: structural guarantee detection for fixed-size containers."""

    def test_detects_single_loop_container_size(self):
        """Verify scanner tracks list built with single fixed loop."""
        code = """
items = []
for i in range(5):
    items.append(i * 2)
value = items[4]  # Should be safe - 5 elements guaranteed
"""
        issues = scan_code(code)
        # Should NOT flag IndexError - container has 5 guaranteed elements
        index_errors = [i for i in issues if "IndexError" in i[2]]
        assert len(index_errors) == 0

    def test_detects_nested_loop_container_size(self):
        """Verify scanner multiplies nested loop counts correctly."""
        # Real pattern from multi_format_import.py: 2×2×2 = 8 elements
        code = """
corners = []
for x in [0, 1]:
    for y in [0, 1]:
        for z in [0, 1]:
            corners.append((x, y, z))
# Access all 8 corners
c0 = corners[0]
c7 = corners[7]
"""
        issues = scan_code(code)
        # Should NOT flag IndexError for corners[0] through corners[7]
        index_errors = [i for i in issues if "IndexError" in i[2]]
        assert len(index_errors) == 0

    def test_flags_access_beyond_guaranteed_bounds(self):
        """Verify scanner flags access beyond guaranteed size."""
        code = """
items = []
for i in range(3):
    items.append(i)
value = items[5]  # Only 3 elements - this should fail!
"""
        issues = scan_code(code)
        # Should flag IndexError - only 3 elements, accessing index 5
        assert has_issue_type(issues, "IndexError")

    def test_detects_tuple_iteration_count(self):
        """Verify scanner counts tuple elements correctly."""
        code = """
results = []
for x in (1, 2, 3, 4):
    results.append(x * 2)
value = results[3]  # Safe - 4 elements
"""
        issues = scan_code(code)
        index_errors = [i for i in issues if "IndexError" in i[2]]
        assert len(index_errors) == 0

    def test_flags_unknown_iteration_source(self):
        """Verify scanner still flags when iteration count is unknown."""
        code = """
items = []
for x in get_data():  # Unknown count
    items.append(x)
value = items[0]  # Risky - could be empty!
"""
        issues = scan_code(code)
        # Should still flag - iteration count is unknown
        assert has_issue_type(issues, "IndexError")


# =============================================================================
# ValueError Detection Tests
# =============================================================================


class TestValueErrorDetection:
    """Test ValueError detection (NEW from research)."""

    def test_catches_unchecked_int_conversion(self):
        """Verify scanner catches int() without try/except."""
        code = """
user_input = "abc"
number = int(user_input)  # Will crash on invalid input!
"""
        issues = scan_code(code)
        assert has_issue_type(issues, "ValueError")
        assert get_severity_count(issues, "MEDIUM") >= 1

    def test_catches_unchecked_float_conversion(self):
        """Verify scanner catches float() without try/except."""
        code = """
value = float(user_input)  # No error handling!
"""
        issues = scan_code(code)
        assert has_issue_type(issues, "ValueError")

    def test_allows_checked_int_conversion(self):
        """Verify scanner allows int() with try/except."""
        code = """
try:
    number = int(user_input)
except ValueError:
    number = 0
"""
        issues = scan_code(code)
        # Should not flag ValueError for checked conversion
        value_errors = [i for i in issues if "ValueError" in i[2]]
        assert len(value_errors) == 0


# =============================================================================
# ZeroDivisionError Tests (Existing - Verify Still Works)
# =============================================================================


class TestZeroDivisionErrorDetection:
    """Test ZeroDivisionError detection (existing, verify it works)."""

    def test_catches_unchecked_division(self):
        """Verify scanner catches division without zero check."""
        code = """
spacing = get_spacing()
result = width / spacing  # No zero check!
"""
        issues = scan_code(code)
        assert has_issue_type(issues, "ZeroDivisionError")
        assert get_severity_count(issues, "CRITICAL") >= 1

    def test_allows_constant_division(self):
        """Verify scanner allows division by non-zero constant."""
        code = "result = width / 100"
        issues = scan_code(code)
        # Should not flag division by constant
        assert not has_issue_type(issues, "ZeroDivisionError")

    def test_allows_checked_division(self):
        """Verify scanner allows validated division."""
        code = """
if spacing > 0:
    result = width / spacing
"""
        issues = scan_code(code)
        # Should not flag checked division
        zero_div_errors = [i for i in issues if "ZeroDivisionError" in i[2]]
        assert len(zero_div_errors) == 0

    def test_allows_ternary_division(self):
        """Verify scanner allows ternary with zero check."""
        code = "result = (width / spacing) if spacing > 0 else 0"
        issues = scan_code(code)
        assert not has_issue_type(issues, "ZeroDivisionError")

    def test_allows_path_division(self):
        """Verify scanner allows Path / 'string' division (Phase 4)."""
        code = """
from pathlib import Path
path = Path('/tmp')
result = path / 'subdir'
"""
        issues = scan_code(code)
        # Path division should not be flagged
        assert not has_issue_type(issues, "ZeroDivisionError")

    def test_allows_chained_path_division(self):
        """Verify scanner allows complex Path expressions (Phase 4)."""
        code = """
from pathlib import Path
lib_path = Path(__file__).resolve().parents[2] / 'Python'
"""
        issues = scan_code(code)
        # Complex Path expressions should not be flagged
        assert not has_issue_type(issues, "ZeroDivisionError")

    def test_allows_max_denominator(self):
        """Verify scanner allows division by max(x, positive) (Phase 4)."""
        code = "result = total / max(count, 1)"
        issues = scan_code(code)
        # max(count, 1) guarantees non-zero
        assert not has_issue_type(issues, "ZeroDivisionError")


# =============================================================================
# NameError Tests (Existing - Verify Still Works)
# =============================================================================


class TestNameErrorDetection:
    """Test NameError detection (existing, verify it works)."""

    def test_catches_undefined_variable(self):
        """Verify scanner catches undefined variable."""
        code = "print(undefined_var)"
        issues = scan_code(code)
        assert has_issue_type(issues, "NameError")

    def test_allows_defined_variable(self):
        """Verify scanner allows defined variable."""
        code = """
my_var = 10
print(my_var)
"""
        issues = scan_code(code)
        # Should not flag NameError
        assert not has_issue_type(issues, "NameError")

    def test_allows_imported_names(self):
        """Verify scanner allows imported names."""
        code = """
import streamlit as st
st.title("Test")
"""
        issues = scan_code(code)
        # Should not flag NameError for st
        name_errors = [i for i in issues if "NameError" in i[2] and "'st'" in i[2]]
        assert len(name_errors) == 0


# =============================================================================
# Session State Tests (Existing - Verify Still Works)
# =============================================================================


class TestSessionStateDetection:
    """Test session state validation (existing, verify it works)."""

    def test_catches_unchecked_session_state(self):
        """Verify scanner catches session state without check."""
        code = """
import streamlit as st
value = st.session_state.my_key  # No initialization check!
"""
        issues = scan_code(code)
        assert has_issue_type(issues, "AttributeError")

    def test_allows_checked_session_state(self):
        """Verify scanner allows validated session state."""
        code = """
import streamlit as st
if 'my_key' not in st.session_state:
    st.session_state.my_key = 0
value = st.session_state.my_key
"""
        issues = scan_code(code)
        # Should not flag AttributeError for checked access
        attr_errors = [
            i for i in issues if "AttributeError" in i[2] and "my_key" in i[2]
        ]
        assert len(attr_errors) == 0


# =============================================================================
# Widget Default Detection Tests (TASK-403)
# =============================================================================


class TestWidgetDefaultDetection:
    """Test widget return type validation (TASK-403).

    Detects widgets without explicit default values:
    - st.number_input() without value=
    - st.text_input() without value=
    - st.selectbox() without index=
    """

    def test_catches_number_input_without_value(self):
        """Verify scanner catches st.number_input() without value=."""
        code = """
import streamlit as st
x = st.number_input("Enter value")
"""
        issues = scan_code(code)
        widget_issues = [i for i in issues if "st.number_input()" in i[2]]
        assert len(widget_issues) == 1
        assert "value=" in widget_issues[0][2]

    def test_allows_number_input_with_value(self):
        """Verify scanner allows st.number_input() with value=."""
        code = """
import streamlit as st
x = st.number_input("Enter value", value=10.0)
"""
        issues = scan_code(code)
        widget_issues = [i for i in issues if "st.number_input()" in i[2]]
        assert len(widget_issues) == 0

    def test_allows_number_input_with_positional_value(self):
        """Verify scanner allows st.number_input() with value as positional arg."""
        code = """
import streamlit as st
# label, min_value, max_value, value
x = st.number_input("Enter value", 0, 100, 50)
"""
        issues = scan_code(code)
        widget_issues = [i for i in issues if "st.number_input()" in i[2]]
        assert len(widget_issues) == 0

    def test_catches_text_input_without_value(self):
        """Verify scanner catches st.text_input() without value=."""
        code = """
import streamlit as st
name = st.text_input("Enter name")
"""
        issues = scan_code(code)
        widget_issues = [i for i in issues if "st.text_input()" in i[2]]
        assert len(widget_issues) == 1

    def test_allows_text_input_with_value(self):
        """Verify scanner allows st.text_input() with value=."""
        code = """
import streamlit as st
name = st.text_input("Enter name", value="default")
"""
        issues = scan_code(code)
        widget_issues = [i for i in issues if "st.text_input()" in i[2]]
        assert len(widget_issues) == 0

    def test_catches_selectbox_without_index(self):
        """Verify scanner catches st.selectbox() without index=."""
        code = """
import streamlit as st
choice = st.selectbox("Choose", ["A", "B", "C"])
"""
        issues = scan_code(code)
        widget_issues = [i for i in issues if "st.selectbox()" in i[2]]
        assert len(widget_issues) == 1
        assert "index=" in widget_issues[0][2]

    def test_allows_selectbox_with_index(self):
        """Verify scanner allows st.selectbox() with index=."""
        code = """
import streamlit as st
choice = st.selectbox("Choose", ["A", "B", "C"], index=0)
"""
        issues = scan_code(code)
        widget_issues = [i for i in issues if "st.selectbox()" in i[2]]
        assert len(widget_issues) == 0

    def test_catches_slider_without_value(self):
        """Verify scanner catches st.slider() without value=."""
        code = """
import streamlit as st
val = st.slider("Adjust")
"""
        issues = scan_code(code)
        widget_issues = [i for i in issues if "st.slider()" in i[2]]
        assert len(widget_issues) == 1

    def test_allows_slider_with_value(self):
        """Verify scanner allows st.slider() with value=."""
        code = """
import streamlit as st
val = st.slider("Adjust", min_value=0, max_value=100, value=50)
"""
        issues = scan_code(code)
        widget_issues = [i for i in issues if "st.slider()" in i[2]]
        assert len(widget_issues) == 0


# =============================================================================
# Integration Tests
# =============================================================================


class TestScannerIntegration:
    """Test scanner on realistic code."""

    def test_catches_multiple_issues(self):
        """Verify scanner catches multiple issue types."""
        code = """
import streamlit as st

# NameError
print(undefined_var)

# ZeroDivisionError
result = 100 / spacing

# IndexError
items = [1, 2, 3]
value = items[10]

# TypeError
key = hash([1, 2, 3])

# ValueError
number = int(user_input)
"""
        issues = scan_code(code)

        # Should catch all 5 types
        assert has_issue_type(issues, "NameError")
        assert has_issue_type(issues, "ZeroDivisionError")
        assert has_issue_type(issues, "IndexError")
        assert has_issue_type(issues, "TypeError")
        assert has_issue_type(issues, "ValueError")

        # Should have multiple critical issues
        assert get_severity_count(issues, "CRITICAL") >= 2

    def test_clean_code_no_issues(self):
        """Verify scanner doesn't flag clean code."""
        code = """
import streamlit as st

def safe_divide(a, b):
    return a / b if b != 0 else 0

def process_items(items):
    if len(items) > 0:
        first = items[0]
        return first
    return None

st.title("Clean Page")
"""
        issues = scan_code(code)

        # Should have no critical issues
        assert get_severity_count(issues, "CRITICAL") == 0


# =============================================================================
# Performance Tests
# =============================================================================


class TestScannerPerformance:
    """Test scanner performance."""

    def test_scans_large_file_quickly(self):
        """Verify scanner handles large files."""
        import time

        # Generate large code file (500 functions)
        code = (
            """
import streamlit as st

def safe_divide(a, b):
    return a / b if b != 0 else 0

"""
            * 500
        )

        start = time.time()
        issues = scan_code(code)
        elapsed = time.time() - start

        # Should complete in under 1 second
        assert elapsed < 1.0
        print(f"Scanned 500 functions in {elapsed:.3f}s")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
