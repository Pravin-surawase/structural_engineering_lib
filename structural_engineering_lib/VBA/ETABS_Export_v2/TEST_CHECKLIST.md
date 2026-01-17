# ETABS Export v2.1 - Test Checklist

## Pre-Test Requirements

- [ ] ETABS 2019+ installed
- [ ] Excel 2016+ available
- [ ] Sample ETABS model with:
  - [ ] Frame objects (beams/columns)
  - [ ] Load cases defined
  - [ ] Analysis run successfully
  - [ ] (Optional) Concrete design run

## Installation Test

- [ ] Import `mod_ETABS_Core.bas` to Excel VBA
- [ ] Import `mod_ETABS_Export.bas` to Excel VBA
- [ ] No compile errors (Debug → Compile VBAProject)
- [ ] `ExportETABSData` appears in macro list (Alt+F8)

## Connection Test

| Test | Expected | Pass |
|------|----------|------|
| Run with ETABS closed | "ETABS is not running" dialog | [ ] |
| Run with ETABS open (no model) | "No model loaded" message | [ ] |
| Run with model open | Connects successfully | [ ] |

## Analysis Test

| Test | Expected | Pass |
|------|----------|------|
| Model analyzed | "Analysis OK" in log | [ ] |
| Model not analyzed | Runs analysis, completes | [ ] |
| Analysis failure | Error message, abort | [ ] |

## Export Test - Beam Forces (PRIMARY)

| Test | Expected | Pass |
|------|----------|------|
| DatabaseTables works | Fast export, uses table name | [ ] |
| DatabaseTables fails | Falls back to Direct API | [ ] |
| CSV created | `raw\beam_forces.csv` exists | [ ] |
| CSV has header | `Story,Label,Output Case,Station,M3,V2,P` | [ ] |
| CSV has data | More than 1 row | [ ] |
| Units correct | M3 in kN·m, V2 in kN, Station in mm | [ ] |

## Export Test - Optional Data

| Export | File Created | Data Valid | Pass |
|--------|--------------|------------|------|
| Base Reactions | `base_reactions.csv` | Fx,Fy,Fz in kN | [ ] |
| Column Design | `column_design.csv` | PMM ratios | [ ] |
| Beam Design | `beam_design.csv` | Ast values | [ ] |
| Sections | `sections.csv` | Section names | [ ] |
| Stories | `stories.csv` | Story names | [ ] |
| Metadata | `metadata.json` | Valid JSON | [ ] |

## Unit Conversion Test

Test with different ETABS unit systems:

| ETABS Units | Force→kN | Length→mm | Moment→kN·m | Pass |
|-------------|----------|-----------|-------------|------|
| kN, m | 1.0 | 1000 | 1.0 | [ ] |
| kN, mm | 1.0 | 1.0 | 0.001 | [ ] |
| kip, ft | 4.448 | 304.8 | 1.355 | [ ] |
| N, mm | 0.001 | 1.0 | 0.000001 | [ ] |

## Streamlit Integration Test

- [ ] Upload `beam_forces.csv` to Streamlit ETABS Import page
- [ ] Column detection successful
- [ ] Beam envelopes created
- [ ] Batch design runs
- [ ] Results display correctly

## Error Handling Test

| Scenario | Expected Behavior | Pass |
|----------|-------------------|------|
| Cancel during export | Graceful abort, partial files OK | [ ] |
| ETABS closes mid-export | Error message, log created | [ ] |
| Disk full | Error message | [ ] |
| Read-only output folder | Error message | [ ] |

## Performance Test

| Model Size | Export Time | Acceptable | Pass |
|------------|-------------|------------|------|
| Small (<100 frames) | <5 sec | <10 sec | [ ] |
| Medium (100-500 frames) | <30 sec | <60 sec | [ ] |
| Large (>500 frames) | <2 min | <5 min | [ ] |

## Log File Test

- [ ] Log file created in output folder
- [ ] Timestamps present
- [ ] All operations logged
- [ ] Errors clearly marked with "ERROR"
- [ ] Debug info available at LOG_LEVEL=0

## Final Validation

- [ ] All PRIMARY tests pass (Connection, Analysis, Beam Forces)
- [ ] Log file useful for debugging
- [ ] CSV format matches Streamlit expectations
- [ ] No VBA compile errors
- [ ] Documentation accurate

## Sign-off

**Tested by:** ________________  
**Date:** ________________  
**ETABS Version:** ________________  
**Model Used:** ________________  
**Result:** ☐ PASS / ☐ FAIL

### Notes:
```




```
