"""
Export Router — BBS, DXF, and Report exports.

Endpoints return binary downloads (CSV, DXF, HTML, JSON, PDF)
using StreamingResponse for efficient delivery.
"""

import html as html_lib
import io
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/export",
    tags=["export"],
)


# =============================================================================
# Request Models
# =============================================================================


class ExportBeamRequest(BaseModel):
    """Beam parameters for generating export artifacts."""

    beam_id: str = Field(default="BEAM-1")
    width: float = Field(..., gt=0, description="Beam width in mm")
    depth: float = Field(..., gt=0, description="Beam depth in mm")
    span_length: float = Field(default=0, ge=0, description="Span in mm")
    clear_cover: float = Field(
        default=40, ge=20, le=75, description="Clear cover in mm"
    )
    fck: float = Field(..., gt=0, description="Concrete grade N/mm²")
    fy: float = Field(..., gt=0, description="Steel grade N/mm²")
    ast_required: float = Field(..., ge=0, description="Required tension steel mm²")
    asc_required: float = Field(
        default=0, ge=0, description="Required compression steel mm²"
    )
    moment: float = Field(default=0, ge=0, description="Design moment kN·m")
    shear: float = Field(default=0, ge=0, description="Design shear kN")


class ExportReportRequest(BaseModel):
    """Design results for report generation."""

    beam_id: str = Field(default="BEAM-1")
    width: float = Field(..., gt=0)
    depth: float = Field(..., gt=0)
    fck: float = Field(..., gt=0)
    fy: float = Field(..., gt=0)
    moment: float = Field(default=0, ge=0)
    shear: float = Field(default=0, ge=0)
    ast_required: float = Field(default=0, ge=0)
    ast_provided: float = Field(default=0, ge=0)
    utilization: float = Field(default=0, ge=0, le=2)
    is_safe: bool = Field(default=True)
    format: str = Field(default="html", pattern="^(html|json|pdf)$")


# =============================================================================
# Helper: Run detailing to get BeamDetailingResult
# =============================================================================


def _run_detailing(req: ExportBeamRequest):
    """Run detailing and return the raw library result."""
    try:
        from structural_lib.services.api import detail_beam_is456
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="structural_lib not available",
        )

    span = req.span_length if req.span_length > 0 else req.depth * 12
    return detail_beam_is456(
        units="IS456",
        beam_id=req.beam_id,
        story="1F",
        b_mm=req.width,
        D_mm=req.depth,
        span_mm=span,
        cover_mm=req.clear_cover,
        fck_nmm2=req.fck,
        fy_nmm2=req.fy,
        ast_start_mm2=req.ast_required,
        ast_mid_mm2=req.ast_required * 0.7,
        ast_end_mm2=req.ast_required,
        asc_start_mm2=req.asc_required,
        asc_mid_mm2=0.0,
        asc_end_mm2=req.asc_required,
        stirrup_dia_mm=8.0,
        stirrup_spacing_start_mm=100.0,
        stirrup_spacing_mid_mm=150.0,
        stirrup_spacing_end_mm=100.0,
        is_seismic=False,
    )


# =============================================================================
# BBS Export
# =============================================================================


@router.post(
    "/bbs",
    summary="Export Bar Bending Schedule (CSV)",
    description="Generate BBS from beam parameters and return as CSV download.",
    response_class=StreamingResponse,
)
async def export_bbs(request: ExportBeamRequest):
    """Generate and download a Bar Bending Schedule as CSV."""
    try:
        from structural_lib.services.bbs import (
            generate_bbs_from_detailing,
            generate_summary_table,
        )
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="BBS module not available",
        )

    detailing = _run_detailing(request)
    items = generate_bbs_from_detailing(detailing)

    # Build CSV in memory
    buf = io.StringIO()
    buf.write(
        "bar_mark,member_id,diameter_mm,shape,cut_length_mm,no_of_bars,total_weight_kg\n"
    )
    for item in items:
        buf.write(
            f"{item.bar_mark},{item.member_id},{item.diameter_mm},"
            f"{item.shape_code},{item.cut_length_mm},"
            f"{item.no_of_bars},{item.total_weight_kg:.2f}\n"
        )

    # Add summary
    buf.write("\n")
    summary = generate_summary_table(items, request.beam_id, "text")
    buf.write(summary)

    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="BBS_{request.beam_id}.csv"'
        },
    )


# =============================================================================
# DXF Export
# =============================================================================


@router.post(
    "/dxf",
    summary="Export DXF Drawing",
    description="Generate beam DXF drawing and return as download.",
    response_class=StreamingResponse,
)
async def export_dxf(request: ExportBeamRequest):
    """Generate and download a DXF drawing of the beam."""
    try:
        from structural_lib.services.dxf_export import quick_dxf_bytes
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DXF export module not available",
        )

    detailing = _run_detailing(request)
    dxf_bytes = quick_dxf_bytes(
        detailing,
        include_title_block=True,
        project_name="Structural Engineering Library",
    )

    return StreamingResponse(
        io.BytesIO(dxf_bytes),
        media_type="application/dxf",
        headers={
            "Content-Disposition": f'attachment; filename="{request.beam_id}.dxf"'
        },
    )


# =============================================================================
# Report Export
# =============================================================================


@router.post(
    "/report",
    summary="Export Design Report",
    description="Generate a design report in HTML or JSON format.",
    response_class=StreamingResponse,
)
async def export_report(request: ExportReportRequest):
    """Generate and download a design report."""
    try:
        from structural_lib.services.report import (
            ReportData,
            export_html,
            export_json,
            export_pdf,
        )
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Report module not available",
        )

    beam_geom = {
        "b_mm": request.width,
        "D_mm": request.depth,
        "d_mm": request.depth - 50.0,
        "fck_nmm2": request.fck,
        "fy_nmm2": request.fy,
    }
    cases = [
        {
            "case_id": "1.5(DL+LL)",
            "mu_knm": request.moment,
            "vu_kn": request.shear,
        }
    ]
    results = {
        "1.5(DL+LL)": {
            "ast_required_mm2": request.ast_required,
            "ast_provided_mm2": request.ast_provided,
            "utilization": request.utilization,
            "is_ok": request.is_safe,
        }
    }
    report_data = ReportData(
        job_id=request.beam_id,
        code="IS456",
        units="SI-mm",
        beam=beam_geom,
        cases=cases,
        results=results,
        is_ok=request.is_safe,
        governing_utilization=request.utilization,
    )

    if request.format == "pdf":
        try:
            pdf_bytes = export_pdf(report_data)
        except (ImportError, OSError):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="PDF export requires weasyprint. Install with: pip install weasyprint>=60.0",
            )
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="Report_{request.beam_id}.pdf"'
            },
        )
    elif request.format == "html":
        content = export_html(report_data)
        return StreamingResponse(
            io.BytesIO(content.encode("utf-8")),
            media_type="text/html",
            headers={
                "Content-Disposition": f'attachment; filename="Report_{request.beam_id}.html"'
            },
        )
    else:
        content = export_json(report_data)
        return StreamingResponse(
            io.BytesIO(content.encode("utf-8")),
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="Report_{request.beam_id}.json"'
            },
        )


# =============================================================================
# Building / Batch Export
# =============================================================================


class BatchBeamRow(BaseModel):
    """One beam in a building-level export."""

    beam_id: str = "BEAM-1"
    story: str = ""
    width: float = Field(..., gt=0)
    depth: float = Field(..., gt=0)
    span_length: float = Field(default=0, ge=0)
    fck: float = Field(default=25, gt=0)
    fy: float = Field(default=500, gt=0)
    moment: float = Field(default=0, ge=0)
    shear: float = Field(default=0, ge=0)
    ast_required: float = Field(default=0, ge=0)
    ast_provided: float = Field(default=0, ge=0)
    asc_required: float = Field(default=0, ge=0)
    bar_count: Optional[int] = None
    bar_diameter: Optional[float] = None
    stirrup_diameter: Optional[float] = None
    stirrup_spacing: Optional[float] = None
    utilization: float = Field(default=0, ge=0)
    is_safe: bool = True
    status: str = "pending"


class BatchExportRequest(BaseModel):
    """Request for building-level export."""

    project_name: str = Field(default="Building Project")
    beams: list[BatchBeamRow]
    format: str = Field(default="html", pattern="^(html|pdf|csv)$")


@router.post(
    "/building-summary",
    summary="Export Building Summary Report",
    description="Generate a summary report for all beams in a building (HTML, PDF, or CSV).",
    response_class=StreamingResponse,
)
async def export_building_summary(request: BatchExportRequest):
    """Generate and download a building-level summary report."""

    beams = request.beams
    if not beams:
        raise HTTPException(400, detail="No beams provided")

    # Aggregate stats
    stories = sorted(set(b.story for b in beams if b.story))
    designed = [b for b in beams if b.ast_required > 0]
    passed = [b for b in designed if b.is_safe]
    failed = [b for b in designed if not b.is_safe]
    pending = [b for b in beams if b.ast_required <= 0]

    # Steel quantities (approximate using provided rebar)
    total_ast = sum(b.ast_provided for b in designed if b.ast_provided > 0)
    total_concrete_vol = sum(
        (b.width / 1000)
        * (b.depth / 1000)
        * (b.span_length / 1000 if b.span_length > 0 else b.depth * 12 / 1000)
        for b in beams
    )

    # Per-story breakdown
    story_data: dict[str, dict] = {}
    for b in beams:
        key = b.story or "Unknown"
        if key not in story_data:
            story_data[key] = {
                "beams": 0,
                "pass": 0,
                "fail": 0,
                "pending": 0,
                "ast_total": 0.0,
                "max_util": 0.0,
            }
        sd = story_data[key]
        sd["beams"] += 1
        if b.ast_required <= 0:
            sd["pending"] += 1
        elif b.is_safe:
            sd["pass"] += 1
        else:
            sd["fail"] += 1
        sd["ast_total"] += b.ast_provided
        sd["max_util"] = max(sd["max_util"], b.utilization)

    if request.format == "csv":
        buf = io.StringIO()
        buf.write("beam_id,story,b_mm,D_mm,span_mm,Mu_kNm,Vu_kN,")
        buf.write("fck,fy,ast_required,ast_provided,bars,stirrup,utilization,status\n")
        for b in beams:
            bars = (
                f"{b.bar_count}-T{b.bar_diameter}"
                if b.bar_count and b.bar_diameter
                else "-"
            )
            stirrup = (
                f"{b.stirrup_diameter or 8}@{b.stirrup_spacing}"
                if b.stirrup_spacing
                else "-"
            )
            sts = (
                "Pass"
                if b.is_safe and b.ast_required > 0
                else ("Fail" if b.ast_required > 0 else "Pending")
            )
            buf.write(
                f"{b.beam_id},{b.story},{b.width:.0f},{b.depth:.0f},"
                f"{b.span_length:.0f},{b.moment:.1f},{b.shear:.1f},"
                f"{b.fck:.0f},{b.fy:.0f},{b.ast_required:.0f},{b.ast_provided:.0f},"
                f"{bars},{stirrup},{b.utilization:.2f},{sts}\n"
            )
        buf.write("\nSummary\n")
        buf.write(f"Total Beams,{len(beams)}\n")
        buf.write(f"Designed,{len(designed)}\n")
        buf.write(f"Pass,{len(passed)}\n")
        buf.write(f"Fail,{len(failed)}\n")
        buf.write(f"Pending,{len(pending)}\n")
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="text/csv",
            headers={
                "Content-Disposition": 'attachment; filename="Building_Summary.csv"'
            },
        )

    # HTML report
    esc = html_lib.escape

    story_rows = ""
    for sname in sorted(story_data.keys()):
        sd = story_data[sname]
        story_rows += (
            f"<tr><td>{esc(sname)}</td><td>{sd['beams']}</td>"
            f"<td class='pass'>{sd['pass']}</td>"
            f"<td class='fail'>{sd['fail']}</td>"
            f"<td>{sd['pending']}</td>"
            f"<td>{sd['ast_total']:.0f}</td>"
            f"<td>{sd['max_util']:.0%}</td></tr>\n"
        )

    beam_rows = ""
    for b in beams:
        bars = (
            f"{b.bar_count}-T{int(b.bar_diameter)}"
            if b.bar_count and b.bar_diameter
            else "-"
        )
        stirrup = (
            f"{int(b.stirrup_diameter or 8)}\u00d8@{int(b.stirrup_spacing)}"
            if b.stirrup_spacing
            else "-"
        )
        sts_cls = (
            "pass"
            if b.is_safe and b.ast_required > 0
            else ("fail" if b.ast_required > 0 else "")
        )
        sts_txt = (
            "Pass"
            if b.is_safe and b.ast_required > 0
            else ("Fail" if b.ast_required > 0 else "Pending")
        )
        util_cls = (
            "fail" if b.utilization > 1 else ("warn" if b.utilization > 0.9 else "pass")
        )
        beam_rows += (
            f"<tr><td class='mono'>{esc(b.beam_id)}</td><td>{esc(b.story)}</td>"
            f"<td class='num'>{b.width:.0f}</td><td class='num'>{b.depth:.0f}</td>"
            f"<td class='num'>{b.span_length:.0f}</td>"
            f"<td class='num'>{b.moment:.1f}</td><td class='num'>{b.shear:.1f}</td>"
            f"<td class='num'>{b.ast_required:.0f}</td><td class='mono'>{bars}</td>"
            f"<td class='mono'>{stirrup}</td>"
            f"<td class='num {util_cls}'>{b.utilization:.0%}</td>"
            f"<td class='{sts_cls}'>{sts_txt}</td></tr>\n"
        )

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Building Summary — {esc(request.project_name)}</title>
<style>
* {{ box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
       margin: 0; padding: 24px; font-size: 13px; color: #2c3e50; background: #fff; max-width: 1200px; margin: 0 auto; }}
@media print {{ body {{ padding: 0; font-size: 11px; max-width: none; }} }}
h1 {{ font-size: 22px; color: #1a365d; border-bottom: 3px solid #3182ce; padding-bottom: 10px; }}
h2 {{ font-size: 16px; color: #2d3748; border-left: 4px solid #3182ce; padding: 6px 12px;
     background: linear-gradient(90deg, #ebf8ff 0%, transparent 100%); margin: 24px 0 12px -12px; }}
.summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin: 16px 0; }}
.stat {{ background: #f7fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; text-align: center; }}
.stat .value {{ font-size: 28px; font-weight: 700; color: #2d3748; }}
.stat .label {{ font-size: 11px; color: #718096; margin-top: 4px; }}
.stat.pass .value {{ color: #22543d; }}
.stat.fail .value {{ color: #c53030; }}
table {{ width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 12px; }}
th {{ background: #2d3748; color: #fff; padding: 8px 10px; text-align: left; font-weight: 600; }}
td {{ padding: 6px 10px; border-bottom: 1px solid #e2e8f0; }}
tr:hover {{ background: #f7fafc; }}
.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
.mono {{ font-family: "SF Mono", "Fira Code", monospace; font-size: 11px; }}
.pass {{ color: #22543d; font-weight: 600; }}
.fail {{ color: #c53030; font-weight: 600; }}
.warn {{ color: #b7791f; font-weight: 600; }}
footer {{ margin-top: 24px; font-size: 11px; color: #a0aec0; border-top: 1px solid #e2e8f0; padding-top: 8px; }}
</style>
</head>
<body>
<h1>Building Summary Report</h1>
<p><strong>Project:</strong> {esc(request.project_name)} &nbsp;|&nbsp;
<strong>Code:</strong> IS 456:2000 &nbsp;|&nbsp;
<strong>Total Beams:</strong> {len(beams)} &nbsp;|&nbsp;
<strong>Stories:</strong> {len(stories)}</p>

<div class="summary-grid">
  <div class="stat"><div class="value">{len(beams)}</div><div class="label">Total Beams</div></div>
  <div class="stat pass"><div class="value">{len(passed)}</div><div class="label">Pass</div></div>
  <div class="stat fail"><div class="value">{len(failed)}</div><div class="label">Fail</div></div>
  <div class="stat"><div class="value">{len(pending)}</div><div class="label">Pending</div></div>
  <div class="stat"><div class="value">{total_ast:.0f}</div><div class="label">Total Ast (mm\u00b2)</div></div>
  <div class="stat"><div class="value">{total_concrete_vol:.1f}</div><div class="label">Conc. Vol (m\u00b3)</div></div>
</div>

<h2>Per-Story Summary</h2>
<table>
<tr><th>Story</th><th>Beams</th><th>Pass</th><th>Fail</th><th>Pending</th><th>Ast Total (mm\u00b2)</th><th>Max Util.</th></tr>
{story_rows}
</table>

<h2>All Beams</h2>
<table>
<tr><th>ID</th><th>Story</th><th>b (mm)</th><th>D (mm)</th><th>Span (mm)</th><th>Mu (kN\u00b7m)</th><th>Vu (kN)</th><th>Ast Req</th><th>Bars</th><th>Stirrup</th><th>Util.</th><th>Status</th></tr>
{beam_rows}
</table>

<footer>Generated by structural_engineering_lib &mdash; IS 456:2000 Beam Design</footer>
</body>
</html>"""

    if request.format == "pdf":
        try:
            import weasyprint
        except (ImportError, OSError):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="PDF export requires weasyprint. Install with: pip install weasyprint>=60.0",
            )
        pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="Building_Summary.pdf"'
            },
        )

    return StreamingResponse(
        io.BytesIO(html_content.encode("utf-8")),
        media_type="text/html",
        headers={"Content-Disposition": 'attachment; filename="Building_Summary.html"'},
    )
