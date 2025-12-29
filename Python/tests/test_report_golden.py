"""Golden file tests for report outputs (V09)."""

from __future__ import annotations

import json
from pathlib import Path

from structural_lib import report


FIXTURES = Path(__file__).parent / "fixtures" / "report"


def _read_text(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def _read_json(name: str) -> dict:
    return json.loads(_read_text(name))


def test_report_single_1_beam_matches_golden() -> None:
    design_results = _read_json("design_results_1.json")
    html = report.render_design_report_single(design_results, batch_threshold=80)
    assert html == _read_text("report_single_1.html")


def test_report_single_79_beams_matches_golden() -> None:
    design_results = _read_json("design_results_79.json")
    html = report.render_design_report_single(design_results, batch_threshold=80)
    assert html == _read_text("report_single_79.html")


def test_report_batch_80_beams_matches_golden(tmp_path: Path) -> None:
    design_results = _read_json("design_results_80.json")
    out_dir = tmp_path / "report"
    report.write_design_report_package(
        design_results, output_path=out_dir, batch_threshold=80
    )

    index_html = (out_dir / "index.html").read_text(encoding="utf-8")
    beam_html = (out_dir / "beams" / "G_B1.html").read_text(encoding="utf-8")

    assert index_html == _read_text("report_batch_index_80.html")
    assert beam_html == _read_text("report_batch_beam_G_B1.html")


def test_export_design_json_matches_golden() -> None:
    design_results = _read_json("design_results_1.json")
    output = report.export_design_json(design_results)
    assert output.strip() == _read_text("report_design_1.json").strip()
