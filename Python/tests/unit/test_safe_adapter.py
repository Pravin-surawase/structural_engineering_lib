# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for SAFE adapter.

These tests verify the SAFEAdapter can load slab strip data
from CSI SAFE export formats.
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from structural_lib.adapters import SAFEAdapter
from structural_lib.models import BeamForces, BeamGeometry

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def safe_adapter() -> SAFEAdapter:
    """Create SAFE adapter instance."""
    return SAFEAdapter()


@pytest.fixture
def sample_safe_forces_csv(tmp_path: Path) -> Path:
    """Create sample SAFE forces CSV with station data."""
    content = dedent(
        """\
        Strip,SpanName,LoadCombo,Position,M22,V23
        Strip1-A,Span1,1.5DL+1.5LL,0,0,-85.2
        Strip1-A,Span1,1.5DL+1.5LL,1500,120.5,0
        Strip1-A,Span1,1.5DL+1.5LL,3000,0,85.2
        Strip2-B,Span2,1.5DL+1.5LL,0,0,-72.1
        Strip2-B,Span2,1.5DL+1.5LL,2000,95.3,0
        Strip2-B,Span2,DL,0,0,-45.0
        Strip2-B,Span2,DL,2000,55.0,0
    """
    )
    filepath = tmp_path / "safe_forces.csv"
    filepath.write_text(content)
    return filepath


@pytest.fixture
def sample_safe_envelope_csv(tmp_path: Path) -> Path:
    """Create sample SAFE envelope format CSV."""
    content = dedent(
        """\
        Strip,Story,Mu_max,Vu_max,Width,Thickness
        Strip1,Slab1,120.5,85.2,1000,200
        Strip2,Slab1,95.3,72.1,1000,200
        Strip3,Slab2,145.0,98.5,1000,250
    """
    )
    filepath = tmp_path / "safe_envelope.csv"
    filepath.write_text(content)
    return filepath


@pytest.fixture
def sample_safe_geometry_csv(tmp_path: Path) -> Path:
    """Create sample SAFE geometry CSV."""
    content = dedent(
        """\
        Strip,Story,Width,Depth_mm,Point1X,Point1Y,Point2X,Point2Y
        Strip1,Slab1,1000,200,0.0,0.0,5.0,0.0
        Strip2,Slab1,1000,200,0.0,3.0,5.0,3.0
        Strip3,Slab2,1200,250,0.0,0.0,6.0,0.0
    """
    )
    filepath = tmp_path / "safe_geometry.csv"
    filepath.write_text(content)
    return filepath


# =============================================================================
# Test: can_handle
# =============================================================================


class TestSAFEAdapterCanHandle:
    """Test SAFE format detection."""

    def test_detects_safe_csv(self, sample_safe_forces_csv: Path) -> None:
        """Should detect SAFE CSV by column names."""
        adapter = SAFEAdapter()
        assert adapter.can_handle(sample_safe_forces_csv)

    def test_rejects_etabs_csv(self, tmp_path: Path) -> None:
        """Should reject ETABS format CSV."""
        content = "Story,Label,Output Case,Station,M3,V2\nS1,B1,LC1,0,100,50\n"
        filepath = tmp_path / "etabs.csv"
        filepath.write_text(content)

        adapter = SAFEAdapter()
        assert not adapter.can_handle(filepath)

    def test_rejects_nonexistent_file(self) -> None:
        """Should reject non-existent file."""
        adapter = SAFEAdapter()
        assert not adapter.can_handle("/nonexistent/file.csv")

    def test_rejects_non_csv(self, tmp_path: Path) -> None:
        """Should reject non-CSV files."""
        filepath = tmp_path / "data.txt"
        filepath.write_text("Strip,M22,V23\n")

        adapter = SAFEAdapter()
        assert not adapter.can_handle(filepath)


# =============================================================================
# Test: load_forces
# =============================================================================


class TestSAFEAdapterLoadForces:
    """Test force loading from SAFE CSV."""

    def test_loads_station_data(
        self, safe_adapter: SAFEAdapter, sample_safe_forces_csv: Path
    ) -> None:
        """Should load SAFE forces with station data."""
        forces = safe_adapter.load_forces(sample_safe_forces_csv)

        # Strip1: 1 case, Strip2: 2 cases
        assert len(forces) == 3

    def test_computes_envelope(
        self, safe_adapter: SAFEAdapter, sample_safe_forces_csv: Path
    ) -> None:
        """Should compute envelope (max values) across stations."""
        forces = safe_adapter.load_forces(sample_safe_forces_csv)

        # Find Strip1-A forces
        strip1 = next(f for f in forces if "Strip1" in f.id)

        # Max moment should be 120.5 (from position 1500)
        assert strip1.mu_knm == pytest.approx(120.5)

        # Max shear should be 85.2 (from positions 0 and 3000)
        assert strip1.vu_kn == pytest.approx(85.2)

    def test_handles_envelope_format(
        self, safe_adapter: SAFEAdapter, sample_safe_envelope_csv: Path
    ) -> None:
        """Should load pre-computed envelope format."""
        forces = safe_adapter.load_forces(sample_safe_envelope_csv)

        assert len(forces) == 3

        strip1 = next(f for f in forces if "Strip1" in f.id)
        assert strip1.mu_knm == pytest.approx(120.5)
        assert strip1.vu_kn == pytest.approx(85.2)
        assert strip1.load_case == "Envelope"

    def test_multiple_load_cases(
        self, safe_adapter: SAFEAdapter, sample_safe_forces_csv: Path
    ) -> None:
        """Should handle multiple load cases per strip."""
        forces = safe_adapter.load_forces(sample_safe_forces_csv)

        # Strip2 has two load cases
        strip2_forces = [f for f in forces if "Strip2" in f.id]
        assert len(strip2_forces) == 2

        load_cases = {f.load_case for f in strip2_forces}
        assert "1.5DL+1.5LL" in load_cases
        assert "DL" in load_cases

    def test_id_format(
        self, safe_adapter: SAFEAdapter, sample_safe_envelope_csv: Path
    ) -> None:
        """Should format ID as strip_story."""
        forces = safe_adapter.load_forces(sample_safe_envelope_csv)

        strip1 = next(f for f in forces if "Strip1" in f.id)
        assert strip1.id == "Strip1_Slab1"

    def test_file_not_found(self, safe_adapter: SAFEAdapter) -> None:
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            safe_adapter.load_forces("/nonexistent/file.csv")

    def test_missing_columns_error(
        self, safe_adapter: SAFEAdapter, tmp_path: Path
    ) -> None:
        """Should raise ValueError for missing required columns."""
        content = "Name,Value\nA,1\n"
        filepath = tmp_path / "invalid.csv"
        filepath.write_text(content)

        with pytest.raises(ValueError, match="Missing"):
            safe_adapter.load_forces(filepath)


# =============================================================================
# Test: load_geometry
# =============================================================================


class TestSAFEAdapterLoadGeometry:
    """Test geometry loading from SAFE CSV."""

    def test_loads_geometry(
        self, safe_adapter: SAFEAdapter, sample_safe_geometry_csv: Path
    ) -> None:
        """Should load strip geometry."""
        beams = safe_adapter.load_geometry(sample_safe_geometry_csv)

        assert len(beams) == 3

    def test_coordinates_loaded(
        self, safe_adapter: SAFEAdapter, sample_safe_geometry_csv: Path
    ) -> None:
        """Should load coordinate data when available."""
        beams = safe_adapter.load_geometry(sample_safe_geometry_csv)

        strip1 = next(b for b in beams if "Strip1" in b.id)
        assert strip1.point1.x == pytest.approx(0.0)
        assert strip1.point2.x == pytest.approx(5.0)
        assert strip1.length_m == pytest.approx(5.0)

    def test_section_properties(
        self, safe_adapter: SAFEAdapter, sample_safe_geometry_csv: Path
    ) -> None:
        """Should load section properties."""
        beams = safe_adapter.load_geometry(sample_safe_geometry_csv)

        strip1 = next(b for b in beams if "Strip1" in b.id)
        assert strip1.section.width_mm == pytest.approx(1000)
        assert strip1.section.depth_mm == pytest.approx(200)

        strip3 = next(b for b in beams if "Strip3" in b.id)
        assert strip3.section.depth_mm == pytest.approx(250)

    def test_id_format(
        self, safe_adapter: SAFEAdapter, sample_safe_geometry_csv: Path
    ) -> None:
        """Should format ID as strip_story."""
        beams = safe_adapter.load_geometry(sample_safe_geometry_csv)

        strip1 = next(b for b in beams if "Strip1" in b.id)
        assert strip1.id == "Strip1_Slab1"

    def test_file_not_found(self, safe_adapter: SAFEAdapter) -> None:
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            safe_adapter.load_geometry("/nonexistent/file.csv")


# =============================================================================
# Integration Tests
# =============================================================================


class TestSAFEAdapterIntegration:
    """Integration tests for SAFE adapter."""

    def test_geometry_forces_matching(
        self,
        safe_adapter: SAFEAdapter,
        sample_safe_geometry_csv: Path,
        sample_safe_envelope_csv: Path,
    ) -> None:
        """Geometry and forces should have matching IDs."""
        beams = safe_adapter.load_geometry(sample_safe_geometry_csv)
        forces = safe_adapter.load_forces(sample_safe_envelope_csv)

        beam_ids = {b.id for b in beams}
        force_ids = {f.id for f in forces}

        # All IDs should match
        matching = force_ids & beam_ids
        assert len(matching) > 0

    def test_model_serialization(
        self,
        safe_adapter: SAFEAdapter,
        sample_safe_geometry_csv: Path,
    ) -> None:
        """Loaded models should be JSON serializable."""
        beams = safe_adapter.load_geometry(sample_safe_geometry_csv)

        for beam in beams:
            # Serialize excluding computed fields
            json_str = beam.model_dump_json(exclude={"length_m", "is_vertical"})
            # Parse and exclude computed fields from section too
            import json

            data = json.loads(json_str)
            if "section" in data and "effective_depth_mm" in data["section"]:
                del data["section"]["effective_depth_mm"]
            restored = BeamGeometry.model_validate(data)
            assert restored.id == beam.id

    def test_forces_serialization(
        self,
        safe_adapter: SAFEAdapter,
        sample_safe_forces_csv: Path,
    ) -> None:
        """Force models should be JSON serializable."""
        forces = safe_adapter.load_forces(sample_safe_forces_csv)

        for force in forces:
            json_str = force.model_dump_json()
            restored = BeamForces.model_validate_json(json_str)
            assert restored.id == force.id
            assert restored.mu_knm == force.mu_knm
