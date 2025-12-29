# Testing Strategy & Setup (Python-first, VBA parity aware)

**Purpose:** Document how testing is currently set up, what it covers well, what gaps remain, and the recommended next improvements.

**Scope:** This doc focuses on Python test automation + CI. VBA tests are currently manual and are tracked as future automation work.

---

## 1) Current test setup (what exists today)

### Python tests

- Location: `Python/tests/`
- Runner: `pytest`
- Config: `Python/pytest.ini` (`testpaths = tests`)

**How to run locally (fast):**
- From `Python/`: `python -m pytest -q`

**Fast checks before commit (pick what changed):**
- Docs-only: from repo root, `python scripts/check_doc_versions.py`
- Links touched: from repo root, `python scripts/check_links.py`
- Code + tests: from `Python/`, `python -m pytest -q`

**How to run with coverage:**
- From `Python/`: `python -m pytest --cov=structural_lib --cov-report=term-missing --cov-report=xml`

**How to run the CI-equivalent check locally (includes coverage gate):**
- From `Python/`: `python -m pytest --cov=structural_lib --cov-branch --cov-report=term-missing --cov-report=xml --cov-fail-under=85`

### CI (GitHub Actions)

Workflow: `.github/workflows/python-tests.yml`

- Lint/typecheck job:
  - `black --check .`
  - `mypy`
- Test job:
  - Python matrix: 3.9, 3.10, 3.11, 3.12
  - Installs: `pip install -e ".[dev,dxf]"`
  - Runs: pytest with coverage + uploads `coverage.xml`
  - Coverage gate: `--cov-fail-under=85` (branch coverage)
  - Packaging smoke: `python -m build`

**What this gives us:**
- Cross-version confidence (3.9–3.12)
- Static formatting check
- Basic typecheck
- Coverage visibility (artifact)
- Packaging correctness check

---

## 2) What’s being tested well

- Core strength design logic:
  - Flexure: limiting moment checks, under/over-reinforced behavior.
  - Shear: Tv/Tc/Tc_max logic, spacing caps, min shear reinforcement behavior.
- Table and materials edge behavior:
  - Table 19 pt clamping and grade selection behavior.
  - Table 20 Tc_max interpolation.
  - Materials curves and guardrails.
- Detailing module:
  - Bond stress lookup.
  - Development length and lap length.
  - Spacing and arrangement selection.
- Integration module:
  - CSV/JSON parsing.
  - Data normalization and defaulting.
- DXF export:
  - Smoke tests exist (basic generation path).

---

## 3) Current coverage snapshot (observed)

Latest verified local run (Dec 2025): **100% total coverage** with `--cov-report=term-missing`.

Notes:
- CI gate is `--cov-fail-under=85` (branch coverage).
- Tests that execute modules via `runpy.run_module(...)` clear entries from `sys.modules` to avoid `RuntimeWarning` noise.

---

## 4) Key gaps / risks (senior tester assessment)

1. **Coverage gate is conservative**
  - CI enforces a minimum total branch coverage of 85% to prevent silent regressions.
  - This is intentionally low to avoid blocking feature work; raise gradually as coverage improves.

2. **High-risk areas (now covered, still sensitive to change)**
  - These modules historically had the most uncovered branches and are the most regression-prone due to edge conditions and I/O/optional-dependency behavior.
  - Current status: tests exercise these paths (including optional DXF behavior via stubs), but future refactors here deserve extra review.

3. **Mixed test style and import patterns**
   - Mix of `unittest.TestCase` and pure pytest.
   - Several tests add `sys.path.append(...)` even though CI installs the package.

4. **Hermeticity / file cleanup**
   - Some tests use temp files with manual cleanup; `tmp_path` would be safer.

5. **Parity regressions not yet automated**
   - There is no Python↔VBA parity harness yet (tracked as future work).

---

## 5) Recommendations (priority order)

### P0 — Protect against regression

- Keep the CI **coverage gate** at 85% (current baseline).

### P1 — Increase confidence where failures are expensive

- Add threshold tests around known transitions:
  - `Mu ≈ Mu_lim` (just below/above)
  - `Tv ≈ Tc_max` (at/just above)
  - Table clamp boundaries (`pt=0.149/0.15`, `pt=3.0/3.01`)

### P2 — Harden I/O paths

- Add negative tests for `excel_integration.py`:
  - missing required columns
  - wrong data types
  - empty input files
  - invalid output directories

### P3 — Improve DXF confidence (without brittle tests)

- Keep tests resilient by checking:
  - file created
  - required layers exist
  - minimum expected entities/text tags exist
  - avoid asserting exact entity order/coordinates unless needed

### P4 — Test hygiene

- Gradually standardize on pytest style.
- Prefer `tmp_path` for filesystem tests.
- Remove `sys.path.append(...)` where not needed.

---

## 6) Where to add new tests (map)

- Flexure/shear/table/material behavior: `Python/tests/test_structural.py`, `Python/tests/test_materials_tables_edges.py`
- Detailing logic: `Python/tests/test_detailing.py`
- ETABS/CSV/JSON integration: `Python/tests/test_excel_integration.py`
- DXF generation: `Python/tests/test_dxf_export_smoke.py` (and future deeper DXF tests)

---

## 7) Definition of “good” (target state)

- CI enforces a stable baseline (coverage gate + full test pass).
- Deterministic tests for boundary conditions and known failure modes.
- Clear separation:
  - core calculation tests (fast, numeric)
  - I/O tests (tmp_path, minimal fixtures)
  - DXF tests (structural, not brittle)
- A parity harness exists for shared vectors (Python ↔ VBA) as a longer-term safety net.
