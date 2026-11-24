---
owner: Main Agent
status: active
last_updated: 2026-11-24
doc_type: reference
complexity: intermediate
tags: []
---

# Third-Party Licenses

**Type:** Reference
**Audience:** Developers
**Status:** Production Ready
**Importance:** Low
**Created:** 2025-01-01
**Last Updated:** 2026-11-24

---

The Python distribution uses a base runtime dependency and optional
dependency groups. The [package manifest](https://github.com/Pravin-surawase/structural_engineering_lib/blob/main/Python/pyproject.toml)
lists their version constraints.

## Runtime Dependencies

- `pydantic>=2.0` for validating the package's data models. Pip installs its
  required dependencies with the base package.

## Optional Dependencies

| Group reported by preflight | Required modules |
| --- | --- |
| `dxf` | ezdxf |
| `render` | ezdxf and Matplotlib |
| `report` | Jinja2 |
| `pdf` | ReportLab and WeasyPrint |
| `validation` | jsonschema |

## Development Dependencies
- `pytest`
- `pytest-cov`
- `black`
- `ruff`
- `mypy`
- `pre-commit`
- `bandit`
- `radon`
- `vulture`

## How to Refresh This File
Use a clean environment to generate a full dependency license report:

```bash
.venv/bin/python -m pip install pip-licenses
.venv/bin/python -m pip_licenses --format=markdown > docs/reference/third-party-licenses.md
```

Review the generated report before committing.
