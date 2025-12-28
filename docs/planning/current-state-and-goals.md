# IS 456 RC Beam Design Library - Current State and Goals

Last updated: 2025-12-27
Current release tag: v0.10.3
Document status: Active

## 0) Executive summary

This repository is a professional-grade, UI-agnostic RC beam design library
targeting IS 456:2000. It currently provides strength design, detailing, DXF
output, Level A serviceability, compliance checking, Bar Bending Schedule
(BBS) generation, **unified CLI**, and **cutting-stock optimization**, with a 
deterministic batch runner and CSV integration. The implementation exists in 
both Python and VBA with parity intent, and is supported by **1680+ Python tests** and CI.

This document is a systematic overview of what exists today, how it is
structured, what gaps remain, and what the next priorities are. It is intended
to guide research, planning, and AI-assisted work so outputs map cleanly to the
codebase and release plan.

## 1) Audience

- Maintainers and contributors (Python + VBA).
- Engineers evaluating production readiness.
- AI-assisted research sessions focused on next features.

## 2) How to use this document

- Use Sections 3-8 to understand what is implemented today.
- Use Section 9 for quality/verification posture.
- Use Section 10 for known gaps and limitations.
- Use Sections 11-13 to plan next work and research prompts.

### 2.1 What “good” looks like (success criteria)

Use these as pass/fail signals for roadmap decisions:

- **Adoption:** A new user can go from install → first compliant beam result in **< 5 minutes** (Python) and **< 10 minutes** (Excel).
- **Trust:** Every check surfaces **governing case**, **utilization**, and a short **reason string** (“why this governs”).
- **Determinism:** Same input → same outputs (JSON/CSV/DXF) across runs and machines.
- **Batch value:** 50–500 beams can be processed with clear error summaries and partial success.
- **Verification:** Benchmarked example pack exists (textbook/SP:16-style) and runs in CI.
- **Distribution:** Release assets are versioned, installable, and documented (Python + Excel add-in).

## 3) Source of truth references

Primary references for deeper detail:
- Project overview: `docs/architecture/project-overview.md`
- Production roadmap: `docs/planning/production-roadmap.md`
- Task board: `docs/TASKS.md`
- Job schema (batch runner): `docs/specs/v0.9_JOB_SCHEMA.md`
- Testing strategy: `docs/contributing/testing-strategy.md`
- Public API reference: `docs/reference/api.md`
- Docs index: `docs/README.md`

## 4) Current feature inventory (from README, normalized)

Core engineering features:
- Pure functions (no UI dependencies).
- Limit state design per IS 456.
- Flexure design: singly, doubly, and flanged (T/L) beams.
- Shear design: Table 19/20 lookup, stirrup spacing limits.
- Ductile detailing checks per IS 13920.
- Reinforcement detailing: Ld, lap length, spacing, bar callouts.
- Serviceability Level A: deflection and crack width.
- Compliance checker: multi-check summary across load cases.

Output and automation features:
- DXF export (Python and VBA paths).
- Batch runner (job.json -> JSON/CSV outputs).
- ETABS CSV import and normalization (Excel/VBA path).
- Dual implementation (VBA + Python).
- Mac compatibility (VBA hardened for Mac stack issues).

## 5) Architecture and layering

Layering (non-negotiable):
1) Core calculation (pure math, deterministic, explicit units).
2) App/orchestration (validation, aggregation, decision logic).
3) UI/I-O (Excel UI, CSV import/export, CLI tooling).

Data flow (typical):
- Inputs (CSV or job.json) -> design checks
- Detailing and DXF output (optional)
- Compliance summary and CSV outputs

## 6) Python module map (current state)

Core calculation:
- `Python/structural_lib/flexure.py`: singly/doubly/flanged flexure.
- `Python/structural_lib/shear.py`: shear checks and spacing.
- `Python/structural_lib/ductile.py`: IS 13920 checks.
- `Python/structural_lib/tables.py`: Table 19/20 data and interpolation.
- `Python/structural_lib/materials.py`: xu_max, material curves.
- `Python/structural_lib/utilities.py`: interpolation helpers.

Serviceability:
- `Python/structural_lib/serviceability.py`: deflection and crack width.

Detailing and outputs:
- `Python/structural_lib/detailing.py`: Ld, lap, spacing, bar callouts.
- `Python/structural_lib/dxf_export.py`: DXF generation (optional ezdxf).

Compliance and orchestration:
- `Python/structural_lib/compliance.py`: case-level checks and governing case.
- `Python/structural_lib/api.py`: stable public entrypoints.

I/O and batch automation:
- `Python/structural_lib/excel_integration.py`: CSV/JSON parsing and schedule.
- `Python/structural_lib/job_cli.py`: Legacy CLI runner.
- `Python/structural_lib/job_runner.py`: deterministic job outputs.
- `Python/structural_lib/__main__.py`: **Unified CLI entrypoint** (v0.9.4).
- `Python/structural_lib/rebar_optimizer.py`: **Cutting-stock optimizer** (v0.9.4).

## 7) VBA module map (current state)

Core calculation modules:
- `VBA/Modules/M03_Tables.bas`
- `VBA/Modules/M04_Utilities.bas`
- `VBA/Modules/M05_Materials.bas`
- `VBA/Modules/M06_Flexure.bas`
- `VBA/Modules/M07_Shear.bas`
- `VBA/Modules/M10_Ductile.bas`

Detailing and DXF:
- `VBA/Modules/M15_Detailing.bas`
- `VBA/Modules/M16_DXF.bas`

BBS and Compliance (v0.9.4):
- `VBA/Modules/M18_BBS.bas`: Bar bending schedule per IS 2502.
- `VBA/Modules/M19_Compliance.bas`: Multi-check compliance orchestration.

UI and orchestration:
- `VBA/Modules/M11_AppLayer.bas`
- `VBA/Modules/M12_UI.bas`
- `VBA/Modules/M13_Integration.bas`
- `VBA/Modules/M14_Reporting.bas`

## 8) Data contracts and inputs

Units (canonical):
- Geometry: mm
- Concrete/steel strength: N/mm2
- Shear force: kN (converted internally)
- Moment: kN*m (converted internally)

Batch job schema (v1):
- Single beam per job, multiple load cases.
- Inputs: geometry, materials, cases with Mu/Vu.
- Outputs: deterministic JSON + compact CSV summaries.
Reference: `docs/specs/v0.9_JOB_SCHEMA.md`

CSV integration (Python and VBA paths):
- Input columns: `BeamID, Story, b, D, Span, Cover, fck, fy, Mu, Vu,
    Ast_req, Asc_req, Stirrup_Dia, Stirrup_Spacing` (case-insensitive).
- Outputs: optional DXF folder + schedule CSV.
Reference: `docs/getting-started/python-quickstart.md`

ETABS import (Excel/VBA path):
- CSV import with header normalization and sign preservation.
Reference: `docs/architecture/project-overview.md` and `docs/specs/v0.7_DATA_MAPPING.md`

## 9) Outputs and deliverables

Available today:
- Design results (flexure + shear + ductility checks).
- Compliance summary (governing case + utilization ratios).
- Detailing schedules (bar layouts, callouts).
- DXF drawings (Python via ezdxf, VBA R12).
- CSV outputs for downstream reporting.

### 9.1 Output contracts (what downstream tools can rely on)

- **Design result contract:** always includes pass/fail, governing case, utilization ratios, and key quantities (Ast, spacing, etc.).
- **Compliance contract:** includes per-case breakdown + overall governing case per check group.
- **DXF contract:** deterministic layer naming, text styles, and geometry conventions.

If any of the above changes, bump schema versions and document migration notes.

## 10) Quality and verification

Python testing and CI:
- Pytest suite with coverage gate enforced in CI.
- Linting and type checks in GitHub Actions.
- Packaging smoke checks in CI.

VBA testing:
- Manual tests exist; automated parity is a future priority.

Reference: `docs/contributing/testing-strategy.md`

### 10.1 Validation packs (what will convince practicing engineers)

Planned “trust artifacts” (publishable):
- **Verified examples folder:** 15–30 benchmark problems (beam flexure, shear, ductile checks, and serviceability Level A) with expected outputs.
- **Comparison notes:** where results match common design aids/textbook outcomes and where assumptions differ.
- **Repro command:** one command to run all verified examples and generate a summary report.

## 11) Known limitations and gaps

Tracked gaps:
- PDF report generation is not implemented.
- Serviceability is Level A only (detailed deflection not implemented).
- VBA automated testing is not implemented.
- Batch job schema is single-beam (multi-beam is future).
- ~~BBS cutting-stock optimization~~ ✅ **Implemented in v0.9.4** (`rebar_optimizer.py`).

## 12) Goals and priorities (next 1-3 releases)

Completed (v0.10):
1) ✅ Rebar arrangement optimizer (TASK-043).
2) ✅ BBS/BOM export (TASK-034) — `bbs.py` with CSV/JSON export.
3) ✅ ETABS mapping docs (TASK-044) — `docs/specs/ETABS_INTEGRATION.md`.

Near-term priorities:
1) Python <-> VBA parity automation (TASK-039/040).
2) BBS VBA parity.
3) Verification examples pack.

### 12.1 Release artifacts (what each release should ship)

For every tagged release:
- Python package install path (tag pinned) + smoke-tested import.
- Sample batch job(s) + expected outputs.
- If DXF changes: at least 1 before/after screenshot in CHANGELOG.
- If schema changes: updated schema doc + migration notes.
- Excel add-in (.xlam) release asset (or a clearly documented path in repo).

Reference: `docs/planning/production-roadmap.md` and `docs/TASKS.md`.

## 13) Research directions (AI-assisted)

Recommended research topics that align with adoption:
- ETABS CSV mapping: document supported tables and column normalization.
- Deterministic constructability: constraints for bar layouts and spacing.
- Compliance guidance: surface "why fail" and "what to change first".
- Multi-beam batch workflows: job schema v2 and CLI UX.
- Verification packs: publish benchmark cases (SP:16 or textbook examples).

### Research Mode prompt (tailored)

Use the prompt below to keep research aligned with the codebase.

**Goal:** Identify what the industry expects (workflows + deliverables), what’s missing, and which “wow factors” will drive adoption of this library.

**Constraints:** Propose only features that can be deterministic, testable, and that preserve layering.

**Inputs to reference:**
- Modules: `flexure.py`, `shear.py`, `ductile.py`, `serviceability.py`, `detailing.py`, `dxf_export.py`, `compliance.py`, `job_runner.py`, `job_cli.py`.
- Contracts: `docs/specs/v0.9_JOB_SCHEMA.md`, CSV column normalization rules.
- Priorities: TASK-043, TASK-034, TASK-044, TASK-039/040.

**Research outputs required:**
- Competitor/workflow map (ETABS/SAFE/STAAD + Excel + AutoCAD/Tekla), and where time is lost.
- A ranked list of 10 “wow outputs” (BBS/BOM, DXF packs, compliance scorecards, revision diffs).
- A v0.10–v1.0 roadmap with acceptance criteria tied to the job schema and API.
- A website plan (pages, demo assets, SEO keywords, and conversion funnel).
- A trust plan (verified examples pack + CI gating).
