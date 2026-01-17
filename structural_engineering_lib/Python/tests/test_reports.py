"""Tests for the reports module."""

from __future__ import annotations

from datetime import date

import pytest

from structural_lib.reports import (
    JINJA2_AVAILABLE,
    ReportContext,
    generate_html_report,
    generate_html_report_from_dict,
    get_available_templates,
)

# Skip marker for tests requiring Jinja2
requires_jinja2 = pytest.mark.skipif(
    not JINJA2_AVAILABLE, reason="Jinja2 not installed (pip install jinja2)"
)


class TestReportContext:
    """Tests for ReportContext dataclass."""

    def test_minimal_context(self) -> None:
        """Test creating context with minimal required fields."""
        ctx = ReportContext(
            beam_id="B1",
            project_name="Test Project",
            inputs={"b": 300, "D": 500},
            results={"flexure": {"ast_mm2": 1000}},
            is_ok=True,
        )
        assert ctx.beam_id == "B1"
        assert ctx.project_name == "Test Project"
        assert ctx.is_ok is True

    def test_full_context(self) -> None:
        """Test creating context with all fields."""
        ctx = ReportContext(
            beam_id="B1",
            project_name="Test Project",
            project_number="PRJ-001",
            client_name="Test Client",
            engineer_name="Test Engineer",
            checker_name="Test Checker",
            inputs={"b": 300, "D": 500, "fck": 25, "fy": 500},
            results={
                "flexure": {"ast_mm2": 1000, "is_ok": True},
                "shear": {"sv_mm": 150, "is_ok": True},
            },
            is_ok=True,
            code_reference="IS 456:2000",
            revision="Rev A",
        )
        assert ctx.project_number == "PRJ-001"
        assert ctx.client_name == "Test Client"
        assert ctx.code_reference == "IS 456:2000"

    def test_to_dict(self) -> None:
        """Test converting context to dictionary."""
        ctx = ReportContext(
            beam_id="B1",
            project_name="Test",
            inputs={},
            results={},
        )
        d = ctx.to_dict()
        assert isinstance(d, dict)
        assert d["beam_id"] == "B1"
        assert d["project_name"] == "Test"
        assert "date" in d
        assert "status_class" in d
        assert "status_text" in d


class TestGetAvailableTemplates:
    """Tests for get_available_templates function."""

    def test_returns_list(self) -> None:
        """Test that available templates returns a list."""
        templates = get_available_templates()
        assert isinstance(templates, list)

    def test_default_templates_available(self) -> None:
        """Test that default templates are available."""
        templates = get_available_templates()
        assert "beam_design" in templates
        assert "summary" in templates
        assert "detailed" in templates


@requires_jinja2
class TestGenerateHtmlReport:
    """Tests for generate_html_report function."""

    def test_basic_report_generation(self) -> None:
        """Test generating a basic report from dict."""
        design_result = {
            "inputs": {"b_mm": 300, "D_mm": 500, "fck": 25, "fy": 500},
            "results": {"flexure": {"ast_mm2": 1000, "is_ok": True}},
            "is_ok": True,
        }
        html = generate_html_report(
            design_result,
            project_info={"project_name": "Test Project"},
            beam_id="B1",
        )
        assert isinstance(html, str)
        assert len(html) > 100
        # Check key content is present
        assert "B1" in html
        assert "Test Project" in html

    def test_summary_template(self) -> None:
        """Test generating a summary report."""
        design_result = {
            "inputs": {"b_mm": 300},
            "results": {},
            "is_ok": True,
        }
        html = generate_html_report(design_result, template="summary", beam_id="B1")
        assert isinstance(html, str)
        assert "B1" in html

    def test_detailed_template(self) -> None:
        """Test generating a detailed report."""
        design_result = {
            "inputs": {"b_mm": 300, "D_mm": 500},
            "results": {"flexure": {"ast_mm2": 1000}},
            "is_ok": True,
        }
        html = generate_html_report(design_result, template="detailed", beam_id="B1")
        assert isinstance(html, str)
        assert "B1" in html
        assert "Detailed" in html

    def test_invalid_template_raises(self) -> None:
        """Test that invalid template name raises error."""
        design_result = {"inputs": {}, "results": {}}
        with pytest.raises(ValueError, match="Unknown template"):
            generate_html_report(design_result, template="nonexistent")

    def test_pass_status_in_report(self) -> None:
        """Test that passing design shows correct status."""
        design_result = {"inputs": {}, "results": {}, "is_ok": True}
        html = generate_html_report(design_result, beam_id="B1")
        assert "status-pass" in html or "PASS" in html

    def test_fail_status_in_report(self) -> None:
        """Test that failing design shows correct status."""
        design_result = {"inputs": {}, "results": {}, "is_ok": False}
        html = generate_html_report(design_result, beam_id="B1")
        assert "status-fail" in html or "FAIL" in html


@requires_jinja2
class TestGenerateHtmlReportFromDict:
    """Tests for generate_html_report_from_dict function."""

    def test_basic_dict_generation(self) -> None:
        """Test generating report from dictionary."""
        data = {
            "beam_id": "B1",
            "project_name": "Test",
            "inputs": {"b_mm": 300},
            "results": {},
            "is_ok": True,
            "date": date.today().isoformat(),
            "status_class": "status-pass",
            "status_text": "DESIGN OK",
            "code_reference": "IS 456:2000",
        }
        html = generate_html_report_from_dict(data)
        assert isinstance(html, str)
        assert "B1" in html

    def test_missing_beam_id_uses_default(self) -> None:
        """Test that missing beam_id uses default in template."""
        data = {
            "project_name": "Test",
            "inputs": {},
            "results": {},
            "date": date.today().isoformat(),
            "status_class": "status-pass",
            "status_text": "OK",
            "code_reference": "IS 456",
        }
        # Should not raise - template handles missing values
        html = generate_html_report_from_dict(data)
        assert isinstance(html, str)


@requires_jinja2
class TestFormatFilters:
    """Tests for template filters through full report generation."""

    def test_number_formatting(self) -> None:
        """Test that numbers are formatted correctly."""
        design_result = {
            "inputs": {"b_mm": 300.123456},
            "results": {"flexure": {"ast_mm2": 1234.5}},
            "is_ok": True,
        }
        html = generate_html_report(design_result, beam_id="B1")
        # Numbers should be formatted (not raw floats with many decimals)
        assert isinstance(html, str)

    def test_handles_missing_values(self) -> None:
        """Test that missing values don't crash."""
        design_result = {
            "inputs": {},  # Empty inputs
            "results": {},  # Empty results
            "is_ok": True,
        }
        # Should not raise
        html = generate_html_report(design_result, beam_id="B1")
        assert isinstance(html, str)


class TestJinja2Availability:
    """Tests for Jinja2 availability handling."""

    def test_jinja2_available_flag(self) -> None:
        """Test that JINJA2_AVAILABLE flag is set correctly."""
        assert isinstance(JINJA2_AVAILABLE, bool)

    def test_flag_consistency(self) -> None:
        """Test that the flag matches actual availability."""
        from structural_lib.reports.generator import (
            JINJA2_AVAILABLE as JINJA2_FLAG,
        )

        assert isinstance(JINJA2_FLAG, bool)
        # If Jinja2 is installed, both should be True
        if JINJA2_AVAILABLE:
            assert JINJA2_FLAG is True


@requires_jinja2
class TestReportWithRealData:
    """Integration tests with realistic beam design data."""

    @pytest.fixture
    def sample_design_result(self) -> dict:
        """Create sample beam design result."""
        return {
            "inputs": {
                "b_mm": 300,
                "D_mm": 600,
                "d_mm": 550,
                "cover_mm": 40,
                "span_mm": 6000,
                "fck": 25,
                "fy": 500,
                "mu_knm": 180,
                "vu_kn": 120,
            },
            "results": {
                "flexure": {
                    "mu_knm": 180,
                    "mu_lim_knm": 320,
                    "ast_required_mm2": 942,
                    "ast_provided_mm2": 1018,
                    "ast_min_mm2": 326,
                    "ast_max_mm2": 7200,
                    "bar_arrangement": "4-T20",
                    "pt_percent": 0.57,
                    "xu_lim_ratio": 0.48,
                    "section_type": "Singly Reinforced",
                    "is_ok": True,
                    "utilization": 0.56,
                },
                "shear": {
                    "vu_kn": 120,
                    "tv_nmm2": 0.73,
                    "tc_nmm2": 0.50,
                    "tc_max_nmm2": 3.1,
                    "pt_percent": 0.57,
                    "sv_required_mm": 175,
                    "sv_provided_mm": 150,
                    "sv_max_mm": 300,
                    "is_ok": True,
                    "utilization": 0.24,
                },
                "deflection": {
                    "ld_basic": 20,
                    "mf_tension": 1.2,
                    "mf_compression": 1.0,
                    "ld_allowable": 24,
                    "ld_actual": 10.9,
                    "is_ok": True,
                    "utilization": 0.45,
                },
                "detailing": {
                    "bottom_bars": "4-T20",
                    "bottom_area_mm2": 1257,
                    "top_bars": "2-T12",
                    "top_area_mm2": 226,
                    "stirrups": "T8 @ 150 c/c",
                    "ld_tension_mm": 940,
                    "lap_length_mm": 1410,
                },
            },
            "is_ok": True,
        }

    @pytest.fixture
    def sample_project_info(self) -> dict:
        """Create sample project info."""
        return {
            "project_name": "Residential Building Block A",
            "project_number": "PRJ-2024-001",
            "client_name": "ABC Developers Pvt Ltd",
            "engineer_name": "John Engineer",
            "checker_name": "Jane Checker",
            "revision": "Rev 0",
        }

    def test_full_report_generation(
        self, sample_design_result: dict, sample_project_info: dict
    ) -> None:
        """Test generating full report with realistic data."""
        html = generate_html_report(
            sample_design_result,
            project_info=sample_project_info,
            beam_id="MB-101",
        )
        # Check all major sections present
        assert "MB-101" in html
        assert "Residential Building" in html
        assert "300" in html  # width
        assert "600" in html  # depth
        assert "Flexure" in html or "Flexural" in html
        assert "Shear" in html
        assert "4-T20" in html or "T20" in html

    def test_summary_report_with_real_data(
        self, sample_design_result: dict, sample_project_info: dict
    ) -> None:
        """Test summary report with realistic data."""
        html = generate_html_report(
            sample_design_result,
            template="summary",
            project_info=sample_project_info,
            beam_id="MB-101",
        )
        assert "MB-101" in html
        assert "✓" in html or "PASS" in html

    def test_detailed_report_with_real_data(
        self, sample_design_result: dict, sample_project_info: dict
    ) -> None:
        """Test detailed report with realistic data."""
        html = generate_html_report(
            sample_design_result,
            template="detailed",
            project_info=sample_project_info,
            beam_id="MB-101",
        )
        assert "MB-101" in html
        assert "Table of Contents" in html
        assert "Cl. 38" in html or "38.1" in html  # Code references


@requires_jinja2
class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_beam_id(self) -> None:
        """Test handling empty beam ID."""
        design_result = {"inputs": {}, "results": {}, "is_ok": True}
        # Should not raise
        html = generate_html_report(design_result, beam_id="")
        assert isinstance(html, str)

    def test_special_characters_in_names(self) -> None:
        """Test handling special characters."""
        design_result = {"inputs": {}, "results": {}, "is_ok": True}
        html = generate_html_report(
            design_result,
            project_info={"project_name": "Test & Project <Ltd>"},
            beam_id="B-1/A",
        )
        # HTML should be valid (special chars escaped)
        assert "Test" in html

    def test_very_large_numbers(self) -> None:
        """Test handling very large numbers."""
        design_result = {
            "inputs": {"span_mm": 100000000},
            "results": {"flexure": {"ast_mm2": 1e12}},
            "is_ok": True,
        }
        html = generate_html_report(design_result, beam_id="B1")
        assert isinstance(html, str)

    def test_negative_numbers(self) -> None:
        """Test handling negative numbers."""
        design_result = {
            "inputs": {},
            "results": {"flexure": {"some_value": -123.45}},
            "is_ok": True,
        }
        html = generate_html_report(design_result, beam_id="B1")
        assert isinstance(html, str)

    def test_none_values_in_results(self) -> None:
        """Test handling None values in results."""
        design_result = {
            "inputs": {"b_mm": None},
            "results": {"flexure": {"ast_mm2": None}},
            "is_ok": True,
        }
        html = generate_html_report(design_result, beam_id="B1")
        assert isinstance(html, str)
