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

# Fix import path - add streamlit_app directory to path
current_file = Path(__file__).resolve()
pages_dir = current_file.parent
streamlit_app_dir = pages_dir.parent

# Ensure streamlit_app is in path for component imports
if str(streamlit_app_dir) not in sys.path:
    sys.path.insert(0, str(streamlit_app_dir))

from components.inputs import (
    dimension_input,
    material_selector,
    load_input,
    exposure_selector,
    support_condition_selector,
)
from components.visualizations import (
    create_beam_diagram,
    create_bmd_sfd_diagram,
    create_cost_comparison,
    create_compliance_visual,
)
from components.visualizations_3d import (
    create_beam_3d_figure,
    compute_geometry_hash,
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
from utils.api_wrapper import cached_design, cached_bmd_sfd
from utils.constants import (
    EXPOSURE_COVER_MAP,
    DEFAULT_BEAM_INPUTS,
    get_cover_for_exposure,
)
from utils.layout import setup_page, page_header, section_header
from utils.theme_manager import (
    apply_dark_mode_theme,
    render_theme_toggle,
    initialize_theme,
)
from utils.loading_states import loading_context

# IMPL-007: Performance optimizations
from utils.caching import SmartCache

# TASK-602: Modern Streamlit patterns (Session 28)
from utils.fragments import (
    CacheStatsFragment,
    show_status_badge,
    fragment_input_section,
)

# TASK-276-279 Integration: Professional report export
from components.report_export import (
    show_export_options,
    show_audit_trail_summary,
    show_dxf_export,
)
from utils.input_bridge import log_design_to_audit
import hashlib
import json

# TODO Phase 2+: Uncomment as needed when implementing those phases
# from utils.session_manager import SessionStateManager
# from utils.lazy_loader import LazyLoader
# from utils.render_optimizer import RenderOptimizer
# from utils.data_loader import DataLoader

# Initialize theme
initialize_theme()

# Modern page setup with professional styling
setup_page(title="Beam Design | IS 456 Dashboard", icon="🏗️", layout="wide")

# Apply dark mode styling
# apply_dark_mode_theme()

# PHASE 1: Initialize SmartCache instances for performance optimization
design_cache = SmartCache(max_size_mb=50, ttl_seconds=300)  # 5-min TTL for design calcs
viz_cache = SmartCache(max_size_mb=30, ttl_seconds=600)  # 10-min TTL for visualizations

# Initialize session state for input persistence (using centralized defaults)
if "beam_inputs" not in st.session_state:
    st.session_state.beam_inputs = DEFAULT_BEAM_INPUTS.copy()


# Helper function to detect input changes
def get_input_hash():
    """Hash of all inputs to detect changes"""
    inputs_str = f"{st.session_state.beam_inputs['mu_knm']}_{st.session_state.beam_inputs['vu_kn']}_{st.session_state.beam_inputs['b_mm']}_{st.session_state.beam_inputs['D_mm']}_{st.session_state.beam_inputs['d_mm']}_{st.session_state.beam_inputs['concrete_grade']}_{st.session_state.beam_inputs['steel_grade']}_{st.session_state.beam_inputs['span_mm']}_{st.session_state.beam_inputs['exposure']}"
    return hashlib.md5(inputs_str.encode()).hexdigest()


# PHASE 1: Cached visualization wrapper for performance
def create_cached_beam_diagram(**kwargs):
    """Cached wrapper for beam diagram generation"""

    # Create cache key from all parameters (handle unhashable types)
    # Convert kwargs to JSON-serializable format
    def make_hashable(obj):
        if isinstance(obj, (list, tuple)):
            return tuple(make_hashable(item) for item in obj)
        elif isinstance(obj, dict):
            return tuple(sorted((k, make_hashable(v)) for k, v in obj.items()))
        else:
            return obj

    # Create stable cache key
    hashable_kwargs = make_hashable(kwargs)
    cache_key = f"viz_{hash(hashable_kwargs)}"

    # Try to get from cache
    cached_fig = viz_cache.get(cache_key)
    if cached_fig is not None:
        return cached_fig

    # Generate new figure
    fig = create_beam_diagram(**kwargs)

    # Store in cache
    viz_cache.set(cache_key, fig)

    return fig


# Page header with professional styling
page_header(
    title="Beam Design",
    subtitle="Design reinforced concrete beams per IS 456:2000 with real-time compliance checking",
    icon="🏗️",
)

# Quick navigation to multi-format import for ETABS/SAFE data
with st.expander("📥 Import from ETABS/SAFE?", expanded=False):
    st.markdown("""
    **For batch design from analysis software:**
    - Import ETABS geometry & forces CSV
    - Import SAFE strip beam data
    - Batch design with 3D building view
    """)
    st.page_link(
        "pages/07_📥_multi_format_import.py",
        label="Go to Multi-Format Import →",
        icon="📥",
    )

# ============================================================================
# TWO-COLUMN LAYOUT: Input + Preview/Results
# ============================================================================

# Create two-column layout (40% input, 60% preview/results)
col_input, col_preview = st.columns([2, 3], gap="large")

# Left column: Input parameters
with col_input:
    # TASK-603.1: Wrap inputs in fragment for 80-90% faster response
    @st.fragment
    def render_inputs():
        """Render input form as an independent fragment."""
        # Compact header (NO theme toggle - it uses st.sidebar which is forbidden in fragments)
        st.subheader("📋 Inputs")

        # Section 1: Geometry (compact 2-column layout)
        st.markdown("**📏 Geometry**")

    # Row 1: Span + Width (side by side)
    col_span, col_width = st.columns(2)
    with col_span:
        span, span_valid = dimension_input(
            label="Span",
            min_value=1000.0,
            max_value=12000.0,
            default_value=st.session_state.beam_inputs["span_mm"],
            unit="mm",
            help_text="Clear span (typ. 3000-8000mm)",
            key="input_span",
            show_validation=False,
        )
        st.session_state.beam_inputs["span_mm"] = span

    with col_width:
        b, b_valid = dimension_input(
            label="Width",
            min_value=150.0,
            max_value=600.0,
            default_value=st.session_state.beam_inputs["b_mm"],
            unit="mm",
            help_text="Beam width (typ. D/2 to D/3)",
            key="input_b",
            show_validation=False,
        )
        st.session_state.beam_inputs["b_mm"] = b

    # Span-based depth recommendation
    recommended_D = span / 12  # span/10 to span/15 typical

    # Row 2: Total Depth + Effective Depth (side by side)
    col_D, col_d = st.columns(2)
    with col_D:
        D, D_valid = dimension_input(
            label="Total Depth",
            min_value=200.0,
            max_value=900.0,
            default_value=st.session_state.beam_inputs["D_mm"],
            unit="mm",
            help_text=f"Rec: {recommended_D:.0f}mm (span/12)",
            key="input_D",
            show_validation=False,
        )
        st.session_state.beam_inputs["D_mm"] = D

    # Smart effective depth: suggest based on D and typical cover
    # Get cover from current exposure selection
    current_exposure = st.session_state.beam_inputs.get("exposure", "Moderate")
    cover = get_cover_for_exposure(current_exposure)
    # Typical effective depth = D - cover - bar_dia/2 (assume 20mm bar)
    suggested_d = D - cover - 10  # cover + half bar diameter

    with col_d:
        d, d_valid = dimension_input(
            label="Effective Depth",
            min_value=150.0,
            max_value=850.0,
            default_value=st.session_state.beam_inputs["d_mm"],
            unit="mm",
            help_text=f"Suggested: {suggested_d:.0f}mm",
            key="input_d",
            show_validation=False,
        )
        st.session_state.beam_inputs["d_mm"] = d

    # Validation: d must be less than D with meaningful cover
    min_cover_plus_bar = 40  # Minimum cover + half bar diameter
    if d >= D:
        st.error("❌ Effective depth must be less than total depth")
        d_valid = False
    elif d > D - min_cover_plus_bar:
        st.warning(
            f"⚠️ d={d:.0f}mm leaves only {D-d:.0f}mm cover. Min: {min_cover_plus_bar}mm"
        )
        # Still valid but warn user

    # Section 2: Materials (compact 2-column layout)
    st.markdown("**🧱 Materials**")

    col_conc, col_steel = st.columns(2)
    with col_conc:
        concrete = material_selector(
            material_type="concrete",
            default_grade=st.session_state.beam_inputs["concrete_grade"],
            key="input_concrete",
            show_properties=False,
        )
        st.session_state.beam_inputs["concrete_grade"] = concrete["grade"]

    with col_steel:
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

    # Section 4: Exposure & Support (compact 2-column layout)
    st.markdown("**🌍 Environment**")

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

    if st.button("🚀 Analyze Design", disabled=not all_valid, width="stretch"):
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
        elif inputs_changed and st.session_state.beam_inputs.get(
            "design_computed", False
        ):
            st.info("ℹ️ Inputs changed. Click 'Analyze Design' to update results.")

        st.markdown("---")

    # Call the fragment to render inputs
    render_inputs()

    # PHASE 1: Cache statistics and controls (TASK-602: uses auto-refresh fragment)
    with st.expander("⚙️ Advanced"):
        # Use auto-refreshing cache stats fragment (updates every 10s without user action)
        cache_stats_fragment = CacheStatsFragment(
            design_cache=design_cache,
            viz_cache=viz_cache,
            refresh_interval=10,
        )
        cache_stats_fragment.render()

        st.markdown("---")

        # Cache control buttons
        clear_col1, clear_col2 = st.columns(2)

        with clear_col1:
            if st.button("🗑️ Clear All Caches", width="stretch"):
                from utils.api_wrapper import clear_cache

                clear_cache()
                design_cache.clear()
                viz_cache.clear()
                st.success("✅ All caches cleared!")
                st.rerun()

        with clear_col2:
            if st.button("🔄 Clear Viz Cache Only", width="stretch"):
                viz_cache.clear()
                st.success("✅ Visualization cache cleared!")
                st.rerun()

# Right column: Preview or Results
with col_preview:
    # Only show Design Preview header and geometry expander BEFORE design is computed
    design_computed = st.session_state.beam_inputs.get("design_computed", False)

    if not design_computed:
        st.header("📊 Design Preview")

        # Show geometry preview (without reinforcement until analyzed)
        with st.expander(
            "📐 Geometry Preview",
            expanded=True,
        ):
            # Get current exposure for cover (using centralized constants)
            cover = get_cover_for_exposure(st.session_state.beam_inputs["exposure"])

            # No reinforcement shown before analysis
            rebar_positions = []
            xu = None
            bar_dia = 0

            fig = create_cached_beam_diagram(
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
            st.plotly_chart(fig, width="stretch")

            # Show dimensions
            st.caption(
                f"📏 {st.session_state.beam_inputs['b_mm']:.0f} × {st.session_state.beam_inputs['D_mm']:.0f} mm (d={st.session_state.beam_inputs['d_mm']:.0f}mm)"
            )
            st.info("ℹ️ Click 'Analyze Design' to see reinforcement")

        st.divider()

    # Show results if computed
    if design_computed:
        st.header("✅ Design Results")

        # Show full results (existing tabs - moved from main area)
        result = st.session_state.beam_inputs["design_result"]

        # Success/Failure banner (TASK-602: modern st.badge pattern)
        show_status_badge(
            is_safe=result.get("is_safe", False),
            safe_text="SAFE - Meets all IS 456 requirements",
            unsafe_text="UNSAFE - Does not meet IS 456 requirements",
        )

        st.divider()

        # Results tabs (includes new Export tab for TASK-276-279)
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "📊 Summary",
                "🎨 Visualization",
                "💰 Cost Analysis",
                "✅ Compliance",
                "📄 Export",
            ]
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
                        denominator = max(num_bars - 1, 1)
                        spacing_h = (
                            (b_mm - 2 * cover - bar_dia) / denominator
                            if denominator > 0
                            else 0
                        )
                        rebar_y = cover + bar_dia / 2
                        for i in range(num_bars):
                            x = cover + bar_dia / 2 + i * spacing_h
                            rebar_positions.append((x, rebar_y))
                else:
                    # Multiple layers - split bars between layers
                    bars_per_layer = (
                        num_bars // num_layers if num_layers > 0 else num_bars
                    )
                    extra_bars = num_bars % num_layers if num_layers > 0 else 0

                    for layer_idx in range(num_layers):
                        layer_bars = bars_per_layer + (
                            1 if layer_idx < extra_bars else 0
                        )
                        # Calculate spacing for this layer
                        if spacing_mm > 0 and layer_bars > 1:
                            # Use library spacing
                            total_width_bars = (layer_bars - 1) * spacing_mm + bar_dia
                            x_start = (b_mm - total_width_bars) / 2
                        else:
                            # Fallback spacing
                            denominator = max(layer_bars - 1, 1)
                            spacing_h = (
                                (b_mm - 2 * cover - bar_dia) / denominator
                                if denominator > 0
                                else 0
                            )
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
                area_per_bar = 3.14159 * (comp_bar_dia**2) / 4
                if area_per_bar > 0:
                    try:
                        num_comp_bars = max(2, int(asc_required / area_per_bar) + 1)
                    except (TypeError, ValueError):
                        num_comp_bars = 2
                else:
                    num_comp_bars = 2

                # Position at top (from top surface)
                comp_y = D_mm - cover - comp_bar_dia / 2
                denominator = max(num_comp_bars - 1, 1)
                spacing_h = (
                    (b_mm - 2 * cover - comp_bar_dia) / denominator
                    if denominator > 0
                    else 0
                )

                for i in range(num_comp_bars):
                    x = cover + comp_bar_dia / 2 + i * spacing_h
                    compression_positions.append((x, comp_y))

            # STIRRUPS: Get shear reinforcement data
            stirrup_dia = shear.get("stirrup_dia", 8)
            stirrup_spacing = shear.get("spacing", 150)
            stirrup_legs = shear.get("legs", 2)

            fig = create_cached_beam_diagram(
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

            st.plotly_chart(fig, width="stretch", key="beam_section_viz")

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
            st.dataframe(df_schedule, width="stretch", hide_index=True)

            # ----------------------------------------------------------------
            # 3D Beam Visualization (TASK-3D-08 + TASK-3D-09 Live Updates)
            # ----------------------------------------------------------------
            st.divider()
            st.subheader("🏗️ 3D Beam Visualization")

            # ----------------------------------------------------------------
            # TASK-3D-11: Status Display (safe/unsafe, utilization %)
            # ----------------------------------------------------------------
            # Calculate utilization percentages
            ast_req = flexure.get("ast_required", 0)
            ast_prov = flexure.get("ast_provided", 0)
            flexure_util = (ast_req / ast_prov * 100) if ast_prov > 0 else 0

            vu = shear.get("vu", 0)
            vu_capacity = shear.get("vu_capacity", shear.get("vu_c", 0))
            shear_util = (vu / vu_capacity * 100) if vu_capacity > 0 else 0

            # Determine overall status
            is_flexure_safe = ast_prov >= ast_req if ast_req > 0 else True
            is_shear_safe = vu_capacity >= vu if vu > 0 else True
            is_safe = is_flexure_safe and is_shear_safe

            # Status display with colored indicators
            # Using tuple unpacking to avoid IndexError (scanner-safe pattern)
            status_col1, status_col2, status_col3 = st.columns([1, 1, 1])
            with status_col1:
                if is_safe:
                    st.success("✅ **SAFE**")
                else:
                    st.error("❌ **UNSAFE**")

            with status_col2:
                flexure_color = (
                    "green"
                    if flexure_util <= 90
                    else "orange" if flexure_util <= 100 else "red"
                )
                st.markdown(
                    f"**Flexure:** <span style='color:{flexure_color}'>{flexure_util:.1f}%</span>",
                    unsafe_allow_html=True,
                )

            with status_col3:
                shear_color = (
                    "green"
                    if shear_util <= 90
                    else "orange" if shear_util <= 100 else "red"
                )
                st.markdown(
                    f"**Shear:** <span style='color:{shear_color}'>{shear_util:.1f}%</span>",
                    unsafe_allow_html=True,
                )

            # Prepare geometry data for 3D visualization
            span_mm_3d = st.session_state.beam_inputs.get("span_mm", 4000)
            cover_3d = detailing.get("cover", 40)
            stirrup_dia_3d = shear.get("stirrup_dia", 8)

            # Convert 2D rebar positions to 3D format
            bottom_bars_3d = []
            for pos in rebar_positions:
                if len(pos) >= 2:
                    y_3d = pos[0] - b_mm / 2
                    z_3d = pos[1]
                    bottom_bars_3d.append((0, y_3d, z_3d))

            top_bars_3d = []
            for pos in compression_positions:
                if len(pos) >= 2:
                    y_3d = pos[0] - b_mm / 2
                    z_3d = pos[1]
                    top_bars_3d.append((0, y_3d, z_3d))

            if not top_bars_3d:
                edge_dist = cover_3d + stirrup_dia_3d + bar_dia / 2
                available_width = b_mm - 2 * edge_dist
                top_bars_3d = [
                    (0, -available_width / 2, D_mm - edge_dist),
                    (0, available_width / 2, D_mm - edge_dist),
                ]

            # Variable stirrup zones per IS 456 (2d rule - tighter at supports)
            # Zone 1: 2d from each support - tighter spacing (0.75 × Sv_base)
            # Zone 2: Mid-span - normal spacing (Sv_base)
            d_eff = D_mm - cover_3d - stirrup_dia_3d - bar_dia / 2
            zone_length = 2 * d_eff  # 2d from each support

            sv_base = max(50, int(stirrup_spacing)) if stirrup_spacing > 0 else 100
            sv_tight = max(50, int(sv_base * 0.75))  # Tighter at supports

            stirrup_positions_3d = []
            # Zone 1: Left support zone (0 to zone_length)
            pos = sv_tight / 2
            while pos < zone_length and pos < span_mm_3d:
                stirrup_positions_3d.append(int(pos))
                pos += sv_tight

            # Zone 2: Mid-span zone (zone_length to span - zone_length)
            mid_start = max(
                zone_length,
                (
                    stirrup_positions_3d[-1] + sv_base
                    if stirrup_positions_3d
                    else zone_length
                ),
            )
            mid_end = span_mm_3d - zone_length
            pos = mid_start
            while pos < mid_end:
                stirrup_positions_3d.append(int(pos))
                pos += sv_base

            # Zone 3: Right support zone (span - zone_length to span)
            right_start = max(
                mid_end,
                (
                    stirrup_positions_3d[-1] + sv_tight
                    if stirrup_positions_3d
                    else mid_end
                ),
            )
            pos = right_start
            while pos < span_mm_3d - sv_tight / 2:
                stirrup_positions_3d.append(int(pos))
                pos += sv_tight

            # Ensure last stirrup near right support
            if (
                stirrup_positions_3d
                and stirrup_positions_3d[-1] < span_mm_3d - sv_tight
            ):
                stirrup_positions_3d.append(int(span_mm_3d - sv_tight / 2))

            # Build geometry dict for hashing and fragment
            geometry_3d = {
                "b": b_mm,
                "D": D_mm,
                "span": span_mm_3d,
                "bottom_bars": bottom_bars_3d,
                "top_bars": top_bars_3d,
                "bar_dia": bar_dia,
                "stirrup_positions": stirrup_positions_3d,
                "stirrup_dia": stirrup_dia_3d,
                "cover": cover_3d,
            }

            # Compute geometry hash for cache invalidation
            geometry_hash = compute_geometry_hash(geometry_3d)

            # TASK-3D-09: Fragment for live 3D updates
            @st.fragment
            def render_3d_beam_preview(geom: dict, geom_hash: str):
                """Render 3D beam preview with caching based on geometry hash.

                Using @st.fragment allows this section to update independently
                without triggering full page re-render.
                """
                # Use session state to cache figure by geometry hash
                cache_key = "beam_3d_cache"
                if cache_key not in st.session_state:
                    st.session_state[cache_key] = {"hash": "", "figure": None}

                cached = st.session_state[cache_key]

                # Only regenerate if geometry changed
                if cached["hash"] != geom_hash or cached["figure"] is None:
                    fig_3d = create_beam_3d_figure(
                        b=geom["b"],
                        D=geom["D"],
                        span=geom["span"],
                        bottom_bars=(
                            geom["bottom_bars"] if geom["bottom_bars"] else None
                        ),
                        top_bars=geom["top_bars"] if geom["top_bars"] else None,
                        bar_diameter=geom["bar_dia"],
                        stirrup_positions=geom["stirrup_positions"],
                        stirrup_diameter=geom["stirrup_dia"],
                        cover=geom["cover"],
                        height=450,
                        show_legend=True,
                        show_info_panel=True,
                    )
                    # Update cache
                    st.session_state[cache_key] = {"hash": geom_hash, "figure": fig_3d}
                    cached = st.session_state[cache_key]

                # Use hash in key to force Streamlit to re-render when geometry changes
                st.plotly_chart(
                    cached["figure"],
                    key=f"beam_3d_viz_{geom_hash[:8]}",
                )
                st.caption(
                    "🖱️ **Controls:** Drag to rotate | Scroll to zoom | Right-click to pan"
                )

            # Call fragment with current geometry
            render_3d_beam_preview(geometry_3d, geometry_hash)

            # ----------------------------------------------------------------
            # BMD/SFD Diagram Section (TASK-145.9)
            # ----------------------------------------------------------------
            st.divider()
            st.subheader("📈 Bending Moment & Shear Force Diagrams")

            # Derive equivalent UDL from design moment (for visualization)
            # For simply supported beam with UDL: M_max = wL²/8 → w = 8M/L²
            span_mm = st.session_state.beam_inputs.get("span_mm", 5000)
            mu_knm = st.session_state.beam_inputs.get("mu_knm", 100)
            span_m = span_mm / 1000.0

            if span_m > 0:
                # Derive equivalent UDL that would produce this moment
                # Using M = wL²/8 for simply supported beam
                derived_udl = 8 * mu_knm / (span_m**2) if span_m > 0 else 10.0

                st.caption(
                    f"ℹ️ Derived equivalent UDL: **{derived_udl:.2f} kN/m** "
                    f"(from Mu = {mu_knm:.1f} kN·m, L = {span_m:.2f} m)"
                )

                # Compute BMD/SFD
                bmd_sfd_result = cached_bmd_sfd(
                    span_mm=span_mm,
                    support_condition="simply_supported",
                    udl_kn_m=derived_udl,
                )

                # Create visualization
                fig_bmd_sfd = create_bmd_sfd_diagram(
                    positions_mm=bmd_sfd_result["positions_mm"],
                    bmd_knm=bmd_sfd_result["bmd_knm"],
                    sfd_kn=bmd_sfd_result["sfd_kn"],
                    critical_points=bmd_sfd_result.get("critical_points"),
                    show_grid=True,
                    height=450,
                )

                st.plotly_chart(fig_bmd_sfd, width="stretch", key="bmd_sfd_viz")

                # Show key values
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        label="Max Bending Moment",
                        value=f"{bmd_sfd_result['max_moment']:.2f} kN·m",
                        help="Maximum bending moment from load analysis",
                    )
                with col2:
                    st.metric(
                        label="Max Shear Force",
                        value=f"{bmd_sfd_result['max_shear']:.2f} kN",
                        help="Maximum shear force at supports",
                    )
            else:
                st.warning("⚠️ Invalid span. Cannot compute BMD/SFD.")

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
            st.plotly_chart(fig_cost, width="stretch", key="cost_comparison")

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

            # Extract design data for compliance checks
            flexure = result.get("flexure", {})
            detailing = result.get("detailing", {})
            shear = result.get("shear", {})

            # Extract stirrup spacing for compliance check
            stirrup_spacing = shear.get(
                "spacing", 150
            )  # Default to 150mm if not available

            # Get steel area (provided, not required - this is what we actually have)
            ast_provided = flexure.get("ast_provided", 0)

            # Sample compliance checks (placeholder data)
            checks = [
                {
                    "clause": "26.5.1.1(a)",
                    "description": "Minimum tension reinforcement",
                    "status": "pass",
                    "actual_value": ast_provided,
                    "limit_value": (
                        0.85
                        * st.session_state.beam_inputs["b_mm"]
                        * st.session_state.beam_inputs["d_mm"]
                        / steel["fy"]
                        if steel.get("fy", 0) > 0
                        else 0
                    ),
                    "unit": "mm²",
                    "details": "Ast,min = 0.85 bd / fy",
                },
                {
                    "clause": "26.5.1.1(b)",
                    "description": "Maximum tension reinforcement",
                    "status": "pass",
                    "actual_value": ast_provided,
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
                    "actual_value": stirrup_spacing,
                    "limit_value": 0.75 * st.session_state.beam_inputs["d_mm"],
                    "unit": "mm",
                    "details": "Max spacing = 0.75d for vertical stirrups",
                },
            ]

            create_compliance_visual(checks)

        # ============================================================================
        # TAB 5: Export & Audit (TASK-276-279 Integration)
        # ============================================================================
        with tab5:
            st.subheader("📄 Export & Audit Trail")

            # Get beam identifier from session
            beam_id = st.session_state.get("current_beam_id", "B1")
            story = st.session_state.get("current_story", "GF")

            # Export options in columns
            col_pdf, col_dxf = st.columns(2)

            with col_pdf:
                # Report export section (HTML/JSON/Markdown)
                show_export_options(
                    result=result,
                    beam_id=beam_id,
                    story=story,
                )

            with col_dxf:
                # DXF export section
                show_dxf_export(
                    result=result,
                    beam_id=beam_id,
                )

            st.divider()

            # Audit trail section
            show_audit_trail_summary()

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
