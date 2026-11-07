# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       calculation_report
Description:  Professional calculation report generation (TASK-277)

Generates engineering calculation sheets that can be used for:
- Design documentation and records
- Client deliverables
- Engineering review submissions
- Audit trail documentation

Provides:
- HTML report generation (styled, printable)
- JSON report generation (machine-readable)
- Markdown report generation (portable)
- Integration with audit trail

Example:
    >>> from structural_lib.calculation_report import CalculationReport
    >>> from structural_lib import api
    >>>
    >>> result = api.design_and_detail_beam_is456(...)
    >>> report = CalculationReport.from_design_result(result, project_info={...})
    >>> report.export_html("report.html")
"""

from __future__ import annotations

import html
import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from structural_lib.services._report_projection import (
    project_beam_report,
    report_evidence_html,
    report_evidence_markdown,
)

_logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Report Data Structures
# -----------------------------------------------------------------------------


@dataclass
class ProjectInfo:
    """Project and engineer information for reports.

    Attributes:
        project_name: Name of the project
        project_number: Project reference number
        client_name: Client name
        engineer_name: Designing engineer's name
        checker_name: Checker/reviewer's name
        revision: Revision number/letter
        date: Report date (auto-set to current if not provided)
    """

    project_name: str = "Untitled Project"
    project_number: str = ""
    client_name: str = ""
    engineer_name: str = ""
    checker_name: str = ""
    revision: str = "A"
    date: str = ""

    def __post_init__(self) -> None:
        if not self.date:
            self.date = datetime.now(UTC).strftime("%Y-%m-%d")


@dataclass
class InputSection:
    """Input parameters section of the report.

    Attributes:
        geometry: Beam geometry parameters
        materials: Material properties
        loads: Load case information
        detailing: Detailing configuration
    """

    geometry: dict[str, Any] = field(default_factory=dict)
    materials: dict[str, Any] = field(default_factory=dict)
    loads: list[dict[str, Any]] = field(default_factory=list)
    detailing: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResultSection:
    """Calculation results section of the report.

    Attributes:
        flexure: Flexure design results
        shear: Shear design results
        serviceability: Serviceability check results
        detailing: Detailing output
        summary: Overall summary
    """

    flexure: dict[str, Any] = field(default_factory=dict)
    shear: dict[str, Any] = field(default_factory=dict)
    serviceability: dict[str, Any] = field(default_factory=dict)
    detailing: dict[str, Any] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)
    torsion: dict[str, Any] = field(default_factory=dict)


@dataclass
class CalculationReport:
    """Professional calculation report container.

    Combines project info, inputs, results, and references into a
    complete engineering calculation sheet.

    Attributes:
        report_id: Unique report identifier
        project_info: Project and engineer information
        beam_id: Beam identifier
        story: Story/floor identifier
        inputs: Input parameters section
        results: Calculation results section
        code_references: List of code clause references
        notes: Additional notes and assumptions
        verification_hash: Optional hash for audit trail
        generated_at: Report generation timestamp
    """

    report_id: str
    project_info: ProjectInfo
    beam_id: str
    story: str
    inputs: InputSection
    results: ResultSection
    code_references: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    verification_hash: str = ""
    generated_at: str = ""
    source: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.generated_at:
            self.generated_at = datetime.now(UTC).isoformat()

    @classmethod
    def from_design_result(
        cls,
        result: Any,
        beam_id: str = "B1",
        story: str = "GF",
        project_info: dict[str, Any] | None = None,
    ) -> CalculationReport:
        """Create report from a design result.

        Args:
            result: Canonical BeamDesignResultV1/BeamDesignAndDetailResultV1,
                legacy DesignAndDetailResult, or design-only ComplianceCaseResult.
            beam_id: Beam identifier
            story: Story/floor identifier
            project_info: Optional project information dict

        Returns:
            CalculationReport instance
        """
        proj = ProjectInfo(**(project_info or {}))

        # Generate unique report ID
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        report_id = f"CALC-{beam_id}-{story}-{timestamp}"

        projection = project_beam_report(result)
        inputs = InputSection(**projection["inputs"])
        results_section = ResultSection(**projection["results"])
        identity = projection["source"]["identity"]
        if beam_id == "B1":
            beam_id = identity.get("member_id", beam_id)
        if story == "GF":
            story = identity.get("story", story)
        report_id = f"CALC-{beam_id}-{story}-{timestamp}"

        return cls(
            report_id=report_id,
            project_info=proj,
            beam_id=beam_id,
            story=story,
            inputs=inputs,
            results=results_section,
            source=projection["source"],
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize report to dictionary."""
        return {
            "report_id": self.report_id,
            "generated_at": self.generated_at,
            "project_info": {
                "project_name": self.project_info.project_name,
                "project_number": self.project_info.project_number,
                "client_name": self.project_info.client_name,
                "engineer_name": self.project_info.engineer_name,
                "checker_name": self.project_info.checker_name,
                "revision": self.project_info.revision,
                "date": self.project_info.date,
            },
            "beam_id": self.beam_id,
            "story": self.story,
            "inputs": {
                "geometry": self.inputs.geometry,
                "materials": self.inputs.materials,
                "loads": self.inputs.loads,
                "detailing": self.inputs.detailing,
            },
            "results": {
                "flexure": self.results.flexure,
                "shear": self.results.shear,
                "serviceability": self.results.serviceability,
                "detailing": self.results.detailing,
                "summary": self.results.summary,
                "torsion": self.results.torsion,
            },
            "source": self.source,
            "result_envelope": self.source.get("envelope", {}),
            "code_references": self.code_references,
            "notes": self.notes,
            "verification_hash": self.verification_hash,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string.

        Args:
            indent: JSON indentation level

        Returns:
            JSON string
        """
        return json.dumps(self.to_dict(), indent=indent)

    def export_json(self, path: str | Path) -> Path:
        """Export report to JSON file.

        Args:
            path: Output file path

        Returns:
            Path to created file
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())

        _logger.info(f"JSON report exported to {path}")
        return path

    def export_html(self, path: str | Path) -> Path:
        """Export report to HTML file.

        Args:
            path: Output file path

        Returns:
            Path to created file
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        html_content = self._generate_html()
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)

        _logger.info(f"HTML report exported to {path}")
        return path

    def export_markdown(self, path: str | Path) -> Path:
        """Export report to Markdown file.

        Args:
            path: Output file path

        Returns:
            Path to created file
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        md_content = self._generate_markdown()
        with open(path, "w", encoding="utf-8") as f:
            f.write(md_content)

        _logger.info(f"Markdown report exported to {path}")
        return path

    def _generate_html(self) -> str:
        """Generate HTML report content."""
        proj = self.project_info
        inputs = self.inputs
        results = self.results

        # Escape helper
        def e(val: Any) -> str:
            return html.escape(str(val))

        classification_label, classification, required = _flexure_display(
            results.flexure
        )
        detail_notice, detail_rows = _detailing_display(results.detailing)
        if detail_notice or detail_rows:
            provided_row = ""
            schedule = "<h3>Provided longitudinal steel</h3>" + (
                f"<p>{e(detail_notice)}</p>" if detail_notice else ""
            )
            if detail_rows:
                headers = "".join(f"<th>{e(h)}</th>" for h in _BAR_COLUMNS)
                rows = "".join(
                    "<tr>" + "".join(f"<td>{e(cell)}</td>" for cell in row) + "</tr>"
                    for row in detail_rows
                )
                schedule += (
                    f'<table class="data-table"><tr>{headers}</tr>{rows}</table>'
                )
        else:
            provided = _format_number(results.flexure.get("ast_provided"))
            provided_row = (
                f'<tr><td>A<sub>st</sub> Provided</td><td class="number">{e(provided)}</td>'
                "<td>mm²</td></tr>"
            )
            schedule = ""

        # Status class
        raw_shear_status = results.shear.get("is_safe")
        shear_status = raw_shear_status if type(raw_shear_status) is bool else None
        raw_is_ok = results.summary.get("is_ok")
        is_ok = raw_is_ok if type(raw_is_ok) is bool else None
        if shear_status is False:
            is_ok = False
        elif shear_status is None:
            is_ok = None
        status_class = "status-pass" if is_ok is True else "status-fail"
        status_text = (
            "PASS"
            if is_ok is True
            else ("FAIL" if is_ok is False else _unevaluated_status(results.summary))
        )
        shear_status_class = "status-pass" if shear_status is True else "status-fail"
        shear_status_text = (
            "PASS"
            if shear_status is True
            else "FAIL" if shear_status is False else "NOT EVALUATED"
        )

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculation Report - {e(self.beam_id)}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0; padding: 20px; font-size: 14px; line-height: 1.5;
        }}
        .header {{
            border-bottom: 2px solid #333;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        .header-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }}
        .project-info h1 {{ margin: 0 0 10px; font-size: 24px; }}
        .project-info p {{ margin: 5px 0; color: #555; }}
        .meta-box {{
            border: 1px solid #ddd;
            padding: 10px;
            font-size: 12px;
        }}
        .meta-box table {{ width: 100%; }}
        .meta-box td {{ padding: 3px 5px; }}
        .meta-box td:first-child {{ font-weight: 600; width: 40%; }}
        .section {{
            margin: 20px 0;
            padding: 15px;
            background: #fafafa;
            border: 1px solid #eee;
            border-radius: 4px;
        }}
        .section h2 {{
            margin: 0 0 15px;
            font-size: 16px;
            color: #333;
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
        }}
        table.data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}
        .data-table th, .data-table td {{
            border: 1px solid #ddd;
            padding: 8px 12px;
            text-align: left;
        }}
        .data-table th {{ background: #f5f5f5; font-weight: 600; }}
        .data-table .number {{ text-align: right; font-family: monospace; }}
        .status-pass {{ color: #1b5e20; font-weight: 700; }}
        .status-fail {{ color: #b71c1c; font-weight: 700; }}
        .summary-box {{
            background: #f0f8ff;
            border: 2px solid #333;
            padding: 15px;
            margin: 20px 0;
            text-align: center;
        }}
        .summary-box h3 {{ margin: 0 0 10px; }}
        .footer {{
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #ddd;
            font-size: 12px;
            color: #666;
        }}
        @media print {{
            .section {{ page-break-inside: avoid; }}
            body {{ padding: 0; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-grid">
            <div class="project-info">
                <h1>{e(proj.project_name)}</h1>
                <p><strong>Beam:</strong> {e(self.beam_id)} @ {e(self.story)}</p>
                <p><strong>Code:</strong> IS 456:2000</p>
            </div>
            <div class="meta-box">
                <table>
                    <tr><td>Project No:</td><td>{e(proj.project_number)}</td></tr>
                    <tr><td>Client:</td><td>{e(proj.client_name)}</td></tr>
                    <tr><td>Engineer:</td><td>{e(proj.engineer_name)}</td></tr>
                    <tr><td>Checker:</td><td>{e(proj.checker_name)}</td></tr>
                    <tr><td>Revision:</td><td>{e(proj.revision)}</td></tr>
                    <tr><td>Date:</td><td>{e(proj.date)}</td></tr>
                </table>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>1. Input Data</h2>
        <h3>1.1 Geometry</h3>
        <table class="data-table">
            <tr><th>Parameter</th><th>Value</th><th>Units</th></tr>
            <tr><td>Beam Width (b)</td><td class="number">{
            inputs.geometry.get("b_mm", "N/A")
        }</td><td>mm</td></tr>
            <tr><td>Overall Depth (D)</td><td class="number">{
            inputs.geometry.get("D_mm", "N/A")
        }</td><td>mm</td></tr>
            <tr><td>Effective Depth (d)</td><td class="number">{
            inputs.geometry.get("d_mm", "N/A")
        }</td><td>mm</td></tr>
            <tr><td>Span (as supplied)</td><td class="number">{
            inputs.geometry.get("span_mm", "N/A")
        }</td><td>mm</td></tr>
            <tr><td>Clear Cover</td><td class="number">{
            inputs.geometry.get("cover_mm", "N/A")
        }</td><td>mm</td></tr>
        </table>

        <h3>1.2 Materials</h3>
        <table class="data-table">
            <tr><th>Parameter</th><th>Value</th><th>Units</th></tr>
            <tr><td>Concrete Grade (f<sub>ck</sub>)</td><td class="number">{
            inputs.materials.get("fck_nmm2", "N/A")
        }</td><td>N/mm²</td></tr>
            <tr><td>Steel Grade (f<sub>y</sub>)</td><td class="number">{
            inputs.materials.get("fy_nmm2", "N/A")
        }</td><td>N/mm²</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>2. Design Results</h2>
        <h3>2.1 Flexure Design</h3>
        <table class="data-table">
            <tr><th>Parameter</th><th>Value</th><th>Units</th></tr>
            <tr><td>{e(classification_label)}</td><td>{
            e(classification)
        }</td><td>-</td></tr>
            <tr><td>Required tension steel</td><td class="number">{
            e(required)
        }</td><td>mm²</td></tr>
            {provided_row}
        </table>
        {schedule}

        <h3>2.2 Shear Design</h3>
        <table class="data-table">
            <tr><th>Parameter</th><th>Value</th><th>Units</th></tr>
            <tr><td>V<sub>u</sub> (Factored Shear)</td><td class="number">{
            _format_number(results.shear.get("Vu_kn"))
        }</td><td>kN</td></tr>
            <tr><td>&tau;<sub>v</sub> (Nominal Shear Stress)</td><td class="number">{
            _format_number(results.shear.get("tau_v"))
        }</td><td>N/mm²</td></tr>
            <tr><td>&tau;<sub>c</sub> (Concrete Shear Strength)</td><td class="number">{
            _format_number(results.shear.get("tau_c"))
        }</td><td>N/mm²</td></tr>
            <tr><td>&tau;<sub>c,max</sub> (Max Shear Stress)</td><td class="number">{
            _format_number(results.shear.get("tau_c_max"))
        }</td><td>N/mm²</td></tr>
            <tr><td>V<sub>us</sub> (Stirrup Capacity)</td><td class="number">{
            _format_number(results.shear.get("Vus"))
        }</td><td>kN</td></tr>
            <tr><td>Stirrup Spacing</td><td class="number">{
            _format_number(results.shear.get("spacing"))
        }</td><td>mm</td></tr>
            <tr><td>Shear Check</td><td class="{shear_status_class}">{
            shear_status_text
        }</td><td>-</td></tr>
        </table>
    </div>

    <div class="summary-box">
        <h3>DESIGN STATUS: <span class="{status_class}">{status_text}</span></h3>
        <p>{e(results.summary.get("summary", ""))}</p>
        <p>Failed checks: {e(", ".join(results.summary.get("failed_checks", [])) or "None recorded")}</p>
        <p>Review status: {e(self.source.get("envelope", {}).get("review_status", "Unavailable"))}</p>
    </div>

    <div class="footer">
        <p><strong>Report ID:</strong> {e(self.report_id)}</p>
        <p><strong>Generated:</strong> {e(self.generated_at)}</p>
        {
            f"<p><strong>Verification Hash:</strong> {e(self.verification_hash[:32])}...</p>"
            if self.verification_hash
            else ""
        }
        <p><em>Generated by structural-lib-is456</em></p>
    </div>
</body>
</html>"""
        if self.source:
            evidence = report_evidence_html(self.to_dict())
            html_content = html_content.replace(
                '<div class="footer">', evidence + '<div class="footer">'
            )
        return html_content

    def _generate_markdown(self) -> str:
        """Generate Markdown report content."""
        proj = self.project_info
        inputs = self.inputs
        results = self.results

        classification_label, classification, required = _flexure_display(
            results.flexure
        )
        detail_notice, detail_rows = _detailing_display(results.detailing)
        if detail_notice or detail_rows:
            schedule_lines = ["", "#### Provided longitudinal steel", ""]
            if detail_notice:
                schedule_lines.extend((detail_notice, ""))
            if detail_rows:
                schedule_lines.append("| " + " | ".join(_BAR_COLUMNS) + " |")
                schedule_lines.append(
                    "| " + " | ".join(["---"] * len(_BAR_COLUMNS)) + " |"
                )
                schedule_lines.extend(
                    "| " + " | ".join(row) + " |" for row in detail_rows
                )
            provided = "\n".join(schedule_lines)
        else:
            area = _format_number(results.flexure.get("ast_provided"))
            provided = f"| Ast Provided | {area} | mm² |"

        raw_is_ok = results.summary.get("is_ok")
        is_ok = raw_is_ok if type(raw_is_ok) is bool else None
        raw_shear_status = results.shear.get("is_safe")
        shear_status = raw_shear_status if type(raw_shear_status) is bool else None
        if shear_status is False:
            is_ok = False
        elif shear_status is None:
            is_ok = None
        status = (
            "✅ PASS"
            if is_ok is True
            else (
                "❌ FAIL"
                if is_ok is False
                else "⚠️ " + _unevaluated_status(results.summary)
            )
        )

        md = f"""# Calculation Report: {self.beam_id} @ {self.story}

**Project:** {proj.project_name}
**Project No:** {proj.project_number}
**Client:** {proj.client_name}
**Code:** IS 456:2000

| Info | Value |
|------|-------|
| Engineer | {proj.engineer_name} |
| Checker | {proj.checker_name} |
| Revision | {proj.revision} |
| Date | {proj.date} |

---

## 1. Input Data

### 1.1 Geometry

| Parameter | Value | Units |
|-----------|-------|-------|
| Beam Width (b) | {inputs.geometry.get("b_mm", "N/A")} | mm |
| Overall Depth (D) | {inputs.geometry.get("D_mm", "N/A")} | mm |
| Effective Depth (d) | {inputs.geometry.get("d_mm", "N/A")} | mm |
| Span (as supplied) | {inputs.geometry.get("span_mm", "N/A")} | mm |
| Clear Cover | {inputs.geometry.get("cover_mm", "N/A")} | mm |

### 1.2 Materials

| Parameter | Value | Units |
|-----------|-------|-------|
| Concrete Grade (fck) | {inputs.materials.get("fck_nmm2", "N/A")} | N/mm² |
| Steel Grade (fy) | {inputs.materials.get("fy_nmm2", "N/A")} | N/mm² |

---

## 2. Design Results

### 2.1 Flexure Design

| Parameter | Value | Units |
|-----------|-------|-------|
| {classification_label} | {classification} | - |
| Required tension steel | {required} | mm² |
{provided}

### 2.2 Shear Design

| Parameter | Value | Units |
|-----------|-------|-------|
| Vu (Factored Shear) | {_format_number(results.shear.get("Vu_kn"))} | kN |
| τv (Nominal Shear Stress) | {_format_number(results.shear.get("tau_v"))} | N/mm² |
| τc (Concrete Shear Strength) | {_format_number(results.shear.get("tau_c"))} | N/mm² |
| τc,max (Max Shear Stress) | {_format_number(results.shear.get("tau_c_max"))} | N/mm² |
| Vus (Stirrup Capacity) | {_format_number(results.shear.get("Vus"))} | kN |
| Stirrup Spacing | {_format_number(results.shear.get("spacing"))} | mm |

---

## 3. Summary

**Design Status:** {status}

**Failed checks:** {", ".join(results.summary.get("failed_checks", [])) or "None recorded"}
**Review status:** {self.source.get("envelope", {}).get("review_status", "Unavailable")}

{results.summary.get("summary", "")}

---

**Report ID:** {self.report_id}
**Generated:** {self.generated_at}
{f"**Verification Hash:** {self.verification_hash[:32]}..." if self.verification_hash else ""}

*Generated by structural-lib-is456*
"""
        if self.source:
            md += report_evidence_markdown(self.to_dict())
        return md


_BAR_COLUMNS = (
    "Face",
    "Zone",
    "Count",
    "Diameter (mm)",
    "Area provided (mm²)",
    "Spacing (mm)",
    "Layers",
)


def _unevaluated_status(summary: dict[str, Any]) -> str:
    """Preserve HOLD while never promoting an unavailable required check."""
    status = summary.get("engineering_status")
    return status if status in {"HOLD", "NOT_EVALUATED"} else "NOT EVALUATED"


def _flexure_values(flexure: Any) -> dict[str, Any]:
    section_type = getattr(flexure, "section_type", None)
    return {
        "ast_required": flexure.Ast_required,
        "ast_provided": None,
        "section_type": getattr(section_type, "name", None),
        "is_safe": getattr(flexure, "is_safe", None),
    }


def _flexure_display(flexure: dict[str, Any]) -> tuple[str, str, str]:
    section_type = flexure.get("section_type")
    label = "Section classification" if section_type else "Beam Type"
    classification = section_type or flexure.get("beam_type") or "N/A"
    area = flexure.get("ast_required")
    required = _format_number(area)
    if area == 0 and flexure.get("is_safe") is False:
        required = "N/A (flexure check failed)"
    return label, classification, required


def _detailing_display(
    detail: dict[str, Any],
) -> tuple[str, list[tuple[str, ...]]]:
    if detail.get("status") == "unavailable":
        reason = {
            "design_only": "This result contains design checks only.",
            "missing_detailing": "The combined result has no detailing record.",
            "no_bar_rows": "The detailing record contains no longitudinal bar rows.",
        }.get(detail.get("reason", ""), "")
        notice = f"Bar layout unavailable. {reason}".strip()
        if detail.get("is_valid") is False:
            notice += " Recorded detailing is invalid."
        return notice, []
    if detail.get("status") != "available":
        return "", []

    rows: list[tuple[str, ...]] = []
    missing: list[str] = []
    for face in ("Top", "Bottom"):
        bars = detail[f"{face.lower()}_bars"]
        zones = {bar["zone"] for bar in bars}
        missing.extend(
            f"{face} {zone}" for zone in ("start", "mid", "end") if zone not in zones
        )
        rows.extend(
            (
                face,
                bar["zone"],
                _format_number(bar["count"]),
                _format_number(bar["diameter_mm"]),
                _format_number(bar["area_provided_mm2"]),
                _format_number(bar["spacing_mm"]),
                _format_number(bar["layers"]),
            )
            for bar in bars
        )
    notice = "Recorded detailing is invalid." if detail.get("is_valid") is False else ""
    if missing:
        notice = f"{notice} Bar rows unavailable for {', '.join(missing)}.".strip()
    return notice, rows


def _format_number(value: Any) -> str:
    """Format a number for display."""
    if value is None:
        return "N/A"
    try:
        num = float(value)
        if num == int(num):
            return str(int(num))
        return f"{num:.2f}"
    except (TypeError, ValueError):
        return str(value)


# -----------------------------------------------------------------------------
# Convenience Functions
# -----------------------------------------------------------------------------


def generate_calculation_report(
    result: Any,
    beam_id: str = "B1",
    story: str = "GF",
    project_info: dict[str, Any] | None = None,
    output_path: str | Path | None = None,
    output_format: str = "html",
) -> CalculationReport:
    """Generate a calculation report from design result.

    Args:
        result: Canonical beam design/combined result, legacy DesignAndDetailResult,
            or design-only ComplianceCaseResult. Known inputs, actual detailing,
            evaluated checks and review requirements are retained in every format.
        beam_id: Beam identifier
        story: Story/floor identifier
        project_info: Optional project information
        output_path: Optional path to export report
        output_format: Export format ("html", "json", "markdown")

    Returns:
        CalculationReport instance

    Example:
        >>> result = api.design_and_detail_beam_is456(...)
        >>> report = generate_calculation_report(
        ...     result,
        ...     beam_id="B1",
        ...     project_info={"project_name": "Tower A"},
        ...     output_path="reports/B1.html",
        ... )
    """
    report = CalculationReport.from_design_result(
        result=result,
        beam_id=beam_id,
        story=story,
        project_info=project_info,
    )

    if output_path:
        path = Path(output_path)
        if output_format == "html":
            report.export_html(path)
        elif output_format == "json":
            report.export_json(path)
        elif output_format == "markdown":
            report.export_markdown(path)
        else:
            raise ValueError(f"Unknown format: {output_format}")

    return report
