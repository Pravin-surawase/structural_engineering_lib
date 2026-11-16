"""Independent rectangular-section strain compatibility for DUCT01 screening.

Distances in ``layers`` are measured from the compression face.  Compression
is positive; each steel force is net of displaced concrete at its own strain.
This is a reference aid, not a product implementation or a frame analysis.
"""

from __future__ import annotations

import math
from collections.abc import Iterable

from check_library_029_beam_sections_reference import stress


def _concrete_stress(strain: float, fck_mpa: float) -> float:
    """IS 456 parabolic-rectangular design stress at a discrete bar level."""
    if strain <= 0:
        return 0.0
    ratio = min(strain / 0.002, 1.0)
    return (0.67 / 1.5) * fck_mpa * (2.0 * ratio - ratio * ratio)


def rectangular_section(
    width_mm: float,
    depth_mm: float,
    fck_mpa: float,
    fy_mpa: float,
    layers: Iterable[tuple[float, int, float]],
    axial_kn: float = 0.0,
) -> dict[str, object]:
    """Solve one rectangular section at prescribed compression-positive axial load.

    The concrete block is ``0.36 fck b x`` at ``0.42x``.  Discrete steel is
    evaluated by a linear strain plane with the concrete displaced by each bar.
    A requested equilibrium root outside ``0 < x < D`` is deliberately refused.
    """
    if min(width_mm, depth_mm, fck_mpa, fy_mpa) <= 0:
        raise ValueError("Section dimensions and material strengths must be positive.")
    bars = tuple(layers)
    if not bars or any(
        distance <= 0 or distance >= depth_mm or count <= 0 or dia <= 0
        for distance, count, dia in bars
    ):
        raise ValueError(
            "Each layer must have positive count/diameter and lie inside depth."
        )
    target_n = axial_kn * 1000.0

    def resultants(axis_mm: float) -> tuple[float, list[dict[str, float]]]:
        concrete_n = 0.36 * fck_mpa * width_mm * axis_mm
        rows: list[dict[str, float]] = []
        for index, (distance, count, diameter) in enumerate(bars, start=1):
            area = count * math.pi * diameter**2 / 4.0
            strain = 0.0035 * (1.0 - distance / axis_mm)
            steel_mpa = stress(strain, fy_mpa)
            concrete_mpa = _concrete_stress(strain, fck_mpa)
            force_n = area * (steel_mpa - concrete_mpa)
            rows.append(
                {
                    "layer": float(index),
                    "distance_from_compression_face_mm": distance,
                    "count": float(count),
                    "diameter_mm": diameter,
                    "area_mm2": area,
                    "strain": strain,
                    "steel_stress_mpa": steel_mpa,
                    "displaced_concrete_stress_mpa": concrete_mpa,
                    "force_n": force_n,
                }
            )
        return concrete_n, rows

    low = max(1e-9, depth_mm * 1e-12)
    high = depth_mm - low
    low_concrete, low_rows = resultants(low)
    high_concrete, high_rows = resultants(high)
    low_force = low_concrete + sum(row["force_n"] for row in low_rows) - target_n
    high_force = high_concrete + sum(row["force_n"] for row in high_rows) - target_n
    if low_force == 0:
        axis = low
    elif high_force == 0:
        axis = high
    elif low_force * high_force > 0:
        raise ValueError(
            "No neutral-axis equilibrium root exists within 0 < x < depth."
        )
    else:
        for _ in range(120):
            axis = (low + high) / 2.0
            concrete_n, rows = resultants(axis)
            residual = concrete_n + sum(row["force_n"] for row in rows) - target_n
            if residual < 0:
                low = axis
            else:
                high = axis
        axis = (low + high) / 2.0

    concrete_n, rows = resultants(axis)
    residual_n = concrete_n + sum(row["force_n"] for row in rows) - target_n
    if abs(residual_n) > 1e-5:
        raise AssertionError(f"Section equilibrium residual {residual_n:g} N")
    moment_nmm = concrete_n * (depth_mm / 2.0 - 0.42 * axis) + sum(
        row["force_n"] * (depth_mm / 2.0 - row["distance_from_compression_face_mm"])
        for row in rows
    )
    yield_strain = 0.002 + fy_mpa / (1.15 * 200000.0)
    tension_rows = [row for row in rows if row["strain"] < 0]
    return {
        "neutral_axis_mm": axis,
        "moment_knm": abs(moment_nmm) / 1e6,
        "axial_kn": axial_kn,
        "concrete_compression_force_n": concrete_n,
        "equilibrium_residual_n": residual_n,
        "tension_yielded": any(
            abs(row["steel_stress_mpa"]) >= fy_mpa / 1.15 - 1e-9 for row in tension_rows
        ),
        "tension_ductile": any(
            abs(row["strain"]) >= yield_strain for row in tension_rows
        ),
        "yield_strain_threshold": yield_strain,
        "layers": rows,
    }
