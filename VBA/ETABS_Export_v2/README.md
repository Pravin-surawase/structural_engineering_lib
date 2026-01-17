# ETABS Export VBA v2.1

**Two-file solution for exporting ETABS data to Streamlit structural engineering app.**

## Files

| File | Purpose | Lines |
|------|---------|-------|
| `mod_ETABS_Core.bas` | Connection, analysis, logging, utilities | ~300 |
| `mod_ETABS_Export.bas` | All export functions | ~450 |

**Total: ~750 lines in 2 files** (vs 10 files previously)

## Quick Start

### 1. Setup (One Time)

1. Open Excel
2. Press `Alt+F11` → VBA Editor
3. File → Import File → Select both `.bas` files
4. Tools → References → Check "ETABSv1" (optional, for IntelliSense)

### 2. Usage

1. Open your model in ETABS
2. Run analysis (F5) if not done
3. In Excel, press `Alt+F8` → Select `ExportETABSData` → Run
4. Files saved to: `Documents\ETABS_Export\`
5. Upload `beam_forces.csv` to Streamlit app

## Output Files

| File | Purpose | Streamlit Use |
|------|---------|---------------|
| `beam_forces.csv` | **PRIMARY** - Frame forces | ETABS Import page |
| `base_reactions.csv` | Foundation loads | Future |
| `column_design.csv` | Column reinforcement | Future |
| `beam_design.csv` | Beam reinforcement | Future |
| `sections.csv` | Section assignments | Reference |
| `stories.csv` | Story definitions | Reference |
| `metadata.json` | Export info & units | Validation |

## CSV Format (beam_forces.csv)

```csv
Story,Label,Output Case,Station,M3,V2,P
Story1,B1,1.5DL+LL,0.000,125.500,85.200,0.000
Story1,B1,1.5DL+LL,1500.000,98.300,42.100,0.000
```

| Column | Description | Unit |
|--------|-------------|------|
| Story | Floor name | - |
| Label | Beam ID | - |
| Output Case | Load combo | - |
| Station | Location along beam | mm |
| M3 | Bending moment | kN·m |
| V2 | Shear force | kN |
| P | Axial force | kN |

## Features

- ✅ Automatic unit conversion (any ETABS units → kN, mm)
- ✅ Works with ETABS 2019-2024
- ✅ DatabaseTables (fast) + Direct API (reliable) fallback
- ✅ Exports all load cases and combinations
- ✅ Column/Beam design results if available
- ✅ Base reactions for foundation design
- ✅ Detailed logging for troubleshooting

## Troubleshooting

### "Cannot connect to ETABS"
- Start ETABS first
- Open a model (not blank)

### "Analysis failed"
- Check ETABS for errors (red messages)
- Model may have issues

### "No frames found"
- Model has no frame objects
- Or model is empty

### "Design results not available"
- Run Design → Start Design in ETABS
- Then re-export

## Key Improvements from v1

1. **2 files instead of 10** - Easier to manage
2. **GetAllFrames()** - More efficient than GetNameList loop
3. **Design results** - Column/Beam reinforcement export
4. **Base reactions** - Foundation design data
5. **Better logging** - Detailed troubleshooting info
6. **Unit handling** - Robust conversion for all ETABS units

## Requirements

- Excel 2016+
- ETABS 2019+ installed
- Model with frame objects
- Analysis run (for forces)
- Design run (for reinforcement - optional)

## Migration from v1

If you have the old 10-file version:
1. Delete all old `mod_*.bas` files from VBA
2. Import the new 2 files
3. That's it!

## Support

Check log file at: `Documents\ETABS_Export\export_*.log`
