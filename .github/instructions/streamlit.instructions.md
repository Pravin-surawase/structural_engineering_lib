---
applyTo: "**/streamlit_app/**"
---

# Streamlit Rules

- NEVER use `st.sidebar` inside `@st.fragment` functions (causes StreamlitAPIException)
- Safe patterns: `data.get('key', default)` not `data['key']`, `st.session_state.get()` not `.key`
- All imports at module level only
- Run before commit: `.venv/bin/python scripts/check_streamlit.py --all-pages`
- Run before commit: `.venv/bin/python scripts/check_streamlit.py --fragments`
