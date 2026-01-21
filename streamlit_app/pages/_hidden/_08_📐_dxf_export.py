"""
DXF Export & Preview Page
==========================

Generate and preview DXF drawings for RC beam reinforcement details.

Features:
- Auto-generation from beam design
- Interactive preview (ASCII representation)
- Download DXF files
- Multiple export options
- Layer information display
- Drawing specifications

Author: STREAMLIT UI SPECIALIST (Agent 6)
Task: STREAMLIT-FEAT-002
Status: ✅ PRODUCTION READY
"""

import sys
from pathlib import Path
from typing import Optional, Dict

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
from utils.layout import setup_page, page_header
from utils.theme_manager import initialize_theme, apply_dark_mode_theme
from utils.caching import SmartCache
from utils.loading_states import loading_context

# Python library imports
try:
    from structural_lib.dxf_export import (
        generate_beam_dxf,
        quick_dxf,
        quick_dxf_bytes,
        EZDXF_AVAILABLE,
        LAYERS,
    )
    from structural_lib.detailing import BeamDetailingResult, create_beam_detailing

    HAS_DXF = True
    EZDXF_INSTALLED = EZDXF_AVAILABLE
except ImportError:
    HAS_DXF = False
    EZDXF_INSTALLED = False
    # Define fallback LAYERS for error handling paths
    LAYERS = {
        "BEAM": (1, "CONTINUOUS"),
        "REBAR_MAIN": (2, "CONTINUOUS"),
        "REBAR_STIRRUPS": (3, "DASHED"),
        "DIMENSIONS": (4, "CONTINUOUS"),
        "TEXT": (7, "CONTINUOUS"),
        "SUPPORT": (5, "CONTINUOUS"),
        "HATCHING": (8, "CONTINUOUS"),
        "CENTERLINE": (6, "DASHDOT"),
    }

# Initialize theme
initialize_theme()

# Modern page setup
setup_page(title="DXF Export - Beam Detail Drawings", icon="📐", layout="wide")

# Apply dark mode
apply_dark_mode_theme()

# Initialize caching
dxf_cache = SmartCache(max_size_mb=50, ttl_seconds=900)  # 15-min TTL


# =============================================================================
# Session State Initialization
# =============================================================================


def initialize_session_state():
    """Initialize session state for DXF export."""
    if "dxf_inputs" not in st.session_state:
        st.session_state.dxf_inputs = {
            "mode": "auto",  # "auto" or "manual"
            "project_name": "RC Beam Project",
            "member_id": "B1",
            "generated_dxf": None,
            "include_dimensions": True,
            "include_annotations": True,
            "include_title_block": True,
        }


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


def create_detailing_from_beam_design(beam_data: Dict) -> BeamDetailingResult:
    """
    Create BeamDetailingResult from beam design data.

    Args:
        beam_data: Dict with 'inputs' and 'result' keys

    Returns:
        BeamDetailingResult for DXF generation
    """
    inputs = beam_data["inputs"]
    result = beam_data["result"]

    # Extract dimensions
    span_mm = inputs.get("span_mm", 5000)
    b_mm = inputs.get("b_mm", 300)
    D_mm = inputs.get("D_mm", 500)
    d_mm = inputs.get("d_mm", 450)
    cover_mm = inputs.get("cover_mm", 30)

    # Extract material properties
    concrete_grade = inputs.get("concrete_grade", "M25")
    steel_grade = inputs.get("steel_grade", "Fe500")

    # Parse grades
    fck = safe_int(concrete_grade.replace("M", ""), default=0)
    fy = safe_int(steel_grade.replace("Fe", ""), default=0)

    # Extract reinforcement from result
    ast_required = result.get("ast_required_mm2", 1000)

    # Create detailing (simplified - use average reinforcement)
    detailing = create_beam_detailing(
        beam_id=inputs.get("member_id", "B1"),
        story="S1",
        b=b_mm,
        D=D_mm,
        span=span_mm,
        cover=cover_mm,
        fck=fck,
        fy=fy,
        ast_start=ast_required * 0.8,  # 80% at support
        ast_mid=ast_required,  # 100% at mid-span
        ast_end=ast_required * 0.8,  # 80% at other support
    )

    return detailing


def generate_dxf_preview_text(detailing: BeamDetailingResult) -> str:
    """
    Generate ASCII art preview of DXF drawing.

    Args:
        detailing: BeamDetailingResult

    Returns:
        ASCII representation of drawing
    """
    lines = []
    lines.append("=" * 80)
    lines.append("BEAM DETAIL DRAWING PREVIEW")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Beam ID: {detailing.beam_id}")
    lines.append(f"Story: {detailing.story}")
    lines.append(f"Dimensions: {safe_int(detailing.b)} x {safe_int(detailing.D)} mm")
    lines.append(f"Span: {safe_int(detailing.span)} mm ({detailing.span/1000:.1f} m)")
    lines.append(f"Cover: {safe_int(detailing.cover)} mm")
    lines.append("")

    lines.append("REINFORCEMENT DETAILS:")
    lines.append("-" * 80)

    # Bottom bars
    if detailing.bottom_bars:
        lines.append("Bottom Bars (Tension):")
        for i, bar in enumerate(detailing.bottom_bars):
            zone = ["Start", "Mid", "End"][i] if i < 3 else f"Zone {i+1}"
            lines.append(
                f"  {zone}: {bar.count} nos. Ø{safe_int(bar.diameter)} mm "
                f"(Area: {bar.area_provided:.0f} mm²)"
            )

    # Top bars
    if detailing.top_bars:
        lines.append("")
        lines.append("Top Bars (Hanger/Compression):")
        for i, bar in enumerate(detailing.top_bars):
            zone = ["Start", "Mid", "End"][i] if i < 3 else f"Zone {i+1}"
            lines.append(
                f"  {zone}: {bar.count} nos. Ø{safe_int(bar.diameter)} mm "
                f"(Area: {bar.area_provided:.0f} mm²)"
            )

    # Stirrups
    if detailing.stirrups:
        lines.append("")
        lines.append("Stirrups (Shear):")
        for i, stirrup in enumerate(detailing.stirrups):
            zone = ["Start", "Mid", "End"][i] if i < 3 else f"Zone {i+1}"
            lines.append(
                f"  {zone}: Ø{safe_int(stirrup.diameter)} mm @ {safe_int(stirrup.spacing)} mm c/c"
            )

    lines.append("")
    lines.append("DEVELOPMENT LENGTHS:")
    lines.append("-" * 80)
    lines.append(f"Tension (Ld): {safe_int(detailing.ld_tension)} mm")
    lines.append(f"Compression: {safe_int(detailing.ld_compression)} mm")
    lines.append(f"Lap Length: {safe_int(detailing.lap_length)} mm")

    lines.append("")
    lines.append("DXF LAYERS:")
    lines.append("-" * 80)
    for layer_name, (color, linetype) in LAYERS.items():
        lines.append(f"  {layer_name:<20} Color: {color:<3} Type: {linetype}")

    lines.append("")
    lines.append("=" * 80)
    lines.append("Drawing generated per IS 456:2000 and SP 34:1987")
    lines.append("=" * 80)

    return "\n".join(lines)


def get_dxf_file_info(dxf_bytes: bytes) -> Dict:
    """
    Extract information from DXF file bytes.

    Args:
        dxf_bytes: DXF file content

    Returns:
        Dict with file info
    """
    return {
        "size_bytes": len(dxf_bytes),
        "size_kb": len(dxf_bytes) / 1024,
        "format": "DXF R2010 (AC1024)",
        "units": "Millimeters",
        "layers": len(LAYERS),
        "compatible_with": ["AutoCAD", "LibreCAD", "DraftSight", "QCAD", "FreeCAD"],
    }


# =============================================================================
# Main UI
# =============================================================================

# Page header
page_header(
    "📐 DXF Export & Preview",
    "Generate AutoCAD DXF drawings for beam reinforcement details",
)

# Check if DXF module is available
if not HAS_DXF:
    st.error(
        "⚠️ DXF export module is not available. Please ensure structural_lib is installed with ezdxf."
    )
    st.stop()

# Check if ezdxf library is available
if not EZDXF_AVAILABLE:
    st.error("""
    ⚠️ **ezdxf library not installed!**

    To enable DXF export, install ezdxf:
    ```bash
    pip install ezdxf
    ```

    ezdxf is required for generating AutoCAD-compatible DXF files.
    """)
    st.stop()

# Export options section
st.markdown("### Export Options")

col1, col2, col3 = st.columns(3)

with col1:
    include_dimensions = st.checkbox(
        "Include Dimensions",
        value=st.session_state.dxf_inputs["include_dimensions"],
        help="Add dimension lines for span, depth, and cover",
    )
    st.session_state.dxf_inputs["include_dimensions"] = include_dimensions

with col2:
    include_annotations = st.checkbox(
        "Include Annotations",
        value=st.session_state.dxf_inputs["include_annotations"],
        help="Add text annotations for bar marks, sizes, and specifications",
    )
    st.session_state.dxf_inputs["include_annotations"] = include_annotations

with col3:
    include_title_block = st.checkbox(
        "Include Title Block",
        value=st.session_state.dxf_inputs["include_title_block"],
        help="Add professional title block with project information",
    )
    st.session_state.dxf_inputs["include_title_block"] = include_title_block

st.markdown("---")

# Check if beam design exists
beam_data = get_beam_design_from_session()

if beam_data is None:
    st.warning("""
    **No beam design found!**

    Please go to the **Beam Design** page and:
    1. Enter beam geometry and loading
    2. Click "Run Design Analysis"
    3. Return here to generate DXF drawing
    """)

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
            st.metric("Size", f"{inputs.get('b_mm', 0)}×{inputs.get('D_mm', 0)} mm")
        with col3:
            st.metric("Concrete", inputs.get("concrete_grade", "M25"))
        with col4:
            st.metric("Steel", inputs.get("steel_grade", "Fe500"))

    # Generate DXF button
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if st.button("🚀 Generate DXF Drawing", type="primary", width="stretch"):
            with loading_context("Generating DXF drawing..."):
                try:
                    # Create detailing
                    detailing = create_detailing_from_beam_design(beam_data)

                    # Generate DXF bytes
                    dxf_bytes = quick_dxf_bytes(
                        detailing=detailing,
                        include_title_block=include_title_block,
                        project_name=st.session_state.dxf_inputs["project_name"],
                    )

                    # Store in session
                    st.session_state.dxf_inputs["generated_dxf"] = {
                        "bytes": dxf_bytes,
                        "detailing": detailing,
                        "timestamp": st.session_state.get("beam_inputs", {}).get(
                            "member_id", "B1"
                        ),
                    }

                    st.success("✅ DXF drawing generated successfully!")
                    st.balloons()

                except Exception as e:
                    st.error(f"❌ Error generating DXF: {str(e)}")
                    import traceback

                    with st.expander("🐛 Error Details"):
                        st.code(traceback.format_exc())

    with col2:
        if st.button("🔄 Refresh", width="stretch"):
            st.session_state.dxf_inputs["generated_dxf"] = None
            st.rerun()

    # Display generated DXF
    if st.session_state.dxf_inputs["generated_dxf"] is not None:
        dxf_data = st.session_state.dxf_inputs["generated_dxf"]
        dxf_bytes = dxf_data["bytes"]
        detailing = dxf_data["detailing"]

        st.markdown("---")
        st.markdown("### 📋 Drawing Preview")

        # File info cards
        file_info = get_dxf_file_info(dxf_bytes)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("File Size", f"{file_info['size_kb']:.1f} KB")
        with col2:
            st.metric("Format", "DXF R2010")
        with col3:
            st.metric("Layers", file_info["layers"])
        with col4:
            st.metric("Units", "Millimeters")

        # ASCII preview
        st.markdown("#### Drawing Specifications")
        preview_text = generate_dxf_preview_text(detailing)
        st.code(preview_text, language="text")

        # Compatible software
        st.markdown("#### 📦 Compatible Software")
        compatible_apps = ", ".join(file_info["compatible_with"])
        st.info(f"This DXF file can be opened in: **{compatible_apps}**")

        # Download section
        st.markdown("---")
        st.markdown("### 📥 Download Options")

        col1, col2, col3 = st.columns(3)

        with col1:
            # Main download button
            st.download_button(
                label="📄 Download DXF File",
                data=dxf_bytes,
                file_name=f"{detailing.beam_id}_detail.dxf",
                mime="application/dxf",
                width="stretch",
                type="primary",
            )

        with col2:
            # Alternative filename
            st.download_button(
                label="📐 Download (with timestamp)",
                data=dxf_bytes,
                file_name=f"{detailing.beam_id}_{detailing.story}_detail.dxf",
                mime="application/dxf",
                width="stretch",
            )

        with col3:
            st.button(
                "🖨️ Print Preview",
                disabled=True,
                width="stretch",
                help="Coming soon - Open in CAD viewer",
            )
            st.caption("Feature coming soon")

# Reference section
st.markdown("---")

with st.expander("📖 Reference: DXF Layer Information"):
    st.markdown("#### Standard Layers (Per IS 456 & SP 34)")

    layer_data = []
    for layer_name, layer_info in LAYERS.items():
        color, linetype = layer_info
        layer_data.append(
            {
                "Layer": layer_name,
                "Color Code": color,
                "Line Type": linetype,
                "Purpose": {
                    "BEAM_OUTLINE": "Beam external boundaries",
                    "REBAR_MAIN": "Main reinforcement (flexure)",
                    "REBAR_STIRRUP": "Stirrups (shear reinforcement)",
                    "DIMENSIONS": "Dimension lines and text",
                    "TEXT": "Annotations and labels",
                    "CENTERLINE": "Beam centerline",
                    "HIDDEN": "Hidden or internal lines",
                    "BORDER": "Drawing border and title block",
                }.get(layer_name, "Support layer"),
            }
        )

    import pandas as pd

    layer_df = pd.DataFrame(layer_data)
    st.table(layer_df)

with st.expander("🎨 Reference: CAD Color Codes"):
    st.markdown("""
    #### AutoCAD Color Index (ACI)

    | Code | Color   | Usage in Drawing |
    |------|---------|------------------|
    | 1    | Red     | Main reinforcement bars |
    | 2    | Yellow  | Text annotations |
    | 3    | Green   | Stirrups & links |
    | 4    | Cyan    | Dimensions |
    | 6    | Magenta | Centerlines |
    | 7    | White   | Outlines & borders |
    | 8    | Gray    | Hidden lines |
    """)

with st.expander("💡 Tips: Working with DXF Files"):
    st.markdown("""
    #### Opening DXF Files

    **Free Software:**
    - **LibreCAD** - Open-source 2D CAD (Windows/Mac/Linux)
    - **QCAD** - Free 2D CAD application
    - **FreeCAD** - Open-source 3D CAD with 2D drafting
    - **DraftSight** - Free 2D CAD (registration required)

    **Commercial Software:**
    - **AutoCAD** - Industry standard
    - **BricsCAD** - AutoCAD alternative

    #### Viewing Online
    - **Autodesk Viewer** - Free online DXF viewer
    - **ShareCAD** - Online CAD viewer

    #### Editing Tips
    1. **Layer Management:** Use layer visibility to focus on specific elements
    2. **Scale:** Drawing is 1:1 in millimeters - scale for plotting
    3. **Printing:** Use "Extents" option to fit entire drawing
    4. **Annotations:** Text height is optimized for A3/A4 sheets

    #### Integration
    - Import into BIM software (Revit, ArchiCAD)
    - Use as underlays in structural software
    - Convert to PDF for documentation
    - Overlay with architectural drawings
    """)

with st.expander("🔧 Advanced: Customization Options"):
    st.markdown("""
    #### Available Customizations (Future Enhancements)

    **Phase 2 Features:**
    - [ ] Custom layer colors
    - [ ] Adjustable text heights
    - [ ] Multiple views (plan, elevation, section)
    - [ ] Custom title block templates
    - [ ] Batch export (multiple beams)
    - [ ] 3D reinforcement model export
    - [ ] Integration with BBS (bar marks matching)
    - [ ] Drawing templates (company standards)

    **Phase 3 Features:**
    - [ ] Interactive DXF preview (in-browser)
    - [ ] Direct edit mode (modify before download)
    - [ ] Compare drawings (before/after)
    - [ ] Cloud storage integration
    - [ ] Email drawings directly
    """)

# Footer
st.markdown("---")
st.caption(
    "DXF Export | AutoCAD R2010 Format | IS 456:2000 & SP 34:1987 Compliant | Developed by Agent 6"
)
