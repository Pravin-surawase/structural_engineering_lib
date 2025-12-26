"""
Module:       materials
Description:  Material properties and derived constants (fck, fy related)
"""

import math


def get_xu_max_d(fy: float) -> float:
    """
    Get Xu,max/d ratio based on steel grade (IS 456 Cl. 38.1)

    Returns 0.0 for invalid fy values (<= 0).
    """
    if fy <= 0:
        return 0.0
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
    if fck < 0:
        return 0.0
    return 5000 * math.sqrt(fck)


def get_fcr(fck: float) -> float:
    """Flexural Strength of Concrete (IS 456 Cl. 6.2.2)"""
    if fck < 0:
        return 0.0
    return 0.7 * math.sqrt(fck)


def get_steel_stress(strain: float, fy: float) -> float:
    """
    Calculate stress in steel for a given strain and yield strength.
    Uses IS 456 Figure 23 curve for HYSD bars (Fe415, Fe500).
    For Fe250, assumes elasto-plastic behavior.
    """
    es = 200000.0  # Modulus of Elasticity (N/mm^2)

    if fy == 250:
        yield_strain = 0.87 * fy / es
        if strain >= yield_strain:
            return 0.87 * fy
        else:
            return strain * es

    # For HYSD bars (Fe415, Fe500, etc.)
    # Define the inelastic curve points (Strain, Stress)
    # Note: Stress values are absolute, not ratios, for simplicity here
    # Data from SP:16 Table A

    points = []
    if fy == 415:
        points = [
            (0.00144, 288.7),
            (0.00163, 306.7),
            (0.00192, 324.8),
            (0.00241, 342.8),
            (0.00380, 360.9),
        ]
    elif fy == 500:
        points = [
            (0.00174, 347.8),
            (0.00195, 369.6),
            (0.00226, 391.3),
            (0.00277, 413.0),
            (0.00417, 434.8),
        ]
    else:
        # Fallback for other grades: assume simple elasto-plastic with 0.87fy yield
        # This is an approximation as IS 456 doesn't explicitly define curves for others
        yield_strain = 0.87 * fy / es + 0.002
        if strain >= yield_strain:
            return 0.87 * fy
        else:
            # Linear approximation up to yield
            return min(strain * es, 0.87 * fy)

    # Interpolation logic for Fe415/500

    # 1. Elastic region check (before first point)
    # The first point is roughly proportional limit (0.8 * 0.87fy)
    if strain < points[0][0]:
        return strain * es

    # 2. Inelastic region interpolation
    for i in range(len(points) - 1):
        s1, f1 = points[i]
        s2, f2 = points[i + 1]

        if s1 <= strain <= s2:
            # Linear interpolation
            return f1 + (f2 - f1) * (strain - s1) / (s2 - s1)

    # 3. Yield plateau (strain > last point)
    return points[-1][1]
