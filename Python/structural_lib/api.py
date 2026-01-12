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

from . import (
    bbs,
    beam_pipeline,
    compliance,
    detailing,
    ductile,
    job_runner,
    report,
    serviceability,
)
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
from .calculation_report import (
    CalculationReport,
    InputSection,
    ProjectInfo,
    ResultSection,
    generate_calculation_report,
)
from .costing import CostProfile
from .data_types import (
    ComplianceCaseResult,
    ComplianceReport,
    CrackWidthParams,
    DeflectionParams,
    ValidationReport,
)
from .inputs import (
    BeamGeometryInput,
    BeamInput,
    DetailingConfigInput,
    LoadCaseInput,
    LoadsInput,
    MaterialsInput,
)
from .insights import cost_optimization, design_suggestions

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
    "check_deflection_span_depth",
    "check_crack_width",
    "check_compliance_report",
    # Smart features
    "optimize_beam_cost",
    "suggest_beam_design_improvements",
    "smart_analyze_design",
]


def _require_is456_units(units: str) -> None:
    beam_pipeline.validate_units(units)


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
    from . import dxf_export as _dxf_export

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
    ast_required = design_result.flexure.ast_required
    asc_required = design_result.flexure.asc_required

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

    from .insights import SmartDesigner

    _require_is456_units(units)

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
        >>> from structural_lib.api import (
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
