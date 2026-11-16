"""Independent SERV02 unequal-span signed actions and finite-age reference."""

from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from pathlib import Path

from check_library_029_serv01_reference import section

BASE = Path(__file__).with_name("library-029-serv02-beam-history.json")
FIXTURE = Path(__file__).with_name("library-030-serv02-unequal-span.json")
MEMBER = "SERV02-B45"
LENGTHS = (4000, 5000)
WIDTH, DEPTH = 250, 550
E_C, E_S, F_Y = 25000, 200000, 415
SUSTAINED, TOTAL = 20, 32  # kN/m, numerically equal to N/mm.
ASSESSMENT_ID, SUSTAINED_ID = "SLS-45", "SLS-45-G"
EPS = 1e-8


def outer_coordinates(span):
    # Rotation compatibility at the interior bearing under unit load.
    total_span = sum(LENGTHS)
    support_moment = -sum(length**3 for length in LENGTHS) / (8 * total_span)
    outer_reaction = span / 2 + support_moment / span
    integration_constant = outer_reaction * span**2 / 6 - span**3 / 24

    def rotation(x):
        return integration_constant - outer_reaction * x**2 / 2 + x**3 / 6

    def displacement(x):
        return integration_constant * x - outer_reaction * x**3 / 6 + x**4 / 24

    assert abs(displacement(span)) < span**4 * 1e-13
    zero_moment = 2 * outer_reaction
    # The slope is monotone on either side of the internal zero moment.
    # Inspect both intervals so unequal spans cannot hide a second extremum.
    roots = []
    for low, high in ((0, zero_moment), (zero_moment, span)):
        sign = rotation(low) > 0
        if sign == (rotation(high) > 0):
            continue
        for _ in range(80):
            middle = (low + high) / 2
            if (rotation(middle) > 0) == sign:
                low = middle
            else:
                high = middle
        roots.append((low + high) / 2)
    assert roots
    return {
        "length_mm": span,
        "support_moment_unit_nmm": support_moment,
        "outer_reaction_unit_n": outer_reaction,
        "zero_moment_from_outer_mm": zero_moment,
        "sagging_peak_from_outer_mm": outer_reaction,
        "deflection_extrema": sorted(
            ((x, displacement(x)) for x in roots),
            key=lambda point: -abs(point[1]),
        ),
        "inner_slope_unit": rotation(span),
    }


def _global(index, x):
    return x if index == 0 else sum(LENGTHS) - x


def _deflection_id(span_index, peak_index):
    face = "L" if span_index == 0 else "R"
    return f"{face}-D" if peak_index == 0 else f"{face}-D{peak_index + 1}"


def stations(spans):
    rows = [
        ("A", 0, "RIGHT"),
        ("A-FACE", 500, "CONTINUOUS"),
        ("B-LEFT-FACE", LENGTHS[0] - 150, "CONTINUOUS"),
        ("B-LEFT", LENGTHS[0], "LEFT"),
        ("B-RIGHT", LENGTHS[0], "RIGHT"),
        ("B-RIGHT-FACE", LENGTHS[0] + 150, "CONTINUOUS"),
        ("C-FACE", sum(LENGTHS) - 500, "CONTINUOUS"),
        ("C", sum(LENGTHS), "LEFT"),
    ]
    for i, item in enumerate(spans):
        mnemonic = "L" if i == 0 else "R"
        rows.extend(
            (f"{mnemonic}-{tag}", _global(i, item[field]), "CONTINUOUS")
            for tag, field in (
                ("M", "sagging_peak_from_outer_mm"),
                ("ZERO", "zero_moment_from_outer_mm"),
            )
        )
        rows.extend(
            (_deflection_id(i, rank), _global(i, point[0]), "CONTINUOUS")
            for rank, point in enumerate(item["deflection_extrema"])
        )
    return [
        {"station_id": name, "x_mm": x, "side": side}
        for name, x, side in sorted(rows, key=lambda value: (value[1], value[2]))
    ]


def actions(station_rows, spans):
    output = []
    for case, load in ((ASSESSMENT_ID, TOTAL), (SUSTAINED_ID, SUSTAINED)):
        for station in station_rows:
            z = station["x_mm"]
            right = z > LENGTHS[0] or (z == LENGTHS[0] and station["side"] == "RIGHT")
            s = _global(int(right), z)
            outer = spans[right]["outer_reaction_unit_n"]
            output.append(
                {
                    "row_id": f"{case}:{station['station_id']}",
                    "combination_id": case,
                    "station_id": station["station_id"],
                    "mu_knm": load * (outer * s - s**2 / 2) / 1e6,
                    "vu_kn": (-1 if right else 1) * load * (outer - s) / 1000,
                    "tu_knm": 0,
                }
            )
    return output


def _section_state(member, coefficient):
    modulus = E_C / (1 + coefficient)
    actual = section(member, 1, 0, modulus)
    return {
        "concrete_modulus_nmm2": modulus,
        "neutral_axis_mm": actual["neutral_axis_mm"],
        "cracked_inertia_mm4": actual["cracked_inertia_mm4"],
        "cracking_moment_knm": actual["cracking_moment_knm"],
    }


def _ei(state):
    return state["concrete_modulus_nmm2"] * state["cracked_inertia_mm4"]


def _width(member, station, total, sustained, initial, final):
    face = "top" if total["mu_knm"] < 0 else "bottom"
    moment = abs(total["mu_knm"])
    sustained_m = abs(sustained["mu_knm"])
    ks = sustained_m * 1e6 / _ei(final)
    kt = (moment - sustained_m) * 1e6 / _ei(initial)
    curvature = ks + kt
    axis = (
        (ks * final["neutral_axis_mm"] + kt * initial["neutral_axis_mm"]) / curvature
        if curvature > 0
        else initial["neutral_axis_mm"]
    )
    tension = [bar for bar in member["bars"] if bar["face"] == face]
    surface = 0 if face == "top" else DEPTH
    surface_strain = curvature * (DEPTH - axis)
    steel_depth = sum(DEPTH - abs(surface - b["y_from_top_mm"]) for b in tension) / len(
        tension
    )
    steel_strain = curvature * (steel_depth - axis)
    assert steel_strain < 0.8 * F_Y / E_S
    minimum_cover = min(
        abs(b["y_from_top_mm"] - surface) - b["diameter_mm"] / 2 for b in tension
    )
    bar_axes = sorted(b["x_from_left_mm"] for b in tension)
    surface_points = [0, WIDTH] + [
        (x + y) / 2 for x, y in zip(bar_axes[:-1], bar_axes[1:], strict=True)
    ]
    nearest = [
        min(
            math.hypot(x - b["x_from_left_mm"], surface - b["y_from_top_mm"])
            - b["diameter_mm"] / 2
            for b in tension
        )
        for x in surface_points
    ]
    acr = max(nearest)
    measured_x = surface_points[nearest.index(acr)]
    cracked = moment > initial["cracking_moment_knm"]
    width = (
        3 * acr * surface_strain / (1 + 2 * (acr - minimum_cover) / (DEPTH - axis))
        if cracked
        else 0
    )
    return {
        "station_id": station["station_id"],
        "x_mm": station["x_mm"],
        "tension_face": face,
        "assessment_row_id": total["row_id"],
        "sustained_row_id": sustained["row_id"],
        "cracked": cracked,
        "width_mm": width,
        "neutral_axis_mm": axis,
        "surface_strain": surface_strain,
        "tensile_steel_stress_nmm2": E_S * steel_strain,
        "surface_x_mm": measured_x,
        "nearest_steel_mm": acr,
    }


def fixture():
    spans = [outer_coordinates(length) for length in LENGTHS]
    assert abs(sum(item["inner_slope_unit"] for item in spans)) < 1e-4
    station_rows = stations(spans)
    signed_rows = actions(station_rows, spans)
    base = json.loads(BASE.read_text(encoding="utf-8"))["cases"]["continuous_history"][
        "request"
    ]
    request = deepcopy(base)
    request.update(
        identity={
            "family_id": "beam",
            "case_id": "SERV02-unequal",
            "member_id": MEMBER,
        },
        span_mm=max(LENGTHS),
        unequal_span_basis={
            "axial_restraint": "free",
            "shrinkage_profile": "uniform_through_section",
            "source_reference": "Prismatic beam, vertically supported and axially free with no shrinkage gradient.",
        },
    )
    member = request["member"]
    member.update(
        member_id=MEMBER,
        width_mm=WIDTH,
        depth_mm=DEPTH,
        clear_cover_mm=36,
        link_spacing_mm=150,
        analysis_revision="B45-A1",
        current_analysis_revision="B45-A1",
        reinforcement_revision="B45-R1",
        supports=[
            {"support_id": name, "centre_mm": centre, "width_mm": support}
            for name, centre, support in (
                ("A", 0, 1000),
                ("B", LENGTHS[0], 300),
                ("C", sum(LENGTHS), 1000),
            )
        ],
        stations=station_rows,
        actions=signed_rows,
        combinations=[
            {
                "combination_id": name,
                "kind": kind,
                "required_station_ids": [row["station_id"] for row in station_rows],
            }
            for name, kind in ((ASSESSMENT_ID, "SLS"), (SUSTAINED_ID, "SUSTAINED_SLS"))
        ],
        straight_bars={
            "start_mm": -460,
            "end_mm": sum(LENGTHS) + 460,
            "source_reference": "Six uninterrupted Ø20 bars with 40 mm nominal cover at the straight ends.",
        },
        source_reference="Independent two-span compatibility reference with both signed service combinations.",
    )
    for bar in member["bars"]:
        index = int(bar["bar_id"][-1]) - 1
        bar["x_from_left_mm"] = (54, 125, 196)[index]
        bar["y_from_top_mm"] = 54 if bar["face"] == "top" else 496
    assert WIDTH - 2 * 54 == 2 * 71 and 71 - 20 >= 20 + 5
    # The chosen 36 mm link cover and Ø8 links with inside radius 10
    # seat Ø20 bars at the centres of the closed link corner bends.
    assert member["clear_cover_mm"] + member["link_diameter_mm"] + 10 == 54
    history = request["history"]
    history["notional_size_mm"] = 2 * WIDTH * DEPTH / (2 * (WIDTH + DEPTH))
    for name, load in (
        (ASSESSMENT_ID, request["service_load"]),
        (SUSTAINED_ID, history["sustained_load"]),
    ):
        load.update(
            combination_id=name,
            analysis_revision="B45-A1",
            reinforcement_revision="B45-R1",
            source_reference="Three-moment signed service actions with identical UDL in each span.",
        )
    initial = _section_state(member, 0)
    finish = _section_state(member, history["at_finishes"]["creep_coefficient"])
    final = _section_state(member, history["at_assessment"]["creep_coefficient"])
    # The first moments of the steel rows about the section mid-depth
    # cancel. Uniform shrinkage in an axially free beam causes shortening
    # without a flexural curvature component.
    assert (
        abs(
            sum(
                math.pi
                * bar["diameter_mm"] ** 2
                / 4
                * (bar["y_from_top_mm"] - DEPTH / 2)
                for bar in member["bars"]
            )
        )
        < EPS
    )
    deflections = []
    all_extrema = []
    for index, item in enumerate(spans):
        span = LENGTHS[index]
        for rank, (position, shape) in enumerate(item["deflection_extrema"]):
            at_finish = SUSTAINED * shape / _ei(finish)
            at_final = SUSTAINED * shape / _ei(final) + (
                TOTAL - SUSTAINED
            ) * shape / _ei(initial)
            change = at_final - at_finish
            assert abs(at_final) < span / 250 and abs(change) < min(span / 350, 20)
            row = {
                "span_id": f"SPAN-{index + 1}",
                "span_mm": span,
                "station_id": _deflection_id(index, rank),
                "x_mm": _global(index, position),
                "initial_total_mm": TOTAL * shape / _ei(initial),
                "initial_sustained_mm": SUSTAINED * shape / _ei(initial),
                "at_finishes_mm": at_finish,
                "at_assessment_mm": at_final,
                "after_finishes_mm": change,
                "shrinkage_deflection_mm": 0,
                "total_limit_mm": span / 250,
                "after_finishes_limit_mm": min(span / 350, 20),
            }
            all_extrema.append(row)
            if rank == 0:
                deflections.append(row)
    assert any(row["at_assessment_mm"] < 0 for row in all_extrema)
    lookup = {(row["combination_id"], row["station_id"]): row for row in signed_rows}
    cracks = [
        _width(
            member,
            st,
            lookup[ASSESSMENT_ID, st["station_id"]],
            lookup[SUSTAINED_ID, st["station_id"]],
            initial,
            final,
        )
        for st in station_rows
        if st["station_id"]
        in {"L-M", "B-LEFT-FACE", "B-LEFT", "B-RIGHT", "B-RIGHT-FACE", "R-M"}
    ]
    governing_deflection = max(
        deflections, key=lambda item: item["at_assessment_mm"] / item["total_limit_mm"]
    )
    governing_increment = max(
        deflections,
        key=lambda item: item["after_finishes_mm"] / item["after_finishes_limit_mm"],
    )
    crack = min(cracks, key=lambda item: (-item["width_mm"], item["station_id"]))
    assert crack["station_id"] == "B-LEFT"
    expected = {
        "status": "PASS",
        "initial": initial,
        "at_finishes": finish,
        "at_assessment": final,
        "signed_rows": signed_rows,
        "span_deflections": deflections,
        "deflection_extrema": all_extrema,
        "crack_sections": cracks,
        "governing_deflection_station_id": governing_deflection["station_id"],
        "governing_after_finishes_station_id": governing_increment["station_id"],
        "governing_crack_station_id": crack["station_id"],
        "uniform_shrinkage_curvature_per_mm": 0,
    }
    cases = {"unequal_history": {"request": request, "expected": expected}}
    lose_history = deepcopy(request)
    del lose_history["history"]
    stale = deepcopy(request)
    stale["history"]["sustained_load"]["reinforcement_revision"] = "B45-R0"
    missing_row = deepcopy(request)
    missing_row["member"]["actions"] = [
        row for row in signed_rows if row["row_id"] != f"{SUSTAINED_ID}:B-RIGHT"
    ]
    crack_fail = deepcopy(request)
    crack_fail["crack_width_limit_mm"] = 0.20
    assert (
        max(c["width_mm"] for c in cracks if c["tension_face"] == "bottom")
        < 0.20
        < crack["width_mm"]
        < 0.30
    )
    for key, supplied, status, issue in (
        ("missing_history", lose_history, "HOLD", "BEAM.SUSTAINED_LOAD_HELD"),
        ("stale_reinforcement", stale, "HOLD", "BEAM.SERVICE_REVISION_STALE"),
        ("missing_sustained_station", missing_row, "HOLD", "BEAM.SERVICE_ROWS_HELD"),
        ("governing_crack_limit", crack_fail, "FAIL", "BEAM.HISTORY_LIMIT_EXCEEDED"),
    ):
        cases[key] = {
            "request": supplied,
            "expected": {
                "status": status,
                "issue": issue,
                **(
                    {"governing_crack_station_id": crack["station_id"]}
                    if status == "FAIL"
                    else {}
                ),
            },
        }
    return {
        "fixture_version": "library-030-serv02-unequal-span/v1",
        "sources": [
            "IS 456:2000 Cl. 23.2, Annex C-3, C-4 and Annex F",
            "Independent elastic rotation compatibility and direct integration with a per-age fully cracked prismatic stiffness",
            "Prescribed finite ages and uniform shrinkage reproduce the declared model",
        ],
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
    print("Reproduced SERV02 unequal-span PASS, one FAIL and three HOLD cases.")
