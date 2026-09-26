"""Typed public Python workflows: beam schedule, column check and slab check.

Run against an installed checkout wheel with Python 3.11+:
    python Python/examples/canonical_workflows.py

All values are illustrative caller inputs. The slab review references below
are example evidence, not approval for a real project. No files are written.
"""

from __future__ import annotations

import json
from typing import assert_type

from structural_lib.design.is456 import beam, column, slab


def beam_schedule() -> beam.BeamBBSResultV1:
    """Design and detail one beam, then obtain its bar bending schedule."""
    detailing = beam.BeamDetailingOptionsV1(
        standard=beam.DetailingStandard.IS456,
        clear_cover_mm=40,
        tension_bar_diameter_mm=20,
        compression_bar_diameter_mm=16,
        nominal_top_steel_ratio=0.25,
        stirrup_diameter_mm=8,
        stirrup_legs=2,
        stirrup_spacing_support_mm=150,
        stirrup_spacing_mid_mm=200,
    )
    request = beam.input(
        member_id="B1",
        story="L1",
        case_id="ULS-1",
        span_mm=5000,
        b_mm=300,
        D_mm=550,
        d_mm=492,
        fck_nmm2=25,
        fy_nmm2=500,
        mu_knm=150,
        vu_kn=80,
        d_dash_mm=56,
        asv_mm2=detailing.asv_mm2,
        detailing=detailing,
        source_provenance="illustrative design envelope",
    )
    result = beam.design_and_detail(request, detailing_standard=detailing.standard)
    # The detailing owner rejects failed designs and incompatible reinforcement.
    return beam.bbs(result)


def column_request() -> column.ColumnDesignInputV1:
    """Construct explicit typed groups entirely through the public facade."""
    return column.input(
        identity=column.FamilyIdentityV1(
            family_id="column",
            case_id="ULS-1",
            member_id="C1",
            story="L1",
            source_reference="illustrative column actions",
        ),
        geometry=column.ColumnGeometryV1(
            b_mm=300,
            D_mm=450,
            unsupported_length_mm=3000,
            minimum_eccentricity_length_mm=3000,
            end_condition="FIXED_FIXED",
            braced=True,
        ),
        actions=column.ColumnActionsV1(
            pu_kn=800,
            mux_knm=120,
            muy_knm=0,
            m1x_signed_knm=120,
            m2x_signed_knm=120,
            m1y_signed_knm=0,
            m2y_signed_knm=0,
        ),
        materials=column.ColumnMaterialsV1(fck_nmm2=25, fy_nmm2=415),
        reinforcement=column.ColumnReinforcementV1(
            supplied_steel_area_mm2=2400,
            reinforcement_centroid_depth_mm=50,
        ),
    )


def slab_request() -> slab.OneWaySlabInputV1:
    """Check one supplied bar layout with an explicit serviceability basis."""
    return slab.input_one_way(
        identity=slab.FamilyIdentityV1(
            family_id="solid_slab",
            case_id="ULS-1",
            member_id="S1",
            story="L1",
            source_reference="illustrative slab actions",
        ),
        geometry=slab.OneWaySlabGeometryV1(
            short_effective_span_mm=3000,
            long_effective_span_mm=7500,
            thickness_mm=150,
            effective_depth_mm=125,
            strip_width_mm=1000,
        ),
        actions=slab.OneWaySlabActionsV1(factored_area_load_kn_per_m2=10),
        materials=slab.SlabMaterialsV1(fck_nmm2=20, fy_nmm2=415),
        reinforcement=slab.OneWaySlabReinforcementV1(
            main_bar_diameter_mm=10,
            main_bar_spacing_mm=250,
            distribution_bar_diameter_mm=8,
            distribution_bar_spacing_mm=250,
        ),
        serviceability_evidence=slab.SlabServiceabilityEvidenceV1(
            reviewed_base_span_depth_limit=20,
            reviewed_aggregate_modification_factor=1.2,
            serviceability_limit_source_reference="example reviewed limit",
            serviceability_limit_source_is_approved=True,
            qualified_serviceability_acceptance_reference="example review",
            qualified_serviceability_acceptance_acknowledged=True,
        ),
    )


def main() -> None:
    schedule = beam_schedule()
    request = column_request()
    # JSON round-trip keeps the strict input contract and calculation identity.
    restored = column.load(json.loads(request.model_dump_json()))
    checked_column = column.check(restored)
    checked_slab = slab.design_one_way(slab_request())

    # Invalid intake is a structured exception; engineering FAIL is a result.
    invalid = request.model_dump(mode="json")
    invalid["geometry"]["b_mm"] = -300
    try:
        column.load(invalid)
    except column.InputContractError as error:
        rejected = [issue.path for issue in error.issues]
    else:
        raise AssertionError("Invalid width was not rejected")

    # calculation carries the specific result type, so IDEs know these fields.
    column_safe = assert_type(checked_column.calculation["is_safe"], bool)
    assert_type(checked_slab.calculation, slab.CompleteOneWaySlabDesignResult)
    print(
        json.dumps(
            {
                "beam_bbs_weight_kg": schedule.total_weight_kg,
                "column_status": checked_column.engineering_status.value,
                "column_check_passed": column_safe,
                "slab_status": checked_slab.engineering_status.value,
                "review_required": checked_column.qualified_review_required,
                "rejected_fields": rejected,
            },
            indent=2,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
