"""Copied-driver qualification of the selected 0.27 beam/column corpus.

This owner runs inside a fresh archive installation with declared dev/dxf/report
extras. Verification tools are separate from the base-only installed profiles.
No package source or repository conftest is copied into the neutral driver tree.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

TESTS = tuple(
    f"Python/tests/integration/{name}.py"
    for name in (
        "test_beam_comparator_example",
        "test_layered_column_section",
        "test_beam_section_closure",
        "test_four_corner_column_member",
        "test_tied_rectangular_column_member",
        "test_positioned_rectangular_column_member",
        "test_slender_rectangular_column_member",
        "test_circular_column_member",
        "test_column_candidate_search",
        "test_column_member_detailing",
        "test_torsion_corner_geometry",
        "test_beam_primary_route_torsion",
        "test_physical_torsion_member",
        "test_torsional_serviceability",
        "test_t_beam_member",
        "test_complete_member_workflow",
        "test_flanged_branch_equilibrium",
        "test_release_027_consumer_repairs",
    )
) + (
    "Python/tests/test_calculation_report.py",
    "Python/tests/test_public_examples.py",
    "Python/tests/unit/test_structural_engineering_wp07.py",
    "Python/tests/unit/test_structural_engineering_wp08.py",
)
EXAMPLES = tuple(
    f"Python/examples/{name}.py"
    for name in (
        "beam_comparator_reference",
        "layered_column_section",
        "beam_section_closure",
        "four_corner_column_member",
        "tied_rectangular_column_member",
        "positioned_rectangular_column_member",
        "slender_rectangular_column_member",
        "circular_column_member",
        "column_catalogue_selection",
        "column_member_detailing",
        "torsion_station_reference",
        "physical_torsion_member",
        "t_beam_member",
        "complete_member_workflow",
        "canonical_workflows",
        "full_pipeline_synthetic",
    )
)
CHECKERS = tuple(
    f"docs/verification/check_library_027_{name}.py"
    for name in (
        "references",
        "beam_section_reference",
        "four_corner_reference",
        "torsion_reference",
        "torsion_physical_reference",
        "torsion_serviceability_reference",
        "t_beam_reference",
    )
) + (
    "docs/verification/check_library_029_col02_reference.py",
    "docs/verification/check_library_029_col03_reference.py",
    "docs/verification/check_library_029_col04_reference.py",
    "docs/verification/check_library_029_col05_reference.py",
    "docs/verification/check_library_029_col06_reference.py",
    "docs/verification/check_library_029_col07_reference.py",
)
COL03_REFERENCE = "docs/verification/library-029-col03-mixed-column.json"
COL04_REFERENCE = "docs/verification/library-029-col04-slender-column.json"
COL05_REFERENCE = "docs/verification/library-029-col05-circular-column.json"
COL06_REFERENCE = "docs/verification/library-029-col06-column-catalogue.json"
COL07_REFERENCE = "docs/verification/library-029-col07-column-member.json"


def input_paths(repo: Path) -> tuple[Path, ...]:
    """Exact transitive driver/fixture inventory; never a source-package glob."""
    return tuple(
        sorted(
            {
                *(repo / name for name in (*TESTS, *EXAMPLES, *CHECKERS)),
                *(repo / "docs/verification").glob("library-027-*.json"),
                repo / "docs/verification/library-029-col02-rectangular-column.json",
                repo / COL03_REFERENCE,
                repo / COL04_REFERENCE,
                repo / COL05_REFERENCE,
                repo / COL06_REFERENCE,
                repo / COL07_REFERENCE,
                repo / "docs/verification/replay_library_027_members.py",
                repo / "docs/verification/replay_library_027_t_member.py",
                repo / "Python/examples/sample_beam_design.csv",
                repo
                / "Python/tests/data/benchmark_vectors/flanged_branch_reference.json",
                repo
                / "contracts/structural-engineering/conformance/wp01-per-bar-vectors.json",
                repo / "docs/reference/api.md",
                repo / "docs/developers/platform-guide.md",
                repo / "scripts/external_cli_test.py",
                *(
                    repo / "docs/getting-started" / name
                    for name in (
                        "python-quickstart.md",
                        "beginners-guide.md",
                        "colab-workflow.md",
                    )
                ),
            }
        )
    )


def qualify_consumer_journeys(
    config: dict[str, Any], *, drawing: bool = False, pdf: bool = False
) -> dict[str, Any]:
    """Replay the copied developer guide and accepted report controls."""
    import contextlib
    import re
    import shutil
    from dataclasses import replace

    from structural_lib import api
    from structural_lib.reports import generator

    target = Path(config["output"]) / "consumer-journeys"
    target.mkdir(parents=True, exist_ok=True)
    guide = target / "platform-guide.md"
    shutil.copyfile(Path(config["repo"]) / "docs/developers/platform-guide.md", guide)
    blocks = re.findall(r"```python\n(.*?)```", guide.read_text(encoding="utf-8"), re.S)
    namespace: dict[str, Any] = {}
    markers = ["# quick_start_example.py", "# verify_quickstart_outputs"]
    if drawing:
        markers.append("# optional_dxf_export")
    if pdf:
        markers.append("# optional_pdf_export")
    with contextlib.chdir(target):
        for marker in markers:
            block = next(block for block in blocks if marker in block)
            exec(compile(block, str(guide), "exec"), namespace)
    if len(namespace["schedule"].items) != 9:
        raise AssertionError("Developer quickstart schedule changed")
    template_html = (target / "beam_B1_outputs/beam_B1.template.html").read_text(
        encoding="utf-8"
    )
    badge = re.search(
        r'<span class="(?:status-badge [^"]+|status)">\s*([^<]+)', template_html
    )
    if badge is None or badge[1].strip() != "PASS":
        raise AssertionError(
            "Canonical overall report badge disagrees with the source PASS"
        )
    common = dict(
        units="IS456",
        b_mm=300,
        D_mm=500,
        d_mm=444,
        fck_nmm2=25,
        fy_nmm2=500,
        mu_knm=150,
        vu_kn=100,
    )
    controls = {}
    combined = api.design_and_detail_beam_is456(
        **common, beam_id="B-FAIL", story="L1", span_mm=6000, cover_mm=40
    )
    invalid_detail = replace(
        combined.detailing,
        is_valid=False,
        remarks="Controlled source detailing failure",
    )
    invalid_report = api.generate_calculation_report(
        replace(combined, detailing=invalid_detail, is_ok=False)
    )
    invalid_data = invalid_report.to_dict()
    if (
        invalid_data["result_envelope"]["engineering_status"] != "FAIL"
        or "detailing_invalid"
        not in invalid_data["results"]["summary"]["failed_checks"]
    ):
        raise AssertionError(
            "Invalid detailing exported a contradictory aggregate envelope"
        )
    invalid_report.export_json(target / "detailing-failure.json")
    invalid_report.export_html(target / "detailing-failure.html")
    invalid_report.export_markdown(target / "detailing-failure.markdown")
    if pdf:
        from weasyprint import HTML

        HTML(filename=str(target / "detailing-failure.html")).write_pdf(
            target / "detailing-failure.pdf"
        )
    controls["detailing-failure"] = {
        "engineering_status": "FAIL",
        "failed_checks": invalid_report.results.summary["failed_checks"],
    }
    for name, params, expected in (
        ("design-only", {}, "PASS"),
        (
            "deflection-failure",
            {
                "deflection_params": {
                    "span_mm": 10000,
                    "d_mm": 444,
                    "support_condition": "simply_supported",
                    "mf_tension_steel": 0.5,
                }
            },
            "FAIL",
        ),
    ):
        result = api.design_beam_is456(**common, **params)
        report = api.generate_calculation_report(result)
        if report.results.summary["engineering_status"] != expected:
            raise AssertionError(f"{name} report changed engineering status")
        if expected == "FAIL" and report.results.summary["failed_checks"] != [
            "deflection"
        ]:
            raise AssertionError("Evaluated serviceability failure disappeared")
        if (
            report.inputs.loads[0]["mu_knm"] != 150
            or report.inputs.materials["fck_nmm2"] != 25
        ):
            raise AssertionError("Report lost retained action/material basis")
        for fmt in ("json", "html", "markdown"):
            getattr(report, f"export_{fmt}")(target / f"{name}.{fmt}")
        (target / f"{name}.template.html").write_text(
            generator.generate_html_report(result), encoding="utf-8"
        )
        if pdf:
            from weasyprint import HTML

            HTML(filename=str(target / f"{name}.html")).write_pdf(
                target / f"{name}.pdf"
            )
        controls[name] = {
            "engineering_status": expected,
            "failed_checks": report.results.summary["failed_checks"],
        }
    return {
        "status": "PASS",
        "guide_sha256": hashlib.sha256(guide.read_bytes()).hexdigest(),
        "source_status": namespace["result"].engineering_status.value,
        "review_status": namespace["report"].source["envelope"]["review_status"],
        "bbs_rows": len(namespace["schedule"].items),
        "jinja2_available": generator.JINJA2_AVAILABLE,
        "drawing": drawing,
        "pdf": pdf,
        "controls": controls,
        "files": {
            str(path.relative_to(target)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(target.rglob("*"))
            if path.is_file()
        },
    }


def qualify(config: dict[str, Any]) -> dict[str, Any]:
    """Replay all selected references, tests and public drivers from installation."""
    import shutil

    import pytest

    repo, output = Path(config["repo"]), Path(config["output"])
    clone = Path.cwd() / "beam-column-drivers"
    hashes = {}
    for source in input_paths(repo):
        relative = source.relative_to(repo)
        target = clone / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        hashes[str(relative)] = hashlib.sha256(source.read_bytes()).hexdigest()
    if (clone / "Python/structural_lib").exists():
        raise AssertionError("Qualification drivers contain package source")
    output.mkdir(parents=True, exist_ok=True)
    commands = []

    def run(label: str, script: str, *args: str, expected_code: int = 0) -> str:
        command = [sys.executable, "-I"]
        if script in CHECKERS:
            # -I deliberately excludes the script directory. These arithmetic
            # drivers share sibling helpers; expose only their copied folder.
            command.extend(
                (
                    "-c",
                    "import runpy,sys;from pathlib import Path;"
                    "sys.argv=sys.argv[1:];"
                    "sys.path.insert(0,str(Path(sys.argv[0]).parent));"
                    "runpy.run_path(sys.argv[0],run_name='__main__')",
                )
            )
        command.extend((str(clone / script), *args))
        completed = subprocess.run(
            command,
            cwd=clone,
            capture_output=True,
            text=True,
            timeout=300,
        )
        (output / f"{label}.stdout.log").write_text(completed.stdout)
        (output / f"{label}.stderr.log").write_text(completed.stderr)
        if completed.returncode != expected_code:
            raise AssertionError(
                f"Installed {label} failed: {completed.returncode}\n"
                f"{completed.stderr[-4000:]}\n{completed.stdout[-4000:]}"
            )
        commands.append({"id": label, "script": script, "status": "PASS"})
        return completed.stdout

    for checker in CHECKERS:
        run(Path(checker).stem, checker)
    for name in (
        "beam_comparator_reference",
        "layered_column_section",
        "beam_section_closure",
        "torsion_station_reference",
    ):
        stdout = run(name, f"Python/examples/{name}.py")
        payload = json.loads(stdout)
        (output / f"{name}.json").write_text(json.dumps(payload, indent=2) + "\n")
        if name == "torsion_station_reference":
            from structural_lib import beam

            assert payload["member_admission"] == "HOLD"
            for case, expected in (
                ("adequate_links", beam.EngineeringState.PASS),
                ("corner_geometry_shortfall", beam.EngineeringState.FAIL),
            ):
                assert payload["station_results"][case]["engineering"] == expected
    run(
        "four-corner",
        "Python/examples/four_corner_column_member.py",
        "--output-dir",
        str(output / "four-corner"),
    )
    for layout in (
        "eight_bar",
        "six_bar_omit_x_face_midpoints",
        "six_bar_omit_y_face_midpoints",
    ):
        label = f"tied-rectangular-{layout}"
        directory = output / label
        stdout = run(
            label,
            "Python/examples/tied_rectangular_column_member.py",
            "--layout",
            layout,
            "--output-dir",
            str(directory),
        )
        member = json.loads(stdout)
        assert member == json.loads((directory / "result.json").read_text())
        assert member["envelope"]["engineering_status"] == "PASS"
        assert member["calculation"]["layout"] == layout
        input_hash = member["envelope"]["result_identity"]["input_hash"]
        assert input_hash in (directory / "report.html").read_text()
    col03_cases = json.loads((clone / COL03_REFERENCE).read_text())["cases"]
    for case, expected in col03_cases.items():
        label = f"positioned-rectangular-{case}"
        directory = output / label
        stdout = run(
            label,
            "Python/examples/positioned_rectangular_column_member.py",
            "--case",
            case,
            "--output-dir",
            str(directory),
        )
        member = json.loads(stdout)
        assert member == json.loads((directory / "result.json").read_text())
        assert member["envelope"]["engineering_status"] == expected["member_status"]
        input_hash = member["envelope"]["result_identity"]["input_hash"]
        assert input_hash in (directory / "report.html").read_text()
    col04_cases = json.loads((clone / COL04_REFERENCE).read_text())["cases"]
    for case in (
        "minor_slender",
        "both_slender",
        "mixed",
        "supplied_second_order",
        "overload",
        "stale_revision",
        "conflicting_summary",
    ):
        label = f"slender-rectangular-{case}"
        directory = output / label
        expected = col04_cases[case]["expected"]
        reject = expected["member_status"] == "REJECT"
        stdout = run(
            label,
            "Python/examples/slender_rectangular_column_member.py",
            "--reference",
            str(clone / COL04_REFERENCE),
            "--case",
            case,
            "--output-dir",
            str(directory),
            expected_code=2 if reject else 0,
        )
        member = json.loads(stdout)
        if reject:
            assert member["details"]["issues"][0]["code"] == expected["issue"]
            assert not directory.exists()
        else:
            assert member == json.loads((directory / "result.json").read_text())
            assert member["envelope"]["engineering_status"] == expected["member_status"]
            input_hash = member["envelope"]["result_identity"]["input_hash"]
            assert input_hash in (directory / "report.html").read_text()
            assert input_hash in (directory / "section.svg").read_text()
    col05_cases = json.loads((clone / COL05_REFERENCE).read_text())["cases"]
    for case in (
        "tied",
        "spiral",
        "spiral_wide",
        "spiral_ordinary_wide",
        "axial_tied",
        "axial_spiral",
        "spiral_missing_anchor",
        "overload",
    ):
        label = f"circular-column-{case}"
        directory = output / label
        stdout = run(
            label,
            "Python/examples/circular_column_member.py",
            "--reference",
            str(clone / COL05_REFERENCE),
            "--case",
            case,
            "--output-dir",
            str(directory),
        )
        member = json.loads(stdout)
        assert member == json.loads((directory / "result.json").read_text())
        assert (
            member["envelope"]["engineering_status"]
            == col05_cases[case]["expected"]["member_status"]
        )
        input_hash = member["envelope"]["result_identity"]["input_hash"]
        assert input_hash in (directory / "report.html").read_text()
        assert input_hash in (directory / "section.svg").read_text()
    col06_cases = json.loads((clone / COL06_REFERENCE).read_text())["cases"]
    for case, entry in col06_cases.items():
        label = f"column-catalogue-{case}"
        directory = output / label
        stdout = run(
            label,
            "Python/examples/column_catalogue_selection.py",
            "--reference",
            str(clone / COL06_REFERENCE),
            "--case",
            case,
            "--output-dir",
            str(directory),
        )
        result = json.loads(stdout)
        assert result == json.loads((directory / "result.json").read_text())
        expected = entry["expected"]
        calculation = result["calculation"]
        assert (
            result["envelope"]["engineering_status"] == expected["engineering_status"]
        )
        assert calculation["terminal_state"] == expected["terminal_state"]
        assert calculation["selected_id"] == expected["selected_id"]
        input_hash = result["envelope"]["result_identity"]["input_hash"]
        report = (directory / "report.html").read_text()
        drawing = directory / "section.svg"
        assert input_hash in report
        if expected["selected_id"] is None:
            assert not drawing.exists()
        else:
            child = calculation["selected"]["checked_member"]
            child_hash = child["envelope"]["result_identity"]["input_hash"]
            assert child_hash in report
            svg = drawing.read_text()
            assert input_hash in svg and child_hash in svg
            ElementTree.fromstring(svg)
    col07_cases = json.loads((clone / COL07_REFERENCE).read_text())["cases"]
    for case, entry in col07_cases.items():
        label = f"column-member-detailing-{case}"
        directory = output / label
        stdout = run(
            label,
            "Python/examples/column_member_detailing.py",
            "--reference",
            str(clone / COL07_REFERENCE),
            "--case",
            case,
            "--output-dir",
            str(directory),
        )
        member = json.loads(stdout)
        assert member == json.loads((directory / "result.json").read_text())
        assert member["envelope"]["engineering_status"] == entry["expected"]["status"]
        input_hash = member["envelope"]["result_identity"]["input_hash"]
        assert input_hash in (directory / "report.html").read_text()
        drawing = (directory / "member.svg").read_text()
        assert input_hash in drawing
        ElementTree.fromstring(drawing)
        bbs = directory / "bbs.csv"
        assert bbs.is_file() == entry["expected"]["bbs_available"]
        if bbs.is_file():
            assert input_hash in bbs.read_text()
    for name, args in (("d2-hold", ()), ("d3-pass", ("--with-serviceability",))):
        run(
            name,
            "Python/examples/physical_torsion_member.py",
            "--output-dir",
            str(output / name),
            *args,
        )
    run(
        "ordinary-members",
        "docs/verification/replay_library_027_members.py",
        "--example",
        str(clone / "Python/examples/complete_member_workflow.py"),
        "--output-dir",
        str(output / "ordinary-members"),
    )
    run(
        "t-members",
        "docs/verification/replay_library_027_t_member.py",
        "--example",
        str(clone / "Python/examples/t_beam_member.py"),
        "--output-dir",
        str(output / "t-members"),
        "--require-site-packages",
    )
    configuration = clone / "pytest.ini"
    configuration.write_text("[pytest]\n")
    junit = output / "beam-column-consumer-tests.xml"
    code = pytest.main(
        [
            "-q",
            "-c",
            str(configuration),
            "--confcutdir",
            str(clone),
            "--import-mode=importlib",
            "--basetemp",
            str(output / "test-artifacts"),
            "--junitxml",
            str(junit),
            *(str(clone / name) for name in TESTS),
        ]
    )
    suites = ElementTree.parse(junit).getroot().findall("testsuite")
    counts = {
        key: sum(int(suite.attrib.get(key, 0)) for suite in suites)
        for key in ("tests", "failures", "errors", "skipped")
    }
    if (
        code != 0
        or not counts["tests"]
        or any(counts[key] for key in ("failures", "errors", "skipped"))
    ):
        raise AssertionError(f"Installed beam/column consumer tests failed: {counts}")
    return {
        "status": "PASS",
        "verification_tools": "Declared dev,dxf,report extras; separate from base-only profiles",
        "driver_inputs_sha256": hashes,
        "commands": commands,
        "tests": counts,
        "junit": str(junit),
        "t_member_journeys": json.loads(
            (output / "t-members/receipt.json").read_text()
        ),
        "professional_approval": False,
    }
