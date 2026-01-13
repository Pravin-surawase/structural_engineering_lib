# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Reports Package — Professional Report Generation with Jinja2

This package provides Jinja2-based templating for generating professional
engineering calculation reports from beam design results.

Features:
- HTML report generation with styled templates
- Support for custom templates
- CLI integration
- Graceful fallback when Jinja2 is not installed

Example:
    >>> from structural_lib.reports import generate_html_report
    >>> from structural_lib import api
    >>>
    >>> result = api.design_and_detail_beam_is456(...)
    >>> html = generate_html_report(result, template="beam_design")
    >>> with open("report.html", "w") as f:
    ...     f.write(html)

Installation:
    pip install structural-lib-is456[report]  # Includes jinja2

TASK-522: Jinja2 report templates
"""

from __future__ import annotations

from structural_lib.reports.generator import (
    JINJA2_AVAILABLE,
    ReportContext,
    generate_html_report,
    generate_html_report_from_dict,
    get_available_templates,
)

__all__ = [
    "generate_html_report",
    "generate_html_report_from_dict",
    "get_available_templates",
    "ReportContext",
    "JINJA2_AVAILABLE",
]
