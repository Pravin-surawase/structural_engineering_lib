"""Canonical service owner for the IS 456 rectangular-beam journey."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from structural_lib.codes.is456.beam.detailing import BeamDetailingResult
from structural_lib.core.data_types import ComplianceCaseResult
from structural_lib.core.errors import (
    CalculationError,
    InputContractError,
    InputIssueV1,
)
from structural_lib.core.result_contract import (
    CalculationStatus,
    EngineeringStatus,
    IntakeStatus,
    ResultIdentityV1,
    ReviewStatus,
    StructuralIssueV1,
    StructuralResultEnvelopeV2,
)
from structural_lib.core.version import get_runtime_version
from structural_lib.services import bbs as bbs_service
from structural_lib.services.contracts.beam import (
    BEAM_DESIGN_SCHEMA_VERSION,
    BeamDesignInputV1,
    DetailingStandard,
    MemberIdentityV1,
)
from structural_lib.services.project_beam import resolve_effective_depth_v1

if TYPE_CHECKING:
    from structural_lib.services.beam_api import DesignAndDetailResult

__all__ = [
    "BEAM_BBS_RESULT_SCHEMA_VERSION",
    "BEAM_DESIGN_RESULT_SCHEMA_VERSION",
    "BeamBBSResultV1",
    "BeamDesignAndDetailResultV1",
    "BeamDesignResultV1",
    "BeamDetailingResultV1",
    "CanonicalBeamResult",
    "check",
    "design",
    "design_compatibility",
    "design_and_detail",
    "design_and_detail_compatibility",
    "detail",
    "generate_bbs",
]


BEAM_DESIGN_RESULT_SCHEMA_VERSION = "beam-design-result/v1"
BEAM_DETAILING_RESULT_SCHEMA_VERSION = "beam-detailing-result/v1"
BEAM_COMBINED_RESULT_SCHEMA_VERSION = "beam-design-and-detail-result/v1"
BEAM_BBS_RESULT_SCHEMA_VERSION = "beam-bbs-result/v1"


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise CalculationError(
                "Canonical result contains a non-finite numeric value.",
                details={"value": str(value)},
            )
        return value
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "model_dump"):
        return _jsonable(value.model_dump(mode="python"))
    if is_dataclass(value) and not isinstance(value, type):
        return _jsonable(asdict(value))
    if hasattr(value, "to_dict"):
        return _jsonable(value.to_dict())
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    raise CalculationError(
        "Canonical result contains an unsupported serialization value.",
        details={"type": type(value).__name__},
    )


def _jsonable_dict(value: Any) -> dict[str, Any]:
    result = _jsonable(value)
    if not isinstance(result, dict):
        raise CalculationError(
            "Canonical result serialization must produce an object.",
            details={"type": type(result).__name__},
        )
    return result


def _input_hash(request: BeamDesignInputV1) -> str:
    payload = json.dumps(
        request.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _envelope(
    request: BeamDesignInputV1,
    *,
    is_ok: bool,
    failed_checks: list[str] | None = None,
) -> StructuralResultEnvelopeV2:
    issues = tuple(
        StructuralIssueV1(
            code="BEAM_ENGINEERING_CHECK_FAILED",
            path="calculation.failed_checks",
            message=str(check),
        )
        for check in (failed_checks or [])
    )
    return StructuralResultEnvelopeV2(
        intake_status=IntakeStatus.VALID,
        calculation_status=CalculationStatus.COMPLETED,
        engineering_status=(
            EngineeringStatus.PASS if is_ok else EngineeringStatus.FAIL
        ),
        review_status=ReviewStatus.QUALIFIED_REVIEW_REQUIRED,
        issues=issues,
        result_identity=ResultIdentityV1(
            contract_version=BEAM_DESIGN_SCHEMA_VERSION,
            library_version=get_runtime_version(),
            input_hash=_input_hash(request),
            calculation_identity="is456-rectangular-beam-strength/v1",
        ),
    )


@runtime_checkable
class CanonicalBeamResult(Protocol):
    """Small maintained protocol shared by canonical beam result types."""

    schema_version: str
    request: BeamDesignInputV1
    envelope: StructuralResultEnvelopeV2

    def to_dict(self) -> dict[str, Any]: ...


@dataclass(frozen=True)
class BeamDesignResultV1:
    """Typed canonical strength-design result."""

    request: BeamDesignInputV1
    calculation: ComplianceCaseResult
    envelope: StructuralResultEnvelopeV2
    limitations: tuple[str, ...]
    assumptions: tuple[str, ...]
    provenance: tuple[str, ...]
    schema_version: str = BEAM_DESIGN_RESULT_SCHEMA_VERSION

    @property
    def identity(self) -> MemberIdentityV1:
        return self.request.identity

    @property
    def intake_status(self) -> IntakeStatus:
        return self.envelope.intake_status

    @property
    def calculation_status(self) -> CalculationStatus:
        return self.envelope.calculation_status

    @property
    def engineering_status(self) -> EngineeringStatus:
        return self.envelope.engineering_status

    @property
    def qualified_review_required(self) -> bool:
        return self.envelope.review_status is ReviewStatus.QUALIFIED_REVIEW_REQUIRED

    @property
    def issues(self) -> tuple[StructuralIssueV1, ...]:
        return self.envelope.issues

    @property
    def is_ok(self) -> bool:
        return self.calculation.is_ok

    def to_dict(self) -> dict[str, Any]:
        return _jsonable_dict(
            {
                "schema_version": self.schema_version,
                "identity": self.request.identity,
                "request": self.request,
                "envelope": self.envelope.to_dict(),
                "calculation": self.calculation,
                "limitations": self.limitations,
                "assumptions": self.assumptions,
                "provenance": self.provenance,
            }
        )


@dataclass(frozen=True)
class BeamDetailingResultV1:
    """Typed canonical detailing result with the same request identity."""

    request: BeamDesignInputV1
    detailing: BeamDetailingResult
    envelope: StructuralResultEnvelopeV2
    schema_version: str = BEAM_DETAILING_RESULT_SCHEMA_VERSION

    @property
    def identity(self) -> MemberIdentityV1:
        return self.request.identity

    @property
    def intake_status(self) -> IntakeStatus:
        return self.envelope.intake_status

    @property
    def calculation_status(self) -> CalculationStatus:
        return self.envelope.calculation_status

    @property
    def engineering_status(self) -> EngineeringStatus:
        return self.envelope.engineering_status

    @property
    def qualified_review_required(self) -> bool:
        return self.envelope.review_status is ReviewStatus.QUALIFIED_REVIEW_REQUIRED

    @property
    def issues(self) -> tuple[StructuralIssueV1, ...]:
        return self.envelope.issues

    @property
    def is_ok(self) -> bool:
        return self.envelope.engineering_status is EngineeringStatus.PASS

    def to_dict(self) -> dict[str, Any]:
        return _jsonable_dict(
            {
                "schema_version": self.schema_version,
                "identity": self.request.identity,
                "envelope": self.envelope.to_dict(),
                "detailing": self.detailing,
            }
        )


@dataclass(frozen=True)
class BeamDesignAndDetailResultV1:
    """Canonical composed result accepted directly by BBS/report/export."""

    request: BeamDesignInputV1
    design: BeamDesignResultV1
    detailing: BeamDetailingResultV1
    envelope: StructuralResultEnvelopeV2
    schema_version: str = BEAM_COMBINED_RESULT_SCHEMA_VERSION

    @property
    def identity(self) -> MemberIdentityV1:
        return self.request.identity

    @property
    def intake_status(self) -> IntakeStatus:
        return self.envelope.intake_status

    @property
    def calculation_status(self) -> CalculationStatus:
        return self.envelope.calculation_status

    @property
    def engineering_status(self) -> EngineeringStatus:
        return self.envelope.engineering_status

    @property
    def qualified_review_required(self) -> bool:
        return self.envelope.review_status is ReviewStatus.QUALIFIED_REVIEW_REQUIRED

    @property
    def issues(self) -> tuple[StructuralIssueV1, ...]:
        return self.envelope.issues

    @property
    def is_ok(self) -> bool:
        return self.design.is_ok and self.detailing.is_ok

    def to_dict(self) -> dict[str, Any]:
        return _jsonable_dict(
            {
                "schema_version": self.schema_version,
                "identity": self.request.identity,
                "envelope": self.envelope.to_dict(),
                "design": self.design.to_dict(),
                "detailing": self.detailing.to_dict(),
            }
        )


@dataclass(frozen=True)
class BeamBBSResultV1:
    """Canonical BBS content generated only from accepted detailing results."""

    member_ids: tuple[str, ...]
    items: tuple[bbs_service.BBSLineItem, ...]
    summary: bbs_service.BBSummary
    source_result_schema_versions: tuple[str, ...]
    schema_version: str = BEAM_BBS_RESULT_SCHEMA_VERSION

    @property
    def total_weight_kg(self) -> float:
        return self.summary.total_weight_kg

    def to_dict(self) -> dict[str, Any]:
        return _jsonable_dict(
            {
                "schema_version": self.schema_version,
                "member_ids": self.member_ids,
                "items": self.items,
                "summary": self.summary,
                "source_result_schema_versions": self.source_result_schema_versions,
            }
        )


def _resolved_depth(request: BeamDesignInputV1) -> float:
    basis = request.section.effective_depth_basis
    return resolve_effective_depth_v1(
        D_mm=request.section.D_mm,
        d_mm=request.section.d_mm,
        effective_depth_basis=basis.to_service() if basis is not None else None,
    ).d_mm


def design(request: BeamDesignInputV1) -> BeamDesignResultV1:
    """Run the canonical strength journey from an already strict request."""

    if not isinstance(request, BeamDesignInputV1):
        raise InputContractError(
            (
                InputIssueV1(
                    code="INPUT_TYPE_INVALID",
                    path="request",
                    message="request must be BeamDesignInputV1",
                    received=f"<{type(request).__name__}>",
                ),
            )
        )
    from structural_lib.services.beam_api import _design_beam_is456_calculation

    detailing = request.detailing
    calculation = _design_beam_is456_calculation(
        units="IS456",
        case_id=request.identity.case_id,
        mu_knm=request.actions.mu_knm,
        vu_kn=request.actions.vu_kn,
        b_mm=request.section.b_mm,
        D_mm=request.section.D_mm,
        d_mm=request.section.d_mm,
        effective_depth_basis=(
            request.section.effective_depth_basis.to_service()
            if request.section.effective_depth_basis is not None
            else None
        ),
        fck_nmm2=request.materials.fck_nmm2,
        fy_nmm2=request.materials.fy_nmm2,
        d_dash_mm=request.calculation_basis.d_dash_mm,
        asv_mm2=request.calculation_basis.asv_mm2,
        pt_percent=request.calculation_basis.pt_percent,
        ast_mm2_for_shear=request.calculation_basis.ast_mm2_for_shear,
        deflection_params=None,
        crack_width_params=None,
        tu_knm=request.actions.tu_knm,
        cover_mm=detailing.clear_cover_mm if detailing is not None else None,
        stirrup_dia_mm=(
            detailing.stirrup_diameter_mm if detailing is not None else 8.0
        ),
    )
    return BeamDesignResultV1(
        request=request,
        calculation=calculation,
        envelope=_envelope(
            request,
            is_ok=calculation.is_ok,
            failed_checks=calculation.failed_checks,
        ),
        limitations=(
            "Rectangular IS 456 beam strength route only.",
            "Factored actions are supplied by the caller; load generation is excluded.",
        ),
        assumptions=("Actions use the documented non-negative magnitude convention.",),
        provenance=("IS 456 maintained calculation owners",),
    )


def check(request: BeamDesignInputV1) -> BeamDesignResultV1:
    """Evaluate the canonical request; engineering inadequacy remains a result."""

    return design(request)


def design_compatibility(**arguments: Any) -> ComplianceCaseResult:
    """Execute the retained signature through the shared calculation owner.

    The compatibility signature lacks canonical member/story/span identity, so
    it cannot truthfully fabricate a ``BeamDesignInputV1``. It still delegates
    through this service owner and shares the exact calculation function used by
    the canonical request path.
    """

    from structural_lib.services.beam_api import _design_beam_is456_calculation

    return _design_beam_is456_calculation(**arguments)


def design_and_detail_compatibility(**arguments: Any) -> DesignAndDetailResult:
    """Execute the retained combined signature through this service owner."""

    from structural_lib.services.beam_api import (
        _design_and_detail_beam_is456_calculation,
    )

    return _design_and_detail_beam_is456_calculation(**arguments)


def detail(
    design_result: BeamDesignResultV1,
    *,
    detailing_standard: DetailingStandard,
) -> BeamDetailingResultV1:
    """Create explicit detailing from a completed canonical design result."""

    if not isinstance(design_result, BeamDesignResultV1):
        raise InputContractError(
            (
                InputIssueV1(
                    code="CONSUMER_TYPE_INVALID",
                    path="design_result",
                    message="design_result must be BeamDesignResultV1",
                    received=f"<{type(design_result).__name__}>",
                ),
            )
        )
    request = design_result.request
    options = request.detailing
    if options is None:
        raise InputContractError(
            (
                InputIssueV1(
                    code="DOWNSTREAM_INPUT_MISSING",
                    path="request.detailing",
                    message="explicit detailing options are required",
                    suggestion="Build BeamDetailingOptionsV1 and include it in the request.",
                ),
            )
        )
    if options.standard is not detailing_standard:
        raise InputContractError(
            (
                InputIssueV1(
                    code="DETAILING_STANDARD_CONFLICT",
                    path="detailing_standard",
                    message="argument must match request.detailing.standard",
                    received=detailing_standard.value,
                    allowed_values=(options.standard.value,),
                ),
            )
        )
    span_mm = request.section.span_mm
    assert span_mm is not None
    from structural_lib.services.beam_api import detail_beam_is456

    calculation = design_result.calculation
    detailing = detail_beam_is456(
        units="IS456",
        beam_id=request.identity.member_id,
        story=request.identity.story,
        b_mm=request.section.b_mm,
        D_mm=request.section.D_mm,
        span_mm=span_mm,
        cover_mm=options.clear_cover_mm,
        fck_nmm2=request.materials.fck_nmm2,
        fy_nmm2=request.materials.fy_nmm2,
        ast_start_mm2=calculation.flexure.Ast_required,
        ast_mid_mm2=calculation.flexure.Ast_required,
        ast_end_mm2=calculation.flexure.Ast_required,
        asc_start_mm2=calculation.flexure.Asc_required,
        asc_mid_mm2=calculation.flexure.Asc_required,
        asc_end_mm2=calculation.flexure.Asc_required,
        stirrup_dia_mm=options.stirrup_diameter_mm,
        stirrup_spacing_start_mm=options.stirrup_spacing_support_mm,
        stirrup_spacing_mid_mm=options.stirrup_spacing_mid_mm,
        stirrup_spacing_end_mm=options.stirrup_spacing_support_mm,
        is_seismic=detailing_standard is DetailingStandard.IS13920,
        preferred_tension_bar_dia_mm=options.tension_bar_diameter_mm,
        preferred_compression_bar_dia_mm=options.compression_bar_diameter_mm,
        nominal_top_steel_ratio=options.nominal_top_steel_ratio,
        stirrup_legs=options.stirrup_legs,
    )
    return BeamDetailingResultV1(
        request=request,
        detailing=detailing,
        envelope=_envelope(
            request,
            is_ok=design_result.is_ok and detailing.is_valid,
            failed_checks=design_result.calculation.failed_checks,
        ),
    )


def design_and_detail(
    request: BeamDesignInputV1,
    *,
    detailing_standard: DetailingStandard,
) -> BeamDesignAndDetailResultV1:
    """Compose canonical strength and detailing without hidden choices."""

    design_result = design(request)
    detailing_result = detail(design_result, detailing_standard=detailing_standard)
    return BeamDesignAndDetailResultV1(
        request=request,
        design=design_result,
        detailing=detailing_result,
        envelope=_envelope(
            request,
            is_ok=design_result.is_ok and detailing_result.is_ok,
            failed_checks=design_result.calculation.failed_checks,
        ),
    )


def _accepted_detailing(value: object) -> tuple[BeamDetailingResult, str]:
    if isinstance(value, BeamDesignAndDetailResultV1):
        if not value.is_ok:
            raise InputContractError(
                (
                    InputIssueV1(
                        code="CONSUMER_RESULT_NOT_ACCEPTED",
                        path="result.engineering_status",
                        message="BBS requires a valid completed detailing result",
                        received=value.engineering_status.value,
                    ),
                )
            )
        return value.detailing.detailing, value.schema_version
    if isinstance(value, BeamDetailingResultV1):
        if not value.is_ok:
            raise InputContractError(
                (
                    InputIssueV1(
                        code="CONSUMER_RESULT_NOT_ACCEPTED",
                        path="result.engineering_status",
                        message="BBS requires valid detailing",
                        received=value.engineering_status.value,
                    ),
                )
            )
        return value.detailing, value.schema_version
    raise InputContractError(
        (
            InputIssueV1(
                code="CONSUMER_TYPE_INVALID",
                path="result",
                message=(
                    "BBS accepts BeamDesignAndDetailResultV1, "
                    "BeamDetailingResultV1, or a sequence of detailing results"
                ),
                received=f"<{type(value).__name__}>",
            ),
        )
    )


def generate_bbs(
    result: (
        BeamDesignAndDetailResultV1
        | BeamDetailingResultV1
        | list[BeamDetailingResultV1]
    ),
) -> BeamBBSResultV1:
    """Generate all-or-nothing BBS content from named canonical result types."""

    if isinstance(result, list):
        values: list[object] = list(result)
    else:
        values = [result]
    if not values:
        raise InputContractError(
            (
                InputIssueV1(
                    code="COLLECTION_EMPTY",
                    path="result",
                    message="at least one canonical detailing result is required",
                ),
            )
        )
    accepted = [_accepted_detailing(value) for value in values]
    details = [item[0] for item in accepted]
    items: list[bbs_service.BBSLineItem] = []
    for detailing in details:
        items.extend(bbs_service.generate_bbs_from_detailing(detailing))
    summary = bbs_service.calculate_bbs_summary(
        items, details[0].beam_id if len(details) == 1 else "PROJECT"
    )
    return BeamBBSResultV1(
        member_ids=tuple(detailing.beam_id for detailing in details),
        items=tuple(items),
        summary=summary,
        source_result_schema_versions=tuple(item[1] for item in accepted),
    )
