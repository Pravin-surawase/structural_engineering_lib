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

**Example prompt:** "Use `PROJECT_OVERVIEW.md` as context. Act as DEV agent. Implement TASK-005."

---

## 🟢 Done

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

- [x] **TASK-012**: IS 13920 ductile detailing (v1.0)
  - Implemented `ductile.py` (Python) and `M10_Ductile.bas` (VBA)
  - Checks: Geometry (b >= 200, b/D >= 0.3), Min/Max Steel, Confinement Spacing
  - Added unit tests `test_ductile.py`
  - Updated API Reference

---

## 🟡 In Progress

*(None currently)*

---

## 🔴 Up Next

- [ ] **TASK-013**: Final Release Preparation (v1.0)
  - Final code review
  - Full documentation pass
  - Release tagging

---

## Notes

- **Current Version**: v1.0.0 (candidate)
- **Last Updated**: 2025-12-11
- **Active Branch**: main
