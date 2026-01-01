# VBA API Reference

**Version:** 0.13.0
**Module:** M09_UDFs.bas
**Purpose:** Excel User-Defined Functions (UDFs) for worksheet calculations

All functions are prefixed with `IS456_` and available in any Excel worksheet once the add-in is loaded.

---

## Table of Contents

- [Core Design Functions](#core-design-functions)
- [Detailing Functions](#detailing-functions)
- [DXF Export Functions](#dxf-export-functions)
- [Error Handling](#error-handling)
- [Usage Examples](#usage-examples)

---

## Core Design Functions

### IS456_MuLim

**Description:** Calculates limiting moment of resistance for singly reinforced rectangular beam.

**Syntax:**
```vb
IS456_MuLim(b, d, fck, fy)
```

**Parameters:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| b | Double | mm | Beam width |
| d | Double | mm | Effective depth |
| fck | Double | N/mm² | Characteristic compressive strength of concrete |
| fy | Double | N/mm² | Yield strength of steel |

**Returns:** `Double` - Limiting moment in kN·m
**Reference:** IS 456 Cl 38.1

**Example:**
```excel
=IS456_MuLim(300, 450, 25, 500)    → 196.5 kN·m
```

---

### IS456_AstRequired

**Description:** Calculates required tension steel area for rectangular beam.

**Syntax:**
```vb
IS456_AstRequired(b, d, Mu_kNm, fck, fy)
```

**Parameters:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| b | Double | mm | Beam width |
| d | Double | mm | Effective depth |
| Mu_kNm | Double | kN·m | Applied factored moment |
| fck | Double | N/mm² | Characteristic compressive strength of concrete |
| fy | Double | N/mm² | Yield strength of steel |

**Returns:** `Variant` - Required steel area in mm² OR "Over-Reinforced" if Mu > Mu_lim
**Reference:** IS 456 Cl 38.1

**Example:**
```excel
=IS456_AstRequired(300, 450, 150, 25, 500)    → 882 mm²
=IS456_AstRequired(300, 450, 250, 25, 500)    → "Over-Reinforced"
```

---

### IS456_ShearSpacing

**Description:** Calculates required stirrup spacing for shear design.

**Syntax:**
```vb
IS456_ShearSpacing(Vu_kN, b, d, fck, fy, Asv, pt)
```

**Parameters:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| Vu_kN | Double | kN | Applied factored shear force |
| b | Double | mm | Beam width |
| d | Double | mm | Effective depth |
| fck | Double | N/mm² | Characteristic compressive strength of concrete |
| fy | Double | N/mm² | Yield strength of steel |
| Asv | Double | mm² | Area of stirrup legs (e.g., 2 legs of 8φ = 100mm²) |
| pt | Double | % | Tension steel percentage (100·Ast/bd) |

**Returns:** `Variant` - Spacing in mm OR "Unsafe: [reason]" if shear capacity exceeded
**Reference:** IS 456 Cl 40.4, Table 19

**Example:**
```excel
=IS456_ShearSpacing(100, 230, 450, 20, 415, 100, 1.0)    → 300 mm
=IS456_ShearSpacing(500, 230, 450, 20, 415, 100, 1.0)    → "Unsafe: Exceeds Tc_max"
```

---

### IS456_MuLim_Flanged

**Description:** Calculates limiting moment for flanged beams (T-beam or L-beam).

**Syntax:**
```vb
IS456_MuLim_Flanged(bw, bf, d, Df, fck, fy)
```

**Parameters:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| bw | Double | mm | Web width |
| bf | Double | mm | Effective flange width |
| d | Double | mm | Effective depth |
| Df | Double | mm | Flange thickness |
| fck | Double | N/mm² | Characteristic compressive strength of concrete |
| fy | Double | N/mm² | Yield strength of steel |

**Returns:** `Double` - Limiting moment in kN·m
**Reference:** IS 456 Cl 23.1.2, Annex G

**Example:**
```excel
=IS456_MuLim_Flanged(230, 1200, 500, 120, 25, 500)    → 387.2 kN·m
```

---

### IS456_Design_Rectangular

**Description:** Complete design of rectangular beam (singly or doubly reinforced). Returns array of results.

**Syntax:**
```vb
IS456_Design_Rectangular(b, d, d_dash, D_total, Mu_kNm, fck, fy)
```

**Parameters:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| b | Double | mm | Beam width |
| d | Double | mm | Effective depth (tension side) |
| d_dash | Double | mm | Effective cover to compression steel |
| D_total | Double | mm | Total beam depth |
| Mu_kNm | Double | kN·m | Applied factored moment |
| fck | Double | N/mm² | Characteristic compressive strength of concrete |
| fy | Double | N/mm² | Yield strength of steel |

**Returns:** `Array(1 to 4)` - [Ast_Required (mm²), Asc_Required (mm²), Xu (mm), Status]
**Status:** "Safe" or error message
**Reference:** IS 456 Cl 38.1

**Example:**
```excel
=IS456_Design_Rectangular(300, 450, 50, 500, 150, 25, 500)
  → [882, 0, 98.5, "Safe"]    (Singly reinforced)

=IS456_Design_Rectangular(300, 450, 50, 500, 250, 25, 500)
  → [1850, 420, 202.5, "Safe"]    (Doubly reinforced)
```

**Usage in Excel:** Select 4 adjacent cells (horizontal), enter formula, press Ctrl+Shift+Enter

---

### IS456_Design_Flanged

**Description:** Complete design of flanged beam (T-beam or L-beam). Returns array of results.

**Syntax:**
```vb
IS456_Design_Flanged(bw, bf, d, Df, D_total, Mu_kNm, fck, fy, [d_dash])
```

**Parameters:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| bw | Double | mm | Web width |
| bf | Double | mm | Effective flange width |
| d | Double | mm | Effective depth |
| Df | Double | mm | Flange thickness |
| D_total | Double | mm | Total beam depth |
| Mu_kNm | Double | kN·m | Applied factored moment |
| fck | Double | N/mm² | Characteristic compressive strength of concrete |
| fy | Double | N/mm² | Yield strength of steel |
| d_dash | Double | mm | Effective cover to compression steel (optional, default=50) |

**Returns:** `Array(1 to 4)` - [Ast_Required (mm²), Asc_Required (mm²), Xu (mm), Status]
**Reference:** IS 456 Cl 23.1, Annex G

**Example:**
```excel
=IS456_Design_Flanged(230, 1200, 500, 120, 550, 300, 25, 500, 50)
  → [1750, 0, 95.3, "Safe"]
```

---

### IS456_Tc

**Description:** Calculates design shear strength of concrete from IS 456 Table 19.

**Syntax:**
```vb
IS456_Tc(fck, pt)
```

**Parameters:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| fck | Double | N/mm² | Characteristic compressive strength of concrete |
| pt | Double | % | Tension steel percentage (100·Ast/bd) |

**Returns:** `Double` - Design shear strength τc in N/mm²
**Reference:** IS 456 Table 19

**Example:**
```excel
=IS456_Tc(25, 0.5)     → 0.48 N/mm²
=IS456_Tc(25, 1.0)     → 0.62 N/mm²
=IS456_Tc(40, 1.5)     → 0.79 N/mm²
```

---

### IS456_TcMax

**Description:** Returns maximum shear stress from IS 456 Table 20.

**Syntax:**
```vb
IS456_TcMax(fck)
```

**Parameters:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| fck | Double | N/mm² | Characteristic compressive strength of concrete |

**Returns:** `Double` - Maximum shear stress τc_max in N/mm²
**Reference:** IS 456 Table 20

**Example:**
```excel
=IS456_TcMax(15)    → 2.5 N/mm²
=IS456_TcMax(25)    → 3.1 N/mm²
=IS456_TcMax(40)    → 3.7 N/mm²
```

---

### IS456_Check_Ductility

**Description:** Checks beam compliance with IS 13920:2016 ductile detailing requirements.

**Syntax:**
```vb
IS456_Check_Ductility(b, D_overall, d, fck, fy, min_long_bar_dia)
```

**Parameters:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| b | Double | mm | Beam width |
| D_overall | Double | mm | Total beam depth |
| d | Double | mm | Effective depth |
| fck | Double | N/mm² | Characteristic compressive strength of concrete |
| fy | Double | N/mm² | Yield strength of steel |
| min_long_bar_dia | Double | mm | Smallest longitudinal bar diameter |

**Returns:** `String` - "Compliant" or detailed error message
**Reference:** IS 13920:2016 Cl 6.1-6.2

**Example:**
```excel
=IS456_Check_Ductility(230, 450, 400, 25, 500, 12)
  → "Compliant"

=IS456_Check_Ductility(150, 450, 400, 25, 500, 12)
  → "Width must be ≥200mm (IS 13920 Cl 6.1.1)"
```

---

## Detailing Functions

### IS456_Ld

**Description:** Calculates development length for reinforcement bars.

**Syntax:**
```vb
IS456_Ld(bar_dia, fck, fy, [bar_type])
```

**Parameters:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| bar_dia | Double | mm | Bar diameter |
| fck | Double | N/mm² | Characteristic compressive strength of concrete |
| fy | Double | N/mm² | Yield strength of steel |
| bar_type | String | - | "deformed" or "plain" (optional, default="deformed") |

**Returns:** `Double` - Development length in mm
**Reference:** IS 456 Cl 26.2.1

**Example:**
```excel
=IS456_Ld(16, 25, 500)               → 777 mm
=IS456_Ld(20, 25, 500)               → 971 mm
=IS456_Ld(16, 25, 500, "plain")      → 1166 mm
```

---

### IS456_LapLength

**Description:** Calculates lap length for reinforcement bars.

**Syntax:**
```vb
IS456_LapLength(bar_dia, fck, fy, [is_seismic], [in_tension])
```

**Parameters:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| bar_dia | Double | mm | Bar diameter |
| fck | Double | N/mm² | Characteristic compressive strength of concrete |
| fy | Double | N/mm² | Yield strength of steel |
| is_seismic | Boolean | - | TRUE for seismic zones (optional, default=FALSE) |
| in_tension | Boolean | - | TRUE for tension zone (optional, default=TRUE) |

**Returns:** `Double` - Lap length in mm
**Reference:** IS 456 Cl 26.2.5, IS 13920 Cl 6.2.5

**Example:**
```excel
=IS456_LapLength(16, 25, 500)                  → 777 mm (non-seismic, tension)
=IS456_LapLength(16, 25, 500, TRUE)            → 1554 mm (seismic, tension, 2×Ld)
=IS456_LapLength(16, 25, 500, FALSE, FALSE)    → 777 mm (non-seismic, compression)
```

---

### IS456_BondStress

**Description:** Returns design bond stress for bars.

**Syntax:**
```vb
IS456_BondStress(fck, [bar_type])
```

**Parameters:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| fck | Double | N/mm² | Characteristic compressive strength of concrete |
| bar_type | String | - | "deformed" or "plain" (optional, default="deformed") |

**Returns:** `Double` - Bond stress τbd in N/mm²
**Reference:** IS 456 Cl 26.2.1.1

**Example:**
```excel
=IS456_BondStress(25)                    → 1.6 N/mm² (deformed bars, M25)
=IS456_BondStress(25, "plain")           → 1.06 N/mm² (plain bars, M25)
```

---

### IS456_BarSpacing

**Description:** Calculates center-to-center spacing between bars in a layer.

**Syntax:**
```vb
IS456_BarSpacing(b, cover, stirrup_dia, bar_dia, bar_count)
```

**Parameters:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| b | Double | mm | Beam width |
| cover | Double | mm | Clear cover |
| stirrup_dia | Double | mm | Stirrup bar diameter |
| bar_dia | Double | mm | Main bar diameter |
| bar_count | Long | - | Number of bars in layer |

**Returns:** `Double` - Spacing in mm
**Reference:** IS 456 Cl 26.3

**Example:**
```excel
=IS456_BarSpacing(300, 25, 8, 16, 3)    → 107 mm
```

---

### IS456_CheckSpacing

**Description:** Checks if bar spacing meets minimum requirements.

**Syntax:**
```vb
IS456_CheckSpacing(spacing, bar_dia, [agg_size])
```

**Parameters:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| spacing | Double | mm | Actual spacing between bars |
| bar_dia | Double | mm | Bar diameter |
| agg_size | Double | mm | Maximum aggregate size (optional, default=20) |

**Returns:** `Boolean` - TRUE if adequate, FALSE if insufficient
**Reference:** IS 456 Cl 26.3.1

**Example:**
```excel
=IS456_CheckSpacing(100, 16, 20)    → TRUE (adequate)
=IS456_CheckSpacing(20, 16, 20)     → FALSE (insufficient)
```

**Minimum spacing:** max(bar_dia, agg_size + 5mm, 25mm)

---

### IS456_BarCount

**Description:** Calculates number of bars required for given steel area.

**Syntax:**
```vb
IS456_BarCount(ast_required, bar_dia)
```

**Parameters:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| ast_required | Double | mm² | Required steel area |
| bar_dia | Double | mm | Bar diameter |

**Returns:** `Long` - Number of bars (rounded up)
**Reference:** Practical detailing

**Example:**
```excel
=IS456_BarCount(882, 16)     → 5 bars (5×201=1005mm² > 882mm²)
=IS456_BarCount(882, 20)     → 3 bars (3×314=942mm² > 882mm²)
```

---

### IS456_BarCallout

**Description:** Formats bar callout text for drawings.

**Syntax:**
```vb
IS456_BarCallout(count, diameter)
```

**Parameters:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| count | Long | - | Number of bars |
| diameter | Double | mm | Bar diameter |

**Returns:** `String` - Formatted callout
**Reference:** SP 34 drawing standards

**Example:**
```excel
=IS456_BarCallout(3, 16)     → "3-16φ"
=IS456_BarCallout(5, 20)     → "5-20φ"
```

---

### IS456_StirrupCallout

**Description:** Formats stirrup callout text for drawings.

**Syntax:**
```vb
IS456_StirrupCallout(legs, diameter, spacing)
```

**Parameters:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| legs | Long | - | Number of stirrup legs (2 or 4) |
| diameter | Double | mm | Stirrup bar diameter |
| spacing | Double | mm | Stirrup spacing |

**Returns:** `String` - Formatted callout
**Reference:** SP 34 drawing standards

**Example:**
```excel
=IS456_StirrupCallout(2, 8, 150)     → "2L-8φ@150 c/c"
=IS456_StirrupCallout(4, 10, 100)    → "4L-10φ@100 c/c"
```

---

## DXF Export Functions

### IS456_DrawSection

**Description:** Generates beam cross-section DXF drawing with reinforcement.

**Syntax:**
```vb
IS456_DrawSection(filePath, B, D, cover, topBarsRange, bottomBarsRange, stirrupDia)
```

**Parameters:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| filePath | String | - | Full path to save DXF file (e.g., "C:\Beams\B1.dxf") |
| B | Double | mm | Beam width |
| D | Double | mm | Beam depth |
| cover | Double | mm | Clear cover |
| topBarsRange | Range | - | Excel range with top bar diameters (e.g., A1:A3) |
| bottomBarsRange | Range | - | Excel range with bottom bar diameters |
| stirrupDia | Double | mm | Stirrup diameter |

**Returns:** `Variant` - TRUE if successful, error message otherwise
**Reference:** Native VBA DXF R12 writer

**Example:**
```excel
=IS456_DrawSection("C:\Beams\B1_Section.dxf", 300, 500, 25, A1:A3, B1:B3, 8)
  → TRUE (DXF file created)
```

**Setup:**
- Cell A1:A3 = [16, 16, 16] (top bars)
- Cell B1:B3 = [20, 20, 20] (bottom bars)

---

### IS456_DrawLongitudinal

**Description:** Generates beam longitudinal section DXF drawing with stirrups.

**Syntax:**
```vb
IS456_DrawLongitudinal(filePath, length, D, cover, topBarDia, bottomBarDia, stirrupDia, stirrupSpacing)
```

**Parameters:**
| Parameter | Type | Unit | Description |
|-----------|------|------|-------------|
| filePath | String | - | Full path to save DXF file |
| length | Double | mm | Beam length |
| D | Double | mm | Beam depth |
| cover | Double | mm | Clear cover |
| topBarDia | Double | mm | Top bar diameter |
| bottomBarDia | Double | mm | Bottom bar diameter |
| stirrupDia | Double | mm | Stirrup diameter |
| stirrupSpacing | Double | mm | Stirrup spacing |

**Returns:** `Variant` - TRUE if successful, error message otherwise
**Reference:** Native VBA DXF R12 writer

**Example:**
```excel
=IS456_DrawLongitudinal("C:\Beams\B1_Long.dxf", 6000, 500, 25, 16, 20, 8, 150)
  → TRUE (DXF file created)
```

---

### IS456_ExportBeamDXF

**Description:** Exports complete beam detailing to DXF from worksheet data. This is a **macro** (Sub), not a worksheet function.

**Syntax:**
```vb
Sub IS456_ExportBeamDXF()
```

**Parameters:** None (reads from active worksheet)

**Returns:** Displays save dialog, generates DXF file

**Expected Worksheet Layout:**
| Cell | Value | Description |
|------|-------|-------------|
| B2 | BeamID | Beam identifier |
| B3 | Width | Beam width (mm) |
| B4 | Depth | Beam depth (mm) |
| B5 | Span | Beam span (mm) |
| B6 | Cover | Clear cover (mm) |
| B7 | Bottom bar count | Number of bottom bars |
| C7 | Bottom bar diameter | Diameter (mm) |
| B8 | Top bar count | Number of top bars |
| C8 | Top bar diameter | Diameter (mm) |
| B9 | Stirrup diameter | Stirrup dia (mm) |
| C9 | Stirrup spacing | Spacing (mm) |
| D9 | Stirrup legs | Number of legs (2 or 4) |

**Usage:**
1. Fill worksheet cells with beam data
2. Run macro from Developer tab or button
3. Choose save location in file dialog
4. DXF file created with cross-section, longitudinal view, and bar schedule

**Reference:** M16_DXF.bas

---

## Error Handling

All UDFs use consistent error handling:

**Error Return Values:**
- `#VALUE!` - Invalid input (wrong type, out of range, calculation error)
- String messages - Engineering errors (e.g., "Over-Reinforced", "Unsafe: Exceeds Tc_max")

**Common Causes:**
- Empty cells or non-numeric values
- Negative or zero dimensions
- Material grades outside IS 456 range (fck < 15 or > 60)
- Structural violations (Mu > Mu_lim without compression steel)

**Best Practices:**
```excel
' Check for errors before using result
=IF(ISERROR(IS456_MuLim(B2,C2,D2,E2)), "INPUT ERROR", IS456_MuLim(B2,C2,D2,E2))

' Handle string returns (e.g., "Over-Reinforced")
=IF(ISNUMBER(IS456_AstRequired(...)), IS456_AstRequired(...), 0)
```

---

## Usage Examples

### Example 1: Single Beam Design

**Worksheet setup:**
| Cell | Value | Description |
|------|-------|-------------|
| A1 | 300 | Beam width (mm) |
| B1 | 450 | Effective depth (mm) |
| C1 | 25 | fck (N/mm²) |
| D1 | 500 | fy (N/mm²) |
| E1 | 150 | Mu (kN·m) |

**Formulas:**
```excel
F1: =IS456_MuLim(A1, B1, C1, D1)                    → 196.5 kN·m (Mu_lim)
G1: =IS456_AstRequired(A1, B1, E1, C1, D1)          → 882 mm² (Ast)
H1: =IS456_BarCount(G1, 16)                         → 5 bars
I1: =IS456_BarCallout(H1, 16)                       → "5-16φ"
J1: =IS456_BarSpacing(A1, 25, 8, 16, H1)            → 42 mm
K1: =IS456_CheckSpacing(J1, 16, 20)                 → TRUE/FALSE
```

---

### Example 2: Batch Design Table

**Worksheet setup:**
| Row | BeamID | b | d | Mu | fck | fy | Mu_lim | Ast | BarCount | Callout | Status |
|-----|--------|---|---|----|----|----| -------|-----|----------|---------|--------|
| 1 | Headers | | | | | | | | | | |
| 2 | B-01 | 300 | 450 | 120 | 25 | 500 | `Formula` | `Formula` | `Formula` | `Formula` | `Formula` |
| 3 | B-02 | 300 | 450 | 180 | 25 | 500 | `Formula` | `Formula` | `Formula` | `Formula` | `Formula` |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Formulas (Row 2, copy down):**
```excel
G2: =IS456_MuLim(B2, C2, E2, F2)
H2: =IS456_AstRequired(B2, C2, D2, E2, F2)
I2: =IS456_BarCount(H2, 16)
J2: =IS456_BarCallout(I2, 16)
K2: =IF(D2<=G2, "Safe", "Over-Reinforced")
```

---

### Example 3: Complete Design with Shear

**Worksheet setup:**
| Cell | Value | Description |
|------|-------|-------------|
| B2 | 230 | b (mm) |
| B3 | 450 | d (mm) |
| B4 | 500 | D (mm) |
| B5 | 25 | fck |
| B6 | 500 | fy |
| B7 | 180 | Mu (kN·m) |
| B8 | 120 | Vu (kN) |
| B9 | 100 | Asv (mm², 2-leg 8φ stirrup) |

**Formulas:**
```excel
B11: =IS456_Design_Rectangular(B2, B3, 50, B4, B7, B5, B6)
     (Select B11:E11, enter formula, Ctrl+Shift+Enter)
     → [Ast, Asc, Xu, Status]

B12: =B11/201    ' Assuming 16φ bars, area = 201mm²
B13: =ROUNDUP(B12, 0)    ' Number of 16φ bars

B15: =100*B11/(B2*B3)    ' pt (%)
B16: =IS456_ShearSpacing(B8, B2, B3, B5, B6, B9, B15)
     → Stirrup spacing in mm

B17: =IS456_BarCallout(B13, 16)                     → Bottom bars
B18: =IS456_StirrupCallout(2, 8, B16)               → Stirrup callout
```

---

### Example 4: Flanged Beam (T-Beam)

**Worksheet setup:**
| Cell | Value | Description |
|------|-------|-------------|
| B2 | 230 | bw (mm) - web width |
| B3 | 1200 | bf (mm) - flange width |
| B4 | 500 | d (mm) |
| B5 | 120 | Df (mm) - flange thickness |
| B6 | 550 | D (mm) |
| B7 | 25 | fck |
| B8 | 500 | fy |
| B9 | 300 | Mu (kN·m) |

**Formulas:**
```excel
B11: =IS456_MuLim_Flanged(B2, B3, B4, B5, B7, B8)
     → Flanged Mu_lim

B12: =IS456_Design_Flanged(B2, B3, B4, B5, B6, B9, B7, B8, 50)
     (Select B12:E12, enter formula, Ctrl+Shift+Enter)
     → [Ast, Asc, Xu, Status]
```

---

### Example 5: Ductile Detailing Check

**Worksheet setup:**
| Cell | Value | Description |
|------|-------|-------------|
| B2 | 230 | b (mm) |
| B3 | 450 | D (mm) |
| B4 | 400 | d (mm) |
| B5 | 25 | fck |
| B6 | 500 | fy |
| B7 | 12 | Min bar diameter (mm) |

**Formula:**
```excel
B9: =IS456_Check_Ductility(B2, B3, B4, B5, B6, B7)
    → "Compliant" or error message
```

---

### Example 6: Development and Lap Lengths

**Worksheet setup:**
| Cell | Value | Description |
|------|-------|-------------|
| A1 | Bar Dia | Header |
| A2 | 12 | |
| A3 | 16 | |
| A4 | 20 | |
| A5 | 25 | |
| B1 | Ld (mm) | Header |
| C1 | Lap (mm) | Header |
| D1 | Lap Seismic (mm) | Header |

**Formulas:**
```excel
B2: =IS456_Ld(A2, 25, 500)               → Development length
C2: =IS456_LapLength(A2, 25, 500)        → Lap length (non-seismic)
D2: =IS456_LapLength(A2, 25, 500, TRUE)  → Lap length (seismic)

' Copy formulas down to rows 3-5
```

---

### Example 7: DXF Export from Worksheet

**Step 1:** Fill worksheet with beam data (see IS456_ExportBeamDXF layout above)

**Step 2:** Add button to worksheet:
1. Developer → Insert → Button (Form Control)
2. Draw button on worksheet
3. Assign macro: `IS456_ExportBeamDXF`
4. Rename button: "Export Beam to DXF"

**Step 3:** Click button
1. File save dialog appears
2. Choose location (e.g., "C:\Beams\B1_Detail.dxf")
3. DXF file created with:
   - Cross-section with rebar
   - Longitudinal view with stirrups
   - Bar schedule table

**Alternative:** Use formula-based export for cross-section only:
```excel
A10: =IS456_DrawSection("C:\Beams\Section.dxf", B3, B4, B6, B7:B9, C7:C9, B10)
```

---

## See Also

- [Excel Quickstart](../getting-started/excel-quickstart.md) - Installation and setup
- [Excel Tutorial](../getting-started/excel-tutorial.md) - Step-by-step guide
- [VBA Guide](../contributing/vba-guide.md) - Module architecture for developers
- [IS 456 Formulas](is456-formulas.md) - Code clause references
- [Known Pitfalls](known-pitfalls.md) - Common issues and solutions

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.13.0 | 2025-01 | Initial API reference document |
| 0.7.0 | 2024-06 | Added detailing and DXF functions |
| 0.5.0 | 2024-03 | Core design functions |

---

## Support

If a UDF returns `#VALUE!` or unexpected results:
1. Check input cell types (must be numeric)
2. Verify parameter units (mm, N/mm², kN, kN·m)
3. Test with simple values (e.g., `=IS456_MuLim(300, 450, 25, 500)`)
4. Check for circular references in worksheet
5. See [Known Pitfalls](known-pitfalls.md) for Mac VBA issues

For bugs or feature requests, see [CONTRIBUTING.md](../../CONTRIBUTING.md).
