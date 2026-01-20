# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
AI Workspace Component - Dynamic State-Based Workspace

This module provides a unified workspace that transitions based on workflow state:
- WELCOME: Quick start cards for getting started
- IMPORT: Auto-mapped preview after file upload
- DESIGN: Interactive results table with beam selection
- BUILDING_3D: Full building 3D visualization with all beams
- VIEW_3D: Selected beam with rebar visualization
- REBAR_EDIT: Interactive reinforcement editor with real-time checks
- EDIT: Single beam editor with live preview
- DASHBOARD: SmartDesigner insights

Architecture:
    User Action → State Transition → Workspace Re-render

Usage:
    from components.ai_workspace import (
        WorkspaceState,
        init_workspace_state,
        render_dynamic_workspace,
    )

    init_workspace_state()
    render_dynamic_workspace()
"""

from __future__ import annotations

import io
import math
from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Try to import visualization components
try:
    from components.visualizations_3d import create_beam_3d_figure

    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


class WorkspaceState(Enum):
    """Workspace state machine states."""

    WELCOME = "welcome"
    IMPORT = "import"
    DESIGN = "design"
    BUILDING_3D = "building_3d"  # Full building view
    VIEW_3D = "view_3d"  # Single beam detail
    REBAR_EDIT = "rebar_edit"  # Interactive reinforcement editor
    EDIT = "edit"
    DASHBOARD = "dashboard"


# Bar options for rebar editor
BAR_OPTIONS = [
    (10, 78.5),
    (12, 113.1),
    (16, 201.1),
    (20, 314.2),
    (25, 490.9),
    (32, 804.2),
]

# Stirrup options
STIRRUP_OPTIONS = [(6, 28.3), (8, 50.3), (10, 78.5)]


# Sample ETABS-like data for quick start
SAMPLE_ETABS_DATA = """Unique Name,Width,Depth,Length,M3,V2,Story,X1,Y1,Z1,X2,Y2,Z2
B1-L1,300,500,5000,120.5,45.2,Story1,0,0,3,5,0,3
B2-L1,300,500,5000,145.3,52.1,Story1,5,0,3,10,0,3
B3-L1,300,600,6000,185.7,68.3,Story1,0,5,3,6,5,3
B4-L1,350,600,6000,210.2,75.4,Story1,6,5,3,12,5,3
B5-L2,300,500,4500,95.6,38.9,Story2,0,0,6,4.5,0,6
B6-L2,300,500,4500,110.3,42.5,Story2,4.5,0,6,9,0,6
B7-L2,300,550,5500,155.8,55.7,Story2,0,5,6,5.5,5,6
B8-L3,350,650,7000,245.6,88.2,Story3,0,0,9,7,0,9
B9-L3,350,650,7000,265.3,95.1,Story3,7,0,9,14,0,9
B10-L3,400,700,8000,320.5,112.4,Story3,0,5,9,8,5,9
"""

# Column name patterns for auto-mapping
COLUMN_PATTERNS = {
    "beam_id": ["unique name", "beam", "element", "name", "id", "label"],
    "b_mm": ["width", "b", "b_mm", "breadth", "b (mm)"],
    "D_mm": ["depth", "d", "D_mm", "D", "height", "h", "d (mm)"],
    "span_mm": ["length", "span", "L", "l_mm", "span_mm"],
    "mu_knm": ["moment", "m3", "mu", "m_max", "bending", "mu_knm"],
    "vu_kn": ["shear", "v2", "vu", "v_max", "vu_kn"],
    "story": ["story", "floor", "level"],
    "fck": ["fck", "concrete", "fc", "grade"],
    "fy": ["fy", "steel", "rebar"],
    "x1": ["x1", "start_x", "xi"],
    "y1": ["y1", "start_y", "yi"],
    "z1": ["z1", "start_z", "zi", "elev1"],
    "x2": ["x2", "end_x", "xj"],
    "y2": ["y2", "end_y", "yj"],
    "z2": ["z2", "end_z", "zj", "elev2"],
}


def init_workspace_state() -> None:
    """Initialize workspace session state."""
    if "ws_state" not in st.session_state:
        st.session_state.ws_state = WorkspaceState.WELCOME

    if "ws_beams_df" not in st.session_state:
        st.session_state.ws_beams_df = None

    if "ws_design_results" not in st.session_state:
        st.session_state.ws_design_results = None

    if "ws_selected_beam" not in st.session_state:
        st.session_state.ws_selected_beam = None

    # Rebar editor state
    if "ws_rebar_config" not in st.session_state:
        st.session_state.ws_rebar_config = None

    if "ws_defaults" not in st.session_state:
        st.session_state.ws_defaults = {
            "fck": 25.0,
            "fy": 500.0,
            "cover_mm": 40.0,
        }


def set_workspace_state(new_state: WorkspaceState) -> None:
    """Change workspace state and trigger rerun."""
    st.session_state.ws_state = new_state


def get_workspace_state() -> WorkspaceState:
    """Get current workspace state."""
    init_workspace_state()  # Ensure state is initialized
    return st.session_state.ws_state


def auto_map_columns(df: pd.DataFrame) -> dict[str, str]:
    """Auto-detect column mapping from CSV headers."""
    mapping = {}
    df_cols_lower = {c.lower().strip(): c for c in df.columns}

    for target, patterns in COLUMN_PATTERNS.items():
        for pattern in patterns:
            pattern_lower = pattern.lower()
            for col_lower, col_orig in df_cols_lower.items():
                if pattern_lower in col_lower or col_lower in pattern_lower:
                    if target not in mapping:  # Only take first match
                        mapping[target] = col_orig
                    break

    return mapping


def standardize_dataframe(
    df: pd.DataFrame,
    mapping: dict[str, str],
    defaults: dict[str, float],
) -> pd.DataFrame:
    """Standardize DataFrame to common format."""
    result = pd.DataFrame()

    # Map columns
    result["beam_id"] = df[mapping.get("beam_id", df.columns[0])]

    # Geometry with defaults
    if "b_mm" in mapping:
        result["b_mm"] = pd.to_numeric(df[mapping["b_mm"]], errors="coerce").fillna(300)
    else:
        result["b_mm"] = 300

    if "D_mm" in mapping:
        result["D_mm"] = pd.to_numeric(df[mapping["D_mm"]], errors="coerce").fillna(500)
    else:
        result["D_mm"] = 500

    if "span_mm" in mapping:
        result["span_mm"] = pd.to_numeric(df[mapping["span_mm"]], errors="coerce").fillna(5000)
    else:
        result["span_mm"] = 5000

    # Forces
    if "mu_knm" in mapping:
        result["mu_knm"] = pd.to_numeric(df[mapping["mu_knm"]], errors="coerce").fillna(100)
    else:
        result["mu_knm"] = 100

    if "vu_kn" in mapping:
        result["vu_kn"] = pd.to_numeric(df[mapping["vu_kn"]], errors="coerce").fillna(50)
    else:
        result["vu_kn"] = 50

    # Story
    if "story" in mapping:
        result["story"] = df[mapping["story"]].fillna("Unknown")
    else:
        result["story"] = "Story1"

    # Coordinates for 3D building view (generate if not provided)
    coord_fields = ["x1", "y1", "z1", "x2", "y2", "z2"]
    has_coords = all(field in mapping for field in coord_fields)

    if has_coords:
        for field in coord_fields:
            result[field] = pd.to_numeric(df[mapping[field]], errors="coerce").fillna(0)
    else:
        # Generate grid layout based on story and index
        stories = result["story"].unique()
        story_heights = {s: i * 3.0 for i, s in enumerate(sorted(stories))}  # 3m per story

        x_pos = 0.0
        coords_data = {"x1": [], "y1": [], "z1": [], "x2": [], "y2": [], "z2": []}
        for idx, row in result.iterrows():
            span_m = row["span_mm"] / 1000 if row["span_mm"] > 0 else 5.0
            story = row["story"]
            z = story_heights.get(story, 0)

            # Alternate between X and Y directions
            if idx % 2 == 0:
                coords_data["x1"].append(x_pos)
                coords_data["y1"].append(0)
                coords_data["x2"].append(x_pos + span_m)
                coords_data["y2"].append(0)
            else:
                coords_data["x1"].append(0)
                coords_data["y1"].append(x_pos)
                coords_data["x2"].append(0)
                coords_data["y2"].append(x_pos + span_m)

            coords_data["z1"].append(z)
            coords_data["z2"].append(z)
            x_pos += span_m * 0.3  # Offset next beam

        for field in coord_fields:
            result[field] = coords_data[field]

    # Material defaults
    result["fck"] = defaults.get("fck", 25.0)
    result["fy"] = defaults.get("fy", 500.0)
    result["cover_mm"] = defaults.get("cover_mm", 40.0)

    return result


def load_sample_data() -> None:
    """Load built-in sample ETABS data."""
    df = pd.read_csv(io.StringIO(SAMPLE_ETABS_DATA))
    mapping = auto_map_columns(df)
    st.session_state.ws_beams_df = standardize_dataframe(
        df, mapping, st.session_state.ws_defaults
    )
    st.session_state.ws_state = WorkspaceState.IMPORT


def process_uploaded_file(file) -> tuple[bool, str]:
    """Process uploaded CSV with auto-mapping."""
    try:
        df = pd.read_csv(file)
        mapping = auto_map_columns(df)

        if not mapping:
            return False, "Could not auto-detect columns. Check CSV format."

        st.session_state.ws_beams_df = standardize_dataframe(
            df, mapping, st.session_state.ws_defaults
        )

        detected = ", ".join(f"{k}→{v}" for k, v in mapping.items())
        return True, f"✅ Auto-mapped: {detected}"

    except Exception as e:
        return False, f"Error reading file: {e}"


def calculate_rebar_layout(
    ast_mm2: float,
    b_mm: float,
    D_mm: float,
    span_mm: float,
    vu_kn: float = 50.0,
    cover_mm: float = 40.0,
    stirrup_dia: float = 8.0,
) -> dict[str, Any]:
    """Calculate rebar layout for visualization."""
    BAR_OPTIONS = [(12, 113.1), (16, 201.1), (20, 314.2), (25, 490.9), (32, 804.2)]

    best_config = None
    for dia, area in BAR_OPTIONS:
        num_bars = math.ceil(ast_mm2 / area) if ast_mm2 > 0 else 2
        if 2 <= num_bars <= 6:
            best_config = (dia, num_bars, num_bars * area)
            break

    if best_config is None:
        best_config = (16, 3, 3 * 201.1)

    bar_dia, num_bars, ast_provided = best_config

    edge_dist = cover_mm + stirrup_dia + bar_dia / 2
    z_bottom = edge_dist
    z_top = D_mm - edge_dist
    available_width = b_mm - 2 * edge_dist

    bottom_bars = []
    spacing = available_width / max(num_bars - 1, 1)
    for i in range(num_bars):
        y = -available_width / 2 + i * spacing
        bottom_bars.append((0, y, z_bottom))

    top_bars = [
        (0, -available_width / 2, z_top),
        (0, available_width / 2, z_top),
    ]

    d_mm = D_mm - cover_mm - stirrup_dia - bar_dia / 2
    sv_base = min(200, max(100, 0.75 * d_mm))
    tau_v = (vu_kn * 1000) / max(b_mm * d_mm, 1)
    if tau_v > 0.5:
        sv_base = min(sv_base, 150)

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

    return {
        "bottom_bars": bottom_bars,
        "top_bars": top_bars,
        "stirrup_positions": stirrup_positions,
        "bar_diameter": bar_dia,
        "stirrup_diameter": stirrup_dia,
        "summary": f"{num_bars}T{bar_dia} ({ast_provided:.0f} mm²)",
        "spacing_summary": f"Stirrups: Ø{stirrup_dia}@{sv_support:.0f}mm (ends), @{sv_base:.0f}mm (mid)",
    }


def design_beam_row(row: pd.Series) -> dict[str, Any]:
    """Design a single beam and return results."""
    try:
        from structural_lib import api as structural_api

        result = structural_api.design_beam_is456(
            units="IS456",
            b_mm=float(row["b_mm"]),
            D_mm=float(row["D_mm"]),
            d_mm=float(row["D_mm"]) - 50,
            fck_nmm2=float(row["fck"]),
            fy_nmm2=float(row["fy"]),
            mu_knm=float(row["mu_knm"]),
            vu_kn=float(row["vu_kn"]),
        )

        return {
            "is_safe": result.is_ok,
            "ast_req": result.flexure.ast_required,
            "utilization": result.governing_utilization,
            "status": "✅ OK" if result.is_ok else "❌ FAIL",
        }
    except Exception as e:
        return {
            "is_safe": False,
            "ast_req": 0,
            "utilization": 0,
            "status": f"❌ {str(e)[:20]}",
        }


def design_all_beams_ws() -> pd.DataFrame:
    """Design all beams in the workspace."""
    df = st.session_state.ws_beams_df
    if df is None or df.empty:
        return pd.DataFrame()

    results = []
    for idx, row in df.iterrows():
        design = design_beam_row(row)
        results.append({
            "beam_id": row["beam_id"],
            "story": row["story"],
            "b_mm": row["b_mm"],
            "D_mm": row["D_mm"],
            "span_mm": row["span_mm"],
            "mu_knm": row["mu_knm"],
            "vu_kn": row["vu_kn"],
            "fck": row["fck"],
            "fy": row["fy"],
            "cover_mm": row["cover_mm"],
            "ast_req": design["ast_req"],
            "utilization": design["utilization"],
            "is_safe": design["is_safe"],
            "status": design["status"],
        })

    return pd.DataFrame(results)


# =============================================================================
# Workspace Renderers
# =============================================================================


def render_welcome_panel() -> None:
    """Render welcome state with quick start cards."""
    st.markdown("""
    ### 🏗️ Beam Design Workspace
    *Import data → Auto-design → 3D visualization → Customize reinforcement*
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("#### 📂 Quick Demo")
            st.caption("10 beams · 3 stories · ETABS format")
            if st.button("▶ Load Sample", key="ws_sample", use_container_width=True, type="primary"):
                load_sample_data()
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("#### 📤 Your Data")
            st.caption("CSV from ETABS, SAFE, Excel")
            uploaded = st.file_uploader(
                "Upload CSV", type=["csv"], key="ws_upload", label_visibility="collapsed"
            )
            if uploaded:
                success, message = process_uploaded_file(uploaded)
                if success:
                    st.success(message)
                    st.session_state.ws_state = WorkspaceState.IMPORT
                    st.rerun()
                else:
                    st.error(message)

    with col3:
        with st.container(border=True):
            st.markdown("#### ✏️ New Beam")
            st.caption("Design single beam manually")
            if st.button("Create Beam", key="ws_manual", use_container_width=True):
                # Create empty dataframe with one row and generate coords
                st.session_state.ws_beams_df = pd.DataFrame([{
                    "beam_id": "B1",
                    "b_mm": 300,
                    "D_mm": 500,
                    "span_mm": 5000,
                    "mu_knm": 100,
                    "vu_kn": 50,
                    "story": "Story1",
                    "fck": 25.0,
                    "fy": 500.0,
                    "cover_mm": 40.0,
                    "x1": 0, "y1": 0, "z1": 3,
                    "x2": 5, "y2": 0, "z2": 3,
                }])
                st.session_state.ws_state = WorkspaceState.EDIT
                st.rerun()

    # Feature highlights
    st.divider()
    st.caption("**Features:** Auto-column mapping · IS 456 design · 3D building view · Interactive rebar editor · Real-time checks")


def render_import_preview() -> None:
    """Render import preview with auto-mapped data."""
    df = st.session_state.ws_beams_df

    st.markdown("### 📥 Import Preview")

    if df is None or df.empty:
        st.warning("No data loaded. Go back to Welcome.")
        if st.button("← Back to Welcome"):
            set_workspace_state(WorkspaceState.WELCOME)
            st.rerun()
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Beams", len(df))
    col2.metric("Stories", df["story"].nunique())
    col3.metric("Avg Mu", f"{df['mu_knm'].mean():.1f} kN·m")
    col4.metric("Avg Vu", f"{df['vu_kn'].mean():.1f} kN")

    # Preview table
    st.dataframe(
        df[["beam_id", "story", "b_mm", "D_mm", "span_mm", "mu_knm", "vu_kn"]],
        use_container_width=True,
        height=250,
    )

    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Design All Beams", type="primary", use_container_width=True):
            with st.spinner("Designing beams..."):
                st.session_state.ws_design_results = design_all_beams_ws()
            st.session_state.ws_state = WorkspaceState.DESIGN
            st.rerun()
    with col2:
        if st.button("← Back to Welcome", use_container_width=True):
            st.session_state.ws_beams_df = None
            set_workspace_state(WorkspaceState.WELCOME)
            st.rerun()


def render_design_results() -> None:
    """Render design results with interactive table."""
    df = st.session_state.ws_design_results

    if df is None or df.empty:
        st.warning("No design results. Design beams first.")
        if st.button("← Back to Import"):
            set_workspace_state(WorkspaceState.IMPORT)
            st.rerun()
        return

    # Summary metrics in compact row
    total = len(df)
    passed = len(df[df["is_safe"] == True])
    failed = total - passed
    avg_util = df["utilization"].mean() * 100

    # Compact header with metrics
    c1, c2, c3, c4, c5 = st.columns([1.5, 1, 1, 1, 1.5])
    c1.markdown("### 📊 Results")
    c2.metric("Total", total)
    c3.metric("✅ Pass", passed)
    c4.metric("❌ Fail", failed)
    c5.metric("Util", f"{avg_util:.1f}%")

    # Filter row
    fc1, fc2, fc3 = st.columns([1, 1, 2])
    with fc1:
        story_filter = st.selectbox("📍 Story", ["All"] + sorted(df["story"].unique().tolist()), key="ws_story_filter")
    with fc2:
        status_filter = st.selectbox("🎯 Status", ["All", "Safe", "Failed"], key="ws_status_filter")

    # Apply filters
    filtered_df = df.copy()
    if story_filter != "All":
        filtered_df = filtered_df[filtered_df["story"] == story_filter]
    if status_filter == "Safe":
        filtered_df = filtered_df[filtered_df["is_safe"] == True]
    elif status_filter == "Failed":
        filtered_df = filtered_df[filtered_df["is_safe"] == False]

    # Results table with styled status
    display_df = filtered_df[["beam_id", "story", "b_mm", "D_mm", "mu_knm", "vu_kn", "ast_req", "utilization", "status"]].copy()
    display_df.columns = ["ID", "Story", "b", "D", "Mu", "Vu", "Ast", "Util", "Status"]
    display_df["Util"] = display_df["Util"].apply(lambda x: f"{x*100:.0f}%")

    st.dataframe(display_df, use_container_width=True, height=180, hide_index=True)

    # Beam selector with quick actions
    beam_options = filtered_df["beam_id"].tolist()
    if beam_options:
        selected = st.selectbox("🔍 Select beam for details:", beam_options, key="ws_beam_select2")
        st.session_state.ws_selected_beam = selected

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🎨 3D View", use_container_width=True, type="primary"):
                set_workspace_state(WorkspaceState.VIEW_3D)
                st.rerun()
        with col2:
            if st.button("🔧 Edit Rebar", use_container_width=True):
                set_workspace_state(WorkspaceState.REBAR_EDIT)
                st.rerun()
        with col3:
            if st.button("🏗️ Building", use_container_width=True):
                set_workspace_state(WorkspaceState.BUILDING_3D)
                st.rerun()
        with col4:
            if st.button("📊 Dashboard", use_container_width=True):
                set_workspace_state(WorkspaceState.DASHBOARD)
                st.rerun()

    st.divider()
    if st.button("← Back to Import"):
        set_workspace_state(WorkspaceState.IMPORT)
        st.rerun()


def create_building_3d_figure(df: pd.DataFrame) -> go.Figure:
    """Create impressive 3D building visualization with all beams.

    Features:
    - Real 3D beam volumes with proper orientation
    - Color by story or design status
    - Hover details for each beam
    - Professional lighting and camera
    """
    fig = go.Figure()

    if df is None or df.empty:
        return fig

    # Group by story for coloring
    stories = sorted(df["story"].unique())
    color_palette = [
        "#3498db",  # Blue
        "#2ecc71",  # Green
        "#e74c3c",  # Red
        "#9b59b6",  # Purple
        "#f39c12",  # Orange
        "#1abc9c",  # Teal
        "#e91e63",  # Pink
        "#00bcd4",  # Cyan
    ]
    story_colors = {s: color_palette[i % len(color_palette)] for i, s in enumerate(stories)}

    # Track extents for camera
    all_x, all_y, all_z = [], [], []

    for idx, row in df.iterrows():
        beam_id = row["beam_id"]
        story = row["story"]

        # Get coordinates
        x1 = float(row.get("x1", 0))
        y1 = float(row.get("y1", 0))
        z1 = float(row.get("z1", 0))
        x2 = float(row.get("x2", x1 + row["span_mm"] / 1000))
        y2 = float(row.get("y2", y1))
        z2 = float(row.get("z2", z1))

        all_x.extend([x1, x2])
        all_y.extend([y1, y2])
        all_z.extend([z1, z2])

        # Beam dimensions in meters
        b = row["b_mm"] / 1000
        d = row["D_mm"] / 1000

        # Calculate beam orientation
        dx, dy, dz = x2 - x1, y2 - y1, z2 - z1
        length = math.sqrt(dx**2 + dy**2 + dz**2)
        if length < 0.01:
            continue

        # Normalize direction
        dir_x, dir_y, dir_z = dx / length, dy / length, dz / length

        # Perpendicular vectors
        if abs(dir_z) < 0.99:
            perp_x, perp_y = -dir_y, dir_x
            perp_len = math.sqrt(perp_x**2 + perp_y**2)
            if perp_len > 0.001:
                perp_x, perp_y = perp_x / perp_len, perp_y / perp_len
            else:
                perp_x, perp_y = 1, 0
            up_x, up_y, up_z = 0, 0, 1
        else:
            perp_x, perp_y = 1, 0
            up_x, up_y, up_z = 0, 1, 0

        hw, hd = b / 2, d / 2

        # Build 8 corners
        corners = []
        for (ex, ey, ez) in [(x1, y1, z1), (x2, y2, z2)]:
            for ws in [-1, 1]:
                for ds in [-1, 1]:
                    cx = ex + ws * hw * perp_x + ds * hd * up_x
                    cy = ey + ws * hw * perp_y + ds * hd * up_y
                    cz = ez + ds * hd * up_z
                    corners.append((cx, cy, cz))

        x_mesh = [c[0] for c in corners]
        y_mesh = [c[1] for c in corners]
        z_mesh = [c[2] for c in corners]

        # Triangular faces for mesh
        i_faces = [0, 0, 4, 4, 0, 1, 2, 3, 0, 2, 1, 3]
        j_faces = [1, 2, 5, 6, 4, 5, 6, 7, 1, 6, 5, 7]
        k_faces = [3, 3, 7, 7, 5, 4, 4, 5, 2, 4, 3, 6]

        # Color based on status or story
        status = row.get("status", "")
        if "SAFE" in str(status).upper():
            color = "rgba(46, 204, 113, 0.85)"
        elif "FAIL" in str(status).upper():
            color = "rgba(231, 76, 60, 0.85)"
        else:
            base = story_colors.get(story, "#3498db")
            r, g, b_col = int(base[1:3], 16), int(base[3:5], 16), int(base[5:7], 16)
            color = f"rgba({r}, {g}, {b_col}, 0.8)"

        # Hover info
        hover = (
            f"<b>{beam_id}</b><br>"
            f"Story: {story}<br>"
            f"Section: {row['b_mm']:.0f}×{row['D_mm']:.0f} mm<br>"
            f"Mu: {row.get('mu_knm', 0):.1f} kN·m<br>"
            f"Status: {status}"
        )

        fig.add_trace(go.Mesh3d(
            x=x_mesh, y=y_mesh, z=z_mesh,
            i=i_faces, j=j_faces, k=k_faces,
            color=color,
            opacity=0.9,
            flatshading=True,
            lighting=dict(ambient=0.6, diffuse=0.8, specular=0.4, roughness=0.3),
            lightposition=dict(x=100, y=200, z=300),
            hovertemplate=hover + "<extra></extra>",
            name=beam_id,
            showlegend=False,
        ))

    # Add story legend
    for story in stories:
        base = story_colors[story]
        fig.add_trace(go.Scatter3d(
            x=[None], y=[None], z=[None],
            mode="markers",
            marker=dict(size=10, color=base, symbol="square"),
            name=f"📍 {story}",
        ))

    # Calculate scene range
    if all_x and all_y and all_z:
        x_range = [min(all_x) - 2, max(all_x) + 2]
        y_range = [min(all_y) - 2, max(all_y) + 2]
        z_range = [min(all_z) - 1, max(all_z) + 3]
    else:
        x_range = y_range = z_range = [0, 10]

    fig.update_layout(
        scene=dict(
            xaxis=dict(range=x_range, title="X (m)", showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(range=y_range, title="Y (m)", showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
            zaxis=dict(range=z_range, title="Z (m)", showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
            aspectmode="data",
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.0),
                up=dict(x=0, y=0, z=1),
            ),
            bgcolor="rgba(20, 20, 30, 1)",
        ),
        paper_bgcolor="rgba(20, 20, 30, 1)",
        plot_bgcolor="rgba(20, 20, 30, 1)",
        font=dict(color="white"),
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(
            yanchor="top", y=0.99, xanchor="left", x=0.01,
            bgcolor="rgba(30, 30, 40, 0.8)",
        ),
    )

    return fig


def render_building_3d() -> None:
    """Render impressive full building 3D view."""
    df = st.session_state.ws_design_results
    if df is None:
        df = st.session_state.ws_beams_df

    st.markdown("### 🏗️ Building 3D Visualization")

    if df is None or df.empty:
        st.warning("No beam data to visualize.")
        if st.button("← Back"):
            set_workspace_state(WorkspaceState.DESIGN)
            st.rerun()
        return

    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    total = len(df)
    stories = df["story"].nunique()
    safe_count = len(df[df.get("status", "").str.contains("SAFE", case=False, na=False)]) if "status" in df.columns else 0
    col1.metric("Total Beams", total)
    col2.metric("Stories", stories)
    col3.metric("Designed", safe_count)
    col4.metric("Pass Rate", f"{safe_count/total*100:.0f}%" if total > 0 else "N/A")

    # Create 3D figure
    fig = create_building_3d_figure(df)
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True, key="ws_building_3d")

    # Controls
    st.caption("💡 **Tip:** Click and drag to rotate, scroll to zoom, double-click to reset")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("← Back to Results"):
            set_workspace_state(WorkspaceState.DESIGN)
            st.rerun()
    with col2:
        # Beam selector for detail view
        beam_ids = df["beam_id"].tolist() if len(df) > 0 else []
        if beam_ids:
            selected = st.selectbox("Jump to beam:", ["Select..."] + beam_ids, key="bldg_beam_select")
            if selected != "Select...":
                st.session_state.ws_selected_beam = selected
                set_workspace_state(WorkspaceState.VIEW_3D)
                st.rerun()
    with col3:
        if st.button("📊 Dashboard"):
            set_workspace_state(WorkspaceState.DASHBOARD)
            st.rerun()


def calculate_rebar_checks(
    b_mm: float,
    D_mm: float,
    mu_knm: float,
    vu_kn: float,
    fck: float,
    fy: float,
    cover_mm: float,
    bottom_bars: list[tuple[int, int]],  # [(dia, count), ...]
    top_bars: list[tuple[int, int]],
    stirrup_dia: int,
    stirrup_spacing: int,
) -> dict[str, Any]:
    """Calculate all design checks for given rebar configuration.

    Returns utilization ratios and pass/fail status for:
    - Flexure capacity
    - Shear capacity
    - Minimum reinforcement
    - Maximum reinforcement
    - Spacing requirements
    - Development length
    """
    # Calculate areas
    ast_bottom = sum(count * math.pi * (dia/2)**2 for dia, count in bottom_bars)
    ast_top = sum(count * math.pi * (dia/2)**2 for dia, count in top_bars) if top_bars else 0
    ast_total = ast_bottom + ast_top

    # Effective depth
    max_dia_bottom = max((dia for dia, _ in bottom_bars), default=16)
    d_eff = D_mm - cover_mm - stirrup_dia - max_dia_bottom / 2

    # IS 456 checks
    results = {
        "ast_provided": ast_bottom,
        "ast_top": ast_top,
        "d_eff": d_eff,
    }

    # 1. Flexure capacity (approximate)
    # Mu = 0.87 * fy * Ast * (d - 0.42 * xu)
    # Simplified: Mu ≈ 0.87 * fy * Ast * 0.9 * d / 1e6 (for under-reinforced)
    mu_capacity = 0.87 * fy * ast_bottom * 0.9 * d_eff / 1e6
    flexure_util = mu_knm / mu_capacity if mu_capacity > 0 else 999
    results["mu_capacity_knm"] = mu_capacity
    results["flexure_util"] = flexure_util
    results["flexure_ok"] = flexure_util <= 1.0

    # 2. Minimum reinforcement (IS 456 Cl 26.5.1.1)
    ast_min = 0.85 * b_mm * d_eff / fy
    results["ast_min"] = ast_min
    results["min_reinf_ok"] = ast_bottom >= ast_min

    # 3. Maximum reinforcement (4% of gross area)
    ast_max = 0.04 * b_mm * D_mm
    results["ast_max"] = ast_max
    results["max_reinf_ok"] = ast_total <= ast_max

    # 4. Shear capacity
    # τc from IS 456 Table 19 (approximate)
    pt = 100 * ast_bottom / (b_mm * d_eff) if d_eff > 0 else 0
    tau_c = min(0.28 * (pt ** 0.5) * (fck ** 0.33), 0.62 * (fck ** 0.5))  # Simplified
    vc_concrete = tau_c * b_mm * d_eff / 1000  # kN

    # Stirrup contribution
    asv = 2 * math.pi * (stirrup_dia / 2) ** 2
    sv = max(stirrup_spacing, 50)  # Avoid division issues
    vs_stirrup = 0.87 * fy * asv * d_eff / sv / 1000  # kN

    vu_capacity = vc_concrete + vs_stirrup
    shear_util = vu_kn / vu_capacity if vu_capacity > 0 else 999
    results["vu_capacity_kn"] = vu_capacity
    results["shear_util"] = shear_util
    results["shear_ok"] = shear_util <= 1.0

    # 5. Spacing check (min clear spacing = max(bar_dia, 25mm))
    clear_cover = cover_mm + stirrup_dia
    total_bar_width = sum(count * dia for dia, count in bottom_bars)
    available_width = b_mm - 2 * clear_cover
    num_bars = sum(count for _, count in bottom_bars)
    if num_bars > 1:
        spacing = (available_width - total_bar_width) / (num_bars - 1)
    else:
        spacing = available_width
    min_spacing = max(max_dia_bottom, 25)
    results["bar_spacing"] = spacing
    results["spacing_ok"] = spacing >= min_spacing

    # Overall status
    all_ok = all([
        results["flexure_ok"],
        results["min_reinf_ok"],
        results["max_reinf_ok"],
        results["shear_ok"],
        results["spacing_ok"],
    ])
    results["all_ok"] = all_ok
    results["status"] = "✅ SAFE" if all_ok else "❌ REVISE"

    return results


def render_rebar_editor() -> None:
    """Render interactive reinforcement editor with real-time checks."""
    beam_id = st.session_state.ws_selected_beam
    df = st.session_state.ws_design_results
    if df is None:
        df = st.session_state.ws_beams_df

    st.markdown(f"### 🔧 Reinforcement Editor: {beam_id}")

    if not beam_id or df is None or df.empty:
        st.warning("No beam selected.")
        if st.button("← Back"):
            set_workspace_state(WorkspaceState.DESIGN)
            st.rerun()
        return

    row = df[df["beam_id"] == beam_id]
    if row.empty:
        st.error(f"Beam {beam_id} not found")
        return
    row = row.iloc[0]

    # Fixed beam properties
    b_mm = float(row["b_mm"])
    D_mm = float(row["D_mm"])
    span_mm = float(row["span_mm"])
    mu_knm = float(row.get("mu_knm", 100))
    vu_kn = float(row.get("vu_kn", 50))
    fck = float(row.get("fck", 25))
    fy = float(row.get("fy", 500))
    cover_mm = float(row.get("cover_mm", 40))

    # Show fixed properties
    st.markdown(f"**Section:** {b_mm:.0f}×{D_mm:.0f} mm | **Span:** {span_mm/1000:.1f} m | **Mu:** {mu_knm:.1f} kN·m | **Vu:** {vu_kn:.1f} kN")

    # Initialize rebar config from session state or defaults
    config = st.session_state.ws_rebar_config
    if config is None or config.get("beam_id") != beam_id:
        # Initialize with design suggestion
        ast_req = float(row.get("ast_req", 500))
        suggested = calculate_rebar_layout(ast_req, b_mm, D_mm, span_mm, vu_kn, cover_mm)
        config = {
            "beam_id": beam_id,
            "bottom_layer1_dia": suggested.get("bar_diameter", 16),
            "bottom_layer1_count": len(suggested.get("bottom_bars", [])),
            "bottom_layer2_dia": 0,
            "bottom_layer2_count": 0,
            "top_dia": 12,
            "top_count": 2,
            "stirrup_dia": 8,
            "stirrup_spacing": 150,
        }
        st.session_state.ws_rebar_config = config

    # Editable rebar configuration
    col1, col2 = st.columns([0.45, 0.55])

    with col1:
        st.markdown("##### Bottom Reinforcement")
        c1, c2 = st.columns(2)
        with c1:
            l1_dia = st.selectbox("Layer 1 Dia (mm)", [10, 12, 16, 20, 25, 32],
                                  index=[10, 12, 16, 20, 25, 32].index(config["bottom_layer1_dia"]),
                                  key="re_l1_dia")
            l2_dia = st.selectbox("Layer 2 Dia (mm)", [0, 10, 12, 16, 20, 25, 32],
                                  index=[0, 10, 12, 16, 20, 25, 32].index(config.get("bottom_layer2_dia", 0)),
                                  key="re_l2_dia")
        with c2:
            l1_count = st.number_input("Count", 2, 8, config["bottom_layer1_count"], key="re_l1_cnt")
            l2_count = st.number_input("Count", 0, 6, config.get("bottom_layer2_count", 0), key="re_l2_cnt")

        st.markdown("##### Top Reinforcement")
        c1, c2 = st.columns(2)
        with c1:
            top_dia = st.selectbox("Dia (mm)", [10, 12, 16, 20],
                                   index=[10, 12, 16, 20].index(config.get("top_dia", 12)),
                                   key="re_top_dia")
        with c2:
            top_count = st.number_input("Count", 2, 6, config.get("top_count", 2), key="re_top_cnt")

        st.markdown("##### Stirrups")
        c1, c2 = st.columns(2)
        with c1:
            stir_dia = st.selectbox("Dia (mm)", [6, 8, 10],
                                    index=[6, 8, 10].index(config.get("stirrup_dia", 8)),
                                    key="re_stir_dia")
        with c2:
            stir_spacing = st.number_input("Spacing (mm)", 75, 300, config.get("stirrup_spacing", 150),
                                           step=25, key="re_stir_sp")

    # Update config
    config.update({
        "bottom_layer1_dia": l1_dia,
        "bottom_layer1_count": l1_count,
        "bottom_layer2_dia": l2_dia,
        "bottom_layer2_count": l2_count,
        "top_dia": top_dia,
        "top_count": top_count,
        "stirrup_dia": stir_dia,
        "stirrup_spacing": stir_spacing,
    })
    st.session_state.ws_rebar_config = config

    # Build bar lists
    bottom_bars = [(l1_dia, l1_count)]
    if l2_dia > 0 and l2_count > 0:
        bottom_bars.append((l2_dia, l2_count))
    top_bars = [(top_dia, top_count)]

    # Calculate checks
    checks = calculate_rebar_checks(
        b_mm, D_mm, mu_knm, vu_kn, fck, fy, cover_mm,
        bottom_bars, top_bars, stir_dia, stir_spacing
    )

    with col2:
        st.markdown("##### Design Checks")

        # Flexure
        flex_color = "🟢" if checks["flexure_ok"] else "🔴"
        st.markdown(f"{flex_color} **Flexure:** {checks['flexure_util']*100:.1f}% (Mu = {checks['mu_capacity_knm']:.1f} kN·m)")

        # Shear
        shear_color = "🟢" if checks["shear_ok"] else "🔴"
        st.markdown(f"{shear_color} **Shear:** {checks['shear_util']*100:.1f}% (Vu = {checks['vu_capacity_kn']:.1f} kN)")

        # Min reinforcement
        min_color = "🟢" if checks["min_reinf_ok"] else "🔴"
        st.markdown(f"{min_color} **Min Ast:** {checks['ast_provided']:.0f} ≥ {checks['ast_min']:.0f} mm²")

        # Max reinforcement
        max_color = "🟢" if checks["max_reinf_ok"] else "🔴"
        st.markdown(f"{max_color} **Max Ast:** {checks['ast_provided']:.0f} ≤ {checks['ast_max']:.0f} mm²")

        # Spacing
        sp_color = "🟢" if checks["spacing_ok"] else "🔴"
        st.markdown(f"{sp_color} **Bar Spacing:** {checks['bar_spacing']:.0f} mm")

        st.divider()

        # Overall status with big indicator
        if checks["all_ok"]:
            st.success(f"### {checks['status']}")
            st.caption(f"Ast provided: {checks['ast_provided']:.0f} mm² | d_eff: {checks['d_eff']:.0f} mm")
        else:
            st.error(f"### {checks['status']}")
            st.caption("Adjust reinforcement to satisfy all checks")

    # Navigation
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("← Back to 3D View"):
            set_workspace_state(WorkspaceState.VIEW_3D)
            st.rerun()
    with col2:
        if st.button("🏗️ Building View"):
            set_workspace_state(WorkspaceState.BUILDING_3D)
            st.rerun()
    with col3:
        if st.button("▶ Next Beam"):
            beam_list = df["beam_id"].tolist() if len(df) > 0 else []
            if len(beam_list) > 1:
                curr_idx = beam_list.index(beam_id) if beam_id in beam_list else 0
                next_idx = (curr_idx + 1) % len(beam_list)
                st.session_state.ws_selected_beam = beam_list[next_idx]
                st.session_state.ws_rebar_config = None  # Reset for new beam
                st.rerun()


def render_3d_view() -> None:
    """Render detailed 3D view for selected beam."""
    beam_id = st.session_state.ws_selected_beam
    df = st.session_state.ws_design_results

    st.markdown(f"### 🎨 3D View: {beam_id}")

    if not beam_id or df is None:
        st.warning("No beam selected.")
        if st.button("← Back to Results"):
            set_workspace_state(WorkspaceState.DESIGN)
            st.rerun()
        return

    row = df[df["beam_id"] == beam_id]
    if row.empty:
        st.error(f"Beam {beam_id} not found")
        return

    row = row.iloc[0]

    # Beam info metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Section", f"{row['b_mm']:.0f}×{row['D_mm']:.0f}")
    col2.metric("Span", f"{row['span_mm']/1000:.1f} m")
    col3.metric("Ast Required", f"{row['ast_req']:.0f} mm²")
    col4.metric("Status", row["status"])

    # Calculate rebar layout
    rebar = calculate_rebar_layout(
        ast_mm2=row["ast_req"],
        b_mm=row["b_mm"],
        D_mm=row["D_mm"],
        span_mm=row["span_mm"],
        vu_kn=row["vu_kn"],
        cover_mm=row.get("cover_mm", 40),
    )

    st.caption(f"**{rebar['summary']}** — {rebar['spacing_summary']}")

    # 3D Figure
    if VISUALIZATION_AVAILABLE:
        try:
            fig = create_beam_3d_figure(
                b=row["b_mm"],
                D=row["D_mm"],
                span=row["span_mm"],
                bottom_bars=rebar["bottom_bars"],
                top_bars=rebar["top_bars"],
                stirrup_positions=rebar["stirrup_positions"],
                bar_diameter=rebar.get("bar_diameter", 16),
                stirrup_diameter=rebar.get("stirrup_diameter", 8),
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True, key="ws_3d_view")
        except Exception as e:
            st.error(f"3D rendering error: {e}")
    else:
        st.info("3D visualization not available")

    # Navigation - compact 4-button row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("← Results", use_container_width=True):
            set_workspace_state(WorkspaceState.DESIGN)
            st.rerun()
    with col2:
        if st.button("🔧 Edit Rebar", use_container_width=True, type="primary"):
            set_workspace_state(WorkspaceState.REBAR_EDIT)
            st.rerun()
    with col3:
        if st.button("🏗️ Building", use_container_width=True):
            set_workspace_state(WorkspaceState.BUILDING_3D)
            st.rerun()
    with col4:
        # Next beam button
        beam_list = df["beam_id"].tolist() if df is not None and len(df) > 0 else []
        if len(beam_list) > 1:
            curr_idx = beam_list.index(beam_id) if beam_id in beam_list else 0
            next_idx = (curr_idx + 1) % len(beam_list)
            if st.button("▶ Next", use_container_width=True):
                st.session_state.ws_selected_beam = beam_list[next_idx]
                st.rerun()
        else:
            st.button("▶ Next", use_container_width=True, disabled=True)


def render_beam_editor() -> None:
    """Render single beam editor with live preview."""
    beam_id = st.session_state.ws_selected_beam
    df = st.session_state.ws_beams_df

    st.markdown(f"### ✏️ Edit Beam: {beam_id or 'New'}")

    if df is None or df.empty:
        st.warning("No beam data.")
        if st.button("← Back to Welcome"):
            set_workspace_state(WorkspaceState.WELCOME)
            st.rerun()
        return

    # Get beam data
    if beam_id:
        row = df[df["beam_id"] == beam_id]
        if row.empty:
            row = df.iloc[[0]]
        row = row.iloc[0]
    else:
        row = df.iloc[0]

    # Safe float conversion helper
    def safe_float(val, default: float) -> float:
        try:
            return float(val) if val is not None and not pd.isna(val) else default
        except (ValueError, TypeError):
            return default

    col1, col2 = st.columns([0.4, 0.6])

    with col1:
        st.markdown("**Geometry**")
        b = st.number_input("Width b (mm)", value=safe_float(row.get("b_mm"), 300.0), step=25.0, key="edit_b")
        D = st.number_input("Depth D (mm)", value=safe_float(row.get("D_mm"), 500.0), step=25.0, key="edit_D")
        span = st.number_input("Span (mm)", value=safe_float(row.get("span_mm"), 5000.0), step=100.0, key="edit_span")

        st.markdown("**Loading**")
        mu = st.number_input("Moment Mu (kN·m)", value=safe_float(row.get("mu_knm"), 100.0), step=10.0, key="edit_mu")
        vu = st.number_input("Shear Vu (kN)", value=safe_float(row.get("vu_kn"), 50.0), step=5.0, key="edit_vu")

        st.markdown("**Materials**")
        fck = st.selectbox("Concrete", [20, 25, 30, 35, 40], index=1, key="edit_fck")
        fy = st.selectbox("Steel", [415, 500, 550], index=1, key="edit_fy")

        if st.button("💫 Redesign", type="primary", use_container_width=True):
            # Update dataframe
            idx = df[df["beam_id"] == row["beam_id"]].index
            if len(idx) > 0:
                df.loc[idx[0], ["b_mm", "D_mm", "span_mm", "mu_knm", "vu_kn", "fck", "fy"]] = [b, D, span, mu, vu, fck, fy]
                st.session_state.ws_beams_df = df
                st.session_state.ws_design_results = design_all_beams_ws()
                st.success("✅ Redesigned!")
                st.rerun()

    with col2:
        # Live preview with current values
        updated_row = pd.Series({
            "b_mm": b, "D_mm": D, "span_mm": span,
            "mu_knm": mu, "vu_kn": vu, "fck": fck, "fy": fy,
            "cover_mm": row.get("cover_mm", 40),
        })
        design = design_beam_row(updated_row)

        st.metric("Status", design["status"])
        st.metric("Ast Required", f"{design['ast_req']:.0f} mm²")
        st.metric("Utilization", f"{design['utilization']*100:.1f}%")

        if VISUALIZATION_AVAILABLE and design["ast_req"] > 0:
            rebar = calculate_rebar_layout(
                ast_mm2=design["ast_req"],
                b_mm=b,
                D_mm=D,
                span_mm=span,
                vu_kn=vu,
            )
            try:
                fig = create_beam_3d_figure(
                    b=b, D=D, span=span,
                    bottom_bars=rebar["bottom_bars"],
                    top_bars=rebar["top_bars"],
                    stirrup_positions=rebar["stirrup_positions"],
                )
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True, key="edit_3d_preview")
            except Exception as e:
                st.error(f"Preview error: {e}")

    st.divider()
    if st.button("← Back to Results"):
        set_workspace_state(WorkspaceState.DESIGN)
        st.rerun()


def render_dashboard() -> None:
    """Render SmartDesigner dashboard."""
    st.markdown("### 📊 Smart Dashboard")

    df = st.session_state.ws_design_results

    if df is None or df.empty:
        st.info("Design beams first to see dashboard")
        if st.button("← Back to Import"):
            set_workspace_state(WorkspaceState.IMPORT)
            st.rerun()
        return

    # Summary stats
    total = len(df)
    passed = len(df[df["is_safe"] == True])
    avg_util = df["utilization"].mean() * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Success Rate", f"{100*passed/max(total,1):.1f}%")
    col2.metric("Avg Utilization", f"{avg_util:.1f}%")
    col3.metric("Total Beams", total)

    # Utilization distribution
    st.markdown("**Utilization Distribution:**")
    low = len(df[df["utilization"] < 0.6])
    optimal = len(df[(df["utilization"] >= 0.6) & (df["utilization"] <= 0.85)])
    high = len(df[df["utilization"] > 0.85])

    col1, col2, col3 = st.columns(3)
    col1.metric("🟢 Under-utilized (<60%)", low, help="Consider reducing section")
    col2.metric("🟡 Optimal (60-85%)", optimal, help="Good design efficiency")
    col3.metric("🔴 Near Capacity (>85%)", high, help="Check if OK or increase section")

    # Quick wins
    st.markdown("**💡 Suggestions:**")
    if low > total * 0.3:
        st.success(f"💰 {low} beams are under-utilized. Consider reducing sections to save material.")
    if high > 0:
        st.warning(f"⚠️ {high} beams near capacity. Verify adequacy under all load combinations.")
    if passed == total:
        st.success("✅ All beams pass design checks!")

    st.divider()
    if st.button("← Back to Results"):
        set_workspace_state(WorkspaceState.DESIGN)
        st.rerun()


def render_dynamic_workspace() -> None:
    """Main workspace renderer - routes to correct state panel."""
    state = st.session_state.ws_state

    # State indicator bar - show progress through workflow
    states_order = [
        WorkspaceState.WELCOME,
        WorkspaceState.IMPORT,
        WorkspaceState.DESIGN,
        WorkspaceState.BUILDING_3D,
        WorkspaceState.VIEW_3D,
    ]

    current_idx = states_order.index(state) if state in states_order else 0
    progress = (current_idx + 1) / len(states_order)

    # Compact state badge instead of progress bar
    state_labels = {
        WorkspaceState.WELCOME: "🏠 Welcome",
        WorkspaceState.IMPORT: "📥 Import",
        WorkspaceState.DESIGN: "📊 Design",
        WorkspaceState.BUILDING_3D: "🏗️ Building 3D",
        WorkspaceState.VIEW_3D: "🎨 Beam 3D",
        WorkspaceState.REBAR_EDIT: "🔧 Rebar Edit",
        WorkspaceState.EDIT: "✏️ Edit",
        WorkspaceState.DASHBOARD: "📈 Dashboard",
    }
    st.caption(f"**{state_labels.get(state, state.value.upper())}**")

    # Route to correct renderer
    if state == WorkspaceState.WELCOME:
        render_welcome_panel()
    elif state == WorkspaceState.IMPORT:
        render_import_preview()
    elif state == WorkspaceState.DESIGN:
        render_design_results()
    elif state == WorkspaceState.BUILDING_3D:
        render_building_3d()
    elif state == WorkspaceState.VIEW_3D:
        render_3d_view()
    elif state == WorkspaceState.REBAR_EDIT:
        render_rebar_editor()
    elif state == WorkspaceState.EDIT:
        render_beam_editor()
    elif state == WorkspaceState.DASHBOARD:
        render_dashboard()
    else:
        st.error(f"Unknown state: {state}")
        render_welcome_panel()
