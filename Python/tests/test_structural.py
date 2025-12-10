import unittest
import math
import sys
import os

# Add parent directory to path to import structural_lib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from structural_lib import flexure, shear, tables, materials, types

class TestStructuralLib(unittest.TestCase):
    
    def test_materials(self):
        # Check Xu_max/d
        self.assertAlmostEqual(materials.get_xu_max_d(250), 0.53)
        self.assertAlmostEqual(materials.get_xu_max_d(415), 0.48)
        self.assertAlmostEqual(materials.get_xu_max_d(500), 0.46)
        
        # Check Ec
        self.assertAlmostEqual(materials.get_ec(25), 25000.0) # 5000 * 5
        
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
        Vu = 100 # kN
        
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

if __name__ == '__main__':
    unittest.main()
