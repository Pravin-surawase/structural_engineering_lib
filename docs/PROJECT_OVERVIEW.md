# IS 456 RC Beam Design Library — Project Overview

**Purpose:** Give a concise, layer-aware guide so any contributor (human or AI) knows what we are building, why, and how.  
**Use:** Treat this as shared context for VS Code AI or other tooling. No code here — just goals and approach.

---

## 1. Mission
Build a structural engineering automation stack starting with a robust, reusable RC beam design engine (IS 456) plus a flagship Excel workbook, backed by a structural library that can become an open-source Python/VBA package.

Principles:
- Engineering-first: every calculation traceable to IS 456 clauses/assumptions.
- Library-first: structural logic lives in reusable modules, not buried in macros.
- Excel-first UI: initial interface is a clean, obvious workbook for practicing engineers.
- Future-proof: design now so it can become an Excel add-in, a Python package, and a base for AI assistance (explanations, QA).
- Goals: build something real and robust; push toward automation/transparency; create reusable assets (library, workbook, tests, docs).

---

## 2. Phase 1 Deliverable (v0) — What “Done” Looks Like

### 2.1 Beam Engine Scope
- IS 456 limit state design, rectangular RC beams only.
- Checks: flexure and shear (no deflection/crack checks in this phase).
- Sections per span: start, midspan, end.
- Inputs: geometry (b, D, cover), materials (fck, fy), factored Mu and Vu at 2–3 key locations.
- Outputs: required/provided reinforcement (top/bottom per section), shear design (Vc, Vus, spacing), beam schedule, clear status (OK/FAIL) with reasons.
- Out of scope for v0: flanged beams, ductile detailing, API links.

### 2.2 Excel Workbook Scope
- Sheets and roles:
  - HOME: metadata, main buttons (import ETABS CSV/paste, run design, clear, view log), status panel.
  - BEAM_INPUT: structured table per beam/span section (IDs, story, span, b, D, cover, fck, fy, Mu/Vu at start/mid/end with sign convention).
  - BEAM_DESIGN: BEAM_INPUT plus effective depth, required/provided steel, shear data, status and failure reasons.
  - BEAM_SCHEDULE: condensed, drawing-ready schedule (ID, story, size, bar patterns top/bottom, stirrup dia/spacing per zone).
  - LOG: timestamped entries for info/warnings/errors.
- UX: usable by another engineer without author guidance; failure rows clearly marked; inline “how to use” notes.

### 2.3 Structural Library Scope
- Pure IS 456 logic for rectangular beams (geometry helpers, flexure, shear).
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
2) Flexure helpers: Ast for singly reinforced; limiting moment; flag when Mu > Mu_lim; (future) doubly reinforced helper.  
3) Shear helpers: τv from Vu,b,d; τc from Table 19 (with pt clamp and interpolation in pt); Vc; Vus; stirrup capacity/spacing with code limits.  
4) Validation/error conventions: detect impossible inputs (negative dims, cover ≥ D, invalid grades); return clear status codes/flags, no UI.

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

## 6. ETABS Integration Approach
- v0: simple — user exports ETABS tables to CSV/Excel; macro maps columns into BEAM_INPUT. Library does not care about source.  
- Later: ETABS API or Python bridge. Current structure should make adding this layer straightforward.

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

**How to use this doc:**  
Reference it when prompting AI: e.g., “Use PROJECT_OVERVIEW.md as context. Act as DEV agent and design the detailed function list for the structural library,” or “Using PROJECT_OVERVIEW.md and TESTER role, propose a test matrix for v0 beams.”

---

**End of Project Overview**
