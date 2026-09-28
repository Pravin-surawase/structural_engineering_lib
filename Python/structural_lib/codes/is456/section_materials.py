"""Signed design stresses for the physical section profile (IS 456 Fig 21/23).

Compression is positive. The caller validates the finite material/strain domain.
These laws are separate from the historical rounded SP16 direct helper.
"""

from __future__ import annotations

import math

ELASTIC_MODULUS_N_PER_MM2 = 200000.0
ULTIMATE_CONCRETE_STRAIN = 0.0035


def section_steel_stress(strain: float, fy_n_per_mm2: float) -> float:
    """Fig 23A deformed steel; Fe250 uses Fig 23B's definite yield point."""
    design_strength = fy_n_per_mm2 / 1.15
    magnitude = abs(strain)
    if abs(fy_n_per_mm2 - 250) < 0.5:
        stress = min(magnitude * ELASTIC_MODULUS_N_PER_MM2, design_strength)
    else:
        previous_strain = previous_stress = 0.0
        stress = design_strength
        for fraction, plastic_strain in (
            (0.8, 0.0),
            (0.85, 0.0001),
            (0.9, 0.0003),
            (0.95, 0.0007),
            (0.975, 0.001),
            (1.0, 0.002),
        ):
            point_stress = fraction * design_strength
            point_strain = point_stress / ELASTIC_MODULUS_N_PER_MM2 + plastic_strain
            if magnitude <= point_strain:
                stress = previous_stress + (point_stress - previous_stress) * (
                    magnitude - previous_strain
                ) / (point_strain - previous_strain)
                break
            previous_strain, previous_stress = point_strain, point_stress
    return math.copysign(stress, strain)


def section_concrete_stress(strain: float, fck_n_per_mm2: float) -> float:
    """Fig 21 parabola to 0.002, then plateau; concrete tension is ignored."""
    ratio = min(1.0, max(0.0, strain / 0.002))
    return (0.67 / 1.5) * fck_n_per_mm2 * (2 * ratio - ratio**2)
