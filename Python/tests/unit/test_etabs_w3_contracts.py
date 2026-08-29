"""W3A normalized result-catalogue and same-row demand contract tests."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

import structural_lib
from structural_lib.core.analysis_contracts import (
    AnalysisStateV1,
    AnalysisStatusIdentityV1,
    BeamActionComponentV1,
    BeamDemandEnvelopeModeV1,
    BeamDemandEnvelopeRuleV1,
    BeamDemandPurposeV1,
    BeamDemandScenarioV1,
    EvidenceStateV1,
    EvidenceValueV1,
    LinearStaticCaseParametersV1,
    LinearStaticInitialConditionV1,
    LinearStaticLoadItemV1,
    LoadCaseDefinitionV1,
    LoadPatternDefinitionV1,
    ResponseCombinationDefinitionV1,
    ResponseCombinationFactorV1,
    ResponseCombinationSourceKindV1,
    ResultSelectionIdentityV1,
    ResultSelectionKindV1,
    UnsupportedCaseParametersV1,
)
from structural_lib.services.contracts import etabs_w3
from structural_lib.services.etabs_beam_baseline import (
    ETABSBaselineDisposition,
    ETABSBaselineDispositionV1,
    ETABSBaselineRowKind,
    ETABSBeamBaselineV1,
    ETABSForceStationV1,
    ETABSFrameKind,
    ETABSFrameResultV1,
    ETABSFrameV1,
    ETABSLocalAxisV1,
    ETABSModelFileEvidenceV1,
    ETABSModelFileSnapshotV1,
    ETABSModelIdentityV1,
    ETABSPointV1,
    ETABSRectangularSectionV1,
    ETABSResultSelectionEvidenceV1,
    ETABSRuntimeProvenanceV1,
    ETABSStoryV1,
    ETABSUnitProofV1,
    canonical_etabs_beam_baseline_hash_basis_json_v1,
)
from structural_lib.services.etabs_live_bridge import (
    ETABSResultSelectionKind,
    ETABSResultSelectionV1,
)

SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64


def _present(value: Any, source: str = "fake:v1") -> EvidenceValueV1[Any]:
    return EvidenceValueV1(
        state=EvidenceStateV1.PRESENT, value=value, source_references=(source,)
    )


def _not_applicable(source: str = "fake:v1") -> EvidenceValueV1[Any]:
    return EvidenceValueV1(
        state=EvidenceStateV1.NOT_APPLICABLE,
        value=None,
        reason_code="FIELD_NOT_APPLICABLE",
        message="The declared type does not use this field.",
        source_references=(source,),
    )


def _linear_case(case_id: str, name: str, ordinal: int) -> LoadCaseDefinitionV1:
    provisional = LoadCaseDefinitionV1(
        case_id=case_id,
        name=name,
        raw_type="Linear Static",
        raw_subtype="Linear",
        raw_design_type="Dead",
        raw_auto_flag=0,
        is_auto=_present(False, f"fake:case:{name}"),
        parameters=LinearStaticCaseParametersV1(
            initial_condition=LinearStaticInitialConditionV1(
                raw_initial_case="None",
                evidence_reference="fake:initial-case",
            ),
            load_items=(
                LinearStaticLoadItemV1(
                    ordinal=0,
                    load_type="Load",
                    load_name=name,
                    scale_factor=1.0,
                    evidence_reference=f"fake:case:{name}",
                ),
            ),
        ),
        analysis_status_id=f"status:{case_id}",
        source_ordinal=ordinal,
        evidence_reference=f"fake:case:{name}",
        definition_sha256="0" * 64,
    )
    return provisional.model_copy(
        update={"definition_sha256": etabs_w3._definition_sha(provisional)}
    )


def _combination(
    combination_id: str,
    name: str,
    ordinal: int,
    factors: tuple[ResponseCombinationFactorV1, ...],
) -> ResponseCombinationDefinitionV1:
    provisional = ResponseCombinationDefinitionV1(
        combination_id=combination_id,
        name=name,
        raw_type="Linear Add",
        normalized_type="LINEAR_ADDITIVE",
        factors=factors,
        design_purpose=_present("STRENGTH", f"fake:combo:{name}"),
        source_ordinal=ordinal,
        evidence_reference=f"fake:combo:{name}",
        definition_sha256="0" * 64,
    )
    return provisional.model_copy(
        update={"definition_sha256": etabs_w3._definition_sha(provisional)}
    )


def _selection(
    kind: ResultSelectionKindV1, name: str, target_id: str
) -> ResultSelectionIdentityV1:
    is_case = kind is ResultSelectionKindV1.CASE
    return ResultSelectionIdentityV1(
        selection_id=etabs_w3._selection_id(kind.value, name),
        kind=kind,
        name=name,
        selected_for_output=_present(True, f"fake:selection:{name}"),
        case_status_id=(
            _present(target_id, f"fake:selection:{name}")
            if is_case
            else _not_applicable()
        ),
        combination_definition_id=(
            _not_applicable()
            if is_case
            else _present(target_id, f"fake:selection:{name}")
        ),
        model_identity_sha256=SHA_A,
        runtime_identity_sha256=SHA_B,
        getter_identity_sha256=SHA_C,
        model_observation_before="fake:model:before",
        model_observation_after="fake:model:after",
        evidence_reference=f"fake:selection:{name}",
    )


def _catalogue_request() -> etabs_w3.ETABSResultCatalogueBuildRequestV1:
    dead = _linear_case("case:dead", "DEAD", 0)
    live = _linear_case("case:live", "LIVE", 1)
    inner = _combination(
        "combo:inner",
        "ULS-INNER",
        0,
        (
            ResponseCombinationFactorV1(
                ordinal=0,
                source_kind=ResponseCombinationSourceKindV1.CASE,
                source_id=dead.case_id,
                source_name=dead.name,
                scale_factor=1.5,
                evidence_reference="fake:factor:0",
            ),
            ResponseCombinationFactorV1(
                ordinal=1,
                source_kind=ResponseCombinationSourceKindV1.CASE,
                source_id=live.case_id,
                source_name=live.name,
                scale_factor=-1.5,
                evidence_reference="fake:factor:1",
            ),
        ),
    )
    outer = _combination(
        "combo:outer",
        "ULS-OUTER",
        1,
        (
            ResponseCombinationFactorV1(
                ordinal=0,
                source_kind=ResponseCombinationSourceKindV1.COMBINATION,
                source_id=inner.combination_id,
                source_name=inner.name,
                scale_factor=1.0,
                evidence_reference="fake:factor:2",
            ),
            ResponseCombinationFactorV1(
                ordinal=1,
                source_kind=ResponseCombinationSourceKindV1.CASE,
                source_id=dead.case_id,
                source_name=dead.name,
                scale_factor=0.0,
                evidence_reference="fake:factor:3",
            ),
        ),
    )
    statuses = tuple(
        AnalysisStatusIdentityV1(
            status_id=f"status:{case.case_id}",
            case_id=case.case_id,
            raw_status_code=4,
            state=AnalysisStateV1.FINISHED,
            getter_identity="Analyze.GetCaseStatus",
            signature_identity=SHA_C,
            model_observation_before="fake:model:before",
            model_observation_after="fake:model:after",
            observed_at_utc="2026-08-30T00:00:00Z",
            evidence_reference=f"fake:status:{case.case_id}",
        )
        for case in (dead, live)
    )
    return etabs_w3.ETABSResultCatalogueBuildRequestV1(
        model_identity_sha256=SHA_A,
        runtime_identity_sha256=SHA_B,
        getter_matrix_sha256=SHA_C,
        load_patterns=(
            LoadPatternDefinitionV1(
                pattern_id="pattern:dead",
                name="DEAD",
                raw_type="Dead",
                normalized_type="DEAD",
                self_weight_multiplier=0.0,
                source_ordinal=0,
                evidence_reference="fake:pattern:dead",
            ),
        ),
        load_cases=(dead, live),
        analysis_statuses=statuses,
        response_combinations=(inner, outer),
        result_selections=(
            _selection(ResultSelectionKindV1.CASE, "DEAD", "status:case:dead"),
            _selection(
                ResultSelectionKindV1.COMBINATION, "ULS-OUTER", outer.combination_id
            ),
        ),
    )


def _snapshot(observed_at: str) -> ETABSModelFileSnapshotV1:
    return ETABSModelFileSnapshotV1(
        model_path=r"C:\Models\W3 Copy.edb",
        model_name="W3 Copy.edb",
        sha256=SHA_A,
        byte_count=123,
        modified_at_utc="2026-08-30T00:00:00Z",
        observed_at_utc=observed_at,
    )


def _baseline() -> ETABSBeamBaselineV1:
    selection = ETABSResultSelectionV1(
        kind=ETABSResultSelectionKind.COMBINATION,
        name="ULS-OUTER",
    )
    stations = tuple(
        ETABSForceStationV1(
            station_id=f"station:{index}",
            member_id="member:1",
            source_frame_name="B1",
            source_row_index=index,
            selection=selection,
            object_name="B1",
            object_station_mm=float(index * 1000),
            element_name="E-B1",
            element_station_mm=float(index * 1000),
            step_type="Max",
            step_number=0.0,
            p_kn=float(index),
            v2_kn=(-20.0, 40.0, -40.0)[index],
            v3_kn=float(index + 1),
            t_knm=(2.0, -8.0, 8.0)[index],
            m2_knm=float(index + 3),
            m3_knm=(100.0, 50.0, -100.0)[index],
        )
        for index in range(3)
    )
    model_evidence = ETABSModelFileEvidenceV1(
        before_read=_snapshot("2026-08-30T00:01:00Z"),
        after_read=_snapshot("2026-08-30T00:02:00Z"),
    )
    provisional = ETABSBeamBaselineV1(
        model=ETABSModelIdentityV1(
            model_name="W3 Copy.edb",
            model_path=r"C:\Models\W3 Copy.edb",
            file_evidence=model_evidence,
            etabs_version="ETABS 23.3.1",
            etabs_version_number=23.31,
            model_locked=True,
        ),
        units=ETABSUnitProofV1(
            original_present_units_enum=6,
            restored_present_units_enum=6,
        ),
        stories=(
            ETABSStoryV1(
                story_id="story:1",
                name="L1",
                elevation_mm=0.0,
                height_mm=3000.0,
                is_master_story=False,
                similar_to_story="",
                splice_above=False,
                splice_height_mm=0.0,
            ),
        ),
        frames=(
            ETABSFrameV1(
                member_id="member:1",
                source_unique_name="B1",
                label="B1",
                story="L1",
                kind=ETABSFrameKind.BEAM,
                point_i=ETABSPointV1(point_name="P1", x_mm=0.0, y_mm=0.0, z_mm=0.0),
                point_j=ETABSPointV1(point_name="P2", x_mm=3000.0, y_mm=0.0, z_mm=0.0),
                local_axis=ETABSLocalAxisV1(
                    local_axis_rotation_deg=0.0,
                    advanced_axes_active=False,
                    direction_x=1.0,
                    direction_y=0.0,
                    direction_z=0.0,
                    length_mm=3000.0,
                ),
                section=ETABSRectangularSectionV1(
                    section_name="R300x500",
                    auto_select_list="",
                    material_property_label="M25",
                    depth_t3_mm=500.0,
                    width_t2_mm=300.0,
                ),
            ),
        ),
        connectivity=(),
        results=(
            ETABSFrameResultV1(
                member_id="member:1",
                source_frame_name="B1",
                selection_evidence=ETABSResultSelectionEvidenceV1(
                    selection=selection,
                    case_status_code=None,
                    status="COMBINATION_ROWS_REQUIRED",
                ),
                stations=stations,
            ),
        ),
        dispositions=(
            ETABSBaselineDispositionV1(
                row_id="disposition:1",
                row_kind=ETABSBaselineRowKind.RESULT_STATION,
                source_id="B1",
                disposition=ETABSBaselineDisposition.ACCEPTED,
                canonical_id="member:1",
                reason_code="RESULT_STATION_ACCEPTED",
                message="fake retained stations",
            ),
        ),
        runtime_provenance=ETABSRuntimeProvenanceV1(
            library_version="0.24.0",
            library_content_identity=SHA_B,
            python_version="3.11.15",
            platform="Windows-11",
            com_provider="fake-com/v1",
        ),
        getter_matrix_sha256=SHA_C,
        frame_analysis_basis=("No solver claim.",),
        limitations=("Fake normalized fixture only.",),
        baseline_sha256="0" * 64,
    )
    import hashlib

    digest = hashlib.sha256(
        canonical_etabs_beam_baseline_hash_basis_json_v1(provisional).encode("utf-8")
    ).hexdigest()
    return provisional.model_copy(update={"baseline_sha256": digest})


def _accepted_catalogue() -> etabs_w3.ETABSResultCatalogueV1:
    result = etabs_w3.build_etabs_result_catalogue_v1(_catalogue_request())
    assert result.status is etabs_w3.W3BuildStatusV1.ACCEPTED
    assert result.catalogue is not None
    return result.catalogue


def test_all_five_evidence_states_and_strict_unknown_fields() -> None:
    assert _present(0).value == 0
    assert _present(False).value is False
    assert _present(()).value == ()
    for state in (
        EvidenceStateV1.UNAVAILABLE,
        EvidenceStateV1.NOT_REQUESTED,
        EvidenceStateV1.NOT_APPLICABLE,
        EvidenceStateV1.BLOCKED,
    ):
        evidence = EvidenceValueV1[str](
            state=state,
            value=None,
            reason_code=f"{state.value}_REASON",
            message="Explicit state evidence.",
            source_references=("fake:v1",),
        )
        assert evidence.value is None
    with pytest.raises(ValidationError):
        EvidenceValueV1[int](
            state=EvidenceStateV1.PRESENT,
            value=0,
            source_references=("fake:v1",),
            unknown=True,
        )
    with pytest.raises(ValidationError):
        EvidenceValueV1[int](
            state=EvidenceStateV1.BLOCKED,
            value=0,
            reason_code="BLOCKED",
            message="bad",
            source_references=("fake:v1",),
        )


def test_catalogue_retains_order_nested_factors_and_hash_round_trip() -> None:
    catalogue = _accepted_catalogue()
    assert [item.name for item in catalogue.response_combinations] == [
        "ULS-INNER",
        "ULS-OUTER",
    ]
    assert [
        factor.scale_factor for factor in catalogue.response_combinations[0].factors
    ] == [
        1.5,
        -1.5,
    ]
    assert catalogue.response_combinations[1].factors[1].scale_factor == 0.0
    assert etabs_w3.verify_etabs_result_catalogue_hash_v1(catalogue)
    restored = etabs_w3.ETABSResultCatalogueV1.model_validate_json(
        catalogue.model_dump_json(), strict=False
    )
    assert restored == catalogue
    tampered = catalogue.model_copy(update={"getter_matrix_sha256": "d" * 64})
    assert not etabs_w3.verify_etabs_result_catalogue_hash_v1(tampered)


def test_catalogue_blocks_missing_target_cycle_unfinished_and_capacity() -> None:
    request = _catalogue_request()
    inner = request.response_combinations[0]
    missing_factor = inner.factors[0].model_copy(update={"source_id": "case:missing"})
    bad_inner = inner.model_copy(
        update={"factors": (missing_factor, *inner.factors[1:])}
    )
    bad_inner = bad_inner.model_copy(
        update={"definition_sha256": etabs_w3._definition_sha(bad_inner)}
    )
    missing = etabs_w3.build_etabs_result_catalogue_v1(
        request.model_copy(
            update={
                "response_combinations": (bad_inner, request.response_combinations[1])
            }
        )
    )
    assert missing.catalogue is None
    assert "COMBINATION_FACTOR_TARGET_MISSING" in {
        issue.code for issue in missing.issues
    }

    outer = request.response_combinations[1]
    cycle_factor = inner.factors[0].model_copy(
        update={
            "source_kind": ResponseCombinationSourceKindV1.COMBINATION,
            "source_id": outer.combination_id,
            "source_name": outer.name,
        }
    )
    cyclic_inner = inner.model_copy(
        update={"factors": (cycle_factor, *inner.factors[1:])}
    )
    cyclic_inner = cyclic_inner.model_copy(
        update={"definition_sha256": etabs_w3._definition_sha(cyclic_inner)}
    )
    cyclic = etabs_w3.build_etabs_result_catalogue_v1(
        request.model_copy(update={"response_combinations": (cyclic_inner, outer)})
    )
    assert "NESTED_COMBINATION_CYCLE" in {issue.code for issue in cyclic.issues}

    status = request.analysis_statuses[0].model_copy(
        update={"state": AnalysisStateV1.NOT_FINISHED}
    )
    unfinished = etabs_w3.build_etabs_result_catalogue_v1(
        request.model_copy(
            update={"analysis_statuses": (status, request.analysis_statuses[1])}
        )
    )
    assert "SELECTED_CASE_NOT_FINISHED" in {issue.code for issue in unfinished.issues}
    capacity = etabs_w3.build_etabs_result_catalogue_v1(
        request.model_copy(update={"capacity_limit": 1})
    )
    assert "CATALOGUE_CAPACITY_EXCEEDED" in {issue.code for issue in capacity.issues}


def test_unsupported_selected_case_parameters_block_demand() -> None:
    request = _catalogue_request()
    case = request.load_cases[0]
    unsupported = case.model_copy(
        update={
            "parameters": UnsupportedCaseParametersV1(
                raw_type="Modal",
                raw_subtype="Eigen",
                parameter_evidence=EvidenceValueV1[bool](
                    state=EvidenceStateV1.BLOCKED,
                    value=None,
                    reason_code="CASE_FAMILY_UNSUPPORTED",
                    message="No accepted typed parameter family.",
                    source_references=("fake:case",),
                ),
            )
        }
    )
    unsupported = unsupported.model_copy(
        update={"definition_sha256": etabs_w3._definition_sha(unsupported)}
    )
    built = etabs_w3.build_etabs_result_catalogue_v1(
        request.model_copy(update={"load_cases": (unsupported, request.load_cases[1])})
    )
    assert built.catalogue is not None
    scenario, rules = _scenario_and_rules(built.catalogue, _baseline())
    result = etabs_w3.derive_beam_demand_snapshot_v1(
        etabs_w3.BeamDemandDerivationRequestV1(
            baseline=_baseline(),
            catalogue=built.catalogue,
            scenario=scenario,
            envelope_rules=rules,
        )
    )
    assert result.snapshot is None
    assert "SCENARIO_CASE_PARAMETERS_BLOCKED" in {issue.code for issue in result.issues}


def _scenario_and_rules(
    catalogue: etabs_w3.ETABSResultCatalogueV1,
    baseline: ETABSBeamBaselineV1,
) -> tuple[BeamDemandScenarioV1, tuple[BeamDemandEnvelopeRuleV1, ...]]:
    selection = next(
        item
        for item in catalogue.result_selections
        if item.kind is ResultSelectionKindV1.COMBINATION
    )
    rules = (
        BeamDemandEnvelopeRuleV1(
            rule_id="rule:same-row",
            mode=BeamDemandEnvelopeModeV1.SAME_ROW_CONCURRENT,
            components=(BeamActionComponentV1.V2, BeamActionComponentV1.M3),
            primary_component=BeamActionComponentV1.M3,
            caller_defined_basis=_not_applicable(),
        ),
        BeamDemandEnvelopeRuleV1(
            rule_id="rule:absolute-screening",
            mode=BeamDemandEnvelopeModeV1.INDEPENDENT_ABSOLUTE_COMPONENTS,
            components=(BeamActionComponentV1.V2, BeamActionComponentV1.T),
            caller_defined_basis=_not_applicable(),
        ),
    )
    scenario = BeamDemandScenarioV1(
        scenario_id="scenario:strength",
        revision=1,
        purpose=BeamDemandPurposeV1.STRENGTH,
        catalogue_sha256=catalogue.catalogue_sha256,
        baseline_sha256=baseline.baseline_sha256,
        included_selection_ids=(selection.selection_id,),
        member_ids=("member:1",),
        required_components=(BeamActionComponentV1.V2, BeamActionComponentV1.M3),
        envelope_rule_ids=("rule:same-row", "rule:absolute-screening"),
    )
    return scenario, rules


def test_same_row_concurrency_cross_row_screening_and_deterministic_tie() -> None:
    baseline = _baseline()
    catalogue = _accepted_catalogue()
    scenario, rules = _scenario_and_rules(catalogue, baseline)
    result = etabs_w3.derive_beam_demand_snapshot_v1(
        etabs_w3.BeamDemandDerivationRequestV1(
            baseline=baseline,
            catalogue=catalogue,
            scenario=scenario,
            envelope_rules=rules,
        )
    )
    assert result.status is etabs_w3.W3BuildStatusV1.ACCEPTED
    assert result.snapshot is not None
    same_row = [
        ref
        for ref in result.snapshot.governing_references
        if ref.rule_id == "rule:same-row"
    ]
    assert {ref.action_row_ids for ref in same_row} == {("station:0",)}
    assert all(ref.is_concurrent for ref in same_row)
    screening = [
        ref
        for ref in result.snapshot.governing_references
        if ref.rule_id == "rule:absolute-screening"
    ]
    assert not any(ref.is_concurrent for ref in screening)
    v2 = next(ref for ref in screening if ref.component is BeamActionComponentV1.V2)
    torsion = next(ref for ref in screening if ref.component is BeamActionComponentV1.T)
    assert v2.action_row_ids == ("station:1",)
    assert torsion.action_row_ids == ("station:1",)
    assert etabs_w3.verify_beam_demand_snapshot_hash_v1(result.snapshot)
    tampered = result.snapshot.model_copy(update={"member_count": 2})
    assert not etabs_w3.verify_beam_demand_snapshot_hash_v1(tampered)


def test_lossless_paging_and_public_exports() -> None:
    baseline = _baseline()
    selection_id = etabs_w3._selection_id("COMBINATION", "ULS-OUTER")
    first = etabs_w3.query_beam_action_rows_v1(
        baseline, selection_ids=(selection_id,), limit=2
    )
    second = etabs_w3.query_beam_action_rows_v1(
        baseline,
        selection_ids=(selection_id,),
        cursor=first.next_cursor,
        limit=2,
    )
    assert first.total_count == 3
    assert [row.station_id for row in (*first.rows, *second.rows)] == [
        "station:0",
        "station:1",
        "station:2",
    ]
    assert second.next_cursor is None
    with pytest.raises(ValueError, match="BEAM_ACTION_LIMIT_INVALID"):
        etabs_w3.query_beam_action_rows_v1(baseline, limit=1001)
    for symbol in etabs_w3.__all__:
        assert hasattr(structural_lib, symbol), symbol
