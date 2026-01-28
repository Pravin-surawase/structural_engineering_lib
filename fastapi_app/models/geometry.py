"""
3D Geometry Pydantic Models.

Models for 3D geometry generation API endpoints for visualization.
"""

from pydantic import BaseModel, Field

# =============================================================================
# Point/Segment Models (matching library's geometry_3d.py)
# =============================================================================


class Point3DModel(BaseModel):
    """3D point in millimeters."""

    x: float = Field(description="X-coordinate along span (mm)")
    y: float = Field(description="Y-coordinate across width (mm)")
    z: float = Field(description="Z-coordinate height (mm)")


class RebarSegmentModel(BaseModel):
    """A single straight segment of a reinforcement bar."""

    start: Point3DModel = Field(description="Start point")
    end: Point3DModel = Field(description="End point")
    diameter: float = Field(description="Bar diameter (mm)")
    type: str = Field(default="straight", description="Segment type")
    length: float = Field(description="Segment length (mm)")


class RebarPathModel(BaseModel):
    """Complete path of a reinforcement bar with segments."""

    barId: str = Field(description="Unique bar identifier")
    segments: list[RebarSegmentModel] = Field(description="Bar segments")
    diameter: float = Field(description="Bar diameter (mm)")
    barType: str = Field(description="Bar type: bottom, top, side")
    zone: str = Field(description="Zone: start, mid, end, full")
    totalLength: float = Field(description="Total cutting length (mm)")


class StirrupLoopModel(BaseModel):
    """A stirrup closed loop at a specific X position."""

    positionX: float = Field(description="X position along span (mm)")
    path: list[Point3DModel] = Field(description="Corner points of loop")
    diameter: float = Field(description="Stirrup bar diameter (mm)")
    legs: int = Field(default=2, description="Number of legs")
    hookType: str = Field(default="90", description="Hook angle")
    perimeter: float = Field(description="Stirrup perimeter (mm)")


class Beam3DGeometryModel(BaseModel):
    """Complete 3D geometry for beam visualization (matches library output)."""

    beamId: str = Field(description="Beam identifier")
    story: str = Field(description="Story/floor identifier")
    dimensions: dict[str, float] = Field(
        description="Beam dimensions {b, D, span} in mm"
    )
    concreteOutline: list[Point3DModel] = Field(
        description="8 corner points of beam box"
    )
    rebars: list[RebarPathModel] = Field(description="All rebar paths")
    stirrups: list[StirrupLoopModel] = Field(description="All stirrup loops")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
    version: str = Field(default="1.0.0", description="Schema version")


class BeamGeometryRequest(BaseModel):
    """Request model for beam 3D geometry generation using library API."""

    # Core beam identification
    beam_id: str = Field(default="B1", description="Beam identifier")
    story: str = Field(default="GF", description="Story/floor name")

    # Section dimensions
    width: float = Field(gt=0, le=2000.0, description="Beam width b (mm)")
    depth: float = Field(gt=0, le=3000.0, description="Beam depth D (mm)")
    span: float = Field(gt=0, description="Beam span L (mm)")

    # Material properties
    fck: float = Field(default=25.0, ge=15.0, le=80.0, description="fck (N/mm²)")
    fy: float = Field(default=500.0, ge=250.0, le=600.0, description="fy (N/mm²)")

    # Reinforcement areas (from design)
    ast_start: float = Field(
        default=500.0, ge=0, description="Tension steel at start (mm²)"
    )
    ast_mid: float = Field(
        default=400.0, ge=0, description="Tension steel at mid-span (mm²)"
    )
    ast_end: float = Field(
        default=500.0, ge=0, description="Tension steel at end (mm²)"
    )

    # Stirrups
    stirrup_dia: float = Field(
        default=8.0, ge=6.0, le=16.0, description="Stirrup diameter (mm)"
    )
    stirrup_spacing_start: float = Field(
        default=100.0, gt=0, le=300.0, description="Stirrup spacing at start (mm)"
    )
    stirrup_spacing_mid: float = Field(
        default=150.0, gt=0, le=300.0, description="Stirrup spacing at mid (mm)"
    )
    stirrup_spacing_end: float = Field(
        default=100.0, gt=0, le=300.0, description="Stirrup spacing at end (mm)"
    )

    # Cover
    cover: float = Field(default=40.0, ge=20.0, le=75.0, description="Clear cover (mm)")

    # Options
    is_seismic: bool = Field(default=False, description="Use seismic detailing")


class BeamGeometryResponse(BaseModel):
    """Response model for full beam 3D geometry."""

    success: bool = Field(description="Whether generation succeeded")
    message: str = Field(description="Summary message")
    geometry: Beam3DGeometryModel | None = Field(
        default=None, description="Full 3D geometry"
    )
    warnings: list[str] = Field(default_factory=list, description="Any warnings")


# =============================================================================
# Building Geometry Models
# =============================================================================


class BuildingBeamModel(BaseModel):
    """Single beam in building geometry (line representation)."""

    beam_id: str = Field(description="Beam identifier")
    story: str = Field(description="Story/floor identifier")
    frame_type: str = Field(description="Frame type: beam, column, brace")
    start: Point3DModel = Field(description="Start point (mm)")
    end: Point3DModel = Field(description="End point (mm)")


class BuildingGeometryResponse(BaseModel):
    """Response model for building-level 3D geometry."""

    success: bool = Field(description="Whether generation succeeded")
    message: str = Field(description="Summary message")
    beams: list[BuildingBeamModel] = Field(description="All building members")
    bounding_box: dict[str, float] = Field(description="Overall bounding box")
    center: Point3DModel = Field(description="Center point")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
    warnings: list[str] = Field(default_factory=list, description="Any warnings")


class BuildingGeometryRequest(BaseModel):
    """Request model for building geometry generation."""

    beams: list[dict] = Field(
        description="List of beam geometry dicts with point1, point2, id, story, frame_type"
    )
    unit_scale: float = Field(
        default=1000.0, description="Scale factor (default: m to mm)"
    )
    include_frame_types: list[str] | None = Field(
        default=None, description="Optional filter for frame types"
    )


# =============================================================================
# Cross-Section Geometry Models
# =============================================================================


class CrossSectionRequest(BaseModel):
    """Request model for 2D cross-section geometry."""

    width: float = Field(gt=0, le=2000.0, description="Beam width b (mm)")
    depth: float = Field(gt=0, le=3000.0, description="Beam depth D (mm)")
    cover: float = Field(default=40.0, ge=20.0, le=75.0, description="Clear cover (mm)")
    tension_bars: int = Field(
        default=3, ge=2, le=12, description="Number of tension bars"
    )
    compression_bars: int = Field(
        default=2, ge=0, le=8, description="Number of compression bars"
    )
    bar_dia: float = Field(
        default=16.0, ge=8.0, le=36.0, description="Main bar diameter (mm)"
    )
    stirrup_dia: float = Field(
        default=8.0, ge=6.0, le=16.0, description="Stirrup diameter (mm)"
    )


class CrossSectionResponse(BaseModel):
    """Response model for 2D cross-section geometry."""

    success: bool = Field(description="Whether generation succeeded")
    message: str = Field(description="Summary message")
    outline: list[Point3DModel] = Field(description="Section outline corners")
    tension_bars: list[Point3DModel] = Field(description="Tension bar positions")
    compression_bars: list[Point3DModel] = Field(
        description="Compression bar positions"
    )
    stirrup_path: list[Point3DModel] = Field(description="Stirrup inner path")
    dimensions: dict[str, float] = Field(description="Section dimensions")
    warnings: list[str] = Field(default_factory=list, description="Any warnings")


# =============================================================================
# Request Models
# =============================================================================


class Geometry3DRequest(BaseModel):
    """Request model for 3D geometry generation."""

    # Section dimensions
    width: float = Field(gt=0, le=2000.0, description="Beam width b (mm)")
    depth: float = Field(gt=0, le=3000.0, description="Beam depth D (mm)")
    length: float = Field(gt=0, description="Beam length L (mm)")

    # Reinforcement (optional - for visualization)
    tension_bars: list[dict] | None = Field(
        default=None,
        description="Tension bar arrangement for visualization",
        examples=[[{"diameter": 16, "count": 3, "layer": 1}]],
    )
    compression_bars: list[dict] | None = Field(
        default=None,
        description="Compression bar arrangement for visualization",
    )
    stirrup_diameter: int | None = Field(
        default=None,
        ge=6,
        le=16,
        description="Stirrup diameter (mm)",
    )
    stirrup_spacing: float | None = Field(
        default=None,
        gt=0,
        le=300.0,
        description="Stirrup spacing (mm)",
    )

    # Cover
    clear_cover: float = Field(
        default=25.0,
        ge=20.0,
        le=75.0,
        description="Clear cover (mm)",
    )

    # Geometry options
    include_rebars: bool = Field(
        default=True,
        description="Include reinforcement in 3D model",
    )
    include_stirrups: bool = Field(
        default=True,
        description="Include stirrups in 3D model",
    )
    mesh_resolution: str = Field(
        default="medium",
        description="Mesh resolution for 3D model",
        pattern="^(low|medium|high)$",
    )
    output_format: str = Field(
        default="vertices_faces",
        description="Output format for 3D geometry",
        pattern="^(vertices_faces|stl|gltf)$",
    )


# =============================================================================
# Response Models
# =============================================================================


class MeshData(BaseModel):
    """3D mesh data in vertices/faces format."""

    vertices: list[list[float]] = Field(
        description="List of vertex coordinates [[x, y, z], ...]"
    )
    faces: list[list[int]] = Field(
        description="List of face indices [[v0, v1, v2], ...]"
    )
    normals: list[list[float]] | None = Field(
        default=None,
        description="Vertex normals for lighting",
    )


class BoundingBox(BaseModel):
    """Axis-aligned bounding box."""

    min_x: float = Field(description="Minimum X coordinate (mm)")
    max_x: float = Field(description="Maximum X coordinate (mm)")
    min_y: float = Field(description="Minimum Y coordinate (mm)")
    max_y: float = Field(description="Maximum Y coordinate (mm)")
    min_z: float = Field(description="Minimum Z coordinate (mm)")
    max_z: float = Field(description="Maximum Z coordinate (mm)")


class GeometryComponent(BaseModel):
    """Single geometry component (beam, rebar, stirrup)."""

    name: str = Field(description="Component name")
    type: str = Field(
        description="Component type",
        examples=["beam", "rebar", "stirrup"],
    )
    mesh: MeshData = Field(description="Mesh data for component")
    color: list[float] = Field(
        description="RGBA color [r, g, b, a] in 0-1 range",
        min_length=4,
        max_length=4,
    )
    material_hint: str = Field(
        default="concrete",
        description="Material type hint for rendering",
        examples=["concrete", "steel", "formwork"],
    )


class Geometry3DResponse(BaseModel):
    """Response model for 3D geometry generation."""

    success: bool = Field(description="Whether geometry generation succeeded")
    message: str = Field(description="Summary message")

    # Geometry data
    components: list[GeometryComponent] = Field(
        description="List of geometry components"
    )

    # Bounding box for camera framing
    bounding_box: BoundingBox = Field(description="Overall bounding box")

    # Scene metadata
    center: list[float] = Field(
        description="Center point [x, y, z] for camera target",
        min_length=3,
        max_length=3,
    )
    suggested_camera_distance: float = Field(
        description="Suggested camera distance for framing (mm)"
    )

    # Statistics
    total_vertices: int = Field(description="Total vertex count")
    total_faces: int = Field(description="Total face count")

    # Alternative formats (if requested)
    stl_base64: str | None = Field(
        default=None,
        description="Base64-encoded STL file (if requested)",
    )
    gltf_json: dict | None = Field(
        default=None,
        description="GLTF JSON data (if requested)",
    )

    # Warnings
    warnings: list[str] = Field(default_factory=list, description="Geometry warnings")
