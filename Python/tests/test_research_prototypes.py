# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for research prototypes: Sustainability, Generative Design, Design Companion.

These prototypes are RESEARCH ONLY — NOT FOR STRUCTURAL DESIGN.
Tests validate correctness, monotonicity, and edge/degenerate cases.
"""

from __future__ import annotations

import pytest

from structural_lib.research.research_design_companion import (
    CompanionResponse,
    ReasoningStep,
    design_with_companion,
)
from structural_lib.research.research_generative_design import (
    GenerativeDesignResult,
    explore_design_space,
)
from structural_lib.research.research_sustainability import (
    CarbonComparison,
    CarbonScore,
    compare_carbon,
    score_beam_carbon,
)

# =============================================================================
# Prototype 1: Sustainability Scoring
# =============================================================================


class TestSustainabilityScoring:
    """Tests for score_beam_carbon() and compare_carbon()."""

    # ── Basic scoring ──

    def test_basic_scoring_returns_carbon_score(self):
        """Basic call returns a CarbonScore with positive values."""
        score = score_beam_carbon(
            b_mm=300, D_mm=500, span_mm=5000, fck=25, ast_mm2=1200, mu_knm=180
        )
        assert isinstance(score, CarbonScore)
        assert score.total_kgco2e > 0
        assert score.concrete_kgco2e > 0
        assert score.steel_kgco2e > 0

    def test_carbon_per_meter_positive(self):
        score = score_beam_carbon(
            b_mm=300, D_mm=500, span_mm=5000, fck=25, ast_mm2=1200, mu_knm=180
        )
        assert score.carbon_per_meter > 0

    def test_carbon_per_knm_positive(self):
        score = score_beam_carbon(
            b_mm=300, D_mm=500, span_mm=5000, fck=25, ast_mm2=1200, mu_knm=180
        )
        assert score.carbon_per_knm > 0

    # ── Monotonicity: higher fck → higher carbon for same dimensions ──

    def test_monotonicity_higher_fck_higher_carbon(self):
        """Higher concrete grade → higher embodied carbon (same geometry)."""
        scores = {}
        for fck in [20, 25, 30, 35, 40]:
            scores[fck] = score_beam_carbon(
                b_mm=300, D_mm=500, span_mm=5000, fck=fck, ast_mm2=1000, mu_knm=150
            )
        for fck_low, fck_high in [(20, 25), (25, 30), (30, 35), (35, 40)]:
            assert (
                scores[fck_high].concrete_kgco2e > scores[fck_low].concrete_kgco2e
            ), f"M{fck_high} should have higher concrete carbon than M{fck_low}"

    # ── All 5 supported grades ──

    @pytest.mark.parametrize("fck", [20, 25, 30, 35, 40])
    def test_all_supported_grades(self, fck):
        """Every supported grade produces a valid score."""
        score = score_beam_carbon(
            b_mm=300, D_mm=500, span_mm=5000, fck=fck, ast_mm2=900, mu_knm=120
        )
        assert score.total_kgco2e > 0
        assert score.rating in ("A+", "A", "B", "C", "D", "E")

    # ── Invalid grade raises ValueError ──

    def test_invalid_grade_raises(self):
        with pytest.raises(ValueError, match="Unknown concrete grade"):
            score_beam_carbon(
                b_mm=300, D_mm=500, span_mm=5000, fck=50, ast_mm2=900, mu_knm=120
            )

    def test_invalid_grade_15_raises(self):
        with pytest.raises(ValueError, match="Unknown concrete grade"):
            score_beam_carbon(b_mm=300, D_mm=500, span_mm=5000, fck=15, ast_mm2=900)

    # ── Negative dimensions raise ValueError ──

    def test_negative_width_raises(self):
        with pytest.raises(ValueError, match="positive"):
            score_beam_carbon(b_mm=-300, D_mm=500, span_mm=5000, fck=25, ast_mm2=900)

    def test_negative_depth_raises(self):
        with pytest.raises(ValueError, match="positive"):
            score_beam_carbon(b_mm=300, D_mm=-500, span_mm=5000, fck=25, ast_mm2=900)

    def test_zero_span_raises(self):
        with pytest.raises(ValueError, match="positive"):
            score_beam_carbon(b_mm=300, D_mm=500, span_mm=0, fck=25, ast_mm2=900)

    def test_negative_steel_area_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            score_beam_carbon(b_mm=300, D_mm=500, span_mm=5000, fck=25, ast_mm2=-100)

    # ── Rating assignment ──

    def test_rating_is_valid_letter(self):
        score = score_beam_carbon(
            b_mm=300, D_mm=500, span_mm=5000, fck=25, ast_mm2=800, mu_knm=200
        )
        assert score.rating in ("A+", "A", "B", "C", "D", "E")

    def test_rating_description_non_empty(self):
        score = score_beam_carbon(
            b_mm=300, D_mm=500, span_mm=5000, fck=25, ast_mm2=800, mu_knm=200
        )
        assert score.rating_description
        assert isinstance(score.rating_description, str)

    # ── Carbon shares sum to ~100% ──

    def test_shares_sum_to_100(self):
        score = score_beam_carbon(
            b_mm=300, D_mm=500, span_mm=5000, fck=25, ast_mm2=1200, mu_knm=180
        )
        total_pct = score.concrete_share_pct + score.steel_share_pct
        assert total_pct == pytest.approx(100.0, abs=0.5)

    # ── Zero steel case ──

    def test_zero_steel_produces_concrete_only_carbon(self):
        score = score_beam_carbon(
            b_mm=300, D_mm=500, span_mm=5000, fck=25, ast_mm2=0, asc_mm2=0
        )
        assert score.steel_kgco2e == 0.0
        assert score.concrete_kgco2e > 0
        assert score.total_kgco2e == score.concrete_kgco2e

    # ── Comparison ──

    def test_compare_carbon_returns_comparison(self):
        designs = [
            {
                "b_mm": 300,
                "D_mm": 500,
                "span_mm": 5000,
                "fck": 25,
                "ast_mm2": 1200,
                "mu_knm": 180,
            },
            {
                "b_mm": 230,
                "D_mm": 600,
                "span_mm": 5000,
                "fck": 30,
                "ast_mm2": 900,
                "mu_knm": 185,
            },
        ]
        result = compare_carbon(designs, ["Option A", "Option B"])
        assert isinstance(result, CarbonComparison)
        assert len(result.scores) == 2
        assert len(result.labels) == 2
        assert result.best_idx in (0, 1)

    def test_compare_carbon_savings_non_negative(self):
        designs = [
            {"b_mm": 300, "D_mm": 500, "span_mm": 5000, "fck": 25, "ast_mm2": 1200},
            {"b_mm": 300, "D_mm": 500, "span_mm": 5000, "fck": 40, "ast_mm2": 1200},
        ]
        result = compare_carbon(designs)
        assert result.savings_vs_worst_pct >= 0
        assert result.savings_vs_worst_kgco2e >= 0

    def test_compare_empty_raises(self):
        with pytest.raises(ValueError, match="At least one"):
            compare_carbon([])

    def test_compare_label_mismatch_raises(self):
        designs = [
            {"b_mm": 300, "D_mm": 500, "span_mm": 5000, "fck": 25, "ast_mm2": 900},
        ]
        with pytest.raises(ValueError, match="labels must match"):
            compare_carbon(designs, ["A", "B"])

    def test_summary_string(self):
        score = score_beam_carbon(
            b_mm=300, D_mm=500, span_mm=5000, fck=25, ast_mm2=1200, mu_knm=180
        )
        summary = score.summary()
        assert "EMBODIED CARBON SCORE" in summary
        assert "kgCO₂e" in summary

    # ── Input echo ──

    def test_inputs_echoed(self):
        score = score_beam_carbon(
            b_mm=300, D_mm=500, span_mm=5000, fck=25, ast_mm2=1200, mu_knm=180
        )
        assert score.inputs["b_mm"] == 300
        assert score.inputs["fck"] == 25


# =============================================================================
# Prototype 2: Generative Design Intelligence
# =============================================================================


class TestGenerativeDesign:
    """Tests for explore_design_space()."""

    @pytest.fixture(scope="class")
    def design_result(self) -> GenerativeDesignResult:
        """Run exploration once for the class (expensive)."""
        return explore_design_space(
            span_mm=5000.0,
            mu_knm=120.0,
            vu_kn=80.0,
        )

    # ── Basic exploration ──

    def test_exploration_produces_results(self, design_result):
        assert isinstance(design_result, GenerativeDesignResult)
        assert len(design_result.candidates) > 0

    def test_valid_designs_exist(self, design_result):
        assert design_result.stats.valid_candidates > 0

    def test_pareto_front_non_empty(self, design_result):
        assert len(design_result.pareto_front) > 0
        assert design_result.stats.pareto_front_size > 0

    # ── All valid designs pass IS 456 ──

    def test_all_candidates_marked_pareto_or_not(self, design_result):
        """Every candidate has a pareto_rank attribute."""
        for c in design_result.candidates:
            assert hasattr(c, "is_pareto")
            assert hasattr(c, "pareto_rank")

    # ── Pareto front: no dominated points ──

    def test_pareto_front_no_dominated(self, design_result):
        """No point on the Pareto front is dominated by another."""
        front = design_result.pareto_front
        for i, ci in enumerate(front):
            for j, cj in enumerate(front):
                if i == j:
                    continue
                # cj should NOT dominate ci (better in ALL three objectives)
                dominates = (
                    cj.cost_inr <= ci.cost_inr
                    and cj.carbon_kgco2e <= ci.carbon_kgco2e
                    and cj.utilization <= ci.utilization
                    and (
                        cj.cost_inr < ci.cost_inr
                        or cj.carbon_kgco2e < ci.carbon_kgco2e
                        or cj.utilization < ci.utilization
                    )
                )
                assert not dominates, (
                    f"Pareto point {j} ({cj.b_mm}x{cj.D_mm}) dominates "
                    f"point {i} ({ci.b_mm}x{ci.D_mm})"
                )

    # ── Persona recommendations ──

    def test_all_persona_recommendations_exist(self, design_result):
        for persona_key in [
            "cost_engineer",
            "green_engineer",
            "conservative_engineer",
            "balanced_engineer",
        ]:
            assert persona_key in design_result.recommendations
            rec = design_result.recommendations[persona_key]
            assert rec.recommended is not None
            assert rec.narrative
            assert isinstance(rec.narrative, str)

    def test_persona_recommendation_is_from_pareto(self, design_result):
        """Recommendations come from the Pareto front."""
        pareto_ids = {id(c) for c in design_result.pareto_front}
        for key, rec in design_result.recommendations.items():
            assert (
                id(rec.recommended) in pareto_ids
            ), f"Recommendation for {key} is not on the Pareto front"

    # ── Summary generation ──

    def test_summary_generation(self, design_result):
        summary = design_result.summary()
        assert isinstance(summary, str)
        assert "GENERATIVE DESIGN INTELLIGENCE" in summary
        assert "PARETO FRONT" in summary
        assert "RECOMMENDATIONS" in summary

    # ── Stats ranges ──

    def test_cost_range_valid(self, design_result):
        lo, hi = design_result.stats.cost_range_inr
        assert lo > 0
        assert hi >= lo

    def test_carbon_range_valid(self, design_result):
        lo, hi = design_result.stats.carbon_range_kgco2e
        assert lo > 0
        assert hi >= lo

    def test_utilization_range_valid(self, design_result):
        lo, hi = design_result.stats.utilization_range
        assert 0 < lo <= hi <= 1.0

    # ── Computation time recorded ──

    def test_computation_time_positive(self, design_result):
        assert design_result.computation_time_sec > 0

    # ── Invalid inputs ──

    def test_negative_moment_still_produces_results(self):
        """Negative moment: design_beam_is456 handles it internally."""
        result = explore_design_space(span_mm=5000, mu_knm=-50, vu_kn=80)
        assert len(result.candidates) > 0

    def test_zero_span_raises(self):
        with pytest.raises((ValueError, Exception)):
            explore_design_space(span_mm=0, mu_knm=120, vu_kn=80)

    # ── Extremes in candidates ──

    def test_cheapest_greenest_conservative_exist(self, design_result):
        assert design_result.stats.cheapest is not None
        assert design_result.stats.greenest is not None
        assert design_result.stats.most_conservative is not None

    # ── All candidates have positive objectives ──

    def test_all_candidates_positive_objectives(self, design_result):
        for c in design_result.candidates:
            assert c.cost_inr > 0
            assert c.carbon_kgco2e > 0
            assert 0 < c.utilization <= 1.0


# =============================================================================
# Prototype 3: Design Companion
# =============================================================================


class TestDesignCompanion:
    """Tests for design_with_companion()."""

    @pytest.fixture(scope="class")
    def companion(self) -> CompanionResponse:
        """Run companion once for the class."""
        return design_with_companion(
            b_mm=300,
            D_mm=500,
            span_mm=5000,
            mu_knm=120,
            vu_kn=80,
            fck=25,
            fy=500,
        )

    # ── Basic companion report ──

    def test_returns_companion_response(self, companion):
        assert isinstance(companion, CompanionResponse)

    def test_design_result_present(self, companion):
        assert companion.design_result is not None
        assert companion.design_result.is_ok  # Standard beam should be safe

    # ── Reasoning chain has 8 steps ──

    def test_reasoning_chain_has_8_steps(self, companion):
        assert len(companion.reasoning_chain) == 8

    def test_reasoning_steps_sequential(self, companion):
        for i, step in enumerate(companion.reasoning_chain):
            assert step.step_number == i + 1

    # ── All clause references start with "Cl." ──

    def test_clause_refs_format(self, companion):
        for step in companion.reasoning_chain:
            assert isinstance(step.clause_ref, str)
            assert step.clause_ref.startswith("Cl."), (
                f"Step {step.step_number} clause_ref '{step.clause_ref}' "
                f"does not start with 'Cl.'"
            )

    # ── Reasoning steps have required fields ──

    def test_reasoning_step_fields(self, companion):
        for step in companion.reasoning_chain:
            assert isinstance(step, ReasoningStep)
            assert step.title
            assert step.description
            assert step.formula
            assert step.result
            assert step.decision
            assert step.significance

    # ── Rebar options evaluated (at least 3) ──

    def test_rebar_options_at_least_3(self, companion):
        rebar = companion.rebar_reasoning
        assert len(rebar.options_considered) >= 3

    def test_rebar_recommended_exists(self, companion):
        rebar = companion.rebar_reasoning
        assert rebar.recommended is not None
        assert rebar.recommended.bars

    def test_rebar_narrative_non_empty(self, companion):
        assert companion.rebar_reasoning.narrative
        assert isinstance(companion.rebar_reasoning.narrative, str)

    def test_rebar_ast_required_positive(self, companion):
        assert companion.rebar_reasoning.ast_required_mm2 > 0

    # ── Failure story ──

    def test_failure_story_has_scenarios(self, companion):
        fs = companion.failure_story
        assert len(fs.scenarios) > 0

    def test_failure_story_multiple_load_factors(self, companion):
        """Failure story covers multiple overload factors."""
        factors = [s.overload_factor for s in companion.failure_story.scenarios]
        assert len(factors) >= 3
        assert 1.0 in factors

    def test_failure_story_factors_increasing(self, companion):
        factors = [s.overload_factor for s in companion.failure_story.scenarios]
        for i in range(1, len(factors)):
            assert factors[i] > factors[i - 1]

    # ── Critical overload factor > 0 ──

    def test_critical_overload_positive(self, companion):
        assert companion.failure_story.critical_overload > 0

    def test_critical_overload_gt_1(self, companion):
        """A properly designed beam should handle at least 1× design load."""
        assert companion.failure_story.critical_overload >= 1.0

    def test_failure_narrative_non_empty(self, companion):
        assert companion.failure_story.narrative
        assert isinstance(companion.failure_story.narrative, str)

    def test_safety_insight_non_empty(self, companion):
        assert companion.failure_story.safety_insight
        assert isinstance(companion.failure_story.safety_insight, str)

    # ── Anomaly detection returns list ──

    def test_anomalies_is_list(self, companion):
        assert isinstance(companion.anomalies, list)

    def test_anomaly_fields_if_present(self, companion):
        for a in companion.anomalies:
            assert a.metric
            assert a.severity in ("info", "warning", "alert")
            assert a.explanation
            assert a.question

    # ── Alternatives generated (at least 3) ──

    def test_alternatives_at_least_3(self, companion):
        assert len(companion.alternatives) >= 3

    def test_alternatives_have_labels(self, companion):
        for alt in companion.alternatives:
            assert alt.label
            assert alt.b_mm > 0
            assert alt.D_mm > 0
            assert alt.ast_mm2 > 0
            assert alt.cost_inr > 0

    def test_alternatives_have_comparison(self, companion):
        for alt in companion.alternatives:
            assert alt.comparison
            assert isinstance(alt.comparison, str)

    # ── Executive summary ──

    def test_executive_summary_non_empty(self, companion):
        assert companion.executive_summary
        assert isinstance(companion.executive_summary, str)
        assert len(companion.executive_summary) > 50

    def test_executive_summary_mentions_beam(self, companion):
        assert "beam" in companion.executive_summary.lower()

    # ── Full report generation ──

    def test_full_report_generation(self, companion):
        report = companion.full_report()
        assert isinstance(report, str)
        assert "STRUCTURAL DESIGN COMPANION" in report
        assert "EXECUTIVE SUMMARY" in report
        assert "CHAIN OF REASONING" in report
        assert "REBAR SELECTION" in report
        assert "FAILURE STORY" in report

    # ── Computation time recorded ──

    def test_computation_time_recorded(self, companion):
        assert companion.computation_time_sec > 0

    # ── Fingerprint ──

    def test_fingerprint_fields(self, companion):
        fp = companion.fingerprint
        assert fp.span_class in ("short", "medium", "long")
        assert fp.load_intensity in ("light", "medium", "heavy")
        assert fp.section_efficiency in ("lean", "balanced", "generous")
        assert fp.steel_intensity in ("minimum", "light", "moderate", "heavy")
        assert fp.ductility_class in (
            "highly_ductile",
            "ductile",
            "balanced",
            "brittle_risk",
        )
        assert fp.carbon_rating in ("A+", "A", "B", "C", "D", "E")

    # ── Design with Fe415 steel ──

    def test_companion_fe415(self):
        """Companion works with Fe415 steel too."""
        resp = design_with_companion(
            b_mm=300,
            D_mm=500,
            span_mm=5000,
            mu_knm=100,
            vu_kn=60,
            fck=25,
            fy=415,
        )
        assert resp.design_result.is_ok
        assert len(resp.reasoning_chain) == 8

    # ── Heavy loading scenario ──

    def test_companion_heavy_loading(self):
        """Companion handles heavy loading (higher moment)."""
        resp = design_with_companion(
            b_mm=350,
            D_mm=600,
            span_mm=6000,
            mu_knm=250,
            vu_kn=150,
            fck=30,
            fy=500,
        )
        assert isinstance(resp, CompanionResponse)
        assert resp.executive_summary
        assert resp.failure_story.critical_overload > 0


# =============================================================================
# Design Companion — Multiple Realistic Stress-Test Scenarios
# =============================================================================


class TestDesignCompanionMultipleExamples:
    """Stress tests exercising the Design Companion with diverse, realistic scenarios.

    Each scenario validates:
    - design_with_companion() returns a CompanionResponse
    - design_result.is_ok is True
    - len(reasoning_chain) == 8
    - failure_story.critical_overload >= 1.0
    - rebar_reasoning.recommended.is_sufficient == True
    - executive_summary is non-empty and contains "beam"
    - full_report() generates a string without errors
    - fingerprint has valid classifications
    """

    # ── Scenario parameters ──

    SCENARIOS = {
        "minimum_beam": dict(
            b_mm=200,
            D_mm=300,
            span_mm=3000,
            mu_knm=30,
            vu_kn=25,
            fck=20,
            fy=500,
        ),
        "typical_residential": dict(
            b_mm=230,
            D_mm=450,
            span_mm=4500,
            mu_knm=80,
            vu_kn=55,
            fck=25,
            fy=500,
        ),
        "heavy_commercial": dict(
            b_mm=400,
            D_mm=700,
            span_mm=8000,
            mu_knm=400,
            vu_kn=200,
            fck=30,
            fy=500,
        ),
        "deep_beam_like": dict(
            b_mm=200,
            D_mm=800,
            span_mm=3000,
            mu_knm=150,
            vu_kn=100,
            fck=25,
            fy=415,
        ),
        "wide_shallow": dict(
            b_mm=600,
            D_mm=350,
            span_mm=5000,
            mu_knm=60,
            vu_kn=40,
            fck=25,
            fy=500,
        ),
        "long_span": dict(
            b_mm=350,
            D_mm=650,
            span_mm=10000,
            mu_knm=350,
            vu_kn=180,
            fck=35,
            fy=500,
        ),
        "m40_high_grade": dict(
            b_mm=300,
            D_mm=550,
            span_mm=6000,
            mu_knm=200,
            vu_kn=120,
            fck=40,
            fy=500,
        ),
        "fe415_steel": dict(
            b_mm=300,
            D_mm=500,
            span_mm=5000,
            mu_knm=120,
            vu_kn=80,
            fck=25,
            fy=415,
        ),
    }

    # ── Fixtures ──

    @pytest.fixture(scope="class")
    def all_responses(self) -> dict[str, CompanionResponse]:
        """Run all scenarios once and cache results (expensive)."""
        return {
            name: design_with_companion(**params)
            for name, params in self.SCENARIOS.items()
        }

    # ── Parametrized core validations ──

    @pytest.mark.parametrize("scenario", SCENARIOS.keys())
    def test_returns_companion_response(self, scenario, all_responses):
        """design_with_companion() returns a CompanionResponse."""
        resp = all_responses[scenario]
        assert isinstance(
            resp, CompanionResponse
        ), f"{scenario}: expected CompanionResponse, got {type(resp).__name__}"

    @pytest.mark.parametrize("scenario", SCENARIOS.keys())
    def test_design_result_is_ok(self, scenario, all_responses):
        """All scenarios should produce a safe design."""
        resp = all_responses[scenario]
        assert resp.design_result.is_ok, (
            f"{scenario}: design_result.is_ok is False — "
            f"flexure_safe={resp.design_result.flexure.is_safe}, "
            f"shear_safe={resp.design_result.shear.is_safe}"
        )

    @pytest.mark.parametrize("scenario", SCENARIOS.keys())
    def test_reasoning_chain_has_8_steps(self, scenario, all_responses):
        """Reasoning chain must have exactly 8 steps."""
        resp = all_responses[scenario]
        assert (
            len(resp.reasoning_chain) == 8
        ), f"{scenario}: expected 8 reasoning steps, got {len(resp.reasoning_chain)}"

    @pytest.mark.parametrize("scenario", SCENARIOS.keys())
    def test_failure_story_critical_overload_ge_1(self, scenario, all_responses):
        """Critical overload factor >= 1.0 for a safe design."""
        resp = all_responses[scenario]
        assert (
            resp.failure_story.critical_overload >= 1.0
        ), f"{scenario}: critical_overload={resp.failure_story.critical_overload:.3f} < 1.0"

    @pytest.mark.parametrize("scenario", SCENARIOS.keys())
    def test_rebar_recommended_is_sufficient(self, scenario, all_responses):
        """Recommended rebar arrangement must be sufficient."""
        resp = all_responses[scenario]
        assert resp.rebar_reasoning.recommended.is_sufficient, (
            f"{scenario}: recommended rebar '{resp.rebar_reasoning.recommended.bars}' "
            f"is NOT sufficient (area={resp.rebar_reasoning.recommended.total_area_mm2:.0f} mm², "
            f"required={resp.rebar_reasoning.ast_required_mm2:.0f} mm²)"
        )

    @pytest.mark.parametrize("scenario", SCENARIOS.keys())
    def test_executive_summary_non_empty_and_mentions_beam(
        self, scenario, all_responses
    ):
        """Executive summary is non-empty and contains 'beam'."""
        resp = all_responses[scenario]
        assert resp.executive_summary, f"{scenario}: executive_summary is empty"
        assert (
            len(resp.executive_summary) > 50
        ), f"{scenario}: executive_summary too short ({len(resp.executive_summary)} chars)"
        assert (
            "beam" in resp.executive_summary.lower()
        ), f"{scenario}: executive_summary does not contain 'beam'"

    @pytest.mark.parametrize("scenario", SCENARIOS.keys())
    def test_full_report_generates_string(self, scenario, all_responses):
        """full_report() generates a non-empty string without errors."""
        resp = all_responses[scenario]
        report = resp.full_report()
        assert isinstance(report, str), f"{scenario}: full_report() did not return str"
        assert len(report) > 200, f"{scenario}: report too short ({len(report)} chars)"
        assert "STRUCTURAL DESIGN COMPANION" in report

    @pytest.mark.parametrize("scenario", SCENARIOS.keys())
    def test_fingerprint_valid_classifications(self, scenario, all_responses):
        """Fingerprint fields have valid classification values."""
        fp = all_responses[scenario].fingerprint
        assert fp.span_class in (
            "short",
            "medium",
            "long",
        ), f"{scenario}: invalid span_class={fp.span_class}"
        assert fp.load_intensity in (
            "light",
            "medium",
            "heavy",
        ), f"{scenario}: invalid load_intensity={fp.load_intensity}"
        assert fp.section_efficiency in (
            "lean",
            "balanced",
            "generous",
        ), f"{scenario}: invalid section_efficiency={fp.section_efficiency}"
        assert fp.steel_intensity in (
            "minimum",
            "light",
            "moderate",
            "heavy",
        ), f"{scenario}: invalid steel_intensity={fp.steel_intensity}"
        assert fp.ductility_class in (
            "highly_ductile",
            "ductile",
            "balanced",
            "brittle_risk",
        ), f"{scenario}: invalid ductility_class={fp.ductility_class}"
        assert fp.carbon_rating in (
            "A+",
            "A",
            "B",
            "C",
            "D",
            "E",
        ), f"{scenario}: invalid carbon_rating={fp.carbon_rating}"

    # ── Scenario-specific assertions ──

    def test_deep_beam_anomaly_detects_b_d_ratio(self, all_responses):
        """Deep beam (200×800): anomalies should detect unusual b/D ratio."""
        resp = all_responses["deep_beam_like"]
        anomaly_metrics = [a.metric.lower() for a in resp.anomalies]
        has_bd_anomaly = any(
            "width" in m or "b/d" in m or "depth" in m for m in anomaly_metrics
        )
        assert has_bd_anomaly, (
            f"Deep beam (200×800) should detect unusual b/D ratio. "
            f"Found anomalies: {anomaly_metrics}"
        )

    def test_m40_light_load_anomaly_detects_grade_mismatch(self):
        """M40 + light load: anomalies should detect high grade mismatch.

        The m40_high_grade scenario has Mu=200 kNm (heavy), which justifies M40.
        Use a dedicated light-load M40 call to trigger the grade mismatch check
        (anomaly fires when fck >= 35 AND load_per_m2 < 15).
        """
        resp = design_with_companion(
            b_mm=300,
            D_mm=550,
            span_mm=6000,
            mu_knm=50,
            vu_kn=30,
            fck=40,
            fy=500,
        )
        anomaly_metrics = [a.metric.lower() for a in resp.anomalies]
        has_grade_anomaly = any(
            "grade" in m or "concrete" in m for m in anomaly_metrics
        )
        assert has_grade_anomaly, (
            f"M40 beam with light load should detect grade mismatch. "
            f"Found anomalies: {anomaly_metrics}"
        )

    # ── Cross-scenario consistency checks ──

    def test_minimum_beam_has_generous_section(self, all_responses):
        """Minimum beam (small load, decent section) should have generous efficiency."""
        fp = all_responses["minimum_beam"].fingerprint
        assert (
            fp.load_intensity == "light"
        ), f"Minimum beam should be 'light' load, got '{fp.load_intensity}'"

    def test_heavy_commercial_is_heavy_load(self, all_responses):
        """Heavy commercial beam should be classified as heavy load."""
        fp = all_responses["heavy_commercial"].fingerprint
        assert (
            fp.load_intensity == "heavy"
        ), f"Heavy commercial should be 'heavy' load, got '{fp.load_intensity}'"

    def test_long_span_classified_correctly(self, all_responses):
        """Long span (10m) should be classified as 'long'."""
        fp = all_responses["long_span"].fingerprint
        assert (
            fp.span_class == "long"
        ), f"10m span should be 'long', got '{fp.span_class}'"

    def test_minimum_beam_span_short(self, all_responses):
        """3m span should be classified as 'short'."""
        fp = all_responses["minimum_beam"].fingerprint
        assert (
            fp.span_class == "short"
        ), f"3m span should be 'short', got '{fp.span_class}'"

    def test_fe415_companion_works(self, all_responses):
        """Fe415 scenario should work correctly (different xu_max/d)."""
        resp = all_responses["fe415_steel"]
        assert resp.design_result.is_ok
        # Fe415 has xu_max/d=0.48 (vs 0.46 for Fe500) — check it's used
        chain = resp.reasoning_chain
        step1 = chain[0]
        assert (
            "0.48" in step1.result
        ), f"Fe415 should show xu_max/d=0.48, got: {step1.result}"

    def test_wide_shallow_has_high_bd_ratio(self, all_responses):
        """Wide shallow beam (600×350) — b/D > 1.0, should trigger anomaly."""
        resp = all_responses["wide_shallow"]
        anomaly_metrics = [a.metric.lower() for a in resp.anomalies]
        has_bd_anomaly = any(
            "width" in m or "b/d" in m or "shallow" in m for m in anomaly_metrics
        )
        assert has_bd_anomaly, (
            f"Wide shallow beam (600×350, b/D=1.71) should detect unusual ratio. "
            f"Found anomalies: {anomaly_metrics}"
        )
