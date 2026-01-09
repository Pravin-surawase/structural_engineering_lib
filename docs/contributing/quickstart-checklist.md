# Quick-Start Checklist (Solution 4 - Developer Guides)

Quick reference for common development tasks with step-by-step checklists.

**Author:** Agent 6 (Quality Improvement - Solution 4)
**Date:** 2026-01-09

---

## 📋 Adding a New Streamlit Page (15 min)

### Checklist
- [ ] **1. Create page file:** `streamlit_app/pages/NN_📋_page_name.py`
  - Use two-digit number (e.g., 07, 08)
  - Include emoji in filename
  - Use snake_case for page_name

- [ ] **2. Add page header:**
  ```python
  import streamlit as st

  st.set_page_config(
      page_title="Page Name",
      page_icon="📋",
      layout="wide"
  )
  ```

- [ ] **3. Initialize session state:**
  ```python
  if 'page_name_state' not in st.session_state:
      st.session_state.page_name_state = {
          'initialized': True,
          # Add your state here
      }
  ```

- [ ] **4. Create test scaffold:**
  ```bash
  python scripts/create_test_scaffold.py PageName \
    streamlit_app.pages.page_name streamlit_page
  ```

- [ ] **5. Implement page logic** (see template below)

- [ ] **6. Add to navigation:** Update `streamlit_app/README.md` with page description

- [ ] **7. Run scanner:**
  ```bash
  python scripts/check_streamlit_issues.py --page page_name
  ```

- [ ] **8. Write tests** (minimum 5 tests):
  - Page loads without errors
  - Session state initialization
  - Input validation
  - Computation logic
  - Error handling

- [ ] **9. Run page tests:**
  ```bash
  ./scripts/test_page.sh page_name
  ```

- [ ] **10. Commit:**
  ```bash
  ./scripts/ai_commit.sh "feat(streamlit): Add PageName page"
  ```

### Page Template
```python
"""
Page Name - Brief Description

This page provides [functionality description].

Author: [Your Name]
Date: [Date]
"""

import streamlit as st
from streamlit_app.utils.layout import create_two_column_layout
from streamlit_app.utils.error_handler import safe_compute

# Page config
st.set_page_config(page_title="Page Name", page_icon="📋", layout="wide")

# Initialize session state
if 'page_name_state' not in st.session_state:
    st.session_state.page_name_state = {
        'initialized': True,
        'last_result': None
    }

# Page header
st.title("📋 Page Name")
st.markdown("""
Brief description of what this page does.
""")

# Two-column layout
col1, col2 = create_two_column_layout()

with col1:
    st.subheader("📥 Input Parameters")

    # Input controls
    param1 = st.number_input(
        "Parameter 1 (mm)",
        min_value=0,
        max_value=10000,
        value=300,
        step=10,
        help="Description of parameter"
    )

    param2 = st.selectbox(
        "Parameter 2",
        options=["Option1", "Option2", "Option3"],
        help="Description of parameter"
    )

    # Compute button
    if st.button("🔄 Compute", type="primary"):
        with st.spinner("Computing..."):
            result = safe_compute(
                compute_function,
                param1=param1,
                param2=param2
            )

            if result.success:
                st.session_state.page_name_state['last_result'] = result.data
                st.success("✅ Computation successful!")
            else:
                st.error(f"❌ Error: {result.error}")

with col2:
    st.subheader("📊 Results")

    if st.session_state.page_name_state['last_result']:
        result = st.session_state.page_name_state['last_result']

        # Display results
        st.metric("Result 1", f"{result['value1']:.2f}")
        st.metric("Result 2", f"{result['value2']:.2f}")

        # Download button
        st.download_button(
            label="📥 Download Results",
            data=format_results(result),
            file_name="results.csv",
            mime="text/csv"
        )
    else:
        st.info("ℹ️ Enter parameters and click Compute")
```

---

## 🧪 Writing Tests (10 min)

### Test Structure Template
```python
"""
Tests for [Feature Name]

Coverage:
- [ ] Happy path
- [ ] Edge cases
- [ ] Error handling
- [ ] Integration
"""

import pytest

class TestFeatureInit:
    """Test initialization."""

    def test_default_initialization(self):
        obj = Feature()
        assert obj is not None

class TestFeatureCore:
    """Test core functionality."""

    @pytest.fixture
    def instance(self):
        return Feature()

    def test_main_operation(self, instance):
        result = instance.operate(valid_input)
        assert result == expected_output

class TestFeatureEdgeCases:
    """Test edge cases."""

    def test_empty_input(self):
        result = Feature().operate([])
        assert result is not None

    def test_large_input(self):
        large_input = [1] * 10000
        result = Feature().operate(large_input)
        assert len(result) == 10000

class TestFeatureErrors:
    """Test error handling."""

    def test_invalid_input_raises_error(self):
        with pytest.raises(ValueError):
            Feature().operate(invalid_input)
```

### Test Checklist
- [ ] At least one test per method
- [ ] Test happy path (normal usage)
- [ ] Test edge cases (empty, None, large values)
- [ ] Test error conditions
- [ ] Use fixtures for setup
- [ ] Add docstrings to tests
- [ ] Run tests locally before committing

---

## 🔧 Adding a Utility Class (20 min)

### Checklist
- [ ] **1. Create module file:** `streamlit_app/utils/utility_name.py`

- [ ] **2. Add class with docstring:**
  ```python
  """Utility Name - Brief Description.

  This utility provides [functionality].

  Example:
      >>> util = UtilityName()
      >>> result = util.method(input)

  Author: [Your Name]
  Date: [Date]
  """

  class UtilityName:
      """Brief description.

      Attributes:
          attr1: Description
          attr2: Description
      """

      def __init__(self, param1: type = default):
          """Initialize utility.

          Args:
              param1: Description
          """
          self.param1 = param1

      def method(self, input: type) -> type:
          """Brief description.

          Args:
              input: Description

          Returns:
              Description

          Raises:
              ValueError: If input is invalid
          """
          if not self._validate(input):
              raise ValueError("Invalid input")
          return self._process(input)
  ```

- [ ] **3. Create test scaffold:**
  ```bash
  python scripts/create_test_scaffold.py UtilityName \
    streamlit_app.utils.utility_name
  ```

- [ ] **4. Write tests** (minimum 8 tests):
  - Initialization tests (2+)
  - Core functionality tests (3+)
  - Edge case tests (2+)
  - Error handling tests (1+)

- [ ] **5. Run tests:**
  ```bash
  pytest tests/test_utilityname.py -v
  ```

- [ ] **6. Add to utils/__init__.py** (if needed)

- [ ] **7. Run scanner:**
  ```bash
  python scripts/check_streamlit_issues.py --file streamlit_app/utils/utility_name.py
  ```

- [ ] **8. Commit:**
  ```bash
  ./scripts/ai_commit.sh "feat(utils): Add UtilityName utility"
  ```

---

## 🚀 Pre-Commit Workflow (5 min)

### Quick Check
```bash
# Run all validations
./scripts/quick_check.sh

# If passes, commit
./scripts/ai_commit.sh "commit message"
```

### Manual Workflow (if quick_check unavailable)
```bash
# 1. Scanner
python scripts/check_streamlit_issues.py --all-pages --fail-on-critical

# 2. Type check
mypy changed_files.py --ignore-missing-imports

# 3. Tests
pytest tests/ -v

# 4. Commit
./scripts/ai_commit.sh "commit message"
```

---

## 📖 Common Patterns

### Pattern 1: Safe Division
```python
# ❌ DON'T
result = width / spacing

# ✅ DO
result = width / spacing if spacing > 0 else 0

# ✅ ALSO GOOD (with error)
if spacing <= 0:
    raise ValueError("Spacing must be positive")
result = width / spacing
```

### Pattern 2: Session State Initialization
```python
# ❌ DON'T
value = st.session_state.my_key

# ✅ DO
if 'my_key' not in st.session_state:
    st.session_state.my_key = default_value
value = st.session_state.my_key

# ✅ ALSO GOOD (one-liner)
value = st.session_state.get('my_key', default_value)
```

### Pattern 3: Input Validation
```python
# ❌ DON'T
result = int(user_input)

# ✅ DO
try:
    result = int(user_input)
except ValueError:
    st.error("Invalid input: must be an integer")
    result = None

# ✅ ALSO GOOD (with validation function)
def validate_int(value, min_val=None, max_val=None):
    try:
        num = int(value)
        if min_val is not None and num < min_val:
            raise ValueError(f"Must be >= {min_val}")
        if max_val is not None and num > max_val:
            raise ValueError(f"Must be <= {max_val}")
        return num
    except ValueError as e:
        raise ValueError(f"Invalid integer: {e}")
```

### Pattern 4: Library Function Call
```python
# ❌ DON'T (implicit units)
result = library_function(b, d)

# ✅ DO (explicit units)
from structural_lib.api import design_beam
result = design_beam(
    width_mm=b,
    depth_mm=d,
    concrete_grade="M25",
    steel_grade="Fe500"
)
```

### Pattern 5: Error Handling with User Feedback
```python
# ❌ DON'T (silent failure)
try:
    result = compute(data)
except Exception:
    result = None

# ✅ DO (informative errors)
try:
    result = compute(data)
except ValueError as e:
    st.error(f"❌ Invalid input: {e}")
    result = None
except Exception as e:
    st.error(f"❌ Unexpected error: {e}")
    st.info("ℹ️ Please check your inputs and try again")
    result = None
```

---

## 🎯 Quality Standards

### Code Quality
- ✅ Type hints on all functions
- ✅ Docstrings on classes and public methods
- ✅ Error handling with informative messages
- ✅ Input validation
- ✅ No magic numbers (use constants)
- ✅ DRY principle (Don't Repeat Yourself)

### Test Quality
- ✅ At least 80% code coverage
- ✅ Tests for happy path, edge cases, errors
- ✅ Descriptive test names
- ✅ Use fixtures for setup
- ✅ Fast tests (<1s per test)
- ✅ Independent tests (no inter-test dependencies)

### Documentation Quality
- ✅ Module-level docstring with example
- ✅ Class docstrings with attributes
- ✅ Method docstrings with Args/Returns/Raises
- ✅ Inline comments for complex logic
- ✅ README updates for new features
- ✅ Changelog entries

---

## 📚 Reference Links

- **Architecture:** `docs/architecture/streamlit-app-architecture.md`
- **UI Patterns:** `docs/planning/ui-layout-decision.md`
- **Testing Guide:** `docs/contributing/development-guide.md`
- **Git Workflow:** `docs/contributing/git-workflow-for-ai-agents.md`
- **Scanner Usage:** `scripts/check_streamlit_issues.py --help`
- **Agent 6 Tasks:** `docs/planning/agent-6-tasks-streamlit.md`

---

## ⚡ Quick Commands

```bash
# Development
./scripts/watch_tests.sh                    # Auto-run tests on changes
./scripts/quick_check.sh                    # Fast validation
./scripts/test_page.sh page_name            # Test specific page

# Test Generation
python scripts/create_test_scaffold.py ClassName module.path

# Validation
python scripts/check_streamlit_issues.py --all-pages
pytest tests/ -v
mypy file.py --ignore-missing-imports

# Commit
./scripts/ai_commit.sh "commit message"
```

---

**Last Updated:** 2026-01-09
**Version:** 1.0
**Maintainer:** Agent 6
