"""
Theme Manager - Dark mode toggle and theme persistence.

Handles theme switching, session state, and CSS injection.

Version: 1.0
Created: 2026-01-08
"""

import streamlit as st
from typing import Literal
from utils.design_system import generate_css_variables, DARK_COLORS, COLORS

ThemeMode = Literal["light", "dark", "auto"]


def initialize_theme() -> None:
    """Initialize theme in session state if not already set."""
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "light"
    if "use_dark_mode" not in st.session_state:
        st.session_state.use_dark_mode = False


def get_current_theme() -> ThemeMode:
    """
    Get current theme mode from session state.

    Returns:
        Current theme mode ('light', 'dark', or 'auto')
    """
    initialize_theme()
    return st.session_state.theme_mode


def set_theme(mode: ThemeMode) -> None:
    """
    Set theme mode and update session state.

    Args:
        mode: Theme mode to set ('light', 'dark', or 'auto')
    """
    initialize_theme()
    st.session_state.theme_mode = mode
    st.session_state.use_dark_mode = mode == "dark"


def toggle_theme() -> None:
    """Toggle between light and dark mode."""
    initialize_theme()
    current = st.session_state.use_dark_mode
    st.session_state.use_dark_mode = not current
    st.session_state.theme_mode = "dark" if not current else "light"


def apply_dark_mode_theme() -> None:
    """
    Apply dark mode theme with CSS injection.

    Injects CSS variables and overrides for dark mode styling.
    Call this at the top of each page that supports dark mode.
    """
    initialize_theme()
    use_dark = st.session_state.use_dark_mode

    # Generate CSS variables for the current theme
    css_vars = generate_css_variables(dark_mode=use_dark)

    # Additional dark mode overrides for Streamlit components
    if use_dark:
        dark_overrides = f"""
        <style>
        {css_vars}

        /* Dark mode overrides */
        .stApp {{
            background-color: {DARK_COLORS.bg_primary};
            color: {DARK_COLORS.text_primary};
        }}

        .stApp header {{
            background-color: {DARK_COLORS.bg_secondary};
            border-bottom: 1px solid {DARK_COLORS.border_primary};
        }}

        /* Sidebar dark mode */
        section[data-testid="stSidebar"] {{
            background-color: {DARK_COLORS.bg_secondary};
            border-right: 1px solid {DARK_COLORS.border_primary};
        }}

        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] label {{
            color: {DARK_COLORS.text_primary} !important;
        }}

        /* Cards and containers */
        .metric-card,
        .info-card,
        .result-card {{
            background-color: {DARK_COLORS.bg_secondary};
            border-color: {DARK_COLORS.border_primary};
        }}

        /* Input fields */
        .stTextInput input,
        .stNumberInput input,
        .stSelectbox select {{
            background-color: {DARK_COLORS.bg_tertiary};
            color: {DARK_COLORS.text_primary};
            border-color: {DARK_COLORS.border_primary};
        }}

        .stTextInput input::placeholder,
        .stNumberInput input::placeholder {{
            color: {DARK_COLORS.text_tertiary};
        }}

        /* Buttons */
        .stButton button {{
            background-color: {DARK_COLORS.primary};
            color: {DARK_COLORS.text_primary};
            border-color: {DARK_COLORS.border_primary};
        }}

        .stButton button:hover {{
            background-color: {DARK_COLORS.primary_hover};
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: {DARK_COLORS.bg_secondary};
            border-bottom: 1px solid {DARK_COLORS.border_primary};
        }}

        .stTabs [data-baseweb="tab"] {{
            color: {DARK_COLORS.text_secondary};
        }}

        .stTabs [aria-selected="true"] {{
            color: {DARK_COLORS.text_primary};
            border-bottom-color: {DARK_COLORS.accent};
        }}

        /* Dataframes */
        .stDataFrame {{
            background-color: {DARK_COLORS.bg_secondary};
        }}

        .stDataFrame table {{
            color: {DARK_COLORS.text_primary};
        }}

        .stDataFrame th {{
            background-color: {DARK_COLORS.bg_tertiary};
            color: {DARK_COLORS.text_primary};
        }}

        /* Metrics */
        [data-testid="stMetricValue"] {{
            color: {DARK_COLORS.text_primary};
        }}

        [data-testid="stMetricLabel"] {{
            color: {DARK_COLORS.text_secondary};
        }}

        /* Expanders */
        .streamlit-expanderHeader {{
            background-color: {DARK_COLORS.bg_secondary};
            color: {DARK_COLORS.text_primary};
            border-color: {DARK_COLORS.border_primary};
        }}

        .streamlit-expanderContent {{
            background-color: {DARK_COLORS.bg_tertiary};
            border-color: {DARK_COLORS.border_primary};
        }}

        /* Code blocks */
        code {{
            background-color: {DARK_COLORS.bg_tertiary};
            color: {DARK_COLORS.accent};
        }}

        pre {{
            background-color: {DARK_COLORS.bg_tertiary};
            border-color: {DARK_COLORS.border_primary};
        }}

        /* Links */
        a {{
            color: {DARK_COLORS.primary};
        }}

        a:hover {{
            color: {DARK_COLORS.primary_hover};
        }}

        /* Scrollbar for dark mode */
        ::-webkit-scrollbar {{
            width: 10px;
            height: 10px;
        }}

        ::-webkit-scrollbar-track {{
            background: {DARK_COLORS.bg_primary};
        }}

        ::-webkit-scrollbar-thumb {{
            background: {DARK_COLORS.border_primary};
            border-radius: 5px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: {DARK_COLORS.text_tertiary};
        }}
        </style>
        """
        st.markdown(dark_overrides, unsafe_allow_html=True)
    else:
        # Light mode CSS
        light_css = f"""
        <style>
        {css_vars}

        /* Light mode overrides */
        .stApp {{
            background-color: {COLORS.gray_50};
        }}

        section[data-testid="stSidebar"] {{
            background-color: white;
        }}
        </style>
        """
        st.markdown(light_css, unsafe_allow_html=True)


def render_theme_toggle() -> None:
    """
    Render theme toggle button in sidebar.

    Displays a toggle button that switches between light and dark mode.
    """
    initialize_theme()

    with st.sidebar:
        st.markdown("---")

        # Theme toggle section
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown("**Theme**")

        with col2:
            # Use emoji for visual feedback
            current_icon = "🌙" if st.session_state.use_dark_mode else "☀️"
            if st.button(current_icon, key="theme_toggle", help="Toggle dark mode"):
                toggle_theme()
                st.rerun()

        # Optional: Show current theme mode
        mode_text = "Dark Mode" if st.session_state.use_dark_mode else "Light Mode"
        st.caption(f"Current: {mode_text}")


def get_theme_colors() -> dict:
    """
    Get current theme colors for use in components.

    Returns:
        Dictionary with color values for current theme
    """
    initialize_theme()
    use_dark = st.session_state.use_dark_mode

    if use_dark:
        return {
            "bg_primary": DARK_COLORS.bg_primary,
            "bg_secondary": DARK_COLORS.bg_secondary,
            "bg_tertiary": DARK_COLORS.bg_tertiary,
            "text_primary": DARK_COLORS.text_primary,
            "text_secondary": DARK_COLORS.text_secondary,
            "text_tertiary": DARK_COLORS.text_tertiary,
            "border_primary": DARK_COLORS.border_primary,
            "border_secondary": DARK_COLORS.border_secondary,
            "primary": DARK_COLORS.primary,
            "primary_hover": DARK_COLORS.primary_hover,
            "accent": DARK_COLORS.accent,
            "accent_hover": DARK_COLORS.accent_hover,
        }
    else:
        return {
            "bg_primary": COLORS.gray_50,
            "bg_secondary": "#FFFFFF",
            "bg_tertiary": COLORS.gray_100,
            "text_primary": COLORS.gray_900,
            "text_secondary": COLORS.gray_600,
            "text_tertiary": COLORS.gray_500,
            "border_primary": COLORS.gray_300,
            "border_secondary": COLORS.gray_200,
            "primary": COLORS.primary_500,
            "primary_hover": COLORS.primary_600,
            "accent": COLORS.accent_500,
            "accent_hover": COLORS.accent_600,
        }


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "ThemeMode",
    "initialize_theme",
    "get_current_theme",
    "set_theme",
    "toggle_theme",
    "apply_dark_mode_theme",
    "render_theme_toggle",
    "get_theme_colors",
]
