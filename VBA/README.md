# VBA - IS 456 Beam Design Library (Visual Basic for Applications)

> **Purpose:** VBA implementation of IS 456:2000 beam design calculations for Excel
> **Owner:** Maintainers
> **Last Updated:** 2026-01-10
> **Parity With:** Python implementation in `Python/structural_lib/`

## Directory Structure

```
VBA/
├── Modules/          # Core calculation modules (.bas)
├── Tests/            # VBA test suites
├── Examples/         # Example usage and demos
└── README.md         # This file
```

## Module Naming Convention

| Module | Purpose |
|--------|---------|
| `M01_Constants.bas` | Material and code constants |
| `M02_Materials.bas` | Concrete and steel properties |
| `M03_Flexure.bas` | Flexural design calculations |
| `M04_Shear.bas` | Shear design calculations |
| `M05_Detailing.bas` | Reinforcement detailing rules |
| `M06_Tables.bas` | IS 456 table lookups |
| `M07_Serviceability.bas` | Deflection and cracking |
| `M08_API.bas` | Public API functions |
| `M09_UDFs.bas` | Excel User Defined Functions |
| `M15-M17` | Additional utilities |

## Guidelines

### Mac VBA Safety (CRITICAL)

When modifying VBA code for Mac compatibility:

1. **Wrap dimension multiplications in `CDbl()`:**
   ```vb
   ' ❌ Wrong
   Area = b * d

   ' ✅ Correct
   Area = CDbl(b) * CDbl(d)
   ```

2. **Never pass inline boolean expressions to ByVal:**
   ```vb
   ' ❌ Wrong
   Call SomeFunc(x > y)

   ' ✅ Correct
   Dim result As Boolean
   result = (x > y)
   Call SomeFunc(result)
   ```

3. **No Debug.Print interleaved with floating-point math**

4. **Prefer Long over Integer**

### Python Parity

- Every VBA function should have a Python equivalent
- Calculation results should match within tolerance
- Use same formula references (IS 456 clause numbers)

## For AI Agents

When modifying VBA code:

1. **Check Python equivalent first** - Ensure behavior matches
2. **Follow Mac safety rules** - Critical for cross-platform
3. **Update both implementations** - Keep Python/VBA in sync
4. **Test in Excel** - VBA requires manual testing
5. **Document clause references** - Add IS 456 clause numbers in comments

### Testing VBA

```
1. Open Excel/BeamDesignApp.xlsm
2. Run tests from Developer > Macros
3. Compare results with Python: pytest tests/test_flexure.py
```

### VBA Smoke Test Automation (macOS)

Quick smoke tests can be run via Excel automation (macOS only):

```
.venv/bin/python scripts/run_vba_smoke_tests.py
```

Defaults:
- Workbook: Excel/BeamDesignApp.xlsm
- Macro: Test_RunAll.RunAllVBATests

Examples:

```
.venv/bin/python scripts/run_vba_smoke_tests.py --workbook Excel/StructEng_BeamDesign_v0.5.xlsm
.venv/bin/python scripts/run_vba_smoke_tests.py --macro Test_RunAll.RunAllVBATests --macro Integration_TestHarness.Run_Integration_TestSuite
```

## Archive Policy

- This folder is **not auto-archived**
- Old modules should be explicitly versioned or removed
- Keep test files current with module changes
