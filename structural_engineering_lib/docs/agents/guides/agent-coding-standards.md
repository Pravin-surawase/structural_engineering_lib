# AI Agent Coding Standards Guide

**Type:** Guide
**Audience:** All AI Agents
**Status:** Approved
**Importance:** Critical
**Version:** 1.0.0
**Created:** 2026-01-11
**Last Updated:** 2026-01-11
**Related Tasks:** TASK-421
**Archive Condition:** Never - this is a living document, update rather than archive

---

## Overview

This guide establishes coding standards for AI agents working on this project. Following these rules prevents 90%+ of runtime errors and CI failures.

**Remember:** Write code that the scanner will pass. If the scanner flags something, fix it - even if you think it's a false positive.

---

## 1. Streamlit-Specific Rules (CRITICAL)

### 1.1 Dictionary Access

❌ **NEVER do this:**
```python
value = data['key']  # KeyError if key missing
text = result['text']  # KeyError risk
```

✅ **ALWAYS do this:**
```python
value = data.get('key', default_value)
text = result.get('text', '')
```

### 1.2 List/Array Access

❌ **NEVER do this:**
```python
first = items[0]  # IndexError if empty
parts = x.split('.')[0]  # Scanner flags this
```

✅ **ALWAYS do this:**
```python
first = items[0] if len(items) > 0 else None
parts = x.split('.')
first_part = parts[0] if len(parts) > 0 else x
```

### 1.3 Division Operations

❌ **NEVER do this:**
```python
result = a / b  # ZeroDivisionError if b=0
ratio = numerator / denominator
```

✅ **ALWAYS do this:**
```python
result = a / b if b != 0 else 0
ratio = numerator / denominator if denominator > 0 else 0.0
```

### 1.4 Session State

❌ **NEVER do this:**
```python
value = st.session_state.my_key  # AttributeError
value = st.session_state['my_key']  # KeyError
```

✅ **ALWAYS do this:**
```python
# Option 1: Use .get()
value = st.session_state.get('my_key', default)

# Option 2: Check first
if 'my_key' not in st.session_state:
    st.session_state['my_key'] = default
value = st.session_state['my_key']

# Option 3: Initialize at module level
def init_session_state():
    defaults = {'my_key': 'default', 'counter': 0}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
```

### 1.5 Imports

❌ **NEVER do this:**
```python
def my_function():
    import pandas as pd  # Import inside function
    from utils import helper  # Import inside function
```

✅ **ALWAYS do this:**
```python
import pandas as pd  # At module level
from utils import helper  # At module level

def my_function():
    # Use imported modules
    df = pd.DataFrame(data)
```

### 1.6 Type Annotations

❌ **Avoid:**
```python
def process(data):  # No type hints
    return result
```

✅ **Preferred:**
```python
def process(data: dict[str, Any]) -> list[str]:
    """Process data and return list of strings."""
    return result
```

---

## 2. Python Best Practices

### 2.1 Error Handling

❌ **NEVER do this:**
```python
try:
    result = risky_operation()
except:  # Bare except
    pass  # Silent failure
```

✅ **ALWAYS do this:**
```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    st.error(f"Error: {e}")
    result = fallback_value
```

### 2.2 Logging

❌ **NEVER do this:**
```python
print(f"Debug: {value}")  # No print statements
```

✅ **ALWAYS do this:**
```python
import logging
logger = logging.getLogger(__name__)

logger.debug(f"Processing: {value}")
logger.info(f"Completed: {result}")
logger.error(f"Failed: {error}")
```

### 2.3 Docstrings

Every public function must have a docstring:

```python
def calculate_reinforcement(
    moment: float,
    width: float,
    depth: float,
    fck: float = 25.0,
    fy: float = 500.0,
) -> dict[str, float]:
    """Calculate required steel reinforcement for given moment.

    Args:
        moment: Design bending moment in kN·m.
        width: Beam width in mm.
        depth: Effective depth in mm.
        fck: Concrete grade in N/mm².
        fy: Steel grade in N/mm².

    Returns:
        Dictionary with 'ast_required', 'ast_min', 'ast_max' in mm².

    Raises:
        ValueError: If moment is negative or dimensions are invalid.

    Example:
        >>> result = calculate_reinforcement(100, 300, 450)
        >>> print(f"Required: {result['ast_required']:.0f} mm²")
    """
```

### 2.4 Constants

❌ **NEVER do this:**
```python
if value > 25:  # Magic number
    factor = 0.85  # What is this?
```

✅ **ALWAYS do this:**
```python
MIN_CONCRETE_GRADE = 25  # N/mm²
STRESS_BLOCK_FACTOR = 0.85  # IS 456 Cl. 38.1

if value > MIN_CONCRETE_GRADE:
    factor = STRESS_BLOCK_FACTOR
```

---

## 3. Scanner Awareness

### 3.1 What the Scanner Checks

| Issue | Detection | Action |
|-------|-----------|--------|
| Undefined variable | ✅ CRITICAL | Fix immediately |
| Division by zero | ✅ CRITICAL | Add zero check |
| KeyError risk | ✅ HIGH | Use .get() |
| IndexError risk | ✅ MEDIUM | Add bounds check |
| Import inside function | ✅ HIGH | Move to module level |
| Session state access | ✅ HIGH | Use .get() or 'in' check |

### 3.2 Patterns Scanner Recognizes as Safe

```python
# Zero-check patterns (all recognized)
x / y if y != 0 else 0
x / y if y > 0 else 0
if y > 0: result = x / y

# Bounds check patterns
items[0] if len(items) > 0 else None
items[0] if items else default

# Session state patterns
if 'key' in st.session_state:
    value = st.session_state['key']
```

### 3.3 Known Scanner Limitations

The scanner may flag these (false positives):
- `x.split('.')[0]` - split always returns at least one element
- Variables defined in one branch of if/else

**When you see a false positive:** Still fix it for consistency, or add a comment:
```python
# Scanner note: split() always returns at least 1 element
parts = x.split('.')
first = parts[0] if len(parts) > 0 else x  # Explicit check for scanner
```

---

## 4. Testing Requirements

### 4.1 Test Coverage

- **New business logic:** 100% coverage required
- **New utility functions:** 90% coverage required
- **New Streamlit pages:** Integration test required

### 4.2 Test Structure

```python
class TestFeature:
    """Tests for feature X."""

    def test_happy_path(self):
        """Test normal operation."""
        result = function(valid_input)
        assert result == expected

    def test_edge_case_empty(self):
        """Test with empty input."""
        result = function([])
        assert result == default

    def test_edge_case_max(self):
        """Test with maximum values."""
        result = function(MAX_VALUE)
        assert result <= MAX_ALLOWED

    def test_error_handling(self):
        """Test error cases."""
        with pytest.raises(ValueError):
            function(invalid_input)
```

### 4.3 Test File Naming

```
tests/
├── test_<module>.py           # Unit tests
├── test_<module>_integration.py  # Integration tests
└── conftest.py                # Shared fixtures
```

---

## 5. Code Review Checklist

Before committing, verify:

### Safety Checks
- [ ] No bare `dict['key']` access (use `.get()`)
- [ ] No bare `list[index]` access (check bounds)
- [ ] No unprotected division
- [ ] Session state properly initialized
- [ ] All imports at module level

### Quality Checks
- [ ] Type hints on function signatures
- [ ] Docstrings on public functions
- [ ] No magic numbers (use constants)
- [ ] Logging instead of print()
- [ ] Specific exception handling

### Testing Checks
- [ ] Tests added/updated for new code
- [ ] All tests passing locally
- [ ] Scanner shows no CRITICAL issues

---

## 6. Quick Reference

### Safe Patterns Cheat Sheet

```python
# Dictionary access
value = data.get('key', default)

# List access
first = items[0] if len(items) > 0 else None

# Division
result = a / b if b != 0 else 0

# Session state
value = st.session_state.get('key', default)

# Error handling
try:
    result = risky_op()
except SpecificError as e:
    logger.error(f"Error: {e}")
    result = fallback
```

### Import Template

```python
"""Module description."""
from __future__ import annotations

import logging
from typing import Any

import streamlit as st
import pandas as pd

from structural_lib import api
from utils.layout import setup_page

logger = logging.getLogger(__name__)
```

---

## 7. Common Mistakes by Agent Role

### Implementation Agent
- Forgetting error handling on API calls
- Not initializing session state
- Using bare dictionary access

### Testing Agent
- Not testing edge cases
- Missing error path tests
- Incomplete mock setup

### Documentation Agent
- Outdated code examples
- Missing parameter descriptions
- Wrong return type documentation

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-11 | Initial guide created |

---

*This guide is automatically loaded by agents. Updates should be coordinated with copilot-instructions.md.*
