# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for API result dataclasses."""

import json

import pytest

from structural_lib.api_results import (
    CostBreakdown,
    CostOptimizationResult,
    DesignSuggestionsResult,
    OptimalDesign,
    SmartAnalysisResult,
    Suggestion,
)


class TestCostOptimizationResult:
    """Tests for CostOptimizationResult."""

    def test_create_cost_optimization_result(self):
        """Test creating a cost optimization result."""
        breakdown = CostBreakdown(
            concrete_cost=15000,
            steel_cost=25000,
            formwork_cost=10000,
            labor_adjustment=5000,
            total_cost=55000,
            currency="INR",
        )

        design = OptimalDesign(
            b_mm=300,
            D_mm=500,
            d_mm=450,
            fck_nmm2=25,
            fy_nmm2=500,
            cost_breakdown=breakdown,
            is_valid=True,
        )

        result = CostOptimizationResult(
            optimal_design=design,
            baseline_cost=70000,
            savings_amount=15000,
            savings_percent=21.4,
            alternatives=[],
            candidates_evaluated=150,
            candidates_valid=45,
            computation_time_sec=2.5,
        )

        assert result.optimal_design.b_mm == 300
        assert result.savings_percent == 21.4
        assert result.candidates_evaluated == 150

    def test_cost_optimization_summary(self):
        """Test summary method."""
        breakdown = CostBreakdown(
            concrete_cost=15000,
            steel_cost=25000,
            formwork_cost=10000,
            labor_adjustment=5000,
            total_cost=55000,
            currency="INR",
        )

        design = OptimalDesign(
            b_mm=300,
            D_mm=500,
            d_mm=450,
            fck_nmm2=25,
            fy_nmm2=500,
            cost_breakdown=breakdown,
            is_valid=True,
        )

        result = CostOptimizationResult(
            optimal_design=design,
            baseline_cost=70000,
            savings_amount=15000,
            savings_percent=21.4,
            alternatives=[],
            candidates_evaluated=150,
            candidates_valid=45,
            computation_time_sec=2.5,
        )

        summary = result.summary()
        assert "300×500mm" in summary
        assert "INR55,000" in summary
        assert "21.4%" in summary

    def test_cost_optimization_to_dict(self):
        """Test to_dict conversion."""
        breakdown = CostBreakdown(
            concrete_cost=15000,
            steel_cost=25000,
            formwork_cost=10000,
            labor_adjustment=5000,
            total_cost=55000,
            currency="INR",
        )

        design = OptimalDesign(
            b_mm=300,
            D_mm=500,
            d_mm=450,
            fck_nmm2=25,
            fy_nmm2=500,
            cost_breakdown=breakdown,
            is_valid=True,
        )

        result = CostOptimizationResult(
            optimal_design=design,
            baseline_cost=70000,
            savings_amount=15000,
            savings_percent=21.4,
            alternatives=[],
            candidates_evaluated=150,
            candidates_valid=45,
            computation_time_sec=2.5,
        )

        data = result.to_dict()
        assert data["savings_percent"] == 21.4
        assert data["optimal_design"]["b_mm"] == 300
        assert data["optimal_design"]["cost_breakdown"]["currency"] == "INR"

    def test_cost_optimization_immutable(self):
        """Test that result is immutable."""
        breakdown = CostBreakdown(
            concrete_cost=15000,
            steel_cost=25000,
            formwork_cost=10000,
            labor_adjustment=5000,
            total_cost=55000,
            currency="INR",
        )

        design = OptimalDesign(
            b_mm=300,
            D_mm=500,
            d_mm=450,
            fck_nmm2=25,
            fy_nmm2=500,
            cost_breakdown=breakdown,
            is_valid=True,
        )

        result = CostOptimizationResult(
            optimal_design=design,
            baseline_cost=70000,
            savings_amount=15000,
            savings_percent=21.4,
            alternatives=[],
            candidates_evaluated=150,
            candidates_valid=45,
            computation_time_sec=2.5,
        )

        with pytest.raises(AttributeError):
            result.savings_percent = 30.0  # type: ignore


class TestDesignSuggestionsResult:
    """Tests for DesignSuggestionsResult."""

    def test_create_design_suggestions_result(self):
        """Test creating design suggestions result."""
        suggestions = [
            Suggestion(
                category="geometry",
                title="Reduce beam depth",
                impact="HIGH",
                confidence=0.85,
                rationale="Current depth exceeds required by 15%",
                estimated_benefit="10% cost savings",
                action_steps=["Reduce D to 450mm", "Verify deflection"],
                clause_refs=["Cl. 23.2"],
            ),
            Suggestion(
                category="steel",
                title="Optimize bar count",
                impact="MEDIUM",
                confidence=0.75,
                rationale="Using 5 bars when 4 sufficient",
                estimated_benefit="5% steel savings",
                action_steps=["Use 4-#20mm", "Check spacing"],
                clause_refs=["Cl. 26.3"],
            ),
        ]

        result = DesignSuggestionsResult(
            suggestions=suggestions,
            total_count=2,
            high_impact_count=1,
            medium_impact_count=1,
            low_impact_count=0,
            analysis_time_ms=125.5,
            engine_version="1.0.0",
        )

        assert result.total_count == 2
        assert result.high_impact_count == 1
        assert len(result.suggestions) == 2

    def test_suggestions_summary(self):
        """Test summary method."""
        suggestions = []
        result = DesignSuggestionsResult(
            suggestions=suggestions,
            total_count=8,
            high_impact_count=2,
            medium_impact_count=4,
            low_impact_count=2,
            analysis_time_ms=125.5,
            engine_version="1.0.0",
        )

        summary = result.summary()
        assert "8 suggestions" in summary
        assert "2 high" in summary
        assert "4 medium" in summary
        assert "2 low" in summary

    def test_high_impact_filter(self):
        """Test filtering high impact suggestions."""
        suggestions = [
            Suggestion(
                category="geometry",
                title="High impact suggestion",
                impact="HIGH",
                confidence=0.85,
                rationale="Test",
                estimated_benefit=None,
                action_steps=[],
                clause_refs=[],
            ),
            Suggestion(
                category="steel",
                title="Medium impact suggestion",
                impact="MEDIUM",
                confidence=0.75,
                rationale="Test",
                estimated_benefit=None,
                action_steps=[],
                clause_refs=[],
            ),
            Suggestion(
                category="cost",
                title="Another high impact",
                impact="HIGH",
                confidence=0.90,
                rationale="Test",
                estimated_benefit=None,
                action_steps=[],
                clause_refs=[],
            ),
        ]

        result = DesignSuggestionsResult(
            suggestions=suggestions,
            total_count=3,
            high_impact_count=2,
            medium_impact_count=1,
            low_impact_count=0,
            analysis_time_ms=125.5,
            engine_version="1.0.0",
        )

        high = result.high_impact_suggestions()
        assert len(high) == 2
        assert all(s.impact == "HIGH" for s in high)

    def test_by_category_filter(self):
        """Test filtering by category."""
        suggestions = [
            Suggestion(
                category="geometry",
                title="Geo 1",
                impact="HIGH",
                confidence=0.85,
                rationale="Test",
                estimated_benefit=None,
                action_steps=[],
                clause_refs=[],
            ),
            Suggestion(
                category="steel",
                title="Steel 1",
                impact="MEDIUM",
                confidence=0.75,
                rationale="Test",
                estimated_benefit=None,
                action_steps=[],
                clause_refs=[],
            ),
            Suggestion(
                category="geometry",
                title="Geo 2",
                impact="LOW",
                confidence=0.65,
                rationale="Test",
                estimated_benefit=None,
                action_steps=[],
                clause_refs=[],
            ),
        ]

        result = DesignSuggestionsResult(
            suggestions=suggestions,
            total_count=3,
            high_impact_count=1,
            medium_impact_count=1,
            low_impact_count=1,
            analysis_time_ms=125.5,
            engine_version="1.0.0",
        )

        geometry = result.by_category("geometry")
        assert len(geometry) == 2
        assert all(s.category == "geometry" for s in geometry)


class TestSmartAnalysisResult:
    """Tests for SmartAnalysisResult."""

    def test_create_smart_analysis_result(self):
        """Test creating smart analysis result."""
        result = SmartAnalysisResult(
            summary_data={"overall_score": 78.5, "recommendations_count": 8},
            metadata={"analysis_time_sec": 5.2, "modules_run": 4},
            cost={"savings_percent": 15.2},
            suggestions={"high_impact_count": 2},
            sensitivity={"critical_parameters": ["fck", "fy"]},
            constructability={"overall_score": 82.0},
        )

        assert result.summary_data["overall_score"] == 78.5
        assert result.cost["savings_percent"] == 15.2
        assert result.metadata["modules_run"] == 4

    def test_smart_analysis_summary(self):
        """Test summary method."""
        result = SmartAnalysisResult(
            summary_data={"overall_score": 78.5},
            metadata={},
        )

        summary = result.summary()
        assert "78.5/100" in summary

    def test_smart_analysis_to_json(self):
        """Test to_json conversion."""
        result = SmartAnalysisResult(
            summary_data={"overall_score": 78.5},
            metadata={},
            cost={"savings_percent": 15.2},
        )

        json_str = result.to_json()
        data = json.loads(json_str)
        assert data["summary_data"]["overall_score"] == 78.5
        assert data["cost"]["savings_percent"] == 15.2

    def test_smart_analysis_to_text(self):
        """Test to_text conversion."""
        result = SmartAnalysisResult(
            summary_data={"overall_score": 78.5},
            metadata={},
            cost={"savings_percent": 15.2},
            suggestions={
                "high_impact_count": 2,
                "medium_impact_count": 4,
                "low_impact_count": 2,
            },
            sensitivity={"critical": ["fck"]},
            constructability={"overall_score": 82.0},
        )

        text = result.to_text()
        assert "Smart Design Analysis Report" in text
        assert "78.5/100" in text
        assert "15.2%" in text
        assert "2 high, 4 medium, 2 low" in text
        assert "82.0/100" in text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
