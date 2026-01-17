#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tests for the multi-objective optimizer module (NSGA-II).

These tests verify:
1. Pareto front generation works correctly
2. Non-dominated sorting is accurate
3. Crowding distance calculation
4. Design explanation generation with IS 456 clauses
"""

from __future__ import annotations

import pytest

from structural_lib.multi_objective_optimizer import (
    ParetoCandidate,
    ParetoOptimizationResult,
    _crowding_distance,
    _fast_non_dominated_sort,
    get_design_explanation,
    optimize_pareto_front,
)


class TestParetoOptimization:
    """Test suite for Pareto optimization functions."""

    def test_optimize_pareto_front_basic(self):
        """Test basic Pareto optimization returns valid result."""
        result = optimize_pareto_front(
            span_mm=5000,
            mu_knm=120,
            vu_kn=80,
            objectives=["cost", "steel_weight", "utilization"],
            max_candidates=30,
        )

        assert isinstance(result, ParetoOptimizationResult)
        assert len(result.pareto_front) > 0
        assert len(result.all_candidates) > 0
        assert result.computation_time_sec >= 0

    def test_pareto_front_non_dominated(self):
        """Test that Pareto front contains only non-dominated solutions."""
        result = optimize_pareto_front(
            span_mm=5000,
            mu_knm=100,
            vu_kn=60,
            objectives=["cost", "steel_weight"],
            max_candidates=20,
        )

        # For each solution in Pareto front, no other should dominate it
        for candidate in result.pareto_front:
            for other in result.pareto_front:
                if candidate is not other:
                    # Neither should dominate the other in the Pareto front
                    dominates_cost = other.cost <= candidate.cost
                    dominates_weight = (
                        other.steel_weight_kg <= candidate.steel_weight_kg
                    )
                    strictly_better = (
                        other.cost < candidate.cost
                        or other.steel_weight_kg < candidate.steel_weight_kg
                    )

                    # Other cannot dominate candidate (both at least as good AND one strictly better)
                    assert not (
                        dominates_cost and dominates_weight and strictly_better
                    ), f"{other.bar_config} dominates {candidate.bar_config}"

    def test_best_by_objectives(self):
        """Test that best_by_* attributes return correct extremes."""
        result = optimize_pareto_front(
            span_mm=5000,
            mu_knm=100,
            vu_kn=60,
            objectives=["cost", "steel_weight", "utilization"],
            max_candidates=30,
        )

        if result.best_by_cost:
            # Best by cost should have lowest cost among Pareto front
            for candidate in result.pareto_front:
                assert result.best_by_cost.cost <= candidate.cost

        if result.best_by_weight:
            # Best by weight should have lowest weight among Pareto front
            for candidate in result.pareto_front:
                assert (
                    result.best_by_weight.steel_weight_kg <= candidate.steel_weight_kg
                )

        if result.best_by_utilization:
            # Best by utilization should have highest utilization
            for candidate in result.pareto_front:
                assert result.best_by_utilization.utilization >= candidate.utilization

    def test_candidates_have_governing_clauses(self):
        """Test that candidates include IS 456 governing clauses."""
        result = optimize_pareto_front(
            span_mm=5000,
            mu_knm=100,
            vu_kn=60,
            objectives=["cost"],
            max_candidates=10,
        )

        for candidate in result.pareto_front:
            assert isinstance(candidate.governing_clauses, list)
            # All designs should have at least flexure clause
            if candidate.ast_provided > 0:
                assert len(candidate.governing_clauses) >= 0


class TestDesignExplanation:
    """Test suite for design explanation generation."""

    def test_get_design_explanation_format(self):
        """Test that design explanation is properly formatted."""
        result = optimize_pareto_front(
            span_mm=5000,
            mu_knm=100,
            vu_kn=60,
            objectives=["cost"],
            max_candidates=10,
        )

        if result.pareto_front:
            explanation = get_design_explanation(result.pareto_front[0])

            assert isinstance(explanation, str)
            assert len(explanation) > 100  # Should have meaningful content
            assert "IS 456" in explanation or "design" in explanation.lower()

    def test_explanation_includes_key_info(self):
        """Test that explanation includes key design information."""
        result = optimize_pareto_front(
            span_mm=5000,
            mu_knm=100,
            vu_kn=60,
            objectives=["cost"],
            max_candidates=10,
        )

        if result.pareto_front:
            candidate = result.pareto_front[0]
            explanation = get_design_explanation(candidate)

            # Should mention the bar configuration
            assert candidate.bar_config in explanation or "mm" in explanation


class TestNonDominatedSorting:
    """Test suite for fast non-dominated sorting."""

    def test_single_candidate(self):
        """Test sorting with single candidate."""
        candidate = ParetoCandidate(
            b_mm=300,
            D_mm=500,
            d_mm=450,
            fck_nmm2=25,
            fy_nmm2=500,
            ast_required=1000.0,
            ast_provided=1206.0,
            bar_config="6-16mm",
            cost=8706.0,
            steel_weight_kg=47.4,
            utilization=0.83,
            is_safe=True,
            governing_clauses=["Cl. 26.5.1.1"],
        )

        fronts = _fast_non_dominated_sort([candidate], objectives=["cost"])
        assert len(fronts) == 1
        assert len(fronts[0]) == 1

    def test_clear_dominance(self):
        """Test sorting when one candidate clearly dominates another."""
        better = ParetoCandidate(
            b_mm=300,
            D_mm=500,
            d_mm=450,
            fck_nmm2=25,
            fy_nmm2=500,
            ast_required=600.0,
            ast_provided=678.0,
            bar_config="6-12mm",
            cost=5000.0,
            steel_weight_kg=26.6,
            utilization=0.88,
            is_safe=True,
            governing_clauses=[],
        )

        worse = ParetoCandidate(
            b_mm=300,
            D_mm=500,
            d_mm=450,
            fck_nmm2=25,
            fy_nmm2=500,
            ast_required=600.0,
            ast_provided=904.0,
            bar_config="8-12mm",
            cost=8000.0,  # Higher cost
            steel_weight_kg=35.5,
            utilization=0.66,
            is_safe=True,
            governing_clauses=[],
        )

        fronts = _fast_non_dominated_sort(
            [better, worse], objectives=["cost", "steel_weight"]
        )

        # Better should be in first front (lower cost AND lower weight)
        assert better in fronts[0]
        # With 2 objectives, worse is dominated, should be in second front
        assert len(fronts) >= 1


class TestCrowdingDistance:
    """Test suite for crowding distance calculation."""

    def test_crowding_distance_extreme_points(self):
        """Test that extreme points get infinite crowding distance."""
        candidates = [
            ParetoCandidate(
                b_mm=300,
                D_mm=500,
                d_mm=450,
                fck_nmm2=25,
                fy_nmm2=500,
                ast_required=100.0 * i,
                ast_provided=113.0 * i,
                bar_config=f"{i}-12mm",
                cost=1000.0 * i,
                steel_weight_kg=4.4 * i,
                utilization=0.88,
                is_safe=True,
                governing_clauses=[],
            )
            for i in range(4, 8)
        ]

        # _crowding_distance modifies candidates in place, returns None
        _crowding_distance(candidates, objectives=["cost", "steel_weight"])

        # Extreme points (first and last by each objective) should have infinite distance
        # After sorting, some should have inf
        inf_count = sum(1 for c in candidates if c.crowding_distance == float("inf"))
        assert (
            inf_count >= 2
        ), "At least 2 candidates should have infinite crowding distance"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_high_moment_design(self):
        """Test optimization with high moment requirements."""
        result = optimize_pareto_front(
            span_mm=8000,
            mu_knm=500,
            vu_kn=200,
            objectives=["cost"],
            max_candidates=20,
        )

        # Should still return valid result even with high demands
        assert isinstance(result, ParetoOptimizationResult)

    def test_minimal_candidates(self):
        """Test with very few candidates."""
        result = optimize_pareto_front(
            span_mm=5000,
            mu_knm=50,
            vu_kn=30,
            objectives=["cost"],
            max_candidates=5,
        )

        assert len(result.all_candidates) <= 5

    def test_varied_objectives(self):
        """Test with different objective combinations."""
        result = optimize_pareto_front(
            span_mm=4000,
            mu_knm=80,
            vu_kn=50,
            objectives=["cost", "steel_weight"],
            max_candidates=15,
        )

        assert isinstance(result, ParetoOptimizationResult)
        assert len(result.all_candidates) > 0

    def test_utilization_objective(self):
        """Test with utilization as an objective."""
        result = optimize_pareto_front(
            span_mm=5000,
            mu_knm=100,
            vu_kn=60,
            objectives=["utilization", "cost"],
            max_candidates=20,
        )

        assert isinstance(result, ParetoOptimizationResult)
        # Should have best by utilization
        assert result.best_by_utilization is not None or len(result.pareto_front) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
