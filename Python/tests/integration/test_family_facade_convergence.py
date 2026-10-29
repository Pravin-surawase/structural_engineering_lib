"""F0 contract, recipe, result, and discovery convergence evidence."""

from __future__ import annotations

import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from structural_lib.core.errors import InputContractError
from structural_lib.services.capabilities import get_supported_is456_capabilities
from structural_lib.services.family_facade_registry import FAMILY_FACADE_WORKFLOWS

pytestmark = pytest.mark.repo_only

_SCRIPT = (
    Path(__file__).resolve().parents[3]
    / "scripts"
    / "verify_lib_pro_013_f0_family_artifact.py"
)
_SPEC = importlib.util.spec_from_file_location("f0_family_artifact", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
recipes = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = recipes
_SPEC.loader.exec_module(recipes)


@pytest.mark.parametrize("recipe", recipes.recipe_specs(), ids=lambda r: r.journey_id)
def test_json_loaders_preserve_typed_requests_and_field_errors(recipe):
    module = __import__(recipe.module, fromlist=[recipe.loader])
    expected = getattr(module, recipe.loader)(recipe.payload)
    load_json = getattr(module, recipe.loader + "_json")
    text = expected.model_dump_json()
    assert load_json(text) == expected
    assert load_json(b"\xef\xbb\xbf" + text.encode("utf-8")) == expected

    invalid = json.loads(text)
    recipes._set_path(invalid, recipe.invalid_path, recipe.invalid_value)
    with pytest.raises(InputContractError) as error:
        load_json(json.dumps(invalid))
    assert error.value.issues


@pytest.mark.parametrize(
    "recipe",
    [r for r in recipes.recipe_specs() if r.module.rsplit(".", 1)[-1] != "beam"],
    ids=lambda recipe: recipe.journey_id,
)
def test_public_typed_builders_preserve_requests_results_and_error_paths(recipe):
    module = __import__(recipe.module, fromlist=[recipe.loader])
    loaded = getattr(module, recipe.loader)(recipe.payload)
    builder_name = "input" + recipe.loader.removeprefix("load")
    builder = getattr(module, builder_name)
    # Each model type is available at the documented facade import path.
    groups = {
        name: getattr(loaded, name)
        for name in type(loaded).model_fields
        if name != "schema_version"
    }
    for value in groups.values():
        assert getattr(module, type(value).__name__) is type(value)
    rebuilt = builder(**groups)
    mapped = builder(**recipe.payload)
    assert rebuilt == mapped == loaded
    result = getattr(module, recipe.operation)(rebuilt)
    assert result.to_dict() == getattr(module, recipe.operation)(loaded).to_dict()
    with pytest.raises(InputContractError) as error:
        builder(**{**recipe.payload, next(iter(groups)): {}})
    assert any(
        issue.path.startswith(next(iter(groups))) for issue in error.value.issues
    )


def test_all_thirteen_facade_classes_run_valid_and_invalid_recipes() -> None:
    receipts = recipes.run_recipes()

    assert len(receipts) == 13
    assert {item["journey_id"] for item in receipts} == {
        item.journey_id for item in FAMILY_FACADE_WORKFLOWS
    }
    assert all(item["invalid_issue_codes"] for item in receipts)
    assert {item["engineering_status"] for item in receipts} == {
        "PASS",
        "FAIL",
        "HOLD",
    }


def test_evidence_heavy_schemas_expose_exactly_five_required_groups() -> None:
    request_names = {
        "braced-wall-input/v1",
        "straight-flight-staircase-input/v1",
        "simply-supported-deep-beam-input/v1",
        "regular-interior-flat-slab-input/v1",
        "concentric-isolated-footing-input/v1",
        "symmetric-combined-footing-input/v1",
        "property-line-strap-footing-input/v1",
    }
    for recipe in recipes.recipe_specs():
        if recipe.payload.get("schema_version") in request_names:
            raise AssertionError("recipes must rely on the frozen contract default")
        module = __import__(recipe.module, fromlist=[recipe.loader])
        request = getattr(module, recipe.loader)(recipe.payload)
        if request.schema_version not in request_names:
            continue
        schema = type(request).model_json_schema(mode="validation")
        required = set(schema["required"])
        assert required == {
            "identity_source",
            "geometry_topology",
            "actions",
            "materials_reinforcement",
            "evidence_review",
        }


def test_schema_and_result_status_are_finite_and_orthogonal() -> None:
    for recipe in recipes.recipe_specs():
        module = __import__(recipe.module, fromlist=[recipe.loader])
        request = getattr(module, recipe.loader)(recipe.payload)
        result = getattr(module, recipe.operation)(request)
        payload = result.to_dict()

        json.dumps(payload, allow_nan=False)
        assert payload["envelope"]["intake_status"] == "VALID"
        assert payload["envelope"]["calculation_status"] == "COMPLETED"
        assert payload["envelope"]["engineering_status"] == (
            recipe.expected_engineering_status
        )
        assert payload["envelope"]["qualified_review_required"] is True


def test_design_functions_reject_unvalidated_request_objects() -> None:
    for recipe in recipes.recipe_specs():
        module = __import__(recipe.module, fromlist=[recipe.operation])
        with pytest.raises(InputContractError, match="request must be"):
            getattr(module, recipe.operation)(object())


def test_capability_truth_remains_thirteen_supported_and_held_families_unchanged() -> (
    None
):
    supported = get_supported_is456_capabilities()
    coverage = json.loads(
        (
            Path(__file__).resolve().parents[3]
            / "docs"
            / "verification"
            / "indian-code-capability-coverage.json"
        ).read_text(encoding="utf-8")
    )
    # The service authority contains ten IS 456 families.  The cross-standard
    # coverage authority adds the three retained IS 13920 families.
    assert len(supported) == 10
    assert coverage["capability_summary"] == {
        "supported_families": 13,
        "held_families": 8,
        "total_declared_families": 21,
        "supported_pct": 61.9,
    }
    assert {item.element for item in supported} >= {
        "beam",
        "column",
        "solid_slab",
        "wall",
        "stair",
        "deep_beam",
        "flat_slab",
        "isolated_footing",
        "combined_footing",
        "strap_footing",
    }


@pytest.mark.parametrize("recipe", recipes.recipe_specs(), ids=lambda r: r.journey_id)
def test_every_family_admission_defaults_schema_and_json_policy(recipe):
    """Exercise shared policy through each real facade, including JSON intake."""
    from jsonschema import Draft202012Validator

    module = __import__(recipe.module, fromlist=[recipe.loader])
    load = getattr(module, recipe.loader)
    load_json = getattr(module, recipe.loader + "_json")
    request = load(recipe.payload)
    schema = type(request).model_json_schema()
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(request.model_dump(mode="json"))
    assert (
        request.schema_version == type(request).model_fields["schema_version"].default
    )
    assert load_json(request.model_dump_json()) == request

    def numeric_leaf(value, model, path=()):
        for name, item in value.items():
            if type(item) in (int, float) and model.model_fields[name].is_required():
                return (*path, name)
            if isinstance(item, dict):
                found = numeric_leaf(item, getattr(model, name), (*path, name))
                if found:
                    return found
        return None

    path = numeric_leaf(recipe.payload, request)
    assert path is not None
    for invalid in (True, None, "123", float("inf"), float("nan")):
        payload = deepcopy(recipe.payload)
        parent = payload
        for part in path[:-1]:
            parent = parent[part]
        parent[path[-1]] = invalid
        with pytest.raises(InputContractError):
            load(payload)
        with pytest.raises(InputContractError):
            load_json(json.dumps(payload))

    with pytest.raises(InputContractError):
        load({**recipe.payload, "ignored_structural_input": 1})
    group = next(k for k, v in recipe.payload.items() if isinstance(v, dict))
    payload = deepcopy(recipe.payload)
    payload[group]["ignored_structural_input"] = 1
    with pytest.raises(InputContractError):
        load(payload)
    payload = deepcopy(recipe.payload)
    del payload[group]
    with pytest.raises(InputContractError):
        load(payload)
    duplicate = (
        '{"schema_version":'
        + json.dumps(request.schema_version)
        + ","
        + request.model_dump_json()[1:]
    )
    with pytest.raises(InputContractError) as error:
        load_json(duplicate)
    assert any(issue.code == "DUPLICATE_JSON_KEY" for issue in error.value.issues)
