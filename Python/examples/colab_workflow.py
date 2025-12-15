"""Colab-friendly full workflow example.

This script is intentionally single-file and copy/paste friendly.
It demonstrates a minimal end-to-end workflow:
- Flexure (singly reinforced)
- Shear
- Basic detailing checks (Ld, lap, bar spacing)
- Optional DXF generation (requires ezdxf)

Usage (local):
    cd Python
    python examples/colab_workflow.py

Usage (Google Colab):
    1) Install the package from GitHub (see repo README / docs)
    2) Copy this file into the notebook environment and run it.
"""

from __future__ import annotations

import math

from structural_lib import detailing, flexure, shear


def main() -> None:
    # === Inputs (all units explicit) ===
    b_mm = 300.0
    D_mm = 500.0
    cover_mm = 40.0
    stirrup_dia_mm = 8.0
    main_bar_dia_mm = 16.0

    fck_nmm2 = 25.0
    fy_nmm2 = 500.0

    Mu_knm = 150.0
    Vu_kn = 100.0

    # Effective depth (simple assumption)
    d_mm = D_mm - cover_mm - stirrup_dia_mm - main_bar_dia_mm / 2

    print("=== FLEXURE ===")
    flex = flexure.design_singly_reinforced(
        b=b_mm,
        d=d_mm,
        d_total=D_mm,
        mu_knm=Mu_knm,
        fck=fck_nmm2,
        fy=fy_nmm2,
    )
    print("Safe?", flex.is_safe, "| Mu_lim:", round(flex.mu_lim, 2), "kN-m")
    print("Ast_req:", round(flex.ast_required, 1), "mm2 | pt:", round(flex.pt_provided, 3), "%")

    # Pick bars (very simple)
    bar_area = math.pi * (main_bar_dia_mm / 2) ** 2
    n_bars = max(2, math.ceil(flex.ast_required / bar_area))
    ast_prov = n_bars * bar_area
    pt_percent = ast_prov * 100 / (b_mm * d_mm)
    print(
        "Provide:",
        n_bars,
        "x",
        int(main_bar_dia_mm),
        "mm bars | Ast_prov:",
        round(ast_prov, 1),
        "mm2",
    )

    print("\n=== SHEAR ===")
    legs = 2
    asv_mm2 = legs * math.pi * (stirrup_dia_mm / 2) ** 2

    shr = shear.design_shear(
        vu_kn=Vu_kn,
        b=b_mm,
        d=d_mm,
        fck=fck_nmm2,
        fy=fy_nmm2,
        asv=asv_mm2,
        pt=pt_percent,
    )

    print("Safe?", shr.is_safe, "| spacing:", round(shr.spacing, 1), "mm")
    print(
        "tv:",
        round(shr.tv, 3),
        "N/mm2 | tc:",
        round(shr.tc, 3),
        "N/mm2 | tc_max:",
        round(shr.tc_max, 3),
        "N/mm2",
    )

    print("\n=== DETAILING (basic) ===")
    ld_mm = detailing.calculate_development_length(main_bar_dia_mm, fck_nmm2, fy_nmm2)
    lap_mm = detailing.calculate_lap_length(
        main_bar_dia_mm, fck_nmm2, fy_nmm2, is_seismic=False
    )

    # calculate_bar_spacing returns center-to-center spacing
    spacing_cc = detailing.calculate_bar_spacing(
        b_mm, cover_mm, stirrup_dia_mm, main_bar_dia_mm, n_bars
    )
    spacing_clear = spacing_cc - main_bar_dia_mm

    # IS 456 Cl. 26.3.2 minimum clear spacing (assume 20mm agg)
    agg_size = 20.0
    min_clear = max(main_bar_dia_mm, agg_size + 5.0, 25.0)

    print("Ld:", round(ld_mm, 0), "mm | Lap:", round(lap_mm, 0), "mm")
    print(
        "Bar spacing:",
        spacing_cc,
        "mm c/c | clear:",
        round(spacing_clear, 0),
        "mm | min clear:",
        min_clear,
        "mm",
    )

    # Optional DXF (requires ezdxf)
    try:
        import ezdxf  # noqa: F401
        from structural_lib.detailing import create_beam_detailing
        from structural_lib.dxf_export import generate_beam_dxf

        det = create_beam_detailing(
            beam_id="B1",
            story="Colab",
            b=b_mm,
            D=D_mm,
            span=4000.0,
            cover=cover_mm,
            fck=fck_nmm2,
            fy=fy_nmm2,
            ast_start=flex.ast_required,
            ast_mid=flex.ast_required,
            ast_end=flex.ast_required,
            asc_start=0.0,
            asc_mid=0.0,
            asc_end=0.0,
            stirrup_dia=stirrup_dia_mm,
            stirrup_spacing_start=shr.spacing,
            stirrup_spacing_mid=shr.spacing,
            stirrup_spacing_end=shr.spacing,
            is_seismic=False,
        )

        out_path = "beam_B1.dxf"
        generate_beam_dxf(det, out_path)
        print("\nDXF saved to:", out_path)
    except ImportError as exc:
        print("\n(DXF skipped) Import failed:", exc)
        print("To enable in Colab:")
        print("  %pip install -q ezdxf")
        print("  (then Runtime > Restart runtime, and rerun)")


if __name__ == "__main__":
    main()
