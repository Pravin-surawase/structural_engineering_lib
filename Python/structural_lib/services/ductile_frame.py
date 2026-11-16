"""PROJECT03 orchestration through the positioned joint and member owners."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from structural_lib.codes.is13920.ductile_frame_actions import (
    BEAM_CONNECTIONS,
    frame_hold_reason,
    resolve_frame_actions,
)
from structural_lib.codes.is13920.joint_strength import JointStrengthDomainError
from structural_lib.codes.is13920.project03_frame_cage import (
    FrameCageDomainError,
    reconcile_frame_marks,
    resolve_shared_beam,
)
from structural_lib.codes.is13920.project03_member_strength import check_project_members
from structural_lib.core.result_contract import (
    CalculationStatus,
    EngineeringStatus,
    FreshnessStatus,
    IntakeStatus,
    ResultIdentityV1,
    StructuralIssueV1,
    StructuralResultEnvelopeV2,
)
from structural_lib.core.version import get_runtime_version
from structural_lib.services.canonical_family import _input_hash, require_request_type
from structural_lib.services.contracts.common import (
    model_validate_or_error,
    parse_json_or_error,
)
from structural_lib.services.contracts.ductile_frame import DuctileFrameRequestV1
from structural_lib.services.ductile_joint import check_joint, load_joint

_WORKFLOW = "PROJECT03_DUCTILE_FRAME_CUT"
_PENDING = "REQUIRES_CONSTRUCTION_SEQUENCE_EVIDENCE"
_LIMITATIONS = (
    "Regular open frame cut with J1 and J2, one shared beam and four short column legs.",
    "The five boundary beams contribute signed forces and couples. Their own strength and BBS lie outside the admitted project cut.",
    "The report, drawing and schedule cover design review. Site insertion, temporary supports and boundary anchorage require separate construction evidence.",
)
_ISSUES = {
    "applicability_missing": (
        "applicability_reference",
        "Declare the basis for this regular frame cut.",
    ),
    "stale_frame_revision": (
        "action_revision",
        "The project, source rows and both cages must use one current action revision.",
    ),
    "incomplete_signed_inventory": (
        "required_combinations",
        "Supply the complete distinct factored rows for X+, X−, Y+ and Y−.",
    ),
    "missing_member_or_boundary_action": (
        "actions",
        "Supply every beam interval and column leg for each declared combination.",
    ),
    "frame_source_equilibrium": (
        "actions",
        "A signed member witness or its force and moment balance disagrees with the declared frame cut.",
    ),
    "shared_cage_continuity": (
        "joint_geometry",
        "The two joint views disagree on the shared beam or its link and bar layout.",
    ),
    "joint_acceptance": (
        "joint_geometry",
        "Both local joint checks must pass on the current source rows.",
    ),
    "shared_beam_strength": (
        "shared_beam.strength",
        "The common beam fails a flexure, shear or end-region check.",
    ),
    "shared_beam_constructible_geometry": (
        "shared_beam.links",
        "The common cage fails link fit, stock development or compaction.",
    ),
    "admitted_column_legs": (
        "column_legs",
        "An admitted column leg fails its concurrent member check.",
    ),
    "cut_mark_and_leg_placement_reconciliation": (
        "artifact_reconciliation",
        "The column transitions or resolved schedule marks cannot be reconciled.",
    ),
    "member_mechanics_outside_profile": (
        "actions",
        "Member strength could not be resolved in the admitted profile.",
    ),
}


@dataclass(frozen=True)
class DuctileFrameResultV1:
    """Frame calculation and checked-artifact identity for one action revision."""

    _request: DuctileFrameRequestV1
    _calculation_json: str
    envelope: StructuralResultEnvelopeV2
    input_hash: str

    @property
    def request(self) -> DuctileFrameRequestV1:
        return self._request.model_copy(deep=True)

    @property
    def calculation(self) -> dict[str, Any]:
        payload: dict[str, Any] = json.loads(self._calculation_json)
        return payload

    @property
    def status(self) -> str:
        return self.envelope.engineering_status.value

    @property
    def issues(self) -> tuple[StructuralIssueV1, ...]:
        return self.envelope.issues

    def artifacts_match(self, current: DuctileFrameRequestV1 | None) -> bool:
        """Require an explicit current request with the same checked identity."""
        return (
            self.status == "PASS"
            and isinstance(current, DuctileFrameRequestV1)
            and _input_hash(current) == self.input_hash
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the request and calculation used by every checked output."""
        return {
            "schema_version": "ductile-frame-cut-result/v1",
            "workflow_id": _WORKFLOW,
            "request": self._request.model_dump(mode="json"),
            "envelope": self.envelope.to_dict(),
            "calculation": self.calculation,
            "limitations": list(_LIMITATIONS),
            "provenance": [
                "IS 13920:2016 with Amendments 1 and 2, §§6.2–6.3, 7.1–7.2, 7.4–7.6 and 9.1–9.2",
                "IS 456:2000 §§25, 26, 38, 39 and 40, Tables 19–20",
            ],
        }


def load_frame(
    value: DuctileFrameRequestV1 | Mapping[str, object] | str | bytes,
) -> DuctileFrameRequestV1:
    """Load and validate the regular two-joint frame cut.

    Parameters
    ----------
    value : mapping, JSON or DuctileFrameRequestV1
        Explicit signed member wrenches and the two connected local cages.
    Returns
    -------
    DuctileFrameRequestV1
        Detached, structurally valid request.
    Raises
    ------
    InputContractError
        Malformed or out-of-schema input.
    Examples
    --------
    See Python/examples/ductile_frame_cut.py.
    Limitations
    -----------
    Requires the declared regular two-joint topology and global units.
    Provenance
    ----------
    PROJECT03 supplied-action frame cut v1.
    """
    if isinstance(value, DuctileFrameRequestV1):
        value = value.model_dump(mode="json")
    if isinstance(value, (str, bytes)):
        value = parse_json_or_error(value)
    return model_validate_or_error(DuctileFrameRequestV1, value)


def _result(
    request: DuctileFrameRequestV1,
    status: EngineeringStatus,
    data: dict[str, Any],
    reasons: tuple[str, ...] = (),
) -> DuctileFrameResultV1:
    held = status is EngineeringStatus.HOLD
    digest = _input_hash(request)
    evidence: dict[str, Any] = {"status": status.value, **data}
    if held:
        evidence.update(reason=reasons[0])
    else:
        evidence.update(failed_checks=list(reasons))
    envelope = StructuralResultEnvelopeV2(
        intake_status=IntakeStatus.PARTIAL if held else IntakeStatus.VALID,
        calculation_status=(
            CalculationStatus.NOT_EVALUATED if held else CalculationStatus.COMPLETED
        ),
        engineering_status=status,
        issues=tuple(
            StructuralIssueV1(f"FRAME.{reason.upper()}", *_ISSUES[reason])
            for reason in reasons
        ),
        freshness_status=(
            FreshnessStatus.STALE
            if "stale_frame_revision" in reasons
            else FreshnessStatus.CURRENT
        ),
        result_identity=ResultIdentityV1(
            contract_version=request.schema_version,
            library_version=get_runtime_version(),
            input_hash=digest,
            calculation_identity=_WORKFLOW,
        ),
    )
    return DuctileFrameResultV1(
        request, json.dumps(evidence, allow_nan=False), envelope, digest
    )


def _shared_geometry(
    left: Mapping[str, Any], right: Mapping[str, Any], detail: Mapping[str, Any]
) -> bool:
    paired = (
        (left["beam_axis_across_column_mm"], right["beam_axes_mm"]["X"]),
        (left["beam_row_depth_from_top_mm"]["X"], right["beam_top_z_mm"]["X"]),
        (
            left["beam_clear_spans_mm"]["X"]["plus"],
            right["beam_clear_spans_mm"]["X"]["minus"],
        ),
        (
            left["beam_dead_plus_live_kn_m"]["X"]["plus"],
            right["beam_dead_plus_live_kn_m"]["X"]["minus"],
        ),
        (left["beam_width_mm"], right["beam_width_mm"]["X"]),
        (left["beam_bar_mm"], right["beam_bar_mm"]["X"]),
        (left["beam_link_centre_radius_mm"], right["beam_link_centre_radius_mm"]["X"]),
        (left["beam_link_seat_inset_mm"], right["beam_link_seat_inset_mm"]["X"]),
        (
            left["beam_link_depth_seat_inset_mm"] or left["beam_link_seat_inset_mm"],
            right["beam_link_depth_seat_inset_mm"].get(
                "X", right["beam_link_seat_inset_mm"]["X"]
            ),
        ),
        (left["beam_clear_spans_mm"]["X"]["minus"], detail["west_clear_span_mm"]),
        (right["beam_link_hook_tail_mm"], detail["beam_link_hook_tail_mm"]),
        *(
            (left[key], right[key])
            for key in (
                "column_width_mm",
                "joint_depth_mm",
                "beam_link_mm",
                "beam_first_link_mm",
                "beam_inner_link_offset_mm",
                "beam_pitch_mm",
                "axis_tolerance_mm",
                "tie_station_tolerance_mm",
                "diameter_overage_mm",
            )
        ),
    )
    return all(a == b for a, b in paired) and left["column_hook_offset_radiused"]


def check_frame(request: DuctileFrameRequestV1) -> DuctileFrameResultV1:
    """Check one common action revision, its local joints and the shared members.

    Parameters
    ----------
    request : DuctileFrameRequestV1
        Joint geometry, current revision and all concurrent end actions.
    Returns
    -------
    DuctileFrameResultV1
        Source equilibrium, member and joint checks and reconciled design marks.
    Raises
    ------
    InputContractError
        The submitted object violates the bounded input contract.
    Examples
    --------
    See Python/examples/ductile_frame_cut.py.
    Limitations
    -----------
    Checks the described frame cut and its nominal final reinforcement fit.
    Provenance
    ----------
    PROJECT03, using the positioned DUCT01 and DUCT02 checks.
    """
    require_request_type(request, DuctileFrameRequestV1)
    request = load_frame(request)
    raw = request.model_dump(mode="json")
    held = (
        "applicability_missing"
        if request.applicability_reference is None
        else frame_hold_reason(raw)
    )
    if held is not None:
        return _result(request, EngineeringStatus.HOLD, {}, (held,))
    if any(item["directions"] for item in raw["joint_geometry"].values()):
        # A second local action inventory could silently disagree with the common source.
        return _result(
            request, EngineeringStatus.HOLD, {}, ("incomplete_signed_inventory",)
        )

    detail = raw["detailing"]
    left, right = (raw["joint_geometry"][name] for name in ("J1", "J2"))
    if (
        left["joint_id"] != "J1"
        or right["joint_id"] != "J2"
        or not _shared_geometry(left, right, detail)
    ):
        return _result(request, EngineeringStatus.FAIL, {}, ("shared_cage_continuity",))

    balances, mapped = resolve_frame_actions(raw)
    data: dict[str, Any] = {"source_balances": balances}
    if not all(row["pass"] for row in balances.values()):
        return _result(
            request, EngineeringStatus.FAIL, data, ("frame_source_equilibrium",)
        )

    inputs, joints, joint_hashes = {}, {}, {}
    for key, geometry in raw["joint_geometry"].items():
        local_request = load_joint(
            {
                **geometry,
                "applicability_reference": request.applicability_reference,
                "directions": mapped[key],
            }
        )
        result = check_joint(local_request)
        inputs[key] = local_request.model_dump(mode="json")
        joints[key] = result.calculation
        joint_hashes[key] = result.input_hash
    data.update(
        joint_action_requests=inputs, joints=joints, joint_input_hashes=joint_hashes
    )
    failed = [name for name, joint in joints.items() if joint["status"] != "PASS"]
    if failed:
        data["failed_joints"] = failed
        data["joint_checks"] = {
            name: [
                key
                for key, passed in joints[name].get("checks", {}).items()
                if not passed
            ]
            for name in failed
        }
        status = (
            EngineeringStatus.FAIL
            if any(joints[name]["status"] == "FAIL" for name in failed)
            else EngineeringStatus.HOLD
        )
        return _result(request, status, data, ("joint_acceptance",))

    try:
        shared = resolve_shared_beam(inputs, joints, detail)
    except FrameCageDomainError as exc:
        data["cage_diagnostic"] = str(exc)
        return _result(
            request,
            EngineeringStatus.FAIL,
            data,
            ("shared_beam_constructible_geometry",),
        )
    data["shared_beam"] = shared
    if not shared["links"]["pass"] or not shared["longitudinal"]["pass"]:
        return _result(
            request,
            EngineeringStatus.FAIL,
            data,
            ("shared_beam_constructible_geometry",),
        )
    try:
        member_result = check_project_members(
            raw["actions"], joints, inputs, shared["links"]["adverse_family_pitch_mm"]
        )
    except JointStrengthDomainError as exc:
        return _result(
            request,
            EngineeringStatus.HOLD,
            data | {"strength_diagnostic": str(exc)},
            ("member_mechanics_outside_profile",),
        )
    shared["strength"] = member_result["beam_strength"]
    columns = member_result["column_legs"]
    data["column_legs"] = columns
    try:
        fabrication = reconcile_frame_marks(joints, columns, shared, inputs=inputs)
    except FrameCageDomainError as exc:
        data["cage_diagnostic"] = str(exc)
        return _result(
            request,
            EngineeringStatus.FAIL,
            data,
            ("cut_mark_and_leg_placement_reconciliation",),
        )
    checks = {
        "frame_source_equilibrium": True,
        "shared_cage_continuity": True,
        "joint_acceptance": True,
        "shared_beam_strength": shared["strength"]["pass"],
        "shared_beam_constructible_geometry": True,
        "admitted_column_legs": all(member["pass"] for member in columns.values()),
        "cut_mark_and_leg_placement_reconciliation": fabrication["pass"],
    }
    reasons = tuple(name for name, passed in checks.items() if not passed)
    return _result(
        request,
        EngineeringStatus.FAIL if reasons else EngineeringStatus.PASS,
        data
        | {
            "checks": checks,
            "artifact_reconciliation": fabrication,
            "excluded_boundary_beams": [
                {
                    "member_id": name,
                    "actions_included": True,
                    "member_design_and_bbs": "OUTSIDE_FRAME_CUT_ACCEPTANCE",
                }
                for name in BEAM_CONNECTIONS
                if name != "BX12"
            ],
            "site_insertion_status": _PENDING,
        },
        reasons,
    )
