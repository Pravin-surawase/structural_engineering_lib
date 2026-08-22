---
owner: Main Agent
status: active
last_updated: 2026-08-23
doc_type: guide
complexity: intermediate
tags: []
---

# Testing Strategy & Setup (Python-first, VBA parity aware)

**Type:** Guide
**Audience:** Developers
**Status:** Production Ready
**Importance:** High
**Created:** 2025-01-01
**Last Updated:** 2026-08-23

---

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

**Fast checks before commit:**

- `./run.sh verification plan` shows the whole candidate's explicit domains.
- `./run.sh check --changed` runs the mapped repository checks; an unknown path
  or failed Git query expands to every domain.
- `./run.sh test --changed` keeps focused Python/FastAPI mappings where proved,
  runs the React/Excel suites for those domains, and falls back to complete
  product suites when test ownership is unclear.
- `./run.sh check --quick` remains the required pre-commit gate. Exact prior
  PASS receipts are reused only when command, runtime, dependency set, and
  current input bytes have the same content address.

**How to run with coverage:**
- From `Python/`: `python -m pytest --cov=structural_lib --cov-report=term-missing --cov-report=xml`

**How to run the CI-equivalent check locally (includes coverage gate):**
- From `Python/`: `python -m pytest --cov=structural_lib --cov-branch --cov-report=term-missing --cov-report=xml --cov-fail-under=85`

### CI (GitHub Actions)

Workflows: `.github/workflows/fast-checks.yml` and
`.github/workflows/nightly.yml`

- Pull requests receive path-aware format, lint, type, contract, focused test,
  frontend, API, and repository checks under the required `PR Gate`.
- Local and hosted scheduling load `scripts/verification-manifest.json`; the
  workflow does not maintain a second path-filter list. Applicable jobs may
  reuse an exact PASS receipt only after their current runtime/dependencies are
  resolved and fingerprinted. Cache misses, malformed receipts, and identity
  changes execute the job normally.
- Weekly/manual verification runs the full Ubuntu Python/FastAPI/React suite,
  branch coverage gate, clean-wheel/CLI verification, dependency audits, and
  Docker health checks.
- macOS and Windows smoke checks are available as an explicit manual option.

**What this gives us:**
- Minimum-version PR confidence plus optional cross-platform smoke evidence
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

## 7) Property-Based Testing (Hypothesis)

Property-based testing uses the [Hypothesis](https://hypothesis.readthedocs.io/) library to automatically generate test inputs and discover edge cases that unit tests might miss.

### Location

- Strategies: `Python/tests/property/strategies.py`
- Tests: `Python/tests/property/test_*_hypothesis.py`
- Profile config: `Python/tests/conftest.py`

### Available Profiles

| Profile | Examples | Use Case |
|---------|----------|----------|
| `dev` | 25 | Fast local development |
| `default` | 100 | Standard test runs |
| `ci` | 200 | CI runs (deterministic) |
| `exhaustive` | 1000 | Thorough testing before release |

### Running Property Tests

```bash
# Fast development run (25 examples per test)
python -m pytest Python/tests/property/ --hypothesis-profile=dev

# Standard run (100 examples)
python -m pytest Python/tests/property/

# CI run (200 examples, deterministic)
python -m pytest Python/tests/property/ --hypothesis-profile=ci

# Thorough run (1000 examples)
python -m pytest Python/tests/property/ --hypothesis-profile=exhaustive
```

### Reusable Strategies

The `strategies.py` module provides domain-specific strategies:

| Strategy | Description |
|----------|-------------|
| `concrete_grade()` | Valid fck values (20-70 N/mm²) |
| `steel_grade()` | Valid fy values (250-550 N/mm²) |
| `beam_section()` | Complete beam geometry (b, d, D) |
| `flexure_inputs()` | All inputs for flexure design |
| `shear_inputs()` | All inputs for shear design |
| `ductile_inputs()` | All inputs for ductile beam check |

### What Property Tests Cover

1. **Flexure module (13 tests)**
   - `calculate_mu_lim`: positivity, scaling with dimensions
   - `calculate_ast_required`: area always positive
   - `design_singly_reinforced`: valid result structure

2. **Shear module (13 tests)**
   - `calculate_tv`: stress bounds
   - `get_tc_from_table19`: grade ordering, interpolation
   - `get_tc_max`: value ordering
   - `design_shear_reinforcement`: stirrup spacing valid

3. **Ductile detailing (17 tests)**
   - `check_ductile_beam_geometry`: b/D ratio limits
   - `get_min_steel_percentage`: percentage bounds
   - `get_confinement_zone_length`: IS 13920 compliance
   - `check_beam_ductility`: integrated checks

### Adding New Property Tests

1. **Use existing strategies** from `strategies.py`:
   ```python
   from tests.property.strategies import flexure_inputs

   @given(inputs=flexure_inputs())
   def test_my_property(self, inputs: dict) -> None:
       result = my_function(**inputs)
       assert invariant_holds(result)
   ```

2. **Create composite strategies** for complex inputs:
   ```python
   @st.composite
   def my_complex_input(draw):
       fck = draw(concrete_grade())
       b = draw(st.integers(200, 500))
       return {"fck": fck, "b": b}
   ```

3. **Use `assume()`** for preconditions:
   ```python
   @given(b=st.integers(100, 1000), d=st.integers(200, 800))
   def test_with_precondition(self, b: int, d: int) -> None:
       assume(d >= b)  # Skip invalid inputs
       result = function(b, d)
   ```

### Key Findings from Property Testing

Hypothesis discovered several edge cases:
- High fck (70) + low fy (250) can exceed 4% max steel even for Mu < Mu_lim
- Narrow beams (100-150mm) stress the geometry validation logic
- Shear stress limits are sensitive to concrete grade transitions

---

## 8) Definition of "good" (target state)

- CI enforces a stable baseline (coverage gate + full test pass).
- Deterministic tests for boundary conditions and known failure modes.
- Clear separation:
  - core calculation tests (fast, numeric)
  - I/O tests (tmp_path, minimal fixtures)
  - DXF tests (structural, not brittle)
- A parity harness exists for shared vectors (Python ↔ VBA) as a longer-term safety net.
