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

---

## 🔴 Up Next (v0.7 - Detailing & Drawings)

- [ ] **TASK-024: PM Scope Lock (v0.7)**
  - **Agent:** PM
  - **Goal:** Finalize scope and create v0.7 release plan

- [ ] **TASK-025: UI Layout Design (v0.7)**
  - **Agent:** UI
  - **Goal:** Design DXF layer structure and drawing layout

- [ ] **TASK-026: DEV Architecture (v0.7)**
  - **Agent:** DEV
  - **Goal:** Design M15_Detailing and M16_Drawing modules

- [ ] **TASK-027: Implement Detailing Logic (v0.7)**
  - **Agent:** DEV
  - **Goal:** Create `M15_Detailing.bas` with Ld, lap length, bar spacing

- [ ] **TASK-028: Implement DXF Export (v0.7)**
  - **Agent:** DEV
  - **Goal:** Create DXF generation (Python ezdxf or VBA)

- [ ] **TASK-029: Data Mapping for Detailing (v0.7)**
  - **Agent:** INTEGRATION
  - **Goal:** Define tbl_BeamDesign → DXF data flow

- [ ] **TASK-030: Test Cases for Detailing (v0.7)**
  - **Agent:** TESTER
  - **Goal:** Define test matrix for DXF output

- [ ] **TASK-031: Documentation Update (v0.7)**
  - **Agent:** DOCS
  - **Goal:** Update API_REFERENCE, CHANGELOG for v0.7

- [ ] **TASK-032: Release v0.7.0**
  - **Agent:** DEVOPS
  - **Goal:** Merge, tag, release

---

## 🔵 Backlog (v0.8+)

- [ ] **TASK-019**: Regression Snapshots (Excel)
- [ ] **TASK-020**: Py/VBA Parity Tests
- [ ] **TASK-021**: Documentation Depth Pass
- [ ] **TASK-033**: Bar Bending Schedule (BBS)
- [ ] **TASK-034**: Section Cuts in DXF
- [ ] **TASK-035**: Multi-beam Layout

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

- **Current Version**: v0.6.0
- **Last Updated**: 2025-12-11
- **Active Branch**: feat/v0.7-detailing
