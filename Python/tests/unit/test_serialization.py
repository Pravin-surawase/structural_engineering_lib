# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for JSON serialization utilities."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from structural_lib.core.models import (
    BeamBatchInput,
    BeamBatchResult,
    BeamDesignResult,
    BeamForces,
    BeamGeometry,
    DesignDefaults,
    DesignStatus,
    Point3D,
    SectionProperties,
)
from structural_lib.services.serialization import (
    cache_exists,
    generate_all_schemas,
    generate_schema,
    get_cache_metadata,
    load_batch_input,
    load_batch_result,
    load_forces,
    load_geometry,
    save_batch_input,
    save_batch_result,
    save_forces,
    save_geometry,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_section() -> SectionProperties:
    """Create sample section properties."""
    return SectionProperties(
        width_mm=300,
        depth_mm=500,
        fck_mpa=25,
        fy_mpa=500,
        cover_mm=40,
    )


@pytest.fixture
def sample_beam(sample_section: SectionProperties) -> BeamGeometry:
    """Create sample beam geometry."""
    return BeamGeometry(
        id="B1_Ground",
        label="B1",
        story="Ground",
        point1=Point3D(x=0, y=0, z=0),
        point2=Point3D(x=5, y=0, z=0),
        section=sample_section,
    )


@pytest.fixture
def sample_beams(sample_section: SectionProperties) -> list[BeamGeometry]:
    """Create multiple sample beams."""
    return [
        BeamGeometry(
            id="B1_Ground",
            label="B1",
            story="Ground",
            point1=Point3D(x=0, y=0, z=0),
            point2=Point3D(x=5, y=0, z=0),
            section=sample_section,
        ),
        BeamGeometry(
            id="B2_Ground",
            label="B2",
            story="Ground",
            point1=Point3D(x=5, y=0, z=0),
            point2=Point3D(x=10, y=0, z=0),
            section=sample_section,
        ),
        BeamGeometry(
            id="B3_First",
            label="B3",
            story="First",
            point1=Point3D(x=0, y=0, z=3),
            point2=Point3D(x=5, y=0, z=3),
            section=sample_section,
        ),
    ]


@pytest.fixture
def sample_forces() -> list[BeamForces]:
    """Create sample beam forces."""
    return [
        BeamForces(
            id="B1_Ground",
            load_case="1.2DL+1.5LL",
            mu_knm=150,
            vu_kn=100,
            pu_kn=10,
        ),
        BeamForces(
            id="B2_Ground",
            load_case="1.2DL+1.5LL",
            mu_knm=200,
            vu_kn=120,
            pu_kn=5,
        ),
    ]


@pytest.fixture
def sample_batch_input(
    sample_beams: list[BeamGeometry],
    sample_forces: list[BeamForces],
) -> BeamBatchInput:
    """Create sample batch input."""
    return BeamBatchInput(
        beams=sample_beams,
        forces=sample_forces[:2],  # Match first 2 beams
        defaults=DesignDefaults(),
    )


@pytest.fixture
def sample_batch_result() -> BeamBatchResult:
    """Create sample batch result."""
    results = [
        BeamDesignResult(
            id="B1_Ground",
            load_case="1.2DL+1.5LL",
            status=DesignStatus.PASS,
            mu_knm=150,
            vu_kn=100,
            ast_mm2=1200,
            asv_mm2_m=300,
            utilization=0.75,
        ),
        BeamDesignResult(
            id="B2_Ground",
            load_case="1.2DL+1.5LL",
            status=DesignStatus.PASS,
            mu_knm=200,
            vu_kn=120,
            ast_mm2=1500,
            asv_mm2_m=350,
            utilization=0.85,
        ),
    ]
    return BeamBatchResult.from_results(results)


# =============================================================================
# Geometry Serialization Tests
# =============================================================================


class TestSaveGeometry:
    """Test save_geometry function."""

    def test_saves_to_file(self, tmp_path: Path, sample_beams: list[BeamGeometry]):
        """Should create JSON file."""
        filepath = tmp_path / "beams.json"
        save_geometry(sample_beams, filepath)

        assert filepath.exists()

    def test_creates_parent_directories(
        self, tmp_path: Path, sample_beams: list[BeamGeometry]
    ):
        """Should create parent directories if needed."""
        filepath = tmp_path / "nested" / "dir" / "beams.json"
        save_geometry(sample_beams, filepath)

        assert filepath.exists()

    def test_saves_all_beams(self, tmp_path: Path, sample_beams: list[BeamGeometry]):
        """Should save all beam data."""
        filepath = tmp_path / "beams.json"
        save_geometry(sample_beams, filepath)

        with open(filepath) as f:
            data = json.load(f)

        assert len(data["beams"]) == 3

    def test_includes_metadata(self, tmp_path: Path, sample_beams: list[BeamGeometry]):
        """Should include metadata."""
        filepath = tmp_path / "beams.json"
        save_geometry(sample_beams, filepath)

        with open(filepath) as f:
            data = json.load(f)

        assert "metadata" in data
        assert data["metadata"]["model_type"] == "BeamGeometry"
        assert data["metadata"]["count"] == 3
        assert "created_at" in data["metadata"]

    def test_pretty_formatting(self, tmp_path: Path, sample_beams: list[BeamGeometry]):
        """Default should be pretty formatted."""
        filepath = tmp_path / "beams.json"
        save_geometry(sample_beams, filepath)

        content = filepath.read_text()
        assert "\n" in content  # Has newlines
        assert "  " in content  # Has indentation

    def test_compact_formatting(self, tmp_path: Path, sample_beams: list[BeamGeometry]):
        """Should support compact formatting."""
        filepath = tmp_path / "beams.json"
        save_geometry(sample_beams, filepath, pretty=False)

        content = filepath.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 1  # Single line


class TestLoadGeometry:
    """Test load_geometry function."""

    def test_loads_saved_beams(self, tmp_path: Path, sample_beams: list[BeamGeometry]):
        """Should load beams that were saved."""
        filepath = tmp_path / "beams.json"
        save_geometry(sample_beams, filepath)

        loaded = load_geometry(filepath)

        assert len(loaded) == 3

    def test_returns_validated_models(
        self, tmp_path: Path, sample_beams: list[BeamGeometry]
    ):
        """Loaded data should be BeamGeometry models."""
        filepath = tmp_path / "beams.json"
        save_geometry(sample_beams, filepath)

        loaded = load_geometry(filepath)

        assert all(isinstance(b, BeamGeometry) for b in loaded)

    def test_preserves_beam_properties(
        self, tmp_path: Path, sample_beams: list[BeamGeometry]
    ):
        """Should preserve all beam properties."""
        filepath = tmp_path / "beams.json"
        save_geometry(sample_beams, filepath)

        loaded = load_geometry(filepath)

        original = sample_beams[0]
        loaded_beam = next(b for b in loaded if b.id == original.id)

        assert loaded_beam.label == original.label
        assert loaded_beam.story == original.story
        assert loaded_beam.point1 == original.point1
        assert loaded_beam.point2 == original.point2
        assert loaded_beam.section.width_mm == original.section.width_mm

    def test_recomputes_computed_fields(
        self, tmp_path: Path, sample_beams: list[BeamGeometry]
    ):
        """Computed fields should be recomputed on load."""
        filepath = tmp_path / "beams.json"
        save_geometry(sample_beams, filepath)

        loaded = load_geometry(filepath)

        # length_m is computed
        assert loaded[0].length_m == 5.0

    def test_file_not_found(self, tmp_path: Path):
        """Should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            load_geometry(tmp_path / "nonexistent.json")

    def test_wrong_model_type(self, tmp_path: Path, sample_forces: list[BeamForces]):
        """Should raise ValueError for wrong model type."""
        filepath = tmp_path / "forces.json"
        save_forces(sample_forces, filepath)

        with pytest.raises(ValueError, match="Expected BeamGeometry"):
            load_geometry(filepath)


# =============================================================================
# Forces Serialization Tests
# =============================================================================


class TestSaveForces:
    """Test save_forces function."""

    def test_saves_to_file(self, tmp_path: Path, sample_forces: list[BeamForces]):
        """Should create JSON file."""
        filepath = tmp_path / "forces.json"
        save_forces(sample_forces, filepath)

        assert filepath.exists()

    def test_includes_metadata(self, tmp_path: Path, sample_forces: list[BeamForces]):
        """Should include metadata."""
        filepath = tmp_path / "forces.json"
        save_forces(sample_forces, filepath)

        with open(filepath) as f:
            data = json.load(f)

        assert data["metadata"]["model_type"] == "BeamForces"


class TestLoadForces:
    """Test load_forces function."""

    def test_loads_saved_forces(self, tmp_path: Path, sample_forces: list[BeamForces]):
        """Should load forces that were saved."""
        filepath = tmp_path / "forces.json"
        save_forces(sample_forces, filepath)

        loaded = load_forces(filepath)

        assert len(loaded) == 2

    def test_preserves_force_values(
        self, tmp_path: Path, sample_forces: list[BeamForces]
    ):
        """Should preserve force values."""
        filepath = tmp_path / "forces.json"
        save_forces(sample_forces, filepath)

        loaded = load_forces(filepath)

        original = sample_forces[0]
        loaded_force = next(f for f in loaded if f.id == original.id)

        assert loaded_force.mu_knm == original.mu_knm
        assert loaded_force.vu_kn == original.vu_kn
        assert loaded_force.load_case == original.load_case


# =============================================================================
# Batch Serialization Tests
# =============================================================================


class TestSaveBatchInput:
    """Test save_batch_input function."""

    def test_saves_to_file(self, tmp_path: Path, sample_batch_input: BeamBatchInput):
        """Should create JSON file."""
        filepath = tmp_path / "batch_input.json"
        save_batch_input(sample_batch_input, filepath)

        assert filepath.exists()

    def test_includes_all_data(
        self, tmp_path: Path, sample_batch_input: BeamBatchInput
    ):
        """Should include beams, forces, and defaults."""
        filepath = tmp_path / "batch_input.json"
        save_batch_input(sample_batch_input, filepath)

        with open(filepath) as f:
            data = json.load(f)

        batch = data["batch"]
        assert "beams" in batch
        assert "forces" in batch
        assert "defaults" in batch


class TestLoadBatchInput:
    """Test load_batch_input function."""

    def test_loads_saved_batch(
        self, tmp_path: Path, sample_batch_input: BeamBatchInput
    ):
        """Should load batch input that was saved."""
        filepath = tmp_path / "batch_input.json"
        save_batch_input(sample_batch_input, filepath)

        loaded = load_batch_input(filepath)

        assert isinstance(loaded, BeamBatchInput)
        assert len(loaded.beams) == 3
        assert len(loaded.forces) == 2


class TestSaveBatchResult:
    """Test save_batch_result function."""

    def test_saves_to_file(self, tmp_path: Path, sample_batch_result: BeamBatchResult):
        """Should create JSON file."""
        filepath = tmp_path / "batch_result.json"
        save_batch_result(sample_batch_result, filepath)

        assert filepath.exists()


class TestLoadBatchResult:
    """Test load_batch_result function."""

    def test_loads_saved_result(
        self, tmp_path: Path, sample_batch_result: BeamBatchResult
    ):
        """Should load batch result that was saved."""
        filepath = tmp_path / "batch_result.json"
        save_batch_result(sample_batch_result, filepath)

        loaded = load_batch_result(filepath)

        assert isinstance(loaded, BeamBatchResult)
        assert loaded.total_beams == 2
        assert loaded.passed == 2


# =============================================================================
# Schema Generation Tests
# =============================================================================


class TestGenerateSchema:
    """Test generate_schema function."""

    def test_generates_schema(self):
        """Should generate valid JSON Schema."""
        schema = generate_schema(BeamGeometry)

        assert isinstance(schema, dict)
        assert "properties" in schema
        assert "title" in schema

    def test_includes_field_descriptions(self):
        """Schema should include field descriptions."""
        schema = generate_schema(BeamForces)

        props = schema.get("properties", {})
        # mu_knm should have description
        assert "mu_knm" in props


class TestGenerateAllSchemas:
    """Test generate_all_schemas function."""

    def test_creates_schema_files(self, tmp_path: Path):
        """Should create schema files for all models."""
        output_files = generate_all_schemas(tmp_path)

        assert len(output_files) == 6
        for path in output_files.values():
            assert path.exists()

    def test_schema_files_are_valid_json(self, tmp_path: Path):
        """Schema files should be valid JSON."""
        output_files = generate_all_schemas(tmp_path)

        for path in output_files.values():
            with open(path) as f:
                data = json.load(f)  # Should not raise

            assert isinstance(data, dict)


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestCacheExists:
    """Test cache_exists function."""

    def test_returns_true_for_existing(
        self, tmp_path: Path, sample_beams: list[BeamGeometry]
    ):
        """Should return True for existing cache."""
        filepath = tmp_path / "cache.json"
        save_geometry(sample_beams, filepath)

        assert cache_exists(filepath) is True

    def test_returns_false_for_nonexistent(self, tmp_path: Path):
        """Should return False for nonexistent file."""
        assert cache_exists(tmp_path / "nonexistent.json") is False


class TestGetCacheMetadata:
    """Test get_cache_metadata function."""

    def test_returns_metadata_for_existing(
        self, tmp_path: Path, sample_beams: list[BeamGeometry]
    ):
        """Should return metadata for existing cache."""
        filepath = tmp_path / "cache.json"
        save_geometry(sample_beams, filepath)

        metadata = get_cache_metadata(filepath)

        assert metadata is not None
        assert metadata["model_type"] == "BeamGeometry"
        assert metadata["count"] == 3

    def test_returns_none_for_nonexistent(self, tmp_path: Path):
        """Should return None for nonexistent file."""
        metadata = get_cache_metadata(tmp_path / "nonexistent.json")

        assert metadata is None
