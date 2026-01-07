# VBA Testing Guide

**Version:** 0.15.0
**Last Updated:** 2026-01-08<br>

## Quick Start

### Running All VBA Tests

1. **Open** the Excel workbook (`Excel/StructEng_BeamDesign_v0.5.xlsm` or `BeamDesignApp.xlsm`)
2. **Press** `Alt+F11` to open the VBA Editor
3. **Open** the Immediate Window (`Ctrl+G` or View → Immediate Window)
4. **Type** and press Enter:
   ```vb
   Test_RunAll.RunAllVBATests
   ```

### Expected Output

```
========================================
  STRUCTURAL ENGINEERING LIB - VBA TESTS
  Version: 0.15.0
  Date: 2025-12-26 14:30:00
========================================

NOTE: Review each suite's output for PASS/FAIL.
      Totals are not aggregated - check for FAIL lines.

>>> Suite: Structural (Flexure, Shear, Materials, Tables)
--- Starting Tests ---
PASS: Flexure_CalcOnly_MuLim_Lower
PASS: Flexure_CalcOnly_MuLim_Upper
...
--- Tests Completed ---

>>> Suite: Flanged Beams
[PASS] FlangedBeam_NA_InFlange
...

========================================
  RUN COMPLETE
========================================
  Suites Run: 7
  Suite Errors: 0
  Time Elapsed: 1.23 seconds
========================================
  All suites executed without runtime errors.
  >> Review output above for FAIL lines <<
========================================
```

> **Important:** The test runner executes all suites but cannot aggregate
> individual PASS/FAIL counts. Review the Immediate Window output manually
> for any `FAIL` or `[FAIL]` lines.

---

## Test Modules

| Module | File | Coverage |
|--------|------|----------|
| Structural | `Test_Structural.bas` | Flexure, Shear, Materials, Tables |
| Flanged | `Test_Flanged.bas` | T-beam, L-beam designs |
| Ductile | `Test_Ductile.bas` | IS 13920 detailing rules |
| Detailing | `Test_Detailing.bas` | Ld, lap, spacing, stirrups |
| DXF | `Test_DXF.bas` | DXF R12 export |
| Serviceability | `Test_Serviceability.bas` | Deflection, crack width |
| Parity | `Test_Parity.bas` | Python ↔ VBA verification |

> Note: Each module prints its own pass/fail lines. Counts vary by module.

---

## Running Individual Suites

From the Immediate Window, you can run individual test suites:

```vb
' Core structural tests
Test_Structural.RunAllTests

' Flanged beam tests
Test_Flanged.RunFlangedTests

' IS 13920 ductile detailing
Test_Ductile.RunDuctileTests

' Detailing (v0.7+)
Test_Detailing.Run_All_Detailing_Tests

' DXF export
Test_DXF.Run_All_DXF_Tests

' Serviceability (v0.8+)
Test_Serviceability.Run_All_Serviceability_Tests

' Integration/end-to-end
Integration_TestHarness.Run_Integration_TestSuite
```

---

## DXF Tests: What’s Verified

The DXF suite does both:

- **API-level checks:** drawing calls increase entity count (sanity check)
- **File-level checks:** exported DXF contains expected sections, layers, and entity types

The file-level checks validate key DXF text markers such as:

- `SECTION` / `HEADER` / `TABLES` / `ENTITIES` / `EOF`
- layer names like `BEAM_OUTLINE`, `REBAR_MAIN`, `REBAR_STIRRUP`, `DIMENSIONS`, `TEXT_CALLOUT`
- entity types like `LINE`, `CIRCLE`, `ARC`, `TEXT`

This is intentionally lightweight (no geometry parsing) but catches many “empty/partial DXF” regressions.

---

## Where DXF Test Files Go

The DXF suite writes temporary files using the first available temp location:

- macOS (Excel): `TMPDIR`
- Windows (Excel): `TEMP` or `TMP`
- Fallback: current working directory

The **full detailing** test keeps its DXF output for manual viewing and prints its location in the Immediate Window.

---

## Test Result Interpretation

### PASS/FAIL Format

All tests output to the Immediate Window in a consistent format:

```
PASS: TestName
FAIL: TestName | Expected X, Got Y
  [PASS] TestName
  [FAIL] TestName - Expected TRUE
```

### Tolerance Rules

Tests use tolerances matching Python parity:

| Quantity | Tolerance | Notes |
|----------|-----------|-------|
| Ast (mm²) | ±1.0 | Steel area |
| Asc (mm²) | ±1.0 | Compression steel |
| Mu (kN·m) | ±0.01 | Moment capacity |
| Spacing (mm) | ±1.0 | Stirrup spacing |
| Stress (N/mm²) | ±0.01 | τc, τv, etc. |
| Length (mm) | ±1.0 | Ld, lap length |

---

## Adding New Tests

### Template

```vb
Public Sub Test_NewFeature()
    On Error GoTo ErrHandler

    ' Arrange
    Dim input1 As Double: input1 = 100#

    ' Act
    Dim result As Double
    result = SomeModule.SomeFunction(input1)

    ' Assert
    AssertAlmostEqual result, 123.45, 0.01, "NewFeature_BasicCase"
    Exit Sub

ErrHandler:
    Debug.Print "FAIL: NewFeature_BasicCase [Error " & Err.Number & "]"
End Sub
```

### Assertion Helpers

Available in all test modules:

```vb
' Numeric comparison with tolerance
AssertAlmostEqual Actual, Expected, Tolerance, "TestName"

' Boolean assertions
AssertTrue Condition, "TestName"
AssertFalse Condition, "TestName"
```

---

## Troubleshooting

### "Sub or Function not defined"

The test module isn't loaded. Ensure all `Test_*.bas` files are imported:
1. File → Import File
2. Select from `VBA/Tests/` folder

### Tests Hang on Mac

Mac VBA has known issues with UDT returns. Workarounds applied:
- Use `#` suffix on all numeric literals
- Capture UDT members immediately after function call
- Use `Variant` intermediates for function returns

### No Output in Immediate Window

1. Ensure Immediate Window is visible (`Ctrl+G`)
2. Check for `On Error Resume Next` swallowing errors
3. Run a simple test: `Debug.Print "Hello"`

---

## Parity with Python

VBA tests should match Python parity test vectors in:
```
Python/tests/data/parity_test_vectors.json
```

When adding VBA tests for a calculation, verify the expected value matches the Python test vector.

---

## Related Documentation

- [API Reference](../reference/api.md) — Function signatures and contracts
- [VBA Guide](vba-guide.md) — VBA module architecture
- [Testing Strategy](testing-strategy.md) — Overall test philosophy
- [Known Pitfalls](../reference/known-pitfalls.md) — Mac VBA issues and workarounds
