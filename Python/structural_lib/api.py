"""
Module:       api
Description:  Public facing API functions
"""

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import json

from typing import Any, Dict, Optional, Sequence, Union

from . import bbs
from . import beam_pipeline
from . import compliance
from . import detailing
from . import ductile
from . import job_runner
from . import report
from . import serviceability
from .types import ComplianceCaseResult, ComplianceReport, ValidationReport

__all__ = [
    "get_library_version",
    "validate_job_spec",
    "validate_design_results",
    "compute_detailing",
    "compute_bbs",
    "export_bbs",
    "compute_dxf",
    "compute_report",
    "compute_critical",
    "check_beam_ductility",
    "check_deflection_span_depth",
    "check_crack_width",
    "check_compliance_report",
    "design_beam_is456",
    "check_beam_is456",
    "detail_beam_is456",
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


def validate_job_spec(path: Union[str, Path]) -> ValidationReport:
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


def _beam_has_geometry(beam: Dict[str, Any]) -> bool:
    geom = beam.get("geometry")
    if isinstance(geom, dict):
        if all(k in geom for k in ("b_mm", "D_mm", "d_mm")):
            return True
        if all(k in geom for k in ("b", "D", "d")):
            return True
    return all(k in beam for k in ("b", "D", "d"))


def _beam_has_materials(beam: Dict[str, Any]) -> bool:
    mats = beam.get("materials")
    if isinstance(mats, dict):
        return any(k in mats for k in ("fck_nmm2", "fck")) and any(
            k in mats for k in ("fy_nmm2", "fy")
        )
    return any(k in beam for k in ("fck_nmm2", "fck")) and any(
        k in beam for k in ("fy_nmm2", "fy")
    )


def _beam_has_loads(beam: Dict[str, Any]) -> bool:
    loads = beam.get("loads")
    if isinstance(loads, dict):
        return any(k in loads for k in ("mu_knm", "Mu")) and any(
            k in loads for k in ("vu_kn", "Vu")
        )
    return any(k in beam for k in ("mu_knm", "Mu")) and any(
        k in beam for k in ("vu_kn", "Vu")
    )


def validate_design_results(path: Union[str, Path]) -> ValidationReport:
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


def _extract_beam_params_from_schema(beam: Dict[str, Any]) -> Dict[str, Any]:
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
) -> Dict[str, Any]:
    zones = ("start", "mid", "end")

    def _bars_to_dict(bars: list[detailing.BarArrangement]) -> list[Dict[str, Any]]:
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
    ) -> list[Dict[str, Any]]:
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
    design_results: Dict[str, Any],
    *,
    config: Optional[Dict[str, Any]] = None,
) -> list[detailing.BeamDetailingResult]:
    """Compute beam detailing results from design results JSON dict."""
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
    """Generate a bar bending schedule document from detailing results."""
    return bbs.generate_bbs_document(detailing_list, project_name=project_name)


def export_bbs(
    bbs_doc: bbs.BBSDocument,
    path: Union[str, Path],
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
    output: Union[str, Path],
    *,
    multi: bool = False,
    include_title_block: bool = False,
    title_block: Optional[Dict[str, Any]] = None,
    sheet_margin_mm: float = 20.0,
    title_block_width_mm: float = 120.0,
    title_block_height_mm: float = 40.0,
) -> Path:
    """Generate DXF drawings from detailing results."""
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
    source: Union[str, Path, Dict[str, Any]],
    *,
    format: str = "html",
    job_path: Optional[Union[str, Path]] = None,
    results_path: Optional[Union[str, Path]] = None,
    output_path: Optional[Union[str, Path]] = None,
    batch_threshold: int = 80,
) -> Union[str, Path, list[Path]]:
    """Generate report output from job outputs or design results."""
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
    job_out: Union[str, Path],
    *,
    top: int = 10,
    format: str = "csv",
    job_path: Optional[Union[str, Path]] = None,
    results_path: Optional[Union[str, Path]] = None,
    output_path: Optional[Union[str, Path]] = None,
) -> Union[str, Path]:
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
    base_allowable_ld: Optional[float] = None,
    mf_tension_steel: Optional[float] = None,
    mf_compression_steel: Optional[float] = None,
    mf_flanged: Optional[float] = None,
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
    limit_mm: Optional[float] = None,
    acr_mm: Optional[float] = None,
    cmin_mm: Optional[float] = None,
    h_mm: Optional[float] = None,
    x_mm: Optional[float] = None,
    epsilon_m: Optional[float] = None,
    fs_service_nmm2: Optional[float] = None,
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
    cases: Sequence[Dict[str, Any]],
    b_mm: float,
    D_mm: float,
    d_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    d_dash_mm: float = 50.0,
    asv_mm2: float = 100.0,
    pt_percent: Optional[float] = None,
    deflection_defaults: Optional[Dict[str, Any]] = None,
    crack_width_defaults: Optional[Dict[str, Any]] = None,
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
    pt_percent: Optional[float] = None,
    ast_mm2_for_shear: Optional[float] = None,
    deflection_params: Optional[Dict[str, Any]] = None,
    crack_width_params: Optional[Dict[str, Any]] = None,
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
    cases: Sequence[Dict[str, Any]],
    b_mm: float,
    D_mm: float,
    d_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    d_dash_mm: float = 50.0,
    asv_mm2: float = 100.0,
    pt_percent: Optional[float] = None,
    deflection_defaults: Optional[Dict[str, Any]] = None,
    crack_width_defaults: Optional[Dict[str, Any]] = None,
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
