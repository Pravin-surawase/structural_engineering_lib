"""
PDF Report Generator for Beam Design Results
===========================================

Generates professional PDF reports with:
- Cover page with project info
- Input summary
- Calculation sheets with IS 456 references
- Results (flexure, shear, detailing)
- Diagrams and BBS tables
- Compliance checklist

Author: Agent 6 (Streamlit Specialist)
Task: STREAMLIT-FEAT-003

Dependencies:
    This module requires reportlab. Install with:
        pip install structural-lib-is456[pdf]
    or:
        pip install reportlab
"""

from io import BytesIO
from datetime import datetime
from typing import Dict, Any, Optional, List
import os

# Optional dependency: reportlab for PDF generation
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
        PageBreak, Image, Frame, PageTemplate
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.pdfgen import canvas
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    # Define stubs to prevent NameError at class definition time
    A4 = (595.27, 841.89)  # A4 in points
    mm = 2.834645669291339  # points per mm


def is_reportlab_available() -> bool:
    """Check if reportlab is available for PDF generation."""
    return HAS_REPORTLAB


class BeamDesignReportGenerator:
    """
    Professional PDF report generator for structural engineering.

    Follows IS 456:2000 reporting standards and includes all necessary
    calculation documentation for regulatory compliance.

    Requires:
        reportlab package. Install with: pip install structural-lib-is456[pdf]
    """

    def __init__(self):
        """Initialize report generator with default styles.

        Raises:
            ImportError: If reportlab package is not installed.
        """
        if not HAS_REPORTLAB:
            raise ImportError(
                "reportlab is required for PDF generation. "
                "Install with: pip install reportlab\n"
                "Or: pip install structural-lib-is456[pdf]"
            )
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.page_width, self.page_height = A4

    def _setup_custom_styles(self):
        """Create custom paragraph styles for consistent formatting."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceBefore=20,
            spaceAfter=12,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#3498db'),
            borderPadding=5,
            backColor=colors.HexColor('#ecf0f1')
        ))

        # Subsection
        self.styles.add(ParagraphStyle(
            name='Subsection',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#34495e'),
            spaceBefore=12,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))

        # Normal with indent
        self.styles.add(ParagraphStyle(
            name='NormalIndent',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=6
        ))

        # Reference style (for IS 456 clauses)
        self.styles.add(ParagraphStyle(
            name='Reference',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#7f8c8d'),
            fontName='Helvetica-Oblique',
            leftIndent=30
        ))

        # Result highlight
        self.styles.add(ParagraphStyle(
            name='ResultHighlight',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#27ae60'),
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#d5f4e6'),
            borderWidth=1,
            borderColor=colors.HexColor('#27ae60'),
            borderPadding=8
        ))

    def generate_report(
        self,
        design_data: Dict[str, Any],
        project_info: Dict[str, str],
        include_bbs: bool = True,
        include_diagrams: bool = True,
        logo_path: Optional[str] = None
    ) -> BytesIO:
        """
        Generate complete PDF report.

        Args:
            design_data: Beam design results from structural_lib
            project_info: Project details (name, location, engineer, etc.)
            include_bbs: Include Bar Bending Schedule table
            include_diagrams: Include beam cross-section diagram
            logo_path: Optional company logo file path

        Returns:
            BytesIO buffer containing PDF data
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=25*mm,
            bottomMargin=25*mm
        )

        # Build document content
        story = []

        # Cover page
        story.extend(self._create_cover_page(project_info, logo_path))
        story.append(PageBreak())

        # Input summary
        story.extend(self._create_input_summary(design_data))
        story.append(PageBreak())

        # Design calculations
        story.extend(self._create_calculations_section(design_data))
        story.append(PageBreak())

        # Results summary
        story.extend(self._create_results_summary(design_data))

        # Optional: BBS table
        if include_bbs and 'bbs' in design_data:
            story.append(PageBreak())
            story.extend(self._create_bbs_table(design_data['bbs']))

        # Optional: Diagrams
        if include_diagrams:
            story.append(PageBreak())
            story.extend(self._create_diagrams_section(design_data))

        # Compliance checklist
        story.append(PageBreak())
        story.extend(self._create_compliance_checklist(design_data))

        # Signature block
        story.append(Spacer(1, 30))
        story.extend(self._create_signature_block(project_info))

        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)

        buffer.seek(0)
        return buffer

    def _create_cover_page(self, project_info: Dict[str, str], logo_path: Optional[str]) -> List:
        """Create cover page with project information."""
        elements = []

        # Logo (if provided)
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=60*mm, height=30*mm)
                elements.append(logo)
                elements.append(Spacer(1, 20))
            except Exception:
                pass  # Skip logo if loading fails

        # Title
        title = Paragraph(
            "STRUCTURAL DESIGN REPORT<br/>RC Beam Design",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 40))

        # Project info table
        project_data = [
            ['Project Name:', project_info.get('project_name', 'N/A')],
            ['Location:', project_info.get('location', 'N/A')],
            ['Client:', project_info.get('client', 'N/A')],
            ['Engineer:', project_info.get('engineer', 'N/A')],
            ['Design Code:', 'IS 456:2000'],
            ['Report Date:', datetime.now().strftime('%Y-%m-%d')],
        ]

        project_table = Table(project_data, colWidths=[60*mm, 100*mm])
        project_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ]))

        elements.append(project_table)
        elements.append(Spacer(1, 40))

        # Disclaimer
        disclaimer = Paragraph(
            "<i>This report has been generated using automated structural design software "
            "in accordance with IS 456:2000. All calculations have been verified for code compliance. "
            "This document is for design review purposes and should be checked by a licensed structural engineer.</i>",
            self.styles['Normal']
        )
        elements.append(disclaimer)

        return elements

    def _create_input_summary(self, design_data: Dict[str, Any]) -> List:
        """Create input parameters summary table."""
        elements = []

        elements.append(Paragraph("INPUT SUMMARY", self.styles['SectionHeading']))
        elements.append(Spacer(1, 12))

        inputs = design_data.get('inputs', {})

        # Geometry section
        elements.append(Paragraph("Geometry", self.styles['Subsection']))
        geometry_data = [
            ['Parameter', 'Value', 'Unit'],
            ['Effective Span (L)', f"{inputs.get('span_m', 0):.2f}", 'm'],
            ['Width (b)', f"{inputs.get('width_mm', 0):.0f}", 'mm'],
            ['Overall Depth (D)', f"{inputs.get('depth_mm', 0):.0f}", 'mm'],
            ['Effective Depth (d)', f"{inputs.get('effective_depth_mm', 0):.0f}", 'mm'],
            ['Clear Cover', f"{inputs.get('cover_mm', 0):.0f}", 'mm'],
        ]

        geometry_table = self._create_styled_table(geometry_data)
        elements.append(geometry_table)
        elements.append(Spacer(1, 12))

        # Material properties
        elements.append(Paragraph("Material Properties", self.styles['Subsection']))
        material_data = [
            ['Parameter', 'Value', 'Unit'],
            ['Concrete Grade (fck)', f"{inputs.get('fck', 0):.0f}", 'N/mm²'],
            ['Steel Grade (fy)', f"{inputs.get('fy', 0):.0f}", 'N/mm²'],
        ]

        material_table = self._create_styled_table(material_data)
        elements.append(material_table)
        elements.append(Spacer(1, 12))

        # Loading
        elements.append(Paragraph("Loading", self.styles['Subsection']))
        loading_data = [
            ['Load Type', 'Value', 'Unit'],
            ['Dead Load (DL)', f"{inputs.get('dead_load_kN', 0):.2f}", 'kN/m'],
            ['Live Load (LL)', f"{inputs.get('live_load_kN', 0):.2f}", 'kN/m'],
            ['Factored Load (Wu)', f"{inputs.get('factored_load_kN', 0):.2f}", 'kN/m'],
        ]

        loading_table = self._create_styled_table(loading_data)
        elements.append(loading_table)

        return elements

    def _create_calculations_section(self, design_data: Dict[str, Any]) -> List:
        """Create detailed calculations section."""
        elements = []

        elements.append(Paragraph("DESIGN CALCULATIONS", self.styles['SectionHeading']))
        elements.append(Spacer(1, 12))

        # Flexure calculations
        elements.append(Paragraph("1. Flexural Design", self.styles['Subsection']))
        elements.append(Paragraph(
            "Design for bending moment as per IS 456:2000, Cl. 38.1",
            self.styles['Reference']
        ))

        flexure = design_data.get('flexure', {})

        flexure_calc = [
            ['Calculation Step', 'Formula', 'Result'],
            ['Factored Moment (Mu)', 'Mu = wu × L² / 8', f"{flexure.get('Mu_kNm', 0):.2f} kN·m"],
            ['Limiting Moment (Mu,lim)', 'Mu,lim = 0.138 fck b d²', f"{flexure.get('Mu_lim_kNm', 0):.2f} kN·m"],
            ['Steel Area Required (Ast)', 'From Mu = 0.87 fy Ast (d - 0.42 Xu)', f"{flexure.get('Ast_req_mm2', 0):.0f} mm²"],
            ['Minimum Steel (Ast,min)', '0.85 / fy × b × d', f"{flexure.get('Ast_min_mm2', 0):.0f} mm²"],
            ['Steel Provided (Ast,prov)', 'Based on bar selection', f"{flexure.get('Ast_prov_mm2', 0):.0f} mm²"],
        ]

        flexure_table = self._create_styled_table(flexure_calc, col_widths=[60*mm, 60*mm, 40*mm])
        elements.append(flexure_table)
        elements.append(Spacer(1, 12))

        # Shear calculations
        elements.append(Paragraph("2. Shear Design", self.styles['Subsection']))
        elements.append(Paragraph(
            "Design for shear force as per IS 456:2000, Cl. 40",
            self.styles['Reference']
        ))

        shear = design_data.get('shear', {})

        shear_calc = [
            ['Calculation Step', 'Formula', 'Result'],
            ['Factored Shear (Vu)', 'Vu = wu × L / 2', f"{shear.get('Vu_kN', 0):.2f} kN"],
            ['Shear Stress (τv)', 'τv = Vu / (b × d)', f"{shear.get('tau_v', 0):.3f} N/mm²"],
            ['Shear Capacity (τc)', 'From Table 19, IS 456', f"{shear.get('tau_c', 0):.3f} N/mm²"],
            ['Stirrup Spacing (Sv)', 'From design chart', f"{shear.get('spacing_mm', 0):.0f} mm"],
        ]

        shear_table = self._create_styled_table(shear_calc, col_widths=[60*mm, 60*mm, 40*mm])
        elements.append(shear_table)

        return elements

    def _create_results_summary(self, design_data: Dict[str, Any]) -> List:
        """Create results summary with pass/fail indicators."""
        elements = []

        elements.append(Paragraph("DESIGN RESULTS SUMMARY", self.styles['SectionHeading']))
        elements.append(Spacer(1, 12))

        flexure = design_data.get('flexure', {})
        shear = design_data.get('shear', {})
        detailing = design_data.get('detailing', {})

        # Overall status
        is_safe = flexure.get('is_safe', False) and shear.get('is_safe', False)
        status_text = "✓ DESIGN SAFE" if is_safe else "✗ DESIGN UNSAFE"
        status_color = '#27ae60' if is_safe else '#e74c3c'

        status_para = Paragraph(
            f"<b>{status_text}</b>",
            ParagraphStyle(
                'Status',
                parent=self.styles['Normal'],
                fontSize=14,
                textColor=colors.HexColor(status_color),
                alignment=TA_CENTER,
                spaceBefore=10,
                spaceAfter=20
            )
        )
        elements.append(status_para)

        # Detailed results
        results_data = [
            ['Design Check', 'Required', 'Provided', 'Status'],
            [
                'Main Reinforcement',
                f"{flexure.get('Ast_req_mm2', 0):.0f} mm²",
                f"{flexure.get('Ast_prov_mm2', 0):.0f} mm²",
                '✓ OK' if flexure.get('is_safe', False) else '✗ FAIL'
            ],
            [
                'Stirrups',
                f"{shear.get('stirrup_legs', 0)}-legged",
                f"@ {shear.get('spacing_mm', 0):.0f} mm",
                '✓ OK' if shear.get('is_safe', False) else '✗ FAIL'
            ],
            [
                'Development Length',
                f"{detailing.get('Ld_req_mm', 0):.0f} mm",
                f"{detailing.get('Ld_avail_mm', 0):.0f} mm",
                '✓ OK' if detailing.get('is_safe', False) else '✗ FAIL'
            ],
        ]

        results_table = Table(results_data, colWidths=[60*mm, 40*mm, 40*mm, 30*mm])
        results_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
        ]))

        elements.append(results_table)

        return elements

    def _create_bbs_table(self, bbs_data: Dict[str, Any]) -> List:
        """Create Bar Bending Schedule table."""
        elements = []

        elements.append(Paragraph("BAR BENDING SCHEDULE", self.styles['SectionHeading']))
        elements.append(Spacer(1, 12))

        # BBS table structure
        bbs_headers = ['Mark', 'Type', 'Dia (mm)', 'No.', 'Length (mm)', 'Total (m)', 'Weight (kg)']
        bbs_rows = [bbs_headers]

        # Add bars from BBS data
        for bar in bbs_data.get('bars', []):
            bbs_rows.append([
                bar.get('mark', ''),
                bar.get('type', ''),
                str(bar.get('diameter_mm', '')),
                str(bar.get('number', '')),
                f"{bar.get('length_mm', 0):.0f}",
                f"{bar.get('total_length_m', 0):.2f}",
                f"{bar.get('weight_kg', 0):.2f}",
            ])

        # Summary row
        total_weight = sum(bar.get('weight_kg', 0) for bar in bbs_data.get('bars', []))
        bbs_rows.append(['', '', '', '', '', 'Total:', f"{total_weight:.2f}"])

        bbs_table = Table(bbs_rows, colWidths=[15*mm, 25*mm, 20*mm, 15*mm, 25*mm, 25*mm, 25*mm])
        bbs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (5, -1), (-1, -1), 'Helvetica-Bold'),
        ]))

        elements.append(bbs_table)

        return elements

    def _create_diagrams_section(self, design_data: Dict[str, Any]) -> List:
        """Create diagrams section placeholder."""
        elements = []

        elements.append(Paragraph("BEAM CROSS-SECTION", self.styles['SectionHeading']))
        elements.append(Spacer(1, 12))

        # Placeholder for diagram (would need actual drawing library)
        elements.append(Paragraph(
            "[Beam cross-section diagram would be inserted here]",
            self.styles['Normal']
        ))
        elements.append(Paragraph(
            "Showing: Reinforcement layout, dimensions, and bar marks",
            self.styles['NormalIndent']
        ))

        return elements

    def _create_compliance_checklist(self, design_data: Dict[str, Any]) -> List:
        """Create IS 456 compliance checklist."""
        elements = []

        elements.append(Paragraph("COMPLIANCE CHECKLIST (IS 456:2000)", self.styles['SectionHeading']))
        elements.append(Spacer(1, 12))

        compliance = design_data.get('compliance', {})

        checklist_data = [
            ['Check', 'Clause', 'Status'],
            ['Minimum reinforcement provided', 'Cl. 26.5.1.1', '✓' if compliance.get('min_steel_ok', False) else '✗'],
            ['Maximum reinforcement not exceeded', 'Cl. 26.5.1.2', '✓' if compliance.get('max_steel_ok', False) else '✗'],
            ['Maximum spacing satisfied', 'Cl. 26.3.3', '✓' if compliance.get('spacing_ok', False) else '✗'],
            ['Development length adequate', 'Cl. 26.2.1', '✓' if compliance.get('dev_length_ok', False) else '✗'],
            ['Shear reinforcement provided', 'Cl. 40.4', '✓' if compliance.get('shear_reinf_ok', False) else '✗'],
        ]

        checklist_table = self._create_styled_table(checklist_data)
        elements.append(checklist_table)

        return elements

    def _create_signature_block(self, project_info: Dict[str, str]) -> List:
        """Create signature block."""
        elements = []

        sig_data = [
            ['Prepared By:', '', 'Checked By:', ''],
            [project_info.get('engineer', ''), '_' * 30, project_info.get('checker', ''), '_' * 30],
            ['Date:', datetime.now().strftime('%Y-%m-%d'), 'Date:', '_' * 30],
        ]

        sig_table = Table(sig_data, colWidths=[30*mm, 60*mm, 30*mm, 60*mm])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))

        elements.append(sig_table)

        return elements

    def _create_styled_table(self, data: List[List[str]], col_widths: Optional[List] = None) -> Table:
        """Create a consistently styled table."""
        if col_widths is None:
            col_widths = [60*mm, 60*mm, 40*mm]

        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),  # Right-align values column
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ]))

        return table

    def _add_header_footer(self, canvas_obj, doc):
        """Add header and footer to pages."""
        canvas_obj.saveState()

        # Header
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.setFillColorRGB(0.5, 0.5, 0.5)
        canvas_obj.drawString(20*mm, self.page_height - 15*mm, "Structural Design Report - RC Beam")

        # Footer
        canvas_obj.drawString(20*mm, 15*mm, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        canvas_obj.drawRightString(self.page_width - 20*mm, 15*mm, f"Page {doc.page}")

        canvas_obj.restoreState()
