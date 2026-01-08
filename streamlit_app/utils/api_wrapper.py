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

    _LIBRARY_AVAILABLE = True
except ImportError as e:
    # Library not available - will use fallback calculations
    _LIBRARY_AVAILABLE = False
    _IMPORT_ERROR = str(e)
    # Stub functions for when library is not available
    optimize_bar_arrangement = None
    calculate_bar_spacing = None
    check_min_spacing = None


def _manual_bar_arrangement(ast_required: float, b_mm: float, cover: float) -> tuple[dict, int]:
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
                            alternatives.append({
                                "dia": alt_arr.diameter,
                                "num": alt_arr.count,
                                "area": alt_arr.area_provided,
                                "layers": alt_arr.layers,
                                "spacing": alt_arr.spacing,
                            })
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

    return {
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
    }


def _shear_result_to_dict(shear: Any) -> dict:
    """Convert ShearResult dataclass to dict for UI."""
    if isinstance(shear, dict):
        return shear

    return {
        "is_safe": shear.is_safe,
        "spacing": round(shear.spacing, 0) if shear.spacing else 0,
        "tau_v": round(shear.tv, 2),
        "tau_c": round(shear.tc, 2),
        "tau_c_max": (
            round(shear.tc_max, 2) if hasattr(shear, "tc_max") and shear.tc_max else 2.5
        ),
        "vus": round(shear.vus, 1) if hasattr(shear, "vus") and shear.vus else 0,
        "stirrup_dia": 8,
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
    shear_dict = _shear_result_to_dict(result.shear)

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
            "stirrup_dia": 8,
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


def clear_cache():
    """Clear all cached computations."""
    st.cache_data.clear()


def is_library_available() -> bool:
    """Check if the structural_lib is available for import."""
    return _LIBRARY_AVAILABLE


def get_library_status() -> dict:
    """Get status information about the library integration."""
    status = {
        "available": _LIBRARY_AVAILABLE,
        "library_path": str(_lib_path),
    }

    if _LIBRARY_AVAILABLE:
        try:
            from structural_lib.api import get_library_version

            status["version"] = get_library_version()
        except Exception:
            status["version"] = "unknown"
    else:
        status["error"] = _IMPORT_ERROR

    return status
