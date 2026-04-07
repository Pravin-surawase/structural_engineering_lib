# Step-by-Step Migration Checklist

**Type:** Guide
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-04-07
**Last Updated:** 2026-04-08

---

## Overview

| Phase | Duration | Focus |
|-------|----------|-------|
| **Pre-Migration** | Week 0 | Setup accounts, finalize naming, prepare benchmarks |
| **Phase 1** | Weeks 1–2 | Library extraction — create repo, migrate 73 CORE + 35 ORCH functions |
| **Phase 2** | Weeks 3–4 | App extraction — create repo, migrate 30 APP functions + FastAPI + React |
| **Phase 3** | Week 5 | Validation — full test suite, SP:16 benchmarks, integration tests |
| **Phase 4** | Week 6 | Release — publish to PyPI, deploy app, cleanup |

---

## Pre-Migration (Week 0)

### Naming & Accounts

- [ ] Choose library name — check PyPI availability with `pip index versions <name>`
- [ ] Set up PyPI account and configure Trusted Publisher
- [ ] Set up TestPyPI account and configure Trusted Publisher
- [ ] Set up Codecov account and connect to GitHub
- [ ] Set up ReadTheDocs account and import repo
- [ ] Decide on GitHub organization (optional)

### Preparation in Current Monorepo

- [ ] Review and finalize function classification (see [10-function-classification.md](10-function-classification.md))
- [ ] Create SP:16 benchmark golden vector test suite (Charts 1–62)
- [ ] Run full test suite — ensure everything passes before migration
- [ ] Document all public API signatures with `discover_api_signatures.py`
- [ ] Export current test coverage baseline
- [ ] Archive stale docs and clean up `docs/_archive/`

---

## Phase 1: Library Extraction (Weeks 1–2)

### Step 1: Create New Repository

- [ ] Create GitHub repo with MIT license, README, .gitignore (Python)
- [ ] Enable branch protection: require PR reviews, require CI status checks
- [ ] Enable Dependabot security alerts + dependency updates
- [ ] Enable secret scanning
- [ ] Add repository topics: `structural-engineering`, `is456`, `reinforced-concrete`, `python-library`
- [ ] Add CODEOWNERS file (owner auto-reviews all PRs)
- [ ] Create `pypi` environment in repo settings for releases

### Step 2: Set Up Project Structure

- [ ] Initialize with `uv init <name> --lib` (creates src/ layout)
- [ ] Create `src/<package>/` folder structure per [03-library-repo-blueprint.md](03-library-repo-blueprint.md)
- [ ] Add `py.typed` marker (PEP 561)
- [ ] Configure `pyproject.toml` — see complete template in blueprint
- [ ] Add `.pre-commit-config.yaml` — see [06-ci-cd-and-tooling.md](06-ci-cd-and-tooling.md)
- [ ] Add `.editorconfig` for cross-editor consistency
- [ ] Add `.python-version` file (`3.12`)
- [ ] Run `uv sync --dev` to verify dependencies resolve

### Step 3: Set Up CI/CD

- [ ] Create `.github/workflows/ci.yml` — test matrix (3 Python × 3 OS)
- [ ] Create `.github/workflows/publish.yml` — Trusted Publishers (OIDC)
- [ ] Configure PyPI Trusted Publisher (repo → workflow → environment)
- [ ] Configure TestPyPI Trusted Publisher
- [ ] Set up Codecov with `CODECOV_TOKEN` in repo secrets
- [ ] Verify CI runs green with empty src/ and a trivial test

### Step 4: Set Up AI Agents

- [ ] Create `.github/copilot-instructions.md` — global instructions
- [ ] Create 4 agent files: `coder.agent.md`, `reviewer.agent.md`, `tester.agent.md`, `math-verifier.agent.md`
- [ ] Create 3 instruction files: `python.instructions.md`, `tests.instructions.md`, `docs.instructions.md`
- [ ] Create 4 prompt files: `new-feature.prompt.md`, `fix-bug.prompt.md`, `add-clause.prompt.md`, `release.prompt.md`
- [ ] Create 2 skill files: `test-pipeline/SKILL.md`, `is456-verify/SKILL.md`
- [ ] Create `AGENTS.md` — cross-agent instructions

### Step 5: Migrate Core Functions (73 CORE)

Migration order: dependencies first, then dependents.

#### 5a: Core types (no dependencies)

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

#### 5b: Common math (depends on core)

- [ ] Copy `common/stress_blocks.py` → `src/<pkg>/common/stress_block.py`
- [ ] Copy `common/tables.py` → `src/<pkg>/common/tables.py`
- [ ] Copy `common/reinforcement.py` → `src/<pkg>/common/reinforcement.py`
- [ ] Copy BBS math (cut lengths, shape codes only) → `src/<pkg>/common/bbs.py`
- [ ] Refactor imports
- [ ] Verify: `uv run pytest tests/test_common.py -v`

#### 5c: Beam math (depends on core + common)

- [ ] Copy beam `flexure.py` (8 functions)
- [ ] Copy beam `shear.py` (5 functions)
- [ ] Copy beam `torsion.py` (6 functions)
- [ ] Copy beam `serviceability.py`
- [ ] Copy beam `detailing.py`
- [ ] Refactor imports, remove `_is456` suffix from function names
- [ ] Verify: `uv run pytest tests/test_beam_*.py -v`

#### 5d: Column math (depends on core + common)

- [ ] Copy column `axial.py` (classify, effective_length, axial_capacity, min_eccentricity)
- [ ] Copy column `uniaxial.py` (pm_interaction_curve, design_short_column_uniaxial)
- [ ] Copy column `biaxial.py` (biaxial_bending_check)
- [ ] Copy column `slenderness.py` / `long_column.py` (additional_moment, design_long_column)
- [ ] Copy column `helical.py`, `detailing.py`, `ductile.py`
- [ ] Refactor imports
- [ ] Verify: `uv run pytest tests/test_column_*.py -v`

#### 5e: Footing math (depends on core + common)

- [ ] Copy footing `bearing.py`, `flexure.py`, `one_way_shear.py`, `punching_shear.py`
- [ ] Refactor imports
- [ ] Verify: `uv run pytest tests/test_footing.py -v`

#### 5f: Clean public API

- [ ] Create `src/<pkg>/__init__.py` with clean `__all__` (~40 public functions)
- [ ] Drop `_is456` suffix from all function names
- [ ] Verify: `from <pkg> import design_beam` works

### Step 6: Migrate Tests

- [ ] Copy all existing unit tests for CORE functions
- [ ] Adapt imports to new package structure
- [ ] Create SP:16 benchmark suite (`test_benchmarks_sp16.py`)
- [ ] Create textbook benchmark suite (`test_benchmarks_textbook.py`)
- [ ] Add Hypothesis property-based tests (`test_property_based.py`)
- [ ] Add edge case tests (`test_edge_cases.py`)
- [ ] Verify 95%+ branch coverage: `uv run pytest --cov --cov-report=term-missing`
- [ ] Verify all SP:16 benchmarks pass at ±0.1%

### Step 7: Migrate Orchestration Functions (35 ORCH)

- [ ] Copy high-level design functions: `design_beam()`, `design_column()`
- [ ] Copy detail functions: `detail_beam()`, `detail_column()`
- [ ] Copy check functions: `check_beam()`, `check_deflection()`, `check_crack_width()`
- [ ] Copy batch functions: `design_beams()`, `design_beams_iter()`
- [ ] Copy combined workflows: `design_and_detail_beam()`
- [ ] Wire into clean API in `__init__.py`
- [ ] Verify: `uv run pytest -v` — all tests pass

---

## Phase 2: App Extraction (Weeks 3–4)

### Step 8: Create App Repository

- [ ] Create GitHub repo: `rcdesign-app` (or chosen name)
- [ ] Set up monorepo structure: `backend/` + `frontend/`
- [ ] Configure `backend/pyproject.toml` with dependency on library: `rcdesign>=1.0,<2.0`
- [ ] Configure Docker: `docker-compose.yml`, `docker-compose.dev.yml`
- [ ] Create Dockerfiles: `Dockerfile.backend`, `Dockerfile.frontend`

### Step 9: Migrate APP Functions (30 APP)

- [ ] Move `services/adapters.py` (71KB) → `backend/app/services/adapters.py`
- [ ] Move `visualization/geometry_3d.py` → `backend/app/services/visualization.py`
- [ ] Move `insights/` (9 files) → `backend/app/services/insights/`
- [ ] Move `reports/` → `backend/app/services/reports.py`
- [ ] Move `services/dxf_export.py` → `backend/app/services/dxf_export.py`
- [ ] Move BBS export functions → `backend/app/services/bbs_export.py`
- [ ] Move `services/costing.py` → `backend/app/services/optimization.py`
- [ ] Move streaming/batch → `backend/app/services/`
- [ ] Update all imports to use installed library: `from rcdesign import design_beam`

### Step 10: Migrate FastAPI

- [ ] Copy 13 routers → `backend/app/routers/`
- [ ] Copy Pydantic models → `backend/app/models/`
- [ ] Copy `main.py`, `config.py`, auth, error handling
- [ ] Update imports: `from rcdesign import design_beam` (not local import)
- [ ] Verify all 60 endpoints respond: `uv run pytest backend/tests/ -v`

### Step 11: Migrate React

- [ ] Copy `react_app/` → `frontend/`
- [ ] Update API base URL configuration
- [ ] Verify build: `cd frontend && npm run build`
- [ ] Verify tests: `cd frontend && npx vitest run`
- [ ] Test all hooks and components against backend

---

## Phase 3: Validation (Week 5)

### Step 12: Library Validation

- [ ] Publish to TestPyPI: create a pre-release tag
- [ ] Install from TestPyPI: `pip install --index-url https://test.pypi.org/simple/ rcdesign`
- [ ] Run full test suite against installed package (not source)
- [ ] SP:16 benchmarks: verify ±0.1% accuracy
- [ ] `mypy --strict src/`: zero errors
- [ ] `ruff check src/`: zero issues
- [ ] CI completes in < 60 seconds
- [ ] Package size < 500KB
- [ ] Verify `py.typed` marker is in wheel

### Step 13: App Validation

- [ ] `docker compose up --build` — all containers start
- [ ] Verify all 60 API endpoints respond at `localhost:8000/docs`
- [ ] React build succeeds and serves at `localhost:5173` (dev) or via Docker
- [ ] App imports library from PyPI (not local path)
- [ ] All user workflows work end-to-end (import CSV → design → export)

### Step 14: Integration Test

- [ ] App uses library via `pip install rcdesign` (not local path or editable install)
- [ ] All user workflows work end-to-end
- [ ] Performance regression check with `pytest-benchmark`
- [ ] Verify library upgrade path: `pip install rcdesign==1.0.1` doesn't break app

---

## Phase 4: Release (Week 6)

### Step 15: Library Release

- [ ] Update version to 1.0.0 in `_version.py` (or let hatch-vcs from git tag)
- [ ] Write CHANGELOG.md entry for v1.0.0
- [ ] Create GitHub Release with tag `v1.0.0`
- [ ] CI auto-publishes to PyPI via Trusted Publishers
- [ ] Verify: `pip install rcdesign` works globally
- [ ] Documentation live on ReadTheDocs
- [ ] Announce on relevant forums/channels

### Step 16: App Release

- [ ] Docker images built and pushed to registry
- [ ] README updated with setup instructions
- [ ] Demo deployment (optional — Render, Fly.io, Railway)
- [ ] Verify fresh deploy works from scratch

### Step 17: Cleanup

- [ ] Archive old monorepo or add deprecation notice to README
- [ ] Update all external references (docs, links, citations)
- [ ] Final documentation pass — verify all cross-references
- [ ] Close migration-related GitHub issues
- [ ] Retrospective: what went well, what to improve

---

## Rollback Plan

### Phase 1 Failure (PREPARE)
- **Trigger:** Repository setup fails, tooling doesn't work, or team decides against split
- **Action:** Delete the new `rcdesign` repo. Monorepo continues unchanged.
- **Impact:** Zero — no changes to existing package or users

### Phase 2 Failure (EXTRACT)
- **Trigger:** Code extraction breaks imports, tests fail, or coverage drops below 90%
- **Action:** Library repo exists but monorepo remains primary. Revert any dependency pinning changes.
- **Impact:** Low — new repo is abandoned, monorepo unaffected

### Phase 3 Failure (BUILD)
- **Trigger:** CI/CD setup fails, Trusted Publishers not working, or packaging issues
- **Action:** Library repo stays in development. Publish to TestPyPI only (not PyPI).
- **Impact:** Low — no public release, can retry

### Phase 4 Failure (SHIP)
- **Trigger:** PyPI publish fails, or critical bug found post-release
- **Action:** Yank the PyPI release (`pip install rcdesign==X.Y.Z` still works but won't auto-install). Fix and re-release.
- **Impact:** Medium — users may have installed broken version

### General Rollback Principles
1. **Monorepo is always the fallback** — it continues working regardless of new repo status
2. **No destructive changes to monorepo** until Phase 4 is confirmed successful
3. **TestPyPI before PyPI** — always verify install + import + test on TestPyPI first
4. **Git history preserved** — use `git filter-branch` or `git subtree split`, never manual copy

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
