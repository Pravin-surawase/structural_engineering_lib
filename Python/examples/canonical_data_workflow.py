# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Example: Complete workflow with canonical data format.

This example demonstrates the full pipeline:
1. Load ETABS CSV exports using ETABSAdapter
2. Convert to canonical Pydantic models
3. Cache to JSON for fast reload
4. Process through design calculations
5. Save results

Run with:
    python examples/canonical_data_workflow.py
"""

from __future__ import annotations

from pathlib import Path

# Import the new canonical data format modules
from structural_lib.models import (
    BeamBatchInput,
    BeamBatchResult,
    BeamDesignResult,
    BeamForces,
    BeamGeometry,
    DesignDefaults,
    DesignStatus,
    Point3D,
    SectionProperties,
)
from structural_lib.serialization import (
    generate_all_schemas,
    get_cache_metadata,
    load_geometry,
    save_geometry,
)


def example_manual_input() -> None:
    """Example: Create beam data programmatically."""
    print("\n" + "=" * 60)
    print("Example 1: Manual Input with Pydantic Validation")
    print("=" * 60)

    # Create beam geometry with validation
    section = SectionProperties(
        width_mm=300,
        depth_mm=500,
        fck_mpa=25,  # M25 concrete
        fy_mpa=500,  # Fe500 steel
        cover_mm=40,
    )

    beam = BeamGeometry(
        id="B1_Ground",
        label="B1",
        story="Ground",
        point1=Point3D(x=0, y=0, z=0),
        point2=Point3D(x=5, y=0, z=0),
        section=section,
    )

    # Computed properties are automatically available
    print(f"Beam: {beam.label} ({beam.story})")
    print(f"  Length: {beam.length_m:.2f} m")
    print(f"  Effective depth: {beam.section.effective_depth_mm:.1f} mm")
    print(f"  Is vertical: {beam.is_vertical}")

    # Create forces
    forces = BeamForces(
        id="B1_Ground",
        load_case="1.2DL+1.5LL",
        mu_knm=150,
        vu_kn=100,
        pu_kn=10,
    )

    print(f"\nForces: {forces.load_case}")
    print(f"  Mu = {forces.mu_knm:.1f} kN·m")
    print(f"  Vu = {forces.vu_kn:.1f} kN")

    # Validation examples
    print("\n📋 Validation Examples:")
    try:
        # This will fail - negative moment not allowed
        BeamForces(id="B2", load_case="DL", mu_knm=-100, vu_kn=50)
    except Exception as e:
        print(f"  ❌ Negative moment rejected: {type(e).__name__}")

    try:
        # This will fail - empty ID not allowed
        BeamGeometry(
            id="",  # Empty!
            label="B",
            story="Ground",
            point1=Point3D(x=0, y=0, z=0),
            point2=Point3D(x=1, y=0, z=0),
            section=section,
        )
    except Exception as e:
        print(f"  ❌ Empty ID rejected: {type(e).__name__}")


def example_batch_processing() -> None:
    """Example: Batch processing with BeamBatchInput."""
    print("\n" + "=" * 60)
    print("Example 2: Batch Processing")
    print("=" * 60)

    # Create multiple beams
    defaults = DesignDefaults(fck_mpa=25, fy_mpa=500, cover_mm=40)

    section = SectionProperties(
        width_mm=300,
        depth_mm=500,
        fck_mpa=defaults.fck_mpa,
        fy_mpa=defaults.fy_mpa,
        cover_mm=defaults.cover_mm,
    )

    beams = [
        BeamGeometry(
            id=f"B{i}_Ground",
            label=f"B{i}",
            story="Ground",
            point1=Point3D(x=i * 5.0, y=0, z=0),
            point2=Point3D(x=(i + 1) * 5.0, y=0, z=0),
            section=section,
        )
        for i in range(1, 6)
    ]

    forces = [
        BeamForces(
            id=f"B{i}_Ground",
            load_case="1.2DL+1.5LL",
            mu_knm=100 + i * 25,
            vu_kn=80 + i * 10,
        )
        for i in range(1, 4)  # Only 3 forces - testing unmatched
    ]

    # Create batch input
    batch = BeamBatchInput(beams=beams, forces=forces, defaults=defaults)

    print(f"Total beams: {len(batch.beams)}")
    print(f"Total forces: {len(batch.forces)}")

    # Get merged data (beams with matching forces)
    merged = batch.get_merged_data()
    print(f"\nMerged (beam + forces): {len(merged)}")
    for beam, force in merged:
        print(f"  {beam.label}: Mu={force.mu_knm:.0f} kN·m")

    # Get unmatched beams (returns IDs)
    unmatched_ids = batch.get_unmatched_beams()
    print(f"\nUnmatched beams: {len(unmatched_ids)}")
    for beam_id in unmatched_ids:
        print(f"  {beam_id} (no forces)")


def example_json_caching(tmp_dir: Path) -> None:
    """Example: JSON serialization for caching."""
    print("\n" + "=" * 60)
    print("Example 3: JSON Caching")
    print("=" * 60)

    # Create sample data
    section = SectionProperties(
        width_mm=300, depth_mm=500, fck_mpa=25, fy_mpa=500, cover_mm=40
    )

    beams = [
        BeamGeometry(
            id="B1_Ground",
            label="B1",
            story="Ground",
            point1=Point3D(x=0, y=0, z=0),
            point2=Point3D(x=5, y=0, z=0),
            section=section,
        ),
        BeamGeometry(
            id="B2_Ground",
            label="B2",
            story="Ground",
            point1=Point3D(x=5, y=0, z=0),
            point2=Point3D(x=10, y=0, z=0),
            section=section,
        ),
    ]

    # Save to JSON cache
    cache_file = tmp_dir / "beams_cache.json"
    save_geometry(beams, cache_file)
    print(f"Saved {len(beams)} beams to {cache_file.name}")

    # Check cache metadata without loading
    metadata = get_cache_metadata(cache_file)
    print("\nCache metadata:")
    print(f"  Model type: {metadata['model_type']}")
    print(f"  Count: {metadata['count']}")
    print(f"  Created: {metadata['created_at']}")

    # Load from cache
    loaded = load_geometry(cache_file)
    print(f"\nLoaded {len(loaded)} beams from cache")

    # Verify data integrity
    assert loaded[0].id == beams[0].id
    assert loaded[0].length_m == beams[0].length_m
    print("✅ Data integrity verified")


def example_design_results() -> None:
    """Example: Creating and aggregating design results."""
    print("\n" + "=" * 60)
    print("Example 4: Design Results")
    print("=" * 60)

    # Simulate design results
    results = [
        BeamDesignResult(
            id="B1_Ground",
            load_case="1.2DL+1.5LL",
            status=DesignStatus.PASS,
            mu_knm=150,
            vu_kn=100,
            ast_mm2=1200,
            asv_mm2_m=300,
            utilization=0.75,
        ),
        BeamDesignResult(
            id="B2_Ground",
            load_case="1.2DL+1.5LL",
            status=DesignStatus.PASS,
            mu_knm=200,
            vu_kn=120,
            ast_mm2=1500,
            asv_mm2_m=350,
            utilization=0.85,
        ),
        BeamDesignResult(
            id="B3_Ground",
            load_case="1.2DL+1.5LL",
            status=DesignStatus.FAIL,
            mu_knm=350,
            vu_kn=180,
            ast_mm2=2200,
            asv_mm2_m=450,
            utilization=1.15,
            messages=["Utilization > 1.0", "Consider increasing section"],
        ),
    ]

    # Create batch result
    batch_result = BeamBatchResult.from_results(results)

    print("Design Summary:")
    print(f"  Total beams: {batch_result.total_beams}")
    print(f"  Passed: {batch_result.passed}")
    print(f"  Failed: {batch_result.failed}")
    print(f"  Pass rate: {batch_result.pass_rate:.1f}%")

    print("\nIndividual Results:")
    for r in results:
        status_icon = "✅" if r.is_acceptable else "❌"
        print(f"  {status_icon} {r.id}: {r.status.value} (u={r.utilization:.2f})")
        if r.messages:
            for msg in r.messages:
                print(f"      ⚠️  {msg}")


def example_schema_generation(tmp_dir: Path) -> None:
    """Example: Generate JSON Schemas for documentation."""
    print("\n" + "=" * 60)
    print("Example 5: JSON Schema Generation")
    print("=" * 60)

    schema_dir = tmp_dir / "schemas"
    output_files = generate_all_schemas(schema_dir)

    print(f"Generated {len(output_files)} schema files:")
    for name, path in output_files.items():
        size = path.stat().st_size
        print(f"  {name}: {size} bytes")


def main() -> None:
    """Run all examples."""
    print("=" * 60)
    print("Canonical Data Format - Complete Workflow Example")
    print("=" * 60)

    # Create temp directory for file examples
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Run all examples
        example_manual_input()
        example_batch_processing()
        example_json_caching(tmp_path)
        example_design_results()
        example_schema_generation(tmp_path)

    print("\n" + "=" * 60)
    print("All examples completed successfully! ✅")
    print("=" * 60)


if __name__ == "__main__":
    main()
