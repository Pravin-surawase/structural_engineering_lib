**Type:** Plan
**Audience:** All Agents, Pravin
**Status:** Draft — Awaiting Review
**Importance:** High
**Created:** 2026-03-25
**Last Updated:** 2026-03-25

---

# Next Phase: What to Build and Why

> This document is a result of a full audit of the beam library, FastAPI layer, and React app.
> Nothing here assumes — it traces every suggestion back to what already exists and what is missing.
> **No code changes. Review first.**

---

## What We Are

We are a complete **IS 456 RC beam design pipeline**:

```
Loads → Design → Detailing → BBS → DXF → Report
```

The library is deep, tested, and published on PyPI. The React app covers single beam + batch import + 3D view + dashboard. The VBA/Excel parity is real.

**The honest position:** We are the best open-source IS 456 beam design tool that exists. The question is how to go from "best" to "actually used daily by engineers."

---

## The Workflow Gap

Our tool sits in the middle of the engineering workflow:

```
[Analysis software: ETABS/SAP]  →  [OUR APP]  →  [Submission: PDF, AutoCAD, Excel BOQ]
```

Engineers must use ETABS before they can use us. And after we give them BBS + DXF + HTML report, they still have manual steps (PDF conversion, quantity aggregation).

**The two ends of that chain are where friction lives.**

---

## The 5 Improvements — Ordered by Value

---

### 1. Quick Load Calculator

**What it is:**
A simple form: span + support condition + load type → auto-computes Mu and Vu → feeds directly into the design flow.

**What already exists (important — don't rebuild):**
- `Python/structural_lib/codes/is456/load_analysis.py` — fully implemented
  - `compute_udl_bmd_sfd(span_mm, w_kn_per_m)` → BMD + SFD arrays
  - `compute_point_load_bmd_sfd()` → Point load case
  - `compute_cantilever_udl_bmd_sfd()` → Cantilever UDL
  - `compute_bmd_sfd()` → Superimposed/combined loads
- IS 456 sign conventions and formulas are correct (sagging positive)
- Tested in `Python/tests/unit/test_load_analysis.py`

**What is missing:**
- No FastAPI endpoint for load_analysis (confirmed: grep of routers/ shows nothing)
- No React component
- No connection from load calculator output → DesignView inputs

**Why this matters:**
Right now, every user needs ETABS or SAP to get Mu and Vu before using our app.
That's a barrier for:
- Small firms (1–3 engineers, no analysis software license)
- Students learning IS 456
- Engineers doing quick preliminary checks
- Solo practitioners

Adding this doubles the audience without adding any new engineering capability — the math is already written.

**What to build:**
```
React: LoadCalculatorPanel.tsx
  - Inputs: span (mm), support (simply supported / cantilever), load type (UDL / point)
  - Load intensity fields (w kN/m or P kN, position for point load)
  - "Compute" → calls /api/v1/analysis/loads/simple
  - Output: shows Mu_max (kN·m), Vu_max (kN), BMD diagram (simple SVG line chart)
  - "Use These Values" button → populates DesignView inputs directly

FastAPI: Add to analysis router
  POST /api/v1/analysis/loads/simple
  - Input: span_mm, support_condition, loads[]
  - Output: mu_max_knm, vu_max_kn, bmd[], sfd[], critical_positions

Python: Zero new code needed — call compute_bmd_sfd() directly
```

**Effort:** Small (2–3 days). Python: zero. FastAPI: 1 endpoint. React: 1 panel.
**Risk:** Very low. The math is tested. This is pure plumbing.

---

### 2. Project Bill of Quantities (BOQ)

**What it is:**
After batch designing a floor or a building, show total material quantities:
- Steel by grade (Fe415, Fe500) in kg, per floor and total
- Concrete by grade (M20, M25, M30) in m³, per floor and total
- Estimated cost using the cost rates we already have

**What already exists:**
- `BBSSummary` in `services/bbs.py` has `weight_by_diameter`, `length_by_diameter`, `count_by_diameter` per beam
- Cost rates are already in `GET /api/v1/optimization/cost-rates` (Fe500: ₹60/kg, M25: ₹6000/m³)
- `DashboardData` from `/api/v1/insights/dashboard` already has `by_story` breakdown
- Batch design results include per-beam steel areas (ast_required, asc_required)
- Concrete volume = b × D × span (geometry data is available)

**What is missing:**
- No aggregation function that sums BBS weights across multiple beams
- No FastAPI endpoint for project-level quantities
- No React component (DashboardPage has per-beam data but no project totals)

**Why this matters:**
At tender stage, a firm submits a BOQ: "400 MT of Fe500 steel, 180 m³ of M25 concrete."
This is a contractual document. Right now, engineers take our BBS CSVs and manually sum them in Excel.
If we produce this automatically, we become part of the procurement workflow, not just the design workflow.

**What to build:**
```
Python: services/boq.py (new, small)
  - aggregate_bbs(bbs_documents: list[BBSDocument]) → ProjectBOQ
  - ProjectBOQ: steel_by_grade {Fe415, Fe500}: {kg, cost_inr}
                concrete_by_grade {M25, M30}: {m3, cost_inr}
                by_story: {GF: {...}, FF: {...}}
                grand_total_cost_inr

FastAPI: Add to insights router
  POST /api/v1/insights/project-boq
  - Input: list of beam results with geometry + materials
  - Output: ProjectBOQ

React: ProjectBOQPanel.tsx — add to DashboardPage
  - Total steel card (kg + cost)
  - Total concrete card (m³ + cost)
  - Per-story table
  - "Export BOQ as CSV" button
```

**Effort:** Small–Medium (3–4 days). Python: ~100 lines. FastAPI: 1 endpoint. React: 1 panel added to Dashboard.
**Risk:** Low. Pure aggregation math.

**One flag to review:**
The concrete volume needs span data. In the current batch design, span_mm is available per beam in the import schema. Confirm this is being passed through before implementing.

---

### 3. PDF Export

**What it is:**
Convert the existing HTML calculation report to a downloadable PDF.

**What already exists:**
- `services/report.py` — generates a complete HTML report with: design inputs, flexure/shear results, sanity checks, stability scorecard, units sentinel, IS 456 references
- `POST /api/v1/export/report` — already serves HTML file download
- `useExportReport()` hook in React — already connected to UI
- The HTML is well-structured (tables, sections, styled)

**What is missing:**
- PDF conversion step in the export router
- A dependency choice: WeasyPrint vs Playwright vs wkhtmltopdf

**Dependency recommendation: WeasyPrint**
- Pure Python, no browser binary needed
- Good CSS support, handles tables well
- ~25 MB install (vs 150 MB for Playwright Chromium)
- Already used in similar open-source structural tools
- Add to `requirements.txt` as optional: `weasyprint>=60.0`

**Why this matters:**
This is the most-asked feature in any engineering tool.
- Firms submit design calculations to clients, consultants, and authorities as PDFs
- HTML files are not accepted in most formal submission workflows
- We are 80% there — the HTML report is good quality

**What to build:**
```
Python: Add to services/report.py
  def export_pdf(data: ReportData) -> bytes:
      html_content = export_html(data)
      from weasyprint import HTML
      return HTML(string=html_content).write_pdf()

FastAPI: Extend export router
  Add format="pdf" to existing /api/v1/export/report endpoint
  (The request model already has format: str field — extend pattern to include "pdf")
  Return: StreamingResponse(pdf_bytes, media_type="application/pdf")

React: Update useExportReport() hook
  Add exportFormat param: 'html' | 'pdf'
  Update ExportPanel to show two buttons: "HTML Report" | "PDF Report"
```

**Effort:** Small (1–2 days). Python: ~15 lines. FastAPI: minimal change. React: minor.
**Risk:** Medium. WeasyPrint rendering of complex HTML can have edge cases (page breaks, wide tables). Needs testing with real report output before shipping.

**Note for review:** Test the PDF output with an actual report before committing. WeasyPrint handles most cases well but tables with many columns can overflow. May need a `@media print` CSS tweak in the report template.

---

### 4. Design Alternatives Panel (Pareto Front)

**What it is:**
A panel in the DesignView that shows 3–5 alternative beam designs side by side, ranked by cost vs safety margin tradeoff. Engineer picks the one that fits their constraints.

**What already exists:**
- `services/multi_objective_optimizer.py` — full NSGA-II Pareto implementation (637 lines)
  - `optimize_pareto_front(span_mm, mu_knm, vu_kn, objectives)` — returns ranked candidates
  - `ParetoCandidate` — contains b_mm, D_mm, ast_required, bar_config, cost, utilization, rank
  - `get_design_explanation(candidate)` — returns human-readable explanation
- `POST /api/v1/optimization/beam/cost` — cost optimizer is in FastAPI
- BUT: `optimize_pareto_front` is NOT exposed in FastAPI (confirmed: no endpoint exists)
- AND: Nothing in React uses multi-objective optimization

**What is missing:**
- 1 FastAPI endpoint for Pareto optimization
- 1 React panel (AlternativesPanel) in DesignView

**Why this matters:**
Engineers don't design beams — they **choose** beams. Given a moment + shear, there are 10+ valid section sizes. The right one depends on:
- Architectural constraints (ceiling height → limits D_mm)
- Site: rebar congestion tolerance
- Budget: minimize steel cost vs minimize concrete volume

The Pareto front is the correct engineering tool for this. It already exists in Python. We just need to surface it.

**What to build:**
```
FastAPI: Add to optimization router
  POST /api/v1/optimization/beam/pareto
  Request: { span_mm, mu_knm, vu_kn, b_mm_range, D_mm_range, fck, fy }
  Response: { candidates: ParetoCandidate[], pareto_front_count, total_evaluated }

React: AlternativesPanel.tsx
  - Triggered by "See Alternatives" button in DesignView
  - Table: Section | Steel (mm²) | Bar config | Utilization | Cost/m | Explanation
  - Highlight current design
  - "Apply" button on any row → updates DesignView inputs
  - Sort by: Cost | Utilization | Steel weight
```

**Effort:** Medium (3–4 days). Python: zero (done). FastAPI: 1 new endpoint + response model. React: 1 new panel.
**Risk:** Low. The Python is tested. The main effort is the React table and connecting "Apply" to the store.

---

### 5. Beam Rationalization (Building-Level)

**What it is:**
After batch-designing a floor or building, suggest reducing the number of unique beam sections.
Example: "You have 23 different beam sizes in this building. Here are 4 standard sections that cover all 23 beams safely. Max utilization increases from 71% to 87% — still safe."

**What already exists:**
- Batch design results (all beams with b_mm, D_mm, utilization)
- `check_beam_is456()` can verify if an alternative section passes for a given load
- No rationalization logic anywhere in the codebase

**Why this matters:**
In practice, every structural engineering firm "rationalizes" sections before issuing drawings:
- Fewer unique formwork types → lower construction cost (formwork is 30–40% of RC cost)
- Fewer bar types on site → less error, easier supervision
- This is a decision engineers currently make manually in Excel

**What to build (conceptual — this needs more design thought):**
```
Python: services/rationalization.py (new)
  - group_by_section(beams) → clusters by b_mm × D_mm
  - propose_standard_sections(beams, max_sections=4) → finds minimum set of sections
    such that all beams pass when assigned to their nearest standard section
  - verify_rationalized_design(beams, standard_sections) → re-checks all pass/fail

FastAPI: POST /api/v1/insights/rationalize
  Input: list of designed beams (with loads + results)
  Output: { proposed_sections: [], assignments: {beam_id: section}, max_utilization }

React: RationalizationPanel in BuildingEditorPage
  - "Rationalize Sections" button
  - Shows: before (23 sizes) / after (4 sizes) comparison
  - Max utilization delta
  - Accept → updates all beam sections in AG Grid
```

**Effort:** Large (1–2 weeks including testing). This is the most complex feature here.
**Risk:** Medium-High. The clustering logic must be conservative (always safe side). Needs careful validation against manual checks.

**Recommendation:** Do not start this until features 1–4 are shipped and used. Wait for engineer feedback on what "rationalization" means to them in practice — it varies by firm.

---

## Summary Table

| # | Feature | Python | FastAPI | React | Effort | Risk | Value |
|---|---------|--------|---------|-------|--------|------|-------|
| 1 | Load Calculator | ✅ Done | ❌ Missing 1 endpoint | ❌ 1 panel | Small | Low | High |
| 2 | Project BOQ | ~100 lines | ❌ 1 endpoint | ❌ 1 panel | Small | Low | High |
| 3 | PDF Export | ~15 lines | ❌ extend existing | ❌ 2 buttons | Small | Medium | High |
| 4 | Alternatives Panel | ✅ Done | ❌ 1 endpoint | ❌ 1 panel | Medium | Low | Medium |
| 5 | Rationalization | ❌ New service | ❌ 1 endpoint | ❌ 1 panel | Large | Medium | High (long term) |

**Recommended order:** 3 → 1 → 2 → 4 → 5

Start with PDF export (smallest code change, highest demand), then load calculator (unlocks new users), then BOQ (completes the workflow), then alternatives panel (exposes existing Python), then rationalization last.

---

## What We Are NOT Building (and Why)

| Not building | Reason |
|-------------|--------|
| Column design | Correct to wait — validate beam library adoption first |
| Slab design | Same reason — breadth before depth is wrong for solo dev |
| ACI 318 / EC2 | Only matters when Indian market is saturated |
| Continuous beam (multi-span) | `load_analysis.py` is simply supported + cantilever only. Multi-span needs moment distribution. Significant effort, unclear demand. |
| AI assistant port to React | TASK-513 is in backlog. Needs LLM API design decision first. |

---

## Engineering Accuracy Notes

These are things to double-check before or during implementation — not blockers, but worth knowing:

1. **Load calculator scope:** `load_analysis.py` covers UDL + point load on simply supported and cantilever. For preliminary design this is sufficient. Do NOT imply it handles continuous beams — that would be misleading to engineers.

2. **BOQ concrete volume:** Volume = b × D × span. This is gross volume (no deductions for voids). Real concrete quantity includes 5–10% waste. Add a note in the UI: "Gross volume, add 5–10% for waste."

3. **PDF report for multi-case designs:** The current HTML report is for single-beam design. When batch design produces multiple beams, the PDF endpoint will need to handle either per-beam PDFs or a combined multi-beam report. Decide this at design time, not mid-implementation.

4. **Pareto front assumptions:** The current `optimize_pareto_front()` explores b_mm and D_mm variations but uses a fixed cover (40mm) and fixed fck/fy. The FastAPI endpoint should expose these as optional parameters so engineers can constrain the search space.

---

## Open Questions for Review

1. **PDF: per-beam or multi-beam?** Should the PDF export produce one PDF per beam or one combined report for all designed beams? Multi-beam is more useful but harder to implement cleanly.

2. **Load calculator placement:** Should it be a panel inside DesignView (alongside the form), or a separate `/loads` route? A panel is simpler. A separate route is cleaner for future expansion.

3. **BOQ cost rates:** The cost rates endpoint returns ₹/kg and ₹/m³ values. Should the BOQ use these as defaults with user-editable override, or always prompt the user to enter rates? User-editable defaults are more practical for a firm.

4. **Rationalization trigger:** Should rationalization be automatic (runs after every batch design) or manual (button)? Manual is safer for v1 — engineers don't want automated changes to their designs.

---
---

# PART 2: Detailed Implementation Plan

> **Audit correction:** Torsion was initially flagged as stubbed. Upon code review, `torsion.py` is **fully implemented** (540 lines, all 6 functions complete, `design_torsion()` returns `TorsionResult`). Imported in `services/api.py` already. What's actually missing is the **FastAPI endpoint** and **React integration** for torsion — not the Python math.

## Execution Order & Task IDs

| # | Task ID | Feature | Layers | Effort | Depends On |
|---|---------|---------|--------|--------|------------|
| 1 | TASK-514 | PDF Export | Python (15 lines) + FastAPI (extend) + React (minor) | 1–2 days | — |
| 2 | TASK-515 | Load Calculator | FastAPI (1 endpoint) + React (1 panel + route) | 2–3 days | — |
| 3 | TASK-516 | Load Analysis: triangular + moment | Python (codes/is456) | 1 day | TASK-515 |
| 4 | TASK-517 | Project BOQ | Python (1 module) + FastAPI (1 endpoint) + React (1 panel) | 3–4 days | — |
| 5 | TASK-518 | Torsion API + React | FastAPI (1 endpoint) + React (panel in DesignView) | 2–3 days | — |
| 6 | TASK-519 | Alternatives Panel (Pareto) | FastAPI (1 endpoint) + React (1 panel in DesignView) | 3–4 days | — |
| 7 | TASK-520 | Report/3D Test Coverage | Python tests | 2–3 days | TASK-514 |
| 8 | TASK-521 | Beam Rationalization | Python (new service) + FastAPI + React | 1–2 weeks | TASK-517 |

**Total: ~16–22 days of work across 8 tasks.**

---

## TASK-514: PDF Export

### Audit

| Item | Status | Location |
|------|--------|----------|
| HTML report generation | ✅ Done | `services/report.py` → `export_html(data: ReportData) -> str` (line 1240) |
| Export endpoint | ✅ Done | `POST /api/v1/export/report` in `fastapi_app/routers/export.py` |
| Format parameter | ✅ Done | `ExportReportRequest.format: str = Field(default="html", pattern="^(html\|json)$")` |
| React hook | ✅ Done | `useExportReport()` in `hooks/useExport.ts` with `ExportReportParams.format` |
| PDF conversion | ❌ Missing | No WeasyPrint dependency, no `export_pdf()` function |

### Python: `services/report.py`

Add one function after `export_html()` (line ~1247):

```python
def export_pdf(data: ReportData) -> bytes:
    """Export report data as PDF bytes via WeasyPrint.

    Args:
        data: ReportData with all design results.

    Returns:
        PDF file content as bytes.

    Raises:
        ImportError: If weasyprint is not installed.
    """
    html_content = export_html(data)
    try:
        from weasyprint import HTML
    except ImportError:
        raise ImportError(
            "weasyprint is required for PDF export. "
            "Install with: pip install weasyprint>=60.0"
        )
    return HTML(string=html_content).write_pdf()
```

**No other Python changes.** The existing `ReportData` model, `_wrap_html()`, and all section renderers remain untouched.

### Python: `requirements.txt`

Add as optional:
```
weasyprint>=60.0  # Optional: PDF export
```

### FastAPI: `routers/export.py`

**Change 1:** Extend `ExportReportRequest.format` regex:
```python
format: str = Field(default="html", pattern="^(html|json|pdf)$")
```

**Change 2:** In the `export_report()` endpoint function, add the PDF branch after the existing HTML/JSON logic:

```python
elif request.format == "pdf":
    from structural_lib.services.report import export_pdf
    pdf_bytes = export_pdf(report_data)
    buffer = io.BytesIO(pdf_bytes)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={request.beam_id}_report.pdf"
        },
    )
```

### React: `hooks/useExport.ts`

**Change:** Extend `ExportReportParams.format` type:
```typescript
format?: "html" | "json" | "pdf";
```

That's it — the hook's `fetchExport()` already sends `format` in the request body, and `downloadBlob()` already handles arbitrary content types.

### React: `ExportPanel.tsx`

Add one more button next to the existing "HTML Report" button:

```tsx
<button onClick={() => exportReport({ ...params, format: "pdf" })}>
  PDF Report
</button>
```

### Tests

| Test | File | Description |
|------|------|-------------|
| Unit: `export_pdf()` returns bytes | `Python/tests/unit/test_report.py` | Mock WeasyPrint, verify bytes output |
| Unit: `export_pdf()` raises ImportError | Same | Verify clear error when weasyprint missing |
| FastAPI: `POST /export/report` with `format=pdf` | `fastapi_app/tests/test_export.py` | Test 200 + content-type `application/pdf` |
| React: Vitest mock for PDF button | `react_app/src/hooks/__tests__/useExport.test.ts` | Verify fetch called with `format: "pdf"` |

---

## TASK-515: Load Calculator

### Audit

| Item | Status | Location |
|------|--------|----------|
| `compute_bmd_sfd()` | ✅ Done | `codes/is456/load_analysis.py` — handles UDL, point, cantilever |
| `compute_udl_bmd_sfd()` | ✅ Done | Same file — simply supported UDL |
| `compute_point_load_bmd_sfd()` | ✅ Done | Same file — simply supported point load |
| `compute_cantilever_udl_bmd_sfd()` | ✅ Done | Same file — cantilever UDL |
| `compute_cantilever_point_load_bmd_sfd()` | ✅ Done | Same file — cantilever point load |
| LoadType enum | ✅ Done | `core/data_types.py` — `UDL`, `POINT`, `TRIANGULAR`, `MOMENT` |
| LoadDefinition dataclass | ✅ Done | `core/data_types.py` — `load_type`, `magnitude`, `position_mm` |
| LoadDiagramResult dataclass | ✅ Done | `core/data_types.py` — `bmd`, `sfd`, `critical_points` |
| Tests | ✅ Done | `tests/unit/test_load_analysis.py` — 25 tests, 6 classes |
| FastAPI endpoint | ❌ Missing | No load analysis endpoint in any router |
| React UI | ❌ Missing | No load calculator component |

### FastAPI: `models/loads.py` (new file)

```python
"""Pydantic models for load analysis endpoints."""
from pydantic import BaseModel, Field

class LoadItem(BaseModel):
    """A single load applied to the beam."""
    load_type: str = Field(
        ..., pattern="^(udl|point)$",
        description="Load type: 'udl' (kN/m) or 'point' (kN)"
    )
    magnitude: float = Field(..., gt=0, description="Load magnitude (kN/m for UDL, kN for point)")
    position_mm: float | None = Field(
        default=None, ge=0,
        description="Position from left support (mm). Required for point loads."
    )

class LoadAnalysisRequest(BaseModel):
    """Request for load analysis (BMD + SFD computation)."""
    span_mm: float = Field(..., gt=0, le=30000, description="Beam span (mm)")
    support_condition: str = Field(
        default="simply_supported",
        pattern="^(simply_supported|cantilever)$",
        description="Support condition"
    )
    loads: list[LoadItem] = Field(..., min_length=1, description="Applied loads")
    num_points: int = Field(default=50, ge=10, le=500, description="Diagram resolution")

class CriticalPointResponse(BaseModel):
    """A critical point on the beam (max moment, max shear, etc.)."""
    position_mm: float
    moment_knm: float
    shear_kn: float
    description: str

class LoadAnalysisResponse(BaseModel):
    """Response with BMD, SFD, and critical values for use in design."""
    success: bool = True
    mu_max_knm: float = Field(description="Maximum bending moment (kN·m)")
    vu_max_kn: float = Field(description="Maximum shear force (kN)")
    bmd: list[float] = Field(description="Bending moment values along span")
    sfd: list[float] = Field(description="Shear force values along span")
    positions_mm: list[float] = Field(description="Position values along span")
    critical_points: list[CriticalPointResponse] = Field(default_factory=list)
    support_condition: str
    span_mm: float
```

> **Key naming:** `mu_max_knm` / `vu_max_kn` — matches the library's `mu_knm` / `vu_kn` convention. These values feed directly into `design_beam_is456(mu_knm=..., vu_kn=...)`.

### FastAPI: `routers/analysis.py`

Add one endpoint to the existing analysis router:

```python
@router.post(
    "/loads/simple",
    response_model=LoadAnalysisResponse,
    summary="Simple Load Analysis",
    description="Compute BMD + SFD for simply supported or cantilever beam.",
)
async def analyze_loads(request: LoadAnalysisRequest) -> LoadAnalysisResponse:
    """
    Compute bending moment diagram (BMD) and shear force diagram (SFD).

    Outputs mu_max_knm and vu_max_kn that can feed directly into
    the /api/v1/design/beam endpoint.

    Supports:
    - UDL (kN/m) on simply supported or cantilever
    - Point load (kN) at any position
    - Multiple superimposed loads

    Per IS 456:2000, coefficients for simply supported beams.
    """
    from structural_lib.codes.is456.load_analysis import compute_bmd_sfd
    from structural_lib.core.data_types import LoadDefinition, LoadType

    # Map request loads to LoadDefinition objects
    load_defs = []
    for load in request.loads:
        lt = LoadType.UDL if load.load_type == "udl" else LoadType.POINT
        load_defs.append(LoadDefinition(
            load_type=lt,
            magnitude=load.magnitude,
            position_mm=load.position_mm or 0,
        ))

    result = compute_bmd_sfd(
        span_mm=request.span_mm,
        loads=load_defs,
        support_condition=request.support_condition,
        num_points=request.num_points,
    )

    return LoadAnalysisResponse(
        mu_max_knm=round(max(abs(v) for v in result.bmd), 3),
        vu_max_kn=round(max(abs(v) for v in result.sfd), 3),
        bmd=result.bmd,
        sfd=result.sfd,
        positions_mm=result.positions,
        critical_points=[
            CriticalPointResponse(
                position_mm=cp.position_mm,
                moment_knm=cp.moment_knm,
                shear_kn=cp.shear_kn,
                description=cp.description,
            ) for cp in result.critical_points
        ],
        support_condition=request.support_condition,
        span_mm=request.span_mm,
    )
```

### React: `hooks/useLoadAnalysis.ts` (new)

```typescript
/**
 * useLoadAnalysis Hook
 *
 * BMD/SFD computation via /api/v1/analysis/loads/simple.
 * Returns mu_max_knm + vu_max_kn ready to feed into DesignView.
 */
import { useMutation } from "@tanstack/react-query";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface LoadItem {
  load_type: "udl" | "point";
  magnitude: number;
  position_mm?: number;
}

export interface LoadAnalysisRequest {
  span_mm: number;
  support_condition: "simply_supported" | "cantilever";
  loads: LoadItem[];
}

export interface LoadAnalysisResult {
  success: boolean;
  mu_max_knm: number;
  vu_max_kn: number;
  bmd: number[];
  sfd: number[];
  positions_mm: number[];
  critical_points: { position_mm: number; moment_knm: number; shear_kn: number; description: string }[];
  support_condition: string;
  span_mm: number;
}

async function fetchLoadAnalysis(req: LoadAnalysisRequest): Promise<LoadAnalysisResult> {
  const res = await fetch(`${API}/api/v1/analysis/loads/simple`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Load analysis failed");
  }
  return res.json();
}

export function useLoadAnalysis() {
  return useMutation({
    mutationFn: fetchLoadAnalysis,
    mutationKey: ["load-analysis"],
  });
}
```

### React: `components/design/LoadCalculatorPanel.tsx` (new)

Panel placed **inside DesignView** (not a separate route). Layout:

```
┌──── Load Calculator ────────────────────────────┐
│ Span:  [5000] mm   Support: [Simply Supported ▼]│
│                                                  │
│ Loads:                                           │
│  [1] UDL   [15] kN/m                    [× Del] │
│  [2] Point [30] kN  at [2500] mm        [× Del] │
│  [+ Add Load]                                    │
│                                                  │
│ [Compute]                                        │
│                                                  │
│ Results:                                         │
│  Mu_max = 46.875 kN·m   Vu_max = 37.500 kN     │
│  ┌─── BMD ─────────────────────────────────┐    │
│  │    /\           (simple line chart)      │    │
│  │   /  \                                   │    │
│  │  /    \                                  │    │
│  └──────────────────────────────────────────┘    │
│                                                  │
│ [Use These Values →]  ← populates Mu_d + Vu_d   │
└──────────────────────────────────────────────────┘
```

**"Use These Values"** button calls `useDesignStore.getState().setInputs({ moment: mu_max_knm, shear: vu_max_kn })` — directly feeding into the design form.

BMD/SFD chart: simple SVG `<polyline>` — no chart library needed. Data from `positions_mm` / `bmd` / `sfd` arrays.

### Tests

| Test | File |
|------|------|
| FastAPI: `POST /analysis/loads/simple` UDL simply supported | `fastapi_app/tests/test_analysis.py` |
| FastAPI: Point load with position | Same |
| FastAPI: Multiple superimposed loads | Same |
| FastAPI: Cantilever UDL | Same |
| FastAPI: Validation (span<=0, empty loads) | Same |
| React: `useLoadAnalysis` hook mock | `react_app/src/hooks/__tests__/useLoadAnalysis.test.ts` |
| React: Vitest fixture for load response | `react_app/src/test/api-fixtures.ts` (extend) |

---

## TASK-516: Load Analysis — Triangular Load + Applied Moment

### Audit

Two `NotImplementedError` stubs in `codes/is456/load_analysis.py`:
- Line 417: `LoadType.TRIANGULAR` → `"Triangular load not yet implemented"`
- Line 421: `LoadType.MOMENT` → `"Applied moment not yet implemented"`

### Python: `codes/is456/load_analysis.py`

**Add function `compute_triangular_load_bmd_sfd()`:**

Triangular load on simply supported beam (zero at left, w_max at right):
- R_A = w × L / 6, R_B = w × L / 3
- Vx = R_A − w × x² / (2L)
- Mx = R_A × x − w × x³ / (6L)
- Max moment at x = L/√3

Follow exact pattern of `compute_udl_bmd_sfd()`:
```python
def compute_triangular_load_bmd_sfd(
    span_mm: float,
    w_max_kn_per_m: float,
    num_points: int = 50,
) -> tuple[list[float], list[float], list[float]]:
    """Simply supported beam with triangular load (zero at left, w_max at right).

    Args:
        span_mm: Beam span (mm).
        w_max_kn_per_m: Maximum load intensity at right end (kN/m).
        num_points: Number of output points.

    Returns:
        Tuple of (positions_mm, bmd_knm, sfd_kn).

    Units:
        span_mm: mm
        w_max_kn_per_m: kN/m
        Result: positions in mm, BMD in kN·m, SFD in kN
    """
```

**Add function `compute_applied_moment_bmd_sfd()`:**

Applied moment M at position a on simply supported beam:
- R_A = −M/L (upward if M positive), R_B = M/L
- BMD: linear, changes slope at applied moment point
- SFD: constant R_A to left, constant R_B to right

```python
def compute_applied_moment_bmd_sfd(
    span_mm: float,
    moment_knm: float,
    position_mm: float,
    num_points: int = 50,
) -> tuple[list[float], list[float], list[float]]:
    """Simply supported beam with an applied moment at a given position.

    Args:
        span_mm: Beam span (mm).
        moment_knm: Applied moment (kN·m). Positive = sagging.
        position_mm: Distance from left support (mm).
        num_points: Number of output points.

    Returns:
        Tuple of (positions_mm, bmd_knm, sfd_kn).
    """
```

**Update `compute_bmd_sfd()`:** Replace the two `NotImplementedError` branches with calls to the new functions.

### Tests: `tests/unit/test_load_analysis.py`

Add two test classes:
- `TestTriangularLoad` — verify reactions, max moment position (L/√3), zero moment at supports
- `TestAppliedMoment` — verify reactions, BMD slope change at moment point, equilibrium

---

## TASK-517: Project Bill of Quantities (BOQ)

### Audit

| Item | Status | Location |
|------|--------|----------|
| `BBSDocument` / `BBSummary` | ✅ Done | `services/bbs.py` — per-beam BBS with weight/length by diameter |
| `generate_bbs_from_detailing()` | ✅ Done | Same — creates full BBS from beam detailing result |
| Cost rates | ✅ Done | `GET /api/v1/optimization/cost-rates` — Fe500: ₹60/kg, M25: ₹6000/m³ |
| By-story breakdown | ✅ Done | `DashboardData.by_story` in insights |
| Project-level aggregation | ❌ Missing | No function sums BBS across multiple beams |
| BOQ endpoint | ❌ Missing | No `/api/v1/insights/project-boq` endpoint |
| BOQ React panel | ❌ Missing | Dashboard has per-beam data only |

### Python: `services/boq.py` (new module, ~120 lines)

```python
"""
Module:       boq
Description:  Project Bill of Quantities aggregation

Aggregates BBSSummary data from multiple beams into a project-level BOQ
with steel by diameter/grade, concrete by grade, and cost estimates.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from structural_lib.services.bbs import BBSDocument, BBSummary


@dataclass
class SteelSummary:
    """Steel quantities for one grade."""
    grade: str                                      # "Fe500", "Fe415"
    total_weight_kg: float = 0.0
    weight_by_diameter: dict[float, float] = field(default_factory=dict)
    count_by_diameter: dict[float, int] = field(default_factory=dict)
    cost_inr: float = 0.0


@dataclass
class ConcreteSummary:
    """Concrete quantities for one grade."""
    grade: str                                      # "M25", "M30"
    total_volume_m3: float = 0.0
    cost_inr: float = 0.0


@dataclass
class StorySummary:
    """Quantities for one story/floor."""
    story: str
    beam_count: int = 0
    steel_kg: float = 0.0
    concrete_m3: float = 0.0
    cost_inr: float = 0.0


@dataclass
class ProjectBOQ:
    """Complete Bill of Quantities for a project."""
    project_name: str
    total_beams: int
    steel: list[SteelSummary]
    concrete: list[ConcreteSummary]
    by_story: list[StorySummary]
    grand_total_steel_kg: float
    grand_total_concrete_m3: float
    grand_total_cost_inr: float


def aggregate_project_boq(
    bbs_documents: list[BBSDocument],
    beam_metadata: list[dict[str, Any]],
    steel_cost_per_kg: float = 60.0,
    concrete_costs: dict[int, float] | None = None,
    project_name: str = "Project",
) -> ProjectBOQ:
    """Aggregate BBS data from multiple beams into project BOQ.

    Args:
        bbs_documents: BBS documents from batch detailing.
        beam_metadata: Per-beam metadata with keys:
            beam_id, story, b_mm, D_mm, span_mm, fck
        steel_cost_per_kg: Steel rate (₹/kg). Default 60.0 (Fe500 India 2023).
        concrete_costs: {fck: ₹/m³}. Default {25: 6000, 30: 7000}.
        project_name: Display name for the project.

    Returns:
        ProjectBOQ with aggregated quantities and costs.

    Units:
        Steel: kg, Concrete: m³, Cost: ₹ (INR)
    """
```

**Key design decisions:**
- **Input = `BBSDocument[]` + metadata** — reuses existing BBS output, not raw design results
- **Concrete volume = b × D × span / 1e9** (mm³ → m³) — gross volume, note in API docs
- **Cost rates match existing `/optimization/cost-rates`** pattern
- **by_story grouping** uses the `story` field from beam metadata (same field used throughout import pipeline)

### FastAPI: `models/boq.py` (new)

Pydantic models matching the dataclasses above:

```python
class BeamMetadata(BaseModel):
    beam_id: str
    story: str = Field(default="GF")
    b_mm: float = Field(..., gt=0)
    D_mm: float = Field(..., gt=0)
    span_mm: float = Field(..., gt=0)
    fck: int = Field(default=25)

class ProjectBOQRequest(BaseModel):
    project_name: str = Field(default="Project")
    beams: list[BeamMetadata]
    bbs_data: list[dict] | None = Field(default=None)  # Optional pre-computed BBS
    steel_cost_per_kg: float = Field(default=60.0, gt=0)
    concrete_costs: dict[int, float] | None = None

class ProjectBOQResponse(BaseModel):
    success: bool = True
    project_name: str
    total_beams: int
    grand_total_steel_kg: float
    grand_total_concrete_m3: float
    grand_total_cost_inr: float
    steel_by_grade: list[dict]
    concrete_by_grade: list[dict]
    by_story: list[dict]
```

### FastAPI: `routers/insights.py`

Add one endpoint:

```python
@router.post(
    "/project-boq",
    response_model=ProjectBOQResponse,
    summary="Project Bill of Quantities",
    description="Aggregate steel + concrete quantities across multiple beams.",
)
async def project_boq(request: ProjectBOQRequest) -> ProjectBOQResponse:
```

### React: `hooks/useProjectBOQ.ts` (new)

```typescript
export function useProjectBOQ() {
  return useMutation({
    mutationFn: fetchProjectBOQ,
    mutationKey: ["project-boq"],
  });
}
```

### React: `components/design/ProjectBOQPanel.tsx` (new)

Add to **DashboardPage** — shows:
- Total steel card (kg + ₹)
- Total concrete card (m³ + ₹)
- Per-story table
- "Export BOQ as CSV" button (client-side CSV from data)

### Tests

| Test | File |
|------|------|
| Unit: `aggregate_project_boq()` — 3 beams, 2 stories | `Python/tests/unit/test_boq.py` |
| Unit: Empty input returns zero totals | Same |
| Unit: Cost rates applied correctly | Same |
| FastAPI: `POST /insights/project-boq` | `fastapi_app/tests/test_insights.py` |
| React: `useProjectBOQ` hook | `react_app/src/hooks/__tests__/useProjectBOQ.test.ts` |

---

## TASK-518: Torsion API + React Integration

### Audit

| Item | Status | Location |
|------|--------|----------|
| `design_torsion()` | ✅ Done | `codes/is456/torsion.py` — 540 lines, complete Clause 41 |
| `TorsionResult` dataclass | ✅ Done | Same — 16 fields (ve, me, tv, tc, asv, spacing, al, is_safe) |
| `calculate_equivalent_shear()` | ✅ Done | Cl 41.3.1: Ve = Vu + 1.6(Tu/b) |
| `calculate_equivalent_moment()` | ✅ Done | Cl 41.4.2: Me = Mu + Mt |
| `calculate_torsion_stirrup_area()` | ✅ Done | Cl 41.4.3: combined T+V stirrups |
| `calculate_longitudinal_torsion_steel()` | ✅ Done | Cl 41.4.2.1: Al for torsion |
| Import in `services/api.py` | ✅ Done | Lines 27-34 — all 6 functions imported |
| API wrapper function | ❌ Missing | No `design_torsion_is456()` in `services/api.py` |
| FastAPI endpoint | ❌ Missing | No torsion endpoint in any router |
| React UI | ❌ Missing | No torsion inputs or results display |

### Python: `services/api.py`

Add one public function (matching `design_beam_is456()` pattern):

```python
def design_torsion_is456(
    *,
    units: str,
    tu_knm: float,
    vu_kn: float,
    mu_knm: float,
    b_mm: float,
    D_mm: float,
    d_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    cover_mm: float = 40.0,
    stirrup_dia_mm: float = 8.0,
    pt_percent: float = 1.0,
) -> dict[str, Any]:
    """Design beam for combined torsion, shear, and bending per IS 456 Cl 41.

    This is the public API entrypoint for torsion design. It wraps
    `codes.is456.torsion.design_torsion()` with consistent naming.

    Args:
        units: Units label (must be IS456).
        tu_knm: Factored torsional moment (kN·m).
        vu_kn: Factored shear force (kN).
        mu_knm: Factored bending moment (kN·m).
        b_mm: Beam width (mm).
        D_mm: Overall depth (mm).
        d_mm: Effective depth (mm).
        fck_nmm2: Concrete strength (N/mm²).
        fy_nmm2: Steel yield strength (N/mm²).
        cover_mm: Clear cover (mm).
        stirrup_dia_mm: Stirrup diameter (mm).
        pt_percent: Tension steel percentage (%).

    Returns:
        Dict with TorsionResult fields.

    Units (IS456):
        Tu: kN·m, Vu: kN, Mu: kN·m
        b_mm, D_mm, d_mm: mm
        fck_nmm2, fy_nmm2: N/mm²
    """
    _require_is456_units(units)

    result = design_torsion(
        tu_knm=tu_knm,
        vu_kn=vu_kn,
        mu_knm=mu_knm,
        b=b_mm,
        D=D_mm,
        d=d_mm,
        fck=fck_nmm2,
        fy=fy_nmm2,
        cover=cover_mm,
        stirrup_dia=stirrup_dia_mm,
        pt=pt_percent,
    )

    return {
        "tu_knm": result.tu_knm,
        "vu_kn": result.vu_kn,
        "mu_knm": result.mu_knm,
        "ve_kn": result.ve_kn,
        "me_knm": result.me_knm,
        "tv_equiv_nmm2": result.tv_equiv,
        "tc_nmm2": result.tc,
        "tc_max_nmm2": result.tc_max,
        "asv_torsion_mm2_per_mm": result.asv_torsion,
        "asv_shear_mm2_per_mm": result.asv_shear,
        "asv_total_mm2_per_mm": result.asv_total,
        "stirrup_spacing_mm": result.stirrup_spacing,
        "al_torsion_mm2": result.al_torsion,
        "is_safe": result.is_safe,
        "requires_closed_stirrups": result.requires_closed_stirrups,
    }
```

> **Key: parameter names use `_nmm2` suffix** (matches `fck_nmm2`, `fy_nmm2` in `design_beam_is456`). Return dict keys use explicit units (matches other API functions).

### FastAPI: `models/torsion.py` (new)

```python
class TorsionDesignRequest(BaseModel):
    width: float = Field(..., gt=0, description="Beam width (mm)")
    depth: float = Field(..., gt=0, description="Overall depth (mm)")
    effective_depth: float | None = Field(default=None, description="Effective depth (mm)")
    fck: float = Field(default=25, gt=0, description="Concrete grade (N/mm²)")
    fy: float = Field(default=500, gt=0, description="Steel grade (N/mm²)")
    torsion: float = Field(..., ge=0, description="Factored torsion Tu (kN·m)")
    shear: float = Field(..., ge=0, description="Factored shear Vu (kN)")
    moment: float = Field(default=0, ge=0, description="Factored moment Mu (kN·m)")
    cover: float = Field(default=40, ge=20, le=75, description="Clear cover (mm)")
    stirrup_dia: float = Field(default=8, description="Stirrup diameter (mm)")

class TorsionDesignResponse(BaseModel):
    success: bool
    is_safe: bool
    ve_kn: float
    me_knm: float
    tv_equiv_nmm2: float
    tc_nmm2: float
    tc_max_nmm2: float
    asv_torsion_mm2_per_mm: float
    asv_shear_mm2_per_mm: float
    asv_total_mm2_per_mm: float
    stirrup_spacing_mm: float
    al_torsion_mm2: float
    requires_closed_stirrups: bool
```

### FastAPI: `routers/design.py`

Add one endpoint alongside existing `/design/beam`:

```python
@router.post(
    "/beam/torsion",
    response_model=TorsionDesignResponse,
    summary="Design Beam for Torsion",
    description="Combined torsion + shear + bending design per IS 456 Clause 41.",
)
async def design_beam_torsion(request: TorsionDesignRequest) -> TorsionDesignResponse:
```

### React: Torsion inputs in `DesignView`

**Not a separate page.** Add to existing DesignView:
1. Toggle: "Include Torsion" checkbox in the beam form
2. When enabled, show: `Tu (kN·m)` input field
3. Call `/api/v1/design/beam/torsion` instead of `/api/v1/design/beam`
4. Show torsion results below shear results (Ve, Me, closed stirrups required, spacing)

### React: `hooks/useTorsionDesign.ts` (new)

```typescript
export function useTorsionDesign() {
  return useMutation({
    mutationFn: fetchTorsionDesign,
    mutationKey: ["torsion-design"],
  });
}
```

### Tests

| Test | File |
|------|------|
| Unit: `design_torsion_is456()` basic case | `Python/tests/unit/test_torsion_api.py` |
| Unit: High torsion → is_safe=false | Same |
| Unit: Zero torsion → acts like pure shear | Same |
| FastAPI: `POST /design/beam/torsion` | `fastapi_app/tests/test_design.py` |
| React: `useTorsionDesign` hook | `react_app/src/hooks/__tests__/useTorsionDesign.test.ts` |

---

## TASK-519: Alternatives Panel (Pareto Front)

### Audit

| Item | Status | Location |
|------|--------|----------|
| `optimize_pareto_front()` | ✅ Done | `services/multi_objective_optimizer.py` — NSGA-II, ~650 lines |
| `ParetoCandidate` dataclass | ✅ Done | Same — b_mm, D_mm, ast, bar_config, cost, utilization, rank |
| `ParetoOptimizationResult` | ✅ Done | Same — pareto_front, all_candidates, stats |
| `get_design_explanation()` | ✅ Done | Same — human-readable explanation string |
| Cost optimizer endpoint | ✅ Done | `POST /api/v1/optimization/beam/cost` |
| Pareto endpoint | ❌ Missing | `optimize_pareto_front` not exposed in FastAPI |
| React UI | ❌ Missing | No alternatives panel anywhere |

### FastAPI: `models/optimization.py` (extend)

Add models:

```python
class ParetoRequest(BaseModel):
    span_mm: float = Field(..., gt=0)
    moment: float = Field(..., gt=0, description="Mu (kN·m)")
    shear: float = Field(..., gt=0, description="Vu (kN)")
    cover_mm: float = Field(default=40, ge=20, le=75)
    objectives: list[str] = Field(
        default=["cost", "utilization"],
        description="Objectives: cost, steel_weight, utilization"
    )
    max_candidates: int = Field(default=50, ge=5, le=200)

class ParetoCandidate(BaseModel):
    rank: int
    b_mm: float
    D_mm: float
    d_mm: float
    fck: float
    fy: float
    ast_required_mm2: float
    bar_config: str
    utilization: float
    cost_per_m: float
    steel_weight_kg: float
    explanation: str

class ParetoResponse(BaseModel):
    success: bool = True
    pareto_front: list[ParetoCandidate]
    total_evaluated: int
    objectives: list[str]
```

### FastAPI: `routers/optimization.py`

```python
@router.post(
    "/beam/pareto",
    response_model=ParetoResponse,
    summary="Pareto-Optimal Beam Designs",
    description="Find cost-vs-safety tradeoff alternatives using NSGA-II.",
)
async def optimize_beam_pareto(request: ParetoRequest) -> ParetoResponse:
```

### React: `hooks/useParetoDesign.ts` (new)

```typescript
export function useParetoDesign() {
  return useMutation({
    mutationFn: fetchParetoDesign,
    mutationKey: ["pareto-design"],
  });
}
```

### React: `components/design/AlternativesPanel.tsx` (new)

Placed in **DesignView** — triggered by "See Alternatives" button:

```
┌──── Design Alternatives (3 Pareto-optimal) ─────┐
│                                                   │
│  Section    │ Steel  │ Config  │ Util  │ ₹/m     │
│  300×500    │ 850mm² │ 3-20φ  │ 78%   │ ₹1,250  │ ← current
│  250×600    │ 720mm² │ 3-18φ  │ 82%   │ ₹1,180  │ [Apply]
│  350×450    │ 950mm² │ 4-18φ  │ 71%   │ ₹1,320  │ [Apply]
│                                                   │
│  Sort by: [Cost ▼] [Utilization] [Steel]         │
└───────────────────────────────────────────────────┘
```

"Apply" button → `useDesignStore.getState().setInputs({ width: b_mm, depth: D_mm })` → triggers re-design.

### Tests

| Test | File |
|------|------|
| FastAPI: `POST /optimization/beam/pareto` returns candidates | `fastapi_app/tests/test_optimization.py` |
| FastAPI: Pareto front has rank ordering | Same |
| React: `useParetoDesign` hook | `react_app/src/hooks/__tests__/useParetoDesign.test.ts` |

---

## TASK-520: Report / 3D Visualization Test Coverage

### Audit

| Module | Lines | Tests | Gap |
|--------|-------|-------|-----|
| `services/report.py` | 1700+ | 0 | Full — `export_html()`, `export_json()`, all section renderers |
| `visualization/geometry_3d.py` | ~400 | Partial | `beam_to_3d_geometry()` may have a basic test |
| `services/dashboard.py` | ~200 | 0 | Dashboard aggregation untested |

### Python Tests to Create

**`tests/unit/test_report.py`:**
- `test_export_html_returns_valid_html` — call with sample ReportData, check `<html>` wrapper
- `test_export_json_returns_valid_json` — parse output, check keys
- `test_export_html_includes_flexure_shear` — check section headings present
- `test_export_html_includes_beam_id` — verify beam_id appears in output
- `test_export_pdf_calls_weasyprint` — mock WeasyPrint, verify called with HTML string

**`tests/unit/test_geometry_3d.py`:**
- `test_beam_to_3d_geometry_returns_positions` — verify rebar positions are realistic
- `test_beam_to_3d_geometry_stirrup_count` — verify stirrup spacing generates correct count
- `test_beam_to_3d_geometry_with_seismic` — verify IS 13920 stirrup rules

**`tests/unit/test_dashboard.py`:**
- `test_aggregate_beam_results` — 5 beams, check pass_rate
- `test_by_story_breakdown` — multi-story input, verify story grouping

---

## TASK-521: Beam Rationalization

### Audit

No rationalization logic exists anywhere. This needs full design + implementation.

### Python: `services/rationalization.py` (new, ~250 lines)

```python
@dataclass
class RationalizationResult:
    """Result of beam section rationalization."""
    original_section_count: int
    proposed_section_count: int
    proposed_sections: list[dict[str, float]]   # [{b_mm, D_mm, count}]
    assignments: dict[str, dict[str, float]]    # {beam_id: {b_mm, D_mm}}
    max_utilization_before: float
    max_utilization_after: float
    all_safe: bool
    savings_summary: str


def rationalize_sections(
    beams: list[dict[str, Any]],
    max_sections: int = 4,
    max_utilization: float = 0.90,
    fck: float = 25,
    fy: float = 500,
) -> RationalizationResult:
    """Propose standard sections to reduce formwork variety.

    Algorithm:
    1. Group beams by b_mm × D_mm
    2. For each unique section, record max(Mu, Vu) among its beams
    3. Sort sections by demand (max moment)
    4. Greedily merge smallest sections into nearest larger section
       until ≤ max_sections remain
    5. Re-check all beams via check_beam_is456() with proposed sections
    6. Reject any merger that pushes utilization > max_utilization

    Args:
        beams: List of dicts with beam_id, b_mm, D_mm, mu_knm, vu_kn, story.
        max_sections: Target number of unique sections (default 4).
        max_utilization: Maximum allowed utilization after rationalization.
        fck: Concrete grade for re-checking.
        fy: Steel grade for re-checking.

    Returns:
        RationalizationResult with proposed sections and safety verification.
    """
```

### FastAPI: `routers/insights.py`

```python
@router.post(
    "/rationalize",
    response_model=RationalizationResponse,
    summary="Rationalize Beam Sections",
    description="Reduce unique beam sections while maintaining IS 456 safety.",
)
async def rationalize_sections(request: RationalizationRequest) -> RationalizationResponse:
```

### React: `components/design/RationalizationPanel.tsx` (new)

Add to **BuildingEditorPage** — "Rationalize Sections" button:

```
Before: 23 unique sections → After: 4 standard sections
Max utilization: 71% → 87% (all safe ✅)
[Accept] → updates AG Grid
```

### Tests

| Test | File |
|------|------|
| Unit: 5 beams → rationalize to 2 sections | `Python/tests/unit/test_rationalization.py` |
| Unit: All beams same section → no change | Same |
| Unit: Utilization cap prevents unsafe merge | Same |
| FastAPI endpoint | `fastapi_app/tests/test_insights.py` |

---

## Summary: Complete File List

### New Python Files (4)
| File | Task | Lines |
|------|------|-------|
| `Python/structural_lib/services/boq.py` | TASK-517 | ~120 |
| `Python/structural_lib/services/rationalization.py` | TASK-521 | ~250 |
| `Python/tests/unit/test_boq.py` | TASK-517 | ~80 |
| `Python/tests/unit/test_rationalization.py` | TASK-521 | ~100 |

### Modified Python Files (3)
| File | Task | Change |
|------|------|--------|
| `services/api.py` | TASK-518 | Add `design_torsion_is456()` (~60 lines) |
| `services/report.py` | TASK-514 | Add `export_pdf()` (~15 lines) |
| `codes/is456/load_analysis.py` | TASK-516 | Add triangular + moment functions (~120 lines) |

### New FastAPI Files (3)
| File | Task | Lines |
|------|------|-------|
| `fastapi_app/models/loads.py` | TASK-515 | ~50 |
| `fastapi_app/models/torsion.py` | TASK-518 | ~40 |
| `fastapi_app/models/boq.py` | TASK-517 | ~40 |

### Modified FastAPI Files (4)
| File | Task | Change |
|------|------|--------|
| `routers/analysis.py` | TASK-515 | Add `POST /analysis/loads/simple` |
| `routers/design.py` | TASK-518 | Add `POST /design/beam/torsion` |
| `routers/optimization.py` | TASK-519 | Add `POST /optimization/beam/pareto` |
| `routers/insights.py` | TASK-517, 521 | Add `POST /insights/project-boq`, `POST /insights/rationalize` |
| `routers/export.py` | TASK-514 | Extend format pattern to include `pdf` |

### New React Files (7)
| File | Task | Lines |
|------|------|-------|
| `hooks/useLoadAnalysis.ts` | TASK-515 | ~50 |
| `hooks/useTorsionDesign.ts` | TASK-518 | ~50 |
| `hooks/useProjectBOQ.ts` | TASK-517 | ~50 |
| `hooks/useParetoDesign.ts` | TASK-519 | ~50 |
| `components/design/LoadCalculatorPanel.tsx` | TASK-515 | ~150 |
| `components/design/AlternativesPanel.tsx` | TASK-519 | ~120 |
| `components/design/ProjectBOQPanel.tsx` | TASK-517 | ~100 |

### Modified React Files (3)
| File | Task | Change |
|------|------|--------|
| `hooks/useExport.ts` | TASK-514 | Extend format type to include `"pdf"` |
| `components/design/DesignView.tsx` | TASK-515, 518, 519 | Add Load Calculator, Torsion toggle, Alternatives button |
| `components/pages/DashboardPage.tsx` | TASK-517 | Add ProjectBOQPanel |

### New Test Files (6)
| File | Task |
|------|------|
| `Python/tests/unit/test_boq.py` | TASK-517 |
| `Python/tests/unit/test_report.py` | TASK-520 |
| `Python/tests/unit/test_rationalization.py` | TASK-521 |
| `react_app/src/hooks/__tests__/useLoadAnalysis.test.ts` | TASK-515 |
| `react_app/src/hooks/__tests__/useTorsionDesign.test.ts` | TASK-518 |
| `react_app/src/hooks/__tests__/useParetoDesign.test.ts` | TASK-519 |

### Total New Endpoints (5)
| Method | Path | Task |
|--------|------|------|
| POST | `/api/v1/analysis/loads/simple` | TASK-515 |
| POST | `/api/v1/design/beam/torsion` | TASK-518 |
| POST | `/api/v1/optimization/beam/pareto` | TASK-519 |
| POST | `/api/v1/insights/project-boq` | TASK-517 |
| POST | `/api/v1/insights/rationalize` | TASK-521 |

After these: **40 endpoints** (up from 35), **6 new React hooks** (up from 18), **~4 new Python modules**.
