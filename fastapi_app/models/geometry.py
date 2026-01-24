"""
3D Geometry Pydantic Models.

Models for 3D geometry generation API endpoints for visualization.
"""

from pydantic import BaseModel, Field


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
