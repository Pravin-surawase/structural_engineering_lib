"""Equilibrium and directional action mapping of a regular two-joint frame cut."""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

_Zero = (0.0, 0.0, 0.0)
Vector = tuple[float, float, float]
_Unit = {"X": (1, 0, 0), "Y": (0, 1, 0)}
_DIRECTIONS = ("X+", "X-", "Y+", "Y-")
_TOL = 1e-9

# Beams are oriented in positive global X or Y. None identifies a cut
# boundary with its own supplied force and couple.
BEAM_CONNECTIONS: dict[str, tuple[str, str | None, str | None]] = {
    "BX12": ("X", "J1", "J2"),
    "BX1W": ("X", None, "J1"),
    "BY1S": ("Y", None, "J1"),
    "BY1N": ("Y", "J1", None),
    "BY2S": ("Y", None, "J2"),
    "BY2N": ("Y", "J2", None),
}
COLUMN_LEGS = {
    f"C-{joint}-{end}": (joint, end)
    for joint in ("J1", "J2")
    for end in ("upper", "lower")
}


def frame_hold_reason(data: Mapping[str, Any]) -> str | None:
    """Require one revision and the complete declared direction and member inventory."""
    revisions = [data["current_action_revision"]]
    for joint in data["joint_geometry"].values():
        revisions.extend((joint["action_revision"], joint["cage_action_revision"]))
    actions = data["actions"]
    revisions.extend(action["action_revision"] for action in actions.values())
    if any(revision != data["action_revision"] for revision in revisions):
        return "stale_frame_revision"
    inventory = data["required_combinations"]
    names = [name for group in inventory.values() for name in group]
    if (
        set(inventory) != set(_DIRECTIONS)
        or len(set(names)) != len(names)
        or set(names) != set(actions)
        or any(
            not group or any(actions[name]["direction"] != direction for name in group)
            for direction, group in inventory.items()
        )
    ):
        return "incomplete_signed_inventory"
    if any(
        set(row["beams"]) != set(BEAM_CONNECTIONS)
        or set(row["columns"]) != set(COLUMN_LEGS)
        for row in actions.values()
    ):
        return "missing_member_or_boundary_action"
    return None


def _scale(v: Sequence[float], factor: float) -> Vector:
    x, y, z = v
    return x * factor, y * factor, z * factor


def _add(a: Sequence[float], b: Sequence[float]) -> Vector:
    x, y, z = a
    u, v, w = b
    return x + u, y + v, z + w


def _difference(a: Sequence[float], b: Sequence[float]) -> Vector:
    return _add(a, _scale(b, -1))


def _cross(a: Sequence[float], b: Sequence[float]) -> Vector:
    x, y, z = a
    u, v, w = b
    return y * w - z * v, z * u - x * w, x * v - y * u


def _balance(
    actions: Iterable[tuple[Mapping[str, Any], int]], origin: Vector = _Zero
) -> dict[str, Vector]:
    force, moment = _Zero, _Zero
    for load, sign in actions:
        applied_force = _scale(load["force_kn"], sign)
        force = _add(force, applied_force)
        transfer = _cross(_difference(load["point_m"], origin), applied_force)
        moment = _add(moment, _add(transfer, _scale(load["couple_knm"], sign)))
    return {"force_kn": force, "moment_knm": moment}


def _near(left: Sequence[float], right: Sequence[float]) -> bool:
    return math.dist(left, right) <= _TOL


def _scalar(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=0, abs_tol=_TOL)


def _midpoint(a: Sequence[float], b: Sequence[float]) -> Vector:
    return _scale(_add(a, b), 0.5)


def _within_balance(residual: Mapping[str, Vector]) -> bool:
    return all(abs(value) <= _TOL for vector in residual.values() for value in vector)


def _beam_witness(
    member: str,
    beam: Mapping[str, Any],
    geometry: Mapping[str, Any],
    centres: Mapping[str, Vector],
) -> bool:
    axis, start, end = BEAM_CONNECTIONS[member]
    if (beam["plane"], beam["start_joint"], beam["end_joint"]) != (axis, start, end):
        return False
    axis_vector = _Unit[axis]
    a, b, body = beam["start_face"], beam["end_face"], beam["distributed_resultant"]
    span = beam["clear_span_m"]
    local_length = _difference(b["point_m"], a["point_m"])
    if not _near(local_length, _scale(axis_vector, span)):
        return False
    for face, joint, side, sign in ((a, start, "plus", 1), (b, end, "minus", -1)):
        if joint is None:
            continue
        local = geometry[joint]
        expected = _add(
            centres[joint], _scale(axis_vector, sign * local["column_width_mm"] / 2000)
        )
        if (
            not _near(face["point_m"], expected)
            or not _scalar(span * 1000, local["beam_clear_spans_mm"][axis][side])
            or not _scalar(
                beam["nominal_dead_plus_live_kn_m"],
                local["beam_dead_plus_live_kn_m"][axis][side],
            )
        ):
            return False
    # A positive sagging section moment at the start maps to the
    # opposite end couple about beam-axis cross vertical.
    moment_axis = _cross(axis_vector, (0, 0, 1))
    moments = beam["sectional_end_moments_knm"]
    reactions = beam["vertical_reactions_kn"]
    return (
        _near(a["force_kn"], (0, 0, reactions[0]))
        and _near(b["force_kn"], (0, 0, reactions[1]))
        and _near(a["couple_knm"], _scale(moment_axis, -moments[0]))
        and _near(b["couple_knm"], _scale(moment_axis, moments[1]))
        and _near(body["force_kn"], (0, 0, -beam["factored_udl_kn_m"] * span))
        and _near(body["couple_knm"], _Zero)
        and _near(body["point_m"], _midpoint(a["point_m"], b["point_m"]))
    )


def _column_witness(
    member: str,
    leg: Mapping[str, Any],
    geometry: Mapping[str, Any],
    centres: Mapping[str, Vector],
    direction: str,
) -> bool:
    joint, end = COLUMN_LEGS[member]
    if (leg["joint"], leg["position"]) != (joint, end):
        return False
    local = geometry[joint]
    sign = 1 if end == "upper" else -1
    near, far, body = (
        leg[key] for key in ("near_face", "boundary_face", "self_weight_resultant")
    )
    near_point = _add(centres[joint], (0, 0, sign * local["joint_depth_mm"] / 2000))
    far_point = _add(
        near_point, (0, 0, sign * local["column_clear_heights_mm"][end] / 1000)
    )
    sway_sign = 1 if direction[1] == "+" else -1
    component = "XY".index(direction[0])
    return (
        sign * sway_sign * near["force_kn"][component] >= -_TOL
        and _near(near["point_m"], near_point)
        and _near(far["point_m"], far_point)
        and _near(body["point_m"], _midpoint(near_point, far_point))
        and _near(body["couple_knm"], _Zero)
        and _near(body["force_kn"], (0, 0, body["force_kn"][2]))
        and body["force_kn"][2] < 0
        and _scalar(near["couple_knm"][2], 0)
        and _scalar(far["couple_knm"][2], 0)
        and sign * near["force_kn"][2] > 0
        and sign * far["force_kn"][2] < 0
    )


def _map_joint_row(
    name: str,
    row: Mapping[str, Any],
    faces: Mapping[tuple[str, str], Mapping[str, Any]],
    joint: str,
) -> dict[str, Any]:
    selected = row["direction"][0]
    upper = row["columns"][f"C-{joint}-upper"]["near_face"]
    payload = {
        "combination_id": name,
        "upper_axial_compression_kn": upper["force_kn"][2],
        "beam_on_joint_downward_shear_kn": {
            side: face["force_kn"][2]
            for (plane, side), face in faces.items()
            if plane == selected
        },
        "orthogonal_downward_reaction_kn": sum(
            face["force_kn"][2]
            for (plane, _), face in faces.items()
            if plane != selected
        ),
        "analysis_column_shear_magnitude_kn": abs(
            upper["force_kn"]["XY".index(selected)]
        ),
    }
    if joint == "J2":
        payload.update(beam_axial_kn=0, sway=row["direction"][1])
    return payload


def resolve_frame_actions(
    data: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Check actual source wrenches and map the accepted rows into both cores."""
    geometry = data["joint_geometry"]
    j1, j2 = geometry["J1"], geometry["J2"]
    span = j1["beam_clear_spans_mm"]["X"]["plus"]
    centres: dict[str, Vector] = {
        "J1": _Zero,
        "J2": (
            (span + (j1["column_width_mm"] + j2["column_width_mm"]) / 2) / 1000,
            0,
            0,
        ),
    }
    mappings: dict[str, Any] = {
        joint: {direction: [] for direction in _DIRECTIONS} for joint in centres
    }
    balances = {}
    for direction in _DIRECTIONS:
        for name in data["required_combinations"][direction]:
            row = data["actions"][name]
            joint_faces: dict[str, list[tuple[Mapping[str, Any], int]]] = {
                joint: [] for joint in centres
            }
            active_faces: dict[str, dict[tuple[str, str], Mapping[str, Any]]] = {
                joint: {} for joint in centres
            }
            boundaries, body_loads = {}, []
            beam_balance, column_balance = {}, {}
            beam_witnesses, column_witnesses = {}, {}
            for member, beam in row["beams"].items():
                axis, start, end = BEAM_CONNECTIONS[member]
                beam_witnesses[member] = _beam_witness(member, beam, geometry, centres)
                a, b, body = (
                    beam["start_face"],
                    beam["end_face"],
                    beam["distributed_resultant"],
                )
                beam_balance[member] = _balance(
                    ((a, 1), (b, 1), (body, 1)), tuple(a["point_m"])
                )
                body_loads.append(body)
                for end_label, face, joint, side in (
                    ("start", a, start, "plus"),
                    ("end", b, end, "minus"),
                ):
                    if joint is None:
                        boundaries[f"{member}:{end_label}"] = face
                    else:
                        joint_faces[joint].append((face, -1))
                        active_faces[joint][axis, side] = face
            for member, leg in row["columns"].items():
                joint, _ = COLUMN_LEGS[member]
                column_witnesses[member] = _column_witness(
                    member, leg, geometry, centres, direction
                )
                near, far, body = (
                    leg[key]
                    for key in ("near_face", "boundary_face", "self_weight_resultant")
                )
                column_balance[member] = _balance(
                    ((near, 1), (far, 1), (body, 1)), tuple(near["point_m"])
                )
                joint_faces[joint].append((near, -1))
                boundaries[f"{member}:boundary"] = far
                body_loads.append(body)
            node_balance = {
                joint: _balance(joint_faces[joint], origin)
                for joint, origin in centres.items()
            }
            frame_balance = _balance(
                (load, 1) for load in (*boundaries.values(), *body_loads)
            )
            balances[name] = {
                "beams": beam_balance,
                "columns": column_balance,
                "joints": node_balance,
                "frame_cut": frame_balance,
                "external_boundary_actions": boundaries,
                "member_witnesses": beam_witnesses,
                "column_witnesses": column_witnesses,
                "pass": all((*beam_witnesses.values(), *column_witnesses.values()))
                and all(
                    _within_balance(residual)
                    for residual in (
                        *beam_balance.values(),
                        *column_balance.values(),
                        *node_balance.values(),
                        frame_balance,
                    )
                ),
            }
            for joint in centres:
                mappings[joint][direction].append(
                    _map_joint_row(name, row, active_faces[joint], joint)
                )
    return balances, mappings
