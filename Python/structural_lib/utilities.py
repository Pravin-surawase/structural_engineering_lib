"""
Module:       utilities
Description:  Helper functions (Interpolation, Rounding, Validation)
"""

def linear_interp(x: float, x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Linear Interpolation: y = y1 + (x - x1) * (y2 - y1) / (x2 - x1)
    """
    if (x2 - x1) == 0:
        return y1
    return y1 + (x - x1) * (y2 - y1) / (x2 - x1)

def round_to(value: float, digits: int) -> float:
    """
    Standard rounding function
    """
    return round(value, digits)
