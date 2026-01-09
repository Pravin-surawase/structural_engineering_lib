"""
Cost Optimizer Page
====================

Interactive cost optimization page for beam designs.

Features:
- Cost vs utilization scatter plot
- Sortable comparison table
- CSV export functionality
- Session state integration with Beam Design
- Manual input fallback

Author: STREAMLIT UI SPECIALIST (Agent 6)
Phase: STREAMLIT-IMPL-005 | UI-002: Page Layout Redesign
"""

import io
import itertools
import logging
import math
import traceback
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    from structural_lib.costing import calculate_beam_cost, CostProfile, STEEL_DENSITY_KG_PER_M3
    HAS_COSTING = True
except ImportError:
    HAS_COSTING = False
    STEEL_DENSITY_KG_PER_M3 = 7850000.0  # Fallback value

from utils.api_wrapper import cached_smart_analysis
from utils.layout import setup_page, page_header
from utils.theme_manager import apply_dark_mode_theme, initialize_theme
from utils.cost_optimizer_validators import (
    validate_beam_inputs,
    validate_design_result,
    safe_divide,
    safe_format_currency,
    safe_format_percent,
)
from utils.cost_optimizer_error_boundary import (
    error_boundary,
    SafeSessionState,
)

# Setup logging
logger = logging.getLogger(__name__)

# Initialize theme
initialize_theme()

# Modern page setup
setup_page(title="Cost Optimizer - IS 456 Beam Design", icon="💰", layout="wide")

# Apply dark mode styling
apply_dark_mode_theme()


def initialize_session_state():
    """Initialize session state for cost optimizer."""
    safe_state = SafeSessionState()

    if not safe_state.exists("cost_results"):
        safe_state.set("cost_results", None)
    if not safe_state.exists("cost_comparison_data"):
        safe_state.set("cost_comparison_data", [])


# Module-level constants (moved out of function)
CONCRETE_GRADE_MAP = {"M20": 20, "M25": 25, "M30": 30, "M35": 35, "M40": 40}
STEEL_GRADE_MAP = {"Fe415": 415, "Fe500": 500, "Fe550": 550}


def get_beam_design_inputs() -> Optional[dict]:
    """Get inputs from Beam Design page session state if available."""
    safe_state = SafeSessionState()

    # Check if beam_inputs exists (from beam design page)
    if not safe_state.exists("beam_inputs"):
        return None

    beam = safe_state.get_dict("beam_inputs")
    if not beam:
        return None

    inputs = {
        "mu_knm": beam.get("mu_knm", 120.0),
        "vu_kn": beam.get("vu_kn", 80.0),
        "b_mm": beam.get("b_mm", 300.0),
        "D_mm": beam.get("D_mm", 500.0),
        "d_mm": beam.get("d_mm", 450.0),
        "span_mm": beam.get("span_mm", 5000.0),
        "fck_nmm2": CONCRETE_GRADE_MAP.get(beam.get("concrete_grade", "M25"), 25),
        "fy_nmm2": STEEL_GRADE_MAP.get(beam.get("steel_grade", "Fe500"), 500),
    }

    # Validate inputs before returning
    validation = validate_beam_inputs(inputs)
    if not validation:
        logger.warning(f"Invalid beam inputs from session state: {validation.errors}")
        # Still return for backward compatibility, but log the issue

    return inputs


def create_cost_scatter(comparison_data: list[dict]) -> go.Figure:
    """
    Create cost vs utilization scatter plot.

    Args:
        comparison_data: List of design alternatives with cost and utilization

    Returns:
        Plotly Figure object
    """
    if not comparison_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No data to display",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        return fig

    df = pd.DataFrame(comparison_data)

    # Add status column for color coding
    df["Status"] = df.apply(
        lambda row: "Optimal" if row.get("is_optimal", False) else "Alternative",
        axis=1,
    )

    fig = px.scatter(
        df,
        x="utilization_ratio",
        y="total_cost",
        color="Status",
        size="steel_area_mm2",
        hover_data={
            "b_mm": ":.0f",
            "D_mm": ":.0f",
            "total_cost": ":,.0f",
            "utilization_ratio": ":.2%",
            "steel_area_mm2": ":.0f",
        },
        labels={
            "utilization_ratio": "Utilization Ratio",
            "total_cost": "Total Cost (INR)",
            "steel_area_mm2": "Steel Area (mm²)",
        },
        title="Cost vs Utilization Trade-off",
        color_discrete_map={"Optimal": "#2e7d32", "Alternative": "#1976d2"},
    )

    fig.update_layout(
        xaxis=dict(tickformat=".0%", range=[0, 1.1]),
        yaxis=dict(tickformat=","),
        hovermode="closest",
        height=500,
    )

    fig.update_traces(marker=dict(line=dict(width=1, color="white")))

    return fig


def create_comparison_table(comparison_data: list[dict]) -> pd.DataFrame:
    """
    Create sortable comparison table.

    Args:
        comparison_data: List of design alternatives

    Returns:
        Pandas DataFrame formatted for display
    """
    if not comparison_data:
        return pd.DataFrame()

    df = pd.DataFrame(comparison_data)

    # Select and rename columns for display
    display_columns = {
        "bar_config": "Bar Config",
        "steel_area_mm2": "Steel Area (mm²)",
        "steel_kg": "Steel Weight (kg)",
        "total_cost": "Total Cost",
        "steel_cost": "Steel Cost",
        "utilization_ratio": "Area Ratio",
    }

    available_columns = [col for col in display_columns.keys() if col in df.columns]
    df_display = df[available_columns].copy()
    df_display.columns = [display_columns[col] for col in available_columns]

    # Format numeric columns
    if "Area Ratio" in df_display.columns:
        df_display["Area Ratio"] = df_display["Area Ratio"].apply(
            lambda x: f"{x:.2%}"
        )

    for col in df_display.columns:
        if "Cost" in col:
            df_display[col] = df_display[col].apply(lambda x: f"₹{x:,.0f}")
        if "Steel Area (mm²)" in col:
            df_display[col] = df_display[col].apply(lambda x: f"{x:,.0f}")
        if "Steel Weight (kg)" in col:
            df_display[col] = df_display[col].apply(lambda x: f"{x:.2f}")

    return df_display


def export_to_csv(comparison_data: list[dict]) -> bytes:
    """
    Export comparison data to CSV format.

    Args:
        comparison_data: List of design alternatives

    Returns:
        CSV data as bytes
    """
    df = pd.DataFrame(comparison_data)
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue().encode("utf-8")


@error_boundary(fallback_value={"analysis": None, "comparison": []}, show_error=True)
def run_cost_optimization(inputs: dict) -> dict:
    """
    Run cost optimization analysis using bar alternatives.

    Args:
        inputs: Design input parameters

    Returns:
        Dictionary with optimization results and comparison data
    """
    # Validate inputs first
    validation = validate_beam_inputs(inputs)
    if not validation:
        for error in validation.errors:
            st.error(f"❌ Input validation failed: {error}")
        return {"analysis": None, "comparison": []}

    # Use module-level imports (already imported at top)
    safe_state = SafeSessionState()

    # Check if we have design results from beam design page
    flexure = None
    if safe_state.exists("design_results"):
        design_result = safe_state.get_dict("design_results")
        if design_result:
            flexure = design_result.get("flexure")

    # If not available, run new analysis
    if not flexure:
        result = cached_smart_analysis(
            mu_knm=inputs.get("mu_knm"),
            vu_kn=inputs.get("vu_kn", 0.0),
            b_mm=inputs.get("b_mm"),
            D_mm=inputs.get("D_mm"),
            d_mm=inputs.get("d_mm"),
            fck_nmm2=inputs.get("fck_nmm2"),
            fy_nmm2=inputs.get("fy_nmm2"),
            span_mm=inputs.get("span_mm"),
        )

        if not result:
            st.warning("⚠️ Design analysis failed. Please run beam design first.")
            return {"analysis": None, "comparison": []}

        # Validate design result structure
        result_validation = validate_design_result(result)
        if not result_validation:
            st.error("⚠️ Design result structure is invalid:")
            for error in result_validation.errors:
                st.error(f"  • {error}")
            return {"analysis": None, "comparison": []}

        design_result = result.get("design", {})
        flexure = design_result.get("flexure")

        if not flexure:
            st.warning("⚠️ No flexure results available.")
            return {"analysis": None, "comparison": []}

    # Check for alternatives
    alternatives = flexure.get("_bar_alternatives", [])
    if not alternatives:
        st.warning("⚠️ No bar alternatives available. Try running beam design first with different parameters.")
        return {"analysis": None, "comparison": []}

    # Get selected design
    selected_bars = flexure.get("tension_steel", {})

    # CRITICAL: Validate selected area to prevent zero division
    selected_area = selected_bars.get("area") or 0
    if selected_area <= 0:
        st.error("❌ Invalid baseline design: steel area is zero or negative.")
        st.error("This usually means the design failed. Please check beam design inputs.")
        return {"analysis": None, "comparison": []}

    selected_num = selected_bars.get("num") or 0
    selected_dia = selected_bars.get("dia") or 0

    # Simple cost calculation using library constants
    if not HAS_COSTING:
        st.error("❌ Costing library not available")
        return {"analysis": None, "comparison": []}

    # Initialize comparison list for storing all design alternatives
    comparison = []

    cost_profile = CostProfile()  # Indian average costs
    steel_unit_cost = cost_profile.steel_cost_per_kg  # ₹72/kg (Fe500)
    # Safe: STEEL_DENSITY_KG_PER_M3 is a positive constant (7850.0) from library
    selected_steel_vol_mm3 = selected_area * (inputs.get("span_mm") or 0)
    # Convert from N/mm³ to kg/mm³: divide by 1e9 to get kg
    selected_steel_kg = selected_steel_vol_mm3 * (STEEL_DENSITY_KG_PER_M3 * 1e-9)
    selected_steel_cost = selected_steel_kg * steel_unit_cost

    comparison.append({
        "bar_config": f"{selected_num}-{selected_dia}mm",
        "b_mm": inputs.get("b_mm") or 0,
        "D_mm": inputs.get("D_mm") or 0,
        "fck_nmm2": inputs.get("fck_nmm2") or 0,
        "fy_nmm2": inputs.get("fy_nmm2") or 0,
        "steel_area_mm2": selected_area,
        "steel_kg": selected_steel_kg,
        "utilization_ratio": 1.00,  # Baseline = 100%
        "total_cost": selected_steel_cost,
        "steel_cost": selected_steel_cost,
        "is_optimal": False,  # Will determine later
    })

    # Calculate costs for alternatives (up to 10)
    MAX_ALTERNATIVES = 10
    for alt in alternatives[:MAX_ALTERNATIVES]:
        alt_area = alt.get("area") or 0
        alt_num = alt.get("num") or 0
        alt_dia = alt.get("dia") or 0

        # Steel volume and cost
        alt_steel_vol_mm3 = alt_area * (inputs.get("span_mm") or 0)
        # Convert from N/mm³ to kg/mm³: divide by 1e9 to get kg
        alt_steel_kg = alt_steel_vol_mm3 * (STEEL_DENSITY_KG_PER_M3 * 1e-9)
        alt_steel_cost = alt_steel_kg * steel_unit_cost

        # FIXED: Use safe_divide to prevent zero division
        utilization_ratio = safe_divide(alt_area, selected_area, default=1.0)

        comparison.append({
            "bar_config": f"{alt_num}-{alt_dia}mm",
            "b_mm": inputs.get("b_mm") or 0,
            "D_mm": inputs.get("D_mm") or 0,
            "fck_nmm2": inputs.get("fck_nmm2") or 0,
            "fy_nmm2": inputs.get("fy_nmm2") or 0,
            "steel_area_mm2": alt_area,
            "steel_kg": alt_steel_kg,
            "utilization_ratio": utilization_ratio,
            "total_cost": alt_steel_cost,
            "steel_cost": alt_steel_cost,
            "is_optimal": False,
        })

    # Sort by total cost
    comparison.sort(key=lambda x: x.get("total_cost", math.inf))

    # Mark lowest cost as optimal
    if comparison:
        for idx, item in enumerate(comparison):
            item["is_optimal"] = idx == 0

    # Calculate savings using safe_divide
    if len(comparison) > 1:
        baseline_cost = 0
        first = next(iter(comparison), None)
        if first:
            baseline_cost = first.get("total_cost") or 0
        if first and not first.get("is_optimal"):
            second = next(itertools.islice(comparison, 1, None), None)
            if second:
                baseline_cost = second.get("total_cost") or baseline_cost
        optimal_cost = min((item.get("total_cost") or 0) for item in comparison)
        savings = baseline_cost - optimal_cost
        savings_pct = safe_divide(savings * 100, baseline_cost, default=0.0)
    else:
        first = next(iter(comparison), None)
        baseline_cost = (first.get("total_cost") or 0) if first else 0
        optimal_cost = baseline_cost
        savings = 0
        savings_pct = 0

    analysis_summary = {
        "baseline_cost": baseline_cost,
        "optimal_cost": optimal_cost,
        "savings_amount": savings,
        "savings_percent": savings_pct,
        "candidates_evaluated": len(comparison),
    }

    return {"analysis": analysis_summary, "comparison": comparison}


# Main page layout
def main():
    initialize_session_state()

    page_header(
        title="Cost Optimizer",
        subtitle="Optimize beam design for minimum cost while meeting IS 456:2000 requirements. Compare different design alternatives and export results.",
        icon="💰",
    )

    # Sidebar - Input Selection
    st.sidebar.header("Input Source")
    input_source = st.sidebar.radio(
        "Select input method:",
        ["From Beam Design", "Manual Input"],
        help="Use inputs from Beam Design page or enter manually",
    )

    inputs = None

    if input_source == "From Beam Design":
        inputs = get_beam_design_inputs()
        if inputs:
            st.sidebar.success("✅ Using inputs from Beam Design page")
            with st.sidebar.expander("View Inputs"):
                st.json(inputs)
        else:
            st.sidebar.warning("⚠️ No inputs available from Beam Design page")
            st.info(
                "👉 Go to **Beam Design** page first to enter parameters, "
                "then return here to optimize costs."
            )
            return

    else:  # Manual Input
        st.sidebar.subheader("Manual Input")

        with st.sidebar.form("manual_input_form"):
            st.markdown("**Loads**")
            mu_knm = st.number_input(
                "Moment Mu (kN·m)", min_value=1.0, value=120.0, step=10.0
            )
            vu_kn = st.number_input(
                "Shear Vu (kN)", min_value=1.0, value=85.0, step=5.0
            )

            st.markdown("**Geometry**")
            b_mm = st.number_input(
                "Width b (mm)", min_value=100.0, value=300.0, step=50.0
            )
            D_mm = st.number_input(
                "Total Depth D (mm)", min_value=150.0, value=500.0, step=50.0
            )
            d_mm = st.number_input(
                "Effective Depth d (mm)", min_value=100.0, value=450.0, step=50.0
            )
            span_mm = st.number_input(
                "Span (mm)", min_value=1000.0, value=5000.0, step=500.0
            )

            st.markdown("**Materials**")
            fck_nmm2 = st.selectbox("fck (N/mm²)", [20, 25, 30, 35, 40], index=1)
            fy_nmm2 = st.selectbox("fy (N/mm²)", [415, 500], index=1)

            submitted = st.form_submit_button("Use These Inputs", type="primary")

            if submitted:
                inputs = {
                    "mu_knm": mu_knm,
                    "vu_kn": vu_kn,
                    "b_mm": b_mm,
                    "D_mm": D_mm,
                    "d_mm": d_mm,
                    "span_mm": span_mm,
                    "fck_nmm2": fck_nmm2,
                    "fy_nmm2": fy_nmm2,
                }

    # Main area - Results
    if inputs:
        # Run optimization button
        if st.button("🚀 Run Cost Optimization", type="primary"):
            with st.spinner("Optimizing design for minimum cost..."):
                results = run_cost_optimization(inputs)
                st.session_state.cost_results = results.get("analysis")
                st.session_state.cost_comparison_data = results.get("comparison", [])

        # Display results if available
        if st.session_state.cost_results or st.session_state.cost_comparison_data:
            st.success("✅ Optimization complete!")

            # Summary metrics
            st.subheader("📊 Cost Summary")
            analysis_data = st.session_state.cost_results
            if analysis_data:
                col1, col2, col3, col4 = st.columns(4)
                col1.metric(
                    "Baseline Cost",
                f"₹{(analysis_data.get('baseline_cost') or 0):,.0f}",
                )
                col2.metric(
                    "Optimal Cost",
                f"₹{(analysis_data.get('optimal_cost') or 0):,.0f}",
                )
                col3.metric(
                    "Savings",
                f"₹{(analysis_data.get('savings_amount') or 0):,.0f}",
                delta=f"{(analysis_data.get('savings_percent') or 0):.1f}%",
                )
                col4.metric(
                    "Candidates Evaluated",
                analysis_data.get("candidates_evaluated") or 0,
                )

            # Tabs for different views
            tab1, tab2, tab3 = st.tabs(
                ["📈 Visualization", "📋 Comparison Table", "📥 Export"]
            )

            with tab1:
                st.subheader("Cost vs Utilization")
                if st.session_state.cost_comparison_data:
                    fig = create_cost_scatter(st.session_state.cost_comparison_data)
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown(
                        """
                    **Interpretation:**
                    - **Green dots** = Optimal design (lowest cost)
                    - **Blue dots** = Alternative designs
                    - **Size** = Steel area (larger = more steel)
                    - **Target zone** = Lower-left (low cost, high efficiency)
                    """
                    )

            with tab2:
                st.subheader("Design Alternatives Comparison")
                if st.session_state.cost_comparison_data:
                    df_display = create_comparison_table(
                        st.session_state.cost_comparison_data
                    )
                    st.dataframe(
                        df_display,
                        use_container_width=True,
                        height=400,
                    )

                    st.caption(
                        "💡 Click column headers to sort. "
                        "Use Export tab to download as CSV."
                    )

            with tab3:
                st.subheader("Export Results")
                if st.session_state.cost_comparison_data:
                    csv_data = export_to_csv(st.session_state.cost_comparison_data)

                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_data,
                        file_name="cost_optimization_results.csv",
                        mime="text/csv",
                    )

                    st.markdown(
                        """
                    **CSV includes:**
                    - All design parameters (b, D, fck, fy)
                    - Cost breakdown (concrete, steel, formwork)
                    - Performance metrics (utilization, steel area)
                    """
                    )
                else:
                    st.info("No data to export. Run optimization first.")
        else:
            st.info("👆 Click 'Run Cost Optimization' to see results")


if __name__ == "__main__":
    main()
