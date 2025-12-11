# Task Board

> **How to use**: Check this file at the start of each session. Pick a task from "Up Next", move it to "In Progress", complete the work, then move to "Done".

---

## Multi-Agent Workflow

When working on tasks, specify which agent role to use:

| Role | Doc | Use For |
|------|-----|---------|
| **DEV** | `agents/DEV.md` | Implementation, refactoring, architecture |
| **TESTER** | `agents/TESTER.md` | Test design, edge cases, validation |
| **DEVOPS** | `agents/DEVOPS.md` | Repo structure, automation, releases |
| **PM** | `agents/PM.md` | Scope, prioritization, changelog |
| **UI** | `agents/UI.md` | Excel layout, UX flow, VBA forms |
| **CLIENT** | `agents/CLIENT.md` | Requirements, user stories, validation |
| **RESEARCHER** | `agents/RESEARCHER.md` | IS Codes, algorithms, technical constraints |

**Example prompt:** "Use `PROJECT_OVERVIEW.md` as context. Act as DEV agent. Implement TASK-005."

---

## � In Progress
- [ ] **TASK-018: Beam Schedule Generation**
  - **Agent:** UI / DEV
  - **Status:** Code Complete (`M14_Reporting`). Refactored for robustness.
  - **Pending:** Manual verification in Excel (Sort/Group logic).
- [ ] **TASK-017: Data Integration (ETABS/CSV)**
  - **Agent:** TESTER / INTEGRATION
  - **Status:** Code Complete (`M13_Integration`). Fixture created.
  - **Pending:** Manual verification in Excel (Import logic).

## 🟢 Done

- [x] **Governance & Docs**
  - Created `docs/GIT_GOVERNANCE.md`
  - Created `docs/MISSION_AND_PRINCIPLES.md`
  - Updated `docs/RELEASES.md` with v0.6 strategy

- [x] **TASK-001**: Project scaffold
  - Created folder structure (VBA/Modules, Python/structural_lib)
  - Set up all module stubs
  - Initialized git repository

- [x] **TASK-002**: Core data layer
  - M01_Constants, M02_Types, M03_Tables
  - Table 19 (τc) with pt interpolation (no fck interpolation; use nearest lower grade)
  - Table 20 (τc,max)
  - Python equivalents

- [x] **TASK-003**: Flexure module (singly reinforced)
  - Mu_lim calculation
  - Ast_required calculation
  - Min/max steel checks (Cl. 26.5.1)
  - VBA + Python implementations

- [x] **TASK-004**: Shear module
  - τv, τc, τc,max calculations
  - Stirrup spacing with limits
  - VBA + Python implementations

- [x] **TASK-005**: Sync VBA with Python refinements
  - Renamed `Asc_Required` → `Ast_Required` in VBA types
  - Renamed `Mu` → `Mu_Lim` in FlexureResult
  - Updated M03_Tables to use nearest lower grade (no fck interpolation)

- [x] **TASK-006**: Doubly Reinforced Flexure (v0.2)
  - Implemented `Design_Doubly_Reinforced` in VBA & Python
  - Added `Get_Steel_Stress` for non-linear stress-strain curve
  - Verified against manual calculations

- [x] **TASK-007**: Mac VBA Hardening (v0.2.1)
  - Fixed "Runtime Error 6: Overflow" using Safe Assertion Pattern
  - Wrapped dimension math in `CDbl()`
  - Removed nested UDT returns

- [x] **TASK-008**: Flanged Beams (v0.3)
  - Implemented T/L beam logic (NA in flange, NA in web singly/doubly)
  - Added iterative bisection solver for NA in web
  - Full Python parity and test coverage

- [x] **TASK-006**: Complete test coverage
  - Added edge case tests (min steel, over-reinforced; shear τv < τc and τv > τc,max)
  - Verified Python tests (pytest) pass locally
  - VBA test module to follow in later iteration

- [x] **TASK-007**: API documentation
  - Updated API_REFERENCE.md with current Python signatures, units, and policies
  - UDFs noted as planned (to be added with VBA parity)

- [x] **TASK-008**: Doubly reinforced beam support (v0.2)
  - Implemented `fsc` lookup/calculation (stress in compression steel)
  - Added `Design_Doubly_Reinforced` in Python and VBA
  - Updated `FlexureResult` to include `Asc_Required`
  - Added tests for doubly reinforced logic

- [x] **TASK-009**: Flanged beams T/L (v0.3)
  - Implemented `calculate_mu_lim_flanged` and `design_flanged_beam` in Python & VBA
  - Handles Neutral Axis in Flange (Rectangular), Web (Singly T), and Doubly Reinforced T
  - Added tests for all 3 cases

- [x] **TASK-010**: Excel Add-in packaging (.xlam)
  - Updated `M09_UDFs.bas` with wrappers for Doubly Reinforced and Flanged Beam design
  - Added `IS456_Design_Rectangular` and `IS456_Design_Flanged` returning dynamic arrays
  - Updated `M08_API.bas` version to 0.3.0
  - See `docs/EXCEL_ADDIN_GUIDE.md` for assembly instructions

- [x] **TASK-011**: Python package (pyproject.toml, wheel)
  - Added packaging metadata (`pyproject.toml`, `setup.cfg`, `Python/LICENSE`)
  - Built wheel/sdist to `Python/dist/`
  - Pytest passing (17 tests) with flanged/doubly included

- [x] **TASK-012**: IS 13920 ductile detailing (v0.4)
  - Implemented `ductile.py` (Python) and `M10_Ductile.bas` (VBA)
  - Checks: Geometry (b >= 200, b/D >= 0.3), Min/Max Steel, Confinement Spacing
  - Added unit tests `test_ductile.py` and `Test_Ductile.bas`
  - Updated API Reference

---

- [x] **TASK-013**: Excel Workbook Skeleton
  - Create `Excel/StructEng_BeamDesign_v0.5.xlsm`
  - Setup Sheets: `HOME`, `BEAM_INPUT`, `BEAM_DESIGN`, `BEAM_SCHEDULE`, `LOG`
  - Define named ranges and table structures

- [x] **TASK-014**: Application Layer (`M11_AppLayer.bas`)
  - Create controller logic to map Worksheet rows -> Library calls -> Output structs
  - Handle unit conversions (if input is m, convert to mm)
  - Error handling for invalid rows

- [x] **TASK-015**: UI/IO Layer (`M12_UI.bas`)
  - Button handlers: `btn_RunDesign`, `btn_Clear`, `btn_Import`
  - Status bar updates
  - Logging mechanism to `LOG` sheet

- [x] **TASK-016**: Integration Testing
  - Verified end-to-end flow from Input Table -> Design Table via `M11_AppLayer.Run_BeamDesign`.
  - Added `Integration_TestHarness.bas` to auto-populate representative cases (singly, flanged, high Mu, high Vu/Tcmax).
  - Manual sanity on Mac add-in: sample row returned status OK, Ast ~1026 mm², shear reinforcement callout produced.

---

## 🟡 In Progress

*(None currently)*

---

## 🔴 Up Next (v0.6 - Drafting & Reporting)

- [ ] **TASK-017**: Data Integration (ETABS/CSV)
  - Define schema mapping for ETABS output
  - Implement `Import_CSV` in `M12_UI.bas`
  - Current: `Import_ETABS_Data` supports CSV import (header aliases, sign preserved) and falls back to built-in sample rows (B1–B3) if no CSV is provided. Sample ETABS-style CSV available at `tests/ETABS_BeamForces_Example.csv`.

- [ ] **TASK-018**: Beam Schedule Generation
  - Transform `BEAM_DESIGN` results into `BEAM_SCHEDULE` format
  - Grouping logic (Same size/reinforcement)

- [ ] **TASK-019**: Regression Snapshots (Excel)
  - Use `Run_And_Export_Integration_Snapshot` to capture BEAM_DESIGN CSV for a standard test set.
  - Store snapshot under `logs/` for manual diff after changes.

- [ ] **TASK-020**: Py/VBA Parity Tests
  - Add pytest cases mirroring integration harness scenarios (flanged, high-shear, Tcmax edge).
  - Document expected outputs and compare with Excel snapshot.

- [ ] **TASK-021**: Documentation Depth Pass
  - Expand `docs/API_REFERENCE.md` with worked examples (inputs/outputs) per public function.
  - Add a one-page “Install on Mac” with screenshots; cross-link from README and EXCEL_ADDIN_GUIDE.

---

## Notes

- **Current Version**: v0.5.0
- **Last Updated**: 2025-12-11
- **Active Branch**: main
