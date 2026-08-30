# SPDX-License-Identifier: MIT
"""W3F readback normalization, without COM, files, setters or analysis.

Only the installed-audited kN/m/C readback is accepted. Raw calls are retained
by the caller and hashed here; absent spring/result evidence is never zero.
This module is an adapter, not a new root public analysis API.
"""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any, Literal

from pydantic import Field, ValidationError

from structural_lib.core import analysis_contracts as core
from structural_lib.services.contracts import etabs_w3 as w3
from structural_lib.services.contracts.common import StrictPublicModel
from structural_lib.services.etabs_beam_baseline import ETABSBeamBaselineV1

_DOFS = ("u1", "u2", "u3", "r1", "r2", "r3")
_Dof = Literal["U1", "U2", "U3", "R1", "R2", "R3"]
_SPRING_DOFS: tuple[_Dof, ...] = ("U1", "U2", "U3", "R1", "R2", "R3")
_MODIFIERS = (
    "axial_area",
    "shear_area_2",
    "shear_area_3",
    "torsion",
    "inertia_2",
    "inertia_3",
    "mass",
    "weight",
)
_DIRECTIONS = {
    1: "LOCAL_1",
    2: "LOCAL_2",
    3: "LOCAL_3",
    4: "CSYS_X",
    5: "CSYS_Y",
    6: "CSYS_Z",
    7: "PROJECTED_CSYS_X",
    8: "PROJECTED_CSYS_Y",
    9: "PROJECTED_CSYS_Z",
    10: "GRAVITY_NEGATIVE_GLOBAL_Z",
    11: "PROJECTED_GRAVITY_NEGATIVE_GLOBAL_Z",
}


class ETABSFoundationAdapterRequestV1(StrictPublicModel):
    baseline: ETABSBeamBaselineV1
    catalogue: w3.ETABSResultCatalogueV1
    context: w3.ETABSModelContextV1
    member_ids: tuple[str, ...] = Field(min_length=1, max_length=5)
    joint_names: tuple[str, ...] = Field(min_length=1, max_length=16)
    displacement_joint_names: tuple[str, ...] = Field(min_length=1, max_length=16)
    reaction_joint_names: tuple[str, ...] = Field(min_length=1, max_length=16)
    selection_id: str = Field(min_length=1)
    raw_calls: dict[str, Any]
    diaphragm_slab_context: core.EvidenceValueV1[str]
    require_calibration_fields: bool = False
    capacity_limit: int = Field(default=2000, ge=1, le=2000)


class ETABSFoundationAdapterResultV1(StrictPublicModel):
    status: w3.W3BuildStatusV1 = Field(strict=False)
    issues: tuple[w3.W3BuildIssueV1, ...]
    model_definition: core.EvidenceValueV1[w3.ETABSModelDefinitionSnapshotV1]
    displacements: core.EvidenceValueV1[w3.ETABSDisplacementSnapshotV1]
    reactions: core.EvidenceValueV1[w3.ETABSReactionSnapshotV1]
    raw_readback_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    limitations: tuple[str, ...]


def _digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    ).hexdigest()


def _present(value: Any, reference: str) -> core.EvidenceValueV1[Any]:
    return core.EvidenceValueV1(
        state=core.EvidenceStateV1.PRESENT, value=value, source_references=(reference,)
    )


def _absent(
    code: str, reference: str, *, blocked: bool = False
) -> core.EvidenceValueV1[Any]:
    return core.EvidenceValueV1(
        state=(
            core.EvidenceStateV1.BLOCKED
            if blocked
            else core.EvidenceStateV1.UNAVAILABLE
        ),
        value=None,
        reason_code=code,
        message=code.replace("_", " "),
        source_references=(reference,),
    )


def _number(value: Any) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
    ):
        raise ValueError("W3F_NONFINITE_OR_NONNUMERIC")
    return float(value)


def _integer(value: Any) -> int:
    if type(value) is not int:
        raise ValueError("W3F_INTEGER_REQUIRED")
    return value


def _boolean(value: Any) -> bool:
    if type(value) is not bool:
        raise ValueError("W3F_BOOLEAN_REQUIRED")
    return value


def _array(value: Any, count: int) -> tuple[Any, ...]:
    if count == 0 and value is None:
        return ()
    if not isinstance(value, (tuple, list)) or len(value) != count:
        raise ValueError("W3F_ARRAY_COUNT_MISMATCH")
    return tuple(value)


class _Readback:
    def __init__(self, request: ETABSFoundationAdapterRequestV1) -> None:
        self.request = request
        self.rows = 0
        self.used: set[str] = set()

    def out(
        self, operation: str, name: str, count: int, *, optional: bool = False
    ) -> tuple[Any, ...] | None:
        key = f"{operation}:{name}"
        self.used.add(key)
        raw = self.request.raw_calls[key]
        try:
            values = _array(raw, count + 1)
        except ValueError as exc:
            raise ValueError(f"{exc}:{key}") from exc
        if _integer(values[-1]) != 0:
            if optional:
                return None
            raise ValueError(f"W3F_CSI_RETURN_CODE:{key}:{values[-1]}")
        return values[:-1]

    def required(self, operation: str, name: str, count: int) -> tuple[Any, ...]:
        value = self.out(operation, name, count)
        assert value is not None
        return value

    def table(
        self, operation: str, name: str, arrays: int
    ) -> tuple[tuple[Any, ...], ...]:
        values = self.required(operation, name, arrays + 1)
        count = _integer(values[0])
        if count < 0 or self.rows + count > self.request.capacity_limit:
            raise ValueError("W3F_CAPACITY_EXCEEDED")
        self.rows += count
        return tuple(zip(*(_array(value, count) for value in values[1:]), strict=True))


def _flags(raw: Any) -> core.ModelDofRestraintsV1:
    return core.ModelDofRestraintsV1(
        **dict(zip(_DOFS, map(_boolean, _array(raw, 6)), strict=True))
    )


def _spring(raw: Any) -> core.ModelSpringV1:
    return core.ModelSpringV1(
        coordinate_system="JOINT_LOCAL",
        representation="DIAGONAL",
        terms=tuple(
            core.ModelSpringTermV1(
                resultant_dof=dof,
                displacement_dof=dof,
                stiffness=_number(value) / (1000.0 if index < 3 else 1.0),
                unit="kN/mm" if index < 3 else "kN.m/rad",
            )
            for index, (dof, value) in enumerate(
                zip(_SPRING_DOFS, _array(raw, 6), strict=True)
            )
        ),
    )


def _modifiers(raw: Any) -> core.ModelModifiersV1:
    return core.ModelModifiersV1(
        **dict(zip(_MODIFIERS, map(_number, _array(raw, 8)), strict=True))
    )


def _point(raw: Any) -> core.ModelPointV1:
    xyz = tuple(_number(value) * 1000.0 for value in _array(raw, 3))
    return core.ModelPointV1(x_mm=xyz[0], y_mm=xyz[1], z_mm=xyz[2])


def _joint(read: _Readback, name: str, point: Any) -> core.ModelJointDefinitionV1:
    ref = "w3f:joint:" + name
    current = _point(read.required("PointObj.GetCoordCartesian", name, 3))
    # The immutable baseline retains its original mm values. A 1e-6 mm bound
    # verifies the independent m readback; it is not a geometric-change allowance.
    if any(
        abs(getattr(current, axis) - getattr(point, axis)) > 1e-6
        for axis in ("x_mm", "y_mm", "z_mm")
    ):
        raise ValueError("W3F_COORDINATE_IDENTITY_MISMATCH")
    axes = read.required("PointObj.GetLocalAxes", name, 4)
    angles = tuple(_number(value) for value in axes[:3])
    if _boolean(axes[3]):
        raise ValueError("W3F_ADVANCED_JOINT_AXES_UNSUPPORTED")
    axes_basis = (
        "JOINT_LOCAL; degrees a,b,c="
        + json.dumps(angles)
        + "; rotations about 3, resulting 2, resulting 1"
    )
    restraint = _flags(read.required("PointObj.GetRestraint", name, 1)[0])
    assignment = read.required("PointObj.GetSpringAssignment", name, 1)[0]
    coupled = read.out("PointObj.IsSpringCoupled", name, 1, optional=True)
    spring = read.out("PointObj.GetSpring", name, 1, optional=True)
    if assignment:
        spring_value = _absent(
            "W3F_NAMED_SPRING_REQUIRES_SEPARATE_PROPERTY_AND_LINK_SCOPE", ref
        )
    elif coupled is None or spring is None:
        spring_value = _absent("W3F_SPRING_ABSENCE_OR_FAILURE_NOT_DISTINGUISHABLE", ref)
    elif _boolean(coupled[0]):
        spring_value = _absent("W3F_COUPLED_SPRING_LAYOUT_NOT_PROVED", ref)
    else:
        spring_value = _present(_spring(spring[0]), ref)
    load_rows = read.table("PointObj.GetLoadForce", name, 10)
    # LcStep is present in installed metadata but has no documented meaning.
    # No nonempty joint-load assignment is silently collapsed across steps.
    loads = (
        _absent("W3F_JOINT_LOAD_STEP_SEMANTICS_NOT_PROVED", ref)
        if load_rows
        else _present((), ref)
    )
    if any(row[0] != name for row in load_rows):
        raise ValueError("W3F_JOINT_LOAD_IDENTITY_MISMATCH")
    return core.ModelJointDefinitionV1(
        joint_id="joint:" + name,
        source_joint_name=name,
        point=core.ModelPointV1(x_mm=point.x_mm, y_mm=point.y_mm, z_mm=point.z_mm),
        restraint_basis="JOINT_LOCAL",
        restraints=_present(restraint, ref),
        springs=spring_value,
        local_axes_basis=_present(axes_basis, ref),
        assigned_loads=loads,
        evidence_reference=ref,
    )


def _frame_loads(read: _Readback, name: str) -> tuple[Any, ...]:
    patterns = {
        item.name: item.pattern_id for item in read.request.catalogue.load_patterns
    }
    loads: list[core.ModelFramePointLoadV1 | core.ModelFrameDistributedLoadV1] = []
    for kind, op, count in (
        ("POINT", "FrameObj.GetLoadPoint", 8),
        ("DISTRIBUTED", "FrameObj.GetLoadDistributed", 11),
    ):
        for index, row in enumerate(read.table(op, name, count)):
            source, pattern, raw_kind, csys, direction = row[:5]
            action = _integer(raw_kind)
            direction = _integer(direction)
            if (
                source != name
                or pattern not in patterns
                or action not in (1, 2)
                or direction not in _DIRECTIONS
            ):
                raise ValueError("W3F_FRAME_LOAD_IDENTITY_OR_ENUM_INVALID")
            if (direction <= 3) != (csys == "Local") or (
                direction >= 10 and csys != "Global"
            ):
                raise ValueError("W3F_FRAME_LOAD_COORDINATE_BASIS_INVALID")
            if kind == "POINT" and direction in (7, 8, 9, 11):
                raise ValueError("W3F_PROJECTED_POINT_LOAD_UNSUPPORTED")
            ref = f"w3f:{op}:{name}:{index}"
            common = {
                "assignment_id": ref,
                "pattern_id": patterns[pattern],
                "coordinate_system": csys,
                "direction_basis": _DIRECTIONS[direction],
                "action_kind": "FORCE" if action == 1 else "MOMENT",
                "evidence_reference": ref,
            }
            if kind == "POINT":
                _number(row[5])  # relative distance is retained in raw evidence
                loads.append(
                    core.ModelFramePointLoadV1(
                        **common,
                        distance_mm=_number(row[6]) * 1000.0,
                        value=_number(row[7]),
                        unit="kN" if action == 1 else "kN.m",
                    )
                )
            else:
                _number(row[5])
                _number(row[6])
                loads.append(
                    core.ModelFrameDistributedLoadV1(
                        **common,
                        start_distance_mm=_number(row[7]) * 1000.0,
                        end_distance_mm=_number(row[8]) * 1000.0,
                        start_value=_number(row[9]) / 1000.0,
                        end_value=_number(row[10]) / 1000.0,
                        unit="kN/mm" if action == 1 else "kN.m/mm",
                    )
                )
    return tuple(loads)


def _frame(read: _Readback, frame: Any) -> core.ModelFrameDefinitionV1:
    name = frame.source_unique_name
    ref = "w3f:frame:" + name
    if read.required("FrameObj.GetPoints", name, 2) != (
        frame.point_i.point_name,
        frame.point_j.point_name,
    ):
        raise ValueError("W3F_FRAME_CONNECTIVITY_MISMATCH")
    section_name, auto = read.required("FrameObj.GetSection", name, 2)
    if (section_name, auto) != (
        frame.section.section_name,
        frame.section.auto_select_list,
    ):
        raise ValueError("W3F_FRAME_SECTION_MISMATCH")
    angle, advanced = read.required("FrameObj.GetLocalAxes", name, 2)
    if _boolean(advanced) or _number(angle) != frame.local_axis.local_axis_rotation_deg:
        raise ValueError("W3F_FRAME_AXES_MISMATCH")
    if read.required("FrameObj.GetSpringAssignment", name, 1)[0]:
        raise ValueError("W3F_LINE_SPRING_OUTSIDE_FROZEN_CONTRACT")
    release = read.required("FrameObj.GetReleases", name, 4)
    start = _spring(release[2]).model_copy(update={"coordinate_system": "FRAME_LOCAL"})
    end = _spring(release[3]).model_copy(update={"coordinate_system": "FRAME_LOCAL"})
    offsets = read.required("FrameObj.GetEndLengthOffset", name, 4)
    insertion = read.required("FrameObj.GetInsertionPoint_1", name, 7)
    material_name = read.required("PropFrame.GetMaterial", section_name, 1)[0]
    if material_name != frame.section.material_property_label:
        raise ValueError("W3F_MATERIAL_IDENTITY_MISMATCH")
    elastic = read.required("PropMaterial.GetMPIsotropic", material_name, 4)
    weight, mass = read.required("PropMaterial.GetWeightAndMass", material_name, 2)
    properties = tuple(
        map(_number, read.required("PropFrame.GetSectProps", section_name, 12))
    )
    material = core.ModelMaterialV1(
        material_label=material_name,
        elastic_modulus_nmm2=_number(elastic[0]) / 1000.0,
        poisson_ratio=_number(elastic[1]),
        mass_density_kg_per_m3=_number(mass) * 1000.0,
        weight_density_kn_per_m3=_number(weight),
        evidence_reference=ref,
    )
    section = core.ModelSectionV1(
        section_label=section_name,
        material_label=material_name,
        area_mm2=properties[0] * 1e6,
        shear_area_2_mm2=properties[1] * 1e6,
        shear_area_3_mm2=properties[2] * 1e6,
        torsional_constant_mm4=properties[3] * 1e12,
        inertia_2_mm4=properties[4] * 1e12,
        inertia_3_mm4=properties[5] * 1e12,
        material=_present(material, ref),
        modifiers=_present(
            _modifiers(read.required("PropFrame.GetModifiers", section_name, 1)[0]), ref
        ),
        evidence_reference=ref,
    )
    return core.ModelFrameDefinitionV1(
        member_id=frame.member_id,
        source_frame_name=name,
        joint_i_id="joint:" + frame.point_i.point_name,
        joint_j_id="joint:" + frame.point_j.point_name,
        section=_present(section, ref),
        releases=_present(
            core.ModelReleasesV1(
                end_i=_flags(release[0]),
                end_j=_flags(release[1]),
                partial_fixity_i=start,
                partial_fixity_j=end,
            ),
            ref,
        ),
        end_offsets=_present(
            core.ModelEndOffsetsV1(
                automatic=_boolean(offsets[0]),
                length_i_mm=_number(offsets[1]) * 1000.0,
                length_j_mm=_number(offsets[2]) * 1000.0,
                rigid_zone_factor=_number(offsets[3]),
            ),
            ref,
        ),
        insertion_point=_present(
            core.ModelInsertionPointV1(
                cardinal_point=_integer(insertion[0]),
                mirror_local_2=_boolean(insertion[1]),
                mirror_local_3=_boolean(insertion[2]),
                transform_stiffness=_boolean(insertion[3]),
                offset_i=_point(insertion[4]),
                offset_j=_point(insertion[5]),
                coordinate_system=insertion[6],
            ),
            ref,
        ),
        object_modifiers=_present(
            _modifiers(read.required("FrameObj.GetModifiers", name, 1)[0]), ref
        ),
        assigned_loads=_present(_frame_loads(read, name), ref),
        evidence_reference=ref,
    )


def _result(
    read: _Readback, definition: w3.ETABSModelDefinitionSnapshotV1, kind: str
) -> core.EvidenceValueV1[Any]:
    request = read.request
    selections = [
        item
        for item in request.catalogue.result_selections
        if item.selection_id == request.selection_id
    ]
    if len(selections) != 1:
        raise ValueError("W3F_RESULT_SELECTION_IDENTITY_INVALID")
    selection = selections[0]
    operation = "Results.JointDispl" if kind == "displacement" else "Results.JointReact"
    rows: list[core.JointDisplacementRowV1 | core.JointReactionRowV1] = []
    counts: list[core.JointResultSourceCountV1] = []
    retained_joints: list[str] = []
    result_row: core.JointDisplacementRowV1 | core.JointReactionRowV1
    requested_names = (
        request.displacement_joint_names
        if kind == "displacement"
        else request.reaction_joint_names
    )
    missing = False
    for name in requested_names:
        raw_rows = read.table(operation, name, 11)
        selected = [
            (index, row)
            for index, row in enumerate(raw_rows)
            if row[2] == selection.name
        ]
        # Preserve all returned selections in raw evidence. No zero reaction or
        # displacement is fabricated for a joint that returned no selected row.
        if not selected:
            missing = True
            continue
        joint_id = "joint:" + name
        retained_joints.append(joint_id)
        counts.append(
            core.JointResultSourceCountV1(
                joint_id=joint_id,
                selection_id=selection.selection_id,
                source_row_count=len(selected),
                evidence_reference=f"w3f:{operation}:{name}",
            )
        )
        for index, row in selected:
            if row[0] != name or not isinstance(row[1], str) or not row[1]:
                raise ValueError("W3F_RESULT_OBJECT_ELEMENT_MISMATCH")
            common = {
                "row_id": f"w3f:{operation}:{name}:{index}",
                "joint_id": joint_id,
                "object_name": name,
                "element_name": row[1],
                "selection_id": selection.selection_id,
                "output_case_name": selection.name,
                "step_type": row[3],
                "step_number": _number(row[4]),
                "source_row_index": index,
                "model_identity_sha256": request.catalogue.model_identity_sha256,
                "baseline_sha256": definition.baseline_sha256,
                "catalogue_sha256": definition.catalogue_sha256,
                "coordinate_system": "JOINT_LOCAL",
                "evidence_reference": f"w3f:{operation}:{name}:{index}",
                "row_sha256": "0" * 64,
            }
            values = tuple(map(_number, row[5:]))
            if kind == "displacement":
                result_row = core.JointDisplacementRowV1(
                    **common,
                    u1_mm=values[0] * 1000.0,
                    u2_mm=values[1] * 1000.0,
                    u3_mm=values[2] * 1000.0,
                    r1_rad=values[3],
                    r2_rad=values[4],
                    r3_rad=values[5],
                )
            else:
                result_row = core.JointReactionRowV1(
                    **common,
                    f1_kn=values[0],
                    f2_kn=values[1],
                    f3_kn=values[2],
                    m1_knm=values[3],
                    m2_knm=values[4],
                    m3_knm=values[5],
                )
            result_row = result_row.model_copy(
                update={
                    "row_sha256": _digest(
                        result_row.model_dump(mode="json", exclude={"row_sha256"})
                    )
                }
            )
            rows.append(result_row)
    if missing or not rows:
        return _absent("W3F_REQUESTED_JOINT_RESULT_GROUP_UNAVAILABLE", operation)
    arguments: dict[str, Any] = {
        "model_definition": definition,
        "catalogue": request.catalogue,
        "context": request.context,
        "joint_ids": tuple(retained_joints),
        "selection_ids": (selection.selection_id,),
        "source_row_counts": tuple(counts),
        "capacity_limit": request.capacity_limit,
        "rows": tuple(rows),
    }
    result = (
        w3.build_etabs_displacement_snapshot_v1(
            w3.ETABSDisplacementBuildRequestV1(**arguments)
        )
        if kind == "displacement"
        else w3.build_etabs_reaction_snapshot_v1(
            w3.ETABSReactionBuildRequestV1(**arguments)
        )
    )
    if result.snapshot is None:
        raise ValueError(";".join(issue.code for issue in result.issues))
    return _present(result.snapshot, operation)


def normalize_etabs_foundation_readback_v1(
    request: ETABSFoundationAdapterRequestV1, /
) -> ETABSFoundationAdapterResultV1:
    """Normalize an exact bounded recorded getter set; never call a provider."""
    digest = "0" * 64
    try:
        digest = _digest(request.raw_calls)
        if (
            request.context.present_units_before != 6
            or request.context.present_units_after != 6
        ):
            raise ValueError("W3F_ONLY_PROVED_KN_M_C_READBACK_SUPPORTED")
        if len(set(request.member_ids)) != len(request.member_ids) or len(
            set(request.joint_names)
        ) != len(request.joint_names):
            raise ValueError("W3F_DUPLICATE_SCOPE")
        for names in (request.displacement_joint_names, request.reaction_joint_names):
            if len(set(names)) != len(names) or not set(names) <= set(
                request.joint_names
            ):
                raise ValueError("W3F_RESULT_JOINT_SCOPE_INVALID")
        read = _Readback(request)
        frames = {frame.member_id: frame for frame in request.baseline.frames}
        points = {
            point.point_name: point
            for frame in request.baseline.frames
            for point in (frame.point_i, frame.point_j)
        }
        joints = tuple(_joint(read, name, points[name]) for name in request.joint_names)
        definitions = tuple(_frame(read, frames[name]) for name in request.member_ids)
        built = w3.build_etabs_model_definition_snapshot_v1(
            w3.ETABSModelDefinitionBuildRequestV1(
                baseline=request.baseline,
                catalogue=request.catalogue,
                context=request.context,
                member_ids=request.member_ids,
                joint_ids=tuple(joint.joint_id for joint in joints),
                joints=joints,
                frame_definitions=definitions,
                diaphragm_slab_context=request.diaphragm_slab_context,
                require_calibration_fields=request.require_calibration_fields,
                capacity_limit=request.capacity_limit,
            )
        )
        if built.snapshot is None:
            raise ValueError(";".join(issue.code for issue in built.issues))
        displacement = _result(read, built.snapshot, "displacement")
        reaction = _result(read, built.snapshot, "reaction")
        if set(request.raw_calls) != read.used:
            raise ValueError("W3F_UNACCOUNTED_RAW_CALLS")
        return ETABSFoundationAdapterResultV1(
            status=w3.W3BuildStatusV1.ACCEPTED,
            issues=(),
            model_definition=_present(built.snapshot, "w3f:definition"),
            displacements=displacement,
            reactions=reaction,
            raw_readback_sha256=digest,
            limitations=(
                "Read-only normalized evidence, not a solver or calibration acceptance.",
                "Any missing requested joint group makes that entire result snapshot UNAVAILABLE; no full-model reaction balance is claimed.",
                "Required spring/joint-load/slab holds must be resolved before dependent calibration.",
            ),
        )
    except (KeyError, TypeError, ValueError, ValidationError) as exc:
        issue = w3.W3BuildIssueV1(
            code="W3F_READBACK_BLOCKED", path="raw_calls", message=str(exc)
        )
        absent = _absent("W3F_READBACK_BLOCKED", "w3f:readback", blocked=True)
        return ETABSFoundationAdapterResultV1(
            status=w3.W3BuildStatusV1.BLOCKED,
            issues=(issue,),
            model_definition=absent,
            displacements=absent,
            reactions=absent,
            raw_readback_sha256=digest,
            limitations=("No partial normalized snapshots are accepted.",),
        )
