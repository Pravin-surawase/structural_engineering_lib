# xlwings Installation - Test Results

**Date:** 2026-01-01
**Tester:** Pravin
**Task:** 0.1 (xlwings Excel integration)

## Environment

- **OS:** macOS (fill exact version)
- **Excel Version:** 16.104 (25121423) (macOS)
- **Python:** 3.9.6 (.venv)
- **xlwings:** 0.33.19 (.venv)

## Installation Steps Completed

- [x] Quit and restart Excel (Cmd-Q, reopen)
- [x] Enabled "Trust access to the VBA project object model"
- [x] Verified xlwings add-in loaded (Tools → Excel Add-ins → xlwings)

## UDF Test Results

## IMPORTANT

- xlwings worksheet UDFs (formulas like `=IS456_MuLim(...)`) are **Windows-only**.
- On **Excel for macOS**, worksheet UDFs are not supported, so formula-based testing will show `#NAME?` and the xlwings ribbon may not offer the expected UDF import UI.

| Function | Formula Tested | Expected | Actual | Status | Notes |
|----------|----------------|----------|--------|--------|-------|
| IS456_MuLim | `=IS456_MuLim(300,450,25,500)` | 202.91 |  |  |  |
| IS456_AstRequired | `=IS456_AstRequired(300,450,120,25,500)` | 682.3 |  |  |  |
| IS456_BarCallout | `=IS456_BarCallout(5,16)` | 5-16φ |  |  |  |
| IS456_StirrupCallout | `=IS456_StirrupCallout(2,8,150)` | 2L-8φ@150 c/c |  |  |  |
| IS456_Ld | `=IS456_Ld(16,25,500)` | 752 |  |  |  |
| IS456_AstRequired (over) | `=IS456_AstRequired(300,450,300,25,500)` | Over-Reinforced |  |  |  |

## Windows UDF Test Results (REQUIRED TO COMPLETE TASK 0.1)

Fill this section in on a Windows machine with Excel:

- **OS:** Windows (fill exact version)
- **Excel Version:** (fill)
- **Python:** 3.9.6 (.venv) or project-supported Python
- **xlwings:** 0.33.19 (or project-supported)

| Function | Formula Tested | Expected | Actual | Status | Notes |
|----------|----------------|----------|--------|--------|-------|
| IS456_MuLim | `=IS456_MuLim(300,450,25,500)` | 202.91 |  |  |  |
| IS456_AstRequired | `=IS456_AstRequired(300,450,120,25,500)` | 682.3 |  |  |  |
| IS456_BarCallout | `=IS456_BarCallout(5,16)` | 5-16φ |  |  |  |
| IS456_StirrupCallout | `=IS456_StirrupCallout(2,8,150)` | 2L-8φ@150 c/c |  |  |  |
| IS456_Ld | `=IS456_Ld(16,25,500)` | 752 |  |  |  |
| IS456_AstRequired (over) | `=IS456_AstRequired(300,450,300,25,500)` | Over-Reinforced |  |  |  |

## Performance

- **First formula delay:** ___ seconds
- **Subsequent formula delay:** ___ seconds
- **Overall:** Acceptable / Needs optimization

## Issues Encountered

- None / (list issues + fixes)

## Conclusion

- [ ] All 6 UDFs working correctly in Excel
- [ ] Ready to proceed to Task 1.1 (BeamDesignSchedule template)
- [ ] xlwings integration VERIFIED
