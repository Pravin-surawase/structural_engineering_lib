# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
LOD (Level of Detail) Manager for 3D Visualization

This module provides automatic simplification of 3D beam geometry
for rendering large numbers of beams (1000+) without performance degradation.

LOD Levels:
    - FULL: Complete detail (stirrups, all bars, labels) - for single beam
    - HIGH: Detailed (reduced stirrups, all bars) - up to 50 beams
    - MEDIUM: Simplified (corner bars only, no stirrups) - up to 200 beams
    - LOW: Basic (box outline, color by status) - up to 1000 beams
    - ULTRA_LOW: Minimal (lines only) - 1000+ beams

Usage:
    >>> from streamlit_app.utils.lod_manager import LODManager, LODLevel
    >>> lod = LODManager()
    >>> simplified_geometry = lod.simplify(geometry, num_beams=500)
    >>> level = lod.get_recommended_level(beam_count=1000)

Author: Session 42 Agent
Task: TASK-3D-003 (LOD system for 1000+ beams)
Status: ✅ IMPLEMENTED
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class LODLevel(Enum):
    """Level of Detail enumeration."""

    FULL = auto()       # Single beam, full detail
    HIGH = auto()       # Up to 50 beams, detailed
    MEDIUM = auto()     # Up to 200 beams, simplified
    LOW = auto()        # Up to 1000 beams, basic
    ULTRA_LOW = auto()  # 1000+ beams, minimal


@dataclass
class LODConfig:
    """Configuration for each LOD level."""

    level: LODLevel
    max_beams: int
    show_stirrups: bool
    stirrup_reduction: int  # Show every Nth stirrup (1 = all, 0 = none)
    show_all_bars: bool     # False = corner bars only
    show_labels: bool
    use_instancing: bool    # Use WebGL instancing for performance
    mesh_segments: int      # Cylinder segments (lower = faster)
    show_section_outline: bool


# Default configurations for each LOD level
LOD_CONFIGS: dict[LODLevel, LODConfig] = {
    LODLevel.FULL: LODConfig(
        level=LODLevel.FULL,
        max_beams=1,
        show_stirrups=True,
        stirrup_reduction=1,  # Show all
        show_all_bars=True,
        show_labels=True,
        use_instancing=False,
        mesh_segments=16,
        show_section_outline=True,
    ),
    LODLevel.HIGH: LODConfig(
        level=LODLevel.HIGH,
        max_beams=50,
        show_stirrups=True,
        stirrup_reduction=3,  # Show every 3rd stirrup
        show_all_bars=True,
        show_labels=True,
        use_instancing=True,
        mesh_segments=12,
        show_section_outline=True,
    ),
    LODLevel.MEDIUM: LODConfig(
        level=LODLevel.MEDIUM,
        max_beams=200,
        show_stirrups=False,
        stirrup_reduction=0,  # No stirrups
        show_all_bars=False,  # Corner bars only
        show_labels=False,
        use_instancing=True,
        mesh_segments=8,
        show_section_outline=True,
    ),
    LODLevel.LOW: LODConfig(
        level=LODLevel.LOW,
        max_beams=1000,
        show_stirrups=False,
        stirrup_reduction=0,
        show_all_bars=False,
        show_labels=False,
        use_instancing=True,
        mesh_segments=4,
        show_section_outline=False,
    ),
    LODLevel.ULTRA_LOW: LODConfig(
        level=LODLevel.ULTRA_LOW,
        max_beams=float("inf"),
        show_stirrups=False,
        stirrup_reduction=0,
        show_all_bars=False,
        show_labels=False,
        use_instancing=True,
        mesh_segments=2,
        show_section_outline=False,
    ),
}


@dataclass
class LODStats:
    """Statistics about LOD simplification."""

    original_stirrup_count: int = 0
    simplified_stirrup_count: int = 0
    original_bar_count: int = 0
    simplified_bar_count: int = 0
    mesh_reduction_percent: float = 0.0
    estimated_vertices: int = 0
    estimated_render_time_ms: float = 0.0


class LODManager:
    """Manager for Level of Detail simplification.

    Automatically determines the appropriate LOD level based on
    beam count and applies geometry simplification accordingly.

    Example:
        >>> lod = LODManager()
        >>> # For 500 beams, get MEDIUM LOD
        >>> level = lod.get_recommended_level(500)
        >>> config = lod.get_config(level)
        >>>
        >>> # Simplify geometry list
        >>> simplified = lod.simplify_batch(geometries, num_beams=500)
    """

    def __init__(self, custom_configs: dict[LODLevel, LODConfig] | None = None):
        """Initialize LOD manager.

        Args:
            custom_configs: Optional custom LOD configurations to override defaults
        """
        self.configs = LOD_CONFIGS.copy()
        if custom_configs:
            self.configs.update(custom_configs)

    def get_recommended_level(self, beam_count: int) -> LODLevel:
        """Get the recommended LOD level for the given beam count.

        Args:
            beam_count: Number of beams to render

        Returns:
            Recommended LODLevel enum value
        """
        if beam_count <= 1:
            return LODLevel.FULL
        elif beam_count <= 50:
            return LODLevel.HIGH
        elif beam_count <= 200:
            return LODLevel.MEDIUM
        elif beam_count <= 1000:
            return LODLevel.LOW
        else:
            return LODLevel.ULTRA_LOW

    def get_config(self, level: LODLevel) -> LODConfig:
        """Get the configuration for a specific LOD level.

        Args:
            level: LOD level to get config for

        Returns:
            LODConfig for the specified level
        """
        return self.configs[level]

    def simplify_geometry(
        self,
        geometry: dict[str, Any],
        level: LODLevel | None = None,
        beam_count: int = 1,
    ) -> tuple[dict[str, Any], LODStats]:
        """Simplify a single beam geometry based on LOD level.

        Args:
            geometry: Beam geometry dict (BeamGeometry3D format)
            level: Optional explicit LOD level (auto-detected if None)
            beam_count: Total beam count (used for auto-detection)

        Returns:
            Tuple of (simplified_geometry, stats)
        """
        if level is None:
            level = self.get_recommended_level(beam_count)

        config = self.get_config(level)
        stats = LODStats()

        # Create a copy to avoid modifying original
        simplified = geometry.copy()

        # Simplify stirrups
        stirrups = geometry.get("stirrups", [])
        stats.original_stirrup_count = len(stirrups)

        if not config.show_stirrups or config.stirrup_reduction == 0:
            simplified["stirrups"] = []
            stats.simplified_stirrup_count = 0
        elif config.stirrup_reduction > 1:
            # Keep every Nth stirrup
            simplified["stirrups"] = stirrups[::config.stirrup_reduction]
            stats.simplified_stirrup_count = len(simplified["stirrups"])
        else:
            stats.simplified_stirrup_count = len(stirrups)

        # Simplify bars
        bars = geometry.get("bars", [])
        stats.original_bar_count = len(bars)

        if not config.show_all_bars:
            # Keep only corner bars (first and last of each type)
            simplified_bars = self._extract_corner_bars(bars)
            simplified["bars"] = simplified_bars
            stats.simplified_bar_count = len(simplified_bars)
        else:
            stats.simplified_bar_count = len(bars)

        # Add LOD metadata
        simplified["_lod"] = {
            "level": level.name,
            "mesh_segments": config.mesh_segments,
            "use_instancing": config.use_instancing,
            "show_section_outline": config.show_section_outline,
            "show_labels": config.show_labels,
        }

        # Calculate mesh reduction
        original_vertices = self._estimate_vertices(geometry, 16)
        simplified_vertices = self._estimate_vertices(simplified, config.mesh_segments)
        stats.estimated_vertices = simplified_vertices

        if original_vertices > 0:
            stats.mesh_reduction_percent = (
                (original_vertices - simplified_vertices) / original_vertices * 100
            )

        # Estimate render time (rough approximation)
        stats.estimated_render_time_ms = simplified_vertices * 0.001

        return simplified, stats

    def simplify_batch(
        self,
        geometries: list[dict[str, Any]],
        level: LODLevel | None = None,
    ) -> tuple[list[dict[str, Any]], LODStats]:
        """Simplify a batch of beam geometries.

        Args:
            geometries: List of beam geometry dicts
            level: Optional explicit LOD level (auto-detected if None)

        Returns:
            Tuple of (simplified_geometries, aggregate_stats)
        """
        num_beams = len(geometries)
        if level is None:
            level = self.get_recommended_level(num_beams)

        simplified = []
        total_stats = LODStats()

        for geom in geometries:
            simp_geom, stats = self.simplify_geometry(geom, level, num_beams)
            simplified.append(simp_geom)

            # Aggregate stats
            total_stats.original_stirrup_count += stats.original_stirrup_count
            total_stats.simplified_stirrup_count += stats.simplified_stirrup_count
            total_stats.original_bar_count += stats.original_bar_count
            total_stats.simplified_bar_count += stats.simplified_bar_count
            total_stats.estimated_vertices += stats.estimated_vertices

        # Calculate overall reduction
        if total_stats.original_stirrup_count + total_stats.original_bar_count > 0:
            orig_total = (
                total_stats.original_stirrup_count + total_stats.original_bar_count
            )
            simp_total = (
                total_stats.simplified_stirrup_count + total_stats.simplified_bar_count
            )
            total_stats.mesh_reduction_percent = (
                (orig_total - simp_total) / orig_total * 100
            )

        total_stats.estimated_render_time_ms = total_stats.estimated_vertices * 0.001

        return simplified, total_stats

    def _extract_corner_bars(self, bars: list[dict]) -> list[dict]:
        """Extract corner bars (first and last) from bar list.

        For simplified LOD, we only show corner bars to indicate
        reinforcement pattern without full detail.
        """
        if not bars:
            return []

        # Group bars by type (bottom, top, side)
        by_type: dict[str, list[dict]] = {}
        for bar in bars:
            bar_type = bar.get("barType", "bottom")
            if bar_type not in by_type:
                by_type[bar_type] = []
            by_type[bar_type].append(bar)

        # Keep first and last of each type
        corner_bars = []
        for bar_type, type_bars in by_type.items():
            if len(type_bars) >= 2:
                corner_bars.extend([type_bars[0], type_bars[-1]])
            else:
                corner_bars.extend(type_bars)

        return corner_bars

    def _estimate_vertices(
        self,
        geometry: dict[str, Any],
        mesh_segments: int,
    ) -> int:
        """Estimate vertex count for geometry rendering."""
        vertices = 0

        # Beam section (box)
        vertices += 24  # 6 faces * 4 vertices

        # Bars (cylinders)
        bars = geometry.get("bars", [])
        for bar in bars:
            segments = bar.get("segments", [])
            # Each segment is a cylinder: 2 caps + side
            vertices += len(segments) * (mesh_segments * 2 + mesh_segments * 2)

        # Stirrups (rectangles)
        stirrups = geometry.get("stirrups", [])
        vertices += len(stirrups) * (mesh_segments * 4)  # 4 bars per stirrup

        return vertices

    def get_performance_estimate(
        self,
        beam_count: int,
        level: LODLevel | None = None,
    ) -> dict[str, Any]:
        """Get performance estimates for rendering beam count.

        Args:
            beam_count: Number of beams to render
            level: Optional explicit LOD level

        Returns:
            Dict with performance estimates
        """
        if level is None:
            level = self.get_recommended_level(beam_count)

        config = self.get_config(level)

        # Rough estimates based on testing
        base_vertices_per_beam = 500 if config.show_stirrups else 100
        if not config.show_all_bars:
            base_vertices_per_beam = 50

        total_vertices = beam_count * base_vertices_per_beam

        # Render time estimates (ms)
        if config.use_instancing:
            render_time_ms = total_vertices * 0.0001  # Instanced is ~10x faster
        else:
            render_time_ms = total_vertices * 0.001

        return {
            "level": level.name,
            "beam_count": beam_count,
            "estimated_vertices": total_vertices,
            "estimated_render_time_ms": round(render_time_ms, 2),
            "estimated_fps": min(60, round(1000 / max(render_time_ms, 16.67), 1)),
            "use_instancing": config.use_instancing,
            "mesh_segments": config.mesh_segments,
            "recommended": True,
        }


def generate_lod_summary(beam_count: int) -> str:
    """Generate a human-readable LOD summary.

    Args:
        beam_count: Number of beams

    Returns:
        Summary string
    """
    lod = LODManager()
    level = lod.get_recommended_level(beam_count)
    config = lod.get_config(level)
    perf = lod.get_performance_estimate(beam_count, level)

    summary = f"""
**LOD: {level.name}** ({beam_count} beams)

| Setting | Value |
|---------|-------|
| Stirrups | {'Yes' if config.show_stirrups else 'No'} |
| All Bars | {'Yes' if config.show_all_bars else 'Corner only'} |
| Labels | {'Yes' if config.show_labels else 'No'} |
| Instancing | {'Enabled' if config.use_instancing else 'Disabled'} |
| Mesh Quality | {config.mesh_segments} segments |

**Performance:**
- Estimated vertices: {perf['estimated_vertices']:,}
- Render time: ~{perf['estimated_render_time_ms']:.1f}ms
- Expected FPS: ~{perf['estimated_fps']}
"""
    return summary


# Convenience functions for common use cases
def simplify_for_overview(
    geometries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Simplify geometries for building overview visualization.

    Forces MEDIUM LOD for clear overview without too much detail.
    """
    lod = LODManager()
    simplified, _ = lod.simplify_batch(geometries, level=LODLevel.MEDIUM)
    return simplified


def simplify_for_large_model(
    geometries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Simplify geometries for large models (1000+ beams).

    Forces LOW or ULTRA_LOW LOD based on count.
    """
    lod = LODManager()
    count = len(geometries)
    level = LODLevel.ULTRA_LOW if count > 1000 else LODLevel.LOW
    simplified, _ = lod.simplify_batch(geometries, level=level)
    return simplified
