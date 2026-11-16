"""Freeze the independent four-direction DUCT01 interior-joint reference."""

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

from _duct01_cage_reference import area, cage
from _duct01_section_reference import _concrete_stress, rectangular_section
from check_library_029_beam_sections_reference import stress
from check_library_029_flow02_reference import TABLE_19_M30

TARGET = Path(__file__).with_name("library-030-duct01-interior-joint.json")
DIRECTIONS = ("X+", "X-", "Y+", "Y-")
AXIAL = ((550, 640), (620, 710), (690, 815), (745, 865))
BEAM_ENDS = ("minus", "plus")
COLUMN_ENDS = ("upper", "lower")


def specimen():
    return {
        "joint_id": "J1",
        "continuity": "Interior, non-roof. Centred beams on four faces, no participating slab steel.",
        "action_revision": "DUCT01-DECLARED-R1",
        "cage_action_revision": "DUCT01-DECLARED-R1",
        "beam_width_mm": 450,
        "column_width_mm": 550,
        "joint_depth_mm": 600,
        "column_clear_heights_mm": {"upper": 3400, "lower": 3600},
        "beam_clear_spans_mm": {
            "X": {"minus": 4000, "plus": 4200},
            "Y": {"minus": 4100, "plus": 4300},
        },
        "beam_dead_plus_live_kn_m": {
            "X": {"minus": 30, "plus": 32},
            "Y": {"minus": 29, "plus": 31},
        },
        "mechanism_inflection_offsets_mm": {"upper": 1700, "lower": 1800},
        "column_fck_mpa": 30,
        "beam_fck_mpa": 30,
        "joint_fck_mpa": 30,
        "longitudinal_fy_mpa": 500,
        "link_fy_mpa": 415,
        "longitudinal_grade": "Fe500D",
        "transverse_grade": "Fe415D",
        "column_bar_mm": 32,
        "column_bar_edge_mm": 79,
        "beam_bar_mm": 25,
        "beam_axis_across_column_mm": [115, 220, 330, 435],
        "beam_row_depth_from_top_mm": {"X": 62, "Y": 105},
        "beam_uninterrupted_development_mm": 1400,
        "beam_link_mm": 10,
        "beam_link_centre_radius_mm": 28,
        "beam_link_seat_inset_mm": 23,
        "beam_first_link_mm": 30,
        "beam_inner_link_offset_mm": 16,
        "beam_pitch_mm": 75,
        "column_cover_mm": 45,
        "column_link_mm": 12,
        "column_link_centre_radius_mm": 32,
        "column_hook_tail_mm": 120,
        "column_hook_rise_mm": 18,
        "column_hook_ramp_length_mm": 60,
        "cross_tie_station_offset_mm": 18,
        "joint_hoop_centres_mm": [18, 149, 249, 349, 443, 582],
        "column_first_end_hoop_mm": 35,
        "column_end_pitch_mm": 65,
        "column_end_confinement_length_mm": 600,
        "required_beam_cover_mm": 30,
        "required_column_cover_mm": 40,
        "aggregate_max_mm": 20,
        "axis_tolerance_mm": 1,
        "tie_station_tolerance_mm": 1,
        "diameter_overage_mm": 0.5,
        "compaction_head_mm": 40,
        "assembly": "Jig the column cage. Thread the lower X and Y rows through their clear corridors, then the upper rows. Keep the two orthogonal row levels distinct. Fit the staggered beam links outside the joint face. Use the central vertical corridor for compaction before closing the forms.",
        "directions": {
            direction: [
                {
                    "combination_id": f"EQ-{direction}-{index + 1}",
                    "upper_axial_compression_kn": axial,
                    "beam_on_joint_downward_shear_kn": {
                        "minus": 45 + 6 * index + 4 * counter,
                        "plus": -17 + 5 * index - 3 * counter,
                    },
                    "analysis_column_shear_magnitude_kn": 150
                    + 7 * index
                    + 12 * counter,
                }
                for index, axial in enumerate(axials)
            ]
            for counter, (direction, axials) in enumerate(
                zip(DIRECTIONS, AXIAL, strict=True)
            )
        },
    }


def beam_mechanism(request, bar_depth):
    """Satisfy horizontal force balance at 1.25fy before taking the moment."""
    fck = request["beam_fck_mpa"]
    fy = request["longitudinal_fy_mpa"]
    beam_width = request["beam_width_mm"]
    depth = request["joint_depth_mm"]
    steel = len(request["beam_axis_across_column_mm"]) * area(request["beam_bar_mm"])
    tension = 1.25 * fy * steel

    def compression(axis):
        strain = max(0.0035 * (1 - bar_depth / axis), 0)
        steel_n = (stress(strain, fy) - _concrete_stress(strain, fck)) * steel
        return 0.36 * fck * beam_width * axis, steel_n

    low, high = 1e-6, depth - bar_depth
    assert sum(compression(low)) < tension < sum(compression(high))
    for _ in range(100):
        axis = (low + high) / 2
        if sum(compression(axis)) < tension:
            low = axis
        else:
            high = axis
    axis = (low + high) / 2
    concrete, compressed_bars = compression(axis)
    assert abs(concrete + compressed_bars - tension) < 1e-6
    lever = depth - bar_depth
    return {
        "tension_kn": tension / 1000,
        "concrete_compression_kn": concrete / 1000,
        "net_steel_compression_kn": compressed_bars / 1000,
        "neutral_axis_mm": axis,
        "moment_knm": (
            concrete * (lever - 0.42 * axis) + compressed_bars * (lever - bar_depth)
        )
        / 1e6,
    }


def shear_capacity(d, b, tie_dia, pitch, link_fy, concrete_kn):
    effective_legs = 2
    asv = effective_legs * area(tie_dia)
    steel = 0.87 * min(link_fy, 415) * asv * d / (1000 * pitch)
    crushing = 3.5 * b * d / 1000  # IS 456 Table 20, M30.
    return min(steel + concrete_kn, crushing), steel, crushing


def gravity_reactions(request, plane, sign, hinge_moment, factor):
    # The minus beam terminates at B, the plus beam starts at A. From
    # dM/dx = V, a positive sway adds a reaction at B and removes it at A.
    reactions = {}
    for side in BEAM_ENDS:
        span = request["beam_clear_spans_mm"][plane][side] / 1000
        gravity = 1.2 * request["beam_dead_plus_live_kn_m"][plane][side] * span / 2
        hinge_increment = 2 * factor * hinge_moment / span
        reactions[side] = (
            gravity + (sign if side == "minus" else -sign) * hinge_increment
        )
    return reactions


def joint_actions(request, direction, beam, mechanism, confinement, column_rows):
    plane = direction[0]
    sign = 1 if direction.endswith("+") else -1
    width = request["column_width_mm"]
    height = request["joint_depth_mm"]
    fck = request["column_fck_mpa"]
    phi = request["column_bar_mm"]
    beam_phi = request["beam_bar_mm"]
    link_fy = request["link_fy_mpa"]
    col_d = width - request["column_bar_edge_mm"]
    beam_d = height - request["beam_row_depth_from_top_mm"][plane]
    b = request["beam_width_mm"]
    beam_pitch = request["beam_pitch_mm"] + 2 * request["tie_station_tolerance_mm"]
    beam_limit = min(beam_d / 4, 6 * beam_phi, 100)
    first_link = (
        request["beam_first_link_mm"]
        + request["beam_inner_link_offset_mm"]
        + request["tie_station_tolerance_mm"]
    )
    beam_capacity, beam_vus, beam_crush = shear_capacity(
        beam_d, b, request["beam_link_mm"], beam_pitch, link_fy, 0.0
    )
    hinge_moment = beam["moment_knm"]
    hinge_reactions = gravity_reactions(request, plane, sign, hinge_moment, 1.4)
    mechanism_reactions = gravity_reactions(
        request, plane, sign, mechanism["moment_knm"], 1.0
    )
    # Free-body about the column centre, bounded at upper/lower inflections.
    # Positive downward beam forces on opposite faces give opposite moment terms.
    shear_arm = (
        sum(request["mechanism_inflection_offsets_mm"].values()) + height
    ) / 1000
    moment_from_reactions = (
        sign
        * (mechanism_reactions["minus"] - mechanism_reactions["plus"])
        * width
        / 2000
    )
    column_mechanism_shear = (
        2 * mechanism["moment_knm"] + moment_from_reactions
    ) / shear_arm
    joint_v = 2 * mechanism["tension_kn"] - column_mechanism_shear
    effective_breadth = min(width, b + 0.5 * width)
    effective_area = effective_breadth * width
    joint_tau = 1000 * joint_v / effective_area
    joint_strength = (1.5 if confinement["confined_faces"] == 4 else 1.0) * math.sqrt(
        request["joint_fck_mpa"]
    )
    # M30 Table 19 lower-bound 0.15% row. Each specimen provides at least that
    # ratio on its tension face. §40.2.2 axial factor is evaluated per row.
    pct = 100 * 3 * area(phi) / (width * col_d)
    tc = TABLE_19_M30[0][1]
    assert pct >= TABLE_19_M30[0][0]
    rows = []
    for action in request["directions"][direction]:
        combo = action["combination_id"]
        vertical = action["beam_on_joint_downward_shear_kn"]
        pu_above = action["upper_axial_compression_kn"]
        axial = {"upper": pu_above, "lower": pu_above + sum(vertical.values())}
        assert min(axial.values()) > 0
        beam_shears = {}
        for side in BEAM_ENDS:
            demand = max(abs(vertical[side]), abs(hinge_reactions[side]))
            beam_shears[side] = {
                "signed_near_hinge_moment_knm": (-sign if side == "minus" else sign)
                * hinge_moment,
                "analysis_downward_reaction_kn": vertical[side],
                "capacity_downward_reaction_kn": hinge_reactions[side],
                "demand_kn": demand,
                "steel_capacity_kn": beam_vus,
                "concrete_crushing_cap_kn": beam_crush,
                "accepted_capacity_kn": beam_capacity,
                "pitch_mm": beam_pitch,
                "pitch_limit_mm": beam_limit,
                "utilization": demand / beam_capacity,
                "pass": demand <= beam_capacity
                and beam_pitch <= beam_limit
                and first_link <= 50,
            }
        column_shears = {}
        for end, pu in axial.items():
            multiplier = min(1.5, 1 + 3000 * pu / (width**2 * fck))
            vc = tc * multiplier * width * col_d / 1000
            col_pitch = confinement["end_pitch_mm"]
            capacity, steel, crushing = shear_capacity(
                col_d, width, request["column_link_mm"], col_pitch, link_fy, vc
            )
            hinge = (
                2 * 1.4 * hinge_moment * 1000 / request["column_clear_heights_mm"][end]
            )
            elastic = action["analysis_column_shear_magnitude_kn"]
            demand = max(elastic, hinge)
            column_shears[end] = {
                "signed_analysis_shear_kn": sign * elastic,
                "signed_capacity_shear_kn": sign * hinge,
                "concurrent_axial_compression_kn": pu,
                "axial_shear_multiplier": multiplier,
                "concrete_capacity_kn": vc,
                "steel_capacity_kn": steel,
                "concrete_crushing_cap_kn": crushing,
                "demand_kn": demand,
                "accepted_capacity_kn": capacity,
                "utilization": demand / capacity,
                "pass": demand <= capacity,
            }
        rows.append(
            {
                "combination_id": combo,
                "column_axial_compression_kn": axial,
                "signed_axial_balance_residual_kn": axial["lower"]
                - axial["upper"]
                - sum(vertical.values()),
                "maximum_axial_stress_mpa": 1000 * max(axial.values()) / width**2,
                "beam_capacity_shear": beam_shears,
                "column_capacity_shear": column_shears,
            }
        )
    columns = {
        end: min(column_rows[end], key=lambda item: item["moment_knm"])
        for end in COLUMN_ENDS
    }
    ratio = (
        1.4 * 2 * hinge_moment / sum(item["moment_knm"] for item in columns.values())
    )
    return {
        "rows": rows,
        "scwb": {
            "beam_capacity_direction": direction,
            "column_capacity_direction": f"{plane}{'-' if sign > 0 else '+'}",
            "required_column_capacity_knm": 1.4 * 2 * hinge_moment,
            "available_column_capacity_knm": sum(
                item["moment_knm"] for item in columns.values()
            ),
            "governing_column_combination_ids": {
                end: result["combination_id"] for end, result in columns.items()
            },
            "utilization": ratio,
            "pass": ratio <= 1,
        },
        "joint_shear": {
            "design_beam_tension_kn_each": mechanism["tension_kn"],
            "mechanism_beam_reactions_kn": mechanism_reactions,
            "reaction_moment_about_centre_knm": moment_from_reactions,
            "column_inflection_force_couple_arm_mm": 1000 * shear_arm,
            "signed_compatible_column_shear_kn": sign * column_mechanism_shear,
            "signed_joint_shear_kn": sign * joint_v,
            "effective_breadth_mm": effective_breadth,
            "effective_area_mm2": effective_area,
            "stress_mpa": joint_tau,
            "strength_mpa": joint_strength,
            "utilization": joint_tau / joint_strength,
            "pass": joint_tau <= joint_strength,
        },
    }


def evaluate(request):
    if set(request["directions"]) != set(DIRECTIONS):
        return {"status": "HOLD", "reason": "required_direction_missing"}
    if request["cage_action_revision"] != request["action_revision"]:
        return {"status": "HOLD", "reason": "stale_action_revision"}
    if request["mechanism_inflection_offsets_mm"] is None:
        return {"status": "HOLD", "reason": "compatible_capacity_mechanism_missing"}
    if request["compaction_head_mm"] is None:
        return {"status": "HOLD", "reason": "compaction_basis_missing"}

    placement = cage(request)
    phi = request["beam_bar_mm"]
    depth = request["joint_depth_mm"]
    width = request["column_width_mm"]
    steel_count = len(request["beam_axis_across_column_mm"])
    call = (
        request["beam_width_mm"],
        depth,
        request["beam_fck_mpa"],
        request["longitudinal_fy_mpa"],
    )
    beams = {
        plane: rectangular_section(
            *call, ((z, steel_count, phi), (depth - z, steel_count, phi))
        )
        for plane, z in request["beam_row_depth_from_top_mm"].items()
    }
    mechanisms = {
        plane: beam_mechanism(request, z)
        for plane, z in request["beam_row_depth_from_top_mm"].items()
    }
    col_phi = request["column_bar_mm"]
    edge = request["column_bar_edge_mm"]
    col_layers = (
        (edge, 3, col_phi),
        (width / 2, 2, col_phi),
        (width - edge, 3, col_phi),
    )
    columns = {end: [] for end in COLUMN_ENDS}
    for actions in request["directions"].values():
        for action in actions:
            upper = action["upper_axial_compression_kn"]
            lower = upper + sum(action["beam_on_joint_downward_shear_kn"].values())
            for end, pu in zip(COLUMN_ENDS, (upper, lower), strict=True):
                result = rectangular_section(
                    width,
                    width,
                    request["column_fck_mpa"],
                    request["longitudinal_fy_mpa"],
                    col_layers,
                    pu,
                )
                columns[end].append(
                    {"combination_id": action["combination_id"], **result}
                )
    directions = {
        direction: joint_actions(
            request,
            direction,
            beams[direction[0]],
            mechanisms[direction[0]],
            placement["confinement"],
            columns,
        )
        for direction in DIRECTIONS
    }
    bond_demand = phi * 0.87 * request["longitudinal_fy_mpa"] / (4 * 2.4)
    anchorage = {
        "through_bar_diameter_mm": phi,
        "joint_length_in_each_plane_mm": width,
        "joint_width_required_mm": 20 * phi,
        "bond_stress_mpa_m30_deformed_in_tension": 2.4,
        "adjacent_member_development_required_mm": bond_demand,
        "adjacent_member_development_provided_mm_each_side": request[
            "beam_uninterrupted_development_mm"
        ],
        "pass": width >= 20 * phi
        and request["beam_uninterrupted_development_mm"] >= bond_demand,
    }
    families = {
        "construction_fit": all(placement["fit_checks"].values()),
        "confinement": all(placement["confinement_checks"].values()),
        "continuous_bar_anchorage": anchorage["pass"],
        "beam_flexural_prerequisite": all(
            item["tension_ductile"] for item in beams.values()
        ),
        "scwb": all(item["scwb"]["pass"] for item in directions.values()),
        "joint_shear": all(item["joint_shear"]["pass"] for item in directions.values()),
        "axial_stress": all(
            row["maximum_axial_stress_mpa"] <= 0.40 * request["column_fck_mpa"]
            for item in directions.values()
            for row in item["rows"]
        ),
    }
    governing = {}
    for family, members in (
        ("beam_capacity_shear", BEAM_ENDS),
        ("column_capacity_shear", COLUMN_ENDS),
    ):
        values = [
            {
                "direction": direction,
                "combination_id": row["combination_id"],
                "side": side,
                **row[family][side],
            }
            for direction, item in directions.items()
            for row in item["rows"]
            for side in members
        ]
        governing[family] = max(values, key=lambda item: item["utilization"])
        families[family] = all(item["pass"] for item in values)
    for family in ("scwb", "joint_shear"):
        direction = max(
            directions, key=lambda label: directions[label][family]["utilization"]
        )
        governing[family] = {"direction": direction, **directions[direction][family]}
    return {
        "status": "PASS" if all(families.values()) else "FAIL",
        "checks": families,
        "governing": governing,
        "directions": directions,
        "beam_section_by_plane": beams,
        "column_sections_by_combination_and_end": columns,
        "beam_joint_shear_mechanism_by_plane": mechanisms,
        "anchorage": anchorage,
        "placement": placement,
    }


def fixture():
    request = specimen()
    baseline = evaluate(request)
    assert baseline["status"] == "PASS", baseline["checks"]
    controls = {}
    mutations = {
        "weak_column": ({"column_bar_mm": 20, "column_bar_edge_mm": 75}, "scwb"),
        "weak_joint_core": ({"joint_fck_mpa": 20}, "joint_shear"),
        "insufficient_joint_links": (
            {"joint_hoop_centres_mm": [18, 149, 349, 443, 582]},
            "confinement",
        ),
        "short_adjacent_development": (
            {"beam_uninterrupted_development_mm": 700},
            "continuous_bar_anchorage",
        ),
        "intersecting_orthogonal_bars": (
            {"beam_row_depth_from_top_mm": {"X": 62, "Y": 62}},
            "construction_fit",
        ),
    }
    for name, (changes, reason) in mutations.items():
        result = evaluate(request | changes)
        failures = [family for family, passes in result["checks"].items() if not passes]
        assert result["status"] == "FAIL" and failures == [reason], (name, failures)
        controls[name] = {
            "changes": changes,
            "expected": {"status": "FAIL", "failed_checks": failures},
        }

    for family, field, value in (
        (
            "beam_capacity_shear",
            "beam_on_joint_downward_shear_kn",
            {"minus": 450, "plus": -17},
        ),
        ("column_capacity_shear", "analysis_column_shear_magnitude_kn", 850),
    ):
        modified = deepcopy(request["directions"])
        modified["X+"][0][field] = value
        result = evaluate(request | {"directions": modified})
        failures = [check for check, passes in result["checks"].items() if not passes]
        assert failures == [family], (family, failures)
        controls[f"excess_{family}"] = {
            "action_override": {
                "direction": "X+",
                "combination_id": "EQ-X+-1",
                "field": field,
                "value": value,
            },
            "expected": {
                "status": "FAIL",
                "failed_checks": failures,
                "governing": result["governing"][family],
            },
        }
    for name, changes, reason in (
        (
            "missing_direction",
            {
                "directions": {
                    k: v for k, v in request["directions"].items() if k != "Y-"
                }
            },
            "required_direction_missing",
        ),
        (
            "stale_revision",
            {"cage_action_revision": "DUCT01-DECLARED-R0"},
            "stale_action_revision",
        ),
        (
            "missing_mechanism",
            {"mechanism_inflection_offsets_mm": None},
            "compatible_capacity_mechanism_missing",
        ),
        (
            "missing_compaction_basis",
            {"compaction_head_mm": None},
            "compaction_basis_missing",
        ),
    ):
        result = evaluate(request | changes)
        assert result == {"status": "HOLD", "reason": reason}
        controls[name] = {"changes": changes, "expected": result}
    return {
        "fixture_version": "library-030-duct01-interior-joint/v1",
        "sources": [
            "BIS IS 13920:2016 with Amendment 1 (2017) and Amendment 2 (2020). https://standards.bis.gov.in/website/standard-details?encryptedId=eyJpdiI6Ik9yaTN1NC9ERTFvYVN5b1UwTG1ZUVE9PSIsInZhbHVlIjoiRHdrTlIzRloyOXg1WXFqMUN6ZTVBdz09IiwibWFjIjoiNmM5NTg5NzU4ZTIwOTNlMDkwMjcyZDg1MzM1MjEzMmNlNGYwMjc2MGVjMWFjYjM2ODdjYWRhOGQyNzE2MDU1NiIsInRhZyI6IiJ9",
            "IS 13920 §§6.2–6.3, 7.1–7.2, 7.4–7.6 and 9.1–9.2, base text. https://nfrlyconstruction.org/uploads/File/Codes/17072023-29_147_IS_13920-2016_DUCTILE_DETAILING_OF_RC_STRUCTURES.pdf_504314034.pdf",
            "IS 456 §§26.2, 26.3, 26.5.3, 38, 40 and Tables 19–20. https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf",
        ],
        "scope": [
            "Independent specimen with declared simultaneous actions and an explicit capacity mechanism. No source ETABS capture or global seismic system inferred.",
            "Columns and opposed beam sections are symmetric. SCWB tests each shaking sign using the lowest member capacity across all eight supplied axial rows.",
            "Beam capacity shear credits two outer hoop legs and no concrete. Column capacity shear credits two closed-hoop legs and the M30 Table 19 lower-bound row, adjusted for the concurrent axial force.",
            "Joint equilibrium uses 1.25fy tension forces, the opposing compression resultants, and the compatible column shear at the supplied inflection heights. It does not substitute the separate §7.5 shear envelope.",
            "End beam restraint uses nested hoops at staggered stations. The joint column tie groups use a closed hoop and two orthogonal cross-ties at distinct elevations. Fit and confinement use the declared adverse placement limits.",
            "The beam path intervals are the checked local continuations used for development. Full-span beam and storey splice schedules belong to the frame specimen.",
        ],
        "acceptance_tolerances": {
            "geometry_and_cut_lengths_abs_mm": 1e-6,
            "section_and_action_results_relative": 1e-8,
            "dispositions_signs_identifiers_and_counts": "exact",
        },
        "request": request,
        "expected": baseline,
        "controls": controls,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    output = json.dumps(fixture(), indent=2, sort_keys=True) + "\n"
    if args.write:
        TARGET.write_text(output, encoding="utf-8")
    elif TARGET.read_text(encoding="utf-8") != output:
        raise SystemExit(f"{TARGET.name} differs from independent regeneration")
    print(
        "DUCT01: four directions, eight simultaneous combinations, seven FAIL and four HOLD controls"
    )


if __name__ == "__main__":
    main()
