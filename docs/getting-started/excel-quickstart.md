# Excel Quickstart (5 minutes)

This quickstart is the fastest way for Excel users to try the library.

## Option A (Recommended): Use the prebuilt add-in (.xlam)

1) Get the add-in file:
- If you have the repository locally: use `Excel/StructEngLib.xlam`.
- If you received a zip from someone: extract it and locate `StructEngLib.xlam`.

2) In Excel: load the add-in
- Excel → File → Options → Add-ins
- At the bottom: **Manage: Excel Add-ins** → **Go…**
- **Browse…** → select `StructEngLib.xlam` → OK

3) Try one function in a sheet

Example (flexure limiting moment, units per IS 456 library conventions):
- `=IS456_MuLim(300, 450, 25, 500)`

If the add-in is loaded successfully, the formula should return a number (kN·m).

## Option B: Use the workbook app (.xlsm)

If you don’t want to install an add-in yet:

1) Open `Excel/BeamDesignApp.xlsm`
2) Enable macros when prompted
3) Follow the workbook’s sheets / buttons (if present)

## Option C (Developer / power user): Bulk-import VBA modules

Use this if you want to build your own add-in or inspect code modules.

- See the bulk importer macro in [docs/contributing/excel-addin-guide.md](../contributing/excel-addin-guide.md)
- VBA modules live in `VBA/Modules/`

Important: the bulk importer requires enabling “Trust access to the VBA project object model” in Excel’s Trust Center.

## Notes

- This project aims for **Python + VBA parity**. If you find a mismatch in outputs between Excel and Python for the same inputs, please report it with a minimal reproducible example.
- Engineering note: this library is a calculation aid; final responsibility for design and detailing remains with the qualified engineer.
