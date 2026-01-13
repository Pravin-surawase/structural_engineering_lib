# Calculation Report Generation

**Document Version:** 1.0
**Last Updated:** 2026-01-07
**Status:** Complete
**Task:** TASK-242
**Author:** Research Team (Structural Engineer + Library Developer)

---

## Executive Summary

**Problem:** Library calculates designs but doesn't generate professional calculation sheets. Engineers need formatted, printable reports for documentation, review, and regulatory submission.

**Goal:** Research report generation patterns for engineering calculations that produce:
1. Professional-quality calculation sheets
2. Multiple formats (PDF, Excel, Word)
3. Reproducible outputs
4. Compliant with professional standards

**Key Finding:** Engineering reports need structured templates + programmatic generation. HTML→PDF via WeasyPrint provides best balance of flexibility, quality, and maintainability.

**Recommendation:**
- Phase 1: HTML templates + CSS (6-8 hours)
- Phase 2: PDF generation (WeasyPrint) (4-5 hours)
- Phase 3: Excel export (openpyxl) (3-4 hours)
- Total: 13-17 hours implementation

---

## Table of Contents

1. [Report Requirements](#1-report-requirements)
2. [Output Format Options](#2-output-format-options)
3. [Recommended Architecture](#3-recommended-architecture)
4. [Template Design](#4-template-design)
5. [PDF Generation](#5-pdf-generation)
6. [Excel Generation](#6-excel-generation)
7. [Implementation Guide](#7-implementation-guide)

---

## 1. Report Requirements

### 1.1 Engineering Calculation Sheet Standards

**Essential Elements:**

1. **Header Information**
   - Project name/number
   - Engineer name & license
   - Calculation date
   - Software version
   - Code standard (IS 456:2000)

2. **Design Inputs**
   - All parameters (dimensions, loads, materials)
   - Units clearly stated
   - Source of values (drawings, specs, etc.)

3. **Calculations**
   - Step-by-step calculations
   - Formulas shown
   - Code clause references
   - Intermediate results

4. **Results Summary**
   - Required reinforcement
   - Utilization ratios
   - Pass/fail status
   - Safety factors

5. **Checks & Verifications**
   - Minimum/maximum limits
   - Serviceability checks
   - Compliance verification

6. **Professional Certification**
   - Engineer signature line
   - License number
   - Date & seal

### 1.2 Example Calculation Sheet Structure

```
================================================================================
                    REINFORCED CONCRETE BEAM DESIGN
                         Per IS 456:2000
================================================================================

PROJECT INFORMATION
  Project:         Residential Building - Block A
  Location:        Mumbai, Maharashtra
  Designed By:     John Doe, P.E.
  License No.:     MH/12345/2024
  Date:            2026-01-07
  Software:        structural_lib v0.15.0

================================================================================
DESIGN INPUTS
================================================================================

Geometry:
  Span (L)                    = 5000 mm
  Width (b)                   = 230 mm
  Effective Depth (d)         = 450 mm
  Clear Cover                 = 25 mm

Materials:
  Concrete Grade (fck)        = 25 N/mm² (M25)
  Steel Grade (fy)            = 415 N/mm² (Fe415)

Loading:
  Factored Moment (Mu)        = 120 kN·m
  Factored Shear (Vu)         = 85 kN

================================================================================
FLEXURAL DESIGN (IS 456:2000 Section 38)
================================================================================

Step 1: Check section adequacy (Cl. 38.1)

  Mu,lim = 0.138 * fck * b * d²
         = 0.138 × 25 × 230 × 450²  [Cl. 38.1]
         = 158.9 kN·m

  Mu / Mu,lim = 120 / 158.9 = 0.755 < 1.0  ✓ Under-reinforced

Step 2: Calculate required steel (Cl. 38.1)

  Ast = (Mu × 10⁶) / (0.87 × fy × d × (1 - Mu/(Mu,lim × 1.15)))
      = (120 × 10⁶) / (0.87 × 415 × 450 × 0.91)
      = 821 mm²

Step 3: Check minimum steel (Cl. 26.5.1.1)

  Ast,min = 0.85 × b × d / fy  [Cl. 26.5.1.1a]
          = 0.85 × 230 × 450 / 415
          = 213 mm²

  Ast,req = max(821, 213) = 821 mm²  ✓

Step 4: Bar selection

  Provide: 3-20φ + 1-16φ (Ast,prov = 1143 mm²)
  Ratio: 1143 / 821 = 1.39  (39% excess)  ✓

================================================================================
SHEAR DESIGN (IS 456:2000 Section 40)
================================================================================

[... similar detailed steps ...]

================================================================================
DESIGN SUMMARY
================================================================================

Flexure:
  Required Steel:      821 mm²
  Provided Steel:      1143 mm² (3-20φ + 1-16φ)
  Utilization:         71.8%  ✓ SAFE

Shear:
  Design Shear:        85 kN
  Capacity:            156 kN
  Utilization:         54.5%  ✓ SAFE

DESIGN STATUS: ✓ PASS - Design complies with IS 456:2000

================================================================================
PROFESSIONAL CERTIFICATION
================================================================================

I, the undersigned licensed professional engineer, have reviewed these
calculations and take full professional responsibility for this design.

Engineer: _____________________    Date: _____________
License:  _____________________    Seal: [ ]

================================================================================
```

---

## 2. Output Format Options

### 2.1 PDF (Primary Format)

**Pros:**
- ✅ Professional appearance
- ✅ Universal compatibility
- ✅ Print-ready
- ✅ Non-editable (integrity)

**Cons:**
- ❌ Not editable by user
- ❌ Requires PDF library

**Use Case:** Final calculations for submission

### 2.2 Excel (Secondary Format)

**Pros:**
- ✅ Editable by engineers
- ✅ Can add custom notes
- ✅ Familiar format
- ✅ Easy calculations review

**Cons:**
- ❌ Can be accidentally modified
- ❌ Less professional appearance

**Use Case:** Working calculations, reviews

### 2.3 HTML (Intermediate Format)

**Pros:**
- ✅ Easy to generate (templates)
- ✅ Can convert to PDF
- ✅ Supports styling (CSS)
- ✅ Viewable in browser

**Cons:**
- ❌ Not standard for engineering
- ❌ Requires browser

**Use Case:** Preview, intermediate step to PDF

### 2.4 Word/DOCX

**Pros:**
- ✅ Editable
- ✅ Professional format
- ✅ Common in engineering

**Cons:**
- ❌ Complex to generate programmatically
- ❌ Formatting can break

**Use Case:** Optional, if requested

---

## 3. Recommended Architecture

### 3.1 Report Generation Pipeline

```
Input Data
    ↓
[Template Engine]  ← Jinja2 templates
    ↓
HTML + CSS
    ↓
[WeasyPrint]
    ↓
PDF Output
```

**Alternative path for Excel:**
```
Input Data
    ↓
[Excel Builder]  ← openpyxl
    ↓
Excel Output
```

### 3.2 Component Architecture

```python
structural_lib/
  reports/
    __init__.py
    templates/
      beam_design.html           # HTML template
      styles.css                 # Report styling
      header.html               # Reusable header
      footer.html               # Reusable footer
    generators/
      pdf_generator.py          # PDF generation
      excel_generator.py        # Excel generation
      html_generator.py         # HTML rendering
    formatters.py               # Value formatting utilities
```

---

## 4. Template Design

### 4.1 Jinja2 Template Pattern

**Template: `templates/beam_design.html`**

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Beam Design Calculation - {{ project_name }}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="report">
        <!-- Header -->
        <div class="header">
            <h1>REINFORCED CONCRETE BEAM DESIGN</h1>
            <h2>Per IS 456:2000</h2>
        </div>

        <!-- Project Info -->
        <section class="project-info">
            <h3>PROJECT INFORMATION</h3>
            <table class="info-table">
                <tr><td>Project:</td><td>{{ project.name }}</td></tr>
                <tr><td>Location:</td><td>{{ project.location }}</td></tr>
                <tr><td>Designed By:</td><td>{{ engineer.name }}</td></tr>
                <tr><td>License No.:</td><td>{{ engineer.license }}</td></tr>
                <tr><td>Date:</td><td>{{ date }}</td></tr>
                <tr><td>Software:</td><td>structural_lib v{{ version }}</td></tr>
            </table>
        </section>

        <!-- Design Inputs -->
        <section class="inputs">
            <h3>DESIGN INPUTS</h3>

            <h4>Geometry:</h4>
            <table class="calc-table">
                <tr>
                    <td>Span (L)</td>
                    <td>{{ inputs.span_mm | format_value }} mm</td>
                </tr>
                <tr>
                    <td>Width (b)</td>
                    <td>{{ inputs.width_mm | format_value }} mm</td>
                </tr>
                <tr>
                    <td>Effective Depth (d)</td>
                    <td>{{ inputs.depth_mm | format_value }} mm</td>
                </tr>
            </table>

            <h4>Materials:</h4>
            <table class="calc-table">
                <tr>
                    <td>Concrete Grade (fck)</td>
                    <td>{{ inputs.fck_mpa | format_value }} N/mm² (M{{ inputs.fck_mpa }})</td>
                </tr>
                <tr>
                    <td>Steel Grade (fy)</td>
                    <td>{{ inputs.fy_mpa | format_value }} N/mm² (Fe{{ inputs.fy_mpa }})</td>
                </tr>
            </table>
        </section>

        <!-- Calculations -->
        <section class="calculations">
            <h3>FLEXURAL DESIGN (IS 456:2000 Section 38)</h3>

            {% for step in calculations.flexure %}
            <div class="calc-step">
                <h4>{{ step.title }}</h4>
                <p class="formula">{{ step.formula }}</p>
                {% if step.reference %}
                <p class="reference">[{{ step.reference }}]</p>
                {% endif %}
                <p class="result">= {{ step.result | format_value }} {{ step.units }}</p>
                {% if step.check %}
                <p class="check {{ 'pass' if step.check.passed else 'fail' }}">
                    {{ step.check.message }} {{ '✓' if step.check.passed else '✗' }}
                </p>
                {% endif %}
            </div>
            {% endfor %}
        </section>

        <!-- Summary -->
        <section class="summary">
            <h3>DESIGN SUMMARY</h3>
            <table class="summary-table">
                <tr>
                    <th>Item</th>
                    <th>Required</th>
                    <th>Provided</th>
                    <th>Utilization</th>
                    <th>Status</th>
                </tr>
                <tr>
                    <td>Flexural Steel</td>
                    <td>{{ results.ast_req | format_value }} mm²</td>
                    <td>{{ results.ast_prov | format_value }} mm²</td>
                    <td>{{ results.flexure_util | format_percent }}</td>
                    <td class="{{ 'pass' if results.flexure_safe else 'fail' }}">
                        {{ '✓ SAFE' if results.flexure_safe else '✗ UNSAFE' }}
                    </td>
                </tr>
                <tr>
                    <td>Shear Capacity</td>
                    <td>{{ results.vu_req | format_value }} kN</td>
                    <td>{{ results.vu_cap | format_value }} kN</td>
                    <td>{{ results.shear_util | format_percent }}</td>
                    <td class="{{ 'pass' if results.shear_safe else 'fail' }}">
                        {{ '✓ SAFE' if results.shear_safe else '✗ UNSAFE' }}
                    </td>
                </tr>
            </table>

            <div class="overall-status {{ 'pass' if results.overall_safe else 'fail' }}">
                DESIGN STATUS: {{ '✓ PASS' if results.overall_safe else '✗ FAIL' }}
            </div>
        </section>

        <!-- Certification -->
        <section class="certification">
            <h3>PROFESSIONAL CERTIFICATION</h3>
            <p class="disclaimer">
                I, the undersigned licensed professional engineer, have reviewed
                these calculations and take full professional responsibility for
                this design.
            </p>
            <div class="signature-block">
                <div class="signature-line">
                    <label>Engineer:</label>
                    <span class="underline"></span>
                    <label>Date:</label>
                    <span class="underline short"></span>
                </div>
                <div class="signature-line">
                    <label>License:</label>
                    <span class="underline"></span>
                    <label>Seal:</label>
                    <span class="seal-box">[ ]</span>
                </div>
            </div>
        </section>

        <!-- Footer -->
        <div class="footer">
            <p>Generated by structural_lib v{{ version }} | {{ date }}</p>
            <p>Page {{ page }} of {{ total_pages }}</p>
        </div>
    </div>
</body>
</html>
```

### 4.2 CSS Styling

**File: `templates/styles.css`**

```css
@page {
    size: A4;
    margin: 20mm;
    @top-center {
        content: "Beam Design Calculation";
        font-size: 10pt;
        color: #666;
    }
    @bottom-center {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 9pt;
    }
}

body {
    font-family: 'Arial', 'Helvetica', sans-serif;
    font-size: 10pt;
    line-height: 1.4;
    color: #000;
}

.report {
    max-width: 210mm;
    margin: 0 auto;
}

.header {
    text-align: center;
    border-bottom: 3px solid #000;
    padding-bottom: 10px;
    margin-bottom: 20px;
}

.header h1 {
    font-size: 18pt;
    margin: 0;
}

.header h2 {
    font-size: 12pt;
    margin: 5px 0 0 0;
    color: #666;
}

section {
    margin: 20px 0;
    page-break-inside: avoid;
}

h3 {
    font-size: 12pt;
    background: #f0f0f0;
    padding: 5px 10px;
    border-left: 4px solid #0066cc;
    margin: 15px 0 10px 0;
}

h4 {
    font-size: 11pt;
    margin: 10px 0 5px 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
}

.info-table td {
    padding: 3px 10px;
    border-bottom: 1px solid #ddd;
}

.info-table td:first-child {
    font-weight: bold;
    width: 150px;
}

.calc-table td {
    padding: 3px 10px;
}

.calc-table td:first-child {
    width: 200px;
}

.calc-step {
    margin: 15px 0;
    padding: 10px;
    background: #fafafa;
    border-left: 3px solid #0066cc;
}

.formula {
    font-family: 'Courier New', monospace;
    background: #fff;
    padding: 5px;
    margin: 5px 0;
    border: 1px solid #ddd;
}

.reference {
    font-size: 9pt;
    color: #666;
    font-style: italic;
}

.result {
    font-weight: bold;
    color: #0066cc;
}

.check.pass {
    color: #008000;
    font-weight: bold;
}

.check.fail {
    color: #cc0000;
    font-weight: bold;
}

.summary-table {
    border: 2px solid #000;
}

.summary-table th {
    background: #0066cc;
    color: #fff;
    padding: 8px;
    text-align: left;
}

.summary-table td {
    padding: 6px 8px;
    border-bottom: 1px solid #ddd;
}

.overall-status {
    margin: 20px 0;
    padding: 15px;
    text-align: center;
    font-size: 14pt;
    font-weight: bold;
    border: 3px solid;
}

.overall-status.pass {
    background: #e8f5e9;
    color: #2e7d32;
    border-color: #2e7d32;
}

.overall-status.fail {
    background: #ffebee;
    color: #c62828;
    border-color: #c62828;
}

.certification {
    margin-top: 30px;
    border-top: 2px solid #000;
    padding-top: 20px;
}

.disclaimer {
    font-size: 9pt;
    font-style: italic;
    margin: 10px 0;
}

.signature-block {
    margin: 20px 0;
}

.signature-line {
    margin: 15px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.underline {
    flex: 1;
    border-bottom: 1px solid #000;
    height: 20px;
}

.underline.short {
    flex: 0 0 100px;
}

.seal-box {
    display: inline-block;
    width: 60px;
    height: 60px;
    border: 2px solid #000;
    text-align: center;
    line-height: 60px;
}

.footer {
    margin-top: 30px;
    padding-top: 10px;
    border-top: 1px solid #999;
    font-size: 8pt;
    color: #666;
    text-align: center;
}
```

---

## 5. PDF Generation

### 5.1 WeasyPrint Implementation

**Why WeasyPrint:**
- ✅ HTML/CSS → PDF (familiar tech)
- ✅ High-quality output
- ✅ Supports page breaks, headers, footers
- ✅ Open source, maintained

**Installation:**
```bash
pip install weasyprint jinja2
```

**Implementation:**

```python
# reports/generators/pdf_generator.py
from pathlib import Path
from typing import Dict
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import tempfile

class PDFReportGenerator:
    """Generate PDF calculation reports."""

    def __init__(self, template_dir: Path = None):
        if template_dir is None:
            template_dir = Path(__file__).parent.parent / 'templates'

        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )

        # Register custom filters
        self.env.filters['format_value'] = self._format_value
        self.env.filters['format_percent'] = self._format_percent

    def generate_beam_report(
        self,
        result: 'BeamDesignResult',
        output_file: str,
        project_info: Dict = None,
        engineer_info: Dict = None
    ) -> None:
        """
        Generate PDF report for beam design.

        Args:
            result: BeamDesignResult object
            output_file: Path to output PDF
            project_info: Dict with project metadata
            engineer_info: Dict with engineer info

        Example:
            >>> generator = PDFReportGenerator()
            >>> generator.generate_beam_report(
            ...     result=beam_result,
            ...     output_file='beam_calc.pdf',
            ...     project_info={'name': 'Building A', 'location': 'Mumbai'},
            ...     engineer_info={'name': 'John Doe', 'license': 'MH/12345'}
            ... )
        """
        # Prepare template data
        template_data = self._prepare_template_data(
            result, project_info, engineer_info
        )

        # Render HTML from template
        template = self.env.get_template('beam_design.html')
        html_content = template.render(**template_data)

        # Generate PDF
        HTML(string=html_content).write_pdf(output_file)

    def _prepare_template_data(
        self,
        result: 'BeamDesignResult',
        project_info: Dict,
        engineer_info: Dict
    ) -> Dict:
        """Prepare data dict for template."""
        from datetime import datetime
        import structural_lib

        return {
            'project': project_info or {},
            'engineer': engineer_info or {},
            'date': datetime.now().strftime('%Y-%m-%d'),
            'version': structural_lib.__version__,
            'inputs': result.inputs,
            'calculations': self._format_calculations(result),
            'results': self._format_results(result),
        }

    def _format_calculations(self, result: 'BeamDesignResult') -> Dict:
        """Format calculation steps for template."""
        # Extract step-by-step calculations from result
        return {
            'flexure': [
                {
                    'title': 'Step 1: Check section adequacy',
                    'formula': 'Mu,lim = 0.138 × fck × b × d²',
                    'reference': 'IS 456 Cl. 38.1',
                    'result': result.mu_lim,
                    'units': 'kN·m',
                    'check': {
                        'passed': result.mu < result.mu_lim,
                        'message': f'Mu / Mu,lim = {result.mu/result.mu_lim:.3f} < 1.0'
                    }
                },
                # ... more steps
            ]
        }

    def _format_results(self, result: 'BeamDesignResult') -> Dict:
        """Format results summary for template."""
        return {
            'ast_req': result.ast_mm2,
            'ast_prov': result.ast_provided_mm2,
            'flexure_util': result.ast_mm2 / result.ast_provided_mm2,
            'flexure_safe': result.is_safe,
            # ... more results
        }

    @staticmethod
    def _format_value(value: float, decimals: int = 1) -> str:
        """Format numeric value for display."""
        return f"{value:.{decimals}f}"

    @staticmethod
    def _format_percent(value: float) -> str:
        """Format as percentage."""
        return f"{value * 100:.1f}%"
```

---

**(Part 1/2 - continuing in next file to stay under size limit)**
