# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""IS 456:2000 — Column design modules.

Subpackage grouping all column-specific IS 456 calculations:
- axial: Axial capacity, classification, min eccentricity per Cl. 25, 39.3
- uniaxial: Uniaxial bending capacity check per Cl. 39.5
- biaxial: Biaxial bending check (Bresler load contour) per Cl. 39.6
- slenderness: Additional moment for slender columns per Cl. 39.7.1
- long_column: Long (slender) column design per Cl. 39.7
- helical: Helical reinforcement check per Cl. 39.4
- detailing: Column detailing checks per Cl. 26.5.3

Created during Phase 2 column design (TASK-630).
"""

# Import order matters: biaxial and slenderness depend on axial and uniaxial
from structural_lib.codes.is456.column import (
    axial,  # noqa: E402
    biaxial,  # noqa: E402
    detailing,  # noqa: E402
    helical,  # noqa: E402
    long_column,  # noqa: E402
    slenderness,  # noqa: E402
    uniaxial,  # noqa: E402
)
from structural_lib.codes.is456.column.detailing import create_column_detailing
from structural_lib.codes.is456.column.helical import check_helical_reinforcement
from structural_lib.codes.is456.column.long_column import design_long_column
from structural_lib.codes.is456.column.slenderness import calculate_additional_moment

__all__ = [
    "axial",
    "biaxial",
    "calculate_additional_moment",
    "check_helical_reinforcement",
    "create_column_detailing",
    "detailing",
    "design_long_column",
    "helical",
    "long_column",
    "slenderness",
    "uniaxial",
]
