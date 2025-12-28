"""
Module:       flexure
Description:  Flexural design and analysis functions
"""

import math
from . import materials
from .types import FlexureResult, DesignSectionType
from .errors import (
    E_INPUT_001,
    E_INPUT_002,
    E_INPUT_003,
    E_INPUT_003a,
    E_INPUT_004,
    E_INPUT_005,
    E_INPUT_010,
    E_INPUT_012,
    E_INPUT_013,
    E_INPUT_014,
    E_INPUT_015,
    E_INPUT_016,
    E_FLEXURE_001,
    E_FLEXURE_002,
    E_FLEXURE_003,
    E_FLEXURE_004,
)


def calculate_mu_lim(b: float, d: float, fck: float, fy: float) -> float:
    """
    Calculate Limiting Moment of Resistance (kN-m)
    """
    if b <= 0 or d <= 0 or fck <= 0 or fy <= 0:
        return 0.0

    xu_max_d = materials.get_xu_max_d(fy)

    # IS 456 Cl. 38.1: Mu_lim = 0.36 * (xu_max/d) * (1 - 0.42 * (xu_max/d)) * b * d^2 * fck
    k = 0.36 * xu_max_d * (1 - 0.42 * xu_max_d)

    mu_lim_nmm = k * fck * b * d * d

    return mu_lim_nmm / 1000000.0  # Convert back to kN-m


def calculate_ast_required(
    b: float, d: float, mu_knm: float, fck: float, fy: float
) -> float:
    """
    Calculate Ast Required for Singly Reinforced Section (mm^2)
    Returns -1 if section is over-reinforced (Mu > Mu_lim)
    """
    if b <= 0 or d <= 0 or fck <= 0 or fy <= 0:
        return -1.0

    mu_nmm = abs(mu_knm) * 1000000.0

    mu_lim_knm = calculate_mu_lim(b, d, fck, fy)

    if abs(mu_knm) > mu_lim_knm:
        return -1.0

    # Ast = (0.5 * fck / fy) * (1 - Sqr(1 - (4.6 * Mu / (fck * b * d^2)))) * b * d
    term1 = 0.5 * fck / fy
    term2 = (4.6 * mu_nmm) / (fck * b * d * d)

    # Safety clamp
    if term2 > 1.0:
        term2 = 1.0

    return term1 * (1.0 - math.sqrt(1.0 - term2)) * b * d


def design_singly_reinforced(
    b: float, d: float, d_total: float, mu_knm: float, fck: float, fy: float
) -> FlexureResult:
    """
    Main Design Function for Singly Reinforced Beam
    """
    # Input validation with structured errors
    input_errors = []
    if b <= 0:
        input_errors.append(E_INPUT_001)
    if d <= 0:
        input_errors.append(E_INPUT_002)
    if d_total <= 0:
        input_errors.append(E_INPUT_003a)

    if input_errors:
        # Build specific error message based on which fields failed
        failed_fields = [e.field for e in input_errors if e.field]
        error_message = f"Invalid input: {', '.join(failed_fields)} must be > 0."
        return FlexureResult(
            mu_lim=0.0,
            ast_required=0.0,
            pt_provided=0.0,
            section_type=DesignSectionType.UNDER_REINFORCED,
            xu=0.0,
            xu_max=0.0,
            is_safe=False,
            error_message=error_message,
            errors=input_errors,
        )

    if d_total <= d:
        return FlexureResult(
            mu_lim=0.0,
            ast_required=0.0,
            pt_provided=0.0,
            section_type=DesignSectionType.UNDER_REINFORCED,
            xu=0.0,
            xu_max=0.0,
            is_safe=False,
            error_message="Invalid input: d_total must be > d.",
            errors=[E_INPUT_003],
        )

    material_errors = []
    if fck <= 0:
        material_errors.append(E_INPUT_004)
    if fy <= 0:
        material_errors.append(E_INPUT_005)

    if material_errors:
        return FlexureResult(
            mu_lim=0.0,
            ast_required=0.0,
            pt_provided=0.0,
            section_type=DesignSectionType.UNDER_REINFORCED,
            xu=0.0,
            xu_max=0.0,
            is_safe=False,
            error_message="Invalid input: fck and fy must be > 0.",
            errors=material_errors,
        )

    mu_lim = calculate_mu_lim(b, d, fck, fy)
    xu_max = materials.get_xu_max_d(fy) * d

    # Check if Doubly Reinforced Needed
    if abs(mu_knm) > mu_lim:
        return FlexureResult(
            mu_lim=mu_lim,
            ast_required=0.0,
            pt_provided=0.0,
            section_type=DesignSectionType.OVER_REINFORCED,
            xu=xu_max,
            xu_max=xu_max,
            is_safe=False,
            error_message="Mu exceeds Mu_lim. Doubly reinforced section required.",
            errors=[E_FLEXURE_001],
        )

    # Singly Reinforced
    ast_calc = calculate_ast_required(b, d, mu_knm, fck, fy)

    # Check Minimum Steel (Cl. 26.5.1.1)
    ast_min = 0.85 * b * d / fy

    error_msg = ""
    design_errors = []
    if ast_calc < ast_min:
        ast_final = ast_min
        error_msg = "Minimum steel provided."
        design_errors.append(E_FLEXURE_002)
    else:
        ast_final = ast_calc

    is_safe = True
    # Check Maximum Steel (Cl. 26.5.1.2)
    ast_max = 0.04 * b * d_total
    if ast_final > ast_max:
        is_safe = False
        error_msg = "Ast exceeds maximum limit (4% bD)."
        design_errors.append(E_FLEXURE_003)

    # Calculate Pt
    pt_provided = (ast_final * 100.0) / (b * d)

    # Calculate actual Xu
    xu = (0.87 * fy * ast_final) / (0.36 * fck * b)

    return FlexureResult(
        mu_lim=mu_lim,
        ast_required=ast_final,
        pt_provided=pt_provided,
        section_type=DesignSectionType.UNDER_REINFORCED,
        xu=xu,
        xu_max=xu_max,
        is_safe=is_safe,
        error_message=error_msg,
        errors=design_errors,
    )


def design_doubly_reinforced(
    b: float,
    d: float,
    d_dash: float,
    d_total: float,
    mu_knm: float,
    fck: float,
    fy: float,
) -> FlexureResult:
    """
    Design a beam that can be singly or doubly reinforced.
    If Mu > Mu_lim, calculates Asc and additional Ast.
    """
    input_errors = []
    if b <= 0:
        input_errors.append(E_INPUT_001)
    if d <= 0:
        input_errors.append(E_INPUT_002)
    if d_total <= 0:
        input_errors.append(E_INPUT_003a)

    if input_errors:
        failed_fields = [e.field for e in input_errors if e.field]
        error_message = f"Invalid input: {', '.join(failed_fields)} must be > 0."
        return FlexureResult(
            mu_lim=0.0,
            ast_required=0.0,
            pt_provided=0.0,
            section_type=DesignSectionType.UNDER_REINFORCED,
            xu=0.0,
            xu_max=0.0,
            is_safe=False,
            error_message=error_message,
            errors=input_errors,
        )

    if d_total <= d:
        return FlexureResult(
            mu_lim=0.0,
            ast_required=0.0,
            pt_provided=0.0,
            section_type=DesignSectionType.UNDER_REINFORCED,
            xu=0.0,
            xu_max=0.0,
            is_safe=False,
            error_message="Invalid input: d_total must be > d.",
            errors=[E_INPUT_003],
        )

    material_errors = []
    if fck <= 0:
        material_errors.append(E_INPUT_004)
    if fy <= 0:
        material_errors.append(E_INPUT_005)

    if material_errors:
        return FlexureResult(
            mu_lim=0.0,
            ast_required=0.0,
            pt_provided=0.0,
            section_type=DesignSectionType.UNDER_REINFORCED,
            xu=0.0,
            xu_max=0.0,
            is_safe=False,
            error_message="Invalid input: fck and fy must be > 0.",
            errors=material_errors,
        )

    if d_dash <= 0:
        return FlexureResult(
            mu_lim=0.0,
            ast_required=0.0,
            pt_provided=0.0,
            section_type=DesignSectionType.UNDER_REINFORCED,
            xu=0.0,
            xu_max=0.0,
            is_safe=False,
            error_message="Invalid input: d' must be > 0.",
            errors=[E_INPUT_010],
        )

    mu_lim = calculate_mu_lim(b, d, fck, fy)
    xu_max = materials.get_xu_max_d(fy) * d
    mu_abs = abs(mu_knm)

    # Case 1: Singly Reinforced (Mu <= Mu_lim)
    if mu_abs <= mu_lim:
        res = design_singly_reinforced(b, d, d_total, mu_knm, fck, fy)
        # Ensure asc_required is 0 (default in dataclass, but explicit is good)
        res.asc_required = 0.0
        return res

    # Case 2: Doubly Reinforced (Mu > Mu_lim)
    # 1. Calculate Mu2 (Excess moment)
    mu2_knm = mu_abs - mu_lim
    mu2_nmm = mu2_knm * 1000000.0

    # Basic geometry guards: compression steel must be within the effective depth
    # and within the compression zone used for strain calculations.
    if d_dash >= d or d_dash >= xu_max:
        return FlexureResult(
            mu_lim=mu_lim,
            ast_required=0.0,
            pt_provided=0.0,
            section_type=DesignSectionType.OVER_REINFORCED,
            xu=xu_max,
            xu_max=xu_max,
            is_safe=False,
            error_message="Invalid section geometry for doubly reinforced design (d' too large or fsc too low).",
            errors=[E_FLEXURE_004],
        )

    # 2. Calculate Strain in Compression Steel
    # strain_sc = 0.0035 * (1 - d'/xu_max)
    strain_sc = 0.0035 * (1.0 - d_dash / xu_max)

    # 3. Calculate Stress in Compression Steel (fsc)
    fsc = materials.get_steel_stress(strain_sc, fy)

    # 4. Calculate Stress in Concrete at level of compression steel (fcc)
    # fcc = 0.446 * fck
    fcc = 0.446 * fck

    # 5. Calculate Asc
    # Mu2 = Asc * (fsc - fcc) * (d - d')
    denom = (fsc - fcc) * (d - d_dash)
    if denom <= 0:
        return FlexureResult(
            mu_lim=mu_lim,
            ast_required=0.0,
            pt_provided=0.0,
            section_type=DesignSectionType.OVER_REINFORCED,
            xu=xu_max,
            xu_max=xu_max,
            is_safe=False,
            error_message="Invalid section geometry for doubly reinforced design (d' too large or fsc too low).",
            errors=[E_FLEXURE_004],
        )

    asc = mu2_nmm / denom

    # 6. Calculate Total Ast
    # Ast1 (for Mu_lim)
    ast1 = calculate_ast_required(b, d, mu_lim, fck, fy)

    # Ast2 (for Mu2)
    # Ast2 * 0.87 * fy = Asc * (fsc - fcc)
    ast2 = (asc * (fsc - fcc)) / (0.87 * fy)

    ast_total = ast1 + ast2

    # 7. Check Max Steel (Cl. 26.5.1.2) - 4% bD
    ast_max = 0.04 * b * d_total
    is_safe = True
    error_msg = ""
    design_errors = []

    if ast_total > ast_max:
        is_safe = False
        error_msg = "Total Ast exceeds maximum limit (4% bD)."
        design_errors.append(E_FLEXURE_003)

    # Note: We should also check Asc max limit (4% bD), but usually Ast controls.
    if asc > ast_max:
        is_safe = False
        error_msg += " Asc exceeds maximum limit."
        if not any(err.code == E_FLEXURE_003.code for err in design_errors):
            design_errors.append(E_FLEXURE_003)

    # Calculate Pt
    pt_provided = (ast_total * 100.0) / (b * d)

    return FlexureResult(
        mu_lim=mu_lim,
        ast_required=ast_total,
        pt_provided=pt_provided,
        section_type=DesignSectionType.OVER_REINFORCED,  # Technically "Doubly Reinforced" is a better name, but using existing enum
        xu=xu_max,  # For doubly reinforced, we design at limiting depth
        xu_max=xu_max,
        is_safe=is_safe,
        asc_required=asc,
        error_message=error_msg,
        errors=design_errors,
    )


def calculate_mu_lim_flanged(
    bw: float, bf: float, d: float, Df: float, fck: float, fy: float
) -> float:
    """
    Calculate Limiting Moment of Resistance for Flanged Beam (T-Beam)
    """
    xu_max = materials.get_xu_max_d(fy) * d

    # Check Df/d ratio for yf
    if (Df / d) <= 0.2:
        yf = Df
    else:
        yf = 0.15 * xu_max + 0.65 * Df
        # yf should not exceed Df
        if yf > Df:
            yf = Df

    # Web contribution (same as rectangular beam of width bw)
    # Mu_web = 0.36 * fck * bw * xu_max * (d - 0.42 * xu_max)
    mu_web_knm = calculate_mu_lim(bw, d, fck, fy)

    # Flange contribution
    # C_flange = 0.45 * fck * (bf - bw) * yf
    # M_flange = C_flange * (d - yf/2)
    c_flange = 0.45 * fck * (bf - bw) * yf
    m_flange_nmm = c_flange * (d - yf / 2.0)
    m_flange_knm = m_flange_nmm / 1000000.0

    return mu_web_knm + m_flange_knm


def design_flanged_beam(
    bw: float,
    bf: float,
    d: float,
    Df: float,
    d_total: float,
    mu_knm: float,
    fck: float,
    fy: float,
    d_dash: float = 50.0,
) -> FlexureResult:
    """
    Design a Flanged Beam (T-Beam).
    Handles:
    1. Neutral axis in flange (Rectangular design)
    2. Neutral axis in web (Singly Reinforced T-Beam)
    3. Doubly Reinforced T-Beam (if Mu > Mu_lim_T)
    """
    input_errors = []
    if bw <= 0:
        input_errors.append(E_INPUT_012)
    if bf <= 0:
        input_errors.append(E_INPUT_013)
    if d <= 0:
        input_errors.append(E_INPUT_002)
    if Df <= 0:
        input_errors.append(E_INPUT_014)
    if d_total <= 0:
        input_errors.append(E_INPUT_003a)

    if input_errors:
        failed_fields = [e.field for e in input_errors if e.field]
        error_message = f"Invalid input: {', '.join(failed_fields)} must be > 0."
        return FlexureResult(
            mu_lim=0.0,
            ast_required=0.0,
            pt_provided=0.0,
            section_type=DesignSectionType.UNDER_REINFORCED,
            xu=0.0,
            xu_max=0.0,
            is_safe=False,
            error_message=error_message,
            errors=input_errors,
        )

    if bf < bw:
        return FlexureResult(
            mu_lim=0.0,
            ast_required=0.0,
            pt_provided=0.0,
            section_type=DesignSectionType.UNDER_REINFORCED,
            xu=0.0,
            xu_max=0.0,
            is_safe=False,
            error_message="Invalid input: bf must be >= bw.",
            errors=[E_INPUT_015],
        )

    if d_total <= d:
        return FlexureResult(
            mu_lim=0.0,
            ast_required=0.0,
            pt_provided=0.0,
            section_type=DesignSectionType.UNDER_REINFORCED,
            xu=0.0,
            xu_max=0.0,
            is_safe=False,
            error_message="Invalid input: d_total must be > d.",
            errors=[E_INPUT_003],
        )

    if Df >= d:
        return FlexureResult(
            mu_lim=0.0,
            ast_required=0.0,
            pt_provided=0.0,
            section_type=DesignSectionType.UNDER_REINFORCED,
            xu=0.0,
            xu_max=0.0,
            is_safe=False,
            error_message="Invalid input: Df must be < d.",
            errors=[E_INPUT_016],
        )

    material_errors = []
    if fck <= 0:
        material_errors.append(E_INPUT_004)
    if fy <= 0:
        material_errors.append(E_INPUT_005)

    if material_errors:
        return FlexureResult(
            mu_lim=0.0,
            ast_required=0.0,
            pt_provided=0.0,
            section_type=DesignSectionType.UNDER_REINFORCED,
            xu=0.0,
            xu_max=0.0,
            is_safe=False,
            error_message="Invalid input: fck and fy must be > 0.",
            errors=material_errors,
        )

    mu_abs = abs(mu_knm)

    # 1. Check if Neutral Axis is in Flange
    # Calculate capacity assuming xu = Df
    # M_capacity_at_Df = 0.36 fck bf Df (d - 0.42 Df)
    # Note: We use bf here because if xu <= Df, the whole width bf is in compression
    mu_capacity_at_df_nmm = 0.36 * fck * bf * Df * (d - 0.42 * Df)
    mu_capacity_at_df = mu_capacity_at_df_nmm / 1000000.0

    if mu_abs <= mu_capacity_at_df:
        # Neutral axis in flange. Design as rectangular beam with width bf
        return design_singly_reinforced(bf, d, d_total, mu_knm, fck, fy)

    # 2. Neutral Axis in Web (xu > Df)
    # Check if Doubly Reinforced T-beam is needed
    mu_lim_t = calculate_mu_lim_flanged(bw, bf, d, Df, fck, fy)
    xu_max = materials.get_xu_max_d(fy) * d

    if mu_abs > mu_lim_t:
        # Doubly Reinforced T-Beam

        # Calculate Flange Contribution at Limiting Depth
        if (Df / d) <= 0.2:
            yf = Df
        else:
            yf = 0.15 * xu_max + 0.65 * Df
            if yf > Df:
                yf = Df

        c_flange = 0.45 * fck * (bf - bw) * yf
        m_flange_nmm = c_flange * (d - yf / 2.0)
        m_flange_knm = m_flange_nmm / 1000000.0

        # Remaining moment to be taken by Web (as Doubly Reinforced Rectangular)
        mu_web_target = mu_abs - m_flange_knm

        # Design Web
        web_result = design_doubly_reinforced(
            bw, d, d_dash, d_total, mu_web_target, fck, fy
        )

        # Combine results
        ast_flange = c_flange / (0.87 * fy)
        total_ast = web_result.ast_required + ast_flange

        # Recalculate Pt based on bw (standard practice for T-beams is usually bw, but sometimes bf...
        # IS 456 Cl 26.5.1.1 refers to bw for min steel. For max steel it refers to gross area?
        # Let's stick to bw for consistency with web design, or maybe provide both?
        # For now, using bw * d for percentage is safer/conservative for shear checks etc.)
        pt_provided = (total_ast * 100.0) / (bw * d)

        # Re-check max steel for the combined T-beam steel.
        # Keep consistent with rectangular design checks: 4% of bD (bw * d_total).
        ast_max = 0.04 * bw * d_total
        is_safe = web_result.is_safe
        error_msg = web_result.error_message
        design_errors = list(web_result.errors)
        if total_ast > ast_max:
            is_safe = False
            error_msg = (
                "Total Ast exceeds maximum limit (4% bw*d_total) for combined T-beam."
            )
            if not any(err.code == E_FLEXURE_003.code for err in design_errors):
                design_errors.append(E_FLEXURE_003)
        if web_result.asc_required > ast_max:
            is_safe = False
            if error_msg:
                error_msg = f"{error_msg} Asc exceeds maximum limit (4% bw*d_total)."
            else:
                error_msg = "Asc exceeds maximum limit (4% bw*d_total)."
            if not any(err.code == E_FLEXURE_003.code for err in design_errors):
                design_errors.append(E_FLEXURE_003)

        return FlexureResult(
            mu_lim=mu_lim_t,
            ast_required=total_ast,
            pt_provided=pt_provided,
            section_type=DesignSectionType.OVER_REINFORCED,
            xu=xu_max,
            xu_max=xu_max,
            is_safe=is_safe,
            asc_required=web_result.asc_required,
            error_message=error_msg,
            errors=design_errors,
        )

    # 3. Singly Reinforced T-Beam (Df < xu <= xu_max)
    # We need to find xu such that Moment(xu) = Mu

    def get_moment_t(xu_val):
        if (Df / d) <= 0.2:
            yf_val = Df
        else:
            yf_val = 0.15 * xu_val + 0.65 * Df
            if yf_val > Df:
                yf_val = Df

        # Web
        c_web = 0.36 * fck * bw * xu_val
        m_web = c_web * (d - 0.42 * xu_val)

        # Flange
        c_flange_val = 0.45 * fck * (bf - bw) * yf_val
        m_flange = c_flange_val * (d - yf_val / 2.0)

        return m_web + m_flange

    # Bisection Solver
    low = Df
    high = xu_max
    mu_target_nmm = mu_abs * 1000000.0

    xu_sol = high  # Default

    for _ in range(50):
        mid = (low + high) / 2.0
        m_mid = get_moment_t(mid)

        if abs(m_mid - mu_target_nmm) < 1000.0:  # 1 Nm tolerance
            xu_sol = mid
            break

        if m_mid < mu_target_nmm:
            low = mid
        else:
            high = mid
    else:
        xu_sol = (low + high) / 2.0

    # Calculate Ast for this xu
    # C = T => 0.36 fck bw xu + 0.45 fck (bf - bw) yf = 0.87 fy Ast
    if (Df / d) <= 0.2:
        yf_sol = Df
    else:
        yf_sol = 0.15 * xu_sol + 0.65 * Df
        if yf_sol > Df:
            yf_sol = Df

    c_total = (0.36 * fck * bw * xu_sol) + (0.45 * fck * (bf - bw) * yf_sol)
    ast_required = c_total / (0.87 * fy)

    # Check Min/Max Steel
    # Min steel: Cl 26.5.1.1 (a) for beams: As/bd = 0.85/fy. b is bw.
    ast_min = 0.85 * bw * d / fy

    error_msg = ""
    design_errors = []
    if ast_required < ast_min:
        ast_final = ast_min
        error_msg = "Minimum steel provided."
        design_errors.append(E_FLEXURE_002)
    else:
        ast_final = ast_required

    # Max steel: 4% of gross area. Gross area approx bw*D + (bf-bw)*Df?
    # Or just 4% bD? Code says "4 percent of the gross cross-sectional area".
    # We'll approximate gross area as bw * d_total + (bf - bw) * Df
    area_gross = (bw * d_total) + ((bf - bw) * Df)
    ast_max = 0.04 * area_gross

    is_safe = True
    if ast_final > ast_max:
        is_safe = False
        error_msg = "Ast exceeds maximum limit."
        if not any(err.code == E_FLEXURE_003.code for err in design_errors):
            design_errors.append(E_FLEXURE_003)

    pt_provided = (ast_final * 100.0) / (bw * d)

    return FlexureResult(
        mu_lim=mu_lim_t,
        ast_required=ast_final,
        pt_provided=pt_provided,
        section_type=DesignSectionType.UNDER_REINFORCED,  # or BALANCED if close
        xu=xu_sol,
        xu_max=xu_max,
        is_safe=is_safe,
        asc_required=0.0,
        error_message=error_msg,
        errors=design_errors,
    )
