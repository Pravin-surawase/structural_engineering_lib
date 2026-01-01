# BeamDesignSchedule.xlsm (Task 1.1)

This template is the Phase 1 "batch beam design" workbook.

## Location

- Target workbook: `Excel/Templates/BeamDesignSchedule.xlsm`
- VBA helper module (import into the workbook): `Excel/Templates/BeamDesignSchedule_vba.bas`

## Prerequisites

- Excel 2016+ (Windows or macOS)
- Add-in loaded: `Excel/StructEngLib.xlam`
  - If formulas show `#NAME?`, the add-in is not loaded.

## What this workbook does

- Sheet **Design**: input columns (A–I) for up to 50 beams + auto-calculated results (J–Q)
- Conditional formatting for quick review (✅ Safe / ⚠️ Check)
- One-click macro: **Export All Beams to DXF**

## DXF export macro

The repo includes a ready-to-import module: `BeamDesignSchedule_vba.bas`.

How to use:
1. Open `BeamDesignSchedule.xlsm`
2. Open VBA editor (`Alt+F11` on Windows)
3. Import the module:
   - `File → Import File…` → select `Excel/Templates/BeamDesignSchedule_vba.bas`
4. Ensure the add-in is loaded (`StructEngLib.xlam`)
5. (Recommended) Run macro once to build the template automatically: `BeamDesignSchedule_SetupWorkbook`
6. Run macro to export DXFs: `BeamDesignSchedule_ExportAllBeamsToDXF`
6. (Optional) Insert a button on the **Design** sheet and assign this macro

Notes:
- The macro uses only primitive values from the **Design** sheet and calls the add-in via `Application.Run("IS456_DrawLongitudinal", ...)`.
- Beam span is not part of the Task 1.1 input table; the macro will:
  - Use a **Span (mm)** column if you add one, otherwise
  - Prompt once for a default span (mm) and apply it to all exported beams.

## Next steps

Follow the implementation spec:
- `docs/_internal/copilot-tasks/TASK_1.1_BeamDesignSchedule_Spec.md`

Track progress here:
- `docs/_internal/copilot-tasks/PROGRESS_TRACKER.md`
