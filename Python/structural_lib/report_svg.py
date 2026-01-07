# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""SVG helpers for report visuals (stdlib only).

Design constraints:
- Deterministic output (fixed viewBox, stable float formatting)
- No external dependencies
- Resilient to missing fields (render a simple placeholder)
"""

from __future__ import annotations

from typing import Any
from xml.etree import (
    ElementTree,  # nosec B405  # SVG generation, not parsing untrusted XML
)

from .data_types import BeamGeometry


def _fmt(value: float, decimals: int = 1) -> str:
    return f"{value:.{decimals}f}"


def _safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _render_error_svg(message: str, *, width: int, height: int) -> str:
    root = ElementTree.Element(
        "svg",
        attrib={
            "xmlns": "http://www.w3.org/2000/svg",
            "viewBox": f"0 0 {width} {height}",
            "width": str(width),
            "height": str(height),
            "role": "img",
            "aria-label": "Beam section (invalid input)",
        },
    )
    rect = ElementTree.SubElement(
        root,
        "rect",
        attrib={
            "x": "10",
            "y": "10",
            "width": str(width - 20),
            "height": str(height - 20),
            "fill": "#fff",
            "stroke": "#cc0000",
            "stroke-width": "2",
        },
    )
    rect.set("data-note", "error-frame")
    text = ElementTree.SubElement(
        root,
        "text",
        attrib={
            "x": str(width / 2),
            "y": str(height / 2),
            "text-anchor": "middle",
            "font-size": "12",
            "fill": "#cc0000",
        },
    )
    text.text = message
    return ElementTree.tostring(root, encoding="unicode")


def render_section_svg(
    *,
    b_mm: float,
    D_mm: float,
    d_mm: float | None = None,
    d_dash_mm: float | None = None,
    width: int = 300,
    height: int = 400,
) -> str:
    """Render a simple rectangular beam cross-section as SVG.

    Args:
        b_mm: Beam width (mm)
        D_mm: Overall depth (mm)
        d_mm: Effective depth (mm), optional
        d_dash_mm: Compression cover (mm), optional
        width: SVG width in pixels
        height: SVG height in pixels

    Returns:
        SVG markup string.
    """
    if b_mm <= 0 or D_mm <= 0:
        return _render_error_svg("Invalid beam geometry", width=width, height=height)

    margin = 20.0
    usable_w = max(width - 2 * margin, 1.0)
    usable_h = max(height - 2 * margin, 1.0)
    scale = min(usable_w / b_mm, usable_h / D_mm)

    section_w = b_mm * scale
    section_h = D_mm * scale
    x0 = (width - section_w) / 2.0
    y0 = (height - section_h) / 2.0

    bar_r = _clamp(min(section_w, section_h) * 0.03, 2.0, 6.0)
    top_y = y0 + d_dash_mm * scale if d_dash_mm is not None else y0 + 0.15 * section_h
    bot_y = y0 + d_mm * scale if d_mm is not None else y0 + 0.85 * section_h

    top_y = _clamp(top_y, y0 + bar_r, y0 + section_h - bar_r)
    bot_y = _clamp(bot_y, y0 + bar_r, y0 + section_h - bar_r)

    x_left = x0 + 0.25 * section_w
    x_right = x0 + 0.75 * section_w

    root = ElementTree.Element(
        "svg",
        attrib={
            "xmlns": "http://www.w3.org/2000/svg",
            "viewBox": f"0 0 {width} {height}",
            "width": str(width),
            "height": str(height),
            "role": "img",
            "aria-label": "Beam cross-section",
        },
    )

    ElementTree.SubElement(
        root,
        "rect",
        attrib={
            "x": _fmt(x0),
            "y": _fmt(y0),
            "width": _fmt(section_w),
            "height": _fmt(section_h),
            "fill": "#ffffff",
            "stroke": "#222222",
            "stroke-width": "2",
        },
    )

    # Compression steel (top)
    for x in (x_left, x_right):
        ElementTree.SubElement(
            root,
            "circle",
            attrib={
                "cx": _fmt(x),
                "cy": _fmt(top_y),
                "r": _fmt(bar_r),
                "fill": "#444444",
            },
        )

    # Tension steel (bottom)
    for x in (x_left, x_right):
        ElementTree.SubElement(
            root,
            "circle",
            attrib={
                "cx": _fmt(x),
                "cy": _fmt(bot_y),
                "r": _fmt(bar_r),
                "fill": "#444444",
            },
        )

    # Depth markers (d and d')
    if d_dash_mm is not None:
        ElementTree.SubElement(
            root,
            "line",
            attrib={
                "x1": _fmt(x0),
                "x2": _fmt(x0 + section_w),
                "y1": _fmt(top_y),
                "y2": _fmt(top_y),
                "stroke": "#888888",
                "stroke-width": "1",
                "stroke-dasharray": "4,3",
            },
        )
        label = ElementTree.SubElement(
            root,
            "text",
            attrib={
                "x": _fmt(x0 + section_w + 6),
                "y": _fmt(top_y + 4),
                "font-size": "10",
                "fill": "#666666",
            },
        )
        label.text = "d'"

    if d_mm is not None:
        ElementTree.SubElement(
            root,
            "line",
            attrib={
                "x1": _fmt(x0),
                "x2": _fmt(x0 + section_w),
                "y1": _fmt(bot_y),
                "y2": _fmt(bot_y),
                "stroke": "#888888",
                "stroke-width": "1",
                "stroke-dasharray": "4,3",
            },
        )
        label = ElementTree.SubElement(
            root,
            "text",
            attrib={
                "x": _fmt(x0 + section_w + 6),
                "y": _fmt(bot_y + 4),
                "font-size": "10",
                "fill": "#666666",
            },
        )
        label.text = "d"

    # Dimension labels
    label_b = ElementTree.SubElement(
        root,
        "text",
        attrib={
            "x": _fmt(width / 2.0),
            "y": _fmt(y0 + section_h + 16),
            "text-anchor": "middle",
            "font-size": "11",
            "fill": "#333333",
        },
    )
    label_b.text = f"b = {b_mm:.0f} mm"

    label_D = ElementTree.SubElement(
        root,
        "text",
        attrib={
            "x": _fmt(x0 + section_w + 6),
            "y": _fmt(y0 + section_h / 2.0),
            "font-size": "11",
            "fill": "#333333",
        },
    )
    label_D.text = f"D = {D_mm:.0f} mm"

    return ElementTree.tostring(root, encoding="unicode")


def render_section_svg_from_beam(
    beam: BeamGeometry,
    *,
    width: int = 300,
    height: int = 400,
) -> str:
    """Render SVG from a beam dict (job spec fields)."""
    b_mm = _safe_float(beam.get("b_mm"))
    D_mm = _safe_float(beam.get("D_mm"))
    d_mm = _safe_float(beam.get("d_mm"))
    d_dash_mm = _safe_float(beam.get("d_dash_mm"))

    if b_mm is None or D_mm is None:
        return _render_error_svg("Missing b_mm or D_mm", width=width, height=height)

    return render_section_svg(
        b_mm=b_mm,
        D_mm=D_mm,
        d_mm=d_mm,
        d_dash_mm=d_dash_mm,
        width=width,
        height=height,
    )
