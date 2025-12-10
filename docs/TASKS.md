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
  - Table 19 (τc) with pt interpolation
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

- [x] **TASK-006**: Complete test coverage
  - Added edge case tests (min steel, max steel, over-reinforced)
  - Added shear edge cases (τv < τc, τv > τc,max)
  - Created VBA test module `Test_Structural.bas`
  - Verified with Python tests

---

## 🟡 In Progress

*(None currently)*

---

## 🔴 Up Next

- [ ] **TASK-007**: API documentation



---

## 🟡 In Progress

*(None currently)*

---

## 🔴 Up Next

- [ ] **TASK-005**: Sync VBA with Python refinements
  - [ ] Rename `Asc_Required` → `Ast_Required` in VBA types
  - [ ] Rename `Mu` → `Mu_Lim` in FlexureResult
  - [ ] Update M03_Tables to use floor(fck) for grade lookup (no fck interpolation)
  - [ ] Run VBA tests to verify

- [ ] **TASK-006**: Complete test coverage
  - [ ] Add edge case tests (min steel, max steel, over-reinforced)
  - [ ] Add shear edge cases (τv < τc, τv > τc,max)
  - [ ] VBA test module

- [ ] **TASK-007**: API documentation
  - [ ] Complete API_REFERENCE.md with all public functions
  - [ ] Add usage examples for each function
  - [ ] Document units and sign conventions

---

## 📋 Backlog (Future Versions)

- [ ] **TASK-008**: Doubly reinforced beam support (v0.2)
- [ ] **TASK-009**: Flanged beams T/L (v0.3)
- [ ] **TASK-010**: Excel Add-in packaging (.xlam)
- [ ] **TASK-011**: Python package (pyproject.toml, wheel)
- [ ] **TASK-012**: IS 13920 ductile detailing (v1.0)

---

## Notes

- **Current Version**: v0.1.0 (in development)
- **Last Updated**: 2025-12-10
- **Active Branch**: main
