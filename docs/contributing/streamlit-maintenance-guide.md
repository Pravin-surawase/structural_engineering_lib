# Streamlit Maintenance Guide
**Version:** 0.16.6
**Last Updated:** 2026-01-09
**For:** Project Maintainers & Future AI Agents

> **Purpose:** Your complete reference for developing, testing, validating, and maintaining the Streamlit UI.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Development Workflow](#development-workflow)
3. [Quality Validation](#quality-validation)
4. [Testing Strategy](#testing-strategy)
5. [Common Patterns](#common-patterns)
6. [Troubleshooting](#troubleshooting)
7. [CI/CD Integration](#cicd-integration)
8. [Best Practices](#best-practices)

---

## 🚀 Quick Start

### Running the Streamlit App

```bash
# Navigate to project root
cd "/path/to/structural_engineering_lib"

# Activate virtual environment
source .venv/bin/activate

# Run the app
cd streamlit_app
streamlit run app.py

# Access at: http://localhost:8501
```

### File Structure

```
streamlit_app/
├── app.py                    # Main entry point
├── pages/                    # Multi-page app pages
│   ├── 01_🏗️_beam_design.py
│   ├── 02_💰_cost_optimizer.py
│   ├── 03_✅_compliance.py
│   ├── 04_📚_documentation.py
│   ├── 05_📋_bbs_generator.py    # FEAT-001 (Agent 6)
│   ├── 06_📐_dxf_export.py       # FEAT-002 (Agent 6)
│   ├── 07_📄_report_generator.py # FEAT-003 (Agent 6)
│   ├── 08_📊_batch_design.py     # FEAT-004 (Agent 6)
│   ├── 09_🔬_advanced_analysis.py # FEAT-005 (Agent 6)
│   ├── 10_📚_learning_center.py  # FEAT-006 (Agent 6)
│   └── 11_🎬_demo_showcase.py    # FEAT-007 (Agent 6)
├── components/               # Reusable UI components
├── utils/                    # Helper utilities
└── tests/                    # Test files
```

---

## 🔄 Development Workflow

### Step 1: Create New Feature

```bash
# Create new page file
touch streamlit_app/pages/12_🎨_new_feature.py

# Use template structure
cat > streamlit_app/pages/12_🎨_new_feature.py << 'EOF'
"""
New Feature Page
================

Brief description of what this page does.

Features:
- Feature 1
- Feature 2

Author: [Your Name/Agent]
Status: 🚧 IN PROGRESS
"""

import streamlit as st
from pathlib import Path
import sys

# Add Python library to path
current_file = Path(__file__).resolve()
streamlit_app_dir = current_file.parent.parent
python_lib_dir = streamlit_app_dir.parent / "Python"
if str(python_lib_dir) not in sys.path:
    sys.path.insert(0, str(python_lib_dir))

# Streamlit imports
from utils.layout import setup_page, page_header
from utils.theme_manager import initialize_theme

# Initialize
initialize_theme()
setup_page(
    title="New Feature",
    icon="🎨",
    layout="wide"
)

# Main content
def main():
    page_header("New Feature", "Description goes here")

    # Your feature code here
    st.write("Coming soon!")

if __name__ == "__main__":
    main()
EOF
```

### Step 2: Run Local Validation

```bash
# ALWAYS run these before committing

# 1. AST Scanner (detects runtime errors)
.venv/bin/python scripts/check_streamlit_issues.py --page "12_🎨_new_feature"

# 2. Pylint (code quality)
.venv/bin/python -m pylint --rcfile=.pylintrc-streamlit streamlit_app/pages/12_🎨_new_feature.py

# 3. Black formatting
.venv/bin/python -m black streamlit_app/pages/12_🎨_new_feature.py

# 4. Ruff linting
.venv/bin/python -m ruff check streamlit_app/pages/12_🎨_new_feature.py --fix
```

### Step 3: Test Manually

```bash
# Run Streamlit and test in browser
streamlit run streamlit_app/app.py

# Check:
# ✓ Page loads without errors
# ✓ All inputs work
# ✓ Results display correctly
# ✓ Session state persists across reruns
# ✓ Error messages are user-friendly
```

### Step 4: Write Tests

```bash
# Create test file
touch streamlit_app/tests/test_new_feature.py

# Use test template (see Testing Strategy section)
```

### Step 5: Commit

```bash
# Use automation for safe commits
./scripts/ai_commit.sh "feat(streamlit): add new feature page"

# OR create PR for substantial features
./scripts/create_task_pr.sh FEAT-XXX "New Feature Implementation"
# ... make changes ...
./scripts/finish_task_pr.sh FEAT-XXX "New Feature Implementation"
```

---

## ✅ Quality Validation

### AST Scanner (Most Important!)

**What it checks:**
- ✅ NameError (undefined variables)
- ✅ ZeroDivisionError (unprotected divisions)
- ✅ AttributeError (missing session state keys)
- ✅ KeyError (direct dict access)
- ✅ ImportError (missing imports)
- ✅ TypeError, IndexError, ValueError

**How to use:**

```bash
# Scan single page
.venv/bin/python scripts/check_streamlit_issues.py --page "01_🏗️_beam_design"

# Scan all pages
.venv/bin/python scripts/check_streamlit_issues.py --all-pages

# Fail on CRITICAL issues only (CI mode)
.venv/bin/python scripts/check_streamlit_issues.py --all-pages --fail-on-critical

# Verbose mode (shows all details)
.venv/bin/python scripts/check_streamlit_issues.py --all-pages --verbose
```

**Issue Severity:**

| Severity | Examples | Action |
|----------|----------|--------|
| 🔴 **CRITICAL** | NameError, ZeroDivisionError | **MUST FIX** before merge |
| 🟠 **HIGH** | KeyError, AttributeError | **SHOULD FIX** (safety) |
| 🟡 **MEDIUM** | ValueError on int() | **CAN DEFER** (Streamlit validates) |

**Known False Positives:**

1. **Loop variables:**
   ```python
   for name, scenario in DEMO_SCENARIOS.items():  # ✓ Valid
       st.markdown(f"{scenario['icon']} {name}")  # Scanner may flag 'name'
   ```

2. **\*\*kwargs:**
   ```python
   def my_function(**kwargs):  # ✓ Valid
       cache_key = f"viz_{hash(kwargs)}"  # Scanner may flag 'kwargs'
   ```

3. **Path operations:**
   ```python
   python_lib_dir = parent / "Python"  # ✓ Valid Path operation
   # Scanner may flag as division
   ```

**Solution for false positives:** See Scanner Phase 2 tasks below.

### Pylint Checks

```bash
# Run pylint with Streamlit-specific config
.venv/bin/python -m pylint --rcfile=.pylintrc-streamlit streamlit_app/

# Config file: .pylintrc-streamlit
# - Disables: C0301 (line-too-long), C0103 (invalid-name)
# - Enables: undefined-variable, import-error, used-before-assignment
```

### Test Suite

```bash
# Run all Streamlit tests
pytest streamlit_app/tests/ -v

# Run specific test file
pytest streamlit_app/tests/test_beam_design.py -v

# Current status: 829/939 passing (88.3%)
# Target: >890/939 (95%+) after FIX-002 Phase 2
```

---

## 🧪 Testing Strategy

### Test Template

```python
"""Tests for New Feature page"""

import pytest
import streamlit as st
from unittest.mock import Mock, patch, MagicMock

# Import page module
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pages import new_feature_page  # Adjust import

class TestNewFeature:
    """Test suite for new feature page"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset session state before each test"""
        if hasattr(st, 'session_state'):
            st.session_state.clear()

    def test_page_loads(self):
        """Page loads without errors"""
        with patch('streamlit.write'):
            new_feature_page.main()  # Should not raise

    def test_input_validation(self):
        """Input validation works correctly"""
        # Test valid input
        result = new_feature_page.validate_input(valid_data)
        assert result is True

        # Test invalid input
        with pytest.raises(ValueError):
            new_feature_page.validate_input(invalid_data)

    def test_session_state(self):
        """Session state persists correctly"""
        st.session_state.test_key = "test_value"
        assert st.session_state.test_key == "test_value"

    def test_api_integration(self):
        """API calls work correctly"""
        with patch('structural_lib.api.design_beam') as mock_api:
            mock_api.return_value = {'status': 'success'}
            result = new_feature_page.call_api(test_data)
            assert result['status'] == 'success'
```

### Test Categories

1. **Unit Tests:** Test individual functions
2. **Integration Tests:** Test page + API integration
3. **UI Tests:** Test Streamlit components (limited)

### Current Test Issues (FIX-002)

**Problem:** Test state pollution (99 failures)
**Cause:** Session state not reset between tests
**Solution (Phase 2):**

```python
# Add to conftest.py
@pytest.fixture(autouse=True)
def reset_streamlit_state():
    """Auto-reset session state before each test"""
    if hasattr(st, 'session_state'):
        st.session_state.clear()
    yield
    if hasattr(st, 'session_state'):
        st.session_state.clear()
```

---

## 🎯 Common Patterns

### Pattern 1: Safe Session State Access

❌ **Wrong:**
```python
result = st.session_state.design_results  # May crash if not exists
```

✅ **Right:**
```python
# Option A: .get() with default
result = st.session_state.get('design_results', {})

# Option B: Check first
if 'design_results' in st.session_state:
    result = st.session_state.design_results
```

### Pattern 2: Safe Dictionary Access

❌ **Wrong:**
```python
ast_req = result['flexure']['Ast_req']  # KeyError if missing
```

✅ **Right:**
```python
# Option A: Nested .get()
ast_req = result.get('flexure', {}).get('Ast_req', 0)

# Option B: Check first
if 'flexure' in result and 'Ast_req' in result['flexure']:
    ast_req = result['flexure']['Ast_req']
```

### Pattern 3: Zero Division Protection

❌ **Wrong:**
```python
ratio = numerator / denominator  # ZeroDivisionError if denominator=0
```

✅ **Right:**
```python
# Option A: Ternary
ratio = numerator / denominator if denominator > 0 else 0

# Option B: If-block
if denominator > 0:
    ratio = numerator / denominator
else:
    ratio = 0
    st.warning("Denominator is zero, using 0 as default")
```

### Pattern 4: Import Error Handling

❌ **Wrong:**
```python
from structural_lib.dxf_export import LAYERS  # May fail
# Use LAYERS later without checking
```

✅ **Right:**
```python
try:
    from structural_lib.dxf_export import LAYERS
    HAS_DXF = True
except ImportError:
    HAS_DXF = False
    LAYERS = {  # Fallback
        "BEAM": (1, "CONTINUOUS"),
        # ... other layers
    }
```

### Pattern 5: Loading States

```python
from utils.loading_states import loading_context

# Use context manager for long operations
with loading_context("Computing design..."):
    result = design_beam(inputs)
    st.session_state.result = result

# Automatically shows spinner and handles errors
```

### Pattern 6: Caching for Performance

```python
from utils.caching import SmartCache

# Create cache instance
viz_cache = SmartCache(max_size=100, ttl=3600)

# Cache expensive operations
@viz_cache.cached
def generate_expensive_plot(data):
    # Expensive computation here
    return figure

# Use it
fig = generate_expensive_plot(st.session_state.data)
st.plotly_chart(fig)
```

---

## 🐛 Troubleshooting

### Issue 1: "NameError: name 'X' is not defined"

**Cause:** Variable used before definition
**Solution:**
1. Check variable is defined in all code paths
2. Check imports are at module level
3. If loop variable, scanner may be wrong (false positive)

### Issue 2: "KeyError: 'key_name'"

**Cause:** Dictionary access without checking if key exists
**Solution:** Use `.get()` with default (see Pattern 2)

### Issue 3: "AttributeError: 'X' object has no attribute 'Y'"

**Cause:** Accessing attribute without checking if exists
**Solution:**
```python
# Check first
if hasattr(obj, 'attr'):
    value = obj.attr

# Or use getattr
value = getattr(obj, 'attr', default_value)
```

### Issue 4: "ZeroDivisionError"

**Cause:** Division without protecting against zero
**Solution:** See Pattern 3

### Issue 5: Page Not Showing in Sidebar

**Cause:** Filename doesn't match pattern
**Solution:** Pages must be named: `NN_emoji_name.py` (e.g., `01_🏗️_beam_design.py`)

### Issue 6: Session State Not Persisting

**Cause:** Not using `st.session_state` correctly
**Solution:**
```python
# Initialize if not exists
if 'my_key' not in st.session_state:
    st.session_state.my_key = default_value

# Update
st.session_state.my_key = new_value

# Read
value = st.session_state.my_key
```

### Issue 7: Tests Failing with "No module named 'streamlit'"

**Cause:** Wrong Python environment
**Solution:**
```bash
# Always use venv Python
.venv/bin/python -m pytest streamlit_app/tests/
```

### Issue 8: Scanner Shows 100+ CRITICAL Issues

**Cause:** Likely false positives (loop vars, kwargs, Path ops)
**Solution:**
1. Review BUG_FIX_PLAN.md for categorization
2. Fix real bugs only
3. Document false positives
4. Wait for Scanner Phase 2 (ignore support)

---

## 🔧 CI/CD Integration

### GitHub Actions Workflows

**File:** `.github/workflows/streamlit-validation.yml`

**Checks:**
1. **AST Scanner** - Detects runtime errors
2. **Pylint** - Code quality
3. **Combined Analysis Report** - Summary

**When it runs:**
- On every push to branches
- On every PR
- Blocks merge if CRITICAL issues found

### Pre-commit Hooks

**File:** `.pre-commit-config.yaml`

**Hooks:**
- Black formatting
- Ruff linting
- Streamlit scanner (if editing streamlit_app/)

**How to use:**
```bash
# Install hooks (once)
pre-commit install

# Run manually
pre-commit run --all-files

# Bypass (emergency only, requires approval)
GIT_HOOKS_BYPASS=1 ./scripts/ai_commit.sh "message"
```

### Automation Scripts

| Script | Purpose |
|--------|---------|
| `scripts/ai_commit.sh` | Safe commit with validation |
| `scripts/check_streamlit_issues.py` | AST scanner |
| `scripts/test_page.sh` | Quick page test |
| `scripts/watch_tests.sh` | Auto-run tests on change |
| `scripts/create_test_scaffold.py` | Generate test boilerplate |

---

## 📖 Best Practices

### Code Organization

1. **One page = One file** in `pages/` directory
2. **Reusable components** go in `components/`
3. **Utilities** go in `utils/`
4. **Keep pages focused** - single responsibility

### Error Handling

```python
try:
    result = risky_operation()
    st.success("✅ Success!")
except ValueError as e:
    st.error(f"❌ Invalid input: {e}")
except Exception as e:
    st.error(f"❌ Unexpected error: {e}")
    # Log for debugging
    import traceback
    st.expander("Debug Info").code(traceback.format_exc())
```

For deep debugging, set `DEBUG=1` before `streamlit run` to show full tracebacks
from the shared `error_handler.py` decorator.

### Performance

1. **Use caching** for expensive operations
2. **Lazy load** data (load only when needed)
3. **Limit reruns** - use session state wisely
4. **Profile slow pages** with `@st.cache_data`

### Security

1. **Never commit secrets** - use environment variables
2. **Validate all user inputs**
3. **Sanitize file uploads**
4. **Use HTTPS in production**

### Documentation

1. **Docstrings on all functions**
2. **Comments for complex logic**
3. **README for each major feature**
4. **Update this guide when patterns change**

### Version Control

1. **Use PR workflow** for production code
2. **Direct commits** only for docs/minor fixes
3. **Descriptive commit messages**
4. **Link to issues/tasks**

---

## 📊 Current Status (Jan 2026)

### Features Implemented

| Feature | Status | Author | Lines |
|---------|--------|--------|-------|
| Beam Design | ✅ Complete | Agent 6 | 847 |
| Cost Optimizer | ✅ Complete | Agent 6 | 587 |
| Compliance Checker | ✅ Complete | Agent 6 | 454 |
| Documentation | ✅ Complete | Agent 6 | 455 |
| BBS Generator | ✅ Complete | Agent 6 | 466 |
| DXF Export | ✅ Complete | Agent 6 | 562 |
| Report Generator | ✅ Complete | Agent 6 | 317 |
| Batch Design | ✅ Complete | Agent 6 | 321 |
| Advanced Analysis | ✅ Complete | Agent 6 | 551 |
| Learning Center | ✅ Complete | Agent 6 | 565 |
| Demo Showcase | ✅ Complete | Agent 6 | 531 |

**Total:** 11 pages, 5,656 lines

### Quality Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| **Scanner Issues** | 120 | <30 | 🟡 In Progress |
| - CRITICAL | 28 (27 FP) | <5 | 🟡 Scanner Phase 2 |
| - HIGH | 62 | <30 | 🟡 Quality PR planned |
| - MEDIUM | 30 | <20 | ✅ OK |
| **Tests Passing** | 829/939 (88.3%) | 890/939 (95%) | 🟡 FIX-002 Phase 2 |
| **Code Coverage** | Unknown | >80% | ⏳ Not measured |

### Priority Tasks

1. **Scanner Phase 2** (~2-3 hours)
   - Add ignore file support
   - Fix loop variable detection
   - Fix **kwargs detection
   - Fix Path operation detection
   - Target: <5 false positives

2. **FIX-002 Phase 2** (~1.5 hours)
   - Add autouse fixture for state reset
   - Separate integration vs unit tests
   - Target: 99→<10 failures (95%+ pass rate)

3. **Quality PR: dict.get()** (~45 min)
   - Add .get() to 36 dict accesses
   - Files: compliance.py, batch_design.py, advanced_analysis.py
   - Target: 62→26 HIGH issues

4. **TASK-270: Python Tests** (~25 min)
   - Update 6 test expectations
   - Target: 2370/2370 tests passing (100%)

---

## 🎓 Learning Resources

### Official Docs
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit API Reference](https://docs.streamlit.io/library/api-reference)
- [Streamlit Community](https://discuss.streamlit.io/)

### Project-Specific
- `docs/streamlit-issues-catalog.md` - Known issues and solutions
- `docs/streamlit-prevention-system-review.md` - Quality system overview
- `BUG_FIX_PLAN.md` - Scanner issue analysis (in worktree)
- `QUALITY_FIX_PLAN.md` - Quality improvement roadmap (in worktree)

### For AI Agents
- `.github/copilot-instructions.md` - Project rules and patterns
- `docs/AGENT_WORKFLOW_MASTER_GUIDE.md` - Automation workflow
- `docs/AGENT_QUICK_REFERENCE.md` - Quick command reference

---

## 🚀 Next Steps for You

### Immediate Actions (Today)
1. ✅ **PR #314 merged** - Agent 6's 7 features now in main
2. ⏳ **Clean up worktree** - Remove Agent 6 worktree manually
3. ⏳ **Run TASK-270** - Fix 6 Python tests (25 min)

### This Week
1. **Scanner Phase 2** - Add ignore support (2-3 hours)
2. **FIX-002 Phase 2** - Test isolation (1.5 hours)
3. **Quality PR** - dict.get() improvements (45 min)

### This Month
1. **Code coverage** - Set up pytest-cov
2. **Documentation** - Add more examples to each page
3. **Performance** - Profile and optimize slow pages
4. **Security** - Add input sanitization

---

## 📝 Changelog

### 2026-01-09 - v1.0.0 (Initial Release)
- Created comprehensive maintenance guide
- Documented all 11 Streamlit features
- Added quality validation workflows
- Added troubleshooting section
- Added best practices and patterns
- Current status: 88.3% tests passing, 120 scanner issues (27 FP)

---

## 🤝 Contributing

When you make changes to the Streamlit app:

1. **Follow this guide** for all development
2. **Run validation** before committing
3. **Write tests** for new features
4. **Update this guide** if you add new patterns
5. **Document issues** in streamlit-issues-catalog.md

**Questions?** Check existing docs first, then ask in project discussions.

---

**Last Updated:** 2026-01-09 by Main Agent (Agent 8)
**Next Review:** After Scanner Phase 2 completion
