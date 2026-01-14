"""
BBS Generator Page
==================

Generate Bar Bending Schedules (BBS) for RC beam designs per IS 2502:1999.

Features:
- Auto-generate BBS from beam design
- Manual BBS input mode
- Bar shape diagrams
- Weight calculations
- CSV/Excel export
- Print-ready formatting

Author: STREAMLIT UI SPECIALIST (Agent 6)
Task: STREAMLIT-FEAT-001
Status: 🚧 IN DEVELOPMENT
"""

import io
import sys
from pathlib import Path
from typing import Optional, Dict, List

import pandas as pd
import streamlit as st

# Fix import path
current_file = Path(__file__).resolve()
pages_dir = current_file.parent
streamlit_app_dir = pages_dir.parent

if str(streamlit_app_dir) not in sys.path:
    sys.path.insert(0, str(streamlit_app_dir))

# Add Python library to path
python_lib_dir = streamlit_app_dir.parent.joinpath("Python")
if str(python_lib_dir) not in sys.path:
    sys.path.insert(0, str(python_lib_dir))


# Streamlit imports
from utils.layout import setup_page, page_header, section_header
from utils.theme_manager import initialize_theme, apply_dark_mode_theme
from utils.api_wrapper import cached_design
from utils.caching import SmartCache
from utils.loading_states import loading_context

# Python library imports
try:
    from structural_lib.bbs import (
        BBSLineItem,
        BBSummary,
        BBSDocument,
        calculate_bar_weight,
        calculate_unit_weight_per_meter,
        calculate_straight_bar_length,
        calculate_stirrup_cut_length,
        calculate_hook_length,
        BAR_SHAPES,
        UNIT_WEIGHTS_KG_M,
    )
    from structural_lib.detailing import BeamDetailingResult

    HAS_BBS = True
except ImportError as e:
    st.error(f"⚠️ BBS module not available: {e}")
    HAS_BBS = False

# Initialize theme
initialize_theme()

# Modern page setup
setup_page(
    title="BBS Generator - IS 2502 Bar Bending Schedule", icon="📋", layout="wide"
)

# Apply dark mode
apply_dark_mode_theme()

# Initialize caching
bbs_cache = SmartCache(max_size_mb=20, ttl_seconds=600)


# =============================================================================
# Session State Initialization
# =============================================================================


def initialize_session_state():
    """Initialize session state for BBS generator."""
    if "bbs_inputs" not in st.session_state:
        st.session_state.bbs_inputs = {
            "mode": "auto",  # "auto" or "manual"
            "project_name": "RC Beam Project",
            "member_id": "B1",
            "bbs_items": [],
            "generated_bbs": None,
        }

    if "bbs_auto_data" not in st.session_state:
        st.session_state.bbs_auto_data = None


initialize_session_state()


# =============================================================================
# Helper Functions
# =============================================================================


def safe_int(value, default=0):
    """Safely cast value to int with fallback."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def get_beam_design_from_session() -> Optional[Dict]:
    """Get beam design inputs from beam_design page if available."""
    if "beam_inputs" in st.session_state:
        beam = st.session_state.beam_inputs
        if beam.get("design_computed") and beam.get("design_result"):
            return {"inputs": beam, "result": beam["design_result"]}
    return None


def create_bbs_from_beam_design(beam_data: Dict) -> BBSDocument:
    """
    Generate BBS document from beam design result.

    Args:
        beam_data: Dict with 'inputs' and 'result' keys

    Returns:
        BBSDocument with complete bar bending schedule
    """
    inputs = beam_data["inputs"]
    result = beam_data["result"]

    # Extract dimensions
    span_mm = inputs.get("span_mm", 5000)
    b_mm = inputs.get("b_mm", 300)
    D_mm = inputs.get("D_mm", 500)
    d_mm = inputs.get("d_mm", 450)
    cover_mm = inputs.get("cover_mm", 30)

    # Extract reinforcement from result
    # TODO: Parse actual result format from cached_design()
    ast_mm2 = result.get("ast_required_mm2", 1000)
    bar_dia = result.get("bar_diameter_mm", 20)
    num_bars = result.get("num_bars", 4)
    stirrup_dia = result.get("stirrup_diameter_mm", 8)
    stirrup_spacing = result.get("stirrup_spacing_mm", 150)

    # Development length (simplified - IS 456 Cl 26.2.1)
    ld_mm = 47 * bar_dia  # Approximate for Fe500

    bbs_items = []

    # === MAIN BARS (Bottom) ===
    cut_length_bottom = calculate_straight_bar_length(
        span_mm=span_mm, cover_mm=cover_mm, ld_mm=ld_mm, location="bottom", zone="full"
    )

    unit_weight_bottom = calculate_bar_weight(bar_dia, cut_length_bottom)

    bbs_items.append(
        BBSLineItem(
            bar_mark=f"{inputs.get('member_id', 'B1')}-BM-B",
            member_id=inputs.get("member_id", "B1"),
            location="bottom",
            zone="full",
            shape_code="A",  # Straight bar
            diameter_mm=bar_dia,
            no_of_bars=num_bars,
            cut_length_mm=cut_length_bottom,
            total_length_mm=cut_length_bottom * num_bars,
            unit_weight_kg=unit_weight_bottom,
            total_weight_kg=unit_weight_bottom * num_bars,
            remarks="Bottom tension steel",
        )
    )

    # === STIRRUPS ===
    hook_length = calculate_hook_length(stirrup_dia, hook_angle=135)
    stirrup_cut_length = calculate_stirrup_cut_length(
        b_mm=b_mm,
        D_mm=D_mm,
        cover_mm=cover_mm,
        stirrup_dia_mm=stirrup_dia,
        hook_length_mm=hook_length,
    )

    # Number of stirrups along span
    if stirrup_spacing > 0:
        num_stirrups = safe_int((span_mm / stirrup_spacing) + 1, default=0)
    else:
        num_stirrups = 0

    unit_weight_stirrup = calculate_bar_weight(stirrup_dia, stirrup_cut_length)

    bbs_items.append(
        BBSLineItem(
            bar_mark=f"{inputs.get('member_id', 'B1')}-ST",
            member_id=inputs.get("member_id", "B1"),
            location="stirrup",
            zone="full",
            shape_code="E",  # Closed stirrup
            diameter_mm=stirrup_dia,
            no_of_bars=num_stirrups,
            cut_length_mm=stirrup_cut_length,
            total_length_mm=stirrup_cut_length * num_stirrups,
            unit_weight_kg=unit_weight_stirrup,
            total_weight_kg=unit_weight_stirrup * num_stirrups,
            a_mm=b_mm - 2 * cover_mm,
            b_mm=D_mm - 2 * cover_mm,
            remarks=f"@ {stirrup_spacing}mm c/c",
        )
    )

    # === SUMMARY ===
    total_weight = sum(item.total_weight_kg for item in bbs_items)
    total_length_m = sum(item.total_length_mm for item in bbs_items) / 1000

    weight_by_dia = {}
    for item in bbs_items:
        dia = item.diameter_mm
        if dia not in weight_by_dia:
            weight_by_dia[dia] = 0
        weight_by_dia[dia] += item.total_weight_kg

    summary = BBSummary(
        member_id=inputs.get("member_id", "B1"),
        total_items=len(bbs_items),
        total_bars=sum(item.no_of_bars for item in bbs_items),
        total_length_m=total_length_m,
        total_weight_kg=total_weight,
        weight_by_diameter=weight_by_dia,
    )

    # Create document
    doc = BBSDocument(
        project_name=st.session_state.bbs_inputs["project_name"],
        member_ids=[inputs.get("member_id", "B1")],
        items=bbs_items,
        summary=summary,
    )

    return doc


def bbs_to_dataframe(bbs_doc: BBSDocument) -> pd.DataFrame:
    """Convert BBS document to pandas DataFrame for display."""
    data = []
    for item in bbs_doc.items:
        data.append(
            {
                "Bar Mark": item.bar_mark,
                "Shape": item.shape_code,
                "Diameter (mm)": safe_int(item.diameter_mm, default=0),
                "Location": item.location.capitalize(),
                "No. of Bars": item.no_of_bars,
                "Cut Length (mm)": safe_int(item.cut_length_mm, default=0),
                "Total Length (m)": f"{item.total_length_mm/1000:.2f}",
                "Unit Wt (kg)": f"{item.unit_weight_kg:.2f}",
                "Total Wt (kg)": f"{item.total_weight_kg:.2f}",
                "Remarks": item.remarks,
            }
        )

    return pd.DataFrame(data)


def export_bbs_to_csv(bbs_doc: BBSDocument) -> bytes:
    """Export BBS to CSV format."""
    df = bbs_to_dataframe(bbs_doc)

    # Add header rows
    header = f"Bar Bending Schedule\\nProject: {bbs_doc.project_name}\\nMember(s): {', '.join(bbs_doc.member_ids)}\\n\\n"

    buffer = io.StringIO()
    buffer.write(header)
    df.to_csv(buffer, index=False)

    return buffer.getvalue().encode()


# =============================================================================
# Main UI
# =============================================================================

# Page header
page_header(
    "📋 Bar Bending Schedule Generator",
    "Generate IS 2502 compliant bar bending schedules from beam designs",
)

# Check if BBS module is available
if not HAS_BBS:
    st.error(
        "⚠️ BBS module is not available. Please ensure structural_lib is installed."
    )
    st.stop()

# Mode selection
st.markdown("### Generation Mode")
col1, col2 = st.columns([1, 3])

with col1:
    mode = st.radio(
        "Select Mode",
        options=["auto", "manual"],
        format_func=lambda x: (
            "🤖 Auto (from design)" if x == "auto" else "✏️ Manual Entry"
        ),
        index=0 if st.session_state.bbs_inputs["mode"] == "auto" else 1,
        key="bbs_mode_select",
    )
    st.session_state.bbs_inputs["mode"] = mode

with col2:
    if mode == "auto":
        st.info(
            "**Auto Mode:** Automatically generate BBS from your beam design on the Beam Design page."
        )
    else:
        st.info("**Manual Mode:** Enter bar details manually to create custom BBS.")

st.markdown("---")

# === AUTO MODE ===
if mode == "auto":
    st.markdown("### 🤖 Automatic BBS Generation")

    # Check if beam design exists
    beam_data = get_beam_design_from_session()

    if beam_data is None:
        st.warning(
            """
        **No beam design found!**

        Please go to the **Beam Design** page and:
        1. Enter beam geometry and loading
        2. Click "Run Design Analysis"
        3. Return here to generate BBS
        """
        )

        if st.button("🔗 Go to Beam Design Page"):
            st.switch_page("pages/01_🏗️_beam_design.py")

    else:
        st.success("✅ Beam design loaded from session")

        # Show beam details
        with st.expander("📐 Beam Design Summary", expanded=False):
            inputs = beam_data["inputs"]
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Span", f"{inputs.get('span_mm', 0)/1000:.1f} m")
            with col2:
                st.metric("Width", f"{inputs.get('b_mm', 0)} mm")
            with col3:
                st.metric("Depth", f"{inputs.get('D_mm', 0)} mm")
            with col4:
                st.metric("Concrete", inputs.get("concrete_grade", "M25"))

        # Generate BBS button
        if st.button("🚀 Generate BBS", type="primary", width="stretch"):
            with loading_context("Generating Bar Bending Schedule..."):
                try:
                    bbs_doc = create_bbs_from_beam_design(beam_data)
                    st.session_state.bbs_inputs["generated_bbs"] = bbs_doc
                    st.success("✅ BBS generated successfully!")
                except Exception as e:
                    st.error(f"❌ Error generating BBS: {str(e)}")

        # Display generated BBS
        if st.session_state.bbs_inputs["generated_bbs"] is not None:
            bbs_doc = st.session_state.bbs_inputs["generated_bbs"]

            st.markdown("---")
            st.markdown("### 📋 Bar Bending Schedule")

            # Summary cards
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Items", bbs_doc.summary.total_items)
            with col2:
                st.metric("Total Bars", bbs_doc.summary.total_bars)
            with col3:
                st.metric("Total Length", f"{bbs_doc.summary.total_length_m:.1f} m")
            with col4:
                st.metric("Total Weight", f"{bbs_doc.summary.total_weight_kg:.1f} kg")

            # BBS table
            st.markdown("#### Detailed Bar List")
            df = bbs_to_dataframe(bbs_doc)
            st.dataframe(df, width="stretch", hide_index=True)

            # Weight breakdown
            st.markdown("#### Weight Breakdown by Diameter")
            weight_data = []
            total_weight_kg = bbs_doc.summary.total_weight_kg
            for dia, weight in bbs_doc.summary.weight_by_diameter.items():
                if total_weight_kg > 0:
                    percent_total = (weight / total_weight_kg) * 100
                else:
                    percent_total = 0.0
                weight_data.append(
                    {
                        "Diameter (mm)": f"Ø{safe_int(dia, default=0)}",
                        "Total Weight (kg)": f"{weight:.2f}",
                        "% of Total": f"{percent_total:.1f}%",
                    }
                )

            weight_df = pd.DataFrame(weight_data)
            st.table(weight_df)

            # Export options
            st.markdown("#### 📥 Export Options")
            col1, col2, col3 = st.columns(3)

            with col1:
                csv_data = export_bbs_to_csv(bbs_doc)
                st.download_button(
                    label="📄 Download CSV",
                    data=csv_data,
                    file_name=f"BBS_{bbs_doc.member_ids[0]}.csv",
                    mime="text/csv",
                    width="stretch",
                )

            with col2:
                st.button("📊 Download Excel", disabled=True, width="stretch")
                st.caption("Coming soon")

            with col3:
                st.button("🖨️ Print Preview", disabled=True, width="stretch")
                st.caption("Coming soon")


# === MANUAL MODE ===
else:
    st.markdown("### ✏️ Manual BBS Entry")
    st.info("**Manual mode is under development.** Use Auto mode for now.")

    # TODO: Implement manual entry interface
    # - Input fields for each bar
    # - Add/remove bars
    # - Manual calculations
    # - Preview and export

st.markdown("---")

# Reference section
with st.expander("📖 Reference: Bar Shapes (IS 2502)"):
    st.markdown("#### Standard Bar Shape Codes")

    shapes_data = []
    for code, description in BAR_SHAPES.items():
        shapes_data.append({"Code": code, "Description": description})

    shapes_df = pd.DataFrame(shapes_data)
    st.table(shapes_df)

with st.expander("⚖️ Reference: Unit Weights"):
    st.markdown("#### Standard Bar Unit Weights (kg/m)")

    weights_data = []
    for dia, weight in UNIT_WEIGHTS_KG_M.items():
        weights_data.append(
            {"Diameter (mm)": f"Ø{dia}", "Unit Weight (kg/m)": f"{weight:.3f}"}
        )

    weights_df = pd.DataFrame(weights_data)
    st.table(weights_df)

# Footer
st.markdown("---")
st.caption(
    "Bar Bending Schedule Generator | IS 2502:1999 & SP 34:1987 | Developed by Agent 6"
)
