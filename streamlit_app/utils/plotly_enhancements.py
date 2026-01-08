"""
Plotly Enhancement Utilities
============================

Advanced Plotly features for modern, interactive visualizations:
- Animations and transitions
- Hover templates with rich formatting
- Click interactions
- Export configurations
- Responsive layouts
- Theme customization

Author: STREAMLIT UI SPECIALIST (Agent 6)
Status: ✅ IMPLEMENTED (STREAMLIT-UI-003)
Version: 1.0
"""

from typing import Dict, Any, Optional
import plotly.graph_objects as go

# Import design system
try:
    from utils.design_system import COLORS, TYPOGRAPHY, ANIMATION
except ImportError:
    class COLORS:
        primary_500 = "#003366"
        gray_100 = "#F5F5F5"
    class TYPOGRAPHY:
        font_ui = "Inter"
    class ANIMATION:
        duration_normal = 200


def add_animation_config(fig: go.Figure, duration_ms: int = 300) -> go.Figure:
    """
    Add smooth animation configuration to figure.

    Args:
        fig: Plotly figure
        duration_ms: Animation duration in milliseconds

    Returns:
        Enhanced figure with animations
    """
    fig.update_layout(
        transition={
            'duration': duration_ms,
            'easing': 'cubic-in-out'
        },
        updatemenus=[{
            'type': 'buttons',
            'direction': 'left',
            'x': 0.1,
            'y': 1.15,
            'showactive': True,
            'buttons': [
                {
                    'label': '▶ Animate',
                    'method': 'animate',
                    'args': [None, {
                        'frame': {'duration': duration_ms, 'redraw': True},
                        'transition': {'duration': duration_ms, 'easing': 'cubic-in-out'},
                        'fromcurrent': True
                    }]
                }
            ]
        }]
    )
    return fig


def add_export_config(fig: go.Figure, filename: str = "chart") -> go.Figure:
    """
    Add export configuration with modern options.

    Args:
        fig: Plotly figure
        filename: Default filename for exports

    Returns:
        Figure with export configuration
    """
    fig.update_layout(
        modebar={
            'orientation': 'v',
            'bgcolor': 'rgba(255,255,255,0.8)',
            'color': COLORS.primary_500,
            'activecolor': COLORS.primary_500
        }
    )

    # Configure export settings
    config = {
        'toImageButtonOptions': {
            'format': 'png',  # png, svg, jpeg
            'filename': filename,
            'height': 800,
            'width': 1200,
            'scale': 2  # High DPI export
        },
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
        'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'eraseshape'],
    }

    return fig, config


def create_rich_hover_template(
    title: str,
    fields: Dict[str, str],
    show_extra: bool = False
) -> str:
    """
    Create rich hover template with consistent formatting.

    Args:
        title: Hover card title
        fields: Dict of {label: value_format}
               e.g., {'Cost': '₹%{x:.2f}/m', 'Area': '%{customdata}mm²'}
        show_extra: Show extra info in hover

    Returns:
        Formatted hover template string

    Example:
        >>> template = create_rich_hover_template(
        ...     "Bar Arrangement",
        ...     {'Cost': '₹%{x:.2f}/m', 'Area': '%{customdata[0]}mm²'}
        ... )
    """
    lines = [f"<b>{title}</b>"]
    lines.append("<br>")

    for label, value_format in fields.items():
        lines.append(f"{label}: {value_format}")
        lines.append("<br>")

    # Remove last <br>
    lines = lines[:-1]

    if not show_extra:
        lines.append("<extra></extra>")

    return "".join(lines)


def add_responsive_layout(
    fig: go.Figure,
    height_px: Optional[int] = None,
    aspect_ratio: Optional[float] = None
) -> go.Figure:
    """
    Make figure responsive with proper margins.

    Args:
        fig: Plotly figure
        height_px: Fixed height in pixels (if None, uses aspect ratio)
        aspect_ratio: Width/height ratio (e.g., 16/9 = 1.778)

    Returns:
        Figure with responsive layout
    """
    layout_updates = {
        'autosize': True,
        'margin': dict(
            l=60,  # Left margin
            r=40,  # Right margin
            t=80,  # Top margin
            b=60,  # Bottom margin
            pad=10  # Padding
        )
    }

    if height_px:
        layout_updates['height'] = height_px

    if aspect_ratio:
        layout_updates['yaxis'] = dict(
            scaleanchor='x',
            scaleratio=aspect_ratio
        )

    fig.update_layout(**layout_updates)
    return fig


def add_gridlines(
    fig: go.Figure,
    x_grid: bool = True,
    y_grid: bool = True,
    grid_color: Optional[str] = None,
    grid_width: float = 1
) -> go.Figure:
    """
    Add styled gridlines to figure.

    Args:
        fig: Plotly figure
        x_grid: Show x-axis grid
        y_grid: Show y-axis grid
        grid_color: Grid line color (defaults to design system)
        grid_width: Grid line width

    Returns:
        Figure with gridlines
    """
    if grid_color is None:
        grid_color = COLORS.gray_100

    fig.update_xaxes(
        showgrid=x_grid,
        gridcolor=grid_color,
        gridwidth=grid_width,
        griddash='dot'
    )

    fig.update_yaxes(
        showgrid=y_grid,
        gridcolor=grid_color,
        gridwidth=grid_width,
        griddash='dot'
    )

    return fig


def add_annotations_layer(
    fig: go.Figure,
    annotations: list[Dict[str, Any]]
) -> go.Figure:
    """
    Add styled annotations to figure.

    Args:
        fig: Plotly figure
        annotations: List of annotation dicts with:
            - text: str
            - x, y: coordinates
            - showarrow: bool (default True)
            - arrowcolor: str (optional)
            - font_size: int (optional)

    Returns:
        Figure with annotations
    """
    for ann in annotations:
        fig.add_annotation(
            text=ann['text'],
            x=ann['x'],
            y=ann['y'],
            showarrow=ann.get('showarrow', True),
            arrowhead=ann.get('arrowhead', 2),
            arrowsize=ann.get('arrowsize', 1),
            arrowwidth=ann.get('arrowwidth', 2),
            arrowcolor=ann.get('arrowcolor', COLORS.primary_500),
            ax=ann.get('ax', 0),
            ay=ann.get('ay', -40),
            font=dict(
                size=ann.get('font_size', 12),
                color=ann.get('font_color', COLORS.primary_500),
                family=TYPOGRAPHY.font_ui
            ),
            bgcolor=ann.get('bgcolor', 'rgba(255,255,255,0.8)'),
            bordercolor=ann.get('bordercolor', COLORS.primary_500),
            borderwidth=1,
            borderpad=4
        )

    return fig


def add_loading_skeleton(message: str = "Generating visualization...") -> go.Figure:
    """
    Create a skeleton/loading state figure.

    Args:
        message: Loading message to display

    Returns:
        Placeholder figure
    """
    fig = go.Figure()

    fig.add_annotation(
        text=f"⏳ {message}",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(
            size=16,
            color=COLORS.primary_500,
            family=TYPOGRAPHY.font_ui
        )
    )

    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor='white',
        paper_bgcolor=COLORS.gray_100,
        height=400,
        margin=dict(l=0, r=0, t=0, b=0)
    )

    return fig


def apply_dark_mode_theme(fig: go.Figure) -> go.Figure:
    """
    Apply dark mode styling to figure.

    Args:
        fig: Plotly figure

    Returns:
        Figure with dark mode theme
    """
    # Dark mode colors
    bg_dark = "#0F1419"
    paper_dark = "#1A1F26"
    text_dark = "#E5E7EB"
    grid_dark = "#374151"

    fig.update_layout(
        plot_bgcolor=bg_dark,
        paper_bgcolor=paper_dark,
        font=dict(color=text_dark, family=TYPOGRAPHY.font_ui)
    )

    fig.update_xaxes(
        gridcolor=grid_dark,
        linecolor=grid_dark,
        tickcolor=text_dark
    )

    fig.update_yaxes(
        gridcolor=grid_dark,
        linecolor=grid_dark,
        tickcolor=text_dark
    )

    return fig


# ============================================================================
# PRESET CONFIGURATIONS
# ============================================================================

ENGINEERING_CHART_CONFIG = {
    'displayModeBar': True,
    'displaylogo': False,
    'toImageButtonOptions': {
        'format': 'png',
        'filename': 'engineering_chart',
        'height': 1000,
        'width': 1400,
        'scale': 2
    },
    'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
    'scrollZoom': True,
    'responsive': True
}

PRESENTATION_CHART_CONFIG = {
    'displayModeBar': False,  # Hide for presentations
    'staticPlot': False,  # Keep interactive
    'responsive': True
}

PRINT_CHART_CONFIG = {
    'displayModeBar': True,
    'displaylogo': False,
    'toImageButtonOptions': {
        'format': 'svg',  # Vector for print
        'filename': 'chart_print',
        'height': 1200,
        'width': 1600,
        'scale': 1
    },
    'staticPlot': True  # No interactions for print
}
