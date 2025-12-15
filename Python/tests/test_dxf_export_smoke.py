import os
import sys
import unittest
import tempfile

# Add parent directory to path to import structural_lib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from structural_lib.detailing import create_beam_detailing
from structural_lib import dxf_export


class TestDXFExportSmoke(unittest.TestCase):
    def test_generate_beam_dxf_smoke(self):
        """Generate a DXF and sanity-check it can be read."""
        if not dxf_export.EZDXF_AVAILABLE:
            self.skipTest("ezdxf is not installed; DXF export smoke test skipped")

        detailing = create_beam_detailing(
            beam_id="B1",
            story="S1",
            b=230,
            D=450,
            span=5000,
            cover=25,
            fck=25,
            fy=415,
            ast_start=900,
            ast_mid=700,
            ast_end=900,
            asc_start=0,
            asc_mid=0,
            asc_end=0,
            stirrup_dia=8,
            stirrup_spacing_start=100,
            stirrup_spacing_mid=150,
            stirrup_spacing_end=100,
            is_seismic=False,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "beam_detail.dxf")
            returned_path = dxf_export.generate_beam_dxf(detailing, out_path)

            self.assertEqual(returned_path, out_path)
            self.assertTrue(os.path.exists(out_path))
            self.assertGreater(os.path.getsize(out_path), 0)

            # Read back and check a few structural expectations.
            import ezdxf

            doc = ezdxf.readfile(out_path)
            self.assertIn("BEAM_OUTLINE", doc.layers)
            self.assertIn("REBAR_MAIN", doc.layers)
            self.assertIn("REBAR_STIRRUP", doc.layers)
            self.assertIn("TEXT", doc.layers)

            msp = doc.modelspace()
            line_count = len(list(msp.query("LINE")))
            text_count = len(list(msp.query("TEXT")))
            self.assertGreater(line_count, 0)
            self.assertGreater(text_count, 0)


if __name__ == "__main__":
    unittest.main()
