# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tests for the inputs module (TASK-276: Input Flexibility).

Tests cover:
- BeamGeometryInput validation and properties
- MaterialsInput factory methods and validation
- LoadsInput and LoadCaseInput validation
- DetailingConfigInput presets
- BeamInput complete workflow
- JSON import/export round-trips
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from structural_lib.inputs import (
    BeamGeometryInput,
    BeamInput,
    DetailingConfigInput,
    LoadCaseInput,
    LoadsInput,
    MaterialsInput,
    from_dict,
    from_json,
    from_json_file,
)


class TestBeamGeometryInput:
    """Tests for BeamGeometryInput dataclass."""

    def test_basic_creation(self) -> None:
        """Test basic geometry creation."""
        geom = BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000)

        assert geom.b_mm == 300
        assert geom.D_mm == 500
        assert geom.span_mm == 5000
        assert geom.cover_mm == 40  # Default

    def test_effective_depth_auto_calculation(self) -> None:
        """Test effective depth is calculated from D - cover."""
        geom = BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000, cover_mm=40)

        assert geom.effective_depth == 460  # 500 - 40

    def test_effective_depth_explicit(self) -> None:
        """Test explicit effective depth is used."""
        geom = BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000, d_mm=450)

        assert geom.effective_depth == 450  # Explicit

    def test_span_depth_ratio(self) -> None:
        """Test L/d ratio calculation."""
        geom = BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000, d_mm=450)

        assert abs(geom.span_depth_ratio - 11.11) < 0.1  # 5000/450

    def test_validation_negative_width(self) -> None:
        """Test that negative width raises ValueError."""
        with pytest.raises(ValueError, match="width must be positive"):
            BeamGeometryInput(b_mm=-300, D_mm=500, span_mm=5000)

    def test_validation_zero_depth(self) -> None:
        """Test that zero depth raises ValueError."""
        with pytest.raises(ValueError, match="depth must be positive"):
            BeamGeometryInput(b_mm=300, D_mm=0, span_mm=5000)

    def test_validation_effective_depth_exceeds_overall(self) -> None:
        """Test that d > D raises ValueError."""
        with pytest.raises(ValueError, match="must be less than overall depth"):
            BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000, d_mm=600)

    def test_immutability(self) -> None:
        """Test that frozen=True prevents mutation."""
        geom = BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000)

        with pytest.raises(AttributeError):
            geom.b_mm = 400  # type: ignore

    def test_to_dict(self) -> None:
        """Test dictionary conversion."""
        geom = BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000)
        d = geom.to_dict()

        assert d["b_mm"] == 300
        assert d["D_mm"] == 500
        assert d["span_mm"] == 5000

    def test_from_dict_canonical(self) -> None:
        """Test creation from canonical keys."""
        data = {"b_mm": 300, "D_mm": 500, "span_mm": 5000}
        geom = BeamGeometryInput.from_dict(data)

        assert geom.b_mm == 300
        assert geom.D_mm == 500

    def test_from_dict_legacy(self) -> None:
        """Test creation from legacy keys (b, D, span)."""
        data = {"b": 300, "D": 500, "span": 5000}
        geom = BeamGeometryInput.from_dict(data)

        assert geom.b_mm == 300
        assert geom.D_mm == 500


class TestMaterialsInput:
    """Tests for MaterialsInput dataclass."""

    def test_basic_creation(self) -> None:
        """Test basic materials creation."""
        mat = MaterialsInput(fck_nmm2=25, fy_nmm2=500)

        assert mat.fck_nmm2 == 25
        assert mat.fy_nmm2 == 500
        assert mat.es_nmm2 == 200000  # Default

    def test_concrete_grade_property(self) -> None:
        """Test concrete grade string."""
        mat = MaterialsInput(fck_nmm2=25, fy_nmm2=500)

        assert mat.concrete_grade == "M25"

    def test_steel_grade_property(self) -> None:
        """Test steel grade string."""
        mat = MaterialsInput(fck_nmm2=25, fy_nmm2=500)

        assert mat.steel_grade == "Fe 500"

    def test_factory_m25_fe500(self) -> None:
        """Test M25/Fe500 factory method."""
        mat = MaterialsInput.m25_fe500()

        assert mat.fck_nmm2 == 25
        assert mat.fy_nmm2 == 500

    def test_factory_m30_fe500(self) -> None:
        """Test M30/Fe500 factory method."""
        mat = MaterialsInput.m30_fe500()

        assert mat.fck_nmm2 == 30
        assert mat.fy_nmm2 == 500

    def test_factory_m20_fe415(self) -> None:
        """Test M20/Fe415 factory method."""
        mat = MaterialsInput.m20_fe415()

        assert mat.fck_nmm2 == 20
        assert mat.fy_nmm2 == 415

    def test_validation_negative_fck(self) -> None:
        """Test that negative fck raises ValueError."""
        with pytest.raises(ValueError, match="fck must be positive"):
            MaterialsInput(fck_nmm2=-25, fy_nmm2=500)

    def test_from_dict_legacy_keys(self) -> None:
        """Test creation from legacy keys (fck, fy)."""
        data = {"fck": 30, "fy": 415}
        mat = MaterialsInput.from_dict(data)

        assert mat.fck_nmm2 == 30
        assert mat.fy_nmm2 == 415


class TestLoadsInput:
    """Tests for LoadsInput dataclass."""

    def test_basic_creation(self) -> None:
        """Test basic loads creation."""
        loads = LoadsInput(mu_knm=150, vu_kn=80)

        assert loads.mu_knm == 150
        assert loads.vu_kn == 80
        assert loads.case_id == "CASE-1"

    def test_with_case_id(self) -> None:
        """Test loads with custom case ID."""
        loads = LoadsInput(mu_knm=150, vu_kn=80, case_id="1.5DL+1.5LL")

        assert loads.case_id == "1.5DL+1.5LL"

    def test_validation_negative_moment(self) -> None:
        """Test that negative moment raises ValueError."""
        with pytest.raises(ValueError, match="Moment cannot be negative"):
            LoadsInput(mu_knm=-150, vu_kn=80)

    def test_from_dict_legacy_keys(self) -> None:
        """Test creation from legacy keys (Mu, Vu)."""
        data = {"Mu": 150, "Vu": 80}
        loads = LoadsInput.from_dict(data)

        assert loads.mu_knm == 150
        assert loads.vu_kn == 80


class TestLoadCaseInput:
    """Tests for LoadCaseInput dataclass."""

    def test_basic_creation(self) -> None:
        """Test load case creation."""
        case = LoadCaseInput("1.5DL+1.5LL", mu_knm=120, vu_kn=85)

        assert case.case_id == "1.5DL+1.5LL"
        assert case.mu_knm == 120
        assert case.vu_kn == 85

    def test_validation_empty_case_id(self) -> None:
        """Test that empty case_id raises ValueError."""
        with pytest.raises(ValueError, match="case_id cannot be empty"):
            LoadCaseInput("", mu_knm=120, vu_kn=85)


class TestDetailingConfigInput:
    """Tests for DetailingConfigInput dataclass."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = DetailingConfigInput()

        assert config.stirrup_dia_mm == 8.0
        assert config.stirrup_spacing_start_mm == 150.0
        assert config.stirrup_spacing_mid_mm == 200.0
        assert config.is_seismic is False

    def test_seismic_preset(self) -> None:
        """Test seismic configuration preset."""
        config = DetailingConfigInput.seismic(zone=3)

        assert config.is_seismic is True
        assert config.stirrup_spacing_start_mm == 125.0

    def test_seismic_zone_4_stricter(self) -> None:
        """Test that zone 4 has stricter requirements."""
        config = DetailingConfigInput.seismic(zone=4)

        assert config.stirrup_dia_mm == 10.0
        assert config.stirrup_spacing_start_mm == 100.0

    def test_gravity_only_preset(self) -> None:
        """Test gravity-only configuration preset."""
        config = DetailingConfigInput.gravity_only()

        assert config.is_seismic is False


class TestBeamInput:
    """Tests for BeamInput complete workflow."""

    def test_simple_creation(self) -> None:
        """Test simple beam input creation."""
        beam = BeamInput(
            beam_id="B1",
            story="GF",
            geometry=BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000),
            materials=MaterialsInput.m25_fe500(),
            loads=LoadsInput(mu_knm=150, vu_kn=80),
        )

        assert beam.beam_id == "B1"
        assert beam.story == "GF"
        assert beam.geometry.b_mm == 300
        assert beam.materials.fck_nmm2 == 25
        assert beam.loads is not None
        assert beam.loads.mu_knm == 150

    def test_multi_case_creation(self) -> None:
        """Test beam with multiple load cases."""
        beam = BeamInput(
            beam_id="B2",
            story="1F",
            geometry=BeamGeometryInput(b_mm=300, D_mm=600, span_mm=6000),
            materials=MaterialsInput.m30_fe500(),
            load_cases=[
                LoadCaseInput("1.5DL+1.5LL", mu_knm=200, vu_kn=100),
                LoadCaseInput("1.2DL+1.6LL", mu_knm=220, vu_kn=110),
            ],
        )

        assert beam.has_multiple_cases is True
        assert len(beam.load_cases) == 2
        assert beam.governing_moment == 220

    def test_validation_no_loads(self) -> None:
        """Test that missing loads raises ValueError."""
        with pytest.raises(ValueError, match="must be provided"):
            BeamInput(
                beam_id="B1",
                story="GF",
                geometry=BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000),
                materials=MaterialsInput.m25_fe500(),
                # No loads or load_cases
            )

    def test_governing_moment_single_case(self) -> None:
        """Test governing moment with single load."""
        beam = BeamInput(
            beam_id="B1",
            story="GF",
            geometry=BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000),
            materials=MaterialsInput.m25_fe500(),
            loads=LoadsInput(mu_knm=150, vu_kn=80),
        )

        assert beam.governing_moment == 150
        assert beam.governing_shear == 80

    def test_to_dict(self) -> None:
        """Test dictionary conversion."""
        beam = BeamInput(
            beam_id="B1",
            story="GF",
            geometry=BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000),
            materials=MaterialsInput.m25_fe500(),
            loads=LoadsInput(mu_knm=150, vu_kn=80),
        )

        d = beam.to_dict()

        assert d["beam_id"] == "B1"
        assert d["geometry"]["b_mm"] == 300
        assert d["materials"]["fck_nmm2"] == 25
        assert d["loads"]["mu_knm"] == 150

    def test_to_json_and_back(self) -> None:
        """Test JSON round-trip."""
        original = BeamInput(
            beam_id="B1",
            story="GF",
            geometry=BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000),
            materials=MaterialsInput.m25_fe500(),
            loads=LoadsInput(mu_knm=150, vu_kn=80),
        )

        json_str = original.to_json()
        restored = BeamInput.from_json(json_str)

        assert restored.beam_id == original.beam_id
        assert restored.geometry.b_mm == original.geometry.b_mm
        assert restored.materials.fck_nmm2 == original.materials.fck_nmm2
        assert restored.loads is not None
        assert restored.loads.mu_knm == original.loads.mu_knm  # type: ignore

    def test_json_file_round_trip(self) -> None:
        """Test JSON file round-trip."""
        original = BeamInput(
            beam_id="B1",
            story="GF",
            geometry=BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000),
            materials=MaterialsInput.m25_fe500(),
            loads=LoadsInput(mu_knm=150, vu_kn=80),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "beam.json"
            original.to_json_file(path)

            restored = BeamInput.from_json_file(path)

            assert restored.beam_id == original.beam_id
            assert restored.geometry.b_mm == original.geometry.b_mm

    def test_from_dict_flat_format(self) -> None:
        """Test creation from flat dictionary format."""
        data = {
            "beam_id": "B1",
            "story": "GF",
            "b_mm": 300,
            "D_mm": 500,
            "span_mm": 5000,
            "fck_nmm2": 25,
            "fy_nmm2": 500,
            "mu_knm": 150,
            "vu_kn": 80,
        }

        beam = BeamInput.from_dict(data)

        assert beam.beam_id == "B1"
        assert beam.geometry.b_mm == 300
        assert beam.materials.fck_nmm2 == 25
        assert beam.loads is not None
        assert beam.loads.mu_knm == 150


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_from_dict_function(self) -> None:
        """Test from_dict convenience function."""
        data = {
            "beam_id": "B1",
            "story": "GF",
            "geometry": {"b_mm": 300, "D_mm": 500, "span_mm": 5000},
            "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
            "loads": {"mu_knm": 150, "vu_kn": 80},
        }

        beam = from_dict(data)

        assert beam.beam_id == "B1"

    def test_from_json_function(self) -> None:
        """Test from_json convenience function."""
        json_str = json.dumps(
            {
                "beam_id": "B1",
                "story": "GF",
                "geometry": {"b_mm": 300, "D_mm": 500, "span_mm": 5000},
                "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
                "loads": {"mu_knm": 150, "vu_kn": 80},
            }
        )

        beam = from_json(json_str)

        assert beam.beam_id == "B1"

    def test_from_json_file_function(self) -> None:
        """Test from_json_file convenience function."""
        data = {
            "beam_id": "B1",
            "story": "GF",
            "geometry": {"b_mm": 300, "D_mm": 500, "span_mm": 5000},
            "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
            "loads": {"mu_knm": 150, "vu_kn": 80},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "beam.json"
            path.write_text(json.dumps(data), encoding="utf-8")

            beam = from_json_file(path)

            assert beam.beam_id == "B1"
