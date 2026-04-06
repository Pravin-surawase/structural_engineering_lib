# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""IS 456:2000 — Footing design modules.

Subpackage grouping all footing-specific IS 456 calculations:
- bearing: Footing sizing and bearing pressure check per Cl. 34.1
- flexure: Bending moment at column face per Cl. 34.2.3.1
- one_way_shear: One-way shear check at d from face per Cl. 34.2.4.1(a)
- punching_shear: Two-way (punching) shear check per Cl. 31.6.1

Created during Phase 3 footing design (TASK-650).
"""

from structural_lib.codes.is456.footing import (
    bearing,
    flexure,
    one_way_shear,
    punching_shear,
)
from structural_lib.codes.is456.footing.bearing import (
    bearing_stress_enhancement,
    check_bearing_pressure,
    size_footing,
)
from structural_lib.codes.is456.footing.flexure import footing_flexure
from structural_lib.codes.is456.footing.one_way_shear import footing_one_way_shear
from structural_lib.codes.is456.footing.punching_shear import footing_punching_shear

__all__ = [
    "bearing",
    "flexure",
    "one_way_shear",
    "punching_shear",
    "size_footing",
    "bearing_stress_enhancement",
    "check_bearing_pressure",
    "footing_flexure",
    "footing_one_way_shear",
    "footing_punching_shear",
]
