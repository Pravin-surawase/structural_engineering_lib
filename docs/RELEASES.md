# Release Ledger

This document serves as the **immutable source of truth** for project releases. 
Entries here represent "locked" versions that have been verified and approved.
**Rule:** Agents may ONLY append to this file. Never edit or delete past entries.

---

## v0.6.0 (In Progress)
**Target:** Integration & Reporting
**Branch:** `feat/v0.6-integration-reporting`
**Mindset:** Transitioning from "Core Logic" (v0.5) to "Usability" (v0.6).
*   **Integration:** Bridging the gap between analysis software (ETABS) and our design engine.
*   **Reporting:** Converting raw design data into professional deliverables (Beam Schedules).
*   **Strategy:** We are using a consolidated feature branch because these features are tightly coupled (Import -> Design -> Schedule) and represent a single "Usability" milestone.
**Key Features:**
- ETABS CSV Import (`M13_Integration.bas`)
- Beam Schedule Generation (`M14_Reporting.bas`)
- Robustness Refactoring (Dynamic Columns, Sorting)
- Governance Docs (`GIT_GOVERNANCE.md`, `MISSION_AND_PRINCIPLES.md`)

## v0.5.0 (Current)
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
