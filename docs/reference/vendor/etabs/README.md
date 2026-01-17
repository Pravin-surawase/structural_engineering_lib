---
**Type:** Reference
**Audience:** Developers, Integration
**Status:** Draft
**Importance:** High
**Created:** 2026-01-17
**Last Updated:** 2026-01-17
---

# CSI API ETABS v1 (Extracted CHM)

This folder now contains the extracted HTML tree of `CSI API ETABS v1.chm` (the
latest ETABS COM/.NET API reference). I installed `chmlib` via Homebrew and ran
`extract_chmLib "docs/reference/CSI API ETABS v1.chm" docs/reference/vendor/etabs/etabs_chm`.

## Purpose

Use this document whenever you need canonical answers about:

- How to bootstrap the COM API from a managed add-in.
- Which ETABS classes expose model data (frames, points, stories).
- How to run the analysis and pull results tables.
- What enums describe load combos, table groups, or output types.

## Key API highlights for the add-in

1. **Bootstrapping cOAPI + SapModel** – The `cOAPI` interface is the root object
   inside `ETABSv1.dll`. It exposes [`ApplicationStart` / `ApplicationExit` /
   `SetAsActiveObject`]-(etabs_chm/html/85e13e9c-4b05-a5ed-4bfe-08903fdb79e1.htm)
   and the `SapModel` property that gives you a `cSapModel` instance. Always call
   `cHelper.GetOAPIVersionNumber` before using the interface so you confirm the
   version you are automating.

2. **Running analysis** – Use
   [`SapModel.Analyze.RunAnalysis`](etabs_chm/html/516e7b74-8cb4-af27-31d5-38bb95b3c1d1.htm)
   to ensure the model is up-to-date. Build simple UI feedback around this call and
   map the return code to our helper messages.

3. **Result selection** – `SapModel.Results` (see
   [`cSapModel.Results Property`](etabs_chm/html/0c2bc8bd-2382-75be-9075-b0a8245283c3.htm))
   exposes `Setup.SetCaseSelectedForOutput`, `Setup.SetComboSelectedForOutput`,
   and the methods that fetch forces (e.g., `FrameForce`, `JointReact`). We can
   mirror our current CSV schema by calling `FrameForce(...)` for beams, then
   walking `NumberResults` to build Mu/Vu envelopes.

4. **Geometry + topology** – Use `FrameObj.GetPoints`
   ([`cFrameObj.GetPoints`](etabs_chm/html/71f957cb-61ed-208a-c949-e015256b9740.htm))
   together with `PointObj.GetCoordCartesian`
   ([`cPointObj.GetCoordCartesian`](etabs_chm/html/b0b9bcdc-9d1c-0f0e-c0c1-b3d457335cb2.htm))
   to reconstruct beam geometry. For stories and levels, `cStory.GetNameList`
   (`etabs_chm/html/f5de53a1-c6a3-5d9f-df6f-f838de3d5563.htm`) returns a list of
   all level names and a boolean per story that you can use to set elevations.

5. **Section + material metadata** – `SapModel.PropFrame` and
   `SapModel.PropMaterial` (`etabs_chm/html/2e4b87d5-ce74-99e8-4f36-afb0dfd47019.htm`)
   provide section depth/width/area and the material grade (fck/fy) required to
   map into our concrete design schema.

6. **Load cases, combos, enums** – The
   [`eNamedSetType`](etabs_chm/html/9d098515-2fc5-166c-50d2-af5259893c96.htm)
   enumeration shows how the API tags built-in case/combination requests. Use
   these values when you automate case selection (RunAnalysis, TableForm).

## Suggested workflow for the add-in

1. Initialize COM (CoInitialize / cOAPI) and attach a minimal form. Display a
   single button `Export to Structural Lib`.
2. When the button executes: ensure a model is open, call `Analyze.RunAnalysis`
   if `SapModel.GetPresentAnalysisStatus` (any helper method) says the results
   are stale.
3. Select the exact load combinations/frames you need by calling
   `SapModel.Results.Setup.SetCaseSelectedForOutput` before `Results.FrameForce`.
4. Gather frames via `FrameObj.GetNameList`/`GetPoints`, joints via `PointObj`,
   story elevations via `Story.GetNameList`, and sections via `PropFrame`.
5. Normalize units (the CHM methods always mention `System.String` names but
   your converter must inspect `SapModel.GetUnit` / `PropFrame.GetUnits` to map
   to `N`, `mm`, `kN-m` etc). Embed unit metadata in the JSON/CSV payload.
6. POST the JSON to the [local bridge](../../docs/planning/etabs-automation-bridge-plan.md)
   endpoint if available; otherwise write a single `structural-engineering-lib.json`
   payload in the download folder and let Streamlit pick it up.

## Next steps

- Expand the add-in doc (`docs/research/etabs-addin-integration.md`) with the
  exact method signatures we now have from this CHM tree.
- Align the JSON schema we emit with the `FrameForce`/`JointReact` table names
  documented in `SapModel.Results.*`.
- Automate version checks by reading `cHelper.GetOAPIVersionNumber` at startup
  and ensuring the user has ETABS 20+ before enabling the export button.

> All HTML topics live inside `docs/reference/vendor/etabs/etabs_chm/html/…`.
> Link to a topic to give peers machine-readable proof for any claim in this doc.
