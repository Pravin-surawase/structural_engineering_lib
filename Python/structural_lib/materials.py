"""
Module:       materials
Description:  Material properties and derived constants (fck, fy related)
"""

import math

def get_xu_max_d(fy: float) -> float:
    """
    Get Xu,max/d ratio based on steel grade (IS 456 Cl. 38.1)
    """
    if fy == 250:
        return 0.53
    elif fy == 415:
        return 0.48
    elif fy == 500:
        return 0.46
    else:
        # For other grades, use formula: 700 / (1100 + 0.87*fy)
        return 700 / (1100 + (0.87 * fy))

def get_ec(fck: float) -> float:
    """Modulus of Elasticity of Concrete (IS 456 Cl. 6.2.3.1)"""
    if fck < 0: return 0.0
    return 5000 * math.sqrt(fck)

def get_fcr(fck: float) -> float:
    """Flexural Strength of Concrete (IS 456 Cl. 6.2.2)"""
    if fck < 0: return 0.0
    return 0.7 * math.sqrt(fck)

