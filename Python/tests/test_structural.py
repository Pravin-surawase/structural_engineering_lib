import unittest
import sys
import os

# Add parent directory to path to import structural_lib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from structural_lib import flexure, shear, tables, materials, types


class TestStructuralLib(unittest.TestCase):

    def test_materials(self):
        # Check Xu_max/d
        self.assertAlmostEqual(materials.get_xu_max_d(250), 0.53)
        self.assertAlmostEqual(materials.get_xu_max_d(415), 0.48)
        self.assertAlmostEqual(materials.get_xu_max_d(500), 0.46)

        # Check Ec
        self.assertAlmostEqual(materials.get_ec(25), 25000.0)  # 5000 * 5

    def test_tables_tc(self):
        # Table 19 Check
        # M20, pt=0.5 -> 0.48
        self.assertAlmostEqual(tables.get_tc_value(20, 0.5), 0.48)

        # M20, pt=0.75 -> 0.56
        self.assertAlmostEqual(tables.get_tc_value(20, 0.75), 0.56)

        # Interpolation: M20, pt=0.625 (mid of 0.5 and 0.75) -> (0.48+0.56)/2 = 0.52
        self.assertAlmostEqual(tables.get_tc_value(20, 0.625), 0.52)

        # Fck Interpolation: M22.5 (mid of 20 and 25), pt=0.5
        # M20, pt=0.5 -> 0.48
        # M25, pt=0.5 -> 0.49
        # No fck interpolation: use lower grade column (M20) -> 0.48
        self.assertAlmostEqual(tables.get_tc_value(22.5, 0.5), 0.48)

    def test_flexure_mulim(self):
        # M20, Fe415, b=230, d=450
        # Q_lim = 0.36 * 0.48 * (1 - 0.42*0.48) * 20 = 2.76 approx
        # Mu_lim = 2.76 * 230 * 450^2 / 1e6 = 128.54 kN-m

        mu_lim = flexure.calculate_mu_lim(230, 450, 20, 415)
        # Exact calc:
        # k = 0.36 * 0.48 * (1 - 0.42 * 0.48) = 0.13795
        # R = k * fck = 2.759
        # Mu = 2.759 * 230 * 450^2 / 1e6 = 128.5
        self.assertTrue(128 < mu_lim < 129)

    def test_flexure_design(self):
        # Design for Mu = 100 kNm (Under reinforced)
        b, d, D = 230, 450, 500
        fck, fy = 20, 415

        res = flexure.design_singly_reinforced(b, d, D, 100, fck, fy)

        self.assertTrue(res.is_safe)
        self.assertEqual(res.section_type, types.DesignSectionType.UNDER_REINFORCED)
        self.assertTrue(res.ast_required > 0)

        # Check Ast calc manually
        # Mu/bd^2 = 100e6 / (230*450^2) = 2.147
        # Pt formula or Ast formula...
        # Approx Ast: Mu / (0.87 * fy * 0.9 * d) = 100e6 / (0.87*415*0.9*450) = 683 mm2
        self.assertTrue(650 < res.ast_required < 750)

    def test_shear_design(self):
        # M20, Fe415
        b, d = 230, 450
        Vu = 100  # kN

        # Tv = 100e3 / (230*450) = 0.966 N/mm2
        # Tc_max (M20) = 2.8
        # Safe.

        # Assume pt = 1.0%
        # Tc (M20, 1.0%) = 0.62
        # Tv > Tc -> Shear Reinf Required.

        # Vus = 100 - (0.62 * 230 * 450 / 1000) = 100 - 64.17 = 35.83 kN

        # 2 legged 8mm stirrups -> Asv = 100.5 mm2
        asv = 100.5

        # Spacing = 0.87 * 415 * 100.5 * 450 / (35.83 * 1000)
        # = 16328737.5 / 35830 = 455 mm

        # Max spacing check: 0.75d = 337.5, or 300.
        # So spacing should be limited to 300.

        res = shear.design_shear(Vu, b, d, 20, 415, asv, 1.0)

        self.assertTrue(res.is_safe)
        self.assertEqual(res.spacing, 300.0)
        self.assertTrue(res.vus > 0)

    def test_flexure_negative_mu_matches_positive(self):
        """Core flexure design should treat Mu by magnitude (sign handled in UI/app layer)."""
        b, d, D = 230, 450, 500
        fck, fy = 20, 415
        mu = 100

        res_pos = flexure.design_singly_reinforced(b, d, D, mu, fck, fy)
        res_neg = flexure.design_singly_reinforced(b, d, D, -mu, fck, fy)

        self.assertEqual(res_pos.is_safe, res_neg.is_safe)
        self.assertEqual(res_pos.section_type, res_neg.section_type)
        self.assertAlmostEqual(res_pos.ast_required, res_neg.ast_required, places=8)
        self.assertAlmostEqual(res_pos.xu, res_neg.xu, places=8)

    def test_shear_negative_vu_matches_positive(self):
        """Core shear design should treat Vu by magnitude (sign handled in UI/app layer)."""
        b, d = 230, 450
        fck, fy = 20, 415
        asv, pt = 100.5, 1.0
        vu = 100

        res_pos = shear.design_shear(vu, b, d, fck, fy, asv, pt)
        res_neg = shear.design_shear(-vu, b, d, fck, fy, asv, pt)

        self.assertEqual(res_pos.is_safe, res_neg.is_safe)
        self.assertAlmostEqual(res_pos.tv, res_neg.tv, places=12)
        self.assertAlmostEqual(res_pos.tc, res_neg.tc, places=12)
        self.assertAlmostEqual(res_pos.vus, res_neg.vus, places=12)
        self.assertAlmostEqual(res_pos.spacing, res_neg.spacing, places=12)

    def test_shear_zero_vu_min_reinforcement_spacing_capped(self):
        """Vu=0 should still trigger minimum shear reinforcement spacing caps deterministically."""
        b, d = 230, 450
        fck, fy = 20, 415
        asv, pt = 100.5, 1.0

        res = shear.design_shear(0.0, b, d, fck, fy, asv, pt)

        self.assertTrue(res.is_safe)
        self.assertEqual(res.vus, 0.0)
        self.assertIn("minimum shear reinforcement", res.remarks)
        self.assertEqual(res.spacing, 300.0)

    # --------------------------------------------------------------------------
    # TASK-006: Edge Case Tests
    # --------------------------------------------------------------------------

    def test_flexure_min_steel(self):
        """Test that minimum steel is provided when Mu is very small."""
        b, d, D = 230, 450, 500
        fck, fy = 20, 415
        mu_small = 5  # Very small moment

        res = flexure.design_singly_reinforced(b, d, D, mu_small, fck, fy)

        # Ast_min = 0.85 * b * d / fy
        ast_min = 0.85 * 230 * 450 / 415
        # = 212.0 mm2

        self.assertTrue(res.is_safe)
        self.assertAlmostEqual(res.ast_required, ast_min, places=1)
        self.assertIn("Minimum steel", res.error_message)

    def test_flexure_over_reinforced(self):
        """Test that section is flagged as over-reinforced when Mu > Mu_lim."""
        b, d, D = 230, 450, 500
        fck, fy = 20, 415

        # Mu_lim for this section is ~128 kNm (from previous test)
        mu_large = 150  # > 128

        res = flexure.design_singly_reinforced(b, d, D, mu_large, fck, fy)

        self.assertFalse(res.is_safe)
        self.assertEqual(res.section_type, types.DesignSectionType.OVER_REINFORCED)
        self.assertEqual(res.ast_required, 0.0)

    def test_flexure_threshold_near_mu_lim(self):
        """Mu just below Mu_lim should be safe; just above should fail (threshold stability)."""
        b, d, D = 230, 450, 500
        fck, fy = 20, 415

        mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)

        res_below = flexure.design_singly_reinforced(
            b, d, D, mu_lim * 0.999999, fck, fy
        )
        self.assertTrue(res_below.is_safe)
        self.assertEqual(
            res_below.section_type, types.DesignSectionType.UNDER_REINFORCED
        )
        self.assertTrue(res_below.ast_required > 0.0)

        res_above = flexure.design_singly_reinforced(
            b, d, D, mu_lim * 1.000001, fck, fy
        )
        self.assertFalse(res_above.is_safe)
        self.assertEqual(
            res_above.section_type, types.DesignSectionType.OVER_REINFORCED
        )

    def test_shear_threshold_at_tc_max(self):
        """Tv == Tc_max should be treated as OK; Tv > Tc_max should fail."""
        b, d = 230, 450
        fck, fy = 20, 415
        asv, pt = 100.5, 1.0

        tc_max = tables.get_tc_max_value(fck)
        vu_at = (tc_max * b * d) / 1000.0

        res_at = shear.design_shear(vu_at, b, d, fck, fy, asv, pt)
        self.assertTrue(res_at.is_safe)
        self.assertAlmostEqual(res_at.tv, tc_max, places=9)

        res_above = shear.design_shear(vu_at + 0.1, b, d, fck, fy, asv, pt)
        self.assertFalse(res_above.is_safe)
        self.assertIn("exceeds Tc_max", res_above.remarks)

    def test_shear_unsafe_section(self):
        """Test that section fails if Tv > Tc_max."""
        b, d = 230, 450
        fck, fy = 20, 415
        asv, pt = 100.5, 1.0

        # Tc_max for M20 is 2.8 N/mm2
        # Need Tv > 2.8
        # Vu > 2.8 * 230 * 450 / 1000 = 289.8 kN
        vu_unsafe = 300

        res = shear.design_shear(vu_unsafe, b, d, fck, fy, asv, pt)

        self.assertFalse(res.is_safe)
        self.assertIn("exceeds Tc_max", res.remarks)

    def test_shear_min_reinforcement(self):
        """Test that min shear reinforcement spacing is calculated when Tv < Tc."""
        b, d = 230, 450
        fck, fy = 20, 415
        asv, pt = 100.5, 1.0

        # Tc for M20, 1.0% is 0.62 N/mm2
        # Need Tv < 0.62
        # Vu < 0.62 * 230 * 450 / 1000 = 64.17 kN
        vu_small = 50

        res = shear.design_shear(vu_small, b, d, fck, fy, asv, pt)

        self.assertTrue(res.is_safe)
        self.assertEqual(res.vus, 0.0)
        self.assertIn("minimum shear reinforcement", res.remarks)

        # Check spacing for min reinf:
        # s = (0.87 * fy * Asv) / (0.4 * b)
        # s = (0.87 * 415 * 100.5) / (0.4 * 230) = 36286 / 92 = 394.4 mm
        # But max spacing limit is 0.75d = 337.5 or 300.
        # So expected spacing is 300.
        self.assertEqual(res.spacing, 300.0)

    def test_tables_pt_clamping(self):
        """Test that pt is clamped to 0.15 and 3.0 for Tc lookup."""
        # Low pt (< 0.15) -> should use 0.15 value
        # M20, pt=0.05 -> use pt=0.15 -> 0.28
        self.assertAlmostEqual(tables.get_tc_value(20, 0.05), 0.28)

        # High pt (> 3.0) -> should use 3.0 value
        # M20, pt=4.0 -> use pt=3.0 -> 0.82
        self.assertAlmostEqual(tables.get_tc_value(20, 4.0), 0.82)


if __name__ == "__main__":
    unittest.main()
