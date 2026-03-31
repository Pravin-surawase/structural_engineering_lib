"""
Column Design Router.

Endpoints for column classification, eccentricity, and axial capacity
calculations per IS 456:2000.
"""

from fastapi import APIRouter, HTTPException, status

from fastapi_app.models.column import (
    ColumnAxialRequest,
    ColumnAxialResponse,
    ColumnClassifyRequest,
    ColumnClassifyResponse,
    ColumnEccentricityRequest,
    ColumnEccentricityResponse,
)

router = APIRouter(
    prefix="/design/column",
    tags=["column"],
)


# =============================================================================
# Column Design Endpoints
# =============================================================================


@router.post(
    "/classify",
    response_model=ColumnClassifyResponse,
    summary="Classify Column (Short/Slender)",
    description=(
        "Classify a column as SHORT or SLENDER based on its slenderness ratio "
        "le/D per IS 456:2000 Cl. 25.1.2. Short columns have le/D ≤ 12."
    ),
)
async def classify_column(request: ColumnClassifyRequest) -> ColumnClassifyResponse:
    """
    Classify a column as short or slender.

    A column is **short** if le/D ≤ 12, otherwise **slender**.
    Per IS 456:2000, Cl. 25.1.2.
    """
    try:
        from structural_lib import classify_column_is456

        classification = classify_column_is456(
            le_mm=request.le_mm,
            D_mm=request.D_mm,
        )

        slenderness_ratio = request.le_mm / request.D_mm

        return ColumnClassifyResponse(
            classification=classification,
            slenderness_ratio=round(slenderness_ratio, 2),
        )

    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Column classification failed: {e}",
        )


@router.post(
    "/eccentricity",
    response_model=ColumnEccentricityResponse,
    summary="Minimum Eccentricity",
    description=(
        "Calculate the minimum eccentricity for a column per IS 456:2000 "
        "Cl. 25.4: e_min = max(l/500 + D/30, 20 mm)."
    ),
)
async def column_eccentricity(
    request: ColumnEccentricityRequest,
) -> ColumnEccentricityResponse:
    """
    Calculate minimum eccentricity per IS 456 Cl. 25.4.

    e_min = max(l_unsupported/500 + D/30, 20 mm)
    """
    try:
        from structural_lib import min_eccentricity_is456

        e_min = min_eccentricity_is456(
            l_unsupported_mm=request.l_unsupported_mm,
            D_mm=request.D_mm,
        )

        return ColumnEccentricityResponse(
            e_min_mm=round(e_min, 2),
        )

    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eccentricity calculation failed: {e}",
        )


@router.post(
    "/axial",
    response_model=ColumnAxialResponse,
    summary="Short Column Axial Capacity",
    description=(
        "Calculate the axial load capacity of a short column under pure axial "
        "load (or minimum eccentricity) per IS 456:2000 Cl. 39.6: "
        "Pu = 0.4·fck·Ac + 0.67·fy·Asc."
    ),
)
async def column_axial_capacity(
    request: ColumnAxialRequest,
) -> ColumnAxialResponse:
    """
    Calculate axial capacity for a short column per IS 456 Cl. 39.6.

    Pu = 0.4·fck·(Ag - Asc) + 0.67·fy·Asc

    Returns capacity, steel ratio, and safety warnings.
    """
    try:
        from structural_lib import design_column_axial_is456

        result = design_column_axial_is456(
            fck=request.fck,
            fy=request.fy,
            Ag_mm2=request.Ag_mm2,
            Asc_mm2=request.Asc_mm2,
        )

        Ac_mm2 = request.Ag_mm2 - request.Asc_mm2
        steel_ratio = result["steel_ratio"]
        is_safe = len(result["warnings"]) == 0

        return ColumnAxialResponse(
            Pu_kN=round(result["Pu_kN"], 2),
            fck=request.fck,
            fy=request.fy,
            Ag_mm2=request.Ag_mm2,
            Asc_mm2=request.Asc_mm2,
            Ac_mm2=round(Ac_mm2, 2),
            steel_ratio=round(steel_ratio, 4),
            is_safe=is_safe,
            warnings=result["warnings"],
        )

    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Column axial design failed: {e}",
        )
