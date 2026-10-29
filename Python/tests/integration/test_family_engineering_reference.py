"""Source-equation references across the declared public family journeys.

Expected values come from the adjacent independent, production-free generator.
The frozen fixture is consumed without SciPy; public outputs never regenerate it.
"""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
import math
import sys
from copy import deepcopy
from pathlib import Path

import pytest

pytestmark = pytest.mark.repo_only

ROOT = Path(__file__).resolve().parents[3]
DATA = Path(__file__).resolve().parents[1] / "data/benchmark_vectors"
INPUTS = json.loads((DATA / "family_review_inputs.json").read_text())["cases"]
REFERENCES = json.loads((DATA / "family_review_reference.json").read_text())["cases"]
SPEC = importlib.util.spec_from_file_location(
    "s4_family_recipes", ROOT / "scripts/verify_lib_pro_013_f0_family_artifact.py"
)
assert SPEC and SPEC.loader
RECIPES = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = RECIPES
SPEC.loader.exec_module(RECIPES)


def test_reference_population_and_frozen_inputs_match_public_recipes():
    recipes = RECIPES.recipe_specs()
    assert len(recipes) == len(INPUTS) == len(REFERENCES) == 13
    assert [r.journey_id for r in recipes] == [r["journey_id"] for r in REFERENCES]
    for recipe, frozen, reference in zip(recipes, INPUTS, REFERENCES, strict=True):
        assert recipe.payload == frozen["request"]
        encoded = json.dumps(recipe.payload, sort_keys=True, separators=(",", ":"))
        assert (
            hashlib.sha256(encoded.encode()).hexdigest() == reference["request_sha256"]
        )
        assert reference["source_clauses"] and reference["independent_method"]


@pytest.mark.parametrize("index", range(13), ids=[r["journey_id"] for r in REFERENCES])
def test_public_design_agrees_with_independent_source_equations(index):
    recipe = RECIPES.recipe_specs()[index]
    reference = REFERENCES[index]
    module = importlib.import_module(recipe.module)
    result = getattr(module, recipe.operation)(
        getattr(module, recipe.loader)(recipe.payload)
    )
    actual = result.to_dict()
    assert (
        actual["envelope"]["engineering_status"]
        == reference["expected_engineering_status"]
    )
    assert actual["envelope"]["qualified_review_required"] is True
    for metric in reference["metrics"]:
        value = actual
        for key in metric["path"].split("."):
            value = value[int(key)] if isinstance(value, list) else value[key]
        assert metric["unit"]
        assert math.isfinite(value)
        assert value == pytest.approx(
            metric["expected"],
            abs=metric["absolute_tolerance"],
            rel=metric["relative_tolerance"],
        ), f"{recipe.journey_id} {metric['path']} [{metric['unit']}]"
    json.dumps(actual, allow_nan=False)


def test_fe500_strap_cannot_pass_between_415_and_500_stirrup_capacities():
    """Cl40.4 false-PASS reproducer: all other bounded checks remain passing."""
    from structural_lib.design.is456 import strap_footing

    recipe = RECIPES.recipe_specs()[-1]
    payload = deepcopy(recipe.payload)
    payload["geometry_topology"].update(
        strap_effective_depth_mm=700, strap_overall_depth_mm=800
    )
    payload["actions"].update(
        service_exterior_column_load_kn=400,
        service_interior_column_load_kn=725.8413461538462,
        service_clear_strap_line_load_kn_per_m=100,
        factored_exterior_column_load_kn=600,
        factored_interior_column_load_kn=1088.7620192307693,
        factored_clear_strap_line_load_kn_per_m=150,
        allowable_gross_bearing_pressure_kn_per_m2=1000,
    )
    actual = strap_footing.design(strap_footing.load(payload)).to_dict()
    strength = actual["calculation"]["strength"]
    shear = strength["shear"]
    # Source cap: two vertical T10 legs, d700, s250, fy_design415.
    expected_capacity = 0.87 * 415 * (2 * math.pi * 10**2 / 4) * 700 / 250 / 1000
    assert shear["stirrup_shear_capacity_provided_kn"] == pytest.approx(
        expected_capacity
    )
    assert (
        expected_capacity
        < shear["stirrup_carried_shear_required_kn"]
        < expected_capacity * 500 / 415
    )
    assert shear["minimum_stirrup_area_is_safe"]
    assert shear["maximum_stress_is_safe"] and shear["stirrup_spacing_is_safe"]
    assert strength["flexure"]["is_safe"] and strength["side_face"]["is_safe"]
    assert shear["stirrup_strength_is_safe"] is False
    assert actual["envelope"]["engineering_status"] == "FAIL"
