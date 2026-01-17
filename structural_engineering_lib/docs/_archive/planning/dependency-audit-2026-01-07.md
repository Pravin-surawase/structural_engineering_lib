# Dependency Audit (2026-01-07)

**Scope:** Python package dependencies (`Python/pyproject.toml`)
**Goal:** Identify unused or unclear dependencies and document next actions

---

## Sources

- `Python/pyproject.toml` (declared dependencies)
- Import scan: `rg -n "import|from" Python/structural_lib`

---

## Declared Dependencies

### Core (runtime)

- **None declared** under `[project].dependencies`

### Optional extras

- `dev`: pytest, pytest-cov, pytest-benchmark, black, mypy, pre-commit, ruff, bandit, isort
- `dxf`: `ezdxf>=1.0`
- `render`: `ezdxf>=1.0`, `matplotlib>=3.5`

---

## Import Scan (external libraries)

Observed imports in `Python/structural_lib`:

- `ezdxf` (used in `dxf_export.py` and referenced in API/CLI guards)

No other third-party imports found (numpy, pandas, matplotlib, etc.).

---

## Findings

1. **`ezdxf` is required for DXF export**
   - ✅ Usage confirmed in `structural_lib/dxf_export.py` and related API helpers.
   - Status: keep `dxf` extra.

2. **`matplotlib` not referenced in codebase**
   - No imports found in `structural_lib` or examples.
   - `render` extra appears to be planned but not implemented.

3. **Dev tools are aligned with pre-commit config**
   - `isort` and `bandit` are used by `.pre-commit-config.yaml`.

---

## Recommendations

- **Decision (pending):**
  - Option A: remove `render` extra until rendering support is implemented.
  - Option B: implement rendering pipeline and add `matplotlib` usage to justify extra.

- **Document intent:** add a short note in `Python/README.md` describing which extras
  are implemented today (`dev`, `dxf`) and which are planned (`render`).

---

## Follow-up Checklist

- [ ] Decide on `render` extra (keep with TODO vs remove)
- [ ] If keeping, add a note to `Python/README.md`
- [ ] If removing, update `pyproject.toml` and documentation
