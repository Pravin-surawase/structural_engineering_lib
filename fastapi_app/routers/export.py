"""
Export Router — BBS, DXF, and Report exports.

Endpoints return binary downloads (CSV, DXF, HTML, JSON)
using StreamingResponse for efficient delivery.
"""

import io
import json

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
    clear_cover: float = Field(default=40, ge=20, le=75, description="Clear cover in mm")
    fck: float = Field(..., gt=0, description="Concrete grade N/mm²")
    fy: float = Field(..., gt=0, description="Steel grade N/mm²")
    ast_required: float = Field(..., ge=0, description="Required tension steel mm²")
    asc_required: float = Field(default=0, ge=0, description="Required compression steel mm²")
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
    format: str = Field(default="html", pattern="^(html|json)$")


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
    buf.write("bar_mark,member_id,diameter_mm,shape,cut_length_mm,quantity,weight_kg\n")
    for item in items:
        buf.write(
            f"{item.bar_mark},{item.member_id},{item.diameter_mm},"
            f"{getattr(item, 'shape', 'straight')},{item.cut_length_mm},"
            f"{item.quantity},{item.weight_kg:.2f}\n"
        )

    # Add summary
    buf.write("\n")
    summary = generate_summary_table(items, request.beam_id, "text")
    buf.write(summary)

    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="BBS_{request.beam_id}.csv"'},
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
        headers={"Content-Disposition": f'attachment; filename="{request.beam_id}.dxf"'},
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
        from structural_lib.services.report import export_html, export_json
        from structural_lib.services.report import ReportData
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Report module not available",
        )

    report_data = ReportData(
        beam_id=request.beam_id,
        b_mm=request.width,
        D_mm=request.depth,
        fck=request.fck,
        fy=request.fy,
        mu_knm=request.moment,
        vu_kn=request.shear,
        ast_required=request.ast_required,
        ast_provided=request.ast_provided,
        utilization=request.utilization,
        is_safe=request.is_safe,
    )

    if request.format == "html":
        content = export_html(report_data)
        return StreamingResponse(
            io.BytesIO(content.encode("utf-8")),
            media_type="text/html",
            headers={"Content-Disposition": f'attachment; filename="Report_{request.beam_id}.html"'},
        )
    else:
        content = export_json(report_data)
        return StreamingResponse(
            io.BytesIO(content.encode("utf-8")),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="Report_{request.beam_id}.json"'},
        )
