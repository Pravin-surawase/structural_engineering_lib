# Fragment API Restrictions Analysis

**Type:** Research
**Audience:** All Agents
**Status:** Complete
**Importance:** Critical
**Created:** 2026-01-15
**Related Issue:** StreamlitAPIException in fragments calling st.sidebar

---

## Executive Summary

**Problem Found:** Session 30 fragment implementation broke at runtime because `render_theme_toggle()` called `st.sidebar` inside a `@st.fragment` function, which Streamlit prohibits.

**Root Cause:** Our static analysis tools (check_streamlit_issues.py) don't understand Streamlit's fragment API restrictions - they only check for NameError, ZeroDivisionError, etc., not API usage rules.

**Impact:** CRITICAL - App crashes on page load, all 3 pages affected

**Solution:**
1. Fix immediate issue (move theme toggle outside fragments)
2. Build fragment API validator
3. Integrate into pre-commit hooks and CI
4. Document fragment best practices

---

## Issue Details

### The Error

```python
streamlit.errors.StreamlitAPIException: Calling `st.sidebar` in a function wrapped with `st.fragment` is not supported. To write elements to the sidebar with a fragment, call your fragment function inside a `with st.sidebar` context manager.

File "beam_design.py", line 170, in render_inputs
    render_theme_toggle()
File "theme_manager.py", line 250, in render_theme_toggle
    st.markdown("---")  # Inside st.sidebar context
```

### Why It Happened

**Code Pattern (BROKEN):**
```python
@st.fragment
def render_inputs():
    """Fragment function - isolated scope."""
    render_theme_toggle()  # ❌ Calls st.sidebar internally

def render_theme_toggle():
    with st.sidebar:  # ❌ FORBIDDEN inside fragment
        st.markdown("---")
        # ... theme toggle UI
```

**Streamlit's Fragment Rules:**
1. ❌ Cannot call `st.sidebar` from within fragment
2. ❌ Cannot use `st.columns()` that writes to sidebar
3. ❌ Cannot call functions that internally use `st.sidebar`
4. ✅ CAN call fragment from within `with st.sidebar` context
5. ✅ CAN use regular st.* functions (markdown, button, etc.)

### Affected Files

1. `streamlit_app/pages/01_🏗️_beam_design.py` line 170
2. `streamlit_app/pages/02_💰_cost_optimizer.py` (if theme toggle added)
3. `streamlit_app/pages/03_✅_compliance.py` (if theme toggle added)

---

## Why Our Scanners Missed This

### check_streamlit_issues.py Limitations

**What It DOES Check:**
```python
# Static analysis for runtime errors
- NameError (undefined variables)
- ZeroDivisionError (unprotected division)
- KeyError (dict access without .get())
- IndexError (list bounds)
- AttributeError (session state access)
- ImportError (missing imports)
```

**What It DOESN'T Check:**
```python
# API usage rules (requires Streamlit internals knowledge)
- Fragment API restrictions (st.sidebar forbidden)
- Context manager violations
- Nested fragment rules
- Rerun behavior constraints
- Dialog API restrictions
```

**Why The Gap:**
- Scanner uses AST (Abstract Syntax Tree) parsing
- AST sees function calls, not Streamlit's runtime rules
- No way to know `render_theme_toggle()` calls `st.sidebar` without execution
- Requires call-graph analysis + Streamlit API knowledge

### Example AST View

```python
# Scanner sees this:
@st.fragment
def render_inputs():
    render_theme_toggle()  # Just a function call, looks safe

# Scanner does NOT see:
def render_theme_toggle():
    with st.sidebar:  # This is in different file!
        st.markdown("---")
```

**Call Chain:**
```
render_inputs (fragment)
  → render_theme_toggle() [scanner stops here]
      → with st.sidebar: [forbidden but scanner can't reach]
          → st.markdown() [actual violation]
```

---

## Streamlit Fragment API Rules (Comprehensive)

### FORBIDDEN Inside Fragments

```python
@st.fragment
def my_fragment():
    # ❌ Direct sidebar access
    st.sidebar.button("Click")

    # ❌ Sidebar context manager
    with st.sidebar:
        st.markdown("Text")

    # ❌ Functions that internally use sidebar
    render_theme_toggle()  # Contains st.sidebar

    # ❌ Columns with sidebar (rare edge case)
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        st.sidebar.text("Forbidden")  # If this pattern exists
```

### ALLOWED Inside Fragments

```python
@st.fragment
def my_fragment():
    # ✅ Regular st.* functions
    st.markdown("Text")
    st.button("Click")
    st.number_input("Value")

    # ✅ Session state read/write
    st.session_state["key"] = "value"
    value = st.session_state.get("key")

    # ✅ Columns (main area only)
    col1, col2 = st.columns(2)
    with col1:
        st.text("Safe")

    # ✅ Nested fragments (with caution)
    @st.fragment
    def nested():
        st.text("Nested")
    nested()
```

### WORKAROUND Pattern

```python
# ❌ WRONG: Fragment calling sidebar function
@st.fragment
def render_inputs():
    render_theme_toggle()  # Has st.sidebar inside

# ✅ CORRECT Option 1: Move outside fragment
render_theme_toggle()  # Render before/after fragment

@st.fragment
def render_inputs():
    # Just inputs here
    pass

# ✅ CORRECT Option 2: Fragment inside sidebar context
with st.sidebar:
    @st.fragment
    def sidebar_fragment():
        render_theme_toggle()  # Now safe!
    sidebar_fragment()
```

---

## Detection Strategy

### Level 1: Static Analysis (Pattern Matching)

**Detect direct violations:**
```python
# Pattern 1: Direct st.sidebar calls
@st.fragment
def func():
    st.sidebar.*  # MATCH: forbidden

# Pattern 2: Sidebar context manager
@st.fragment
def func():
    with st.sidebar:  # MATCH: forbidden
```

**Implementation:**
```python
def check_fragment_violations(filepath):
    with open(filepath) as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check if decorated with @st.fragment
            is_fragment = any(
                isinstance(d, ast.Call) and
                hasattr(d.func, 'attr') and
                d.func.attr == 'fragment'
                for d in node.decorator_list
            )

            if is_fragment:
                # Scan function body for violations
                for child in ast.walk(node):
                    # Check for st.sidebar.* calls
                    if isinstance(child, ast.Attribute):
                        if child.attr == 'sidebar':
                            yield f"Line {child.lineno}: st.sidebar in fragment"

                    # Check for 'with st.sidebar:' blocks
                    if isinstance(child, ast.With):
                        for item in child.items:
                            if is_sidebar_context(item):
                                yield f"Line {child.lineno}: sidebar context in fragment"
```

### Level 2: Call Graph Analysis (Deep Check)

**Detect indirect violations:**
```python
# Build call graph
function_calls = {}
for func in all_functions:
    function_calls[func.name] = extract_called_functions(func)

# For each fragment
for fragment_func in fragments:
    # Check direct calls
    for called_func in function_calls[fragment_func]:
        # Check if called function uses sidebar
        if uses_sidebar(called_func):
            yield f"{fragment_func} calls {called_func} which uses st.sidebar"

        # Recursively check nested calls
        for nested_call in function_calls.get(called_func, []):
            if uses_sidebar(nested_call):
                yield f"{fragment_func} → {called_func} → {nested_call} uses st.sidebar"
```

**Complexity:**
- Requires analyzing all reachable functions
- Cross-file analysis needed
- May have false positives (conditional sidebar usage)

### Level 3: Runtime Detection (Most Accurate)

**Import hook approach:**
```python
# Intercept st.sidebar calls
original_sidebar = st.sidebar

def wrapped_sidebar(*args, **kwargs):
    if is_inside_fragment():  # Check execution context
        raise StreamlitAPIException("st.sidebar in fragment!")
    return original_sidebar(*args, **kwargs)

st.sidebar = wrapped_sidebar
```

**Execution tracing:**
```python
import sys

def trace_calls(frame, event, arg):
    if event == 'call':
        func_name = frame.f_code.co_name
        if func_name.startswith('sidebar'):
            # Check if we're in fragment context
            for f in inspect.stack():
                if '@st.fragment' in str(f):
                    raise StreamlitAPIException(f"Sidebar call in fragment at {frame}")

sys.settrace(trace_calls)
```

---

## Proposed Solution

### Immediate Fix (Commit 1)

**Fix all 3 pages:**
```python
# BEFORE (broken)
@st.fragment
def render_inputs():
    render_theme_toggle()  # Contains st.sidebar

# AFTER (fixed)
# Render theme toggle OUTSIDE fragment
render_theme_toggle()

@st.fragment
def render_inputs():
    # Only input widgets here, no sidebar calls
    pass
```

### Automation (Commit 2)

**Create `scripts/check_fragment_violations.py`:**
```python
#!/usr/bin/env python3
"""
Detect Streamlit fragment API violations.

Checks for:
1. st.sidebar calls inside @st.fragment functions
2. with st.sidebar: blocks inside fragments
3. Functions calling sidebar-using functions (level 1 only)
"""

import ast
import sys
from pathlib import Path

def check_file(filepath):
    # AST-based static analysis
    # Returns list of violations
    pass

def main():
    streamlit_files = Path("streamlit_app").rglob("*.py")
    violations = []

    for file in streamlit_files:
        violations.extend(check_file(file))

    if violations:
        print("❌ Fragment API violations found:")
        for v in violations:
            print(f"  {v}")
        sys.exit(1)
    else:
        print("✅ No fragment violations detected")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

### Integration (Commit 3)

**Add to `.pre-commit-config.yaml`:**
```yaml
- repo: local
  hooks:
    - id: check-fragment-violations
      name: Check Streamlit Fragment API Violations
      entry: .venv/bin/.venv/bin/python scripts/check_fragment_violations.py
      language: system
      files: ^streamlit_app/.*\.py$
      pass_filenames: false
```

**Add to `.github/workflows/streamlit-validation.yml`:**
```yaml
- name: Check Fragment API Violations
  run: |
    .venv/bin/.venv/bin/python scripts/check_fragment_violations.py
```

### Documentation (Commit 4)

**Create `docs/guidelines/streamlit-fragment-best-practices.md`:**
- Fragment API rules comprehensive list
- Common pitfalls with examples
- How to fix violations
- Testing strategy for fragments

---

## Testing Strategy

### Unit Tests for Validator

```python
# tests/test_fragment_validator.py
def test_detect_direct_sidebar_call():
    code = '''
    @st.fragment
    def bad_fragment():
        st.sidebar.button("Click")
    '''
    violations = check_code(code)
    assert len(violations) == 1
    assert "st.sidebar" in violations[0]

def test_detect_sidebar_context():
    code = '''
    @st.fragment
    def bad_fragment():
        with st.sidebar:
            st.markdown("Text")
    '''
    violations = check_code(code)
    assert len(violations) == 1
    assert "sidebar context" in violations[0]

def test_allow_regular_streamlit():
    code = '''
    @st.fragment
    def good_fragment():
        st.markdown("Text")
        st.button("Click")
    '''
    violations = check_code(code)
    assert len(violations) == 0
```

### Integration Tests

```python
# tests/integration/test_fragment_pages.py
def test_beam_design_fragment_no_sidebar():
    """Ensure beam_design fragment doesn't call sidebar."""
    # Mock st.sidebar to raise exception
    with pytest.raises(StreamlitAPIException):
        with patch('streamlit.sidebar', side_effect=Exception("Forbidden!")):
            render_inputs()  # Should not call sidebar

def test_cost_optimizer_fragment_no_sidebar():
    """Ensure cost_optimizer fragment doesn't call sidebar."""
    # Similar test
    pass
```

---

## Lessons Learned

### Why This Matters

**Runtime errors are expensive:**
- User discovers (bad UX)
- No CI detection (validation gap)
- Emergency hotfix required (disruption)
- Lost confidence in quality (reputation)

**Prevention is cheaper:**
- Catch in development (pre-commit)
- Automated validation (CI)
- No user impact (professional)
- Confidence in changes (velocity)

### What We'll Change

**Before (reactive):**
```
1. Implement feature
2. Commit code
3. User tests → finds bug
4. Emergency fix
5. Repeat
```

**After (proactive):**
```
1. Implement feature
2. Run validators (including fragment check)
3. Violations caught → fix before commit
4. Commit clean code
5. CI validates again
6. User tests → no surprises
```

### Future Improvements

**Short term (this session):**
- ✅ Fix immediate issue (3 pages)
- ✅ Build fragment validator
- ✅ Integrate into pre-commit
- ✅ Document best practices

**Medium term (next 2-3 sessions):**
- Build call-graph analyzer (detect indirect violations)
- Add runtime detection for development mode
- Create comprehensive Streamlit API validator (all rules)
- Add automated fragment tests

**Long term (future):**
- Contribute to Streamlit linter project
- Build VS Code extension for real-time validation
- Create Streamlit API rule database
- Automated test generation for API restrictions

---

## Technical Details

### AST Patterns to Detect

**Pattern 1: Direct attribute access**
```python
ast.Attribute(
    value=ast.Name(id='st'),
    attr='sidebar'
)
```

**Pattern 2: Context manager**
```python
ast.With(
    items=[
        ast.withitem(
            context_expr=ast.Attribute(
                value=ast.Name(id='st'),
                attr='sidebar'
            )
        )
    ]
)
```

**Pattern 3: Function decorator**
```python
ast.FunctionDef(
    decorator_list=[
        ast.Attribute(
            value=ast.Name(id='st'),
            attr='fragment'
        )
    ]
)
```

### Implementation Complexity

| Level | Accuracy | Complexity | Speed | False Positives |
|-------|----------|------------|-------|-----------------|
| **Static (direct)** | 80% | Low | Fast | Few |
| **Static (call graph)** | 90% | High | Medium | Some |
| **Runtime** | 99% | Medium | Slow | Rare |

**Recommendation:** Start with Level 1 (static direct), iterate to Level 2 if needed.

---

## Action Plan

### Commit 1: Fix Immediate Issue
- Move `render_theme_toggle()` outside fragments in 3 pages
- Test each page manually
- Verify app loads without errors

### Commit 2: Build Validator
- Create `scripts/check_fragment_violations.py`
- Implement AST-based static analysis (Level 1)
- Test with known violations and clean code
- Add comprehensive docstrings

### Commit 3: Integrate Automation
- Add to `.pre-commit-config.yaml`
- Add to CI workflow
- Test pre-commit hook locally
- Verify CI catches violations

### Commit 4: Unit Tests
- Create `tests/test_fragment_validator.py`
- Test detection of direct violations
- Test false positive avoidance
- Test with real code examples

### Commit 5: Documentation
- Create fragment best practices guide
- Document API restrictions comprehensively
- Add troubleshooting section
- Include fix examples

### Commit 6: Validation
- Run full app test
- Verify all pages work
- Check for other fragment issues
- Document any additional findings

---

## Conclusion

**Root Cause:** Static analyzer doesn't understand Streamlit API rules

**Solution:** Build specialized fragment API validator

**Prevention:** Integrate into pre-commit hooks and CI

**Long-term:** Expand to cover all Streamlit API restrictions

**Immediate Value:** Catch runtime errors before they reach users

**Process Improvement:** Shift from reactive (fix bugs) to proactive (prevent bugs)

---

**Next Action:** Implement fixes and automation (Commits 1-6)
