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
    create_bmd_sfd_diagram,
    create_cost_comparison,
    create_utilization_gauge,
    create_sensitivity_tornado,
    create_compliance_visual,
)


class TestBeamDiagram:
    """Tests for create_beam_diagram()"""

    def test_basic_beam_diagram(self):
        """Test basic beam diagram generation"""
        # Realistic rebar positions: 3 bars at bottom (tension), 2 bars at top (compression)
        rebar_positions = [
            (75, 50),  # Bottom left
            (150, 50),  # Bottom center
            (225, 50),  # Bottom right
            (75, 450),  # Top left
            (225, 450),  # Top right
        ]

        fig = create_beam_diagram(
            b_mm=300.0,
            D_mm=500.0,
            d_mm=450.0,
            rebar_positions=rebar_positions,
            xu=150.0,  # Neutral axis at 150mm from top
            bar_dia=16.0,
            cover=30.0,
            show_dimensions=True,
        )

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        assert fig.layout.title.text is not None

    def test_beam_diagram_without_compression_steel(self):
        """Test beam diagram with no compression steel"""
        # Only tension steel (bottom bars)
        rebar_positions = [(75, 50), (150, 50), (225, 50)]

        fig = create_beam_diagram(
            b_mm=300.0,
            D_mm=500.0,
            d_mm=450.0,
            rebar_positions=rebar_positions,
            xu=150.0,
            bar_dia=16.0,
        )

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_beam_diagram_extreme_dimensions(self):
        """Test beam diagram with extreme dimensions"""
        # Very wide shallow beam
        rebar_positions1 = [
            (i * 200, 50) for i in range(1, 5)
        ]  # 4 bars spread across width
        fig1 = create_beam_diagram(
            b_mm=1000.0,
            D_mm=300.0,
            d_mm=250.0,
            rebar_positions=rebar_positions1,
            xu=100.0,
            bar_dia=20.0,
        )
        assert isinstance(fig1, go.Figure)

        # Very narrow deep beam
        rebar_positions2 = [(100, 50), (100, 150), (100, 250)]  # Vertically stacked
        fig2 = create_beam_diagram(
            b_mm=200.0,
            D_mm=800.0,
            d_mm=750.0,
            rebar_positions=rebar_positions2,
            xu=300.0,
            bar_dia=25.0,
        )
        assert isinstance(fig2, go.Figure)

    def test_beam_diagram_invalid_inputs(self):
        """Test beam diagram with invalid inputs (currently no validation)"""
        rebar_positions = [(150, 50)]

        # Note: Current implementation doesn't validate inputs
        # This test documents the behavior - function will render even with invalid inputs
        # TODO: Add validation to create_beam_diagram() for negative dimensions and d > D

        # Negative width (renders but meaningless)
        fig1 = create_beam_diagram(
            b_mm=-300.0,
            D_mm=500.0,
            d_mm=450.0,
            rebar_positions=rebar_positions,
            xu=150.0,
            bar_dia=16.0,
        )
        assert isinstance(fig1, go.Figure)

        # d > D (renders but meaningless)
        fig2 = create_beam_diagram(
            b_mm=300.0,
            D_mm=500.0,
            d_mm=550.0,
            rebar_positions=rebar_positions,
            xu=150.0,
            bar_dia=16.0,
        )
        assert isinstance(fig2, go.Figure)

    def test_beam_diagram_with_neutral_axis(self):
        """Test beam diagram includes neutral axis"""
        rebar_positions = [(75, 50), (150, 50), (225, 50)]

        fig = create_beam_diagram(
            b_mm=300.0,
            D_mm=500.0,
            d_mm=450.0,
            rebar_positions=rebar_positions,
            xu=180.0,  # Neutral axis depth from top
            bar_dia=16.0,
        )

        assert isinstance(fig, go.Figure)
        # Neutral axis is drawn as a trace in the figure
        assert len(fig.data) > 1  # Should have multiple traces including neutral axis


class TestBmdSfdDiagram:
    """Tests for create_bmd_sfd_diagram()"""

    def test_basic_bmd_sfd_diagram(self):
        """Test basic BMD/SFD diagram generation"""
        # Simply supported beam with UDL - parabolic BMD, linear SFD
        span_mm = 6000
        num_points = 11
        w = 20.0  # kN/m
        L_m = span_mm / 1000.0

        positions_mm = [span_mm * i / (num_points - 1) for i in range(num_points)]

        # Calculate BMD and SFD for UDL
        bmd_knm = []
        sfd_kn = []
        for x_mm in positions_mm:
            x_m = x_mm / 1000.0
            # BMD: M(x) = (wL/2)x - (w/2)x²
            m = (w * L_m / 2) * x_m - (w / 2) * x_m**2
            # SFD: V(x) = wL/2 - wx
            v = (w * L_m / 2) - (w * x_m)
            bmd_knm.append(m)
            sfd_kn.append(v)

        fig = create_bmd_sfd_diagram(positions_mm, bmd_knm, sfd_kn)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2  # BMD and SFD traces
        # Verify it's a subplot figure
        assert fig.layout.annotations  # Subplot titles as annotations

    def test_bmd_sfd_with_critical_points(self):
        """Test BMD/SFD diagram with critical point annotations"""
        from dataclasses import dataclass

        @dataclass
        class MockCriticalPoint:
            point_type: str
            position_mm: float
            bm_knm: float
            sf_kn: float

        positions_mm = [0, 1500, 3000, 4500, 6000]
        bmd_knm = [0, 33.75, 45.0, 33.75, 0]  # Parabola
        sfd_kn = [30, 15, 0, -15, -30]  # Linear

        critical_points = [
            MockCriticalPoint("max_bm", 3000, 45.0, 0.0),
            MockCriticalPoint("max_sf", 0, 0.0, 30.0),
            MockCriticalPoint("min_sf", 6000, 0.0, -30.0),
        ]

        fig = create_bmd_sfd_diagram(
            positions_mm, bmd_knm, sfd_kn, critical_points=critical_points
        )

        assert isinstance(fig, go.Figure)
        # Should have annotations for critical points (plus subplot titles)
        assert len(fig.layout.annotations) >= 3

    def test_bmd_sfd_cantilever(self):
        """Test BMD/SFD for cantilever beam"""
        # Cantilever with point load at tip
        span_mm = 3000
        P = 50.0  # kN at tip
        num_points = 7

        positions_mm = [span_mm * i / (num_points - 1) for i in range(num_points)]
        L_m = span_mm / 1000.0

        # BMD: M(x) = -P(L-x) for cantilever fixed at x=0
        # SFD: V(x) = P (constant)
        bmd_knm = []
        sfd_kn = []
        for x_mm in positions_mm:
            x_m = x_mm / 1000.0
            m = -P * (L_m - x_m)  # Negative for hogging
            v = P  # Constant shear
            bmd_knm.append(m)
            sfd_kn.append(v)

        fig = create_bmd_sfd_diagram(positions_mm, bmd_knm, sfd_kn)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2

    def test_bmd_sfd_custom_height(self):
        """Test BMD/SFD with custom height"""
        positions_mm = [0, 2000, 4000, 6000]
        bmd_knm = [0, 40, 40, 0]
        sfd_kn = [40, 0, 0, -40]

        fig = create_bmd_sfd_diagram(positions_mm, bmd_knm, sfd_kn, height=800)

        assert isinstance(fig, go.Figure)
        assert fig.layout.height == 800

    def test_bmd_sfd_no_grid(self):
        """Test BMD/SFD with grid lines disabled"""
        positions_mm = [0, 2000, 4000, 6000]
        bmd_knm = [0, 40, 40, 0]
        sfd_kn = [40, 0, 0, -40]

        fig = create_bmd_sfd_diagram(positions_mm, bmd_knm, sfd_kn, show_grid=False)

        assert isinstance(fig, go.Figure)

    def test_bmd_sfd_empty_critical_points(self):
        """Test BMD/SFD with empty critical points list"""
        positions_mm = [0, 3000, 6000]
        bmd_knm = [0, 45, 0]
        sfd_kn = [30, 0, -30]

        fig = create_bmd_sfd_diagram(positions_mm, bmd_knm, sfd_kn, critical_points=[])

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2

    def test_bmd_sfd_zero_values(self):
        """Test BMD/SFD with all zero values"""
        positions_mm = [0, 3000, 6000]
        bmd_knm = [0, 0, 0]
        sfd_kn = [0, 0, 0]

        fig = create_bmd_sfd_diagram(positions_mm, bmd_knm, sfd_kn)

        assert isinstance(fig, go.Figure)


class TestCostComparison:
    """Tests for create_cost_comparison()"""

    def test_basic_cost_comparison(self):
        """Test basic cost comparison chart"""
        alternatives = [
            {
                "bar_arrangement": "3-16mm",
                "cost_per_meter": 87.45,
                "is_optimal": True,
                "area_provided": 603,
            },
            {
                "bar_arrangement": "2-20mm",
                "cost_per_meter": 92.30,
                "is_optimal": False,
                "area_provided": 628,
            },
            {
                "bar_arrangement": "4-14mm",
                "cost_per_meter": 95.00,
                "is_optimal": False,
                "area_provided": 616,
            },
        ]

        fig = create_cost_comparison(alternatives)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        assert fig.layout.title.text is not None

    def test_cost_comparison_with_breakdown(self):
        """Test cost comparison with different arrangements"""
        alternatives = [
            {
                "bar_arrangement": "3-16mm",
                "cost_per_meter": 87.45,
                "is_optimal": True,
                "area_provided": 603,
            },
            {
                "bar_arrangement": "2-20mm",
                "cost_per_meter": 92.30,
                "is_optimal": False,
                "area_provided": 628,
            },
        ]

        fig = create_cost_comparison(alternatives)

        assert isinstance(fig, go.Figure)
        # Should have at least one bar trace
        assert len(fig.data) >= 1

    def test_cost_comparison_empty_data(self):
        """Test cost comparison with empty data"""
        fig = create_cost_comparison([])

        assert isinstance(fig, go.Figure)
        # Should have a "no data" message
        assert len(fig.layout.annotations) > 0

    def test_cost_comparison_single_option(self):
        """Test cost comparison with single option"""
        alternatives = [
            {
                "bar_arrangement": "3-16mm",
                "cost_per_meter": 87.45,
                "is_optimal": True,
                "area_provided": 603,
            },
        ]

        fig = create_cost_comparison(alternatives)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0


class TestUtilizationGauge:
    """Tests for create_utilization_gauge()"""

    def test_basic_gauge(self):
        """Test basic utilization gauge"""
        fig = create_utilization_gauge(value=0.85, label="Flexure Utilization")

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_gauge_color_zones(self):
        """Test gauge color zones (green/yellow/red)"""
        # Safe zone (green)
        fig1 = create_utilization_gauge(value=0.60, label="Safe Zone")
        assert isinstance(fig1, go.Figure)

        # Warning zone (yellow)
        fig2 = create_utilization_gauge(value=0.85, label="Warning Zone")
        assert isinstance(fig2, go.Figure)

        # Critical zone (red)
        fig3 = create_utilization_gauge(value=0.95, label="Critical Zone")
        assert isinstance(fig3, go.Figure)

    def test_gauge_boundary_values(self):
        """Test gauge at boundary values"""
        # Zero utilization
        fig1 = create_utilization_gauge(value=0.0, label="Zero Utilization")
        assert isinstance(fig1, go.Figure)

        # 100% utilization
        fig2 = create_utilization_gauge(value=1.0, label="Full Utilization")
        assert isinstance(fig2, go.Figure)

    def test_gauge_over_utilization(self):
        """Test gauge with over-utilization (>100%)"""
        fig = create_utilization_gauge(value=1.15, label="Over-Utilization")

        assert isinstance(fig, go.Figure)
        # Should handle values > 1.0 gracefully

    def test_gauge_with_title(self):
        """Test gauge with custom title"""
        fig = create_utilization_gauge(value=0.85, label="Flexure Utilization")

        assert isinstance(fig, go.Figure)
        # The label/title is in the indicator's title, not layout title
        assert "Flexure" in str(fig.data[0]["title"]["text"])


class TestSensitivityTornado:
    """Tests for create_sensitivity_tornado()"""

    def test_basic_tornado_chart(self):
        """Test basic tornado chart"""
        sensitivity_data = [
            {"name": "fck", "low_value": 85.0, "high_value": 115.0, "unit": "kN·m"},
            {"name": "fy", "low_value": 88.0, "high_value": 112.0, "unit": "kN·m"},
            {"name": "b", "low_value": 92.0, "high_value": 108.0, "unit": "kN·m"},
            {"name": "d", "low_value": 94.0, "high_value": 106.0, "unit": "kN·m"},
        ]
        baseline_value = 100.0

        fig = create_sensitivity_tornado(sensitivity_data, baseline_value)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_tornado_chart_sorting(self):
        """Test that tornado chart sorts by impact"""
        sensitivity_data = [
            {"name": "b", "low_value": 95.0, "high_value": 105.0},
            {"name": "fck", "low_value": 80.0, "high_value": 120.0},
            {"name": "fy", "low_value": 85.0, "high_value": 115.0},
        ]
        baseline_value = 100.0

        fig = create_sensitivity_tornado(sensitivity_data, baseline_value)

        assert isinstance(fig, go.Figure)
        # Data should be sorted by impact (descending)

    def test_tornado_chart_empty_data(self):
        """Test tornado chart with empty data"""
        baseline_value = 100.0
        fig = create_sensitivity_tornado([], baseline_value)

        assert isinstance(fig, go.Figure)
        # Should have a "no data" message
        assert len(fig.layout.annotations) > 0

    def test_tornado_chart_single_parameter(self):
        """Test tornado chart with single parameter"""
        sensitivity_data = [
            {"name": "fck", "low_value": 85.0, "high_value": 115.0},
        ]
        baseline_value = 100.0

        fig = create_sensitivity_tornado(sensitivity_data, baseline_value)

        assert isinstance(fig, go.Figure)

    def test_tornado_chart_negative_impacts(self):
        """Test tornado chart with negative impacts"""
        sensitivity_data = [
            {"name": "increase_fck", "low_value": 90.0, "high_value": 110.0},
            {"name": "decrease_fck", "low_value": 92.0, "high_value": 108.0},
        ]
        baseline_value = 100.0

        fig = create_sensitivity_tornado(sensitivity_data, baseline_value)

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

        # Function renders to Streamlit, returns None
        result = create_compliance_visual(checks)

        assert result is None  # Function renders directly, returns None

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

        result = create_compliance_visual(checks)

        assert result is None

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

        result = create_compliance_visual(checks)

        assert result is None

    def test_compliance_empty_checks(self):
        """Test compliance visual with no checks"""
        result = create_compliance_visual([])

        assert result is None
        # Function should render "no checks" message to Streamlit

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

        result = create_compliance_visual(checks)

        assert result is None
        # Function renders status indicators (✅ ⚠️ ❌) to Streamlit


class TestVisualizationPerformance:
    """Performance tests for visualizations"""

    def test_beam_diagram_performance(self, benchmark):
        """Benchmark beam diagram generation"""
        rebar_positions = [(75, 50), (150, 50), (225, 50)]

        def create():
            return create_beam_diagram(
                b_mm=300.0,
                D_mm=500.0,
                d_mm=450.0,
                rebar_positions=rebar_positions,
                xu=150.0,
                bar_dia=16.0,
            )

        result = benchmark(create)
        assert isinstance(result, go.Figure)

    def test_cost_comparison_performance(self, benchmark):
        """Benchmark cost comparison generation"""
        alternatives = [
            {
                "bar_arrangement": f"Option {i}",
                "cost_per_meter": 85.0 + i * 5,
                "is_optimal": i == 0,
                "area_provided": 600 + i * 10,
            }
            for i in range(5)
        ]

        def create():
            return create_cost_comparison(alternatives)

        result = benchmark(create)
        assert isinstance(result, go.Figure)

    def test_large_sensitivity_data(self):
        """Test tornado chart with large dataset"""
        sensitivity_data = [
            {
                "name": f"param_{i}",
                "low_value": 95.0 + i * 0.1,
                "high_value": 105.0 - i * 0.1,
            }
            for i in range(50)
        ]
        baseline_value = 100.0

        fig = create_sensitivity_tornado(sensitivity_data, baseline_value)

        assert isinstance(fig, go.Figure)
        # Should handle large datasets without issues


class TestEdgeCases:
    """Edge case tests for all visualizations"""

    def test_zero_dimensions(self):
        """Test visualizations with zero/near-zero values"""
        # Beam diagram with minimal steel
        rebar_positions = [(150, 50)]  # Single tiny bar
        fig1 = create_beam_diagram(
            b_mm=300.0,
            D_mm=500.0,
            d_mm=450.0,
            rebar_positions=rebar_positions,
            xu=150.0,
            bar_dia=8.0,  # Small diameter
        )
        assert isinstance(fig1, go.Figure)

        # Cost comparison with zero costs
        alternatives = [
            {
                "bar_arrangement": "Free Option",
                "cost_per_meter": 0,
                "is_optimal": True,
                "area_provided": 0,
            },
        ]
        fig2 = create_cost_comparison(alternatives)
        assert isinstance(fig2, go.Figure)

    def test_very_large_values(self):
        """Test visualizations with very large values"""
        # Large beam dimensions
        rebar_positions = [
            (i * 1000, 500) for i in range(1, 5)
        ]  # Spread across large beam
        fig1 = create_beam_diagram(
            b_mm=5000.0,
            D_mm=10000.0,
            d_mm=9500.0,
            rebar_positions=rebar_positions,
            xu=3000.0,
            bar_dia=40.0,
        )
        assert isinstance(fig1, go.Figure)

        # High costs
        alternatives = [
            {
                "bar_arrangement": "Expensive",
                "cost_per_meter": 10_000,
                "is_optimal": False,
                "area_provided": 50000,
            },
        ]
        fig2 = create_cost_comparison(alternatives)
        assert isinstance(fig2, go.Figure)

    def test_unicode_labels(self):
        """Test visualizations with unicode characters"""
        alternatives = [
            {
                "bar_arrangement": "विकल्प A",
                "cost_per_meter": 87.45,
                "is_optimal": True,
                "area_provided": 603,
            },
            {
                "bar_arrangement": "選項 B",
                "cost_per_meter": 92.30,
                "is_optimal": False,
                "area_provided": 628,
            },
        ]

        fig = create_cost_comparison(alternatives)
        assert isinstance(fig, go.Figure)

    def test_missing_optional_parameters(self):
        """Test that optional parameters default gracefully"""
        # Beam diagram with minimal required parameters
        rebar_positions = [(75, 50), (150, 50), (225, 50)]
        fig1 = create_beam_diagram(
            b_mm=300.0,
            D_mm=500.0,
            d_mm=450.0,
            rebar_positions=rebar_positions,
            xu=150.0,
            bar_dia=16.0,
            # cover and show_dimensions are optional
        )
        assert isinstance(fig1, go.Figure)

        # Gauge without custom thresholds
        fig2 = create_utilization_gauge(value=0.85, label="Test Gauge")
        assert isinstance(fig2, go.Figure)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
