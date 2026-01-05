"""
Sample: Complete Beam Design Workflow
=====================================

This example demonstrates the full workflow:
1. Read beam data from CSV
2. Perform flexure and shear design
3. Generate detailing (Ld, lap, spacing)
4. Create bar schedule
5. Export DXF drawings (if ezdxf available)

Usage:
    python complete_beam_design.py

Input:
    sample_building_beams.csv (in same folder)

Output:
    beam_schedule_output.csv
    dxf_files/ (folder with DXF drawings)
"""

import csv
import math
import os
from dataclasses import dataclass
from typing import List

# Import library modules
from structural_lib import detailing, flexure, shear

# Optional DXF support (requires ezdxf)
try:
    from structural_lib.dxf_export import EZDXF_AVAILABLE, generate_beam_dxf

    DXF_AVAILABLE = EZDXF_AVAILABLE
except Exception:
    DXF_AVAILABLE = False
    generate_beam_dxf = None  # type: ignore[assignment]
    print("Note: Install ezdxf for DXF export: pip install ezdxf")


@dataclass
class BeamDesignOutput:
    """Complete design output for one beam."""

    beam_id: str
    story: str
    size: str
    span: float

    # Flexure
    mu_lim: float
    ast_required: float
    asc_required: float
    section_type: str

    # Reinforcement selected
    bottom_bars: str
    top_bars: str
    ast_provided: float
    asc_provided: float

    # Shear
    vu: float
    tv: float
    tc: float
    stirrup_spacing: float
    stirrups: str

    # Detailing
    ld: float
    lap_length: float
    bar_spacing: float

    # Status
    is_safe: bool
    remarks: str


def select_bars(area_required: float, min_count: int = 2) -> tuple:
    """
    Select practical bar arrangement for required area.

    Returns: (count, diameter, area_provided)
    """
    # Standard bar diameters and their areas
    bars = {12: 113.1, 16: 201.1, 20: 314.2, 25: 490.9, 32: 804.2}

    # Try each diameter, prefer smaller bars
    for dia, area in bars.items():
        count = max(min_count, math.ceil(area_required / area))
        if count <= 6:  # Practical limit per layer
            return count, dia, count * area

    # Fall back to 25mm bars
    dia = 25
    count = max(min_count, math.ceil(area_required / bars[dia]))
    return count, dia, count * bars[dia]


def design_beam(row: dict) -> BeamDesignOutput:
    """
    Complete design of a single beam.

    Args:
        row: Dictionary with beam data from CSV

    Returns:
        BeamDesignOutput with all design results
    """
    # Parse inputs
    beam_id = row["BeamID"]
    story = row["Story"]
    b = float(row["b"])
    D = float(row["D"])
    span = float(row["Span"])
    cover = float(row["Cover"])
    fck = float(row["fck"])
    fy = float(row["fy"])
    Mu = float(row["Mu"])
    Vu = float(row["Vu"])
    stirrup_dia = float(row.get("Stirrup_Dia", 8))

    # Calculate effective depth
    # d = D - cover - stirrup_dia - bar_dia/2 (assume 16mm main bar)
    d = D - cover - stirrup_dia - 8

    # =========================================
    # 1. FLEXURE DESIGN
    # =========================================

    # Check limiting moment
    mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)

    if Mu <= mu_lim:
        # Singly reinforced
        section_type = "Singly"
        flex_result = flexure.design_singly_reinforced(b, d, D, Mu, fck, fy)
        ast_required = flex_result.ast_required
        asc_required = 0
    else:
        # Doubly reinforced
        section_type = "Doubly"
        d_dash = cover + stirrup_dia + 8  # Compression steel level
        flex_result = flexure.design_doubly_reinforced(b, d, d_dash, D, Mu, fck, fy)
        ast_required = flex_result.ast_required
        asc_required = flex_result.asc_required

    # Select tension bars
    n_bot, dia_bot, ast_provided = select_bars(ast_required)
    bottom_bars = f"{n_bot}-{dia_bot}φ"

    # Select compression/hanger bars
    if asc_required > 0:
        n_top, dia_top, asc_provided = select_bars(asc_required)
    else:
        # Minimum hanger bars (2-12mm)
        n_top, dia_top, asc_provided = 2, 12, 226.2
    top_bars = f"{n_top}-{dia_top}φ"

    # =========================================
    # 2. SHEAR DESIGN
    # =========================================

    # Stirrup area (2-legged)
    Asv = 2 * math.pi * (stirrup_dia / 2) ** 2

    # Percentage of tension steel
    pt = (ast_provided * 100) / (b * d)

    shear_result = shear.design_shear(Vu, b, d, fck, fy, Asv, pt)

    # Round spacing down to nearest 25mm
    sv_calc = shear_result.spacing
    sv_practical = max(75, (sv_calc // 25) * 25)

    stirrups = f"2L-{int(stirrup_dia)}φ@{int(sv_practical)}"

    # =========================================
    # 3. DETAILING
    # =========================================

    # Use maximum bar diameter for Ld
    max_bar_dia = max(dia_bot, dia_top)
    ld = detailing.calculate_development_length(max_bar_dia, fck, fy)
    lap = detailing.calculate_lap_length(max_bar_dia, fck, fy, is_seismic=False)

    # Check bar spacing
    bar_spacing_cc = detailing.calculate_bar_spacing(
        b, cover, stirrup_dia, dia_bot, n_bot
    )

    # Minimum clear spacing per IS 456 Cl. 26.3.2
    agg_size = 20
    min_clear = max(dia_bot, agg_size + 5, 25)
    bar_spacing_clear = bar_spacing_cc - dia_bot

    # =========================================
    # 4. STATUS CHECK
    # =========================================

    is_safe = True
    remarks = []

    if not flex_result.is_safe:
        is_safe = False
        remarks.append(flex_result.error_message)

    if not shear_result.is_safe:
        is_safe = False
        remarks.append("Shear failure")

    if bar_spacing_clear < min_clear:
        is_safe = False
        remarks.append(
            f"Clear spacing {bar_spacing_clear:.0f}mm < min {min_clear:.0f}mm"
        )

    if not remarks:
        remarks = ["OK"]

    return BeamDesignOutput(
        beam_id=beam_id,
        story=story,
        size=f"{int(b)}×{int(D)}",
        span=span,
        mu_lim=round(mu_lim, 1),
        ast_required=round(ast_required, 0),
        asc_required=round(asc_required, 0),
        section_type=section_type,
        bottom_bars=bottom_bars,
        top_bars=top_bars,
        ast_provided=round(ast_provided, 0),
        asc_provided=round(asc_provided, 0),
        vu=Vu,
        tv=round(shear_result.tv, 3),
        tc=round(shear_result.tc, 3),
        stirrup_spacing=sv_practical,
        stirrups=stirrups,
        ld=round(ld, 0),
        lap_length=round(lap, 0),
        bar_spacing=round(bar_spacing_cc, 0),
        is_safe=is_safe,
        remarks="; ".join(remarks),
    )


def print_schedule(results: List[BeamDesignOutput]):
    """Print formatted beam schedule."""
    print("\n" + "=" * 100)
    print("BEAM DESIGN SCHEDULE - IS 456:2000")
    print("=" * 100)

    # Header
    print(
        f"{'Beam':<6} {'Story':<8} {'Size':<10} {'Span':<6} "
        f"{'Bottom':<10} {'Top':<10} {'Stirrups':<16} "
        f"{'Ld':<6} {'Status'}"
    )
    print("-" * 100)

    for r in results:
        status = "✓ OK" if r.is_safe else "✗ " + r.remarks[:15]
        print(
            f"{r.beam_id:<6} {r.story:<8} {r.size:<10} {int(r.span):<6} "
            f"{r.bottom_bars:<10} {r.top_bars:<10} {r.stirrups:<16} "
            f"{int(r.ld):<6} {status}"
        )

    print("=" * 100)


def save_schedule_csv(results: List[BeamDesignOutput], filepath: str):
    """Save results to CSV file."""
    fieldnames = [
        "BeamID",
        "Story",
        "Size",
        "Span",
        "Mu_lim",
        "Ast_req",
        "Asc_req",
        "Section_Type",
        "Bottom_Bars",
        "Top_Bars",
        "Ast_prov",
        "Asc_prov",
        "Vu",
        "Tv",
        "Tc",
        "Stirrup_Spacing",
        "Stirrups",
        "Ld",
        "Lap_Length",
        "Bar_Spacing",
        "Status",
        "Remarks",
    ]

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for r in results:
            writer.writerow(
                {
                    "BeamID": r.beam_id,
                    "Story": r.story,
                    "Size": r.size,
                    "Span": r.span,
                    "Mu_lim": r.mu_lim,
                    "Ast_req": r.ast_required,
                    "Asc_req": r.asc_required,
                    "Section_Type": r.section_type,
                    "Bottom_Bars": r.bottom_bars,
                    "Top_Bars": r.top_bars,
                    "Ast_prov": r.ast_provided,
                    "Asc_prov": r.asc_provided,
                    "Vu": r.vu,
                    "Tv": r.tv,
                    "Tc": r.tc,
                    "Stirrup_Spacing": r.stirrup_spacing,
                    "Stirrups": r.stirrups,
                    "Ld": r.ld,
                    "Lap_Length": r.lap_length,
                    "Bar_Spacing": r.bar_spacing,
                    "Status": "OK" if r.is_safe else "Check",
                    "Remarks": r.remarks,
                }
            )

    print(f"✓ Saved schedule to: {filepath}")


def main():
    """Main entry point."""
    print("=" * 60)
    print("COMPLETE BEAM DESIGN WORKFLOW")
    print("IS 456:2000 / SP 34:1987")
    print("=" * 60)

    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Input file
    input_file = os.path.join(script_dir, "sample_building_beams.csv")

    if not os.path.exists(input_file):
        print(f"✗ Input file not found: {input_file}")
        print("  Please ensure sample_building_beams.csv exists.")
        return

    # Read input beams
    print(f"\nReading: {input_file}")
    with open(input_file, "r") as f:
        reader = csv.DictReader(f)
        beams = list(reader)

    print(f"Found {len(beams)} beams to design")

    # Design all beams
    print("\nDesigning beams...")
    results = []
    for beam in beams:
        try:
            result = design_beam(beam)
            results.append(result)
            status = "✓" if result.is_safe else "✗"
            print(
                f"  {status} {result.beam_id}: {result.bottom_bars}, {result.stirrups}"
            )
        except Exception as e:
            print(f"  ✗ {beam['BeamID']}: Error - {e}")

    # Print schedule
    print_schedule(results)

    # Save to CSV
    output_file = os.path.join(script_dir, "beam_schedule_output.csv")
    save_schedule_csv(results, output_file)

    # Generate DXF files (if available)
    if DXF_AVAILABLE:
        dxf_dir = os.path.join(script_dir, "dxf_output")
        os.makedirs(dxf_dir, exist_ok=True)

        print(f"\nGenerating DXF files in: {dxf_dir}")
        for r in results[:3]:  # First 3 beams as demo
            try:
                # Parse size
                b, D = map(int, r.size.replace("×", "x").split("x"))

                # Create detailing result for DXF
                detail_result = detailing.create_beam_detailing(
                    beam_id=r.beam_id,
                    story=r.story,
                    b=b,
                    D=D,
                    span=r.span,
                    cover=40,
                    fck=25,
                    fy=500,
                    ast_start=r.ast_required,
                    ast_mid=r.ast_required,
                    ast_end=r.ast_required,
                    asc_start=r.asc_required,
                    asc_mid=r.asc_required,
                    asc_end=r.asc_required,
                    stirrup_dia=8,
                    stirrup_spacing_start=r.stirrup_spacing - 25,
                    stirrup_spacing_mid=r.stirrup_spacing,
                    stirrup_spacing_end=r.stirrup_spacing - 25,
                    is_seismic=False,
                )

                dxf_path = os.path.join(dxf_dir, f"{r.beam_id}.dxf")
                if generate_beam_dxf is None:
                    raise RuntimeError("DXF export is not available (ezdxf missing)")
                generate_beam_dxf(detail_result, dxf_path)
                print(f"  ✓ {r.beam_id}.dxf")
            except Exception as e:
                print(f"  ✗ {r.beam_id}: {e}")
    else:
        print("\n(DXF export skipped - install ezdxf for CAD drawings)")

    print("\n" + "=" * 60)
    print("Design complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
