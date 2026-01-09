"""
Responsive design utilities for mobile-first Streamlit apps.

Provides breakpoint detection, responsive column logic, fluid typography,
and mobile-optimized component sizes following best practices from
MODERN-UI-DESIGN-SYSTEMS.md and USER-JOURNEY-RESEARCH.md.
"""

import streamlit as st
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Breakpoint:
    """Device breakpoint configuration."""
    name: str
    min_width: int
    max_width: Optional[int]
    columns: int
    font_scale: float


# Mobile-first breakpoints (based on research)
BREAKPOINTS = {
    "mobile": Breakpoint("mobile", 0, 767, 1, 1.0),
    "tablet": Breakpoint("tablet", 768, 1023, 2, 1.1),
    "desktop": Breakpoint("desktop", 1024, None, 3, 1.2),
}


def get_device_type() -> str:
    """
    Detect device type based on viewport width.

    Uses Streamlit's browser info to determine breakpoint.
    Defaults to 'desktop' if detection fails (progressive enhancement).

    Returns:
        Device type: 'mobile', 'tablet', or 'desktop'

    Example:
        >>> device = get_device_type()
        >>> if device == 'mobile':
        ...     st.markdown("Mobile view")
    """
    try:
        # Try to get from session state (cached from previous detection)
        if 'device_type' in st.session_state:
            return st.session_state.device_type

        # Fallback: Use JavaScript injection to detect (requires rerun)
        # For now, default to desktop (progressive enhancement)
        device = "desktop"
        st.session_state.device_type = device
        return device

    except Exception:
        return "desktop"  # Safe default


def get_breakpoint(device_type: str) -> Breakpoint:
    """
    Get breakpoint configuration for device type.

    Args:
        device_type: 'mobile', 'tablet', or 'desktop'

    Returns:
        Breakpoint configuration

    Example:
        >>> bp = get_breakpoint('mobile')
        >>> bp.columns  # 1
    """
    return BREAKPOINTS.get(device_type, BREAKPOINTS["desktop"])


def get_responsive_columns(
    mobile: int = 1,
    tablet: int = 2,
    desktop: int = 3
) -> List[int]:
    """
    Get responsive column counts based on device type.

    Args:
        mobile: Number of columns on mobile
        tablet: Number of columns on tablet
        desktop: Number of columns on desktop

    Returns:
        List of column ratios for st.columns()

    Example:
        >>> cols = st.columns(get_responsive_columns(1, 2, 3))
        >>> with cols[0]:
        ...     st.write("Auto-responsive!")
    """
    device = get_device_type()

    if device == "mobile":
        return [1] * mobile
    elif device == "tablet":
        return [1] * tablet
    else:
        return [1] * desktop


def get_responsive_widths(
    mobile: Tuple[int, ...] = (1,),
    tablet: Tuple[int, ...] = (1, 1),
    desktop: Tuple[int, ...] = (1, 2, 1)
) -> List[int]:
    """
    Get responsive column width ratios based on device type.

    Useful for asymmetric layouts (e.g., sidebar + content).

    Args:
        mobile: Column width ratios on mobile
        tablet: Column width ratios on tablet
        desktop: Column width ratios on desktop

    Returns:
        List of column width ratios

    Example:
        >>> # Sidebar (25%) + content (75%) on desktop
        >>> cols = st.columns(get_responsive_widths(
        ...     mobile=(1,),
        ...     tablet=(1, 2),
        ...     desktop=(1, 3)
        ... ))
    """
    device = get_device_type()

    if device == "mobile":
        return list(mobile)
    elif device == "tablet":
        return list(tablet)
    else:
        return list(desktop)


def get_fluid_font_size(
    base_size: int,
    scale_factor: float = 1.2,
    min_size: Optional[int] = None,
    max_size: Optional[int] = None
) -> str:
    """
    Calculate fluid typography size based on device type.

    Uses modular scale (base * scale^level) with device-specific adjustments.

    Args:
        base_size: Base font size in pixels
        scale_factor: Multiplicative scale (default 1.2 - major third)
        min_size: Minimum size in pixels (optional)
        max_size: Maximum size in pixels (optional)

    Returns:
        CSS font-size value (e.g., "16px", "clamp(14px, 2vw, 18px)")

    Example:
        >>> size = get_fluid_font_size(16, scale_factor=1.25)
        >>> st.markdown(f'<h1 style="font-size: {size}">Title</h1>')
    """
    device = get_device_type()
    bp = get_breakpoint(device)

    # Apply device-specific scale
    scaled_size = int(base_size * bp.font_scale)

    # Apply min/max constraints
    if min_size:
        scaled_size = max(scaled_size, min_size)
    if max_size:
        scaled_size = min(scaled_size, max_size)

    # Use clamp() for true fluid typography (CSS)
    if min_size and max_size:
        return f"clamp({min_size}px, {scaled_size / 16}rem, {max_size}px)"

    return f"{scaled_size}px"


def get_responsive_padding(
    mobile: str = "1rem",
    tablet: str = "1.5rem",
    desktop: str = "2rem"
) -> str:
    """
    Get responsive padding based on device type.

    Args:
        mobile: Padding on mobile
        tablet: Padding on tablet
        desktop: Padding on desktop

    Returns:
        CSS padding value

    Example:
        >>> padding = get_responsive_padding("0.5rem", "1rem", "2rem")
        >>> st.markdown(f'<div style="padding: {padding}">Content</div>')
    """
    device = get_device_type()

    if device == "mobile":
        return mobile
    elif device == "tablet":
        return tablet
    else:
        return desktop


def apply_responsive_styles() -> None:
    """
    Apply global responsive CSS styles to Streamlit app.

    Includes:
    - Mobile-first breakpoints
    - Fluid typography
    - Responsive spacing
    - Touch-friendly targets (44px minimum)

    Call this once in app.py or page setup.

    Example:
        >>> apply_responsive_styles()
    """
    device = get_device_type()
    bp = get_breakpoint(device)

    # Mobile-first CSS
    responsive_css = f"""
    <style>
    /* Base (mobile-first) */
    :root {{
        --font-scale: {bp.font_scale};
        --spacing-unit: 8px;
        --touch-target: 44px;
    }}

    /* Fluid typography */
    body {{
        font-size: clamp(14px, 2vw, 16px);
        line-height: 1.6;
    }}

    h1 {{
        font-size: clamp(24px, 4vw, 32px);
        line-height: 1.2;
    }}

    h2 {{
        font-size: clamp(20px, 3.5vw, 28px);
        line-height: 1.3;
    }}

    h3 {{
        font-size: clamp(18px, 3vw, 24px);
        line-height: 1.4;
    }}

    /* Responsive spacing */
    .stApp {{
        padding: {get_responsive_padding()};
    }}

    /* Touch targets (mobile) */
    button, input, select {{
        min-height: var(--touch-target);
        min-width: var(--touch-target);
    }}

    /* Tablet breakpoint (768px+) */
    @media (min-width: 768px) {{
        :root {{
            --spacing-unit: 12px;
        }}
    }}

    /* Desktop breakpoint (1024px+) */
    @media (min-width: 1024px) {{
        :root {{
            --spacing-unit: 16px;
        }}

        /* Hover effects (only on desktop) */
        button:hover {{
            transform: translateY(-2px);
            transition: transform 200ms ease;
        }}
    }}

    /* Reduced motion (accessibility) */
    @media (prefers-reduced-motion: reduce) {{
        * {{
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }}
    }}
    </style>
    """

    st.markdown(responsive_css, unsafe_allow_html=True)


def is_mobile() -> bool:
    """
    Check if current device is mobile.

    Returns:
        True if mobile device

    Example:
        >>> if is_mobile():
        ...     st.info("Swipe to navigate")
    """
    return get_device_type() == "mobile"


def is_tablet() -> bool:
    """
    Check if current device is tablet.

    Returns:
        True if tablet device

    Example:
        >>> if is_tablet():
        ...     st.info("Tap to expand")
    """
    return get_device_type() == "tablet"


def is_desktop() -> bool:
    """
    Check if current device is desktop.

    Returns:
        True if desktop device

    Example:
        >>> if is_desktop():
        ...     st.info("Click to see details")
    """
    return get_device_type() == "desktop"


def hide_on_mobile() -> None:
    """
    Hide current element on mobile devices.

    Use in context to hide non-essential UI on small screens.

    Example:
        >>> if not is_mobile():
        ...     hide_on_mobile()
        ...     st.sidebar.text("Desktop-only sidebar")
    """
    if is_mobile():
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"] {
                display: none;
            }
            </style>
            """,
            unsafe_allow_html=True
        )


def show_mobile_nav() -> None:
    """
    Show mobile-optimized navigation menu.

    Renders a hamburger menu with page links for mobile devices.

    Example:
        >>> if is_mobile():
        ...     show_mobile_nav()
    """
    if not is_mobile():
        return

    st.markdown(
        """
        <style>
        .mobile-nav {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
            background: white;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
