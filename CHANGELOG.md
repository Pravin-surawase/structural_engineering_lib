# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

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
  - `docs/AGENT_WORKFLOW.md`: Multi-agent governance system.
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
  - `docs/GIT_GOVERNANCE.md`: Branching, commits, versioning, release process.
  - `docs/MISSION_AND_PRINCIPLES.md`: Project philosophy and design principles.
- **Test Fixtures**:
  - `tests/ETABS_BeamForces_Example.csv`: Sample ETABS export (10 rows, B1/B2).

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
