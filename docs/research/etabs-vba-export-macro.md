---
**Type:** Research + Recipe
**Audience:** Developers, Automation
**Status:** Draft
**Importance:** Medium
**Created:** 2026-01-18
**Last Updated:** 2026-01-18
---

# ETABS VBA Export Macro — Testing Shortcut

While the bridge + add-in roadmap matures, a VBA macro gives us the fastest path
to test imports, combos, and unit metadata. The macro runs entirely inside the
existing ETABS+Excel workflow and can:

1. Instantiate the CSI OAPI using `cHelper.GetObject` (attach) or
   `cHelper.CreateObjectProgID` (launch).
2. Verify analysis status using `SapModel.Analyze.GetCaseStatus`, optionally
   set run flags with `SapModel.Analyze.SetRunCaseFlag`.
3. Call `SapModel.Analyze.RunAnalysis` when results are stale, then re-check
   case status until all required cases are solved.
4. Select required cases/combos via `SapModel.Results.Setup.SetCaseSelectedForOutput`
   (use `eNamedSetType` values) and `SetComboSelectedForOutput`.
5. Fetch beam forces via `SapModel.Results.FrameForce` and joint reactions via
   `SapModel.Results.JointReact`, or use `SapModel.DatabaseTables` to export
   CSV tables in bulk.
6. Query geometry: `FrameObj.GetPoints`, `PointObj.GetCoordCartesian`,
   `SapModel.Story.GetNameList`.
7. Grab section + units metadata from `SapModel.PropFrame.GetSection` and
   `SapModel.GetPresentUnits_2`, then normalize to our CSV schema units.
8. Save the selected columns into structured CSV files (beam_forces.csv,
   sections.csv, geometry.csv) and optionally ZIP them with metadata.json.

## Target Environment (Windows + ETABS v22)

- Windows 10/11, ETABS v22 installed (64-bit).
- Excel 64-bit (match ETABS bitness).
- CSI API registered via ETABS install (ProgID:
  `CSI.ETABS.API.ETABSObject`).
- Macro security set to allow signed macros or trusted local workbooks.

## One-Time Setup on the Windows Machine

1. Open Excel, press `Alt+F11` to open VBA editor.
2. Go to `Tools -> References` and check
   `ETABS v1.0 Type Library` (browse to the ETABS install if needed).
3. Insert a new VBA module, e.g. `mod_etabs_export`.
4. Paste the macro and update output paths (CSV destination folder).
5. Save the workbook as `.xlsm`.

If the reference cannot be added, use late binding and call the OAPI via
`CreateObject("ETABSv1.Helper")` and `GetObject`/`CreateObjectProgID`.

## Implementation Plan (Phased)

- Phase 0 - Connect + Version Check
  - Attach to running ETABS instance; fall back to launching ETABS.
  - Validate OAPI version (`cHelper.GetOAPIVersionNumber`).
  - Open model file if needed and confirm model path is set before analysis.
- Phase 1 - Core Metadata Export (1-2 days)
  - Units via `GetPresentUnits_2` or set a known system with `SetPresentUnits_2`.
  - Story list, frame connectivity, point coordinates, section names.
  - Export CSVs: `stories.csv`, `frames.csv`, `points.csv`, `sections.csv`.
- Phase 2 - Results Export (2-3 days)
  - Select cases/combos for output.
  - Export forces and reactions via `Results.FrameForce` and `Results.JointReact`.
  - Optionally use `DatabaseTables.GetTableForDisplayCSVFile` for bulk output.
- Phase 3 - Design + Governing Combos (2-3 days)
  - Run design if required, capture governing combos and utilization ratios.
  - Produce `design_summary.csv` with governing case/combo per frame.

## Data Outputs (Minimum Viable Set)

- `points.csv`: point id, x, y, z
- `frames.csv`: frame id, i-end, j-end, story, section
- `sections.csv`: section name, material, dims
- `stories.csv`: story name, elevation
- `beam_forces.csv`: frame id, station, P/V2/V3/T/M2/M3, load case/combo
- `joint_reactions.csv`: joint id, F1/F2/F3/M1/M2/M3, load case/combo
- `units.json`: force/length/temperature unit metadata


## Macro Flow (Excel + ETABS)

```
Sub ExportToStructuralLib()
  Dim helper As ETABSv1.cHelper
  Set helper = New ETABSv1.Helper
  Dim etabs As ETABSv1.cOAPI
  Set etabs = helper.GetObject("CSI.ETABS.API.ETABSObject")
  Dim sapModel As ETABSv1.cSapModel
  Set sapModel = etabs.SapModel

  If Not AreCasesSolved(sapModel) Then
     sapModel.Analyze.RunAnalysis
     WaitForCasesToSolve sapModel
  End If

  SelectCasesAndCombos sapModel
  ExportFramesAndPoints sapModel
  ExportForcesAndReactions sapModel
  ' Optionally call Streamlit bridge by pinging localhost via WinHTTP
End Sub
```

## API References (ETABS v22 CHM)

- OAPI entry points: `docs/reference/vendor/etabs/etabs-chm/html/26c23d4c-221d-7bb7-4ae5-e9d97657cdcf.htm`
- Attach to running ETABS: `docs/reference/vendor/etabs/etabs-chm/html/10421d6a-9180-f71a-b493-a7e7785053f1.htm`
- Launch ETABS by ProgID: `docs/reference/vendor/etabs/etabs-chm/html/3f1a3df2-006a-723d-f97c-4fd19fd4fa03.htm`
- OAPI version check: `docs/reference/vendor/etabs/etabs-chm/html/d28f3634-a3f5-f333-0f77-748e390c4742.htm`
- Analyze property: `docs/reference/vendor/etabs/etabs-chm/html/60fd8343-7468-5e79-c5e7-0d9f5712e439.htm`
- Run analysis: `docs/reference/vendor/etabs/etabs-chm/html/516e7b74-8cb4-af27-31d5-38bb95b3c1d1.htm`
- Get case status: `docs/reference/vendor/etabs/etabs-chm/html/94fc4a33-5784-228c-62ad-edcc74eaf034.htm`
- Results property: `docs/reference/vendor/etabs/etabs-chm/html/0c2bc8bd-2382-75be-9075-b0a8245283c3.htm`
- Select case output: `docs/reference/vendor/etabs/etabs-chm/html/9a897e48-fbcd-d8cc-90f3-8aab80ae0e51.htm`
- Select combo output: `docs/reference/vendor/etabs/etabs-chm/html/50252dbb-7c20-eee8-ac7f-a58d8d50a695.htm`
- Named set enum: `docs/reference/vendor/etabs/etabs-chm/html/9d098515-2fc5-166c-50d2-af5259893c96.htm`
- Frame forces: `docs/reference/vendor/etabs/etabs-chm/html/5efb0061-e25c-363c-1191-6fb001f48978.htm`
- Joint reactions: `docs/reference/vendor/etabs/etabs-chm/html/10645966-190c-ff74-46f2-a87da774df65.htm`
- Frame geometry: `docs/reference/vendor/etabs/etabs-chm/html/71f957cb-61ed-208a-c949-e015256b9740.htm`
- Point coordinates: `docs/reference/vendor/etabs/etabs-chm/html/b0b9bcdc-9d1c-0f0e-c0c1-b3d457335cb2.htm`
- Story list: `docs/reference/vendor/etabs/etabs-chm/html/f5de53a1-c6a3-5d9f-df6f-f838de3d5563.htm`
- Frame section property: `docs/reference/vendor/etabs/etabs-chm/html/2e4b87d5-ce74-99e8-4f36-afb0dfd47019.htm`
- Units (get/set): `docs/reference/vendor/etabs/etabs-chm/html/bbeca1c7-a471-6d04-bd18-2df96a44a7a3.htm`,
  `docs/reference/vendor/etabs/etabs-chm/html/78a3d044-770b-6a3e-1bcc-39c132a5ab0d.htm`
- Database tables: `docs/reference/vendor/etabs/etabs-chm/html/e39eded9-8da2-c558-ecbc-a942b9bb42a3.htm`
- Export tables to Excel: `docs/reference/vendor/etabs/etabs-chm/html/a240d8bb-e778-1fea-ca53-8938ec0fa4a6.htm`
- Export CSV table: `docs/reference/vendor/etabs/etabs-chm/html/3ffd7174-be56-d9cc-7802-781240f0581b.htm`

## Post-Processing Guidance

- Validate that each CSV column matches `docs/specs/csv-import-schema.md`
  (`Mu`, `Vu`, `P`, `Station`, `OutputCase`, `Length`, `Width`, `Fy`, etc.).
- Normalize units using `GetPresentUnits_2` or `SetPresentUnits_2` so Streamlit
  sees consistent `N` and `mm` values.
- If desired, run ETABS design and capture the governing combo per beam so we
  can label the Streamlit outputs.
- Optionally, run the macro nightly using Windows Task Scheduler to keep data
  fresh for demos; store logs and the output paths for traceability.

## Next Steps

- Package the macro inside `docs/reference/etabs-macros/` or embed in the Excel
  workbook used by engineers.
- Use the CHM topics above to confirm parameter order, return codes, and
  enumerations before finalizing the macro.
- Transition to the bridge/add-in once the macro proves the data contract:
  beam forces, sections, stories, combos, and units.
