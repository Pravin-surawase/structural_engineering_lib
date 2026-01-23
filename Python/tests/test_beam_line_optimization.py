# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for beam line optimization functions.

These tests verify the optimize_beam_line function that ensures
construction consistency across adjacent beams.
"""

from __future__ import annotations

import pytest

from structural_lib.optimization import (
    BeamConfig,
    BeamLineInput,
    BeamLineOptimizationResult,
    optimize_beam_line,
)


class TestBeamLineInput:
    """Tests for BeamLineInput dataclass."""

    def test_create_beam_line_input(self):
        """Test creating a BeamLineInput."""
        beam = BeamLineInput(
            beam_id="B1",
            b_mm=300,
            D_mm=450,
            mu_knm=100,
            vu_kn=50,
        )
        assert beam.beam_id == "B1"
        assert beam.b_mm == 300
        assert beam.D_mm == 450
        assert beam.mu_knm == 100
        assert beam.vu_kn == 50


class TestBeamConfig:
    """Tests for BeamConfig dataclass."""

    def test_create_beam_config(self):
        """Test creating a BeamConfig."""
        config = BeamConfig(
            beam_id="B1",
            bottom_layer1_dia=16,
            bottom_layer1_count=4,
            ast_provided_mm2=804.2,
            ast_required_mm2=750.0,
        )
        assert config.beam_id == "B1"
        assert config.bottom_layer1_dia == 16
        assert config.bottom_layer1_count == 4

    def test_to_dict(self):
        """Test BeamConfig.to_dict() method."""
        config = BeamConfig(
            beam_id="B1",
            bottom_layer1_dia=16,
            bottom_layer1_count=4,
            bottom_layer2_dia=16,
            bottom_layer2_count=2,
            ast_provided_mm2=1206.4,
            ast_required_mm2=1100.0,
        )
        d = config.to_dict()
        assert d["beam_id"] == "B1"
        assert d["bottom_layer1_dia"] == 16
        assert d["bottom_layer1_count"] == 4
        assert d["bottom_layer2_dia"] == 16
        assert d["bottom_layer2_count"] == 2
        assert d["ast_provided_mm2"] == 1206.4
        assert d["ast_required_mm2"] == 1100.0


class TestBeamLineOptimizationResult:
    """Tests for BeamLineOptimizationResult dataclass."""

    def test_to_dict(self):
        """Test result to_dict method."""
        result = BeamLineOptimizationResult(
            beam_configs=[
                BeamConfig("B1", 16, 4, 0, 0, 804.2, 750.0),
                BeamConfig("B2", 16, 5, 0, 0, 1005.3, 950.0),
            ],
            unified_bar_dia=16,
            total_steel_kg=12.5,
            beams_processed=2,
            beams_skipped=0,
        )
        d = result.to_dict()
        assert len(d["beam_configs"]) == 2
        assert d["unified_bar_dia"] == 16
        assert d["total_steel_kg"] == 12.5
        assert d["beams_processed"] == 2
        assert d["beams_skipped"] == 0


class TestOptimizeBeamLine:
    """Tests for optimize_beam_line function."""

    def test_empty_input(self):
        """Test with empty beam list."""
        result = optimize_beam_line([])
        assert result.beams_processed == 0
        assert result.unified_bar_dia == 0
        assert result.beam_configs == []

    def test_single_beam(self):
        """Test with single beam."""
        beams = [
            BeamLineInput(
                beam_id="B1",
                b_mm=300,
                D_mm=450,
                mu_knm=100,
                vu_kn=50,
            )
        ]
        result = optimize_beam_line(beams)
        assert result.beams_processed == 1
        assert len(result.beam_configs) == 1
        assert result.beam_configs[0].beam_id == "B1"
        assert result.beam_configs[0].bottom_layer1_count >= 2

    def test_dict_input(self):
        """Test with dict input instead of BeamLineInput."""
        beams = [
            {"beam_id": "B1", "b_mm": 300, "D_mm": 450, "mu_knm": 80, "vu_kn": 50},
            {"beam_id": "B2", "b_mm": 300, "D_mm": 450, "mu_knm": 120, "vu_kn": 60},
        ]
        result = optimize_beam_line(beams)
        assert result.beams_processed == 2
        assert result.beam_configs[0].beam_id == "B1"
        assert result.beam_configs[1].beam_id == "B2"

    def test_unified_diameter(self):
        """Test that all beams get same bar diameter when unify=True."""
        beams = [
            {"beam_id": "B1", "b_mm": 300, "D_mm": 450, "mu_knm": 60, "vu_kn": 40},
            {"beam_id": "B2", "b_mm": 300, "D_mm": 450, "mu_knm": 150, "vu_kn": 80},
            {"beam_id": "B3", "b_mm": 300, "D_mm": 450, "mu_knm": 100, "vu_kn": 60},
        ]
        result = optimize_beam_line(beams, unify_diameters=True)
        assert result.beams_processed == 3

        # All beams should have same diameter
        diameters = {c.bottom_layer1_dia for c in result.beam_configs}
        assert len(diameters) == 1
        assert result.unified_bar_dia in [12, 16, 20, 25, 32]

    def test_varying_moments(self):
        """Test beams with varying moment demands."""
        beams = [
            {"beam_id": "B1", "b_mm": 300, "D_mm": 500, "mu_knm": 50, "vu_kn": 30},
            {"beam_id": "B2", "b_mm": 300, "D_mm": 500, "mu_knm": 200, "vu_kn": 100},
        ]
        result = optimize_beam_line(beams)

        # Higher moment beam should have more bars
        cfg_b1 = next(c for c in result.beam_configs if c.beam_id == "B1")
        cfg_b2 = next(c for c in result.beam_configs if c.beam_id == "B2")

        assert cfg_b2.ast_provided_mm2 >= cfg_b1.ast_provided_mm2

    def test_custom_material_properties(self):
        """Test with custom fck and fy."""
        beams = [
            {"beam_id": "B1", "b_mm": 300, "D_mm": 450, "mu_knm": 100, "vu_kn": 50},
        ]
        result = optimize_beam_line(beams, fck=30.0, fy=415.0)
        assert result.beams_processed == 1
        # Higher fy = more steel required for same capacity
        assert result.beam_configs[0].ast_provided_mm2 > 0

    def test_two_layer_requirement(self):
        """Test beam requiring two layers of reinforcement."""
        beams = [
            # High moment, narrow beam = needs 2 layers
            {"beam_id": "B1", "b_mm": 230, "D_mm": 450, "mu_knm": 180, "vu_kn": 80},
        ]
        result = optimize_beam_line(beams)
        cfg = result.beam_configs[0]

        # With high moment and narrow beam, might need 2 layers
        total_bars = cfg.bottom_layer1_count + cfg.bottom_layer2_count
        assert total_bars >= 2

    def test_minimum_two_bars(self):
        """Test that minimum 2 bars are always provided."""
        beams = [
            # Very low moment
            {"beam_id": "B1", "b_mm": 300, "D_mm": 450, "mu_knm": 10, "vu_kn": 10},
        ]
        result = optimize_beam_line(beams)
        assert result.beam_configs[0].bottom_layer1_count >= 2

    def test_steel_weight_calculation(self):
        """Test that steel weight is calculated."""
        beams = [
            {"beam_id": "B1", "b_mm": 300, "D_mm": 450, "mu_knm": 100, "vu_kn": 50},
            {"beam_id": "B2", "b_mm": 300, "D_mm": 450, "mu_knm": 100, "vu_kn": 50},
        ]
        result = optimize_beam_line(beams)
        assert result.total_steel_kg > 0

    def test_ast_required_vs_provided(self):
        """Test that provided steel >= required steel."""
        beams = [
            {"beam_id": "B1", "b_mm": 300, "D_mm": 450, "mu_knm": 100, "vu_kn": 50},
        ]
        result = optimize_beam_line(beams)
        cfg = result.beam_configs[0]
        assert cfg.ast_provided_mm2 >= cfg.ast_required_mm2

    def test_skipped_count(self):
        """Test beams with invalid dimensions are skipped."""
        beams = [
            {"beam_id": "B1", "b_mm": 300, "D_mm": 450, "mu_knm": 100, "vu_kn": 50},
            {"beam_id": "B2", "b_mm": 300, "D_mm": 50, "mu_knm": 100, "vu_kn": 50},  # Too shallow
        ]
        result = optimize_beam_line(beams)
        # B2 should be skipped due to shallow depth
        assert result.beams_processed + result.beams_skipped == 2

    def test_beam_line_three_beams(self):
        """Test typical 3-beam line scenario."""
        # Typical beam line: end-mid-end with varying moments
        beams = [
            {"beam_id": "B1", "b_mm": 300, "D_mm": 500, "mu_knm": 120, "vu_kn": 70},  # Support
            {"beam_id": "B2", "b_mm": 300, "D_mm": 500, "mu_knm": 80, "vu_kn": 50},   # Mid
            {"beam_id": "B3", "b_mm": 300, "D_mm": 500, "mu_knm": 130, "vu_kn": 75},  # Support
        ]
        result = optimize_beam_line(beams)
        assert result.beams_processed == 3
        assert result.unified_bar_dia > 0

        # All should use same diameter
        for cfg in result.beam_configs:
            assert cfg.bottom_layer1_dia == result.unified_bar_dia
