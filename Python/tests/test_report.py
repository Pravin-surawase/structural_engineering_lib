"""Tests for report module (V01).

Tests the report data loading and export functions.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from structural_lib.report import load_report_data, export_json, export_html


# Sample test data matching job output structure
SAMPLE_JOB = {
    "schema_version": 1,
    "job_id": "TEST-001",
    "code": "IS456",
    "units": "IS456",
    "beam": {
        "b_mm": 300,
        "D_mm": 600,
        "d_mm": 550,
        "fck_nmm2": 25,
        "fy_nmm2": 500,
        "d_dash_mm": 50,
        "asv_mm2": 100,
    },
    "cases": [
        {"case_id": "LC1", "Mu_kNm": 150, "Vu_kN": 80},
        {"case_id": "LC2", "Mu_kNm": 200, "Vu_kN": 100},
    ],
}

SAMPLE_RESULTS = {
    "is_ok": True,
    "governing_case_id": "LC2",
    "governing_utilization": 0.85,
    "cases": [
        {
            "case_id": "LC1",
            "is_ok": True,
            "governing_utilization": 0.65,
            "utilizations": {"flexure": 0.65, "shear": 0.40},
        },
        {
            "case_id": "LC2",
            "is_ok": True,
            "governing_utilization": 0.85,
            "utilizations": {"flexure": 0.85, "shear": 0.50},
        },
    ],
    "summary": {"total_cases": 2, "passed": 2, "failed": 0},
    "job": {
        "job_id": "TEST-001",
        "code": "IS456",
        "units": "IS456",
    },
}


@pytest.fixture
def sample_output_dir(tmp_path: Path) -> Path:
    """Create a sample job output directory structure."""
    inputs_dir = tmp_path / "inputs"
    design_dir = tmp_path / "design"
    inputs_dir.mkdir()
    design_dir.mkdir()

    # Write job.json
    (inputs_dir / "job.json").write_text(
        json.dumps(SAMPLE_JOB, indent=2), encoding="utf-8"
    )

    # Write design_results.json
    (design_dir / "design_results.json").write_text(
        json.dumps(SAMPLE_RESULTS, indent=2), encoding="utf-8"
    )

    return tmp_path


class TestLoadReportData:
    """Tests for load_report_data function."""

    def test_load_from_output_folder(self, sample_output_dir: Path) -> None:
        """Test loading report data from standard output folder."""
        data = load_report_data(sample_output_dir)

        assert data.job_id == "TEST-001"
        assert data.code == "IS456"
        assert data.units == "IS456"
        assert data.is_ok is True
        assert data.governing_case_id == "LC2"
        assert data.governing_utilization == 0.85
        assert data.beam["b_mm"] == 300
        assert len(data.cases) == 2

    def test_load_with_explicit_paths(self, sample_output_dir: Path) -> None:
        """Test loading with explicit file paths."""
        job_path = sample_output_dir / "inputs" / "job.json"
        results_path = sample_output_dir / "design" / "design_results.json"

        data = load_report_data(
            sample_output_dir, job_path=job_path, results_path=results_path
        )

        assert data.job_id == "TEST-001"
        assert data.is_ok is True

    def test_missing_job_file_raises(self, tmp_path: Path) -> None:
        """Test that missing job.json raises FileNotFoundError."""
        design_dir = tmp_path / "design"
        design_dir.mkdir()
        (design_dir / "design_results.json").write_text("{}", encoding="utf-8")

        with pytest.raises(FileNotFoundError, match="Job file not found"):
            load_report_data(tmp_path)

    def test_missing_results_file_raises(self, tmp_path: Path) -> None:
        """Test that missing design_results.json raises FileNotFoundError."""
        inputs_dir = tmp_path / "inputs"
        inputs_dir.mkdir()
        (inputs_dir / "job.json").write_text(json.dumps(SAMPLE_JOB), encoding="utf-8")

        with pytest.raises(FileNotFoundError, match="Results file not found"):
            load_report_data(tmp_path)

    def test_malformed_job_json_raises(self, tmp_path: Path) -> None:
        """Test that malformed job.json raises ValueError."""
        inputs_dir = tmp_path / "inputs"
        design_dir = tmp_path / "design"
        inputs_dir.mkdir()
        design_dir.mkdir()

        (inputs_dir / "job.json").write_text("not valid json", encoding="utf-8")
        (design_dir / "design_results.json").write_text("{}", encoding="utf-8")

        with pytest.raises(ValueError, match="Invalid JSON"):
            load_report_data(tmp_path)

    def test_missing_beam_raises(self, tmp_path: Path) -> None:
        """Test that job without 'beam' raises ValueError."""
        inputs_dir = tmp_path / "inputs"
        design_dir = tmp_path / "design"
        inputs_dir.mkdir()
        design_dir.mkdir()

        bad_job = {"schema_version": 1, "job_id": "X", "cases": []}
        (inputs_dir / "job.json").write_text(json.dumps(bad_job), encoding="utf-8")
        (design_dir / "design_results.json").write_text("{}", encoding="utf-8")

        with pytest.raises(ValueError, match="missing 'beam'"):
            load_report_data(tmp_path)


class TestExportJson:
    """Tests for export_json function."""

    def test_export_json_deterministic(self, sample_output_dir: Path) -> None:
        """Test that JSON export is deterministic (sorted keys)."""
        data = load_report_data(sample_output_dir)

        json1 = export_json(data)
        json2 = export_json(data)

        assert json1 == json2

        # Verify it's valid JSON
        parsed = json.loads(json1)
        assert parsed["job_id"] == "TEST-001"
        assert parsed["is_ok"] is True

    def test_export_json_contains_required_fields(
        self, sample_output_dir: Path
    ) -> None:
        """Test that JSON export contains all required fields."""
        data = load_report_data(sample_output_dir)
        output = json.loads(export_json(data))

        assert "job_id" in output
        assert "code" in output
        assert "units" in output
        assert "is_ok" in output
        assert "governing_case_id" in output
        assert "governing_utilization" in output
        assert "beam" in output
        assert "cases" in output


class TestExportHtml:
    """Tests for export_html function."""

    def test_export_html_basic(self, sample_output_dir: Path) -> None:
        """Test basic HTML export."""
        data = load_report_data(sample_output_dir)
        html = export_html(data)

        assert "<!DOCTYPE html>" in html
        assert "TEST-001" in html
        assert "IS456" in html
        assert "✓ PASS" in html  # is_ok = True

    def test_export_html_fail_status(self, sample_output_dir: Path) -> None:
        """Test HTML export with failed status."""
        data = load_report_data(sample_output_dir)
        data.is_ok = False
        html = export_html(data)

        assert "✗ FAIL" in html


class TestLoadJobSpec:
    """Tests for load_job_spec in job_runner module."""

    def test_load_job_spec_valid(self, tmp_path: Path) -> None:
        """Test loading a valid job spec."""
        from structural_lib.job_runner import load_job_spec

        job_file = tmp_path / "job.json"
        job_file.write_text(json.dumps(SAMPLE_JOB), encoding="utf-8")

        spec = load_job_spec(job_file)

        assert spec["job_id"] == "TEST-001"
        assert spec["code"] == "IS456"
        assert spec["schema_version"] == 1
        assert spec["beam"]["b_mm"] == 300
        assert len(spec["cases"]) == 2

    def test_load_job_spec_missing_file(self, tmp_path: Path) -> None:
        """Test that missing file raises FileNotFoundError."""
        from structural_lib.job_runner import load_job_spec

        with pytest.raises(FileNotFoundError):
            load_job_spec(tmp_path / "nonexistent.json")

    def test_load_job_spec_missing_schema_version(self, tmp_path: Path) -> None:
        """Test that missing schema_version raises ValueError."""
        from structural_lib.job_runner import load_job_spec

        bad_job = {"job_id": "X", "code": "IS456", "beam": {}, "cases": []}
        job_file = tmp_path / "job.json"
        job_file.write_text(json.dumps(bad_job), encoding="utf-8")

        with pytest.raises(ValueError, match="schema_version"):
            load_job_spec(job_file)
