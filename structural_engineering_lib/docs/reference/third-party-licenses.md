# Third-Party Licenses

**Type:** Reference
**Audience:** Developers
**Status:** Production Ready
**Importance:** Low
**Created:** 2025-01-01
**Last Updated:** 2026-01-13

---

This repository is primarily standard-library based. Optional and development tools introduce third-party licenses.

## Runtime Dependencies
- Standard library only (core runtime)

## Optional Dependencies
- `ezdxf` (DXF export)
- `matplotlib` (rendering support)

## Development Dependencies
- `pytest`
- `pytest-cov`
- `black`
- `ruff`
- `mypy`
- `pre-commit`
- `bandit`
- `isort`
- `radon`
- `vulture`

## How to Refresh This File
Use a clean environment to generate a full dependency license report:

```bash
.venv/bin/python -m pip install pip-licenses
.venv/bin/python -m pip_licenses --format=markdown > docs/reference/third-party-licenses.md
```

Review the generated report before committing.
