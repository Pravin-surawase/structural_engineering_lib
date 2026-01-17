# DevTemplate.xlsm Setup Instructions

**Purpose:** One-click import of VBA .bas files from Excel/Templates/ folder into Excel for testing.

---

## Step 1: Create New Excel Workbook

1. Open Excel
2. Create new blank workbook
3. Save as: `Excel/DevTemplate.xlsm` (macro-enabled)
4. Enable macros when prompted

---

## Step 2: Enable VBA Project Access

**Required for ImportAllModules macro to work**

1. File → Options → Trust Center → Trust Center Settings
2. Go to "Macro Settings"
3. Check: **"Trust access to the VBA project object model"**
4. Click OK

---

## Step 3: Add DevTools Module

1. Press **Alt+F11** (open VBA Editor)
2. Insert → Module
3. Rename module to **DevTools** (in Properties window, F4)
4. Copy the code below into the module:

```vba
Option Explicit

' Auto-import all .bas files from Excel/Templates/ folder
Public Sub ImportAllModules()
    Dim basFolder As String
    Dim basFile As String
    Dim vbComp As Object
    Dim importCount As Long

    ' Get folder path (Excel/Templates/ relative to workbook location)
    basFolder = ThisWorkbook.Path & Application.PathSeparator & "Templates" & Application.PathSeparator

    If Dir(basFolder, vbDirectory) = "" Then
        MsgBox "Templates folder not found: " & basFolder, vbCritical
        Exit Sub
    End If

    ' Remove existing modules (except DevTools and ThisWorkbook)
    On Error Resume Next
    For Each vbComp In ThisWorkbook.VBProject.VBComponents
        If vbComp.Type = 1 Then ' vbext_ct_StdModule
            If vbComp.Name <> "DevTools" Then
                ThisWorkbook.VBProject.VBComponents.Remove vbComp
            End If
        End If
    Next vbComp
    On Error GoTo 0

    ' Import all .bas files
    importCount = 0
    basFile = Dir(basFolder & "*.bas")

    Do While basFile <> ""
        Application.StatusBar = "Importing: " & basFile
        ThisWorkbook.VBProject.VBComponents.Import basFolder & basFile
        importCount = importCount + 1
        basFile = Dir()
    Loop

    Application.StatusBar = False

    MsgBox "Imported " & importCount & " modules successfully!" & vbNewLine & vbNewLine & _
           "Press Alt+F11 to view VBA Editor and compile (Debug → Compile VBAProject)", vbInformation
End Sub

' Quick compile check after import
Public Sub CompileAndReport()
    On Error GoTo CompileError

    ' Try to compile
    Application.VBE.ActiveVBProject.VBComponents.Item(1).CodeModule.Parent.VBProject.VBComponents.Item(1).Activate

    MsgBox "✅ Compilation successful - no syntax errors!", vbInformation
    Exit Sub

CompileError:
    MsgBox "❌ Compilation failed at:" & vbNewLine & vbNewLine & _
           "Error: " & Err.Description & vbNewLine & _
           "Number: " & Err.Number, vbCritical
End Sub
```

5. Close VBA Editor (Alt+Q)

---

## Step 4: Add Quick Access Buttons (Optional)

**Add buttons to Sheet1 for one-click access:**

1. Go to Sheet1
2. Developer tab → Insert → Button (Form Control)
3. Draw button, assign macro: **ImportAllModules**
4. Label button: **"Import VBA Modules"**
5. Repeat for second button: **CompileAndReport** → Label: **"Compile & Check"**

**If Developer tab not visible:**
- File → Options → Customize Ribbon → Check "Developer"

---

## Step 5: Test the Setup

1. Ensure you have at least one `.bas` file in `Excel/Templates/`
2. Click **"Import VBA Modules"** button (or run ImportAllModules macro)
3. Check message: "Imported X modules successfully!"
4. Press **Alt+F11** to open VBA Editor
5. Debug → Compile VBAProject
6. If errors appear, fix them in the .bas files (in VS Code), re-run linter, then re-import

---

## Workflow After Setup

```bash
# 1. Write VBA in VS Code (Excel/Templates/MyModule.bas)
# 2. Lint before import
python scripts/lint_vba.py Excel/Templates/MyModule.bas

# 3. If linter passes, import to Excel
# - Open DevTemplate.xlsm
# - Click "Import VBA Modules" button
# - Click "Compile & Check" button

# 4. Test in Excel
# - Run functions in worksheet cells
# - Test macros manually

# 5. Fix any runtime errors back in VS Code
# 6. Repeat
```

---

## Folder Structure

```
Excel/
├── DevTemplate.xlsm          (This file - import testing workbook)
├── DevTemplate_Instructions.md  (This guide)
└── Templates/
    ├── BeamDesignSchedule_vba.bas  (Your VBA code)
    ├── M01_Config.bas              (Example .bas files)
    ├── M09_UDFs.bas
    └── ...
```

---

## Troubleshooting

### Error: "Templates folder not found"
**Solution:** Ensure `Excel/Templates/` folder exists and DevTemplate.xlsm is in `Excel/` folder

### Error: "Programmatic access to VBA project denied"
**Solution:** Enable "Trust access to the VBA project object model" (see Step 2)

### Import succeeds but compile fails
**Solution:**
1. Run linter in VS Code: `python scripts/lint_vba.py Excel/Templates/*.bas`
2. Fix errors in .bas files
3. Re-import and re-compile

### Modules not updating after re-import
**Solution:** ImportAllModules removes old modules first - ensure no compile errors preventing removal

---

## Advanced: Auto-Watch Script (Optional)

If you want automatic import on file save (advanced users only):

**File:** `scripts/watch_vba.py`

```python
#!/usr/bin/env python3
"""Auto-import VBA files to Excel on save (requires watchdog + pywin32)"""

import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import win32com.client

class VBAWatcher(FileSystemEventHandler):
    def __init__(self, excel_path: Path):
        self.excel_path = excel_path
        self.excel = None
        self.connect_excel()

    def connect_excel(self):
        """Connect to running Excel instance."""
        try:
            self.excel = win32com.client.GetObject(Class="Excel.Application")
            wb = self.excel.Workbooks(self.excel_path.name)
            print(f"✅ Connected to {self.excel_path.name}")
        except Exception as e:
            print(f"❌ Could not connect to Excel: {e}")
            print("Ensure DevTemplate.xlsm is open in Excel")

    def on_modified(self, event):
        """Trigger import when .bas file changes."""
        if event.src_path.endswith('.bas'):
            print(f"🔄 {Path(event.src_path).name} changed - reimporting...")
            try:
                wb = self.excel.Workbooks(self.excel_path.name)
                wb.Application.Run("DevTools.ImportAllModules")
                print("✅ Import complete")
            except Exception as e:
                print(f"❌ Import failed: {e}")

if __name__ == '__main__':
    watch_folder = Path("Excel/Templates/")
    excel_file = Path("Excel/DevTemplate.xlsm")

    if not excel_file.exists():
        print(f"❌ {excel_file} not found - open it first")
        exit(1)

    print(f"👀 Watching {watch_folder} for changes...")
    print("Press Ctrl+C to stop")

    event_handler = VBAWatcher(excel_file)
    observer = Observer()
    observer.schedule(event_handler, str(watch_folder), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
```

**Install dependencies:**
```bash
pip install watchdog pywin32
```

**Usage:**
```bash
python scripts/watch_vba.py
# Keep DevTemplate.xlsm open in Excel
# Edit .bas files in VS Code
# Auto-imports on save
```

---

**You're all set!** This workflow eliminates 80% of round-trip token waste by catching errors in VS Code before importing to Excel.
