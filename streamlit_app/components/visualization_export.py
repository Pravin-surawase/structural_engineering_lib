# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
CAD-Quality Export Module — PyVista Integration.

This module provides high-quality export capabilities for beam visualizations
using PyVista (VTK-based). It's designed as an optional enhancement to the
primary Plotly visualization.

Key Features:
    - STL export for CAD software import
    - High-resolution screenshot rendering (up to 4K)
    - VTK export for engineering tools
    - PBR (Physically Based Rendering) materials

Requirements:
    pip install pyvista stpyvista

Usage:
    >>> from streamlit_app.components.visualization_export import (
    ...     export_beam_stl,
    ...     render_beam_screenshot,
    ...     check_pyvista_available,
    ... )
    >>> if check_pyvista_available():
    ...     render_beam_screenshot(geometry, 'beam.png', resolution=2048)

Note:
    PyVista requires Xvfb on headless servers (Streamlit Cloud).
    Use stpyvista.utils.start_xvfb() for cloud deployment.
"""

from __future__ import annotations

import logging
import math
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from structural_lib.visualization.geometry_3d import Beam3DGeometry

logger = logging.getLogger(__name__)

__all__ = [
    "check_pyvista_available",
    "export_beam_stl",
    "export_beam_vtk",
    "render_beam_screenshot",
    "create_pyvista_plotter",
    "geometry_to_pyvista_meshes",
    "show_pyvista_in_streamlit",
    "SCREENSHOT_RESOLUTIONS",
    "DEFAULT_MATERIALS",
    "_create_beam_box",  # For testing
]


# =============================================================================
# Availability Check
# =============================================================================


def check_pyvista_available() -> bool:
    """
    Check if PyVista is available for import.

    Returns:
        True if pyvista can be imported, False otherwise.

    Example:
        >>> if check_pyvista_available():
        ...     render_beam_screenshot(geometry, 'output.png')
        ... else:
        ...     st.warning("Install pyvista for CAD export: pip install pyvista")
    """
    try:
        import pyvista  # noqa: F401
        return True
    except ImportError:
        return False


def _ensure_pyvista() -> None:
    """Raise ImportError with helpful message if PyVista not available."""
    if not check_pyvista_available():
        raise ImportError(
            "PyVista is required for CAD export. "
            "Install with: pip install pyvista stpyvista"
        )


# =============================================================================
# Color Constants (matches visualizations_3d.py)
# =============================================================================

COLORS = {
    "concrete": "#D1D5DB",  # Light gray
    "rebar_bottom": "#DC2626",  # Red for tension steel
    "rebar_top": "#1E40AF",  # Blue for compression steel
    "stirrup": "#16A34A",  # Green for stirrups
    "background": "#1a1a2e",  # Dark background
}

# =============================================================================
# Screenshot Resolution Presets
# =============================================================================

SCREENSHOT_RESOLUTIONS: dict[str, tuple[int, int]] = {
    "HD": (1280, 720),
    "Full HD": (1920, 1080),
    "2K": (2560, 1440),
    "4K": (3840, 2160),
}

# =============================================================================
# Material Configurations for PBR Rendering
# =============================================================================

DEFAULT_MATERIALS: dict[str, dict[str, Any]] = {
    "concrete": {
        "color": "#D1D5DB",
        "metallic": 0.0,
        "roughness": 0.8,
        "opacity": 1.0,
    },
    "rebar": {
        "color": "#DC2626",
        "metallic": 0.8,
        "roughness": 0.3,
        "opacity": 1.0,
    },
    "stirrup": {
        "color": "#16A34A",
        "metallic": 0.7,
        "roughness": 0.4,
        "opacity": 1.0,
    },
}


# =============================================================================
# Mesh Generation Helpers
# =============================================================================


def _create_beam_box(
    start: list[float],
    end: list[float],
    width: float,
    depth: float,
) -> Any | None:
    """
    Create a beam box mesh from start/end points and dimensions.

    Args:
        start: [x, y, z] start point in mm
        end: [x, y, z] end point in mm
        width: Beam width in mm
        depth: Beam depth in mm

    Returns:
        PyVista mesh or None if invalid dimensions
    """
    if not check_pyvista_available():
        return None

    import numpy as np

    start_arr = np.array(start)
    end_arr = np.array(end)
    length = np.linalg.norm(end_arr - start_arr)

    # Validate dimensions
    if length < 1 or width <= 0 or depth <= 0:
        return None

    try:
        # Use bounds-based box for simplicity
        x_min = min(start[0], end[0])
        x_max = max(start[0], end[0])
        y_min = start[1] - width / 2
        y_max = start[1] + width / 2
        z_min = start[2]
        z_max = start[2] + depth

        # Ensure non-zero dimensions
        if x_max - x_min < 1:
            x_max = x_min + length
        if y_max - y_min < 1:
            y_max = y_min + width
        if z_max - z_min < 1:
            z_max = z_min + depth

        return _create_box_mesh(x_min, x_max, y_min, y_max, z_min, z_max)
    except Exception as e:
        logger.warning(f"Failed to create beam box: {e}")
        return None


def _create_box_mesh(
    x_min: float, x_max: float,
    y_min: float, y_max: float,
    z_min: float, z_max: float,
) -> Any:
    """Create a PyVista box mesh from bounds."""
    import pyvista as pv

    return pv.Box(bounds=(x_min, x_max, y_min, y_max, z_min, z_max))


def _create_cylinder_mesh(
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    radius: float,
) -> Any:
    """Create a PyVista cylinder mesh between two points."""
    import pyvista as pv
    import numpy as np

    # Calculate direction and length
    start_arr = np.array(start)
    end_arr = np.array(end)
    direction = end_arr - start_arr
    length = np.linalg.norm(direction)

    if length < 0.001:
        return pv.PolyData()  # Empty mesh for zero-length

    # Center point
    center = (start_arr + end_arr) / 2

    # Create cylinder
    cylinder = pv.Cylinder(
        center=center,
        direction=direction,
        radius=radius,
        height=length,
        resolution=16,
        capping=True,
    )

    return cylinder


def _create_stirrup_mesh(
    x_pos: float,
    b: float,  # beam width
    d: float,  # beam depth
    cover: float,
    bar_diameter: float = 8.0,
) -> Any:
    """Create a rectangular stirrup mesh at given x position."""
    import pyvista as pv

    # Stirrup dimensions (inside cover)
    inner_width = b - 2 * cover
    inner_height = d - 2 * cover
    radius = bar_diameter / 2

    # Create the four sides of the stirrup
    meshes = []

    # Bottom horizontal
    bottom = _create_cylinder_mesh(
        (x_pos, -inner_width/2, cover),
        (x_pos, inner_width/2, cover),
        radius,
    )
    meshes.append(bottom)

    # Top horizontal
    top = _create_cylinder_mesh(
        (x_pos, -inner_width/2, d - cover),
        (x_pos, inner_width/2, d - cover),
        radius,
    )
    meshes.append(top)

    # Left vertical
    left = _create_cylinder_mesh(
        (x_pos, -inner_width/2, cover),
        (x_pos, -inner_width/2, d - cover),
        radius,
    )
    meshes.append(left)

    # Right vertical
    right = _create_cylinder_mesh(
        (x_pos, inner_width/2, cover),
        (x_pos, inner_width/2, d - cover),
        radius,
    )
    meshes.append(right)

    # Combine all parts
    combined = meshes[0]
    for mesh in meshes[1:]:
        combined = combined.merge(mesh)

    return combined


# =============================================================================
# Geometry Conversion
# =============================================================================


def geometry_to_pyvista_meshes(geometry: dict[str, Any]) -> dict[str, Any]:
    """
    Convert beam geometry dictionary to PyVista meshes.

    Args:
        geometry: Dictionary with keys:
            - b, D, span: Beam dimensions in mm
            - bottom_bars: List of (x, y, z, diameter) tuples
            - top_bars: List of (x, y, z, diameter) tuples
            - stirrup_positions: List of x positions
            - cover: Clear cover in mm

    Returns:
        Dictionary with PyVista meshes:
            - concrete: Box mesh
            - bottom_bars: List of cylinder meshes
            - top_bars: List of cylinder meshes
            - stirrups: List of stirrup meshes

    Example:
        >>> meshes = geometry_to_pyvista_meshes({
        ...     'b': 300, 'D': 450, 'span': 4000,
        ...     'bottom_bars': [(0, -96, 52, 16), (0, 0, 52, 16), (0, 96, 52, 16)],
        ...     'top_bars': [(0, -96, 398, 12), (0, 96, 398, 12)],
        ...     'stirrup_positions': [100, 200, 300],
        ...     'cover': 40,
        ... })
    """
    _ensure_pyvista()

    b = geometry.get('b', 300)
    d = geometry.get('D', 450)
    span = geometry.get('span', 4000)
    cover = geometry.get('cover', 40)

    result = {}

    # Concrete beam
    result['concrete'] = _create_box_mesh(
        x_min=0, x_max=span,
        y_min=-b/2, y_max=b/2,
        z_min=0, z_max=d,
    )

    # Bottom bars (tension)
    bottom_bars = []
    for bar in geometry.get('bottom_bars', []):
        if len(bar) >= 4:
            x_start, y, z, dia = bar[:4]
            x_end = span  # Full span
        elif len(bar) == 3:
            x_start, y, z = bar
            dia = 16  # Default diameter
            x_end = span
        else:
            continue

        mesh = _create_cylinder_mesh(
            start=(x_start, y, z),
            end=(x_end, y, z),
            radius=dia / 2,
        )
        bottom_bars.append(mesh)
    result['bottom_bars'] = bottom_bars

    # Top bars (compression)
    top_bars = []
    for bar in geometry.get('top_bars', []):
        if len(bar) >= 4:
            x_start, y, z, dia = bar[:4]
            x_end = span
        elif len(bar) == 3:
            x_start, y, z = bar
            dia = 12
            x_end = span
        else:
            continue

        mesh = _create_cylinder_mesh(
            start=(x_start, y, z),
            end=(x_end, y, z),
            radius=dia / 2,
        )
        top_bars.append(mesh)
    result['top_bars'] = top_bars

    # Stirrups
    stirrups = []
    stirrup_dia = geometry.get('stirrup_diameter', 8)
    for x_pos in geometry.get('stirrup_positions', []):
        mesh = _create_stirrup_mesh(x_pos, b, d, cover, stirrup_dia)
        stirrups.append(mesh)
    result['stirrups'] = stirrups

    return result


# =============================================================================
# Export Functions
# =============================================================================


def export_beam_stl(
    geometry: dict[str, Any],
    output_path: str | Path,
    include_rebar: bool = True,
) -> Path:
    """
    Export beam geometry to STL file for CAD import.

    Args:
        geometry: Beam geometry dictionary (see geometry_to_pyvista_meshes)
        output_path: Path for output STL file
        include_rebar: Include reinforcement bars in export

    Returns:
        Path to the created STL file

    Example:
        >>> path = export_beam_stl(geometry, 'beam_with_rebar.stl')
        >>> print(f"Exported to {path}")
    """
    _ensure_pyvista()
    import pyvista as pv

    output_path = Path(output_path)
    meshes = geometry_to_pyvista_meshes(geometry)

    # Combine all meshes
    combined = meshes['concrete']

    if include_rebar:
        for bar in meshes['bottom_bars']:
            combined = combined.merge(bar)
        for bar in meshes['top_bars']:
            combined = combined.merge(bar)
        for stirrup in meshes['stirrups']:
            combined = combined.merge(stirrup)

    # Export
    combined.save(str(output_path))
    logger.info(f"Exported beam to STL: {output_path}")

    return output_path


def export_beam_vtk(
    geometry: dict[str, Any],
    output_path: str | Path,
) -> Path:
    """
    Export beam geometry to VTK file for engineering tools.

    Args:
        geometry: Beam geometry dictionary
        output_path: Path for output VTK file

    Returns:
        Path to the created VTK file
    """
    _ensure_pyvista()

    output_path = Path(output_path)
    meshes = geometry_to_pyvista_meshes(geometry)

    # Combine all meshes
    combined = meshes['concrete']
    for bar in meshes['bottom_bars']:
        combined = combined.merge(bar)
    for bar in meshes['top_bars']:
        combined = combined.merge(bar)
    for stirrup in meshes['stirrups']:
        combined = combined.merge(stirrup)

    # Export as VTK
    combined.save(str(output_path))
    logger.info(f"Exported beam to VTK: {output_path}")

    return output_path


# =============================================================================
# Screenshot Rendering
# =============================================================================


def create_pyvista_plotter(
    geometry: dict[str, Any],
    background: str = COLORS["background"],
    use_pbr: bool = True,
) -> Any:
    """
    Create a PyVista plotter with beam visualization.

    Args:
        geometry: Beam geometry dictionary
        background: Background color (hex)
        use_pbr: Use PBR (physically based rendering) materials

    Returns:
        Configured pyvista.Plotter object

    Note:
        For Streamlit integration, use with stpyvista:
        >>> import stpyvista
        >>> plotter = create_pyvista_plotter(geometry)
        >>> stpyvista.stpyvista(plotter)
    """
    _ensure_pyvista()
    import pyvista as pv

    plotter = pv.Plotter()
    plotter.set_background(background)

    meshes = geometry_to_pyvista_meshes(geometry)

    # Add concrete beam (semi-transparent)
    plotter.add_mesh(
        meshes['concrete'],
        color=COLORS["concrete"],
        opacity=0.3,
        pbr=use_pbr,
        roughness=0.8,
        metallic=0.0,
    )

    # Add bottom bars (tension - red)
    for bar in meshes['bottom_bars']:
        plotter.add_mesh(
            bar,
            color=COLORS["rebar_bottom"],
            pbr=use_pbr,
            roughness=0.3,
            metallic=0.8,
        )

    # Add top bars (compression - blue)
    for bar in meshes['top_bars']:
        plotter.add_mesh(
            bar,
            color=COLORS["rebar_top"],
            pbr=use_pbr,
            roughness=0.3,
            metallic=0.8,
        )

    # Add stirrups (green)
    for stirrup in meshes['stirrups']:
        plotter.add_mesh(
            stirrup,
            color=COLORS["stirrup"],
            pbr=use_pbr,
            roughness=0.4,
            metallic=0.6,
        )

    # Camera and lighting
    plotter.camera_position = 'iso'
    plotter.add_light(pv.Light(position=(1, 1, 1), intensity=0.8))

    return plotter


def render_beam_screenshot(
    geometry: dict[str, Any],
    output_path: str | Path,
    resolution: int = 2048,
    background: str = COLORS["background"],
    camera_position: str = 'iso',
) -> Path:
    """
    Render high-quality beam screenshot using PyVista.

    Args:
        geometry: Beam geometry dictionary
        output_path: Path for output PNG file
        resolution: Target resolution (width in pixels)
        background: Background color (hex)
        camera_position: Camera angle ('iso', 'xy', 'xz', 'yz')

    Returns:
        Path to the created PNG file

    Example:
        >>> path = render_beam_screenshot(geometry, 'beam_hq.png', resolution=4096)
        >>> print(f"Rendered to {path}")

    Note:
        Requires Xvfb on headless servers. Use:
        >>> from stpyvista.utils import start_xvfb
        >>> start_xvfb()
    """
    _ensure_pyvista()
    import pyvista as pv

    output_path = Path(output_path)

    # Enable off-screen rendering
    pv.OFF_SCREEN = True

    plotter = pv.Plotter(off_screen=True)
    plotter.set_background(background)

    meshes = geometry_to_pyvista_meshes(geometry)

    # Add meshes with PBR materials
    plotter.add_mesh(
        meshes['concrete'],
        color=COLORS["concrete"],
        opacity=0.3,
        pbr=True,
        roughness=0.8,
    )

    for bar in meshes['bottom_bars']:
        plotter.add_mesh(bar, color=COLORS["rebar_bottom"],
                        pbr=True, metallic=0.8, roughness=0.3)

    for bar in meshes['top_bars']:
        plotter.add_mesh(bar, color=COLORS["rebar_top"],
                        pbr=True, metallic=0.8, roughness=0.3)

    for stirrup in meshes['stirrups']:
        plotter.add_mesh(stirrup, color=COLORS["stirrup"],
                        pbr=True, metallic=0.6, roughness=0.4)

    # Configure camera
    plotter.camera_position = camera_position
    plotter.add_light(pv.Light(position=(1, 1, 1), intensity=0.8))

    # Render at high resolution
    scale = max(1, resolution // 800)
    plotter.screenshot(str(output_path), scale=scale)
    plotter.close()

    logger.info(f"Rendered screenshot: {output_path} (scale={scale})")

    return output_path


# =============================================================================
# Streamlit Integration Helper
# =============================================================================


def show_pyvista_in_streamlit(geometry: dict[str, Any], key: str = "pyvista") -> None:
    """
    Display PyVista visualization in Streamlit using stpyvista.

    Args:
        geometry: Beam geometry dictionary
        key: Unique key for Streamlit component

    Note:
        Requires stpyvista: pip install stpyvista
        On Streamlit Cloud, Xvfb must be started first.

    Example:
        >>> import streamlit as st
        >>> if check_pyvista_available():
        ...     show_pyvista_in_streamlit(geometry)
    """
    try:
        import stpyvista
        from stpyvista.utils import start_xvfb
        import streamlit as st

        # Ensure Xvfb is running (for headless servers)
        if "IS_XVFB_RUNNING" not in st.session_state:
            try:
                start_xvfb()
                st.session_state.IS_XVFB_RUNNING = True
            except Exception as e:
                logger.warning(f"Could not start Xvfb: {e}")

        plotter = create_pyvista_plotter(geometry)
        stpyvista.stpyvista(plotter, key=key)

    except ImportError as e:
        import streamlit as st
        st.warning(f"stpyvista not available: {e}")
        st.info("Install with: pip install stpyvista")
