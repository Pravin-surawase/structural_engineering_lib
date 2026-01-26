"""
3D Geometry Router.

Endpoints for geometry generation for visualization.
Uses structural_lib.visualization.geometry_3d for accurate calculations.
"""

from fastapi import APIRouter, HTTPException, status

from fastapi_app.models.geometry import (
    Geometry3DRequest,
    Geometry3DResponse,
    MeshData,
    BoundingBox,
    GeometryComponent,
    BeamGeometryRequest,
    BeamGeometryResponse,
    Beam3DGeometryModel,
    Point3DModel,
    RebarPathModel,
    RebarSegmentModel,
    StirrupLoopModel,
)

router = APIRouter(
    prefix="/geometry",
    tags=["geometry"],
)


# =============================================================================
# Geometry Endpoints
# =============================================================================


@router.post(
    "/beam/3d",
    response_model=Geometry3DResponse,
    summary="Generate 3D Beam Geometry",
    description="Generate 3D mesh geometry for beam visualization.",
)
async def generate_beam_geometry(
    request: Geometry3DRequest,
) -> Geometry3DResponse:
    """
    Generate 3D geometry for a beam section.

    Creates:
    - Beam concrete mesh
    - Reinforcement bar meshes (if specified)
    - Stirrup meshes (if specified)

    Output formats:
    - vertices_faces: Direct mesh data (default)
    - stl: Base64-encoded STL file
    - gltf: GLTF JSON data

    Useful for:
    - React Three.js visualization
    - CAD export
    - 3D printing
    """
    try:
        from structural_lib.api import detail_beam_is456, beam_to_3d_geometry

        # First create a detailing result to pass to geometry function
        detailing_result = detail_beam_is456(
            units="IS456",
            beam_id="BEAM-3D",
            story="1F",
            b_mm=request.width,
            D_mm=request.depth,
            span_mm=request.length,
            cover_mm=request.clear_cover,
            fck_nmm2=25.0,
            fy_nmm2=500.0,
            ast_start_mm2=500.0,
            ast_mid_mm2=400.0,
            ast_end_mm2=500.0,
            stirrup_dia_mm=request.stirrup_diameter or 8.0,
            stirrup_spacing_start_mm=request.stirrup_spacing or 150.0,
            stirrup_spacing_mid_mm=request.stirrup_spacing or 200.0,
            stirrup_spacing_end_mm=request.stirrup_spacing or 150.0,
            is_seismic=False,
        )

        # Generate 3D geometry from detailing result
        geometry_result = beam_to_3d_geometry(
            detailing=detailing_result,
            is_seismic=False,
        )

        # Parse components from result - if not available, use fallback
        if not hasattr(geometry_result, "vertices") or not geometry_result.vertices:
            return _generate_fallback_geometry(request)

        # Build mesh from geometry result
        mesh = MeshData(
            vertices=(
                geometry_result.vertices if hasattr(geometry_result, "vertices") else []
            ),
            faces=geometry_result.faces if hasattr(geometry_result, "faces") else [],
            normals=None,
        )

        beam_component = GeometryComponent(
            name="beam",
            type="beam",
            mesh=mesh,
            color=[0.75, 0.75, 0.75, 1.0],
            material_hint="concrete",
        )

        import math

        bounding_box = BoundingBox(
            min_x=0,
            max_x=request.width,
            min_y=0,
            max_y=request.depth,
            min_z=0,
            max_z=request.length,
        )

        center = [request.width / 2, request.depth / 2, request.length / 2]
        diagonal = math.sqrt(request.width**2 + request.depth**2 + request.length**2)

        return Geometry3DResponse(
            success=True,
            message=f"Generated beam geometry with {len(mesh.vertices)} vertices",
            components=[beam_component],
            bounding_box=bounding_box,
            center=center,
            suggested_camera_distance=diagonal * 1.5,
            total_vertices=len(mesh.vertices),
            total_faces=len(mesh.faces),
            stl_base64=None,
            gltf_json=None,
            warnings=[],
        )

    except ImportError:
        # Fallback: Generate simple box geometry if structural_lib unavailable
        return _generate_fallback_geometry(request)
    except (ValueError, AttributeError, TypeError):
        # Fallback on errors
        return _generate_fallback_geometry(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Geometry generation failed: {e}",
        )


def _generate_fallback_geometry(request: Geometry3DRequest) -> Geometry3DResponse:
    """Generate simple box geometry as fallback."""
    import math

    w, d, length_val = request.width, request.depth, request.length

    # Simple box vertices (8 corners)
    vertices = [
        [0, 0, 0],
        [w, 0, 0],
        [w, d, 0],
        [0, d, 0],  # Front face
        [0, 0, length_val],
        [w, 0, length_val],
        [w, d, length_val],
        [0, d, length_val],  # Back face
    ]

    # Box faces (12 triangles for 6 faces)
    faces = [
        [0, 1, 2],
        [0, 2, 3],  # Front
        [4, 6, 5],
        [4, 7, 6],  # Back
        [0, 4, 5],
        [0, 5, 1],  # Bottom
        [2, 6, 7],
        [2, 7, 3],  # Top
        [0, 3, 7],
        [0, 7, 4],  # Left
        [1, 5, 6],
        [1, 6, 2],  # Right
    ]

    mesh = MeshData(vertices=vertices, faces=faces, normals=None)

    beam_component = GeometryComponent(
        name="beam",
        type="beam",
        mesh=mesh,
        color=[0.75, 0.75, 0.75, 1.0],  # Concrete gray
        material_hint="concrete",
    )

    bounding_box = BoundingBox(
        min_x=0,
        max_x=w,
        min_y=0,
        max_y=d,
        min_z=0,
        max_z=length_val,
    )

    center = [w / 2, d / 2, length_val / 2]
    diagonal = math.sqrt(w**2 + d**2 + length_val**2)

    return Geometry3DResponse(
        success=True,
        message="Generated fallback geometry (structural_lib not available)",
        components=[beam_component],
        bounding_box=bounding_box,
        center=center,
        suggested_camera_distance=diagonal * 1.5,
        total_vertices=8,
        total_faces=12,
        stl_base64=None,
        gltf_json=None,
        warnings=["Using fallback geometry - structural_lib not available"],
    )


# =============================================================================
# Full 3D Geometry from Library (Recommended for React)
# =============================================================================


@router.post(
    "/beam/full",
    response_model=BeamGeometryResponse,
    summary="Generate Full Beam 3D Geometry",
    description="""
Generate complete 3D geometry with rebars and stirrups using structural_lib.

This endpoint returns rich geometry data including:
- Concrete outline (8 corner points)
- Rebar paths with segments (position, diameter, length)
- Stirrup loops with corner positions

Ideal for React Three Fiber rendering with cylinder/tube primitives.
""",
)
async def generate_full_beam_geometry(
    request: BeamGeometryRequest,
) -> BeamGeometryResponse:
    """
    Generate complete 3D geometry for beam visualization.

    Uses structural_lib.visualization.geometry_3d.beam_to_3d_geometry()
    to compute accurate rebar and stirrup positions based on:
    - IS 456:2000 detailing rules
    - Bar spacing requirements
    - Zone-based stirrup calculations

    Returns geometry suitable for:
    - React Three Fiber (cylinders, tubes)
    - Three.js BufferGeometry
    - CAD visualization

    Note: This is the recommended endpoint for modern 3D visualization.
    """
    try:
        from structural_lib.api import detail_beam_is456, beam_to_3d_geometry

        # Create detailing result from design parameters
        detailing_result = detail_beam_is456(
            units="IS456",
            beam_id=request.beam_id,
            story=request.story,
            b_mm=request.width,
            D_mm=request.depth,
            span_mm=request.span,
            cover_mm=request.cover,
            fck_nmm2=request.fck,
            fy_nmm2=request.fy,
            ast_start_mm2=request.ast_start,
            ast_mid_mm2=request.ast_mid,
            ast_end_mm2=request.ast_end,
            stirrup_dia_mm=request.stirrup_dia,
            stirrup_spacing_start_mm=request.stirrup_spacing_start,
            stirrup_spacing_mid_mm=request.stirrup_spacing_mid,
            stirrup_spacing_end_mm=request.stirrup_spacing_end,
            is_seismic=request.is_seismic,
        )

        # Generate 3D geometry from detailing
        geometry = beam_to_3d_geometry(
            detailing=detailing_result,
            is_seismic=request.is_seismic,
        )

        # Convert library dataclass to Pydantic model
        geometry_dict = geometry.to_dict()

        # Convert to Pydantic models
        concrete_outline = [
            Point3DModel(**pt) for pt in geometry_dict["concreteOutline"]
        ]

        rebars = []
        for rb in geometry_dict["rebars"]:
            segments = [RebarSegmentModel(**seg) for seg in rb["segments"]]
            rebars.append(
                RebarPathModel(
                    barId=rb["barId"],
                    segments=segments,
                    diameter=rb["diameter"],
                    barType=rb["barType"],
                    zone=rb["zone"],
                    totalLength=rb["totalLength"],
                )
            )

        stirrups = []
        for st in geometry_dict["stirrups"]:
            path = [Point3DModel(**pt) for pt in st["path"]]
            stirrups.append(
                StirrupLoopModel(
                    positionX=st["positionX"],
                    path=path,
                    diameter=st["diameter"],
                    legs=st["legs"],
                    hookType=st["hookType"],
                    perimeter=st["perimeter"],
                )
            )

        geometry_model = Beam3DGeometryModel(
            beamId=geometry_dict["beamId"],
            story=geometry_dict["story"],
            dimensions=geometry_dict["dimensions"],
            concreteOutline=concrete_outline,
            rebars=rebars,
            stirrups=stirrups,
            metadata=geometry_dict["metadata"],
            version=geometry_dict.get("version", "1.0.0"),
        )

        return BeamGeometryResponse(
            success=True,
            message=(
                f"Generated geometry with {len(rebars)} rebars "
                f"and {len(stirrups)} stirrups"
            ),
            geometry=geometry_model,
            warnings=[],
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"structural_lib not available: {e}",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid parameters: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Geometry generation failed: {e}",
        )


@router.get(
    "/materials",
    summary="Get Material Appearance",
    description="Get material colors and properties for visualization.",
)
async def get_materials() -> dict:
    """
    Get standard material appearances for visualization.

    Returns RGBA colors and material hints for different components.
    """
    return {
        "concrete": {
            "color": [0.75, 0.75, 0.75, 1.0],
            "roughness": 0.9,
            "metalness": 0.0,
            "description": "Standard concrete gray",
        },
        "steel": {
            "color": [0.3, 0.3, 0.35, 1.0],
            "roughness": 0.4,
            "metalness": 0.8,
            "description": "Reinforcement steel",
        },
        "formwork": {
            "color": [0.6, 0.4, 0.2, 0.5],
            "roughness": 0.7,
            "metalness": 0.0,
            "description": "Timber formwork (semi-transparent)",
        },
        "highlight": {
            "color": [1.0, 0.8, 0.0, 1.0],
            "roughness": 0.3,
            "metalness": 0.0,
            "description": "Highlight color for selection",
        },
    }


# =============================================================================
# Building 3D Geometry (V2)
# =============================================================================


from pydantic import BaseModel, Field
from typing import Any


class BuildingGeometryRequest(BaseModel):
    """Request for building 3D geometry."""

    beams: list[dict[str, Any]] = Field(
        ...,
        description="List of beam data with id, story, section, coordinates",
    )
    design_results: list[dict[str, Any]] | None = Field(
        None,
        description="Optional design results for status coloring",
    )
    lod: str = Field(
        "medium",
        description="Level of detail: low, medium, high",
    )
    story_height: float = Field(
        3000.0,
        description="Default story height in mm for auto-positioning",
    )


class BuildingGeometryResponse(BaseModel):
    """Response with building 3D geometry."""

    success: bool
    message: str
    beam_count: int
    story_count: int
    bounds: dict[str, list[float]]
    camera_target: dict[str, float]
    beams: list[dict[str, Any]]
    metadata: dict[str, Any] = Field(default_factory=dict)


@router.post(
    "/building",
    response_model=BuildingGeometryResponse,
    summary="Generate Building 3D Geometry",
    description="Generate 3D geometry for entire building (multi-beam view).",
)
async def generate_building_geometry(
    request: BuildingGeometryRequest,
) -> BuildingGeometryResponse:
    """
    Generate 3D geometry for building visualization.

    Creates instancing-ready geometry for React Three Fiber:
    - Beam instances with position, rotation, dimensions
    - Color by design status (pass/fail/warning)
    - Camera target and bounds for framing

    Useful for:
    - Building overview in React workspace
    - Multi-beam visualization
    - Story filtering and navigation
    """
    try:
        from structural_lib.visualization.geometry_3d import building_to_3d_geometry

        # Call library function
        result = building_to_3d_geometry(
            beams=request.beams,
            design_results=request.design_results,
            lod=request.lod,
            story_height=request.story_height,
        )

        # Convert to response format
        result_dict = result.to_dict()

        return BuildingGeometryResponse(
            success=True,
            message=f"Generated geometry for {result.beam_count} beams",
            beam_count=result.beam_count,
            story_count=len(result.stories),
            bounds=result_dict["bounds"],
            camera_target=result_dict["cameraTarget"],
            beams=result_dict["beams"],
            metadata=result_dict["metadata"],
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"structural_lib not available: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Building geometry generation failed: {e}",
        )


# =============================================================================
# Cross-Section Geometry
# =============================================================================


class CrossSectionRequest(BaseModel):
    """Request for 2D cross-section geometry."""

    width: float = Field(..., description="Beam width in mm")
    depth: float = Field(..., description="Beam depth in mm")
    cover: float = Field(40.0, description="Clear cover in mm")
    bottom_bars: list[tuple[int, float]] = Field(
        default_factory=list,
        description="Bottom bars as [(count, diameter), ...]",
    )
    top_bars: list[tuple[int, float]] = Field(
        default_factory=list,
        description="Top bars as [(count, diameter), ...]",
    )
    stirrup_dia: float = Field(8.0, description="Stirrup diameter in mm")


class CrossSectionResponse(BaseModel):
    """Response with 2D cross-section geometry."""

    success: bool
    width: float
    depth: float
    cover: float
    rebars: list[dict[str, float]]
    stirrup_path: list[dict[str, float]]


@router.post(
    "/cross-section",
    response_model=CrossSectionResponse,
    summary="Generate Cross-Section Geometry",
    description="Generate 2D cross-section for beam editor view.",
)
async def generate_cross_section(
    request: CrossSectionRequest,
) -> CrossSectionResponse:
    """
    Generate 2D cross-section geometry for editor.

    Creates geometry data for canvas/SVG rendering:
    - Rebar positions (y, z, diameter)
    - Stirrup outline path

    Useful for:
    - React rebar editor
    - Cross-section overlay in 3D view
    """
    try:
        from structural_lib.visualization.geometry_3d import cross_section_geometry

        result = cross_section_geometry(
            width=request.width,
            depth=request.depth,
            cover=request.cover,
            bottom_bars=request.bottom_bars,
            top_bars=request.top_bars,
            stirrup_dia=request.stirrup_dia,
        )

        result_dict = result.to_dict()

        return CrossSectionResponse(
            success=True,
            width=result.width,
            depth=result.depth,
            cover=result.cover,
            rebars=result_dict["rebars"],
            stirrup_path=result_dict["stirrupPath"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cross-section generation failed: {e}",
        )


# =============================================================================
# Rebar Validation
# =============================================================================


class RebarConfigRequest(BaseModel):
    """Request for rebar validation."""

    beam_width: float = Field(..., description="Beam width in mm")
    beam_depth: float = Field(..., description="Beam depth in mm")
    cover: float = Field(40.0, description="Clear cover in mm")
    bottom_bars: list[tuple[int, float]] = Field(
        default_factory=list,
        description="Bottom bars as [(count, diameter), ...]",
    )
    top_bars: list[tuple[int, float]] = Field(
        default_factory=list,
        description="Top bars as [(count, diameter), ...]",
    )
    stirrup_dia: float = Field(8.0, description="Stirrup diameter in mm")
    stirrup_spacing: float = Field(150.0, description="Stirrup spacing in mm")
    is_seismic: bool = Field(False, description="Apply seismic detailing rules")
    ast_required: float | None = Field(None, description="Required steel area for check")


class RebarValidationResponse(BaseModel):
    """Response from rebar validation."""

    success: bool
    is_valid: bool
    errors: list[dict[str, Any]]
    warnings: list[dict[str, Any]]
    computed: dict[str, Any]


@router.post(
    "/rebar/validate",
    response_model=RebarValidationResponse,
    summary="Validate Rebar Configuration",
    description="Validate rebar layout against IS 456 requirements.",
)
async def validate_rebar(
    request: RebarConfigRequest,
) -> RebarValidationResponse:
    """
    Validate rebar configuration against code requirements.

    Checks:
    - Bar spacing (horizontal clearance)
    - Cover requirements
    - Seismic stirrup rules (if is_seismic)
    - Steel area vs required (if ast_required provided)

    Returns structured errors and warnings for UI display.
    """
    try:
        from structural_lib.rebar import validate_rebar_config, RebarConfig

        config = RebarConfig(
            bottom_bars=request.bottom_bars,
            top_bars=request.top_bars,
            stirrup_dia=request.stirrup_dia,
            stirrup_spacing=request.stirrup_spacing,
            is_seismic=request.is_seismic,
            cover_mm=request.cover,
        )

        result = validate_rebar_config(
            beam_width=request.beam_width,
            beam_depth=request.beam_depth,
            cover=request.cover,
            config=config,
            ast_required=request.ast_required,
        )

        result_dict = result.to_dict()

        return RebarValidationResponse(
            success=True,
            is_valid=result.is_valid,
            errors=result_dict["errors"],
            warnings=result_dict["warnings"],
            computed=result_dict["computed"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rebar validation failed: {e}",
        )
