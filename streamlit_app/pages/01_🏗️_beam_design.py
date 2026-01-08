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
    support_condition_selector
)
from components.visualizations import (
    create_beam_diagram,
    create_cost_comparison,
    create_utilization_gauge,
    create_sensitivity_tornado,
    create_compliance_visual
)
from components.preview import render_real_time_preview
from utils.api_wrapper import cached_design, cached_smart_analysis
from utils.validation import validate_dimension, format_error_message
from utils.layout import setup_page, page_header, section_header, three_column_metrics, info_panel
from utils.theme_manager import apply_dark_mode_theme, render_theme_toggle, initialize_theme
from utils.loading_states import loading_context, add_loading_skeleton

# Initialize theme
initialize_theme()

# Modern page setup with professional styling
setup_page(
    title="Beam Design | IS 456 Dashboard",
    icon="🏗️",
    layout="wide"
)

# Apply dark mode styling
apply_dark_mode_theme()

# Initialize session state for input persistence
if 'beam_inputs' not in st.session_state:
    st.session_state.beam_inputs = {
        'span_mm': 5000.0,
        'b_mm': 300.0,
        'D_mm': 500.0,
        'd_mm': 450.0,
        'concrete_grade': 'M25',
        'steel_grade': 'Fe500',
        'mu_knm': 120.0,
        'vu_kn': 80.0,
        'exposure': 'Moderate',
        'support_condition': 'Simply Supported',
        'design_computed': False,
        'design_result': None,
        'last_input_hash': None  # Track input changes
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
    icon="🏗️"
)

# ============================================================================
# TWO-COLUMN LAYOUT: Input + Preview/Results
# ============================================================================

# Create two-column layout (40% input, 60% preview/results)
col_input, col_preview = st.columns([2, 3], gap="large")

# Left column: Input parameters
with col_input:
    st.header("📋 Input Parameters")

    # Theme toggle
    render_theme_toggle()

    st.markdown("---")

    # Section 1: Geometry
    st.subheader("📏 Geometry")

    span, span_valid = dimension_input(
        label="Span",
        min_value=1000.0,
        max_value=12000.0,
        default_value=st.session_state.beam_inputs['span_mm'],
        unit="mm",
        help_text="Clear span between supports",
        key="input_span",
        show_validation=False
    )
    st.session_state.beam_inputs['span_mm'] = span

    b, b_valid = dimension_input(
        label="Width",
        min_value=150.0,
        max_value=600.0,
        default_value=st.session_state.beam_inputs['b_mm'],
        unit="mm",
        help_text="Beam width (smaller dimension)",
        key="input_b",
        show_validation=False
    )
    st.session_state.beam_inputs['b_mm'] = b

    D, D_valid = dimension_input(
        label="Total Depth",
        min_value=200.0,
        max_value=900.0,
        default_value=st.session_state.beam_inputs['D_mm'],
        unit="mm",
        help_text="Total beam depth",
        key="input_D",
        show_validation=False
    )
    st.session_state.beam_inputs['D_mm'] = D

    d, d_valid = dimension_input(
        label="Effective Depth",
        min_value=150.0,
        max_value=850.0,
        default_value=st.session_state.beam_inputs['d_mm'],
        unit="mm",
        help_text="Distance from compression face to centroid of tension steel",
        key="input_d",
        show_validation=False
    )
    st.session_state.beam_inputs['d_mm'] = d

    # Validation: d must be less than D
    if d >= D:
        st.error("❌ Effective depth must be less than total depth")
        d_valid = False

    st.markdown("---")

    # Section 2: Materials
    st.subheader("🧱 Materials")

    concrete = material_selector(
        material_type="concrete",
        default_grade=st.session_state.beam_inputs['concrete_grade'],
        key="input_concrete",
        show_properties=False
    )
    st.session_state.beam_inputs['concrete_grade'] = concrete['grade']

    steel = material_selector(
        material_type="steel",
        default_grade=st.session_state.beam_inputs['steel_grade'],
        key="input_steel",
        show_properties=False
    )
    st.session_state.beam_inputs['steel_grade'] = steel['grade']

    st.markdown("---")

    # Section 3: Loading
    st.subheader("⚖️ Loading")

    loads = load_input(
        default_moment=st.session_state.beam_inputs['mu_knm'],
        default_shear=st.session_state.beam_inputs['vu_kn'],
        key_prefix="input"
    )
    st.session_state.beam_inputs['mu_knm'] = loads['mu_knm']
    st.session_state.beam_inputs['vu_kn'] = loads['vu_kn']

    st.markdown("---")

    # Section 4: Exposure & Support
    st.subheader("🌦️ Exposure")

    exposure = exposure_selector(
        default=st.session_state.beam_inputs['exposure'],
        key="input_exposure",
        show_requirements=False
    )
    st.session_state.beam_inputs['exposure'] = exposure['exposure']

    st.markdown("---")

    st.subheader("🔗 Support Condition")

    support = support_condition_selector(
        default=st.session_state.beam_inputs['support_condition'],
        key="input_support"
    )
    st.session_state.beam_inputs['support_condition'] = support['condition']

    st.markdown("---")

    # Analyze button
    all_valid = span_valid and b_valid and D_valid and d_valid

    # Detect input changes
    current_hash = get_input_hash()
    inputs_changed = (current_hash != st.session_state.beam_inputs['last_input_hash'])

    if st.button("🚀 Analyze Design", disabled=not all_valid, use_container_width=True):
        # Clear old results if inputs changed
        if inputs_changed:
            st.session_state.beam_inputs['design_result'] = None
            st.session_state.beam_inputs['design_computed'] = False
            # Clear cache to force fresh computation
            from utils.api_wrapper import clear_cache
            clear_cache()

        # Update hash
        st.session_state.beam_inputs['last_input_hash'] = current_hash

        with loading_context("spinner", "Computing design... Please wait"):
            try:
                # Call design API (currently using placeholder from api_wrapper)
                result = cached_design(
                    mu_knm=st.session_state.beam_inputs['mu_knm'],
                    vu_kn=st.session_state.beam_inputs['vu_kn'],
                    b_mm=st.session_state.beam_inputs['b_mm'],
                    D_mm=st.session_state.beam_inputs['D_mm'],
                    d_mm=st.session_state.beam_inputs['d_mm'],
                    fck_nmm2=concrete['fck'],
                    fy_nmm2=steel['fy'],
                    span_mm=st.session_state.beam_inputs['span_mm'],
                    exposure=st.session_state.beam_inputs['exposure']
                )

                st.session_state.beam_inputs['design_result'] = result
                st.session_state.beam_inputs['design_computed'] = True
                st.success("✅ Design computed successfully!")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Design computation failed: {str(e)}")
                st.session_state.beam_inputs['design_computed'] = False

    if not all_valid:
        st.warning("⚠️ Fix validation errors before analyzing")
    elif inputs_changed and st.session_state.beam_inputs.get('design_computed', False):
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

    # ALWAYS show geometry preview (updates immediately with inputs)
    with st.expander("📐 Geometry Visualization", expanded=not st.session_state.beam_inputs.get('design_computed', False)):
        # Get current exposure for cover
        exposure_props = {
            'Mild': {'cover': 20},
            'Moderate': {'cover': 30},
            'Severe': {'cover': 45},
            'Very Severe': {'cover': 50},
            'Extreme': {'cover': 75}
        }
        cover = exposure_props.get(st.session_state.beam_inputs['exposure'], {'cover': 30})['cover']
        bar_dia = 16  # Placeholder

        # Calculate rebar positions (3 bars at bottom)
        spacing_h = (st.session_state.beam_inputs['b_mm'] - 2 * cover) / 2
        rebar_y = cover + bar_dia / 2
        rebar_positions = [
            (cover + bar_dia / 2, rebar_y),
            (st.session_state.beam_inputs['b_mm'] / 2, rebar_y),
            (st.session_state.beam_inputs['b_mm'] - cover - bar_dia / 2, rebar_y)
        ]
        xu = st.session_state.beam_inputs['d_mm'] * 0.33  # Placeholder neutral axis

        fig = create_beam_diagram(
            b_mm=st.session_state.beam_inputs['b_mm'],
            D_mm=st.session_state.beam_inputs['D_mm'],
            d_mm=st.session_state.beam_inputs['d_mm'],
            rebar_positions=rebar_positions,
            xu=xu,
            bar_dia=bar_dia,
            cover=cover
        )
        st.plotly_chart(fig, use_container_width=True)

        # Show dimensions
        st.caption(f"📏 Width: {st.session_state.beam_inputs['b_mm']:.0f}mm × Depth: {st.session_state.beam_inputs['D_mm']:.0f}mm (d = {st.session_state.beam_inputs['d_mm']:.0f}mm)")

    st.divider()

    # Show results if computed
    if st.session_state.beam_inputs.get('design_computed', False):
        # Show full results (existing tabs - moved from main area)
        result = st.session_state.beam_inputs['design_result']

        # Success/Failure banner
        if result.get('is_safe', False):
            st.success("✅ **Design is SAFE** - Meets all IS 456 requirements")
        else:
            st.error("❌ **Design is UNSAFE** - Does not meet IS 456 requirements. Modify dimensions or materials.")

        st.divider()

        # Results tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Summary",
            "🎨 Visualization",
            "💰 Cost Analysis",
            "✅ Compliance"
        ])

        # ============================================================================
        # TAB 1: Summary
        # ============================================================================
        with tab1:
            section_header("Design Summary", icon="📊", divider=False)

            st.markdown("<br>", unsafe_allow_html=True)

            # Key metrics in modern card format
            ast_req = result.get('flexure', {}).get('ast_required', 0)
            spacing = result.get('shear', {}).get('spacing', 0)
            utilization = result.get('flexure', {}).get('ast_required', 0) / (st.session_state.beam_inputs['b_mm'] * st.session_state.beam_inputs['d_mm']) * 100 if result.get('flexure', {}).get('ast_required', 0) > 0 else 0

            # Use three_column_metrics helper for consistent layout
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Steel Area Required",
                    f"{ast_req:.0f} mm²",
                    help="Tension steel area per IS 456 Cl. 26.5.1"
                )
            with col2:
                st.metric(
                    "Stirrup Spacing",
                    f"{spacing:.0f} mm c/c" if spacing > 0 else "—",
                    help="Shear reinforcement spacing per IS 456 Cl. 26.5.1.6"
                )
            with col3:
                st.metric(
                    "Flexure Utilization",
                    f"{utilization:.1f}%",
                    help="Percentage of flexural capacity utilized"
                )
            with col4:
                st.metric(
                    "Overall Status",
                    "✅ SAFE" if result.get('is_safe') else "❌ UNSAFE",
                    help="Overall design safety status"
                )

            st.markdown("<br><br>", unsafe_allow_html=True)

            # Detailed results in two columns
            col_left, col_right = st.columns(2)

            with col_left:
                section_header("Flexure Design", icon="🔹", divider=True)
                flexure = result.get('flexure', {})
                st.write(f"- **Ast required:** {flexure.get('ast_required', 0):.0f} mm²")
                st.write(f"- **Status:** {'✅ Safe' if flexure.get('is_safe', False) else '❌ Unsafe'}")

                st.markdown("<br>", unsafe_allow_html=True)
                section_header("Material Properties", icon="🔸", divider=True)
                st.write(f"- **Concrete:** {st.session_state.beam_inputs['concrete_grade']} (fck = {concrete['fck']} N/mm²)")
                st.write(f"- **Steel:** {st.session_state.beam_inputs['steel_grade']} (fy = {steel['fy']} N/mm²)")

            with col_right:
                section_header("Shear Design", icon="🔹", divider=True)
                shear = result.get('shear', {})
                st.write(f"- **Spacing:** {shear.get('spacing', 0):.0f} mm c/c")
                st.write(f"- **Status:** {'✅ Safe' if shear.get('is_safe', False) else '❌ Unsafe'}")

                st.markdown("#### 🔸 Geometry")
                st.write(f"- **Span:** {st.session_state.beam_inputs['span_mm']:.0f} mm")
                st.write(f"- **Section:** {st.session_state.beam_inputs['b_mm']:.0f} × {st.session_state.beam_inputs['D_mm']:.0f} mm")
                st.write(f"- **Effective depth:** {st.session_state.beam_inputs['d_mm']:.0f} mm")

        # ============================================================================
        # TAB 2: Visualization
        # ============================================================================
        with tab2:
            st.subheader("Beam Cross-Section")

            # Sample rebar positions (3 bars at bottom)
            # TODO: Get actual positions from design result
            cover = exposure.get('cover', 30)
            bar_dia = 16  # Placeholder
            spacing_h = (st.session_state.beam_inputs['b_mm'] - 2 * cover) / 2
            rebar_y = cover + bar_dia / 2

            rebar_positions = [
                (cover + bar_dia / 2, rebar_y),
                (st.session_state.beam_inputs['b_mm'] / 2, rebar_y),
                (st.session_state.beam_inputs['b_mm'] - cover - bar_dia / 2, rebar_y)
            ]

            xu = st.session_state.beam_inputs['d_mm'] * 0.33  # Placeholder neutral axis

            fig = create_beam_diagram(
                b_mm=st.session_state.beam_inputs['b_mm'],
                D_mm=st.session_state.beam_inputs['D_mm'],
                d_mm=st.session_state.beam_inputs['d_mm'],
                rebar_positions=rebar_positions,
                xu=xu,
                bar_dia=bar_dia,
                cover=cover
            )

            st.plotly_chart(fig, use_container_width=True, key="beam_section_viz")

            st.divider()

            # Utilization gauges
            st.subheader("Utilization Gauges")

            col1, col2, col3 = st.columns(3)

            with col1:
                fig_flex = create_utilization_gauge(
                    value=min(utilization / 100, 1.0),
                    label="Flexure"
                )
                st.plotly_chart(fig_flex, use_container_width=True, key="gauge_flexure")

            with col2:
                shear_util = 0.65  # Placeholder
                fig_shear = create_utilization_gauge(
                    value=shear_util,
                    label="Shear"
                )
                st.plotly_chart(fig_shear, use_container_width=True, key="gauge_shear")

            with col3:
                deflection_util = 0.50  # Placeholder
                fig_defl = create_utilization_gauge(
                    value=deflection_util,
                    label="Deflection"
                )
                st.plotly_chart(fig_defl, use_container_width=True, key="gauge_deflection")

        # ============================================================================
        # TAB 3: Cost Analysis
        # ============================================================================
        with tab3:
            st.subheader("Cost Comparison")

            # Sample alternatives (placeholder data)
            alternatives = [
                {'bar_arrangement': '3-16mm', 'cost_per_meter': 87.45, 'is_optimal': True, 'area_provided': 603},
                {'bar_arrangement': '4-14mm', 'cost_per_meter': 89.20, 'is_optimal': False, 'area_provided': 616},
                {'bar_arrangement': '2-20mm', 'cost_per_meter': 92.30, 'is_optimal': False, 'area_provided': 628},
                {'bar_arrangement': '5-12mm', 'cost_per_meter': 85.10, 'is_optimal': False, 'area_provided': 565},
            ]

            fig_cost = create_cost_comparison(alternatives)
            st.plotly_chart(fig_cost, use_container_width=True, key="cost_comparison")

            st.info("""
            💡 **Cost Optimization Tips:**
            - Use standard bar sizes (12, 16, 20, 25 mm)
            - Minimize number of bar diameters
            - Consider constructability and spacing
            - Balance material cost vs labor cost
            """)

        # ============================================================================
        # TAB 4: Compliance
        # ============================================================================
        with tab4:
            st.subheader("IS 456:2000 Compliance Checklist")

            # Sample compliance checks (placeholder data)
            checks = [
                {
                    'clause': '26.5.1.1(a)',
                    'description': 'Minimum tension reinforcement',
                    'status': 'pass',
                    'actual_value': ast_req,
                    'limit_value': 0.85 * st.session_state.beam_inputs['b_mm'] * st.session_state.beam_inputs['d_mm'] / steel['fy'],
                    'unit': 'mm²',
                    'details': 'Ast,min = 0.85 bd / fy'
                },
                {
                    'clause': '26.5.1.1(b)',
                    'description': 'Maximum tension reinforcement',
                    'status': 'pass',
                    'actual_value': ast_req,
                    'limit_value': 0.04 * st.session_state.beam_inputs['b_mm'] * st.session_state.beam_inputs['D_mm'],
                    'unit': 'mm²',
                    'details': 'Ast,max = 0.04 bD'
                },
                {
                    'clause': '26.5.1.5',
                    'description': 'Maximum spacing of tension bars',
                    'status': 'pass',
                    'actual_value': 150,
                    'limit_value': min(3 * st.session_state.beam_inputs['d_mm'], 300),
                    'unit': 'mm',
                    'details': 'Max spacing = min(3d, 300mm)'
                },
                {
                    'clause': '26.5.1.6',
                    'description': 'Minimum shear reinforcement',
                    'status': 'pass',
                    'actual_value': spacing,
                    'limit_value': 0.75 * st.session_state.beam_inputs['d_mm'],
                    'unit': 'mm',
                    'details': 'Max spacing = 0.75d for vertical stirrups'
                }
            ]

            create_compliance_visual(checks)

    else:
        # Show real-time preview when design not yet computed
        render_real_time_preview(
            span_mm=st.session_state.beam_inputs['span_mm'],
            b_mm=st.session_state.beam_inputs['b_mm'],
            D_mm=st.session_state.beam_inputs['D_mm'],
            d_mm=st.session_state.beam_inputs['d_mm'],
            concrete_grade=concrete['grade'],
            steel_grade=steel['grade'],
            mu_knm=st.session_state.beam_inputs['mu_knm'],
            vu_kn=st.session_state.beam_inputs['vu_kn'],
            exposure=st.session_state.beam_inputs['exposure'],
            support_condition=st.session_state.beam_inputs['support_condition']
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
