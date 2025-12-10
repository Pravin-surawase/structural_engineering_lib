"""
Module:       flexure
Description:  Flexural design and analysis functions
"""

import math
from . import materials
from .types import FlexureResult, DesignSectionType

def calculate_mu_lim(b: float, d: float, fck: float, fy: float) -> float:
    """
    Calculate Limiting Moment of Resistance (kN-m)
    """
    xu_max_d = materials.get_xu_max_d(fy)
    
    # Mu_lim = 0.36 * (xu_max/d) * (1 - 0.42 * (xu_max/d)) * b * d^2 * fck
    k = 0.36 * xu_max_d * (1 - 0.42 * xu_max_d)
    
    mu_lim_nmm = k * fck * b * d * d
    
    return mu_lim_nmm / 1000000.0 # Convert back to kN-m

def calculate_ast_required(b: float, d: float, mu_knm: float, fck: float, fy: float) -> float:
    """
    Calculate Ast Required for Singly Reinforced Section (mm^2)
    Returns -1 if section is over-reinforced (Mu > Mu_lim)
    """
    mu_nmm = abs(mu_knm) * 1000000.0
    
    mu_lim_knm = calculate_mu_lim(b, d, fck, fy)
    
    if abs(mu_knm) > mu_lim_knm:
        return -1.0
    
    # Ast = (0.5 * fck / fy) * (1 - Sqr(1 - (4.6 * Mu / (fck * b * d^2)))) * b * d
    term1 = 0.5 * fck / fy
    term2 = (4.6 * mu_nmm) / (fck * b * d * d)
    
    # Safety clamp
    if term2 > 1.0: term2 = 1.0
    
    return term1 * (1.0 - math.sqrt(1.0 - term2)) * b * d

def design_singly_reinforced(b: float, d: float, d_total: float, mu_knm: float, fck: float, fy: float) -> FlexureResult:
    """
    Main Design Function for Singly Reinforced Beam
    """
    mu_lim = calculate_mu_lim(b, d, fck, fy)
    xu_max = materials.get_xu_max_d(fy) * d
    
    # Check if Doubly Reinforced Needed
    if abs(mu_knm) > mu_lim:
        return FlexureResult(
            mu=mu_lim,
            asc_required=0.0,
            pt_provided=0.0,
            section_type=DesignSectionType.OVER_REINFORCED,
            xu=xu_max,
            xu_max=xu_max,
            is_safe=False,
            error_message="Mu exceeds Mu_lim. Doubly reinforced section required."
        )
    
    # Singly Reinforced
    ast_calc = calculate_ast_required(b, d, mu_knm, fck, fy)
    
    # Check Minimum Steel (Cl. 26.5.1.1)
    ast_min = 0.85 * b * d / fy
    
    error_msg = ""
    if ast_calc < ast_min:
        ast_final = ast_min
        error_msg = "Minimum steel provided."
    else:
        ast_final = ast_calc
        
    is_safe = True
    # Check Maximum Steel (Cl. 26.5.1.2)
    ast_max = 0.04 * b * d_total
    if ast_final > ast_max:
        is_safe = False
        error_msg = "Ast exceeds maximum limit (4% bD)."
        
    # Calculate Pt
    pt_provided = (ast_final * 100.0) / (b * d)
    
    # Calculate actual Xu
    xu = (0.87 * fy * ast_final) / (0.36 * fck * b)
    
    return FlexureResult(
        mu=mu_lim,
        asc_required=ast_final,
        pt_provided=pt_provided,
        section_type=DesignSectionType.UNDER_REINFORCED,
        xu=xu,
        xu_max=xu_max,
        is_safe=is_safe,
        error_message=error_msg
    )

