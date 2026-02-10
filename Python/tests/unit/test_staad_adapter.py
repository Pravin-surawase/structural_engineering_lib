# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for STAADAdapter - STAAD.Pro data import adapter.

Tests cover:
- can_handle: STAAD vs ETABS format detection
- load_forces: Station data, envelope data, edge cases
- load_geometry: Member coordinates and properties
- Integration: Full workflow tests

Author: Session 41 Agent
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from structural_lib.adapters import STAADAdapter
from structural_lib.core.models import DesignDefaults, FrameType


@pytest.fixture
def adapter() -> STAADAdapter:
    """Create a STAADAdapter instance."""
    return STAADAdapter()


@pytest.fixture
def staad_forces_csv(tmp_path: Path) -> Path:
    """Create a sample STAAD.Pro forces CSV file."""
    csv_path = tmp_path / "staad_forces.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Member", "LC", "Dist", "Fx", "Fy", "My", "Mz"])
        # Member 1: 3 stations across 2 load cases
        writer.writerow(["1", "LC1", "0", "10.0", "50.0", "100.0", "5.0"])
        writer.writerow(["1", "LC1", "2500", "10.0", "0.0", "150.0", "3.0"])
        writer.writerow(["1", "LC1", "5000", "10.0", "-50.0", "100.0", "5.0"])
        writer.writerow(["1", "LC2", "0", "15.0", "60.0", "120.0", "6.0"])
        writer.writerow(["1", "LC2", "2500", "15.0", "0.0", "180.0", "4.0"])
        writer.writerow(["1", "LC2", "5000", "15.0", "-60.0", "120.0", "6.0"])
        # Member 2: 2 stations, 1 load case
        writer.writerow(["2", "LC1", "0", "5.0", "40.0", "80.0", "2.0"])
        writer.writerow(["2", "LC1", "3000", "5.0", "-40.0", "80.0", "2.0"])
    return csv_path


@pytest.fixture
def staad_envelope_csv(tmp_path: Path) -> Path:
    """Create a STAAD.Pro envelope format CSV."""
    csv_path = tmp_path / "staad_envelope.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Member", "LC", "My_max", "Fy_max"])
        writer.writerow(["1", "Envelope", "200.0", "75.0"])
        writer.writerow(["2", "Envelope", "150.0", "55.0"])
        writer.writerow(["3", "Envelope", "120.0", "45.0"])
    return csv_path


@pytest.fixture
def staad_geometry_csv(tmp_path: Path) -> Path:
    """Create a STAAD.Pro geometry CSV."""
    csv_path = tmp_path / "staad_geometry.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "Member",
                "Label",
                "Group",
                "X1",
                "Y1",
                "Z1",
                "X2",
                "Y2",
                "Z2",
                "Width",
                "Depth",
            ]
        )
        writer.writerow(
            ["1", "B1", "Floor1", "0", "0", "3", "5", "0", "3", "300", "500"]
        )
        writer.writerow(
            ["2", "B2", "Floor1", "5", "0", "3", "10", "0", "3", "300", "450"]
        )
        writer.writerow(
            ["3", "B3", "Floor2", "0", "0", "6", "5", "0", "6", "350", "600"]
        )
    return csv_path


@pytest.fixture
def etabs_forces_csv(tmp_path: Path) -> Path:
    """Create an ETABS-style forces CSV (should NOT match STAAD)."""
    csv_path = tmp_path / "etabs_forces.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Story", "Frame", "Output Case", "Station", "M3", "V2"])
        writer.writerow(["Story1", "B1", "1.5DL+LL", "0", "100.0", "50.0"])
    return csv_path


class TestSTAADAdapterCanHandle:
    """Test can_handle detection logic."""

    def test_can_handle_staad_forces_file(
        self, adapter: STAADAdapter, staad_forces_csv: Path
    ):
        """STAADAdapter should handle STAAD.Pro forces CSV."""
        assert adapter.can_handle(staad_forces_csv) is True

    def test_can_handle_staad_envelope_file(
        self, adapter: STAADAdapter, staad_envelope_csv: Path
    ):
        """STAADAdapter should handle STAAD.Pro envelope CSV."""
        assert adapter.can_handle(staad_envelope_csv) is True

    def test_rejects_etabs_format(self, adapter: STAADAdapter, etabs_forces_csv: Path):
        """STAADAdapter should reject ETABS format files."""
        assert adapter.can_handle(etabs_forces_csv) is False

    def test_rejects_nonexistent_file(self, adapter: STAADAdapter):
        """STAADAdapter should reject non-existent files."""
        assert adapter.can_handle(Path("/nonexistent/file.csv")) is False

    def test_rejects_wrong_extension(self, adapter: STAADAdapter, tmp_path: Path):
        """STAADAdapter should reject non-CSV/TXT files."""
        xlsx_file = tmp_path / "forces.xlsx"
        xlsx_file.touch()
        assert adapter.can_handle(xlsx_file) is False


class TestSTAADAdapterLoadForces:
    """Test load_forces for various STAAD.Pro formats."""

    def test_load_station_data_forces(
        self, adapter: STAADAdapter, staad_forces_csv: Path
    ):
        """Load forces from station data and compute envelope."""
        forces = adapter.load_forces(staad_forces_csv)

        # Should have 3 envelopes: Member 1/LC1, Member 1/LC2, Member 2/LC1
        assert len(forces) == 3

        # Find Member 1, LC1
        m1_lc1 = next(f for f in forces if f.id == "1" and f.load_case == "LC1")
        assert m1_lc1.mu_knm == pytest.approx(150.0)  # max(100, 150, 100)
        assert m1_lc1.vu_kn == pytest.approx(50.0)  # max(50, 0, 50)
        assert m1_lc1.station_count == 3

        # Find Member 1, LC2
        m1_lc2 = next(f for f in forces if f.id == "1" and f.load_case == "LC2")
        assert m1_lc2.mu_knm == pytest.approx(180.0)  # max(120, 180, 120)
        assert m1_lc2.vu_kn == pytest.approx(60.0)  # max(60, 0, 60)

    def test_load_envelope_forces(
        self, adapter: STAADAdapter, staad_envelope_csv: Path
    ):
        """Load forces from pre-computed envelope format."""
        forces = adapter.load_forces(staad_envelope_csv)

        assert len(forces) == 3

        # Check specific values
        m1 = next(f for f in forces if f.id == "1")
        assert m1.mu_knm == pytest.approx(200.0)
        assert m1.vu_kn == pytest.approx(75.0)
        assert m1.load_case == "Envelope"

    def test_load_forces_without_load_case(self, adapter: STAADAdapter, tmp_path: Path):
        """Load forces when LC column is missing - should default."""
        csv_path = tmp_path / "no_lc.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Member", "Dist", "My", "Fy"])
            writer.writerow(["1", "0", "100.0", "50.0"])
            writer.writerow(["1", "2500", "150.0", "30.0"])

        forces = adapter.load_forces(csv_path)

        assert len(forces) == 1
        assert forces[0].id == "1"
        assert forces[0].load_case == "Default"
        assert forces[0].mu_knm == pytest.approx(150.0)

    def test_load_forces_with_axial(self, adapter: STAADAdapter, tmp_path: Path):
        """Load forces including axial force (Fx)."""
        csv_path = tmp_path / "with_axial.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Member", "LC", "Fx", "Fy", "My"])
            writer.writerow(["1", "LC1", "100.0", "50.0", "150.0"])
            writer.writerow(["1", "LC1", "120.0", "40.0", "180.0"])

        forces = adapter.load_forces(csv_path)

        assert len(forces) == 1
        assert forces[0].pu_kn == pytest.approx(120.0)  # max(100, 120)

    def test_load_forces_file_not_found(self, adapter: STAADAdapter):
        """Raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            adapter.load_forces(Path("/nonexistent/forces.csv"))

    def test_load_forces_missing_columns(self, adapter: STAADAdapter, tmp_path: Path):
        """Raise ValueError for missing required columns."""
        csv_path = tmp_path / "bad_columns.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["X", "Y", "Z"])  # No valid columns
            writer.writerow(["1", "2", "3"])

        with pytest.raises(ValueError, match="Missing"):
            adapter.load_forces(csv_path)

    def test_handles_empty_rows(self, adapter: STAADAdapter, tmp_path: Path):
        """Skip rows with empty member ID."""
        csv_path = tmp_path / "empty_rows.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Member", "LC", "My", "Fy"])
            writer.writerow(["1", "LC1", "100.0", "50.0"])
            writer.writerow(["", "LC1", "999.0", "999.0"])  # Empty member
            writer.writerow(["2", "LC1", "80.0", "40.0"])

        forces = adapter.load_forces(csv_path)

        assert len(forces) == 2
        assert {f.id for f in forces} == {"1", "2"}


class TestSTAADAdapterLoadGeometry:
    """Test load_geometry for STAAD.Pro member data."""

    def test_load_geometry_basic(self, adapter: STAADAdapter, staad_geometry_csv: Path):
        """Load basic geometry with coordinates."""
        beams = adapter.load_geometry(staad_geometry_csv)

        assert len(beams) == 3

        # Check first beam
        b1 = next(b for b in beams if b.source_id == "1")
        assert b1.label == "B1"
        assert b1.story == "Floor1"
        assert b1.id == "1_Floor1"
        assert b1.point1.x == pytest.approx(0.0)
        assert b1.point2.x == pytest.approx(5.0)
        assert b1.section.width_mm == pytest.approx(300.0)
        assert b1.section.depth_mm == pytest.approx(500.0)

    def test_load_geometry_uses_defaults(self, adapter: STAADAdapter, tmp_path: Path):
        """Use default values when section properties not in CSV."""
        csv_path = tmp_path / "minimal_geo.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Member", "X1", "Y1", "X2", "Y2"])
            writer.writerow(["1", "0", "0", "5", "0"])

        # DesignDefaults only has material properties, not dimensions
        defaults = DesignDefaults(fck_mpa=30.0, fy_mpa=415.0)
        beams = adapter.load_geometry(csv_path, defaults=defaults)

        assert len(beams) == 1
        # Default dimensions are 300mm x 500mm (hardcoded in adapter)
        assert beams[0].section.width_mm == pytest.approx(300.0)
        assert beams[0].section.depth_mm == pytest.approx(500.0)
        # Material properties from defaults
        assert beams[0].section.fck_mpa == pytest.approx(30.0)
        assert beams[0].section.fy_mpa == pytest.approx(415.0)

    def test_load_geometry_without_coordinates(
        self, adapter: STAADAdapter, tmp_path: Path
    ):
        """Use placeholder coordinates when not provided."""
        csv_path = tmp_path / "no_coords.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Member", "Label", "Width", "Depth"])
            writer.writerow(["1", "B1", "300", "500"])

        beams = adapter.load_geometry(csv_path)

        assert len(beams) == 1
        # Should have placeholder coordinates (0,0,0) to (1,0,0)
        assert beams[0].point1.x == pytest.approx(0.0)
        assert beams[0].point2.x == pytest.approx(1.0)
        # Dimensions from CSV
        assert beams[0].section.width_mm == pytest.approx(300.0)
        assert beams[0].section.depth_mm == pytest.approx(500.0)

    def test_load_geometry_missing_beam_id(self, adapter: STAADAdapter, tmp_path: Path):
        """Raise ValueError when beam identifier column is missing."""
        csv_path = tmp_path / "no_id.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["X1", "Y1", "X2", "Y2"])
            writer.writerow(["0", "0", "5", "0"])

        with pytest.raises(ValueError, match="Missing beam identifier"):
            adapter.load_geometry(csv_path)

    def test_load_geometry_file_not_found(self, adapter: STAADAdapter):
        """Raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            adapter.load_geometry(Path("/nonexistent/geometry.csv"))

    def test_all_beams_have_correct_frame_type(
        self, adapter: STAADAdapter, staad_geometry_csv: Path
    ):
        """All loaded beams should have BEAM frame type."""
        beams = adapter.load_geometry(staad_geometry_csv)

        for beam in beams:
            assert beam.frame_type == FrameType.BEAM


class TestSTAADAdapterIntegration:
    """Integration tests for complete STAAD.Pro workflows."""

    def test_geometry_and_forces_together(
        self,
        adapter: STAADAdapter,
        staad_geometry_csv: Path,
        staad_forces_csv: Path,
    ):
        """Load both geometry and forces, verify they can be matched."""
        beams = adapter.load_geometry(staad_geometry_csv)
        forces = adapter.load_forces(staad_forces_csv)

        # Get beam IDs (source_id for geometry)
        beam_ids = {b.source_id for b in beams}
        force_ids = {f.id for f in forces}

        # Should have some overlap (member 1 and 2 are in both)
        common_ids = beam_ids & force_ids
        assert len(common_ids) >= 2

    def test_adapter_name(self, adapter: STAADAdapter):
        """Adapter should have correct name."""
        assert adapter.name == "STAAD.Pro"

    def test_supported_formats(self, adapter: STAADAdapter):
        """Adapter should support .csv and .txt."""
        assert ".csv" in adapter.supported_formats
        assert ".txt" in adapter.supported_formats

    def test_txt_extension_supported(self, adapter: STAADAdapter, tmp_path: Path):
        """STAAD often exports to .txt - should be handled."""
        txt_path = tmp_path / "staad_output.txt"
        with open(txt_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Member", "LC", "My", "Fy"])
            writer.writerow(["1", "LC1", "100.0", "50.0"])

        assert adapter.can_handle(txt_path) is True
        forces = adapter.load_forces(txt_path)
        assert len(forces) == 1


class TestSTAADAdapterColumnMapping:
    """Test column alias handling."""

    def test_alternative_column_names(self, adapter: STAADAdapter, tmp_path: Path):
        """Test various STAAD column name variations."""
        csv_path = tmp_path / "alt_columns.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            # Use alternative column names
            writer.writerow(["Memb", "LoadCase", "Moment", "Shear"])
            writer.writerow(["1", "DL", "100.0", "50.0"])

        forces = adapter.load_forces(csv_path)

        assert len(forces) == 1
        assert forces[0].mu_knm == pytest.approx(100.0)

    def test_mixed_case_headers(self, adapter: STAADAdapter, tmp_path: Path):
        """Headers should be case-insensitive."""
        csv_path = tmp_path / "mixed_case.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["MEMBER", "lc", "My", "FY"])
            writer.writerow(["1", "LC1", "100.0", "50.0"])

        forces = adapter.load_forces(csv_path)

        assert len(forces) == 1


class TestSTAADAdapterEdgeCases:
    """Edge case handling tests."""

    def test_single_station_per_member(self, adapter: STAADAdapter, tmp_path: Path):
        """Handle single station per member."""
        csv_path = tmp_path / "single_station.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Member", "LC", "My", "Fy"])
            writer.writerow(["1", "LC1", "100.0", "50.0"])

        forces = adapter.load_forces(csv_path)

        assert len(forces) == 1
        assert forces[0].station_count == 1

    def test_negative_forces(self, adapter: STAADAdapter, tmp_path: Path):
        """Negative forces should be converted to absolute values."""
        csv_path = tmp_path / "negative.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Member", "LC", "My", "Fy", "Fx"])
            writer.writerow(["1", "LC1", "-150.0", "-75.0", "-50.0"])

        forces = adapter.load_forces(csv_path)

        assert forces[0].mu_knm == pytest.approx(150.0)
        assert forces[0].vu_kn == pytest.approx(75.0)
        assert forces[0].pu_kn == pytest.approx(50.0)

    def test_many_members(self, adapter: STAADAdapter, tmp_path: Path):
        """Handle large number of members efficiently."""
        csv_path = tmp_path / "many_members.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Member", "LC", "My", "Fy"])
            for i in range(1, 101):
                writer.writerow([str(i), "LC1", str(i * 10), str(i * 5)])

        forces = adapter.load_forces(csv_path)

        assert len(forces) == 100

    def test_malformed_numeric_values_skipped(
        self, adapter: STAADAdapter, tmp_path: Path
    ):
        """Rows with invalid numeric values should be skipped."""
        csv_path = tmp_path / "malformed.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Member", "LC", "My", "Fy"])
            writer.writerow(["1", "LC1", "100.0", "50.0"])
            writer.writerow(["2", "LC1", "N/A", "invalid"])  # Bad values
            writer.writerow(["3", "LC1", "80.0", "40.0"])

        forces = adapter.load_forces(csv_path)

        # Should have 2 valid members, member 2 skipped
        assert len(forces) == 2
        assert {f.id for f in forces} == {"1", "3"}
