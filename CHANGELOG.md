# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

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
