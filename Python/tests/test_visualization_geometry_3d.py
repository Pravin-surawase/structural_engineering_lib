# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tests for visualization.geometry_3d module.

Coverage targets:
- Point3D: All operations (add, sub, scale, distance, serialization)
- RebarSegment: Length calculation, serialization
- RebarPath: Total length, start/end points, serialization
- StirrupLoop: Perimeter calculation, serialization
- Beam3DGeometry: Complete serialization
- Computation functions: All edge cases and typical scenarios
"""

from __future__ import annotations

import pytest

from structural_lib.visualization.geometry_3d import (
    Beam3DGeometry,
    Point3D,
    RebarPath,
    RebarSegment,
    StirrupLoop,
    compute_beam_outline,
    compute_rebar_positions,
    compute_stirrup_path,
    compute_stirrup_positions,
)

# =============================================================================
# Point3D Tests
# =============================================================================


class TestPoint3D:
    """Tests for Point3D dataclass."""

    def test_create_point(self):
        """Test basic point creation."""
        p = Point3D(100.0, 50.0, 25.0)
        assert p.x == 100.0
        assert p.y == 50.0
        assert p.z == 25.0

    def test_point_immutable(self):
        """Test that Point3D is immutable (frozen)."""
        p = Point3D(1.0, 2.0, 3.0)
        with pytest.raises(AttributeError):
            p.x = 5.0  # type: ignore

    def test_to_tuple(self):
        """Test tuple conversion."""
        p = Point3D(10.0, 20.0, 30.0)
        assert p.to_tuple() == (10.0, 20.0, 30.0)

    def test_to_dict(self):
        """Test JSON dict conversion with rounding."""
        p = Point3D(10.123456, 20.789123, 30.999999)
        d = p.to_dict()
        assert d == {"x": 10.12, "y": 20.79, "z": 31.0}

    def test_addition(self):
        """Test vector addition."""
        p1 = Point3D(1.0, 2.0, 3.0)
        p2 = Point3D(4.0, 5.0, 6.0)
        result = p1 + p2
        assert result == Point3D(5.0, 7.0, 9.0)

    def test_subtraction(self):
        """Test vector subtraction."""
        p1 = Point3D(10.0, 20.0, 30.0)
        p2 = Point3D(3.0, 5.0, 7.0)
        result = p1 - p2
        assert result == Point3D(7.0, 15.0, 23.0)

    def test_scale(self):
        """Test scalar multiplication."""
        p = Point3D(2.0, 3.0, 4.0)
        result = p.scale(2.5)
        assert result == Point3D(5.0, 7.5, 10.0)

    def test_distance_to_same_point(self):
        """Test distance to same point is zero."""
        p = Point3D(5.0, 5.0, 5.0)
        assert p.distance_to(p) == 0.0

    def test_distance_to_other_point(self):
        """Test Euclidean distance calculation."""
        p1 = Point3D(0.0, 0.0, 0.0)
        p2 = Point3D(3.0, 4.0, 0.0)  # 3-4-5 triangle
        assert p1.distance_to(p2) == 5.0

    def test_distance_3d(self):
        """Test 3D distance calculation."""
        p1 = Point3D(0.0, 0.0, 0.0)
        p2 = Point3D(1.0, 2.0, 2.0)  # sqrt(1+4+4) = 3
        assert p1.distance_to(p2) == 3.0


# =============================================================================
# RebarSegment Tests
# =============================================================================


class TestRebarSegment:
    """Tests for RebarSegment dataclass."""

    def test_create_segment(self):
        """Test basic segment creation."""
        start = Point3D(0.0, 50.0, 52.0)
        end = Point3D(4000.0, 50.0, 52.0)
        seg = RebarSegment(start, end, 16.0, "straight")

        assert seg.start == start
        assert seg.end == end
        assert seg.diameter == 16.0
        assert seg.segment_type == "straight"

    def test_segment_length(self):
        """Test segment length calculation."""
        start = Point3D(0.0, 0.0, 0.0)
        end = Point3D(4000.0, 0.0, 0.0)
        seg = RebarSegment(start, end, 16.0)

        assert seg.length == 4000.0

    def test_segment_length_angled(self):
        """Test angled segment length."""
        start = Point3D(0.0, 0.0, 0.0)
        end = Point3D(3000.0, 0.0, 4000.0)  # 3-4-5 scaled by 1000
        seg = RebarSegment(start, end, 16.0)

        assert seg.length == 5000.0

    def test_segment_to_dict(self):
        """Test JSON serialization."""
        start = Point3D(0.0, 50.0, 52.0)
        end = Point3D(4000.0, 50.0, 52.0)
        seg = RebarSegment(start, end, 16.0, "straight")

        d = seg.to_dict()
        assert d["start"] == {"x": 0.0, "y": 50.0, "z": 52.0}
        assert d["end"] == {"x": 4000.0, "y": 50.0, "z": 52.0}
        assert d["diameter"] == 16.0
        assert d["type"] == "straight"
        assert d["length"] == 4000.0


# =============================================================================
# RebarPath Tests
# =============================================================================


class TestRebarPath:
    """Tests for RebarPath dataclass."""

    def test_create_path(self):
        """Test basic path creation."""
        seg = RebarSegment(
            Point3D(0.0, 0.0, 52.0),
            Point3D(4000.0, 0.0, 52.0),
            16.0,
        )
        path = RebarPath(
            bar_id="B1",
            segments=[seg],
            diameter=16.0,
            bar_type="bottom",
            zone="full",
        )

        assert path.bar_id == "B1"
        assert len(path.segments) == 1
        assert path.diameter == 16.0

    def test_total_length_single_segment(self):
        """Test total length with single segment."""
        seg = RebarSegment(
            Point3D(0.0, 0.0, 0.0),
            Point3D(4000.0, 0.0, 0.0),
            16.0,
        )
        path = RebarPath("B1", [seg], 16.0)

        assert path.total_length == 4000.0

    def test_total_length_multiple_segments(self):
        """Test total length with multiple segments."""
        seg1 = RebarSegment(
            Point3D(0.0, 0.0, 0.0),
            Point3D(3800.0, 0.0, 0.0),
            16.0,
            "straight",
        )
        seg2 = RebarSegment(
            Point3D(3800.0, 0.0, 0.0),
            Point3D(3800.0, 0.0, 100.0),
            16.0,
            "hook_90",
        )
        path = RebarPath("B1", [seg1, seg2], 16.0)

        assert path.total_length == 3900.0

    def test_start_point(self):
        """Test start point property."""
        seg = RebarSegment(
            Point3D(100.0, 50.0, 52.0),
            Point3D(3900.0, 50.0, 52.0),
            16.0,
        )
        path = RebarPath("B1", [seg], 16.0)

        assert path.start_point == Point3D(100.0, 50.0, 52.0)

    def test_end_point(self):
        """Test end point property."""
        seg = RebarSegment(
            Point3D(100.0, 50.0, 52.0),
            Point3D(3900.0, 50.0, 52.0),
            16.0,
        )
        path = RebarPath("B1", [seg], 16.0)

        assert path.end_point == Point3D(3900.0, 50.0, 52.0)

    def test_empty_segments_start_point(self):
        """Test start point with empty segments."""
        path = RebarPath("B1", [], 16.0)
        assert path.start_point == Point3D(0, 0, 0)

    def test_path_to_dict(self):
        """Test JSON serialization."""
        seg = RebarSegment(
            Point3D(0.0, 50.0, 52.0),
            Point3D(4000.0, 50.0, 52.0),
            16.0,
        )
        path = RebarPath("B1", [seg], 16.0, "bottom", "full")

        d = path.to_dict()
        assert d["barId"] == "B1"
        assert d["barType"] == "bottom"
        assert d["zone"] == "full"
        assert d["diameter"] == 16.0
        assert d["totalLength"] == 4000.0
        assert len(d["segments"]) == 1


# =============================================================================
# StirrupLoop Tests
# =============================================================================


class TestStirrupLoop:
    """Tests for StirrupLoop dataclass."""

    def test_create_stirrup(self):
        """Test basic stirrup creation."""
        path = [
            Point3D(150.0, -96.0, 44.0),
            Point3D(150.0, 96.0, 44.0),
            Point3D(150.0, 96.0, 406.0),
            Point3D(150.0, -96.0, 406.0),
        ]
        stirrup = StirrupLoop(
            position_x=150.0,
            path=path,
            diameter=8.0,
            legs=2,
            hook_type="135",
        )

        assert stirrup.position_x == 150.0
        assert len(stirrup.path) == 4
        assert stirrup.diameter == 8.0
        assert stirrup.legs == 2
        assert stirrup.hook_type == "135"

    def test_stirrup_perimeter(self):
        """Test perimeter calculation for rectangular stirrup."""
        # 192mm wide x 362mm tall rectangle
        path = [
            Point3D(0.0, -96.0, 44.0),
            Point3D(0.0, 96.0, 44.0),
            Point3D(0.0, 96.0, 406.0),
            Point3D(0.0, -96.0, 406.0),
        ]
        stirrup = StirrupLoop(0.0, path, 8.0)

        # Perimeter = 2*(192) + 2*(362) = 1108
        expected = 2 * 192 + 2 * 362
        assert abs(stirrup.perimeter - expected) < 0.01

    def test_stirrup_perimeter_empty(self):
        """Test perimeter with empty path."""
        stirrup = StirrupLoop(0.0, [], 8.0)
        assert stirrup.perimeter == 0.0

    def test_stirrup_to_dict(self):
        """Test JSON serialization."""
        path = [
            Point3D(150.0, -96.0, 44.0),
            Point3D(150.0, 96.0, 44.0),
            Point3D(150.0, 96.0, 406.0),
            Point3D(150.0, -96.0, 406.0),
        ]
        stirrup = StirrupLoop(150.0, path, 8.0, 2, "135")

        d = stirrup.to_dict()
        assert d["positionX"] == 150.0
        assert d["diameter"] == 8.0
        assert d["legs"] == 2
        assert d["hookType"] == "135"
        assert len(d["path"]) == 4
        assert "perimeter" in d


# =============================================================================
# Beam3DGeometry Tests
# =============================================================================


class TestBeam3DGeometry:
    """Tests for Beam3DGeometry dataclass."""

    def test_create_geometry(self):
        """Test basic geometry creation."""
        outline = compute_beam_outline(300, 450, 4000)
        geometry = Beam3DGeometry(
            beam_id="B1",
            story="GF",
            dimensions={"b": 300, "D": 450, "span": 4000},
            concrete_outline=outline,
            rebars=[],
            stirrups=[],
            metadata={"fck": 25, "fy": 500},
        )

        assert geometry.beam_id == "B1"
        assert geometry.story == "GF"
        assert geometry.dimensions["b"] == 300

    def test_geometry_to_dict(self):
        """Test complete JSON serialization."""
        outline = compute_beam_outline(300, 450, 4000)
        geometry = Beam3DGeometry(
            beam_id="B1",
            story="GF",
            dimensions={"b": 300, "D": 450, "span": 4000},
            concrete_outline=outline,
            rebars=[],
            stirrups=[],
            metadata={"fck": 25, "fy": 500},
        )

        d = geometry.to_dict()
        assert d["beamId"] == "B1"
        assert d["story"] == "GF"
        assert d["version"] == "1.0.0"
        assert len(d["concreteOutline"]) == 8
        assert d["dimensions"]["b"] == 300


# =============================================================================
# compute_rebar_positions Tests
# =============================================================================


class TestComputeRebarPositions:
    """Tests for compute_rebar_positions function."""

    def test_bottom_bars_2_count(self):
        """Test 2 bottom bars placement."""
        positions = compute_rebar_positions(
            beam_width=300,
            beam_depth=450,
            cover=40,
            bar_count=2,
            bar_dia=16,
            stirrup_dia=8,
            is_top=False,
        )

        assert len(positions) == 2
        # Both bars at same Z (near soffit)
        z_expected = 40 + 8 + 16 / 2  # cover + stirrup + bar_dia/2 = 56
        assert positions[0].z == z_expected
        assert positions[1].z == z_expected
        # Y positions symmetric about center
        assert positions[0].y < 0  # Left of center
        assert positions[1].y > 0  # Right of center

    def test_top_bars_2_count(self):
        """Test 2 top bars placement."""
        positions = compute_rebar_positions(
            beam_width=300,
            beam_depth=450,
            cover=40,
            bar_count=2,
            bar_dia=16,
            stirrup_dia=8,
            is_top=True,
        )

        assert len(positions) == 2
        # Z near top
        z_expected = 450 - 40 - 8 - 16 / 2  # D - cover - stirrup - bar_dia/2 = 394
        assert positions[0].z == z_expected

    def test_single_bar_centered(self):
        """Test single bar is centered."""
        positions = compute_rebar_positions(
            beam_width=300,
            beam_depth=450,
            cover=40,
            bar_count=1,
            bar_dia=16,
            stirrup_dia=8,
            is_top=False,
        )

        assert len(positions) == 1
        assert positions[0].y == 0.0  # Centered

    def test_zero_bars(self):
        """Test zero bars returns empty list."""
        positions = compute_rebar_positions(
            beam_width=300,
            beam_depth=450,
            cover=40,
            bar_count=0,
            bar_dia=16,
            stirrup_dia=8,
            is_top=False,
        )

        assert positions == []

    def test_invalid_layers_raises(self):
        """Test invalid layer count raises ValueError."""
        with pytest.raises(ValueError):
            compute_rebar_positions(
                beam_width=300,
                beam_depth=450,
                cover=40,
                bar_count=2,
                bar_dia=16,
                stirrup_dia=8,
                layers=0,
            )

    def test_insufficient_width_raises(self):
        """Test insufficient beam width raises ValueError."""
        with pytest.raises(ValueError):
            compute_rebar_positions(
                beam_width=100,
                beam_depth=450,
                cover=40,
                bar_count=2,
                bar_dia=25,
                stirrup_dia=8,
                is_top=False,
            )

    def test_4_bars_single_layer(self):
        """Test 4 bars evenly distributed."""
        positions = compute_rebar_positions(
            beam_width=300,
            beam_depth=450,
            cover=40,
            bar_count=4,
            bar_dia=16,
            stirrup_dia=8,
            is_top=False,
            layers=1,
        )

        assert len(positions) == 4
        # All at same Z
        assert all(p.z == positions[0].z for p in positions)
        # Evenly spaced
        y_values = sorted([p.y for p in positions])
        spacing = y_values[1] - y_values[0]
        for i in range(1, len(y_values)):
            assert abs(y_values[i] - y_values[i - 1] - spacing) < 0.1

    def test_multi_layer(self):
        """Test bars in two layers."""
        positions = compute_rebar_positions(
            beam_width=300,
            beam_depth=450,
            cover=40,
            bar_count=4,
            bar_dia=16,
            stirrup_dia=8,
            is_top=False,
            layers=2,
        )

        assert len(positions) == 4
        # Should have two different Z values
        z_values = {p.z for p in positions}
        assert len(z_values) == 2


# =============================================================================
# compute_stirrup_path Tests
# =============================================================================


class TestComputeStirrupPath:
    """Tests for compute_stirrup_path function."""

    def test_stirrup_path_4_corners(self):
        """Test stirrup has 4 corners for 2-leg."""
        path = compute_stirrup_path(
            beam_width=300,
            beam_depth=450,
            cover=40,
            stirrup_dia=8,
            position_x=150,
            legs=2,
        )

        assert len(path) == 4

    def test_stirrup_path_x_position(self):
        """Test all corners at same X position."""
        path = compute_stirrup_path(
            beam_width=300,
            beam_depth=450,
            cover=40,
            stirrup_dia=8,
            position_x=150,
        )

        assert all(p.x == 150 for p in path)

    def test_stirrup_symmetric(self):
        """Test stirrup is symmetric about Y=0."""
        path = compute_stirrup_path(
            beam_width=300,
            beam_depth=450,
            cover=40,
            stirrup_dia=8,
            position_x=0,
        )

        y_values = [p.y for p in path]
        assert min(y_values) == -max(y_values)

    def test_stirrup_z_range(self):
        """Test stirrup Z range covers most of depth."""
        path = compute_stirrup_path(
            beam_width=300,
            beam_depth=450,
            cover=40,
            stirrup_dia=8,
            position_x=0,
        )

        z_values = [p.z for p in path]
        z_min = min(z_values)
        z_max = max(z_values)

        # Bottom of stirrup should be near cover + stirrup_dia/2
        assert z_min == 40 + 8 / 2  # 44mm
        # Top should be near D - cover - stirrup_dia/2
        assert z_max == 450 - 40 - 8 / 2  # 406mm


# =============================================================================
# compute_stirrup_positions Tests
# =============================================================================


class TestComputeStirrupPositions:
    """Tests for compute_stirrup_positions function."""

    def test_first_stirrup_at_half_spacing(self):
        """Test first stirrup at half-spacing from support."""
        positions = compute_stirrup_positions(
            span=4000,
            stirrup_spacing_start=100,
            stirrup_spacing_mid=150,
            stirrup_spacing_end=100,
        )

        assert positions[0] == 50.0  # Half of start spacing

    def test_stirrup_count_reasonable(self):
        """Test reasonable number of stirrups for typical beam."""
        positions = compute_stirrup_positions(
            span=4000,
            stirrup_spacing_start=100,
            stirrup_spacing_mid=150,
            stirrup_spacing_end=100,
        )

        # Approximate: 4000mm span, avg 125mm spacing = ~32 stirrups
        assert 20 < len(positions) < 50

    def test_stirrup_positions_increasing(self):
        """Test positions are strictly increasing."""
        positions = compute_stirrup_positions(
            span=4000,
            stirrup_spacing_start=100,
            stirrup_spacing_mid=150,
            stirrup_spacing_end=100,
        )

        for i in range(1, len(positions)):
            assert positions[i] > positions[i - 1]

    def test_stirrup_positions_within_span(self):
        """Test all positions within span."""
        positions = compute_stirrup_positions(
            span=4000,
            stirrup_spacing_start=100,
            stirrup_spacing_mid=150,
            stirrup_spacing_end=100,
        )

        assert all(0 < p < 4000 for p in positions)

    def test_invalid_spacing_raises(self):
        """Test invalid spacing raises ValueError."""
        with pytest.raises(ValueError):
            compute_stirrup_positions(
                span=4000,
                stirrup_spacing_start=0,
                stirrup_spacing_mid=150,
                stirrup_spacing_end=100,
            )

    def test_invalid_span_raises(self):
        """Test invalid span raises ValueError."""
        with pytest.raises(ValueError):
            compute_stirrup_positions(
                span=0,
                stirrup_spacing_start=100,
                stirrup_spacing_mid=150,
                stirrup_spacing_end=100,
            )


# =============================================================================
# compute_beam_outline Tests
# =============================================================================


class TestComputeBeamOutline:
    """Tests for compute_beam_outline function."""

    def test_outline_8_corners(self):
        """Test outline has 8 corners."""
        corners = compute_beam_outline(300, 450, 4000)
        assert len(corners) == 8

    def test_outline_bottom_at_z0(self):
        """Test bottom 4 corners at z=0."""
        corners = compute_beam_outline(300, 450, 4000)
        bottom = corners[:4]
        assert all(c.z == 0 for c in bottom)

    def test_outline_top_at_depth(self):
        """Test top 4 corners at z=D."""
        corners = compute_beam_outline(300, 450, 4000)
        top = corners[4:]
        assert all(c.z == 450 for c in top)

    def test_outline_x_range(self):
        """Test X range is 0 to span."""
        corners = compute_beam_outline(300, 450, 4000)
        x_values = [c.x for c in corners]
        assert min(x_values) == 0
        assert max(x_values) == 4000

    def test_outline_y_symmetric(self):
        """Test Y range is symmetric about 0."""
        corners = compute_beam_outline(300, 450, 4000)
        y_values = [c.y for c in corners]
        assert min(y_values) == -150  # -b/2
        assert max(y_values) == 150  # +b/2


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for geometry_3d module."""

    def test_full_beam_geometry_creation(self):
        """Test creating complete beam geometry."""
        # Create test data mimicking BeamDetailingResult
        outline = compute_beam_outline(300, 450, 4000)

        # Create some rebars
        bottom_seg = RebarSegment(
            Point3D(0.0, -50.0, 56.0),
            Point3D(4000.0, -50.0, 56.0),
            16.0,
        )
        bottom_bar = RebarPath("B1", [bottom_seg], 16.0, "bottom", "full")

        # Create stirrups
        stirrup_positions = compute_stirrup_positions(4000, 100, 150, 100)
        stirrups = []
        for x in stirrup_positions[:5]:  # Just first 5 for test
            path = compute_stirrup_path(300, 450, 40, 8, x)
            stirrups.append(StirrupLoop(x, path, 8.0, 2, "135"))

        geometry = Beam3DGeometry(
            beam_id="B1",
            story="GF",
            dimensions={"b": 300, "D": 450, "span": 4000},
            concrete_outline=outline,
            rebars=[bottom_bar],
            stirrups=stirrups,
            metadata={"fck": 25, "fy": 500},
        )

        # Serialize and check
        d = geometry.to_dict()
        assert d["beamId"] == "B1"
        assert len(d["rebars"]) == 1
        assert len(d["stirrups"]) == 5
        assert d["version"] == "1.0.0"

    def test_json_schema_structure(self):
        """Test JSON output matches expected schema for Three.js."""
        outline = compute_beam_outline(300, 450, 4000)
        geometry = Beam3DGeometry(
            beam_id="B1",
            story="GF",
            dimensions={"b": 300, "D": 450, "span": 4000},
            concrete_outline=outline,
            rebars=[],
            stirrups=[],
        )

        d = geometry.to_dict()

        # Required fields
        required_fields = [
            "beamId",
            "story",
            "dimensions",
            "concreteOutline",
            "rebars",
            "stirrups",
            "metadata",
            "version",
        ]
        for field in required_fields:
            assert field in d, f"Missing required field: {field}"

        # Dimension fields
        for dim in ["b", "D", "span"]:
            assert dim in d["dimensions"]
