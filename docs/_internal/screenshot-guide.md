# Screenshot Capture Guide for Excel Tutorial

**Purpose:** Instructions for capturing screenshots to add to [excel-tutorial.md](../getting-started/excel-tutorial.md)

**Target:** 8-10 screenshots showing key Excel workflows

---

## Setup Before Capturing

1. **Excel Version:** Use Excel 2016+ on Windows (most common user environment)
2. **Window Size:** Full screen or at least 1280×720px
3. **Zoom:** 100% (not zoomed in/out)
4. **Theme:** Office Light theme (default white)
5. **Workbook:** Create sample workbook with data from tutorial
6. **Add-in:** StructEngLib.xlam loaded

---

## Screenshot List

### 📸 Screenshot 1: Add-in Installation Dialog

**File:** `docs/images/excel-tutorial-01-addin-install.png`

**What to capture:**
- Excel Options window → Add-ins section
- Shows "Excel Add-ins" dropdown selected
- "Go" button highlighted
- Add-ins dialog box open with "StructEngLib" visible in list

**Steps:**
1. File → Options → Add-ins
2. Select "Excel Add-ins" from dropdown
3. Click "Go"
4. Browse → Select StructEngLib.xlam
5. Capture window showing checked add-in

**Annotations (optional):**
- Arrow pointing to "StructEngLib" checkbox
- Text box: "Ensure this is checked"

---

### 📸 Screenshot 2: Basic Design Worksheet (Input Data)

**File:** `docs/images/excel-tutorial-02-input-table.png`

**What to capture:**
- Worksheet showing columns A-I, rows 1-5
- Headers: BeamID, b (mm), D (mm), d (mm), fck, fy, Mu (kN·m), Ast (mm²)
- Sample data for 3-5 beams (from Part 2.1 of tutorial)
- Cell H2 selected showing formula bar: `=IS456_AstRequired(B2, D2, G2, E2, F2)`

**Steps:**
1. Create table from Part 2.1
2. Click cell H2
3. Formula bar should show the function
4. Capture worksheet area A1:I5

**Annotations:**
- Highlight formula bar
- Circle cell H2

---

### 📸 Screenshot 3: Formula Result in Cell

**File:** `docs/images/excel-tutorial-03-formula-result.png`

**What to capture:**
- Same worksheet as Screenshot 2
- Cell H2 showing calculated result (e.g., "882" for 882 mm²)
- Cell H2 selected
- Formula bar still visible

**Steps:**
1. Press Enter to execute formula
2. Result appears in cell
3. Capture result

**Purpose:** Show users what successful formula execution looks like

---

### 📸 Screenshot 4: Complete Design Table with All Formulas

**File:** `docs/images/excel-tutorial-04-complete-table.png`

**What to capture:**
- Worksheet showing columns A-Q, rows 1-6
- Part 6 complete design worksheet with all calculated columns filled
- All formulas showing results (not formulas text)
- Status column showing "OK" for valid designs

**Steps:**
1. Build complete table from Part 6
2. All formulas copied down to rows 2-6
3. Capture full table A1:Q6

**Annotations:**
- Box around calculated columns (J-Q)
- Label: "Auto-calculated results"

---

### 📸 Screenshot 5: Bar Callout Results

**File:** `docs/images/excel-tutorial-05-callouts.png`

**What to capture:**
- Close-up of columns S-T (Bar Callout, Stirrup Callout)
- Shows formatted callouts like "3-16φ", "2L-8φ@150 c/c"
- Cell selected showing formula

**Steps:**
1. Create callout columns from Part 5
2. Select cell with callout formula
3. Zoom to 120% to make text readable
4. Capture columns R-T, rows 1-5

**Purpose:** Show practical detailing output format

---

### 📸 Screenshot 6: UDF Autocomplete

**File:** `docs/images/excel-tutorial-06-udf-autocomplete.png`

**What to capture:**
- Type `=IS456_` in a cell
- Excel autocomplete dropdown showing all available UDFs
- List should show: IS456_MuLim, IS456_AstRequired, IS456_ShearSpacing, etc.

**Steps:**
1. Click empty cell
2. Type `=IS456_` (don't press Enter)
3. Wait for autocomplete menu
4. Capture dropdown list

**Purpose:** Show discoverability of UDFs

---

### 📸 Screenshot 7: Array Formula Entry

**File:** `docs/images/excel-tutorial-07-array-formula.png`

**What to capture:**
- Select cells B11:E11 (4 adjacent cells)
- Formula bar showing: `{=IS456_Design_Rectangular(B2, D2, 50, E2, G2, F2, H2)}`
- Note the curly braces {} indicating array formula
- Status bar showing "4 cells selected"

**Steps:**
1. Select B11:E11 (4 cells horizontally)
2. Type formula (don't press Enter yet)
3. Press Ctrl+Shift+Enter (Windows) or Cmd+Return (Mac)
4. Capture with formula bar visible

**Purpose:** Show how to enter array formulas

---

### 📸 Screenshot 8: Macro Dialog

**File:** `docs/images/excel-tutorial-08-macro-dialog.png`

**What to capture:**
- Alt+F8 Macro dialog box
- List showing "IS456_ExportBeamDXF" and other macros
- "Run" button highlighted

**Steps:**
1. Press Alt+F8
2. Macro list appears
3. Select "IS456_ExportBeamDXF"
4. Capture dialog

**Annotations:**
- Arrow pointing to macro name
- Circle "Run" button

---

### 📸 Screenshot 9: Insert Button for Macro

**File:** `docs/images/excel-tutorial-09-insert-button.png`

**What to capture:**
- Developer tab ribbon
- Insert dropdown menu showing Form Controls
- Button control highlighted
- Drawn button on worksheet with text "Export to DXF"

**Steps:**
1. Developer → Insert → Button (Form Control)
2. Draw button on worksheet
3. Assign Macro dialog appears (capture this too if possible)
4. Show finished button

**Purpose:** Show visual workflow for macro execution

---

### 📸 Screenshot 10: Sample Output (Formatted Report)

**File:** `docs/images/excel-tutorial-10-output-report.png`

**What to capture:**
- Formatted beam schedule from Part 9
- Professional-looking table with:
  - Header (project name, date)
  - Column alignment
  - Monospace font for tabular data
  - Footer with notes

**Steps:**
1. Create formatted version of Part 9 output
2. Apply table formatting (Courier New or Consolas font)
3. Add borders and shading
4. Capture final report

**Purpose:** Show what professional output looks like

---

## Bonus Screenshots (Optional)

### 📸 Bonus 1: Error Handling

**File:** `docs/images/excel-tutorial-bonus-error.png`

**What to capture:**
- Cell showing `#VALUE!` error
- Cell showing "Over-Reinforced" message (when Mu > Mu_lim)
- Tooltip or formula auditing trace

**Purpose:** Show how errors appear and how to debug

---

### 📸 Bonus 2: Conditional Formatting

**File:** `docs/images/excel-tutorial-bonus-conditional.png`

**What to capture:**
- Status column with cells color-coded:
  - Green = "OK" (safe design)
  - Red = "Check" or "Fail" (unsafe)
- Show Conditional Formatting rules dialog

**Purpose:** Teach visual quality indicators

---

## Technical Specifications

**Image Format:** PNG (preferred) or JPG
**Resolution:** Minimum 1280×720px, 96 DPI
**File Size:** <500 KB per image (compress if needed)
**Naming:** `excel-tutorial-XX-description.png` (XX = 01, 02, etc.)
**Location:** Save to `docs/images/` folder (create if doesn't exist)

**Tools for Capture:**
- **Windows:** Snipping Tool, Snip & Sketch (Win+Shift+S)
- **Mac:** Screenshot app (Cmd+Shift+4 for selection)
- **Annotations:** Windows Snip & Sketch, Mac Preview, or Greenshot (free)

---

## After Capturing Screenshots

1. **Save all images** to `docs/images/` folder
2. **Update excel-tutorial.md** with image references:
   ```markdown
   ![Add-in Installation](../images/excel-tutorial-01-addin-install.png)
   ```
3. **Test rendering** by previewing markdown file
4. **Compress images** if any exceed 500 KB (use TinyPNG or similar)
5. **Commit to git** (images are tracked, listed in .gitignore exceptions if needed)

---

## Checklist

- [ ] Screenshot 1: Add-in installation
- [ ] Screenshot 2: Input table
- [ ] Screenshot 3: Formula result
- [ ] Screenshot 4: Complete table
- [ ] Screenshot 5: Callouts
- [ ] Screenshot 6: UDF autocomplete
- [ ] Screenshot 7: Array formula
- [ ] Screenshot 8: Macro dialog
- [ ] Screenshot 9: Insert button
- [ ] Screenshot 10: Output report
- [ ] (Optional) Bonus screenshots
- [ ] Images saved to `docs/images/`
- [ ] excel-tutorial.md updated with image references
- [ ] Images tested in markdown preview
- [ ] Committed to repository

---

**Estimated Time:** 30-45 minutes to capture all screenshots

**Next Steps:**
Once screenshots are captured and saved, the images will be automatically referenced in the updated excel-tutorial.md file.
