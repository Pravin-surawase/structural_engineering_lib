"""CLI regression tests for report/critical commands (fixture-based)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


FIXTURES = Path(__file__).parent / "fixtures"
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
