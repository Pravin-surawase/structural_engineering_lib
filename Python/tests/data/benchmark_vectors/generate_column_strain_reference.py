# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Independent column reference: piecewise polynomial integration plus quadrature.

No structural_lib imports. IS456:2000 Cl38.1(a,c,d), Fig21 and Cl39.1(b)
define plane sections, zero tensile concrete, .67/1.5 peak, .002 plateau and
the full-compression face-strain relation. Coordinates y run from the compressed
top face in mm; compression is positive, force N, moment Nmm before conversion.

The representative Fig23 law uses gamma_s=1.15, six cold-worked plastic
offsets and definite-yield Fe250. This material revision is separate from
the previously frozen five-point/.87 compatibility packet.
SciPy is required only to regenerate the fixture, never by the fixture tests.
Cl39.7.1.1 Pb uses tensile strain .002, independently of the public curve's
yield-balanced point. Cl39.7.1 note2 defines relative curvature, not global sign.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from scipy.integrate import quad
from scipy.optimize import brentq


def steel_stress(strain: float, fy: float) -> float:
    yield_stress = fy / 1.15
    if abs(fy - 250.0) < 0.5:
        return math.copysign(min(200000.0 * abs(strain), yield_stress), strain)
    points = [(0.0, 0.0)] + [
        (plastic_strain + fraction * yield_stress / 200000.0, fraction * yield_stress)
        for fraction, plastic_strain in (
            (0.8, 0.0),
            (0.85, 0.0001),
            (0.9, 0.0003),
            (0.95, 0.0007),
            (0.975, 0.001),
            (1.0, 0.002),
        )
    ]
    for (e0, s0), (e1, s1) in zip(points, points[1:], strict=False):
        if abs(strain) <= e1:
            return math.copysign(
                s0 + (s1 - s0) * (abs(strain) - e0) / (e1 - e0), strain
            )
    return math.copysign(yield_stress, strain)


def reference(
    ratio: float | None,
    fy: float,
    peak: float = 0.67 / 1.5,
    *,
    width: float = 230.0,
    depth: float = 450.0,
    fck: float = 20.0,
    steel_area: float = 6 * math.pi * 20 * 20 / 4,
    cover: float = 50.0,
) -> dict:
    xu = math.inf if ratio is None else ratio * depth
    if ratio is None:
        top, gradient = 0.002, 0.0
    elif ratio <= 1:
        top, gradient = 0.0035, -0.0035 / xu
    else:
        # Solve independent constraints: e_far/e_top=1-D/xu,
        # e_top+.75*e_far=.0035, rather than the production expression.
        top = 0.0035 / (1 + 0.75 * (1 - depth / xu))
        far = top * (1 - depth / xu)
        gradient = (far - top) / depth

    def stress(y: float) -> float:
        strain_ratio = min(1.0, max(0.0, (top + gradient * y) / 0.002))
        return peak * fck * (2 * strain_ratio - strain_ratio * strain_ratio)

    breaks = [0.0, depth]
    if gradient:
        breaks += [
            y
            for threshold in (0.0, 0.002)
            if 0 < (y := (threshold - top) / gradient) < depth
        ]
    breaks.sort()
    force = first = 0.0
    for lo, hi in zip(breaks, breaks[1:], strict=False):
        middle_strain = top + gradient * (lo + hi) / 2
        if middle_strain <= 0:
            coefficients = (0.0,)
        elif middle_strain >= 0.002:
            coefficients = (peak * fck,)
        else:
            a, g = top / 0.002, gradient / 0.002
            coefficients = tuple(
                peak * fck * x for x in (2 * a - a * a, 2 * g * (1 - a), -g * g)
            )
        force += width * math.fsum(
            c * (hi ** (i + 1) - lo ** (i + 1)) / (i + 1)
            for i, c in enumerate(coefficients)
        )
        first += width * math.fsum(
            c * (hi ** (i + 2) - lo ** (i + 2)) / (i + 2)
            for i, c in enumerate(coefficients)
        )
    q_force, q_error = quad(
        lambda y: width * stress(y),
        0,
        depth,
        points=breaks[1:-1],
        epsabs=1e-8,
        epsrel=1e-12,
    )
    q_moment, m_error = quad(
        lambda y: width * stress(y) * (depth / 2 - y),
        0,
        depth,
        points=breaks[1:-1],
        epsabs=1e-5,
        epsrel=1e-12,
    )
    rows = []
    for y in (cover, depth - cover):
        strain = top + gradient * y
        area = steel_area / 2
        fs = steel_stress(strain, fy)
        fc = stress(y)
        rows.append(
            {
                "y_mm": y,
                "area_mm2": area,
                "strain": strain,
                "steel_stress_nmm2": fs,
                "concrete_stress_nmm2": fc,
                "net_force_n": area * (fs - fc),
            }
        )
    p = force + math.fsum(row["net_force_n"] for row in rows)
    m = (
        force * depth / 2
        - first
        + math.fsum(row["net_force_n"] * (depth / 2 - row["y_mm"]) for row in rows)
    )
    return {
        "xu_over_D": ratio,
        "fy_nmm2": fy,
        "peak_fck_factor": peak,
        "eps_top": top,
        "eps_far": top + gradient * depth,
        "concrete_force_n": force,
        "concrete_first_top_nmm": first,
        "concrete_moment_center_nmm": force * depth / 2 - first,
        "quad_force_n": q_force,
        "quad_force_error_n": q_error,
        "quad_moment_center_nmm": q_moment,
        "quad_moment_error_nmm": m_error,
        "bars": rows,
        "Pu_kN": p / 1000,
        "Mu_kNm": m / 1e6,
    }


def sampled_curve(section: dict, n_points: int = 50) -> tuple[list, list, float]:
    raw = []
    for i in range(n_points + 1):
        state = reference(0.01 + 2.99 * i / n_points, **section)
        raw.append((state["Pu_kN"], abs(state["Mu_kNm"])))
    nominal = (
        0.4
        * section["fck"]
        * (section["width"] * section["depth"] - section["steel_area"])
        + 0.67 * section["fy"] * section["steel_area"]
    ) / 1000
    capped = [(p, m) if p <= nominal else (nominal, 0.0) for p, m in raw]
    if capped[-1] != (nominal, 0):
        capped.append((nominal, 0.0))
    return raw, capped, nominal


def moment_at(points: list, force: float) -> float:
    intersections = []
    for (p0, m0), (p1, m1) in zip(points, points[1:], strict=False):
        if min(p0, p1) <= force <= max(p0, p1) and p0 != p1:
            intersections.append(m0 + (m1 - m0) * (force - p0) / (p1 - p0))
    return max(intersections, default=0.0)


def radial_capacity(points: list, p: float, m: float) -> dict:
    # Interpolate signed cross products with the load ray, independently of
    # the production matrix inversion. No production source or outputs used.
    intersections = []
    for (p0, m0), (p1, m1) in zip(points, points[1:], strict=False):
        f0, f1 = p0 * m - m0 * p, p1 * m - m1 * p
        if f0 * f1 <= 0 and f0 != f1:
            t = f0 / (f0 - f1)
            pc, mc = p0 + t * (p1 - p0), m0 + t * (m1 - m0)
            if pc >= 0 and mc >= 0:
                intersections.append((pc, mc))
    pc, mc = min(intersections, key=lambda v: math.hypot(*v))
    ratio = math.hypot(p, m) / math.hypot(pc, mc)
    return {
        "Pu_cap_kN": pc,
        "Mu_cap_kNm": mc,
        "utilization_ratio": ratio,
        "is_safe": ratio <= 1,
    }


def continuous_radial(section: dict, p: float, m: float) -> dict:
    def residual(k):
        s = reference(k, **section)
        return s["Pu_kN"] * m - s["Mu_kNm"] * p

    k = brentq(residual, 0.01, 3, xtol=1e-13)
    state = reference(k, **section)
    return {
        "xu_over_D": k,
        "Pu_cap_kN": state["Pu_kN"],
        "Mu_cap_kNm": state["Mu_kNm"],
        "ray_residual_kN_kNm": residual(k),
    }


def slenderness_balance(section: dict) -> dict:
    # Plane-section constraint: .0035*(d-xu)/xu=.002, Cl39.7.1.1.
    xu = (section["depth"] - section["cover"]) / (1 + 0.002 / 0.0035)
    state = reference(xu / section["depth"], **section)
    assert abs(state["bars"][1]["strain"] + 0.002) < 1e-17
    return {"inputs": section, "xu_mm": xu, "state": state}


def long_reference(
    section: dict,
    load: float,
    lengths: tuple[float, float],
    unsupported: float,
    end_x: tuple[float, float],
    end_y: tuple[float, float],
    braced: bool = True,
) -> dict:
    balance = slenderness_balance(section)
    pb = balance["state"]["Pu_kN"]
    puz = (
        0.45
        * section["fck"]
        * (section["width"] * section["depth"] - section["steel_area"])
        + 0.75 * section["fy"] * section["steel_area"]
    ) / 1000
    additional, initial, design, capacities, balances, factors = [], [], [], [], [], []
    for axis, ((m1, m2), le, depth) in enumerate(
        zip((end_x, end_y), lengths, (section["depth"], section["width"]), strict=True)
    ):
        oriented = (
            section
            if axis == 0
            else {**section, "width": section["depth"], "depth": section["width"]}
        )
        plane_balance = slenderness_balance(oriented)
        plane_pb = plane_balance["state"]["Pu_kN"]
        k = max(0, min(1, (puz - load) / (puz - plane_pb)))
        balances.append(plane_balance)
        factors.append(k)
        ma = load * le**2 / (2000 * depth * 1000) if le / depth >= 12 else 0.0
        smaller = abs(m1) if m1 * m2 >= 0 else -abs(m1)
        mi = max(0.4 * smaller + 0.6 * abs(m2), 0.4 * abs(m2)) if braced else abs(m2)
        minimum = load * max(unsupported / 500 + depth / 30, 20) / 1000
        additional.append(ma)
        initial.append(mi)
        design.append(max(mi + k * ma, abs(m2), minimum))
        _, curve, _ = sampled_curve(oriented)
        capacities.append(moment_at(curve, load))
    alpha = max(1, min(2, 1 + (load / puz - 0.2) / 0.6))
    ratio = math.fsum((m / c) ** alpha for m, c in zip(design, capacities, strict=True))
    return {
        "inputs": section,
        "Pu_kN": load,
        "M1x_kNm": end_x[0],
        "M2x_kNm": end_x[1],
        "M1y_kNm": end_y[0],
        "M2y_kNm": end_y[1],
        "lex_mm": lengths[0],
        "ley_mm": lengths[1],
        "l_unsupported_mm": unsupported,
        "braced": braced,
        "Puz_kN": puz,
        "Pb_kN": pb,
        "k": factors[0],
        "k_x": factors[0],
        "k_y": factors[1],
        "Pb_x_kN": pb,
        "Pb_y_kN": balances[1]["state"]["Pu_kN"],
        "xu_39_7_mm": balance["xu_mm"],
        "tension_strain_39_7": balance["state"]["bars"][1]["strain"],
        "xu_y_39_7_mm": balances[1]["xu_mm"],
        "tension_strain_y_39_7": balances[1]["state"]["bars"][1]["strain"],
        "Max_kNm": additional[0],
        "May_kNm": additional[1],
        "Max_reduced_kNm": factors[0] * additional[0],
        "May_reduced_kNm": factors[1] * additional[1],
        "Mi_x_kNm": initial[0],
        "Mi_y_kNm": initial[1],
        "Mux_design_kNm": design[0],
        "Muy_design_kNm": design[1],
        "Mux1_kNm": capacities[0],
        "Muy1_kNm": capacities[1],
        "interaction_ratio": ratio,
        "is_safe": ratio <= 1,
    }


def consumers() -> dict:
    pm = {
        "width": 400.0,
        "depth": 400.0,
        "fck": 25.0,
        "fy": 415.0,
        "steel_area": 8 * math.pi * 16 * 16 / 4,
        "cover": 50.0,
    }
    _, capped, nominal = sampled_curve(pm)
    bal = (
        (pm["depth"] - pm["cover"])
        * 0.0035
        / (0.0035 + pm["fy"] / (1.15 * 200000) + 0.002)
    )
    balanced = reference(bal / pm["depth"], **pm)
    gc_pm = {
        "inputs": pm,
        "Pu_0_kN": nominal,
        "Pu_bal_kN": balanced["Pu_kN"],
        "Mu_bal_kNm": balanced["Mu_kNm"],
        "Mu_0_kNm": moment_at(capped, 0),
    }

    uni = {**pm, "steel_area": 4 * math.pi * 25 * 25 / 4}
    raw, _, _ = sampled_curve(uni, n_points=200)
    gc_uni = {
        "inputs": uni,
        "Pu_kN": 1000.0,
        "Mu_kNm": 100.0,
        "sampled": radial_capacity(raw, 1000, 100),
        "continuous": continuous_radial(uni, 1000, 100),
    }
    boundary = {**pm, "steel_area": 3200.0}
    raw, _, _ = sampled_curve(boundary, n_points=200)
    boundary_m = moment_at(raw, 500) * 1.00001
    display_boundary = {
        "inputs": boundary,
        "Pu_kN": 500.0,
        "Mu_kNm": boundary_m,
        "sampled": radial_capacity(raw, 500, boundary_m),
    }

    biax = {
        "width": 400.0,
        "depth": 500.0,
        "fck": 25.0,
        "fy": 415.0,
        "steel_area": 2400.0,
        "cover": 50.0,
    }
    _, xp, _ = sampled_curve(biax)
    _, yp, _ = sampled_curve({**biax, "width": biax["depth"], "depth": biax["width"]})
    mx, my = moment_at(xp, 1200), moment_at(yp, 1200)
    puz = (
        0.45 * biax["fck"] * (biax["width"] * biax["depth"] - biax["steel_area"])
        + 0.75 * biax["fy"] * biax["steel_area"]
    ) / 1000
    alpha = max(1, min(2, 1 + (1200 / puz - 0.2) / 0.6))
    interaction = (80 / mx) ** alpha + (60 / my) ** alpha
    gc_bi = {
        "inputs": biax,
        "Pu_kN": 1200.0,
        "Mux_kNm": 80.0,
        "Muy_kNm": 60.0,
        "Mux1_kNm": mx,
        "Muy1_kNm": my,
        "Puz_kN": puz,
        "alpha_n": alpha,
        "interaction_ratio": interaction,
        "is_safe": interaction <= 1,
    }
    long_section = {
        "width": 300.0,
        "depth": 500.0,
        "fck": 25.0,
        "fy": 415.0,
        "steel_area": 3000.0,
        "cover": 50.0,
    }
    long_case = long_reference(
        long_section, 1100, (6500, 4000), 5000, (50, 80), (30, 50)
    )
    review_section = {**long_section, "depth": 450.0, "steel_area": 2700.0}
    golden_long = long_reference(
        {**long_section, "steel_area": 2400.0},
        800,
        (7000, 5000),
        7000,
        (40, 80),
        (20, 50),
    )
    review_cases = [
        long_reference(review_section, 1000, (6300, 3000), 6300, (m, m), (0, 0))
        for m in (170, -170, 165)
    ] + [
        long_reference(
            review_section,
            1000,
            (6300, 3000),
            6300,
            (curvature * 80 * flip_x, 170 * flip_x),
            (curvature * 25 * flip_y, 60 * flip_y),
            braced,
        )
        for braced in (True, False)
        for curvature in (1, -1)
        for flip_x in (1, -1)
        for flip_y in (1, -1)
    ]
    axis_cases = []
    for exchanged in (False, True):
        oriented = (
            {**review_section, "width": 450.0, "depth": 300.0}
            if exchanged
            else review_section
        )
        for braced in (True, False):
            for sign in (1, -1):
                ends = (
                    ((0, 0), (161 * sign, 161 * sign))
                    if exchanged
                    else ((161 * sign, 161 * sign), (0, 0))
                )
                lengths = (3000, 6300) if exchanged else (6300, 3000)
                axis_cases.append(
                    long_reference(oriented, 1000, lengths, 6300, *ends, braced)
                )
            for curvature in (1, -1):
                for flip_x in (1, -1):
                    for flip_y in (1, -1):
                        ends = (
                            (curvature * 40 * flip_x, 80 * flip_x),
                            (curvature * 25 * flip_y, 60 * flip_y),
                        )
                        lengths = (6300, 4200)
                        if exchanged:
                            ends, lengths = ends[::-1], lengths[::-1]
                        axis_cases.append(
                            long_reference(oriented, 1000, lengths, 6300, *ends, braced)
                        )
    axis_cases += [
        long_reference(
            {**review_section, "width": 400, "depth": 400, "steel_area": 3200},
            1000,
            (6000, 6000),
            6000,
            (40, 80),
            (25, 60),
        ),
        long_reference(
            {**review_section, "width": 450, "depth": 300},
            1000,
            (4200, 6300),
            6300,
            (40, 40),
            (112.3, 112.3),
        ),
    ]
    return {
        "GC-PM1": gc_pm,
        "GC-UNI1": gc_uni,
        "GC-BI1": gc_bi,
        "uniaxial_display_boundary": display_boundary,
        "long_column": long_case,
        "long_column_sign_and_pb": review_cases,
        "long_column_axes": axis_cases,
        "GC-AM1": {
            name: golden_long[name]
            for name in ("Puz_kN", "Pb_kN", "k", "Max_kNm", "May_kNm")
        },
        "GC-LC1": golden_long,
    }


if __name__ == "__main__":
    ratios = [
        0.25,
        0.5,
        1 - 1e-8,
        1.0,
        1 + 1e-8,
        1.000001,
        1.05,
        1.5,
        2.0,
        7 / 3,
        3.0,
        20.0,
        1000.0,
        None,
    ]
    peak_45 = (0.67 / 1.5) * 25.0
    steel_45 = steel_stress(0.002625, 415.0)
    pc_45 = 4 * 100.0**2 * peak_45 * (33 / 98)
    mc_45 = 4 * 100.0**3 * peak_45 * (1499 / 10290)
    p_45 = pc_45 - peak_45 * 400
    m_45 = mc_45 + (2 * steel_45 - peak_45) * 400 * 75
    data = {
        "source": {
            "standard": "IS 456:2000 fourth revision, Cl38.1(a,c,d,e)/Fig21/Fig23/Cl39.1(b)",
            "primary_url": "https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf#page=82",
            "source_limit": "Controlled Amd5 and Amd6 inspected for relevant provisions; latest complete amendment set not certified",
            "mechanics": "independent face-constraint solution and piecewise polynomial integral",
            "method": "IS456_FIG21_INTEGRATED_V1__STEEL_FIG23_GS115_V1",
            "sampling": "50 intervals for public PM/biaxial/long owners; 200 for uniaxial radial check",
            "slenderness_source": "Cl39.7.1 note2 and Cl39.7.1.1, printed p72; Pb eps_top=.0035, eps_t=-.002",
            "slenderness_method": "IS456_39_7_1_1_PER_AXIS_V1",
            "scalar_compatibility": "Legacy k and Pb_kN remain x-plane aliases; each additional moment uses its own plane state",
            "steel_limit": "Fig23A source-parameterized representative cold-worked law; Fe250 Fig23B definite-yield; gamma_s=1.15; material-family applicability remains caller responsibility",
            "units": "mm, N/mm2, N, Nmm; reported Pu kN, Mu kNm",
            "b_mm": 230.0,
            "D_mm": 450.0,
            "fck_nmm2": 20.0,
            "d_prime_mm": 50.0,
            "Asc_mm2": 6 * math.pi * 20 * 20 / 4,
        },
        "states": [
            reference(k, fy) for fy in (250.0, 415.0, 500.0, 550.0) for k in ratios
        ],
        "peak_sensitivities": [
            reference(k, 415.0, peak)
            for k in (1.0, 2.0, 3.0)
            for peak in (0.67 / 1.5, 4 / 9, 0.446)
        ],
        "oblique_45": {
            "concrete_force_kN": pc_45 / 1000,
            "concrete_moment_kNm": mc_45 / 1e6,
            "steel_stress_nmm2": steel_45,
            "Pu_kN": p_45 / 1000,
            "Mx_kNm": m_45 / 1e6,
            "My_kNm": -m_45 / 1e6,
        },
        "consumers": consumers(),
        "slenderness_balanced_states": [
            slenderness_balance(
                {
                    "width": 300.0,
                    "depth": 450.0,
                    "fck": 25.0,
                    "fy": fy,
                    "steel_area": 2700.0,
                    "cover": 50.0,
                }
            )
            for fy in (250.0, 415.0, 500.0, 550.0)
        ],
    }
    path = Path(__file__).with_name("column_strain_compatibility.json")
    path.write_text(
        json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        f"Frozen {len(data['states'])} independent states and 9 peak sensitivities: {path}"
    )
