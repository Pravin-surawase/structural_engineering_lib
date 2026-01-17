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

1. Instantiate the CSI OAPI using `SetEtabsObject` and `cHelper.SetRunType`.
2. Inspect `SapModel.Analyze.IsSolved` (or similar) to confirm the latest analysis.
3. Call `SapModel.Analyze.RunAnalysis` when results are stale, then loop on
   `SapModel.Analyze.GetRunProgress` until completion.
4. Select required cases/combos via `SapModel.Results.Setup.SetCaseSelectedForOutput`
   (use `eNamedSetType` values) and `SetComboSelectedForOutput`.
5. Fetch beam forces via `SapModel.Results.FrameForce` and `JointReact`, walking
   the `NumberResults` envelope.
6. Query geometry: `FrameObj.GetPoints`, `PointObj.GetCoordCartesian`, `cStory.GetNameList`.
7. Grab section/units metadata from `SapModel.PropFrame.GetSection` and
   `SapModel.GetUnit`, then convert to our CSV schema units (N, mm, kN-m).
8. Save the selected columns into structured CSV files (beam_forces.csv,
   sections.csv, geometry.csv) and optionally ZIP them with metadata.json.

## Macro Flow (Excel + ETABS)

```
Sub ExportToStructuralLib()
  Dim etabs As ETABSv1.cOAPI
  Set etabs = cHelper.InitializeObject()
  Dim sapModel As ETABSv1.cSapModel
  Set sapModel = etabs.SapModel

  If Not IsAnalysisUpToDate(sapModel) Then
     sapModel.Analyze.RunAnalysis
     WaitForAnalysisCompletion sapModel
  End If

  SelectCasesAndCombos sapModel
  Dim csvPayload As String
  csvPayload = BuildCSVPayload(sapModel)
  SavePayload csvPayload, "beam_forces.csv"
  ' Optionally call Streamlit bridge by pinging localhost via WinHTTP
End Sub
```

## Post-Processing Guidance

- Validate that each CSV column matches `docs/specs/csv-import-schema.md`
  (`Mu`, `Vu`, `P`, `Station`, `OutputCase`, `Length`, `Width`, `Fy`, etc.).
- Normalize units using the ETABS unit system so Streamlit sees consistent `N`
  and `mm` values.
- If desired, run ETABS design (e.g., `MyVBAWrapper.DesignBeam`) and capture the
  governing combo per beam so we can label the Streamlit outputs.
- Optionally, run the macro nightly using Windows Task Scheduler to keep data
  fresh for demos; store logs and the output paths for traceability.

## Next Steps

- Package the macro inside `docs/reference/etabs-macros/` or embed in the Excel
  workbook used by engineers.
- Use the extracted CHM topics (e.g., `SapModel.Results.FrameForce`) to confirm
  parameter order and return codes.
- Transition to the bridge/add-in once the macro proves the data contract:
  beam forces, sections, stories, combos, and units.
