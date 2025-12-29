# BBS + DXF Improvement Plan (Beam-Only)

Goal: make BBS and DXF outputs fabrication-ready, deterministic, and consistent
with each other, without changing the current 3-layer architecture.

---

## Scope (v1.x)
- Beam-only (IS 456).
- Keep existing CLI (`design`, `bbs`, `dxf`, `job`) and schema flow.
- Improve correctness, consistency, and output contracts.

## Non-Goals (v1.x)
- No frame/analysis solver.
- No multi-code plugins.
- No heavy DXF rendering stack (PDF export is optional).

---

## Current Gaps (Summary)

### BBS
- Bar marks are not project-unique (marks reset per beam).
- Cut length math is simplified (hooks/bend deductions/stirrups).
- Rounding rules are implied, not documented or tested.
- Total weights are rounded per-bar, which can drift.

### DXF
- Bar marks are not embedded in callouts (no BBS/DXF linkage).
- Zone-specific callouts are limited.
- Text size/offsets are fixed; scaling can clash on small/large beams.
- Layer contract exists but is not validated by tests.

---

## Contracts to Freeze (v1.x)

1) **Bar mark identity**
- Deterministic and unique across a project.
- One format, used in both BBS and DXF.

2) **BBS line item schema**
- Fields, units, rounding rules, totals.
- Stable column names for CSV export.

3) **DXF contract**
- Layer names + minimum content.
- Text labels include bar marks and zones.

Contract doc: `docs/reference/bbs-dxf-contract.md`

4) **Rounding rules**
- Length rounding (mm) and weight rounding (kg).
- Defined once, reused across code + docs.

---

## Work Bundles (each can be done in one focused pass)

### Bundle A — Contracts + Bar Mark Spec
**Goal:** establish stable identity and output contracts.
- Define bar mark format (project-unique).
- Document BBS line-item schema + rounding rules.
- Document DXF layer + text contract (what must appear).
- Align docs/specs to existing modules.

**Files:** `docs/reference/`, `docs/specs/v0.7_DATA_MAPPING.md`, `docs/reference/error-schema.md` (if needed for error codes)
**Tests:** none (docs-only)
**Done when:** contract doc + references are linked and consistent.

---

### Bundle B — Bar Mark Generator + BBS Wiring
**Goal:** deterministic bar marks across beams.
- Implement a single bar mark generator.
- Ensure BBS line items use the generator.
- Add tests for uniqueness across multi-beam BBS.

**Files:** `Python/structural_lib/bbs.py`, tests in `Python/tests/`
**Tests:** unit tests for mark format + uniqueness
**Done when:** same inputs always yield same marks, no duplicates in multi-beam.

---

### Bundle C — BBS Cut-Length + Weight Correctness
**Goal:** fabrication-ready lengths and weights.
- Update hook and bend deductions (IS 2502 / SP 34).
- Improve stirrup cut length (cover + dia + bend radius).
- Compute total weight from total length; round at summary.
- Document the math in code comments.

**Files:** `Python/structural_lib/bbs.py`
**Tests:** known example fixtures for lengths + totals
**Done when:** lengths/weights match expected for sample beams.

---

### Bundle D — DXF Callouts + Scaling
**Goal:** DXF outputs are readable and traceable.
- Embed bar marks in callouts (top/bottom/stirrups).
- Zone-specific callouts (start/mid/end).
- Scale text/offsets based on beam size.

**Files:** `Python/structural_lib/dxf_export.py`
**Tests:** DXF entity text content checks
**Done when:** callouts include bar marks and pass content tests.

---

### Bundle E — DXF/BBS Consistency Check
**Goal:** verify marks match across outputs.
- Add a CLI or helper to compare BBS vs DXF marks.
- Report missing/extra marks.

**Files:** `Python/structural_lib/dxf_export.py`, `Python/structural_lib/bbs.py`, CLI in `Python/structural_lib/__main__.py`
**Tests:** fixture-based comparison tests
**Done when:** mismatches are reported deterministically.

---

### Bundle F — DXF Deliverable Polish (Optional)
**Goal:** improve output deliverables without new dependencies.
- Title block polish, line weights, scale notation.
- Optional render to PNG/PDF via existing script.

**Files:** `Python/structural_lib/dxf_export.py`, `scripts/dxf_render.py`
**Tests:** smoke tests + manual viewer check
**Done when:** sample DXF is readable in CAD viewer.

---

## Suggested Order
Bundle A → Bundle B → Bundle C → Bundle D → Bundle E → Bundle F

This keeps contracts stable before changing outputs.
