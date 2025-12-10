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
            mu_lim=mu_lim,
            ast_required=0.0,
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
        mu_lim=mu_lim,
        ast_required=ast_final,
        pt_provided=pt_provided,
        section_type=DesignSectionType.UNDER_REINFORCED,
        xu=xu,
        xu_max=xu_max,
        is_safe=is_safe,
        error_message=error_msg
    )

def design_doubly_reinforced(b: float, d: float, d_dash: float, d_total: float, mu_knm: float, fck: float, fy: float) -> FlexureResult:
    """
    Design a beam that can be singly or doubly reinforced.
    If Mu > Mu_lim, calculates Asc and additional Ast.
    """
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
            error_message="Invalid section geometry for doubly reinforced design (d' too large or fsc too low)."
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
    
    if ast_total > ast_max:
        is_safe = False
        error_msg = "Total Ast exceeds maximum limit (4% bD)."
        
    # Note: We should also check Asc max limit (4% bD), but usually Ast controls.
    if asc > ast_max:
        is_safe = False
        error_msg += " Asc exceeds maximum limit."
        
    # Calculate Pt
    pt_provided = (ast_total * 100.0) / (b * d)
    
    return FlexureResult(
        mu_lim=mu_lim,
        ast_required=ast_total,
        pt_provided=pt_provided,
        section_type=DesignSectionType.OVER_REINFORCED, # Technically "Doubly Reinforced" is a better name, but using existing enum
        xu=xu_max, # For doubly reinforced, we design at limiting depth
        xu_max=xu_max,
        is_safe=is_safe,
        asc_required=asc,
        error_message=error_msg
    )

