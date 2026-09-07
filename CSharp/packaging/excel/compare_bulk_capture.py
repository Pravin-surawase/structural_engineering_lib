"""Independent comparison of complete WP10 bulk projection with exact direct getters.

Run with the repository Python launcher. Evidence stays in an explicit external
directory; no ETABS/Excel process or model mutation is performed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from structural_lib.analysis_snapshot import (
    parse_analysis_snapshot_json,
    parse_analysis_snapshot_transport,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--reference-sha256", required=True)
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    if args.receipt.exists():
        raise ValueError("Use a new evidence receipt path.")
    reference_bytes = args.reference.read_bytes()
    if hashlib.sha256(reference_bytes).hexdigest() != args.reference_sha256:
        raise ValueError("Reference bytes do not match the frozen direct acquisition.")
    reference = json.loads(reference_bytes)["content"]["capture"]
    payload = args.snapshot.read_bytes()
    compressed = payload.startswith(b"STRUCTSNAP-GZIP-1\n")
    replay = (
        parse_analysis_snapshot_transport(payload)
        if compressed
        else parse_analysis_snapshot_json(payload.decode("utf-8"))
    )
    if replay.snapshot is None:
        raise ValueError(str(replay.diagnostics))
    snapshot = (
        replay.snapshot.model_dump(mode="json") if compressed else json.loads(payload)
    )
    calls = {
        (call["operation"], call["inputs"][0] if call["inputs"] else ""): call
        for call in reference["calls"]
        if not call["inputs"] or isinstance(call["inputs"][0], (str, int))
    }
    metadata = next(
        record["fields"]["data"]
        for record in snapshot["raw_capture"]["model_records"]
        if record["record_kind"] == "model_metadata"
    )
    bulk = metadata["projection"]["acquisition_evidence"]["capture"]
    if bulk["host_identity"] != reference["host_identity"]:
        raise ValueError("Bulk and reference have different source identities.")
    members = {
        record["fields"]["data"]["object_id"]: record["fields"]["data"]
        for record in snapshot["raw_capture"]["model_records"]
        if record["record_kind"] == "member"
    }
    if set(members) != {member["object_name"] for member in reference["members"]}:
        raise ValueError("The required member scope differs from the direct reference.")
    points = {
        record["fields"]["data"]["name"]: record["fields"]["data"]
        for record in snapshot["raw_capture"]["model_records"]
        if record["record_kind"] == "point"
    }
    maximum = {"coordinate_m": 0.0, "relative_station": 0.0, "axis_matrix": 0.0}
    element_count = 0
    row_count = 0

    def outputs(method: str, name: str) -> list:
        return calls[method, name]["outputs"]

    def equal(actual, expected, label: str) -> None:
        if actual != expected:
            raise ValueError(f"Exact source mismatch: {label}")

    def close(actual, expected, kind: str) -> None:
        error = abs(actual - expected)
        maximum[kind] = max(maximum[kind], error)
        if error > 1e-8:
            raise ValueError(
                f"Source derivation exceeds the existing tolerance: {kind}"
            )

    force_evidence = {
        item["inputs"][0]: item["outputs"]
        for item in metadata["projection"]["getter_evidence"]
        if item["operation"] == "Results.FrameForce"
    }
    for name, member in members.items():
        equal(
            force_evidence[name], outputs("Results.FrameForce", name), "complete forces"
        )
        row_count += force_evidence[name][0]
        equal(
            member["modifiers"], outputs("FrameObj.GetModifiers", name)[0], "modifiers"
        )
        offsets = outputs("FrameObj.GetEndLengthOffset", name)
        equal(
            [
                member[field]
                for field in (
                    "automatic_offsets",
                    "end_offset_i",
                    "end_offset_j",
                    "rigid_zone_factor",
                )
            ],
            offsets,
            "offsets",
        )
        equal(
            [
                member[field]
                for field in ("releases_i", "releases_j", "springs_i", "springs_j")
            ],
            outputs("FrameObj.GetReleases", name),
            "releases and partial fixity",
        )
        insertion = member["insertion"]
        direct_insertion = outputs("FrameObj.GetInsertionPoint_1", name)
        equal(
            [
                insertion[field]
                for field in (
                    "cardinal_point",
                    "mirror2",
                    "mirror3",
                    "stiffness_transformed",
                    "offset_i",
                    "offset_j",
                )
            ],
            direct_insertion[:6],
            "insertion",
        )
        if any(insertion["offset_i"] + insertion["offset_j"]):
            equal(insertion["coordinate_system"], direct_insertion[6], "offset basis")
        for element in member["elements"]:
            element_count += 1
            element_id = element["id"]
            direct_owner = outputs("LineElm.GetObj", element_id)
            equal(element["object_id"], direct_owner[0], "element owner")
            direct_points = outputs("LineElm.GetPoints", element_id)
            equal(
                [element["point_i_id"], element["point_j_id"]],
                ["point:" + point for point in direct_points],
                "mesh connectivity",
            )
            close(element["relative_i"], direct_owner[2], "relative_station")
            close(element["relative_j"], direct_owner[3], "relative_station")
            for actual, expected in zip(
                element["local_to_global"],
                outputs("LineElm.GetTransformationMatrix", element_id)[0],
                strict=True,
            ):
                close(actual, expected, "axis_matrix")
            for point_id in direct_points:
                call = (
                    calls.get(("PointObj.GetCoordCartesian", point_id))
                    or calls[("PointElm.GetCoordCartesian", point_id)]
                )
                for field, expected in zip(
                    ("x", "y", "z"), call["outputs"], strict=True
                ):
                    close(points[point_id][field], expected, "coordinate_m")
    equal(row_count, len(snapshot["action_rows"]), "complete row accounting")
    receipt = {
        "schema_version": "wp10-bulk-reference-comparison/v1",
        "passed": True,
        "pf9_acceptance": False,
        "reference_sha256": args.reference_sha256,
        "snapshot_file_sha256": hashlib.sha256(payload).hexdigest(),
        "snapshot_sha256": snapshot["snapshot_sha256"],
        "members": len(members),
        "analysis_elements": element_count,
        "action_rows": row_count,
        "maximum_derivation_errors": maximum,
        "full_signed_force_payloads_equal": True,
        "assignment_values_equal": True,
        "independent_python_replay": True,
    }
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
