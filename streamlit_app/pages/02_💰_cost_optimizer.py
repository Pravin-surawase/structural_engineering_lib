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
    from structural_lib.costing import (
        calculate_beam_cost,
        CostProfile,
        STEEL_DENSITY_KG_PER_M3,
    )

    HAS_COSTING = True
except ImportError:
    HAS_COSTING = False
    STEEL_DENSITY_KG_PER_M3 = 7850000.0  # Fallback value

# Import multi-objective optimizer for Pareto front
try:
    from structural_lib.multi_objective_optimizer import (
        optimize_pareto_front,
        get_design_explanation,
        ParetoCandidate,
    )

    HAS_PARETO = True
except ImportError:
    HAS_PARETO = False
    optimize_pareto_front = None
    get_design_explanation = None

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

# TASK-602: Modern Streamlit patterns
from utils.fragments import show_status_badge, fragment_input_section
from utils.constants import CONCRETE_GRADE_MAP, STEEL_GRADE_MAP

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
        df_display["Area Ratio"] = df_display["Area Ratio"].apply(lambda x: f"{x:.2%}")

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


def create_pareto_scatter(pareto_result: dict) -> go.Figure:
    """
    Create Pareto front scatter plot with 3 objectives.

    Args:
        pareto_result: Result from optimize_pareto_front().to_dict()

    Returns:
        Plotly Figure object
    """
    pareto_front = pareto_result.get("pareto_front", [])
    if not pareto_front:
        fig = go.Figure()
        fig.add_annotation(
            text="No Pareto-optimal designs found",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        return fig

    df = pd.DataFrame(pareto_front)

    # Create 3D scatter plot for cost vs utilization vs steel weight
    fig = go.Figure()

    # Add Pareto front points
    fig.add_trace(
        go.Scatter(
            x=df["utilization"],
            y=df["cost"],
            mode="markers+text",
            marker=dict(
                size=df["steel_weight_kg"] * 0.5 + 10,  # Size by weight
                color=df["steel_weight_kg"],
                colorscale="Viridis",
                showscale=True,
                colorbar=dict(title="Steel (kg)"),
                line=dict(width=2, color="white"),
            ),
            text=df["bar_config"],
            textposition="top center",
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Cost: ₹%{y:,.0f}<br>"
                "Utilization: %{x:.1%}<br>"
                "Steel: %{marker.color:.1f} kg<br>"
                "<extra></extra>"
            ),
            name="Pareto Front",
        )
    )

    # Highlight best designs
    best_cost = pareto_result.get("best_by_cost")
    if best_cost:
        fig.add_trace(
            go.Scatter(
                x=[best_cost.get("utilization", 0)],
                y=[best_cost.get("cost", 0)],
                mode="markers",
                marker=dict(size=20, color="green", symbol="star"),
                name="Cheapest",
                hovertemplate=(
                    f"<b>Cheapest: {best_cost.get('bar_config', '')}</b><br>"
                    f"Cost: ₹{best_cost.get('cost', 0):,.0f}<br>"
                    "<extra></extra>"
                ),
            )
        )

    best_util = pareto_result.get("best_by_utilization")
    if best_util and best_util != best_cost:
        fig.add_trace(
            go.Scatter(
                x=[best_util.get("utilization", 0)],
                y=[best_util.get("cost", 0)],
                mode="markers",
                marker=dict(size=20, color="blue", symbol="diamond"),
                name="Most Efficient",
                hovertemplate=(
                    f"<b>Efficient: {best_util.get('bar_config', '')}</b><br>"
                    f"Utilization: {best_util.get('utilization', 0):.1%}<br>"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title="Pareto Front: Cost vs Utilization Trade-off",
        xaxis=dict(
            title="Capacity Utilization",
            tickformat=".0%",
            range=[0, 1.1],
        ),
        yaxis=dict(title="Total Cost (INR)", tickformat=","),
        hovermode="closest",
        height=500,
        showlegend=True,
        legend=dict(x=0.02, y=0.98),
    )

    return fig


def run_pareto_optimization(inputs: dict) -> dict | None:
    """
    Run Pareto multi-objective optimization.

    Args:
        inputs: Design input parameters

    Returns:
        Dictionary with Pareto optimization results or None
    """
    if not HAS_PARETO or optimize_pareto_front is None:
        st.error("❌ Multi-objective optimizer not available")
        return None

    # Validate inputs first
    validation = validate_beam_inputs(inputs)
    if not validation:
        for error in validation.errors:
            st.error(f"❌ Input validation failed: {error}")
        return None

    try:
        result = optimize_pareto_front(
            span_mm=inputs.get("span_mm", 5000),
            mu_knm=inputs.get("mu_knm", 120),
            vu_kn=inputs.get("vu_kn", 80),
            objectives=["cost", "steel_weight", "utilization"],
            max_candidates=50,
        )
        return result.to_dict()
    except Exception as e:
        st.error(f"❌ Pareto optimization failed: {str(e)}")
        return None


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
        st.warning(
            "⚠️ No bar alternatives available. Try running beam design first with different parameters."
        )
        return {"analysis": None, "comparison": []}

    # Get selected design
    selected_bars = flexure.get("tension_steel", {})

    # CRITICAL: Validate selected area to prevent zero division
    selected_area = selected_bars.get("area") or 0
    if selected_area <= 0:
        st.error("❌ Invalid baseline design: steel area is zero or negative.")
        st.error(
            "This usually means the design failed. Please check beam design inputs."
        )
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

    comparison.append(
        {
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
        }
    )

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

        comparison.append(
            {
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
            }
        )

    # SAVE baseline cost BEFORE sorting (first item is the originally selected design)
    if len(comparison) > 0:
        baseline_cost = comparison[0].get("total_cost") or 0
        baseline_config = comparison[0].get("bar_config", "")
    else:
        baseline_cost = 0
        baseline_config = ""

    # Sort by total cost
    comparison.sort(key=lambda x: x.get("total_cost", math.inf))

    # Mark lowest cost as optimal
    if len(comparison) > 0:
        for idx, item in enumerate(comparison):
            item["is_optimal"] = idx == 0

    # Calculate savings: baseline (original design) vs optimal (cheapest)
    if len(comparison) > 0:
        # Scanner: len check above guards this access
        first_item = comparison[0]
        optimal_cost = first_item.get("total_cost") or 0  # First after sort = cheapest
        optimal_config = first_item.get("bar_config", "")
        savings = baseline_cost - optimal_cost
        savings_pct = safe_divide(savings * 100, baseline_cost, default=0.0)
    else:
        optimal_cost = baseline_cost
        optimal_config = baseline_config
        savings = 0
        savings_pct = 0

    analysis_summary = {
        "baseline_cost": baseline_cost,
        "baseline_config": baseline_config,
        "optimal_cost": optimal_cost,
        "optimal_config": optimal_config,
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
        @st.fragment
        def render_manual_inputs():
            """Manual input form wrapped in fragment for better performance."""
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
                    return {
                        "mu_knm": mu_knm,
                        "vu_kn": vu_kn,
                        "b_mm": b_mm,
                        "D_mm": D_mm,
                        "d_mm": d_mm,
                        "span_mm": span_mm,
                        "fck_nmm2": fck_nmm2,
                        "fy_nmm2": fy_nmm2,
                    }
            return None

        manual_inputs = render_manual_inputs()
        if manual_inputs:
            inputs = manual_inputs

    # Main area - Results
    if inputs:
        # Optimization mode selection
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🚀 Quick Optimization", type="primary"):
                with st.spinner("Optimizing design for minimum cost..."):
                    results = run_cost_optimization(inputs)
                    st.session_state.cost_results = results.get("analysis")
                    st.session_state.cost_comparison_data = results.get(
                        "comparison", []
                    )

        with col_btn2:
            if HAS_PARETO:
                if st.button("🎯 Pareto Multi-Objective", type="secondary"):
                    with st.spinner("Finding Pareto-optimal designs..."):
                        pareto_result = run_pareto_optimization(inputs)
                        if pareto_result:
                            st.session_state.pareto_results = pareto_result

        # Display results if available
        has_results = st.session_state.get("cost_results") is not None
        has_comparison = len(st.session_state.get("cost_comparison_data") or []) > 0
        has_pareto = st.session_state.get("pareto_results") is not None

        if has_results or has_comparison or has_pareto:
            st.success("✅ Optimization complete!")

            # Summary metrics
            st.subheader("📊 Cost Summary")
            analysis_data = st.session_state.get("cost_results")
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
            tab1, tab2, tab3, tab4 = st.tabs(
                [
                    "📈 Visualization",
                    "🎯 Pareto Front",
                    "📋 Comparison Table",
                    "📥 Export",
                ]
            )

            with tab1:
                st.subheader("Cost vs Utilization")
                comparison_data = st.session_state.get("cost_comparison_data") or []
                if comparison_data:
                    fig = create_cost_scatter(comparison_data)
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
                else:
                    st.info("Run Quick Optimization to see results.")

            with tab2:
                st.subheader("🎯 Pareto Multi-Objective Optimization")

                # Explanation for users unfamiliar with Pareto optimization
                with st.expander("ℹ️ What is Pareto Optimization?", expanded=False):
                    st.markdown("""
**Pareto optimization** finds designs that are optimal across multiple objectives simultaneously.

**Three objectives balanced:**
- **💰 Cost** — Minimize total material cost
- **⚡ Utilization** — Maximize structural efficiency (closer to capacity = more efficient)
- **🪶 Weight** — Minimize steel consumption for sustainability

**Why Pareto?**
No single design is "best" for everything. A cheaper design might use more steel.
The **Pareto front** shows all designs where improving one objective means sacrificing another.

**How to choose:**
- **Budget-constrained?** → Pick the "Cheapest" design
- **Need efficiency?** → Pick "Most Efficient" (highest utilization)
- **Sustainability focus?** → Pick "Lightest" (least steel)
                    """)

                pareto_data = st.session_state.get("pareto_results")
                if pareto_data:
                    # Summary metrics for Pareto
                    p_col1, p_col2, p_col3 = st.columns(3)
                    p_col1.metric(
                        "Pareto-Optimal Designs", pareto_data.get("pareto_count", 0)
                    )
                    p_col2.metric(
                        "Total Candidates", pareto_data.get("total_candidates", 0)
                    )
                    p_col3.metric(
                        "Computation Time",
                        f"{pareto_data.get('computation_time_sec', 0):.3f}s",
                    )

                    # Pareto scatter plot
                    fig = create_pareto_scatter(pareto_data)
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown("---")
                    st.subheader("🏆 Best Designs by Objective")

                    best_col1, best_col2, best_col3 = st.columns(3)

                    with best_col1:
                        # TASK-602: Modern badge pattern
                        if hasattr(st, "badge"):
                            st.badge("💰 Cheapest", color="green")
                        else:
                            st.markdown("**💰 Cheapest**")
                        best_cost = pareto_data.get("best_by_cost")
                        if best_cost:
                            st.write(f"**{best_cost.get('bar_config', '')}**")
                            st.write(f"Cost: ₹{best_cost.get('cost', 0):,.0f}")
                            st.write(
                                f"Utilization: {best_cost.get('utilization', 0):.1%}"
                            )
                            # Show governing clauses
                            clauses = best_cost.get("governing_clauses", [])
                            if clauses:
                                st.markdown("**Why this design?**")
                                for c in clauses[:2]:
                                    st.caption(f"• {c}")

                    with best_col2:
                        # TASK-602: Modern badge pattern
                        if hasattr(st, "badge"):
                            st.badge("⚡ Most Efficient", color="blue")
                        else:
                            st.markdown("**⚡ Most Efficient**")
                        best_util = pareto_data.get("best_by_utilization")
                        if best_util:
                            st.write(f"**{best_util.get('bar_config', '')}**")
                            st.write(f"Cost: ₹{best_util.get('cost', 0):,.0f}")
                            st.write(
                                f"Utilization: {best_util.get('utilization', 0):.1%}"
                            )
                            clauses = best_util.get("governing_clauses", [])
                            if clauses:
                                st.markdown("**Why this design?**")
                                for c in clauses[:2]:
                                    st.caption(f"• {c}")

                    with best_col3:
                        # TASK-602: Modern badge pattern
                        if hasattr(st, "badge"):
                            st.badge("🪶 Lightest", color="orange")
                        else:
                            st.markdown("**🪶 Lightest**")
                        best_wt = pareto_data.get("best_by_weight")
                        if best_wt:
                            st.write(f"**{best_wt.get('bar_config', '')}**")
                            st.write(
                                f"Steel: {best_wt.get('steel_weight_kg', 0):.1f} kg"
                            )
                            st.write(
                                f"Utilization: {best_wt.get('utilization', 0):.1%}"
                            )
                            clauses = best_wt.get("governing_clauses", [])
                            if clauses:
                                st.markdown("**Why this design?**")
                                for c in clauses[:2]:
                                    st.caption(f"• {c}")

                    # Interactive design selection
                    st.markdown("---")
                    st.subheader("📋 All Pareto-Optimal Designs")
                    pareto_front = pareto_data.get("pareto_front", [])
                    if pareto_front:
                        # Create dataframe for display
                        df_pareto = pd.DataFrame(pareto_front)
                        display_cols = [
                            "bar_config",
                            "b_mm",
                            "D_mm",
                            "cost",
                            "steel_weight_kg",
                            "utilization",
                        ]
                        available_cols = [
                            c for c in display_cols if c in df_pareto.columns
                        ]
                        df_display = df_pareto[available_cols].copy()
                        df_display.columns = [
                            "Config",
                            "Width",
                            "Depth",
                            "Cost (₹)",
                            "Steel (kg)",
                            "Utilization",
                        ]
                        df_display["Cost (₹)"] = df_display["Cost (₹)"].apply(
                            lambda x: f"₹{x:,.0f}"
                        )
                        df_display["Utilization"] = df_display["Utilization"].apply(
                            lambda x: f"{x:.1%}"
                        )
                        df_display["Steel (kg)"] = df_display["Steel (kg)"].apply(
                            lambda x: f"{x:.1f}"
                        )
                        st.dataframe(
                            df_display, use_container_width=True, hide_index=True
                        )

                        # Design selection for WHY display
                        st.markdown("---")
                        st.subheader("🔍 Design Deep Dive")
                        design_options = [
                            d.get("bar_config", f"Design {i+1}")
                            for i, d in enumerate(pareto_front)
                        ]
                        selected_design_idx = st.selectbox(
                            "Select a design to see why it was chosen:",
                            range(len(design_options)),
                            format_func=lambda i: design_options[i],
                        )

                        if (
                            selected_design_idx is not None
                            and len(pareto_front) > selected_design_idx
                        ):
                            selected = pareto_front[selected_design_idx]
                            st.markdown(
                                f"### {selected.get('bar_config', '')} - {selected.get('b_mm', 0)}×{selected.get('D_mm', 0)}mm"
                            )

                            detail_col1, detail_col2 = st.columns(2)
                            with detail_col1:
                                st.markdown("**Design Parameters:**")
                                st.write(f"- Width: {selected.get('b_mm', 0)} mm")
                                st.write(f"- Depth: {selected.get('D_mm', 0)} mm")
                                st.write(f"- Concrete: M{selected.get('fck_nmm2', 0)}")
                                st.write(f"- Steel: Fe{selected.get('fy_nmm2', 0)}")

                            with detail_col2:
                                st.markdown("**Performance:**")
                                st.write(
                                    f"- Ast required: {selected.get('ast_required', 0):.0f} mm²"
                                )
                                st.write(
                                    f"- Ast provided: {selected.get('ast_provided', 0):.0f} mm²"
                                )
                                st.write(
                                    f"- Total cost: ₹{selected.get('cost', 0):,.0f}"
                                )
                                st.write(
                                    f"- Steel weight: {selected.get('steel_weight_kg', 0):.2f} kg"
                                )

                            # WHY section - governing clauses
                            st.markdown("---")
                            st.markdown("### ⚖️ Why This Design? (IS 456 Clauses)")
                            clauses = selected.get("governing_clauses", [])
                            if clauses:
                                for clause in clauses:
                                    st.info(f"📖 {clause}")
                            else:
                                st.write(
                                    "Standard flexural design per IS 456:2000 Cl. 38.1"
                                )

                            # Utilization insight
                            util = selected.get("utilization", 0)
                            if util > 0.85:
                                st.success(
                                    "✅ **High Efficiency** (>85% utilization) - Excellent use of material capacity"
                                )
                            elif util > 0.7:
                                st.info(
                                    "✅ **Good Efficiency** (70-85% utilization) - Well-balanced design"
                                )
                            else:
                                st.warning(
                                    "⚠️ **Low Efficiency** (<70% utilization) - Consider smaller section if possible"
                                )
                else:
                    st.info(
                        "👆 Click '🎯 Pareto Multi-Objective' button above to find "
                        "Pareto-optimal designs with multiple trade-offs (cost vs efficiency vs weight)."
                    )

            with tab3:
                st.subheader("Design Alternatives Comparison")
                comparison_data = st.session_state.get("cost_comparison_data") or []
                if comparison_data:
                    df_display = create_comparison_table(comparison_data)
                    st.dataframe(
                        df_display,
                        use_container_width=True,
                        height=400,
                    )

                    st.caption(
                        "💡 Click column headers to sort. "
                        "Use Export tab to download as CSV."
                    )
                else:
                    st.info("Run Quick Optimization to see comparison table.")

            with tab4:
                st.subheader("Export Results")
                comparison_data = st.session_state.get("cost_comparison_data") or []
                pareto_data = st.session_state.get("pareto_results")

                if comparison_data:
                    st.markdown("**Quick Optimization Results:**")
                    csv_data = export_to_csv(comparison_data)

                    st.download_button(
                        label="📥 Download Quick Optimization CSV",
                        data=csv_data,
                        file_name="cost_optimization_results.csv",
                        mime="text/csv",
                    )

                if pareto_data and pareto_data.get("pareto_front"):
                    st.markdown("**Pareto Optimization Results:**")
                    pareto_csv = export_to_csv(pareto_data.get("pareto_front", []))

                    st.download_button(
                        label="📥 Download Pareto Front CSV",
                        data=pareto_csv,
                        file_name="pareto_optimization_results.csv",
                        mime="text/csv",
                    )

                if not comparison_data and not pareto_data:
                    st.info("No data to export. Run optimization first.")
                else:
                    st.markdown(
                        """
                    **CSV includes:**
                    - All design parameters (b, D, fck, fy)
                    - Cost breakdown
                    - Performance metrics (utilization, steel area)
                    - Governing IS 456 clauses (for Pareto results)
                    """
                    )
        else:
            st.info("👆 Click 'Run Cost Optimization' to see results")


if __name__ == "__main__":
    main()
