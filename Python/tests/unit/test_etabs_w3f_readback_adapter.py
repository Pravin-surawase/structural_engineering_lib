"""Synthetic installed-shape fixtures; no COM, file or model activity."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from structural_lib.core.analysis_contracts import EvidenceStateV1
from structural_lib.services.contracts import etabs_w3 as w3
from structural_lib.services.etabs_model_foundation_adapter import (
    ETABSFoundationAdapterRequestV1,
    normalize_etabs_foundation_readback_v1,
)
from tests.unit.test_etabs_w3f_snapshots import _definition_request


def _request() -> ETABSFoundationAdapterRequestV1:
    source = _definition_request()
    frame = source.baseline.frames[0]
    name, section = frame.source_unique_name, frame.section.section_name
    material = frame.section.material_property_label
    selection = source.catalogue.result_selections[-1]
    pattern = source.catalogue.load_patterns[0].name
    raw: dict[str, Any] = {
        f"FrameObj.GetPoints:{name}": [
            frame.point_i.point_name,
            frame.point_j.point_name,
            0,
        ],
        f"FrameObj.GetSection:{name}": [section, frame.section.auto_select_list, 0],
        f"FrameObj.GetLocalAxes:{name}": [
            frame.local_axis.local_axis_rotation_deg,
            False,
            0,
        ],
        f"FrameObj.GetSpringAssignment:{name}": ["", 0],
        f"FrameObj.GetReleases:{name}": [
            [False] * 6,
            [False] * 6,
            [0.0] * 6,
            [0.0] * 6,
            0,
        ],
        f"FrameObj.GetEndLengthOffset:{name}": [True, 0.1, 0.2, 0.5, 0],
        f"FrameObj.GetInsertionPoint_1:{name}": [
            5,
            False,
            True,
            True,
            [0.0] * 3,
            [0.0] * 3,
            "Global",
            0,
        ],
        f"FrameObj.GetModifiers:{name}": [[1.0] * 8, 0],
        f"PropFrame.GetMaterial:{section}": [material, 0],
        f"PropFrame.GetSectProps:{section}": [
            0.15,
            0.125,
            0.125,
            0.002817,
            0.001125,
            0.003125,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            0,
        ],
        f"PropFrame.GetModifiers:{section}": [[1.0] * 8, 0],
        f"PropMaterial.GetMPIsotropic:{material}": [
            25000000.0,
            0.2,
            1e-5,
            10416666.666,
            0,
        ],
        f"PropMaterial.GetWeightAndMass:{material}": [25.0, 2.5, 0],
        f"FrameObj.GetLoadPoint:{name}": [
            1,
            [name],
            [pattern],
            [2],
            ["Local"],
            [3],
            [0.5],
            [1.5],
            [-12.0],
            0,
        ],
        f"FrameObj.GetLoadDistributed:{name}": [
            1,
            [name],
            [pattern],
            [1],
            ["Global"],
            [10],
            [0.0],
            [1.0],
            [0.0],
            [3.0],
            [10.0],
            [10.0],
            0,
        ],
    }
    names = []
    for point in (frame.point_i, frame.point_j):
        name = point.point_name
        names.append(name)
        raw.update(
            {
                f"PointObj.GetCoordCartesian:{name}": [
                    point.x_mm / 1000.0,
                    point.y_mm / 1000.0,
                    point.z_mm / 1000.0,
                    0,
                ],
                f"PointObj.GetLocalAxes:{name}": [0.0, 0.0, 0.0, False, 0],
                f"PointObj.GetRestraint:{name}": [
                    [True, True, True, False, False, False],
                    0,
                ],
                f"PointObj.GetSpringAssignment:{name}": ["", 0],
                f"PointObj.IsSpringCoupled:{name}": [False, 0],
                f"PointObj.GetSpring:{name}": [
                    [1000.0, 2000.0, 3000.0, 4.0, 5.0, 6.0],
                    0,
                ],
                f"PointObj.GetLoadForce:{name}": [0, *([None] * 10), 0],
                f"Results.JointDispl:{name}": [
                    1,
                    [name],
                    ["elm:" + name],
                    [selection.name],
                    [""],
                    [0.0],
                    [-0.001],
                    [0.002],
                    [-0.003],
                    [0.01],
                    [-0.02],
                    [0.03],
                    0,
                ],
                f"Results.JointReact:{name}": [
                    1,
                    [name],
                    ["elm:" + name],
                    [selection.name],
                    [""],
                    [0.0],
                    [-1.0],
                    [2.0],
                    [-3.0],
                    [4.0],
                    [-5.0],
                    [6.0],
                    0,
                ],
            }
        )
    return ETABSFoundationAdapterRequestV1(
        baseline=source.baseline,
        catalogue=source.catalogue,
        context=source.context,
        member_ids=source.member_ids,
        joint_names=tuple(names),
        displacement_joint_names=tuple(names),
        reaction_joint_names=tuple(names),
        selection_id=selection.selection_id,
        raw_calls=raw,
        diaphragm_slab_context=source.diaphragm_slab_context,
        require_calibration_fields=True,
    )


def test_normalized_dimensions_signs_mirrors_and_exact_source_rows() -> None:
    result = normalize_etabs_foundation_readback_v1(_request())
    assert result.status is w3.W3BuildStatusV1.ACCEPTED, result.issues
    definition = result.model_definition.value
    displacements, reactions = result.displacements.value, result.reactions.value
    assert definition and displacements and reactions
    assert definition.calibration_fields_complete
    frame = definition.frame_definitions[0]
    assert frame.insertion_point.value.mirror_local_3 is True
    assert frame.end_offsets.value.length_i_mm == 100.0
    assert frame.section.value.material.value.elastic_modulus_nmm2 == 25000.0
    assert frame.section.value.material.value.mass_density_kg_per_m3 == 2500.0
    assert frame.section.value.inertia_3_mm4 == 3125000000.0
    assert frame.assigned_loads.value[0].value == -12.0
    assert frame.assigned_loads.value[1].start_value == 0.01
    assert frame.assigned_loads.value[1].direction_basis == "GRAVITY_NEGATIVE_GLOBAL_Z"
    assert definition.joints[0].springs.value.terms[0].stiffness == 1.0
    assert definition.joints[0].restraint_basis == "JOINT_LOCAL"
    assert displacements.row_count == reactions.row_count == 2
    assert displacements.rows[0].u1_mm == -1.0
    assert displacements.rows[0].r2_rad == -0.02
    assert reactions.rows[0].m2_knm == -5.0
    assert all(row.coordinate_system == "JOINT_LOCAL" for row in reactions.rows)
    assert w3.verify_etabs_model_definition_snapshot_hash_v1(definition)
    assert w3.verify_etabs_displacement_snapshot_hash_v1(displacements)
    assert w3.verify_etabs_reaction_snapshot_hash_v1(reactions)


def test_list_tuple_readback_is_deterministic() -> None:
    request = _request()
    first = normalize_etabs_foundation_readback_v1(request)
    assert first.status is w3.W3BuildStatusV1.ACCEPTED, first.issues
    calls = {
        key: tuple(tuple(x) if isinstance(x, list) else x for x in value)
        for key, value in request.raw_calls.items()
    }
    second = normalize_etabs_foundation_readback_v1(
        request.model_copy(update={"raw_calls": calls})
    )
    assert first == second


@pytest.mark.parametrize(
    "key,index,value",
    [
        ("FrameObj.GetReleases:B1", -1, 1),
        ("FrameObj.GetReleases:B1", -1, False),
        ("FrameObj.GetPoints:B1", 0, "wrong"),
        ("FrameObj.GetLocalAxes:B1", 1, True),
        ("FrameObj.GetSpringAssignment:B1", 0, "line-spring"),
        ("FrameObj.GetInsertionPoint_1:B1", 2, 1),
        ("FrameObj.GetModifiers:B1", 0, [1.0] * 7),
        ("PointObj.GetCoordCartesian:P1", 0, 0.01),
        ("PointObj.GetLocalAxes:P1", 3, True),
        ("Results.JointDispl:P1", 0, 2),
        ("Results.JointReact:P1", 1, ["wrong"]),
        ("Results.JointReact:P1", 7, [float("inf")]),
    ],
)
def test_malformed_or_unproved_readback_has_no_partial_value(
    key: str, index: int, value: Any
) -> None:
    request = _request()
    calls = deepcopy(request.raw_calls)
    calls[key][index] = value
    result = normalize_etabs_foundation_readback_v1(
        request.model_copy(update={"raw_calls": calls})
    )
    assert result.status is w3.W3BuildStatusV1.BLOCKED
    assert result.model_definition.state is EvidenceStateV1.BLOCKED
    assert result.displacements.value is result.reactions.value is None


@pytest.mark.parametrize("reason", ["nonzero", "coupled", "named"])
def test_spring_unavailability_is_explicit_and_required_mode_blocks(
    reason: str,
) -> None:
    request = _request()
    if reason == "nonzero":
        request.raw_calls["PointObj.GetSpring:P1"][-1] = 1
    elif reason == "coupled":
        request.raw_calls["PointObj.IsSpringCoupled:P1"][0] = True
    else:
        request.raw_calls["PointObj.GetSpringAssignment:P1"][0] = "named-property"
    assert (
        normalize_etabs_foundation_readback_v1(request).status
        is w3.W3BuildStatusV1.BLOCKED
    )
    optional = normalize_etabs_foundation_readback_v1(
        request.model_copy(update={"require_calibration_fields": False})
    )
    assert optional.status is w3.W3BuildStatusV1.ACCEPTED, optional.issues
    assert (
        optional.model_definition.value.joints[0].springs.state
        is EvidenceStateV1.UNAVAILABLE
    )
    assert not optional.model_definition.value.calibration_fields_complete


@pytest.mark.parametrize("container", [list, tuple])
@pytest.mark.parametrize("scope", ["joint", "frame", "both"])
def test_unsuccessful_assignment_is_unavailable_not_zero_or_global_failure(
    container: Any,
    scope: str,
) -> None:
    request = _request()
    if scope in ("joint", "both"):
        request.raw_calls["PointObj.GetSpringAssignment:P1"] = container([None, 1])
        request.raw_calls["PointObj.IsSpringCoupled:P1"] = container([False, 1])
        request.raw_calls["PointObj.GetSpring:P1"] = container([[], 1])
    if scope in ("frame", "both"):
        request.raw_calls["FrameObj.GetSpringAssignment:B1"] = container([None, 1])
    required = normalize_etabs_foundation_readback_v1(request)
    assert required.status is w3.W3BuildStatusV1.BLOCKED
    assert required.model_definition.value is required.displacements.value is None
    optional = normalize_etabs_foundation_readback_v1(
        request.model_copy(update={"require_calibration_fields": False})
    )
    assert optional.status is w3.W3BuildStatusV1.ACCEPTED, optional.issues
    definition = optional.model_definition.value
    assert definition is not None and not definition.calibration_fields_complete
    if scope in ("joint", "both"):
        assert definition.joints[0].springs.state is EvidenceStateV1.UNAVAILABLE
        assert definition.joints[0].springs.value is None
    if scope in ("frame", "both"):
        assert (
            definition.frame_definitions[0].line_spring_assignment.state
            is EvidenceStateV1.UNAVAILABLE
        )
        assert definition.frame_definitions[0].line_spring_assignment.value is None
    assert (
        optional.displacements.state
        is optional.reactions.state
        is EvidenceStateV1.PRESENT
    )
    assert optional.displacements.value.rows[0].u1_mm == -1.0
    assert optional.reactions.value.rows[0].m2_knm == -5.0
    assert w3.verify_etabs_model_definition_snapshot_hash_v1(definition)
    assert request.raw_calls.get("FrameObj.GetSpringAssignment:B1")[-1] == (
        1 if scope in ("frame", "both") else 0
    )


@pytest.mark.parametrize("owner,name", [("PointObj", "P1"), ("FrameObj", "B1")])
@pytest.mark.parametrize(
    "raw", [[None, 0], [False, 0], [None, True], [None], [None, "1"]]
)
def test_malformed_assignment_still_blocks_optional_read(
    owner: str,
    name: str,
    raw: Any,
) -> None:
    request = _request()
    request.raw_calls[f"{owner}.GetSpringAssignment:{name}"] = raw
    result = normalize_etabs_foundation_readback_v1(
        request.model_copy(update={"require_calibration_fields": False})
    )
    assert result.status is w3.W3BuildStatusV1.BLOCKED
    assert (
        result.model_definition.value
        is result.displacements.value
        is result.reactions.value
        is None
    )


def test_no_result_group_never_becomes_zero_or_partial_snapshot() -> None:
    request = _request()
    request.raw_calls["Results.JointReact:P1"] = [0, *([None] * 11), 0]
    result = normalize_etabs_foundation_readback_v1(request)
    assert result.status is w3.W3BuildStatusV1.ACCEPTED
    assert result.displacements.state is EvidenceStateV1.PRESENT
    assert result.reactions.state is EvidenceStateV1.UNAVAILABLE
    assert result.reactions.value is None


def test_nonempty_joint_load_cannot_discard_undocumented_step() -> None:
    request = _request()
    request.raw_calls["PointObj.GetLoadForce:P1"] = [
        1,
        ["P1"],
        ["DEAD"],
        [1],
        ["Global"],
        *([[0.0]] * 6),
        0,
    ]
    result = normalize_etabs_foundation_readback_v1(
        request.model_copy(update={"require_calibration_fields": False})
    )
    assert result.status is w3.W3BuildStatusV1.ACCEPTED
    assert (
        result.model_definition.value.joints[0].assigned_loads.state
        is EvidenceStateV1.UNAVAILABLE
    )


def test_capacity_units_unaccounted_calls_and_postflight_fail_closed() -> None:
    request = _request()
    for changed in (
        request.model_copy(update={"capacity_limit": 1}),
        request.model_copy(
            update={"raw_calls": {**request.raw_calls, "unexpected": [0]}}
        ),
        request.model_copy(
            update={
                "context": request.context.model_copy(update={"present_units_after": 5})
            }
        ),
        request.model_copy(
            update={
                "context": request.context.model_copy(
                    update={"state_after_sha256": "f" * 64}
                )
            }
        ),
    ):
        assert (
            normalize_etabs_foundation_readback_v1(changed).status
            is w3.W3BuildStatusV1.BLOCKED
        )
