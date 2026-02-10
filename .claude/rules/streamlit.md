---
description: Rules for editing Streamlit app files
globs: streamlit_app/**
---

# Streamlit Safety Rules

## Fragment API (Session 30 crisis — causes runtime crashes)

NEVER use `st.sidebar` inside `@st.fragment` functions — causes `StreamlitAPIException`.
Also forbidden inside fragments: `st.tabs`, any function that uses `st.sidebar` internally.

```python
# WRONG — crashes at runtime:
@st.fragment
def bad():
    st.sidebar.button("Click")  # StreamlitAPIException!

# CORRECT:
@st.fragment
def good():
    st.button("Click")  # Regular widgets OK

# OR wrap the call:
with st.sidebar:
    my_fragment()  # Sidebar context OK outside the fragment
```

## Safe Patterns (scanner-enforced)

```python
value = data.get('key', default)              # NOT data['key'] (KeyError)
first = items[0] if len(items) > 0 else None  # NOT items[0] (IndexError)
result = a / b if b != 0 else 0               # NOT a / b (ZeroDivisionError)
value = st.session_state.get('key', default)  # NOT st.session_state.key (AttributeError)
```

## Import Rules

All imports at module level. NEVER import inside functions.

## Validation Before Commit

```bash
.venv/bin/python scripts/check_streamlit_issues.py --all-pages
.venv/bin/python scripts/check_fragment_violations.py
```
