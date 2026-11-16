"""Freeze one common supplied-action ductile frame cut before product integration."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from copy import deepcopy
from pathlib import Path

import check_library_030_duct01_interior_reference as interior
import check_library_030_duct02_exterior_reference as exterior
from _project03_frame_statics import (
    BEAMS,
    CENTRES,
    DIRECTIONS,
    REVISION,
    combinations,
    UP,
    cross,
    subtract,
    resultant,
    reversed_action,
)
from _project03_member_reference import (
    BAR_AXES_MM,
    BAR_LEVELS_MM,
    BEAM_HOOP_RADIUS_MM,
    SIDE_SEAT_INSET_MM,
    TOP_SEAT_INSET_MM,
    WIDTH_MM,
    artifacts,
    beam_bars,
    beam_links,
    beam_strength,
    column_strength,
)

TARGET = Path(__file__).with_name("library-030-project03-ductile-frame.json")
ACTIONS = Path(__file__).with_name("library-030-project03-frame-actions.json")
BASE = "59bef91a4f5e479c59304c7f41e22fbe9fe51b50"


def joint_geometry():
    """Bind both local profiles to the independently shaped common bay."""
    west = interior.specimen()
    east = exterior.specimen()
    for field in (
        "column_width_mm",
        "joint_depth_mm",
        "column_cover_mm",
        "column_bar_edge_mm",
        "column_bar_mm",
        "column_link_mm",
        "column_end_confinement_length_mm",
    ):
        west[field] = east[field]
    west.update(
        beam_width_mm=WIDTH_MM,
        beam_bar_mm=east["beam_bar_mm"]["X"],
        beam_axis_across_column_mm=list(BAR_AXES_MM),
        beam_row_depth_from_top_mm=dict(east["beam_top_z_mm"]),
        beam_link_centre_radius_mm=BEAM_HOOP_RADIUS_MM,
        beam_link_seat_inset_mm=SIDE_SEAT_INSET_MM,
        beam_link_depth_seat_inset_mm=TOP_SEAT_INSET_MM,
        column_link_centre_radius_mm=40,
        column_hook_tail_mm=136,
        column_hook_rise_mm=20,
        column_first_end_hoop_mm=40,
        column_hook_offset_radiused=True,
        cross_tie_station_offset_mm=20,
        joint_hoop_centres_mm=[24, 115, 209, 311, 414, 517, 629, 720],
    )
    east["column_end_link_first_mm"] = 40
    east["beam_axes_mm"]["X"] = list(BAR_AXES_MM)
    east["beam_width_mm"]["X"] = WIDTH_MM
    east["beam_link_seat_inset_mm"]["X"] = SIDE_SEAT_INSET_MM
    east["beam_link_depth_seat_inset_mm"] = {"X": TOP_SEAT_INSET_MM}
    west["beam_clear_spans_mm"]["X"]["plus"] = east["beam_clear_spans_mm"]["X"]["minus"]
    west["beam_dead_plus_live_kn_m"]["X"]["plus"] = east["beam_dead_plus_live_kn_m"][
        "X"
    ]["minus"]
    for req in (west, east):
        req.update(action_revision=REVISION, cage_action_revision=REVISION)
        req.pop("directions")
    return {"J1": west, "J2": east}


def source_packet(*, overload=False):
    actions = combinations(overload=overload)
    stripped = {
        name: {
            "direction": action["direction"],
            "action_revision": action["action_revision"],
            "beams": {
                member: {
                    key: value for key, value in row.items() if key != "equilibrium"
                }
                for member, row in action["beams"].items()
            },
            "columns": {
                member: {
                    key: value for key, value in row.items() if key != "equilibrium"
                }
                for member, row in action["columns"].items()
            },
        }
        for name, action in actions.items()
    }
    return {
        "project_id": "PROJECT03",
        "action_revision": REVISION,
        "current_action_revision": REVISION,
        "required_combinations": {
            direction: [
                name for name, row in stripped.items() if row["direction"] == direction
            ]
            for direction in DIRECTIONS
        },
        "joint_geometry": joint_geometry(),
        "actions": stripped,
    }


def _small(residual):
    return max(abs(value) for vector in residual.values() for value in vector) <= 1e-9


def _witness_consistent(member, beam):
    plane, start, end, span, nominal = BEAMS[member]
    if (beam["plane"], beam["start_joint"], beam["end_joint"]) != (plane, start, end):
        return False
    if beam["clear_span_m"] != span or beam["nominal_dead_plus_live_kn_m"] != nominal:
        return False
    a, b = beam["start_face"], beam["end_face"]
    vector = subtract(b["point_m"], a["point_m"])
    axis = tuple(component / span for component in vector)
    axis_expected = (1, 0, 0) if plane == "X" else (0, 1, 0)
    if math.dist(axis, axis_expected) > 1e-12 or beam["factored_udl_kn_m"] <= 0:
        return False
    m_axis = cross(axis, UP)
    m0, m1 = beam["sectional_end_moments_knm"]
    expected = (
        (a, -m0, beam["vertical_reactions_kn"][0]),
        (b, m1, beam["vertical_reactions_kn"][1]),
    )
    return (
        all(
            math.dist(face["force_kn"], (0, 0, r)) <= 1e-9
            and math.dist(
                face["couple_knm"], tuple(m * component for component in m_axis)
            )
            <= 1e-9
            for face, m, r in expected
        )
        and math.dist(
            beam["distributed_resultant"]["force_kn"],
            (0, 0, -beam["factored_udl_kn_m"] * span),
        )
        <= 1e-9
    )


def _origin_balance(row):
    beam_residuals, column_residuals = {}, {}
    beam_face_by_joint = {joint: {} for joint in CENTRES}
    joint_faces = {joint: [] for joint in CENTRES}
    boundary_actions, distributed = {}, []
    source_witnesses = {}
    for member, beam in row["beams"].items():
        source_witnesses[member] = _witness_consistent(member, beam)
        body = beam["distributed_resultant"]
        start, end = beam["start_face"], beam["end_face"]
        beam_residuals[member] = resultant((start, end, body), start["point_m"])
        for at, side in (("start", "plus"), ("end", "minus")):
            joint = beam[f"{at}_joint"]
            face = beam[f"{at}_face"]
            if joint is None:
                boundary_actions[f"{member}:{at}"] = face
            else:
                beam_face_by_joint[joint][(beam["plane"], side)] = face
                joint_faces[joint].append(reversed_action(face))
        distributed.append(body)
    for member, leg in row["columns"].items():
        near, far, body = (
            leg[key] for key in ("near_face", "boundary_face", "self_weight_resultant")
        )
        column_residuals[member] = resultant((near, far, body), near["point_m"])
        joint_faces[leg["joint"]].append(reversed_action(near))
        boundary_actions[f"{member}:boundary"] = far
        distributed.append(body)
    joint_residuals = {
        name: resultant(rows, CENTRES[name]) for name, rows in joint_faces.items()
    }
    frame = resultant((*boundary_actions.values(), *distributed))
    return {
        "beams": beam_residuals,
        "columns": column_residuals,
        "joints": joint_residuals,
        "frame_cut": frame,
        "external_boundary_actions": boundary_actions,
        "beam_face_by_joint": beam_face_by_joint,
        "member_witnesses": source_witnesses,
        "pass": all(source_witnesses.values())
        and all(
            _small(residual)
            for residual in (
                *beam_residuals.values(),
                *column_residuals.values(),
                *joint_residuals.values(),
                frame,
            )
        ),
    }


def _mapped_rows(combo, row, joint, balance):
    plane = row["direction"][0]
    faces = balance["beam_face_by_joint"][joint]
    upper = row["columns"][f"C-{joint}-upper"]["near_face"]
    return {
        "combination_id": combo,
        "upper_axial_compression_kn": upper["force_kn"][2],
        "beam_on_joint_downward_shear_kn": {
            side: face["force_kn"][2]
            for (axis, side), face in faces.items()
            if axis == plane
        },
        "orthogonal_downward_reaction_kn": sum(
            face["force_kn"][2] for (axis, _), face in faces.items() if axis != plane
        ),
        "analysis_column_shear_magnitude_kn": abs(upper["force_kn"]["XY".index(plane)]),
    }


def _materialize_joint_inputs(request, balances):
    result = deepcopy(request["joint_geometry"])
    for joint, payload in result.items():
        payload["directions"] = {direction: [] for direction in DIRECTIONS}
        for direction, names in request["required_combinations"].items():
            for combo in names:
                row = request["actions"][combo]
                mapped = _mapped_rows(combo, row, joint, balances[combo])
                if joint == "J2":
                    mapped.update(beam_axial_kn=0, sway=direction[1])
                payload["directions"][direction].append(mapped)
    return result


def _shared_geometry(left, right):
    axis1, axis2 = left["beam_axis_across_column_mm"], right["beam_axes_mm"]["X"]
    return (
        axis1 == axis2 == list(BAR_AXES_MM)
        and left["joint_depth_mm"] == right["joint_depth_mm"]
        and left["beam_row_depth_from_top_mm"]["X"]
        == right["beam_top_z_mm"]["X"]
        == BAR_LEVELS_MM[0]
        and left["beam_clear_spans_mm"]["X"]["plus"]
        == right["beam_clear_spans_mm"]["X"]["minus"]
        == 4300
        and left["beam_dead_plus_live_kn_m"]["X"]["plus"]
        == right["beam_dead_plus_live_kn_m"]["X"]["minus"]
        and left["beam_width_mm"] == right["beam_width_mm"]["X"] == WIDTH_MM
        and left["beam_bar_mm"] == right["beam_bar_mm"]["X"] == 20
        and left["beam_link_centre_radius_mm"]
        == right["beam_link_centre_radius_mm"]["X"]
        == BEAM_HOOP_RADIUS_MM
        and left["beam_first_link_mm"] == right["beam_first_link_mm"] == 30
        and left["beam_inner_link_offset_mm"]
        == right["beam_inner_link_offset_mm"]
        == 16
        and left["beam_pitch_mm"] == right["beam_pitch_mm"] == 75
        and left["beam_link_mm"] == right["beam_link_mm"] == 10
        and left["beam_link_seat_inset_mm"]
        == right["beam_link_seat_inset_mm"]["X"]
        == SIDE_SEAT_INSET_MM
        and left["beam_link_depth_seat_inset_mm"]
        == right["beam_link_depth_seat_inset_mm"]["X"]
        == TOP_SEAT_INSET_MM
    )


def evaluate(request):
    """Check source completeness, shared geometry and every admitted component."""
    revision = request["action_revision"]
    actions = request["actions"]
    if (
        request["current_action_revision"] != revision
        or any(row["action_revision"] != revision for row in actions.values())
        or any(
            data["cage_action_revision"] != revision
            for data in request["joint_geometry"].values()
        )
    ):
        return {"status": "HOLD", "reason": "stale_frame_revision"}
    inventory = request["required_combinations"]
    required = {name for names in inventory.values() for name in names}
    if (
        required != set(actions)
        or set(inventory) != set(DIRECTIONS)
        or any(
            not names or any(actions[name]["direction"] != direction for name in names)
            for direction, names in inventory.items()
        )
    ):
        return {"status": "HOLD", "reason": "incomplete_signed_inventory"}
    columns = {f"C-{joint}-{end}" for joint in CENTRES for end in ("upper", "lower")}
    if any(
        set(row["beams"]) != set(BEAMS) or set(row["columns"]) != columns
        for row in actions.values()
    ):
        return {"status": "HOLD", "reason": "missing_member_or_boundary_action"}
    balances = {name: _origin_balance(row) for name, row in actions.items()}
    if not all(record["pass"] for record in balances.values()):
        return {"status": "FAIL", "failed_checks": ["frame_source_equilibrium"]}
    inputs = _materialize_joint_inputs(request, balances)
    west, east = inputs["J1"], inputs["J2"]
    if not _shared_geometry(west, east):
        return {"status": "FAIL", "failed_checks": ["shared_cage_continuity"]}
    joints = {"J1": interior.evaluate(west), "J2": exterior.evaluate(east)}
    failed_joints = [
        joint for joint, result in joints.items() if result["status"] != "PASS"
    ]
    if failed_joints:
        return {
            "status": "FAIL",
            "failed_checks": ["joint_acceptance"],
            "failed_joints": failed_joints,
            "joint_checks": {
                name: [
                    key for key, passed in joints[name]["checks"].items() if not passed
                ]
                for name in failed_joints
            },
        }
    links = beam_links()
    bars = beam_bars(joints["J2"])
    beam = beam_strength(actions, joints["J1"], joints["J2"], links)
    columns = column_strength(actions, joints, inputs)
    fabrication = artifacts(joints, columns, links, bars)
    checks = {
        "frame_source_equilibrium": True,
        "shared_cage_continuity": True,
        "joint_acceptance": True,
        "shared_beam_strength": beam["pass"],
        "shared_beam_constructible_geometry": links["pass"] and bars["pass"],
        "admitted_column_legs": all(member["pass"] for member in columns.values()),
        "cut_mark_and_leg_placement_reconciliation": fabrication["pass"],
    }
    failed = [name for name, passed in checks.items() if not passed]
    return {
        "status": "FAIL" if failed else "PASS",
        "failed_checks": failed,
        "checks": checks,
        "source_balances": {
            name: {
                key: value
                for key, value in record.items()
                if key != "beam_face_by_joint"
            }
            for name, record in balances.items()
        },
        "joint_action_requests": inputs,
        "joints": joints,
        "shared_beam": {"strength": beam, "links": links, "longitudinal": bars},
        "column_legs": columns,
        "artifact_reconciliation": fabrication,
        "excluded_boundary_beams": [
            {
                "member_id": name,
                "actions_included": True,
                "member_design_and_bbs": "OUTSIDE_FRAME_CUT_ACCEPTANCE",
            }
            for name in BEAMS
            if name != "BX12"
        ],
        "site_insertion_status": "REQUIRES_CONSTRUCTION_SEQUENCE_EVIDENCE",
    }


def fixture():
    request = source_packet()
    result = evaluate(request)
    assert result["status"] == "PASS", (
        result["checks"],
        {
            name: (
                row["pass"],
                row["governing_flexure"],
                row["governing_shear"]["shear_utilization"],
            )
            for name, row in result["column_legs"].items()
        },
    )
    controls = {}
    cases = (
        (
            "stale_project_revision",
            [("current_action_revision",)],
            "R0",
            "HOLD",
            "stale_frame_revision",
        ),
        (
            "missing_required_direction_row",
            [("actions", "P03-Y--2")],
            None,
            "HOLD",
            "incomplete_signed_inventory",
        ),
        (
            "missing_boundary_leg",
            [("actions", "P03-X+-1", "columns", "C-J2-upper")],
            None,
            "HOLD",
            "missing_member_or_boundary_action",
        ),
        (
            "unbalanced_beam_at_j2",
            [
                ("actions", "P03-X+-1", "beams", "BX12", "end_face", "force_kn"),
            ],
            [0.0, 0.0, 142.0],
            "FAIL",
            "frame_source_equilibrium",
        ),
        (
            "same_steel_mismatched_axes",
            [("joint_geometry", "J2", "beam_axes_mm", "X")],
            [122, 178, 422, 478],
            "FAIL",
            "shared_cage_continuity",
        ),
        (
            "column_boundary_biaxial_overload",
            [("actions", "P03-Y+-2")],
            source_packet(overload=True)["actions"]["P03-Y+-2"],
            "FAIL",
            "admitted_column_legs",
        ),
        (
            "short_exterior_bottom_tail",
            [("joint_geometry", "J2", "x_hooks", "BOTTOM", "tail_mm")],
            470,
            "FAIL",
            "joint_acceptance",
        ),
    )
    for name, paths, value, status, reason in cases:
        changed = deepcopy(request)
        (path,) = paths
        parent = changed
        for token in path[:-1]:
            parent = parent[token]
        if value is None:
            del parent[path[-1]]
        else:
            parent[path[-1]] = value
        actual = evaluate(changed)
        assert actual["status"] == status, (name, actual["status"])
        if status == "HOLD":
            assert actual["reason"] == reason
        else:
            assert actual["failed_checks"] == [reason]
        controls[name] = {
            "path": path,
            "operation": "delete" if value is None else "replace",
            "value": value,
            "expected": {
                key: value
                for key, value in actual.items()
                if key
                in (
                    "status",
                    "reason",
                    "failed_checks",
                    "failed_joints",
                    "joint_checks",
                )
            },
        }
        if name == "column_boundary_biaxial_overload":
            failed = {
                member: result["governing_flexure"]
                for member, result in actual["column_legs"].items()
                if not result["pass"]
            }
            assert set(failed) == {"C-J2-upper", "C-J2-lower"}
            controls[name]["expected"]["failed_column_boundaries"] = failed
    return {
        "fixture_version": "library-030-project03-ductile-frame/v1",
        "baseline_commit": BASE,
        "method": [
            "Static equilibrium of a declared three-dimensional frame cut with two cores, six beam intervals and four column legs. Each outer cut is represented by its supplied force and moment. Actions are factored witness loads for the bounded frame cut.",
            "Global X east, Y north, Z upward. Vertical beam reactions positive upward on the beam map to positive downwards on the joint. The three-dimensional joint axial balance includes the reactions of both beam planes.",
            "Bending, shear, joint capacity mechanism, confinement and anchorage use the separate independent local sections. The four short column legs use a conservative linear biaxial flexure envelope and shared-hoop shear sum for the concurrent planes.",
            "The shared BX12 stock paths include the west boundary-beam carry-through and straight development in its declared thick support. The boundary support cage, construction-stage handling, insertion and temporary supports require project-specific evidence.",
            "The local joint schedules and the shared beam links use disjoint marks. Local joint views of the eight continuous X bars belong to one shared inventory and carry no duplicate order quantities.",
        ],
        "sources": [
            "IS 13920:2016 and Amendments 1 and 2, §§6.2–6.3, 7.1–7.2, 7.4–7.6 and 9.1–9.2. https://standards.bis.gov.in/website/standard-details?encryptedId=eyJpdiI6Ik9yaTN1NC9ERTFvYVN5b1UwTG1ZUVE9PSIsInZhbHVlIjoiRHdrTlIzRloyOXg1WXFqMUN6ZTVBdz09IiwibWFjIjoiNmM5NTg5NzU4ZTIwOTNlMDkwMjcyZDg1MzM1MjEzMmNlNGYwMjc2MGVjMWFjYjM2ODdjYWRhOGQyNzE2MDU1NiIsInRhZyI6IiJ9",
            "IS 456:2000 §§25.1, 25.4, 26.2, 26.3, 38, 39.6, 40 and Tables 19–20. https://law.resource.org/pub/in/bis/S03/is.456.2000.pdf",
        ],
        "request": request,
        "expected": result,
        "controls": controls,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    values = fixture()
    source_json = (
        json.dumps(values.pop("request"), allow_nan=False, indent=2, sort_keys=True)
        + "\n"
    )
    values["source_packet"] = {
        "filename": ACTIONS.name,
        "sha256": sha256(source_json.encode()).hexdigest(),
    }
    expected_json = json.dumps(values, allow_nan=False, indent=2, sort_keys=True) + "\n"
    for path, serialized in ((ACTIONS, source_json), (TARGET, expected_json)):
        if args.write:
            path.write_text(serialized, encoding="utf-8")
        elif path.read_text(encoding="utf-8") != serialized:
            raise SystemExit(f"{path.name} differs from independent regeneration")
    print(
        "PROJECT03: eight combinations, two joints, five admitted members, four FAIL and three HOLD controls"
    )


if __name__ == "__main__":
    main()
