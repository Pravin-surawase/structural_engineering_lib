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


def mm_to_m(value_mm: float) -> float:
    """Convert millimeters to meters.

    Args:
        value_mm: Value in millimeters.

    Returns:
        Value in meters.

    Example:
        >>> mm_to_m(1500)
        1.5
    """
    return value_mm / 1000.0


def m_to_mm(value_m: float) -> float:
    """Convert meters to millimeters.

    Args:
        value_m: Value in meters.

    Returns:
        Value in millimeters.

    Example:
        >>> m_to_mm(1.5)
        1500.0
    """
    return value_m * 1000.0
