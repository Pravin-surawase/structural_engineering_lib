# Task 1.1: Create BeamDesignSchedule.xlsm Template

**For:** GitHub Copilot Execution
**Estimated Time:** 2-3 hours
**Prerequisites:** Excel 2016+, StructEngLib.xlam loaded
**Output:** `Excel/Templates/BeamDesignSchedule.xlsm`

---

## Objective

Create a professional, production-ready Excel workbook for batch beam design (10-50 beams) with:
- Pre-configured input/output tables
- Auto-calculating formulas using StructEngLib UDFs
- Conditional formatting (visual pass/fail indicators)
- One-click DXF export for all beams
- Print-ready format (A4 landscape)

---

## Step-by-Step Implementation

### Step 1: Create New Workbook

**Action:**
```
1. Open Excel
2. Create new blank workbook
3. Save As: Excel/Templates/BeamDesignSchedule.xlsm (Macro-Enabled)
```

**Copilot Prompt:**
```
Create a new Excel macro-enabled workbook named "BeamDesignSchedule.xlsm"
with 3 sheets: "Design", "Instructions", "Summary"
```

---

### Step 2: Design Sheet - Input Columns (A-I)

**Worksheet:** Sheet "Design"

**Column Headers (Row 1):**
| Col | Header | Unit | Data Type | Example |
|-----|--------|------|-----------|---------|
| A | BeamID | - | Text | B1 |
| B | b (mm) | mm | Number | 300 |
| C | D (mm) | mm | Number | 500 |
| D | d (mm) | mm | Number | 450 |
| E | fck | N/mm² | Number | 25 |
| F | fy | N/mm² | Number | 500 |
| G | Mu (kN·m) | kN·m | Number | 150 |
| H | Vu (kN) | kN | Number | 100 |
| I | Cover (mm) | mm | Number | 40 |

**Copilot Prompt:**
```
In Excel sheet "Design", create a table starting at A1 with headers:
BeamID, b (mm), D (mm), d (mm), fck, fy, Mu (kN·m), Vu (kN), Cover (mm)

Format row 1 as:
- Bold, white text
- Fill color: Dark Blue (RGB 0, 32, 96)
- Borders: All borders, medium weight
- Center alignment
- Font: Calibri 11pt

Apply data validation to columns B-I:
- Allow: Decimal
- Minimum: 0
- Error message: "Value must be greater than 0"
```

**Manual:** Apply header formatting in Excel

---

### Step 3: Design Sheet - Calculated Columns (J-Q)

**Column Headers (Row 1):**
| Col | Header | Formula (Row 2) | Description |
|-----|--------|----------------|-------------|
| J | Mu_lim (kN·m) | `=IS456_MuLim(B2,D2,E2,F2)` | Limiting moment |
| K | Ast (mm²) | `=IS456_AstRequired(B2,D2,G2,E2,F2)` | Required tension steel |
| L | Bar Count | `=IF(ISNUMBER(K2),CEILING(K2/201,1),"")` | Number of 16φ bars |
| M | Bar Callout | `=IF(ISNUMBER(L2),IS456_BarCallout(L2,16),"")` | e.g., "5-16φ" |
| N | Stirrup Spacing (mm) | `=IS456_ShearSpacing(H2,B2,D2,E2,F2,100,K2*100/(B2*D2))` | Required spacing |
| O | Stirrup Callout | `=IF(ISNUMBER(N2),IS456_StirrupCallout(2,8,FLOOR(N2/25,1)*25),"")` | e.g., "2L-8φ@150" |
| P | Ld (mm) | `=IS456_Ld(16,E2,F2)` | Development length |
| Q | Status | `=IF(AND(ISNUMBER(K2),G2<=J2),"✅ Safe","⚠️ Check")` | Pass/fail |

**Copilot Prompt:**
```
In Excel sheet "Design", add calculated column headers in J1:Q1:
Mu_lim (kN·m), Ast (mm²), Bar Count, Bar Callout, Stirrup Spacing (mm),
Stirrup Callout, Ld (mm), Status

In row 2, add these formulas (copy from table above).
Copy formulas down to row 51 (for 50 beams).

Format calculated columns (J-Q):
- Fill color: Light gray (RGB 242, 242, 242)
- Italic font
- Borders: All borders
```

**Manual:** Copy formulas to rows 2-51

---

### Step 4: Conditional Formatting

**Rules:**

**Rule 1: Highlight failed beams**
```
Range: Q2:Q51 (Status column)
Condition: Cell Value = "⚠️ Check"
Format: Red fill (RGB 255, 199, 206), Dark red text
```

**Rule 2: Highlight safe beams**
```
Range: Q2:Q51
Condition: Cell Value = "✅ Safe"
Format: Green fill (RGB 198, 239, 206), Dark green text
```

**Rule 3: Highlight over-reinforced**
```
Range: K2:K51 (Ast column)
Condition: Cell Value = "Over-Reinforced"
Format: Orange fill, bold text
```

**Copilot Prompt:**
```
Apply Excel conditional formatting to sheet "Design":
1. Column Q (Status): Red fill if "⚠️ Check", Green fill if "✅ Safe"
2. Column K (Ast): Orange fill if text contains "Over-Reinforced"
3. Entire row 2-51: Light yellow fill if Q cell = "⚠️ Check"
```

**Manual:** Apply in Excel via Home → Conditional Formatting

---

### Step 5: Sample Data (Rows 2-11)

**Pre-populate 10 beams with realistic data:**

| BeamID | b | D | d | fck | fy | Mu | Vu | Cover |
|--------|---|---|---|-----|----|----|----|----|
| B1 | 300 | 500 | 450 | 25 | 500 | 150 | 100 | 40 |
| B2 | 300 | 450 | 400 | 25 | 500 | 120 | 80 | 40 |
| B3 | 350 | 600 | 550 | 30 | 500 | 250 | 150 | 40 |
| B4 | 230 | 450 | 400 | 25 | 500 | 100 | 70 | 40 |
| B5 | 300 | 500 | 450 | 25 | 500 | 180 | 120 | 40 |
| B6 | 400 | 600 | 550 | 30 | 500 | 280 | 180 | 50 |
| B7 | 300 | 450 | 400 | 20 | 500 | 90 | 60 | 40 |
| B8 | 350 | 550 | 500 | 25 | 500 | 200 | 130 | 40 |
| B9 | 230 | 400 | 350 | 25 | 500 | 80 | 50 | 40 |
| B10 | 300 | 500 | 450 | 25 | 500 | 160 | 110 | 40 |

**Copilot Prompt:**
```
Populate rows 2-11 in "Design" sheet with the sample data above.
Ensure formulas in columns J-Q auto-calculate.
```

---

### Step 6: Instructions Sheet

**Worksheet:** Sheet "Instructions"

**Content:**
```markdown
# Beam Design Schedule - User Guide

## How to Use

1. **Input Data (Columns A-I)**
   - Fill in beam details: ID, dimensions (b, D, d), materials (fck, fy), loads (Mu, Vu), cover
   - Units are in column headers (mm, kN, kN·m, N/mm²)

2. **Review Results (Columns J-Q)**
   - Results auto-calculate using IS 456:2000 formulas
   - ✅ Safe = Design is valid
   - ⚠️ Check = Review required (over-reinforced or unsafe)

3. **Export to DXF**
   - Click "Export All Beams to DXF" button
   - Select output folder
   - DXF files created for each beam

## Column Descriptions

| Column | Description |
|--------|-------------|
| Mu_lim | Limiting moment of resistance |
| Ast | Required tension steel area |
| Bar Count | Number of bars (assuming 16φ) |
| Bar Callout | Reinforcement notation (e.g., 5-16φ) |
| Stirrup Spacing | Required stirrup spacing |
| Stirrup Callout | Stirrup notation (e.g., 2L-8φ@150) |
| Ld | Development length for 16φ bars |
| Status | Pass/fail indicator |

## Notes

- Sample data provided in rows 2-11 (delete and add your beams)
- Maximum 50 beams per sheet (rows 2-51)
- For more beams, copy sheet or create new workbook
- All formulas use StructEngLib add-in (must be loaded)

## Troubleshooting

**#NAME? error:** Add-in not loaded. Go to File → Options → Add-ins → Load StructEngLib.xlam
**#VALUE! error:** Check input values (must be numeric, non-zero)
**"Over-Reinforced":** Beam needs compression steel (doubly reinforced design)
```

**Copilot Prompt:**
```
Create "Instructions" sheet with formatted markdown-style content above.
Use merged cells for title, bullet lists, table formatting.
```

**Manual:** Format instructions sheet in Excel

---

### Step 7: Summary Sheet (Dashboard)

**Worksheet:** Sheet "Summary"

**Layout:**
```
A1: "DESIGN SUMMARY" (Title, font size 16, bold)
A3: "Total Beams:" | B3: =COUNTA(Design!A2:A51)
A4: "Safe Beams:" | B4: =COUNTIF(Design!Q2:Q51,"✅ Safe")
A5: "Check Required:" | B5: =COUNTIF(Design!Q2:Q51,"⚠️ Check")
A6: "Success Rate:" | B6: =B4/B3 (format as percentage)

A8: "MATERIAL SUMMARY"
A9: "Total Steel (kg):" | B9: =SUM(Design!K2:K51)*7850/1000000*4 (rough estimate)

A11: "CRITICAL BEAMS (Top 5 by Mu)"
A12: Headers: BeamID | Mu | Status
A13-A17: Top 5 beams sorted by Mu descending
```

**Copilot Prompt:**
```
Create "Summary" sheet with dashboard layout above.
Add formulas to calculate:
- Total beams
- Safe vs Check count
- Success rate percentage
- Total steel weight estimate

Add a table showing top 5 beams by moment (Mu) in descending order.
```

**Manual:** Create summary formulas

---

### Step 8: VBA Macro - Export All Beams to DXF

**Module:** Add new module "ExportMacros"

**Code:**
```vba
Option Explicit

Sub ExportAllBeamsToDXF()
    Dim ws As Worksheet
    Dim lastRow As Long
    Dim i As Long
    Dim outputFolder As String
    Dim beamID As String
    Dim result As BeamDetailingResult
    Dim exportCount As Long

    ' Get Design worksheet
    Set ws = ThisWorkbook.Sheets("Design")

    ' Find last row with data
    lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row

    If lastRow < 2 Then
        MsgBox "No beam data found. Please add beams to the Design sheet.", vbExclamation
        Exit Sub
    End If

    ' Prompt for output folder
    With Application.FileDialog(msoFileDialogFolderPicker)
        .Title = "Select Output Folder for DXF Files"
        .ButtonName = "Select"
        If .Show = -1 Then
            outputFolder = .SelectedItems(1)
        Else
            Exit Sub  ' User cancelled
        End If
    End With

    ' Ensure folder path ends with separator
    If Right(outputFolder, 1) <> Application.PathSeparator Then
        outputFolder = outputFolder & Application.PathSeparator
    End If

    ' Loop through each beam
    exportCount = 0
    For i = 2 To lastRow
        ' Skip empty rows
        If Len(ws.Cells(i, 1).Value) = 0 Then GoTo NextBeam

        ' Get beam ID
        beamID = ws.Cells(i, 1).Value

        ' Populate BeamDetailingResult from row data
        With result
            .beam_id = beamID
            .b = ws.Cells(i, 2).Value          ' B (width)
            .D = ws.Cells(i, 3).Value          ' D (depth)
            .span = 4000  ' Default span (or add column)
            .cover = ws.Cells(i, 9).Value      ' I (cover)

            ' Bottom bars (mid-span)
            .bottom_mid.count = ws.Cells(i, 12).Value  ' L (bar count)
            .bottom_mid.diameter = 16  ' Assuming 16φ

            ' Top bars (supports) - assume 2-12φ nominal
            .top_start.count = 2
            .top_start.diameter = 12

            ' Stirrups
            ' Parse stirrup callout to get spacing
            Dim stirrupText As String
            stirrupText = ws.Cells(i, 15).Value  ' O (stirrup callout)
            .stirrup_mid.diameter = 8
            .stirrup_mid.legs = 2
            .stirrup_mid.spacing = ExtractSpacing(stirrupText)  ' Helper function
            .stirrup_mid.zone_length = 2400  ' Default

            .is_valid = (ws.Cells(i, 17).Value = "✅ Safe")  ' Q (status)
        End With

        ' Export to DXF
        Dim filePath As String
        filePath = outputFolder & beamID & ".dxf"

        If M16_DXF.Draw_BeamDetailing(filePath, result) Then
            exportCount = exportCount + 1
        Else
            Debug.Print "Failed to export: " & beamID
        End If

NextBeam:
    Next i

    ' Show summary
    MsgBox "Exported " & exportCount & " beams to:" & vbCrLf & outputFolder, _
           vbInformation, "Export Complete"
End Sub

' Helper function to extract spacing from callout (e.g., "2L-8φ@150" -> 150)
Private Function ExtractSpacing(ByVal callout As String) As Double
    Dim atPos As Long
    Dim spacePos As Long
    Dim spacingStr As String

    ' Find @ symbol
    atPos = InStr(callout, "@")
    If atPos = 0 Then
        ExtractSpacing = 150  ' Default
        Exit Function
    End If

    ' Extract number after @
    spacePos = InStr(atPos, callout, " ")
    If spacePos = 0 Then spacePos = Len(callout) + 1

    spacingStr = Mid(callout, atPos + 1, spacePos - atPos - 1)
    ExtractSpacing = Val(spacingStr)
End Function
```

**Copilot Prompt:**
```
Add VBA module "ExportMacros" with Sub ExportAllBeamsToDXF() as shown above.
This macro:
1. Reads beam data from "Design" sheet (rows 2-51)
2. Prompts user for output folder
3. Generates DXF file for each beam using M16_DXF.Draw_BeamDetailing
4. Shows summary message
```

**Manual:** Insert VBA module and paste code

---

### Step 9: Add Export Button to Design Sheet

**Action:**
1. Go to Developer tab → Insert → Button (Form Control)
2. Draw button in cell R1 (right of Status column)
3. Assign macro: `ExportAllBeamsToDXF`
4. Right-click button → Edit Text: "Export All Beams to DXF"
5. Format button: Bold, Blue text, Border

**Copilot Prompt:**
```
Add a Form Control button in Excel at cell R1 (Design sheet).
Text: "Export All Beams to DXF"
Assign to macro: ExportAllBeamsToDXF
```

**Manual:** Insert button via Developer tab

---

### Step 10: Page Setup (Print-Ready)

**Settings:**
```
Page Setup (Design sheet):
- Orientation: Landscape
- Paper: A4
- Margins: Narrow (0.25" all sides)
- Scaling: Fit to 1 page wide × N pages tall
- Print titles: Row 1 (headers repeat on each page)
- Gridlines: Off
- Headers/Footers:
  - Header Center: "Beam Design Schedule - IS 456:2000"
  - Footer Left: "&[Date]"
  - Footer Right: "Page &[Page] of &[Pages]"
```

**Copilot Prompt:**
```
Configure Page Setup for "Design" sheet:
- Landscape orientation
- A4 paper
- Fit to 1 page wide
- Print row 1 headers on every page
- Add header "Beam Design Schedule - IS 456:2000"
- Add footer with date and page numbers
```

**Manual:** Set via Page Layout → Page Setup

---

### Step 11: Protect Sheet (Optional)

**Action:**
1. Select columns A-I (input columns)
2. Format Cells → Protection → Unlock cells
3. Review → Protect Sheet
4. Password: (optional)
5. Allow: "Select unlocked cells", "Format cells"

**Purpose:** Prevent accidental modification of formulas in J-Q

**Copilot Prompt:**
```
Protect "Design" sheet with:
- Unlocked cells: A2:I51 (input range)
- Locked cells: J2:Q51 (formula range)
- No password
- Allow selecting, formatting unlocked cells only
```

**Manual:** Protect sheet via Review tab

---

## Acceptance Criteria

**Functionality:**
- [ ] Input columns (A-I) accept numeric data
- [ ] Calculated columns (J-Q) show correct formulas
- [ ] Conditional formatting highlights failed beams (red)
- [ ] Sample data (10 beams) pre-loaded and formulas work
- [ ] "Export All Beams to DXF" button functional
- [ ] Instructions sheet complete and readable
- [ ] Summary sheet shows correct counts

**Quality:**
- [ ] No #NAME? or #VALUE! errors with add-in loaded
- [ ] Print preview shows all columns on A4 landscape
- [ ] File size <1 MB
- [ ] Tested on fresh Excel install (2016 and 365)
- [ ] All sheets have appropriate names

**User Experience:**
- [ ] Professional appearance (consistent fonts, colors)
- [ ] Clear visual hierarchy (headers stand out)
- [ ] Intuitive layout (inputs left, outputs right)
- [ ] Built-in instructions (no external docs needed for basic use)

---

## Testing Checklist

**Test 1: Fresh Install**
```
1. Open BeamDesignSchedule.xlsm on clean Excel
2. Load StructEngLib.xlam
3. Verify sample data calculates correctly
4. Expected: 10 beams, 8 safe, 2 check required
```

**Test 2: Add New Beam**
```
1. Add beam in row 12: B11, 300, 500, 450, 25, 500, 200, 120, 40
2. Verify formulas auto-calculate
3. Expected: Ast ≈ 1176 mm², Status = "⚠️ Check" (doubly reinforced)
```

**Test 3: Export DXF**
```
1. Click "Export All Beams to DXF" button
2. Select output folder
3. Verify 10-11 DXF files created
4. Open random DXF in AutoCAD
5. Expected: Valid beam drawing with rebar
```

**Test 4: Print Preview**
```
1. File → Print → Print Preview
2. Expected: All columns visible, headers on each page, landscape
```

---

## Files to Deliver

```
Excel/Templates/
├── BeamDesignSchedule.xlsm      (Main template)
└── BeamDesignSchedule_README.md (Quick start guide)
```

**README.md content:**
```markdown
# BeamDesignSchedule.xlsm

**Purpose:** Batch design of 10-50 beams per IS 456:2000

**Requirements:**
- Excel 2016+ (Windows or Mac)
- StructEngLib.xlam add-in loaded

**Quick Start:**
1. Open BeamDesignSchedule.xlsm
2. Enable macros when prompted
3. Review sample data (rows 2-11)
4. Delete sample data, add your beams
5. Click "Export All Beams to DXF" when done

**Columns:**
- Input: A-I (BeamID through Cover)
- Output: J-Q (Mu_lim through Status)

**See Instructions sheet for full guide**
```

---

## Estimated Time Breakdown

| Step | Task | Time |
|------|------|------|
| 1-2 | Create workbook, input headers | 15 min |
| 3 | Add calculated columns & formulas | 30 min |
| 4 | Conditional formatting | 15 min |
| 5 | Sample data | 10 min |
| 6 | Instructions sheet | 20 min |
| 7 | Summary sheet | 20 min |
| 8 | VBA macro | 30 min |
| 9 | Export button | 5 min |
| 10 | Page setup | 10 min |
| 11 | Sheet protection | 5 min |
| Testing | All test cases | 30 min |
| **Total** | | **~3 hours** |

---

## Copilot Workflow

**Session 1: Structure (30 min)**
```
1. Prompt Copilot: "Create Excel workbook with 3 sheets: Design, Instructions, Summary"
2. Prompt: "Add input headers A1-I1 as specified"
3. Prompt: "Add calculated headers J1-Q1 as specified"
4. Save progress
```

**Session 2: Formulas (45 min)**
```
1. Prompt: "Add formulas in J2-Q2 for beam calculations"
2. Prompt: "Copy formulas to row 51"
3. Prompt: "Add sample data in rows 2-11"
4. Verify calculations
```

**Session 3: Formatting (30 min)**
```
1. Prompt: "Apply conditional formatting for status column"
2. Prompt: "Format header row (bold, blue fill, white text)"
3. Prompt: "Set page layout to landscape A4"
```

**Session 4: Automation (45 min)**
```
1. Prompt: "Create VBA macro ExportAllBeamsToDXF"
2. Add helper functions
3. Insert button, assign macro
4. Test export
```

**Session 5: Documentation (30 min)**
```
1. Create Instructions sheet
2. Create Summary dashboard
3. Add README.md
4. Final testing
```

---

**END OF SPEC**

*This spec is designed for GitHub Copilot execution. Each "Copilot Prompt" can be fed directly to Copilot Chat or inline suggestions.*
