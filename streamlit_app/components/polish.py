"""
Visual Polish Components for Streamlit App

Provides loading states, empty states, toast notifications, and other
visual polish features to enhance user experience.

Author: Agent 6 (STREAMLIT SPECIALIST)
Date: 2026-01-09
"""

import streamlit as st
from typing import Literal, Optional
import time


def show_skeleton_loader(rows: int = 3, height: int = 60) -> None:
    """
    Display a skeleton loading screen with animated pulse effect.

    Args:
        rows: Number of skeleton rows to display (default: 3)
        height: Height of each skeleton row in pixels (default: 60)

    Example:
        show_skeleton_loader(rows=5, height=80)
    """
    skeleton_css = f"""
    <style>
    .skeleton {{
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: skeleton-loading 1.5s ease-in-out infinite;
        border-radius: 8px;
        margin-bottom: 12px;
        height: {height}px;
    }}

    @keyframes skeleton-loading {{
        0% {{ background-position: 200% 0; }}
        100% {{ background-position: -200% 0; }}
    }}
    </style>
    """

    st.markdown(skeleton_css, unsafe_allow_html=True)

    for i in range(rows):
        st.markdown(f'<div class="skeleton"></div>', unsafe_allow_html=True)


def show_empty_state(
    title: str,
    message: str,
    icon: str = "📭",
    action_label: Optional[str] = None,
    action_key: Optional[str] = None
) -> bool:
    """
    Display a friendly empty state with icon, title, message, and optional action.

    Args:
        title: Main heading for empty state
        message: Descriptive message explaining the empty state
        icon: Emoji or icon to display (default: "📭")
        action_label: Optional label for action button
        action_key: Unique key for action button (required if action_label provided)

    Returns:
        True if action button clicked, False otherwise

    Example:
        clicked = show_empty_state(
            title="No Results Found",
            message="Try adjusting your design parameters.",
            icon="🔍",
            action_label="Reset Inputs",
            action_key="reset_btn"
        )
    """
    empty_css = """
    <style>
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 60px 20px;
        text-align: center;
        background: #f8f9fa;
        border-radius: 12px;
        margin: 20px 0;
    }

    .empty-icon {
        font-size: 64px;
        margin-bottom: 16px;
        opacity: 0.8;
    }

    .empty-title {
        font-size: 24px;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 8px;
    }

    .empty-message {
        font-size: 16px;
        color: #7f8c8d;
        max-width: 400px;
        line-height: 1.5;
    }
    </style>
    """

    st.markdown(empty_css, unsafe_allow_html=True)

    empty_html = f"""
    <div class="empty-state">
        <div class="empty-icon">{icon}</div>
        <div class="empty-title">{title}</div>
        <div class="empty-message">{message}</div>
    </div>
    """

    st.markdown(empty_html, unsafe_allow_html=True)

    if action_label and action_key:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            return st.button(action_label, key=action_key, width="stretch")

    return False


def show_toast(
    message: str,
    type: Literal["info", "success", "warning", "error"] = "info",
    duration: int = 3000
) -> None:
    """
    Display a toast notification with auto-dismiss.

    Args:
        message: Message to display in toast
        type: Toast type - "info", "success", "warning", or "error" (default: "info")
        duration: Duration in milliseconds before auto-dismiss (default: 3000)

    Example:
        show_toast("Design calculation complete!", type="success", duration=2000)
    """
    # Color mapping for toast types
    colors = {
        "info": "#3498db",
        "success": "#27ae60",
        "warning": "#f39c12",
        "error": "#e74c3c"
    }

    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌"
    }

    color = colors.get(type, colors["info"])
    icon = icons.get(type, icons["info"])

    toast_css = f"""
    <style>
    @keyframes toast-slide-in {{
        from {{
            transform: translateY(-100px);
            opacity: 0;
        }}
        to {{
            transform: translateY(0);
            opacity: 1;
        }}
    }}

    @keyframes toast-fade-out {{
        from {{
            opacity: 1;
        }}
        to {{
            opacity: 0;
        }}
    }}

    .toast {{
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        background: white;
        border-left: 4px solid {color};
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border-radius: 8px;
        padding: 16px 20px;
        display: flex;
        align-items: center;
        gap: 12px;
        min-width: 300px;
        max-width: 500px;
        animation: toast-slide-in 0.3s ease-out, toast-fade-out 0.3s ease-in {duration - 300}ms forwards;
    }}

    .toast-icon {{
        font-size: 24px;
    }}

    .toast-message {{
        flex: 1;
        color: #2c3e50;
        font-size: 14px;
        line-height: 1.4;
    }}
    </style>
    """

    st.markdown(toast_css, unsafe_allow_html=True)

    toast_html = f"""
    <div class="toast">
        <div class="toast-icon">{icon}</div>
        <div class="toast-message">{message}</div>
    </div>
    """

    # Use st.empty() to allow auto-dismiss
    placeholder = st.empty()
    placeholder.markdown(toast_html, unsafe_allow_html=True)
    time.sleep(duration / 1000)
    placeholder.empty()


def show_progress(
    current: int,
    total: int,
    label: str = "",
    show_percentage: bool = True,
    color: str = "#3498db"
) -> None:
    """
    Display a custom progress bar with label and percentage.

    Args:
        current: Current progress value
        total: Total/maximum value
        label: Optional label to display above progress bar
        show_percentage: Whether to show percentage text (default: True)
        color: Progress bar color (default: "#3498db")

    Example:
        show_progress(7, 10, label="Processing beams", color="#27ae60")
    """
    if total <= 0:
        percentage = 0
    else:
        percentage = min(100, max(0, (current / total) * 100))

    progress_css = f"""
    <style>
    .progress-container {{
        margin: 16px 0;
    }}

    .progress-label {{
        font-size: 14px;
        color: #2c3e50;
        margin-bottom: 8px;
        font-weight: 500;
    }}

    .progress-bar-bg {{
        width: 100%;
        height: 24px;
        background: #e0e0e0;
        border-radius: 12px;
        overflow: hidden;
        position: relative;
    }}

    .progress-bar-fill {{
        height: 100%;
        background: {color};
        border-radius: 12px;
        transition: width 0.3s ease-out;
        width: {percentage}%;
    }}

    .progress-percentage {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: {('#ffffff' if percentage > 50 else '#2c3e50')};
        font-size: 12px;
        font-weight: 600;
    }}
    </style>
    """

    st.markdown(progress_css, unsafe_allow_html=True)

    progress_html = f"""
    <div class="progress-container">
        {f'<div class="progress-label">{label}</div>' if label else ''}
        <div class="progress-bar-bg">
            <div class="progress-bar-fill"></div>
            {f'<div class="progress-percentage">{percentage:.0f}%</div>' if show_percentage else ''}
        </div>
    </div>
    """

    st.markdown(progress_html, unsafe_allow_html=True)


def apply_hover_effect(
    element_selector: str = ".stButton button",
    hover_color: str = "#2980b9",
    transition_duration: str = "0.2s"
) -> None:
    """
    Apply hover effects to specified elements using CSS.

    Args:
        element_selector: CSS selector for target elements (default: ".stButton button")
        hover_color: Color on hover (default: "#2980b9")
        transition_duration: Transition duration (default: "0.2s")

    Example:
        apply_hover_effect(".stButton button", hover_color="#27ae60")
    """
    hover_css = f"""
    <style>
    {element_selector} {{
        transition: all {transition_duration} ease-in-out;
    }}

    {element_selector}:hover {{
        background-color: {hover_color} !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }}

    {element_selector}:active {{
        transform: translateY(0);
    }}
    </style>
    """

    st.markdown(hover_css, unsafe_allow_html=True)


def apply_smooth_transitions(duration: str = "0.3s", easing: str = "ease-in-out") -> None:
    """
    Apply smooth transitions to all interactive elements globally.

    Args:
        duration: Transition duration (default: "0.3s")
        easing: Easing function (default: "ease-in-out")

    Example:
        apply_smooth_transitions(duration="0.2s", easing="cubic-bezier(0.4, 0, 0.2, 1)")
    """
    transition_css = f"""
    <style>
    /* Smooth transitions for interactive elements */
    .stButton button,
    .stSelectbox select,
    .stNumberInput input,
    .stTextInput input,
    .stSlider,
    .stCheckbox,
    .stRadio {{
        transition: all {duration} {easing};
    }}

    /* Focus states */
    .stButton button:focus,
    .stSelectbox select:focus,
    .stNumberInput input:focus,
    .stTextInput input:focus {{
        outline: 2px solid #3498db;
        outline-offset: 2px;
    }}

    /* Smooth scroll */
    html {{
        scroll-behavior: smooth;
    }}
    </style>
    """

    st.markdown(transition_css, unsafe_allow_html=True)
