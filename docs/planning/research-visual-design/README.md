# Research: Visual Layer for Beam Design

Purpose: explore visual/interactive outputs that make design, loading, steel, and BBS
more intuitive without weakening correctness or traceability.

Scope: concept ideas, data needs, and phased experiments. No code yet.

**Last Updated:** 2025-12-29
**Status:** Research in progress — brainstorming and review phase

> **Document Purpose:** This is research guidance, NOT an implementation spec.
> Several decisions remain open (marked in text). Do not treat as ready-to-execute.
>
> **Review Rounds:**
> - R1 (2025-12-29): Schema example corrected, Jinja2 dep clarified, determinism relaxed
> - R2 (2025-12-29): HTML escaping, ordered list guards, BBS input requirement
> - R3 (2025-12-29): Innovation ideas reviewed, roadmap alignment assessed
> - R4 (2025-12-29): Problem-first reframe, user personas, low-effort solutions added

---

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
| 3 | Change Ledger (what changed) | "What changed?" | Low |
| 4 | Stability Scorecard (buildability flags) | "Will it build?" | Low |
| 5 | Units Sentinel (kN vs N warnings) | "Can I trust?" | Low |
| 6 | Cross-section SVG (single beam visual) | Nice-to-have | Low |
| 7 | Utilization bar chart | Nice-to-have | Low |

**Phase 2+ — After trust is established:**

| Rank | Solution | Problem Solved | Blocker |
|------|----------|----------------|--------|
| 8 | Proof Trace with clause refs | "Can I trust?" (deep) | W08 clause metadata |
| 9 | DXF-BBS consistency check | "Does BBS match?" | Bar-mark identity contract |

### 0.5 Low-Effort High-Impact Ideas (From R3/R4 Review)

| Idea | What It Does | Effort | Impact | Phase |
|------|--------------|--------|--------|-------|
| **Change Ledger** | `.ledger.json` with input/output hashes + key deltas | Low | High | 1 |
| **Stability Scorecard** | 5 boolean flags: over-reinforced, brittle shear, min ductility, spacing, layers | Low | Medium | 1 |
| **Input Sanity Heatmap** | Table highlighting suspicious inputs (low cover, b/D outliers) | Low | High | 1 |
| **Units Sentinel** | Auto-detect kN vs N by magnitude; warn without blocking | Low | High | 1 |
| **Critical Set Export** | Top N beams by utilization as separate JSON/CSV | Low | High | 1 |
| **Tolerance Overlay** | Show provided vs required as a band, not single number | Low | Medium | 1 |
| **Spec-to-Output Manifest** | `public-api.json` for LLM/tool integration | Low | Medium | 1 |
| **DXF Checksum Stamp** | Metadata in DXF/BBS for mismatch detection | Low | Medium | 1 |
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

### Phase 1: Static HTML Report

> **Decision Required:** Confirm Phase 1 scope before implementation.
> This section documents the *proposed* approach, not final spec.

**Scope:**
- New command: `python -m structural_lib report results.json -o report.html`
- **Single HTML file** with inline CSS/SVG (no external deps)
- Contents: geometry, bars, stirrups, utilization, compliance summary
- Template: `string.Template` (stdlib) with `html.escape()` for all user-supplied values
- **For batch (500 beams):** One HTML with all beams in sections, not 500 files

**Explicit non-goals for Phase 1:**
- No per-beam separate files (that's Phase 2)
- No index page (that's Phase 2)
- No BBS linking (that's Phase 3+)

**Trade-off: Single file vs folder output (Decision Required)**
- *Single file:* Easier to share, no broken links, but large for 500+ beams
- *Folder output:* Scalable, but adds complexity (index page, relative links)
- *Current recommendation:* Single file for Phase 1, revisit if performance issues

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
- <50 beams: single HTML with collapsible sections
- ≥50 beams: index.html + per-beam HTML files in folder

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
| How to handle 500 beams? | **Phase 1:** Single HTML with all beams. **Phase 2:** Index + per-beam pages |

### 9.1 Additional Questions from Review (2025-12-29)

| Question | Resolution |
|----------|------------|
| Which output to consume: CLI design, job output, or both? | **Job output (`ComplianceReport`)** — it has all cases in one structure |
| Phase 1 single HTML or folder with index? | **Single self-contained HTML** (folder is Phase 2) |
| Clause refs now or Phase 2? | **Phase 2** — current schema has clause in `DesignError` only, not in results |
| Tie phase targets to versions or milestones? | **Milestones** — version numbers are indicative, actual scheduling per production roadmap |
| Will this doc be published in-repo or internal? | **In-repo** — serves as research record and implementation guide |
| Should report accept CLI or job output? | **Job output** — unified structure; CLI users run job first |

---

## Part 10: Recommended Next Steps

### Before Implementation (Decision Gate)

1. **Confirm schema source** — CLI design output, job output, or unified schema?
2. **Confirm output packaging** — Single HTML (recommended) or folder structure?
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
| **Units Sentinel** | Warn on likely unit mistakes | Phase 2 | Needs access to input ranges |
| **Input Sanity Heatmap** | Surface outlier inputs in batches | Phase 2 | Needs input geometry/materials |
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

## Conclusion

### What We Learned

1. **Users want answers, not visuals.** The question is "which beams are critical?" not "show me a pretty diagram."

2. **Trust comes before beauty.** A sorted table with utilization bars beats a fancy SVG that can't be verified.

3. **Low-effort features solve real problems.** Critical Beam Map, batch threshold packaging, and `data-source` traces give immediate trust.

4. **Visuals are Phase 1 nice-to-haves, not must-haves.** Cross-section SVG is useful for single-beam reports, but not the priority.

5. **Clause refs unlock deep trust.** Proof Trace with clause refs is the long-term differentiator, but needs W08 first.

### Next Steps

1. Finalize Phase 1 scope: Critical Beam Map + batch threshold rule + `data-source` traces + optional SVG
2. Prototype Critical Beam Map + batch packaging
3. Define `.ledger.json` schema (Phase 2) with stable hash rules
4. Define Units Sentinel + Input Sanity thresholds (Phase 2)

---

*End of research document. Brainstorming continues.*
