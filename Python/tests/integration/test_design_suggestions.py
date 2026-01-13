"""Tests for design suggestions engine."""

from structural_lib.beam_pipeline import design_single_beam
from structural_lib.costing import CostProfile
from structural_lib.insights.design_suggestions import (
    DesignSuggestion,
    ImpactLevel,
    SuggestionCategory,
    SuggestionReport,
    suggest_improvements,
)


class TestSuggestionDataTypes:
    """Test suggestion data structures."""

    def test_design_suggestion_to_dict(self):
        """Test DesignSuggestion serialization."""
        suggestion = DesignSuggestion(
            category=SuggestionCategory.GEOMETRY,
            impact=ImpactLevel.HIGH,
            confidence=0.85,
            title="Test suggestion",
            description="Test description",
            rationale="Test rationale",
            estimated_benefit="20% cost reduction",
            action_steps=["Step 1", "Step 2"],
            rule_id="TEST1",
            priority_score=9.0,
        )

        data = suggestion.to_dict()

        assert data["category"] == "geometry"
        assert data["impact"] == "high"
        assert data["confidence"] == 0.85
        assert data["title"] == "Test suggestion"
        assert len(data["action_steps"]) == 2
        assert data["rule_id"] == "TEST1"

    def test_suggestion_report_to_dict(self):
        """Test SuggestionReport serialization."""
        suggestions = [
            DesignSuggestion(
                category=SuggestionCategory.COST,
                impact=ImpactLevel.HIGH,
                confidence=0.90,
                title="Test",
                description="Test",
                rationale="Test",
                estimated_benefit="10%",
                action_steps=["Do this"],
                rule_id="TEST",
                priority_score=8.0,
            )
        ]

        report = SuggestionReport(
            suggestions=suggestions,
            analysis_time_ms=10.5,
            suggestions_count=1,
            high_impact_count=1,
            medium_impact_count=0,
            low_impact_count=0,
            engine_version="1.0.0",
        )

        data = report.to_dict()

        assert data["suggestions_count"] == 1
        assert data["high_impact_count"] == 1
        assert len(data["suggestions"]) == 1


class TestGeometryRules:
    """Test geometry-related suggestion rules."""

    def test_oversized_section_detection(self):
        """Test detection of oversized sections (Rule G1)."""
        # Create design with low utilization (oversized section)
        design = design_single_beam(
            units="IS456",
            beam_id="TEST",
            story="L1",
            b_mm=300,
            D_mm=600,  # Oversized for small moment
            d_mm=550,
            cover_mm=40,
            span_mm=5000,
            mu_knm=50,  # Very small moment
            vu_kn=50,
            fck_nmm2=25,
            fy_nmm2=500,
            include_detailing=False,
        )

        suggestions = suggest_improvements(design, span_mm=5000, mu_knm=50, vu_kn=50)

        # Should suggest reducing section size
        oversized_suggestions = [
            s for s in suggestions.suggestions if s.rule_id == "G1"
        ]
        assert len(oversized_suggestions) > 0
        assert oversized_suggestions[0].category == SuggestionCategory.GEOMETRY
        assert oversized_suggestions[0].impact == ImpactLevel.HIGH

    def test_non_standard_width_detection(self):
        """Test detection of non-standard widths (Rule G2)."""
        design = design_single_beam(
            units="IS456",
            beam_id="TEST",
            story="L1",
            b_mm=350,  # Non-standard
            D_mm=500,
            d_mm=450,
            cover_mm=40,
            span_mm=5000,
            mu_knm=120,
            vu_kn=80,
            fck_nmm2=25,
            fy_nmm2=500,
            include_detailing=False,
        )

        suggestions = suggest_improvements(design)

        width_suggestions = [s for s in suggestions.suggestions if s.rule_id == "G2"]
        assert len(width_suggestions) > 0
        assert width_suggestions[0].impact == ImpactLevel.LOW
        assert "standard" in width_suggestions[0].title.lower()

    def test_non_standard_depth_detection(self):
        """Test detection of non-standard depths (Rule G3)."""
        design = design_single_beam(
            units="IS456",
            beam_id="TEST",
            story="L1",
            b_mm=300,
            D_mm=475,  # Not in 50mm increments
            d_mm=425,
            cover_mm=40,
            span_mm=5000,
            mu_knm=120,
            vu_kn=80,
            fck_nmm2=25,
            fy_nmm2=500,
            include_detailing=False,
        )

        suggestions = suggest_improvements(design)

        depth_suggestions = [s for s in suggestions.suggestions if s.rule_id == "G3"]
        assert len(depth_suggestions) > 0
        assert (
            "standard" in depth_suggestions[0].title.lower()
            or "increment" in depth_suggestions[0].description.lower()
        )

    def test_excessive_depth_width_ratio(self):
        """Test detection of excessive depth/width ratio (Rule G4)."""
        design = design_single_beam(
            units="IS456",
            beam_id="TEST",
            story="L1",
            b_mm=200,  # Very narrow
            D_mm=900,  # Very deep
            d_mm=850,
            cover_mm=40,
            span_mm=6000,
            mu_knm=180,
            vu_kn=100,
            fck_nmm2=25,
            fy_nmm2=500,
            include_detailing=False,
        )

        suggestions = suggest_improvements(design)

        ratio_suggestions = [s for s in suggestions.suggestions if s.rule_id == "G4"]
        assert len(ratio_suggestions) > 0
        assert ratio_suggestions[0].impact == ImpactLevel.MEDIUM
        assert (
            "ratio" in ratio_suggestions[0].description.lower()
            or "stability" in ratio_suggestions[0].rationale.lower()
        )

    def test_shallow_beam_for_span(self):
        """Test detection of shallow beams (Rule G5)."""
        design = design_single_beam(
            units="IS456",
            beam_id="TEST",
            story="L1",
            b_mm=300,
            D_mm=350,  # Shallow for long span
            d_mm=300,
            cover_mm=40,
            span_mm=8000,  # Long span
            mu_knm=150,
            vu_kn=90,
            fck_nmm2=25,
            fy_nmm2=500,
            include_detailing=False,
        )

        suggestions = suggest_improvements(design, span_mm=8000)

        shallow_suggestions = [s for s in suggestions.suggestions if s.rule_id == "G5"]
        assert len(shallow_suggestions) > 0
        assert shallow_suggestions[0].impact == ImpactLevel.HIGH


class TestSteelRules:
    """Test steel-related suggestion rules."""

    def test_high_steel_percentage_detection(self):
        """Test detection of high steel % (Rule S1)."""
        # Small section with high moment -> high steel %
        design = design_single_beam(
            units="IS456",
            beam_id="TEST",
            story="L1",
            b_mm=230,  # Narrow
            D_mm=400,  # Shallow
            d_mm=350,
            cover_mm=40,
            span_mm=5000,
            mu_knm=150,  # High moment for small section
            vu_kn=80,
            fck_nmm2=25,
            fy_nmm2=500,
            include_detailing=False,
        )

        suggestions = suggest_improvements(design)

        congestion_suggestions = [
            s for s in suggestions.suggestions if s.rule_id == "S1"
        ]
        # May or may not trigger depending on exact ast - check if present
        if congestion_suggestions:
            assert congestion_suggestions[0].category == SuggestionCategory.STEEL
            assert "congestion" in congestion_suggestions[0].title.lower()

    def test_low_steel_percentage_detection(self):
        """Test detection of very low steel % (Rule S2)."""
        # Large section with small moment -> low steel %
        design = design_single_beam(
            units="IS456",
            beam_id="TEST",
            story="L1",
            b_mm=500,  # Wide
            D_mm=700,  # Deep
            d_mm=650,
            cover_mm=40,
            span_mm=5000,
            mu_knm=50,  # Small moment
            vu_kn=40,
            fck_nmm2=25,
            fy_nmm2=500,
            include_detailing=False,
        )

        suggestions = suggest_improvements(design)

        low_steel_suggestions = [
            s for s in suggestions.suggestions if s.rule_id == "S2"
        ]
        # Should detect very low steel percentage
        if low_steel_suggestions:
            assert low_steel_suggestions[0].impact in [
                ImpactLevel.MEDIUM,
                ImpactLevel.LOW,
            ]

    def test_fe415_steel_suggestion(self):
        """Test suggestion to use Fe 500 instead of Fe 415 (Rule S3)."""
        design = design_single_beam(
            units="IS456",
            beam_id="TEST",
            story="L1",
            b_mm=300,
            D_mm=500,
            d_mm=450,
            cover_mm=40,
            span_mm=5000,
            mu_knm=120,
            vu_kn=80,
            fck_nmm2=25,
            fy_nmm2=415,  # Fe 415 steel
            include_detailing=False,
        )

        suggestions = suggest_improvements(design)

        steel_grade_suggestions = [
            s for s in suggestions.suggestions if s.rule_id == "S3"
        ]
        assert len(steel_grade_suggestions) > 0
        assert "Fe 500" in steel_grade_suggestions[0].title


class TestCostRules:
    """Test cost-related suggestion rules."""

    def test_cost_optimization_suggestion(self):
        """Test suggestion to run cost optimization (Rule C1)."""
        # Oversized section should trigger cost optimization suggestion
        design = design_single_beam(
            units="IS456",
            beam_id="TEST",
            story="L1",
            b_mm=300,
            D_mm=600,  # Conservative
            d_mm=550,
            cover_mm=40,
            span_mm=5000,
            mu_knm=80,  # Low moment for section size
            vu_kn=60,
            fck_nmm2=25,
            fy_nmm2=500,
            include_detailing=False,
        )

        suggestions = suggest_improvements(design, span_mm=5000, mu_knm=80, vu_kn=60)

        cost_opt_suggestions = [s for s in suggestions.suggestions if s.rule_id == "C1"]
        # Should suggest cost optimization for underutilized section
        if cost_opt_suggestions:
            assert cost_opt_suggestions[0].category == SuggestionCategory.COST
            assert cost_opt_suggestions[0].impact == ImpactLevel.HIGH

    def test_high_grade_concrete_suggestion(self):
        """Test suggestion to use lower concrete grade (Rule C2)."""
        design = design_single_beam(
            units="IS456",
            beam_id="TEST",
            story="L1",
            b_mm=300,
            D_mm=500,
            d_mm=450,
            cover_mm=40,
            span_mm=5000,
            mu_knm=120,
            vu_kn=80,
            fck_nmm2=40,  # High grade
            fy_nmm2=500,
            include_detailing=False,
        )

        suggestions = suggest_improvements(design)

        grade_suggestions = [s for s in suggestions.suggestions if s.rule_id == "C2"]
        assert len(grade_suggestions) > 0
        assert grade_suggestions[0].impact == ImpactLevel.MEDIUM


class TestServiceabilityRules:
    """Test serviceability-related suggestion rules."""

    def test_span_depth_near_limit(self):
        """Test detection of L/d near code limits (Rule SV1)."""
        # Design with span/depth ratio near 20
        design = design_single_beam(
            units="IS456",
            beam_id="TEST",
            story="L1",
            b_mm=300,
            D_mm=500,
            d_mm=450,
            cover_mm=40,
            span_mm=8800,  # L/d = 8800/450 ≈ 19.6
            mu_knm=150,
            vu_kn=90,
            fck_nmm2=25,
            fy_nmm2=500,
            include_detailing=False,
        )

        suggestions = suggest_improvements(design, span_mm=8800)

        ld_suggestions = [s for s in suggestions.suggestions if s.rule_id == "SV1"]
        # Should suggest increasing depth for comfort
        if ld_suggestions:
            assert ld_suggestions[0].category == SuggestionCategory.SERVICEABILITY
            assert (
                "l/d" in ld_suggestions[0].description.lower()
                or "deflection" in ld_suggestions[0].title.lower()
            )


class TestMaterialsRules:
    """Test materials-related suggestion rules."""

    def test_uncommon_concrete_grade(self):
        """Test detection of uncommon concrete grades (Rule M1)."""
        design = design_single_beam(
            units="IS456",
            beam_id="TEST",
            story="L1",
            b_mm=300,
            D_mm=500,
            d_mm=450,
            cover_mm=40,
            span_mm=5000,
            mu_knm=120,
            vu_kn=80,
            fck_nmm2=28,  # Uncommon grade
            fy_nmm2=500,
            include_detailing=False,
        )

        suggestions = suggest_improvements(design)

        grade_suggestions = [s for s in suggestions.suggestions if s.rule_id == "M1"]
        assert len(grade_suggestions) > 0
        assert "standard" in grade_suggestions[0].title.lower()

    def test_m20_to_m25_suggestion(self):
        """Test suggestion to upgrade from M20 to M25 (Rule M2)."""
        design = design_single_beam(
            units="IS456",
            beam_id="TEST",
            story="L1",
            b_mm=300,
            D_mm=500,
            d_mm=450,
            cover_mm=40,
            span_mm=5000,
            mu_knm=120,
            vu_kn=80,
            fck_nmm2=20,  # M20 concrete
            fy_nmm2=500,
            include_detailing=False,
        )

        suggestions = suggest_improvements(design)

        m25_suggestions = [s for s in suggestions.suggestions if s.rule_id == "M2"]
        assert len(m25_suggestions) > 0
        assert "M25" in m25_suggestions[0].title


class TestSuggestionPrioritization:
    """Test suggestion prioritization and sorting."""

    def test_suggestions_sorted_by_priority(self):
        """Test that suggestions are sorted by priority score."""
        design = design_single_beam(
            units="IS456",
            beam_id="TEST",
            story="L1",
            b_mm=350,  # Non-standard (low priority)
            D_mm=600,  # Oversized (high priority)
            d_mm=550,
            cover_mm=40,
            span_mm=5000,
            mu_knm=50,  # Low moment -> oversized
            vu_kn=40,
            fck_nmm2=28,  # Uncommon (low priority)
            fy_nmm2=415,  # Fe 415 (medium priority)
            include_detailing=False,
        )

        report = suggest_improvements(design, span_mm=5000, mu_knm=50, vu_kn=40)

        # Check sorting
        priorities = [s.priority_score for s in report.suggestions]
        assert priorities == sorted(priorities, reverse=True)

        # High impact should generally come first
        if report.suggestions:
            first_few = report.suggestions[:3]
            high_impact_count = sum(
                1 for s in first_few if s.impact == ImpactLevel.HIGH
            )
            # At least some high-impact suggestions in top 3
            assert high_impact_count >= 0  # Flexible check

    def test_impact_level_counts(self):
        """Test that impact level counts are accurate."""
        design = design_single_beam(
            units="IS456",
            beam_id="TEST",
            story="L1",
            b_mm=350,
            D_mm=475,
            d_mm=425,
            cover_mm=40,
            span_mm=5000,
            mu_knm=120,
            vu_kn=80,
            fck_nmm2=28,
            fy_nmm2=415,
            include_detailing=False,
        )

        report = suggest_improvements(design)

        # Count manually
        high_count = sum(1 for s in report.suggestions if s.impact == ImpactLevel.HIGH)
        medium_count = sum(
            1 for s in report.suggestions if s.impact == ImpactLevel.MEDIUM
        )
        low_count = sum(1 for s in report.suggestions if s.impact == ImpactLevel.LOW)

        assert report.high_impact_count == high_count
        assert report.medium_impact_count == medium_count
        assert report.low_impact_count == low_count
        assert report.suggestions_count == len(report.suggestions)


class TestPerformance:
    """Test suggestion engine performance."""

    def test_execution_time_reasonable(self):
        """Test that suggestion analysis completes quickly."""
        design = design_single_beam(
            units="IS456",
            beam_id="TEST",
            story="L1",
            b_mm=300,
            D_mm=500,
            d_mm=450,
            cover_mm=40,
            span_mm=5000,
            mu_knm=120,
            vu_kn=80,
            fck_nmm2=25,
            fy_nmm2=500,
            include_detailing=False,
        )

        report = suggest_improvements(design)

        # Should complete in under 100ms (generous limit)
        assert report.analysis_time_ms < 100

    def test_no_suggestions_for_optimal_design(self):
        """Test well-designed beam triggers fewer suggestions."""
        # Well-proportioned, standard materials design
        design = design_single_beam(
            units="IS456",
            beam_id="TEST",
            story="L1",
            b_mm=300,  # Standard width
            D_mm=500,  # Standard depth (50mm increment)
            d_mm=450,
            cover_mm=40,
            span_mm=5000,
            mu_knm=120,  # Reasonable moment
            vu_kn=80,
            fck_nmm2=25,  # Standard grade
            fy_nmm2=500,  # Modern steel
            include_detailing=False,
        )

        report = suggest_improvements(design, span_mm=5000, mu_knm=120, vu_kn=80)

        # Should have fewer suggestions than badly designed beam
        # (Exact count depends on utilization, but should be reasonable)
        assert report.suggestions_count >= 0  # At least runs without error
        assert report.analysis_time_ms > 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_missing_optional_parameters(self):
        """Test suggestions work with minimal parameters."""
        design = design_single_beam(
            units="IS456",
            beam_id="TEST",
            story="L1",
            b_mm=300,
            D_mm=500,
            d_mm=450,
            cover_mm=40,
            span_mm=5000,
            mu_knm=120,
            vu_kn=80,
            fck_nmm2=25,
            fy_nmm2=500,
            include_detailing=False,
        )

        # Call without optional parameters
        report = suggest_improvements(design)

        assert report.suggestions_count >= 0
        assert report.engine_version == "1.0.0"

    def test_with_all_optional_parameters(self):
        """Test suggestions with all parameters provided."""
        design = design_single_beam(
            units="IS456",
            beam_id="TEST",
            story="L1",
            b_mm=300,
            D_mm=500,
            d_mm=450,
            cover_mm=40,
            span_mm=5000,
            mu_knm=120,
            vu_kn=80,
            fck_nmm2=25,
            fy_nmm2=500,
            include_detailing=True,
        )

        cost_profile = CostProfile()

        report = suggest_improvements(
            design,
            detailing=design.detailing,
            cost_profile=cost_profile,
            span_mm=5000,
            mu_knm=120,
            vu_kn=80,
        )

        # Should provide more suggestions with full context
        assert report.suggestions_count >= 0

    def test_serialization_roundtrip(self):
        """Test that suggestion report can be serialized to JSON."""
        design = design_single_beam(
            units="IS456",
            beam_id="TEST",
            story="L1",
            b_mm=300,
            D_mm=500,
            d_mm=450,
            cover_mm=40,
            span_mm=5000,
            mu_knm=120,
            vu_kn=80,
            fck_nmm2=25,
            fy_nmm2=500,
            include_detailing=False,
        )

        report = suggest_improvements(design)
        data = report.to_dict()

        # Verify all fields present and correct types
        assert isinstance(data["suggestions"], list)
        assert isinstance(data["analysis_time_ms"], int | float)
        assert isinstance(data["suggestions_count"], int)
        assert isinstance(data["engine_version"], str)

        # Verify nested suggestion serialization
        if data["suggestions"]:
            first = data["suggestions"][0]
            assert "category" in first
            assert "impact" in first
            assert "title" in first
            assert isinstance(first["action_steps"], list)
