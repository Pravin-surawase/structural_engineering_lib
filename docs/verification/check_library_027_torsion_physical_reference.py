"""Standard-library-only D2 reference replay; never import the design engine."""

from __future__ import annotations

import json
import math
from pathlib import Path


def main() -> None:
    reference = json.loads(
        Path(__file__)
        .with_name("library-027-torsion-physical.json")
        .read_text(encoding="utf-8")
    )
    inputs, expected = reference["inputs"], reference["expected"]
    span, load, eccentricity = (
        inputs["centre_span_mm"],
        inputs["uniform_load_n_per_mm"],
        inputs["eccentricity_mm"],
    )
    for row in expected["action_rows"]:
        x = row["station_mm"]
        independent = {
            "v2_kn": load * (span / 2 - x) / 1000,
            "m3_knm": load * x * (span - x) / 2e6,
            "torsion_knm": load * eccentricity * (span / 2 - x) / 1e6,
        }
        for key, value in independent.items():
            assert math.isclose(row[key], value, rel_tol=0, abs_tol=1e-8), (
                key,
                row,
                value,
            )
    offset = abs(eccentricity) * (1 + inputs["D_mm"] / inputs["b_mm"]) / 1.7
    for station in (span / 2 - offset, span / 2 + offset):
        assert any(
            math.isclose(row["station_mm"], station, rel_tol=0, abs_tol=1e-8)
            for row in expected["action_rows"]
        )
    governing = max(
        row["m3_knm"]
        + abs(row["torsion_knm"]) * (1 + inputs["D_mm"] / inputs["b_mm"]) / 1.7
        for row in expected["action_rows"]
    )
    assert math.isclose(
        governing, expected["governing_equivalent_moment_knm"], rel_tol=0, abs_tol=1e-8
    )
    reaction = load * span / 2000
    torque = -load * eccentricity * span / 2e6
    lines = expected["support_line_forces_kn"]
    assert math.isclose(sum(lines), reaction, rel_tol=0, abs_tol=1e-8)
    couple = (
        -sum(
            force * (z - 1500)
            for force, z in zip(lines, expected["support_lines_mm"], strict=True)
        )
        / 1000
    )
    assert math.isclose(couple, torque, rel_tol=0, abs_tol=1e-8)
    assert math.isclose(
        2 * couple + expected["total_applied_torque_knm"], 0, abs_tol=1e-8
    )
    right_reaction = (
        sum(f * z for f, z in zip(lines, expected["support_lines_mm"], strict=True))
        / 3000
    )
    left_reaction = sum(lines) - right_reaction
    assert [left_reaction, right_reaction] == expected[
        "receiver_transfer_only_reactions_kn"
    ]
    moments = [
        left_reaction * z
        - sum(
            f * max(0, z - p)
            for f, p in zip(lines, expected["support_lines_mm"], strict=True)
        )
        for z in expected["support_lines_mm"]
    ]
    assert max(moments) / 1000 == expected["receiver_transfer_only_peak_moment_knm"]
    assert (
        max(left_reaction, right_reaction)
        == expected["receiver_transfer_only_peak_shear_kn"]
    )
    receiver_load = (
        1000
        * 400
        * inputs["receiver_unit_weight_kn_per_m3"]
        * inputs["receiver_self_weight_factor"]
        / 1e6
    )
    assert receiver_load == expected["receiver_factored_self_weight_n_per_mm"]
    total_reactions = [
        left_reaction + receiver_load * 3000 / 2000,
        right_reaction + receiver_load * 3000 / 2000,
    ]
    assert total_reactions == expected["receiver_reactions_kn"]
    total_moments = [
        total_reactions[0] * z
        - receiver_load * z * z / 2000
        - sum(
            f * max(0, z - p)
            for f, p in zip(lines, expected["support_lines_mm"], strict=True)
        )
        for z in expected["support_lines_mm"]
    ]
    assert max(total_moments) / 1000 == expected["receiver_peak_moment_knm"]
    assert max(total_reactions) == expected["receiver_peak_shear_kn"]
    assert math.isclose(
        20 * 0.87 * 415 / (4 * 1.4 * 1.6),
        expected["tension_development_mm"],
        rel_tol=0,
        abs_tol=1e-8,
    )
    link_length = (
        100 + 342 + math.hypot(242, 10) + 342 + 242 + 100 - 5 * (40 - 20 * math.pi / 2)
    )
    assert math.isclose(
        link_length, expected["link_path_length_mm"], rel_tol=0, abs_tol=1e-8
    )
    assert (4950 - 50) // 100 + 1 == expected["link_count"]
    print(
        "PASS independent D2 actions, signed support/crosshead equilibrium, tension Ld and physical lengths"
    )


if __name__ == "__main__":
    main()
