#!/usr/bin/env python3
"""End-to-end beam design workflow.

Complete pipeline: Design → Detailing → BBS → Report

Requirements:
    pip install structural-lib-is456

Usage:
    python end_to_end_workflow.py
"""

from structural_lib.services import api


def main():
    # ─── Step 1: Design the beam ───────────────────────────────
    print("Step 1: Designing beam per IS 456:2000...")
    result = api.design_beam_is456(
        units="IS456",
        case_id="DL+LL",
        b_mm=300,  # Beam width (mm)
        D_mm=500,  # Overall depth (mm)
        d_mm=450,  # Effective depth (mm)
        fck_nmm2=25,  # Concrete grade M25 (N/mm²)
        fy_nmm2=500,  # Steel grade Fe500 (N/mm²)
        mu_knm=150,  # Factored bending moment (kN·m)
        vu_kn=100,  # Factored shear force (kN)
    )
    print(f"  Flexure: Ast = {result.flexure.Ast_required:.0f} mm²")
    print(f"  Shear:   spacing = {result.shear.spacing:.0f} mm")
    print(
        f"  Status:  flexure {'SAFE' if result.flexure.is_safe else 'UNSAFE'}, "
        f"shear {'SAFE' if result.shear.is_safe else 'UNSAFE'}"
    )

    # ─── Step 2: Generate detailing ────────────────────────────
    print("\nStep 2: Generating bar detailing...")
    detailing_input = api.build_detailing_input(
        result,
        beam_id="B1",
        b_mm=300,
        D_mm=500,
        d_mm=450,
        span_mm=6000,
        cover_mm=30,
        fck_nmm2=25,
        fy_nmm2=500,
    )
    detailed = api.compute_detailing(detailing_input)
    print(f"  Beams detailed: {len(detailed)}")
    for beam in detailed:
        print(
            f"  - {beam.beam_id}: "
            f"{len(beam.top_bars)} top zones, "
            f"{len(beam.bottom_bars)} bottom zones, "
            f"{len(beam.stirrups)} stirrup zones"
        )

    # ─── Step 3: Generate BBS (Bar Bending Schedule) ───────────
    print("\nStep 3: Generating BBS...")
    bbs_doc = api.compute_bbs(detailed, project_name="Example Project")
    print(f"  BBS items: {len(bbs_doc.items)}")
    print(f"  Total weight: {bbs_doc.summary.total_weight_kg:.1f} kg")
    for item in bbs_doc.items[:3]:
        print(
            f"  - {item.bar_mark}: dia {item.diameter_mm:.0f}mm "
            f"× {item.no_of_bars} nos, "
            f"cut length {item.cut_length_mm:.0f} mm"
        )

    # ─── Step 4: Generate report ───────────────────────────────
    print("\nStep 4: Generating HTML report...")
    report_html = api.compute_report(detailing_input, format="html")
    print(f"  Report size: {len(report_html)} characters")
    print(f"  Report type: {type(report_html).__name__}")

    print("\n✓ Complete pipeline finished successfully!")


if __name__ == "__main__":
    main()
