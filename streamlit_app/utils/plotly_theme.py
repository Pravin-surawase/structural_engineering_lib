"""
Plotly Theme Configuration - IS 456 Engineering Theme.

Based on RESEARCH-006 (Data Visualization Excellence).
Implements professional chart styling for engineering data.

Version: 1.0
Created: 2026-01-08
"""

from typing import Dict, Any
from .design_system import COLORS, TYPOGRAPHY

# ============================================================================
# IS456 PLOTLY THEME
# ============================================================================

IS456_THEME: Dict[str, Any] = {
    "layout": {
        # Fonts
        "font": {
            "family": TYPOGRAPHY.font_ui,
            "size": 14,
            "color": COLORS.gray_700,
        },
        # Title
        "title": {
            "font": {
                "family": TYPOGRAPHY.font_ui,
                "size": 20,
                "color": COLORS.gray_900,
                "weight": 600,
            },
            "x": 0.5,  # Center title
            "xanchor": "center",
        },
        # Paper and plot background
        "paper_bgcolor": "#FFFFFF",
        "plot_bgcolor": COLORS.gray_50,
        # Grid
        "xaxis": {
            "gridcolor": COLORS.gray_200,
            "gridwidth": 1,
            "showgrid": True,
            "zeroline": True,
            "zerolinecolor": COLORS.gray_300,
            "zerolinewidth": 2,
            "title": {
                "font": {
                    "family": TYPOGRAPHY.font_ui,
                    "size": 13,
                    "color": COLORS.gray_600,
                    "weight": 500,
                }
            },
            "tickfont": {
                "family": TYPOGRAPHY.font_mono,
                "size": 12,
                "color": COLORS.gray_600,
            },
        },
        "yaxis": {
            "gridcolor": COLORS.gray_200,
            "gridwidth": 1,
            "showgrid": True,
            "zeroline": True,
            "zerolinecolor": COLORS.gray_300,
            "zerolinewidth": 2,
            "title": {
                "font": {
                    "family": TYPOGRAPHY.font_ui,
                    "size": 13,
                    "color": COLORS.gray_600,
                    "weight": 500,
                }
            },
            "tickfont": {
                "family": TYPOGRAPHY.font_mono,
                "size": 12,
                "color": COLORS.gray_600,
            },
        },
        # Legend
        "legend": {
            "bgcolor": "rgba(255, 255, 255, 0.9)",
            "bordercolor": COLORS.gray_200,
            "borderwidth": 1,
            "font": {
                "family": TYPOGRAPHY.font_ui,
                "size": 12,
                "color": COLORS.gray_700,
            },
        },
        # Hover label
        "hoverlabel": {
            "bgcolor": COLORS.gray_900,
            "bordercolor": COLORS.gray_700,
            "font": {
                "family": TYPOGRAPHY.font_mono,
                "size": 13,
                "color": "#FFFFFF",
            },
        },
        # Color sequence (for multiple series)
        "colorway": [
            COLORS.primary_500,  # Navy
            COLORS.accent_500,  # Orange
            COLORS.success,  # Green
            COLORS.info,  # Blue
            COLORS.warning,  # Amber
            COLORS.primary_300,  # Light navy
            COLORS.accent_300,  # Light orange
        ],
        # Margins
        "margin": {"l": 60, "r": 40, "t": 60, "b": 60},
        # Interaction
        "hovermode": "closest",
        "dragmode": "zoom",
    },
    # Data trace defaults
    "data": {
        "scatter": [
            {
                "marker": {
                    "line": {"width": 1, "color": "#FFFFFF"},
                    "size": 8,
                },
                "line": {"width": 2},
            }
        ],
        "bar": [
            {
                "marker": {
                    "line": {"width": 0.5, "color": COLORS.gray_200},
                },
                "textfont": {
                    "family": TYPOGRAPHY.font_mono,
                    "size": 11,
                },
            }
        ],
        "indicator": [
            {
                "mode": "gauge+number+delta",
                "gauge": {
                    "axis": {
                        "tickfont": {
                            "family": TYPOGRAPHY.font_mono,
                            "size": 11,
                        }
                    },
                    "bar": {"color": COLORS.primary_500},
                    "bgcolor": COLORS.gray_100,
                    "borderwidth": 2,
                    "bordercolor": COLORS.gray_300,
                },
                "number": {
                    "font": {
                        "family": TYPOGRAPHY.font_mono,
                        "size": 24,
                        "color": COLORS.gray_900,
                    },
                    "suffix": "%",
                },
                "delta": {
                    "font": {
                        "family": TYPOGRAPHY.font_mono,
                        "size": 14,
                    }
                },
            }
        ],
    },
}


# ============================================================================
# DARK MODE THEME
# ============================================================================

IS456_DARK_THEME: Dict[str, Any] = {
    **IS456_THEME,
    "layout": {
        **IS456_THEME["layout"],
        "font": {
            **IS456_THEME["layout"]["font"],
            "color": "#E5E5E5",
        },
        "paper_bgcolor": "#0F1419",
        "plot_bgcolor": "#1A1F26",
        "xaxis": {
            **IS456_THEME["layout"]["xaxis"],
            "gridcolor": "#404040",
            "zerolinecolor": "#525252",
            "title": {
                "font": {
                    **IS456_THEME["layout"]["xaxis"]["title"]["font"],
                    "color": "#A3A3A3",
                }
            },
            "tickfont": {
                **IS456_THEME["layout"]["xaxis"]["tickfont"],
                "color": "#A3A3A3",
            },
        },
        "yaxis": {
            **IS456_THEME["layout"]["yaxis"],
            "gridcolor": "#404040",
            "zerolinecolor": "#525252",
            "title": {
                "font": {
                    **IS456_THEME["layout"]["yaxis"]["title"]["font"],
                    "color": "#A3A3A3",
                }
            },
            "tickfont": {
                **IS456_THEME["layout"]["yaxis"]["tickfont"],
                "color": "#A3A3A3",
            },
        },
        "legend": {
            **IS456_THEME["layout"]["legend"],
            "bgcolor": "rgba(26, 31, 38, 0.9)",
            "bordercolor": "#404040",
            "font": {
                **IS456_THEME["layout"]["legend"]["font"],
                "color": "#E5E5E5",
            },
        },
    },
}


# ============================================================================
# ENGINEERING-SPECIFIC COLOR SCALES
# ============================================================================

# Stress visualization (compression to tension)
STRESS_COLORSCALE = [
    [0.0, COLORS.error],  # Compression (red)
    [0.5, COLORS.gray_300],  # Neutral
    [1.0, COLORS.info],  # Tension (blue)
]

# Utilization (0% to 100%+)
UTILIZATION_COLORSCALE = [
    [0.0, COLORS.success],  # Safe (green)
    [0.7, COLORS.success],  # Still safe
    [0.85, COLORS.warning],  # Warning zone (amber)
    [1.0, COLORS.error],  # Over limit (red)
]

# Safety factor (high to low)
SAFETY_FACTOR_COLORSCALE = [
    [0.0, COLORS.error],  # Low safety (red)
    [0.5, COLORS.warning],  # Moderate safety (amber)
    [1.0, COLORS.success],  # High safety (green)
]


# ============================================================================
# COLORBLIND-SAFE PALETTES
# ============================================================================

# Deuteranopia-safe (most common colorblindness)
COLORBLIND_SAFE_PALETTE = [
    "#0173B2",  # Blue
    "#DE8F05",  # Orange
    "#029E73",  # Green
    "#CC78BC",  # Purple
    "#CA9161",  # Brown
    "#949494",  # Gray
    "#ECE133",  # Yellow
    "#56B4E9",  # Sky blue
]


# ============================================================================
# CHART TYPE CONFIGS
# ============================================================================


def get_chart_config(interactive: bool = True) -> Dict[str, Any]:
    """
    Get standard Plotly chart configuration.

    Args:
        interactive: Enable interactive features

    Returns:
        Plotly config dict
    """
    if interactive:
        return {
            "displayModeBar": True,
            "modeBarButtonsToRemove": [
                "select2d",
                "lasso2d",
                "autoScale2d",
            ],
            "modeBarButtonsToAdd": ["hoverclosest", "hovercompare"],
            "toImageButtonOptions": {
                "format": "png",
                "filename": "is456_chart",
                "height": 1000,
                "width": 1400,
                "scale": 2,
            },
            "displaylogo": False,
        }
    else:
        return {
            "displayModeBar": False,
            "staticPlot": True,
        }


def apply_theme(fig, dark_mode: bool = False) -> None:
    """
    Apply IS456 theme to a Plotly figure.

    Args:
        fig: Plotly figure object
        dark_mode: Use dark mode theme

    Example:
        >>> import plotly.graph_objects as go
        >>> fig = go.Figure(data=[go.Bar(x=[1,2,3], y=[4,5,6])])
        >>> apply_theme(fig)
        >>> fig.show()
    """
    theme = IS456_DARK_THEME if dark_mode else IS456_THEME

    # Apply layout theme
    fig.update_layout(**theme["layout"])

    # Apply trace-specific styling
    for trace in fig.data:
        trace_type = trace.type
        if trace_type in theme["data"]:
            trace_defaults = theme["data"][trace_type][0]
            for key, value in trace_defaults.items():
                if not hasattr(trace, key) or getattr(trace, key) is None:
                    setattr(trace, key, value)


def create_hover_template(
    labels: Dict[str, str],
    units: Dict[str, str],
    precision: Dict[str, int] = None,
) -> str:
    """
    Create custom hover template for engineering data.

    Args:
        labels: Dict mapping field names to display labels
        units: Dict mapping field names to unit strings
        precision: Dict mapping field names to decimal places

    Returns:
        Hover template string

    Example:
        >>> template = create_hover_template(
        ...     labels={"mu": "Moment", "ast": "Steel Area"},
        ...     units={"mu": "kN·m", "ast": "mm²"},
        ...     precision={"mu": 1, "ast": 0}
        ... )
    """
    if precision is None:
        precision = {}

    lines = []
    for field, label in labels.items():
        unit = units.get(field, "")
        prec = precision.get(field, 2)
        lines.append(f"<b>{label}:</b> %{{customdata[{field}]:.{prec}f}} {unit}")

    return "<br>".join(lines) + "<extra></extra>"


# ============================================================================
# EXPORT PUBLIC API
# ============================================================================

__all__ = [
    "IS456_THEME",
    "IS456_DARK_THEME",
    "STRESS_COLORSCALE",
    "UTILIZATION_COLORSCALE",
    "SAFETY_FACTOR_COLORSCALE",
    "COLORBLIND_SAFE_PALETTE",
    "get_chart_config",
    "apply_theme",
    "create_hover_template",
]
