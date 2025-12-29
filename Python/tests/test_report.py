"""Tests for report module (V01, V03).

Tests the report data loading, export functions, and critical set export.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from structural_lib.report import (
    load_report_data,
    load_design_results,
    export_json,
    export_design_json,
    export_html,
    render_design_report_single,
    write_design_report_package,
    get_input_sanity,
    get_stability_scorecard,
    get_units_sentinel,
    get_critical_set,
    export_critical_csv,
    export_critical_html,
)
from structural_lib import report_svg


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
            "mu_knm": 150.0,
            "vu_kn": 80.0,
            "is_ok": True,
            "governing_utilization": 0.65,
            "utilizations": {"flexure": 0.65, "shear": 0.40},
            "flexure": {
                "section_type": "UNDER_REINFORCED",
                "pt_provided": 1.2,
                "xu": 120.0,
                "xu_max": 200.0,
            },
            "shear": {"is_safe": True},
        },
        {
            "case_id": "LC2",
            "mu_knm": 200.0,
            "vu_kn": 100.0,
            "is_ok": True,
            "governing_utilization": 0.85,
            "utilizations": {"flexure": 0.85, "shear": 0.50},
            "flexure": {
                "section_type": "UNDER_REINFORCED",
                "pt_provided": 1.5,
                "xu": 140.0,
                "xu_max": 200.0,
            },
            "shear": {"is_safe": True},
        },
    ],
    "summary": {"total_cases": 2, "passed": 2, "failed": 0},
    "job": {
        "job_id": "TEST-001",
        "code": "IS456",
        "units": "IS456",
    },
}

SAMPLE_DESIGN_RESULTS = {
    "schema_version": 1,
    "code": "IS456",
    "units": "IS456",
    "beams": [
        {
            "beam_id": "B1",
            "story": "G",
            "geometry": {
                "b_mm": 300,
                "D_mm": 600,
                "d_mm": 550,
                "span_mm": 4000,
                "cover_mm": 40,
                "d_dash_mm": 50,
            },
            "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
            "loads": {"case_id": "G_B1", "mu_knm": 120, "vu_kn": 80},
            "flexure": {
                "ast_required_mm2": 900.0,
                "section_type": "UNDER_REINFORCED",
                "utilization": 0.7,
            },
            "shear": {"is_safe": True, "utilization": 0.4},
            "serviceability": {
                "deflection_utilization": 0.3,
                "crack_width_utilization": 0.2,
            },
            "is_ok": True,
            "governing_utilization": 0.7,
        },
        {
            "beam_id": "B2",
            "story": "G",
            "geometry": {
                "b_mm": 250,
                "D_mm": 500,
                "d_mm": 450,
                "span_mm": 3500,
                "cover_mm": 40,
                "d_dash_mm": 50,
            },
            "materials": {"fck_nmm2": 20, "fy_nmm2": 415},
            "loads": {"case_id": "G_B2", "mu_knm": 140, "vu_kn": 90},
            "flexure": {
                "ast_required_mm2": 1000.0,
                "section_type": "UNDER_REINFORCED",
                "utilization": 0.85,
            },
            "shear": {"is_safe": True, "utilization": 0.6},
            "serviceability": {
                "deflection_utilization": 0.4,
                "crack_width_utilization": 0.3,
            },
            "is_ok": True,
            "governing_utilization": 0.85,
        },
    ],
    "summary": {"total_beams": 2, "passed": 2, "failed": 0},
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


@pytest.fixture
def sample_design_results_path(tmp_path: Path) -> Path:
    """Create a sample design results JSON file."""
    path = tmp_path / "design_results.json"
    path.write_text(json.dumps(SAMPLE_DESIGN_RESULTS, indent=2), encoding="utf-8")
    return path


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
        assert "input_sanity" in output
        assert "stability_scorecard" in output
        assert "units_sentinel" in output


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
        assert "Input Sanity Heatmap" in html
        assert "Stability Scorecard" in html
        assert "Units Sentinel" in html
        assert "<svg" in html

    def test_export_html_fail_status(self, sample_output_dir: Path) -> None:
        """Test HTML export with failed status."""
        data = load_report_data(sample_output_dir)
        data.is_ok = False
        html = export_html(data)

        assert "✗ FAIL" in html


class TestInputSanity:
    """Tests for input sanity heatmap checks."""

    def test_input_sanity_ok(self, sample_output_dir: Path) -> None:
        data = load_report_data(sample_output_dir)
        items = get_input_sanity(data)
        status_map = {item.field: item.status for item in items}

        assert status_map["b_mm"] == "OK"
        assert status_map["D_mm"] == "OK"
        assert status_map["d_mm"] == "OK"
        assert status_map["b_over_D"] == "OK"
        assert status_map["fck_nmm2"] == "OK"
        assert status_map["fy_nmm2"] == "OK"
        assert status_map["d_dash_mm"] == "OK"
        assert status_map["asv_mm2"] == "OK"

    def test_input_sanity_warns_on_bad_values(self, sample_output_dir: Path) -> None:
        data = load_report_data(sample_output_dir)
        data.beam["b_mm"] = -100
        data.beam["fck_nmm2"] = 5
        items = get_input_sanity(data)

        status_map = {item.field: item.status for item in items}
        assert status_map["b_mm"] == "WARN"
        assert status_map["fck_nmm2"] == "WARN"


class TestStabilityScorecard:
    """Tests for stability scorecard."""

    def test_scorecard_has_expected_checks(self, sample_output_dir: Path) -> None:
        data = load_report_data(sample_output_dir)
        items = get_stability_scorecard(data)

        checks = {item.check for item in items}
        assert {
            "over_reinforced",
            "min_ductility",
            "max_ductility",
            "shear_margin",
            "governing_utilization",
        } == checks

    def test_scorecard_warns_on_over_reinforced(self, sample_output_dir: Path) -> None:
        data = load_report_data(sample_output_dir)
        data.results["cases"][1]["flexure"]["section_type"] = "OVER_REINFORCED"
        items = get_stability_scorecard(data)

        status_map = {item.check: item.status for item in items}
        assert status_map["over_reinforced"] == "WARN"


class TestUnitsSentinel:
    """Tests for units sentinel."""

    def test_units_sentinel_warns_on_large_values(
        self, sample_output_dir: Path
    ) -> None:
        data = load_report_data(sample_output_dir)
        data.results["cases"][0]["mu_knm"] = 1.0e6
        data.results["cases"][0]["vu_kn"] = 2.0e5

        alerts = get_units_sentinel(data)
        fields = {alert.field for alert in alerts}

        assert "mu_knm" in fields
        assert "vu_kn" in fields


class TestDesignResultsReport:
    """Tests for V08 design results reporting."""

    def test_load_design_results(self, sample_design_results_path: Path) -> None:
        data = load_design_results(sample_design_results_path)
        assert data["code"] == "IS456"
        assert len(data["beams"]) == 2

    def test_load_design_results_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_design_results(tmp_path / "missing.json")

    def test_load_design_results_invalid_json(self, tmp_path: Path) -> None:
        bad_path = tmp_path / "bad.json"
        bad_path.write_text("{not-json}", encoding="utf-8")

        with pytest.raises(ValueError, match="Invalid JSON"):
            load_design_results(bad_path)

    def test_load_design_results_non_object(self, tmp_path: Path) -> None:
        bad_path = tmp_path / "list.json"
        bad_path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")

        with pytest.raises(ValueError, match="JSON object"):
            load_design_results(bad_path)

    def test_load_design_results_missing_beams(self, tmp_path: Path) -> None:
        bad_path = tmp_path / "missing_beams.json"
        bad_path.write_text(json.dumps({"code": "IS456"}), encoding="utf-8")

        with pytest.raises(ValueError, match="beams"):
            load_design_results(bad_path)

    def test_export_design_json(self, sample_design_results_path: Path) -> None:
        data = load_design_results(sample_design_results_path)
        output = json.loads(export_design_json(data))

        assert output["code"] == "IS456"
        assert len(output["beams"]) == 2

    def test_render_design_report_single(
        self, sample_design_results_path: Path
    ) -> None:
        data = load_design_results(sample_design_results_path)
        html = render_design_report_single(data, batch_threshold=10)

        assert "<!DOCTYPE html>" in html
        assert "Beam Index" in html
        assert "B1" in html
        assert "B2" in html

    def test_write_design_report_package_folder(
        self, sample_design_results_path: Path, tmp_path: Path
    ) -> None:
        data = load_design_results(sample_design_results_path)
        out_dir = tmp_path / "report"
        written = write_design_report_package(
            data, output_path=out_dir, batch_threshold=1
        )

        assert (out_dir / "index.html") in written
        assert (out_dir / "beams").is_dir()
        assert (out_dir / "beams" / "G_B1.html").exists()

    def test_write_design_report_package_file_output(
        self, sample_design_results_path: Path, tmp_path: Path
    ) -> None:
        data = load_design_results(sample_design_results_path)
        out_file = tmp_path / "report.html"
        written = write_design_report_package(
            data, output_path=out_file, batch_threshold=10
        )

        assert out_file in written
        assert out_file.exists()

    def test_write_design_report_package_html_suffix_folder(
        self, sample_design_results_path: Path, tmp_path: Path
    ) -> None:
        data = load_design_results(sample_design_results_path)
        out_file = tmp_path / "report.html"
        written = write_design_report_package(
            data, output_path=out_file, batch_threshold=1
        )

        out_dir = tmp_path / "report"
        assert (out_dir / "index.html") in written
        assert (out_dir / "beams").is_dir()


class TestReportSvg:
    """Tests for SVG rendering helpers."""

    def test_render_section_svg_basic(self) -> None:
        svg = report_svg.render_section_svg(
            b_mm=300,
            D_mm=600,
            d_mm=550,
            d_dash_mm=50,
        )

        assert svg.startswith("<svg")
        assert "viewBox" in svg
        assert "b = 300 mm" in svg
        assert "D = 600 mm" in svg

    def test_render_section_svg_missing_values(self) -> None:
        svg = report_svg.render_section_svg_from_beam({"b_mm": None})
        assert "Missing b_mm or D_mm" in svg


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


# =============================================================================
# Critical Set Tests (V03)
# =============================================================================


class TestGetCriticalSet:
    """Tests for get_critical_set function."""

    def test_sorts_by_utilization_descending(self, sample_output_dir: Path) -> None:
        """Test that cases are sorted by utilization (highest first)."""
        data = load_report_data(sample_output_dir)
        critical = get_critical_set(data)

        assert len(critical) == 2
        # LC2 has higher utilization (0.85) than LC1 (0.65)
        assert critical[0].case_id == "LC2"
        assert critical[0].utilization == 0.85
        assert critical[1].case_id == "LC1"
        assert critical[1].utilization == 0.65

    def test_top_filter(self, sample_output_dir: Path) -> None:
        """Test top N filter."""
        data = load_report_data(sample_output_dir)

        # Get only top 1
        critical = get_critical_set(data, top=1)

        assert len(critical) == 1
        assert critical[0].case_id == "LC2"

    def test_top_none_returns_all(self, sample_output_dir: Path) -> None:
        """Test that top=None returns all cases."""
        data = load_report_data(sample_output_dir)
        critical = get_critical_set(data, top=None)

        assert len(critical) == 2

    def test_extracts_utilization_values(self, sample_output_dir: Path) -> None:
        """Test that flexure and shear utilization are extracted."""
        data = load_report_data(sample_output_dir)
        critical = get_critical_set(data)

        lc2 = critical[0]
        assert lc2.flexure_util == 0.85
        assert lc2.shear_util == 0.50
        assert lc2.is_ok is True

    def test_json_path_traceability(self, sample_output_dir: Path) -> None:
        """Test that json_path is set for traceability."""
        data = load_report_data(sample_output_dir)
        critical = get_critical_set(data)

        # LC2 is at index 1 in original data, but comes first after sorting
        assert critical[0].json_path == "cases[1]"
        assert critical[1].json_path == "cases[0]"

    def test_empty_cases(self, tmp_path: Path) -> None:
        """Test handling of empty cases array."""
        inputs_dir = tmp_path / "inputs"
        design_dir = tmp_path / "design"
        inputs_dir.mkdir()
        design_dir.mkdir()

        job = {**SAMPLE_JOB}
        results = {"is_ok": True, "cases": []}

        (inputs_dir / "job.json").write_text(json.dumps(job), encoding="utf-8")
        (design_dir / "design_results.json").write_text(
            json.dumps(results), encoding="utf-8"
        )

        data = load_report_data(tmp_path)
        critical = get_critical_set(data)

        assert critical == []


class TestExportCriticalCsv:
    """Tests for export_critical_csv function."""

    def test_csv_header_and_rows(self, sample_output_dir: Path) -> None:
        """Test CSV output has correct header and rows."""
        data = load_report_data(sample_output_dir)
        critical = get_critical_set(data)
        csv_output = export_critical_csv(critical)

        lines = csv_output.strip().split("\n")
        assert len(lines) == 3  # header + 2 data rows

        header = lines[0]
        assert "case_id" in header
        assert "utilization" in header
        assert "flexure_util" in header
        assert "shear_util" in header
        assert "is_ok" in header
        assert "json_path" in header

    def test_csv_values(self, sample_output_dir: Path) -> None:
        """Test CSV values are correct."""
        data = load_report_data(sample_output_dir)
        critical = get_critical_set(data)
        csv_output = export_critical_csv(critical)

        # LC2 should be first row (highest utilization)
        assert "LC2" in csv_output
        assert "0.8500" in csv_output
        assert "TRUE" in csv_output

    def test_empty_cases_csv(self) -> None:
        """Test CSV output for empty cases."""
        csv_output = export_critical_csv([])

        # Should have header only
        lines = csv_output.strip().split("\n")
        assert len(lines) == 1
        assert "case_id" in lines[0]


class TestExportCriticalHtml:
    """Tests for export_critical_html function."""

    def test_html_structure(self, sample_output_dir: Path) -> None:
        """Test HTML output has correct structure."""
        data = load_report_data(sample_output_dir)
        critical = get_critical_set(data)
        html = export_critical_html(critical)

        assert "<!DOCTYPE html>" in html
        assert "<table>" in html
        assert "<thead>" in html
        assert "<tbody>" in html
        assert "Case ID" in html
        assert "Utilization" in html

    def test_html_data_source_attribute(self, sample_output_dir: Path) -> None:
        """Test data-source attribute for traceability."""
        data = load_report_data(sample_output_dir)
        critical = get_critical_set(data)
        html = export_critical_html(critical)

        assert 'data-source="cases[1]"' in html
        assert 'data-source="cases[0]"' in html

    def test_html_utilization_bar(self, sample_output_dir: Path) -> None:
        """Test utilization bar CSS is present."""
        data = load_report_data(sample_output_dir)
        critical = get_critical_set(data)
        html = export_critical_html(critical)

        assert "util-bar" in html
        assert "width:" in html
        assert "85.0%" in html  # LC2 utilization

    def test_html_status_badges(self, sample_output_dir: Path) -> None:
        """Test pass/fail status badges."""
        data = load_report_data(sample_output_dir)
        critical = get_critical_set(data)
        html = export_critical_html(critical)

        assert "✓ PASS" in html
        assert "badge pass" in html

    def test_html_custom_title(self, sample_output_dir: Path) -> None:
        """Test custom title in HTML."""
        data = load_report_data(sample_output_dir)
        critical = get_critical_set(data)
        html = export_critical_html(critical, title="Custom Title")

        assert "Custom Title" in html
