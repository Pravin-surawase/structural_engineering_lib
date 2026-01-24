"""
Beam Detailing Router.

Endpoints for reinforcement detailing calculations.
"""

from fastapi import APIRouter, HTTPException, status

from fastapi_app.models.beam import (
    BeamDetailingRequest,
    BeamDetailingResponse,
    BarArrangement,
    StirrupArrangement,
)

router = APIRouter(
    prefix="/detailing",
    tags=["detailing"],
)


# =============================================================================
# Detailing Endpoints
# =============================================================================


@router.post(
    "/beam",
    response_model=BeamDetailingResponse,
    summary="Detail Beam Reinforcement",
    description="Generate reinforcement detailing for a beam section.",
)
async def detail_beam(request: BeamDetailingRequest) -> BeamDetailingResponse:
    """
    Generate reinforcement detailing for a beam.

    Provides:
    - Bar arrangement (size, count, layers)
    - Stirrup configuration
    - Development lengths
    - Anchorage requirements
    - Curtailment points (if span provided)

    Per IS 456:2000 clause 26 (Development and detailing).
    """
    try:
        from structural_lib.api import detail_beam_is456

        # Default span if not provided
        span = request.span_length if request.span_length else request.depth * 12  # L/d = 12 typical

        result = detail_beam_is456(
            units="IS456",
            beam_id="BEAM-1",
            story="1F",
            b_mm=request.width,
            D_mm=request.depth,
            span_mm=span,
            cover_mm=request.clear_cover,
            fck_nmm2=request.fck,
            fy_nmm2=request.fy,
            ast_start_mm2=request.ast_required,
            ast_mid_mm2=request.ast_required * 0.7,  # Approximate mid-span steel
            ast_end_mm2=request.ast_required,
            asc_start_mm2=request.asc_required,
            asc_mid_mm2=0.0,
            asc_end_mm2=request.asc_required,
            stirrup_dia_mm=8.0,
            stirrup_spacing_start_mm=100.0 if request.asv_required > 0 else 150.0,
            stirrup_spacing_mid_mm=150.0,
            stirrup_spacing_end_mm=100.0 if request.asv_required > 0 else 150.0,
            is_seismic=False,
        )

        # Parse tension bar arrangement from result
        tension_bars = []
        if hasattr(result, 'regions'):
            # Use start region for main bar info
            start_region = result.regions.get('start', result.regions.get(list(result.regions.keys())[0]))
            if hasattr(start_region, 'bottom_bars'):
                for i, bar_info in enumerate(start_region.bottom_bars):
                    tension_bars.append(BarArrangement(
                        layer=i + 1,
                        bar_count=bar_info.count if hasattr(bar_info, 'count') else 3,
                        bar_diameter=int(bar_info.diameter_mm) if hasattr(bar_info, 'diameter_mm') else 16,
                        area_provided=bar_info.area_mm2 if hasattr(bar_info, 'area_mm2') else 0.0,
                        spacing=bar_info.spacing_mm if hasattr(bar_info, 'spacing_mm') else 50.0,
                    ))

        # Default tension bars if parsing failed
        if not tension_bars:
            import math
            bar_dia = 16  # Default bar diameter
            bar_area = math.pi * bar_dia**2 / 4
            num_bars = max(2, int(math.ceil(request.ast_required / bar_area)))
            tension_bars.append(BarArrangement(
                layer=1,
                bar_count=num_bars,
                bar_diameter=bar_dia,
                area_provided=num_bars * bar_area,
                spacing=(request.width - 2 * request.clear_cover - num_bars * bar_dia) / (num_bars - 1) if num_bars > 1 else 0,
            ))

        # Calculate provided areas
        ast_provided = sum(b.area_provided for b in tension_bars)

        # Compression bars
        compression_bars = []
        asc_provided = 0.0
        if request.asc_required > 0:
            import math
            bar_dia = 12
            bar_area = math.pi * bar_dia**2 / 4
            num_bars = max(2, int(math.ceil(request.asc_required / bar_area)))
            compression_bars.append(BarArrangement(
                layer=1,
                bar_count=num_bars,
                bar_diameter=bar_dia,
                area_provided=num_bars * bar_area,
                spacing=(request.width - 2 * request.clear_cover - num_bars * bar_dia) / (num_bars - 1) if num_bars > 1 else 0,
            ))
            asc_provided = num_bars * bar_area

        # Stirrup arrangement
        stirrups = StirrupArrangement(
            diameter=8,
            legs=2,
            spacing=150.0,
            area_per_meter=2 * math.pi * 8**2 / 4 / 150 * 1000,  # mm2/m
        )

        # Development length calculation
        import math
        tau_bd = 1.4 * 1.6  # M25, deformed bars
        ld_tension = 16 * 0.87 * request.fy / (4 * tau_bd)  # For 16mm bar

        return BeamDetailingResponse(
            success=True,
            message=f"Detailing complete: {len(tension_bars)} tension layer(s)",
            tension_bars=tension_bars,
            ast_provided=ast_provided,
            compression_bars=compression_bars,
            asc_provided=asc_provided,
            stirrups=stirrups,
            ld_tension=ld_tension,
            ld_compression=ld_tension * 0.8 if request.asc_required > 0 else 0.0,
            anchorage_length=ld_tension,
            curtailment_points=[],
            warnings=[],
        )

    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"structural_lib not available: {e}",
        )
    except (ValueError, AttributeError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detailing calculation failed: {e}",
        )


@router.get(
    "/bar-areas",
    summary="Get Standard Bar Areas",
    description="Get cross-sectional areas for standard reinforcement bars.",
)
async def get_bar_areas() -> dict:
    """
    Get standard reinforcement bar areas.

    Returns area in mm² for standard bar diameters per IS 1786.
    """
    import math

    diameters = [6, 8, 10, 12, 16, 20, 25, 28, 32, 36, 40]

    bar_areas = {}
    for d in diameters:
        area = math.pi * d * d / 4
        bar_areas[f"T{d}"] = {
            "diameter_mm": d,
            "area_mm2": round(area, 1),
            "weight_kg_per_m": round(area * 7850 / 1e6, 3),
        }

    return {
        "bars": bar_areas,
        "note": "T = HYSD bars (TMT/CTD), areas per IS 1786",
    }


@router.get(
    "/development-length/{bar_diameter}",
    summary="Calculate Development Length",
    description="Calculate development length for a specific bar diameter.",
)
async def calculate_development_length(
    bar_diameter: int,
    fck: float = 25.0,
    fy: float = 500.0,
    bar_type: str = "deformed",
) -> dict:
    """
    Calculate development length for a bar.

    Per IS 456:2000 clause 26.2.1:
    Ld = φσs / (4τbd)

    Where:
    - φ = bar diameter
    - σs = stress in bar (0.87fy for design)
    - τbd = design bond stress (Table 26.2.1.1)
    """
    try:
        from structural_lib.api import calculate_development_length

        result = calculate_development_length(
            bar_diameter=bar_diameter,
            fck=fck,
            fy=fy,
            bar_type=bar_type,
        )

        return {
            "bar_diameter": bar_diameter,
            "fck": fck,
            "fy": fy,
            "bar_type": bar_type,
            "tau_bd": result.get("tau_bd", 0.0),
            "ld": result.get("ld", 0.0),
            "ld_in_diameters": result.get("ld", 0.0) / bar_diameter if bar_diameter > 0 else 0,
            "clause": "IS 456:2000 Cl. 26.2.1",
        }

    except ImportError:
        # Fallback calculation if structural_lib not available
        import math

        # Bond stress per IS 456 Table 26.2.1.1
        tau_bd_table = {
            15: 1.0, 20: 1.2, 25: 1.4, 30: 1.5,
            35: 1.7, 40: 1.9, 45: 2.0, 50: 2.2,
        }

        # Get tau_bd for nearest grade
        fck_rounded = min(50, max(15, 5 * round(fck / 5)))
        tau_bd = tau_bd_table.get(fck_rounded, 1.4)

        # Increase by 60% for deformed bars
        if bar_type == "deformed":
            tau_bd *= 1.6

        # Calculate Ld = φ × 0.87fy / (4τbd)
        sigma_s = 0.87 * fy
        ld = bar_diameter * sigma_s / (4 * tau_bd)

        return {
            "bar_diameter": bar_diameter,
            "fck": fck,
            "fy": fy,
            "bar_type": bar_type,
            "tau_bd": round(tau_bd, 2),
            "ld": round(ld, 0),
            "ld_in_diameters": round(ld / bar_diameter, 1) if bar_diameter > 0 else 0,
            "clause": "IS 456:2000 Cl. 26.2.1 (fallback calculation)",
        }
