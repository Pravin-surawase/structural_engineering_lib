"""Independent stdlib-only Packet E arithmetic; never import structural_lib.

The normalized IS constitutive laws/data are shared source lineage. This
replay independently solves force equilibrium and integrates the piecewise
T compression area; it is not an independent choice of engineering model.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


def steel_stress(strain: float) -> float:
    strength = 415 / 1.15
    points = [(0.0, 0.0)] + [
        (ratio * strength / 200000 + plastic, ratio * strength)
        for ratio, plastic in (
            (0.8, 0), (0.85, 0.0001), (0.9, 0.0003),
            (0.95, 0.0007), (0.975, 0.001), (1, 0.002),
        )
    ]
    value = strength
    for (e0, s0), (e1, s1) in zip(points, points[1:]):
        if abs(strain) <= e1:
            value = s0 + (s1 - s0) * (abs(strain) - e0) / (e1 - e0)
            break
    return math.copysign(value, strain)


def derive(physical_width: float) -> dict[str, float]:
    bw, depth, flange, span, d = 300.0, 550.0, 150.0, 6000.0, 500.0
    effective = min(physical_width, span / 6 + bw + 6 * flange)
    area = physical_width * flange + bw * (depth - flange)
    bottom, top = 4 * math.pi * 20**2 / 4, 2 * math.pi * 16**2 / 4
    layers = ((50.0, top), (500.0, bottom))
    permanent = area * 25 / 1e6 + 2
    total, ultimate = permanent + 3, 1.5 * (permanent + 3)

    def integrals(x: float) -> tuple[float, float]:
        # Exact integrals of b(y)*(x-y) and b(y)*(x-y)^2 from 0 to x.
        first = effective * (x * min(x, flange) - min(x, flange)**2 / 2)
        second = effective * (x**3 - max(0, x - flange)**3) / 3
        if x > flange:
            first += bw * (x - flange)**2 / 2
            second += bw * (x - flange)**3 / 3
        return first, second

    lower, upper = 0.0, depth
    for _ in range(180):
        x = (lower + upper) / 2
        force = integrals(x)[0] + sum(
            (8 - int(y < x)) * a * (x - y) for y, a in layers
        )
        if force > 0:
            upper = x
        else:
            lower = x
    axis = (lower + upper) / 2
    inertia = integrals(axis)[1] + sum(
        (8 - int(y < axis)) * a * (y - axis)**2 for y, a in layers
    )
    curvature = total * span**2 / 8 / (25000 * inertia)
    strain, stress = curvature * (depth - axis), 200000 * curvature * (d - axis)
    surface_points = (0, 250 / 3, 150, 650 / 3, 300)
    bars_x = (50, 350 / 3, 550 / 3, 250)
    cracks = []
    for surface in surface_points:
        acr = min(math.hypot(surface - x, 50) - 10 for x in bars_x)
        cracks.append(3 * acr * strain / (1 + 2 * (acr - 40) / (depth - axis)))

    def net_steel(x: float) -> tuple[tuple[float, float], ...]:
        result = []
        for y, a in layers:
            e = 0.0035 * (1 - y / x)
            r = min(1.0, max(0.0, e / 0.002))
            displaced = (0.67 / 1.5) * 25 * (2 * r - r*r)
            result.append((y, a * (steel_stress(e) - displaced)))
        return tuple(result)

    lower, upper = 1e-8, flange
    for _ in range(180):
        x = (lower + upper) / 2
        # Both selected cases are independently checked within-flange states.
        residual = 0.36 * 25 * effective * x + sum(f for _, f in net_steel(x))
        if residual > 0:
            upper = x
        else:
            lower = x
    xu = (lower + upper) / 2
    capacity = (
        0.36 * 25 * effective * xu * (d - 0.42 * xu)
        + sum(f * (d - y) for y, f in net_steel(xu))
    ) / 1e6
    pt_web = 100 * bottom / (bw * d)
    tau = 0.57 + (pt_web - 0.75) / 0.25 * (0.64 - 0.57)
    links_area = 2 * math.pi * 8**2 / 4
    shear = (tau * bw * d + 0.87 * 415 * links_area * d / 150) / 1000
    link_length = (
        2 * 100 + 2 * 492 + 242 + math.hypot(242, 10)
        - 10 * 20 + 5 * math.pi / 2 * 20
    )
    steel_mass = (6900 * (bottom + top) + 40 * math.pi * 8**2 / 4 * link_length) * 7850 / 1e9
    return {
        "physical_width_mm": physical_width,
        "effective_width_mm": effective,
        "physical_area_mm2": area,
        "self_weight_n_per_mm": area * 25 / 1e6,
        "permanent_load_n_per_mm": permanent,
        "service_load_n_per_mm": total,
        "ultimate_load_n_per_mm": ultimate,
        "service_moment_knm": total * span**2 / 8 / 1e6,
        "ultimate_moment_knm": ultimate * span**2 / 8 / 1e6,
        "ultimate_shear_kn": ultimate * span / 2 / 1000,
        "service_neutral_axis_mm": axis,
        "cracked_inertia_mm4": inertia,
        "service_bottom_steel_stress_nmm2": stress,
        "elastic_bottom_surface_strain": strain,
        "maximum_crack_width_mm": max(cracks),
        "ultimate_neutral_axis_mm": xu,
        "flexural_capacity_knm": capacity,
        "tension_area_mm2": bottom,
        "compression_face_area_mm2": top,
        "tension_percentage_effective_flange": 100 * bottom / (effective * d),
        "compression_percentage_effective_flange": 100 * top / (effective * d),
        "table19_tau_c_nmm2": tau,
        "provided_shear_capacity_kn": shear,
        "development_20_mm": 20 * (0.87 * 415) / (4 * 1.4 * 1.6),
        "development_16_mm": 16 * (0.87 * 415) / (4 * 1.4 * 1.6),
        "link_path_length_mm": link_length,
        "beam_scheduled_steel_mass_kg": steel_mass,
        "owned_concrete_volume_m3": area * 7000 / 1e9,
        "exposed_formwork_area_m2": (300 + 2 * 400 + physical_width - 300) * 5000 / 1e6,
        "actual_span_depth_ratio": 5500 / d,
        "conservative_allowable_span_depth_ratio": 20 * 1 * 1 * 0.8,
    }


def main() -> None:
    reference = json.loads(Path(__file__).with_name("library-027-t-beam-member.json").read_text(encoding="utf-8"))
    for name, width in (("main", 1000), ("width_limited", 2500)):
        actual = derive(width)
        for key, value in actual.items():
            assert math.isclose(value, reference["cases"][name]["expected"][key], rel_tol=1e-11, abs_tol=1e-8), (name, key, value)
    print("PASS independent Packet E physical widths, ULS/SLS statics, T section, Annex F, steel, hooks and quantities")


if __name__ == "__main__":
    main()
