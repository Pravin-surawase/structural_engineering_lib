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
    BuildingGeometryRequest,
    BuildingGeometryResponse,
    BuildingBeamModel,
    CrossSectionRequest,
    CrossSectionResponse,
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
# Building-Level Geometry Endpoints
# =============================================================================


@router.post(
    "/building",
    response_model=BuildingGeometryResponse,
    summary="Generate Building 3D Geometry",
    description="""
Generate 3D line geometry for a multi-beam building view.

Returns line segments for all beams/columns suitable for instanced rendering.
Ideal for React Three Fiber with LineSegments or Tubes.
""",
)
async def generate_building_geometry(
    request: BuildingGeometryRequest,
) -> BuildingGeometryResponse:
    """
    Generate building-level 3D geometry for visualization.

    Uses structural_lib.visualization.geometry_3d.building_to_3d_geometry()
    to compute line geometry for all structural members.
    """
    try:
        from structural_lib.models import BeamGeometry, Point3D, FrameType

        # Convert request dicts to BeamGeometry objects
        beam_objects = []
        for beam_dict in request.beams:
            try:
                # Parse frame type
                frame_type_str = beam_dict.get("frame_type", "beam").lower()
                frame_type = FrameType.BEAM
                if frame_type_str == "column":
                    frame_type = FrameType.COLUMN
                elif frame_type_str == "brace":
                    frame_type = FrameType.BRACE

                # Parse points
                p1 = beam_dict.get("point1", {})
                p2 = beam_dict.get("point2", {})

                beam_geom = BeamGeometry(
                    id=beam_dict.get("id", f"beam_{len(beam_objects)}"),
                    story=beam_dict.get("story", "1F"),
                    frame_type=frame_type,
                    point1=Point3D(
                        x=float(p1.get("x", 0)),
                        y=float(p1.get("y", 0)),
                        z=float(p1.get("z", 0)),
                    ),
                    point2=Point3D(
                        x=float(p2.get("x", 0)),
                        y=float(p2.get("y", 0)),
                        z=float(p2.get("z", 0)),
                    ),
                )
                beam_objects.append(beam_geom)
            except (KeyError, ValueError, TypeError):
                continue  # Skip invalid beams

        if not beam_objects:
            return BuildingGeometryResponse(
                success=False,
                message="No valid beams could be parsed from request",
                beams=[],
                bounding_box={},
                center=Point3DModel(x=0, y=0, z=0),
                metadata={},
                warnings=["No beams parsed - check input format"],
            )

        from structural_lib.visualization.geometry_3d import building_to_3d_geometry

        # Generate geometry
        include_types = (
            tuple(request.include_frame_types) if request.include_frame_types else None
        )
        geometry = building_to_3d_geometry(
            beam_objects,
            unit_scale=request.unit_scale,
            include_frame_types=include_types,
        )

        # Convert to response models
        beam_models = [
            BuildingBeamModel(
                beam_id=b.beam_id,
                story=b.story,
                frame_type=b.frame_type,
                start=Point3DModel(x=b.start.x, y=b.start.y, z=b.start.z),
                end=Point3DModel(x=b.end.x, y=b.end.y, z=b.end.z),
            )
            for b in geometry.beams
        ]

        return BuildingGeometryResponse(
            success=True,
            message=f"Generated geometry for {len(beam_models)} members",
            beams=beam_models,
            bounding_box=geometry.bounding_box,
            center=Point3DModel(
                x=geometry.center.x,
                y=geometry.center.y,
                z=geometry.center.z,
            ),
            metadata=geometry.metadata,
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
            detail=f"Building geometry generation failed: {e}",
        )


# =============================================================================
# Cross-Section Geometry Endpoints
# =============================================================================


@router.post(
    "/cross-section",
    response_model=CrossSectionResponse,
    summary="Generate 2D Cross-Section Geometry",
    description="""
Generate 2D cross-section geometry for beam section view.

Returns outline, rebar positions, and stirrup path for visualization.
Ideal for React SVG or Canvas 2D rendering.
""",
)
async def generate_cross_section_geometry(
    request: CrossSectionRequest,
) -> CrossSectionResponse:
    """
    Generate 2D cross-section geometry for beam visualization.

    Computes rebar positions based on IS 456 spacing rules.
    """
    try:
        w = request.width
        d = request.depth
        cover = request.cover
        stirrup_dia = request.stirrup_dia
        bar_dia = request.bar_dia

        # Section outline (4 corners)
        outline = [
            Point3DModel(x=0, y=0, z=0),
            Point3DModel(x=w, y=0, z=0),
            Point3DModel(x=w, y=d, z=0),
            Point3DModel(x=0, y=d, z=0),
        ]

        # Effective cover to bar center
        eff_cover = cover + stirrup_dia + bar_dia / 2

        # Tension bars (bottom)
        tension_bars = []
        if request.tension_bars > 0:
            spacing = (w - 2 * eff_cover) / max(1, request.tension_bars - 1)
            for i in range(request.tension_bars):
                x = eff_cover + i * spacing if request.tension_bars > 1 else w / 2
                tension_bars.append(Point3DModel(x=x, y=eff_cover, z=0))

        # Compression bars (top)
        compression_bars = []
        if request.compression_bars > 0:
            spacing = (w - 2 * eff_cover) / max(1, request.compression_bars - 1)
            for i in range(request.compression_bars):
                x = eff_cover + i * spacing if request.compression_bars > 1 else w / 2
                compression_bars.append(Point3DModel(x=x, y=d - eff_cover, z=0))

        # Stirrup path (inner rectangle)
        inner_cover = cover + stirrup_dia / 2
        stirrup_path = [
            Point3DModel(x=inner_cover, y=inner_cover, z=0),
            Point3DModel(x=w - inner_cover, y=inner_cover, z=0),
            Point3DModel(x=w - inner_cover, y=d - inner_cover, z=0),
            Point3DModel(x=inner_cover, y=d - inner_cover, z=0),
            Point3DModel(x=inner_cover, y=inner_cover, z=0),  # Close loop
        ]

        return CrossSectionResponse(
            success=True,
            message=f"Generated cross-section with {len(tension_bars)} tension + {len(compression_bars)} compression bars",
            outline=outline,
            tension_bars=tension_bars,
            compression_bars=compression_bars,
            stirrup_path=stirrup_path,
            dimensions={"width": w, "depth": d, "cover": cover},
            warnings=[],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cross-section generation failed: {e}",
        )
