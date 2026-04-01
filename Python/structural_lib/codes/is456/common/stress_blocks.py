"""IS 456 rectangular stress-block force and moment helpers.

Pure functions --- no I/O, no side effects. All units in N and mm.
Uses named constants from :mod:`.constants` (never magic numbers).

References:
    IS 456:2000 Cl. 38.1, Annex G (G-2.2)
    SP:16:1980 Charts 1--26
"""

from __future__ import annotations

from structural_lib.codes.is456.common.constants import (
    ES_STEEL_MPA,
    FLANGE_STRESS_FACTOR,
    STRESS_BLOCK_DEPTH,
    STRESS_BLOCK_FACTOR,
    STRESS_RATIO,
)


def concrete_compressive_force(fck: float, b: float, xu: float) -> float:
    """Resultant compressive force in the concrete stress block.

    Cu = 0.36 * fck * b * xu  (IS 456 Cl. 38.1)

    Args:
        fck: Characteristic compressive strength of concrete (N/mm2).
        b: Width of the compression face (mm).
        xu: Depth of the neutral axis from the extreme compression fibre (mm).

    Returns:
        Compressive force (N).
    """
    return STRESS_BLOCK_FACTOR * fck * b * xu


def concrete_moment_capacity(
    fck: float,
    b: float,
    xu: float,
    d: float,
) -> float:
    """Moment of resistance of the concrete stress block about the tension steel.

    Mu = 0.36 * fck * b * xu * (d - 0.42 * xu)  (IS 456 Cl. 38.1)

    Args:
        fck: Characteristic compressive strength of concrete (N/mm2).
        b: Width of the compression face (mm).
        xu: Depth of the neutral axis (mm).
        d: Effective depth to the tension steel centroid (mm).

    Returns:
        Moment capacity (N*mm).
    """
    return STRESS_BLOCK_FACTOR * fck * b * xu * (d - STRESS_BLOCK_DEPTH * xu)


def flange_compressive_force(
    fck: float,
    bf: float,
    bw: float,
    yf: float,
) -> float:
    """Compressive force in the flange overhang of a T- or L-beam.

    Cf = 0.45 * fck * (bf - bw) * yf  (IS 456 Annex G, G-2.2)

    Args:
        fck: Characteristic compressive strength of concrete (N/mm2).
        bf: Effective flange width (mm).
        bw: Web width (mm).
        yf: Effective depth of flange stress block (mm).

    Returns:
        Flange compressive force (N).
    """
    return FLANGE_STRESS_FACTOR * fck * (bf - bw) * yf


def steel_stress_from_strain(strain: float, fy: float) -> float:
    """Compute design steel stress from strain per IS 456 Fig. 23.

    Uses a bilinear stress-strain model for cold-worked deformed bars
    (Fe 415 / Fe 500). The design yield stress is ``0.87 * fy`` (i.e.
    ``fy / gamma_s`` with ``gamma_s = 1.15`` already applied).

    The bilinear model:
    - Elastic region: ``f_s = E_s × |strain|`` for ``|strain| <= 0.87*fy / E_s``
    - Yield plateau:  ``f_s = 0.87 * fy``      for ``|strain| > 0.87*fy / E_s``

    Returns stress with the same sign as the input strain (positive for
    compression, negative for tension).

    Args:
        strain: Steel strain (dimensionless). Positive = compression.
        fy: Characteristic yield strength of steel (N/mm²).

    Returns:
        Design steel stress (N/mm²), with sign matching input strain.

    References:
        IS 456:2000 Fig. 23
        SP:16:1980 Table F
    """
    # IS 456 Fig. 23: design yield stress = 0.87 * fy
    f_yd = STRESS_RATIO * fy

    # IS 456 Fig. 23: yield strain = f_yd / E_s
    eps_yd = f_yd / ES_STEEL_MPA

    abs_strain = abs(strain)

    # IS 456 Fig. 23: bilinear — elastic up to yield, then constant
    if abs_strain <= eps_yd:
        stress_mag = ES_STEEL_MPA * abs_strain
    else:
        stress_mag = f_yd

    # Return with sign matching input strain
    if strain < 0.0:
        return -stress_mag
    return stress_mag
