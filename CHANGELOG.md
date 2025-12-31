# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
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
  - Multi-agent review document (`docs/_internal/MULTI_AGENT_REVIEW_2025-12-28.md`)
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
  - Updated GIT_GOVERNANCE.md with accurate CI checks
  - AI agent workflow rules in `copilot-instructions.md`

### Changed
- **Documentation Polish:**
  - TASKS.md refactored (209→103 lines) — cleaner sections, current status
  - SESSION_LOG.md archived and cleaned (641→135 lines)
  - AI_CONTEXT_PACK.md reformatted with tables and clear sections
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
  - `docs/specs/v0.7_DATA_MAPPING.md`: Complete data flow specification.
  - `docs/specs/v0.7_REQUIREMENTS.md`: CLIENT requirements for detailing.
  - `docs/RESEARCH_DETAILING.md`: IS 456/SP 34 detailing research.
  - `docs/_internal/AGENT_WORKFLOW.md`: Multi-agent governance system.
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
  - `docs/_internal/GIT_GOVERNANCE.md`: Branching, commits, versioning, release process.
  - `docs/MISSION_AND_PRINCIPLES.md`: Project philosophy and design principles.
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
  - Formalized Feature/Bug/Release workflows in `PM.md` and `PROJECT_OVERVIEW.md`.
- **Documentation**:
  - Added `docs/specs/v0.5_EXCEL_SPEC.md`.
  - Updated `EXCEL_ADDIN_GUIDE.md` with dynamic path handling.

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
  - Updated `API_REFERENCE.md` to v0.4.0.
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
  - Documentation structure (`API_REFERENCE.md`, `TASKS.md`).
  - Excel add-in guide (`EXCEL_ADDIN_GUIDE.md`).

---

Format: Keep a section per release with Added/Changed/Fixed as needed. Tag releases as `vX.Y.Z`.
