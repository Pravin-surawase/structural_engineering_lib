#!/usr/bin/env python
"""Professional Engineering Workflow Example.

This example demonstrates the complete professional workflow using the
v0.18+ modules:
- BeamInput: Structured input validation
- Audit trail: SHA-256 verification and immutable logs
- Calculation reports: HTML/JSON/Markdown output
- Testing strategies: Quality assurance

Example Use Case:
A structural engineer needs to:
1. Define beam parameters with validation
2. Run IS 456 design calculations
3. Generate auditable reports
4. Verify calculation integrity
5. Run regression tests

This workflow ensures:
- Full traceability for professional liability
- Reproducible calculations with SHA-256 verification
- Print-ready reports for client delivery
- Quality assurance through property-based testing
"""

from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path

from structural_lib import api
from structural_lib.audit import AuditTrail, CalculationHash
from structural_lib.calculation_report import generate_calculation_report
from structural_lib.inputs import (
    BeamGeometryInput,
    BeamInput,
    LoadsInput,
    MaterialsInput,
)
from structural_lib.testing_strategies import (
    AREA_TOLERANCE,
    BeamDesignInvariants,
    PropertyBasedTester,
)


def main() -> None:
    """Run the professional workflow example."""
    print("=" * 60)
    print("Professional Engineering Workflow - IS 456 Beam Design")
    print("=" * 60)

    # =========================================================================
    # STEP 1: Define inputs with structured validation
    # =========================================================================
    print("\n📋 STEP 1: Input Definition & Validation")
    print("-" * 40)

    # Create structured beam input using dataclasses
    geometry = BeamGeometryInput(
        b_mm=300.0,
        D_mm=600.0,
        span_mm=6000.0,
        cover_mm=40.0,
    )
    materials = MaterialsInput(fck_nmm2=30.0, fy_nmm2=500.0)
    loads = LoadsInput(mu_knm=250.0, vu_kn=180.0)

    beam = BeamInput(
        beam_id="B1-L2",
        story="GF",
        geometry=geometry,
        materials=materials,
        loads=loads,
    )

    # Display validated inputs
    print(f"✅ Input validation passed: {beam.beam_id}")
    print(f"   Geometry: {geometry.b_mm}×{geometry.D_mm} mm")
    print(f"   Materials: M{int(materials.fck_nmm2)}/Fe{int(materials.fy_nmm2)}")
    print(f"   Loads: Mu={loads.mu_knm} kN·m, Vu={loads.vu_kn} kN")

    # =========================================================================
    # STEP 2: Run design calculations
    # =========================================================================
    print("\n🔧 STEP 2: Design Calculations")
    print("-" * 40)

    # Run IS 456 design using the API
    result = api.design_beam_is456(
        units="IS456",
        case_id="CASE-1",
        b_mm=geometry.b_mm,
        D_mm=geometry.D_mm,
        d_mm=geometry.effective_depth,
        fck_nmm2=materials.fck_nmm2,
        fy_nmm2=materials.fy_nmm2,
        mu_knm=loads.mu_knm,
        vu_kn=loads.vu_kn,
    )

    print(f"   Flexure: Ast_req = {result.flexure.ast_required:.0f} mm²")
    print(f"   Shear: Stirrup spacing = {result.shear.spacing:.0f} mm")
    print(f"   Status: {'✅ SAFE' if result.is_ok else '❌ UNSAFE'}")

    # =========================================================================
    # STEP 3: Create audit trail for traceability
    # =========================================================================
    print("\n📝 STEP 3: Audit Trail Creation")
    print("-" * 40)

    # Create input/output dictionaries for hashing
    inputs_dict = {
        "beam_id": beam.beam_id,
        "story": beam.story,
        "geometry": geometry.to_dict(),
        "materials": materials.to_dict(),
        "loads": loads.to_dict(),
    }
    outputs_dict = {
        "ast_required": result.flexure.ast_required,
        "pt_provided": result.flexure.pt_provided,
        "stirrup_spacing": result.shear.spacing,
        "is_ok": result.is_ok,
    }

    # Create calculation hash for verification
    calc_hash = CalculationHash.from_calculation(inputs_dict, outputs_dict)

    # Create audit trail
    trail = AuditTrail(project_id="PRJ-2026-001")
    entry = trail.log_design(
        beam_id=beam.beam_id,
        story=beam.story,
        inputs=inputs_dict,
        outputs=outputs_dict,
        metadata={"notes": "Ground floor beam, exposed to weather"},
    )

    print(f"   Calculation hash: {calc_hash.combined_hash[:16]}...")
    print(f"   Timestamp: {entry.timestamp}")
    print(f"   Version: {trail.library_version}")

    # Verify integrity
    is_verified = calc_hash.verify_inputs(inputs_dict) and calc_hash.verify_outputs(
        outputs_dict
    )
    print(f"   Integrity: {'✅ Verified' if is_verified else '❌ Failed'}")

    # =========================================================================
    # STEP 4: Generate professional reports
    # =========================================================================
    print("\n📄 STEP 4: Report Generation")
    print("-" * 40)

    # Generate report from result
    report = generate_calculation_report(
        result=result,
        beam_id=beam.beam_id,
        story=beam.story,
        project_info={
            "project_name": "Multi-Story Residential Building",
            "project_number": "PRJ-2026-001",
            "client_name": "ABC Developers Ltd.",
            "engineer_name": "Demo User",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
    )

    # Save reports to temp directory for demo
    with tempfile.TemporaryDirectory() as tmpdir:
        html_path = Path(tmpdir) / "report.html"
        json_path = Path(tmpdir) / "report.json"
        md_path = Path(tmpdir) / "report.md"

        # Export all formats
        report.export_html(html_path)
        report.export_json(json_path)
        report.export_markdown(md_path)

        print(f"   HTML report: {len(html_path.read_text())} bytes")
        print(f"   JSON report: {len(json_path.read_text())} bytes")
        print(f"   Markdown report: {len(md_path.read_text())} bytes")

    # =========================================================================
    # STEP 5: Quality assurance with testing strategies
    # =========================================================================
    print("\n🧪 STEP 5: Quality Assurance")
    print("-" * 40)

    # Check engineering invariants
    print("   Invariant checks:")
    invariants = BeamDesignInvariants.check_all(result)
    for passed, message in invariants:
        status = "✅" if passed else "❌"
        print(f"      {status} {message}")

    # Demonstrate tolerance-based comparison
    print("\n   Tolerance comparisons:")
    expected_ast = result.flexure.ast_required
    actual_ast = expected_ast * 1.0005  # 0.05% difference
    within_tolerance = AREA_TOLERANCE.is_close(actual_ast, expected_ast)
    print(f"      Area tolerance (0.1%): {AREA_TOLERANCE}")
    print(f"      Expected: {expected_ast:.2f}, Actual: {actual_ast:.2f}")
    print(f"      Within tolerance: {'✅ Yes' if within_tolerance else '❌ No'}")

    # Demonstrate property-based testing (quick example)
    print("\n   Property-based testing (3 random cases):")
    tester = PropertyBasedTester(seed=42)
    cases = tester.generate_beam_cases(n=3)
    for i, case in enumerate(cases):
        print(
            f"      Case {i+1}: b={case.inputs['b_mm']:.0f}, D={case.inputs['D_mm']:.0f}, fck={case.inputs['fck_nmm2']}"
        )

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 60)
    print("✅ Professional Workflow Complete")
    print("=" * 60)
    print(
        """
Summary:
1. ✅ Input validated with BeamInput dataclass
2. ✅ Design calculated with IS 456 API
3. ✅ Audit trail created with SHA-256 hash
4. ✅ Reports generated in HTML/JSON/Markdown
5. ✅ Quality assured with invariant checks

This workflow ensures:
- Full traceability for professional liability
- Reproducible calculations with version control
- Print-ready reports for client delivery
- Quality assurance through automated testing
"""
    )


if __name__ == "__main__":
    main()
