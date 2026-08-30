"""Pure W3F normalized snapshots: no COM, application or model file I/O."""

from __future__ import annotations

import inspect
from typing import Any

import pytest
from pydantic import ValidationError

import structural_lib
from structural_lib.core import analysis_contracts as core
from structural_lib.services.contracts import etabs_w3 as w3
from tests.unit.test_etabs_w3_contracts import (
    _accepted_catalogue,
    _baseline,
    _catalogue_request,
    _linear_case,
    _not_applicable,
    _present,
)


def _absent(state: core.EvidenceStateV1) -> core.EvidenceValueV1[Any]:
    return core.EvidenceValueV1(
        state=state,
        value=None,
        reason_code="FIXTURE_" + state.value,
        message="Explicit synthetic evidence scope.",
        source_references=("fixture:W3F",),
    )


def _zero_flags() -> core.ModelDofRestraintsV1:
    return core.ModelDofRestraintsV1(
        u1=False, u2=False, u3=False, r1=False, r2=False, r3=False
    )


def _zero_spring() -> core.ModelSpringV1:
    return core.ModelSpringV1(
        coordinate_system="Local",
        representation="DIAGONAL",
        terms=tuple(
            core.ModelSpringTermV1(
                resultant_dof=dof,
                displacement_dof=dof,
                stiffness=0.0,
                unit="kN/mm" if dof.startswith("U") else "kN.m/rad",
            )
            for dof in ("U1", "U2", "U3", "R1", "R2", "R3")
        ),
    )


def _definition_request() -> w3.ETABSModelDefinitionBuildRequestV1:
    baseline, catalogue = _baseline(), _accepted_catalogue()
    context = w3.ETABSModelContextV1(
        model=baseline.model,
        present_units_before=6,
        present_units_after=6,
        database_units_enum=6,
        runtime_identity_sha256="b" * 64,
        getter_matrix_sha256="d" * 64,
        analysis_statuses=catalogue.analysis_statuses,
        output_selection_states=tuple(
            w3.ETABSOutputSelectionStateV1(kind=kind, name=item.name, selected=True)
            for kind, items in (
                ("CASE", catalogue.load_cases),
                ("COMBINATION", catalogue.response_combinations),
            )
            for item in items
        ),
        state_before_sha256="e" * 64,
        state_after_sha256="e" * 64,
        normalization_evidence_reference="fixture:explicit-units",
    )
    modifiers = core.ModelModifiersV1(
        axial_area=1.0,
        shear_area_2=1.0,
        shear_area_3=1.0,
        torsion=1.0,
        inertia_2=1.0,
        inertia_3=1.0,
        mass=1.0,
        weight=1.0,
    )
    section = core.ModelSectionV1(
        section_label="R300x500",
        material_label="M25",
        area_mm2=150000.0,
        shear_area_2_mm2=125000.0,
        shear_area_3_mm2=125000.0,
        torsional_constant_mm4=2817000000.0,
        inertia_2_mm4=1125000000.0,
        inertia_3_mm4=3125000000.0,
        material=_present(
            core.ModelMaterialV1(
                material_label="M25",
                elastic_modulus_nmm2=25000.0,
                poisson_ratio=0.2,
                mass_density_kg_per_m3=2500.0,
                weight_density_kn_per_m3=25.0,
                evidence_reference="fixture:material",
            )
        ),
        modifiers=_present(modifiers),
        evidence_reference="fixture:section",
    )
    joints = tuple(
        core.ModelJointDefinitionV1(
            joint_id="joint:" + point.point_name,
            source_joint_name=point.point_name,
            point=core.ModelPointV1(x_mm=point.x_mm, y_mm=point.y_mm, z_mm=point.z_mm),
            restraint_basis="GLOBAL",
            restraints=_present(_zero_flags()),
            springs=_present(_zero_spring()),
            local_axes_basis=_present("Global axes; no rotation"),
            assigned_loads=_present(()),
            evidence_reference="fixture:joint",
        )
        for point in (baseline.frames[0].point_i, baseline.frames[0].point_j)
    )
    zero = core.ModelPointV1(x_mm=0.0, y_mm=0.0, z_mm=0.0)
    frame = core.ModelFrameDefinitionV1(
        member_id="member:1",
        source_frame_name="B1",
        joint_i_id="joint:P1",
        joint_j_id="joint:P2",
        section=_present(section),
        releases=_present(
            core.ModelReleasesV1(
                end_i=_zero_flags(),
                end_j=_zero_flags(),
                partial_fixity_i=_zero_spring(),
                partial_fixity_j=_zero_spring(),
            )
        ),
        end_offsets=_present(
            core.ModelEndOffsetsV1(
                automatic=False, length_i_mm=0.0, length_j_mm=0.0, rigid_zone_factor=0.0
            )
        ),
        insertion_point=_present(
            core.ModelInsertionPointV1(
                cardinal_point=5,
                mirror_local_2=False,
                mirror_local_3=False,
                transform_stiffness=True,
                coordinate_system="Global",
                offset_i=zero,
                offset_j=zero,
            )
        ),
        object_modifiers=_present(modifiers),
        assigned_loads=_present(
            (
                core.ModelFrameDistributedLoadV1(
                    assignment_id="load:0",
                    pattern_id=catalogue.load_patterns[0].pattern_id,
                    coordinate_system="Global",
                    direction_basis="Global Z",
                    action_kind="FORCE",
                    start_distance_mm=0.0,
                    end_distance_mm=3000.0,
                    start_value=-0.01,
                    end_value=-0.01,
                    unit="kN/mm",
                    evidence_reference="fixture:load",
                ),
            )
        ),
        evidence_reference="fixture:frame",
    )
    return w3.ETABSModelDefinitionBuildRequestV1(
        baseline=baseline,
        catalogue=catalogue,
        context=context,
        member_ids=("member:1",),
        joint_ids=("joint:P1", "joint:P2"),
        joints=joints,
        frame_definitions=(frame,),
        diaphragm_slab_context=_not_applicable("fixture:isolated-beam-no-slab"),
        require_calibration_fields=True,
        capacity_limit=20,
    )


def _definition() -> w3.ETABSModelDefinitionSnapshotV1:
    result = w3.build_etabs_model_definition_snapshot_v1(_definition_request())
    assert result.status is w3.W3BuildStatusV1.ACCEPTED, result.issues
    assert result.snapshot is not None
    return result.snapshot


def _results_request(kind: str) -> Any:
    request = _definition_request()
    definition = _definition()
    selection = request.catalogue.result_selections[-1]
    rows = []
    for index, joint in enumerate(definition.joints):
        kwargs = {
            "row_id": f"row:{index}",
            "joint_id": joint.joint_id,
            "object_name": joint.source_joint_name,
            "element_name": "element:" + joint.source_joint_name,
            "selection_id": selection.selection_id,
            "output_case_name": selection.name,
            "step_type": "Max",
            "step_number": 0.0,
            "source_row_index": index,
            "model_identity_sha256": request.catalogue.model_identity_sha256,
            "baseline_sha256": definition.baseline_sha256,
            "catalogue_sha256": definition.catalogue_sha256,
            "coordinate_system": "Global",
            "evidence_reference": f"fixture:row:{index}",
            "row_sha256": "0" * 64,
        }
        if kind == "displacement":
            row = core.JointDisplacementRowV1(
                **kwargs,
                u1_mm=-1.0,
                u2_mm=2.0,
                u3_mm=-3.0,
                r1_rad=0.001,
                r2_rad=-0.002,
                r3_rad=0.0,
            )
        else:
            row = core.JointReactionRowV1(
                **kwargs,
                f1_kn=-10.0,
                f2_kn=20.0,
                f3_kn=-30.0,
                m1_knm=40.0,
                m2_knm=-50.0,
                m3_knm=0.0,
            )
        rows.append(
            row.model_copy(update={"row_sha256": w3._w3f_digest(row, "row_sha256")})
        )
    cls = (
        w3.ETABSDisplacementBuildRequestV1
        if kind == "displacement"
        else w3.ETABSReactionBuildRequestV1
    )
    return cls(
        model_definition=definition,
        catalogue=request.catalogue,
        context=request.context,
        joint_ids=definition.joint_ids,
        selection_ids=(selection.selection_id,),
        source_row_counts=tuple(
            core.JointResultSourceCountV1(
                joint_id=joint.joint_id,
                selection_id=selection.selection_id,
                source_row_count=1,
                evidence_reference="fixture:source-count",
            )
            for joint in definition.joints
        ),
        capacity_limit=10,
        rows=tuple(rows),
    )


def test_model_definition_complete_semantics_and_deterministic_hash() -> None:
    snapshot = _definition()
    assert snapshot.calibration_fields_complete
    assert snapshot.frames[0].local_axis.length_mm == 3000.0
    assert snapshot.frames[0].section.auto_select_list == ""
    assert snapshot.frame_definitions[0].assigned_loads.value[0].start_value == -0.01
    assert snapshot.frame_definitions[0].releases.value.end_i.u1 is False
    assert (
        snapshot.context.present_units_before
        == snapshot.context.present_units_after
        == 6
    )
    assert w3.verify_etabs_model_definition_snapshot_hash_v1(snapshot)
    assert snapshot == _definition()
    restored = w3.ETABSModelDefinitionSnapshotV1.model_validate_json(
        snapshot.model_dump_json(), strict=False
    )
    assert restored == snapshot
    assert not w3.verify_etabs_model_definition_snapshot_hash_v1(
        snapshot.model_copy(update={"joint_ids": ("changed",)})
    )


@pytest.mark.parametrize("state", list(core.EvidenceStateV1)[1:])
def test_five_states_never_overload_missing_mandatory_topology(
    state: core.EvidenceStateV1,
) -> None:
    req = _definition_request()
    frame = req.frame_definitions[0].model_copy(update={"section": _absent(state)})
    req = req.model_copy(update={"frame_definitions": (frame,)})
    result = w3.build_etabs_model_definition_snapshot_v1(req)
    assert result.status is w3.W3BuildStatusV1.BLOCKED and result.snapshot is None
    optional = w3.build_etabs_model_definition_snapshot_v1(
        req.model_copy(update={"require_calibration_fields": False})
    )
    if state is core.EvidenceStateV1.BLOCKED:
        assert optional.snapshot is None
    else:
        assert (
            optional.snapshot is not None
            and not optional.snapshot.calibration_fields_complete
        )


@pytest.mark.parametrize(
    "change",
    [
        "units",
        "state",
        "lock",
        "status",
        "selection",
        "capacity",
        "member",
        "joint",
        "file",
        "version",
        "pattern",
        "length",
    ],
)
def test_definition_identity_state_scope_and_capacity_fail_closed(change: str) -> None:
    req = _definition_request()
    ctx = req.context
    if change == "units":
        ctx = ctx.model_copy(update={"present_units_after": 5})
    elif change == "state":
        ctx = ctx.model_copy(update={"state_after_sha256": "f" * 64})
    elif change == "lock":
        ctx = ctx.model_copy(
            update={"model": ctx.model.model_copy(update={"model_locked": False})}
        )
    elif change == "status":
        ctx = ctx.model_copy(update={"analysis_statuses": ctx.analysis_statuses[:-1]})
    elif change == "selection":
        ctx = ctx.model_copy(
            update={"output_selection_states": ctx.output_selection_states[:-1]}
        )
    elif change == "version":
        ctx = ctx.model_copy(
            update={"model": ctx.model.model_copy(update={"etabs_version": "wrong"})}
        )
    elif change == "file":
        ctx = ctx.model_copy(
            update={
                "model": ctx.model.model_copy(
                    update={"model_path": r"C:\Models\Wrong.edb"}
                )
            }
        )
    elif change == "capacity":
        req = req.model_copy(update={"capacity_limit": 1})
    elif change == "member":
        req = req.model_copy(update={"member_ids": ("wrong",)})
    elif change == "joint":
        req = req.model_copy(
            update={
                "joints": (
                    req.joints[0].model_copy(update={"source_joint_name": "wrong"}),
                    req.joints[1],
                )
            }
        )
    else:
        frame = req.frame_definitions[0]
        load = frame.assigned_loads.value[0].model_copy(
            update=(
                {"pattern_id": "wrong"}
                if change == "pattern"
                else {"end_distance_mm": 4000.0}
            )
        )
        req = req.model_copy(
            update={
                "frame_definitions": (
                    frame.model_copy(update={"assigned_loads": _present((load,))}),
                )
            }
        )
    result = w3.build_etabs_model_definition_snapshot_v1(
        req.model_copy(update={"context": ctx})
    )
    assert result.status is w3.W3BuildStatusV1.BLOCKED and result.snapshot is None
    assert result.issues


@pytest.mark.parametrize("kind", ["displacement", "reaction"])
def test_signed_six_component_rows_and_lossless_hashes(kind: str) -> None:
    req = _results_request(kind)
    builder = getattr(w3, f"build_etabs_{kind}_snapshot_v1")
    verify = getattr(w3, f"verify_etabs_{kind}_snapshot_hash_v1")
    result = builder(req)
    assert result.status is w3.W3BuildStatusV1.ACCEPTED, result.issues
    snapshot = result.snapshot
    assert snapshot.row_count == 2 and snapshot.rows == req.rows
    assert snapshot.rows[0].source_row_index == 0
    assert snapshot.rows[0].output_case_name == "ULS-OUTER"
    values = (
        ("u1_mm", "u2_mm", "u3_mm", "r1_rad", "r2_rad", "r3_rad")
        if kind == "displacement"
        else ("f1_kn", "f2_kn", "f3_kn", "m1_knm", "m2_knm", "m3_knm")
    )
    assert [getattr(snapshot.rows[0], key) > 0 for key in values] == [
        False,
        True,
        False,
        True,
        False,
        False,
    ]
    assert verify(snapshot)
    assert (
        type(snapshot).model_validate_json(snapshot.model_dump_json(), strict=False)
        == snapshot
    )
    assert not verify(snapshot.model_copy(update={"rows": snapshot.rows[::-1]}))


@pytest.mark.parametrize("kind", ["displacement", "reaction"])
@pytest.mark.parametrize(
    "change",
    [
        "capacity",
        "missing",
        "duplicate",
        "object",
        "selection",
        "hash",
        "parent",
        "unselected",
    ],
)
def test_result_rows_complete_or_blocked_without_partial_output(
    kind: str, change: str
) -> None:
    req = _results_request(kind)
    if change == "capacity":
        req = req.model_copy(update={"capacity_limit": 1})
    elif change == "missing":
        req = req.model_copy(update={"rows": req.rows[:1]})
    elif change == "duplicate":
        req = req.model_copy(update={"rows": req.rows + (req.rows[0],)})
    elif change == "parent":
        req = req.model_copy(
            update={
                "model_definition": req.model_definition.model_copy(
                    update={"baseline_sha256": "f" * 64}
                )
            }
        )
    elif change == "unselected":
        req = req.model_copy(
            update={
                "context": req.context.model_copy(
                    update={
                        "output_selection_states": tuple(
                            item.model_copy(update={"selected": False})
                            for item in req.context.output_selection_states
                        )
                    }
                )
            }
        )
    else:
        fields = {
            "object": {"object_name": "wrong"},
            "selection": {"output_case_name": "wrong"},
            "hash": {"row_sha256": "f" * 64},
        }
        req = req.model_copy(
            update={
                "rows": (req.rows[0].model_copy(update=fields[change]), req.rows[1])
            }
        )
    result = getattr(w3, f"build_etabs_{kind}_snapshot_v1")(req)
    assert result.status is w3.W3BuildStatusV1.BLOCKED and result.snapshot is None


def test_unit_typed_springs_loads_and_strict_finite_contracts() -> None:
    with pytest.raises(ValidationError):
        core.ModelSpringTermV1(
            resultant_dof="U1", displacement_dof="R1", stiffness=1.0, unit="kN/mm"
        )
    with pytest.raises(ValidationError):
        core.ModelSpringV1(
            coordinate_system="Local",
            representation="DIAGONAL",
            terms=_zero_spring().terms[:-1],
        )
    with pytest.raises(ValidationError):
        core.ModelPointV1(x_mm=float("nan"), y_mm=0.0, z_mm=0.0)
    with pytest.raises(ValidationError):
        core.ModelPointV1(x_mm=0.0, y_mm=0.0, z_mm=0.0, unknown=True)
    load = _definition_request().frame_definitions[0].assigned_loads.value[0]
    bad = load.model_dump()
    bad["unit"] = "kN"
    with pytest.raises(ValidationError):
        core.ModelFrameDistributedLoadV1.model_validate(bad)


def test_unrequested_unfinished_case_is_retained_but_requested_cases_must_finish() -> (
    None
):
    req = _definition_request()
    catalogue_request = _catalogue_request()
    spare = _linear_case("case:spare", "SPARE", 2)
    spare_status = catalogue_request.analysis_statuses[0].model_copy(
        update={
            "status_id": spare.analysis_status_id,
            "case_id": spare.case_id,
            "raw_status_code": 1,
            "state": core.AnalysisStateV1.NOT_RUN,
        }
    )
    catalogue = w3.build_etabs_result_catalogue_v1(
        catalogue_request.model_copy(
            update={
                "load_cases": catalogue_request.load_cases + (spare,),
                "analysis_statuses": catalogue_request.analysis_statuses
                + (spare_status,),
            }
        )
    ).catalogue
    assert catalogue is not None
    context = req.context.model_copy(
        update={
            "analysis_statuses": catalogue.analysis_statuses,
            "output_selection_states": req.context.output_selection_states
            + (
                w3.ETABSOutputSelectionStateV1(
                    kind="CASE", name="SPARE", selected=False
                ),
            ),
        }
    )
    assert (
        w3.build_etabs_model_definition_snapshot_v1(
            req.model_copy(
                update={
                    "catalogue": catalogue,
                    "context": context,
                }
            )
        ).snapshot
        is not None
    )

    result_req = _results_request("reaction")
    statuses = tuple(
        (
            item.model_copy(
                update={
                    "state": core.AnalysisStateV1.NOT_FINISHED,
                    "raw_status_code": 3,
                }
            )
            if item.case_id == "case:live"
            else item
        )
        for item in result_req.catalogue.analysis_statuses
    )
    catalogue = result_req.catalogue.model_copy(update={"analysis_statuses": statuses})
    catalogue = catalogue.model_copy(
        update={
            "catalogue_sha256": w3._sha(
                catalogue.model_dump(mode="json", exclude={"catalogue_sha256"})
            )
        }
    )
    result = w3.build_etabs_reaction_snapshot_v1(
        result_req.model_copy(
            update={
                "catalogue": catalogue,
                "context": result_req.context.model_copy(
                    update={"analysis_statuses": statuses}
                ),
            }
        )
    )
    assert result.snapshot is None
    assert "W3F_SELECTED_RESULTS_NOT_FINISHED" in {
        issue.code for issue in result.issues
    }


def test_exact_public_signatures_and_no_partial_accepted_result() -> None:
    for stem in ("model_definition", "displacement", "reaction"):
        for prefix in ("build", "verify"):
            name = f"{prefix}_etabs_{stem}_snapshot" + (
                "_hash_v1" if prefix == "verify" else "_v1"
            )
            function = getattr(w3, name)
            assert getattr(structural_lib, name) is function
            params = list(inspect.signature(function).parameters.values())
            assert (
                len(params) == 1 and params[0].kind is inspect.Parameter.POSITIONAL_ONLY
            )
    with pytest.raises(ValidationError):
        w3.ETABSModelDefinitionBuildResultV1(
            status=w3.W3BuildStatusV1.ACCEPTED, issues=(), snapshot=None
        )


def test_declared_source_counts_prevent_within_group_truncation() -> None:
    req = _results_request("displacement")
    first = req.source_row_counts[0].model_copy(update={"source_row_count": 2})
    result = w3.build_etabs_displacement_snapshot_v1(
        req.model_copy(
            update={
                "source_row_counts": (first, req.source_row_counts[1]),
            }
        )
    )
    assert result.snapshot is None
    assert "W3F_SOURCE_ROW_COUNT_MISMATCH" in {issue.code for issue in result.issues}


def test_joint_assigned_loads_are_signed_and_part_of_definition_identity() -> None:
    req = _definition_request()
    load = core.ModelJointLoadV1(
        assignment_id="joint-load:0",
        pattern_id=req.catalogue.load_patterns[0].pattern_id,
        coordinate_system="Global",
        f1_kn=0.0,
        f2_kn=-2.0,
        f3_kn=-5.0,
        m1_knm=1.0,
        m2_knm=-1.0,
        m3_knm=0.0,
        evidence_reference="fixture:nodal-load",
    )
    joint = req.joints[0].model_copy(update={"assigned_loads": _present((load,))})
    result = w3.build_etabs_model_definition_snapshot_v1(
        req.model_copy(update={"joints": (joint, req.joints[1])})
    )
    assert result.snapshot is not None
    assert result.snapshot.joints[0].assigned_loads.value == (load,)
    assert result.snapshot.snapshot_sha256 != _definition().snapshot_sha256
