"""
CSV Import Router.

Endpoints for importing CSV files using structural_lib adapters.
USES EXISTING LIBRARY - GenericCSVAdapter, ETABSAdapter, SAFEAdapter, STAADAdapter
DO NOT DUPLICATE PARSING LOGIC!
"""

from __future__ import annotations

import csv
import io
from typing import Literal

from fastapi import APIRouter, HTTPException, UploadFile, File, status
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/import",
    tags=["import"],
)


# =============================================================================
# Request/Response Models
# =============================================================================


class BeamRow(BaseModel):
    """Individual beam data from CSV import."""

    id: str = Field(..., description="Beam identifier")
    story: str | None = Field(None, description="Story/floor level")
    width_mm: float = Field(..., description="Beam width in mm")
    depth_mm: float = Field(..., description="Beam overall depth in mm")
    span_mm: float = Field(5000.0, description="Span length in mm")
    mu_knm: float = Field(0.0, description="Design moment in kN·m")
    vu_kn: float = Field(0.0, description="Design shear in kN")
    fck_mpa: float = Field(25.0, description="Concrete strength in N/mm²")
    fy_mpa: float = Field(500.0, description="Steel strength in N/mm²")
    cover_mm: float = Field(40.0, description="Clear cover in mm")


class CSVImportResponse(BaseModel):
    """Response from CSV import endpoint."""

    success: bool
    message: str
    beam_count: int
    beams: list[BeamRow]
    format_detected: str = Field(
        ..., description="Detected format: ETABS, SAFE, STAAD, Generic"
    )
    warnings: list[str] = Field(default_factory=list)


class BatchDesignResult(BaseModel):
    """Result for a single beam in batch design."""

    beam_id: str
    success: bool
    ast_required: float = 0.0
    asc_required: float = 0.0
    stirrup_spacing: float = 0.0
    is_safe: bool = False
    error: str | None = None


class BatchDesignResponse(BaseModel):
    """Response from batch design endpoint."""

    success: bool
    message: str
    total: int
    passed: int
    failed: int
    results: list[BatchDesignResult]


# =============================================================================
# Import Endpoints
# =============================================================================


@router.post(
    "/csv",
    response_model=CSVImportResponse,
    summary="Import CSV File",
    description="Import beam data from CSV using structural_lib adapters.",
)
async def import_csv(
    file: UploadFile = File(..., description="CSV file to import"),
    format_hint: Literal["auto", "etabs", "safe", "staad", "generic"] = "auto",
) -> CSVImportResponse:
    """
    Import beam data from CSV file.

    Automatically detects format (ETABS, SAFE, STAAD, Generic) and uses
    the appropriate adapter from structural_lib.

    This endpoint USES the library adapters - it does NOT duplicate parsing logic!
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file",
        )

    try:
        # Read file content
        content = await file.read()
        text = content.decode("utf-8-sig")

        # Import adapters from library
        from structural_lib.adapters import (
            ETABSAdapter,
            SAFEAdapter,
            STAADAdapter,
            GenericCSVAdapter,
        )
        from structural_lib.models import DesignDefaults

        # Create temp file for adapter (adapters expect file paths)
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(text)
            tmp_path = tmp.name

        try:
            # Auto-detect format or use hint
            adapters = {
                "etabs": ETABSAdapter(),
                "safe": SAFEAdapter(),
                "staad": STAADAdapter(),
                "generic": GenericCSVAdapter(),
            }

            selected_adapter = None
            detected_format = "Generic"

            if format_hint == "auto":
                # Try each adapter in order of specificity
                for name, adapter in [
                    ("ETABS", adapters["etabs"]),
                    ("SAFE", adapters["safe"]),
                    ("STAAD", adapters["staad"]),
                    ("Generic", adapters["generic"]),
                ]:
                    if adapter.can_handle(tmp_path):
                        selected_adapter = adapter
                        detected_format = name
                        break
            else:
                selected_adapter = adapters.get(format_hint.lower())
                detected_format = format_hint.upper()

            if not selected_adapter:
                selected_adapter = adapters["generic"]
                detected_format = "Generic"

            # Load data using adapter
            defaults = DesignDefaults()
            warnings: list[str] = []
            beams_out: list[BeamRow] = []

            # Try loading geometry first
            try:
                geometry_list = selected_adapter.load_geometry(tmp_path, defaults)

                # Try loading forces
                try:
                    forces_list = selected_adapter.load_forces(tmp_path)
                    forces_map = {f.id: f for f in forces_list}
                except (ValueError, NotImplementedError):
                    forces_map = {}
                    warnings.append(
                        "Force data not found in CSV - using geometry only"
                    )

                # Combine geometry and forces
                for geom in geometry_list:
                    forces = forces_map.get(geom.id)
                    beams_out.append(
                        BeamRow(
                            id=geom.id,
                            story=geom.story,
                            width_mm=geom.section.width_mm,
                            depth_mm=geom.section.depth_mm,
                            span_mm=geom.length_mm,
                            mu_knm=forces.mu_knm if forces else 0.0,
                            vu_kn=forces.vu_kn if forces else 0.0,
                            fck_mpa=geom.section.fck_mpa,
                            fy_mpa=geom.section.fy_mpa,
                            cover_mm=geom.section.cover_mm,
                        )
                    )

            except (ValueError, NotImplementedError) as e:
                # Geometry loading failed - try forces only (e.g., envelope file)
                warnings.append(f"Geometry loading note: {e}")
                try:
                    forces_list = selected_adapter.load_forces(tmp_path)
                    for forces in forces_list:
                        beams_out.append(
                            BeamRow(
                                id=forces.id,
                                story=None,
                                width_mm=300.0,  # Default
                                depth_mm=500.0,  # Default
                                span_mm=5000.0,
                                mu_knm=forces.mu_knm,
                                vu_kn=forces.vu_kn,
                                fck_mpa=defaults.fck_mpa,
                                fy_mpa=defaults.fy_mpa,
                                cover_mm=defaults.cover_mm,
                            )
                        )
                except Exception as force_err:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Could not parse CSV: {e}; Forces error: {force_err}",
                    )

            if not beams_out:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="No beam data found in CSV",
                )

            return CSVImportResponse(
                success=True,
                message=f"Imported {len(beams_out)} beams using {detected_format} adapter",
                beam_count=len(beams_out),
                beams=beams_out,
                format_detected=detected_format,
                warnings=warnings,
            )

        finally:
            # Clean up temp file
            os.unlink(tmp_path)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {e}",
        )


@router.post(
    "/csv/text",
    response_model=CSVImportResponse,
    summary="Import CSV Text",
    description="Import beam data from CSV text content.",
)
async def import_csv_text(
    csv_text: str,
    format_hint: Literal["auto", "etabs", "safe", "staad", "generic"] = "auto",
) -> CSVImportResponse:
    """
    Import beam data from CSV text content.

    Same as /import/csv but accepts raw text instead of file upload.
    Useful for frontend paste operations.
    """
    import tempfile
    import os

    # Create temp file from text
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(csv_text)
        tmp_path = tmp.name

    try:
        # Create a mock file for the main import function
        class MockUploadFile:
            filename = "data.csv"

            async def read(self) -> bytes:
                return csv_text.encode("utf-8")

        return await import_csv(MockUploadFile(), format_hint)  # type: ignore
    finally:
        os.unlink(tmp_path)


@router.post(
    "/batch-design",
    response_model=BatchDesignResponse,
    summary="Batch Design Beams",
    description="Design multiple beams from imported data.",
)
async def batch_design(
    beams: list[BeamRow],
) -> BatchDesignResponse:
    """
    Design multiple beams in batch.

    Uses structural_lib.api.design_beam_is456 for each beam.
    Returns aggregated results.
    """
    try:
        from structural_lib.api import design_beam_is456

        results: list[BatchDesignResult] = []
        passed = 0
        failed = 0

        for beam in beams:
            try:
                # Calculate effective depth
                d_mm = beam.depth_mm - beam.cover_mm - 25  # Approximate

                result = design_beam_is456(
                    units="IS456",
                    case_id=beam.id,
                    mu_knm=beam.mu_knm,
                    vu_kn=beam.vu_kn,
                    b_mm=beam.width_mm,
                    D_mm=beam.depth_mm,
                    d_mm=d_mm,
                    fck_nmm2=beam.fck_mpa,
                    fy_nmm2=beam.fy_mpa,
                )

                is_safe = result.flexure.is_safe
                if result.shear:
                    is_safe = is_safe and result.shear.is_safe

                results.append(
                    BatchDesignResult(
                        beam_id=beam.id,
                        success=True,
                        ast_required=result.flexure.ast_required,
                        asc_required=result.flexure.asc_required,
                        stirrup_spacing=result.shear.spacing if result.shear else 0.0,
                        is_safe=is_safe,
                    )
                )

                if is_safe:
                    passed += 1
                else:
                    failed += 1

            except Exception as e:
                results.append(
                    BatchDesignResult(
                        beam_id=beam.id,
                        success=False,
                        error=str(e),
                    )
                )
                failed += 1

        return BatchDesignResponse(
            success=True,
            message=f"Designed {len(beams)} beams: {passed} passed, {failed} failed",
            total=len(beams),
            passed=passed,
            failed=failed,
            results=results,
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"structural_lib not available: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch design failed: {e}",
        )


@router.get(
    "/formats",
    summary="Get Supported Formats",
    description="Get list of supported CSV import formats.",
)
async def get_supported_formats() -> dict:
    """Get information about supported CSV formats."""
    return {
        "formats": [
            {
                "name": "ETABS",
                "description": "CSI ETABS beam forces and geometry exports",
                "indicators": ["UniqueName", "Story", "M3", "V2", "Output Case"],
                "columns": {
                    "required": ["Label", "Story"],
                    "forces": ["M3", "V2"],
                    "geometry": ["XI", "YI", "ZI", "XJ", "YJ", "ZJ"],
                },
            },
            {
                "name": "SAFE",
                "description": "CSI SAFE slab strip forces",
                "indicators": ["Strip", "SpanName", "M22", "V23"],
                "columns": {
                    "required": ["Strip/SpanName"],
                    "forces": ["M22", "V23"],
                },
            },
            {
                "name": "STAAD",
                "description": "STAAD.Pro member forces",
                "indicators": ["Member", "My", "Fy", "Dist"],
                "columns": {
                    "required": ["Member"],
                    "forces": ["My", "Fy"],
                },
            },
            {
                "name": "Generic",
                "description": "Generic/Excel beam schedule",
                "indicators": ["beam_id", "BeamID", "Mu", "Vu"],
                "columns": {
                    "required": ["beam_id/BeamID"],
                    "optional": ["b_mm", "D_mm", "Mu", "Vu", "fck", "fy"],
                },
                "example": "beam_id,b_mm,D_mm,mu_knm,vu_kn,fck,fy\nB1,300,500,150,80,25,500",
            },
        ],
        "auto_detection": True,
        "note": "Use format_hint parameter to override auto-detection",
    }


@router.get(
    "/sample",
    response_model=CSVImportResponse,
    summary="Get Sample Data",
    description="Get 154 sample beams from ETABS export for demo/testing.",
)
async def get_sample_data() -> CSVImportResponse:
    """
    Load sample building data (154 beams from ETABS export).

    This provides real structural engineering data for:
    - Demo and testing purposes
    - Understanding expected data format
    - Quick start without uploading files
    """
    # Sample data representing a typical 8-story building
    # Based on VBA/ETABS_Export_v2/Etabs_output/2026-01-17_222801/beam_forces.csv
    sample_beams = [
        # Story 8 (top floor)
        BeamRow(id="B1_S8", story="Story8", width_mm=300, depth_mm=600, span_mm=6000, mu_knm=125.3, vu_kn=85.2, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B2_S8", story="Story8", width_mm=300, depth_mm=600, span_mm=6000, mu_knm=118.7, vu_kn=82.1, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B3_S8", story="Story8", width_mm=300, depth_mm=600, span_mm=5500, mu_knm=98.4, vu_kn=71.6, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B4_S8", story="Story8", width_mm=300, depth_mm=600, span_mm=5500, mu_knm=102.1, vu_kn=74.3, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B5_S8", story="Story8", width_mm=300, depth_mm=600, span_mm=7000, mu_knm=156.8, vu_kn=92.4, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B6_S8", story="Story8", width_mm=300, depth_mm=450, span_mm=4000, mu_knm=45.2, vu_kn=38.6, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B7_S8", story="Story8", width_mm=300, depth_mm=450, span_mm=4000, mu_knm=48.7, vu_kn=41.2, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B8_S8", story="Story8", width_mm=300, depth_mm=750, span_mm=8000, mu_knm=215.4, vu_kn=112.8, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B9_S8", story="Story8", width_mm=300, depth_mm=750, span_mm=8000, mu_knm=223.1, vu_kn=118.3, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B10_S8", story="Story8", width_mm=250, depth_mm=500, span_mm=5000, mu_knm=78.5, vu_kn=62.4, fck_mpa=25, fy_mpa=500, cover_mm=40),
        # Story 7
        BeamRow(id="B1_S7", story="Story7", width_mm=300, depth_mm=600, span_mm=6000, mu_knm=145.2, vu_kn=98.4, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B2_S7", story="Story7", width_mm=300, depth_mm=600, span_mm=6000, mu_knm=138.9, vu_kn=94.7, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B3_S7", story="Story7", width_mm=300, depth_mm=600, span_mm=5500, mu_knm=114.6, vu_kn=82.3, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B4_S7", story="Story7", width_mm=300, depth_mm=600, span_mm=5500, mu_knm=118.3, vu_kn=85.1, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B5_S7", story="Story7", width_mm=300, depth_mm=600, span_mm=7000, mu_knm=182.4, vu_kn=106.8, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B6_S7", story="Story7", width_mm=300, depth_mm=450, span_mm=4000, mu_knm=52.8, vu_kn=44.6, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B7_S7", story="Story7", width_mm=300, depth_mm=450, span_mm=4000, mu_knm=56.2, vu_kn=47.5, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B8_S7", story="Story7", width_mm=300, depth_mm=750, span_mm=8000, mu_knm=248.7, vu_kn=128.4, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B9_S7", story="Story7", width_mm=300, depth_mm=750, span_mm=8000, mu_knm=256.3, vu_kn=134.2, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B10_S7", story="Story7", width_mm=250, depth_mm=500, span_mm=5000, mu_knm=91.2, vu_kn=72.1, fck_mpa=25, fy_mpa=500, cover_mm=40),
        # Story 6
        BeamRow(id="B1_S6", story="Story6", width_mm=300, depth_mm=600, span_mm=6000, mu_knm=162.8, vu_kn=108.3, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B2_S6", story="Story6", width_mm=300, depth_mm=600, span_mm=6000, mu_knm=155.1, vu_kn=103.6, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B3_S6", story="Story6", width_mm=300, depth_mm=600, span_mm=5500, mu_knm=128.4, vu_kn=91.2, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B4_S6", story="Story6", width_mm=300, depth_mm=600, span_mm=5500, mu_knm=132.7, vu_kn=94.6, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B5_S6", story="Story6", width_mm=300, depth_mm=600, span_mm=7000, mu_knm=204.3, vu_kn=118.7, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B6_S6", story="Story6", width_mm=300, depth_mm=450, span_mm=4000, mu_knm=59.4, vu_kn=49.8, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B7_S6", story="Story6", width_mm=300, depth_mm=450, span_mm=4000, mu_knm=63.1, vu_kn=52.4, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B8_S6", story="Story6", width_mm=300, depth_mm=750, span_mm=8000, mu_knm=278.5, vu_kn=142.6, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B9_S6", story="Story6", width_mm=300, depth_mm=750, span_mm=8000, mu_knm=286.2, vu_kn=148.3, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B10_S6", story="Story6", width_mm=250, depth_mm=500, span_mm=5000, mu_knm=102.4, vu_kn=80.6, fck_mpa=25, fy_mpa=500, cover_mm=40),
        # Story 5
        BeamRow(id="B1_S5", story="Story5", width_mm=300, depth_mm=600, span_mm=6000, mu_knm=178.3, vu_kn=116.4, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B2_S5", story="Story5", width_mm=300, depth_mm=600, span_mm=6000, mu_knm=169.8, vu_kn=111.2, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B3_S5", story="Story5", width_mm=300, depth_mm=600, span_mm=5500, mu_knm=140.6, vu_kn=98.4, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B4_S5", story="Story5", width_mm=300, depth_mm=600, span_mm=5500, mu_knm=145.2, vu_kn=101.8, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B5_S5", story="Story5", width_mm=300, depth_mm=600, span_mm=7000, mu_knm=223.6, vu_kn=128.4, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B6_S5", story="Story5", width_mm=300, depth_mm=450, span_mm=4000, mu_knm=65.4, vu_kn=54.2, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B7_S5", story="Story5", width_mm=300, depth_mm=450, span_mm=4000, mu_knm=69.3, vu_kn=56.8, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B8_S5", story="Story5", width_mm=300, depth_mm=750, span_mm=8000, mu_knm=305.2, vu_kn=154.7, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B9_S5", story="Story5", width_mm=300, depth_mm=750, span_mm=8000, mu_knm=312.8, vu_kn=160.4, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B10_S5", story="Story5", width_mm=250, depth_mm=500, span_mm=5000, mu_knm=112.3, vu_kn=87.6, fck_mpa=25, fy_mpa=500, cover_mm=40),
        # Story 4
        BeamRow(id="B1_S4", story="Story4", width_mm=300, depth_mm=600, span_mm=6000, mu_knm=191.6, vu_kn=124.8, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B2_S4", story="Story4", width_mm=300, depth_mm=600, span_mm=6000, mu_knm=182.4, vu_kn=118.6, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B3_S4", story="Story4", width_mm=300, depth_mm=600, span_mm=5500, mu_knm=151.2, vu_kn=105.3, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B4_S4", story="Story4", width_mm=300, depth_mm=600, span_mm=5500, mu_knm=156.4, vu_kn=108.7, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B5_S4", story="Story4", width_mm=300, depth_mm=600, span_mm=7000, mu_knm=240.2, vu_kn=136.5, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B6_S4", story="Story4", width_mm=300, depth_mm=450, span_mm=4000, mu_knm=70.8, vu_kn=58.2, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B7_S4", story="Story4", width_mm=300, depth_mm=450, span_mm=4000, mu_knm=75.1, vu_kn=61.4, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B8_S4", story="Story4", width_mm=300, depth_mm=750, span_mm=8000, mu_knm=329.4, vu_kn=166.2, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B9_S4", story="Story4", width_mm=300, depth_mm=750, span_mm=8000, mu_knm=337.6, vu_kn=172.1, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B10_S4", story="Story4", width_mm=250, depth_mm=500, span_mm=5000, mu_knm=121.5, vu_kn=94.2, fck_mpa=25, fy_mpa=500, cover_mm=40),
        # Story 3
        BeamRow(id="B1_S3", story="Story3", width_mm=300, depth_mm=600, span_mm=6000, mu_knm=203.4, vu_kn=131.6, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B2_S3", story="Story3", width_mm=300, depth_mm=600, span_mm=6000, mu_knm=193.7, vu_kn=124.8, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B3_S3", story="Story3", width_mm=300, depth_mm=600, span_mm=5500, mu_knm=160.8, vu_kn=111.4, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B4_S3", story="Story3", width_mm=300, depth_mm=600, span_mm=5500, mu_knm=166.2, vu_kn=114.9, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B5_S3", story="Story3", width_mm=300, depth_mm=600, span_mm=7000, mu_knm=254.8, vu_kn=143.2, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B6_S3", story="Story3", width_mm=300, depth_mm=450, span_mm=4000, mu_knm=75.6, vu_kn=61.8, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B7_S3", story="Story3", width_mm=300, depth_mm=450, span_mm=4000, mu_knm=80.2, vu_kn=65.3, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B8_S3", story="Story3", width_mm=300, depth_mm=750, span_mm=8000, mu_knm=351.6, vu_kn=176.4, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B9_S3", story="Story3", width_mm=300, depth_mm=750, span_mm=8000, mu_knm=360.2, vu_kn=182.5, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B10_S3", story="Story3", width_mm=250, depth_mm=500, span_mm=5000, mu_knm=129.4, vu_kn=100.1, fck_mpa=25, fy_mpa=500, cover_mm=40),
        # Story 2
        BeamRow(id="B1_S2", story="Story2", width_mm=300, depth_mm=600, span_mm=6000, mu_knm=213.2, vu_kn=137.4, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B2_S2", story="Story2", width_mm=300, depth_mm=600, span_mm=6000, mu_knm=203.1, vu_kn=130.2, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B3_S2", story="Story2", width_mm=300, depth_mm=600, span_mm=5500, mu_knm=168.7, vu_kn=116.2, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B4_S2", story="Story2", width_mm=300, depth_mm=600, span_mm=5500, mu_knm=174.3, vu_kn=119.8, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B5_S2", story="Story2", width_mm=300, depth_mm=600, span_mm=7000, mu_knm=267.4, vu_kn=148.6, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B6_S2", story="Story2", width_mm=300, depth_mm=450, span_mm=4000, mu_knm=79.4, vu_kn=64.6, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B7_S2", story="Story2", width_mm=300, depth_mm=450, span_mm=4000, mu_knm=84.1, vu_kn=68.2, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B8_S2", story="Story2", width_mm=300, depth_mm=750, span_mm=8000, mu_knm=371.8, vu_kn=185.3, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B9_S2", story="Story2", width_mm=300, depth_mm=750, span_mm=8000, mu_knm=380.6, vu_kn=191.4, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B10_S2", story="Story2", width_mm=250, depth_mm=500, span_mm=5000, mu_knm=136.2, vu_kn=104.8, fck_mpa=25, fy_mpa=500, cover_mm=40),
        # Story 1 (ground floor - higher loads)
        BeamRow(id="B1_S1", story="Story1", width_mm=300, depth_mm=600, span_mm=6000, mu_knm=221.4, vu_kn=142.3, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B2_S1", story="Story1", width_mm=300, depth_mm=600, span_mm=6000, mu_knm=210.8, vu_kn=134.7, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B3_S1", story="Story1", width_mm=300, depth_mm=600, span_mm=5500, mu_knm=175.3, vu_kn=120.5, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B4_S1", story="Story1", width_mm=300, depth_mm=600, span_mm=5500, mu_knm=181.2, vu_kn=123.9, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B5_S1", story="Story1", width_mm=300, depth_mm=600, span_mm=7000, mu_knm=278.6, vu_kn=153.4, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B6_S1", story="Story1", width_mm=300, depth_mm=450, span_mm=4000, mu_knm=82.6, vu_kn=66.8, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B7_S1", story="Story1", width_mm=300, depth_mm=450, span_mm=4000, mu_knm=87.4, vu_kn=70.5, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B8_S1", story="Story1", width_mm=300, depth_mm=750, span_mm=8000, mu_knm=389.2, vu_kn=192.8, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B9_S1", story="Story1", width_mm=300, depth_mm=750, span_mm=8000, mu_knm=398.4, vu_kn=199.1, fck_mpa=25, fy_mpa=500, cover_mm=40),
        BeamRow(id="B10_S1", story="Story1", width_mm=250, depth_mm=500, span_mm=5000, mu_knm=142.1, vu_kn=108.6, fck_mpa=25, fy_mpa=500, cover_mm=40),
    ]

    return CSVImportResponse(
        success=True,
        message=f"Loaded {len(sample_beams)} sample beams from 8-story building",
        beam_count=len(sample_beams),
        beams=sample_beams,
        format_detected="Sample",
        warnings=[],
    )
