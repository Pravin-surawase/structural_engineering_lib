"""
Simplified Integration Tests
=============================

End-to-end workflow tests using the actual API signatures.

Author: Agent 6
Phase: Test Enhancement
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.session_manager import BeamInputs, DesignResult, SessionStateManager
from utils.error_handler import validate_beam_inputs
from utils.validation import validate_dimension, validate_materials
from components.inputs import CONCRETE_GRADES, STEEL_GRADES, EXPOSURE_CONDITIONS


class TestSessionWorkflow:
    """Test complete session workflows."""

    def test_create_and_cache_design(self):
        """Test creating a design and caching it."""
        # Create inputs
        inputs = BeamInputs(
            span_mm=6000.0,
            b_mm=300.0,
            d_mm=410.0,
            D_mm=450.0,
            fck_mpa=25.0,
            fy_mpa=415.0,
            mu_knm=120.0,
            vu_kn=80.0,
        )

        # Create manager
        manager = SessionStateManager()
        manager.initialize()

        # Initially no cached result
        cached = manager.get_cached_design(inputs)
        assert cached is None

        # Create result
        result = DesignResult(
            inputs=inputs,
            ast_mm2=800.0,
            ast_provided_mm2=942.0,
            num_bars=3,
            bar_diameter_mm=20,
            stirrup_diameter_mm=8,
            stirrup_spacing_mm=200,
            utilization_pct=85.0,
            status="PASS",
            compliance_checks={"flexure": True, "shear": True},
            cost_per_meter=150.0,
        )

        # Cache it
        manager.cache_design(inputs, result)

        # Retrieve it
        retrieved = manager.get_cached_design(inputs)
        assert retrieved is not None
        assert retrieved.ast_mm2 == 800.0
        assert retrieved.status == "PASS"

    def test_multiple_designs_cached_independently(self):
        """Test that different designs are cached separately."""
        manager = SessionStateManager()
        manager.initialize()

        # Design 1
        inputs1 = BeamInputs(b_mm=300.0, d_mm=400.0)
        result1 = DesignResult(
            inputs=inputs1,
            ast_mm2=800.0,
            ast_provided_mm2=900.0,
            num_bars=3,
            bar_diameter_mm=20,
            stirrup_diameter_mm=8,
            stirrup_spacing_mm=200,
            utilization_pct=85.0,
            status="PASS",
            compliance_checks={},
            cost_per_meter=150.0,
        )
        manager.cache_design(inputs1, result1)

        # Design 2
        inputs2 = BeamInputs(b_mm=350.0, d_mm=450.0)
        result2 = DesignResult(
            inputs=inputs2,
            ast_mm2=900.0,
            ast_provided_mm2=1000.0,
            num_bars=4,
            bar_diameter_mm=20,
            stirrup_diameter_mm=8,
            stirrup_spacing_mm=180,
            utilization_pct=90.0,
            status="PASS",
            compliance_checks={},
            cost_per_meter=180.0,
        )
        manager.cache_design(inputs2, result2)

        # Retrieve both
        retrieved1 = manager.get_cached_design(inputs1)
        retrieved2 = manager.get_cached_design(inputs2)

        assert retrieved1.ast_mm2 == 800.0
        assert retrieved2.ast_mm2 == 900.0


class TestValidationWorkflow:
    """Test validation workflows."""

    def test_valid_beam_passes_all_checks(self):
        """Test that a valid beam passes all validation checks."""
        errors = validate_beam_inputs(
            span_mm=6000.0,
            b_mm=300.0,
            d_mm=410.0,
            D_mm=450.0,
            fck_mpa=25.0,
            fy_mpa=415.0,
            mu_knm=120.0,
            vu_kn=80.0,
        )
        assert len(errors) == 0, "Valid beam should pass all checks"

    def test_small_dimensions_detected(self):
        """Test that too-small dimensions are detected."""
        errors = validate_beam_inputs(
            span_mm=800.0,  # Too small (min 1000)
            b_mm=100.0,  # Too small (min 150)
            d_mm=150.0,  # Too small (min 200)
            D_mm=200.0,  # Too small (min 250)
            fck_mpa=25.0,
            fy_mpa=415.0,
            mu_knm=120.0,
            vu_kn=80.0,
        )
        assert len(errors) > 0, "Too-small dimensions should be detected"

    def test_large_dimensions_detected(self):
        """Test that too-large dimensions are detected."""
        errors = validate_beam_inputs(
            span_mm=20000.0,  # Too large (max 15000)
            b_mm=1200.0,  # Too large (max 1000)
            d_mm=2500.0,  # Too large (max 2000)
            D_mm=3000.0,  # Too large (max 2500)
            fck_mpa=25.0,
            fy_mpa=415.0,
            mu_knm=120.0,
            vu_kn=80.0,
        )
        assert len(errors) > 0, "Too-large dimensions should be detected"

    def test_invalid_materials_detected(self):
        """Test that invalid materials are detected."""
        errors = validate_beam_inputs(
            span_mm=6000.0,
            b_mm=300.0,
            d_mm=410.0,
            D_mm=450.0,
            fck_mpa=99.0,  # Invalid
            fy_mpa=999.0,  # Invalid
            mu_knm=120.0,
            vu_kn=80.0,
        )
        assert len(errors) > 0, "Invalid materials should be detected"

    def test_excessive_loads_detected(self):
        """Test that excessive loads are detected."""
        errors = validate_beam_inputs(
            span_mm=6000.0,
            b_mm=300.0,
            d_mm=410.0,
            D_mm=450.0,
            fck_mpa=25.0,
            fy_mpa=415.0,
            mu_knm=6000.0,  # Too large (max 5000)
            vu_kn=4000.0,  # Too large (max 3000)
        )
        assert len(errors) > 0, "Excessive loads should be detected"

    def test_depth_relationship_validated(self):
        """Test that d must be less than D."""
        errors = validate_beam_inputs(
            span_mm=6000.0,
            b_mm=300.0,
            d_mm=450.0,  # Greater than D!
            D_mm=400.0,
            fck_mpa=25.0,
            fy_mpa=415.0,
            mu_knm=120.0,
            vu_kn=80.0,
        )
        assert len(errors) > 0, "d >= D should be detected"


class TestDimensionValidation:
    """Test dimension validation helpers."""

    def test_dimension_in_range(self):
        """Test dimension within valid range."""
        is_valid, msg = validate_dimension(500.0, 100.0, 1000.0, "Width")
        assert is_valid
        assert msg == ""

    def test_dimension_below_min(self):
        """Test dimension below minimum."""
        is_valid, msg = validate_dimension(50.0, 100.0, 1000.0, "Width")
        assert not is_valid
        assert "Width" in msg

    def test_dimension_above_max(self):
        """Test dimension above maximum."""
        is_valid, msg = validate_dimension(1500.0, 100.0, 1000.0, "Width")
        assert not is_valid
        assert "Width" in msg

    def test_dimension_at_boundaries(self):
        """Test dimension at exact boundaries."""
        # At minimum
        is_valid, msg = validate_dimension(100.0, 100.0, 1000.0, "Width")
        assert is_valid

        # At maximum
        is_valid, msg = validate_dimension(1000.0, 100.0, 1000.0, "Width")
        assert is_valid


class TestMaterialValidation:
    """Test material validation helpers."""

    def test_valid_material_combinations(self):
        """Test various valid material combinations."""
        test_cases = [
            (20.0, 415.0),  # M20 + Fe415
            (25.0, 500.0),  # M25 + Fe500
            (30.0, 415.0),  # M30 + Fe415
            (40.0, 550.0),  # M40 + Fe550
        ]

        for fck, fy in test_cases:
            is_valid, msg = validate_materials(fck, fy)
            # Currently returns True for all (TODO in implementation)
            assert is_valid


class TestDataStructures:
    """Test data classes and structures."""

    def test_beam_inputs_defaults(self):
        """Test BeamInputs default values."""
        inputs = BeamInputs()
        assert inputs.span_mm == 5000.0
        assert inputs.b_mm == 300.0
        assert inputs.d_mm == 450.0
        assert inputs.D_mm == 500.0
        assert inputs.fck_mpa == 25.0
        assert inputs.fy_mpa == 500.0
        assert inputs.mu_knm == 120.0
        assert inputs.vu_kn == 80.0
        assert inputs.cover_mm == 30.0
        assert inputs.timestamp != ""

    def test_beam_inputs_to_dict(self):
        """Test BeamInputs serialization."""
        inputs = BeamInputs(b_mm=400.0, d_mm=500.0)
        data = inputs.to_dict()
        assert isinstance(data, dict)
        assert data["b_mm"] == 400.0
        assert data["d_mm"] == 500.0

    def test_beam_inputs_from_dict(self):
        """Test BeamInputs deserialization."""
        data = {
            "span_mm": 7000.0,
            "b_mm": 350.0,
            "d_mm": 450.0,
            "D_mm": 500.0,
            "fck_mpa": 30.0,
            "fy_mpa": 415.0,
            "mu_knm": 150.0,
            "vu_kn": 100.0,
            "cover_mm": 40.0,
            "timestamp": "2024-01-01T12:00:00",
        }
        inputs = BeamInputs.from_dict(data)
        assert inputs.span_mm == 7000.0
        assert inputs.b_mm == 350.0
        assert inputs.fck_mpa == 30.0

    def test_design_result_creation(self):
        """Test DesignResult creation."""
        inputs = BeamInputs()
        result = DesignResult(
            inputs=inputs,
            ast_mm2=1000.0,
            ast_provided_mm2=1100.0,
            num_bars=4,
            bar_diameter_mm=20,
            stirrup_diameter_mm=8,
            stirrup_spacing_mm=200,
            utilization_pct=90.0,
            status="PASS",
            compliance_checks={"flexure": True},
            cost_per_meter=200.0,
        )
        assert result.ast_mm2 == 1000.0
        assert result.status == "PASS"
        assert result.timestamp != ""


class TestComponentData:
    """Test component data structures."""

    def test_concrete_grades_available(self):
        """Test that concrete grades dictionary exists and has data."""
        assert isinstance(CONCRETE_GRADES, dict)
        assert len(CONCRETE_GRADES) > 0
        assert "M20" in CONCRETE_GRADES
        assert "M25" in CONCRETE_GRADES

    def test_steel_grades_available(self):
        """Test that steel grades dictionary exists and has data."""
        assert isinstance(STEEL_GRADES, dict)
        assert len(STEEL_GRADES) > 0
        assert "Fe415" in STEEL_GRADES
        assert "Fe500" in STEEL_GRADES

    def test_exposure_conditions_available(self):
        """Test that exposure conditions exist."""
        assert isinstance(EXPOSURE_CONDITIONS, dict)
        assert len(EXPOSURE_CONDITIONS) > 0

    def test_concrete_grade_properties(self):
        """Test that concrete grades have required properties."""
        for grade, props in CONCRETE_GRADES.items():
            assert "fck" in props, f"{grade} missing fck"
            assert "cost_factor" in props, f"{grade} missing cost_factor"

    def test_steel_grade_properties(self):
        """Test that steel grades have required properties."""
        for grade, props in STEEL_GRADES.items():
            assert "fy" in props, f"{grade} missing fy"
            assert "cost_factor" in props, f"{grade} missing cost_factor"


class TestPerformance:
    """Test performance characteristics."""

    def test_hash_generation_fast(self):
        """Test that hash generation is fast."""
        import time

        manager = SessionStateManager()
        inputs = BeamInputs()

        start = time.time()
        for _ in range(100):
            manager._input_hash(inputs)  # Use private method for testing
        duration = time.time() - start

        assert duration < 1.0, f"100 hashes took {duration}s, should be < 1s"

    def test_validation_fast(self):
        """Test that validation is fast."""
        import time

        start = time.time()
        for _ in range(100):
            validate_beam_inputs(
                span_mm=6000.0,
                b_mm=300.0,
                d_mm=410.0,
                D_mm=450.0,
                fck_mpa=25.0,
                fy_mpa=415.0,
                mu_knm=120.0,
                vu_kn=80.0,
            )
        duration = time.time() - start

        assert duration < 1.0, f"100 validations took {duration}s, should be < 1s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
