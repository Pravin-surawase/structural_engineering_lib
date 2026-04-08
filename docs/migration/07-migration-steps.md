# Step-by-Step Migration Checklist

**Type:** Guide
**Version:** 2.0
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-04-07
**Last Updated:** 2026-04-08

## Version History

- **v2.0 (2026-04-08):** Restructured phases for consistency with multi-code scope, added rollback plan and success criteria per phase, fixed phase numbering
- **v1.0 (2026-04-07):** Initial 4-phase migration plan (IS 456 only)

---

## Overview

| Phase | Duration | Focus | Success Gate |
|-------|----------|-------|-------------|
| **Phase 0** | Week 0 | Pre-migration setup, naming, benchmarks | Repo created, tach.toml configured, name chosen |
| **Phase 1** | Weeks 1–2 | Extract IS 456 core (123 functions → new structure) | `pip install <pkg>` works, all IS 456 tests pass |
| **Phase 2** | Weeks 3–4 | Validate & test | 95% coverage, SP:16 ±0.1%, type checks pass |
| **Phase 3** | Week 5 | Release IS 456 v1.0 to PyPI | Package live, deprecation notice on old package |
| **Phase 4** | Weeks 6+ | Multi-code expansion (ACI 318, EC2) | 564 total functions, cross-code comparison works |

---

## Phase 0 — Pre-Migration (Week 0)

### Tasks

- [ ] **Choose package name** — ⚠️ BLOCKED: `rcdesign` is taken on PyPI. See [08-naming-and-accounts.md](08-naming-and-accounts.md)
- [ ] Set up new GitHub repository with MIT license, README, .gitignore (Python)
- [ ] Initialize with `uv init <name> --lib` (creates src/ layout)
- [ ] Configure `pyproject.toml` — see [03-library-repo-blueprint.md](03-library-repo-blueprint.md)
- [ ] Set up `tach.toml` for 5-layer architecture enforcement:
  ```toml
  [[modules]]
  path = "core"
  depends_on = []

  [[modules]]
  path = "common"
  depends_on = ["core"]

  [[modules]]
  path = "codes"
  depends_on = ["core", "common"]

  [[modules]]
  path = "services"
  depends_on = ["core", "common", "codes"]
  ```
- [ ] Set up CI skeleton: pytest, ruff, basedpyright, tach check
- [ ] Set up PyPI account and configure Trusted Publisher
- [ ] Set up TestPyPI account and configure Trusted Publisher
- [ ] Set up Codecov account and connect to GitHub
- [ ] Create SP:16 benchmark golden vector test suite (Charts 1–62)
- [ ] Create Pillai & Menon textbook test suite
- [ ] Run full test suite in current monorepo — ensure 100% pass before migration
- [ ] Document all public API signatures with `discover_api_signatures.py`
- [ ] Review and finalize function classification (see [10-function-classification.md](10-function-classification.md))

### Rollback Plan

- **Trigger:** Naming blocked, tooling doesn't work, or team decides against split
- **Action:** Delete the new repo. Monorepo continues unchanged.
- **Impact:** Zero — no changes to existing package or users

### Success Criteria

| Criterion | Target |
|-----------|--------|
| Package name decided | ✅ Name available on PyPI and importable |
| Repo initialized | ✅ `uv sync --dev` resolves cleanly |
| CI skeleton green | ✅ Empty test suite passes |
| tach.toml configured | ✅ `tach check` passes with 5-layer rules |
| Benchmark suite ready | ✅ SP:16 Charts 1–62 encoded as JSON golden vectors |

---

## Phase 1 — Extract IS 456 Core (Weeks 1–2)

### Tasks

#### 1a: Core types (no dependencies)

- [ ] Copy `core/types.py` → `src/<pkg>/core/types.py`
- [ ] Copy `core/constants.py` → `src/<pkg>/core/constants.py`
- [ ] Copy `core/materials.py` → `src/<pkg>/core/materials.py`
- [ ] Copy `core/sections.py` → `src/<pkg>/core/sections.py`
- [ ] Copy `core/reinforcement.py` → `src/<pkg>/core/reinforcement.py`
- [ ] Copy `core/errors.py` → `src/<pkg>/core/errors.py`
- [ ] Copy `core/numerics.py` → `src/<pkg>/core/numerics.py`
- [ ] Copy `core/validation.py` → `src/<pkg>/core/validation.py`
- [ ] Refactor imports to new package structure
- [ ] Verify: `uv run pytest tests/test_core.py -v`

#### 1b: Common math (depends on core)

- [ ] Copy `common/stress_blocks.py` → `src/<pkg>/common/stress_block.py`
- [ ] Copy `common/tables.py` → `src/<pkg>/common/tables.py`
- [ ] Copy `common/reinforcement.py` → `src/<pkg>/common/reinforcement.py`
- [ ] Copy BBS math (cut lengths, shape codes only) → `src/<pkg>/common/bbs.py`
- [ ] Copy `common/detailing.py` → `src/<pkg>/common/detailing.py`
- [ ] Refactor imports
- [ ] Verify: `uv run pytest tests/test_common.py -v`

#### 1c: Beam math (depends on core + common)

- [ ] Copy beam `flexure.py` (8 functions)
- [ ] Copy beam `shear.py` (5 functions)
- [ ] Copy beam `torsion.py` (6 functions)
- [ ] Copy beam `serviceability.py`
- [ ] Copy beam `detailing.py`
- [ ] Refactor imports, remove `_is456` suffix from function names
- [ ] Verify: `uv run pytest tests/test_beam_*.py -v`

#### 1d: Column math (depends on core + common)

- [ ] Copy column `axial.py` (classify, effective_length, axial_capacity, min_eccentricity)
- [ ] Copy column `uniaxial.py` (pm_interaction_curve, design_short_column_uniaxial)
- [ ] Copy column `biaxial.py` (biaxial_bending_check)
- [ ] Copy column `slenderness.py` / `long_column.py` (additional_moment, design_long_column)
- [ ] Copy column `helical.py`, `detailing.py`, `ductile.py`
- [ ] Refactor imports
- [ ] Verify: `uv run pytest tests/test_column_*.py -v`

#### 1e: Footing math (depends on core + common)

- [ ] Copy footing `bearing.py`, `flexure.py`, `one_way_shear.py`, `punching_shear.py`
- [ ] Refactor imports
- [ ] Verify: `uv run pytest tests/test_footing.py -v`

#### 1f: Orchestration API + clean public surface

- [ ] Copy high-level design functions: `design_beam()`, `design_column()`
- [ ] Copy detail functions: `detail_beam()`, `detail_column()`
- [ ] Copy check functions: `check_beam()`, `check_deflection()`, `check_crack_width()`
- [ ] Copy batch functions: `design_beams()`, `design_beams_iter()`
- [ ] Create `src/<pkg>/__init__.py` with clean `__all__` (~40 public functions)
- [ ] Drop `_is456` suffix from all function names
- [ ] Verify: `from <pkg> import design_beam` works
- [ ] Goal: `pip install <package>` works with IS 456 beams + columns + footings

### Rollback Plan

- **Trigger:** Code extraction breaks imports, tests fail, or coverage drops below 90%
- **Action:** Library repo exists but monorepo remains primary. Revert any dependency pinning.
- **Impact:** Low — new repo is abandoned, monorepo unaffected

### Success Criteria

| Criterion | Target |
|-----------|--------|
| 123 functions extracted | ✅ All 73 CORE + 35 ORCH + BBS math |
| Import structure correct | ✅ `tach check` passes |
| Tests pass | ✅ `uv run pytest -v` — all green |
| Package installable | ✅ `pip install .` works in clean venv |
| `_is456` suffixes removed | ✅ Clean API names |

---

## Phase 2 — Validate & Test (Weeks 3–4)

### Tasks

- [ ] Run full test suite against new structure: `uv run pytest tests/ -v`
- [ ] SP:16 benchmarks pass at ±0.1% (62 test cases)
- [ ] Pillai & Menon textbook benchmarks pass at ±1% (~30 test cases)
- [ ] Hypothesis property-based tests pass (monotonicity, dimensional consistency)
- [ ] Architecture boundaries enforced:
  - [ ] `tach check` — 5-layer import direction
  - [ ] `import-linter` — no upward imports
- [ ] Type checking passes:
  - [ ] `basedpyright --strict src/` — zero errors
  - [ ] `mypy --strict src/` — zero errors
- [ ] Linting passes:
  - [ ] `ruff check src/` — zero issues
  - [ ] `ruff format --check src/` — no formatting violations
- [ ] Coverage: 95% branch minimum: `uv run pytest --cov --cov-report=term-missing`
- [ ] Package size < 500KB
- [ ] `py.typed` marker is in built wheel
- [ ] CI completes in < 60 seconds
- [ ] Publish to TestPyPI: `uv run pytest` on installed TestPyPI package

### Rollback Plan

- **Trigger:** Coverage below 95%, SP:16 benchmarks fail, type errors can't be resolved
- **Action:** Library stays in development. Fix issues and re-run Phase 2.
- **Impact:** Low — no public release, can retry

### Success Criteria

| Criterion | Target |
|-----------|--------|
| SP:16 accuracy | ±0.1% on all 62 charts |
| Textbook accuracy | ±1% on ~30 examples |
| Branch coverage | ≥ 95% |
| Type check | Zero errors (basedpyright + mypy strict) |
| Lint | Zero issues (ruff) |
| Architecture | `tach check` passes |
| CI time | < 60 seconds |
| Package size | < 500KB |
| TestPyPI install | `pip install` + `import` + tests pass |

---

## Phase 3 — Release IS 456 v1.0 (Week 5)

### Tasks

- [ ] Update version to 1.0.0 (or let hatch-vcs from git tag)
- [ ] Write CHANGELOG.md entry for v1.0.0
- [ ] **TestPyPI dry run first:**
  - [ ] Publish pre-release to TestPyPI
  - [ ] Install from TestPyPI in clean venv
  - [ ] Run full test suite against installed package
  - [ ] Verify `py.typed` marker in wheel
- [ ] **PyPI release:**
  - [ ] Create GitHub Release with tag `v1.0.0`
  - [ ] CI auto-publishes via Trusted Publishers (OIDC — no secrets)
  - [ ] Sigstore signing for supply chain security
  - [ ] Verify: `pip install <package>` works globally
- [ ] **Documentation:**
  - [ ] API docs live on MkDocs (mkdocstrings auto-generated)
  - [ ] README with badges, examples, benchmark results
  - [ ] Theory pages for derivations and assumptions
- [ ] **Deprecation notice on old package:**
  - [ ] Final release of `structural-lib-is456` with `DeprecationWarning`
  - [ ] PyPI description updated with migration notice
  - [ ] Keep `structural-lib-is456` on PyPI indefinitely (don't delete)
- [ ] Announce on relevant forums/channels

### Rollback Plan

- **Trigger:** PyPI publish fails, or critical bug found post-release
- **Action:** Yank the PyPI release. Fix and re-release as v1.0.1.
- **Impact:** Medium — users may have installed broken version, but yank prevents new installs

### Success Criteria

| Criterion | Target |
|-----------|--------|
| `pip install <package>` | ✅ Works in <5 seconds |
| `import <package>` | ✅ Zero config, zero warnings |
| Docs live | ✅ MkDocs deployed to ReadTheDocs/GitHub Pages |
| Old package deprecated | ✅ DeprecationWarning in `structural-lib-is456` |
| Sigstore signed | ✅ Supply chain attestation present |
| README examples runnable | ✅ Verified in CI |

---

## Phase 4 — Multi-Code Expansion (Weeks 6+)

> **New in v2.0** — This phase was not in v1.0 of the migration plan.

### Phase 4a: ACI 318 Beam Module (Weeks 6–8)

- [ ] Create `src/<pkg>/codes/aci318/` directory structure
- [ ] Implement ACI 318-19 beam flexure (rectangular stress block, φMn)
- [ ] Implement ACI 318-19 beam shear (Vc, Vs, stirrup design)
- [ ] Implement ACI 318-19 beam torsion
- [ ] Add PCA Notes benchmark suite (~30 test cases, ±0.1%)
- [ ] Wire into multi-code API: `design_beam(code="ACI318")`
- [ ] ~50 new functions

### Phase 4b: EC2 Beam Module (Weeks 9–11)

- [ ] Create `src/<pkg>/codes/ec2/` directory structure
- [ ] Implement EC2 beam flexure (parabolic-rectangular stress block)
- [ ] Implement EC2 beam shear (variable angle truss model)
- [ ] Implement EC2 beam torsion
- [ ] Add fib Model Code benchmark suite (~30 test cases, ±0.1%)
- [ ] Wire into multi-code API: `design_beam(code="EC2")`
- [ ] ~50 new functions

### Phase 4c: Multi-Code Comparison API (Week 12)

- [ ] Implement `compare_beam_design()` — run same inputs through IS456 + ACI318 + EC2
- [ ] Implement grade mapping lookup (M25 → C25/30 → f'c=25 MPa)
- [ ] Add comparison result model with side-by-side output
- [ ] Add app API endpoints: `POST /api/v2/compare/beam`, `GET /api/v2/codes`

### Phase 4d: Expand to Columns, Slabs, Footings (Weeks 13+)

- [ ] ACI 318 column design (axial, uniaxial, biaxial)
- [ ] EC2 column design
- [ ] IS 456 slab design (one-way + two-way — Tier 1 gap)
- [ ] IS 456 load combinations (Table 18 — Tier 1 gap)
- [ ] ACI 318 slab design
- [ ] EC2 slab design
- [ ] Target: 564 total functions across all codes

### Rollback Plan

- **Trigger:** Multi-code architecture doesn't work with Protocol pattern, or quality drops
- **Action:** Revert to IS 456-only library. Phase 4 work stays on a branch.
- **Impact:** Low — IS 456 v1.0 is already released and stable

### Success Criteria

| Criterion | Target |
|-----------|--------|
| ACI 318 beam functions | ~50 functions, PCA Notes ±0.1% |
| EC2 beam functions | ~50 functions, fib Model Code ±0.1% |
| Cross-code comparison | `compare_beam_design()` returns consistent results |
| Total functions | 564 across IS 456 + ACI 318 + EC2 |
| Architecture | `tach check` passes with all 3 code modules |
| Grade mapping | All concrete/steel equivalences verified |

---

## Backward Compatibility

### For `structural-lib-is456` Users
1. Final release of `structural-lib-is456` with deprecation warning in `__init__.py`:
   ```python
   import warnings
   warnings.warn(
       "structural-lib-is456 is deprecated. Use 'pip install rcdesign' instead. "
       "See https://github.com/<org>/rcdesign for migration guide.",
       DeprecationWarning, stacklevel=2
   )
   ```
2. README updated to redirect to `rcdesign`
3. PyPI description updated with migration notice
4. Keep `structural-lib-is456` on PyPI indefinitely (don't delete)

### API Compatibility
- All 73 CORE functions maintain same signatures
- All 35 ORCHESTRATION functions maintain same signatures
- Import path changes: `from structural_lib import X` → `from rcdesign import X`
- Provide `structural_lib` compatibility shim for 6 months (optional)

### Sequencing Decision
- **Slabs + Load Combinations:** Implemented in NEW repo post-migration (not pre-migration)
- **Rationale:** Clean repo is the right place for new code. Migration timeline stays at 6 weeks.
