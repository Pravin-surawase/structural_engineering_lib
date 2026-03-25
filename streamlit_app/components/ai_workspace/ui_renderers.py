# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
UI rendering functions for the AI Workspace.

Extracted from ai_workspace.py (TASK-508).
Contains all render_* functions, 3D visualization builders,
table editors, and the main render_dynamic_workspace dispatcher.
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Try to import visualization components
try:
    from components.visualizations_3d import (
        create_beam_3d_figure,
        create_multi_beam_3d_figure,
    )

    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

# Import from sibling modules
from .workspace_state import (
    WorkspaceState,
    BAR_OPTIONS,
    STIRRUP_OPTIONS,
    init_workspace_state,
    set_workspace_state,
    get_workspace_state,
)
from .import_handler import (
    load_sample_data,
    process_uploaded_file,
    process_multi_files,
)
from .design_handler import (
    calculate_rebar_layout,
    design_beam_row,
    design_all_beams_ws,
)
from .rebar_handler import (
    calculate_constructability_score,
    suggest_optimal_rebar,
    optimize_beam_line,
    calculate_rebar_checks,
)
from .export_handler import (
    _generate_and_download_report,
    _generate_and_download_pdf_report,
    _generate_and_download_dxf,
    calculate_material_takeoff,
)

# Import shared section geometry
from utils.section_geometry import calculate_bar_positions

# Import PDF availability check
try:
    from utils.pdf_generator import is_reportlab_available

    PDF_AVAILABLE = is_reportlab_available()
except ImportError:
    PDF_AVAILABLE = False


def render_welcome_panel() -> None:
    """Render welcome state with quick start cards."""
    st.markdown("### 🏗️ Beam Design Workspace")

    # Compact intro
    st.caption("Import your ETABS/SAFE data or start with sample beams")

    col1, col2 = st.columns([1, 1])

    with col1:
        with st.container(border=True):
            st.markdown("#### 📂 Quick Demo")
            st.caption("10 beams · 3 stories · Ready to design")
            if st.button(
                "▶ Load Sample Data",
                key="ws_sample",
                use_container_width=True,
                type="primary",
                help="Load sample ETABS data with 3D coordinates",
            ):
                with st.spinner("Loading sample data..."):
                    load_sample_data()
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("#### 📤 Import CSV Files")
            st.caption("Geometry + Forces (1 or 2 files)")

            # Single unified file uploader that accepts multiple files
            uploaded_files = st.file_uploader(
                "Upload CSV/Excel",
                type=["csv", "xlsx"],
                key="ws_multi_upload",
                label_visibility="collapsed",
                accept_multiple_files=True,
                help="Upload 1 file (combined) or 2 files (geometry + forces)",
            )

            if uploaded_files:
                if len(uploaded_files) == 1:
                    # Single file - process as combined
                    with st.spinner("Processing file..."):
                        success, message = process_uploaded_file(uploaded_files[0])
                    if success:
                        st.success(message)
                        st.session_state.ws_state = WorkspaceState.IMPORT
                        st.rerun()
                    else:
                        st.error(message)
                elif len(uploaded_files) == 2:
                    # Two files - merge geometry + forces
                    st.info(f"📁 {uploaded_files[0].name} + {uploaded_files[1].name}")
                    if st.button(
                        "🔄 Merge & Import", type="primary", use_container_width=True
                    ):
                        with st.spinner("Merging files..."):
                            success, message = process_multi_files(
                                uploaded_files[0], uploaded_files[1]
                            )
                        if success:
                            st.success(message)
                            st.session_state.ws_state = WorkspaceState.IMPORT
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.warning("Please upload 1 or 2 files only")

    # Compact workflow hint
    st.markdown("---")
    st.markdown(
        "**Workflow:** `load sample` → `design all` → `building 3d` → Select beam → `edit rebar`"
    )


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
        if st.button(
            "🚀 Design All Beams",
            type="primary",
            use_container_width=True,
            help="Run IS456 flexure & shear design on all beams",
        ):
            with st.spinner("Designing beams..."):
                st.session_state.ws_design_results = design_all_beams_ws()
            st.session_state.ws_state = WorkspaceState.DESIGN
            st.rerun()
    with col2:
        if st.button(
            "← Back to Welcome",
            use_container_width=True,
            help="Clear data and return to start screen",
        ):
            st.session_state.ws_beams_df = None
            set_workspace_state(WorkspaceState.WELCOME)
            st.rerun()
def render_design_results() -> None:
    """Render design results with interactive editable table.

    Features Excel-like inline editing for rebar configuration with live
    design checks that update as you type, similar to how engineers work
    in spreadsheets.
    """
    df = st.session_state.ws_design_results

    if df is None or df.empty:
        st.warning("No design results. Design beams first.")
        if st.button("← Back to Import"):
            set_workspace_state(WorkspaceState.IMPORT)
            st.rerun()
        return

    # Summary metrics in compact row
    total = len(df)
    passed = len(df[df["is_safe"]])
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
        story_filter = st.selectbox(
            "📍 Story",
            ["All"] + sorted(df["story"].unique().tolist()),
            key="ws_story_filter",
        )
    with fc2:
        status_filter = st.selectbox(
            "🎯 Status", ["All", "Safe", "Failed"], key="ws_status_filter"
        )
    with fc3:
        edit_mode = st.checkbox(
            "✏️ Enable inline editing",
            key="ws_edit_mode",
            help="Edit rebar directly in the table",
        )

    # Apply filters
    filtered_df = df.copy()
    if story_filter != "All":
        filtered_df = filtered_df[filtered_df["story"] == story_filter]
    if status_filter == "Safe":
        filtered_df = filtered_df[filtered_df["is_safe"]]
    elif status_filter == "Failed":
        filtered_df = filtered_df[~filtered_df["is_safe"]]

    if edit_mode:
        # Editable mode - allows changing rebar configuration inline
        _render_editable_results_table(filtered_df, df)
    else:
        # Read-only mode - standard display
        display_df = filtered_df[
            [
                "beam_id",
                "story",
                "b_mm",
                "D_mm",
                "mu_knm",
                "vu_kn",
                "ast_req",
                "utilization",
                "status",
            ]
        ].copy()
        display_df.columns = [
            "ID",
            "Story",
            "b",
            "D",
            "Mu",
            "Vu",
            "Ast",
            "Util",
            "Status",
        ]
        display_df["Util"] = display_df["Util"].apply(lambda x: f"{x * 100:.0f}%")
        st.dataframe(display_df, use_container_width=True, height=180, hide_index=True)

    # Beam selector with quick actions
    beam_options = filtered_df["beam_id"].tolist()
    if beam_options:
        selected = st.selectbox(
            "🔍 Select beam for details:", beam_options, key="ws_beam_select2"
        )
        st.session_state.ws_selected_beam = selected

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if st.button(
                "✏️ Editor",
                use_container_width=True,
                type="primary",
                help="Full-width unified editor with live checks",
            ):
                # Initialize editor mode
                st.session_state.ws_editor_mode["beam_queue"] = beam_options
                st.session_state.ws_editor_mode["current_beam_idx"] = (
                    beam_options.index(selected)
                )
                st.session_state.ws_editor_mode["filter_mode"] = "all"
                set_workspace_state(WorkspaceState.UNIFIED_EDITOR)
                st.rerun()
        with col2:
            if st.button(
                "🎨 3D View",
                use_container_width=True,
                help="Interactive 3D visualization of the selected beam",
            ):
                set_workspace_state(WorkspaceState.VIEW_3D)
                st.rerun()
        with col3:
            if st.button(
                "📐 Section",
                use_container_width=True,
                help="View cross-section with reinforcement layout",
            ):
                set_workspace_state(WorkspaceState.CROSS_SECTION)
                st.rerun()
        with col4:
            if st.button(
                "🔧 Rebar",
                use_container_width=True,
                help="Edit reinforcement to fix failed designs",
            ):
                set_workspace_state(WorkspaceState.REBAR_EDIT)
                st.rerun()
        with col5:
            if st.button(
                "🏗️ Building",
                use_container_width=True,
                help="See all beams in 3D building context",
            ):
                set_workspace_state(WorkspaceState.BUILDING_3D)
                st.rerun()

    # Help tip for failed beams
    if failed > 0:
        if edit_mode:
            st.info(
                "💡 **Tip:** Increase bar count or diameter for failed beams. Changes update live!"
            )
        else:
            st.warning(
                f"💡 **{failed} beams failed.** Enable **inline editing** or select one and use **Edit Rebar**."
            )


def _render_editable_results_table(
    filtered_df: pd.DataFrame, full_df: pd.DataFrame
) -> None:
    """Render editable results table with live design checks.

    Allows engineers to modify rebar configuration (bar count, diameter, layers)
    directly in the table, similar to Excel workflows. Design checks update
    automatically as values change.
    """

    # Prepare editable dataframe
    edit_df = filtered_df[
        ["beam_id", "story", "b_mm", "D_mm", "mu_knm", "vu_kn", "fck", "fy"]
    ].copy()

    # Add editable rebar columns with default values
    edit_df["bot_bars"] = (
        filtered_df.get("bottom_bar_count", pd.Series([4] * len(filtered_df)))
        .fillna(4)
        .astype(int)
    )
    edit_df["bot_dia"] = (
        filtered_df.get("bottom_bar_dia", pd.Series([16] * len(filtered_df)))
        .fillna(16)
        .astype(int)
    )
    edit_df["top_bars"] = (
        filtered_df.get("top_bar_count", pd.Series([2] * len(filtered_df)))
        .fillna(2)
        .astype(int)
    )
    edit_df["top_dia"] = (
        filtered_df.get("top_bar_dia", pd.Series([12] * len(filtered_df)))
        .fillna(12)
        .astype(int)
    )
    edit_df["stirrup_sp"] = (
        filtered_df.get("stirrup_spacing", pd.Series([150] * len(filtered_df)))
        .fillna(150)
        .astype(int)
    )

    # Display columns for editing
    column_config = {
        "beam_id": st.column_config.TextColumn("ID", disabled=True, width="small"),
        "story": st.column_config.TextColumn("Story", disabled=True, width="small"),
        "b_mm": st.column_config.NumberColumn(
            "b", disabled=True, width="small", format="%d"
        ),
        "D_mm": st.column_config.NumberColumn(
            "D", disabled=True, width="small", format="%d"
        ),
        "mu_knm": st.column_config.NumberColumn(
            "Mu", disabled=True, width="small", format="%.0f"
        ),
        "vu_kn": st.column_config.NumberColumn(
            "Vu", disabled=True, width="small", format="%.0f"
        ),
        "fck": st.column_config.NumberColumn("fck", disabled=True, width="small"),
        "fy": st.column_config.NumberColumn("fy", disabled=True, width="small"),
        "bot_bars": st.column_config.NumberColumn(
            "Bot#",
            min_value=2,
            max_value=12,
            step=1,
            width="small",
            help="Number of bottom bars",
        ),
        "bot_dia": st.column_config.SelectboxColumn(
            "ϕBot",
            options=[10, 12, 16, 20, 25, 32],
            width="small",
            help="Bottom bar diameter (mm)",
        ),
        "top_bars": st.column_config.NumberColumn(
            "Top#",
            min_value=2,
            max_value=8,
            step=1,
            width="small",
            help="Number of top (hanger) bars",
        ),
        "top_dia": st.column_config.SelectboxColumn(
            "ϕTop",
            options=[10, 12, 16, 20, 25],
            width="small",
            help="Top bar diameter (mm)",
        ),
        "stirrup_sp": st.column_config.SelectboxColumn(
            "Sv",
            options=[100, 125, 150, 175, 200, 225, 250, 275, 300],
            width="small",
            help="Stirrup spacing (mm)",
        ),
    }

    # Editable data editor
    edited_df = st.data_editor(
        edit_df,
        column_config=column_config,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key="ws_edit_table",
    )

    # Calculate live checks for edited values
    st.markdown("#### Live Design Checks")
    check_results = []

    def safe_int(val: Any, default: int = 0) -> int:
        """Safely convert value to int, handling NaN and None."""
        if pd.isna(val) or val is None:
            return default
        try:
            return int(val)
        except (ValueError, TypeError):
            return default

    for idx, row in edited_df.iterrows():
        beam_id = row["beam_id"]
        b = safe_int(row.get("b_mm", 300), 300)
        D = safe_int(row.get("D_mm", 450), 450)
        mu = row.get("mu_knm", 0) if pd.notna(row.get("mu_knm")) else 0
        vu = row.get("vu_kn", 0) if pd.notna(row.get("vu_kn")) else 0
        fck = row.get("fck", 25) if pd.notna(row.get("fck")) else 25
        fy = row.get("fy", 500) if pd.notna(row.get("fy")) else 500
        bot_bars, bot_dia = (
            safe_int(row.get("bot_bars"), 2),
            safe_int(row.get("bot_dia"), 16),
        )
        top_bars, top_dia = (
            safe_int(row.get("top_bars"), 2),
            safe_int(row.get("top_dia"), 12),
        )
        stirrup_sp = safe_int(row.get("stirrup_sp"), 150)

        # Calculate provided steel area
        ast_prov = bot_bars * (math.pi * bot_dia**2 / 4)
        cover = 40  # Assume 40mm cover
        d_eff = D - cover - 8 - bot_dia / 2

        # Calculate required steel (simplified)
        try:
            # Use IS 456 formula for Ast required
            mu_nm = mu * 1e6  # kN·m to N·mm
            xu_max = 0.48 * d_eff  # For Fe500
            mu_lim = 0.36 * fck * b * xu_max * (d_eff - 0.416 * xu_max)

            if mu_nm <= mu_lim:
                ast_req = (
                    (0.5 * fck / fy)
                    * (1 - math.sqrt(1 - 4.6 * mu_nm / (fck * b * d_eff**2)))
                    * b
                    * d_eff
                )
            else:
                ast_req = mu_nm / (0.87 * fy * (d_eff - 0.416 * xu_max))

            # Minimum steel
            ast_min = 0.85 * b * d_eff / fy

            is_flexure_ok = ast_prov >= max(ast_req, ast_min)
            utilization = ast_req / ast_prov if ast_prov > 0 else 999

            # Shear check (simplified)
            tv = vu * 1000 / (b * d_eff)  # N/mm²
            tc_max = 0.63 * math.sqrt(fck)  # Approximate
            is_shear_ok = tv < tc_max

            is_safe = is_flexure_ok and is_shear_ok
            status = "✅ SAFE" if is_safe else "❌ FAIL"

        except Exception:
            is_safe = False
            utilization = 1.0
            status = "⚠️ Error"
            ast_req = 0

        check_results.append(
            {
                "ID": beam_id,
                "Ast Req": f"{ast_req:.0f}",
                "Ast Prov": f"{ast_prov:.0f}",
                "Util": f"{utilization * 100:.0f}%",
                "Status": status,
            }
        )

    # Display check results
    check_df = pd.DataFrame(check_results)
    st.dataframe(check_df, hide_index=True, use_container_width=True, height=150)

    # Apply changes button
    if st.button("💾 Apply Changes to All", type="primary", use_container_width=True):
        # Update the main results DataFrame with edited values
        for idx, row in edited_df.iterrows():
            beam_id = row["beam_id"]
            mask = full_df["beam_id"] == beam_id
            if mask.any():
                full_df.loc[mask, "bottom_bar_count"] = safe_int(row.get("bot_bars"), 2)
                full_df.loc[mask, "bottom_bar_dia"] = safe_int(row.get("bot_dia"), 16)
                full_df.loc[mask, "top_bar_count"] = safe_int(row.get("top_bars"), 2)
                full_df.loc[mask, "top_bar_dia"] = safe_int(row.get("top_dia"), 12)
                full_df.loc[mask, "stirrup_spacing"] = safe_int(
                    row.get("stirrup_sp"), 150
                )

        st.session_state.ws_design_results = full_df
        st.success("✅ Changes applied! Recalculating design checks...")
        st.rerun()

    st.divider()

    # Export buttons row
    st.caption("📤 **Export Options**")
    exp1, exp2, exp3, exp4 = st.columns(4)

    with exp1:
        if st.button(
            "📄 HTML",
            use_container_width=True,
            help="Design report in HTML format (web viewable)",
        ):
            _generate_and_download_report(filtered_df)

    with exp2:
        if st.button(
            "📑 PDF",
            use_container_width=True,
            help="Professional PDF report (printable)",
        ):
            _generate_and_download_pdf_report(filtered_df)

    with exp3:
        if st.button(
            "📐 DXF", use_container_width=True, help="Export CAD drawings for detailing"
        ):
            _generate_and_download_dxf(filtered_df)

    with exp4:
        if st.button(
            "📊 CSV", use_container_width=True, help="Export results as CSV spreadsheet"
        ):
            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv_data,
                file_name="beam_design_results.csv",
                mime="text/csv",
                key="ws_csv_download",
            )

    c1, c2 = st.columns(2)
    with c1:
        if st.button(
            "📊 Dashboard",
            use_container_width=True,
            help="See summary stats, cost breakdown, and export options",
        ):
            set_workspace_state(WorkspaceState.DASHBOARD)
            st.rerun()
    with c2:
        if st.button(
            "← Import",
            use_container_width=True,
            help="Go back to review or modify imported data",
        ):
            set_workspace_state(WorkspaceState.IMPORT)
            st.rerun()


def create_building_3d_figure(
    df: pd.DataFrame,
    selected_beam: str | None = None,
) -> go.Figure:
    """Create impressive 3D building visualization with all beams.

    Features:
    - Real 3D beam volumes with proper orientation
    - Color by story or design status
    - Selected beam highlighted with glow effect
    - Hover details for each beam
    - Professional lighting and camera

    Args:
        df: DataFrame with beam data (beam_id, b_mm, D_mm, coordinates)
        selected_beam: Optional beam ID to highlight (bright yellow + larger)
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
    story_colors = {
        s: color_palette[i % len(color_palette)] for i, s in enumerate(stories)
    }

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
        for ex, ey, ez in [(x1, y1, z1), (x2, y2, z2)]:
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

        # Check if this beam is selected for highlighting
        is_selected = selected_beam and beam_id == selected_beam

        # Color based on selection, status, or story
        if is_selected:
            # Bright yellow highlight for selected beam
            color = "rgba(255, 215, 0, 1.0)"  # Gold
            opacity = 1.0
        else:
            status = row.get("status", "")
            if "SAFE" in str(status).upper():
                color = "rgba(46, 204, 113, 0.85)"
            elif "FAIL" in str(status).upper():
                color = "rgba(231, 76, 60, 0.85)"
            else:
                base = story_colors.get(story, "#3498db")
                r, g, b_col = int(base[1:3], 16), int(base[3:5], 16), int(base[5:7], 16)
                color = f"rgba({r}, {g}, {b_col}, 0.8)"
            # Dim non-selected beams when one is selected
            opacity = 0.4 if selected_beam else 0.9

        # Concise hover info - just beam name, utilization, pass/fail
        util_pct = row.get("utilization", 0) * 100
        status = row.get("status", "")
        status_icon = (
            "✅"
            if "SAFE" in str(status).upper()
            else "❌"
            if "FAIL" in str(status).upper()
            else "⏳"
        )
        selected_label = "★ SELECTED " if is_selected else ""
        hover = (
            f"<b>{selected_label}{beam_id}</b> {status_icon}<br>Util: {util_pct:.0f}%"
        )

        fig.add_trace(
            go.Mesh3d(
                x=x_mesh,
                y=y_mesh,
                z=z_mesh,
                i=i_faces,
                j=j_faces,
                k=k_faces,
                color=color,
                opacity=opacity,
                flatshading=True,
                lighting=dict(
                    ambient=0.7 if is_selected else 0.6,
                    diffuse=0.9 if is_selected else 0.8,
                    specular=0.6 if is_selected else 0.4,
                    roughness=0.2 if is_selected else 0.3,
                ),
                lightposition=dict(x=100, y=200, z=300),
                hovertemplate=hover + "<extra></extra>",
                name=beam_id,
                showlegend=False,
            )
        )

    # Add story legend
    for story in stories:
        base = story_colors[story]
        fig.add_trace(
            go.Scatter3d(
                x=[None],
                y=[None],
                z=[None],
                mode="markers",
                marker=dict(size=10, color=base, symbol="square"),
                name=f"📍 {story}",
            )
        )

    # Calculate scene range
    if all_x and all_y and all_z:
        x_range = [min(all_x) - 2, max(all_x) + 2]
        y_range = [min(all_y) - 2, max(all_y) + 2]
        z_range = [min(all_z) - 1, max(all_z) + 3]
    else:
        x_range = y_range = z_range = [0, 10]

    fig.update_layout(
        scene=dict(
            xaxis=dict(
                range=x_range,
                title="X (m)",
                showgrid=True,
                gridcolor="rgba(255,255,255,0.1)",
            ),
            yaxis=dict(
                range=y_range,
                title="Y (m)",
                showgrid=True,
                gridcolor="rgba(255,255,255,0.1)",
            ),
            zaxis=dict(
                range=z_range,
                title="Z (m)",
                showgrid=True,
                gridcolor="rgba(255,255,255,0.1)",
            ),
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
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(30, 30, 40, 0.8)",
        ),
    )

    return fig


def render_building_3d() -> None:
    """Render impressive full building 3D view."""
    # Get design results for status, but use beams_df for coordinates
    results_df = st.session_state.ws_design_results
    beams_df = st.session_state.ws_beams_df

    if beams_df is None or beams_df.empty:
        st.warning("No beam data to visualize. Load data first.")
        if st.button("← Back"):
            set_workspace_state(WorkspaceState.WELCOME)
            st.rerun()
        return

    # Merge status from results into beams data if available
    df = beams_df.copy()
    if results_df is not None and not results_df.empty:
        # Add status and utilization from design results
        status_map = dict(zip(results_df["beam_id"], results_df["status"]))
        util_map = dict(zip(results_df["beam_id"], results_df["utilization"]))
        df["status"] = df["beam_id"].map(status_map).fillna("⏳ Pending")
        df["utilization"] = df["beam_id"].map(util_map).fillna(0)
    else:
        df["status"] = "⏳ Pending"
        df["utilization"] = 0

    # Compact header with stats inline
    total = len(df)
    stories = df["story"].nunique()
    safe_count = (
        len(df[df["status"].str.contains("OK|SAFE", case=False, na=False)])
        if "status" in df.columns
        else 0
    )
    pass_rate = f"{safe_count / total * 100:.0f}%" if total > 0 else "N/A"

    st.markdown(
        f"### 🏗️ Building 3D — {total} beams, {stories} stories, {pass_rate} pass"
    )

    # Beam selection UI with highlighting
    beam_ids = df["beam_id"].tolist() if len(df) > 0 else []
    select_col, info_col = st.columns([2, 3])
    with select_col:
        highlighted_beam = st.selectbox(
            "🎯 Highlight beam:",
            ["None (show all)"] + beam_ids,
            key="bldg_highlight_select",
            help="Select a beam to highlight it in the 3D view",
        )
        selected_beam = (
            None if highlighted_beam == "None (show all)" else highlighted_beam
        )

    with info_col:
        if selected_beam and selected_beam in df["beam_id"].values:
            beam_row = df[df["beam_id"] == selected_beam].iloc[0]
            status = beam_row.get("status", "N/A")
            util = beam_row.get("utilization", 0)
            dims = f"{beam_row['b_mm']:.0f}×{beam_row['D_mm']:.0f}"
            st.info(
                f"**{selected_beam}** | {dims}mm | Util: {util * 100:.0f}% | {status}"
            )

    # Create 3D figure with highlighting
    fig = create_building_3d_figure(df, selected_beam=selected_beam)
    fig.update_layout(height=550)
    st.plotly_chart(fig, use_container_width=True, key="ws_building_3d")

    # Compact controls in single row
    c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
    with c1:
        if st.button("← Back", key="bldg_back"):
            # Go back to design if results exist, else import
            if results_df is not None:
                set_workspace_state(WorkspaceState.DESIGN)
            else:
                set_workspace_state(WorkspaceState.IMPORT)
            st.rerun()
    with c2:
        if beam_ids and selected_beam:
            if st.button(f"🔍 View {selected_beam} Details", key="view_selected_beam"):
                st.session_state.ws_selected_beam = selected_beam
                set_workspace_state(WorkspaceState.VIEW_3D)
                st.rerun()
    with c3:
        if st.button("📊 Dashboard", key="bldg_dash"):
            set_workspace_state(WorkspaceState.DASHBOARD)
            st.rerun()
    with c4:
        st.caption("Drag to rotate")
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
    st.markdown(
        f"**Section:** {b_mm:.0f}×{D_mm:.0f} mm | **Span:** {span_mm / 1000:.1f} m | **Mu:** {mu_knm:.1f} kN·m | **Vu:** {vu_kn:.1f} kN"
    )

    # Initialize rebar config from session state or defaults
    config = st.session_state.ws_rebar_config
    if config is None or config.get("beam_id") != beam_id:
        # Initialize with design suggestion
        ast_req = float(row.get("ast_req", 500))
        suggested = calculate_rebar_layout(
            ast_req, b_mm, D_mm, span_mm, vu_kn, cover_mm
        )
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

    # Use version counter in keys to force refresh on optimize
    re_version = config.get("_version", 0)
    re_key_prefix = f"re_{beam_id}_{re_version}"

    with col1:
        st.markdown("##### Bottom Reinforcement")
        c1, c2 = st.columns(2)
        with c1:
            l1_dia = st.selectbox(
                "Layer 1 Dia (mm)",
                [10, 12, 16, 20, 25, 32],
                index=[10, 12, 16, 20, 25, 32].index(config["bottom_layer1_dia"]),
                key=f"{re_key_prefix}_l1_dia",
            )
            l2_dia = st.selectbox(
                "Layer 2 Dia (mm)",
                [0, 10, 12, 16, 20, 25, 32],
                index=[0, 10, 12, 16, 20, 25, 32].index(
                    config.get("bottom_layer2_dia", 0)
                ),
                key=f"{re_key_prefix}_l2_dia",
            )
        with c2:
            l1_count = st.number_input(
                "Count",
                2,
                8,
                config["bottom_layer1_count"],
                key=f"{re_key_prefix}_l1_cnt",
            )
            l2_count = st.number_input(
                "Count",
                0,
                6,
                config.get("bottom_layer2_count", 0),
                key=f"{re_key_prefix}_l2_cnt",
            )

        st.markdown("##### Top Reinforcement")
        c1, c2 = st.columns(2)
        with c1:
            top_dia = st.selectbox(
                "Dia (mm)",
                [10, 12, 16, 20],
                index=[10, 12, 16, 20].index(config.get("top_dia", 12)),
                key=f"{re_key_prefix}_top_dia",
            )
        with c2:
            top_count = st.number_input(
                "Count",
                2,
                6,
                config.get("top_count", 2),
                key=f"{re_key_prefix}_top_cnt",
            )

        st.markdown("##### Stirrups")
        c1, c2 = st.columns(2)
        with c1:
            stir_dia = st.selectbox(
                "Dia (mm)",
                [6, 8, 10, 12],
                index=[6, 8, 10, 12].index(config.get("stirrup_dia", 8)),
                key=f"{re_key_prefix}_stir_dia",
            )
        with c2:
            stir_spacing = st.number_input(
                "Spacing (mm)",
                75,
                300,
                config.get("stirrup_spacing", 150),
                step=25,
                key=f"{re_key_prefix}_stir_sp",
            )

    # Update config
    config.update(
        {
            "bottom_layer1_dia": l1_dia,
            "bottom_layer1_count": l1_count,
            "bottom_layer2_dia": l2_dia,
            "bottom_layer2_count": l2_count,
            "top_dia": top_dia,
            "top_count": top_count,
            "stirrup_dia": stir_dia,
            "stirrup_spacing": stir_spacing,
        }
    )
    st.session_state.ws_rebar_config = config

    # Build bar lists
    bottom_bars = [(l1_dia, l1_count)]
    if l2_dia > 0 and l2_count > 0:
        bottom_bars.append((l2_dia, l2_count))
    top_bars = [(top_dia, top_count)]

    # Calculate checks
    checks = calculate_rebar_checks(
        b_mm,
        D_mm,
        mu_knm,
        vu_kn,
        fck,
        fy,
        cover_mm,
        bottom_bars,
        top_bars,
        stir_dia,
        stir_spacing,
    )

    with col2:
        st.markdown("##### Design Checks")

        # Flexure
        flex_color = "🟢" if checks["flexure_ok"] else "🔴"
        st.markdown(
            f"{flex_color} **Flexure:** {checks['flexure_util'] * 100:.1f}% (Mu = {checks['mu_capacity_knm']:.1f} kN·m)"
        )

        # Shear
        shear_color = "🟢" if checks["shear_ok"] else "🔴"
        st.markdown(
            f"{shear_color} **Shear:** {checks['shear_util'] * 100:.1f}% (Vu = {checks['vu_capacity_kn']:.1f} kN)"
        )

        # Min reinforcement
        min_color = "🟢" if checks["min_reinf_ok"] else "🔴"
        st.markdown(
            f"{min_color} **Min Ast:** {checks['ast_provided']:.0f} ≥ {checks['ast_min']:.0f} mm²"
        )

        # Max reinforcement
        max_color = "🟢" if checks["max_reinf_ok"] else "🔴"
        st.markdown(
            f"{max_color} **Max Ast:** {checks['ast_provided']:.0f} ≤ {checks['ast_max']:.0f} mm²"
        )

        # Spacing
        sp_color = "🟢" if checks["spacing_ok"] else "🔴"
        st.markdown(f"{sp_color} **Bar Spacing:** {checks['bar_spacing']:.0f} mm")

        st.divider()

        # Overall status with big indicator
        if checks["all_ok"]:
            st.success(f"### {checks['status']}")
            st.caption(
                f"Ast provided: {checks['ast_provided']:.0f} mm² | d_eff: {checks['d_eff']:.0f} mm"
            )
        else:
            st.error(f"### {checks['status']}")
            st.caption("Adjust reinforcement to satisfy all checks")

        # Constructability rating
        st.divider()
        constructability = calculate_constructability_score(
            bottom_bars, top_bars, stir_spacing, b_mm
        )
        const_icon = (
            "🟢"
            if constructability["score"] >= 80
            else ("🟡" if constructability["score"] >= 60 else "🔴")
        )
        st.markdown(
            f"##### {const_icon} Construction Ease: {constructability['score']}/100"
        )
        st.caption(constructability["summary"])

        # Quick optimization button
        if st.button(
            "⚡ Auto-Optimize",
            use_container_width=True,
            help="Optimize for cost while maintaining safety",
        ):
            optimized = suggest_optimal_rebar(
                b_mm, D_mm, mu_knm, vu_kn, fck, fy, cover_mm
            )
            if optimized:
                # Preserve top bars and stirrups, only optimize bottom
                optimized["top_dia"] = config.get("top_dia", 12)
                optimized["top_count"] = config.get("top_count", 2)
                optimized["stirrup_dia"] = config.get("stirrup_dia", 8)
                optimized["stirrup_spacing"] = config.get("stirrup_spacing", 150)
                optimized["beam_id"] = beam_id
                # Increment version to force widget refresh (new keys)
                optimized["_version"] = config.get("_version", 0) + 1
                st.session_state.ws_rebar_config = optimized

                # NOTE: Don't modify widget keys directly - that causes
                # StreamlitAPIException. The rerun will use the new config.
                st.toast("✅ Optimized rebar configuration applied!")
                st.rerun()
            else:
                st.warning("Could not find better configuration")

    # Live cross-section preview (updates as user edits)
    st.divider()
    st.markdown("##### 📐 Live Cross-Section Preview")

    if VISUALIZATION_AVAILABLE:
        # Use shared bar position calculator (Session 32 fix - uses actual stirrup_dia)
        bottom_bars_vis, top_bars_vis = calculate_bar_positions(
            b_mm=b_mm,
            D_mm=D_mm,
            cover_mm=cover_mm,
            stirrup_dia=stir_dia,  # Uses actual stirrup diameter, not hardcoded 8
            l1_count=l1_count,
            l1_dia=l1_dia,
            l2_count=l2_count,
            l2_dia=l2_dia,
            top_count=top_count,
            top_dia=top_dia,
        )

        # Create and display cross-section figure
        fig = create_cross_section_figure(
            b=b_mm,
            D=D_mm,
            cover=cover_mm,
            bottom_bars=bottom_bars_vis,
            top_bars=top_bars_vis,
            stirrup_dia=stir_dia,
            rebar_config=config,
        )
        st.plotly_chart(fig, use_container_width=True, key="rebar_editor_cross_section")
    else:
        # Fallback text display
        st.info(
            f"Section: {b_mm:.0f}×{D_mm:.0f} mm | Bottom: {l1_count}Φ{l1_dia} + {l2_count}Φ{l2_dia} | Top: {top_count}Φ{top_dia}"
        )

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


def create_cross_section_figure(
    b: float,
    D: float,
    cover: float,
    bottom_bars: list[tuple[float, float, float]],
    top_bars: list[tuple[float, float, float]],
    stirrup_dia: float = 8,
    rebar_config: dict | None = None,
) -> go.Figure:
    """Create professional cross-section 2D view using Plotly.

    Args:
        b: Beam width in mm
        D: Beam depth in mm
        cover: Clear cover in mm
        bottom_bars: List of (x, y, dia) for bottom reinforcement
        top_bars: List of (x, y, dia) for top reinforcement
        stirrup_dia: Stirrup diameter in mm
        rebar_config: Optional config from rebar editor

    Returns:
        Plotly figure showing cross-section
    """
    fig = go.Figure()

    # Colors for professional look
    concrete_color = "#e8e4e0"
    stirrup_color = "#666666"
    main_bar_color = "#1a5276"
    top_bar_color = "#28b463"

    # Concrete outline (filled rectangle)
    fig.add_shape(
        type="rect",
        x0=0,
        y0=0,
        x1=b,
        y1=D,
        line=dict(color="#333", width=2),
        fillcolor=concrete_color,
        layer="below",
    )

    # Stirrup (inner rectangle)
    stirrup_offset = cover + stirrup_dia / 2
    fig.add_shape(
        type="rect",
        x0=stirrup_offset,
        y0=stirrup_offset,
        x1=b - stirrup_offset,
        y1=D - stirrup_offset,
        line=dict(color=stirrup_color, width=3),
        fillcolor="rgba(0,0,0,0)",
    )

    # Draw bottom bars
    for bx, by, dia in bottom_bars:
        fig.add_trace(
            go.Scatter(
                x=[bx],
                y=[by],
                mode="markers",
                marker=dict(
                    size=max(10, dia * 0.6),
                    color=main_bar_color,
                    line=dict(color="#000", width=1),
                ),
                name=f"Bottom Bar Φ{dia:.0f}",
                hovertemplate=f"Bottom Bar<br>Φ{dia:.0f}mm<br>x: {bx:.1f}, y: {by:.1f}<extra></extra>",
                showlegend=False,
            )
        )

    # Draw top bars
    for tx, ty, dia in top_bars:
        fig.add_trace(
            go.Scatter(
                x=[tx],
                y=[ty],
                mode="markers",
                marker=dict(
                    size=max(10, dia * 0.6),
                    color=top_bar_color,
                    line=dict(color="#000", width=1),
                ),
                name=f"Top Bar Φ{dia:.0f}",
                hovertemplate=f"Top Bar<br>Φ{dia:.0f}mm<br>x: {tx:.1f}, y: {ty:.1f}<extra></extra>",
                showlegend=False,
            )
        )

    # Dimension lines and annotations
    # Width dimension
    fig.add_annotation(
        x=b / 2,
        y=-30,
        text=f"b = {b:.0f} mm",
        showarrow=False,
        font=dict(size=12, color="#333"),
    )
    fig.add_shape(
        type="line",
        x0=0,
        y0=-15,
        x1=b,
        y1=-15,
        line=dict(color="#666", width=1),
    )
    fig.add_shape(
        type="line", x0=0, y0=-5, x1=0, y1=-25, line=dict(color="#666", width=1)
    )
    fig.add_shape(
        type="line", x0=b, y0=-5, x1=b, y1=-25, line=dict(color="#666", width=1)
    )

    # Depth dimension
    fig.add_annotation(
        x=b + 40,
        y=D / 2,
        text=f"D = {D:.0f} mm",
        showarrow=False,
        font=dict(size=12, color="#333"),
        textangle=-90,
    )
    fig.add_shape(
        type="line",
        x0=b + 15,
        y0=0,
        x1=b + 15,
        y1=D,
        line=dict(color="#666", width=1),
    )
    fig.add_shape(
        type="line", x0=b + 5, y0=0, x1=b + 25, y1=0, line=dict(color="#666", width=1)
    )
    fig.add_shape(
        type="line", x0=b + 5, y0=D, x1=b + 25, y1=D, line=dict(color="#666", width=1)
    )

    # Cover annotation
    fig.add_annotation(
        x=cover / 2,
        y=cover / 2,
        text=f"{cover:.0f}",
        showarrow=False,
        font=dict(size=9, color="#888"),
    )

    # Legend/key
    legend_items = [
        (b + 60, D - 30, main_bar_color, "Bottom Bars"),
        (b + 60, D - 60, top_bar_color, "Top Bars"),
        (b + 60, D - 90, stirrup_color, "Stirrups"),
    ]
    for lx, ly, color, text in legend_items:
        fig.add_trace(
            go.Scatter(
                x=[lx],
                y=[ly],
                mode="markers+text",
                marker=dict(size=10, color=color),
                text=[f"  {text}"],
                textposition="middle right",
                showlegend=False,
                hoverinfo="skip",
            )
        )

    # Layout
    fig.update_layout(
        title=dict(
            text="Beam Cross-Section",
            font=dict(size=16, color="#333"),
            x=0.5,
        ),
        xaxis=dict(
            scaleanchor="y",
            scaleratio=1,
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-50, b + 120],
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-60, D + 30],
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=50, b=20),
        height=400,
    )

    return fig


def render_cross_section() -> None:
    """Render beautiful 2D cross-section view for selected beam."""
    beam_id = st.session_state.ws_selected_beam
    df = st.session_state.ws_design_results

    st.markdown(f"### 📐 Cross-Section: {beam_id}")

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
    b = row["b_mm"]
    D = row["D_mm"]
    cover = row.get("cover_mm", 40)

    # Get rebar layout
    rebar = calculate_rebar_layout(
        ast_mm2=row["ast_req"],
        b_mm=b,
        D_mm=D,
        span_mm=row["span_mm"],
        vu_kn=row["vu_kn"],
        cover_mm=cover,
    )

    # Check for custom config from rebar editor
    rebar_config = st.session_state.get("ws_rebar_config")

    # Calculate bar positions for cross-section
    bottom_bars = []
    top_bars = []

    if rebar_config:
        # Use custom rebar configuration
        bottom_dia_1 = rebar_config.get("bottom_dia_1", 16)
        bottom_count_1 = rebar_config.get("bottom_count_1", 3)
        bottom_dia_2 = rebar_config.get("bottom_dia_2", 0)
        bottom_count_2 = rebar_config.get("bottom_count_2", 0)
        top_dia = rebar_config.get("top_dia", 12)
        top_count = rebar_config.get("top_count", 2)
    else:
        # Use calculated values
        bottom_dia_1 = rebar.get("bar_diameter", 16)
        n_bars = len(rebar["bottom_bars"])
        bottom_count_1 = min(n_bars, 4)
        bottom_count_2 = max(0, n_bars - 4)
        bottom_dia_2 = bottom_dia_1 if bottom_count_2 > 0 else 0
        top_dia = 12
        top_count = len(rebar["top_bars"])

    # Calculate bottom layer 1 positions
    stirrup_dia = 8
    layer1_y = cover + stirrup_dia + bottom_dia_1 / 2  # stirrup + half bar dia
    # Available width for bar centers (inside stirrups, accounting for bar radius on both sides)
    x_start = cover + stirrup_dia + bottom_dia_1 / 2  # First bar center position
    x_end = b - cover - stirrup_dia - bottom_dia_1 / 2  # Last bar center position
    available_width_for_spacing = x_end - x_start
    if bottom_count_1 > 1:
        spacing_1 = available_width_for_spacing / (bottom_count_1 - 1)
    else:
        spacing_1 = 0
    for i in range(bottom_count_1):
        bx = x_start + i * spacing_1 if bottom_count_1 > 1 else b / 2
        bottom_bars.append((bx, layer1_y, bottom_dia_1))

    # Calculate bottom layer 2 positions (if any)
    if bottom_count_2 > 0 and bottom_dia_2 > 0:
        layer2_y = (
            layer1_y + bottom_dia_1 / 2 + 25 + bottom_dia_2 / 2
        )  # vertical spacing
        x_start_2 = cover + stirrup_dia + bottom_dia_2 / 2
        x_end_2 = b - cover - stirrup_dia - bottom_dia_2 / 2
        available_width_2 = x_end_2 - x_start_2
        if bottom_count_2 > 1:
            spacing_2 = available_width_2 / (bottom_count_2 - 1)
        else:
            spacing_2 = 0
        for i in range(bottom_count_2):
            bx = x_start_2 + i * spacing_2 if bottom_count_2 > 1 else b / 2
            bottom_bars.append((bx, layer2_y, bottom_dia_2))

    # Calculate top bar positions
    top_y = D - cover - stirrup_dia - top_dia / 2
    x_start_top = cover + stirrup_dia + top_dia / 2
    x_end_top = b - cover - stirrup_dia - top_dia / 2
    available_width_top = x_end_top - x_start_top
    if top_count > 1:
        spacing_top = available_width_top / (top_count - 1)
    else:
        spacing_top = 0
    for i in range(top_count):
        tx = x_start_top + i * spacing_top if top_count > 1 else b / 2
        top_bars.append((tx, top_y, top_dia))

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Section", f"{b:.0f} × {D:.0f}")
    col2.metric("Cover", f"{cover:.0f} mm")

    # Calculate total Ast
    total_ast = sum(3.14159 * (d / 2) ** 2 for _, _, d in bottom_bars)
    col3.metric("Ast Provided", f"{total_ast:.0f} mm²")

    utilization = (row["ast_req"] / total_ast * 100) if total_ast > 0 else 0
    col4.metric("Utilization", f"{utilization:.0f}%")

    # Create and display cross-section
    if VISUALIZATION_AVAILABLE:
        fig = create_cross_section_figure(
            b=b,
            D=D,
            cover=cover,
            bottom_bars=bottom_bars,
            top_bars=top_bars,
            stirrup_dia=8,
            rebar_config=rebar_config,
        )
        st.plotly_chart(fig, use_container_width=True, key="cross_section_fig")
    else:
        st.warning("Plotly not available for visualization")
        st.write(f"Section: {b}×{D} mm")
        st.write(f"Bottom bars: {len(bottom_bars)}")
        st.write(f"Top bars: {len(top_bars)}")

    # Rebar schedule table
    st.markdown("#### 📋 Rebar Schedule")
    schedule_data = {
        "Location": ["Bottom Layer 1", "Bottom Layer 2", "Top Bars"],
        "Bars": [
            f"{bottom_count_1}Φ{bottom_dia_1}",
            f"{bottom_count_2}Φ{bottom_dia_2}" if bottom_count_2 > 0 else "-",
            f"{top_count}Φ{top_dia}",
        ],
        "Ast (mm²)": [
            f"{bottom_count_1 * 3.14159 * (bottom_dia_1 / 2) ** 2:.0f}",
            (
                f"{bottom_count_2 * 3.14159 * (bottom_dia_2 / 2) ** 2:.0f}"
                if bottom_count_2 > 0
                else "-"
            ),
            f"{top_count * 3.14159 * (top_dia / 2) ** 2:.0f}",
        ],
    }
    st.dataframe(schedule_data, hide_index=True, use_container_width=True)

    # Navigation
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("← Back to 3D"):
            set_workspace_state(WorkspaceState.VIEW_3D)
            st.rerun()
    with c2:
        if st.button("🔧 Edit Rebar"):
            set_workspace_state(WorkspaceState.REBAR_EDIT)
            st.rerun()
    with c3:
        if st.button("🏗️ Building"):
            set_workspace_state(WorkspaceState.BUILDING_3D)
            st.rerun()
    with c4:
        if st.button("📊 Results"):
            set_workspace_state(WorkspaceState.DESIGN)
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
    col2.metric("Span", f"{row['span_mm'] / 1000:.1f} m")
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

    # Navigation - compact 5-button row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("← Results", use_container_width=True):
            set_workspace_state(WorkspaceState.DESIGN)
            st.rerun()
    with col2:
        if st.button("📐 Section", use_container_width=True):
            set_workspace_state(WorkspaceState.CROSS_SECTION)
            st.rerun()
    with col3:
        if st.button("🔧 Edit Rebar", use_container_width=True, type="primary"):
            set_workspace_state(WorkspaceState.REBAR_EDIT)
            st.rerun()
    with col4:
        if st.button("🏗️ Building", use_container_width=True):
            set_workspace_state(WorkspaceState.BUILDING_3D)
            st.rerun()
    with col5:
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
    def safe_float(val: Any, default: float) -> float:
        try:
            return float(val) if val is not None and not pd.isna(val) else default
        except (ValueError, TypeError):
            return default

    col1, col2 = st.columns([0.4, 0.6])

    with col1:
        st.markdown("**Geometry**")
        b = st.number_input(
            "Width b (mm)",
            value=safe_float(row.get("b_mm"), 300.0),
            step=25.0,
            key="edit_b",
        )
        D = st.number_input(
            "Depth D (mm)",
            value=safe_float(row.get("D_mm"), 500.0),
            step=25.0,
            key="edit_D",
        )
        span = st.number_input(
            "Span (mm)",
            value=safe_float(row.get("span_mm"), 5000.0),
            step=100.0,
            key="edit_span",
        )

        st.markdown("**Loading**")
        mu = st.number_input(
            "Moment Mu (kN·m)",
            value=safe_float(row.get("mu_knm"), 100.0),
            step=10.0,
            key="edit_mu",
        )
        vu = st.number_input(
            "Shear Vu (kN)",
            value=safe_float(row.get("vu_kn"), 50.0),
            step=5.0,
            key="edit_vu",
        )

        st.markdown("**Materials**")
        fck = st.selectbox("Concrete", [20, 25, 30, 35, 40], index=1, key="edit_fck")
        fy = st.selectbox("Steel", [415, 500, 550], index=1, key="edit_fy")

        if st.button("💫 Redesign", type="primary", use_container_width=True):
            # Update dataframe
            idx = df[df["beam_id"] == row["beam_id"]].index
            if len(idx) > 0:
                df.loc[
                    idx[0], ["b_mm", "D_mm", "span_mm", "mu_knm", "vu_kn", "fck", "fy"]
                ] = [b, D, span, mu, vu, fck, fy]
                st.session_state.ws_beams_df = df
                st.session_state.ws_design_results = design_all_beams_ws()
                st.success("✅ Redesigned!")
                st.rerun()

    with col2:
        # Live preview with current values
        updated_row = pd.Series(
            {
                "b_mm": b,
                "D_mm": D,
                "span_mm": span,
                "mu_knm": mu,
                "vu_kn": vu,
                "fck": fck,
                "fy": fy,
                "cover_mm": row.get("cover_mm", 40),
            }
        )
        design = design_beam_row(updated_row)

        st.metric("Status", design["status"])
        st.metric("Ast Required", f"{design['ast_req']:.0f} mm²")
        st.metric("Utilization", f"{design['utilization'] * 100:.1f}%")

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
                    b=b,
                    D=D,
                    span=span,
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
    """Render SmartDesigner dashboard with material takeoff."""
    st.markdown("### 📊 Smart Dashboard")

    df = st.session_state.ws_design_results

    if df is None or df.empty:
        st.info("Design beams first to see dashboard")
        if st.button("← Back to Import"):
            set_workspace_state(WorkspaceState.IMPORT)
            st.rerun()
        return

    # Summary stats row
    total = len(df)
    passed = len(df[df["is_safe"]])
    avg_util = df["utilization"].mean() * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Beams", total)
    c2.metric("Pass Rate", f"{100 * passed / max(total, 1):.0f}%")
    c3.metric("Avg Util", f"{avg_util:.0f}%")
    c4.metric(
        "Failed",
        total - passed,
        delta=f"-{total - passed}" if total > passed else None,
        delta_color="inverse",
    )

    st.divider()

    # Tabs for different insights
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📈 Analysis", "📦 Material Takeoff", "💰 Cost Estimate", "📥 Export"]
    )

    with tab1:
        # Utilization distribution
        st.markdown("##### Utilization Distribution")
        low = len(df[df["utilization"] < 0.6])
        optimal = len(df[(df["utilization"] >= 0.6) & (df["utilization"] <= 0.85)])
        high = len(df[df["utilization"] > 0.85])

        col1, col2, col3 = st.columns(3)
        col1.metric("🟢 Under-utilized", low, help="<60% - consider reducing section")
        col2.metric("🟡 Optimal", optimal, help="60-85% - good efficiency")
        col3.metric("🔴 Near Capacity", high, help=">85% - check carefully")

        # Quick wins
        st.markdown("##### 💡 Suggestions")
        if low > total * 0.3:
            st.success(
                f"💰 {low} beams under-utilized. Reduce sections to save {low * 5:.0f}% material."
            )
        if high > 0:
            st.warning(
                f"⚠️ {high} beams near capacity. Verify under all load combinations."
            )
        if passed == total:
            st.success("✅ All beams pass design checks!")
        else:
            failed_beams = df[~df["is_safe"]]["beam_id"].tolist()[:3]
            st.error(
                f"❌ Failed: {', '.join(failed_beams)}{'...' if len(failed_beams) > 3 else ''}"
            )

    with tab2:
        # Material takeoff
        takeoff = calculate_material_takeoff(df)

        st.markdown("##### Material Quantities")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("🧱 Concrete", f"{takeoff['concrete_m3']:.1f} m³")
            st.caption("All beams combined")

        with col2:
            st.metric("🔩 Reinforcement", f"{takeoff['steel_kg']:.0f} kg")
            st.caption(f"≈ {takeoff['steel_kg'] / 1000:.2f} tonnes")

        # Steel ratio
        steel_ratio = (
            takeoff["steel_kg"] / (takeoff["concrete_m3"] * 2400) * 100
            if takeoff["concrete_m3"] > 0
            else 0
        )
        st.metric("Steel Ratio", f"{steel_ratio:.1f}%", help="kg steel per kg concrete")

        # Per-story breakdown if multiple stories
        if "story" in df.columns:
            st.markdown("##### Per-Story Breakdown")
            story_data = []
            for story in df["story"].unique():
                story_df = df[df["story"] == story]
                story_takeoff = calculate_material_takeoff(story_df)
                story_data.append(
                    {
                        "Story": story,
                        "Beams": len(story_df),
                        "Concrete (m³)": f"{story_takeoff['concrete_m3']:.1f}",
                        "Steel (kg)": f"{story_takeoff['steel_kg']:.0f}",
                    }
                )
            st.dataframe(story_data, hide_index=True, use_container_width=True)

    with tab3:
        # Cost estimate
        takeoff = calculate_material_takeoff(df)

        st.markdown("##### Cost Estimate (INR)")
        st.caption("Rates: Concrete ₹8000/m³ | Steel ₹85/kg")

        col1, col2, col3 = st.columns(3)
        col1.metric("Concrete", f"₹{takeoff['concrete_cost']:,.0f}")
        col2.metric("Steel", f"₹{takeoff['steel_cost']:,.0f}")
        col3.metric("**Total**", f"₹{takeoff['total_cost']:,.0f}")

        # Cost per meter
        total_length = df["span_mm"].sum() / 1000  # m
        cost_per_m = takeoff["total_cost"] / total_length if total_length > 0 else 0

        st.metric(
            "Cost per Running Meter",
            f"₹{cost_per_m:,.0f}/m",
            help="Total cost / total beam length",
        )

        # Visualization
        if VISUALIZATION_AVAILABLE:
            cost_data = {
                "Item": ["Concrete", "Steel"],
                "Cost (₹)": [takeoff["concrete_cost"], takeoff["steel_cost"]],
            }
            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=cost_data["Item"],
                        values=cost_data["Cost (₹)"],
                        hole=0.4,
                        marker_colors=["#2ecc71", "#3498db"],
                    )
                ]
            )
            fig.update_layout(
                height=250,
                margin=dict(l=0, r=0, t=30, b=0),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.1),
            )
            st.plotly_chart(fig, use_container_width=True, key="cost_pie")

    with tab4:
        # Export options
        st.markdown("##### Download Design Results")
        st.caption("Export your beam designs for documentation or further analysis")

        # Prepare export data with key columns
        export_cols = [
            "beam_id",
            "b_mm",
            "D_mm",
            "span_mm",
            "mu_knm",
            "vu_kn",
            "is_safe",
            "utilization",
            "ast_provided_mm2",
            "ast_required_mm2",
            "main_bars",
            "stirrup_spacing_mm",
        ]
        export_df = df[[c for c in export_cols if c in df.columns]].copy()

        # Add status column for clarity
        export_df.insert(
            0, "status", export_df["is_safe"].apply(lambda x: "PASS" if x else "FAIL")
        )

        # CSV download
        csv_data = export_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name="beam_design_results.csv",
            mime="text/csv",
            use_container_width=True,
            help="Download all beam design results as CSV file",
        )

        # Summary download
        takeoff = calculate_material_takeoff(df)
        summary_text = f"""BEAM DESIGN SUMMARY
====================
Generated by: structural_engineering_lib AI Assistant v2
Date: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}

DESIGN SUMMARY
--------------
Total Beams: {len(df)}
Passed: {len(df[df["is_safe"]])}
Failed: {len(df[~df["is_safe"]])}
Average Utilization: {df["utilization"].mean() * 100:.1f}%

MATERIAL TAKEOFF
----------------
Concrete: {takeoff["concrete_m3"]:.2f} m³
Steel: {takeoff["steel_kg"]:.0f} kg ({takeoff["steel_kg"] / 1000:.2f} tonnes)

COST ESTIMATE (INR)
-------------------
Concrete (@₹8000/m³): ₹{takeoff["concrete_cost"]:,.0f}
Steel (@₹85/kg): ₹{takeoff["steel_cost"]:,.0f}
TOTAL: ₹{takeoff["total_cost"]:,.0f}
"""
        st.download_button(
            label="📄 Download Summary",
            data=summary_text,
            file_name="beam_design_summary.txt",
            mime="text/plain",
            use_container_width=True,
            help="Download material takeoff and cost summary",
        )

        st.info(
            "💡 **Tip:** Use CSV export to import results into Excel for detailed reporting."
        )

    # Navigation
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("← Results", use_container_width=True):
            set_workspace_state(WorkspaceState.DESIGN)
            st.rerun()
    with c2:
        if st.button("🏗️ Building 3D", use_container_width=True):
            set_workspace_state(WorkspaceState.BUILDING_3D)
            st.rerun()
    with c3:
        if st.button("📥 New Import", use_container_width=True):
            set_workspace_state(WorkspaceState.IMPORT)
            st.rerun()


# =============================================================================
# UNIFIED EDITOR - Full-width design editor with integrated 3D and checks
# =============================================================================


def _get_beam_queue(df: pd.DataFrame, filter_mode: str = "all") -> list[str]:
    """Get ordered list of beams based on filter mode."""
    if df is None or df.empty:
        return []

    if filter_mode == "failed":
        filtered = df[~df["is_safe"]]
    elif filter_mode == "passed":
        filtered = df[df["is_safe"]]
    else:
        filtered = df

    return filtered["beam_id"].tolist()


def _save_current_beam_changes(
    beam_id: str, config: dict, df: pd.DataFrame
) -> pd.DataFrame:
    """Save current rebar configuration to the dataframe."""
    if config is None or df is None:
        return df

    mask = df["beam_id"] == beam_id
    if not mask.any():
        return df

    # Update rebar columns
    df.loc[mask, "bottom_bar_count"] = config.get("bottom_layer1_count", 3)
    df.loc[mask, "bottom_bar_dia"] = config.get("bottom_layer1_dia", 16)
    df.loc[mask, "top_bar_count"] = config.get("top_count", 2)
    df.loc[mask, "top_bar_dia"] = config.get("top_dia", 12)
    df.loc[mask, "stirrup_spacing"] = config.get("stirrup_spacing", 150)

    return df


def _render_smart_table_editor(df: pd.DataFrame, editor_state: dict) -> None:
    """Render Excel-like table editor with smart batch features.

    Engineer-friendly view for revisions:
    - Edit multiple beams at once like Excel
    - Group by beam-line for standardization
    - Smart "Apply to Similar" feature
    - Live status updates as you edit

    Session 33 Redesign:
    - 3D view always visible (not hidden in expander)
    - Compact toolbar saves vertical space
    - Per-row optimize button
    - Smart column widths
    - Single optimize button (removed duplicate)
    """
    # =========================================================================
    # COMPACT TOOLBAR ROW (saves vertical space)
    # =========================================================================
    tool1, tool2, tool3, tool4, tool5 = st.columns([1.2, 1.2, 1.2, 1.5, 1])
    with tool1:
        group_by = st.selectbox(
            "Group",
            ["None", "Story", "Beam Line", "Section"],
            key="ue_table_group",
            label_visibility="collapsed",
            help="Group beams for batch operations",
        )
    with tool2:
        filter_status = st.selectbox(
            "Status",
            ["All", "Failed Only", "Passed Only"],
            key="ue_table_filter",
            label_visibility="collapsed",
        )
    with tool3:
        # Floor filter for 3D sync
        stories = sorted(df["story"].unique().tolist()) if "story" in df.columns else []
        floor_options = ["All Floors"] + stories
        # Session 34: Use session state for floor filter (allows auto-sync when beam selected)
        default_floor = st.session_state.get("ue_floor_filter", "All Floors")
        if default_floor not in floor_options:
            default_floor = "All Floors"
        selected_floor = st.selectbox(
            "Floor",
            floor_options,
            index=floor_options.index(default_floor),
            key="table_3d_floor",
            label_visibility="collapsed",
        )
        # Sync back to session state
        st.session_state.ue_floor_filter = selected_floor
    with tool4:
        # Single optimize button (removed duplicate from below)
        failed_count = (
            len(df[~df.get("is_safe", True)]) if "is_safe" in df.columns else 0
        )
        btn_label = (
            f"⚡ Fix {failed_count} Failed" if failed_count > 0 else "⚡ All Optimized"
        )
        if st.button(
            btn_label,
            type="primary" if failed_count > 0 else "secondary",
            use_container_width=True,
            disabled=failed_count == 0,
        ):
            optimized_count = 0
            for idx, row in df.iterrows():
                if not row.get("is_safe", True):
                    fb = float(row.get("b_mm", 300))
                    fD = float(row.get("D_mm", 500))
                    fmu = float(row.get("mu_knm", 100))
                    fvu = float(row.get("vu_kn", 50))
                    ffck = float(row.get("fck", 25))
                    ffy = float(row.get("fy", 500))
                    fcover = float(row.get("cover_mm", 40))
                    opt = suggest_optimal_rebar(fb, fD, fmu, fvu, ffck, ffy, fcover)
                    if opt:
                        # Apply flexural reinforcement
                        df.at[idx, "bottom_bar_count"] = opt.get(
                            "bottom_layer1_count", 4
                        )
                        df.at[idx, "bottom_bar_dia"] = opt.get("bottom_layer1_dia", 16)
                        # Apply shear reinforcement (Session 33: 8/10/12mm, 100-300mm)
                        df.at[idx, "stirrup_dia"] = opt.get("stirrup_dia", 8)
                        df.at[idx, "stirrup_spacing"] = opt.get("stirrup_spacing", 150)
                        ast_prov = (
                            opt.get("bottom_layer1_count", 4)
                            * math.pi
                            * (opt.get("bottom_layer1_dia", 16) ** 2)
                            / 4
                        )
                        ast_req = float(row.get("ast_req", 500))
                        if ast_prov >= ast_req:
                            df.at[idx, "is_safe"] = True
                            util = (ast_req / ast_prov * 100) if ast_prov > 0 else 0
                            df.at[idx, "status"] = f"✅ {util:.0f}%"
                            optimized_count += 1
            st.session_state.ws_design_results = df
            st.toast(f"✅ Optimized {optimized_count} beams!")
            st.rerun()
    with tool5:
        if st.button("📊 Results", use_container_width=True):
            set_workspace_state(WorkspaceState.DESIGN)
            st.rerun()

    # =========================================================================
    # 3D VIEW (Always visible, dynamic based on selection)
    # =========================================================================
    # Get selected beam from session state (set by table interaction)
    selected_beam_id = st.session_state.get("ue_selected_beam_id", None)

    if VISUALIZATION_AVAILABLE and len(df) > 0:
        # Filter by floor if selected
        if selected_floor != "All Floors":
            view_df = df[df["story"] == selected_floor]
        else:
            view_df = df

        # Check if we should show single beam detail or building view
        if selected_beam_id and selected_beam_id in df["beam_id"].values:
            # FOCUSED VIEW: Single beam with reinforcement
            beam_row = df[df["beam_id"] == selected_beam_id].iloc[0]

            # Create beam with reinforcement using existing function
            b_mm = float(beam_row.get("b_mm", 300))
            D_mm = float(beam_row.get("D_mm", 500))
            span_mm = float(beam_row.get("span_mm", 4000))
            cover = float(beam_row.get("cover_mm", 40))
            stirrup_dia = float(beam_row.get("stirrup_dia", 8))

            # Get bar configuration
            bot_count = int(beam_row.get("bottom_bar_count", 4))
            bot_dia = float(beam_row.get("bottom_bar_dia", 16))
            top_count = int(beam_row.get("top_bar_count", 2))
            top_dia = float(beam_row.get("top_bar_dia", 12))
            stirrup_spacing = float(beam_row.get("stirrup_spacing", 150))

            # Calculate bar positions using shared geometry module
            from utils.section_geometry import calculate_bar_positions

            bottom_bars, top_bars = calculate_bar_positions(
                b_mm=b_mm,
                D_mm=D_mm,
                cover_mm=cover,
                stirrup_dia=stirrup_dia,
                bottom_layer1_count=bot_count,
                bottom_layer1_dia=bot_dia,
                bottom_layer2_count=0,
                bottom_layer2_dia=0,
                top_count=top_count,
                top_dia=top_dia,
            )

            # Convert to 3D positions (extend along span)
            bottom_3d = [(0, bar[0], bar[1]) for bar in bottom_bars]  # (x, y, z)
            top_3d = [(0, bar[0], bar[1]) for bar in top_bars]

            # Generate stirrup positions
            num_stirrups = max(int(span_mm / stirrup_spacing), 3)
            stirrup_positions = [i * stirrup_spacing for i in range(num_stirrups + 1)]

            # Create detailed beam figure
            from components.visualizations_3d import create_beam_3d_figure

            fig = create_beam_3d_figure(
                b=b_mm,
                D=D_mm,
                span=span_mm,
                bottom_bars=bottom_3d,
                top_bars=top_3d,
                bar_diameter=bot_dia,
                stirrup_positions=stirrup_positions,
                stirrup_diameter=stirrup_dia,
                cover=cover,
                height=280,
                show_legend=True,
                show_info_panel=True,
            )

            # Header for focused view
            v_col1, v_col2, v_col3, v_col4 = st.columns([2, 1.5, 1.5, 1])
            with v_col1:
                is_safe = beam_row.get("is_safe", False)
                status = "✅" if is_safe else "❌"
                st.markdown(
                    f"**{status} {selected_beam_id}** — {int(b_mm)}×{int(D_mm)} | {bot_count}Φ{int(bot_dia)}"
                )
            with v_col2:
                if st.button(
                    "⚡ Optimize This", key="opt_single", use_container_width=True
                ):
                    # Optimize just this beam
                    fb, fD = (
                        float(beam_row.get("b_mm", 300)),
                        float(beam_row.get("D_mm", 500)),
                    )
                    fmu, fvu = (
                        float(beam_row.get("mu_knm", 100)),
                        float(beam_row.get("vu_kn", 50)),
                    )
                    ffck, ffy = (
                        float(beam_row.get("fck", 25)),
                        float(beam_row.get("fy", 500)),
                    )
                    fcover = float(beam_row.get("cover_mm", 40))
                    opt = suggest_optimal_rebar(fb, fD, fmu, fvu, ffck, ffy, fcover)
                    if opt:
                        mask = df["beam_id"] == selected_beam_id
                        # Apply flexural reinforcement
                        df.loc[mask, "bottom_bar_count"] = opt.get(
                            "bottom_layer1_count", 4
                        )
                        df.loc[mask, "bottom_bar_dia"] = opt.get(
                            "bottom_layer1_dia", 16
                        )
                        # Apply shear reinforcement (Session 33: 8/10/12mm, 100-300mm)
                        df.loc[mask, "stirrup_dia"] = opt.get("stirrup_dia", 8)
                        df.loc[mask, "stirrup_spacing"] = opt.get(
                            "stirrup_spacing", 150
                        )
                        ast_prov = (
                            opt.get("bottom_layer1_count", 4)
                            * math.pi
                            * (opt.get("bottom_layer1_dia", 16) ** 2)
                            / 4
                        )
                        ast_req = float(beam_row.get("ast_req", 500))
                        df.loc[mask, "is_safe"] = ast_prov >= ast_req
                        util = (ast_req / ast_prov * 100) if ast_prov > 0 else 0
                        df.loc[mask, "status"] = (
                            f"✅ {util:.0f}%"
                            if ast_prov >= ast_req
                            else f"❌ {util:.0f}%"
                        )
                        st.session_state.ws_design_results = df
                        st.toast(f"✅ Optimized {selected_beam_id}")
                        st.rerun()
            with v_col3:
                # Find next failed beam
                failed_beams = (
                    df[~df.get("is_safe", True)]["beam_id"].tolist()
                    if "is_safe" in df.columns
                    else []
                )
                if failed_beams:
                    if st.button(
                        f"→ Next Failed ({len(failed_beams)})",
                        key="next_failed",
                        use_container_width=True,
                    ):
                        # Find next failed after current, or first if at end
                        try:
                            current_idx = failed_beams.index(selected_beam_id)
                            next_idx = (current_idx + 1) % len(failed_beams)
                        except ValueError:
                            next_idx = 0
                        st.session_state.ue_selected_beam_id = failed_beams[next_idx]
                        st.rerun()
            with v_col4:
                if st.button("← Floor", key="back_to_floor", use_container_width=True):
                    st.session_state.ue_selected_beam_id = None
                    st.rerun()

            st.plotly_chart(fig, use_container_width=True, key="focused_beam_3d")
        else:
            # BUILDING VIEW: Use the same proven create_building_3d_figure as "3D Building" button
            # Session 34: Simplified to reuse working implementation
            fig = create_building_3d_figure(view_df, selected_beam=None)
            fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True, key="table_3d_view")
    else:
        st.caption("💡 Load data with coordinates to see 3D view")

    # Initialize rebar columns in MAIN df (not just filtered) - fixes beam line grouping bug
    # Session 32: Adding columns to df ensures they persist across grouping changes
    # Session 33: ALSO recalculate is_safe and status based on new rebar values
    rebar_init_needed = "bottom_bar_count" not in df.columns
    if rebar_init_needed:
        # Smart defaults based on ast_req + recalculate status
        for idx, row in df.iterrows():
            ast_req = float(row.get("ast_req", 500))
            # Estimate bar count/dia based on ast_req
            # Default: 4Φ16 = 804 mm² - good for ~500-800 mm² requirement
            if ast_req > 1200:
                bar_count, bar_dia = 4, 20
            elif ast_req > 800:
                bar_count, bar_dia = 4, 16
            else:
                bar_count, bar_dia = 3, 16

            df.at[idx, "bottom_bar_count"] = bar_count
            df.at[idx, "bottom_bar_dia"] = bar_dia

            # Session 33 FIX: Recalculate is_safe based on actual rebar provided
            ast_prov = bar_count * math.pi * (bar_dia**2) / 4
            is_safe = ast_prov >= ast_req
            util = (ast_req / ast_prov * 100) if ast_prov > 0 else 999

            df.at[idx, "is_safe"] = is_safe
            if is_safe:
                df.at[idx, "status"] = f"✅ {util:.0f}%"
            else:
                shortfall = ast_req - ast_prov
                df.at[idx, "status"] = f"❌ +{shortfall:.0f}mm²"

        df["top_bar_count"] = 2
        df["top_bar_dia"] = 12
        df["stirrup_spacing"] = 150
        df["stirrup_dia"] = 8
        st.session_state.ws_design_results = df

    # Ensure stirrup_dia column exists (may be missing from older data)
    if "stirrup_dia" not in df.columns:
        df["stirrup_dia"] = 8
        st.session_state.ws_design_results = df

    # Apply floor filter (synced with 3D view)
    if selected_floor != "All Floors":
        filtered_df = df[df["story"] == selected_floor].copy()
    else:
        filtered_df = df.copy()

    # Apply status filter
    if filter_status == "Failed Only":
        filtered_df = filtered_df[~filtered_df["is_safe"]]
    elif filter_status == "Passed Only":
        filtered_df = filtered_df[filtered_df["is_safe"]]

    # Extract beam line from beam_id (e.g., "B1" from "B1-1F" or "FB1" from "FB1-2F")
    def get_beam_line(beam_id: str) -> str:
        import re

        match = re.match(r"^([A-Za-z]+\d+)", str(beam_id))
        return match.group(1) if match else beam_id

    filtered_df["_beam_line"] = filtered_df["beam_id"].apply(get_beam_line)
    filtered_df["_section"] = (
        filtered_df["b_mm"].astype(str) + "x" + filtered_df["D_mm"].astype(str)
    )

    # Prepare editable columns
    edit_cols = ["beam_id", "story", "b_mm", "D_mm", "mu_knm", "vu_kn"]

    # Ensure integer types for rebar columns FIRST (before utilization calc)
    for col in [
        "bottom_bar_count",
        "bottom_bar_dia",
        "top_bar_count",
        "top_bar_dia",
        "stirrup_spacing",
        "stirrup_dia",
    ]:
        if col in filtered_df.columns:
            filtered_df[col] = (
                filtered_df[col]
                .fillna(
                    4
                    if "count" in col
                    else 16
                    if "bar_dia" in col
                    else 8
                    if col == "stirrup_dia"
                    else 150
                )
                .astype(int)
            )

    # Calculate utilization for each beam (Ast provided / Ast required * 100)
    # Must happen AFTER column cleanup to avoid NaN conversion errors
    def calc_util(row: Any) -> float:
        ast_req = float(row.get("ast_req", 500))
        if ast_req <= 0:
            return 100.0
        bar_count = int(row.get("bottom_bar_count", 4))
        bar_dia = float(row.get("bottom_bar_dia", 16))
        ast_prov = bar_count * math.pi * (bar_dia**2) / 4
        return (ast_req / ast_prov) * 100 if ast_prov > 0 else 999.0

    filtered_df["_utilization"] = filtered_df.apply(calc_util, axis=1)

    edit_cols += [
        "bottom_bar_count",
        "bottom_bar_dia",
        "top_bar_count",
        "top_bar_dia",
        "stirrup_dia",
        "stirrup_spacing",
        "_utilization",
        "status",
    ]

    # Group display
    if group_by == "Story":
        edit_cols = ["story"] + [c for c in edit_cols if c != "story"]
        filtered_df = filtered_df.sort_values("story")
    elif group_by == "Beam Line":
        filtered_df = filtered_df.sort_values("_beam_line")
        edit_cols = ["_beam_line"] + edit_cols
    elif group_by == "Section":
        filtered_df = filtered_df.sort_values("_section")
        edit_cols = ["_section"] + edit_cols

    display_df = filtered_df[edit_cols].copy()

    # Session 33: Improved column config with smart widths
    # Narrow for IDs, wider for editable fields, progress bar for utilization
    column_config = {
        "beam_id": st.column_config.TextColumn("ID", disabled=True, width=75),
        "story": st.column_config.TextColumn("Floor", disabled=True, width=55),
        "_beam_line": st.column_config.TextColumn("Line", disabled=True, width=55),
        "_section": st.column_config.TextColumn("Size", disabled=True, width=70),
        "b_mm": st.column_config.NumberColumn(
            "b", disabled=True, width=45, format="%d"
        ),
        "D_mm": st.column_config.NumberColumn(
            "D", disabled=True, width=45, format="%d"
        ),
        "mu_knm": st.column_config.NumberColumn(
            "Mu", disabled=True, width=55, format="%.0f"
        ),
        "vu_kn": st.column_config.NumberColumn(
            "Vu", disabled=True, width=50, format="%.0f"
        ),
        "bottom_bar_count": st.column_config.NumberColumn(
            "n",
            min_value=2,
            max_value=12,
            step=1,
            width=45,
            help="Number of bottom bars",
        ),
        "bottom_bar_dia": st.column_config.SelectboxColumn(
            "ϕ",
            options=[10, 12, 16, 20, 25, 32],
            width=50,
            help="Bottom bar diameter (mm)",
        ),
        "top_bar_count": st.column_config.NumberColumn(
            "n'", min_value=2, max_value=8, step=1, width=45, help="Number of top bars"
        ),
        "top_bar_dia": st.column_config.SelectboxColumn(
            "ϕ'", options=[10, 12, 16, 20], width=50, help="Top bar diameter (mm)"
        ),
        "stirrup_dia": st.column_config.SelectboxColumn(
            "st", options=[6, 8, 10, 12], width=45, help="Stirrup diameter (mm)"
        ),
        "stirrup_spacing": st.column_config.SelectboxColumn(
            "Sv",
            options=[100, 125, 150, 175, 200, 225, 250, 275, 300],
            width=55,
            help="Stirrup spacing (mm)",
        ),
        "_utilization": st.column_config.ProgressColumn(
            "Util",
            help="Steel utilization: Ast_req/Ast_prov. Green <85%, Yellow 85-100%, Red >100% (under-designed)",
            min_value=0,
            max_value=150,
            format="%.0f%%",
            width=75,
        ),
        "status": st.column_config.TextColumn("✓", disabled=True, width=80),
    }

    # Render editable table with dynamic height (fills available space)
    # Calculate table height based on row count (max 600px, min 200px)
    table_height = min(600, max(200, len(display_df) * 35 + 40))

    # Track if table was edited (for dynamic refresh)
    def on_table_change() -> None:
        st.session_state.ue_table_edited = True

    edited_df = st.data_editor(
        display_df,
        column_config=column_config,
        hide_index=True,
        use_container_width=True,
        height=table_height,
        num_rows="fixed",
        key="ue_smart_table",
        on_change=on_table_change,
    )

    # Tip for selecting beams
    st.caption(
        "💡 Click beam ID to see 3D detail | Edit cells directly | Changes auto-save"
    )

    # Handle row click for 3D focus (using a workaround since no native row selection)
    # We'll add a selectbox for beam selection as fallback
    beam_ids = display_df["beam_id"].tolist()
    if beam_ids:
        sel_col1, sel_col2, sel_col3 = st.columns([2, 2, 1])
        with sel_col1:
            focus_beam = st.selectbox(
                "Focus beam",
                ["(none)"] + beam_ids,
                key="ue_beam_focus",
                label_visibility="collapsed",
                help="Select a beam to see 3D reinforcement detail",
            )
            if focus_beam != "(none)" and focus_beam != st.session_state.get(
                "ue_selected_beam_id"
            ):
                st.session_state.ue_selected_beam_id = focus_beam
                # Session 34: Auto-filter to the beam's story for better context
                beam_story = (
                    df[df["beam_id"] == focus_beam]["story"].iloc[0]
                    if focus_beam in df["beam_id"].values
                    else None
                )
                if beam_story and beam_story != selected_floor:
                    st.session_state.ue_floor_filter = beam_story
                st.rerun()
        with sel_col3:
            if st.session_state.get("ue_selected_beam_id"):
                if st.button("Clear", key="clear_focus", use_container_width=True):
                    st.session_state.ue_selected_beam_id = None
                    st.rerun()

    # Sync changes back to main dataframe (ONLY when table was actually edited)
    # This optimization avoids recalculating all beams on every filter/sort
    if edited_df is not None and st.session_state.get("ue_table_edited", False):
        changed_beams = []
        for idx, row in edited_df.iterrows():
            beam_id = row["beam_id"]
            mask = df["beam_id"] == beam_id
            if not mask.any():
                continue

            # Check if values actually changed
            orig = df.loc[mask].iloc[0]
            bottom_count = row.get("bottom_bar_count", 4)
            bottom_dia = row.get("bottom_bar_dia", 16)
            top_count = row.get("top_bar_count", 2)
            top_dia = row.get("top_bar_dia", 12)
            stirrup_d = row.get("stirrup_dia", 8)
            stirrup_s = row.get("stirrup_spacing", 150)

            # Only recalculate if something changed
            if (
                orig.get("bottom_bar_count", 4) != bottom_count
                or orig.get("bottom_bar_dia", 16) != bottom_dia
                or orig.get("top_bar_count", 2) != top_count
                or orig.get("top_bar_dia", 12) != top_dia
                or orig.get("stirrup_dia", 8) != stirrup_d
                or orig.get("stirrup_spacing", 150) != stirrup_s
            ):
                # Update rebar configuration
                df.loc[mask, "bottom_bar_count"] = bottom_count
                df.loc[mask, "bottom_bar_dia"] = bottom_dia
                df.loc[mask, "top_bar_count"] = top_count
                df.loc[mask, "top_bar_dia"] = top_dia
                df.loc[mask, "stirrup_dia"] = stirrup_d
                df.loc[mask, "stirrup_spacing"] = stirrup_s

                # Full design checks (flexure + shear + spacing)
                beam_row = df.loc[mask].iloc[0]
                checks = calculate_rebar_checks(
                    b_mm=float(beam_row.get("b_mm", 300)),
                    D_mm=float(beam_row.get("D_mm", 450)),
                    mu_knm=float(beam_row.get("mu_knm", 100)),
                    vu_kn=float(beam_row.get("vu_kn", 50)),
                    fck=float(beam_row.get("fck", 25)),
                    fy=float(beam_row.get("fy", 500)),
                    cover_mm=float(beam_row.get("cover_mm", 40)),
                    bottom_bars=[(bottom_dia, bottom_count)],
                    top_bars=[(top_dia, top_count)],
                    stirrup_dia=stirrup_d,
                    stirrup_spacing=stirrup_s,
                )

                # Update status with comprehensive check
                is_safe = checks["all_ok"]
                df.loc[mask, "is_safe"] = is_safe

                # Show most critical issue in status
                if is_safe:
                    util = max(checks["flexure_util"], checks["shear_util"]) * 100
                    df.loc[mask, "status"] = f"✅ {util:.0f}%"
                else:
                    # Find which check failed
                    issues = []
                    if not checks["flexure_ok"]:
                        issues.append(f"M:{checks['flexure_util'] * 100:.0f}%")
                    if not checks["shear_ok"]:
                        issues.append(f"V:{checks['shear_util'] * 100:.0f}%")
                    if not checks["spacing_ok"]:
                        issues.append("Sp")
                    if not checks["min_reinf_ok"]:
                        issues.append("Min")
                    df.loc[mask, "status"] = f"❌ {', '.join(issues)}"

                changed_beams.append(beam_id)

        if changed_beams:
            st.session_state.ws_design_results = df
            st.toast(f"✅ Updated {len(changed_beams)} beam(s)")

        # Reset edit flag and refresh
        st.session_state.ue_table_edited = False
        st.rerun()

    # Beam Line Optimization Section (only when grouped by Beam Line)
    if group_by == "Beam Line" and "_beam_line" in filtered_df.columns:
        st.divider()
        st.subheader("🔗 Beam Line Optimization")
        st.caption(
            "Optimize all beams in a line for consistent reinforcement (construction-friendly)"
        )

        # Get unique beam lines
        beam_lines = filtered_df["_beam_line"].unique()

        # Display beam lines with optimize buttons
        line_cols = st.columns(min(len(beam_lines), 4))
        for i, beam_line in enumerate(beam_lines):
            col_idx = i % len(line_cols)
            with line_cols[col_idx]:
                line_beams = filtered_df[filtered_df["_beam_line"] == beam_line][
                    "beam_id"
                ].tolist()
                failed_count = len(
                    filtered_df[
                        (filtered_df["_beam_line"] == beam_line)
                        & (~filtered_df["is_safe"])
                    ]
                )

                # Status badge
                if failed_count > 0:
                    badge = f"❌ {failed_count}/{len(line_beams)}"
                else:
                    badge = f"✅ {len(line_beams)}"

                if st.button(
                    f"⚡ {beam_line} ({badge})",
                    key=f"opt_line_{beam_line}",
                    use_container_width=True,
                    type="primary" if failed_count > 0 else "secondary",
                ):
                    # Get material properties from first beam
                    first_row = (
                        df[df["beam_id"] == line_beams[0]].iloc[0] if line_beams else {}
                    )
                    fck = float(first_row.get("fck", 25))
                    fy = float(first_row.get("fy", 500))
                    cover = float(first_row.get("cover_mm", 40))

                    # Optimize the beam line
                    unified = optimize_beam_line(line_beams, df, fck, fy, cover)

                    # Apply to dataframe
                    for beam_id, config in unified.items():
                        mask = df["beam_id"] == beam_id
                        if mask.any():
                            df.loc[mask, "bottom_bar_count"] = config.get(
                                "bottom_layer1_count", 4
                            )
                            df.loc[mask, "bottom_bar_dia"] = config.get(
                                "bottom_layer1_dia", 16
                            )
                            # Recalculate status
                            ast_prov = (
                                config.get("bottom_layer1_count", 4)
                                * math.pi
                                * (config.get("bottom_layer1_dia", 16) ** 2)
                                / 4
                            )
                            ast_req = (
                                float(df.loc[mask, "ast_req"].iloc[0])
                                if "ast_req" in df.columns
                                else 500
                            )
                            if ast_prov >= ast_req:
                                df.loc[mask, "is_safe"] = True
                                df.loc[mask, "status"] = "✅ PASS"
                            else:
                                df.loc[mask, "is_safe"] = False
                                df.loc[mask, "status"] = "❌ FAIL"

                    st.session_state.ws_design_results = df
                    st.toast(
                        f"✅ Optimized beam line {beam_line} ({len(unified)} beams) with unified ϕ{unified[line_beams[0]].get('bottom_layer1_dia', 16)}mm bars"
                    )
                    st.rerun()

    # Summary row at bottom
    st.divider()
    s1, s2, s3, s4 = st.columns(4)
    total = len(df)
    passed = len(df[df["is_safe"]])
    s1.metric("Total Beams", total)
    s2.metric("✅ Passed", passed)
    s3.metric("❌ Failed", total - passed)
    s4.metric("Pass Rate", f"{passed / total * 100:.0f}%" if total > 0 else "0%")


def render_unified_editor() -> None:
    """Render full-width unified design editor.

    Features:
    - Compact header with navigation
    - Live 2D cross-section preview
    - Side-by-side controls and checks
    - Beam navigation bar at bottom
    """
    df = st.session_state.ws_design_results
    editor_state = st.session_state.ws_editor_mode

    if df is None or df.empty:
        st.warning("No design results. Run design first.")
        if st.button("← Back to Design"):
            set_workspace_state(WorkspaceState.DESIGN)
            st.rerun()
        return

    # Initialize editor state if needed
    if not editor_state.get("beam_queue"):
        editor_state["beam_queue"] = _get_beam_queue(
            df, editor_state.get("filter_mode", "all")
        )
        editor_state["current_beam_idx"] = 0
        st.session_state.ws_editor_mode = editor_state

    beam_queue = editor_state["beam_queue"]
    if not beam_queue:
        st.warning("No beams match current filter.")
        if st.button("← Back"):
            set_workspace_state(WorkspaceState.DESIGN)
            st.rerun()
        return

    current_idx = editor_state.get("current_beam_idx", 0)
    current_idx = min(current_idx, len(beam_queue) - 1)
    beam_id = beam_queue[current_idx]
    st.session_state.ws_selected_beam = beam_id

    # Get beam data
    row = df[df["beam_id"] == beam_id]
    if row.empty:
        st.error(f"Beam {beam_id} not found")
        return
    row = row.iloc[0]

    # Extract beam properties
    b_mm = float(row["b_mm"])
    D_mm = float(row["D_mm"])
    span_mm = float(row["span_mm"])
    mu_knm = float(row.get("mu_knm", 100))
    vu_kn = float(row.get("vu_kn", 50))
    fck = float(row.get("fck", 25))
    fy = float(row.get("fy", 500))
    cover_mm = float(row.get("cover_mm", 40))

    # Initialize config for this beam
    config = st.session_state.ws_rebar_config
    if config is None or config.get("beam_id") != beam_id:
        ast_req = float(row.get("ast_req", 500))
        suggested = calculate_rebar_layout(
            ast_req, b_mm, D_mm, span_mm, vu_kn, cover_mm
        )
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

    # =========================================================================
    # VIEW MODE TOGGLE: Single Beam vs Table View
    # =========================================================================
    view_mode = editor_state.get("view_mode", "single")  # "single" or "table"

    # Header with view toggle
    hdr_left, hdr_center, hdr_right = st.columns([0.5, 0.3, 0.2])
    with hdr_left:
        st.markdown("### ✏️ Beam Editor")
    with hdr_center:
        mode_options = {"🎯 Single Beam": "single", "📋 Table View": "table"}
        selected_mode_label = (
            "🎯 Single Beam" if view_mode == "single" else "📋 Table View"
        )
        mode_choice = st.radio(
            "View",
            list(mode_options.keys()),
            index=0 if view_mode == "single" else 1,
            horizontal=True,
            key="ue_view_mode",
            label_visibility="collapsed",
        )
        new_mode = mode_options[mode_choice]
        if new_mode != view_mode:
            # Save current beam before switching
            df = _save_current_beam_changes(beam_id, config, df)
            st.session_state.ws_design_results = df
            editor_state["view_mode"] = new_mode
            st.session_state.ws_editor_mode = editor_state
            st.rerun()
    with hdr_right:
        if st.button("✕ Exit", use_container_width=True):
            df = _save_current_beam_changes(beam_id, config, df)
            st.session_state.ws_design_results = df
            set_workspace_state(WorkspaceState.DESIGN)
            st.rerun()

    st.divider()

    # =========================================================================
    # TABLE VIEW MODE - Excel-like batch editing
    # =========================================================================
    if view_mode == "table":
        _render_smart_table_editor(df, editor_state)
        return  # Skip single-beam view

    # =========================================================================
    # SINGLE BEAM VIEW - Detailed editing with preview
    # =========================================================================
    # Compact beam info with status indicator
    is_safe = row.get("is_safe", False)
    status_badge = "✅" if is_safe else "❌"
    info1, info2, info3, info4 = st.columns([0.3, 0.25, 0.25, 0.2])
    with info1:
        st.markdown(f"**{status_badge} {beam_id}**")
    with info2:
        st.caption(f"📐 {b_mm:.0f}×{D_mm:.0f} mm")
    with info3:
        st.caption(f"📏 {span_mm / 1000:.1f} m span")
    with info4:
        st.caption(f"⚡ {mu_knm:.0f} kN·m")

    # =========================================================================
    # MAIN CONTENT: Controls + Checks + Preview
    # =========================================================================
    col_controls, col_checks, col_preview = st.columns([0.3, 0.35, 0.35])

    # Create unique widget keys based on beam_id to force reset on beam change
    # Also include a version counter that changes on optimize/reset
    config_version = config.get("_version", 0)
    key_prefix = f"ue_{beam_id}_{config_version}"

    # --- LEFT: Reinforcement Controls ---
    with col_controls:
        st.markdown("##### 🔧 Reinforcement")

        # Bottom bars - Main tension steel
        st.caption("**Bottom Bars** (tension)")
        bc1, bc2 = st.columns(2)
        with bc1:
            l1_dia = st.selectbox(
                "Dia (mm)",
                [10, 12, 16, 20, 25, 32],
                index=[10, 12, 16, 20, 25, 32].index(config["bottom_layer1_dia"]),
                key=f"{key_prefix}_l1_dia",
                label_visibility="collapsed",
                help="Bar diameter in mm",
            )
        with bc2:
            l1_count = st.number_input(
                "Count",
                2,
                8,
                config["bottom_layer1_count"],
                key=f"{key_prefix}_l1_cnt",
                label_visibility="collapsed",
                help="Number of bars",
            )
        # Show provided area
        ast_l1 = l1_count * math.pi * (l1_dia**2) / 4
        st.caption(f"{l1_count}×Φ{l1_dia} = **{ast_l1:.0f} mm²**")

        # Second layer (optional)
        with st.expander("Layer 2 (optional)", expanded=False):
            l2c1, l2c2 = st.columns(2)
            with l2c1:
                l2_dia = st.selectbox(
                    "Dia2",
                    [0, 10, 12, 16, 20, 25],
                    index=[0, 10, 12, 16, 20, 25].index(
                        config.get("bottom_layer2_dia", 0)
                    ),
                    key=f"{key_prefix}_l2_dia",
                    label_visibility="collapsed",
                )
            with l2c2:
                l2_count = st.number_input(
                    "Cnt2",
                    0,
                    6,
                    config.get("bottom_layer2_count", 0),
                    key=f"{key_prefix}_l2_cnt",
                    label_visibility="collapsed",
                )

        # Top bars
        st.caption("**Top Bars**")
        tc1, tc2 = st.columns(2)
        with tc1:
            top_dia = st.selectbox(
                "TDia",
                [10, 12, 16, 20],
                index=[10, 12, 16, 20].index(config.get("top_dia", 12)),
                key=f"{key_prefix}_top_dia",
                label_visibility="collapsed",
            )
        with tc2:
            top_count = st.number_input(
                "TCnt",
                2,
                6,
                config.get("top_count", 2),
                key=f"{key_prefix}_top_cnt",
                label_visibility="collapsed",
            )
        st.caption(f"{top_count}×Φ{top_dia}")

        # Stirrups
        st.caption("**Stirrups**")
        sc1, sc2 = st.columns(2)
        with sc1:
            stir_dia = st.selectbox(
                "SDia",
                [6, 8, 10],
                index=[6, 8, 10].index(config.get("stirrup_dia", 8)),
                key=f"{key_prefix}_stir_dia",
                label_visibility="collapsed",
            )
        with sc2:
            stir_spacing = st.number_input(
                "Sp",
                75,
                300,
                config.get("stirrup_spacing", 150),
                step=25,
                key=f"{key_prefix}_stir_sp",
                label_visibility="collapsed",
            )
        st.caption(f"Φ{stir_dia}@{stir_spacing}mm")

    # Update config with new values
    config.update(
        {
            "bottom_layer1_dia": l1_dia,
            "bottom_layer1_count": l1_count,
            "bottom_layer2_dia": l2_dia,
            "bottom_layer2_count": l2_count,
            "top_dia": top_dia,
            "top_count": top_count,
            "stirrup_dia": stir_dia,
            "stirrup_spacing": stir_spacing,
        }
    )
    st.session_state.ws_rebar_config = config

    # Build bar lists for checks
    bottom_bars = [(l1_dia, l1_count)]
    if l2_dia > 0 and l2_count > 0:
        bottom_bars.append((l2_dia, l2_count))
    top_bars = [(top_dia, top_count)]

    # Calculate checks
    checks = calculate_rebar_checks(
        b_mm,
        D_mm,
        mu_knm,
        vu_kn,
        fck,
        fy,
        cover_mm,
        bottom_bars,
        top_bars,
        stir_dia,
        stir_spacing,
    )

    # --- CENTER: Design Checks ---
    with col_checks:
        st.markdown("##### ✓ Design Checks")

        # Flexure
        flex_icon = "🟢" if checks["flexure_ok"] else "🔴"
        st.markdown(f"{flex_icon} **Flexure:** {checks['flexure_util'] * 100:.0f}%")
        st.caption(f"Mu_cap = {checks['mu_capacity_knm']:.0f} kN·m")

        # Shear
        shear_icon = "🟢" if checks["shear_ok"] else "🔴"
        st.markdown(f"{shear_icon} **Shear:** {checks['shear_util'] * 100:.0f}%")
        st.caption(f"Vu_cap = {checks['vu_capacity_kn']:.0f} kN")

        # Min/Max steel
        min_icon = "🟢" if checks["min_reinf_ok"] else "🔴"
        st.markdown(
            f"{min_icon} **Min Ast:** {checks['ast_provided']:.0f} ≥ {checks['ast_min']:.0f} mm²"
        )

        max_icon = "🟢" if checks["max_reinf_ok"] else "🔴"
        st.markdown(
            f"{max_icon} **Max Ast:** {checks['ast_provided']:.0f} ≤ {checks['ast_max']:.0f} mm²"
        )

        # Spacing
        sp_icon = "🟢" if checks["spacing_ok"] else "🔴"
        st.markdown(f"{sp_icon} **Spacing:** {checks['bar_spacing']:.0f} mm")

        st.divider()

        # Overall status
        if checks["all_ok"]:
            st.success(f"### {checks['status']}")
        else:
            st.error(f"### {checks['status']}")

        # Quick actions
        act1, act2 = st.columns(2)
        with act1:
            if st.button(
                "⚡ Optimize", use_container_width=True, help="Auto-optimize rebar"
            ):
                optimized = suggest_optimal_rebar(
                    b_mm, D_mm, mu_knm, vu_kn, fck, fy, cover_mm
                )
                if optimized:
                    optimized["beam_id"] = beam_id
                    optimized["top_dia"] = config.get("top_dia", 12)
                    optimized["top_count"] = config.get("top_count", 2)
                    optimized["stirrup_dia"] = config.get("stirrup_dia", 8)
                    optimized["stirrup_spacing"] = config.get("stirrup_spacing", 150)
                    optimized["_version"] = (
                        config.get("_version", 0) + 1
                    )  # Force widget refresh
                    st.session_state.ws_rebar_config = optimized
                    st.toast("✅ Optimized!")
                    st.rerun()
        with act2:
            if st.button(
                "🔄 Reset", use_container_width=True, help="Reset to calculated"
            ):
                # Clear config to reload from original data
                st.session_state.ws_rebar_config = None
                st.rerun()

    # --- RIGHT: Cross-Section Preview ---
    with col_preview:
        # 2D/3D toggle
        view_2d_3d = st.radio(
            "View",
            ["📐 2D Section", "🎨 3D Beam"],
            horizontal=True,
            key=f"{key_prefix}_view_toggle",
            label_visibility="collapsed",
        )

        if view_2d_3d == "📐 2D Section":
            # 2D Cross-Section View
            if VISUALIZATION_AVAILABLE:
                # Use shared bar position calculator (Session 32 - DRY refactor)
                bottom_bars_vis, top_bars_vis = calculate_bar_positions(
                    b_mm=b_mm,
                    D_mm=D_mm,
                    cover_mm=cover_mm,
                    stirrup_dia=stir_dia,
                    l1_count=l1_count,
                    l1_dia=l1_dia,
                    l2_count=l2_count,
                    l2_dia=l2_dia,
                    top_count=top_count,
                    top_dia=top_dia,
                )

                fig = create_cross_section_figure(
                    b=b_mm,
                    D=D_mm,
                    cover=cover_mm,
                    bottom_bars=bottom_bars_vis,
                    top_bars=top_bars_vis,
                    stirrup_dia=stir_dia,
                    rebar_config=config,
                )
                st.plotly_chart(
                    fig, use_container_width=True, key=f"{key_prefix}_cross_section"
                )
            else:
                st.info(
                    f"{b_mm:.0f}×{D_mm:.0f} | Bot: {l1_count}Φ{l1_dia} | Top: {top_count}Φ{top_dia}"
                )
        else:
            # 3D Beam View
            if VISUALIZATION_AVAILABLE:
                try:
                    # Get rebar layout for 3D
                    rebar_3d = calculate_rebar_layout(
                        ast_mm2=float(row.get("ast_req", 500)),
                        b_mm=b_mm,
                        D_mm=D_mm,
                        span_mm=span_mm,
                        vu_kn=vu_kn,
                        cover_mm=cover_mm,
                    )
                    fig_3d = create_beam_3d_figure(
                        b=b_mm,
                        D=D_mm,
                        span=span_mm,
                        bottom_bars=rebar_3d["bottom_bars"],
                        top_bars=rebar_3d["top_bars"],
                        stirrup_positions=rebar_3d["stirrup_positions"],
                        bar_diameter=l1_dia,
                        stirrup_diameter=stir_dia,
                    )
                    fig_3d.update_layout(height=280, margin=dict(l=0, r=0, t=0, b=0))
                    st.plotly_chart(
                        fig_3d, use_container_width=True, key=f"{key_prefix}_3d_view"
                    )
                except Exception as e:
                    st.error(f"3D error: {e}")
            else:
                st.info("3D visualization requires plotly")

    # =========================================================================
    # FOOTER: Beam Navigation
    # =========================================================================
    st.divider()

    # Progress bar showing position in queue
    progress_pct = (current_idx + 1) / len(beam_queue)
    st.progress(progress_pct, text=f"Beam {current_idx + 1} of {len(beam_queue)}")

    # Navigation buttons
    nav1, nav2, nav3, nav4, nav5 = st.columns([0.15, 0.25, 0.2, 0.25, 0.15])

    with nav1:
        if st.button("◀◀ First", use_container_width=True, disabled=current_idx == 0):
            # Save current beam
            df = _save_current_beam_changes(beam_id, config, df)
            st.session_state.ws_design_results = df
            editor_state["current_beam_idx"] = 0
            st.session_state.ws_editor_mode = editor_state  # Persist state
            st.session_state.ws_rebar_config = None
            st.rerun()

    with nav2:
        if st.button("◀ Previous", use_container_width=True, disabled=current_idx == 0):
            df = _save_current_beam_changes(beam_id, config, df)
            st.session_state.ws_design_results = df
            editor_state["current_beam_idx"] = current_idx - 1
            st.session_state.ws_editor_mode = editor_state  # Persist state
            st.session_state.ws_rebar_config = None
            st.rerun()

    with nav3:
        # Quick jump
        jump_to = st.selectbox(
            "Jump to",
            beam_queue,
            index=current_idx,
            key="ue_jump_beam",
            label_visibility="collapsed",
        )
        if jump_to != beam_id:
            df = _save_current_beam_changes(beam_id, config, df)
            st.session_state.ws_design_results = df
            editor_state["current_beam_idx"] = beam_queue.index(jump_to)
            st.session_state.ws_editor_mode = editor_state  # Persist state
            st.session_state.ws_rebar_config = None
            st.rerun()

    with nav4:
        if st.button(
            "Next ▶",
            use_container_width=True,
            type="primary",
            disabled=current_idx >= len(beam_queue) - 1,
        ):
            df = _save_current_beam_changes(beam_id, config, df)
            st.session_state.ws_design_results = df
            editor_state["current_beam_idx"] = current_idx + 1
            st.session_state.ws_editor_mode = editor_state  # Persist state
            st.session_state.ws_rebar_config = None
            st.rerun()

    with nav5:
        if st.button(
            "Last ▶▶",
            use_container_width=True,
            disabled=current_idx >= len(beam_queue) - 1,
        ):
            df = _save_current_beam_changes(beam_id, config, df)
            st.session_state.ws_design_results = df
            editor_state["current_beam_idx"] = len(beam_queue) - 1
            st.session_state.ws_editor_mode = editor_state  # Persist state
            st.session_state.ws_rebar_config = None
            st.rerun()

    # Filter options
    with st.expander("🔍 Filter beams", expanded=False):
        filter_cols = st.columns(4)
        with filter_cols[0]:
            if st.button("All Beams", use_container_width=True):
                editor_state["filter_mode"] = "all"
                editor_state["beam_queue"] = _get_beam_queue(df, "all")
                editor_state["current_beam_idx"] = 0
                st.session_state.ws_editor_mode = editor_state
                st.session_state.ws_rebar_config = None
                st.rerun()
        with filter_cols[1]:
            failed_count = len(df[~df["is_safe"]])
            if st.button(
                f"Failed ({failed_count})",
                use_container_width=True,
                disabled=failed_count == 0,
            ):
                editor_state["filter_mode"] = "failed"
                editor_state["beam_queue"] = _get_beam_queue(df, "failed")
                editor_state["current_beam_idx"] = 0
                st.session_state.ws_editor_mode = editor_state
                st.session_state.ws_rebar_config = None
                st.rerun()
        with filter_cols[2]:
            passed_count = len(df[df["is_safe"]])
            if st.button(f"Passed ({passed_count})", use_container_width=True):
                editor_state["filter_mode"] = "passed"
                editor_state["beam_queue"] = _get_beam_queue(df, "passed")
                editor_state["current_beam_idx"] = 0
                st.session_state.ws_editor_mode = editor_state
                st.session_state.ws_rebar_config = None
                st.rerun()
        with filter_cols[3]:
            if st.button("📊 Back to Results", use_container_width=True):
                df = _save_current_beam_changes(beam_id, config, df)
                st.session_state.ws_design_results = df
                set_workspace_state(WorkspaceState.DESIGN)
                st.rerun()

    # Batch operations (Phase 3 feature)
    with st.expander("⚡ Batch Operations", expanded=False):
        st.caption("Apply optimizations to multiple beams at once")
        batch_cols = st.columns([0.5, 0.5])
        with batch_cols[0]:
            if st.button(
                "⚡ Optimize All Failed",
                use_container_width=True,
                disabled=failed_count == 0,
                help="Auto-optimize rebar for all failed beams",
            ):
                # Batch optimize all failed beams
                failed_beams = df[~df["is_safe"]]["beam_id"].tolist()
                optimized_count = 0
                for failed_id in failed_beams:
                    failed_row = df[df["beam_id"] == failed_id].iloc[0]
                    fb = float(failed_row.get("b_mm", 300))
                    fD = float(failed_row.get("D_mm", 500))
                    fmu = float(failed_row.get("mu_knm", 100))
                    fvu = float(failed_row.get("vu_kn", 50))
                    ffck = float(failed_row.get("fck", 25))
                    ffy = float(failed_row.get("fy", 500))
                    fcover = float(failed_row.get("cover_mm", 40))
                    opt = suggest_optimal_rebar(fb, fD, fmu, fvu, ffck, ffy, fcover)
                    if opt:
                        # Apply to dataframe (simulate re-design)
                        l1_dia = opt.get("bottom_layer1_dia", 16)
                        l1_cnt = opt.get("bottom_layer1_count", 4)
                        ast_prov = l1_cnt * math.pi * (l1_dia**2) / 4
                        ast_req = float(failed_row.get("ast_req", 500))
                        if ast_prov >= ast_req:
                            idx = df[df["beam_id"] == failed_id].index[0]
                            df.at[idx, "is_safe"] = True
                            df.at[idx, "status"] = "✅ PASS"
                            optimized_count += 1
                st.session_state.ws_design_results = df
                editor_state["beam_queue"] = _get_beam_queue(
                    df, editor_state.get("filter_mode", "all")
                )
                st.toast(f"✅ Optimized {optimized_count} failed beams!")
                st.rerun()
        with batch_cols[1]:
            total_beams = len(df)
            if st.button(
                f"⚡ Optimize All ({total_beams})",
                use_container_width=True,
                help="Auto-optimize rebar for all beams",
            ):
                optimized_count = 0
                for _, row in df.iterrows():
                    bid = row["beam_id"]
                    fb = float(row.get("b_mm", 300))
                    fD = float(row.get("D_mm", 500))
                    fmu = float(row.get("mu_knm", 100))
                    fvu = float(row.get("vu_kn", 50))
                    ffck = float(row.get("fck", 25))
                    ffy = float(row.get("fy", 500))
                    fcover = float(row.get("cover_mm", 40))
                    opt = suggest_optimal_rebar(fb, fD, fmu, fvu, ffck, ffy, fcover)
                    if opt:
                        l1_dia = opt.get("bottom_layer1_dia", 16)
                        l1_cnt = opt.get("bottom_layer1_count", 4)
                        ast_prov = l1_cnt * math.pi * (l1_dia**2) / 4
                        ast_req = float(row.get("ast_req", 500))
                        if ast_prov >= ast_req:
                            idx = df[df["beam_id"] == bid].index[0]
                            df.at[idx, "is_safe"] = True
                            df.at[idx, "status"] = "✅ PASS"
                            optimized_count += 1
                st.session_state.ws_design_results = df
                editor_state["beam_queue"] = _get_beam_queue(
                    df, editor_state.get("filter_mode", "all")
                )
                st.toast(f"✅ Optimized {optimized_count} beams!")
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
    # Calculate progress (safe division - states_order always has 5 items)
    progress = (current_idx + 1) / max(len(states_order), 1)

    # Compact state badge instead of progress bar
    state_labels = {
        WorkspaceState.WELCOME: "🏠 Welcome",
        WorkspaceState.IMPORT: "📥 Import",
        WorkspaceState.DESIGN: "📊 Design",
        WorkspaceState.BUILDING_3D: "🏗️ Building 3D",
        WorkspaceState.VIEW_3D: "🎨 Beam 3D",
        WorkspaceState.CROSS_SECTION: "📐 Cross-Section",
        WorkspaceState.REBAR_EDIT: "🔧 Rebar Edit",
        WorkspaceState.UNIFIED_EDITOR: "✏️ Unified Editor",
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
    elif state == WorkspaceState.CROSS_SECTION:
        render_cross_section()
    elif state == WorkspaceState.REBAR_EDIT:
        render_rebar_editor()
    elif state == WorkspaceState.UNIFIED_EDITOR:
        render_unified_editor()
    elif state == WorkspaceState.EDIT:
        render_beam_editor()
    elif state == WorkspaceState.DASHBOARD:
        render_dashboard()
    else:
        st.error(f"Unknown state: {state}")
        render_welcome_panel()
