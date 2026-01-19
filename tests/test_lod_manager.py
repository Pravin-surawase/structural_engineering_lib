# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for LOD (Level of Detail) manager."""

from __future__ import annotations

import pytest
import sys
from pathlib import Path

# Add streamlit_app to path for imports
project_root = Path(__file__).parent.parent
streamlit_app_dir = project_root / "streamlit_app"
if str(streamlit_app_dir) not in sys.path:
    sys.path.insert(0, str(streamlit_app_dir))

from streamlit_app.utils.lod_manager import (
    LODLevel,
    LODManager,
    LODConfig,
    LODStats,
    generate_lod_summary,
    simplify_for_overview,
    simplify_for_large_model,
)


class TestLODLevel:
    """Tests for LODLevel enum."""

    def test_lod_levels_exist(self):
        """All expected LOD levels should exist."""
        assert LODLevel.HIGH
        assert LODLevel.MEDIUM
        assert LODLevel.LOW
        assert LODLevel.ULTRA_LOW

    def test_lod_levels_order(self):
        """LOD levels should be in order of detail."""
        levels = list(LODLevel)
        # HIGH is most detailed, ULTRA_LOW is least detailed
        assert levels[0] == LODLevel.HIGH
        assert levels[-1] == LODLevel.ULTRA_LOW


class TestLODManager:
    """Tests for LODManager class."""

    @pytest.fixture
    def lod_manager(self) -> LODManager:
        """Create LOD manager instance."""
        return LODManager()

    @pytest.fixture
    def sample_geometry(self) -> dict:
        """Create sample beam geometry for testing."""
        return {
            "beamId": "B1",
            "section": {
                "width": 300,
                "height": 500,
                "length": 6000,
            },
            "bars": [
                {"barId": "B1", "barType": "bottom", "diameter": 20},
                {"barId": "B2", "barType": "bottom", "diameter": 20},
                {"barId": "B3", "barType": "bottom", "diameter": 20},
                {"barId": "B4", "barType": "bottom", "diameter": 20},
                {"barId": "T1", "barType": "top", "diameter": 16},
                {"barId": "T2", "barType": "top", "diameter": 16},
            ],
            "stirrups": [
                {"position": 0, "diameter": 8},
                {"position": 100, "diameter": 8},
                {"position": 200, "diameter": 8},
                {"position": 300, "diameter": 8},
                {"position": 400, "diameter": 8},
                {"position": 500, "diameter": 8},
            ],
        }

    def test_get_recommended_level_single_beam(self, lod_manager):
        """Single beam should get HIGH LOD (full detail)."""
        assert lod_manager.get_recommended_level(1) == LODLevel.HIGH

    def test_get_recommended_level_small_building(self, lod_manager):
        """Up to 150 beams (small-medium buildings) should get HIGH LOD."""
        assert lod_manager.get_recommended_level(10) == LODLevel.HIGH
        assert lod_manager.get_recommended_level(75) == LODLevel.HIGH
        assert lod_manager.get_recommended_level(150) == LODLevel.HIGH

    def test_get_recommended_level_medium_building(self, lod_manager):
        """151-400 beams (large buildings) should get MEDIUM LOD."""
        assert lod_manager.get_recommended_level(151) == LODLevel.MEDIUM
        assert lod_manager.get_recommended_level(200) == LODLevel.MEDIUM
        assert lod_manager.get_recommended_level(400) == LODLevel.MEDIUM

    def test_get_recommended_level_large_building(self, lod_manager):
        """401-1000 beams (very large buildings) should get LOW LOD."""
        assert lod_manager.get_recommended_level(401) == LODLevel.LOW
        assert lod_manager.get_recommended_level(500) == LODLevel.LOW
        assert lod_manager.get_recommended_level(1000) == LODLevel.LOW

    def test_get_recommended_level_complex(self, lod_manager):
        """1000+ beams (industrial complexes) should get ULTRA_LOW LOD."""
        assert lod_manager.get_recommended_level(1001) == LODLevel.ULTRA_LOW
        assert lod_manager.get_recommended_level(5000) == LODLevel.ULTRA_LOW

    def test_get_config_returns_correct_type(self, lod_manager):
        """get_config should return LODConfig."""
        config = lod_manager.get_config(LODLevel.HIGH)
        assert isinstance(config, LODConfig)

    def test_full_lod_config(self, lod_manager):
        """HIGH LOD should have full detail enabled."""
        config = lod_manager.get_config(LODLevel.HIGH)
        assert config.show_stirrups is True
        assert config.show_all_bars is True
        assert config.show_labels is True
        assert config.mesh_segments == 16
        assert config.stirrup_reduction == 1  # Show all

    def test_medium_lod_config(self, lod_manager):
        """MEDIUM LOD should have balanced detail."""
        config = lod_manager.get_config(LODLevel.MEDIUM)
        assert config.show_stirrups is True
        assert config.stirrup_reduction == 2  # Show every 2nd
        assert config.show_all_bars is False  # Corner bars only
        assert config.show_labels is False
        assert config.mesh_segments == 12

    def test_ultra_low_config(self, lod_manager):
        """ULTRA_LOW LOD should have minimal detail."""
        config = lod_manager.get_config(LODLevel.ULTRA_LOW)
        assert config.show_stirrups is False
        assert config.show_all_bars is False
        assert config.show_labels is False
        assert config.mesh_segments == 4
        assert config.use_instancing is True

    def test_simplify_geometry_high_lod(self, lod_manager, sample_geometry):
        """HIGH LOD should preserve all geometry."""
        simplified, stats = lod_manager.simplify_geometry(
            sample_geometry, level=LODLevel.HIGH
        )

        # All stirrups and bars should be preserved
        assert stats.simplified_stirrup_count == stats.original_stirrup_count
        assert stats.simplified_bar_count == stats.original_bar_count

    def test_simplify_geometry_medium_lod(self, lod_manager, sample_geometry):
        """MEDIUM LOD should reduce stirrups but show representative ones."""
        simplified, stats = lod_manager.simplify_geometry(
            sample_geometry, level=LODLevel.MEDIUM
        )

        # Some stirrups should be shown (every 2nd)
        assert 0 < stats.simplified_stirrup_count < stats.original_stirrup_count

        # Bars should be reduced to corners
        assert stats.simplified_bar_count < stats.original_bar_count

    def test_simplify_geometry_adds_lod_metadata(self, lod_manager, sample_geometry):
        """Simplified geometry should include LOD metadata."""
        simplified, _ = lod_manager.simplify_geometry(
            sample_geometry, level=LODLevel.HIGH
        )

        assert "_lod" in simplified
        assert simplified["_lod"]["level"] == "HIGH"
        assert "mesh_segments" in simplified["_lod"]
        assert "use_instancing" in simplified["_lod"]

    def test_simplify_batch(self, lod_manager, sample_geometry):
        """Batch simplification should work for multiple geometries."""
        geometries = [sample_geometry.copy() for _ in range(100)]

        # 100 beams = HIGH LOD (keeps all stirrups)
        simplified, stats = lod_manager.simplify_batch(geometries)

        assert len(simplified) == 100
        # HIGH LOD keeps all stirrups (stirrup_reduction=1 means show all)
        assert stats.original_stirrup_count == stats.simplified_stirrup_count

    def test_get_performance_estimate(self, lod_manager):
        """Performance estimates should be reasonable."""
        perf = lod_manager.get_performance_estimate(500)

        assert "level" in perf
        assert "beam_count" in perf
        assert "estimated_vertices" in perf
        assert "estimated_render_time_ms" in perf
        assert "estimated_fps" in perf

        # Should be usable FPS for 500 beams
        assert perf["estimated_fps"] > 0

    def test_large_model_performance(self, lod_manager):
        """1000+ beams should still have acceptable performance."""
        perf = lod_manager.get_performance_estimate(1000)

        assert perf["level"] == "LOW"
        assert perf["use_instancing"] is True
        assert perf["estimated_fps"] > 10  # At least 10 FPS

    def test_mesh_reduction_calculation(self, lod_manager, sample_geometry):
        """Mesh reduction percentage should be calculated."""
        _, high_stats = lod_manager.simplify_geometry(
            sample_geometry, level=LODLevel.HIGH
        )
        _, low_stats = lod_manager.simplify_geometry(
            sample_geometry, level=LODLevel.LOW
        )

        # LOW should have more reduction than HIGH
        assert low_stats.mesh_reduction_percent >= high_stats.mesh_reduction_percent


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @pytest.fixture
    def sample_geometries(self) -> list[dict]:
        """Create list of sample geometries."""
        return [
            {
                "beamId": f"B{i}",
                "bars": [{"barId": "B1", "barType": "bottom"}],
                "stirrups": [{"position": 0}],
            }
            for i in range(100)
        ]

    def test_generate_lod_summary(self):
        """Summary should be a readable string."""
        summary = generate_lod_summary(500)

        assert isinstance(summary, str)
        assert "LOD" in summary
        assert "LOW" in summary  # 500 beams = LOW LOD (201-1000 range)
        assert "Performance" in summary

    def test_simplify_for_overview(self, sample_geometries):
        """Overview simplification should use MEDIUM LOD."""
        simplified = simplify_for_overview(sample_geometries)

        assert len(simplified) == len(sample_geometries)
        # Check LOD metadata
        assert simplified[0]["_lod"]["level"] == "MEDIUM"

    def test_simplify_for_large_model_low(self, sample_geometries):
        """Large model with <1000 beams should use LOW."""
        simplified = simplify_for_large_model(sample_geometries)

        assert simplified[0]["_lod"]["level"] == "LOW"

    def test_simplify_for_large_model_ultra_low(self):
        """Large model with >1000 beams should use ULTRA_LOW."""
        geometries = [
            {"beamId": f"B{i}", "bars": [], "stirrups": []}
            for i in range(1500)
        ]

        simplified = simplify_for_large_model(geometries)

        assert simplified[0]["_lod"]["level"] == "ULTRA_LOW"


class TestCustomConfigs:
    """Tests for custom LOD configurations."""

    def test_custom_config_override(self):
        """Custom configs should override defaults."""
        custom = {
            LODLevel.HIGH: LODConfig(
                level=LODLevel.HIGH,
                max_beams=100,  # Custom max
                show_stirrups=False,  # Different from default
                stirrup_reduction=0,
                show_all_bars=True,
                show_labels=True,
                use_instancing=True,
                mesh_segments=8,
                show_section_outline=True,
            )
        }

        lod = LODManager(custom_configs=custom)
        config = lod.get_config(LODLevel.HIGH)

        assert config.max_beams == 100
        assert config.show_stirrups is False

    def test_custom_config_preserves_others(self):
        """Customizing one level should preserve others."""
        custom = {
            LODLevel.HIGH: LODConfig(
                level=LODLevel.HIGH,
                max_beams=100,
                show_stirrups=False,
                stirrup_reduction=0,
                show_all_bars=True,
                show_labels=True,
                use_instancing=True,
                mesh_segments=8,
                show_section_outline=True,
            )
        }

        lod = LODManager(custom_configs=custom)

        # MEDIUM should still be default
        medium_config = lod.get_config(LODLevel.MEDIUM)
        assert medium_config.show_stirrups is True  # Default behavior
