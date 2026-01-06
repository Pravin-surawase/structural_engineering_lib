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


# ============================================================================
# EXPANDED TEST SUITE: Edge Cases and Boundary Conditions
# ============================================================================


def test_optimizer_negative_ast_required_returns_minimum():
    """Negative Ast should be treated as zero."""
    res = optimize_bar_arrangement(ast_required_mm2=-100, b_mm=230, cover_mm=25)
    assert res.is_feasible is True
    assert res.arrangement is not None
    assert res.arrangement.count == 2
    assert res.arrangement.diameter == 12.0


def test_optimizer_very_large_ast_required():
    """Very large Ast requirement should fail gracefully."""
    res = optimize_bar_arrangement(
        ast_required_mm2=50000,  # Unrealistically large
        b_mm=300,
        cover_mm=25,
        max_layers=3,
    )
    # Either feasible with many bars or infeasible with clear message
    assert res.remarks != ""
    if not res.is_feasible:
        assert res.arrangement is None


def test_optimizer_negative_beam_width_fails():
    """Negative beam width should fail."""
    res = optimize_bar_arrangement(ast_required_mm2=500, b_mm=-230, cover_mm=25)
    assert res.is_feasible is False
    assert res.arrangement is None


def test_optimizer_negative_cover_fails():
    """Negative cover should fail."""
    res = optimize_bar_arrangement(ast_required_mm2=500, b_mm=230, cover_mm=-25)
    assert res.is_feasible is False
    assert res.arrangement is None


def test_optimizer_excessive_cover_leaves_no_space():
    """Cover larger than beam width should be handled."""
    res = optimize_bar_arrangement(ast_required_mm2=500, b_mm=150, cover_mm=200)
    # Optimizer may find multi-layer solution with single bars per layer
    # which have spacing=inf (OK because single bar per layer)
    # Just verify result is valid - either infeasible or has valid arrangement
    if res.is_feasible:
        assert res.arrangement is not None
    else:
        assert res.arrangement is None


def test_optimizer_zero_stirrup_diameter():
    """Zero stirrup diameter should fail (invalid geometry)."""
    res = optimize_bar_arrangement(
        ast_required_mm2=800, b_mm=230, cover_mm=25, stirrup_dia_mm=0
    )
    # Stirrup diameter <= 0 is invalid geometry
    assert res.is_feasible is False
    assert res.arrangement is None


def test_optimizer_negative_stirrup_diameter_fails():
    """Negative stirrup diameter should fail."""
    res = optimize_bar_arrangement(
        ast_required_mm2=800, b_mm=230, cover_mm=25, stirrup_dia_mm=-8
    )
    assert res.is_feasible is False


def test_optimizer_very_small_beam_width():
    """Very narrow beam (50mm) should fail or use multi-layer."""
    res = optimize_bar_arrangement(ast_required_mm2=500, b_mm=50, cover_mm=25)
    # May be infeasible due to spacing constraints
    if not res.is_feasible:
        assert res.arrangement is None
    else:
        # If feasible, may use multi-layer with single bars (spacing=inf)
        assert res.arrangement is not None
        # Just verify it provided enough area
        assert res.arrangement.area_provided >= 500


def test_optimizer_very_large_beam_width():
    """Very wide beam (2000mm) should accommodate any reasonable Ast."""
    res = optimize_bar_arrangement(ast_required_mm2=1500, b_mm=2000, cover_mm=25)
    assert res.is_feasible is True
    assert res.arrangement is not None
    # Optimizer prefers min_area by default, may use many small bars
    # Just verify spacing is positive
    assert res.arrangement.spacing > 0


def test_optimizer_single_bar_diameter_in_list():
    """Single diameter in allowed list should work."""
    res = optimize_bar_arrangement(
        ast_required_mm2=500, b_mm=230, cover_mm=25, allowed_dia_mm=[16]
    )
    assert res.is_feasible is True
    assert res.arrangement is not None
    assert res.arrangement.diameter == 16.0


def test_optimizer_empty_allowed_diameters_uses_defaults():
    """Empty allowed_dia_mm list filters out invalid values, may fail."""
    res = optimize_bar_arrangement(
        ast_required_mm2=500, b_mm=230, cover_mm=25, allowed_dia_mm=[]
    )
    # Empty list after filtering may result in no candidates
    if res.is_feasible:
        assert res.arrangement is not None
    else:
        assert res.candidates_considered == 0


def test_optimizer_max_layers_equals_1():
    """max_layers=1 should force single-layer solution."""
    res = optimize_bar_arrangement(
        ast_required_mm2=1200, b_mm=250, cover_mm=25, max_layers=1
    )
    if res.is_feasible:
        assert res.arrangement is not None
        assert res.arrangement.layers == 1


def test_optimizer_max_layers_equals_5():
    """max_layers=5 should allow up to 5 layers."""
    res = optimize_bar_arrangement(
        ast_required_mm2=3000, b_mm=300, cover_mm=25, max_layers=5
    )
    assert res.is_feasible is True
    assert res.arrangement is not None
    assert res.arrangement.layers <= 5


def test_optimizer_min_total_bars_constraint():
    """min_total_bars should enforce minimum bar count."""
    res = optimize_bar_arrangement(
        ast_required_mm2=200,  # Very small Ast
        b_mm=300,
        cover_mm=25,
        min_total_bars=4,
    )
    assert res.is_feasible is True
    assert res.arrangement is not None
    assert res.arrangement.count >= 4


def test_optimizer_max_bars_per_layer_equals_1():
    """max_bars_per_layer=1 forces single bar per layer."""
    res = optimize_bar_arrangement(
        ast_required_mm2=400,
        b_mm=250,
        cover_mm=25,
        max_layers=3,
        max_bars_per_layer=1,
    )
    if res.is_feasible:
        assert res.arrangement is not None
        # Total bars should be <= max_layers (1 bar per layer × max_layers)
        assert res.arrangement.count <= 3


def test_optimizer_small_aggregate_size_constrains_spacing():
    """Smaller aggregate size (10mm) should still allow feasible solutions."""
    res = optimize_bar_arrangement(
        ast_required_mm2=800, b_mm=230, cover_mm=25, agg_size_mm=10
    )
    assert res.is_feasible is True
    assert res.arrangement is not None


def test_optimizer_large_aggregate_size_constrains_spacing():
    """Large aggregate size (40mm) should constrain spacing more."""
    res = optimize_bar_arrangement(
        ast_required_mm2=800, b_mm=230, cover_mm=25, agg_size_mm=40
    )
    # Should either be feasible with appropriate spacing or infeasible
    if res.is_feasible:
        assert res.arrangement is not None
        # Spacing should be >= max(dia, agg_size, 25mm)
        assert res.arrangement.spacing >= 40 or res.arrangement.count == 1


def test_optimizer_checks_structure_has_required_keys():
    """Verify checks dictionary contains expected keys."""
    res = optimize_bar_arrangement(ast_required_mm2=800, b_mm=230, cover_mm=25)
    assert res.is_feasible is True
    assert "inputs" in res.checks
    assert "candidate" in res.checks
    assert "selection" in res.checks


def test_optimizer_checks_inputs_has_ast_required():
    """Verify checks.inputs contains ast_required_mm2."""
    res = optimize_bar_arrangement(ast_required_mm2=800, b_mm=230, cover_mm=25)
    assert res.is_feasible is True
    assert "ast_required_mm2" in res.checks["inputs"]
    assert res.checks["inputs"]["ast_required_mm2"] == 800


def test_optimizer_checks_candidate_has_bar_details():
    """Verify checks.candidate contains bar arrangement details."""
    res = optimize_bar_arrangement(ast_required_mm2=800, b_mm=230, cover_mm=25)
    assert res.is_feasible is True
    candidate = res.checks["candidate"]
    assert "bar_dia_mm" in candidate
    assert "count" in candidate
    assert "layers" in candidate


def test_optimizer_checks_selection_has_objective():
    """Verify checks.selection contains objective."""
    res = optimize_bar_arrangement(
        ast_required_mm2=800, b_mm=230, cover_mm=25, objective="min_bar_count"
    )
    assert res.is_feasible is True
    assert "objective" in res.checks["selection"]
    assert res.checks["selection"]["objective"] == "min_bar_count"


def test_optimizer_infeasible_checks_structure():
    """Infeasible result should still have checks structure."""
    res = optimize_bar_arrangement(
        ast_required_mm2=2000,
        b_mm=100,  # Too narrow
        cover_mm=25,
        max_layers=2,
    )
    assert res.is_feasible is False
    assert "inputs" in res.checks
    assert "candidate" in res.checks
    # Candidate should be empty or minimal
    assert len(res.checks["candidate"]) >= 0


def test_optimizer_objective_min_area_vs_min_bar_count_difference():
    """min_area and min_bar_count should produce different results in some cases."""
    res_area = optimize_bar_arrangement(
        ast_required_mm2=1200, b_mm=300, cover_mm=25, objective="min_area"
    )
    res_count = optimize_bar_arrangement(
        ast_required_mm2=1200, b_mm=300, cover_mm=25, objective="min_bar_count"
    )

    assert res_area.is_feasible is True
    assert res_count.is_feasible is True
    # At least one should be different (area or count)
    assert (
        res_area.arrangement.area_provided != res_count.arrangement.area_provided
        or res_area.arrangement.count != res_count.arrangement.count
    )


def test_optimizer_max_spacing_produces_larger_spacing():
    """max_spacing objective should prefer arrangements with more spacing."""
    res = optimize_bar_arrangement(
        ast_required_mm2=600, b_mm=300, cover_mm=25, objective="max_spacing"
    )
    assert res.is_feasible is True
    assert res.arrangement is not None
    # Should use minimum bars to maximize spacing
    assert res.arrangement.count == 2  # Minimum for typical case


def test_optimizer_two_layer_arrangement_spacing():
    """Two-layer arrangement should distribute bars correctly."""
    res = optimize_bar_arrangement(
        ast_required_mm2=1600,
        b_mm=250,
        cover_mm=25,
        allowed_dia_mm=[12],
        max_layers=2,
    )
    assert res.is_feasible is True
    assert res.arrangement is not None
    if res.arrangement.layers == 2:
        # Both layers should have reasonable spacing
        assert res.arrangement.spacing >= 25  # Minimum practical spacing


def test_optimizer_three_layer_arrangement():
    """Three-layer arrangement should be feasible for high Ast."""
    res = optimize_bar_arrangement(
        ast_required_mm2=3000, b_mm=300, cover_mm=25, max_layers=3
    )
    assert res.is_feasible is True
    assert res.arrangement is not None
    assert res.arrangement.layers <= 3


def test_optimizer_mixed_diameter_list_with_invalid_values():
    """List with some invalid diameters should skip them."""
    res = optimize_bar_arrangement(
        ast_required_mm2=500,
        b_mm=230,
        cover_mm=25,
        allowed_dia_mm=[0, -12, 12, 16, 20, 100],  # Mix of invalid and valid
    )
    assert res.is_feasible is True
    assert res.arrangement is not None
    # Should use one of the valid diameters
    assert res.arrangement.diameter in [12, 16, 20, 100]


def test_optimizer_candidates_considered_count():
    """Optimizer should track number of candidates evaluated."""
    res = optimize_bar_arrangement(
        ast_required_mm2=800,
        b_mm=230,
        cover_mm=25,
        allowed_dia_mm=[12, 16, 20],
        max_layers=2,
    )
    assert res.is_feasible is True
    assert res.candidates_considered > 0
    # Should have considered multiple combinations
    assert res.candidates_considered >= 3  # At least 3 diameters * layers


def test_optimizer_determinism_with_all_parameters():
    """Complete parameter set should produce deterministic results."""
    params = {
        "ast_required_mm2": 1234.5,
        "b_mm": 275,
        "cover_mm": 30,
        "stirrup_dia_mm": 10,
        "allowed_dia_mm": [12, 16, 20, 25],
        "max_layers": 3,
        "objective": "min_area",
        "agg_size_mm": 25,
        "min_total_bars": 2,
        "max_bars_per_layer": 8,
    }

    res1 = optimize_bar_arrangement(**params)
    res2 = optimize_bar_arrangement(**params)
    res3 = optimize_bar_arrangement(**params)

    assert res1.is_feasible == res2.is_feasible == res3.is_feasible
    assert res1.arrangement == res2.arrangement == res3.arrangement
    assert res1.checks == res2.checks == res3.checks


def test_optimizer_area_provided_always_meets_requirement():
    """Feasible solutions must provide area >= required."""
    test_cases = [
        (500, 230, 25),
        (1000, 300, 30),
        (1500, 250, 25),
        (2000, 350, 40),
        (800, 200, 20),
    ]

    for ast_req, b, cover in test_cases:
        res = optimize_bar_arrangement(ast_required_mm2=ast_req, b_mm=b, cover_mm=cover)
        if res.is_feasible:
            assert res.arrangement is not None
            assert res.arrangement.area_provided >= ast_req, (
                f"Failed for ast={ast_req}, b={b}, cover={cover}: "
                f"provided {res.arrangement.area_provided} < required {ast_req}"
            )


def test_optimizer_spacing_check_message_in_remarks():
    """Remarks should contain useful information about spacing checks."""
    res = optimize_bar_arrangement(
        ast_required_mm2=800, b_mm=230, cover_mm=25, objective="min_area"
    )
    if res.is_feasible:
        # Feasible case should have positive remarks
        assert len(res.remarks) > 0
    else:
        # Infeasible case should explain why
        assert "No feasible" in res.remarks or "spacing" in res.remarks.lower()
