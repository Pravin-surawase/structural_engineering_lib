"""
Column Design Router.

Endpoints for column classification, eccentricity, and axial capacity
calculations per IS 456:2000.
"""

import logging
from dataclasses import asdict

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from fastapi_app.error_utils import sanitize_float
from fastapi_app.models.response import error_response, success_response

from fastapi_app.models.column import (
    AdditionalMomentRequest,
    AdditionalMomentResponse,
    BiaxialCheckRequest,
    BiaxialCheckResponse,
    ColumnAxialRequest,
    ColumnAxialResponse,
    ColumnClassifyRequest,
    ColumnClassifyResponse,
    ColumnDesignRequest,
    ColumnDesignResponse,
    ColumnDetailingRequest,
    ColumnDetailingResponse,
    ColumnDuctileDetailingRequest,
    ColumnEccentricityRequest,
    ColumnEccentricityResponse,
    ColumnUniaxialRequest,
    ColumnUniaxialResponse,
    EffectiveLengthRequest,
    EffectiveLengthResponse,
    HelicalCheckRequest,
    HelicalCheckResponse,
    LongColumnRequest,
    LongColumnResponse,
    PMInteractionRequest,
    PMInteractionResponse,
    PMPoint,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/design/column",
    tags=["column"],
)


# =============================================================================
# Column Design Endpoints
# =============================================================================


@router.post(
    "/effective-length",
    summary="Effective Length per IS 456 Table 28",
    description=(
        "Calculate the effective length of a column based on end restraint "
        "conditions per IS 456:2000 Cl. 25.2, Table 28. Returns le = ratio × l "
        "for seven standard end-condition cases."
    ),
)
async def calculate_effective_length(
    request: EffectiveLengthRequest,
):
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

        return success_response(
            EffectiveLengthResponse(
                le_mm=round(sanitize_float(result["le_mm"]), 2),
                ratio=round(sanitize_float(result["ratio"]), 4),
                end_condition=result["end_condition"],
                method=result["method"],
            )
        )

    except (ValueError, TypeError):
        logger.exception("Invalid input for effective-length calculation")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response("Invalid input parameters"),
        )
    except (RuntimeError, KeyError, AttributeError):
        logger.exception("Column effective-length calculation failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )


@router.post(
    "/classify",
    summary="Classify Column (Short/Slender)",
    description=(
        "Classify a column as SHORT or SLENDER based on its slenderness ratio "
        "le/D per IS 456:2000 Cl. 25.1.2. Short columns have le/D < 12."
    ),
)
async def classify_column(request: ColumnClassifyRequest):
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

        return success_response(
            ColumnClassifyResponse(
                classification=classification,
                slenderness_ratio=round(slenderness_ratio, 2),
            )
        )

    except (ValueError, TypeError):
        logger.exception("Invalid input for column classification")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response("Invalid input parameters"),
        )
    except (RuntimeError, KeyError, AttributeError):
        logger.exception("Column classification failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )


@router.post(
    "/eccentricity",
    summary="Minimum Eccentricity",
    description=(
        "Calculate the minimum eccentricity for a column per IS 456:2000 "
        "Cl. 25.4: e_min = max(l/500 + D/30, 20 mm)."
    ),
)
async def column_eccentricity(
    request: ColumnEccentricityRequest,
):
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

        return success_response(
            ColumnEccentricityResponse(
                e_min_mm=round(e_min, 2),
            )
        )

    except (ValueError, TypeError):
        logger.exception("Invalid input for eccentricity calculation")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response("Invalid input parameters"),
        )
    except (RuntimeError, KeyError, AttributeError):
        logger.exception("Column eccentricity calculation failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )


@router.post(
    "/axial",
    summary="Short Column Axial Capacity",
    description=(
        "Calculate the axial load capacity of a short column under pure axial "
        "load (or minimum eccentricity) per IS 456:2000 Cl. 39.3: "
        "Pu = 0.4·fck·Ac + 0.67·fy·Asc."
    ),
)
async def column_axial_capacity(
    request: ColumnAxialRequest,
):
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

        return success_response(
            ColumnAxialResponse(
                Pu_kN=round(sanitize_float(result["Pu_kN"]), 2),
                fck=request.fck,
                fy=request.fy,
                Ag_mm2=request.Ag_mm2,
                Asc_mm2=request.Asc_mm2,
                Ac_mm2=round(sanitize_float(Ac_mm2), 2),
                steel_ratio=round(sanitize_float(steel_ratio), 4),
                is_safe=is_safe,
                warnings=result["warnings"],
            )
        )

    except (ValueError, TypeError):
        logger.exception("Invalid input for axial capacity calculation")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response("Invalid input parameters"),
        )
    except (RuntimeError, KeyError, AttributeError):
        logger.exception("Column axial capacity design failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )


@router.post(
    "/uniaxial",
    summary="Short Column Uniaxial Bending Design",
    description=(
        "Design a short column for uniaxial bending per IS 456:2000 Cl. 39.5. "
        "Generates the P-M interaction envelope and checks whether the applied "
        "(Pu, Mu) lies within it."
    ),
)
async def design_column_uniaxial(
    request: ColumnUniaxialRequest,
):
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

        return success_response(
            ColumnUniaxialResponse(
                ok=result["is_safe"],
                utilization=round(sanitize_float(result["utilization_ratio"]), 4),
                Pu_cap_kN=round(sanitize_float(result["Pu_cap_kN"]), 2),
                Mu_cap_kNm=round(sanitize_float(result["Mu_cap_kNm"]), 2),
                classification=(
                    result["classification"].name
                    if hasattr(result["classification"], "name")
                    else str(result["classification"])
                ),
                eccentricity_mm=round(sanitize_float(result["eccentricity_mm"]), 2),
                e_min_mm=(
                    round(sanitize_float(result["e_min_mm"]), 2)
                    if result.get("e_min_mm") is not None
                    else None
                ),
                warnings=list(result["warnings"]),
            )
        )

    except (ValueError, TypeError):
        logger.exception("Invalid input for uniaxial design")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response("Invalid input parameters"),
        )
    except (RuntimeError, KeyError, AttributeError):
        logger.exception("Column uniaxial design failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )


@router.post(
    "/interaction-curve",
    summary="P-M Interaction Curve",
    description=(
        "Generate the P-M interaction diagram for a rectangular column "
        "section per IS 456:2000 Cl. 39.5. Returns the full curve with "
        "key points (pure axial, balanced, pure bending)."
    ),
)
async def pm_interaction_curve(
    request: PMInteractionRequest,
):
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

        return success_response(
            PMInteractionResponse(
                points=[PMPoint(Pu_kN=pt[0], Mu_kNm=pt[1]) for pt in result["points"]],
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
        )

    except (ValueError, TypeError):
        logger.exception("Invalid input for P-M interaction curve")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response("Invalid input parameters"),
        )
    except (RuntimeError, KeyError, AttributeError):
        logger.exception("Column P-M interaction curve generation failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )


@router.post(
    "/biaxial-check",
    summary="Biaxial Bending Check per IS 456 Cl 39.6",
    description=(
        "Check a column section under biaxial bending using the Bresler load "
        "contour method per IS 456:2000 Cl. 39.6. Returns the interaction "
        "ratio (Mux/Mux1)^αn + (Muy/Muy1)^αn and safety status."
    ),
)
async def biaxial_check(
    request: BiaxialCheckRequest,
):
    """
    Biaxial bending check per IS 456 Cl 39.6 (Bresler load contour).

    Computes uniaxial capacities Mux1 and Muy1 at the given Pu,
    then evaluates the Bresler interaction equation with exponent αn
    interpolated from Pu/Puz.

    Returns interaction ratio, safety status, and component capacities.
    """
    try:
        from structural_lib.services.api import biaxial_bending_check_is456

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

        return success_response(
            BiaxialCheckResponse(
                Pu_kN=result["Pu_kN"],
                Mux_kNm=result["Mux_kNm"],
                Muy_kNm=result["Muy_kNm"],
                Mux1_kNm=round(sanitize_float(result["Mux1_kNm"]), 2),
                Muy1_kNm=round(sanitize_float(result["Muy1_kNm"]), 2),
                Puz_kN=round(sanitize_float(result["Puz_kN"]), 2),
                alpha_n=round(sanitize_float(result["alpha_n"]), 4),
                interaction_ratio=round(sanitize_float(result["interaction_ratio"]), 4),
                is_safe=result["is_safe"],
                classification=result["classification"],
                clause_ref=result.get("clause_ref", "Cl. 39.6"),
                warnings=result.get("warnings", []),
            )
        )

    except (ValueError, TypeError):
        logger.exception("Invalid input for biaxial bending check")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response("Invalid input parameters"),
        )
    except (RuntimeError, KeyError, AttributeError):
        logger.exception("Column biaxial bending check failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )


@router.post(
    "/additional-moment",
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

        return success_response(AdditionalMomentResponse(**asdict(result)))

    except (ValueError, TypeError):
        logger.exception("Invalid input for additional moment calculation")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response("Invalid input parameters"),
        )
    except (RuntimeError, KeyError, AttributeError):
        logger.exception("Column additional moment calculation failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )


@router.post(
    "/long-column",
    summary="Long (Slender) Column Design per IS 456 Cl 39.7",
    description=(
        "Design a slender column with augmented moments for P-delta effects. "
        "Classifies each axis, computes additional eccentricities, applies "
        "k-factor reduction, and checks biaxial interaction."
    ),
)
async def design_long_column(request: LongColumnRequest):
    """
    Design a long (slender) column per IS 456 Cl 39.7.

    Augments applied moments for P-delta effects, applies k-factor
    reduction, and checks biaxial interaction capacity.
    """
    try:
        from structural_lib.services.api import design_long_column_is456

        result = design_long_column_is456(
            Pu_kN=request.Pu_kN,
            M1x_kNm=request.M1x_kNm,
            M2x_kNm=request.M2x_kNm,
            M1y_kNm=request.M1y_kNm,
            M2y_kNm=request.M2y_kNm,
            b_mm=request.b_mm,
            D_mm=request.D_mm,
            lex_mm=request.lex_mm,
            ley_mm=request.ley_mm,
            fck=request.fck,
            fy=request.fy,
            Asc_mm2=request.Asc_mm2,
            d_prime_mm=request.d_prime_mm,
            braced=request.braced,
        )
        # Convert ColumnClassification enum to string
        result["classification_x"] = str(result.get("classification_x", ""))
        result["classification_y"] = str(result.get("classification_y", ""))
        return success_response(LongColumnResponse(**result))

    except (ValueError, TypeError):
        logger.exception("Invalid input for long column design")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response("Invalid input parameters"),
        )
    except (RuntimeError, KeyError, AttributeError):
        logger.exception("Column long (slender) column design failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )


@router.post(
    "/helical-check",
    summary="Helical Reinforcement Check per IS 456 Cl 39.4",
    description=(
        "Check helical reinforcement adequacy for circular columns. "
        "Verifies pitch limits and computes the 1.05 enhancement factor "
        "per IS 456 Cl 39.4."
    ),
)
async def helical_check(request: HelicalCheckRequest):
    """
    Check helical reinforcement per IS 456 Cl 39.4.

    Validates pitch limits, computes the helical ratio, and determines
    whether the 1.05× axial capacity enhancement applies.
    """
    try:
        from structural_lib.services.api import check_helical_reinforcement_is456

        result = check_helical_reinforcement_is456(
            D_mm=request.D_mm,
            D_core_mm=request.D_core_mm,
            fck=request.fck,
            fy=request.fy,
            d_helix_mm=request.d_helix_mm,
            pitch_mm=request.pitch_mm,
            Pu_axial_kN=request.Pu_axial_kN,
        )
        return success_response(HelicalCheckResponse(**result))

    except (ValueError, TypeError):
        logger.exception("Invalid input for helical reinforcement check")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response("Invalid input parameters"),
        )
    except (RuntimeError, KeyError, AttributeError):
        logger.exception("Column helical reinforcement check failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )


@router.post(
    "",
    summary="Unified Column Design per IS 456",
    description=(
        "Complete column design check — classifies the column, computes "
        "effective length, applies minimum eccentricity, checks axial and "
        "bending capacity per the appropriate IS 456 clause."
    ),
)
async def design_column(request: ColumnDesignRequest):
    """
    Unified column design per IS 456.

    Orchestrates classification, effective length, eccentricity,
    and capacity checks into a single endpoint.
    """
    try:
        from structural_lib.services.api import design_column_is456

        result = design_column_is456(
            Pu_kN=request.Pu_kN,
            Mux_kNm=request.Mux_kNm,
            Muy_kNm=request.Muy_kNm,
            b_mm=request.b_mm,
            D_mm=request.D_mm,
            l_mm=request.l_mm,
            end_condition=request.end_condition,
            fck=request.fck,
            fy=request.fy,
            Asc_mm2=request.Asc_mm2,
            d_prime_mm=request.d_prime_mm,
            l_unsupported_mm=request.l_unsupported_mm,
            braced=request.braced,
            M1x_kNm=request.M1x_kNm,
            M2x_kNm=request.M2x_kNm,
            M1y_kNm=request.M1y_kNm,
            M2y_kNm=request.M2y_kNm,
        )
        return success_response(ColumnDesignResponse(**result))

    except (ValueError, TypeError):
        logger.exception("Invalid input for unified column design")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response("Invalid input parameters"),
        )
    except (RuntimeError, KeyError, AttributeError):
        logger.exception("Column unified design failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )


@router.post(
    "/ductile-detailing",
    summary="IS 13920 Column Ductile Detailing Check",
    description=(
        "Check column ductile detailing per IS 13920:2016 Cl 7. "
        "Validates geometry, longitudinal steel limits, special confining "
        "reinforcement spacing, confinement zone length, and confining bar area."
    ),
)
async def column_ductile_detailing(request: ColumnDuctileDetailingRequest):
    """Check column ductile detailing per IS 13920:2016 Cl 7."""
    try:
        from structural_lib import check_column_ductility_is13920

        result = check_column_ductility_is13920(**request.model_dump())
        return success_response(result)

    except (ValueError, TypeError):
        logger.exception("Invalid input for ductile detailing check")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response("Invalid input parameters"),
        )
    except (RuntimeError, KeyError, AttributeError):
        logger.exception("Column ductile detailing check failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )


@router.post(
    "/detailing",
    summary="Column Detailing per IS 456 Cl 26.5.3",
    description=(
        "Check longitudinal bar limits, tie sizing, spacing, and cross-tie "
        "requirements for a column section per IS 456:2000 Cl. 26.5.3."
    ),
)
async def column_detailing(
    request: ColumnDetailingRequest,
):
    """
    Column detailing check per IS 456 Cl 26.5.3.

    Validates longitudinal bar count, diameter, spacing, steel ratio,
    tie diameter, tie spacing, and cross-tie requirements.
    """
    try:
        from structural_lib.services.api import detail_column_is456

        result = detail_column_is456(
            b_mm=request.b_mm,
            D_mm=request.D_mm,
            cover_mm=request.cover_mm,
            fck=request.fck,
            fy=request.fy,
            num_bars=request.num_bars,
            bar_dia_mm=request.bar_dia_mm,
            tie_dia_mm=request.tie_dia_mm,
            is_circular=request.is_circular,
            at_lap_section=request.at_lap_section,
        )
        return success_response(ColumnDetailingResponse(**result))

    except (ValueError, TypeError):
        logger.exception("Invalid input for column detailing check")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response("Invalid input parameters"),
        )
    except (RuntimeError, KeyError, AttributeError):
        logger.exception("Column detailing check failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("Internal calculation error"),
        )
