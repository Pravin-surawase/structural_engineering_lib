# Excel Quickstart (Step by Step)

This is the easiest path if you prefer Excel and do not want to code.

---

## Step 1: Get the Excel file
Use one of these:
- `Excel/StructEngLib.xlam` (add-in, recommended)
- `Excel/BeamDesignApp.xlsm` (standalone workbook)

If you received a zip or release bundle, extract it first.

---

## Step 2: Enable macros (required)
In Excel:
1. File -> Options -> Trust Center -> Trust Center Settings
2. Macro Settings -> Enable all macros
3. Check "Trust access to the VBA project object model"

Close and re-open Excel after changing these settings.

---

## Step 3: Load the add-in (if using .xlam)
1. Excel -> File -> Options -> Add-ins
2. At the bottom: Manage "Excel Add-ins" -> Go...
3. Browse -> select `StructEngLib.xlam` -> OK

---

## Step 4: Test one formula
In any cell, enter:
```
=IS456_MuLim(300, 450, 25, 500)
```

Expected result: a number around 196.5 (kN-m).

---

## Step 5: Try the workbook (optional)
If you opened `BeamDesignApp.xlsm`, follow the sheet instructions and buttons (if present).

---

## Advanced (optional)
If you want to build your own add-in or inspect modules:
- See `docs/contributing/excel-addin-guide.md`
- VBA modules live in `VBA/Modules/`

---

## Notes
- Engineering note: this library is a calculation aid; final responsibility for design and detailing remains with the qualified engineer.
- If Excel and Python results differ for the same inputs, report it with a minimal reproducible example.
