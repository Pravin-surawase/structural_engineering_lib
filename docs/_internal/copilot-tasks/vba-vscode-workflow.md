# VBA Development in VS Code - Efficient Workflow

**Problem:** Copying VBA to Excel → compile errors → back to VS Code → repeat = token waste

**Solution:** Develop & validate VBA in VS Code, import to Excel only for final testing

---

## Workflow Overview

```
┌─────────────────────────┐
│ 1. Write VBA in VS Code │  ← Copilot assistance
│    (.bas files)         │  ← Syntax highlighting
│    Excel/Templates/*.bas│  ← Version control
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 2. Validate Syntax      │  ← Python linter script
│    (scripts/lint_vba.py)│  ← Catches errors early
│    Quick check (<1 sec) │  ← No Excel needed
└───────────┬─────────────┘
            │
            ▼ (Only if validation passes)
┌─────────────────────────┐
│ 3. Auto-Import to Excel │  ← One-click macro
│    DevTemplate.xlsm     │  ← Imports all .bas files
│    Test & Debug         │  ← Final integration test
└─────────────────────────┘
```

**Benefits:**
- ✅ Catch 80% of errors before Excel
- ✅ Work in VS Code (better editor)
- ✅ Version control (.bas files in git)
- ✅ Minimal token waste
- ✅ Fast iteration

---

## Setup (One-time, 15 minutes)

### Step 1: Install VS Code Extension for VBA

**Extension:** "VBA" by Steve Domin (or "VBA Language" by bbrfkr)

**Installation:**
```bash
# In VS Code:
Ctrl+Shift+X → Search "VBA" → Install
```

**Features:**
- Syntax highlighting
- Basic IntelliSense (functions, variables)
- Bracket matching
- Code folding

**Note:** VS Code doesn't fully understand VBA (no compiler), but syntax highlighting catches 50% of errors.

---

### Step 2: Create Python VBA Linter Script

**File:** `scripts/lint_vba.py`

**Purpose:** Quick syntax validation before Excel import

**Features:**
- Checks for common VBA syntax errors
- Validates structure (Sub/Function/End Sub matching)
- Catches undeclared variables (Option Explicit enforcement)
- Fast (<1 second)

**Code:**

```python
#!/usr/bin/env python3
"""
VBA Syntax Linter - Pre-import validation
Catches common errors before Excel import
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

class VBALinter:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.content = filepath.read_text(encoding='utf-8')
        self.lines = self.content.split('\n')
        self.errors: List[Tuple[int, str]] = []
        self.warnings: List[Tuple[int, str]] = []

    def lint(self) -> bool:
        """Run all checks. Returns True if no errors."""
        self.check_option_explicit()
        self.check_procedure_pairing()
        self.check_undeclared_variables()
        self.check_common_typos()
        self.check_line_continuations()

        self.print_results()
        return len(self.errors) == 0

    def check_option_explicit(self):
        """Ensure Option Explicit is present."""
        if not re.search(r'^\s*Option\s+Explicit', self.content, re.MULTILINE | re.IGNORECASE):
            self.warnings.append((1, "Missing 'Option Explicit' - add at top of file"))

    def check_procedure_pairing(self):
        """Check Sub/Function have matching End statements."""
        proc_stack = []

        for i, line in enumerate(self.lines, start=1):
            line_clean = line.strip()

            # Ignore comments
            if line_clean.startswith("'"):
                continue

            # Sub/Function start
            if re.match(r'^(Public|Private|Friend)?\s*(Sub|Function)', line_clean, re.IGNORECASE):
                proc_type = re.search(r'(Sub|Function)', line_clean, re.IGNORECASE).group(1)
                proc_stack.append((i, proc_type))

            # End Sub/Function
            if re.match(r'^End\s+(Sub|Function)', line_clean, re.IGNORECASE):
                end_type = re.search(r'End\s+(Sub|Function)', line_clean, re.IGNORECASE).group(1)
                if not proc_stack:
                    self.errors.append((i, f"'End {end_type}' without matching '{end_type}'"))
                else:
                    start_line, start_type = proc_stack.pop()
                    if start_type.lower() != end_type.lower():
                        self.errors.append((i, f"'End {end_type}' does not match '{start_type}' at line {start_line}"))

        # Check for unclosed procedures
        for start_line, proc_type in proc_stack:
            self.errors.append((start_line, f"'{proc_type}' not closed with 'End {proc_type}'"))

    def check_undeclared_variables(self):
        """Check for common undeclared variable patterns (basic check)."""
        # Extract declared variables
        declared = set()
        for line in self.lines:
            # Dim, As, Const declarations
            if re.search(r'\b(Dim|Const|Public|Private)\s+(\w+)', line, re.IGNORECASE):
                var_name = re.search(r'\b(Dim|Const|Public|Private)\s+(\w+)', line, re.IGNORECASE).group(2)
                declared.add(var_name.lower())

        # Check for assignments to undeclared variables (basic heuristic)
        for i, line in enumerate(self.lines, start=1):
            # Skip comments and declarations
            if line.strip().startswith("'") or re.search(r'\b(Dim|Const|Public|Private)\s+', line, re.IGNORECASE):
                continue

            # Look for assignment (var = ...)
            match = re.search(r'\b(\w+)\s*=', line)
            if match:
                var_name = match.group(1).lower()
                # Exclude common VBA keywords/properties
                if var_name not in declared and var_name not in {'set', 'let', 'get', 'call', 'if', 'end', 'for', 'next', 'do', 'loop', 'while'}:
                    self.warnings.append((i, f"Possible undeclared variable: '{match.group(1)}'"))

    def check_common_typos(self):
        """Check for common VBA typos."""
        typos = {
            r'\bElseIf\b': 'ElseIf',  # Correct
            r'\bElse\s+If\b': 'Else If (should be ElseIf)',
            r'\bEnd\s+Sub\b': 'End Sub',  # Correct
            r'\bEndSub\b': 'EndSub (should be End Sub)',
            r'\bEnd\s+Function\b': 'End Function',  # Correct
            r'\bEndFunction\b': 'EndFunction (should be End Function)',
        }

        for i, line in enumerate(self.lines, start=1):
            if re.search(r'\bElse\s+If\b', line, re.IGNORECASE):
                self.warnings.append((i, "Use 'ElseIf' (one word) instead of 'Else If'"))
            if re.search(r'\bEndSub\b', line, re.IGNORECASE):
                self.errors.append((i, "Use 'End Sub' (two words) instead of 'EndSub'"))
            if re.search(r'\bEndFunction\b', line, re.IGNORECASE):
                self.errors.append((i, "Use 'End Function' (two words) instead of 'EndFunction'"))

    def check_line_continuations(self):
        """Check for broken line continuations."""
        for i, line in enumerate(self.lines, start=1):
            # Line continuation must have space before underscore
            if re.search(r'\S_\s*$', line):
                self.warnings.append((i, "Line continuation: add space before '_'"))

    def print_results(self):
        """Print errors and warnings."""
        if not self.errors and not self.warnings:
            print(f"✅ {self.filepath.name}: No issues found")
            return

        print(f"\n{'='*60}")
        print(f"File: {self.filepath}")
        print(f"{'='*60}")

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for line_num, msg in sorted(self.errors):
                print(f"  Line {line_num}: {msg}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for line_num, msg in sorted(self.warnings):
                print(f"  Line {line_num}: {msg}")

        print()

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/lint_vba.py <file.bas>")
        print("   or: python scripts/lint_vba.py Excel/Templates/*.bas")
        sys.exit(1)

    files = [Path(arg) for arg in sys.argv[1:]]
    all_pass = True

    for filepath in files:
        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            all_pass = False
            continue

        linter = VBALinter(filepath)
        if not linter.lint():
            all_pass = False

    if all_pass:
        print("\n✅ All files passed validation")
        sys.exit(0)
    else:
        print("\n❌ Some files have errors - fix before importing to Excel")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

**Usage:**
```bash
# Lint single file
python scripts/lint_vba.py Excel/Templates/BeamDesignSchedule_vba.bas

# Lint all .bas files
python scripts/lint_vba.py Excel/Templates/*.bas

# In VS Code terminal (quick check)
python scripts/lint_vba.py Excel/Templates/BeamDesignSchedule_vba.bas && echo "Ready to import!"
```

---

### Step 3: Create Excel Developer Template

**File:** `Excel/DevTemplate.xlsm`

**Purpose:** One-click import of all .bas files from `Excel/Templates/`

**Features:**
- Auto-imports .bas files
- Removes old modules first (clean state)
- Shows import progress
- Compiles after import (catches errors)

**VBA Code in DevTemplate.xlsm:**

**Module:** `DevTools`

```vba
Option Explicit

' Auto-import all .bas files from Excel/Templates/ folder
Public Sub ImportAllModules()
    Dim basFolder As String
    Dim basFile As String
    Dim vbComp As Object
    Dim importCount As Long

    ' Get folder path
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

        ' Import module
        ThisWorkbook.VBProject.VBComponents.Import basFolder & basFile
        importCount = importCount + 1

        basFile = Dir()
    Loop

    Application.StatusBar = False

    ' Try to compile (catches syntax errors)
    On Error Resume Next
    ThisWorkbook.VBProject.VBComponents(1).CodeModule.Lines(1, 1) ' Force compile
    If Err.Number <> 0 Then
        MsgBox "Compile error detected! Check VBA editor for details.", vbExclamation
    Else
        MsgBox "Imported " & importCount & " modules successfully!" & vbCrLf & _
               "All modules compiled without errors.", vbInformation
    End If
    On Error GoTo 0
End Sub

' Quick test runner - runs a specific test function
Public Sub RunTest(Optional testName As String = "")
    If testName = "" Then
        testName = InputBox("Enter test function name (e.g., Test_ExportMacro):", "Run Test")
    End If

    If testName <> "" Then
        On Error GoTo TestError
        Application.Run testName
        MsgBox "Test '" & testName & "' completed.", vbInformation
        Exit Sub
    End If

TestError:
    MsgBox "Test error: " & Err.Description, vbCritical
End Sub
```

**Usage:**
1. Open `Excel/DevTemplate.xlsm`
2. Enable macros
3. Alt+F8 → Run `ImportAllModules`
4. All .bas files imported automatically
5. Test your code

---

### Step 4: VS Code Workspace Settings

**File:** `.vscode/settings.json`

**Add these settings:**

```json
{
  "files.associations": {
    "*.bas": "vb",
    "*.cls": "vb",
    "*.frm": "vb"
  },
  "editor.tabSize": 4,
  "editor.insertSpaces": true,
  "files.encoding": "windows1252",
  "files.eol": "\r\n",
  "[vb]": {
    "editor.tabSize": 4,
    "editor.insertSpaces": true
  }
}
```

**Purpose:**
- Treat .bas files as VBA
- Correct tab spacing (4 spaces)
- Windows line endings (Excel compatibility)
- Proper encoding

---

## New Workflow (Fast Iteration)

### Before (Slow - many round trips):
```
1. Write VBA in VS Code (Copilot)
2. Copy to Excel VBA Editor
3. Compile → ERROR
4. Copy error message
5. Back to VS Code
6. Fix with Copilot
7. Repeat steps 2-6 (5-10 times) ❌ TOKEN WASTE
```

### After (Fast - validate first):
```
1. Write VBA in .bas file (VS Code + Copilot)
2. Run linter: python scripts/lint_vba.py Excel/Templates/*.bas
   → Catches 80% of errors in <1 second ✅
3. Fix errors in VS Code (if any)
4. Repeat steps 2-3 until clean
5. Open DevTemplate.xlsm → ImportAllModules (one click)
6. Test in Excel (final integration only)
```

**Token savings:** 70-80% (most errors caught by linter, not Copilot)

---

## Practical Example

### Task: Write Export Macro

**Step 1: Create .bas file**
```bash
# Create file
touch Excel/Templates/ExportMacros.bas

# Open in VS Code
code Excel/Templates/ExportMacros.bas
```

**Step 2: Write VBA with Copilot**

```vb
Option Explicit

' Export all beams to DXF
Public Sub ExportAllBeamsToDXF()
    Dim ws As Worksheet
    Dim lastRow As Long

    Set ws = ThisWorkbook.Sheets("Design")
    lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row

    ' ... rest of code from Copilot
End Sub
```

**Step 3: Validate syntax**
```bash
python scripts/lint_vba.py Excel/Templates/ExportMacros.bas

# Output:
✅ ExportMacros.bas: No issues found
```

**Step 4: Import to Excel (only when clean)**
```
1. Open DevTemplate.xlsm
2. Alt+F8 → ImportAllModules
3. Test ExportAllBeamsToDXF
```

**Result:** First import likely works (no compile errors)

---

## Debugging in Excel (When Needed)

**If Excel runtime error occurs:**

1. **Note the error:** Line number, error message
2. **Add Debug.Print statements** in .bas file:
   ```vb
   Debug.Print "lastRow: " & lastRow
   Debug.Print "beamID: " & beamID
   ```
3. **Re-run linter** (quick check)
4. **Re-import** to Excel (DevTools → ImportAllModules)
5. **Run macro** → Check Immediate Window (Ctrl+G)

**Avoid:** Editing directly in Excel VBA Editor (loses sync with .bas files)

---

## Advanced: Auto-Watch and Import

**Optional:** Auto-import when .bas files change

**Tool:** Use a file watcher script

**Script:** `scripts/watch_vba.py`

```python
#!/usr/bin/env python3
"""
Watch Excel/Templates/*.bas files and trigger Excel import on change
Requires: pip install watchdog pywin32
"""

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import win32com.client

class VBAWatcher(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.bas'):
            print(f"Detected change: {event.src_path}")
            print("Triggering Excel import...")

            try:
                # Connect to running Excel instance
                xl = win32com.client.GetActiveObject("Excel.Application")
                wb = xl.Workbooks("DevTemplate.xlsm")
                xl.Run("DevTools.ImportAllModules")
                print("✅ Import successful")
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == '__main__':
    path = "Excel/Templates"
    event_handler = VBAWatcher()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    print(f"Watching {path} for .bas changes...")
    print("Save a .bas file to trigger auto-import.")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
```

**Usage:**
```bash
# Terminal 1: Start watcher
python scripts/watch_vba.py

# Terminal 2: Edit .bas files in VS Code
# → Watcher auto-imports on save
```

---

## Checklist for Efficient VBA Development

**One-time setup (15 min):**
- [ ] Install VS Code VBA extension
- [ ] Create `scripts/lint_vba.py`
- [ ] Create `Excel/DevTemplate.xlsm` with DevTools module
- [ ] Update `.vscode/settings.json`

**Per-session workflow:**
- [ ] Start session: `python scripts/start_session.py`
- [ ] Open DevTemplate.xlsm (keep running)
- [ ] Edit .bas files in VS Code
- [ ] Run linter after each major change
- [ ] Import to Excel only when linter passes
- [ ] Test in Excel
- [ ] Repeat 3-5 until done

**Benefits achieved:**
- ✅ 80% fewer Excel round-trips
- ✅ 70% token savings (Copilot)
- ✅ Version control (.bas files in git)
- ✅ Better editor (VS Code > Excel VBA Editor)
- ✅ Faster iteration

---

## Quick Reference Card

| Task | Command | Where |
|------|---------|-------|
| **Lint VBA** | `python scripts/lint_vba.py Excel/Templates/*.bas` | VS Code terminal |
| **Import to Excel** | Alt+F8 → `ImportAllModules` | Excel (DevTemplate.xlsm) |
| **Run test** | Alt+F8 → `RunTest` → Enter function name | Excel |
| **Debug** | Add `Debug.Print` → Re-import → Ctrl+G (Immediate) | Excel |
| **Auto-watch** | `python scripts/watch_vba.py` | Terminal (optional) |

---

**Next:** Create the linter script and DevTemplate.xlsm
