"""Report generation module for beam design results.

This module generates human-readable reports from job outputs.

Design constraints:
- Deterministic outputs (same input → same output)
- stdlib only (no external dependencies)
- Explicit error handling for missing/malformed inputs

Usage:
    from structural_lib import report

    # Load from job output folder
    data = report.load_report_data("./output/")

    # Generate JSON summary
    json_output = report.export_json(data)

    # Generate HTML report
    html_output = report.export_html(data)

    # Get critical set (sorted by utilization)
    critical = report.get_critical_set(data, top=10)
    csv_output = report.export_critical_csv(critical)
    html_table = report.export_critical_html(critical)
"""

from __future__ import annotations

import csv
import html
import io
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import report_svg


@dataclass
class ReportData:
    """Container for report input data.

    Combines job spec (geometry/materials) with design results.
    """

    job_id: str
    code: str
    units: str
    beam: Dict[str, Any]
    cases: List[Dict[str, Any]]
    results: Dict[str, Any]

    # Computed fields
    is_ok: bool = False
    governing_case_id: str = ""
    governing_utilization: float = 0.0


@dataclass
class CriticalCase:
    """A single case entry for critical set output.

    Attributes:
        case_id: Load case identifier
        utilization: Governing utilization ratio (0.0 to 1.0+)
        flexure_util: Flexure utilization ratio
        shear_util: Shear utilization ratio
        is_ok: Whether design passes all checks
        json_path: Source path in results JSON for traceability
    """

    case_id: str
    utilization: float
    flexure_util: float
    shear_util: float
    is_ok: bool
    json_path: str = ""


@dataclass
class SanityCheck:
    """A single input sanity check result."""

    field: str
    value: Optional[float]
    status: str
    message: str
    json_path: str


def load_report_data(
    output_dir: str | Path,
    *,
    job_path: Optional[str | Path] = None,
    results_path: Optional[str | Path] = None,
) -> ReportData:
    """Load report data from job output folder.

    Args:
        output_dir: Path to job output folder (e.g., "./output/")
        job_path: Override path to job.json (default: output_dir/inputs/job.json)
        results_path: Override path to design_results.json
                     (default: output_dir/design/design_results.json)

    Returns:
        ReportData with combined job spec and design results

    Raises:
        FileNotFoundError: If required files are missing
        ValueError: If files are malformed
    """
    out_root = Path(output_dir)

    # Resolve paths
    job_file = Path(job_path) if job_path else out_root / "inputs" / "job.json"
    results_file = (
        Path(results_path)
        if results_path
        else out_root / "design" / "design_results.json"
    )

    # Load job spec
    if not job_file.exists():
        raise FileNotFoundError(f"Job file not found: {job_file}")

    try:
        job_text = job_file.read_text(encoding="utf-8")
        job = json.loads(job_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in job file: {e}") from e

    if not isinstance(job, dict):
        raise ValueError("Job file must contain a JSON object")

    # Validate required job fields
    beam = job.get("beam")
    if not isinstance(beam, dict):
        raise ValueError("Job file missing 'beam' object")

    cases = job.get("cases")
    if not isinstance(cases, list):
        raise ValueError("Job file missing 'cases' array")

    # Load design results
    if not results_file.exists():
        raise FileNotFoundError(f"Results file not found: {results_file}")

    try:
        results_text = results_file.read_text(encoding="utf-8")
        results = json.loads(results_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in results file: {e}") from e

    if not isinstance(results, dict):
        raise ValueError("Results file must contain a JSON object")

    # Extract job metadata (prefer from results, fallback to job file)
    job_meta = results.get("job", {})
    job_id = str(job_meta.get("job_id", job.get("job_id", "")))
    code = str(job_meta.get("code", job.get("code", "")))
    units = str(job_meta.get("units", job.get("units", "")))

    return ReportData(
        job_id=job_id,
        code=code,
        units=units,
        beam=beam,
        cases=cases,
        results=results,
        is_ok=bool(results.get("is_ok", False)),
        governing_case_id=str(results.get("governing_case_id", "")),
        governing_utilization=float(results.get("governing_utilization", 0.0)),
    )


def _safe_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _make_sanity_check(
    *,
    field: str,
    value: Optional[float],
    status: str,
    message: str,
    json_path: str,
) -> SanityCheck:
    return SanityCheck(
        field=field,
        value=value,
        status=status,
        message=message,
        json_path=json_path,
    )


def get_input_sanity(data: ReportData) -> List[SanityCheck]:
    """Evaluate input sanity checks for geometry/material inputs."""
    beam = data.beam or {}

    b_mm = _safe_float(beam.get("b_mm"))
    D_mm = _safe_float(beam.get("D_mm"))
    d_mm = _safe_float(beam.get("d_mm"))
    d_dash_mm = _safe_float(beam.get("d_dash_mm"))
    fck_nmm2 = _safe_float(beam.get("fck_nmm2"))
    fy_nmm2 = _safe_float(beam.get("fy_nmm2"))
    asv_mm2 = _safe_float(beam.get("asv_mm2"))

    checks: List[SanityCheck] = []

    def check_positive(field: str, value: Optional[float], json_path: str) -> None:
        if value is None:
            checks.append(
                _make_sanity_check(
                    field=field,
                    value=None,
                    status="WARN",
                    message="missing value",
                    json_path=json_path,
                )
            )
            return
        if value <= 0:
            checks.append(
                _make_sanity_check(
                    field=field,
                    value=value,
                    status="WARN",
                    message="must be > 0",
                    json_path=json_path,
                )
            )
        else:
            checks.append(
                _make_sanity_check(
                    field=field,
                    value=value,
                    status="OK",
                    message="within expected range",
                    json_path=json_path,
                )
            )

    check_positive("b_mm", b_mm, "beam.b_mm")
    check_positive("D_mm", D_mm, "beam.D_mm")

    # d_mm should be > 0 and <= D_mm
    if d_mm is None:
        checks.append(
            _make_sanity_check(
                field="d_mm",
                value=None,
                status="WARN",
                message="missing value",
                json_path="beam.d_mm",
            )
        )
    elif d_mm <= 0:
        checks.append(
            _make_sanity_check(
                field="d_mm",
                value=d_mm,
                status="WARN",
                message="must be > 0",
                json_path="beam.d_mm",
            )
        )
    elif D_mm is None:
        checks.append(
            _make_sanity_check(
                field="d_mm",
                value=d_mm,
                status="WARN",
                message="cannot compare to D_mm (missing D_mm)",
                json_path="beam.d_mm",
            )
        )
    elif d_mm > D_mm:
        checks.append(
            _make_sanity_check(
                field="d_mm",
                value=d_mm,
                status="WARN",
                message="d_mm should be <= D_mm",
                json_path="beam.d_mm",
            )
        )
    else:
        checks.append(
            _make_sanity_check(
                field="d_mm",
                value=d_mm,
                status="OK",
                message="within expected range",
                json_path="beam.d_mm",
            )
        )

    # b/D ratio sanity (b_over_D)
    if b_mm is None or D_mm is None or D_mm == 0:
        checks.append(
            _make_sanity_check(
                field="b_over_D",
                value=None,
                status="WARN",
                message="cannot compute b/D ratio",
                json_path="beam.b_mm",
            )
        )
    else:
        ratio = b_mm / D_mm
        if ratio < 0.2 or ratio > 1.0:
            checks.append(
                _make_sanity_check(
                    field="b_over_D",
                    value=ratio,
                    status="WARN",
                    message="b/D ratio outside expected range (0.20 to 1.00)",
                    json_path="beam.b_mm",
                )
            )
        else:
            checks.append(
                _make_sanity_check(
                    field="b_over_D",
                    value=ratio,
                    status="OK",
                    message="b/D ratio within expected range",
                    json_path="beam.b_mm",
                )
            )

    # Material strengths
    if fck_nmm2 is None:
        checks.append(
            _make_sanity_check(
                field="fck_nmm2",
                value=None,
                status="WARN",
                message="missing value",
                json_path="beam.fck_nmm2",
            )
        )
    elif fck_nmm2 < 15 or fck_nmm2 > 60:
        checks.append(
            _make_sanity_check(
                field="fck_nmm2",
                value=fck_nmm2,
                status="WARN",
                message="outside expected range (15 to 60)",
                json_path="beam.fck_nmm2",
            )
        )
    else:
        checks.append(
            _make_sanity_check(
                field="fck_nmm2",
                value=fck_nmm2,
                status="OK",
                message="within expected range",
                json_path="beam.fck_nmm2",
            )
        )

    if fy_nmm2 is None:
        checks.append(
            _make_sanity_check(
                field="fy_nmm2",
                value=None,
                status="WARN",
                message="missing value",
                json_path="beam.fy_nmm2",
            )
        )
    elif fy_nmm2 < 250 or fy_nmm2 > 600:
        checks.append(
            _make_sanity_check(
                field="fy_nmm2",
                value=fy_nmm2,
                status="WARN",
                message="outside expected range (250 to 600)",
                json_path="beam.fy_nmm2",
            )
        )
    else:
        checks.append(
            _make_sanity_check(
                field="fy_nmm2",
                value=fy_nmm2,
                status="OK",
                message="within expected range",
                json_path="beam.fy_nmm2",
            )
        )

    # d_dash_mm should be > 0 and < d_mm (if provided)
    if d_dash_mm is None:
        checks.append(
            _make_sanity_check(
                field="d_dash_mm",
                value=None,
                status="WARN",
                message="missing value",
                json_path="beam.d_dash_mm",
            )
        )
    elif d_dash_mm <= 0:
        checks.append(
            _make_sanity_check(
                field="d_dash_mm",
                value=d_dash_mm,
                status="WARN",
                message="must be > 0",
                json_path="beam.d_dash_mm",
            )
        )
    elif d_mm is not None and d_dash_mm >= d_mm:
        checks.append(
            _make_sanity_check(
                field="d_dash_mm",
                value=d_dash_mm,
                status="WARN",
                message="d_dash_mm should be < d_mm",
                json_path="beam.d_dash_mm",
            )
        )
    else:
        checks.append(
            _make_sanity_check(
                field="d_dash_mm",
                value=d_dash_mm,
                status="OK",
                message="within expected range",
                json_path="beam.d_dash_mm",
            )
        )

    # asv_mm2 (shear reinforcement area)
    if asv_mm2 is None:
        checks.append(
            _make_sanity_check(
                field="asv_mm2",
                value=None,
                status="WARN",
                message="missing value",
                json_path="beam.asv_mm2",
            )
        )
    elif asv_mm2 <= 0:
        checks.append(
            _make_sanity_check(
                field="asv_mm2",
                value=asv_mm2,
                status="WARN",
                message="must be > 0",
                json_path="beam.asv_mm2",
            )
        )
    else:
        checks.append(
            _make_sanity_check(
                field="asv_mm2",
                value=asv_mm2,
                status="OK",
                message="within expected range",
                json_path="beam.asv_mm2",
            )
        )

    return checks


def export_json(data: ReportData, *, indent: int = 2) -> str:
    """Export report data as JSON string.

    Args:
        data: ReportData to export
        indent: JSON indentation (default: 2)

    Returns:
        JSON string with sorted keys for determinism
    """
    input_sanity = [
        {
            "field": item.field,
            "value": item.value,
            "status": item.status,
            "message": item.message,
            "json_path": item.json_path,
        }
        for item in get_input_sanity(data)
    ]
    output = {
        "job_id": data.job_id,
        "code": data.code,
        "units": data.units,
        "is_ok": data.is_ok,
        "governing_case_id": data.governing_case_id,
        "governing_utilization": data.governing_utilization,
        "beam": data.beam,
        "cases": data.results.get("cases", []),
        "summary": data.results.get("summary", {}),
        "input_sanity": input_sanity,
    }
    return json.dumps(output, indent=indent, sort_keys=True, ensure_ascii=False)


def _format_sanity_value(item: SanityCheck) -> str:
    if item.value is None:
        return "NA"
    if item.field == "b_over_D":
        return f"{item.value:.3f}"
    if item.field in ("fck_nmm2", "fy_nmm2"):
        return f"{item.value:.0f}"
    if item.field.endswith("_mm") or item.field.endswith("_mm2"):
        return f"{item.value:.1f}"
    return f"{item.value:.2f}"


def _render_sanity_table(items: List[SanityCheck]) -> str:
    rows = []
    for item in items:
        status_class = "ok" if item.status == "OK" else "warn"
        value = _format_sanity_value(item)
        message = html.escape(item.message)
        field = html.escape(item.field)
        json_path = html.escape(item.json_path)
        rows.append(
            f"""        <tr class="sanity-{status_class}" data-source="{json_path}">
            <td>{field}</td>
            <td>{value}</td>
            <td>{item.status}</td>
            <td>{message}</td>
        </tr>"""
        )

    rows_joined = "\n".join(rows)
    return f"""<table class="sanity-table">
        <thead>
            <tr>
                <th>Field</th>
                <th>Value</th>
                <th>Status</th>
                <th>Notes</th>
            </tr>
        </thead>
        <tbody>
{rows_joined}
        </tbody>
    </table>"""


def export_html(data: ReportData) -> str:
    """Export report data as HTML string (Phase 1 visuals)."""
    status = "✓ PASS" if data.is_ok else "✗ FAIL"
    job_id = html.escape(data.job_id)
    code = html.escape(data.code)
    svg = report_svg.render_section_svg_from_beam(data.beam)
    sanity_items = get_input_sanity(data)
    sanity_table = _render_sanity_table(sanity_items)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Beam Design Report - {job_id}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 20px; }}
        h1, h2 {{ color: #333; }}
        .summary {{ margin-bottom: 20px; }}
        .section {{ margin: 20px 0; }}
        .sanity-table {{ border-collapse: collapse; width: 100%; max-width: 900px; }}
        .sanity-table th, .sanity-table td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
        .sanity-table th {{ background: #f5f5f5; font-weight: 600; }}
        .sanity-ok {{ background: #f7fff7; }}
        .sanity-warn {{ background: #fff8e1; }}
        .svg-wrap {{ border: 1px solid #eee; padding: 10px; display: inline-block; }}
    </style>
</head>
<body>
    <h1>Beam Design Report</h1>
    <div class="summary">
        <p><strong>Job ID:</strong> {job_id}</p>
        <p><strong>Code:</strong> {code}</p>
        <p><strong>Status:</strong> {status}</p>
        <p><strong>Governing Utilization:</strong> {data.governing_utilization:.2%}</p>
    </div>
    <div class="section">
        <h2>Cross-Section SVG</h2>
        <div class="svg-wrap">{svg}</div>
    </div>
    <div class="section">
        <h2>Input Sanity Heatmap</h2>
        {sanity_table}
    </div>
    <p><em>Full report implementation in V08.</em></p>
</body>
</html>
"""


# =============================================================================
# Critical Set Functions (V03)
# =============================================================================


def get_critical_set(
    data: ReportData,
    *,
    top: Optional[int] = None,
) -> List[CriticalCase]:
    """Extract cases sorted by utilization (highest first).

    Args:
        data: ReportData containing design results
        top: Limit to top N cases (None = all cases)

    Returns:
        List of CriticalCase sorted by utilization descending
    """
    cases_data = data.results.get("cases", [])
    critical_cases: List[CriticalCase] = []

    for idx, case in enumerate(cases_data):
        if not isinstance(case, dict):
            continue

        case_id = str(case.get("case_id", f"case_{idx}"))

        # Extract utilization values
        utils = case.get("utilizations", {})
        if not isinstance(utils, dict):
            utils = {}

        # Governing utilization (max of flexure and shear)
        flexure_util = float(utils.get("flexure", 0.0))
        shear_util = float(utils.get("shear", 0.0))
        governing_util = float(
            case.get("governing_utilization", max(flexure_util, shear_util))
        )

        is_ok = bool(case.get("is_ok", False))
        json_path = f"cases[{idx}]"

        critical_cases.append(
            CriticalCase(
                case_id=case_id,
                utilization=governing_util,
                flexure_util=flexure_util,
                shear_util=shear_util,
                is_ok=is_ok,
                json_path=json_path,
            )
        )

    # Sort by utilization descending (highest first)
    critical_cases.sort(key=lambda c: c.utilization, reverse=True)

    # Apply top N filter
    if top is not None and top > 0:
        critical_cases = critical_cases[:top]

    return critical_cases


def export_critical_csv(cases: List[CriticalCase]) -> str:
    """Export critical set as CSV string.

    Args:
        cases: List of CriticalCase (already sorted)

    Returns:
        CSV string with header row
    """
    output = io.StringIO()
    fieldnames = [
        "case_id",
        "utilization",
        "flexure_util",
        "shear_util",
        "is_ok",
        "json_path",
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for case in cases:
        writer.writerow(
            {
                "case_id": case.case_id,
                "utilization": f"{case.utilization:.4f}",
                "flexure_util": f"{case.flexure_util:.4f}",
                "shear_util": f"{case.shear_util:.4f}",
                "is_ok": "TRUE" if case.is_ok else "FALSE",
                "json_path": case.json_path,
            }
        )

    return output.getvalue()


def export_critical_html(
    cases: List[CriticalCase],
    *,
    title: str = "Critical Set - Utilization Summary",
) -> str:
    """Export critical set as HTML table with utilization bars.

    Args:
        cases: List of CriticalCase (already sorted)
        title: Table title

    Returns:
        HTML string with styled table
    """
    # Build table rows
    rows_html = []
    for case in cases:
        # Utilization bar width (cap at 100% for display)
        bar_width = min(case.utilization * 100, 100)
        bar_color = "#28a745" if case.is_ok else "#dc3545"  # green or red

        status_badge = (
            '<span class="badge pass">✓ PASS</span>'
            if case.is_ok
            else '<span class="badge fail">✗ FAIL</span>'
        )

        row = f"""        <tr data-source="{case.json_path}">
            <td>{case.case_id}</td>
            <td>
                <div class="util-bar-container">
                    <div class="util-bar" style="width: {bar_width:.1f}%; background: {bar_color};"></div>
                    <span class="util-value">{case.utilization:.2%}</span>
                </div>
            </td>
            <td>{case.flexure_util:.2%}</td>
            <td>{case.shear_util:.2%}</td>
            <td>{status_badge}</td>
        </tr>"""
        rows_html.append(row)

    rows_joined = "\n".join(rows_html)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; max-width: 900px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
        th {{ background: #f5f5f5; font-weight: 600; }}
        tr:hover {{ background: #f9f9f9; }}
        .util-bar-container {{ position: relative; width: 120px; height: 20px; background: #eee; border-radius: 3px; }}
        .util-bar {{ height: 100%; border-radius: 3px; }}
        .util-value {{ position: absolute; top: 0; left: 0; right: 0; text-align: center; line-height: 20px; font-size: 12px; font-weight: 500; }}
        .badge {{ padding: 2px 8px; border-radius: 3px; font-size: 12px; font-weight: 500; }}
        .badge.pass {{ background: #d4edda; color: #155724; }}
        .badge.fail {{ background: #f8d7da; color: #721c24; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <table>
        <thead>
            <tr>
                <th>Case ID</th>
                <th>Utilization</th>
                <th>Flexure</th>
                <th>Shear</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
{rows_joined}
        </tbody>
    </table>
</body>
</html>
"""
