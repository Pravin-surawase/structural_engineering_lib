# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tests for visualization_export module — PyVista CAD export functionality.

This module tests the CAD export functions without requiring PyVista
to be installed, using mocking where necessary.

Run: pytest tests/test_visualization_export.py -v
"""

from __future__ import annotations

from pathlib import Path
import importlib.util

import pytest

# Path to the module under test
streamlit_app_dir = Path(__file__).parent.parent / "streamlit_app"


@pytest.fixture(scope="module")
def viz_module():
    """Import the module directly without going through __init__.py."""
    spec = importlib.util.spec_from_file_location(
        "visualization_export",
        streamlit_app_dir / "components" / "visualization_export.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestCheckPyvistaAvailable:
    """Tests for check_pyvista_available function."""

    def test_check_returns_boolean(self, viz_module):
        """Test that check always returns a boolean."""
        result = viz_module.check_pyvista_available()
        assert isinstance(result, bool)


class TestGeometryConversion:
    """Tests for geometry to mesh conversion functions."""

    def test_geometry_empty_raises_without_pyvista(self, viz_module):
        """Test that ImportError is raised when PyVista not installed."""
        if viz_module.check_pyvista_available():
            pytest.skip("Test requires PyVista NOT to be installed")
        with pytest.raises(ImportError):
            viz_module.geometry_to_pyvista_meshes({})

    def test_geometry_with_beams_structure(self, viz_module):
        """Test geometry with beams."""
        if not viz_module.check_pyvista_available():
            pytest.skip("PyVista not installed")
        geometry = {
            "beams": [
                {
                    "id": "B1",
                    "start": [0, 0, 0],
                    "end": [3000, 0, 0],
                    "width": 300,
                    "depth": 500,
                }
            ]
        }

        result = viz_module.geometry_to_pyvista_meshes(geometry)
        # Should return list
        assert isinstance(result, list)


class TestExportFunctions:
    """Tests for export functions (STL, VTK, screenshot)."""

    def test_export_stl_raises_without_pyvista(self, viz_module):
        """Test STL export raises without PyVista."""
        if viz_module.check_pyvista_available():
            pytest.skip("Test requires PyVista NOT to be installed")
        with pytest.raises(ImportError):
            viz_module.export_beam_stl({"beams": []}, "/tmp/test.stl")

    def test_export_vtk_raises_without_pyvista(self, viz_module):
        """Test VTK export raises without PyVista."""
        if viz_module.check_pyvista_available():
            pytest.skip("Test requires PyVista NOT to be installed")
        with pytest.raises(ImportError):
            viz_module.export_beam_vtk({"beams": []}, "/tmp/test.vtk")

    def test_render_screenshot_raises_without_pyvista(self, viz_module, tmp_path):
        """Test screenshot raises without PyVista."""
        if viz_module.check_pyvista_available():
            pytest.skip("Test requires PyVista NOT to be installed")
        output_path = tmp_path / "test.png"
        with pytest.raises(ImportError):
            viz_module.render_beam_screenshot({"beams": []}, str(output_path))


class TestExportResolutionOptions:
    """Tests for export resolution configuration."""

    def test_screenshot_resolutions_exist(self, viz_module):
        """Test that resolution options are valid."""
        resolutions = viz_module.SCREENSHOT_RESOLUTIONS

        assert "HD" in resolutions
        assert "Full HD" in resolutions
        assert "4K" in resolutions

    def test_resolution_values_are_tuples(self, viz_module):
        """Test resolution values are (width, height) tuples."""
        for name, res in viz_module.SCREENSHOT_RESOLUTIONS.items():
            assert isinstance(res, tuple)
            assert len(res) == 2
            width, height = res
            assert width > 0
            assert height > 0


class TestMaterialConfigurations:
    """Tests for material and rendering configurations."""

    def test_default_materials_defined(self, viz_module):
        """Test that default materials are properly defined."""
        materials = viz_module.DEFAULT_MATERIALS

        assert "concrete" in materials
        assert "rebar" in materials

    def test_materials_have_required_properties(self, viz_module):
        """Test materials have required PBR properties."""
        for name, props in viz_module.DEFAULT_MATERIALS.items():
            assert "color" in props
            assert "metallic" in props
            assert "roughness" in props


class TestBeamBoxGeneration:
    """Tests for beam box mesh generation helpers."""

    def test_create_beam_box_returns_mesh_or_none(self, viz_module):
        """Test beam box creation returns mesh or None."""
        result = viz_module._create_beam_box(
            start=[0, 0, 0],
            end=[3000, 0, 0],
            width=300,
            depth=500,
        )
        # Returns mesh (if PyVista available) or None
        assert result is None or hasattr(result, "n_points")

    def test_create_beam_box_zero_length_returns_none(self, viz_module):
        """Test beam box with zero length returns None."""
        result = viz_module._create_beam_box(
            start=[0, 0, 0],
            end=[0, 0, 0],
            width=300,
            depth=500,
        )
        assert result is None

    def test_create_beam_box_negative_width_returns_none(self, viz_module):
        """Test beam box with negative dimensions returns None."""
        result = viz_module._create_beam_box(
            start=[0, 0, 0],
            end=[3000, 0, 0],
            width=-300,
            depth=500,
        )
        assert result is None


class TestPyVistaPlotterConfiguration:
    """Tests for PyVista plotter configuration."""

    def test_create_plotter_raises_without_pyvista(self, viz_module):
        """Test plotter creation raises without PyVista."""
        if viz_module.check_pyvista_available():
            pytest.skip("Test requires PyVista NOT to be installed")
        with pytest.raises(ImportError):
            viz_module.create_pyvista_plotter([])


class TestIntegration:
    """Tests for integration with main visualization."""

    def test_accepts_standard_geometry_format(self, viz_module):
        """Test that standard geometry format is accepted."""
        if not viz_module.check_pyvista_available():
            pytest.skip("PyVista not installed")
        geometry = {
            "beams": [
                {
                    "id": "B1",
                    "start": [0, 0, 0],
                    "end": [3000, 0, 0],
                    "width": 300,
                    "depth": 500,
                    "level": 0,
                    "story": "Ground",
                }
            ],
            "columns": [],
            "slabs": [],
        }

        result = viz_module.geometry_to_pyvista_meshes(geometry)
        assert isinstance(result, list)


# =============================================================================
# Conditional tests that only run if PyVista is installed
# =============================================================================


@pytest.fixture
def pyvista_available(viz_module):
    """Skip test if PyVista is not installed."""
    if not viz_module.check_pyvista_available():
        pytest.skip("PyVista not installed")
    return True


class TestPyVistaIntegration:
    """Tests that only run when PyVista is available."""

    def test_actual_mesh_creation(self, viz_module, pyvista_available):
        """Test actual mesh creation with PyVista."""
        result = viz_module._create_beam_box(
            start=[0, 0, 0],
            end=[3000, 0, 0],
            width=300,
            depth=500,
        )

        assert result is not None
        assert result.n_points > 0
        assert result.n_cells > 0

    def test_stl_export_creates_file(self, viz_module, pyvista_available, tmp_path):
        """Test that STL export creates a valid file."""
        geometry = {
            "beams": [
                {
                    "id": "B1",
                    "start": [0, 0, 0],
                    "end": [3000, 0, 0],
                    "width": 300,
                    "depth": 500,
                }
            ]
        }

        output_path = tmp_path / "test.stl"
        result = viz_module.export_beam_stl(geometry, str(output_path))

        assert result is True
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_vtk_export_creates_file(self, viz_module, pyvista_available, tmp_path):
        """Test that VTK export creates a valid file."""
        geometry = {
            "beams": [
                {
                    "id": "B1",
                    "start": [0, 0, 0],
                    "end": [3000, 0, 0],
                    "width": 300,
                    "depth": 500,
                }
            ]
        }

        output_path = tmp_path / "test.vtk"
        result = viz_module.export_beam_vtk(geometry, str(output_path))

        assert result is True
        assert output_path.exists()
        assert output_path.stat().st_size > 0
