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
"""

from __future__ import annotations

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
