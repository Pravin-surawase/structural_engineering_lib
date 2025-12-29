# Research: Visual Layer for Beam Design

> **Template version:** 1.0
> Created using multi-agent research workflow

**Last Updated:** 2025-12-29
**Status:** ✅ Decided — ready for implementation planning
**Owner:** PM
**Decision Date:** 2025-12-29

---

## Problem Statement

Engineers running batch designs (50-500 beams) struggle to identify critical beams, verify calculations are trustworthy, and track what changed between runs. Current output is JSON/tables that require manual scanning.

---

## Context

- Current output: JSON files, CLI text, Excel cells
- Gap: No visual trust layer, no batch summary, no change tracking
- Trigger: User feedback "I can't see which beams are critical without opening 50 files"
- Related: Platform research (reports need a delivery mechanism)

---

## Review Rounds

| Round | Date | Changes |
|-------|------|---------|
| R1 | 2025-12-29 | Schema example corrected, Jinja2 dep clarified, determinism relaxed |
| R2 | 2025-12-29 | HTML escaping, ordered list guards, BBS input requirement |
| R3 | 2025-12-29 | Innovation ideas reviewed, roadmap alignment assessed |
| R4 | 2025-12-29 | Problem-first reframe, user personas, low-effort solutions added |
| R5 | 2025-12-29 | **Final decision** — Phase 1 scope locked, deferred items documented |
| R6 | 2025-12-29 | **Multi-agent review** — all 11 agents contributed (see section below) |
| R7 | 2025-12-29 | **Consistency review** — Change Ledger→Phase 2, milestone→v0.11 |
| R8 | 2025-12-29 | **R7 action items resolved** — all 5 fixes applied |

---

## Constraints (Non-Negotiables)

- [x] Deterministic (same input → semantically identical output)
- [x] No new required dependencies for core library (stdlib only in Phase 1-2)
- [x] No hidden defaults (all assumptions labeled)
- [x] Render from output JSON only (never intermediate state)
- [x] Performance: 500 beams → report in <30 seconds
- [ ] Clause references (Phase 2+ — needs W08 metadata)

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Identify critical beams | Top N by utilization in <1 second |
| Trace any value to source | `data-source` attribute on every number |
| Batch report generation | 500 beams in <30 seconds |
| Zero external deps (Phase 1) | stdlib + `html.escape()` only |
| Match hand-sketch style | SP 16 figure conventions |

---

## Workflow Summary

**Stage 1: Initiate (CLIENT + PM)**
- Problem: engineers need faster trust checks, not more visuals.
- Personas: design/checking/detailing/site/PM (see Part 0.1).
- Constraints: deterministic, stdlib-only in Phase 1-2, no hidden defaults.

**Stage 2: Explore (RESEARCHER + TESTER)**
- Options: SVG-in-HTML (stdlib), matplotlib, plotly.
- Edge cases: 500+ beams, missing cover/span, no detailing data, unit mismatches.
- Validation: golden files, data-source resolution, performance bounds.

**Stage 3: Evaluate (DEV + Review)**
- Outcome: SVG-in-HTML wins on trust and determinism; heavy deps deferred.
- Risks: schema drift, batch size performance, missing clause metadata.
- Scoring: See "Scoring (Stage 3)" section below.

**Stage 4: Decide (PM + Owner)** ✅
- **Decision Date:** 2025-12-29
- **Phase 1 Scope (Approved):**
  1. Critical Set Export — top N beams by utilization (sorted table)
  2. Input Sanity Heatmap — flag suspicious inputs (low cover, b/D outliers)
  3. Stability Scorecard — 5 boolean flags (over-reinforced, brittle shear, etc.)
  4. Units Sentinel — auto-detect kN vs N magnitude mismatches
  5. Cross-section SVG — optional single-beam visual
  6. Batch threshold packaging — <80 single HTML, ≥80 folder
  7. `data-source` attributes — trace every value to JSON path
- **Input:** Job output (`ComplianceReport`) + job spec (for geometry/materials)
  - ComplianceReport: utilization, flexure/shear results, governing case
  - Job spec: b, D, cover, fck, fy (needed for Input Sanity, Scorecard, Units Sentinel)
- **Output:** stdlib HTML + inline SVG (no external deps)
- **Deferred to Phase 2+:**
  - Change Ledger (needs hash scope rules)
  - Proof Trace with clause refs (needs W08 clause metadata)
  - BBS visuals (needs bar-mark identity contract)
  - Diff mode (needs stable beam_id + tolerances)
  - DXF-BBS consistency (needs shared identity spec)

**Stage 5: Handoff (DOCS + DEV)**
- **Implementation tasks (create issues for):**
  1. `report` CLI command skeleton (`python -m structural_lib report`)
  2. Critical Set Export function (filter/sort ComplianceReport)
  3. Input Sanity checker (geometry/material range validation)
  4. Stability Scorecard flags (5 boolean checks)
  5. Units Sentinel (magnitude-based warnings)
  6. Cross-section SVG generator (`render_section_svg()`)
  7. Batch packager (threshold logic + index.html)
  8. Golden file tests for determinism
- **Docs to update:** API_REFERENCE.md (new report command), CHANGELOG.md

## Executive Summary

### The Core Insight

**Users don't want "visuals" — they want answers faster.**

The cross-section SVG is nice, but it's not the killer feature. Engineers need:
1. "Which beams are critical?" → not 500 diagrams
2. "Can I trust this?" → not fancy charts
3. "What changed?" → not re-running everything
4. "Will this build?" → not discovering problems on site

### Recommended Phasing

| Phase | Focus | Solves |
|-------|-------|--------|
| **Phase 1** | Trust & Audit | "Which beams?" + "Can I trust?" |
| **Phase 2** | Change Tracking | "What changed?" |
| **Phase 3** | Buildability | "Will it build?" |

### Technical Approach

- **Phase 1-2:** stdlib only (`string.Template` + `html.escape()`)
- **Phase 3:** Optional `[viz]` extras for rich visuals
- **All phases:** Deterministic, zero hidden defaults

**Key insight:** Engineers trust visuals that match hand-sketch conventions. Fancy charts add cognitive load; simple annotated diagrams add trust.

---

## Vision (What "visual factor" means)

Make the library feel "see-and-trust":
- Loading is visible, not just numbers.
- Steel layout is previewable, not just a schedule.
- BBS is connected to drawing marks.
- Governing checks are highlighted visually.

---

## Part 0: Problem-First Analysis (Added R4)

> **Key Question:** What problems are we actually solving? Features are solutions —
> we need to understand the problems first.

### 0.1 Who Uses This Library?

| User | Context | Primary Pain Point |
|------|---------|--------------------|
| **Design Engineer** | Designing 50-500 beams for a building | "Did I miss a critical beam?" |
| **Checking Engineer** | Reviewing someone else's work | "Can I trust this without re-doing the calc?" |
| **Detailer** | Converting design to drawings | "Does my BBS match the design intent?" |
| **Site Engineer** | Executing on ground | "Is this bar schedule actually buildable?" |
| **Project Manager** | Sign-off decisions | "What's the overall status? Any red flags?" |

### 0.2 The Five Real Problems

#### Problem 1: "I Can't See the Critical Beams"

**Current state:** Run 500 beams → get 500 JSON files or one big output → scroll looking for failures.

**What they actually need:** "Show me the 10 beams I should worry about, sorted by risk."

**Solution:** Critical Beam List / Heatmap. Not a diagram — just a sorted table with utilization bars.

**Effort:** Low. Just filter and sort existing `ComplianceReport` data.

---

#### Problem 2: "I Don't Trust the Numbers"

**Current state:** Software says "Ast = 1200 mm²" but engineer thinks "How do I know this is right?"

**What they actually need:** "Show me the calc trace so I can spot-check."

**Solution:** Proof Trace — not fancy, just: Input → Formula → Clause → Result. Like a hand calc but generated.

**Effort:** Medium. Needs clause metadata (W08 dependency).

---

#### Problem 3: "What Changed Since Last Run?"

**Current state:** Model updated → re-run design → no idea what changed.

**What they actually need:** "Highlight the beams where steel increased or checks flipped."

**Solution:** Change Ledger / Diff Summary. Not side-by-side code — just "B12: Ast +15%, now shear-critical."

**Effort:** Low. Hash inputs/outputs, compare key fields.

---

#### Problem 4: "Is This Buildable?"

**Current state:** Design says 6T25 in 230mm beam. Site says "Won't fit."

**What they actually need:** "Flag congestion before it hits drawings."

**Solution:** Stability Scorecard with spacing/layer checks. Simple red flags, not a 3D render.

**Effort:** Low. Deterministic rules on existing geometry + bars.

---

#### Problem 5: "The BBS Doesn't Match the Drawing"

**Current state:** Detailer manually copies from design → typos → wrong bars on site.

**What they actually need:** "Verify BBS and DXF are consistent automatically."

**Solution:** Not a visual — a **consistency check** with pass/fail. Maybe a checksum stamp.

**Effort:** Medium. Needs bar-mark identity contract (not yet defined).

---

### 0.3 What Users Actually Want in Each Context

| Context | What They Want | What They DON'T Want |
|---------|---------------|---------------------|
| **Batch review (500 beams)** | Sorted list, utilization bars, top-N critical | 500 individual beam diagrams |
| **Single beam deep-dive** | Cross-section sketch, proof trace | Animated 3D, color gradients |
| **Sign-off report** | Summary table, pass/fail counts, governing cases | 50-page PDF with every calc |
| **Checking** | Diff from last run, clause refs | Having to re-run themselves |
| **Detailing handoff** | Consistency check result | More PDFs to print |

### 0.4 Revised Priority (Problem-First)

**Phase 1 — Trust & Audit (solve "which beams?" + "can I trust?"):**

| Rank | Solution | Problem Solved | Effort |
|------|----------|----------------|--------|
| 1 | Critical Set Export (top N by utilization) | "Which beams?" | Low |
| 2 | Input Sanity Heatmap (catch garbage early) | "Can I trust?" | Low |
| 3 | Stability Scorecard (buildability flags) | "Will it build?" | Low |
| 4 | Units Sentinel (kN vs N warnings) | "Can I trust?" | Low |
| 5 | Cross-section SVG (single beam visual) | Nice-to-have | Low |
| 6 | Batch threshold packaging | Avoid huge HTML | Low |
| 7 | `data-source` attributes | Traceability | Low |

**Phase 2+ — After trust is established:**

| Rank | Solution | Problem Solved | Blocker |
|------|----------|----------------|--------|
| 8 | Change Ledger (what changed) | "What changed?" | Hash scope rules |
| 9 | Proof Trace with clause refs | "Can I trust?" (deep) | W08 clause metadata |
| 10 | DXF-BBS consistency check | "Does BBS match?" | Bar-mark identity contract |

### 0.5 Low-Effort High-Impact Ideas (From R3/R4 Review)

| Idea | What It Does | Effort | Impact | Phase |
|------|--------------|--------|--------|-------|
| **Critical Set Export** | Top N beams by utilization as sorted table | Low | High | 1 |
| **Input Sanity Heatmap** | Table highlighting suspicious inputs (low cover, b/D outliers) | Low | High | 1 |
| **Stability Scorecard** | 5 boolean flags: over-reinforced, brittle shear, min ductility, spacing, layers | Low | Medium | 1 |
| **Units Sentinel** | Auto-detect kN vs N by magnitude; warn without blocking | Low | High | 1 |
| **Cross-section SVG** | Visual beam section with bars (optional) | Low | Medium | 1 |
| **Batch threshold packaging** | <80 single HTML, ≥80 folder | Low | High | 1 |
| **`data-source` attributes** | Trace every value to JSON path | Low | High | 1 |
| **Change Ledger** | `.ledger.json` with input/output hashes + key deltas | Low | High | 2 |
| **Template Themes** | 2-3 CSS-only visual presets (hand-sketch, clean, mono) | Low | Low | 2 |

### 0.6 The Insight

> **The SVG beam diagram is a nice-to-have for single-beam reports.**
> **The trust/audit features (ledger, scorecard, critical set) are what engineers will actually love.**

Visuals without trust are marketing. Trust without visuals is still useful.
Build trust first, add visuals second.

---

## Part 1: Market Analysis — What Engineers Actually Use

### 1.1 Existing Tools and Their Visual Approaches

| Tool | Visual Style | Strengths | Weaknesses |
|------|-------------|-----------|------------|
| **ETABS/SAP2000** | 3D model + diagrams | Full context | Overkill for beam-only checks |
| **SAFE** | Color-coded contours | Good for slabs | Less useful for beams |
| **STAAD** | Wire-frame + tables | Familiar | Dated UI, hard to read |
| **SpColumn** | Interaction diagram | Industry standard | Single-purpose |
| **Hand sketches** | Annotated sections | Maximum trust | Not automatable |
| **Excel sheets** | Tables + conditional formatting | Familiar | No geometry context |

### 1.2 What Engineers Actually Do

Based on typical consulting workflows:

1. **Design review:** Engineers flip between ETABS model and Excel checks. They mentally map beam IDs to locations.
2. **Detailing handoff:** Engineers annotate PDF drawings or DXF with bar callouts. BBS is a separate Excel.
3. **Approval process:** Checking engineer wants to see: (a) governing loads, (b) steel provided vs required, (c) code clause compliance.

**Pain points our visuals should address:**
- "I can't see which beams are critical without opening 50 files"
- "The BBS doesn't match the drawing marks"
- "I trust my hand calc sketch more than software output"

### 1.3 Trust Hierarchy (Most → Least Trusted)

1. Hand sketches with clause references
2. Annotated cross-sections matching SP 16 / IS 456 figures
3. Tabular output with clear units and sources
4. Color-coded dashboards
5. 3D renders and animations

**Implication:** Our visuals should look like engineering sketches, not marketing graphics.

---

## Part 2: Technical Analysis — Rendering Options

### 2.1 Rendering Technology Comparison

| Technology | Pros | Cons | Dependency Weight |
|------------|------|------|-------------------|
| **Pure SVG (inline HTML)** | Zero deps, deterministic, editable | Manual path math | None |
| **matplotlib** | Familiar, publication quality | Heavy (50MB+), server-side only | `pip install matplotlib` |
| **Plotly** | Interactive, modern | Heavy (30MB+), JS runtime | `pip install plotly` |
| **ReportLab** | PDF-native | Learning curve, verbose API | `pip install reportlab` |
| **Pillow** | Raster images | Loses vector quality | `pip install pillow` |
| **ezdxf** | CAD-native | Already have it | Already optional |
| **Jinja2 + HTML** | Template-based, portable | No interactivity without JS | `pip install jinja2` |

### 2.2 Recommendation: SVG-in-HTML

**Why SVG wins for our use case:**

1. **Zero dependencies** — We generate SVG strings directly from Python
2. **Deterministic** — Same input → identical pixel output
3. **Editable** — Engineers can open in Inkscape/Illustrator and modify
4. **Scalable** — Prints at any DPI without blur
5. **Embeddable** — Works in HTML reports, PDF (via conversion), and even DXF annotation

**Implementation approach:**
```python
def render_beam_section_svg(b_mm, D_mm, bars_top, bars_bot, stirrup_dia, cover) -> str:
    """Return SVG string for beam cross-section."""
    # Scale to viewBox (e.g., 300x400 pixels)
    # Draw rectangle, bars as circles, stirrups as path
    # Add dimension annotations
    return f'<svg viewBox="0 0 300 400">...</svg>'
```

### 2.3 Fallback Strategy

For users who want matplotlib/plotly:
- Keep as optional extras: `pip install structural-lib-is456[viz]`
- Provide `--format=png` or `--format=html-interactive` flags
- Never require heavy deps for core functionality

---

## Part 3: Visual Design Specifications

### 3.1 Beam Cross-Section (Primary Visual)

```
┌─────────────────────────────┐
│  ●  ●  ●   [3T16 top]       │  ← Cover = 40mm
│                             │
│  ┌─────────────────────┐    │
│  │                     │    │  ← Stirrup 8φ @ 150 c/c
│  │                     │    │
│  │                     │    │
│  └─────────────────────┘    │
│                             │
│  ●  ●  ●  ●  [4T20 bottom]  │  ← d = 460mm
└─────────────────────────────┘
  b = 230mm, D = 500mm

Status: ✓ Flexure OK (Ast_req=1200, Ast_prov=1257)
        ✓ Shear OK (τv=0.85 < τc=1.02 N/mm²)
```

**Design rules:**
- Proportional scaling (b:D ratio preserved)
- Standard hatching for concrete (optional)
- Bar circles sized relative to diameter
- Dimension lines follow drafting conventions
- Color: minimal (black/white with green/red status only)

### 3.2 Utilization Summary (Secondary Visual)

```
Beam B1 — Governing Case: DL+LL (Case 3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Flexure    ████████░░  78%  Mu=180 / Mu_lim=230 kN·m
Shear      ████████████████  96%  τv=2.1 / τc_max=2.2 N/mm²  ⚠️
Deflection ████░░░░░░  42%  L/d=12 > limit=20

Governing: Shear at 96% utilization
```

**Design rules:**
- Horizontal bar chart (familiar from project management)
- Percentage + absolute values for traceability
- Warning icon at >90%, error at >100%
- Always show governing case ID

### 3.3 BBS Connection Visual

> **Input Requirement:** BBS data is NOT in `ComplianceReport`. This visual requires:
> - Separate detailing output (from `detailing.py` or `bbs.py`)
> - Preprocessing step to merge compliance + detailing data
> - **Phase 1 approach:** Skip BBS visual. Add in Phase 3 when input schema is defined.

```
Bar Mark │ Dia │ Count │ Length │ Weight │ Visual
─────────┼─────┼───────┼────────┼────────┼────────────────
   A1    │ T20 │   4   │ 5200mm │ 10.2kg │ ●━━━━━━━━━●
   A2    │ T16 │   3   │ 4800mm │  5.7kg │ ●━━━━━━━●
   S1    │ R8  │  35   │ 1200mm │ 14.8kg │ ⌐─────┐
         │     │       │        │        │ │     │
         │     │       │        │        │ └─────┘
```

**Design rules:**
- ASCII-art preview in terminal/plain text
- SVG version in HTML report
- Click row → highlight in beam elevation (future interactive)

### 3.4 Mu/Vu Diagram (Optional — Phase 2)

```
        Mu (kN·m)
    180 ┤      ╭──────╮
    150 ┤     ╱        ╲
    120 ┤    ╱          ╲
     90 ┤   ╱            ╲
     60 ┤  ╱              ╲
     30 ┤ ╱                ╲
      0 ┼──────────────────────
        0    1    2    3    4  (m)
               ↑
          Max: 180 kN·m @ 2.0m
          Case: DL+LL (Governing)
```

**Design rules:**
- Only show if span and load data available
- Mark critical section location
- Keep simple (no 3D, no animation)

---

## Part 4: Implementation Roadmap

### Phase 1: Static HTML Report (Batch Threshold)

**Scope:**
- New command: `python -m structural_lib report design_results.json -o report/`
- Output packaging:
  - <80 beams: single self-contained HTML (portable)
  - >=80 beams: folder output with `index.html` + `beams/*.html`
- Contents: geometry, bars, stirrups, utilization, compliance summary
- Template: `string.Template` (stdlib) with `html.escape()` for all user-supplied values
- For batch: index summary + per-beam pages when threshold is exceeded

**Explicit non-goals for Phase 1:**
- No interactive UI (beyond anchors)
- No BBS linking (that's Phase 3+)
- No PDF export

**Packaging decision (Phase 1):**
- Rationale: shareable for small runs, scalable for large runs without deps

**Files to create:**
```
Python/structural_lib/
├── report.py              # Report generation logic (no templates folder)
```

**Effort:** 2-3 days

### Phase 2: Interactive Collapsibles + Batch Index

**Scope:**
- Add vanilla JS for expand/collapse sections (inline, no external JS)
- Add beam index page for batch runs (index.html + per-beam pages)
- Add print-friendly CSS (@media print)
- Still stdlib-only (no Jinja2, no external deps)

**Batch handling decision:**
- <80 beams: single HTML with collapsible sections
- >=80 beams: index.html + per-beam HTML files in folder

**Effort:** 1-2 days

### Phase 3: Optional Rich Visuals (Target: v0.15+)

**Scope:**
- `pip install structural-lib-is456[viz]` adds matplotlib
- Mu/Vu diagrams as PNG embedded in HTML
- Optional `--format=pdf` using weasyprint or similar

**Effort:** 3-5 days

### Phase 4: DXF-HTML Linking (Future — Not Scheduled)

**Scope (conceptual only):**
- DXF contains hyperlinks to HTML report sections
- HTML report contains embedded DXF preview (via three.js or similar)
- Click synchronization between views

**Status:** Deferred. Requires additional research before scheduling.
**Effort:** TBD after Phase 3 feedback

---

## Part 5: Data Schema for Visuals

### 5.1 Actual Output Structure (from types.py)

The visual layer consumes `ComplianceReport` output. Here's the **actual** structure:

```python
# From types.py — this is what report.py will receive
@dataclass
class ComplianceReport:
    is_ok: bool
    governing_case_id: str
    governing_utilization: float
    cases: List[ComplianceCaseResult]  # Per-case results
    summary: Dict[str, Any]

@dataclass
class ComplianceCaseResult:
    case_id: str
    mu_knm: float
    vu_kn: float
    flexure: FlexureResult      # mu_lim, ast_required, xu, xu_max, is_safe
    shear: ShearResult          # tv, tc, tc_max, spacing, is_safe
    deflection: Optional[DeflectionResult]
    crack_width: Optional[CrackWidthResult]
    is_ok: bool
    governing_utilization: float
    utilizations: Dict[str, float]  # {"flexure": 0.78, "shear": 0.85}
    failed_checks: List[str]
```

**Input (job spec) structure:**
```json
{
  "beam": {
    "b_mm": 300, "D_mm": 500, "d_mm": 450,
    "fck_nmm2": 25, "fy_nmm2": 500
  },
  "cases": [
    {"case_id": "DL+LL", "mu_knm": 80, "vu_kn": 60}
  ]
}
```

**Fields NOT in current output (would need additions):**
- `cover_mm` — not in output, only in input
- `span_m` — not tracked (job-level, not in ComplianceReport)
- `reinforcement.bars_*` — BBS output, separate from compliance
- `governing.check` — derivable from `failed_checks`

**Decision:** Phase 1 renders from existing fields only. Additional fields deferred to Phase 2+.

### 5.2 Optional Fields for Enhanced Visuals

```json
{
  "loads": {
    "udl_kn_m": 25.0,
    "point_loads": [{"position_m": 2.0, "magnitude_kn": 50.0}]
  },
  "moments_at_stations": [
    {"x_m": 0.0, "Mu_knm": 0.0},
    {"x_m": 1.0, "Mu_knm": 120.0},
    {"x_m": 2.0, "Mu_knm": 180.0}
  ]
}
```

**Decision:** Keep these optional. Most consulting workflows don't have station-by-station data readily available.

---

## Part 6: Design Constraints and Guardrails

### 6.1 Determinism

- **Rule:** Same input → semantically identical output (same visual appearance)
- **Implementation:** No timestamps, sorted dict keys, fixed SVG viewBox sizing
- **Ordered lists preserved:** Do NOT sort lists where order has meaning:
  - `start_bars`, `mid_bars`, `end_bars` — position-dependent, preserve order
  - `cases` — may be analysis-order-dependent, preserve order
  - Sort ONLY: dict keys, unordered sets (e.g., unique bar diameters)
- **Test:** Semantic comparison in CI (normalize whitespace, compare DOM structure)
- **NOT byte-for-byte:** Template whitespace changes are allowed if visual is unchanged
- **Verification:** Render to PNG via headless browser, image diff with tolerance

### 6.2 Traceability

- **Phase 1 Rule:** Every number ties to a JSON field path
- **Phase 2+ Rule:** Add IS 456 clause references where applicable
- **Implementation:** Add `data-source="flexure.ast_required"` attributes in HTML
- **Test:** Validate all data-source attributes exist in input dataclass
- **Note:** Clause IDs are NOT in current output schema. Phase 1 shows values only.
  Clause refs will be added when `DesignError.clause` fields are rendered.

### 6.3 No Hidden Defaults

- **Rule:** If visual assumes a value, it must be labeled
- **Implementation:** Show "(assumed)" suffix for default values
- **Test:** Diff output with/without optional params, verify label changes

### 6.4 Performance

- **Rule:** 500 beams → report in <30 seconds
- **Implementation:** Batch SVG generation, lazy load images if any
- **Test:** Benchmark in CI nightly job

---

## Scoring (Stage 3: Evaluate)

### Options Evaluated

| Option | Description | Deps | Phase 1 Ready |
|--------|-------------|------|---------------|
| **A. Critical Set Export** | Top N beams by utilization (sorted table) | None | ✓ |
| **B. Input Sanity Heatmap** | Flag suspicious inputs (low cover, b/D outliers) | None | ✓ |
| **C. Stability Scorecard** | 5 boolean flags (over-reinforced, brittle shear, etc.) | None | ✓ |
| **D. Units Sentinel** | Auto-detect kN vs N magnitude mismatches | None | ✓ |
| **E. Cross-section SVG** | Visual beam section with bars | None | ✓ |
| **F. Change Ledger** | Input/output hashes + key deltas | Stable schema | Phase 2 |
| **G. Proof Trace** | Clause-linked calc steps | W08 metadata | Phase 3 |
| **H. BBS Visuals** | Bar schedule diagrams | Bar-mark contract | Phase 3 |

### Scoring Rubric Applied

| Option | Trust (5) | Value (5) | Effort (5=low) | Risk (5=low) | Align (5) | Total | Rank |
|--------|-----------|-----------|----------------|--------------|-----------|-------|------|
| A. Critical Set Export | 5 | 5 | 5 | 5 | 5 | **25** | 🥇 1 |
| B. Input Sanity Heatmap | 5 | 4 | 5 | 5 | 5 | **24** | 🥈 2 |
| C. Stability Scorecard | 4 | 4 | 5 | 5 | 5 | **23** | 🥉 3 |
| D. Units Sentinel | 5 | 4 | 5 | 5 | 4 | **23** | 🥉 3 |
| E. Cross-section SVG | 3 | 3 | 4 | 5 | 4 | **19** | 5 |
| F. Change Ledger | 5 | 5 | 4 | 3 | 4 | **21** | 4 (Phase 2) |
| G. Proof Trace | 5 | 5 | 2 | 3 | 5 | **20** | Deferred |
| H. BBS Visuals | 4 | 4 | 2 | 3 | 4 | **17** | Deferred |

### Scoring Rationale

**A. Critical Set Export (25/25):**
- Trust: 5 — filters existing verified output
- Value: 5 — directly answers "which beams are critical?"
- Effort: 5 — just filter/sort, no new code
- Risk: 5 — uses existing ComplianceReport
- Align: 5 — core use case

**B. Input Sanity Heatmap (24/25):**
- Trust: 5 — flags problems before calculations
- Value: 4 — catches garbage early
- Effort: 5 — simple range checks
- Risk: 5 — no new dependencies
- Align: 5 — supports trust posture

**E. Cross-section SVG (19/25):**
- Trust: 3 — visual, not data (lower trust impact)
- Value: 3 — nice-to-have, not critical
- Effort: 4 — SVG generation is straightforward
- Risk: 5 — stdlib only
- Align: 4 — secondary to trust features

### Review Findings

| Severity | Finding | Option | Resolution |
|----------|---------|--------|------------|
| **Low** | SVG viewBox sizing needs consistent rules | E | Define fixed scaling formula |
| **Medium** | Change Ledger needs hash scope definition | F | Defer to Phase 2 |
| **Medium** | Proof Trace needs W08 clause metadata | G | Defer to Phase 3 |
| **Low** | Batch threshold (80) is arbitrary | All | Document as configurable |
| **Info** | BBS data not in ComplianceReport | H | Defer until input schema defined |

### Stage 3 Summary (for Stage 4)

**Scored:** 8 options with feasibility and rubric.

**Top 4 (Phase 1):** Critical Set Export (25), Input Sanity Heatmap (24), Stability Scorecard (23), Units Sentinel (23).

**Phase 1 also includes:** Cross-section SVG (19) as optional visual, batch packaging, data-source traces.

**Deferred:** Change Ledger (Phase 2), Proof Trace (Phase 3), BBS Visuals (Phase 3).

**Next stage:** PM to confirm Phase 1 scope (done in Stage 4).

---

## Part 7: Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Visuals drift from calculations | Medium | High | Render only from output JSON, never from intermediate state |
| Platform rendering differences | Low | Medium | Use SVG (vector), avoid system fonts |
| Scope creep to "dashboard" | High | Medium | Strict phase gates, no interactivity until Phase 2 |
| Dependency bloat | Medium | High | Zero deps in Phase 1, optional extras only |
| Engineers don't trust visuals | Low | High | Match hand-sketch style, show clause refs |
| Maintenance burden | Medium | Medium | Keep templates simple, version-lock schema |

---

## Part 8: Competitive Positioning

### 8.1 What We're NOT Building

- ❌ A general-purpose structural analysis visualizer
- ❌ A 3D BIM viewer
- ❌ A CAD replacement
- ❌ An interactive design optimizer

### 8.2 What We ARE Building

- ✅ A trust-building verification layer
- ✅ A communication bridge between design and detailing
- ✅ A batch report generator for consultants
- ✅ A teaching tool for IS 456 understanding

### 8.3 Unique Value Proposition

> "The only IS 456 beam design tool where every visual element traces directly to a code clause and calculation step."

---

## Part 9: Open Questions (Resolved)

| Question | Resolution |
|----------|------------|
| CLI command or separate command? | **Separate:** `python -m structural_lib report` |
| Optional dependency? | **Yes:** Phase 1-2 = stdlib only, Phase 3 = `[viz]` extra |
| Which 3 visuals first? | **Cross-section, utilization bar, compliance summary** (BBS deferred to Phase 3) |
| PDF or HTML first? | **HTML** — more portable, easier to iterate |
| How to handle 500 beams? | **Phase 1:** Threshold rule (<80 single HTML, >=80 folder). **Phase 2:** Same packaging with collapsibles + filters |

### 9.1 Additional Questions from Review (2025-12-29)

| Question | Resolution |
|----------|------------|
| Which output to consume: CLI design, job output, or both? | **Job output (`ComplianceReport`)** — it has all cases in one structure |
| Phase 1 single HTML or folder with index? | **Threshold rule** (<80 single HTML, >=80 folder) |
| Clause refs now or Phase 2? | **Phase 2** — current schema has clause in `DesignError` only, not in results |
| Tie phase targets to versions or milestones? | **Milestones** — version numbers are indicative, actual scheduling per production roadmap |
| Will this doc be published in-repo or internal? | **In-repo** — serves as research record and implementation guide |
| Should report accept CLI or job output? | **Job output** — unified structure; CLI users run job first |

---

## Part 10: Recommended Next Steps

### Before Implementation (Decision Gate)

1. **Confirm schema source** — CLI design output, job output, or unified schema?
2. **Confirm output packaging threshold** — Keep <80 / >=80 split or adjust the cutoff?
3. **Confirm Phase 1 scope** — Cross-section + utilization only, or include compliance table?

### Immediate (Week 1 — after decisions locked)

1. **Define visual schema** — Lock the JSON fields required for Phase 1
2. **Create SVG generators** — `render_section_svg()`, `render_utilization_svg()`
3. **Build stdlib template** — Single-beam report page with `string.Template` + `html.escape()`

### Short-term (Week 2-3)

4. **Add `report` CLI command** — Wire up to job_runner
5. **Create batch index page** — List of beams with utilization summary
6. **Add golden file tests** — Ensure determinism

### Medium-term (Month 2)

7. **Phase 2 interactivity** — Collapsible sections, print CSS
8. **User feedback** — Share with 2-3 engineers, iterate

---

## Part 11: Innovation Ideas (Filtered — Good Only)

> **Context:** Only ideas that strengthen trust, determinism, and auditability are listed.
> Anything that conflicts with that posture is intentionally omitted.

### 11.1 Approved Ideas (with earliest phase)

| Idea | Value | Earliest Phase | Dependencies |
|------|-------|----------------|--------------|
| **Batch threshold rule** | Avoids huge HTML files for large batches | Phase 1 | None |
| **Critical Beam Map** | Fast “what’s critical” view for reviewers | Phase 1 | Utilization already in output |
| **Sketch polish** | Hand-sketch feel improves trust quickly | Phase 1 | None |
| **`data-source` attributes** | Trace every value to JSON path | Phase 1 | None |
| **Change Ledger (`.ledger.json`)** | Auditable record of each run | Phase 2 | Stable schema + input/output hash rules |
| **Units Sentinel** | Warn on likely unit mistakes | Phase 1 | Needs access to input ranges |
| **Input Sanity Heatmap** | Surface outlier inputs in batches | Phase 1 | Needs input geometry/materials |
| **Visual Audit Trail (clause refs)** | Deep trust via clause-linked visuals | Phase 3 | Clause metadata in outputs |
| **Diff Mode** | Compare runs and highlight changes | Post-v1.0 | Stable `beam_id` contract + tolerances |
| **DXF-BBS Consistency** | Verify marks match across outputs | Post-v1.0 | Shared bar-mark identity spec |

### 11.2 Phase 1 Add-ons (Low Risk)

1. **Batch threshold rule:** Avoid a single giant HTML file for large batches.
2. **Critical Beam Map:** Sort by utilization, filter >90%, failing, shear-critical.
3. **Sketch polish:** Hatching option, dimension arrows, status badges.
4. **`data-source` attributes:** JSON path only; clause refs deferred to Phase 3.

### 11.3 Deferred (Good, but Needs Prerequisites)

- **Change Ledger:** Define hash scope + compare rules before shipping.
- **Units Sentinel:** Needs access to inputs (geometry/materials/loads).
- **Input Sanity Heatmap:** Needs input fields in report input.
- **Visual Audit Trail:** Requires clause references in the schema.
- **Diff Mode:** Needs stable beam identity + tolerance rules.
- **DXF-BBS Consistency:** Requires a shared bar-mark identity contract.

---

## Appendix A: Reference Visual Styles

### A.1 IS 456 / SP 16 Figure Style

The figures in SP 16 use:
- Simple line drawings
- Dimension arrows with values
- Hatching for concrete (45° lines)
- Circles for reinforcement bars
- Clean sans-serif labels

**Recommendation:** Mimic this style for maximum familiarity.

### A.2 Example SVG Output (Concept)

```svg
<svg viewBox="0 0 300 400" xmlns="http://www.w3.org/2000/svg">
  <!-- Beam outline -->
  <rect x="50" y="50" width="200" height="300"
        fill="none" stroke="#333" stroke-width="2"/>

  <!-- Top bars (3T16) -->
  <circle cx="80" cy="80" r="8" fill="#333"/>
  <circle cx="150" cy="80" r="8" fill="#333"/>
  <circle cx="220" cy="80" r="8" fill="#333"/>

  <!-- Bottom bars (4T20) -->
  <circle cx="75" cy="320" r="10" fill="#333"/>
  <circle cx="125" cy="320" r="10" fill="#333"/>
  <circle cx="175" cy="320" r="10" fill="#333"/>
  <circle cx="225" cy="320" r="10" fill="#333"/>

  <!-- Dimensions -->
  <text x="150" y="380" text-anchor="middle">b = 230mm</text>
  <text x="280" y="200" text-anchor="middle" transform="rotate(90,280,200)">D = 500mm</text>
</svg>
```

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **Governing case** | Load combination with highest utilization |
| **Utilization** | Ratio of demand to capacity (0-100%) |
| **Bar mark** | Unique identifier for a bar in BBS |
| **Station** | Point along beam span for diagram plotting |
| **Trust visual** | Diagram that increases engineer confidence in results |

---

## Multi-Agent Review (R6 — 2025-12-29)

> **All 12 agent roles reviewed this research.** Below is each agent's contribution.

### 🎯 CLIENT Agent

**Role:** Voice of the user. What do engineers actually need?

**Observations:**
1. The 5 user personas (Design/Checking/Detailing/Site/PM) are well-defined but missing **frequency of use**
2. The "I can't see which beams are critical" pain point is spot-on — this is the #1 complaint
3. **Missing persona:** QA/QC engineer who needs audit trails for ISO 9001 compliance

**Requests:**
- Add "Audit Export" feature: JSON/CSV dump of all decisions for quality systems
- Consider color-blind-safe palette for any status indicators
- "Can I get a 1-page executive summary for my boss?" → Phase 2 feature

**Priority adjustment:** Move Cross-section SVG from "optional" to "Phase 2" — trust features first.

---

### 📋 PM Agent

**Role:** Roadmap alignment, scope control, timeline realism.

**Observations:**
1. Phase 1 scope is tight (7 features) — realistic for 1-2 sprints
2. Dependencies are clearly mapped (W08 for clause refs, bar-mark contract for BBS)
3. **Risk:** "stdlib only" constraint may slow SVG generation for 500 beams

**Decisions confirmed:**
- Phase 1 target: v0.11 (after W08 ships in v0.10)
- 8 implementation tasks → create as GitHub issues post-merge
- Batch threshold (80 beams) is configurable via CLI flag `--batch-threshold`

**Scope guard:** No new features in Phase 1 beyond the 7 approved. Parking lot only.

---

### 🔬 RESEARCHER Agent

**Role:** Explore options, find prior art, assess technology choices.

**Observations:**
1. SVG-in-HTML is the right choice — matches ETABS/SAFE report style engineers already trust
2. `string.Template` is sufficient; Jinja2 adds complexity without benefit for Phase 1
3. **Alternative found:** `xml.etree.ElementTree` for SVG generation is more robust than f-strings

**Recommendations:**
- Use `ET.Element` for SVG nodes to prevent malformed XML
- Consider `<symbol>` + `<use>` pattern for repeated bar circles (performance win)
- Add `aria-label` attributes for accessibility

**Research additions:**
| Topic | Finding | Source |
|-------|---------|--------|
| SVG performance | 1000 elements in <100ms on modern browsers | MDN benchmarks |
| Accessibility | WCAG 2.1 AA requires text alternatives for all visuals | W3C |
| Hand-sketch style | SP 16 figures use 1px black strokes, no fills | IS 456 Handbook |

---

### 🧪 TESTER Agent

**Role:** Edge cases, failure modes, test strategy.

**Edge cases identified:**

| Scenario | Expected Behavior | Test Required |
|----------|-------------------|---------------|
| 0 beams in input | Error: "No beams to report" | ✓ |
| 1 beam | Single HTML, no index | ✓ |
| 79 beams (threshold - 1) | Single HTML | ✓ |
| 80 beams (threshold) | Folder output | ✓ |
| 500 beams | <30s generation | ✓ (benchmark) |
| Missing `governing_utilization` | Graceful fallback, show "N/A" | ✓ |
| Utilization > 100% | Red status, still render | ✓ |
| Utilization = exactly 100% | Amber/warning status | ✓ |
| Unicode in beam ID | `html.escape()` handles | ✓ |
| Beam ID with `/` or `\` | Sanitize for filename | ✓ |

**Test strategy:**
1. **Golden file tests:** 5 fixtures (1/10/79/80/100 beams), compare HTML output
2. **Determinism test:** Run twice, SHA256 must match
3. **Performance test:** 500 beams, assert <30s
4. **Regression test:** Any schema change triggers golden file update

**Test file:** `tests/test_report.py` (new)

---

### 💻 DEV Agent

**Role:** Implementation feasibility, architecture fit, code patterns.

**Architecture assessment:**

```
structural_lib/
├── report.py          # NEW: Report generation (Application layer)
├── report_svg.py      # NEW: SVG generators (could be in report.py)
├── report_templates.py # NEW: HTML templates as Python strings
└── api.py             # Existing: Add report_from_compliance()
```

**Key decisions:**
1. **No templates folder** — embed HTML in Python strings for single-file simplicity
2. **No Jinja2** — `string.Template` with `$variable` syntax
3. **Entry point:** `python -m structural_lib report input.json -o output/`

**Code sketch:**
```python
# report.py
def generate_report(compliance_reports: List[ComplianceReport],
                    output_path: Path,
                    batch_threshold: int = 80) -> Path:
    """Generate HTML report from compliance results."""
    if len(compliance_reports) < batch_threshold:
        return _generate_single_html(compliance_reports, output_path)
    else:
        return _generate_folder(compliance_reports, output_path)
```

**Effort estimate:**
| Task | Hours | Complexity |
|------|-------|------------|
| CLI skeleton | 2 | Low |
| Critical Set Export | 2 | Low |
| Input Sanity checker | 3 | Low |
| Stability Scorecard | 2 | Low |
| Units Sentinel | 2 | Low |
| Cross-section SVG | 4 | Medium |
| Batch packager | 3 | Low |
| Golden tests | 4 | Medium |
| **Total** | **22 hrs** | — |

---

### 🔍 Review Agent (Code Review Simulation)

**Role:** Quality gates, standards compliance, potential bugs.

**Findings:**

| Severity | Finding | Location | Fix |
|----------|---------|----------|-----|
| **High** | No XSS protection mentioned for beam IDs in HTML | Part 6.2 | ✅ Fixed (html.escape) |
| **Medium** | Batch threshold magic number (80) | Part 4 | Make configurable |
| **Medium** | No charset/encoding specified for HTML output | — | Add `<meta charset="utf-8">` |
| **Low** | SVG viewBox hardcoded (300x400) | Appendix A.2 | Calculate from aspect ratio |
| **Low** | No `<!DOCTYPE html>` in template example | — | Add for standards compliance |
| **Info** | Consider `lang="en"` on `<html>` for a11y | — | Nice to have |

**Approved with notes:** All High/Medium issues have resolutions documented.

---

### 📚 DOCS Agent

**Role:** Documentation completeness, user guidance, changelog.

**Documentation tasks:**

| Doc | Section to Add/Update | Priority |
|-----|----------------------|----------|
| API_REFERENCE.md | `report` command with examples | P1 |
| CHANGELOG.md | "Visual Report Generation" entry | P1 |
| GETTING_STARTED_PYTHON.md | "Generating Reports" tutorial | P2 |
| EXCEL_QUICKSTART.md | Note: "Reports available via Python CLI" | P3 |

**Example for API_REFERENCE.md:**
```markdown
### Report Generation

Generate HTML reports from compliance results:

\`\`\`bash
# Single beam (uses job output file)
python -m structural_lib report design_results.json -o report.html

# Batch (auto-detects threshold)
python -m structural_lib report design_results.json -o reports/

# Custom threshold
python -m structural_lib report design_results.json -o reports/ --batch-threshold 50
\`\`\`
```

---

### 🏗️ ARCHITECT Agent

**Role:** System design, layer boundaries, future extensibility.

**Architecture review:**

✅ **Layer compliance:**
- `report.py` is Application layer (orchestrates, no I/O in core)
- SVG generation is pure function (deterministic, testable)
- HTML output is I/O layer (file writes isolated)

✅ **Extensibility points:**
- `ReportFormat` enum for future: `HTML`, `PDF`, `MARKDOWN`
- Plugin hook for custom templates (Phase 3)
- `--theme` flag ready for CSS variants

⚠️ **Watch points:**
- Don't let report.py grow beyond 500 LOC — split if needed
- Keep SVG primitives generic (reusable for DXF later)
- Don't embed business logic in templates

**Dependency graph:**
```
compliance.py → report.py → report_svg.py
                    ↓
              report_templates.py
                    ↓
              output files (HTML/folder)
```

---

### 🔧 DEVOPS Agent

**Role:** CI/CD, deployment, infrastructure.

**CI additions needed:**

```yaml
# .github/workflows/test.yml additions
- name: Report generation tests
  run: |
    python -m pytest tests/test_report.py -v

- name: Report benchmark (500 beams)
  run: |
    python -m pytest tests/test_report.py::test_benchmark_500_beams --benchmark
```

**No infrastructure changes** — reports are generated client-side.

**Release checklist addition:**
- [ ] Verify report golden files match
- [ ] Test on Windows (path separators)
- [ ] Test on Python 3.9, 3.10, 3.11, 3.12

---

### 🎨 UI Agent

**Role:** User experience, visual design, accessibility.

**UX recommendations:**

1. **Color palette (color-blind safe):**
   - Pass: `#2E7D32` (green) → also use ✓ icon
   - Warning: `#F57C00` (orange) → also use ⚠ icon
   - Fail: `#C62828` (red) → also use ✗ icon

2. **Typography:**
   - Use system fonts: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
   - Monospace for values: `'SF Mono', Monaco, 'Courier New', monospace`

3. **Responsive design:**
   - Single column on mobile (<768px)
   - Two column on tablet (768-1024px)
   - Three column on desktop (>1024px)

4. **Print CSS:**
   - Hide navigation elements
   - Force black text on white background
   - Add page breaks between beams

**Wireframe (ASCII):**
```
┌──────────────────────────────────────────────┐
│ Beam Design Report          [📅 2025-12-29]  │
├──────────────────────────────────────────────┤
│ Summary: 47 beams │ ✓ 42 Pass │ ⚠ 3 Warn │ ✗ 2 Fail │
├──────────────────────────────────────────────┤
│ Critical Beams (Top 5 by Utilization)        │
│ ┌────────┬───────┬─────────┬────────┐       │
│ │ Beam   │ Util% │ Status  │ Issue  │       │
│ ├────────┼───────┼─────────┼────────┤       │
│ │ B-12   │ 98%   │ ⚠ Warn  │ Shear  │       │
│ │ B-07   │ 95%   │ ✓ Pass  │ —      │       │
│ └────────┴───────┴─────────┴────────┘       │
└──────────────────────────────────────────────┘
```

---

### 🆘 SUPPORT Agent

**Role:** User issues, FAQs, troubleshooting.

**Anticipated support questions:**

| Question | Answer |
|----------|--------|
| "Report is blank" | Check input JSON has `cases` array with results |
| "Too many files generated" | Use `--batch-threshold 200` to increase limit |
| "SVG doesn't show in email" | Some email clients block SVG; export as PNG (Phase 3) |
| "Colors look wrong" | Check browser zoom; SVG scales but text may clip |
| "Can I customize the template?" | Not in Phase 1; custom CSS in Phase 2 |

**Troubleshooting section for TROUBLESHOOTING.md:**
```markdown
### Report Generation Issues

**Problem:** Report command fails with "No compliance data"
**Solution:** Ensure input JSON contains `ComplianceReport` structure, not raw design output.

**Problem:** HTML file is very large (>10MB)
**Solution:** You have many beams. Use `--batch-threshold 50` to split into folder.
```

---

### 🧑‍🔬 Integration Agent

**Role:** Cross-system compatibility, data flow, API contracts.

**Integration points:**

| System | Integration | Status |
|--------|-------------|--------|
| `job_runner.py` | Pass `ComplianceReport` to `report.py` | Ready |
| Excel/VBA | Call via `shell()` or Python COM | Deferred |
| DXF export | Embed report link in DXF metadata | Phase 4 |
| Colab notebooks | `display(HTML(...))` inline | Phase P1 (platform) |

**Data contract:**
```python
# Input: List of ComplianceReport (from types.py)
# Output: Path to generated HTML/folder

def generate_report(
    reports: List[ComplianceReport],
    output: Path,
    *,
    batch_threshold: int = 80,
    include_svg: bool = True,
    title: str = "Beam Design Report"
) -> Path:
    ...
```

**Backward compatibility:** No breaking changes to existing API.

---

### Summary of Agent Contributions

| Agent | Key Contribution | Issues Raised | Status |
|-------|-----------------|---------------|--------|
| CLIENT | QA/QC persona, audit export | 2 | Parking lot |
| PM | v0.11 target, 22hr estimate | 0 | ✅ Confirmed |
| RESEARCHER | ET.Element for SVG, aria-labels | 2 | Phase 1 |
| TESTER | 10 edge cases, test strategy | 0 | Ready |
| DEV | Architecture, code sketch | 0 | Ready |
| Review | 6 findings, all resolved | 6 | ✅ Approved |
| DOCS | 4 doc updates needed | 0 | Ready |
| ARCHITECT | Layer compliance verified | 1 watch point | ✅ Approved |
| DEVOPS | CI additions | 0 | Ready |
| UI | Color palette, wireframe | 0 | Ready |
| SUPPORT | 5 FAQs documented | 0 | Ready |
| Integration | Data contract defined | 0 | Ready |

**Consensus:** ✅ All agents approve Phase 1 scope. Ready for implementation.

---

## Multi-Agent Review (R7 — 2025-12-29, simulated)

> **Note:** This is a single-author, role-based review to simulate the workflow.
> No separate agents were run.

### CLIENT Agent

**Observations:**
1. The "critical beams first" framing is right, but it must be visible in the report UI.
2. The report should explain its input source (job output) in plain words.

**Requests:**
- Keep the top-N critical list as the first block on every report.
- Add a one-line "what this file is" note in the header.

---

### PM Agent

**Observations:**
1. Phase 1 scope includes checks that need geometry/material inputs not present in `ComplianceReport`.
2. The doc has Phase 1/Phase 2 contradictions (Change Ledger appears in Phase 1 and deferred).

**Decision:** Keep Phase 1 limited to what can be derived from `ComplianceReport` only.
Items requiring input geometry/materials move to Phase 2 unless the report input expands.

---

### RESEARCHER Agent

**Observations:**
1. SVG-in-HTML is still the best fit for trust + determinism.
2. `xml.etree.ElementTree` remains a safer way to build SVG than f-strings.

**Recommendation:** Use ElementTree to avoid malformed SVG and to support accessibility tags.

---

### TESTER Agent

**Edge cases to prioritize:**
- 0 beams (error with clear message).
- 1 beam (single HTML).
- 79/80 beam threshold boundary.
- Missing utilization (render "N/A" but keep report valid).
- Beam IDs with path separators (sanitize filenames).

---

### DEV Agent

**Implementation notes:**
1. Report input should be the job output (`design_results.json`), not raw design output.
2. Add a thin adapter to accept dict input and validate required fields.
3. Keep report logic in Application layer; file writes in I/O layer.

---

### Review Agent

**Findings to fix before implementation:**
1. Phase 1 scope vs available data mismatch (Input Sanity/Units/Scorecard).
2. Change Ledger listed as Phase 1 in some sections but deferred elsewhere.
3. CLI examples should consistently show `design_results.json`.
4. Target milestone is inconsistent (v0.11 vs v0.9/v0.10).

---

### DOCS Agent

**Docs to update once implementation starts:**
- `docs/API_REFERENCE.md` (report command examples with job output file).
- `docs/GETTING_STARTED_PYTHON.md` (report walkthrough).
- `docs/TROUBLESHOOTING.md` (input format + batch threshold).

---

### ARCHITECT Agent

**Notes:**
- Keep SVG generation pure and testable.
- Avoid embedding business logic in HTML templates.
- Define a small internal schema for report inputs (validated at entry).

---

### DEVOPS Agent

**CI notes:**
- Golden-file tests should run in CI.
- Performance test (500 beams) should be nightly, not on every PR.

---

### UI Agent

**UI guidance:**
- Use color-blind safe colors plus icon markers.
- Keep layout minimal: header -> critical list -> per-beam details.
- Print CSS should remove navigation and force black text.

---

### SUPPORT Agent

**Support risk:**
- Most common error will be using the wrong input file.
- Add a clear error message: "This command expects job output (design_results.json)."

---

### INTEGRATION Agent

**Data contract:**
- Report consumes job output (`design_results.json`) from `job_runner`.
- If CLI design output is used in future, create a converter and document it.

---

### R7 Action Items (doc-only fixes) — ✅ Resolved in R8

1. ✅ Phase 1 scope matches `ComplianceReport` + job spec fields (7 features).
2. ✅ Change Ledger moved to Phase 2 in sections 0.4, 0.5, 11.1.
3. ✅ Report examples use `design_results.json` (job output).
4. ✅ Milestone target: v0.11 (after W08 in v0.10).
5. ✅ Agent count confirmed: 12 agents (CLIENT through Integration).

---

## Conclusion

### What We Learned

1. **Users want answers, not visuals.** The question is "which beams are critical?" not "show me a pretty diagram."

2. **Trust comes before beauty.** A sorted table with utilization bars beats a fancy SVG that can't be verified.

3. **Low-effort features solve real problems.** Critical Beam Map, batch threshold packaging, and `data-source` traces give immediate trust.

4. **Visuals are Phase 1 nice-to-haves, not must-haves.** Cross-section SVG is useful for single-beam reports, but not the priority.

5. **Clause refs unlock deep trust.** Proof Trace with clause refs is the long-term differentiator, but needs W08 first.

### Decision Summary

**Phase 1 ships:** Critical Set Export, Input Sanity Heatmap, Stability Scorecard, Units Sentinel, Cross-section SVG (optional), batch threshold packaging, `data-source` traces.

**Phase 2+ deferred:** Change Ledger, Proof Trace, BBS visuals, Diff mode, DXF-BBS checks.

### Next Steps

1. ✅ Research complete — move to implementation planning
2. Create GitHub issues for 8 implementation tasks (see Stage 5)
3. Target milestone: v0.11 (after W08 ships in v0.10)
4. Phase 2 prerequisites: W08 clause metadata, stable hash rules

---

*Research complete. Status: Decided. Implementation planning begins.*
