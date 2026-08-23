"""Hand-checkable contract and load-ledger tests for Building Gravity V1."""

from __future__ import annotations

import math

import pytest
from pydantic import ValidationError

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
    GravityPracticalActionKindV1,
    GravityPracticalActionUnitsV1,
    GravityPracticalActionV1,
    GravitySectionKindV1,
    GravitySectionV1,
    GravitySourceReferenceV1,
    GravitySupportIdealizationV1,
    LoadModelV1,
    SourceDispositionV1,
)
from structural_lib.services.gravity_loads import (
    GravityBalanceBoundaryV1,
    GravityLedgerStageV1,
    GravityLoadLedgerError,
    GravityLoadLedgerV1,
    build_gravity_load_ledger_v1,
)


def _building(*, unit_weight_kn_m3: float = 25.0) -> BuildingModelV1:
    nodes = (
        GravityNodeV1(id="N1", x_mm=0, y_mm=0, z_mm=0),
        GravityNodeV1(id="N2", x_mm=6000, y_mm=0, z_mm=0),
        GravityNodeV1(id="N3", x_mm=0, y_mm=4000, z_mm=0),
        GravityNodeV1(id="N4", x_mm=6000, y_mm=4000, z_mm=0),
        GravityNodeV1(id="N5", x_mm=0, y_mm=0, z_mm=3000),
        GravityNodeV1(id="N6", x_mm=6000, y_mm=0, z_mm=3000),
        GravityNodeV1(id="N7", x_mm=0, y_mm=4000, z_mm=3000),
        GravityNodeV1(id="N8", x_mm=6000, y_mm=4000, z_mm=3000),
    )
    materials = (
        GravityMaterialV1(
            id="M_CONC", unit_weight_kn_m3=unit_weight_kn_m3, fck_nmm2=25
        ),
    )
    sections = (
        GravitySectionV1(
            id="S_SLAB",
            kind=GravitySectionKindV1.SLAB,
            material_id="M_CONC",
            thickness_mm=150,
        ),
        GravitySectionV1(
            id="S_BEAM",
            kind=GravitySectionKindV1.BEAM,
            material_id="M_CONC",
            width_mm=300,
            depth_mm=500,
        ),
        GravitySectionV1(
            id="S_COLUMN",
            kind=GravitySectionKindV1.COLUMN,
            material_id="M_CONC",
            width_mm=300,
            depth_mm=300,
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
            support_idealization=GravitySupportIdealizationV1.BEAM_SIMPLY_SUPPORTED,
            load_path_id="LP_BEAM_B1",
            render_id="RENDER_BEAM_B1",
        ),
        GravityMemberV1(
            id="B2",
            kind=GravityMemberKindV1.BEAM,
            start_node_id="N7",
            end_node_id="N8",
            section_id="S_BEAM",
            support_idealization=GravitySupportIdealizationV1.BEAM_SIMPLY_SUPPORTED,
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
                support_idealization=(
                    GravitySupportIdealizationV1.COLUMN_BRACED_AXIAL_ONLY
                ),
                load_path_id=f"LP_COLUMN_C{index}",
                render_id=f"RENDER_COLUMN_C{index}",
            )
            for index in range(1, 5)
        ),
    )
    footings = tuple(
        GravityFootingDestinationV1(
            id=f"F{index}",
            column_id=f"C{index}",
            node_id=f"N{index}",
            load_path_id=f"LP_FOOTING_F{index}",
        )
        for index in range(1, 5)
    )
    canonical_entities = (*nodes, *materials, *sections, *panels, *members, *footings)
    source_records = tuple(
        BuildingSourceRecordV1(
            source_index=index,
            source_id=f"input-row-{index}",
            disposition=SourceDispositionV1.ACCEPTED,
            canonical_id=entity.id,
        )
        for index, entity in enumerate(canonical_entities)
    )
    return BuildingModelV1(
        model_id="HAND_MODEL_01",
        project_id="HAND_PROJECT_01",
        raw_source_hash="1" * 64,
        nodes=nodes,
        materials=materials,
        sections=sections,
        panels=panels,
        members=members,
        footing_destinations=footings,
        source_records=source_records,
    )


def _loads(
    building: BuildingModelV1,
    *,
    superimposed_dead_load_kn_m2: float = 1.5,
    live_load_kn_m2: float = 3.0,
    practical_actions: tuple[GravityPracticalActionV1, ...] = (),
) -> LoadModelV1:
    references = (
        GravitySourceReferenceV1(
            id="PROJECT_BASIS",
            title="Hand example load basis",
            reference="B1 frozen hand example",
            source_hash="2" * 64,
        ),
        GravitySourceReferenceV1(
            id="COMBINATION_BASIS",
            title="V1 dead and live combinations",
            reference="Approved B1 combination contract",
            source_hash="3" * 64,
        ),
    )
    dispositions = {
        GravityActionCategoryV1.SLAB_SELF_WEIGHT: (
            GravityInclusionDispositionV1.GENERATED
        ),
        GravityActionCategoryV1.SLAB_SUPERIMPOSED_DEAD: (
            GravityInclusionDispositionV1.SUPPLIED
        ),
        GravityActionCategoryV1.BEAM_SELF_WEIGHT: (
            GravityInclusionDispositionV1.GENERATED
        ),
        GravityActionCategoryV1.COLUMN_SELF_WEIGHT: (
            GravityInclusionDispositionV1.GENERATED
        ),
        GravityActionCategoryV1.LIVE_OCCUPANCY: (
            GravityInclusionDispositionV1.SUPPLIED
        ),
    }
    inclusion_rules = tuple(
        GravityInclusionRuleV1(
            category=category,
            disposition=disposition,
            source_ref_id="PROJECT_BASIS",
        )
        for category, disposition in dispositions.items()
    )
    combinations = (
        GravityCombinationV1(
            id="SERVICE_DL_LL",
            state=GravityLoadStateV1.SERVICE,
            factors=(
                GravityCombinationFactorV1(case_id=GravityLoadCaseV1.DEAD, factor=1.0),
                GravityCombinationFactorV1(case_id=GravityLoadCaseV1.LIVE, factor=1.0),
            ),
            source_ref_id="COMBINATION_BASIS",
        ),
        GravityCombinationV1(
            id="ULS_1_5_DL_LL",
            state=GravityLoadStateV1.FACTORED,
            factors=(
                GravityCombinationFactorV1(case_id=GravityLoadCaseV1.DEAD, factor=1.5),
                GravityCombinationFactorV1(case_id=GravityLoadCaseV1.LIVE, factor=1.5),
            ),
            source_ref_id="COMBINATION_BASIS",
        ),
    )
    exclusions = tuple(
        GravityApprovedExclusionV1(
            category=category,
            reason=f"{category.value} is outside the bounded dead/live V1 scope",
            source_ref_id="PROJECT_BASIS",
        )
        for category in ExcludedGravityActionV1
        if category not in {action.source_category for action in practical_actions}
    )
    return LoadModelV1(
        model_hash=building.accepted_model_hash,
        raw_source_hash="4" * 64,
        superimposed_dead_load_kn_m2=superimposed_dead_load_kn_m2,
        live_load_kn_m2=live_load_kn_m2,
        live_load_category="OFFICE_UNREDUCED",
        source_references=references,
        inclusion_rules=inclusion_rules,
        combinations=combinations,
        practical_actions=practical_actions,
        approved_exclusions=exclusions,
    )


def _practical_actions() -> tuple[GravityPracticalActionV1, ...]:
    return (
        GravityPracticalActionV1(
            id="WALL_B1_DL",
            kind=GravityPracticalActionKindV1.WALL_LINE,
            source_category=ExcludedGravityActionV1.WALL,
            case_id=GravityLoadCaseV1.DEAD,
            source_identity="wall:north:segment:01",
            source_ref_id="PROJECT_BASIS",
            destination_id="B1",
            magnitude=5,
            units=GravityPracticalActionUnitsV1.KILONEWTON_PER_METRE,
            assignment_basis="Caller assigned full-span north wall line to B1.",
        ),
        GravityPracticalActionV1(
            id="FACADE_B2_DL",
            kind=GravityPracticalActionKindV1.BEAM_LINE,
            source_category=ExcludedGravityActionV1.FACADE,
            case_id=GravityLoadCaseV1.DEAD,
            source_identity="facade:south:segment:01",
            source_ref_id="PROJECT_BASIS",
            destination_id="B2",
            magnitude=2,
            units=GravityPracticalActionUnitsV1.KILONEWTON_PER_METRE,
            assignment_basis="Caller assigned full-span facade line to B2.",
        ),
        GravityPracticalActionV1(
            id="EQUIPMENT_B1_DL",
            kind=GravityPracticalActionKindV1.BEAM_POINT,
            source_category=ExcludedGravityActionV1.EQUIPMENT,
            case_id=GravityLoadCaseV1.DEAD,
            source_identity="equipment:item:01",
            source_ref_id="PROJECT_BASIS",
            destination_id="B1",
            magnitude=12,
            units=GravityPracticalActionUnitsV1.KILONEWTON,
            point_position_mm=2000,
            assignment_basis="Caller assigned equipment item to B1 at 2000 mm.",
        ),
        GravityPracticalActionV1(
            id="ROOF_SPECIAL_P1_LL",
            kind=GravityPracticalActionKindV1.SLAB_AREA,
            source_category=ExcludedGravityActionV1.ROOF_SPECIAL,
            case_id=GravityLoadCaseV1.LIVE,
            source_identity="roof:special:zone:01",
            source_ref_id="PROJECT_BASIS",
            destination_id="P1",
            magnitude=1,
            units=GravityPracticalActionUnitsV1.KILONEWTON_PER_SQUARE_METRE,
            assignment_basis="Caller assigned supported roof area action to P1.",
        ),
    )


def _footing_actions(ledger: GravityLoadLedgerV1, combination_id: str) -> list[float]:
    return sorted(
        action.total_kn
        for action in ledger.combination_actions
        if action.combination_id == combination_id
    )


def test_hand_example_reconciles_every_boundary_and_expected_action() -> None:
    building = _building()
    loads = _loads(building)

    ledger = build_gravity_load_ledger_v1(building, loads)

    footing_entries = {
        (entry.case_id, entry.destination_id): entry.magnitude_kn
        for entry in ledger.entries
        if entry.stage is GravityLedgerStageV1.FOOTING_ACTION
    }
    assert set(footing_entries.values()) == {49.5, 18.0}
    assert all(
        footing_entries[(GravityLoadCaseV1.DEAD, f"F{index}")] == 49.5
        for index in range(1, 5)
    )
    assert all(
        footing_entries[(GravityLoadCaseV1.LIVE, f"F{index}")] == 18.0
        for index in range(1, 5)
    )
    assert _footing_actions(ledger, "SERVICE_DL_LL") == [67.5] * 4
    assert _footing_actions(ledger, "ULS_1_5_DL_LL") == [101.25] * 4
    assert (
        math.fsum(
            entry.magnitude_kn
            for entry in ledger.entries
            if entry.stage is GravityLedgerStageV1.SOURCE
            and entry.case_id is GravityLoadCaseV1.DEAD
        )
        == 198.0
    )
    assert (
        math.fsum(
            entry.magnitude_kn
            for entry in ledger.entries
            if entry.stage is GravityLedgerStageV1.SOURCE
            and entry.case_id is GravityLoadCaseV1.LIVE
        )
        == 72.0
    )
    assert ledger.all_balanced
    assert len(ledger.balances) == 26
    assert all(balance.residual_kn == pytest.approx(0.0) for balance in ledger.balances)


def test_ledger_accounts_for_sources_and_exclusions_without_footing_inference() -> None:
    building = _building()
    loads = _loads(building)

    ledger = build_gravity_load_ledger_v1(building, loads)

    assert ledger.source_entry_count == 9
    assert ledger.accepted_entry_count == 41
    assert ledger.blocked_entry_count == 0
    assert ledger.approved_exclusion_count == len(ExcludedGravityActionV1)
    source_ids = {
        entry.source_id
        for entry in ledger.entries
        if entry.stage is GravityLedgerStageV1.SOURCE
    }
    assert source_ids.isdisjoint({"F1", "F2", "F3", "F4"})
    assert ExcludedGravityActionV1.FOOTING_SELF_WEIGHT in {
        exclusion.category for exclusion in loads.approved_exclusions
    }
    assert ExcludedGravityActionV1.OVERBURDEN in {
        exclusion.category for exclusion in loads.approved_exclusions
    }


def test_explicit_practical_actions_reconcile_without_silent_loss() -> None:
    building = _building()
    loads = _loads(building, practical_actions=_practical_actions())

    ledger = build_gravity_load_ledger_v1(building, loads)

    footing_entries = {
        (entry.case_id, entry.destination_id): entry.magnitude_kn
        for entry in ledger.entries
        if entry.stage is GravityLedgerStageV1.FOOTING_ACTION
    }
    assert [
        footing_entries[(GravityLoadCaseV1.DEAD, f"F{index}")] for index in range(1, 5)
    ] == pytest.approx([72.5, 68.5, 55.5, 55.5])
    assert [
        footing_entries[(GravityLoadCaseV1.LIVE, f"F{index}")] for index in range(1, 5)
    ] == pytest.approx([24.0, 24.0, 24.0, 24.0])
    assert _footing_actions(ledger, "SERVICE_DL_LL") == pytest.approx(
        [79.5, 79.5, 92.5, 96.5]
    )
    assert _footing_actions(ledger, "ULS_1_5_DL_LL") == pytest.approx(
        [119.25, 119.25, 138.75, 144.75]
    )
    practical_balances = [
        item
        for item in ledger.balances
        if item.boundary is GravityBalanceBoundaryV1.PRACTICAL_ACTION_ASSIGNMENT
    ]
    assert len(practical_balances) == 4
    assert all(item.passed and item.residual_kn == 0 for item in practical_balances)
    assert ledger.all_balanced
    assert len(ledger.balances) == 30
    assert ledger.source_entry_count == 13
    assert ledger.accepted_entry_count == 50
    assert ledger.approved_exclusion_count == 7

    point_entries = [
        item for item in ledger.entries if item.practical_action_id == "EQUIPMENT_B1_DL"
    ]
    assert {item.stage for item in point_entries} == {
        GravityLedgerStageV1.SOURCE,
        GravityLedgerStageV1.BEAM_POINT,
    }
    assert {item.practical_source_identity for item in point_entries} == {
        "equipment:item:01"
    }
    assert {item.practical_source_ref_id for item in point_entries} == {"PROJECT_BASIS"}
    assert {item.practical_input_units.value for item in point_entries} == {"kN"}


def test_hashes_ignore_harmless_order_and_raw_provenance_serialization() -> None:
    building = _building()
    building_payload = building.model_dump(
        mode="python", exclude={"accepted_model_hash"}
    )
    building_payload["raw_source_hash"] = "9" * 64
    for key in (
        "nodes",
        "materials",
        "sections",
        "panels",
        "members",
        "footing_destinations",
        "source_records",
    ):
        building_payload[key] = tuple(reversed(building_payload[key]))
    reordered_building = BuildingModelV1.model_validate(building_payload)

    assert reordered_building.accepted_model_hash == building.accepted_model_hash

    loads = _loads(building, practical_actions=_practical_actions())
    load_payload = loads.model_dump(mode="python", exclude={"load_model_hash"})
    load_payload["raw_source_hash"] = "8" * 64
    for key in (
        "source_references",
        "inclusion_rules",
        "combinations",
        "practical_actions",
        "approved_exclusions",
    ):
        load_payload[key] = tuple(reversed(load_payload[key]))
    reordered_loads = LoadModelV1.model_validate(load_payload)

    assert reordered_loads.load_model_hash == loads.load_model_hash
    assert (
        build_gravity_load_ledger_v1(building, loads).ledger_hash
        == build_gravity_load_ledger_v1(reordered_building, reordered_loads).ledger_hash
    )


def test_model_rejects_orphan_section_and_duplicate_source_mapping() -> None:
    building = _building()
    payload = building.model_dump(mode="python", exclude={"accepted_model_hash"})
    payload["sections"] = (
        *payload["sections"],
        GravitySectionV1(
            id="S_ORPHAN",
            kind=GravitySectionKindV1.BEAM,
            material_id="M_CONC",
            width_mm=250,
            depth_mm=400,
        ),
    )
    with pytest.raises(ValidationError, match="one slab"):
        BuildingModelV1.model_validate(payload)

    payload = building.model_dump(mode="python", exclude={"accepted_model_hash"})
    first = payload["source_records"][0]
    payload["source_records"] = (
        *payload["source_records"],
        {**first, "source_index": 100, "source_id": "duplicate-row"},
    )
    with pytest.raises(ValidationError, match="account for every canonical entity"):
        BuildingModelV1.model_validate(payload)


def test_load_contract_rejects_missing_exclusion_and_wrong_combination() -> None:
    building = _building()
    loads = _loads(building)
    payload = loads.model_dump(mode="python", exclude={"load_model_hash"})
    payload["approved_exclusions"] = payload["approved_exclusions"][:-1]
    with pytest.raises(ValidationError, match="every action excluded"):
        LoadModelV1.model_validate(payload)

    payload = loads.model_dump(mode="python", exclude={"load_model_hash"})
    service = dict(payload["combinations"][0])
    service["factors"] = (
        GravityCombinationFactorV1(case_id=GravityLoadCaseV1.DEAD, factor=1.2),
        GravityCombinationFactorV1(case_id=GravityLoadCaseV1.LIVE, factor=1.0),
    )
    payload["combinations"] = (
        service,
        payload["combinations"][1],
    )
    with pytest.raises(ValidationError, match="DL/LL factor=1.0"):
        LoadModelV1.model_validate(payload)


def test_practical_action_contract_rejects_shape_source_and_exclusion_mismatch() -> (
    None
):
    point = _practical_actions()[2].model_dump(mode="python")
    point["units"] = "kN/m"
    with pytest.raises(ValidationError, match="BEAM_POINT requires units=kN"):
        GravityPracticalActionV1.model_validate(point)

    point = _practical_actions()[2].model_dump(mode="python")
    point["point_position_mm"] = None
    with pytest.raises(ValidationError, match="requires point_position_mm"):
        GravityPracticalActionV1.model_validate(point)

    point = _practical_actions()[2].model_dump(mode="python")
    point["source_category"] = "LATERAL"
    with pytest.raises(ValidationError, match="not a supported practical"):
        GravityPracticalActionV1.model_validate(point)

    building = _building()
    payload = _loads(building).model_dump(mode="python", exclude={"load_model_hash"})
    payload["practical_actions"] = (_practical_actions()[0],)
    with pytest.raises(ValidationError, match="omit explicitly supplied"):
        LoadModelV1.model_validate(payload)


def test_mismatched_model_hash_fails_closed_before_calculation() -> None:
    building = _building()
    loads = _loads(building).model_copy(update={"model_hash": "f" * 64})

    with pytest.raises(GravityLoadLedgerError, match="does not match"):
        build_gravity_load_ledger_v1(building, loads)


def test_doubling_every_load_source_doubles_every_foundation_action() -> None:
    building = _building()
    ledger = build_gravity_load_ledger_v1(building, _loads(building))
    doubled_building = _building(unit_weight_kn_m3=50.0)
    doubled = build_gravity_load_ledger_v1(
        doubled_building,
        _loads(
            doubled_building,
            superimposed_dead_load_kn_m2=3.0,
            live_load_kn_m2=6.0,
        ),
    )

    for combination_id in ("SERVICE_DL_LL", "ULS_1_5_DL_LL"):
        assert _footing_actions(doubled, combination_id) == pytest.approx(
            [2.0 * value for value in _footing_actions(ledger, combination_id)]
        )


@pytest.mark.parametrize("invalid", [math.inf, -math.inf, math.nan])
def test_nonfinite_physical_or_load_value_is_rejected(invalid: float) -> None:
    with pytest.raises(ValidationError):
        GravityNodeV1(id="N_BAD", x_mm=invalid, y_mm=0, z_mm=0)

    building = _building()
    payload = _loads(building).model_dump(mode="python", exclude={"load_model_hash"})
    payload["live_load_kn_m2"] = invalid
    with pytest.raises(ValidationError):
        LoadModelV1.model_validate(payload)
