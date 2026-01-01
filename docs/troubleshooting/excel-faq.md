# Excel VBA - FAQ & Troubleshooting

**Version:** 0.13.0
**Platform:** Microsoft Excel 2016+ (Windows & Mac)

Common issues and solutions for using the Structural Engineering Library in Excel.

---

## Table of Contents

- [Installation & Setup Issues](#installation--setup-issues)
- [Function & Formula Issues](#function--formula-issues)
- [Macro & Security Issues](#macro--security-issues)
- [Platform-Specific Issues](#platform-specific-issues)
- [Performance & Compatibility](#performance--compatibility)
- [DXF Export Issues](#dxf-export-issues)
- [General Excel Tips](#general-excel-tips)

---

## Installation & Setup Issues

### Q: Add-in not showing in Excel Add-ins list

**Problem:** Installed StructEngLib.xlam but functions not available.

**Solutions:**
1. **Verify file location:**
   - Add-in must be in a stable location (not Downloads or Temp folder)
   - Move to: `C:\Users\[YourName]\Documents\Excel Add-ins\` (Windows)
   - Or: `/Users/[YourName]/Library/Application Support/Microsoft/Office/` (Mac)

2. **Re-install add-in:**
   - File → Options → Add-ins
   - Manage: Excel Add-ins → Go
   - Uncheck StructEngLib (if present)
   - Click OK, then re-open dialog
   - Browse → Select StructEngLib.xlam
   - Check box → OK

3. **Check if add-in is enabled:**
   - In Add-ins dialog, ensure **checkbox is ticked** next to StructEngLib
   - If greyed out, file may be corrupted or blocked

4. **Unblock file (Windows):**
   - Right-click StructEngLib.xlam
   - Properties → General tab
   - If you see "This file came from another computer...", click **Unblock**
   - Click Apply → OK
   - Re-install add-in

---

### Q: Functions return #NAME? error

**Problem:** `=IS456_MuLim(...)` shows `#NAME?` instead of result.

**Solutions:**
1. **Add-in not loaded:**
   - Check File → Options → Add-ins → Manage Excel Add-ins
   - StructEngLib must be checked

2. **Typo in function name:**
   - Function names are case-sensitive: `IS456_MuLim` not `is456_mulim`
   - All functions start with `IS456_` prefix
   - Use autocomplete: type `=IS456_` and select from dropdown

3. **Workbook-specific issue:**
   - Close and reopen Excel
   - Or use standalone workbook (BeamDesignApp.xlsm) instead of add-in

---

### Q: Macros are disabled / Security warning

**Problem:** Yellow security bar: "Macros have been disabled."

**Solutions:**
1. **Enable for this session:**
   - Click "Enable Content" in yellow bar
   - Temporary fix (resets when you reopen file)

2. **Trust location (permanent):**
   - File → Options → Trust Center → Trust Center Settings
   - Trusted Locations → Add new location
   - Browse to folder containing StructEngLib.xlam
   - Check "Subfolders of this location are also trusted"
   - OK → OK

3. **Enable all macros (for development only):**
   - ⚠️ **Not recommended for production**
   - File → Options → Trust Center → Trust Center Settings
   - Macro Settings → Enable all macros
   - Check "Trust access to the VBA project object model"
   - OK → OK

---

## Function & Formula Issues

### Q: Function returns #VALUE! error

**Problem:** Formula like `=IS456_AstRequired(B2,C2,D2,E2,F2)` returns `#VALUE!`.

**Causes and Solutions:**

1. **Empty or non-numeric cells:**
   - Check all input cells contain numbers (not text or blank)
   - Use `=ISNUMBER(B2)` to verify
   - Solution: Fill in missing values

2. **Invalid parameter values:**
   - Zero or negative dimensions (b, d, D must be > 0)
   - fck outside IS 456 range (15-60 N/mm²)
   - fy outside range (250, 415, 500 N/mm²)
   - Solution: Check IS 456 limits

3. **Division by zero:**
   - Spacing formulas fail if b, d, or Asv = 0
   - Solution: Ensure all denominators are non-zero

4. **Circular reference:**
   - Cell references itself indirectly
   - Check status bar for "Circular:" warning
   - Solution: Break circular dependency

**Debug tip:**
```excel
' Wrap formula to catch errors:
=IFERROR(IS456_AstRequired(B2,C2,D2,E2,F2), "INPUT ERROR")
```

---

### Q: Function returns string instead of number

**Problem:** `=IS456_AstRequired(...)` returns "Over-Reinforced" instead of Ast value.

**Explanation:** This is **intentional behavior** (not an error).
- If Mu > Mu_lim, beam needs compression steel (doubly reinforced)
- Function returns message instead of invalid number

**Solutions:**
1. **Check message:**
   - "Over-Reinforced" → Use `IS456_Design_Rectangular` for doubly reinforced design
   - "Unsafe: Exceeds Tc_max" → Increase section size

2. **Handle in formula:**
   ```excel
   ' Return 0 if text, otherwise return value:
   =IF(ISNUMBER(IS456_AstRequired(...)), IS456_AstRequired(...), 0)
   ```

3. **Use array formula:**
   - Use `IS456_Design_Rectangular` which returns [Ast, Asc, Xu, Status]
   - Handles both singly and doubly reinforced automatically

---

### Q: Array formula not working

**Problem:** `IS456_Design_Rectangular` returns only one value instead of 4.

**Solution:**
1. **Select 4 adjacent cells horizontally** (e.g., B10:E10)
2. Type formula: `=IS456_Design_Rectangular(B2, C2, 50, D2, E2, F2, G2)`
3. Press **Ctrl+Shift+Enter** (Windows) or **Cmd+Return** (Mac)
4. Formula bar shows curly braces: `{=IS456_Design_Rectangular(...)}`
5. All 4 cells populate with [Ast, Asc, Xu, Status]

**If still not working:**
- Formula bar must show `{}` braces (added automatically by Ctrl+Shift+Enter)
- Don't type the braces manually
- Must select all 4 cells BEFORE entering formula
- Excel 365: Array formulas work differently (spill arrays) - may not need Ctrl+Shift+Enter

---

### Q: Formulas calculate slowly

**Problem:** Worksheet recalculates very slowly (5+ seconds).

**Solutions:**
1. **Disable automatic calculation (temporary):**
   - Formulas → Calculation Options → Manual
   - Press F9 to recalculate when needed
   - Re-enable Automatic when done

2. **Reduce formula complexity:**
   - Avoid nested IF/IFERROR chains
   - Calculate intermediate values in separate cells
   - Use helper columns instead of mega-formulas

3. **Check for circular references:**
   - File → Options → Formulas → Enable iterative calculation
   - Or fix circular dependencies

4. **Limit volatile functions:**
   - Avoid INDIRECT, OFFSET, NOW, TODAY in large tables
   - Use static references instead

---

## Macro & Security Issues

### Q: "Macro not found" error when clicking button

**Problem:** Button assigned to `IS456_ExportBeamDXF` shows error.

**Solutions:**
1. **Verify macro exists:**
   - Alt+F8 (Windows) or Fn+Option+F8 (Mac)
   - Check if `IS456_ExportBeamDXF` is in list
   - If not, add-in not loaded or modules not imported

2. **Re-assign macro:**
   - Right-click button → Assign Macro
   - Select `IS456_ExportBeamDXF` from list
   - OK

3. **Check module name:**
   - Macro might be in different workbook
   - Assign macro as: `StructEngLib.xlam!IS456_ExportBeamDXF`

---

### Q: VBA compile error: "User-defined type not defined"

**Problem:** VBA code shows error on `Dim result As FlexureResult`.

**Solutions:**
1. **Import M02_Types.bas first:**
   - User-defined types (FlexureResult, ShearResult, etc.) are in M02_Types.bas
   - When manually importing modules, **always import M02_Types.bas FIRST**

2. **Check module import order:**
   - Correct order: M02 → M01, M03-M07 → M08-M19 → M99
   - See [VBA Guide](../contributing/vba-guide.md) for details

3. **Re-import modules:**
   - Remove all modules
   - Use bulk import macro from [Excel Add-in Guide](../contributing/excel-addin-guide.md)

---

### Q: "Trust access to VBA project" required

**Problem:** Installer macro fails with permission error.

**Solution:**
1. File → Options → Trust Center → Trust Center Settings
2. Macro Settings
3. ✅ Check **"Trust access to the VBA project object model"**
4. OK → OK
5. Re-run installer macro

---

## Platform-Specific Issues

### Q: Excel for Mac: Functions not working

**Problem:** Mac Excel shows #VALUE! for all IS456_ functions.

**Known Issues:**
- **Mac Excel 2016/2019 has VBA limitations:**
  - Some Windows API calls not supported
  - User-defined types (UDTs) may have issues in older Mac Excel versions
  - File path handling different (/ vs \)

**Solutions:**
1. **Use Excel 365 for Mac:**
   - Better VBA compatibility than Excel 2016/2019
   - UDT issues mostly resolved

2. **Test with standalone workbook:**
   - Use BeamDesignApp.xlsm instead of add-in
   - Modules embedded in workbook are more reliable on Mac

3. **Check VBA compatibility:**
   - See [Known Pitfalls - Mac VBA](../reference/known-pitfalls.md) for workarounds
   - Some features (DXF export with file dialogs) may have reduced functionality

4. **File paths:**
   - Use `/Users/[name]/Documents/` not `C:\Users\`
   - Check `Application.PathSeparator` in VBA (returns "/" on Mac)

---

### Q: Excel 365 vs Excel 2016 differences

**Problem:** Formulas work in Excel 365 but not Excel 2016.

**Differences:**

| Feature | Excel 365 | Excel 2016/2019 |
|---------|-----------|-----------------|
| Array formulas | Spill arrays (auto-expand) | Ctrl+Shift+Enter required |
| Dynamic arrays | FILTER, SORT, UNIQUE | Not supported |
| UDFs | Work in both | Work in both |
| Add-ins | Work in both | Work in both |

**Solutions:**
- Stick to compatible syntax (Ctrl+Shift+Enter for arrays)
- Avoid Excel 365-only functions (FILTER, XLOOKUP) in templates
- Test workbooks in Excel 2016 if distributing widely

---

## Performance & Compatibility

### Q: Workbook file size very large (10+ MB)

**Problem:** Workbook with VBA modules is huge.

**Solutions:**
1. **Use add-in instead of embedded modules:**
   - Load StructEngLib.xlam as add-in
   - Workbook becomes just data (10x smaller)

2. **Remove unnecessary modules:**
   - Alt+F11 → VBAProject
   - Delete unused test modules (Test_*.bas)

3. **Compress workbook:**
   - Save As → Excel Workbook (.xlsx) - removes macros
   - Or use .xlsb (binary) format for smaller size with macros

---

### Q: Function calculation taking too long (>5 seconds)

**Problem:** `IS456_Design_Rectangular` freezes Excel.

**Causes:**
- Usually not the UDF itself (design functions are fast)
- Likely circular references or complex worksheet formulas

**Debug:**
1. **Test function in isolation:**
   ```excel
   =IS456_Design_Rectangular(300, 450, 50, 500, 150, 25, 500)
   ```
   - Should calculate in <0.1 seconds
   - If instant, problem is in worksheet setup

2. **Check for circular references:**
   - Formulas → Error Checking → Circular References
   - Resolve loops

3. **Disable automatic calculation temporarily:**
   - See "Formulas calculate slowly" above

---

## DXF Export Issues

### Q: DXF export fails / File not created

**Problem:** `IS456_ExportBeamDXF` runs but no DXF file appears.

**Solutions:**
1. **Check file path:**
   - Ensure save location exists (e.g., `C:\Beams\` folder created)
   - Avoid special characters in path (use A-Z, 0-9, dash, underscore)

2. **Check permissions:**
   - Ensure write permission to target folder
   - Try saving to Desktop or Documents

3. **Verify worksheet data:**
   - Macro expects specific cell layout (see [VBA API Reference](../reference/vba-api-reference.md#is456_exportbeamdxf))
   - Missing cells (B2, B3, etc.) cause failure

4. **Check for VBA errors:**
   - Alt+F11 → Immediate window (Ctrl+G)
   - Look for error messages

---

### Q: DXF file opens empty in CAD software

**Problem:** DXF file created but AutoCAD shows blank drawing.

**Causes:**
- DXF file may be valid but geometry outside visible area
- Layer visibility issues

**Solutions:**
1. **Zoom Extents in CAD:**
   - AutoCAD: Type `ZOOM` → `E` → Enter
   - Drafts sight: View → Zoom → Zoom Extents
   - This shows all geometry

2. **Check layer visibility:**
   - All layers ON (not frozen/hidden)
   - Layers: BEAM_OUTLINE, REBAR_MAIN, REBAR_STIRRUP

3. **Open DXF in text editor:**
   - DXF is text-based
   - Check if file contains ENTITIES section
   - If empty, VBA export failed

4. **Use simpler beam:**
   - Test with minimal data (simple rectangular beam)
   - Verify basic export works before complex cases

---

### Q: DXF compatibility issues with AutoCAD LT / BricsCAD

**Problem:** DXF opens in AutoCAD but not in other CAD software.

**Solution:**
- StructEngLib generates **DXF R12** format (maximum compatibility)
- Should work in: AutoCAD R12+, AutoCAD LT, BricsCAD, LibreCAD, QCAD, DraftSight
- If issues persist, try:
  - Open in AutoCAD → Save As → DXF R14/2000 format
  - Or report compatibility issue with your CAD software version

---

## General Excel Tips

### Q: How do I copy formulas without changing references?

**Problem:** Copying `=IS456_AstRequired(B2,C2,D2,E2,F2)` to row 10 changes B2→B10.

**Solutions:**
1. **Use absolute references (lock cell):**
   ```excel
   =IS456_AstRequired($B$2, $C$2, $D$2, $E$2, $F$2)
   ```
   - `$` locks row and column
   - Press F4 to toggle absolute/relative

2. **Use mixed references:**
   ```excel
   =IS456_AstRequired(B$2, C$2, D$2, E$2, F$2)
   ```
   - `B$2` locks row 2, allows column B to vary

3. **Use named ranges:**
   ```excel
   =IS456_AstRequired(BeamWidth, BeamDepth, Moment, fck, fy)
   ```
   - Select B2 → Name Box → Type "BeamWidth"
   - Formula uses name instead of cell reference

---

### Q: How do I hide #VALUE! errors in blank rows?

**Problem:** Formulas in empty rows show errors.

**Solution:**
```excel
' Option 1: IFERROR
=IFERROR(IS456_AstRequired(B2,C2,D2,E2,F2), "")

' Option 2: IF with blank check
=IF(B2="", "", IS456_AstRequired(B2,C2,D2,E2,F2))

' Option 3: Conditional formatting (hide, don't delete)
- Select formula cells
- Conditional Formatting → New Rule → Format only cells that contain → Errors
- Format: White text on white background
```

---

### Q: Can I use these functions in Google Sheets?

**Answer:** **No, not directly.**
- Google Sheets doesn't support VBA/Excel Add-ins
- Python library works (use Python CLI or API)
- Future: Google Apps Script port possible but not planned

**Workaround:**
1. Design in Excel with StructEngLib
2. Copy results (values only) to Google Sheets
3. Or use Python CLI to generate CSV, import to Sheets

---

### Q: Where can I find working examples?

**Answer:**
1. **Sample workbooks:**
   - `Excel/BeamDesignApp.xlsm` - Application template
   - Check `Excel/Templates/` (if available)

2. **Documentation:**
   - [Excel Tutorial](../getting-started/excel-tutorial.md) - Step-by-step guide
   - [VBA API Reference](../reference/vba-api-reference.md) - All functions with examples
   - [Excel Quickstart](../getting-started/excel-quickstart.md) - 5-minute intro

3. **Test files:**
   - `VBA/Tests/Test_*.bas` - Unit test examples (for developers)

---

## Still Having Issues?

1. **Check documentation:**
   - [Excel Quickstart](../getting-started/excel-quickstart.md)
   - [Excel Tutorial](../getting-started/excel-tutorial.md)
   - [VBA API Reference](../reference/vba-api-reference.md)
   - [Known Pitfalls](../reference/known-pitfalls.md)

2. **Report a bug:**
   - See [CONTRIBUTING.md](../../CONTRIBUTING.md) for issue reporting
   - Include: Excel version, Windows/Mac, error message, sample worksheet

3. **Community support:**
   - See [SUPPORT.md](../../SUPPORT.md) for contact options

---

## Quick Reference Card

### Common Error Messages

| Error | Meaning | Fix |
|-------|---------|-----|
| `#NAME?` | Function not recognized | Load add-in or check spelling |
| `#VALUE!` | Invalid input | Check cell values (numeric, non-zero) |
| `#REF!` | Broken cell reference | Check formula references valid cells |
| `#DIV/0!` | Division by zero | Check b, d, or Asv not zero |
| `#N/A` | Not applicable | Rarely occurs, check formula syntax |
| "Over-Reinforced" | Mu > Mu_lim | Use doubly reinforced design |
| "Unsafe: Exceeds Tc_max" | Shear capacity exceeded | Increase section size or fck |

### Keyboard Shortcuts

| Windows | Mac | Action |
|---------|-----|--------|
| Alt+F8 | Fn+Option+F8 | Open Macro dialog |
| Alt+F11 | Fn+Option+F11 | Open VBA Editor |
| Ctrl+Shift+Enter | Cmd+Return | Enter array formula |
| F9 | Fn+F9 | Recalculate worksheet |
| Ctrl+` | Ctrl+` | Toggle formula view |
| F4 | Cmd+T | Toggle absolute reference ($) |

---

*Document Version: 0.13.0 | Last Updated: 2026-01-01*
