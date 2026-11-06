"""Replay and reconcile the 0.27 beam member evidence from an installed build."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import runpy
import subprocess
import sys
from collections import Counter
from html.parser import HTMLParser
from importlib.metadata import version
from pathlib import Path

import structural_lib
from structural_lib.design.is456 import beam


def same(label, actual, expected):
    if actual != expected:
        raise ValueError(f"{label} does not match the expected evidence")


def near(label, actual, expected):
    if not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-8):
        raise ValueError(f"{label}: {actual} differs from {expected}")


class Report(HTMLParser):
    """Read the report's visible table cells and retained package."""

    def __init__(self, text):
        super().__init__()
        self.tables = []
        self.preformatted = []
        self.heading = ""
        self.active = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.tables.append([])
        elif tag == "tr":
            self.row = []
        elif tag in {"td", "h1", "pre"}:
            self.active = tag
            self.buffer = ""

    def handle_data(self, data):
        if self.active is not None:
            self.buffer += data

    def handle_endtag(self, tag):
        if tag == self.active:
            if tag == "td":
                self.row.append(self.buffer)
            elif tag == "pre":
                self.preformatted.append(self.buffer)
            else:
                self.heading = self.buffer
            self.active = None
        if tag == "tr" and self.row:
            self.tables[-1].append(self.row)


def report_checks(report, package, results, bbs):
    def number(value):
        return "—" if value is None else f"{value:.3f}"

    same("report issue state", report.heading, f"B1 — {package['issue_state'].upper()}")
    steel = [
        [
            row["bar_id"],
            str(row["layer"]),
            f"{row['depth_from_compression_face_mm']:g}",
            f"{row['strain']:.8f}",
            f"{row['steel_stress_n_per_mm2']:.6f}",
            f"{row['displaced_concrete_stress_n_per_mm2']:.6f}",
            f"{row['net_force_n']:.3f}",
        ]
        for row in results["capacity"]["outputs"]["bar_responses"]
    ]
    checks = [
        [
            leaf["leaf_id"],
            "qualified" if leaf["qualified"] else "unqualified",
            number(leaf["required_value"]),
            number(leaf["provided_value"]),
            leaf["unit"] or "",
            ", ".join(leaf["reason_codes"]),
        ]
        for leaf in package["leaves"]
    ]
    schedule = [
        [
            row["bar_mark"],
            f"{row['diameter_mm']:g}",
            str(row["scheduled_bar_count"]),
            f"{row['fabrication_cut_length_each_mm']:.3f}",
            f"{row['theoretical_mass_kg']:.3f}",
        ]
        for row in bbs["rows"]
    ]
    same(
        "rendered steel, checks and schedule tables",
        report.tables,
        [steel, checks, schedule],
    )
    same("embedded calculation package", json.loads(report.preformatted[-1]), package)
    for label, identity in (
        ("Package", package["calculation_package_id"]),
        ("Paths", results["paths"]["result_id"]),
        ("BBS", results["bbs"]["result_id"]),
    ):
        same(
            f"rendered {label} identity",
            f"{label}: {identity}" in report.preformatted[0],
            True,
        )


def reconcile(directory, *, counts, loads, mass, failing=False):
    calculation = directory / "calculation.json"
    schedule_csv = directory / "bbs.csv"
    html = directory / "report.html"
    data = json.loads(calculation.read_text(encoding="utf-8"))
    results = data["results"]
    member = results["member"]["outputs"]["member_design"]
    package = results["package"]["outputs"]["calculation_package"]
    paths = results["paths"]["outputs"]["reinforcement_schedule"]
    bbs = results["bbs"]["outputs"]["bbs"]
    quantities = results["quantities"]["outputs"]["quantities"]
    same(
        "member state", results["member"]["engineering"], "fail" if failing else "pass"
    )
    same("package state", package["issue_state"], "draft" if failing else "issue_ready")
    same("professional approval", package["active_approval"], False)
    same(
        "retained schedule, BBS and quantities",
        (
            package["reinforcement_schedule"],
            package["bbs"],
            package["quantities"],
        ),
        (paths, bbs, quantities),
    )
    same(
        "topology revision",
        paths["topology_revision_id"],
        member["topology_revision_id"],
    )
    for revision in (
        paths["detail_revision_id"],
        bbs["detail_revision_id"],
        quantities["detail_revision_id"],
    ):
        same(
            "physical reinforcement revision",
            revision,
            member["reinforcement_revision_id"],
        )
    same("BBS path result", bbs["schedule_result_id"], results["paths"]["result_id"])
    same(
        "quantity BBS result", quantities["bbs_result_id"], results["bbs"]["result_id"]
    )
    same(
        "package result bindings",
        [r["result_id"] for r in package["dependency_bindings"]],
        [
            results[name]["result_id"]
            for name in ("member", "paths", "bbs", "quantities")
        ],
    )
    same(
        "400 mm support widths",
        [
            row["right_face_x_mm"] - row["left_face_x_mm"]
            for row in results["topology"]["outputs"]["supports"]
        ],
        [400, 400],
    )
    for role, load in zip(("ULS", "SLS"), loads, strict=True):
        request = results[f"analysis-{role}"]["effective_inputs"]["request"]["value"]
        same("analysis load case", request["load_case_id"], role)
        same(f"{role} load", request["elements"][0]["uniform_load_n_per_mm"], -load)

    leaves = package["leaves"]
    same("required check count", len(leaves), counts[0])
    same(
        "required check IDs",
        Counter(leaf["leaf_id"] for leaf in leaves),
        Counter(leaf["leaf_id"] for leaf in member["expected_leaves"]),
    )
    checks = {
        check["expectation"]["leaf_id"]: check
        for check in member["leaf_qualifications"]
    }
    same("qualified check IDs", set(checks), {leaf["leaf_id"] for leaf in leaves})
    result_ids = {result["result_id"] for result in results.values()}
    for leaf in leaves:
        check = checks[leaf["leaf_id"]]
        evidence = check["evidence"]
        same(
            "member leaf state",
            (leaf["qualified"], leaf["reason_codes"]),
            (check["qualified"], check["reason_codes"]),
        )
        for label, field in (
            ("result_id", "result_id"),
            ("required_value", "required_value"),
            ("provided_value", "supplied_value"),
            ("selected_value", "selected_value"),
            ("unit", "unit"),
            ("utilization", "governing_utilization"),
        ):
            same(f"{leaf['leaf_id']} {label}", leaf[label], evidence[field])
        same(
            "leaf result is in calculation JSON", leaf["result_id"] in result_ids, True
        )
    failed = {
        leaf["leaf_id"]: leaf["reason_codes"]
        for leaf in leaves
        if not leaf["qualified"]
    }
    if failing:
        same("insufficient flexure fails", failed.get("flexure@B1"), ["LEAF.FAIL"])
    else:
        same("qualified check set", failed, {})

    by_id = {path["bar_id"]: path for path in paths["paths"]}
    same(
        "unique physical paths",
        (len(paths["paths"]), len(by_id)),
        (counts[1], counts[1]),
    )
    grouped = {
        path_id: row for row in bbs["rows"] for path_id in row["source_path_ids"]
    }
    same(
        "BBS partition of physical paths",
        Counter(path_id for row in bbs["rows"] for path_id in row["source_path_ids"]),
        Counter(by_id.keys()),
    )
    for row in bbs["rows"]:
        same("BBS bar count", row["scheduled_bar_count"], len(row["source_path_ids"]))
        mass_kg = (
            row["scheduled_cut_length_mm"]
            * math.pi
            * row["diameter_mm"] ** 2
            / 4
            * 7850
            / 1e9
        )
        near("BBS row mass", row["theoretical_mass_kg"], mass_kg)
    near(
        "sum of scheduled steel mass",
        math.fsum(row["theoretical_mass_kg"] for row in bbs["rows"]),
        mass,
    )
    near("BBS scheduled steel mass", bbs["scheduled_steel_mass_kg"], mass)
    near("quantity scheduled steel mass", quantities["steel_scheduled_mass_kg"], mass)
    with schedule_csv.open(encoding="utf-8", newline="") as stream:
        csv_rows = list(csv.DictReader(stream))
    same(
        "CSV physical path IDs",
        Counter(row["bar_id"] for row in csv_rows),
        Counter(by_id.keys()),
    )
    for row in csv_rows:
        path = by_id[row["bar_id"]]
        group = grouped[row["bar_id"]]
        same("scheduled path mark", group["bar_mark"], path["bar_mark"])
        near("scheduled path diameter", group["diameter_mm"], path["diameter_mm"])
        same(
            "CSV status and provenance",
            (row["issue_state"], row["path_result_id"], row["bbs_result_id"]),
            (
                package["issue_state"],
                results["paths"]["result_id"],
                results["bbs"]["result_id"],
            ),
        )
        same(
            "CSV mark and shape",
            (row["mark"], row["shape_code"]),
            (path["bar_mark"], group["shape_code"]),
        )
        near("CSV diameter", float(row["diameter_mm"]), path["diameter_mm"])
        near(
            "CSV cut length",
            float(row["fabrication_cut_length_mm"]),
            group["fabrication_cut_length_each_mm"],
        )
        near(
            "BBS path centreline length",
            group["centreline_developed_length_each_mm"],
            path["developed_centreline_length_mm"],
        )
        near(
            "CSV path length",
            float(row["length_mm"]),
            math.fsum(s["centreline_length_mm"] for s in path["segments"]),
        )

    report_text = html.read_text(encoding="utf-8")
    report_checks(Report(report_text), package, results, bbs)
    if counts[0] == 27:
        same(
            "multilayer rendered load basis",
            f"ULS/SLS total loads {loads[0]}/{loads[1]} N/mm" in report_text,
            True,
        )
    return {
        "member": results["member"]["engineering"],
        "issue_state": package["issue_state"],
        "required_checks": counts[0],
        "physical_bars": counts[1],
        "scheduled_steel_kg": bbs["scheduled_steel_mass_kg"],
        "loads_n_per_mm": dict(zip(("ULS", "SLS"), loads, strict=True)),
        "unqualified_leaves": failed,
        "professional_approval": package["active_approval"],
        "sha256": {
            file.name: hashlib.sha256(file.read_bytes()).hexdigest()
            for file in (calculation, schedule_csv, html)
        },
    }


def supplied_controls(output):
    def request():
        return {
            "correlation_id": "LIB-12-control",
            "identity": {"member_id": "B1", "story": "control", "case_id": "ULS"},
            "section": {
                "b_mm": 300,
                "D_mm": 500,
                "effective_depth_basis": {
                    "clear_cover_mm": 40,
                    "stirrup_diameter_mm": 8,
                    "tension_bar_diameter_mm": 20,
                },
            },
            "materials": {"fck_nmm2": 25, "fy_nmm2": 500, "fy_transverse_nmm2": 415},
            "actions": {"mu_knm": 150, "vu_kn": 60, "primary_tension_face": "BOTTOM"},
            "reinforcement": {
                "clear_cover_mm": 40,
                "tension": {"diameter_mm": 20, "bars_per_layer": [4]},
                "compression_or_hanger": {"diameter_mm": 12, "bars_per_layer": [2]},
                "stirrup_diameter_mm": 8,
                "stirrup_legs": 2,
                "stirrup_spacing_mm": 150,
                "bar_type": "deformed",
                "has_standard_bend_at_start": True,
                "has_standard_bend_at_end": True,
                "source_reference": "LIB-12 diagnostic",
            },
            "selection": {
                "permitted_diameters_mm": [12, 16, 20, 25],
                "maximum_layers": 2,
                "maximum_bars_per_layer": 8,
                "nominal_max_aggregate_size_mm": 20,
                "effective_depth_tolerance_mm": 1,
                "objective": "min_area",
                "source_reference": "LIB-12 diagnostic",
            },
            "support": {
                "start_width_mm": 2000,
                "end_width_mm": 2000,
                "source_reference": "LIB-12 isolated control",
            },
            "source_provenance": "LIB-12 supplied-check diagnostic",
        }

    cases = {}
    for name, status, issues in (
        ("adequate", "PASS", []),
        ("missing_support_width", "HOLD", ["BEAM_SUPPORT_WIDTH_BASIS_NOT_SUPPLIED"]),
        ("conflicting_depth", "FAIL", ["BEAM_SUPPLIED_EFFECTIVE_DEPTH_MISMATCH"]),
        (
            "insufficient_reinforcement",
            "FAIL",
            ["BEAM_TENSION_REINFORCEMENT_AREA_INSUFFICIENT"],
        ),
    ):
        payload = request()
        if name == "missing_support_width":
            payload["support"] = None
        elif name == "conflicting_depth":
            payload["section"] = {"b_mm": 300, "D_mm": 500, "d_mm": 440}
        elif name == "insufficient_reinforcement":
            payload["reinforcement"]["tension"]["bars_per_layer"] = [2]
        result = beam.check_supplied(beam.load_supplied_check(payload))
        same(name, result.status, status)
        same(f"{name} disposition", result.result_envelope.overall_status.value, status)
        same(
            f"{name} issue codes",
            [item.code for item in result.result_envelope.issues],
            issues,
        )
        path = output / f"{name}.json"
        path.write_text(
            json.dumps(result.to_dict(), indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        cases[name] = {
            "status": status,
            "issue_codes": issues,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        if name == "insufficient_reinforcement":
            area = result.longitudinal.checks["tension_area"]
            near("provided steel", area["provided_mm2"], 628.3185307179587)
            near("required steel", area["required_mm2"], 905.7458469878037)
            cases[name].update(
                required_mm2=area["required_mm2"], provided_mm2=area["provided_mm2"]
            )
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--example", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    origin = Path(structural_lib.__file__).resolve()
    same(
        "installed package origin",
        origin.is_relative_to(sys.prefix) and "site-packages" in origin.parts,
        True,
    )
    example = args.example.resolve()
    output = args.output_dir.resolve()
    output.mkdir(parents=True)
    driver = runpy.run_path(str(example))
    cases = {}
    for name, counts, loads, mass, overload in (
        ("single-layer", (19, 39), (12, 8), 56.95229312438693, 40),
        ("multilayer", (27, 43), (36, 24), 129.91458084481988, 100),
    ):
        subprocess.run(
            [
                sys.executable,
                "-I",
                str(example),
                "--case",
                name,
                "--output-dir",
                str(output / name),
            ],
            cwd=output,
            capture_output=True,
            text=True,
            check=True,
        )
        cases[name] = reconcile(output / name, counts=counts, loads=loads, mass=mass)
        failed_name = f"{name}-insufficient-for-demand"
        failed = driver["run_workflow"](
            multilayer=name == "multilayer", ultimate_load_n_per_mm=overload
        )
        driver["write_artifacts"](failed, output / failed_name)
        cases[failed_name] = reconcile(
            output / failed_name,
            counts=counts,
            loads=(overload, loads[1]),
            mass=mass,
            failing=True,
        )
    print(
        json.dumps(
            {
                "installed_version": version("structural-lib-is456"),
                "package_origin": "site-packages",
                "member_cases": cases,
                "supplied_check_controls": supplied_controls(output),
            },
            indent=2,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
