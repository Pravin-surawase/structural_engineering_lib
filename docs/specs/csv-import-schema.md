# CSV Import Schema Specification

**Type:** Specification
**Audience:** Developers, Users
**Status:** Draft
**Importance:** High
**Created:** 2026-01-20
**Last Updated:** 2026-01-21
**Related Tasks:** TASK-CSV-01, TASK-CSV-02, TASK-3D-002

---

## Overview

This document defines the CSV schemas for importing beam data and geometry from structural analysis software (ETABS, SAFE, and generic formats) into structural_engineering_lib for design and visualization.

**Scope:**
- ETABS beam force exports (beam_forces.csv)
- ETABS frame geometry exports (frames_geometry.csv) — **NEW in Session 39**
- SAFE beam force exports
- Generic/custom CSV format

**Goals:**
- Import 1000+ beams efficiently
- Support real 3D building visualization
- Support multiple analysis software formats
- Clear validation and error reporting

---

## Supported Formats

### 1. ETABS Format (Primary)

ETABS exports beam forces via: Display → Show Tables → Element Forces - Beams

#### Required Columns

| Column | Aliases | Description | Units |
|--------|---------|-------------|-------|
| `Story` | Level, Floor | Floor/level name | Text |
| `Label` | Frame, Element, Beam, Name | Beam identifier | Text |
| `Output Case` | Load Case/Combo, Load Case, LoadCase, Combo, Case | Load combination | Text |
| `M3` | Moment3, Mz, BendingMoment | Bending moment about local 3 axis | kN·m |
| `V2` | Shear2, Vy, ShearForce | Shear force in local 2 plane | kN |

#### Optional Columns

| Column | Aliases | Description | Units | Default |
|--------|---------|-------------|-------|---------|
| `Station` | Distance, Location, Loc | Location along beam | mm or m | 0 |
| `Unique Name` | UniqueName, Unique, GUID | Internal ID | Text | "" |
| `P` | Axial, N, AxialForce | Axial force | kN | 0 |

#### Example ETABS CSV

```csv
Story,Label,Output Case,Station,M3,V2,P
Story1,B1,1.5(DL+LL),0,0,-125.5,0
Story1,B1,1.5(DL+LL),2500,180.2,0,0
Story1,B1,1.5(DL+LL),5000,0,125.5,0
Story1,B2,1.5(DL+LL),0,0,-98.3,0
Story1,B2,1.5(DL+LL),3000,145.6,0,0
```

---

### 1b. ETABS Frames Geometry Format (NEW)

ETABS exports frame geometry via the VBA export tool (frames_geometry.csv).
This provides 3D coordinates for real building visualization.

#### Required Columns

| Column | Description | Units | Example |
|--------|-------------|-------|---------|
| `UniqueName` | Internal ETABS ID | Text | "C1", "B23" |
| `Label` | User-friendly label | Text | "B1", "C2" |
| `Story` | Floor/level name | Text | "Story1", "Ground" |
| `FrameType` | Element type | Text | "Beam" or "Column" |
| `SectionName` | Section identifier | Text | "B230X450M20" |
| `Point1Name` | Node at start | Text | "1" |
| `Point2Name` | Node at end | Text | "2" |
| `Point1X` | X coordinate of start | m | 0.0 |
| `Point1Y` | Y coordinate of start | m | 0.0 |
| `Point1Z` | Z coordinate of start | m | 3.0 |
| `Point2X` | X coordinate of end | m | 4.5 |
| `Point2Y` | Y coordinate of end | m | 0.0 |
| `Point2Z` | Z coordinate of end | m | 3.0 |

#### Optional Columns

| Column | Description | Units | Default |
|--------|-------------|-------|---------|
| `Angle` | Rotation angle | degrees | 0.0 |
| `CardinalPoint` | Insertion point | 1-11 | 10 |

#### Example Frames Geometry CSV

```csv
UniqueName,Label,Story,FrameType,SectionName,Point1Name,Point2Name,Point1X,Point1Y,Point1Z,Point2X,Point2Y,Point2Z,Angle,CardinalPoint
B1,B1,Story1,Beam,RB300x500,1,2,0.0,0.0,3.0,4.5,0.0,3.0,0.0,10
B2,B2,Story1,Beam,RB300x500,2,3,4.5,0.0,3.0,9.0,0.0,3.0,0.0,10
C1,C1,Story1,Column,RC300x300,4,5,0.0,0.0,0.0,0.0,0.0,3.0,90.0,10
```

#### Python API for Geometry

```python
from structural_lib.etabs_import import (
    load_frames_geometry,
    merge_forces_and_geometry,
    FrameGeometry,
)

# Load geometry
frames = load_frames_geometry("frames_geometry.csv")
print(f"Loaded {len(frames)} frames")

# Filter by type
beams = [f for f in frames if f.frame_type == "Beam"]
columns = [f for f in frames if f.frame_type == "Column"]

# Access properties
for beam in beams[:5]:
    print(f"{beam.label}: {beam.length_m:.2f} m at Z={beam.point1_z} m")

# Merge with forces for visualization
envelopes = normalize_etabs_forces("beam_forces.csv")
merged = merge_forces_and_geometry(envelopes, frames)
```

---

### 2. SAFE Format

SAFE exports slab strip forces similarly to ETABS.

#### Column Mapping

| SAFE Column | Internal Mapping | Description |
|-------------|------------------|-------------|
| `Strip` | beam_id | Strip/band identifier |
| `SpanName` | beam_id (alternate) | Span name |
| `M22` | m3 | Moment about 2 axis |
| `V23` | v2 | Shear in 23 plane |
| `Position` | station | Location along strip |

#### Example SAFE CSV

```csv
Strip,SpanName,LoadCombo,Position,M22,V23
Strip1-A,Span1,1.5DL+1.5LL,0,0,-85.2
Strip1-A,Span1,1.5DL+1.5LL,1500,120.5,0
Strip1-A,Span1,1.5DL+1.5LL,3000,0,85.2
```

---

### 3. Generic Format (Recommended for New Projects)

Simplified format for custom data or manual entry.

#### Required Columns

| Column | Description | Units | Example |
|--------|-------------|-------|---------|
| `beam_id` | Unique beam identifier | Text | "B1", "GF-B1" |
| `mu_knm` | Design moment (factored) | kN·m | 180.5 |
| `vu_kn` | Design shear (factored) | kN | 125.0 |

#### Optional Columns

| Column | Description | Units | Default |
|--------|-------------|-------|---------|
| `story` | Level/floor identifier | Text | "" |
| `span_mm` | Clear span | mm | 5000 |
| `b_mm` | Beam width | mm | 300 |
| `D_mm` | Total depth | mm | 500 |
| `d_mm` | Effective depth | mm | 450 |
| `fck_nmm2` | Concrete strength | N/mm² | 25 |
| `fy_nmm2` | Steel yield strength | N/mm² | 500 |
| `exposure` | Exposure condition | Text | "Moderate" |
| `support` | Support condition | Text | "Simply Supported" |

#### Example Generic CSV

```csv
beam_id,story,mu_knm,vu_kn,span_mm,b_mm,D_mm,fck_nmm2
B1,GF,180.5,125.0,5000,300,500,25
B2,GF,145.2,98.3,4500,300,450,25
B3,FF,210.8,140.5,6000,350,600,30
B4,FF,165.0,110.2,5500,300,550,25
```

---

## Envelope Processing

For ETABS/SAFE formats with multiple stations per beam, the library computes envelopes:

```python
# Per beam, compute:
mu_max = max(abs(m3) for all stations)
vu_max = max(abs(v2) for all stations)
```

This ensures conservative design using the maximum forces along the beam length.

---

## Validation Rules

### File Validation

1. **Encoding:** UTF-8 (with fallback to Latin-1)
2. **Size Limit:** 50 MB recommended, 100 MB max
3. **Row Limit:** 1,000,000 rows max
4. **Header Required:** First row must be column headers

### Data Validation

| Rule | Severity | Message |
|------|----------|---------|
| Required columns missing | Error | "Required column 'M3' not found" |
| Empty beam_id | Error | "Row 5: Empty beam identifier" |
| Non-numeric force value | Error | "Row 10: Invalid moment value '---'" |
| Negative dimensions | Warning | "Row 15: Negative width (-300 mm)" |
| Unusual M/V ratio | Warning | "B1: M/V ratio > 15m, verify loads" |
| Duplicate beam_id | Warning | "B1 appears 3 times (will use envelope)" |

### Value Ranges (Warnings)

| Field | Typical Range | Flag If |
|-------|---------------|---------|
| mu_knm | 10 - 1000 | < 1 or > 2000 |
| vu_kn | 5 - 500 | < 1 or > 1000 |
| span_mm | 1000 - 12000 | < 500 or > 20000 |
| b_mm | 150 - 600 | < 100 or > 1000 |
| D_mm | 200 - 900 | < 150 or > 1500 |

---

## API Usage

### Python API

```python
from structural_lib import (
    validate_etabs_csv,
    load_etabs_csv,
    create_jobs_from_etabs_csv,
)

# Validate first
is_valid, issues, col_map = validate_etabs_csv("forces.csv")
if not is_valid:
    for issue in issues:
        print(f"Error: {issue}")
    return

# Load and process
rows = load_etabs_csv("forces.csv")
jobs = create_jobs_from_etabs_csv(
    csv_path="forces.csv",
    b_mm=300,
    D_mm=500,
    fck_nmm2=25,
    fy_nmm2=500,
)
```

### Streamlit Import (Phase 2)

```python
# File uploader with validation
uploaded = st.file_uploader("Upload beam forces CSV", type=["csv"])
if uploaded:
    is_valid, issues, _ = validate_etabs_csv(uploaded)
    if is_valid:
        beams = load_etabs_csv(uploaded)
        st.success(f"Loaded {len(beams)} beams")
    else:
        st.error("Validation failed")
        for issue in issues:
            st.warning(issue)
```

---

## Performance Targets

| Metric | Target | Measured |
|--------|--------|----------|
| Load 1000 beams | < 1 second | TBD |
| Validate 50MB file | < 5 seconds | TBD |
| Memory per 1000 beams | < 50 MB | TBD |

---

## References

- [ETABS Import Module](../../Python/structural_lib/etabs_import.py)
- [8-Week Development Plan](../planning/8-week-development-plan.md)
- [API Documentation](../reference/api.md)
- ETABS User Manual: Table Export Format
- SAFE User Manual: Strip/Band Force Export

---

## Changelog

| Date | Version | Change |
|------|---------|--------|
| 2026-01-21 | 1.1 | Added frames_geometry.csv schema for 3D visualization |
| 2026-01-20 | 1.0 | Initial schema definition |
