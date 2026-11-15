"""Regenerate frozen SL06 S1 targets from IS 456 and the documented B02/B04 inputs."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

TARGET = Path(__file__).with_name("library-030-sl06-actions.json")
BASE = "67b8f879c88cc2d4e3c11b46afc2671da1e90e7e"
FCK, FY, WIDTH_MM = 20, 415, 1000


def ratio(demand, limit):
    value = demand / limit
    return {
        "demand": demand,
        "limit": limit,
        "utilization": value,
        "status": "PASS" if value <= 1 else "FAIL",
    }


def provided(diameter, spacing):
    return math.pi * diameter**2 * WIDTH_MM / (4 * spacing)


def flexure(moment, depth):
    # IS 456 cl. 38.1. Solve M = C(d - 0.42 x) with C = 0.36 fck b x.
    absolute_moment = abs(moment)
    x_limit = 0.48 * depth
    limiting_moment = 0.36 * FCK * WIDTH_MM * x_limit * (depth - 0.42 * x_limit) / 1e6
    moment_term = absolute_moment * 1e6 / (0.36 * FCK * WIDTH_MM)
    neutral_axis = 2 * moment_term / (depth + math.sqrt(depth**2 - 1.68 * moment_term))
    area = 0.36 * FCK * WIDTH_MM * neutral_axis / (0.87 * FY)
    return area, neutral_axis, ratio(absolute_moment, limiting_moment)


def bars(area, height, depth, diameter, spacing, *, distribution=False):
    minimum = 0.0012 * WIDTH_MM * height
    # Amendment 3 to cl. 26.3.3(b)(2) retains the 300 mm cap for distribution bars.
    spacing_limit = min((5 if distribution else 3) * depth, 300)
    return {
        "area": ratio(max(area, minimum), provided(diameter, spacing)),
        "diameter": ratio(diameter, height / 8),
        "spacing": ratio(spacing, spacing_limit),
    }


def shear(v_kn_m, depth, height, continuing_area):
    # M20 Table 19 bracket from 0.15 to 0.25 percent. The B02/B04
    # references stay within this interval. Both use unit-width strips.
    steel_percent = 100 * continuing_area / (WIDTH_MM * depth)
    assert 0.15 <= steel_percent <= 0.25
    tau_c = 0.28 + (steel_percent - 0.15) * (0.36 - 0.28) / (0.25 - 0.15)
    assert 140 <= height <= 175
    factor = 1.30 if height <= 150 else 1.30 + (height - 150) * (1.25 - 1.30) / 25
    nominal = v_kn_m * 1000 / (WIDTH_MM * depth)
    concrete = factor * tau_c
    maximum = 2.8 / 2  # Table 20 M20 and Amendment 5 to cl. 40.2.3.1.
    return ratio(nominal, min(concrete, maximum)), {
        "steel_percent": steel_percent,
        "base_tau_c_n_per_mm2": tau_c,
        "depth_factor": factor,
        "design_tau_c_n_per_mm2": concrete,
        "maximum_tau_n_per_mm2": maximum,
    }


def row_actions(q, span_m, moment_coefficients, shear_coefficient, depth_by_region):
    moments = {
        region: coefficient * q * span_m**2
        for region, coefficient in moment_coefficients.items()
    }
    steel = {}
    checks = {}
    for region, moment in moments.items():
        area, x, check = flexure(moment, depth_by_region[region])
        steel[region] = {
            "required_for_moment_mm2_per_m": area,
            "neutral_axis_depth_mm": x,
        }
        checks[f"{region}.section_flexure"] = check
    return (
        {
            "signed_moments_knm_per_m": moments,
            "support_shear_magnitude_kn_per_m": q * shear_coefficient * span_m,
        },
        steel,
        checks,
    )


def b02(q):
    actions, steel, checks = row_actions(
        q,
        3,
        {"positive_midspan": 1 / 12, "negative_support": -1 / 10},
        0.4,
        {"positive_midspan": 115, "negative_support": 115},
    )
    for region, diameter, spacing in (
        ("positive_midspan", 8, 180),
        ("negative_support", 10, 230),
        ("distribution", 8, 250),
    ):
        area = steel.get(region, {}).get("required_for_moment_mm2_per_m", 0)
        checks.update(
            {
                f"{region}.{key}": value
                for key, value in bars(
                    area,
                    140,
                    115,
                    diameter,
                    spacing,
                    distribution=region == "distribution",
                ).items()
            }
        )
    checks["support_shear"], shear_basis = shear(
        actions["support_shear_magnitude_kn_per_m"],
        115,
        140,
        min(provided(8, 180), provided(10, 230)),
    )
    checks["reviewed_span_depth"] = ratio(3000 / 115, 23 * 1.18)
    return {
        "actions": actions,
        "flexure": steel,
        "shear_basis": shear_basis,
        "checks": checks,
    }


def b04(q):
    actions, steel, checks = row_actions(
        q,
        4,
        {
            "x_negative": -0.075,
            "x_positive": 0.056,
            "y_negative": -0.047,
            "y_positive": 0.035,
        },
        0.5,
        {"x_negative": 135, "x_positive": 135, "y_negative": 125, "y_positive": 125},
    )
    for region, depth, diameter, spacing in (
        ("x_negative", 135, 10, 200),
        ("x_positive", 135, 10, 200),
        ("y_negative", 125, 8, 200),
        ("y_positive", 125, 8, 200),
        ("edge_strips", 125, 8, 250),
    ):
        area = steel.get(region, {}).get("required_for_moment_mm2_per_m", 0)
        checks.update(
            {
                f"{region}.{key}": value
                for key, value in bars(
                    area,
                    160,
                    depth,
                    diameter,
                    spacing,
                    distribution=region == "edge_strips",
                ).items()
            }
        )
    # Annex D D-1.8 to D-1.10. Corner class depends on the adjacent edges.
    peak_positive_area = max(
        steel[key]["required_for_moment_mm2_per_m"]
        for key in ("x_positive", "y_positive")
    )
    corners = {
        "x_min_y_min": ("full", 3 / 4),
        "x_min_y_max": ("half", 3 / 8),
        "x_max_y_min": ("half", 3 / 8),
        "x_max_y_max": ("none", 0),
    }
    for corner, (_, factor) in corners.items():
        checks[f"{corner}.torsion_area_per_layer"] = (
            ratio(factor * peak_positive_area, provided(8, 200))
            if factor
            else {
                "demand": 0,
                "limit": provided(8, 200),
                "utilization": None,
                "status": "NOT_APPLICABLE",
            }
        )
    checks["support_shear"], shear_basis = shear(
        actions["support_shear_magnitude_kn_per_m"],
        125,
        160,
        min(provided(10, 200), provided(8, 200)),
    )
    checks["reviewed_span_depth"] = ratio(4000 / 125, 30)
    return {
        "actions": actions,
        "flexure": steel,
        "shear_basis": shear_basis,
        "checks": checks,
        "corner_classes": {corner: kind for corner, (kind, _) in corners.items()},
        "corner_zone_mm": 4000 / 5,
        "strip_widths_mm": {
            "x_middle": 4500,
            "x_each_edge": 750,
            "y_middle": 3000,
            "y_each_edge": 500,
        },
    }


def service_basis(case, base, factor):
    return {
        "reviewed_base_span_depth_limit": base,
        "reviewed_aggregate_modification_factor": factor,
        "serviceability_limit_source_reference": f"NPTEL-{case}-SLS",
        "serviceability_limit_source_is_approved": True,
        "qualified_serviceability_acceptance_reference": f"example-review:{case}-SLS",
        "qualified_serviceability_acceptance_acknowledged": True,
    }


def external_basis(case, coefficients):
    return {
        **coefficients,
        "coefficient_source_reference": f"NPTEL-{case}",
        "coefficient_source_is_approved": True,
        "qualified_coefficient_acceptance_reference": f"example-review:{case}",
        "qualified_coefficient_acceptance_acknowledged": True,
    }


def steel_input(**regions):
    return {
        f"{region}_bar_{name}_mm": value
        for region, (diameter, spacing) in regions.items()
        for name, value in (("diameter", diameter), ("spacing", spacing))
    }


def specimen(case, loads, calculate, geometry, reinforcement, service, routes):
    rows = {
        row_id: {
            "input": {"row_id": row_id, "factored_area_load_kn_per_m2": q},
            "expected": calculate(q),
        }
        for row_id, q in zip(("A", "B"), loads, strict=True)
    }
    for row in rows.values():
        checks = row["expected"]["checks"]
        row["expected"]["uls_status"] = (
            "FAIL"
            if any(
                value["status"] == "FAIL"
                for key, value in checks.items()
                if key != "reviewed_span_depth"
            )
            else "PASS"
        )
        row["expected"]["reviewed_service_status"] = checks["reviewed_span_depth"][
            "status"
        ]
    # Identical ratios select A. For these admitted descriptors a failing check
    # has a ratio above unity and outranks the corresponding passing check.
    a, b = (row["expected"]["checks"] for row in rows.values())
    assert a.keys() == b.keys()
    governing = {}
    for key, check_a in a.items():
        check_b = b[key]
        if check_a["status"] == check_b["status"] == "NOT_APPLICABLE":
            governing[key] = None
            continue
        governing[key] = "B" if check_b["utilization"] > check_a["utilization"] else "A"
    available_a = {
        key: "A" if value["utilization"] is not None else None
        for key, value in a.items()
    }
    failures = {
        row_id: [
            key
            for key, value in row["expected"]["checks"].items()
            if value["status"] == "FAIL"
        ]
        for row_id, row in rows.items()
    }
    uls = (
        "FAIL"
        if any(row["expected"]["uls_status"] == "FAIL" for row in rows.values())
        else "PASS"
    )
    service_status = a["reviewed_span_depth"]["status"]
    assert service_status == b["reviewed_span_depth"]["status"]
    overall = "FAIL" if "FAIL" in (uls, service_status) else "PASS"
    available_a_uls = rows["A"]["expected"]["uls_status"]
    absent_b_overall = "FAIL" if "FAIL" in (available_a_uls, service_status) else "HOLD"
    return {
        "geometry_revision": f"{case}-geometry/v1",
        "reinforcement_revision": f"{case}-reinforcement/v1",
        "geometry_material_and_support_inputs": geometry,
        "reinforcement_inputs": reinforcement,
        "shared_reviewed_service_basis": service,
        "coefficient_routes": routes,
        "required_row_ids": ["A", "B"],
        "rows": rows,
        "expected_governing_ids": governing,
        "expected_status": {
            "coverage": "COMPLETE",
            "uls": uls,
            "reviewed_service": service_status,
            "engineering": overall,
            "failed_checks_by_row": failures,
        },
        "controls": {
            "reordered": {
                "input_order": ["B", "A"],
                "expected_governing_ids": governing,
                "coverage": "COMPLETE",
            },
            "exact_tie": {
                "input_order": ["B", "A"],
                "replace_B_load_with_A_load": True,
                "expected_governing_ids": available_a,
                "coverage": "COMPLETE",
            },
            "duplicate_id": {
                "input_order": ["A", "A", "B"],
                "intake": "REJECT_DUPLICATE_ID",
            },
            "missing_B": {
                "input_order": ["A"],
                "coverage": "HOLD",
                "missing_required_row_ids": ["B"],
                "available_governing_ids": available_a,
                "available_uls": available_a_uls,
                "available_reviewed_service": service_status,
                "engineering": absent_b_overall,
                "evaluated_A_retained": True,
            },
            "missing_shared_service_basis": {
                "input_order": ["A", "B"],
                "set_shared_service_basis_to_null": True,
                "uls": uls,
                "reviewed_service": "HOLD",
                "engineering": "FAIL" if uls == "FAIL" else "HOLD",
                "expected_governing_ids": {**governing, "reviewed_span_depth": None},
                "strength_failures_retained": uls == "FAIL",
            },
        },
    }


def build():
    b02_geometry = {
        "short_effective_span_mm": 3000,
        "long_effective_span_mm": 7500,
        "thickness_mm": 140,
        "d_mm": 115,
        "fck_n_per_mm2": FCK,
        "fy_n_per_mm2": FY,
        "number_of_spans": 3,
        "maximum_span_variation_percent": 0,
        "uniform_cross_section_acknowledged": True,
        "substantially_uniform_load_acknowledged": True,
        "redistribution_applied": False,
    }
    b04_geometry = {
        "x_effective_span_mm": 4000,
        "y_effective_span_mm": 6000,
        "thickness_mm": 160,
        "d_x_mm": 135,
        "d_y_mm": 125,
        "fck_n_per_mm2": FCK,
        "fy_n_per_mm2": FY,
        "x_min_edge": "discontinuous",
        "x_max_edge": "continuous",
        "y_min_edge": "discontinuous",
        "y_max_edge": "continuous",
        "corner_lift_condition": "restrained",
    }
    return {
        "fixture_version": "library-030-sl06-actions/v1",
        "reference_base_commit": BASE,
        "sources": {
            "code": "IS 456:2000 cl. 26.5.2, 38.1, 40.1 and 40.2, Tables 12/13/19/20/26 and Annex D",
            "primary_mirror": "https://www.cracindia.in/admin/uploads/IS-456.pdf",
            "amendments": [
                "Amendment 3 (August 2007), cl. 26.3.3(b)(2), 300 mm cap for slab distribution bars",
                "Amendment 5 (July 2019), cl. 40.2.3.1, half of Table 20 for solid slabs",
            ],
            "amendments_mirror": "https://nfrlyconstruction.org/uploads/File/Codes/17072023-23_147_IS-456-with-all-ammendments.pdf_504314034.pdf",
            "admitted_input_basis": "SLAB-B02 and SLAB-B04 in is456-slab-evidence.md and Python/examples/slab_coefficient_references.py",
        },
        "absolute_tolerances": {
            "actions_knm_per_m_or_kn_per_m": 1e-10,
            "reinforcement_mm2_per_m": 1e-3,
            "stress_n_per_mm2": 1e-9,
            "length_mm": 1e-8,
            "utilization": 1e-9,
        },
        "check_definitions": {
            "section_flexure": "abs(Mu) / limiting moment for the direction",
            "area": "governing required area / provided steel area",
            "diameter": "provided diameter / maximum diameter",
            "spacing": "provided spacing / maximum spacing",
            "torsion_area_per_layer": "required area / provided area in each of four layers, only where applicable",
            "support_shear": "nominal shear stress / min(depth-adjusted concrete design shear stress, amended maximum)",
            "reviewed_span_depth": "actual span/depth / reviewed modified span/depth limit",
        },
        "service_scope": "Reviewed span/depth only. Direct deflection and crack-width acceptance remain in SERV03.",
        "tie_rule": "Highest unrounded utilization per check among evaluated failures if present, otherwise among passes. Lexical ID on exact ties. Preserve incomplete coverage and every conclusive failure.",
        "row_binding": "Materialize each row with the common geometry, reinforcement, selected coefficient route and shared service basis. For all-fixed B02 built-in, pass that row's UDL as fixed.",
        "specimens": {
            "B02": specimen(
                "B02",
                (10, 14.25),
                b02,
                b02_geometry,
                steel_input(
                    positive=(8, 180), negative=(10, 230), distribution=(8, 250)
                ),
                service_basis("L18-B02", 23, 1.18),
                {
                    "external": {
                        "entry_point": "design_continuous_one_way_slab_is456",
                        "inputs": external_basis(
                            "L18-B02",
                            {
                                "positive_moment_coefficient": 1 / 12,
                                "negative_moment_coefficient": 1 / 10,
                                "shear_coefficient": 0.4,
                            },
                        ),
                        "load_argument": "factored_area_load_kn_per_m2",
                        "verified_by_library": False,
                    },
                    "builtin": {
                        "entry_point": "design_continuous_one_way_slab_builtin_is456",
                        "table_id": "IS456_TABLE_12_13",
                        "inputs": {
                            "factored_nonfixed_imposed_load_kn_per_m2": 0,
                            "positive_location": "end_span_positive",
                            "negative_location": "next_to_end_support_negative",
                            "shear_location": "end_support",
                        },
                        "load_argument": "factored_dead_and_fixed_imposed_load_kn_per_m2",
                        "verified_by_library": True,
                    },
                },
            ),
            "B04": specimen(
                "B04",
                (12, 15.5),
                b04,
                b04_geometry,
                steel_input(
                    x_positive=(10, 200),
                    x_negative=(10, 200),
                    y_positive=(8, 200),
                    y_negative=(8, 200),
                    edge_strip=(8, 250),
                    torsion=(8, 200),
                ),
                service_basis("L19-B04", 30, 1),
                {
                    "external": {
                        "entry_point": "design_two_way_slab_panel_is456",
                        "inputs": external_basis(
                            "L19-B04",
                            {
                                "support_topology_kind": "two_adjacent_edges_discontinuous",
                                "alpha_x_negative": 0.075,
                                "alpha_x_positive": 0.056,
                                "alpha_y_negative": 0.047,
                                "alpha_y_positive": 0.035,
                            },
                        ),
                        "load_argument": "factored_area_load_kn_per_m2",
                        "verified_by_library": False,
                    },
                    "builtin": {
                        "entry_point": "design_two_way_slab_panel_builtin_is456",
                        "table_id": "IS456_TABLE_26",
                        "case_id": "table_26_case_4",
                        "inputs": {},
                        "load_argument": "factored_area_load_kn_per_m2",
                        "verified_by_library": True,
                    },
                },
            ),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    expected = build()
    if args.freeze:
        TARGET.write_text(
            json.dumps(expected, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
    else:
        assert json.loads(TARGET.read_text(encoding="utf-8")) == expected
    print("Independent SL06 reference: B02 and B04, two rows and five controls each")


if __name__ == "__main__":
    main()
