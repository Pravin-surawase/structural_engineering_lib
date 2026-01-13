"""
Design System Demo - Visual showcase of all design tokens and components.

Run with: streamlit run streamlit_app/utils/design_system_demo.py

This file demonstrates all features of the UI-001 Design System.
"""

import streamlit as st
import plotly.graph_objects as go

# Import design system
from design_system import COLORS, TYPOGRAPHY, SPACING, ELEVATION, RADIUS
from plotly_theme import apply_theme, get_chart_config
from styled_components import (
    styled_card,
    status_badge,
    metric_card,
    alert_box,
    progress_bar,
    styled_table,
    divider,
)
from global_styles import get_global_css

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="IS 456 Design System Demo",
    page_icon="🎨",
    layout="wide",
)

# Inject global CSS
st.markdown(f"<style>{get_global_css()}</style>", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================

st.title("🎨 IS 456 Design System Demo")
st.markdown("**UI-001 Implementation Showcase** - All design tokens and components")

divider()

# ============================================================================
# COLOR PALETTE
# ============================================================================

st.header("1. Color Palette")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Primary (Navy)")
    st.markdown(
        f"""
    <div style="background: {COLORS.primary_500}; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 10px;">
        <strong>Primary 500</strong><br>{COLORS.primary_500}
    </div>
    """,
        unsafe_allow_html=True,
    )

with col2:
    st.subheader("Accent (Orange)")
    st.markdown(
        f"""
    <div style="background: {COLORS.accent_500}; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 10px;">
        <strong>Accent 500</strong><br>{COLORS.accent_500}
    </div>
    """,
        unsafe_allow_html=True,
    )

with col3:
    st.subheader("Semantic Colors")
    for label, color in [
        ("Success", COLORS.success),
        ("Warning", COLORS.warning),
        ("Error", COLORS.error),
        ("Info", COLORS.info),
    ]:
        st.markdown(
            f"""
        <div style="background: {color}; color: white; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 5px; font-size: 14px;">
            {label}: {color}
        </div>
        """,
            unsafe_allow_html=True,
        )

divider()

# ============================================================================
# TYPOGRAPHY
# ============================================================================

st.header("2. Typography System")

st.markdown(
    f"""
<h1 style="font-size: {TYPOGRAPHY.h1_size};">Heading 1 - {TYPOGRAPHY.h1_size}</h1>
<h2 style="font-size: {TYPOGRAPHY.h2_size};">Heading 2 - {TYPOGRAPHY.h2_size}</h2>
<h3 style="font-size: {TYPOGRAPHY.h3_size};">Heading 3 - {TYPOGRAPHY.h3_size}</h3>
<h4 style="font-size: {TYPOGRAPHY.h4_size};">Heading 4 - {TYPOGRAPHY.h4_size}</h4>
<p style="font-size: {TYPOGRAPHY.body_size};">Body text - {TYPOGRAPHY.body_size}</p>
<p style="font-size: {TYPOGRAPHY.body_sm_size};">Small text - {TYPOGRAPHY.body_sm_size}</p>
<p style="font-family: {TYPOGRAPHY.font_mono}; font-size: {TYPOGRAPHY.body_size};">Monospace (numbers): 1234.56 mm²</p>
""",
    unsafe_allow_html=True,
)

divider()

# ============================================================================
# SPACING SYSTEM
# ============================================================================

st.header("3. Spacing System")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Base Unit: 8px")
    for i in range(0, 11):
        space = getattr(SPACING, f"space_{i}")
        st.markdown(
            f"""
        <div style="background: {COLORS.primary_100}; height: 20px; width: {space}; margin-bottom: 5px; display: inline-block;"></div>
        <span style="margin-left: 10px;">space_{i} = {space}</span>
        """,
            unsafe_allow_html=True,
        )

with col2:
    st.subheader("Elevation Levels")
    for i in range(1, 5):
        shadow = getattr(ELEVATION, f"level_{i}")
        st.markdown(
            f"""
        <div style="background: white; padding: 20px; margin-bottom: 10px; border-radius: 8px; box-shadow: {shadow};">
            Level {i} Elevation
        </div>
        """,
            unsafe_allow_html=True,
        )

divider()

# ============================================================================
# STYLED COMPONENTS
# ============================================================================

st.header("4. Styled Components")

# Status badges
st.subheader("Status Badges")
st.markdown(
    status_badge("Compliant", "success")
    + " "
    + status_badge("Warning", "warning")
    + " "
    + status_badge("Error", "error")
    + " "
    + status_badge("Info", "info"),
    unsafe_allow_html=True,
)

st.markdown("")

# Metric cards
st.subheader("Metric Cards")
col1, col2, col3, col4 = st.columns(4)

with col1:
    metric_card(
        label="Steel Area",
        value="1200",
        unit="mm²",
        delta="+50 vs minimum",
        delta_color="success",
    )

with col2:
    metric_card(
        label="Utilization",
        value="85.5",
        unit="%",
        delta="Within limits",
        delta_color="success",
    )

with col3:
    metric_card(
        label="Moment",
        value="125.4",
        unit="kN·m",
        help_text="Factored design moment",
    )

with col4:
    metric_card(label="Shear", value="78.2", unit="kN", delta="Critical", delta_color="warning")

# Alert boxes
st.subheader("Alert Boxes")
alert_box("Design complies with IS 456:2000 requirements", "success", icon="✓")
alert_box("Steel area is near minimum - consider increasing", "warning", icon="⚠")
alert_box("Shear capacity exceeded! Increase section depth", "error", icon="✕")
alert_box("Refer to Clause 26.5.1.5 for detailing requirements", "info", icon="ℹ")

# Progress bars
st.subheader("Progress Bars")
progress_bar(value=45, max_value=100, label="Flexural Utilization", color=COLORS.success)
progress_bar(value=78, max_value=100, label="Shear Utilization", color=COLORS.warning)
progress_bar(value=92, max_value=100, label="Serviceability Check", color=COLORS.error)

# Data table
st.subheader("Styled Table")
styled_table(
    headers=["Parameter", "Value", "Unit", "Status"],
    rows=[
        ["Width (b)", "300", "mm", status_badge("✓", "success")],
        ["Depth (D)", "500", "mm", status_badge("✓", "success")],
        ["Clear Cover", "25", "mm", status_badge("✓", "success")],
        ["Steel Area", "1200", "mm²", status_badge("⚠", "warning")],
    ],
    align=["left", "right", "left", "center"],
)

divider()

# ============================================================================
# PLOTLY CHARTS
# ============================================================================

st.header("5. Plotly Theme")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Bar Chart")
    fig1 = go.Figure(
        data=[
            go.Bar(x=["Option A", "Option B", "Option C"], y=[1200, 1350, 1180], name="Steel Area (mm²)")
        ]
    )
    apply_theme(fig1)
    fig1.update_layout(title="Steel Area Comparison", height=400)
    st.plotly_chart(fig1, config=get_chart_config(), width="stretch")

with col2:
    st.subheader("Scatter Plot")
    fig2 = go.Figure(
        data=[
            go.Scatter(
                x=[50, 60, 70, 80, 90],
                y=[1000, 1200, 1400, 1600, 1800],
                mode="markers+lines",
                name="Cost vs Utilization",
            )
        ]
    )
    apply_theme(fig2)
    fig2.update_layout(
        title="Cost Optimization",
        xaxis_title="Utilization (%)",
        yaxis_title="Cost (₹)",
        height=400,
    )
    st.plotly_chart(fig2, config=get_chart_config(), width="stretch")

# Gauge chart
st.subheader("Utilization Gauge")
fig3 = go.Figure(
    go.Indicator(
        mode="gauge+number+delta",
        value=85.5,
        title={"text": "Utilization Ratio"},
        delta={"reference": 100},
        gauge={
            "axis": {"range": [None, 100]},
            "bar": {"color": COLORS.primary_500},
            "steps": [
                {"range": [0, 70], "color": COLORS.success_light},
                {"range": [70, 85], "color": COLORS.warning_light},
                {"range": [85, 100], "color": COLORS.error_light},
            ],
            "threshold": {
                "line": {"color": COLORS.error, "width": 4},
                "thickness": 0.75,
                "value": 90,
            },
        },
    )
)
apply_theme(fig3)
fig3.update_layout(height=300)
st.plotly_chart(fig3, config=get_chart_config(interactive=False), width="stretch")

divider()

# ============================================================================
# RESPONSIVE DEMO
# ============================================================================

st.header("6. Responsive Layout")
st.markdown("*Resize browser window to see responsive behavior*")

# Grid of cards
col1, col2, col3 = st.columns(3)

for i, col in enumerate([col1, col2, col3], 1):
    with col:
        styled_card(
            title=f"Card {i}",
            content=f"""
            <p>Responsive card that stacks on mobile devices.</p>
            <p style="font-family: {TYPOGRAPHY.font_mono}; color: {COLORS.primary_500};">
                Value: {i * 100} mm²
            </p>
            """,
            elevation=2,
        )

divider()

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption(
    """
**Design System v1.0** | UI-001 Implementation | Agent 6 (Streamlit Specialist)
Based on: RESEARCH-004, RESEARCH-005, RESEARCH-006
WCAG 2.1 AA Compliant | Colorblind-Safe | Responsive Design
"""
)
