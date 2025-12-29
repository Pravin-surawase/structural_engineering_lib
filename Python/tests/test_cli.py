"""
Tests for unified CLI entrypoint (__main__.py).

Tests cover all subcommands: design, bbs, dxf, and job.
"""

import json
import csv
import subprocess
import sys
from pathlib import Path

import pytest

from structural_lib import __main__ as cli_main


@pytest.fixture
def sample_csv_file(tmp_path):
    """Create a sample CSV file for testing design command."""
    csv_path = tmp_path / "beams.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "BeamID",
                "Story",
                "b",
                "D",
                "Span",
                "Cover",
                "fck",
                "fy",
                "Mu",
                "Vu",
                "Ast_req",
                "Asc_req",
                "Stirrup_Dia",
                "Stirrup_Spacing",
                "Status",
            ]
        )
        writer.writerow(
            [
                "B1",
                "Story1",
                "300",
                "500",
                "4000",
                "40",
                "25",
                "500",
                "150",
                "100",
                "942.5",
                "0",
                "8",
                "150",
                "OK",
            ]
        )
        writer.writerow(
            [
                "B2",
                "Story1",
                "300",
                "450",
                "3000",
                "40",
                "25",
                "500",
                "100",
                "80",
                "628.3",
                "0",
                "8",
                "175",
                "OK",
            ]
        )

    return csv_path


@pytest.fixture
def sample_json_beams_file(tmp_path):
    """Create a sample JSON file for testing design command."""
    json_path = tmp_path / "beams.json"

    data = {
        "beams": [
            {
                "beam_id": "B1",
                "story": "Story1",
                "b": 300,
                "D": 500,
                "d": 460,
                "span": 4000,
                "cover": 40,
                "fck": 25,
                "fy": 500,
                "Mu": 150,
                "Vu": 100,
                "Ast_req": 942.5,
                "Asc_req": 0,
                "stirrup_dia": 8,
                "stirrup_spacing": 150,
                "status": "OK",
            }
        ]
    }

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return json_path


@pytest.fixture
def sample_design_results_file(tmp_path):
    """Create a sample design results JSON for testing bbs and dxf commands."""
    results_path = tmp_path / "design_results.json"

    data = {
        "schema_version": 1,
        "code": "IS456",
        "beams": [
            {
                "beam_id": "B1",
                "story": "Story1",
                "geometry": {
                    "b": 300,
                    "D": 500,
                    "d": 460,
                    "span": 4000,
                    "cover": 40,
                },
                "materials": {
                    "fck": 25,
                    "fy": 500,
                },
                "loads": {
                    "Mu": 150,
                    "Vu": 100,
                },
                "flexure": {
                    "ast_req": 942.5,
                    "asc_req": 0,
                    "status": "OK",
                    "xu_d": 0.35,
                    "mu_rd": 160.0,
                },
                "shear": {
                    "tau_v": 0.72,
                    "tau_c": 0.48,
                    "sv_req": 150,
                    "status": "OK",
                },
                "detailing": {
                    "bottom_bars": [
                        {"count": 3, "diameter": 20, "callout": "3-T20"},
                        {"count": 3, "diameter": 20, "callout": "3-T20"},
                        {"count": 3, "diameter": 20, "callout": "3-T20"},
                    ],
                    "top_bars": [
                        {"count": 2, "diameter": 16, "callout": "2-T16"},
                        {"count": 2, "diameter": 16, "callout": "2-T16"},
                        {"count": 2, "diameter": 16, "callout": "2-T16"},
                    ],
                    "stirrups": [
                        {"diameter": 8, "spacing": 150, "callout": "T8@150"},
                        {"diameter": 8, "spacing": 200, "callout": "T8@200"},
                        {"diameter": 8, "spacing": 150, "callout": "T8@150"},
                    ],
                    "ld_tension": 752,
                    "lap_length": 940,
                },
                "status": "OK",
            }
        ],
    }

    with results_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return results_path


@pytest.fixture
def sample_job_file(tmp_path):
    """Create a sample job JSON for testing job command."""
    job_path = tmp_path / "job.json"

    data = {
        "schema_version": 1,
        "job_id": "test_job_001",
        "code": "IS456",
        "units": "IS456",
        "beam": {
            "b_mm": 300.0,
            "D_mm": 500.0,
            "d_mm": 450.0,
            "d_dash_mm": 50.0,
            "fck_nmm2": 25.0,
            "fy_nmm2": 500.0,
            "asv_mm2": 100.0,
            "pt_percent": None,
        },
        "cases": [
            {"case_id": "DL+LL", "mu_knm": 80.0, "vu_kn": 60.0},
            {"case_id": "1.5(DL+LL)", "mu_knm": 120.0, "vu_kn": 200.0},
        ],
    }

    with job_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return job_path


# =============================================================================
# Main CLI Tests
# =============================================================================


def test_cli_help():
    """Test main CLI help output."""
    with pytest.raises(SystemExit) as exc:
        cli_main.main(["--help"])
    assert exc.value.code == 0


def test_cli_requires_command():
    """Test that CLI requires a subcommand."""
    with pytest.raises(SystemExit):
        cli_main.main([])


# =============================================================================
# Design Command Tests
# =============================================================================


def test_design_missing_args_exit_code():
    """Missing required args should exit with code 2 (argparse)."""
    with pytest.raises(SystemExit) as exc:
        cli_main.main(["design"])
    assert exc.value.code == 2


def test_design_from_csv(sample_csv_file, tmp_path):
    """Test design command with CSV input."""
    output_file = tmp_path / "results.json"

    rc = cli_main.main(["design", str(sample_csv_file), "-o", str(output_file)])

    assert rc == 0
    assert output_file.exists()

    # Verify output content
    with output_file.open("r") as f:
        data = json.load(f)

    assert data["schema_version"] == 1
    assert data["code"] == "IS456"
    assert len(data["beams"]) == 2
    assert data["beams"][0]["beam_id"] == "B1"
    assert data["beams"][1]["beam_id"] == "B2"
    assert "flexure" in data["beams"][0]
    assert "shear" in data["beams"][0]
    assert "detailing" in data["beams"][0]


def test_design_with_deflection(sample_csv_file, tmp_path):
    """Deflection flag should populate serviceability fields."""
    output_file = tmp_path / "results.json"

    rc = cli_main.main(
        ["design", str(sample_csv_file), "-o", str(output_file), "--deflection"]
    )

    assert rc == 0
    assert output_file.exists()

    with output_file.open("r") as f:
        data = json.load(f)

    svc = data["beams"][0]["serviceability"]
    assert svc["deflection_status"] in {"ok", "fail"}
    assert svc["deflection_ok"] is not None


def test_design_summary_csv(sample_csv_file, tmp_path):
    """Summary CSV should be written when requested."""
    output_file = tmp_path / "results.json"
    summary_file = tmp_path / "summary.csv"

    rc = cli_main.main(
        [
            "design",
            str(sample_csv_file),
            "-o",
            str(output_file),
            "--summary",
            str(summary_file),
        ]
    )

    assert rc == 0
    assert summary_file.exists()

    with summary_file.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 2
    assert "beam_id" in rows[0]
    assert "governing_utilization" in rows[0]


def test_design_summary_default_path(sample_csv_file, tmp_path, monkeypatch):
    """Summary CSV should default to CWD when no path provided."""
    monkeypatch.chdir(tmp_path)

    rc = cli_main.main(["design", str(sample_csv_file), "--summary"])

    assert rc == 0
    summary_path = tmp_path / "design_summary.csv"
    assert summary_path.exists()


def test_design_summary_csv_default_path(sample_csv_file, tmp_path):
    """Summary CSV with default path (next to output file)."""
    output_file = tmp_path / "results.json"

    rc = cli_main.main(
        [
            "design",
            str(sample_csv_file),
            "-o",
            str(output_file),
            "--summary",
        ]
    )

    assert rc == 0
    default_summary = tmp_path / "design_summary.csv"
    assert default_summary.exists()


def test_design_with_crack_width_params(sample_csv_file, tmp_path):
    """Crack width params should populate serviceability fields."""
    output_file = tmp_path / "results.json"
    params_file = tmp_path / "crack_width.json"
    params_file.write_text(
        json.dumps(
            {
                "acr_mm": 120.0,
                "cmin_mm": 25.0,
                "h_mm": 500.0,
                "x_mm": 200.0,
                "epsilon_m": 0.001,
            }
        )
    )

    rc = cli_main.main(
        [
            "design",
            str(sample_csv_file),
            "-o",
            str(output_file),
            "--crack-width-params",
            str(params_file),
        ]
    )

    assert rc == 0
    assert output_file.exists()

    with output_file.open("r") as f:
        data = json.load(f)

    svc = data["beams"][0]["serviceability"]
    assert svc["crack_width_status"] in {"ok", "fail"}
    assert svc["crack_width_ok"] is not None


def test_design_crack_width_params_not_found(sample_csv_file, tmp_path):
    """Error when crack width params file does not exist."""
    output_file = tmp_path / "results.json"

    rc = cli_main.main(
        [
            "design",
            str(sample_csv_file),
            "-o",
            str(output_file),
            "--crack-width-params",
            str(tmp_path / "nonexistent.json"),
        ]
    )

    assert rc == 1


def test_design_crack_width_params_invalid(sample_csv_file, tmp_path):
    """Error when crack width params is not a JSON object."""
    output_file = tmp_path / "results.json"
    params_file = tmp_path / "invalid.json"
    params_file.write_text('["not", "an", "object"]')

    rc = cli_main.main(
        [
            "design",
            str(sample_csv_file),
            "-o",
            str(output_file),
            "--crack-width-params",
            str(params_file),
        ]
    )

    assert rc == 1


def test_design_from_json(sample_json_beams_file, tmp_path):
    """Test design command with JSON input."""
    output_file = tmp_path / "results.json"

    rc = cli_main.main(["design", str(sample_json_beams_file), "-o", str(output_file)])

    assert rc == 0
    assert output_file.exists()

    with output_file.open("r") as f:
        data = json.load(f)

    assert len(data["beams"]) == 1
    assert data["beams"][0]["beam_id"] == "B1"


def test_design_missing_input():
    """Test design command with missing input file."""
    rc = cli_main.main(["design", "nonexistent.csv", "-o", "output.json"])

    assert rc == 1


def test_design_unsupported_format(tmp_path):
    """Test design command with unsupported file format."""
    bad_file = tmp_path / "data.txt"
    bad_file.write_text("some data")

    rc = cli_main.main(["design", str(bad_file), "-o", str(tmp_path / "output.json")])

    assert rc == 1


def test_design_stdout_output(sample_csv_file, capsys):
    """Test design command output to stdout."""
    rc = cli_main.main(["design", str(sample_csv_file)])

    assert rc == 0

    captured = capsys.readouterr()
    # Verify JSON was printed to stdout
    data = json.loads(captured.out)
    assert "beams" in data
    assert len(data["beams"]) == 2


# =============================================================================
# BBS Command Tests
# =============================================================================


def test_bbs_to_csv(sample_design_results_file, tmp_path):
    """Test bbs command with CSV output."""
    output_file = tmp_path / "bbs.csv"

    rc = cli_main.main(["bbs", str(sample_design_results_file), "-o", str(output_file)])

    assert rc == 0
    assert output_file.exists()

    # Verify CSV content
    with output_file.open("r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) > 0
    # Check expected columns
    assert "bar_mark" in rows[0]
    assert "member_id" in rows[0]
    assert "diameter_mm" in rows[0]
    assert "cut_length_mm" in rows[0]
    assert "total_weight_kg" in rows[0]


def test_bbs_to_json(sample_design_results_file, tmp_path):
    """Test bbs command with JSON output."""
    output_file = tmp_path / "bbs.json"

    rc = cli_main.main(["bbs", str(sample_design_results_file), "-o", str(output_file)])

    assert rc == 0
    assert output_file.exists()

    # Verify JSON content
    with output_file.open("r") as f:
        data = json.load(f)

    assert "items" in data
    assert "summary" in data
    assert len(data["items"]) > 0


def test_bbs_stdout_output(sample_design_results_file, capsys):
    """Test bbs command output to stdout."""
    rc = cli_main.main(["bbs", str(sample_design_results_file)])

    assert rc == 0

    captured = capsys.readouterr()
    # Verify CSV was printed
    lines = captured.out.strip().split("\n")
    assert len(lines) > 1  # Header + data rows
    assert "bar_mark" in lines[0]


def test_bbs_missing_input():
    """Test bbs command with missing input file."""
    rc = cli_main.main(["bbs", "nonexistent.json", "-o", "bbs.csv"])

    assert rc == 1


def test_bbs_empty_beams(tmp_path):
    """Test bbs command with empty beams array."""
    empty_file = tmp_path / "empty.json"
    empty_file.write_text('{"beams": []}')

    rc = cli_main.main(["bbs", str(empty_file), "-o", str(tmp_path / "bbs.csv")])

    assert rc == 1


# =============================================================================
# Detail Command Tests
# =============================================================================


def test_detail_to_json(sample_design_results_file, tmp_path):
    """Test detail command with JSON output."""
    output_file = tmp_path / "detail.json"

    rc = cli_main.main(
        ["detail", str(sample_design_results_file), "-o", str(output_file)]
    )

    assert rc == 0
    assert output_file.exists()

    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert data["beams"]
    assert data["beams"][0]["beam_id"] == "B1"


def test_detail_missing_input():
    """Test detail command with missing input file."""
    rc = cli_main.main(["detail", "nonexistent.json"])

    assert rc == 1


# =============================================================================
# DXF Command Tests
# =============================================================================


def test_dxf_requires_output():
    """Test dxf command requires output argument."""
    with pytest.raises(SystemExit):
        cli_main.main(["dxf", "input.json"])


def test_dxf_missing_input(tmp_path):
    """Test dxf command with missing input file."""
    rc = cli_main.main(["dxf", "nonexistent.json", "-o", str(tmp_path / "output.dxf")])

    assert rc == 1


def test_dxf_generation(sample_design_results_file, tmp_path):
    """Test dxf command with valid input."""
    # Import to check if ezdxf is available
    from structural_lib import dxf_export

    if not dxf_export.EZDXF_AVAILABLE:
        pytest.skip("ezdxf not installed")

    output_file = tmp_path / "beam.dxf"

    rc = cli_main.main(["dxf", str(sample_design_results_file), "-o", str(output_file)])

    assert rc == 0
    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_dxf_title_block(sample_design_results_file, tmp_path):
    """Title block option should create BORDER layer and title text."""
    from structural_lib import dxf_export

    if not dxf_export.EZDXF_AVAILABLE:
        pytest.skip("ezdxf not installed")

    output_file = tmp_path / "beam_title.dxf"

    rc = cli_main.main(
        [
            "dxf",
            str(sample_design_results_file),
            "-o",
            str(output_file),
            "--title-block",
            "--title",
            "Beam Sheet",
        ]
    )

    assert rc == 0
    assert output_file.exists()

    doc = dxf_export.ezdxf.readfile(str(output_file))
    assert "BORDER" in doc.layers

    texts = [e.dxf.text for e in doc.modelspace().query("TEXT")]
    assert any("Beam Sheet" in text for text in texts)


def test_dxf_without_ezdxf(sample_design_results_file, tmp_path, monkeypatch):
    """Test dxf command when ezdxf is not available."""
    from structural_lib import dxf_export

    # Mock ezdxf as unavailable
    monkeypatch.setattr(dxf_export, "EZDXF_AVAILABLE", False)

    rc = cli_main.main(
        ["dxf", str(sample_design_results_file), "-o", str(tmp_path / "output.dxf")]
    )

    assert rc == 1


def test_mark_diff_missing_bbs(tmp_path):
    """Test mark-diff command with missing BBS file."""
    dxf_path = tmp_path / "drawings.dxf"
    dxf_path.write_text("", encoding="utf-8")

    rc = cli_main.main(
        ["mark-diff", "--bbs", str(tmp_path / "missing.csv"), "--dxf", str(dxf_path)]
    )

    assert rc == 1


def test_mark_diff_missing_dxf(tmp_path):
    """Test mark-diff command with missing DXF file."""
    bbs_path = tmp_path / "schedule.csv"
    bbs_path.write_text("", encoding="utf-8")

    rc = cli_main.main(
        ["mark-diff", "--bbs", str(bbs_path), "--dxf", str(tmp_path / "missing.dxf")]
    )

    assert rc == 1


def test_mark_diff_without_ezdxf(tmp_path, monkeypatch):
    """Test mark-diff command when ezdxf is not installed."""
    from types import SimpleNamespace

    bbs_path = tmp_path / "schedule.csv"
    dxf_path = tmp_path / "drawings.dxf"
    bbs_path.write_text("", encoding="utf-8")
    dxf_path.write_text("", encoding="utf-8")

    monkeypatch.setattr(cli_main, "dxf_export", SimpleNamespace(EZDXF_AVAILABLE=False))

    rc = cli_main.main(["mark-diff", "--bbs", str(bbs_path), "--dxf", str(dxf_path)])

    assert rc == 1


def test_mark_diff_json_output(tmp_path, monkeypatch):
    """Test mark-diff command JSON output."""
    from types import SimpleNamespace

    bbs_path = tmp_path / "schedule.csv"
    dxf_path = tmp_path / "drawings.dxf"
    out_path = tmp_path / "mark_diff.json"
    bbs_path.write_text("", encoding="utf-8")
    dxf_path.write_text("", encoding="utf-8")

    def _fake_compare(_bbs, _dxf):
        return {"ok": True, "summary": {"beams_checked": 1}}

    monkeypatch.setattr(
        cli_main,
        "dxf_export",
        SimpleNamespace(EZDXF_AVAILABLE=True, compare_bbs_dxf_marks=_fake_compare),
    )

    rc = cli_main.main(
        [
            "mark-diff",
            "--bbs",
            str(bbs_path),
            "--dxf",
            str(dxf_path),
            "--format",
            "json",
            "-o",
            str(out_path),
        ]
    )

    assert rc == 0
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["ok"] is True


def test_mark_diff_text_fail(tmp_path, monkeypatch, capsys):
    """Test mark-diff command text output on failure."""
    from types import SimpleNamespace

    bbs_path = tmp_path / "schedule.csv"
    dxf_path = tmp_path / "drawings.dxf"
    bbs_path.write_text("", encoding="utf-8")
    dxf_path.write_text("", encoding="utf-8")

    def _fake_compare(_bbs, _dxf):
        return {"ok": False, "summary": {"beams_checked": 0}}

    monkeypatch.setattr(
        cli_main,
        "dxf_export",
        SimpleNamespace(EZDXF_AVAILABLE=True, compare_bbs_dxf_marks=_fake_compare),
    )

    rc = cli_main.main(["mark-diff", "--bbs", str(bbs_path), "--dxf", str(dxf_path)])

    assert rc == 2
    output = capsys.readouterr().out
    assert "FAIL" in output


# =============================================================================
# Job Command Tests
# =============================================================================


def test_job_requires_output():
    """Test job command requires output argument."""
    with pytest.raises(SystemExit):
        cli_main.main(["job", "job.json"])


def test_job_missing_input(tmp_path):
    """Test job command with missing input file."""
    rc = cli_main.main(["job", "nonexistent.json", "-o", str(tmp_path / "output")])

    assert rc == 1


def test_job_execution(sample_job_file, tmp_path):
    """Test job command with valid job file."""
    output_dir = tmp_path / "job_output"

    rc = cli_main.main(["job", str(sample_job_file), "-o", str(output_dir)])

    assert rc == 0
    assert output_dir.exists()

    # Check that job runner created expected outputs
    # Job runner creates subfolders like design/, deliverables/, etc.
    csv_files = list(output_dir.rglob("*.csv"))
    json_files = list(output_dir.rglob("*.json"))

    # Should have at least some output files
    assert len(csv_files) > 0 or len(json_files) > 0


def test_validate_job_auto(sample_job_file):
    """Validate job.json with auto detection."""
    rc = cli_main.main(["validate", str(sample_job_file)])
    assert rc == 0


def test_validate_results_auto(sample_design_results_file):
    """Validate results.json with auto detection."""
    rc = cli_main.main(["validate", str(sample_design_results_file)])
    assert rc == 0


def test_validate_missing_input(tmp_path):
    """Validate command with missing input file."""
    rc = cli_main.main(["validate", str(tmp_path / "missing.json")])
    assert rc == 1


def test_validate_auto_unknown_type(tmp_path):
    """Validate command with unknown JSON type."""
    path = tmp_path / "unknown.json"
    path.write_text(json.dumps({"foo": 1}), encoding="utf-8")

    rc = cli_main.main(["validate", str(path)])
    assert rc == 1


def test_validate_json_output(sample_job_file, tmp_path):
    """Validate job.json and write JSON report to file."""
    output_path = tmp_path / "validation.json"

    rc = cli_main.main(
        ["validate", str(sample_job_file), "--format", "json", "-o", str(output_path)]
    )

    assert rc == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["ok"] is True


def test_validate_results_errors_output(tmp_path, capsys):
    """Validate results.json with errors and capture text output."""
    path = tmp_path / "bad_results.json"
    path.write_text(
        json.dumps({"schema_version": 1, "code": "IS456", "beams": []}, indent=2),
        encoding="utf-8",
    )

    rc = cli_main.main(["validate", str(path), "--type", "results"])

    assert rc == 2
    output = capsys.readouterr().out
    assert "Errors:" in output


# =============================================================================
# Report Command Tests
# =============================================================================


@pytest.fixture
def sample_job_output_dir(tmp_path, sample_job_file):
    """Create a job output folder by running the job command."""
    output_dir = tmp_path / "job_output_for_report"
    rc = cli_main.main(["job", str(sample_job_file), "-o", str(output_dir)])
    assert rc == 0
    assert output_dir.exists()
    return output_dir


def test_report_missing_output_dir(tmp_path):
    """Test report command with missing output directory."""
    rc = cli_main.main(["report", str(tmp_path / "nonexistent_dir")])
    assert rc == 1


def test_report_json_to_stdout(sample_job_output_dir, capsys):
    """Test report command outputs JSON to stdout."""
    rc = cli_main.main(["report", str(sample_job_output_dir), "--format=json"])
    assert rc == 0

    captured = capsys.readouterr()
    # Should be valid JSON
    output = json.loads(captured.out)
    assert "job_id" in output
    assert "is_ok" in output


def test_report_json_to_file(sample_job_output_dir, tmp_path):
    """Test report command writes JSON to file."""
    out_file = tmp_path / "report.json"
    rc = cli_main.main(
        ["report", str(sample_job_output_dir), "--format=json", "-o", str(out_file)]
    )
    assert rc == 0
    assert out_file.exists()

    with out_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    assert "job_id" in data


def test_report_html_format(sample_job_output_dir, capsys):
    """Test report command with HTML format."""
    rc = cli_main.main(["report", str(sample_job_output_dir), "--format=html"])
    assert rc == 0

    captured = capsys.readouterr()
    assert "<!DOCTYPE html>" in captured.out
    assert "Beam Design Report" in captured.out


def test_report_html_to_file(sample_job_output_dir, tmp_path):
    """Test report command writes HTML to file."""
    out_file = tmp_path / "report.html"
    rc = cli_main.main(
        ["report", str(sample_job_output_dir), "--format=html", "-o", str(out_file)]
    )
    assert rc == 0
    assert out_file.exists()

    content = out_file.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content


def test_report_default_format_is_json(sample_job_output_dir, capsys):
    """Test that default format is JSON."""
    rc = cli_main.main(["report", str(sample_job_output_dir)])
    assert rc == 0

    captured = capsys.readouterr()
    # Should be valid JSON (default format)
    output = json.loads(captured.out)
    assert isinstance(output, dict)


# =============================================================================
# Critical Command Tests (V03)
# =============================================================================


def test_critical_missing_output_dir(tmp_path):
    """Test critical command with missing output directory."""
    rc = cli_main.main(["critical", str(tmp_path / "nonexistent_dir")])
    assert rc == 1


def test_critical_csv_to_stdout(sample_job_output_dir, capsys):
    """Test critical command outputs CSV to stdout."""
    rc = cli_main.main(["critical", str(sample_job_output_dir), "--format=csv"])
    assert rc == 0

    captured = capsys.readouterr()
    # Should have CSV header and data
    assert "case_id" in captured.out
    assert "utilization" in captured.out


def test_critical_csv_to_file(sample_job_output_dir, tmp_path):
    """Test critical command writes CSV to file."""
    out_file = tmp_path / "critical.csv"
    rc = cli_main.main(
        ["critical", str(sample_job_output_dir), "--format=csv", "-o", str(out_file)]
    )
    assert rc == 0
    assert out_file.exists()

    content = out_file.read_text(encoding="utf-8")
    assert "case_id" in content


def test_critical_html_format(sample_job_output_dir, capsys):
    """Test critical command with HTML format."""
    rc = cli_main.main(["critical", str(sample_job_output_dir), "--format=html"])
    assert rc == 0

    captured = capsys.readouterr()
    assert "<!DOCTYPE html>" in captured.out
    assert "Critical Set" in captured.out


def test_critical_top_filter(sample_job_output_dir, capsys):
    """Test critical command with --top filter."""
    rc = cli_main.main(
        ["critical", str(sample_job_output_dir), "--top=1", "--format=csv"]
    )
    assert rc == 0

    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    # Header + 1 data row
    assert len(lines) == 2


def test_critical_default_format_is_csv(sample_job_output_dir, capsys):
    """Test that default format is CSV."""
    rc = cli_main.main(["critical", str(sample_job_output_dir)])
    assert rc == 0

    captured = capsys.readouterr()
    # Should be CSV (default format)
    assert "case_id" in captured.out
    assert "utilization" in captured.out


# =============================================================================
# Integration Tests
# =============================================================================


def test_full_workflow_csv_to_bbs(sample_csv_file, tmp_path):
    """Test full workflow: CSV -> design -> BBS."""
    design_output = tmp_path / "design.json"
    bbs_output = tmp_path / "bbs.csv"

    # Step 1: Design
    rc1 = cli_main.main(["design", str(sample_csv_file), "-o", str(design_output)])
    assert rc1 == 0
    assert design_output.exists()

    # Step 2: BBS
    rc2 = cli_main.main(["bbs", str(design_output), "-o", str(bbs_output)])
    assert rc2 == 0
    assert bbs_output.exists()


def test_full_workflow_csv_to_dxf(sample_csv_file, tmp_path):
    """Test full workflow: CSV -> design -> DXF."""
    from structural_lib import dxf_export

    if not dxf_export.EZDXF_AVAILABLE:
        pytest.skip("ezdxf not installed")

    design_output = tmp_path / "design.json"
    dxf_output = tmp_path / "drawings.dxf"

    # Step 1: Design
    rc1 = cli_main.main(["design", str(sample_csv_file), "-o", str(design_output)])
    assert rc1 == 0

    # Step 2: DXF
    rc2 = cli_main.main(["dxf", str(design_output), "-o", str(dxf_output)])
    assert rc2 == 0
    assert dxf_output.exists()


# =============================================================================
# Module Execution Tests
# =============================================================================


def test_module_execution_with_subprocess(sample_csv_file, tmp_path):
    """Test that module can be executed with python -m."""
    output_file = tmp_path / "results.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "structural_lib",
            "design",
            str(sample_csv_file),
            "-o",
            str(output_file),
        ],
        cwd=Path(__file__).parent.parent,  # Run from Python/ directory
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert output_file.exists()


def test_help_via_subprocess():
    """Test help output via subprocess."""
    result = subprocess.run(
        [sys.executable, "-m", "structural_lib", "--help"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Available commands" in result.stdout
    assert "design" in result.stdout
    assert "bbs" in result.stdout
    assert "dxf" in result.stdout
    assert "job" in result.stdout
    assert "report" in result.stdout
    assert "critical" in result.stdout


# =============================================================================
# End-to-End Integration Tests (CSV/JSON → detailing → outputs)
# =============================================================================


def test_integration_design_output_has_detailing(sample_csv_file, tmp_path):
    """Test that design output includes detailing information."""
    output_file = tmp_path / "results.json"

    rc = cli_main.main(["design", str(sample_csv_file), "-o", str(output_file)])
    assert rc == 0

    with output_file.open("r") as f:
        data = json.load(f)

    for beam in data["beams"]:
        det = beam.get("detailing", {})
        # Check detailing fields are present and populated
        assert "bottom_bars" in det
        assert "top_bars" in det
        assert "stirrups" in det
        # Schema v1 uses _mm suffix for lengths
        assert "ld_tension_mm" in det or "ld_tension" in det
        assert "lap_length_mm" in det or "lap_length" in det
        # Check they have actual values
        assert len(det["bottom_bars"]) > 0
        ld = det.get("ld_tension_mm") or det.get("ld_tension", 0)
        lap = det.get("lap_length_mm") or det.get("lap_length", 0)
        assert ld > 0
        assert lap > 0


def test_integration_bbs_has_all_bar_types(sample_csv_file, tmp_path):
    """Test that BBS output includes main bars and stirrups."""
    design_output = tmp_path / "design.json"
    bbs_output = tmp_path / "bbs.csv"

    # Design first
    rc1 = cli_main.main(["design", str(sample_csv_file), "-o", str(design_output)])
    assert rc1 == 0

    # Generate BBS
    rc2 = cli_main.main(["bbs", str(design_output), "-o", str(bbs_output)])
    assert rc2 == 0

    # Check BBS content
    with bbs_output.open("r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Should have multiple bar types
    locations = {row["location"] for row in rows}
    assert len(locations) >= 2  # At least bottom + stirrup or top + stirrup


def test_integration_multi_beam_workflow(tmp_path):
    """Test complete workflow with multiple beams of different sizes."""
    # Create CSV with diverse beams
    csv_path = tmp_path / "multi_beams.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "BeamID",
                "Story",
                "b",
                "D",
                "Span",
                "Cover",
                "fck",
                "fy",
                "Mu",
                "Vu",
                "Ast_req",
                "Asc_req",
                "Stirrup_Dia",
                "Stirrup_Spacing",
                "Status",
            ]
        )
        # Small beam
        writer.writerow(
            [
                "B1",
                "GF",
                "230",
                "400",
                "3000",
                "40",
                "25",
                "500",
                "80",
                "50",
                "500",
                "0",
                "8",
                "150",
                "OK",
            ]
        )
        # Medium beam
        writer.writerow(
            [
                "B2",
                "1F",
                "300",
                "500",
                "4000",
                "40",
                "25",
                "500",
                "150",
                "100",
                "900",
                "0",
                "8",
                "150",
                "OK",
            ]
        )
        # Large beam
        writer.writerow(
            [
                "B3",
                "1F",
                "400",
                "700",
                "6000",
                "50",
                "30",
                "500",
                "400",
                "200",
                "2500",
                "500",
                "10",
                "100",
                "OK",
            ]
        )

    design_output = tmp_path / "design.json"
    bbs_output = tmp_path / "bbs.csv"

    # Step 1: Design all beams
    rc1 = cli_main.main(["design", str(csv_path), "-o", str(design_output)])
    assert rc1 == 0

    with design_output.open("r") as f:
        data = json.load(f)
    assert len(data["beams"]) == 3

    # Step 2: Generate BBS
    rc2 = cli_main.main(["bbs", str(design_output), "-o", str(bbs_output)])
    assert rc2 == 0

    with bbs_output.open("r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Check all beams are in BBS
    member_ids = {row["member_id"] for row in rows}
    assert "B1" in member_ids
    assert "B2" in member_ids
    assert "B3" in member_ids


class TestExtractBeamParamsFromSchema:
    """Tests for _extract_beam_params_from_schema helper function."""

    def test_handles_detailing_none(self):
        """Should handle explicit null detailing without crashing."""
        # Simulates JSON with "detailing": null
        beam = {
            "beam_id": "B1",
            "story": "Story1",
            "geometry": {"b_mm": 300, "D_mm": 500, "d_mm": 450},
            "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
            "flexure": {"ast_required_mm2": 1000},
            "detailing": None,  # Explicit null
        }

        params = cli_main._extract_beam_params_from_schema(beam)

        # Should not crash, detailing should be empty dict
        assert params["detailing"] == {}
        assert params["ld_tension"] is None
        assert params["lap_length"] is None

    def test_handles_detailing_missing(self):
        """Should handle missing detailing key."""
        beam = {
            "beam_id": "B1",
            "story": "Story1",
            "geometry": {"b_mm": 300, "D_mm": 500, "d_mm": 450},
            "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
            "flexure": {"ast_required_mm2": 1000},
            # No detailing key
        }

        params = cli_main._extract_beam_params_from_schema(beam)
        assert params["detailing"] == {}

    def test_handles_geometry_null(self):
        """Should handle null geometry without crashing."""
        beam = {
            "beam_id": "B1",
            "story": "Story1",
            "geometry": None,
            "materials": None,
            "flexure": None,
            "detailing": None,
        }

        params = cli_main._extract_beam_params_from_schema(beam)

        # Should use defaults
        assert params["b"] == 300.0
        assert params["D"] == 500.0
        assert params["fck"] == 25.0
