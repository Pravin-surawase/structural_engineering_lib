---
**Type:** User Guide
**Audience:** Engineers, End Users
**Status:** Production Ready
**Importance:** High
**Created:** 2026-01-17
**Last Updated:** 2026-01-17
**Related Docs:** [etabs-vba-implementation-plan.md](../research/etabs-vba-implementation-plan.md), [etabs-vba-export-macro.md](../research/etabs-vba-export-macro.md)
---

# ETABS VBA Export Macro - User Setup Guide

## Overview

This guide helps you set up and use the ETABS VBA Export Macro to export beam forces from ETABS to the structural_engineering_lib CSV format.

**What it does:**
- ✅ Connects to ETABS automatically
- ✅ Runs analysis if needed
- ✅ Exports frame forces, sections, geometry
- ✅ Converts units automatically (→ kN, mm)
- ✅ Creates CSV files ready for Streamlit import

**Requirements:**
- Windows 10/11 (64-bit recommended)
- ETABS v18, v19, v20, v21, or v22 installed
- Microsoft Excel 2016 or later (64-bit recommended)
- 100 MB free disk space

---

## Quick Start (5 Minutes)

### Step 1: Download the Macro Files
1. Download all VBA module files (`.bas` files) from:
   ```
   VBA/ETABS_Export/
   ├── mod_Main.bas
   ├── mod_Connection.bas
   ├── mod_Analysis.bas
   ├── mod_Export.bas
   ├── mod_Validation.bas
   ├── mod_Logging.bas
   ├── mod_Types.bas
   └── mod_Utils.bas
   ```

2. Save them to a temporary folder on your computer

### Step 2: Create Excel Workbook
1. Open Excel
2. Save as: `ETABS_Export.xlsm` (Excel Macro-Enabled Workbook)
3. Choose location: Recommended `Documents\ETABS_Export\`

### Step 3: Import VBA Modules
1. Press `Alt+F11` to open VBA Editor
2. In VBA Editor menu: **File → Import File...**
3. Select **all 8 `.bas` files** (Ctrl+Click to select multiple)
4. Click **Open**
5. Verify all modules appear in Project Explorer:
   ```
   VBAProject (ETABS_Export.xlsm)
   ├─ Microsoft Excel Objects
   │  └─ Sheet1 (Sheet1)
   ├─ Modules
   │  ├─ mod_Main
   │  ├─ mod_Connection
   │  ├─ mod_Analysis
   │  ├─ mod_Export
   │  ├─ mod_Validation
   │  ├─ mod_Logging
   │  ├─ mod_Types
   │  └─ mod_Utils
   ```

### Step 4: Add ETABS API Reference
1. In VBA Editor menu: **Tools → References...**
2. Scroll down and check: ☑ **ETABS v1.0 Type Library**
   - If not found, click **Browse...**
   - Navigate to: `C:\Program Files\Computers and Structures\ETABS 22\`
   - Select: `ETABSv1.dll`
   - Click **OK**

3. Click **OK** to close References dialog

### Step 5: Create Run Button
1. Return to Excel (press `Alt+F11` again)
2. Go to **Developer** tab
   - If Developer tab not visible: **File → Options → Customize Ribbon → Check Developer**
3. Click **Insert → Button (Form Control)**
4. Draw button on Sheet1
5. In "Assign Macro" dialog, select: **ExportETABSData**
6. Click **OK**
7. Right-click button → **Edit Text** → Change to: **"Export to Structural Lib"**

### Step 6: Enable Macros
1. **File → Options → Trust Center → Trust Center Settings**
2. **Macro Settings**
3. Select: **"Enable all macros (not recommended; potentially dangerous code can run)"**
   - *Or* select: **"Disable all macros with notification"** (you'll need to enable each time)
4. Click **OK**

### Step 7: Test the Export
1. Open ETABS and load a model
2. In Excel, click **"Export to Structural Lib"** button
3. The macro will:
   - Connect to ETABS ✓
   - Check analysis status ✓
   - Export data ✓
   - Create normalized CSV files ✓

4. Check output folder:
   ```
   Documents\ETABS_Export\
   ├─ normalized\
   │  ├─ beam_forces.csv  ← Import this to Streamlit
   │  └─ metadata.json
   ├─ raw\
   │  ├─ frame_forces_raw.csv
   │  ├─ sections_raw.csv
   │  ├─ geometry_raw.csv
   │  └─ stories_raw.csv
   └─ etabs_export_20260117_143022.log
   ```

---

## Detailed Setup Instructions

### A. Windows System Requirements

#### 1. Check Windows Version
- Open: **Settings → System → About**
- Required: Windows 10 (build 1809+) or Windows 11
- Architecture: 64-bit recommended

#### 2. Check ETABS Installation
- Open ETABS
- Menu: **Help → About ETABS**
- Note your version (e.g., v22.3.0)
- Verify ETABS runs without license errors

#### 3. Check Excel Version
- Open Excel
- **File → Account → About Excel**
- Required: Excel 2016 or later
- Architecture: **64-bit recommended** (matches ETABS bitness)
- Check bitness: Look for "(64-bit)" in About dialog

**⚠️ Important:** If ETABS is 64-bit, Excel should also be 64-bit. Mismatched bitness causes COM errors.

---

### B. ETABS API Setup

#### Method 1: Automatic (ETABS installs API automatically)
ETABS installation registers the API. No action needed if ETABS runs normally.

#### Method 2: Manual Registration (if API not found)

**Option A: Using regsvr32 (Administrator)**
1. Open **Command Prompt as Administrator**
2. Navigate to ETABS folder:
   ```
   cd "C:\Program Files\Computers and Structures\ETABS 22"
   ```
3. Register DLL:
   ```
   regsvr32 ETABSv1.dll
   ```
4. Should see: "DllRegisterServer in ETABSv1.dll succeeded"

**Option B: Reinstall ETABS**
1. Download latest ETABS from CSI website
2. Run installer **as Administrator**
3. Choose "Repair" or "Reinstall"

#### Verify API Registration
1. Press `Win+R`
2. Type: `regedit`
3. Navigate to: `HKEY_CLASSES_ROOT\ETABSv1.Helper`
4. If key exists → API is registered ✓

---

### C. Excel VBA Editor Setup

#### 1. Enable Developer Tab
**If Developer tab is not visible:**
1. **File → Options**
2. **Customize Ribbon**
3. Right panel: Check ☑ **Developer**
4. Click **OK**

#### 2. Set Macro Security
**Recommended for development:**
1. **Developer → Macro Security**
2. Select: **"Disable all macros with notification"**
   - You'll click "Enable Content" banner when opening workbook
   - Safer than "Enable all macros"

**For production use:**
- Sign macros with digital certificate
- Or: Store workbook in Trusted Location

#### 3. Add ETABS Reference (Detailed)
1. Press `Alt+F11` (VBA Editor)
2. Menu: **Tools → References...**
3. **Scroll down** to find: **ETABS v1.0 Type Library**
4. **Check the box** ☑
5. Click **OK**

**If "ETABS v1.0 Type Library" not in list:**

**Option A: Browse to DLL**
1. Click **Browse...**
2. Change file type to: **"Type Libraries (*.tlb, *.dll)"**
3. Navigate to:
   ```
   C:\Program Files\Computers and Structures\ETABS 22\ETABSv1.dll
   ```
4. Click **Open**
5. Should now appear in Available References
6. Click **OK**

**Option B: Use Late Binding (no reference needed)**
- Macro already supports late binding as fallback
- Performance slightly slower but more compatible

---

### D. Import VBA Modules

#### Method 1: Import All at Once (Recommended)
1. VBA Editor: **File → Import File...**
2. Navigate to folder with `.bas` files
3. **Select all 8 files** (Ctrl+Click):
   - mod_Main.bas
   - mod_Connection.bas
   - mod_Analysis.bas
   - mod_Export.bas
   - mod_Validation.bas
   - mod_Logging.bas
   - mod_Types.bas
   - mod_Utils.bas
4. Click **Open**

#### Method 2: Copy-Paste Code (Alternative)
1. Create module: **Insert → Module**
2. Open `.bas` file in Notepad
3. **Copy all text** (Ctrl+A, Ctrl+C)
4. **Paste** into VBA module (Ctrl+V)
5. Rename module: In Properties window, change "(Name)" to match (e.g., "mod_Main")
6. Repeat for all 8 modules

#### Verify Import
In **Project Explorer** (Ctrl+R if not visible):
```
VBAProject (ETABS_Export.xlsm)
├─ Microsoft Excel Objects
│  └─ Sheet1 (Sheet1)
├─ Modules
   ├─ mod_Main             ← ExportETABSData() is here
   ├─ mod_Connection
   ├─ mod_Analysis
   ├─ mod_Export
   ├─ mod_Validation
   ├─ mod_Logging
   ├─ mod_Types
   └─ mod_Utils
```

---

### E. Create User Interface

#### Option 1: Simple Button (Recommended)
1. Return to Excel (Alt+F11)
2. **Developer → Insert → Button (Form Control)**
3. Draw button on sheet
4. Assign Macro: **ExportETABSData**
5. Edit text: "Export to Structural Lib"

#### Option 2: Ribbon Button (Advanced)
1. **File → Options → Customize Ribbon**
2. **New Tab** → Name: "ETABS Export"
3. **New Group** → Name: "Export"
4. **Choose commands from:** Macros
5. Add: **ExportETABSData**
6. Click **OK**

#### Option 3: Quick Access Toolbar
1. Right-click Quick Access Toolbar
2. **Customize Quick Access Toolbar...**
3. **Choose commands from:** Macros
4. Add: **ExportETABSData**
5. Click **OK**

---

## Usage Instructions

### Basic Workflow

#### 1. Prepare ETABS Model
✅ **Model must be open in ETABS**
- If ETABS not running, macro will try to launch it
- You'll need to manually open your model file

✅ **Analysis Status**
- If analysis is complete → Export runs immediately
- If analysis needed → Macro will prompt you
- You can run analysis in ETABS first to skip this step

#### 2. Run the Export
1. Click **"Export to Structural Lib"** button in Excel
2. Wait for progress messages in status bar
3. If analysis required, click **Yes** when prompted
4. Export completes in 15-60 seconds (depending on model size)

#### 3. Review Output
**Output folder:** `Documents\ETABS_Export\`

**Files created:**
```
ETABS_Export/
├─ normalized/
│  ├─ beam_forces.csv       ← MAIN FILE (import to Streamlit)
│  └─ metadata.json          ← Units and timestamp info
├─ raw/
│  ├─ frame_forces_raw.csv   ← Raw ETABS data (debugging)
│  ├─ sections_raw.csv
│  ├─ geometry_raw.csv
│  └─ stories_raw.csv
└─ etabs_export_TIMESTAMP.log ← Detailed log
```

**Import to Streamlit:**
- Use file: `normalized/beam_forces.csv`
- Already in correct format (kN, kN·m, mm)
- No manual conversion needed

---

### Advanced Usage

#### Change Output Folder
**Edit in VBA:**
1. VBA Editor: Open `mod_Main`
2. Find function: `GetOutputFolder()`
3. Change line:
   ```vba
   folder = Environ("USERPROFILE") & "\Documents\ETABS_Export"
   ```
   To your preferred location:
   ```vba
   folder = "C:\Projects\MyProject\ETABS_Data"
   ```

#### Enable Debug Logging
**For troubleshooting:**
1. VBA Editor: Open `mod_Main`
2. Find line:
   ```vba
   Public Const LOG_LEVEL As LogLevel = INFO_LEVEL
   ```
3. Change to:
   ```vba
   Public Const LOG_LEVEL As LogLevel = DEBUG_LEVEL
   ```
4. Save workbook
5. Next export will have detailed debug logs

#### Run from VBA Immediate Window
**For testing:**
1. VBA Editor: **View → Immediate Window** (Ctrl+G)
2. Type: `ExportETABSData`
3. Press **Enter**
4. Watch progress in Immediate Window

---

## Troubleshooting

### Common Issues

#### 1. "ETABS API not registered"
**Symptoms:**
- Error message on export start
- "Cannot create ETABSv1.Helper object"

**Solutions:**
1. **Check ETABS installation:**
   - Open ETABS → Verify it runs
   - Menu: Help → About → Note version

2. **Re-register API:**
   ```
   cd "C:\Program Files\Computers and Structures\ETABS 22"
   regsvr32 ETABSv1.dll
   ```

3. **Reinstall ETABS** as Administrator

#### 2. "User-defined type not defined"
**Symptoms:**
- Compile error when running macro
- Highlights: `As Object`, `As ETABSv1.cOAPI`, etc.

**Solutions:**
1. **Add ETABS reference:**
   - Tools → References → Check "ETABS v1.0 Type Library"

2. **Use late binding (if reference fails):**
   - Macro already supports this automatically
   - No code changes needed

#### 3. "Cannot connect to ETABS"
**Symptoms:**
- Macro reports connection failure
- ETABS is running but macro can't attach

**Solutions:**
1. **Close and reopen ETABS**
2. **Open model before running macro**
3. **Check ETABS is not locked:**
   - Close any ETABS dialog boxes
   - Ensure ETABS not running analysis
4. **Run Excel as Administrator**

#### 4. "Analysis timeout"
**Symptoms:**
- Analysis runs but doesn't complete in 30 minutes

**Solutions:**
1. **Run analysis in ETABS first:**
   - Analyze → Run Analysis
   - Wait for completion
   - Then run macro

2. **Increase timeout (Advanced):**
   - Edit `mod_Analysis.bas`
   - Find: `Optional maxWaitMinutes As Integer = 30`
   - Change to: `= 60` (or higher)

#### 5. "Permission denied" or "Path not found"
**Symptoms:**
- Cannot create output files
- Error writing to Documents folder

**Solutions:**
1. **Check output folder permissions:**
   - Right-click folder → Properties → Security
   - Ensure you have "Write" permissions

2. **Change output folder:**
   - Edit `GetOutputFolder()` function
   - Use folder where you have full access

3. **Run Excel as Administrator**

#### 6. Wrong values in exported CSV
**Symptoms:**
- Forces don't match ETABS display
- Units seem incorrect

**Solutions:**
1. **Check ETABS units:**
   - ETABS menu: Define → Units
   - Note current units (kN/m, kip/ft, etc.)

2. **Review log file:**
   - Open: `etabs_export_TIMESTAMP.log`
   - Find line: "ETABS Units: Force=..., Length=..."
   - Verify conversion factors

3. **Manually verify one beam:**
   - Compare ETABS display vs CSV value
   - Check metadata.json for unit info

---

### Getting Help

#### 1. Check the Log File
**Location:** `Documents\ETABS_Export\etabs_export_TIMESTAMP.log`

**What to look for:**
- Error messages (marked "ERROR")
- Warnings (marked "WARN")
- Last successful checkpoint before failure

#### 2. Enable Debug Mode
**See "Enable Debug Logging" in Advanced Usage section**

#### 3. Report Issues
**Include in report:**
- ETABS version (Help → About)
- Excel version (File → Account → About)
- Windows version
- Log file content
- Screenshot of error message

---

## Performance Tips

### For Large Models (1000+ Beams)

#### 1. Close Other Programs
- Free up RAM before export
- Close browser tabs, other applications

#### 2. Run Analysis First
- Analyze → Run Analysis in ETABS
- Wait for completion
- Then run macro (skips analysis step)

#### 3. Expected Times
| Beam Count | Export Time |
|------------|-------------|
| 100 beams | 5-10 seconds |
| 500 beams | 15-20 seconds |
| 1000 beams | 30-45 seconds |
| 5000 beams | 2-3 minutes |

#### 4. Monitor Progress
- Watch Excel status bar for updates
- Check log file for checkpoint times
- If stuck >5 min, press ESC to cancel

---

## Best Practices

### Before Each Export
1. ✅ Save ETABS model
2. ✅ Run analysis in ETABS (or let macro do it)
3. ✅ Close unnecessary programs
4. ✅ Check output folder has space

### After Each Export
1. ✅ Review log for warnings
2. ✅ Verify CSV row count makes sense
3. ✅ Check metadata.json units
4. ✅ Import to Streamlit and test

### Workflow Integration
1. **Design iteration cycle:**
   - Modify model in ETABS
   - Run analysis
   - Export with macro (30 seconds)
   - Review in Streamlit (visual feedback)
   - Iterate

2. **Batch processing:**
   - Export multiple models in sequence
   - Each creates timestamped folder
   - Compare results in Streamlit

---

## Appendix

### A. File Locations

**VBA Modules:**
```
VBA/ETABS_Export/
├── mod_Main.bas         (Entry point, main workflow)
├── mod_Connection.bas   (ETABS API connection)
├── mod_Analysis.bas     (Analysis status & execution)
├── mod_Export.bas       (Data export functions)
├── mod_Validation.bas   (Unit conversion, CSV normalization)
├── mod_Logging.bas      (Checkpoint system, log files)
├── mod_Types.bas        (Data type definitions)
└── mod_Utils.bas        (Helper functions)
```

**Excel Workbook:**
```
Documents\ETABS_Export\ETABS_Export.xlsm
```

**Output Files:**
```
Documents\ETABS_Export\
├── normalized\beam_forces.csv    (Import this!)
├── normalized\metadata.json
├── raw\frame_forces_raw.csv
└── etabs_export_TIMESTAMP.log
```

### B. Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open VBA Editor | Alt+F11 |
| Run macro | F5 (in VBA Editor) |
| Immediate Window | Ctrl+G |
| Save workbook | Ctrl+S |
| Stop running macro | Ctrl+Break or ESC |

### C. CSV Schema Reference

**Output format (beam_forces.csv):**
```csv
Story,Label,Output Case,Station,M3,V2,P
Story1,B1,1.5(DL+LL),0,0.000,-125.500,0.000
Story1,B1,1.5(DL+LL),2500,180.200,0.000,0.000
Story1,B1,1.5(DL+LL),5000,0.000,125.500,0.000
```

**Units:**
- M3 (Moment): kN·m
- V2 (Shear): kN
- P (Axial): kN
- Station: mm

**See also:** [csv-import-schema.md](../../docs/specs/csv-import-schema.md)

---

## Quick Reference Card

### Essential Commands
```
1. Import modules:  Alt+F11 → File → Import File
2. Add reference:   Alt+F11 → Tools → References → ETABS v1.0
3. Create button:   Developer → Insert → Button
4. Run export:      Click "Export to Structural Lib"
5. View log:        Documents\ETABS_Export\*.log
```

### File Paths
```
Workbook:  Documents\ETABS_Export\ETABS_Export.xlsm
Output:    Documents\ETABS_Export\normalized\beam_forces.csv
Log:       Documents\ETABS_Export\etabs_export_TIMESTAMP.log
```

### Support
- Documentation: [docs/research/etabs-vba-implementation-plan.md](../research/etabs-vba-implementation-plan.md)
- Issues: Check log file first, then report with details

---

**Version:** 1.0.0
**Last Updated:** 2026-01-17
**Status:** Production Ready ✅
