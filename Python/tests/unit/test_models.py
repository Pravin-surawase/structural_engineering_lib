# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for canonical data models.

This module tests the Pydantic-based canonical models defined in models.py:
- Point3D: 3D coordinates
- SectionProperties: Beam section properties
- BeamGeometry: Complete beam geometry
- BeamForces: Force envelope values
- BeamDesignResult: Design output
- BeamBatchInput/BeamBatchResult: Batch processing

Task: TASK-DATA-001
Author: Session 40 Agent
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from structural_lib.models import (
    BeamBatchInput,
    BeamBatchResult,
    BeamDesignResult,
    BeamForces,
    BeamGeometry,
    BuildingStatistics,
    DesignDefaults,
    DesignStatus,
    FrameType,
    Point3D,
    SectionProperties,
)

# =============================================================================
# Point3D Tests
# =============================================================================


class TestPoint3D:
    """Tests for Point3D model."""

    def test_create_point_valid(self):
        """Test creating a valid point."""
        point = Point3D(x=1.0, y=2.0, z=3.0)
        assert point.x == 1.0
        assert point.y == 2.0
        assert point.z == 3.0

    def test_point_is_frozen(self):
        """Test that point is immutable."""
        point = Point3D(x=1.0, y=2.0, z=3.0)
        with pytest.raises(ValidationError):
            point.x = 5.0  # type: ignore

    def test_distance_to_same_point(self):
        """Test distance to same point is zero."""
        point = Point3D(x=1.0, y=2.0, z=3.0)
        assert point.distance_to(point) == 0.0

    def test_distance_to_other_point(self):
        """Test distance calculation."""
        p1 = Point3D(x=0.0, y=0.0, z=0.0)
        p2 = Point3D(x=3.0, y=4.0, z=0.0)
        assert p1.distance_to(p2) == 5.0  # 3-4-5 triangle

    def test_distance_3d(self):
        """Test 3D distance calculation."""
        p1 = Point3D(x=0.0, y=0.0, z=0.0)
        p2 = Point3D(x=1.0, y=2.0, z=2.0)
        assert p1.distance_to(p2) == 3.0  # sqrt(1 + 4 + 4) = 3

    def test_point_json_serialization(self):
        """Test JSON serialization."""
        point = Point3D(x=1.5, y=2.5, z=3.5)
        json_str = point.model_dump_json()
        data = json.loads(json_str)
        assert data == {"x": 1.5, "y": 2.5, "z": 3.5}

    def test_point_from_dict(self):
        """Test creating point from dictionary."""
        point = Point3D.model_validate({"x": 1.0, "y": 2.0, "z": 3.0})
        assert point.x == 1.0

    def test_point_extra_fields_forbidden(self):
        """Test that extra fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Point3D(x=1.0, y=2.0, z=3.0, extra=5.0)  # type: ignore
        assert "extra" in str(exc_info.value)


# =============================================================================
# SectionProperties Tests
# =============================================================================


class TestSectionProperties:
    """Tests for SectionProperties model."""

    def test_create_section_valid(self):
        """Test creating a valid section."""
        section = SectionProperties(width_mm=300, depth_mm=500)
        assert section.width_mm == 300
        assert section.depth_mm == 500
        assert section.fck_mpa == 25.0  # Default
        assert section.fy_mpa == 500.0  # Default
        assert section.cover_mm == 40.0  # Default

    def test_section_effective_depth(self):
        """Test effective depth calculation."""
        section = SectionProperties(width_mm=300, depth_mm=500, cover_mm=40)
        # d = D - cover - bar_dia/2 = 500 - 40 - 12.5 = 447.5
        assert section.effective_depth_mm == 447.5

    def test_section_width_must_be_positive(self):
        """Test that width must be positive."""
        with pytest.raises(ValidationError) as exc_info:
            SectionProperties(width_mm=0, depth_mm=500)
        assert "width_mm" in str(exc_info.value)

    def test_section_width_negative_rejected(self):
        """Test that negative width is rejected."""
        with pytest.raises(ValidationError):
            SectionProperties(width_mm=-100, depth_mm=500)

    def test_section_depth_upper_limit(self):
        """Test depth upper limit."""
        with pytest.raises(ValidationError):
            SectionProperties(width_mm=300, depth_mm=5000)  # > 3000 limit

    def test_section_with_custom_materials(self):
        """Test section with custom material properties."""
        section = SectionProperties(
            width_mm=350,
            depth_mm=600,
            fck_mpa=40,
            fy_mpa=415,
            cover_mm=50,
        )
        assert section.fck_mpa == 40
        assert section.fy_mpa == 415

    def test_section_json_roundtrip(self):
        """Test JSON serialization roundtrip."""
        section = SectionProperties(width_mm=300, depth_mm=500, fck_mpa=30)
        # Exclude computed fields for roundtrip
        data = section.model_dump(exclude={"effective_depth_mm"})
        restored = SectionProperties.model_validate(data)
        assert restored == section


# =============================================================================
# BeamGeometry Tests
# =============================================================================


class TestBeamGeometry:
    """Tests for BeamGeometry model."""

    @pytest.fixture
    def sample_beam(self) -> BeamGeometry:
        """Create a sample beam for testing."""
        return BeamGeometry(
            id="B1_Ground",
            label="B1",
            story="Ground",
            point1=Point3D(x=0, y=0, z=0),
            point2=Point3D(x=5, y=0, z=0),
            section=SectionProperties(width_mm=300, depth_mm=500),
        )

    def test_create_beam_valid(self, sample_beam: BeamGeometry):
        """Test creating a valid beam."""
        assert sample_beam.id == "B1_Ground"
        assert sample_beam.label == "B1"
        assert sample_beam.story == "Ground"
        assert sample_beam.frame_type == FrameType.BEAM  # Default

    def test_beam_length_calculation(self, sample_beam: BeamGeometry):
        """Test beam length calculation."""
        assert sample_beam.length_m == 5.0

    def test_beam_is_horizontal(self, sample_beam: BeamGeometry):
        """Test horizontal beam detection."""
        assert sample_beam.is_vertical is False

    def test_beam_is_vertical(self):
        """Test vertical beam (column) detection."""
        column = BeamGeometry(
            id="C1",
            label="C1",
            story="Ground",
            frame_type=FrameType.COLUMN,
            point1=Point3D(x=0, y=0, z=0),
            point2=Point3D(x=0, y=0, z=3),  # 3m height, no horizontal movement
            section=SectionProperties(width_mm=400, depth_mm=400),
        )
        assert column.is_vertical is True

    def test_beam_minimum_length_validation(self):
        """Test that beam must have minimum length."""
        with pytest.raises(ValidationError) as exc_info:
            BeamGeometry(
                id="B1",
                label="B1",
                story="Ground",
                point1=Point3D(x=0, y=0, z=0),
                point2=Point3D(x=0.05, y=0, z=0),  # 50mm < 100mm minimum
                section=SectionProperties(width_mm=300, depth_mm=500),
            )
        assert "length" in str(exc_info.value).lower()

    def test_beam_with_source_id(self):
        """Test beam with source system ID."""
        beam = BeamGeometry(
            id="B1",
            label="B1",
            story="Ground",
            point1=Point3D(x=0, y=0, z=0),
            point2=Point3D(x=5, y=0, z=0),
            section=SectionProperties(width_mm=300, depth_mm=500),
            source_id="ETABS_12345",
        )
        assert beam.source_id == "ETABS_12345"

    def test_beam_json_roundtrip(self, sample_beam: BeamGeometry):
        """Test JSON serialization roundtrip."""
        # Exclude computed fields for roundtrip (they're recalculated on load)
        exclude_fields = {
            "length_m": True,
            "is_vertical": True,
            "section": {"effective_depth_mm"},
        }
        data = sample_beam.model_dump(exclude=exclude_fields)
        restored = BeamGeometry.model_validate(data)
        assert restored.id == sample_beam.id
        assert restored.length_m == sample_beam.length_m

    def test_beam_json_schema_generation(self):
        """Test JSON Schema generation for documentation."""
        schema = BeamGeometry.model_json_schema()
        assert "properties" in schema
        assert "id" in schema["properties"]
        assert "point1" in schema["properties"]


# =============================================================================
# BeamForces Tests
# =============================================================================


class TestBeamForces:
    """Tests for BeamForces model."""

    def test_create_forces_valid(self):
        """Test creating valid force data."""
        forces = BeamForces(
            id="B1",
            load_case="1.5(DL+LL)",
            mu_knm=150.0,
            vu_kn=80.0,
        )
        assert forces.id == "B1"
        assert forces.mu_knm == 150.0
        assert forces.vu_kn == 80.0
        assert forces.pu_kn == 0.0  # Default
        assert forces.station_count == 1  # Default

    def test_forces_moment_must_be_non_negative(self):
        """Test that moment must be non-negative (absolute value)."""
        with pytest.raises(ValidationError):
            BeamForces(
                id="B1",
                load_case="1.5(DL+LL)",
                mu_knm=-150.0,  # Negative not allowed
                vu_kn=80.0,
            )

    def test_forces_with_axial(self):
        """Test forces with axial load."""
        forces = BeamForces(
            id="B1",
            load_case="1.5(DL+LL)",
            mu_knm=150.0,
            vu_kn=80.0,
            pu_kn=50.0,
        )
        assert forces.pu_kn == 50.0

    def test_forces_json_serialization(self):
        """Test JSON serialization."""
        forces = BeamForces(
            id="B1",
            load_case="1.5DL+1.5LL",
            mu_knm=100.0,
            vu_kn=50.0,
        )
        data = forces.model_dump()
        assert data["id"] == "B1"
        assert data["load_case"] == "1.5DL+1.5LL"


# =============================================================================
# BeamDesignResult Tests
# =============================================================================


class TestBeamDesignResult:
    """Tests for BeamDesignResult model."""

    @pytest.fixture
    def sample_result(self) -> BeamDesignResult:
        """Create a sample design result."""
        return BeamDesignResult(
            id="B1",
            load_case="1.5(DL+LL)",
            mu_knm=150.0,
            vu_kn=80.0,
            ast_mm2=942.0,
            asv_mm2_m=200.0,
            status=DesignStatus.PASS,
            utilization=0.75,
        )

    def test_create_result_valid(self, sample_result: BeamDesignResult):
        """Test creating a valid result."""
        assert sample_result.id == "B1"
        assert sample_result.status == DesignStatus.PASS
        assert sample_result.is_acceptable is True

    def test_result_is_acceptable_pass(self, sample_result: BeamDesignResult):
        """Test is_acceptable for PASS status."""
        assert sample_result.is_acceptable is True

    def test_result_is_acceptable_warning(self):
        """Test is_acceptable for WARNING status."""
        result = BeamDesignResult(
            id="B1",
            load_case="1.5(DL+LL)",
            mu_knm=150.0,
            vu_kn=80.0,
            ast_mm2=942.0,
            asv_mm2_m=200.0,
            status=DesignStatus.WARNING,
            utilization=0.95,
            messages=["High utilization ratio"],
        )
        assert result.is_acceptable is True

    def test_result_is_not_acceptable_fail(self):
        """Test is_acceptable for FAIL status."""
        result = BeamDesignResult(
            id="B1",
            load_case="1.5(DL+LL)",
            mu_knm=300.0,
            vu_kn=150.0,
            ast_mm2=0.0,
            asv_mm2_m=0.0,
            status=DesignStatus.FAIL,
            utilization=1.5,
            messages=["Section capacity exceeded"],
        )
        assert result.is_acceptable is False

    def test_result_with_capacity_values(self):
        """Test result with capacity values."""
        result = BeamDesignResult(
            id="B1",
            load_case="1.5(DL+LL)",
            mu_knm=150.0,
            vu_kn=80.0,
            ast_mm2=942.0,
            asv_mm2_m=200.0,
            status=DesignStatus.PASS,
            utilization=0.75,
            moment_capacity_knm=200.0,
            shear_capacity_kn=120.0,
        )
        assert result.moment_capacity_knm == 200.0
        assert result.shear_capacity_kn == 120.0


# =============================================================================
# Batch Processing Tests
# =============================================================================


class TestDesignDefaults:
    """Tests for DesignDefaults model."""

    def test_create_defaults(self):
        """Test creating defaults with default values."""
        defaults = DesignDefaults()
        assert defaults.fck_mpa == 25.0
        assert defaults.fy_mpa == 500.0
        assert defaults.cover_mm == 40.0

    def test_create_custom_defaults(self):
        """Test creating custom defaults."""
        defaults = DesignDefaults(fck_mpa=30, fy_mpa=415)
        assert defaults.fck_mpa == 30
        assert defaults.fy_mpa == 415

    def test_rejects_unknown_fields(self):
        """Test that DesignDefaults rejects unknown fields.

        This is critical because DesignDefaults uses `extra="forbid"`.
        Section dimensions (width_mm, depth_mm) belong in SectionProperties,
        not DesignDefaults.

        See Session 46: Bug where width_mm/depth_mm were incorrectly
        passed to DesignDefaults in Streamlit page 07.
        """
        with pytest.raises(ValidationError) as exc_info:
            DesignDefaults(
                fck_mpa=25,
                fy_mpa=500,
                width_mm=300,  # Invalid - not allowed in DesignDefaults
                depth_mm=500,  # Invalid - not allowed in DesignDefaults
            )

        # Verify the error mentions the extra fields
        errors = exc_info.value.errors()
        extra_fields = {e.get("loc", (None,))[0] for e in errors}
        assert "width_mm" in extra_fields
        assert "depth_mm" in extra_fields


class TestBeamBatchInput:
    """Tests for BeamBatchInput model."""

    @pytest.fixture
    def sample_beams(self) -> list[BeamGeometry]:
        """Create sample beams."""
        return [
            BeamGeometry(
                id="B1",
                label="B1",
                story="Ground",
                point1=Point3D(x=0, y=0, z=0),
                point2=Point3D(x=5, y=0, z=0),
                section=SectionProperties(width_mm=300, depth_mm=500),
            ),
            BeamGeometry(
                id="B2",
                label="B2",
                story="Ground",
                point1=Point3D(x=5, y=0, z=0),
                point2=Point3D(x=10, y=0, z=0),
                section=SectionProperties(width_mm=300, depth_mm=500),
            ),
        ]

    @pytest.fixture
    def sample_forces(self) -> list[BeamForces]:
        """Create sample forces."""
        return [
            BeamForces(id="B1", load_case="LC1", mu_knm=100.0, vu_kn=50.0),
            BeamForces(id="B2", load_case="LC1", mu_knm=120.0, vu_kn=60.0),
        ]

    def test_create_batch_input(
        self,
        sample_beams: list[BeamGeometry],
        sample_forces: list[BeamForces],
    ):
        """Test creating batch input."""
        batch = BeamBatchInput(beams=sample_beams, forces=sample_forces)
        assert len(batch.beams) == 2
        assert len(batch.forces) == 2

    def test_get_merged_data(
        self,
        sample_beams: list[BeamGeometry],
        sample_forces: list[BeamForces],
    ):
        """Test merging geometry and forces."""
        batch = BeamBatchInput(beams=sample_beams, forces=sample_forces)
        merged = batch.get_merged_data()
        assert len(merged) == 2
        assert merged[0][0].id == "B1"
        assert merged[0][1].mu_knm == 100.0

    def test_get_unmatched_beams(
        self,
        sample_beams: list[BeamGeometry],
    ):
        """Test finding beams without forces."""
        forces = [BeamForces(id="B1", load_case="LC1", mu_knm=100.0, vu_kn=50.0)]
        batch = BeamBatchInput(beams=sample_beams, forces=forces)
        unmatched = batch.get_unmatched_beams()
        assert unmatched == ["B2"]

    def test_batch_requires_at_least_one_beam(self):
        """Test that batch requires at least one beam."""
        with pytest.raises(ValidationError):
            BeamBatchInput(
                beams=[],  # Empty list
                forces=[BeamForces(id="B1", load_case="LC1", mu_knm=100.0, vu_kn=50.0)],
            )


class TestBeamBatchResult:
    """Tests for BeamBatchResult model."""

    def test_create_from_results(self):
        """Test creating batch result from individual results."""
        results = [
            BeamDesignResult(
                id="B1",
                load_case="LC1",
                mu_knm=100.0,
                vu_kn=50.0,
                ast_mm2=500.0,
                asv_mm2_m=100.0,
                status=DesignStatus.PASS,
                utilization=0.7,
            ),
            BeamDesignResult(
                id="B2",
                load_case="LC1",
                mu_knm=150.0,
                vu_kn=80.0,
                ast_mm2=800.0,
                asv_mm2_m=150.0,
                status=DesignStatus.WARNING,
                utilization=0.9,
            ),
            BeamDesignResult(
                id="B3",
                load_case="LC1",
                mu_knm=300.0,
                vu_kn=150.0,
                ast_mm2=0.0,
                asv_mm2_m=0.0,
                status=DesignStatus.FAIL,
                utilization=1.5,
            ),
        ]
        batch_result = BeamBatchResult.from_results(results)

        assert batch_result.total_beams == 3
        assert batch_result.passed == 1
        assert batch_result.warnings == 1
        assert batch_result.failed == 1

    def test_pass_rate_calculation(self):
        """Test pass rate calculation."""
        batch_result = BeamBatchResult(
            total_beams=10,
            passed=7,
            warnings=2,
            failed=1,
        )
        assert batch_result.pass_rate == 70.0

    def test_pass_rate_zero_beams(self):
        """Test pass rate with zero beams."""
        batch_result = BeamBatchResult()
        assert batch_result.pass_rate == 0.0


# =============================================================================
# JSON Schema Tests
# =============================================================================


class TestJSONSchemaGeneration:
    """Tests for JSON Schema generation."""

    def test_beam_geometry_schema(self):
        """Test BeamGeometry JSON Schema generation."""
        schema = BeamGeometry.model_json_schema()
        assert schema["type"] == "object"
        assert "id" in schema["properties"]
        assert "point1" in schema["properties"]
        # Check that description is included
        assert "description" in schema["properties"]["id"]

    def test_beam_batch_input_schema(self):
        """Test BeamBatchInput JSON Schema generation."""
        schema = BeamBatchInput.model_json_schema()
        assert "beams" in schema["properties"]
        assert "forces" in schema["properties"]

    def test_full_schema_export(self):
        """Test that full schema can be exported to JSON."""
        schema = BeamBatchInput.model_json_schema()
        json_str = json.dumps(schema, indent=2)
        assert len(json_str) > 100  # Reasonable schema size
        # Schema should be valid JSON
        parsed = json.loads(json_str)
        assert "properties" in parsed


# =============================================================================
# BuildingStatistics Tests
# =============================================================================


class TestBuildingStatistics:
    """Tests for BuildingStatistics utility model."""

    def test_empty_beams_list(self):
        """Test statistics for empty beam list."""
        stats = BuildingStatistics.from_beams([])
        assert stats.total_beams == 0
        assert stats.total_stories == 0
        assert stats.stories == []
        assert stats.beams_per_story == {}
        assert stats.total_length_m == 0.0
        assert stats.total_concrete_m3 == 0.0

    def test_single_beam_statistics(self):
        """Test statistics for single beam."""
        beam = BeamGeometry(
            id="B1_Story1",
            label="B1",
            story="Story1",
            point1=Point3D(x=0, y=0, z=3),
            point2=Point3D(x=5, y=0, z=3),
            section=SectionProperties(width_mm=300, depth_mm=500),
        )
        stats = BuildingStatistics.from_beams([beam])

        assert stats.total_beams == 1
        assert stats.total_stories == 1
        assert stats.stories == ["Story1"]
        assert stats.beams_per_story == {"Story1": 1}
        assert stats.total_length_m == 5.0
        # Volume: 5m × 0.3m × 0.5m = 0.75 m³
        assert stats.total_concrete_m3 == 0.75
        assert stats.bounding_box["x"] == (0, 5)
        assert stats.bounding_box["z"] == (3, 3)

    def test_multi_story_statistics(self):
        """Test statistics for multi-story building."""
        beams = [
            BeamGeometry(
                id="B1_Story1",
                label="B1",
                story="Story1",
                point1=Point3D(x=0, y=0, z=3),
                point2=Point3D(x=4, y=0, z=3),
                section=SectionProperties(width_mm=300, depth_mm=450),
            ),
            BeamGeometry(
                id="B2_Story1",
                label="B2",
                story="Story1",
                point1=Point3D(x=0, y=5, z=3),
                point2=Point3D(x=4, y=5, z=3),
                section=SectionProperties(width_mm=300, depth_mm=450),
            ),
            BeamGeometry(
                id="B1_Story2",
                label="B1",
                story="Story2",
                point1=Point3D(x=0, y=0, z=6),
                point2=Point3D(x=4, y=0, z=6),
                section=SectionProperties(width_mm=300, depth_mm=450),
            ),
        ]
        stats = BuildingStatistics.from_beams(beams)

        assert stats.total_beams == 3
        assert stats.total_stories == 2
        assert "Story1" in stats.stories
        assert "Story2" in stats.stories
        assert stats.beams_per_story["Story1"] == 2
        assert stats.beams_per_story["Story2"] == 1
        assert stats.total_length_m == 12.0  # 3 beams × 4m
        assert stats.bounding_box["y"] == (0, 5)
        assert stats.bounding_box["z"] == (3, 6)

    def test_statistics_is_immutable(self):
        """Test that BuildingStatistics is frozen/immutable."""
        stats = BuildingStatistics.from_beams([])
        with pytest.raises(ValidationError):
            stats.total_beams = 10  # Should fail - frozen model
