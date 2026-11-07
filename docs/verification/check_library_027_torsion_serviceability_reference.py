"""Independent stdlib-only service-state replay; never import the engine."""

from __future__ import annotations

import json
import math
from pathlib import Path


def main() -> None:
    reference = json.loads(
        Path(__file__).with_name("library-027-torsion-serviceability.json").read_text()
    )
    inputs, expected = reference["inputs"], reference["expected"]
    b, D, span = inputs["b_mm"], inputs["D_mm"], inputs["analysis_span_mm"]
    steel = inputs["steel_modulus_nmm2"]
    area = math.pi * inputs["bar_diameter_mm"] ** 2 / 4
    depths = inputs["bar_depths_mm"]

    def transformed(modulus: float) -> tuple[float, float]:
        ratio = steel / modulus
        lo, hi = 0.0, D
        for _ in range(180):
            x = (lo + hi) / 2
            force = b * x * x / 2 + sum(
                (ratio - int(y < x)) * 2 * area * (x - y) for y in depths
            )
            if force > 0:
                hi = x
            else:
                lo = x
        x = (lo + hi) / 2
        inertia = b * x**3 / 3 + sum(
            (ratio - int(y < x)) * 2 * area * (x - y) ** 2 for y in depths
        )
        return x, inertia

    def check(key: str, value: float, *, absolute: float = 1e-8) -> None:
        assert math.isclose(value, expected[key], rel_tol=1e-12, abs_tol=absolute), (
            key,
            value,
            expected[key],
        )

    Ec = 5000 * math.sqrt(inputs["concrete_strength_nmm2"])
    x, inertia = transformed(Ec)
    xl, inertia_long = transformed(Ec / 2.6)
    check("short_term_neutral_axis_mm", x)
    check("short_term_cracked_inertia_mm4", inertia)
    check("long_term_neutral_axis_mm", xl)
    check("long_term_cracked_inertia_mm4", inertia_long)
    g, q = inputs["permanent_load_n_per_mm"], inputs["transient_load_n_per_mm"]
    assert inputs["permanent_eccentricity_mm"] == 0
    assert g + q == 8 and 1.5 * (g + q) == 12
    intensity = q * inputs["transient_eccentricity_mm"]
    assert intensity == 8 * 50 and 1.5 * intensity == 12 * 50
    curvature = (g + q) * span**2 / 8 / (Ec * inertia)
    strain = curvature * (D - x)
    check("elastic_tension_surface_strain", strain, absolute=1e-12)
    check("bottom_steel_stress_nmm2", steel * curvature * (depths[-1] - x))
    acr = math.hypot(100, 50) - 10
    check(
        "flexural_crack_width_upper_bound_mm",
        3 * acr * strain / (1 + 2 * (acr - 40) / (D - x)),
    )
    initial = 5 * (g + q) * span**4 / (384 * Ec * inertia)
    permanent = initial * g / (g + q)
    long = 5 * g * span**4 / (384 * (Ec / 2.6) * inertia_long)
    check("initial_total_flexural_deflection_mm", initial)
    check("initial_permanent_flexural_deflection_mm", permanent)
    check("long_term_permanent_flexural_deflection_mm", long)
    pt = 100 * 2 * area / (b * depths[-1])
    shrinkage = 0.125 * 0.72 * math.sqrt(pt) * 0.0003 / D * span**2
    check("shrinkage_upper_bound_mm", shrinkage)
    rl = 4 * area / (b * D)
    rt = (math.pi * 8**2 / 4) * 1168 / (b * D * 100)
    stiffness = 4 * steel * 60000**3 / (1000**2 * (1 / rl + 1 / rt))
    twist = intensity * span**2 / (8 * stiffness)
    check("lampert_stiffness_nmm2", stiffness)
    check("midspan_relative_twist_rad", twist)
    check(
        "final_total_edge_deflection_mm",
        initial + long - permanent + shrinkage + 150 * twist,
    )
    check(
        "after_finishes_edge_deflection_upper_bound_mm",
        initial + long - 2 * permanent + shrinkage + 150 * twist,
    )
    paper = 4 * steel * 434125**3 / (2660**2 * (1 / 0.045 + 1 / 0.015))
    check("paper_stiffness_nmm2", paper)
    assert abs(paper / 1e9 - 104100) < 50  # source rounded to 104.1e3 kNm²
    assert (g + q) * span**2 / 8 / 1e6 == expected["midspan_service_moment_knm"]
    assert inputs["code_effective_span_mm"] / 250 == expected["total_limit_mm"]
    print(
        "PASS independent D3 load reconstruction, transformed section, time components, flexural crack and published cubic-area torsional stiffness"
    )


if __name__ == "__main__":
    main()
