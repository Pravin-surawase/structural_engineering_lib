import os
import sys
import unittest

# Add parent directory to path to import structural_lib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from structural_lib import materials, tables


class TestMaterialsEdges(unittest.TestCase):
    def test_get_xu_max_d_other_grade_uses_formula(self):
        fy = 550
        expected = 700 / (1100 + (0.87 * fy))
        self.assertAlmostEqual(materials.get_xu_max_d(fy), expected)

    def test_get_ec_and_fcr_negative_fck_returns_zero(self):
        self.assertEqual(materials.get_ec(-1), 0.0)
        self.assertEqual(materials.get_fcr(-5), 0.0)

    def test_get_steel_stress_fe250_elastoplastic(self):
        # Below yield: sigma = Es * strain
        s1 = materials.get_steel_stress(0.0005, 250)
        self.assertAlmostEqual(s1, 200000.0 * 0.0005)

        # Above yield: sigma = 0.87 fy
        s2 = materials.get_steel_stress(0.01, 250)
        self.assertAlmostEqual(s2, 0.87 * 250)

    def test_get_steel_stress_fe415_interpolation_and_plateau(self):
        # In the elastic region (< first point)
        s_el = materials.get_steel_stress(0.0010, 415)
        self.assertAlmostEqual(s_el, 200000.0 * 0.0010)

        # Between points: should be between adjacent stresses
        s_mid = materials.get_steel_stress(0.0020, 415)
        self.assertTrue(324.8 <= s_mid <= 342.8)

        # Beyond last point: plateau at last point
        s_pl = materials.get_steel_stress(0.01, 415)
        self.assertAlmostEqual(s_pl, 360.9)


class TestTablesEdges(unittest.TestCase):
    def test_tc_value_grade_clamping(self):
        # Below minimum grade: clamps to M15 column
        self.assertAlmostEqual(tables.get_tc_value(10, 0.15), 0.28)

        # Above maximum grade: clamps to M40 column
        self.assertAlmostEqual(tables.get_tc_value(60, 0.15), 0.30)

    def test_tc_value_grade_selection_nearest_lower(self):
        # For fck just below 40, nearest lower grade column is M35
        self.assertAlmostEqual(tables.get_tc_value(39.9, 0.15), 0.29)

        # At 40 and above, grade column is M40
        self.assertAlmostEqual(tables.get_tc_value(40.0, 0.15), 0.30)

    def test_tc_value_exact_table_points(self):
        # Exact pt points should return exact tabulated values (no drift)
        self.assertAlmostEqual(tables.get_tc_value(25, 0.15), 0.29)
        self.assertAlmostEqual(tables.get_tc_value(25, 3.0), 0.92)

    def test_tc_max_value_bounds_and_interpolation(self):
        self.assertEqual(tables.get_tc_max_value(10), 2.5)
        self.assertEqual(tables.get_tc_max_value(45), 4.0)

        # Interpolation between M25 (3.1) and M30 (3.5) at 27.5 should be 3.3
        self.assertAlmostEqual(tables.get_tc_max_value(27.5), 3.3)


if __name__ == "__main__":
    unittest.main()
