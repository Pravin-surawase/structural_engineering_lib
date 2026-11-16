"""Independent three-dimensional statics of the bounded PROJECT03 frame cut."""

from __future__ import annotations

import math
from collections import defaultdict
from itertools import product

DIRECTIONS = ("X+", "X-", "Y+", "Y-")
REVISION = "PROJECT03-CUT-R1"
CENTRES = {"J1": (0.0, 0.0, 0.0), "J2": (4.9, 0.0, 0.0)}
FACE_OFFSET_M = 0.3
DEPTH_M = 0.745
HEIGHTS_M = {"upper": 3.4, "lower": 3.6}
ZERO = (0.0, 0.0, 0.0)
UP = (0.0, 0.0, 1.0)

# Each tuple describes a physical beam in global plus-axis order. Boundary
# cuts are external reaction locations. Only BX12 has two admitted ends.
BEAMS = {
    "BX12": ("X", "J1", "J2", 4.3, 30),
    "BX1W": ("X", None, "J1", 4.0, 30),
    "BY1S": ("Y", None, "J1", 4.1, 29),
    "BY1N": ("Y", "J1", None, 4.3, 31),
    "BY2S": ("Y", None, "J2", 4.5, 31),
    "BY2N": ("Y", "J2", None, 4.7, 32),
}


def add(*vectors):
    return tuple(map(sum, zip(*vectors, strict=True))) if vectors else ZERO


def scale(v, factor):
    return tuple(value * factor for value in v)


def subtract(v, w):
    return add(v, scale(w, -1))


def cross(v, w):
    x, y, z = v
    a, b, c = w
    return y * c - z * b, z * a - x * c, x * b - y * a


def action(point, force, couple=ZERO):
    return {"point_m": point, "force_kn": force, "couple_knm": couple}


def resultant(actions, about=ZERO):
    actions = tuple(actions)
    return {
        "force_kn": add(*(row["force_kn"] for row in actions)),
        "moment_knm": add(
            *(
                add(
                    row["couple_knm"],
                    cross(subtract(row["point_m"], about), row["force_kn"]),
                )
                for row in actions
            )
        ),
    }


def reversed_action(load):
    return action(
        load["point_m"], scale(load["force_kn"], -1), scale(load["couple_knm"], -1)
    )


def _assert_equilibrium(result):
    assert (
        max(abs(value) for vector in result.values() for value in vector) <= 1e-9
    ), result


def _faces(plane, start, finish, span):
    axis = (1.0, 0.0, 0.0) if plane == "X" else (0.0, 1.0, 0.0)
    if start is not None:
        p0 = add(CENTRES[start], scale(axis, FACE_OFFSET_M))
        p1 = add(p0, scale(axis, span))
    else:
        p1 = add(CENTRES[finish], scale(axis, -FACE_OFFSET_M))
        p0 = add(p1, scale(axis, -span))
    if start is not None and finish is not None:
        assert math.dist(p1, add(CENTRES[finish], scale(axis, -FACE_OFFSET_M))) <= 1e-12
    return p0, p1, axis


def _beam_rows(direction, load_variant):
    plane, sense = direction
    sign = 1 if sense == "+" else -1
    result = {}
    for index, (member, (axis, start, end, span, nominal)) in enumerate(BEAMS.items()):
        p0, p1, e = _faces(axis, start, end, span)
        w = (1.2 + 0.2 * load_variant) * nominal
        # Sectional moments are sagging positive and independent supplied
        # boundary terms. Opposite sway reverses this term only.
        eq = sign * (125 + 5 * index + 10 * load_variant) if plane == axis else 0
        m0 = -82 - 4 * load_variant + eq
        m1 = -91 - 3 * load_variant - eq
        r0 = w * span / 2 + (m1 - m0) / span
        r1 = w * span - r0
        m_axis = cross(e, UP)
        start_action = action(p0, scale(UP, r0), scale(m_axis, -m0))
        end_action = action(p1, scale(UP, r1), scale(m_axis, m1))
        dead = action(scale(add(p0, p1), 0.5), scale(UP, -w * span))
        residual = resultant((start_action, end_action, dead), p0)
        _assert_equilibrium(residual)
        result[member] = {
            "start_joint": start,
            "end_joint": end,
            "plane": axis,
            "clear_span_m": span,
            "nominal_dead_plus_live_kn_m": nominal,
            "factored_udl_kn_m": w,
            "start_face": start_action,
            "end_face": end_action,
            "distributed_resultant": dead,
            "sectional_end_moments_knm": (m0, m1),
            "vertical_reactions_kn": (r0, r1),
            "equilibrium": residual,
        }
    return result


def _column_leg(joint, position, force, moment):
    up = 1 if position == "upper" else -1
    height = HEIGHTS_M[position]
    near = add(CENTRES[joint], scale(UP, up * DEPTH_M / 2))
    far = add(near, scale(UP, up * height))
    # The declared factored unit weight includes the column body load,
    # independent of the supported beam load.
    factored_self_weight_kn_m = 10.8
    body = action(
        scale(add(near, far), 0.5), scale(UP, -factored_self_weight_kn_m * height)
    )
    near_action = action(near, force, moment)
    far_force = scale(add(force, body["force_kn"]), -1)
    far_couple = scale(add(moment, cross(subtract(far, near), far_force)), -1)
    far_action = action(far, far_force, far_couple)
    residual = resultant((near_action, far_action, body), near)
    _assert_equilibrium(residual)
    return {
        "joint": joint,
        "position": position,
        "near_face": near_action,
        "boundary_face": far_action,
        "self_weight_resultant": body,
        "equilibrium": residual,
    }


def _place_column_pair(joint, beam_faces, direction, variant, added_shear_kn):
    sign = 1 if direction[1] == "+" else -1
    active_shear = sign * (
        84 + variant * 12 + (8 if joint == "J2" else 0) + added_shear_kn
    )
    other_shear = sign * 7
    vx, vy = (
        (active_shear, other_shear)
        if direction[0] == "X"
        else (other_shear, active_shear)
    )
    p_upper = 570 + variant * 43 + (24 if joint == "J2" else 0)
    vertical = sum(row["force_kn"][2] for row in beam_faces)
    p_lower = p_upper + vertical
    upper_force = (vx, vy, p_upper)
    lower_force = (-vx, -vy, -p_lower)
    on_joint = resultant((reversed_action(row) for row in beam_faces), CENTRES[joint])
    eccentric_column_moment = add(
        cross(scale(UP, DEPTH_M / 2), upper_force),
        cross(scale(UP, -DEPTH_M / 2), lower_force),
    )
    couples = subtract(on_joint["moment_knm"], eccentric_column_moment)
    upper_couple = scale(couples, HEIGHTS_M["lower"] / sum(HEIGHTS_M.values()))
    lower_couple = subtract(couples, upper_couple)
    upper = _column_leg(joint, "upper", upper_force, upper_couple)
    lower = _column_leg(joint, "lower", lower_force, lower_couple)
    member_faces = (*beam_faces, upper["near_face"], lower["near_face"])
    residual = resultant((reversed_action(row) for row in member_faces), CENTRES[joint])
    _assert_equilibrium(residual)
    return upper, lower, residual


def combinations(*, overload=False):
    """Emit source member actions, their mapped joint actions and frame balance."""
    rows = {}
    for direction, variant in product(DIRECTIONS, range(2)):
        combination_id = f"P03-{direction}-{variant + 1}"
        beams = _beam_rows(direction, variant)
        incident = defaultdict(dict)
        boundaries = {}
        member_loads = []
        for name, beam in beams.items():
            for at, side in (("start", "plus"), ("end", "minus")):
                joint = beam[f"{at}_joint"]
                load = beam[f"{at}_face"]
                if joint is None:
                    boundaries[f"{name}:{at}"] = load
                else:
                    incident[joint][(beam["plane"], side)] = load
            member_loads.append(beam["distributed_resultant"])
        columns, mapped, joint_residuals = {}, {}, {}
        for joint in CENTRES:
            by_face = incident[joint]
            upper, lower, residual = _place_column_pair(
                joint,
                tuple(by_face.values()),
                direction,
                variant,
                11 if overload and combination_id == "P03-Y+-2" else 0,
            )
            for leg in (upper, lower):
                member = f"C-{joint}-{leg['position']}"
                columns[member] = leg
                boundaries[f"{member}:boundary"] = leg["boundary_face"]
                member_loads.append(leg["self_weight_resultant"])
            joint_residuals[joint] = residual
            active = {
                side: row["force_kn"][2]
                for (plane, side), row in by_face.items()
                if plane == direction[0]
            }
            orthogonal = sum(
                row["force_kn"][2]
                for (plane, _), row in by_face.items()
                if plane != direction[0]
            )
            active_component = "XY".index(direction[0])
            mapped[joint] = {
                "combination_id": combination_id,
                "upper_axial_compression_kn": upper["near_face"]["force_kn"][2],
                "beam_on_joint_downward_shear_kn": active,
                "orthogonal_downward_reaction_kn": orthogonal,
                "analysis_column_shear_magnitude_kn": abs(
                    upper["near_face"]["force_kn"][active_component]
                ),
            }
            assert math.isclose(
                sum(active.values()) + orthogonal,
                -lower["near_face"]["force_kn"][2] - upper["near_face"]["force_kn"][2],
                abs_tol=1e-10,
            )
        global_residual = resultant((*boundaries.values(), *member_loads))
        _assert_equilibrium(global_residual)
        rows[combination_id] = {
            "action_revision": REVISION,
            "direction": direction,
            "beams": beams,
            "columns": columns,
            "mapped_joint_rows": mapped,
            "joint_equilibrium": joint_residuals,
            "external_boundary_actions": boundaries,
            "frame_cut_equilibrium": global_residual,
        }
    return rows
