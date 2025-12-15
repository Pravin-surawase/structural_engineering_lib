"""
Simple Examples for Beginners
=============================

This file contains simple, copy-paste examples for common tasks.
Each function can be run independently.

Usage:
    python simple_examples.py
"""

from structural_lib import flexure, shear, detailing
import math


def example_1_basic_flexure():
    """
    Example 1: Design a Simply Supported Beam for Bending

    Problem: A beam 300mm wide and 500mm deep carries a
    factored moment of 150 kN·m. Design using M25/Fe500.
    """
    print("\n" + "=" * 50)
    print("EXAMPLE 1: Basic Flexure Design")
    print("=" * 50)

    # Inputs
    b = 300  # Width (mm)
    D = 500  # Overall depth (mm)
    cover = 40  # Clear cover (mm)
    stirrup = 8  # Stirrup diameter (mm)
    d = D - cover - stirrup - 8  # Effective depth (assuming 16mm bars)

    fck = 25  # Concrete M25
    fy = 500  # Steel Fe500
    Mu = 150  # Factored moment (kN·m)

    # Design
    result = flexure.design_singly_reinforced(b, d, D, Mu, fck, fy)

    # Output
    print(f"Section: {b} × {D} mm")
    print(f"Effective depth d = {d} mm")
    print(f"Materials: M{fck} / Fe{fy}")
    print(f"Applied moment Mu = {Mu} kN·m")
    print(f"Limiting moment Mu_lim = {result.mu_lim:.2f} kN·m")
    print(f"Required steel Ast = {result.ast_required:.0f} mm²")
    print(f"Steel percentage pt = {result.pt_provided:.2f}%")

    # Select bars
    bar_dia = 16
    bar_area = math.pi * (bar_dia / 2) ** 2
    n_bars = math.ceil(result.ast_required / bar_area)
    print(f"\nProvide: {n_bars} nos. of {bar_dia}mm bars")
    print(f"Area provided = {n_bars * bar_area:.0f} mm²")


def example_2_shear_design():
    """
    Example 2: Design Stirrups for Shear

    Problem: The beam in Example 1 has a factored shear
    of 100 kN at support. Design stirrups.
    """
    print("\n" + "=" * 50)
    print("EXAMPLE 2: Shear Design")
    print("=" * 50)

    # Inputs from previous example
    b = 300
    d = 444
    fck = 25
    fy = 500
    Vu = 100  # Factored shear (kN)

    # Stirrup details
    stirrup_dia = 8
    legs = 2
    Asv = legs * math.pi * (stirrup_dia / 2) ** 2

    # Tension steel percentage (from Example 1)
    Ast = 950  # Approximate
    pt = (Ast * 100) / (b * d)

    # Design
    result = shear.design_shear(Vu, b, d, fck, fy, Asv, pt)

    # Output
    print(f"Shear force Vu = {Vu} kN")
    print(f"Nominal shear stress τv = {result.tv:.3f} N/mm²")
    print(f"Design shear strength τc = {result.tc:.3f} N/mm²")
    print(f"Maximum shear τc,max = {result.tc_max:.3f} N/mm²")
    print(f"Stirrup area Asv = {Asv:.1f} mm² ({legs}L-{stirrup_dia}mm)")
    print(f"Required spacing = {result.spacing:.0f} mm")

    # Practical spacing
    sv_practical = (result.spacing // 25) * 25
    print(f"\nProvide: 2L-{stirrup_dia}φ @ {int(sv_practical)} mm c/c")


def example_3_development_length():
    """
    Example 3: Calculate Development Length

    Problem: Calculate the development length for 16mm
    bars in M25 concrete with Fe500 steel.
    """
    print("\n" + "=" * 50)
    print("EXAMPLE 3: Development Length")
    print("=" * 50)

    bar_dia = 16
    fck = 25
    fy = 500

    # Calculate Ld
    Ld = detailing.calculate_development_length(bar_dia, fck, fy)

    # Bond stress
    tau_bd = detailing.get_bond_stress(fck)

    print(f"Bar diameter = {bar_dia} mm")
    print(f"Concrete grade = M{fck}")
    print(f"Steel grade = Fe{fy}")
    print(f"Bond stress τbd = {tau_bd:.2f} N/mm²")
    print(f"Development length Ld = {Ld:.0f} mm")
    print(f"In terms of bar diameter = {Ld/bar_dia:.0f}φ")


def example_4_lap_length():
    """
    Example 4: Calculate Lap Length

    Problem: Calculate lap length for the bars in Example 3,
    considering both normal and seismic conditions.
    """
    print("\n" + "=" * 50)
    print("EXAMPLE 4: Lap Length")
    print("=" * 50)

    bar_dia = 16
    fck = 25
    fy = 500

    # Normal condition (non-seismic)
    lap_normal = detailing.calculate_lap_length(bar_dia, fck, fy, is_seismic=False)

    # Seismic condition (IS 13920)
    lap_seismic = detailing.calculate_lap_length(bar_dia, fck, fy, is_seismic=True)

    print(f"Bar diameter = {bar_dia} mm")
    print(f"Normal lap length = {lap_normal:.0f} mm ({lap_normal/bar_dia:.0f}φ)")
    print(f"Seismic lap length = {lap_seismic:.0f} mm ({lap_seismic/bar_dia:.0f}φ)")
    print("\nNote: Seismic lap = 1.5 × Ld (IS 13920 requirement)")


def example_5_bar_spacing():
    """
    Example 5: Check Bar Spacing

    Problem: Check if 4 nos. of 16mm bars can fit in a
    300mm wide beam with 40mm cover and 8mm stirrups.
    """
    print("\n" + "=" * 50)
    print("EXAMPLE 5: Bar Spacing Check")
    print("=" * 50)

    b = 300
    cover = 40
    stirrup_dia = 8
    bar_dia = 16
    bar_count = 4

    # Calculate actual spacing
    spacing = detailing.calculate_bar_spacing(b, cover, stirrup_dia, bar_dia, bar_count)

    # Minimum required spacing
    min_spacing = detailing.get_min_spacing(bar_dia)

    print(f"Beam width b = {b} mm")
    print(f"Clear cover = {cover} mm")
    print(f"Stirrup = {stirrup_dia} mm")
    print(f"Main bars = {bar_count} nos. of {bar_dia}mm")
    print(f"Calculated spacing = {spacing:.0f} mm c/c")
    print(f"Minimum required = {min_spacing:.0f} mm")

    if spacing >= min_spacing:
        print("\n✓ Spacing is ADEQUATE")
    else:
        print("\n✗ Spacing is INADEQUATE - use larger section or fewer bars")


def example_6_doubly_reinforced():
    """
    Example 6: Doubly Reinforced Beam Design

    Problem: A beam 300×500mm carries Mu = 250 kN·m.
    The limiting moment is exceeded, design compression steel.
    """
    print("\n" + "=" * 50)
    print("EXAMPLE 6: Doubly Reinforced Design")
    print("=" * 50)

    b = 300
    D = 500
    d = 444
    d_dash = 56  # Distance to compression steel center
    fck = 25
    fy = 500
    Mu = 250  # This exceeds Mu_lim

    # Check Mu_lim
    Mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)
    print(f"Applied Mu = {Mu} kN·m")
    print(f"Limiting Mu_lim = {Mu_lim:.2f} kN·m")
    print("Mu > Mu_lim: Doubly reinforced section required")

    # Design
    result = flexure.design_doubly_reinforced(b, d, d_dash, D, Mu, fck, fy)

    print(f"\nTension steel Ast = {result.ast_required:.0f} mm²")
    print(f"Compression steel Asc = {result.asc_required:.0f} mm²")

    # Select bars
    n_tension = math.ceil(result.ast_required / 314.2)  # 20mm bars
    n_compression = max(2, math.ceil(result.asc_required / 113.1))  # 12mm bars

    print("\nProvide:")
    print(f"  Bottom (tension): {n_tension}-20φ")
    print(f"  Top (compression): {n_compression}-12φ")


def example_7_complete_design():
    """
    Example 7: Complete Beam Design Summary

    Combines all the above into one comprehensive example.
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Complete Beam Design (IS 456:2000)")
    print("=" * 60)

    # GIVEN DATA
    print("\n--- GIVEN DATA ---")
    beam_id = "B1"
    b, D = 300, 500
    span = 4000
    cover = 40
    fck, fy = 25, 500
    Mu = 150  # kN·m
    Vu = 100  # kN

    print(f"Beam: {beam_id}")
    print(f"Size: {b} × {D} mm, Span: {span} mm")
    print(f"Materials: M{fck}/Fe{fy}")
    print(f"Loads: Mu = {Mu} kN·m, Vu = {Vu} kN")

    # DESIGN
    stirrup_dia = 8
    main_bar = 16
    d = D - cover - stirrup_dia - main_bar / 2

    print("\n--- FLEXURE DESIGN ---")
    flex = flexure.design_singly_reinforced(b, d, D, Mu, fck, fy)
    n_bars = math.ceil(flex.ast_required / (math.pi * (main_bar / 2) ** 2))
    Ast_prov = n_bars * math.pi * (main_bar / 2) ** 2
    print(f"Ast required = {flex.ast_required:.0f} mm²")
    print(f"Provide: {n_bars}-{main_bar}φ ({Ast_prov:.0f} mm²)")

    print("\n--- SHEAR DESIGN ---")
    Asv = 2 * math.pi * (stirrup_dia / 2) ** 2
    pt = Ast_prov * 100 / (b * d)
    shear_res = shear.design_shear(Vu, b, d, fck, fy, Asv, pt)
    sv = (shear_res.spacing // 25) * 25
    print(f"τv = {shear_res.tv:.3f} N/mm², τc = {shear_res.tc:.3f} N/mm²")
    print(f"Provide: 2L-{stirrup_dia}φ @ {int(sv)} mm c/c")

    print("\n--- DETAILING ---")
    Ld = detailing.calculate_development_length(main_bar, fck, fy)
    lap = detailing.calculate_lap_length(main_bar, fck, fy)
    spacing = detailing.calculate_bar_spacing(b, cover, stirrup_dia, main_bar, n_bars)
    print(f"Ld = {Ld:.0f} mm, Lap = {lap:.0f} mm")
    print(
        f"Bar spacing = {spacing:.0f} mm (min = {detailing.get_min_spacing(main_bar):.0f} mm)"
    )

    print("\n--- SUMMARY ---")
    print(f"Beam {beam_id}: {b}×{D} mm")
    print(
        f"Bottom: {n_bars}-{main_bar}φ | Top: 2-12φ | Stirrups: 2L-{stirrup_dia}φ@{int(sv)}"
    )
    print(f"Status: {'✓ OK' if flex.is_safe and shear_res.is_safe else '✗ Check'}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("STRUCTURAL ENGINEERING LIBRARY - BEGINNER EXAMPLES")
    print("=" * 60)

    example_1_basic_flexure()
    example_2_shear_design()
    example_3_development_length()
    example_4_lap_length()
    example_5_bar_spacing()
    example_6_doubly_reinforced()
    example_7_complete_design()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
