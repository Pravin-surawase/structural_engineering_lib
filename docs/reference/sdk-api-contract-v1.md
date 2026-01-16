# Structural SDK API Contract — v1.0

**Type:** Reference
**Audience:** All Agents, Developers, Testers
**Status:** Draft
**Importance:** Critical
**Created:** 2026-01-16
**Last Updated:** 2026-01-16
**Related Tasks:** AUTOMATION-PHASE0, LIB-IMPROVEMENT

---

## Overview

This document defines the public API contract for the Structural SDK. All functions documented here are considered stable and will follow semantic versioning.

**Namespace:** `structural_sdk` (aliased as `sk`)

```python
import structural_sdk as sk

# Access via namespaces
sk.engine.design_beam(...)
sk.viz.beam_3d(...)
sk.io.export_dxf(...)
sk.codes.is456.flexure.design(...)
```

---

## Namespace Structure

```
sk
├── engine          # Design, verification, optimization
│   ├── design_beam()
│   ├── verify_beam()
│   ├── batch_design()
│   ├── optimize_beam()
│   ├── analyze_beam()
│   └── compare_designs()
├── viz             # Visualization (2D + 3D)
│   ├── beam_3d()
│   ├── to_threejs_json()
│   ├── plot_bmd_sfd()
│   ├── plot_section()
│   ├── plot_rebar_layout()
│   ├── compliance_panel()
│   └── comparison_chart()
├── io              # Import/Export
│   ├── read_csv()
│   ├── read_excel()
│   ├── read_etabs()
│   ├── export_csv()
│   ├── export_json()
│   ├── export_dxf()
│   ├── export_bbs()
│   └── export_report()
├── codes           # Code-specific modules
│   ├── is456/
│   ├── aci318/
│   └── ec2/
├── types           # Data types
│   ├── BeamInput
│   ├── BeamGeometryInput
│   ├── MaterialsInput
│   ├── LoadsInput
│   ├── DesignResult
│   └── ...
└── utils           # Utilities
    ├── validate()
    ├── get_version()
    └── list_codes()
```

---

## Core Data Types

### Input Types

```python
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class BeamGeometryInput:
    """Beam geometry specification."""
    b_mm: float           # Width (mm)
    D_mm: float           # Overall depth (mm)
    span_mm: float        # Clear span (mm)
    d_mm: float | None = None      # Effective depth (auto-calc if None)
    cover_mm: float = 40.0         # Clear cover (mm)

    @property
    def effective_depth(self) -> float:
        """Effective depth, calculated if not provided."""
        return self.d_mm if self.d_mm else self.D_mm - self.cover_mm - 10

    def validate(self) -> list[str]:
        """Return list of validation errors, empty if valid."""


@dataclass(frozen=True)
class MaterialsInput:
    """Material specification."""
    fck_nmm2: float       # Concrete characteristic strength (N/mm²)
    fy_nmm2: float        # Steel yield strength (N/mm²)
    Es_nmm2: float = 200000.0      # Steel modulus (N/mm²)
    gamma_c: float = 1.5           # Concrete partial safety factor
    gamma_s: float = 1.15          # Steel partial safety factor

    @classmethod
    def M20_FE415(cls) -> "MaterialsInput":
        return cls(fck_nmm2=20, fy_nmm2=415)

    @classmethod
    def M25_FE500(cls) -> "MaterialsInput":
        return cls(fck_nmm2=25, fy_nmm2=500)

    @classmethod
    def M30_FE500(cls) -> "MaterialsInput":
        return cls(fck_nmm2=30, fy_nmm2=500)

    @classmethod
    def M35_FE500(cls) -> "MaterialsInput":
        return cls(fck_nmm2=35, fy_nmm2=500)

    @classmethod
    def M40_FE500(cls) -> "MaterialsInput":
        return cls(fck_nmm2=40, fy_nmm2=500)


@dataclass(frozen=True)
class LoadsInput:
    """Load specification for a single case."""
    mu_knm: float         # Factored bending moment (kN·m)
    vu_kn: float          # Factored shear force (kN)
    tu_knm: float = 0.0   # Factored torsion (kN·m), optional


@dataclass(frozen=True)
class LoadCaseInput:
    """Named load case."""
    case_id: str          # Unique identifier (e.g., "DL+LL")
    mu_knm: float
    vu_kn: float
    tu_knm: float = 0.0


@dataclass
class BeamInput:
    """Complete beam input specification."""
    beam_id: str                    # Unique beam identifier
    geometry: BeamGeometryInput
    materials: MaterialsInput
    loads: LoadsInput | None = None           # Single load case
    load_cases: list[LoadCaseInput] | None = None  # Multiple cases
    story: str = ""                 # Building story (optional)
    code: str = "IS456"             # Design code

    def validate(self) -> list[str]:
        """Return list of validation errors, empty if valid."""

    def to_dict(self) -> dict:
        """Serialize to dictionary."""

    @classmethod
    def from_dict(cls, data: dict) -> "BeamInput":
        """Deserialize from dictionary."""
```

### Output Types

```python
@dataclass
class FlexureResult:
    """Flexure design results."""
    is_ok: bool
    mu_capacity_knm: float         # Moment capacity
    mu_demand_knm: float           # Applied moment
    utilization: float             # Demand/capacity ratio
    ast_required_mm2: float        # Required tension steel
    ast_provided_mm2: float        # Provided tension steel
    asc_required_mm2: float = 0.0  # Compression steel (if doubly)
    asc_provided_mm2: float = 0.0
    section_type: str = "SINGLY"   # SINGLY, DOUBLY, OVER_REINFORCED
    xu_mm: float = 0.0             # Neutral axis depth
    xu_max_mm: float = 0.0         # Max neutral axis depth
    clause_refs: list[str] = None  # IS 456 clause references


@dataclass
class ShearResult:
    """Shear design results."""
    is_ok: bool
    vu_demand_kn: float            # Applied shear
    vc_capacity_kn: float          # Concrete shear capacity
    vs_capacity_kn: float          # Stirrup shear capacity
    vn_capacity_kn: float          # Total shear capacity
    utilization: float
    tv_nmm2: float                 # Shear stress
    tc_nmm2: float                 # Design shear strength
    tc_max_nmm2: float             # Max shear stress
    stirrup_asv_mm2: float         # Required stirrup area
    stirrup_spacing_mm: float      # Recommended spacing
    clause_refs: list[str] = None


@dataclass
class TorsionResult:
    """Torsion design results."""
    is_ok: bool
    tu_demand_knm: float
    equivalent_shear_kn: float
    equivalent_moment_knm: float
    asv_torsion_mm2: float         # Stirrup area for torsion
    al_torsion_mm2: float          # Longitudinal steel for torsion
    clause_refs: list[str] = None


@dataclass
class DetailingResult:
    """Detailing results with bar arrangements."""
    is_valid: bool
    bottom_bars: list[BarArrangement]
    top_bars: list[BarArrangement]
    stirrups: list[StirrupArrangement]
    ld_tension_mm: float           # Development length (tension)
    ld_compression_mm: float       # Development length (compression)
    lap_length_mm: float
    clear_spacing_ok: bool
    cover_ok: bool
    remarks: str


@dataclass
class BarArrangement:
    """Single layer bar arrangement."""
    count: int
    diameter_mm: float
    area_mm2: float
    spacing_mm: float
    zone: str = "full"             # "start", "mid", "end", "full"

    def callout(self) -> str:
        """Return callout string like '4-20φ'."""
        return f"{self.count}-{int(self.diameter_mm)}φ"


@dataclass
class StirrupArrangement:
    """Stirrup arrangement for a zone."""
    diameter_mm: float
    legs: int
    spacing_mm: float
    zone_start_mm: float
    zone_end_mm: float

    def callout(self) -> str:
        """Return callout string like 'φ8 @ 150 c/c (4-leg)'."""
        return f"φ{int(self.diameter_mm)} @ {int(self.spacing_mm)} c/c ({self.legs}-leg)"


@dataclass
class DesignResult:
    """Complete design result."""
    beam_id: str
    story: str
    code: str
    is_ok: bool                    # Overall pass/fail
    flexure: FlexureResult
    shear: ShearResult
    torsion: TorsionResult | None = None
    detailing: DetailingResult | None = None
    governing_check: str = ""      # "flexure", "shear", "torsion"
    utilization: float = 0.0       # Max utilization
    remarks: str = ""
    warnings: list[str] = None
    errors: list[str] = None
    timestamp: str = ""            # ISO 8601 timestamp
    version: str = ""              # Library version

    def summary(self) -> str:
        """Human-readable summary."""

    def to_dict(self) -> dict:
        """Serialize to dictionary."""

    def to_json(self) -> str:
        """Serialize to JSON string."""
```

### 3D Geometry Types

```python
@dataclass(frozen=True, slots=True)
class Point3D:
    """3D point in millimeters."""
    x: float  # Along span
    y: float  # Across width
    z: float  # Vertical

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "z": self.z}


@dataclass(frozen=True, slots=True)
class RebarSegment:
    """Single rebar segment."""
    start: Point3D
    end: Point3D
    diameter_mm: float
    segment_type: str = "straight"  # "straight", "bend", "hook"

    @property
    def length_mm(self) -> float:
        """Segment length."""


@dataclass
class RebarPath:
    """Complete rebar path (one bar)."""
    bar_id: str
    segments: list[RebarSegment]
    diameter_mm: float
    bar_type: str      # "bottom", "top", "side"
    zone: str          # "start", "mid", "end", "full"

    @property
    def total_length_mm(self) -> float:
        """Total bar length."""


@dataclass
class StirrupLoop:
    """Single stirrup loop."""
    loop_id: str
    segments: list[RebarSegment]
    diameter_mm: float
    position_mm: float  # Position along span
    legs: int


@dataclass
class Beam3DGeometry:
    """Complete 3D beam geometry for visualization."""
    beam_id: str
    story: str
    geometry: dict[str, float]     # {b_mm, D_mm, span_mm, cover_mm}
    beam_outline: list[Point3D]    # 8 corners of beam box
    bottom_bars: list[RebarPath]
    top_bars: list[RebarPath]
    side_bars: list[RebarPath]
    stirrups: list[StirrupLoop]

    def to_dict(self) -> dict:
        """Serialize for Three.js."""

    def to_json(self) -> str:
        """JSON string for Three.js."""
```

---

## Engine API (`sk.engine`)

### `design_beam`

```python
def design_beam(
    beam: BeamInput,
    include_detailing: bool = True,
    include_3d: bool = False
) -> DesignResult:
    """
    Design a reinforced concrete beam.

    Performs complete beam design including flexure, shear, and
    optionally torsion checks per the specified code.

    Args:
        beam: Complete beam specification
        include_detailing: If True, compute bar/stirrup arrangements
        include_3d: If True, compute 3D geometry

    Returns:
        DesignResult with all check results

    Raises:
        ValidationError: If beam input is invalid
        CodeNotFoundError: If specified code not available

    Example:
        >>> beam = BeamInput(
        ...     beam_id="B1",
        ...     geometry=BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000),
        ...     materials=MaterialsInput.M25_FE500(),
        ...     loads=LoadsInput(mu_knm=200, vu_kn=100)
        ... )
        >>> result = sk.engine.design_beam(beam)
        >>> print(f"Status: {'PASS' if result.is_ok else 'FAIL'}")
        >>> print(f"Steel required: {result.flexure.ast_required_mm2:.0f} mm²")
    """
```

### `verify_beam`

```python
def verify_beam(
    beam: BeamInput,
    provided_ast_mm2: float,
    provided_stirrups: StirrupArrangement
) -> VerificationResult:
    """
    Verify a beam with provided reinforcement.

    Checks if provided reinforcement satisfies code requirements.
    Does not size or optimize—just verification.

    Args:
        beam: Beam specification
        provided_ast_mm2: Provided tension steel area
        provided_stirrups: Provided stirrup arrangement

    Returns:
        VerificationResult with pass/fail for each check

    Example:
        >>> result = sk.engine.verify_beam(
        ...     beam,
        ...     provided_ast_mm2=1256,  # 4-20φ
        ...     provided_stirrups=StirrupArrangement(8, 2, 150, 0, 5000)
        ... )
        >>> print(f"Flexure: {'OK' if result.flexure_ok else 'FAIL'}")
    """
```

### `batch_design`

```python
def batch_design(
    beams: list[BeamInput],
    parallel: bool = False,
    progress_callback: Callable[[int, int], None] | None = None
) -> list[DesignResult]:
    """
    Design multiple beams.

    Args:
        beams: List of beam specifications
        parallel: If True, use parallel processing
        progress_callback: Called with (completed, total) for progress

    Returns:
        List of DesignResult in same order as input

    Example:
        >>> beams = sk.io.read_csv("beams.csv")
        >>> results = sk.engine.batch_design(beams, parallel=True)
        >>> failures = [r for r in results if not r.is_ok]
        >>> print(f"Failures: {len(failures)}/{len(results)}")
    """
```

### `optimize_beam`

```python
def optimize_beam(
    constraints: OptimizationConstraints,
    objective: Literal["cost", "weight", "carbon"] = "cost",
    max_candidates: int = 1000
) -> OptimizationResult:
    """
    Find optimal beam dimensions.

    Searches through valid dimension combinations to minimize
    the specified objective while satisfying all constraints.

    Args:
        constraints: Design constraints (span, loads, limits)
        objective: What to minimize
        max_candidates: Maximum candidates to evaluate

    Returns:
        OptimizationResult with optimal design and alternatives

    Example:
        >>> constraints = OptimizationConstraints(
        ...     span_mm=5000,
        ...     mu_knm=200,
        ...     vu_kn=100,
        ...     b_range=(200, 400),
        ...     D_range=(400, 700)
        ... )
        >>> result = sk.engine.optimize_beam(constraints, objective="cost")
        >>> print(f"Optimal: {result.optimal.b_mm}x{result.optimal.D_mm}")
        >>> print(f"Cost: ₹{result.optimal.cost:.0f}")
    """
```

### `analyze_beam`

```python
def analyze_beam(
    beam: BeamInput,
    include_cost: bool = True,
    include_suggestions: bool = True,
    include_sensitivity: bool = False,
    include_constructability: bool = False
) -> AnalysisResult:
    """
    Comprehensive beam analysis with insights.

    Combines design with cost optimization, improvement suggestions,
    sensitivity analysis, and constructability assessment.

    Args:
        beam: Beam specification
        include_cost: Include cost breakdown and optimization
        include_suggestions: Include design improvement suggestions
        include_sensitivity: Include parameter sensitivity analysis
        include_constructability: Include constructability score

    Returns:
        AnalysisResult with all requested analyses

    Example:
        >>> result = sk.engine.analyze_beam(beam, include_suggestions=True)
        >>> for s in result.suggestions:
        ...     print(f"[{s.impact}] {s.title}")
    """
```

---

## Visualization API (`sk.viz`)

### `beam_3d`

```python
def beam_3d(
    result: DesignResult | DetailingResult
) -> Beam3DGeometry:
    """
    Generate 3D geometry from design result.

    Computes positions for all bars and stirrups in 3D space.

    Args:
        result: Design or detailing result

    Returns:
        Beam3DGeometry ready for rendering

    Example:
        >>> geometry = sk.viz.beam_3d(design_result)
        >>> print(f"Bottom bars: {len(geometry.bottom_bars)}")
        >>> print(f"Stirrups: {len(geometry.stirrups)}")
    """
```

### `to_threejs_json`

```python
def to_threejs_json(
    geometry: Beam3DGeometry,
    options: RenderOptions | None = None
) -> str:
    """
    Convert geometry to Three.js-compatible JSON.

    Args:
        geometry: 3D geometry object
        options: Rendering options (colors, scale, etc.)

    Returns:
        JSON string for Three.js viewer

    Example:
        >>> json_str = sk.viz.to_threejs_json(geometry)
        >>> # Pass to Three.js viewer component
    """
```

### `plot_bmd_sfd`

```python
def plot_bmd_sfd(
    span_mm: float,
    loads: list[LoadDefinition],
    support: str = "simply_supported"
) -> go.Figure:
    """
    Plot bending moment and shear force diagrams.

    Args:
        span_mm: Beam span
        loads: List of load definitions
        support: Support condition

    Returns:
        Plotly figure with BMD and SFD

    Example:
        >>> fig = sk.viz.plot_bmd_sfd(5000, [UDL(25)])
        >>> fig.show()
    """
```

### `plot_section`

```python
def plot_section(
    result: DesignResult,
    show_bars: bool = True,
    show_stirrups: bool = True
) -> go.Figure:
    """
    Plot beam cross-section with reinforcement.

    Args:
        result: Design result with detailing
        show_bars: Show longitudinal bars
        show_stirrups: Show stirrup outline

    Returns:
        Plotly figure of cross-section
    """
```

### `compliance_panel`

```python
def compliance_panel(
    result: DesignResult
) -> dict:
    """
    Generate compliance panel data for UI.

    Returns:
        Dictionary with check statuses for rendering traffic-light panel
        {
            "flexure": {"status": "pass", "utilization": 0.85, "color": "green"},
            "shear": {"status": "pass", "utilization": 0.72, "color": "green"},
            "detailing": {"status": "warn", "utilization": 0.95, "color": "yellow"}
        }
    """
```

---

## I/O API (`sk.io`)

### `read_csv`

```python
def read_csv(
    path: str | Path,
    schema: str = "standard",
    column_mapping: dict[str, str] | None = None
) -> list[BeamInput]:
    """
    Read beams from CSV file.

    Args:
        path: Path to CSV file
        schema: Column schema ("standard", "etabs", "custom")
        column_mapping: Custom column name mapping

    Returns:
        List of BeamInput objects

    Standard Schema Columns:
        beam_id, story, b_mm, D_mm, span_mm, cover_mm,
        fck_nmm2, fy_nmm2, mu_knm, vu_kn

    Example:
        >>> beams = sk.io.read_csv("input.csv")
        >>> print(f"Loaded {len(beams)} beams")
    """
```

### `read_etabs`

```python
def read_etabs(
    path: str | Path,
    geometry_spec: dict | None = None
) -> list[BeamInput]:
    """
    Read beams from ETABS CSV export.

    Args:
        path: Path to ETABS export CSV
        geometry_spec: Default geometry for beams

    Returns:
        List of BeamInput with forces from ETABS

    Example:
        >>> beams = sk.io.read_etabs("etabs_forces.csv", {"b_mm": 300, "D_mm": 500})
    """
```

### `export_dxf`

```python
def export_dxf(
    detailing: DetailingResult | list[DetailingResult],
    path: str | Path,
    include_dimensions: bool = True,
    include_title_block: bool = False
) -> Path:
    """
    Export detailing to DXF drawing.

    Args:
        detailing: Detailing result(s) to export
        path: Output file path
        include_dimensions: Add dimension annotations
        include_title_block: Add standard title block

    Returns:
        Path to created DXF file

    Example:
        >>> path = sk.io.export_dxf(result.detailing, "beam_B1.dxf")
        >>> print(f"Created: {path}")
    """
```

### `export_bbs`

```python
def export_bbs(
    detailing: DetailingResult | list[DetailingResult],
    path: str | Path,
    format: Literal["csv", "json", "excel"] = "csv",
    project_name: str = "Project"
) -> Path:
    """
    Export bar bending schedule.

    Args:
        detailing: Detailing result(s)
        path: Output file path
        format: Output format
        project_name: Project name for header

    Returns:
        Path to created file

    Example:
        >>> path = sk.io.export_bbs(results, "bbs.csv")
    """
```

### `export_report`

```python
def export_report(
    result: DesignResult,
    path: str | Path,
    format: Literal["html", "pdf", "json"] = "html",
    include_calculations: bool = True,
    include_3d: bool = False
) -> Path:
    """
    Export design report.

    Args:
        result: Design result to report
        path: Output file path
        format: Report format
        include_calculations: Show step-by-step calculations
        include_3d: Embed 3D view (HTML only)

    Returns:
        Path to created report

    Example:
        >>> path = sk.io.export_report(result, "report.html")
    """
```

---

## Utility API (`sk.utils`)

### `validate`

```python
def validate(beam: BeamInput) -> ValidationResult:
    """
    Validate beam input without designing.

    Returns:
        ValidationResult with errors and warnings

    Example:
        >>> result = sk.utils.validate(beam)
        >>> if not result.is_valid:
        ...     for error in result.errors:
        ...         print(f"Error: {error}")
    """
```

### `get_version`

```python
def get_version() -> str:
    """Return library version string."""
```

### `list_codes`

```python
def list_codes() -> list[CodeInfo]:
    """
    List available design codes.

    Returns:
        List of CodeInfo with name, version, status
    """
```

---

## Code-Specific API (`sk.codes`)

For advanced users who need direct access to code-specific functions:

```python
# IS 456 direct access
sk.codes.is456.flexure.design_singly_reinforced(mu, b, d, fck, fy)
sk.codes.is456.flexure.design_doubly_reinforced(mu, b, d, d_dash, fck, fy)
sk.codes.is456.shear.design_stirrups(vu, b, d, fck, pt)
sk.codes.is456.shear.get_tc(fck, pt)  # Table 19
sk.codes.is456.detailing.compute_development_length(bar_dia, fck, fy)
sk.codes.is456.detailing.compute_lap_length(bar_dia, fck, fy)
sk.codes.is456.tables.get_xu_max_ratio(fy)

# ACI 318 direct access (when implemented)
sk.codes.aci318.flexure.design(mu, b, d, fc, fy)
sk.codes.aci318.shear.design(vu, b, d, fc, rho)

# EC2 direct access (when implemented)
sk.codes.ec2.flexure.design(med, b, d, fck, fyk)
sk.codes.ec2.shear.design_variable_strut(ved, b, d, fck, rho)
```

---

## Error Handling

```python
class StructuralSDKError(Exception):
    """Base exception for all SDK errors."""

class ValidationError(StructuralSDKError):
    """Input validation failed."""
    errors: list[str]

class DesignError(StructuralSDKError):
    """Design calculation failed."""
    check: str  # "flexure", "shear", etc.
    reason: str

class CodeNotFoundError(StructuralSDKError):
    """Requested design code not available."""
    code: str
    available: list[str]

class ExportError(StructuralSDKError):
    """Export operation failed."""
    format: str
    reason: str
```

---

## Backward Compatibility

The existing `api.py` functions remain available but are deprecated:

```python
# Old API (deprecated)
from structural_lib import api
api.design_beam_is456(...)  # Still works, emits DeprecationWarning

# New API (preferred)
import structural_sdk as sk
sk.engine.design_beam(...)
```

Migration guide:

| Old Function | New Function |
|--------------|--------------|
| `api.design_beam_is456()` | `sk.engine.design_beam(beam, code="IS456")` |
| `api.check_beam_is456()` | `sk.engine.verify_beam()` |
| `api.compute_detailing()` | Included in `design_beam()` |
| `api.compute_bbs()` | `sk.io.export_bbs()` |
| `api.compute_dxf()` | `sk.io.export_dxf()` |
| `api.beam_to_3d_geometry()` | `sk.viz.beam_3d()` |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-16 | Initial contract definition |

---

*This contract is binding. Breaking changes require major version bump.*
