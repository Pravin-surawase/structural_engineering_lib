from typing import cast

import pytest

from structural_lib.rebar_optimizer import Objective, optimize_bar_arrangement


@pytest.mark.parametrize(
    "case",
    [
        {
            "name": "min_area_can_choose_more_bars",
            "inputs": {
                "ast_required_mm2": 1500.0,
                "b_mm": 300.0,
                "cover_mm": 25.0,
                "stirrup_dia_mm": 8.0,
                "allowed_dia_mm": [12.0, 16.0],
                "max_layers": 2,
                "objective": "min_area",
                "agg_size_mm": 20.0,
            },
            "expected": {"count": 14, "dia": 12.0, "layers": 2, "spacing": 37.0},
        },
        {
            "name": "two_layers_when_one_layer_spacing_fails",
            "inputs": {
                "ast_required_mm2": 1000.0,
                "b_mm": 200.0,
                "cover_mm": 25.0,
                "stirrup_dia_mm": 8.0,
                "allowed_dia_mm": [12.0],
                "max_layers": 2,
                "objective": "min_area",
                "agg_size_mm": 20.0,
            },
            "expected": {"count": 9, "dia": 12.0, "layers": 2, "spacing": 30.0},
        },
        {
            "name": "max_bars_per_layer_can_force_dia_change",
            "inputs": {
                "ast_required_mm2": 1600.0,
                "b_mm": 250.0,
                "cover_mm": 25.0,
                "stirrup_dia_mm": 8.0,
                "allowed_dia_mm": [12.0, 16.0],
                "max_layers": 2,
                "objective": "min_area",
                "max_bars_per_layer": 7,
                "agg_size_mm": 20.0,
            },
            "expected": {"count": 8, "dia": 16.0, "layers": 2, "spacing": 56.0},
        },
        {
            "name": "simple_feasible_single_layer",
            "inputs": {
                "ast_required_mm2": 1000.0,
                "b_mm": 300.0,
                "cover_mm": 25.0,
                "stirrup_dia_mm": 8.0,
                "allowed_dia_mm": [12.0, 16.0, 20.0],
                "max_layers": 2,
                "objective": "min_area",
                "agg_size_mm": 20.0,
            },
            "expected": {"count": 5, "dia": 16.0, "layers": 1, "spacing": 54.0},
        },
        {
            "name": "zero_ast_returns_minimum_arrangement",
            "inputs": {
                "ast_required_mm2": 0.0,
                "b_mm": 230.0,
                "cover_mm": 25.0,
                "stirrup_dia_mm": 8.0,
                "objective": "min_area",
            },
            "expected": {"count": 2, "dia": 12.0, "layers": 1, "spacing": 0.0},
        },
    ],
)
def test_optimizer_min_area_benchmark_vectors(case):
    res = optimize_bar_arrangement(**case["inputs"])

    assert res.is_feasible is True, case["name"]
    assert res.arrangement is not None
    assert res.objective == "min_area"

    exp = case["expected"]
    assert res.arrangement.count == exp["count"], case["name"]
    assert res.arrangement.diameter == pytest.approx(exp["dia"]), case["name"]
    assert res.arrangement.layers == exp["layers"], case["name"]
    assert res.arrangement.spacing == pytest.approx(exp["spacing"]), case["name"]
    assert res.arrangement.area_provided >= case["inputs"]["ast_required_mm2"]


def test_optimizer_is_deterministic_for_same_inputs():
    r1 = optimize_bar_arrangement(
        ast_required_mm2=900, b_mm=230, cover_mm=25, stirrup_dia_mm=8
    )
    r2 = optimize_bar_arrangement(
        ast_required_mm2=900, b_mm=230, cover_mm=25, stirrup_dia_mm=8
    )

    assert r1.is_feasible is True
    assert r2.is_feasible is True
    assert r1.arrangement == r2.arrangement
    assert r1.checks["selection"]["objective"] == "min_area"


def test_optimizer_prefers_two_layers_when_one_layer_spacing_fails():
    # Force a case where 1-layer spacing fails but 2-layer spacing passes
    # by restricting to a single diameter.
    res = optimize_bar_arrangement(
        ast_required_mm2=1600,
        b_mm=200,
        cover_mm=25,
        stirrup_dia_mm=8,
        allowed_dia_mm=[16],
        max_layers=2,
    )

    assert res.is_feasible is True
    assert res.arrangement is not None
    assert res.arrangement.layers == 2


def test_optimizer_returns_structured_failure_when_infeasible():
    # Extremely narrow section: should be infeasible under spacing rules.
    res = optimize_bar_arrangement(
        ast_required_mm2=2000,
        b_mm=120,
        cover_mm=25,
        stirrup_dia_mm=8,
        max_layers=2,
    )

    assert res.is_feasible is False
    assert res.arrangement is None
    assert "No feasible" in res.remarks
    assert res.candidates_considered > 0


def test_optimizer_rejects_invalid_geometry_inputs():
    res = optimize_bar_arrangement(ast_required_mm2=500, b_mm=0, cover_mm=25)
    assert res.is_feasible is False
    assert res.arrangement is None


def test_optimizer_min_bar_count_objective_changes_preference():
    # With min_bar_count, the optimizer should prefer a larger dia / fewer bars
    # compared to min_area in at least some cases.
    base = optimize_bar_arrangement(
        ast_required_mm2=800, b_mm=250, cover_mm=25, objective="min_area"
    )
    alt = optimize_bar_arrangement(
        ast_required_mm2=800, b_mm=250, cover_mm=25, objective="min_bar_count"
    )

    assert base.is_feasible is True
    assert alt.is_feasible is True
    assert base.arrangement is not None
    assert alt.arrangement is not None

    # min_bar_count should not increase bar count vs min_area.
    assert alt.arrangement.count <= base.arrangement.count


def test_optimizer_rejects_max_layers_lt_1():
    res = optimize_bar_arrangement(
        ast_required_mm2=500, b_mm=230, cover_mm=25, max_layers=0
    )
    assert res.is_feasible is False
    assert res.arrangement is None
    assert "max_layers" in res.remarks


def test_optimizer_ast_required_le_zero_returns_minimum_arrangement():
    res = optimize_bar_arrangement(ast_required_mm2=0, b_mm=230, cover_mm=25)
    assert res.is_feasible is True
    assert res.arrangement is not None
    assert res.arrangement.count == 2
    assert res.arrangement.diameter == 12.0
    assert res.arrangement.layers == 1


def test_optimizer_max_spacing_objective_prefers_more_spacing():
    # Include an invalid diameter to cover the dia_mm <= 0 branch.
    res = optimize_bar_arrangement(
        ast_required_mm2=300,
        b_mm=250,
        cover_mm=25,
        allowed_dia_mm=[-16, 12, 16],
        objective="max_spacing",
        max_layers=1,
    )

    assert res.is_feasible is True
    assert res.arrangement is not None
    assert res.arrangement.count == 2
    assert res.arrangement.diameter == 16.0


def test_optimizer_max_bars_per_layer_cap_can_force_infeasible():
    res = optimize_bar_arrangement(
        ast_required_mm2=2000,
        b_mm=250,
        cover_mm=25,
        allowed_dia_mm=[12],
        max_layers=2,
        max_bars_per_layer=2,
    )

    assert res.is_feasible is False
    assert res.arrangement is None
    assert res.candidates_considered > 0


def test_optimizer_unknown_objective_raises_value_error():
    with pytest.raises(ValueError):
        optimize_bar_arrangement(
            ast_required_mm2=400,
            b_mm=250,
            cover_mm=25,
            allowed_dia_mm=[16],
            objective=cast(Objective, "not_a_real_objective"),
        )
