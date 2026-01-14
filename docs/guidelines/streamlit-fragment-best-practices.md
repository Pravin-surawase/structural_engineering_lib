# Streamlit Fragment Best Practices

**Type:** Guide
**Audience:** All Agents, Developers
**Status:** Approved
**Importance:** Critical
**Version:** 1.0.0
**Created:** 2026-01-13
**Last Updated:** 2026-01-13
**Related Tasks:** TASK-603
**Location Rationale:** Guidelines for code patterns (per folder-structure-governance.md)

---

## Overview

This guide establishes best practices for using Streamlit's `@st.fragment` decorator to prevent API violations and runtime errors.

**Why This Matters:** In Session 30, we added fragments to three pages but violated Streamlit API rules, causing runtime crashes. This guide documents the rules and patterns to prevent such issues.

---

## Fragment API Rules

### ✅ Allowed in Fragments

```python
@st.fragment
def render_content():
    # Regular Streamlit calls are OK
    st.write("Hello")
    st.number_input("Value", value=0)
    st.button("Click me")
    st.markdown("**Bold text**")
    st.selectbox("Choice", [1, 2, 3])

    # Data display is OK
    st.dataframe(df)
    st.table(data)
    st.metric("Score", 100)

    # Layouts are OK
    col1, col2 = st.columns(2)
    with col1:
        st.write("Left")
    with col2:
        st.write("Right")

    # Forms are OK (but use carefully)
    with st.form("my_form"):
        st.text_input("Name")
        st.form_submit_button("Submit")
```

### ❌ Forbidden in Fragments

```python
@st.fragment
def bad_fragment():
    # ❌ FORBIDDEN: st.sidebar calls
    st.sidebar.write("Text")
    st.sidebar.number_input("Value", value=0)
    st.sidebar.button("Click")

    # ❌ FORBIDDEN: with st.sidebar context
    with st.sidebar:
        st.write("Text")

    # ❌ FORBIDDEN: Function that internally uses sidebar
    render_theme_toggle()  # If this calls st.sidebar internally!
```

---

## Common Patterns

### Pattern 1: Sidebar Inputs (CORRECT)

```python
# ✅ CORRECT: Call fragment INSIDE sidebar context
with st.sidebar:
    @st.fragment
    def render_inputs():
        # No st.sidebar prefix needed - we're already in sidebar!
        st.subheader("Configuration")

        with st.form("input_form"):
            value = st.number_input("Value", value=0)
            submitted = st.form_submit_button("Apply")
            if submitted:
                return {"value": value}
        return None

    inputs = render_inputs()
```

**Why this works:** The fragment function doesn't call `st.sidebar.*` - the fragment itself is called from within the sidebar context.

### Pattern 2: Main Area with Fragmented Sections

```python
# ✅ CORRECT: Fragment for main area calculations
@st.fragment
def render_results(inputs):
    """Render results section with live updates."""
    st.subheader("Results")

    # Calculations
    result = calculate_something(inputs)

    # Display
    st.metric("Output", result)
    st.plotly_chart(create_chart(result))

# Call from main area
render_results(inputs)
```

### Pattern 3: Avoiding Indirect Sidebar Usage

```python
# ❌ WRONG: Fragment calls function that uses sidebar
@st.fragment
def bad_pattern():
    render_theme_toggle()  # This uses st.sidebar internally!

# ✅ CORRECT: Don't call sidebar-using functions from fragments
@st.fragment
def good_pattern():
    # Only use direct Streamlit calls that don't touch sidebar
    st.selectbox("Theme", ["Light", "Dark"])  # Direct widget
```

---

## Debugging Fragment Issues

### Symptom: StreamlitAPIException

```
StreamlitAPIException: Calling st.sidebar in a function wrapped with st.fragment is not supported.
```

**Diagnosis Steps:**

1. **Find the fragment definition:**
   ```bash
   grep -n "@st.fragment" streamlit_app/pages/*.py
   ```

2. **Check for direct sidebar calls:**
   ```bash
   python scripts/check_fragment_violations.py --file <file>.py
   ```

3. **Check for indirect sidebar calls:**
   - Look at functions called from fragment
   - Trace through: fragment → helper_function → st.sidebar

### Fix Strategies

**Strategy 1: Move fragment inside sidebar**
```python
# BEFORE (broken)
@st.fragment
def render():
    st.sidebar.subheader("Title")

render()

# AFTER (fixed)
with st.sidebar:
    @st.fragment
    def render():
        st.subheader("Title")  # No st.sidebar prefix

    render()
```

**Strategy 2: Remove fragment from sidebar sections**
```python
# BEFORE (broken)
@st.fragment
def render():
    with st.sidebar:
        st.write("Text")

# AFTER (fixed) - Don't use fragments for sidebar
def render():
    with st.sidebar:
        st.write("Text")
```

**Strategy 3: Extract non-sidebar logic**
```python
# BEFORE (broken)
@st.fragment
def render():
    render_theme_toggle()  # Uses sidebar
    st.write("Main content")

# AFTER (fixed) - Split responsibilities
render_theme_toggle()  # Outside fragment

@st.fragment
def render_content():
    st.write("Main content")  # Only main area

render_content()
```

---

## Automation & Validation

### Pre-commit Hook (Automatic)

Fragment validator runs automatically on commit:

```bash
# Triggers on any streamlit_app/*.py file change
git commit -m "fix: update page"

# Hook output:
# Check Streamlit fragment API violations..........Passed
```

### Manual Validation

```bash
# Check single file
python scripts/check_fragment_violations.py --file streamlit_app/pages/beam_design.py

# Check all Streamlit files
python scripts/check_fragment_violations.py

# Verbose mode (shows fragments found)
python scripts/check_fragment_violations.py --verbose
```

### CI Integration

GitHub Actions runs fragment validator on every push/PR:

```yaml
# .github/workflows/streamlit-validation.yml
fragment-validator:
  name: Fragment API Validator
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Run Fragment API Validator
      run: python scripts/check_fragment_violations.py
```

---

## Testing Fragment Code

### Unit Test Pattern

```python
# tests/test_fragments.py
def test_fragment_no_sidebar_calls():
    """Fragment should not call st.sidebar."""
    # Use AST to verify
    from scripts.check_fragment_violations import FragmentViolationDetector

    with open("streamlit_app/pages/my_page.py") as f:
        code = f.read()

    detector = FragmentViolationDetector(code, "my_page.py")
    violations = detector.check()

    assert len(violations) == 0, f"Found violations: {violations}"
```

### Integration Test Pattern

```python
# tests/apptest/test_page_loads.py
from streamlit.testing.v1 import AppTest

def test_page_loads_without_error():
    """Page should load without StreamlitAPIException."""
    at = AppTest.from_file("streamlit_app/pages/02_💰_cost_optimizer.py")
    at.run()

    # Should not raise exception
    assert not at.exception
```

---

## Migration Checklist

When adding fragments to existing pages:

### Phase 1: Analysis
- [ ] Identify sections that would benefit from fragments
- [ ] Check if section uses `st.sidebar` (direct or indirect)
- [ ] Plan fragment boundaries (forms, calculations, displays)

### Phase 2: Implementation
- [ ] Add `@st.fragment` decorator
- [ ] Move fragment call inside `with st.sidebar:` if needed
- [ ] Remove `st.sidebar` prefixes from inside fragment
- [ ] Test locally (load page, interact with widgets)

### Phase 3: Validation
- [ ] Run fragment validator: `python scripts/check_fragment_violations.py`
- [ ] Run AST scanner: `python scripts/check_streamlit_issues.py --all-pages`
- [ ] Run AppTest: `pytest tests/apptest/test_<page>.py`
- [ ] Manual browser test: Load page, verify no exceptions

### Phase 4: Commit
- [ ] Pre-commit hooks pass (automatic)
- [ ] CI checks pass (automatic)
- [ ] Document any non-standard patterns in code comments

---

## Performance Considerations

### When to Use Fragments

✅ **Good candidates:**
- Forms with multiple inputs that change frequently
- Calculation sections that update independently
- Data visualizations that refresh on their own
- Widgets that trigger expensive re-renders

❌ **Avoid for:**
- Simple static content
- Sections that rarely change
- Sidebar navigation (violates API)
- Theme switching (uses sidebar internally)

### Fragment Granularity

```python
# ❌ TOO FINE: Every widget is a fragment (overhead!)
@st.fragment
def widget1():
    st.number_input("A", value=0)

@st.fragment
def widget2():
    st.number_input("B", value=0)

# ✅ RIGHT: Logical group is a fragment
@st.fragment
def input_group():
    with st.form("inputs"):
        a = st.number_input("A", value=0)
        b = st.number_input("B", value=0)
        st.form_submit_button("Apply")
```

---

## Troubleshooting

### Issue: "Calling st.sidebar not supported"

**Cause:** Fragment calls `st.sidebar.*` directly or indirectly.

**Solution:** Run validator, fix violations:
```bash
python scripts/check_fragment_violations.py --verbose
# Shows: Line X: Direct st.sidebar in 'function_name'
```

### Issue: Pre-commit hook fails

**Cause:** New fragment code has API violations.

**Solution:**
1. See which file failed: `git status`
2. Run validator on that file
3. Fix violations
4. Re-commit (hook will pass)

### Issue: CI fails but local checks pass

**Cause:** Different Python versions or missing dependencies.

**Solution:** CI uses Python 3.11, check locally:
```bash
python --version  # Should match CI
python scripts/check_fragment_violations.py  # Should pass
```

---

## References

- **Streamlit Fragment Docs:** https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment
- **API Restrictions Analysis:** [docs/research/fragment-api-restrictions-analysis.md](../research/fragment-api-restrictions-analysis.md)
- **Validator Script:** [scripts/check_fragment_violations.py](../../scripts/check_fragment_violations.py)
- **Session 30 Bug Discovery:** [docs/SESSION_LOG.md](../SESSION_LOG.md) (2026-01-13)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-13 | Initial guide after Session 30 bug discovery |

---

**Remember:** When in doubt, run the validator! It's faster than debugging runtime errors.
