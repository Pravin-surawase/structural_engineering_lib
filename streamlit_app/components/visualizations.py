"""
Visualization Components
========================

Reusable chart and diagram components using Plotly.

Components:
- create_beam_diagram() - Cross-section with rebar positions
- create_cost_comparison() - Bar chart of alternatives
- create_utilization_gauge() - Semicircular gauge with zones
- create_sensitivity_tornado() - Tornado diagram
- create_compliance_visual() - IS 456 compliance checklist

All visualizations follow:
- IS 456 color theme (Navy #003366, Orange #FF6600)
- WCAG 2.1 AA accessibility (colorblind-safe)
- Interactive Plotly features
- Responsive design

Author: STREAMLIT UI SPECIALIST (Agent 6)
Status: ✅ UPGRADED (STREAMLIT-UI-003)
Version: 2.0 - Modern Design System Integration
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Tuple, Optional
import streamlit as st

# Import design system
try:
    from utils.design_system import COLORS, TYPOGRAPHY, SPACING, ELEVATION, ANIMATION
except ImportError:
    # Fallback if design_system not available
    class COLORS:
        primary_500 = "#003366"
        accent_500 = "#FF6600"
        success = "#10B981"
        warning = "#F59E0B"
        error = "#EF4444"
        gray_100 = "#F5F5F5"
        gray_500 = "#737373"
        gray_900 = "#171717"

    class TYPOGRAPHY:
        font_ui = "Inter"
        h3_size = "20px"
        body_size = "14px"

    class SPACING:
        space_4 = "16px"

    class ELEVATION:
        level_1 = "0 1px 3px rgba(0,0,0,0.1)"

    class ANIMATION:
        duration_normal = 200


# Theme colors (using design system)
THEME_NAVY = COLORS.primary_500
THEME_ORANGE = COLORS.accent_500
THEME_GREEN = COLORS.success
THEME_YELLOW = COLORS.warning
THEME_RED = COLORS.error
THEME_LIGHT_GRAY = COLORS.gray_100

# Colorblind-safe palette (enhanced)
CB_SAFE_BLUE = "#0173B2"
CB_SAFE_ORANGE = "#DE8F05"
CB_SAFE_GREEN = "#029E73"
CB_SAFE_RED = "#CC3311"
CB_SAFE_PURPLE = "#949494"


def get_plotly_theme() -> Dict:
    """
    Get unified Plotly theme based on design system.

    Returns consistent styling across all visualizations:
    - Typography (Inter font family)
    - Colors (Design system palette)
    - Layout spacing and margins
    - Hover and interaction styles
    """
    return {
        "font_family": TYPOGRAPHY.font_ui,
        "font_color": COLORS.gray_900,
        "paper_bgcolor": "white",
        "plot_bgcolor": "white",
        "grid_color": COLORS.gray_100,
        "title_font_size": 18,
        "title_font_weight": 600,
        "axis_font_size": 12,
        "legend_bgcolor": "rgba(255,255,255,0.95)",
        "legend_border_color": COLORS.gray_200,
        "legend_border_width": 1,
        "hover_bgcolor": COLORS.gray_50,
        "hover_border_color": COLORS.primary_500,
    }


def create_beam_diagram(
    b_mm: float,
    D_mm: float,
    d_mm: float,
    rebar_positions: List[Tuple[float, float]],
    xu: float,
    bar_dia: float,
    cover: float = 30.0,
    show_dimensions: bool = True,
    compression_positions: Optional[List[Tuple[float, float]]] = None,
    stirrup_dia: float = 8.0,
    stirrup_spacing: float = 150.0,
) -> go.Figure:
    """
    Create interactive beam cross-section diagram with rebar placement.

    Features:
    - Concrete section (gray rectangle)
    - Tension rebar positions (orange circles)
    - Compression rebar positions (purple circles) - for doubly reinforced
    - Stirrups (dashed rectangles)
    - Neutral axis (red dashed line)
    - Compression/tension zones (shaded)
    - Cover lines (blue dotted)
    - Dimensions (annotations)
    - Interactive hover tooltips

    Args:
        b_mm: Width (mm)
        D_mm: Total depth (mm)
        d_mm: Effective depth (mm)
        rebar_positions: [(x1, y1), (x2, y2), ...] tension steel in mm from bottom-left
        xu: Neutral axis depth from top (mm)
        bar_dia: Main tension bar diameter (mm)
        cover: Clear cover (mm)
        show_dimensions: Show dimension annotations
        compression_positions: [(x1, y1), ...] compression steel positions (optional)
        stirrup_dia: Stirrup diameter (mm)
        stirrup_spacing: Stirrup spacing (mm c/c)

    Returns:
        Plotly figure

    Example:
        >>> tension_pos = [(75, 50), (150, 50), (225, 50)]  # 3 bars at bottom
        >>> comp_pos = [(75, 450), (225, 450)]  # 2 bars at top
        >>> fig = create_beam_diagram(300, 500, 450, tension_pos, 150, 16,
        ...                           compression_positions=comp_pos)
        >>> st.plotly_chart(fig, width="stretch")
    """
    fig = go.Figure()

    # Handle None xu (before design is computed)
    xu_valid = xu is not None and xu > 0

    # 1. Concrete section (light gray rectangle)
    fig.add_trace(
        go.Scatter(
            x=[0, b_mm, b_mm, 0, 0],
            y=[0, 0, D_mm, D_mm, 0],
            fill="toself",
            fillcolor="rgba(200, 200, 200, 0.3)",
            line=dict(color=THEME_NAVY, width=2),
            mode="lines",
            name="Concrete Section",
            hovertemplate=f"Beam Section<br>Width: {b_mm}mm<br>Depth: {D_mm}mm<extra></extra>",
        )
    )

    # 2. Compression zone (light blue shading above neutral axis)
    if xu_valid:
        fig.add_trace(
            go.Scatter(
                x=[0, b_mm, b_mm, 0, 0],
                y=[D_mm, D_mm, D_mm - xu, D_mm - xu, D_mm],
                fill="toself",
                fillcolor="rgba(0, 115, 178, 0.15)",  # Colorblind-safe blue
                line=dict(width=0),
                mode="lines",
                name="Compression Zone",
                hovertemplate=f"Compression Zone<br>Depth: {xu:.1f}mm<extra></extra>",
                showlegend=True,
            )
        )

    # 3. Tension zone (light orange shading below neutral axis)
    if xu_valid:
        tension_depth = D_mm - xu
        if tension_depth > 0:
            fig.add_trace(
                go.Scatter(
                    x=[0, b_mm, b_mm, 0, 0],
                    y=[0, 0, D_mm - xu, D_mm - xu, 0],
                    fill="toself",
                    fillcolor="rgba(222, 143, 5, 0.15)",  # Colorblind-safe orange
                    line=dict(width=0),
                    mode="lines",
                    name="Tension Zone",
                    hovertemplate=f"Tension Zone<br>Depth: {tension_depth:.1f}mm<extra></extra>",
                    showlegend=True,
                )
            )

    # 4. Neutral axis (red dashed line) - only if xu is valid
    if xu_valid:
        na_y = D_mm - xu
        fig.add_trace(
            go.Scatter(
                x=[0, b_mm],
                y=[na_y, na_y],
                mode="lines",
                line=dict(color=CB_SAFE_RED, width=2, dash="dash"),
                name="Neutral Axis",
                hovertemplate=f"Neutral Axis<br>xu = {xu:.1f}mm from top<extra></extra>",
            )
        )

    # 5. Effective depth line (green dashed)
    ed_y = D_mm - d_mm
    fig.add_trace(
        go.Scatter(
            x=[0, b_mm],
            y=[ed_y, ed_y],
            mode="lines",
            line=dict(color=CB_SAFE_GREEN, width=1, dash="dot"),
            name="Effective Depth",
            hovertemplate=f"Effective Depth<br>d = {d_mm}mm<extra></extra>",
        )
    )

    # 6. Cover lines (blue dotted)
    if cover > 0:
        # Bottom cover
        fig.add_trace(
            go.Scatter(
                x=[0, b_mm],
                y=[cover, cover],
                mode="lines",
                line=dict(color=CB_SAFE_BLUE, width=1, dash="dot"),
                name="Cover",
                hovertemplate=f"Clear Cover<br>{cover}mm<extra></extra>",
                showlegend=False,
            )
        )
        # Side covers
        fig.add_trace(
            go.Scatter(
                x=[cover, cover],
                y=[0, D_mm],
                mode="lines",
                line=dict(color=CB_SAFE_BLUE, width=1, dash="dot"),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[b_mm - cover, b_mm - cover],
                y=[0, D_mm],
                mode="lines",
                line=dict(color=CB_SAFE_BLUE, width=1, dash="dot"),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    # 7. Tension steel rebar positions (orange circles)
    if rebar_positions:
        rebar_x = [pos[0] for pos in rebar_positions]
        rebar_y = [pos[1] for pos in rebar_positions]

        fig.add_trace(
            go.Scatter(
                x=rebar_x,
                y=rebar_y,
                mode="markers",
                marker=dict(
                    size=bar_dia * 0.8,  # Scale to mm (approximate visual size)
                    color=THEME_ORANGE,
                    line=dict(color=THEME_NAVY, width=1),
                ),
                name=f"Tension Steel ({bar_dia}mm)",
                hovertemplate="Tension Steel<br>x: %{x:.0f}mm<br>y: %{y:.0f}mm<extra></extra>",
            )
        )

    # 8. Compression steel rebar positions (purple circles) - for doubly reinforced
    if compression_positions:
        comp_x = [pos[0] for pos in compression_positions]
        comp_y = [pos[1] for pos in compression_positions]

        fig.add_trace(
            go.Scatter(
                x=comp_x,
                y=comp_y,
                mode="markers",
                marker=dict(
                    size=bar_dia * 0.8,
                    color=CB_SAFE_PURPLE,  # Purple for compression
                    line=dict(color=THEME_NAVY, width=1),
                ),
                name=f"Compression Steel ({bar_dia}mm)",
                hovertemplate="Compression Steel<br>x: %{x:.0f}mm<br>y: %{y:.0f}mm<extra></extra>",
            )
        )

    # 9. Stirrups (dashed rectangles) - show 2 stirrups for visualization
    if stirrup_dia > 0:
        stirrup_inner_width = b_mm - 2 * cover
        stirrup_inner_height = D_mm - 2 * cover

        # Show 2 stirrups at different positions
        stirrup_positions_x = [
            cover + stirrup_inner_width * 0.25,
            cover + stirrup_inner_width * 0.75,
        ]

        for stirrup_x_offset in stirrup_positions_x:
            # Stirrup outline (simplified rectangular shape)
            fig.add_trace(
                go.Scatter(
                    x=[cover, cover, b_mm - cover, b_mm - cover, cover],
                    y=[cover, D_mm - cover, D_mm - cover, cover, cover],
                    mode="lines",
                    line=dict(color=CB_SAFE_BLUE, width=2, dash="dash"),
                    name=f"Stirrups ({stirrup_dia}mm @ {stirrup_spacing:.0f}mm)",
                    hovertemplate=f"Stirrups<br>{stirrup_dia}mm dia<br>@ {stirrup_spacing:.0f}mm c/c<extra></extra>",
                    showlegend=(
                        stirrup_x_offset == stirrup_positions_x[0]
                    ),  # Show legend only once
                )
            )

    # 10. Dimension annotations (if enabled)
    if show_dimensions:
        # Width dimension (bottom)
        fig.add_annotation(
            x=b_mm / 2,
            y=-20,
            text=f"b = {b_mm}mm",
            showarrow=False,
            font=dict(size=10, color=THEME_NAVY),
        )
        # Height dimension (right side)
        fig.add_annotation(
            x=b_mm + 30,
            y=D_mm / 2,
            text=f"D = {D_mm}mm",
            showarrow=False,
            textangle=-90,
            font=dict(size=10, color=THEME_NAVY),
        )

    # Layout configuration with design system theme
    theme = get_plotly_theme()
    fig.update_layout(
        title=dict(
            text="Beam Cross-Section",
            font=dict(
                size=theme["title_font_size"],
                color=theme["font_color"],
                family=theme["font_family"],
                weight=theme["title_font_weight"],
            ),
        ),
        xaxis=dict(
            title=dict(text="Width (mm)", font=dict(size=theme["axis_font_size"])),
            range=[-30, b_mm + 50],
            showgrid=True,
            gridcolor=theme["grid_color"],
            zeroline=False,
        ),
        yaxis=dict(
            title=dict(text="Height (mm)", font=dict(size=theme["axis_font_size"])),
            range=[-30, D_mm + 30],
            showgrid=True,
            gridcolor=theme["grid_color"],
            zeroline=False,
            scaleanchor="x",
            scaleratio=1,  # Equal aspect ratio
        ),
        plot_bgcolor=theme["plot_bgcolor"],
        paper_bgcolor=theme["paper_bgcolor"],
        font=dict(family=theme["font_family"], color=theme["font_color"]),
        hovermode="closest",
        showlegend=True,
        legend=dict(
            x=1.05,
            y=1,
            bgcolor=theme["legend_bgcolor"],
            bordercolor=theme["legend_border_color"],
            borderwidth=theme["legend_border_width"],
            font=dict(size=12),
        ),
        height=500,
        margin=dict(l=50, r=150, t=60, b=50),
        # Add subtle animation (use _ms suffix for Plotly numeric format)
        transition=dict(duration=ANIMATION.duration_normal_ms, easing="cubic-in-out"),
    )

    return fig


def create_cost_comparison(alternatives: List[Dict[str, any]]) -> go.Figure:
    """
    Create cost comparison bar chart for bar arrangements.

    Features:
    - Horizontal bar chart (easier to read labels)
    - Color coding (green for optimal, gray for others)
    - Cost values displayed on bars
    - Sorted by cost (ascending)
    - Interactive hover with details

    Args:
        alternatives: List of dicts with:
            - 'bar_arrangement': str (e.g., "3-16mm")
            - 'cost_per_meter': float (₹/m)
            - 'is_optimal': bool
            - 'area_provided': float (mm², optional)

    Returns:
        Plotly figure

    Example:
        >>> alternatives = [
        ...     {'bar_arrangement': '3-16mm', 'cost_per_meter': 87.45,
        ...      'is_optimal': True, 'area_provided': 603},
        ...     {'bar_arrangement': '2-20mm', 'cost_per_meter': 92.30,
        ...      'is_optimal': False, 'area_provided': 628}
        ... ]
        >>> fig = create_cost_comparison(alternatives)
        >>> st.plotly_chart(fig, width="stretch")
    """
    if not alternatives:
        # Empty chart
        fig = go.Figure()
        fig.add_annotation(
            text="No alternatives to compare",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray"),
        )
        return fig

    # Sort by cost (ascending)
    sorted_alts = sorted(alternatives, key=lambda x: x["cost_per_meter"])

    # Extract data
    arrangements = [alt["bar_arrangement"] for alt in sorted_alts]
    costs = [alt["cost_per_meter"] for alt in sorted_alts]
    is_optimal_list = [alt.get("is_optimal", False) for alt in sorted_alts]
    areas = [alt.get("area_provided", 0) for alt in sorted_alts]

    # Color bars (green for optimal, colorblind-safe blue for others)
    colors = [CB_SAFE_GREEN if opt else CB_SAFE_BLUE for opt in is_optimal_list]

    # Create horizontal bar chart
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=arrangements,
            x=costs,
            orientation="h",
            marker=dict(color=colors, line=dict(color=THEME_NAVY, width=1)),
            text=[f"₹{cost:.2f}/m" for cost in costs],
            textposition="outside",
            textfont=dict(size=11, color=THEME_NAVY),
            hovertemplate=(
                "<b>%{y}</b><br>"
                + "Cost: ₹%{x:.2f}/m<br>"
                + "Area: %{customdata}mm²<br>"
                + "<extra></extra>"
            ),
            customdata=areas,
            showlegend=False,
        )
    )

    # Add optimal marker
    optimal_idx = next((i for i, opt in enumerate(is_optimal_list) if opt), None)
    if optimal_idx is not None:
        fig.add_annotation(
            x=costs[optimal_idx],
            y=optimal_idx,
            text="⭐ Optimal",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=CB_SAFE_GREEN,
            ax=50,
            ay=0,
            font=dict(size=10, color=CB_SAFE_GREEN, family="Inter"),
        )

    # Layout with design system theme
    theme = get_plotly_theme()
    fig.update_layout(
        title=dict(
            text="Cost Comparison: Bar Arrangements",
            font=dict(
                size=theme["title_font_size"],
                color=theme["font_color"],
                family=theme["font_family"],
                weight=theme["title_font_weight"],
            ),
        ),
        xaxis=dict(
            title=dict(text="Cost (₹/meter)", font=dict(size=theme["axis_font_size"])),
            showgrid=True,
            gridcolor=theme["grid_color"],
            zeroline=False,
        ),
        yaxis=dict(
            title=dict(text="Bar Arrangement", font=dict(size=theme["axis_font_size"])),
            showgrid=False,
        ),
        plot_bgcolor=theme["plot_bgcolor"],
        paper_bgcolor=theme["paper_bgcolor"],
        font=dict(family=theme["font_family"], color=theme["font_color"]),
        hovermode="closest",
        height=max(300, len(alternatives) * 60),  # Dynamic height
        margin=dict(l=100, r=100, t=60, b=50),
        transition=dict(duration=ANIMATION.duration_normal_ms, easing="cubic-in-out"),
    )

    return fig


def create_bmd_sfd_diagram(
    positions_mm: list[float],
    bmd_knm: list[float],
    sfd_kn: list[float],
    critical_points: Optional[list] = None,
    show_grid: bool = True,
    height: int = 500,
) -> go.Figure:
    """
    Create combined BMD and SFD diagram using Plotly subplots.

    Features:
    - BMD (Bending Moment Diagram) on top subplot
    - SFD (Shear Force Diagram) on bottom subplot
    - Critical points marked with annotations
    - Zero reference lines
    - Filled area under curves
    - Interactive hover tooltips
    - IS 456 color theme

    Args:
        positions_mm: List of positions along span (mm)
        bmd_knm: List of bending moments (kN·m)
        sfd_kn: List of shear forces (kN)
        critical_points: Optional list of CriticalPoint objects
        show_grid: Show grid lines
        height: Figure height in pixels

    Returns:
        Plotly figure with two subplots

    Example:
        >>> from structural_lib.api import compute_bmd_sfd, LoadDefinition, LoadType
        >>> loads = [LoadDefinition(LoadType.UDL, magnitude=20.0)]
        >>> result = compute_bmd_sfd(6000, "simply_supported", loads)
        >>> fig = create_bmd_sfd_diagram(
        ...     result.positions_mm, result.bmd_knm, result.sfd_kn,
        ...     result.critical_points
        ... )
        >>> st.plotly_chart(fig, use_container_width=True)
    """
    theme = get_plotly_theme()

    # Create subplots (BMD on top, SFD on bottom)
    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=("Bending Moment Diagram (BMD)", "Shear Force Diagram (SFD)"),
        vertical_spacing=0.12,
        row_heights=[0.5, 0.5],
    )

    # Convert positions to meters for display
    positions_m = [x / 1000.0 for x in positions_mm]

    # BMD trace (filled area)
    fig.add_trace(
        go.Scatter(
            x=positions_m,
            y=bmd_knm,
            mode="lines",
            name="BMD",
            line=dict(color=CB_SAFE_BLUE, width=2),
            fill="tozeroy",
            fillcolor="rgba(1, 115, 178, 0.2)",
            hovertemplate="Position: %{x:.2f} m<br>Moment: %{y:.2f} kN·m<extra></extra>",
        ),
        row=1,
        col=1,
    )

    # Zero line for BMD
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1, row=1, col=1)

    # SFD trace (filled area)
    fig.add_trace(
        go.Scatter(
            x=positions_m,
            y=sfd_kn,
            mode="lines",
            name="SFD",
            line=dict(color=CB_SAFE_ORANGE, width=2),
            fill="tozeroy",
            fillcolor="rgba(222, 143, 5, 0.2)",
            hovertemplate="Position: %{x:.2f} m<br>Shear: %{y:.2f} kN<extra></extra>",
        ),
        row=2,
        col=1,
    )

    # Zero line for SFD
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1, row=2, col=1)

    # Add critical point annotations
    if critical_points:
        for cp in critical_points:
            x_m = cp.position_mm / 1000.0

            # Annotation for BMD critical points
            if cp.point_type in ("max_bm", "min_bm"):
                fig.add_annotation(
                    x=x_m,
                    y=cp.bm_knm,
                    text=f"{cp.bm_knm:.1f}",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=1,
                    ax=0,
                    ay=-30 if cp.bm_knm >= 0 else 30,
                    font=dict(size=10, color=CB_SAFE_BLUE),
                    row=1,
                    col=1,
                )

            # Annotation for SFD critical points
            if cp.point_type in ("max_sf", "min_sf"):
                fig.add_annotation(
                    x=x_m,
                    y=cp.sf_kn,
                    text=f"{cp.sf_kn:.1f}",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=1,
                    ax=0,
                    ay=-30 if cp.sf_kn >= 0 else 30,
                    font=dict(size=10, color=CB_SAFE_ORANGE),
                    row=2,
                    col=1,
                )

    # Update layout
    fig.update_layout(
        height=height,
        showlegend=False,
        plot_bgcolor=theme["plot_bgcolor"],
        paper_bgcolor=theme["paper_bgcolor"],
        font=dict(family=theme["font_family"], color=theme["font_color"]),
        margin=dict(l=60, r=40, t=60, b=50),
    )

    # Update axes
    fig.update_xaxes(
        title_text="Position (m)",
        showgrid=show_grid,
        gridcolor=theme["grid_color"],
        row=1,
        col=1,
    )
    fig.update_xaxes(
        title_text="Position (m)",
        showgrid=show_grid,
        gridcolor=theme["grid_color"],
        row=2,
        col=1,
    )
    fig.update_yaxes(
        title_text="Moment (kN·m)",
        showgrid=show_grid,
        gridcolor=theme["grid_color"],
        row=1,
        col=1,
    )
    fig.update_yaxes(
        title_text="Shear (kN)",
        showgrid=show_grid,
        gridcolor=theme["grid_color"],
        row=2,
        col=1,
    )

    return fig


def create_utilization_gauge(
    value: float, label: str, thresholds: Optional[Dict[str, float]] = None
) -> go.Figure:
    """
    Create semicircular utilization gauge with color zones.

    Features:
    - Semicircular gauge (0-100%)
    - Three color zones: green (safe), yellow (warning), red (critical)
    - Current value indicator
    - Customizable thresholds
    - WCAG 2.1 AA colorblind-safe colors

    Args:
        value: Utilization value (0.0 to 1.0)
        label: Gauge label (e.g., "Flexure", "Shear")
        thresholds: Optional dict with 'warning' and 'critical' (default: 0.8, 0.95)

    Returns:
        Plotly figure

    Example:
        >>> fig = create_utilization_gauge(0.75, "Flexure Utilization")
        >>> st.plotly_chart(fig, width="stretch")
    """
    if thresholds is None:
        thresholds = {"warning": 0.8, "critical": 0.95}

    warning_threshold = thresholds.get("warning", 0.8)
    critical_threshold = thresholds.get("critical", 0.95)

    # Determine color based on value
    if value < warning_threshold:
        bar_color = CB_SAFE_GREEN
        status = "Safe"
    elif value < critical_threshold:
        bar_color = THEME_YELLOW
        status = "Warning"
    else:
        bar_color = CB_SAFE_RED
        status = "Critical"

    # Create gauge with design system theme
    theme = get_plotly_theme()
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=value * 100,  # Convert to percentage
            title={
                "text": label,
                "font": {
                    "size": theme["title_font_size"],
                    "color": theme["font_color"],
                    "family": theme["font_family"],
                },
            },
            number={
                "suffix": "%",
                "font": {
                    "size": 32,
                    "color": bar_color,
                    "family": theme["font_family"],
                },
            },
            delta={
                "reference": critical_threshold * 100,
                "increasing": {"color": CB_SAFE_RED},
                "decreasing": {"color": CB_SAFE_GREEN},
                "font": {"size": 14, "family": theme["font_family"]},
            },
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickwidth": 2,
                    "tickcolor": theme["font_color"],
                    "tickvals": [
                        0,
                        warning_threshold * 100,
                        critical_threshold * 100,
                        100,
                    ],
                    "ticktext": [
                        "0%",
                        f"{warning_threshold * 100:.0f}%",
                        f"{critical_threshold * 100:.0f}%",
                        "100%",
                    ],
                    "tickfont": {"size": 11, "family": theme["font_family"]},
                },
                "bar": {"color": bar_color, "thickness": 0.8},
                "bgcolor": theme["plot_bgcolor"],
                "borderwidth": 2,
                "bordercolor": COLORS.primary_500,
                "steps": [
                    {
                        "range": [0, warning_threshold * 100],
                        "color": "rgba(2, 158, 115, 0.15)",
                    },  # Light green
                    {
                        "range": [warning_threshold * 100, critical_threshold * 100],
                        "color": "rgba(245, 158, 11, 0.15)",
                    },  # Light yellow
                    {
                        "range": [critical_threshold * 100, 100],
                        "color": "rgba(204, 51, 17, 0.15)",
                    },  # Light red
                ],
                "threshold": {
                    "line": {"color": COLORS.primary_700, "width": 4},
                    "thickness": 0.85,
                    "value": value * 100,
                },
            },
        )
    )

    # Add status annotation with design system theme
    fig.add_annotation(
        text=f"Status: {status}",
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.1,
        showarrow=False,
        font=dict(size=14, color=bar_color, family=theme["font_family"], weight="bold"),
    )

    fig.update_layout(
        height=320,
        margin=dict(l=30, r=30, t=60, b=50),
        paper_bgcolor=theme["paper_bgcolor"],
        font={"family": theme["font_family"], "color": theme["font_color"]},
        transition=dict(duration=ANIMATION.duration_normal_ms, easing="cubic-in-out"),
    )

    return fig


def create_sensitivity_tornado(
    parameters: List[Dict[str, any]], baseline_value: float
) -> go.Figure:
    """
    Create tornado diagram showing parameter sensitivity.

    Features:
    - Horizontal bars showing +/- impact
    - Sorted by total impact (most sensitive first)
    - Colorblind-safe colors (blue for decrease, orange for increase)
    - Baseline reference line
    - Interactive hover with values

    Args:
        parameters: List of dicts with:
            - 'name': str (parameter name)
            - 'low_value': float (result when param decreased)
            - 'high_value': float (result when param increased)
            - 'unit': str (optional, e.g., "mm", "N/mm²")
        baseline_value: Baseline result value

    Returns:
        Plotly figure

    Example:
        >>> params = [
        ...     {'name': 'Moment', 'low_value': 450, 'high_value': 750, 'unit': 'mm²'},
        ...     {'name': 'Width', 'low_value': 550, 'high_value': 650, 'unit': 'mm²'}
        ... ]
        >>> fig = create_sensitivity_tornado(params, baseline_value=600)
        >>> st.plotly_chart(fig, width="stretch")
    """
    if not parameters:
        fig = go.Figure()
        fig.add_annotation(
            text="No sensitivity data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="gray"),
        )
        return fig

    # Calculate impacts and sort by total impact
    for param in parameters:
        param["low_impact"] = param["low_value"] - baseline_value
        param["high_impact"] = param["high_value"] - baseline_value
        param["total_impact"] = abs(param["low_impact"]) + abs(param["high_impact"])

    sorted_params = sorted(parameters, key=lambda x: x["total_impact"], reverse=True)

    # Get theme for consistent styling
    theme = get_plotly_theme()

    # Extract data
    names = [p["name"] for p in sorted_params]
    low_impacts = [p["low_impact"] for p in sorted_params]
    high_impacts = [p["high_impact"] for p in sorted_params]
    units = [p.get("unit", "") for p in sorted_params]

    fig = go.Figure()

    # Low values (left bars, blue)
    fig.add_trace(
        go.Bar(
            name="Decrease",
            y=names,
            x=low_impacts,
            orientation="h",
            marker=dict(color=CB_SAFE_BLUE),
            hovertemplate=(
                "<b>%{y} (Decrease)</b><br>"
                + "Impact: %{x:+.1f}<br>"
                + "<extra></extra>"
            ),
        )
    )

    # High values (right bars, orange)
    fig.add_trace(
        go.Bar(
            name="Increase",
            y=names,
            x=high_impacts,
            orientation="h",
            marker=dict(color=CB_SAFE_ORANGE),
            hovertemplate=(
                "<b>%{y} (Increase)</b><br>"
                + "Impact: %{x:+.1f}<br>"
                + "<extra></extra>"
            ),
        )
    )

    # Baseline reference line
    fig.add_vline(
        x=0,
        line=dict(color=THEME_NAVY, width=2, dash="solid"),
        annotation_text="Baseline",
        annotation_position="top",
    )

    fig.update_layout(
        title=dict(
            text=f"Sensitivity Analysis (Baseline: {baseline_value:.1f})",
            font=dict(size=16, color=THEME_NAVY, family="Inter"),
        ),
        xaxis=dict(
            title="Impact on Result",
            showgrid=True,
            gridcolor="rgba(0,0,0,0.1)",
            zeroline=True,
            zerolinecolor=THEME_NAVY,
            zerolinewidth=2,
        ),
        yaxis=dict(title="Parameter", showgrid=False),
        barmode="overlay",
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="closest",
        showlegend=True,
        legend=dict(
            x=1.05,
            y=1,
            bgcolor=theme.get("legend_bgcolor", "rgba(255,255,255,0.9)"),
            bordercolor=theme.get("legend_border_color", "#E0E0E0"),
            borderwidth=theme.get("legend_border_width", 1),
            font=dict(size=12),
        ),
        height=max(300, len(parameters) * 50),
        margin=dict(l=120, r=100, t=60, b=50),
        transition=dict(duration=ANIMATION.duration_normal_ms, easing="cubic-in-out"),
    )

    return fig


def create_compliance_visual(checks: List[Dict[str, any]]) -> None:
    """
    Create IS 456 compliance checklist with visual status indicators.

    Features:
    - Status icons (✅ ⚠️ ❌)
    - Clause references
    - Expandable details
    - Color coding (colorblind-safe)
    - Summary statistics

    Args:
        checks: List of dicts with:
            - 'clause': str (e.g., "26.5.1.1 (a)")
            - 'description': str (check description)
            - 'status': str ('pass', 'warning', 'fail')
            - 'actual_value': float (optional)
            - 'limit_value': float (optional)
            - 'unit': str (optional)
            - 'details': str (optional, additional info)

    Returns:
        None (renders directly to Streamlit)

    Example:
        >>> checks = [
        ...     {'clause': '26.5.1.1(a)', 'description': 'Min steel area',
        ...      'status': 'pass', 'actual_value': 603, 'limit_value': 360, 'unit': 'mm²'},
        ...     {'clause': '26.5.1.5', 'description': 'Max steel area',
        ...      'status': 'pass', 'actual_value': 603, 'limit_value': 2400, 'unit': 'mm²'}
        ... ]
        >>> create_compliance_visual(checks)
    """
    if not checks:
        st.info("ℹ️ No compliance checks available")
        return

    # Calculate summary statistics
    total = len(checks)
    passed = sum(1 for c in checks if c["status"] == "pass")
    warnings = sum(1 for c in checks if c["status"] == "warning")
    failed = sum(1 for c in checks if c["status"] == "fail")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Checks", total)
    col2.metric("✅ Passed", passed, delta=None, delta_color="normal")
    col3.metric("⚠️ Warnings", warnings, delta=None, delta_color="normal")
    col4.metric("❌ Failed", failed, delta=None, delta_color="inverse")

    # Overall status
    if failed > 0:
        st.error(f"❌ Design does NOT comply with IS 456:2000 ({failed} failures)")
    elif warnings > 0:
        st.warning(f"⚠️ Design complies with warnings ({warnings} warnings)")
    else:
        st.success(f"✅ Design fully complies with IS 456:2000")

    st.divider()

    # Detailed checklist
    st.subheader("📋 Detailed Compliance Checks")

    for i, check in enumerate(checks, 1):
        # Status icon and color
        if check["status"] == "pass":
            icon = "✅"
            status_color = CB_SAFE_GREEN
            expander_label = f"{icon} [{check['clause']}] {check['description']}"
        elif check["status"] == "warning":
            icon = "⚠️"
            status_color = THEME_YELLOW
            expander_label = f"{icon} [{check['clause']}] {check['description']}"
        else:  # fail
            icon = "❌"
            status_color = CB_SAFE_RED
            expander_label = f"{icon} [{check['clause']}] {check['description']}"

        # Expandable details
        with st.expander(expander_label, expanded=(check["status"] != "pass")):
            # Clause reference
            st.markdown(f"**IS 456:2000 Clause:** `{check['clause']}`")

            # Values (if provided)
            if "actual_value" in check and "limit_value" in check:
                unit = check.get("unit", "")
                actual = check["actual_value"]
                limit = check["limit_value"]

                col_a, col_b = st.columns(2)
                col_a.metric("Actual Value", f"{actual:.2f} {unit}")
                col_b.metric("Limit Value", f"{limit:.2f} {unit}")

                # Comparison
                if check["status"] == "pass":
                    st.markdown(
                        f"✅ `{actual:.2f}` meets requirement `{limit:.2f}` {unit}"
                    )
                elif check["status"] == "warning":
                    st.markdown(
                        f"⚠️ `{actual:.2f}` marginally meets requirement `{limit:.2f}` {unit}"
                    )
                else:
                    st.markdown(
                        f"❌ `{actual:.2f}` FAILS requirement `{limit:.2f}` {unit}"
                    )

            # Additional details
            if "details" in check and check["details"]:
                st.info(check["details"])

            # Recommendations (for failures/warnings)
            if check["status"] == "fail":
                st.error("**Action Required:** Modify design to meet this requirement")
            elif check["status"] == "warning":
                st.warning(
                    "**Recommendation:** Consider design adjustments for better safety margin"
                )

    # Footer note
    st.caption(
        "Note: All checks per IS 456:2000 - Plain and Reinforced Concrete - Code of Practice"
    )
