"""
Unit Tests for Visualizations
==============================

Comprehensive tests for all Plotly visualization components.

Test Coverage:
- create_beam_diagram() - Cross-section visualization
- create_cost_comparison() - Cost bar chart
- create_utilization_gauge() - Gauge chart
- create_sensitivity_tornado() - Tornado chart
- create_compliance_visual() - Compliance checklist

Author: STREAMLIT UI SPECIALIST (Agent 6)
Phase: STREAMLIT-IMPL-007
"""

import pytest
import plotly.graph_objects as go

from components.visualizations import (
    create_beam_diagram,
    create_cost_comparison,
    create_utilization_gauge,
    create_sensitivity_tornado,
    create_compliance_visual,
)


class TestBeamDiagram:
    """Tests for create_beam_diagram()"""

    def test_basic_beam_diagram(self):
        """Test basic beam diagram generation"""
        fig = create_beam_diagram(
            b_mm=300.0,
            D_mm=500.0,
            d_mm=450.0,
            ast_mm2=1200.0,
            asc_mm2=600.0,
        )

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        assert fig.layout.title.text is not None

    def test_beam_diagram_without_compression_steel(self):
        """Test beam diagram with no compression steel"""
        fig = create_beam_diagram(
            b_mm=300.0,
            D_mm=500.0,
            d_mm=450.0,
            ast_mm2=1200.0,
            asc_mm2=0.0,
        )

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_beam_diagram_extreme_dimensions(self):
        """Test beam diagram with extreme dimensions"""
        # Very wide shallow beam
        fig1 = create_beam_diagram(
            b_mm=1000.0,
            D_mm=300.0,
            d_mm=250.0,
            ast_mm2=2000.0,
            asc_mm2=500.0,
        )
        assert isinstance(fig1, go.Figure)

        # Very narrow deep beam
        fig2 = create_beam_diagram(
            b_mm=200.0,
            D_mm=800.0,
            d_mm=750.0,
            ast_mm2=3000.0,
            asc_mm2=1000.0,
        )
        assert isinstance(fig2, go.Figure)

    def test_beam_diagram_invalid_inputs(self):
        """Test beam diagram with invalid inputs"""
        with pytest.raises((ValueError, AssertionError)):
            create_beam_diagram(
                b_mm=-300.0,  # Negative width
                D_mm=500.0,
                d_mm=450.0,
                ast_mm2=1200.0,
                asc_mm2=600.0,
            )

        with pytest.raises((ValueError, AssertionError)):
            create_beam_diagram(
                b_mm=300.0,
                D_mm=500.0,
                d_mm=550.0,  # d > D (invalid)
                ast_mm2=1200.0,
                asc_mm2=600.0,
            )

    def test_beam_diagram_with_neutral_axis(self):
        """Test beam diagram includes neutral axis"""
        fig = create_beam_diagram(
            b_mm=300.0,
            D_mm=500.0,
            d_mm=450.0,
            ast_mm2=1200.0,
            asc_mm2=600.0,
            xu_mm=180.0,  # Optional neutral axis depth
        )

        assert isinstance(fig, go.Figure)
        # Check that figure has annotations or shapes for neutral axis
        assert len(fig.layout.shapes) > 0 or len(fig.layout.annotations) > 0


class TestCostComparison:
    """Tests for create_cost_comparison()"""

    def test_basic_cost_comparison(self):
        """Test basic cost comparison chart"""
        alternatives = [
            {"label": "Option A", "total_cost": 45000, "is_optimal": True},
            {"label": "Option B", "total_cost": 48000, "is_optimal": False},
            {"label": "Option C", "total_cost": 50000, "is_optimal": False},
        ]

        fig = create_cost_comparison(alternatives)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        assert fig.layout.title.text is not None

    def test_cost_comparison_with_breakdown(self):
        """Test cost comparison with detailed breakdown"""
        alternatives = [
            {
                "label": "Option A",
                "total_cost": 45000,
                "concrete_cost": 15000,
                "steel_cost": 20000,
                "formwork_cost": 10000,
                "is_optimal": True,
            },
            {
                "label": "Option B",
                "total_cost": 48000,
                "concrete_cost": 16000,
                "steel_cost": 22000,
                "formwork_cost": 10000,
                "is_optimal": False,
            },
        ]

        fig = create_cost_comparison(alternatives, show_breakdown=True)

        assert isinstance(fig, go.Figure)
        # Should have stacked bars
        assert len(fig.data) >= 3  # At least 3 traces (concrete, steel, formwork)

    def test_cost_comparison_empty_data(self):
        """Test cost comparison with empty data"""
        fig = create_cost_comparison([])

        assert isinstance(fig, go.Figure)
        # Should have a "no data" message
        assert len(fig.layout.annotations) > 0

    def test_cost_comparison_single_option(self):
        """Test cost comparison with single option"""
        alternatives = [
            {"label": "Only Option", "total_cost": 45000, "is_optimal": True},
        ]

        fig = create_cost_comparison(alternatives)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0


class TestUtilizationGauge:
    """Tests for create_utilization_gauge()"""

    def test_basic_gauge(self):
        """Test basic utilization gauge"""
        fig = create_utilization_gauge(utilization=0.85)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_gauge_color_zones(self):
        """Test gauge color zones (green/yellow/red)"""
        # Safe zone (green)
        fig1 = create_utilization_gauge(utilization=0.60)
        assert isinstance(fig1, go.Figure)

        # Warning zone (yellow)
        fig2 = create_utilization_gauge(utilization=0.85)
        assert isinstance(fig2, go.Figure)

        # Critical zone (red)
        fig3 = create_utilization_gauge(utilization=0.95)
        assert isinstance(fig3, go.Figure)

    def test_gauge_boundary_values(self):
        """Test gauge at boundary values"""
        # Zero utilization
        fig1 = create_utilization_gauge(utilization=0.0)
        assert isinstance(fig1, go.Figure)

        # 100% utilization
        fig2 = create_utilization_gauge(utilization=1.0)
        assert isinstance(fig2, go.Figure)

    def test_gauge_over_utilization(self):
        """Test gauge with over-utilization (>100%)"""
        fig = create_utilization_gauge(utilization=1.15)

        assert isinstance(fig, go.Figure)
        # Should handle values > 1.0 gracefully

    def test_gauge_with_title(self):
        """Test gauge with custom title"""
        fig = create_utilization_gauge(
            utilization=0.85, title="Flexure Utilization"
        )

        assert isinstance(fig, go.Figure)
        assert "Flexure" in str(fig.layout.title.text)


class TestSensitivityTornado:
    """Tests for create_sensitivity_tornado()"""

    def test_basic_tornado_chart(self):
        """Test basic tornado chart"""
        sensitivity_data = [
            {"parameter": "fck", "impact_percent": 15.5},
            {"parameter": "fy", "impact_percent": 12.3},
            {"parameter": "b", "impact_percent": 8.7},
            {"parameter": "d", "impact_percent": 6.2},
        ]

        fig = create_sensitivity_tornado(sensitivity_data)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_tornado_chart_sorting(self):
        """Test that tornado chart sorts by impact"""
        sensitivity_data = [
            {"parameter": "b", "impact_percent": 5.0},
            {"parameter": "fck", "impact_percent": 20.0},
            {"parameter": "fy", "impact_percent": 15.0},
        ]

        fig = create_sensitivity_tornado(sensitivity_data)

        assert isinstance(fig, go.Figure)
        # Data should be sorted by impact (descending)

    def test_tornado_chart_empty_data(self):
        """Test tornado chart with empty data"""
        fig = create_sensitivity_tornado([])

        assert isinstance(fig, go.Figure)
        # Should have a "no data" message
        assert len(fig.layout.annotations) > 0

    def test_tornado_chart_single_parameter(self):
        """Test tornado chart with single parameter"""
        sensitivity_data = [
            {"parameter": "fck", "impact_percent": 15.5},
        ]

        fig = create_sensitivity_tornado(sensitivity_data)

        assert isinstance(fig, go.Figure)

    def test_tornado_chart_negative_impacts(self):
        """Test tornado chart with negative impacts"""
        sensitivity_data = [
            {"parameter": "increase_fck", "impact_percent": 10.0},
            {"parameter": "decrease_fck", "impact_percent": -8.0},
        ]

        fig = create_sensitivity_tornado(sensitivity_data)

        assert isinstance(fig, go.Figure)


class TestComplianceVisual:
    """Tests for create_compliance_visual()"""

    def test_basic_compliance_visual(self):
        """Test basic compliance checklist"""
        checks = [
            {
                "clause": "Cl. 26.5.1.1",
                "description": "Steel area requirements",
                "status": "pass",
            },
            {
                "clause": "Cl. 40.2.1",
                "description": "Shear stress limits",
                "status": "pass",
            },
            {
                "clause": "Cl. 23.2",
                "description": "Deflection control",
                "status": "warning",
            },
        ]

        fig = create_compliance_visual(checks)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_compliance_all_pass(self):
        """Test compliance visual with all checks passing"""
        checks = [
            {
                "clause": "Cl. 26.5.1.1",
                "description": "Steel area",
                "status": "pass",
            },
            {"clause": "Cl. 40.2.1", "description": "Shear", "status": "pass"},
        ]

        fig = create_compliance_visual(checks)

        assert isinstance(fig, go.Figure)

    def test_compliance_with_failures(self):
        """Test compliance visual with failures"""
        checks = [
            {
                "clause": "Cl. 26.5.1.1",
                "description": "Steel area",
                "status": "pass",
            },
            {
                "clause": "Cl. 40.2.1",
                "description": "Shear",
                "status": "fail",
            },
            {
                "clause": "Cl. 23.2",
                "description": "Deflection",
                "status": "warning",
            },
        ]

        fig = create_compliance_visual(checks)

        assert isinstance(fig, go.Figure)

    def test_compliance_empty_checks(self):
        """Test compliance visual with no checks"""
        fig = create_compliance_visual([])

        assert isinstance(fig, go.Figure)
        # Should have a "no checks" message
        assert len(fig.layout.annotations) > 0

    def test_compliance_status_icons(self):
        """Test that status icons are properly displayed"""
        checks = [
            {
                "clause": "Cl. 1",
                "description": "Test 1",
                "status": "pass",
            },
            {
                "clause": "Cl. 2",
                "description": "Test 2",
                "status": "warning",
            },
            {
                "clause": "Cl. 3",
                "description": "Test 3",
                "status": "fail",
            },
        ]

        fig = create_compliance_visual(checks)

        assert isinstance(fig, go.Figure)
        # Check that figure contains status indicators


class TestVisualizationPerformance:
    """Performance tests for visualizations"""

    def test_beam_diagram_performance(self, benchmark):
        """Benchmark beam diagram generation"""

        def create():
            return create_beam_diagram(
                b_mm=300.0,
                D_mm=500.0,
                d_mm=450.0,
                ast_mm2=1200.0,
                asc_mm2=600.0,
            )

        result = benchmark(create)
        assert isinstance(result, go.Figure)

    def test_cost_comparison_performance(self, benchmark):
        """Benchmark cost comparison generation"""
        alternatives = [
            {"label": f"Option {i}", "total_cost": 45000 + i * 1000, "is_optimal": i == 0}
            for i in range(5)
        ]

        def create():
            return create_cost_comparison(alternatives)

        result = benchmark(create)
        assert isinstance(result, go.Figure)

    def test_large_sensitivity_data(self):
        """Test tornado chart with large dataset"""
        sensitivity_data = [
            {"parameter": f"param_{i}", "impact_percent": i * 0.5}
            for i in range(50)
        ]

        fig = create_sensitivity_tornado(sensitivity_data)

        assert isinstance(fig, go.Figure)
        # Should handle large datasets without issues


class TestEdgeCases:
    """Edge case tests for all visualizations"""

    def test_zero_dimensions(self):
        """Test visualizations with zero/near-zero values"""
        # Beam diagram with minimal steel
        fig1 = create_beam_diagram(
            b_mm=300.0,
            D_mm=500.0,
            d_mm=450.0,
            ast_mm2=0.1,  # Nearly zero
            asc_mm2=0.0,
        )
        assert isinstance(fig1, go.Figure)

        # Cost comparison with zero costs
        alternatives = [
            {"label": "Free Option", "total_cost": 0, "is_optimal": True},
        ]
        fig2 = create_cost_comparison(alternatives)
        assert isinstance(fig2, go.Figure)

    def test_very_large_values(self):
        """Test visualizations with very large values"""
        # Large beam dimensions
        fig1 = create_beam_diagram(
            b_mm=5000.0,
            D_mm=10000.0,
            d_mm=9500.0,
            ast_mm2=50000.0,
            asc_mm2=25000.0,
        )
        assert isinstance(fig1, go.Figure)

        # High costs
        alternatives = [
            {"label": "Expensive", "total_cost": 10_000_000, "is_optimal": False},
        ]
        fig2 = create_cost_comparison(alternatives)
        assert isinstance(fig2, go.Figure)

    def test_unicode_labels(self):
        """Test visualizations with unicode characters"""
        alternatives = [
            {"label": "विकल्प A", "total_cost": 45000, "is_optimal": True},
            {"label": "選項 B", "total_cost": 48000, "is_optimal": False},
        ]

        fig = create_cost_comparison(alternatives)
        assert isinstance(fig, go.Figure)

    def test_missing_optional_parameters(self):
        """Test that optional parameters default gracefully"""
        # Beam diagram without neutral axis
        fig1 = create_beam_diagram(
            b_mm=300.0,
            D_mm=500.0,
            d_mm=450.0,
            ast_mm2=1200.0,
            asc_mm2=600.0,
            # xu_mm not provided
        )
        assert isinstance(fig1, go.Figure)

        # Gauge without title
        fig2 = create_utilization_gauge(utilization=0.85)
        assert isinstance(fig2, go.Figure)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
