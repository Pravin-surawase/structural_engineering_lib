"""Run a regular ductile joint check and bind its artifacts to the input."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from structural_lib.codes.is456.beam.detailing import (
    calculate_development_length_unrounded,
    get_bond_stress,
)
from structural_lib.codes.is13920.exterior_joint_cage import exterior_joint_placement
from structural_lib.codes.is13920.exterior_joint_detail import (
    exterior_anchorage,
    exterior_beam_link_sections,
    exterior_confinement,
)
from structural_lib.codes.is13920.joint_cage import check_joint_cage
from structural_lib.codes.is13920.joint_strength import (
    JointStrengthDomainError,
    check_regular_joint_strength,
)
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
from structural_lib.services.contracts.ductile_joint import (
    JOINT_DIRECTIONS,
    DuctileExteriorJointRequestV1,
    DuctileJointRequestV1,
)

__all__ = [
    "DuctileExteriorJointRequestV1",
    "DuctileJointRequestV1",
    "DuctileJointResultV1",
    "load_joint",
    "check_joint",
]

JointRequest = DuctileJointRequestV1 | DuctileExteriorJointRequestV1

_WORKFLOW = "DUCT01_INTERIOR_JOINT"
_EXTERIOR_WORKFLOW = "DUCT02_EXTERIOR_JOINT"
_EXTERIOR_SCHEMA = "ductile-exterior-joint/v1"
_PROVENANCE = (
    "IS 13920:2016 with Amendment 1 (2017) and Amendment 2 (2020)",
    "IS 13920 §§6.2–6.3, 7.1–7.2, 7.4–7.6 and 9.1–9.2",
    "IS 456:2000 §§26.2, 26.3, 26.5.3, 38, 40 and Tables 19–20",
)
_LIMITATIONS = (
    "Regular, centred four-beam interior joint with equal-depth rectangular beams, "
    "symmetric bars and no participating slab steel.",
    "The complete factored action inventory and compatible column inflection "
    "positions come from the caller.",
    "The BBS covers the joint hoop and cross-ties. The drawing shows local through-bar "
    "continuations and adjacent cages. Frame fabrication and global seismic acceptance require separate evidence.",
)
_EXTERIOR_LIMITATIONS = (
    "Regular exterior joint with one terminating X-minus beam and two Y through beams. "
    "The equal-depth rectangular beams contain symmetric bar rows and no participating slab steel.",
    "The action inventory, inflection offsets, fabrication tolerances and compaction "
    "basis come from the caller.",
    "The local BBS schedules the joint links. It lists the in-core X termination "
    "geometry separately from the cut list. Whole-member fabrication, installation "
    "sequencing and temporary support require project evidence.",
)
_CHECK_ISSUES = {
    "anchorage": (
        "anchorage",
        "A terminating bar, through-joint width or adjacent straight development is inadequate.",
    ),
    "column_axial_stress": (
        "directions",
        "A concurrent factored column compression exceeds 0.40 fck.",
    ),
    "construction_fit": (
        "placement",
        "The supplied cage fails a physical fit or restraint check.",
    ),
    "confinement": (
        "placement.confinement",
        "The provided joint or adjoining confinement layout is inadequate.",
    ),
    "continuous_bar_anchorage": (
        "anchorage",
        "Through-joint width or adjacent straight development is inadequate.",
    ),
    "beam_flexural_prerequisite": (
        "beam_section_by_plane",
        "The beam geometry or ductile longitudinal layout is inadequate.",
    ),
    "scwb": (
        "governing.scwb",
        "Column moment capacity is below the strong-column weak-beam requirement.",
    ),
    "joint_shear": (
        "governing.joint_shear",
        "Joint shear exceeds the concrete joint shear limit.",
    ),
    "axial_stress": (
        "directions",
        "A concurrent factored column compression exceeds 0.40 fck.",
    ),
    "beam_capacity_shear": (
        "governing.beam_capacity_shear",
        "Beam capacity shear or end link spacing is inadequate.",
    ),
    "column_capacity_shear": (
        "governing.column_capacity_shear",
        "Column capacity shear exceeds the available resistance.",
    ),
}


@dataclass(frozen=True)
class DuctileJointResultV1:
    """Checked local joint result with detached request and calculation views."""

    _request: JointRequest
    _calculation_json: str
    envelope: StructuralResultEnvelopeV2
    input_hash: str

    @property
    def request(self) -> JointRequest:
        return self._request.model_copy(deep=True)

    @property
    def calculation(self) -> dict[str, Any]:
        value: dict[str, Any] = json.loads(self._calculation_json)
        return value

    @property
    def status(self) -> str:
        return self.envelope.engineering_status.value

    @property
    def issues(self) -> tuple[StructuralIssueV1, ...]:
        return self.envelope.issues

    def artifacts_match(self, current: JointRequest | None) -> bool:
        """Require an explicit current request that matches the checked inputs."""
        return (
            self.envelope.engineering_status is EngineeringStatus.PASS
            and current is not None
            and type(current) is type(self._request)
            and _input_hash(current) == self.input_hash
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the same evidence that is used by all artifact renderers."""
        exterior = isinstance(self._request, DuctileExteriorJointRequestV1)
        return {
            "schema_version": (
                "ductile-exterior-joint-result/v1"
                if exterior
                else "ductile-interior-joint-result/v1"
            ),
            "workflow_id": _EXTERIOR_WORKFLOW if exterior else _WORKFLOW,
            "request": self._request.model_dump(mode="json"),
            "envelope": self.envelope.to_dict(),
            "calculation": self.calculation,
            "provenance": list(_PROVENANCE),
            "limitations": list(_EXTERIOR_LIMITATIONS if exterior else _LIMITATIONS),
        }


def load_joint(
    value: Mapping[str, object] | str | bytes | JointRequest,
) -> JointRequest:
    """Load a regular interior or explicitly versioned exterior joint request.

    Parameters
    ----------
    value : mapping, str, bytes or joint request model
        Interior or exterior JSON data. Exterior data declares the exterior schema version.
    Returns
    -------
    DuctileJointRequestV1 or DuctileExteriorJointRequestV1
        Validated geometry, action rows and supplied evidence.
    Raises
    ------
    InputContractError
        Invalid JSON or inputs outside the request contract.
    Examples
    --------
    See Python/examples/ductile_interior_joint.py.
    Limitations
    -----------
    Admits centred equal-depth rectangular beams and a square column.
    Provenance
    ----------
    DUCT01 interior-joint and DUCT02 exterior-joint requests v1.
    """
    if isinstance(value, (DuctileJointRequestV1, DuctileExteriorJointRequestV1)):
        value = value.model_dump(mode="json")
    if isinstance(value, (str, bytes)):
        value = parse_json_or_error(value)
    if isinstance(value, Mapping) and value.get("schema_version") == _EXTERIOR_SCHEMA:
        return model_validate_or_error(DuctileExteriorJointRequestV1, value)
    return model_validate_or_error(DuctileJointRequestV1, value)


def _result(
    request: JointRequest,
    status: EngineeringStatus,
    calculation: dict[str, Any],
    issues: tuple[StructuralIssueV1, ...] = (),
    *,
    stale: bool = False,
) -> DuctileJointResultV1:
    digest = _input_hash(request)
    held = status is EngineeringStatus.HOLD
    envelope = StructuralResultEnvelopeV2(
        intake_status=IntakeStatus.PARTIAL if held else IntakeStatus.VALID,
        calculation_status=(
            CalculationStatus.NOT_EVALUATED if held else CalculationStatus.COMPLETED
        ),
        engineering_status=status,
        issues=issues,
        freshness_status=FreshnessStatus.STALE if stale else FreshnessStatus.CURRENT,
        result_identity=ResultIdentityV1(
            contract_version=request.schema_version,
            library_version=get_runtime_version(),
            input_hash=digest,
            calculation_identity=(
                _EXTERIOR_WORKFLOW
                if isinstance(request, DuctileExteriorJointRequestV1)
                else _WORKFLOW
            ),
        ),
    )
    return DuctileJointResultV1(
        request, json.dumps(calculation, allow_nan=False), envelope, digest
    )


def _hold(
    request: JointRequest,
    reason: str,
    path: str,
    message: str,
    *,
    stale: bool = False,
) -> DuctileJointResultV1:
    return _result(
        request,
        EngineeringStatus.HOLD,
        {"status": "HOLD", "reason": reason},
        (StructuralIssueV1(f"JOINT.{reason.upper()}", path, message),),
        stale=stale,
    )


def _missing_evidence(request: JointRequest) -> DuctileJointResultV1 | None:
    if request.applicability_reference is None:
        return _hold(
            request,
            "applicability_missing",
            "applicability_reference",
            "Declare IS 13920 applicability and the regular non-roof joint basis.",
        )
    if any(not request.directions.get(direction) for direction in JOINT_DIRECTIONS):
        return _hold(
            request,
            "required_direction_missing",
            "directions",
            "Supply factored action rows for X+, X−, Y+ and Y−.",
        )
    if request.action_revision is None or request.cage_action_revision is None:
        return _hold(
            request,
            "action_revision_missing",
            "action_revision",
            "Identify the current actions and the action revision used by the cage.",
        )
    if request.cage_action_revision != request.action_revision:
        return _hold(
            request,
            "stale_action_revision",
            "cage_action_revision",
            "The cage action revision differs from the current analysis actions.",
            stale=True,
        )
    if isinstance(request, DuctileExteriorJointRequestV1) and (
        request.x_hooks is None or set(request.x_hooks) != {"TOP", "BOTTOM"}
    ):
        return _hold(
            request,
            "terminated_bar_path_missing",
            "x_hooks",
            "Provide the upper and lower terminating bar bends and tails.",
        )
    offsets = request.mechanism_inflection_offsets_mm
    if offsets is None or any(
        value >= request.column_clear_heights_mm[end] for end, value in offsets.items()
    ):
        return _hold(
            request,
            "compatible_capacity_mechanism_missing",
            "mechanism_inflection_offsets_mm",
            "Provide compatible column inflection offsets within both adjoining members.",
        )
    if request.compaction_head_mm is None or request.assembly is None:
        return _hold(
            request,
            "compaction_basis_missing",
            "compaction_head_mm",
            "Provide the compaction head and local assembly procedure.",
        )
    return None


def _straight_anchorage(request: DuctileJointRequestV1) -> dict[str, Any]:
    diameter = request.beam_bar_mm
    required_width = 20 * diameter
    available = request.beam_uninterrupted_development_mm
    required = calculate_development_length_unrounded(
        diameter, request.beam_fck_mpa, request.longitudinal_fy_mpa
    )
    return {
        "through_bar_diameter_mm": diameter,
        "joint_length_in_each_plane_mm": request.column_width_mm,
        "joint_width_required_mm": required_width,
        "bond_stress_mpa_m30_deformed_in_tension": get_bond_stress(
            request.beam_fck_mpa
        ),
        "adjacent_member_development_required_mm": required,
        "adjacent_member_development_provided_mm_each_side": available,
        "pass": request.column_width_mm >= required_width and available >= required,
    }


def _governing_strength(
    directions: dict[str, Any], checks: dict[str, bool]
) -> dict[str, Any]:
    result = {}
    for family in ("beam_capacity_shear", "column_capacity_shear"):
        values = [
            {
                "direction": direction,
                "combination_id": row["combination_id"],
                "side": side,
                **value,
            }
            for direction, item in directions.items()
            for row in item["rows"]
            for side, value in row[family].items()
        ]
        checks[family] = all(item["pass"] for item in values)
        result[family] = max(values, key=lambda item: item["utilization"])
    for family in ("scwb", "joint_shear"):
        direction = max(
            directions, key=lambda label: directions[label][family]["utilization"]
        )
        checks[family] = all(item[family]["pass"] for item in directions.values())
        result[family] = {"direction": direction, **directions[direction][family]}
    return result


def _checked_result(
    request: JointRequest,
    calculation: dict[str, Any],
    checks: dict[str, bool],
) -> DuctileJointResultV1:
    status = EngineeringStatus.PASS if all(checks.values()) else EngineeringStatus.FAIL
    issues = tuple(
        StructuralIssueV1(f"JOINT.{check.upper()}", *_CHECK_ISSUES[check])
        for check, passed in checks.items()
        if not passed
    )
    return _result(
        request,
        status,
        {"status": status.value, "checks": checks, **calculation},
        issues,
    )


def check_joint(request: JointRequest) -> DuctileJointResultV1:
    """Check the supplied joint in X+, X−, Y+ and Y−.

    Parameters
    ----------
    request : DuctileJointRequestV1 or DuctileExteriorJointRequestV1
        Checked input contract with the caller's complete action inventory.
    Returns
    -------
    DuctileJointResultV1
        Directional capacities, cage evidence, issues and request identity.
    Raises
    ------
    InputContractError
        The request has the wrong type or contains invalid nested inputs.
    Examples
    --------
    See Python/examples/ductile_interior_joint.py.
    Limitations
    -----------
    Uses supplied actions and inflection positions for the local joint.
    Provenance
    ----------
    IS 13920:2016 with Amendments 1 and 2 and IS 456:2000.
    """
    if not isinstance(request, DuctileExteriorJointRequestV1):
        require_request_type(request, DuctileJointRequestV1)
    # Snapshot and validate nested data, including Python-side mutable mappings.
    request = load_joint(request)
    held = _missing_evidence(request)
    if held is not None:
        return held
    physical = request.model_dump(mode="json")
    physical["directions"] = {
        direction: physical["directions"][direction] for direction in JOINT_DIRECTIONS
    }
    exterior = isinstance(request, DuctileExteriorJointRequestV1)
    calculation: dict[str, Any]
    if isinstance(request, DuctileExteriorJointRequestV1):
        cage = exterior_joint_placement(physical)
        anchorage = exterior_anchorage(physical)
        confinement = exterior_confinement(physical)
        beam_links = exterior_beam_link_sections(physical)
        calculation = {
            "placement": cage,
            "anchorage": anchorage,
            "confinement": confinement,
            "adjacent_beam_link_sections": beam_links,
        }
        checks = {
            "construction_fit": all(cage["fit_checks"].values())
            and all(section["pass"] for section in beam_links.values()),
            "confinement": confinement["pass"],
            "anchorage": anchorage["pass"],
        }
    else:
        cage = check_joint_cage(physical)
        anchorage = _straight_anchorage(request)
        confinement = cage["confinement"]
        calculation = {"placement": cage, "anchorage": anchorage}
        checks = {
            "construction_fit": all(cage["fit_checks"].values()),
            "confinement": all(cage["confinement_checks"].values()),
            "continuous_bar_anchorage": anchorage["pass"],
        }
    if not confinement:
        return _checked_result(request, calculation, checks)
    try:
        strengths = check_regular_joint_strength(physical, confinement)
    except JointStrengthDomainError as exc:
        if not all(checks.values()):
            calculation["strength_diagnostic"] = str(exc)
            return _checked_result(request, calculation, checks)
        return _hold(request, "strength_basis_outside_profile", "directions", str(exc))
    directions = strengths["directions"]
    checks["beam_flexural_prerequisite"] = strengths.pop("beam_flexure_pass")
    axial_status = "column_axial_stress" if exterior else "axial_stress"
    axial_measure = (
        "maximum_column_axial_stress_mpa" if exterior else "maximum_axial_stress_mpa"
    )
    checks[axial_status] = all(
        row[axial_measure] <= 0.40 * request.column_fck_mpa
        for item in directions.values()
        for row in item["rows"]
    )
    governing = _governing_strength(directions, checks)
    calculation.update(strengths, governing=governing)
    return _checked_result(request, calculation, checks)
