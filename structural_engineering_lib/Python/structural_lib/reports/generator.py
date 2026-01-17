# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Report Generator — Jinja2-based HTML report generation.

This module provides the core report generation logic using Jinja2 templates.
It gracefully handles the case where Jinja2 is not installed.

TASK-522: Jinja2 report templates
"""

from __future__ import annotations

import html
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

_logger = logging.getLogger(__name__)

# Check for Jinja2 availability
try:
    from jinja2 import Environment, PackageLoader, select_autoescape

    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    if TYPE_CHECKING:
        from jinja2 import Environment, PackageLoader, select_autoescape


__all__ = [
    "JINJA2_AVAILABLE",
    "ReportContext",
    "generate_html_report",
    "generate_html_report_from_dict",
    "get_available_templates",
]


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class ReportContext:
    """Context data for report generation.

    This dataclass holds all the information needed to render a report template.

    Attributes:
        beam_id: Unique identifier for the beam.
        project_name: Name of the project.
        project_number: Project reference number.
        client_name: Client name.
        engineer_name: Designing engineer's name.
        checker_name: Checker/reviewer's name.
        revision: Revision number/letter.
        date: Report date.
        inputs: Input parameters (geometry, materials, loads).
        results: Calculation results.
        is_ok: Overall pass/fail status.
        code_reference: Code standard used (e.g., "IS 456:2000").
        software_version: Software version string.
    """

    beam_id: str = "B1"
    project_name: str = "Untitled Project"
    project_number: str = ""
    client_name: str = ""
    engineer_name: str = ""
    checker_name: str = ""
    revision: str = "A"
    date: str = ""
    inputs: dict[str, Any] = field(default_factory=dict)
    results: dict[str, Any] = field(default_factory=dict)
    is_ok: bool = False
    code_reference: str = "IS 456:2000"
    software_version: str = ""

    def __post_init__(self) -> None:
        if not self.date:
            self.date = datetime.now(UTC).strftime("%Y-%m-%d")

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary for template rendering."""
        return {
            "beam_id": self.beam_id,
            "project_name": self.project_name,
            "project_number": self.project_number,
            "client_name": self.client_name,
            "engineer_name": self.engineer_name,
            "checker_name": self.checker_name,
            "revision": self.revision,
            "date": self.date,
            "inputs": self.inputs,
            "results": self.results,
            "is_ok": self.is_ok,
            "status_text": "PASS" if self.is_ok else "FAIL",
            "status_class": "status-pass" if self.is_ok else "status-fail",
            "code_reference": self.code_reference,
            "software_version": self.software_version,
        }


# =============================================================================
# Template Registry
# =============================================================================

TEMPLATES_DIR = Path(__file__).parent / "templates"

TEMPLATE_REGISTRY: dict[str, str] = {
    "beam_design": "beam_design_report.html.j2",
    "summary": "summary_report.html.j2",
    "detailed": "detailed_report.html.j2",
}


def get_available_templates() -> list[str]:
    """Return list of available template names.

    Returns:
        List of template names that can be used with generate_html_report().

    Example:
        >>> templates = get_available_templates()
        >>> print(templates)
        ['beam_design', 'summary', 'detailed']
    """
    return list(TEMPLATE_REGISTRY.keys())


# =============================================================================
# Report Generation Functions
# =============================================================================


def generate_html_report(
    design_result: Any,
    template: str = "beam_design",
    project_info: dict[str, Any] | None = None,
    beam_id: str = "B1",
) -> str:
    """Generate HTML report from a design result object.

    This function takes a design result (from api.design_and_detail_beam_is456
    or similar) and generates a professional HTML report using Jinja2 templates.

    Args:
        design_result: Design result object or dictionary.
        template: Template name (see get_available_templates()).
        project_info: Optional project information dictionary with keys:
            project_name, project_number, client_name, engineer_name, etc.
        beam_id: Beam identifier for the report.

    Returns:
        HTML string of the rendered report.

    Raises:
        ImportError: If Jinja2 is not installed.
        ValueError: If template name is not recognized.

    Example:
        >>> from structural_lib import api
        >>> from structural_lib.reports import generate_html_report
        >>>
        >>> result = api.design_and_detail_beam_is456(...)
        >>> html = generate_html_report(result, template="beam_design")
        >>> with open("report.html", "w") as f:
        ...     f.write(html)
    """
    if not JINJA2_AVAILABLE:
        raise ImportError(
            "Jinja2 is required for report generation. "
            "Install with: pip install structural-lib-is456[report]"
        )

    # Convert design result to dictionary if needed
    if hasattr(design_result, "to_dict"):
        result_dict = design_result.to_dict()
    elif hasattr(design_result, "__dict__"):
        result_dict = vars(design_result)
    elif isinstance(design_result, dict):
        result_dict = design_result
    else:
        result_dict = {"data": design_result}

    # Build context
    proj = project_info or {}
    context = ReportContext(
        beam_id=beam_id,
        project_name=proj.get("project_name", "Untitled Project"),
        project_number=proj.get("project_number", ""),
        client_name=proj.get("client_name", ""),
        engineer_name=proj.get("engineer_name", ""),
        checker_name=proj.get("checker_name", ""),
        revision=proj.get("revision", "A"),
        date=proj.get("date", ""),
        inputs=result_dict.get("inputs", {}),
        results=result_dict.get("results", result_dict),
        is_ok=result_dict.get(
            "is_ok", result_dict.get("results", {}).get("is_ok", False)
        ),
        software_version=proj.get("software_version", ""),
    )

    return generate_html_report_from_dict(context.to_dict(), template=template)


def generate_html_report_from_dict(
    context: dict[str, Any],
    template: str = "beam_design",
) -> str:
    """Generate HTML report from a context dictionary.

    Lower-level function that renders a template directly from a dictionary.

    Args:
        context: Dictionary with template variables.
        template: Template name (see get_available_templates()).

    Returns:
        HTML string of the rendered report.

    Raises:
        ImportError: If Jinja2 is not installed.
        ValueError: If template name is not recognized.
    """
    if not JINJA2_AVAILABLE:
        raise ImportError(
            "Jinja2 is required for report generation. "
            "Install with: pip install structural-lib-is456[report]"
        )

    if template not in TEMPLATE_REGISTRY:
        available = ", ".join(TEMPLATE_REGISTRY.keys())
        raise ValueError(f"Unknown template '{template}'. Available: {available}")

    template_file = TEMPLATE_REGISTRY[template]

    # Create Jinja2 environment
    env = Environment(
        loader=PackageLoader("structural_lib.reports", "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )

    # Add custom filters
    env.filters["format_number"] = _format_number
    env.filters["format_mm"] = _format_mm
    env.filters["format_percent"] = _format_percent

    # Load and render template
    tmpl = env.get_template(template_file)
    rendered: str = tmpl.render(**context)
    return rendered


# =============================================================================
# Fallback HTML Generation (when Jinja2 not available)
# =============================================================================


def _generate_fallback_html(context: dict[str, Any]) -> str:
    """Generate basic HTML report without Jinja2.

    This is a minimal fallback for when Jinja2 is not installed.

    Args:
        context: Report context dictionary.

    Returns:
        Basic HTML string.
    """

    def e(val: Any) -> str:
        return html.escape(str(val))

    beam_id = e(context.get("beam_id", "B1"))
    project_name = e(context.get("project_name", ""))
    is_ok = context.get("is_ok", False)
    status = "PASS" if is_ok else "FAIL"
    status_color = "#28a745" if is_ok else "#dc3545"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Beam Design Report - {beam_id}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ border-bottom: 2px solid #333; padding-bottom: 10px; }}
        .status {{ color: {status_color}; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Beam Design Report: {beam_id}</h1>
        <p>Project: {project_name}</p>
        <p>Status: <span class="status">{status}</span></p>
    </div>
    <div class="content">
        <p><em>Note: Install Jinja2 for full report formatting:</em></p>
        <code>pip install structural-lib-is456[report]</code>
        <hr>
        <pre>{html.escape(str(context.get('results', {})))}</pre>
    </div>
</body>
</html>
"""


# =============================================================================
# Template Filters
# =============================================================================


def _format_number(value: Any, decimals: int = 2) -> str:
    """Format a number with specified decimal places."""
    if value is None:
        return "-"
    try:
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return str(value)


def _format_mm(value: Any, decimals: int = 0) -> str:
    """Format a value in millimeters."""
    if value is None:
        return "-"
    try:
        return f"{float(value):,.{decimals}f} mm"
    except (TypeError, ValueError):
        return str(value)


def _format_percent(value: Any, decimals: int = 2) -> str:
    """Format a value as percentage."""
    if value is None:
        return "-"
    try:
        return f"{float(value):.{decimals}f}%"
    except (TypeError, ValueError):
        return str(value)
