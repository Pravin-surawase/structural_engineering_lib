# VBA Library Guide

Practical guide to consume, ship, and maintain the VBA side of the Structural Engineering Library.

---

## Scope & Parity
- **Current modules:** `M01_Constants` through `M16_DXF` plus optional tests in `VBA/Tests`.
- **Coverage:** Flexure, shear, ductility, integration/reporting, detailing helpers (Ld, lap length, spacing, bar/stirrup callouts), and **DXF CAD export**.
- **Version note:** VBA project version strings (e.g., `Get_Library_Version`) should be aligned with the tagged release (v0.7.0 for detailing).
- **Python parity:** Both Python and VBA now support detailing calculations AND DXF export. VBA uses native DXF R12 format writer.

## Import & Project Setup
- **Import order (clean workbook/add-in):**
  1. `M02_Types.bas` (UDTs)
  2. `M01_Constants.bas`, `M03_Tables.bas`, `M04_Utilities.bas`, `M05_Materials.bas`
  3. `M06_Flexure.bas`, `M07_Shear.bas`, `M10_Ductile.bas`
  4. `M08_API.bas`, `M09_UDFs.bas`
  5. `M13_Integration.bas`, `M14_Reporting.bas`
  6. `M15_Detailing.bas`
  7. `M16_DXF.bas`
  8. (Optional) `VBA/Tests/*.bas`
- **Add-in packaging:** See `docs/EXCEL_ADDIN_GUIDE.md` for bulk import macro and `.xlam` packaging. Set the VBA project name to `StructEngLib` (no spaces), then save as `.xlam`.
- **Trusted access:** Enable “Trust access to the VBA project object model” when running the bulk importer macro (Excel Trust Center).

## Public Entry Points
- **Worksheet UDFs (M09_UDFs):** `IS456_MuLim`, `IS456_AstRequired`, `IS456_ShearSpacing`, `IS456_Design_Rectangular`, `IS456_Design_Flanged`, `IS456_Tc`, `IS456_TcMax`, `IS456_Check_Ductility`.
- **Detailing UDFs (M09_UDFs + M15):** `IS456_Ld`, `IS456_LapLength`, `IS456_BondStress`, `IS456_BarSpacing`, `IS456_CheckSpacing`, `IS456_BarCount`, `IS456_BarCallout`, `IS456_StirrupCallout`.
- **DXF Export UDFs (M09_UDFs + M16):** `IS456_DrawSection`, `IS456_DrawLongitudinal`, `IS456_ExportBeamDXF` (macro).
- **Programmatic API (M08_API/M15/M16):** Call the underlying module procedures directly (e.g., `M15_Detailing.Create_Beam_Detailing`, `M16_DXF.Draw_BeamDetailing`) for macros or other VBA projects.
- **Version check:** `Get_Library_Version` in `M08_API`—keep this updated during releases.

## Usage Patterns
- **Design → Detailing → Drawing flow (VBA-only):**
  1. Compute design outputs via `M06_Flexure`/`M07_Shear` or the worksheet UDFs.
  2. Pass required steel areas, cover, and geometry to `M15_Detailing.Create_Beam_Detailing` to populate a `BeamDetailingResult` UDT.
  3. Use callouts (`Format_Bar_Callout`, `Format_Stirrup_Callout`) for schedules or export.
  4. Generate DXF drawing via `M16_DXF.Draw_BeamDetailing` or worksheet UDFs.
- **Integration/Reporting:** `M13_Integration` parses ETABS-style CSV; `M14_Reporting` builds beam schedules inside Excel tables.

## Testing & Verification
- **Manual checks:** `VBA/Tests/*.bas` can be imported into a test workbook; run subs directly in the VBA editor (e.g., `Run Test_Structural`, `Run_All_DXF_Tests`).
- **DXF verification:** Use `Generate_Sample_DXF` in `Test_DXF.bas` to create a sample file, then open in AutoCAD, DraftSight, or any DXF viewer.
- **Regression:** Re-run a known design case after upgrading modules (flexure/shear outputs, detailing Ld/lap length).
- **Parity:** When Python logic changes, mirror the formulas and update both `M15_Detailing` and `M09_UDFs`.

## Maintenance Checklist (per release)
- Update `Get_Library_Version` and module headers to the release tag.
- Rebuild the `.xlam` using the import order above; publish to the shared location.
- Smoke-test key UDFs and one detailing flow; confirm no missing references.
- Generate sample DXF and verify layer colors and content in CAD viewer.
- Note VBA scope in `docs/RELEASES.md` if it diverges from Python.
