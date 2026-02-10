# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for building_to_3d_geometry."""

from __future__ import annotations

from structural_lib.core.models import (
    BeamGeometry,
    FrameType,
    Point3D,
    SectionProperties,
)
from structural_lib.visualization.geometry_3d import building_to_3d_geometry


def test_building_to_3d_geometry_basic() -> None:
    section = SectionProperties(width_mm=300, depth_mm=500, fck_mpa=25, fy_mpa=500)
    beams = [
        BeamGeometry(
            id="B1",
            label="B1",
            story="L1",
            frame_type=FrameType.BEAM,
            point1=Point3D(x=0.0, y=0.0, z=0.0),
            point2=Point3D(x=5.0, y=0.0, z=0.0),
            section=section,
            angle=0.0,
        ),
        BeamGeometry(
            id="B2",
            label="B2",
            story="L1",
            frame_type=FrameType.BEAM,
            point1=Point3D(x=0.0, y=0.0, z=3.0),
            point2=Point3D(x=5.0, y=0.0, z=3.0),
            section=section,
            angle=0.0,
        ),
    ]

    geometry = building_to_3d_geometry(beams, unit_scale=1000.0)

    assert len(geometry.beams) == 2
    assert geometry.bounding_box["max_x"] == 5000.0
    assert geometry.bounding_box["max_z"] == 3000.0
