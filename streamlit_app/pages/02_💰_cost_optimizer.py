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
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    from structural_lib.costing import calculate_beam_cost, CostProfile
    HAS_COSTING = True
except ImportError:
    HAS_COSTING = False

from utils.api_wrapper import cached_smart_analysis
from utils.layout import setup_page, page_header
from utils.theme_manager import apply_dark_mode_theme, initialize_theme

# Initialize theme
initialize_theme()

# Modern page setup
setup_page(title="Cost Optimizer - IS 456 Beam Design", icon="💰", layout="wide")

# Apply dark mode styling
apply_dark_mode_theme()


def initialize_session_state():
    """Initialize session state for cost optimizer."""
    if "cost_results" not in st.session_state:
        st.session_state.cost_results = None
    if "cost_comparison_data" not in st.session_state:
        st.session_state.cost_comparison_data = []


def get_beam_design_inputs() -> Optional[dict]:
    """Get inputs from Beam Design page session state if available."""
    # Check if beam_inputs exists (from beam design page)
    if "beam_inputs" in st.session_state:
        beam = st.session_state.beam_inputs
        # Map concrete/steel grades to fck/fy values
        fck_map = {"M20": 20, "M25": 25, "M30": 30, "M35": 35, "M40": 40}
        fy_map = {"Fe415": 415, "Fe500": 500, "Fe550": 550}

        return {
            "mu_knm": beam.get("mu_knm", 120.0),
            "vu_kn": beam.get("vu_kn", 80.0),
            "b_mm": beam.get("b_mm", 300.0),
            "D_mm": beam.get("D_mm", 500.0),
            "d_mm": beam.get("d_mm", 450.0),
            "span_mm": beam.get("span_mm", 5000.0),
            "fck_nmm2": fck_map.get(beam.get("concrete_grade", "M25"), 25),
            "fy_nmm2": fy_map.get(beam.get("steel_grade", "Fe500"), 500),
        }
    return None


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
        "steel_area_mm2": "Steel (mm²)",
        "total_cost": "Total Cost (INR)",
        "steel_cost": "Steel (INR)",
        "concrete_cost": "Concrete (INR)",
        "formwork_cost": "Formwork (INR)",
        "utilization_ratio": "Relative Area",
    }

    available_columns = [col for col in display_columns.keys() if col in df.columns]
    df_display = df[available_columns].copy()
    df_display.columns = [display_columns[col] for col in available_columns]

    # Format numeric columns
    if "Relative Area" in df_display.columns:
        df_display["Relative Area"] = df_display["Relative Area"].apply(
            lambda x: f"{x:.2f}"
        )

    for col in df_display.columns:
        if "Cost" in col or "INR" in col:
            df_display[col] = df_display[col].apply(lambda x: f"{x:,.0f}")
        if "Steel (mm²)" in col:
            df_display[col] = df_display[col].apply(lambda x: f"{x:,.0f}")

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


def run_cost_optimization(inputs: dict) -> dict:
    """
    Run cost optimization analysis using bar alternatives.

    Args:
        inputs: Design input parameters

    Returns:
        Dictionary with optimization results and comparison data
    """
    try:
        # Import here to avoid circular import
        from utils.api_wrapper import cached_design_beam_flexure

        # Run flexure design to get bar alternatives
        flexure = cached_design_beam_flexure(
            mu_knm=inputs["mu_knm"],
            b_mm=inputs["b_mm"],
            D_mm=inputs["D_mm"],
            d_mm=inputs["d_mm"],
            fck_nmm2=inputs["fck_nmm2"],
            fy_nmm2=inputs["fy_nmm2"],
            d_dash_mm=inputs.get("d_dash_mm", 50.0),
        )

        if not flexure or "_bar_alternatives" not in flexure:
            st.warning("⚠️ No bar alternatives available. Using default cost estimates.")
            return {"analysis": None, "comparison": []}

        # Get selected design and alternatives
        selected_bars = flexure.get("tension_steel", {})
        alternatives = flexure.get("_bar_alternatives", [])

        # Cost profile (Indian average)
        if HAS_COSTING:
            cost_profile = CostProfile()
        else:
            st.warning("⚠️ Costing module not available. Showing placeholders.")
            return {"analysis": None, "comparison": []}

        # Calculate cost for selected design
        comparison = []
        span_m = inputs["span_mm"] / 1000.0

        # Selected design (baseline)
        selected_area = selected_bars.get("area", 0)
        selected_pt = 100 * selected_area / (inputs["b_mm"] * inputs["d_mm"])

        selected_cost = calculate_beam_cost(
            b_mm=inputs["b_mm"],
            D_mm=inputs["D_mm"],
            span_mm=inputs["span_mm"],
            ast_mm2=selected_area,
            fck_nmm2=int(inputs["fck_nmm2"]),
            steel_percentage=selected_pt,
            cost_profile=cost_profile,
        )

        comparison.append({
            "bar_config": f"{selected_bars.get('num', 0)}-{selected_bars.get('dia', 0)}mm",
            "b_mm": inputs["b_mm"],
            "D_mm": inputs["D_mm"],
            "fck_nmm2": inputs["fck_nmm2"],
            "fy_nmm2": inputs["fy_nmm2"],
            "steel_area_mm2": selected_area,
            "utilization_ratio": selected_area / (selected_area + 1),  # Approximate
            "total_cost": selected_cost.total_cost,
            "concrete_cost": selected_cost.concrete_cost,
            "steel_cost": selected_cost.steel_cost,
            "formwork_cost": selected_cost.formwork_cost,
            "is_optimal": True,  # Mark as baseline/selected
        })

        # Calculate costs for alternatives
        for alt in alternatives[:10]:  # Limit to 10 alternatives
            alt_area = alt.get("area", 0)
            alt_pt = 100 * alt_area / (inputs["b_mm"] * inputs["d_mm"])

            alt_cost = calculate_beam_cost(
                b_mm=inputs["b_mm"],
                D_mm=inputs["D_mm"],
                span_mm=inputs["span_mm"],
                ast_mm2=alt_area,
                fck_nmm2=int(inputs["fck_nmm2"]),
                steel_percentage=alt_pt,
                cost_profile=cost_profile,
            )

            comparison.append({
                "bar_config": f"{alt.get('num', 0)}-{alt.get('dia', 0)}mm",
                "b_mm": inputs["b_mm"],
                "D_mm": inputs["D_mm"],
                "fck_nmm2": inputs["fck_nmm2"],
                "fy_nmm2": inputs["fy_nmm2"],
                "steel_area_mm2": alt_area,
                "utilization_ratio": alt_area / (selected_area + 1),  # Relative to selected
                "total_cost": alt_cost.total_cost,
                "concrete_cost": alt_cost.concrete_cost,
                "steel_cost": alt_cost.steel_cost,
                "formwork_cost": alt_cost.formwork_cost,
                "is_optimal": False,
            })

        # Sort by total cost
        comparison.sort(key=lambda x: x["total_cost"])

        # Mark lowest cost as optimal
        if comparison:
            comparison[0]["is_optimal"] = True
            for i in range(1, len(comparison)):
                comparison[i]["is_optimal"] = False

        # Calculate savings
        if len(comparison) > 1:
            baseline_cost = comparison[1]["total_cost"] if not comparison[0]["is_optimal"] else comparison[0]["total_cost"]
            optimal_cost = min(c["total_cost"] for c in comparison)
            savings = baseline_cost - optimal_cost
            savings_pct = (savings / baseline_cost) * 100 if baseline_cost > 0 else 0
        else:
            baseline_cost = comparison[0]["total_cost"] if comparison else 0
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

    except Exception as e:
        st.error(f"❌ Cost optimization failed: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return {"analysis": None, "comparison": []}


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
                    f"₹{analysis_data.get('baseline_cost', 0):,.0f}",
                )
                col2.metric(
                    "Optimal Cost",
                    f"₹{analysis_data.get('optimal_cost', 0):,.0f}",
                )
                col3.metric(
                    "Savings",
                    f"₹{analysis_data.get('savings_amount', 0):,.0f}",
                    delta=f"{analysis_data.get('savings_percent', 0):.1f}%",
                )
                col4.metric(
                    "Candidates Evaluated",
                    analysis_data.get("candidates_evaluated", 0),
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
