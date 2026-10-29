"""Isolated child for the release qualification owner; execute with Python -I."""

from __future__ import annotations

import csv
import hashlib
import importlib
import importlib.metadata
import json
import math
import platform
import runpy
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def assert_installed(config: dict[str, Any]) -> dict[str, str]:
    import structural_lib
    from structural_lib.core.version import get_runtime_version_identity

    prefix = Path(config["venv"]).resolve()
    origin = Path(structural_lib.__file__).resolve()
    if not origin.is_relative_to(prefix):
        raise AssertionError(f"Checkout/foreign package import: {origin}")
    version = importlib.metadata.version("structural-lib-is456")
    if version != config["version"]:
        raise AssertionError(f"Installed {version}, expected {config['version']}")
    for name, module in list(sys.modules.items()):
        location = getattr(module, "__file__", None)
        if name.startswith("structural_lib") and location:
            if not Path(location).resolve().is_relative_to(prefix):
                raise AssertionError(f"Foreign module {name}: {location}")
    identity = get_runtime_version_identity(origin).to_dict()
    if identity["execution_mode"] != "INSTALLED_DISTRIBUTION":
        raise AssertionError(identity)
    for name, digest in config["package_files"].items():
        actual = origin.parent.parent / name
        if (
            not actual.is_file()
            or hashlib.sha256(actual.read_bytes()).hexdigest() != digest
        ):
            raise AssertionError(f"Installed package payload drift: {name}")
    return {
        "origin": str(origin),
        "version": version,
        "execution_mode": identity["execution_mode"],
    }


def _families(repo: Path, budgets: dict[str, float]) -> dict[str, Any]:
    # Import only the repository's verification driver, never its Python tree.
    from scripts.verify_lib_pro_013_f0_family_artifact import recipe_specs, run_recipes

    data = repo / "Python/tests/data/benchmark_vectors"
    inputs = json.loads((data / "family_review_inputs.json").read_text())["cases"]
    references = json.loads((data / "family_review_reference.json").read_text())[
        "cases"
    ]
    recipes = recipe_specs()
    if len(recipes) != len(references) or len(recipes) != 13:
        raise AssertionError("Family population is not thirteen")
    contracts = run_recipes()
    comparisons = []
    timings = []
    for recipe, frozen, reference in zip(recipes, inputs, references, strict=True):
        if recipe.payload != frozen["request"]:
            raise AssertionError("Frozen family input drift")
        encoded = json.dumps(recipe.payload, sort_keys=True, separators=(",", ":"))
        if hashlib.sha256(encoded.encode()).hexdigest() != reference["request_sha256"]:
            raise AssertionError("Frozen family request hash drift")
        module = importlib.import_module(recipe.module)
        operation, load = getattr(module, recipe.operation), getattr(
            module, recipe.loader
        )
        request = load(recipe.payload)
        actual = operation(request).to_dict()
        timing = _timed(lambda: operation(load(recipe.payload)), 5, 1)
        if timing["p95_ms"] > budgets["family_p95_ms"]:
            raise AssertionError(f"Family exceeds frozen budget: {recipe.journey_id}")
        timings.append({"journey": recipe.journey_id, **timing})
        if (
            actual["envelope"]["engineering_status"]
            != reference["expected_engineering_status"]
        ):
            raise AssertionError("Family PASS/FAIL/HOLD drift")
        for metric in reference["metrics"]:
            value = actual
            for key in metric["path"].split("."):
                value = value[int(key)] if isinstance(value, list) else value[key]
            if not math.isfinite(value) or not math.isclose(
                value,
                metric["expected"],
                abs_tol=metric["absolute_tolerance"],
                rel_tol=metric["relative_tolerance"],
            ):
                raise AssertionError(
                    f"{recipe.journey_id} {metric['path']} {value} != {metric['expected']} [{metric['unit']}]"
                )
            comparisons.append(
                {"journey": recipe.journey_id, **metric, "actual": value}
            )
    if len(comparisons) != 106:
        raise AssertionError("Independent numerical population drift")
    return {
        "contracts": contracts,
        "numerical_metric_count": len(comparisons),
        "comparisons": comparisons,
        "performance": timings,
        "reference_sha256": hashlib.sha256(
            (data / "family_review_reference.json").read_bytes()
        ).hexdigest(),
    }


def _timed(function: Any, samples: int, warmups: int = 3) -> dict[str, float]:
    for _ in range(warmups):
        function()
    values = []
    for _ in range(samples):
        started = time.perf_counter()
        function()
        values.append((time.perf_counter() - started) * 1000)
    return {
        "samples": samples,
        "median_ms": statistics.median(values),
        "p95_ms": sorted(values)[math.ceil(0.95 * len(values)) - 1],
        "errors": 0,
    }


def _performance(config: dict[str, Any]) -> dict[str, Any]:
    from structural_lib.services.beam_api import design_beam_is456
    from structural_lib.services.batch import design_project_beams_v1

    def beam() -> None:
        result = design_beam_is456(
            units="IS456",
            b_mm=300,
            D_mm=500,
            d_mm=450,
            mu_knm=150,
            vu_kn=75,
            fck_nmm2=25,
            fy_nmm2=415,
        )
        if not result.is_ok:
            raise AssertionError("Performance case must remain engineering PASS")

    members = [
        dict(
            schema_version="project-beam-design/v1",
            member_id=f"S5-{i}",
            b_mm=300.0,
            D_mm=500.0,
            d_mm=450.0,
            mu_knm=150.0,
            vu_kn=75.0,
            fck_nmm2=25.0,
            fy_nmm2=415.0,
        )
        for i in range(100)
    ]

    def batch() -> None:
        result = design_project_beams_v1(members, units="IS456").to_dict()
        if len(result["members"]) != 100 or any(
            row["engineering_status"] != "PASS" for row in result["members"]
        ):
            raise AssertionError("Batch performance case changed its outcomes")

    results = {"beam": _timed(beam, 25), "batch100": _timed(batch, 7)}
    for name, value in results.items():
        if value["p95_ms"] > config["budgets"][name + "_p95_ms"]:
            raise AssertionError(
                f"{name} exceeds its frozen performance budget: {value}"
            )
    return {
        **results,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "processor": platform.processor(),
        },
    }


def _physical(
    config: dict[str, Any], *, render: bool = False, pdf: bool = False
) -> list[dict[str, Any]]:
    import ezdxf

    repo, output = Path(config["repo"]), Path(config["output"])
    example = runpy.run_path(str(repo / "Python/examples/complete_member_workflow.py"))
    renderer = runpy.run_path(str(repo / "scripts/dxf_render.py")) if render else None
    records = []
    for name, multi in (("single-layer", False), ("multilayer", True)):
        workflow = example["run_workflow"](multilayer=multi)
        target = output / name
        example["write_artifacts"](workflow, target, include_dxf=True)
        document = ezdxf.readfile(target / "physical-beam.dxf")
        metadata = json.loads(
            "".join(
                tag.value
                for tag in document.rootdict["STRUCTLIB_PHYSICAL_METADATA"].tags
                if tag.code == 1000
            )
        )
        package = workflow.package
        if (
            metadata["package_id"] != package["calculation_package_id"]
            or metadata["issue_state"] != package["issue_state"]
            or metadata["active_approval"]
        ):
            raise AssertionError("Physical artifact identity/state drift")
        entities = list(document.modelspace().query('POLYLINE[layer=="PHYSICAL_3D"]'))
        circles = list(
            document.modelspace().query('CIRCLE[layer=="LONGITUDINAL_SECTION"]')
        )
        paths = workflow.package_request.schedule.paths
        if len(entities) != (43 if multi else 39) or len(circles) != (
            8 if multi else 4
        ):
            raise AssertionError("Physical path/section population drift")
        by_id = {e.get_xdata("STRUCTLIB_PHYSICAL")[1].value: e for e in entities}
        for path in paths:
            point = path.segments[0].start
            expected = (
                point.station_x_mm,
                point.section_x_from_left_mm,
                500 - point.section_y_from_top_mm,
            )
            if (
                math.dist(tuple(by_id[path.bar_id].vertices[0].dxf.location), expected)
                > 1e-7
            ):
                raise AssertionError(
                    "Physical bar endpoint differs from resolved source"
                )
            if (
                by_id[path.bar_id].get_xdata("STRUCTLIB_PHYSICAL")[4].value
                != path.layer
            ):
                raise AssertionError("Physical layer identity drift")
        with (target / "bbs.csv").open() as stream:
            rows = list(csv.DictReader(stream))
        if len(rows) != len(paths) or {row["path_result_id"] for row in rows} != {
            workflow.results["paths"].result_id
        }:
            raise AssertionError("CSV/path identity drift")
        steel = workflow.package_request.bbs.scheduled_steel_mass_kg
        if not math.isclose(
            steel, 129.91458084481988 if multi else 56.95229312438693, abs_tol=1e-8
        ):
            raise AssertionError("Physical mass differs from frozen S4 value")
        if render and renderer:
            renderer["render_dxf"](
                target / "physical-beam.dxf", target / "drawing.png", dpi=180, pad_mm=2
            )
            renderer["render_dxf"](
                target / "physical-beam.dxf", target / "drawing.pdf", dpi=200, pad_mm=2
            )
        if pdf:
            from weasyprint import HTML

            HTML(filename=str(target / "report.html")).write_pdf(target / "report.pdf")
        records.append(
            {
                "case": name,
                "package_id": package["calculation_package_id"],
                "path_result_id": workflow.results["paths"].result_id,
                "bbs_result_id": workflow.results["bbs"].result_id,
                "physical_bars": len(paths),
                "longitudinal_section_bars": len(circles),
                "steel_kg": steel,
                "issue_state": package["issue_state"],
                "active_approval": False,
                "files": [
                    {
                        "path": str(p),
                        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                    }
                    for p in sorted(target.iterdir())
                    if p.is_file()
                ],
            }
        )
    return records


def run_probe(config: dict[str, Any]) -> dict[str, Any]:
    repo = Path(config["repo"])
    sys.path.insert(0, str(repo))  # Verification drivers only; never repo/Python.
    before = assert_installed(config)
    profile = config["profile"]
    result: dict[str, Any] = {"identity_before": before, "profile_scope": profile}
    if profile == "examples":
        result["examples"] = _examples(config)
    if profile in ("base", "sdist"):
        from structural_lib.release_uat import run

        result["installed_uat"] = run()
        if result["installed_uat"]["status"] != "PASS":
            raise AssertionError("Installed release UAT failed")
        result["families"] = _families(repo, config["budgets"])
        for args in (("install-preflight",), ("capabilities", "--json"), ("--help",)):
            subprocess.run(
                [sys.executable, "-I", "-m", "structural_lib", *args],
                check=True,
                capture_output=True,
                text=True,
            )
    if profile in ("base", "baseline"):
        result["performance"] = _performance(config)
    if profile in ("dxf", "render", "exports"):
        result["physical_outputs"] = _physical(
            config, render=profile in ("render", "exports"), pdf=profile == "exports"
        )
    if profile == "pdf":
        # PDF's own dependency closure need not include the separate dxf extra.
        from weasyprint import HTML

        example = runpy.run_path(
            str(repo / "Python/examples/complete_member_workflow.py")
        )
        outputs = []
        for name, multi in (("single-layer", False), ("multilayer", True)):
            target = Path(config["output"]) / name
            workflow = example["run_workflow"](multilayer=multi)
            example["write_artifacts"](workflow, target)
            HTML(filename=str(target / "report.html")).write_pdf(target / "report.pdf")
            outputs.append(
                {
                    "case": name,
                    "package_id": workflow.package["calculation_package_id"],
                    "pdf": str(target / "report.pdf"),
                    "sha256": hashlib.sha256(
                        (target / "report.pdf").read_bytes()
                    ).hexdigest(),
                }
            )
        result["reports"] = outputs
    if profile in ("report", "exports"):
        from structural_lib.reports import (
            get_available_templates,
            generate_html_report_from_dict,
        )
        from structural_lib.reports import generator

        if not generator.JINJA2_AVAILABLE or not {
            "beam_design",
            "summary",
            "detailed",
        } <= set(get_available_templates()):
            raise AssertionError("Installed Jinja template resources unavailable")
        document = generate_html_report_from_dict(
            {
                "beam_id": "S5-R",
                "project_name": "S5",
                "inputs": {"b_mm": 300},
                "results": {},
                "is_ok": True,
            },
            template="beam_design",
        )
        if "S5-R" not in document:
            raise AssertionError("Installed template did not render beam identity")
        target = Path(config["output"]) / "template-report.html"
        target.write_text(document)
        result["installed_template"] = str(target)
    if profile in ("validation", "exports"):
        from jsonschema import Draft202012Validator, ValidationError
        from structural_lib.services.tool_manifest import (
            get_tool_manifest_document,
            validate_tool_input,
        )

        safe = dict(
            width=300.0,
            depth=500.0,
            clear_cover=25.0,
            stirrup_dia_mm=8.0,
            main_bar_dia_mm=20.0,
            moment=150.0,
            shear=75.0,
            fck=25.0,
            fy=500.0,
        )
        validator = Draft202012Validator(
            get_tool_manifest_document()["tools"][0]["input_schema"]
        )
        validator.validate(safe)
        if validate_tool_input("is456.beam.design", safe) != safe:
            raise AssertionError("Tool manifest changed validated inputs")
        try:
            validator.validate({**safe, "invented": 1})
        except ValidationError:
            result["invalid_schema_rejected"] = True
        else:
            raise AssertionError("Tool schema accepted an unknown field")
    if profile == "pmm":
        from structural_lib.codes.is456.column.pmm import (
            create_symmetric_two_face_layout,
            experimental_pmm_interaction_surface,
        )
        from structural_lib.core.materials import Steel

        layout = create_symmetric_two_face_layout(
            b_mm=300.0,
            D_mm=500.0,
            Asc_mm2=3000.0,
            d_prime_mm=75.0,
            material=Steel(fy=415.0, steel_type="Fe415"),
        )
        surface = experimental_pmm_interaction_surface(
            b_mm=300.0,
            D_mm=500.0,
            fck_nmm2=25.0,
            reinforcement=layout,
            n_angles=4,
            n_fibers_x=12,
            n_fibers_y=16,
            n_depths=32,
        )
        if not surface.experimental or not math.isfinite(
            surface.nominal_axial_point.Pu_kN
        ):
            raise AssertionError("Experimental PMM dependency/runtime failed")
        result["pmm"] = {
            "experimental": True,
            "nominal_axial_kn": surface.nominal_axial_point.Pu_kN,
            "warnings": surface.warnings,
        }
    if profile == "cad":
        import pyvista

        result["cad"] = {
            "dependency_version": pyvista.__version__,
            "library_export": "UNAVAILABLE",
            "native_acceptance": "HOLD",
        }
    if profile == "etabs":
        expected = platform.system() == "Windows"
        available = importlib.util.find_spec("comtypes") is not None
        if expected != available:
            raise AssertionError("ETABS platform dependency marker drift")
        result["etabs"] = {
            "platform_marker_satisfied": True,
            "native_acceptance": "HOLD",
        }
    if profile == "dev":
        for module in ("pytest", "hypothesis", "numpy", "black", "mypy", "ruff"):
            importlib.import_module(module)
        result["development_dependencies"] = "AVAILABLE"
    if profile == "docs":
        import mkdocs

        completed = subprocess.run(
            [
                sys.executable,
                "-I",
                "-m",
                "mkdocs",
                "build",
                "--strict",
                "-f",
                str(repo / "mkdocs.yml"),
                "--site-dir",
                str(Path(config["output"]) / "site"),
            ],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if completed.returncode:
            raise AssertionError(
                f"Declared docs extra cannot build frozen docs:\n{completed.stderr[-5000:]}"
            )
        result["documentation"] = {
            "mkdocs_version": mkdocs.__version__,
            "strict_build": "PASS",
            "scope": "frozen source documentation; installed docs dependencies",
        }
    if profile == "transport":
        from scripts.verify_canonical_transport_artifact import verify as canonical
        from scripts.verify_lib_pro_012_s0_artifact import verify as s0
        from scripts.verify_lib_pro_013_f0_family_artifact import verify as f0

        result["canonical_transport"] = canonical(Path(config["wheel"]))
        result["s0"] = s0(Path(config["wheel"]))
        result["f0"] = f0(Path(config["wheel"]))
    result["identity_after"] = assert_installed(config)
    return result


def _example_child(config: dict[str, Any]) -> dict[str, Any]:
    before = assert_installed(config)
    script = Path(config["example_script"])
    sys.path.insert(0, str(script.parent))
    sys.argv = [str(script), *config["example_args"]]
    try:
        runpy.run_path(str(script), run_name="__main__")
    except SystemExit as exc:
        if exc.code not in (None, 0):
            raise
    return {"identity_before": before, "identity_after": assert_installed(config)}


def _examples(config: dict[str, Any]) -> dict[str, Any]:
    """Replay copied public drivers/fixtures with no checkout package available."""
    repo, output = Path(config["repo"]), Path(config["output"])
    clone = Path.cwd() / "example-drivers"
    inventory_path = (
        repo / "docs/verification/library-professional-standards-20261008.json"
    )
    inventory = json.loads(inventory_path.read_text())["standalone_examples"][
        "examples"
    ]
    if len(inventory) != 17:
        raise AssertionError("Standalone example population changed")
    sources = [repo / row["path"] for row in inventory]
    sources += list((repo / "Python/examples").glob("*.csv"))
    sources += list((repo / "Python/examples").glob("*.json"))
    sources += [
        repo / "Python/tests/test_public_examples.py",
        repo / "scripts/external_cli_test.py",
        repo / "contracts/structural-engineering/conformance/wp10-vectors.json",
        repo / "contracts/structural-engineering/conformance/beam-readiness-v1.gz",
        *(
            repo / "docs/getting-started" / name
            for name in (
                "python-quickstart.md",
                "beginners-guide.md",
                "colab-workflow.md",
            )
        ),
    ]
    hashes = {}
    for source in sources:
        relative = source.relative_to(repo)
        target = clone / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        hashes[str(relative)] = hashlib.sha256(source.read_bytes()).hexdigest()
    if (clone / "Python/structural_lib").exists():
        raise AssertionError("Example driver tree contains a package checkout")
    records = []
    for row in inventory:
        script = clone / row["path"]
        target = output / script.stem
        target.mkdir(exist_ok=True)
        args = []
        if script.name == "complete_member_workflow.py":
            args = ["--output-dir", str(target / "outputs"), "--dxf"]
        elif script.name == "full_pipeline_synthetic.py":
            args = ["--count", "5", "--output-dir", str(target / "outputs")]
        elif script.name == "member_readiness_workflow.py":
            args = [
                str(
                    clone
                    / "contracts/structural-engineering/conformance/beam-readiness-v1.gz"
                )
            ]
        child = {**config, "example_script": str(script), "example_args": args}
        config_path = clone / "child.json"
        config_path.write_text(json.dumps(child))
        completed = subprocess.run(
            [sys.executable, "-I", str(Path(__file__)), str(config_path)],
            cwd=target,
            capture_output=True,
            text=True,
            timeout=180,
        )
        (target / "stdout.log").write_text(completed.stdout)
        (target / "stderr.log").write_text(completed.stderr)
        if completed.returncode:
            raise AssertionError(
                f"Installed example failed: {script.name}\n{completed.stderr[-3000:]}\n{completed.stdout[-3000:]}"
            )
        if script.name == "complete_beam_design.py":
            with (script.parent / "sample_building_beams.csv").open() as stream:
                expected = {row["BeamID"] for row in csv.DictReader(stream)}
            schedule = script.parent / "beam_schedule_output.csv"
            with schedule.open() as stream:
                rows = list(csv.DictReader(stream))
            if len(rows) != len(expected) or "✗" in completed.stdout:
                raise AssertionError(
                    f"Complete beam example concealed a failed workflow:\n{completed.stdout[-6000:]}"
                )
            for beam in ("B1", "B2", "B3"):
                if not (script.parent / "dxf_output" / f"{beam}.dxf").is_file():
                    raise AssertionError(f"Complete beam example omitted {beam}.dxf")
            shutil.copytree(
                script.parent / "dxf_output", target / "dxf_output", dirs_exist_ok=True
            )
            shutil.copyfile(schedule, target / schedule.name)
        proof = json.loads(
            next(
                line.removeprefix("S5_RESULT=")
                for line in reversed(completed.stdout.splitlines())
                if line.startswith("S5_RESULT=")
            )
        )
        records.append({"path": row["path"], "args": args, "status": "PASS", **proof})
    # The copied module has no conftest, pytest config, or package source tree.
    # Run in this guarded interpreter so imports are checked after collection too.
    import pytest

    config_file = clone / "pytest.ini"
    config_file.write_text("[pytest]\n")
    junit = output / "public-examples.xml"
    code = pytest.main(
        [
            "-q",
            "-c",
            str(config_file),
            "--confcutdir",
            str(clone),
            "--junitxml",
            str(junit),
            str(clone / "Python/tests/test_public_examples.py"),
        ]
    )
    if code != 0:
        raise AssertionError(f"Installed public example/guide checks failed: {code}")
    return {
        "standalone": records,
        "driver_inputs_sha256": hashes,
        "public_example_tests_junit": str(junit),
        "limits": ["Colab Files UI and native application replay are not exercised"],
    }


if __name__ == "__main__":
    configuration = json.loads(Path(sys.argv[1]).read_text())
    print(
        "S5_RESULT="
        + json.dumps(
            (
                _example_child(configuration)
                if "example_script" in configuration
                else run_probe(configuration)
            ),
            allow_nan=False,
        )
    )
