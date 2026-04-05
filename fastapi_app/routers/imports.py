"""
CSV Import Router.

Endpoints for importing CSV files using structural_lib adapters.
USES EXISTING LIBRARY - GenericCSVAdapter, ETABSAdapter, SAFEAdapter, STAADAdapter
DO NOT DUPLICATE PARSING LOGIC!
"""

from __future__ import annotations

import csv
import logging
import math
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, Field

from fastapi_app.config import get_settings

router = APIRouter(
    prefix="/import",
    tags=["import"],
)

logger = logging.getLogger(__name__)


# =============================================================================
# Request/Response Models
# =============================================================================


class Point3D(BaseModel):
    """3D point for beam geometry."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


class BeamRow(BaseModel):
    """Individual beam data from CSV import."""

    id: str = Field(..., max_length=200, description="Beam identifier")
    story: str | None = Field(None, max_length=200, description="Story/floor level")
    width_mm: float = Field(..., description="Beam width in mm")
    depth_mm: float = Field(..., description="Beam overall depth in mm")
    span_mm: float = Field(5000.0, description="Span length in mm")
    mu_knm: float = Field(0.0, description="Design moment in kN·m")
    vu_kn: float = Field(0.0, description="Design shear in kN")
    fck_mpa: float = Field(25.0, description="Concrete strength in N/mm²")
    fy_mpa: float = Field(500.0, description="Steel strength in N/mm²")
    cover_mm: float = Field(40.0, description="Clear cover in mm")


class BeamWith3D(BeamRow):
    """Beam data with 3D positioning for visualization."""

    point1: Point3D = Field(default_factory=Point3D, description="Start point")
    point2: Point3D = Field(default_factory=Point3D, description="End point")


class SampleDataResponse(BaseModel):
    """Response from sample data endpoint with 3D geometry."""

    success: bool
    message: str
    beam_count: int
    beams: list[BeamWith3D]
    format_detected: str = "ETABS"
    warnings: list[str] = Field(default_factory=list)


class CSVImportResponse(BaseModel):
    """Response from CSV import endpoint."""

    success: bool
    message: str
    beam_count: int
    beams: list[BeamRow]
    format_detected: str = Field(
        ..., max_length=50, description="Detected format: ETABS, SAFE, STAAD, Generic"
    )
    warnings: list[str] = Field(default_factory=list)


class DualCSVImportResponse(BaseModel):
    """Response from dual CSV import endpoint."""

    success: bool
    message: str
    beam_count: int
    beams: list[BeamWith3D]
    format_detected: str = Field(
        ...,
        max_length=50,
        description="Detected format: ETABS, SAFE, STAAD, Generic, AUTO",
    )
    warnings: list[str] = Field(default_factory=list)
    unmatched_beams: list[str] = Field(default_factory=list)
    unmatched_forces: list[str] = Field(default_factory=list)


class BatchDesignResult(BaseModel):
    """Result for a single beam in batch design."""

    beam_id: str
    success: bool
    ast_required: float = 0.0
    asc_required: float = 0.0
    stirrup_spacing: float = 0.0
    is_safe: bool = False
    utilization_ratio: float = 0.0  # Mu / Mu_cap (moment demand / moment capacity)
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
    format_hint: Literal["auto", "etabs", "safe", "staad", "generic"] = Query(
        "auto", description="Optional format override for CSV import"
    ),
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
        settings = get_settings()
        max_size = settings.max_upload_size_bytes

        # Fast-path: check declared size if available
        if file.size and file.size > max_size:
            logger.warning(
                "CSV upload rejected: declared size %d exceeds limit %d",
                file.size,
                max_size,
            )
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {max_size // (1024 * 1024)}MB",
            )

        # Read with size guard (handles spoofed content-length)
        content = await file.read(max_size + 1)
        if len(content) > max_size:
            logger.warning(
                "CSV upload rejected: actual size %d exceeds limit %d",
                len(content),
                max_size,
            )
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {max_size // (1024 * 1024)}MB",
            )

        text = content.decode("utf-8-sig")

        # Import adapters from library
        import os

        # Create temp file for adapter (adapters expect file paths)
        import tempfile

        from structural_lib.services.api import DesignDefaults
        from structural_lib.services.adapters import (
            ETABSAdapter,
            GenericCSVAdapter,
            SAFEAdapter,
            STAADAdapter,
        )

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

            detected_format = "Generic"

            adapter_order = [
                ("ETABS", adapters["etabs"]),
                ("SAFE", adapters["safe"]),
                ("STAAD", adapters["staad"]),
                ("Generic", adapters["generic"]),
            ]

            if format_hint == "auto":
                # Filter to adapters that claim to handle this file
                candidates = [
                    (name, adapter)
                    for name, adapter in adapter_order
                    if adapter.can_handle(tmp_path)
                ]
                if not candidates:
                    candidates = [("Generic", adapters["generic"])]
            else:
                adapter_obj = adapters.get(format_hint.lower())
                if adapter_obj:
                    candidates = [(format_hint.upper(), adapter_obj)]
                else:
                    candidates = [("Generic", adapters["generic"])]

            # Load data using adapter — try each candidate until one succeeds
            defaults = DesignDefaults()
            warnings: list[str] = []
            beams_out: list[BeamRow] = []
            last_error: str | None = None

            for adapter_name, adapter in candidates:
                detected_format = adapter_name
                beams_out = []
                adapter_warnings: list[str] = []

                try:
                    geometry_list = adapter.load_geometry(tmp_path, defaults)

                    # Try loading forces
                    try:
                        forces_list = adapter.load_forces(tmp_path)
                        forces_map = {f.id: f for f in forces_list}
                    except (ValueError, NotImplementedError):
                        forces_map = {}
                        adapter_warnings.append(
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
                                span_mm=geom.length_m * 1000,
                                mu_knm=forces.mu_knm if forces else 0.0,
                                vu_kn=forces.vu_kn if forces else 0.0,
                                fck_mpa=geom.section.fck_mpa,
                                fy_mpa=geom.section.fy_mpa,
                                cover_mm=geom.section.cover_mm,
                            )
                        )

                    if beams_out:
                        warnings = adapter_warnings
                        break  # Success — stop trying adapters

                except (ValueError, NotImplementedError, AttributeError) as e:
                    # Geometry loading failed — try forces only
                    last_error = str(e)
                    try:
                        forces_list = adapter.load_forces(tmp_path)
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
                        if beams_out:
                            adapter_warnings.append(
                                "Geometry loading encountered a non-critical issue"
                            )
                            logger.warning("Geometry loading note: %s", e)
                            warnings = adapter_warnings
                            break  # Success with forces only
                    except Exception as force_err:
                        last_error = f"{last_error}; forces: {force_err}"

                    # This adapter failed completely — try next one
                    continue

            if not beams_out:
                logger.warning(
                    "CSV import failed with all adapters. Last error: %s", last_error
                )
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Could not parse CSV with any adapter. Please check file format.",
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
    except Exception:
        logger.exception("CSV import failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Import failed: unable to process the uploaded CSV file",
        )


@router.post(
    "/dual-csv",
    response_model=DualCSVImportResponse,
    summary="Import Dual CSV Files",
    description="Import beam geometry + forces from separate CSV files.",
)
async def import_dual_csv(
    geometry_file: UploadFile = File(..., description="Geometry CSV file"),
    forces_file: UploadFile = File(..., description="Forces CSV file"),
    format_hint: Literal["auto", "etabs", "safe", "staad", "generic"] = Query(
        "auto", description="Optional format override for dual CSV import"
    ),
) -> DualCSVImportResponse:
    """
    Import beam data from two CSV files (geometry + forces).

    Uses structural_lib.imports.parse_dual_csv to build canonical models and
    merges them into BeamWith3D responses for React visualization.
    """
    if not geometry_file.filename or not geometry_file.filename.lower().endswith(
        ".csv"
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geometry file must be a CSV file",
        )
    if not forces_file.filename or not forces_file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Forces file must be a CSV file",
        )

    try:
        import tempfile

        from structural_lib.services.imports import parse_dual_csv, validate_import

        settings = get_settings()
        max_size = settings.max_upload_size_bytes

        # Validate geometry file size
        if geometry_file.size and geometry_file.size > max_size:
            logger.warning(
                "Geometry CSV rejected: declared size %d exceeds limit %d",
                geometry_file.size,
                max_size,
            )
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Geometry file too large. Maximum size: {max_size // (1024 * 1024)}MB",
            )
        # Validate forces file size
        if forces_file.size and forces_file.size > max_size:
            logger.warning(
                "Forces CSV rejected: declared size %d exceeds limit %d",
                forces_file.size,
                max_size,
            )
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Forces file too large. Maximum size: {max_size // (1024 * 1024)}MB",
            )

        geometry_path = None
        forces_path = None

        geometry_content = await geometry_file.read(max_size + 1)
        if len(geometry_content) > max_size:
            logger.warning(
                "Geometry CSV rejected: actual size %d exceeds limit %d",
                len(geometry_content),
                max_size,
            )
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Geometry file too large. Maximum size: {max_size // (1024 * 1024)}MB",
            )
        forces_content = await forces_file.read(max_size + 1)
        if len(forces_content) > max_size:
            logger.warning(
                "Forces CSV rejected: actual size %d exceeds limit %d",
                len(forces_content),
                max_size,
            )
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Forces file too large. Maximum size: {max_size // (1024 * 1024)}MB",
            )

        geometry_text = geometry_content.decode("utf-8-sig")
        forces_text = forces_content.decode("utf-8-sig")

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as geom_tmp:
            geom_tmp.write(geometry_text)
            geometry_path = geom_tmp.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as force_tmp:
            force_tmp.write(forces_text)
            forces_path = force_tmp.name

        try:
            try:
                batch, import_warnings = parse_dual_csv(
                    geometry_path,
                    forces_path,
                    format_hint=format_hint,
                )
            except Exception as exc:
                if format_hint != "generic":
                    batch, import_warnings = parse_dual_csv(
                        geometry_path,
                        forces_path,
                        format_hint="generic",
                    )
                else:
                    raise exc
            report = validate_import(batch)

            if not report.ok:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="; ".join(report.errors),
                )

            forces_by_id = {f.id: f for f in batch.forces}
            beams_out: list[BeamWith3D] = []

            for beam in batch.beams:
                forces = forces_by_id.get(beam.id)
                beams_out.append(
                    BeamWith3D(
                        id=beam.id,
                        story=beam.story,
                        width_mm=beam.section.width_mm,
                        depth_mm=beam.section.depth_mm,
                        span_mm=beam.length_m * 1000.0,
                        mu_knm=forces.mu_knm if forces else 0.0,
                        vu_kn=forces.vu_kn if forces else 0.0,
                        fck_mpa=beam.section.fck_mpa,
                        fy_mpa=beam.section.fy_mpa,
                        cover_mm=beam.section.cover_mm,
                        point1=Point3D(
                            x=beam.point1.x,
                            y=beam.point1.y,
                            z=beam.point1.z,
                        ),
                        point2=Point3D(
                            x=beam.point2.x,
                            y=beam.point2.y,
                            z=beam.point2.z,
                        ),
                    )
                )

            merged_warnings = list(
                dict.fromkeys(report.warnings + import_warnings.warnings)
            )

            detected = (
                format_hint.upper() if format_hint and format_hint != "auto" else "AUTO"
            )

            return DualCSVImportResponse(
                success=True,
                message=f"Imported {len(beams_out)} beams from dual CSV files",
                beam_count=len(beams_out),
                beams=beams_out,
                format_detected=detected,
                warnings=merged_warnings,
                unmatched_beams=import_warnings.unmatched_beams,
                unmatched_forces=import_warnings.unmatched_forces,
            )
        finally:
            import os

            if geometry_path:
                os.unlink(geometry_path)
            if forces_path:
                os.unlink(forces_path)

    except HTTPException:
        raise
    except Exception:
        logger.exception("Dual CSV import failed")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not parse dual CSV files",
        )


@router.post(
    "/csv/text",
    response_model=CSVImportResponse,
    summary="Import CSV Text",
    description="Import beam data from CSV text content.",
)
async def import_csv_text(
    csv_text: str,
    format_hint: Literal["auto", "etabs", "safe", "staad", "generic"] = Query(
        "auto", description="Optional format override for CSV text import"
    ),
) -> CSVImportResponse:
    """
    Import beam data from CSV text content.

    Same as /import/csv but accepts raw text instead of file upload.
    Useful for frontend paste operations.
    """
    import os
    import tempfile

    settings = get_settings()
    max_size = settings.max_upload_size_bytes
    if len(csv_text.encode("utf-8")) > max_size:
        logger.warning(
            "CSV text rejected: size %d exceeds limit %d",
            len(csv_text.encode("utf-8")),
            max_size,
        )
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"CSV text too large. Maximum size: {max_size // (1024 * 1024)}MB",
        )

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
            size = None  # Unknown size; import_csv checks `if file.size`

            async def read(self, size: int = -1) -> bytes:
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
    from fastapi_app.config import get_settings

    settings = get_settings()
    if len(beams) > settings.max_batch_size:
        raise HTTPException(
            status_code=422,
            detail=f"Batch size {len(beams)} exceeds maximum of {settings.max_batch_size}. Send at most {settings.max_batch_size} beams per request.",
        )

    try:
        from structural_lib.services.api import design_beam_is456

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

                mu_cap = (
                    result.flexure.Mu_lim
                    if result.flexure.Mu_lim and result.flexure.Mu_lim > 0
                    else None
                )
                utilization_ratio = min(beam.mu_knm / mu_cap, 2.0) if mu_cap else 1.0

                results.append(
                    BatchDesignResult(
                        beam_id=beam.id,
                        success=True,
                        ast_required=result.flexure.Ast_required,
                        asc_required=result.flexure.Asc_required,
                        stirrup_spacing=result.shear.spacing if result.shear else 0.0,
                        is_safe=is_safe,
                        utilization_ratio=utilization_ratio,
                    )
                )

                if is_safe:
                    passed += 1
                else:
                    failed += 1

            except (ValueError, TypeError):
                logger.exception("Invalid input for beam %s", beam.id)
                results.append(
                    BatchDesignResult(
                        beam_id=beam.id,
                        success=False,
                        error="Invalid input parameters",
                    )
                )
                failed += 1
            except Exception:
                logger.exception("Batch design failed for beam %s", beam.id)
                results.append(
                    BatchDesignResult(
                        beam_id=beam.id,
                        success=False,
                        error="Internal calculation error",
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

    except ImportError:
        logger.exception("structural_lib not available for batch design")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="structural_lib not available",
        )
    except Exception:
        logger.exception("Batch design failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch design failed",
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
    response_model=SampleDataResponse,
    summary="Get Sample Data with 3D Geometry",
    description="Load 154 real beams from ETABS export with 3D positions for visualization.",
)
async def get_sample_data() -> SampleDataResponse:
    """
    Load sample building data from actual ETABS export CSV files.

    Loads and merges:
    - beam_forces.csv (154 beams with Mu, Vu, dimensions)
    - frames_geometry.csv (3D positions Point1X/Y/Z, Point2X/Y/Z)

    This provides real structural engineering data with 3D positions for:
    - Demo and testing purposes
    - 3D visualization of building frame
    - Understanding expected data format
    """
    # Path to sample CSV files — try multiple locations
    base_path = Path(__file__).parent.parent.parent
    candidate_dirs = [
        base_path / "VBA" / "ETABS_Export_v2" / "Etabs_output" / "2026-01-17_222801",
        base_path / "Etabs_CSV",
    ]

    forces_path = None
    geometry_path = None
    for sample_dir in candidate_dirs:
        fp = sample_dir / "beam_forces.csv"
        gp = sample_dir / "frames_geometry.csv"
        if fp.exists() and gp.exists():
            forces_path = fp
            geometry_path = gp
            break

    warnings_list: list[str] = []

    if not forces_path or not geometry_path:
        searched = ", ".join(str(d) for d in candidate_dirs)
        logger.warning("Sample files not found. Searched: %s", searched)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample files not found",
        )

    # Read forces CSV
    forces_data: dict[str, dict[str, str | float]] = {}
    try:
        with open(forces_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                unique_name = row.get("UniqueName", "")
                if unique_name:
                    forces_data[unique_name] = {
                        "label": row.get("Label", ""),
                        "story": row.get("Story", ""),
                        "width_mm": float(row.get("Width_mm", 300)),
                        "depth_mm": float(row.get("Depth_mm", 500)),
                        "span_m": float(row.get("Span_m", 5.0)),
                        "mu_max": abs(float(row.get("Mu_max_kNm", 0))),
                        "mu_min": abs(float(row.get("Mu_min_kNm", 0))),
                        "vu_max": abs(float(row.get("Vu_max_kN", 0))),
                    }
    except Exception as e:
        logger.warning("Error reading forces CSV: %s", e)
        warnings_list.append("Error reading forces data")

    # Read geometry CSV (filter beams only)
    geometry_data: dict[str, dict[str, float]] = {}
    try:
        with open(geometry_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("FrameType") == "Beam":
                    unique_name = row.get("UniqueName", "")
                    if unique_name:
                        geometry_data[unique_name] = {
                            "point1_x": float(row.get("Point1X", 0)),
                            "point1_y": float(row.get("Point1Y", 0)),
                            "point1_z": float(row.get("Point1Z", 0)),
                            "point2_x": float(row.get("Point2X", 0)),
                            "point2_y": float(row.get("Point2Y", 0)),
                            "point2_z": float(row.get("Point2Z", 0)),
                        }
    except Exception as e:
        logger.warning("Error reading geometry CSV: %s", e)
        warnings_list.append("Error reading geometry data")

    # Merge forces with geometry
    sample_beams: list[BeamWith3D] = []
    for unique_name, force in forces_data.items():
        geom = geometry_data.get(unique_name, {})

        # Calculate span from geometry if available
        if geom:
            p1_x, p1_y = geom.get("point1_x", 0), geom.get("point1_y", 0)
            p2_x, p2_y = geom.get("point2_x", 0), geom.get("point2_y", 0)
            span_from_geom = math.sqrt((p2_x - p1_x) ** 2 + (p2_y - p1_y) ** 2)
            span_mm = span_from_geom * 1000  # m to mm
        else:
            span_mm = force["span_m"] * 1000

        # Use max of Mu_max and abs(Mu_min) for design moment
        mu_design = max(force["mu_max"], force["mu_min"])

        beam = BeamWith3D(
            id=f"{force['label']}_{force['story']}",
            story=str(force["story"]),
            width_mm=force["width_mm"],
            depth_mm=force["depth_mm"],
            span_mm=span_mm,
            mu_knm=mu_design,
            vu_kn=force["vu_max"],
            fck_mpa=25.0,
            fy_mpa=500.0,
            cover_mm=40.0,
            point1=Point3D(
                x=geom.get("point1_x", 0),
                y=geom.get("point1_y", 0),
                z=geom.get("point1_z", 0),
            ),
            point2=Point3D(
                x=geom.get("point2_x", 0),
                y=geom.get("point2_y", 0),
                z=geom.get("point2_z", 0),
            ),
        )
        sample_beams.append(beam)

    return SampleDataResponse(
        success=True,
        message=f"Loaded {len(sample_beams)} beams with 3D positions from ETABS export",
        beam_count=len(sample_beams),
        beams=sample_beams,
        format_detected="ETABS",
        warnings=warnings_list,
    )
