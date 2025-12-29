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
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import ductile
from . import report_svg

_REPORT_CSS = """
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 20px; }
h1, h2 { color: #333; }
.summary { margin-bottom: 20px; }
.section { margin: 20px 0; }
.beam-section { margin-top: 30px; padding-top: 10px; border-top: 1px solid #e5e5e5; }
.index-table, .sanity-table, .scorecard-table, .units-table { border-collapse: collapse; width: 100%; max-width: 900px; }
.index-table th, .index-table td,
.sanity-table th, .sanity-table td,
.scorecard-table th, .scorecard-table td,
.units-table th, .units-table td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
.index-table th, .sanity-table th, .scorecard-table th, .units-table th { background: #f5f5f5; font-weight: 600; }
.sanity-ok, .scorecard-ok, .units-ok { background: #f7fff7; }
.sanity-warn, .scorecard-warn, .units-warn { background: #fff8e1; }
.svg-wrap { border: 1px solid #eee; padding: 10px; display: inline-block; }
.svg-legend { font-size: 12px; color: #555; margin-top: 6px; }
.svg-legend span { margin-right: 12px; }
.status-pass { color: #1b5e20; font-weight: 600; }
.status-fail { color: #b71c1c; font-weight: 600; }
.status-warn { color: #e65100; font-weight: 600; }
"""


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


@dataclass
class ScorecardItem:
    """A single stability scorecard item."""

    check: str
    status: str
    message: str
    json_path: str


@dataclass
class UnitsAlert:
    """A single units sentinel alert."""

    field: str
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


def _safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


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


def _case_utilization(case: Dict[str, Any]) -> float:
    util = case.get("governing_utilization")
    if util is not None:
        try:
            return float(util)
        except (TypeError, ValueError):
            return 0.0
    utils = case.get("utilizations", {})
    if isinstance(utils, dict) and utils:
        try:
            return max(float(v) for v in utils.values())
        except (TypeError, ValueError):
            return 0.0
    return 0.0


def _select_governing_case(data: ReportData) -> tuple[Optional[Dict[str, Any]], int]:
    cases_data = data.results.get("cases", [])
    if not isinstance(cases_data, list) or not cases_data:
        return None, -1

    if data.governing_case_id:
        for idx, case in enumerate(cases_data):
            if str(case.get("case_id", "")) == data.governing_case_id:
                return case, idx

    # Fallback: pick highest utilization (tie -> first)
    best_idx = 0
    best_util = _case_utilization(cases_data[0])
    for idx, case in enumerate(cases_data[1:], start=1):
        util = _case_utilization(case)
        if util > best_util:
            best_util = util
            best_idx = idx
    return cases_data[best_idx], best_idx


def get_stability_scorecard(data: ReportData) -> List[ScorecardItem]:
    """Generate stability scorecard flags from governing case results."""
    case, case_idx = _select_governing_case(data)
    items: List[ScorecardItem] = []

    if case is None:
        missing = "no cases available"
        items.extend(
            [
                ScorecardItem("over_reinforced", "INFO", missing, "cases[]"),
                ScorecardItem("min_ductility", "INFO", missing, "cases[]"),
                ScorecardItem("max_ductility", "INFO", missing, "cases[]"),
                ScorecardItem("shear_margin", "INFO", missing, "cases[]"),
                ScorecardItem(
                    "governing_utilization", "INFO", missing, "governing_utilization"
                ),
            ]
        )
        return items

    flexure = case.get("flexure", {}) if isinstance(case.get("flexure"), dict) else {}
    shear = case.get("shear", {}) if isinstance(case.get("shear"), dict) else {}

    section_type = str(flexure.get("section_type", "") or "")
    section_path = f"cases[{case_idx}].flexure.section_type"
    if not section_type:
        items.append(
            ScorecardItem(
                "over_reinforced",
                "INFO",
                "section_type missing",
                section_path,
            )
        )
    elif section_type == "OVER_REINFORCED":
        items.append(
            ScorecardItem(
                "over_reinforced",
                "WARN",
                "over-reinforced section",
                section_path,
            )
        )
    elif section_type == "BALANCED":
        items.append(
            ScorecardItem(
                "over_reinforced",
                "WARN",
                "balanced section (low ductility margin)",
                section_path,
            )
        )
    else:
        items.append(
            ScorecardItem(
                "over_reinforced",
                "OK",
                "under-reinforced section",
                section_path,
            )
        )

    pt_provided = _safe_float(flexure.get("pt_provided"))
    fck_nmm2 = _safe_float(data.beam.get("fck_nmm2"))
    fy_nmm2 = _safe_float(data.beam.get("fy_nmm2"))
    pt_path = f"cases[{case_idx}].flexure.pt_provided"

    if pt_provided is None or fck_nmm2 is None or fy_nmm2 is None:
        items.append(
            ScorecardItem(
                "min_ductility",
                "INFO",
                "missing pt_provided/fck/fy",
                pt_path,
            )
        )
        items.append(
            ScorecardItem(
                "max_ductility",
                "INFO",
                "missing pt_provided/fck/fy",
                pt_path,
            )
        )
    else:
        min_pt = ductile.get_min_tension_steel_percentage(fck_nmm2, fy_nmm2)
        max_pt = ductile.get_max_tension_steel_percentage()

        if pt_provided < min_pt:
            items.append(
                ScorecardItem(
                    "min_ductility",
                    "WARN",
                    f"pt_provided {pt_provided:.2f}% < min {min_pt:.2f}%",
                    pt_path,
                )
            )
        else:
            items.append(
                ScorecardItem(
                    "min_ductility",
                    "OK",
                    "min ductility OK",
                    pt_path,
                )
            )

        if pt_provided > max_pt:
            items.append(
                ScorecardItem(
                    "max_ductility",
                    "WARN",
                    f"pt_provided {pt_provided:.2f}% > max {max_pt:.2f}%",
                    pt_path,
                )
            )
        else:
            items.append(
                ScorecardItem(
                    "max_ductility",
                    "OK",
                    "max ductility OK",
                    pt_path,
                )
            )

    shear_path = f"cases[{case_idx}].shear.is_safe"
    shear_safe = shear.get("is_safe")
    shear_util = 0.0
    utils = case.get("utilizations", {})
    if isinstance(utils, dict):
        shear_util = _safe_float(utils.get("shear")) or 0.0

    if shear_safe is None:
        items.append(
            ScorecardItem(
                "shear_margin",
                "INFO",
                "shear result missing",
                shear_path,
            )
        )
    elif not bool(shear_safe):
        items.append(
            ScorecardItem(
                "shear_margin",
                "WARN",
                "shear check failed",
                shear_path,
            )
        )
    elif shear_util >= 0.9:
        items.append(
            ScorecardItem(
                "shear_margin",
                "WARN",
                "shear utilization high (>= 0.90)",
                f"cases[{case_idx}].utilizations.shear",
            )
        )
    else:
        items.append(
            ScorecardItem(
                "shear_margin",
                "OK",
                "shear margin OK",
                shear_path,
            )
        )

    if data.governing_utilization >= 0.9:
        items.append(
            ScorecardItem(
                "governing_utilization",
                "WARN",
                "overall utilization high (>= 0.90)",
                "governing_utilization",
            )
        )
    else:
        items.append(
            ScorecardItem(
                "governing_utilization",
                "OK",
                "overall utilization OK",
                "governing_utilization",
            )
        )

    return items


def get_units_sentinel(data: ReportData) -> List[UnitsAlert]:
    """Flag likely unit mismatches based on magnitude heuristics."""
    cases_data = data.results.get("cases", [])
    if not isinstance(cases_data, list) or not cases_data:
        return []

    alerts: List[UnitsAlert] = []

    mu_values = []
    vu_values = []
    for idx, case in enumerate(cases_data):
        if not isinstance(case, dict):
            continue
        mu_val = _safe_float(case.get("mu_knm"))
        vu_val = _safe_float(case.get("vu_kn"))
        if mu_val is not None:
            mu_values.append((idx, mu_val))
        if vu_val is not None:
            vu_values.append((idx, vu_val))

    # Only evaluate when values exist
    for idx, value in mu_values:
        if value < 5.0:
            alerts.append(
                UnitsAlert(
                    field="mu_knm",
                    status="WARN",
                    message=f"mu_knm unusually small ({value:.2f}); check units",
                    json_path=f"cases[{idx}].mu_knm",
                )
            )
        elif value > 1.0e5:
            alerts.append(
                UnitsAlert(
                    field="mu_knm",
                    status="WARN",
                    message=f"mu_knm unusually large ({value:.2f}); check units",
                    json_path=f"cases[{idx}].mu_knm",
                )
            )

    for idx, value in vu_values:
        if value < 5.0:
            alerts.append(
                UnitsAlert(
                    field="vu_kn",
                    status="WARN",
                    message=f"vu_kn unusually small ({value:.2f}); check units",
                    json_path=f"cases[{idx}].vu_kn",
                )
            )
        elif value > 1.0e4:
            alerts.append(
                UnitsAlert(
                    field="vu_kn",
                    status="WARN",
                    message=f"vu_kn unusually large ({value:.2f}); check units",
                    json_path=f"cases[{idx}].vu_kn",
                )
            )

    return alerts


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
    stability_scorecard = [
        {
            "check": item.check,
            "status": item.status,
            "message": item.message,
            "json_path": item.json_path,
        }
        for item in get_stability_scorecard(data)
    ]
    units_sentinel = [
        {
            "field": item.field,
            "status": item.status,
            "message": item.message,
            "json_path": item.json_path,
        }
        for item in get_units_sentinel(data)
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
        "stability_scorecard": stability_scorecard,
        "units_sentinel": units_sentinel,
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


def _render_scorecard_table(items: List[ScorecardItem]) -> str:
    rows = []
    for item in items:
        status_class = "ok" if item.status == "OK" else "warn"
        message = html.escape(item.message)
        check = html.escape(item.check)
        json_path = html.escape(item.json_path)
        rows.append(
            f"""        <tr class="scorecard-{status_class}" data-source="{json_path}">
            <td>{check}</td>
            <td>{item.status}</td>
            <td>{message}</td>
        </tr>"""
        )

    rows_joined = "\n".join(rows)
    return f"""<table class="scorecard-table">
        <thead>
            <tr>
                <th>Check</th>
                <th>Status</th>
                <th>Notes</th>
            </tr>
        </thead>
        <tbody>
{rows_joined}
        </tbody>
    </table>"""


def _render_units_table(items: List[UnitsAlert]) -> str:
    if not items:
        return "<p>No unit anomalies detected.</p>"

    rows = []
    for item in items:
        status_class = "ok" if item.status == "OK" else "warn"
        message = html.escape(item.message)
        field = html.escape(item.field)
        json_path = html.escape(item.json_path)
        rows.append(
            f"""        <tr class="units-{status_class}" data-source="{json_path}">
            <td>{field}</td>
            <td>{item.status}</td>
            <td>{message}</td>
        </tr>"""
        )

    rows_joined = "\n".join(rows)
    return f"""<table class="units-table">
        <thead>
            <tr>
                <th>Field</th>
                <th>Status</th>
                <th>Notes</th>
            </tr>
        </thead>
        <tbody>
{rows_joined}
        </tbody>
    </table>"""


def _wrap_html(title: str, body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{html.escape(title)}</title>
    <style>{_REPORT_CSS}</style>
</head>
<body>
{body_html}
</body>
</html>
"""


def _render_report_sections(data: ReportData) -> str:
    status = "✓ PASS" if data.is_ok else "✗ FAIL"
    status_class = "status-pass" if data.is_ok else "status-fail"
    limit_note = ""
    if data.is_ok and data.governing_utilization >= 0.9:
        limit_note = (
            "\n    <p><strong>Limit status:</strong> "
            '<span class="status-warn">Near limit (>= 0.90)</span></p>'
        )
    job_id = html.escape(data.job_id)
    code = html.escape(data.code)
    svg = report_svg.render_section_svg_from_beam(data.beam)
    sanity_table = _render_sanity_table(get_input_sanity(data))
    scorecard_table = _render_scorecard_table(get_stability_scorecard(data))
    units_table = _render_units_table(get_units_sentinel(data))

    return f"""<div class="summary">
    <p><strong>Job ID:</strong> {job_id}</p>
    <p><strong>Code:</strong> {code}</p>
    <p><strong>Status:</strong> <span class="{status_class}">{status}</span></p>
    <p><strong>Governing Utilization:</strong> {data.governing_utilization:.2%}</p>{limit_note}
</div>
<div class="section">
    <h2>Cross-Section SVG</h2>
    <div class="svg-wrap">{svg}</div>
    <div class="svg-legend"><span>d = effective depth</span><span>d&#39; = compression cover</span></div>
</div>
<div class="section">
    <h2>Input Sanity Heatmap</h2>
    {sanity_table}
</div>
<div class="section">
    <h2>Stability Scorecard</h2>
    {scorecard_table}
</div>
<div class="section">
    <h2>Units Sentinel</h2>
    {units_table}
</div>"""


def _render_beam_section(
    data: ReportData, *, heading: str, section_id: Optional[str] = None
) -> str:
    anchor = f' id="{section_id}"' if section_id else ""
    return f"""<section class="beam-section"{anchor}>
    <h2>{html.escape(heading)}</h2>
    {_render_report_sections(data)}
</section>"""


def export_html(data: ReportData) -> str:
    """Export report data as HTML string (Phase 1 visuals)."""
    body = f"""<h1>Beam Design Report</h1>
{_render_report_sections(data)}
<p><em>Generated by structural_lib report.</em></p>"""
    return _wrap_html(f"Beam Design Report - {data.job_id}", body)


# =============================================================================
# Design Results Reporting (V08)
# =============================================================================


def load_design_results(path: str | Path) -> Dict[str, Any]:
    """Load design results JSON (multi-beam output)."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Design results file not found: {p}")

    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in design results: {e}") from e

    if not isinstance(payload, dict):
        raise ValueError("Design results must contain a JSON object")
    beams = payload.get("beams")
    if not isinstance(beams, list):
        raise ValueError("Design results missing 'beams' array")
    return payload


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip())
    slug = slug.strip("_")
    return slug or "beam"


def _build_beam_index(beams: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: Dict[str, int] = {}
    indexed: List[Dict[str, Any]] = []

    for idx, beam in enumerate(beams):
        beam_id = str(beam.get("beam_id", "") or f"Beam_{idx + 1}")
        story = str(beam.get("story", "") or "")
        label = f"{story}/{beam_id}" if story else beam_id

        base_slug = _safe_slug(label)
        count = seen.get(base_slug, 0)
        seen[base_slug] = count + 1
        slug = base_slug if count == 0 else f"{base_slug}-{count + 1}"

        indexed.append({"beam": beam, "label": label, "slug": slug})

    return indexed


def _beam_report_data_from_design(
    beam: Dict[str, Any], *, code: str, units: str
) -> ReportData:
    geometry: Dict[str, Any] = _safe_dict(beam.get("geometry"))
    materials: Dict[str, Any] = _safe_dict(beam.get("materials"))
    loads: Dict[str, Any] = _safe_dict(beam.get("loads"))
    flexure: Dict[str, Any] = _safe_dict(beam.get("flexure"))
    shear: Dict[str, Any] = _safe_dict(beam.get("shear"))
    serviceability: Dict[str, Any] = _safe_dict(beam.get("serviceability"))

    beam_id = str(beam.get("beam_id", "") or "")
    story = str(beam.get("story", "") or "")
    job_id = f"{story}/{beam_id}" if story else beam_id

    beam_info = {
        **geometry,
        **materials,
        "beam_id": beam_id,
        "story": story,
    }

    util_flexure = _safe_float(flexure.get("utilization"))
    util_shear = _safe_float(shear.get("utilization"))
    utilizations: Dict[str, float] = {}
    if util_flexure is not None:
        utilizations["flexure"] = util_flexure
    if util_shear is not None:
        utilizations["shear"] = util_shear

    defl_util = _safe_float(serviceability.get("deflection_utilization"))
    crack_util = _safe_float(serviceability.get("crack_width_utilization"))
    if defl_util is not None:
        utilizations["deflection"] = defl_util
    if crack_util is not None:
        utilizations["crack_width"] = crack_util

    ast_required = _safe_float(flexure.get("ast_required_mm2"))
    b_mm = _safe_float(geometry.get("b_mm"))
    d_mm = _safe_float(geometry.get("d_mm"))
    pt_est = None
    if ast_required is not None and b_mm and d_mm:
        pt_est = 100.0 * ast_required / (b_mm * d_mm)

    case_id = str(loads.get("case_id", "") or beam_id or "CASE_1")
    governing_util = _safe_float(
        beam.get("governing_utilization")
    ) or _case_utilization({"utilizations": utilizations})

    case = {
        "case_id": case_id,
        "mu_knm": loads.get("mu_knm"),
        "vu_kn": loads.get("vu_kn"),
        "is_ok": beam.get("is_ok", False),
        "governing_utilization": governing_util,
        "utilizations": utilizations,
        "flexure": {
            "section_type": flexure.get("section_type"),
            "pt_provided": pt_est,
        },
        "shear": {"is_safe": shear.get("is_safe")},
    }

    results = {
        "is_ok": beam.get("is_ok", False),
        "governing_case_id": case_id,
        "governing_utilization": governing_util,
        "cases": [case],
        "summary": {},
    }

    return ReportData(
        job_id=job_id,
        code=code,
        units=units,
        beam=beam_info,
        cases=[case],
        results=results,
        is_ok=bool(beam.get("is_ok", False)),
        governing_case_id=case_id,
        governing_utilization=governing_util,
    )


def export_design_json(design_results: Dict[str, Any], *, indent: int = 2) -> str:
    """Export report JSON for multi-beam design results."""
    beams = design_results.get("beams", [])
    code = str(design_results.get("code", "") or "")
    units = str(design_results.get("units", "") or "")
    summary = design_results.get("summary", {})

    beam_reports = []
    for beam in beams:
        data = _beam_report_data_from_design(beam, code=code, units=units)
        beam_reports.append(json.loads(export_json(data)))

    output = {
        "code": code,
        "units": units,
        "summary": summary,
        "beams": beam_reports,
    }
    return json.dumps(output, indent=indent, sort_keys=True, ensure_ascii=False)


def _render_batch_index_table(
    indexed: List[Dict[str, Any]],
    *,
    link_prefix: str,
    link_suffix: str = "",
) -> str:
    rows = []
    for item in indexed:
        beam = item["beam"]
        label = html.escape(item["label"])
        slug = item["slug"]
        util = _safe_float(beam.get("governing_utilization")) or 0.0
        is_ok = bool(beam.get("is_ok", False))
        status = "PASS" if is_ok else "FAIL"
        status_class = "status-pass" if is_ok else "status-fail"
        rows.append(
            f"""        <tr>
            <td><a href="{link_prefix}{slug}{link_suffix}">{label}</a></td>
            <td class="{status_class}">{status}</td>
            <td>{util:.2%}</td>
        </tr>"""
        )

    rows_joined = "\n".join(rows)
    return f"""<table class="index-table">
        <thead>
            <tr>
                <th>Beam</th>
                <th>Status</th>
                <th>Governing Utilization</th>
            </tr>
        </thead>
        <tbody>
{rows_joined}
        </tbody>
    </table>"""


def render_design_report_single(
    design_results: Dict[str, Any],
    *,
    batch_threshold: int = 80,
) -> str:
    """Render a single HTML report for multi-beam results."""
    beams = design_results.get("beams", [])
    code = str(design_results.get("code", "") or "")
    units = str(design_results.get("units", "") or "")

    indexed = _build_beam_index(beams)
    index_table = _render_batch_index_table(
        indexed, link_prefix="#beam-", link_suffix=""
    )

    sections = []
    for item in indexed:
        data = _beam_report_data_from_design(item["beam"], code=code, units=units)
        sections.append(
            _render_beam_section(
                data,
                heading=item["label"],
                section_id=f"beam-{item['slug']}",
            )
        )

    summary = design_results.get("summary", {})
    total = summary.get("total_beams", len(beams))
    passed = summary.get("passed", "")
    failed = summary.get("failed", "")

    body = f"""<h1>Beam Design Report (Batch)</h1>
<div class="summary">
    <p><strong>Code:</strong> {html.escape(code)}</p>
    <p><strong>Units:</strong> {html.escape(units)}</p>
    <p><strong>Total beams:</strong> {total} | <strong>Passed:</strong> {passed} | <strong>Failed:</strong> {failed}</p>
</div>
<div class="section">
    <h2>Beam Index</h2>
    {index_table}
</div>
{''.join(sections)}"""

    return _wrap_html("Beam Design Report (Batch)", body)


def write_design_report_package(
    design_results: Dict[str, Any],
    *,
    output_path: Path,
    batch_threshold: int = 80,
) -> List[Path]:
    """Write HTML report package for multi-beam results."""
    beams = design_results.get("beams", [])
    indexed = _build_beam_index(beams)
    code = str(design_results.get("code", "") or "")
    units = str(design_results.get("units", "") or "")

    if len(beams) < batch_threshold:
        html_output = render_design_report_single(
            design_results, batch_threshold=batch_threshold
        )
        if output_path.suffix.lower() in {".html", ".htm"}:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(html_output, encoding="utf-8")
            return [output_path]

        output_path.mkdir(parents=True, exist_ok=True)
        index_path = output_path / "index.html"
        index_path.write_text(html_output, encoding="utf-8")
        return [index_path]

    # Folder output with index + per-beam pages
    out_dir = output_path
    if output_path.suffix.lower() in {".html", ".htm"}:
        out_dir = output_path.parent / output_path.stem

    out_dir.mkdir(parents=True, exist_ok=True)
    beams_dir = out_dir / "beams"
    beams_dir.mkdir(parents=True, exist_ok=True)

    index_table = _render_batch_index_table(
        indexed, link_prefix="beams/", link_suffix=".html"
    )
    summary = design_results.get("summary", {})
    total = summary.get("total_beams", len(beams))
    passed = summary.get("passed", "")
    failed = summary.get("failed", "")

    index_body = f"""<h1>Beam Design Report (Batch)</h1>
<div class="summary">
    <p><strong>Code:</strong> {html.escape(code)}</p>
    <p><strong>Units:</strong> {html.escape(units)}</p>
    <p><strong>Total beams:</strong> {total} | <strong>Passed:</strong> {passed} | <strong>Failed:</strong> {failed}</p>
</div>
<div class="section">
    <h2>Beam Index</h2>
    {index_table}
</div>"""

    index_path = out_dir / "index.html"
    index_path.write_text(
        _wrap_html("Beam Design Report (Batch)", index_body), encoding="utf-8"
    )

    written = [index_path]
    for item in indexed:
        data = _beam_report_data_from_design(item["beam"], code=code, units=units)
        html_output = export_html(data)
        beam_path = beams_dir / f"{item['slug']}.html"
        beam_path.write_text(html_output, encoding="utf-8")
        written.append(beam_path)

    return written


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
