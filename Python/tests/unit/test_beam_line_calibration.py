"""W3H L1 software tests; synthetic criteria are NOT project calibration criteria."""

from __future__ import annotations

import hashlib
import inspect
import json

import pytest
from pydantic import BaseModel, ValidationError

from structural_lib import compare_beam_line_to_reference_v1
from structural_lib.core.analysis_contracts import (
    BeamActionRowV1,
    EvidenceValueV1,
    JointDisplacementRowV1,
    JointReactionRowV1,
)
from structural_lib.core.beam_line_calibration import (
    BeamLineActionMappingV1,
    BeamLineCalibrationV1,
    BeamLineComparisonCriteriaV1,
    BeamLineComparisonRequestV1,
    BeamLineComponentToleranceV1,
    BeamLineJointMappingV1,
    BeamLineReferenceIdentityV1,
    BeamLineReferenceMappingV1,
    BeamLineReferenceV1,
)
from structural_lib.services.beam_line import solve_beam_line_linear_v1
from tests.unit.test_beam_line import request as solver_request


def digest(value, omit=None):
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json", exclude={omit} if omit else set())
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def seal(value, field):
    return value.model_copy(update={field: digest(value, field)})


def present(value):
    return {
        "state": "PRESENT",
        "value": value,
        "source_references": ("synthetic-independent-reference",),
    }


def missing(state="NOT_REQUESTED"):
    return {
        "state": state,
        "reason_code": "TEST_MISSING",
        "message": "Explicit synthetic missing evidence",
        "source_references": ("fixture",),
    }


def comparison_request(*, joints=True):
    result = solve_beam_line_linear_v1(solver_request()).result
    assert result is not None
    identity = BeamLineReferenceIdentityV1(
        model_file_sha256="4" * 64,
        model_identity_sha256="5" * 64,
        baseline_sha256="6" * 64,
        catalogue_sha256="2" * 64,
        model_definition_sha256="1" * 64,
        scenario_definition_sha256="3" * 64,
        analysis_settings_sha256="7" * 64,
        etabs_version="SYNTHETIC_NOT_INSTALLED",
        selection_id="selection-G",
        result_kind="CASE",
        result_name="G",
        step_type="Single",
        step_number=0.0,
    )
    common = {
        "model_identity_sha256": identity.model_identity_sha256,
        "baseline_sha256": identity.baseline_sha256,
        "catalogue_sha256": identity.catalogue_sha256,
        "selection_id": identity.selection_id,
        "output_case_name": "G",
        "step_type": "Single",
        "step_number": 0.0,
    }
    rows, mappings = [], []
    # Independent simply supported UDL formulas, not copied solver actions.
    for i, station in enumerate(result.spans[0].stations):
        x = station.distance_from_flexible_start_m
        row = BeamActionRowV1(
            **common,
            row_id=f"row-{i}",
            member_id="member-1",
            source_frame_name="1",
            station_id=f"station-{i}",
            selection_kind="CASE",
            selection_name="G",
            object_name="1",
            object_station_mm=x * 1000,
            element_name="1-1",
            element_station_mm=x * 1000,
            source_row_index=i,
            p_kn=-8.0,
            v2_kn=10.0 * (x - 3.0),
            v3_kn=4.0,
            t_knm=-2.0,
            m2_knm=7.0,
            m3_knm=5.0 * x * (6.0 - x),
            local_axis_basis="synthetic vertical local-2",
            row_sha256="0" * 64,
        )
        rows.append(seal(row, "row_sha256"))
        mappings.append(
            BeamLineActionMappingV1(
                reference_row_id=row.row_id,
                member_id=row.member_id,
                span_id="S0",
                solver_station_index=i,
                station_side="CONTINUOUS",
                source_station_origin_mm=0.0,
                source_distance_direction=1,
                local_axis_basis=row.local_axis_basis,
                shear_component="v2_kn",
                moment_component="m3_knm",
                shear_sign=-1,
                moment_sign=1,
            )
        )
    displacements, reactions, dm, rm = [], [], [], []
    for i in range(2):
        joint = dict(
            **common,
            joint_id=f"J{i}",
            object_name=f"J{i}",
            element_name=f"J{i}",
            source_row_index=i,
            coordinate_system="GLOBAL",
            evidence_reference="closed-form-UDL",
        )
        rotation = (-1 if i == 0 else 1) * 10.0 * 6.0**3 / (24 * 24000)
        disp = seal(
            JointDisplacementRowV1(
                **joint,
                row_id=f"d{i}",
                u1_mm=0.0,
                u2_mm=0.0,
                u3_mm=0.0,
                r1_rad=0.0,
                r2_rad=rotation,
                r3_rad=0.0,
                row_sha256="0" * 64,
            ),
            "row_sha256",
        )
        reaction = seal(
            JointReactionRowV1(
                **joint,
                row_id=f"r{i}",
                f1_kn=0.0,
                f2_kn=0.0,
                f3_kn=30.0,
                m1_knm=0.0,
                m2_knm=0.0,
                m3_knm=0.0,
                row_sha256="0" * 64,
            ),
            "row_sha256",
        )
        displacements.append(disp)
        reactions.append(reaction)
        data = {
            "joint_id": f"J{i}",
            "node_id": f"N{i}",
            "coordinate_system": "GLOBAL",
            "translation_axis": 3,
            "rotation_axis": 2,
            "translation_sign": 1,
            "rotation_sign": 1,
        }
        dm.append(BeamLineJointMappingV1(**data, reference_row_id=disp.row_id))
        rm.append(BeamLineJointMappingV1(**data, reference_row_id=reaction.row_id))
    reference = BeamLineReferenceV1(
        identity=identity,
        source_basis="SYNTHETIC_REFERENCE",
        topology_review=present(
            "UDL simply supported closed-form fixture; no slab or spring"
        ),
        linear_response_review=present("Single linear static synthetic case"),
        source_references=(
            "test_beam_line.py closed-form references; NOT a project model",
        ),
        actions=tuple(rows),
        displacements=present(tuple(displacements)) if joints else missing(),
        reactions=present(tuple(reactions)) if joints else missing(),
        reference_sha256="0" * 64,
    )
    reference = seal(reference, "reference_sha256")
    mapping = BeamLineReferenceMappingV1(
        solver_scenario_id="reference",
        solver_result_id="G",
        reference_selection_id=identity.selection_id,
        actions=tuple(mappings),
        displacements=tuple(dm) if joints else (),
        reactions=tuple(rm) if joints else (),
        assumptions=("Independent simply supported UDL benchmark",),
        reviewed_basis=present(
            "Synthetic mapping checked against the closed form, not a real model"
        ),
    )
    components = ["SHEAR_KN", "MOMENT_KNM"]
    if joints:
        components.extend(
            ["DISPLACEMENT_MM", "ROTATION_RAD", "REACTION_KN", "REACTION_KNM"]
        )
    criteria = BeamLineComparisonCriteriaV1(
        criteria_id="synthetic-roundoff-only",
        declaration_reference="test fixture before comparison",
        declared_before_comparison=True,
        station_distance_tolerance_mm=1e-9,
        tolerances=tuple(
            BeamLineComponentToleranceV1(component=c, absolute=1e-9, relative=1e-9)
            for c in components
        ),
    )
    return BeamLineComparisonRequestV1(
        solver_result=result,
        current_identity=present(identity),
        reference=present(reference),
        mapping=present(mapping),
        criteria=present(criteria),
    )


def with_reference(req, **updates):
    ref = seal(req.reference.value.model_copy(update=updates), "reference_sha256")
    return req.model_copy(
        update={"reference": EvidenceValueV1[BeamLineReferenceV1](**present(ref))}
    )


def with_mapping(req, **updates):
    value = req.mapping.value.model_copy(update=updates)
    return req.model_copy(
        update={
            "mapping": EvidenceValueV1[BeamLineReferenceMappingV1](**present(value))
        }
    )


def not_comparable(req, code):
    result = compare_beam_line_to_reference_v1(req)
    assert result.status == "NOT_COMPARABLE"
    assert result.comparisons == ()
    assert result.issues[0].reason_code == code
    return result


@pytest.mark.parametrize("joints, count", [(True, 50), (False, 42)])
def test_independent_udl_reference_with_signed_components_and_optional_modes(
    joints, count
):
    req = comparison_request(joints=joints)
    result = compare_beam_line_to_reference_v1(req)
    assert result.status == "CALIBRATED", result.issues
    assert len(result.comparisons) == count
    assert not result.issues
    assert result.independent_frame_analysis == "HELD_NOT_SUPPORTED"
    assert result.evidence_claim == "NUMERIC_COMPARISON_ONLY"
    assert result.reference_basis.value == "SYNTHETIC_REFERENCE"
    assert result.professional_approval == "NOT_PROVIDED"
    assert any(row.reference_value < 0 for row in result.comparisons)
    assert req.reference.value.actions[0].t_knm == -2.0
    assert req.reference.value.actions[0].p_kn == -8.0
    assert result.request_sha256 == digest(req)
    assert result.calibration_sha256 == digest(result, "calibration_sha256")
    roundtrip = BeamLineComparisonRequestV1.model_validate_json(req.model_dump_json())
    assert compare_beam_line_to_reference_v1(roundtrip) == result
    assert BeamLineCalibrationV1.model_validate_json(result.model_dump_json()) == result
    assert (
        inspect.signature(compare_beam_line_to_reference_v1).parameters["request"].kind
        == inspect.Parameter.POSITIONAL_ONLY
    )


@pytest.mark.parametrize(
    "field", ["current_identity", "reference", "mapping", "criteria"]
)
@pytest.mark.parametrize(
    "state", ["UNAVAILABLE", "NOT_REQUESTED", "NOT_APPLICABLE", "BLOCKED"]
)
def test_five_state_missing_evidence_is_not_a_default(field, state):
    req = comparison_request()
    raw = req.model_dump()
    raw[field] = missing(state)
    not_comparable(BeamLineComparisonRequestV1.model_validate(raw), "MISSING_EVIDENCE")


@pytest.mark.parametrize(
    "field",
    [
        "model_file_sha256",
        "model_identity_sha256",
        "baseline_sha256",
        "catalogue_sha256",
        "model_definition_sha256",
        "scenario_definition_sha256",
        "analysis_settings_sha256",
        "etabs_version",
        "selection_id",
        "result_kind",
        "result_name",
        "step_type",
        "step_number",
    ],
)
def test_every_reference_identity_change_invalidates_calibration(field):
    req = comparison_request()
    replacement = (
        1.0
        if field == "step_number"
        else ("f" * 64 if field.endswith("sha256") else "changed")
    )
    if field == "result_kind":
        replacement = "COMBINATION"
    identity = req.current_identity.value.model_copy(update={field: replacement})
    req = req.model_copy(
        update={
            "current_identity": EvidenceValueV1[BeamLineReferenceIdentityV1](
                **present(identity)
            )
        }
    )
    not_comparable(req, "REFERENCE_INVALIDATED")


@pytest.mark.parametrize("component, value", [("v2_kn", 300.0), ("m3_knm", -90.0)])
def test_signed_error_out_of_band_retains_all_rows(component, value):
    req = comparison_request()
    rows = list(req.reference.value.actions)
    rows[10] = seal(rows[10].model_copy(update={component: value}), "row_sha256")
    result = compare_beam_line_to_reference_v1(with_reference(req, actions=tuple(rows)))
    assert result.status == "OUT_OF_BAND"
    assert len(result.comparisons) == 50
    assert any(not row.within_tolerance for row in result.comparisons)
    assert not result.issues


def test_absolute_plus_relative_uses_reference_and_explicit_units():
    req = comparison_request()
    rows = list(req.reference.value.reactions.value)
    rows[0] = seal(rows[0].model_copy(update={"f3_kn": 29.0}), "row_sha256")
    req = with_reference(
        req,
        reactions=EvidenceValueV1[tuple[JointReactionRowV1, ...]](
            **present(tuple(rows))
        ),
    )
    criteria = req.criteria.value
    tolerances = tuple(
        (
            t.model_copy(update={"absolute": 0.42, "relative": 0.02})
            if t.component == "REACTION_KN"
            else t
        )
        for t in criteria.tolerances
    )
    req = req.model_copy(
        update={
            "criteria": EvidenceValueV1[BeamLineComparisonCriteriaV1](
                **present(criteria.model_copy(update={"tolerances": tolerances}))
            )
        }
    )
    result = compare_beam_line_to_reference_v1(req)
    row = next(
        r
        for r in result.comparisons
        if r.reference_row_id == "r0" and r.component == "REACTION_KN"
    )
    assert row.allowed_error == pytest.approx(1.0)
    assert row.absolute_error == pytest.approx(1.0)
    assert row.within_tolerance


@pytest.mark.parametrize("field", ["topology_review", "linear_response_review"])
def test_unavailable_topology_or_response_never_calibrates(field):
    req = comparison_request()
    not_comparable(
        with_reference(req, **{field: EvidenceValueV1[str](**missing("UNAVAILABLE"))}),
        "MISSING_EVIDENCE",
    )


def test_missing_reaction_cannot_silently_downgrade_declared_mode():
    req = comparison_request()
    req = with_reference(
        req,
        reactions=EvidenceValueV1[tuple[JointReactionRowV1, ...]](
            **missing("UNAVAILABLE")
        ),
    )
    not_comparable(req, "MISSING_EVIDENCE")


@pytest.mark.parametrize(
    "change",
    ["missing", "duplicate", "bad_member", "wrong_station", "wrong_side", "wrong_axis"],
)
def test_exact_station_mapping_or_no_partial_result(change):
    req = comparison_request()
    rows = list(req.mapping.value.actions)
    expected = "ACTION_MAPPING"
    if change == "missing":
        rows.pop()
        expected = "INCOMPLETE_MAPPING"
    elif change == "duplicate":
        rows[-1] = rows[0]
        expected = "DUPLICATE_MAPPING"
    elif change == "bad_member":
        rows = [r.model_copy(update={"member_id": "wrong"}) for r in rows]
    elif change == "wrong_station":
        rows = [r.model_copy(update={"source_station_origin_mm": 1000.0}) for r in rows]
        expected = "STATION_MAPPING"
    elif change == "wrong_side":
        rows[0] = rows[0].model_copy(update={"station_side": "LEFT"})
        expected = "STATION_MAPPING"
    else:
        rows = [r.model_copy(update={"local_axis_basis": "wrong axes"}) for r in rows]
    not_comparable(with_mapping(req, actions=tuple(rows)), expected)


@pytest.mark.parametrize("layer", ["reference", "row", "solver", "binding"])
def test_tampered_hash_or_cross_snapshot_binding_fails_closed(layer):
    req = comparison_request()
    if layer == "reference":
        ref = req.reference.value.model_copy(update={"source_references": ("changed",)})
        req = req.model_copy(
            update={"reference": EvidenceValueV1[BeamLineReferenceV1](**present(ref))}
        )
        code = "REFERENCE_HASH"
    elif layer == "row":
        rows = list(req.reference.value.actions)
        rows[0] = rows[0].model_copy(update={"p_kn": 77.0})
        req = with_reference(req, actions=tuple(rows))
        code = "ROW_HASH"
    elif layer == "solver":
        result = req.solver_result.model_copy(update={"request_sha256": "0" * 64})
        req = req.model_copy(update={"solver_result": result})
        code = "SOLVER_HASH"
    else:
        raw = req.solver_result.request.model_copy(
            update={"catalogue_sha256": "f" * 64}
        )
        result = solve_beam_line_linear_v1(raw).result
        req = req.model_copy(update={"solver_result": result})
        code = "SOLVER_REFERENCE_BINDING"
    not_comparable(req, code)


@pytest.mark.parametrize("field", ["absolute", "relative"])
@pytest.mark.parametrize("value", [-1.0, float("nan"), float("inf")])
def test_invalid_tolerance_is_not_accepted(field, value):
    data = {"component": "SHEAR_KN", "absolute": 0.0, "relative": 0.0}
    data[field] = value
    with pytest.raises(ValidationError):
        BeamLineComponentToleranceV1(**data)


def test_explicit_internal_scenario_mapping_does_not_assume_etabs_names_are_ids():
    req = comparison_request()
    analysis = req.solver_result.request
    analysis = analysis.model_copy(
        update={
            "load_cases": (
                analysis.load_cases[0].model_copy(
                    update={"case_id": "internal-gravity"}
                ),
            ),
            "scenario": analysis.scenario.model_copy(
                update={
                    "scenario_id": "internal-comparison",
                    "result_id": "internal-gravity",
                }
            ),
        }
    )
    req = req.model_copy(
        update={"solver_result": solve_beam_line_linear_v1(analysis).result}
    )
    not_comparable(req, "SOLVER_REFERENCE_BINDING")
    req = with_mapping(
        req,
        solver_scenario_id="internal-comparison",
        solver_result_id="internal-gravity",
    )
    assert compare_beam_line_to_reference_v1(req).status == "CALIBRATED"


@pytest.mark.parametrize("wrong", ["mixed_plane", "row_sign_flip", "joint_axis"])
def test_no_selective_sign_flips_or_mixed_bending_planes(wrong):
    req = comparison_request()
    if wrong == "joint_axis":
        rows = tuple(
            r.model_copy(update={"rotation_axis": r.translation_axis})
            for r in req.mapping.value.reactions
        )
        req = with_mapping(req, reactions=rows)
        code = "PLANE_MAPPING"
    else:
        rows = list(req.mapping.value.actions)
        field, value = (
            ("moment_component", "m2_knm")
            if wrong == "mixed_plane"
            else ("shear_sign", 1)
        )
        rows[0] = rows[0].model_copy(update={field: value})
        req = with_mapping(req, actions=tuple(rows))
        code = "PLANE_MAPPING" if wrong == "mixed_plane" else "INCONSISTENT_FRAME_BASIS"
    not_comparable(req, code)


def test_nonzero_displacement_mm_and_rotation_cantilever_closed_form():
    req = comparison_request()
    analysis = req.solver_result.request
    supports = (
        analysis.supports[0].model_copy(update={"rotation": "FIXED"}),
        analysis.supports[1].model_copy(update={"vertical": "FREE"}),
    )
    result = solve_beam_line_linear_v1(
        analysis.model_copy(update={"supports": supports})
    ).result
    assert result is not None
    req = req.model_copy(update={"solver_result": result})
    rows = tuple(
        seal(
            r.model_copy(
                update={
                    "v2_kn": -10 * (6 - r.object_station_mm / 1000),
                    "m3_knm": -5 * (6 - r.object_station_mm / 1000) ** 2,
                }
            ),
            "row_sha256",
        )
        for r in req.reference.value.actions
    )
    drows = list(req.reference.value.displacements.value)
    drows[0] = seal(drows[0].model_copy(update={"r2_rad": 0.0}), "row_sha256")
    drows[1] = seal(
        drows[1].model_copy(
            update={
                "u3_mm": -10 * 6**4 / (8 * 24000) * 1000,
                "r2_rad": -10 * 6**3 / (6 * 24000),
            }
        ),
        "row_sha256",
    )
    rrows = list(req.reference.value.reactions.value)
    rrows[0] = seal(
        rrows[0].model_copy(update={"f3_kn": 60.0, "m2_knm": 180.0}), "row_sha256"
    )
    rrows[1] = seal(rrows[1].model_copy(update={"f3_kn": 0.0}), "row_sha256")
    req = with_reference(
        req,
        actions=rows,
        displacements=EvidenceValueV1[tuple[JointDisplacementRowV1, ...]](
            **present(tuple(drows))
        ),
        reactions=EvidenceValueV1[tuple[JointReactionRowV1, ...]](
            **present(tuple(rrows))
        ),
    )
    output = compare_beam_line_to_reference_v1(req)
    assert output.status == "CALIBRATED", output
    displacement = next(
        r
        for r in output.comparisons
        if r.reference_row_id == "d1" and r.component == "DISPLACEMENT_MM"
    )
    assert displacement.reference_value == -67.5
    assert displacement.local_value == pytest.approx(-67.5)
