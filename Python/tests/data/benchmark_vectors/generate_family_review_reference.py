# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Independent S4 engineering references for the thirteen frozen F0 journeys.

No structural_lib imports or calculated production outputs. This file evaluates
the explicitly frozen specimens in family_review_inputs.json. IS456 coefficients
are normalized data, not clause prose. Source editions/hashes and applicability
are recorded in docs/verification/library-s4-20261029.json. Regeneration needs
SciPy only for the adjacent independent column integrator; replay does not.

Rectangular flexure is solved by Decimal bisection of concrete force equilibrium,
independently of the production quadratic. Stair actions use integrated piecewise
loads; footing actions use free-body equilibrium. The column specimen deliberately
compares the public 50-interval polygon and separately records mesh sensitivity.
These checks do not qualify excluded models or caller-supplied physical facts.
"""

from __future__ import annotations

import hashlib
import json
import math
from decimal import Decimal, localcontext
from pathlib import Path

from tests.data.benchmark_vectors.generate_column_strain_reference import (
    moment_at,
    sampled_curve,
)

HERE = Path(__file__).parent


def rect(moment: float, width: float, depth: float, fck: float, fy: float):
    """Cl38.1/Annex G: force block .36 fck b xu; lever arm d-.42 xu."""
    with localcontext() as context:
        context.prec = 45
        m, b, d, fc, steel = map(Decimal, map(str, (moment, width, depth, fck, fy)))
        lo, hi = Decimal(0), d
        for _ in range(160):
            x = (lo + hi) / 2
            capacity = Decimal(".36") * fc * b * x * (d - Decimal(".42") * x)
            if capacity < m * 10**6:
                lo = x
            else:
                hi = x
        x = (lo + hi) / 2
        area = Decimal(".36") * fc * b * x / (Decimal(".87") * steel)
        limit = Decimal(".46" if fy == 500 else ".48") * d
        mu_limit = (
            Decimal(".36") * fc * b * limit * (d - Decimal(".42") * limit) / 10**6
        )
        return float(area), float(x), float(mu_limit)


def area(diameter: float, count: float = 1):
    return count * math.pi * diameter**2 / 4


def generate():
    inputs = json.loads((HERE / "family_review_inputs.json").read_text())
    result = []

    def case(index, clauses, method):
        specimen = inputs["cases"][index]
        record = {
            "journey_id": specimen["journey_id"],
            "request_sha256": hashlib.sha256(
                json.dumps(
                    specimen["request"], sort_keys=True, separators=(",", ":")
                ).encode()
            ).hexdigest(),
            "expected_engineering_status": (
                "FAIL" if index == 5 else "HOLD" if index == 7 else "PASS"
            ),
            "source_clauses": clauses,
            "independent_method": method,
            "metrics": [],
        }
        result.append(record)

        def metric(path, value, unit, absolute=1e-7, relative=1e-10):
            record["metrics"].append(
                {
                    "path": "calculation." + path,
                    "expected": value,
                    "unit": unit,
                    "absolute_tolerance": absolute,
                    "relative_tolerance": relative,
                }
            )

        return metric

    add = case(
        0,
        ["38.1", "Annex G", "40.1"],
        "Decimal force-equilibrium bisection and V/(bd).",
    )
    a, x, ml = rect(150, 300, 457, 25, 500)
    for path, value, unit in [
        ("flexure.Ast_required", a, "mm2"),
        ("flexure.xu", x, "mm"),
        ("flexure.Mu_lim", ml, "kNm"),
        ("shear.tau_v", 75000 / (300 * 457), "N/mm2"),
    ]:
        add(path, value, unit)

    add = case(
        1,
        ["41.3", "41.4.3"],
        "Equivalent actions and distinct torsion/shear terms using supplied corner-bar centres; public rounding retained.",
    )
    for path, value, unit, tol in [
        ("Ve_kn", 75 + 1.6 * 10 * 1000 / 300, "kN", 1e-7),
        ("Me_knm", 150 + 10 * (1 + 500 / 300) / 1.7, "kNm", 1e-7),
        ("tau_ve", (75 + 1.6 * 10 * 1000 / 300) * 1000 / (300 * 457), "N/mm2", 0.0005),
        ("Asv_torsion", 10e6 / (214 * 414 * 0.87 * 500), "mm2/mm", 0.00005),
        ("Asv_shear", 75e3 / (2.5 * 414 * 0.87 * 500), "mm2/mm", 0.00005),
        (
            "Asv_total",
            10e6 / (214 * 414 * 0.87 * 500) + 75e3 / (2.5 * 414 * 0.87 * 500),
            "mm2/mm",
            0.00005,
        ),
    ]:
        add(path, value, unit, tol)

    add = case(
        2,
        ["25.4", "38.1", "39.6", "Fig21", "Fig23"],
        "Independent piecewise stress integration, 50-interval public polygon, biaxial equation; mesh sensitivity is separate.",
    )
    section = {
        "width": 300.0,
        "depth": 450.0,
        "fck": 25.0,
        "fy": 415.0,
        "steel_area": 2400.0,
        "cover": 50.0,
    }
    mx = moment_at(sampled_curve(section)[1], 800)
    my = moment_at(sampled_curve({**section, "width": 450.0, "depth": 300.0})[1], 800)
    puz = (0.45 * 25 * (300 * 450 - 2400) + 0.75 * 415 * 2400) / 1000
    alpha = 1 + (800 / puz - 0.2) / 0.6
    for path, value, unit, tol in [
        ("emin_x_mm", 3000 / 500 + 450 / 30, "mm", 1e-7),
        ("Muy_design_kNm", 800 * 20 / 1000, "kNm", 1e-7),
        ("checks.biaxial.Puz_kN", puz, "kN", 0.005),
        ("checks.biaxial.Mux1_kNm", mx, "kNm", 0.005),
        ("checks.biaxial.Muy1_kNm", my, "kNm", 0.005),
        ("checks.biaxial.alpha_n", alpha, "ratio", 0.00005),
        (
            "checks.biaxial.interaction_ratio",
            (120 / mx) ** alpha + (16 / my) ** alpha,
            "ratio",
            0.00005,
        ),
    ]:
        add(path, value, unit, tol)
    result[-1]["mesh_sensitivity"] = [
        {
            "intervals": n,
            "mx_capacity_knm": moment_at(sampled_curve(section, n)[1], 800),
            "my_capacity_knm": moment_at(
                sampled_curve({**section, "width": 450.0, "depth": 300.0}, n)[1], 800
            ),
        }
        for n in (200, 1000)
    ]

    add = case(
        3,
        ["38.1", "26.5.2.1", "26.3.3", "40.2.1.1+A5", "23.2.1"],
        "Simply supported UDL; Decimal flexure; independent bar areas and reviewed span/depth bound.",
    )
    a, x, ml = rect(10 * 3**2 / 8, 1000, 125, 20, 415)
    for path, value, unit in [
        ("reinforcement.flexure.factored_moment_knm", 11.25, "kNm"),
        ("reinforcement.flexure.ast_required_mm2", a, "mm2"),
        ("reinforcement.flexure.limiting_moment_knm", ml, "kNm"),
        (
            "reinforcement.detailing.main_reinforcement_provided_mm2",
            area(10) * 1000 / 250,
            "mm2",
        ),
        (
            "reinforcement.detailing.minimum_reinforcement_mm2",
            0.0012 * 1000 * 150,
            "mm2",
        ),
        ("shear.tau_v_n_per_mm2", 15e3 / (1000 * 125), "N/mm2"),
        ("shear.tau_c_max_n_per_mm2", 2.8 / 2, "N/mm2"),
        ("serviceability.utilization", (3000 / 125) / (20 * 1.2), "ratio"),
    ]:
        add(path, value, unit)

    add = case(
        4,
        ["Table12", "Table13", "38.1", "26.5.2.1", "26.3.3+A3"],
        "Separate DL/IL end-span and next-to-end support coefficients; Decimal flexure.",
    )
    positive = 7.5 * 9 / 12 + 2.5 * 9 / 10
    negative = 7.5 * 9 / 10 + 2.5 * 9 / 9
    for name, moment in [
        ("positive_midspan", positive),
        ("negative_support", negative),
    ]:
        add(f"flexure.{name}.factored_moment_knm_per_m", moment, "kNm/m")
        add(
            f"flexure.{name}.ast_required_mm2_per_m",
            rect(moment, 1000, 130, 20, 415)[0],
            "mm2/m",
        )
    add("flexure.factored_shear_kn_per_m", 7.5 * 3 * 0.4 + 2.5 * 3 * 0.45, "kN/m")
    add("distribution_reinforcement.maximum_spacing_mm", 300, "mm")

    add = case(
        5,
        ["Annex D", "Table26 case4+A2", "26.5.2.1"],
        "Two adjacent discontinuous edges, aspect1.5; four distinct source coefficients and independent steel demand. FAIL is expected.",
    )
    for name, coefficient, depth, dia in [
        ("x_negative", 0.075, 135, 10),
        ("x_positive", 0.056, 135, 10),
        ("y_negative", 0.047, 125, 8),
        ("y_positive", 0.035, 125, 8),
    ]:
        m = coefficient * 15.5 * 4**2
        add(f"panel.{name}.coefficient", coefficient, "ratio")
        add(f"panel.{name}.factored_moment_knm_per_m", m, "kNm/m")
        add(
            f"panel.{name}.ast_required_mm2_per_m",
            rect(m, 1000, depth, 20, 415)[0],
            "mm2/m",
        )
        add(
            f"panel.{name}.reinforcement.provided_mm2_per_m",
            area(dia) * 1000 / 200,
            "mm2/m",
        )

    add = case(
        6,
        ["32.2", "32.5", "A6"],
        "Braced axial wall: source effective height/eccentricity and net compression thickness; independent reinforcement ratios.",
    )
    for path, value, unit in [
        ("axial.geometry.effective_height_mm", 0.75 * 3000, "mm"),
        ("axial.minimum_eccentricity_mm", 0.05 * 150, "mm"),
        ("axial.additional_eccentricity_mm", 2250**2 / (2500 * 150), "mm"),
        (
            "axial.axial_capacity_n_per_mm",
            0.3 * 20 * (150 - 1.2 * 7.5 - 2 * 13.5),
            "N/mm",
        ),
        ("axial.utilization_ratio", 500 / 684, "ratio"),
        (
            "reinforcement.vertical.required_area_mm2_per_m",
            0.0012 * 150 * 1000,
            "mm2/m",
        ),
        (
            "reinforcement.horizontal.required_area_mm2_per_m",
            0.002 * 150 * 1000,
            "mm2/m",
        ),
    ]:
        add(path, value, unit)

    add = case(
        7,
        ["33.1-33.3", "38.1", "26.3.3+A3"],
        "Three piecewise uniform loads integrated by equilibrium and zero shear. Independent source math does not remove physical-spacing HOLD.",
    )
    slope = math.hypot(270, 160) / 270
    loads = [
        (0.75, (5 + 6) * 0.5 * 1.5 * 1.5),
        (2.7, (0.25 * 25 * slope + 0.160 * 25 / 2 + 6) * 1.5 * 1.5),
        (1.65, (5 + 6) * 1.5 * 1.5),
    ]
    total = sum(length * q for length, q in loads)
    start, first = 0.0, 0.0
    for length, q in loads:
        first += length * q * (start + length / 2)
        start += length
    right = first / start
    left = total - right
    zero = 0.75 + (left - loads[0][0] * loads[0][1]) / loads[1][1]
    moment = (
        left * zero
        - loads[0][0] * loads[0][1] * (zero - 0.75 / 2)
        - loads[1][1] * (zero - 0.75) ** 2 / 2
    )
    for path, value, unit in [
        ("geometry.slope_factor", slope, "ratio"),
        ("actions.total_factored_load_kn", total, "kN"),
        ("actions.lower_support_reaction_kn", left, "kN"),
        ("actions.upper_support_reaction_kn", right, "kN"),
        ("actions.maximum_moment_location_mm", zero * 1000, "mm"),
        ("actions.maximum_factored_moment_knm_per_m", moment / 1.5, "kNm/m"),
        (
            "design.ast_required_mm2_per_m",
            rect(moment / 1.5, 1000, 224, 20, 415)[0],
            "mm2/m",
        ),
        ("design.maximum_distribution_bar_spacing_mm", 300, "mm"),
    ]:
        add(path, value, unit)

    add = case(
        8,
        ["29.2", "29.3", "26.2.1", "32.5"],
        "Deep-beam lever arm, tie equilibrium and .8 Ld embedment; two face grids counted separately.",
    )
    for path, value, unit in [
        ("reinforcement.geometry.lever_arm_mm", 0.2 * (3000 + 2 * 2000), "mm"),
        (
            "reinforcement.positive_tie.required_area_mm2",
            900e6 / (0.87 * 500 * 1400),
            "mm2",
        ),
        ("reinforcement.positive_tie.provided_area_mm2", area(22, 4), "mm2"),
        (
            "reinforcement.anchorage.development_length_mm",
            22 * 0.87 * 500 / (4 * 2.4),
            "mm",
        ),
        (
            "reinforcement.anchorage.required_embedment_mm",
            0.8 * 22 * 0.87 * 500 / (4 * 2.4),
            "mm",
        ),
        (
            "reinforcement.vertical_side_face.provided_area_mm2_per_m",
            area(10, 2) * 1000 / 300,
            "mm2/m",
        ),
        (
            "reinforcement.horizontal_side_face.provided_area_mm2_per_m",
            area(10, 2) * 1000 / 250,
            "mm2/m",
        ),
    ]:
        add(path, value, unit)

    add = case(
        9,
        ["31.4.2.2", "31.6.3.2", "Fig16", "38.1"],
        "Direct design regular interior panel only; source strip factors and critical-perimeter load subtraction.",
    )
    m0 = 19.5 * 6 * 5.5**2 / 8
    for axis in ("x", "y"):
        add(f"reinforcement.moments.{axis}.total_static_moment_knm", m0, "kNm")
        add(f"reinforcement.moments.{axis}.total_negative_moment_knm", 0.65 * m0, "kNm")
        add(
            f"reinforcement.moments.{axis}.column_strip_negative_moment_knm",
            0.75 * 0.65 * m0,
            "kNm",
        )
        add(
            f"reinforcement.{axis}.column_strip_negative.ast_required_total_mm2",
            rect(0.75 * 0.65 * m0, 3000, 260, 30, 500)[0],
            "mm2",
        )
    add("punching.critical_perimeter_mm", 4 * (500 + 260), "mm")
    add("punching.punching_shear_force_kn", 702 - 19.5 * 0.760**2, "kN")
    add(
        "punching.nominal_punching_stress_n_per_mm2",
        (702 - 19.5 * 0.760**2) * 1000 / (3040 * 260),
        "N/mm2",
    )

    add = case(
        10,
        ["34.1", "34.2.3.1", "34.2.4.1", "Table19", "31.6.3.2"],
        "Concentric footing equilibrium; face flexure; actual 13T12 pt interpolated between M25 .15/.25 anchors; critical punching perimeter.",
    )
    pt = area(12, 13) / (2000 * 400) * 100
    tc = 0.29 + (0.36 - 0.29) * (pt - 0.15) / (0.25 - 0.15)
    for path, value, unit in [
        ("bearing.q_max_kPa", 800 / 4, "kPa"),
        ("flexure.Mu_L_kNm", 0.3 * 2000 * 800**2 / 2 / 1e6, "kNm"),
        ("flexure.Ast_L_mm2", rect(192, 2000, 400, 25, 415)[0], "mm2"),
        ("one_way_shear.Vu_kN", 0.3 * 2000 * (800 - 400) / 1000, "kN"),
        ("one_way_shear.tau_c_nmm2", tc, "N/mm2"),
        ("one_way_shear.utilization_ratio", 0.3 / tc, "ratio"),
        ("punching.perimeter_mm", 4 * (400 + 400), "mm"),
        ("punching.Vu_punch_kN", 1200 - 0.3 * 800**2 / 1000, "kN"),
        ("punching.utilization_ratio", 0.7875 / 1.25, "ratio"),
    ]:
        add(path, value, unit)

    add = case(
        11,
        ["34.2.3", "34.2.4", "31.6", "38.1"],
        "Uniform-soil rigid-body equilibrium; signed midpoint moment; independent top steel and punching load subtraction.",
    )
    for path, value, unit in [
        (
            "strength.actions.gross_service_pressure_kn_per_m2",
            (1800 + 25 * 15) / 15,
            "kPa",
        ),
        (
            "strength.actions.net_factored_structural_pressure_kn_per_m2",
            2700 / 15,
            "kPa",
        ),
        ("strength.actions.upward_line_load_kn_per_m", 180 * 2.5, "kN/m"),
        (
            "strength.top_longitudinal_flexure.flexural_steel_required_mm2",
            rect(675, 2500, 750, 30, 500)[0],
            "mm2",
        ),
        (
            "strength.top_longitudinal_flexure.minimum_steel_required_mm2",
            0.0012 * 2500 * 850,
            "mm2",
        ),
        (
            "strength.top_longitudinal_flexure.provided_steel_area_mm2",
            area(16) * 2500 / 190,
            "mm2",
        ),
        ("strength.punching.0.factored_punching_shear_kn", 1350 - 180 * 1.25**2, "kN"),
        ("strength.punching.0.utilization", 0.285 / (0.25 * math.sqrt(30)), "ratio"),
    ]:
        add(path, value, unit)

    add = case(
        12,
        ["34.1", "38.1", "40.4", "26.5.1.6", "Table19"],
        "Two-reaction free body, signed clear-strap moment, independent stress block and actual-pt M30 interpolation; stirrup fy capped415.",
    )
    # Solve reactions from sum forces and moments about the exterior reaction.
    total = 1538.34375 + 2612.15625 + 18 * 2.75
    ri = (
        1538.34375 * (0.4 - 1.2) + 2612.15625 * (6.4 - 1.2) + 18 * 2.75 * (3.775 - 1.2)
    ) / (6.4 - 1.2)
    re = total - ri
    shear = re - 1538.34375
    moment = abs(re * 1.2 - 1538.34375 * (2.4 - 0.4))
    steel = area(25, 6)
    xu = 0.87 * 500 * steel / (0.36 * 30 * 500)
    pt = 100 * steel / (500 * 850)
    tc = 0.5 + (0.59 - 0.5) * (pt - 0.5) / 0.25
    for path, value, unit in [
        ("strength.actions.factored.exterior_reaction_kn", re, "kN"),
        ("strength.actions.factored.interior_reaction_kn", ri, "kN"),
        ("strength.flexure.factored_moment_demand_kn_m", moment, "kNm"),
        (
            "strength.flexure.exact_flexural_steel_required_mm2",
            rect(moment, 500, 850, 30, 500)[0],
            "mm2",
        ),
        (
            "strength.flexure.top_moment_capacity_kn_m",
            0.87 * 500 * steel * (850 - 0.42 * xu) / 1e6,
            "kNm",
        ),
        ("strength.shear.concrete_design_shear_strength_nmm2", tc, "N/mm2"),
        (
            "strength.shear.stirrup_carried_shear_required_kn",
            shear - tc * 500 * 850 / 1000,
            "kN",
        ),
        (
            "strength.shear.minimum_stirrup_area_at_provided_spacing_mm2",
            0.4 * 500 * 250 / (0.87 * 415),
            "mm2",
        ),
        (
            "strength.shear.stirrup_shear_capacity_provided_kn",
            0.87 * 415 * area(10, 2) * 850 / 250 / 1000,
            "kN",
        ),
    ]:
        add(path, value, unit)

    return {
        "schema_version": "s4-family-reference/v1",
        "source": "IS456:2000 controlled A1-A5 collection plus issued A6 2024; selected locators only, full amendment qualification remains HOLD",
        "independence": "No production imports or outputs; source equations, Decimal force equilibrium, statics, and adjacent independent column integrator.",
        "tolerances": "Unrounded equations: absolute1e-7/relative1e-10; documented public column rounding .005 kNm/.00005 ratio and torsion rounding .0005 stress/.00005 Asv/s. No tolerance widening from observed output.",
        "cases": result,
    }


if __name__ == "__main__":
    (HERE / "family_review_reference.json").write_text(
        json.dumps(generate(), indent=2, allow_nan=False) + "\n"
    )
