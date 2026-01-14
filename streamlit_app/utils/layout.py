"""
Modern Layout System - Page layouts with depth and visual hierarchy.

Based on RESEARCH-004 (Modern UI Design Systems) and RESEARCH-005 (Streamlit Custom Components).
Implements professional page layouts with cards, sections, and responsive design.

Features:
- Card-based layouts with elevation/shadows
- Responsive grid system
- Section headers with actions
- Professional spacing and typography
- Print-friendly layouts
- Dark mode support (prepared)

Version: 1.0
Created: 2026-01-08 (UI-002: Page Layout Redesign)
"""

import streamlit as st
from typing import Optional, Literal, Callable, Any
from dataclasses import dataclass

from utils.design_system import COLORS, TYPOGRAPHY, SPACING, ELEVATION


# ============================================================================
# LAYOUT CONFIGURATION
# ============================================================================


@dataclass
class LayoutConfig:
    """Configuration for page layout behavior."""

    max_width: str = "1400px"
    sidebar_width: str = "320px"
    padding_top: str = SPACING.space_6  # 48px
    padding_bottom: str = SPACING.space_6
    enable_print_mode: bool = True
    enable_responsive: bool = True


# Default configuration
DEFAULT_LAYOUT = LayoutConfig()


# ============================================================================
# CSS INJECTION - Modern Professional Styling
# ============================================================================


def inject_modern_css(config: LayoutConfig = DEFAULT_LAYOUT) -> None:
    """
    Inject modern CSS with depth, shadows, and professional styling.

    Args:
        config: Layout configuration
    """
    css = f"""
    <style>
    /* ==================== GLOBAL RESETS ==================== */
    :root {{
        --primary-color: {COLORS.primary_500};
        --accent-color: {COLORS.accent_500};
        --text-primary: {COLORS.gray_900};
        --text-secondary: {COLORS.gray_600};
        --bg-primary: #FFFFFF;
        --bg-secondary: {COLORS.gray_50};
        --border-color: {COLORS.gray_200};
        --shadow-sm: {ELEVATION.shadow_sm};
        --shadow-md: {ELEVATION.shadow_md};
        --shadow-lg: {ELEVATION.shadow_lg};
        --radius-md: 12px;
        --radius-lg: 16px;
        --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
    }}

    /* ==================== TYPOGRAPHY ==================== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    body {{
        font-family: {TYPOGRAPHY.font_ui};
        color: var(--text-primary);
        line-height: 1.6;
    }}

    h1, h2, h3, h4, h5, h6 {{
        font-family: {TYPOGRAPHY.font_ui};
        font-weight: 600;
        line-height: 1.3;
        letter-spacing: -0.02em;
    }}

    h1 {{ font-size: {TYPOGRAPHY.display_sm}; margin-bottom: {SPACING.space_6}; }}
    h2 {{ font-size: {TYPOGRAPHY.heading_xl}; margin-bottom: {SPACING.space_5}; }}
    h3 {{ font-size: {TYPOGRAPHY.heading_lg}; margin-bottom: {SPACING.space_4}; }}

    code, pre {{
        font-family: {TYPOGRAPHY.font_mono};
        font-size: {TYPOGRAPHY.body_sm};
    }}

    /* ==================== MAIN CONTAINER ==================== */
    .main .block-container {{
        max-width: {config.max_width};
        padding-top: {config.padding_top};
        padding-bottom: {config.padding_bottom};
        padding-left: {SPACING.space_6};
        padding-right: {SPACING.space_6};
    }}

    /* ==================== SIDEBAR STYLING ==================== */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS.primary_50} 0%, #FFFFFF 100%);
        border-right: 1px solid {COLORS.gray_200};
        box-shadow: {ELEVATION.shadow_md};
    }}

    [data-testid="stSidebar"] .block-container {{
        padding: {SPACING.space_5};
    }}

    /* Sidebar section headers */
    [data-testid="stSidebar"] h3 {{
        color: {COLORS.primary_700};
        font-size: {TYPOGRAPHY.heading_sm};
        font-weight: 600;
        margin-top: {SPACING.space_5};
        margin-bottom: {SPACING.space_3};
        padding-bottom: {SPACING.space_2};
        border-bottom: 2px solid {COLORS.primary_200};
    }}

    /* ==================== CARD COMPONENTS ==================== */
    .stat-card {{
        background: white;
        border: 1px solid {COLORS.gray_200};
        border-radius: var(--radius-md);
        padding: {SPACING.space_4};
        box-shadow: var(--shadow-sm);
        transition: all var(--transition-base);
    }}

    .stat-card:hover {{
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
        border-color: {COLORS.primary_200};
    }}

    .info-card {{
        background: linear-gradient(135deg, {COLORS.primary_50} 0%, white 100%);
        border-left: 4px solid {COLORS.primary_500};
        border-radius: var(--radius-md);
        padding: {SPACING.space_4};
        margin: {SPACING.space_4} 0;
        box-shadow: var(--shadow-sm);
    }}

    .warning-card {{
        background: linear-gradient(135deg, {COLORS.warning_light} 0%, white 100%);
        border-left: 4px solid {COLORS.warning};
        border-radius: var(--radius-md);
        padding: {SPACING.space_4};
        margin: {SPACING.space_4} 0;
        box-shadow: var(--shadow-sm);
    }}

    .success-card {{
        background: linear-gradient(135deg, {COLORS.success_light} 0%, white 100%);
        border-left: 4px solid {COLORS.success};
        border-radius: var(--radius-md);
        padding: {SPACING.space_4};
        margin: {SPACING.space_4} 0;
        box-shadow: var(--shadow-sm);
    }}

    .error-card {{
        background: linear-gradient(135deg, {COLORS.error_light} 0%, white 100%);
        border-left: 4px solid {COLORS.error};
        border-radius: var(--radius-md);
        padding: {SPACING.space_4};
        margin: {SPACING.space_4} 0;
        box-shadow: var(--shadow-sm);
    }}

    /* ==================== METRICS/STATS ==================== */
    [data-testid="stMetric"] {{
        background: white;
        border: 1px solid {COLORS.gray_200};
        border-radius: var(--radius-md);
        padding: {SPACING.space_4};
        box-shadow: var(--shadow-sm);
        transition: all var(--transition-base);
    }}

    [data-testid="stMetric"]:hover {{
        box-shadow: var(--shadow-md);
        border-color: {COLORS.primary_300};
    }}

    [data-testid="stMetricLabel"] {{
        font-size: {TYPOGRAPHY.body_sm};
        color: {COLORS.gray_600};
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    [data-testid="stMetricValue"] {{
        font-size: {TYPOGRAPHY.heading_xl};
        color: {COLORS.primary_600};
        font-weight: 700;
        font-family: {TYPOGRAPHY.font_mono};
    }}

    [data-testid="stMetricDelta"] {{
        font-size: {TYPOGRAPHY.body_sm};
        font-weight: 500;
    }}

    /* ==================== TABS ==================== */
    .stTabs {{
        background: white;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
        padding: {SPACING.space_2};
        margin-bottom: {SPACING.space_5};
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: {SPACING.space_2};
        background: {COLORS.gray_100};
        border-radius: var(--radius-md);
        padding: {SPACING.space_1};
    }}

    .stTabs [data-baseweb="tab"] {{
        padding: {SPACING.space_3} {SPACING.space_5};
        font-weight: 500;
        font-size: {TYPOGRAPHY.body_md};
        color: {COLORS.gray_600};
        border-radius: calc(var(--radius-md) - 4px);
        transition: all var(--transition-fast);
        border: none;
        background: transparent;
    }}

    .stTabs [data-baseweb="tab"]:hover {{
        background: {COLORS.gray_200};
        color: {COLORS.primary_600};
    }}

    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        background: white;
        color: {COLORS.primary_600};
        box-shadow: var(--shadow-sm);
        font-weight: 600;
    }}

    .stTabs [data-baseweb="tab-panel"] {{
        padding: {SPACING.space_5};
    }}

    /* ==================== BUTTONS ==================== */
    .stButton > button {{
        width: 100%;
        font-family: {TYPOGRAPHY.font_ui};
        font-size: {TYPOGRAPHY.body_md};
        font-weight: 600;
        padding: {SPACING.space_3} {SPACING.space_5};
        border-radius: var(--radius-md);
        border: none;
        transition: all var(--transition-base);
        cursor: pointer;
        text-transform: none;
        letter-spacing: 0.01em;
    }}

    /* Primary button (default) */
    .stButton > button {{
        background: linear-gradient(135deg, {COLORS.accent_500} 0%, {COLORS.accent_600} 100%);
        color: white;
        box-shadow: var(--shadow-sm);
    }}

    .stButton > button:hover {{
        background: linear-gradient(135deg, {COLORS.accent_600} 0%, {COLORS.accent_700} 100%);
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }}

    .stButton > button:active {{
        transform: translateY(0);
        box-shadow: var(--shadow-sm);
    }}

    .stButton > button:focus {{
        outline: 3px solid {COLORS.accent_200};
        outline-offset: 2px;
    }}

    /* Secondary button variant */
    .stButton.secondary > button {{
        background: white;
        color: {COLORS.primary_600};
        border: 2px solid {COLORS.primary_500};
    }}

    .stButton.secondary > button:hover {{
        background: {COLORS.primary_50};
        border-color: {COLORS.primary_600};
    }}

    /* ==================== INPUTS ==================== */
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div {{
        font-family: {TYPOGRAPHY.font_mono};
        font-size: {TYPOGRAPHY.body_md};
        padding: {SPACING.space_3};
        border: 2px solid {COLORS.gray_300};
        border-radius: var(--radius-md);
        transition: all var(--transition-fast);
        background: white;
    }}

    .stNumberInput > div > div > input:focus,
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus-within {{
        border-color: {COLORS.primary_500};
        box-shadow: 0 0 0 3px {COLORS.primary_100};
        outline: none;
    }}

    /* Input labels */
    .stNumberInput > label,
    .stTextInput > label,
    .stSelectbox > label {{
        font-size: {TYPOGRAPHY.body_sm};
        font-weight: 600;
        color: {COLORS.gray_700};
        margin-bottom: {SPACING.space_2};
    }}

    /* ==================== EXPANDERS ==================== */
    .streamlit-expanderHeader {{
        background: {COLORS.gray_50};
        border: 1px solid {COLORS.gray_200};
        border-radius: var(--radius-md);
        padding: {SPACING.space_3} {SPACING.space_4};
        font-weight: 600;
        color: {COLORS.primary_700};
        transition: all var(--transition-fast);
    }}

    .streamlit-expanderHeader:hover {{
        background: {COLORS.primary_50};
        border-color: {COLORS.primary_300};
        box-shadow: var(--shadow-sm);
    }}

    .streamlit-expanderContent {{
        border: 1px solid {COLORS.gray_200};
        border-top: none;
        border-radius: 0 0 var(--radius-md) var(--radius-md);
        padding: {SPACING.space_4};
        background: white;
    }}

    /* ==================== ALERTS ==================== */
    .stAlert {{
        border-radius: var(--radius-md);
        border: none;
        padding: {SPACING.space_4};
        box-shadow: var(--shadow-sm);
    }}

    /* Info alert */
    .stAlert[data-baseweb="notification"][kind="info"] {{
        background: linear-gradient(135deg, {COLORS.info_light} 0%, white 100%);
        border-left: 4px solid {COLORS.info};
    }}

    /* Success alert */
    .stAlert[data-baseweb="notification"][kind="success"] {{
        background: linear-gradient(135deg, {COLORS.success_light} 0%, white 100%);
        border-left: 4px solid {COLORS.success};
    }}

    /* Warning alert */
    .stAlert[data-baseweb="notification"][kind="warning"] {{
        background: linear-gradient(135deg, {COLORS.warning_light} 0%, white 100%);
        border-left: 4px solid {COLORS.warning};
    }}

    /* Error alert */
    .stAlert[data-baseweb="notification"][kind="error"] {{
        background: linear-gradient(135deg, {COLORS.error_light} 0%, white 100%);
        border-left: 4px solid {COLORS.error};
    }}

    /* ==================== DATAFRAMES ==================== */
    .stDataFrame {{
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-sm);
        overflow: hidden;
    }}

    /* ==================== PLOTLY CHARTS ==================== */
    .js-plotly-plot {{
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-sm);
        background: white;
        padding: {SPACING.space_3};
    }}

    /* ==================== DIVIDERS ==================== */
    hr {{
        margin: {SPACING.space_6} 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, {COLORS.gray_300} 50%, transparent 100%);
    }}

    /* ==================== LOADING STATES ==================== */
    .stSpinner > div {{
        border-color: {COLORS.primary_200};
        border-top-color: {COLORS.primary_500};
    }}

    /* ==================== TOOLTIPS ==================== */
    [data-baseweb="tooltip"] {{
        background: {COLORS.gray_900};
        color: white;
        font-size: {TYPOGRAPHY.body_sm};
        padding: {SPACING.space_2} {SPACING.space_3};
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-lg);
    }}

    /* ==================== RESPONSIVE DESIGN ==================== */
    @media (max-width: 768px) {{
        .main .block-container {{
            padding-left: {SPACING.space_4};
            padding-right: {SPACING.space_4};
        }}

        [data-testid="stMetricValue"] {{
            font-size: {TYPOGRAPHY.heading_lg};
        }}

        h1 {{ font-size: {TYPOGRAPHY.heading_xl}; }}
        h2 {{ font-size: {TYPOGRAPHY.heading_lg}; }}
    }}

    /* ==================== PRINT STYLES ==================== */
    @media print {{
        .stButton, .stDownloadButton {{
            display: none !important;
        }}

        [data-testid="stSidebar"] {{
            display: none !important;
        }}

        .main .block-container {{
            max-width: 100%;
            padding: 0;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            display: none;
        }}

        .stTabs [data-baseweb="tab-panel"] {{
            padding: 0;
        }}

        .stat-card, .info-card {{
            box-shadow: none;
            border: 1px solid {COLORS.gray_300};
            page-break-inside: avoid;
        }}
    }}

    /* ==================== ACCESSIBILITY ==================== */
    /* Respect reduced motion preference */
    @media (prefers-reduced-motion: reduce) {{
        * {{
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }}
    }}

    /* Focus visible for keyboard navigation */
    :focus-visible {{
        outline: 3px solid {COLORS.accent_500};
        outline-offset: 2px;
    }}

    /* Skip to main content link (for screen readers) */
    .skip-to-main {{
        position: absolute;
        left: -9999px;
        z-index: 999;
    }}

    .skip-to-main:focus {{
        left: 50%;
        transform: translateX(-50%);
        background: {COLORS.primary_600};
        color: white;
        padding: {SPACING.space_3} {SPACING.space_5};
        border-radius: var(--radius-md);
    }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)


# ============================================================================
# LAYOUT COMPONENTS
# ============================================================================


def page_header(
    title: str,
    subtitle: Optional[str] = None,
    icon: Optional[str] = None,
    action_button: Optional[tuple[str, Callable]] = None,
) -> None:
    """
    Render a professional page header with title, subtitle, and optional action.

    Args:
        title: Page title (H1)
        subtitle: Optional subtitle/description
        icon: Optional emoji icon
        action_button: Optional tuple of (button_text, callback)
    """
    col1, col2 = st.columns([3, 1])

    with col1:
        if icon:
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; gap: {SPACING.space_3};">
                    <span style="font-size: 48px;">{icon}</span>
                    <div>
                        <h1 style="margin: 0; color: {COLORS.primary_700};">{title}</h1>
                        {f'<p style="margin: 0; color: {COLORS.gray_600}; font-size: {TYPOGRAPHY.body_lg};">{subtitle}</p>' if subtitle else ''}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div>
                    <h1 style="color: {COLORS.primary_700};">{title}</h1>
                    {f'<p style="color: {COLORS.gray_600}; font-size: {TYPOGRAPHY.body_lg};">{subtitle}</p>' if subtitle else ''}
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col2:
        if action_button:
            button_text, callback = action_button
            if st.button(button_text, key=f"header_action_{title}"):
                callback()

    st.markdown("<hr>", unsafe_allow_html=True)


def section_header(
    title: str, icon: Optional[str] = None, divider: bool = True
) -> None:
    """
    Render a section header (H2/H3) with optional icon and divider.

    Args:
        title: Section title
        icon: Optional emoji icon
        divider: Whether to show divider below
    """
    if icon:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: {SPACING.space_2}; margin-top: {SPACING.space_5};">
                <span style="font-size: 24px;">{icon}</span>
                <h3 style="margin: 0; color: {COLORS.primary_600};">{title}</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<h3 style="color: {COLORS.primary_600};">{title}</h3>',
            unsafe_allow_html=True,
        )

    if divider:
        st.markdown(
            f'<div style="height: 1px; background: {COLORS.gray_200}; margin: {SPACING.space_3} 0;"></div>',
            unsafe_allow_html=True,
        )


def card(
    content_func: Callable,
    variant: Literal["default", "info", "success", "warning", "error"] = "default",
    elevation: Literal["sm", "md", "lg"] = "sm",
) -> None:
    """
    Render content inside a card with depth/shadow.

    Args:
        content_func: Function that renders card content
        variant: Card variant (affects border color and background)
        elevation: Shadow level
    """
    card_class = f"{variant}-card" if variant != "default" else "stat-card"

    st.markdown(
        f'<div class="{card_class}" style="box-shadow: var(--shadow-{elevation});">',
        unsafe_allow_html=True,
    )

    content_func()

    st.markdown("</div>", unsafe_allow_html=True)


def metric_card(
    label: str, value: str, delta: Optional[str] = None, help_text: Optional[str] = None
) -> None:
    """
    Render a metric in a professional card (wrapper around st.metric).

    Args:
        label: Metric label
        value: Metric value
        delta: Optional delta/change indicator
        help_text: Optional help text
    """
    st.metric(label=label, value=value, delta=delta, help=help_text)


def info_panel(message: str, title: Optional[str] = None, icon: str = "ℹ️") -> None:
    """
    Render an info panel with icon and optional title.

    Args:
        message: Info message
        title: Optional title
        icon: Emoji icon (default: info)
    """
    st.markdown(
        f"""
        <div class="info-card">
            <div style="display: flex; gap: {SPACING.space_3};">
                <span style="font-size: 24px; flex-shrink: 0;">{icon}</span>
                <div>
                    {f'<div style="font-weight: 600; color: {COLORS.primary_700}; margin-bottom: {SPACING.space_2};">{title}</div>' if title else ''}
                    <div style="color: {COLORS.gray_700};">{message}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def three_column_metrics(
    metric1: tuple[str, str, Optional[str]],
    metric2: tuple[str, str, Optional[str]],
    metric3: tuple[str, str, Optional[str]],
) -> None:
    """
    Render 3 metrics in a row (common pattern).

    Args:
        metric1: Tuple of (label, value, delta)
        metric2: Tuple of (label, value, delta)
        metric3: Tuple of (label, value, delta)
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        metric_card(*metric1)
    with col2:
        metric_card(*metric2)
    with col3:
        metric_card(*metric3)


def two_column_layout(
    left_content: Callable, right_content: Callable, ratio: tuple[int, int] = (1, 1)
) -> None:
    """
    Render a two-column layout.

    Args:
        left_content: Function that renders left column content
        right_content: Function that renders right column content
        ratio: Column width ratio (default: equal)
    """
    col1, col2 = st.columns(ratio)

    with col1:
        left_content()

    with col2:
        right_content()


# ============================================================================
# PAGE SETUP FUNCTION (CALL AT START OF EACH PAGE)
# ============================================================================


def setup_page(
    title: str,
    icon: str = "🏗️",
    layout: Literal["centered", "wide"] = "wide",
    config: LayoutConfig = DEFAULT_LAYOUT,
) -> None:
    """
    Setup page configuration and inject modern CSS.

    Call this at the start of every page file.

    Args:
        title: Page title (for browser tab)
        icon: Page icon (emoji)
        layout: Layout mode
        config: Layout configuration

    Example:
        ```python
        setup_page(
            title="Beam Design | IS 456",
            icon="🏗️",
            layout="wide"
        )
        ```
    """
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout=layout,
        initial_sidebar_state="expanded",
    )

    inject_modern_css(config)
