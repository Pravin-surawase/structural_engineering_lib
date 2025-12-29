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
import io
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


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


def export_json(data: ReportData, *, indent: int = 2) -> str:
    """Export report data as JSON string.

    Args:
        data: ReportData to export
        indent: JSON indentation (default: 2)

    Returns:
        JSON string with sorted keys for determinism
    """
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
    }
    return json.dumps(output, indent=indent, sort_keys=True, ensure_ascii=False)


def export_html(data: ReportData) -> str:
    """Export report data as HTML string.

    Placeholder implementation for V08.

    Args:
        data: ReportData to export

    Returns:
        HTML string
    """
    # Minimal placeholder - V08 will implement full HTML
    status = "✓ PASS" if data.is_ok else "✗ FAIL"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Beam Design Report - {data.job_id}</title>
</head>
<body>
    <h1>Beam Design Report</h1>
    <p><strong>Job ID:</strong> {data.job_id}</p>
    <p><strong>Code:</strong> {data.code}</p>
    <p><strong>Status:</strong> {status}</p>
    <p><strong>Governing Utilization:</strong> {data.governing_utilization:.2%}</p>
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
