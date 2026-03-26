# Calculation Report Generation - Part 2/2

**(Continued from part1.md)**

## 6. Excel Generation

### 6.1 openpyxl Implementation

**Why openpyxl:**
- ✅ Pure Python (no external deps)
- ✅ Full Excel format support
- ✅ Styling, formulas, charts
- ✅ Well-maintained

**Implementation:**

```python
# reports/generators/excel_generator.py
from pathlib import Path
from typing import Dict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

class ExcelReportGenerator:
    """Generate Excel calculation reports."""

    def __init__(self):
        self.wb = None
        self.ws = None

        # Define styles
        self.styles = {
            'header': Font(size=14, bold=True),
            'section': Font(size=12, bold=True),
            'label': Font(bold=True),
            'pass': PatternFill(start_color='C6EFCE', fill_type='solid'),
            'fail': PatternFill(start_color='FFC7CE', fill_type='solid'),
        }

    def generate_beam_report(
        self,
        result: 'BeamDesignResult',
        output_file: str,
        project_info: Dict = None
    ) -> None:
        """
        Generate Excel report for beam design.

        Args:
            result: BeamDesignResult object
            output_file: Path to output Excel file
            project_info: Dict with project metadata
        """
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.title = "Beam Design"

        row = 1

        # Header
        row = self._add_header(row)
        row += 1

        # Project info
        row = self._add_project_info(row, project_info)
        row += 1

        # Design inputs
        row = self._add_inputs(row, result.inputs)
        row += 1

        # Calculations
        row = self._add_calculations(row, result)
        row += 1

        # Summary
        row = self._add_summary(row, result)

        # Adjust column widths
        self._autosize_columns()

        # Save
        self.wb.save(output_file)

    def _add_header(self, row: int) -> int:
        """Add report header."""
        self.ws.merge_cells(f'A{row}:F{row}')
        cell = self.ws[f'A{row}']
        cell.value = 'REINFORCED CONCRETE BEAM DESIGN'
        cell.font = self.styles['header']
        cell.alignment = Alignment(horizontal='center')

        row += 1
        self.ws.merge_cells(f'A{row}:F{row}')
        cell = self.ws[f'A{row}']
        cell.value = 'Per IS 456:2000'
        cell.alignment = Alignment(horizontal='center')

        return row + 1

    def _add_project_info(self, row: int, project_info: Dict) -> int:
        """Add project information section."""
        # Section header
        self.ws.merge_cells(f'A{row}:F{row}')
        cell = self.ws[f'A{row}']
        cell.value = 'PROJECT INFORMATION'
        cell.font = self.styles['section']
        cell.fill = PatternFill(start_color='D9D9D9', fill_type='solid')
        row += 1

        # Project fields
        fields = [
            ('Project:', project_info.get('name', '')),
            ('Location:', project_info.get('location', '')),
            ('Designed By:', project_info.get('engineer', '')),
            ('Date:', project_info.get('date', '')),
        ]

        for label, value in fields:
            self.ws[f'A{row}'] = label
            self.ws[f'A{row}'].font = self.styles['label']
            self.ws[f'B{row}'] = value
            row += 1

        return row

    def _add_inputs(self, row: int, inputs: Dict) -> int:
        """Add design inputs section."""
        # Section header
        self.ws.merge_cells(f'A{row}:F{row}')
        cell = self.ws[f'A{row}']
        cell.value = 'DESIGN INPUTS'
        cell.font = self.styles['section']
        cell.fill = PatternFill(start_color='D9D9D9', fill_type='solid')
        row += 1

        # Geometry subsection
        self.ws[f'A{row}'] = 'Geometry:'
        self.ws[f'A{row}'].font = Font(bold=True, underline='single')
        row += 1

        geom_fields = [
            ('Span (L)', inputs.span_mm, 'mm'),
            ('Width (b)', inputs.width_mm, 'mm'),
            ('Effective Depth (d)', inputs.depth_mm, 'mm'),
        ]

        for label, value, unit in geom_fields:
            self.ws[f'A{row}'] = label
            self.ws[f'B{row}'] = value
            self.ws[f'C{row}'] = unit
            row += 1

        row += 1

        # Materials subsection
        self.ws[f'A{row}'] = 'Materials:'
        self.ws[f'A{row}'].font = Font(bold=True, underline='single')
        row += 1

        mat_fields = [
            ('Concrete Grade (fck)', inputs.fck_mpa, f"N/mm² (M{inputs.fck_mpa})"),
            ('Steel Grade (fy)', inputs.fy_mpa, f"N/mm² (Fe{inputs.fy_mpa})"),
        ]

        for label, value, unit in mat_fields:
            self.ws[f'A{row}'] = label
            self.ws[f'B{row}'] = value
            self.ws[f'C{row}'] = unit
            row += 1

        return row

    def _add_calculations(self, row: int, result: 'BeamDesignResult') -> int:
        """Add calculation steps."""
        # Section header
        self.ws.merge_cells(f'A{row}:F{row}')
        cell = self.ws[f'A{row}']
        cell.value = 'FLEXURAL DESIGN (IS 456:2000 Section 38)'
        cell.font = self.styles['section']
        cell.fill = PatternFill(start_color='D9D9D9', fill_type='solid')
        row += 1

        # Step 1
        self.ws[f'A{row}'] = 'Step 1: Check section adequacy'
        self.ws[f'A{row}'].font = Font(bold=True)
        row += 1

        self.ws[f'A{row}'] = 'Mu,lim = 0.138 × fck × b × d²'
        row += 1

        self.ws[f'A{row}'] = '='
        self.ws[f'B{row}'] = result.mu_lim
        self.ws[f'C{row}'] = 'kN·m'
        self.ws[f'D{row}'] = '[IS 456 Cl. 38.1]'
        row += 1

        # Check result
        ratio = result.mu / result.mu_lim
        self.ws[f'A{row}'] = f'Mu / Mu,lim = {ratio:.3f}'
        if ratio < 1.0:
            self.ws[f'A{row}'].fill = self.styles['pass']
            self.ws[f'B{row}'] = '✓ Under-reinforced'
        else:
            self.ws[f'A{row}'].fill = self.styles['fail']
            self.ws[f'B{row}'] = '✗ Over-reinforced'
        row += 2

        # More steps would be added similarly...

        return row

    def _add_summary(self, row: int, result: 'BeamDesignResult') -> int:
        """Add summary table."""
        # Section header
        self.ws.merge_cells(f'A{row}:F{row}')
        cell = self.ws[f'A{row}']
        cell.value = 'DESIGN SUMMARY'
        cell.font = self.styles['section']
        cell.fill = PatternFill(start_color='D9D9D9', fill_type='solid')
        row += 1

        # Table headers
        headers = ['Item', 'Required', 'Provided', 'Utilization', 'Status']
        for col, header in enumerate(headers, start=1):
            cell = self.ws.cell(row, col)
            cell.value = header
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color='4472C4', fill_type='solid')
            cell.font = Font(bold=True, color='FFFFFF')
        row += 1

        # Flexure row
        self.ws[f'A{row}'] = 'Flexural Steel'
        self.ws[f'B{row}'] = f"{result.ast_mm2:.0f} mm²"
        self.ws[f'C{row}'] = f"{result.ast_provided_mm2:.0f} mm²"
        util = result.ast_mm2 / result.ast_provided_mm2
        self.ws[f'D{row}'] = f"{util*100:.1f}%"

        status_cell = self.ws[f'E{row}']
        if result.is_safe:
            status_cell.value = '✓ SAFE'
            status_cell.fill = self.styles['pass']
        else:
            status_cell.value = '✗ UNSAFE'
            status_cell.fill = self.styles['fail']
        row += 1

        # Overall status
        row += 1
        self.ws.merge_cells(f'A{row}:E{row}')
        cell = self.ws[f'A{row}']
        if result.is_safe:
            cell.value = 'DESIGN STATUS: ✓ PASS - Design complies with IS 456:2000'
            cell.fill = self.styles['pass']
        else:
            cell.value = 'DESIGN STATUS: ✗ FAIL - Design does NOT comply'
            cell.fill = self.styles['fail']
        cell.font = Font(bold=True, size=12)
        cell.alignment = Alignment(horizontal='center')

        return row

    def _autosize_columns(self):
        """Auto-adjust column widths."""
        for column_cells in self.ws.columns:
            length = max(len(str(cell.value or '')) for cell in column_cells)
            self.ws.column_dimensions[column_cells[0].column_letter].width = length + 2
```

---

## 7. Implementation Guide

### 7.1 Phase 1: HTML Templates (6-8 hours)

**Step 1: Create template structure** (2 hours)
- Base template with header/footer
- Beam design template
- CSS styling

**Step 2: Template filters** (1 hour)
- Value formatting
- Percentage formatting
- Unit handling

**Step 3: Data preparation** (2 hours)
- Extract calculation steps from results
- Format for template consumption
- Handle edge cases

**Step 4: Testing** (2-3 hours)
- Test with various beam designs
- Check formatting edge cases
- Verify output quality

### 7.2 Phase 2: PDF Generation (4-5 hours)

**Step 1: WeasyPrint integration** (2 hours)
- Install and configure
- Render HTML to PDF
- Handle page breaks

**Step 2: Styling refinement** (1-2 hours)
- Print-specific CSS
- Page headers/footers
- Professional appearance

**Step 3: Testing** (1 hour)
- Generate sample PDFs
- Verify print quality
- Check cross-platform rendering

### 7.3 Phase 3: Excel Export (3-4 hours)

**Step 1: Excel builder** (2 hours)
- Create workbook structure
- Add data sections
- Apply styling

**Step 2: Formula support** (1 hour)
- Add Excel formulas where useful
- Allow user modifications

**Step 3: Testing** (1 hour)
- Test with Excel/LibreOffice
- Verify formatting
- Check formulas

---

## 8. Usage Examples

### 8.1 Generate PDF Report

```python
from structural_lib import design_beam
from structural_lib.reports import PDFReportGenerator

# Design beam
result = design_beam(
    span_mm=5000,
    width_mm=230,
    depth_mm=450,
    moment_knm=120,
    shear_kn=85
)

# Generate PDF report
generator = PDFReportGenerator()
generator.generate_beam_report(
    result=result,
    output_file='beam_design_calc.pdf',
    project_info={
        'name': 'Residential Building - Block A',
        'location': 'Mumbai, Maharashtra',
    },
    engineer_info={
        'name': 'John Doe, P.E.',
        'license': 'MH/12345/2024',
    }
)

print("PDF report generated: beam_design_calc.pdf")
```

### 8.2 Generate Excel Report

```python
from structural_lib.reports import ExcelReportGenerator

# Generate Excel report
generator = ExcelReportGenerator()
generator.generate_beam_report(
    result=result,
    output_file='beam_design_calc.xlsx',
    project_info={
        'name': 'Residential Building - Block A',
        'date': '2026-01-07',
    }
)

print("Excel report generated: beam_design_calc.xlsx")
```

### 8.3 Batch Report Generation

```python
from structural_lib.reports import PDFReportGenerator
from pathlib import Path

# Design multiple beams
beams = [...]  # List of beam designs

# Generate reports
generator = PDFReportGenerator()
output_dir = Path('reports')
output_dir.mkdir(exist_ok=True)

for i, result in enumerate(beams, start=1):
    output_file = output_dir / f'beam_{i:02d}_calc.pdf'
    generator.generate_beam_report(
        result=result,
        output_file=str(output_file),
        project_info={'name': f'Beam B{i}'}
    )

print(f"Generated {len(beams)} reports in {output_dir}")
```

---

## 9. Cost-Benefit Analysis

### 9.1 Development Cost

| Phase | Effort | Timeline |
|-------|--------|----------|
| HTML Templates | 6-8 hours | Week 1 |
| PDF Generation | 4-5 hours | Week 1 |
| Excel Export | 3-4 hours | Week 2 |
| **Total** | **13-17 hours** | **2 weeks** |

### 9.2 Benefits

**Time Savings:**
- Manual report creation: 2-4 hours per beam
- Automated report: 5 seconds per beam
- **ROI:** Break-even after 4-8 beams

**Quality:**
- Consistent formatting
- No transcription errors
- Professional appearance
- Always up-to-date

**Compliance:**
- Includes all required elements
- Code references automatic
- Version tracking built-in

---

## 10. Recommendations

### 10.1 Immediate Actions (v0.16)

**Priority 1: PDF Generation** (10 hours)
- HTML template + CSS
- WeasyPrint integration
- Basic beam report
- **Why:** Most requested feature

**Priority 2: Template Customization** (3 hours)
- Company logo support
- Custom headers/footers
- **Why:** Professional appearance

### 10.2 Future Enhancements (v0.17+)

**Priority 3: Excel Export** (4 hours)
- Working calculations format
- **Why:** Engineering review needs

**Priority 4: More Report Types** (variable)
- Column design reports
- Slab design reports
- Foundation reports

### 10.3 Long-Term Vision

**Advanced Features:**
- Custom templates (user-defined)
- Multi-language support
- Interactive HTML reports
- Integration with project management systems

---

## Document Control

**Version History:**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-07 | Initial research complete (parts 1-2) | Research Team |

**Next Steps:**

1. Review with engineering team
2. Create implementation task (Phase 1: PDF)
3. Design template with sample data
4. Implement WeasyPrint integration
5. Test with real beam designs

---

**End of Document**
**Total Length:** Parts 1-2 combined ≈ 1300 lines
**Implementation Time:** 13-17 hours (2 weeks)
**Priority:** HIGH (requested feature, improves professional workflow)
**Dependencies:** weasyprint, jinja2, openpyxl
