"""Conservative principal-plane shear and straight bond checks for COL07."""

from __future__ import annotations

from dataclasses import dataclass
from math import pi

from structural_lib.codes.is456 import tables
from structural_lib.codes.is456.beam.detailing import (
    calculate_development_length_unrounded,
)
from structural_lib.codes.is456.beam.shear import shear_reinforcement_component_kn


@dataclass(frozen=True)
class ColumnShearCheck:
    """Components of the selected ordinary shear plane."""

    width_mm: float
    d_mm: float
    pitch_mm: float
    axial_factor: float
    base_concrete_stress_nmm2: float
    vc_kn: float
    vus_kn: float
    crushing_kn: float
    capacity_kn: float
    utilization: float


def ordinary_column_shear(
    *,
    width_mm: float,
    d_mm: float,
    gross_area_mm2: float,
    pu_kn: float,
    vu_kn: float,
    fck_nmm2: float,
    hoop_diameter_mm: float,
    hoop_fy_nmm2: float,
    pitch_mm: float,
) -> ColumnShearCheck:
    """Cl. 40 using the lowest Table 19 row and two effective closed hoop legs."""
    base_stress = tables.get_tc_value(fck_nmm2, 0.15)
    axial_factor = min(1 + 3000 * pu_kn / (gross_area_mm2 * fck_nmm2), 1.5)
    area = width_mm * d_mm
    vc = base_stress * axial_factor * area / 1000
    vus = shear_reinforcement_component_kn(
        pi * hoop_diameter_mm**2 / 2, hoop_fy_nmm2, d_mm, 90, pitch_mm
    )
    crushing = tables.get_tc_max_value(fck_nmm2) * area / 1000
    capacity = min(vc + vus, crushing)
    return ColumnShearCheck(
        width_mm,
        d_mm,
        pitch_mm,
        axial_factor,
        base_stress,
        vc,
        vus,
        crushing,
        capacity,
        abs(vu_kn) / capacity,
    )


def straight_column_bond_lengths(
    diameter_mm: float, fck_nmm2: float, fy_nmm2: float
) -> tuple[float, float]:
    """Full design tension development and equal-bar compression lap minima."""
    tension = calculate_development_length_unrounded(diameter_mm, fck_nmm2, fy_nmm2)
    # Cl. 26.2.1.1 permits 25% higher bond stress in compression.
    return tension, max(tension / 1.25, 24 * diameter_mm)
