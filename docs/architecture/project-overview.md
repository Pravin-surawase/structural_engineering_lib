# IS 456 RC Beam Design Library — Project Overview

**Purpose:** Give a concise, layer-aware guide so any contributor (human or AI) knows what we are building, why, and how.
**Use:** Treat this as shared context for VS Code AI or other tooling. No code here — just goals and approach.
**See also:**
- [mission-and-principles.md](mission-and-principles.md) for the deeper "why" and product philosophy.
- [docs/_internal/GIT_GOVERNANCE.md](../_internal/GIT_GOVERNANCE.md) for version control and contribution rules.

---

## 1. Mission
Build the **definitive, professional-grade** structural engineering automation stack with enterprise-level quality standards — starting with a robust, contract-tested RC beam design engine (IS 456) plus a flagship Excel workbook, backed by a structural library that is now a production-ready open-source Python/VBA package.

Principles:
- Engineering-first: every calculation traceable to IS 456 clauses/assumptions.
- Library-first: structural logic lives in reusable modules, not buried in macros.
- Excel-first UI: initial interface is a clean, obvious workbook for practicing engineers.
- Future-proof: design now so it can become an Excel add-in, a Python package, and a base for AI assistance (explanations, QA).
- Goals: build something real and robust; push toward automation/transparency; create reusable assets (library, workbook, tests, docs).

---

## 2. Phase 1 Deliverable (v0) — What “Done” Looks Like

### 2.1 Beam Engine Scope
- IS 456 limit state design for Rectangular and Flanged (T/L) beams.
- Checks: Flexure (Singly/Doubly), Shear, and IS 13920 Ductile Detailing.
- Sections per span: start, midspan, end.
- Inputs: geometry (b, D, cover), materials (fck, fy), factored Mu and Vu.
- Outputs: required/provided reinforcement, shear design, status (OK/FAIL).
- Out of scope for v0: Deflection checks, Crack width checks.

### 2.2 Excel Workbook Scope
- Sheets and roles:
  - HOME: metadata, main buttons (import ETABS CSV/paste, run design, clear, view log), status panel.
  - BEAM_INPUT: structured table per beam/span section (IDs, story, span, b, D, cover, fck, fy, Mu/Vu at start/mid/end with sign convention).
  - BEAM_DESIGN: BEAM_INPUT plus effective depth, required/provided steel, shear data, status and failure reasons.
  - BEAM_SCHEDULE: condensed, drawing-ready schedule (ID, story, size, bar patterns top/bottom, stirrup dia/spacing per zone).
  - LOG: timestamped entries for info/warnings/errors.
- UX: usable by another engineer without author guidance; failure rows clearly marked; inline “how to use” notes.

### 2.3 Structural Library Scope
- Pure IS 456 logic for rectangular and flanged beams (flexure, shear, ductile detailing).
- VBA first, isolated in its own modules (no Excel sheet/UI/file references).
- Designed to mirror in Python with the same conceptual API.

---

## 3. Architecture (Layered)
1) Core structural library: pure calculations; inputs are numbers; outputs are numbers/structs; no Excel/UI/I/O.
2) Application layer (beam engine): per-row coordination — read inputs, call library, decide bar patterns and zones, set OK/FAIL with reasons; still no UI/formatting.
3) UI/I-O layer (Excel macros): read/write ranges, handle buttons, import ETABS CSV into BEAM_INPUT, run designs, write outputs, log messages.
4) DevOps/docs: repo layout, exported VBA modules, tests/CI (later), Python port.

Keep logic in the right layer. The AI should always know which layer it is editing.

---

## 4. Structural Library — Intent and Function Groups

Goals:
- Pure/deterministic functions with explicit inputs/outputs.
- IS 456 aligned; comments reference clauses/tables.
- Unit consistency: mm, N/mm², kN, kN·m; convert at boundaries.
- UI independent; portable to Python with matching behavior.

Function groups (conceptual):
1) Geometry/reinforcement helpers: effective depth; pt from Ast,b,d; Ast min/max per IS 456.
2) Flexure helpers: singly, doubly, and flanged (T/L) beams; limiting moment; flag when Mu > Mu_lim; compression steel and flange checks.
3) Shear helpers: τv from Vu,b,d; τc from Table 19 (with pt clamp and interpolation in pt); Vc; Vus; stirrup capacity/spacing with code limits.
4) Ductile detailing (IS 13920): geometry limits, min/max steel, confinement spacing.
5) Validation/error conventions: detect impossible inputs (negative dims, cover ≥ D, invalid grades); return clear status codes/flags, no UI.

The AI should refine names, inputs/outputs, and ensure logic consistency without duplication.

---

## 5. Workbook Behavior (User Flow)
1) Fill BEAM_INPUT manually or via ETABS CSV import.
2) On HOME, click “Design Beams”.
3) App layer loops rows, calls library, writes BEAM_DESIGN.
4) Update BEAM_SCHEDULE from BEAM_DESIGN.
5) Failures are highlighted with reasons; user inspects BEAM_DESIGN for detail.

AI assistance: design column sets; keep sheet I/O separate from core logic; keep macros simple and safe.

---

## 6. ETABS Integration (v0.6 — Implemented)
- **M13_Integration.bas**: Robust CSV import with header normalization (Story/Story Name, Label/Beam, M3/Moment, etc.).
- **File Picker**: Mac/Windows compatible with fallback to InputBox or built-in sample data.
- **Grouping**: Dictionary-based grouping handles unsorted CSV; bucket aggregation (Start 0-20%, Mid 20-80%, End 80-100%).
- **Sign Preservation**: Negative moments (hogging) and shears are preserved for correct steel placement.
- **Sample Generator**: `Generate_Sample_ETABS_CSV` creates test data for validation.
- **Future**: ETABS API or Python bridge. Current structure makes this straightforward.

---

## 7. Multi-Agent Docs (for VS Code AI)
Keep role docs under `/agents/` (to add):
- DEV agent: implementation/refactors, clean architecture, units, purity.
- TESTER agent: tests and edge cases.
- DEVOPS agent: repo layout, exports, versioning, automation.
- PM/PRODUCT agent: scope/roadmap, value, changelog guidance.

Workflow: specify role and context (“Use PROJECT_OVERVIEW.md and agents/DEV.md…”), ask for concrete outputs (design decisions, tests, sheet layouts).

---

## 8. AI Behavior Expectations
- Respect layering (core vs app vs UI).
- Be explicit about layer, assumptions, clauses used, and limitations.
- Prefer small, composable functions; clear naming; comments on units and code refs.
- Avoid mixing UI with structural logic, over-engineering, or inventing non-IS456 behavior.

---

## 9. Choosing Agent Roles (VS Code AI)
- **PM:** Scope/prioritization, roadmap, changelog, “does this fit v0.1?”.
- **DEVOPS:** Repo layout, exports, packaging, CI, version bumps, release checklists.
- **DEV:** Implement/refactor core/app/UI code, align with clauses/units, fix logic bugs.
- **TESTER:** Design/expand tests, expected values/tolerances, edge/benchmark cases.

Suggested flow:
- New feature/bug: PM (scope) → DEV (code) → TESTER (cases) → DEVOPS (run/report).
- Docs/API: PM (confirm scope) → DEV (fill signatures/units) → TESTER (validate examples).
- Release: DEVOPS (checklist/CI) → PM (notes).

Use this with `agents/*.md` for prompts.

---

**How to use this doc:**
Reference it when prompting AI: e.g., “Use PROJECT_OVERVIEW.md as context. Act as DEV agent and design the detailed function list for the structural library,” or “Using PROJECT_OVERVIEW.md and TESTER role, propose a test matrix for v0 beams.”

---

**End of Project Overview**

---

## Agent Workflow (Cheat Sheet)
- **Feature:** PM → CLIENT (requirements) → RESEARCHER (clauses/constraints) → UI (layout) → DEV (build) → TESTER (verify) → DEVOPS (package) → DOCS (update notes/API) → PM (ledger) → SUPPORT (troubleshooting if needed).
- **Bug:** PM triage → DEV/RESEARCHER (root cause) → TESTER (repro/regression) → DEV (fix) → TESTER (verify) → DEVOPS (ship) → DOCS/SUPPORT (notes) → PM (ledger).
- **Data/Integration change:** PM → INTEGRATION (schema/mapping/validation) → DEV (implement) → TESTER (data-path cases) → DEVOPS (import/export workflow) → DOCS (schema reference) → PM.
- **Release:** PM sets scope/go/no-go → DEVOPS runs tests/builds/tags → DOCS drafts CHANGELOG/RELEASES/API updates → PM appends to `docs/RELEASES.md` (immutable) → SUPPORT/TROUBLESHOOTING refreshed → announce.

Reference: `agents/README.md` for agent prompt templates.
