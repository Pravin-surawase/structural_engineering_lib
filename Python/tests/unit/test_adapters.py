# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for input adapters.

Tests cover:
- ETABSAdapter: CSV loading, column detection, section parsing
- ManualInputAdapter: Dictionary to model conversion
"""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

import pytest

from structural_lib.adapters import (
    ETABSAdapter,
    InputAdapter,
    ManualInputAdapter,
)
from structural_lib.models import (
    BeamForces,
    BeamGeometry,
    DesignDefaults,
    Point3D,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def etabs_adapter() -> ETABSAdapter:
    """Create ETABS adapter instance."""
    return ETABSAdapter()


@pytest.fixture
def manual_adapter() -> ManualInputAdapter:
    """Create manual input adapter instance."""
    return ManualInputAdapter()


@pytest.fixture
def sample_geometry_csv(tmp_path: Path) -> Path:
    """Create sample ETABS geometry CSV."""
    csv_path = tmp_path / "frames_geometry.csv"

    headers = [
        "Story", "Label", "UniqueName", "ObjType", "AnalSect",
        "XI", "YI", "ZI", "XJ", "YJ", "ZJ", "Angle"
    ]

    rows = [
        ["Ground", "B1", "GUID1", "Beam", "B230X450M25",
         "0", "0", "0", "5", "0", "0", "0"],
        ["Ground", "B2", "GUID2", "Beam", "B300X600M30",
         "5", "0", "0", "10", "0", "0", "0"],
        ["Ground", "C1", "GUID3", "Column", "C400X400M40",
         "0", "0", "0", "0", "0", "3", "0"],
        ["First", "B3", "GUID4", "Beam", "B230X450",
         "0", "0", "3", "5", "0", "3", "0"],
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    return csv_path


@pytest.fixture
def sample_forces_csv(tmp_path: Path) -> Path:
    """Create sample ETABS forces CSV."""
    csv_path = tmp_path / "beam_forces.csv"

    headers = [
        "Story", "Label", "Output Case", "Station", "M3", "V2", "P"
    ]

    rows = [
        # Beam B1 with multiple stations
        ["Ground", "B1", "1.2DL+1.5LL", "0", "50", "80", "10"],
        ["Ground", "B1", "1.2DL+1.5LL", "0.5", "100", "20", "10"],
        ["Ground", "B1", "1.2DL+1.5LL", "1", "-60", "-90", "10"],
        # Beam B2 with different load case
        ["Ground", "B2", "1.2DL+1.5LL", "0", "150", "100", "5"],
        ["Ground", "B2", "1.2DL+1.5LL", "0.5", "-200", "30", "5"],
        # Beam B2 with another load case
        ["Ground", "B2", "DL", "0", "80", "50", "2"],
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    return csv_path


@pytest.fixture
def alternate_column_geometry_csv(tmp_path: Path) -> Path:
    """Create CSV with alternate column names."""
    csv_path = tmp_path / "geometry_alt.csv"

    # Use alternate column names
    headers = [
        "Level", "Frame", "Unique Name", "Type", "Section",
        "X1", "Y1", "Z1", "X2", "Y2", "Z2", "Rotation"
    ]

    rows = [
        ["Story1", "FB1", "U1", "Beam", "RC250x500",
         "0", "0", "3", "6", "0", "3", "0"],
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    return csv_path


# =============================================================================
# ETABSAdapter Tests
# =============================================================================


class TestETABSAdapterInterface:
    """Test ETABSAdapter implements InputAdapter interface."""

    def test_is_input_adapter(self, etabs_adapter: ETABSAdapter):
        """Verify ETABSAdapter is an InputAdapter."""
        assert isinstance(etabs_adapter, InputAdapter)

    def test_has_name(self, etabs_adapter: ETABSAdapter):
        """Verify adapter has name."""
        assert etabs_adapter.name == "ETABS"

    def test_has_supported_formats(self, etabs_adapter: ETABSAdapter):
        """Verify adapter declares CSV support."""
        assert ".csv" in etabs_adapter.supported_formats


class TestETABSAdapterCanHandle:
    """Test can_handle() detection logic."""

    def test_handles_geometry_csv(
        self, etabs_adapter: ETABSAdapter, sample_geometry_csv: Path
    ):
        """Should recognize ETABS geometry CSV."""
        assert etabs_adapter.can_handle(sample_geometry_csv) is True

    def test_handles_forces_csv(
        self, etabs_adapter: ETABSAdapter, sample_forces_csv: Path
    ):
        """Should recognize ETABS forces CSV."""
        assert etabs_adapter.can_handle(sample_forces_csv) is True

    def test_rejects_non_csv(self, etabs_adapter: ETABSAdapter, tmp_path: Path):
        """Should reject non-CSV files."""
        txt_file = tmp_path / "data.txt"
        txt_file.write_text("some data")
        assert etabs_adapter.can_handle(txt_file) is False

    def test_rejects_non_existent(self, etabs_adapter: ETABSAdapter):
        """Should reject non-existent files."""
        assert etabs_adapter.can_handle("/nonexistent/file.csv") is False

    def test_rejects_non_etabs_csv(self, etabs_adapter: ETABSAdapter, tmp_path: Path):
        """Should reject CSV without ETABS columns."""
        csv_path = tmp_path / "generic.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["A", "B", "C"])
            writer.writerow(["1", "2", "3"])

        assert etabs_adapter.can_handle(csv_path) is False


class TestETABSAdapterLoadGeometry:
    """Test geometry loading from CSV."""

    def test_loads_beams(
        self, etabs_adapter: ETABSAdapter, sample_geometry_csv: Path
    ):
        """Should load beam geometry from CSV."""
        beams = etabs_adapter.load_geometry(sample_geometry_csv)

        # Should have 3 beams (column filtered out)
        assert len(beams) == 3

    def test_filters_columns(
        self, etabs_adapter: ETABSAdapter, sample_geometry_csv: Path
    ):
        """Should filter out non-beam elements."""
        beams = etabs_adapter.load_geometry(sample_geometry_csv)

        # No columns should be included
        for beam in beams:
            assert beam.id != "C1_Ground"

    def test_beam_geometry_properties(
        self, etabs_adapter: ETABSAdapter, sample_geometry_csv: Path
    ):
        """Should correctly parse beam properties."""
        beams = etabs_adapter.load_geometry(sample_geometry_csv)

        # Find B1
        b1 = next(b for b in beams if "B1" in b.id)

        assert b1.label == "B1"
        assert b1.story == "Ground"
        assert b1.point1.x == 0
        assert b1.point1.y == 0
        assert b1.point1.z == 0
        assert b1.point2.x == 5
        assert b1.length_m == 5.0

    def test_section_parsing_with_grade(
        self, etabs_adapter: ETABSAdapter, sample_geometry_csv: Path
    ):
        """Should parse section with concrete grade."""
        beams = etabs_adapter.load_geometry(sample_geometry_csv)

        # B1 has B230X450M25 -> width=230, depth=450, fck=25
        b1 = next(b for b in beams if "B1" in b.id)

        assert b1.section.width_mm == 230
        assert b1.section.depth_mm == 450
        assert b1.section.fck_mpa == 25

    def test_section_parsing_without_grade(
        self, etabs_adapter: ETABSAdapter, sample_geometry_csv: Path
    ):
        """Should parse section without grade, using defaults."""
        defaults = DesignDefaults(fck_mpa=30)
        beams = etabs_adapter.load_geometry(sample_geometry_csv, defaults)

        # B3 has B230X450 (no grade)
        b3 = next(b for b in beams if "B3" in b.id)

        assert b3.section.width_mm == 230
        assert b3.section.depth_mm == 450
        assert b3.section.fck_mpa == 30  # From defaults

    def test_alternate_column_names(
        self, etabs_adapter: ETABSAdapter, alternate_column_geometry_csv: Path
    ):
        """Should handle alternate ETABS column names."""
        beams = etabs_adapter.load_geometry(alternate_column_geometry_csv)

        assert len(beams) == 1
        beam = beams[0]

        assert beam.label == "FB1"
        assert beam.story == "Story1"
        assert beam.section.width_mm == 250
        assert beam.section.depth_mm == 500

    def test_applies_defaults(
        self, etabs_adapter: ETABSAdapter, sample_geometry_csv: Path
    ):
        """Should apply design defaults for missing values."""
        defaults = DesignDefaults(
            fck_mpa=35,
            fy_mpa=550,
            cover_mm=50,
        )
        beams = etabs_adapter.load_geometry(sample_geometry_csv, defaults)

        # All beams should have defaults for fy and cover
        for beam in beams:
            assert beam.section.fy_mpa == 550
            assert beam.section.cover_mm == 50

    def test_file_not_found(self, etabs_adapter: ETABSAdapter):
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            etabs_adapter.load_geometry("/nonexistent/file.csv")


class TestETABSAdapterLoadForces:
    """Test force loading from CSV."""

    def test_loads_forces(
        self, etabs_adapter: ETABSAdapter, sample_forces_csv: Path
    ):
        """Should load beam forces from CSV."""
        forces = etabs_adapter.load_forces(sample_forces_csv)

        # B1: 1 case, B2: 2 cases
        assert len(forces) == 3

    def test_envelope_max_moment(
        self, etabs_adapter: ETABSAdapter, sample_forces_csv: Path
    ):
        """Should take maximum absolute moment across stations."""
        forces = etabs_adapter.load_forces(sample_forces_csv)

        # Find B1 forces
        b1_forces = next(f for f in forces if "B1" in f.id)

        # Stations: 50, 100, -60 -> max abs = 100
        assert b1_forces.mu_knm == 100

    def test_envelope_max_shear(
        self, etabs_adapter: ETABSAdapter, sample_forces_csv: Path
    ):
        """Should take maximum absolute shear across stations."""
        forces = etabs_adapter.load_forces(sample_forces_csv)

        b1_forces = next(f for f in forces if "B1" in f.id)

        # Stations: 80, 20, -90 -> max abs = 90
        assert b1_forces.vu_kn == 90

    def test_station_count(
        self, etabs_adapter: ETABSAdapter, sample_forces_csv: Path
    ):
        """Should count stations per beam/case."""
        forces = etabs_adapter.load_forces(sample_forces_csv)

        b1_forces = next(f for f in forces if "B1" in f.id)

        assert b1_forces.station_count == 3

    def test_multiple_load_cases(
        self, etabs_adapter: ETABSAdapter, sample_forces_csv: Path
    ):
        """Should handle multiple load cases per beam."""
        forces = etabs_adapter.load_forces(sample_forces_csv)

        # B2 has two load cases
        b2_forces = [f for f in forces if "B2" in f.id]
        assert len(b2_forces) == 2

        load_cases = {f.load_case for f in b2_forces}
        assert "1.2DL+1.5LL" in load_cases
        assert "DL" in load_cases

    def test_beam_id_format(
        self, etabs_adapter: ETABSAdapter, sample_forces_csv: Path
    ):
        """Should format beam ID as label_story."""
        forces = etabs_adapter.load_forces(sample_forces_csv)

        b1_forces = next(f for f in forces if "B1" in f.id)

        # Should be B1_Ground to match geometry
        assert b1_forces.id == "B1_Ground"

    def test_file_not_found(self, etabs_adapter: ETABSAdapter):
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            etabs_adapter.load_forces("/nonexistent/file.csv")


class TestETABSAdapterSectionParsing:
    """Test section name parsing edge cases."""

    def test_parse_b_width_x_depth_m_grade(self, etabs_adapter: ETABSAdapter):
        """Parse BwidthXdepthMgrade format."""
        section = etabs_adapter._parse_section_name("B300X600M40", None)

        assert section.width_mm == 300
        assert section.depth_mm == 600
        assert section.fck_mpa == 40

    def test_parse_lowercase(self, etabs_adapter: ETABSAdapter):
        """Parse lowercase section name."""
        section = etabs_adapter._parse_section_name("b230x450m25", None)

        assert section.width_mm == 230
        assert section.depth_mm == 450
        assert section.fck_mpa == 25

    def test_parse_simple_dimension(self, etabs_adapter: ETABSAdapter):
        """Parse simple widthXdepth format."""
        defaults = DesignDefaults(fck_mpa=30)
        section = etabs_adapter._parse_section_name("RC300x500", defaults)

        assert section.width_mm == 300
        assert section.depth_mm == 500
        assert section.fck_mpa == 30  # From defaults

    def test_parse_unparseable_uses_defaults(self, etabs_adapter: ETABSAdapter):
        """Unparseable names should use defaults."""
        defaults = DesignDefaults(fck_mpa=25, fy_mpa=500, cover_mm=40)
        section = etabs_adapter._parse_section_name("UNKNOWN_SECTION", defaults)

        assert section.width_mm == 300  # Default
        assert section.depth_mm == 500  # Default
        assert section.fck_mpa == 25


# =============================================================================
# ManualInputAdapter Tests
# =============================================================================


class TestManualInputAdapterInterface:
    """Test ManualInputAdapter interface."""

    def test_is_input_adapter(self, manual_adapter: ManualInputAdapter):
        """Verify ManualInputAdapter is an InputAdapter."""
        assert isinstance(manual_adapter, InputAdapter)

    def test_has_name(self, manual_adapter: ManualInputAdapter):
        """Verify adapter has name."""
        assert manual_adapter.name == "Manual"

    def test_cannot_handle_files(self, manual_adapter: ManualInputAdapter):
        """Manual adapter doesn't handle files."""
        assert manual_adapter.can_handle("any_file.csv") is False


class TestManualInputAdapterGeometry:
    """Test manual geometry creation."""

    def test_create_from_dict(self):
        """Should create BeamGeometry from dictionary."""
        data = {
            "id": "B1",
            "label": "B1",
            "story": "Ground",
            "point1": {"x": 0, "y": 0, "z": 0},
            "point2": {"x": 5, "y": 0, "z": 0},
            "width_mm": 300,
            "depth_mm": 500,
        }

        beam = ManualInputAdapter.geometry_from_dict(data)

        assert isinstance(beam, BeamGeometry)
        assert beam.id == "B1"
        assert beam.length_m == 5.0
        assert beam.section.width_mm == 300

    def test_create_with_nested_section(self):
        """Should accept nested section properties."""
        data = {
            "id": "B2",
            "point1": {"x": 0, "y": 0, "z": 0},
            "point2": {"x": 6, "y": 0, "z": 0},
            "section": {
                "width_mm": 350,
                "depth_mm": 600,
                "fck_mpa": 35,
                "fy_mpa": 550,
                "cover_mm": 45,
            },
        }

        beam = ManualInputAdapter.geometry_from_dict(data)

        assert beam.section.width_mm == 350
        assert beam.section.fck_mpa == 35
        assert beam.section.fy_mpa == 550

    def test_applies_defaults(self):
        """Should apply defaults for missing properties."""
        defaults = DesignDefaults(fck_mpa=40, fy_mpa=550)
        data = {
            "id": "B3",
            "point1": {"x": 0, "y": 0, "z": 0},
            "point2": {"x": 4, "y": 0, "z": 0},
        }

        beam = ManualInputAdapter.geometry_from_dict(data, defaults)

        assert beam.section.fck_mpa == 40
        assert beam.section.fy_mpa == 550

    def test_validates_input(self):
        """Should validate input data."""
        data = {
            "id": "",  # Invalid: empty
            "point1": {"x": 0, "y": 0, "z": 0},
            "point2": {"x": 5, "y": 0, "z": 0},
        }

        with pytest.raises(Exception):  # Pydantic validation error
            ManualInputAdapter.geometry_from_dict(data)


class TestManualInputAdapterForces:
    """Test manual force creation."""

    def test_create_from_dict(self):
        """Should create BeamForces from dictionary."""
        data = {
            "id": "B1_Ground",
            "load_case": "1.2DL+1.5LL",
            "mu_knm": 150,
            "vu_kn": 100,
            "pu_kn": 10,
        }

        forces = ManualInputAdapter.forces_from_dict(data)

        assert isinstance(forces, BeamForces)
        assert forces.id == "B1_Ground"
        assert forces.mu_knm == 150
        assert forces.vu_kn == 100

    def test_validates_input(self):
        """Should validate input data."""
        data = {
            "id": "B1",
            "load_case": "DL",
            "mu_knm": -100,  # Invalid: negative
            "vu_kn": 50,
        }

        with pytest.raises(Exception):  # Pydantic validation error
            ManualInputAdapter.forces_from_dict(data)


# =============================================================================
# Integration Tests
# =============================================================================


class TestAdapterIntegration:
    """Test adapter integration with canonical models."""

    def test_geometry_forces_matching(
        self,
        etabs_adapter: ETABSAdapter,
        sample_geometry_csv: Path,
        sample_forces_csv: Path,
    ):
        """Geometry and forces should have matching IDs."""
        beams = etabs_adapter.load_geometry(sample_geometry_csv)
        forces = etabs_adapter.load_forces(sample_forces_csv)

        beam_ids = {b.id for b in beams}
        force_ids = {f.id for f in forces}

        # All force IDs should have corresponding geometry
        matching = force_ids & beam_ids
        assert len(matching) > 0

    def test_model_serialization(
        self,
        etabs_adapter: ETABSAdapter,
        sample_geometry_csv: Path,
    ):
        """Loaded models should be JSON serializable."""
        beams = etabs_adapter.load_geometry(sample_geometry_csv)

        for beam in beams:
            json_str = beam.model_dump_json()
            assert isinstance(json_str, str)
            assert len(json_str) > 0

    def test_model_immutability(
        self,
        etabs_adapter: ETABSAdapter,
        sample_geometry_csv: Path,
    ):
        """Loaded models should be immutable."""
        beams = etabs_adapter.load_geometry(sample_geometry_csv)

        with pytest.raises(Exception):  # Frozen model
            beams[0].story = "Modified"
