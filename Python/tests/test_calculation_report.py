# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tests for the calculation_report module (TASK-277).

Tests cover:
- ProjectInfo creation and defaults
- InputSection and ResultSection data classes
- CalculationReport creation and serialization
- HTML, JSON, and Markdown export
- Report generation convenience function
"""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from structural_lib.calculation_report import (
    CalculationReport,
    InputSection,
    ProjectInfo,
    ResultSection,
    _format_number,
    generate_calculation_report,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_project_info() -> dict[str, str]:
    """Sample project information."""
    return {
        "project_name": "Tower A Design",
        "project_number": "PRJ-2026-001",
        "client_name": "ABC Builders",
        "engineer_name": "John Doe",
        "checker_name": "Jane Smith",
        "revision": "B",
    }


@pytest.fixture
def sample_input_section() -> InputSection:
    """Sample input section with geometry and materials."""
    return InputSection(
        geometry={
            "beam_id": "B1",
            "story": "GF",
            "b_mm": 300,
            "D_mm": 500,
            "d_mm": 460,
            "span_mm": 6000,
            "cover_mm": 40,
        },
        materials={"fck_nmm2": 25, "fy_nmm2": 500},
        loads=[{"case": "DL+LL", "mu_knm": 150, "vu_kn": 100}],
        detailing={"stirrup_dia_mm": 8, "spacing_mm": 150},
    )


@pytest.fixture
def sample_result_section() -> ResultSection:
    """Sample result section with flexure and shear."""
    return ResultSection(
        flexure={
            "ast_required": 942.48,
            "ast_provided": 1017.88,
            "beam_type": "singly reinforced",
        },
        shear={"vu_kn": 100, "vc_kn": 65, "vs_kn": 50, "is_ok": True},
        serviceability={"deflection_ratio": 0.85, "crack_width_mm": 0.25},
        detailing={"main_bars": "3-20φ", "stirrups": "8φ@150 c/c"},
        summary={"is_ok": True, "summary": "Design satisfies all IS 456 requirements."},
    )


@pytest.fixture
def mock_design_result(sample_input_section, sample_result_section) -> MagicMock:
    """Mock design result with all expected attributes."""
    result = MagicMock()

    # Geometry and materials
    result.geometry = sample_input_section.geometry
    result.materials = sample_input_section.materials

    # Design object with flexure and shear
    result.design = MagicMock()
    result.design.flexure = MagicMock()
    result.design.flexure.ast_required = 942.48
    result.design.flexure.ast_provided = 1017.88
    result.design.flexure.beam_type = "singly reinforced"

    result.design.shear = MagicMock()
    result.design.shear.vu_kn = 100.0
    result.design.shear.vc_kn = 65.0
    result.design.shear.vs_kn = 50.0
    result.design.shear.is_ok = True

    result.is_ok = True
    result.summary = MagicMock(return_value="Design OK")

    return result


# =============================================================================
# Test ProjectInfo
# =============================================================================


class TestProjectInfo:
    """Tests for ProjectInfo dataclass."""

    def test_default_values(self):
        """Test ProjectInfo with default values."""
        info = ProjectInfo()
        assert info.project_name == "Untitled Project"
        assert info.project_number == ""
        assert info.revision == "A"
        assert info.date != ""  # Auto-set to current date

    def test_custom_values(self, sample_project_info):
        """Test ProjectInfo with custom values."""
        info = ProjectInfo(**sample_project_info)
        assert info.project_name == "Tower A Design"
        assert info.project_number == "PRJ-2026-001"
        assert info.client_name == "ABC Builders"
        assert info.engineer_name == "John Doe"
        assert info.checker_name == "Jane Smith"
        assert info.revision == "B"

    def test_date_auto_set(self):
        """Test that date is auto-set if not provided."""
        info = ProjectInfo(project_name="Test")
        assert len(info.date) == 10  # YYYY-MM-DD format
        assert "-" in info.date

    def test_date_preserved(self):
        """Test that provided date is preserved."""
        info = ProjectInfo(project_name="Test", date="2026-01-15")
        assert info.date == "2026-01-15"


# =============================================================================
# Test InputSection
# =============================================================================


class TestInputSection:
    """Tests for InputSection dataclass."""

    def test_default_empty(self):
        """Test InputSection with default empty values."""
        section = InputSection()
        assert section.geometry == {}
        assert section.materials == {}
        assert section.loads == []
        assert section.detailing == {}

    def test_populated_section(self, sample_input_section):
        """Test fully populated InputSection."""
        assert sample_input_section.geometry["b_mm"] == 300
        assert sample_input_section.materials["fck_nmm2"] == 25
        assert len(sample_input_section.loads) == 1
        assert sample_input_section.detailing["stirrup_dia_mm"] == 8


# =============================================================================
# Test ResultSection
# =============================================================================


class TestResultSection:
    """Tests for ResultSection dataclass."""

    def test_default_empty(self):
        """Test ResultSection with default empty values."""
        section = ResultSection()
        assert section.flexure == {}
        assert section.shear == {}
        assert section.serviceability == {}
        assert section.detailing == {}
        assert section.summary == {}

    def test_populated_section(self, sample_result_section):
        """Test fully populated ResultSection."""
        assert sample_result_section.flexure["ast_required"] == 942.48
        assert sample_result_section.shear["vu_kn"] == 100
        assert sample_result_section.shear["is_ok"] is True
        assert sample_result_section.summary["is_ok"] is True


# =============================================================================
# Test CalculationReport
# =============================================================================


class TestCalculationReport:
    """Tests for CalculationReport class."""

    def test_basic_creation(self):
        """Test creating a basic report."""
        report = CalculationReport(
            report_id="CALC-B1-GF-001",
            project_info=ProjectInfo(),
            beam_id="B1",
            story="GF",
            inputs=InputSection(),
            results=ResultSection(),
        )
        assert report.report_id == "CALC-B1-GF-001"
        assert report.beam_id == "B1"
        assert report.story == "GF"
        assert report.generated_at != ""

    def test_from_design_result(self, mock_design_result, sample_project_info):
        """Test creating report from design result."""
        report = CalculationReport.from_design_result(
            result=mock_design_result,
            beam_id="B2",
            story="1F",
            project_info=sample_project_info,
        )
        assert "B2" in report.report_id
        assert report.beam_id == "B2"
        assert report.story == "1F"
        assert report.project_info.project_name == "Tower A Design"

    def test_from_design_result_extracts_geometry(self, mock_design_result):
        """Test that geometry is correctly extracted."""
        report = CalculationReport.from_design_result(
            result=mock_design_result, beam_id="B1"
        )
        assert report.inputs.geometry["b_mm"] == 300
        assert report.inputs.geometry["D_mm"] == 500
        assert report.inputs.geometry["d_mm"] == 460

    def test_from_design_result_extracts_flexure(self, mock_design_result):
        """Test that flexure results are correctly extracted."""
        report = CalculationReport.from_design_result(result=mock_design_result)
        assert report.results.flexure["ast_required"] == 942.48
        assert report.results.flexure["ast_provided"] == 1017.88
        assert report.results.flexure["beam_type"] == "singly reinforced"

    def test_from_design_result_extracts_shear(self, mock_design_result):
        """Test that shear results are correctly extracted."""
        report = CalculationReport.from_design_result(result=mock_design_result)
        assert report.results.shear["vu_kn"] == 100.0
        assert report.results.shear["vc_kn"] == 65.0
        assert report.results.shear["is_ok"] is True

    def test_to_dict(self, mock_design_result, sample_project_info):
        """Test serializing report to dictionary."""
        report = CalculationReport.from_design_result(
            result=mock_design_result, project_info=sample_project_info
        )
        data = report.to_dict()

        assert "report_id" in data
        assert "generated_at" in data
        assert "project_info" in data
        assert data["project_info"]["project_name"] == "Tower A Design"
        assert "inputs" in data
        assert "results" in data

    def test_to_json(self, mock_design_result):
        """Test serializing report to JSON."""
        report = CalculationReport.from_design_result(result=mock_design_result)
        json_str = report.to_json()

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert "report_id" in parsed
        assert "beam_id" in parsed

    def test_code_references_and_notes(self, mock_design_result):
        """Test adding code references and notes."""
        report = CalculationReport.from_design_result(result=mock_design_result)
        report.code_references = [
            "IS 456:2000 Cl. 26.5.1.1",
            "IS 456:2000 Cl. 40.4",
        ]
        report.notes = ["Assumed seismic zone III", "Clear span used for calculations"]

        data = report.to_dict()
        assert len(data["code_references"]) == 2
        assert len(data["notes"]) == 2

    def test_verification_hash(self, mock_design_result):
        """Test adding verification hash."""
        report = CalculationReport.from_design_result(result=mock_design_result)
        report.verification_hash = "abc123def456" * 4  # 48 char hash

        data = report.to_dict()
        assert len(data["verification_hash"]) > 0


# =============================================================================
# Test Export Functions
# =============================================================================


class TestExportFunctions:
    """Tests for report export functions."""

    def test_export_json(self, mock_design_result):
        """Test exporting report to JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = CalculationReport.from_design_result(result=mock_design_result)
            path = Path(tmpdir) / "test_report.json"
            result_path = report.export_json(path)

            assert result_path.exists()
            assert result_path.suffix == ".json"

            # Verify content
            with open(result_path) as f:
                data = json.load(f)
            assert "report_id" in data
            assert "beam_id" in data

    def test_export_json_creates_directories(self, mock_design_result):
        """Test that export creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = CalculationReport.from_design_result(result=mock_design_result)
            path = Path(tmpdir) / "subdir" / "nested" / "report.json"
            result_path = report.export_json(path)

            assert result_path.exists()
            assert result_path.parent.exists()

    def test_export_html(self, mock_design_result, sample_project_info):
        """Test exporting report to HTML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = CalculationReport.from_design_result(
                result=mock_design_result, project_info=sample_project_info
            )
            path = Path(tmpdir) / "test_report.html"
            result_path = report.export_html(path)

            assert result_path.exists()
            assert result_path.suffix == ".html"

            content = result_path.read_text()
            assert "<!DOCTYPE html>" in content
            assert "Tower A Design" in content
            assert "B1" in content
            assert "IS 456:2000" in content

    def test_export_html_contains_structure(self, mock_design_result):
        """Test that HTML contains expected structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = CalculationReport.from_design_result(result=mock_design_result)
            path = Path(tmpdir) / "report.html"
            report.export_html(path)

            content = path.read_text()
            # Check for major sections
            assert "<style>" in content
            assert "Input Data" in content
            assert "Design Results" in content
            assert "Flexure" in content
            assert "Shear" in content
            assert "DESIGN STATUS" in content

    def test_export_html_status_pass(self, mock_design_result):
        """Test that PASS status is shown correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = CalculationReport.from_design_result(result=mock_design_result)
            path = Path(tmpdir) / "report.html"
            report.export_html(path)

            content = path.read_text()
            assert "PASS" in content
            assert "status-pass" in content

    def test_export_html_status_fail(self, mock_design_result):
        """Test that FAIL status is shown correctly."""
        mock_design_result.is_ok = False

        with tempfile.TemporaryDirectory() as tmpdir:
            report = CalculationReport.from_design_result(result=mock_design_result)
            path = Path(tmpdir) / "report.html"
            report.export_html(path)

            content = path.read_text()
            assert "FAIL" in content
            assert "status-fail" in content

    def test_export_markdown(self, mock_design_result, sample_project_info):
        """Test exporting report to Markdown file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = CalculationReport.from_design_result(
                result=mock_design_result, project_info=sample_project_info
            )
            path = Path(tmpdir) / "test_report.md"
            result_path = report.export_markdown(path)

            assert result_path.exists()
            assert result_path.suffix == ".md"

            content = result_path.read_text()
            assert "# Calculation Report:" in content
            assert "Tower A Design" in content
            assert "## 1. Input Data" in content
            assert "## 2. Design Results" in content
            assert "✅ PASS" in content

    def test_export_markdown_tables(self, mock_design_result):
        """Test that Markdown contains proper tables."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = CalculationReport.from_design_result(result=mock_design_result)
            path = Path(tmpdir) / "report.md"
            report.export_markdown(path)

            content = path.read_text()
            # Check for table structure
            assert "| Parameter | Value | Units |" in content
            assert "|-----------|-------|-------|" in content


# =============================================================================
# Test Convenience Function
# =============================================================================


class TestGenerateCalculationReport:
    """Tests for the generate_calculation_report convenience function."""

    def test_basic_generation(self, mock_design_result):
        """Test basic report generation without export."""
        report = generate_calculation_report(
            result=mock_design_result, beam_id="B1", story="GF"
        )
        assert isinstance(report, CalculationReport)
        assert report.beam_id == "B1"
        assert report.story == "GF"

    def test_with_project_info(self, mock_design_result, sample_project_info):
        """Test generation with project info."""
        report = generate_calculation_report(
            result=mock_design_result, project_info=sample_project_info
        )
        assert report.project_info.project_name == "Tower A Design"

    def test_with_html_export(self, mock_design_result):
        """Test generation with HTML export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.html"
            report = generate_calculation_report(
                result=mock_design_result,
                output_path=path,
                output_format="html",
            )
            assert path.exists()
            assert report is not None

    def test_with_json_export(self, mock_design_result):
        """Test generation with JSON export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.json"
            _report = generate_calculation_report(
                result=mock_design_result,
                output_path=path,
                output_format="json",
            )
            assert path.exists()

    def test_with_markdown_export(self, mock_design_result):
        """Test generation with Markdown export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.md"
            _report = generate_calculation_report(
                result=mock_design_result,
                output_path=path,
                output_format="markdown",
            )
            assert path.exists()

    def test_invalid_format(self, mock_design_result):
        """Test that invalid format raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.txt"
            with pytest.raises(ValueError, match="Unknown format"):
                generate_calculation_report(
                    result=mock_design_result,
                    output_path=path,
                    output_format="txt",
                )


# =============================================================================
# Test Helper Functions
# =============================================================================


class TestFormatNumber:
    """Tests for the _format_number helper."""

    def test_none_returns_na(self):
        """Test that None returns 'N/A'."""
        assert _format_number(None) == "N/A"

    def test_integer_no_decimals(self):
        """Test that whole numbers have no decimals."""
        assert _format_number(100) == "100"
        assert _format_number(100.0) == "100"

    def test_decimal_two_places(self):
        """Test that decimals are formatted to 2 places."""
        assert _format_number(123.456) == "123.46"
        assert _format_number(0.1) == "0.10"

    def test_string_passthrough(self):
        """Test that strings are passed through."""
        assert _format_number("N/A") == "N/A"
        assert _format_number("text") == "text"


# =============================================================================
# Test Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_result(self):
        """Test handling of minimal/empty result."""
        result = MagicMock()
        result.geometry = {}
        result.materials = {}
        result.design = MagicMock()
        result.design.flexure = MagicMock()
        result.design.flexure.ast_required = 0
        result.design.flexure.ast_provided = 0
        result.design.flexure.beam_type = "unknown"
        result.design.shear = MagicMock()
        result.design.shear.vu_kn = 0
        result.design.shear.vc_kn = 0
        result.design.shear.vs_kn = 0
        result.design.shear.is_ok = True
        result.is_ok = True
        result.summary = MagicMock(return_value="")

        report = CalculationReport.from_design_result(result=result)
        # Should not raise
        json_str = report.to_json()
        assert json_str is not None

    def test_result_without_design(self):
        """Test handling of compliance result (without .design)."""

        @dataclass
        class MockFlexure:
            ast_required: float = 500.0
            pt_provided: float = 0.5

        @dataclass
        class MockShear:
            spacing: float = 150.0
            is_safe: bool = True

        result = MagicMock(spec=["flexure", "shear", "is_ok"])
        result.flexure = MockFlexure()
        result.shear = MockShear()
        result.is_ok = True

        # Should handle this case
        report = CalculationReport.from_design_result(result=result)
        assert report.results.flexure["ast_required"] == 500.0

    def test_special_characters_escaped_in_html(self, mock_design_result):
        """Test that special characters are escaped in HTML."""
        report = CalculationReport.from_design_result(
            result=mock_design_result,
            project_info={"project_name": "<script>alert('XSS')</script>"},
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "report.html"
            report.export_html(path)

            content = path.read_text()
            # Should be escaped
            assert "<script>" not in content
            assert "&lt;script&gt;" in content

    def test_verification_hash_in_exports(self, mock_design_result):
        """Test that verification hash appears in exports."""
        report = CalculationReport.from_design_result(result=mock_design_result)
        report.verification_hash = "a" * 64

        with tempfile.TemporaryDirectory() as tmpdir:
            # HTML
            html_path = Path(tmpdir) / "report.html"
            report.export_html(html_path)
            assert "aaaa" in html_path.read_text()

            # Markdown
            md_path = Path(tmpdir) / "report.md"
            report.export_markdown(md_path)
            assert "aaaa" in md_path.read_text()
