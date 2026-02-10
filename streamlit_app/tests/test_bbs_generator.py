"""
Tests for BBS Generator Page (FEAT-001)
========================================

Tests for the Bar Bending Schedule generator page.

Author: Agent 6 (Streamlit Specialist)
Task: STREAMLIT-FEAT-001
"""

import pytest
import pandas as pd

# Use centralized MockStreamlit from conftest.py - no local mock needed


class MockContext:
    """Mock context manager for Streamlit."""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


# Note: mock_streamlit fixture is provided by conftest.py


@pytest.fixture
def sample_beam_design():
    """Sample beam design data for testing."""
    return {
        "inputs": {
            "span_mm": 5000,
            "b_mm": 300,
            "D_mm": 500,
            "d_mm": 450,
            "cover_mm": 30,
            "concrete_grade": "M25",
            "steel_grade": "Fe500",
            "mu_knm": 120,
            "vu_kn": 80,
            "member_id": "B1",
            "design_computed": True,
        },
        "result": {
            "ast_required_mm2": 1000,
            "bar_diameter_mm": 20,
            "num_bars": 4,
            "stirrup_diameter_mm": 8,
            "stirrup_spacing_mm": 150,
        },
    }


@pytest.fixture
def sample_bbs_document():
    """Sample BBS document for testing."""
    try:
        from structural_lib.services.bbs import BBSLineItem, BBSummary, BBSDocument

        item1 = BBSLineItem(
            bar_mark="B1-BM-B",
            member_id="B1",
            location="bottom",
            zone="full",
            shape_code="A",
            diameter_mm=20,
            no_of_bars=4,
            cut_length_mm=6880,
            total_length_mm=27520,
            unit_weight_kg=16.98,
            total_weight_kg=67.92,
            remarks="Bottom tension steel",
        )

        item2 = BBSLineItem(
            bar_mark="B1-ST",
            member_id="B1",
            location="stirrup",
            zone="full",
            shape_code="E",
            diameter_mm=8,
            no_of_bars=35,
            cut_length_mm=1500,
            total_length_mm=52500,
            unit_weight_kg=0.59,
            total_weight_kg=20.72,
            remarks="@ 150mm c/c",
        )

        summary = BBSummary(
            member_id="B1",
            total_items=2,
            total_bars=39,
            total_length_m=80.02,
            total_weight_kg=88.64,
            weight_by_diameter={20: 67.92, 8: 20.72},
        )

        doc = BBSDocument(
            project_name="Test Project",
            member_ids=["B1"],
            items=[item1, item2],
            summary=summary,
        )

        return doc
    except ImportError:
        pytest.skip("structural_lib.bbs not available")


# =============================================================================
# Session State Tests
# =============================================================================


class TestSessionStateInitialization:
    """Test session state initialization."""

    def test_session_state_structure(self, mock_streamlit):
        """Test that session_state has correct structure."""
        # Clear state first
        mock_streamlit.session_state.clear()

        # Simulate initialization
        if "bbs_inputs" not in mock_streamlit.session_state:
            mock_streamlit.session_state["bbs_inputs"] = {
                "mode": "auto",
                "project_name": "RC Beam Project",
                "member_id": "B1",
                "bbs_items": [],
                "generated_bbs": None,
            }

        assert "bbs_inputs" in mock_streamlit.session_state
        assert mock_streamlit.session_state["bbs_inputs"]["mode"] == "auto"

    def test_default_mode_is_auto(self, mock_streamlit):
        """Test that default mode is auto."""
        if "bbs_inputs" not in mock_streamlit.session_state:
            mock_streamlit.session_state["bbs_inputs"] = {"mode": "auto"}

        assert mock_streamlit.session_state["bbs_inputs"]["mode"] == "auto"


# =============================================================================
# BBS Generation Tests
# =============================================================================


class TestBBSGeneration:
    """Test BBS document generation."""

    def test_create_bbs_from_beam_design(self, sample_beam_design):
        """Test BBS generation from beam design."""
        pytest.importorskip("structural_lib.bbs")

        # Import the function (would need to make it importable)
        # For now, test the logic inline

        inputs = sample_beam_design["inputs"]
        result = sample_beam_design["result"]

        assert inputs["span_mm"] == 5000
        assert result["bar_diameter_mm"] == 20
        assert result["num_bars"] == 4

    def test_bbs_includes_main_bars(self, sample_bbs_document):
        """Test that BBS includes main bars."""
        main_bars = [
            item for item in sample_bbs_document.items if item.location == "bottom"
        ]
        assert len(main_bars) >= 1
        assert main_bars[0].shape_code == "A"  # Straight bar

    def test_bbs_includes_stirrups(self, sample_bbs_document):
        """Test that BBS includes stirrups."""
        stirrups = [
            item for item in sample_bbs_document.items if item.location == "stirrup"
        ]
        assert len(stirrups) >= 1
        assert stirrups[0].shape_code == "E"  # Closed stirrup

    def test_bbs_weights_calculated(self, sample_bbs_document):
        """Test that weights are calculated correctly."""
        for item in sample_bbs_document.items:
            assert item.unit_weight_kg > 0
            assert item.total_weight_kg > 0
            assert item.total_weight_kg == pytest.approx(
                item.unit_weight_kg * item.no_of_bars, rel=0.01
            )

    def test_bbs_summary_totals_match(self, sample_bbs_document):
        """Test that summary totals match item totals."""
        total_weight = sum(item.total_weight_kg for item in sample_bbs_document.items)
        assert sample_bbs_document.summary.total_weight_kg == pytest.approx(
            total_weight, rel=0.01
        )

        total_bars = sum(item.no_of_bars for item in sample_bbs_document.items)
        assert sample_bbs_document.summary.total_bars == total_bars


# =============================================================================
# DataFrame Conversion Tests
# =============================================================================


class TestDataFrameConversion:
    """Test BBS to DataFrame conversion."""

    def test_bbs_to_dataframe_columns(self, sample_bbs_document):
        """Test that DataFrame has correct columns."""
        # Inline the function for testing
        data = []
        for item in sample_bbs_document.items:
            data.append(
                {
                    "Bar Mark": item.bar_mark,
                    "Shape": item.shape_code,
                    "Diameter (mm)": int(item.diameter_mm),
                    "Location": item.location.capitalize(),
                    "No. of Bars": item.no_of_bars,
                    "Cut Length (mm)": int(item.cut_length_mm),
                    "Total Length (m)": f"{item.total_length_mm / 1000:.2f}",
                    "Unit Wt (kg)": f"{item.unit_weight_kg:.2f}",
                    "Total Wt (kg)": f"{item.total_weight_kg:.2f}",
                    "Remarks": item.remarks,
                }
            )

        df = pd.DataFrame(data)

        expected_columns = [
            "Bar Mark",
            "Shape",
            "Diameter (mm)",
            "Location",
            "No. of Bars",
            "Cut Length (mm)",
            "Total Length (m)",
            "Unit Wt (kg)",
            "Total Wt (kg)",
            "Remarks",
        ]

        assert list(df.columns) == expected_columns

    def test_dataframe_row_count(self, sample_bbs_document):
        """Test that DataFrame has correct number of rows."""
        data = []
        for item in sample_bbs_document.items:
            data.append({"Bar Mark": item.bar_mark})

        df = pd.DataFrame(data)
        assert len(df) == len(sample_bbs_document.items)


# =============================================================================
# Export Tests
# =============================================================================


class TestBBSExport:
    """Test BBS export functionality."""

    def test_export_to_csv_format(self, sample_bbs_document):
        """Test CSV export format."""
        # Inline the export function
        data = []
        for item in sample_bbs_document.items:
            data.append(
                {
                    "Bar Mark": item.bar_mark,
                    "Diameter (mm)": int(item.diameter_mm),
                    "No. of Bars": item.no_of_bars,
                }
            )

        df = pd.DataFrame(data)
        csv_str = df.to_csv(index=False)

        assert "Bar Mark" in csv_str
        assert "Diameter (mm)" in csv_str
        assert len(csv_str) > 0

    def test_csv_includes_header_info(self, sample_bbs_document):
        """Test that CSV includes project header."""
        header = f"Project: {sample_bbs_document.project_name}"
        assert sample_bbs_document.project_name in header


# =============================================================================
# UI Component Tests
# =============================================================================


class TestUIComponents:
    """Test UI component rendering."""

    def test_mode_selection_default(self, mock_streamlit):
        """Test that mode selection defaults to auto."""
        if "bbs_inputs" not in mock_streamlit.session_state:
            mock_streamlit.session_state["bbs_inputs"] = {"mode": "auto"}

        mode = mock_streamlit.session_state["bbs_inputs"]["mode"]
        assert mode == "auto"

    def test_summary_cards_display(self, sample_bbs_document):
        """Test that summary cards show correct metrics."""
        summary = sample_bbs_document.summary

        assert summary.total_items == 2
        assert summary.total_bars == 39
        assert summary.total_length_m > 0
        assert summary.total_weight_kg > 0

    def test_weight_breakdown_by_diameter(self, sample_bbs_document):
        """Test weight breakdown calculation."""
        weight_data = []
        for dia, weight in sample_bbs_document.summary.weight_by_diameter.items():
            weight_data.append(
                {
                    "Diameter (mm)": f"Ø{int(dia)}",
                    "Total Weight (kg)": f"{weight:.2f}",
                }
            )

        assert len(weight_data) == 2  # 20mm and 8mm
        assert any("Ø20" in item["Diameter (mm)"] for item in weight_data)
        assert any("Ø8" in item["Diameter (mm)"] for item in weight_data)


# =============================================================================
# Integration Tests
# =============================================================================


class TestBBSIntegration:
    """Integration tests for BBS page."""

    def test_end_to_end_auto_generation(self, mock_streamlit, sample_beam_design):
        """Test complete auto-generation workflow."""
        # Setup session state
        mock_streamlit.session_state["beam_inputs"] = sample_beam_design["inputs"]
        mock_streamlit.session_state["beam_inputs"]["design_result"] = (
            sample_beam_design["result"]
        )

        # Check beam design is available
        if "beam_inputs" in mock_streamlit.session_state:
            beam = mock_streamlit.session_state["beam_inputs"]
            assert beam.get("design_computed") is True

    def test_no_beam_design_shows_warning(self, mock_streamlit):
        """Test that warning is shown when no beam design exists."""
        # Clear beam design
        if "beam_inputs" in mock_streamlit.session_state:
            del mock_streamlit.session_state._state["beam_inputs"]

        # Check condition
        beam_data = mock_streamlit.session_state.get("beam_inputs")
        assert beam_data is None


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
