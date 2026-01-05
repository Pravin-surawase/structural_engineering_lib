import os
import sys
import unittest

# Add parent directory to path to import structural_lib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from structural_lib.costing import (
    CostProfile,
    calculate_concrete_cost,
    calculate_steel_cost,
    calculate_formwork_cost,
    calculate_total_beam_cost,
    STEEL_DENSITY_KG_PER_M3,
)


class TestCostProfile(unittest.TestCase):
    """Test CostProfile dataclass."""

    def test_default_cost_profile(self):
        """Test that default CostProfile has expected rates."""
        profile = CostProfile()

        # Check concrete rates
        self.assertEqual(profile.concrete_costs[20], 6200)
        self.assertEqual(profile.concrete_costs[25], 6700)
        self.assertEqual(profile.concrete_costs[30], 7200)

        # Check steel rates
        self.assertEqual(profile.steel_cost_per_kg, 72.0)

        # Check formwork rate
        self.assertEqual(profile.formwork_cost_per_m2, 500.0)

        # Check labor parameters
        self.assertEqual(profile.base_labor_rate_per_day, 800.0)
        self.assertEqual(profile.labor_productivity_m3_per_day, 5.0)

        # Check wastage factor
        self.assertEqual(profile.wastage_factor, 1.05)

    def test_custom_cost_profile(self):
        """Test creating custom CostProfile."""
        profile = CostProfile(
            concrete_costs={25: 7000.0},
            steel_cost_per_kg=70.0,
            formwork_cost_per_m2=550.0,
            base_labor_rate_per_day=1000.0,
            labor_productivity_m3_per_day=4.0,
            wastage_factor=1.10,
        )

        self.assertEqual(profile.concrete_costs[25], 7000.0)
        self.assertEqual(profile.steel_cost_per_kg, 70.0)
        self.assertEqual(profile.formwork_cost_per_m2, 550.0)
        self.assertEqual(profile.wastage_factor, 1.10)


class TestConcreteCost(unittest.TestCase):
    """Test calculate_concrete_cost function."""

    def setUp(self):
        self.profile = CostProfile()

    def test_basic_concrete_cost_m25(self):
        """Test concrete cost calculation for M25."""
        cost = calculate_concrete_cost(1.0, "M25", self.profile)
        expected = 6700.0 * 1.05  # Rate × wastage
        self.assertAlmostEqual(cost, expected, places=2)

    def test_basic_concrete_cost_m30(self):
        """Test concrete cost calculation for M30."""
        cost = calculate_concrete_cost(1.0, "M30", self.profile)
        expected = 7200.0 * 1.05
        self.assertAlmostEqual(cost, expected, places=2)

    def test_concrete_cost_with_volume(self):
        """Test concrete cost with different volume."""
        cost = calculate_concrete_cost(2.5, "M25", self.profile)
        expected = 6700.0 * 2.5 * 1.05
        self.assertAlmostEqual(cost, expected, places=2)

    def test_concrete_cost_unknown_grade_uses_default(self):
        """Test that unknown grade uses default rate."""
        cost = calculate_concrete_cost(1.0, "M99", self.profile)
        expected = 6700.0 * 1.05  # Default M25 rate
        self.assertAlmostEqual(cost, expected, places=2)

    def test_concrete_cost_zero_volume(self):
        """Test concrete cost with zero volume."""
        cost = calculate_concrete_cost(0.0, "M25", self.profile)
        self.assertEqual(cost, 0.0)

    def test_concrete_cost_negative_volume_raises_error(self):
        """Test that negative volume raises ValueError."""
        with self.assertRaises(ValueError):
            calculate_concrete_cost(-1.0, "M25", self.profile)


class TestSteelCost(unittest.TestCase):
    """Test calculate_steel_cost function."""

    def setUp(self):
        self.profile = CostProfile()

    def test_basic_steel_cost_fe415(self):
        """Test steel cost calculation for Fe415."""
        cost = calculate_steel_cost(100.0, "Fe415", self.profile)
        expected = 72.0 * 100.0 * 1.05  # Rate × weight × wastage
        self.assertAlmostEqual(cost, expected, places=2)

    def test_basic_steel_cost_fe500(self):
        """Test steel cost calculation for Fe500."""
        cost = calculate_steel_cost(100.0, "Fe500", self.profile)
        expected = 72.0 * 100.0 * 1.05
        self.assertAlmostEqual(cost, expected, places=2)

    def test_steel_cost_unknown_grade_uses_default(self):
        """Test that unknown grade uses default rate."""
        cost = calculate_steel_cost(100.0, "Fe999", self.profile)
        expected = 72.0 * 100.0 * 1.05  # Default Fe500 rate
        self.assertAlmostEqual(cost, expected, places=2)

    def test_steel_cost_zero_weight(self):
        """Test steel cost with zero weight."""
        cost = calculate_steel_cost(0.0, "Fe415", self.profile)
        self.assertEqual(cost, 0.0)

    def test_steel_cost_negative_weight_raises_error(self):
        """Test that negative weight raises ValueError."""
        with self.assertRaises(ValueError):
            calculate_steel_cost(-1.0, "Fe415", self.profile)


class TestFormworkCost(unittest.TestCase):
    """Test calculate_formwork_cost function."""

    def setUp(self):
        self.profile = CostProfile()

    def test_basic_formwork_cost(self):
        """Test formwork cost calculation."""
        cost = calculate_formwork_cost(10.0, self.profile)
        expected = 10.0 * 500.0
        self.assertAlmostEqual(cost, expected, places=2)

    def test_formwork_cost_zero_area(self):
        """Test formwork cost with zero area."""
        cost = calculate_formwork_cost(0.0, self.profile)
        self.assertEqual(cost, 0.0)

    def test_formwork_cost_negative_area_raises_error(self):
        """Test that negative area raises ValueError."""
        with self.assertRaises(ValueError):
            calculate_formwork_cost(-1.0, self.profile)


class TestTotalBeamCost(unittest.TestCase):
    """Test calculate_total_beam_cost function."""

    def setUp(self):
        self.profile = CostProfile()
        self.standard_beam = {
            "b_mm": 300,
            "d_mm": 450,
            "h_mm": 500,
            "length_m": 6.0,
            "ast_mm2": 1256,  # 4-20mm bars, pt ≈ 0.93%
            "asc_mm2": 0,
            "fck": 25,
            "fy": 415,
        }

    def test_total_beam_cost_structure(self):
        """Test that total beam cost returns correct structure."""
        result = calculate_total_beam_cost(self.standard_beam, self.profile)

        # Check all keys exist
        self.assertIn("concrete_cost", result)
        self.assertIn("steel_cost", result)
        self.assertIn("formwork_cost", result)
        self.assertIn("labor_cost", result)
        self.assertIn("congestion_penalty", result)
        self.assertIn("total_cost", result)
        self.assertIn("reinforcement_percentage", result)

    def test_total_beam_cost_values_positive(self):
        """Test that all cost components are positive."""
        result = calculate_total_beam_cost(self.standard_beam, self.profile)

        self.assertGreater(result["concrete_cost"], 0)
        self.assertGreater(result["steel_cost"], 0)
        self.assertGreater(result["formwork_cost"], 0)
        self.assertGreater(result["labor_cost"], 0)
        self.assertGreaterEqual(result["congestion_penalty"], 0)
        self.assertGreater(result["total_cost"], 0)

    def test_total_beam_cost_sum(self):
        """Test that total cost equals sum of components."""
        result = calculate_total_beam_cost(self.standard_beam, self.profile)

        expected_total = (
            result["concrete_cost"]
            + result["steel_cost"]
            + result["formwork_cost"]
            + result["labor_cost"]
        )

        self.assertAlmostEqual(result["total_cost"], expected_total, places=2)

    def test_concrete_cost_calculation(self):
        """Test concrete cost component calculation."""
        result = calculate_total_beam_cost(self.standard_beam, self.profile)

        # Manual calculation
        volume_m3 = (300 * 500 * 6000) / 1e9  # 0.9 m³
        expected_concrete_cost = volume_m3 * 6700.0 * 1.05

        self.assertAlmostEqual(
            result["concrete_cost"], expected_concrete_cost, places=2
        )

    def test_steel_cost_calculation(self):
        """Test steel cost component calculation."""
        result = calculate_total_beam_cost(self.standard_beam, self.profile)

        # Manual calculation
        steel_volume_m3 = (1256 * 6000) / 1e9
        steel_weight_kg = steel_volume_m3 * STEEL_DENSITY_KG_PER_M3
        expected_steel_cost = steel_weight_kg * 72.0 * 1.05

        self.assertAlmostEqual(result["steel_cost"], expected_steel_cost, places=2)

    def test_formwork_cost_calculation(self):
        """Test formwork cost component calculation."""
        result = calculate_total_beam_cost(self.standard_beam, self.profile)

        # Manual calculation: perimeter (3 sides) × length
        perimeter_m = (300 + 2 * 500) / 1000.0  # 1.3 m
        area_m2 = perimeter_m * 6.0  # 7.8 m²
        expected_formwork_cost = area_m2 * 500.0

        self.assertAlmostEqual(
            result["formwork_cost"], expected_formwork_cost, places=2
        )

    def test_reinforcement_percentage_calculation(self):
        """Test reinforcement percentage calculation."""
        result = calculate_total_beam_cost(self.standard_beam, self.profile)

        # Manual calculation
        expected_pt = (1256 / (300 * 450)) * 100.0

        self.assertAlmostEqual(
            result["reinforcement_percentage"], expected_pt, places=4
        )

    def test_no_congestion_penalty_below_threshold(self):
        """Test that no congestion penalty applies when pt <= 2.5%."""
        result = calculate_total_beam_cost(self.standard_beam, self.profile)

        # Standard beam has pt ≈ 0.93%, should have no penalty
        self.assertEqual(result["congestion_penalty"], 0.0)
        self.assertLess(result["reinforcement_percentage"], 2.5)

    def test_congestion_penalty_above_threshold(self):
        """Test that congestion penalty applies when pt > 2.5%."""
        # Create beam with high reinforcement (pt > 2.5%)
        high_rebar_beam = self.standard_beam.copy()
        high_rebar_beam["ast_mm2"] = 4000  # pt ≈ 2.96%

        result = calculate_total_beam_cost(high_rebar_beam, self.profile)

        # Should have congestion penalty
        self.assertGreater(result["congestion_penalty"], 0.0)
        self.assertGreater(result["reinforcement_percentage"], 2.5)

        # Penalty should be 20% of base labor cost
        volume_m3 = (300 * 500 * 6000) / 1e9
        labor_days = volume_m3 / 5.0
        base_labor = labor_days * 800.0
        expected_penalty = base_labor * 0.2

        self.assertAlmostEqual(result["congestion_penalty"], expected_penalty, places=2)

    def test_congestion_penalty_at_threshold(self):
        """Test behavior at exactly pt = 2.5%."""
        # Create beam with pt exactly at 2.5%
        threshold_beam = self.standard_beam.copy()
        threshold_beam["ast_mm2"] = 0.025 * 300 * 450  # pt = 2.5%

        result = calculate_total_beam_cost(threshold_beam, self.profile)

        # At exactly 2.5%, no penalty should apply
        self.assertEqual(result["congestion_penalty"], 0.0)
        self.assertAlmostEqual(result["reinforcement_percentage"], 2.5, places=2)

    def test_beam_with_compression_steel(self):
        """Test beam cost with compression reinforcement."""
        beam_with_asc = self.standard_beam.copy()
        beam_with_asc["asc_mm2"] = 628  # 2-20mm bars

        result = calculate_total_beam_cost(beam_with_asc, self.profile)

        # Total steel area should include both tension and compression
        total_area = 1256 + 628
        steel_volume_m3 = (total_area * 6000) / 1e9
        steel_weight_kg = steel_volume_m3 * STEEL_DENSITY_KG_PER_M3
        expected_steel_cost = steel_weight_kg * 72.0 * 1.05

        self.assertAlmostEqual(result["steel_cost"], expected_steel_cost, places=2)

    def test_missing_required_key_raises_error(self):
        """Test that missing required keys raise ValueError."""
        incomplete_beam = {"b_mm": 300, "d_mm": 450}

        with self.assertRaises(ValueError) as context:
            calculate_total_beam_cost(incomplete_beam, self.profile)

        self.assertIn("Missing required key", str(context.exception))

    def test_negative_dimensions_raise_error(self):
        """Test that negative dimensions raise ValueError."""
        invalid_beam = self.standard_beam.copy()
        invalid_beam["b_mm"] = -300

        with self.assertRaises(ValueError) as context:
            calculate_total_beam_cost(invalid_beam, self.profile)

        self.assertIn("must be positive", str(context.exception))

    def test_zero_dimensions_raise_error(self):
        """Test that zero dimensions raise ValueError."""
        invalid_beam = self.standard_beam.copy()
        invalid_beam["h_mm"] = 0

        with self.assertRaises(ValueError):
            calculate_total_beam_cost(invalid_beam, self.profile)

    def test_negative_steel_area_raises_error(self):
        """Test that negative steel area raises ValueError."""
        invalid_beam = self.standard_beam.copy()
        invalid_beam["ast_mm2"] = -100

        with self.assertRaises(ValueError) as context:
            calculate_total_beam_cost(invalid_beam, self.profile)

        self.assertIn("Steel areas cannot be negative", str(context.exception))

    def test_different_concrete_grades(self):
        """Test cost calculation with different concrete grades."""
        # Test M20
        beam_m20 = self.standard_beam.copy()
        beam_m20["fck"] = 20
        result_m20 = calculate_total_beam_cost(beam_m20, self.profile)

        # Test M30
        beam_m30 = self.standard_beam.copy()
        beam_m30["fck"] = 30
        result_m30 = calculate_total_beam_cost(beam_m30, self.profile)

        # M30 should be more expensive than M20
        self.assertGreater(result_m30["concrete_cost"], result_m20["concrete_cost"])

    def test_different_steel_grades(self):
        """Test cost calculation with different steel grades."""
        # Test Fe415
        beam_fe415 = self.standard_beam.copy()
        beam_fe415["fy"] = 415
        result_fe415 = calculate_total_beam_cost(beam_fe415, self.profile)

        # Test Fe500
        beam_fe500 = self.standard_beam.copy()
        beam_fe500["fy"] = 500
        result_fe500 = calculate_total_beam_cost(beam_fe500, self.profile)

        # Single steel rate by default, so costs should match
        self.assertAlmostEqual(
            result_fe500["steel_cost"], result_fe415["steel_cost"], places=2
        )


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def setUp(self):
        self.profile = CostProfile()

    def test_very_small_beam(self):
        """Test cost calculation for very small beam."""
        small_beam = {
            "b_mm": 150,
            "d_mm": 200,
            "h_mm": 230,
            "length_m": 1.0,
            "ast_mm2": 157,  # 1-16mm bar
            "asc_mm2": 0,
            "fck": 20,
            "fy": 415,
        }

        result = calculate_total_beam_cost(small_beam, self.profile)

        self.assertGreater(result["total_cost"], 0)
        self.assertEqual(result["congestion_penalty"], 0.0)

    def test_very_large_beam(self):
        """Test cost calculation for very large beam."""
        large_beam = {
            "b_mm": 600,
            "d_mm": 900,
            "h_mm": 1000,
            "length_m": 12.0,
            "ast_mm2": 5000,
            "asc_mm2": 1000,
            "fck": 40,
            "fy": 500,
        }

        result = calculate_total_beam_cost(large_beam, self.profile)

        self.assertGreater(result["total_cost"], 0)
        # Check all components are reasonable
        self.assertGreater(result["concrete_cost"], 0)
        self.assertGreater(result["steel_cost"], 0)
        self.assertGreater(result["formwork_cost"], 0)
        self.assertGreater(result["labor_cost"], 0)

    def test_beam_with_zero_steel(self):
        """Test beam with zero reinforcement (edge case)."""
        no_steel_beam = {
            "b_mm": 300,
            "d_mm": 450,
            "h_mm": 500,
            "length_m": 6.0,
            "ast_mm2": 0,
            "asc_mm2": 0,
            "fck": 25,
            "fy": 415,
        }

        result = calculate_total_beam_cost(no_steel_beam, self.profile)

        self.assertEqual(result["steel_cost"], 0.0)
        self.assertGreater(result["concrete_cost"], 0)
        self.assertEqual(result["reinforcement_percentage"], 0.0)


if __name__ == "__main__":
    unittest.main()
