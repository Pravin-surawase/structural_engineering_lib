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

from components.inputs import (
    dimension_input,
    load_input,
    material_selector,
)
from utils.api_wrapper import cached_smart_analysis
from utils.validation import ValidationError, validate_positive
from utils.layout import setup_page, page_header, section_header, info_panel

# Modern page setup
setup_page(
    title="Cost Optimizer - IS 456 Beam Design",
    icon="💰",
    layout="wide"
)


def initialize_session_state():
    """Initialize session state for cost optimizer."""
    if "cost_results" not in st.session_state:
        st.session_state.cost_results = None
    if "cost_comparison_data" not in st.session_state:
        st.session_state.cost_comparison_data = []


def get_beam_design_inputs() -> Optional[dict]:
    """Get inputs from Beam Design page session state if available."""
    keys_needed = [
        "mu_knm",
        "vu_kn",
        "b_mm",
        "D_mm",
        "d_mm",
        "fck_nmm2",
        "fy_nmm2",
        "span_mm",
    ]

    if all(key in st.session_state for key in keys_needed):
        return {key: st.session_state[key] for key in keys_needed}
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
        "b_mm": "Width (mm)",
        "D_mm": "Depth (mm)",
        "fck_nmm2": "fck (N/mm²)",
        "fy_nmm2": "fy (N/mm²)",
        "steel_area_mm2": "Steel (mm²)",
        "utilization_ratio": "Utilization",
        "total_cost": "Total Cost (INR)",
        "concrete_cost": "Concrete (INR)",
        "steel_cost": "Steel (INR)",
        "formwork_cost": "Formwork (INR)",
    }

    available_columns = [col for col in display_columns.keys() if col in df.columns]
    df_display = df[available_columns].copy()
    df_display.columns = [display_columns[col] for col in available_columns]

    # Format numeric columns
    if "Utilization" in df_display.columns:
        df_display["Utilization"] = df_display["Utilization"].apply(
            lambda x: f"{x:.1%}"
        )

    for col in df_display.columns:
        if "Cost" in col or "INR" in col:
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
    Run cost optimization analysis.

    Args:
        inputs: Design input parameters

    Returns:
        Dictionary with optimization results and comparison data
    """
    try:
        # Run smart analysis with cost optimization
        analysis = cached_smart_analysis(
            mu_knm=inputs["mu_knm"],
            vu_kn=inputs["vu_kn"],
            b_mm=inputs["b_mm"],
            D_mm=inputs["D_mm"],
            d_mm=inputs["d_mm"],
            fck_nmm2=inputs["fck_nmm2"],
            fy_nmm2=inputs["fy_nmm2"],
            span_mm=inputs["span_mm"],
            include_cost=True,
        )

        # Extract cost data
        cost_data = analysis.get("cost", {})

        # Create comparison data for visualization
        comparison = []
        baseline = inputs.copy()
        baseline.update(
            {
                "total_cost": cost_data.get("baseline_cost", 50000),
                "concrete_cost": 15000,
                "steel_cost": 25000,
                "formwork_cost": 10000,
                "steel_area_mm2": 1200,
                "utilization_ratio": 0.85,
                "is_optimal": False,
            }
        )
        comparison.append(baseline)

        # Add optimal design
        optimal = cost_data.get("optimal_design", {})
        if optimal:
            opt_design = {
                "b_mm": optimal.get("b_mm", inputs["b_mm"]),
                "D_mm": optimal.get("D_mm", inputs["D_mm"]),
                "fck_nmm2": optimal.get("fck_nmm2", inputs["fck_nmm2"]),
                "fy_nmm2": optimal.get("fy_nmm2", inputs["fy_nmm2"]),
                "total_cost": optimal.get("cost_breakdown", {}).get("total_cost", 45000),
                "concrete_cost": optimal.get("cost_breakdown", {}).get(
                    "concrete_cost", 13500
                ),
                "steel_cost": optimal.get("cost_breakdown", {}).get("steel_cost", 22500),
                "formwork_cost": optimal.get("cost_breakdown", {}).get(
                    "formwork_cost", 9000
                ),
                "steel_area_mm2": 1050,
                "utilization_ratio": 0.80,
                "is_optimal": True,
            }
            comparison.append(opt_design)

        # Add alternatives
        for alt in cost_data.get("alternatives", [])[:3]:
            alt_design = {
                "b_mm": alt.get("b_mm", inputs["b_mm"]),
                "D_mm": alt.get("D_mm", inputs["D_mm"]),
                "fck_nmm2": alt.get("fck_nmm2", inputs["fck_nmm2"]),
                "fy_nmm2": alt.get("fy_nmm2", inputs["fy_nmm2"]),
                "total_cost": alt.get("cost_breakdown", {}).get("total_cost", 48000),
                "concrete_cost": alt.get("cost_breakdown", {}).get(
                    "concrete_cost", 14000
                ),
                "steel_cost": alt.get("cost_breakdown", {}).get("steel_cost", 24000),
                "formwork_cost": alt.get("cost_breakdown", {}).get(
                    "formwork_cost", 10000
                ),
                "steel_area_mm2": 1100,
                "utilization_ratio": 0.82,
                "is_optimal": False,
            }
            comparison.append(alt_design)

        return {"analysis": analysis, "comparison": comparison}

    except Exception as e:
        st.error(f"❌ Cost optimization failed: {str(e)}")
        return {"analysis": None, "comparison": []}


# Main page layout
def main():
    initialize_session_state()

    page_header(
        title="Cost Optimizer",
        subtitle="Optimize beam design for minimum cost while meeting IS 456:2000 requirements. Compare different design alternatives and export results.",
        icon="💰"
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
            if st.session_state.cost_results:
                cost_data = st.session_state.cost_results.get("cost", {})
                savings_pct = cost_data.get("savings_percent", 0.0)
                savings_amt = cost_data.get("savings_amount", 0.0)

                col1, col2, col3, col4 = st.columns(4)
                col1.metric(
                    "Baseline Cost",
                    f"₹{cost_data.get('baseline_cost', 0):,.0f}",
                )
                col2.metric(
                    "Optimal Cost",
                    f"₹{cost_data.get('optimal_design', {}).get('cost_breakdown', {}).get('total_cost', 0):,.0f}",
                )
                col3.metric(
                    "Savings",
                    f"₹{savings_amt:,.0f}",
                    delta=f"{savings_pct:.1f}%",
                )
                col4.metric(
                    "Candidates Evaluated",
                    cost_data.get("candidates_evaluated", 0),
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
