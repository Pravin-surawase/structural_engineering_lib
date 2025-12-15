"""
Module:       tables
Description:  Data tables from IS 456:2000 (Table 19, Table 20, etc.)
"""

from . import utilities

# ------------------------------------------------------------------------------
# Table 19: Design Shear Strength of Concrete (Tc)
# ------------------------------------------------------------------------------

_PT_ROWS = [0.15, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0]

_TC_COLUMNS = {
    15: [0.28, 0.35, 0.46, 0.54, 0.6, 0.64, 0.68, 0.71, 0.71, 0.71, 0.71, 0.71, 0.71],
    20: [0.28, 0.36, 0.48, 0.56, 0.62, 0.67, 0.72, 0.75, 0.79, 0.81, 0.82, 0.82, 0.82],
    25: [0.29, 0.36, 0.49, 0.57, 0.64, 0.7, 0.74, 0.78, 0.82, 0.85, 0.88, 0.9, 0.92],
    30: [0.29, 0.37, 0.5, 0.59, 0.66, 0.71, 0.76, 0.8, 0.84, 0.88, 0.91, 0.94, 0.96],
    35: [0.29, 0.37, 0.5, 0.59, 0.67, 0.73, 0.78, 0.82, 0.86, 0.9, 0.93, 0.96, 0.99],
    40: [0.3, 0.38, 0.51, 0.6, 0.68, 0.74, 0.79, 0.84, 0.88, 0.92, 0.95, 0.98, 1.01],
}


def _get_tc_for_grade(grade: int, pt: float) -> float:
    """Helper to get Tc for a specific grade (interpolating Pt)"""
    # Determine column
    if grade in _TC_COLUMNS:
        arr_tc = _TC_COLUMNS[grade]
    else:
        # Fallback to M40 if > 40, or M15 if < 15 (though logic below handles this)
        arr_tc = _TC_COLUMNS[40]

    # Clamp Pt
    if pt < 0.15:
        pt = 0.15
    if pt > 3.0:
        pt = 3.0

    # Find interval
    for i in range(len(_PT_ROWS) - 1):
        if pt >= _PT_ROWS[i] and pt <= _PT_ROWS[i + 1]:
            return utilities.linear_interp(
                pt, _PT_ROWS[i], arr_tc[i], _PT_ROWS[i + 1], arr_tc[i + 1]
            )

    return arr_tc[-1]


def get_tc_value(fck: float, pt: float) -> float:
    """
    Get Design Shear Strength (Tc) from Table 19.
    Interpolates in pt, uses nearest lower grade column (no fck interpolation).
    """
    grades = sorted(_TC_COLUMNS.keys())

    # Select nearest lower grade (clamped to bounds).
    grade = grades[0]
    for g in grades:
        if fck >= g:
            grade = g

    return _get_tc_for_grade(grade, pt)


# ------------------------------------------------------------------------------
# Table 20: Maximum Shear Stress (Tc_max)
# ------------------------------------------------------------------------------


def get_tc_max_value(fck: float) -> float:
    """
    Get Maximum Shear Stress (Tc_max) from Table 20.
    Interpolates for Fck.
    """
    if fck >= 40:
        return 4.0
    elif fck <= 15:
        return 2.5
    else:
        # Interpolate
        if fck < 20:
            x1, y1, x2, y2 = 15, 2.5, 20, 2.8
        elif fck < 25:
            x1, y1, x2, y2 = 20, 2.8, 25, 3.1
        elif fck < 30:
            x1, y1, x2, y2 = 25, 3.1, 30, 3.5
        elif fck < 35:
            x1, y1, x2, y2 = 30, 3.5, 35, 3.7
        else:
            x1, y1, x2, y2 = 35, 3.7, 40, 4.0

        return utilities.linear_interp(fck, float(x1), y1, float(x2), y2)
