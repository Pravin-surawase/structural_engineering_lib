"""
Tests for Excel Integration Module

Tests:
- CSV/JSON parsing
- Data mapping and validation
- Batch processing
- Schedule generation
"""

import pytest
import os
import tempfile
import json
import csv
from structural_lib.excel_integration import (
    BeamDesignData,
    load_beam_data_from_csv,
    load_beam_data_from_json,
    export_beam_data_to_json,
    process_single_beam,
    batch_generate_dxf,
    generate_summary_report,
    generate_detailing_schedule,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_beam_dict():
    """Sample beam design data as dictionary."""
    return {
        "BeamID": "B1",
        "Story": "Story1",
        "b": 300,
        "D": 500,
        "Span": 4000,
        "Cover": 40,
        "fck": 25,
        "fy": 500,
        "Mu": 150,
        "Vu": 100,
        "Ast_req": 942.5,
        "Asc_req": 0,
        "Stirrup_Dia": 8,
        "Stirrup_Spacing": 150,
        "Status": "OK",
    }


@pytest.fixture
def sample_beam_data(sample_beam_dict):
    """Sample BeamDesignData object."""
    return BeamDesignData.from_dict(sample_beam_dict)


@pytest.fixture
def temp_csv_file(sample_beam_dict):
    """Create a temporary CSV file with sample data."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        writer = csv.DictWriter(f, fieldnames=sample_beam_dict.keys())
        writer.writeheader()
        writer.writerow(sample_beam_dict)
        # Add another row
        row2 = sample_beam_dict.copy()
        row2["BeamID"] = "B2"
        row2["Ast_req"] = 628.3
        writer.writerow(row2)
        return f.name


@pytest.fixture
def temp_json_file(sample_beam_dict):
    """Create a temporary JSON file with sample data."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        data = {"beams": [sample_beam_dict]}
        json.dump(data, f)
        return f.name


@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory."""
    return tempfile.mkdtemp()


# =============================================================================
# Test BeamDesignData
# =============================================================================


class TestBeamDesignData:
    """Tests for BeamDesignData dataclass."""

    def test_from_dict_standard_keys(self, sample_beam_dict):
        """Test creation from standard column names."""
        beam = BeamDesignData.from_dict(sample_beam_dict)

        assert beam.beam_id == "B1"
        assert beam.story == "Story1"
        assert beam.b == 300
        assert beam.D == 500
        assert beam.span == 4000
        assert beam.cover == 40
        assert beam.fck == 25
        assert beam.fy == 500
        assert beam.Ast_req == 942.5
        assert beam.Asc_req == 0
        assert beam.stirrup_dia == 8
        assert beam.stirrup_spacing == 150

    def test_from_dict_lowercase_keys(self):
        """Test creation with lowercase keys."""
        data = {
            "beamid": "B1",
            "story": "Story1",
            "b": 300,
            "d": 500,  # lowercase D
            "span": 4000,
            "cover": 40,
            "fck": 25,
            "fy": 500,
            "mu": 150,
            "vu": 100,
            "ast_req": 942.5,
            "stirrup_dia": 8,
            "stirrup_spacing": 150,
        }
        beam = BeamDesignData.from_dict(data)
        assert beam.beam_id == "B1"
        assert beam.D == 500

    def test_from_dict_defaults(self):
        """Test default values are applied."""
        # Minimal data
        data = {
            "BeamID": "B1",
            "Story": "Story1",
            "b": 300,
            "D": 500,
            "Span": 4000,
            "fck": 25,
            "fy": 500,
            "Mu": 150,
            "Vu": 100,
            "Ast_req": 942.5,
            "Stirrup_Dia": 8,
            "Stirrup_Spacing": 150,
        }
        beam = BeamDesignData.from_dict(data)

        assert beam.cover == 40  # Default cover
        assert beam.Asc_req == 0  # Default compression steel
        assert beam.d == 460  # Calculated effective depth


# =============================================================================
# Test File Parsing
# =============================================================================


class TestCSVParsing:
    """Tests for CSV file parsing."""

    def test_load_beam_data_from_csv(self, temp_csv_file):
        """Test loading beam data from CSV."""
        beams = load_beam_data_from_csv(temp_csv_file)

        assert len(beams) == 2
        assert beams[0].beam_id == "B1"
        assert beams[1].beam_id == "B2"

        # Cleanup
        os.unlink(temp_csv_file)

    def test_csv_with_missing_optional_fields(self, temp_output_dir):
        """Test CSV with missing optional fields."""
        csv_path = os.path.join(temp_output_dir, "test.csv")

        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "BeamID",
                    "Story",
                    "b",
                    "D",
                    "Span",
                    "fck",
                    "fy",
                    "Mu",
                    "Vu",
                    "Ast_req",
                    "Stirrup_Dia",
                    "Stirrup_Spacing",
                ]
            )
            writer.writerow(
                ["B1", "Story1", 300, 500, 4000, 25, 500, 150, 100, 942.5, 8, 150]
            )

        beams = load_beam_data_from_csv(csv_path)

        assert len(beams) == 1
        assert beams[0].cover == 40  # Default applied


class TestJSONParsing:
    """Tests for JSON file parsing."""

    def test_load_beam_data_from_json_with_beams_key(self, temp_json_file):
        """Test loading from JSON with 'beams' key."""
        beams = load_beam_data_from_json(temp_json_file)

        assert len(beams) == 1
        assert beams[0].beam_id == "B1"

        # Cleanup
        os.unlink(temp_json_file)

    def test_load_beam_data_from_json_array(self, temp_output_dir, sample_beam_dict):
        """Test loading from JSON as direct array."""
        json_path = os.path.join(temp_output_dir, "test.json")

        with open(json_path, "w") as f:
            json.dump([sample_beam_dict], f)

        beams = load_beam_data_from_json(json_path)

        assert len(beams) == 1
        assert beams[0].beam_id == "B1"

    def test_export_beam_data_to_json(self, sample_beam_data, temp_output_dir):
        """Test exporting beam data to JSON."""
        json_path = os.path.join(temp_output_dir, "export.json")

        export_beam_data_to_json([sample_beam_data], json_path)

        assert os.path.exists(json_path)

        with open(json_path, "r") as f:
            data = json.load(f)

        assert "beams" in data
        assert len(data["beams"]) == 1
        assert data["beams"][0]["beam_id"] == "B1"


# =============================================================================
# Test Processing
# =============================================================================


class TestProcessing:
    """Tests for beam processing functions."""

    def test_process_single_beam_detailing_only(
        self, sample_beam_data, temp_output_dir
    ):
        """Test processing without DXF generation."""
        result = process_single_beam(
            sample_beam_data, temp_output_dir, generate_dxf=False
        )

        assert result.success is True
        assert result.beam_id == "B1"
        assert result.detailing is not None
        assert result.dxf_path is None
        assert result.error is None

    def test_process_single_beam_with_detailing_values(
        self, sample_beam_data, temp_output_dir
    ):
        """Test that detailing values are calculated correctly."""
        result = process_single_beam(
            sample_beam_data, temp_output_dir, generate_dxf=False
        )

        d = result.detailing
        assert d.beam_id == "B1"
        assert d.b == 300
        assert d.D == 500
        assert d.ld_tension > 0
        assert d.lap_length > 0
        assert len(d.bottom_bars) > 0

    def test_batch_generate_from_csv(self, temp_csv_file, temp_output_dir):
        """Test batch processing from CSV (without DXF)."""
        # Since ezdxf may not be installed, we test the flow
        results = batch_generate_dxf(temp_csv_file, temp_output_dir, is_seismic=False)

        assert len(results) == 2
        # At least detailing should succeed even if DXF fails
        for r in results:
            if r.success:
                assert r.detailing is not None

        # Cleanup
        os.unlink(temp_csv_file)


# =============================================================================
# Test Reporting
# =============================================================================


class TestReporting:
    """Tests for report generation."""

    def test_generate_summary_report(self, sample_beam_data, temp_output_dir):
        """Test summary report generation."""
        result = process_single_beam(
            sample_beam_data, temp_output_dir, generate_dxf=False
        )

        report = generate_summary_report([result])

        assert "Total Beams:     1" in report
        assert "Successful:      1" in report
        assert "Failed:          0" in report

    def test_generate_detailing_schedule(self, sample_beam_data, temp_output_dir):
        """Test detailing schedule generation."""
        result = process_single_beam(
            sample_beam_data, temp_output_dir, generate_dxf=False
        )

        schedule = generate_detailing_schedule([result])

        assert len(schedule) == 1
        row = schedule[0]
        assert row["Story"] == "Story1"
        assert row["Beam"] == "B1"
        assert row["Size"] == "300x500"
        assert "Ld_Tension" in row
        assert "Lap_Length" in row


# =============================================================================
# Test Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_invalid_file_format(self, temp_output_dir):
        """Test error on unsupported file format."""
        txt_path = os.path.join(temp_output_dir, "test.txt")

        with open(txt_path, "w") as f:
            f.write("some data")

        with pytest.raises(ValueError, match="Unsupported file format"):
            batch_generate_dxf(txt_path, temp_output_dir)

    def test_empty_csv(self, temp_output_dir):
        """Test handling of empty CSV file."""
        csv_path = os.path.join(temp_output_dir, "empty.csv")

        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "BeamID",
                    "Story",
                    "b",
                    "D",
                    "Span",
                    "fck",
                    "fy",
                    "Mu",
                    "Vu",
                    "Ast_req",
                    "Stirrup_Dia",
                    "Stirrup_Spacing",
                ]
            )
            # No data rows

        beams = load_beam_data_from_csv(csv_path)
        assert len(beams) == 0
