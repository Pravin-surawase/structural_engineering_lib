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
        "test_torsion_corner_geometry",
        "test_physical_torsion_member",
        "test_torsional_serviceability",
        "test_t_beam_member",
        "test_complete_member_workflow",
        "test_flanged_branch_equilibrium",
    )
) + (
    "Python/tests/test_calculation_report.py",
    "Python/tests/test_public_examples.py",
)
EXAMPLES = tuple(
    f"Python/examples/{name}.py"
    for name in (
        "beam_comparator_reference",
        "layered_column_section",
        "beam_section_closure",
        "four_corner_column_member",
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
)


def input_paths(repo: Path) -> tuple[Path, ...]:
    """Exact transitive driver/fixture inventory; never a source-package glob."""
    return tuple(
        sorted(
            {
                *(repo / name for name in (*TESTS, *EXAMPLES, *CHECKERS)),
                *(repo / "docs/verification").glob("library-027-*.json"),
                repo / "docs/verification/replay_library_027_members.py",
                repo / "docs/verification/replay_library_027_t_member.py",
                repo / "Python/examples/sample_beam_design.csv",
                repo
                / "Python/tests/data/benchmark_vectors/flanged_branch_reference.json",
                repo
                / "contracts/structural-engineering/conformance/wp01-per-bar-vectors.json",
                repo / "docs/reference/api.md",
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

    def run(label: str, script: str, *args: str) -> str:
        completed = subprocess.run(
            [sys.executable, "-I", str(clone / script), *args],
            cwd=clone,
            capture_output=True,
            text=True,
            timeout=300,
        )
        (output / f"{label}.stdout.log").write_text(completed.stdout)
        (output / f"{label}.stderr.log").write_text(completed.stderr)
        if completed.returncode:
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
