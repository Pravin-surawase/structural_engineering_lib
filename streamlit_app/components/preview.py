"""
Real-Time Preview Component
===========================

Provides instant visual feedback as users modify beam design inputs.

Features:
- Beam elevation diagram with support symbols
- Quick design checks (span/d, cover, b/D ratios)
- Color-coded status dashboard
- Rough cost estimate

Author: Agent 6 implementing UI-IMPLEMENTATION-AGENT-GUIDE
Status: 🆕 NEW COMPONENT
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Dict, List

# Import design system
from utils.design_system import COLORS, ANIMATION


def render_real_time_preview(
    span_mm: float,
    b_mm: float,
    D_mm: float,
    d_mm: float,
    concrete_grade: str,
    steel_grade: str,
    mu_knm: float,
    vu_kn: float,
    exposure: str,
    support_condition: str
) -> None:
    """
    Render the complete real-time preview panel.

    This is the main entry point for the preview component.
    Called from beam_design.py in col_preview context.

    Args:
        span_mm: Beam span in millimeters
        b_mm: Beam width in millimeters
        D_mm: Total beam depth in millimeters
        d_mm: Effective depth in millimeters
        concrete_grade: e.g., "M25", "M30"
        steel_grade: e.g., "Fe500", "Fe415"
        mu_knm: Design moment in kN·m
        vu_kn: Design shear in kN
        exposure: Exposure condition string
        support_condition: e.g., "Simply Supported", "Cantilever"
    """
    # Section 1: Beam Diagram
    st.subheader("🏗️ Beam Elevation")
    fig = create_beam_preview_diagram(
        span_mm=span_mm,
        b_mm=b_mm,
        D_mm=D_mm,
        support_condition=support_condition
    )
    st.plotly_chart(fig, width="stretch", key="preview_beam_diagram")

    # Section 2: Quick Checks
    st.subheader("✅ Design Checks")
    checks = calculate_quick_checks(
        span_mm=span_mm,
        d_mm=d_mm,
        b_mm=b_mm,
        D_mm=D_mm,
        exposure=exposure
    )
    render_status_dashboard(checks)

    # Section 3: Rough Cost
    st.subheader("💰 Preliminary Cost")
    cost = calculate_rough_cost(
        b_mm=b_mm,
        D_mm=D_mm,
        span_mm=span_mm,
        concrete_grade=concrete_grade,
        mu_knm=mu_knm
    )
    render_cost_summary(cost)


def create_beam_preview_diagram(
    span_mm: float,
    b_mm: float,
    D_mm: float,
    support_condition: str
) -> go.Figure:
    """
    Create a simple beam elevation diagram with supports.

    Args:
        span_mm: Beam span
        b_mm: Beam width (for label)
        D_mm: Beam depth (for scale)
        support_condition: Determines support symbols

    Returns:
        Plotly figure with beam diagram
    """
    fig = go.Figure()

    # Scale: fit 0-100 coordinate system
    # Beam drawn from x=10 to x=90 (80% of width)
    beam_left = 10
    beam_right = 90
    beam_top = 60
    beam_bottom = 40

    # Draw beam (gray rectangle)
    fig.add_shape(
        type="rect",
        x0=beam_left, y0=beam_bottom,
        x1=beam_right, y1=beam_top,
        fillcolor="rgba(200, 200, 200, 0.5)",
        line=dict(color=COLORS.primary_500, width=2)
    )

    # Beam label
    fig.add_annotation(
        x=50, y=50,
        text=f"{span_mm/1000:.1f}m × {b_mm}×{D_mm}mm",
        showarrow=False,
        font=dict(size=12, color=COLORS.gray_700)
    )

    # Support symbols based on condition
    if support_condition == "Simply Supported":
        # Left support: triangle (pinned)
        _add_triangle_support(fig, beam_left, beam_bottom)
        # Right support: triangle with roller
        _add_roller_support(fig, beam_right, beam_bottom)
    elif support_condition == "Cantilever":
        # Fixed support at left
        _add_fixed_support(fig, beam_left, beam_bottom, beam_top)
        # Free end at right (no support)
    elif support_condition == "Fixed-Fixed":
        _add_fixed_support(fig, beam_left, beam_bottom, beam_top)
        _add_fixed_support(fig, beam_right, beam_bottom, beam_top)
    else:
        # Default: simply supported
        _add_triangle_support(fig, beam_left, beam_bottom)
        _add_roller_support(fig, beam_right, beam_bottom)

    # Layout
    fig.update_layout(
        showlegend=False,
        xaxis=dict(visible=False, range=[0, 100]),
        yaxis=dict(visible=False, range=[0, 100], scaleanchor="x"),
        margin=dict(l=10, r=10, t=10, b=10),
        height=200,
        paper_bgcolor='white',
        plot_bgcolor='white',
        # Use integer duration for Plotly (CRITICAL!)
        transition=dict(duration=ANIMATION.duration_normal_ms, easing='cubic-in-out')
    )

    return fig


def _add_triangle_support(fig: go.Figure, x: float, y: float) -> None:
    """Add triangular (pinned) support symbol."""
    size = 5
    fig.add_trace(go.Scatter(
        x=[x - size, x, x + size, x - size],
        y=[y - size, y, y - size, y - size],
        fill="toself",
        fillcolor=COLORS.gray_400,
        line=dict(color=COLORS.gray_600, width=1),
        mode="lines",
        hoverinfo="skip",
        showlegend=False
    ))


def _add_roller_support(fig: go.Figure, x: float, y: float) -> None:
    """Add roller support symbol (triangle + circle)."""
    size = 5
    # Triangle
    fig.add_trace(go.Scatter(
        x=[x - size, x, x + size, x - size],
        y=[y - size - 3, y - 3, y - size - 3, y - size - 3],
        fill="toself",
        fillcolor=COLORS.gray_400,
        line=dict(color=COLORS.gray_600, width=1),
        mode="lines",
        hoverinfo="skip",
        showlegend=False
    ))
    # Circles (rollers)
    for dx in [-3, 0, 3]:
        fig.add_shape(
            type="circle",
            x0=x + dx - 1.5, y0=y - size - 5,
            x1=x + dx + 1.5, y1=y - size - 2,
            fillcolor=COLORS.gray_300,
            line=dict(color=COLORS.gray_500, width=1)
        )


def _add_fixed_support(fig: go.Figure, x: float, y_bottom: float, y_top: float) -> None:
    """Add fixed support symbol (hatched rectangle)."""
    width = 5
    if x < 50:  # Left side
        x0 = x - width
        x1 = x
    else:  # Right side
        x0 = x
        x1 = x + width

    fig.add_shape(
        type="rect",
        x0=x0, y0=y_bottom,
        x1=x1, y1=y_top,
        fillcolor="rgba(100, 100, 100, 0.3)",
        line=dict(color=COLORS.gray_600, width=2)
    )
    # Hatching lines
    for i in range(5):
        y = y_bottom + i * (y_top - y_bottom) / 4
        fig.add_shape(
            type="line",
            x0=x0, y0=y,
            x1=x1, y1=y + 3,
            line=dict(color=COLORS.gray_600, width=1)
        )


def calculate_quick_checks(
    span_mm: float,
    d_mm: float,
    b_mm: float,
    D_mm: float,
    exposure: str
) -> List[Dict]:
    """
    Calculate quick design checks for status dashboard.

    Returns list of check results, each with:
    - name: Check name
    - status: "pass", "warning", or "fail"
    - value: Current value
    - limit: Limit or reference value
    - message: Human-readable message
    """
    checks = []

    # Check 1: Span/d ratio (IS 456 Cl. 23.2.1)
    span_d = span_mm / d_mm if d_mm > 0 else float('inf')
    span_d_limit = 20  # Simply supported basic limit
    if span_d <= span_d_limit:
        status = "pass"
        message = f"OK ({span_d:.1f} ≤ {span_d_limit})"
    elif span_d <= span_d_limit * 1.2:
        status = "warning"
        message = f"Review ({span_d:.1f} > {span_d_limit})"
    else:
        status = "fail"
        message = f"Exceeds ({span_d:.1f} >> {span_d_limit})"

    checks.append({
        "name": "Span/d Ratio",
        "status": status,
        "value": round(span_d, 1),
        "limit": span_d_limit,
        "message": message,
        "clause": "IS 456 Cl. 23.2.1"
    })

    # Check 2: Cover adequacy
    cover_required = _get_min_cover(exposure)
    cover_available = (D_mm - d_mm)  # Approximate from effective depth
    if cover_available >= cover_required:
        status = "pass"
        message = f"OK ({cover_available:.0f}mm ≥ {cover_required}mm)"
    elif cover_available >= cover_required * 0.9:
        status = "warning"
        message = f"Marginal ({cover_available:.0f}mm ~ {cover_required}mm)"
    else:
        status = "fail"
        message = f"Insufficient ({cover_available:.0f}mm < {cover_required}mm)"

    checks.append({
        "name": "Cover",
        "status": status,
        "value": round(cover_available, 0),
        "limit": cover_required,
        "message": message,
        "clause": "IS 456 Cl. 26.4"
    })

    # Check 3: b/D ratio (reasonable proportions)
    b_D = b_mm / D_mm if D_mm > 0 else 0
    if 0.3 <= b_D <= 0.67:
        status = "pass"
        message = f"Good proportions ({b_D:.2f})"
    elif 0.25 <= b_D <= 0.75:
        status = "warning"
        message = f"Unusual ({b_D:.2f})"
    else:
        status = "fail"
        message = f"Check proportions ({b_D:.2f})"

    checks.append({
        "name": "b/D Ratio",
        "status": status,
        "value": round(b_D, 2),
        "limit": "0.3-0.67",
        "message": message,
        "clause": "Practice"
    })

    # Check 4: d < D
    if d_mm < D_mm:
        status = "pass"
        message = "OK"
    else:
        status = "fail"
        message = f"d ({d_mm}) must be < D ({D_mm})"

    checks.append({
        "name": "d < D",
        "status": status,
        "value": d_mm,
        "limit": D_mm,
        "message": message,
        "clause": "Basic"
    })

    return checks


def _get_min_cover(exposure: str) -> int:
    """Get minimum cover per IS 456 Table 16."""
    cover_map = {
        "Mild": 20,
        "Moderate": 30,
        "Severe": 45,
        "Very Severe": 50,
        "Extreme": 75
    }
    return cover_map.get(exposure, 30)


def render_status_dashboard(checks: List[Dict]) -> None:
    """
    Render color-coded status dashboard.

    Args:
        checks: List of check dicts from calculate_quick_checks()
    """
    # Create columns for checks
    cols = st.columns(len(checks))

    for i, check in enumerate(checks):
        with cols[i]:
            # Status indicator
            if check["status"] == "pass":
                icon = "✅"
                color = COLORS.success
            elif check["status"] == "warning":
                icon = "⚠️"
                color = COLORS.warning
            else:
                icon = "❌"
                color = COLORS.error

            # Render metric-like display
            st.markdown(f"""
            <div style="
                padding: 8px;
                border-radius: 8px;
                background: {color}15;
                border-left: 4px solid {color};
                text-align: center;
            ">
                <div style="font-size: 20px;">{icon}</div>
                <div style="font-weight: 600; font-size: 12px; color: {COLORS.gray_700};">
                    {check['name']}
                </div>
                <div style="font-size: 11px; color: {COLORS.gray_500};">
                    {check['message']}
                </div>
            </div>
            """, unsafe_allow_html=True)


def calculate_rough_cost(
    b_mm: float,
    D_mm: float,
    span_mm: float,
    concrete_grade: str,
    mu_knm: float
) -> Dict:
    """
    Calculate rough cost estimate for beam.

    Uses simplified assumptions:
    - Concrete volume = b × D × span
    - Steel estimate from moment (empirical formula)
    - Standard rates (approximate)

    Returns dict with cost breakdown.
    """
    # Convert to meters
    b_m = b_mm / 1000
    D_m = D_mm / 1000
    span_m = span_mm / 1000

    # Concrete volume (m³)
    volume_m3 = b_m * D_m * span_m

    # Concrete rate (₹/m³) - approximate
    concrete_rates = {
        "M20": 5500,
        "M25": 6000,
        "M30": 6500,
        "M35": 7500,
        "M40": 8500
    }
    concrete_rate = concrete_rates.get(concrete_grade, 6000)
    concrete_cost = volume_m3 * concrete_rate

    # Steel estimate (kg) - rough empirical: 80-120 kg/m³ concrete
    steel_kg_per_m3 = 100  # Middle estimate
    steel_kg = volume_m3 * steel_kg_per_m3

    # Adjust for moment intensity (higher moment = more steel)
    moment_factor = min(max(mu_knm / 100, 0.5), 2.0)  # Scale 0.5-2.0
    steel_kg *= moment_factor

    # Steel rate (₹/kg) - approximate
    steel_rate = 85
    steel_cost = steel_kg * steel_rate

    # Total
    total_cost = concrete_cost + steel_cost

    return {
        "concrete_m3": round(volume_m3, 3),
        "concrete_rate": concrete_rate,
        "concrete_cost": round(concrete_cost, 0),
        "steel_kg": round(steel_kg, 1),
        "steel_rate": steel_rate,
        "steel_cost": round(steel_cost, 0),
        "total_cost": round(total_cost, 0)
    }


def render_cost_summary(cost: Dict) -> None:
    """
    Render cost summary in compact format.

    Args:
        cost: Dict from calculate_rough_cost()
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Concrete",
            value=f"₹{cost['concrete_cost']:,.0f}",
            help=f"{cost['concrete_m3']} m³ @ ₹{cost['concrete_rate']}/m³"
        )

    with col2:
        st.metric(
            label="Steel (est.)",
            value=f"₹{cost['steel_cost']:,.0f}",
            help=f"~{cost['steel_kg']:.0f} kg @ ₹{cost['steel_rate']}/kg"
        )

    with col3:
        st.metric(
            label="Total (approx.)",
            value=f"₹{cost['total_cost']:,.0f}",
            help="Preliminary estimate only"
        )

    st.caption("⚠️ Estimates are approximate. Actual costs depend on detailed design.")


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "render_real_time_preview",
    "create_beam_preview_diagram",
    "calculate_quick_checks",
    "render_status_dashboard",
    "calculate_rough_cost",
    "render_cost_summary"
]
