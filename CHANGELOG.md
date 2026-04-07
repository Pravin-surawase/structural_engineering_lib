# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.21.6] — 2026-04-07

### Fixed
- **ETABS job generator:** Units corrected from `"SI-mm"` to `"IS456"` (EXT-P1-1)
- **ETABS batch processing:** Group by `(story, beam_id)` instead of just `beam_id` — prevents cross-story beam collision (EXT-P1-2)
- **Geometry merge:** Key by `(story, label)` with fallback — prevents geometry overwrite when multiple stories share label names (EXT-P1-3)
- **SmartDesigner CLI:** Now uses `design_single_beam()` returning correct `BeamDesignOutput` type (EXT-P1-4)
- **Report templates:** `.j2` Jinja2 templates now included in wheel package data via `pyproject.toml` (EXT-P1-5)
- **README batch example:** Corrected `parse_file()` → `load_combined()` (non-existent function reference) (EXT-P2-1)
- **`bbs.py` import path:** Updated from deprecated shim to canonical `codes/is456/beam/detailing` (EXT-P2-2)
- **README version:** Updated from `0.21.3` to `0.21.5` (EXT-P3-1)

### Added
- `check_code("IS456")` — self-validation function for IS 456 code implementation (TASK-724)
- `show_versions()` — diagnostic utility reporting library, Python, platform, and dependency versions (TASK-725)
- OpenAPI baseline drift check script (`scripts/check_openapi_drift.py`) and CI step (TASK-726)

### Documentation
- Added `Limitations:` sections to 22 IS 456 function docstrings across 12 modules — beam flexure, shear, torsion, serviceability, detailing; column axial, uniaxial, detailing; footing bearing, flexure, one-way shear, punching shear (TASK-727)

## [0.21.5] — 2026-04-06

Test Coverage & Regression Prevention release.

### Added
- **Golden vector baselines (TASK-720):** 42+ regression tests with `@pytest.mark.golden` — 9 beam (flexure, torsion, serviceability), 20 column (effective length, classification, axial, uniaxial, biaxial, P-M, helical, long column), 13 footing (bearing, flexure, shear, punching)
- **Contract tests (TASK-721):** 18 API surface stability tests with `@pytest.mark.contract` — freezes parameter names and return types for column, footing, torsion APIs
- **conftest.py golden fixture (TASK-722):** Session-scoped `golden_vectors` fixture loading SP:16 reference data
- **CI golden gate (TASK-723):** Dedicated `pytest -m golden` step in GitHub Actions `python-tests.yml` (Ubuntu + Python 3.12)
- **Report/3D edge case tests (TASK-520):** 71 new tests — 29 report edge cases (XSS escaping, fallback HTML, template filters) + 42 visualization edge cases (minimum dimensions, dense rebar, stirrup positions, serialization)
- Coverage boost: 19 targeted tests pushing `codes/is456/` to 99% branch coverage
- `unwrapResponse<T>()` helper in `react_app/src/api/client.ts` — standard contract for FastAPI response unwrapping
- 3 contract tests for `unwrapResponse` in `endpoints.test.ts`

### Fixed
- Added `@clause("34.1")` to `size_footing()` — resolved footing clause coverage gap
- **Response envelope mismatch** — React client now unwraps FastAPI's `{success, data}` wrapper via `unwrapResponse()` across all 16 API fetch calls. Fixed Import page crash (`beams.map` undefined), Design page crash (`result.flexure` undefined), and silent data failures on geometry/insights/rebar pages.
- Fixed `new URL()` crash on relative paths in `useCSVImport.ts` (dev mode)
- Fixed 3 wrong type names in `useInsights.ts`

## [0.21.4] — 2026-04-05

### Security
- Replaced 49 bare `except Exception` blocks with specific exception types across 11 FastAPI routers (ARCH-NEW-09)
- WCAG AA form accessibility: aria-required, aria-invalid, aria-describedby, fieldset+legend in 4 components (FE-NEW-02)

### Added
- Column API: 6 additional column functions exported at top-level (`design_column_is456`, `detail_column_is456`, etc.) + `EndCondition` enum
- Clause DB: Added 7 missing IS 456 clause/annex/figure references
- 18 `@clause` decorators added to footing + serviceability functions (IS-NEW-01/02)
- `clause_refs` field added to FlexureResult, ShearResult, TorsionResult, ComplianceCaseResult (UX-05)
- 62 new FastAPI router tests across 6 test files, 7 routers covered (T-NEW-08)
- Standardized all API responses with `success_response()`/`error_response()` wrapper across 9 routers (API-NEW-01)
- Split `services/api.py` god module: `beam_api.py` (1895L), `column_api.py` (1387L), `common_api.py` (230L) (ARCH-NEW-12)
- CI failure delegation protocol added to ops agent instructions

### Fixed
- DXF CLI: Fixed `KeyError: 'story'` when processing `build_detailing_input()` output
- Eliminated 16 warning messages on package import by fixing clause database loading
- README: Corrected `compute_dxf` and `optimize_beam_cost` example signatures
- Sdist: Fixed packaging to exclude test files properly (global-exclude/prune in MANIFEST.in)
- Replaced 17 MagicMock instances with real dataclass fixtures in tests (T-NEW-01)
- Traceability logger switched to centralized `get_logger()`, added figures/tables lookup

## [0.21.3] — 2026-04-05

### Security
- **Global rate limiter middleware** — 120 req/min per-IP, configurable via `RATE_LIMIT_PER_MINUTE` env var (EA-17)
- **Sanitized error responses** — removed 28 `str(e)` instances across 6 routers, preventing internal detail leakage (CWE-209) (EA-18)
- **WebSocket Pydantic validation** — `WSDesignParams`/`WSCheckParams` models enforce input validation (EA-19)
- **CORS from settings** — origins configurable via `CORS_ORIGINS` env var instead of hardcoded (EA-20)
- **Production auth warning** — config.py warns when `AUTH_ENABLED=False` in production (EA-16)

### Added
- **API stability tests** — 4 tests verifying all `__all__` exports importable (EA-9)
- **Import silence test** — verifies `import structural_lib` emits zero warnings (EA-6)
- **E2E pipeline test** — design→detailing→BBS→DXF→report chain tested (EA-7)
- **`repo_only` pytest marker** — separates repo-dependent tests from package tests (EA-8)
- **`build_detailing_input()` factory** — validated builder for detailing input dicts (EA-5)
- **`.to_dict()` on core dataclasses** — consistent serialization across result types (EA-4)
- **Lazy module loading** — 7 modules lazy-loaded via `__getattr__`, ~3x faster import (EA-10)
- **WorkflowHint component** — contextual guidance on Import, Editor, Dashboard pages (EA-11)
- **"Which API?" decision doc** — [api-levels.md](docs/reference/api-levels.md) (EA-12)
- **E2E example script** — `examples/end_to_end_workflow.py` (EA-13)
- **BeamForm validation** — custom cross-field validation (depth > cover, range checks) (EA-15)
- **Torsion `D_mm` parameter** — accepts actual total depth instead of estimating `d+50` (EA-21)
- **`bearing_stress_enhancement()`** — IS 456 Cl 34.4 bearing pressure check (EA-22)
- **`check_scwb()`** — IS 13920 Cl 7.2.1 Strong Column Weak Beam joint check (EA-23)

### Fixed
- **CI publish workflow** — added `tests/__init__.py` + `pythonpath = .` to fix import errors in CI (PR #526)
- **Task-oriented README** — rewritten around "If you want X, call Y" pattern (EA-14)
- **`compute_report()` documented** — return type `str|Path|list[Path]` clarified in docstring (EA-3)
- **Import-time warning cleanup** — lazy clause DB loading, deprecation stubs gated (EA-2)
- **sdist test isolation** — `repo_only` marker prevents false failures in distributed packages (EA-1)

## [0.21.2] - 2026-04-05

Packaging quality release addressing external audit findings. All design calculations are unchanged — fixes are distribution and documentation only.

### Fixed
- **Missing `clauses.json` in PyPI wheel** — IS 456 clause traceability now works from pip-installed package (was silently degrading to empty results)
- **Silent exception swallowing in traceability.py** — Bare `except Exception` narrowed to specific exceptions with `warnings.warn()` on fallback
- **Over-broad package discovery** — `tests/`, `examples/`, `scripts/` excluded from wheel via explicit `include`/`exclude` patterns in pyproject.toml
- **Inaccurate README claims** — Replaced `optimize_pareto_front()` reference (not in public API) with accurate `optimize_beam_cost()` entry
- **Duplicate README heading** — Merged two `## New in v0.21.0` sections

### Added
- **Packaging verification tests** — `test_packaging.py` validates `clauses.json` accessibility, clause lookup, and package scope
- **Python version guidance** — README now notes Python 3.11+ requirement and behavior for older Python versions
- **MANIFEST.in update** — `clauses.json` included for sdist builds

## [0.21.1] - 2026-04-05

Patch release with audit fixes, accessibility improvements, CI hardening, and a column design bug fix.

### Fixed
- **Column uniaxial `is_safe` rounding consistency** — `is_safe` flag now computed from the same rounded `utilization_ratio` value displayed to users, preventing edge-case inconsistency at utilization ≈ 1.0
- **CI bypass prevention** — Closed remaining escape hatches in `finish_task_pr.sh` that could allow merging with failing CI checks
- **CI failure fixes** — Fixed React Validation CI (added hook mocks) and Docker Build CI (JWT_SECRET_KEY env var)

### Improved
- **Audit grade B- → B+** — Resolved all 5 P0 findings, all 20 P1 findings, and 38/52 P2 findings
- **Input validation hardening** — Enhanced boundary checks and error messages across structural modules
- **Accessibility** — Added ARIA labels, skip-to-content link, improved keyboard navigation
- **Code quality** — P2 batch fixes covering error handling, documentation, test coverage improvements

## [0.21.0] - 2026-04-04

Complete column design system (IS 456 Cl 25–39, IS 13920 Cl 7), footing design foundation (Cl 31.6, 34), IS 456 beam restructure, agent infrastructure maturity.

### Highlights

- **Complete column design** — 14 IS 456 column functions covering axial capacity, uniaxial/biaxial bending, P-M interaction curves, slenderness effects, and IS 13920 ductile detailing for seismic zones
- **Footing design** — Isolated footing calculations for bearing capacity, punching shear, one-way shear, and flexural reinforcement per IS 456 Cl 31.6 & 34
- **IS 456 beam restructure** — Beam modules reorganized into a clean subpackage with ductile detailing separated into IS 13920
- **59 REST + WebSocket endpoints** — Full API coverage for all structural calculations including 13 new column design endpoints
- **3,400+ tests passing** — 515+ column-specific tests ensuring code-level compliance with IS 456 and SP:16

### Added
- **Column Design (IS 456)** — `classify_column` (Cl 25.1.2), `min_eccentricity` (Cl 25.4), `short_axial_capacity` (Cl 39.3) with ColumnClassification enum, ColumnAxialResult dataclass, E_COLUMN_001–005 error codes, 7 constants, 3 API wrappers, FastAPI column router with 3 POST endpoints, 75 tests (TASK-630/631/632)
- **TASK-633:** Short column uniaxial bending (Cl 39.5) — design_short_column_uniaxial() + 57 tests + API + FastAPI endpoint
- **TASK-634:** P-M interaction curve (Cl 39.5, Annex G) — pm_interaction_curve() + 45 tests + API + endpoint
- **TASK-635:** Biaxial bending check (Cl 39.6) — biaxial_bending_check() + 84 tests + API + endpoint
- **TASK-636:** Effective length per Table 28 (Cl 25.2) — calculate_effective_length() + EndCondition enum + 69 tests + API + endpoint
- **TASK-637:** Additional moment for slender columns (Cl 39.7.1) — calculate_additional_moment() + 24 tests + API + endpoint
- **TASK-638:** Long column design (IS 456 Cl 39.7) — `design_long_column()` with braced/unbraced support, k-factor reduction, additional moments, 23 tests
- **TASK-639:** Helical reinforcement check (IS 456 Cl 39.4) — `check_helical_reinforcement()` with 1.05 enhancement factor, pitch limits, 14 tests
- **TASK-640:** Column design orchestrator — unified `design_column_is456()` in services/api.py routing short/slender columns
- **TASK-641:** Column FastAPI endpoints — 13 POST endpoints at `/api/v1/design/column/*` with Pydantic models and 89 API tests
- **TASK-645:** Column detailing (IS 456 Cl 26.5.3) — `column_detailing()` with 8 functions, longitudinal/tie requirements, 47 tests
- **TASK-646:** IS 13920 column ductile detailing (Cl 7) — `column_ductile_detailing()` with confining reinforcement, seismic spacing, 18 tests
- **TASK-650–653:** Phase 3 Footing Design — `size_footing` (Cl 34.1), `footing_flexure` (Cl 34.2.3.1), `footing_one_way_shear` (Cl 34.2.4.1a), `footing_punching_shear` (Cl 31.6.1), 61 tests
- **Enhanced Shear Near Supports** — `enhanced_shear_strength` (Cl 40.3) with 14 tests and API endpoint (TASK-712)
- **TASK-642:** Five-point steel stress-strain curve (IS 456 Fig 23) — stress_strain_steel_5pt() in stress_blocks.py + 26 tests
- **TASK-671:** Fix 4 known limitations — unified effective depth, serviceability opt-in, multi-layer rebar support, failure story field
- **TASK-800:** Agent evolver infrastructure — 10 scripts (scorer, drift detector, compliance checker, trend analysis, session collector, instruction evolution), P12 burn-in
- **TASK-850–872:** Agent Infrastructure — agent registry JSON, prompt router (14 rules), tool permissions (3 levels), pipeline state, hooks framework (6 hooks), parity dashboard, skill tiers, config precedence, CLI smoke tests
- **Foundation Cleanup (Phase 1 Complete)**
- **TASK-621:** Added `recovery` field to DesignError — step-by-step fix instructions for all 39 error codes
- **TASK-622:** Created check_function_quality.py — 12-point AST-based IS 456 function quality checker
- **TASK-623:** Created check_clause_coverage.py — IS 456 clause gap detection (119 clauses tracked)
- **TASK-624:** Created check_new_element_completeness.py — 7-layer element completeness matrix
- **TASK-625:** Created docs/governance/maintenance-playbook.md — governance playbook (11 sections)

### Changed
- **TASK-660:** Variable naming standardization to IS 456 convention — 21 field renames across 4 dataclasses with backward-compat aliases
- **TASK-700–712:** IS 456 Beam Restructure (Phase 1.5) — beam modules organized into `codes/is456/beam/` subpackage, ductile detailing moved to `codes/is13920/beam.py`, backward-compat shims
- **Agent count:** 14 → 16 agents, 8 → 10 skills, 15 → 16 prompt files
- **Endpoint count:** 43 → 59 REST endpoints across 13 routers

### Fixed
- **Column P-M Interaction (TASK-690)** — SP:16 Table I continuity at k=1.0, Cl 38.1 modified strain for xu>D, xu_bal 0.002 inelastic strain for HYSD bars, Pu_0 envelope cap
- **Column Biaxial e_min (TASK-691)** — Enforce Cl 25.4 minimum eccentricity on both axes before Bresler interaction check
- **TASK-670:** Fix calculation_report.py ShearResult field bug — corrected 4 non-existent field accesses
- **TASK-900:** Git workflow hardening — safe_push.sh divergence detection, --amend blocking, actionable error messages (13/14 phases complete)

### Security
- **Column Router (TASK-692)** — Sanitized 13 exception handlers removing internal error details (CWE-209)
- **TASK-681:** Migrated python-jose → PyJWT — removed legacy JWT library with full test coverage

### Developer
- 56+ commits since v0.20.0
- 3,401 tests passing (515+ column-specific)
- Sessions 103–current logged
- Innovation prototypes: sustainability scoring, generative design, structural companion

## [0.20.0] - 2026-03-30

V3 Foundation release — everything built since v0.19.1. Full-stack maturity milestone: React 19 + FastAPI + Python structural_lib with comprehensive quality infrastructure.

### Added
- **Batch Design React UI** — SSE streaming progress for multi-beam design (`TASK-510`)
- **Compliance Checker** — IS 456 compliance wired into React DesignView panel
- **Cost Optimizer** — Pareto-optimal beam design exposed in React UI
- **86 API Integration Tests** — Vitest test suites across all 12 FastAPI routers (`TASK-505`)
- **React UX Overhaul**
  - `BeamDetailPanel` with correct utilization, top bars, redesign button, edit rebar mode (`TASK-522`)
  - `CrossSectionView` annotations — utilization color, actual barDia/barCount, badge (`TASK-526`)
  - `HomePage` rewrite — minimal landing with continuous beam rotation
  - TopBar nav links, ModeSelect quick access
  - Code-split React bundle with lazy routes and manual chunks (`TASK-502`)
  - WebSocket REST fallback when connection drops (`TASK-503`)
  - React test infrastructure — Vitest + 5 smoke test suites, 23 tests (`TASK-506`)
- **Library Expansion**
  - PDF export via `compute_bmd_sfd` FastAPI endpoint (`TASK-514/515`)
  - Load calculator hook `useLoadCalculator` (`TASK-515`)
  - Project BOQ full-stack implementation (`TASK-517`)
  - Torsion API + `useTorsionDesign` React hook (`TASK-518`)
- **Phase 1 Foundation Cleanup**
  - `core/numerics.py` — centralized numerical utilities (`TASK-611`)
  - `codes/is456/common/` — IS 456 constants and shared math (`TASK-612/613`)
  - Deprecation decorator module (`TASK-614`)
  - `clauses.json` expansion to 119 entries (`TASK-615`)
  - Test assertion helpers for IS 456 compliance (`TASK-616/617`)
  - 41 new tests for Phase 1 foundations
- **Quality Infrastructure**
  - Function-quality-pipeline skill (9-step mandatory gate for IS 456 functions)
  - 14 Copilot agents, 8 skills, 15 prompt files
  - `structural-math` agent + `new-structural-element` skill
  - Self-evolving agent system with architecture fixes
  - Security agent with FORBIDDEN command gates
- **Developer Tooling**
  - Release infrastructure overhaul — preflight checks, CI publish workflow, release docs (`#460`)
  - `ai_commit.sh` upgrades — `--preview`, `--undo`, `--signoff`, `--status`, `--branch`, `--finish`, `--pr-check`
  - `run.sh` unified CLI + `check_all.py` validation (28 checks)
  - `launch_stack.sh` full-stack dev launcher (FastAPI + React)
  - Centralized React API config with Vite proxy
  - Git hygiene — stale branch detection, pre-merge conflict check, tracking ref cleanup
  - MkDocs Material documentation site with lychee CI link checking
  - ETABS VBA column aliases and E2E integration tests for adapters

### Changed
- **Streamlit Removal** — Legacy Streamlit app and all related files deleted; VBA/Excel extracted to separate repo
- **Scripts Cleanup** — Stale files deleted, deprecation markers added, phase 1+2 cleanup
- **Agent Upgrades** — All agents upgraded to Opus 4.6, professional `ai_commit.sh` with retry and stash recovery
- **Doc System Overhaul** — Budget checks, CODEOWNERS, append-first policy, doc metadata backfill
- **Git Workflow** — Consolidated 5 git docs into single source, practical PR policy, push-only mode

### Fixed
- Architecture violations — stub imports in Streamlit, dead test deletion (`TASK-507`)
- `check_all.py` — 19/28 → 25/28 passing (API validation, manifest, OpenAPI snapshot, links) (`TASK-501`)
- Git workflow — SIGPIPE under pipefail, duplicate PR creation, stash loss, CI polling race
- Slenderness monotonicity test flaky float precision edge case
- Single CSV import crash and adapter auto-detection fallback
- React build errors, pre-commit fixes, IPv6 uvicorn binding
- CodeQL taint flow in `check_docker_config.py`
- 21 scripts cleaned of Streamlit remnants, 4 orphaned tests deleted

### Developer
- 90+ commits since v0.19.1
- Sessions 92–113 logged
- Benchmark configs consolidated, `.gitignore` updated
- 178 research files archived to `docs/_archive/research/pre-v021`
- Comprehensive maintenance: indexes, stale dates, archival (session 109)

## [0.19.1] - 2026-03-24

### Added
- **React 19 Frontend (V3 Stack)** 🎉
  - Modern Gen Z UI with BentoGrid layout and Tailwind CSS
  - 3D beam visualization with React Three Fiber (`Viewport3D`)
  - Building frame visualization with story-based color coding
  - Live design via WebSocket (`useLiveDesign`, `useAutoDesign`)
  - Dual CSV import with auto-column mapping (`useDualCSVImport`)
  - AG Grid for beam data tables, cmdk command palette
  - Cross-section view with rebar positions
  - Export panel with BBS, DXF, and report downloads (`useExport`)
  - Dashboard insights, code checks, and rebar suggestions wired into UI

- **FastAPI Backend**
  - 35 endpoints across 12 routers (design, detailing, geometry, import, export, insights, rebar, streaming, websocket, health, optimization, analysis)
  - WebSocket resilience with reconnection and error handling
  - Real CSV loading replacing hardcoded sample data
  - OpenAPI snapshot test for schema drift detection

- **4-Layer Architecture Enforcement**
  - Migration: 10 core modules to `core/`, 17 service modules to `services/`, 9 root modules relocated
  - `check_architecture_boundaries.py` enhanced with UI-layer import rules (11 forbidden patterns)
  - Migration scripts: `migrate_python_module.py`, `migrate_react_component.py`
  - Governance locking with integration tests
  - Zero circular imports, zero broken imports (567 total, 220 internal)

- **Developer Tooling**
  - `AGENTS.md` — Cross-agent instructions for Copilot, Claude, Cursor, Windsurf
  - 5 Copilot prompt files (session-end, new-feature, bug-fix, add-api-endpoint, code-review)
  - `automation-map.json` with 84 scripts mapped
  - `sync_numbers.py` + `session.py` for automated doc sync
  - `check_instruction_drift.py` for agent instruction file consistency
  - When-to-use docstrings for all 84 scripts
  - Post-commit stale-number detection

### Changed
- **Scripts Consolidation** — 163 → 84 active scripts (Phase 1–3)
  - Created `_lib/utils.py`, `_lib/output.py`, `_lib/ast_helpers.py` shared utilities
  - Archived 53 deprecated scripts, consolidated 4 script groups
- **React Component Organization** — Feature-grouped under `components/design/`, `components/import/`, `components/viewport/`, `components/layout/`, `components/pages/`, `components/ui/`
- **CSS → Tailwind Migration** — All component styles migrated to Tailwind utility classes

### Fixed
- Architecture violations: 3 streamlit imports routed through `services.api` facade
- Unit conversion annotations added to `shear.py` for clarity
- 11 broken doc links repaired after file moves
- 280+ stale script references fixed across 45 files
- Scanner false positives eliminated, `safe_file_delete` 170x speedup
- React hooks errors, 3D rendering, dual CSV UI issues resolved
- Critical `ZeroDivisionError` risks in multi-format import fixed
- NaN handling in editable results table
- 267 ruff lint errors auto-fixed

### Added
- **Industry-Standard DXF Export Improvements**
  - Beam grouping by type (size + span + reinforcement)
  - Beam schedule table in IS 2502 format
  - Rebar unit weights per IS 2502:1963
  - Smart text truncation to prevent overlap

- **Streamlit API Index**
  - Comprehensive function/component reference
  - Easy lookup for reusable code
  - Pattern examples for safe coding

### Changed
- **DXF Schedule Table**
  - Increased column widths for better text fit
  - Reduced text height for data cells
  - Smarter text truncation based on column width
  - Higher row/header heights for readability

### Fixed
- **AI Assistant Model Name**
  - Fixed invalid `gpt-5-mini` to `gpt-4o-mini`
  - Updated all occurrences in code and secrets

## [0.19.0] - 2026-01-21

### Changed
- **DXF Schedule Polish** — Column widths, text sizing, smart truncation
- **AI Model Name Fix** — Fixed invalid `gpt-5-mini` to `gpt-4o-mini`
- **Streamlit API Index** — Component reuse index for Streamlit app

## [0.18.0] - 2026-01-20

### Added
- **AI Assistant v2 with Dynamic Workspace** 🎉
  - Complete redesign with 35% chat / 65% dynamic workspace layout
  - 9-state workflow: WELCOME → IMPORT → DESIGN → BUILDING_3D → VIEW_3D → CROSS_SECTION → REBAR_EDIT → EDIT → DASHBOARD
  - Auto-column-mapping for ETABS/SAFE CSV imports
  - Built-in sample data (10 beams, 3 stories) for quick demos
  - Smart chat commands: `load sample`, `design all`, `building 3d`, `edit rebar`, `cross section`

- **Building 3D Visualization**
  - Full building view with all beams in 3D
  - Story-based color coding (Story1=blue, Story2=green, Story3=orange)
  - Hover info with beam details
  - Summary stats (beams per story, pass/fail counts)

- **Interactive Rebar Editor**
  - Bottom/top layer configuration with bar diameter and count
  - Stirrup diameter and spacing controls
  - Real-time IS 456 design checks:
    - Flexure capacity (Mu = 0.87 × fy × Ast × 0.9 × d)
    - Shear capacity (τc from IS 456 Table 19 + stirrups)
    - Min/max reinforcement (IS 456 Cl 26.5.1.1)
    - Bar spacing check
  - Pass/fail indicators with utilization percentage

- **Cross-Section View**
  - Professional 2D cross-section using Plotly
  - Dimension annotations (b, D, cover)
  - Bar positions with hover info
  - Color-coded: bottom (blue), top (green), stirrups (gray)
  - Rebar schedule table

- **Material Takeoff & Cost Estimation**
  - Concrete volume (m³), steel weight (kg)
  - Per-story breakdown
  - Cost estimation (₹8000/m³ concrete, ₹85/kg steel)
  - Cost per running meter
  - Pie chart visualization

- **Dashboard Export Tab**
  - CSV download with all design results
  - Text summary with material takeoff and costs

- **Phase 3 Rebar Visualization**
  - Variable stirrup zones per IS 456 2d rule (tighter at supports)
  - Development length and lap length calculations
  - Beam detail 3D view in Page 07

### Changed
- **OpenAI Model Configuration**
  - Default model: `gpt-4o-mini` (fast, cost-efficient)
  - Configurable via secrets.toml for OpenAI or OpenRouter

- **UI/UX Improvements**
  - Loading spinners on data operations
  - Feature highlights with icons on welcome panel
  - Helpful tooltips on all action buttons
  - Chat tips for workflow guidance
  - Contextual warnings for failed beams

- **Package Updates**
  - Streamlit 1.52.2 → 1.53.0
  - Plotly 6.5.1 → 6.5.2
  - Ruff 0.14.11 → 0.14.13
  - Rich 13.9.4 → 14.2.0
  - Reportlab 4.4.7 → 4.4.9

### Fixed
- Zero-division guards in rebar checks and progress calculation
- Safe float conversion in data processing
- API signature validation for `bar_diameter` parameter

## [0.17.5] - 2026-01-14

### Added
- **Multi-Objective Pareto Optimization (NSGA-II)**
  - `multi_objective_optimizer.py` - Pure Python NSGA-II implementation
  - `ParetoCandidate` dataclass with 17 attributes including governing IS 456 clauses
  - `optimize_pareto_front()` for multi-objective beam optimization
  - Fast non-dominated sorting and crowding distance algorithms
  - `get_design_explanation()` with IS 456 clause references

- **Cost Optimizer UI Enhancement**
  - Dual optimization buttons: "Quick Optimization" vs "Pareto Multi-Objective"
  - Interactive Pareto scatter plot visualization
  - Best designs by cost/weight/utilization with governing clauses
  - WHY explanations for design decisions with IS 456 references

- **API Signature Validation**
  - `scripts/check_api_signatures.py` - AST-based API contract testing
  - Detects wrong parameter names, missing params, incorrect dict keys
  - Smart false-positive reduction (ignores local functions, DataFrame access)
  - Pre-commit hook integration
  - CI workflow job for API validation

- **Test Coverage**
  - 13 new tests for multi-objective optimizer
  - Pareto front generation, non-dominated sorting tests
  - Crowding distance calculation tests

### Changed
- Updated CI workflow with API signature validation job
- Enhanced pre-commit hooks with API signature checking

### Fixed
- Session 24 API signature mismatches across all Streamlit pages
- Fixed 50+ tests passing, 0 CRITICAL scanner issues

## [0.17.0] - 2026-01-13

### Added
- **Professional API Features**
  - `BeamInput` dataclasses for flexible input handling (TASK-276)
  - Professional calculation report generation module (TASK-277)
  - Verification and audit trail module for compliance tracking (TASK-278)
  - Engineering testing strategies module with benchmark framework (TASK-279)

- **Debug & Diagnostics Infrastructure**
  - `scripts/collect_diagnostics.py` - Creates timestamped diagnostic bundles for troubleshooting
  - `scripts/generate_api_manifest.py` - Generates/validates API manifest with 38 public symbols
  - `scripts/check_scripts_index.py` - Validates scripts/index.json accuracy
  - `docs/reference/api-manifest.json` - Complete API surface documentation
  - Diagnostics reminders in `agent_start.sh` and `end_session.py`
  - Debug snapshot checklist in handoff documentation

- **Documentation Metadata System (TASK-458)**
  - Added metadata headers to 50+ documentation files
  - `scripts/create_doc.py` - Creates new docs with proper metadata
  - `scripts/check_doc_metadata.py` - Validates metadata in pre-commit
  - Standardized Type, Audience, Status, Importance, Version fields

- **Documentation Consolidation (TASK-457)**
  - Archived 91 session/task docs from streamlit_app/docs
  - Archived 26 completed research files with 180 link fixes
  - `scripts/consolidate_docs.py` - Improved consolidation workflow
  - Reduced documentation sprawl significantly

### Changed
- **Git Workflow Automation**
  - Added enforcement hook blocking manual git commands
  - Improved error clarity with 'why' and recovery guidance
  - Policy-aware merge with `--force` mode for batched commits
  - Removed manual git examples from active documentation

- **Pre-commit Hooks**
  - Added API manifest validation hook
  - Added scripts index validation hook
  - Added doc metadata check (warning mode)
  - Skip research folder in filename validation

### Fixed
- Streamlit import checker: added `--skip-known` flag to reduce false positives
- CI: skip research folder in filename validation for legacy naming
- Fixed invalid 'local' keyword in `finish_task_pr.sh`
- Pre-commit whitespace and line ending fixes across 15 files
- Ruff UP038 fixes in test files (use `X | Y` in isinstance)

### Developer Notes
- All 2598 tests passing
- 128 automation scripts indexed
- 38 public API symbols tracked
- Pre-commit validation strengthened

## [0.16.6] - 2026-01-12

### Changed
- **Python 3.11 Baseline Upgrade**
  - Minimum Python version raised from 3.9 to 3.11
  - CI matrix reduced from [3.9, 3.10, 3.11, 3.12] to [3.11, 3.12] (50% faster CI)
  - Fast checks now use Python 3.11 only
  - Local virtual environment recreated with Python 3.11.14

- **Type Hint Modernization (PEP 604)**
  - Converted `Optional[X]` to `X | None` across 20+ modules
  - Converted `Union[X, Y]` to `X | Y` using ruff --fix
  - Converted `isinstance((X, Y))` to `isinstance(X | Y)` (UP038)
  - Added `from __future__ import annotations` to all affected modules

- **Pre-commit Hook Updates**
  - All local hooks now use `.venv/bin/python` for Python 3.11 compatibility
  - Added `check_python_version.py` to enforce version consistency

### Added
- `scripts/check_python_version.py` - Validates Python version references across project
- `scripts/add_future_annotations.py` - Helper to add `__future__` imports

### Developer Notes
- Users must have Python 3.11+ installed locally (`brew install python@3.11`)
- Virtual environment should be recreated: `rm -rf .venv && python3.11 -m venv .venv`
- All 2430 tests passing on Python 3.11

## [0.16.5] - 2026-01-11

### Added
- **Unified Agent Onboarding** (`scripts/agent_start.sh`)
  - Single command replaces 4-command workflow (agent_setup + agent_preflight + start_session + copilot_setup)
  - 90% faster onboarding (4 commands → 1 command, ~30s → ~3s)
  - Agent-specific guidance with `--agent` flag (6, 8, 9)
  - Worktree support for background agents (`--worktree NAME`)
  - Quick mode (`--quick`) and full validation modes
  - v2.1: Fixed full mode to run complete setup, proper worktree passthrough

- **Folder Structure Governance** (`docs/guidelines/folder-structure-governance.md`)
  - Comprehensive V2.0 spec with 115 validation errors fixed
  - CI-enforced folder limits (max 10 root files, currently 9)
  - Automated compliance checking via `scripts/check_governance_compliance.py`
  - Safe file operations: `safe_file_move.py`, `safe_file_delete.py`
  - Link validation protecting 789 internal links
  - Repository hygiene: zero orphan files, semantic READMEs in all folders

- **Git Workflow Automation Improvements**
  - 90-95% faster commits (45-60s → 5s average)
  - Parallel fetch optimization (saves 30-40s per commit)
  - Incremental whitespace checking (Step 2.5 prevents hash divergence)
  - CI monitoring daemon for PR status tracking
  - Merge conflict test suite (31 test cases)
  - Comprehensive audit logging in `git_operations_log/`

- **Multi-Code Foundation Architecture**
  - New `core/` package for code-agnostic modules (geometry, materials, base classes)
  - New `codes/` package with `is456/` subdirectory
  - CodeRegistry for multi-code support (future: ACI 318, EC2)
  - MaterialFactory with code-specific material properties
  - All 7 IS 456 modules migrated to `codes/is456/` (3,048 lines)
  - Zero breaking changes (100% backward compatibility via stubs)
  - 2392 tests passing, 86% coverage maintained

- **103 Automation Scripts**
  - Module migration: `migrate_module.py`, `validate_migration.py`, `pre_migration_check.py`
  - Governance: `check_governance_compliance.py`, `validate_folder_structure.py`
  - Link management: `check_links.py`, `fix_broken_links.py` (fixed 213 links in 5s)
  - File operations: `safe_file_move.py`, `safe_file_delete.py`, `find_orphan_files.py`
  - Documentation: `generate_folder_index.py`, `enhance_readme.py`, `check_folder_readmes.py`
  - Metrics: `measure_agent_navigation.sh`, `analyze_navigation_data.py`

### Changed
- **Documentation Consolidation**
  - Archived 7 redundant automation docs (reduced from 8 → 5 canonical)
  - Updated agent onboarding docs to use `agent_start.sh` as primary workflow
  - Marked Agent 9 governance content as archived (migrated to `docs/guidelines/`)
  - Fixed 20+ stale FOLDER_STRUCTURE_GOVERNANCE.md references in historical docs

- **README Showcase**
  - Updated "At a glance" with 103 automation scripts, 789 validated links
  - Added v0.16.5 highlights: automation, governance, multi-code foundation
  - Work-in-progress banner with links to TASKS.md and next-session-brief.md

### Fixed
- Pre-commit hook whitespace handling (Step 2.5 prevents commit hash divergence)
- Governance validator: root file counting, limit enforcement (20→10), path resolution
- Link validation: 789 internal links, zero broken links
- agent_start.sh v2.1: Full mode now runs complete setup (not --quick)
- Worktree passthrough to both agent_setup.sh and agent_preflight.sh

### Repository Metrics (Session 13)
- **Commits:** ~25 commits across 7 parts
- **PRs:** 7 PRs merged (#323, #326, #327, #328, #329, #330)
- **Files:** 11 governance tasks complete, 164 files archived
- **Links:** 789 internal links validated, zero broken
- **Scripts:** 103 total automation scripts (+15 from Session 13)
- **Root Files:** 14 → 9 (below CI limit of 10)

## [0.16.0] - 2026-01-08

### Added
- **Streamlit UI Enhancement - Phase 2 Complete**
  - **UI-003: Chart/Visualization Upgrade** (`streamlit_app/utils/plotly_enhancements.py`)
    - Enhanced Plotly theme integration with dark mode support
    - Professional color schemes for technical engineering charts
    - Consistent styling across all visualizations
    - 350 lines of visualization theme code
  - **UI-004: Dark Mode Implementation** (`streamlit_app/utils/theme_manager.py`)
    - Complete dark/light theme toggle with session persistence
    - WCAG 2.1 Level AA accessibility compliance
    - Theme-aware color management for 15+ component types
    - Moon/sun icon toggle in sidebar
    - 325 lines of theme management code
  - **UI-005: Loading States & Animations** (`streamlit_app/utils/loading_states.py`)
    - 5 professional loader types (skeleton, spinner, progress, dots, shimmer)
    - Context manager for operation loading states
    - Theme-aware animations
    - Sub-10ms render performance
    - 494 lines of loading state code
  - **Test Coverage:** 70+ new tests for UI components
    - `test_theme_manager.py` (278 lines, 20+ test cases)
    - `test_loading_states.py` (407 lines, 40+ test cases)
    - `test_plotly_enhancements.py` (350 lines, 30+ test cases)
- **API Convenience Functions for Streamlit Integration**
  - `api.design_and_detail_beam_is456()` - Combined design + detailing in one call
  - `bbs.generate_summary_table()` - Markdown/HTML/text BBS output formats
  - `dxf_export.quick_dxf()` - One-liner DXF file generation
  - `dxf_export.quick_dxf_bytes()` - DXF as bytes for Streamlit downloads
  - `DesignAndDetailResult` dataclass with serialization methods (to_dict, from_dict, to_json)
  - 16 new integration tests for convenience functions

### Fixed
- **Test Naming Conventions:** Fixed 7 test functions in `test_validation.py` with uppercase 'D' to comply with ruff N802 naming rules
- **Python 3.9 Compatibility:** Fixed type annotations using `Optional[str]` instead of `str | None`
- **Serialization:** Fixed recursion error in `to_dict()` methods using `asdict()` directly

### Changed
- **Streamlit Pages Updated:** All 4 pages (Beam Design, Cost Optimizer, Compliance, Documentation) now support dark mode
- **API Documentation:** Updated `docs/reference/api.md` and `docs/reference/api-stability.md` with new convenience functions

### Repository Maintenance
- Cleaned up merged worktree branches (removed 3 obsolete worktrees)
- Removed merged remote branches (worktree-2026-01-07T07-28-08, worktree-2026-01-07T08-14-04, worktree-2026-01-08T06-07-26)
- Updated Agent 6 task documentation to mark UI-001 through UI-005 as complete

## [0.15.0] - 2026-01-07

### Added
- **Smart design analysis dashboard** (`structural_lib.insights.smart_designer`)
  - `SmartDesigner` class with unified `analyze()` method
  - Combines cost optimization, design suggestions, sensitivity analysis, and constructability
  - 6 structured dataclasses: `SmartAnalysisSummary`, `CostAnalysis`, `DesignSuggestions`, `SensitivityInsights`, `ConstructabilityInsights`, `DashboardReport`
  - Overall design score (0-100) with customizable weights
  - Multiple output formats: dict, JSON, formatted text
  - Helper function `quick_analysis()` for simplified text output
  - 19/20 comprehensive tests passing
- **Public API wrapper for smart analysis** (`smart_analyze_design()`)
  - Simple API accepting beam parameters (b_mm, D_mm, d_mm, fck, fy, mu, vu, span)
  - Runs full design pipeline internally to get complete design context
  - Returns unified dashboard with all insights
  - Supports selective feature inclusion (cost, suggestions, sensitivity, constructability)
  - Output formats: dict (default), JSON string, or formatted text
  - Solves type architecture mismatch between public API and SmartDesigner
- **Comparison and sensitivity enhancement module** (`structural_lib.insights.comparison`)
  - `compare_designs()` function for multi-design alternative comparison
  - `cost_aware_sensitivity()` function combining sensitivity with cost impact
  - 4 dataclasses: `DesignAlternative`, `ComparisonMetrics`, `ComparisonResult`, `CostSensitivityResult`
  - Comprehensive comparison metrics: material usage, structural performance, cost efficiency
  - Pareto frontier identification for multi-objective optimization
  - Cost-weighted sensitivity rankings
  - 19 comprehensive tests covering comparison logic, edge cases, and cost integration
  - Exported via `insights/__init__.py` for public API access
- **Rebar optimizer comprehensive test suite** (`tests/test_rebar_optimizer.py`)
  - 31 comprehensive test cases added (46 total tests passing)
  - Coverage: bar combinations, diameter constraints, symmetry, edge cases
  - Benchmark vectors for regression detection
  - Validates optimization logic and constraint handling
- **Workflow automation tools** (`scripts/`)
  - `create_task_pr.sh` and `finish_task_pr.sh` for fast PR workflow
  - `safe_push_v2.sh` with comprehensive audit logging and conflict prevention
  - `test_git_workflow.sh` with 31 test cases validating git operations
  - `validate_git_state.sh` for pre-push safety checks
  - Professional workflow review documentation (`docs/contributing/workflow-professional-review.md`)
- **CLI scaffolding for smart command** (`smart` subcommand in `__main__.py`)
  - Command structure ready for future CLI integration
  - Configurable analysis components (--no-cost, --no-suggestions, etc.)
  - Text and JSON output format support

## [0.14.0] - 2026-01-06

### Added
- **Contract testing for API stability** (`tests/test_contracts.py`)
  - Prevents accidental breaking changes to public API signatures
  - Tests for function parameters, return types, and dataclass fields
  - Schema version tracking enforcement
  - Units parameter backwards compatibility validation
  - Can run standalone as pre-commit hook: `python tests/test_contracts.py`
  - 6 comprehensive tests protecting API surface
- **Centralized validation utilities** (`structural_lib/validation.py`)
  - `validate_dimensions()` - beam width, depth, and geometry checks
  - `validate_materials()` - concrete and steel strength validation
  - `validate_cover()` - cover requirements per IS 456 with min/max checks
  - `validate_loads()` - moment and shear validation with reasonableness checks
  - `validate_material_grades()` - IS 456 Table 2 and Annex C grade verification
  - `validate_reinforcement()` - steel area min/max limit enforcement
  - `validate_span()` - beam span reasonableness validation
  - `validate_beam_inputs()` - composite validator for full beam design inputs
  - 78 comprehensive tests with 100% coverage
  - Reduces code duplication by ~30% across calculation modules
- **Deprecation policy and tools** (`structural_lib/utilities.py`, `docs/reference/deprecation-policy.md`)
  - `@deprecated()` decorator for marking deprecated functions
  - `deprecated_field()` helper for dataclass field deprecation
  - Follows semantic versioning with minimum 1 minor version notice period
  - Metadata storage for programmatic introspection (`__deprecated__` attribute)
  - Complete policy documentation with migration guide templates
  - 18 tests for deprecation mechanism
  - References: PEP 387, NumPy/pandas deprecation policies
- **Error handling strategy documentation** (`CONTRIBUTING.md`)
  - 5-layer error handling architecture (Core, Validation, Orchestration, I/O, CLI)
  - Clear guidelines for when to raise exceptions vs return structured errors
  - Audit compliance script: `scripts/audit_error_handling.py`
  - Examples for each layer with rationale
- **Comprehensive research documentation** (`docs/research/`)
  - `cs-best-practices-audit.md` (938 lines) - Comparison to numpy/scipy/pandas patterns
  - `backward-compatibility-strategy.md` (1197 lines) - Contract testing, regression testing, deprecation strategy
  - `modern-python-tooling.md` (1540 lines) - Evaluation of uv, Hypothesis, pytest-benchmark, mutmut
  - `cs-practices-implementation-plan.md` (1575 lines) - 23 actionable tasks across 3 phases
  - `xlwings-vba-strategy.md` (868 lines) - VBA deprecation roadmap (85% reduction target)
- **Git workflow improvements** (`scripts/safe_push.sh`, `.pre-commit-config.yaml`)
  - Pre-commit hook to detect unfinished merges
  - Pull-first workflow to prevent merge conflicts
  - Contract tests integrated as pre-commit hook

### Changed
- **Eliminated silent failures in core modules** (17 functions fixed)
  - Functions in `flexure.py`, `shear.py`, `materials.py`, `detailing.py`, `serviceability.py`, `ductile.py`
  - Changed from returning `0.0`/empty values to raising explicit `ValueError` with clear messages
  - Examples: `calculate_mu_lim()`, `calculate_tv()`, `calculate_ast_required()`, `get_xu_max_d()`, `get_ec()`, `get_fcr()`, `calculate_development_length()`, `calculate_bar_spacing()`
  - Updated 7 tests to expect exceptions with proper error messages
  - All core calculations now fail fast with actionable error messages
- **Strengthened mypy type checking** (`Python/pyproject.toml`)
  - Enabled `warn_return_any = true` (catches `Dict[str, Any]` returns)
  - Enabled `strict_optional = true` (stricter None handling)
  - Enabled `warn_redundant_casts = true` (code quality)
  - Added `show_error_codes = true` for better debugging
  - Fixed 5 mypy errors across modules
- **Pre-commit hook configuration**
  - Fixed mypy hook to use local venv Python (`cd Python && ../.venv/bin/python -m mypy`)
  - Contract tests run automatically before commits
  - Removed deprecated `stages` parameter from hook configs
- **Test infrastructure improvements**
  - Total test count: 2200 tests (up from ~2040)
  - Test coverage: 86% (up from 84%)
  - 100% coverage modules: `data_types`, `errors`, `excel_integration`, `materials`, `shear`, `tables`, `utilities`, `validation`
  - All tests passing in 3.67s

### Fixed
- **Merge conflict prevention** (fixes #246)
  - Implemented pull-first workflow in `safe_push.sh`
  - Added pre-commit hook to detect unfinished merges
  - Prevents race conditions between parallel agent commits
  - Documented in `docs/contributing/git-workflow-for-ai-agents.md`

### Documentation
- **Updated CONTRIBUTING.md** with comprehensive error handling strategy
- **New deprecation policy** in `docs/reference/deprecation-policy.md`
- **Research reports** (5 documents, 5,800+ lines total) in `docs/research/`
- **Git workflow guide** for AI agents with merge conflict solutions

## [0.13.0] - 2025-12-31

### Added
- **Insights verification pack** (`tests/test_insights_verification_pack.py`, `tests/data/insights_benchmark_cases.json`)
  - 10 benchmark cases covering precheck, sensitivity, and constructability
  - JSON-driven parametrized tests for regression detection
  - Categories: 3 precheck, 4 sensitivity, 3 constructability
  - User documentation: `docs/verification/insights-verification-pack.md`
- Side-face reinforcement check per IS 456 Cl 26.5.1.3 (`check_side_face_reinforcement` in `detailing.py`)
  - Required when D > 750 mm
  - Calculates 0.1% web area per face with 300mm max spacing
  - Comprehensive test coverage (9 test cases)
- **Insights JSON serialization and CLI integration** (`insights/types.py`, `__main__.py`)
  - Added `.to_dict()` methods to all 6 insights dataclasses for JSON export
  - Proper enum conversion (e.g., Severity.WARNING → "warning")
  - Nested dataclass serialization (lists, nested objects)
  - New `--insights` flag for `design` CLI command
  - Outputs insights to separate JSON file (e.g., `results_insights.json`)
  - Safe error handling (insights failures don't crash main design)
  - 6 comprehensive tests for JSON serialization (`test_insights_json.py`)
  - Precheck, sensitivity, and robustness working in CLI
  - Constructability deferred for future API alignment
- **Insights module examples in Colab notebook** (`colab-workflow.ipynb`)
  - Quick precheck demonstration
  - Sensitivity analysis with parameter ranking
  - Constructability scoring breakdown
- **Comprehensive test coverage for insights module**
  - Sensitivity analysis: 14 tests covering golden vectors, edge cases, physical validation, robustness scoring
  - Constructability scoring: 10 tests covering full design spectrum (light/typical/heavy/congested), factor-specific tests
  - JSON serialization: 6 tests covering all insights types, round-trip validation, enum conversion
- **Complete insights documentation** (`docs/getting-started/insights-guide.md`, `docs/reference/insights-api.md`)
  - User guide covering all three insight types (precheck, sensitivity, constructability)
  - Python API and CLI usage examples with working code
  - Risk level interpretation and sensitivity coefficient explanation
  - Complete API reference with function signatures, parameters, complexity analysis
  - Dataclass documentation with JSON serialization methods
  - Best practices, limitations, and troubleshooting guidance
  - Cross-linked to main API reference and docs index

### Changed
- **Constructability scoring upgraded to 0-100 scale** (`insights/constructability.py`)
  - Changed from 0-10 to 0-100 for finer granularity
  - Scaled all penalties/bonuses (10× multiplier)
  - Updated rating thresholds: 85+ excellent, 70-84 good, 55-69 acceptable, <55 poor
  - Added missing factors:
    - Depth increments (50mm multiples for formwork reuse)
    - Bar configuration simplicity (2-3 bars per layer ideal)
  - Enhanced recommendations with impact statements (labor cost, quality, productivity)
  - Comprehensive docstring with BDAS framework reference (Poh & Chen 1998)

### Fixed
- **Sensitivity analysis normalization bug** (`insights/sensitivity.py`)
  - Changed from `S = Δu/Δp` to `S = (Δu/u)/(Δp/p)` for dimensionless coefficients
  - Sensitivities now comparable across different parameter units (mm, MPa, kNm)
- **Robustness calculation improved** (`insights/sensitivity.py`)
  - Changed from heuristic penalty-based to margin-based calculation
  - Now quantifies allowable parameter variation before failure
  - Formula: `robustness = min_variation / 0.20` (normalized to 0-1)
- Enhanced docstrings for `sensitivity_analysis()` and `calculate_robustness()` with examples

## [0.12.0] - 2025-12-30

### Added
- Library-first API wrappers for detailing/BBS/DXF/report/critical outputs.
- `validate` CLI + validation APIs for job/results JSON.
- `detail` CLI to emit detailing JSON from design results.
- BBS/DXF bar mark consistency check (CLI + API helpers).
- DXF content tests for required layers and callout text.
- DXF render workflow (PNG/PDF) with optional `render` dependency.
- Wrapper test coverage for v0.12 APIs.

### Changed
- DXF title block now includes size/cover/span context for deliverables.
- Colab notebook updated with BBS/DXF + mark-diff workflow.
- API reference and stability docs updated for new wrappers.

### Fixed
- Avoided import cycle in DXF wrapper initialization.

## [0.11.0] - 2025-12-29

### Added
- **Visual report HTML (V04–V07):**
  - Cross-section SVG rendering
  - Input sanity heatmap
  - Stability scorecard
  - Units sentinel checks
- **Batch report packaging (V08):**
  - `report` supports `design_results.json` input
  - Folder output with `--batch-threshold` for large batches
- **Golden fixtures (V09):**
  - Deterministic HTML outputs verified via golden-file tests

### Changed
- CLI help and docs updated for `report` + `critical` workflows

## [0.10.7] - 2025-12-29

### Added
- **Visual v0.11 — Critical Set Export (V03):**
  - New `critical` CLI subcommand outputs sorted utilization tables (CSV/HTML)
  - `--top` flag to slice top-N critical beams
  - `data-source` traces on each field for auditability
- **Report foundations:** `report.py` skeleton and `load_job_spec()` helper for report pipelines
- **CLI discoverability:** `report` CLI subcommand scaffolded for future report generation

### Changed
- Documentation refreshed for v0.10.7 (TASKS, AI context, next-session brief)

### Fixed
- Version references synced to v0.10.7 across Python, VBA, and docs

## [0.10.6] - 2025-12-28

### Added
- **W5 Structured Validation for Doubly/Flanged Beams:**
  - New error codes: `E_INPUT_010` (d_dash), `E_INPUT_011` (min_long_bar_dia)
  - New error codes: `E_INPUT_012-016` for flanged beam inputs (bw, bf, Df, constraints)
  - New error code: `E_FLEXURE_004` for d' too large in doubly reinforced design
  - Structured validation in `design_doubly_reinforced()` with error list
  - Structured validation in `design_flanged_beam()` with error list
  - Validation for d, fck, fy, min_long_bar_dia in `check_beam_ductility()`
  - 9 new tests for new error codes
- **Documentation:**
  - Solo maintainer operating system guide
  - Beginner learning path with exercises
  - Updated error-schema.md with new error codes

### Changed
- Improved CLI error messages for better user experience

### Fixed
- Error schema review findings (frozen dataclass, E_INPUT_003a, dynamic messages)

## [0.10.5] - 2025-12-28

### Added
- **Structured Error Schema (W03-W04):**
  - New `structural_lib/errors.py` module with `DesignError` dataclass and `Severity` enum
  - Machine-readable error codes: `E_INPUT_*`, `E_FLEXURE_*`, `E_SHEAR_*`, `E_DUCTILE_*`
  - Each error includes: code, severity, message, field (optional), hint (optional), clause (optional)
  - Pre-defined error constants for common validation failures
  - `to_dict()` method for JSON serialization
- **Error Schema Integration in Core Functions:**
  - `FlexureResult` and `ShearResult` now include `errors: List[DesignError]` field
  - `DuctileBeamResult` now includes `errors: List[DesignError]` field
  - `design_singly_reinforced()` returns structured errors for all validation failures
  - `design_shear()` returns structured errors for all validation failures
  - `check_beam_ductility()` returns structured errors for geometry failures
- **Error Schema Tests:**
  - New `tests/test_error_schema.py` with 29 tests covering:
    - DesignError dataclass structure and serialization
    - Severity enum values
    - Pre-defined error constants
    - Integration tests for flexure, shear, and ductile modules
    - Error code prefix conventions
- **Documentation:**
  - `docs/reference/error-schema.md` — Full error catalog with hints and clause references

### Changed
- `ductile.check_geometry()` now returns 3 values: `(valid, message, errors)`
- Existing `error_message` and `remarks` fields deprecated (use `errors` list instead)

## [0.10.4] - 2025-12-28

### Added
- **Session Automation Scripts:**
  - `scripts/start_session.py` — Run at session start (shows status, adds SESSION_LOG entry, lists active tasks)
  - `scripts/end_session.py` — Pre-handoff checks (uncommitted files, doc freshness, log completeness)
  - `scripts/check_handoff_ready.py` — Deep check of dates, test counts, version consistency
- **Nightly QA Workflow:**
  - `.github/workflows/nightly.yml` — Runs tests + full CLI smoke test (design → bbs → dxf → job)
  - Uploads artifacts and creates GitHub issue on failure
  - Scheduled for ~11:30pm IST daily
- **New Backlog Tasks:**
  - TASK-090: Publish JSON Schemas
  - TASK-091: CLI console script alias
  - TASK-092: Structured error payloads

### Changed
- **copilot-instructions.md:**
  - Added "Session workflow" section with start/end script usage
  - Consolidated handoff rules
- **.gitignore:**
  - Added `/docs/learning/` for private owner notes

## [0.10.3] - 2025-12-28

### Added
- **v0.20.0 Stabilization Sprint (PRs #89–93):**
  - Link checker script (`scripts/check_links.py`) — validates 173 internal links across 85 markdown files
  - Improved job_runner error messages for missing `code` and `schema_version` fields
- **Multi-Agent Repository Review (Phase 1+2):**
  - Branch coverage gate (`--cov-branch --cov-fail-under=85`) in CI
  - Pytest timeout (15 min) to prevent CI hangs
  - `.github/CODEOWNERS` file for review ownership
  - IS 456 Cl. 38.1 clause comment added to Mu_lim formula
  - Complete `design_shear()` docstring with Args/Returns/Units
  - `__all__` export list in `api.py` (8 public functions)
  - Golden vector source documentation (`tests/data/sources.md`)
  - Shear module section completed in `docs/reference/api.md`
  - Multi-agent review document (`docs/_internal/multi-agent-review-2025-12-28.md`)
- **Critical IS 456 Tests (45 new tests):**
  - Mu_lim boundary tests for all concrete grades
  - xu/d ratio limit tests (balanced section)
  - T-beam flange contribution tests
  - Shear strength boundary tests (Table 19)
  - Serviceability and detailing edge cases
  - Integration and determinism validation
- **Guardrails & Governance:**
  - Local CI parity script (`scripts/ci_local.sh`)
  - Doc version drift checker (`scripts/check_doc_versions.py`)
  - Pre-commit hooks documentation
  - Updated git-governance.md with accurate CI checks
  - AI agent workflow rules in `copilot-instructions.md`

### Changed
- **Documentation Polish:**
  - TASKS.md refactored (209→103 lines) — cleaner sections, current status
  - SESSION_LOG.md archived and cleaned (641→135 lines)
  - ai-context-pack.md reformatted with tables and clear sections
- **CLI Warning for Global Crack-Width Params:**
  - Emits warning when `--crack-width-params` is used with multiple beams
  - Alerts users that same parameters apply to all beams in batch
- **CI Workflow Standardization:**
  - Standardized GitHub Action versions to @v6 across all workflows
  - Removed duplicate doc version drift check

## [0.10.2] - 2025-12-28

### Added
- **CLI Serviceability Flags (PR #70):**
  - `--deflection` — Run Level A deflection check (span/depth ratio)
  - `--support-condition` — Set support condition (simply_supported, continuous, cantilever)
  - `--crack-width-params` — JSON file with crack width parameters
  - `--summary` — Write compact `design_summary.csv` alongside JSON output
- **Serviceability Status Fields:**
  - `deflection_status` and `crack_width_status` in schema (`not_run` | `ok` | `fail`)
  - Avoids ambiguous null values in JSON output
- **DXF Title Block Documentation:**
  - CLI reference updated with `--title-block` usage
  - Colab workflow guide with title block examples
- **New CLI Tests:**
  - 8 new tests for serviceability flags and error paths
  - Test coverage for summary CSV default path logic

### Changed
- CI coverage threshold temporarily lowered to 90% (from 92%)
- Getting-started docs simplified (beginners-guide, python-quickstart, excel-quickstart)
- Python/README.md updated with dev preview wording

### Fixed
- Mypy shadowing error in `__main__.py` (renamed loop variable)
- Version drift in README.md PyPI pin example

## [0.10.1] - 2025-12-27

### Changed
- Documentation improvements and synthetic batch example
- Bumped version references across 19 files

## [0.10.0] - 2025-12-27

### Added
- **Level B Serviceability (TASK-055):**
  - `check_deflection_level_b()` — Full curvature-based deflection per IS 456 Cl 23.2 / Annex C
  - `calculate_cracking_moment()` — Cracking moment $M_{cr}$
  - `calculate_gross_moment_of_inertia()` — $I_{gross} = bD^3/12$
  - `calculate_cracked_moment_of_inertia()` — $I_{cr}$ using transformed section
  - `calculate_effective_moment_of_inertia()` — Branson's equation for $I_{eff}$
  - `get_long_term_deflection_factor()` — Creep/shrinkage per Cl 23.2.1
  - `calculate_short_term_deflection()` — Elastic analysis
  - `DeflectionLevelBResult` dataclass for structured outputs
  - 16 new tests for Level B serviceability functions (1730 total tests)
- **CLI/AI Discoverability Sprint (TASK-069-072):**
  - `llms.txt` — AI-friendly summary for LLM tools and indexing
  - Enhanced CLI help text with examples and required args
  - CLI reference synced to canonical schema v1
  - Cross-links from README/docs to llms.txt
- **Release Automation Sprint (TASK-065-068):**
  - `scripts/release.py` — One-command release helper with version bump and checklist
  - `scripts/check_doc_versions.py` — Doc version drift detector with auto-fix
  - Enhanced `.pre-commit-config.yaml` with ruff linter, doc version check hooks
  - CI doc drift check step in `python-tests.yml`
- **API Stability Document:** `docs/reference/api-stability.md` — Defines stable vs internal APIs
- **Dedicated shear tests:** `tests/test_shear.py` with 22 unit tests for `calculate_tv` and `design_shear`

### Improved
- Added docstrings to 12 private helper functions in `serviceability.py` and `compliance.py`
- Added return type hints to 4 `api.py` convenience wrappers
- Test count increased to 1753 passed, 95 skipped

### Fixed
- Doc version drift: `docs/reference/api.md` version sync
- `bump_version.py`: Added `**Document Version:**` pattern and `--check-docs` flag

## [0.9.6] - 2025-12-27
### Added
- **Verification Examples Pack:** Appendix A (IS 456 derivations), Appendix B (runnable commands), Appendix C (textbook examples from Pillai & Menon, Krishna Raju, Varghese, SP:16).
- **Pre-release checklist:** Beta readiness gates with validation tracking.
- **API docs UX pass:** Comprehensive docstrings for all public API functions.

### Changed
- Fixed function signatures in examples.md (use `b=`, `d=` not `b_mm=`, `d_mm=`).
- Fixed `acr_mm` docstring (distance to bar surface, not area).
- CLI reference aligned with actual behavior.
- python-recipes.md aligned with real function signatures.

### Validated
- Singly reinforced beam: 0.14% Ast difference ✅
- Doubly reinforced beam: 0.06% Asc difference ✅
- Flanged beam (T-beam): exact match ✅
- High shear design: exact match ✅
- 5 textbook examples: all within 0.5% tolerance ✅

## [0.9.5] - 2025-12-27
### Added
- **Published to PyPI:** `pip install structural-lib-is456` now works.
- Automated publish workflow using Trusted Publishing (OIDC).
- GitHub Release auto-creation on version tags.

### Changed
- README updated with PyPI badge and simplified install instructions.
- `project.urls` added to pyproject.toml (Homepage, Docs, Changelog, Issues).
- **Docs restructure (6 phases):** Reorganized docs into 7 folders:
  - `getting-started/` — Quickstart guides (4 docs)
  - `reference/` — API, formulas, troubleshooting (4 docs)
  - `verification/` — Test examples, benchmarks (2 docs)
  - `contributing/` — Dev guides, testing strategy (5 docs)
  - `architecture/` — Project structure, design decisions (3 docs)
  - `planning/` — Roadmaps, research notes (5 docs)
  - `cookbook/` — Recipes and patterns (scaffold)
- Redirect stubs at old locations for backwards compatibility (will be removed in v1.0).

## [0.9.4] - 2025-12-26
### Added
- **Cutting-Stock Optimization (Python):** `optimize_cutting_stock()` function with first-fit-decreasing bin packing algorithm for minimizing rebar waste.
- **VBA BBS Module:** `M18_BBS.bas` — bar weight calculations, cut lengths, stirrup lengths, line item creation, summary aggregation.
- **VBA Compliance Checker:** `M19_Compliance.bas` — multi-check orchestration (flexure + shear + serviceability) with utilization ratios.
- VBA test suites: `Test_BBS.bas` (20 tests), `Test_Compliance.bas` (12 tests).
- New types: `BBSLineItem`, `BBSSummary` in `M02_Types.bas`.
- `CuttingPlan`, `CuttingAssignment` dataclasses in Python `types.py`.

### Changed
- Test runner now includes 9 suites (was 7).
- TASKS.md updated with priority completion status.

## [0.9.3] - 2025-12-26
### Added
- **Code Quality Sweep:** 14-task hardening across 5 phases.
- Edge case tests for `job_runner` (malformed JSON) and `dxf_export` (single beam, large grids).

### Fixed
- Input validation guards to prevent `ZeroDivisionError`:
  - `get_min_tension_steel_percentage` (fy=0)
  - `calculate_development_length` (tau_bd=0)
  - `get_xu_max_d` (fy<=0)
- VBA parity: added matching guards to `M05_Materials.bas` and `M10_Ductile.bas`.
- Exception handlers now log stack traces via `logging.exception()` while preserving graceful degradation.
- README import example fixed (`parse_etabs_export` → `load_beam_data_from_csv`).
- DXF layout: row height calculation, column width sizing, geometry overlap assertions.

## [0.9.1] - 2025-12-25
### Changed
- CI policy: coverage floor enforced at `--cov-fail-under=92` (temporary).
- Docs: refreshed onboarding/quickstart and version pins; clarified batch runner + DXF usage.

### Fixed
- Robustness regressions from findings audit (flexure flanged-beam max-steel check, detailing spacing validation, compliance utilization semantics, serviceability input normalization).

## [0.9.0] - 2025-12-19
### Added
- **Stable public API (IS456):** explicit entrypoints designed for future multi-code support.
- **Golden vectors:** pinned regression targets for key IS456 cases.
- **Deterministic automation runner:** job schema + batch runner + CLI producing JSON/CSV outputs.

### Changed
- Compliance report dict export hardened so results are JSON-serializable.

## [0.8.2] - 2025-12-16
### Changed
- **Robustness + CI (no design algorithm changes):**
  - Compliance checker hardened against malformed serviceability inputs; deterministic governing-case utilization in failure modes.
  - DXF export optional dependency surface made more monkeypatch/type-check friendly.
  - CI reliability fix: raise total coverage above the enforced `--cov-fail-under=92` gate.

## [0.8.1] - 2025-12-16
### Changed
- **Packaging/CI tooling (no engineering behavior changes):**
  - Remove `setup.cfg` metadata duplication (single source of truth in `pyproject.toml`).
  - Add `ruff` to dev extras and run `ruff check` in CI.
  - Strengthen CI packaging smoke test to install the built wheel and import `structural_lib`.
  - Add `Python/scripts/pre_release_check.sh` for local release gating.

## [0.8.0] - 2025-12-15
### Added
- **Serviceability (Level A)**:
  - Python: deflection check (span/depth with explicit modifiers) and crack width estimate (Annex-F-style), returning auditable result payloads.
  - VBA parity: serviceability module + types + test harness.
- **Compliance Checker**:
  - Python: multi-case orchestrator across flexure + shear (+ optional serviceability), deterministic governing-case selection, and Excel-friendly summary row.

### Documentation
- Updated API reference and task board to reflect the new modules.

## [0.7.1] - 2025-12-15
### Added
 - **Python Testing**:
   - DXF export smoke test (generate + read-back).
   - Materials/Tables edge-case tests.
   - CI installs optional DXF dependencies (`.[dev,dxf]`) so DXF tests run in Actions.
   - Extensive branch/edge coverage additions across integration, DXF, flexure, shear, tables, and materials.
### Changed
- **CI**:
  - Raised Python coverage floor to `--cov-fail-under=92`.

### Fixed
- **Excel Integration**:
  - `generate_detailing_schedule()` no longer fails when only one bottom bar arrangement exists.
  - `BeamDesignData.from_dict()` now deterministically handles `d` vs `D` key collisions (legacy lowercase `d` won’t override an explicit `D`).
- **Tables**:
  - Simplified `get_tc_value()` grade selection loop without changing behavior (removes an effectively-unreachable branch).

- **Python Packaging**:
  - Include `structural_lib/py.typed` in built distributions (PEP 561).

- **VBA DXF Export Module (`M16_DXF.bas`)**:
  - Native DXF R12 format writer (no external dependencies).
  - `Draw_BeamSection`: Beam cross-section with rebar arrangement.
  - `Draw_BeamLongitudinal`: Longitudinal section with stirrup spacing.
  - `Draw_BeamDetailing`: Complete detailing drawing with bar schedule.
  - DXF primitives: `DXF_Line`, `DXF_Circle`, `DXF_Arc`, `DXF_Text`, `DXF_Rectangle`.
  - Structural components: `DXF_Stirrup`, `DXF_RebarSection`, `DXF_Dimension`.
  - Professional CAD layer system with proper colors and linetypes.
- **DXF UDFs (M09_UDFs)**:
  - `IS456_DrawSection`: Generate section DXF from worksheet.
  - `IS456_DrawLongitudinal`: Generate longitudinal DXF.
  - `IS456_ExportBeamDXF`: One-click macro for beam drawing export.
- **Test Coverage**:
  - `Test_DXF.bas`: 21 test cases for DXF module.
  - `Generate_Sample_DXF`: Visual verification utility.

### CAD Layer Standards (M16_DXF)
| Layer | Color | Purpose |
|-------|-------|---------|
| BEAM_OUTLINE | Cyan (4) | Section boundary |
| REBAR_MAIN | Red (1) | Main bars |
| REBAR_STIRRUP | Green (3) | Stirrups |
| DIMENSIONS | Yellow (2) | Dim lines |
| TEXT_CALLOUT | White (7) | Labels |
| CENTERLINE | Magenta (6) | Center lines |
| COVER_LINE | Blue (5) | Cover indication |

## [0.7.0] - 2025-12-11
### Added
- **Reinforcement Detailing Module (`detailing.py`)**:
  - `calculate_development_length`: IS 456 Cl 26.2.1 Ld calculation with bond stress lookup.
  - `calculate_lap_length`: Lap splice length with zone multipliers (1.5× tension).
  - `calculate_bar_spacing`: Center-to-center spacing calculation.
  - `check_min_spacing`: IS 456 Cl 26.3.2 validation (≥ max(bar_dia, agg+5, 25mm)).
  - `select_bar_arrangement`: Practical bar selection from standard diameters.
  - `calculate_stirrup_legs`: Determines 2L/4L/6L based on beam width.
  - `create_beam_detailing`: Complete beam detailing from design output.
  - Data classes: `BarArrangement`, `StirrupArrangement`, `BeamDetailingResult`.
- **DXF Export Module (`dxf_export.py`)**:
  - `generate_beam_dxf`: Creates DXF R2010 drawing from detailing result.
  - `draw_beam_elevation`: Elevation view with reinforcement.
  - `draw_beam_section`: Cross-section view at specified location.
  - `draw_dimensions`: Automatic dimensioning.
  - `draw_annotations`: Bar callouts (e.g., "3-20φ BOT").
  - Layer system: BEAM_OUTLINE, REBAR_MAIN, REBAR_STIRRUP, DIMENSIONS, TEXT.
  - Optional dependency: `ezdxf` library.
- **Excel Integration Module (`excel_integration.py`)**:
  - `BeamDesignData`: Dataclass for parsing beam design rows.
  - `load_beam_data_from_csv`: Flexible CSV parser with key normalization.
  - `load_beam_data_from_json`: JSON parser supporting both array and object formats.
  - `process_single_beam`: Generate detailing + optional DXF for one beam.
  - `batch_generate_dxf`: Batch processing with progress tracking.
  - `generate_summary_report`: Text report of batch results.
  - `generate_detailing_schedule`: Export detailing to CSV schedule format.
  - CLI entry point: `python -m structural_lib.excel_integration`.
- **Documentation**:
  - `docs/specs/v0.7-data-mapping.md`: Complete data flow specification.
  - `docs/specs/v0.7-requirements.md`: CLIENT requirements for detailing.
  - `docs/research-detailing.md`: IS 456/SP 34 detailing research.
  - `docs/_internal/agent-workflow.md`: Multi-agent governance system.
- **Test Coverage**:
  - `test_detailing.py`: 31 tests for detailing module.
  - `test_excel_integration.py`: 15 tests for integration module.
  - Total: 67 tests passing.

### Technical Details
- Bond stress table: M15-M50 grades with 60% increase for deformed bars.
- Standard bar diameters: 8, 10, 12, 16, 20, 25, 32 mm.
- DXF output: 1:1 scale (mm units), R2010 format for compatibility.

## [0.6.0] - 2025-12-11
### Added
- **ETABS Integration (`M13_Integration.bas`)**:
  - `Import_ETABS_Data`: Mac/Windows file picker with fallback to sample data.
  - `Process_ETABS_CSV`: Robust CSV parser handling quoted values and header aliases.
  - `Generate_Sample_ETABS_CSV`: Creates sample ETABS-style CSV for testing.
  - Dictionary-based grouping for unsorted CSV input.
  - Bucket aggregation (Start 0-20%, Mid 20-80%, End 80-100%) with sign preservation.
- **Beam Schedule Generation (`M14_Reporting.bas`)**:
  - `Generate_Beam_Schedule`: Transforms design output to drafting-ready format.
  - Dynamic column lookup for robustness against schema changes.
  - Auto-sorting by Story/ID before grouping.
  - `Get_Bar_Pattern`: Converts steel area to practical bar notation (e.g., "3-16").
- **Governance Documentation**:
  - `docs/_internal/git-governance.md`: Branching, commits, versioning, release process.
  - `docs/mission-and-principles.md`: Project philosophy and design principles.
- **Test Fixtures**:
  - `Python/examples/ETABS_BeamForces_Example.csv`: Sample ETABS export.

### Changed
- Integration test harness (`Integration_TestHarness.bas`) to auto-populate BEAM_INPUT and run end-to-end design scenarios.
- Application layer now computes effective/compression covers from clear cover + bar/stirrup inputs.

## [0.5.0] - 2025-12-11
### Added
- **Excel Integration**:
  - `M11_AppLayer.bas`: Application controller linking Excel Tables to Core Library.
  - `M12_UI.bas`: UI event handlers for "Run Design" and "Clear Results".
  - `M99_Setup.bas`: Scaffolding script to generate the v0.5 Workbook structure.
- **Governance**:
  - Added `DOCS`, `INTEGRATION`, and `SUPPORT` agent roles.
  - Formalized Feature/Bug/Release workflows in `pm.md` and `project-overview.md`.
- **Documentation**:
  - Added `docs/specs/v0.5-excel-spec.md`.
  - Updated `excel-addin-guide.md` with dynamic path handling.

## [0.4.0] - 2025-12-11
### Added
- **Ductile Detailing (IS 13920:2016)**:
  - `M10_Ductile.bas` / `ductile.py`: Implemented ductile detailing checks.
  - Geometry checks: `b >= 200`, `b/D >= 0.3`.
  - Reinforcement checks: Min/Max tension steel ratios per Cl 6.2.
  - Confinement: Hoop spacing calculations per Cl 6.3.5.
- **Packaging**:
  - Python: Added `pyproject.toml`, `setup.cfg`, and build artifacts.
  - Excel: Added `StructEngLib.xlam` add-in support.
  - UDFs: Added `IS456_Check_Ductility` to `M09_UDFs.bas`.
- **Documentation**:
  - Updated `api-reference.md` to v0.4.0.
  - Completed `TASKS.md` for v0.4 scope.

## [0.3.0] - 2025-12-11
### Added (VBA & Python)
- **Flanged Beam Design (T/L Beams)**:
  - `Calculate_Mu_Lim_Flanged` / `calculate_mu_lim_flanged`: Calculates limiting moment for T-sections.
  - `Design_Flanged_Beam` / `design_flanged_beam`: Handles Neutral Axis in Flange, Web (Singly), and Web (Doubly).
  - `Test_Flanged.bas` / `test_flanged_beam.py`: Comprehensive unit tests for all three cases.

## [0.2.1] - 2025-12-11
### Fixed (Mac VBA Compatibility)
- **Stack Corruption:** Fixed `Runtime Error 6: Overflow` caused by passing inline boolean expressions to subroutines.
- **Integer Overflow:** Wrapped all dimension multiplications in `CDbl()` within library modules.
- **UDT Stability:** Removed nested UDT returns in `Design_Doubly_Reinforced` to prevent stack corruption.
- **Test Harness:** Refactored `Test_Structural.bas` to use the "Safe Assertion Pattern" and deferred `Debug.Print`.

## [0.2.0] - 2025-12-11
### Added
- **Doubly Reinforced Beam Design**:
  - `design_doubly_reinforced`: Logic to handle `Mu > Mu_lim` by adding compression steel.
  - `get_steel_stress`: Non-linear stress-strain curve implementation for Fe415/Fe500 (IS 456 Figure 23).
  - Updated `FlexureResult` to include `asc_required`.

## [0.1.0] - 2025-12-10
### Added
- **Core Flexure Module**:
  - Singly reinforced rectangular beam design (`design_singly_reinforced`).
  - Limiting moment calculation (`calculate_mu_lim`).
  - Steel area calculation (`calculate_ast_required`).
- **Shear Module**:
  - Shear capacity calculation (`calculate_shear_capacity`).
  - Stirrup design (`design_shear_reinforcement`).
  - Table 19 (Tc) and Table 20 (Tc_max) lookups.
- **Infrastructure**:
  - Dual implementation in Python and VBA.
  - Unit tests for Python (`pytest`).
  - Documentation structure (`api-reference.md`, `TASKS.md`).
  - Excel add-in guide (`excel-addin-guide.md`).

---

Format: Keep a section per release with Added/Changed/Fixed as needed. Tag releases as `vX.Y.Z`.

[Unreleased]: https://github.com/AravindanVasudeworthy/structural_engineering_lib/compare/v0.21.6...HEAD
[0.21.6]: https://github.com/AravindanVasudeworthy/structural_engineering_lib/compare/v0.21.5...v0.21.6
[0.21.4]: https://github.com/Pravin-surawase/structural_engineering_lib/compare/v0.21.3...v0.21.4
