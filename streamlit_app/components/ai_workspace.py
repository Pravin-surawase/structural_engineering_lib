# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
AI Workspace Component - Dynamic State-Based Workspace

This module provides a unified workspace that transitions based on workflow state:
- WELCOME: Quick start cards for getting started
- IMPORT: Auto-mapped preview after file upload
- DESIGN: Interactive results table with beam selection
- VIEW_3D: Selected beam with rebar visualization
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
from enum import Enum
from typing import Any

import pandas as pd
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
    VIEW_3D = "view_3d"
    EDIT = "edit"
    DASHBOARD = "dashboard"


# Sample ETABS-like data for quick start
SAMPLE_ETABS_DATA = """Unique Name,Width,Depth,Length,M3,V2,Story
B1-L1,300,500,5000,120.5,45.2,Story1
B2-L1,300,500,5000,145.3,52.1,Story1
B3-L1,300,600,6000,185.7,68.3,Story1
B4-L1,350,600,6000,210.2,75.4,Story1
B5-L2,300,500,4500,95.6,38.9,Story2
B6-L2,300,500,4500,110.3,42.5,Story2
B7-L2,300,550,5500,155.8,55.7,Story2
B8-L3,350,650,7000,245.6,88.2,Story3
B9-L3,350,650,7000,265.3,95.1,Story3
B10-L3,400,700,8000,320.5,112.4,Story3
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

    if "ws_defaults" not in st.session_state:
        st.session_state.ws_defaults = {
            "fck": 25.0,
            "fy": 500.0,
            "cover_mm": 40.0,
        }


def set_workspace_state(new_state: WorkspaceState) -> None:
    """Change workspace state and trigger rerun."""
    st.session_state.ws_state = new_state


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
    st.markdown("### 🚀 Get Started")
    st.caption("Choose how to import beam data for design")

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("**📂 Sample Data**")
            st.caption("Try with 10 beams from ETABS-like export")
            if st.button("Load Sample", key="ws_sample", use_container_width=True):
                load_sample_data()
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("**📤 Upload CSV**")
            st.caption("From ETABS, SAFE, or custom format")
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
            st.markdown("**✏️ Manual Input**")
            st.caption("Enter beam parameters directly")
            if st.button("Start Manual", key="ws_manual", use_container_width=True):
                # Create empty dataframe with one row
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
                }])
                st.session_state.ws_state = WorkspaceState.EDIT
                st.rerun()


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

    st.markdown("### 📊 Design Results")

    if df is None or df.empty:
        st.warning("No design results. Design beams first.")
        if st.button("← Back to Import"):
            set_workspace_state(WorkspaceState.IMPORT)
            st.rerun()
        return

    # Summary metrics
    total = len(df)
    passed = len(df[df["is_safe"] == True])
    failed = total - passed
    avg_util = df["utilization"].mean() * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Beams", total)
    col2.metric("Passed ✅", passed, delta=f"{100*passed/max(total,1):.0f}%")
    col3.metric("Failed ❌", failed)
    col4.metric("Avg Utilization", f"{avg_util:.1f}%")

    # Results table with selection
    st.markdown("**Click a beam row to view 3D details:**")
    display_df = df[["beam_id", "story", "b_mm", "D_mm", "mu_knm", "vu_kn", "ast_req", "status"]].copy()
    display_df.columns = ["ID", "Story", "b (mm)", "D (mm)", "Mu (kN·m)", "Vu (kN)", "Ast_req", "Status"]

    # Beam selector (since st.dataframe selection has limitations)
    beam_options = ["Select a beam..."] + df["beam_id"].tolist()
    selected = st.selectbox("🔍 Select Beam", beam_options, key="ws_beam_select")

    st.dataframe(display_df, use_container_width=True, height=200)

    # Action buttons based on selection
    if selected != "Select a beam...":
        st.session_state.ws_selected_beam = selected

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🎨 View 3D", use_container_width=True, type="primary"):
                set_workspace_state(WorkspaceState.VIEW_3D)
                st.rerun()
        with col2:
            if st.button("✏️ Edit Beam", use_container_width=True):
                set_workspace_state(WorkspaceState.EDIT)
                st.rerun()
        with col3:
            if st.button("📊 Dashboard", use_container_width=True):
                set_workspace_state(WorkspaceState.DASHBOARD)
                st.rerun()

    st.divider()
    if st.button("← Back to Import"):
        set_workspace_state(WorkspaceState.IMPORT)
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
            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True, key="ws_3d_view")
        except Exception as e:
            st.error(f"3D rendering error: {e}")
    else:
        st.info("3D visualization not available")

    # Navigation
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("← Back to Results", use_container_width=True):
            set_workspace_state(WorkspaceState.DESIGN)
            st.rerun()
    with col2:
        if st.button("✏️ Edit This Beam", use_container_width=True):
            set_workspace_state(WorkspaceState.EDIT)
            st.rerun()
    with col3:
        # Next beam button
        beam_list = df["beam_id"].tolist()
        curr_idx = beam_list.index(beam_id) if beam_id in beam_list else 0
        next_idx = (curr_idx + 1) % len(beam_list)
        if st.button("▶ Next Beam", use_container_width=True):
            st.session_state.ws_selected_beam = beam_list[next_idx]
            st.rerun()


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

    col1, col2 = st.columns([0.4, 0.6])

    with col1:
        st.markdown("**Geometry**")
        b = st.number_input("Width b (mm)", value=float(row["b_mm"]), step=25.0, key="edit_b")
        D = st.number_input("Depth D (mm)", value=float(row["D_mm"]), step=25.0, key="edit_D")
        span = st.number_input("Span (mm)", value=float(row["span_mm"]), step=100.0, key="edit_span")

        st.markdown("**Loading**")
        mu = st.number_input("Moment Mu (kN·m)", value=float(row["mu_knm"]), step=10.0, key="edit_mu")
        vu = st.number_input("Shear Vu (kN)", value=float(row["vu_kn"]), step=5.0, key="edit_vu")

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

    # State indicator bar
    states_order = [
        WorkspaceState.WELCOME,
        WorkspaceState.IMPORT,
        WorkspaceState.DESIGN,
        WorkspaceState.VIEW_3D,
    ]

    current_idx = states_order.index(state) if state in states_order else 0
    progress = (current_idx + 1) / len(states_order)

    st.progress(progress, text=f"📍 {state.value.upper()}")

    # Route to correct renderer
    if state == WorkspaceState.WELCOME:
        render_welcome_panel()
    elif state == WorkspaceState.IMPORT:
        render_import_preview()
    elif state == WorkspaceState.DESIGN:
        render_design_results()
    elif state == WorkspaceState.VIEW_3D:
        render_3d_view()
    elif state == WorkspaceState.EDIT:
        render_beam_editor()
    elif state == WorkspaceState.DASHBOARD:
        render_dashboard()
    else:
        st.error(f"Unknown state: {state}")
        render_welcome_panel()
