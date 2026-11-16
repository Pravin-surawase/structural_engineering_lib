"""Independent finite-age service reference for the actual B01 one-way slab strip."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

FIXTURE = Path(__file__).with_name("library-030-serv03-b01-service.json")
WIDTH, DEPTH, EFFECTIVE_DEPTH = 1000, 150, 125
FCK, FY, ES = 20, 415, 200000
EC = 5000 * math.sqrt(FCK)
IG = WIDTH * DEPTH**3 / 12
MCR = 0.7 * math.sqrt(FCK) * IG / (DEPTH / 2) / 1e6
BAR_POSITIONS = (125, 375, 625, 875)
BAR_DIA = 10
AST = len(BAR_POSITIONS) * math.pi * BAR_DIA**2 / 4
CRACK_LIMIT = 0.30
LOAD_SUSTAINED, LOAD_TOTAL = 4, 7
FINISH = {"age_days": 90, "creep_coefficient": 0.6, "shrinkage_strain": 0.00010}
ASSESSMENT = {"age_days": 365, "creep_coefficient": 1.2, "shrinkage_strain": 0.00022}


def actions(span: float, intensity: float) -> tuple[float, float]:
    # A one-metre strip has the same numerical N/mm line load as its kPa.
    return intensity * span**2 / 8e6, intensity * span / 2000


def section(modulus: float, moment: float) -> dict[str, float | bool]:
    modular_ratio = ES / modulus
    first_moment_factor = modular_ratio * AST / WIDTH
    x = (
        math.sqrt(first_moment_factor**2 + 2 * first_moment_factor * EFFECTIVE_DEPTH)
        - first_moment_factor
    )
    concrete_q = WIDTH * x**2 / 2
    steel_q = modular_ratio * AST * (EFFECTIVE_DEPTH - x)
    assert math.isclose(concrete_q, steel_q, abs_tol=1e-8)
    inertia = WIDTH * x**3 / 3 + modular_ratio * AST * (EFFECTIVE_DEPTH - x) ** 2
    assert 0 < inertia < IG
    lever = EFFECTIVE_DEPTH - x / 3
    cracked = moment > MCR
    if cracked:
        reduction = 1.2 - (MCR / moment) * (lever / EFFECTIVE_DEPTH) * (
            1 - x / EFFECTIVE_DEPTH
        )
        effective_inertia = min(IG, max(inertia, inertia / reduction))
    else:
        effective_inertia = IG
    return {
        "concrete_modulus_nmm2": modulus,
        "neutral_axis_mm": x,
        "cracked_inertia_mm4": inertia,
        "effective_inertia_mm4": effective_inertia,
        "cracked": cracked,
    }


def uniform_displacement(
    load: float, span: float, modulus: float, inertia: float
) -> float:
    # Double integration of EI v'' = M with zero end displacement.
    return 5 * load * span**4 / (384 * modulus * inertia)


def stage(span: float, creep: float, shrinkage: float, sustained_moment: float) -> dict:
    modulus = EC / (1 + creep)
    state = section(modulus, sustained_moment)
    displacement = uniform_displacement(
        LOAD_SUSTAINED, span, modulus, state["effective_inertia_mm4"]
    )
    # Only the parallel Ø10 bars participate in longitudinal shrinkage.
    pt = 100 * AST / (WIDTH * EFFECTIVE_DEPTH)
    assert 0.25 < pt < 1
    k4 = min(1, 0.72 * pt / math.sqrt(pt))
    curvature = k4 * shrinkage / DEPTH
    delta_shrinkage = curvature * span**2 / 8
    return {
        **state,
        "sustained_deflection_mm": displacement,
        "shrinkage_curvature_per_mm": curvature,
        "shrinkage_deflection_mm": delta_shrinkage,
    }


def conditional_crack_width(
    total_moment: float, sustained_moment: float, initial: dict, long_stage: dict
) -> dict:
    if total_moment <= MCR:
        return {
            "status": "PASS",
            "method": "uncracked_flexure",
            "width_mm": 0.0,
            "crack_limit_mm": CRACK_LIMIT,
        }
    # On the cracked assessment section, sum the sustained and assessment-
    # only transient strain planes. Give no tension-stiffening reduction.
    k_s = (
        sustained_moment
        * 1e6
        / (long_stage["concrete_modulus_nmm2"] * long_stage["cracked_inertia_mm4"])
    )
    k_q = (
        (total_moment - sustained_moment) * 1e6 / (EC * initial["cracked_inertia_mm4"])
    )
    curvature = k_s + k_q
    x = (
        k_s * long_stage["neutral_axis_mm"] + k_q * initial["neutral_axis_mm"]
    ) / curvature
    steel_strain = curvature * (EFFECTIVE_DEPTH - x)
    surface_strain = curvature * (DEPTH - x)
    limit = 0.8 * FY / ES
    trace = {
        "crack_limit_mm": CRACK_LIMIT,
        "initial_elastic_steel_stress_nmm2": elastic_steel(total_moment, initial),
        "assessment_elastic_steel_stress_nmm2": ES * steel_strain,
        "assessment_elastic_steel_strain": steel_strain,
        "annex_f_strain_limit": limit,
    }
    if steel_strain > limit or trace["initial_elastic_steel_stress_nmm2"] > 0.8 * FY:
        return {
            **trace,
            "status": "HOLD",
            "method": "annex_f_strain_limit_exceeded",
            "width_mm": None,
        }
    points = [
        0,
        WIDTH,
        *(
            (a + b) / 2
            for a, b in zip(BAR_POSITIONS[:-1], BAR_POSITIONS[1:], strict=True)
        ),
    ]
    # Strip boundaries are periodic cell seams. Adjacent cells have the
    # same pitch, so edge and interior mid-gap checks share one bound.
    nearest = [
        min(
            math.hypot(point - bar, DEPTH - EFFECTIVE_DEPTH) - BAR_DIA / 2
            for bar in BAR_POSITIONS
        )
        for point in points
    ]
    acr = max(nearest)
    cover = DEPTH - EFFECTIVE_DEPTH - BAR_DIA / 2
    width = 3 * acr * surface_strain / (1 + 2 * (acr - cover) / (DEPTH - x))
    return {
        **trace,
        "status": "PASS" if width <= CRACK_LIMIT else "FAIL",
        "method": "annex_f_one_way_flexure",
        "width_mm": width,
        "governing_strip_position_mm": points[nearest.index(acr)],
        "surface_strain": surface_strain,
        "neutral_axis_mm": x,
        "nearest_steel_mm": acr,
        "main_bar_cover_mm": cover,
    }


def elastic_steel(moment: float, state: dict) -> float:
    return (
        ES
        * moment
        * 1e6
        * (EFFECTIVE_DEPTH - state["neutral_axis_mm"])
        / (state["concrete_modulus_nmm2"] * state["cracked_inertia_mm4"])
    )


def expected_service(span: float, witness_load: float | None = None) -> dict:
    m_total, v_total = actions(span, LOAD_TOTAL)
    m_g, v_g = actions(span, LOAD_SUSTAINED)
    initial = section(EC, m_total)
    initial_g = section(EC, m_g)
    before = stage(span, FINISH["creep_coefficient"], FINISH["shrinkage_strain"], m_g)
    final = stage(
        span, ASSESSMENT["creep_coefficient"], ASSESSMENT["shrinkage_strain"], m_g
    )
    crack = conditional_crack_width(m_total, m_g, initial, final)
    limit = span / 250
    limit_after_finishes = min(span / 350, 20)
    target_outside_elastic = initial["cracked"] and (
        elastic_steel(m_total, initial) >= FY
        or crack["assessment_elastic_steel_stress_nmm2"] >= FY
    )
    values = {
        "limit_final_mm": limit,
        "limit_after_finishes_mm": limit_after_finishes,
        "midspan_mm": span / 2,
    }
    if not target_outside_elastic:
        immediate = uniform_displacement(
            LOAD_TOTAL, span, EC, initial["effective_inertia_mm4"]
        )
        immediate_g = uniform_displacement(
            LOAD_SUSTAINED, span, EC, initial_g["effective_inertia_mm4"]
        )
        before["total_deflection_mm"] = (
            before["sustained_deflection_mm"] + before["shrinkage_deflection_mm"]
        )
        final["total_deflection_mm"] = (
            final["sustained_deflection_mm"]
            + final["shrinkage_deflection_mm"]
            + immediate
            - immediate_g
        )
        change = final["total_deflection_mm"] - before["total_deflection_mm"]
        values.update(
            status=(
                "PASS"
                if final["total_deflection_mm"] <= limit
                and change <= limit_after_finishes
                else "FAIL"
            ),
            method="annex_c_2_3_4",
            initial_total_mm=immediate,
            initial_sustained_mm=immediate_g,
            at_finishes=before,
            at_assessment=final,
            after_finishes_mm=change,
        )
    else:
        values.update(
            status="HOLD", method="outside_elastic_profile", final_deflection_mm=None
        )
        if witness_load is not None:
            witness_m, witness_v = actions(span, witness_load)
            trial = section(EC, witness_m)
            stress = elastic_steel(witness_m, trial)
            displacement = uniform_displacement(
                witness_load, span, EC, trial["effective_inertia_mm4"]
            )
            assert LOAD_SUSTAINED < witness_load < LOAD_TOTAL
            assert MCR < witness_m and stress < FY and displacement > limit
            values.update(
                status="FAIL",
                method="elastic_lower_load_exceeds_final_limit",
                elastic_witness={
                    "load_kn_per_m2": witness_load,
                    "midspan_moment_knm": witness_m,
                    "support_shear_kn": witness_v,
                    "tension_steel_stress_nmm2": stress,
                    "instantaneous_deflection_mm": displacement,
                    "effective_inertia_mm4": trial["effective_inertia_mm4"],
                },
            )
    statuses = {values["status"], crack["status"]}
    return {
        "status": (
            "FAIL" if "FAIL" in statuses else "HOLD" if "HOLD" in statuses else "PASS"
        ),
        "actions": {
            "assessment_moment_knm": m_total,
            "sustained_moment_knm": m_g,
            "assessment_support_shear_kn": v_total,
            "sustained_support_shear_kn": v_g,
        },
        "section": {
            "gross_inertia_mm4": IG,
            "cracking_moment_knm": MCR,
            "main_steel_area_mm2": AST,
            "cracked_at_assessment": initial["cracked"],
        },
        "deflection": values,
        "crack": crack,
    }


def request_for(case_id: str, span: float, witness: float | None = None) -> dict:
    member_id, revision = "B01-STRIP", f"B01-{span:g}-A1"
    reinforcement_revision = "B01-R1"
    service = {}
    for name, intensity in (("total", LOAD_TOTAL), ("sustained", LOAD_SUSTAINED)):
        moment, shear = actions(span, intensity)
        service[name] = {
            "combination_id": f"{case_id}-{name}",
            "action_row_id": f"{case_id}-{name}-MID",
            "analysis_revision": revision,
            "reinforcement_revision": reinforcement_revision,
            "uniform_area_load_kn_per_m2": intensity,
            "midspan_moment_knm": moment,
            "support_shear_kn": shear,
        }
    return {
        "identity": {"family_id": "slab", "case_id": case_id, "member_id": member_id},
        "analysis_revision": revision,
        "reinforcement_revision": reinforcement_revision,
        "effective_span_mm": span,
        "transverse_panel_span_mm": 7500,
        "support_edges": {
            "x_min": "simple",
            "x_max": "simple",
            "y_min": "free",
            "y_max": "free",
        },
        "section": {
            "strip_width_mm": WIDTH,
            "thickness_mm": DEPTH,
            "nominal_cover_mm": 20,
            "fck_nmm2": FCK,
            "fy_nmm2": FY,
            "maximum_aggregate_mm": 20,
            "main_pitch_mm": 250,
            "main_bars": [
                {
                    "bar_id": f"M{number}",
                    "x_from_left_mm": position,
                    "y_from_top_mm": EFFECTIVE_DEPTH,
                    "diameter_mm": BAR_DIA,
                }
                for number, position in enumerate(BAR_POSITIONS, 1)
            ],
            "distribution": {"pitch_mm": 250, "diameter_mm": 8, "y_from_top_mm": 116},
        },
        "service_loads": service,
        "history": {
            "loading_age_days": 28,
            "finishes": FINISH,
            "assessment": ASSESSMENT,
            "finish_added_load_kn_per_m2": 0,
            "relative_humidity_percent": 60,
            "notional_size_mm": 150,
            "axial_restraint": "free_shortening",
            "shrinkage_basis": "uniform_through_depth",
            "source_reference": "Prescribed finite-age input worksheet with a single gravity UDL sustained through finishes.",
        },
        "exposure": "mild",
        "crack_width_limit_mm": CRACK_LIMIT,
        "elastic_witness_load_kn_per_m2": witness,
        "source_reference": "B01 periodic tributary strip, one-way action from two verified supported edges.",
    }


def fixture():
    b01 = request_for("B01-3000", 3000)
    longer = request_for("B01-4500", 4500, 5.25)
    cracked = request_for("B01-3680", 3680)
    geometry = b01["section"]
    distribution = geometry["distribution"]
    minimum_area = 0.0012 * WIDTH * DEPTH
    assert AST > minimum_area
    assert (
        math.pi
        * distribution["diameter_mm"] ** 2
        / 4
        * WIDTH
        / distribution["pitch_mm"]
        > minimum_area
    )
    assert DEPTH - EFFECTIVE_DEPTH - BAR_DIA / 2 == geometry["nominal_cover_mm"]
    assert (
        EFFECTIVE_DEPTH - BAR_DIA / 2
        == distribution["y_from_top_mm"] + distribution["diameter_mm"] / 2
    )
    assert 250 - BAR_DIA >= geometry["maximum_aggregate_mm"] + 5
    cases = {}
    for name, request, status, crack_status in (
        ("b01_service_history", b01, "PASS", "PASS"),
        ("cracked_width_control", cracked, "PASS", "PASS"),
        ("longer_span", longer, "FAIL", "HOLD"),
    ):
        expected = expected_service(
            request["effective_span_mm"], request["elastic_witness_load_kn_per_m2"]
        )
        assert (
            expected["status"] == status and expected["crack"]["status"] == crack_status
        )
        cases[name] = {"request": request, "expected": expected}
    assert cases["b01_service_history"]["expected"]["crack"]["width_mm"] == 0
    assert (
        0
        < cases["cracked_width_control"]["expected"]["crack"]["width_mm"]
        <= CRACK_LIMIT
    )

    no_witness = deepcopy(longer)
    no_witness["identity"]["case_id"] = "B01-4500-NO-WITNESS"
    no_witness["elastic_witness_load_kn_per_m2"] = None
    held_service = expected_service(4500)
    assert held_service["status"] == "HOLD"
    assert held_service["deflection"]["final_deflection_mm"] is None
    assert held_service["crack"]["width_mm"] is None
    cases["longer_span_without_witness"] = {
        "request": no_witness,
        "expected": held_service,
    }
    missing = deepcopy(b01)
    del missing["history"]
    stale = deepcopy(b01)
    stale["service_loads"]["sustained"]["reinforcement_revision"] = "B01-R0"
    unknown_topology = deepcopy(longer)
    del unknown_topology["support_edges"]
    for name, request, issue in (
        ("missing_history", missing, "SLAB.SERVICE_HISTORY_HELD"),
        ("stale_reinforcement", stale, "SLAB.SERVICE_REVISION_STALE"),
        ("missing_support_evidence", unknown_topology, "SLAB.SERVICE_SUPPORT_HELD"),
    ):
        cases[name] = {
            "request": request,
            "expected": {"status": "HOLD", "issue": issue},
        }

    # Preserve the separate installed B01 ultimate benchmark as a regression.
    moment, _ = actions(3000, 10)
    axial_factor = 0.36 * FCK * WIDTH
    c = moment * 1e6 / axial_factor
    x = (EFFECTIVE_DEPTH - math.sqrt(EFFECTIVE_DEPTH**2 - 4 * 0.42 * c)) / (2 * 0.42)
    steel = axial_factor * x / (0.87 * FY)
    assert abs(steel - 260.72663042521697) < 1e-8
    return {
        "fixture_version": "library-030-serv03-b01-service/v1",
        "sources": [
            "B01 public provided-bar replay in Python/tests/integration/test_api_entrypoints_is456.py",
            "IS 456:2000 Cl. 23.2, Cl. 24.1, Annex C-2, C-3, C-4 and Annex F",
            "Direct one-way strip adaptation using verified two-edge support and prescribed finite-age evidence",
        ],
        "published_b01_ultimate_control": {
            "effective_span_mm": 3000,
            "factored_area_load_kn_per_m2": 10,
            "moment_knm_per_m": moment,
            "required_main_steel_mm2_per_m": steel,
        },
        "cases": cases,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    payload = json.dumps(fixture(), indent=2, allow_nan=False) + "\n"
    if args.write:
        FIXTURE.write_text(payload, encoding="utf-8")
    else:
        assert payload == FIXTURE.read_text(
            encoding="utf-8"
        ), "Independent reference drift"
    print("Reproduced SERV03 B01 two PASS, one FAIL and four HOLD cases.")
