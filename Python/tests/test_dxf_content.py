import os
import sys
import tempfile
import unittest

# Add parent directory to path to import structural_lib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from structural_lib import bbs
from structural_lib import dxf_export
from structural_lib.detailing import create_beam_detailing


class TestDXFContent(unittest.TestCase):
    def test_dxf_contains_required_text(self):
        if not dxf_export.EZDXF_AVAILABLE:
            self.skipTest("ezdxf is not installed; DXF tests skipped")

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
            dxf_export.generate_beam_dxf(detailing, out_path)

            import ezdxf

            doc = ezdxf.readfile(out_path)
            msp = doc.modelspace()

        text_entities = list(msp.query("TEXT"))
        texts = [t.dxf.text for t in text_entities]
        combined = "\n".join(texts)

        # Header includes beam ID and story.
        self.assertIn("BEAM B1", combined)
        self.assertIn("Story: S1", combined)

        # Zone labels for callouts should be present.
        self.assertIn("Bottom Start:", combined)
        self.assertIn("Bottom Mid:", combined)
        self.assertIn("Bottom End:", combined)
        self.assertIn("Top Start:", combined)
        self.assertIn("Top Mid:", combined)
        self.assertIn("Top End:", combined)
        self.assertIn("Stirrup Start:", combined)

        # At least one bar mark should appear in text callouts.
        marks = set()
        for text in texts:
            marks.update(bbs.extract_bar_marks_from_text(text))
        self.assertGreater(len(marks), 0)


if __name__ == "__main__":
    unittest.main()
