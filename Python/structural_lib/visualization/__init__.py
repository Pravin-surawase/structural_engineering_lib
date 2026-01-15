# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Visualization Module — 3D Geometry for Reinforced Concrete Elements

This module provides coordinate computation and JSON serialization for
3D visualization of structural elements like beams, columns, and slabs.

The module bridges the gap between structural design output (WHAT reinforcement
is needed) and 3D visualization (WHERE reinforcement is placed in space).

Key Components:
- geometry_3d: Core dataclasses (Point3D, RebarSegment, StirrupLoop, Beam3DGeometry)
- Coordinate computation functions for rebar and stirrup placement
- JSON serialization for Three.js/WebGL visualization

Example:
    >>> from structural_lib.visualization import Beam3DGeometry
    >>> from structural_lib.visualization.geometry_3d import beam_to_3d_geometry
    >>> geometry = beam_to_3d_geometry(detailing_result)
    >>> json_data = geometry.to_dict()

References:
    - IS 456:2000 for reinforcement detailing rules
    - SP 34:1987 for bar placement conventions
"""

from __future__ import annotations

from structural_lib.visualization.geometry_3d import (
    Beam3DGeometry,
    Point3D,
    RebarPath,
    RebarSegment,
    StirrupLoop,
)

__all__ = [
    "Point3D",
    "RebarSegment",
    "RebarPath",
    "StirrupLoop",
    "Beam3DGeometry",
]
