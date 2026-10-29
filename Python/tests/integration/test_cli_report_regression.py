"""CLI regression tests for report/critical commands (fixture-based)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

# Path to tests/fixtures/ (two levels up from tests/integration/)
FIXTURES = Path(__file__).parent.parent / "fixtures"
REPORT_FIXTURES = FIXTURES / "report"
CLI_FIXTURES = FIXTURES / "cli"


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def test_cli_report_from_design_results(tmp_path: Path) -> None:
    design_results = REPORT_FIXTURES / "design_results_1.json"
    out_html = tmp_path / "report.html"

    _run(
        [
            sys.executable,
            "-m",
            "structural_lib",
            "report",
            str(design_results),
            "--format",
            "html",
            "-o",
            str(out_html),
            "--batch-threshold",
            "80",
        ]
    )

    expected = (REPORT_FIXTURES / "report_single_1.html").read_text(encoding="utf-8")
    assert out_html.read_text(encoding="utf-8") == expected


def test_cli_critical_from_job_output(tmp_path: Path) -> None:
    job_out = CLI_FIXTURES / "job_out_min"
    out_csv = tmp_path / "critical.csv"

    _run(
        [
            sys.executable,
            "-m",
            "structural_lib",
            "critical",
            str(job_out),
            "--top",
            "1",
            "--format",
            "csv",
            "-o",
            str(out_csv),
        ]
    )

    expected = (CLI_FIXTURES / "critical_top1.csv").read_text(encoding="utf-8")
    assert out_csv.read_text(encoding="utf-8") == expected


def test_cli_report_and_critical_preserve_unavailable_overload_reason(
    tmp_path: Path,
) -> None:
    """A real overload stays FAIL with its core unavailable-ratio reason."""
    job = {
        "schema_version": 1,
        "job_id": "unavailable-utilization",
        "code": "IS456",
        "units": "IS456",
        "beam": {
            "b_mm": 300.0,
            "D_mm": 500.0,
            "d_mm": 457.0,
            "fck_nmm2": 25.0,
            "fy_nmm2": 500.0,
            "d_dash_mm": 50.0,
            "asv_mm2": 100.0,
        },
        "cases": [{"case_id": "OVERLOAD", "mu_knm": 2000.0, "vu_kn": 75.0}],
    }
    job_path = tmp_path / "overload-job.json"
    output_dir = tmp_path / "job-output"
    report_json = tmp_path / "report.json"
    report_html = tmp_path / "report.html"
    critical_csv = tmp_path / "critical.csv"
    critical_html = tmp_path / "critical.html"
    job_path.write_text(json.dumps(job), encoding="utf-8")

    _run(
        [
            sys.executable,
            "-m",
            "structural_lib",
            "job",
            str(job_path),
            "-o",
            str(output_dir),
        ]
    )
    _run(
        [
            sys.executable,
            "-m",
            "structural_lib",
            "report",
            str(output_dir),
            "--format",
            "json",
            "-o",
            str(report_json),
        ]
    )
    _run(
        [
            sys.executable,
            "-m",
            "structural_lib",
            "report",
            str(output_dir),
            "--format",
            "html",
            "-o",
            str(report_html),
        ]
    )
    _run(
        [
            sys.executable,
            "-m",
            "structural_lib",
            "critical",
            str(output_dir),
            "--format",
            "csv",
            "-o",
            str(critical_csv),
        ]
    )
    _run(
        [
            sys.executable,
            "-m",
            "structural_lib",
            "critical",
            str(output_dir),
            "--format",
            "html",
            "-o",
            str(critical_html),
        ]
    )

    def reject_nonfinite(value: str) -> None:
        raise AssertionError(f"Non-finite JSON constant: {value}")

    payload = json.loads(
        report_json.read_text(encoding="utf-8"), parse_constant=reject_nonfinite
    )
    marker = payload["unavailable_utilizations"]["governing_utilization"]
    assert payload["is_ok"] is False
    assert payload["governing_utilization"] is None
    assert marker["code"] == "UTILIZATION_NOT_EVALUATED"
    assert marker["reason"]

    report_rendered = report_html.read_text(encoding="utf-8")
    assert "Unavailable" in report_rendered
    assert marker["reason"] in report_rendered

    case_marker = payload["cases"][0]["unavailable_utilizations"][
        "governing_utilization"
    ]
    assert case_marker["code"] == "UTILIZATION_NOT_EVALUATED"
    assert case_marker["reason"]
    for rendered in (
        critical_csv.read_text(encoding="utf-8"),
        critical_html.read_text(encoding="utf-8"),
    ):
        assert "Unavailable" in rendered
        assert case_marker["reason"] in rendered
        assert "Infinity" not in rendered
        assert "NaN" not in rendered
