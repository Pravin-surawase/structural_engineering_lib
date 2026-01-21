"""
Styled Components Library - Reusable UI components with consistent styling.

Based on RESEARCH-005 (Streamlit Custom Components & Styling).
Provides professional, accessible UI components.

Version: 1.0
Created: 2026-01-08
"""

import streamlit as st
from typing import Optional, Literal, List
from .design_system import (
    COLORS,
    SPACING,
    ELEVATION,
    RADIUS,
    TYPOGRAPHY,
    get_semantic_color,
)

# ============================================================================
# HELPER: CSS INJECTION
# ============================================================================


def inject_custom_css(css: str) -> None:
    """
    Inject custom CSS into the Streamlit app.

    Args:
        css: CSS string to inject
    """
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# ============================================================================
# COMPONENT: STYLED CARD
# ============================================================================


def styled_card(
    content: str,
    title: Optional[str] = None,
    elevation: Literal[1, 2, 3, 4] = 1,
    padding: Literal["sm", "md", "lg"] = "md",
    border_color: Optional[str] = None,
) -> None:
    """
    Display content in a styled card with elevation.

    Args:
        content: HTML content to display
        title: Optional card title
        elevation: Shadow level (1-4)
        padding: Padding size (sm, md, lg)
        border_color: Optional border color (hex)

    Example:
        >>> styled_card(
        ...     title="Design Summary",
        ...     content="<p>Ast = 1200 mm²</p>",
        ...     elevation=2
        ... )
    """
    elevation_map = {
        1: ELEVATION.level_1,
        2: ELEVATION.level_2,
        3: ELEVATION.level_3,
        4: ELEVATION.level_4,
    }

    padding_map = {
        "sm": SPACING.space_4,
        "md": SPACING.space_5,
        "lg": SPACING.space_6,
    }

    shadow = elevation_map[elevation]
    pad = padding_map[padding]
    border = f"border-left: 4px solid {border_color};" if border_color else ""

    card_html = f"""
    <div style="
        background: white;
        border-radius: {RADIUS.lg};
        box-shadow: {shadow};
        padding: {pad};
        {border}
        margin-bottom: {SPACING.space_4};
    ">
        {f'<h4 style="margin-top: 0; color: {COLORS.gray_900}; font-size: {TYPOGRAPHY.h4_size};">{title}</h4>' if title else ''}
        {content}
    </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)


# ============================================================================
# COMPONENT: STATUS BADGE
# ============================================================================


def status_badge(
    text: str,
    status: Literal["success", "warning", "error", "info"] = "info",
    size: Literal["sm", "md", "lg"] = "md",
) -> str:
    """
    Create a status badge HTML.

    Args:
        text: Badge text
        status: Badge status type
        size: Badge size

    Returns:
        HTML string for badge

    Example:
        >>> badge = status_badge("Compliant", "success")
        >>> st.markdown(badge, unsafe_allow_html=True)
    """
    color = get_semantic_color(status, "base")
    bg_color = get_semantic_color(status, "light")

    size_map = {
        "sm": (TYPOGRAPHY.caption_size, f"{SPACING.space_1} {SPACING.space_2}"),
        "md": (TYPOGRAPHY.body_sm_size, f"{SPACING.space_2} {SPACING.space_3}"),
        "lg": (TYPOGRAPHY.body_size, f"{SPACING.space_3} {SPACING.space_4}"),
    }

    font_size, padding = size_map[size]

    return f"""
    <span style="
        display: inline-block;
        background: {bg_color};
        color: {color};
        font-size: {font_size};
        font-weight: 500;
        padding: {padding};
        border-radius: {RADIUS.md};
        line-height: 1;
    ">
        {text}
    </span>
    """


# ============================================================================
# COMPONENT: METRIC CARD
# ============================================================================


def metric_card(
    label: str,
    value: str,
    unit: str = "",
    delta: Optional[str] = None,
    delta_color: Literal["success", "warning", "error"] = "success",
    help_text: Optional[str] = None,
) -> None:
    """
    Display a metric in a styled card.

    Args:
        label: Metric label
        value: Metric value (formatted string)
        unit: Unit of measurement
        delta: Optional change/comparison value
        delta_color: Color for delta indicator
        help_text: Optional help text tooltip

    Example:
        >>> metric_card(
        ...     label="Steel Area",
        ...     value="1200",
        ...     unit="mm²",
        ...     delta="+50 vs minimum",
        ...     delta_color="success"
        ... )
    """
    delta_html = ""
    if delta:
        delta_bg = get_semantic_color(delta_color, "light")
        delta_fg = get_semantic_color(delta_color, "base")
        delta_html = f"""
        <div style="
            color: {delta_fg};
            background: {delta_bg};
            font-size: {TYPOGRAPHY.body_sm_size};
            padding: {SPACING.space_1} {SPACING.space_2};
            border-radius: {RADIUS.sm};
            display: inline-block;
            margin-top: {SPACING.space_2};
        ">
            {delta}
        </div>
        """

    help_icon = ""
    if help_text:
        help_icon = f'<span title="{help_text}" style="cursor: help; margin-left: 4px; color: {COLORS.gray_400};">ⓘ</span>'

    content = f"""
    <div style="text-align: center;">
        <div style="
            font-size: {TYPOGRAPHY.body_sm_size};
            color: {COLORS.gray_500};
            margin-bottom: {SPACING.space_2};
            font-weight: 500;
        ">
            {label}{help_icon}
        </div>
        <div style="
            font-family: {TYPOGRAPHY.font_mono};
            font-size: {TYPOGRAPHY.h2_size};
            color: {COLORS.gray_900};
            font-weight: 700;
            line-height: 1;
        ">
            {value}<span style="font-size: {TYPOGRAPHY.body_size}; color: {COLORS.gray_600};"> {unit}</span>
        </div>
        {delta_html}
    </div>
    """

    styled_card(content, elevation=1, padding="md")


# ============================================================================
# COMPONENT: ALERT BOX
# ============================================================================


def alert_box(
    message: str,
    alert_type: Literal["success", "warning", "error", "info"] = "info",
    dismissible: bool = False,
    icon: Optional[str] = None,
) -> None:
    """
    Display an alert message box.

    Args:
        message: Alert message text
        alert_type: Type of alert
        dismissible: Show dismiss button (not functional in static HTML)
        icon: Optional emoji icon

    Example:
        >>> alert_box(
        ...     "Design complies with IS 456:2000",
        ...     alert_type="success",
        ...     icon="✓"
        ... )
    """
    color = get_semantic_color(alert_type, "base")
    bg_color = get_semantic_color(alert_type, "light")

    icon_map = {
        "success": "✓",
        "warning": "⚠",
        "error": "✕",
        "info": "ℹ",
    }

    icon_display = icon if icon else icon_map[alert_type]

    alert_html = f"""
    <div style="
        background: {bg_color};
        border-left: 4px solid {color};
        color: {COLORS.gray_900};
        padding: {SPACING.space_4};
        border-radius: {RADIUS.md};
        margin-bottom: {SPACING.space_4};
        display: flex;
        align-items: center;
        gap: {SPACING.space_3};
    ">
        <div style="
            font-size: 24px;
            color: {color};
            flex-shrink: 0;
        ">
            {icon_display}
        </div>
        <div style="flex: 1;">
            {message}
        </div>
    </div>
    """

    st.markdown(alert_html, unsafe_allow_html=True)


# ============================================================================
# COMPONENT: PROGRESS BAR
# ============================================================================


def progress_bar(
    value: float,
    max_value: float = 100.0,
    label: Optional[str] = None,
    show_percentage: bool = True,
    color: Optional[str] = None,
) -> None:
    """
    Display a custom styled progress bar.

    Args:
        value: Current value
        max_value: Maximum value
        label: Optional label text
        show_percentage: Show percentage text
        color: Custom bar color (defaults to primary)

    Example:
        >>> progress_bar(
        ...     value=85.5,
        ...     max_value=100,
        ...     label="Utilization Ratio",
        ...     color="#10B981"
        ... )
    """
    percentage = min((value / max_value) * 100, 100)

    # Auto-color based on percentage if not specified
    if color is None:
        if percentage < 70:
            color = COLORS.success
        elif percentage < 85:
            color = COLORS.warning
        else:
            color = COLORS.error

    progress_html = f"""
    <div style="margin-bottom: {SPACING.space_4};">
        {f'<div style="font-size: {TYPOGRAPHY.body_sm_size}; color: {COLORS.gray_600}; margin-bottom: {SPACING.space_2};">{label}</div>' if label else ''}
        <div style="
            background: {COLORS.gray_200};
            border-radius: {RADIUS.full};
            height: 12px;
            position: relative;
            overflow: hidden;
        ">
            <div style="
                background: {color};
                width: {percentage}%;
                height: 100%;
                border-radius: {RADIUS.full};
                transition: width 0.3s ease;
            "></div>
        </div>
        {f'<div style="font-family: {TYPOGRAPHY.font_mono}; font-size: {TYPOGRAPHY.caption_size}; color: {COLORS.gray_500}; margin-top: {SPACING.space_1}; text-align: right;">{percentage:.1f}%</div>' if show_percentage else ''}
    </div>
    """

    st.markdown(progress_html, unsafe_allow_html=True)


# ============================================================================
# COMPONENT: DATA TABLE
# ============================================================================


def styled_table(
    headers: List[str],
    rows: List[List[str]],
    align: List[Literal["left", "center", "right"]] = None,
    zebra: bool = True,
) -> None:
    """
    Display a styled data table.

    Args:
        headers: List of header labels
        rows: List of rows (each row is list of cell values)
        align: Alignment for each column
        zebra: Use zebra striping

    Example:
        >>> styled_table(
        ...     headers=["Parameter", "Value", "Unit"],
        ...     rows=[
        ...         ["Width (b)", "300", "mm"],
        ...         ["Depth (D)", "500", "mm"]
        ...     ],
        ...     align=["left", "right", "left"]
        ... )
    """
    if align is None:
        align = ["left"] * len(headers)

    # Build header row
    header_cells = "".join(
        f'<th style="text-align: {align[i]}; padding: {SPACING.space_3}; background: {COLORS.primary_500}; color: white; font-weight: 600;">{h}</th>'
        for i, h in enumerate(headers)
    )

    # Build body rows
    body_rows = []
    for row_idx, row in enumerate(rows):
        row_bg = COLORS.gray_50 if (zebra and row_idx % 2 == 1) else "white"
        cells = "".join(
            f'<td style="text-align: {align[i]}; padding: {SPACING.space_3}; border-bottom: 1px solid {COLORS.gray_200};">{cell}</td>'
            for i, cell in enumerate(row)
        )
        body_rows.append(
            f'<tr style="background: {row_bg}; transition: background 0.2s;">{cells}</tr>'
        )

    table_html = f"""
    <table style="
        width: 100%;
        border-collapse: collapse;
        border-radius: {RADIUS.md};
        overflow: hidden;
        box-shadow: {ELEVATION.level_1};
        margin-bottom: {SPACING.space_4};
        font-family: {TYPOGRAPHY.font_mono};
        font-size: {TYPOGRAPHY.body_sm_size};
    ">
        <thead>
            <tr>{header_cells}</tr>
        </thead>
        <tbody>
            {''.join(body_rows)}
        </tbody>
    </table>
    """

    st.markdown(table_html, unsafe_allow_html=True)


# ============================================================================
# COMPONENT: COLLAPSIBLE SECTION
# ============================================================================


def collapsible_section(title: str, content: str, default_open: bool = False) -> None:
    """
    Display a collapsible section with title.

    Args:
        title: Section title
        content: Section content (HTML)
        default_open: Whether section starts open

    Example:
        >>> collapsible_section(
        ...     title="Detailed Calculations",
        ...     content="<p>Mu = 0.87 * fy * Ast * (d - 0.42 * xu)</p>"
        ... )
    """
    open_attr = "open" if default_open else ""

    section_html = f"""
    <details {open_attr} style="
        border: 1px solid {COLORS.gray_200};
        border-radius: {RADIUS.md};
        padding: {SPACING.space_4};
        margin-bottom: {SPACING.space_4};
        background: white;
    ">
        <summary style="
            font-weight: 600;
            color: {COLORS.gray_900};
            cursor: pointer;
            user-select: none;
            font-size: {TYPOGRAPHY.body_size};
        ">
            {title}
        </summary>
        <div style="
            margin-top: {SPACING.space_3};
            padding-top: {SPACING.space_3};
            border-top: 1px solid {COLORS.gray_200};
        ">
            {content}
        </div>
    </details>
    """

    st.markdown(section_html, unsafe_allow_html=True)


# ============================================================================
# COMPONENT: ICON BUTTON (HTML only, not interactive)
# ============================================================================


def icon_button_html(
    label: str,
    icon: str = "",
    variant: Literal["primary", "secondary", "danger"] = "primary",
    size: Literal["sm", "md", "lg"] = "md",
) -> str:
    """
    Generate HTML for a styled button (display only).

    Args:
        label: Button text
        icon: Optional emoji icon
        variant: Button style variant
        size: Button size

    Returns:
        HTML string for button

    Example:
        >>> btn = icon_button_html("Download PDF", "📄", "primary")
        >>> st.markdown(btn, unsafe_allow_html=True)
    """
    variant_styles = {
        "primary": (COLORS.primary_500, "white", COLORS.primary_600),
        "secondary": (COLORS.gray_200, COLORS.gray_900, COLORS.gray_300),
        "danger": (COLORS.error, "white", COLORS.error_dark),
    }

    bg, fg, hover = variant_styles[variant]

    size_map = {
        "sm": ("32px", f"{SPACING.space_2} {SPACING.space_4}", TYPOGRAPHY.body_sm_size),
        "md": ("40px", f"{SPACING.space_3} {SPACING.space_5}", TYPOGRAPHY.body_size),
        "lg": ("48px", f"{SPACING.space_4} {SPACING.space_6}", TYPOGRAPHY.body_lg_size),
    }

    height, padding, font_size = size_map[size]

    return f"""
    <button style="
        background: {bg};
        color: {fg};
        border: none;
        border-radius: {RADIUS.md};
        padding: {padding};
        font-size: {font_size};
        font-weight: 500;
        cursor: pointer;
        height: {height};
        display: inline-flex;
        align-items: center;
        gap: {SPACING.space_2};
        transition: all 0.2s ease;
        box-shadow: {ELEVATION.level_1};
    ">
        {f'<span>{icon}</span>' if icon else ''}
        <span>{label}</span>
    </button>
    """


# ============================================================================
# COMPONENT: DIVIDER
# ============================================================================


def divider(
    text: Optional[str] = None,
    margin: str = "md",
) -> None:
    """
    Display a horizontal divider with optional text.

    Args:
        text: Optional text in center of divider
        margin: Margin size (sm, md, lg)

    Example:
        >>> divider("OR")
    """
    margin_map = {
        "sm": SPACING.space_4,
        "md": SPACING.space_6,
        "lg": SPACING.space_8,
    }

    margin_val = margin_map[margin]

    if text:
        divider_html = f"""
        <div style="
            display: flex;
            align-items: center;
            margin: {margin_val} 0;
            gap: {SPACING.space_4};
        ">
            <div style="flex: 1; height: 1px; background: {COLORS.gray_200};"></div>
            <div style="color: {COLORS.gray_500}; font-size: {TYPOGRAPHY.body_sm_size}; font-weight: 500;">{text}</div>
            <div style="flex: 1; height: 1px; background: {COLORS.gray_200};"></div>
        </div>
        """
    else:
        divider_html = f"""
        <div style="
            height: 1px;
            background: {COLORS.gray_200};
            margin: {margin_val} 0;
        "></div>
        """

    st.markdown(divider_html, unsafe_allow_html=True)


# ============================================================================
# EXPORT PUBLIC API
# ============================================================================

__all__ = [
    "inject_custom_css",
    "styled_card",
    "status_badge",
    "metric_card",
    "alert_box",
    "progress_bar",
    "styled_table",
    "collapsible_section",
    "icon_button_html",
    "divider",
]
