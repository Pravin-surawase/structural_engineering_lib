"""Replay Packet E APIs/artifacts against the selected installed build.

The independent engineering arithmetic is in check_library_027_t_beam_reference.py.
This consumer verifier deliberately exercises the installed public API and
checks its unchanged JSON/BBS/HTML against that separately frozen record.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import subprocess
import sys
from dataclasses import replace
from html.parser import HTMLParser
from html import unescape
from pathlib import Path


def same(label, actual, expected):
    if actual != expected:
        raise AssertionError((label, actual, expected))


def near(label, actual, expected, absolute=1e-8):
    if not math.isclose(float(actual), float(expected), rel_tol=0, abs_tol=absolute):
        raise AssertionError((label, actual, expected))


class Report(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tables = []
        self.polygons = []
        self.circles = []
        self.links = []
        self.active = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "table":
            self.tables.append([])
        if tag == "tr":
            self.row = []
        if tag in ("td", "th"):
            self.active = True
            self.buffer = ""
        if tag == "polygon":
            self.polygons.append(attributes)
        if tag == "circle":
            self.circles.append(attributes)
        if tag == "polyline":
            self.links.append(attributes)

    def handle_data(self, data):
        if self.active:
            self.buffer += data

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.active:
            self.row.append(self.buffer)
            self.active = False
        if tag == "tr" and self.row:
            self.tables[-1].append(self.row)


def reconcile(directory: Path, reference: dict, *, case: str, status: str) -> dict:
    payload = json.loads((directory / "calculation.json").read_text(encoding="utf-8"))
    results = payload["results"]
    package = results["package"]["outputs"]["calculation_package"]
    member = results["member"]["outputs"]["member_design"]
    schedule = results["paths"]["outputs"]["reinforcement_schedule"]
    bbs = results["bbs"]["outputs"]["bbs"]
    quantities = results["quantities"]["outputs"]["quantities"]
    same("workflow decision", payload["status"], status)
    same(
        "member engineering transported",
        payload["member_engineering"],
        results["member"]["engineering"],
    )
    same(
        "member completeness transported",
        payload["member_completeness"],
        results["member"]["completeness"],
    )
    same(
        "issue state",
        package["issue_state"],
        "issue_ready" if status == "PASS" else "draft",
    )
    same("approval", results["member"]["approval"], "unreviewed")
    same("active approval", package["active_approval"], False)
    same(
        "expected obligations",
        len(member["expected_leaves"]),
        reference["expected_member_obligation_count"],
    )
    same("retained paths", package["reinforcement_schedule"], schedule)
    same("retained BBS", package["bbs"], bbs)
    same("retained quantities", package["quantities"], quantities)
    same(
        "actual beam path count",
        len(schedule["paths"]),
        reference["expected_beam_path_count"],
    )
    with (directory / "bbs.csv").open(encoding="utf-8", newline="") as stream:
        csv_rows = list(csv.DictReader(stream))
    same("CSV count", len(csv_rows), len(schedule["paths"]))
    path_map = {p["bar_id"]: p for p in schedule["paths"]}
    same("CSV IDs", {row["bar_id"] for row in csv_rows}, set(path_map))
    for row in csv_rows:
        path = path_map[row["bar_id"]]
        same("CSV issue state", row["issue_state"], package["issue_state"])
        same("CSV mark", row["mark"], path["bar_mark"])
        same("CSV path binding", row["path_result_id"], results["paths"]["result_id"])
        same("CSV BBS binding", row["bbs_result_id"], results["bbs"]["result_id"])
        near("CSV diameter", row["diameter_mm"], path["diameter_mm"])
        near(
            "CSV developed length",
            row["length_mm"],
            path["developed_centreline_length_mm"],
        )
    for row in bbs["rows"]:
        paths = [path_map[path_id] for path_id in row["source_path_ids"]]
        same("scheduled mark count", row["scheduled_bar_count"], len(paths))
        near(
            "mark lengths",
            row["scheduled_cut_length_mm"],
            sum(p["developed_centreline_length_mm"] for p in paths),
        )
        mass = sum(
            math.pi
            * p["diameter_mm"] ** 2
            / 4
            * p["developed_centreline_length_mm"]
            * 7850
            / 1e9
            for p in paths
        )
        near("mark mass", row["theoretical_mass_kg"], mass)
    mass = sum(
        math.pi
        * p["diameter_mm"] ** 2
        / 4
        * p["developed_centreline_length_mm"]
        * 7850
        / 1e9
        for p in schedule["paths"]
    )
    near("quantity steel mass", quantities["steel_scheduled_mass_kg"], mass)
    same(
        "no slab steel silently scheduled",
        any(p["bar_id"].startswith("SLAB-") for p in schedule["paths"]),
        False,
    )
    report_text = (directory / "report.html").read_text(encoding="utf-8")
    report = Report(report_text)
    same(
        "HTML unchanged quantity payload",
        json.dumps(quantities, sort_keys=True) in unescape(report_text),
        True,
    )
    same("rendered decision", f"T-beam — {status}" in report_text, True)
    same(
        "rendered issue state",
        f"Issue state: {package['issue_state']}" in report_text,
        True,
    )
    same(
        "rendered member dimensions",
        f"Full member engineering: {results['member']['engineering']}; completeness: {results['member']['completeness']}"
        in report_text,
        True,
    )
    tables = {tuple(table[0]): table[1:] for table in report.tables if table}
    hooks = next(rows for header, rows in tables.items() if header[0] == "Hook path")
    source_hooks = results["hooks"]["outputs"].get("checks", ())
    same("HTML hook count", len(hooks), len(source_hooks))
    for row, check in zip(hooks, source_hooks, strict=True):
        same("HTML hook ID", row[0], check["bar_id"])
        near("HTML hook tail1", row[1], check["tails_mm"][0])
        near("HTML hook tail2", row[2], check["tails_mm"][1])
        near("HTML hook minimum", row[3], check["minimum_tail_mm"])
        same("HTML hook decision", row[4], str(check["passed"]))
    for result in results.values():
        for diagnostic in result["diagnostics"]:
            same("HTML retained diagnostic", diagnostic["code"] in report_text, True)
    states = results["t_serviceability"]["outputs"].get("section_states", ())
    rendered_states = next(
        (rows for header, rows in tables.items() if header[0] == "Model"), []
    )
    same("HTML actual service state count", len(rendered_states), len(states))
    for row, state in zip(rendered_states, states, strict=True):
        same("HTML service model", row[0], state["model"])
        for cell, key in zip(
            row[1:],
            (
                "neutral_axis_mm",
                "cracked_inertia_mm4",
                "bottom_steel_stress_nmm2",
                "elastic_bottom_surface_strain",
            ),
            strict=True,
        ):
            near(
                "HTML service value",
                cell,
                state[key],
                absolute=(
                    1e-3 if "inertia" in key else 1e-12 if "strain" in key else 1e-8
                ),
            )
    check_rows = next(
        rows for header, rows in tables.items() if header[0] == "Obligation"
    )
    same(
        "HTML required leaf IDs",
        [row[0] for row in check_rows],
        [q["expectation"]["leaf_id"] for q in member["leaf_qualifications"]],
    )
    for row, q in zip(check_rows, member["leaf_qualifications"], strict=True):
        evidence = q["evidence"]
        same(
            "HTML leaf decision",
            row[1],
            "QUALIFIED" if q["qualified"] else " / ".join(q["reason_codes"]),
        )
        for cell, key in ((row[2], "required_value"), (row[3], "supplied_value")):
            value = evidence[key] if evidence else None
            if value is None:
                same("HTML missing numeric value", cell, "—")
            else:
                near("HTML check numeric value", cell, value)
        if evidence:
            same("HTML method identity", evidence["method_revision_id"] in row[5], True)
            same(
                "HTML code identity", evidence["code_data_revision_id"] in row[5], True
            )
    rendered_paths = next(
        rows
        for header, rows in tables.items()
        if header == ("ID", "Diameter mm", "Developed length mm")
    )
    same(
        "HTML physical IDs",
        [row[0] for row in rendered_paths],
        [p["bar_id"] for p in schedule["paths"]],
    )
    for row, path in zip(rendered_paths, schedule["paths"], strict=True):
        near("HTML path diameter", row[1], path["diameter_mm"])
        near("HTML path length", row[2], path["developed_centreline_length_mm"])
    geometry = results["t_geometry"]["effective_inputs"]["request"]["value"]
    section = geometry["section"]
    width, depth, df, bw, left = (
        section[k]
        for k in (
            "flange_width_physical_mm",
            "depth_mm",
            "flange_thickness_mm",
            "web_width_mm",
            "web_left_from_flange_left_mm",
        )
    )
    outline = (
        (0, 0),
        (width, 0),
        (width, df),
        (left + bw, df),
        (left + bw, depth),
        (left, depth),
        (left, df),
        (0, df),
    )
    same(
        "physical T outline (not rectangle)",
        tuple(
            tuple(float(v) for v in pair.split(","))
            for pair in report.polygons[0]["points"].split()
        ),
        outline,
    )
    circles = {
        item["data-bar-id"]: item
        for item in report.circles
        if item.get("class") == "beam-bar"
    }
    same(
        "drawn actual beam bar IDs",
        set(circles),
        {bar["bar_id"] for bar in geometry["bars"]},
    )
    for bar in geometry["bars"]:
        circle = circles[bar["bar_id"]]
        near("drawing actual x", circle["cx"], bar["x_from_left_mm"])
        near("drawing actual y", circle["cy"], bar["y_from_top_mm"])
        near("drawing actual diameter", 2 * float(circle["r"]), bar["diameter_mm"])
    same(
        "actual hook path drawing",
        report.links[0]["data-bar-id"],
        next(p["bar_id"] for p in schedule["paths"] if p["role"] == "transverse_link"),
    )
    if status == "PASS":
        target = reference["cases"][
            "width_limited" if case == "width-limited" else "main"
        ]
        expected = target["expected"]
        same(
            "all member obligations qualify",
            all(q["qualified"] for q in member["leaf_qualifications"]),
            True,
        )
        same("member qualifies", member["qualified"], True)
        near(
            "physical-width concrete",
            quantities["concrete_volume_m3"],
            expected["owned_concrete_volume_m3"],
        )
        near(
            "actual formwork",
            quantities["formwork_area_m2"],
            expected["exposed_formwork_area_m2"],
        )
        near("frozen beam steel mass", mass, expected["beam_scheduled_steel_mass_kg"])
        near(
            "frozen supplied-bar resistance",
            results["capacity"]["outputs"]["capacity_knm"],
            expected["flexural_capacity_knm"],
        )
        near(
            "frozen web shear resistance",
            results["shear"]["outputs"]["checks"][0]["capacity_kn"],
            expected["provided_shear_capacity_kn"],
        )
        flange = results["flange_participation"]["outputs"]
        near(
            "derived effective width",
            flange["effective_flange_width_mm"],
            expected["effective_width_mm"],
        )
        same("separate slab owner", flange["slab_steel_in_beam_BBS"], False)
        strip = target["flange_strip_reference"]
        near(
            "local strip moment",
            flange["strip_two_face_moment_envelope_knm"],
            strip["two_face_moment_envelope_knm"],
        )
        for checked_face in flange["strip_flexure"]:
            near(
                "independent local strip resistance",
                checked_face["outputs"]["checks"][0]["capacity_knm"],
                strip["strip_flexural_capacity_each_face_knm"],
            )
        for anchor in flange["strip_anchorages"]:
            near(
                "actual transverse full-stress Ld",
                anchor["required_development_mm"],
                strip["full_stress_development_10_mm"],
            )
            near(
                "actual transverse left development",
                anchor["available_left_mm"],
                strip["available_development_each_side_mm"],
            )
            near(
                "actual transverse right development",
                anchor["available_right_mm"],
                strip["available_development_each_side_mm"],
            )
        actual_audit = flange["actual_parallel_steel_section_audit"]["outputs"]
        near(
            "actual parallel-steel ultimate axis",
            actual_audit["equilibrium_neutral_axis_depth_mm"],
            target["slab_parallel_steel_audit"]["ultimate_neutral_axis_mm"],
        )
        near(
            "actual parallel-steel capacity audit",
            actual_audit["capacity_knm"],
            target["slab_parallel_steel_audit"]["flexural_capacity_knm"],
        )
        same(
            "no slab beam strength credit",
            flange["slab_steel_beam_strength_credit"],
            False,
        )
        same(
            "local slab primary count",
            sum(
                p["role"] == "flange_transverse"
                for p in flange["strip_paths"]["outputs"]["reinforcement_schedule"][
                    "paths"
                ]
            ),
            strip["physical_primary_path_count"],
        )
        same(
            "local slab distribution count",
            sum(
                p["role"] == "flange_distribution"
                for p in flange["strip_paths"]["outputs"]["reinforcement_schedule"][
                    "paths"
                ]
            ),
            strip["physical_distribution_path_count"],
        )
        service = results["t_serviceability"]["outputs"]
        for state, key in zip(
            service["section_states"],
            ("expected", "slab_parallel_steel_audit"),
            strict=True,
        ):
            values = target[key]
            for actual_name, expected_name in (
                ("neutral_axis_mm", "service_neutral_axis_mm"),
                ("cracked_inertia_mm4", "cracked_inertia_mm4"),
                ("bottom_steel_stress_nmm2", "service_bottom_steel_stress_nmm2"),
                ("elastic_bottom_surface_strain", "elastic_bottom_surface_strain"),
            ):
                near(
                    "independent T service " + actual_name,
                    state[actual_name],
                    values[expected_name],
                    absolute=(
                        1e-3
                        if "inertia" in actual_name
                        else 1e-12 if "strain" in actual_name else 1e-8
                    ),
                )
        near(
            "independent selected crack envelope",
            results["crack"]["outputs"]["calculated_crack_width_mm"],
            expected["maximum_crack_width_mm"],
        )
        same(
            "no invented calculated deflection",
            service["calculated_deflection_mm"],
            None,
        )
    else:
        same("unqualified negative member", member["qualified"], False)
        if status == "FAIL":
            same(
                "retained known failed obligation",
                any(
                    q["evidence"]
                    and q["evidence"]["engineering"] == "fail"
                    and q["reason_codes"] == ["LEAF.FAIL"]
                    for q in member["leaf_qualifications"]
                ),
                True,
            )
    return {
        "case": case,
        "status": status,
        "issue_state": package["issue_state"],
        "qualified": sum(q["qualified"] for q in member["leaf_qualifications"]),
        "expected": len(member["expected_leaves"]),
        "paths": len(schedule["paths"]),
        "member_engineering": results["member"]["engineering"],
        "member_completeness": results["member"]["completeness"],
    }


def replay_public_requests(directory: Path) -> None:
    from pydantic import TypeAdapter
    from structural_lib import beam as b

    results = json.loads((directory / "calculation.json").read_text(encoding="utf-8"))[
        "results"
    ]
    for name, request_type, operation, result_name in (
        ("t-geometry", b.TGeometryCheckRequest, b.check_t_geometry, "t_geometry"),
        (
            "t-actions",
            b.TBeamActionBasisRequest,
            b.check_t_action_basis,
            "action_basis",
        ),
        (
            "t-zero-torsion",
            b.TBeamActionBasisRequest,
            b.check_t_zero_torsion,
            "torsion",
        ),
        (
            "t-flange",
            b.TFlangeParticipationRequest,
            b.check_t_flange_participation,
            "flange_participation",
        ),
        (
            "t-serviceability",
            b.TServiceabilityRequest,
            b.check_t_serviceability,
            "t_serviceability",
        ),
        (
            "t-stability",
            b.TLateralStabilityRequest,
            b.check_t_lateral_stability,
            "stability",
        ),
        ("member", b.MemberDesignRequest, b.design_member, "member"),
    ):
        adapter = TypeAdapter(request_type)
        same(
            "exported schema " + name,
            json.loads(
                (directory / "schemas" / (name + ".schema.json")).read_text(
                    encoding="utf-8"
                )
            ),
            adapter.json_schema(),
        )
        request = adapter.validate_json(
            (directory / "requests" / (name + ".json")).read_bytes(), strict=True
        )
        same(
            "strict public replay " + name,
            operation(request).result_id,
            results[result_name]["result_id"],
        )


def public_controls(directory: Path) -> None:
    from pydantic import TypeAdapter
    from structural_lib import beam as b

    geometry = TypeAdapter(b.TGeometryCheckRequest).validate_json(
        (directory / "requests/t-geometry.json").read_bytes(), strict=True
    )
    same(
        "stale T geometry cannot qualify",
        b.check_t_geometry(
            replace(geometry, expected_geometry_revision_id="old")
        ).engineering,
        "not_evaluated",
    )
    flange = TypeAdapter(b.TFlangeParticipationRequest).validate_json(
        (directory / "requests/t-flange.json").read_bytes(), strict=True
    )
    for changed in (
        replace(flange, integrally_cast=False),
        replace(flange, slab_main_direction="parallel_to_beam"),
        replace(flange, adjacent_clear_distance_left_mm=None),
    ):
        same(
            "unadmitted flange basis cannot qualify",
            b.check_t_flange_participation(changed).engineering,
            "not_evaluated",
        )
    action = flange.action_basis
    raw = TypeAdapter(b.RawActionSnapshot).validate_python(
        action.total_service_actions.effective_inputs["snapshot"]["value"]
    )
    torqued = b.normalize_action_snapshot(
        replace(raw, rows=tuple(replace(row, t=1000) for row in raw.rows))
    )
    same(
        "nonzero T service action HOLD",
        b.check_t_action_basis(
            replace(action, total_service_actions=torqued)
        ).engineering,
        "not_evaluated",
    )
    results = json.loads((directory / "calculation.json").read_text(encoding="utf-8"))[
        "results"
    ]
    capacity = TypeAdapter(b.ShearCapacityRequest).validate_python(
        results["shear"]["effective_inputs"]["capacities"]["value"][0]
    )
    # Component trap uses the same two legs at75mm. It does not advertise
    # another qualified physical cage/member; it proves why width matters.
    capacity = replace(capacity, link=replace(capacity.link, spacing_mm=75))
    demand = (b.ShearDemand("WEB-WIDTH-TRAP", b.ShearAxis.V2, 360),)
    same(
        "web-width trap FAIL",
        b.check_shear(b.ShearCheckRequest((capacity,), demand)).engineering,
        "fail",
    )
    same(
        "incorrect flange-width trap would PASS",
        b.check_shear(
            b.ShearCheckRequest((replace(capacity, resisting_width_mm=1000),), demand)
        ).engineering,
        "pass",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--example", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--reference",
        type=Path,
        default=Path(__file__).with_name("library-027-t-beam-member.json"),
    )
    parser.add_argument("--require-site-packages", action="store_true")
    parser.add_argument("--wheel", type=Path)
    args = parser.parse_args()
    origin = Path(importlib.util.find_spec("structural_lib").origin).resolve()
    if args.require_site_packages and not any(
        part in ("site-packages", "dist-packages") for part in origin.parts
    ):
        raise AssertionError(("Not an external installed package", str(origin)))
    reference = json.loads(args.reference.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    receipt = {
        "schema_version": "library-027-t-beam-consumer-replay/v1",
        "package_origin": str(origin),
        "python_version": sys.version,
        "pydantic_version": importlib.metadata.version("pydantic"),
        "installed_metadata_version": importlib.metadata.version(
            "structural-lib-is456"
        ),
        "journeys": [],
    }
    journeys = [("main", "adequate", "PASS"), ("width-limited", "adequate", "PASS")] + [
        ("main", name, state)
        for name, state in (
            ("overload", "FAIL"),
            ("insufficient-bars", "FAIL"),
            ("service-fail", "FAIL"),
            ("short-anchor", "FAIL"),
            ("short-hook", "FAIL"),
            ("missing-support", "HOLD"),
            ("missing-flange", "HOLD"),
            ("missing-service", "HOLD"),
            ("depth-conflict", "FAIL"),
            ("shoulder-bar", "FAIL"),
            ("end-cover", "FAIL"),
        )
    ]
    for case, probe, status in journeys:
        directory = args.output_dir / (case + "-" + probe)
        subprocess.run(
            [
                sys.executable,
                "-I",
                str(args.example.resolve()),
                "--case",
                case,
                "--probe",
                probe,
                "--output-dir",
                str(directory.resolve()),
            ],
            check=True,
        )
        receipt["journeys"].append(
            reconcile(directory, reference, case=case, status=status) | {"probe": probe}
        )
        if probe in ("adequate", "service-fail", "missing-service", "shoulder-bar"):
            replay_public_requests(directory)
        print("PASS artifacts/API", case, probe, flush=True)
    public_controls(args.output_dir / "main-adequate")
    receipt["public_controls"] = (
        "PASS stale geometry, unsupported flange/parallel main, missing adjacency, nonzero torsion and web shear-width trap"
    )
    if args.wheel:
        receipt["wheel"] = {
            "name": args.wheel.name,
            "sha256": hashlib.sha256(args.wheel.read_bytes()).hexdigest(),
            "bytes": args.wheel.stat().st_size,
        }
    (args.output_dir / "receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )
    print(
        "PASS Packet E installed journeys, strict public schemas, actual paths/BBS/quantities/HTML and invalid/FAIL/HOLD controls"
    )


if __name__ == "__main__":
    main()
