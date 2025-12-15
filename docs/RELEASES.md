# Release Ledger

This document serves as the **immutable source of truth** for project releases. 
Entries here represent "locked" versions that have been verified and approved.
**Rule:** Agents may ONLY append to this file. Never edit or delete past entries.

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
  - `docs/specs/v0.7_DATA_MAPPING.md`
  - `docs/RESEARCH_DETAILING.md`
  - `docs/AGENT_WORKFLOW.md`
- Tests: 67 passing (31 detailing + 15 integration + 21 original)

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
- Governance Docs (`GIT_GOVERNANCE.md`, `MISSION_AND_PRINCIPLES.md`)

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
  - Coverage floor enforced at `--cov-fail-under=95`.
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
