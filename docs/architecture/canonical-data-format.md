# Canonical Data Format Architecture

**Type:** Architecture
**Audience:** All Agents, Developers
**Status:** Draft
**Importance:** High
**Created:** 2026-01-19
**Last Updated:** 2026-01-19
**Related Tasks:** TASK-DATA-001

---

## Executive Summary

This document defines the canonical data format architecture for the structural_engineering_lib project. The goal is to create a stable, efficient, AI-agent-friendly internal data representation that can adapt to varying input CSV formats from ETABS, SAFE, and other structural analysis software.

## Problem Statement

### Current Challenges

1. **Varying Input Formats**: ETABS exports can vary between versions (2019-2024) with different column names
2. **Fragile Parsing**: Current dataclass-based approach requires manual updates for new formats
3. **No Schema Validation**: Silent failures when input data is malformed
4. **Limited Serialization**: No standard way to save/load intermediate results
5. **AI-Agent Friction**: Agents must understand multiple CSV formats to work effectively

### Goals

1. **Stability**: Internal format remains constant regardless of input source
2. **Validation**: Clear error messages for invalid data
3. **Serialization**: Easy JSON/binary export for caching and debugging
4. **Extensibility**: Easy to add new input formats without changing core logic
5. **AI-Friendly**: Single, well-documented format for agents to target

## Solution: Pydantic-Based Canonical Models

### Why Pydantic Over Dataclasses?

| Feature | Python dataclasses | Pydantic |
|---------|-------------------|----------|
| Type validation | ❌ None | ✅ Automatic |
| JSON serialization | ❌ Manual | ✅ Built-in |
| JSON Schema generation | ❌ None | ✅ Automatic |
| Error messages | ❌ Generic | ✅ Detailed, localized |
| Default values | ✅ Yes | ✅ Yes + coercion |
| Immutability option | ✅ frozen=True | ✅ frozen=True |
| Nested validation | ❌ None | ✅ Recursive |
| Alias support | ❌ None | ✅ Field aliases |
| Extra fields handling | ❌ None | ✅ ignore/allow/forbid |

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ ETABS CSV    │  │ SAFE CSV     │  │ Manual Input │  ...         │
│  │ (2019-2024)  │  │ (Foundation) │  │ (Streamlit)  │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                 │                       │
│         ▼                 ▼                 ▼                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    ADAPTER LAYER                              │  │
│  │  ETABSAdapter    SAFEAdapter    ManualInputAdapter   ...      │  │
│  │  (normalize column names, units, coordinate systems)          │  │
│  └──────────────────────────────┬───────────────────────────────┘  │
│                                 │                                   │
└─────────────────────────────────┼───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   CANONICAL LAYER (Pydantic)                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │ BeamGeometry    │  │ BeamForces      │  │ BeamDesignResult    │ │
│  │ - id: str       │  │ - id: str       │  │ - id: str           │ │
│  │ - label: str    │  │ - load_case: str│  │ - mu_knm: float     │ │
│  │ - story: str    │  │ - mu_knm: float │  │ - vu_kn: float      │ │
│  │ - point1: Point3D│ │ - vu_kn: float  │  │ - ast_mm2: float    │ │
│  │ - point2: Point3D│ │ - pu_kn: float  │  │ - asv_mm2_m: float  │ │
│  │ - section: Sect │  └─────────────────┘  │ - status: str       │ │
│  └─────────────────┘                       └─────────────────────┘ │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ BeamBatchInput - Complete validated input for batch design      ││
│  │ - beams: list[BeamGeometry]                                     ││
│  │ - forces: list[BeamForces]                                      ││
│  │ - defaults: DesignDefaults                                      ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      OUTPUT LAYER                                   │
├─────────────────────────────────────────────────────────────────────┤
│  JSON export │ Excel report │ 3D Visualization │ DXF drawings      │
└─────────────────────────────────────────────────────────────────────┘
```

## Canonical Model Definitions

### Core Models

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum

class FrameType(str, Enum):
    BEAM = "beam"
    COLUMN = "column"
    BRACE = "brace"

class Point3D(BaseModel):
    """3D coordinate point with explicit units (meters)."""
    model_config = ConfigDict(frozen=True)

    x: float = Field(..., description="X coordinate in meters")
    y: float = Field(..., description="Y coordinate in meters")
    z: float = Field(..., description="Z coordinate in meters")

class SectionProperties(BaseModel):
    """Beam cross-section properties with explicit units."""
    model_config = ConfigDict(frozen=True)

    width_mm: float = Field(..., gt=0, description="Width in mm")
    depth_mm: float = Field(..., gt=0, description="Depth in mm")
    fck_mpa: float = Field(25.0, gt=0, description="Concrete strength in MPa")
    fy_mpa: float = Field(500.0, gt=0, description="Steel yield strength in MPa")
    cover_mm: float = Field(40.0, gt=0, description="Clear cover in mm")

class BeamGeometry(BaseModel):
    """Canonical beam geometry model."""
    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Unique identifier")
    label: str = Field(..., description="User-friendly label (e.g., B1)")
    story: str = Field(..., description="Story/level name")
    frame_type: FrameType = Field(default=FrameType.BEAM)
    point1: Point3D = Field(..., description="Start point")
    point2: Point3D = Field(..., description="End point")
    section: SectionProperties = Field(..., description="Section properties")

    @property
    def length_m(self) -> float:
        """Calculate beam length in meters."""
        dx = self.point2.x - self.point1.x
        dy = self.point2.y - self.point1.y
        dz = self.point2.z - self.point1.z
        return (dx**2 + dy**2 + dz**2) ** 0.5

class BeamForces(BaseModel):
    """Canonical beam forces model (envelope values)."""
    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Beam ID matching BeamGeometry")
    load_case: str = Field(..., description="Load combination name")
    mu_knm: float = Field(..., description="Design moment in kN·m")
    vu_kn: float = Field(..., description="Design shear in kN")
    pu_kn: float = Field(0.0, description="Axial force in kN (usually 0 for beams)")
    station_count: int = Field(1, ge=1, description="Number of stations processed")

class BeamDesignResult(BaseModel):
    """Canonical beam design result model."""
    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Beam ID")
    mu_knm: float = Field(..., description="Applied moment in kN·m")
    vu_kn: float = Field(..., description="Applied shear in kN")
    ast_mm2: float = Field(..., ge=0, description="Required tension steel area in mm²")
    asv_mm2_m: float = Field(..., ge=0, description="Required stirrup area per meter in mm²/m")
    status: str = Field(..., description="Design status: PASS, FAIL, or WARNING")
    utilization: float = Field(..., ge=0, le=2.0, description="Utilization ratio")
    messages: list[str] = Field(default_factory=list, description="Design messages/warnings")
```

### Batch Input Model

```python
class DesignDefaults(BaseModel):
    """Default design parameters for batch processing."""

    fck_mpa: float = Field(25.0, gt=0)
    fy_mpa: float = Field(500.0, gt=0)
    cover_mm: float = Field(40.0, gt=0)
    min_bar_dia_mm: int = Field(12, ge=8)
    max_bar_dia_mm: int = Field(32, le=40)
    stirrup_dia_mm: int = Field(8, ge=6)

class BeamBatchInput(BaseModel):
    """Complete validated input for batch beam design."""

    beams: list[BeamGeometry] = Field(..., min_length=1)
    forces: list[BeamForces] = Field(..., min_length=1)
    defaults: DesignDefaults = Field(default_factory=DesignDefaults)
    metadata: dict = Field(default_factory=dict)

    def get_merged_data(self) -> list[tuple[BeamGeometry, BeamForces]]:
        """Merge geometry and forces by beam ID."""
        forces_by_id = {f.id: f for f in self.forces}
        return [(b, forces_by_id[b.id]) for b in self.beams if b.id in forces_by_id]
```

## Adapter Pattern for Input Sources

### Base Adapter Interface

```python
from abc import ABC, abstractmethod
from pathlib import Path

class InputAdapter(ABC):
    """Base class for input format adapters."""

    @abstractmethod
    def can_handle(self, source: Path | str) -> bool:
        """Check if this adapter can handle the given source."""
        pass

    @abstractmethod
    def load_geometry(self, source: Path | str) -> list[BeamGeometry]:
        """Load beam geometry from source."""
        pass

    @abstractmethod
    def load_forces(self, source: Path | str) -> list[BeamForces]:
        """Load beam forces from source."""
        pass
```

### ETABS Adapter

```python
class ETABSAdapter(InputAdapter):
    """Adapter for ETABS CSV exports."""

    # Column name mappings for different ETABS versions
    GEOMETRY_COLUMNS = {
        "unique_name": ["UniqueName", "Unique Name", "GUID"],
        "label": ["Label", "Frame", "Element", "Name"],
        "story": ["Story", "Level", "Floor"],
        # ... more mappings
    }

    def can_handle(self, source: Path | str) -> bool:
        """Detect ETABS format by checking headers."""
        # Check for ETABS-specific columns
        pass

    def load_geometry(self, source: Path | str) -> list[BeamGeometry]:
        """Convert ETABS geometry CSV to canonical format."""
        # 1. Read CSV
        # 2. Map column names using GEOMETRY_COLUMNS
        # 3. Convert units (m to m, no conversion needed)
        # 4. Create BeamGeometry instances with validation
        pass
```

## Benefits

### 1. Validation at Boundaries

```python
# Invalid data fails early with clear error
try:
    beam = BeamGeometry(
        id="B1",
        label="B1",
        story="Ground",
        point1=Point3D(x=0, y=0, z=0),
        point2=Point3D(x=5, y=0, z=0),
        section=SectionProperties(width_mm=-100, depth_mm=500)  # Invalid!
    )
except ValidationError as e:
    print(e)
    # 1 validation error for BeamGeometry
    # section.width_mm
    #   Input should be greater than 0 [type=greater_than, input_value=-100, ...]
```

### 2. JSON Schema for Documentation

```python
# Auto-generate JSON Schema for documentation
schema = BeamGeometry.model_json_schema()
# Can be used to generate API docs, validate JSON input, etc.
```

### 3. Efficient Serialization

```python
# Fast JSON serialization
batch_input = BeamBatchInput(beams=[...], forces=[...])
json_str = batch_input.model_dump_json()

# Load from JSON (with validation)
loaded = BeamBatchInput.model_validate_json(json_str)
```

### 4. AI-Agent Friendly

Agents only need to understand one format:
- Clear field names with descriptions
- Explicit units in field names
- Validation prevents common errors
- JSON Schema provides self-documentation

## Migration Path

### Phase 1: Create New Models (Session 40)
- Create `models.py` with Pydantic models
- Add unit tests for all models
- No changes to existing code

### Phase 2: Add Adapters (Session 41)
- Create ETABS adapter
- Test with existing CSV files
- Run in parallel with existing code

### Phase 3: Gradual Migration (Sessions 42-44)
- Update `etabs_import.py` to use new models
- Update Streamlit pages to use canonical format
- Deprecate old dataclasses

### Phase 4: Cleanup (Session 45)
- Remove deprecated code
- Update all tests
- Update documentation

## Related Files

- [etabs_import.py](../../Python/structural_lib/etabs_import.py) - Current implementation
- [csv-import-schema.md](../specs/csv-import-schema.md) - CSV format specs
- [8-week-development-plan.md](../planning/8-week-development-plan.md) - Project timeline

## Decision Record

**Decision**: Use Pydantic over standard dataclasses

**Rationale**:
1. Automatic validation prevents runtime errors
2. JSON serialization is built-in and fast
3. JSON Schema generation enables self-documenting APIs
4. Widely used in industry (FastAPI, etc.)
5. Excellent type checker support

**Trade-offs**:
- Additional dependency (pydantic already in project)
- Slightly more verbose model definitions
- Learning curve for team

**Alternatives Considered**:
- attrs: Good but less validation features
- msgspec: Faster but less validation
- Protocol Buffers: Better for cross-language, overkill for this project
- Apache Arrow: Better for big data, not needed here
