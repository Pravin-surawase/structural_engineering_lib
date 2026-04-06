# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Edge case tests for 3D visualization / geometry module (TASK-520).

Coverage targets:
- Minimum dimension beam (150×300mm) — rebar should still fit
- Maximum reinforcement (dense rebar, multi-layer)
- Compression reinforcement in 3D view
- compute_stirrup_positions with custom zone_length
- BuildingBeam3D.to_dict / Building3DGeometry.to_dict
- building_to_3d_geometry: empty beams, frame type filter
- StirrupLoop perimeter with degenerate paths
- beam_to_3d_geometry with minimal / extreme detailing
"""

from __future__ import annotations

import json

import pytest

from structural_lib.codes.is456.beam.detailing import create_beam_detailing
from structural_lib.visualization.geometry_3d import (
    Building3DGeometry,
    BuildingBeam3D,
    Point3D,
    RebarPath,
    RebarSegment,
    StirrupLoop,
    beam_to_3d_geometry,
    building_to_3d_geometry,
    compute_beam_outline,
    compute_rebar_positions,
    compute_stirrup_path,
    compute_stirrup_positions,
)

# =============================================================================
# Minimum dimension beam (150×300mm)
# =============================================================================


class TestMinimumDimensionBeam:
    """Test 3D geometry with minimum practical beam dimensions."""

    def test_rebar_positions_fit_150x300(self) -> None:
        """150×300mm beam with 2-12φ bars should fit within cross-section."""
        positions = compute_rebar_positions(
            beam_width=150,
            beam_depth=300,
            cover=25,
            bar_count=2,
            bar_dia=12,
            stirrup_dia=8,
            is_top=False,
        )
        assert len(positions) == 2
        half_width = 150 / 2
        for p in positions:
            assert -half_width < p.y < half_width, "Bar must be inside beam width"
            assert 0 < p.z < 300, "Bar must be inside beam depth"

    def test_stirrup_path_fits_150x300(self) -> None:
        """Stirrup corners should fit within 150×300mm beam."""
        path = compute_stirrup_path(
            beam_width=150,
            beam_depth=300,
            cover=25,
            stirrup_dia=8,
            position_x=100,
        )
        assert len(path) == 4
        for p in path:
            assert -75 <= p.y <= 75
            assert 0 <= p.z <= 300

    def test_full_geometry_150x300(self) -> None:
        """Complete 3D geometry for 150×300mm beam (minimum practical)."""
        detailing = create_beam_detailing(
            beam_id="MIN150",
            story="GF",
            b=150,
            D=300,
            span=3000,
            cover=25,
            fck=20,
            fy=415,
            ast_start=226,
            ast_mid=226,
            ast_end=226,
        )
        geometry = beam_to_3d_geometry(detailing)
        assert geometry.beam_id == "MIN150"
        assert geometry.dimensions["b"] == 150
        assert len(geometry.rebars) > 0
        assert len(geometry.stirrups) > 0

        # Check all rebar Y positions are within the beam width
        for rebar in geometry.rebars:
            for seg in rebar.segments:
                assert -75 <= seg.start.y <= 75
                assert -75 <= seg.end.y <= 75


# =============================================================================
# Maximum reinforcement / dense rebar layout
# =============================================================================


class TestDenseRebarLayout:
    """Test 3D geometry with high reinforcement ratios."""

    def test_max_bars_single_layer(self) -> None:
        """6 bars in 300mm beam width, single layer."""
        positions = compute_rebar_positions(
            beam_width=300,
            beam_depth=600,
            cover=40,
            bar_count=6,
            bar_dia=16,
            stirrup_dia=8,
            is_top=False,
            layers=1,
        )
        assert len(positions) == 6
        # All bars at same Z
        z_values = {p.z for p in positions}
        assert len(z_values) == 1

    def test_multi_layer_6_bars(self) -> None:
        """6 bars in 2 layers (3+3)."""
        positions = compute_rebar_positions(
            beam_width=300,
            beam_depth=600,
            cover=40,
            bar_count=6,
            bar_dia=20,
            stirrup_dia=8,
            is_top=False,
            layers=2,
        )
        assert len(positions) == 6
        z_values = sorted({p.z for p in positions})
        assert len(z_values) == 2
        # Second layer should be above first
        assert z_values[1] > z_values[0]
        # Layer spacing = bar_dia + 25 = 45mm
        assert abs(z_values[1] - z_values[0] - (20 + 25)) < 0.1

    def test_large_bar_diameter_25mm(self) -> None:
        """25mm bars in 400mm beam — check clearances."""
        positions = compute_rebar_positions(
            beam_width=400,
            beam_depth=700,
            cover=40,
            bar_count=4,
            bar_dia=25,
            stirrup_dia=10,
            is_top=False,
        )
        assert len(positions) == 4
        # Bars should be evenly spaced
        y_sorted = sorted(p.y for p in positions)
        spacings = [y_sorted[i + 1] - y_sorted[i] for i in range(len(y_sorted) - 1)]
        assert all(abs(s - spacings[0]) < 0.1 for s in spacings)


# =============================================================================
# Compression reinforcement in 3D view
# =============================================================================


class TestCompressionReinforcement3D:
    """Test 3D geometry with compression reinforcement."""

    def test_beam_with_compression_steel(self) -> None:
        """Beam with explicit compression steel should have top bars in geometry."""
        detailing = create_beam_detailing(
            beam_id="DRC",
            story="1F",
            b=300,
            D=600,
            span=6000,
            cover=40,
            fck=25,
            fy=500,
            ast_start=1500,
            ast_mid=1500,
            ast_end=1500,
            asc_start=750,
            asc_mid=750,
            asc_end=750,
        )
        geometry = beam_to_3d_geometry(detailing)

        top_bars = [r for r in geometry.rebars if r.bar_type == "top"]
        bottom_bars = [r for r in geometry.rebars if r.bar_type == "bottom"]

        assert len(top_bars) > 0, "Should have top (compression) bars"
        assert len(bottom_bars) > 0, "Should have bottom (tension) bars"

        # Top bars should be near the top of the beam
        for bar in top_bars:
            z = bar.segments[0].start.z
            assert z > 300, f"Top bar at z={z} should be in upper half (D=600)"

        # Bottom bars near bottom
        for bar in bottom_bars:
            z = bar.segments[0].start.z
            assert z < 300, f"Bottom bar at z={z} should be in lower half (D=600)"


# =============================================================================
# compute_stirrup_positions edge cases
# =============================================================================


class TestStirrupPositionsEdgeCases:
    """Edge case tests for compute_stirrup_positions."""

    def test_custom_zone_length(self) -> None:
        """Custom zone_length should affect distribution."""
        # Default zone_length = span/4 = 1000
        default = compute_stirrup_positions(4000, 100, 200, 100)
        # Custom zone_length = 500 (shorter support zones)
        custom = compute_stirrup_positions(4000, 100, 200, 100, zone_length=500)
        # With shorter zones, should have fewer close-spaced stirrups
        assert len(custom) != len(default) or custom != default

    def test_zone_length_half_span(self) -> None:
        """zone_length = span/2 should clamp to half span (no mid zone)."""
        positions = compute_stirrup_positions(4000, 100, 200, 100, zone_length=2000)
        assert len(positions) > 0
        # All stirrups should be within span
        assert all(0 < p < 4000 for p in positions)

    def test_zone_length_exceeds_half_span(self) -> None:
        """zone_length > span/2 should be clamped."""
        positions = compute_stirrup_positions(4000, 100, 200, 100, zone_length=3000)
        assert len(positions) > 0
        assert all(0 < p < 4000 for p in positions)

    def test_negative_zone_length_raises(self) -> None:
        """Negative zone_length should raise ValueError."""
        with pytest.raises(ValueError):
            compute_stirrup_positions(4000, 100, 200, 100, zone_length=-100)

    def test_uniform_spacing(self) -> None:
        """Same spacing in all zones should give roughly uniform distribution."""
        positions = compute_stirrup_positions(4000, 150, 150, 150)
        spacings = [positions[i + 1] - positions[i] for i in range(len(positions) - 1)]
        # All spacings should be ~150mm (except possibly first/last)
        interior = spacings[1:-1] if len(spacings) > 2 else spacings
        for s in interior:
            assert abs(s - 150) < 1.0

    def test_very_short_span(self) -> None:
        """Very short span (500mm) should produce at least some stirrups."""
        positions = compute_stirrup_positions(500, 75, 100, 75)
        assert len(positions) >= 1
        assert all(0 < p < 500 for p in positions)

    def test_negative_span_raises(self) -> None:
        """Negative span should raise ValueError."""
        with pytest.raises(ValueError):
            compute_stirrup_positions(-4000, 100, 200, 100)

    def test_negative_mid_spacing_raises(self) -> None:
        """Negative mid spacing should raise ValueError."""
        with pytest.raises(ValueError):
            compute_stirrup_positions(4000, 100, -200, 100)

    def test_negative_end_spacing_raises(self) -> None:
        """Negative end spacing should raise ValueError."""
        with pytest.raises(ValueError):
            compute_stirrup_positions(4000, 100, 200, -100)


# =============================================================================
# BuildingBeam3D and Building3DGeometry serialization
# =============================================================================


class TestBuildingBeam3DSerialization:
    """Tests for BuildingBeam3D.to_dict()."""

    def test_to_dict(self) -> None:
        """BuildingBeam3D.to_dict should produce complete JSON."""
        beam = BuildingBeam3D(
            beam_id="B10",
            story="L2",
            frame_type="beam",
            start=Point3D(0.0, 0.0, 3000.0),
            end=Point3D(5000.0, 0.0, 3000.0),
        )
        d = beam.to_dict()
        assert d["beamId"] == "B10"
        assert d["story"] == "L2"
        assert d["frameType"] == "beam"
        assert d["start"]["x"] == 0.0
        assert d["end"]["x"] == 5000.0
        assert d["start"]["z"] == 3000.0

    def test_frozen(self) -> None:
        """BuildingBeam3D should be immutable."""
        beam = BuildingBeam3D(
            beam_id="B1",
            story="L1",
            frame_type="beam",
            start=Point3D(0, 0, 0),
            end=Point3D(1000, 0, 0),
        )
        with pytest.raises(AttributeError):
            beam.beam_id = "B2"  # type: ignore


class TestBuilding3DGeometrySerialization:
    """Tests for Building3DGeometry.to_dict()."""

    def test_to_dict_structure(self) -> None:
        """Building3DGeometry.to_dict should have correct schema."""
        beam = BuildingBeam3D(
            beam_id="B1",
            story="L1",
            frame_type="beam",
            start=Point3D(0, 0, 0),
            end=Point3D(5000, 0, 0),
        )
        geo = Building3DGeometry(
            beams=[beam],
            bounding_box={
                "min_x": 0,
                "max_x": 5000,
                "min_y": 0,
                "max_y": 0,
                "min_z": 0,
                "max_z": 0,
            },
            center=Point3D(2500, 0, 0),
            metadata={"beamCount": 1},
        )
        d = geo.to_dict()
        assert d["version"] == "1.0.0"
        assert len(d["beams"]) == 1
        assert d["center"]["x"] == 2500.0
        assert d["metadata"]["beamCount"] == 1

    def test_json_serializable(self) -> None:
        """Building3DGeometry.to_dict should be JSON-serializable."""
        beam = BuildingBeam3D(
            beam_id="B1",
            story="L1",
            frame_type="beam",
            start=Point3D(0, 0, 0),
            end=Point3D(5000, 0, 0),
        )
        geo = Building3DGeometry(
            beams=[beam],
            bounding_box={
                "min_x": 0,
                "max_x": 5000,
                "min_y": 0,
                "max_y": 0,
                "min_z": 0,
                "max_z": 0,
            },
            center=Point3D(2500, 0, 0),
        )
        json_str = json.dumps(geo.to_dict())
        parsed = json.loads(json_str)
        assert parsed["version"] == "1.0.0"


# =============================================================================
# building_to_3d_geometry edge cases
# =============================================================================


class TestBuildingTo3DGeometryEdgeCases:
    """Edge case tests for building_to_3d_geometry function."""

    def test_empty_beams_raises(self) -> None:
        """Empty beam list should raise ValueError."""
        with pytest.raises(ValueError, match="No beams"):
            building_to_3d_geometry([])

    def test_frame_type_filter(self) -> None:
        """include_frame_types should filter beams."""
        from structural_lib.core.models import (
            BeamGeometry,
            FrameType,
            SectionProperties,
        )
        from structural_lib.core.models import (
            Point3D as ModelPoint3D,
        )

        section = SectionProperties(width_mm=300, depth_mm=500, fck_mpa=25, fy_mpa=500)
        beams = [
            BeamGeometry(
                id="B1",
                label="B1",
                story="L1",
                frame_type=FrameType.BEAM,
                point1=ModelPoint3D(x=0, y=0, z=0),
                point2=ModelPoint3D(x=5, y=0, z=0),
                section=section,
                angle=0.0,
            ),
            BeamGeometry(
                id="C1",
                label="C1",
                story="L1",
                frame_type=FrameType.COLUMN,
                point1=ModelPoint3D(x=0, y=0, z=0),
                point2=ModelPoint3D(x=0, y=0, z=3),
                section=section,
                angle=90.0,
            ),
        ]
        # Filter beams only
        geometry = building_to_3d_geometry(beams, include_frame_types=("beam",))
        assert len(geometry.beams) == 1
        assert geometry.beams[0].beam_id == "B1"

    def test_filter_excludes_all_raises(self) -> None:
        """Filter that excludes all beams should raise ValueError."""
        from structural_lib.core.models import (
            BeamGeometry,
            FrameType,
            SectionProperties,
        )
        from structural_lib.core.models import (
            Point3D as ModelPoint3D,
        )

        section = SectionProperties(width_mm=300, depth_mm=500, fck_mpa=25, fy_mpa=500)
        beams = [
            BeamGeometry(
                id="B1",
                label="B1",
                story="L1",
                frame_type=FrameType.BEAM,
                point1=ModelPoint3D(x=0, y=0, z=0),
                point2=ModelPoint3D(x=5, y=0, z=0),
                section=section,
                angle=0.0,
            ),
        ]
        with pytest.raises(ValueError, match="No beams"):
            building_to_3d_geometry(beams, include_frame_types=("column",))

    def test_custom_unit_scale(self) -> None:
        """Custom unit_scale should scale all coordinates."""
        from structural_lib.core.models import (
            BeamGeometry,
            FrameType,
            SectionProperties,
        )
        from structural_lib.core.models import (
            Point3D as ModelPoint3D,
        )

        section = SectionProperties(width_mm=300, depth_mm=500, fck_mpa=25, fy_mpa=500)
        beams = [
            BeamGeometry(
                id="B1",
                label="B1",
                story="L1",
                frame_type=FrameType.BEAM,
                point1=ModelPoint3D(x=0, y=0, z=0),
                point2=ModelPoint3D(x=5, y=0, z=0),
                section=section,
                angle=0.0,
            ),
        ]
        # Scale factor 1.0 (keep meters)
        geometry = building_to_3d_geometry(beams, unit_scale=1.0)
        assert geometry.bounding_box["max_x"] == 5.0

        # Scale factor 1000.0 (default, meters → mm)
        geometry_mm = building_to_3d_geometry(beams, unit_scale=1000.0)
        assert geometry_mm.bounding_box["max_x"] == 5000.0


# =============================================================================
# StirrupLoop degenerate cases
# =============================================================================


class TestStirrupLoopDegenerate:
    """Degenerate cases for StirrupLoop."""

    def test_perimeter_single_point(self) -> None:
        """Single-point path should return 0 perimeter."""
        stirrup = StirrupLoop(
            position_x=0,
            path=[Point3D(0, 0, 0)],
            diameter=8.0,
        )
        assert stirrup.perimeter == 0.0

    def test_perimeter_two_points(self) -> None:
        """Two-point path should return distance × 2 (round trip)."""
        stirrup = StirrupLoop(
            position_x=0,
            path=[Point3D(0, 0, 0), Point3D(0, 100, 0)],
            diameter=8.0,
        )
        # Round trip: 100 + 100 = 200
        assert abs(stirrup.perimeter - 200.0) < 0.1

    def test_to_dict_with_empty_path(self) -> None:
        """to_dict with empty path should still serialize."""
        stirrup = StirrupLoop(position_x=500, path=[], diameter=8.0)
        d = stirrup.to_dict()
        assert d["positionX"] == 500.0
        assert d["path"] == []
        assert d["perimeter"] == 0.0


# =============================================================================
# RebarPath degenerate cases
# =============================================================================


class TestRebarPathDegenerate:
    """Degenerate cases for RebarPath."""

    def test_end_point_empty_segments(self) -> None:
        """Empty segments should return origin for end_point."""
        path = RebarPath("B1", [], 16.0)
        assert path.end_point == Point3D(0, 0, 0)

    def test_total_length_zero_length_segment(self) -> None:
        """Zero-length segment (same start/end) should give 0 total length."""
        seg = RebarSegment(
            Point3D(100, 50, 50),
            Point3D(100, 50, 50),
            16.0,
        )
        path = RebarPath("B1", [seg], 16.0)
        assert path.total_length == 0.0

    def test_multiple_zones(self) -> None:
        """RebarPath should correctly record zone attribute."""
        seg = RebarSegment(Point3D(0, 0, 50), Point3D(1000, 0, 50), 16.0)
        for zone in ("start", "mid", "end", "full"):
            path = RebarPath("B1", [seg], 16.0, zone=zone)
            assert path.zone == zone
            assert path.to_dict()["zone"] == zone


# =============================================================================
# beam_to_3d_geometry edge cases
# =============================================================================


class TestBeamTo3DGeometryEdgeCases:
    """Edge cases for beam_to_3d_geometry integration."""

    def test_seismic_vs_non_seismic(self) -> None:
        """Seismic flag should affect stirrup hook types only."""
        detailing = create_beam_detailing(
            beam_id="SEIS",
            story="GF",
            b=300,
            D=500,
            span=5000,
            cover=40,
            fck=25,
            fy=500,
            ast_start=900,
            ast_mid=900,
            ast_end=900,
        )
        geo_seismic = beam_to_3d_geometry(detailing, is_seismic=True)
        geo_normal = beam_to_3d_geometry(detailing, is_seismic=False)

        # Same rebars, different hook types
        assert len(geo_seismic.rebars) == len(geo_normal.rebars)
        assert all(s.hook_type == "135" for s in geo_seismic.stirrups)
        assert all(s.hook_type == "90" for s in geo_normal.stirrups)
        assert geo_seismic.metadata["isSeismic"] is True
        assert geo_normal.metadata["isSeismic"] is False

    def test_high_compression_steel(self) -> None:
        """Beam with Asc > Ast should still produce valid geometry."""
        detailing = create_beam_detailing(
            beam_id="HCS",
            story="1F",
            b=300,
            D=500,
            span=4000,
            cover=40,
            fck=25,
            fy=500,
            ast_start=600,
            ast_mid=600,
            ast_end=600,
            asc_start=900,
            asc_mid=900,
            asc_end=900,
        )
        geometry = beam_to_3d_geometry(detailing)
        top_bars = [r for r in geometry.rebars if r.bar_type == "top"]
        bottom_bars = [r for r in geometry.rebars if r.bar_type == "bottom"]
        assert len(top_bars) > 0
        assert len(bottom_bars) > 0

    def test_close_stirrup_spacing(self) -> None:
        """Very close stirrup spacing (50mm) should produce many stirrups."""
        detailing = create_beam_detailing(
            beam_id="CLOSE",
            story="GF",
            b=300,
            D=500,
            span=3000,
            cover=40,
            fck=25,
            fy=500,
            ast_start=900,
            ast_mid=900,
            ast_end=900,
            stirrup_spacing_start=50,
            stirrup_spacing_mid=75,
            stirrup_spacing_end=50,
        )
        geometry = beam_to_3d_geometry(detailing)
        # 3000mm span / ~63mm avg = ~47 stirrups expected
        assert len(geometry.stirrups) > 30

    def test_json_round_trip(self) -> None:
        """to_dict → JSON → parse should preserve structure."""
        detailing = create_beam_detailing(
            beam_id="RT",
            story="GF",
            b=300,
            D=450,
            span=4000,
            cover=40,
            fck=25,
            fy=500,
            ast_start=904,
            ast_mid=904,
            ast_end=904,
        )
        geometry = beam_to_3d_geometry(detailing)
        json_str = json.dumps(geometry.to_dict())
        parsed = json.loads(json_str)

        assert parsed["beamId"] == "RT"
        assert parsed["dimensions"]["b"] == 300
        assert parsed["version"] == "1.0.0"
        assert len(parsed["rebars"]) > 0
        assert len(parsed["stirrups"]) > 0
        assert parsed["metadata"]["cover"] == 40


# =============================================================================
# compute_rebar_positions error cases
# =============================================================================


class TestRebarPositionErrors:
    """Error case tests for compute_rebar_positions."""

    def test_negative_beam_width_raises(self) -> None:
        """Negative beam width should raise ValueError."""
        with pytest.raises(ValueError, match="positive"):
            compute_rebar_positions(
                beam_width=-300,
                beam_depth=450,
                cover=40,
                bar_count=2,
                bar_dia=16,
                stirrup_dia=8,
            )

    def test_zero_beam_depth_raises(self) -> None:
        """Zero beam depth should raise ValueError."""
        with pytest.raises(ValueError, match="positive"):
            compute_rebar_positions(
                beam_width=300,
                beam_depth=0,
                cover=40,
                bar_count=2,
                bar_dia=16,
                stirrup_dia=8,
            )

    def test_negative_cover_raises(self) -> None:
        """Negative cover should raise ValueError."""
        with pytest.raises(ValueError, match="non-negative"):
            compute_rebar_positions(
                beam_width=300,
                beam_depth=450,
                cover=-10,
                bar_count=2,
                bar_dia=16,
                stirrup_dia=8,
            )

    def test_zero_bar_dia_raises(self) -> None:
        """Zero bar diameter should raise ValueError."""
        with pytest.raises(ValueError, match="positive"):
            compute_rebar_positions(
                beam_width=300,
                beam_depth=450,
                cover=40,
                bar_count=2,
                bar_dia=0,
                stirrup_dia=8,
            )

    def test_zero_stirrup_dia_raises(self) -> None:
        """Zero stirrup diameter should raise ValueError."""
        with pytest.raises(ValueError, match="positive"):
            compute_rebar_positions(
                beam_width=300,
                beam_depth=450,
                cover=40,
                bar_count=2,
                bar_dia=16,
                stirrup_dia=0,
            )


# =============================================================================
# compute_beam_outline edge cases
# =============================================================================


class TestBeamOutlineEdgeCases:
    """Edge case tests for compute_beam_outline."""

    def test_very_small_beam(self) -> None:
        """Very small beam (100×200×500mm) should produce valid outline."""
        corners = compute_beam_outline(100, 200, 500)
        assert len(corners) == 8
        y_vals = [c.y for c in corners]
        assert min(y_vals) == -50
        assert max(y_vals) == 50

    def test_very_large_beam(self) -> None:
        """Very large beam (1000×2000×20000mm) should produce valid outline."""
        corners = compute_beam_outline(1000, 2000, 20000)
        assert len(corners) == 8
        assert max(c.x for c in corners) == 20000
        assert max(c.z for c in corners) == 2000

    def test_square_beam(self) -> None:
        """Square cross-section beam should work."""
        corners = compute_beam_outline(400, 400, 5000)
        z_vals = [c.z for c in corners]
        assert max(z_vals) == 400
