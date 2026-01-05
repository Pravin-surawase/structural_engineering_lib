"""Generate sample DXF files for quality assessment."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[5]
PYTHON_DIR = REPO_ROOT / "Python"
sys.path.insert(0, str(PYTHON_DIR))

from structural_lib import detailing, dxf_export, flexure  # noqa: E402

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def design_beam(*, b: float, d: float, D: float, mu_knm: float, fck: float, fy: float):
    return flexure.design_singly_reinforced(
        b=b, d=d, d_total=D, mu_knm=mu_knm, fck=fck, fy=fy
    )


print("Generating Test Case 1: Simple residential beam...")
beam1 = design_beam(b=300, d=450, D=500, mu_knm=120, fck=25, fy=500)
print(f"  Ast required: {beam1.ast_required:.2f} mm^2")

try:
    detailing_1 = detailing.create_beam_detailing(
        beam_id="B1",
        story="L1",
        b=300,
        D=500,
        span=6000,
        cover=25,
        fck=25,
        fy=500,
        ast_start=beam1.ast_required,
        ast_mid=beam1.ast_required,
        ast_end=beam1.ast_required,
        stirrup_dia=8,
        stirrup_spacing_start=150,
        stirrup_spacing_mid=200,
        stirrup_spacing_end=150,
    )
    out_path = OUTPUT_DIR / "test_beam_1.dxf"
    dxf_export.generate_beam_dxf(
        detailing_1,
        str(out_path),
        include_dimensions=True,
        include_annotations=True,
        include_section_cuts=True,
        include_title_block=True,
    )
    print(f"  DXF generated: {out_path}")
except Exception as exc:
    print(f"  DXF generation failed: {exc}")

print("\nGenerating Test Case 2: Commercial heavy beam...")
beam2 = design_beam(b=400, d=600, D=650, mu_knm=300, fck=30, fy=500)
print(f"  Ast required: {beam2.ast_required:.2f} mm^2")

try:
    detailing_2 = detailing.create_beam_detailing(
        beam_id="B2",
        story="L2",
        b=400,
        D=650,
        span=8000,
        cover=30,
        fck=30,
        fy=500,
        ast_start=beam2.ast_required,
        ast_mid=beam2.ast_required,
        ast_end=beam2.ast_required,
        stirrup_dia=10,
        stirrup_spacing_start=125,
        stirrup_spacing_mid=175,
        stirrup_spacing_end=125,
    )
    out_path = OUTPUT_DIR / "test_beam_2.dxf"
    dxf_export.generate_beam_dxf(
        detailing_2,
        str(out_path),
        include_dimensions=True,
        include_annotations=True,
        include_section_cuts=True,
        include_title_block=True,
    )
    print(f"  DXF generated: {out_path}")
except Exception as exc:
    print(f"  DXF generation failed: {exc}")

print("\nDXF Generation Test Complete")
