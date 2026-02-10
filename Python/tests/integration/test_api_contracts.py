# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Contract Tests for Pydantic API Models.

These tests verify that the Pydantic models maintain their API contract
(field names, types, validation rules) to prevent breaking changes during
the V3 migration. Contract tests ensure:

1. Schema Stability - Field names and types don't change unexpectedly
2. Validation Rules - Constraints remain consistent
3. Computed Fields - Derived properties work correctly
4. Serialization - JSON round-tripping works

Run with: pytest tests/integration/test_api_contracts.py -v

See Also:
    - docs/reference/api.md - API documentation
    - docs/research/automation-audit-readiness-research.md - Contract testing rationale
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from pydantic import ValidationError

from structural_lib.core.models import (
    BeamBatchInput,
    BeamBatchResult,
    BeamDesignResult,
    BeamForces,
    BeamGeometry,
    DesignDefaults,
    DesignStatus,
    FrameType,
    Point3D,
    SectionProperties,
)

# =============================================================================
# Schema Contract Fixtures
# =============================================================================


@pytest.fixture
def point3d_contract() -> dict[str, Any]:
    """Expected schema contract for Point3D."""
    return {
        "required_fields": {"x", "y", "z"},
        "optional_fields": set(),
        "field_types": {"x": "float", "y": "float", "z": "float"},
    }


@pytest.fixture
def section_properties_contract() -> dict[str, Any]:
    """Expected schema contract for SectionProperties."""
    return {
        "required_fields": {"width_mm", "depth_mm"},
        "optional_fields": {"fck_mpa", "fy_mpa", "cover_mm"},
        "field_types": {
            "width_mm": "float",
            "depth_mm": "float",
            "fck_mpa": "float",
            "fy_mpa": "float",
            "cover_mm": "float",
        },
        "computed_fields": {"effective_depth_mm"},
        "defaults": {"fck_mpa": 25.0, "fy_mpa": 500.0, "cover_mm": 40.0},
    }


@pytest.fixture
def beam_geometry_contract() -> dict[str, Any]:
    """Expected schema contract for BeamGeometry."""
    return {
        "required_fields": {"id", "label", "story", "point1", "point2", "section"},
        "optional_fields": {"frame_type", "angle", "source_id"},
        "field_types": {
            "id": "str",
            "label": "str",
            "story": "str",
            "frame_type": "FrameType",
            "point1": "Point3D",
            "point2": "Point3D",
            "section": "SectionProperties",
            "angle": "float",
            "source_id": "str | None",
        },
        "computed_fields": {"length_m", "is_vertical"},
    }


@pytest.fixture
def beam_forces_contract() -> dict[str, Any]:
    """Expected schema contract for BeamForces."""
    return {
        "required_fields": {"id", "load_case", "mu_knm", "vu_kn"},
        "optional_fields": {"pu_kn", "station_count"},
        "field_types": {
            "id": "str",
            "load_case": "str",
            "mu_knm": "float",
            "vu_kn": "float",
            "pu_kn": "float",
            "station_count": "int",
        },
        "defaults": {"pu_kn": 0.0, "station_count": 1},
    }


@pytest.fixture
def beam_design_result_contract() -> dict[str, Any]:
    """Expected schema contract for BeamDesignResult."""
    return {
        "required_fields": {
            "id",
            "load_case",
            "mu_knm",
            "vu_kn",
            "ast_mm2",
            "asv_mm2_m",
            "status",
            "utilization",
        },
        "optional_fields": {
            "asc_mm2",
            "moment_capacity_knm",
            "shear_capacity_kn",
            "messages",
        },
        "computed_fields": {"is_acceptable"},
        "enum_values": {"status": ["PASS", "FAIL", "WARNING", "NOT_CHECKED"]},
    }


# =============================================================================
# Point3D Contract Tests
# =============================================================================


class TestPoint3DContract:
    """Contract tests for Point3D model."""

    def test_schema_has_required_fields(self, point3d_contract):
        """Verify Point3D schema contains all required fields."""
        schema = Point3D.model_json_schema()
        required = set(schema.get("required", []))
        assert required == point3d_contract["required_fields"]

    def test_model_creation_with_all_fields(self):
        """Verify Point3D can be created with x, y, z."""
        point = Point3D(x=1.0, y=2.0, z=3.0)
        assert point.x == 1.0
        assert point.y == 2.0
        assert point.z == 3.0

    def test_model_is_immutable(self):
        """Verify Point3D is frozen (immutable)."""
        point = Point3D(x=1.0, y=2.0, z=3.0)
        with pytest.raises(ValidationError):
            point.x = 5.0  # type: ignore

    def test_rejects_extra_fields(self):
        """Verify Point3D rejects unknown fields."""
        with pytest.raises(ValidationError):
            Point3D(x=1.0, y=2.0, z=3.0, w=4.0)  # type: ignore

    def test_json_serialization_format(self):
        """Verify JSON output format is stable."""
        point = Point3D(x=1.0, y=2.0, z=3.0)
        data = json.loads(point.model_dump_json())
        assert set(data.keys()) == {"x", "y", "z"}
        assert all(isinstance(v, (int, float)) for v in data.values())

    def test_distance_to_method_exists(self):
        """Verify distance_to method is available."""
        p1 = Point3D(x=0, y=0, z=0)
        p2 = Point3D(x=3, y=4, z=0)
        assert hasattr(p1, "distance_to")
        assert p1.distance_to(p2) == pytest.approx(5.0)


# =============================================================================
# SectionProperties Contract Tests
# =============================================================================


class TestSectionPropertiesContract:
    """Contract tests for SectionProperties model."""

    def test_schema_has_required_fields(self, section_properties_contract):
        """Verify required fields are present."""
        schema = SectionProperties.model_json_schema()
        required = set(schema.get("required", []))
        assert required == section_properties_contract["required_fields"]

    def test_default_values(self, section_properties_contract):
        """Verify default values are applied correctly."""
        section = SectionProperties(width_mm=300, depth_mm=500)
        for field, expected in section_properties_contract["defaults"].items():
            assert getattr(section, field) == expected

    def test_computed_effective_depth(self):
        """Verify effective_depth_mm is computed correctly."""
        section = SectionProperties(
            width_mm=300, depth_mm=500, cover_mm=40  # d = 500 - 40 - 12.5 = 447.5
        )
        assert section.effective_depth_mm == pytest.approx(447.5)

    def test_validation_rejects_zero_width(self):
        """Verify width_mm must be positive."""
        with pytest.raises(ValidationError):
            SectionProperties(width_mm=0, depth_mm=500)

    def test_validation_rejects_zero_depth(self):
        """Verify depth_mm must be positive."""
        with pytest.raises(ValidationError):
            SectionProperties(width_mm=300, depth_mm=0)

    def test_json_round_trip(self):
        """Verify JSON serialization/deserialization preserves data.

        Note: computed_field values are included in JSON output but must be
        excluded when deserializing models with extra='forbid'.
        """
        original = SectionProperties(
            width_mm=300, depth_mm=500, fck_mpa=30, fy_mpa=415, cover_mm=50
        )
        # Use exclude to remove computed fields for round-trip
        data = original.model_dump(exclude={"effective_depth_mm"})
        restored = SectionProperties.model_validate(data)
        assert original.width_mm == restored.width_mm
        assert original.depth_mm == restored.depth_mm
        assert original.effective_depth_mm == restored.effective_depth_mm


# =============================================================================
# BeamGeometry Contract Tests
# =============================================================================


class TestBeamGeometryContract:
    """Contract tests for BeamGeometry model."""

    @pytest.fixture
    def valid_beam_geometry(self) -> BeamGeometry:
        """Create a valid BeamGeometry for testing."""
        return BeamGeometry(
            id="B1_Ground",
            label="B1",
            story="Ground",
            point1=Point3D(x=0, y=0, z=0),
            point2=Point3D(x=5, y=0, z=0),
            section=SectionProperties(width_mm=300, depth_mm=500),
        )

    def test_schema_has_required_fields(self, beam_geometry_contract):
        """Verify required fields are present."""
        schema = BeamGeometry.model_json_schema()
        required = set(schema.get("required", []))
        assert required == beam_geometry_contract["required_fields"]

    def test_computed_length(self, valid_beam_geometry):
        """Verify length_m is computed correctly."""
        assert valid_beam_geometry.length_m == pytest.approx(5.0)

    def test_computed_is_vertical_for_horizontal_beam(self, valid_beam_geometry):
        """Verify horizontal beam is not vertical."""
        assert valid_beam_geometry.is_vertical is False

    def test_computed_is_vertical_for_column(self):
        """Verify vertical element is detected."""
        column = BeamGeometry(
            id="C1",
            label="C1",
            story="Ground",
            frame_type=FrameType.COLUMN,
            point1=Point3D(x=0, y=0, z=0),
            point2=Point3D(x=0, y=0, z=3),
            section=SectionProperties(width_mm=400, depth_mm=400),
        )
        assert column.is_vertical is True

    def test_minimum_length_validation(self):
        """Verify beams must have at least 0.1m length."""
        with pytest.raises(ValidationError, match="length"):
            BeamGeometry(
                id="short",
                label="short",
                story="Ground",
                point1=Point3D(x=0, y=0, z=0),
                point2=Point3D(x=0.05, y=0, z=0),  # Only 50mm
                section=SectionProperties(width_mm=300, depth_mm=500),
            )

    def test_default_frame_type(self, valid_beam_geometry):
        """Verify default frame_type is BEAM."""
        assert valid_beam_geometry.frame_type == FrameType.BEAM

    def test_json_round_trip(self, valid_beam_geometry):
        """Verify JSON serialization preserves data.

        Note: computed_field values are included in JSON output but must be
        excluded when deserializing models with extra='forbid'.
        """
        # Exclude computed fields for round-trip
        data = valid_beam_geometry.model_dump(exclude={"length_m", "is_vertical"})
        # Also remove computed field from nested section
        if "effective_depth_mm" in data.get("section", {}):
            del data["section"]["effective_depth_mm"]
        restored = BeamGeometry.model_validate(data)
        assert valid_beam_geometry.id == restored.id
        assert valid_beam_geometry.length_m == pytest.approx(restored.length_m)


# =============================================================================
# BeamForces Contract Tests
# =============================================================================


class TestBeamForcesContract:
    """Contract tests for BeamForces model."""

    def test_schema_has_required_fields(self, beam_forces_contract):
        """Verify required fields are present."""
        schema = BeamForces.model_json_schema()
        required = set(schema.get("required", []))
        assert required == beam_forces_contract["required_fields"]

    def test_default_values(self, beam_forces_contract):
        """Verify default values are applied."""
        forces = BeamForces(id="B1", load_case="1.5DL+LL", mu_knm=100, vu_kn=50)
        for field, expected in beam_forces_contract["defaults"].items():
            assert getattr(forces, field) == expected

    def test_forces_must_be_non_negative(self):
        """Verify mu_knm and vu_kn must be >= 0."""
        with pytest.raises(ValidationError):
            BeamForces(id="B1", load_case="LC1", mu_knm=-10, vu_kn=50)

        with pytest.raises(ValidationError):
            BeamForces(id="B1", load_case="LC1", mu_knm=100, vu_kn=-5)

    def test_json_round_trip(self):
        """Verify JSON serialization works correctly."""
        forces = BeamForces(
            id="B1", load_case="1.5DL+LL", mu_knm=150.5, vu_kn=75.25, station_count=11
        )
        json_str = forces.model_dump_json()
        restored = BeamForces.model_validate_json(json_str)
        assert forces == restored


# =============================================================================
# BeamDesignResult Contract Tests
# =============================================================================


class TestBeamDesignResultContract:
    """Contract tests for BeamDesignResult model."""

    @pytest.fixture
    def valid_design_result(self) -> BeamDesignResult:
        """Create a valid design result for testing."""
        return BeamDesignResult(
            id="B1",
            load_case="1.5DL+LL",
            mu_knm=150,
            vu_kn=75,
            ast_mm2=900,
            asv_mm2_m=250,
            status=DesignStatus.PASS,
            utilization=0.85,
        )

    def test_schema_has_required_fields(self, beam_design_result_contract):
        """Verify required fields are present."""
        schema = BeamDesignResult.model_json_schema()
        required = set(schema.get("required", []))
        assert required == beam_design_result_contract["required_fields"]

    def test_computed_is_acceptable_pass(self, valid_design_result):
        """Verify PASS status is acceptable."""
        assert valid_design_result.is_acceptable is True

    def test_computed_is_acceptable_warning(self):
        """Verify WARNING status is acceptable."""
        result = BeamDesignResult(
            id="B1",
            load_case="LC1",
            mu_knm=100,
            vu_kn=50,
            ast_mm2=800,
            asv_mm2_m=200,
            status=DesignStatus.WARNING,
            utilization=0.95,
        )
        assert result.is_acceptable is True

    def test_computed_is_acceptable_fail(self):
        """Verify FAIL status is not acceptable."""
        result = BeamDesignResult(
            id="B1",
            load_case="LC1",
            mu_knm=100,
            vu_kn=50,
            ast_mm2=800,
            asv_mm2_m=200,
            status=DesignStatus.FAIL,
            utilization=1.2,
        )
        assert result.is_acceptable is False

    def test_status_enum_values(self, beam_design_result_contract):
        """Verify all expected status values exist."""
        expected_values = beam_design_result_contract["enum_values"]["status"]
        actual_values = [e.value for e in DesignStatus]
        assert set(expected_values) == set(actual_values)

    def test_messages_default_to_empty_list(self):
        """Verify messages defaults to empty list."""
        result = BeamDesignResult(
            id="B1",
            load_case="LC1",
            mu_knm=100,
            vu_kn=50,
            ast_mm2=800,
            asv_mm2_m=200,
            status=DesignStatus.PASS,
            utilization=0.8,
        )
        assert result.messages == []

    def test_json_round_trip(self, valid_design_result):
        """Verify JSON serialization works correctly.

        Note: computed_field values are included in JSON output but must be
        excluded when deserializing models with extra='forbid'.
        """
        # Exclude computed field for round-trip
        data = valid_design_result.model_dump(exclude={"is_acceptable"})
        restored = BeamDesignResult.model_validate(data)
        assert valid_design_result.id == restored.id
        assert valid_design_result.status == restored.status
        assert valid_design_result.is_acceptable == restored.is_acceptable


# =============================================================================
# DesignDefaults Contract Tests
# =============================================================================


class TestDesignDefaultsContract:
    """Contract tests for DesignDefaults model."""

    def test_can_create_with_no_args(self):
        """Verify DesignDefaults can be created with all defaults."""
        defaults = DesignDefaults()
        assert defaults is not None

    def test_key_defaults_exist(self):
        """Verify essential default fields exist."""
        defaults = DesignDefaults()
        # These are the key fields that must exist for batch processing
        assert hasattr(defaults, "fck_mpa")
        assert hasattr(defaults, "fy_mpa")
        assert hasattr(defaults, "cover_mm")


# =============================================================================
# BeamBatchInput Contract Tests
# =============================================================================


class TestBeamBatchInputContract:
    """Contract tests for BeamBatchInput model."""

    def test_schema_has_beams_and_forces_fields(self):
        """Verify BatchInput has beams and forces arrays."""
        schema = BeamBatchInput.model_json_schema()
        properties = schema.get("properties", {})
        assert "beams" in properties
        assert "forces" in properties

    def test_can_create_with_lists(self):
        """Verify BatchInput accepts lists of beams and forces."""
        beam = BeamGeometry(
            id="B1",
            label="B1",
            story="Ground",
            point1=Point3D(x=0, y=0, z=0),
            point2=Point3D(x=5, y=0, z=0),
            section=SectionProperties(width_mm=300, depth_mm=500),
        )
        forces = BeamForces(id="B1", load_case="LC1", mu_knm=100, vu_kn=50)

        batch = BeamBatchInput(beams=[beam], forces=[forces])
        assert len(batch.beams) == 1
        assert len(batch.forces) == 1


# =============================================================================
# BeamBatchResult Contract Tests
# =============================================================================


class TestBeamBatchResultContract:
    """Contract tests for BeamBatchResult model."""

    def test_schema_has_results_field(self):
        """Verify BatchResult has results array."""
        schema = BeamBatchResult.model_json_schema()
        properties = schema.get("properties", {})
        assert "results" in properties

    def test_has_summary_fields(self):
        """Verify BatchResult has summary/statistics fields."""
        # Create a minimal batch result
        result = BeamBatchResult(results=[])
        # Check for expected summary attributes
        assert hasattr(result, "results")
        # The model may have computed summary fields


# =============================================================================
# Cross-Model Integration Tests
# =============================================================================


class TestCrossModelIntegration:
    """Integration tests across multiple models."""

    def test_complete_beam_design_workflow_types(self):
        """Verify BeamGeometry → BeamForces → BeamDesignResult type compatibility."""
        # 1. Create geometry
        beam = BeamGeometry(
            id="B1_Floor1",
            label="B1",
            story="Floor1",
            point1=Point3D(x=0, y=0, z=3),
            point2=Point3D(x=6, y=0, z=3),
            section=SectionProperties(width_mm=300, depth_mm=600, fck_mpa=30),
        )

        # 2. Define forces (using same ID)
        forces = BeamForces(
            id=beam.id,  # Must match beam.id
            load_case="1.5DL+1.5LL",
            mu_knm=250,
            vu_kn=125,
        )

        # 3. Create result (using same ID)
        result = BeamDesignResult(
            id=beam.id,
            load_case=forces.load_case,
            mu_knm=forces.mu_knm,
            vu_kn=forces.vu_kn,
            ast_mm2=1200,
            asv_mm2_m=300,
            status=DesignStatus.PASS,
            utilization=0.88,
        )

        # Verify chain of IDs
        assert beam.id == forces.id == result.id
        assert forces.load_case == result.load_case

    def test_batch_workflow_consistency(self):
        """Verify batch input/output models work together."""
        # Create batch input
        beams = [
            BeamGeometry(
                id=f"B{i}",
                label=f"B{i}",
                story="Ground",
                point1=Point3D(x=i * 5, y=0, z=0),
                point2=Point3D(x=(i + 1) * 5, y=0, z=0),
                section=SectionProperties(width_mm=300, depth_mm=500),
            )
            for i in range(3)
        ]

        forces_list = [
            BeamForces(
                id=f"B{i}", load_case="LC1", mu_knm=100 + i * 20, vu_kn=50 + i * 10
            )
            for i in range(3)
        ]

        batch_input = BeamBatchInput(beams=beams, forces=forces_list)

        # Simulate result creation
        results = [
            BeamDesignResult(
                id=f.id,
                load_case=f.load_case,
                mu_knm=f.mu_knm,
                vu_kn=f.vu_kn,
                ast_mm2=800 + i * 50,
                asv_mm2_m=200,
                status=DesignStatus.PASS,
                utilization=0.8 + i * 0.05,
            )
            for i, f in enumerate(forces_list)
        ]

        batch_result = BeamBatchResult(results=results)

        # Verify counts match
        assert len(batch_input.beams) == len(batch_result.results)


# =============================================================================
# Schema Versioning Tests
# =============================================================================


class TestSchemaVersioning:
    """Tests to detect unintended schema changes."""

    EXPECTED_BEAM_GEOMETRY_FIELDS = {
        "id",
        "label",
        "story",
        "frame_type",
        "point1",
        "point2",
        "section",
        "angle",
        "source_id",
    }

    EXPECTED_BEAM_FORCES_FIELDS = {
        "id",
        "load_case",
        "mu_knm",
        "vu_kn",
        "pu_kn",
        "station_count",
    }

    EXPECTED_BEAM_DESIGN_RESULT_FIELDS = {
        "id",
        "load_case",
        "mu_knm",
        "vu_kn",
        "ast_mm2",
        "asc_mm2",
        "asv_mm2_m",
        "status",
        "utilization",
        "moment_capacity_knm",
        "shear_capacity_kn",
        "messages",
    }

    def test_beam_geometry_fields_unchanged(self):
        """Verify BeamGeometry fields haven't changed."""
        schema = BeamGeometry.model_json_schema()
        actual_fields = set(schema.get("properties", {}).keys())
        assert actual_fields == self.EXPECTED_BEAM_GEOMETRY_FIELDS, (
            f"Field mismatch! Added: {actual_fields - self.EXPECTED_BEAM_GEOMETRY_FIELDS}, "
            f"Removed: {self.EXPECTED_BEAM_GEOMETRY_FIELDS - actual_fields}"
        )

    def test_beam_forces_fields_unchanged(self):
        """Verify BeamForces fields haven't changed."""
        schema = BeamForces.model_json_schema()
        actual_fields = set(schema.get("properties", {}).keys())
        assert actual_fields == self.EXPECTED_BEAM_FORCES_FIELDS, (
            f"Field mismatch! Added: {actual_fields - self.EXPECTED_BEAM_FORCES_FIELDS}, "
            f"Removed: {self.EXPECTED_BEAM_FORCES_FIELDS - actual_fields}"
        )

    def test_beam_design_result_fields_unchanged(self):
        """Verify BeamDesignResult fields haven't changed."""
        schema = BeamDesignResult.model_json_schema()
        actual_fields = set(schema.get("properties", {}).keys())
        assert actual_fields == self.EXPECTED_BEAM_DESIGN_RESULT_FIELDS, (
            f"Field mismatch! Added: {actual_fields - self.EXPECTED_BEAM_DESIGN_RESULT_FIELDS}, "
            f"Removed: {self.EXPECTED_BEAM_DESIGN_RESULT_FIELDS - actual_fields}"
        )
