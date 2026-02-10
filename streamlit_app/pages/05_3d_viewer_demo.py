# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
3D Viewer Demo Page — POC for Streamlit Cloud

This page demonstrates the 3D beam visualization component.
It's designed to test the iframe + Three.js approach on Streamlit Cloud.
"""

from __future__ import annotations

import streamlit as st

# Page config must be first Streamlit command
st.set_page_config(
    page_title="3D Beam Viewer Demo",
    page_icon="🏗️",
    layout="wide",
)

# Add parent directory to path for imports
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from components.beam_viewer_3d import render_beam_3d

# PyVista CAD export integration (optional)
try:
    from components.visualization_export import (
        check_pyvista_available,
        export_beam_stl,
        render_beam_screenshot,
        SCREENSHOT_RESOLUTIONS,
    )

    PYVISTA_AVAILABLE = check_pyvista_available()
except ImportError:
    PYVISTA_AVAILABLE = False


def generate_geometry(
    beam_id: str,
    story: str,
    b: int,
    D: int,
    span: int,
    num_bottom_bars: int,
    num_top_bars: int,
    bottom_dia: int,
    top_dia: int,
    stirrup_dia: int,
    stirrup_spacing: int,
    is_seismic: bool,
) -> dict:
    """Generate beam geometry from parameters."""
    cover = 40

    # Calculate bar positions
    half_width = b / 2
    available_width = b - 2 * (cover + stirrup_dia) - bottom_dia

    # Bottom bars
    bottom_bars = []
    if num_bottom_bars <= 1:
        y_positions = [0.0]
    else:
        denominator = num_bottom_bars - 1
        spacing = available_width / denominator if denominator > 0 else 0
        y_positions = [
            -available_width / 2 + i * spacing for i in range(num_bottom_bars)
        ]

    z_bottom = cover + stirrup_dia + bottom_dia / 2
    for i, y in enumerate(y_positions):
        bottom_bars.append(
            {
                "barId": f"B{i + 1}",
                "segments": [
                    {
                        "start": {"x": 0, "y": round(y, 1), "z": round(z_bottom, 1)},
                        "end": {"x": span, "y": round(y, 1), "z": round(z_bottom, 1)},
                        "diameter": bottom_dia,
                        "type": "straight",
                        "length": span,
                    }
                ],
                "diameter": bottom_dia,
                "barType": "bottom",
                "zone": "full",
                "totalLength": span,
            }
        )

    # Top bars
    top_bars = []
    z_top = D - cover - stirrup_dia - top_dia / 2
    if num_top_bars <= 1:
        y_positions_top = [0.0]
    else:
        denominator_top = num_top_bars - 1
        spacing = available_width / denominator_top if denominator_top > 0 else 0
        y_positions_top = [
            -available_width / 2 + i * spacing for i in range(num_top_bars)
        ]

    for i, y in enumerate(y_positions_top):
        top_bars.append(
            {
                "barId": f"T{i + 1}",
                "segments": [
                    {
                        "start": {"x": 0, "y": round(y, 1), "z": round(z_top, 1)},
                        "end": {"x": span, "y": round(y, 1), "z": round(z_top, 1)},
                        "diameter": top_dia,
                        "type": "straight",
                        "length": span,
                    }
                ],
                "diameter": top_dia,
                "barType": "top",
                "zone": "full",
                "totalLength": span,
            }
        )

    # Stirrups
    stirrups = []
    y_outer = half_width - cover - stirrup_dia / 2
    z_bottom_stirrup = cover + stirrup_dia / 2
    z_top_stirrup = D - cover - stirrup_dia / 2

    for x in range(stirrup_spacing // 2, span, stirrup_spacing):
        stirrups.append(
            {
                "positionX": x,
                "path": [
                    {"x": x, "y": round(-y_outer, 1), "z": round(z_bottom_stirrup, 1)},
                    {"x": x, "y": round(y_outer, 1), "z": round(z_bottom_stirrup, 1)},
                    {"x": x, "y": round(y_outer, 1), "z": round(z_top_stirrup, 1)},
                    {"x": x, "y": round(-y_outer, 1), "z": round(z_top_stirrup, 1)},
                ],
                "diameter": stirrup_dia,
                "legs": 2,
                "hookType": "135" if is_seismic else "90",
                "perimeter": round(
                    2 * (2 * y_outer) + 2 * (z_top_stirrup - z_bottom_stirrup), 1
                ),
            }
        )

    return {
        "beamId": beam_id,
        "story": story,
        "dimensions": {"b": b, "D": D, "span": span},
        "concreteOutline": [
            {"x": 0, "y": -half_width, "z": 0},
            {"x": 0, "y": half_width, "z": 0},
            {"x": span, "y": half_width, "z": 0},
            {"x": span, "y": -half_width, "z": 0},
            {"x": 0, "y": -half_width, "z": D},
            {"x": 0, "y": half_width, "z": D},
            {"x": span, "y": half_width, "z": D},
            {"x": span, "y": -half_width, "z": D},
        ],
        "rebars": bottom_bars + top_bars,
        "stirrups": stirrups,
        "metadata": {
            "fck": 25,
            "fy": 500,
            "cover": cover,
            "isSeismic": is_seismic,
            "remarks": "Generated from demo page",
        },
        "version": "1.0.0",
    }


def main():
    """Main demo page."""
    st.title("🏗️ 3D Beam Viewer Demo")
    st.markdown("""
    This page demonstrates the **Three.js-based 3D beam visualization** component.

    **Features:**
    - 🖱️ **Rotate**: Click and drag
    - 🔍 **Zoom**: Scroll wheel
    - 🎯 **Pan**: Right-click and drag
    - 📊 **Info Panel**: Shows beam dimensions and rebar count
    """)

    st.divider()

    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Beam Parameters")

        beam_id = st.text_input("Beam ID", value="B1")
        story = st.text_input("Story", value="Ground Floor")

        st.subheader("Dimensions")
        width = st.slider("Width (b)", 200, 600, 300, 25)
        depth = st.slider("Depth (D)", 300, 900, 450, 25)
        span = st.slider("Span", 2000, 8000, 4000, 500)

        st.subheader("Reinforcement")
        num_bottom_bars = st.slider("Bottom Bars", 2, 6, 3)
        num_top_bars = st.slider("Top Bars", 2, 4, 2)
        bottom_dia = st.selectbox("Bottom Bar Dia", [12, 16, 20, 25], index=1)
        top_dia = st.selectbox("Top Bar Dia", [10, 12, 16, 20], index=1)

        st.subheader("Stirrups")
        stirrup_dia = st.selectbox("Stirrup Dia", [6, 8, 10], index=1)
        stirrup_spacing = st.slider("Stirrup Spacing", 75, 200, 100, 25)
        is_seismic = st.checkbox("Seismic Detailing (135° hooks)", value=True)

        render_btn = st.button("🔄 Update 3D View", type="primary", width="stretch")

    # Generate custom geometry based on inputs
    if render_btn or "beam_geometry" not in st.session_state:
        st.session_state["beam_geometry"] = generate_geometry(
            beam_id=beam_id,
            story=story,
            b=width,
            D=depth,
            span=span,
            num_bottom_bars=num_bottom_bars,
            num_top_bars=num_top_bars,
            bottom_dia=bottom_dia,
            top_dia=top_dia,
            stirrup_dia=stirrup_dia,
            stirrup_spacing=stirrup_spacing,
            is_seismic=is_seismic,
        )

    geometry = st.session_state["beam_geometry"]

    # Render the 3D viewer
    st.subheader(f"📐 Beam {beam_id} — {story}")
    render_beam_3d(geometry, height=650)

    # Show geometry summary
    with st.expander("📋 Geometry Data (JSON)", expanded=False):
        st.json(geometry)

    # CAD Export Section (PyVista integration)
    st.divider()
    st.subheader("📦 CAD Export")

    if PYVISTA_AVAILABLE:
        st.success("✅ PyVista available — CAD export enabled")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📐 STL Export** (for CAD software)")
            include_rebar = st.checkbox(
                "Include reinforcement", value=True, key="stl_rebar"
            )
            if st.button("⬇️ Generate STL", key="export_stl"):
                with st.spinner("Generating STL..."):
                    import tempfile
                    import os

                    # Prepare geometry dict for export
                    beam_data = geometry.get("beamGeometry", {})
                    export_geom = {
                        "b": beam_data.get("b_mm", 300),
                        "D": beam_data.get("D_mm", 450),
                        "span": beam_data.get("span_mm", 4000),
                        "cover": 40,
                        "bottom_bars": [(0, 0, 60), (0, -100, 60), (0, 100, 60)],
                        "top_bars": [(0, -100, 390), (0, 100, 390)],
                        "stirrup_positions": list(range(100, 4000, 150)),
                        "bar_diameter": 16,
                        "stirrup_diameter": 8,
                    }

                    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as f:
                        try:
                            output_path = export_beam_stl(
                                export_geom, f.name, include_rebar=include_rebar
                            )
                            with open(output_path, "rb") as stl_file:
                                st.download_button(
                                    label="⬇️ Download STL",
                                    data=stl_file.read(),
                                    file_name=f"beam_{beam_id}.stl",
                                    mime="application/octet-stream",
                                )
                            st.success(
                                f"✅ STL generated: {os.path.getsize(output_path) / 1024:.1f} KB"
                            )
                        except Exception as e:
                            st.error(f"Export failed: {e}")
                        finally:
                            if os.path.exists(f.name):
                                os.unlink(f.name)

        with col2:
            st.markdown("**📷 High-Resolution Screenshot**")
            resolution = st.selectbox(
                "Resolution",
                ["1080p (1920×1080)", "2K (2560×1440)", "4K (3840×2160)"],
                key="screenshot_res",
            )
            res_map = {
                "1080p (1920×1080)": 1920,
                "2K (2560×1440)": 2560,
                "4K (3840×2160)": 3840,
            }
            res_value = res_map.get(resolution, 1920)

            if st.button("📷 Render Screenshot", key="render_screenshot"):
                with st.spinner(f"Rendering at {resolution}..."):
                    import tempfile
                    import os

                    beam_data = geometry.get("beamGeometry", {})
                    export_geom = {
                        "b": beam_data.get("b_mm", 300),
                        "D": beam_data.get("D_mm", 450),
                        "span": beam_data.get("span_mm", 4000),
                        "cover": 40,
                        "bottom_bars": [(0, 0, 60), (0, -100, 60), (0, 100, 60)],
                        "top_bars": [(0, -100, 390), (0, 100, 390)],
                        "stirrup_positions": list(range(100, 4000, 150)),
                        "bar_diameter": 16,
                        "stirrup_diameter": 8,
                    }

                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                        try:
                            render_beam_screenshot(
                                export_geom, f.name, resolution=res_value
                            )
                            with open(f.name, "rb") as img_file:
                                st.download_button(
                                    label="⬇️ Download PNG",
                                    data=img_file.read(),
                                    file_name=f"beam_{beam_id}_{resolution.split()[0]}.png",
                                    mime="image/png",
                                )
                            st.success(f"✅ Screenshot rendered at {resolution}")
                        except Exception as e:
                            st.error(f"Render failed: {e}")
                        finally:
                            if os.path.exists(f.name):
                                os.unlink(f.name)
    else:
        st.info(
            "💡 **PyVista not installed** — CAD export disabled\n\n"
            "Install with: `pip install pyvista stpyvista`"
        )


if __name__ == "__main__":
    main()
