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
| **INTEGRATION** | `agents/INTEGRATION.md` | Data schemas, ETABS/CSV mapping |
| **DOCS** | `agents/DOCS.md` | API docs, guides, changelog |
| **SUPPORT** | `agents/SUPPORT.md` | Troubleshooting, known issues |

**See also:** `docs/AGENT_WORKFLOW.md` for detailed agent protocols.

---

## 🟡 In Progress (v0.7 - Detailing & Drawings)

- [x] **TASK-022: CLIENT Requirements (v0.7)**
  - **Agent:** CLIENT
  - **Status:** ✅ Complete
  - **Output:** `docs/v0.7_REQUIREMENTS.md`
  - Format: DXF (AutoCAD compatible)
  - Content: Beam elevation + reinforcement layout
  - Level: Shop drawing (fabrication-ready)

- [x] **TASK-023: IS Code Detailing Research (v0.7)**
  - **Agent:** RESEARCHER
  - **Status:** ✅ Complete
  - **Output:** `docs/RESEARCH_DETAILING.md`
  - Covers: IS 456, IS 13920, SP 34

- [x] **TASK-024: PM Scope Lock (v0.7)**
  - **Agent:** PM
  - **Status:** ✅ Complete
  - **Output:** Scope locked in `docs/v0.7_REQUIREMENTS.md`
  - IN: DXF export, beam elevation, rebar, stirrups, dimensions
  - OUT: Section cuts, BBS, multi-beam layout

- [x] **TASK-025: UI Layout Design (v0.7)**
  - **Agent:** UI
  - **Status:** ✅ Complete
  - **Output:** Layer structure in `docs/v0.7_REQUIREMENTS.md`
  - Layers: BEAM_OUTLINE, REBAR_MAIN, REBAR_STIRRUP, DIMENSIONS, TEXT

- [x] **TASK-026: DEV Architecture (v0.7)**
  - **Agent:** DEV
  - **Status:** ✅ Complete
  - **Decision:** Python `ezdxf` for DXF, VBA trigger or CLI
  - Modules: `Python/structural_lib/detailing.py`, `Python/structural_lib/dxf_export.py`

---

## 🔴 Up Next (v0.7 - Implementation)

- [x] **TASK-027: Implement Detailing Logic (v0.7)**
  - **Agent:** DEV
  - **Status:** ✅ Complete
  - **Output:** `Python/structural_lib/detailing.py`
  - Functions: Ld, lap length, bar spacing, bar arrangement

- [x] **TASK-028: Implement DXF Export (v0.7)**
  - **Agent:** DEV
  - **Status:** ✅ Complete
  - **Output:** `Python/structural_lib/dxf_export.py`
  - Uses ezdxf library for DXF generation

- [x] **TASK-029: Data Mapping for Detailing (v0.7)**
  - **Agent:** INTEGRATION
  - **Status:** ✅ Complete
  - **Output:** `docs/specs/v0.7_DATA_MAPPING.md`, `excel_integration.py`
  - CSV/JSON parsing, batch DXF generation, schedule export

- [x] **TASK-030: Test Cases for Detailing (v0.7)**
  - **Agent:** TESTER
  - **Status:** ✅ Complete (31 tests pass)
  - **Output:** `Python/tests/test_detailing.py`

- [x] **TASK-031: Documentation Update (v0.7)**
  - **Agent:** DOCS
  - **Status:** ✅ Complete
  - **Output:** API_REFERENCE.md v0.7.0, CHANGELOG.md updated
  - Added Sections 9-11 for detailing, DXF, integration APIs

- [x] **TASK-032: Release v0.7.0**
  - **Agent:** DEVOPS
  - **Status:** ✅ Complete
  - **Output:** Merged to main, tagged v0.7.0
  - Branch deleted: feat/v0.7-detailing

---

## 🔵 Backlog (v0.8+)

- [x] **TASK-033: VBA Detailing Module (M15)**
  - **Agent:** DEV
  - **Status:** ✅ Complete
  - **Output:** `VBA/Modules/M15_Detailing.bas`
  - Functions: Ld, lap length, bar spacing, bar selection, callouts
  - UDTs: BarArrangement, StirrupArrangement, BeamDetailingResult
  - UDFs: IS456_Ld, IS456_LapLength, IS456_BondStress, etc.
  - Tests: `VBA/Tests/Test_Detailing.bas` (25 test cases)

- [ ] **TASK-037: GitHub Repo Professionalization (community + CI)**
  - **Agent:** DEVOPS / DOCS
  - **Goal:** Make the repository easy/safe for other engineers to use and contribute.
  - **Checklist:**
    - [ ] Add community files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`
    - [ ] Add PR template: `.github/pull_request_template.md`
    - [ ] Add issue templates: `.github/ISSUE_TEMPLATE/*`
    - [ ] Add CI workflow: `.github/workflows/python-tests.yml` running `pytest` in `Python/`
    - [ ] README polish: add “Contributing / Support / Security” links; ensure install commands are correct
    - [ ] Verify CI passes on GitHub; update badges if desired
    - [ ] Keep scope minimal: no new features, only repo hygiene

- [ ] **TASK-034**: Bar Bending Schedule (BBS)
- [ ] **TASK-035**: Section Cuts in DXF
- [ ] **TASK-036**: Multi-beam Layout
- [ ] **TASK-019**: Regression Snapshots (Excel)
- [ ] **TASK-020**: Py/VBA Parity Tests
- [ ] **TASK-021**: Documentation Depth Pass

- [ ] **TASK-038: Professional-grade Python Testing (coverage + reliability)**
  - **Agent:** TESTER / DEVOPS
  - **Goal:** Make testing robust enough for external contributors and regression safety.
  - **Checklist:**
    - [ ] Add coverage reporting (pytest-cov) and publish in CI artifacts
    - [ ] Establish a baseline coverage target (start informational, then enforce threshold)
    - [ ] Add golden-reference tests for boundary cases (Mu≈Mu_lim, Vus≈0, pt clamps)
    - [ ] Add property tests for invariants (non-negativity, monotonicity where expected)
    - [ ] Add CLI/integration tests (CSV/JSON → detailing → DXF generation)

- [ ] **TASK-039: Test Vectors + Parity Harness (Python ↔ VBA)**
  - **Agent:** TESTER / DEV
  - **Goal:** Ensure Python and VBA stay identical for the same inputs.
  - **Checklist:**
    - [ ] Create shared test vector set (CSV/JSON) with expected outputs + tolerances
    - [ ] Python: parametrized tests load vectors and assert outputs
    - [ ] VBA: TestHarness reads vectors and writes pass/fail summary
    - [ ] Document tolerances (Ast, tc, spacing, Ld, lap) and units

- [ ] **TASK-040: VBA Testing Automation (repeatable test runs)**
  - **Agent:** DEVOPS / TESTER
  - **Goal:** Make VBA tests repeatable and reviewable in PRs.
  - **Checklist:**
    - [ ] Add a single entrypoint macro: `RunAllTests`
    - [ ] Standardize test output/log format (counts + failures)
    - [ ] Provide a manual run guide + expected output in docs

---

## 🟢 Done

- [x] **TASK-018: Beam Schedule Generation**
  - **Agent:** UI / DEV
  - **Status:** ✅ Complete (v0.6.0)
  - **Output:** `M14_Reporting.bas`

- [x] **TASK-017: Data Integration (ETABS/CSV)**
  - **Agent:** INTEGRATION
  - **Status:** ✅ Complete (v0.6.0)
  - **Output:** `M13_Integration.bas`

- [x] **Governance & Docs**
  - Created `docs/GIT_GOVERNANCE.md`
  - Created `docs/MISSION_AND_PRINCIPLES.md`
  - Updated `docs/RELEASES.md`

- [x] **TASK-016**: Integration Testing
- [x] **TASK-015**: UI/IO Layer (`M12_UI.bas`)
- [x] **TASK-014**: Application Layer (`M11_AppLayer.bas`)
- [x] **TASK-013**: Excel Workbook Skeleton
- [x] **TASK-012**: IS 13920 ductile detailing (v0.4)
- [x] **TASK-011**: Python package (pyproject.toml, wheel)
- [x] **TASK-010**: Excel Add-in packaging (.xlam)
- [x] **TASK-009**: Flanged beams T/L (v0.3)
- [x] **TASK-008**: Doubly reinforced beam support (v0.2)
- [x] **TASK-007**: Mac VBA Hardening (v0.2.1)
- [x] **TASK-006**: Complete test coverage
- [x] **TASK-005**: Sync VBA with Python refinements
- [x] **TASK-004**: Shear module
- [x] **TASK-003**: Flexure module (singly reinforced)
- [x] **TASK-002**: Core data layer
- [x] **TASK-001**: Project scaffold

---

## Notes

- **Current Version**: v0.7.0
- **Last Updated**: 2025-12-15
- **Active Branch**: main

### v0.7 Implementation Notes
- **Python:** Full implementation (detailing, DXF, integration) - 67 tests
- **VBA:** Full implementation (M15_Detailing.bas) - 25 test cases
- **DXF Dependency:** `pip install .[dxf]` for ezdxf support
