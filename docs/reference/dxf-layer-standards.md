# DXF Layer Standards & Drawing Conventions

**Version:** 0.13.0
**Module:** M16_DXF.bas
**DXF Format:** AutoCAD R12 (maximum compatibility)
**Reference:** IS 456:2000, SP 34:1987 (Drawing Practices for RC Structures)

This document defines CAD layer standards used in DXF drawings exported by the Structural Engineering Library.

---

## Table of Contents

- [Layer Definitions](#layer-definitions)
- [AutoCAD Color Index (ACI)](#autocad-color-index-aci)
- [Linetype Definitions](#linetype-definitions)
- [Drawing Types](#drawing-types)
- [Drawing Conventions](#drawing-conventions)
- [CAD Software Compatibility](#cad-software-compatibility)
- [Customization Guide](#customization-guide)

---

## Layer Definitions

All DXF exports use standardized layer names based on IS/SP 34 drawing practices for reinforced concrete structures.

| Layer Name | Color | Linetype | Purpose | Typical Entities |
|------------|-------|----------|---------|------------------|
| **BEAM_OUTLINE** | Cyan (4) | CONTINUOUS | Beam section boundary | Lines, Polylines |
| **REBAR_MAIN** | Red (1) | CONTINUOUS | Main reinforcement bars | Circles, Lines |
| **REBAR_STIRRUP** | Green (3) | CONTINUOUS | Stirrups and shear links | Polylines, Rectangles |
| **DIMENSIONS** | Yellow (2) | CONTINUOUS | Dimension lines and arrows | Lines, Text, Arrows |
| **TEXT_CALLOUT** | White (7) | CONTINUOUS | Bar callouts, labels, notes | Text |
| **CENTERLINE** | Magenta (6) | CENTER | Center lines (symmetry) | Lines |
| **COVER_LINE** | Blue (5) | DASHED | Clear cover lines | Lines, Rectangles |

**Additional Layers:**
- **Layer 0** - Default layer (White, CONTINUOUS) - Used for miscellaneous entities

---

## AutoCAD Color Index (ACI)

The library uses the AutoCAD Color Index (ACI) standard for consistent layer colors across all CAD software.

| ACI Number | Color | Usage |
|------------|-------|-------|
| 1 | **Red** | Main reinforcement (primary structural element) |
| 2 | **Yellow** | Dimensions and measurements |
| 3 | **Green** | Stirrups and secondary reinforcement |
| 4 | **Cyan** | Structural boundaries (beams, columns) |
| 5 | **Blue** | Cover lines and construction lines |
| 6 | **Magenta** | Centerlines and axes |
| 7 | **White** | Text, callouts, general annotation |
| 8 | **Gray** | Hatching and fill patterns |

**Why ACI?**
- Universal standard across all CAD software
- Consistent appearance in AutoCAD, BricsCAD, LibreCAD, QCAD
- Predictable printing colors when using CTB (color-dependent plot styles)

---

## Linetype Definitions

Three linetypes are used in DXF exports:

### CONTINUOUS
- **Appearance:** Solid line (———————)
- **Layers:** BEAM_OUTLINE, REBAR_MAIN, REBAR_STIRRUP, DIMENSIONS, TEXT_CALLOUT
- **Purpose:** Primary structural elements and annotation
- **Load Order:** Built-in linetype (always available)

### CENTER
- **Appearance:** Long dash - short dash (—— · —— · ——)
- **Layers:** CENTERLINE
- **Purpose:** Symmetry axes and centerlines
- **Load Order:** Standard linetype (loaded in DXF header)

### DASHED
- **Appearance:** Short dashes (— — — — —)
- **Layers:** COVER_LINE
- **Purpose:** Non-structural lines (clear cover, reference lines)
- **Load Order:** Standard linetype (loaded in DXF header)

**Note:** All linetypes are defined in the LTYPE table of the DXF file (no need to manually load them).

---

## Drawing Types

The library generates three types of structural drawings:

### 1. Beam Cross-Section

**Purpose:** Show rebar arrangement in section view

**Layers Used:**
- BEAM_OUTLINE (rectangle outline)
- REBAR_MAIN (circles for bar cross-sections)
- REBAR_STIRRUP (rectangle for stirrup outline)
- COVER_LINE (dashed rectangle for clear cover boundary)
- TEXT_CALLOUT (bar callouts, e.g., "3-16φ")
- DIMENSIONS (section dimensions: width × depth)

**Example:**
```
┌────────────────────────┐
│  ┌──────────────┐      │ ← COVER_LINE (dashed)
│  │  ● ● ● ●     │      │ ← REBAR_MAIN (top bars)
│  │              │      │ ← BEAM_OUTLINE
│  │              │      │
│  │  ● ● ● ●     │      │ ← REBAR_MAIN (bottom bars)
│  └──────────────┘      │ ← REBAR_STIRRUP
└────────────────────────┘
   ↑ 300mm ↑              ← DIMENSIONS
```

**Entities:**
- BEAM_OUTLINE: 1 polyline (closed rectangle)
- REBAR_MAIN: N circles (1 per bar)
- REBAR_STIRRUP: 1 polyline (stirrup outline)
- COVER_LINE: 1 polyline (dashed)
- TEXT_CALLOUT: 2-4 text labels
- DIMENSIONS: 2-4 dimension lines

---

### 2. Longitudinal Section

**Purpose:** Show main bars and stirrup spacing along beam length

**Layers Used:**
- BEAM_OUTLINE (beam profile)
- REBAR_MAIN (longitudinal bars)
- REBAR_STIRRUP (vertical stirrup lines)
- CENTERLINE (beam centerline)
- TEXT_CALLOUT (stirrup spacing labels)
- DIMENSIONS (span length)

**Example:**
```
           ──────── CENTERLINE (center) ────────
┌──────────────────────────────────────────────┐
│─────● ● ────────────────────────● ●─────────│ ← REBAR_MAIN (top)
│ ┊   ┊  ┊   ┊   ┊   ┊   ┊   ┊   ┊  ┊   ┊   │ ← REBAR_STIRRUP
│─────● ● ────────────────────────● ●─────────│ ← REBAR_MAIN (bottom)
└──────────────────────────────────────────────┘ ← BEAM_OUTLINE
 ↑ 150mm spacing ↑
```

**Entities:**
- BEAM_OUTLINE: 1 polyline (beam profile)
- REBAR_MAIN: 2N lines (top + bottom bars)
- REBAR_STIRRUP: N lines (vertical stirrups)
- CENTERLINE: 1 line (horizontal centerline)
- TEXT_CALLOUT: 3-5 labels (spacing zones)
- DIMENSIONS: 1 dimension (total span)

---

### 3. Beam Detailing (Combined View)

**Purpose:** Complete detailing with cross-section + longitudinal + bar schedule

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│ TITLE BLOCK (TEXT_CALLOUT)                          │
│ Beam ID: B1 | Size: 300×500 | Span: 4000mm         │
├─────────────────────────────────────────────────────┤
│                                                      │
│ [Cross-Section]     [Longitudinal Section]          │
│                                                      │
├─────────────────────────────────────────────────────┤
│ BAR BENDING SCHEDULE (TEXT_CALLOUT)                 │
│ Mark  Dia  No.  Length  Weight                      │
│ A1    20   4    3950    9.88kg                      │
│ B1    16   3    2000    4.74kg                      │
│ S1    8    30   1300    3.21kg                      │
└─────────────────────────────────────────────────────┘
```

**Combines all three drawing types in a single layout**

---

## Drawing Conventions

### Units
- **Drawing Units:** Millimeters (mm)
- **Scale:** 1:1 (1 DXF unit = 1 mm in real world)
- **Coordinate System:** Cartesian (X=horizontal, Y=vertical)
- **Origin:** Bottom-left corner of drawing (0, 0)

### Text
- **Layer:** TEXT_CALLOUT
- **Height:** 3.5mm (standard annotation height)
- **Font:** STANDARD (built-in AutoCAD font)
- **Alignment:** Left-justified (horizontal), baseline (vertical)
- **Rotation:** 0° (horizontal text)

### Dimensions
- **Layer:** DIMENSIONS
- **Extension Line Overhang:** 1.25mm
- **Arrow Size:** 2.5mm
- **Text Height:** 3.5mm
- **Precision:** 0 decimal places (integer mm)

### Bar Symbols
- **Reinforcement Bars:** Circles (filled) with diameter = bar diameter
  - 12mm bar → 12mm diameter circle
  - 16mm bar → 16mm diameter circle
  - 20mm bar → 20mm diameter circle
- **Stirrups:** Rectangles (unfilled polylines)

### Callout Format
- **Main Bars:** `3-16φ` (count - diameter - phi symbol)
- **Stirrups:** `2L-8φ@150 c/c` (legs - diameter - spacing)
- **Position:** Near relevant rebar group (3mm offset)

---

## CAD Software Compatibility

### Tested CAD Software

| Software | Version | Compatibility | Notes |
|----------|---------|---------------|-------|
| **AutoCAD** | R12+ | ✅ Full | Native DXF R12 format |
| **AutoCAD LT** | 2000+ | ✅ Full | Full feature support |
| **BricsCAD** | V19+ | ✅ Full | Native DXF support |
| **LibreCAD** | 2.1+ | ✅ Full | Open-source, free |
| **QCAD** | 3.0+ | ✅ Full | Free/paid versions |
| **DraftSight** | 2019+ | ✅ Full | Dassault Systèmes |
| **FreeCAD** | 0.19+ | ⚠️ Partial | Some text formatting issues |
| **Inkscape** | 1.0+ | ⚠️ View Only | Can view, cannot edit |

**Compatibility Notes:**
- DXF R12 format ensures compatibility with CAD software from 1992+
- All standard linetypes (CONTINUOUS, CENTER, DASHED) are universally supported
- ACI colors render consistently across all platforms
- Text may appear different depending on font availability

### Opening in CAD Software

**AutoCAD / AutoCAD LT / BricsCAD:**
1. File → Open → Select DXF file
2. All layers load automatically
3. Use ZOOM EXTENTS (type `Z` → `E` → Enter) to view full drawing

**LibreCAD / QCAD:**
1. File → Open → Select DXF file
2. Layers panel shows all structural layers
3. View → Zoom Auto to fit drawing

**FreeCAD:**
1. File → Import → Select DXF file
2. Choose "Import" mode (not "Open as project")
3. Layers appear in Tree View

---

## Customization Guide

### For VBA Developers

If you need to customize layer properties (colors, linetypes), modify constants in `M16_DXF.bas`:

```vb
' Change layer colors (M16_DXF.bas, lines 59-65)
Public Const LAYER_BEAM_OUTLINE As String = "BEAM_OUTLINE"
Public Const LAYER_REBAR_MAIN As String = "REBAR_MAIN"
' ... etc

' Change layer definitions (M16_DXF.bas, WriteLayerTable subroutine)
Call WriteLayerDef LAYER_BEAM_OUTLINE, ACI_CYAN, "CONTINUOUS"
Call WriteLayerDef LAYER_REBAR_MAIN, ACI_RED, "CONTINUOUS"
' ... etc
```

**Example: Change main rebar color from Red to Blue:**
```vb
' In WriteLayerTable subroutine (line 271)
' OLD:
Call WriteLayerDef LAYER_REBAR_MAIN, ACI_RED, "CONTINUOUS"

' NEW:
Call WriteLayerDef LAYER_REBAR_MAIN, ACI_BLUE, "CONTINUOUS"
```

### For CAD Users

If you want to change layer properties after export:

**AutoCAD / BricsCAD:**
1. Type `LAYER` or `LA` → Enter
2. Select layer (e.g., REBAR_MAIN)
3. Click color swatch → Choose new color
4. Click linetype → Choose new linetype
5. OK to apply

**LibreCAD:**
1. View → Layer List
2. Double-click layer name
3. Modify color, linetype, lineweight
4. OK to apply

**Save as Template:**
- After customizing layers, save as DXF template
- Reuse for future drawings

---

## Layer Management Best Practices

### For Viewing
- **Turn layers ON/OFF** to focus on specific elements:
  - OFF: COVER_LINE, CENTERLINE (declutter view)
  - ON: BEAM_OUTLINE, REBAR_MAIN, REBAR_STIRRUP (core elements)

### For Printing
- **Freeze layers** not needed for print output:
  - Freeze: COVER_LINE (construction lines)
  - Keep: BEAM_OUTLINE, REBAR_MAIN, REBAR_STIRRUP, TEXT_CALLOUT

### For Editing
- **Lock layers** to prevent accidental modification:
  - Lock: TEXT_CALLOUT (preserve annotations)
  - Unlock: REBAR_MAIN (allow bar position adjustments)

---

## Drawing Standards Compliance

### IS/SP 34 Drawing Practices

The layer standards follow Indian Standard drawing practices for reinforced concrete:

- **SP 34:1987** - Handbook on Concrete Reinforcement and Detailing
  - Section 5: Drawing Conventions
  - Section 6: Bar Bending Schedules
  - Appendix A: Standard Symbols

**Compliance Points:**
- ✅ Red color for main reinforcement (SP 34 convention)
- ✅ Green color for stirrups (SP 34 convention)
- ✅ Bar callout format: `3-16φ` (SP 34 Clause 6.2)
- ✅ Stirrup notation: `2L-8φ@150 c/c` (SP 34 Clause 6.3)
- ✅ Section line conventions (SP 34 Appendix A)

### International CAD Standards

- **ISO 128** - Technical Drawings (linetype conventions)
- **ISO 13567** - CAD Layers (layer naming)
- **AutoCAD DXF R12** - Maximum compatibility

---

## Troubleshooting

### Issue: Layers not visible after opening DXF

**Solutions:**
1. **Check layer status:**
   - All layers should be ON and THAWED
   - Use `LAYON` command to turn all layers on
   - Use `LAYUNLCK` to unlock all layers

2. **Zoom to extents:**
   - Type `ZOOM` → `E` → Enter
   - Or use View menu → Zoom → Extents

3. **Check color settings:**
   - White layers may not be visible on white background
   - Switch to black background: OPTIONS → Display → Colors

---

### Issue: Linetypes not showing correctly

**Solutions:**
1. **Linetype scale too large:**
   - Type `LTSCALE` → Enter
   - Set value to 1.0 (default)

2. **Regenerate drawing:**
   - Type `REGEN` → Enter
   - Forces redraw with correct linetypes

---

### Issue: Text appears garbled or missing

**Solutions:**
1. **Font not installed:**
   - DXF uses STANDARD font (built-in)
   - If missing, AutoCAD substitutes with default font

2. **Text height too small:**
   - Use ZOOM to magnify text
   - Or change text height to 3.5mm minimum

---

## See Also

- [VBA API Reference](vba-api-reference.md) - DXF export functions
- [Excel Tutorial - Part 7](../getting-started/excel-tutorial.md#part-7-export-to-dxf) - Using DXF export
- [BBS & DXF Contract](bbs-dxf-contract.md) - BBS and DXF specifications
- [M16_DXF.bas](../../VBA/Modules/M16_DXF.bas) - Source code

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.13.0 | 2026-01 | Initial layer standards document |
| 0.8.0 | 2024-07 | Native VBA DXF R12 writer implemented |
| 0.7.0 | 2024-06 | Layer standards defined in M16_DXF.bas |

---

## Quick Reference Card

### Layer Quick Reference

| Element | Layer | Color Code | Turn Off for Print? |
|---------|-------|------------|---------------------|
| Beam outline | BEAM_OUTLINE | Cyan (4) | No |
| Main bars | REBAR_MAIN | Red (1) | No |
| Stirrups | REBAR_STIRRUP | Green (3) | No |
| Dimensions | DIMENSIONS | Yellow (2) | No |
| Callouts | TEXT_CALLOUT | White (7) | No |
| Centerlines | CENTERLINE | Magenta (6) | Optional |
| Cover lines | COVER_LINE | Blue (5) | Yes (construction lines) |

### CAD Commands Cheat Sheet

| Task | AutoCAD Command | LibreCAD Equivalent |
|------|-----------------|---------------------|
| Zoom to fit | `ZOOM` → `E` | View → Zoom Auto |
| Layer manager | `LAYER` or `LA` | View → Layer List |
| Turn layer on/off | `LAYON` / `LAYOFF` | Right-click layer → Toggle |
| Freeze layer | `LAYFRZ` | Right-click → Freeze |
| Change layer color | `LAYER` → Select → Color | Double-click layer → Color |
| Regenerate drawing | `REGEN` | View → Redraw |

---

*Document Version: 0.13.0 | Last Updated: 2026-01-01*
