# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       api
Description:  Public facing API functions
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from structural_lib.codes.is456 import (
    compliance,
    detailing,
    ductile,
    serviceability,
    slenderness,
)
from structural_lib.codes.is456.beam.shear import enhanced_shear_strength
from structural_lib.codes.is456.beam.torsion import (
    TorsionResult,
    calculate_equivalent_moment,
    calculate_equivalent_shear,
    calculate_longitudinal_torsion_steel,
    calculate_torsion_shear_stress,
    calculate_torsion_stirrup_area,
    design_torsion,
)
from structural_lib.codes.is456.column.axial import (
    classify_column,
    effective_length,
    min_eccentricity,
    short_axial_capacity,
)
from structural_lib.codes.is456.column.biaxial import biaxial_bending_check
from structural_lib.codes.is456.column.uniaxial import (
    design_short_column_uniaxial,
    pm_interaction_curve,
)
from structural_lib.codes.is456.load_analysis import compute_bmd_sfd
from structural_lib.core.data_types import (
    ComplianceCaseResult,
    ComplianceReport,
    CrackWidthParams,
    CriticalPoint,
    DeflectionParams,
    EndCondition,
    LoadDefinition,
    LoadDiagramResult,
    LoadType,
    ValidationReport,
)
from structural_lib.core.inputs import (
    BeamGeometryInput,
    BeamInput,
    DetailingConfigInput,
    LoadCaseInput,
    LoadsInput,
    MaterialsInput,
)
from structural_lib.core.models import BeamGeometry, DesignDefaults, FrameType
from structural_lib.insights import cost_optimization, design_suggestions
from structural_lib.services import bbs, job_runner, report
from structural_lib.services.calculation_report import (
    CalculationReport,
    InputSection,
    ProjectInfo,
    ResultSection,
    generate_calculation_report,
)
from structural_lib.visualization.geometry_3d import (
    Beam3DGeometry,
    Point3D,
    RebarPath,
    RebarSegment,
    StirrupLoop,
    beam_to_3d_geometry,
    compute_beam_outline,
    compute_rebar_positions,
    compute_stirrup_path,
    compute_stirrup_positions,
)

from . import beam_pipeline
from .api_results import (
    CostBreakdown,
    CostOptimizationResult,
    DesignAndDetailResult,
    DesignSuggestionsResult,
    OptimalDesign,
    SmartAnalysisResult,
)
from .audit import (
    AuditLogEntry,
    AuditTrail,
    CalculationHash,
    compute_hash,
    create_calculation_certificate,
    verify_calculation,
)
from .costing import CostProfile
from .etabs_import import (
    ETABSEnvelopeResult,
    ETABSForceRow,
    create_job_from_etabs,
    create_jobs_from_etabs_csv,
    load_etabs_csv,
    normalize_etabs_forces,
    validate_etabs_csv,
)

__all__ = [
    # Version
    "get_library_version",
    # Validation
    "validate_job_spec",
    "validate_design_results",
    # Core design functions
    "design_beam_is456",
    "check_beam_is456",
    "detail_beam_is456",
    "design_and_detail_beam_is456",
    # Input dataclasses (TASK-276)
    "BeamInput",
    "BeamGeometryInput",
    "MaterialsInput",
    "LoadsInput",
    "LoadCaseInput",
    "DetailingConfigInput",
    "design_from_input",
    # Audit & Verification (TASK-278)
    "AuditTrail",
    "AuditLogEntry",
    "CalculationHash",
    "compute_hash",
    "create_calculation_certificate",
    "verify_calculation",
    # Calculation Report (TASK-277)
    "CalculationReport",
    "ProjectInfo",
    "InputSection",
    "ResultSection",
    "generate_calculation_report",
    # Outputs
    "compute_detailing",
    "compute_bbs",
    "export_bbs",
    "compute_dxf",
    "compute_report",
    "compute_critical",
    # Serviceability
    "check_beam_ductility",
    "check_beam_slenderness",
    "check_deflection_span_depth",
    "check_crack_width",
    "check_compliance_report",
    # Column Design (IS 456 Clause 39)
    "calculate_effective_length_is456",
    "calculate_additional_moment_is456",
    "classify_column_is456",
    "min_eccentricity_is456",
    "design_column_axial_is456",
    "design_short_column_uniaxial_is456",
    "pm_interaction_curve_is456",
    "biaxial_bending_check_is456",
    "design_long_column_is456",
    "check_helical_reinforcement_is456",
    "design_column_is456",
    # Shear (IS 456 Clause 40)
    "enhanced_shear_strength_is456",
    # Smart features
    "optimize_beam_cost",
    "suggest_beam_design_improvements",
    "smart_analyze_design",
    # Torsion Design (IS 456 Clause 41)
    "design_torsion",
    "calculate_equivalent_shear",
    "calculate_equivalent_moment",
    "calculate_torsion_shear_stress",
    "calculate_torsion_stirrup_area",
    "calculate_longitudinal_torsion_steel",
    "TorsionResult",
    # ETABS Integration (CSV Import)
    "validate_etabs_csv",
    "load_etabs_csv",
    "normalize_etabs_forces",
    "create_job_from_etabs",
    "create_jobs_from_etabs_csv",
    "ETABSForceRow",
    "ETABSEnvelopeResult",
    # Load Analysis (BMD/SFD) (TASK-145)
    "compute_bmd_sfd",
    "LoadType",
    "LoadDefinition",
    "CriticalPoint",
    "LoadDiagramResult",
    # 3D Visualization (TASK-3D-03)
    "Point3D",
    "BeamGeometry",
    "FrameType",
    "DesignDefaults",
    "RebarSegment",
    "RebarPath",
    "StirrupLoop",
    "Beam3DGeometry",
    "compute_rebar_positions",
    "compute_stirrup_path",
    "compute_stirrup_positions",
    "compute_beam_outline",
    "beam_to_3d_geometry",
]


def _require_is456_units(units: str) -> None:
    beam_pipeline.validate_units(units)


def _validate_plausibility(
    *,
    fck_nmm2: float | None = None,
    fy_nmm2: float | None = None,
    b_mm: float | None = None,
    d_mm: float | None = None,
    D_mm: float | None = None,
) -> None:
    """Catch common unit-confusion mistakes at the API boundary.

    Guards are deliberately generous (e.g. fck ≤ 120 allows UHPC).
    The goal is to catch Pa-vs-MPa and μm-vs-mm mistakes, not to
    enforce IS 456 material limits.
    """
    if fck_nmm2 is not None and fck_nmm2 > 120:
        raise ValueError(
            f"fck_nmm2={fck_nmm2} seems too large. "
            "Expected N/mm² (e.g., 25), not Pa or kPa."
        )
    if fy_nmm2 is not None and fy_nmm2 > 700:
        raise ValueError(
            f"fy_nmm2={fy_nmm2} seems too large. "
            "Expected N/mm² (e.g., 415), not Pa or kPa."
        )
    if b_mm is not None and b_mm > 5000:
        raise ValueError(
            f"b_mm={b_mm} seems too large. " "Expected mm (e.g., 300), not μm or m."
        )
    if d_mm is not None and d_mm > 5000:
        raise ValueError(
            f"d_mm={d_mm} seems too large. " "Expected mm (e.g., 450), not μm or m."
        )
    if D_mm is not None and D_mm > 5000:
        raise ValueError(
            f"D_mm={D_mm} seems too large. " "Expected mm (e.g., 500), not μm or m."
        )


def get_library_version() -> str:
    """Return the installed package version.

    Returns:
        Package version string. Falls back to a default when package metadata
        is unavailable (e.g., running from a source checkout).
    """
    try:
        return version("structural-lib-is456")
    except PackageNotFoundError:
        pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text(encoding="utf-8")
            for line in content.splitlines():
                if line.strip().startswith("version"):
                    return line.split("=", 1)[1].strip().strip('"')
        return "0.0.0-dev"


def validate_job_spec(path: str | Path) -> ValidationReport:
    """Validate a job.json specification file.

    Returns a ValidationReport with errors/warnings and summary details.
    """
    try:
        spec = job_runner.load_job_spec(path)
    except Exception as exc:
        return ValidationReport(ok=False, errors=[str(exc)])

    details = {
        "schema_version": spec.get("schema_version"),
        "job_id": spec.get("job_id"),
        "code": spec.get("code"),
        "units": spec.get("units"),
        "beam_keys": sorted(spec.get("beam", {}).keys()),
        "cases_count": len(spec.get("cases", [])),
    }
    return ValidationReport(ok=True, details=details)


def _beam_has_geometry(beam: dict[str, Any]) -> bool:
    geom = beam.get("geometry")
    if isinstance(geom, dict):
        if all(k in geom for k in ("b_mm", "D_mm", "d_mm")):
            return True
        if all(k in geom for k in ("b", "D", "d")):
            return True
    return all(k in beam for k in ("b", "D", "d"))


def _beam_has_materials(beam: dict[str, Any]) -> bool:
    mats = beam.get("materials")
    if isinstance(mats, dict):
        return any(k in mats for k in ("fck_nmm2", "fck")) and any(
            k in mats for k in ("fy_nmm2", "fy")
        )
    return any(k in beam for k in ("fck_nmm2", "fck")) and any(
        k in beam for k in ("fy_nmm2", "fy")
    )


def _beam_has_loads(beam: dict[str, Any]) -> bool:
    loads = beam.get("loads")
    if isinstance(loads, dict):
        return any(k in loads for k in ("mu_knm", "Mu")) and any(
            k in loads for k in ("vu_kn", "Vu")
        )
    return any(k in beam for k in ("mu_knm", "Mu")) and any(
        k in beam for k in ("vu_kn", "Vu")
    )


def validate_design_results(path: str | Path) -> ValidationReport:
    """Validate a design results JSON file (single or multi-beam)."""
    errors: list[str] = []
    warnings: list[str] = []

    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc:
        return ValidationReport(ok=False, errors=[str(exc)])

    if not isinstance(data, dict):
        return ValidationReport(
            ok=False, errors=["Results file must be a JSON object."]
        )

    schema_version = data.get("schema_version")
    if schema_version is None:
        errors.append("Missing required field 'schema_version'.")
    else:
        try:
            schema_version_int = int(schema_version)
            if schema_version_int != beam_pipeline.SCHEMA_VERSION:
                errors.append(
                    f"Unsupported schema_version: {schema_version_int} "
                    f"(expected {beam_pipeline.SCHEMA_VERSION})."
                )
        except (ValueError, TypeError):
            errors.append(f"Invalid schema_version: {schema_version!r}.")

    code = data.get("code")
    if not code:
        errors.append("Missing required field 'code'.")

    units = data.get("units")
    if not units:
        warnings.append("Missing 'units' field (recommended for stable outputs).")

    beams = data.get("beams")
    if not isinstance(beams, list) or not beams:
        errors.append("Missing or empty 'beams' list.")
        beams = []

    for idx, beam in enumerate(beams):
        if not isinstance(beam, dict):
            errors.append(f"Beam {idx}: expected object, got {type(beam).__name__}.")
            continue
        if not beam.get("beam_id"):
            errors.append(f"Beam {idx}: missing 'beam_id'.")
        if not beam.get("story"):
            errors.append(f"Beam {idx}: missing 'story'.")
        if not _beam_has_geometry(beam):
            errors.append(f"Beam {idx}: missing geometry fields.")
        if not _beam_has_materials(beam):
            errors.append(f"Beam {idx}: missing material fields.")
        if not _beam_has_loads(beam):
            errors.append(f"Beam {idx}: missing load fields.")

    details = {
        "schema_version": schema_version,
        "code": code,
        "units": units,
        "beams_count": len(beams),
    }

    return ValidationReport(
        ok=not errors, errors=errors, warnings=warnings, details=details
    )


def _extract_beam_params_from_schema(beam: dict[str, Any]) -> dict[str, Any]:
    """
    Extract beam parameters from either old or new schema format.

    Supports:
    - New schema (v1 canonical): geometry.b_mm, materials.fck_nmm2, etc.
    - Old schema: geometry.b, materials.fck, etc.

    Returns normalized dict with short keys (b, D, d, fck, fy, etc.)
    """
    geom = beam.get("geometry") or {}
    mat = beam.get("materials") or {}
    flex = beam.get("flexure") or {}
    det = beam.get("detailing") or {}  # Guard against explicit null

    b = geom.get("b_mm") or geom.get("b", 300)
    D = geom.get("D_mm") or geom.get("D", 500)
    d = geom.get("d_mm") or geom.get("d", 450)
    span = geom.get("span_mm") or geom.get("span", 4000)
    cover = geom.get("cover_mm") or geom.get("cover", 40)

    fck = mat.get("fck_nmm2") or mat.get("fck", 25)
    fy = mat.get("fy_nmm2") or mat.get("fy", 500)

    ast = flex.get("ast_required_mm2") or flex.get("ast_req", 0)
    asc = flex.get("asc_required_mm2") or flex.get("asc_req", 0)

    ld_tension = None
    lap_length = None
    if det:
        ld_tension = det.get("ld_tension_mm") or det.get("ld_tension")
        lap_length = det.get("lap_length_mm") or det.get("lap_length")

    return {
        "beam_id": beam.get("beam_id", "BEAM"),
        "story": beam.get("story", "STORY"),
        "b": float(b),
        "D": float(D),
        "d": float(d),
        "span": float(span),
        "cover": float(cover),
        "fck": float(fck),
        "fy": float(fy),
        "ast": float(ast),
        "asc": float(asc),
        "detailing": det,
        "ld_tension": ld_tension,
        "lap_length": lap_length,
    }


def _detailing_result_to_dict(
    result: detailing.BeamDetailingResult,
) -> dict[str, Any]:
    zones = ("start", "mid", "end")

    def _bars_to_dict(bars: list[detailing.BarArrangement]) -> list[dict[str, Any]]:
        output = []
        for idx, arr in enumerate(bars):
            zone = zones[idx] if idx < len(zones) else f"zone_{idx}"
            output.append(
                {
                    "zone": zone,
                    "count": arr.count,
                    "diameter_mm": arr.diameter,
                    "area_provided_mm2": arr.area_provided,
                    "spacing_mm": arr.spacing,
                    "layers": arr.layers,
                    "callout": arr.callout(),
                }
            )
        return output

    def _stirrups_to_dict(
        stirrups: list[detailing.StirrupArrangement],
    ) -> list[dict[str, Any]]:
        output = []
        for idx, arr in enumerate(stirrups):
            zone = zones[idx] if idx < len(zones) else f"zone_{idx}"
            output.append(
                {
                    "zone": zone,
                    "diameter_mm": arr.diameter,
                    "legs": arr.legs,
                    "spacing_mm": arr.spacing,
                    "zone_length_mm": arr.zone_length,
                    "callout": arr.callout(),
                }
            )
        return output

    return {
        "beam_id": result.beam_id,
        "story": result.story,
        "geometry": {
            "b_mm": result.b,
            "D_mm": result.D,
            "span_mm": result.span,
            "cover_mm": result.cover,
        },
        "top_bars": _bars_to_dict(result.top_bars),
        "bottom_bars": _bars_to_dict(result.bottom_bars),
        "stirrups": _stirrups_to_dict(result.stirrups),
        "ld_tension_mm": result.ld_tension,
        "ld_compression_mm": result.ld_compression,
        "lap_length_mm": result.lap_length,
        "is_valid": result.is_valid,
        "remarks": result.remarks,
    }


def compute_detailing(
    design_results: dict[str, Any],
    *,
    config: dict[str, Any] | None = None,
) -> list[detailing.BeamDetailingResult]:
    """Compute beam detailing results from design results JSON dict.

    Extracts beam geometry, materials, and reinforcement from design results
    and generates detailed bar schedules, stirrup layouts, and construction notes.

    Args:
        design_results: Design results dictionary with 'beams' key containing
            list of beam designs. Must include geometry (b, D, span, cover),
            materials (fck, fy), and reinforcement (ast, asc).
        config: Optional configuration dictionary with keys:
            - stirrup_dia_mm (float): Stirrup diameter in mm (default: 8)
            - stirrup_spacing_start_mm (float): Spacing at ends (default: 150)
            - stirrup_spacing_mid_mm (float): Spacing at midspan (default: 200)
            - stirrup_spacing_end_mm (float): Spacing at ends (default: 150)
            - is_seismic (bool): Seismic detailing requirements (default: False)

    Returns:
        List of BeamDetailingResult objects containing:
            - bar_schedule: List of rebar items (mark, diameter, length, count)
            - stirrup_layout: Stirrup arrangement (zones, spacing, diameter)
            - construction_notes: Detailing notes per IS 456:2000

    Raises:
        TypeError: If design_results is not a dict
        ValueError: If no beams found in design_results
        ValueError: If units in design_results are not IS 456 standard (mm, N/mm², kN, kN·m)

    References:
        IS 456:2000, Cl. 26 (Detailing)

    Examples:
        >>> results = {"beams": [{"beam_id": "B1", "geometry": {...}, ...}]}
        >>> detailing_list = compute_detailing(results)
        >>> print(f"Generated {len(detailing_list)} beam details")
        Generated 1 beam details
    """
    if not isinstance(design_results, dict):
        raise TypeError("design_results must be a dict")

    units = design_results.get("units")
    if units:
        _require_is456_units(units)

    beams = design_results.get("beams", [])
    if not isinstance(beams, list) or not beams:
        raise ValueError("No beams found in design results.")

    cfg = config or {}
    spacing_default = cfg.get("stirrup_spacing_mm")

    detailing_list: list[detailing.BeamDetailingResult] = []

    for beam in beams:
        params = _extract_beam_params_from_schema(beam)
        det = params["detailing"] or {}

        stirrups = det.get("stirrups") if isinstance(det, dict) else []

        stirrup_dia = cfg.get("stirrup_dia_mm")
        if stirrup_dia is None and isinstance(stirrups, list) and stirrups:
            stirrup_dia = stirrups[0].get("diameter") or stirrups[0].get("diameter_mm")
        if stirrup_dia is None:
            stirrup_dia = 8.0

        spacing_start = cfg.get("stirrup_spacing_start_mm", spacing_default)
        spacing_mid = cfg.get("stirrup_spacing_mid_mm", spacing_default)
        spacing_end = cfg.get("stirrup_spacing_end_mm", spacing_default)

        if isinstance(stirrups, list) and stirrups:
            if spacing_start is None:
                spacing_start = stirrups[0].get("spacing")
            if spacing_mid is None and len(stirrups) > 1:
                spacing_mid = stirrups[1].get("spacing")
            if spacing_end is None and len(stirrups) > 2:
                spacing_end = stirrups[2].get("spacing")

        if spacing_start is None:
            spacing_start = 150.0
        if spacing_mid is None:
            spacing_mid = 200.0
        if spacing_end is None:
            spacing_end = 150.0

        detailing_result = detailing.create_beam_detailing(
            beam_id=params["beam_id"],
            story=params["story"],
            b=params["b"],
            D=params["D"],
            span=params["span"],
            cover=params["cover"],
            fck=params["fck"],
            fy=params["fy"],
            ast_start=params["ast"],
            ast_mid=params["ast"],
            ast_end=params["ast"],
            asc_start=params["asc"],
            asc_mid=params["asc"],
            asc_end=params["asc"],
            stirrup_dia=float(stirrup_dia),
            stirrup_spacing_start=float(spacing_start),
            stirrup_spacing_mid=float(spacing_mid),
            stirrup_spacing_end=float(spacing_end),
            is_seismic=bool(cfg.get("is_seismic", False)),
        )

        detailing_list.append(detailing_result)

    return detailing_list


def compute_bbs(
    detailing_list: list[detailing.BeamDetailingResult],
    *,
    project_name: str = "Beam BBS",
) -> bbs.BBSDocument:
    """Generate a bar bending schedule (BBS) document from detailing results.

    Consolidates reinforcement from multiple beams into a structured BBS document
    with bar marks, shapes, dimensions, and quantities for steel fabrication.

    Args:
        detailing_list: List of BeamDetailingResult objects from compute_detailing()
        project_name: Project name for BBS document header (default: "Beam BBS")

    Returns:
        BBSDocument object containing:
            - items: List of BBS entries (mark, shape, dimensions, count, weight)
            - summary: Total steel weight by diameter
            - project_name: Project identifier

    References:
        IS 2502:1963 (Code of practice for bending and fixing of bars for RCC)

    Examples:
        >>> detailing_list = compute_detailing(design_results)
        >>> bbs_doc = compute_bbs(detailing_list, project_name="Tower A")
        >>> print(f"Total steel: {bbs_doc.summary.total_weight_kg:.1f} kg")
        Total steel: 1234.5 kg
    """
    return bbs.generate_bbs_document(detailing_list, project_name=project_name)


def export_bbs(
    bbs_doc: bbs.BBSDocument,
    path: str | Path,
    *,
    fmt: str = "csv",
) -> Path:
    """Export a BBS document to CSV or JSON."""
    output_path = Path(path)
    fmt_lower = fmt.lower()

    if output_path.suffix.lower() == ".json" or fmt_lower == "json":
        bbs.export_bbs_to_json(bbs_doc, str(output_path))
    else:
        bbs.export_bbs_to_csv(bbs_doc.items, str(output_path))

    return output_path


def compute_dxf(
    detailing_list: list[detailing.BeamDetailingResult],
    output: str | Path,
    *,
    multi: bool = False,
    include_title_block: bool = False,
    title_block: dict[str, Any] | None = None,
    sheet_margin_mm: float = 20.0,
    title_block_width_mm: float = 120.0,
    title_block_height_mm: float = 40.0,
) -> Path:
    """Generate DXF CAD drawings from detailing results.

    Creates AutoCAD-compatible DXF files with beam elevations, cross-sections,
    reinforcement layouts, and dimensional annotations. Requires ezdxf package.

    Args:
        detailing_list: List of BeamDetailingResult objects from compute_detailing()
        output: Output DXF file path
        multi: If True, generate multi-beam layout on single sheet.
            Auto-enabled if len(detailing_list) > 1 (default: False)
        include_title_block: If True, add title block to drawing (default: False)
        title_block: Optional title block data dictionary with keys:
            - project_name (str): Project name
            - drawing_number (str): Drawing identifier
            - drawn_by (str): Designer name
            - date (str): Drawing date
        sheet_margin_mm: Sheet margin width in mm (default: 20.0)
        title_block_width_mm: Title block width in mm (default: 120.0)
        title_block_height_mm: Title block height in mm (default: 40.0)

    Returns:
        Path to generated DXF file

    Raises:
        RuntimeError: If ezdxf library not installed (install with: pip install "structural-lib-is456[dxf]")
        ValueError: If detailing_list is empty

    Examples:
        >>> detailing_list = compute_detailing(design_results)
        >>> dxf_path = compute_dxf(
        ...     detailing_list,
        ...     "output/beams.dxf",
        ...     include_title_block=True,
        ...     title_block={"project_name": "Tower A", "drawn_by": "John"}
        ... )
        >>> print(f"DXF generated: {dxf_path}")
        DXF generated: output/beams.dxf
    """
    from structural_lib import dxf_export as _dxf_export

    if _dxf_export is None:
        raise RuntimeError(
            "DXF export module not available. Install with: "
            'pip install "structural-lib-is456[dxf]"'
        )
    if not _dxf_export.EZDXF_AVAILABLE:
        raise RuntimeError(
            "ezdxf library not installed. Install with: "
            'pip install "structural-lib-is456[dxf]"'
        )
    if not detailing_list:
        raise ValueError("Detailing list is empty.")

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    use_multi = multi or len(detailing_list) > 1
    if use_multi:
        _dxf_export.generate_multi_beam_dxf(
            detailing_list,
            str(output_path),
            include_title_block=include_title_block,
            title_block=title_block,
            sheet_margin_mm=sheet_margin_mm,
            title_block_width_mm=title_block_width_mm,
            title_block_height_mm=title_block_height_mm,
        )
    else:
        _dxf_export.generate_beam_dxf(
            detailing_list[0],
            str(output_path),
            include_title_block=include_title_block,
            title_block=title_block,
            sheet_margin_mm=sheet_margin_mm,
            title_block_width_mm=title_block_width_mm,
            title_block_height_mm=title_block_height_mm,
        )

    return output_path


def compute_report(
    source: str | Path | dict[str, Any],
    *,
    format: str = "html",
    job_path: str | Path | None = None,
    results_path: str | Path | None = None,
    output_path: str | Path | None = None,
    batch_threshold: int = 80,
) -> str | Path | list[Path]:
    """Generate design report from job outputs or design results.

    Creates HTML or JSON reports with design calculations, code checks, reinforcement
    details, and compliance summaries. Supports single-beam and batch reporting.

    Args:
        source: Input source - one of:
            - dict: Design results dictionary (from design_beam_is456())
            - str/Path: Path to design results JSON file
            - str/Path: Path to folder with job.json and results/ (for batch jobs)
        format: Output format - "html" or "json" (default: "html")
        job_path: Optional job specification path (for folder source)
        results_path: Optional results folder path (for folder source)
        output_path: Output file/folder path. If None, returns string (HTML/JSON).
            For batch reports (>= batch_threshold beams), creates folder package.
        batch_threshold: Number of beams threshold for batch report mode (default: 80)

    Returns:
        - str: HTML or JSON string if output_path is None
        - Path: Output file path if output_path provided (single report)
        - list[Path]: List of output paths if batch report with multiple files

    Raises:
        ValueError: If format not in {"html", "json"}
        ValueError: If design results missing 'beams' key
        ValueError: If batch report (>= batch_threshold) requested without output_path

    Examples:
        >>> # Generate HTML report from dict
        >>> results = design_beam_is456(b_mm=300, D_mm=450, ...)
        >>> html = compute_report(results, format="html")

        >>> # Save batch HTML report to folder
        >>> report_path = compute_report(
        ...     "results/design_results.json",
        ...     format="html",
        ...     output_path="reports/batch_001"
        ... )
        >>> print(f"Report saved to: {report_path}")
        Report saved to: reports/batch_001/index.html
    """
    fmt = format.lower()
    if fmt not in {"html", "json"}:
        raise ValueError("Unknown format. Use format='html' or format='json'.")

    if isinstance(source, dict):
        design_results = source
        if "beams" not in design_results:
            raise ValueError("Design results must include a 'beams' array.")

        if fmt == "json":
            output = report.export_design_json(design_results)
            if output_path:
                path = Path(output_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(output, encoding="utf-8")
                return path
            return output

        beams = design_results.get("beams", [])
        if not output_path:
            if len(beams) >= batch_threshold:
                raise ValueError(
                    "Batch report requires output path for folder packaging."
                )
            return report.render_design_report_single(
                design_results, batch_threshold=batch_threshold
            )

        path = Path(output_path)
        return report.write_design_report_package(
            design_results,
            output_path=path,
            batch_threshold=batch_threshold,
        )

    source_path = Path(source)
    if source_path.is_file():
        design_results = report.load_design_results(source_path)

        if fmt == "json":
            output = report.export_design_json(design_results)
            if output_path:
                path = Path(output_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(output, encoding="utf-8")
                return path
            return output

        beams = design_results.get("beams", [])
        if not output_path:
            if len(beams) >= batch_threshold:
                raise ValueError(
                    "Batch report requires output path for folder packaging."
                )
            return report.render_design_report_single(
                design_results, batch_threshold=batch_threshold
            )

        path = Path(output_path)
        return report.write_design_report_package(
            design_results,
            output_path=path,
            batch_threshold=batch_threshold,
        )

    data = report.load_report_data(
        source_path,
        job_path=Path(job_path) if job_path else None,
        results_path=Path(results_path) if results_path else None,
    )

    output = report.export_json(data) if fmt == "json" else report.export_html(data)
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output, encoding="utf-8")
        return path
    return output


def compute_critical(
    job_out: str | Path,
    *,
    top: int = 10,
    format: str = "csv",
    job_path: str | Path | None = None,
    results_path: str | Path | None = None,
    output_path: str | Path | None = None,
) -> str | Path:
    """Generate critical set export from job outputs."""
    fmt = format.lower()
    if fmt not in {"csv", "html"}:
        raise ValueError("Unknown format. Use format='csv' or format='html'.")

    data = report.load_report_data(
        Path(job_out),
        job_path=Path(job_path) if job_path else None,
        results_path=Path(results_path) if results_path else None,
    )
    top_n = top if top and top > 0 else None
    critical_cases = report.get_critical_set(data, top=top_n)
    if not critical_cases:
        return ""

    output = (
        report.export_critical_csv(critical_cases)
        if fmt == "csv"
        else report.export_critical_html(critical_cases)
    )
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output, encoding="utf-8")
        return path
    return output


def check_beam_ductility(
    b: float, D: float, d: float, fck: float, fy: float, min_long_bar_dia: float
) -> ductile.DuctileBeamResult:
    """
    Run IS 13920 beam ductility checks for a single section.

    Args:
        b: Beam width (mm).
        D: Overall depth (mm).
        d: Effective depth (mm).
        fck: Concrete strength (N/mm²).
        fy: Steel yield strength (N/mm²).
        min_long_bar_dia: Minimum longitudinal bar diameter (mm).

    Returns:
        DuctileBeamResult with pass/fail flags and limiting values.
    """
    return ductile.check_beam_ductility(b, D, d, fck, fy, min_long_bar_dia)


def check_beam_slenderness(
    b_mm: float,
    d_mm: float,
    l_eff_mm: float,
    beam_type: str = "simply_supported",
    has_lateral_restraint: bool = False,
) -> slenderness.SlendernessResult:
    """Check beam slenderness for lateral stability per IS 456 Cl 23.3.

    This function checks whether a beam section satisfies the lateral
    stability requirements of IS 456:2000.

    Args:
        b_mm: Width of compression flange in mm (typically beam width).
        d_mm: Overall depth of beam in mm.
        l_eff_mm: Effective unsupported length in mm.
        beam_type: Type of beam ('simply_supported', 'continuous', 'cantilever').
        has_lateral_restraint: If True, beam is laterally restrained (slab on top).

    Returns:
        SlendernessResult with check status and details.

    Raises:
        ValueError: If inputs are invalid (non-positive dimensions).

    Example:
        >>> result = check_beam_slenderness(
        ...     b_mm=300,
        ...     d_mm=600,
        ...     l_eff_mm=8000,
        ...     beam_type="simply_supported"
        ... )
        >>> result.is_ok
        True

    References:
        IS 456:2000 Cl 23.3: Slenderness limits for beams
    """
    return slenderness.check_beam_slenderness(
        b_mm=b_mm,
        d_mm=d_mm,
        l_eff_mm=l_eff_mm,
        beam_type=beam_type,
        has_lateral_restraint=has_lateral_restraint,
    )


def check_anchorage_at_simple_support(
    bar_dia_mm: float,
    fck: float,
    fy: float,
    vu_kn: float,
    support_width_mm: float,
    cover_mm: float = 40.0,
    bar_type: str = "deformed",
    has_standard_bend: bool = True,
) -> detailing.AnchorageCheckResult:
    """Check anchorage of bottom bars at simple supports per IS 456 Cl 26.2.3.3.

    At simple supports, the positive moment tension reinforcement must have
    sufficient anchorage beyond the face of the support. This function checks
    whether the provided development length is adequate.

    The available anchorage length includes:
    - Standard 90° bend: provides 8 times bar diameter
    - Straight extension beyond support center
    - Support width contribution

    Args:
        bar_dia_mm: Bottom bar diameter in mm.
        fck: Concrete strength in N/mm².
        fy: Steel yield strength in N/mm².
        vu_kn: Factored shear force at support in kN.
        support_width_mm: Width of support in mm.
        cover_mm: Clear cover at support in mm (default 40mm).
        bar_type: "plain" or "deformed" (default "deformed").
        has_standard_bend: True if bar has 90° bend at support (default True).

    Returns:
        AnchorageCheckResult with check status and details.

    Example:
        >>> result = check_anchorage_at_simple_support(
        ...     bar_dia_mm=12,
        ...     fck=25,
        ...     fy=500,
        ...     vu_kn=50,
        ...     support_width_mm=300
        ... )
        >>> result.is_adequate
        True

    References:
        IS 456:2000 Cl 26.2.3.3: Anchorage of bars at simple supports
    """
    return detailing.check_anchorage_at_simple_support(
        bar_dia=bar_dia_mm,
        fck=fck,
        fy=fy,
        vu_kn=vu_kn,
        support_width=support_width_mm,
        cover=cover_mm,
        bar_type=bar_type,
        has_standard_bend=has_standard_bend,
    )


def check_deflection_span_depth(
    span_mm: float,
    d_mm: float,
    support_condition: str = "simply_supported",
    base_allowable_ld: float | None = None,
    mf_tension_steel: float | None = None,
    mf_compression_steel: float | None = None,
    mf_flanged: float | None = None,
) -> serviceability.DeflectionResult:
    """Check deflection using span/depth ratio (Level A).

    Args:
        span_mm: Clear span (mm).
        d_mm: Effective depth (mm).
        support_condition: Support condition string or enum.
        base_allowable_ld: Base L/d limit (optional).
        mf_tension_steel: Tension steel modification factor (optional).
        mf_compression_steel: Compression steel modification factor (optional).
        mf_flanged: Flanged beam modification factor (optional).

    Returns:
        DeflectionResult with computed L/d and allowable ratio.
    """

    return serviceability.check_deflection_span_depth(
        span_mm=span_mm,
        d_mm=d_mm,
        support_condition=support_condition,
        base_allowable_ld=base_allowable_ld,
        mf_tension_steel=mf_tension_steel,
        mf_compression_steel=mf_compression_steel,
        mf_flanged=mf_flanged,
    )


def check_crack_width(
    exposure_class: str = "moderate",
    limit_mm: float | None = None,
    acr_mm: float | None = None,
    cmin_mm: float | None = None,
    h_mm: float | None = None,
    x_mm: float | None = None,
    epsilon_m: float | None = None,
    fs_service_nmm2: float | None = None,
    es_nmm2: float = 200000.0,
) -> serviceability.CrackWidthResult:
    """Check crack width using an Annex-F-style estimate.

    Args:
        exposure_class: Exposure class string or enum.
        limit_mm: Crack width limit (mm), overrides defaults.
        acr_mm: Distance from point considered to nearest bar surface (mm).
        cmin_mm: Minimum cover to bar surface (mm).
        h_mm: Member depth (mm).
        x_mm: Neutral axis depth (mm).
        epsilon_m: Mean strain at reinforcement level.
        fs_service_nmm2: Steel stress at service (N/mm²).
        es_nmm2: Modulus of elasticity of steel (N/mm²).

    Returns:
        CrackWidthResult with computed width and pass/fail.
    """

    return serviceability.check_crack_width(
        exposure_class=exposure_class,
        limit_mm=limit_mm,
        acr_mm=acr_mm,
        cmin_mm=cmin_mm,
        h_mm=h_mm,
        x_mm=x_mm,
        epsilon_m=epsilon_m,
        fs_service_nmm2=fs_service_nmm2,
        es_nmm2=es_nmm2,
    )


def check_compliance_report(
    cases: Sequence[dict[str, Any]],
    b_mm: float,
    D_mm: float,
    d_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    d_dash_mm: float = 50.0,
    asv_mm2: float = 100.0,
    pt_percent: float | None = None,
    deflection_defaults: DeflectionParams | None = None,
    crack_width_defaults: CrackWidthParams | None = None,
) -> ComplianceReport:
    """Run a multi-case IS 456 compliance report.

    Args:
        cases: List of dicts with at least `case_id`, `mu_knm`, `vu_kn`.
        b_mm: Beam width (mm).
        D_mm: Overall depth (mm).
        d_mm: Effective depth (mm).
        fck_nmm2: Concrete strength (N/mm²).
        fy_nmm2: Steel yield strength (N/mm²).
        d_dash_mm: Compression steel depth from top (mm).
        asv_mm2: Area of stirrup legs (mm²).
        pt_percent: Percentage steel for shear table lookup (optional).
        deflection_defaults: Default deflection params (optional).
        crack_width_defaults: Default crack width params (optional).

    Returns:
        ComplianceReport with per-case results and governing case.
    """

    return compliance.check_compliance_report(
        cases=cases,
        b_mm=b_mm,
        D_mm=D_mm,
        d_mm=d_mm,
        fck_nmm2=fck_nmm2,
        fy_nmm2=fy_nmm2,
        d_dash_mm=d_dash_mm,
        asv_mm2=asv_mm2,
        pt_percent=pt_percent,
        deflection_defaults=deflection_defaults,
        crack_width_defaults=crack_width_defaults,
    )


def enhanced_shear_strength_is456(
    fck_nmm2: float,
    pt_percent: float,
    d_mm: float,
    av_mm: float,
) -> float:
    """Enhanced design shear strength for sections close to supports (IS 456 Cl 40.3).

    When a concentrated load is applied within 2d of the face of a support,
    the design shear strength τc may be enhanced to τc' = (2d/av) × τc,
    subject to τc' ≤ τc,max.

    NOTE: This enhancement applies ONLY to concentrated loads, NOT distributed loads.
    The caller is responsible for determining load type.

    Args:
        fck_nmm2: Characteristic concrete strength (N/mm²).
        pt_percent: Tension steel percentage (%).
        d_mm: Effective depth (mm). Must be > 0.
        av_mm: Distance from face of support to nearest edge of
            concentrated load (mm). Must be > 0.

    Returns:
        Enhanced shear strength τc' (N/mm²). If av ≥ 2d, returns base τc.

    Raises:
        DimensionError: If d_mm ≤ 0 or av_mm ≤ 0.

    References:
        IS 456:2000, Cl. 40.3

    Examples:
        >>> tau_c_enhanced = enhanced_shear_strength_is456(
        ...     fck_nmm2=25.0,
        ...     pt_percent=0.5,
        ...     d_mm=450.0,
        ...     av_mm=300.0
        ... )
        >>> print(f"Enhanced τc: {tau_c_enhanced:.3f} N/mm²")
        Enhanced τc: 0.880 N/mm²
    """
    # Unit plausibility guards (catch common mistakes)
    _validate_plausibility(fck_nmm2=fck_nmm2, d_mm=d_mm)

    return enhanced_shear_strength(
        fck=fck_nmm2,
        pt=pt_percent,
        d_mm=d_mm,
        av_mm=av_mm,
    )


def design_beam_is456(
    *,
    units: str,
    case_id: str = "CASE-1",
    mu_knm: float,
    vu_kn: float,
    b_mm: float,
    D_mm: float,
    d_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    d_dash_mm: float = 50.0,
    asv_mm2: float = 100.0,
    pt_percent: float | None = None,
    ast_mm2_for_shear: float | None = None,
    deflection_params: DeflectionParams | None = None,
    crack_width_params: CrackWidthParams | None = None,
) -> ComplianceCaseResult:
    """Design/check a single IS 456 beam case (strength + optional serviceability).

    This is a *public entrypoint* intended to stay stable even if internals evolve.

    Args:
        units: Units label (must be one of the IS456 aliases).
        case_id: Case identifier for reporting.
        mu_knm: Factored bending moment (kN·m).
        vu_kn: Factored shear (kN).
        b_mm: Beam width (mm).
        D_mm: Overall depth (mm).
        d_mm: Effective depth (mm).
        fck_nmm2: Concrete strength (N/mm²).
        fy_nmm2: Steel yield strength (N/mm²).
        d_dash_mm: Compression steel depth from top (mm).
        asv_mm2: Area of stirrup legs (mm²).
        pt_percent: Percentage steel for shear table lookup (optional).
        ast_mm2_for_shear: Use this Ast for shear table lookup (optional).
        deflection_params: Per-case deflection params (optional).
        crack_width_params: Per-case crack width params (optional).

    Returns:
        ComplianceCaseResult with flexure, shear, and optional serviceability checks.

    Raises:
        ValueError: If units is not one of the accepted IS456 aliases.

    Units (IS456):
    - Mu: kN·m (factored)
    - Vu: kN (factored)
    - b_mm, D_mm, d_mm, d_dash_mm: mm
    - fck_nmm2, fy_nmm2: N/mm² (MPa)

    Example:
        result = design_beam_is456(
            units="IS456",
            case_id="DL+LL",
            mu_knm=150,
            vu_kn=100,
            b_mm=300,
            D_mm=500,
            d_mm=450,
            fck_nmm2=25,
            fy_nmm2=500,
        )
    """

    _require_is456_units(units)

    # Unit plausibility guards (catch common mistakes)
    _validate_plausibility(
        fck_nmm2=fck_nmm2,
        fy_nmm2=fy_nmm2,
        b_mm=b_mm,
        d_mm=d_mm,
        D_mm=D_mm,
    )

    return compliance.check_compliance_case(
        case_id=case_id,
        mu_knm=mu_knm,
        vu_kn=vu_kn,
        b_mm=b_mm,
        D_mm=D_mm,
        d_mm=d_mm,
        fck_nmm2=fck_nmm2,
        fy_nmm2=fy_nmm2,
        d_dash_mm=d_dash_mm,
        asv_mm2=asv_mm2,
        pt_percent=pt_percent,
        ast_mm2_for_shear=ast_mm2_for_shear,
        deflection_params=deflection_params,
        crack_width_params=crack_width_params,
    )


def check_beam_is456(
    *,
    units: str,
    cases: Sequence[dict[str, Any]],
    b_mm: float,
    D_mm: float,
    d_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    d_dash_mm: float = 50.0,
    asv_mm2: float = 100.0,
    pt_percent: float | None = None,
    deflection_defaults: DeflectionParams | None = None,
    crack_width_defaults: CrackWidthParams | None = None,
) -> ComplianceReport:
    """Run an IS 456 compliance report across multiple cases.

    This is the stable multi-case entrypoint for IS456.

    Args:
        units: Units label (must be one of the IS456 aliases).
        cases: List of dicts with at least `case_id`, `mu_knm`, `vu_kn`.
        b_mm: Beam width (mm).
        D_mm: Overall depth (mm).
        d_mm: Effective depth (mm).
        fck_nmm2: Concrete strength (N/mm²).
        fy_nmm2: Steel yield strength (N/mm²).
        d_dash_mm: Compression steel depth from top (mm).
        asv_mm2: Area of stirrup legs (mm²).
        pt_percent: Percentage steel for shear table lookup (optional).
        deflection_defaults: Default deflection params (optional).
        crack_width_defaults: Default crack width params (optional).

    Returns:
        ComplianceReport with per-case results and governing case.

    Raises:
        ValueError: If units is not one of the accepted IS456 aliases.

    Example:
        cases = [
            {"case_id": "DL+LL", "mu_knm": 80, "vu_kn": 60},
            {"case_id": "1.5(DL+LL)", "mu_knm": 120, "vu_kn": 90},
        ]
        report = check_beam_is456(
            units="IS456",
            cases=cases,
            b_mm=300,
            D_mm=500,
            d_mm=450,
            fck_nmm2=25,
            fy_nmm2=500,
        )
    """

    _require_is456_units(units)

    # Unit plausibility guards (catch common mistakes)
    _validate_plausibility(
        fck_nmm2=fck_nmm2,
        fy_nmm2=fy_nmm2,
        b_mm=b_mm,
        d_mm=d_mm,
        D_mm=D_mm,
    )

    return compliance.check_compliance_report(
        cases=cases,
        b_mm=b_mm,
        D_mm=D_mm,
        d_mm=d_mm,
        fck_nmm2=fck_nmm2,
        fy_nmm2=fy_nmm2,
        d_dash_mm=d_dash_mm,
        asv_mm2=asv_mm2,
        pt_percent=pt_percent,
        deflection_defaults=deflection_defaults,
        crack_width_defaults=crack_width_defaults,
    )


def detail_beam_is456(
    *,
    units: str,
    beam_id: str,
    story: str,
    b_mm: float,
    D_mm: float,
    span_mm: float,
    cover_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    ast_start_mm2: float,
    ast_mid_mm2: float,
    ast_end_mm2: float,
    asc_start_mm2: float = 0.0,
    asc_mid_mm2: float = 0.0,
    asc_end_mm2: float = 0.0,
    stirrup_dia_mm: float = 8.0,
    stirrup_spacing_start_mm: float = 150.0,
    stirrup_spacing_mid_mm: float = 200.0,
    stirrup_spacing_end_mm: float = 150.0,
    is_seismic: bool = False,
) -> detailing.BeamDetailingResult:
    """Create IS456/SP34 detailing outputs from design Ast/Asc and stirrups.

    Args:
        units: Units label (must be one of the IS456 aliases).
        beam_id: Beam identifier.
        story: Story/level name.
        b_mm: Beam width (mm).
        D_mm: Overall depth (mm).
        span_mm: Beam span (mm).
        cover_mm: Clear cover (mm).
        fck_nmm2: Concrete strength (N/mm²).
        fy_nmm2: Steel yield strength (N/mm²).
        ast_start_mm2: Tension steel at start (mm²).
        ast_mid_mm2: Tension steel at midspan (mm²).
        ast_end_mm2: Tension steel at end (mm²).
        asc_start_mm2: Compression steel at start (mm²).
        asc_mid_mm2: Compression steel at midspan (mm²).
        asc_end_mm2: Compression steel at end (mm²).
        stirrup_dia_mm: Stirrup diameter (mm).
        stirrup_spacing_start_mm: Stirrup spacing at start (mm).
        stirrup_spacing_mid_mm: Stirrup spacing at midspan (mm).
        stirrup_spacing_end_mm: Stirrup spacing at end (mm).
        is_seismic: Apply IS 13920 detailing rules if True.

    Returns:
        BeamDetailingResult with bars, stirrups, and development lengths.
    """

    _require_is456_units(units)

    # Unit plausibility guards (catch common mistakes)
    _validate_plausibility(
        fck_nmm2=fck_nmm2,
        fy_nmm2=fy_nmm2,
        b_mm=b_mm,
        D_mm=D_mm,
    )

    return detailing.create_beam_detailing(
        beam_id=beam_id,
        story=story,
        b=b_mm,
        D=D_mm,
        span=span_mm,
        cover=cover_mm,
        fck=fck_nmm2,
        fy=fy_nmm2,
        ast_start=ast_start_mm2,
        ast_mid=ast_mid_mm2,
        ast_end=ast_end_mm2,
        asc_start=asc_start_mm2,
        asc_mid=asc_mid_mm2,
        asc_end=asc_end_mm2,
        stirrup_dia=stirrup_dia_mm,
        stirrup_spacing_start=stirrup_spacing_start_mm,
        stirrup_spacing_mid=stirrup_spacing_mid_mm,
        stirrup_spacing_end=stirrup_spacing_end_mm,
        is_seismic=is_seismic,
    )


def design_and_detail_beam_is456(
    *,
    units: str,
    beam_id: str,
    story: str,
    span_mm: float,
    mu_knm: float,
    vu_kn: float,
    b_mm: float,
    D_mm: float,
    d_mm: float | None = None,
    cover_mm: float = 40.0,
    fck_nmm2: float = 25.0,
    fy_nmm2: float = 500.0,
    d_dash_mm: float = 50.0,
    asv_mm2: float = 100.0,
    stirrup_dia_mm: float = 8.0,
    stirrup_spacing_support_mm: float = 150.0,
    stirrup_spacing_mid_mm: float = 200.0,
    is_seismic: bool = False,
) -> DesignAndDetailResult:
    """Design AND detail a beam in one call (IS 456:2000).

    This is a convenience function that combines design_beam_is456() and
    detail_beam_is456() into a single call. It:
    1. Designs the beam (flexure + shear checks per IS 456)
    2. Extracts required steel areas from design
    3. Creates detailing with bar arrangements per SP 34

    This eliminates the need to manually extract Ast from design and pass
    it to the detailing function - perfect for quick prototyping and
    Streamlit dashboards.

    Args:
        units: Units label (must be one of the IS456 aliases).
        beam_id: Beam identifier (e.g., "B1", "FB-101").
        story: Story/level name (e.g., "GF", "1F").
        span_mm: Beam span (mm).
        mu_knm: Factored bending moment (kN·m).
        vu_kn: Factored shear (kN).
        b_mm: Beam width (mm).
        D_mm: Overall depth (mm).
        d_mm: Effective depth (mm). If None, calculated as D_mm - cover_mm.
        cover_mm: Clear cover (mm). Default: 40mm.
        fck_nmm2: Concrete strength (N/mm²). Default: 25.
        fy_nmm2: Steel yield strength (N/mm²). Default: 500.
        d_dash_mm: Compression steel depth (mm). Default: 50.
        asv_mm2: Area of stirrup legs (mm²). Default: 100 (2x8mm).
        stirrup_dia_mm: Stirrup diameter (mm). Default: 8.
        stirrup_spacing_support_mm: Stirrup spacing at supports (mm). Default: 150.
        stirrup_spacing_mid_mm: Stirrup spacing at midspan (mm). Default: 200.
        is_seismic: Apply IS 13920 detailing if True. Default: False.

    Returns:
        DesignAndDetailResult with:
            - design: ComplianceCaseResult (flexure, shear, serviceability)
            - detailing: BeamDetailingResult (bars, stirrups, Ld, lap)
            - geometry: Dict of geometric properties
            - materials: Dict of material properties
            - is_ok: True if design is safe and detailing is valid
            - summary(): Human-readable summary

    Example:
        >>> result = design_and_detail_beam_is456(
        ...     units="IS456",
        ...     beam_id="B1",
        ...     story="GF",
        ...     span_mm=5000,
        ...     mu_knm=150,
        ...     vu_kn=80,
        ...     b_mm=300,
        ...     D_mm=500,
        ...     fck_nmm2=25,
        ...     fy_nmm2=500,
        ... )
        >>> print(result.summary())
        'B1@GF: 300×500mm, Ast=960mm², OK'
        >>> print(f"Tension steel: {result.design.flexure.ast_required:.0f} mm²")
        >>> print(f"Bottom bars: {result.detailing.bottom_bars}")

    See Also:
        - design_beam_is456(): Design-only (returns ComplianceCaseResult)
        - detail_beam_is456(): Detailing-only (requires Ast as input)
    """
    _require_is456_units(units)

    # Calculate effective depth if not provided
    if d_mm is None:
        d_mm = D_mm - cover_mm

    # Step 1: Design the beam
    design_result = design_beam_is456(
        units=units,
        case_id=f"{beam_id}@{story}",
        mu_knm=mu_knm,
        vu_kn=vu_kn,
        b_mm=b_mm,
        D_mm=D_mm,
        d_mm=d_mm,
        fck_nmm2=fck_nmm2,
        fy_nmm2=fy_nmm2,
        d_dash_mm=d_dash_mm,
        asv_mm2=asv_mm2,
    )

    # Step 2: Extract steel areas from design
    # For simplicity, use same Ast at all zones (conservative for gravity loads)
    ast_required = design_result.flexure.Ast_required
    asc_required = design_result.flexure.Asc_required

    # Step 3: Create detailing
    detail_result = detail_beam_is456(
        units=units,
        beam_id=beam_id,
        story=story,
        b_mm=b_mm,
        D_mm=D_mm,
        span_mm=span_mm,
        cover_mm=cover_mm,
        fck_nmm2=fck_nmm2,
        fy_nmm2=fy_nmm2,
        ast_start_mm2=ast_required,
        ast_mid_mm2=ast_required,
        ast_end_mm2=ast_required,
        asc_start_mm2=asc_required,
        asc_mid_mm2=asc_required,
        asc_end_mm2=asc_required,
        stirrup_dia_mm=stirrup_dia_mm,
        stirrup_spacing_start_mm=stirrup_spacing_support_mm,
        stirrup_spacing_mid_mm=stirrup_spacing_mid_mm,
        stirrup_spacing_end_mm=stirrup_spacing_support_mm,
        is_seismic=is_seismic,
    )

    # Combine results
    is_ok = design_result.is_ok and detail_result.is_valid
    remarks_parts = []
    if design_result.remarks:
        remarks_parts.append(design_result.remarks)
    if detail_result.remarks:
        remarks_parts.append(detail_result.remarks)

    return DesignAndDetailResult(
        beam_id=beam_id,
        story=story,
        design=design_result,
        detailing=detail_result,
        geometry={
            "b_mm": b_mm,
            "D_mm": D_mm,
            "d_mm": d_mm,
            "span_mm": span_mm,
            "cover_mm": cover_mm,
        },
        materials={
            "fck_nmm2": fck_nmm2,
            "fy_nmm2": fy_nmm2,
        },
        is_ok=is_ok,
        remarks="; ".join(remarks_parts) if remarks_parts else "",
    )


# ============================================================================
# Column Design Functions (IS 456:2000 Clause 39)
# ============================================================================


def calculate_effective_length_is456(
    l_mm: float,
    end_condition: str,
    use_theoretical: bool = False,
) -> dict[str, Any]:
    """Calculate effective length per IS 456 Cl 25.2, Table 28.

    Computes the effective length le = ratio × l for a column based on
    end restraint conditions. IS 456 Table 28 provides both theoretical
    (Euler) and recommended design values for seven standard cases.

    Args:
        l_mm: Unsupported length of column (mm). Must be between 100 and 50000 mm.
        end_condition: End condition string — one of:
            'FIXED_FIXED'      - Both ends fixed, no lateral translation
            'FIXED_HINGED'     - One end fixed, one hinged
            'FIXED_FIXED_SWAY' - Both ends fixed, lateral translation allowed
            'FIXED_FREE'       - One end fixed, one free (cantilever)
            'HINGED_HINGED'    - Both ends hinged
            'FIXED_PARTIAL'    - One fixed, partial restraint at other
            'HINGED_PARTIAL'   - One hinged, partial restraint at other
        use_theoretical: If True, use theoretical values (default: recommended).
            Note: Cases 6 and 7 have no theoretical values; recommended is used.

    Returns:
        dict with keys:
            - le_mm (float): Effective length (mm)
            - ratio (float): Effective length ratio (le/l)
            - end_condition (str): End condition used
            - method (str): 'theoretical' or 'recommended'

    Raises:
        ValueError: If l_mm is out of range or end_condition is invalid.

    References:
        IS 456:2000, Cl. 25.2, Table 28

    Examples:
        >>> calculate_effective_length_is456(3000, 'FIXED_FIXED')
        {'le_mm': 1950.0, 'ratio': 0.65, 'end_condition': 'FIXED_FIXED', 'method': 'recommended'}
        >>> calculate_effective_length_is456(4000, 'HINGED_HINGED', use_theoretical=True)
        {'le_mm': 4000.0, 'ratio': 1.0, 'end_condition': 'HINGED_HINGED', 'method': 'theoretical'}
    """
    # Plausibility guard: reasonable column lengths (100mm to 50m)
    if not (100 <= l_mm <= 50000):
        raise ValueError(
            f"Unsupported length l_mm must be between 100 and 50000 mm, got {l_mm}"
        )

    # Convert string to EndCondition enum
    try:
        end_cond_enum = EndCondition[end_condition]
    except KeyError as err:
        valid_conditions = ", ".join([ec.name for ec in EndCondition])
        raise ValueError(
            f"Invalid end_condition '{end_condition}'. "
            f"Valid options: {valid_conditions}"
        ) from err

    # Call the underlying IS 456 function
    le_mm = effective_length(
        l_mm=l_mm,
        end_condition=end_cond_enum,
        use_theoretical=use_theoretical,
    )

    # Calculate the ratio for reference
    ratio = le_mm / l_mm

    return {
        "le_mm": le_mm,
        "ratio": ratio,
        "end_condition": end_condition,
        "method": "theoretical" if use_theoretical else "recommended",
    }


def classify_column_is456(
    le_mm: float,
    D_mm: float,
) -> str:
    """Classify column as SHORT or SLENDER based on slenderness ratio (IS 456 Cl 25.1.2).

    A column is considered SHORT if both:
    - le/D < 12 for a rectangular column
    - le/d < 12 for a circular column (d = diameter)

    where le = effective length based on end restraints.

    Args:
        le_mm: Effective length (mm). Must be > 0.
        D_mm: Least lateral dimension (mm). For rectangular: smaller of b or D.
              For circular: diameter. Must be > 0.

    Returns:
        "SHORT" if slenderness ratio < 12, "SLENDER" otherwise.

    Raises:
        E_COLUMN_001: If le_mm ≤ 0 or D_mm ≤ 0.

    References:
        IS 456:2000, Cl. 25.1.2, Table 28

    Examples:
        >>> classify_column_is456(le_mm=3000, D_mm=300)
        'SHORT'
        >>> classify_column_is456(le_mm=4800, D_mm=300)
        'SLENDER'
    """

    result = classify_column(le_mm=le_mm, D_mm=D_mm)
    return result.name  # Return "SHORT" or "SLENDER" string


def min_eccentricity_is456(
    l_unsupported_mm: float,
    D_mm: float,
) -> float:
    """Calculate minimum design eccentricity for a column (IS 456 Cl 25.4).

    Per IS 456:2000 Cl 25.4, all columns must be designed for minimum eccentricity:
        e_min = greater of (l_unsupported/500 + D/30) or 20mm

    where:
    - l_unsupported = unsupported length of the column
    - D = lateral dimension in the plane of bending

    Args:
        l_unsupported_mm: Unsupported length of column (mm). Must be > 0.
        D_mm: Lateral dimension in the plane of bending (mm). Must be > 0.

    Returns:
        Minimum eccentricity e_min (mm). Always ≥ 20mm.

    Raises:
        E_COLUMN_002: If l_unsupported_mm ≤ 0 or D_mm ≤ 0.

    References:
        IS 456:2000, Cl. 25.4

    Examples:
        >>> min_eccentricity_is456(l_unsupported_mm=3000, D_mm=300)
        26.0
        >>> min_eccentricity_is456(l_unsupported_mm=2000, D_mm=200)
        20.67
    """
    return min_eccentricity(l_unsupported_mm=l_unsupported_mm, D_mm=D_mm)


def design_column_axial_is456(
    fck: float,
    fy: float,
    Ag_mm2: float,
    Asc_mm2: float,
) -> dict[str, Any]:
    """Calculate axial load capacity for a short column (IS 456 Cl 39.3).

    For a short column under pure axial load (or minimum eccentricity),
    the design strength is:

        Pu = 0.4·fck·Ac + 0.67·fy·Asc

    where:
    - Ac = Ag - Asc (net concrete area)
    - Asc = area of longitudinal steel (must be 0.8% to 6% of Ag)

    NOTE: This applies ONLY to SHORT columns with minimum eccentricity.
    For slender columns or significant eccentricity, use interaction diagrams.

    Args:
        fck: Characteristic concrete strength (N/mm²). Must be > 0.
        fy: Yield strength of steel (N/mm²). Must be > 0.
        Ag_mm2: Gross cross-sectional area (mm²). Must be > 0.
        Asc_mm2: Area of longitudinal reinforcement (mm²). Must be ≥ 0.

    Returns:
        Dictionary with:
            - Pu_kN: Axial load capacity (kN)
            - steel_ratio: Asc/Ag (percentage)
            - warnings: List of warnings (e.g., steel ratio out of code limits)

    Raises:
        E_COLUMN_003: If fck ≤ 0, fy ≤ 0, or Ag_mm2 ≤ 0.
        E_COLUMN_004: If Asc_mm2 < 0.
        E_COLUMN_005: If Asc_mm2 > Ag_mm2.

    References:
        IS 456:2000, Cl. 39.3
        IS 456:2000, Cl. 26.5.3.1 (steel ratio limits)

    Examples:
        >>> result = design_column_axial_is456(
        ...     fck=25.0,
        ...     fy=415.0,
        ...     Ag_mm2=90000.0,
        ...     Asc_mm2=1800.0
        ... )
        >>> result['Pu_kN']
        1380.62
        >>> result['steel_ratio']
        0.02
    """
    from structural_lib.core.data_types import ColumnAxialResult

    result: ColumnAxialResult = short_axial_capacity(
        fck=fck,
        fy=fy,
        Ag_mm2=Ag_mm2,
        Asc_mm2=Asc_mm2,
    )

    return {
        "Pu_kN": result.Pu_kN,
        "steel_ratio": result.steel_ratio,
        "warnings": result.warnings,
    }


def design_short_column_uniaxial_is456(
    Pu_kN: float,  # noqa: N803
    Mu_kNm: float,  # noqa: N803
    b_mm: float,
    D_mm: float,
    le_mm: float,
    fck: float,
    fy: float,
    Asc_mm2: float,
    d_prime_mm: float,
    l_unsupported_mm: float | None = None,
) -> dict[str, Any]:
    """Design short column for uniaxial bending per IS 456 Cl 39.5.

    Generates the P-M interaction envelope for the given section and
    determines whether the applied (Pu, Mu) lies within it. Uses radial
    intersection to find capacity: a ray from origin through (Pu, Mu)
    intersects the envelope at (Pu_cap, Mu_cap).

    Reinforcement is assumed symmetrical: Asc_mm2 / 2 on each face, placed
    at d_prime_mm from the nearest face.

    Args:
        Pu_kN: Applied factored axial load (kN). Must be >= 0.
        Mu_kNm: Applied factored moment about bending axis (kNm). Must be >= 0.
        b_mm: Column width perpendicular to bending axis (mm). Typical: 100-2000.
        D_mm: Column depth in direction of bending (mm). Typical: 100-2000.
        le_mm: Effective length of column (mm). Must be > 0.
        fck: Characteristic concrete strength (N/mm²). IS 456 range: 15-80.
        fy: Yield strength of steel (N/mm²). IS 456 range: 250-550.
        Asc_mm2: Total longitudinal reinforcement area (mm²), symmetrically placed.
        d_prime_mm: Distance from face to steel centroid (mm). Must be > 0 and < D_mm/2.
        l_unsupported_mm: Unsupported length (mm) for min eccentricity per Cl 25.4.
            If None, minimum eccentricity check is skipped.

    Returns:
        Dictionary with:
            - ok: True if (Pu, Mu) is within capacity envelope
            - utilization: Radial utilization ratio (applied / capacity)
            - Pu_cap_kN: Capacity axial load at same Pu/Mu slope
            - Mu_cap_kNm: Capacity moment at same Pu/Mu slope
            - classification: "SHORT" or "SLENDER"
            - eccentricity_mm: Actual eccentricity e = M/P
            - e_min_mm: Minimum eccentricity (if l_unsupported_mm provided)
            - warnings: List of code compliance warnings

    Raises:
        DimensionError: If geometric dimensions are invalid.
        MaterialError: If material properties are out of range.
        ValueError: If plausibility checks fail.

    References:
        IS 456:2000, Cl. 39.5 (P-M interaction)
        IS 456:2000, Cl. 25.4 (minimum eccentricity)
        IS 456:2000, Cl. 25.1.2 (column classification)
        SP:16:1980 Design Aids, Charts 27-62, Table I

    Examples:
        >>> result = design_short_column_uniaxial_is456(
        ...     Pu_kN=1200.0,
        ...     Mu_kNm=150.0,
        ...     b_mm=300.0,
        ...     D_mm=450.0,
        ...     le_mm=3000.0,
        ...     fck=25.0,
        ...     fy=415.0,
        ...     Asc_mm2=2700.0,
        ...     d_prime_mm=50.0,
        ...     l_unsupported_mm=3000.0,
        ... )
        >>> print(f"Safe: {result['ok']}")
        >>> print(f"Utilization: {result['utilization']:.1%}")

    See Also:
        - classify_column_is456: Check if column is short or slender
        - min_eccentricity_is456: Calculate minimum eccentricity
        - design_column_axial_is456: Pure axial capacity (no moment)
        - codes.is456.column.uniaxial.design_short_column_uniaxial: Core implementation
    """
    from structural_lib.core.data_types import ColumnUniaxialResult

    # Plausibility guards (aligned with existing api.py patterns)
    if Pu_kN < 0:
        raise ValueError(f"Axial load Pu_kN must be >= 0, got {Pu_kN}")
    if Mu_kNm < 0:
        raise ValueError(f"Moment Mu_kNm must be >= 0, got {Mu_kNm}")

    # Dimension checks
    if not (100 <= b_mm <= 2000):
        raise ValueError(
            f"Column width b_mm should be 100-2000mm (got {b_mm}). "
            "If intentional, adjust validation."
        )
    if not (100 <= D_mm <= 2000):
        raise ValueError(
            f"Column depth D_mm should be 100-2000mm (got {D_mm}). "
            "If intentional, adjust validation."
        )

    # Material checks
    if not (15 <= fck <= 80):
        raise ValueError(
            f"fck should be 15-80 N/mm² per IS 456 (got {fck}). "
            "If intentional, adjust validation."
        )
    if not (250 <= fy <= 550):
        raise ValueError(
            f"fy should be 250-550 N/mm² per IS 456 (got {fy}). "
            "If intentional, adjust validation."
        )

    # Call core implementation (already has full validation)
    result: ColumnUniaxialResult = design_short_column_uniaxial(
        Pu_kN=Pu_kN,
        Mu_kNm=Mu_kNm,
        b_mm=b_mm,
        D_mm=D_mm,
        le_mm=le_mm,
        fck=fck,
        fy=fy,
        Asc_mm2=Asc_mm2,
        d_prime_mm=d_prime_mm,
        l_unsupported_mm=l_unsupported_mm,
    )

    # Return serializable dict (not dataclass)
    return {
        "ok": result.is_safe,
        "utilization": result.utilization_ratio,
        "Pu_cap_kN": result.Pu_cap_kN,
        "Mu_cap_kNm": result.Mu_cap_kNm,
        "classification": result.classification.name,
        "eccentricity_mm": result.eccentricity_mm,
        "e_min_mm": result.e_min_mm,
        "warnings": list(result.warnings),
    }


def pm_interaction_curve_is456(
    b_mm: float,
    D_mm: float,  # noqa: N803
    fck: float,
    fy: float,
    Asc_mm2: float,  # noqa: N803
    d_prime_mm: float,
    n_points: int = 50,
) -> dict[str, Any]:
    """Generate P-M interaction curve for column per IS 456 Cl 39.5.

    Produces the complete P-M interaction diagram for a rectangular column
    section with symmetrically placed reinforcement. Returns key points
    (pure axial, balanced, pure bending) and the full curve data.

    Args:
        b_mm: Column width (mm). Must be > 0.
        D_mm: Column depth in bending direction (mm). Must be > 0.
        fck: Characteristic compressive strength of concrete (N/mm²).
        fy: Characteristic yield strength of steel (N/mm²).
        Asc_mm2: Total area of longitudinal reinforcement (mm²).
        d_prime_mm: Cover to steel centroid from nearest face (mm).
        n_points: Number of points on the curve (default 50, min 10).

    Returns:
        dict with keys:
            points: list of {"Pu_kN": float, "Mu_kNm": float} dicts
            Pu_0_kN: Pure axial capacity (kN)
            Mu_0_kNm: Pure bending capacity (kN·m)
            Pu_bal_kN: Balanced point axial load (kN)
            Mu_bal_kNm: Balanced point moment (kN·m)
            fck, fy, b_mm, D_mm, Asc_mm2, d_prime_mm: echoed inputs
            clause_ref: "Cl. 39.5"
            warnings: list of warning strings

    Raises:
        DimensionError: If geometric dimensions are invalid.
        MaterialError: If material properties are out of range.
        ValueError: If n_points < 10.

    Example:
        >>> result = pm_interaction_curve_is456(
        ...     b_mm=300, D_mm=500, fck=25, fy=415,
        ...     Asc_mm2=3000, d_prime_mm=50,
        ... )
        >>> result["Pu_0_kN"]  # Pure axial capacity
        2304.15

    See Also:
        - codes.is456.column.uniaxial.pm_interaction_curve: Core implementation
    """
    from structural_lib.core.data_types import PMInteractionResult

    result: PMInteractionResult = pm_interaction_curve(
        b_mm=b_mm,
        D_mm=D_mm,
        fck=fck,
        fy=fy,
        Asc_mm2=Asc_mm2,
        d_prime_mm=d_prime_mm,
        n_points=n_points,
    )
    return result.to_dict()


def biaxial_bending_check_is456(
    Pu_kN: float,
    Mux_kNm: float,
    Muy_kNm: float,
    b_mm: float,
    D_mm: float,
    le_mm: float,
    fck: float,
    fy: float,
    Asc_mm2: float,
    d_prime_mm: float,
    l_unsupported_mm: float | None = None,
) -> dict[str, Any]:
    """Check column under biaxial bending per IS 456 Cl 39.6.

    Implements the Bresler load contour formula to check if a column section
    with symmetrical reinforcement can safely resist combined axial load and
    biaxial bending moments.

    The Bresler formula is:
        (Mux / Mux1)^alpha_n + (Muy / Muy1)^alpha_n <= 1.0

    where Mux1, Muy1 are the uniaxial moment capacities at the applied
    axial load Pu, obtained from P-M interaction curves. The exponent
    alpha_n varies from 1.0 to 2.0 based on the Pu/Puz ratio.

    Reinforcement is assumed symmetrical: Asc_mm2 / 2 on each face,
    placed at d_prime_mm from the nearest face.

    Args:
        Pu_kN: Applied factored axial load (kN). Must be >= 0.
        Mux_kNm: Applied factored moment about x-axis (kNm). Must be >= 0.
        Muy_kNm: Applied factored moment about y-axis (kNm). Must be >= 0.
        b_mm: Column width perpendicular to x-axis bending (mm).
            Typical: 100-2000.
        D_mm: Column depth in x-axis bending direction (mm).
            Typical: 100-2000.
        le_mm: Effective length of column (mm). Must be > 0.
        fck: Characteristic concrete strength (N/mm²). IS 456 range: 15-80.
        fy: Yield strength of steel (N/mm²). IS 456 range: 250-550.
        Asc_mm2: Total longitudinal reinforcement area (mm²),
            symmetrically placed.
        d_prime_mm: Distance from face to steel centroid (mm).
            Must be > 0 and < min(b_mm, D_mm)/2.
        l_unsupported_mm: Unsupported length (mm) for slenderness warning.
            If None, slenderness is checked using le_mm only.

    Returns:
        Dictionary with:
            - Pu_kN: Applied axial load (kN)
            - Mux_kNm: Applied moment about x-axis (kN·m)
            - Muy_kNm: Applied moment about y-axis (kN·m)
            - Mux1_kNm: Uniaxial moment capacity about x at Pu (kN·m)
            - Muy1_kNm: Uniaxial moment capacity about y at Pu (kN·m)
            - Puz_kN: Pure axial crush capacity (kN) per Cl 39.6a
            - alpha_n: Bresler exponent (1.0–2.0)
            - interaction_ratio: (Mux/Mux1)^αn + (Muy/Muy1)^αn
            - is_safe: True if interaction_ratio ≤ 1.0
            - classification: "SHORT" or "SLENDER"
            - clause_ref: "Cl. 39.6"
            - warnings: List of warning messages

    Raises:
        DimensionError: If geometric dimensions are invalid.
        MaterialError: If material properties are out of range.
        CalculationError: If numerical issues are encountered.
        ValueError: If plausibility checks fail.

    References:
        IS 456:2000, Cl. 39.6 (biaxial bending, Bresler formula)
        IS 456:2000, Cl. 39.6a (Puz formula)
        IS 456:2000, Cl. 39.5 (P-M interaction envelope)
        IS 456:2000, Cl. 25.1.2 (column classification)
        SP:16:1980 Design Aids, Charts 63-64
        Pillai & Menon, "Reinforced Concrete Design", 3rd Ed., Ch. 13

    Examples:
        >>> result = biaxial_bending_check_is456(
        ...     Pu_kN=1200.0,
        ...     Mux_kNm=80.0,
        ...     Muy_kNm=60.0,
        ...     b_mm=300.0,
        ...     D_mm=450.0,
        ...     le_mm=3000.0,
        ...     fck=25.0,
        ...     fy=415.0,
        ...     Asc_mm2=2700.0,
        ...     d_prime_mm=50.0,
        ... )
        >>> print(f"Safe: {result['is_safe']}")
        >>> print(f"Interaction Ratio: {result['interaction_ratio']:.3f}")

    See Also:
        - design_short_column_uniaxial_is456: Uniaxial bending check
        - pm_interaction_curve_is456: Generate P-M interaction curve
        - classify_column_is456: Check if column is short or slender
        - codes.is456.column.biaxial.biaxial_bending_check: Core implementation
    """
    from structural_lib.core.data_types import ColumnBiaxialResult

    # Plausibility guards (aligned with existing api.py patterns)
    if Pu_kN < 0:
        raise ValueError(f"Axial load Pu_kN must be >= 0, got {Pu_kN}")
    if Mux_kNm < 0:
        raise ValueError(f"Moment Mux_kNm must be >= 0, got {Mux_kNm}")
    if Muy_kNm < 0:
        raise ValueError(f"Moment Muy_kNm must be >= 0, got {Muy_kNm}")

    # Dimension checks
    if not (100 <= b_mm <= 2000):
        raise ValueError(
            f"Column width b_mm should be 100-2000mm (got {b_mm}). "
            "If intentional, adjust validation."
        )
    if not (100 <= D_mm <= 2000):
        raise ValueError(
            f"Column depth D_mm should be 100-2000mm (got {D_mm}). "
            "If intentional, adjust validation."
        )

    # Material checks
    if not (15 <= fck <= 80):
        raise ValueError(
            f"fck should be 15-80 N/mm² per IS 456 (got {fck}). "
            "If intentional, adjust validation."
        )
    if not (250 <= fy <= 550):
        raise ValueError(
            f"fy should be 250-550 N/mm² per IS 456 (got {fy}). "
            "If intentional, adjust validation."
        )

    # Call core implementation (already has full validation)
    result: ColumnBiaxialResult = biaxial_bending_check(
        Pu_kN=Pu_kN,
        Mux_kNm=Mux_kNm,
        Muy_kNm=Muy_kNm,
        b_mm=b_mm,
        D_mm=D_mm,
        le_mm=le_mm,
        fck=fck,
        fy=fy,
        Asc_mm2=Asc_mm2,
        d_prime_mm=d_prime_mm,
        l_unsupported_mm=l_unsupported_mm,
    )

    # Return serializable dict (not dataclass)
    return result.to_dict()


def calculate_additional_moment_is456(
    Pu_kN: float,
    b_mm: float,
    D_mm: float,
    lex_mm: float,
    ley_mm: float,
    fck: float,
    fy: float,
    Asc_mm2: float,
    d_prime_mm: float,
) -> dict[str, Any]:
    """Calculate additional moment for slender columns per IS 456 Cl 39.7.1.

    For slender columns (le/D >= 12), IS 456 requires an additional moment
    Ma = Pu × eadd to account for P-delta effects.

    Args:
        Pu_kN: Factored axial load (kN). Must be >= 0.
        b_mm: Column width (mm). Must be > 0.
        D_mm: Column depth (mm). Must be > 0.
        lex_mm: Effective length about x-axis (mm). Must be > 0.
        ley_mm: Effective length about y-axis (mm). Must be > 0.
        fck: Concrete characteristic strength (N/mm²).
        fy: Steel yield strength (N/mm²).
        Asc_mm2: Total longitudinal steel area (mm²).
        d_prime_mm: Cover to centroid of reinforcement (mm).

    Returns:
        Dictionary with additional moments, eccentricities, k-factor,
        and slenderness classification for both axes.

    Raises:
        DimensionError: If geometric dimensions are invalid.
        MaterialError: If material properties are out of range.
        CalculationError: If numerical issues are encountered.
        ValueError: If plausibility checks fail.

    References:
        IS 456:2000, Cl. 39.7.1, 39.7.1.1

    Examples:
        >>> result = calculate_additional_moment_is456(
        ...     Pu_kN=1200.0,
        ...     b_mm=300.0,
        ...     D_mm=450.0,
        ...     lex_mm=5400.0,
        ...     ley_mm=3600.0,
        ...     fck=25.0,
        ...     fy=415.0,
        ...     Asc_mm2=2700.0,
        ...     d_prime_mm=50.0,
        ... )
        >>> print(f"Ma_x: {result['Ma_x_kNm']:.2f} kN·m")
        >>> print(f"Ma_y: {result['Ma_y_kNm']:.2f} kN·m")

    See Also:
        - classify_column_is456: Check if column is short or slender
        - biaxial_bending_check_is456: Biaxial bending check
        - codes.is456.column.slenderness.calculate_additional_moment: Core implementation
    """
    from structural_lib.codes.is456.column.slenderness import (
        calculate_additional_moment,
    )

    # Plausibility guards (unit confusion detection)
    if b_mm > 5000:
        raise ValueError("b_mm > 5000 — did you pass meters instead of mm?")
    if D_mm > 5000:
        raise ValueError("D_mm > 5000 — did you pass meters instead of mm?")
    if lex_mm > 100000:
        raise ValueError("lex_mm > 100000 — did you pass meters instead of mm?")
    if ley_mm > 100000:
        raise ValueError("ley_mm > 100000 — did you pass meters instead of mm?")

    # Call core implementation (already has full validation)
    result = calculate_additional_moment(
        Pu_kN=Pu_kN,
        b_mm=b_mm,
        D_mm=D_mm,
        lex_mm=lex_mm,
        ley_mm=ley_mm,
        fck=fck,
        fy=fy,
        Asc_mm2=Asc_mm2,
        d_prime_mm=d_prime_mm,
    )

    return result.to_dict()


def design_long_column_is456(
    Pu_kN: float,
    M1x_kNm: float,
    M2x_kNm: float,
    M1y_kNm: float,
    M2y_kNm: float,
    b_mm: float,
    D_mm: float,
    lex_mm: float,
    ley_mm: float,
    fck: float,
    fy: float,
    Asc_mm2: float,
    d_prime_mm: float,
    braced: bool = True,
) -> dict[str, Any]:
    """Design a long (slender) column per IS 456 Cl 39.7.

    For slender columns (le/D >= 12), the design must account for additional
    moments due to P-delta effects. This function:
    1. Calculates additional moment Ma per Cl 39.7.1
    2. Augments applied moments: Mx_design = Mx + Ma_x
    3. Checks biaxial capacity with augmented moments

    The column must satisfy both:
    - Uniaxial checks with augmented moments
    - Biaxial interaction check (Bresler formula)

    Args:
        Pu_kN: Factored axial load (kN). Must be >= 0.
        M1x_kNm: End moment 1 about x-axis (kNm). For equal end moments,
            M1x = M2x. Sign convention: +ve causes tension on same face.
        M2x_kNm: End moment 2 about x-axis (kNm).
        M1y_kNm: End moment 1 about y-axis (kNm).
        M2y_kNm: End moment 2 about y-axis (kNm).
        b_mm: Column width perpendicular to x-axis (mm). Typical: 100-2000.
        D_mm: Column depth in x-direction (mm). Typical: 100-2000.
        lex_mm: Effective length about x-axis (mm). Must be > 0.
        ley_mm: Effective length about y-axis (mm). Must be > 0.
        fck: Concrete characteristic strength (N/mm²). IS 456 range: 15-80.
        fy: Steel yield strength (N/mm²). IS 456 range: 250-550.
        Asc_mm2: Total longitudinal steel area (mm²), symmetrically placed.
        d_prime_mm: Cover to centroid of reinforcement (mm). Must be > 0.
        braced: If True, assumes braced frame (sway prevented). Default: True.

    Returns:
        Dictionary with:
            - is_safe (bool): True if column is adequate
            - classification (str): "SLENDER"
            - Pu_kN (float): Applied axial load (kN)
            - M1x_kNm, M2x_kNm, M1y_kNm, M2y_kNm (float): Applied end moments
            - Ma_x_kNm, Ma_y_kNm (float): Additional moments from P-delta (kNm)
            - Mx_design_kNm, My_design_kNm (float): Total design moments (kNm)
            - biaxial_check (dict): Result from biaxial_bending_check_is456
            - clause_ref (str): "Cl. 39.7"
            - warnings (list): Warning messages

    Raises:
        DimensionError: If geometric dimensions are invalid.
        MaterialError: If material properties are out of range.
        CalculationError: If numerical issues are encountered.
        ValueError: If plausibility checks fail.

    References:
        IS 456:2000, Cl. 39.7 (slender column design)
        IS 456:2000, Cl. 39.7.1 (additional moment Ma)
        IS 456:2000, Cl. 39.6 (biaxial bending check)

    Examples:
        >>> result = design_long_column_is456(
        ...     Pu_kN=1200.0,
        ...     M1x_kNm=60.0,
        ...     M2x_kNm=80.0,
        ...     M1y_kNm=40.0,
        ...     M2y_kNm=50.0,
        ...     b_mm=300.0,
        ...     D_mm=450.0,
        ...     lex_mm=5400.0,
        ...     ley_mm=3600.0,
        ...     fck=25.0,
        ...     fy=415.0,
        ...     Asc_mm2=2700.0,
        ...     d_prime_mm=50.0,
        ... )
        >>> print(f"Safe: {result['is_safe']}")
        >>> print(f"Design Moment X: {result['Mx_design_kNm']:.2f} kN·m")

    See Also:
        - calculate_additional_moment_is456: Calculate Ma per Cl 39.7.1
        - biaxial_bending_check_is456: Biaxial capacity check
        - classify_column_is456: Classify as SHORT or SLENDER
        - codes.is456.column.long_column.design_long_column: Core implementation
    """
    from structural_lib.codes.is456.column.long_column import design_long_column
    from structural_lib.core.data_types import LongColumnResult

    # Plausibility guards (unit confusion detection)
    if Pu_kN < 0:
        raise ValueError(f"Axial load Pu_kN must be >= 0, got {Pu_kN}")
    if not (100 <= b_mm <= 2000):
        raise ValueError(
            f"Column width b_mm should be 100-2000mm (got {b_mm}). "
            "If intentional, adjust validation."
        )
    if not (100 <= D_mm <= 2000):
        raise ValueError(
            f"Column depth D_mm should be 100-2000mm (got {D_mm}). "
            "If intentional, adjust validation."
        )
    if not (15 <= fck <= 80):
        raise ValueError(
            f"fck should be 15-80 N/mm² per IS 456 (got {fck}). "
            "If intentional, adjust validation."
        )
    if not (250 <= fy <= 550):
        raise ValueError(
            f"fy should be 250-550 N/mm² per IS 456 (got {fy}). "
            "If intentional, adjust validation."
        )

    # Call core implementation (already has full validation)
    result: LongColumnResult = design_long_column(
        Pu_kN=Pu_kN,
        M1x_kNm=M1x_kNm,
        M2x_kNm=M2x_kNm,
        M1y_kNm=M1y_kNm,
        M2y_kNm=M2y_kNm,
        b_mm=b_mm,
        D_mm=D_mm,
        lex_mm=lex_mm,
        ley_mm=ley_mm,
        fck=fck,
        fy=fy,
        Asc_mm2=Asc_mm2,
        d_prime_mm=d_prime_mm,
        braced=braced,
    )

    # Return serializable dict (not dataclass)
    return result.to_dict()


def check_helical_reinforcement_is456(
    D_mm: float,
    D_core_mm: float,
    fck: float,
    fy: float,
    d_helix_mm: float,
    pitch_mm: float,
    Pu_axial_kN: float,
) -> dict[str, Any]:
    """Check helical reinforcement for circular column per IS 456 Cl 39.4.

    For circular columns with helical (spiral) reinforcement, IS 456 Cl 39.4
    provides an alternative design approach where the helically reinforced
    core can carry significantly higher loads than a tied column.

    The pure axial capacity is given by:
        Pu = 1.05 × (0.4·fck·Ac + 0.67·fy·Asc + ρh·fck·Ak)

    where:
    - Ac = core area within helix
    - Asc = longitudinal steel area
    - Ak = core area measured to outside of helix
    - ρh = volumetric ratio of helical steel

    The helix must satisfy minimum pitch and bar diameter requirements
    per Cl 26.5.3.2(c).

    Args:
        D_mm: Overall column diameter (mm). Must be > 200 (typical: 200-2000).
        D_core_mm: Core diameter to centerline of helix (mm). Must be < D_mm.
        fck: Concrete characteristic strength (N/mm²). IS 456 range: 15-80.
        fy: Steel yield strength (N/mm²). IS 456 range: 250-550.
        d_helix_mm: Diameter of helical bar (mm). Typical: 8-20.
        pitch_mm: Pitch of helix (mm). Must satisfy: 25mm ≤ pitch ≤ 75mm
            or pitch ≤ D_core/6 per Cl 26.5.3.2(c).
        Pu_axial_kN: Applied factored axial load (kN). Must be >= 0.

    Returns:
        Dictionary with:
            - is_safe (bool): True if helix satisfies IS 456 requirements
            - Pu_capacity_kN (float): Axial capacity with helical reinforcement (kN)
            - rho_h (float): Volumetric ratio of helical steel (dimensionless)
            - Ah_mm2 (float): Cross-sectional area of one helix turn (mm²)
            - pitch_ok (bool): True if pitch meets Cl 26.5.3.2(c)
            - d_helix_ok (bool): True if bar diameter adequate
            - utilization (float): Pu_axial / Pu_capacity (0.0-1.0)
            - clause_ref (str): "Cl. 39.4"
            - warnings (list): Warning messages

    Raises:
        DimensionError: If geometric dimensions are invalid.
        MaterialError: If material properties are out of range.
        ValueError: If plausibility checks fail.

    References:
        IS 456:2000, Cl. 39.4 (helically reinforced columns)
        IS 456:2000, Cl. 26.5.3.2(c) (helix pitch and bar diameter)

    Examples:
        >>> result = check_helical_reinforcement_is456(
        ...     D_mm=500.0,
        ...     D_core_mm=440.0,
        ...     fck=25.0,
        ...     fy=415.0,
        ...     d_helix_mm=10.0,
        ...     pitch_mm=50.0,
        ...     Pu_axial_kN=2000.0,
        ... )
        >>> print(f"Safe: {result['is_safe']}")
        >>> print(f"Capacity: {result['Pu_capacity_kN']:.2f} kN")

    See Also:
        - design_column_axial_is456: Pure axial capacity check
        - codes.is456.column.helical.check_helical_reinforcement: Core implementation
    """
    from structural_lib.codes.is456.column.helical import check_helical_reinforcement
    from structural_lib.core.data_types import HelicalReinforcementResult

    # Plausibility guards (unit confusion detection)
    if D_mm > 5000:
        raise ValueError("D_mm > 5000 — did you pass meters instead of mm?")
    if D_core_mm >= D_mm:
        raise ValueError(
            f"Core diameter D_core_mm ({D_core_mm}) must be < overall diameter D_mm ({D_mm})"
        )
    if not (15 <= fck <= 80):
        raise ValueError(
            f"fck should be 15-80 N/mm² per IS 456 (got {fck}). "
            "If intentional, adjust validation."
        )
    if not (250 <= fy <= 550):
        raise ValueError(
            f"fy should be 250-550 N/mm² per IS 456 (got {fy}). "
            "If intentional, adjust validation."
        )

    # Call core implementation (already has full validation)
    result: HelicalReinforcementResult = check_helical_reinforcement(
        D_mm=D_mm,
        D_core_mm=D_core_mm,
        fck=fck,
        fy=fy,
        d_helix_mm=d_helix_mm,
        pitch_mm=pitch_mm,
        Pu_axial_kN=Pu_axial_kN,
    )

    # Return serializable dict (not dataclass)
    return result.to_dict()


def design_column_is456(
    Pu_kN: float,
    Mux_kNm: float = 0.0,
    Muy_kNm: float = 0.0,
    b_mm: float = 0.0,
    D_mm: float = 0.0,
    l_mm: float = 0.0,
    end_condition: str = "FIXED_FIXED",
    fck: float = 25.0,
    fy: float = 415.0,
    Asc_mm2: float = 0.0,
    d_prime_mm: float = 50.0,
    l_unsupported_mm: float | None = None,
    braced: bool = True,
    M1x_kNm: float | None = None,
    M2x_kNm: float | None = None,
    M1y_kNm: float | None = None,
    M2y_kNm: float | None = None,
) -> dict[str, Any]:
    """Design column per IS 456:2000 — unified orchestrator.

    Master entry point for column design that automatically routes to the
    appropriate design checks based on column classification. Handles:
    1. Effective length calculation from end conditions (Cl 25.2, Table 28)
    2. Column classification as SHORT or SLENDER (Cl 25.1.2)
    3. Minimum eccentricity enforcement (Cl 25.4)
    4. Short column checks: uniaxial or biaxial (Cl 39.5, 39.6)
    5. Slender column checks with additional moments (Cl 39.7)

    This function provides a single, consistent interface for all column
    design scenarios, automatically selecting the appropriate IS 456 clauses.

    Args:
        Pu_kN: Factored axial load (kN). Must be >= 0.
        Mux_kNm: Applied factored moment about x-axis (kNm). Default: 0.0.
        Muy_kNm: Applied factored moment about y-axis (kNm). Default: 0.0.
        b_mm: Column width perpendicular to x-axis (mm). Default: 0.0.
            Typical: 100-2000.
        D_mm: Column depth in x-direction (mm). Default: 0.0.
            Typical: 100-2000.
        l_mm: Unsupported length of column (mm). Default: 0.0.
        end_condition: End restraint condition. Default: 'FIXED_FIXED'.
            Options: 'FIXED_FIXED', 'FIXED_HINGED', 'FIXED_FIXED_SWAY',
            'FIXED_FREE', 'HINGED_HINGED', 'FIXED_PARTIAL', 'HINGED_PARTIAL'.
        fck: Concrete characteristic strength (N/mm²). Default: 25.0.
            IS 456 range: 15-80.
        fy: Steel yield strength (N/mm²). Default: 415.0.
            IS 456 range: 250-550.
        Asc_mm2: Total longitudinal steel area (mm²). Default: 0.0.
            For initial sizing, use 0.8-6% of gross area.
        d_prime_mm: Cover to centroid of reinforcement (mm). Default: 50.0.
        l_unsupported_mm: Unsupported length for min eccentricity (mm).
            If None, uses l_mm. Used for Cl 25.4 minimum eccentricity.
        braced: If True, assumes braced frame (sway prevented). Default: True.
            Affects slender column moment magnification.
        M1x_kNm: End moment 1 about x-axis (kNm) for slender columns.
            If None and column is slender, assumes M1x = M2x = Mux.
        M2x_kNm: End moment 2 about x-axis (kNm) for slender columns.
            If None and column is slender, assumes M2x = Mux.
        M1y_kNm: End moment 1 about y-axis (kNm) for slender columns.
            If None and column is slender, assumes M1y = M2y = Muy.
        M2y_kNm: End moment 2 about y-axis (kNm) for slender columns.
            If None and column is slender, assumes M2y = Muy.

    Returns:
        Dictionary with:
            - is_safe (bool): Overall adequacy indicator
            - classification (str): "SHORT" or "SLENDER"
            - le_x_mm, le_y_mm (float): Effective lengths (mm)
            - slenderness_x, slenderness_y (float): Slenderness ratios
            - emin_x_mm, emin_y_mm (float): Minimum eccentricities (mm)
            - Mux_design_kNm, Muy_design_kNm (float): Design moments with
                minimum eccentricity and (for slender) additional moments (kNm)
            - governing_check (str): "uniaxial_x", "uniaxial_y", "biaxial",
                or "long_column"
            - checks (dict): Results from all applicable sub-checks
            - clause_refs (list): List of applicable IS 456 clause references
            - warnings (list): Warning messages

    Raises:
        DimensionError: If geometric dimensions are invalid.
        MaterialError: If material properties are out of range.
        CalculationError: If numerical issues are encountered.
        ValueError: If plausibility checks fail or required inputs missing.

    References:
        IS 456:2000, Cl. 25.2 (effective length)
        IS 456:2000, Cl. 25.1.2 (column classification)
        IS 456:2000, Cl. 25.4 (minimum eccentricity)
        IS 456:2000, Cl. 39.5 (short column uniaxial)
        IS 456:2000, Cl. 39.6 (short column biaxial)
        IS 456:2000, Cl. 39.7 (slender column design)

    Examples:
        >>> # Short column, uniaxial
        >>> result = design_column_is456(
        ...     Pu_kN=800.0,
        ...     Mux_kNm=120.0,
        ...     b_mm=300.0,
        ...     D_mm=450.0,
        ...     l_mm=3000.0,
        ...     fck=25.0,
        ...     fy=415.0,
        ...     Asc_mm2=2400.0,
        ... )
        >>> print(f"Safe: {result['is_safe']}")
        >>> print(f"Classification: {result['classification']}")
        >>> print(f"Governing: {result['governing_check']}")

        >>> # Slender column, biaxial
        >>> result = design_column_is456(
        ...     Pu_kN=1200.0,
        ...     Mux_kNm=80.0,
        ...     Muy_kNm=60.0,
        ...     b_mm=300.0,
        ...     D_mm=450.0,
        ...     l_mm=6000.0,
        ...     end_condition='HINGED_HINGED',
        ...     fck=25.0,
        ...     fy=415.0,
        ...     Asc_mm2=2700.0,
        ... )
        >>> print(f"Classification: {result['classification']}")  # SLENDER
        >>> print(f"Additional Moment X: {result.get('Ma_x_kNm', 0):.2f} kN·m")

    See Also:
        - calculate_effective_length_is456: Effective length per Table 28
        - classify_column_is456: SHORT vs SLENDER classification
        - min_eccentricity_is456: Minimum eccentricity per Cl 25.4
        - design_short_column_uniaxial_is456: Short column uniaxial check
        - biaxial_bending_check_is456: Short column biaxial check
        - design_long_column_is456: Slender column design with Ma
    """
    # Validate required inputs
    if b_mm <= 0 or D_mm <= 0:
        raise ValueError(f"Column dimensions must be > 0 (got b={b_mm}, D={D_mm})")
    if l_mm <= 0:
        raise ValueError(f"Column length l_mm must be > 0 (got {l_mm})")
    if Pu_kN < 0:
        raise ValueError(f"Axial load Pu_kN must be >= 0 (got {Pu_kN})")

    # Step 1: Calculate effective lengths in both directions
    le_result = calculate_effective_length_is456(l_mm, end_condition)
    le_mm = le_result["le_mm"]

    # Use same effective length for both axes unless different unsupported lengths
    le_x_mm = le_mm
    le_y_mm = le_mm

    # Step 2: Classify column based on slenderness in both directions
    classification_x = classify_column_is456(le_x_mm, D_mm)
    classification_y = classify_column_is456(le_y_mm, b_mm)

    # Overall classification: SLENDER if slender in either direction
    is_slender = (classification_x == "SLENDER") or (classification_y == "SLENDER")
    classification = "SLENDER" if is_slender else "SHORT"

    # Step 3: Calculate minimum eccentricities per Cl 25.4
    l_unsup = l_unsupported_mm if l_unsupported_mm is not None else l_mm
    emin_x_mm = min_eccentricity_is456(l_unsup, D_mm)
    emin_y_mm = min_eccentricity_is456(l_unsup, b_mm)

    # Minimum moments from eccentricity
    Mux_min_kNm = Pu_kN * emin_x_mm / 1000.0  # Convert mm to m
    Muy_min_kNm = Pu_kN * emin_y_mm / 1000.0

    # Enforce minimum eccentricity
    Mux_design = max(Mux_kNm, Mux_min_kNm)
    Muy_design = max(Muy_kNm, Muy_min_kNm)

    # Initialize result dictionary
    result: dict[str, Any] = {
        "Pu_kN": Pu_kN,
        "Mux_applied_kNm": Mux_kNm,
        "Muy_applied_kNm": Muy_kNm,
        "classification": classification,
        "le_x_mm": le_x_mm,
        "le_y_mm": le_y_mm,
        "slenderness_x": le_x_mm / D_mm,
        "slenderness_y": le_y_mm / b_mm,
        "emin_x_mm": emin_x_mm,
        "emin_y_mm": emin_y_mm,
        "Mux_min_kNm": Mux_min_kNm,
        "Muy_min_kNm": Muy_min_kNm,
        "checks": {},
        "warnings": [],
        "clause_refs": ["Cl. 25.2", "Cl. 25.1.2", "Cl. 25.4"],
    }

    # Step 4 & 5: Design path depends on classification
    if classification == "SHORT":
        # SHORT column checks
        result["Mux_design_kNm"] = Mux_design
        result["Muy_design_kNm"] = Muy_design

        # Determine if uniaxial or biaxial
        is_biaxial = (Mux_design > 0.001) and (Muy_design > 0.001)

        if is_biaxial:
            # Biaxial check
            biaxial_result = biaxial_bending_check_is456(
                Pu_kN=Pu_kN,
                Mux_kNm=Mux_design,
                Muy_kNm=Muy_design,
                b_mm=b_mm,
                D_mm=D_mm,
                le_mm=le_mm,
                fck=fck,
                fy=fy,
                Asc_mm2=Asc_mm2,
                d_prime_mm=d_prime_mm,
                l_unsupported_mm=l_unsup,
            )
            result["checks"]["biaxial"] = biaxial_result
            result["is_safe"] = biaxial_result["is_safe"]
            result["governing_check"] = "biaxial"
            result["clause_refs"].append("Cl. 39.6")
        else:
            # Uniaxial check (x-axis or y-axis dominant)
            if Mux_design >= Muy_design:
                # X-axis bending dominant
                uniaxial_result = design_short_column_uniaxial_is456(
                    Pu_kN=Pu_kN,
                    Mu_kNm=Mux_design,
                    b_mm=b_mm,
                    D_mm=D_mm,
                    le_mm=le_mm,
                    fck=fck,
                    fy=fy,
                    Asc_mm2=Asc_mm2,
                    d_prime_mm=d_prime_mm,
                )
                result["checks"]["uniaxial_x"] = uniaxial_result
                result["is_safe"] = uniaxial_result["ok"]
                result["governing_check"] = "uniaxial_x"
            else:
                # Y-axis bending dominant (swap dimensions)
                uniaxial_result = design_short_column_uniaxial_is456(
                    Pu_kN=Pu_kN,
                    Mu_kNm=Muy_design,
                    b_mm=D_mm,  # Swap for y-axis bending
                    D_mm=b_mm,
                    le_mm=le_mm,
                    fck=fck,
                    fy=fy,
                    Asc_mm2=Asc_mm2,
                    d_prime_mm=d_prime_mm,
                )
                result["checks"]["uniaxial_y"] = uniaxial_result
                result["is_safe"] = uniaxial_result["ok"]
                result["governing_check"] = "uniaxial_y"

            result["clause_refs"].append("Cl. 39.5")

    else:
        # SLENDER column — must account for additional moments
        result["clause_refs"].append("Cl. 39.7")

        # If end moments not provided, assume equal end moments
        M1x = M1x_kNm if M1x_kNm is not None else Mux_design
        M2x = M2x_kNm if M2x_kNm is not None else Mux_design
        M1y = M1y_kNm if M1y_kNm is not None else Muy_design
        M2y = M2y_kNm if M2y_kNm is not None else Muy_design

        # Call slender column design
        long_result = design_long_column_is456(
            Pu_kN=Pu_kN,
            M1x_kNm=M1x,
            M2x_kNm=M2x,
            M1y_kNm=M1y,
            M2y_kNm=M2y,
            b_mm=b_mm,
            D_mm=D_mm,
            lex_mm=le_x_mm,
            ley_mm=le_y_mm,
            fck=fck,
            fy=fy,
            Asc_mm2=Asc_mm2,
            d_prime_mm=d_prime_mm,
            braced=braced,
        )

        result["checks"]["long_column"] = long_result
        result["is_safe"] = long_result["is_safe"]
        result["governing_check"] = "long_column"

        # Include additional moments in top-level result
        result["Ma_x_kNm"] = long_result.get("Max_kNm", 0.0)
        result["Ma_y_kNm"] = long_result.get("May_kNm", 0.0)
        result["Mux_design_kNm"] = long_result.get("Mux_design_kNm", 0.0)
        result["Muy_design_kNm"] = long_result.get("Muy_design_kNm", 0.0)

        # Aggregate warnings
        if long_result.get("warnings"):
            result["warnings"].extend(long_result["warnings"])

    return result


def optimize_beam_cost(
    *,
    units: str,
    span_mm: float,
    mu_knm: float,
    vu_kn: float,
    cost_profile: CostProfile | None = None,
    cover_mm: int = 40,
) -> CostOptimizationResult:
    """Find the most cost-effective beam design meeting IS 456:2000.

    Uses brute-force optimization to find the cheapest valid beam design
    from a search space of standard dimensions and material grades.

    Args:
        units: Units label (must be one of the IS456 aliases).
        span_mm: Beam span (mm).
        mu_knm: Factored bending moment (kNm).
        vu_kn: Factored shear force (kN).
        cost_profile: Regional cost data (defaults to India CPWD 2023).
        cover_mm: Concrete cover (default 40mm).

    Returns:
        CostOptimizationResult with:
            - optimal_design: Best design found
            - baseline_cost: Conservative design cost for comparison
            - savings_amount: Cost saved (currency units)
            - savings_percent: Percentage saved
            - alternatives: List of next 3 cheapest designs
            - candidates_evaluated: Total candidates evaluated
            - candidates_valid: Number of valid candidates
            - computation_time_sec: Time taken for optimization

    Example:
        >>> result = optimize_beam_cost(
        ...     units="IS456",
        ...     span_mm=5000,
        ...     mu_knm=120,
        ...     vu_kn=80
        ... )
        >>> print(result.summary())
        'Optimal: 300×500mm, Cost: INR45,230, Savings: 18.5%'
        >>> print(f"Width: {result.optimal_design.b_mm}mm")
        >>> print(f"Savings: {result.savings_percent:.1f}%")
    """

    _require_is456_units(units)

    result = cost_optimization.optimize_beam_design(
        span_mm=span_mm,
        mu_knm=mu_knm,
        vu_kn=vu_kn,
        cost_profile=cost_profile,
    )

    # Convert internal result to CostOptimizationResult
    def _to_cost_breakdown(breakdown: Any) -> CostBreakdown:
        """Convert internal cost breakdown to CostBreakdown."""
        return CostBreakdown(
            concrete_cost=breakdown.concrete_cost,
            steel_cost=breakdown.steel_cost,
            formwork_cost=breakdown.formwork_cost,
            labor_adjustment=breakdown.labor_adjustment,
            total_cost=breakdown.total_cost,
            currency=breakdown.currency,
        )

    def _to_optimal_design(candidate: Any) -> OptimalDesign:
        """Convert internal candidate to OptimalDesign."""
        return OptimalDesign(
            b_mm=candidate.b_mm,
            D_mm=candidate.D_mm,
            d_mm=candidate.d_mm,
            fck_nmm2=candidate.fck_nmm2,
            fy_nmm2=candidate.fy_nmm2,
            cost_breakdown=_to_cost_breakdown(candidate.cost_breakdown),
            is_valid=candidate.is_valid,
            failure_reason=candidate.failure_reason,
        )

    # Convert optimal and alternatives
    optimal = result.optimal_candidate
    optimal_design = _to_optimal_design(optimal)
    alternatives = [_to_optimal_design(alt) for alt in result.alternatives if alt]
    return CostOptimizationResult(
        optimal_design=optimal_design,
        baseline_cost=result.baseline_cost,
        savings_amount=result.savings_amount,
        savings_percent=result.savings_percent,
        alternatives=alternatives,
        candidates_evaluated=result.candidates_evaluated,
        candidates_valid=result.candidates_valid,
        computation_time_sec=result.computation_time_sec,
    )


def suggest_beam_design_improvements(
    *,
    units: str,
    design: beam_pipeline.BeamDesignOutput,
    span_mm: float | None = None,
    mu_knm: float | None = None,
    vu_kn: float | None = None,
) -> DesignSuggestionsResult:
    """Get AI-driven design improvement suggestions for an IS 456:2000 beam design.

    Analyzes a completed beam design and provides actionable suggestions for:
    - Geometry optimization (oversized sections, non-standard dimensions)
    - Steel detailing (congestion, low utilization, grade optimization)
    - Cost reduction (optimization opportunities, material grade)
    - Constructability (bar count, stirrup spacing)
    - Serviceability (span/depth ratios, deflection checks)
    - Materials (uncommon grades, upgrade opportunities)

    Each suggestion includes:
    - Category and impact level (LOW/MEDIUM/HIGH)
    - Confidence score (0.0-1.0)
    - Detailed rationale with IS 456 clause references
    - Estimated benefit (quantified where possible)
    - Concrete action steps

    Args:
        units: Units label (must be one of the IS456 aliases).
        design: Completed beam design from design_beam_is456().
        span_mm: Beam span (mm), optional context for better suggestions.
        mu_knm: Factored moment (kNm), optional context.
        vu_kn: Factored shear (kN), optional context.

    Returns:
        DesignSuggestionsResult with:
            - suggestions: List of suggestions sorted by priority
            - total_count: Number of suggestions
            - high_impact_count: Number of HIGH impact suggestions
            - medium_impact_count: Number of MEDIUM impact suggestions
            - low_impact_count: Number of LOW impact suggestions
            - analysis_time_ms: Time taken for analysis
            - engine_version: Suggestion engine version

    Example:
        >>> design = design_beam_is456(...)
        >>> result = suggest_beam_design_improvements(
        ...     units="IS456",
        ...     design=design,
        ...     span_mm=5000,
        ...     mu_knm=120,
        ...     vu_kn=80
        ... )
        >>> print(result.summary())
        'Found 8 suggestions: 2 high, 4 medium, 2 low impact'
        >>> for sug in result.high_impact_suggestions():
        ...     print(f"  • [{sug.impact}] {sug.title}")
    """

    _require_is456_units(units)

    report = design_suggestions.suggest_improvements(
        design=design,
        span_mm=span_mm,
        mu_knm=mu_knm,
        vu_kn=vu_kn,
    )

    # Convert internal suggestion report to DesignSuggestionsResult
    from .api_results import Suggestion

    suggestions = [
        Suggestion(
            category=sug.category.value,
            title=sug.title,
            impact=sug.impact.value.upper(),
            confidence=sug.confidence,
            rationale=sug.rationale,
            estimated_benefit=sug.estimated_benefit,
            action_steps=sug.action_steps,
            clause_refs=[],
        )
        for sug in report.suggestions
    ]

    return DesignSuggestionsResult(
        suggestions=suggestions,
        total_count=report.suggestions_count,
        high_impact_count=report.high_impact_count,
        medium_impact_count=report.medium_impact_count,
        low_impact_count=report.low_impact_count,
        analysis_time_ms=report.analysis_time_ms,
        engine_version=report.engine_version,
    )


def smart_analyze_design(
    *,
    units: str,
    span_mm: float,
    mu_knm: float,
    vu_kn: float,
    b_mm: float,
    D_mm: float,
    d_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    d_dash_mm: float = 50.0,
    asv_mm2: float = 100.0,
    include_cost: bool = True,
    include_suggestions: bool = True,
    include_sensitivity: bool = True,
    include_constructability: bool = True,
    cost_profile: CostProfile | None = None,
    weights: dict[str, float] | None = None,
) -> SmartAnalysisResult:
    """Unified smart design analysis dashboard.

    Combines cost optimization, design suggestions, sensitivity analysis,
    and constructability assessment into a comprehensive dashboard.

    This function runs the full design pipeline internally to get complete
    design context, then performs all smart analyses.

    Args:
        units: Units label (must be "IS456").
        span_mm: Beam span (mm).
        mu_knm: Factored bending moment (kN·m).
        vu_kn: Factored shear (kN).
        b_mm: Beam width (mm).
        D_mm: Overall depth (mm).
        d_mm: Effective depth (mm).
        fck_nmm2: Concrete strength (N/mm²).
        fy_nmm2: Steel yield strength (N/mm²).
        d_dash_mm: Compression steel depth (mm, default: 50).
        asv_mm2: Stirrup area (mm², default: 100).
        include_cost: Include cost optimization (default: True).
        include_suggestions: Include design suggestions (default: True).
        include_sensitivity: Include sensitivity analysis (default: True).
        include_constructability: Include constructability (default: True).
        cost_profile: Custom cost profile (optional).
        weights: Custom weights for overall score (optional).

    Returns:
        SmartAnalysisResult with complete dashboard data.
        Use .to_dict(), .to_json(), or .to_text() for different formats.

    Raises:
        ValueError: If units is not IS456 or design fails.

    Example:
        >>> result = smart_analyze_design(
        ...     units="IS456",
        ...     span_mm=5000,
        ...     mu_knm=120,
        ...     vu_kn=85,
        ...     b_mm=300,
        ...     D_mm=500,
        ...     d_mm=450,
        ...     fck_nmm2=25,
        ...     fy_nmm2=500,
        ... )
        >>> print(result.summary())
        'Analysis Score: 78.5/100'
        >>> print(result.to_json())  # JSON string
        >>> print(result.to_text())  # Formatted text
        >>> data = result.to_dict()  # Dictionary
    """

    from structural_lib.insights import SmartDesigner

    _require_is456_units(units)

    # Unit plausibility guards (catch common mistakes)
    _validate_plausibility(
        fck_nmm2=fck_nmm2,
        fy_nmm2=fy_nmm2,
        b_mm=b_mm,
        d_mm=d_mm,
        D_mm=D_mm,
    )

    # Run full pipeline to get BeamDesignOutput
    pipeline_result = beam_pipeline.design_single_beam(
        units=units,
        b_mm=b_mm,
        D_mm=D_mm,
        d_mm=d_mm,
        cover_mm=D_mm - d_mm,  # Calculate cover from D and d
        fck_nmm2=fck_nmm2,
        fy_nmm2=fy_nmm2,
        mu_knm=mu_knm,
        vu_kn=vu_kn,
        beam_id="smart-analysis",
        story="N/A",
        span_mm=span_mm,
        d_dash_mm=d_dash_mm,
        asv_mm2=asv_mm2,
    )

    # Run smart analysis
    dashboard = SmartDesigner.analyze(
        design=pipeline_result,
        span_mm=span_mm,
        mu_knm=mu_knm,
        vu_kn=vu_kn,
        include_cost=include_cost,
        include_suggestions=include_suggestions,
        include_sensitivity=include_sensitivity,
        include_constructability=include_constructability,
        cost_profile=cost_profile,
        weights=weights,
    )

    # Convert dashboard to SmartAnalysisResult
    dashboard_dict = dashboard.to_dict()
    return SmartAnalysisResult(
        summary_data=dashboard_dict.get("summary", {}),
        metadata=dashboard_dict.get("metadata", {}),
        cost=dashboard_dict.get("cost"),
        suggestions=dashboard_dict.get("suggestions"),
        sensitivity=dashboard_dict.get("sensitivity"),
        constructability=dashboard_dict.get("constructability"),
    )


# =============================================================================
# BeamInput-based API (TASK-276: Input Flexibility)
# =============================================================================


def design_from_input(
    beam: BeamInput,
    *,
    include_detailing: bool = True,
) -> DesignAndDetailResult | ComplianceReport:
    """Design a beam using the structured BeamInput dataclass.

    This is the recommended API for new projects. It accepts a structured
    BeamInput object instead of individual parameters, providing:
    - Type safety and IDE autocompletion
    - Input validation at construction time
    - Clean separation of geometry, materials, and loads
    - Easy JSON import/export for automation

    Args:
        beam: BeamInput dataclass with geometry, materials, loads.
        include_detailing: If True, return DesignAndDetailResult with
            full bar and stirrup layouts. If False, return ComplianceReport
            with design checks only.

    Returns:
        DesignAndDetailResult if include_detailing=True (single case or envelope)
        ComplianceReport if include_detailing=False (multi-case analysis)

    Examples:
        >>> # Simple usage with dataclasses
        >>> from structural_lib.services.api import (
        ...     BeamInput, BeamGeometryInput, MaterialsInput, LoadsInput,
        ...     design_from_input
        ... )
        >>> beam = BeamInput(
        ...     beam_id="B1",
        ...     story="GF",
        ...     geometry=BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000),
        ...     materials=MaterialsInput.m25_fe500(),
        ...     loads=LoadsInput(mu_knm=150, vu_kn=80),
        ... )
        >>> result = design_from_input(beam)
        >>> print(result.summary())

        >>> # From JSON file
        >>> beam = BeamInput.from_json_file("inputs/beam_b1.json")
        >>> result = design_from_input(beam)

        >>> # Multi-case analysis without detailing
        >>> beam = BeamInput(
        ...     beam_id="B2",
        ...     story="1F",
        ...     geometry=BeamGeometryInput(b_mm=300, D_mm=600, span_mm=6000),
        ...     materials=MaterialsInput.m30_fe500(),
        ...     load_cases=[
        ...         LoadCaseInput("1.5DL+1.5LL", mu_knm=200, vu_kn=100),
        ...         LoadCaseInput("1.2DL+1.6LL+EQ", mu_knm=220, vu_kn=110),
        ...     ],
        ... )
        >>> report = design_from_input(beam, include_detailing=False)
        >>> print(f"Governing case: {report.governing_case_id}")

    See Also:
        - BeamInput: Complete input dataclass with helper methods
        - BeamGeometryInput: Geometry with validation
        - MaterialsInput: Material grades with factory methods
        - design_and_detail_beam_is456: Low-level parameter-based API
    """
    geom = beam.geometry
    mat = beam.materials
    config = beam.detailing_config

    # Get effective depth
    d_mm = geom.effective_depth

    if beam.has_multiple_cases:
        # Multi-case analysis
        cases = [
            {
                "case_id": case.case_id,
                "mu_knm": case.mu_knm,
                "vu_kn": case.vu_kn,
            }
            for case in beam.load_cases
        ]

        report = check_beam_is456(
            units=beam.units,
            cases=cases,
            b_mm=geom.b_mm,
            D_mm=geom.D_mm,
            d_mm=d_mm,
            fck_nmm2=mat.fck_nmm2,
            fy_nmm2=mat.fy_nmm2,
            d_dash_mm=config.d_dash_mm,
            asv_mm2=config.asv_mm2,
        )

        if not include_detailing:
            return report

        # Create detailing using governing case
        governing = report.governing_case_id
        governing_case = next(
            (c for c in report.cases if c.case_id == governing),
            report.cases[0] if report.cases else None,
        )

        if governing_case is None:
            raise ValueError("No valid load cases in report")

        return design_and_detail_beam_is456(
            units=beam.units,
            beam_id=beam.beam_id,
            story=beam.story,
            span_mm=geom.span_mm,
            mu_knm=governing_case.mu_knm,
            vu_kn=governing_case.vu_kn,
            b_mm=geom.b_mm,
            D_mm=geom.D_mm,
            d_mm=d_mm,
            cover_mm=geom.cover_mm,
            fck_nmm2=mat.fck_nmm2,
            fy_nmm2=mat.fy_nmm2,
            d_dash_mm=config.d_dash_mm,
            asv_mm2=config.asv_mm2,
            stirrup_dia_mm=config.stirrup_dia_mm,
            stirrup_spacing_support_mm=config.stirrup_spacing_start_mm,
            stirrup_spacing_mid_mm=config.stirrup_spacing_mid_mm,
            is_seismic=config.is_seismic,
        )

    # Single case
    if beam.loads is None:
        raise ValueError("BeamInput requires either 'loads' or 'load_cases'")

    return design_and_detail_beam_is456(
        units=beam.units,
        beam_id=beam.beam_id,
        story=beam.story,
        span_mm=geom.span_mm,
        mu_knm=beam.loads.mu_knm,
        vu_kn=beam.loads.vu_kn,
        b_mm=geom.b_mm,
        D_mm=geom.D_mm,
        d_mm=d_mm,
        cover_mm=geom.cover_mm,
        fck_nmm2=mat.fck_nmm2,
        fy_nmm2=mat.fy_nmm2,
        d_dash_mm=config.d_dash_mm,
        asv_mm2=config.asv_mm2,
        stirrup_dia_mm=config.stirrup_dia_mm,
        stirrup_spacing_support_mm=config.stirrup_spacing_start_mm,
        stirrup_spacing_mid_mm=config.stirrup_spacing_mid_mm,
        is_seismic=config.is_seismic,
    )
