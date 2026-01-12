# Excel Step-by-Step Tutorial

This tutorial walks you through using the Structural Engineering Library in Excel, step by step with screenshots descriptions and sample data.

---

## Prerequisites

- Microsoft Excel 2016 or later (Windows or Mac)
- The `StructEngLib.xlam` add-in OR `BeamDesignApp.xlsm` workbook

---

## Part 1: Setting Up

### Step 1.1: Enable Macros

1. Open Excel
2. Go to **File → Options → Trust Center**
3. Click **Trust Center Settings**
4. Select **Macro Settings**
5. Choose **Enable all macros**
6. ✅ Check **Trust access to the VBA project object model**
7. Click **OK** twice

### Step 1.2: Install the Add-in (Option A)

1. Go to **File → Options → Add-ins**
2. At the bottom, select **Excel Add-ins** and click **Go**
3. Click **Browse**
4. Navigate to and select `StructEngLib.xlam`
5. Click **OK**
6. The add-in is now loaded!

![Add-in Installation Dialog](../images/excel-tutorial-01-addin-install.png)
*Figure 1: Excel Add-ins dialog showing StructEngLib.xlam loaded*

### Step 1.3: Open the Workbook (Option B)

Alternatively, just open `BeamDesignApp.xlsm` directly. All functions will be available.

---

## Part 2: Basic Beam Design

### Step 2.1: Create Your Data Table

Set up a worksheet like this:

| | A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|---|
| 1 | **BeamID** | **b (mm)** | **D (mm)** | **d (mm)** | **fck** | **fy** | **Mu (kN·m)** | **Ast (mm²)** |
| 2 | B1 | 300 | 500 | 450 | 25 | 500 | 150 | |
| 3 | B2 | 300 | 450 | 400 | 25 | 500 | 100 | |
| 4 | B3 | 350 | 600 | 550 | 30 | 500 | 250 | |

![Input Data Table](../images/excel-tutorial-02-input-table.png)
*Figure 2: Input table with beam geometry and loading data*

### Step 2.2: Calculate Required Steel

In cell **H2**, enter:
```
=IS456_AstRequired(B2, D2, G2, E2, F2)
```

This calculates the tension steel area required for the given moment.

**Parameters explained:**
- `B2` = b (beam width in mm)
- `D2` = d (effective depth in mm)
- `G2` = Mu (factored moment in kN·m)
- `E2` = fck (concrete grade)
- `F2` = fy (steel grade)

Copy the formula down to H3, H4, etc.

![UDF Autocomplete](../images/excel-tutorial-06-udf-autocomplete.png)
*Figure 3: Excel autocomplete showing available IS456_ functions*

![Formula Result](../images/excel-tutorial-03-formula-result.png)
*Figure 4: Calculated steel area (882 mm²) displayed in cell H2*

### Step 2.3: Check Limiting Moment

Add a column to check if the section is adequate:

| I |
|---|
| **Mu_lim (kN·m)** |
| `=IS456_MuLim(B2, D2, E2, F2)` |

If **Mu > Mu_lim**, the beam needs compression steel (doubly reinforced).

---

## Part 3: Shear Design

### Step 3.1: Add Shear Data

Extend your table:

| | J | K | L | M | N |
|---|---|---|---|---|---|
| 1 | **Vu (kN)** | **pt (%)** | **Asv (mm²)** | **sv (mm)** | **τc,max** |
| 2 | 100 | =H2*100/(B2*D2) | 100 | | |

Where:
- `Vu` = Factored shear force (kN)
- `pt` = Tension steel percentage
- `Asv` = Stirrup leg area (e.g., 2 × π × 4² = 100 mm² for 2L-8mm)

### Step 3.2: Calculate Stirrup Spacing

In cell **M2**:
```
=IS456_ShearSpacing(J2, B2, D2, E2, F2, L2, K2)
```

This returns the required stirrup spacing.

### Step 3.3: Check Maximum Shear

In cell **N2**:
```
=IS456_TcMax(E2)
```

The actual shear stress must be less than τc,max.

---

## Part 4: Detailing

### Step 4.1: Development Length

| O |
|---|
| **Ld (mm)** |
| `=IS456_Ld(16, E2, F2)` |

Where 16 is the bar diameter in mm.

### Step 4.2: Lap Length

| P |
|---|
| **Lap (mm)** |
| `=IS456_LapLength(16, E2, F2)` |

### Step 4.3: Bar Spacing Check

| Q | R |
|---|---|
| **Spacing (mm)** | **Check** |
| `=IS456_BarSpacing(B2, 40, 8, 16, CEILING(H2/201,1))` | `=IF(Q2>=25, "OK", "Fail")` |

---

## Part 5: Generate Callouts

### Step 5.1: Bar Callout

| S |
|---|
| **Bottom Bars** |
| `=IS456_BarCallout(CEILING(H2/201,1), 16)` |

Result: `3-16φ` (3 nos. of 16mm bars)

### Step 5.2: Stirrup Callout

| T |
|---|
| **Stirrups** |
| `=IS456_StirrupCallout(2, 8, FLOOR(M2/25,1)*25)` |

Result: `2L-8φ@150` (2-legged 8mm stirrups at 150mm c/c)

![Bar and Stirrup Callouts](../images/excel-tutorial-05-callouts.png)
*Figure 5: Formatted callouts for reinforcement detailing*

---

## Part 6: Complete Design Worksheet

Here's a complete sample worksheet you can recreate:

### Input Data

| A | B | C | D | E | F | G | H | I |
|---|---|---|---|---|---|---|---|---|
| BeamID | b | D | Cover | Span | fck | fy | Mu | Vu |
| B1 | 300 | 500 | 40 | 4000 | 25 | 500 | 150 | 100 |
| B2 | 300 | 450 | 40 | 3500 | 25 | 500 | 120 | 80 |
| B3 | 350 | 600 | 40 | 5000 | 30 | 500 | 250 | 150 |
| B4 | 300 | 500 | 40 | 4000 | 25 | 500 | 180 | 120 |
| B5 | 250 | 400 | 40 | 3000 | 25 | 500 | 80 | 60 |

### Calculated Results

| J | K | L | M | N | O | P | Q |
|---|---|---|---|---|---|---|---|
| d | Mu_lim | Ast | Bars | sv | Stirrups | Ld | Status |
| =C2-D2-16 | =IS456_MuLim(B2,J2,F2,G2) | =IS456_AstRequired(B2,J2,H2,F2,G2) | =IS456_BarCallout(CEILING(L2/201,1),16) | =IS456_ShearSpacing(I2,B2,J2,F2,G2,100,L2*100/(B2*J2)) | =IS456_StirrupCallout(2,8,FLOOR(N2/25,1)*25) | =IS456_Ld(16,F2,G2) | =IF(AND(L2>0,H2<=K2),"OK","Check") |

![Complete Design Worksheet](../images/excel-tutorial-04-complete-table.png)
*Figure 6: Complete design worksheet with input data (columns A-I) and calculated results (columns J-Q)*

---

## Part 7: Export to DXF

### Step 7.1: Using the Macro

1. Press `Alt + F8` to open the Macro dialog
2. Select `IS456_ExportBeamDXF` or similar
3. Click **Run**
4. The DXF file will be saved to the workbook folder

![Macro Dialog](../images/excel-tutorial-08-macro-dialog.png)
*Figure 7: Macro dialog showing IS456_ExportBeamDXF function*

### Step 7.2: Using a Button

1. Go to **Developer → Insert → Button**
2. Draw a button on your sheet
3. Assign the macro `IS456_ExportBeamDXF`
4. Click the button to export

![Insert Macro Button](../images/excel-tutorial-09-insert-button.png)
*Figure 8: Creating a button to run DXF export macro*

### Step 7.3: Export VBA Code

For custom export, use this VBA code (Alt+F11 to open editor):

```vba
Sub ExportCurrentBeam()
    Dim result As BeamDetailingResult
    Dim ws As Worksheet
    Dim row As Long

    Set ws = ActiveSheet
    row = ActiveCell.row  ' Current selected row

    ' Read data from current row
    Call M15_Detailing.Create_Beam_Detailing( _
        beam_id:=ws.Cells(row, 1).Value, _
        story:="", _
        b:=ws.Cells(row, 2).Value, _
        D:=ws.Cells(row, 3).Value, _
        span:=ws.Cells(row, 5).Value, _
        cover:=ws.Cells(row, 4).Value, _
        fck:=ws.Cells(row, 6).Value, _
        fy:=ws.Cells(row, 7).Value, _
        ast_start:=ws.Cells(row, 12).Value, _
        ast_mid:=ws.Cells(row, 12).Value, _
        ast_end:=ws.Cells(row, 12).Value, _
        result:=result)

    ' Export DXF
    Dim filePath As String
    filePath = ThisWorkbook.Path & "\" & ws.Cells(row, 1).Value & ".dxf"

    If M16_DXF.Draw_BeamDetailing(filePath, result) Then
        MsgBox "Exported to: " & filePath, vbInformation
    Else
        MsgBox "Export failed!", vbCritical
    End If
End Sub
```

---

## Part 8: Common Formulas Cheat Sheet

### Flexure
```excel
' Limiting moment
=IS456_MuLim(b, d, fck, fy)

' Required tension steel
=IS456_AstRequired(b, d, Mu, fck, fy)

' Doubly reinforced (returns Asc if Mu > Mu_lim)
=IS456_Design_Rectangular(b, D, d, d_dash, Mu, fck, fy)
```

### Shear
```excel
' Concrete shear strength
=IS456_Tc(fck, pt)

' Maximum shear stress
=IS456_TcMax(fck)

' Required stirrup spacing
=IS456_ShearSpacing(Vu, b, d, fck, fy, Asv, pt)
```

### Detailing
```excel
' Development length
=IS456_Ld(bar_dia, fck, fy)

' Lap length
=IS456_LapLength(bar_dia, fck, fy)

' Bar spacing
=IS456_BarSpacing(b, cover, stirrup_dia, bar_dia, bar_count)

' Check minimum spacing
=IS456_CheckSpacing(spacing, bar_dia)

' Number of bars needed
=IS456_BarCount(Ast_required, bar_dia)

' Format callouts
=IS456_BarCallout(count, diameter)
=IS456_StirrupCallout(legs, diameter, spacing)
```

---

## Part 9: Sample Output Report

After completing the design, your worksheet should look like:

```
=========================================================
BEAM DESIGN SCHEDULE - IS 456:2000
Project: Sample Building
Date: Dec 2025
=========================================================

BEAM  SIZE      SPAN   Mu      BOTTOM     TOP       STIRRUPS          Ld
ID    (mm)      (mm)   (kN·m)  BARS       BARS      (c/c)             (mm)
----- --------- ------ ------- ---------- --------- ----------------- -----
B1    300×500   4000   150     3-16φ      2-12φ     2L-8φ@150         752
B2    300×450   3500   120     3-16φ      2-12φ     2L-8φ@175         752
B3    350×600   5000   250     4-20φ      2-16φ     2L-10φ@125        915
B4    300×500   4000   180     4-16φ      2-12φ     2L-8φ@150         752
B5    250×400   3000   80      2-16φ      2-10φ     2L-8φ@175         752

NOTES:
1. Cover to main bars = 40mm
2. All dimensions in mm unless noted
3. Stirrup spacing at supports may be reduced as per shear diagram
4. Development lengths at simple supports = Ld/3 or 12φ (whichever greater)
=========================================================
```

![Sample Output Report](../images/excel-tutorial-10-output-report.png)
*Figure 9: Professional beam design schedule with formatted output*

---

## Part 10: Tips for Beginners

### Do's ✅
- Always verify your units (mm, N/mm², kN·m)
- Check if Mu < Mu_lim before using singly reinforced formulas
- Use FLOOR() for stirrup spacing to get practical values
- Add a "Status" column to flag errors

### Don'ts ❌
- Don't forget to calculate effective depth d = D - cover - stirrup - bar/2
- Don't mix up pt (percentage) with Ast (area)
- Don't use spacing less than minimum (25mm or bar diameter)
- Don't exceed maximum steel percentage (4% of bD)

### Quick Checks
| Check | Formula | Typical Range |
|-------|---------|---------------|
| Steel % | `=Ast*100/(b*d)` | 0.3% to 2.5% |
| Xu/d | `=0.87*fy*Ast/(0.36*fck*b*d)` | < 0.46 for Fe500 |
| Shear τv | `=Vu*1000/(b*d)` | < τc,max |

---

*Document Version: 0.16.6 | Last Updated: 2026-01-12
