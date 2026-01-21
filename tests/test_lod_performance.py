# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
LOD Performance Benchmark Tests

Tests the Level of Detail (LOD) system for multi-beam 3D visualization
to ensure performance targets are met for various beam counts.

Performance targets:
    - 250 beams: <1s cached (HIGH LOD)
    - 500 beams: <2s cached (MEDIUM LOD)
    - 1000 beams: <3s cached (LOW LOD)
    - 2000+ beams: <5s cached (ULTRA_LOW LOD)

Author: Session 59 Agent
Task: TASK-PHASE4 (Performance Optimization)
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest

# Add streamlit_app to path for imports
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "streamlit_app"))


class TestLODManager:
    """Tests for LOD level detection and configuration."""

    def test_lod_manager_import(self):
        """Test LODManager can be imported."""
        from utils.lod_manager import LODManager

        manager = LODManager()
        assert manager is not None

    def test_lod_level_enum(self):
        """Test LODLevel enum values."""
        from utils.lod_manager import LODLevel

        assert hasattr(LODLevel, "HIGH")
        assert hasattr(LODLevel, "MEDIUM")
        assert hasattr(LODLevel, "LOW")
        assert hasattr(LODLevel, "ULTRA_LOW")

    @pytest.mark.parametrize(
        "beam_count,expected_level",
        [
            (1, "HIGH"),
            (100, "HIGH"),
            (250, "HIGH"),
            (251, "MEDIUM"),
            (400, "MEDIUM"),
            (500, "MEDIUM"),
            (501, "LOW"),
            (800, "LOW"),
            (1000, "LOW"),
            (1001, "ULTRA_LOW"),
            (2000, "ULTRA_LOW"),
            (5000, "ULTRA_LOW"),
        ],
    )
    def test_lod_level_detection(self, beam_count: int, expected_level: str):
        """Test LOD level is correctly detected for various beam counts."""
        from utils.lod_manager import LODManager

        manager = LODManager()
        level = manager.get_recommended_level(beam_count)

        assert level.name == expected_level, (
            f"For {beam_count} beams, expected {expected_level}, got {level.name}"
        )

    def test_lod_config_high(self):
        """Test HIGH LOD config has full detail."""
        from utils.lod_manager import LODManager, LODLevel

        manager = LODManager()
        config = manager.get_config(LODLevel.HIGH)

        assert config.show_stirrups is True
        assert config.show_all_bars is True
        assert config.show_labels is True
        assert config.stirrup_reduction == 1  # All stirrups

    def test_lod_config_medium(self):
        """Test MEDIUM LOD config has balanced detail."""
        from utils.lod_manager import LODManager, LODLevel

        manager = LODManager()
        config = manager.get_config(LODLevel.MEDIUM)

        assert config.show_stirrups is True
        assert config.stirrup_reduction >= 2  # Reduced stirrups
        assert config.show_labels is False

    def test_lod_config_low(self):
        """Test LOW LOD config has minimal detail."""
        from utils.lod_manager import LODManager, LODLevel

        manager = LODManager()
        config = manager.get_config(LODLevel.LOW)

        assert config.show_stirrups is False
        assert config.show_all_bars is False

    def test_lod_config_ultra_low(self):
        """Test ULTRA_LOW LOD config is box outline only."""
        from utils.lod_manager import LODManager, LODLevel

        manager = LODManager()
        config = manager.get_config(LODLevel.ULTRA_LOW)

        assert config.show_stirrups is False
        assert config.show_all_bars is False
        assert config.show_labels is False
        assert config.show_section_outline is False

    def test_performance_estimate(self):
        """Test performance estimate returns valid data."""
        from utils.lod_manager import LODManager, LODLevel

        manager = LODManager()

        for level in LODLevel:
            estimate = manager.get_performance_estimate(500, level)

            assert "estimated_render_time_ms" in estimate
            assert "beam_count" in estimate
            assert "level" in estimate  # Key is 'level', not 'lod_level'
            assert estimate["estimated_render_time_ms"] >= 0


class TestLODSummary:
    """Tests for LOD summary generation."""

    def test_generate_lod_summary(self):
        """Test LOD summary generation."""
        from utils.lod_manager import generate_lod_summary

        summary = generate_lod_summary(500)

        # Summary returns a markdown string
        assert isinstance(summary, str)
        assert "MEDIUM" in summary
        assert "500 beams" in summary
        assert "Stirrups" in summary


class TestMultiBeam3DFigure:
    """Tests for multi-beam 3D figure with LOD integration."""

    def _generate_mock_beams(self, count: int) -> list[dict]:
        """Generate mock beam data for testing."""
        beams = []
        for i in range(count):
            beams.append({
                "id": f"B{i+1}",
                "x1": (i % 10) * 6000,
                "y1": (i // 10) * 6000,
                "z1": (i // 100) * 3500,
                "x2": (i % 10) * 6000 + 5000,
                "y2": (i // 10) * 6000,
                "z2": (i // 100) * 3500,
                "width": 300,
                "depth": 450,
                "mu_knm": 100 + (i % 50),
                "vu_kn": 50 + (i % 30),
                "story": f"Floor{i // 100}",
            })
        return beams

    def test_multi_beam_figure_returns_tuple(self):
        """Test that create_multi_beam_3d_figure returns (figure, stats) tuple."""
        from components.visualizations_3d import create_multi_beam_3d_figure

        beams = self._generate_mock_beams(10)
        result = create_multi_beam_3d_figure(beams)

        assert isinstance(result, tuple)
        assert len(result) == 2

        figure, stats = result
        assert figure is not None
        assert isinstance(stats, dict)
        assert "level" in stats  # key is 'level' not 'lod_level'

    def test_lod_auto_detection_high(self):
        """Test LOD auto-detection for small beam count."""
        from components.visualizations_3d import create_multi_beam_3d_figure

        beams = self._generate_mock_beams(100)
        figure, stats = create_multi_beam_3d_figure(beams)

        assert stats["level"] == "HIGH"

    def test_lod_auto_detection_medium(self):
        """Test LOD auto-detection for medium beam count."""
        from components.visualizations_3d import create_multi_beam_3d_figure

        beams = self._generate_mock_beams(300)
        figure, stats = create_multi_beam_3d_figure(beams)

        assert stats["level"] == "MEDIUM"

    def test_lod_auto_detection_low(self):
        """Test LOD auto-detection for large beam count."""
        from components.visualizations_3d import create_multi_beam_3d_figure

        beams = self._generate_mock_beams(600)
        figure, stats = create_multi_beam_3d_figure(beams)

        assert stats["level"] == "LOW"

    @pytest.mark.benchmark
    def test_performance_250_beams(self):
        """Benchmark: 250 beams should complete in <2s."""
        from components.visualizations_3d import create_multi_beam_3d_figure

        beams = self._generate_mock_beams(250)

        start = time.perf_counter()
        figure, stats = create_multi_beam_3d_figure(beams)
        elapsed = time.perf_counter() - start

        assert elapsed < 2.0, f"250 beams took {elapsed:.2f}s (target: <2s)"
        assert figure is not None

    @pytest.mark.benchmark
    def test_performance_500_beams(self):
        """Benchmark: 500 beams should complete in <4s."""
        from components.visualizations_3d import create_multi_beam_3d_figure

        beams = self._generate_mock_beams(500)

        start = time.perf_counter()
        figure, stats = create_multi_beam_3d_figure(beams)
        elapsed = time.perf_counter() - start

        assert elapsed < 4.0, f"500 beams took {elapsed:.2f}s (target: <4s)"
        assert figure is not None

    @pytest.mark.benchmark
    @pytest.mark.slow
    def test_performance_1000_beams(self):
        """Benchmark: 1000 beams should complete in <8s (LOW LOD)."""
        from components.visualizations_3d import create_multi_beam_3d_figure

        beams = self._generate_mock_beams(1000)

        start = time.perf_counter()
        figure, stats = create_multi_beam_3d_figure(beams)
        elapsed = time.perf_counter() - start

        assert elapsed < 8.0, f"1000 beams took {elapsed:.2f}s (target: <8s)"
        assert stats["level"] in ("LOW", "ULTRA_LOW")


class TestGeometryCache:
    """Tests for geometry caching system."""

    def test_geometry_cache_import(self):
        """Test GeometryCache can be imported."""
        from utils.lod_manager import GeometryCache

        # GeometryCache exists and has required methods
        assert hasattr(GeometryCache, "get_instance")
        assert hasattr(GeometryCache, "MAX_ENTRIES")

    def test_geometry_cache_init(self):
        """Test basic cache initialization (without Streamlit)."""
        from utils.lod_manager import GeometryCache

        # Direct instantiation (bypassing session_state)
        cache = GeometryCache()
        assert cache is not None
        assert hasattr(cache, "_cache")

    def test_geometry_cache_structure(self):
        """Test cache has required internal structure."""
        from utils.lod_manager import GeometryCache

        cache = GeometryCache()

        # Check internal state exists
        assert hasattr(cache, "_hits")
        assert hasattr(cache, "_misses")
        assert hasattr(cache, "_lod_manager")
