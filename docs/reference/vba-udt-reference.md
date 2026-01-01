# VBA User-Defined Types (UDT) Reference

**Version:** 0.13.0
**Modules:** M02_Types.bas, M10_Ductile.bas
**Purpose:** Technical reference for VBA data structures

This document describes all custom data types (UDTs) and enumerations used in the Structural Engineering Library VBA implementation.

---

## Table of Contents

- [Enumerations](#enumerations)
- [Core Design Types](#core-design-types)
- [Serviceability Types](#serviceability-types)
- [Detailing Types](#detailing-types)
- [Bar Bending Schedule Types](#bar-bending-schedule-types)
- [Ductile Detailing Types](#ductile-detailing-types)
- [Usage Examples](#usage-examples)

---

## Enumerations

### BeamType

**Module:** M02_Types.bas
**Purpose:** Identifies beam cross-section geometry

| Value | Name | Description |
|-------|------|-------------|
| 1 | Rectangular | Rectangular section (width × depth) |
| 2 | Flanged_T | T-beam with flange on one side (monolithic slab) |
| 3 | Flanged_L | L-beam with flange on one side (edge beam) |

**Usage:**
```vb
Dim beamType As BeamType
beamType = Rectangular  ' Or Flanged_T, Flanged_L
```

**Reference:** Used internally for section classification

---

### DesignSectionType

**Module:** M02_Types.bas
**Purpose:** Classifies reinforcement design category

| Value | Name | Description |
|-------|------|-------------|
| 1 | UnderReinforced | Xu < Xu_max (singly reinforced, ductile failure) |
| 2 | Balanced | Xu = Xu_max (theoretical limit) |
| 3 | OverReinforced | Xu > Xu_max (requires compression steel) |

**Usage:**
```vb
Dim result As FlexureResult
result = M06_Flexure.Design_Singly_Reinforced(...)
If result.SectionType = UnderReinforced Then
    ' Safe, singly reinforced design
ElseIf result.SectionType = OverReinforced Then
    ' Needs doubly reinforced design
End If
```

**Reference:** IS 456 Cl 38.1

---

### SupportCondition

**Module:** M02_Types.bas (v0.8+)
**Purpose:** Beam support type for deflection checks

| Value | Name | Description |
|-------|------|-------------|
| 1 | Cantilever | Fixed at one end, free at other |
| 2 | SimplySupported | Simply supported at both ends |
| 3 | Continuous | Continuous over multiple supports |

**Usage:**
```vb
Dim support As SupportCondition
support = SimplySupported  ' Or Cantilever, Continuous
```

**Reference:** IS 456 Cl 23.2 (span/depth ratios vary by support type)

---

### ExposureClass

**Module:** M02_Types.bas (v0.8+)
**Purpose:** Environmental exposure for crack width limits

| Value | Name | Description | Max Crack Width |
|-------|------|-------------|-----------------|
| 1 | Mild | Interior, protected | 0.3 mm |
| 2 | Moderate | Sheltered exterior | 0.3 mm |
| 3 | Severe | Exposed to weather | 0.2 mm |
| 4 | VerySevere | Coastal/industrial | 0.1 mm (special case) |

**Usage:**
```vb
Dim exposure As ExposureClass
exposure = Moderate  ' Sets crack width limit = 0.3mm
```

**Reference:** IS 456 Cl 35.3 (Table 12A)

---

## Core Design Types

### FlexureResult

**Module:** M02_Types.bas
**Purpose:** Returns flexural design calculations

**Fields:**

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| Mu_Lim | Double | kN·m | Limiting moment of resistance (Mu_lim) |
| Ast_Required | Double | mm² | Required tension steel area |
| Asc_Required | Double | mm² | Required compression steel area (0 if singly reinforced) |
| Pt_Provided | Double | % | Percentage of steel provided (100·Ast/bd) |
| SectionType | DesignSectionType | - | UnderReinforced / Balanced / OverReinforced |
| Xu | Double | mm | Depth of neutral axis |
| Xu_max | Double | mm | Maximum depth of neutral axis (Xu_max/d limit) |
| IsSafe | Boolean | - | TRUE if design is valid, FALSE if failure |
| ErrorMessage | String | - | Error description if IsSafe = FALSE |

**Usage Example:**
```vb
Dim result As FlexureResult
result = M06_Flexure.Design_Singly_Reinforced(b:=300, d:=450, Mu_kNm:=150, fck:=25, fy:=500)

If result.IsSafe Then
    Debug.Print "Ast required: " & result.Ast_Required & " mm²"
    Debug.Print "Section type: " & result.SectionType  ' 1=UnderReinforced
    Debug.Print "Xu/d ratio: " & result.Xu / 450
Else
    Debug.Print "Design failed: " & result.ErrorMessage
End If
```

**Reference:** IS 456 Cl 38.1

---

### ShearResult

**Module:** M02_Types.bas
**Purpose:** Returns shear design calculations

**Fields:**

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| Tv | Double | N/mm² | Nominal shear stress (Vu / bd) |
| Tc | Double | N/mm² | Design shear strength of concrete (Table 19) |
| Tc_max | Double | N/mm² | Maximum shear stress limit (Table 20) |
| Vus | Double | kN | Shear capacity of stirrups |
| Spacing | Double | mm | Calculated stirrup spacing |
| IsSafe | Boolean | - | TRUE if Tv ≤ Tc_max, FALSE if shear failure |
| Remarks | String | - | Design remarks (e.g., "Min Shear Reinforcement") |

**Usage Example:**
```vb
Dim result As ShearResult
result = M07_Shear.Design_Shear(Vu_kN:=100, b:=230, d:=450, fck:=20, fy:=415, Asv:=100, pt:=1.0)

If result.IsSafe Then
    Debug.Print "Required spacing: " & result.Spacing & " mm"
    Debug.Print "Tv/Tc ratio: " & result.Tv / result.Tc  ' Should be > 1.0 for stirrups
Else
    Debug.Print "Unsafe: " & result.Remarks  ' e.g., "Exceeds Tc_max"
End If
```

**Reference:** IS 456 Cl 40, Table 19, Table 20

---

## Serviceability Types

### DeflectionResult

**Module:** M02_Types.bas (v0.8+)
**Purpose:** Returns deflection control checks

**Fields:**

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| IsOK | Boolean | - | TRUE if L/D ratio within limit |
| Remarks | String | - | Pass/fail message |
| Support | SupportCondition | - | Support type (Cantilever / SimplySupported / Continuous) |
| LD_Ratio | Double | - | Actual span/depth ratio (L/D) |
| Allowable_LD | Double | - | Allowable L/D with all modification factors |
| BaseAllowable_LD | Double | - | Base allowable L/D (before modification) |
| MF_TensionSteel | Double | - | Modification factor for tension steel % |
| MF_CompressionSteel | Double | - | Modification factor for compression steel |
| MF_Flanged | Double | - | Modification factor for flanged beams (1.0 for rectangular) |
| Assumptions | String | - | Notes on calculation assumptions |

**Usage Example:**
```vb
Dim result As DeflectionResult
result = M17_Serviceability.Check_Deflection_Level_A( _
    support:=SimplySupported, span_mm:=4000, D_mm:=300, _
    b_mm:=230, d_mm:=250, Ast_mm2:=800, Asc_mm2:=0, fck_nmm2:=25, fy_nmm2:=500)

If result.IsOK Then
    Debug.Print "Deflection OK: L/D = " & result.LD_Ratio & " ≤ " & result.Allowable_LD
Else
    Debug.Print "Deflection Fail: " & result.Remarks
End If
```

**Reference:** IS 456 Cl 23.2

---

### CrackWidthResult

**Module:** M02_Types.bas (v0.8+)
**Purpose:** Returns crack width calculations

**Fields:**

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| IsOK | Boolean | - | TRUE if Wcr ≤ limit for exposure class |
| Remarks | String | - | Pass/fail message |
| Exposure | ExposureClass | - | Exposure class (Mild / Moderate / Severe) |
| Wcr_mm | Double | mm | Calculated crack width |
| Limit_mm | Double | mm | Allowable crack width for exposure class |
| Acr_mm | Double | mm² | Area of concrete in tension (intermediate calc) |
| Cmin_mm | Double | mm | Minimum cover to reinforcement |
| h_mm | Double | mm | Overall depth of member |
| x_mm | Double | mm | Depth to neutral axis |
| Epsilon_m | Double | - | Average strain in tension zone |
| Denom | Double | - | Denominator in crack width formula |
| Assumptions | String | - | Notes on calculation |

**Usage Example:**
```vb
Dim result As CrackWidthResult
result = M17_Serviceability.Calculate_Crack_Width( _
    exposure:=Moderate, h_mm:=500, x_mm:=180, d_mm:=450, _
    cmin_mm:=40, fs_nmm2:=200, Es_nmm2:=200000, acr_mm2:=15000)

If result.IsOK Then
    Debug.Print "Crack width OK: " & result.Wcr_mm & " mm ≤ " & result.Limit_mm & " mm"
Else
    Debug.Print "Crack width exceeded: " & result.Remarks
End If
```

**Reference:** IS 456 Cl 35.3.2

---

## Detailing Types

### BarArrangement

**Module:** M02_Types.bas (v0.7+)
**Purpose:** Describes reinforcement bars in a single zone/location

**Fields:**

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| count | Long | - | Number of bars (e.g., 3, 4, 5) |
| diameter | Double | mm | Bar diameter (e.g., 12, 16, 20, 25) |
| area_provided | Double | mm² | Total area provided (count × π × dia²/4) |
| spacing | Double | mm | Center-to-center spacing between bars |
| layers | Long | - | Number of layers (1 or 2) |

**Usage Example:**
```vb
Dim bottomBars As BarArrangement
bottomBars.count = 4
bottomBars.diameter = 20
bottomBars.area_provided = 4 * 3.14159 * 20 * 20 / 4  ' 1256 mm²
bottomBars.spacing = 80  ' mm
bottomBars.layers = 1
```

**Reference:** Practical detailing

---

### StirrupArrangement

**Module:** M02_Types.bas (v0.7+)
**Purpose:** Describes stirrups in a beam zone

**Fields:**

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| diameter | Double | mm | Stirrup bar diameter (typically 8, 10, 12mm) |
| legs | Long | - | Number of stirrup legs (2 for 1 stirrup, 4 for 2 stirrups) |
| spacing | Double | mm | Stirrup spacing (c/c distance) |
| zone_length | Double | mm | Length of zone with this spacing |

**Usage Example:**
```vb
Dim stirrups As StirrupArrangement
stirrups.diameter = 8      ' 8mm bars
stirrups.legs = 2          ' 2-legged stirrup
stirrups.spacing = 150     ' 150mm c/c
stirrups.zone_length = 1200  ' 1200mm zone
```

**Reference:** IS 456 Cl 26.5, IS 13920 Cl 6.3

---

### BeamDetailingResult

**Module:** M02_Types.bas (v0.7+)
**Purpose:** Complete detailing for one beam

**Fields:**

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| beam_id | String | - | Beam identifier (e.g., "B1", "GB-01") |
| story | String | - | Story identifier (e.g., "GF", "1F", "2F") |
| b | Double | mm | Beam width |
| D | Double | mm | Beam depth |
| span | Double | mm | Span length |
| cover | Double | mm | Clear cover to main bars |
| bottom_start | BarArrangement | - | Bottom bars at start support |
| bottom_mid | BarArrangement | - | Bottom bars at mid-span |
| bottom_end | BarArrangement | - | Bottom bars at end support |
| top_start | BarArrangement | - | Top bars at start support |
| top_mid | BarArrangement | - | Top bars at mid-span |
| top_end | BarArrangement | - | Top bars at end support |
| stirrup_start | StirrupArrangement | - | Stirrups near start support |
| stirrup_mid | StirrupArrangement | - | Stirrups at mid-span |
| stirrup_end | StirrupArrangement | - | Stirrups near end support |
| ld_tension | Double | mm | Development length for tension bars |
| ld_compression | Double | mm | Development length for compression bars |
| lap_length | Double | mm | Lap splice length |
| is_valid | Boolean | - | TRUE if detailing is valid |
| remarks | String | - | Notes or errors |

**Usage Example:**
```vb
Dim detailing As BeamDetailingResult

' Populate fields
detailing.beam_id = "B1"
detailing.b = 300
detailing.D = 500
detailing.span = 4000
detailing.cover = 40

' Bottom bars (tension at mid-span)
detailing.bottom_mid.count = 4
detailing.bottom_mid.diameter = 20
detailing.bottom_mid.area_provided = 1256

' Top bars (compression at mid, tension at supports)
detailing.top_start.count = 3
detailing.top_start.diameter = 16

' Stirrups
detailing.stirrup_mid.diameter = 8
detailing.stirrup_mid.spacing = 150
detailing.stirrup_mid.legs = 2

' Development lengths
detailing.ld_tension = 752  ' mm
detailing.ld_compression = 600  ' mm

detailing.is_valid = True
```

**Used By:** M15_Detailing, M16_DXF, M18_BBS

---

## Bar Bending Schedule Types

### BBSLineItem

**Module:** M02_Types.bas (v0.9+)
**Purpose:** Single line item in a Bar Bending Schedule

**Fields:**

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| bar_mark | String | - | Unique bar identifier (e.g., "A1", "B1", "S1") |
| member_id | String | - | Beam/element ID (e.g., "B1", "GB-01") |
| location | String | - | "bottom", "top", "stirrup" |
| zone | String | - | "start", "mid", "end", "full" |
| shape_code | String | - | Shape per IS 2502 (A, B, C, D, E, F, etc.) |
| diameter_mm | Double | mm | Bar diameter |
| no_of_bars | Long | - | Quantity (number of bars) |
| cut_length_mm | Double | mm | Single bar cut length (including hooks/bends) |
| total_length_mm | Double | mm | Total length (no_of_bars × cut_length_mm) |
| unit_weight_kg | Double | kg | Weight per bar |
| total_weight_kg | Double | kg | Total weight (no_of_bars × unit_weight_kg) |
| remarks | String | - | Additional notes |

**Usage Example:**
```vb
Dim item As BBSLineItem

item.bar_mark = "A1"
item.member_id = "B1"
item.location = "bottom"
item.zone = "mid"
item.shape_code = "A"  ' Straight bar with hooks
item.diameter_mm = 20
item.no_of_bars = 4
item.cut_length_mm = 3950  ' mm (includes hooks)
item.total_length_mm = 4 * 3950  ' 15800 mm
item.unit_weight_kg = 2.47  ' kg (20mm bar, 3.95m long)
item.total_weight_kg = 4 * 2.47  ' 9.88 kg
item.remarks = "Mid-span bottom bars"
```

**Reference:** IS 2502:1999 (Bar Bending Schedule)

---

### BBSSummary

**Module:** M02_Types.bas (v0.9+)
**Purpose:** Summary totals for Bar Bending Schedule

**Fields:**

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| member_id | String | - | Beam/element ID |
| total_items | Long | - | Number of distinct bar marks |
| total_bars | Long | - | Total number of individual bars |
| total_length_m | Double | m | Total length in meters |
| total_weight_kg | Double | kg | Total weight in kilograms |

**Usage Example:**
```vb
Dim summary As BBSSummary

summary.member_id = "B1"
summary.total_items = 5     ' 5 different bar marks (A1, A2, B1, B2, S1)
summary.total_bars = 20     ' 20 individual bars total
summary.total_length_m = 45.3  ' 45.3 meters total
summary.total_weight_kg = 35.7  ' 35.7 kg total

Debug.Print "Beam " & summary.member_id & " requires " & summary.total_weight_kg & " kg of steel"
```

**Used By:** M18_BBS

---

## Ductile Detailing Types

### DuctileBeamResult

**Module:** M10_Ductile.bas
**Purpose:** Returns IS 13920 ductile detailing check results

**Fields:**

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| IsGeometryValid | Boolean | - | TRUE if b ≥ 200mm and b/D ≥ 0.3 |
| MinPt | Double | % | Minimum tension steel % (0.24√fck / fy) |
| MaxPt | Double | % | Maximum steel % (2.5% for ductile) |
| ConfinementSpacing | Double | mm | Max confinement spacing (min of d/4, 8db, 100mm) |
| Remarks | String | - | Compliance message or error |

**Usage Example:**
```vb
Dim result As DuctileBeamResult
result = M10_Ductile.Check_Beam_Ductility(b:=230, D_overall:=450, d:=400, _
                                          fck:=25, fy:=500, min_long_bar_dia:=12)

If result.IsGeometryValid Then
    Debug.Print "Min steel %: " & result.MinPt  ' 0.24%
    Debug.Print "Max steel %: " & result.MaxPt  ' 2.5%
    Debug.Print "Confinement spacing: " & result.ConfinementSpacing  ' 100mm
    Debug.Print result.Remarks  ' "Compliant"
Else
    Debug.Print "Non-compliant: " & result.Remarks
End If
```

**Reference:** IS 13920:2016 Cl 6.1, 6.2

---

## Usage Examples

### Example 1: Complete Flexure + Shear Design

```vb
Sub DesignBeam()
    Dim flexResult As FlexureResult
    Dim shearResult As ShearResult

    ' Input data
    Dim b As Double: b = 300
    Dim d As Double: d = 450
    Dim D As Double: D = 500
    Dim Mu_kNm As Double: Mu_kNm = 150
    Dim Vu_kN As Double: Vu_kN = 100
    Dim fck As Double: fck = 25
    Dim fy As Double: fy = 500

    ' Flexure design
    flexResult = M06_Flexure.Design_Singly_Reinforced(b, d, Mu_kNm, fck, fy)

    If flexResult.IsSafe Then
        Debug.Print "Ast required: " & flexResult.Ast_Required & " mm²"

        ' Calculate steel percentage for shear
        Dim pt As Double
        pt = (flexResult.Ast_Required / (b * d)) * 100

        ' Shear design (assuming 2-leg 8mm stirrup, Asv = 100mm²)
        shearResult = M07_Shear.Design_Shear(Vu_kN, b, d, fck, fy, Asv:=100, pt:=pt)

        If shearResult.IsSafe Then
            Debug.Print "Stirrup spacing: " & shearResult.Spacing & " mm"
        Else
            Debug.Print "Shear unsafe: " & shearResult.Remarks
        End If
    Else
        Debug.Print "Flexure unsafe: " & flexResult.ErrorMessage
    End If
End Sub
```

---

### Example 2: Detailing with Bar Arrangement

```vb
Sub CreateBeamDetailing()
    Dim detailing As BeamDetailingResult

    ' Basic geometry
    detailing.beam_id = "GB-01"
    detailing.b = 300
    detailing.D = 500
    detailing.span = 5000
    detailing.cover = 40

    ' Bottom bars (4-20φ at mid-span)
    With detailing.bottom_mid
        .count = 4
        .diameter = 20
        .area_provided = 4 * 3.14159 * 20 * 20 / 4  ' 1256 mm²
        .spacing = M15_Detailing.Calculate_Bar_Spacing(300, 40, 8, 20, 4)
        .layers = 1
    End With

    ' Top bars (3-16φ at supports)
    With detailing.top_start
        .count = 3
        .diameter = 16
        .area_provided = 3 * 3.14159 * 16 * 16 / 4  ' 603 mm²
        .spacing = M15_Detailing.Calculate_Bar_Spacing(300, 40, 8, 16, 3)
        .layers = 1
    End With

    ' Stirrups (2L-8φ@150)
    With detailing.stirrup_mid
        .diameter = 8
        .legs = 2
        .spacing = 150
        .zone_length = detailing.span * 0.6  ' 3000mm
    End With

    ' Development lengths
    detailing.ld_tension = M15_Detailing.Calculate_Development_Length(20, 25, 500, "deformed")
    detailing.ld_compression = M15_Detailing.Calculate_Development_Length(16, 25, 500, "deformed")

    detailing.is_valid = True
    detailing.remarks = "Designed per IS 456:2000"

    ' Export to DXF
    Dim filePath As String
    filePath = "C:\Beams\GB-01_Detailing.dxf"
    Call M16_DXF.Draw_BeamDetailing(filePath, detailing)

    Debug.Print "DXF exported: " & filePath
End Sub
```

---

### Example 3: Bar Bending Schedule Generation

```vb
Sub GenerateBBS()
    Dim items() As BBSLineItem
    Dim summary As BBSSummary
    Dim i As Long

    ReDim items(1 To 3)  ' 3 bar marks

    ' A1: Bottom bars (4-20φ)
    With items(1)
        .bar_mark = "A1"
        .member_id = "B1"
        .location = "bottom"
        .zone = "mid"
        .shape_code = "A"  ' Straight with hooks
        .diameter_mm = 20
        .no_of_bars = 4
        .cut_length_mm = 3950  ' mm
        .total_length_mm = 4 * 3950
        .unit_weight_kg = (20 * 20 * 3.95 * 0.00617)  ' D² × L × 0.00617
        .total_weight_kg = .unit_weight_kg * 4
    End With

    ' B1: Top bars (3-16φ)
    With items(2)
        .bar_mark = "B1"
        .member_id = "B1"
        .location = "top"
        .zone = "start"
        .shape_code = "A"
        .diameter_mm = 16
        .no_of_bars = 3
        .cut_length_mm = 2000
        .total_length_mm = 3 * 2000
        .unit_weight_kg = (16 * 16 * 2.0 * 0.00617)
        .total_weight_kg = .unit_weight_kg * 3
    End With

    ' S1: Stirrups (10-8φ)
    With items(3)
        .bar_mark = "S1"
        .member_id = "B1"
        .location = "stirrup"
        .zone = "full"
        .shape_code = "E"  ' Rectangular stirrup
        .diameter_mm = 8
        .no_of_bars = 30  ' Quantity
        .cut_length_mm = 1300  ' Perimeter
        .total_length_mm = 30 * 1300
        .unit_weight_kg = (8 * 8 * 1.3 * 0.00617)
        .total_weight_kg = .unit_weight_kg * 30
    End With

    ' Calculate summary
    summary.member_id = "B1"
    summary.total_items = 3
    summary.total_bars = 4 + 3 + 30  ' 37 bars
    summary.total_weight_kg = 0

    For i = 1 To 3
        summary.total_weight_kg = summary.total_weight_kg + items(i).total_weight_kg
    Next i

    Debug.Print "Total steel weight: " & summary.total_weight_kg & " kg"
End Sub
```

---

## See Also

- [VBA API Reference](vba-api-reference.md) - Public functions (UDFs)
- [VBA Guide](../contributing/vba-guide.md) - Module architecture
- [Excel Tutorial](../getting-started/excel-tutorial.md) - Practical usage examples
- [IS 456 Formulas](is456-formulas.md) - Code clause references

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.13.0 | 2026-01 | Initial UDT reference document |
| 0.9.0 | 2024-09 | Added BBS types (BBSLineItem, BBSSummary) |
| 0.8.0 | 2024-07 | Added serviceability types (DeflectionResult, CrackWidthResult) |
| 0.7.0 | 2024-06 | Added detailing types (BarArrangement, StirrupArrangement, BeamDetailingResult) |
| 0.5.0 | 2024-03 | Core types (FlexureResult, ShearResult) |

---

*Document Version: 0.13.0 | Last Updated: 2026-01-01*
