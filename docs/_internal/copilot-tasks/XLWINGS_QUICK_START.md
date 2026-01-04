# xlwings Quick Start Guide

**Date:** 2026-01-01
**Status:** Installation Complete ✅

## Platform Note (IMPORTANT)

- **Worksheet UDFs (Excel formulas like `=IS456_MuLim(...)`) are Windows-only in xlwings.**
- On **Excel for macOS**, worksheet UDFs are not supported, so you will not be able to use “Import Functions/UDF Modules” for formulas (and will likely see `#NAME?`).
- Use this guide’s UDF testing section on **Windows Excel**.

---

## Installation Checklist

- [x] Install xlwings in virtual environment
- [x] Install Excel add-in: `.venv/bin/xlwings addin install`
- [ ] Restart Excel (fully quit, then reopen)
- [ ] Enable VBA project access (see below)
- [ ] (Windows) Test first UDF formula

---

## Excel Settings (One-Time Setup)

**Enable VBA Project Access:**

1. Excel → Settings (or Preferences)
2. Security & Privacy → Trust Center Settings
3. Privacy tab
4. ☑ "Trust access to the VBA project object model"
5. OK → OK

**Why needed:** xlwings needs this permission to connect Excel with Python.

---

## Testing Python UDFs in Excel

### Quick Test (Copy-Paste into Excel)

| Formula | Expected Result | What it Calculates |
|---------|----------------|-------------------|
| `=IS456_MuLim(300,450,25,500)` | 202.91 | Limiting moment (kN·m) |
| `=IS456_AstRequired(300,450,120,25,500)` | 682.3 | Required steel area (mm²) |
| `=IS456_AstRequired(300,450,300,25,500)` | Over-Reinforced | Over-reinforced condition |
| `=IS456_BarCallout(5,16)` | 5-16φ | Bar notation string |
| `=IS456_StirrupCallout(2,8,150)` | 2L-8φ@150 c/c | Stirrup notation string |
| `=IS456_Ld(16,25,500)` | 752 | Development length (mm) |

---

## Available Python UDFs

All functions from `Python/structural_lib/excel_bridge.py` are available in Excel:

### Flexure Functions

#### IS456_MuLim
```excel
=IS456_MuLim(b, d, fck, fy)
```
- **b** = Beam width (mm)
- **d** = Effective depth (mm)
- **fck** = Concrete grade (N/mm²)
- **fy** = Steel grade (N/mm²)
- **Returns:** Limiting moment (kN·m)

#### IS456_AstRequired
```excel
=IS456_AstRequired(b, d, mu, fck, fy)
```
- **b** = Beam width (mm)
- **d** = Effective depth (mm)
- **mu** = Factored moment (kN·m)
- **fck** = Concrete grade (N/mm²)
- **fy** = Steel grade (N/mm²)
- **Returns:** Required Ast (mm²) or "Over-Reinforced"

### Shear Functions

#### IS456_ShearSpacing
```excel
=IS456_ShearSpacing(vu, b, d, fck, fy, dia_stirrup, pt)
```
- **vu** = Factored shear force (kN)
- **b** = Beam width (mm)
- **d** = Effective depth (mm)
- **fck** = Concrete grade (N/mm²)
- **fy** = Steel grade (N/mm²)
- **dia_stirrup** = Stirrup diameter (mm)
- **pt** = Tension steel percentage (%)
- **Returns:** Required spacing (mm) or "Shear Failure"

### Detailing Functions

#### IS456_BarCallout
```excel
=IS456_BarCallout(num_bars, dia)
```
- **num_bars** = Number of bars
- **dia** = Bar diameter (mm)
- **Returns:** "5-16φ" format string

#### IS456_StirrupCallout
```excel
=IS456_StirrupCallout(legs, dia, spacing)
```
- **legs** = Number of legs (2 or 4)
- **dia** = Stirrup diameter (mm)
- **spacing** = Spacing (mm)
- **Returns:** "2L-8φ@150 c/c" format string

#### IS456_Ld
```excel
=IS456_Ld(dia, fck, fy)
```
- **dia** = Bar diameter (mm)
- **fck** = Concrete grade (N/mm²)
- **fy** = Steel grade (N/mm²)
- **Returns:** Development length (mm)

---

## Troubleshooting

### Formula shows #NAME? error

**Cause:** Excel can't find the Python function.

**Fix:**
1. Check xlwings add-in is enabled: Excel → Tools → Excel Add-ins → check "xlwings"
2. Restart Excel (Cmd-Q, then reopen)
3. Verify Python virtual environment is activated: `source .venv/bin/activate`

### Formula shows #VALUE! error

**Cause:** Python function returned an error or invalid value.

**Fix:**
1. Check input values are valid (positive numbers, fck/fy in correct range)
2. Look for "Error: ..." message in cell (click to expand)
3. Test function in Python first:
   ```bash
   python test_xlwings_bridge.py
   ```

### Excel shows "Can't find Python" error

**Cause:** xlwings can't locate the virtual environment.

**Fix:**
1. Prefer a project path **without spaces** (macOS Excel/xlwings can break otherwise).
   This repo uses iCloud path `.../Mobile Documents/...` which includes spaces.

2. Use the no-spaces symlink:
   - `/Users/Pravin/structural_engineering_lib`

3. Create (or use) `.xlwings.conf` in the project root:
   ```bash
   cat > .xlwings.conf << 'EOF'
   INTERPRETER,/Users/Pravin/structural_engineering_lib/.venv/bin/python
   PYTHONPATH,/Users/Pravin/structural_engineering_lib/Python
   UDF_MODULES,structural_lib.excel_bridge
   EOF
   ```

4. Restart Excel and click: xlwings → Import Functions

### macOS error: `sh: /Users/.../Mobile: Permission denied`

**Cause:** Unquoted path with spaces being passed to `sh`.

**Fix:** Switch xlwings settings (Interpreter/PYTHONPATH) to the no-spaces symlink path:
- `/Users/Pravin/structural_engineering_lib/.venv/bin/python`
- `/Users/Pravin/structural_engineering_lib/Python`

### Formulas work but are very slow

**Cause:** xlwings free version starts Python process for each cell calculation.

**Workaround (Free):**
- Batch calculations (calculate 10 beams at once, not cell-by-cell)
- Use manual calculation mode: Excel → Formulas → Calculation Options → Manual

**Long-term Fix:**
- Upgrade to xlSlim ($91/year) or PyXLL ($299/year) for 100x faster performance

---

## Development Workflow

### When Updating Python Code

1. Edit Python files in `Python/structural_lib/excel_bridge.py`
2. Save changes
3. **Restart Excel** (xlwings loads Python code on startup)
4. Test formulas again

**Pro Tip:** Keep Excel closed while developing Python code, open only for testing.

### Adding New UDFs

**Example: Add a new function for moment of resistance**

1. Edit `Python/structural_lib/excel_bridge.py`:
   ```python
   @xw.func
   @xw.arg("b", doc="Beam width (mm)")
   @xw.arg("d", doc="Effective depth (mm)")
   @xw.ret(doc="Moment of resistance (kN·m)")
   def IS456_MuR(b: float, d: float) -> float:
       """Calculate moment of resistance."""
       try:
           # Your Python logic here
           result = b * d * 0.138  # Example calculation
           return round(result, 2)
       except Exception as e:
           return f"Error: {str(e)}"
   ```

2. Save file
3. Restart Excel
4. Use in Excel: `=IS456_MuR(300, 450)`

---

## Next Steps

### Phase 1: Verify Installation (Today)
- [x] Install xlwings add-in
- [ ] Enable VBA project access
- [ ] Test 3-5 functions in Excel
- [ ] Verify all functions return correct values

### Phase 2: Create First Template (Next)
- [ ] Create BeamDesignSchedule.xlsm workbook
- [ ] Use Python UDFs for calculations (no VBA!)
- [ ] Add sample data
- [ ] Test full workflow

### Phase 3: Build More Templates (Future)
- [ ] QuickDesignSheet.xlsm
- [ ] ComplianceReport.xlsm
- [ ] BeamSizingHelper.xlsm
- [ ] All reusing same Python UDFs!

---

## Benefits vs VBA (What You Escaped!)

| Aspect | VBA (Before) | xlwings (Now) |
|--------|-------------|---------------|
| **Write code in** | VBA Editor | VS Code (Python) |
| **Syntax errors** | ❌ Constant | ✅ Never (Python linter) |
| **Testing** | Manual in Excel | pytest (automated) |
| **Code reuse** | ❌ Copy-paste | ✅ Import same module |
| **Token waste** | ❌ High | ✅ Zero |
| **Development time** | ~4 hours | ~30 minutes |

**You made the right choice! 🎉**

---

## Support

**If things don't work:**
1. Check this troubleshooting section
2. Test Python functions first: `python test_xlwings_bridge.py`
3. Check xlwings docs: https://docs.xlwings.org/
4. Ask GitHub Copilot to help debug specific errors

**Files to reference:**
- Python UDF definitions: `Python/structural_lib/excel_bridge.py`
- Python test script: `test_xlwings_bridge.py`
- Research document: `docs/_internal/copilot-tasks/PYTHON_EXCEL_RESEARCH_2025.md`
