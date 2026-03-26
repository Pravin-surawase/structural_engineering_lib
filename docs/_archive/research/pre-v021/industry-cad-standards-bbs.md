# Industry CAD Standards for Structural Engineering Deliverables

**Type:** Research
**Audience:** Developers
**Status:** Approved
**Importance:** Critical
**Created:** 2026-01-21
**Last Updated:** 2026-01-21
**Related Tasks:** TASK-PHASE3, DXF-EXPORT

---

## Executive Summary

This document consolidates industry standards for structural engineering CAD deliverables, focusing on:
1. **Bar Bending Schedule (BBS)** format per IS 2502
2. **Drawing organization** (plan, elevation, sections, details)
3. **Client expectations** vs **firm delivery formats**
4. **Batch export efficiency** (similar beams grouped)

**Key Finding:** Current implementation lacks industry-standard BBS table format and efficient grouping of similar beams.

---

## 1. Industry Standard Drawing Set Organization

### 1.1 Structural Drawing Hierarchy (Indian Practice)

| Drawing Type | Content | Scale | Priority |
|--------------|---------|-------|----------|
| **General Arrangement (GA)** | Floor plans with beam/column grid | 1:100 | Sheet 1 |
| **Beam Schedule** | Tabular summary of all beams | N/A | Sheet 2 |
| **Bar Bending Schedule** | Rebar quantities per IS 2502 | N/A | Sheet 3 |
| **Beam Details** | Individual beam drawings | 1:20 to 1:50 | Sheets 4+ |
| **Section Details** | Cross-sections at supports/midspan | 1:10 to 1:20 | With details |
| **Standard Details** | Typical hook shapes, lap details | 1:5 to 1:10 | Reference sheet |

### 1.2 Client Expectations (What They Need)

| Deliverable | Purpose | Format |
|-------------|---------|--------|
| **Beam Schedule Table** | Quick reference for quantities | Excel/PDF table |
| **BBS (Bar Bending Schedule)** | Procurement & fabrication | IS 2502 format |
| **Detail Drawings** | Construction reference | DXF/DWG/PDF |
| **Quantity Summary** | Cost estimation | Excel with totals |
| **Standard Details** | Typical construction notes | Attached to drawings |

### 1.3 What Firms Typically Deliver

**Minimum Package:**
1. Structural General Arrangement (GA) drawings
2. Beam schedule table
3. Bar bending schedule (IS 2502 format)
4. Typical beam details (1-2 sheets for unique types)

**Full Package (Large Projects):**
- All of minimum package, plus:
- Individual beam detail sheets
- Column schedule and details
- Slab reinforcement drawings
- Foundation details
- Standard details sheet

---

## 2. Bar Bending Schedule (BBS) Format - IS 2502

### 2.1 Standard BBS Table Columns (IS 2502:1963)

| Column | Header | Description | Example |
|--------|--------|-------------|---------|
| 1 | **Bar Mark** | Unique identifier | A1, A2, B1 |
| 2 | **Type/Shape** | Shape code per BS 8666 | 00 (straight), 11 (bent) |
| 3 | **Size (mm)** | Bar diameter | 12, 16, 20, 25 |
| 4 | **No. of Members** | Quantity of structural members | 5 |
| 5 | **No. in Each** | Bars per member | 4 |
| 6 | **Total No.** | Col 4 × Col 5 | 20 |
| 7 | **Length (mm)** | Cut length per bar | 6500 |
| 8 | **Shape Dimensions** | A, B, C, D, E, R values | A=500, B=200 |
| 9 | **Total Length (m)** | Col 6 × Col 7 / 1000 | 130.0 |
| 10 | **Weight (kg)** | Based on unit weight | 129.5 |

### 2.2 Shape Codes (BS 8666 / IS 2502)

| Code | Shape | Description |
|------|-------|-------------|
| 00 | Straight | No bends |
| 11 | L-shape | Single 90° bend |
| 21 | U-shape | Two 90° bends (stirrup) |
| 31 | Double bent | Cranked bar |
| 32 | Z-shape | Two opposite bends |
| 37 | Spiral | Helical reinforcement |
| 41 | Links | Closed stirrup with hooks |

### 2.3 Standard Unit Weights (Mild Steel)

| Diameter (mm) | Weight (kg/m) |
|---------------|---------------|
| 8 | 0.395 |
| 10 | 0.617 |
| 12 | 0.888 |
| 16 | 1.579 |
| 20 | 2.467 |
| 25 | 3.854 |
| 32 | 6.313 |

---

## 3. Beam Schedule Format (Industry Standard)

### 3.1 Beam Schedule Table Columns

| Column | Description | Example |
|--------|-------------|---------|
| **Beam ID** | Unique identifier | B1, B2, FB1 |
| **Story/Level** | Floor level | GF, 1F, 2F |
| **Span (mm)** | Clear span | 4500 |
| **Size (b×D)** | Width × Depth | 230×450 |
| **Top Steel** | At support | 3-T16 |
| **Bottom Steel** | At midspan | 4-T20 |
| **Stirrups** | Shear reinforcement | 8φ@150 c/c |
| **Remarks** | Special notes | Hanger bars, etc. |

### 3.2 Grouping Similar Beams (Efficiency)

**Industry Practice:** Group beams with identical:
- Cross-section size (b×D)
- Span (±100mm tolerance)
- Reinforcement arrangement
- Stirrup spacing

**Example Grouping:**
```
TYPE B1 (applies to: B1-GF, B1-1F, B1-2F, B3-GF)
Size: 230×450 mm, Span: 4500 mm
Bottom: 4-T20, Top: 3-T16, Stirrups: 8φ@150 c/c
```

This reduces 50 individual beams to 8-12 beam types typically.

---

## 4. Drawing Layout Standards

### 4.1 Sheet Sizes (ISO 216 / IS 10711)

| Size | Dimensions (mm) | Use Case |
|------|-----------------|----------|
| A0 | 841 × 1189 | Large projects, GA drawings |
| A1 | 594 × 841 | Standard details, schedules |
| A2 | 420 × 594 | Individual beam details |
| A3 | 297 × 420 | Small details, references |

### 4.2 Title Block Information (Required)

| Field | Description |
|-------|-------------|
| **Project Name** | Building/structure name |
| **Client Name** | Owner/developer |
| **Drawing Title** | e.g., "Beam Details - Level 1" |
| **Drawing Number** | Unique ID (e.g., STR-B-001) |
| **Revision** | Version (Rev A, Rev B) |
| **Date** | Issue date |
| **Scale** | 1:20, 1:50, etc. |
| **Designed By** | Engineer name |
| **Checked By** | Reviewer name |
| **Approved By** | Project lead |

### 4.3 Layer Organization (CAD Standard)

| Layer Name | Color | Content |
|------------|-------|---------|
| BEAM_OUTLINE | White (7) | Concrete outline |
| REBAR_MAIN | Red (1) | Main reinforcement |
| REBAR_STIRRUP | Green (3) | Shear reinforcement |
| DIMENSIONS | Cyan (4) | Dimension lines |
| TEXT | Yellow (2) | Labels, annotations |
| CENTERLINE | Magenta (6) | Centerlines |
| HIDDEN | Gray (8) | Hidden lines |
| BORDER | White (7) | Title block, border |
| HATCH | Gray (8) | Section hatching |

---

## 5. Recommendations for Our Implementation

### 5.1 Current Gaps

| Feature | Current State | Industry Standard |
|---------|---------------|-------------------|
| BBS Table | Basic format | IS 2502 full format |
| Beam Grouping | None | Group similar beams |
| Shape Codes | Not implemented | BS 8666 codes |
| Beam Schedule | Not in DXF | Tabular on drawing |
| Cut Lengths | Calculated but not shown | Required column |
| Weight Summary | Per bar only | Total per type |

### 5.2 Priority Improvements

1. **Add Beam Schedule Table to DXF** (HIGH)
   - Group similar beams
   - Show in tabular format on drawing

2. **Enhance BBS with Shape Codes** (HIGH)
   - Add IS 2502 shape codes
   - Include cut length calculations
   - Show hook/bend allowances

3. **Add Quantity Summary** (MEDIUM)
   - Total weight by diameter
   - Total length by diameter
   - Wastage allowance (3-5%)

4. **Improve Batch Export Efficiency** (HIGH)
   - Group beams by type before export
   - Generate one detail per beam type
   - Reference multiple beams in title

### 5.3 Implementation Approach

```python
# Proposed beam grouping logic
def group_similar_beams(beams: list[BeamDetailingResult]) -> dict[str, list[BeamDetailingResult]]:
    """Group beams by type (size + reinforcement)."""
    groups = {}
    for beam in beams:
        # Create type key from key characteristics
        type_key = f"{beam.b}x{beam.D}_{beam.bottom_bars[0].count}T{beam.bottom_bars[0].diameter}"
        if type_key not in groups:
            groups[type_key] = []
        groups[type_key].append(beam)
    return groups

# Proposed BBS format
class BBSEntry:
    bar_mark: str           # A1, A2, etc.
    shape_code: str         # 00, 11, 21, 41
    diameter: int           # mm
    no_of_members: int      # How many beams use this
    no_in_each: int         # Bars per beam
    total_no: int           # Total bars
    cut_length: float       # mm
    total_length: float     # m
    weight: float           # kg
```

---

## 6. Client Delivery Checklist

### 6.1 Minimum Viable Delivery

- [ ] Beam Schedule (Excel/table format)
- [ ] Bar Bending Schedule (IS 2502)
- [ ] Representative Beam Details (1 per type)
- [ ] Quantity Summary (total steel weight)

### 6.2 Professional Delivery

- [ ] All minimum items
- [ ] General Arrangement drawing reference
- [ ] Standard Details sheet (hooks, laps, bends)
- [ ] Revision history
- [ ] Design basis notes
- [ ] Material specifications

### 6.3 Export Formats Clients Accept

| Format | Use Case | Compatibility |
|--------|----------|---------------|
| **DXF** | CAD editing | AutoCAD, BricsCAD |
| **DWG** | Native AutoCAD | Best compatibility |
| **PDF** | Viewing, printing | Universal |
| **Excel** | Schedules, quantities | Universal |

---

## 7. References

1. **IS 2502:1963** - Code of practice for bending and fixing of bars for concrete reinforcement
2. **BS 8666:2020** - Specification for scheduling, dimensioning, bending and cutting of steel reinforcement
3. **IS 456:2000** - Plain and reinforced concrete code of practice
4. **ACI 315-99** - Details and Detailing of Concrete Reinforcement
5. **Standard CAD practices** - NCS (National CAD Standard) principles

---

## 8. Next Steps

1. Implement `group_similar_beams()` function
2. Add BBS table drawing to DXF export
3. Add beam schedule table to multi-beam export
4. Update batch export to use beam grouping
5. Add shape codes to BBS entries
