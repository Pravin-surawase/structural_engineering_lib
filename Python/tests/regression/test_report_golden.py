"""Golden file tests for report outputs (V09)."""

from __future__ import annotations

import json
from pathlib import Path

from structural_lib.services import report

# Path to tests/fixtures/ (two levels up from tests/regression/)
FIXTURES = Path(__file__).parent.parent / "fixtures" / "report"


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


def test_design_report_preserves_envelope_and_withholds_rejected_layout() -> None:
    design = {
        "code": "IS456",
        "units": "IS456",
        "summary": {"total_beams": 1, "passed": 0, "failed": 1},
        "beams": [
            {
                "beam_id": "B1",
                "story": "S1",
                "geometry": {"b_mm": 230, "D_mm": 450, "d_mm": 392},
                "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
                "loads": {"case_id": "S1_B1", "mu_knm": 600, "vu_kn": 90},
                "flexure": {"ast_required_mm2": 2000, "asc_required_mm2": 0},
                "shear": {"is_safe": True},
                "is_ok": False,
                "governing_utilization": None,
                "detailing": {
                    "is_valid": False,
                    "remarks": "Detailing has spacing violations",
                    "bottom_bars": [{"count": 6, "diameter": 32}] * 3,
                    "top_bars": [{"count": 5, "diameter": 32}] * 3,
                },
                "result_envelope": {
                    "engineering_status": "FAIL",
                    "review_status": "QUALIFIED_REVIEW_REQUIRED",
                },
            }
        ],
    }

    exported = json.loads(report.export_design_json(design))
    beam = exported["beams"][0]
    assert beam["result_envelope"] == design["beams"][0]["result_envelope"]
    assert beam["detailing_status"] == "REJECTED"
    assert all(zone["tension_provided_mm2"] is None for zone in beam["steel_zones"])

    html = report.render_design_report_single(design)
    assert "Engineering status:</strong> FAIL" in html
    assert "Detailing status:</strong> REJECTED" in html
    assert "Detailing has spacing violations" in html
    assert "6,032.12" not in html


def test_legacy_design_without_envelope_does_not_invent_review_evidence() -> None:
    legacy = _read_json("design_results_1.json")

    exported = json.loads(report.export_design_json(legacy))
    assert "result_envelope" not in exported["beams"][0]
    assert "Factored Actions and Review" not in report.render_design_report_single(
        legacy
    )
