"""Replay the synthetic paired Element Forces beam and column intake."""

from __future__ import annotations

import argparse
import csv
import io
import json
from dataclasses import replace
from pathlib import Path
from typing import Literal

from structural_lib.beam.analysis import (
    ForceUnit,
    LengthUnit,
    LocalAxes,
    MomentUnit,
    Vector3,
)
from structural_lib.services.etabs_paired_forces import (
    EtabsActionBasis,
    EtabsCombination,
    EtabsForceTable,
    EtabsMemberBinding,
    EtabsPairedForcesRequest,
    EtabsTableUnits,
    import_etabs_paired_forces,
)

REFERENCE = (
    Path(__file__).resolve().parents[2]
    / "docs/verification/library-029-flow04-paired-intake.json"
)


def build_request(
    path: Path = REFERENCE, *, alternate_units: bool = False
) -> EtabsPairedForcesRequest:
    data = json.loads(path.read_text(encoding="utf-8"))
    basis = EtabsActionBasis("teaching-model", "a" * 64, "run-1", "sections-1")
    units = (
        EtabsTableUnits(ForceUnit.N, MomentUnit.N_MM, LengthUnit.M)
        if alternate_units
        else EtabsTableUnits(ForceUnit.KN, MomentUnit.KN_M, LengthUnit.MM)
    )
    definitions = tuple(
        EtabsCombination(case, "Linear Add", use)
        for case, use in data["combinations"].items()
    )
    kinds: tuple[Literal["beam", "column"], ...] = ("beam", "column")
    members = []
    tables = []
    x, y, z = Vector3(1, 0, 0), Vector3(0, 1, 0), Vector3(0, 0, 1)
    for kind in kinds:
        member = data["members"][kind]
        label = kind.capitalize()
        object_id = member["object_id"]
        length = member["length_mm"]
        e1, e2, e3 = (x, z, Vector3(0, -1, 0)) if kind == "beam" else (z, x, y)
        members.append(
            EtabsMemberBinding(
                kind,
                member["story"],
                member["label"],
                object_id,
                object_id,
                Vector3(0, 0, 0),
                Vector3(e1.x * length, e1.y * length, e1.z * length),
                LocalAxes(f"{kind}-axes", e1, e2, e3),
                (member["station_mm"],),
                tuple(data["combinations"]),
            )
        )
        stream = io.StringIO(newline="")
        writer = csv.writer(stream)
        writer.writerow([f"TABLE:  Element Forces - {label}s"])
        writer.writerow(
            [
                "Story",
                label,
                "Unique Name",
                "Output Case",
                "Case Type",
                *(["Step Type"] if kind == "beam" else []),
                "Station",
                "P",
                "V2",
                "V3",
                "T",
                "M2",
                "M3",
                "Element",
                "Elem Station",
                *(["Location"] if kind == "column" else []),
            ]
        )
        station, force, moment = (
            ("m", "N", "N-mm") if alternate_units else ("mm", "kN", "kN-m")
        )
        writer.writerow(
            [""] * (6 if kind == "beam" else 5)
            + [station]
            + [force] * 3
            + [moment] * 3
            + ["", station]
            + ([""] if kind == "column" else [])
        )
        position = member["station_mm"]
        values = member["components_kn_knm"]
        if alternate_units:
            position /= 1000
            values = [
                value * factor
                for value, factor in zip(
                    values, (1000, 1000, 1000, 1000000, 1000000, 1000000), strict=True
                )
            ]
        for combination in definitions:
            writer.writerow(
                [
                    member["story"],
                    member["label"],
                    object_id,
                    combination.combination_id,
                    "Combination",
                    *([""] if kind == "beam" else []),
                    position,
                    *values,
                    object_id,
                    position,
                    *([""] if kind == "column" else []),
                ]
            )
        tables.append(
            EtabsForceTable(stream.getvalue().encode(), "22.7.0", "capture-1", basis)
        )
    return EtabsPairedForcesRequest(
        tables[0], tables[1], basis, units, tuple(members), definitions
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, default=REFERENCE)
    parser.add_argument("--missing-combination", action="store_true")
    parser.add_argument("--alternate-units", action="store_true")
    args = parser.parse_args()
    request = build_request(args.reference, alternate_units=args.alternate_units)
    if args.missing_combination:
        table = request.beam_table
        rows = [line for line in table.csv_bytes.splitlines() if b",U2," not in line]
        request = replace(
            request, beam_table=replace(table, csv_bytes=b"\n".join(rows))
        )
    result = import_etabs_paired_forces(request)
    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()
