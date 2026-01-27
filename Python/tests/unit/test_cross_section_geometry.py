# SPDX-License-Identifier: MIT
"""Tests for cross_section_geometry."""

from structural_lib.visualization.geometry_3d import cross_section_geometry


def test_cross_section_geometry_basic() -> None:
    geometry = cross_section_geometry(
        beam_width=300.0,
        beam_depth=500.0,
        cover=40.0,
        bar_count=3,
        bar_dia=16.0,
        stirrup_dia=8.0,
        is_top=False,
        layers=1,
    )

    data = geometry.to_dict()
    assert data["width_mm"] == 300.0
    assert data["depth_mm"] == 500.0
    assert len(data["bars"]) == 3
    assert len(data["outline"]) >= 4
