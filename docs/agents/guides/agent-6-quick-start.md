# Agent 6 Quick Start (Streamlit UI Specialist)

**Role:** Build production-ready Streamlit dashboards for structural engineering
**Time to onboard:** 60 seconds

---

## Your Mission

You build the **Streamlit web interface** for the structural engineering library.
This includes beam design calculators, results visualization, and user-friendly forms.

---

## Quick Start (Copy-Paste Ready)

```bash
# 1. Check Streamlit app status
ls -la streamlit_app/

# 2. Run the app locally
cd streamlit_app && streamlit run Home.py

# 3. Run tests
cd streamlit_app && pytest tests/ -v

# 4. Check for code issues (AST scanner)
.venv/bin/python scripts/check_streamlit.py --all-pages
```

---

## Key Files

| File | Purpose |
|------|---------|
| `streamlit_app/Home.py` | Main entry point |
| `streamlit_app/pages/*.py` | Individual pages |
| `streamlit_app/utils/*.py` | Shared utilities |
| `streamlit_app/tests/*.py` | Test suite |
| `docs/contributing/streamlit-maintenance-guide.md` | Maintenance docs |

---

## Your Workflow

1. **Check current tasks:** [agent-6-tasks-streamlit.md](../../_archive/planning-20260119/agent-6-tasks-streamlit.md)
2. **Understand prevention system:** [streamlit-comprehensive-prevention-system.md](../../contributing/streamlit-comprehensive-prevention-system.md)
3. **Review issues catalog:** [streamlit-issues-catalog.md](../../contributing/streamlit-issues-catalog.md)

---

## Quality Standards

- ✅ Type hints on all functions
- ✅ Docstrings with examples
- ✅ Error handling for user inputs
- ✅ 100% test coverage for new features
- ✅ Run AST scanner before commit

---

## Common Patterns

### Safe Division
```python
# ❌ Wrong
result = value / divisor

# ✅ Correct
result = value / divisor if divisor != 0 else 0.0
```

### Session State
```python
# ❌ Wrong
if "key" in st.session_state:
    value = st.session_state["key"]

# ✅ Correct
value = st.session_state.get("key", default_value)
```

---

## Next Step

→ Go to [Agent 6 Streamlit Hub](agent-6-streamlit-hub.md) for detailed docs
