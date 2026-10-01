# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Column section equilibrium using the IS 456:2000 Fig. 21 design curve.

Compression is positive; depths are in mm, stress in N/mm2, force in N and
moment in Nmm. The steel compatibility profile is separately identified.
"""

from __future__ import annotations

from structural_lib.codes.is456.common.constants import EPSILON_C0, EPSILON_CU

CONCRETE_PEAK_FACTOR = 0.67 / 1.5  # Cl. 38.1(c); do not round to SP:16's 0.446.
COLUMN_SECTION_METHOD = "IS456_FIG21_INTEGRATED_V1__STEEL_FIG23_GS115_V1"


def extreme_compression_strain(
    neutral_axis_depth_mm: float, section_depth_mm: float
) -> float:
    """Return the extreme strain for a positive prescribed neutral-axis depth.

    With the neutral axis inside the section, the compression-face strain is
    0.0035. For full compression, plane sections and Cl. 39.1(b) together give
    ``epsilon(y) = 0.002*(1-y/xu)/(1-3*D/(7*xu))``. Thus the requested zero-strain
    axis is preserved, the strain at ``y=3*D/7`` is 0.002, and the uniform
    compression limit is 0.002. ``D`` is the projected depth for an oblique plane.

    This helper selects strain geometry only; it does not select concrete or
    steel stress laws, nominal axial design caps, or material partial factors.
    """
    if neutral_axis_depth_mm <= section_depth_mm:
        return EPSILON_CU
    return EPSILON_C0 / (1.0 - (3.0 / 7.0) * section_depth_mm / neutral_axis_depth_mm)


def concrete_stress_at_strain(strain: float, fck_nmm2: float) -> float:
    """Evaluate Fig. 21 with the literal Cl. 38.1(c) strength and partial factor.

    This is the selected ULS design law, not a physical concrete constitutive
    model. Callers enforce the applicable limiting strain plane. Tensile
    concrete carries no force; the parabola reaches its plateau at 0.002.
    """
    if strain <= 0.0:
        return 0.0
    ratio = min(strain / EPSILON_C0, 1.0)
    return CONCRETE_PEAK_FACTOR * fck_nmm2 * (2.0 * ratio - ratio * ratio)


def rectangular_concrete_resultants(
    neutral_axis_depth_mm: float, b_mm: float, D_mm: float, fck_nmm2: float
) -> tuple[float, float]:
    """Return gross concrete force N and moment Nmm about the section centroid.

    Integrating Fig. 21's parabola/plateau gives C=f0*b*xu*17/21 and a
    centroid at 99*xu/238 for xu<=D. For xu>D, plane sections and 39.1(b)
    put the plateau boundary at 3*D/7. Let q=[4*D/(7*xu-3*D)]^2; then
    C=f0*b*D*(1-4*q/21) and Mcenter=f0*b*D^2*10*q/147.

    The latter moment is evaluated directly to avoid subtracting nearly equal
    first moments at uniform compression. These expressions are exact for
    this stipulated design curve. They do not replace the separately published
    0.36/0.42 block, Cl. 39.3 nominal capacity, or Cl. 39.6 Puz formula.
    """
    peak_nmm2 = CONCRETE_PEAK_FACTOR * fck_nmm2
    if neutral_axis_depth_mm <= D_mm:
        concrete_force_n = peak_nmm2 * b_mm * neutral_axis_depth_mm * (17.0 / 21.0)
        concrete_centroid_mm = (99.0 / 238.0) * neutral_axis_depth_mm
        return concrete_force_n, concrete_force_n * (D_mm / 2.0 - concrete_centroid_mm)

    depth_ratio = D_mm / neutral_axis_depth_mm
    q = ((4.0 / 7.0) * depth_ratio / (1.0 - (3.0 / 7.0) * depth_ratio)) ** 2
    concrete_force_n = peak_nmm2 * b_mm * D_mm * (1.0 - (4.0 / 21.0) * q)
    concrete_moment_nmm = peak_nmm2 * b_mm * D_mm * D_mm * (10.0 / 147.0) * q
    return concrete_force_n, concrete_moment_nmm
