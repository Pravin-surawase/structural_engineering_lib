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

**See also:** [docs/_internal/AGENT_WORKFLOW.md](_internal/AGENT_WORKFLOW.md) for detailed agent protocols.

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

### Mindset (v0.8+)

These tasks are based on the research log (`docs/RESEARCH_AI_ENHANCEMENTS.md`) and are intended to make the library *production-ready* for real engineering workflows.

- **Deterministic first:** same inputs → same outputs (no “magic”).
- **Auditable outputs:** every check should show inputs, assumptions, and “why pass/fail”.
- **Verification packs:** publish benchmark vectors + tests to build trust.
- **Engineer-friendly failures:** when something can’t be checked (missing inputs / infeasible detailing), return a structured reason.
- **Start simple, then deepen:** ship Level A checks (fast + robust), then add Level B detail once benchmarks exist.
- **Cross-platform default:** prefer CSV/Excel import/export paths; keep any .NET/COM automation Windows-first and optional.

- [x] **TASK-033: VBA Detailing Module (M15)**
  - **Agent:** DEV
  - **Status:** ✅ Complete
  - **Output:** `VBA/Modules/M15_Detailing.bas`
  - Functions: Ld, lap length, bar spacing, bar selection, callouts
  - UDTs: BarArrangement, StirrupArrangement, BeamDetailingResult
  - UDFs: IS456_Ld, IS456_LapLength, IS456_BondStress, etc.
  - Tests: `VBA/Tests/Test_Detailing.bas` (25 test cases)

- [x] **TASK-041: Serviceability Module (Deflection + Crack Width)**
  - **Agent:** DEV / RESEARCHER / TESTER
  - **Why:** Strength-only design is not “production-ready”; serviceability is required for professional acceptance.
  - **Scope (v0.8 Level A):**
    - [x] Deflection check (span/depth + explicit modifiers)
    - [x] Crack-width check (Annex-F-style estimate + exposure-driven limits)
    - [x] Add result types and Excel-friendly auditable payload fields
  - **Verification:**
    - [x] Add benchmark-style unit tests around threshold transitions
    - [x] Ensure assumptions are explicit in outputs (no silent defaults)

  **Outputs (implemented):**
  - Python: `Python/structural_lib/serviceability.py`, `Python/tests/test_serviceability.py`
  - Python types: extended `Python/structural_lib/types.py`
  - Docs: `docs/API_REFERENCE.md`, `docs/KNOWN_PITFALLS.md`
  - VBA parity (implemented): `VBA/Modules/M17_Serviceability.bas`, `VBA/Tests/Test_Serviceability.bas`, extended `VBA/Modules/M02_Types.bas`

- [x] **TASK-042: Compliance Checker (Pass/Fail + Reasons, Excel-Friendly)**
  - **Agent:** DEV / INTEGRATION / TESTER
  - **Why:** Users want a one-click verdict across multiple checks with clear “why fail” remarks.
  - **MVP Contract:** accept **already-factored** actions (Mu/Vu) for each case/combination.
  - **Checklist:**
    - [x] Orchestrate flexure + shear + (serviceability when available)
    - [x] Output: per-case results + governing case + compact summary row
    - [x] Add tests for governing-case stability and failure propagation

  **Outputs (implemented):**
  - Python: `Python/structural_lib/compliance.py`, `Python/tests/test_compliance.py`
  - Python types: extended `Python/structural_lib/types.py`
  - API wrapper: `Python/structural_lib/api.py`
  - Docs: `docs/API_REFERENCE.md`

- [x] **TASK-044: ETABS Integration (Keep CSV Default; API Optional)**
  - **Agent:** INTEGRATION / DEV
  - **Why:** ETABS is a real upstream source; integration should be reliable across machines.
  - **Status:** ✅ Complete — mapping docs created.
  - **Outputs:**
    - `docs/specs/ETABS_INTEGRATION.md`
    - Sample CSVs: `Python/examples/ETABS_Sample_Export.csv`, `Python/examples/ETABS_BeamForces_Example.csv`
  - **Checklist:**
    - [x] Document the supported ETABS export tables + column mapping
    - [x] Implement/extend CSV import normalization for compliance runs
    - [x] Add a small verification pack: sample ETABS-exported CSV → compliance run → stable summary
    - [ ] Keep CSI API automation as Windows-first/optional (separate task if needed)

- [x] **TASK-043: Rebar Arrangement Optimizer (Deterministic Layout Search)**
  - **Agent:** DEV / TESTER
  - **Why:** Converts required Ast into a buildable rebar pattern (dia/count/layers) while respecting spacing/cover.
  - **Status:** ✅ Complete — implemented in `rebar_optimizer.py` + tested in `test_rebar_optimizer.py`.
  - **Outputs:**
    - `Python/structural_lib/rebar_optimizer.py`
    - `Python/tests/test_rebar_optimizer.py`
  - **Checklist:**
    - [x] Define input contract (units, required params, allowed dia set)
    - [x] Encode hard constraints (cover, stirrups, min clear spacing, max bars/layer, max layers)
    - [x] Deterministic selection rule (tie-breakers) + optional objective toggle (min weight / min bar count / min congestion)
    - [x] Return an explanation payload (chosen pattern, checks evaluated, controlling constraint)
    - [x] Add deterministic tests (same inputs → same pattern)
    - [x] Add infeasible tests with structured reasons (e.g., "insufficient width for min spacing")

- [x] **TASK-034: Bar Bending Schedule (BBS) + BOM Export (CSV First)**
  - **Agent:** DEV / UI / INTEGRATION
  - **Why:** Turns detailing results into fabrication deliverables (site-friendly schedules).
  - **Status:** ✅ Complete — Python BBS module implemented with tests.
  - **Outputs:**
    - `Python/structural_lib/bbs.py`
    - `Python/tests/test_bbs.py` (29 tests)
  - **Checklist:**
    - [x] Define a BBS line-item schema (mark, dia, shape, cut length, qty, total length/weight)
    - [x] Define explicit rounding rules (length rounding + weight rounding)
    - [x] Export CSV (first); Excel formatting later
    - [x] Treat this as a primary adoption hook: keep outputs auditable + stable across versions
    - [x] Tests for totals (length/weight) + stable schema ordering
    - [ ] Optional (later): cutting-stock / waste optimization (6m/7.5m/9m/12m)

- [ ] **TASK-035**: Section Cuts in DXF
- [ ] **TASK-036**: Multi-beam Layout
- [ ] **TASK-019**: Regression Snapshots (Excel)
- [ ] **TASK-020**: Py/VBA Parity Tests
- [ ] **TASK-021**: Documentation Depth Pass

- [x] **TASK-037: GitHub Repo Professionalization (community + CI)**
  - **Agent:** DEVOPS / DOCS
  - **Goal:** Make the repository easy/safe for other engineers to use and contribute.
  - **Status:** ✅ Complete
  - **Checklist:**
    - [x] Add community files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`
    - [x] Add PR template: `.github/pull_request_template.md`
    - [x] Add issue templates: `.github/ISSUE_TEMPLATE/*`
    - [x] Add CI workflow: `.github/workflows/python-tests.yml` running `pytest` in `Python/`
    - [x] Harden CI permissions (least-privilege `GITHUB_TOKEN` in workflows)
    - [x] Protect `main` branch (require PR + required checks; disallow force-push + deletion)
    - [x] README polish: add “Contributing / Support / Security” links; ensure install commands are correct
    - [x] Verify CI passes on GitHub; update badges if desired
    - [x] Keep scope minimal: no new features, only repo hygiene

- [ ] **TASK-038: Professional-grade Python Testing (coverage + reliability)**
  - **Agent:** TESTER / DEVOPS
  - **Goal:** Make testing robust enough for external contributors and regression safety.
  - **Status:** 🟡 Partially done — CLI tests exist (`test_job_cli.py`, `test_job_runner_is456.py`) but no end-to-end CSV → detailing → DXF tests yet.
  - **Checklist:**
    - [x] Add coverage reporting (pytest-cov) and publish in CI artifacts
    - [x] Establish an enforced baseline coverage target (CI gate)
    - [x] Add targeted tests to stabilize coverage across environments
    - [ ] Add property tests for invariants (non-negativity, monotonicity where expected)
    - [ ] Add CLI/integration tests (CSV/JSON → detailing → DXF generation)

- [x] **TASK-045: Release Hygiene — Tag Post-Fix Patch Release**
  - **Agent:** DEVOPS / DOCS
  - **Why:** v0.9.0 tag points to the original release baseline; a patch tag (v0.9.1) makes the latest green `main` state easy to consume.
  - **Checklist:**
    - [x] Decide patch version (v0.9.1)
    - [x] Update `CHANGELOG.md` + append-only `docs/RELEASES.md`
    - [x] Tag + push

- [x] **TASK-039: Test Vectors + Parity Harness (Python ↔ VBA)**
  - **Agent:** TESTER / DEV
  - **Goal:** Ensure Python and VBA stay identical for the same inputs.
  - **Status:** ✅ Complete (Python side) — shared vectors + Python harness implemented.
  - **Outputs:**
    - `Python/tests/data/parity_test_vectors.json` — 20 vectors covering flexure, shear, detailing, serviceability, BBS
    - `Python/tests/test_parity_vectors.py` — parametrized tests with tolerance rules
    - `docs/VERIFICATION_EXAMPLES.md` — benchmark verification pack
  - **Checklist:**
    - [x] Create shared test vector set (JSON) with expected outputs + tolerances
    - [x] Python: parametrized tests load vectors and assert outputs
    - [ ] VBA: TestHarness reads vectors and writes pass/fail summary
    - [x] Document tolerances (Ast, tc, spacing, Ld, lap) and units

- [x] **TASK-040: VBA Testing Automation (repeatable test runs)**
  - **Agent:** DEVOPS / TESTER
  - **Goal:** Make VBA tests repeatable and reviewable in PRs.
  - **Status:** ✅ Complete — unified runner + documentation created.
  - **Outputs:**
    - `VBA/Tests/Test_RunAll.bas` — single entrypoint macro
    - `docs/VBA_TESTING_GUIDE.md` — run guide + expected output
  - **Checklist:**
    - [x] Add a single entrypoint macro: `RunAllVBATests`
    - [x] Standardize test output/log format (counts + failures)
    - [x] Provide a manual run guide + expected output in docs

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
  - Created `docs/_internal/GIT_GOVERNANCE.md`
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

- **Current Version**: v0.9.1
- **Last Updated**: 2025-12-25
- **Active Branch**: main

### v0.7 Implementation Notes
- **Python:** Full implementation (detailing, DXF, integration) - 67 tests (v0.7); 212 tests passing (v0.9.x)
- **VBA:** Full implementation (M15_Detailing.bas) - 25 test cases
- **DXF Dependency:** `pip install .[dxf]` for ezdxf support
