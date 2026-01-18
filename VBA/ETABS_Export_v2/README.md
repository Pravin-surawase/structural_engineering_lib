# ETABS Export for Streamlit

**One-click export of ETABS model data to CSV for Streamlit visualization.**

## 🚀 Quick Start (2 Minutes)

### Step 1: Add Reference (One Time Only)
1. Open Excel → Press `Alt+F11` (VBA Editor)
2. **Tools → References → Browse**
3. Navigate to: `C:\Program Files\Computers and Structures\ETABS XX\ETABS.exe`
4. Check "ETABS Object Library" → OK

### Step 2: Import Module
1. **File → Import File**
2. Select your export module:
   - `ETABS_SimpleExport.bas` - Basic beam forces (one CSV)
   - `ETABS_ComprehensiveExport.bas` - **NEW** Full 3D model data (4 CSVs)

### Step 3: Export
1. Open your model in ETABS (with analysis completed)
2. In Excel: Press `Alt+F8`
3. Run one of:
   - `ExportBeamsSimple` - Quick beam data
   - `ExportAllForVisualization` - **Complete 3D model data**
   - `ExportGeometryOnly` - Fast geometry without forces
4. Files saved to: `Documents\ETABS_Export\<timestamp>\`

---

## 📊 Comprehensive Export (3D Visualization)

**`ExportAllForVisualization` produces 4 CSVs:**

### 1. `stories.csv` - Story Definitions
| Column | Description | Unit |
|--------|-------------|------|
| StoryName | Floor name | - |
| Elevation_m | Elevation from base | m |

### 2. `frames_geometry.csv` - Frame Coordinates & Connectivity
| Column | Description | Unit |
|--------|-------------|------|
| UniqueName | ETABS unique ID | - |
| Label | User label (e.g., B1, C1) | - |
| Story | Story level | - |
| FrameType | Beam/Column/Other | - |
| SectionName | Section property name | - |
| Point1Name, Point2Name | End point IDs | - |
| Point1X, Point1Y, Point1Z | Start coordinates | m |
| Point2X, Point2Y, Point2Z | End coordinates | m |
| Angle, CardinalPoint | Orientation | degrees |

### 3. `frames_properties.csv` - Section Dimensions
| Column | Description | Unit |
|--------|-------------|------|
| SectionName | Property name | - |
| Width_mm | Section width | mm |
| Depth_mm | Section depth | mm |
| Material | Material name | - |
| FrameType | Beam/Column | - |

### 4. `beam_forces.csv` - Envelope Forces
| Column | Description | Unit |
|--------|-------------|------|
| UniqueName | ETABS unique ID | - |
| Label | User label | - |
| Story | Story level | - |
| SectionName | Property name | - |
| Width_mm, Depth_mm | Dimensions | mm |
| Span_m | Beam length | m |
| Mu_max_kNm | Max positive moment | kN·m |
| Mu_min_kNm | Max negative moment | kN·m |
| Vu_max_kN | Max shear force | kN |

---

## 🎯 Simple Export (Beam Design Only)

**`ExportBeamsSimple` produces 1 CSV:**

| Column | Description | Unit |
|--------|-------------|------|
| Label | Beam name from ETABS | - |
| Story | Story level | - |
| Width_mm | Beam width | mm |
| Depth_mm | Beam depth | mm |
| Span_m | Beam span length | m |
| Mu_max_kNm | Max positive moment | kN·m |
| Mu_min_kNm | Max negative moment | kN·m |
| Vu_max_kN | Max shear force | kN |
| fck | Concrete grade | MPa |
| fy | Steel grade | MPa |

---

## ❓ Troubleshooting

### "User-defined type not defined"
→ You forgot Step 1. Add the ETABS reference.

### "Cannot connect to ETABS"
→ Make sure ETABS is open with a model loaded.

### "No results" / All zeros
→ Run analysis in ETABS first (F5).

---

## 📁 Files

| File | Purpose | Functions |
|------|---------|-----------|
| `ETABS_ComprehensiveExport.bas` | **3D Visualization** | `ExportAllForVisualization`, `ExportGeometryOnly` |
| `ETABS_SimpleExport.bas` | Beam design | `ExportBeamsSimple` |
| `ETABS_Export_Config.bas` | Legacy config | Reference only |
| `GUIDE_Implementation.md` | Technical details | Troubleshooting |

---

## 🔄 Workflow Summary

```
ETABS Model → Run Analysis → Export → CSVs → Streamlit 3D Visualization
```

## ✅ Features

- Works with ETABS 2019-2024
- Efficient `GetAllFrames()` API (single call)
- Exports beams AND columns
- Frame coordinates for 3D rendering
- Connectivity data (Point1, Point2 names)
- Story definitions for multi-level models
- Envelope forces for design calculations

## 📋 Requirements

- Excel 2016+
- ETABS 2019+ installed
- Model with frame objects
- Analysis run (for forces)

## 📝 Notes

- All coordinates in meters (SetPresentUnits = kN_m_C)
- Section dimensions converted to mm for design
- Envelope values = worst case across ALL load combos
