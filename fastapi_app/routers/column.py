"""
Column Design Router.

Endpoints for column classification, eccentricity, and axial capacity
calculations per IS 456:2000.
"""

from fastapi import APIRouter, HTTPException, status

from fastapi_app.models.column import (
    AdditionalMomentRequest,
    AdditionalMomentResponse,
    BiaxialCheckRequest,
    BiaxialCheckResponse,
    ColumnAxialRequest,
    ColumnAxialResponse,
    ColumnClassifyRequest,
    ColumnClassifyResponse,
    ColumnEccentricityRequest,
    ColumnEccentricityResponse,
    ColumnUniaxialRequest,
    ColumnUniaxialResponse,
    EffectiveLengthRequest,
    EffectiveLengthResponse,
    PMInteractionRequest,
    PMInteractionResponse,
    PMPoint,
)

router = APIRouter(
    prefix="/design/column",
    tags=["column"],
)


# =============================================================================
# Column Design Endpoints
# =============================================================================


@router.post(
    "/effective-length",
    response_model=EffectiveLengthResponse,
    summary="Effective Length per IS 456 Table 28",
    description=(
        "Calculate the effective length of a column based on end restraint "
        "conditions per IS 456:2000 Cl. 25.2, Table 28. Returns le = ratio × l "
        "for seven standard end-condition cases."
    ),
)
async def calculate_effective_length(
    request: EffectiveLengthRequest,
) -> EffectiveLengthResponse:
    """
    Calculate effective length per IS 456 Cl 25.2, Table 28.

    Computes le = ratio × l for the given end condition.
    Supports both recommended (default) and theoretical values.
    """
    try:
        from structural_lib.services.api import calculate_effective_length_is456

        result = calculate_effective_length_is456(
            l_mm=request.l_mm,
            end_condition=request.end_condition,
            use_theoretical=request.use_theoretical,
        )

        return EffectiveLengthResponse(
            le_mm=round(result["le_mm"], 2),
            ratio=round(result["ratio"], 4),
            end_condition=result["end_condition"],
            method=result["method"],
        )

    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Effective length calculation failed: {e}",
        )


@router.post(
    "/classify",
    response_model=ColumnClassifyResponse,
    summary="Classify Column (Short/Slender)",
    description=(
        "Classify a column as SHORT or SLENDER based on its slenderness ratio "
        "le/D per IS 456:2000 Cl. 25.1.2. Short columns have le/D < 12."
    ),
)
async def classify_column(request: ColumnClassifyRequest) -> ColumnClassifyResponse:
    """
    Classify a column as short or slender.

    A column is **short** if le/D < 12, otherwise **slender**.
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
        "load (or minimum eccentricity) per IS 456:2000 Cl. 39.3: "
        "Pu = 0.4·fck·Ac + 0.67·fy·Asc."
    ),
)
async def column_axial_capacity(
    request: ColumnAxialRequest,
) -> ColumnAxialResponse:
    """
    Calculate axial capacity for a short column per IS 456 Cl. 39.3.

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


@router.post(
    "/uniaxial",
    response_model=ColumnUniaxialResponse,
    summary="Short Column Uniaxial Bending Design",
    description=(
        "Design a short column for uniaxial bending per IS 456:2000 Cl. 39.5. "
        "Generates the P-M interaction envelope and checks whether the applied "
        "(Pu, Mu) lies within it."
    ),
)
async def design_column_uniaxial(
    request: ColumnUniaxialRequest,
) -> ColumnUniaxialResponse:
    """
    Design short column for uniaxial bending per IS 456 Cl. 39.5.

    Generates the P-M interaction envelope for the given section and
    determines whether the applied (Pu, Mu) lies within it. Uses radial
    intersection to find capacity.

    Returns utilization ratio, capacity point, classification, and warnings.
    """
    try:
        from structural_lib.services.api import design_short_column_uniaxial_is456

        result = design_short_column_uniaxial_is456(
            Pu_kN=request.Pu_kN,
            Mu_kNm=request.Mu_kNm,
            b_mm=request.b_mm,
            D_mm=request.D_mm,
            le_mm=request.le_mm,
            fck=request.fck,
            fy=request.fy,
            Asc_mm2=request.Asc_mm2,
            d_prime_mm=request.d_prime_mm,
            l_unsupported_mm=request.l_unsupported_mm,
        )

        return ColumnUniaxialResponse(
            ok=result["ok"],
            utilization=round(result["utilization"], 4),
            Pu_cap_kN=round(result["Pu_cap_kN"], 2),
            Mu_cap_kNm=round(result["Mu_cap_kNm"], 2),
            classification=result["classification"],
            eccentricity_mm=round(result["eccentricity_mm"], 2),
            e_min_mm=(
                round(result["e_min_mm"], 2)
                if result.get("e_min_mm") is not None
                else None
            ),
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
            detail=f"Column uniaxial design failed: {e}",
        )


@router.post(
    "/interaction-curve",
    response_model=PMInteractionResponse,
    summary="P-M Interaction Curve",
    description=(
        "Generate the P-M interaction diagram for a rectangular column "
        "section per IS 456:2000 Cl. 39.5. Returns the full curve with "
        "key points (pure axial, balanced, pure bending)."
    ),
)
async def pm_interaction_curve(
    request: PMInteractionRequest,
) -> PMInteractionResponse:
    """
    Generate P-M interaction curve per IS 456 Cl. 39.5.

    Sweeps the neutral axis depth and computes (Pu, Mu) pairs
    at each point using the IS 456 stress-block model and SP:16 Table I
    coefficients for xu > D.
    """
    try:
        from structural_lib.services.api import pm_interaction_curve_is456

        result = pm_interaction_curve_is456(
            b_mm=request.b_mm,
            D_mm=request.D_mm,
            fck=request.fck,
            fy=request.fy,
            Asc_mm2=request.Asc_mm2,
            d_prime_mm=request.d_prime_mm,
            n_points=request.n_points,
        )

        return PMInteractionResponse(
            points=[PMPoint(**pt) for pt in result["points"]],
            Pu_0_kN=round(result["Pu_0_kN"], 2),
            Mu_0_kNm=round(result["Mu_0_kNm"], 2),
            Pu_bal_kN=round(result["Pu_bal_kN"], 2),
            Mu_bal_kNm=round(result["Mu_bal_kNm"], 2),
            fck=result["fck"],
            fy=result["fy"],
            b_mm=result["b_mm"],
            D_mm=result["D_mm"],
            Asc_mm2=result["Asc_mm2"],
            d_prime_mm=result["d_prime_mm"],
            clause_ref=result.get("clause_ref", "Cl. 39.5"),
            warnings=result.get("warnings", []),
        )

    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"P-M interaction curve generation failed: {e}",
        )


@router.post(
    "/biaxial-check",
    response_model=BiaxialCheckResponse,
    summary="Biaxial Bending Check per IS 456 Cl 39.6",
    description=(
        "Check a column section under biaxial bending using the Bresler load "
        "contour method per IS 456:2000 Cl. 39.6. Returns the interaction "
        "ratio (Mux/Mux1)^αn + (Muy/Muy1)^αn and safety status."
    ),
)
async def biaxial_check(
    request: BiaxialCheckRequest,
) -> BiaxialCheckResponse:
    """
    Biaxial bending check per IS 456 Cl 39.6 (Bresler load contour).

    Computes uniaxial capacities Mux1 and Muy1 at the given Pu,
    then evaluates the Bresler interaction equation with exponent αn
    interpolated from Pu/Puz.

    Returns interaction ratio, safety status, and component capacities.
    """
    try:
        from structural_lib.services.api import biaxial_bending_check_is456
        import math

        result = biaxial_bending_check_is456(
            Pu_kN=request.Pu_kN,
            Mux_kNm=request.Mux_kNm,
            Muy_kNm=request.Muy_kNm,
            b_mm=request.b_mm,
            D_mm=request.D_mm,
            le_mm=request.le_mm,
            fck=request.fck,
            fy=request.fy,
            Asc_mm2=request.Asc_mm2,
            d_prime_mm=request.d_prime_mm,
            l_unsupported_mm=request.l_unsupported_mm,
        )

        # Cap inf to a large finite value for JSON serialization
        ratio = result["interaction_ratio"]
        if math.isinf(ratio) or math.isnan(ratio):
            ratio = 9999.0

        return BiaxialCheckResponse(
            Pu_kN=result["Pu_kN"],
            Mux_kNm=result["Mux_kNm"],
            Muy_kNm=result["Muy_kNm"],
            Mux1_kNm=round(result["Mux1_kNm"], 2),
            Muy1_kNm=round(result["Muy1_kNm"], 2),
            Puz_kN=round(result["Puz_kN"], 2),
            alpha_n=round(result["alpha_n"], 4),
            interaction_ratio=round(ratio, 4),
            is_safe=result["is_safe"],
            classification=result["classification"],
            clause_ref=result.get("clause_ref", "Cl. 39.6"),
            warnings=result.get("warnings", []),
        )

    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Biaxial bending check failed: {e}",
        )


@router.post(
    "/additional-moment",
    response_model=AdditionalMomentResponse,
    summary="Additional Moment for Slender Columns per IS 456 Cl 39.7.1",
    description=(
        "Calculate additional moment Ma = Pu × eadd for slender columns, "
        "where eadd = D × (le/D)² / 2000. Includes k-factor reduction "
        "per Cl 39.7.1.1."
    ),
)
async def additional_moment(request: AdditionalMomentRequest):
    """Calculate additional moment for slender columns."""
    try:
        from structural_lib.services.api import calculate_additional_moment_is456

        result = calculate_additional_moment_is456(
            Pu_kN=request.Pu_kN,
            b_mm=request.b_mm,
            D_mm=request.D_mm,
            lex_mm=request.lex_mm,
            ley_mm=request.ley_mm,
            fck=request.fck,
            fy=request.fy,
            Asc_mm2=request.Asc_mm2,
            d_prime_mm=request.d_prime_mm,
        )

        return AdditionalMomentResponse(**result)
    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Additional moment calculation failed: {e}",
        )
