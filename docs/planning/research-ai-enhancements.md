# Research Log — AI/High-Value Enhancements

**Research Version:** v0.9.1 baseline (+ CI hardening)
**Last Updated:** 2026-01-12<br>
**Scope:** Identify additions that make the library materially more valuable for professional use (beyond current strength/detailing + serviceability Level A baseline).

This log captures goals/mindset, a lightweight online-scan snapshot, and a prioritized shortlist of high-value additions (serviceability, rebar optimizer, BBS/BOM export, load-combo compliance checking), plus longer-horizon AI/NL helper ideas.

---

## Mindset & Goals
- Deliver **high-leverage, low-friction** features that slot into existing workflows (Excel/Python) without heavy user training.
- Maintain **code compliance** (IS 456/IS 875/IS 1893) as the non-negotiable backbone; AI is an accelerator, not a substitute for code checks.
- Keep **Python/VBA parity** for core calculations; advanced/AI helpers can remain Python-first where needed.
- Prioritize **explainability** (calculations, inputs, assumptions) to make AI features auditable.

---

## Quick Online Scan (Dec 15, 2025)
- **Structural health monitoring + ML**: abundant academic work (e.g., “deep learning for SHM review” queries surface review papers on vibration-based damage detection). Relevance: informs future module for post-construction monitoring, but not immediate for design library.
- **Rebar optimization / layout automation**: industry chatter around automated detailing/rebar schedulers; most proprietary (e.g., CAD plugins) with few open-source options. Opportunity: open, transparent optimizer tied to code rules.
- **Crack/deflection ML prediction**: some papers use ML to predict serviceability (deflection/crack) from geometry/material inputs. Relevance: a data-driven checker could complement code formulas but must remain secondary to codified checks.
- Note: This is a lightweight scan of publicly available material (not a systematic literature review). The takeaways above are synthesized from high-level search results and general domain trends.

---

## Candidate Initiatives

1) **Serviceability Module (Deflection + Crack Width)**
   - Value: Mandatory for professional acceptance; unblocks “production-ready” status.
   - Scope: IS 456 Cl. 23.2 (span/depth + modification factors), Annex C (detailed), Annex F (crack width limits by exposure).
   - Deliverables: `serviceability.py` + `M17_Serviceability.bas`, 20+ tests, docs, API/README updates.

2) **Load Combination & Compliance Checker**
   - Value: One-click “code compliance” verdict for a beam row from ETABS/CSV.
   - Scope: IS 875 load combos, IS 456 limit state checks (strength + serviceability), output structured pass/fail with remarks.
   - Deliverables: Combo generator, wrapper that calls flexure/shear/serviceability; Excel-friendly summary.

3) **Rebar Arrangement Optimizer (Cost/Weight/Constructability)**
   - Value: Converts required Ast into best bar pattern (size/count/layers) respecting spacing, cover, constructability, and stocking rules.
   - Approach: Small search/ILP over standard diameters; optional objective (min steel weight / min bar count / min congestion).
   - Output: Pattern, spacing check, callouts, and “why chosen”.

4) **Bar Bending Schedule (BBS) + BOM Export**
   - Value: Moves detailing into fabrication deliverables; high utility for site teams.
   - Scope: From detailing result → cutting lengths, hooks, bends, quantities; export CSV/PDF; align with IS 2502 conventions.
   - VBA/Python parity: Python-first for generation; VBA formatter for Excel users.

5) **IFC/DXF/BIM Bridge (Lightweight)**
   - Value: Interop with CAD/BIM without locking into proprietary plugins.
   - Scope: Export beam detailing to IFC entities (beam + rebars as proxy geometry), enrich DXF with metadata layers, optional glTF preview.
   - Constraint: Keep dependencies optional (Python-only).

6) **Parametric Batch Runner + Sensitivity/Monte Carlo**
   - Value: Helps engineers test robustness (cover variations, material strengths, bar sizes).
   - Scope: Simple file-in/file-out runner with deterministic JSON/CSV outputs; optional parameter sweeps later.
   - Output: JSON + CSV artifacts with a fixed folder layout.
   - Status: **Baseline implemented** (job schema + batch runner + CLI).

7) **Natural-Language Assistant / Explainer (Python-first)**
   - Value: Converts plain-language prompts (“Design 300x500 beam, M25/Fe500, Mu=150, span 4m”) into structured calls; produces “calculation sheet” style explanations.
   - Guardrails: Always show inputs/outputs and clause references; no hidden calculations.
   - Deployment: Optional CLI flag or notebook helper; no hard dependency on an LLM runtime.

8) **Post-Construction Monitoring Hook (Future)**
   - Value: Long-term roadmap item—ingest SHM data (strain, vibration) and compare against design/serviceability envelopes.
   - Status: Parked until core design/serviceability is complete.

---

## Prioritized Shortlist (High Impact / Moderate Effort)
- **P1 (done):** Serviceability module (Deflection + Crack).
- **P4 (done):** Compliance checker (pass/fail + reasons).
- **P2 (next):** Rebar arrangement optimizer — immediate user value, improves constructability/cost outcomes.
- **P3 (next):** BBS/BOM export — closes loop to fabrication, pairs with optimizer.
- **P5 (next):** ETABS → compliance mapping docs + normalization hardening (CSV-first).

---

## Proposed Next Steps (v0.9-v0.10)
- **v0.9 (done):** Stable IS456 entrypoints + deterministic job runner baseline.
- **v0.9.x (done):** CI hardening (formatting + coverage stability).
- **v0.10 (next):** Add P2 (deterministic rebar layout optimizer) + P3 (BBS/BOM CSV export), and wire outputs into schedules.
- **Research follow-up:** prototype P7 (NL assistant) as opt-in CLI/notebook helper that only emits deterministic calls + an auditable explanation.

---

## Research Update (Pass 6 - Adoption and Positioning Insights, Dec 25, 2025)

This pass extracts the useful ideas from broader ecosystem research and maps
them to repo-aligned actions. It avoids new claims and focuses on adoption
leverage for the current IS456 design/compliance engine.

### Useful ideas to keep (repo-aligned)
- **Excel-first transparency**: keep the Excel/VBA path explicit and auditable.
- **BBS/BOM as an adoption hook**: fabrication-ready outputs create trust and
   immediate user value (TASK-034).
- **ETABS mapping docs**: low-effort documentation with high adoption impact
   (TASK-044).
- **Determinism as brand**: same inputs -> same outputs + clause references.
- **Job schema as platform contract**: stable interface for batch automation.
- **Verification packs**: publish benchmark cases to convert skeptics.
- **Scope guardrail**: do not build a new solver; focus on code compliance and
   detailing outputs where the gap is real.

---

## Research Update (Pass 7 — Rebar Optimizer Spec: Min Steel Weight + Longitudinal Only, Dec 26, 2025)

This pass converts two product decisions into an implementation-ready spec for v0.10:

- **Objective:** minimize steel weight.
- **Scope:** start with **main longitudinal bars only** (no stirrups, no cutting lengths, no BBS yet).

### 1) What “min steel weight” means (deterministic, units-explicit)

For longitudinal bar selection (single beam section, no length modeling yet), “minimum steel weight” reduces to:

- Minimize total steel area provided, $A_{s,prov}$, because weight per unit length is proportional to area.

In code terms, this matches an objective of **minimizing `area_provided`** (mm²) for feasible layouts.

### 2) Ground truth in repo (already present)

The Python implementation exists as a deterministic bounded search:

- `Python/structural_lib/rebar_optimizer.py` — `optimize_bar_arrangement(..., objective="min_area")`

So the immediate “research-to-code” action is **productization** (docs/API/tests/parity), not inventing a new algorithm.

### 3) Constraints (v0.10 “Level A constructability”)

Hard constraints to enforce (must pass):

- Allowed diameters: `STANDARD_BAR_DIAMETERS` (or explicit `allowed_dia_mm`).
- Minimum bars: `min_total_bars` (default 2).
- Maximum layers: `max_layers` (default 2).
- Spacing feasibility: use the existing min-spacing check (same helper used by detailing) with explicit `agg_size_mm`.

Notes:

- Layering model is “split bars equally across layers” (via `ceil(count/layers)`), which is simple and deterministic.
- Feasibility is horizontal spacing only (good for v0.10; vertical clear spacing and layering offsets can be a later refinement).

### 4) Deterministic tie-break rules (no surprises)

For `objective="min_area"`, use a fixed lexicographic score:

1) `area_provided` (ascending)
2) `layers` (ascending)
3) `count` (ascending)
4) `bar_dia_mm` (ascending)

This is already the shape used by the Python optimizer and keeps outputs reproducible.

### 5) Test/benchmark vectors (what to add before extending features)

Add a small benchmark pack (5–10 vectors) that asserts:

- Determinism: same inputs → identical arrangement (count/dia/layers/area_provided).
- Feasible case: arrangement spacing passes `check_min_spacing`.
- Infeasible case: returns a structured failure with `candidates_considered` and inputs echoed.

Suggested vector fields:

- `ast_required_mm2`, `b_mm`, `cover_mm`, `stirrup_dia_mm`, `agg_size_mm`, `max_layers`, `allowed_dia_mm`
- Expected: `count`, `dia_mm`, `layers` OR expected infeasible.

### 6) What is explicitly out of scope in this pass

- Stirrup optimization
- BBS/cutting lengths
- Waste optimization / stock-length cutting plans
- Any ML/AI-based selection

---

## Research Update (Pass 5 — Repo Status + Plan Ahead, Dec 20, 2025)

### What’s Already Implemented (so research should not re-plan it)
- **Serviceability (Level A)** is implemented (deflection + crack width).
- **Compliance checker** is implemented (orchestration + governing-case summary).
- **Deterministic job runner** is implemented (file-in/file-out).
- CI is active with lint/typecheck and a strict coverage gate.

### Planning Notes (pragmatic order)
1) **Rebar layout optimizer (TASK-043)**
   - Start with bounded enumeration (no heavy solver dependency).
   - Make constraints/assumptions explicit: cover, stirrup dia, min clear spacing, max layers.
   - Output should include an explanation payload: chosen layout + why feasible.

2) **BBS/BOM export (TASK-034)**
   - Keep “BBS line items” as the core representation.
   - Export **CSV first** (Excel formatting later).
   - Treat bend/hook conventions as explicit parameters (no hidden defaults).

3) **ETABS → compliance mapping deepening (TASK-044)**
   - Document supported ETABS export tables/columns + normalization rules.
   - Add at least one end-to-end test: sample CSV → compliance run → stable summary.

4) **Parity harness (TASK-039 / TASK-040)**
   - Establish shared vectors and a repeatable VBA test run entrypoint.
   - Start with a small curated set (boundaries + typical cases), then expand.

### “Drop-in References” Workflow
- Put your personal PDFs/spreadsheets under `docs/_references/`.
- Large local-only snapshots should go under `docs/_references/downloads_snapshot/` (ignored by git).
- From there, convert worked examples into small benchmark vectors + tests without copying copyrighted clause text.

---

## Notes
- Keep any AI-driven feature **transparent and overrideable**; always show the deterministic calculation path.
- Prefer **small, deterministic search/optimization** over heavyweight ML to avoid reproducibility issues in regulated contexts.

---

## Research Update (Pass 2 — Repo-Aware Design Notes, Dec 15, 2025)

This pass focuses on *how* the shortlisted initiatives would fit into the current codebase (Python + VBA), and what “done” should mean in terms of APIs, outputs, and tests.

### Repo Scan Takeaways
- The Python package is organized around small, testable modules (e.g., `flexure.py`, `shear.py`) with simple dataclass outputs in `types.py`.
- The current public API surface in `api.py` is intentionally small, suggesting new features should remain **module-first** and only add API wrappers once stable.
- Existing design functions already compute intermediate quantities useful for serviceability/compliance (e.g., `xu`, `pt_provided`, `tv/tc/tc_max`). New features should reuse these outputs rather than re-derive values in multiple places.

### 1) Serviceability Module — Practical Implementation Notes
- **Keep two levels of rigor:**
   - Level A (fast): span/depth checks and modification-factor based deflection verification (good for Excel “quick check”).
   - Level B (detailed): optional calculations where inputs are available (sustained loads, creep/shrinkage assumptions, cracked section behavior).
- **Output structure:** add a `ServiceabilityResult` dataclass in `types.py` with fields like `deflection_ok`, `crack_ok`, `limit_values`, `governing_case`, and `remarks`.
- **Avoid silent assumptions:** make any assumed values explicit (e.g., sustained load fraction, effective span definition, exposure-driven crack limits).
- **Acceptance criteria (tests):**
   - “No crash” tests across typical ranges.
   - Boundary tests around $L/d$ limits and modification factor transitions.
   - Deterministic results for representative benchmark examples (even if the benchmark values are from the standard’s worked examples or internal reference sheets).

### 2) Load Combination + Compliance Checker — Minimal Useful Shape
- Treat this as a **reporting/orchestration** layer: it should not duplicate flexure/shear math.
- **Two outputs:**
   - Machine-friendly: a list of per-combo results (pass/fail + controlling ratio).
   - Excel-friendly: a compact summary row with governing combo + remarks.
- **Design principle:** include “why fail” text (e.g., “Tv > Tc,max”, “Ast > 4% bD”, “serviceability deflection exceeds limit”).
- **Acceptance criteria (tests):**
   - Given known combo inputs, the governing combo is stable.
   - Any failure in a sub-check propagates correctly to overall verdict.

### 3) Rebar Arrangement Optimizer — Constraints to Encode First
Prioritize deterministic, engineer-explainable constraints before any fancy objective function.

- **Hard constraints (must-pass):**
   - Bar diameters from a standard set.
   - Maximum bars per layer (based on beam width, cover, stirrup dia, bar dia, min clear spacing).
   - Min spacing checks and “constructability sanity” (avoid extreme congestion).
   - Limit on layers (e.g., 2–3) unless user opts in.
- **Soft objectives (choose one):** minimize steel weight, minimize bar count, or minimize congestion.
- **Output structure:** a `RebarLayoutResult` that includes chosen diameters/counts/layers plus a list of passed/failed spacing checks.
- **Acceptance criteria (tests):**
   - For fixed Ast demand and geometry, solution is deterministic.
   - If no feasible layout exists, return a structured failure with actionable reason (“insufficient width for min spacing”).

### 4) BBS/BOM Export — Keep It Code-Agnostic
- Start from **detailing outputs** (bar counts/lengths/shapes) rather than trying to infer detailing from strength design.
- Represent BBS as a list of line-items (shape code, dia, cut length, quantity, mark) and export CSV first.
- Add PDF/pretty Excel formatting later; keep core generation logic independent.
- **Acceptance criteria (tests):**
   - Known detailing input produces stable total weight and total length.
   - Hooks/bends and length rounding rules are explicit and tested.

### 5) VBA/Python Parity Guidance
- Keep **core deterministic calculations** parity across Python/VBA (serviceability “Level A”, compliance wrapper, basic spacing checks).
- Keep advanced helpers Python-first if they need non-trivial search/optimization; provide VBA as a consumer (call Python or use simplified VBA variant) only if required.

### AI/NL Helper — Guardrails Clarified
- If an NL assistant is added later, it should only:
   - parse user intent → structured inputs,
   - call the same deterministic functions as everyone else,
   - return a calculation-sheet style explanation with clause references.
- It must not introduce alternative computation paths.

### Open Questions (Needed Before Implementation)
- Beam scope: simply supported vs continuous (effective span rules differ).
- Exposure classes to support first for crack limits.
- Whether “compliance checker” should accept **factored design actions only** (simpler) or generate combos from unfactored loads (more helpful but requires clearer conventions).

---

## Research Update (Pass 3 — Source-Backed Research + Decision Matrix, Dec 15, 2025)

This pass adds *source-backed* notes (public URLs), plus concrete decision/benchmark templates to make P1–P4 implementation-ready.

### Sources Consulted (Public)
- NPTEL (Deflection of Structures) — Moment Area Method (beam deflection fundamentals):
   - https://archive.nptel.ac.in/content/storage2/courses/105101085/Slides/Module-4/Lecture-1/4.1_1.html
- NPTEL (Deflection of Structures) — Bending deflection due to temperature gradient (curvature/strain → deflection):
   - https://archive.nptel.ac.in/content/storage2/courses/105101085/Slides/Module-4/Lecture-5/4.5_2.html
- Google OR-Tools — combinatorial optimization (LP/MIP/CP-SAT), relevant to bar-layout search and cutting-stock/waste minimization:
   - https://developers.google.com/optimization
- BarMate (open-source reference) — rebar cut-length, waste optimization across stock lengths, BBS generation with `pandas`, optional AutoCAD integration:
   - https://github.com/Arishneel-Narayan/BarMate

### Takeaways Mapped to P1–P4

**P1 Serviceability (Deflection + Crack Width)**
- The NPTEL material is not an IS 456 guide, but it is a clean reference for the *mechanics* of deflection computation (curvature, moment-area method, and how temperature gradients induce curvature). This supports a two-level approach:
   - Level A (fast, IS 456-driven): span/depth + mod-factor checks (parameterized by user inputs).
   - Level B (detailed, mechanics-driven): compute deflection via curvature integration for standard cases where sufficient inputs exist.
- Important compliance note: IS 456/IS 2502 clause text and numeric limits are copyrighted; implement them as parameters/config and reference clause IDs in documentation without reproducing the code text.

**P2 Rebar Arrangement Optimizer**
- OR-Tools is a strong fit for deterministic search when constraints get richer than a brute-force enumeration (layering, spacing, max diameters, preferred bar counts, etc.).
- Recommended modeling split:
   - “Layout feasibility” as hard constraints.
   - “Best layout” as an objective (min weight / min bar count / min congestion).

**P3 BBS/BOM Export**
- BarMate demonstrates a minimal-but-realistic baseline feature set for BBS-related automation: cut length calculation with bend deductions, waste optimization over discrete stock lengths, and schedule generation via tabular outputs.
- Key product insight: keep BBS generation *data-first* (line items), then emit CSV/Excel formatting as separate layers.

**P4 Compliance Checker + Load Combos**
- Keep as orchestration/reporting (as stated in Pass 2), but add a strict input convention:
   - Option A (simplest): accept already-factored Mu/Vu and only run checks.
   - Option B: accept characteristic loads and generate combos (needs explicit IS 875/IS 1893 conventions, and is harder to test without a reference set).

### Decision Matrix (P1–P4)

Scores: 1 (low) → 5 (high). “Risk” is *implementation + validation risk* (higher means riskier).

| Item | User Value | Effort | Risk | Depends On | Notes |
| --- | ---: | ---: | ---: | --- | --- |
| P1 Serviceability | 5 | 4 | 4 | none | Core for professional acceptance; needs careful assumptions + test benchmarks. |
| P2 Optimizer | 5 | 3 | 3 | spacing rules + preferred bar sets | High value; can start with brute force, later switch to OR-Tools if needed. |
| P3 BBS/BOM | 4 | 3 | 3 | detailing outputs | Great pairing with optimizer; keep conventions configurable. |
| P4 Compliance wrapper | 4 | 2 | 2 | flexure/shear/serviceability | Mostly plumbing + report shape; keep strict input contract. |

### Benchmark Templates (Add to Tests/Docs)

These are templates intended to be filled with known reference examples (internal spreadsheets, project examples, or user-provided worked examples) without copying copyrighted clause text.

**Template A — Deflection (span/depth + mod factors)**
- Inputs:
   - span definition (clear vs c/c vs effective)
   - support condition (SS/continuous/cantilever)
   - b, D, d, cover, bar dia (if needed)
   - concrete grade, steel grade
   - tension steel ratio and/or provided bars
   - load case tags (short-term / sustained fraction)
- Expected outputs:
   - `deflection_ok` boolean
   - governing check label (e.g., "basic L/d" or "modified L/d")
   - computed L/d, allowable L/d
   - remarks that list which inputs were assumed vs provided

**Template B — Rebar layout feasibility & determinism**
- Given: required Ast, beam width, cover, stirrup dia, allowed bar diameters.
- Assertions:
   - returns same layout each run (deterministic)
   - spacing checks pass for the chosen layout
   - if infeasible, returns a structured failure reason (not just `None`)

**Template C — Cutting-stock / waste optimization**
- Given: a set of cut lengths (mm) for a bar mark and candidate stock lengths (6m/7.5m/9m/12m).
- Assertions:
   - chosen stock length is one of allowed
   - waste % (or total scrap length) matches expected
   - output includes a cutting pattern breakdown (how many stock bars, what cuts per stock)

**Template D — Compliance orchestration**
- Given: a small list of combos and their Mu/Vu.
- Assertions:
   - the governing combo is correctly identified
   - overall pass/fail is consistent with sub-check failures
   - report includes “why fail” text

### How to Incorporate Your Local Saved Research (Downloads)

If you want Pass 3 to explicitly cite and extract notes from your local PDFs/spreadsheets (e.g., `CE371.pdf`), the most reliable workflow is:
- Copy those files into the repo under a references folder (e.g., `docs/_references/`) and then we can summarize them into a Pass 4 section.
- Or paste a small excerpt / the key pages as text here (best if you only need a few formulas/tables).

---

## Research Update (Pass 4 — Extracted Local Notes from Downloads Snapshot, Dec 15, 2025)

This pass incorporates *your locally saved artifacts* by summarizing their structure and what they imply for P1–P4. The raw files were copied into a local-only folder under `docs/_references/` for analysis, but are excluded from git (see `.gitignore`).

### Local Artifacts Reviewed (from `docs/_references/downloads_snapshot/`)
- `CE371.pdf` (single-page course outline/syllabus)
- `BEAM SCHEDULE.xlsx` (beam schedule table)
- `AST cal.xlsx` (Ast and bar-count calculation sheet)
- `CSI API ETABS v1.txt` / `CSI API ETABS v1.pdf` (ETABS API documentation)
- `Etabs G+2.EDB` (ETABS model file)
- `Beam_Detailing.dxf` (beam detailing drawing)

### Key Findings and How They Map to P1–P4

**P1 Serviceability (Deflection + Crack Width)**
- `CE371.pdf` confirms serviceability topics (deflection computation, creep strain) are part of typical RC design curricula. This supports making P1 a first-class module rather than an optional “nice-to-have”.
- Practical implementation note: serviceability will need explicit conventions around sustained-load fraction and creep/shrinkage assumptions (even if the first release is a conservative “Level A” check).

**P2 Rebar Arrangement Optimizer**
- `AST cal.xlsx` suggests an engineer workflow that maps demand (moment ranges / Ast) to bar sizes and bar counts. This is a strong starting point for an optimizer that:
   - accepts required Ast and geometry constraints,
   - enumerates feasible bar diameter/count/layer patterns,
   - picks the best pattern with a deterministic objective.
- Product implication: include an “explain” output that mirrors the spreadsheet logic (Ast → area per bar → required count → rounded count → spacing feasibility).

**P3 BBS/BOM Export**
- `BEAM SCHEDULE.xlsx` shows the kind of deliverable users expect: a compact tabular schedule keyed by beam type/mark, with bottom/top steel and likely stirrup details.
- `Beam_Detailing.dxf` indicates there is real value in exporting *both* a schedule (CSV/Excel) and a drawing artifact (DXF) or at least DXF metadata layers. Even if DXF export remains future scope, the internal data model should retain “bar marks” and groupings needed for schedules.

**P4 Compliance Checker / ETABS Integration**
- `CSI API ETABS v1.*` + `Etabs G+2.EDB` make ETABS interoperability a practical near-term integration target. Two realistic integration shapes:
   1) **Low-friction MVP (file-based):** user exports ETABS tables to CSV/Excel → library ingests → runs compliance checks.
   2) **Automation (API-based, Windows-first):** attach to a running ETABS instance, extract tables via API, run checks, write results back.
- Important platform note: the CSI API documentation is heavily .NET/COM oriented. In practice, the API-based approach is likely Windows-first. The file-based approach stays cross-platform and should be the default path.

### Concrete “Next” Artifacts We Can Derive from These Files
- From `BEAM SCHEDULE.xlsx`: define a minimal schedule schema (beam mark, b, D, bottom bars, top bars, stirrups) to become the baseline CSV export format.
- From `AST cal.xlsx`: create 5–10 deterministic unit tests for optimizer rounding and bar selection logic using representative rows (Ast → bar count).
- From `CSI API ETABS v1.txt`: document an integration plan (no code text copied) covering “attach/connect”, “export tables”, and “map table columns to library inputs”.

---

## Roadmap (Action-Oriented) — v0.10 (Option A)

This is a short, execution-focused plan based on the research passes above.

### v0.10 (Fabrication Deliverables)
- **P2 Rebar arrangement optimizer (deterministic):** bounded enumeration over bar diameters/counts/layers + spacing constraints; deterministic tie-breakers; structured “no feasible layout” reasons.
- **P3 BBS/BOM export (CSV-first):** stable line-item schema + CSV export; explicit rounding rules; tests for totals and schema stability.

### Follow-up (after v0.10)
- **ETABS integration (TASK-044):** deepen CSV mapping docs + normalization and add end-to-end CSV → compliance tests.
- **Parity automation (TASK-039 / TASK-040):** shared vectors + repeatable VBA test entrypoint.

### “Definition of Done” (Applies to Every Feature)
- Deterministic results (same inputs → same outputs)
- Clear assumptions surfaced in output (no hidden defaults)
- Structured failures (actionable reasons when inputs/geometry make a check impossible)
- Tests for at least: nominal case, boundary case, infeasible case
---

## Research Update (Pass 8 — "Wow Factor" Feature Candidates, Dec 26, 2025)

This pass identifies high-visibility features that showcase the library's capabilities and accelerate adoption.

### Candidate Ideas (ranked by impact/effort)

| Idea | Wow Factor | Effort | Notes |
|------|:----------:|:------:|-------|
| **1. One-Line Full Design** | ⭐⭐⭐⭐⭐ | Low | A single `full_beam_design(...)` call that chains flexure → optimizer → detailing → DXF → compliance summary. "Give me moments, get a complete deliverable." |
| **2. Interactive HTML Report** | ⭐⭐⭐⭐ | Medium | Export a self-contained HTML (no server) with collapsible sections: design summary, clause references, bar schedule, embedded SVG of cross-section. |
| **3. 3D Rebar Preview (glTF/Jupyter)** | ⭐⭐⭐⭐ | Medium | Generate a 3D wireframe of the beam + bars as glTF or inline Jupyter `pythreejs` widget. Visual for presentations/reviews. |
| **4. Natural Language Prompt → Design** | ⭐⭐⭐⭐⭐ | Medium | "Design 300×600 M25/Fe500 beam for Mu=250 kNm, span 5m" → structured call → complete output + calc sheet. (No LLM dependency—regex/template parsing.) |
| **5. Instant QR Code to Calc Sheet** | ⭐⭐⭐ | Low | Embed a QR in the DXF/PDF that links to a hosted calc sheet or encodes a verification URL. Site teams scan → see design params. |

### Recommended First: One-Line Full Design (`full_beam_design`)

**Why:** Fastest "wow" with highest leverage—showcases every module in one call:

```python
from structural_lib import full_beam_design

result = full_beam_design(
    b=300, D=600, cover=40, fck=25, fy=500,
    Mu_top=180, Mu_bottom=250, Vu=120,
    span=5000, support="continuous",
    output_dxf="beam1.dxf"
)
print(result.summary)  # pass/fail + bar schedule + file paths
```

**Deliverables in one call:**
- Flexure design (singly or doubly, auto-detected)
- Optimal bar arrangement (via rebar optimizer)
- Shear/stirrup design
- Serviceability checks
- Compliance verdict with clause references
- DXF drawing generated

**Implementation:** orchestration wrapper in `api.py` that calls existing modules; no new math.

---

## Task Audit Summary (Dec 26, 2025)

Quick audit of TASKS.md status vs. actual codebase:

### Most Overdue (high impact)
- **TASK-044** (ETABS mapping docs + normalization + verification pack): code exists in VBA, but mapping docs for compliance/batch use are still missing.
- **TASK-034** (BBS/BOM CSV export): no code found for BBS; still open.
- **TASK-039/040** (Python↔VBA parity harness + VBA automation): no shared vectors or parity harness yet; `RunAllTests` exists but not wired/documented.

### Likely Out of Sync
- **TASK-043** is still open in TASKS.md, but the optimizer exists and is tested in `rebar_optimizer.py` + `test_rebar_optimizer.py`. Looks done or nearly done—update task board.

### Partially Done
- **TASK-038** mentions CLI/integration tests; `test_job_cli.py` and `test_job_runner_is456.py` exist, but no end-to-end CSV → detailing → DXF tests yet.

### Suggested Finish Order (fastest impact)
1. **TASK-044** — ETABS mapping docs + verification pack
2. **TASK-034** — BBS/BOM CSV export
3. **TASK-039** — parity vectors + harness
4. **TASK-040** — VBA test automation docs + output format
5. **TASK-038** — expand integration tests (CSV/JSON → detailing → DXF)
