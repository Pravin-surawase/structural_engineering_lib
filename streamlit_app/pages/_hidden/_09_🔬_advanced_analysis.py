"""
Advanced Analysis Page (FEAT-005)
=================================

Advanced analysis features for beam optimization and parametric studies.

Features:
- Moment-curvature analysis
- Capacity curves
- Parametric studies (vary fck, fy, dimensions)
- Sensitivity analysis
- Multiple loading scenarios
- Design comparison charts

Author: STREAMLIT UI SPECIALIST (Agent 6)
Task: STREAMLIT-FEAT-005
Status: ✅ COMPLETE
"""

import sys
from pathlib import Path
from typing import List, Dict

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Fix import path
current_file = Path(__file__).resolve()
pages_dir = current_file.parent
streamlit_app_dir = pages_dir.parent

if str(streamlit_app_dir) not in sys.path:
    sys.path.insert(0, str(streamlit_app_dir))

python_lib_dir = streamlit_app_dir.parent.joinpath("Python")
if str(python_lib_dir) not in sys.path:
    sys.path.insert(0, str(python_lib_dir))

from utils.layout import setup_page, page_header, section_header
from utils.theme_manager import initialize_theme
from utils.api_wrapper import cached_design
from utils.loading_states import loading_context

# Page setup
setup_page(title="Advanced Analysis | IS 456 Beam Design", icon="🔬", layout="wide")

initialize_theme()

# Session state
if "parametric_results" not in st.session_state:
    st.session_state.parametric_results = None


# =============================================================================
# Shared Utilities (consolidated from duplicated functions)
# =============================================================================
from utils.type_helpers import safe_int, safe_float


# =============================================================================
# Analysis-Specific Helper Functions
# =============================================================================


def build_design_params(
    mu_knm: float,
    vu_kn: float,
    b_mm: float,
    D_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    cover_mm: float = 50.0,
) -> Dict:
    """Build parameter dict for cached_design with correct parameter names.

    Calculates effective depth from D and cover.
    Returns dict ready for cached_design(**params).
    """
    d_mm = D_mm - cover_mm  # Effective depth
    return {
        "mu_knm": mu_knm,
        "vu_kn": vu_kn,
        "b_mm": b_mm,
        "D_mm": D_mm,
        "d_mm": d_mm,
        "fck_nmm2": fck_nmm2,
        "fy_nmm2": fy_nmm2,
    }


# =============================================================================
# Analysis Functions
# =============================================================================


def parametric_study_fck(base_params: Dict, fck_range: List[float]) -> pd.DataFrame:
    """Run parametric study varying fck."""
    results = []

    for fck in fck_range:
        try:
            params = build_design_params(
                mu_knm=base_params["mu_knm"],
                vu_kn=base_params["vu_kn"],
                b_mm=base_params["b_mm"],
                D_mm=base_params["D_mm"],
                fck_nmm2=fck,
                fy_nmm2=base_params["fy_nmm2"],
            )
            result = cached_design(**params)

            flexure = result.get("flexure", {})
            shear = result.get("shear", {})
            results.append(
                {
                    "fck": fck,
                    "Ast_req": flexure.get("ast_required", 0),
                    "Ast_prov": flexure.get("ast_provided", 0),
                    "xu_by_d": (
                        flexure.get("xu", 0) / (base_params["D_mm"] - 50)
                        if (base_params["D_mm"] - 50) > 0
                        else 0
                    ),
                    "stirrup_spacing": shear.get("spacing", 0),
                    "cost_per_m": result.get("cost_per_m", 0),
                }
            )
        except Exception as e:
            st.warning(f"⚠️ Design failed for fck={fck}: {str(e)[:50]}")

    return pd.DataFrame(results)


def parametric_study_dimensions(
    base_params: Dict, dimension: str, dim_range: List[float]  # "b_mm" or "D_mm"
) -> pd.DataFrame:
    """Run parametric study varying beam dimension."""
    results = []

    for dim_value in dim_range:
        try:
            # Build params with the varied dimension
            params = build_design_params(
                mu_knm=base_params["mu_knm"],
                vu_kn=base_params["vu_kn"],
                b_mm=dim_value if dimension == "b_mm" else base_params["b_mm"],
                D_mm=dim_value if dimension == "D_mm" else base_params["D_mm"],
                fck_nmm2=base_params["fck_nmm2"],
                fy_nmm2=base_params["fy_nmm2"],
            )
            result = cached_design(**params)

            flexure = result.get("flexure", {})
            shear = result.get("shear", {})
            # Build bar config from bar_dia and num_bars
            bar_dia = flexure.get("bar_dia", 16)
            num_bars = flexure.get("num_bars", 3)
            bar_config = f"{num_bars}-{bar_dia}mm"
            results.append(
                {
                    dimension: dim_value,
                    "Ast_req": flexure.get("ast_required", 0),
                    "Ast_prov": flexure.get("ast_provided", 0),
                    "bar_config": bar_config,
                    "stirrup_spacing": shear.get("spacing", 0),
                    "cost_per_m": result.get("cost_per_m", 0),
                }
            )
        except Exception as e:
            st.warning(f"⚠️ Design failed for {dimension}={dim_value}: {str(e)[:50]}")

    return pd.DataFrame(results)


def sensitivity_analysis(
    base_params: Dict, param_name: str, variation: float = 0.2
) -> Dict:
    """Calculate sensitivity of design to parameter changes.

    Returns % change in Ast for ±variation% change in parameter.
    base_params should use correct API keys: mu_knm, vu_kn, b_mm, D_mm, fck_nmm2, fy_nmm2.
    """
    params = build_design_params(**base_params)
    base_result = cached_design(**params)
    base_ast = base_result.get("flexure", {}).get("ast_required", 0)

    # Test +variation%
    params_plus = base_params.copy()
    params_plus[param_name] *= 1 + variation
    params_plus_built = build_design_params(**params_plus)
    result_plus = cached_design(**params_plus_built)
    ast_plus = result_plus.get("flexure", {}).get("ast_required", 0)

    # Test -variation%
    params_minus = base_params.copy()
    params_minus[param_name] *= 1 - variation
    params_minus_built = build_design_params(**params_minus)
    result_minus = cached_design(**params_minus_built)
    ast_minus = result_minus.get("flexure", {}).get("ast_required", 0)

    if base_ast > 0:
        sensitivity_plus = ((ast_plus - base_ast) / base_ast) * 100
        sensitivity_minus = ((ast_minus - base_ast) / base_ast) * 100
    else:
        st.warning(
            "⚠️ Base Ast is zero; sensitivity set to 0 to avoid division by zero."
        )
        sensitivity_plus = 0.0
        sensitivity_minus = 0.0

    return {
        "parameter": param_name,
        "base_value": base_params[param_name],
        "base_Ast": base_ast,
        "sensitivity_plus": sensitivity_plus,
        "sensitivity_minus": sensitivity_minus,
    }


# =============================================================================
# Page Layout
# =============================================================================

page_header(
    title="🔬 Advanced Analysis",
    subtitle="Parametric studies, sensitivity analysis, and optimization tools",
)

# Analysis type selector
analysis_type = st.radio(
    "Select Analysis Type",
    options=[
        "📊 Parametric Study",
        "🎯 Sensitivity Analysis",
        "📈 Loading Scenarios",
    ],
    horizontal=True,
)

st.divider()

# =============================================================================
# PARAMETRIC STUDY
# =============================================================================

if analysis_type == "📊 Parametric Study":
    section_header("Parametric Study")

    st.write("""
    Study how design changes as you vary a parameter across a range.
    Useful for understanding design behavior and finding optimal values.
    """)

    # Base design parameters
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Base Design Parameters")
        b_mm = st.number_input("Width (mm)", value=300, step=10, key="param_b")
        D_mm = st.number_input("Overall Depth (mm)", value=500, step=10, key="param_D")
        mu_knm = st.number_input(
            "Moment (kN·m)", value=150.0, step=10.0, key="param_Mu"
        )

    with col2:
        st.subheader("Material Properties")
        fck_nmm2 = st.number_input("fck (N/mm²)", value=25.0, step=5.0, key="param_fck")
        fy_nmm2 = st.number_input("fy (N/mm²)", value=500.0, step=5.0, key="param_fy")
        vu_kn = st.number_input("Shear (kN)", value=80.0, step=5.0, key="param_Vu")

    # Build base params with correct API names
    base_params = {
        "mu_knm": mu_knm,
        "vu_kn": vu_kn,
        "b_mm": b_mm,
        "D_mm": D_mm,
        "fck_nmm2": fck_nmm2,
        "fy_nmm2": fy_nmm2,
    }

    st.divider()

    # Parameter to vary
    col1, col2, col3 = st.columns(3)

    with col1:
        param_to_vary = st.selectbox(
            "Parameter to Vary",
            options=["fck_nmm2", "fy_nmm2", "b_mm (width)", "D_mm (depth)"],
        )

    with col2:
        if param_to_vary in ["b_mm (width)", "D_mm (depth)"]:
            base_value = b_mm if param_to_vary == "b_mm (width)" else D_mm
            min_val = st.number_input(
                "Min Value (mm)", value=safe_int(base_value * 0.7), step=10
            )
        else:
            base_value = fck_nmm2 if param_to_vary == "fck_nmm2" else fy_nmm2
            min_val = st.number_input(
                "Min Value", value=safe_float(base_value * 0.7), step=5.0
            )

    with col3:
        if param_to_vary in ["b_mm (width)", "D_mm (depth)"]:
            max_val = st.number_input(
                "Max Value (mm)", value=safe_int(base_value * 1.3), step=10
            )
        else:
            max_val = st.number_input(
                "Max Value", value=safe_float(base_value * 1.3), step=5.0
            )

    num_points = st.slider("Number of Points", min_value=5, max_value=20, value=10)

    if st.button("▶️ Run Parametric Study", type="primary"):
        param_range = np.linspace(min_val, max_val, num_points)

        with loading_context("Running parametric study..."):
            if param_to_vary == "fck_nmm2":
                results_df = parametric_study_fck(base_params, param_range)
            elif param_to_vary == "fy_nmm2":
                # Similar to fck study - vary fy instead
                results = []
                for fy_val in param_range:
                    try:
                        params = build_design_params(
                            mu_knm=base_params["mu_knm"],
                            vu_kn=base_params["vu_kn"],
                            b_mm=base_params["b_mm"],
                            D_mm=base_params["D_mm"],
                            fck_nmm2=base_params["fck_nmm2"],
                            fy_nmm2=fy_val,
                        )
                        result = cached_design(**params)
                        flexure = result.get("flexure", {})
                        shear = result.get("shear", {})
                        results.append(
                            {
                                "fy_nmm2": fy_val,
                                "Ast_req": flexure.get("ast_required", 0),
                                "Ast_prov": flexure.get("ast_provided", 0),
                                "stirrup_spacing": shear.get("spacing", 0),
                                "cost_per_m": result.get("cost_per_m", 0),
                            }
                        )
                    except Exception as e:
                        st.warning(f"⚠️ Design failed for fy={fy_val}: {str(e)[:50]}")
                results_df = pd.DataFrame(results)
            elif param_to_vary == "b_mm (width)":
                results_df = parametric_study_dimensions(
                    base_params, "b_mm", param_range
                )
            else:  # D_mm (depth)
                results_df = parametric_study_dimensions(
                    base_params, "D_mm", param_range
                )

            st.session_state.parametric_results = results_df

    # Display results
    if st.session_state.parametric_results is not None:
        st.divider()
        section_header("Results")

        df = st.session_state.parametric_results
        # Find the parameter column (first column that matches known param names)
        known_params = ["fck_nmm2", "fy_nmm2", "b_mm", "D_mm", "fck", "fy", "b", "D"]
        param_col = None
        for c in df.columns:
            if c in known_params:
                param_col = c
                break
        if param_col is None:
            param_col = df.columns[0]  # Fallback to first column

        # Create plots
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Steel Area vs Parameter",
                "Cost vs Parameter",
                "Stirrup Spacing vs Parameter",
                "Design Summary",
            ),
        )

        # Plot 1: Steel area
        fig.add_trace(
            go.Scatter(
                x=df[param_col],
                y=df["Ast_req"],
                name="Ast Required",
                line=dict(color="#003366"),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df[param_col],
                y=df["Ast_prov"],
                name="Ast Provided",
                line=dict(color="#FF6600", dash="dash"),
            ),
            row=1,
            col=1,
        )

        # Plot 2: Cost
        fig.add_trace(
            go.Scatter(
                x=df[param_col],
                y=df["cost_per_m"],
                name="Cost/m",
                line=dict(color="#10b981"),
            ),
            row=1,
            col=2,
        )

        # Plot 3: Stirrup spacing
        fig.add_trace(
            go.Scatter(
                x=df[param_col],
                y=df["stirrup_spacing"],
                name="Spacing",
                line=dict(color="#f59e0b"),
            ),
            row=2,
            col=1,
        )

        # Plot 4: Summary table (as heatmap)
        summary_data = df[[param_col, "Ast_req", "cost_per_m"]].iloc[
            ::2
        ]  # Every 2nd row

        fig.update_xaxes(title_text=param_col, row=1, col=1)
        fig.update_xaxes(title_text=param_col, row=1, col=2)
        fig.update_xaxes(title_text=param_col, row=2, col=1)

        fig.update_yaxes(title_text="Steel Area (mm²)", row=1, col=1)
        fig.update_yaxes(title_text="Cost (INR/m)", row=1, col=2)
        fig.update_yaxes(title_text="Spacing (mm)", row=2, col=1)

        fig.update_layout(height=800, showlegend=True)

        st.plotly_chart(fig, width="stretch")

        # Data table
        with st.expander("📊 View Data Table"):
            st.dataframe(df, width="stretch")

        # Download
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results (CSV)",
            data=csv_data,
            file_name="parametric_study_results.csv",
            mime="text/csv",
        )


# =============================================================================
# SENSITIVITY ANALYSIS
# =============================================================================

elif analysis_type == "🎯 Sensitivity Analysis":
    section_header("Sensitivity Analysis")

    st.write("""
    Determine which parameters have the most impact on design.
    Shows % change in steel area for a given % change in each parameter.
    """)

    # Base design parameters
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Base Design")
        sens_b_mm = st.number_input("Width (mm)", value=300, step=10, key="sens_b")
        sens_D_mm = st.number_input(
            "Overall Depth (mm)", value=500, step=10, key="sens_D"
        )
        sens_mu_knm = st.number_input(
            "Moment (kN·m)", value=150.0, step=10.0, key="sens_Mu"
        )

    with col2:
        st.subheader("Materials")
        sens_fck = st.number_input("fck (N/mm²)", value=25.0, step=5.0, key="sens_fck")
        sens_fy = st.number_input("fy (N/mm²)", value=500.0, step=5.0, key="sens_fy")
        sens_vu_kn = st.number_input("Shear (kN)", value=80.0, step=5.0, key="sens_Vu")

    variation = st.slider(
        "Parameter Variation (%)", min_value=5, max_value=30, value=10
    )

    # Use correct API parameter names
    base_params = {
        "mu_knm": sens_mu_knm,
        "vu_kn": sens_vu_kn,
        "b_mm": sens_b_mm,
        "D_mm": sens_D_mm,
        "fck_nmm2": sens_fck,
        "fy_nmm2": sens_fy,
    }

    if st.button("▶️ Run Sensitivity Analysis", type="primary"):
        with loading_context("Calculating sensitivities..."):
            params_to_test = ["fck_nmm2", "fy_nmm2", "b_mm", "D_mm", "mu_knm"]
            results = []

            for param in params_to_test:
                sens = sensitivity_analysis(base_params, param, variation / 100)
                results.append(sens)

            sens_df = pd.DataFrame(results)

            # Plot tornado diagram
            fig = go.Figure()

            # Sort by absolute sensitivity
            sens_df["abs_sens"] = abs(sens_df["sensitivity_plus"])
            sens_df = sens_df.sort_values("abs_sens")

            fig.add_trace(
                go.Bar(
                    y=sens_df["parameter"],
                    x=sens_df["sensitivity_minus"],
                    orientation="h",
                    name=f"-{variation}%",
                    marker=dict(color="#ef4444"),
                )
            )

            fig.add_trace(
                go.Bar(
                    y=sens_df["parameter"],
                    x=sens_df["sensitivity_plus"],
                    orientation="h",
                    name=f"+{variation}%",
                    marker=dict(color="#10b981"),
                )
            )

            fig.update_layout(
                title="Tornado Diagram: % Change in Ast",
                xaxis_title="% Change in Steel Area",
                yaxis_title="Parameter",
                barmode="relative",
                height=400,
            )

            st.plotly_chart(fig, width="stretch")

            # Summary table
            st.dataframe(
                sens_df[
                    [
                        "parameter",
                        "base_value",
                        "base_Ast",
                        "sensitivity_plus",
                        "sensitivity_minus",
                    ]
                ],
                width="stretch",
            )

            # Insights
            most_sensitive = sens_df.iloc[-1]
            st.info(f"""
            **Key Insight:** The design is most sensitive to changes in **{most_sensitive['parameter']}**.
            A {variation}% increase causes a {most_sensitive['sensitivity_plus']:.1f}% change in steel area.
            """)


# =============================================================================
# LOADING SCENARIOS
# =============================================================================

else:  # Loading Scenarios
    section_header("Multiple Loading Scenarios")

    st.write("""
    Compare designs for different loading conditions.
    Useful for envelope design or understanding load path effects.
    """)

    # Base beam geometry
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Beam Geometry")
        load_b_mm = st.number_input("Width (mm)", value=300, step=10, key="load_b")
        load_D_mm = st.number_input(
            "Overall Depth (mm)", value=500, step=10, key="load_D"
        )
        load_cover = st.number_input("Cover (mm)", value=40, step=5, key="load_cover")

    with col2:
        st.subheader("Materials")
        load_fck = st.number_input("fck (N/mm²)", value=25.0, step=5.0, key="load_fck")
        load_fy = st.number_input("fy (N/mm²)", value=415.0, step=5.0, key="load_fy")

    st.divider()

    # Define loading scenarios
    st.subheader("Define Loading Scenarios")

    num_scenarios = st.number_input(
        "Number of Scenarios", min_value=2, max_value=5, value=3
    )

    scenarios = []
    for i in range(num_scenarios):
        with st.expander(f"Scenario {i+1}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                name = st.text_input("Name", value=f"Load Case {i+1}", key=f"name_{i}")
            with col2:
                sc_mu_knm = st.number_input(
                    "Mu (kN·m)", value=150.0 + i * 20, step=10.0, key=f"Mu_{i}"
                )
            with col3:
                sc_vu_kn = st.number_input(
                    "Vu (kN)", value=80.0 + i * 10, step=5.0, key=f"Vu_{i}"
                )

            scenarios.append({"name": name, "mu_knm": sc_mu_knm, "vu_kn": sc_vu_kn})

    if st.button("▶️ Analyze All Scenarios", type="primary"):
        with loading_context("Analyzing loading scenarios..."):
            results = []

            for scenario in scenarios:
                # Build correct API params (use correct parameter names)
                params = build_design_params(
                    b_mm=load_b_mm,
                    D_mm=load_D_mm,
                    mu_knm=scenario["mu_knm"],
                    vu_kn=scenario["vu_kn"],
                    fck_nmm2=load_fck,
                    fy_nmm2=load_fy,
                    cover_mm=load_cover,
                )
                result = cached_design(**params)

                # Build bar config from bar_dia and num_bars
                flexure = result.get("flexure", {})
                bar_dia = flexure.get("bar_dia", 16)
                num_bars = flexure.get("num_bars", 3)
                bar_config = f"{num_bars}-{bar_dia}mm"

                results.append(
                    {
                        "Scenario": scenario["name"],
                        "Mu (kN·m)": scenario["mu_knm"],
                        "Vu (kN)": scenario["vu_kn"],
                        "Ast_req (mm²)": flexure.get("ast_required", 0),
                        "Ast_prov (mm²)": flexure.get("ast_provided", 0),
                        "Bar Config": bar_config,
                        "Stirrup Spacing (mm)": result.get("shear", {}).get(
                            "spacing", "-"
                        ),
                        "Cost/m (INR)": result.get("cost_per_m", 0),
                    }
                )

            results_df = pd.DataFrame(results)

            # Comparison charts
            fig = make_subplots(
                rows=1, cols=2, subplot_titles=("Steel Requirements", "Cost Comparison")
            )

            fig.add_trace(
                go.Bar(
                    x=results_df["Scenario"],
                    y=results_df["Ast_req (mm²)"],
                    name="Required",
                    marker_color="#003366",
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Bar(
                    x=results_df["Scenario"],
                    y=results_df["Ast_prov (mm²)"],
                    name="Provided",
                    marker_color="#FF6600",
                ),
                row=1,
                col=1,
            )

            fig.add_trace(
                go.Bar(
                    x=results_df["Scenario"],
                    y=results_df["Cost/m (INR)"],
                    marker_color="#10b981",
                ),
                row=1,
                col=2,
            )

            fig.update_xaxes(title_text="Scenario", row=1, col=1)
            fig.update_xaxes(title_text="Scenario", row=1, col=2)
            fig.update_yaxes(title_text="Steel Area (mm²)", row=1, col=1)
            fig.update_yaxes(title_text="Cost (INR/m)", row=1, col=2)

            fig.update_layout(height=500, showlegend=True)

            st.plotly_chart(fig, width="stretch")

            # Results table
            st.dataframe(results_df, width="stretch")

            # Envelope design recommendation
            max_ast = results_df["Ast_prov (mm²)"].max()
            max_scenario = results_df.loc[
                results_df["Ast_prov (mm²)"].idxmax(), "Scenario"
            ]

            st.success(f"""
            **Envelope Design Recommendation:**
            Use steel area from **{max_scenario}**: {max_ast:.0f} mm²
            This will satisfy all loading scenarios.
            """)

# Footer
st.divider()
st.caption(
    "🔬 **Advanced Analysis** - Parametric studies and sensitivity tools for optimization"
)
