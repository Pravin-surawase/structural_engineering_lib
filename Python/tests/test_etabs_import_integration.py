# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Integration tests for etabs_import Pydantic conversion functions.

These tests verify the integration between the existing dataclass-based
etabs_import workflow and the new Pydantic canonical data models.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from structural_lib.etabs_import import (
    ETABSEnvelopeResult,
    FrameGeometry,
    envelopes_to_beam_forces,
    frames_to_beam_geometries,
    load_frames_geometry,
    to_beam_forces,
    to_beam_geometry,
)
from structural_lib.models import BeamForces, BeamGeometry, FrameType

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_frame_geometry() -> FrameGeometry:
    """Create a sample FrameGeometry dataclass for testing."""
    return FrameGeometry(
        unique_name="123",
        label="B1",
        story="Ground",
        frame_type="Beam",
        section_name="B300x500",
        point1_name="P1",
        point2_name="P2",
        point1_x=0.0,
        point1_y=0.0,
        point1_z=3.0,
        point2_x=5.0,
        point2_y=0.0,
        point2_z=3.0,
        angle=0.0,
        cardinal_point=10,
    )


@pytest.fixture
def sample_column_geometry() -> FrameGeometry:
    """Create a sample column FrameGeometry for testing."""
    return FrameGeometry(
        unique_name="456",
        label="C1",
        story="Ground",
        frame_type="Column",
        section_name="C300x300",
        point1_name="P3",
        point2_name="P4",
        point1_x=0.0,
        point1_y=0.0,
        point1_z=0.0,
        point2_x=0.0,
        point2_y=0.0,
        point2_z=3.0,
        angle=0.0,
        cardinal_point=10,
    )


@pytest.fixture
def sample_envelope() -> ETABSEnvelopeResult:
    """Create a sample ETABSEnvelopeResult dataclass for testing."""
    return ETABSEnvelopeResult(
        story="Ground",
        beam_id="B1",
        case_id="1.5(DL+LL)",
        mu_knm=150.0,
        vu_kn=100.0,
        station_count=5,
    )


@pytest.fixture
def real_etabs_data_dir() -> Path | None:
    """Path to real ETABS test data, or None if not available."""
    data_dir = Path("VBA/ETABS_Export_v2/Etabs_output/2026-01-17_222801")
    if data_dir.exists():
        return data_dir
    # Try relative to structural_engineering_lib
    alt_dir = Path(__file__).parents[3] / data_dir
    if alt_dir.exists():
        return alt_dir
    return None


# =============================================================================
# Unit Tests: to_beam_geometry
# =============================================================================


class TestToBeamGeometry:
    """Tests for to_beam_geometry conversion function."""

    def test_basic_conversion(self, sample_frame_geometry: FrameGeometry) -> None:
        """Test basic dataclass to Pydantic conversion."""
        beam = to_beam_geometry(sample_frame_geometry)

        assert isinstance(beam, BeamGeometry)
        assert beam.label == "B1"
        assert beam.story == "Ground"
        assert beam.frame_type == FrameType.BEAM
        assert beam.source_id == "123"

    def test_id_format(self, sample_frame_geometry: FrameGeometry) -> None:
        """Test that ID is formatted as label_story."""
        beam = to_beam_geometry(sample_frame_geometry)
        assert beam.id == "B1_Ground"

    def test_coordinates_preserved(self, sample_frame_geometry: FrameGeometry) -> None:
        """Test that coordinates are correctly converted."""
        beam = to_beam_geometry(sample_frame_geometry)

        assert beam.point1.x == 0.0
        assert beam.point1.y == 0.0
        assert beam.point1.z == 3.0
        assert beam.point2.x == 5.0
        assert beam.point2.y == 0.0
        assert beam.point2.z == 3.0

    def test_length_calculated(self, sample_frame_geometry: FrameGeometry) -> None:
        """Test that length is calculated correctly."""
        beam = to_beam_geometry(sample_frame_geometry)
        assert abs(beam.length_m - 5.0) < 0.001

    def test_section_properties_custom(
        self, sample_frame_geometry: FrameGeometry
    ) -> None:
        """Test custom section properties."""
        beam = to_beam_geometry(
            sample_frame_geometry,
            width_mm=400.0,
            depth_mm=600.0,
            fck_mpa=30.0,
            fy_mpa=550.0,
            cover_mm=50.0,
        )

        assert beam.section.width_mm == 400.0
        assert beam.section.depth_mm == 600.0
        assert beam.section.fck_mpa == 30.0
        assert beam.section.fy_mpa == 550.0
        assert beam.section.cover_mm == 50.0

    def test_column_frame_type(self, sample_column_geometry: FrameGeometry) -> None:
        """Test column frame type mapping."""
        column = to_beam_geometry(sample_column_geometry)
        assert column.frame_type == FrameType.COLUMN


# =============================================================================
# Unit Tests: to_beam_forces
# =============================================================================


class TestToBeamForces:
    """Tests for to_beam_forces conversion function."""

    def test_basic_conversion(self, sample_envelope: ETABSEnvelopeResult) -> None:
        """Test basic dataclass to Pydantic conversion."""
        forces = to_beam_forces(sample_envelope)

        assert isinstance(forces, BeamForces)
        assert forces.load_case == "1.5(DL+LL)"
        assert forces.mu_knm == 150.0
        assert forces.vu_kn == 100.0

    def test_id_format(self, sample_envelope: ETABSEnvelopeResult) -> None:
        """Test that ID is formatted as beam_id_story."""
        forces = to_beam_forces(sample_envelope)
        assert forces.id == "B1_Ground"

    def test_station_count_preserved(
        self, sample_envelope: ETABSEnvelopeResult
    ) -> None:
        """Test that station count is preserved."""
        forces = to_beam_forces(sample_envelope)
        assert forces.station_count == 5

    def test_axial_default_zero(self, sample_envelope: ETABSEnvelopeResult) -> None:
        """Test that axial force defaults to zero."""
        forces = to_beam_forces(sample_envelope)
        assert forces.pu_kn == 0.0


# =============================================================================
# Unit Tests: Batch Conversion
# =============================================================================


class TestBatchConversion:
    """Tests for batch conversion functions."""

    def test_frames_to_beam_geometries_empty(self) -> None:
        """Test with empty list."""
        result = frames_to_beam_geometries([])
        assert result == []

    def test_frames_to_beam_geometries_beam_only(
        self,
        sample_frame_geometry: FrameGeometry,
        sample_column_geometry: FrameGeometry,
    ) -> None:
        """Test beam_only filter."""
        frames = [sample_frame_geometry, sample_column_geometry]

        # beam_only=True (default)
        beams = frames_to_beam_geometries(frames, beam_only=True)
        assert len(beams) == 1
        assert beams[0].label == "B1"

        # beam_only=False
        all_frames = frames_to_beam_geometries(frames, beam_only=False)
        assert len(all_frames) == 2

    def test_frames_to_beam_geometries_section_map(
        self, sample_frame_geometry: FrameGeometry
    ) -> None:
        """Test section property lookup from section_map."""
        section_map = {
            "B300x500": {"width_mm": 300.0, "depth_mm": 500.0, "fck_mpa": 30.0},
        }

        beams = frames_to_beam_geometries([sample_frame_geometry], section_map)
        assert len(beams) == 1
        assert beams[0].section.width_mm == 300.0
        assert beams[0].section.depth_mm == 500.0
        assert beams[0].section.fck_mpa == 30.0

    def test_envelopes_to_beam_forces_empty(self) -> None:
        """Test with empty list."""
        result = envelopes_to_beam_forces([])
        assert result == []

    def test_envelopes_to_beam_forces_multiple(
        self, sample_envelope: ETABSEnvelopeResult
    ) -> None:
        """Test conversion of multiple envelopes."""
        envelopes = [sample_envelope, sample_envelope]
        forces = envelopes_to_beam_forces(envelopes)
        assert len(forces) == 2


# =============================================================================
# Integration Tests: Real ETABS Data
# =============================================================================


class TestRealETABSData:
    """Integration tests with real ETABS export data."""

    def test_load_and_convert_frames(self, real_etabs_data_dir: Path | None) -> None:
        """Test loading and converting real frame geometry."""
        if real_etabs_data_dir is None:
            pytest.skip("Real ETABS data not available")

        frames_file = real_etabs_data_dir / "frames_geometry.csv"
        frames = load_frames_geometry(frames_file)
        beams = frames_to_beam_geometries(frames, beam_only=True)

        assert len(beams) > 0, "Should convert at least one beam"

        # Verify all beams have valid properties
        for beam in beams:
            assert beam.length_m > 0.1, f"Beam {beam.id} has invalid length"
            assert beam.section.width_mm > 0
            assert beam.section.depth_mm > 0

    def test_load_and_convert_forces(self, real_etabs_data_dir: Path | None) -> None:
        """Test loading and converting real force data.

        Note: The VBA export format uses pre-normalized envelope data
        with columns like Mu_max_kNm instead of raw ETABS station data.
        This test uses the new adapter from adapters.py which handles
        the VBA export format.
        """
        if real_etabs_data_dir is None:
            pytest.skip("Real ETABS data not available")

        # The VBA export file has different column names than raw ETABS
        # Use the ETABSAdapter from adapters.py which handles this format
        from structural_lib.adapters import ETABSAdapter

        adapter = ETABSAdapter()
        forces_file = real_etabs_data_dir / "beam_forces.csv"

        # Load using the adapter which handles VBA export format
        forces = adapter.load_forces(forces_file)

        assert len(forces) > 0, "Should convert at least one force record"

        # Verify all forces have valid properties
        for force in forces:
            assert force.mu_knm >= 0, f"Force {force.id} has negative moment"
            assert force.vu_kn >= 0, f"Force {force.id} has negative shear"
            assert force.station_count >= 1

    def test_round_trip_serialization(self, real_etabs_data_dir: Path | None) -> None:
        """Test that converted models can serialize/deserialize."""
        if real_etabs_data_dir is None:
            pytest.skip("Real ETABS data not available")

        frames_file = real_etabs_data_dir / "frames_geometry.csv"
        frames = load_frames_geometry(frames_file)
        beams = frames_to_beam_geometries(frames[:3], beam_only=True)

        if not beams:
            pytest.skip("No beams in test data")

        # Serialize and deserialize
        for beam in beams:
            json_str = beam.model_dump_json()
            restored = BeamGeometry.model_validate_json(json_str)
            assert restored.id == beam.id
            assert restored.length_m == beam.length_m
