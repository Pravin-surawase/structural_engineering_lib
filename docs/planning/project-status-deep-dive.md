# IS 456 RC Beam Design Library — Deep Dive

*Detailed architecture, module maps, and research directions*

**Last updated:** 2025-07-11
**Parent document:** [project-status.md](../_archive/planning/project-status.md)

---

## Table of Contents

1. [Audience](#1-audience)
2. [Source of Truth References](#2-source-of-truth-references)
3. [Feature Inventory](#3-feature-inventory)
4. [Architecture and Layering](#4-architecture-and-layering)
5. [Python Module Map](#5-python-module-map)
6. [VBA Module Map](#6-vba-module-map)
7. [Data Contracts](#7-data-contracts)
8. [Output Contracts](#8-output-contracts)
9. [Quality and Verification](#9-quality-and-verification)
10. [Release Artifacts](#10-release-artifacts)
11. [Research Directions](#11-research-directions)

---

## 1. Audience

- Maintainers and contributors (Python + VBA)
- Engineers evaluating production readiness
- AI-assisted research sessions focused on next features

## 2. Source of Truth References

| Topic | Document |
|-------|----------|
| Project overview | [project-overview.md](../architecture/project-overview.md) |
| Production roadmap | [production-roadmap.md](../_archive/planning/production-roadmap.md) |
| Task board | [TASKS.md](../TASKS.md) |
| Job schema | [v0.9-job-schema.md](../specs/v0.9-job-schema.md) |
| Testing strategy | [testing-strategy.md](../contributing/testing-strategy.md) |
| API reference | [api.md](../reference/api.md) |

## 3. Feature Inventory

### Core Engineering Features
- Pure functions (no UI dependencies)
- Limit state design per IS 456
- Flexure design: singly, doubly, and flanged (T/L) beams
- Shear design: Table 19/20 lookup, stirrup spacing limits
- Ductile detailing checks per IS 13920
- Reinforcement detailing: Ld, lap length, spacing, bar callouts
- Serviceability: Level A (deflection + crack width) and Level B (deflection)
- Compliance checker: multi-check summary across load cases

### Output and Automation Features
- DXF export (Python and VBA paths)
- Batch runner (job.json → JSON/CSV outputs)
- ETABS CSV import and normalization (Excel/VBA path)
- Dual implementation (VBA + Python)
- Mac compatibility (VBA hardened for Mac stack issues)

## 4. Architecture and Layering

### Layering (Non-Negotiable)

1. **Core calculation** — Pure math, deterministic, explicit units
2. **App/orchestration** — Validation, aggregation, decision logic
3. **UI/I-O** — Excel UI, CSV import/export, CLI tooling

### Data Flow (Typical)

```
Inputs (CSV or job.json)
    ↓
Design checks (flexure/shear/ductile)
    ↓
Detailing and DXF output (optional)
    ↓
Compliance summary and CSV outputs
```

## 5. Python Module Map

### Core Calculation

| Module | Purpose |
|--------|---------|
| `flexure.py` | Singly/doubly/flanged flexure |
| `shear.py` | Shear checks and spacing |
| `ductile.py` | IS 13920 checks |
| `tables.py` | Table 19/20 data and interpolation |
| `materials.py` | xu_max, material curves |
| `utilities.py` | Interpolation helpers |

### Serviceability

| Module | Purpose |
|--------|---------|
| `serviceability.py` | Deflection and crack width |

### Detailing and Outputs

| Module | Purpose |
|--------|---------|
| `detailing.py` | Ld, lap, spacing, bar callouts |
| `dxf_export.py` | DXF generation (optional ezdxf) |

### Compliance and Orchestration

| Module | Purpose |
|--------|---------|
| `compliance.py` | Case-level checks and governing case |
| `api.py` | Stable public entrypoints |

### I/O and Batch Automation

| Module | Purpose |
|--------|---------|
| `excel_integration.py` | CSV/JSON parsing and schedule |
| `job_runner.py` | Deterministic job outputs |
| `__main__.py` | Unified CLI entrypoint |
| `rebar_optimizer.py` | Cutting-stock optimizer |

## 6. VBA Module Map

### Core Calculation

| Module | Purpose |
|--------|---------|
| `M03_Tables.bas` | Table 19/20 data |
| `M04_Utilities.bas` | Helper functions |
| `M05_Materials.bas` | Material properties |
| `M06_Flexure.bas` | Flexure calculations |
| `M07_Shear.bas` | Shear calculations |
| `M10_Ductile.bas` | Ductile detailing |

### Detailing and DXF

| Module | Purpose |
|--------|---------|
| `M15_Detailing.bas` | Bar layouts |
| `M16_DXF.bas` | DXF export |

### BBS and Compliance

| Module | Purpose |
|--------|---------|
| `M18_BBS.bas` | Bar bending schedule |
| `M19_Compliance.bas` | Multi-check compliance |

### UI and Orchestration

| Module | Purpose |
|--------|---------|
| `M11_AppLayer.bas` | App orchestration |
| `M12_UI.bas` | UI layer |
| `M13_Integration.bas` | External integration |
| `M14_Reporting.bas` | Report generation |

## 7. Data Contracts

### Units (Canonical)

| Quantity | Unit |
|----------|------|
| Geometry | mm |
| Concrete/steel strength | N/mm² |
| Shear force | kN (converted internally) |
| Moment | kN·m (converted internally) |

### Batch Job Schema (v1)

- Single beam per job, multiple load cases
- Inputs: geometry, materials, cases with Mu/Vu
- Outputs: deterministic JSON + compact CSV summaries
- Reference: [v0.9-job-schema.md](../specs/v0.9-job-schema.md)

### CSV Integration

- Input columns: `BeamID, Story, b, D, Span, Cover, fck, fy, Mu, Vu, Ast_req, Asc_req, Stirrup_Dia, Stirrup_Spacing` (case-insensitive)
- Outputs: optional DXF folder + schedule CSV

## 8. Output Contracts

What downstream tools can rely on:

| Output Type | Contract |
|-------------|----------|
| Design result | Pass/fail, governing case, utilization ratios, key quantities |
| Compliance | Per-case breakdown + overall governing case per check group |
| DXF | Deterministic layer naming, text styles, geometry conventions |

**Breaking change policy:** If any contract changes, bump schema versions and document migration notes.

## 9. Quality and Verification

### Python Testing and CI

- Pytest suite with coverage gate enforced in CI
- Linting and type checks in GitHub Actions
- Packaging smoke checks in CI

### VBA Testing

- Manual tests exist; automated parity is a future priority

### Validation Packs (Planned)

"Trust artifacts" for practicing engineers:

1. **Verified examples folder:** 15–30 benchmark problems with expected outputs
2. **Comparison notes:** Where results match design aids/textbooks, and where assumptions differ
3. **Repro command:** One command to run all verified examples and generate a summary report

## 10. Release Artifacts

For every tagged release:

- [ ] Python package install path (tag pinned) + smoke-tested import
- [ ] Sample batch job(s) + expected outputs
- [ ] If DXF changes: at least 1 before/after screenshot in CHANGELOG
- [ ] If schema changes: updated schema doc + migration notes
- [ ] Excel add-in (.xlam) release asset (or documented path in repo)

## 11. Research Directions

Recommended research topics that align with adoption:

1. **ETABS CSV mapping:** Document supported tables and column normalization
2. **Deterministic constructability:** Constraints for bar layouts and spacing
3. **Compliance guidance:** Surface "why fail" and "what to change first"
4. **Multi-beam batch workflows:** Job schema v2 and CLI UX
5. **Verification packs:** Publish benchmark cases (SP:16 or textbook examples)

### Research Mode Prompt

Use this prompt to keep research aligned with the codebase:

> **Goal:** Identify what the industry expects (workflows + deliverables), what's missing, and which "wow factors" will drive adoption of this library.
>
> **Constraints:** Propose only features that can be deterministic, testable, and that preserve layering.
>
> **Inputs to reference:**
> - Modules: `flexure.py`, `shear.py`, `ductile.py`, `serviceability.py`, `detailing.py`, `dxf_export.py`, `compliance.py`, `job_runner.py`
> - Contracts: `docs/specs/v0.9-job-schema.md`, CSV column normalization rules
>
> **Research outputs required:**
> - Competitor/workflow map (ETABS/SAFE/STAAD + Excel + AutoCAD/Tekla), and where time is lost
> - A ranked list of 10 "wow outputs" (BBS/BOM, DXF packs, compliance scorecards, revision diffs)
> - A v0.10–v1.0 roadmap with acceptance criteria tied to the job schema and API
> - A trust plan (verified examples pack + CI gating)
