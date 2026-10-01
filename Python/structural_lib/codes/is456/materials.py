# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       materials
Description:  Material properties and derived constants (fck, fy related)
"""

import math

from structural_lib.codes.is456._validation import (
    require_finite_real,
    require_range,
)
from structural_lib.codes.is456.section_materials import (
    section_steel_stress as _section_steel_stress,
)

STEEL_STRAIN_METHOD = "IS456_FIG23_REP_GS115_V1"


def get_xu_max_d(fy: float) -> float:
    """
    Get Xu,max/d ratio based on steel grade (IS 456 Cl. 38.1)

    The maintained direct-helper steel domain is 250-550 N/mm2.
    """
    require_range("fy", fy, minimum=250.0, maximum=550.0)
    if abs(fy - 250) < 0.5:
        return 0.53
    elif abs(fy - 415) < 0.5:
        return 0.48
    elif abs(fy - 500) < 0.5:
        return 0.46
    else:
        # For other grades, use formula: 700 / (1100 + 0.87*fy)
        return 700 / (1100 + (0.87 * fy))


def get_ec(fck: float) -> float:
    """Modulus of Elasticity of Concrete (IS 456 Cl. 6.2.3.1)

    The maintained material-helper concrete domain is 15-80 N/mm2.
    """
    require_range("fck", fck, minimum=15.0, maximum=80.0)
    return 5000 * math.sqrt(fck)


def get_fcr(fck: float) -> float:
    """Flexural Strength of Concrete (IS 456 Cl. 6.2.2)

    The maintained material-helper concrete domain is 15-80 N/mm2.
    """
    require_range("fck", fck, minimum=15.0, maximum=80.0)
    return 0.7 * math.sqrt(fck)


def get_steel_stress(strain: float, fy: float) -> float:
    """Signed stress for the representative IS 456 Fig. 23 design profile.

    Cl. 38.1(e) supplies gamma_s=1.15 and Es=200000 N/mm2. The existing
    grade convention selects Fig. 23B definite-yield steel for Fe250 and
    Fig. 23A cold-worked deformed steel otherwise, within 250-550 N/mm2.
    Six source-defined plastic-strain offsets are used, including 0.975.
    Strength is a parameter of that representative law; no nearest-grade
    SP16 table interpolation or ideal-plastic HYSD fallback is used.

    This is not a manufacturer-tested curve for every bar carrying that fy.
    Callers must establish that the selected representative family applies.
    Stress is compression-positive and odd in strain, with signed clipping
    at fy/1.15. Normative 0.87fy design-force expressions remain separate.

    Raises:
        ValueError: If inputs are not finite or fy is outside 250-550 N/mm2.
    """
    require_finite_real("strain", strain)
    require_range("fy", fy, minimum=250.0, maximum=550.0)
    return _section_steel_stress(strain, fy)
