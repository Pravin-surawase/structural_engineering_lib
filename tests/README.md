# Top-Level Tests

Cross-cutting tests for Streamlit pages, migration workflows, and script validation.

## Structure

| Directory | Purpose |
|-----------|---------|
| `apptest/` | Streamlit page smoke and integration tests |
| `fixtures/migration/` | Golden files for migration test verification |
| `integration/` | Migration integration tests |

Root-level test files cover script validation, Streamlit component tests, and design system tests.

## Running Tests

```bash
cd /path/to/repo && .venv/bin/pytest tests/ -v
```

## Relationship to Other Test Directories

- `Python/tests/` — structural_lib core library tests
- `fastapi_app/tests/` — FastAPI endpoint tests
- `streamlit_app/tests/` — Streamlit-specific component tests
- This directory (`tests/`) — cross-cutting and Streamlit page-level tests
