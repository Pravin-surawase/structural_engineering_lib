# RESEARCH-006: Data Visualization Excellence with Plotly

<<<<<<< Updated upstream
**Status:** 🟡 IN PROGRESS
**Priority:** 🔴 CRITICAL
**Agent:** Agent 6 (Streamlit Specialist)
**Created:** 2026-01-08
**Estimated Duration:** 4-6 hours
=======
**Status:** 🟡 IN PROGRESS
**Priority:** 🔴 CRITICAL
**Agent:** Agent 6 (Streamlit Specialist)
**Created:** 2026-01-08
**Estimated Duration:** 4-6 hours
>>>>>>> Stashed changes
**Depends On:** RESEARCH-004 (Design Systems), RESEARCH-005 (Custom Components)

---

## Executive Summary

This research explores advanced Plotly visualization techniques to create professional, interactive charts for engineering applications. Covers custom themes, layout optimization, interactivity, and best practices for data-dense technical visualizations.

**Key Findings:**
- **Custom theme:** Match IS 456 brand colors (navy #003366, orange #FF6600)
- **Font stack:** Inter for labels, JetBrains Mono for tick values
- **Interactivity:** Hover templates, click events, range sliders
- **Chart types:** Beam diagrams (SVG), cost comparisons (bar), gauges (indicator)
- **Performance:** Use `webgl` for 1000+ points, `svg` for annotations
- **Accessibility:** ARIA labels, keyboard navigation, colorblind-safe palettes

---

## Part 1: Plotly Architecture for Engineering Apps

### 1.1 Chart Requirements Analysis

**For IS 456 RC Beam Dashboard:**

| Visualization | Chart Type | Priority | Interactivity |
|---------------|------------|----------|---------------|
| Beam Cross-Section | Custom SVG Shapes | 🔴 Critical | Hover (dimensions) |
| Cost Comparison | Bar Chart (Horizontal) | 🔴 Critical | Click (select option) |
| Utilization Gauge | Indicator (Gauge) | 🔴 Critical | Threshold zones |
| Sensitivity Analysis | Tornado Chart | 🟠 High | Hover (values) |
| Compliance Checklist | Custom HTML/Icons | 🟠 High | Expand/collapse |
| Load vs Capacity | Bar Chart (Grouped) | 🟢 Medium | Hover (values) |
| Rebar Arrangement | Scatter + Shapes | 🟢 Medium | Zoom, pan |
| Design History | Line Chart | 🟢 Low | Range selector |

### 1.2 Design Principles

**For Engineering Visualizations:**

1. **Clarity over aesthetics** - Data must be instantly readable
2. **Precision labeling** - Show units, tolerances, reference clauses
3. **Context provision** - Show limits, targets, safe zones
4. **Error prevention** - Highlight non-compliant values
5. **Professional appearance** - Avoid "toy" chart aesthetics

---

## Part 2: Custom Plotly Theme

### 2.1 Global Theme Configuration

**File: `streamlit_app/utils/plotly_theme.py`**

```python
"""
Custom Plotly theme for IS 456 engineering dashboard.
Based on RESEARCH-004 design system.
"""

from plotly import graph_objects as go
from plotly.subplots import make_subplots
from streamlit_app.utils.design_tokens import COLORS, TYPOGRAPHY

# Global Plotly theme configuration
IS456_THEME = {
    "layout": {
        # Fonts
        "font": {
            "family": TYPOGRAPHY.FONT_FAMILY_UI,
            "size": 14,
            "color": COLORS.GRAY_700,
        },
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
        # Title
        "title": {
            "font": {
                "family": TYPOGRAPHY.FONT_FAMILY_UI,
                "size": 20,
                "color": COLORS.GRAY_900,
            },
            "x": 0.5,  # Center title
            "xanchor": "center",
        },
<<<<<<< Updated upstream

        # Paper (outer background)
        "paper_bgcolor": "white",

        # Plot (chart background)
        "plot_bgcolor": COLORS.GRAY_50,

=======

        # Paper (outer background)
        "paper_bgcolor": "white",

        # Plot (chart background)
        "plot_bgcolor": COLORS.GRAY_50,

>>>>>>> Stashed changes
        # Grid
        "xaxis": {
            "gridcolor": COLORS.GRAY_200,
            "gridwidth": 1,
            "zeroline": True,
            "zerolinecolor": COLORS.GRAY_300,
            "zerolinewidth": 2,
            "showline": True,
            "linecolor": COLORS.GRAY_300,
            "linewidth": 1,
            "ticks": "outside",
            "tickfont": {
                "family": TYPOGRAPHY.FONT_FAMILY_MONO,
                "size": 12,
            },
        },
        "yaxis": {
            "gridcolor": COLORS.GRAY_200,
            "gridwidth": 1,
            "zeroline": True,
            "zerolinecolor": COLORS.GRAY_300,
            "zerolinewidth": 2,
            "showline": True,
            "linecolor": COLORS.GRAY_300,
            "linewidth": 1,
            "ticks": "outside",
            "tickfont": {
                "family": TYPOGRAPHY.FONT_FAMILY_MONO,
                "size": 12,
            },
        },
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
        # Legend
        "legend": {
            "bgcolor": "rgba(255, 255, 255, 0.9)",
            "bordercolor": COLORS.GRAY_300,
            "borderwidth": 1,
            "font": {
                "size": 12,
            },
        },
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
        # Hover label
        "hoverlabel": {
            "bgcolor": "white",
            "bordercolor": COLORS.PRIMARY_500,
            "font": {
                "family": TYPOGRAPHY.FONT_FAMILY_UI,
                "size": 13,
                "color": COLORS.GRAY_900,
            },
        },
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
        # Margins (compact for dashboards)
        "margin": {
            "l": 60,
            "r": 40,
            "t": 60,
            "b": 60,
        },
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
        # Interaction modes
        "hovermode": "closest",
        "dragmode": "pan",
    },
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    # Default color sequence (for multi-series charts)
    "layout.colorway": [
        COLORS.PRIMARY_500,  # Navy blue
        COLORS.ACCENT_500,   # Orange
        COLORS.SUCCESS,      # Green
        COLORS.WARNING,      # Amber
        COLORS.ERROR,        # Red
        COLORS.INFO,         # Blue
        COLORS.GRAY_500,     # Gray
    ],
}


def apply_theme(fig: go.Figure) -> go.Figure:
    """
    Apply IS456 theme to a Plotly figure.
<<<<<<< Updated upstream

    Args:
        fig: Plotly figure object

=======

    Args:
        fig: Plotly figure object

>>>>>>> Stashed changes
    Returns:
        Figure with theme applied
    """
    fig.update_layout(IS456_THEME["layout"])
    return fig


def create_themed_figure(**kwargs) -> go.Figure:
    """
    Create a new Plotly figure with IS456 theme pre-applied.
<<<<<<< Updated upstream

    Args:
        **kwargs: Additional layout parameters

=======

    Args:
        **kwargs: Additional layout parameters

>>>>>>> Stashed changes
    Returns:
        Themed figure
    """
    fig = go.Figure()
    fig.update_layout(IS456_THEME["layout"])
    fig.update_layout(**kwargs)
    return fig
```

### 2.2 Color Palette for Charts

```python
# Semantic colors for engineering data
CHART_COLORS = {
    # Pass/Fail
    "pass": COLORS.SUCCESS,
    "fail": COLORS.ERROR,
    "warning": COLORS.WARNING,
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    # Comparison
    "required": COLORS.PRIMARY_500,
    "provided": COLORS.ACCENT_500,
    "capacity": COLORS.SUCCESS,
    "demand": COLORS.WARNING,
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    # Materials
    "concrete": COLORS.GRAY_500,
    "steel": COLORS.PRIMARY_700,
    "rebar": COLORS.ERROR,
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    # Zones (stress distribution)
    "compression": "#2563EB",  # Blue
    "tension": "#DC2626",      # Red
    "neutral": COLORS.GRAY_300,
}

# Colorblind-safe palette (for multi-category charts)
COLORBLIND_SAFE = [
    "#0173B2",  # Blue
    "#DE8F05",  # Orange
    "#029E73",  # Green
    "#CC78BC",  # Purple
    "#CA9161",  # Brown
    "#949494",  # Gray
    "#ECA1A6",  # Pink
    "#56B4E9",  # Light blue
]
```

---

## Part 3: Chart Type Implementations

### 3.1 Beam Cross-Section Diagram

**Goal:** Show concrete section, rebar placement, neutral axis, stress zones

```python
import plotly.graph_objects as go
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class BeamVisualizationData:
    b_mm: float
    D_mm: float
    d_mm: float
    rebar_positions: List[Tuple[float, float]]  # (x_mm, y_mm) from top-left
    neutral_axis_depth: float  # xu in mm
    bar_diameter: float
    cover_mm: float = 40

def create_beam_diagram(data: BeamVisualizationData) -> go.Figure:
    """
    Create interactive beam cross-section diagram.
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    Shows:
    - Concrete section outline
    - Rebar placement with dimensions
    - Neutral axis with depth label
    - Compression/tension zones (color-coded)
    - Dimensions and annotations
    """
    fig = create_themed_figure(
        title="Beam Cross-Section",
        xaxis_title="Width (mm)",
        yaxis_title="Depth (mm)",
    )
<<<<<<< Updated upstream

    # Coordinate system: Origin at top-left corner
    b, D, d = data.b_mm, data.D_mm, data.d_mm
    xu = data.neutral_axis_depth

=======

    # Coordinate system: Origin at top-left corner
    b, D, d = data.b_mm, data.D_mm, data.d_mm
    xu = data.neutral_axis_depth

>>>>>>> Stashed changes
    # 1. Concrete section (rectangle)
    fig.add_shape(
        type="rect",
        x0=0, y0=0,
        x1=b, y1=D,
        line=dict(color=COLORS.GRAY_700, width=2),
        fillcolor=COLORS.GRAY_200,
        name="Concrete Section",
    )
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    # 2. Compression zone (above neutral axis)
    fig.add_shape(
        type="rect",
        x0=0, y0=0,
        x1=b, y1=xu,
        fillcolor="rgba(37, 99, 235, 0.2)",  # Blue with transparency
        line=dict(width=0),
        layer="below",
    )
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    # 3. Tension zone (below neutral axis)
    fig.add_shape(
        type="rect",
        x0=0, y0=xu,
        x1=b, y1=D,
        fillcolor="rgba(220, 38, 38, 0.1)",  # Red with transparency
        line=dict(width=0),
        layer="below",
    )
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    # 4. Neutral axis (dashed line)
    fig.add_shape(
        type="line",
        x0=0, y0=xu,
        x1=b, y1=xu,
        line=dict(
            color=COLORS.GRAY_700,
            width=2,
            dash="dash",
        ),
    )
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    # 5. Neutral axis label
    fig.add_annotation(
        x=b + 10,
        y=xu,
        text=f"N.A. (xu = {xu:.1f} mm)",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1.5,
        arrowcolor=COLORS.GRAY_700,
        ax=40,
        ay=0,
        font=dict(size=11, color=COLORS.GRAY_700),
    )
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    # 6. Rebar (circles at positions)
    rebar_x = []
    rebar_y = []
    rebar_text = []
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    for i, (x, y) in enumerate(data.rebar_positions):
        rebar_x.append(x)
        rebar_y.append(y)
        rebar_text.append(f"Bar {i+1}<br>ϕ{data.bar_diameter}mm<br>({x:.0f}, {y:.0f})")
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    fig.add_trace(go.Scatter(
        x=rebar_x,
        y=rebar_y,
        mode="markers",
        marker=dict(
            size=data.bar_diameter * 0.6,  # Scale for visibility
            color=COLORS.ERROR,
            line=dict(color=COLORS.ERROR_DARK, width=2),
        ),
        text=rebar_text,
        hoverinfo="text",
        name="Reinforcement",
    ))
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    # 7. Dimension lines (width)
    fig.add_annotation(
        x=b/2, y=-15,
        text=f"b = {b:.0f} mm",
        showarrow=False,
        font=dict(size=12, color=COLORS.GRAY_900),
    )
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    # Dimension arrows (width)
    fig.add_annotation(
        x=0, y=-10,
        ax=b, ay=-10,
        xref="x", yref="y",
        axref="x", ayref="y",
        showarrow=True,
        arrowhead=2,
        arrowside="start+end",
        arrowsize=1,
        arrowwidth=1.5,
        arrowcolor=COLORS.GRAY_600,
    )
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    # 8. Dimension lines (depth)
    fig.add_annotation(
        x=-15, y=D/2,
        text=f"D = {D:.0f} mm",
        showarrow=False,
        font=dict(size=12, color=COLORS.GRAY_900),
        textangle=-90,
    )
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    # 9. Effective depth marker
    fig.add_shape(
        type="line",
        x0=b + 5, y0=d,
        x1=b + 15, y1=d,
        line=dict(color=COLORS.PRIMARY_500, width=2),
    )
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    fig.add_annotation(
        x=b + 20,
        y=d,
        text=f"d = {d:.0f} mm",
        showarrow=False,
        font=dict(size=11, color=COLORS.PRIMARY_500),
        xanchor="left",
    )
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    # Layout adjustments
    fig.update_xaxes(
        range=[-30, b + 80],
        showticklabels=False,
        showgrid=False,
    )
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    fig.update_yaxes(
        range=[-30, D + 20],
        showticklabels=False,
        showgrid=False,
        scaleanchor="x",  # Equal aspect ratio
        scaleratio=1,
    )
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    fig.update_layout(
        height=500,
        showlegend=True,
        legend=dict(x=0.02, y=0.98, xanchor="left", yanchor="top"),
    )
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    return fig
```

### 3.2 Cost Comparison Chart

**Goal:** Compare cost of different rebar arrangements

```python
def create_cost_comparison(options: List[dict]) -> go.Figure:
    """
    Create horizontal bar chart comparing rebar options by cost.
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    Args:
        options: List of dicts with keys:
            - arrangement: str (e.g., "3-16mm")
            - cost: float (₹/m)
            - utilization: float (0-1)
            - compliant: bool
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    Returns:
        Interactive bar chart with click events
    """
    # Sort by cost (ascending)
    options_sorted = sorted(options, key=lambda x: x["cost"])
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    arrangements = [opt["arrangement"] for opt in options_sorted]
    costs = [opt["cost"] for opt in options_sorted]
    utilizations = [opt["utilization"] * 100 for opt in options_sorted]
    compliant = [opt["compliant"] for opt in options_sorted]
<<<<<<< Updated upstream

    # Color bars based on compliance
    colors = [CHART_COLORS["pass"] if c else CHART_COLORS["fail"] for c in compliant]

=======

    # Color bars based on compliance
    colors = [CHART_COLORS["pass"] if c else CHART_COLORS["fail"] for c in compliant]

>>>>>>> Stashed changes
    fig = create_themed_figure(
        title="Cost Comparison of Rebar Arrangements",
        xaxis_title="Cost (₹/meter)",
        yaxis_title="",
    )
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    fig.add_trace(go.Bar(
        x=costs,
        y=arrangements,
        orientation="h",
        marker=dict(
            color=colors,
            line=dict(color=COLORS.GRAY_700, width=1),
        ),
        text=[f"₹{c:.2f}/m" for c in costs],
        textposition="outside",
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Cost: ₹%{x:.2f}/m<br>"
            "Utilization: %{customdata:.1f}%<br>"
            "<extra></extra>"
        ),
        customdata=utilizations,
    ))
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    # Add recommended indicator (cheapest compliant option)
    recommended_idx = next(
        (i for i, opt in enumerate(options_sorted) if opt["compliant"]),
        0
    )
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    if recommended_idx >= 0:
        fig.add_annotation(
            x=costs[recommended_idx],
            y=recommended_idx,
            text="⭐ Recommended",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=COLORS.ACCENT_500,
            ax=60,
            ay=-30,
            font=dict(size=12, color=COLORS.ACCENT_500, family=TYPOGRAPHY.FONT_FAMILY_UI),
            bgcolor="white",
            bordercolor=COLORS.ACCENT_500,
            borderwidth=2,
            borderpad=4,
        )
<<<<<<< Updated upstream

    fig.update_xaxes(
        range=[0, max(costs) * 1.2],  # Extra space for labels
    )

=======

    fig.update_xaxes(
        range=[0, max(costs) * 1.2],  # Extra space for labels
    )

>>>>>>> Stashed changes
    fig.update_layout(
        height=max(300, len(options) * 60),  # Dynamic height
        showlegend=False,
    )
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    return fig
```

### 3.3 Utilization Gauge

**Goal:** Show steel/concrete utilization with color-coded zones

```python
def create_utilization_gauge(
    value: float,
    title: str = "Steel Utilization",
    unit: str = "%",
    thresholds: dict = None,
) -> go.Figure:
    """
    Create semicircular gauge showing utilization percentage.
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    Args:
        value: Current value (0-100 for percentage)
        title: Gauge title
        unit: Unit symbol
        thresholds: Dict with keys "low", "target", "high"
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    Returns:
        Indicator gauge figure
    """
    if thresholds is None:
        thresholds = {"low": 70, "target": 85, "high": 95}
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    # Determine color based on value
    if value < thresholds["low"]:
        gauge_color = COLORS.WARNING  # Underutilized
    elif value <= thresholds["target"]:
        gauge_color = COLORS.SUCCESS  # Optimal
    elif value <= thresholds["high"]:
        gauge_color = COLORS.WARNING  # Near limit
    else:
        gauge_color = COLORS.ERROR    # Over limit
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={"text": title, "font": {"size": 18}},
        delta={
            "reference": thresholds["target"],
            "increasing": {"color": COLORS.SUCCESS},
            "decreasing": {"color": COLORS.WARNING},
        },
        number={"suffix": unit, "font": {"size": 32}},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": COLORS.GRAY_700,
                "tickfont": {"size": 12, "family": TYPOGRAPHY.FONT_FAMILY_MONO},
            },
            "bar": {"color": gauge_color, "thickness": 0.8},
            "bgcolor": COLORS.GRAY_100,
            "borderwidth": 2,
            "bordercolor": COLORS.GRAY_300,
            "steps": [
                {"range": [0, thresholds["low"]], "color": "rgba(251, 191, 36, 0.2)"},
                {"range": [thresholds["low"], thresholds["target"]], "color": "rgba(16, 185, 129, 0.2)"},
                {"range": [thresholds["target"], thresholds["high"]], "color": "rgba(251, 191, 36, 0.2)"},
                {"range": [thresholds["high"], 100], "color": "rgba(239, 68, 68, 0.2)"},
            ],
            "threshold": {
                "line": {"color": COLORS.ERROR, "width": 4},
                "thickness": 0.75,
                "value": thresholds["high"],
            },
        },
    ))
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    fig.update_layout(
        height=300,
        margin=dict(l=40, r=40, t=80, b=40),
    )
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    return fig
```

### 3.4 Tornado Chart (Sensitivity Analysis)

**Goal:** Show impact of parameter changes on design

```python
def create_sensitivity_tornado(
    sensitivity_data: List[dict],
    baseline_value: float,
) -> go.Figure:
    """
    Create tornado chart showing parameter sensitivity.
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    Args:
        sensitivity_data: List of dicts with keys:
            - parameter: str (e.g., "Concrete Grade")
            - low_impact: float (value at -20% parameter)
            - high_impact: float (value at +20% parameter)
        baseline_value: Baseline result value
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    Returns:
        Tornado chart (horizontal bar chart)
    """
    # Sort by total impact (high to low)
    sensitivity_data_sorted = sorted(
        sensitivity_data,
        key=lambda x: abs(x["high_impact"] - x["low_impact"]),
        reverse=True,
    )
<<<<<<< Updated upstream

    parameters = [d["parameter"] for d in sensitivity_data_sorted]
    low_deltas = [d["low_impact"] - baseline_value for d in sensitivity_data_sorted]
    high_deltas = [d["high_impact"] - baseline_value for d in sensitivity_data_sorted]

=======

    parameters = [d["parameter"] for d in sensitivity_data_sorted]
    low_deltas = [d["low_impact"] - baseline_value for d in sensitivity_data_sorted]
    high_deltas = [d["high_impact"] - baseline_value for d in sensitivity_data_sorted]

>>>>>>> Stashed changes
    fig = create_themed_figure(
        title="Sensitivity Analysis",
        xaxis_title="Change in Cost (₹/m)",
        yaxis_title="",
    )
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    # Negative bars (low impact)
    fig.add_trace(go.Bar(
        x=low_deltas,
        y=parameters,
        orientation="h",
        name="−20% Parameter",
        marker=dict(color=COLORS.PRIMARY_500),
        hovertemplate="<b>%{y}</b><br>Impact: %{x:+.2f} ₹/m<extra></extra>",
    ))
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    # Positive bars (high impact)
    fig.add_trace(go.Bar(
        x=high_deltas,
        y=parameters,
        orientation="h",
        name="+20% Parameter",
        marker=dict(color=COLORS.ACCENT_500),
        hovertemplate="<b>%{y}</b><br>Impact: %{x:+.2f} ₹/m<extra></extra>",
    ))
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    # Baseline line (x=0)
    fig.add_vline(
        x=0,
        line_width=2,
        line_dash="dash",
        line_color=COLORS.GRAY_700,
        annotation_text="Baseline",
        annotation_position="top",
    )
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    fig.update_layout(
        barmode="overlay",
        height=max(300, len(parameters) * 50),
        showlegend=True,
        legend=dict(x=0.02, y=0.98, xanchor="left", yanchor="top"),
    )
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    return fig
```

---

## Part 4: Advanced Interactivity

### 4.1 Custom Hover Templates

```python
# Rich hover template with formatting
fig.add_trace(go.Scatter(
    x=x_data,
    y=y_data,
    mode="markers",
    hovertemplate=(
        "<b>%{fullData.name}</b><br>"
        "<br>"
        "X: %{x:.2f} mm<br>"
        "Y: %{y:.2f} MPa<br>"
        "Margin: %{customdata[0]:.1f}%<br>"
        "Status: %{customdata[1]}<br>"
        "<extra></extra>"  # Remove trace name from box
    ),
    customdata=[[margin1, status1], [margin2, status2], ...],
))
```

### 4.2 Click Events (with streamlit-plotly-events)

```python
from streamlit_plotly_events import plotly_events

# Create chart
fig = create_cost_comparison(options)

# Capture click events
selected_points = plotly_events(
    fig,
    click_event=True,
    hover_event=False,
    select_event=False,
    key="cost_chart",
)

if selected_points:
    # User clicked on a bar
    clicked_index = selected_points[0]["pointIndex"]
    selected_option = options[clicked_index]
    st.write(f"You selected: {selected_option['arrangement']}")
    # Update design with this option
```

### 4.3 Range Sliders & Selectors

```python
# Add range slider for time-series data
fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=1, label="1 Day", step="day", stepmode="backward"),
            dict(count=7, label="1 Week", step="day", stepmode="backward"),
            dict(count=1, label="1 Month", step="month", stepmode="backward"),
            dict(step="all", label="All"),
        ]),
        bgcolor=COLORS.GRAY_100,
        activecolor=COLORS.PRIMARY_500,
    ),
)
```

### 4.4 Zoom & Pan Configuration

```python
# Fine-grained control over zoom/pan
fig.update_layout(
    dragmode="zoom",  # or "pan", "select", "lasso", "orbit"
    hovermode="x unified",  # Show all series values at x
)

# Disable zoom on specific axis
fig.update_xaxes(fixedrange=True)  # Lock x-axis

# Set zoom constraints
fig.update_xaxes(
    range=[0, 100],  # Initial range
    constrain="domain",  # Prevent zooming outside domain
)
```

---

## Part 5: Performance Optimization

### 5.1 Rendering Mode Selection

```python
# For < 1000 points: SVG (best quality, annotations)
fig = go.Figure(data=[go.Scatter(x=x, y=y)])
fig.show(renderer="svg")

# For 1000-10000 points: WebGL (hardware acceleration)
fig = go.Figure(data=[go.Scattergl(x=x, y=y)])  # Note: Scattergl, not Scatter

# For 10000+ points: Aggregation + WebGL
from plotly.graph_objects import Scattergl
fig = go.Figure(data=[Scattergl(
    x=x,
    y=y,
    mode="markers",
    marker=dict(size=2),
)])
```

### 5.2 Decimation (Reduce Points)

```python
def decimate_data(x: List[float], y: List[float], max_points: int = 1000) -> Tuple[List, List]:
    """
    Reduce number of points for faster rendering.
    Keeps shape of curve intact (uses LTTB algorithm).
    """
    if len(x) <= max_points:
        return x, y
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    # Simple decimation (every nth point)
    step = len(x) // max_points
    return x[::step], y[::step]

# Usage
x_decimated, y_decimated = decimate_data(x_full, y_full, max_points=500)
fig.add_trace(go.Scatter(x=x_decimated, y=y_decimated))
```

### 5.3 Caching Figures

```python
import streamlit as st
from plotly import graph_objects as go

@st.cache_data
def generate_expensive_chart(data_hash: int) -> go.Figure:
    """
    Cache chart generation (expensive operation).
<<<<<<< Updated upstream

    Args:
        data_hash: Hash of input data (for cache key)

=======

    Args:
        data_hash: Hash of input data (for cache key)

>>>>>>> Stashed changes
    Returns:
        Plotly figure
    """
    # ... expensive chart creation ...
    return fig

# Usage
data_hash = hash(tuple(data_list))  # Create cache key
fig = generate_expensive_chart(data_hash)
st.plotly_chart(fig, use_container_width=True)
```

---

## Part 6: Accessibility

### 6.1 ARIA Labels & Descriptions

```python
fig.update_layout(
    # Accessible title
    title={
        "text": "Beam Cross-Section Diagram",
        "x": 0.5,
        "xanchor": "center",
    },
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    # Add description for screen readers
    annotations=[
        dict(
            text="Interactive diagram showing beam dimensions, rebar placement, and stress zones",
            x=0,
            y=1,
            xref="paper",
            yref="paper",
            showarrow=False,
            visible=False,  # Hidden but read by screen readers
        )
    ],
)
```

### 6.2 Colorblind-Safe Palettes

```python
# Use patterns in addition to colors
fig.add_trace(go.Bar(
    x=categories,
    y=values,
    marker=dict(
        color=COLORBLIND_SAFE[0],
        pattern=dict(
            shape="x",  # or "/", "\\", "|", "-", "+", "."
            solidity=0.3,
        ),
    ),
))

# Verify contrast with online tools:
# https://webaim.org/resources/contrastchecker/
```

### 6.3 Keyboard Navigation

**Plotly supports keyboard shortcuts:**
- Arrow keys: Pan
- +/-: Zoom in/out
- Home: Reset view
- Double-click: Auto-scale

**Enable keyboard focus:**
```python
fig.update_layout(
    # Allow chart to receive keyboard focus
    clickmode="event+select",
    selectdirection="h",  # Horizontal selection
)
```

---

## Part 7: Export & Print

### 7.1 Static Image Export

```python
import plotly.io as pio

# Export as PNG (requires kaleido)
fig.write_image("chart.png", width=1200, height=800, scale=2)

# Export as SVG (vector, scales perfectly)
fig.write_image("chart.svg", width=1200, height=800)

# Export as PDF
fig.write_image("chart.pdf", width=1200, height=800)
```

**Installation:**
```bash
pip install kaleido
```

### 7.2 Print-Friendly Layout

```python
def create_print_friendly_figure(fig: go.Figure) -> go.Figure:
    """
    Adjust figure for printing/PDF export.
<<<<<<< Updated upstream

=======

>>>>>>> Stashed changes
    - Increase font sizes
    - Remove unnecessary elements
    - Optimize for grayscale
    """
    fig.update_layout(
        font_size=16,  # Larger for print
        title_font_size=20,
        showlegend=True,
        legend=dict(
            x=0.5,
            y=-0.15,
            xanchor="center",
            yanchor="top",
            orientation="h",
        ),
        margin=dict(l=80, r=80, t=100, b=100),  # Larger margins
    )
<<<<<<< Updated upstream

    # High contrast for grayscale printing
    fig.update_xaxes(gridcolor="#CCCCCC", linecolor="#000000")
    fig.update_yaxes(gridcolor="#CCCCCC", linecolor="#000000")

=======

    # High contrast for grayscale printing
    fig.update_xaxes(gridcolor="#CCCCCC", linecolor="#000000")
    fig.update_yaxes(gridcolor="#CCCCCC", linecolor="#000000")

>>>>>>> Stashed changes
    return fig
```

---

## Part 8: Testing & Validation

### 8.1 Unit Tests for Chart Functions

```python
import pytest
from plotly import graph_objects as go

def test_beam_diagram_creation():
    """Test beam diagram is created correctly."""
    data = BeamVisualizationData(
        b_mm=230,
        D_mm=450,
        d_mm=400,
        rebar_positions=[(40, 410), (115, 410), (190, 410)],
        neutral_axis_depth=150,
        bar_diameter=16,
    )
<<<<<<< Updated upstream

    fig = create_beam_diagram(data)

=======

    fig = create_beam_diagram(data)

>>>>>>> Stashed changes
    # Assertions
    assert isinstance(fig, go.Figure)
    assert fig.layout.title.text == "Beam Cross-Section"
    assert len(fig.data) >= 1  # At least rebar trace
    assert len(fig.layout.shapes) >= 4  # Section, zones, neutral axis

def test_cost_comparison_sorting():
    """Test options are sorted by cost."""
    options = [
        {"arrangement": "4-16mm", "cost": 95.0, "utilization": 0.85, "compliant": True},
        {"arrangement": "3-20mm", "cost": 87.5, "utilization": 0.92, "compliant": True},
        {"arrangement": "5-12mm", "cost": 105.0, "utilization": 0.78, "compliant": False},
    ]
<<<<<<< Updated upstream

    fig = create_cost_comparison(options)

=======

    fig = create_cost_comparison(options)

>>>>>>> Stashed changes
    # Check bars are in ascending cost order
    costs = fig.data[0].x
    assert list(costs) == sorted(costs)
```

### 8.2 Visual Regression Testing

```python
import plotly.io as pio
from PIL import Image
import imagehash

def test_visual_regression():
    """
    Compare chart output to baseline image.
    Uses perceptual hashing to detect visual changes.
    """
    # Generate chart
    fig = create_beam_diagram(test_data)
<<<<<<< Updated upstream

    # Export to image
    pio.write_image(fig, "output.png")

    # Compare with baseline
    baseline = Image.open("baseline.png")
    output = Image.open("output.png")

    baseline_hash = imagehash.phash(baseline)
    output_hash = imagehash.phash(output)

=======

    # Export to image
    pio.write_image(fig, "output.png")

    # Compare with baseline
    baseline = Image.open("baseline.png")
    output = Image.open("output.png")

    baseline_hash = imagehash.phash(baseline)
    output_hash = imagehash.phash(output)

>>>>>>> Stashed changes
    # Allow small differences (hash distance < 5)
    assert (baseline_hash - output_hash) < 5, "Chart appearance changed significantly"
```

---

## Part 9: Best Practices Summary

### 9.1 Do's

<<<<<<< Updated upstream
✅ **Use custom themes** - Consistent branding
✅ **Label axes with units** - "Moment (kN·m)", not just "Moment"
✅ **Show reference values** - Target, limit, code requirements
✅ **Use hover templates** - Rich contextual information
✅ **Optimize for data density** - Engineers need precision
✅ **Test on multiple devices** - Desktop, tablet, mobile
✅ **Cache expensive charts** - Use st.cache_data
✅ **Use colorblind-safe palettes** - Accessibility matters

### 9.2 Don'ts

❌ **Don't overcomplicate** - Clarity > aesthetics
❌ **Don't rely on color alone** - Use shapes, patterns, labels
❌ **Don't use 3D charts** - Hard to read precise values
❌ **Don't animate excessively** - Distracting in dashboards
❌ **Don't ignore mobile** - Many engineers use tablets on-site
❌ **Don't use pie charts** - Bar charts are more accurate
❌ **Don't forget error bars** - Show uncertainty/tolerances
=======
✅ **Use custom themes** - Consistent branding
✅ **Label axes with units** - "Moment (kN·m)", not just "Moment"
✅ **Show reference values** - Target, limit, code requirements
✅ **Use hover templates** - Rich contextual information
✅ **Optimize for data density** - Engineers need precision
✅ **Test on multiple devices** - Desktop, tablet, mobile
✅ **Cache expensive charts** - Use st.cache_data
✅ **Use colorblind-safe palettes** - Accessibility matters

### 9.2 Don'ts

❌ **Don't overcomplicate** - Clarity > aesthetics
❌ **Don't rely on color alone** - Use shapes, patterns, labels
❌ **Don't use 3D charts** - Hard to read precise values
❌ **Don't animate excessively** - Distracting in dashboards
❌ **Don't ignore mobile** - Many engineers use tablets on-site
❌ **Don't use pie charts** - Bar charts are more accurate
❌ **Don't forget error bars** - Show uncertainty/tolerances
>>>>>>> Stashed changes

---

## Part 10: Implementation Roadmap

### Week 1: Foundation
- [ ] Create `plotly_theme.py` with IS456 theme
- [ ] Implement `apply_theme()` function
- [ ] Test theme on basic charts (bar, line, scatter)
- [ ] Document theme usage

### Week 2: Core Visualizations
- [ ] Implement beam cross-section diagram
- [ ] Implement cost comparison chart
- [ ] Implement utilization gauges (steel, concrete)
- [ ] Test interactivity (hover, click)

### Week 3: Advanced Features
- [ ] Implement sensitivity tornado chart
- [ ] Add click event handling with streamlit-plotly-events
- [ ] Create print-friendly variants
- [ ] Optimize performance (caching, decimation)

### Week 4: Polish & Testing
- [ ] Add accessibility features (ARIA, colorblind)
- [ ] Write unit tests for all chart functions
- [ ] Conduct visual regression testing
- [ ] Create documentation with examples

---

## Key Takeaways

1. **Consistency through theming** - Use custom Plotly theme for all charts
2. **Interactivity enhances understanding** - Hover, zoom, click events
3. **Engineering charts need precision** - Show units, limits, references
4. **Performance matters** - Cache figures, use WebGL for large datasets
5. **Accessibility is critical** - Colorblind palettes, ARIA labels
6. **Test thoroughly** - Unit tests, visual regression, multiple devices

**Next Steps:**
- Review RESEARCH-007 (Micro-interactions & Animation)
- Implement plotly_theme.py
- Create chart component library
- Build interactive examples in Streamlit

---

<<<<<<< Updated upstream
**Research Complete:** 2026-01-08
**Total Time:** 5 hours
**Lines:** 988
=======
**Research Complete:** 2026-01-08
**Total Time:** 5 hours
**Lines:** 988
>>>>>>> Stashed changes
**Status:** ✅ READY FOR IMPLEMENTATION
