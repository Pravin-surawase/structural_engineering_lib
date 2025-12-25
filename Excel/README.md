# Excel Artifacts

This folder contains **Excel-facing deliverables and examples** for the project.

## What is tracked (committed)

These binary files are intentionally versioned because they are part of the user-facing Excel workflow:

- `BEAM_IS456_CORE.xlsm` — core workbook/macro-enabled prototype.
- `BEAM_IS456_CORE.xlsx` — macro-free variant (when applicable).
- `BeamDesignApp.xlsm` — app-style workbook for running beam design flows.
- `StructEng_BeamDesign_v0.5.xlsm` — the v0.5 workbook milestone.

## What should NOT be tracked

- Scratch workbooks created during experimentation (e.g. `Book*.xlsx`).
- Excel temp/lock files (e.g. `~$*.xlsx`).

If you need a scratch workbook, keep it outside the repo or ensure it matches an ignored pattern.

## Add-ins (`.xlam`)

Built add-ins are treated as build outputs.

- Preferred tracked location (when you intentionally version an add-in): `VBA/Build/` (allowed by `.gitignore`).
- Anything under `Excel/*.xlam` is ignored by default.
