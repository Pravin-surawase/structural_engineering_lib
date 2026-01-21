#!/usr/bin/env python3
"""Regenerate golden HTML files for report tests."""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from structural_lib import report


def main() -> None:
    """Regenerate all golden HTML files."""
    fixtures = Path(__file__).parent.parent / "tests" / "fixtures" / "report"

    # 1. Regenerate report_single_1.html
    design_results_1 = json.loads((fixtures / "design_results_1.json").read_text())
    html_1 = report.render_design_report_single(design_results_1, batch_threshold=80)
    (fixtures / "report_single_1.html").write_text(html_1)
    print("Updated: report_single_1.html")

    # 2. Regenerate report_single_79.html
    design_results_79 = json.loads((fixtures / "design_results_79.json").read_text())
    html_79 = report.render_design_report_single(design_results_79, batch_threshold=80)
    (fixtures / "report_single_79.html").write_text(html_79)
    print("Updated: report_single_79.html")

    # 3. Regenerate batch files
    design_results_80 = json.loads((fixtures / "design_results_80.json").read_text())
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "report"
        report.write_design_report_package(
            design_results_80, output_path=out, batch_threshold=80
        )
        shutil.copy(out / "index.html", fixtures / "report_batch_index_80.html")
        shutil.copy(out / "beams" / "G_B1.html", fixtures / "report_batch_beam_G_B1.html")

    print("Updated: report_batch_index_80.html")
    print("Updated: report_batch_beam_G_B1.html")
    print("\nAll golden files regenerated!")


if __name__ == "__main__":
    main()
