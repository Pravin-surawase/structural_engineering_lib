# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tests for the testing_strategies module (TASK-279).

Tests cover:
- ToleranceSpec and numerical comparisons
- BoundaryValueGenerator for edge case testing
- PropertyBasedTester for random case generation
- Engineering invariants checking
- Regression testing utilities
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from structural_lib.testing_strategies import (
    AREA_TOLERANCE,
    FORCE_TOLERANCE,
    LENGTH_TOLERANCE,
    RATIO_TOLERANCE,
    STRESS_TOLERANCE,
    BeamDesignInvariants,
    BeamParameterRanges,
    BoundaryValueGenerator,
    InvariantCheck,
    PropertyBasedTester,
    RandomTestCase,
    RegressionBaseline,
    RegressionTestSuite,
    ToleranceSpec,
    assert_beam_design_valid,
    create_test_case_id,
)

# =============================================================================
# Test ToleranceSpec
# =============================================================================


class TestToleranceSpec:
    """Tests for ToleranceSpec class."""

    def test_default_values(self):
        """Test default tolerance values."""
        tol = ToleranceSpec()
        assert tol.relative == 0.001
        assert tol.absolute == 0.1

    def test_custom_values(self):
        """Test custom tolerance values."""
        tol = ToleranceSpec(relative=0.01, absolute=0.5, description="custom")
        assert tol.relative == 0.01
        assert tol.absolute == 0.5
        assert tol.description == "custom"

    def test_is_close_exact_match(self):
        """Test is_close with exact match."""
        tol = ToleranceSpec()
        assert tol.is_close(100.0, 100.0) is True

    def test_is_close_within_relative(self):
        """Test is_close within relative tolerance."""
        tol = ToleranceSpec(relative=0.01, absolute=0)
        # 0.5% difference should pass 1% tolerance
        assert tol.is_close(100.5, 100.0) is True
        # 2% difference should fail 1% tolerance
        assert tol.is_close(102.0, 100.0) is False

    def test_is_close_within_absolute(self):
        """Test is_close within absolute tolerance."""
        tol = ToleranceSpec(relative=0, absolute=0.5)
        # 0.3 difference should pass 0.5 tolerance
        assert tol.is_close(100.3, 100.0) is True
        # 0.6 difference should fail 0.5 tolerance
        assert tol.is_close(100.6, 100.0) is False

    def test_is_close_combined(self):
        """Test is_close with combined tolerance."""
        tol = ToleranceSpec(relative=0.001, absolute=0.1)
        # For expected=100, threshold = 0.1 + 0.001*100 = 0.2
        assert tol.is_close(100.15, 100.0) is True
        assert tol.is_close(100.3, 100.0) is False

    def test_assert_close_pass(self):
        """Test assert_close when values match."""
        tol = ToleranceSpec(relative=0.01, absolute=0.1)
        # Should not raise
        tol.assert_close(100.5, 100.0, "test value")

    def test_assert_close_fail(self):
        """Test assert_close when values don't match."""
        tol = ToleranceSpec(relative=0.001, absolute=0.01)
        with pytest.raises(AssertionError) as exc_info:
            tol.assert_close(102.0, 100.0, "test value")

        error_msg = str(exc_info.value)
        assert "test value" in error_msg
        assert "Expected: 100" in error_msg
        assert "102.000000" in error_msg  # Actual value is formatted with decimals


class TestPredefinedTolerances:
    """Test predefined tolerance constants."""

    def test_area_tolerance(self):
        """Test area tolerance (0.1%, 1.0 mm²)."""
        assert AREA_TOLERANCE.relative == 0.001
        assert AREA_TOLERANCE.absolute == 1.0
        assert AREA_TOLERANCE.description == "mm²"

    def test_length_tolerance(self):
        """Test length tolerance (0.1%, 0.1 mm)."""
        assert LENGTH_TOLERANCE.relative == 0.001
        assert LENGTH_TOLERANCE.absolute == 0.1
        assert LENGTH_TOLERANCE.description == "mm"

    def test_force_tolerance(self):
        """Test force tolerance (0.1%, 0.01 kN)."""
        assert FORCE_TOLERANCE.relative == 0.001
        assert FORCE_TOLERANCE.absolute == 0.01
        assert FORCE_TOLERANCE.description == "kN"

    def test_stress_tolerance(self):
        """Test stress tolerance (1%, 0.1 N/mm²)."""
        assert STRESS_TOLERANCE.relative == 0.01
        assert STRESS_TOLERANCE.absolute == 0.1
        assert STRESS_TOLERANCE.description == "N/mm²"

    def test_ratio_tolerance(self):
        """Test ratio tolerance (0.1%, 0.0001)."""
        assert RATIO_TOLERANCE.relative == 0.001
        assert RATIO_TOLERANCE.absolute == 0.0001
        assert RATIO_TOLERANCE.description == "ratio"


# =============================================================================
# Test BoundaryValueGenerator
# =============================================================================


class TestBoundaryValueGenerator:
    """Tests for BoundaryValueGenerator class."""

    def test_basic_generation(self):
        """Test basic boundary value generation."""
        gen = BoundaryValueGenerator(min_val=100, max_val=200)
        values = gen.generate()

        assert len(values) == 5
        assert values[0] == 100  # Minimum
        assert values[-1] == 200  # Maximum
        assert values[2] == 150  # Midpoint (typical)

    def test_custom_typical(self):
        """Test with custom typical value."""
        gen = BoundaryValueGenerator(min_val=100, max_val=200, typical_val=120)
        values = gen.generate()

        assert values[2] == 120  # Custom typical

    def test_boundary_values(self):
        """Test that near-boundary values are included."""
        gen = BoundaryValueGenerator(min_val=0, max_val=100, epsilon=1.0)
        values = gen.generate()

        assert values[1] == 1.0  # Just above minimum
        assert values[3] == 99.0  # Just below maximum

    def test_include_invalid(self):
        """Test with invalid values included."""
        gen = BoundaryValueGenerator(
            min_val=100, max_val=200, epsilon=1.0, include_invalid=True
        )
        values = gen.generate()

        assert len(values) == 7
        assert values[0] == 99.0  # Below minimum
        assert values[-1] == 201.0  # Above maximum

    def test_auto_epsilon(self):
        """Test automatic epsilon calculation."""
        gen = BoundaryValueGenerator(min_val=0, max_val=1000)
        # Epsilon should be 0.1% of range = 1.0
        assert gen.epsilon == pytest.approx(1.0)


class TestBeamParameterRanges:
    """Tests for BeamParameterRanges class."""

    def test_default_ranges(self):
        """Test default parameter ranges."""
        ranges = BeamParameterRanges()
        assert ranges.b_min == 200.0
        assert ranges.b_max == 600.0
        assert ranges.fck_min == 20.0
        assert ranges.fck_max == 50.0

    def test_get_boundary_generator(self):
        """Test getting boundary generator for parameter."""
        ranges = BeamParameterRanges()

        gen = ranges.get_boundary_generator("b")
        assert gen.min_val == 200.0
        assert gen.max_val == 600.0
        assert gen.typical_val == 300.0

    def test_get_boundary_generator_fck(self):
        """Test boundary generator for concrete grade."""
        ranges = BeamParameterRanges()

        gen = ranges.get_boundary_generator("fck")
        values = gen.generate()
        assert 20.0 in values
        assert 50.0 in values
        assert 25.0 in values  # Typical

    def test_unknown_parameter_raises(self):
        """Test that unknown parameter raises error."""
        ranges = BeamParameterRanges()

        with pytest.raises(ValueError, match="Unknown parameter"):
            ranges.get_boundary_generator("unknown")


# =============================================================================
# Test PropertyBasedTester
# =============================================================================


class TestPropertyBasedTester:
    """Tests for PropertyBasedTester class."""

    def test_reproducible_with_seed(self):
        """Test that same seed produces same cases."""
        tester1 = PropertyBasedTester(seed=42)
        tester2 = PropertyBasedTester(seed=42)

        cases1 = tester1.generate_beam_cases(n=10)
        cases2 = tester2.generate_beam_cases(n=10)

        for c1, c2 in zip(cases1, cases2, strict=False):
            assert c1.inputs == c2.inputs

    def test_different_seeds_different_cases(self):
        """Test that different seeds produce different cases."""
        tester1 = PropertyBasedTester(seed=42)
        tester2 = PropertyBasedTester(seed=123)

        cases1 = tester1.generate_beam_cases(n=10)
        cases2 = tester2.generate_beam_cases(n=10)

        # At least some should differ
        different = sum(
            c1.inputs != c2.inputs for c1, c2 in zip(cases1, cases2, strict=False)
        )
        assert different > 0

    def test_generate_beam_cases_count(self):
        """Test generating specified number of cases."""
        tester = PropertyBasedTester(seed=42)
        cases = tester.generate_beam_cases(n=50)
        assert len(cases) == 50

    def test_generated_cases_have_required_keys(self):
        """Test that generated cases have all required input keys."""
        tester = PropertyBasedTester(seed=42)
        cases = tester.generate_beam_cases(n=10)

        required_keys = {
            "b_mm",
            "D_mm",
            "d_mm",
            "cover_mm",
            "fck_nmm2",
            "fy_nmm2",
            "mu_knm",
            "vu_kn",
        }

        for case in cases:
            assert required_keys.issubset(case.inputs.keys())

    def test_generated_values_within_ranges(self):
        """Test that generated values are within parameter ranges."""
        tester = PropertyBasedTester(seed=42)
        ranges = BeamParameterRanges()
        cases = tester.generate_beam_cases(n=100, ranges=ranges)

        for case in cases:
            inputs = case.inputs
            assert ranges.b_min <= inputs["b_mm"] <= ranges.b_max
            assert ranges.fck_min <= inputs["fck_nmm2"] <= ranges.fck_max
            assert ranges.fy_min <= inputs["fy_nmm2"] <= ranges.fy_max
            assert ranges.mu_min <= inputs["mu_knm"] <= ranges.mu_max

    def test_reset_with_seed(self):
        """Test resetting with new seed."""
        tester = PropertyBasedTester(seed=42)
        cases1 = tester.generate_beam_cases(n=5)

        tester.reset(seed=42)
        cases2 = tester.generate_beam_cases(n=5)

        for c1, c2 in zip(cases1, cases2, strict=False):
            assert c1.inputs == c2.inputs

    def test_case_has_expected_properties(self):
        """Test that cases have expected properties list."""
        tester = PropertyBasedTester(seed=42)
        cases = tester.generate_beam_cases(n=5)

        for case in cases:
            assert len(case.expected_properties) > 0
            assert "ast_provided >= ast_required" in case.expected_properties


# =============================================================================
# Test Engineering Invariants
# =============================================================================


class TestInvariantCheck:
    """Tests for InvariantCheck class."""

    def test_passing_invariant(self):
        """Test invariant that passes."""
        inv = InvariantCheck(
            name="positive_value",
            description="Value must be positive",
            check_fn=lambda r: r > 0,
        )
        passed, msg = inv.check(10)
        assert passed is True
        assert "positive_value" in msg

    def test_failing_invariant(self):
        """Test invariant that fails."""
        inv = InvariantCheck(
            name="positive_value",
            description="Value must be positive",
            check_fn=lambda r: r > 0,
        )
        passed, msg = inv.check(-5)
        assert passed is False
        assert "positive_value" in msg
        assert "must be positive" in msg

    def test_invariant_with_exception(self):
        """Test invariant that raises exception."""
        inv = InvariantCheck(
            name="will_fail",
            description="Will raise error",
            check_fn=lambda r: r.nonexistent_attribute,
        )
        passed, msg = inv.check({})
        assert passed is False
        assert "Error" in msg


class TestBeamDesignInvariants:
    """Tests for BeamDesignInvariants class."""

    def test_get_all_returns_list(self):
        """Test that get_all returns list of invariants."""
        invariants = BeamDesignInvariants.get_all()
        assert isinstance(invariants, list)
        assert len(invariants) > 0
        assert all(isinstance(i, InvariantCheck) for i in invariants)

    def test_check_all_passing(self):
        """Test check_all with passing result."""
        # Create mock result that passes all invariants
        result = MagicMock()
        result.flexure.ast_provided = 1000
        result.flexure.ast_required = 800
        result.flexure.ast_min = 500
        result.flexure.ast_max = 2000
        result.shear.is_ok = True
        result.shear.vn_kn = 150
        result.shear.vu_kn = 100
        result.detailing.main_bar_dia = 16
        result.detailing.stirrup_dia = 8

        results = BeamDesignInvariants.check_all(result)
        assert len(results) > 0
        # All should pass (or be skipped for missing attrs)
        failures = [msg for passed, msg in results if not passed]
        assert len(failures) == 0

    def test_check_all_failing(self):
        """Test check_all with failing invariant."""
        # Create mock result that fails ast_provided >= ast_required
        result = MagicMock()
        result.flexure.ast_provided = 500
        result.flexure.ast_required = 800  # More than provided - FAIL

        results = BeamDesignInvariants.check_all(result)
        failures = [msg for passed, msg in results if not passed]
        assert len(failures) > 0


class TestAssertBeamDesignValid:
    """Tests for assert_beam_design_valid function."""

    def test_valid_design_passes(self):
        """Test that valid design doesn't raise."""
        result = MagicMock()
        result.flexure.ast_provided = 1000
        result.flexure.ast_required = 800
        result.flexure.ast_min = 500  # Add all attributes to avoid MagicMock comparison
        result.flexure.ast_max = 2000
        result.shear.is_ok = True
        result.shear.vn_kn = 150
        result.shear.vu_kn = 100
        result.detailing.main_bar_dia = 16
        result.detailing.stirrup_dia = 8

        # Should not raise
        assert_beam_design_valid(result)

    def test_invalid_design_raises(self):
        """Test that invalid design raises AssertionError."""
        result = MagicMock()
        result.flexure.ast_provided = 500
        result.flexure.ast_required = 800  # FAIL
        result.flexure.ast_min = 300  # Add to avoid MagicMock comparison errors
        result.flexure.ast_max = 2000
        result.shear.is_ok = True
        result.shear.vn_kn = 150
        result.shear.vu_kn = 100
        result.detailing.main_bar_dia = 16
        result.detailing.stirrup_dia = 8

        with pytest.raises(AssertionError, match="invariant violations"):
            assert_beam_design_valid(result)


# =============================================================================
# Test Regression Testing
# =============================================================================


class TestRegressionBaseline:
    """Tests for RegressionBaseline class."""

    def test_basic_creation(self):
        """Test basic baseline creation."""
        baseline = RegressionBaseline(
            version="0.16.0",
            inputs={"b_mm": 300, "D_mm": 500},
            outputs={"ast_required": 856},
        )
        assert baseline.version == "0.16.0"
        assert baseline.inputs["b_mm"] == 300
        assert len(baseline.hash) == 16

    def test_hash_deterministic(self):
        """Test that hash is deterministic."""
        b1 = RegressionBaseline(
            version="0.16.0",
            inputs={"b_mm": 300},
            outputs={"ast": 100},
        )
        b2 = RegressionBaseline(
            version="0.16.0",
            inputs={"b_mm": 300},
            outputs={"ast": 100},
        )
        assert b1.hash == b2.hash

    def test_to_dict(self):
        """Test serialization to dict."""
        baseline = RegressionBaseline(
            version="0.16.0",
            inputs={"b_mm": 300},
            outputs={"ast": 100},
        )
        data = baseline.to_dict()

        assert data["version"] == "0.16.0"
        assert data["inputs"]["b_mm"] == 300
        assert "hash" in data

    def test_from_dict(self):
        """Test deserialization from dict."""
        data = {
            "version": "0.16.0",
            "inputs": {"b_mm": 300},
            "outputs": {"ast": 100},
            "tolerances": {"ast": {"relative": 0.001, "absolute": 1.0}},
            "hash": "abc123",
        }
        baseline = RegressionBaseline.from_dict(data)

        assert baseline.version == "0.16.0"
        assert baseline.inputs["b_mm"] == 300
        assert "ast" in baseline.tolerances


class TestRegressionTestSuite:
    """Tests for RegressionTestSuite class."""

    def test_add_baseline(self):
        """Test adding a baseline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            suite = RegressionTestSuite(tmpdir)

            baseline = suite.add_baseline(
                name="test_case",
                inputs={"b_mm": 300},
                outputs={"ast": 100},
                version="0.16.0",
            )

            assert "test_case" in suite.baselines
            assert baseline.version == "0.16.0"

    def test_save_and_load(self):
        """Test saving and loading baselines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and save
            suite1 = RegressionTestSuite(tmpdir)
            suite1.add_baseline(
                name="case1",
                inputs={"b_mm": 300},
                outputs={"ast": 100},
            )
            suite1.save()

            # Verify file exists
            assert (Path(tmpdir) / "case1.json").exists()

            # Load in new suite
            suite2 = RegressionTestSuite(tmpdir)
            assert "case1" in suite2.baselines
            assert suite2.baselines["case1"].inputs["b_mm"] == 300

    def test_compare_matching(self):
        """Test comparison with matching values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            suite = RegressionTestSuite(tmpdir)
            suite.add_baseline(
                name="test",
                inputs={"b_mm": 300},
                outputs={"ast": 100.0, "is_ok": True},
            )

            results = suite.compare("test", {"ast": 100.05, "is_ok": True})

            # All should pass
            assert all(passed for _, passed, _ in results)

    def test_compare_failing(self):
        """Test comparison with failing values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            suite = RegressionTestSuite(tmpdir)
            suite.add_baseline(
                name="test",
                inputs={"b_mm": 300},
                outputs={"ast": 100.0},
            )

            results = suite.compare("test", {"ast": 200.0})  # Very different

            # Should fail
            ast_result = [r for r in results if r[0] == "ast"][0]
            assert ast_result[1] is False

    def test_compare_missing_output(self):
        """Test comparison with missing output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            suite = RegressionTestSuite(tmpdir)
            suite.add_baseline(
                name="test",
                inputs={"b_mm": 300},
                outputs={"ast": 100.0, "extra": 50.0},
            )

            results = suite.compare("test", {"ast": 100.0})  # Missing 'extra'

            # Should have failure for missing
            extra_result = [r for r in results if r[0] == "extra"][0]
            assert extra_result[1] is False
            assert "Missing" in extra_result[2]

    def test_compare_unknown_baseline_raises(self):
        """Test that comparing unknown baseline raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            suite = RegressionTestSuite(tmpdir)

            with pytest.raises(ValueError, match="not found"):
                suite.compare("nonexistent", {"ast": 100})


# =============================================================================
# Test Utilities
# =============================================================================


class TestCreateTestCaseId:
    """Tests for create_test_case_id function."""

    def test_deterministic(self):
        """Test that ID is deterministic."""
        inputs = {"b_mm": 300, "D_mm": 500}
        id1 = create_test_case_id(inputs)
        id2 = create_test_case_id(inputs)
        assert id1 == id2

    def test_format(self):
        """Test ID format."""
        id = create_test_case_id({"a": 1})
        assert id.startswith("TC-")
        assert len(id) == 11  # TC- + 8 hex chars

    def test_different_inputs_different_ids(self):
        """Test that different inputs give different IDs."""
        id1 = create_test_case_id({"a": 1})
        id2 = create_test_case_id({"a": 2})
        assert id1 != id2


class TestRandomTestCase:
    """Tests for RandomTestCase dataclass."""

    def test_basic_creation(self):
        """Test creating a random test case."""
        case = RandomTestCase(
            seed=42,
            inputs={"b_mm": 300},
            expected_properties=["positive_ast"],
        )
        assert case.seed == 42
        assert case.inputs["b_mm"] == 300
        assert "positive_ast" in case.expected_properties

    def test_default_properties(self):
        """Test default empty properties list."""
        case = RandomTestCase(seed=42, inputs={})
        assert case.expected_properties == []
