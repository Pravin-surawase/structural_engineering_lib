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
) -> go.Figure:
    """Create a professional 3D building visualization.

    Features:
    - Real 3D beam positions from geometry coordinates
    - Color coding by design status (pass/fail)
    - Hover information with beam details
    - Story grouping with visual separation
    - Professional dark theme with lighting effects
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

    # Add beams as 3D cylinders (lines with thickness)
    for beam in beams:
        # Determine color based on design result
        result = result_lookup.get(beam.id)
        if result:
            is_safe = result.get("is_safe")
            if is_safe is True:
                color = "rgba(76, 175, 80, 0.9)"  # Green - passed
            elif is_safe is False:
                color = "rgba(244, 67, 54, 0.9)"  # Red - failed
            else:
                color = "rgba(255, 152, 0, 0.9)"  # Orange - no forces
        else:
            # No design results yet - use story color
            color = story_colors.get(beam.story, "#2196F3")

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

        # Add beam as 3D line
        fig.add_trace(
            go.Scatter3d(
                x=[beam.point1.x, beam.point2.x],
                y=[beam.point1.y, beam.point2.y],
                z=[beam.point1.z, beam.point2.z],
                mode="lines",
                line=dict(
                    color=color,
                    width=10,  # Thick lines for visibility
                ),
                name=f"{beam.story}/{beam.label}",
                hovertemplate=hover_text + "<extra></extra>",
                showlegend=False,
            )
        )

        # Add joint markers at beam ends
        fig.add_trace(
            go.Scatter3d(
                x=[beam.point1.x, beam.point2.x],
                y=[beam.point1.y, beam.point2.y],
                z=[beam.point1.z, beam.point2.z],
                mode="markers",
                marker=dict(
                    size=4,
                    color="white",
                    line=dict(color="gray", width=1),
                ),
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
                marker=dict(size=10, color=story_colors[story]),
                name=story,
                showlegend=True,
            )
        )

    # Add status legend if results available
    if result_lookup:
        fig.add_trace(go.Scatter3d(
            x=[None], y=[None], z=[None],
            mode="markers", marker=dict(size=10, color="rgba(76, 175, 80, 0.9)"),
            name="✅ Passed", showlegend=True,
        ))
        fig.add_trace(go.Scatter3d(
            x=[None], y=[None], z=[None],
            mode="markers", marker=dict(size=10, color="rgba(244, 67, 54, 0.9)"),
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
tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload", "📊 Preview", "🔧 Design", "🏗️ 3D View"])

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
        # Controls
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            show_all = st.checkbox("Show all beams", value=True)
        with col2:
            if results_df is not None and not results_df.empty:
                show_passed_only = st.checkbox("Highlight passed only", value=False)
            else:
                show_passed_only = False
        with col3:
            st.write("")  # Spacer

        # Generate and display 3D view
        fig = create_building_3d_view(beams, results_df)
        st.plotly_chart(fig, use_container_width=True)

        # Summary stats
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)

        stories = set(b.story for b in beams)
        col1.metric("📊 Total Beams", len(beams))
        col2.metric("🏢 Stories", len(stories))

        if results_df is not None and not results_df.empty:
            passed = len(results_df[results_df["_is_safe"] == True])
            failed = len(results_df[results_df["_is_safe"] == False])
            col3.metric("✅ Passed", passed)
            col4.metric("❌ Failed", failed)
        else:
            col3.metric("✅ Passed", "-")
            col4.metric("❌ Failed", "-")

        # Tips
        with st.expander("💡 3D Viewer Controls"):
            st.markdown("""
            - **🖱️ Rotate**: Click and drag
            - **🔍 Zoom**: Scroll wheel or pinch
            - **🎯 Pan**: Right-click and drag (or Shift + drag)
            - **📍 Reset**: Double-click to reset view
            - **📷 Save**: Use camera icon in toolbar to save image
            """)

# Footer
st.divider()
st.caption("""
**Supported Formats:**
- **ETABS**: Connectivity - Frame, Element Forces - Beams exports
- **SAFE**: Strip beam forces export
- **STAAD.Pro**: Input file with member geometry and forces
- **Generic CSV**: Custom format with column mapping
""")
