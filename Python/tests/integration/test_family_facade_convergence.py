"""F0 contract, recipe, result, and discovery convergence evidence."""

from __future__ import annotations

import importlib.util
import json
import sys
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
