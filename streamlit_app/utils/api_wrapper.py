"""
API Wrapper
===========

Cached wrapper functions for structural_lib API calls.

This module provides:
- cached_design() - Cached beam design computation
- cached_smart_analysis() - Cached smart analysis
- clear_cache() - Manual cache clearing
- is_library_available() - Check if structural_lib is available
- get_library_status() - Get library integration status

All functions use @st.cache_data for performance:
- First call: 0.5-2s (actual computation)
- Subsequent calls: <10ms (from cache)

Author: STREAMLIT UI SPECIALIST (Agent 6)
Status: ✅ INTEGRATED (IMPL-001) - Uses actual structural_lib
Updated: 2026-01-08
"""

import math
import re
import sys
from pathlib import Path
from typing import Any

import streamlit as st

# Add Python library to path for imports
_lib_path = Path(__file__).resolve().parents[2] / "Python"
if str(_lib_path) not in sys.path:
    sys.path.insert(0, str(_lib_path))

# Try to import the actual library
_LIBRARY_AVAILABLE = False
_IMPORT_ERROR = ""
try:
    from structural_lib.api import design_beam_is456, smart_analyze_design
    from structural_lib.rebar_optimizer import optimize_bar_arrangement
    from structural_lib.detailing import calculate_bar_spacing, check_min_spacing
    from structural_lib.codes.is456.shear import select_stirrup_diameter
    from structural_lib.codes.is456.load_analysis import compute_bmd_sfd
    from structural_lib.core.data_types import LoadDefinition, LoadType

    _LIBRARY_AVAILABLE = True
except ImportError as e:
    # Library not available - will use fallback calculations
    _LIBRARY_AVAILABLE = False
    _IMPORT_ERROR = str(e)
    # Stub functions for when library is not available
    optimize_bar_arrangement = None
    calculate_bar_spacing = None
    check_min_spacing = None
    select_stirrup_diameter = None
    compute_bmd_sfd = None
    LoadDefinition = None
    LoadType = None


def _manual_bar_arrangement(
    ast_required: float, b_mm: float, cover: float
) -> tuple[dict, int]:
    """Fallback manual bar arrangement when library optimizer is not available."""
    # Exclude 32mm for narrow beams, prefer practical sizes
    bar_dia_options = [12, 16, 20, 25]
    if b_mm >= 400:
        bar_dia_options.append(32)

    best_bars = None
    for dia in bar_dia_options:
        area_per_bar = math.pi * (dia**2) / 4
        num_bars = math.ceil(ast_required / area_per_bar)
        # Enforce minimum 3 bars for redundancy
        if num_bars >= 3:
            ast_provided = num_bars * area_per_bar
            if ast_provided >= ast_required:
                best_bars = {"dia": dia, "num": num_bars, "area": ast_provided}
                break

    if not best_bars:
        # Fallback to 16mm with at least 3 bars
        area_per_bar = math.pi * (16**2) / 4
        num_bars = max(3, math.ceil(ast_required / area_per_bar))
        best_bars = {"dia": 16, "num": num_bars, "area": num_bars * area_per_bar}

    # Estimate number of layers (rough calculation)
    clear_spacing = (b_mm - 2 * cover - best_bars["num"] * best_bars["dia"]) / max(
        best_bars["num"] - 1, 1
    )
    num_layers = 1 if clear_spacing >= 25 else 2

    return best_bars, num_layers


def _flexure_result_to_dict(flexure: Any, **kwargs) -> dict:
    """Convert FlexureResult dataclass to dict for UI."""
    if isinstance(flexure, dict):
        return flexure

    b_mm = kwargs.get("b_mm", 300)
    d_mm = kwargs.get("d_mm", 450)
    D_mm = kwargs.get("D_mm", 500)
    fck_nmm2 = kwargs.get("fck_nmm2", 25)
    fy_nmm2 = kwargs.get("fy_nmm2", 500)
    cover = kwargs.get("cover", 30)

    ast_required = flexure.ast_required
    ast_min = 0.85 * b_mm * d_mm / fy_nmm2

    # Use library's optimize_bar_arrangement for IS 456 compliant bar selection
    if _LIBRARY_AVAILABLE and optimize_bar_arrangement is not None:
        try:
            # Use library optimizer with IS 456 spacing checks
            # Use min_area objective for practical bar selection (not min_bar_count)
            # Exclude 32mm for narrow beams (b < 400mm) - too large and impractical
            allowed_diameters = [12, 16, 20, 25]
            if b_mm >= 400:
                allowed_diameters.append(32)  # Only allow 32mm for wide beams

            result = optimize_bar_arrangement(
                ast_required_mm2=ast_required,
                b_mm=b_mm,
                cover_mm=cover,
                stirrup_dia_mm=8.0,  # Standard stirrup
                allowed_dia_mm=allowed_diameters,
                max_layers=2,
                objective="min_area",  # Minimize steel area (practical)
                agg_size_mm=20.0,  # Standard aggregate size
                min_total_bars=3,  # Minimum 3 bars for redundancy
                max_bars_per_layer=7,  # Maximum 7 bars per layer (practical limit)
            )

            if result.is_feasible and result.arrangement:
                arr = result.arrangement
                best_bars = {
                    "dia": arr.diameter,
                    "num": arr.count,
                    "area": arr.area_provided,
                }
                num_layers = arr.layers
                spacing_mm = arr.spacing

                # Generate alternatives for cost comparison
                # Try other diameters to give user options
                alternatives = []
                for alt_dia in [12, 16, 20, 25, 32]:
                    if alt_dia == arr.diameter:
                        continue  # Skip the selected diameter
                    try:
                        alt_result = optimize_bar_arrangement(
                            ast_required_mm2=ast_required,
                            b_mm=b_mm,
                            cover_mm=cover,
                            stirrup_dia_mm=8.0,
                            allowed_dia_mm=[alt_dia],  # Only this diameter
                            max_layers=2,
                            objective="min_area",
                            agg_size_mm=20.0,
                            min_total_bars=3,
                            max_bars_per_layer=7,
                        )
                        if alt_result.is_feasible and alt_result.arrangement:
                            alt_arr = alt_result.arrangement
                            alternatives.append(
                                {
                                    "dia": alt_arr.diameter,
                                    "num": alt_arr.count,
                                    "area": alt_arr.area_provided,
                                    "layers": alt_arr.layers,
                                    "spacing": alt_arr.spacing,
                                }
                            )
                    except Exception:
                        pass  # Skip if alternative fails

                # Store alternatives in kwargs for later use
                kwargs["_bar_alternatives"] = alternatives
            else:
                # Fallback to manual calculation
                raise ValueError("Optimizer failed: " + result.remarks)
        except Exception as e:
            # Fallback to manual calculation if optimizer fails
            st.warning(f"⚠️ Bar optimizer failed, using fallback: {str(e)[:80]}")
            best_bars, num_layers = _manual_bar_arrangement(ast_required, b_mm, cover)
            spacing_mm = 0.0
    else:
        # Library not available - use manual calculation
        best_bars, num_layers = _manual_bar_arrangement(ast_required, b_mm, cover)
        spacing_mm = 0.0

    # Check doubly reinforced
    is_doubly = (
        flexure.asc_required > 0
        if hasattr(flexure, "asc_required") and flexure.asc_required
        else False
    )

    result_dict = {
        "is_safe": flexure.is_safe,
        "ast_required": round(flexure.ast_required, 0),
        "ast_provided": round(best_bars["area"], 0),
        "mu_limit_knm": round(flexure.mu_lim, 1),
        "xu": round(flexure.xu, 1) if flexure.xu else 0,
        "xu_max": round(flexure.xu_max, 1) if flexure.xu_max else 0,
        "pt_provided": (
            round(flexure.pt_provided, 3) if hasattr(flexure, "pt_provided") else 0
        ),
        "section_type": (
            flexure.section_type.name
            if hasattr(flexure.section_type, "name")
            else str(flexure.section_type)
        ),
        "ast_min": round(ast_min, 0),
        "bar_dia": best_bars["dia"],
        "num_bars": best_bars["num"],
        "num_layers": num_layers,
        "spacing_mm": round(spacing_mm, 1),  # Actual spacing from optimizer
        "is_doubly_reinforced": is_doubly,
        "asc_required": (
            round(flexure.asc_required, 0)
            if hasattr(flexure, "asc_required") and flexure.asc_required
            else 0
        ),
        # Issue #3: Add tension_steel nested structure for cost optimizer
        "tension_steel": {
            "num": best_bars["num"],
            "dia": best_bars["dia"],
            "area": best_bars["area"],
        },
    }

    # Issue #2: Propagate bar alternatives from kwargs
    if "_bar_alternatives" in kwargs:
        result_dict["_bar_alternatives"] = kwargs["_bar_alternatives"]

    return result_dict


def _shear_result_to_dict(shear: Any, **kwargs) -> dict:
    """Convert ShearResult dataclass to dict for UI.

    Args:
        shear: ShearResult object or dict
        **kwargs: Additional parameters for stirrup selection:
            - vu_kn: Factored shear (kN)
            - b_mm: Beam width (mm)
            - d_mm: Effective depth (mm)
            - fck: Concrete strength (N/mm²)
            - main_bar_dia: Main bar diameter (mm)
    """
    if isinstance(shear, dict):
        return shear

    # Calculate appropriate stirrup diameter if function available
    stirrup_dia = 8  # Default
    if _LIBRARY_AVAILABLE and select_stirrup_diameter is not None:
        vu_kn = kwargs.get("vu_kn", 0)
        b_mm = kwargs.get("b_mm", 300)
        d_mm = kwargs.get("d_mm", 450)
        fck = kwargs.get("fck", 25)
        main_bar_dia = kwargs.get("main_bar_dia", 16)

        if vu_kn > 0 and b_mm > 0 and d_mm > 0:
            stirrup_dia = select_stirrup_diameter(
                vu_kn=vu_kn,
                b_mm=b_mm,
                d_mm=d_mm,
                fck=fck,
                main_bar_dia=main_bar_dia,
            )

    return {
        "is_safe": shear.is_safe,
        "spacing": round(shear.spacing, 0) if shear.spacing else 0,
        "tau_v": round(shear.tv, 2),
        "tau_c": round(shear.tc, 2),
        "tau_c_max": (
            round(shear.tc_max, 2) if hasattr(shear, "tc_max") and shear.tc_max else 2.5
        ),
        "vus": round(shear.vus, 1) if hasattr(shear, "vus") and shear.vus else 0,
        "stirrup_dia": stirrup_dia,
        "legs": 2,
    }


def _compliance_result_to_dict(result: Any, **kwargs) -> dict:
    """Convert ComplianceCaseResult to dict for UI consumption."""
    if isinstance(result, dict):
        return result

    b_mm = kwargs.get("b_mm", 300)
    D_mm = kwargs.get("D_mm", 500)
    d_mm = kwargs.get("d_mm", 450)
    exposure = kwargs.get("exposure", "Moderate")
    fck_nmm2 = kwargs.get("fck_nmm2", 25)
    fy_nmm2 = kwargs.get("fy_nmm2", 500)

    # Cover based on exposure
    cover_map = {
        "Mild": 20,
        "Moderate": 30,
        "Severe": 45,
        "Very Severe": 50,
        "Extreme": 75,
    }
    cover = cover_map.get(exposure, 30)

    # Get core results
    flexure_dict = _flexure_result_to_dict(
        result.flexure,
        b_mm=b_mm,
        d_mm=d_mm,
        D_mm=D_mm,
        fck_nmm2=fck_nmm2,
        fy_nmm2=fy_nmm2,
        cover=cover,
    )

    # Get main bar diameter for stirrup selection
    main_bar_dia = flexure_dict.get("bar_dia", 16)

    # Get shear force from result if available
    vu_kn = 0
    if hasattr(result, "shear") and hasattr(result.shear, "tv"):
        # Approximate Vu from tv (reverse calculation for stirrup selection)
        vu_kn = result.shear.tv * b_mm * d_mm / 1000  # kN

    shear_dict = _shear_result_to_dict(
        result.shear,
        vu_kn=vu_kn,
        b_mm=b_mm,
        d_mm=d_mm,
        fck=fck_nmm2,
        main_bar_dia=main_bar_dia,
    )

    # Side face reinforcement (IS 456 Cl. 26.5.1.3) - for D > 450mm
    needs_side_face = D_mm > 450
    side_face_area = 0.1 * b_mm * D_mm / 100 if needs_side_face else 0

    return {
        "flexure": flexure_dict,
        "shear": shear_dict,
        "detailing": {
            "needs_side_face": needs_side_face,
            "side_face_area": round(side_face_area, 0) if needs_side_face else 0,
            "cover": cover,
        },
        "cover_mm": cover,
        "is_safe": result.is_ok,
        "case_id": result.case_id if hasattr(result, "case_id") else "UI-DESIGN",
        "governing_utilization": (
            result.governing_utilization
            if hasattr(result, "governing_utilization")
            else 0
        ),
        "utilizations": result.utilizations if hasattr(result, "utilizations") else {},
        "failed_checks": (
            result.failed_checks if hasattr(result, "failed_checks") else []
        ),
        "remarks": result.remarks if hasattr(result, "remarks") else [],
        # Library metadata
        "_source": "structural_lib",
        "_library_available": True,
    }


def _fallback_design(
    mu_knm: float,
    vu_kn: float,
    b_mm: float,
    D_mm: float,
    d_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    exposure: str = "Moderate",
    **kwargs,
) -> dict:
    """Fallback calculations when library is not available.

    Uses simplified IS 456 equations for demonstration.
    """
    # IS 456 flexure calculation (simplified)
    mu_limit = 0.138 * fck_nmm2 * b_mm * (d_mm**2) / 1e6  # kNm

    # Required steel area
    if mu_knm > 0:
        lever_arm = 0.9 * d_mm
        ast_required = (mu_knm * 1e6) / (0.87 * fy_nmm2 * lever_arm)
    else:
        ast_required = 0

    # Minimum steel (IS 456 Cl. 26.5.1.1)
    ast_min = 0.85 * b_mm * d_mm / fy_nmm2
    ast_required = max(ast_required, ast_min)

    # Shear calculation
    tau_v = (vu_kn * 1000) / (b_mm * d_mm)
    tau_c = 0.56 if fck_nmm2 >= 25 else 0.48

    if tau_v > tau_c:
        vus = vu_kn * 1000 - tau_c * b_mm * d_mm
        asv = 100.6
        spacing = (0.87 * fy_nmm2 * asv * d_mm) / vus if vus > 0 else 300
        spacing = max(50, min(spacing, 0.75 * d_mm))
    else:
        spacing = min(300, 0.75 * d_mm)

    # Safety checks
    flexure_safe = mu_knm <= mu_limit * 1.1
    shear_safe = tau_v <= 0.5 * (fck_nmm2**0.5)

    # Cover
    cover_map = {
        "Mild": 20,
        "Moderate": 30,
        "Severe": 45,
        "Very Severe": 50,
        "Extreme": 75,
    }
    cover = cover_map.get(exposure, 30)

    # Bar arrangement
    bar_dia_options = [12, 16, 20, 25, 32]
    best_bars = None
    for dia in bar_dia_options:
        area_per_bar = math.pi * (dia**2) / 4
        num_bars = math.ceil(ast_required / area_per_bar)
        if num_bars >= 2:
            ast_provided = num_bars * area_per_bar
            if ast_provided >= ast_required:
                best_bars = {"dia": dia, "num": num_bars, "area": ast_provided}
                break

    if not best_bars:
        area_per_bar = math.pi * (16**2) / 4
        num_bars = max(3, math.ceil(ast_required / area_per_bar))
        best_bars = {"dia": 16, "num": num_bars, "area": num_bars * area_per_bar}

    # Doubly reinforced check
    is_doubly_reinforced = mu_knm > mu_limit
    asc_required = 0
    if is_doubly_reinforced:
        mu2 = mu_knm - mu_limit
        d_prime = cover + 8
        asc_required = (mu2 * 1e6) / (0.87 * fy_nmm2 * (d_mm - d_prime))

    # Side face reinforcement
    needs_side_face = D_mm > 450
    side_face_area = 0.1 * b_mm * D_mm / 100 if needs_side_face else 0

    # Number of layers
    clear_spacing = (b_mm - 2 * cover - best_bars["num"] * best_bars["dia"]) / max(
        best_bars["num"] - 1, 1
    )
    num_layers = 1 if clear_spacing >= 25 else 2

    # Calculate stirrup diameter based on shear demand
    stirrup_dia = 8  # Default
    if select_stirrup_diameter is not None:
        stirrup_dia = select_stirrup_diameter(
            vu_kn=vu_kn,
            b_mm=b_mm,
            d_mm=d_mm,
            fck=fck_nmm2,
            main_bar_dia=best_bars["dia"],
        )
    else:
        # Simple fallback logic if function not available
        if tau_v >= 1.5:
            stirrup_dia = 12 if b_mm >= 400 else 10
        elif tau_v >= 0.8:
            stirrup_dia = 10 if b_mm >= 400 else 8
        else:
            stirrup_dia = 8

    return {
        "flexure": {
            "is_safe": flexure_safe,
            "ast_required": round(ast_required, 0),
            "ast_provided": round(best_bars["area"], 0),
            "mu_limit_knm": round(mu_limit, 1),
            "ast_min": round(ast_min, 0),
            "bar_dia": best_bars["dia"],
            "num_bars": best_bars["num"],
            "num_layers": num_layers,
            "is_doubly_reinforced": is_doubly_reinforced,
            "asc_required": round(asc_required, 0) if is_doubly_reinforced else 0,
        },
        "shear": {
            "is_safe": shear_safe,
            "spacing": round(spacing, 0),
            "tau_v": round(tau_v, 2),
            "tau_c": round(tau_c, 2),
            "stirrup_dia": stirrup_dia,
            "legs": 2,
        },
        "detailing": {
            "needs_side_face": needs_side_face,
            "side_face_area": round(side_face_area, 0) if needs_side_face else 0,
            "cover": cover,
        },
        "cover_mm": cover,
        "is_safe": flexure_safe and shear_safe,
        "_source": "fallback",
        "_library_available": False,
    }


@st.cache_data
def cached_design(
    mu_knm: float,
    vu_kn: float,
    b_mm: float,
    D_mm: float,
    d_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    **kwargs,
) -> dict:
    """
    Cached beam design computation using structural_lib.

    Args:
        mu_knm: Factored moment (kN·m)
        vu_kn: Factored shear (kN)
        b_mm: Width (mm)
        D_mm: Total depth (mm)
        d_mm: Effective depth (mm)
        fck_nmm2: Concrete strength (N/mm²)
        fy_nmm2: Steel strength (N/mm²)
        **kwargs: Optional parameters (span_mm, exposure, etc.)

    Returns:
        Design result dict with flexure, shear, detailing

    Example:
        >>> result = cached_design(
        ...     mu_knm=120, vu_kn=80, b_mm=300, D_mm=500, d_mm=450,
        ...     fck_nmm2=25, fy_nmm2=500
        ... )
        >>> print(result['flexure']['is_safe'])
        True
    """
    exposure = kwargs.get("exposure", "Moderate")

    if _LIBRARY_AVAILABLE:
        try:
            # Call actual library function
            result = design_beam_is456(
                units="IS456",
                case_id="UI-DESIGN",
                mu_knm=mu_knm,
                vu_kn=vu_kn,
                b_mm=b_mm,
                D_mm=D_mm,
                d_mm=d_mm,
                fck_nmm2=fck_nmm2,
                fy_nmm2=fy_nmm2,
            )

            # Convert to UI-friendly dict
            return _compliance_result_to_dict(
                result,
                b_mm=b_mm,
                D_mm=D_mm,
                d_mm=d_mm,
                exposure=exposure,
                fck_nmm2=fck_nmm2,
                fy_nmm2=fy_nmm2,
            )

        except Exception as e:
            # Log error and fallback
            st.warning(f"⚠️ Library error, using fallback: {str(e)[:100]}")
            return _fallback_design(
                mu_knm=mu_knm,
                vu_kn=vu_kn,
                b_mm=b_mm,
                D_mm=D_mm,
                d_mm=d_mm,
                fck_nmm2=fck_nmm2,
                fy_nmm2=fy_nmm2,
                exposure=exposure,
            )
    else:
        # Use fallback when library not available
        return _fallback_design(
            mu_knm=mu_knm,
            vu_kn=vu_kn,
            b_mm=b_mm,
            D_mm=D_mm,
            d_mm=d_mm,
            fck_nmm2=fck_nmm2,
            fy_nmm2=fy_nmm2,
            exposure=exposure,
        )


@st.cache_data
def cached_smart_analysis(
    mu_knm: float,
    vu_kn: float,
    b_mm: float,
    D_mm: float,
    d_mm: float,
    fck_nmm2: float,
    fy_nmm2: float,
    span_mm: float,
    **kwargs,
) -> dict:
    """
    Cached smart analysis computation using structural_lib.

    Args:
        mu_knm: Factored moment (kN·m)
        vu_kn: Factored shear (kN)
        b_mm: Width (mm)
        D_mm: Total depth (mm)
        d_mm: Effective depth (mm)
        fck_nmm2: Concrete strength (N/mm²)
        fy_nmm2: Steel strength (N/mm²)
        span_mm: Span length (mm)
        **kwargs: Optional (include_cost, include_suggestions, etc.)

    Returns:
        SmartAnalysisResult as dict

    Example:
        >>> analysis = cached_smart_analysis(
        ...     mu_knm=120, vu_kn=80, b_mm=300, D_mm=500, d_mm=450,
        ...     fck_nmm2=25, fy_nmm2=500, span_mm=5000
        ... )
        >>> print(analysis['summary']['overall_score'])
        0.85
    """
    include_cost = kwargs.get("include_cost", True)
    include_suggestions = kwargs.get("include_suggestions", True)

    if _LIBRARY_AVAILABLE:
        try:
            result = smart_analyze_design(
                units="IS456",
                span_mm=span_mm,
                mu_knm=mu_knm,
                vu_kn=vu_kn,
                b_mm=b_mm,
                D_mm=D_mm,
                d_mm=d_mm,
                fck_nmm2=fck_nmm2,
                fy_nmm2=fy_nmm2,
                include_cost=include_cost,
                include_suggestions=include_suggestions,
            )

            # Normalize SmartAnalysisResult to a dict
            if hasattr(result, "to_dict"):
                analysis = result.to_dict()
            elif hasattr(result, "__dict__"):
                analysis = vars(result)
            else:
                analysis = dict(result)

            # Ensure contract: top-level "design" and "summary" keys
            design = analysis.get("design")
            if design is None:
                design = cached_design(
                    mu_knm=mu_knm,
                    vu_kn=vu_kn,
                    b_mm=b_mm,
                    D_mm=D_mm,
                    d_mm=d_mm,
                    fck_nmm2=fck_nmm2,
                    fy_nmm2=fy_nmm2,
                    span_mm=span_mm,
                )

            summary = analysis.get("summary") or {}
            if "overall_score" not in summary:
                overall_score = analysis.get("overall_score")
                if overall_score is None:
                    overall_score = 0.85 if design.get("is_safe") else 0.50
                summary = {**summary, "overall_score": overall_score}

            return {
                "design": design,
                "summary": summary,
                "analysis": analysis,
                "cost": analysis.get("cost"),
                "suggestions": analysis.get("suggestions"),
                "_source": "structural_lib",
                "_library_available": True,
            }

        except Exception as e:
            st.warning(f"⚠️ Smart analysis error, using fallback: {str(e)[:100]}")

    # Fallback - return basic design with placeholder summary
    design = cached_design(
        mu_knm=mu_knm,
        vu_kn=vu_kn,
        b_mm=b_mm,
        D_mm=D_mm,
        d_mm=d_mm,
        fck_nmm2=fck_nmm2,
        fy_nmm2=fy_nmm2,
        span_mm=span_mm,
    )

    return {
        "design": design,
        "summary": {"overall_score": 0.85 if design.get("is_safe") else 0.50},
        "cost": None,
        "suggestions": None,
        "analysis": None,
        "_source": "fallback",
        "_library_available": _LIBRARY_AVAILABLE,
    }


@st.cache_data
def cached_bmd_sfd(
    span_mm: float,
    support_condition: str,
    udl_kn_m: float = 0.0,
    point_load_kn: float = 0.0,
    point_load_position_mm: float = None,
) -> dict:
    """
    Cached BMD/SFD computation using structural_lib.

    Computes bending moment diagram and shear force diagram for a beam
    with specified loading conditions.

    Args:
        span_mm: Beam span length (mm)
        support_condition: "simply_supported" or "cantilever"
        udl_kn_m: Uniformly distributed load (kN/m). Optional.
        point_load_kn: Point load magnitude (kN). Optional.
        point_load_position_mm: Position of point load from left (mm).
                                Default: mid-span for simply supported,
                                free end for cantilever.

    Returns:
        Dict with keys:
        - positions_mm: List of positions along span
        - bmd_knm: List of bending moments
        - sfd_kn: List of shear forces
        - max_moment: Maximum bending moment (kN·m)
        - max_shear: Maximum shear force (kN)
        - critical_points: List of critical points
        - _source: "structural_lib" or "fallback"
        - _library_available: bool

    Example:
        >>> result = cached_bmd_sfd(
        ...     span_mm=6000, support_condition="simply_supported",
        ...     udl_kn_m=20.0
        ... )
        >>> print(f"Max moment: {result['max_moment']:.1f} kN·m")
        Max moment: 90.0 kN·m
    """
    if _LIBRARY_AVAILABLE and compute_bmd_sfd is not None:
        try:
            # Build load definitions
            loads = []

            if udl_kn_m > 0:
                loads.append(LoadDefinition(LoadType.UDL, magnitude=udl_kn_m))

            if point_load_kn > 0:
                # Default position: mid-span for SS, free end for cantilever
                if point_load_position_mm is None:
                    if support_condition == "simply_supported":
                        point_load_position_mm = span_mm / 2
                    else:  # cantilever
                        point_load_position_mm = span_mm

                loads.append(
                    LoadDefinition(
                        LoadType.POINT,
                        magnitude=point_load_kn,
                        position_mm=point_load_position_mm,
                    )
                )

            # If no loads specified, use minimal UDL
            if not loads:
                loads.append(LoadDefinition(LoadType.UDL, magnitude=1.0))

            # Compute BMD/SFD
            result = compute_bmd_sfd(span_mm, support_condition, loads)

            return {
                "positions_mm": result.positions_mm,
                "bmd_knm": result.bmd_knm,
                "sfd_kn": result.sfd_kn,
                "max_moment": result.max_bm_knm,
                "max_shear": result.max_sf_kn,
                "critical_points": result.critical_points,
                "_source": "structural_lib",
                "_library_available": True,
            }

        except Exception as e:
            st.warning(f"⚠️ BMD/SFD computation error: {str(e)[:100]}")

    # Fallback - simple parabolic BMD for UDL, linear SFD
    num_points = 101
    positions_mm = [span_mm * i / (num_points - 1) for i in range(num_points)]

    # Derive equivalent UDL from any available load
    w = udl_kn_m if udl_kn_m > 0 else 10.0  # Default 10 kN/m
    L = span_mm / 1000.0  # Convert to meters

    if support_condition == "simply_supported":
        # Parabolic BMD: M(x) = wx(L-x)/2
        # Linear SFD: V(x) = wL/2 - wx
        bmd_knm = [w * (x / 1000) * (L - x / 1000) / 2 for x in positions_mm]
        sfd_kn = [w * L / 2 - w * (x / 1000) for x in positions_mm]
        max_moment = w * L**2 / 8
        max_shear = w * L / 2
    else:  # cantilever
        # BMD: M(x) = -wx²/2 (max at support)
        # SFD: V(x) = w(L-x)
        bmd_knm = [-w * (x / 1000) ** 2 / 2 for x in positions_mm]
        sfd_kn = [w * (L - x / 1000) for x in positions_mm]
        max_moment = w * L**2 / 2
        max_shear = w * L

    return {
        "positions_mm": positions_mm,
        "bmd_knm": bmd_knm,
        "sfd_kn": sfd_kn,
        "max_moment": max_moment,
        "max_shear": max_shear,
        "critical_points": [],
        "_source": "fallback",
        "_library_available": _LIBRARY_AVAILABLE,
    }


def clear_cache() -> None:
    """Clear all cached computations."""
    st.cache_data.clear()


def is_library_available() -> bool:
    """Check if the structural_lib is available for import."""
    return _LIBRARY_AVAILABLE


def get_library_status() -> dict:
    """
    Get detailed status information about the library integration.

    Returns:
        Dict with keys:
        - available (bool): Whether library is available
        - version (str): Library version if available
        - library_path (str): Path to Python library
        - missing_modules (list): List of missing modules if unavailable
        - error_message (str): Error message if import failed
        - fallback_mode (bool): Whether using fallback calculations
    """
    status = {
        "available": _LIBRARY_AVAILABLE,
        "library_path": str(_lib_path),
        "fallback_mode": not _LIBRARY_AVAILABLE,
        "missing_modules": [],
        "error_message": None,
    }

    if _LIBRARY_AVAILABLE:
        try:
            from structural_lib.api import get_library_version

            status["version"] = get_library_version()
        except Exception:
            status["version"] = "unknown"
    else:
        status["error_message"] = _IMPORT_ERROR

        # Parse import error to identify missing modules
        if "No module named" in _IMPORT_ERROR:
            # Extract module name from error message
            match = re.search(r"No module named '([^']+)'", _IMPORT_ERROR)
            if match:
                status["missing_modules"].append(match.group(1))

    return status


def get_library_status_message() -> str:
    """
    Get human-readable status message about library integration.

    Returns:
        Formatted status message for display
    """
    status = get_library_status()

    if status["available"]:
        version = status.get("version", "unknown")
        return f"✅ structural_lib {version} available"
    else:
        error = status.get("error_message", "Unknown error")
        return f"⚠️ structural_lib unavailable: {error[:100]}"
