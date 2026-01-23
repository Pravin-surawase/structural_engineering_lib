"""Tests for material takeoff functions.

Session 34 (Jan 23, 2026): Phase 3 - Testing material takeoff extraction.
"""

from __future__ import annotations

import pytest

from structural_lib.bbs import (
    BeamQuantity,
    MaterialTakeoffResult,
    calculate_material_takeoff,
)


class TestMaterialTakeoff:
    """Tests for calculate_material_takeoff function."""

    def test_single_beam_nominal(self):
        """Single beam should produce valid quantities."""
        beams = [
            {
                "beam_id": "B1",
                "b_mm": 300,
                "D_mm": 450,
                "span_mm": 4000,
                "bottom_bar_count": 4,
                "bottom_bar_dia": 16,
                "top_bar_count": 2,
                "top_bar_dia": 12,
                "stirrup_dia": 8,
                "stirrup_spacing": 150,
            }
        ]
        result = calculate_material_takeoff(beams)

        assert isinstance(result, MaterialTakeoffResult)
        assert result.total_concrete_m3 > 0
        assert result.total_steel_kg > 0
        assert result.concrete_cost > 0
        assert result.steel_cost > 0
        assert result.total_cost == result.concrete_cost + result.steel_cost

    def test_multiple_beams(self):
        """Multiple beams should accumulate correctly."""
        beams = [
            {
                "beam_id": "B1",
                "b_mm": 300,
                "D_mm": 450,
                "span_mm": 4000,
                "bottom_bar_count": 4,
                "bottom_bar_dia": 16,
                "top_bar_count": 2,
                "top_bar_dia": 12,
                "stirrup_dia": 8,
                "stirrup_spacing": 150,
            },
            {
                "beam_id": "B2",
                "b_mm": 300,
                "D_mm": 450,
                "span_mm": 5000,
                "bottom_bar_count": 5,
                "bottom_bar_dia": 20,
                "top_bar_count": 2,
                "top_bar_dia": 12,
                "stirrup_dia": 10,
                "stirrup_spacing": 125,
            },
        ]
        result = calculate_material_takeoff(beams)

        assert len(result.beam_quantities) == 2
        total = sum(bq.steel_kg for bq in result.beam_quantities)
        assert abs(total - result.total_steel_kg) < 0.01

    def test_concrete_volume_calculation(self):
        """Concrete volume should be b × D × span."""
        beams = [
            {
                "beam_id": "B1",
                "b_mm": 300,  # 0.3 m
                "D_mm": 500,  # 0.5 m
                "span_mm": 6000,  # 6 m
                "bottom_bar_count": 4,
                "bottom_bar_dia": 16,
                "top_bar_count": 2,
                "top_bar_dia": 12,
                "stirrup_dia": 8,
                "stirrup_spacing": 150,
            }
        ]
        result = calculate_material_takeoff(beams)

        # Expected: 0.3 × 0.5 × 6.0 = 0.9 m³
        assert abs(result.total_concrete_m3 - 0.9) < 0.001

    def test_custom_rates(self):
        """Custom rates should affect costs."""
        beams = [
            {
                "beam_id": "B1",
                "b_mm": 300,
                "D_mm": 450,
                "span_mm": 4000,
                "bottom_bar_count": 4,
                "bottom_bar_dia": 16,
                "top_bar_count": 2,
                "top_bar_dia": 12,
                "stirrup_dia": 8,
                "stirrup_spacing": 150,
            }
        ]

        result1 = calculate_material_takeoff(beams, concrete_rate=8000, steel_rate=85)
        result2 = calculate_material_takeoff(beams, concrete_rate=10000, steel_rate=100)

        assert result2.concrete_cost > result1.concrete_cost
        assert result2.steel_cost > result1.steel_cost

    def test_wastage_factor(self):
        """Wastage should increase steel quantity."""
        beams = [
            {
                "beam_id": "B1",
                "b_mm": 300,
                "D_mm": 450,
                "span_mm": 4000,
                "bottom_bar_count": 4,
                "bottom_bar_dia": 16,
                "top_bar_count": 2,
                "top_bar_dia": 12,
                "stirrup_dia": 8,
                "stirrup_spacing": 150,
            }
        ]

        result_no_wastage = calculate_material_takeoff(beams, wastage_percent=0)
        result_with_wastage = calculate_material_takeoff(beams, wastage_percent=10)

        assert result_with_wastage.total_steel_kg > result_no_wastage.total_steel_kg

    def test_by_diameter_breakdown(self):
        """Steel breakdown by diameter should be correct."""
        beams = [
            {
                "beam_id": "B1",
                "b_mm": 300,
                "D_mm": 450,
                "span_mm": 4000,
                "bottom_bar_count": 4,
                "bottom_bar_dia": 16,
                "top_bar_count": 2,
                "top_bar_dia": 12,
                "stirrup_dia": 8,
                "stirrup_spacing": 150,
            }
        ]
        result = calculate_material_takeoff(beams)

        assert 16 in result.by_diameter  # Bottom bars
        assert 12 in result.by_diameter  # Top bars
        assert 8 in result.by_diameter  # Stirrups

        total_by_dia = sum(result.by_diameter.values())
        assert abs(total_by_dia - result.total_steel_kg) < 0.01

    def test_beam_quantities_structure(self):
        """BeamQuantity should have all required fields."""
        beams = [
            {
                "beam_id": "B1",
                "b_mm": 300,
                "D_mm": 450,
                "span_mm": 4000,
                "bottom_bar_count": 4,
                "bottom_bar_dia": 16,
                "top_bar_count": 2,
                "top_bar_dia": 12,
                "stirrup_dia": 8,
                "stirrup_spacing": 150,
            }
        ]
        result = calculate_material_takeoff(beams)

        bq = result.beam_quantities[0]
        assert isinstance(bq, BeamQuantity)
        assert bq.beam_id == "B1"
        assert bq.concrete_m3 > 0
        assert bq.bottom_steel_kg > 0
        assert bq.top_steel_kg > 0
        assert bq.stirrup_steel_kg > 0
        assert (
            abs(
                bq.steel_kg
                - (bq.bottom_steel_kg + bq.top_steel_kg + bq.stirrup_steel_kg)
            )
            < 0.001
        )

    def test_to_dict_serializable(self):
        """Result should be JSON-serializable."""
        beams = [
            {
                "beam_id": "B1",
                "b_mm": 300,
                "D_mm": 450,
                "span_mm": 4000,
                "bottom_bar_count": 4,
                "bottom_bar_dia": 16,
                "top_bar_count": 2,
                "top_bar_dia": 12,
                "stirrup_dia": 8,
                "stirrup_spacing": 150,
            }
        ]
        result = calculate_material_takeoff(beams)
        d = result.to_dict()

        assert isinstance(d, dict)
        assert "total_concrete_m3" in d
        assert "total_steel_kg" in d
        assert "by_diameter" in d
        assert "beam_count" in d

    def test_empty_beams_list(self):
        """Empty list should return zero quantities."""
        result = calculate_material_takeoff([])

        assert result.total_concrete_m3 == 0
        assert result.total_steel_kg == 0
        assert result.total_cost == 0

    def test_default_values_used(self):
        """Missing keys should use defaults."""
        beams = [{"beam_id": "B1"}]  # Minimal data
        result = calculate_material_takeoff(beams)

        # Should not raise, uses defaults
        assert result.total_concrete_m3 > 0
        assert result.total_steel_kg > 0
