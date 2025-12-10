# How to Create and Use the Excel Add-in (.xlam)

This guide explains how to package the VBA library into a reusable Excel Add-in (`StructEngLib.xlam`).

---

## Quickstart (Beginner-Friendly)
1) Open a new blank Excel workbook.  
2) Press `Alt + F11` to open the VBA editor.  
3) Import all `.bas` files from `VBA/Modules/` (Right-click project → Import File).  
4) In the Properties window (F4), set the project Name to `StructEngLib`.  
5) Save the workbook as **Excel Add-In (*.xlam)** (e.g., `StructEngLib.xlam`).  
6) In Excel: File → Options → Add-ins → Manage: Excel Add-ins → Go → Browse… → select `StructEngLib.xlam` → OK.  
7) In your beam workbook, add a reference (Tools → References… → check `StructEngLib`) and call functions, e.g., `StructEngLib.Ast_singly_IS456(...)`.

### Bulk import macro (if your Import dialog doesn’t support multi-select)
Enable “Trust access to the VBA project object model” (Excel Trust Center). Paths differ by platform:
- **Windows:** File → Options → Trust Center → Trust Center Settings… → Macro Settings → check “Trust access to the VBA project object model”.
- **Mac:** Excel → Preferences → Security → enable “Trust access to the VBA project object model”.

Run this once from a blank workbook:

```vba
Sub ImportAllModules()
    Const folder As String = "/Users/Pravin/Library/Mobile Documents/com~apple~CloudDocs/pravin/projects/project_21_dec_25/structural_engineering_lib/VBA/Modules/"
    Dim file As String
    file = Dir(folder & "*.bas")
    Do While file <> ""
        Application.VBE.ActiveVBProject.VBComponents.Import folder & file
        file = Dir
    Loop
End Sub
```

---

## 1. What is an Add-in?

In Excel/VBA terms:
- A normal `.xlsm` workbook with code becomes an add-in when you save it as `.xlam`.
- When a user loads that `.xlam` as an add-in:
  - Its VBA project is loaded into Excel in the background.
  - All `Public` functions/subs inside are available to any open workbook.
  - You don’t copy modules anymore; you just reference that loaded project.

**For us:**
`StructEngLib.xlam` = one hidden workbook that contains `mod_SE_Lib_IS456` and any other structural library modules.

Your beam workbook (`BEAM_IS456_CORE.xlsm`) will use those functions instead of owning them.

---

## 2. Setting up the Structural Library Add-in

### Step 1: Create the library workbook
1. Open Excel → New blank workbook.
2. Open VBA editor (`Alt+F11`).
3. In the Project Explorer, remove any default modules/sheets you don’t need.
4. Import modules from `VBA/Modules/`:
   - `M01_Constants.bas`, `M02_Types.bas`, `M03_Tables.bas`, `M04_Utilities.bas`, `M05_Materials.bas`, `M06_Flexure.bas`, `M07_Shear.bas`, `M08_API.bas`.
   - **No sheet access, no MsgBox, no UI stuff in these files.**

### Step 2: Give the VBA project a proper name
Still in the VBA editor:
1. Select the project (e.g. `VBAProject (Book1)`).
2. Press `F4` to open the Properties window.
3. Set:
   - **Name** = `StructEngLib` (or any clean name, no spaces).
4. Save.

This name is how Excel identifies your library later.

### Step 3: Save it as an add-in
Back in Excel:
1. File → Save As.
2. Choose a stable folder (e.g. `C:\StructAutomate\Libs\` or your OneDrive/Docs that won’t move daily).
3. Save as type: **Excel Add-In (*.xlam)**.
4. File name: `StructEngLib.xlam`.

That’s it. You now have an add-in file.

---

## 3. Loading the Add-in in Excel

You (and later your users) need to load this add-in once per machine.

1. In Excel: File → Options → Add-ins.
2. At the bottom: “Manage: Excel Add-ins” → click **Go…**
3. In the Add-Ins dialog:
   - Click **Browse…**
   - Navigate to your `StructEngLib.xlam` file.
   - Select it, click OK.
4. It should now appear in the list with a checkmark.

**From now on:**
- Whenever Excel starts, it loads `StructEngLib.xlam`.
- The project `StructEngLib` (and its modules) are in memory and callable.
- You usually don’t see the add-in workbook – it stays hidden in the background.

---

## 4. How your Beam Workbook uses the Library

Now open your beam workbook: `BEAM_IS456_CORE.xlsm`.

### Step 4.1: Remove duplicate library modules
If your beam workbook already has copies of the library modules, delete them. The add-in already contains M01–M10.
- Remove any imported M01_Constants … M10_Ductile from the workbook.
- Keep only your workbook-specific code (e.g., your own macros, UI/orchestration modules) that call into `StructEngLib`.

**Idea:**
- Beam workbook = UI + engine orchestration
- Add-in = structural brain

### Step 4.2: (Optional but recommended) Add a reference
This step makes everything cleaner and gives you IntelliSense for the library.

In the beam workbook’s VBA editor:
1. Make sure `StructEngLib.xlam` is loaded as an add-in (from step 3).
2. In the VBA editor: Tools → References…
3. Look for something like `StructEngLib` or the name of the add-in project.
   - If you set the project name earlier, you should see it.
4. Check the box → OK.

Now, in your beam code, you can explicitly call:
```vba
' Pseudo-code style:
AstReq = StructEngLib.Ast_singly_IS456(Mu, b, d, fck, fy)
```

### Quick sanity tests after referencing
Run these from your workbook (or from `VBA/Examples/Example_Usage.bas`) to confirm the add-in is working:

```vba
Sub Test_Addin_Basic()
    Dim res As FlexureResult
    res = StructEngLib.Design_Singly_Reinforced(230, 450, 500, 150, 25, 500)
    Debug.Print "Mu_lim (kN·m):"; res.Mu_Lim
    Debug.Print "Ast (mm^2):"; res.Ast_Required   ' Expect ~1040–1100
End Sub

Sub Test_Addin_Shear()
    Dim s As ShearResult
    s = StructEngLib.Design_Shear(100, 230, 450, 20, 415, 100.5, 1)
    Debug.Print "Tv (N/mm^2):"; s.Tv              ' ~0.97
    Debug.Print "Tc (N/mm^2):"; s.Tc              ' 0.62
    Debug.Print "Spacing (mm):"; s.Spacing        ' Capped at 300
End Sub

Sub Test_Addin_Ductile()
    Dim dres As DuctileBeamResult
    dres = StructEngLib.Check_Beam_Ductility(230, 450, 410, 25, 500, 12)
    Debug.Print "Geo OK:"; dres.IsGeometryValid; " MinPt:"; dres.MinPt; " MaxPt:"; dres.MaxPt; " Spacing:"; dres.ConfinementSpacing
End Sub
```
Compare outputs to `docs/API_REFERENCE.md` worked examples (flexure/shear) and ductile checks (spacing = min(d/4, 8*db_min, 100)).

If you don’t add the reference, you can often still call `Ast_singly_IS456` directly (because the add-in is in global scope), but namespacing with `StructEngLib.` is cleaner and avoids name conflicts.

---

## 5. How it works at Runtime

**When user opens Excel:**
1. Excel loads all checked add-ins, including `StructEngLib.xlam`.
   → The library code is now available in the session.

**When user opens your beam workbook:**
1. Your `.xlsm` opens with:
   - HOME, BEAM_INPUT, BEAM_DESIGN, etc.
   - Macros for looping rows, reading inputs, writing outputs.
2. When your macro needs to calculate something structural:
   - It calls the functions inside `StructEngLib`.
   - e.g. `StructEngLib.Ast_singly_IS456(...)`
3. The results get written back into the beam workbook.

**Execution Flow:**
Button on HOME sheet → `Run_Beam_Design` in your `.xlsm` → Loops rows → for each row calls library functions from `.xlam` → Writes to BEAM_DESIGN/BEAM_SCHEDULE.

---

## 6. Updating the Library (Versioning and Changes)

Let’s say you fix a bug or change a formula in `mod_SE_Lib_IS456`.

**The update cycle:**
1. Open `StructEngLib.xlam` directly (File → Open → select it; Excel will show it as a workbook).
2. Open the VBA editor, edit `mod_SE_Lib_IS456`:
   - tweak formulas, add new functions, improve comments, etc.
3. Save the add-in again.

**Now:**
- Any future Excel session that loads this updated `.xlam` uses the new logic.
- Any beam workbook that calls the library will use the updated formulas (as long as they’re referencing the same file).

**Important:**
- If your users have copies of the old `.xlam` lying around, you need a policy:
  - central location (network/shared folder / versioned path),
  - or a version in the project name (e.g. `StructEngLib_v1`, `StructEngLib_v2`), but that complicates references.

For you alone on your machine, it’s simple: overwrite the file, keep the same name.

---

## 7. When to NOT use Add-in (for now)

Don’t rush to move to add-in while:
- your library function names keep changing,
- your units and conventions are still unstable,
- you’re still discovering what belongs in lib vs what belongs in UI.

Right now you can:
- keep the library module inside your beam workbook while designing it,
- then move it out to `.xlam` once the IS 456 core feels solid.

The add-in architecture only starts paying off once the library is relatively stable and used by multiple tools.

---

## 8. Testing and Validation
- Run VBA tests (manual/Rubberduck) in a workbook that references the add-in to confirm functions behave identically to the module version.
- Cross-check against Python tests/values for key cases (see `docs/API_REFERENCE.md` worked examples).
- Keep unit conventions consistent (kN·m, kN, mm, N/mm²) and table policies (pt clamped 0.15–3.0, no fck interpolation for Table 19) aligned with the library code.

---

## 9. Troubleshooting
- **Add-in not visible in References:** Ensure it’s loaded via Add-ins dialog; re-open Tools → References and check `StructEngLib`.
- **Old logic still used:** User has an older `.xlam` copy. Confirm path/version; centralize the add-in location.
- **Name conflicts:** Prefix calls with `StructEngLib.`; avoid duplicate module names in workbooks.

---

## 10. Release Checklist (Add-in)
1. Export fresh `.bas` modules from source control.
2. Import into add-in workbook; set project name/version constant (M01_Constants).
3. Run VBA tests; sanity-check against worked examples.
4. Save as `.xlam` to the distribution path.
5. Update changelog/version in README/docs if behavior changed.

---
