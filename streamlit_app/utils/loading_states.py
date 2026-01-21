"""
Loading States - Skeleton loaders and animated loading indicators.

Provides smooth loading states for async operations and data fetching.

Version: 1.0
Created: 2026-01-08
"""

import streamlit as st
import time
from typing import Generator, Optional, Literal
from contextlib import contextmanager
from utils.design_system import COLORS, ANIMATION
from utils.theme_manager import get_theme_colors

LoaderType = Literal["skeleton", "spinner", "progress", "dots", "pulse"]


def add_loading_skeleton(
    height: str = "100px",
    count: int = 1,
    border_radius: str = "8px",
    margin: str = "8px 0",
) -> None:
    """
    Add animated skeleton loader for content that's loading.

    Args:
        height: Height of each skeleton block
        count: Number of skeleton blocks to show
        border_radius: Border radius of skeleton blocks
        margin: Margin between blocks

    Example:
        >>> add_loading_skeleton(height="50px", count=3)
    """
    theme = get_theme_colors()

    skeleton_html = f"""
    <style>
    @keyframes skeleton-loading {{
        0% {{
            background-position: -200px 0;
        }}
        100% {{
            background-position: calc(200px + 100%) 0;
        }}
    }}

    .skeleton-loader {{
        display: block;
        width: 100%;
        height: {height};
        margin: {margin};
        border-radius: {border_radius};
        background: linear-gradient(
            90deg,
            {theme['bg_secondary']} 0%,
            {theme['bg_tertiary']} 50%,
            {theme['bg_secondary']} 100%
        );
        background-size: 200px 100%;
        animation: skeleton-loading 1.5s ease-in-out infinite;
    }}
    </style>
    """

    # Add skeleton blocks
    for i in range(count):
        skeleton_html += f'<div class="skeleton-loader skeleton-{i}"></div>'

    st.markdown(skeleton_html, unsafe_allow_html=True)


def add_loading_spinner(
    size: str = "40px",
    color: Optional[str] = None,
    message: str = "Loading...",
) -> None:
    """
    Add animated spinner with optional message.

    Args:
        size: Size of spinner (CSS dimension)
        color: Color of spinner (hex code)
        message: Loading message to display

    Example:
        >>> add_loading_spinner(size="60px", message="Analyzing beam...")
    """
    theme = get_theme_colors()
    spinner_color = color or theme["primary"]

    spinner_html = f"""
    <style>
    @keyframes spinner-rotate {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}

    .loading-spinner-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 32px;
        gap: 16px;
    }}

    .loading-spinner {{
        width: {size};
        height: {size};
        border: 4px solid {theme['border_primary']};
        border-top: 4px solid {spinner_color};
        border-radius: 50%;
        animation: spinner-rotate 1s linear infinite;
    }}

    .loading-message {{
        color: {theme['text_secondary']};
        font-size: 14px;
        font-weight: 500;
    }}
    </style>

    <div class="loading-spinner-container">
        <div class="loading-spinner"></div>
        <div class="loading-message">{message}</div>
    </div>
    """

    st.markdown(spinner_html, unsafe_allow_html=True)


def add_loading_progress(
    progress: float,
    message: str = "Processing...",
    show_percentage: bool = True,
) -> None:
    """
    Add animated progress bar with percentage.

    Args:
        progress: Progress value (0.0 to 1.0)
        message: Loading message to display
        show_percentage: Whether to show percentage text

    Example:
        >>> add_loading_progress(0.75, "Calculating design...")
    """
    theme = get_theme_colors()
    percentage = int(progress * 100)

    progress_html = f"""
    <style>
    .progress-container {{
        width: 100%;
        padding: 16px;
    }}

    .progress-label {{
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        color: {theme['text_secondary']};
        font-size: 14px;
    }}

    .progress-bar-bg {{
        width: 100%;
        height: 8px;
        background-color: {theme['bg_tertiary']};
        border-radius: 4px;
        overflow: hidden;
    }}

    .progress-bar-fill {{
        height: 100%;
        width: {percentage}%;
        background: linear-gradient(90deg, {theme['primary']}, {theme['accent']});
        border-radius: 4px;
        transition: width {ANIMATION.normal} {ANIMATION.ease_in_out};
    }}
    </style>

    <div class="progress-container">
        <div class="progress-label">
            <span>{message}</span>
            {f'<span>{percentage}%</span>' if show_percentage else ''}
        </div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill"></div>
        </div>
    </div>
    """

    st.markdown(progress_html, unsafe_allow_html=True)


def add_loading_dots(message: str = "Loading", dot_count: int = 3) -> None:
    """
    Add animated loading dots indicator.

    Args:
        message: Loading message (dots will be appended)
        dot_count: Number of dots to animate

    Example:
        >>> add_loading_dots("Fetching data")
    """
    theme = get_theme_colors()

    dots_html = f"""
    <style>
    @keyframes dot-flashing {{
        0%, 80%, 100% {{
            opacity: 0;
        }}
        40% {{
            opacity: 1;
        }}
    }}

    .loading-dots-container {{
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 16px;
        color: {theme['text_secondary']};
        font-size: 16px;
    }}

    .loading-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: {theme['primary']};
        animation: dot-flashing 1.4s infinite;
    }}

    .loading-dot:nth-child(2) {{
        animation-delay: 0.2s;
    }}

    .loading-dot:nth-child(3) {{
        animation-delay: 0.4s;
    }}
    </style>

    <div class="loading-dots-container">
        <span>{message}</span>
        {''.join([f'<div class="loading-dot"></div>' for _ in range(dot_count)])}
    </div>
    """

    st.markdown(dots_html, unsafe_allow_html=True)


def add_loading_pulse(
    size: str = "60px",
    color: Optional[str] = None,
    message: str = "",
) -> None:
    """
    Add pulsing loader with optional message.

    Args:
        size: Size of pulse circle
        color: Color of pulse
        message: Optional message below pulse

    Example:
        >>> add_loading_pulse(size="80px", message="Analyzing...")
    """
    theme = get_theme_colors()
    pulse_color = color or theme["accent"]

    pulse_html = f"""
    <style>
    @keyframes pulse-scale {{
        0%, 100% {{
            transform: scale(0.8);
            opacity: 1;
        }}
        50% {{
            transform: scale(1.2);
            opacity: 0.5;
        }}
    }}

    .pulse-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 32px;
        gap: 16px;
    }}

    .pulse-circle {{
        width: {size};
        height: {size};
        border-radius: 50%;
        background-color: {pulse_color};
        animation: pulse-scale 2s ease-in-out infinite;
    }}

    .pulse-message {{
        color: {theme['text_secondary']};
        font-size: 14px;
        font-weight: 500;
    }}
    </style>

    <div class="pulse-container">
        <div class="pulse-circle"></div>
        {f'<div class="pulse-message">{message}</div>' if message else ''}
    </div>
    """

    st.markdown(pulse_html, unsafe_allow_html=True)


@contextmanager
def loading_context(
    loader_type: LoaderType = "spinner",
    message: str = "Loading...",
    min_display_time: float = 0.5,
) -> Generator[None, None, None]:
    """Context manager for showing loading state during operation.

    Args:
        loader_type: Type of loader to show
        message: Loading message
        min_display_time: Minimum time to show loader (seconds)

    Yields:
        None

    Example:
        >>> with loading_context("spinner", "Calculating..."):
        ...     result = expensive_calculation()
    """
    start_time = time.time()

    # Create placeholder for loading indicator
    placeholder = st.empty()

    with placeholder.container():
        if loader_type == "skeleton":
            add_loading_skeleton()
        elif loader_type == "spinner":
            add_loading_spinner(message=message)
        elif loader_type == "dots":
            add_loading_dots(message)
        elif loader_type == "pulse":
            add_loading_pulse(message=message)
        else:
            st.info(message)

    try:
        yield placeholder
    finally:
        # Ensure minimum display time
        elapsed = time.time() - start_time
        if elapsed < min_display_time:
            time.sleep(min_display_time - elapsed)

        # Clear the loading indicator
        placeholder.empty()


def show_loading_card(
    title: str = "Loading",
    description: str = "Please wait...",
    loader_type: LoaderType = "spinner",
) -> None:
    """
    Show a full loading card with title, description, and loader.

    Args:
        title: Card title
        description: Card description
        loader_type: Type of loader to show

    Example:
        >>> show_loading_card("Analyzing Design", "Running calculations...")
    """
    theme = get_theme_colors()

    card_html = f"""
    <style>
    .loading-card {{
        background-color: {theme['bg_secondary']};
        border: 1px solid {theme['border_primary']};
        border-radius: 8px;
        padding: 24px;
        margin: 16px 0;
        text-align: center;
    }}

    .loading-card-title {{
        color: {theme['text_primary']};
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 8px;
    }}

    .loading-card-description {{
        color: {theme['text_secondary']};
        font-size: 14px;
        margin-bottom: 24px;
    }}
    </style>

    <div class="loading-card">
        <div class="loading-card-title">{title}</div>
        <div class="loading-card-description">{description}</div>
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)

    if loader_type == "skeleton":
        add_loading_skeleton(count=3)
    elif loader_type == "spinner":
        add_loading_spinner(message="")
    elif loader_type == "dots":
        add_loading_dots("")
    elif loader_type == "pulse":
        add_loading_pulse(message="")


def add_shimmer_effect(height: str = "100px", width: str = "100%") -> None:
    """
    Add shimmer effect (moving gradient) for loading placeholders.

    Args:
        height: Height of shimmer block
        width: Width of shimmer block

    Example:
        >>> add_shimmer_effect(height="200px")
    """
    theme = get_theme_colors()

    shimmer_html = f"""
    <style>
    @keyframes shimmer {{
        0% {{
            background-position: -1000px 0;
        }}
        100% {{
            background-position: 1000px 0;
        }}
    }}

    .shimmer-block {{
        width: {width};
        height: {height};
        background: linear-gradient(
            90deg,
            {theme['bg_secondary']} 25%,
            {theme['bg_tertiary']} 50%,
            {theme['bg_secondary']} 75%
        );
        background-size: 1000px 100%;
        animation: shimmer 2s infinite;
        border-radius: 8px;
        margin: 8px 0;
    }}
    </style>

    <div class="shimmer-block"></div>
    """

    st.markdown(shimmer_html, unsafe_allow_html=True)


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    "LoaderType",
    "add_loading_skeleton",
    "add_loading_spinner",
    "add_loading_progress",
    "add_loading_dots",
    "add_loading_pulse",
    "loading_context",
    "show_loading_card",
    "add_shimmer_effect",
]
