# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tests for visualizations_3d module — Plotly 3D mesh generation.

Run: cd Python && pytest ../tests/test_visualizations_3d.py -v
"""

from __future__ import annotations

import math
import sys
import time
from pathlib import Path

import pytest

# Add streamlit_app to path for imports
streamlit_app_dir = Path(__file__).parent.parent / "streamlit_app"
sys.path.insert(0, str(streamlit_app_dir))

from components.visualizations_3d import (
    create_beam_3d_figure,
    create_beam_3d_from_dict,
    generate_box_mesh,
    generate_cylinder_mesh,
    generate_stirrup_tube,
    compute_geometry_hash,
    COLORS,
)


class TestGenerateCylinderMesh:
    """Tests for generate_cylinder_mesh function."""

    def test_basic_cylinder_creation(self):
        """Test that a cylinder mesh is created with correct structure."""
        mesh = generate_cylinder_mesh(
            start=(0, 0, 0),
            end=(100, 0, 0),
            radius=5,
            color="#ff0000",
        )

        # Check mesh has vertices
        assert len(mesh.x) > 0
        assert len(mesh.y) > 0
        assert len(mesh.z) > 0

        # Check face indices exist
        assert len(mesh.i) > 0
        assert len(mesh.j) > 0
        assert len(mesh.k) > 0

    def test_cylinder_along_x_axis(self):
        """Test cylinder aligned with X axis."""
        mesh = generate_cylinder_mesh(
            start=(0, 0, 0),
            end=(1000, 0, 0),
            radius=8,
            color="#e53935",
        )

        # End points should be at x=0 and x=1000
        assert min(mesh.x) >= -10  # Allow for radius
        assert max(mesh.x) <= 1010

    def test_cylinder_diagonal(self):
        """Test cylinder at diagonal orientation."""
        mesh = generate_cylinder_mesh(
            start=(0, 0, 0),
            end=(100, 100, 100),
            radius=5,
            color="#1e88e5",
        )

        # Mesh should have proper vertices
        assert len(mesh.x) > 30  # Multiple vertices for caps

    def test_cylinder_zero_length(self):
        """Test that zero-length cylinder returns empty mesh."""
        mesh = generate_cylinder_mesh(
            start=(50, 50, 50),
            end=(50, 50, 50),
            radius=5,
            color="#ff0000",
        )

        # Should return empty mesh
        assert len(mesh.x) == 0

    def test_cylinder_resolution(self):
        """Test that resolution affects vertex count."""
        mesh_low = generate_cylinder_mesh(
            start=(0, 0, 0),
            end=(100, 0, 0),
            radius=5,
            color="#ff0000",
            resolution=8,
        )

        mesh_high = generate_cylinder_mesh(
            start=(0, 0, 0),
            end=(100, 0, 0),
            radius=5,
            color="#ff0000",
            resolution=32,
        )

        # Higher resolution = more vertices
        assert len(mesh_high.x) > len(mesh_low.x)


class TestGenerateBoxMesh:
    """Tests for generate_box_mesh function."""

    def test_basic_box_creation(self):
        """Test that a box mesh is created."""
        mesh = generate_box_mesh(
            width=300,
            depth=450,
            span=4000,
        )

        # Box has 8 vertices
        assert len(mesh.x) == 8
        assert len(mesh.y) == 8
        assert len(mesh.z) == 8

    def test_box_dimensions(self):
        """Test that box respects dimensions."""
        mesh = generate_box_mesh(
            width=300,
            depth=450,
            span=4000,
        )

        # X range: 0 to span
        assert min(mesh.x) == 0
        assert max(mesh.x) == 4000

        # Y range: -width/2 to +width/2
        assert min(mesh.y) == -150
        assert max(mesh.y) == 150

        # Z range: 0 to depth
        assert min(mesh.z) == 0
        assert max(mesh.z) == 450

    def test_box_opacity(self):
        """Test box opacity setting."""
        mesh = generate_box_mesh(
            width=300,
            depth=450,
            span=4000,
            opacity=0.5,
        )

        assert mesh.opacity == 0.5


class TestGenerateStirrupTube:
    """Tests for generate_stirrup_tube function."""

    def test_stirrup_creation(self):
        """Test that stirrup tube segments are created."""
        corners = [
            (100, -106, 44),
            (100, 106, 44),
            (100, 106, 406),
            (100, -106, 406),
        ]

        meshes = generate_stirrup_tube(
            position_x=100,
            corners=corners,
            radius=4,
        )

        # Should have 4 segments (one per side of rectangle)
        assert len(meshes) == 4

    def test_stirrup_segment_connectivity(self):
        """Test that stirrup segments connect properly."""
        corners = [
            (100, -50, 50),
            (100, 50, 50),
            (100, 50, 150),
            (100, -50, 150),
        ]

        meshes = generate_stirrup_tube(
            position_x=100,
            corners=corners,
            radius=4,
        )

        # Each segment should have vertices
        for mesh in meshes:
            assert len(mesh.x) > 0


class TestCreateBeam3dFigure:
    """Tests for create_beam_3d_figure function."""

    def test_basic_figure_creation(self):
        """Test that a figure is created with default parameters."""
        fig = create_beam_3d_figure(
            b=300,
            D=450,
            span=4000,
        )

        # Should have multiple traces
        assert len(fig.data) > 0

        # Should have proper layout
        assert fig.layout.scene.xaxis.title.text == "Span (mm)"
        assert fig.layout.scene.yaxis.title.text == "Width (mm)"
        assert fig.layout.scene.zaxis.title.text == "Depth (mm)"

    def test_figure_with_custom_bars(self):
        """Test figure with custom bar positions."""
        bottom_bars = [
            (0, -96, 52),
            (0, 0, 52),
            (0, 96, 52),
        ]

        fig = create_beam_3d_figure(
            b=300,
            D=450,
            span=4000,
            bottom_bars=bottom_bars,
        )

        # Should include bar meshes
        assert len(fig.data) > 5

    def test_figure_with_custom_stirrups(self):
        """Test figure with custom stirrup positions."""
        stirrup_positions = [100, 200, 300, 400, 500]

        fig = create_beam_3d_figure(
            b=300,
            D=450,
            span=4000,
            stirrup_positions=stirrup_positions,
        )

        # Should have many traces (concrete + bars + stirrup segments)
        assert len(fig.data) > 10

    def test_figure_height_setting(self):
        """Test that figure height is set correctly."""
        fig = create_beam_3d_figure(
            b=300,
            D=450,
            span=4000,
            height=700,
        )

        assert fig.layout.height == 700

    def test_figure_legend_control(self):
        """Test legend visibility control."""
        fig_with_legend = create_beam_3d_figure(
            b=300,
            D=450,
            span=4000,
            show_legend=True,
        )

        fig_without_legend = create_beam_3d_figure(
            b=300,
            D=450,
            span=4000,
            show_legend=False,
        )

        assert fig_with_legend.layout.showlegend is True
        assert fig_without_legend.layout.showlegend is False


class TestCreateBeam3dFromDict:
    """Tests for create_beam_3d_from_dict function."""

    def test_from_dict_basic(self):
        """Test creating figure from basic dict."""
        geometry_dict = {
            "dimensions": {"b": 300, "D": 450, "span": 4000},
            "rebars": [],
            "stirrups": [],
            "metadata": {"cover": 40},
        }

        fig = create_beam_3d_from_dict(geometry_dict)

        assert len(fig.data) > 0

    def test_from_dict_with_rebars(self):
        """Test creating figure from dict with rebar data."""
        geometry_dict = {
            "dimensions": {"b": 300, "D": 450, "span": 4000},
            "rebars": [
                {
                    "barId": "B1",
                    "barType": "bottom",
                    "diameter": 16,
                    "segments": [
                        {
                            "start": {"x": 0, "y": -96, "z": 52},
                            "end": {"x": 4000, "y": -96, "z": 52},
                        }
                    ],
                },
                {
                    "barId": "T1",
                    "barType": "top",
                    "diameter": 12,
                    "segments": [
                        {
                            "start": {"x": 0, "y": -96, "z": 398},
                            "end": {"x": 4000, "y": -96, "z": 398},
                        }
                    ],
                },
            ],
            "stirrups": [],
            "metadata": {"cover": 40},
        }

        fig = create_beam_3d_from_dict(geometry_dict)

        # Should have concrete + bars
        assert len(fig.data) > 3


class TestComputeGeometryHash:
    """Tests for compute_geometry_hash function."""

    def test_hash_consistency(self):
        """Test that same input produces same hash."""
        geometry = {
            "dimensions": {"b": 300, "D": 450, "span": 4000},
            "rebars": [],
            "stirrups": [],
        }

        hash1 = compute_geometry_hash(geometry)
        hash2 = compute_geometry_hash(geometry)

        assert hash1 == hash2

    def test_hash_changes_with_dimensions(self):
        """Test that different dimensions produce different hash."""
        geom1 = {
            "dimensions": {"b": 300, "D": 450, "span": 4000},
            "rebars": [],
            "stirrups": [],
        }

        geom2 = {
            "dimensions": {"b": 350, "D": 450, "span": 4000},
            "rebars": [],
            "stirrups": [],
        }

        hash1 = compute_geometry_hash(geom1)
        hash2 = compute_geometry_hash(geom2)

        assert hash1 != hash2

    def test_hash_length(self):
        """Test that hash is proper MD5 length."""
        geometry = {
            "dimensions": {"b": 300, "D": 450, "span": 4000},
            "rebars": [],
            "stirrups": [],
        }

        hash_val = compute_geometry_hash(geometry)

        assert len(hash_val) == 32  # MD5 hex length


class TestPerformance:
    """Performance benchmarks for mesh generation."""

    def test_simple_figure_performance(self):
        """Test that simple figure generation is fast (<150ms).

        Note: Threshold set at 150ms to account for CI variability.
        Typical local performance is 50-100ms.
        """
        # Warm-up call to ensure imports and JIT are ready
        _ = create_beam_3d_figure(b=300, D=450, span=1000)

        start = time.time()

        fig = create_beam_3d_figure(
            b=300,
            D=450,
            span=4000,
        )

        elapsed_ms = (time.time() - start) * 1000

        # Should complete in under 150ms (with CI headroom)
        assert elapsed_ms < 150, f"Figure generation took {elapsed_ms:.1f}ms"

    def test_complex_figure_performance(self):
        """Test that complex figure (many stirrups) is under 500ms."""
        start = time.time()

        fig = create_beam_3d_figure(
            b=300,
            D=450,
            span=8000,
            bottom_bars=[
                (0, -96, 52),
                (0, -32, 52),
                (0, 32, 52),
                (0, 96, 52),
            ],
            top_bars=[
                (0, -96, 398),
                (0, 96, 398),
            ],
            stirrup_positions=list(range(50, 8000, 100)),  # 80 stirrups
        )

        elapsed_ms = (time.time() - start) * 1000

        # Should complete in under 500ms
        assert elapsed_ms < 500, f"Complex figure took {elapsed_ms:.1f}ms"

    def test_cylinder_mesh_performance(self):
        """Test that single cylinder mesh is very fast (<5ms)."""
        start = time.time()

        for _ in range(10):
            mesh = generate_cylinder_mesh(
                start=(0, 0, 0),
                end=(4000, 0, 0),
                radius=8,
                color="#e53935",
            )

        elapsed_ms = (time.time() - start) * 1000 / 10

        # Should be under 5ms per cylinder
        assert elapsed_ms < 5, f"Cylinder generation took {elapsed_ms:.1f}ms"

    def test_geometry_hash_performance(self):
        """Test that geometry hash is very fast (<1ms)."""
        geometry = {
            "dimensions": {"b": 300, "D": 450, "span": 4000},
            "rebars": [{"segments": [{"start": {"y": i, "z": 52}}]} for i in range(10)],
            "stirrups": [{"positionX": i * 100} for i in range(40)],
        }

        start = time.time()

        for _ in range(100):
            hash_val = compute_geometry_hash(geometry)

        elapsed_ms = (time.time() - start) * 1000 / 100

        # Should be under 1ms per hash
        assert elapsed_ms < 1, f"Hash computation took {elapsed_ms:.2f}ms"


class TestColors:
    """Tests for color constants."""

    def test_colors_defined(self):
        """Test that all expected colors are defined."""
        assert "concrete" in COLORS
        assert "rebar_bottom" in COLORS
        assert "rebar_top" in COLORS
        assert "stirrup" in COLORS
        assert "background" in COLORS

    def test_color_format(self):
        """Test that colors are valid format (hex or rgba)."""
        for name, color in COLORS.items():
            # Either starts with # (hex) or rgba
            is_hex = color.startswith("#")
            is_rgba = color.startswith("rgba")
            assert is_hex or is_rgba, f"Invalid color format for {name}: {color}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
