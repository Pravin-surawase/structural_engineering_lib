# Streamlit App Tests

Component, page, and integration tests for the Streamlit UI.

## Coverage

45 test files covering pages, components, utils, and design system integration.

## Running Tests

```bash
cd /path/to/repo && .venv/bin/pytest streamlit_app/tests/ -v
```

## Key Test Areas

- Page smoke tests (`test_page_smoke.py`)
- AI assistant (`test_ai_page.py`)
- Visualization components (`test_visualizations.py`, `test_enhanced_visualizations.py`)
- Session management (`test_session_manager.py`)
- Error handling (`test_error_handler.py`)
- Design system integration (`test_design_system_integration.py`)
- Cost optimizer (`test_cost_optimizer.py`)
- CSV import (`test_multi_format_import.py`)
