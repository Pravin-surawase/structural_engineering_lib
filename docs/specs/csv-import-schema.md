---
owner: Main Agent
status: active
last_updated: 2026-08-17
doc_type: spec
complexity: intermediate
tags: []
---

# CSV Import Schema Specification

**Type:** Specification
**Audience:** Developers, Users
**Status:** Active
**Importance:** High
**Created:** 2026-01-20
**Last Updated:** 2026-08-17
**Related Tasks:** TASK-CSV-01, TASK-CSV-02, TASK-3D-002

---

## Overview

This document defines the strict CSV schemas for importing beam data and geometry
from structural analysis software into `structural_engineering_lib`. ETABS CSV
support is read-only and beam-scoped; it does not establish global-model,
load-basis, analysis-validity, or professional-review approval.

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
| `Station` | Distance, Location, Loc | Source location along the beam | Declared source length unit |
| `M3` | Moment, M, Mu, MomentY, Myy | Signed bending moment about local 3 axis | kN·m |
| `V2` | Shear, V, Vu, ShearY, Vyy | Signed shear force in local 2 plane | kN |

#### Optional Columns

| Column | Aliases | Description | Units | Default |
|--------|---------|-------------|-------|---------|
| `Unique Name` | UniqueName, Unique, GUID | Internal ID | Text | "" |
| `P` | Axial, N, Pu, AxialForce | Signed axial force when supplied | kN | Not supplied / `0` in beam-only output |

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

ETABS exports frame geometry via the VBA export tool (`frames_geometry.csv`).
This file supports read-only member geometry and visualization. It is not a
gravity-analysis model.

#### Required Columns

| Column | Description | Units | Example |
|--------|-------------|-------|---------|
| `Label` | User-friendly label | Text | "B1", "C2" |
| `Story` | Floor/level name | Text | "Story1", "Ground" |
| `SectionName` | Section identifier | Text | "B230X450M20" |
| `Point1X` | X coordinate of start | m | 0.0 |
| `Point1Y` | Y coordinate of start | m | 0.0 |
| `Point1Z` | Z coordinate of start | m | 3.0 |
| `Point2X` | X coordinate of end | m | 4.5 |
| `Point2Y` | Y coordinate of end | m | 0.0 |
| `Point2Z` | Z coordinate of end | m | 3.0 |

#### Optional Columns

| Column | Description | Units | Default |
|--------|-------------|-------|---------|
| `UniqueName` | Internal ETABS ID | Text | Empty |
| `FrameType` | Element type; non-beams are deliberately excluded | Text | Beam |
| `Point1Name` | Node at start | Text | Empty |
| `Point2Name` | Node at end | Text | Empty |
| `Angle` | Rotation angle | degrees | 0.0 |
| `CardinalPoint` | Insertion point | 1-11 | 10 |

`SectionName` must contain explicit RC dimensions such as `B300X500`, or the
caller must provide an explicit section map. Unknown names never become a
default `300 x 500` section.

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

#### Required calculation columns for strict import

| Column | Description | Units |
|--------|-------------|-------|
| `b_mm` / `b (mm)` | Beam width | mm |
| `D_mm` / `D (mm)` | Total depth | mm |
| `fck_nmm2` / `fck` | Concrete strength | N/mm² |
| `fy_nmm2` / `fy` | Steel yield strength | N/mm² |
| `cover_mm` / `Cover (mm)` | Explicit clear cover basis | mm |

`story`, `span_mm`, effective-depth metadata, exposure, support, and notes may be
retained when present, but no missing calculation value is silently invented.

#### Example Generic CSV

```csv
beam_id,story,mu_knm,vu_kn,span_mm,b_mm,D_mm,fck_nmm2,fy_nmm2,cover_mm
B1,GF,180.5,125.0,5000,300,500,25,500,40
B2,GF,145.2,98.3,4500,300,450,25,500,40
B3,FF,210.8,140.5,6000,350,600,30,500,45
B4,FF,165.0,110.2,5500,300,550,25,500,40
```

---

## Envelope Processing

For raw ETABS station data, the library selects moment and shear extrema
independently and preserves their provenance:

```python
# Per beam, compute:
mu_max = max(abs(m3) for all stations)
vu_max = max(abs(v2) for all stations)
```

Each result also retains the signed governing value, its station, and the
concurrent companion action at that station. The basis is recorded as
`independent_absolute_extrema_with_concurrent_values`. A source-precomputed VBA
envelope is labelled `source_precomputed_extrema_provenance_unavailable`; it is
not represented as though station provenance existed. Raw row values remain in
the lossless import ledger.

---

## Validation Rules

### File Validation

1. **Encoding:** UTF-8 or UTF-8 with BOM; decoding failure blocks.
2. **Header required:** the first row must contain recognized headers.
3. **Data required:** header-only inputs block.
4. **Conservation:** every physical row is accepted or blocked and appears in the ledger.

### Data Validation

| Rule | Severity | Message |
|------|----------|---------|
| Required columns missing | Error | "Required column 'M3' not found" |
| Empty beam_id | Error | "Row 5: Empty beam identifier" |
| Non-numeric force value | Error | "Row 10: Invalid moment value '---'" |
| Non-finite number (`NaN`, `inf`) | Error | Row is blocked; no calculation batch is exposed |
| Unknown section dimensions | Error | Explicit section map or parseable source name required |
| Duplicate source record identity | Error | Every duplicate row is ledgered and blocked |
| Unmatched geometry/force member | Error | Batch is blocked |

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
from structural_lib.core.models import DesignDefaults
from structural_lib.services.imports import (
    parse_dual_csv_lossless,
)

result = parse_dual_csv_lossless(
    "frames_geometry.csv",
    "beam_forces.csv",
    format_hint="etabs",
    defaults=DesignDefaults(fck_mpa=25, fy_mpa=500, cover_mm=40),
)

if result.batch is None:
    for issue in result.issues:
        print(issue.code, issue.path, issue.message)
    raise SystemExit("ETABS import blocked")

assert result.ledger.totals.source_rows == (
    result.ledger.totals.accepted_rows + result.ledger.totals.blocked_rows
)
```

UI transports must present the same ledger/result. They may not calculate from a
blocked result, replace malformed cells with zero, or report a partial row count
as a successful import.

---

## Performance Targets

| Metric | Target | Measured |
|--------|--------|----------|
| Load 1000 beams | < 1 second | TBD |
| Validate 50MB file | < 5 seconds | TBD |
| Memory per 1000 beams | < 50 MB | TBD |

---

## References

- [ETABS Import Module](../../Python/structural_lib/services/etabs_import.py)
- [8-Week Development Plan](../_archive/planning-completed-2026-03/8-week-development-plan.md)
- [API Documentation](../reference/api.md)
- ETABS User Manual: Table Export Format
- SAFE User Manual: Strip/Band Force Export

---

## Changelog

| Date | Version | Change |
|------|---------|--------|
| 2026-08-17 | 1.2 | Froze lossless ETABS/section/envelope and strict generic-input contracts |
| 2026-01-21 | 1.1 | Added frames_geometry.csv schema for 3D visualization |
| 2026-01-20 | 1.0 | Initial schema definition |
