# How to Create and Use the Excel Add-in (.xlam)

This guide explains how to package the VBA library into a reusable Excel Add-in (`StructEngLib.xlam`).

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
4. Add a standard module:
   - Right-click project → Insert → Module.
   - Name it `mod_SE_Lib_IS456` (or similar).
5. Paste/move your structural functions into this module:
   - All the pure calc stuff: effective depth, Ast, tau_v, tau_c, Vuc, stirrups spacing, etc.
   - **No sheet access, no MsgBox, no UI stuff in this file.**

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
In the beam workbook’s VBA project:
- Delete any modules that contain the same structural library functions (`mod_SE_Lib_IS456` or similar).
- Leave only:
  - `mod_Main`
  - `mod_BeamCalc`
  - `mod_Utils`
  - etc.

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
