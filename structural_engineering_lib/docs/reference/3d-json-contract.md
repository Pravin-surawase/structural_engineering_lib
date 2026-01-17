---
**Type:** Reference
**Audience:** Developers, AI Agents
**Status:** Production Ready
**Importance:** Critical
**Created:** 2026-01-14
**Last Updated:** 2026-01-14
**Related Tasks:** TASK-3D-02, TASK-3D-03
---

# 3D JSON Contract — Beam Geometry Data Format

> **Version:** 1.0.0
> **Purpose:** Defines the JSON schema for exchanging 3D beam geometry between Python (structural_lib) and JavaScript/TypeScript (Three.js viewer).

## Overview

This document specifies the data contract for 3D visualization of reinforced concrete beams. The contract enables:

1. **Python → JavaScript**: Serialize beam geometry from `structural_lib.visualization.geometry_3d`
2. **JavaScript → Three.js**: Parse JSON and render with react-three-fiber
3. **Bidirectional**: postMessage API for Streamlit Cloud iframe communication

```
┌─────────────────┐     JSON via      ┌─────────────────┐
│ Python Backend  │ ─────────────────► │ Three.js Viewer │
│ (structural_lib)│   postMessage      │ (react-three-   │
│ Beam3DGeometry  │ ◄───────────────── │  fiber)         │
└─────────────────┘   user events      └─────────────────┘
```

## TypeScript Type Definitions

```typescript
/**
 * BeamGeometry3D — Complete 3D geometry for beam visualization
 *
 * This is the primary data structure received from Python backend.
 * All coordinates in millimeters (mm).
 */
interface BeamGeometry3D {
  /** Unique beam identifier (e.g., "B1", "FB2") */
  beamId: string;

  /** Story/floor identifier (e.g., "GF", "1F", "ROOF") */
  story: string;

  /** Beam dimensions in mm */
  dimensions: {
    b: number;      // Width
    D: number;      // Total depth
    span: number;   // Clear span
  };

  /** 8 corner points of concrete bounding box */
  concreteOutline: Point3D[];

  /** All reinforcement bar paths */
  rebars: RebarPath[];

  /** All stirrup loops along span */
  stirrups: StirrupLoop[];

  /** Additional metadata for display/tooltips */
  metadata: BeamMetadata;

  /** Schema version for compatibility checking */
  version: "1.0.0";
}

/**
 * Point3D — Immutable 3D coordinate
 *
 * Coordinate System (Right-hand rule):
 * - X: Along beam span (0 = left support)
 * - Y: Beam width (0 = center, +Y = front face)
 * - Z: Beam height (0 = soffit, +Z = up)
 */
interface Point3D {
  x: number;  // mm, along span
  y: number;  // mm, across width
  z: number;  // mm, vertical height
}

/**
 * RebarPath — Complete path of a reinforcement bar
 */
interface RebarPath {
  /** Unique bar identifier (e.g., "B1", "T2") */
  barId: string;

  /** Segments making up the bar (straight, hooks, bends) */
  segments: RebarSegment[];

  /** Bar diameter in mm */
  diameter: number;

  /** Bar position type */
  barType: "bottom" | "top" | "side" | "bent_up";

  /** Zone where bar is located */
  zone: "start" | "mid" | "end" | "full";

  /** Total cutting length in mm */
  totalLength: number;
}

/**
 * RebarSegment — Single straight segment of a bar
 */
interface RebarSegment {
  start: Point3D;
  end: Point3D;
  diameter: number;
  type: "straight" | "bend" | "hook_90" | "hook_135" | "hook_180";
  length: number;  // mm
}

/**
 * StirrupLoop — Closed stirrup at a specific X position
 */
interface StirrupLoop {
  /** X-coordinate along span (mm) */
  positionX: number;

  /** Corner points forming closed loop (Y-Z plane) */
  path: Point3D[];

  /** Stirrup bar diameter (mm) */
  diameter: number;

  /** Number of legs (2, 4, 6) */
  legs: number;

  /** Hook type at ends */
  hookType: "90" | "135";

  /** Perimeter length (mm) */
  perimeter: number;
}

/**
 * BeamMetadata — Additional information for display
 */
interface BeamMetadata {
  fck?: number;            // Concrete grade (N/mm²)
  fy?: number;             // Steel grade (N/mm²)
  cover?: number;          // Clear cover (mm)
  ldTension?: number;      // Development length tension (mm)
  ldCompression?: number;  // Development length compression (mm)
  lapLength?: number;      // Lap splice length (mm)
  isSeismic?: boolean;     // Seismic detailing applied
  isValid?: boolean;       // Detailing validity
  remarks?: string;        // Validation notes
}
```

## Sample JSON Payload

### Minimal Beam (300×450, 4m span)

```json
{
  "beamId": "B1",
  "story": "GF",
  "dimensions": {
    "b": 300,
    "D": 450,
    "span": 4000
  },
  "concreteOutline": [
    {"x": 0, "y": -150, "z": 0},
    {"x": 0, "y": 150, "z": 0},
    {"x": 4000, "y": 150, "z": 0},
    {"x": 4000, "y": -150, "z": 0},
    {"x": 0, "y": -150, "z": 450},
    {"x": 0, "y": 150, "z": 450},
    {"x": 4000, "y": 150, "z": 450},
    {"x": 4000, "y": -150, "z": 450}
  ],
  "rebars": [
    {
      "barId": "B1",
      "segments": [
        {
          "start": {"x": 0, "y": -96, "z": 56},
          "end": {"x": 4000, "y": -96, "z": 56},
          "diameter": 16,
          "type": "straight",
          "length": 4000
        }
      ],
      "diameter": 16,
      "barType": "bottom",
      "zone": "full",
      "totalLength": 4000
    },
    {
      "barId": "B2",
      "segments": [
        {
          "start": {"x": 0, "y": 0, "z": 56},
          "end": {"x": 4000, "y": 0, "z": 56},
          "diameter": 16,
          "type": "straight",
          "length": 4000
        }
      ],
      "diameter": 16,
      "barType": "bottom",
      "zone": "full",
      "totalLength": 4000
    },
    {
      "barId": "B3",
      "segments": [
        {
          "start": {"x": 0, "y": 96, "z": 56},
          "end": {"x": 4000, "y": 96, "z": 56},
          "diameter": 16,
          "type": "straight",
          "length": 4000
        }
      ],
      "diameter": 16,
      "barType": "bottom",
      "zone": "full",
      "totalLength": 4000
    },
    {
      "barId": "T1",
      "segments": [
        {
          "start": {"x": 0, "y": -96, "z": 394},
          "end": {"x": 4000, "y": -96, "z": 394},
          "diameter": 12,
          "type": "straight",
          "length": 4000
        }
      ],
      "diameter": 12,
      "barType": "top",
      "zone": "full",
      "totalLength": 4000
    },
    {
      "barId": "T2",
      "segments": [
        {
          "start": {"x": 0, "y": 96, "z": 394},
          "end": {"x": 4000, "y": 96, "z": 394},
          "diameter": 12,
          "type": "straight",
          "length": 4000
        }
      ],
      "diameter": 12,
      "barType": "top",
      "zone": "full",
      "totalLength": 4000
    }
  ],
  "stirrups": [
    {
      "positionX": 50,
      "path": [
        {"x": 50, "y": -106, "z": 44},
        {"x": 50, "y": 106, "z": 44},
        {"x": 50, "y": 106, "z": 406},
        {"x": 50, "y": -106, "z": 406}
      ],
      "diameter": 8,
      "legs": 2,
      "hookType": "135",
      "perimeter": 936
    },
    {
      "positionX": 150,
      "path": [
        {"x": 150, "y": -106, "z": 44},
        {"x": 150, "y": 106, "z": 44},
        {"x": 150, "y": 106, "z": 406},
        {"x": 150, "y": -106, "z": 406}
      ],
      "diameter": 8,
      "legs": 2,
      "hookType": "135",
      "perimeter": 936
    }
  ],
  "metadata": {
    "fck": 25,
    "fy": 500,
    "cover": 40,
    "ldTension": 752,
    "ldCompression": 752,
    "lapLength": 940,
    "isSeismic": true,
    "remarks": "Detailing complete"
  },
  "version": "1.0.0"
}
```

## Coordinate System Details

```
                    +Z (up)
                     │
                     │     +Y (front)
                     │    /
                     │   /
                     │  /
        ┌────────────┼─/──────────────┐ beam end (x=span)
       /│            │/              /│
      / │            │              / │
     /  │            │             /  │
    ┌───│────────────┼────────────┐   │
    │   │            │            │   │
    │   │            O────────────│───┼───► +X (along span)
    │   │           origin        │   │
    │   │                         │   │
    │   └─────────────────────────│───┘
    │  /                          │  /
    │ /                           │ /
    │/                            │/
    └─────────────────────────────┘
    beam start (x=0)
```

**Key Points:**
- Origin (0, 0, 0) is at left support, center-width, at soffit
- X increases along beam span (left to right)
- Y is transverse (−Y = back, +Y = front)
- Z is vertical (+Z = up from soffit)
- All values in millimeters

## Usage Examples

### Python: Generate JSON from BeamDetailingResult

```python
from structural_lib.codes.is456.detailing import create_beam_detailing
from structural_lib.visualization.geometry_3d import beam_to_3d_geometry
import json

# Create detailing result
detailing = create_beam_detailing(
    beam_id="B1",
    story="GF",
    b=300, D=450, span=4000,
    cover=40, fck=25, fy=500,
    ast_start=904, ast_mid=904, ast_end=904,
)

# Convert to 3D geometry
geometry = beam_to_3d_geometry(detailing, is_seismic=True)

# Serialize to JSON
json_str = json.dumps(geometry.to_dict(), indent=2)

# Shortcut: direct JSON payload
json_payload = detailing.to_3d_json(is_seismic=True)

# Send via postMessage to iframe
send_to_viewer(json_str)
```

### TypeScript: Parse and Render

```typescript
import { useEffect, useState } from 'react';
import { BeamViewer } from './BeamViewer';
import type { BeamGeometry3D } from './types';

function App() {
  const [geometry, setGeometry] = useState<BeamGeometry3D | null>(null);

  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data.type === 'BEAM_GEOMETRY') {
        const data = event.data.payload as BeamGeometry3D;

        // Validate version
        if (data.version !== '1.0.0') {
          console.warn('Schema version mismatch');
        }

        setGeometry(data);
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  return geometry ? <BeamViewer geometry={geometry} /> : <Loading />;
}
```

## Validation Rules

| Field | Rule | Error if Violated |
|-------|------|-------------------|
| `version` | Must be "1.0.0" | Log warning, attempt parse |
| `beamId` | Non-empty string | Reject payload |
| `dimensions.b` | > 0 | Reject payload |
| `dimensions.D` | > 0 | Reject payload |
| `dimensions.span` | > 0 | Reject payload |
| `concreteOutline` | Exactly 8 points | Use default box |
| `rebars[].diameter` | > 0 | Skip bar |
| `stirrups[].path` | >= 3 points | Skip stirrup |

## Versioning Strategy

**Semantic Versioning:**
- MAJOR: Breaking changes to schema structure
- MINOR: New optional fields added
- PATCH: Documentation/example fixes

**Backward Compatibility:**
- Viewers MUST handle missing optional fields with defaults
- Viewers SHOULD warn on version mismatch but attempt parse
- Python MUST include version field in every payload

## Related Files

| File | Purpose |
|------|---------|
| [geometry_3d.py](../../Python/structural_lib/visualization/geometry_3d.py) | Python dataclasses and serialization |
| [types.ts](../../three_viewer/src/types.ts) | TypeScript type definitions (future) |
| [BeamViewer.tsx](../../three_viewer/src/components/BeamViewer.tsx) | React component (future) |

## Changelog

### v1.0.0 (2026-01-14)
- Initial schema definition
- Core types: Point3D, RebarSegment, RebarPath, StirrupLoop, BeamGeometry3D
- Sample payloads for minimal beam
- Coordinate system documentation
