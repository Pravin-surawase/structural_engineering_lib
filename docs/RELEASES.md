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
  - Coverage floor enforced at `--cov-fail-under=92`.
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

---

## v0.8.2
**Date:** 2025-12-16
**Status:** ✅ Locked & Verified
**Commit Hash:** (tag: v0.8.2)
**Mindset:** Robustness + CI patch after v0.8.1.
**Key Changes:**
- Compliance robustness:
  - Hardened serviceability parameter handling and made failure-mode utilization deterministic.
- DXF export robustness:
  - Improved optional `ezdxf` surface handling for tests and type checking.
- CI:
  - Addressed coverage-gate failures by adding targeted regression tests to keep total coverage ≥ 92%.

## Chronological Index Addendum (2025-12-16, patch)

- v0.8.2 (2025-12-16)

---

## v0.9.0
**Date:** 2025-12-19
**Status:** ✅ Locked & Verified
**Commit Hash:** (tag: v0.9.0)
**Mindset:** Move from library usage to automation usage: stable entrypoints + deterministic file-in/file-out runs.
**Key Changes:**
- Stable IS456 public entrypoints (future-proof for additional design codes).
- Golden-vector regression tests to lock down key outputs and determinism.
- Deterministic job schema + batch runner + CLI (JSON/CSV outputs with a fixed folder layout).

## Chronological Index Addendum (2025-12-19)

- v0.9.0 (2025-12-19)

---

## v0.9.1
**Date:** 2025-12-25
**Status:** ✅ Locked & Verified
**Commit Hash:** (tag: v0.9.1)
**Mindset:** Patch release tagging the latest green `main` state.
**Key Changes:**
- CI: enforce `--cov-fail-under=92` (reduced friction while iterating).
- Robustness fixes + regression tests (findings audit across flexure/detailing/compliance/serviceability).
- Docs: README + quickstart pins updated; batch runner + DXF usage clarified.

## Chronological Index Addendum (2025-12-25)

- v0.9.1 (2025-12-25)

---

## Release Notes Addendum (2025-12-25)

This section **adds depth** to the existing locked entries for recent releases.
It exists because this ledger is **append-only**.

### v0.7.1 — Expanded Notes

**Why it existed:** v0.7 shipped big deliverables (detailing + DXF + integration). v0.7.1 focused on making them safer to use via CI hardening and better edge coverage.

**Engineering behavior:** no intentional algorithm changes; focused on robustness.

**Python test/CI hardening:**
- Added targeted regression and edge-case tests, including a DXF smoke test, so DXF behavior is exercised in CI when optional dependencies are present.
- Introduced/raised the Python coverage gate to keep long-term safety against accidental numerical drift.

**Packaging correctness:**
- Ensured `structural_lib/py.typed` is shipped so type checkers can consume the package as typed (PEP 561).

**Integration fixes:**
- Made schedule generation resilient when a beam has only one valid bar arrangement.
- Made `BeamDesignData.from_dict()` deterministic when both `d` and `D` keys exist (legacy lowercase `d` won’t override a provided `D`).

**VBA parity (DXF):**
- Added native VBA DXF export (`M16_DXF.bas`) and UDF/macro entrypoints so the Excel flow can generate drawings without Python.

### v0.8.0 — Expanded Notes

**Why it existed:** move toward “production readiness” by adding serviceability checks and an Excel-friendly compliance verdict.

**Serviceability (Python + VBA parity):**
- Deflection: span/depth check via `serviceability.check_deflection_span_depth(...)` with explicit assumptions recorded.
- Crack width: simplified Annex-F-style workflow via `serviceability.check_crack_width(...)` with exposure-driven limits.

**Compliance orchestration:**
- Added a deterministic multi-check orchestrator (`compliance.check_compliance_report(...)`) that selects a governing case and governing utilization in a stable, auditable manner.
- Structured outputs are designed to be consumed by Excel/reporting layers (summary payloads + clear remarks).

### v0.8.1 — Expanded Notes

**Why it existed:** tooling-only patch after v0.8.0 to reduce release friction and make CI “tell the truth”.

**No engineering behavior changes** (design calculations intended unchanged).

**Packaging / build hygiene:**
- Consolidated packaging metadata into `Python/pyproject.toml` to avoid split-brain configuration.
- Standardized license inclusion via `project.license-files`.

**CI quality gates:**
- Added `ruff check` alongside formatting/type checks.
- Strengthened packaging smoke testing by installing the built wheel and importing `structural_lib`.

**Local workflow:**
- Added `Python/scripts/pre_release_check.sh` as a single “run the release gate locally” entrypoint.

### v0.8.2 — Expanded Notes

**Why it existed:** robustness patch to keep behavior deterministic under slightly malformed inputs and to stabilize the DXF optional-dependency surface.

**Compliance robustness:**
- Hardened serviceability parameter handling so missing/malformed fields fail fast or normalize deterministically.
- Ensured governing-case utilization remains deterministic in failure modes (no accidental dependence on dict ordering or incidental iteration).

**DXF optional dependency surface:**
- Made `ezdxf`-optional code easier to monkeypatch/test and friendlier for type checking when DXF extras are not installed.

**CI reliability:**
- Added targeted regression tests to keep overall coverage at/above the configured threshold.

### v0.9.0 — Expanded Notes

**Why it existed:** “automation usage” milestone — stable entrypoints + deterministic file-in/file-out workflows.

**Stable public entrypoints (IS456):**
- `api.design_beam_is456(...)`: single-case design/check returning a structured `ComplianceCaseResult`.
- `api.check_beam_is456(...)`: multi-case report returning `ComplianceReport` with governing-case selection.
- `api.detail_beam_is456(...)`: wraps detailing to produce structured reinforcement outputs.

**Golden vectors (regression targets):**
- Introduced pinned numerical targets that lock key outputs and determinism across core modules.

**Deterministic job runner + CLI:**
- Job spec: [docs/specs/v0.9_JOB_SCHEMA.md](docs/specs/v0.9_JOB_SCHEMA.md).
- Runner: `structural_lib.job_runner.run_job(...)` writes stable outputs (JSON + CSV) in a fixed folder layout.
- CLI: `python -m structural_lib.job_cli run --job job.json --out <dir>`.

### v0.9.1 — Expanded Notes

**Why it existed:** patch release tagging a known-green state and capturing the “findings audit” fixes.

**CI policy (temporary):**
- Standardized the Python coverage floor at 92% to keep signal high while reducing friction during rapid iteration.

**Robustness fixes (findings audit):**
- Flexure: corrected flanged-beam max-steel behavior at edge cases.
- Detailing: tightened spacing validation so rule violations are reported deterministically.
- Compliance: clarified utilization semantics so summary/governing-case values are consistent.
- Serviceability: normalized inputs so equivalent values produce identical outputs.

**Docs updates:**
- Refreshed onboarding/version pins and clarified batch runner + DXF workflows so users can run the end-to-end pipeline without repo-specific tribal knowledge.
