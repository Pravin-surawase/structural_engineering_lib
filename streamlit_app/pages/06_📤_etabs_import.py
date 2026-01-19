# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
ETABS Import Page
=================

Import beam forces from ETABS CSV export and batch design all beams.

Features:
- Direct ETABS CSV upload (supports ETABS 2019-2024 formats)
- Automatic column detection and validation
- Envelope extraction (max |M|, max |V| per beam)
- Batch design with progress tracking
- 3D visualization grid of all beams
- Export designed beams to Excel/CSV

Integration:
    ETABS → VBA Export → CSV → This Page → Batch Design → 3D View

Author: Session 37 Agent
Task: TASK-3D-001 (Phase 2 - CSV Import UI)
Status: ✅ IMPLEMENTED
"""

from __future__ import annotations

import io
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

# Import ETABS library functions
try:
    from structural_lib.etabs_import import (
        validate_etabs_csv,
        load_etabs_csv,
        normalize_etabs_forces,
        ETABSEnvelopeResult,
        load_frames_geometry,
        merge_forces_and_geometry,
        FrameGeometry,
    )

    ETABS_IMPORT_AVAILABLE = True
except ImportError:
    ETABS_IMPORT_AVAILABLE = False

# Page setup
setup_page(title="ETABS Import | IS 456 Beam Design", icon="📤", layout="wide")
initialize_theme()

# =============================================================================
# Session State
# =============================================================================

if "etabs_csv_path" not in st.session_state:
    st.session_state.etabs_csv_path = None
if "etabs_envelopes" not in st.session_state:
    st.session_state.etabs_envelopes = None
if "etabs_design_results" not in st.session_state:
    st.session_state.etabs_design_results = None
if "etabs_beam_sections" not in st.session_state:
    st.session_state.etabs_beam_sections = {}  # beam_id -> {b_mm, D_mm}
if "etabs_frames_geometry" not in st.session_state:
    st.session_state.etabs_frames_geometry = None  # list[FrameGeometry]
if "etabs_geometry_map" not in st.session_state:
    st.session_state.etabs_geometry_map = {}  # beam_id -> FrameGeometry

# Default section properties (can be overridden per beam)
DEFAULT_SECTION = {
    "b_mm": 300,
    "D_mm": 500,
    "fck_MPa": 25,
    "fy_MPa": 500,
    "cover_mm": 40,
}


# =============================================================================
# Helper Functions
# =============================================================================


def process_etabs_csv(uploaded_file) -> tuple[bool, str, list | None]:
    """Process uploaded ETABS CSV file.

    Returns:
        Tuple of (success, message, envelope_list)
    """
    if not ETABS_IMPORT_AVAILABLE:
        return False, "ETABS import library not available", None

    # Save to temp file for processing
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8"
    ) as f:
        content = uploaded_file.getvalue().decode("utf-8")
        f.write(content)
        temp_path = f.name

    try:
        # Validate first
        is_valid, issues, column_map = validate_etabs_csv(temp_path)

        if not is_valid:
            return False, f"Invalid ETABS CSV: {'; '.join(issues)}", None

        # Get warnings for optional columns
        warnings = [i for i in issues if "optional" in i.lower()]
        if warnings:
            st.warning(f"⚠️ {'; '.join(warnings)}")

        # Normalize to envelopes
        envelopes = normalize_etabs_forces(temp_path)

        msg = f"✅ Loaded {len(envelopes)} beam-load case combinations"
        if column_map:
            detected = ", ".join(f"{k}→{v}" for k, v in column_map.items())
            msg += f"\n\nDetected columns: {detected}"

        return True, msg, envelopes

    except Exception as e:
        return False, f"Error processing CSV: {str(e)}", None

    finally:
        # Cleanup temp file
        Path(temp_path).unlink(missing_ok=True)


def envelopes_to_dataframe(envelopes: list) -> pd.DataFrame:
    """Convert envelope list to DataFrame for display."""
    data = []
    for env in envelopes:
        data.append(
            {
                "Story": env.story,
                "Beam ID": env.beam_id,
                "Load Case": env.case_id,
                "Mu (kN·m)": round(env.mu_knm, 2),
                "Vu (kN)": round(env.vu_kn, 2),
                "Stations": env.station_count,
            }
        )
    return pd.DataFrame(data)


def get_unique_beams(envelopes: list) -> list[tuple[str, str]]:
    """Get unique (story, beam_id) pairs."""
    seen = set()
    unique = []
    for env in envelopes:
        key = (env.story, env.beam_id)
        if key not in seen:
            seen.add(key)
            unique.append(key)
    return unique


def get_governing_envelope(
    envelopes: list, story: str, beam_id: str
) -> tuple[float, float, str]:
    """Get governing (max) envelope for a beam across all load cases.

    Returns:
        (max_mu, max_vu, governing_case)
    """
    beam_envelopes = [e for e in envelopes if e.story == story and e.beam_id == beam_id]
    if not beam_envelopes:
        return 0.0, 0.0, ""

    # Find max moment and max shear (may be from different cases)
    max_mu_env = max(beam_envelopes, key=lambda e: e.mu_knm)
    max_vu_env = max(beam_envelopes, key=lambda e: e.vu_kn)

    # Use governing case as the one with higher utilization (simplified)
    # In practice, might want to design for both cases separately
    governing_case = (
        max_mu_env.case_id if max_mu_env.mu_knm >= max_vu_env.vu_kn else max_vu_env.case_id
    )

    return max_mu_env.mu_knm, max_vu_env.vu_kn, governing_case


def design_beam(
    mu_knm: float,
    vu_kn: float,
    b_mm: float,
    D_mm: float,
    fck: float = 25.0,
    fy: float = 500.0,
    cover_mm: float = 40.0,
) -> dict[str, Any]:
    """Design a single beam using the library API."""
    d_mm = D_mm - cover_mm
    return cached_design(
        mu_knm=mu_knm,
        vu_kn=vu_kn,
        b_mm=b_mm,
        D_mm=D_mm,
        d_mm=d_mm,
        fck_nmm2=fck,
        fy_nmm2=fy,
    )


def process_all_beams(
    envelopes: list,
    beam_sections: dict,
    progress_bar,
    status_text,
) -> pd.DataFrame:
    """Design all beams and return results DataFrame."""
    unique_beams = get_unique_beams(envelopes)
    results = []
    total = len(unique_beams)

    if total == 0:
        return pd.DataFrame(results)

    for idx, (story, beam_id) in enumerate(unique_beams):
        progress = (idx + 1) / total
        progress_bar.progress(progress)
        status_text.text(f"Designing {story}/{beam_id}... ({idx + 1}/{total})")

        # Get governing forces
        mu, vu, case = get_governing_envelope(envelopes, story, beam_id)

        # Get section properties (use beam-specific or default)
        section_key = f"{story}_{beam_id}"
        section = beam_sections.get(section_key, DEFAULT_SECTION)

        try:
            result = design_beam(
                mu_knm=mu,
                vu_kn=vu,
                b_mm=section["b_mm"],
                D_mm=section["D_mm"],
                fck=section["fck_MPa"],
                fy=section["fy_MPa"],
                cover_mm=section.get("cover_mm", 40),
            )

            flexure = result.get("flexure", {})
            shear = result.get("shear", {})
            is_safe = result.get("is_safe", False)

            bar_dia = flexure.get("bar_dia", 16)
            num_bars = flexure.get("num_bars", 3)
            bar_config = f"{num_bars}T{bar_dia}"

            results.append(
                {
                    "Story": story,
                    "Beam ID": beam_id,
                    "Load Case": case,
                    "Mu (kN·m)": round(mu, 1),
                    "Vu (kN)": round(vu, 1),
                    "b×D (mm)": f"{section['b_mm']}×{section['D_mm']}",
                    "Ast_req": round(flexure.get("ast_required", 0), 0),
                    "Ast_prov": round(flexure.get("ast_provided", 0), 0),
                    "Bars": bar_config,
                    "Sv (mm)": shear.get("spacing", "-"),
                    "Status": "✅ OK" if is_safe else "❌ FAIL",
                    "_is_safe": is_safe,  # For filtering
                }
            )

        except Exception as e:
            results.append(
                {
                    "Story": story,
                    "Beam ID": beam_id,
                    "Load Case": case,
                    "Mu (kN·m)": round(mu, 1),
                    "Vu (kN)": round(vu, 1),
                    "b×D (mm)": f"{section['b_mm']}×{section['D_mm']}",
                    "Ast_req": "-",
                    "Ast_prov": "-",
                    "Bars": "-",
                    "Sv (mm)": "-",
                    "Status": f"❌ {str(e)[:30]}",
                    "_is_safe": False,
                }
            )

    return pd.DataFrame(results)


def create_story_summary_chart(results_df: pd.DataFrame) -> go.Figure:
    """Create a story-wise summary chart showing pass/fail counts."""
    if results_df.empty:
        return go.Figure()

    summary = results_df.groupby("Story").agg(
        total=("Beam ID", "count"),
        passed=("_is_safe", "sum"),
    )
    summary["failed"] = summary["total"] - summary["passed"]
    summary = summary.reset_index()

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Passed",
            x=summary["Story"],
            y=summary["passed"],
            marker_color="#28a745",
        )
    )
    fig.add_trace(
        go.Bar(
            name="Failed",
            x=summary["Story"],
            y=summary["failed"],
            marker_color="#dc3545",
        )
    )

    fig.update_layout(
        title="Design Results by Story",
        xaxis_title="Story",
        yaxis_title="Number of Beams",
        barmode="stack",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=400,
    )

    return fig


def create_beam_grid_3d(results_df: pd.DataFrame) -> go.Figure:
    """Create a 3D grid visualization of all beams colored by status."""
    if results_df.empty:
        return go.Figure()

    # Get unique stories and beams for grid layout
    stories = results_df["Story"].unique()
    story_map = {s: i for i, s in enumerate(sorted(stories, reverse=True))}

    beams_per_story = {}
    for story in stories:
        story_beams = results_df[results_df["Story"] == story]["Beam ID"].unique()
        beams_per_story[story] = {b: j for j, b in enumerate(sorted(story_beams))}

    fig = go.Figure()

    # Add beams as 3D boxes
    for _, row in results_df.iterrows():
        story = row["Story"]
        beam_id = row["Beam ID"]
        is_safe = row["_is_safe"]

        z = story_map.get(story, 0) * 4  # Vertical spacing
        x = beams_per_story.get(story, {}).get(beam_id, 0) * 2  # Horizontal spacing
        y = 0

        # Parse section dimensions
        section_str = row["b×D (mm)"]
        try:
            b, D = map(float, section_str.split("×"))
            b = b / 1000 * 0.5  # Scale for visualization
            D = D / 1000 * 0.5
        except (ValueError, AttributeError):
            b, D = 0.15, 0.25

        color = "rgb(40, 167, 69)" if is_safe else "rgb(220, 53, 69)"

        # Add beam as a line with markers
        fig.add_trace(
            go.Scatter3d(
                x=[x - 0.5, x + 0.5],
                y=[y, y],
                z=[z, z],
                mode="lines+markers",
                line=dict(color=color, width=10),
                marker=dict(size=5, color=color),
                name=f"{story}/{beam_id}",
                hovertemplate=(
                    f"<b>{story}/{beam_id}</b><br>"
                    f"Mu: {row['Mu (kN·m)']} kN·m<br>"
                    f"Vu: {row['Vu (kN)']} kN<br>"
                    f"Bars: {row['Bars']}<br>"
                    f"Status: {row['Status']}<extra></extra>"
                ),
                showlegend=False,
            )
        )

    # Add story labels
    for story, z_idx in story_map.items():
        fig.add_trace(
            go.Scatter3d(
                x=[-1],
                y=[0],
                z=[z_idx * 4],
                mode="text",
                text=[story],
                textfont=dict(size=14, color="white"),
                showlegend=False,
            )
        )

    fig.update_layout(
        title="3D Beam Grid - Color by Design Status",
        scene=dict(
            xaxis_title="Beam Position",
            yaxis_title="",
            zaxis_title="Story",
            aspectmode="manual",
            aspectratio=dict(x=2, y=0.5, z=1.5),
        ),
        height=600,
        margin=dict(l=0, r=0, t=40, b=0),
    )

    return fig


# =============================================================================
# Page Layout
# =============================================================================

page_header(
    title="📤 ETABS Import",
    subtitle="Import beam forces from ETABS and batch design",
)

if not ETABS_IMPORT_AVAILABLE:
    st.error(
        "⚠️ ETABS import library not available. "
        "Please ensure `structural_lib` is installed."
    )
    st.stop()

# Instructions
with st.expander("📖 How to Use", expanded=False):
    st.markdown(
        """
    ### Workflow
    1. **Export from ETABS** using VBA tool or manually
    2. **Upload CSV** here - automatic column detection
    3. **Set beam sections** (or use defaults)
    4. **Run batch design** - all beams designed per IS 456
    5. **Review results** in table and 3D view
    6. **Download** results as Excel/CSV

    ### Supported ETABS Formats
    - ETABS 2019, 2020, 2021, 2022, 2023, 2024
    - SAFE slab strip exports
    - Custom CSV with required columns

    ### Required CSV Columns
    | Column | Aliases Detected |
    |--------|------------------|
    | Story | Story, Level, Floor |
    | Beam ID | Label, Frame, Element, Beam |
    | Load Case | Output Case, Load Case, Combo |
    | Moment | M3, Moment3, Mz, M22 |
    | Shear | V2, Shear2, Vy, V23 |

    ### Sample ETABS Export
    ```
    Story,Label,Output Case,Station,M3,V2
    Story1,B1,1.5DL+1.5LL,0.0,125.5,85.2
    Story1,B1,1.5DL+1.5LL,1.5,98.3,42.1
    ...
    ```
    """
    )

st.divider()

# Step 1: Upload
section_header("1️⃣ Upload ETABS CSV")

uploaded_file = st.file_uploader(
    "Choose ETABS CSV export file",
    type=["csv"],
    help="Upload CSV exported from ETABS Frame Forces or Element Forces",
)

if uploaded_file is not None:
    success, message, envelopes = process_etabs_csv(uploaded_file)

    if success and envelopes:
        st.success(message)
        st.session_state.etabs_envelopes = envelopes

        # Show envelope summary
        with st.expander("👁️ Preview Envelope Data", expanded=True):
            df = envelopes_to_dataframe(envelopes)
            st.dataframe(df, use_container_width=True, height=300)

            unique_beams = get_unique_beams(envelopes)
            unique_stories = list(set(e.story for e in envelopes))
            unique_cases = list(set(e.case_id for e in envelopes))

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Records", len(envelopes))
            col2.metric("Unique Beams", len(unique_beams))
            col3.metric("Stories", len(unique_stories))
            col4.metric("Load Cases", len(unique_cases))
    else:
        st.error(message)
        st.session_state.etabs_envelopes = None

st.divider()

# Step 2: Section Properties
if st.session_state.etabs_envelopes is not None:
    section_header("2️⃣ Set Beam Sections")

    with st.expander("⚙️ Section Properties", expanded=True):
        st.markdown("Set default section or customize per beam type.")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            default_b = st.number_input(
                "Width b (mm)",
                min_value=150,
                max_value=1000,
                value=DEFAULT_SECTION["b_mm"],
                step=25,
            )
        with col2:
            default_D = st.number_input(
                "Depth D (mm)",
                min_value=200,
                max_value=2000,
                value=DEFAULT_SECTION["D_mm"],
                step=25,
            )
        with col3:
            default_fck = st.selectbox(
                "Concrete Grade",
                options=[20, 25, 30, 35, 40, 45, 50],
                index=1,
            )
        with col4:
            default_fy = st.selectbox(
                "Steel Grade",
                options=[415, 500, 550],
                index=1,
            )

        # Update defaults
        DEFAULT_SECTION["b_mm"] = default_b
        DEFAULT_SECTION["D_mm"] = default_D
        DEFAULT_SECTION["fck_MPa"] = default_fck
        DEFAULT_SECTION["fy_MPa"] = default_fy

        st.info(
            f"📐 Default section: {default_b}×{default_D}mm, "
            f"M{default_fck}/Fe{default_fy}"
        )

    st.divider()

    # Step 3: Design
    section_header("3️⃣ Batch Design")

    unique_beams = get_unique_beams(st.session_state.etabs_envelopes)
    st.write(f"**Ready to design {len(unique_beams)} beams**")

    if st.button("▶️ Run Batch Design", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        with loading_context("Running IS 456 design calculations..."):
            results_df = process_all_beams(
                st.session_state.etabs_envelopes,
                st.session_state.etabs_beam_sections,
                progress_bar,
                status_text,
            )
            st.session_state.etabs_design_results = results_df

        progress_bar.progress(100)
        status_text.text("✅ Design complete!")
        time.sleep(0.5)
        st.rerun()

st.divider()

# Step 4: Results
if st.session_state.etabs_design_results is not None:
    section_header("4️⃣ Design Results")

    results_df = st.session_state.etabs_design_results

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    total = len(results_df)
    passed = results_df["_is_safe"].sum()
    failed = total - passed

    col1.metric("Total Beams", total)
    col2.metric("Passed ✅", int(passed))
    col3.metric("Failed ❌", int(failed))
    col4.metric("Success Rate", f"{100*passed/total:.0f}%" if total > 0 else "N/A")

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Table", "📊 Charts", "🎮 3D View"])

    with tab1:
        # Filter options
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            status_filter = st.multiselect(
                "Filter by Status",
                options=["✅ OK", "❌ FAIL"],
                default=["✅ OK", "❌ FAIL"],
            )
        with filter_col2:
            story_filter = st.multiselect(
                "Filter by Story",
                options=results_df["Story"].unique().tolist(),
                default=results_df["Story"].unique().tolist(),
            )

        # Apply filters
        display_df = results_df[
            (results_df["Status"].str.contains("|".join(status_filter)))
            & (results_df["Story"].isin(story_filter))
        ]

        # Show table (without internal columns)
        st.dataframe(
            display_df.drop(columns=["_is_safe"]),
            use_container_width=True,
            height=400,
        )

    with tab2:
        st.plotly_chart(create_story_summary_chart(results_df), use_container_width=True)

    with tab3:
        st.plotly_chart(create_beam_grid_3d(results_df), use_container_width=True)

    # Download options
    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        csv_export = results_df.drop(columns=["_is_safe"]).to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            data=csv_export,
            file_name="etabs_design_results.csv",
            mime="text/csv",
        )

    with col2:
        buffer = io.BytesIO()
        export_df = results_df.drop(columns=["_is_safe"])
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            export_df.to_excel(writer, index=False, sheet_name="Design Results")
        excel_data = buffer.getvalue()

        st.download_button(
            "📥 Download Excel",
            data=excel_data,
            file_name="etabs_design_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    with col3:
        if st.button("🔄 Reset All"):
            st.session_state.etabs_envelopes = None
            st.session_state.etabs_design_results = None
            st.session_state.etabs_beam_sections = {}
            st.rerun()

# Footer
st.divider()
st.caption(
    """
💡 **Integration:** Export from ETABS using the VBA tool, then import here for batch design.
See [VBA Export Documentation](https://github.com/your-repo/docs/vba) for setup.
"""
)
