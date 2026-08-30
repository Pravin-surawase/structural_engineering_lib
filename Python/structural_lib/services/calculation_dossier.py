"""W3J immutable dossier assembly and evidence checks; no I/O or signing.

Provider-reported signature/credential evidence is never promoted to trusted
verification. This provider-neutral packet always retains that distinct hold.
"""

from __future__ import annotations

import hashlib
import json
from typing import Literal, TypeVar

from pydantic import BaseModel, ValidationError

from structural_lib.core.analysis_contracts import EvidenceStateV1, EvidenceValueV1
from structural_lib.core.calculation_dossier import (
    AttestedCalculationDossierV1,
    CalculationDossierBuildRequestV1,
    CalculationDossierBuildResultV1,
    CalculationDossierV1,
    DigitalSignatureEvidenceV1,
    DossierIssueV1,
    DossierVerificationResultV1,
    ReviewAttestationV1,
    SignedCalculationDossierV1,
    _utc,
)

__all__ = [
    "build_calculation_dossier_v1",
    "record_review_attestation_v1",
    "attach_digital_signature_evidence_v1",
    "verify_signed_calculation_dossier_v1",
]

_ModelT = TypeVar("_ModelT", bound=BaseModel)
_KINDS = {
    "MODEL": "model_file_sha256",
    "CATALOGUE": "catalogue_sha256",
    "DEMAND": "demand_sha256",
    "CALCULATION": "calculation_sha256",
    "REPORT": "report_sha256",
    "WORKBOOK": "workbook_sha256",
    "SURROGATE": "surrogate_sha256",
    "CALIBRATION": "calibration_sha256",
    "OPTIMIZATION": "optimization_sha256",
    "GOVERNING_CANDIDATE": "governing_candidate_sha256",
}


def _revalidate(value: _ModelT) -> _ModelT:
    # Revalidate nested values, including objects assembled with model_copy/update.
    return type(value).model_validate(value.model_dump(mode="python"))


def _json(value: object) -> str:
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json")
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _hash(value: object) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _issue(code: str, message: str) -> DossierIssueV1:
    return DossierIssueV1(code=code, message=message)


def _request_issues(
    request: CalculationDossierBuildRequestV1,
) -> tuple[DossierIssueV1, ...]:
    issues: list[DossierIssueV1] = []
    identity, scope = request.identity, request.scope
    if scope.project_id != identity.project_id:
        issues.append(_issue("PROJECT_MISMATCH", "Scope and source project differ."))
    expected: dict[str, str] = {}
    for kind, field in _KINDS.items():
        value = getattr(identity, field)
        if isinstance(value, EvidenceValueV1):
            if value.state is EvidenceStateV1.BLOCKED:
                issues.append(
                    _issue("BLOCKED_IDENTITY", f"{kind} identity is blocked.")
                )
            if value.state is EvidenceStateV1.PRESENT:
                digest = value.value
                assert isinstance(digest, str)
                expected[kind] = digest
        else:
            expected[kind] = value
    observed = {artifact.kind: artifact.sha256 for artifact in request.artifacts}
    if len(observed) != len(request.artifacts) or observed != expected:
        issues.append(
            _issue(
                "ARTIFACT_IDENTITY_MISMATCH",
                "Artifacts must match every declared identity exactly once.",
            )
        )
    all_hashes = set(expected.values())
    if (
        not set(scope.reviewed_input_hashes) <= all_hashes
        or not set(scope.reviewed_result_hashes) <= all_hashes
        or not {
            identity.model_file_sha256,
            identity.catalogue_sha256,
            identity.demand_sha256,
        }
        <= set(scope.reviewed_input_hashes)
        or not {identity.calculation_sha256, identity.report_sha256}
        <= set(scope.reviewed_result_hashes)
    ):
        issues.append(
            _issue(
                "REVIEW_ARTIFACT_SCOPE_MISMATCH",
                "Review input/result scope must bind the complete required artifacts.",
            )
        )
    previous = request.supersedes_dossier_sha256
    if previous.state is EvidenceStateV1.PRESENT:
        digest = previous.value
        if (
            digest is None
            or len(digest) != 64
            or any(c not in "0123456789abcdef" for c in digest)
        ):
            issues.append(
                _issue(
                    "SUPERSEDES_IDENTITY_INVALID",
                    "Superseded dossier requires a SHA-256.",
                )
            )
    elif previous.state is EvidenceStateV1.BLOCKED:
        issues.append(
            _issue("BLOCKED_REVISION", "Dossier revision history is blocked.")
        )
    if request.revision > 1 and previous.state is not EvidenceStateV1.PRESENT:
        issues.append(
            _issue(
                "REVISION_HISTORY_MISSING",
                "A successor revision must identify the superseded dossier.",
            )
        )
    if request.revision == 1 and previous.state is not EvidenceStateV1.NOT_APPLICABLE:
        issues.append(
            _issue(
                "REVISION_HISTORY_INVALID",
                "An initial revision must explicitly declare no predecessor.",
            )
        )
    for artifact in request.artifacts:
        payload = artifact.canonical_json
        if payload.state is EvidenceStateV1.BLOCKED:
            issues.append(
                _issue("BLOCKED_ARTIFACT", f"{artifact.kind} artifact is blocked.")
            )
        if payload.state is not EvidenceStateV1.PRESENT:
            continue
        text = payload.value
        assert text is not None
        try:
            if len(text.encode("utf-8")) > 25_000_000:
                raise ValueError("canonical artifact exceeds byte limit")
            parsed = json.loads(text)
            if (
                _json(parsed) != text
                or hashlib.sha256(text.encode("utf-8")).hexdigest() != artifact.sha256
            ):
                raise ValueError("canonical JSON or artifact digest differs")
        except (ValueError, TypeError) as error:
            issues.append(
                _issue("CANONICAL_ARTIFACT_INVALID", f"{artifact.kind}: {error}")
            )
    return tuple(issues)


def build_calculation_dossier_v1(
    request: CalculationDossierBuildRequestV1, /
) -> CalculationDossierBuildResultV1:
    """Build a hash-bound review dossier; no external file or professional check."""
    request = _revalidate(request)
    issues = _request_issues(request)
    if issues:
        return CalculationDossierBuildResultV1(
            status="BLOCKED", dossier=None, issues=issues
        )
    dossier = CalculationDossierV1(
        request=request,
        dossier_sha256=_hash(request),
        scope_sha256=_hash(request.scope),
        attestations=(),
        state="REVIEW_READY",
    )
    return CalculationDossierBuildResultV1(
        status="ACCEPTED", dossier=dossier, issues=()
    )


def _active_attestations(
    attestations: tuple[ReviewAttestationV1, ...],
) -> tuple[ReviewAttestationV1, ...]:
    superseded = {
        item.supersedes.value
        for item in attestations
        if item.supersedes.state is EvidenceStateV1.PRESENT
    }
    return tuple(item for item in attestations if item.attestation_id not in superseded)


def _review_state(dossier: CalculationDossierV1) -> str:
    active = _active_attestations(dossier.attestations)
    if any(item.decision == "REJECTED" for item in active):
        return "REVIEWED_REJECTED"
    approvers = {
        item.identity.identity_id for item in active if item.role == "APPROVED"
    }
    checkers = {item.identity.identity_id for item in active if item.role == "CHECKED"}
    preparers = {
        item.identity.identity_id for item in active if item.role == "PREPARED"
    }
    if approvers and (
        not dossier.request.scope.independent_check_required
        or (preparers and checkers - preparers)
    ):
        return "REVIEWED_ACCEPTED"
    return "REVIEW_READY"


def _validate_attestations(dossier: CalculationDossierV1) -> None:
    seen: dict[str, ReviewAttestationV1] = {}
    superseded: set[str] = set()
    for item in dossier.attestations:
        if (
            item.dossier_sha256 != dossier.dossier_sha256
            or item.scope_sha256 != dossier.scope_sha256
        ):
            raise ValueError("attestation dossier or review scope mismatch")
        if item.attestation_id in seen or _utc(item.attested_at_utc) < _utc(
            dossier.request.created_at_utc
        ):
            raise ValueError("duplicate attestation or attestation predates dossier")
        if item.supersedes.state is EvidenceStateV1.PRESENT:
            old = seen.get(item.supersedes.value or "")
            if old is None or old.attestation_id in superseded:
                raise ValueError(
                    "superseded attestation is missing or already superseded"
                )
            if (
                item.identity.identity_id != old.identity.identity_id
                or item.role != old.role
                or item.revision != old.revision + 1
                or _utc(item.attested_at_utc) < _utc(old.attested_at_utc)
            ):
                raise ValueError(
                    "attestation successor identity, revision or time differs"
                )
            superseded.add(old.attestation_id)
        elif (
            item.revision != 1
            or item.supersedes.state is not EvidenceStateV1.NOT_APPLICABLE
        ):
            raise ValueError("attestation revision history is incomplete")
        seen[item.attestation_id] = item


def _base(dossier: CalculationDossierV1) -> CalculationDossierV1:
    return CalculationDossierV1.model_validate(
        {name: getattr(dossier, name) for name in CalculationDossierV1.model_fields}
    )


def _validate_dossier(dossier: CalculationDossierV1) -> CalculationDossierV1:
    dossier = _revalidate(dossier)
    if _request_issues(dossier.request):
        raise ValueError("dossier request no longer validates")
    if dossier.dossier_sha256 != _hash(
        dossier.request
    ) or dossier.scope_sha256 != _hash(dossier.request.scope):
        raise ValueError("dossier or scope hash mismatch")
    _validate_attestations(dossier)
    if dossier.state != _review_state(dossier):
        raise ValueError("review state contradicts active attestations")
    if isinstance(
        dossier, AttestedCalculationDossierV1
    ) and dossier.attested_sha256 != _hash(_base(dossier)):
        raise ValueError("attested artifact hash mismatch")
    return dossier


def record_review_attestation_v1(
    dossier: CalculationDossierV1,
    attestation: ReviewAttestationV1,
    /,
) -> AttestedCalculationDossierV1:
    """Append one immutable claimed decision; never infer professional eligibility."""
    dossier = _validate_dossier(dossier)
    attestation = _revalidate(attestation)
    updated = _base(dossier).model_copy(
        update={"attestations": (*dossier.attestations, attestation)}
    )
    _validate_attestations(updated)
    updated = updated.model_copy(update={"state": _review_state(updated)})
    updated = _revalidate(updated)
    return AttestedCalculationDossierV1(
        **updated.model_dump(mode="python"), attested_sha256=_hash(updated)
    )


def attach_digital_signature_evidence_v1(
    dossier: AttestedCalculationDossierV1,
    evidence: DigitalSignatureEvidenceV1,
    /,
) -> SignedCalculationDossierV1:
    """Bind provider-reported evidence to the exact attested artifact, not a name."""
    _validate_dossier(dossier)
    evidence = _revalidate(evidence)
    if evidence.signed_artifact_sha256 != dossier.attested_sha256:
        raise ValueError("signed artifact hash mismatch")
    signers = [
        item
        for item in _active_attestations(dossier.attestations)
        if item.identity.identity_id == evidence.signer_identity_id
    ]
    if not signers or any(
        _utc(item.attested_at_utc) > _utc(evidence.signed_at_utc)
        for item in dossier.attestations
    ):
        raise ValueError(
            "signature signer is not active or signature predates attestation"
        )
    basis = {
        "dossier": dossier.model_dump(mode="json"),
        "signature": evidence.model_dump(mode="json"),
    }
    return SignedCalculationDossierV1(
        dossier=dossier, signature=evidence, signed_dossier_sha256=_hash(basis)
    )


def verify_signed_calculation_dossier_v1(
    dossier: SignedCalculationDossierV1,
    *,
    verification_time_utc: str,
) -> DossierVerificationResultV1:
    """Recompute local bindings; report external evidence without trusting it.

    A separately accepted provider adapter is required for SIGNED_VERIFIED.
    No network, private key, signature algorithm or credential authority is used.
    """
    checked = _utc(verification_time_utc)
    signature = dossier.signature
    issues: list[DossierIssueV1] = []
    artifact_ok = True
    scope_ok = (
        dossier.dossier.scope_sha256 == _hash(dossier.dossier.request.scope)
        and dossier.dossier.request.scope.project_id
        == dossier.dossier.request.identity.project_id
        and all(
            item.scope_sha256 == dossier.dossier.scope_sha256
            for item in dossier.dossier.attestations
        )
    )
    try:
        _revalidate(dossier)
        _validate_dossier(dossier.dossier)
        expected = attach_digital_signature_evidence_v1(dossier.dossier, signature)
        if expected.signed_dossier_sha256 != dossier.signed_dossier_sha256:
            raise ValueError("signed dossier hash mismatch")
    except (ValueError, ValidationError) as error:
        artifact_ok = False
        issues.append(_issue("ARTIFACT_OR_SCOPE_INVALID", str(error)[:2000]))
    stale = (
        not _utc(signature.verified_at_utc)
        <= checked
        <= _utc(signature.evidence_valid_until_utc)
    )
    if stale:
        issues.append(
            _issue(
                "SIGNATURE_EVIDENCE_STALE",
                "Verification time is outside the provider observation validity interval.",
            )
        )
    for name in (
        "signature_valid",
        "certificate_chain_valid",
        "certificate_not_revoked",
        "credential_eligible",
    ):
        item = getattr(signature, name)
        if item.state is EvidenceStateV1.PRESENT and item.value is False:
            issues.append(
                _issue("PROVIDER_REPORTED_FAILURE", f"Provider reports {name}=false.")
            )
        elif item.state is not EvidenceStateV1.PRESENT:
            issues.append(
                _issue("PROVIDER_EVIDENCE_HELD", f"{name} remains {item.state.value}.")
            )
    for item in _active_attestations(dossier.dossier.attestations):
        start, end = (
            item.identity.valid_from_utc.value,
            item.identity.valid_until_utc.value,
        )
        attested = _utc(item.attested_at_utc)
        if (start is not None and attested < _utc(start)) or (
            end is not None and attested > _utc(end)
        ):
            issues.append(
                _issue(
                    "CREDENTIAL_INTERVAL_INVALID",
                    "Claimed credential interval excludes the attestation time.",
                )
            )
    trust = EvidenceValueV1[bool](
        state=EvidenceStateV1.UNAVAILABLE,
        reason_code="PROVIDER_TRUST_NOT_ESTABLISHED",
        message="Provider-neutral evidence intake does not authenticate a verifier or establish legal eligibility.",
        source_references=(signature.verification_report_reference,),
    )
    issues.append(
        _issue(
            "PROVIDER_TRUST_NOT_ESTABLISHED",
            trust.message or "Provider trust unavailable.",
        )
    )
    invalid = any(
        item.code
        in {
            "ARTIFACT_OR_SCOPE_INVALID",
            "PROVIDER_REPORTED_FAILURE",
            "CREDENTIAL_INTERVAL_INVALID",
        }
        for item in issues
    )
    status: Literal["SIGNATURE_INVALID", "STALE_SUPERSEDED", "SIGNATURE_PENDING"] = (
        "SIGNATURE_INVALID"
        if invalid
        else "STALE_SUPERSEDED" if stale else "SIGNATURE_PENDING"
    )
    return DossierVerificationResultV1(
        status=status,
        checked_at_utc=verification_time_utc,
        artifact_hash_valid=artifact_ok,
        review_scope_valid=scope_ok,
        provider_signature=signature.signature_valid,
        certificate_chain=signature.certificate_chain_valid,
        certificate_revocation=signature.certificate_not_revoked,
        credential_eligibility=signature.credential_eligible,
        provider_trust=trust,
        issues=tuple(issues),
        software_status=dossier.dossier.request.software_status,
        limitations=(
            "Local hashes verify supplied content/claims, not external model or workbook bytes.",
            "Provider evidence is reported, not independently cryptographically verified or trusted.",
            "Credential and jurisdiction eligibility, engineering acceptance and professional approval remain external.",
        ),
    )
