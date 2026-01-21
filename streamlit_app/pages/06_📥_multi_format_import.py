# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Multi-Format Import Page
========================

Import beam data from multiple structural analysis software formats:
- ETABS CSV (Connectivity - Frame, Element Forces - Beams)
- SAFE CSV (strip beam forces)
- STAAD.Pro (input/output files)
- Generic CSV (custom column mapping)

Features:
- Format auto-detection with manual override
- Unified column mapping across all formats
- Batch design with progress tracking
- Export to canonical JSON format

Integration:
    Analysis Software → Export → CSV → This Page → Design → 3D Viewer

Author: Session 42 Agent
Task: TASK-DATA-001 (Multi-format import integration)
Status: ✅ IMPLEMENTED
"""

from __future__ import annotations

import math
import sys
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Fix import path
current_file = Path(__file__).resolve()
pages_dir = current_file.parent
streamlit_app_dir = pages_dir.parent

if str(streamlit_app_dir) not in sys.path:
    sys.path.insert(0, str(streamlit_app_dir))

python_lib_dir = streamlit_app_dir.parent / "Python"
if str(python_lib_dir) not in sys.path:
    sys.path.insert(0, str(python_lib_dir))

from utils.layout import setup_page, page_header, section_header
from utils.theme_manager import initialize_theme
from utils.api_wrapper import cached_design
from utils.loading_states import loading_context
from components.visualizations_3d import create_beam_3d_figure

# Import adapter system
try:
    from structural_lib.adapters import (
        ETABSAdapter,
        SAFEAdapter,
        STAADAdapter,
        GenericCSVAdapter,
        ManualInputAdapter,
    )
    from structural_lib.models import (
        BeamGeometry,
        BeamForces,
        DesignDefaults,
    )

    ADAPTERS_AVAILABLE = True
    ADAPTERS = {
        "ETABS": ETABSAdapter(),
        "SAFE": SAFEAdapter(),
        "STAAD.Pro": STAADAdapter(),
        "Generic CSV": GenericCSVAdapter(),
    }
except ImportError as e:
    ADAPTERS_AVAILABLE = False
    ADAPTERS = {}
    import traceback
    _import_error = str(e)

# Import DXF export module
try:
    from structural_lib.dxf_export import (
        quick_dxf_bytes,
        generate_multi_beam_dxf,
        EZDXF_AVAILABLE,
    )
    from structural_lib.detailing import BeamDetailingResult, create_beam_detailing
    HAS_DXF = True
except ImportError:
    HAS_DXF = False
    EZDXF_AVAILABLE = False

# Page setup
setup_page(title="Multi-Format Import | IS 456 Beam Design", icon="📥", layout="wide")
initialize_theme()

# =============================================================================
# Session State
# =============================================================================

if "mf_format" not in st.session_state:
    st.session_state.mf_format = "Auto-detect"
if "mf_beams" not in st.session_state:
    st.session_state.mf_beams = []  # list[BeamGeometry]
if "mf_forces" not in st.session_state:
    st.session_state.mf_forces = []  # list[BeamForces]
if "mf_design_results" not in st.session_state:
    st.session_state.mf_design_results = None
if "mf_defaults" not in st.session_state:
    st.session_state.mf_defaults = {
        "width_mm": 300,
        "depth_mm": 500,
        "fck_mpa": 25.0,
        "fy_mpa": 500.0,
        "cover_mm": 40.0,
    }
if "mf_selected_beam" not in st.session_state:
    st.session_state.mf_selected_beam = None  # Selected beam ID for detail view


# =============================================================================
# Helper Functions
# =============================================================================


def detect_format(file_content: str, filename: str) -> str:
    """Auto-detect the format based on content and filename."""
    filename_lower = filename.lower()
    content_lower = file_content.lower()

    # Check filename patterns
    if "staad" in filename_lower or ".std" in filename_lower:
        return "STAAD.Pro"

    # Check for ETABS-specific patterns in content
    etabs_patterns = ["story", "unique name", "m3", "v2", "output case"]
    if any(p in content_lower for p in etabs_patterns):
        return "ETABS"

    # Check for SAFE-specific patterns
    safe_patterns = ["strip", "m22", "v23", "span"]
    if any(p in content_lower for p in safe_patterns):
        return "SAFE"

    # Default to generic CSV
    return "Generic CSV"


def process_uploaded_files(
    geometry_file,
    forces_file,
    selected_format: str,
    defaults: dict[str, float],
) -> tuple[bool, str, list, list]:
    """Process uploaded files using the selected adapter.

    Returns:
        (success, message, beams_list, forces_list)
    """
    if not ADAPTERS_AVAILABLE:
        return False, f"Adapters not available: {_import_error}", [], []

    # Get the adapter
    format_key = selected_format
    if format_key not in ADAPTERS:
        return False, f"Unknown format: {format_key}", [], []

    adapter = ADAPTERS[format_key]
    beams = []
    forces = []

    # Create DesignDefaults from dict
    # Note: width_mm/depth_mm are section properties, not design defaults
    # They come from the CSV or are set per-beam by the adapter
    design_defaults = DesignDefaults(
        fck_mpa=defaults["fck_mpa"],
        fy_mpa=defaults["fy_mpa"],
        cover_mm=defaults["cover_mm"],
    )

    # Process geometry file
    if geometry_file is not None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            content = geometry_file.getvalue().decode("utf-8")
            f.write(content)
            temp_geom_path = f.name

        try:
            if adapter.can_handle(temp_geom_path):
                beams = adapter.load_geometry(temp_geom_path, defaults=design_defaults)
            else:
                return False, f"File not compatible with {format_key} adapter", [], []
        except Exception as e:
            return False, f"Error loading geometry: {e}", [], []
        finally:
            Path(temp_geom_path).unlink(missing_ok=True)

    # Process forces file
    if forces_file is not None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            content = forces_file.getvalue().decode("utf-8")
            f.write(content)
            temp_forces_path = f.name

        try:
            forces = adapter.load_forces(temp_forces_path)
        except Exception as e:
            return False, f"Error loading forces: {e}", [], []
        finally:
            Path(temp_forces_path).unlink(missing_ok=True)

    # Generate summary
    msg = f"✅ Loaded from {format_key}:"
    if beams:
        msg += f"\n- {len(beams)} beams with geometry"
    if forces:
        msg += f"\n- {len(forces)} force records"

    return True, msg, beams, forces


def beams_to_dataframe(beams: list[BeamGeometry]) -> pd.DataFrame:
    """Convert BeamGeometry list to DataFrame."""
    data = []
    for beam in beams:
        data.append({
            "ID": beam.id,
            "Label": beam.label,
            "Story": beam.story,
            "Length (m)": round(beam.length_m, 2),
            "Width (mm)": beam.section.width_mm,
            "Depth (mm)": beam.section.depth_mm,
            "fck (MPa)": beam.section.fck_mpa,
        })
    return pd.DataFrame(data)


def forces_to_dataframe(forces: list[BeamForces]) -> pd.DataFrame:
    """Convert BeamForces list to DataFrame."""
    data = []
    for force in forces:
        data.append({
            "Beam ID": force.id,
            "Load Case": force.load_case,
            "Mu (kN·m)": round(force.mu_knm, 2),
            "Vu (kN)": round(force.vu_kn, 2),
            "Pu (kN)": round(force.pu_kn, 2),
            "Stations": force.station_count,
        })
    return pd.DataFrame(data)


def get_governing_forces(
    forces: list[BeamForces],
    beam_id: str,
) -> tuple[float, float, str]:
    """Get governing (max) forces for a beam across all load cases."""
    beam_forces = [f for f in forces if f.id == beam_id]
    if not beam_forces:
        return 0.0, 0.0, ""

    # Find max moment and shear
    max_mu_force = max(beam_forces, key=lambda f: f.mu_knm)
    max_vu_force = max(beam_forces, key=lambda f: f.vu_kn)

    # Use case with higher moment as governing
    governing = max_mu_force.load_case

    return max_mu_force.mu_knm, max_vu_force.vu_kn, governing


def calculate_rebar_layout_for_beam(
    ast_mm2: float,
    b_mm: float,
    D_mm: float,
    span_mm: float,
    vu_kn: float = 50.0,
    cover_mm: float = 40.0,
    stirrup_dia: float = 8.0,
    fck: float = 25.0,
    fy: float = 500.0,
) -> dict[str, Any]:
    """Calculate rebar layout for a beam.

    Returns:
        dict with bottom_bars, top_bars, stirrup_positions, and summary info.
    """
    # Standard bar diameters and areas
    BAR_OPTIONS = [
        (12, 113.1),
        (16, 201.1),
        (20, 314.2),
        (25, 490.9),
        (32, 804.2),
    ]

    # Find optimal bar combination (prefer 3-5 bars)
    best_config = None
    for dia, area in BAR_OPTIONS:
        num_bars = math.ceil(ast_mm2 / area) if ast_mm2 > 0 else 2
        if 2 <= num_bars <= 6:
            ast_provided = num_bars * area
            best_config = (dia, num_bars, ast_provided)
            break

    if best_config is None:
        best_config = (16, 3, 3 * 201.1)

    bar_dia, num_bars, ast_provided = best_config

    # Calculate bar positions
    edge_dist = cover_mm + stirrup_dia + bar_dia / 2
    z_bottom = edge_dist
    z_top = D_mm - edge_dist
    available_width = b_mm - 2 * edge_dist

    bottom_bars = []
    if num_bars == 1:
        bottom_bars = [(0, 0, z_bottom)]
    elif num_bars == 2:
        bottom_bars = [(0, -available_width / 2, z_bottom), (0, available_width / 2, z_bottom)]
    else:
        spacing = available_width / max(num_bars - 1, 1)
        for i in range(num_bars):
            y = -available_width / 2 + i * spacing
            bottom_bars.append((0, y, z_bottom))

    # Top bars (2 hanger bars)
    top_bars = [
        (0, -available_width / 2, z_top),
        (0, available_width / 2, z_top),
    ]

    # Calculate stirrup spacing zones
    d_mm = D_mm - cover_mm - stirrup_dia - bar_dia / 2
    sv_base = min(200, max(100, 0.75 * d_mm))

    tau_v = (vu_kn * 1000) / max(b_mm * d_mm, 1)
    if tau_v > 0.5:
        sv_base = min(sv_base, 150)
    if tau_v > 1.0:
        sv_base = min(sv_base, 100)

    stirrup_positions = []
    zone_2d = 2 * d_mm
    sv_support = sv_base * 0.75

    x = 50
    while x < min(zone_2d, span_mm - 50):
        stirrup_positions.append(x)
        x += sv_support

    while x < max(span_mm - zone_2d, zone_2d):
        stirrup_positions.append(x)
        x += sv_base

    while x < span_mm - 50:
        stirrup_positions.append(x)
        x += sv_support

    summary = f"{num_bars}T{bar_dia} ({ast_provided:.0f} mm²)"
    spacing_summary = f"Stirrups: Ø{stirrup_dia}@{sv_support:.0f}mm (ends), @{sv_base:.0f}mm (mid)"

    return {
        "bottom_bars": bottom_bars,
        "top_bars": top_bars,
        "stirrup_positions": stirrup_positions,
        "bar_diameter": bar_dia,
        "stirrup_diameter": stirrup_dia,
        "ast_provided": ast_provided,
        "summary": summary,
        "spacing_summary": spacing_summary,
    }


def design_all_beams(
    beams: list[BeamGeometry],
    forces: list[BeamForces],
    progress_bar,
    status_text,
) -> pd.DataFrame:
    """Design all beams and return results DataFrame."""
    results = []
    total = len(beams)

    if total == 0:
        return pd.DataFrame(results)

    # Create lookup for forces by beam ID
    force_lookup = {}
    for force in forces:
        if force.id not in force_lookup:
            force_lookup[force.id] = []
        force_lookup[force.id].append(force)

    for idx, beam in enumerate(beams):
        progress = (idx + 1) / total
        progress_bar.progress(progress)
        status_text.text(f"Designing {beam.id}... ({idx + 1}/{total})")

        # Get forces for this beam
        mu, vu, case = get_governing_forces(forces, beam.id)

        if mu == 0 and vu == 0:
            # No forces found for this beam
            results.append({
                "ID": beam.id,
                "Story": beam.story,
                "Label": beam.label,
                "Load Case": "-",
                "Mu (kN·m)": 0,
                "Vu (kN)": 0,
                "b×D (mm)": f"{beam.section.width_mm}×{beam.section.depth_mm}",
                "Ast_req": "-",
                "Ast_prov": "-",
                "Status": "⚠️ No forces",
                "_is_safe": None,
            })
            continue

        try:
            result = cached_design(
                mu_knm=mu,
                vu_kn=vu,
                b_mm=beam.section.width_mm,
                D_mm=beam.section.depth_mm,
                d_mm=beam.section.depth_mm - beam.section.cover_mm,
                fck_nmm2=beam.section.fck_mpa,
                fy_nmm2=beam.section.fy_mpa,
            )

            flexure = result.get("flexure", {})
            shear = result.get("shear", {})
            is_safe = result.get("is_safe", False)

            bar_dia = flexure.get("bar_dia", 16)
            num_bars = flexure.get("num_bars", 3)
            bar_config = f"{num_bars}T{bar_dia}"

            results.append({
                "ID": beam.id,
                "Story": beam.story,
                "Label": beam.label,
                "Load Case": case,
                "Mu (kN·m)": round(mu, 1),
                "Vu (kN)": round(vu, 1),
                "b×D (mm)": f"{beam.section.width_mm}×{beam.section.depth_mm}",
                "Ast_req": round(flexure.get("ast_required", 0), 0),
                "Ast_prov": round(flexure.get("ast_provided", 0), 0),
                "Bars": bar_config,
                "Sv (mm)": shear.get("spacing", "-"),
                "Status": "✅ OK" if is_safe else "❌ FAIL",
                "_is_safe": is_safe,
            })

        except Exception as e:
            results.append({
                "ID": beam.id,
                "Story": beam.story,
                "Label": beam.label,
                "Load Case": case,
                "Mu (kN·m)": round(mu, 1),
                "Vu (kN)": round(vu, 1),
                "b×D (mm)": f"{beam.section.width_mm}×{beam.section.depth_mm}",
                "Ast_req": "-",
                "Ast_prov": "-",
                "Status": f"❌ {str(e)[:30]}",
                "_is_safe": False,
            })

    return pd.DataFrame(results)


def create_building_3d_view(
    beams: list[BeamGeometry],
    results_df: pd.DataFrame | None = None,
    color_mode: str = "Design Status",
    show_edges: bool = True,
) -> go.Figure:
    """Create a professional 3D building visualization with solid beam volumes.

    Features:
    - Real 3D beam volumes (not just lines) from geometry coordinates
    - Color coding by design status (pass/fail), story, or utilization
    - Hover information with beam details
    - Story grouping with visual separation
    - Professional dark theme with lighting effects
    - Semi-transparent concrete for visual depth

    Args:
        beams: List of BeamGeometry objects to visualize
        results_df: Optional DataFrame with design results
        color_mode: "Design Status", "By Story", or "Utilization"
        show_edges: Whether to show beam edge lines
    """
    fig = go.Figure()

    if not beams:
        return fig

    # Build result lookup for status coloring
    result_lookup = {}
    if results_df is not None and not results_df.empty:
        for _, row in results_df.iterrows():
            result_lookup[row["ID"]] = {
                "is_safe": row.get("_is_safe"),
                "mu": row.get("Mu (kN·m)", 0),
                "vu": row.get("Vu (kN)", 0),
                "bars": row.get("Bars", "-"),
                "status": row.get("Status", "-"),
                "ast_req": row.get("Ast_req", 0),
                "ast_prov": row.get("Ast_prov", 0),
            }

    # Group beams by story for legend organization
    stories = sorted(set(b.story for b in beams))
    story_colors = {}
    color_palette = [
        "#2196F3",  # Blue
        "#4CAF50",  # Green
        "#FF9800",  # Orange
        "#9C27B0",  # Purple
        "#00BCD4",  # Cyan
        "#E91E63",  # Pink
        "#FFEB3B",  # Yellow
        "#795548",  # Brown
    ]
    # Safe modulo: palette is never empty (hardcoded list)
    palette_len = len(color_palette)
    if palette_len > 0:
        for i, story in enumerate(stories):
            story_colors[story] = color_palette[i % palette_len]

    # Calculate building extents
    x_coords = []
    y_coords = []
    z_coords = []
    for beam in beams:
        x_coords.extend([beam.point1.x, beam.point2.x])
        y_coords.extend([beam.point1.y, beam.point2.y])
        z_coords.extend([beam.point1.z, beam.point2.z])

    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    z_min, z_max = min(z_coords), max(z_coords)

    # Add beams as 3D solid boxes
    for beam in beams:
        result = result_lookup.get(beam.id)

        # Determine color based on color mode
        if color_mode == "Design Status" and result:
            is_safe = result.get("is_safe")
            if is_safe is True:
                color = "rgba(76, 175, 80, 0.85)"  # Green - passed
                edge_color = "rgba(56, 142, 60, 1)"
            elif is_safe is False:
                color = "rgba(244, 67, 54, 0.85)"  # Red - failed
                edge_color = "rgba(198, 40, 40, 1)"
            else:
                color = "rgba(255, 152, 0, 0.85)"  # Orange - no forces
                edge_color = "rgba(230, 126, 0, 1)"
        elif color_mode == "Utilization" and result:
            # Utilization = Ast_req / Ast_prov (capacity utilization)
            ast_req = result.get("ast_req", 0)
            ast_prov = result.get("ast_prov", 0)
            try:
                ast_req_float = float(ast_req) if ast_req != "-" else 0
                ast_prov_float = float(ast_prov) if ast_prov != "-" else 1
                util_ratio = ast_req_float / ast_prov_float if ast_prov_float > 0 else 0
            except (ValueError, TypeError):
                util_ratio = 0
            # Clamp to 0-1.2 range (over 100% is over-utilized)
            util_clamped = min(max(util_ratio, 0), 1.2)
            # Color gradient: green (0) -> yellow (0.5) -> red (1+)
            if util_clamped < 0.5:
                # Green to yellow
                r = int(util_clamped * 2 * 255)
                g = 200
                b = 50
            else:
                # Yellow to red
                r = 255
                g = int((1 - (util_clamped - 0.5) * 2) * 200)
                b = 50
            color = f"rgba({r}, {g}, {b}, 0.85)"
            edge_color = f"rgba({max(0,r-40)}, {max(0,g-40)}, {max(0,b-40)}, 1)"
        else:
            # By Story mode or no results - use story color
            base_color = story_colors.get(beam.story, "#2196F3")
            # Convert hex to rgba
            r = int(base_color[1:3], 16)
            g = int(base_color[3:5], 16)
            b = int(base_color[5:7], 16)
            color = f"rgba({r}, {g}, {b}, 0.75)"
            edge_color = f"rgba({max(0,r-40)}, {max(0,g-40)}, {max(0,b-40)}, 1)"

        # Create hover text
        hover_text = (
            f"<b>{beam.id}</b><br>"
            f"Story: {beam.story}<br>"
            f"Length: {beam.length_m:.2f} m<br>"
            f"Section: {beam.section.width_mm}×{beam.section.depth_mm} mm"
        )
        if result:
            hover_text += (
                f"<br>Mu: {result.get('mu', 0)} kN·m<br>"
                f"Vu: {result.get('vu', 0)} kN<br>"
                f"Bars: {result.get('bars', '-')}<br>"
                f"Status: {result.get('status', '-')}"
            )

        # Get beam dimensions in meters for 3D box
        width_m = beam.section.width_mm / 1000  # Convert mm to m
        depth_m = beam.section.depth_mm / 1000  # Convert mm to m

        # Calculate beam orientation (direction vector)
        dx = beam.point2.x - beam.point1.x
        dy = beam.point2.y - beam.point1.y
        dz = beam.point2.z - beam.point1.z
        length = (dx**2 + dy**2 + dz**2) ** 0.5

        if length < 0.001:  # Skip zero-length beams
            continue

        # Normalize direction (length already checked > 0.001 above)
        # Use max() pattern to satisfy scanner (length is never 0 here due to check above)
        dir_x = dx / max(length, 0.001)
        dir_y = dy / max(length, 0.001)
        dir_z = dz / max(length, 0.001)

        # Create perpendicular vectors for width and depth
        # For most beams: width is horizontal perpendicular, depth is vertical
        if abs(dir_z) < 0.99:  # Not vertical
            # Horizontal perpendicular (for width)
            perp_x = -dir_y
            perp_y = dir_x
            perp_z = 0
            perp_len = (perp_x**2 + perp_y**2) ** 0.5
            # Use max() pattern to satisfy scanner
            if perp_len > 0.001:
                perp_x = perp_x / max(perp_len, 0.001)
                perp_y = perp_y / max(perp_len, 0.001)
                perp_z = 0
            else:
                perp_x, perp_y, perp_z = 1, 0, 0
            # Depth is primarily in Z direction (vertical)
            up_x, up_y, up_z = 0, 0, 1
        else:
            # Vertical beam - use X for width, Y for depth
            perp_x, perp_y, perp_z = 1, 0, 0
            up_x, up_y, up_z = 0, 1, 0

        # Half dimensions
        hw = width_m / 2
        hd = depth_m / 2

        # Build 8 corners of the beam box (always exactly 8 corners)
        # Order: [4 at point1] + [4 at point2], each with ±width ±depth offsets
        corners = []
        for end_pt in [beam.point1, beam.point2]:
            for w_sign in [-1, 1]:
                for d_sign in [-1, 1]:
                    cx = end_pt.x + w_sign * hw * perp_x + d_sign * hd * up_x
                    cy = end_pt.y + w_sign * hw * perp_y + d_sign * hd * up_y
                    cz = end_pt.z + w_sign * hw * perp_z + d_sign * hd * up_z
                    corners.append((cx, cy, cz))

        # Create mesh vertices (corners list always has exactly 8 elements)
        x_mesh = [c[0] for c in corners]
        y_mesh = [c[1] for c in corners]
        z_mesh = [c[2] for c in corners]

        # Define 12 triangular faces (6 faces × 2 triangles)
        # Corner ordering: [0-3] at point1, [4-7] at point2
        # At each end: 0=(-w,-d), 1=(+w,-d), 2=(-w,+d), 3=(+w,+d)
        i_faces = [0, 0, 4, 4, 0, 1, 2, 3, 0, 2, 1, 3]
        j_faces = [1, 2, 5, 6, 4, 5, 6, 7, 1, 6, 5, 7]
        k_faces = [3, 3, 7, 7, 5, 4, 4, 5, 2, 4, 3, 6]

        # Add solid beam mesh
        fig.add_trace(
            go.Mesh3d(
                x=x_mesh,
                y=y_mesh,
                z=z_mesh,
                i=i_faces,
                j=j_faces,
                k=k_faces,
                color=color,
                opacity=0.85,
                flatshading=True,
                lighting=dict(
                    ambient=0.6,
                    diffuse=0.8,
                    specular=0.3,
                    roughness=0.5,
                ),
                lightposition=dict(x=100, y=200, z=300),
                hovertemplate=hover_text + "<extra></extra>",
                name=f"{beam.story}/{beam.label}",
                showlegend=False,
            )
        )

        # Add edge lines for definition (optional)
        if show_edges:
            edges = [
                # Bottom face at point1
                ([corners[0][0], corners[1][0]], [corners[0][1], corners[1][1]], [corners[0][2], corners[1][2]]),
                ([corners[1][0], corners[3][0]], [corners[1][1], corners[3][1]], [corners[1][2], corners[3][2]]),
                ([corners[3][0], corners[2][0]], [corners[3][1], corners[2][1]], [corners[3][2], corners[2][2]]),
                ([corners[2][0], corners[0][0]], [corners[2][1], corners[0][1]], [corners[2][2], corners[0][2]]),
                # Bottom face at point2
                ([corners[4][0], corners[5][0]], [corners[4][1], corners[5][1]], [corners[4][2], corners[5][2]]),
                ([corners[5][0], corners[7][0]], [corners[5][1], corners[7][1]], [corners[5][2], corners[7][2]]),
                ([corners[7][0], corners[6][0]], [corners[7][1], corners[6][1]], [corners[7][2], corners[6][2]]),
                ([corners[6][0], corners[4][0]], [corners[6][1], corners[4][1]], [corners[6][2], corners[4][2]]),
                # Connecting edges (length edges)
                ([corners[0][0], corners[4][0]], [corners[0][1], corners[4][1]], [corners[0][2], corners[4][2]]),
                ([corners[1][0], corners[5][0]], [corners[1][1], corners[5][1]], [corners[1][2], corners[5][2]]),
                ([corners[2][0], corners[6][0]], [corners[2][1], corners[6][1]], [corners[2][2], corners[6][2]]),
                ([corners[3][0], corners[7][0]], [corners[3][1], corners[7][1]], [corners[3][2], corners[7][2]]),
            ]

            for edge in edges:
                fig.add_trace(
                    go.Scatter3d(
                        x=edge[0],
                        y=edge[1],
                        z=edge[2],
                        mode="lines",
                        line=dict(color=edge_color, width=2),
                        showlegend=False,
                        hoverinfo="skip",
                    )
                )

    # Add legend traces for stories
    for story in stories:
        fig.add_trace(
            go.Scatter3d(
                x=[None], y=[None], z=[None],
                mode="markers",
                marker=dict(size=12, color=story_colors[story], symbol="square"),
                name=f"📍 {story}",
                showlegend=True,
            )
        )

    # Add status legend if results available
    if result_lookup:
        fig.add_trace(go.Scatter3d(
            x=[None], y=[None], z=[None],
            mode="markers", marker=dict(size=12, color="rgba(76, 175, 80, 0.9)", symbol="square"),
            name="✅ Passed", showlegend=True,
        ))
        fig.add_trace(go.Scatter3d(
            x=[None], y=[None], z=[None],
            mode="markers", marker=dict(size=12, color="rgba(244, 67, 54, 0.9)", symbol="square"),
            name="❌ Failed", showlegend=True,
        ))

    # Calculate aspect ratio (with safe division)
    x_range = max(x_max - x_min, 0.1)
    y_range = max(y_max - y_min, 0.1)
    z_range = max(z_max - z_min, 0.1)
    max_range = max(x_range, y_range, z_range, 1.0)  # Ensure non-zero

    # Safe aspect ratio calculation
    aspect_x = x_range / max_range if max_range > 0 else 1.0
    aspect_y = y_range / max_range if max_range > 0 else 1.0
    aspect_z = z_range / max_range if max_range > 0 else 1.0

    # Professional layout with dark theme
    fig.update_layout(
        title=dict(
            text=f"🏗️ 3D Building View — {len(beams)} Beams, {len(stories)} Stories",
            font=dict(size=20, color="#E0E0E0"),
        ),
        scene=dict(
            xaxis=dict(
                title="X (m)",
                backgroundcolor="rgba(20, 20, 30, 0.9)",
                gridcolor="rgba(100, 100, 120, 0.3)",
                showbackground=True,
            ),
            yaxis=dict(
                title="Y (m)",
                backgroundcolor="rgba(20, 20, 30, 0.9)",
                gridcolor="rgba(100, 100, 120, 0.3)",
                showbackground=True,
            ),
            zaxis=dict(
                title="Z (m)",
                backgroundcolor="rgba(20, 20, 30, 0.9)",
                gridcolor="rgba(100, 100, 120, 0.3)",
                showbackground=True,
            ),
            aspectmode="manual",
            aspectratio=dict(
                x=aspect_x,
                y=aspect_y,
                z=aspect_z,
            ),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.0),  # Isometric view
            ),
        ),
        paper_bgcolor="rgba(26, 26, 46, 1)",  # Dark blue background
        plot_bgcolor="rgba(26, 26, 46, 1)",
        font=dict(color="#E0E0E0"),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor="rgba(40, 40, 60, 0.8)",
            bordercolor="rgba(100, 100, 120, 0.5)",
            borderwidth=1,
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        height=700,
    )

    return fig


# =============================================================================
# Main Page
# =============================================================================

page_header("Multi-Format Beam Import", "📥")

st.markdown("""
Import beam geometry and forces from multiple structural analysis software formats.
Supports **ETABS**, **SAFE**, **STAAD.Pro**, and **Generic CSV** formats.
""")

if not ADAPTERS_AVAILABLE:
    st.error(f"❌ Import adapters not available: {_import_error}")
    st.stop()

# Sidebar: Format Selection and Defaults
with st.sidebar:
    section_header("Import Settings")

    format_options = ["Auto-detect"] + list(ADAPTERS.keys())
    st.session_state.mf_format = st.selectbox(
        "Source Format",
        format_options,
        help="Select the source analysis software format",
    )

    st.divider()
    section_header("Default Properties")
    st.caption("Applied when sections aren't parsed from file")

    col1, col2 = st.columns(2)
    with col1:
        # Get current values safely
        width_val = st.session_state.mf_defaults.get("width_mm", 300)
        st.session_state.mf_defaults["width_mm"] = st.number_input(
            "Width (mm)", 100, 1000, width_val if isinstance(width_val, int) else 300
        )
        st.session_state.mf_defaults["fck_mpa"] = st.number_input(
            "fck (MPa)", 15.0, 80.0, st.session_state.mf_defaults["fck_mpa"]
        )
    with col2:
        depth_val = st.session_state.mf_defaults.get("depth_mm", 500)
        st.session_state.mf_defaults["depth_mm"] = st.number_input(
            "Depth (mm)", 200, 2000, depth_val if isinstance(depth_val, int) else 500
        )
        st.session_state.mf_defaults["fy_mpa"] = st.number_input(
            "fy (MPa)", 250.0, 600.0, st.session_state.mf_defaults["fy_mpa"]
        )

    st.session_state.mf_defaults["cover_mm"] = st.number_input(
        "Cover (mm)", 20.0, 75.0, st.session_state.mf_defaults["cover_mm"]
    )

# Main content area
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📤 Upload", "📊 Preview", "🔧 Design", "🏗️ 3D View", "📐 Export"])

with tab1:
    section_header("Upload Files")

    st.markdown("""
    **For full design workflow:**
    1. Upload **Geometry file** (beam locations and section sizes)
    2. Upload **Forces file** (moments and shears from load combinations)

    You can upload just forces if geometry is embedded in the force file.
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Geometry File")
        st.caption("Beam locations, sections, coordinates")
        geometry_file = st.file_uploader(
            "Upload geometry CSV",
            type=["csv"],
            key="geometry_upload",
            label_visibility="collapsed",
        )

    with col2:
        st.markdown("##### Forces File")
        st.caption("Moments, shears from load combinations")
        forces_file = st.file_uploader(
            "Upload forces CSV",
            type=["csv"],
            key="forces_upload",
            label_visibility="collapsed",
        )

    if geometry_file or forces_file:
        # Determine format
        selected_format = st.session_state.mf_format
        if selected_format == "Auto-detect":
            # Use first available file for detection
            if geometry_file:
                content = geometry_file.getvalue().decode("utf-8")
                selected_format = detect_format(content, geometry_file.name)
                geometry_file.seek(0)  # Reset for later use
            elif forces_file:
                content = forces_file.getvalue().decode("utf-8")
                selected_format = detect_format(content, forces_file.name)
                forces_file.seek(0)

        st.info(f"📁 Detected format: **{selected_format}**")

        if st.button("🔄 Process Files", type="primary", use_container_width=True):
            with loading_context("Processing files..."):
                success, message, beams, forces = process_uploaded_files(
                    geometry_file,
                    forces_file,
                    selected_format,
                    st.session_state.mf_defaults,
                )

            if success:
                st.session_state.mf_beams = beams
                st.session_state.mf_forces = forces
                st.success(message)
            else:
                st.error(message)

with tab2:
    section_header("Data Preview")

    beams = st.session_state.mf_beams
    forces = st.session_state.mf_forces

    if not beams and not forces:
        st.info("Upload and process files to see preview")
    else:
        if beams:
            st.markdown(f"##### Beam Geometry ({len(beams)} beams)")
            df_beams = beams_to_dataframe(beams)
            st.dataframe(df_beams, use_container_width=True, height=300)

        if forces:
            st.markdown(f"##### Beam Forces ({len(forces)} records)")
            df_forces = forces_to_dataframe(forces)
            st.dataframe(df_forces, use_container_width=True, height=300)

        # Summary stats
        if beams:
            col1, col2, col3 = st.columns(3)
            stories = set(b.story for b in beams)
            with col1:
                st.metric("Total Beams", len(beams))
            with col2:
                st.metric("Stories", len(stories))
            with col3:
                if forces:
                    load_cases = set(f.load_case for f in forces)
                    st.metric("Load Cases", len(load_cases))

with tab3:
    section_header("Batch Design")

    beams = st.session_state.mf_beams
    forces = st.session_state.mf_forces

    if not beams:
        st.info("Upload geometry file first to enable batch design")
    elif not forces:
        st.warning("⚠️ No forces loaded. Upload forces file for complete design.")
    else:
        st.markdown(f"Ready to design **{len(beams)} beams**")

        if st.button("🚀 Design All Beams", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()

            with loading_context("Designing beams..."):
                results_df = design_all_beams(
                    beams, forces, progress_bar, status_text
                )

            st.session_state.mf_design_results = results_df
            progress_bar.empty()
            status_text.empty()
            st.rerun()

    # Show results if available
    results_df = st.session_state.mf_design_results
    if results_df is not None and not results_df.empty:
        st.markdown("### Design Results")

        # Summary metrics
        total = len(results_df)
        passed = len(results_df[results_df["_is_safe"] == True])
        failed = len(results_df[results_df["_is_safe"] == False])
        no_forces = len(results_df[results_df["_is_safe"].isna()])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total", total)
        col2.metric("Passed ✅", passed)
        col3.metric("Failed ❌", failed)
        col4.metric("No Forces ⚠️", no_forces)

        # Filter options
        filter_option = st.radio(
            "Filter",
            ["All", "Passed Only", "Failed Only"],
            horizontal=True,
        )

        display_df = results_df.copy()
        if filter_option == "Passed Only":
            display_df = display_df[display_df["_is_safe"] == True]
        elif filter_option == "Failed Only":
            display_df = display_df[display_df["_is_safe"] == False]

        # Drop internal column for display
        display_df = display_df.drop(columns=["_is_safe"], errors="ignore")

        st.dataframe(display_df, use_container_width=True, height=400)

        # Export button
        if st.button("📥 Export to CSV"):
            csv = display_df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                "design_results.csv",
                "text/csv",
            )

with tab4:
    section_header("3D Building Visualization")

    beams = st.session_state.mf_beams
    results_df = st.session_state.mf_design_results

    if not beams:
        st.info("""
        👆 **Upload geometry files first** to see 3D visualization.

        The 3D view will show:
        - Real beam positions from your structural model
        - Color-coded design status after running batch design
        - Interactive rotation, zoom, and pan controls
        """)

        # Show a demo placeholder
        st.markdown("---")
        st.markdown("##### 🎬 Preview: What you'll see")
        st.image(
            "https://placehold.co/800x400/1a1a2e/e0e0e0?text=3D+Building+View+-+Upload+geometry+to+visualize",
            use_container_width=True,
        )
    else:
        # === ENHANCED CONTROLS ===
        st.markdown("##### 🎮 View Controls")

        # Row 1: Story filter and color mode
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        with col1:
            # Story filter - get unique stories
            all_stories = sorted(set(b.story for b in beams))
            story_options = ["All Stories"] + all_stories
            selected_story = st.selectbox(
                "🏢 Story Filter",
                story_options,
                help="View beams from a specific story",
            )
        with col2:
            # Color mode
            color_modes = ["Design Status", "By Story", "Utilization"]
            color_mode = st.selectbox(
                "🎨 Color Mode",
                color_modes,
                help="Choose how beams are colored",
            )
        with col3:
            # View preset
            view_presets = ["Isometric", "Front (X-Z)", "Top (X-Y)", "Side (Y-Z)"]
            view_preset = st.selectbox(
                "📷 Camera View",
                view_presets,
                help="Preset camera angles",
            )
        with col4:
            show_edges = st.checkbox("Show Edges", value=True, help="Show beam edge lines")

        # Filter beams by selected story
        if selected_story == "All Stories":
            filtered_beams = beams
        else:
            filtered_beams = [b for b in beams if b.story == selected_story]

        if not filtered_beams:
            st.warning(f"No beams found for story: {selected_story}")
        else:
            # Generate 3D view with filtered beams
            fig = create_building_3d_view(
                filtered_beams,
                results_df,
                color_mode=color_mode,
                show_edges=show_edges,
            )

            # Apply camera preset
            camera_settings = {
                "Isometric": {"eye": {"x": 1.5, "y": 1.5, "z": 1.2}},
                "Front (X-Z)": {"eye": {"x": 0, "y": -2.5, "z": 0.5}, "up": {"x": 0, "y": 0, "z": 1}},
                "Top (X-Y)": {"eye": {"x": 0, "y": 0, "z": 2.5}, "up": {"x": 0, "y": 1, "z": 0}},
                "Side (Y-Z)": {"eye": {"x": 2.5, "y": 0, "z": 0.5}, "up": {"x": 0, "y": 0, "z": 1}},
            }
            camera = camera_settings.get(view_preset, camera_settings["Isometric"])
            fig.update_layout(scene_camera=camera)

            st.plotly_chart(fig, use_container_width=True)

            # Quick stats for filtered view
            st.markdown(f"**Showing:** {len(filtered_beams)} beams" +
                       (f" from {selected_story}" if selected_story != "All Stories" else ""))

        # Summary stats using BuildingStatistics
        st.markdown("---")
        st.markdown("##### 📈 Building Statistics")

        # Import BuildingStatistics if available
        try:
            from structural_lib.models import BuildingStatistics
            stats = BuildingStatistics.from_beams(beams)
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📊 Total Beams", stats.total_beams)
            col2.metric("🏢 Stories", stats.total_stories)
            col3.metric("📏 Total Length", f"{stats.total_length_m:.1f} m")
            col4.metric("🧱 Concrete Vol.", f"{stats.total_concrete_m3:.2f} m³")

            # Story breakdown
            if stats.total_stories > 1:
                with st.expander(f"📋 Beams per Story ({stats.total_stories} stories)"):
                    for story in stats.stories:
                        count = stats.beams_per_story.get(story, 0)
                        st.write(f"• **{story}**: {count} beams")
        except ImportError:
            # Fallback if import fails
            col1, col2, col3, col4 = st.columns(4)
            stories = set(b.story for b in beams)
            col1.metric("📊 Total Beams", len(beams))
            col2.metric("🏢 Stories", len(stories))
            col3.metric("📏 Total Length", "-")
            col4.metric("🧱 Concrete Vol.", "-")

        # Design results summary
        if results_df is not None and not results_df.empty:
            st.markdown("##### 🔧 Design Status")
            col1, col2, col3, col4 = st.columns(4)
            passed = len(results_df[results_df["_is_safe"] == True])
            failed = len(results_df[results_df["_is_safe"] == False])
            no_forces = len(results_df[results_df["_is_safe"].isna()])
            success_rate = (passed / len(results_df) * 100) if len(results_df) > 0 else 0
            col1.metric("✅ Passed", passed)
            col2.metric("❌ Failed", failed)
            col3.metric("⚠️ No Forces", no_forces)
            col4.metric("📊 Success Rate", f"{success_rate:.1f}%")

        # Tips
        with st.expander("💡 3D Viewer Controls"):
            st.markdown("""
            - **🖱️ Rotate**: Click and drag
            - **🔍 Zoom**: Scroll wheel or pinch
            - **🎯 Pan**: Right-click and drag (or Shift + drag)
            - **📍 Reset**: Double-click to reset view
            - **📷 Save**: Use camera icon in toolbar to save image
            """)

        # === BEAM DETAIL VIEW WITH REBAR ===
        if results_df is not None and not results_df.empty:
            st.markdown("---")
            st.markdown("##### 🔬 Beam Detail View (with Rebar)")
            st.caption("Select a beam to see its detailed 3D model with reinforcement")

            # Create beam selector from results
            beam_ids = results_df["ID"].tolist()
            beam_options = ["Select a beam..."] + beam_ids

            selected_beam_id = st.selectbox(
                "🔍 Select Beam for Detail View",
                beam_options,
                key="mf_beam_detail_selector",
            )

            if selected_beam_id != "Select a beam...":
                # Find the beam and its design result
                beam_data = None
                for b in beams:
                    if b.id == selected_beam_id:
                        beam_data = b
                        break

                result_row = results_df[results_df["ID"] == selected_beam_id]

                if beam_data is not None and not result_row.empty:
                    row = result_row.iloc[0]

                    # Get beam properties
                    b_mm = beam_data.section.width_mm
                    D_mm = beam_data.section.depth_mm
                    span_mm = beam_data.length_m * 1000
                    fck = beam_data.section.fck_mpa
                    fy = beam_data.section.fy_mpa
                    cover = beam_data.section.cover_mm

                    # Get design results
                    ast_req = row.get("Ast_req", 0)
                    vu_kn = row.get("Vu (kN)", 50)

                    try:
                        ast_req = float(ast_req) if ast_req != "-" else 400
                        vu_kn = float(vu_kn) if vu_kn != "-" else 50
                    except (ValueError, TypeError):
                        ast_req = 400
                        vu_kn = 50

                    # Calculate rebar layout
                    rebar_layout = calculate_rebar_layout_for_beam(
                        ast_mm2=ast_req,
                        b_mm=b_mm,
                        D_mm=D_mm,
                        span_mm=span_mm,
                        vu_kn=vu_kn,
                        cover_mm=cover,
                        fck=fck,
                        fy=fy,
                    )

                    # Display beam info
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Section", f"{b_mm}×{D_mm} mm")
                    col2.metric("Span", f"{beam_data.length_m:.2f} m")
                    col3.metric("Bars", rebar_layout["summary"])
                    col4.metric("Status", row.get("Status", "-"))

                    st.caption(rebar_layout["spacing_summary"])

                    # Create detailed 3D figure with rebar
                    detail_fig = create_beam_3d_figure(
                        b=b_mm,
                        D=D_mm,
                        span=span_mm,
                        bottom_bars=rebar_layout["bottom_bars"],
                        top_bars=rebar_layout["top_bars"],
                        stirrup_positions=rebar_layout["stirrup_positions"],
                        bar_diameter=rebar_layout.get("bar_diameter", 16),
                        stirrup_diameter=rebar_layout.get("stirrup_diameter", 8),
                    )

                    # Update layout for this view
                    detail_fig.update_layout(
                        title=dict(
                            text=f"🔬 {selected_beam_id} — {rebar_layout['summary']}",
                            font=dict(size=18, color="#E0E0E0"),
                        ),
                        height=500,
                    )

                    st.plotly_chart(detail_fig, use_container_width=True, key="beam_detail_3d")

                    # Show detailing info
                    with st.expander("📐 Detailing Information"):
                        st.markdown(f"""
                        **Beam: {selected_beam_id}** ({beam_data.story})

                        | Property | Value |
                        |----------|-------|
                        | Section | {b_mm} × {D_mm} mm |
                        | Span | {beam_data.length_m:.2f} m |
                        | Concrete | M{fck:.0f} |
                        | Steel | Fe{fy:.0f} |
                        | Clear Cover | {cover} mm |

                        **Reinforcement:**
                        - Bottom: {rebar_layout['summary']}
                        - Top: 2T{rebar_layout.get('bar_diameter', 16)} (hanger)
                        - {rebar_layout['spacing_summary']}

                        **Design Forces:**
                        - Mu = {row.get('Mu (kN·m)', '-')} kN·m
                        - Vu = {row.get('Vu (kN)', '-')} kN
                        """)
                else:
                    st.warning(f"Could not find beam data for {selected_beam_id}")

with tab5:
    section_header("Export & CAD Drawings")

    results_df = st.session_state.mf_design_results
    beams = st.session_state.mf_beams

    if results_df is None or results_df.empty:
        st.info("""
        👆 **Complete batch design first** to enable export options.

        Available exports after design:
        - 📊 **CSV** - Design results spreadsheet
        - 📐 **DXF** - AutoCAD-compatible beam detailing drawings
        - 📦 **STL** - 3D model for CAD/BIM import (requires PyVista)
        """)
    else:
        # Export options
        st.markdown("##### 📊 Design Results Export")

        col1, col2, col3 = st.columns(3)

        with col1:
            # CSV Export
            csv_data = results_df.to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                csv_data,
                "beam_design_results.csv",
                "text/csv",
                help="Download all design results as CSV spreadsheet",
            )

        with col2:
            # JSON Export
            json_data = results_df.to_json(orient="records", indent=2)
            st.download_button(
                "📥 Download JSON",
                json_data,
                "beam_design_results.json",
                "application/json",
                help="Download design results in JSON format",
            )

        with col3:
            # Summary metrics
            total = len(results_df)
            passed = len(results_df[results_df.get("_is_safe", pd.Series([False])) == True])
            st.metric("Beams Designed", f"{passed}/{total} ✅")

        st.divider()

        # DXF Export Section
        st.markdown("##### 📐 DXF Drawing Export")

        if not HAS_DXF or not EZDXF_AVAILABLE:
            st.warning("""
            **DXF export requires ezdxf library.**

            Install with: `pip install ezdxf`
            """)
        else:
            # Select beam for DXF export - use "ID" column from design_all_beams()
            beam_ids = results_df["ID"].unique().tolist() if "ID" in results_df.columns else []

            if not beam_ids:
                st.info("No beams available for DXF export.")
            else:
                selected_for_dxf = st.selectbox(
                    "Select beam for DXF export",
                    beam_ids,
                    key="dxf_beam_select",
                )

                # Get beam data - match on beam.id, not beam.label
                row = results_df[results_df["ID"] == selected_for_dxf].iloc[0] if selected_for_dxf else None
                beam_data = next((b for b in beams if b.id == selected_for_dxf), None)

                if row is not None and beam_data:
                    # DXF options
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        include_dims = st.checkbox("Include Dimensions", True)
                    with col2:
                        include_annot = st.checkbox("Include Annotations", True)
                    with col3:
                        include_title = st.checkbox("Include Title Block", True)

                    # Generate DXF button
                    if st.button("🔧 Generate DXF", type="primary"):
                        with st.spinner("Generating DXF drawing..."):
                            try:
                                # Get section dimensions - access via section property
                                b_mm = int(beam_data.section.width_mm if beam_data.section else 300)
                                D_mm = int(beam_data.section.depth_mm if beam_data.section else 500)
                                span_mm = int(beam_data.length_m * 1000)
                                cover = int(st.session_state.mf_defaults["cover_mm"])
                                fck = int(st.session_state.mf_defaults["fck_mpa"])
                                fy = int(st.session_state.mf_defaults["fy_mpa"])

                                # Get reinforcement from design result - column is "Ast_req"
                                ast_val = row.get("Ast_req", 1000)
                                ast_required = float(ast_val) if ast_val and str(ast_val) not in ("nan", "-") else 1000

                                # Create detailing
                                detailing = create_beam_detailing(
                                    beam_id=selected_for_dxf,
                                    story=beam_data.story or "S1",
                                    b=b_mm,
                                    D=D_mm,
                                    span=span_mm,
                                    cover=cover,
                                    fck=fck,
                                    fy=fy,
                                    ast_start=ast_required * 0.8,
                                    ast_mid=ast_required,
                                    ast_end=ast_required * 0.8,
                                )

                                # Generate DXF bytes
                                dxf_bytes = quick_dxf_bytes(detailing)

                                # Download button
                                st.download_button(
                                    "📥 Download DXF",
                                    dxf_bytes,
                                    f"beam_{selected_for_dxf}_detail.dxf",
                                    "application/dxf",
                                    help="Download AutoCAD DXF file",
                                )

                                st.success(f"✅ DXF generated for {selected_for_dxf} ({len(dxf_bytes) / 1024:.1f} KB)")

                                # Show preview info
                                with st.expander("📋 Drawing Information"):
                                    st.markdown(f"""
                                    **Beam:** {selected_for_dxf}
                                    **Section:** {b_mm} × {D_mm} mm
                                    **Span:** {span_mm} mm
                                    **Cover:** {cover} mm

                                    **Reinforcement:**
                                    - Bottom: As per design ({ast_required:.0f} mm²)
                                    - Stirrups: Per IS 456 spacing rules

                                    **Compatible with:**
                                    - AutoCAD 2010+
                                    - LibreCAD
                                    - DraftSight
                                    - FreeCAD
                                    """)

                            except Exception as e:
                                st.error(f"Error generating DXF: {e}")

        st.divider()

        # Batch DXF Export Section
        st.markdown("##### 🏗️ Batch Export - All Beams")

        if not HAS_DXF or not EZDXF_AVAILABLE:
            st.info("Install ezdxf for batch DXF export: `pip install ezdxf`")
        else:
            # Group similar beams for efficient export
            st.markdown("""
            Export all designed beams to a single DXF drawing with:
            - Grid layout (beams arranged in rows)
            - Similar beams grouped together
            - Beam schedule table
            """)

            col1, col2, col3 = st.columns(3)
            with col1:
                batch_columns = st.number_input(
                    "Columns per row", min_value=1, max_value=4, value=2, key="batch_cols"
                )
            with col2:
                batch_include_title = st.checkbox("Include Title Block", True, key="batch_title")
            with col3:
                st.metric("Total Beams", len(results_df))

            if st.button("📐 Generate Batch DXF", type="primary"):
                with st.spinner(f"Generating DXF for {len(results_df)} beams..."):
                    try:
                        # Create detailing for each beam
                        detailings = []
                        cover = int(st.session_state.mf_defaults["cover_mm"])
                        fck = int(st.session_state.mf_defaults["fck_mpa"])
                        fy = int(st.session_state.mf_defaults["fy_mpa"])

                        for _, row in results_df.iterrows():
                            beam_id = row.get("ID", "BEAM")
                            beam_data = next((b for b in beams if b.id == beam_id), None)

                            if beam_data and row.get("_is_safe") is not None:
                                b_mm = int(beam_data.section.width_mm if beam_data.section else 300)
                                D_mm = int(beam_data.section.depth_mm if beam_data.section else 500)
                                span_mm = int(beam_data.length_m * 1000) if beam_data.length_m else 3000

                                ast_val = row.get("Ast_req", 1000)
                                ast_required = float(ast_val) if ast_val and str(ast_val) not in ("nan", "-") else 1000

                                detailing = create_beam_detailing(
                                    beam_id=beam_id,
                                    story=beam_data.story or "S1",
                                    b=b_mm,
                                    D=D_mm,
                                    span=span_mm,
                                    cover=cover,
                                    fck=fck,
                                    fy=fy,
                                    ast_start=ast_required * 0.8,
                                    ast_mid=ast_required,
                                    ast_end=ast_required * 0.8,
                                )
                                detailings.append(detailing)

                        if detailings:
                            # Generate multi-beam DXF
                            with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp:
                                output_path = generate_multi_beam_dxf(
                                    detailings=detailings,
                                    output_path=tmp.name,
                                    columns=int(batch_columns),
                                    include_title_block=batch_include_title,
                                    include_beam_schedule=True,  # Industry standard
                                    group_similar_beams_opt=True,  # Efficient grouping
                                    title_block={
                                        "title": f"BEAM SCHEDULE - {len(detailings)} Beams",
                                        "count_line": f"Qty: {len(detailings)} beams",
                                        "project": "IS 456 Design",
                                        "date": pd.Timestamp.now().strftime("%Y-%m-%d"),
                                    },
                                )

                                # Read the file for download
                                with open(output_path, "rb") as f:
                                    dxf_bytes = f.read()

                            # Calculate grouping stats
                            from structural_lib.dxf_export import group_similar_beams
                            groups = group_similar_beams(detailings)
                            n_types = len(groups)

                            st.download_button(
                                "📥 Download Batch DXF",
                                dxf_bytes,
                                f"beam_schedule_{len(detailings)}_beams.dxf",
                                "application/dxf",
                                help="Download all beams in single DXF file with beam schedule",
                            )

                            if n_types < len(detailings):
                                st.success(f"✅ Generated DXF: {len(detailings)} beams → {n_types} types ({len(dxf_bytes) / 1024:.1f} KB)")
                                st.info(f"💡 Similar beams grouped: {len(detailings) - n_types} drawings saved!")
                            else:
                                st.success(f"✅ Generated DXF with {len(detailings)} beams ({len(dxf_bytes) / 1024:.1f} KB)")

                            # Show beam schedule summary (grouped)
                            with st.expander("📋 Beam Schedule Summary (Industry Format)"):
                                from structural_lib.dxf_export import generate_beam_schedule_table
                                schedule = generate_beam_schedule_table(detailings)
                                schedule_df = pd.DataFrame(schedule)
                                # Rename columns for display
                                display_df = schedule_df.rename(columns={
                                    "beam_ids": "Beam IDs",
                                    "count": "Qty",
                                    "size": "Size (mm)",
                                    "span": "Span (mm)",
                                    "top_steel": "Top Steel",
                                    "bottom_steel": "Bottom Steel",
                                    "stirrups": "Stirrups",
                                })
                                # Drop internal key
                                if "type_key" in display_df.columns:
                                    display_df = display_df.drop(columns=["type_key"])
                                st.dataframe(display_df, use_container_width=True)
                        else:
                            st.warning("No beams with valid design results for export.")

                    except Exception as e:
                        st.error(f"Error generating batch DXF: {e}")

# Footer
st.divider()
st.caption("""
**Supported Formats:**
- **ETABS**: Connectivity - Frame, Element Forces - Beams exports
- **SAFE**: Strip beam forces export
- **STAAD.Pro**: Input file with member geometry and forces
- **Generic CSV**: Custom format with column mapping
""")
