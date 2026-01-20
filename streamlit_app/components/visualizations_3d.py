# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
3D Visualization Components — Plotly Integration for Streamlit

This module provides Plotly 3D mesh generation functions for rendering
reinforced concrete beams with rebar and stirrups. It's designed for
native Streamlit integration without iframe/postMessage complexity.

Key Features:
    - <50ms mesh generation for typical beams
    - Native Plotly Graph Objects (no external dependencies)
    - Geometry hashing for efficient caching
    - Fragment-compatible for live updates

Architecture:
    ┌─────────────────────────┐
    │ geometry_3d.py (data)   │
    │  Beam3DGeometry         │
    └───────────┬─────────────┘
                │ to_dict()
                ▼
    ┌─────────────────────────┐
    │ visualizations_3d.py    │  ← This module
    │  create_beam_3d_figure  │
    └───────────┬─────────────┘
                │ Plotly Figure
                ▼
    ┌─────────────────────────┐
    │ Streamlit st.plotly_chart│
    └─────────────────────────┘

Coordinate System (matches geometry_3d.py):
    - X: Along beam span (0 to span)
    - Y: Beam width (-width/2 to +width/2)
    - Z: Beam height (0 at bottom, D at top)

Performance:
    - Mesh generation: <50ms for 6 rebars + 30 stirrups
    - Geometry hash: <1ms (xxhash if available, else hashlib)
    - Caching: Streamlit @st.cache_data compatible

Usage:
    >>> from streamlit_app.components.visualizations_3d import (
    ...     create_beam_3d_figure,
    ...     create_beam_3d_from_geometry,
    ... )
    >>> fig = create_beam_3d_figure(
    ...     b=300, D=450, span=4000,
    ...     bottom_bars=[(0, -96, 52), (0, 0, 52), (0, 96, 52)],
    ...     top_bars=[(0, -96, 398), (0, 96, 398)],
    ...     stirrup_positions=[100, 200, 300],
    ... )
    >>> st.plotly_chart(fig, width="stretch")

References:
    - IS 456:2000 (RC detailing)
    - Plotly 3D documentation
    - geometry_3d.py for data structures
"""

from __future__ import annotations

import hashlib
import math
from typing import TYPE_CHECKING, Any

import plotly.graph_objects as go

if TYPE_CHECKING:
    from structural_lib.visualization.geometry_3d import Beam3DGeometry


__all__ = [
    "create_beam_3d_figure",
    "create_beam_3d_from_geometry",
    "create_beam_3d_from_dict",
    "create_multi_beam_3d_figure",
    "generate_cylinder_mesh",
    "generate_box_mesh",
    "generate_stirrup_tube",
    "compute_geometry_hash",
]


# =============================================================================
# Color Constants
# =============================================================================

COLORS = {
    "concrete": "rgba(160, 160, 160, 0.25)",  # Semi-transparent gray
    "concrete_edge": "rgba(100, 100, 100, 0.5)",  # Darker edges
    "rebar_bottom": "#e53935",  # Red for tension steel
    "rebar_top": "#1e88e5",  # Blue for compression steel
    "stirrup": "#43a047",  # Green for stirrups
    "background": "#1a1a2e",  # Dark background
}

# Mesh resolution (segments per circle)
CYLINDER_RESOLUTION = 16  # Balance between quality and performance


# =============================================================================
# Mesh Generation Functions
# =============================================================================


def generate_cylinder_mesh(
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    radius: float,
    color: str,
    resolution: int = CYLINDER_RESOLUTION,
) -> go.Mesh3d:
    """
    Generate a 3D cylinder mesh between two points.

    This creates a cylinder (tube) connecting two points, used for
    representing rebar bars. The cylinder is oriented along the
    direction vector from start to end.

    Args:
        start: (x, y, z) start point in mm
        end: (x, y, z) end point in mm
        radius: Cylinder radius in mm
        color: Plotly color string (hex or rgba)
        resolution: Number of segments around circumference

    Returns:
        Plotly Mesh3d object representing the cylinder

    Performance:
        ~0.5ms per cylinder at resolution=16

    Example:
        >>> mesh = generate_cylinder_mesh(
        ...     start=(0, -96, 52),
        ...     end=(4000, -96, 52),
        ...     radius=8,  # 16mm bar
        ...     color="#e53935"
        ... )
    """
    # Direction vector
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)

    if length < 0.001:  # Avoid division by zero
        return go.Mesh3d(x=[], y=[], z=[])

    # Normalize direction
    dir_x, dir_y, dir_z = dx / length, dy / length, dz / length

    # Find perpendicular vectors using cross product
    # Start with a non-parallel vector
    if abs(dir_x) < 0.9:
        ref = (1, 0, 0)
    else:
        ref = (0, 1, 0)

    # Cross product: dir × ref → perp1
    perp1_x = dir_y * ref[2] - dir_z * ref[1]
    perp1_y = dir_z * ref[0] - dir_x * ref[2]
    perp1_z = dir_x * ref[1] - dir_y * ref[0]
    perp1_len = math.sqrt(perp1_x**2 + perp1_y**2 + perp1_z**2)
    perp1_x /= perp1_len
    perp1_y /= perp1_len
    perp1_z /= perp1_len

    # Cross product: dir × perp1 → perp2
    perp2_x = dir_y * perp1_z - dir_z * perp1_y
    perp2_y = dir_z * perp1_x - dir_x * perp1_z
    perp2_z = dir_x * perp1_y - dir_y * perp1_x

    # Generate vertices for both end circles
    x_vertices = []
    y_vertices = []
    z_vertices = []

    for cap_idx in range(2):
        base = start if cap_idx == 0 else end
        for i in range(resolution):
            angle = 2 * math.pi * i / resolution
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)

            # Point on circle: base + radius * (cos * perp1 + sin * perp2)
            x = base[0] + radius * (cos_a * perp1_x + sin_a * perp2_x)
            y = base[1] + radius * (cos_a * perp1_y + sin_a * perp2_y)
            z = base[2] + radius * (cos_a * perp1_z + sin_a * perp2_z)

            x_vertices.append(x)
            y_vertices.append(y)
            z_vertices.append(z)

    # Generate triangular faces
    i_faces = []
    j_faces = []
    k_faces = []

    # Side faces (quads split into triangles)
    for i in range(resolution):
        next_i = (i + 1) % resolution

        # Bottom ring indices: 0 to resolution-1
        # Top ring indices: resolution to 2*resolution-1
        b1 = i
        b2 = next_i
        t1 = i + resolution
        t2 = next_i + resolution

        # Triangle 1: b1, b2, t1
        i_faces.append(b1)
        j_faces.append(b2)
        k_faces.append(t1)

        # Triangle 2: b2, t2, t1
        i_faces.append(b2)
        j_faces.append(t2)
        k_faces.append(t1)

    # Add center points for end caps
    # Bottom center
    x_vertices.append(start[0])
    y_vertices.append(start[1])
    z_vertices.append(start[2])
    bottom_center = len(x_vertices) - 1

    # Top center
    x_vertices.append(end[0])
    y_vertices.append(end[1])
    z_vertices.append(end[2])
    top_center = len(x_vertices) - 1

    # Bottom cap faces
    for i in range(resolution):
        next_i = (i + 1) % resolution
        i_faces.append(bottom_center)
        j_faces.append(i)
        k_faces.append(next_i)

    # Top cap faces
    for i in range(resolution):
        next_i = (i + 1) % resolution
        i_faces.append(top_center)
        j_faces.append(i + resolution)
        k_faces.append(next_i + resolution)

    return go.Mesh3d(
        x=x_vertices,
        y=y_vertices,
        z=z_vertices,
        i=i_faces,
        j=j_faces,
        k=k_faces,
        color=color,
        flatshading=True,
        lighting=dict(
            ambient=0.6,
            diffuse=0.8,
            specular=0.5,
            roughness=0.3,
        ),
        lightposition=dict(x=2000, y=2000, z=3000),
        hoverinfo="skip",
    )


def generate_box_mesh(
    width: float,
    depth: float,
    span: float,
    opacity: float = 0.25,
) -> go.Mesh3d:
    """
    Generate a 3D box mesh for concrete beam.

    Creates a rectangular box centered at Y=0, with:
    - X from 0 to span
    - Y from -width/2 to +width/2
    - Z from 0 to depth

    Args:
        width: Beam width (b) in mm
        depth: Beam depth (D) in mm
        span: Beam span in mm
        opacity: Transparency (0-1)

    Returns:
        Plotly Mesh3d object for the concrete box

    Example:
        >>> mesh = generate_box_mesh(300, 450, 4000)
    """
    half_w = width / 2

    # 8 corners of the box
    x = [0, 0, span, span, 0, 0, span, span]
    y = [-half_w, half_w, half_w, -half_w, -half_w, half_w, half_w, -half_w]
    z = [0, 0, 0, 0, depth, depth, depth, depth]

    # 12 triangular faces (6 sides × 2 triangles each)
    # Face indices: each face defined by 4 corners, split into 2 triangles
    i = [0, 0, 4, 4, 0, 0, 1, 1, 0, 0, 3, 3]
    j = [1, 2, 5, 6, 4, 1, 5, 2, 3, 4, 7, 4]
    k = [2, 3, 6, 7, 1, 5, 6, 6, 4, 7, 4, 0]

    return go.Mesh3d(
        x=x,
        y=y,
        z=z,
        i=i,
        j=j,
        k=k,
        color=COLORS["concrete"],
        opacity=opacity,
        flatshading=False,
        hoverinfo="skip",
    )


def generate_stirrup_tube(
    position_x: float,
    corners: list[tuple[float, float, float]],
    radius: float,
    color: str = COLORS["stirrup"],
) -> list[go.Mesh3d]:
    """
    Generate tube segments for a closed stirrup loop.

    Creates cylinder segments connecting each corner of the stirrup,
    forming a closed rectangular loop.

    Args:
        position_x: X position along span (overrides corner x values)
        corners: List of (x, y, z) corner points
        radius: Stirrup bar radius in mm
        color: Stirrup color

    Returns:
        List of Mesh3d objects for stirrup segments

    Example:
        >>> corners = [
        ...     (100, -106, 44),
        ...     (100, 106, 44),
        ...     (100, 106, 406),
        ...     (100, -106, 406),
        ... ]
        >>> meshes = generate_stirrup_tube(100, corners, 4)
    """
    meshes = []
    n_corners = len(corners)

    for i in range(n_corners):
        start = (position_x, corners[i][1], corners[i][2])
        end_idx = (i + 1) % n_corners
        end = (position_x, corners[end_idx][1], corners[end_idx][2])

        mesh = generate_cylinder_mesh(
            start=start,
            end=end,
            radius=radius,
            color=color,
            resolution=8,  # Lower resolution for stirrups (many of them)
        )
        meshes.append(mesh)

    return meshes


# =============================================================================
# Figure Creation Functions
# =============================================================================


def create_beam_3d_figure(
    b: float,
    D: float,
    span: float,
    bottom_bars: list[tuple[float, float, float]] | None = None,
    top_bars: list[tuple[float, float, float]] | None = None,
    bar_diameter: float = 16.0,
    stirrup_positions: list[float] | None = None,
    stirrup_diameter: float = 8.0,
    cover: float = 40.0,
    height: int = 500,
    show_legend: bool = True,
    show_info_panel: bool = True,
) -> go.Figure:
    """
    Create a complete 3D beam visualization figure.

    This is the main entry point for creating 3D beam visualizations.
    It generates concrete box, rebar cylinders, and stirrup loops.

    Args:
        b: Beam width in mm
        D: Beam depth in mm
        span: Beam span in mm
        bottom_bars: List of (x, y, z) positions for bottom bars
                     If None, auto-generated based on geometry
        top_bars: List of (x, y, z) positions for top bars
                  If None, auto-generated based on geometry
        bar_diameter: Main bar diameter in mm
        stirrup_positions: List of X positions for stirrups
                          If None, auto-generated at 100mm spacing
        stirrup_diameter: Stirrup bar diameter in mm
        cover: Clear cover in mm
        height: Figure height in pixels
        show_legend: Whether to show legend
        show_info_panel: Whether to show dimensions annotation

    Returns:
        Plotly Figure object ready for st.plotly_chart()

    Performance:
        <50ms for typical beam (6 bars, 30 stirrups)

    Example:
        >>> fig = create_beam_3d_figure(
        ...     b=300, D=450, span=4000,
        ...     bottom_bars=[(0, -96, 52), (0, 0, 52), (0, 96, 52)],
        ... )
        >>> st.plotly_chart(fig, width="stretch")
    """
    meshes: list[go.Mesh3d | go.Scatter3d] = []

    # 1. Concrete box
    concrete_mesh = generate_box_mesh(b, D, span)
    meshes.append(concrete_mesh)

    # 2. Add wireframe edges for concrete
    half_w = b / 2
    edge_lines = _create_box_wireframe(span, half_w, D)
    meshes.append(edge_lines)

    # 3. Bottom rebar
    if bottom_bars is None:
        # Auto-generate 3 bottom bars
        edge_dist = cover + stirrup_diameter + bar_diameter / 2
        z_bottom = edge_dist
        available_width = b - 2 * edge_dist
        bottom_bars = [
            (0, -available_width / 2, z_bottom),
            (0, 0, z_bottom),
            (0, available_width / 2, z_bottom),
        ]

    bar_radius = bar_diameter / 2
    for idx, bar_pos in enumerate(bottom_bars):
        start = (0, bar_pos[1], bar_pos[2])
        end = (span, bar_pos[1], bar_pos[2])
        mesh = generate_cylinder_mesh(
            start=start,
            end=end,
            radius=bar_radius,
            color=COLORS["rebar_bottom"],
        )
        mesh.name = f"Bottom Bar {idx + 1}" if idx == 0 else None
        mesh.legendgroup = "bottom"
        mesh.showlegend = idx == 0
        meshes.append(mesh)

    # 4. Top rebar
    if top_bars is None:
        # Auto-generate 2 top bars
        edge_dist = cover + stirrup_diameter + bar_diameter / 2
        z_top = D - edge_dist
        available_width = b - 2 * edge_dist
        top_bars = [
            (0, -available_width / 2, z_top),
            (0, available_width / 2, z_top),
        ]

    for idx, bar_pos in enumerate(top_bars):
        start = (0, bar_pos[1], bar_pos[2])
        end = (span, bar_pos[1], bar_pos[2])
        mesh = generate_cylinder_mesh(
            start=start,
            end=end,
            radius=bar_radius,
            color=COLORS["rebar_top"],
        )
        mesh.name = f"Top Bar {idx + 1}" if idx == 0 else None
        mesh.legendgroup = "top"
        mesh.showlegend = idx == 0
        meshes.append(mesh)

    # 5. Stirrups
    if stirrup_positions is None:
        # Auto-generate stirrups at 100mm spacing
        stirrup_positions = list(range(int(stirrup_diameter / 2) + 50, int(span), 100))

    stirrup_radius = stirrup_diameter / 2
    y_outer = half_w - cover - stirrup_radius
    z_bottom_stirrup = cover + stirrup_radius
    z_top_stirrup = D - cover - stirrup_radius

    stirrup_corners = [
        (0, -y_outer, z_bottom_stirrup),
        (0, y_outer, z_bottom_stirrup),
        (0, y_outer, z_top_stirrup),
        (0, -y_outer, z_top_stirrup),
    ]

    for idx, x_pos in enumerate(stirrup_positions):
        tube_meshes = generate_stirrup_tube(
            position_x=x_pos,
            corners=stirrup_corners,
            radius=stirrup_radius,
            color=COLORS["stirrup"],
        )
        for seg_idx, mesh in enumerate(tube_meshes):
            # Only show legend for first segment of first stirrup
            mesh.name = "Stirrup" if idx == 0 and seg_idx == 0 else None
            mesh.legendgroup = "stirrup"
            mesh.showlegend = idx == 0 and seg_idx == 0
            meshes.append(mesh)

    # Create figure
    fig = go.Figure(data=meshes)

    # Camera position: isometric view from front-right
    camera = dict(
        eye=dict(x=1.5, y=-1.2, z=0.8),
        center=dict(x=0, y=0, z=0.1),
        up=dict(x=0, y=0, z=1),
    )

    # Layout
    fig.update_layout(
        scene=dict(
            xaxis=dict(
                title="Span (mm)",
                showgrid=True,
                gridcolor="rgba(255,255,255,0.1)",
                backgroundcolor=COLORS["background"],
            ),
            yaxis=dict(
                title="Width (mm)",
                showgrid=True,
                gridcolor="rgba(255,255,255,0.1)",
                backgroundcolor=COLORS["background"],
            ),
            zaxis=dict(
                title="Depth (mm)",
                showgrid=True,
                gridcolor="rgba(255,255,255,0.1)",
                backgroundcolor=COLORS["background"],
            ),
            aspectmode="data",
            camera=camera,
            bgcolor=COLORS["background"],
        ),
        paper_bgcolor=COLORS["background"],
        plot_bgcolor=COLORS["background"],
        height=height,
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=show_legend,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(0,0,0,0.5)",
            font=dict(color="white", size=11),
        ),
    )

    # Add info annotation
    if show_info_panel:
        info_text = (
            f"<b>Dimensions:</b> {b:.0f} × {D:.0f} × {span:.0f} mm<br>"
            f"<b>Bottom bars:</b> {len(bottom_bars)} @ Ø{bar_diameter:.0f}mm<br>"
            f"<b>Top bars:</b> {len(top_bars)} @ Ø{bar_diameter:.0f}mm<br>"
            f"<b>Stirrups:</b> {len(stirrup_positions)} @ Ø{stirrup_diameter:.0f}mm"
        )
        fig.add_annotation(
            text=info_text,
            xref="paper",
            yref="paper",
            x=0.99,
            y=0.01,
            xanchor="right",
            yanchor="bottom",
            showarrow=False,
            bgcolor="rgba(0,0,0,0.7)",
            bordercolor="rgba(255,255,255,0.2)",
            borderwidth=1,
            borderpad=8,
            font=dict(size=11, color="white"),
            align="left",
        )

    return fig


def create_beam_3d_from_geometry(
    geometry: Beam3DGeometry,
    height: int = 500,
    show_legend: bool = True,
) -> go.Figure:
    """
    Create 3D figure from Beam3DGeometry object.

    This is a convenience wrapper that extracts data from
    a Beam3DGeometry dataclass and calls create_beam_3d_figure.

    Args:
        geometry: Beam3DGeometry object from geometry_3d module
        height: Figure height in pixels
        show_legend: Whether to show legend

    Returns:
        Plotly Figure object

    Example:
        >>> from structural_lib.visualization.geometry_3d import beam_to_3d_geometry
        >>> geometry = beam_to_3d_geometry(detailing_result)
        >>> fig = create_beam_3d_from_geometry(geometry)
    """
    return create_beam_3d_from_dict(geometry.to_dict(), height, show_legend)


def create_beam_3d_from_dict(
    geometry_dict: dict[str, Any],
    height: int = 500,
    show_legend: bool = True,
) -> go.Figure:
    """
    Create 3D figure from geometry dictionary.

    This function accepts the JSON-serialized format from
    Beam3DGeometry.to_dict() and creates a Plotly figure.

    Args:
        geometry_dict: Dict matching BeamGeometry3D JSON schema
        height: Figure height in pixels
        show_legend: Whether to show legend

    Returns:
        Plotly Figure object

    Example:
        >>> geometry_dict = {
        ...     "dimensions": {"b": 300, "D": 450, "span": 4000},
        ...     "rebars": [...],
        ...     "stirrups": [...],
        ... }
        >>> fig = create_beam_3d_from_dict(geometry_dict)
    """
    dims = geometry_dict.get("dimensions", {})
    b = dims.get("b", 300)
    D = dims.get("D", 450)
    span = dims.get("span", 4000)

    # Extract rebar positions
    bottom_bars = []
    top_bars = []
    bar_diameter = 16.0

    for rebar in geometry_dict.get("rebars", []):
        bar_type = rebar.get("barType", "bottom")
        segments = rebar.get("segments", [])
        diameter = rebar.get("diameter", 16)
        bar_diameter = diameter  # Use last diameter

        for seg in segments:
            start = seg.get("start", {})
            y = start.get("y", 0)
            z = start.get("z", 0)
            pos = (0, y, z)

            if bar_type == "top":
                top_bars.append(pos)
            else:
                bottom_bars.append(pos)

    # Extract stirrup positions
    stirrup_positions = []
    stirrup_diameter = 8.0

    for stirrup in geometry_dict.get("stirrups", []):
        stirrup_positions.append(stirrup.get("positionX", 0))
        stirrup_diameter = stirrup.get("diameter", 8)

    # Get cover from metadata
    metadata = geometry_dict.get("metadata", {})
    cover = metadata.get("cover", 40)

    return create_beam_3d_figure(
        b=b,
        D=D,
        span=span,
        bottom_bars=bottom_bars if bottom_bars else None,
        top_bars=top_bars if top_bars else None,
        bar_diameter=bar_diameter,
        stirrup_positions=stirrup_positions if stirrup_positions else None,
        stirrup_diameter=stirrup_diameter,
        cover=cover,
        height=height,
        show_legend=show_legend,
    )


# =============================================================================
# Caching and Performance Utilities
# =============================================================================


def compute_geometry_hash(geometry_dict: dict[str, Any]) -> str:
    """
    Compute a hash for geometry to enable efficient caching.

    Supports both:
    - Flat dict: {"b": 300, "D": 450, "span": 4000, "bottom_bars": [...], ...}
    - Nested JSON schema: {"dimensions": {...}, "rebars": [...], "stirrups": [...]}

    Args:
        geometry_dict: Geometry dictionary (flat or nested format)

    Returns:
        MD5 hash string (32 chars)

    Performance:
        <1ms for typical geometry

    Example:
        >>> hash_val = compute_geometry_hash({"b": 300, "D": 450, "span": 4000})
        >>> len(hash_val) == 32
    """
    hash_parts = []

    # Handle flat dict format (from beam_design.py)
    if "b" in geometry_dict:
        hash_parts.append(f"b{geometry_dict.get('b', 0)}")
        hash_parts.append(f"D{geometry_dict.get('D', 0)}")
        hash_parts.append(f"span{geometry_dict.get('span', 0)}")
        hash_parts.append(f"bar_dia{geometry_dict.get('bar_dia', 0)}")
        hash_parts.append(f"stirrup_dia{geometry_dict.get('stirrup_dia', 0)}")
        hash_parts.append(f"cover{geometry_dict.get('cover', 0)}")

        # Bottom bars
        bottom_bars = geometry_dict.get("bottom_bars", [])
        hash_parts.append(f"bb{len(bottom_bars)}")
        for bar in bottom_bars[:10]:
            if len(bar) >= 3:
                hash_parts.append(f"{bar[1]:.0f}_{bar[2]:.0f}")

        # Top bars
        top_bars = geometry_dict.get("top_bars", [])
        hash_parts.append(f"tb{len(top_bars)}")
        for bar in top_bars[:10]:
            if len(bar) >= 3:
                hash_parts.append(f"{bar[1]:.0f}_{bar[2]:.0f}")

        # Stirrup positions
        stirrup_pos = geometry_dict.get("stirrup_positions", [])
        hash_parts.append(f"sp{len(stirrup_pos)}")
        if stirrup_pos:
            hash_parts.append(
                f"{stirrup_pos[0]}_{stirrup_pos[-1] if len(stirrup_pos) > 1 else stirrup_pos[0]}"
            )

    # Handle nested JSON schema format (from JSON contract)
    elif "dimensions" in geometry_dict:
        dims = geometry_dict.get("dimensions", {})
        hash_parts.append(f"b{dims.get('b', 0)}")
        hash_parts.append(f"D{dims.get('D', 0)}")
        hash_parts.append(f"span{dims.get('span', 0)}")

        # Rebars
        rebars = geometry_dict.get("rebars", [])
        hash_parts.append(f"r{len(rebars)}")
        for rebar in rebars[:10]:
            segs = rebar.get("segments", [])
            if segs:
                s = segs[0].get("start", {})
                hash_parts.append(f"{s.get('y', 0):.0f}_{s.get('z', 0):.0f}")

        # Stirrups
        stirrups = geometry_dict.get("stirrups", [])
        hash_parts.append(f"s{len(stirrups)}")
        if stirrups:
            hash_parts.append(f"{stirrups[0].get('positionX', 0):.0f}")
            if len(stirrups) > 1:
                hash_parts.append(f"{stirrups[-1].get('positionX', 0):.0f}")

    hash_input = "_".join(hash_parts)
    return hashlib.md5(hash_input.encode()).hexdigest()


# =============================================================================
# Helper Functions
# =============================================================================


def _create_box_wireframe(
    span: float,
    half_width: float,
    depth: float,
) -> go.Scatter3d:
    """Create wireframe edges for the concrete box."""
    # Define the 12 edges of a box
    edges = [
        # Bottom face
        [(0, -half_width, 0), (span, -half_width, 0)],
        [(span, -half_width, 0), (span, half_width, 0)],
        [(span, half_width, 0), (0, half_width, 0)],
        [(0, half_width, 0), (0, -half_width, 0)],
        # Top face
        [(0, -half_width, depth), (span, -half_width, depth)],
        [(span, -half_width, depth), (span, half_width, depth)],
        [(span, half_width, depth), (0, half_width, depth)],
        [(0, half_width, depth), (0, -half_width, depth)],
        # Vertical edges
        [(0, -half_width, 0), (0, -half_width, depth)],
        [(span, -half_width, 0), (span, -half_width, depth)],
        [(span, half_width, 0), (span, half_width, depth)],
        [(0, half_width, 0), (0, half_width, depth)],
    ]

    x_vals = []
    y_vals = []
    z_vals = []

    for edge in edges:
        x_vals.extend([edge[0][0], edge[1][0], None])
        y_vals.extend([edge[0][1], edge[1][1], None])
        z_vals.extend([edge[0][2], edge[1][2], None])

    return go.Scatter3d(
        x=x_vals,
        y=y_vals,
        z=z_vals,
        mode="lines",
        line=dict(color=COLORS["concrete_edge"], width=2),
        hoverinfo="skip",
        showlegend=False,
    )


# =============================================================================
# Multi-Beam Building View (Session 45)
# =============================================================================


def create_multi_beam_3d_figure(
    beam_data: list[dict[str, Any]],
    show_forces: bool = True,
    title: str = "Building View",
    height: int = 600,
) -> go.Figure:
    """Create 3D building view with multiple beams.

    This function creates a Plotly figure showing all beams in their
    actual 3D positions, with optional force-based coloring.

    Args:
        beam_data: List of beam dictionaries with keys:
            - id: Beam identifier
            - x1, y1, z1: Start point coordinates (mm)
            - x2, y2, z2: End point coordinates (mm)
            - width: Section width (mm)
            - depth: Section depth (mm)
            - mu_knm: Optional moment for coloring
            - vu_kn: Optional shear for coloring
        show_forces: Color beams by force utilization
        title: Plot title
        height: Figure height in pixels

    Returns:
        Plotly Figure with multi-beam 3D visualization

    Performance:
        - <100ms for 150 beams (simplified box geometry)
        - Uses hover info instead of full mesh for scalability
    """
    traces = []

    # Calculate force ranges for color scaling
    if show_forces and beam_data:
        max_mu = max((b.get("mu_knm", 0) for b in beam_data), default=1)
        max_mu = max(max_mu, 1)  # Avoid division by zero

    # Define color scale (low to high force)
    def get_force_color(mu: float) -> str:
        """Get color based on force magnitude."""
        if not show_forces or max_mu == 0:
            return "rgba(100, 149, 237, 0.7)"  # Cornflower blue

        # Normalize 0-1
        ratio = min(mu / max_mu, 1.0)

        # Green (low) → Yellow (medium) → Red (high)
        if ratio < 0.5:
            # Green to Yellow
            r = int(255 * (ratio * 2))
            g = 200
            b = 50
        else:
            # Yellow to Red
            r = 255
            g = int(200 * (1 - (ratio - 0.5) * 2))
            b = 50

        return f"rgba({r}, {g}, {b}, 0.8)"

    # Create beam boxes
    for beam in beam_data:
        x1, y1, z1 = beam["x1"], beam["y1"], beam["z1"]
        x2, y2, z2 = beam["x2"], beam["y2"], beam["z2"]
        width = beam.get("width", 230)
        depth = beam.get("depth", 450)
        beam_id = beam.get("id", "Beam")
        story = beam.get("story", "")
        mu = beam.get("mu_knm", 0)
        vu = beam.get("vu_kn", 0)

        # Calculate beam direction vector
        dx = x2 - x1
        dy = y2 - y1
        dz = z2 - z1
        length = math.sqrt(dx * dx + dy * dy + dz * dz)

        if length < 1:
            continue  # Skip zero-length beams

        # Normalize direction
        dx_n, dy_n, dz_n = dx / length, dy / length, dz / length

        # Calculate perpendicular vectors for width/depth
        # For horizontal beams, use Z-up as reference
        if abs(dz_n) < 0.99:
            # Cross with Z to get perpendicular in XY plane
            perp_x = -dy_n
            perp_y = dx_n
            perp_z = 0
            perp_len = math.sqrt(perp_x * perp_x + perp_y * perp_y)
            if perp_len > 0:
                perp_x /= perp_len
                perp_y /= perp_len
        else:
            # Vertical beam - use X as perpendicular
            perp_x, perp_y, perp_z = 1, 0, 0

        # Half dimensions
        hw = width / 2
        hd = depth / 2

        # Build 8 corners of the box
        # offset along perpendicular (width) and up (depth)
        corners = []
        for i in range(2):  # start/end
            cx = x1 + i * dx
            cy = y1 + i * dy
            cz = z1 + i * dz

            for w_sign in [-1, 1]:  # width direction
                for d_sign in [-1, 1]:  # depth direction
                    px = cx + w_sign * hw * perp_x
                    py = cy + w_sign * hw * perp_y
                    pz = cz + d_sign * hd  # Depth in Z

                    corners.append([px, py, pz])

        # Create mesh faces (6 faces, 2 triangles each = 12 triangles)
        # Corner indices: 0-3 at start, 4-7 at end
        # At each end: corners arranged as (-w,-d), (-w,+d), (+w,-d), (+w,+d)
        # So: 0=(-w,-d,start), 1=(-w,+d,start), 2=(+w,-d,start), 3=(+w,+d,start)
        #     4=(-w,-d,end), 5=(-w,+d,end), 6=(+w,-d,end), 7=(+w,+d,end)

        # Define triangles by corner indices
        i_vals = []
        j_vals = []
        k_vals = []

        faces = [
            # Start face
            (0, 1, 2), (1, 3, 2),
            # End face
            (4, 6, 5), (5, 6, 7),
            # Bottom face (-d)
            (0, 2, 4), (2, 6, 4),
            # Top face (+d)
            (1, 5, 3), (3, 5, 7),
            # Left face (-w)
            (0, 4, 1), (1, 4, 5),
            # Right face (+w)
            (2, 3, 6), (3, 7, 6),
        ]

        for face in faces:
            i_vals.append(face[0])
            j_vals.append(face[1])
            k_vals.append(face[2])

        x_vals = [c[0] for c in corners]
        y_vals = [c[1] for c in corners]
        z_vals = [c[2] for c in corners]

        color = get_force_color(mu)

        # Create mesh trace for this beam
        hover_text = (
            f"<b>{beam_id}</b><br>"
            f"Story: {story}<br>"
            f"Size: {width}×{depth} mm<br>"
            f"Mu: {mu:.1f} kN·m<br>"
            f"Vu: {vu:.1f} kN"
        )

        traces.append(
            go.Mesh3d(
                x=x_vals,
                y=y_vals,
                z=z_vals,
                i=i_vals,
                j=j_vals,
                k=k_vals,
                color=color,
                opacity=0.85,
                hoverinfo="text",
                hovertext=hover_text,
                name=beam_id,
                showlegend=False,
            )
        )

    # Create figure
    fig = go.Figure(data=traces)

    # Configure layout
    fig.update_layout(
        title=dict(text=title, x=0.5),
        height=height,
        scene=dict(
            aspectmode="data",
            xaxis=dict(
                title="X (mm)",
                showgrid=True,
                gridcolor="rgba(128,128,128,0.2)",
                showbackground=False,
            ),
            yaxis=dict(
                title="Y (mm)",
                showgrid=True,
                gridcolor="rgba(128,128,128,0.2)",
                showbackground=False,
            ),
            zaxis=dict(
                title="Z (mm)",
                showgrid=True,
                gridcolor="rgba(128,128,128,0.2)",
                showbackground=False,
            ),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2),
                up=dict(x=0, y=0, z=1),
            ),
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    # Add color scale legend if showing forces
    if show_forces and beam_data:
        # Add annotation for color scale
        fig.add_annotation(
            x=0.02,
            y=0.98,
            xref="paper",
            yref="paper",
            text=(
                f"<b>Force Scale</b><br>"
                f"🟢 Low (0 kN·m)<br>"
                f"🟡 Medium<br>"
                f"🔴 High ({max_mu:.0f} kN·m)"
            ),
            showarrow=False,
            font=dict(size=10),
            align="left",
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0.3)",
            borderwidth=1,
        )

    return fig
