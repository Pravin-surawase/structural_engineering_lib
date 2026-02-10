# Release Ledger

**Type:** Reference
**Audience:** Maintainers
**Status:** Approved
**Importance:** Critical
**Version:** 1.0.0
**Created:** 2025-12-01
**Last Updated:** 2026-01-21

---

This document serves as the **immutable source of truth** for project releases.
Entries here represent "locked" versions that have been verified and approved.
**Rule:** Agents may ONLY append to this file. Never edit or delete past entries.

---

## Release Process

### For maintainers: How to publish a new release

1. **Update version** in 3 files:
   - `Python/pyproject.toml` → `version = "X.Y.Z"`
   - `Python/structural_lib/api.py` → `__version__ = "X.Y.Z"`
   - `VBA/Modules/M08_API.bas` → `VERSION = "X.Y.Z"`

2. **Update CHANGELOG.md** with release notes

3. **Create and push tag:**
   - Create an annotated tag `vX.Y.Z`
   - Push the tag to origin (maintainer-only, use the release workflow checklist)

4. **Automatic publishing:**
   - GitHub Actions builds wheel + sdist
   - Publishes to PyPI via Trusted Publishing
   - Creates GitHub Release with assets

5. **Verify installation:**
   ```bash
   pip install structural-lib-is456==X.Y.Z
   python -c "from structural_lib import api; print(api.get_library_version())"
   ```

6. **Recommended: clean-venv verification**
   ```bash
   .venv/bin/python scripts/release.py verify --version X.Y.Z --source pypi
   ```

### TestPyPI (for testing before release)

Use workflow_dispatch with `testpypi` target:
1. Go to Actions → Publish to PyPI → Run workflow
2. Select `testpypi` and run
3. Test: `pip install -i https://test.pypi.org/simple/ structural-lib-is456`

---

## v0.17.0
**Date:** 2026-01-13
**Status:** ✅ Locked & Verified
**Mindset:** Professional API Features + Debug Infrastructure + Documentation Excellence
**Commits:** `a2587da` (Phase 1+2), `70da224` (IMP-02/03), `87c137f` (fixes), `234ac4b` (release), `d1610ff` (docs)

**Key Changes:**

**Added - Professional API Features:**
- `BeamInput` dataclasses for flexible input handling (TASK-276)
- Professional calculation report generation module (TASK-277)
- Verification and audit trail module for compliance tracking (TASK-278)
- Engineering testing strategies module with benchmark framework (TASK-279)

**Added - Debug & Diagnostics Infrastructure:**
- `scripts/collect_diagnostics.py` - Creates timestamped diagnostic bundles (5 min → 10 sec)
- `scripts/generate_api_manifest.py` - Generates/validates API manifest with 38 public symbols
- `scripts/check_scripts_index.py` - Validates scripts/index.json accuracy (128 scripts)
- `docs/reference/api-manifest.json` - Complete API surface documentation
- Diagnostics reminders in `agent_start.sh` and `end_session.py`
- Debug snapshot checklist in handoff documentation

**Added - Documentation Metadata System (TASK-458):**
- Added metadata headers to 50+ documentation files
- `scripts/create_doc.py` - Creates new docs with proper metadata
- `scripts/check_doc_metadata.py` - Validates metadata in pre-commit
- Standardized Type, Audience, Status, Importance, Version fields

**Added - Documentation Consolidation (TASK-457):**
- Archived 91 session/task docs from streamlit_app/docs (98% reduction: 93 → 2 files)
- Archived 26 completed research files with 180 link fixes
- `scripts/consolidate_docs.py` - Improved consolidation workflow
- Reduced documentation sprawl significantly

**Changed - Git Workflow Automation:**
- Added enforcement hook blocking manual git commands
- Improved error clarity with 'why' and recovery guidance
- Policy-aware merge with `--force` mode for batched commits
- Removed manual git examples from active documentation

**Changed - Pre-commit Hooks:**
- Added API manifest validation hook
- Added scripts index validation hook
- Added doc metadata check (warning mode)
- Skip research folder in filename validation

**Fixed:**
- Streamlit import checker: added `--skip-known` flag to reduce false positives
- CI: skip research folder in filename validation for legacy naming
- Fixed invalid 'local' keyword in `finish_task_pr.sh`
- Pre-commit whitespace and line ending fixes across 15 files
- Ruff UP038 fixes in test files (use `X | Y` in isinstance)

**Impact Metrics:**
- Diagnostics collection: 5 min → 10 sec (96% faster)
- API breakage detection: Post-CI → Pre-commit (earlier)
- Documentation: 50+ files with metadata, 91 files archived
- All 2598 tests passing
- 128 automation scripts indexed
- 38 public API symbols tracked

---

## v0.16.6
**Date:** 2026-01-12
**Status:** ✅ Locked & Verified
**Mindset:** Python 3.11 Baseline - Modern Python, faster CI, cleaner codebase
**Key Changes:**
- **Python 3.11 Baseline:** Minimum Python version raised from 3.9 to 3.11
- **CI Optimization:** Test matrix reduced from 4 versions to 2 (50% faster CI)
- **Type Hint Modernization:** PEP 604 syntax (`X | None` instead of `Optional[X]`)
- **Pre-commit Updates:** All local hooks use `.venv/bin/python` for 3.11 compatibility

**Developer Requirements:**
- Python 3.11+ required locally (`brew install python@3.11` on macOS)
- Virtual environment should be recreated with Python 3.11

**New Scripts:**
- `scripts/check_python_version.py` - Validates Python version consistency across project
- `scripts/add_future_annotations.py` - Helper to add `from __future__ import annotations`

**Tests:** 2430 passing on Python 3.11

---

## v0.17.5
**Date:** 2026-01-14
**Status:** ✅ Locked & Verified
**Mindset:** Multi-Objective Optimization + API Validation
**Tag:** v0.17.5

**Key Changes:**
- NSGA-II multi-objective optimizer for Pareto-optimal beam designs
- Cost optimizer UI enhancements with Pareto scatter + best-by-objective views
- API signature validation in pre-commit + CI
- Added optimizer tests for non-dominated sorting + crowding distance

**Tests:** 1317 passing (per tag notes)

---

## v0.16.5
**Date:** 2026-01-11
**Status:** ✅ Locked & Verified
**Mindset:** Developer Experience & Automation - Workflow efficiency and multi-code foundation
**Key Changes:**
- **Unified Agent Onboarding:** Single `./scripts/agent_start.sh` command replaces 4-command workflow (90% faster)
- **Folder Structure Governance:** 115 validation errors → 0, CI-enforced folder limits, comprehensive V2.0 spec
- **Git Workflow Automation:** 90-95% faster commits (45-60s → 5s), parallel fetch, incremental whitespace checks
- **Multi-Code Foundation:** New `core/` and `codes/` architecture ready for ACI 318/EC2 support
- **IS 456 Module Migration:** All 7 modules reorganized under `codes/is456/` (3,048 lines, zero breaking changes)
- **Documentation Quality:** 789 internal links validated, zero orphan files, semantic READMEs in all folders
- **103 Automation Scripts:** Safe file operations, link validation, governance compliance, migration tools

**New Infrastructure:**
- `scripts/agent_start.sh` (164 lines) - Unified onboarding replacing 4 commands
- `docs/guidelines/folder-structure-governance.md` (272 lines) - V2.0 governance spec
- `scripts/safe_file_move.py` (200+ lines) - Automated link-safe file operations
- `scripts/check_governance.py` - CI-enforced folder validation
- `Python/structural_lib/core/` - Code-agnostic base modules (geometry, materials)
- `Python/structural_lib/codes/is456/` - IS 456 module namespace (7 modules)

**Tests:** 2392 passed (all categories), maintained 86% coverage
**Commits:** ~25 commits across 7 session parts
**PRs:** #323, #326, #327, #328, #329, #330

**Impact:**
- Agent onboarding: 4 commands → 1, ~30s → ~3s (90% faster)
- Commit speed: 45-60s → 5s (90-95% improvement)
- Documentation: Zero broken links (789 validated)
- Folder hygiene: Root files 14 → 9 (below CI limit of 10)
- Multi-code ready: Foundation for ACI 318/EC2 support
- Repository health: 115 governance issues → 0

---

## v0.16.0
**Date:** 2026-01-08
**Status:** ✅ Locked & Verified
**Mindset:** Streamlit UI Excellence + API Convenience
**Key Changes:**
- **Streamlit UI Phase 2 Complete:** Dark mode (theme_manager.py), loading states (loading_states.py), chart enhancements (plotly_enhancements.py)
- **API Convenience Layer:** `design_and_detail_beam_is456()`, `generate_summary_table()`, `quick_dxf()`, `quick_dxf_bytes()`
- **UI Component Testing:** 70+ new tests for theme management, loading states, and visualizations
- **Developer Experience:** One-liner functions for common Streamlit integration patterns
- **Serialization Support:** `to_dict()`, `from_dict()`, `to_json()` methods on `DesignAndDetailResult`
- **Repository Hygiene:** Cleaned up 3 merged worktrees and remote branches

**New Files:**
- `streamlit_app/utils/theme_manager.py` (325 lines) - Dark mode with session persistence
- `streamlit_app/utils/loading_states.py` (494 lines) - Professional loading animations
- `streamlit_app/utils/plotly_enhancements.py` (383 lines) - Chart theme integration
- `streamlit_app/tests/test_theme_manager.py` (278 lines, 20+ tests)
- `streamlit_app/tests/test_loading_states.py` (407 lines, 40+ tests)
- `streamlit_app/tests/test_plotly_enhancements.py` (350 lines, 30+ tests)

**Tests:** 2370+ passed (includes 70+ new UI tests, 16 API convenience tests)
**PRs:** #286 (API convenience), #287 (UI-003/004/005)

**Impact:**
- Professional dark mode UX with accessibility compliance (WCAG 2.1 AA)
- Enhanced developer productivity with convenience API functions
- Improved Streamlit integration patterns (one-liners for common tasks)
- Complete UI modernization foundation (UI-001 through UI-005 done)
- Ready for Phase 3 feature expansion

---

## v0.15.0
**Date:** 2026-01-07
**Status:** ✅ Locked & Verified
**Mindset:** Code Quality Excellence — Enterprise-grade standards with comprehensive tooling
**Key Changes:**
- **License Compliance:** SPDX headers on all 73 files (100% coverage)
- **Type Safety:** PEP 585/604 modernization (398 issues resolved), `disallow_untyped_defs` enabled
- **Code Quality:** Zero ruff errors (down from 91), 9 linting rule categories
- **Test Organization:** 5-category structure (unit/integration/regression/property/performance), 2270 tests
- **Performance Tracking:** 13 benchmarks baseline established with pytest-benchmark
- **Documentation:** Complete docstrings for api.py + core modules, architecture diagrams, 450+ page automation catalog
- **Smart Features:** SmartDesigner unified dashboard, multi-design comparison, cost-aware sensitivity
- **Git Workflow:** PR-first enforcement, audit logging, comprehensive testing suite
- **TypedDicts Phase 1:** BarDict and StirrupDict for type-safe reinforcement data

**Tests:** 2270 passed (all categories), 13 benchmarks
**Coverage:** 86% (6 modules >90%, 8 modules 80-90%)
**PRs:** #256-#276, #263-#273

**Impact:**
- Industry-leading code quality (0 lint errors, modern type hints, 100% license compliance)
- Professional test infrastructure (organized, benchmarked, comprehensive)
- Enhanced developer experience (complete docs, automated workflows, clear standards)
- Advanced design intelligence (smart analysis, comparison tools)
- v1.0-ready foundation (deprecation policy, type safety, contract testing)

---

## v0.14.0
**Date:** 2026-01-06
**Status:** ✅ Locked & Verified
**Mindset:** Foundation Hardening — Professional-grade engineering practices
**Key Changes:**
- **Contract testing:** Prevents accidental API breaking changes (6 tests protecting API surface)
- **Validation utilities:** 8 reusable validators reducing code duplication by ~30%
- **Deprecation policy:** Safe evolution with `@deprecated` decorator following NumPy/pandas patterns
- **Error handling:** 5-layer architecture documented in CONTRIBUTING.md, 17 silent failures eliminated
- **Type safety:** Stricter mypy checks (`warn_return_any`, `strict_optional`, `warn_redundant_casts`)
- **Research documentation:** 5 comprehensive reports (5,800+ lines) covering CS best practices, backward compatibility, modern tooling, implementation roadmap, and VBA deprecation strategy
- **Git workflow:** Pull-first workflow and pre-commit hooks prevent merge conflicts
- **Test improvements:** 2200 tests (+160), 86% coverage (+2%), 10 modules at 100% coverage

**Tests:** 2269 passed (up from 2200)
**Coverage:** 86% (up from 84%)
**PRs:** #247, #248, #249, #250

**Impact:**
- Eliminates fear of AI agents breaking existing code (contract tests)
- Professional-grade error handling and validation patterns
- Foundation now ready for v1.0 with safe deprecation path
- Addresses CS knowledge gaps with comprehensive research

---

## v0.13.0
**Date:** 2025-12-31
**Status:** ✅ Locked & Verified
**Mindset:** Insights Foundation — Advisory intelligence for beam design
**Key Changes:**
- **Insights module:** Complete `structural_lib.insights` package with three advisory features:
  - `quick_precheck()` — Heuristic validation before full design (~1ms)
  - `sensitivity_analysis()` — Identify critical parameters and robustness scoring
  - `calculate_constructability_score()` — Ease of construction assessment (0-100 scale)
- **CLI integration:** New `--insights` flag for `design` command exports insights to JSON
- **Verification pack:** 10 benchmark cases with JSON-driven parametrized tests
- **Documentation:** User guide, API reference, and Colab examples for all insights features
- **Side-face reinforcement:** IS 456 Cl 26.5.1.3 check for beams with D > 750mm

**Tests:** 2200 passed
**PRs:** #224, #226, #230, #233, #234, #235, #236

---

## v0.12.0
**Date:** 2025-12-30
**Status:** ✅ Locked & Verified
**Mindset:** Library-First API Expansion + DXF/BBS Quality
**Key Changes:**
- **Library-first APIs:** `validate_*`, `compute_detailing`, `compute_bbs`, `export_bbs`, `compute_dxf`, `compute_report`, `compute_critical`.
- **New CLI helpers:** `validate` and `detail` subcommands for schema checks and detailing JSON export.
- **DXF/BBS quality:** bar mark consistency checks, DXF content tests, title block context, render workflow.
- **Docs & examples:** README + Colab workflow refreshed for report/critical/detail usage.

**Tests:** 1958 passed, 91 skipped
**PRs:** #193, #194, #195, #196

## v0.11.0
**Date:** 2025-12-29
**Status:** ✅ Locked & Verified
**Mindset:** Visual v0.11 Complete (Reports + Packaging)
**Key Changes:**
- **V04–V07 HTML report visuals:** Cross-section SVG, input sanity heatmap, stability scorecard, units sentinel.
- **V08 batch packaging:** `report` supports `design_results.json` and `--batch-threshold` for folder output.
- **V09 golden fixtures:** Deterministic HTML outputs locked by golden-file tests.
- **Docs:** README, Colab workflow, and API reference updated for report/critical usage.

**Tests:** 1958 passed, 91 skipped
**PRs:** #151, #153, #154, #155, #156

---

## v0.10.7
**Date:** 2025-12-29
**Status:** ✅ Locked & Verified
**Mindset:** Visual Layer Phase 1 (Critical Set)
**Key Changes:**
- **Critical Set CLI (V03):** New `critical` subcommand exports sorted utilization tables (CSV/HTML) with `--top` filter and `data-source` traces for auditability.
- **Report foundations:** `report.py` skeleton + `load_job_spec()` helper underpin report pipelines.
- **CLI discoverability:** `report` subcommand scaffold added ahead of SVG/report deliverables.
- **Docs:** AI context, TASKS, next-session brief refreshed for v0.10.7.

**PRs:** #147

---

## v0.10.6
**Date:** 2025-12-28
**Status:** ✅ Locked & Verified
**Mindset:** Complete Structured Validation
**Key Changes:**
- **W5 Structured Validation:**
  - New error codes: `E_INPUT_010-016` for d_dash, min_long_bar_dia, and flanged beam inputs
  - New `E_FLEXURE_004` for d' too large in doubly reinforced design
  - Structured validation in `design_doubly_reinforced()` and `design_flanged_beam()`
  - Validation in `check_beam_ductility()` for d, fck, fy, min_long_bar_dia
- **Docs:** Solo maintainer guide, beginner learning path, improved error schema docs
- **CLI:** Improved error messages

**Note:** v0.10.5 was not published to PyPI. This release includes all v0.10.5 changes.

**PRs:** #81, #94, #112, #113, #114, #115

---

## v0.10.5
**Date:** 2025-12-28
**Status:** ✅ Locked & Verified
**Mindset:** Structured Error Schema
**Key Changes:**
- **New errors.py module:** `DesignError` dataclass with code/severity/message/field/hint/clause
- **Core integration:** Structured errors in `design_singly_reinforced()`, `design_shear()`, `check_beam_ductility()`
- **FlexureResult/ShearResult/DuctileBeamResult:** Added `errors: List[DesignError]` field
- **29 new tests:** Comprehensive error schema validation
- **Error catalog:** 20+ error codes with hints and IS 456 clause references

**Breaking Changes:**
- `ductile.check_geometry()` now returns 3 values: `(valid, message, errors)`

**PRs:** #106, #107, #108, #109, #110, #111, #112

---

## v0.10.4
**Date:** 2025-12-28
**Status:** ✅ Locked & Verified
**Mindset:** Developer Automation & Nightly QA
**Key Changes:**
- **Session Automation:**
  - `start_session.py` — Shows status, adds SESSION_LOG entry, lists active tasks
  - `end_session.py` — Pre-handoff checks (uncommitted files, doc freshness, log completeness)
  - `check_handoff_ready.py` — Deep doc freshness validation
- **Nightly QA Workflow:**
  - Full test suite + CLI smoke test (design → bbs → dxf → job)
  - Artifact upload + auto-issue on failure
  - Scheduled 11:30pm IST daily
- **Docs & Tasks:**
  - Updated copilot-instructions with session workflow
  - Added TASK-090/091/092 to backlog
  - Private `/docs/learning/` gitignored
**Tests:** 1958 passed, 91 skipped
**Coverage:** 92% branch

---

## v0.10.3
**Date:** 2025-12-28
**Status:** ✅ Locked & Verified
**Mindset:** Multi-Agent Review Phase 1+2 + CI Improvements
**Key Changes:**
- **Multi-Agent Repository Review:**
  - Branch coverage gate (`--cov-branch --cov-fail-under=85`)
  - Pytest timeout (15 min)
  - CODEOWNERS file added
  - IS 456 Cl. 38.1 clause comment for Mu_lim formula
  - `design_shear()` docstring complete
  - `__all__` export list in api.py
  - Golden vector source documentation
  - Shear section complete in api.md
  - Review document at `docs/_internal/multi-agent-review-2025-12-28.md`
- **CLI Warning:** Warns when `--crack-width-params` used with multiple beams
- **CI Standardization:** GitHub Actions versions unified to @v6
- **Documentation Polish:** TASKS.md, SESSION_LOG.md, ai-context-pack.md cleaned and reformatted

**Test Results:** 1958 passed, 91 skipped
**PyPI:** `pip install structural-lib-is456==0.10.3`

---

## v0.10.2
**Date:** 2025-12-28
**Status:** ✅ Locked & Verified
**Mindset:** CLI Serviceability + DXF Title Block + Documentation Polish
**Key Changes:**
- **CLI Serviceability Flags (PR #70):**
  - `--deflection` — Level A deflection check (span/depth)
  - `--support-condition` — Support condition option
  - `--crack-width-params` — JSON file for crack width parameters
  - `--summary` — Compact CSV summary output
- **Schema Improvements:**
  - `deflection_status` and `crack_width_status` fields (`not_run` | `ok` | `fail`)
- **DXF Title Block Documentation:**
  - `--title-block` usage documented in CLI reference
- **Getting-Started Simplification:**
  - beginners-guide.md reduced from 631 to 137 lines
  - Python/README.md with dev preview wording
- **New Tests:** 8 CLI tests for serviceability and error paths
- **CI:** Coverage threshold lowered to 90%

**Test Results:** 1760+ passed, 91 skipped
**PyPI:** `pip install structural-lib-is456==0.10.2`

---

## v0.10.1
**Date:** 2025-12-27
**Status:** ✅ Locked & Verified
**Mindset:** Documentation improvements and version sync
**Key Changes:**
- Bumped version references across 19 files
- Fixed README.md PyPI pin example

---

## v0.10.0
**Date:** 2025-12-27
**Status:** ✅ Locked & Verified
**Mindset:** Level B Serviceability + AI/CLI Discoverability + Release Automation
**Key Changes:**
- **Level B Serviceability (TASK-055):** Full curvature-based deflection per IS 456 Cl 23.2 / Annex C
  - 7 new functions: cracking moment, gross/cracked/effective MOI, long-term factor, short-term deflection
  - `DeflectionLevelBResult` dataclass for structured outputs
- **CLI/AI Discoverability (TASK-069-072):**
  - `llms.txt` — AI-friendly summary for LLM tools
  - Enhanced CLI help text with examples
  - CLI reference synced to canonical schema v1
- **Release Automation (TASK-065-068):**
  - `scripts/release.py` — One-command release helper
  - `scripts/check_doc_versions.py` — Doc version drift detector
  - CI doc drift check step
- **Tests:** 1958 passed, 95 skipped

---

## v0.9.6
**Date:** 2025-12-27
**Status:** ✅ Locked & Verified
**Mindset:** Verification examples + API docs UX + Pre-release checklist

---

## v0.9.5
**Date:** 2025-12-27
**Status:** ✅ Locked & Verified
**Mindset:** PyPI launch + docs restructure + release automation
**Key Changes:**
- **Published to PyPI:** Trusted Publishing (OIDC) with GitHub Release auto-creation.
- **Docs restructure:** 7 folders (getting-started, reference, verification, contributing, architecture, planning, cookbook).
- **Project metadata:** `project.urls` added to `pyproject.toml`.

---

## v0.9.4
**Date:** 2025-12-27
**Status:** ✅ Locked & Verified
**Mindset:** Unified CLI + VBA parity + Cutting-stock optimizer
**Key Changes:**
- **Unified CLI:** `python -m structural_lib design|bbs|dxf|job`
- **Cutting-Stock Optimizer:** First-fit-decreasing bin packing for rebar nesting
- **VBA BBS Module:** `M18_BBS.bas` — bar weights, cut lengths, stirrup lengths
- **VBA Compliance Module:** `M19_Compliance.bas` — multi-check orchestration
- **Tests:** 1680+ passed, 9 VBA test suites
- **Docs:** Professional README with pipeline diagram, trust section

---

## v0.9.3
**Date:** 2025-12-26
**Status:** ✅ Locked & Verified
**Mindset:** Code quality hardening before feature expansion.
**Key Changes:**
- **Code Quality Sweep:** 14 targeted fixes across 5 phases:
  - Phase 1: Input validation guards (ZeroDivisionError prevention)
  - Phase 2: Logging for stack trace preservation
  - Phase 3: VBA/Python parity verified + VBA guards added
  - Phase 4: API/doc drift fixed
  - Phase 5: Edge case tests for job_runner and dxf_export
- **Tests:** 1958 passed, 93 skipped
- **VBA:** Guards added to M05_Materials.bas and M10_Ductile.bas

---

## v0.7.0
**Date:** 2025-12-11
**Status:** ✅ Locked & Verified
**Commit Hash:** 8f64d93
**Mindset:** Transitioning from "Usability" (v0.6) to "Deliverables" (v0.7).
*   **Detailing:** Pure-function calculations for IS 456 reinforcement detailing (Ld, lap, spacing).
*   **DXF Export:** CAD-ready drawing generation for shop drawings.
*   **Integration:** CSV/JSON batch processing with CLI for automation.
*   **Strategy:** Python-first implementation with optional ezdxf dependency for DXF generation.
**Key Features:**
- Reinforcement Detailing (`detailing.py`)
  - Development length (Ld) per IS 456 Cl 26.2.1
  - Lap length with zone multipliers (1.5× tension)
  - Bar spacing validation per IS 456 Cl 26.3.2
  - Automatic bar arrangement selection
- DXF Export (`dxf_export.py`)
  - DXF R2010 format with standard layers
  - Beam elevation and section views
  - Automatic dimensioning and callouts
- Excel Integration (`excel_integration.py`)
  - CSV/JSON parsing with flexible key mapping
  - Batch DXF generation with progress tracking
  - Detailing schedule export
  - CLI: `python -m structural_lib.excel_integration`
- Documentation:
  - `docs/specs/v0.7-data-mapping.md`
  - `docs/planning/research-detailing.md`
  - `docs/agent-workflow.md`
- Tests: 1958 passing (31 detailing + 15 integration + 21 original)

## v0.6.0
**Date:** 2025-12-11
**Status:** ✅ Locked & Verified
**Commit Hash:** 48c4c88
**Mindset:** Transitioning from "Core Logic" (v0.5) to "Usability" (v0.6).
*   **Integration:** Bridging the gap between analysis software (ETABS) and our design engine.
*   **Reporting:** Converting raw design data into professional deliverables (Beam Schedules).
*   **Strategy:** We are using a consolidated feature branch because these features are tightly coupled (Import -> Design -> Schedule) and represent a single "Usability" milestone.
**Key Features:**
- ETABS CSV Import (`M13_Integration.bas`)
- Beam Schedule Generation (`M14_Reporting.bas`)
- Robustness Refactoring (Dynamic Columns, Sorting)
- Governance Docs (`git-governance.md`, `mission-and-principles.md`)

## v0.5.0
**Date:** 2025-12-11
**Status:** ✅ Locked & Verified
**Commit Hash:** be04b12b65a0e2c147ec018ea3ba7b826ac5abdc
**Key Features:**
- Excel Workbook Integration (`StructEng_BeamDesign_v0.5.xlsm`)
- Application Layer (`M11_AppLayer.bas`) for Table-to-Library orchestration
- UI Layer (`M12_UI.bas`) with "Run Design" and "Clear" controls
- Setup Script (`M99_Setup.bas`) for automated workbook scaffolding
- Governance: Added DOCS, INTEGRATION, and SUPPORT agents
- Verification: Sample run (B1, 230x450, Mu=150 kN·m, Vu=100 kN, M25/Fe500) returned Ast ≈ 1026 mm², Status OK, shear reinforcement required, stirrups "2L-8mm @ 300 mm", remarks "Doubly Reinforced" as expected.

## v0.4.0
**Date:** 2025-12-11
**Status:** ✅ Locked & Verified
**Commit Hash:** 1e1d3ce45be5e003f7d233ff7c94f9cfc7c9011a
**Key Features:**
- IS 13920 Ductile Detailing (Geometry, Min/Max Steel, Confinement)
- Python Packaging (`pyproject.toml`)
- Excel Add-in (`StructEngLib.xlam`)
- Full Test Coverage (Python + VBA)

## v0.3.0
**Date:** 2025-12-11
**Status:** ✅ Locked
**Key Features:**
- Flanged Beam Design (T/L Sections)
- Neutral Axis analysis (Flange vs Web)
- `Test_Flanged.bas`

## v0.2.1
**Date:** 2025-12-11
**Status:** ✅ Locked
**Key Fixes (Mac VBA Compatibility):**
- Stack corruption fixes for boolean pass-by-value cases.
- Wrapped dimension multiplications in `CDbl()` to avoid overflow.
- Safer test harness assertions in `Test_Structural.bas`.

## v0.2.0
**Date:** 2025-12-11
**Status:** ✅ Locked
**Key Features:**
- Doubly Reinforced Beam Design
- Non-linear stress-strain curve (IS 456 Fig 23)
- Mac VBA Overflow Fixes

## v0.1.0
**Date:** 2025-12-10
**Status:** ✅ Locked
**Key Features:**
- Core Flexure (Singly Reinforced)
- Shear Design (Table 19/20)
- Dual Python/VBA Architecture

---

## v0.7.1
**Date:** 2025-12-15
**Status:** ✅ Locked & Verified
**Commit Hash:** eef6c7d3212b2cc00bccee7cb8a574148157698a
**Mindset:** Hardening the v0.7 deliverables with stronger CI/testing and DXF parity.
**Key Features:**
- CI/test hardening:
  - Expanded Python edge-case coverage and DXF smoke testing.
  - Coverage floor enforced at `--cov-fail-under=92`.
- Packaging:
  - Ensured `structural_lib/py.typed` is included in built distributions.
- VBA DXF:
  - Native DXF R12 export module (`M16_DXF.bas`) + UDF entrypoints + VBA test suite.

## v0.8.0
**Date:** 2025-12-15
**Status:** ✅ Locked & Verified
**Commit Hash:** 8319bc487ad8fab445b19dab00bdd169b4759ec7
**Mindset:** Moving toward production readiness: add serviceability and an Excel-friendly compliance verdict.
**Key Features:**
- Serviceability (Level A):
  - Deflection span/depth check with explicit modifiers and auditable assumptions.
  - Crack width estimate (Annex-F-style) with exposure-driven limits.
  - Python + VBA parity.
- Compliance checker:
  - Multi-case orchestration across flexure + shear (+ optional serviceability) with deterministic governing-case selection.
  - Excel-friendly summary row output.
- Verification:
  - Python tests: 158 collected/passing.

---

## Chronological Index (read in order)

Note: This ledger is **append-only**, so entries may not appear in chronological order above.
Use this index as the canonical “timeline view”.

- v0.1.0 (2025-12-10)
- v0.2.0 (2025-12-11)
- v0.3.0 (2025-12-11)
- v0.4.0 (2025-12-11)
- v0.5.0 (2025-12-11)
- v0.6.0 (2025-12-11)
- v0.7.0 (2025-12-11)
- v0.7.1 (2025-12-15)
- v0.8.0 (2025-12-15)

---

## Append-Only Clarification (2025-12-15)

The `v0.7.1` and `v0.8.0` entries were **finalized later** and therefore **appended after** the earlier `v0.1.0`–`v0.7.0` block.
To preserve the “immutable / append-only” rule, older entries were not reordered; use the **Chronological Index** section as the intended reading order.

---

## v0.8.1
**Date:** 2025-12-16
**Status:** ✅ Locked & Verified
**Commit Hash:** (tag: v0.8.1)
**Mindset:** Tooling-only hardening patch after v0.8.0.
**Key Changes (no engineering behavior changes):**
- Packaging:
  - `pyproject.toml` is the single source of truth (remove duplicated metadata from `setup.cfg`).
  - Standardize license inclusion via `project.license-files`.
- CI quality gates:
  - Run `ruff check` alongside black + mypy.
  - Packaging smoke check now installs the built wheel and imports `structural_lib`.
- Local workflow:
  - Add `Python/scripts/pre_release_check.sh` to run the full gate locally.

## Chronological Index Addendum (2025-12-16)

- v0.8.1 (2025-12-16)

---

## v0.8.2
**Date:** 2025-12-16
**Status:** ✅ Locked & Verified
**Commit Hash:** (tag: v0.8.2)
**Mindset:** Robustness + CI patch after v0.8.1.
**Key Changes:**
- Compliance robustness:
  - Hardened serviceability parameter handling and made failure-mode utilization deterministic.
- DXF export robustness:
  - Improved optional `ezdxf` surface handling for tests and type checking.
- CI:
  - Addressed coverage-gate failures by adding targeted regression tests to keep total coverage ≥ 92%.

## Chronological Index Addendum (2025-12-16, patch)

- v0.8.2 (2025-12-16)

---

## v0.9.0
**Date:** 2025-12-19
**Status:** ✅ Locked & Verified
**Commit Hash:** (tag: v0.9.0)
**Mindset:** Move from library usage to automation usage: stable entrypoints + deterministic file-in/file-out runs.
**Key Changes:**
- Stable IS456 public entrypoints (future-proof for additional design codes).
- Golden-vector regression tests to lock down key outputs and determinism.
- Deterministic job schema + batch runner + CLI (JSON/CSV outputs with a fixed folder layout).

## Chronological Index Addendum (2025-12-19)

- v0.9.0 (2025-12-19)

---

## v0.9.1
**Date:** 2025-12-25
**Status:** ✅ Locked & Verified
**Commit Hash:** (tag: v0.9.1)
**Mindset:** Patch release tagging the latest green `main` state.
**Key Changes:**
- CI: enforce `--cov-fail-under=92` (reduced friction while iterating).
- Robustness fixes + regression tests (findings audit across flexure/detailing/compliance/serviceability).
- Docs: README + quickstart pins updated; batch runner + DXF usage clarified.

## Chronological Index Addendum (2025-12-25)

- v0.9.1 (2025-12-25)

---

## Release Notes Addendum (2025-12-25)

This section **adds depth** to the existing locked entries for recent releases.
It exists because this ledger is **append-only**.

### v0.7.1 — Expanded Notes

**Why it existed:** v0.7 shipped big deliverables (detailing + DXF + integration). v0.7.1 focused on making them safer to use via CI hardening and better edge coverage.

**Engineering behavior:** no intentional algorithm changes; focused on robustness.

**Python test/CI hardening:**
- Added targeted regression and edge-case tests, including a DXF smoke test, so DXF behavior is exercised in CI when optional dependencies are present.
- Introduced/raised the Python coverage gate to keep long-term safety against accidental numerical drift.

**Packaging correctness:**
- Ensured `structural_lib/py.typed` is shipped so type checkers can consume the package as typed (PEP 561).

**Integration fixes:**
- Made schedule generation resilient when a beam has only one valid bar arrangement.
- Made `BeamDesignData.from_dict()` deterministic when both `d` and `D` keys exist (legacy lowercase `d` won’t override a provided `D`).

**VBA parity (DXF):**
- Added native VBA DXF export (`M16_DXF.bas`) and UDF/macro entrypoints so the Excel flow can generate drawings without Python.

### v0.8.0 — Expanded Notes

**Why it existed:** move toward “production readiness” by adding serviceability checks and an Excel-friendly compliance verdict.

**Serviceability (Python + VBA parity):**
- Deflection: span/depth check via `serviceability.check_deflection_span_depth(...)` with explicit assumptions recorded.
- Crack width: simplified Annex-F-style workflow via `serviceability.check_crack_width(...)` with exposure-driven limits.

**Compliance orchestration:**
- Added a deterministic multi-check orchestrator (`compliance.check_compliance_report(...)`) that selects a governing case and governing utilization in a stable, auditable manner.
- Structured outputs are designed to be consumed by Excel/reporting layers (summary payloads + clear remarks).

### v0.8.1 — Expanded Notes

**Why it existed:** tooling-only patch after v0.8.0 to reduce release friction and make CI “tell the truth”.

**No engineering behavior changes** (design calculations intended unchanged).

**Packaging / build hygiene:**
- Consolidated packaging metadata into `Python/pyproject.toml` to avoid split-brain configuration.
- Standardized license inclusion via `project.license-files`.

**CI quality gates:**
- Added `ruff check` alongside formatting/type checks.
- Strengthened packaging smoke testing by installing the built wheel and importing `structural_lib`.

**Local workflow:**
- Added `Python/scripts/pre_release_check.sh` as a single “run the release gate locally” entrypoint.

### v0.8.2 — Expanded Notes

**Why it existed:** robustness patch to keep behavior deterministic under slightly malformed inputs and to stabilize the DXF optional-dependency surface.

**Compliance robustness:**
- Hardened serviceability parameter handling so missing/malformed fields fail fast or normalize deterministically.
- Ensured governing-case utilization remains deterministic in failure modes (no accidental dependence on dict ordering or incidental iteration).

**DXF optional dependency surface:**
- Made `ezdxf`-optional code easier to monkeypatch/test and friendlier for type checking when DXF extras are not installed.

**CI reliability:**
- Added targeted regression tests to keep overall coverage at/above the configured threshold.

### v0.9.0 — Expanded Notes

**Why it existed:** “automation usage” milestone — stable entrypoints + deterministic file-in/file-out workflows.

**Stable public entrypoints (IS456):**
- `api.design_beam_is456(...)`: single-case design/check returning a structured `ComplianceCaseResult`.
- `api.check_beam_is456(...)`: multi-case report returning `ComplianceReport` with governing-case selection.
- `api.detail_beam_is456(...)`: wraps detailing to produce structured reinforcement outputs.

**Golden vectors (regression targets):**
- Introduced pinned numerical targets that lock key outputs and determinism across core modules.

**Deterministic job runner + CLI:**
- Job spec: [docs/specs/v0.9-job-schema.md](../specs/v0.9-job-schema.md).
- Runner: `structural_lib.job_runner.run_job(...)` writes stable outputs (JSON + CSV) in a fixed folder layout.
- CLI: `python -m structural_lib.job_cli run --job job.json --out <dir>`.

### v0.9.1 — Expanded Notes

**Why it existed:** patch release tagging a known-green state and capturing the “findings audit” fixes.

**CI policy (temporary):**
- Standardized the Python coverage floor at 92% to keep signal high while reducing friction during rapid iteration.

**Robustness fixes (findings audit):**
- Flexure: corrected flanged-beam max-steel behavior at edge cases.
- Detailing: tightened spacing validation so rule violations are reported deterministically.
- Compliance: clarified utilization semantics so summary/governing-case values are consistent.
- Serviceability: normalized inputs so equivalent values produce identical outputs.

**Docs updates:**
- Refreshed onboarding/version pins and clarified batch runner + DXF workflows so users can run the end-to-end pipeline without repo-specific tribal knowledge.

---

## Docs Layout Note (2025-12-25)

To keep `docs/` cleaner, several top-level redirect stubs were removed.

- Canonical governance docs:
  - `docs/_internal/git-governance.md`
  - `docs/_internal/agent-workflow.md`
- Archived research:
  - `docs/_archive/research-and-findings.md`

Older release notes may reference the historical stub paths that existed at the time; prefer the canonical locations above.

---

## v0.18.0
**Date:** 2026-01-20
**Status:** ✅ Locked & Verified
**Tag:** `v0.18.0`

**Key Changes:**
- AI Assistant v2 with dynamic workspace (9 states)
- Interactive rebar editor + cross-section views
- Material takeoff and cost estimation panel
- Model configuration defaulted to `gpt-4o-mini`

---

## v0.19.0
**Date:** 2026-01-21
**Status:** ✅ Locked & Verified
**Tag:** `v0.19.0`

**Key Changes:**
- DXF schedule polish (column widths, text sizing, smart truncation)
- AI model name fix (`gpt-4o-mini`)
- Streamlit API index for component reuse
