#!/usr/bin/env python3
"""
BMD/SFD Computation Example
===========================

This example demonstrates how to use the compute_bmd_sfd() function
to calculate bending moment and shear force diagrams for different
beam configurations and load types.

Author: Structural Engineering Library
License: MIT
"""

from structural_lib.api import (
    compute_bmd_sfd,
    LoadDefinition,
    LoadType,
)


def example_simply_supported_udl():
    """
    Example 1: Simply Supported Beam with UDL

    Configuration:
    - Span: 6m (6000mm)
    - UDL: 20 kN/m

    Expected results:
    - Max BM at midspan: wL²/8 = 20 × 6² / 8 = 90 kN·m
    - Max SF at supports: wL/2 = 20 × 6 / 2 = 60 kN
    """
    print("=" * 60)
    print("Example 1: Simply Supported Beam with UDL")
    print("=" * 60)

    # Define loads
    loads = [
        LoadDefinition(
            load_type=LoadType.UDL,
            magnitude=20.0,  # kN/m
        )
    ]

    # Compute BMD/SFD
    result = compute_bmd_sfd(
        span_mm=6000,  # 6m span
        support_condition="simply_supported",
        loads=loads,
        num_points=21,  # More points for smooth diagram
    )

    # Print results
    print(f"Span: {result.span_mm} mm")
    print(f"Support: {result.support_condition}")
    print(f"\nMax/Min Values:")
    print(f"  Max BM: {result.max_bm_knm:.2f} kN·m")
    print(f"  Min BM: {result.min_bm_knm:.2f} kN·m")
    print(f"  Max SF: {result.max_sf_kn:.2f} kN")
    print(f"  Min SF: {result.min_sf_kn:.2f} kN")

    print(f"\nCritical Points:")
    for cp in result.critical_points:
        print(f"  {cp.point_type}: x={cp.position_mm:.0f}mm, "
              f"BM={cp.bm_knm:.2f} kN·m, SF={cp.sf_kn:.2f} kN")

    print(f"\nTheoretical (verification):")
    print(f"  Max BM = wL²/8 = {20 * 6**2 / 8:.2f} kN·m")
    print(f"  Max SF = wL/2 = {20 * 6 / 2:.2f} kN")

    return result


def example_simply_supported_point_load():
    """
    Example 2: Simply Supported Beam with Point Load at Center

    Configuration:
    - Span: 8m (8000mm)
    - Point load: 100 kN at midspan

    Expected results:
    - Max BM at midspan: PL/4 = 100 × 8 / 4 = 200 kN·m
    - Max SF at supports: P/2 = 100 / 2 = 50 kN
    """
    print("\n" + "=" * 60)
    print("Example 2: Simply Supported Beam with Point Load")
    print("=" * 60)

    # Define loads
    loads = [
        LoadDefinition(
            load_type=LoadType.POINT,
            magnitude=100.0,  # kN
            position_mm=4000.0,  # At midspan
        )
    ]

    # Compute BMD/SFD
    result = compute_bmd_sfd(
        span_mm=8000,
        support_condition="simply_supported",
        loads=loads,
    )

    print(f"Span: {result.span_mm} mm")
    print(f"\nMax/Min Values:")
    print(f"  Max BM: {result.max_bm_knm:.2f} kN·m")
    print(f"  Max SF: {result.max_sf_kn:.2f} kN")
    print(f"  Min SF: {result.min_sf_kn:.2f} kN")

    print(f"\nCritical Points:")
    for cp in result.critical_points:
        print(f"  {cp.point_type}: x={cp.position_mm:.0f}mm, "
              f"BM={cp.bm_knm:.2f} kN·m, SF={cp.sf_kn:.2f} kN")

    print(f"\nTheoretical (verification):")
    print(f"  Max BM = PL/4 = {100 * 8 / 4:.2f} kN·m")
    print(f"  Max SF = P/2 = {100 / 2:.2f} kN")

    return result


def example_combined_loads():
    """
    Example 3: Simply Supported Beam with Combined Loads

    Configuration:
    - Span: 6m (6000mm)
    - UDL: 15 kN/m
    - Point load: 50 kN at L/3 (2000mm from left)

    Superposition principle applies - each load analyzed separately
    then combined.
    """
    print("\n" + "=" * 60)
    print("Example 3: Combined UDL + Point Load")
    print("=" * 60)

    # Define multiple loads
    loads = [
        LoadDefinition(
            load_type=LoadType.UDL,
            magnitude=15.0,  # kN/m
        ),
        LoadDefinition(
            load_type=LoadType.POINT,
            magnitude=50.0,  # kN
            position_mm=2000.0,  # At L/3
        ),
    ]

    # Compute BMD/SFD
    result = compute_bmd_sfd(
        span_mm=6000,
        support_condition="simply_supported",
        loads=loads,
    )

    print(f"Span: {result.span_mm} mm")
    print(f"Loads: {len(loads)} (UDL + Point)")

    print(f"\nMax/Min Values:")
    print(f"  Max BM: {result.max_bm_knm:.2f} kN·m")
    print(f"  Max SF: {result.max_sf_kn:.2f} kN")
    print(f"  Min SF: {result.min_sf_kn:.2f} kN")

    print(f"\nCritical Points:")
    for cp in result.critical_points:
        print(f"  {cp.point_type}: x={cp.position_mm:.0f}mm, "
              f"BM={cp.bm_knm:.2f} kN·m, SF={cp.sf_kn:.2f} kN")

    return result


def example_cantilever():
    """
    Example 4: Cantilever Beam with UDL

    Configuration:
    - Span: 3m (3000mm)
    - UDL: 25 kN/m

    Expected results:
    - Max BM at fixed end: wL²/2 = 25 × 3² / 2 = 112.5 kN·m (hogging)
    - Max SF at fixed end: wL = 25 × 3 = 75 kN
    """
    print("\n" + "=" * 60)
    print("Example 4: Cantilever Beam with UDL")
    print("=" * 60)

    # Define loads
    loads = [
        LoadDefinition(
            load_type=LoadType.UDL,
            magnitude=25.0,  # kN/m
        )
    ]

    # Compute BMD/SFD
    result = compute_bmd_sfd(
        span_mm=3000,
        support_condition="cantilever",
        loads=loads,
    )

    print(f"Span: {result.span_mm} mm")
    print(f"Support: {result.support_condition}")

    print(f"\nMax/Min Values:")
    print(f"  Max BM: {result.max_bm_knm:.2f} kN·m")
    print(f"  Min BM: {result.min_bm_knm:.2f} kN·m (hogging)")
    print(f"  Max SF: {result.max_sf_kn:.2f} kN")

    print(f"\nCritical Points:")
    for cp in result.critical_points:
        print(f"  {cp.point_type}: x={cp.position_mm:.0f}mm, "
              f"BM={cp.bm_knm:.2f} kN·m, SF={cp.sf_kn:.2f} kN")

    print(f"\nTheoretical (verification):")
    print(f"  Max BM = wL²/2 = {25 * 3**2 / 2:.2f} kN·m (hogging)")
    print(f"  Max SF = wL = {25 * 3:.2f} kN")

    return result


def example_cantilever_point_load():
    """
    Example 5: Cantilever with Point Load at Tip

    Configuration:
    - Span: 4m (4000mm)
    - Point load: 80 kN at free end

    Expected results:
    - Max BM at fixed end: PL = 80 × 4 = 320 kN·m (hogging)
    - Constant SF: P = 80 kN
    """
    print("\n" + "=" * 60)
    print("Example 5: Cantilever with Point Load at Tip")
    print("=" * 60)

    # Define loads
    loads = [
        LoadDefinition(
            load_type=LoadType.POINT,
            magnitude=80.0,  # kN
            position_mm=4000.0,  # At tip
        )
    ]

    # Compute BMD/SFD
    result = compute_bmd_sfd(
        span_mm=4000,
        support_condition="cantilever",
        loads=loads,
    )

    print(f"Span: {result.span_mm} mm")

    print(f"\nMax/Min Values:")
    print(f"  Max BM: {result.max_bm_knm:.2f} kN·m")
    print(f"  Min BM: {result.min_bm_knm:.2f} kN·m (hogging)")
    print(f"  Max SF: {result.max_sf_kn:.2f} kN")

    print(f"\nCritical Points:")
    for cp in result.critical_points:
        print(f"  {cp.point_type}: x={cp.position_mm:.0f}mm, "
              f"BM={cp.bm_knm:.2f} kN·m, SF={cp.sf_kn:.2f} kN")

    print(f"\nTheoretical (verification):")
    print(f"  Max BM = PL = {80 * 4:.2f} kN·m (hogging)")
    print(f"  Constant SF = P = {80:.2f} kN")

    return result


if __name__ == "__main__":
    print("Structural Engineering Library - BMD/SFD Examples")
    print("=" * 60)
    print()

    # Run all examples
    example_simply_supported_udl()
    example_simply_supported_point_load()
    example_combined_loads()
    example_cantilever()
    example_cantilever_point_load()

    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
