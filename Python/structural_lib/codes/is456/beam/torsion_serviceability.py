"""Pure selected-profile service mechanics; all lengths in mm, forces in N.

IS 456 supplies the elastic/creep/shrinkage and Annex-B stress/detail basis.
The supplementary cracked torsional stiffness is Bruun/Kuan/Bentz (2020),
Eq. 3 (Lampert), not an IS 456 formula. No torsional crack width is inferred.
"""

from __future__ import annotations

import math


def cracked_service_section(
    b_mm: float,
    D_mm: float,
    layers: tuple[tuple[float, float], ...],
    concrete_modulus_nmm2: float,
    steel_modulus_nmm2: float,
) -> tuple[float, float]:
    """Return neutral axis and fully cracked transformed inertia.

    Each layer is (depth from compression face, actual steel area). Concrete
    displaced by compression steel is removed; tension concrete is ignored.
    The lower-bound Icr is used without Annex-C tension-stiffening credit.
    """
    ratio = steel_modulus_nmm2 / concrete_modulus_nmm2
    cuts = sorted({0.0, D_mm, *(y for y, _ in layers)})
    for lower, upper in zip(cuts, cuts[1:], strict=False):
        middle = (lower + upper) / 2
        weighted = tuple(
            (y, (ratio - (1 if y < middle else 0)) * area) for y, area in layers
        )
        first = sum(area for _, area in weighted)
        second = sum(y * area for y, area in weighted)
        axis = 2 * second / (first + math.sqrt(first**2 + 2 * b_mm * second))
        if lower <= axis <= upper:
            inertia = b_mm * axis**3 / 3 + sum(
                area * (y - axis) ** 2 for y, area in weighted
            )
            return axis, inertia
    raise ValueError("No compatible cracked neutral axis within this rectangle")


def lampert_cracked_stiffness(
    steel_modulus_nmm2: float,
    corner_area_mm2: float,
    corner_perimeter_mm: float,
    longitudinal_ratio: float,
    transverse_ratio: float,
) -> float:
    """Return GKcr in N mm², Bruun et al. Eq. 3, PDF p.5/printed p.53.

    A2 is an AREA and its power is THREE. The source's p.12 worked result
    (104.1e3 kNm²) independently verifies this dimensional interpretation.
    This secant-to-yield model conservatively estimates short-term twist;
    it supplies neither sustained-torque creep nor a crack-width model.
    """
    return (
        4
        * steel_modulus_nmm2
        * corner_area_mm2**3
        / (corner_perimeter_mm**2 * (1 / longitudinal_ratio + 1 / transverse_ratio))
    )


def uniform_flexural_deflection(
    load_n_per_mm: float, span_mm: float, modulus_nmm2: float, inertia_mm4: float
) -> float:
    """Simply supported prismatic UDL displacement, consistent with Annex C."""
    return 5 * load_n_per_mm * span_mm**4 / (384 * modulus_nmm2 * inertia_mm4)


def shrinkage_upper_bound(
    tension_area_mm2: float,
    b_mm: float,
    d_mm: float,
    D_mm: float,
    span_mm: float,
    shrinkage_strain: float,
) -> float:
    """Annex C-3 single-face equivalent; ignore beneficial compression steel.

    This deliberate upper-bound model avoids extrapolating C-3 below its
    stated pt-pc >= 0.25 percent range. The actual bars remain in all other
    checks and stiffness calculations. Uniform shrinkage only.
    """
    percentage = 100 * tension_area_mm2 / (b_mm * d_mm)
    if percentage < 0.25:
        raise ValueError("Shrinkage equivalent is outside Annex C-3 range")
    factor = 0.72 if percentage < 1 else 0.65
    k4 = min(1.0, factor * math.sqrt(percentage))
    return 0.125 * k4 * shrinkage_strain / D_mm * span_mm**2


def wsm_torsion_row(
    *,
    b_mm: float,
    D_mm: float,
    d_mm: float,
    corner_b_mm: float,
    corner_d_mm: float,
    face_area_mm2: float,
    link_area_mm2: float,
    link_spacing_mm: float,
    moment_nmm: float,
    shear_n: float,
    torque_nmm: float,
) -> dict[str, float]:
    """M25/Fe415 Annex-B B5/B6 conservative stress/detail demands.

    Table21 M25 bending compression 8.5 MPa, Table22 Fe415 tension/shear
    230 MPa, Table24 M25 maximum shear 1.9 MPa. Concrete shear resistance
    and compression-steel benefit are conservatively ignored, not inferred
    from an LSM result or from Annex F.
    """
    equivalent_torsion = abs(torque_nmm) * (1 + D_mm / b_mm) / 1.7
    primary = abs(moment_nmm) + equivalent_torsion
    opposite = max(0.0, equivalent_torsion - abs(moment_nmm))
    modular_ratio = 280 / (3 * 8.5)
    weighted_area = modular_ratio * face_area_mm2
    axis = (
        2
        * weighted_area
        * d_mm
        / (
            weighted_area
            + math.sqrt(weighted_area**2 + 2 * b_mm * weighted_area * d_mm)
        )
    )
    lever = d_mm - axis / 3
    equivalent_shear = abs(shear_n) + 1.6 * abs(torque_nmm) / b_mm
    transverse_stress = (
        link_spacing_mm
        / link_area_mm2
        * (
            abs(torque_nmm) / (corner_b_mm * corner_d_mm)
            + abs(shear_n) / (2.5 * corner_d_mm)
        )
    )
    return {
        "neutral_axis_mm": axis,
        "primary_equivalent_moment_knm": primary / 1e6,
        "opposite_equivalent_moment_knm": opposite / 1e6,
        "primary_tension_stress_nmm2": primary / (face_area_mm2 * lever),
        "opposite_tension_stress_nmm2": opposite / (face_area_mm2 * lever),
        "compression_stress_nmm2": 2 * primary / (b_mm * axis * lever),
        "equivalent_shear_stress_nmm2": equivalent_shear / (b_mm * d_mm),
        "torsion_link_stress_nmm2": transverse_stress,
        "full_equivalent_shear_link_stress_nmm2": (
            equivalent_shear * link_spacing_mm / (link_area_mm2 * d_mm)
        ),
    }
