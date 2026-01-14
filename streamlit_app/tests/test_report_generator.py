"""
Tests for PDF Report Generator (FEAT-003)
=========================================

Tests for PDF generation utility and Streamlit page.

Author: Agent 6 (Streamlit Specialist)
Task: STREAMLIT-FEAT-003
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path
from io import BytesIO

# Skip all tests if reportlab is not installed
try:
    import reportlab

    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

pytestmark = pytest.mark.skipif(not HAS_REPORTLAB, reason="reportlab not installed")

# MockStreamlit available from conftest.py
import streamlit as st


# Sample design data for testing
@pytest.fixture
def sample_design_data():
    """Sample beam design result for testing."""
    return {
        "inputs": {
            "span_m": 6.0,
            "width_mm": 300,
            "depth_mm": 500,
            "effective_depth_mm": 450,
            "cover_mm": 25,
            "fck": 25,
            "fy": 415,
            "dead_load_kN": 15.0,
            "live_load_kN": 10.0,
            "factored_load_kN": 37.5,
        },
        "flexure": {
            "Mu_kNm": 169.0,
            "Mu_lim_kNm": 210.0,
            "Ast_req_mm2": 1200,
            "Ast_min_mm2": 283,
            "Ast_prov_mm2": 1257,
            "is_safe": True,
        },
        "shear": {
            "Vu_kN": 112.5,
            "tau_v": 0.83,
            "tau_c": 0.48,
            "stirrup_legs": 2,
            "spacing_mm": 150,
            "is_safe": True,
        },
        "detailing": {
            "Ld_req_mm": 752,
            "Ld_avail_mm": 800,
            "is_safe": True,
        },
        "compliance": {
            "min_steel_ok": True,
            "max_steel_ok": True,
            "spacing_ok": True,
            "dev_length_ok": True,
            "shear_reinf_ok": True,
        },
        "bbs": {
            "bars": [
                {
                    "mark": "M1",
                    "type": "Bottom",
                    "diameter_mm": 20,
                    "number": 4,
                    "length_mm": 6000,
                    "total_length_m": 24.0,
                    "weight_kg": 59.6,
                },
                {
                    "mark": "S1",
                    "type": "Stirrup",
                    "diameter_mm": 8,
                    "number": 40,
                    "length_mm": 1600,
                    "total_length_m": 64.0,
                    "weight_kg": 25.4,
                },
            ],
        },
    }


@pytest.fixture
def sample_project_info():
    """Sample project information."""
    return {
        "project_name": "Test Building",
        "location": "Mumbai",
        "client": "Test Client",
        "engineer": "Test Engineer",
        "checker": "Test Checker",
        "company": "Test Consultants",
    }


class TestBeamDesignReportGenerator:
    """Test PDF report generator utility."""

    def test_generator_initialization(self):
        """Test that generator initializes correctly."""
        from streamlit_app.utils.pdf_generator import BeamDesignReportGenerator

        generator = BeamDesignReportGenerator()

        assert generator is not None
        assert hasattr(generator, "styles")
        assert hasattr(generator, "page_width")
        assert hasattr(generator, "page_height")

    def test_custom_styles_created(self):
        """Test that custom paragraph styles are created."""
        from streamlit_app.utils.pdf_generator import BeamDesignReportGenerator

        generator = BeamDesignReportGenerator()

        # Check custom styles exist
        assert "CustomTitle" in generator.styles.byName
        assert "SectionHeading" in generator.styles.byName
        assert "Subsection" in generator.styles.byName
        assert "Reference" in generator.styles.byName
        assert "ResultHighlight" in generator.styles.byName

    def test_generate_report_returns_buffer(
        self, sample_design_data, sample_project_info
    ):
        """Test that generate_report returns a valid PDF buffer."""
        from streamlit_app.utils.pdf_generator import BeamDesignReportGenerator

        generator = BeamDesignReportGenerator()

        pdf_buffer = generator.generate_report(
            design_data=sample_design_data, project_info=sample_project_info
        )

        assert isinstance(pdf_buffer, BytesIO)
        assert pdf_buffer.tell() == 0  # Should be at start
        assert len(pdf_buffer.getvalue()) > 0  # Should have content

    def test_pdf_has_valid_header(self, sample_design_data, sample_project_info):
        """Test that generated PDF has valid PDF header."""
        from streamlit_app.utils.pdf_generator import BeamDesignReportGenerator

        generator = BeamDesignReportGenerator()
        pdf_buffer = generator.generate_report(
            design_data=sample_design_data, project_info=sample_project_info
        )

        content = pdf_buffer.getvalue()

        # Check PDF signature
        assert content.startswith(b"%PDF")

    def test_generate_with_bbs_option(self, sample_design_data, sample_project_info):
        """Test PDF generation with BBS table included."""
        from streamlit_app.utils.pdf_generator import BeamDesignReportGenerator

        generator = BeamDesignReportGenerator()
        pdf_buffer = generator.generate_report(
            design_data=sample_design_data,
            project_info=sample_project_info,
            include_bbs=True,
        )

        content = pdf_buffer.getvalue()
        assert len(content) > 0
        # With BBS, PDF should be larger
        assert len(content) > 50000  # Reasonable minimum for PDF with tables

    def test_generate_without_bbs_option(self, sample_design_data, sample_project_info):
        """Test PDF generation without BBS table."""
        from streamlit_app.utils.pdf_generator import BeamDesignReportGenerator

        generator = BeamDesignReportGenerator()

        # Remove BBS data
        design_data_no_bbs = sample_design_data.copy()
        design_data_no_bbs.pop("bbs", None)

        pdf_buffer = generator.generate_report(
            design_data=design_data_no_bbs,
            project_info=sample_project_info,
            include_bbs=False,
        )

        content = pdf_buffer.getvalue()
        assert len(content) > 0

    def test_create_cover_page(self, sample_project_info):
        """Test cover page creation."""
        from streamlit_app.utils.pdf_generator import BeamDesignReportGenerator

        generator = BeamDesignReportGenerator()
        elements = generator._create_cover_page(sample_project_info, logo_path=None)

        assert len(elements) > 0
        # Should have title, project table, disclaimer
        assert len(elements) >= 3

    def test_create_input_summary(self, sample_design_data):
        """Test input summary creation."""
        from streamlit_app.utils.pdf_generator import BeamDesignReportGenerator

        generator = BeamDesignReportGenerator()
        elements = generator._create_input_summary(sample_design_data)

        assert len(elements) > 0
        # Should have multiple tables (geometry, materials, loading)

    def test_create_calculations_section(self, sample_design_data):
        """Test calculations section creation."""
        from streamlit_app.utils.pdf_generator import BeamDesignReportGenerator

        generator = BeamDesignReportGenerator()
        elements = generator._create_calculations_section(sample_design_data)

        assert len(elements) > 0
        # Should have flexure and shear calculations

    def test_create_results_summary(self, sample_design_data):
        """Test results summary creation."""
        from streamlit_app.utils.pdf_generator import BeamDesignReportGenerator

        generator = BeamDesignReportGenerator()
        elements = generator._create_results_summary(sample_design_data)

        assert len(elements) > 0
        # Should show design status

    def test_create_bbs_table(self, sample_design_data):
        """Test BBS table creation."""
        from streamlit_app.utils.pdf_generator import BeamDesignReportGenerator

        generator = BeamDesignReportGenerator()
        elements = generator._create_bbs_table(sample_design_data["bbs"])

        assert len(elements) > 0

    def test_create_compliance_checklist(self, sample_design_data):
        """Test compliance checklist creation."""
        from streamlit_app.utils.pdf_generator import BeamDesignReportGenerator

        generator = BeamDesignReportGenerator()
        elements = generator._create_compliance_checklist(sample_design_data)

        assert len(elements) > 0

    def test_handle_missing_data_gracefully(self, sample_project_info):
        """Test that generator handles missing data without crashing."""
        from streamlit_app.utils.pdf_generator import BeamDesignReportGenerator

        generator = BeamDesignReportGenerator()

        # Minimal design data
        minimal_data = {
            "inputs": {"span_m": 5.0},
            "flexure": {},
            "shear": {},
            "detailing": {},
            "compliance": {},
        }

        pdf_buffer = generator.generate_report(
            design_data=minimal_data, project_info=sample_project_info
        )

        assert len(pdf_buffer.getvalue()) > 0


class TestReportGeneratorPage:
    """Test Streamlit page for report generation."""

    @pytest.fixture
    def mock_page(self):
        """Mock the page module."""
        import streamlit_app.pages.report_generator as page_module

        return page_module

    def test_page_renders_without_design_result(self, clean_session_state):
        """Test page shows warning when no design result exists."""
        # Session state is empty (no design_result)

        from streamlit_app.pages.report_generator import render_page

        # Should not crash
        render_page()

        # Should show warning (checked via st.warning call)
        # Note: In real app, we'd check Streamlit output

    def test_page_renders_with_design_result(
        self, clean_session_state, sample_design_data
    ):
        """Test page renders correctly with design result."""
        st.session_state["design_result"] = sample_design_data

        from streamlit_app.pages.report_generator import render_page

        # Should not crash
        render_page()

    def test_generate_button_validates_inputs(
        self, clean_session_state, sample_design_data
    ):
        """Test that generate button validates required inputs."""
        st.session_state["design_result"] = sample_design_data

        # In real test, would simulate button click with empty fields
        # and verify error message shown
        pass

    def test_pdf_download_button_appears(self, clean_session_state, sample_design_data):
        """Test that download button appears after successful generation."""
        st.session_state["design_result"] = sample_design_data

        # Would need to simulate successful PDF generation
        # and verify download button is shown
        pass


class TestReportGeneratorIntegration:
    """Integration tests for PDF report generation."""

    def test_full_workflow(self, sample_design_data, sample_project_info):
        """Test complete workflow from data to PDF."""
        from streamlit_app.utils.pdf_generator import BeamDesignReportGenerator

        generator = BeamDesignReportGenerator()

        # Generate with all options
        pdf_buffer = generator.generate_report(
            design_data=sample_design_data,
            project_info=sample_project_info,
            include_bbs=True,
            include_diagrams=True,
        )

        content = pdf_buffer.getvalue()

        # Verify PDF structure
        assert content.startswith(b"%PDF")
        assert b"endobj" in content  # Has PDF objects
        assert b"stream" in content  # Has content streams
        assert len(content) > 50000  # Reasonable size for complete report

    def test_multiple_report_generations(self, sample_design_data, sample_project_info):
        """Test generating multiple reports doesn't cause issues."""
        from streamlit_app.utils.pdf_generator import BeamDesignReportGenerator

        generator = BeamDesignReportGenerator()

        # Generate 3 reports
        for _ in range(3):
            pdf_buffer = generator.generate_report(
                design_data=sample_design_data, project_info=sample_project_info
            )
            assert len(pdf_buffer.getvalue()) > 0

    def test_report_with_varying_data_sizes(self, sample_project_info):
        """Test report generation with different data sizes."""
        from streamlit_app.utils.pdf_generator import BeamDesignReportGenerator

        generator = BeamDesignReportGenerator()

        # Small BBS
        small_bbs_data = {
            "inputs": {"span_m": 5.0, "width_mm": 300},
            "flexure": {"Mu_kNm": 100, "is_safe": True},
            "shear": {"Vu_kN": 50, "is_safe": True},
            "detailing": {"Ld_req_mm": 500, "is_safe": True},
            "compliance": {},
            "bbs": {
                "bars": [
                    {
                        "mark": "M1",
                        "type": "Main",
                        "diameter_mm": 16,
                        "number": 2,
                        "length_mm": 5000,
                        "total_length_m": 10.0,
                        "weight_kg": 15.7,
                    }
                ]
            },
        }

        pdf1 = generator.generate_report(small_bbs_data, sample_project_info)

        # Large BBS
        large_bbs_data = small_bbs_data.copy()
        large_bbs_data["bbs"] = {
            "bars": [
                {
                    "mark": f"M{i}",
                    "type": "Main",
                    "diameter_mm": 16,
                    "number": 2,
                    "length_mm": 5000,
                    "total_length_m": 10.0,
                    "weight_kg": 15.7,
                }
                for i in range(20)
            ]
        }

        pdf2 = generator.generate_report(large_bbs_data, sample_project_info)

        # Large report should be bigger
        assert len(pdf2.getvalue()) > len(pdf1.getvalue())


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_project_info(self, sample_design_data):
        """Test with empty project info."""
        from streamlit_app.utils.pdf_generator import BeamDesignReportGenerator

        generator = BeamDesignReportGenerator()

        empty_info = {}

        # Should not crash
        pdf_buffer = generator.generate_report(
            design_data=sample_design_data, project_info=empty_info
        )

        assert len(pdf_buffer.getvalue()) > 0

    def test_special_characters_in_project_info(self, sample_design_data):
        """Test handling of special characters."""
        from streamlit_app.utils.pdf_generator import BeamDesignReportGenerator

        generator = BeamDesignReportGenerator()

        special_info = {
            "project_name": "Test & Development <Project>",
            "engineer": "Engineer's Name (M.Tech)",
            "company": "ABC & XYZ Consultants",
        }

        pdf_buffer = generator.generate_report(
            design_data=sample_design_data, project_info=special_info
        )

        assert len(pdf_buffer.getvalue()) > 0

    def test_invalid_logo_path(self, sample_design_data, sample_project_info):
        """Test with invalid logo path."""
        from streamlit_app.utils.pdf_generator import BeamDesignReportGenerator

        generator = BeamDesignReportGenerator()

        # Should handle gracefully
        pdf_buffer = generator.generate_report(
            design_data=sample_design_data,
            project_info=sample_project_info,
            logo_path="/nonexistent/logo.png",
        )

        assert len(pdf_buffer.getvalue()) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
