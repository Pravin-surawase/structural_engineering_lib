"""
CSV Import Router.

Endpoints for importing CSV files using structural_lib adapters.
USES EXISTING LIBRARY - GenericCSVAdapter, ETABSAdapter, SAFEAdapter, STAADAdapter
DO NOT DUPLICATE PARSING LOGIC!
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import math
from pathlib import Path
from typing import Any, Literal

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from fastapi_app.config import get_settings
from fastapi_app.models.beam import EvidenceEnvelopeResponse
from fastapi_app.models.metadata import ImportFormatsResponse
from fastapi_app.models.response import APIResponse, error_response, success_response

router = APIRouter(
    prefix="/import",
    tags=["import"],
)

logger = logging.getLogger(__name__)


def _required_sample_text(
    row: dict[str, str | None],
    field: str,
    *,
    artifact: str,
    row_number: int,
) -> str:
    """Return one required bundled-sample value without silent fallback."""

    value = row.get(field)
    if value is None or not value.strip():
        raise ValueError(f"{artifact} row {row_number}: missing {field}")
    return value.strip()


def _required_sample_float(
    row: dict[str, str | None],
    field: str,
    *,
    artifact: str,
    row_number: int,
) -> float:
    """Parse one required finite bundled-sample number."""

    value = float(
        _required_sample_text(
            row,
            field,
            artifact=artifact,
            row_number=row_number,
        )
    )
    if not math.isfinite(value):
        raise ValueError(f"{artifact} row {row_number}: non-finite {field}")
    return value


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
    source_id: str | None = Field(
        None,
        max_length=200,
        description="Stable source-system identity, such as ETABS UniqueName; import responses always populate it",
    )
    story: str | None = Field(None, max_length=200, description="Story/floor level")
    width_mm: float = Field(..., description="Beam width in mm")
    depth_mm: float = Field(..., description="Beam overall depth in mm")
    span_mm: float = Field(..., description="Span length in mm")
    mu_knm: float = Field(..., description="Design moment in kN·m")
    vu_kn: float = Field(..., description="Design shear in kN")
    fck_mpa: float = Field(..., description="Concrete strength in N/mm²")
    fy_mpa: float = Field(..., description="Steel strength in N/mm²")
    cover_mm: float = Field(..., description="Clear cover in mm")
    source_metadata: dict[str, Any] | None = None


class BeamWith3D(BeamRow):
    """Beam data with 3D positioning for visualization."""

    point1: Point3D = Field(default_factory=Point3D, description="Start point")
    point2: Point3D = Field(default_factory=Point3D, description="End point")


class SampleDatasetEvidence(BaseModel):
    """Stable identity for the exact bundled source files."""

    dataset_id: str
    dataset_version: str
    dataset_sha256: str
    hash_algorithm: str
    source_files: list[str]
    beam_count: int


class SampleDataResponse(BaseModel):
    """Response from sample data endpoint with 3D geometry."""

    success: bool
    message: str
    beam_count: int
    beams: list[BeamWith3D]
    format_detected: str = "ETABS"
    warnings: list[str] = Field(default_factory=list)
    dataset: SampleDatasetEvidence


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
    normalization_ledger: dict[str, Any]
    issues: list[dict[str, Any]] = Field(default_factory=list)


def _lossless_import_response(
    *,
    import_result: Any,
    stirrup_diameter_mm: float,
    tension_bar_diameter_mm: float,
) -> APIResponse[CSVImportResponse]:
    """Map one accepted lossless import into the public preview model."""

    if import_result.batch is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "schema_version": import_result.schema_version,
                "status": import_result.status.value,
                "issues": [
                    issue.model_dump(mode="json") for issue in import_result.issues
                ],
                "normalization_ledger": import_result.ledger.model_dump(mode="json"),
            },
        )
    ledger_payload = import_result.ledger.model_dump(mode="json")
    ledger_hash = hashlib.sha256(
        json.dumps(
            ledger_payload,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    detected = (
        import_result.ledger.adapter_selection.selected_format or "BLOCKED"
    ).upper()
    forces_by_id = {force.id: force for force in import_result.batch.forces}
    beams = [
        BeamRow(
            id=beam.id,
            source_id=beam.source_id or beam.id,
            story=beam.story,
            width_mm=beam.section.width_mm,
            depth_mm=beam.section.depth_mm,
            span_mm=beam.length_m * 1000.0,
            mu_knm=forces_by_id[beam.id].mu_knm,
            vu_kn=forces_by_id[beam.id].vu_kn,
            fck_mpa=beam.section.fck_mpa,
            fy_mpa=beam.section.fy_mpa,
            cover_mm=beam.section.cover_mm,
            source_metadata={
                "source_record_identity": beam.source_id or beam.id,
                "artifact_sha256": import_result.ledger.geometry_artifact.sha256,
                "normalization_ledger_hash": ledger_hash,
                "adapter": detected,
                "effective_depth_basis": {
                    "clear_cover_mm": beam.section.cover_mm,
                    "stirrup_diameter_mm": stirrup_diameter_mm,
                    "tension_bar_diameter_mm": tension_bar_diameter_mm,
                },
            },
        )
        for beam in import_result.batch.beams
    ]
    return success_response(
        CSVImportResponse(
            success=True,
            message=f"Imported {len(beams)} beams using {detected} adapter",
            beam_count=len(beams),
            beams=beams,
            format_detected=detected,
            warnings=[],
            normalization_ledger=ledger_payload,
            issues=[],
        )
    )


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
    normalization_ledger: dict[str, Any]
    issues: list[dict[str, Any]] = Field(default_factory=list)


class BatchDesignResult(BaseModel):
    """Result for a single beam in batch design."""

    beam_id: str
    success: bool
    ast_required: float = 0.0
    asc_required: float = 0.0
    stirrup_spacing: float = 0.0
    is_safe: bool = False
    # Governing IS 456 compliance utilization. Doubly reinforced flexure is
    # reported as 1.0 when the designed reinforcement is valid because the
    # current FlexureResult does not expose its final reinforced capacity.
    utilization_ratio: float = 0.0
    error: str | None = None
    evidence: EvidenceEnvelopeResponse | None = None


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
    response_model=APIResponse[CSVImportResponse],
    summary="Import CSV File",
    description="Import beam data from CSV using structural_lib adapters.",
)
async def import_csv(
    file: UploadFile = File(..., description="CSV file to import"),
    fck_mpa: float = Form(..., gt=0),
    fy_mpa: float = Form(..., gt=0),
    cover_mm: float = Form(..., gt=0),
    stirrup_diameter_mm: int = Form(..., gt=0),
    tension_bar_diameter_mm: float = Form(..., gt=0),
    format_hint: Literal["auto", "etabs", "safe", "staad", "generic"] = Query(
        "auto", description="Optional format override for CSV import"
    ),
):
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

        import os
        import tempfile

        from structural_lib.services.imports import (
            build_import_design_defaults,
            parse_single_csv_lossless,
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as strict_tmp:
            strict_tmp.write(text)
            strict_path = strict_tmp.name
        try:
            import_result = parse_single_csv_lossless(
                strict_path,
                format_hint=format_hint,
                defaults=build_import_design_defaults(
                    fck_mpa=fck_mpa,
                    fy_mpa=fy_mpa,
                    cover_mm=cover_mm,
                    stirrup_dia_mm=stirrup_diameter_mm,
                ),
                artifact_name=file.filename,
            )
            return _lossless_import_response(
                import_result=import_result,
                stirrup_diameter_mm=stirrup_diameter_mm,
                tension_bar_diameter_mm=tension_bar_diameter_mm,
            )
        finally:
            os.unlink(strict_path)

    except HTTPException:
        raise
    except (IOError, ValueError, KeyError, csv.Error):
        logger.exception("CSV import failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )


@router.post(
    "/dual-csv",
    response_model=APIResponse[DualCSVImportResponse],
    summary="Import Dual CSV Files",
    description="Import beam geometry + forces from separate CSV files.",
)
async def import_dual_csv(
    geometry_file: UploadFile = File(..., description="Geometry CSV file"),
    forces_file: UploadFile = File(..., description="Forces CSV file"),
    fck_mpa: float = Form(..., gt=0),
    fy_mpa: float = Form(..., gt=0),
    cover_mm: float = Form(..., gt=0),
    stirrup_diameter_mm: int = Form(..., gt=0),
    tension_bar_diameter_mm: float = Form(..., gt=0),
    format_hint: Literal["auto", "etabs", "safe", "staad", "generic"] = Query(
        "auto", description="Optional format override for dual CSV import"
    ),
):
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

        from structural_lib.services.imports import (
            build_import_design_defaults,
            parse_dual_csv_lossless,
        )

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
            import_result = parse_dual_csv_lossless(
                geometry_path,
                forces_path,
                format_hint=format_hint,
                defaults=build_import_design_defaults(
                    fck_mpa=fck_mpa,
                    fy_mpa=fy_mpa,
                    cover_mm=cover_mm,
                    stirrup_dia_mm=stirrup_diameter_mm,
                ),
                geometry_artifact_name=geometry_file.filename,
                forces_artifact_name=forces_file.filename,
            )
            if import_result.batch is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "schema_version": import_result.schema_version,
                        "status": import_result.status.value,
                        "issues": [
                            issue.model_dump(mode="json")
                            for issue in import_result.issues
                        ],
                        "normalization_ledger": import_result.ledger.model_dump(
                            mode="json"
                        ),
                    },
                )
            batch = import_result.batch
            ledger_payload = import_result.ledger.model_dump(mode="json")
            normalization_ledger_hash = hashlib.sha256(
                json.dumps(
                    ledger_payload,
                    allow_nan=False,
                    separators=(",", ":"),
                    sort_keys=True,
                ).encode("utf-8")
            ).hexdigest()
            detected = (
                import_result.ledger.adapter_selection.selected_format or "BLOCKED"
            ).upper()

            forces_by_id = {f.id: f for f in batch.forces}
            beams_out: list[BeamWith3D] = []

            for beam in batch.beams:
                forces = forces_by_id[beam.id]
                beams_out.append(
                    BeamWith3D(
                        id=beam.id,
                        source_id=beam.source_id or beam.id,
                        story=beam.story,
                        width_mm=beam.section.width_mm,
                        depth_mm=beam.section.depth_mm,
                        span_mm=beam.length_m * 1000.0,
                        mu_knm=forces.mu_knm,
                        vu_kn=forces.vu_kn,
                        fck_mpa=beam.section.fck_mpa,
                        fy_mpa=beam.section.fy_mpa,
                        cover_mm=beam.section.cover_mm,
                        source_metadata={
                            "source_record_identity": beam.source_id or beam.id,
                            "geometry_artifact_sha256": (
                                import_result.ledger.geometry_artifact.sha256
                            ),
                            "forces_artifact_sha256": (
                                import_result.ledger.forces_artifact.sha256
                            ),
                            "normalization_ledger_hash": normalization_ledger_hash,
                            "adapter": detected,
                            "effective_depth_basis": {
                                "clear_cover_mm": beam.section.cover_mm,
                                "stirrup_diameter_mm": stirrup_diameter_mm,
                                "tension_bar_diameter_mm": (tension_bar_diameter_mm),
                            },
                        },
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

            return success_response(
                DualCSVImportResponse(
                    success=True,
                    message=f"Imported {len(beams_out)} beams from dual CSV files",
                    beam_count=len(beams_out),
                    beams=beams_out,
                    format_detected=detected,
                    warnings=[],
                    unmatched_beams=[],
                    unmatched_forces=[],
                    normalization_ledger=ledger_payload,
                    issues=[],
                )
            )
        finally:
            import os

            if geometry_path:
                os.unlink(geometry_path)
            if forces_path:
                os.unlink(forces_path)

    except HTTPException:
        raise
    except (IOError, ValueError, KeyError, csv.Error):
        logger.exception("Dual CSV import failed")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response("Could not parse dual CSV files"),
        )


@router.post(
    "/csv/text",
    response_model=APIResponse[CSVImportResponse],
    summary="Import CSV Text",
    description="Import beam data from CSV text content.",
    deprecated=True,
)
async def import_csv_text(
    csv_text: str,
    fck_mpa: float = Query(..., gt=0),
    fy_mpa: float = Query(..., gt=0),
    cover_mm: float = Query(..., gt=0),
    stirrup_diameter_mm: int = Query(..., gt=0),
    tension_bar_diameter_mm: float = Query(..., gt=0),
    format_hint: Literal["auto", "etabs", "safe", "staad", "generic"] = Query(
        "auto", description="Optional format override for CSV text import"
    ),
):
    """
    Import beam data from CSV text content.

    Same as /import/csv but accepts raw text instead of file upload.
    Useful for frontend paste operations.
    """
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

    class MockUploadFile:
        filename = "data.csv"
        size = None

        async def read(self, size: int = -1):
            return csv_text.encode("utf-8")

    return await import_csv(  # type: ignore[arg-type]
        MockUploadFile(),
        fck_mpa,
        fy_mpa,
        cover_mm,
        stirrup_diameter_mm,
        tension_bar_diameter_mm,
        format_hint,
    )


@router.post(
    "/project-beams",
    response_model=APIResponse[dict[str, Any]],
    summary="Design Canonical Project Beams",
    description="Validate and design canonical project-beam/v1 payloads.",
)
async def design_project_beams(
    beams: list[dict[str, Any]],
) -> APIResponse[dict[str, Any]]:
    """Delegate canonical transport input to the strict service command."""

    settings = get_settings()
    if len(beams) > settings.max_batch_size:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Batch size {len(beams)} exceeds maximum of "
                f"{settings.max_batch_size}"
            ),
        )
    from structural_lib.services.batch import design_project_beams_v1

    return success_response(design_project_beams_v1(beams).to_dict())


@router.post(
    "/batch-design",
    response_model=APIResponse[dict[str, Any]],
    summary="Compatibility Batch Design",
    description="Deprecated compatibility transport delegating to the strict service.",
    deprecated=True,
)
async def batch_design(
    beams: list[dict[str, Any]],
    response: Response,
) -> APIResponse[dict[str, Any]]:
    """Preserve known aliases without route-level defaults or derivation."""

    response.headers["Deprecation"] = "true"
    response.headers["Warning"] = (
        '299 - "Deprecated compatibility route; use POST /import/project-beams"'
    )
    settings = get_settings()
    if len(beams) > settings.max_batch_size:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Batch size {len(beams)} exceeds maximum of "
                f"{settings.max_batch_size}"
            ),
        )
    from structural_lib.services.batch import design_beams

    return success_response(design_beams(beams))


@router.get(
    "/formats",
    response_model=APIResponse[ImportFormatsResponse],
    response_model_exclude_unset=True,
    summary="Get Supported Formats",
    description="Get list of supported CSV import formats.",
)
async def get_supported_formats():
    """Get information about supported CSV formats."""
    return success_response(
        {
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
    )


@router.get(
    "/sample",
    response_model=APIResponse[SampleDataResponse],
    summary="Get Sample Data with 3D Geometry",
    description="Load the bundled ETABS sample building with 3D positions for visualization.",
)
async def get_sample_data():
    """
    Load sample building data from actual ETABS export CSV files.

    Loads and merges:
    - beam_forces.csv (beam forces and dimensions)
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

    dataset_hash = hashlib.sha256()
    for source_path in (forces_path, geometry_path):
        dataset_hash.update(source_path.name.encode("utf-8"))
        dataset_hash.update(b"\0")
        dataset_hash.update(source_path.read_bytes())
        dataset_hash.update(b"\0")

    dataset_sha256 = dataset_hash.hexdigest()

    # Read forces CSV. Bundled acceptance data is a controlled fixture: a
    # malformed or incomplete row invalidates the complete sample rather than
    # receiving a structural fallback.
    forces_data: dict[str, dict[str, str | float]] = {}
    try:
        with open(forces_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_number, row in enumerate(reader, start=2):
                unique_name = _required_sample_text(
                    row,
                    "UniqueName",
                    artifact=forces_path.name,
                    row_number=row_number,
                )
                if unique_name in forces_data:
                    raise ValueError(
                        f"{forces_path.name} row {row_number}: duplicate UniqueName {unique_name}"
                    )
                forces_data[unique_name] = {
                    "label": _required_sample_text(
                        row,
                        "Label",
                        artifact=forces_path.name,
                        row_number=row_number,
                    ),
                    "story": _required_sample_text(
                        row,
                        "Story",
                        artifact=forces_path.name,
                        row_number=row_number,
                    ),
                    "width_mm": _required_sample_float(
                        row,
                        "Width_mm",
                        artifact=forces_path.name,
                        row_number=row_number,
                    ),
                    "depth_mm": _required_sample_float(
                        row,
                        "Depth_mm",
                        artifact=forces_path.name,
                        row_number=row_number,
                    ),
                    "span_m": _required_sample_float(
                        row,
                        "Span_m",
                        artifact=forces_path.name,
                        row_number=row_number,
                    ),
                    "mu_max": abs(
                        _required_sample_float(
                            row,
                            "Mu_max_kNm",
                            artifact=forces_path.name,
                            row_number=row_number,
                        )
                    ),
                    "mu_min": abs(
                        _required_sample_float(
                            row,
                            "Mu_min_kNm",
                            artifact=forces_path.name,
                            row_number=row_number,
                        )
                    ),
                    "vu_max": abs(
                        _required_sample_float(
                            row,
                            "Vu_max_kN",
                            artifact=forces_path.name,
                            row_number=row_number,
                        )
                    ),
                }
    except (IOError, ValueError, KeyError, csv.Error) as e:
        logger.error("Bundled sample forces are invalid: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bundled sample forces failed integrity validation",
        ) from e

    # Read geometry CSV (filter beams only)
    geometry_data: dict[str, dict[str, float]] = {}
    try:
        with open(geometry_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_number, row in enumerate(reader, start=2):
                if row.get("FrameType") == "Beam":
                    unique_name = _required_sample_text(
                        row,
                        "UniqueName",
                        artifact=geometry_path.name,
                        row_number=row_number,
                    )
                    if unique_name in geometry_data:
                        raise ValueError(
                            f"{geometry_path.name} row {row_number}: duplicate UniqueName {unique_name}"
                        )
                    geometry_data[unique_name] = {
                        field.lower(): _required_sample_float(
                            row,
                            csv_field,
                            artifact=geometry_path.name,
                            row_number=row_number,
                        )
                        for field, csv_field in (
                            ("point1_x", "Point1X"),
                            ("point1_y", "Point1Y"),
                            ("point1_z", "Point1Z"),
                            ("point2_x", "Point2X"),
                            ("point2_y", "Point2Y"),
                            ("point2_z", "Point2Z"),
                        )
                    }
    except (IOError, ValueError, KeyError, csv.Error) as e:
        logger.error("Bundled sample geometry is invalid: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bundled sample geometry failed integrity validation",
        ) from e

    if set(forces_data) != set(geometry_data):
        logger.error("Bundled sample force/geometry identities do not match")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bundled sample force/geometry identities do not match",
        )

    # Merge forces with geometry
    sample_beams: list[BeamWith3D] = []
    for unique_name, force in forces_data.items():
        geom = geometry_data[unique_name]

        # Calculate span from the required matched geometry.
        p1_x, p1_y = geom["point1_x"], geom["point1_y"]
        p2_x, p2_y = geom["point2_x"], geom["point2_y"]
        span_from_geom = math.sqrt((p2_x - p1_x) ** 2 + (p2_y - p1_y) ** 2)
        span_mm = round(span_from_geom * 1000, 3)  # m to mm

        # Use max of Mu_max and abs(Mu_min) for design moment
        mu_design = max(force["mu_max"], force["mu_min"])

        beam = BeamWith3D(
            id=f"{force['label']}_{force['story']}",
            source_id=unique_name,
            story=str(force["story"]),
            width_mm=force["width_mm"],
            depth_mm=force["depth_mm"],
            span_mm=span_mm,
            mu_knm=mu_design,
            vu_kn=force["vu_max"],
            fck_mpa=25.0,
            fy_mpa=500.0,
            cover_mm=40.0,
            source_metadata={
                "dataset_id": "bundled-etabs-beam-sample",
                "dataset_version": "etabs-csv-v1",
                "dataset_sha256": dataset_sha256,
                "source_record_identity": unique_name,
                "sample_only": True,
                "calculation_basis_origins": {
                    "fck_mpa": "assumed_sample",
                    "fy_mpa": "assumed_sample",
                    "cover_mm": "assumed_sample",
                },
                "qualified_review_required": True,
            },
            point1=Point3D(
                x=geom["point1_x"],
                y=geom["point1_y"],
                z=geom["point1_z"],
            ),
            point2=Point3D(
                x=geom["point2_x"],
                y=geom["point2_y"],
                z=geom["point2_z"],
            ),
        )
        sample_beams.append(beam)

    return success_response(
        SampleDataResponse(
            success=True,
            message=f"Loaded {len(sample_beams)} beams with 3D positions from ETABS export",
            beam_count=len(sample_beams),
            beams=sample_beams,
            format_detected="ETABS",
            warnings=warnings_list,
            dataset=SampleDatasetEvidence(
                dataset_id="bundled-etabs-beam-sample",
                dataset_version="etabs-csv-v1",
                dataset_sha256=dataset_sha256,
                hash_algorithm="sha256-framed-files-v1",
                source_files=[forces_path.name, geometry_path.name],
                beam_count=len(sample_beams),
            ),
        )
    )
