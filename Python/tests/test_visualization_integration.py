# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Integration tests for visualization.geometry_3d with detailing module.

These tests verify the beam_to_3d_geometry() function correctly converts
BeamDetailingResult to Beam3DGeometry for visualization.
"""

from __future__ import annotations

import pytest

from structural_lib.codes.is456.detailing import create_beam_detailing
from structural_lib.visualization.geometry_3d import (
    Beam3DGeometry,
    beam_to_3d_geometry,
)


class TestBeamTo3DGeometryIntegration:
    """Integration tests for beam_to_3d_geometry with real BeamDetailingResult."""

    @pytest.fixture
    def sample_detailing(self):
        """Create a sample BeamDetailingResult for testing."""
        return create_beam_detailing(
            beam_id="B1",
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
            asc_start=226,
            asc_mid=226,
            asc_end=226,
            stirrup_dia=8,
            stirrup_spacing_start=100,
            stirrup_spacing_mid=150,
            stirrup_spacing_end=100,
            is_seismic=True,
        )

    def test_basic_conversion(self, sample_detailing):
        """Test basic conversion from BeamDetailingResult to Beam3DGeometry."""
        geometry = beam_to_3d_geometry(sample_detailing)

        assert isinstance(geometry, Beam3DGeometry)
        assert geometry.beam_id == "B1"
        assert geometry.story == "GF"
        assert geometry.dimensions["b"] == 300
        assert geometry.dimensions["D"] == 450
        assert geometry.dimensions["span"] == 4000

    def test_concrete_outline(self, sample_detailing):
        """Test concrete outline has 8 corners."""
        geometry = beam_to_3d_geometry(sample_detailing)

        assert len(geometry.concrete_outline) == 8
        # Check Z range (bottom to top)
        z_values = [p.z for p in geometry.concrete_outline]
        assert min(z_values) == 0
        assert max(z_values) == 450
        # Check X range (0 to span)
        x_values = [p.x for p in geometry.concrete_outline]
        assert min(x_values) == 0
        assert max(x_values) == 4000

    def test_rebars_generated(self, sample_detailing):
        """Test rebars are generated from detailing."""
        geometry = beam_to_3d_geometry(sample_detailing)

        # Should have both top and bottom bars
        assert len(geometry.rebars) > 0

        bottom_rebars = [r for r in geometry.rebars if r.bar_type == "bottom"]
        top_rebars = [r for r in geometry.rebars if r.bar_type == "top"]
        assert bottom_rebars
        assert top_rebars

        expected_bottom = max(arr.count for arr in sample_detailing.bottom_bars)
        expected_top = max(arr.count for arr in sample_detailing.top_bars)
        assert len(bottom_rebars) == expected_bottom
        assert len(top_rebars) == expected_top

        # Check bar IDs are unique
        bar_ids = [r.bar_id for r in geometry.rebars]
        assert len(bar_ids) == len(set(bar_ids))

    def test_stirrups_generated(self, sample_detailing):
        """Test stirrups are generated along span."""
        geometry = beam_to_3d_geometry(sample_detailing)

        assert len(geometry.stirrups) > 0

        # Check stirrups are along span
        x_positions = [s.position_x for s in geometry.stirrups]
        assert all(0 < x < 4000 for x in x_positions)

        # Check stirrups are sorted by X
        assert x_positions == sorted(x_positions)

    def test_seismic_hook_type(self, sample_detailing):
        """Test seismic detailing uses 135° hooks."""
        geometry = beam_to_3d_geometry(sample_detailing, is_seismic=True)

        # All stirrups should have 135° hooks
        for stirrup in geometry.stirrups:
            assert stirrup.hook_type == "135"

    def test_non_seismic_hook_type(self, sample_detailing):
        """Test non-seismic detailing uses 90° hooks."""
        geometry = beam_to_3d_geometry(sample_detailing, is_seismic=False)

        for stirrup in geometry.stirrups:
            assert stirrup.hook_type == "90"

    def test_metadata_populated(self, sample_detailing):
        """Test metadata is populated from detailing."""
        geometry = beam_to_3d_geometry(sample_detailing, is_seismic=True)

        assert geometry.metadata["cover"] == 40
        assert geometry.metadata["ldTension"] > 0
        assert geometry.metadata["ldCompression"] > 0
        assert geometry.metadata["lapLength"] > 0
        assert geometry.metadata["isSeismic"] is True
        assert geometry.metadata["isValid"] is True

    def test_to_dict_produces_valid_json(self, sample_detailing):
        """Test to_dict() produces JSON-serializable output."""
        import json

        geometry = beam_to_3d_geometry(sample_detailing)
        json_str = json.dumps(geometry.to_dict())

        # Should be parseable JSON
        parsed = json.loads(json_str)
        assert parsed["beamId"] == "B1"
        assert parsed["version"] == "1.0.0"

    def test_to_3d_json_method(self, sample_detailing):
        """Test BeamDetailingResult.to_3d_json() convenience method."""
        payload = sample_detailing.to_3d_json(is_seismic=True)

        assert payload["beamId"] == "B1"
        assert payload["metadata"]["isSeismic"] is True

    def test_json_schema_compliance(self, sample_detailing):
        """Test JSON output matches BeamGeometry3D schema."""
        geometry = beam_to_3d_geometry(sample_detailing)
        d = geometry.to_dict()

        # Required top-level fields
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

        # Rebar structure
        if d["rebars"]:
            rebar = d["rebars"][0]
            assert "barId" in rebar
            assert "segments" in rebar
            assert "diameter" in rebar
            assert "barType" in rebar

            if rebar["segments"]:
                seg = rebar["segments"][0]
                assert "start" in seg
                assert "end" in seg
                assert "x" in seg["start"]
                assert "y" in seg["start"]
                assert "z" in seg["start"]

        # Stirrup structure
        if d["stirrups"]:
            stirrup = d["stirrups"][0]
            assert "positionX" in stirrup
            assert "path" in stirrup
            assert "diameter" in stirrup
            assert "legs" in stirrup


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_minimal_beam(self):
        """Test with minimal beam dimensions."""
        detailing = create_beam_detailing(
            beam_id="MIN",
            story="TEST",
            b=200,
            D=300,
            span=2000,
            cover=25,
            fck=20,
            fy=415,
            ast_start=226,
            ast_mid=226,
            ast_end=226,
        )

        geometry = beam_to_3d_geometry(detailing)
        assert geometry.beam_id == "MIN"
        assert len(geometry.concrete_outline) == 8
        assert len(geometry.stirrups) > 0

    def test_large_beam(self):
        """Test with large beam dimensions."""
        detailing = create_beam_detailing(
            beam_id="LARGE",
            story="TEST",
            b=600,
            D=900,
            span=10000,
            cover=50,
            fck=40,
            fy=500,
            ast_start=2500,
            ast_mid=2500,
            ast_end=2500,
        )

        geometry = beam_to_3d_geometry(detailing)
        assert geometry.beam_id == "LARGE"
        assert geometry.dimensions["span"] == 10000
        # Should have more stirrups for longer span
        assert len(geometry.stirrups) > 30
