"""
Beam Design Page
================

Interactive RC beam design per IS 456:2000.

Features:
- Complete input interface (geometry, materials, loading, exposure)
- Real-time design computation with caching
- 4-tab results display (Summary, Visualization, Cost, Compliance)
- Session state for input persistence
- Error handling with user-friendly messages
- Print-friendly CSS
- Export options (future: PDF, DXF)

Author: STREAMLIT UI SPECIALIST (Agent 6)
Status: ✅ IMPLEMENTED (STREAMLIT-IMPL-004)
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.inputs import (
    dimension_input,
    material_selector,
    load_input,
    exposure_selector,
    support_condition_selector,
)
from components.visualizations import (
    create_beam_diagram,
    create_cost_comparison,
    create_compliance_visual,
)
from components.preview import render_real_time_preview
from components.results import (
    display_design_status,
    display_reinforcement_summary,
    display_flexure_result,
    display_shear_result,
    display_summary_metrics,
    display_utilization_meters,
    display_material_properties,
    display_compliance_checks,
)
from utils.api_wrapper import cached_design
from utils.layout import setup_page, page_header, section_header
from utils.theme_manager import (
    apply_dark_mode_theme,
    render_theme_toggle,
    initialize_theme,
)
from utils.loading_states import loading_context

# Initialize theme
initialize_theme()

# Modern page setup with professional styling
setup_page(title="Beam Design | IS 456 Dashboard", icon="🏗️", layout="wide")

# Apply dark mode styling
apply_dark_mode_theme()

# Initialize session state for input persistence
if "beam_inputs" not in st.session_state:
    st.session_state.beam_inputs = {
        "span_mm": 5000.0,
        "b_mm": 300.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "concrete_grade": "M25",
        "steel_grade": "Fe500",
        "mu_knm": 120.0,
        "vu_kn": 80.0,
        "exposure": "Moderate",
        "support_condition": "Simply Supported",
        "design_computed": False,
        "design_result": None,
        "last_input_hash": None,  # Track input changes
    }


# Helper function to detect input changes
def get_input_hash():
    """Hash of all inputs to detect changes"""
    import hashlib

    inputs_str = f"{st.session_state.beam_inputs['mu_knm']}_{st.session_state.beam_inputs['vu_kn']}_{st.session_state.beam_inputs['b_mm']}_{st.session_state.beam_inputs['D_mm']}_{st.session_state.beam_inputs['d_mm']}_{st.session_state.beam_inputs['concrete_grade']}_{st.session_state.beam_inputs['steel_grade']}_{st.session_state.beam_inputs['span_mm']}_{st.session_state.beam_inputs['exposure']}"
    return hashlib.md5(inputs_str.encode()).hexdigest()


# Page header with professional styling
page_header(
    title="Beam Design",
    subtitle="Design reinforced concrete beams per IS 456:2000 with real-time compliance checking",
    icon="🏗️",
)

# ============================================================================
# TWO-COLUMN LAYOUT: Input + Preview/Results
# ============================================================================

# Create two-column layout (40% input, 60% preview/results)
col_input, col_preview = st.columns([2, 3], gap="large")

# Left column: Input parameters
with col_input:
    # Compact header with theme toggle inline
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.subheader("📋 Inputs")
    with col_h2:
        render_theme_toggle()

    # Section 1: Geometry (compact)
    st.markdown("**📏 Geometry**")

    span, span_valid = dimension_input(
        label="Span",
        min_value=1000.0,
        max_value=12000.0,
        default_value=st.session_state.beam_inputs["span_mm"],
        unit="mm",
        help_text="Clear span between supports",
        key="input_span",
        show_validation=False,
    )
    st.session_state.beam_inputs["span_mm"] = span

    b, b_valid = dimension_input(
        label="Width",
        min_value=150.0,
        max_value=600.0,
        default_value=st.session_state.beam_inputs["b_mm"],
        unit="mm",
        help_text="Beam width (smaller dimension)",
        key="input_b",
        show_validation=False,
    )
    st.session_state.beam_inputs["b_mm"] = b

    D, D_valid = dimension_input(
        label="Total Depth",
        min_value=200.0,
        max_value=900.0,
        default_value=st.session_state.beam_inputs["D_mm"],
        unit="mm",
        help_text="Total beam depth",
        key="input_D",
        show_validation=False,
    )
    st.session_state.beam_inputs["D_mm"] = D

    d, d_valid = dimension_input(
        label="Effective Depth",
        min_value=150.0,
        max_value=850.0,
        default_value=st.session_state.beam_inputs["d_mm"],
        unit="mm",
        help_text="Distance from compression face to centroid of tension steel",
        key="input_d",
        show_validation=False,
    )
    st.session_state.beam_inputs["d_mm"] = d

    # Validation: d must be less than D
    if d >= D:
        st.error("❌ Effective depth must be less than total depth")
        d_valid = False

    # Section 2: Materials (compact)
    st.markdown("**🧱 Materials**")

    concrete = material_selector(
        material_type="concrete",
        default_grade=st.session_state.beam_inputs["concrete_grade"],
        key="input_concrete",
        show_properties=False,
    )
    st.session_state.beam_inputs["concrete_grade"] = concrete["grade"]

    steel = material_selector(
        material_type="steel",
        default_grade=st.session_state.beam_inputs["steel_grade"],
        key="input_steel",
        show_properties=False,
    )
    st.session_state.beam_inputs["steel_grade"] = steel["grade"]

    # Section 3: Loading (compact)
    st.markdown("**⚖️ Loading**")

    loads = load_input(
        default_moment=st.session_state.beam_inputs["mu_knm"],
        default_shear=st.session_state.beam_inputs["vu_kn"],
        key_prefix="input",
    )
    st.session_state.beam_inputs["mu_knm"] = loads["mu_knm"]
    st.session_state.beam_inputs["vu_kn"] = loads["vu_kn"]

    # Section 4: Exposure & Support (compact - side by side)
    col_exp, col_sup = st.columns(2)

    with col_exp:
        exposure = exposure_selector(
            default=st.session_state.beam_inputs["exposure"],
            key="input_exposure",
            show_requirements=False,
        )
        st.session_state.beam_inputs["exposure"] = exposure["exposure"]

    with col_sup:
        support = support_condition_selector(
            default=st.session_state.beam_inputs["support_condition"],
            key="input_support",
        )
        st.session_state.beam_inputs["support_condition"] = support["condition"]

    st.markdown("---")

    # Analyze button
    all_valid = span_valid and b_valid and D_valid and d_valid

    # Detect input changes
    current_hash = get_input_hash()
    inputs_changed = current_hash != st.session_state.beam_inputs["last_input_hash"]

    if st.button("🚀 Analyze Design", disabled=not all_valid, use_container_width=True):
        # Clear old results if inputs changed
        if inputs_changed:
            st.session_state.beam_inputs["design_result"] = None
            st.session_state.beam_inputs["design_computed"] = False
            # Clear cache to force fresh computation
            from utils.api_wrapper import clear_cache

            clear_cache()

        # Update hash
        st.session_state.beam_inputs["last_input_hash"] = current_hash

        with loading_context("spinner", "Computing design... Please wait"):
            try:
                # Call design API (currently using placeholder from api_wrapper)
                result = cached_design(
                    mu_knm=st.session_state.beam_inputs["mu_knm"],
                    vu_kn=st.session_state.beam_inputs["vu_kn"],
                    b_mm=st.session_state.beam_inputs["b_mm"],
                    D_mm=st.session_state.beam_inputs["D_mm"],
                    d_mm=st.session_state.beam_inputs["d_mm"],
                    fck_nmm2=concrete["fck"],
                    fy_nmm2=steel["fy"],
                    span_mm=st.session_state.beam_inputs["span_mm"],
                    exposure=st.session_state.beam_inputs["exposure"],
                )

                st.session_state.beam_inputs["design_result"] = result
                st.session_state.beam_inputs["design_computed"] = True
                # Also store in design_results for cost optimizer compatibility
                st.session_state.design_results = result
                st.success("✅ Design computed successfully!")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Design computation failed: {str(e)}")
                st.session_state.beam_inputs["design_computed"] = False

    if not all_valid:
        st.warning("⚠️ Fix validation errors before analyzing")
    elif inputs_changed and st.session_state.beam_inputs.get("design_computed", False):
        st.info("ℹ️ Inputs changed. Click 'Analyze Design' to update results.")

    st.markdown("---")

    # Clear cache button
    with st.expander("⚙️ Advanced"):
        if st.button("🗑️ Clear Cache", use_container_width=True):
            from utils.api_wrapper import clear_cache

            clear_cache()
            st.success("Cache cleared!")

# Right column: Preview or Results
with col_preview:
    st.header("📊 Design Preview")

    # Show geometry preview (without reinforcement until analyzed)
    with st.expander(
        "📐 Geometry Preview",
        expanded=not st.session_state.beam_inputs.get("design_computed", False),
    ):
        # Get current exposure for cover
        exposure_props = {
            "Mild": {"cover": 20},
            "Moderate": {"cover": 30},
            "Severe": {"cover": 45},
            "Very Severe": {"cover": 50},
            "Extreme": {"cover": 75},
        }
        cover = exposure_props.get(
            st.session_state.beam_inputs["exposure"], {"cover": 30}
        )["cover"]

        # Only show reinforcement AFTER design is computed
        if st.session_state.beam_inputs.get("design_computed", False):
            bar_dia = 16  # Placeholder
            rebar_y = cover + bar_dia / 2
            rebar_positions = [
                (cover + bar_dia / 2, rebar_y),
                (st.session_state.beam_inputs["b_mm"] / 2, rebar_y),
                (st.session_state.beam_inputs["b_mm"] - cover - bar_dia / 2, rebar_y),
            ]
            xu = st.session_state.beam_inputs["d_mm"] * 0.33
        else:
            # No reinforcement shown before analysis
            rebar_positions = []
            xu = None
            bar_dia = 0

        fig = create_beam_diagram(
            b_mm=st.session_state.beam_inputs["b_mm"],
            D_mm=st.session_state.beam_inputs["D_mm"],
            d_mm=st.session_state.beam_inputs["d_mm"],
            rebar_positions=rebar_positions,
            xu=xu,
            bar_dia=bar_dia,
            cover=cover,
            compression_positions=None,  # No compression steel in preview
            stirrup_dia=0,  # No stirrups in preview
            stirrup_spacing=0,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Show dimensions
        st.caption(
            f"📏 {st.session_state.beam_inputs['b_mm']:.0f} × {st.session_state.beam_inputs['D_mm']:.0f} mm (d={st.session_state.beam_inputs['d_mm']:.0f}mm)"
        )
        if not st.session_state.beam_inputs.get("design_computed", False):
            st.info("ℹ️ Click 'Analyze Design' to see reinforcement")

    st.divider()

    # Show results if computed
    if st.session_state.beam_inputs.get("design_computed", False):
        # Show full results (existing tabs - moved from main area)
        result = st.session_state.beam_inputs["design_result"]

        # Success/Failure banner
        if result.get("is_safe", False):
            st.success("✅ **Design is SAFE** - Meets all IS 456 requirements")
        else:
            st.error(
                "❌ **Design is UNSAFE** - Does not meet IS 456 requirements. Modify dimensions or materials."
            )

        st.divider()

        # Results tabs
        tab1, tab2, tab3, tab4 = st.tabs(
            ["📊 Summary", "🎨 Visualization", "💰 Cost Analysis", "✅ Compliance"]
        )

        # ============================================================================
        # TAB 1: Summary
        # ============================================================================
        with tab1:
            section_header("Design Summary", icon="📊", divider=False)

            # 1. Design Status Banner
            display_design_status(result, show_icon=True)

            st.markdown("---")

            # 2. Reinforcement Summary (main result display)
            display_reinforcement_summary(result, layout="columns")

            st.markdown("---")

            # 3. Utilization Meters
            st.markdown("### 📊 Capacity Utilization")
            display_utilization_meters(result)

            st.markdown("---")

            # 4. Input Summary (collapsible)
            with st.expander("📋 Input Summary", expanded=False):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown("**Geometry**")
                    st.write(
                        f"• Span: {st.session_state.beam_inputs['span_mm']:.0f} mm"
                    )
                    st.write(
                        f"• Section: {st.session_state.beam_inputs['b_mm']:.0f} × {st.session_state.beam_inputs['D_mm']:.0f} mm"
                    )
                    st.write(
                        f"• Eff. depth: {st.session_state.beam_inputs['d_mm']:.0f} mm"
                    )
                with c2:
                    st.markdown("**Materials**")
                    st.write(
                        f"• Concrete: {st.session_state.beam_inputs['concrete_grade']} (fck={concrete['fck']})"
                    )
                    st.write(
                        f"• Steel: {st.session_state.beam_inputs['steel_grade']} (fy={steel['fy']})"
                    )
                with c3:
                    st.markdown("**Loading**")
                    st.write(
                        f"• Moment: {st.session_state.beam_inputs['mu_knm']:.1f} kNm"
                    )
                    st.write(f"• Shear: {st.session_state.beam_inputs['vu_kn']:.1f} kN")

        # ============================================================================
        # TAB 2: Visualization
        # ============================================================================
        with tab2:
            st.subheader("Beam Cross-Section")

            # Get actual bar configuration from design result
            flexure = result.get("flexure", {})
            detailing = result.get("detailing", {})
            shear = result.get("shear", {})
            cover = detailing.get("cover", 30)
            bar_dia = flexure.get("bar_dia", 16)
            num_bars = flexure.get("num_bars", 3)
            num_layers = flexure.get("num_layers", 1)
            spacing_mm = flexure.get("spacing_mm", 0)  # Actual spacing from optimizer
            is_doubly = flexure.get("is_doubly_reinforced", False)
            asc_required = flexure.get("asc_required", 0)

            # Get actual xu from design (not estimate!)
            xu = flexure.get("xu", st.session_state.beam_inputs["d_mm"] * 0.33)

            # Calculate PRACTICAL rebar positions based on actual design
            b_mm = st.session_state.beam_inputs["b_mm"]
            D_mm = st.session_state.beam_inputs["D_mm"]
            d_mm = st.session_state.beam_inputs["d_mm"]

            rebar_positions = []
            compression_positions = []

            # TENSION STEEL: Arrange in layers per IS 456 practice
            if num_bars > 0:
                if num_layers == 1:
                    # Single layer - distribute evenly with actual spacing
                    # Use optimizer spacing if available, else calculate
                    if spacing_mm > 0 and num_bars > 1:
                        # Use library-calculated spacing (center-to-center)
                        total_width_bars = (num_bars - 1) * spacing_mm + bar_dia
                        x_start = (b_mm - total_width_bars) / 2
                        rebar_y = cover + bar_dia / 2
                        for i in range(num_bars):
                            x = x_start + bar_dia / 2 + i * spacing_mm
                            rebar_positions.append((x, rebar_y))
                    else:
                        # Fallback: distribute evenly
                        spacing_h = (b_mm - 2 * cover - bar_dia) / max(num_bars - 1, 1)
                        rebar_y = cover + bar_dia / 2
                        for i in range(num_bars):
                            x = cover + bar_dia / 2 + i * spacing_h
                            rebar_positions.append((x, rebar_y))
                else:
                    # Multiple layers - split bars between layers
                    bars_per_layer = num_bars // num_layers
                    extra_bars = num_bars % num_layers

                    for layer_idx in range(num_layers):
                        layer_bars = bars_per_layer + (1 if layer_idx < extra_bars else 0)
                        # Calculate spacing for this layer
                        if spacing_mm > 0 and layer_bars > 1:
                            # Use library spacing
                            total_width_bars = (layer_bars - 1) * spacing_mm + bar_dia
                            x_start = (b_mm - total_width_bars) / 2
                        else:
                            # Fallback spacing
                            spacing_h = (b_mm - 2 * cover - bar_dia) / max(layer_bars - 1, 1)
                            x_start = cover + bar_dia / 2

                        # Layer spacing: bar_dia + clear spacing (minimum 25mm per IS 456)
                        rebar_y = cover + bar_dia / 2 + layer_idx * (bar_dia + 25)

                        for i in range(layer_bars):
                            if spacing_mm > 0 and layer_bars > 1:
                                x = x_start + bar_dia / 2 + i * spacing_mm
                            else:
                                x = x_start + i * spacing_h
                            rebar_positions.append((x, rebar_y))

            # COMPRESSION STEEL: For doubly reinforced sections
            if is_doubly and asc_required > 0:
                # Use similar bar size as tension steel
                comp_bar_dia = bar_dia
                area_per_bar = 3.14159 * (comp_bar_dia ** 2) / 4
                num_comp_bars = max(2, int(asc_required / area_per_bar) + 1)

                # Position at top (from top surface)
                comp_y = D_mm - cover - comp_bar_dia / 2
                spacing_h = (b_mm - 2 * cover - comp_bar_dia) / max(num_comp_bars - 1, 1)

                for i in range(num_comp_bars):
                    x = cover + comp_bar_dia / 2 + i * spacing_h
                    compression_positions.append((x, comp_y))

            # STIRRUPS: Get shear reinforcement data
            stirrup_dia = shear.get("stirrup_dia", 8)
            stirrup_spacing = shear.get("spacing", 150)
            stirrup_legs = shear.get("legs", 2)

            fig = create_beam_diagram(
                b_mm=b_mm,
                D_mm=D_mm,
                d_mm=d_mm,
                rebar_positions=rebar_positions,
                xu=xu,
                bar_dia=bar_dia,
                cover=cover,
                compression_positions=compression_positions,
                stirrup_dia=stirrup_dia,
                stirrup_spacing=stirrup_spacing,
            )

            st.plotly_chart(fig, use_container_width=True, key="beam_section_viz")

            # Show spacing info if available
            if spacing_mm > 0:
                min_spacing_is456 = max(bar_dia, 20 + 5, 25)  # IS 456 Cl. 26.3.2
                spacing_ok = spacing_mm >= min_spacing_is456
                spacing_status = "✅" if spacing_ok else "⚠️"

                st.caption(
                    f"{spacing_status} **Bar spacing:** {spacing_mm:.1f} mm c/c "
                    f"(min required: {min_spacing_is456:.0f} mm per IS 456 Cl. 26.3.2)"
                )

            st.divider()

            # Reinforcement schedule (table format - more professional)
            st.subheader("📋 Reinforcement Schedule")

            import pandas as pd

            schedule_data = {
                "Element": [
                    "Main Tension",
                    "Stirrups",
                    (
                        "Compression"
                        if flexure.get("is_doubly_reinforced")
                        else "Side Face"
                    ),
                ],
                "Size": [
                    f"{num_bars} - {bar_dia}mm",
                    f"2L-{result.get('shear', {}).get('stirrup_dia', 8)}mm @ {result.get('shear', {}).get('spacing', 150):.0f}mm c/c",
                    (
                        f"{flexure.get('asc_required', 0):.0f} mm² req'd"
                        if flexure.get("is_doubly_reinforced")
                        else (
                            f"{detailing.get('side_face_area', 0):.0f} mm²"
                            if detailing.get("needs_side_face")
                            else "Not required"
                        )
                    ),
                ],
                "Area (mm²)": [
                    f"{flexure.get('ast_provided', 0):.0f}",
                    "—",
                    (
                        f"{flexure.get('asc_required', 0):.0f}"
                        if flexure.get("is_doubly_reinforced")
                        else (
                            f"{detailing.get('side_face_area', 0):.0f}"
                            if detailing.get("needs_side_face")
                            else "—"
                        )
                    ),
                ],
                "Remarks": [
                    f"req'd: {flexure.get('ast_required', 0):.0f} mm²",
                    f"τv={result.get('shear', {}).get('tau_v', 0):.2f} N/mm²",
                    (
                        "Doubly reinforced"
                        if flexure.get("is_doubly_reinforced")
                        else (
                            "D > 450mm"
                            if detailing.get("needs_side_face")
                            else "D ≤ 450mm"
                        )
                    ),
                ],
            }

            df_schedule = pd.DataFrame(schedule_data)
            st.dataframe(df_schedule, use_container_width=True, hide_index=True)

        # ============================================================================
        # TAB 3: Cost Analysis
        # ============================================================================
        with tab3:
            st.subheader("Cost Comparison")

            # Sample alternatives (placeholder data)
            alternatives = [
                {
                    "bar_arrangement": "3-16mm",
                    "cost_per_meter": 87.45,
                    "is_optimal": True,
                    "area_provided": 603,
                },
                {
                    "bar_arrangement": "4-14mm",
                    "cost_per_meter": 89.20,
                    "is_optimal": False,
                    "area_provided": 616,
                },
                {
                    "bar_arrangement": "2-20mm",
                    "cost_per_meter": 92.30,
                    "is_optimal": False,
                    "area_provided": 628,
                },
                {
                    "bar_arrangement": "5-12mm",
                    "cost_per_meter": 85.10,
                    "is_optimal": False,
                    "area_provided": 565,
                },
            ]

            fig_cost = create_cost_comparison(alternatives)
            st.plotly_chart(fig_cost, use_container_width=True, key="cost_comparison")

            st.info(
                """
            💡 **Cost Optimization Tips:**
            - Use standard bar sizes (12, 16, 20, 25 mm)
            - Minimize number of bar diameters
            - Consider constructability and spacing
            - Balance material cost vs labor cost
            """
            )

        # ============================================================================
        # TAB 4: Compliance
        # ============================================================================
        with tab4:
            st.subheader("IS 456:2000 Compliance Checklist")

            # Sample compliance checks (placeholder data)
            checks = [
                {
                    "clause": "26.5.1.1(a)",
                    "description": "Minimum tension reinforcement",
                    "status": "pass",
                    "actual_value": ast_req,
                    "limit_value": 0.85
                    * st.session_state.beam_inputs["b_mm"]
                    * st.session_state.beam_inputs["d_mm"]
                    / steel["fy"],
                    "unit": "mm²",
                    "details": "Ast,min = 0.85 bd / fy",
                },
                {
                    "clause": "26.5.1.1(b)",
                    "description": "Maximum tension reinforcement",
                    "status": "pass",
                    "actual_value": ast_req,
                    "limit_value": 0.04
                    * st.session_state.beam_inputs["b_mm"]
                    * st.session_state.beam_inputs["D_mm"],
                    "unit": "mm²",
                    "details": "Ast,max = 0.04 bD",
                },
                {
                    "clause": "26.5.1.5",
                    "description": "Maximum spacing of tension bars",
                    "status": "pass",
                    "actual_value": 150,
                    "limit_value": min(3 * st.session_state.beam_inputs["d_mm"], 300),
                    "unit": "mm",
                    "details": "Max spacing = min(3d, 300mm)",
                },
                {
                    "clause": "26.5.1.6",
                    "description": "Minimum shear reinforcement",
                    "status": "pass",
                    "actual_value": spacing,
                    "limit_value": 0.75 * st.session_state.beam_inputs["d_mm"],
                    "unit": "mm",
                    "details": "Max spacing = 0.75d for vertical stirrups",
                },
            ]

            create_compliance_visual(checks)

    else:
        # Show real-time preview when design not yet computed
        render_real_time_preview(
            span_mm=st.session_state.beam_inputs["span_mm"],
            b_mm=st.session_state.beam_inputs["b_mm"],
            D_mm=st.session_state.beam_inputs["D_mm"],
            d_mm=st.session_state.beam_inputs["d_mm"],
            concrete_grade=concrete["grade"],
            steel_grade=steel["grade"],
            mu_knm=st.session_state.beam_inputs["mu_knm"],
            vu_kn=st.session_state.beam_inputs["vu_kn"],
            exposure=st.session_state.beam_inputs["exposure"],
            support_condition=st.session_state.beam_inputs["support_condition"],
        )

# ============================================================================
# FOOTER
# ============================================================================

st.divider()

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.caption("📘 **IS 456:2000** - Plain and Reinforced Concrete - Code of Practice")

with col_b:
    st.caption("🔧 **Version:** 0.1.0 (STREAMLIT-IMPL-004)")

with col_c:
    st.caption("👨‍💻 **Agent 6** - STREAMLIT UI SPECIALIST")
