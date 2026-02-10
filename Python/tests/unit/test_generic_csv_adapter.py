# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for GenericCSVAdapter (Excel/manual CSV input).

This test module verifies the GenericCSVAdapter's ability to handle:
1. Generic format CSV (beam_id, mu_knm, vu_kn, b_mm, D_mm)
2. Excel BeamDesignSchedule template format
3. Various column name aliases and edge cases

Author: Session 41 Agent
Task: TASK-3D-002
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from structural_lib.services.adapters import GenericCSVAdapter
from structural_lib.core.models import DesignDefaults


@pytest.fixture
def adapter() -> GenericCSVAdapter:
    """Create GenericCSVAdapter instance."""
    return GenericCSVAdapter()


@pytest.fixture
def generic_format_csv(tmp_path: Path) -> Path:
    """Create a generic format CSV file."""
    csv_path = tmp_path / "generic_beams.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["beam_id", "story", "mu_knm", "vu_kn", "b_mm", "D_mm", "fck_nmm2"]
        )
        writer.writerow(["B1", "GF", "180.5", "125.0", "300", "500", "25"])
        writer.writerow(["B2", "GF", "145.2", "98.3", "300", "450", "25"])
        writer.writerow(["B3", "FF", "210.8", "140.5", "350", "600", "30"])
    return csv_path


@pytest.fixture
def excel_template_csv(tmp_path: Path) -> Path:
    """Create an Excel BeamDesignSchedule template format CSV."""
    csv_path = tmp_path / "excel_beams.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "BeamID",
                "b (mm)",
                "D (mm)",
                "d (mm)",
                "fck",
                "fy",
                "Mu (kN-m)",
                "Vu (kN)",
                "Cover (mm)",
            ]
        )
        writer.writerow(["B1", "300", "500", "450", "25", "500", "150", "100", "40"])
        writer.writerow(["B2", "300", "450", "400", "25", "500", "120", "80", "40"])
        writer.writerow(["B3", "350", "600", "550", "30", "500", "250", "150", "40"])
    return csv_path


@pytest.fixture
def etabs_format_csv(tmp_path: Path) -> Path:
    """Create an ETABS format CSV (should be rejected)."""
    csv_path = tmp_path / "etabs_forces.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Story", "Label", "Output Case", "M3", "V2"])
        writer.writerow(["Story1", "B1", "1.5DL+LL", "150", "100"])
    return csv_path


@pytest.fixture
def staad_format_csv(tmp_path: Path) -> Path:
    """Create a STAAD format CSV (should be rejected)."""
    csv_path = tmp_path / "staad_forces.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Member", "LC", "My", "Fy", "Fx", "Dist"])
        writer.writerow(["1", "LC1", "150", "100", "50", "0"])
    return csv_path


class TestGenericCSVAdapterCanHandle:
    """Test can_handle detection logic."""

    def test_can_handle_generic_format(
        self, adapter: GenericCSVAdapter, generic_format_csv: Path
    ):
        """GenericCSVAdapter should handle generic format CSV."""
        assert adapter.can_handle(generic_format_csv) is True

    def test_can_handle_excel_template(
        self, adapter: GenericCSVAdapter, excel_template_csv: Path
    ):
        """GenericCSVAdapter should handle Excel template CSV."""
        assert adapter.can_handle(excel_template_csv) is True

    def test_rejects_etabs_format(
        self, adapter: GenericCSVAdapter, etabs_format_csv: Path
    ):
        """GenericCSVAdapter should reject ETABS format files."""
        assert adapter.can_handle(etabs_format_csv) is False

    def test_rejects_staad_format(
        self, adapter: GenericCSVAdapter, staad_format_csv: Path
    ):
        """GenericCSVAdapter should reject STAAD format files."""
        assert adapter.can_handle(staad_format_csv) is False

    def test_rejects_nonexistent_file(self, adapter: GenericCSVAdapter):
        """GenericCSVAdapter should reject non-existent files."""
        assert adapter.can_handle(Path("/nonexistent/file.csv")) is False

    def test_rejects_wrong_extension(self, adapter: GenericCSVAdapter, tmp_path: Path):
        """GenericCSVAdapter should reject non-CSV files."""
        xlsx_file = tmp_path / "beams.xlsx"
        xlsx_file.touch()
        assert adapter.can_handle(xlsx_file) is False


class TestGenericCSVAdapterLoadForces:
    """Test load_forces for generic/Excel CSV."""

    def test_load_generic_format_forces(
        self, adapter: GenericCSVAdapter, generic_format_csv: Path
    ):
        """Load forces from generic format CSV."""
        forces = adapter.load_forces(generic_format_csv)

        assert len(forces) == 3

        # Check first beam
        b1 = next(f for f in forces if f.id == "B1_GF")
        assert b1.mu_knm == pytest.approx(180.5)
        assert b1.vu_kn == pytest.approx(125.0)
        assert b1.load_case == "Design"

    def test_load_excel_template_forces(
        self, adapter: GenericCSVAdapter, excel_template_csv: Path
    ):
        """Load forces from Excel template format CSV."""
        forces = adapter.load_forces(excel_template_csv)

        assert len(forces) == 3

        # Check specific values
        b1 = next(f for f in forces if f.id == "B1")
        assert b1.mu_knm == pytest.approx(150.0)
        assert b1.vu_kn == pytest.approx(100.0)

        b3 = next(f for f in forces if f.id == "B3")
        assert b3.mu_knm == pytest.approx(250.0)
        assert b3.vu_kn == pytest.approx(150.0)

    def test_load_forces_with_load_case(
        self, adapter: GenericCSVAdapter, tmp_path: Path
    ):
        """Load forces with explicit load case column."""
        csv_path = tmp_path / "with_lc.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["BeamID", "Load Case", "Mu (kN-m)", "Vu (kN)"])
            writer.writerow(["B1", "1.5DL+LL", "180.0", "120.0"])
            writer.writerow(["B1", "1.2DL+1.6LL", "200.0", "140.0"])

        forces = adapter.load_forces(csv_path)

        assert len(forces) == 2
        assert forces[0].load_case == "1.5DL+LL"
        assert forces[1].load_case == "1.2DL+1.6LL"

    def test_load_forces_file_not_found(self, adapter: GenericCSVAdapter):
        """Raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            adapter.load_forces(Path("/nonexistent/forces.csv"))

    def test_load_forces_missing_beam_id(
        self, adapter: GenericCSVAdapter, tmp_path: Path
    ):
        """Raise ValueError when beam ID column is missing."""
        csv_path = tmp_path / "no_id.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["X", "Y", "Z"])
            writer.writerow(["1", "2", "3"])

        with pytest.raises(ValueError, match="Missing beam identifier"):
            adapter.load_forces(csv_path)

    def test_load_forces_missing_force_columns(
        self, adapter: GenericCSVAdapter, tmp_path: Path
    ):
        """Raise ValueError when no force columns present."""
        csv_path = tmp_path / "no_forces.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["BeamID", "b (mm)", "D (mm)"])
            writer.writerow(["B1", "300", "500"])

        with pytest.raises(ValueError, match="Missing force columns"):
            adapter.load_forces(csv_path)

    def test_handles_empty_rows(self, adapter: GenericCSVAdapter, tmp_path: Path):
        """Skip rows with empty beam ID."""
        csv_path = tmp_path / "empty_rows.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["BeamID", "Mu (kN-m)", "Vu (kN)"])
            writer.writerow(["B1", "100.0", "50.0"])
            writer.writerow(["", "999.0", "999.0"])  # Empty ID
            writer.writerow(["B2", "80.0", "40.0"])

        forces = adapter.load_forces(csv_path)

        assert len(forces) == 2
        assert {f.id for f in forces} == {"B1", "B2"}


class TestGenericCSVAdapterLoadGeometry:
    """Test load_geometry for generic/Excel CSV."""

    def test_load_generic_format_geometry(
        self, adapter: GenericCSVAdapter, generic_format_csv: Path
    ):
        """Load geometry from generic format CSV."""
        beams = adapter.load_geometry(generic_format_csv)

        assert len(beams) == 3

        # Check first beam
        b1 = next(b for b in beams if b.source_id == "B1")
        assert b1.id == "B1_GF"
        assert b1.story == "GF"
        assert b1.section.width_mm == pytest.approx(300.0)
        assert b1.section.depth_mm == pytest.approx(500.0)
        assert b1.section.fck_mpa == pytest.approx(25.0)

    def test_load_excel_template_geometry(
        self, adapter: GenericCSVAdapter, excel_template_csv: Path
    ):
        """Load geometry from Excel template format CSV."""
        beams = adapter.load_geometry(excel_template_csv)

        assert len(beams) == 3

        # Check values
        b1 = next(b for b in beams if b.source_id == "B1")
        assert b1.section.width_mm == pytest.approx(300.0)
        assert b1.section.depth_mm == pytest.approx(500.0)
        assert b1.section.fck_mpa == pytest.approx(25.0)
        assert b1.section.fy_mpa == pytest.approx(500.0)
        assert b1.section.cover_mm == pytest.approx(40.0)

        b3 = next(b for b in beams if b.source_id == "B3")
        assert b3.section.width_mm == pytest.approx(350.0)
        assert b3.section.depth_mm == pytest.approx(600.0)
        assert b3.section.fck_mpa == pytest.approx(30.0)

    def test_load_geometry_with_span(self, adapter: GenericCSVAdapter, tmp_path: Path):
        """Load geometry with span column for coordinates."""
        csv_path = tmp_path / "with_span.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["BeamID", "Span (mm)", "b (mm)", "D (mm)"])
            writer.writerow(["B1", "6000", "300", "500"])

        beams = adapter.load_geometry(csv_path)

        assert len(beams) == 1
        # Span of 6000mm = 6m in coordinates
        assert beams[0].point2.x == pytest.approx(6.0)
        assert beams[0].length_m == pytest.approx(6.0)

    def test_load_geometry_uses_defaults(
        self, adapter: GenericCSVAdapter, tmp_path: Path
    ):
        """Use default values when section properties not in CSV."""
        csv_path = tmp_path / "minimal.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["BeamID", "Mu (kN-m)"])
            writer.writerow(["B1", "150"])

        defaults = DesignDefaults(fck_mpa=30.0, fy_mpa=415.0, cover_mm=50.0)
        beams = adapter.load_geometry(csv_path, defaults=defaults)

        assert len(beams) == 1
        # Default dimensions from adapter (300mm x 500mm)
        assert beams[0].section.width_mm == pytest.approx(300.0)
        assert beams[0].section.depth_mm == pytest.approx(500.0)
        # Material properties from defaults
        assert beams[0].section.fck_mpa == pytest.approx(30.0)
        assert beams[0].section.fy_mpa == pytest.approx(415.0)
        assert beams[0].section.cover_mm == pytest.approx(50.0)

    def test_load_geometry_missing_beam_id(
        self, adapter: GenericCSVAdapter, tmp_path: Path
    ):
        """Raise ValueError when beam ID column is missing."""
        csv_path = tmp_path / "no_id.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["b (mm)", "D (mm)"])
            writer.writerow(["300", "500"])

        with pytest.raises(ValueError, match="Missing beam identifier"):
            adapter.load_geometry(csv_path)


class TestGenericCSVAdapterLoadCombined:
    """Test load_combined for loading both geometry and forces."""

    def test_load_combined(self, adapter: GenericCSVAdapter, excel_template_csv: Path):
        """Load both geometry and forces from combined CSV."""
        geometry, forces = adapter.load_combined(excel_template_csv)

        assert len(geometry) == 3
        assert len(forces) == 3

        # Check geometry
        b1_geo = next(b for b in geometry if b.source_id == "B1")
        assert b1_geo.section.width_mm == pytest.approx(300.0)

        # Check forces
        b1_force = next(f for f in forces if f.id == "B1")
        assert b1_force.mu_knm == pytest.approx(150.0)


class TestGenericCSVAdapterColumnMapping:
    """Test column mapping flexibility."""

    def test_case_insensitive_columns(self, adapter: GenericCSVAdapter, tmp_path: Path):
        """Column names should be case-insensitive."""
        csv_path = tmp_path / "mixed_case.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["BEAMID", "MU (KN-M)", "VU (KN)"])
            writer.writerow(["B1", "150", "100"])

        forces = adapter.load_forces(csv_path)
        assert len(forces) == 1
        assert forces[0].mu_knm == pytest.approx(150.0)

    def test_alternate_column_names(self, adapter: GenericCSVAdapter, tmp_path: Path):
        """Accept alternate column name patterns."""
        csv_path = tmp_path / "alternate.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Moment", "Shear", "Width", "Depth"])
            writer.writerow(["B1", "150", "100", "300", "500"])

        forces = adapter.load_forces(csv_path)
        geometry = adapter.load_geometry(csv_path)

        assert len(forces) == 1
        assert forces[0].mu_knm == pytest.approx(150.0)

        assert len(geometry) == 1
        assert geometry[0].section.width_mm == pytest.approx(300.0)


class TestGenericCSVAdapterEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_non_numeric_forces(
        self, adapter: GenericCSVAdapter, tmp_path: Path
    ):
        """Handle non-numeric force values gracefully."""
        csv_path = tmp_path / "bad_forces.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["BeamID", "Mu (kN-m)", "Vu (kN)"])
            writer.writerow(["B1", "150.0", "100.0"])
            writer.writerow(["B2", "N/A", "---"])  # Invalid values

        forces = adapter.load_forces(csv_path)

        assert len(forces) == 2
        # B2 should have 0 for invalid forces
        b2 = next(f for f in forces if f.id == "B2")
        assert b2.mu_knm == pytest.approx(0.0)
        assert b2.vu_kn == pytest.approx(0.0)

    def test_handles_bom_encoding(self, adapter: GenericCSVAdapter, tmp_path: Path):
        """Handle UTF-8 BOM encoding from Excel exports."""
        csv_path = tmp_path / "with_bom.csv"
        # Write with BOM
        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["BeamID", "Mu (kN-m)", "Vu (kN)"])
            writer.writerow(["B1", "150.0", "100.0"])

        forces = adapter.load_forces(csv_path)
        assert len(forces) == 1
        assert forces[0].id == "B1"

    def test_preserves_negative_forces_as_absolute(
        self, adapter: GenericCSVAdapter, tmp_path: Path
    ):
        """Negative forces should be converted to absolute values."""
        csv_path = tmp_path / "negative.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["BeamID", "Mu (kN-m)", "Vu (kN)"])
            writer.writerow(["B1", "-150.0", "-100.0"])

        forces = adapter.load_forces(csv_path)

        assert len(forces) == 1
        assert forces[0].mu_knm == pytest.approx(150.0)  # abs(-150)
        assert forces[0].vu_kn == pytest.approx(100.0)  # abs(-100)

    def test_handles_whitespace_in_values(
        self, adapter: GenericCSVAdapter, tmp_path: Path
    ):
        """Handle whitespace in cell values."""
        csv_path = tmp_path / "whitespace.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["BeamID", "Mu (kN-m)", "Vu (kN)"])
            writer.writerow(["  B1  ", " 150.0 ", " 100.0 "])

        forces = adapter.load_forces(csv_path)

        assert len(forces) == 1
        assert forces[0].id == "B1"  # Trimmed
        assert forces[0].mu_knm == pytest.approx(150.0)
