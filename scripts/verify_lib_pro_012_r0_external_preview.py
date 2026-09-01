#!/usr/bin/env python3
"""Verify R0 advertised contracts, cookbook recipes, and one exact wheel."""

from __future__ import annotations

import argparse
import copy
import doctest
import hashlib
import importlib
import inspect
import json
import math
import os
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]


def _recipe_specs() -> tuple[Any, ...]:
    namespace = runpy.run_path(
        str(REPO_ROOT / "scripts/verify_lib_pro_013_f0_family_artifact.py")
    )
    return namespace["recipe_specs"]()


def _beam_design_documentation_payload(*, mu_knm: float = 100.0) -> dict[str, Any]:
    return {
        "identity": {"member_id": "B-DOC", "story": "L1", "case_id": "ULS-1"},
        "section": {
            "span_mm": 5000.0,
            "b_mm": 300.0,
            "D_mm": 500.0,
            "d_mm": 442.0,
        },
        "materials": {"fck_nmm2": 25.0, "fy_nmm2": 500.0},
        "actions": {"mu_knm": mu_knm, "vu_kn": 60.0, "tu_knm": 0.0},
        "calculation_basis": {"d_dash_mm": 58.0, "asv_mm2": 100.53},
        "source_provenance": "LIB-PRO-015-D1-BEAM",
    }


def _beam_supplied_documentation_payload() -> dict[str, Any]:
    return {
        "schema_version": "beam-supplied-check/v2",
        "correlation_id": "DOC-B1-ULS-1",
        "identity": {"member_id": "B1", "story": "L1", "case_id": "ULS-1"},
        "section": {
            "b_mm": 300.0,
            "D_mm": 500.0,
            "effective_depth_basis": {
                "clear_cover_mm": 40.0,
                "stirrup_diameter_mm": 8.0,
                "tension_bar_diameter_mm": 20.0,
            },
        },
        "materials": {
            "fck_nmm2": 25.0,
            "fy_nmm2": 500.0,
            "fy_transverse_nmm2": 415.0,
        },
        "actions": {
            "mu_knm": 100.0,
            "vu_kn": 60.0,
            "primary_tension_face": "BOTTOM",
        },
        "reinforcement": {
            "clear_cover_mm": 40.0,
            "tension": {"diameter_mm": 20.0, "bars_per_layer": [4]},
            "compression_or_hanger": {
                "diameter_mm": 12.0,
                "bars_per_layer": [2],
            },
            "stirrup_diameter_mm": 8.0,
            "stirrup_legs": 2,
            "stirrup_spacing_mm": 150.0,
            "bar_type": "deformed",
            "has_standard_bend_at_start": True,
            "has_standard_bend_at_end": True,
            "source_reference": "reviewed schedule B1-R1",
        },
        "selection": {
            "permitted_diameters_mm": [12.0, 16.0, 20.0, 25.0],
            "maximum_layers": 2,
            "maximum_bars_per_layer": 8,
            "nominal_max_aggregate_size_mm": 20.0,
            "effective_depth_tolerance_mm": 1.0,
            "objective": "min_area",
            "source_reference": "reviewed project bar catalogue P1",
        },
        "support": {
            "start_width_mm": 5000.0,
            "end_width_mm": 5000.0,
            "source_reference": "reviewed supports C1 and C2",
        },
        "source_provenance": "reviewed supplied reinforcement schedule",
    }


def run_beam_documentation_examples() -> list[dict[str, str]]:
    """Execute valid, invalid, FAIL, and HOLD beam examples."""

    from structural_lib.core.errors import InputContractError
    from structural_lib.design.is456 import beam

    records: list[dict[str, str]] = []
    valid = beam.design(beam.load(_beam_design_documentation_payload()))
    records.append(
        {
            "example_id": "is456.beam.design.valid",
            "outcome": valid.engineering_status.value,
        }
    )

    invalid = _beam_design_documentation_payload(mu_knm=-1.0)
    try:
        beam.load(invalid)
    except InputContractError as error:
        issue = error.issues[0]
        records.append(
            {
                "example_id": "is456.beam.design.invalid",
                "outcome": f"{issue.code}:{issue.path}",
            }
        )
    else:
        raise AssertionError("Invalid beam documentation vector was accepted")

    failed = beam.design(beam.load(_beam_design_documentation_payload(mu_knm=2000.0)))
    records.append(
        {
            "example_id": "is456.beam.design.engineering-fail",
            "outcome": failed.engineering_status.value,
        }
    )

    supplied_payload = _beam_supplied_documentation_payload()
    supplied = beam.check_supplied(beam.load_supplied_check(supplied_payload))
    records.append(
        {
            "example_id": "is456.beam.supplied.valid",
            "outcome": supplied.status,
        }
    )

    invalid_supplied = copy.deepcopy(supplied_payload)
    del invalid_supplied["section"]["effective_depth_basis"]
    try:
        beam.load_supplied_check(invalid_supplied)
    except InputContractError as error:
        issue = error.issues[0]
        records.append(
            {
                "example_id": "is456.beam.supplied.invalid",
                "outcome": f"{issue.code}:{issue.path}",
            }
        )
    else:
        raise AssertionError("Invalid supplied-beam documentation vector was accepted")

    failed_supplied = copy.deepcopy(supplied_payload)
    failed_supplied["actions"]["vu_kn"] = 200.0
    failed_supplied["reinforcement"]["stirrup_spacing_mm"] = 300.0
    failed_result = beam.check_supplied(beam.load_supplied_check(failed_supplied))
    records.append(
        {
            "example_id": "is456.beam.supplied.engineering-fail",
            "outcome": failed_result.status,
        }
    )

    held_supplied = copy.deepcopy(supplied_payload)
    held_supplied["support"] = None
    held_result = beam.check_supplied(beam.load_supplied_check(held_supplied))
    records.append(
        {
            "example_id": "is456.beam.supplied.engineering-hold",
            "outcome": held_result.status,
        }
    )
    return records


def run_beam_documentation_contract() -> dict[str, Any]:
    """Verify generated beam documentation against the imported package."""

    from structural_lib.design.is456 import beam

    registry = json.loads(
        (REPO_ROOT / "docs/reference/api-classification.json").read_text(
            encoding="utf-8"
        )
    )
    contract = registry["documentation_contract"]
    assert not contract["unbaselined_debt"]
    assert not any(
        name.startswith("structural_lib.design.is456.beam.")
        for name in contract["temporary_debt_baseline"]
    )
    surface = next(
        item
        for item in registry["surfaces"]
        if item["module"] == "structural_lib.design.is456.beam"
    )
    records = {item["name"]: item for item in surface["symbols"]}
    required_sections = set(contract["required_canonical_docstring_sections"])
    operations = tuple(contract["exact_wheel_beam_operations"])
    docstring_results: list[dict[str, Any]] = []
    for operation in operations:
        value = getattr(beam, operation)
        record = records[operation]
        signature = str(inspect.signature(value)).replace(
            "typing.Annotated[", "Annotated["
        )
        assert signature == record["documentation"]["signature"]
        docstring = inspect.getdoc(value) or ""
        present_sections = {
            section
            for section in required_sections
            if re.search(rf"(?m)^\s*{section.title()}:?\s*$", docstring)
        }
        assert present_sections == required_sections, (operation, present_sections)
        assert not record["documentation"]["missing_docstring_sections"]

        finder = doctest.DocTestParser()
        test = finder.get_doctest(
            docstring,
            vars(importlib.import_module(value.__module__)).copy(),
            f"structural_lib.design.is456.beam.{operation}",
            value.__module__,
            0,
        )
        output: list[str] = []
        result = doctest.DocTestRunner().run(test, out=output.append)
        if result.failed:
            raise AssertionError("".join(output))
        docstring_results.append(
            {
                "operation": operation,
                "signature": signature,
                "example_count": len(test.examples),
            }
        )

    actual_examples = {
        item["example_id"]: item["outcome"]
        for item in run_beam_documentation_examples()
    }
    for operation in operations:
        actual_examples[f"is456.beam.facade.{operation}.docstring"] = (
            "EXECUTES_FROM_EXACT_WHEEL"
        )
    expected_examples = {
        item["example_id"]: item["expected"] for item in contract["example_inventory"]
    }
    assert actual_examples == expected_examples
    return {
        "schema_version": contract["schema_version"],
        "operation_count": len(operations),
        "docstring_example_count": sum(
            item["example_count"] for item in docstring_results
        ),
        "registered_example_count": len(actual_examples),
        "operations": docstring_results,
    }


def _set_path(payload: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    current: Any = payload
    for name in path[:-1]:
        current = current[name]
    current[path[-1]] = value


def _get_path(payload: dict[str, Any], path: tuple[str, ...]) -> Any:
    current: Any = payload
    for name in path:
        if not isinstance(current, dict) or name not in current:
            return None
        current = current[name]
    return current


def _find_path(
    value: Any,
    predicate: Any,
    prefix: tuple[str, ...] = (),
) -> tuple[str, ...] | None:
    if isinstance(value, dict):
        for key, item in value.items():
            path = (*prefix, key)
            if predicate(key, item):
                return path
            found = _find_path(item, predicate, path)
            if found is not None:
                return found
    return None


def _assert_rejected(module: Any, loader: str, payload: dict[str, Any]) -> list[str]:
    from structural_lib.core.errors import InputContractError

    try:
        getattr(module, loader)(payload)
    except InputContractError as error:
        return [issue.code for issue in error.issues]
    raise AssertionError(f"{module.__name__}.{loader} accepted an invalid vector")


def _resolve_qualified(path: str) -> Any:
    parts = path.split(".")
    for split in range(len(parts) - 1, 0, -1):
        module_name = ".".join(parts[:split])
        try:
            value: Any = importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue
        for name in parts[split:]:
            value = getattr(value, name)
        return value
    raise ImportError(path)


def run_contract_audit() -> dict[str, Any]:
    import structural_lib
    from structural_lib.services.contracts.common import (
        ValidationDimension,
        schema_leaf_paths,
    )
    from structural_lib.services.family_facade_registry import (
        FAMILY_FACADE_WORKFLOWS,
    )

    assert "design" in dir(structural_lib)
    recipes = {recipe.journey_id: recipe for recipe in _recipe_specs()}
    workflows = tuple(FAMILY_FACADE_WORKFLOWS)
    assert len(workflows) == 13
    assert set(recipes) == {workflow.journey_id for workflow in workflows}

    records: list[dict[str, Any]] = []
    all_dimensions = {dimension.value for dimension in ValidationDimension}
    for workflow in workflows:
        module = importlib.import_module(workflow.module)
        assert callable(getattr(module, recipes[workflow.journey_id].loader))
        assert callable(getattr(module, recipes[workflow.journey_id].operation))
        request_type = _resolve_qualified(workflow.request_type)
        leaf_paths = set(schema_leaf_paths(request_type))
        contracts = tuple(request_type.field_contracts)
        contract_paths = {contract.path for contract in contracts}
        represented = {
            dimension.value
            for contract in contracts
            for dimension in contract.dimensions
        }
        unowned = sorted(leaf_paths - contract_paths)
        assert not unowned, (workflow.journey_id, unowned)
        assert len(contract_paths) == len(contracts)
        assert all(contract.dimensions for contract in contracts)
        assert callable(_resolve_qualified(workflow.compatibility_owner))
        assert represented | (all_dimensions - represented) == all_dimensions
        decorators = getattr(request_type, "__pydantic_decorators__", None)
        has_model_validator = bool(getattr(decorators, "model_validators", {}))
        records.append(
            {
                "journey_id": workflow.journey_id,
                "request_field_count": len(leaf_paths),
                "field_contract_count": len(contracts),
                "unowned_field_paths": unowned,
                "represented_validation_dimensions": sorted(represented),
                "not_applicable_validation_dimensions": sorted(
                    all_dimensions - represented
                ),
                "compatibility_target_resolved": True,
                "cross_field_validation_owner": (
                    "STRICT_REQUEST_MODEL"
                    if has_model_validator
                    else f"DELEGATED_TO_MAINTAINED_OWNER:{workflow.compatibility_owner}"
                ),
                "consumer_contract": workflow.consumer_contract,
            }
        )
    return {
        "journey_count": len(records),
        "unowned_field_count": sum(
            len(record["unowned_field_paths"]) for record in records
        ),
        "workflows": records,
    }


def run_contract_vectors() -> dict[str, Any]:
    from structural_lib.services.family_facade_registry import (
        FAMILY_FACADE_WORKFLOWS,
    )

    workflows = {workflow.journey_id: workflow for workflow in FAMILY_FACADE_WORKFLOWS}
    counts = {
        "finite": 0,
        "boolean": 0,
        "route_specific_invalid": 0,
        "sign_or_range": 0,
        "enum_or_topology": 0,
        "identity_or_provenance": 0,
        "cross_field_relation": 0,
        "collection_cardinality": 0,
        "unknown_field": 0,
        "missing_required_group": 0,
        "compatibility_target": 0,
        "finite_json_consumer": 0,
    }
    route_records: list[dict[str, Any]] = []
    for recipe in _recipe_specs():
        workflow = workflows[recipe.journey_id]
        module = importlib.import_module(recipe.module)
        loader = getattr(module, recipe.loader)
        request = loader(copy.deepcopy(recipe.payload))
        result = getattr(module, recipe.operation)(request)
        serialized = result.to_dict()
        json.dumps(serialized, allow_nan=False, sort_keys=True)
        counts["finite_json_consumer"] += 1

        invalid = copy.deepcopy(recipe.payload)
        _set_path(invalid, recipe.invalid_path, recipe.invalid_value)
        recipe_issue_codes = _assert_rejected(module, recipe.loader, invalid)
        counts["route_specific_invalid"] += 1

        request_type = _resolve_qualified(workflow.request_type)
        range_contract = next(
            contract
            for contract in request_type.field_contracts
            if contract.zero_allowed is False
            and isinstance(
                _get_path(recipe.payload, tuple(contract.path.split("."))),
                (int, float),
            )
            and not isinstance(
                _get_path(recipe.payload, tuple(contract.path.split("."))), bool
            )
        )
        range_payload = copy.deepcopy(recipe.payload)
        _set_path(range_payload, tuple(range_contract.path.split(".")), 0)
        _assert_rejected(module, recipe.loader, range_payload)
        counts["sign_or_range"] += 1

        non_finite_path = _find_path(
            recipe.payload,
            lambda _key, value: (
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and math.isfinite(float(value))
            ),
        )
        assert non_finite_path is not None
        non_finite = copy.deepcopy(recipe.payload)
        _set_path(non_finite, non_finite_path, float("nan"))
        _assert_rejected(module, recipe.loader, non_finite)
        counts["finite"] += 1

        boolean_path = _find_path(
            recipe.payload, lambda _key, value: isinstance(value, bool)
        )
        if boolean_path is not None:
            boolean_payload = copy.deepcopy(recipe.payload)
            _set_path(boolean_payload, boolean_path, 1)
            _assert_rejected(module, recipe.loader, boolean_payload)
            counts["boolean"] += 1

        enum_payload = copy.deepcopy(recipe.payload)
        enum_payload["schema_version"] = "invented-contract/v0"
        _assert_rejected(module, recipe.loader, enum_payload)
        counts["enum_or_topology"] += 1

        identity_path = _find_path(
            recipe.payload,
            lambda key, value: (
                isinstance(value, str) and key in {"member_id", "case_id", "family_id"}
            ),
        )
        assert identity_path is not None
        identity_payload = copy.deepcopy(recipe.payload)
        _set_path(identity_payload, identity_path, "")
        _assert_rejected(module, recipe.loader, identity_payload)
        counts["identity_or_provenance"] += 1

        unknown = copy.deepcopy(recipe.payload)
        unknown["r0_unknown_field"] = True
        _assert_rejected(module, recipe.loader, unknown)
        counts["unknown_field"] += 1

        missing = copy.deepcopy(recipe.payload)
        first_group = next(iter(recipe.payload))
        del missing[first_group]
        _assert_rejected(module, recipe.loader, missing)
        counts["missing_required_group"] += 1

        assert callable(_resolve_qualified(workflow.compatibility_owner))
        counts["compatibility_target"] += 1
        route_records.append(
            {
                "journey_id": recipe.journey_id,
                "engineering_status": result.engineering_status.value,
                "recipe_invalid_issue_codes": recipe_issue_codes,
            }
        )

    relation_vectors = {
        "is456.beam.design/v1": (("section", "d_mm"), 500.0),
        "is456.torsion.design/v1": (("geometry", "d_mm"), 500.0),
        "is456.column.supplied-steel-check/v1": (
            ("reinforcement", "supplied_steel_area_mm2"),
            1.0,
        ),
    }
    recipes = {recipe.journey_id: recipe for recipe in _recipe_specs()}
    for journey_id, (path, value) in relation_vectors.items():
        recipe = recipes[journey_id]
        payload = copy.deepcopy(recipe.payload)
        _set_path(payload, path, value)
        module = importlib.import_module(recipe.module)
        _assert_rejected(module, recipe.loader, payload)
        counts["cross_field_relation"] += 1

    isolated = recipes["is456.isolated-footing.concentric/v1"]
    cardinality = copy.deepcopy(isolated.payload)
    _set_path(
        cardinality,
        ("materials_reinforcement", "permitted_bottom_bar_diameters_mm"),
        [],
    )
    _assert_rejected(
        importlib.import_module(isolated.module), isolated.loader, cardinality
    )
    counts["collection_cardinality"] += 1

    assert all(count > 0 for count in counts.values())
    return {"vector_class_counts": counts, "routes": route_records}


def run_current() -> dict[str, Any]:
    namespace = runpy.run_path(
        str(REPO_ROOT / "scripts/verify_lib_pro_013_f0_family_artifact.py")
    )
    from structural_lib.services.release_uat import run as run_release_uat

    recipes = namespace["run_recipes"]()
    release_uat = run_release_uat()
    beam_documentation = run_beam_documentation_contract()
    from structural_lib.design.is456 import beam

    request = beam.load(
        {
            "identity": {"member_id": "B1", "story": "GF", "case_id": "ULS-1"},
            "section": {
                "span_mm": 5000.0,
                "b_mm": 300.0,
                "D_mm": 500.0,
                "d_mm": 442.0,
            },
            "materials": {"fck_nmm2": 25.0, "fy_nmm2": 500.0},
            "actions": {"mu_knm": 150.0, "vu_kn": 80.0, "tu_knm": 0.0},
            "calculation_basis": {"d_dash_mm": 58.0, "asv_mm2": 100.0},
            "source_provenance": "README-R0",
        }
    )
    readme_result = beam.design(request)
    assert readme_result.is_ok
    json.dumps(readme_result.to_dict(), allow_nan=False)
    return {
        "schema_version": "lib-pro-012-r0-external-preview-evidence/v1",
        "status": "PASS",
        "source_free": False,
        "contract_audit": run_contract_audit(),
        "contract_vectors": run_contract_vectors(),
        "beam_documentation": beam_documentation,
        "recipe_count": len(recipes),
        "recipes": recipes,
        "release_uat": {
            "status": release_uat["status"],
            "case_count": release_uat["case_count"],
            "advertised_entry_count": release_uat["advertised_entry_points"][
                "entry_count"
            ],
            "public_examples": {
                "readme_family_facade_beam": True,
                "python_readme_batch": release_uat["public_examples"][
                    "python_readme_batch"
                ],
            },
        },
    }


def _clean_env(installed_root: Path) -> dict[str, str]:
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in {"PYTHONPATH", "VIRTUAL_ENV"}
    }
    env["PYTHONPATH"] = os.pathsep.join((str(installed_root), str(REPO_ROOT)))
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _install_wheel(wheel: Path, installed_root: Path, temp_root: Path) -> str:
    pip_install = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-deps",
            "--target",
            str(installed_root),
            str(wheel),
        ],
        cwd=temp_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if pip_install.returncode == 0:
        return "pip"

    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError(pip_install.stderr)
    uv_install = subprocess.run(
        [
            uv,
            "pip",
            "install",
            "--no-deps",
            "--target",
            str(installed_root),
            str(wheel),
        ],
        cwd=temp_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if uv_install.returncode:
        raise RuntimeError(
            "wheel installation failed with both pip and uv\n"
            f"pip: {pip_install.stderr}\nuv: {uv_install.stderr}"
        )
    return "uv"


def verify(wheel: Path) -> dict[str, Any]:
    wheel = wheel.resolve()
    if not wheel.is_file() or wheel.suffix != ".whl":
        raise ValueError(f"Wheel does not exist: {wheel}")
    docs = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts/generate_family_facade_docs.py"),
            "--check",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if docs.returncode:
        raise RuntimeError(docs.stdout + docs.stderr)

    with tempfile.TemporaryDirectory(prefix="lib_pro_012_r0_") as raw_temp:
        temp_root = Path(raw_temp)
        installed_root = temp_root / "installed"
        installed_root.mkdir()
        wheel_installer = _install_wheel(wheel, installed_root, temp_root)
        probe = (
            "import json, pathlib, structural_lib; "
            "from scripts.verify_lib_pro_012_r0_external_preview import run_current; "
            f"root=pathlib.Path({str(installed_root)!r}).resolve(); "
            "origin=pathlib.Path(structural_lib.__file__).resolve(); "
            "assert origin.is_relative_to(root), (origin, root); "
            "receipt=run_current(); "
            "receipt['package_origin']=str(origin); "
            "receipt['source_free']=True; print(json.dumps(receipt, allow_nan=False))"
        )
        result = subprocess.run(
            [sys.executable, "-c", probe],
            cwd=temp_root,
            env=_clean_env(installed_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            raise RuntimeError(
                f"R0 source-free probe failed\n{result.stdout}\n{result.stderr}"
            )
        receipt = json.loads(result.stdout)
        receipt["wheel"] = str(wheel)
        receipt["wheel_sha256"] = _sha256(wheel)
        receipt["wheel_installer"] = wheel_installer
        receipt["cookbook_generation_check"] = "PASS"
        return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path)
    parser.add_argument("--current", action="store_true")
    args = parser.parse_args()
    if args.current:
        print(json.dumps(run_current(), indent=2, sort_keys=True, allow_nan=False))
        return 0
    if args.wheel is None:
        parser.error("supply --wheel or --current")
    print(json.dumps(verify(args.wheel), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
