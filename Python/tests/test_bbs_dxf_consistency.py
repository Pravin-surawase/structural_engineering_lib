import csv
import os
import sys
import tempfile
import unittest

# Add parent directory to path to import structural_lib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from structural_lib import bbs, dxf_export
from structural_lib.detailing import create_beam_detailing


class TestBBSDXFConsistency(unittest.TestCase):
    def test_mark_diff_ok(self):
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

        items = bbs.generate_bbs_from_detailing(detailing)

        with tempfile.TemporaryDirectory() as tmpdir:
            bbs_path = os.path.join(tmpdir, "bbs.csv")
            dxf_path = os.path.join(tmpdir, "beam.dxf")

            bbs.export_bbs_to_csv(items, bbs_path, include_summary=False)
            dxf_export.generate_beam_dxf(detailing, dxf_path)

            result = dxf_export.compare_bbs_dxf_marks(bbs_path, dxf_path)

        self.assertTrue(result["ok"])
        self.assertEqual(result["summary"]["missing_in_dxf"], 0)
        self.assertEqual(result["summary"]["extra_in_dxf"], 0)

    def test_mark_diff_missing_in_dxf(self):
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

        items = bbs.generate_bbs_from_detailing(detailing)

        with tempfile.TemporaryDirectory() as tmpdir:
            bbs_path = os.path.join(tmpdir, "bbs.csv")
            dxf_path = os.path.join(tmpdir, "beam.dxf")

            bbs.export_bbs_to_csv(items, bbs_path, include_summary=False)
            dxf_export.generate_beam_dxf(detailing, dxf_path)

            with open(bbs_path, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                rows = list(reader)

            extra_mark = f"{detailing.beam_id}-B-S-D16-99"
            extra_row = {name: "" for name in (fieldnames or [])}
            extra_row["bar_mark"] = extra_mark
            extra_row["member_id"] = detailing.beam_id
            rows.append(extra_row)

            with open(bbs_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            result = dxf_export.compare_bbs_dxf_marks(bbs_path, dxf_path)

        self.assertFalse(result["ok"])
        self.assertEqual(result["summary"]["missing_in_dxf"], 1)
        self.assertEqual(result["summary"]["extra_in_dxf"], 0)

    def test_mark_diff_extra_in_dxf(self):
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

        items = bbs.generate_bbs_from_detailing(detailing)

        with tempfile.TemporaryDirectory() as tmpdir:
            bbs_path = os.path.join(tmpdir, "bbs.csv")
            dxf_path = os.path.join(tmpdir, "beam.dxf")

            bbs.export_bbs_to_csv(items, bbs_path, include_summary=False)
            dxf_export.generate_beam_dxf(detailing, dxf_path)

            with open(bbs_path, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                rows = list(reader)

            removed_mark = items[0].bar_mark
            rows = [row for row in rows if row.get("bar_mark") != removed_mark]

            with open(bbs_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            result = dxf_export.compare_bbs_dxf_marks(bbs_path, dxf_path)

        self.assertFalse(result["ok"])
        self.assertEqual(result["summary"]["missing_in_dxf"], 0)
        self.assertEqual(result["summary"]["extra_in_dxf"], 1)


if __name__ == "__main__":
    unittest.main()
