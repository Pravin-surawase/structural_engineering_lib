# SPDX-License-Identifier: MIT
"""Explicit builder and maintained example for Building Gravity Workflow V1.

The builder automates only the topology and identity bookkeeping fixed by the
V1 contract.  Every engineering value, source identity, exclusion, design
basis, and numerical balance tolerance remains caller supplied.
"""

from __future__ import annotations

import hashlib
import math
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from structural_lib.core.building_gravity import (
    BuildingModelV1,
    BuildingSourceRecordV1,
    ExcludedGravityActionV1,
    GravityActionCategoryV1,
    GravityApprovedExclusionV1,
    GravityCombinationFactorV1,
    GravityCombinationV1,
    GravityFootingDestinationV1,
    GravityInclusionDispositionV1,
    GravityInclusionRuleV1,
    GravityLoadCaseV1,
    GravityLoadStateV1,
    GravityMaterialV1,
    GravityMemberKindV1,
    GravityMemberV1,
    GravityNodeV1,
    GravityPanelV1,
    GravityPracticalActionV1,
    GravitySectionKindV1,
    GravitySectionV1,
    GravitySourceReferenceV1,
    GravitySupportIdealizationV1,
    LoadModelV1,
    SourceDispositionV1,
)
from structural_lib.core.gravity_workflow import (
    GravityBeamDesignBasisV1,
    GravityBeamReinforcementBasisV1,
    GravityColumnDesignBasisV1,
    GravityFootingDesignBasisV1,
    GravitySlabDesignBasisV1,
    GravityWorkflowRequestV1,
)

__all__ = [
    "RectangularGravityWorkflowBuilderInputV1",
    "build_rectangular_gravity_workflow_request_v1",
    "get_gravity_workflow_example_document_v1",
    "get_gravity_workflow_example_request_v1",
]

_SHA256_PATTERN = r"^[0-9a-f]{64}$"


class RectangularGravityWorkflowBuilderInputV1(BaseModel):
    """All caller-owned values needed to build the fixed rectangular V1 model."""

    model_config = ConfigDict(frozen=True, extra="forbid", allow_inf_nan=False)

    schema_version: Literal["rectangular-gravity-builder-input/v1"] = (
        "rectangular-gravity-builder-input/v1"
    )
    model_id: str = Field(min_length=1, max_length=128)
    project_id: str = Field(min_length=1, max_length=128)
    building_raw_source_hash: str = Field(pattern=_SHA256_PATTERN)
    load_raw_source_hash: str = Field(pattern=_SHA256_PATTERN)
    span_x_mm: float = Field(gt=0)
    span_y_mm: float = Field(gt=0)
    storey_height_mm: float = Field(gt=0)
    slab_thickness_mm: float = Field(gt=0)
    beam_width_mm: float = Field(gt=0)
    beam_depth_mm: float = Field(gt=0)
    column_width_mm: float = Field(gt=0)
    column_depth_mm: float = Field(gt=0)
    concrete_unit_weight_kn_m3: float = Field(gt=0)
    concrete_fck_nmm2: float = Field(gt=0)
    superimposed_dead_load_kn_m2: float = Field(ge=0)
    live_load_kn_m2: float = Field(ge=0)
    live_load_category: str = Field(min_length=1, max_length=128)
    balance_tolerance_kn: float = Field(gt=0, le=1e-3)
    load_basis_reference: GravitySourceReferenceV1
    combination_basis_reference: GravitySourceReferenceV1
    beam_support_idealization: GravitySupportIdealizationV1
    column_support_idealization: GravitySupportIdealizationV1
    inclusion_rules: tuple[GravityInclusionRuleV1, ...]
    combinations: tuple[GravityCombinationV1, GravityCombinationV1]
    practical_actions: tuple[GravityPracticalActionV1, ...]
    approved_exclusions: tuple[GravityApprovedExclusionV1, ...]
    slab_design_bases: tuple[GravitySlabDesignBasisV1, ...]
    beam_design_bases: tuple[GravityBeamDesignBasisV1, ...]
    column_design_bases: tuple[GravityColumnDesignBasisV1, ...]
    footing_design_bases: tuple[GravityFootingDesignBasisV1, ...]

    @model_validator(mode="after")
    def validate_source_identities(self) -> RectangularGravityWorkflowBuilderInputV1:
        if self.load_basis_reference.id == self.combination_basis_reference.id:
            raise ValueError("load and combination source reference IDs must differ")
        if (
            self.beam_support_idealization
            is not GravitySupportIdealizationV1.BEAM_SIMPLY_SUPPORTED
        ):
            raise ValueError(
                "Building Gravity Workflow V1 requires explicitly acknowledged "
                "simply supported beam idealization"
            )
        if (
            self.column_support_idealization
            is not GravitySupportIdealizationV1.COLUMN_BRACED_AXIAL_ONLY
        ):
            raise ValueError(
                "Building Gravity Workflow V1 requires explicitly acknowledged "
                "braced axial-only column idealization"
            )
        return self


def _accepted_source_records(
    entities: tuple[
        GravityNodeV1
        | GravityMaterialV1
        | GravitySectionV1
        | GravityPanelV1
        | GravityMemberV1
        | GravityFootingDestinationV1,
        ...,
    ],
) -> tuple[BuildingSourceRecordV1, ...]:
    return tuple(
        BuildingSourceRecordV1(
            source_index=index,
            source_id=f"rectangular-builder:{entity.id}",
            disposition=SourceDispositionV1.ACCEPTED,
            canonical_id=entity.id,
        )
        for index, entity in enumerate(entities)
    )


def build_rectangular_gravity_workflow_request_v1(
    builder_input: RectangularGravityWorkflowBuilderInputV1,
) -> GravityWorkflowRequestV1:
    """Build the exact V1 topology without inventing engineering defaults."""

    nodes = (
        GravityNodeV1(id="N1", x_mm=0, y_mm=0, z_mm=0),
        GravityNodeV1(id="N2", x_mm=builder_input.span_x_mm, y_mm=0, z_mm=0),
        GravityNodeV1(id="N3", x_mm=0, y_mm=builder_input.span_y_mm, z_mm=0),
        GravityNodeV1(
            id="N4",
            x_mm=builder_input.span_x_mm,
            y_mm=builder_input.span_y_mm,
            z_mm=0,
        ),
        GravityNodeV1(id="N5", x_mm=0, y_mm=0, z_mm=builder_input.storey_height_mm),
        GravityNodeV1(
            id="N6",
            x_mm=builder_input.span_x_mm,
            y_mm=0,
            z_mm=builder_input.storey_height_mm,
        ),
        GravityNodeV1(
            id="N7",
            x_mm=0,
            y_mm=builder_input.span_y_mm,
            z_mm=builder_input.storey_height_mm,
        ),
        GravityNodeV1(
            id="N8",
            x_mm=builder_input.span_x_mm,
            y_mm=builder_input.span_y_mm,
            z_mm=builder_input.storey_height_mm,
        ),
    )
    materials = (
        GravityMaterialV1(
            id="M_CONC",
            unit_weight_kn_m3=builder_input.concrete_unit_weight_kn_m3,
            fck_nmm2=builder_input.concrete_fck_nmm2,
        ),
    )
    sections = (
        GravitySectionV1(
            id="S_SLAB",
            kind=GravitySectionKindV1.SLAB,
            material_id="M_CONC",
            thickness_mm=builder_input.slab_thickness_mm,
        ),
        GravitySectionV1(
            id="S_BEAM",
            kind=GravitySectionKindV1.BEAM,
            material_id="M_CONC",
            width_mm=builder_input.beam_width_mm,
            depth_mm=builder_input.beam_depth_mm,
        ),
        GravitySectionV1(
            id="S_COLUMN",
            kind=GravitySectionKindV1.COLUMN,
            material_id="M_CONC",
            width_mm=builder_input.column_width_mm,
            depth_mm=builder_input.column_depth_mm,
        ),
    )
    panels = (
        GravityPanelV1(
            id="P1",
            corner_node_ids=("N5", "N6", "N7", "N8"),
            section_id="S_SLAB",
            supporting_beam_ids=("B1", "B2"),
            load_path_id="LP_PANEL_P1",
            render_id="RENDER_PANEL_P1",
        ),
    )
    members = (
        GravityMemberV1(
            id="B1",
            kind=GravityMemberKindV1.BEAM,
            start_node_id="N5",
            end_node_id="N6",
            section_id="S_BEAM",
            support_idealization=builder_input.beam_support_idealization,
            load_path_id="LP_BEAM_B1",
            render_id="RENDER_BEAM_B1",
        ),
        GravityMemberV1(
            id="B2",
            kind=GravityMemberKindV1.BEAM,
            start_node_id="N7",
            end_node_id="N8",
            section_id="S_BEAM",
            support_idealization=builder_input.beam_support_idealization,
            load_path_id="LP_BEAM_B2",
            render_id="RENDER_BEAM_B2",
        ),
        *(
            GravityMemberV1(
                id=f"C{index}",
                kind=GravityMemberKindV1.COLUMN,
                start_node_id=f"N{index}",
                end_node_id=f"N{index + 4}",
                section_id="S_COLUMN",
                support_idealization=builder_input.column_support_idealization,
                load_path_id=f"LP_COLUMN_C{index}",
                render_id=f"RENDER_COLUMN_C{index}",
            )
            for index in range(1, 5)
        ),
    )
    footing_destinations = tuple(
        GravityFootingDestinationV1(
            id=f"F{index}",
            column_id=f"C{index}",
            node_id=f"N{index}",
            load_path_id=f"LP_FOOTING_F{index}",
        )
        for index in range(1, 5)
    )
    entities: tuple[
        GravityNodeV1
        | GravityMaterialV1
        | GravitySectionV1
        | GravityPanelV1
        | GravityMemberV1
        | GravityFootingDestinationV1,
        ...,
    ] = (*nodes, *materials, *sections, *panels, *members, *footing_destinations)
    building = BuildingModelV1(
        model_id=builder_input.model_id,
        project_id=builder_input.project_id,
        raw_source_hash=builder_input.building_raw_source_hash,
        nodes=nodes,
        materials=materials,
        sections=sections,
        panels=panels,
        members=members,
        footing_destinations=footing_destinations,
        source_records=_accepted_source_records(entities),
    )

    loads = LoadModelV1(
        model_hash=building.accepted_model_hash,
        raw_source_hash=builder_input.load_raw_source_hash,
        superimposed_dead_load_kn_m2=(builder_input.superimposed_dead_load_kn_m2),
        live_load_kn_m2=builder_input.live_load_kn_m2,
        live_load_category=builder_input.live_load_category,
        balance_tolerance_kn=builder_input.balance_tolerance_kn,
        source_references=(
            builder_input.load_basis_reference,
            builder_input.combination_basis_reference,
        ),
        inclusion_rules=builder_input.inclusion_rules,
        combinations=builder_input.combinations,
        practical_actions=builder_input.practical_actions,
        approved_exclusions=builder_input.approved_exclusions,
    )
    return GravityWorkflowRequestV1(
        model_hash=building.accepted_model_hash,
        load_model_hash=loads.load_model_hash,
        building=building,
        loads=loads,
        slab_design_bases=builder_input.slab_design_bases,
        beam_design_bases=builder_input.beam_design_bases,
        column_design_bases=builder_input.column_design_bases,
        footing_design_bases=builder_input.footing_design_bases,
    )


def _example_hash(label: str) -> str:
    return hashlib.sha256(
        f"structural-lib-gravity-example-v1:{label}".encode()
    ).hexdigest()


def _example_exclusions(source_ref_id: str) -> tuple[GravityApprovedExclusionV1, ...]:
    reasons = {
        ExcludedGravityActionV1.WALL: "The open-hall example has no wall actions.",
        ExcludedGravityActionV1.FACADE: "The open-hall example has no facade actions.",
        ExcludedGravityActionV1.EQUIPMENT: "No equipment action is included in the example.",
        ExcludedGravityActionV1.TANK: "No tank action is included in the example.",
        ExcludedGravityActionV1.STAIR: "No stair action is included in the example.",
        ExcludedGravityActionV1.ROOF_SPECIAL: "No special roof action is included in the example.",
        ExcludedGravityActionV1.LATERAL: "Building Gravity Workflow V1 excludes all lateral action.",
        ExcludedGravityActionV1.SOIL: "Soil-pressure generation is excluded; the footing adapter receives an external allowable pressure basis.",
        ExcludedGravityActionV1.FOOTING_SELF_WEIGHT: "Footing self-weight is external to the superstructure ledger and included in each complete footing action.",
        ExcludedGravityActionV1.OVERBURDEN: "Overburden is external to the superstructure ledger and included in each complete footing action.",
        ExcludedGravityActionV1.LIVE_LOAD_REDUCTION: "No live-load reduction is applied in this example.",
    }
    return tuple(
        GravityApprovedExclusionV1(
            category=category,
            reason=reasons[category],
            source_ref_id=source_ref_id,
        )
        for category in ExcludedGravityActionV1
    )


def get_gravity_workflow_example_request_v1() -> GravityWorkflowRequestV1:
    """Return a runnable, deterministic open-hall demonstration request."""

    load_reference = GravitySourceReferenceV1(
        id="DEMO_PROJECT_BASIS",
        title="Demonstration open-hall gravity basis",
        reference="Maintained software example; not a real project design basis",
        source_hash=_example_hash("project-basis"),
    )
    combination_reference = GravitySourceReferenceV1(
        id="DEMO_COMBINATION_BASIS",
        title="Demonstration DL plus LL combinations",
        reference="Building Gravity Workflow V1 fixed service and ULS combinations",
        source_hash=_example_hash("combination-basis"),
    )
    column_steel_area_mm2 = math.pi * 20.0**2
    return build_rectangular_gravity_workflow_request_v1(
        RectangularGravityWorkflowBuilderInputV1(
            model_id="DEMO_OPEN_HALL_01",
            project_id="DEMONSTRATION_ONLY",
            building_raw_source_hash=_example_hash("building-source"),
            load_raw_source_hash=_example_hash("load-source"),
            span_x_mm=10_000,
            span_y_mm=4_000,
            storey_height_mm=3_000,
            slab_thickness_mm=150,
            beam_width_mm=300,
            beam_depth_mm=700,
            column_width_mm=300,
            column_depth_mm=300,
            concrete_unit_weight_kn_m3=25,
            concrete_fck_nmm2=25,
            superimposed_dead_load_kn_m2=1.5,
            live_load_kn_m2=3.0,
            live_load_category="DEMONSTRATION_OCCUPANCY",
            balance_tolerance_kn=1e-9,
            load_basis_reference=load_reference,
            combination_basis_reference=combination_reference,
            beam_support_idealization=(
                GravitySupportIdealizationV1.BEAM_SIMPLY_SUPPORTED
            ),
            column_support_idealization=(
                GravitySupportIdealizationV1.COLUMN_BRACED_AXIAL_ONLY
            ),
            inclusion_rules=tuple(
                GravityInclusionRuleV1(
                    category=category,
                    disposition=disposition,
                    source_ref_id=load_reference.id,
                )
                for category, disposition in (
                    (
                        GravityActionCategoryV1.SLAB_SELF_WEIGHT,
                        GravityInclusionDispositionV1.GENERATED,
                    ),
                    (
                        GravityActionCategoryV1.SLAB_SUPERIMPOSED_DEAD,
                        GravityInclusionDispositionV1.SUPPLIED,
                    ),
                    (
                        GravityActionCategoryV1.BEAM_SELF_WEIGHT,
                        GravityInclusionDispositionV1.GENERATED,
                    ),
                    (
                        GravityActionCategoryV1.COLUMN_SELF_WEIGHT,
                        GravityInclusionDispositionV1.GENERATED,
                    ),
                    (
                        GravityActionCategoryV1.LIVE_OCCUPANCY,
                        GravityInclusionDispositionV1.SUPPLIED,
                    ),
                )
            ),
            combinations=(
                GravityCombinationV1(
                    id="SERVICE_DL_LL",
                    state=GravityLoadStateV1.SERVICE,
                    factors=(
                        GravityCombinationFactorV1(
                            case_id=GravityLoadCaseV1.DEAD, factor=1.0
                        ),
                        GravityCombinationFactorV1(
                            case_id=GravityLoadCaseV1.LIVE, factor=1.0
                        ),
                    ),
                    source_ref_id=combination_reference.id,
                ),
                GravityCombinationV1(
                    id="ULS_1_5_DL_LL",
                    state=GravityLoadStateV1.FACTORED,
                    factors=(
                        GravityCombinationFactorV1(
                            case_id=GravityLoadCaseV1.DEAD, factor=1.5
                        ),
                        GravityCombinationFactorV1(
                            case_id=GravityLoadCaseV1.LIVE, factor=1.5
                        ),
                    ),
                    source_ref_id=combination_reference.id,
                ),
            ),
            practical_actions=(),
            approved_exclusions=_example_exclusions(load_reference.id),
            slab_design_bases=(
                GravitySlabDesignBasisV1(
                    panel_id="P1",
                    d_mm=125,
                    fy_nmm2=415,
                    main_bar_diameter_mm=10,
                    main_bar_spacing_mm=100,
                    distribution_bar_diameter_mm=8,
                    distribution_bar_spacing_mm=150,
                    reviewed_base_span_depth_limit=20,
                    reviewed_aggregate_modification_factor=2,
                    serviceability_limit_source_reference=(
                        "Demonstration reviewed span-depth basis"
                    ),
                    serviceability_limit_source_is_approved=True,
                    qualified_serviceability_acceptance_reference=(
                        "Demonstration-only qualified review acknowledgement"
                    ),
                    qualified_serviceability_acceptance_acknowledged=True,
                    effective_depth_source_reference=(
                        "Demonstration 125 mm effective depth"
                    ),
                ),
            ),
            beam_design_bases=tuple(
                GravityBeamDesignBasisV1(
                    beam_id=beam_id,
                    d_mm=650,
                    fy_nmm2=415,
                    asv_mm2=100,
                    ast_mm2_for_shear=2_454,
                    cover_mm=25,
                    stirrup_dia_mm=8,
                    effective_depth_source_reference=(
                        "Demonstration 650 mm effective depth"
                    ),
                    reinforcement_basis=GravityBeamReinforcementBasisV1(
                        permitted_diameters_mm=(12, 16, 20, 25, 32),
                        maximum_layers=2,
                        maximum_bars_per_layer=8,
                        nominal_max_aggregate_size_mm=20,
                        effective_depth_tolerance_mm=5,
                        objective="min_area",
                        selection_source_reference=(
                            "Demonstration bar-selection constraints; not a "
                            "supplied reinforcement schedule"
                        ),
                    ),
                )
                for beam_id in ("B1", "B2")
            ),
            column_design_bases=tuple(
                GravityColumnDesignBasisV1(
                    column_id=column_id,
                    fy_nmm2=415,
                    Asc_mm2=column_steel_area_mm2,
                    d_prime_mm=50,
                    end_condition="FIXED_FIXED",
                    end_condition_source_reference=(
                        "Demonstration braced fixed-fixed basis"
                    ),
                    reinforcement_source_reference=(
                        "Demonstration four 20 mm longitudinal bars"
                    ),
                    braced_acknowledged=True,
                    axial_only_action_acknowledged=True,
                )
                for column_id in ("C1", "C2", "C3", "C4")
            ),
            footing_design_bases=tuple(
                GravityFootingDesignBasisV1(
                    footing_id=footing_id,
                    complete_service_axial_load_kn=130,
                    service_load_combination_id=(
                        "SERVICE_DL_LL_WITH_EXTERNAL_FOOTING_ACTIONS"
                    ),
                    service_load_basis=("includes_footing_self_weight_and_overburden"),
                    service_load_origin="provided",
                    complete_factored_axial_load_kn=195,
                    factored_load_combination_id=(
                        "ULS_1_5_DL_LL_WITH_EXTERNAL_FOOTING_ACTIONS"
                    ),
                    allowable_soil_pressure_kpa=200,
                    allowable_soil_pressure_source_reference=(
                        "Demonstration allowable pressure; not geotechnical approval"
                    ),
                    allowable_soil_pressure_origin="provided",
                    allowable_soil_pressure_is_externally_approved=True,
                    footing_type="SQUARE",
                    minimum_overall_thickness_mm=300,
                    maximum_overall_thickness_mm=600,
                    thickness_increment_mm=50,
                    effective_depth_offset_l_mm=75,
                    effective_depth_offset_b_mm=75,
                    footing_concrete_fck_nmm2=25,
                    steel_fy_nmm2=415,
                    effective_supporting_area_a1_mm2=360_000,
                    effective_supporting_area_basis="largest_frustum_1v_2h",
                    effective_supporting_area_origin="provided",
                    effective_supporting_area_is_approved=True,
                    dowel_count=4,
                    dowel_diameter_mm=16,
                    column_longitudinal_bar_diameter_mm=20,
                    available_dowel_development_length_into_footing_mm=700,
                    available_dowel_development_length_into_column_mm=700,
                    nominal_cover_mm=50,
                    cover_exposure_basis="Demonstration footing cover basis",
                    cover_exposure_basis_is_approved=True,
                    nominal_max_aggregate_size_mm=20,
                    lower_bottom_bar_direction="L",
                    upper_bottom_bar_direction="B",
                    permitted_bottom_bar_diameters_mm=(10, 12, 16, 20),
                    footing_bottom_bar_type="deformed",
                )
                for footing_id in ("F1", "F2", "F3", "F4")
            ),
        )
    )


def get_gravity_workflow_example_document_v1() -> dict[str, Any]:
    """Return runnable JSON input without output-only computed hash fields."""

    return get_gravity_workflow_example_request_v1().model_dump(
        mode="json",
        exclude={
            "building": {"accepted_model_hash": True},
            "loads": {"load_model_hash": True},
        },
    )
