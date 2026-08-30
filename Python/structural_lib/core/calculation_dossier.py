"""W3J provider-neutral evidence contracts, not professional authorization."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .analysis_contracts import EvidenceStateV1, EvidenceValueV1

_Id = Annotated[str, Field(min_length=1, max_length=160)]
_Text = Annotated[str, Field(min_length=1, max_length=2000)]
_Sha = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
_Git = Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
_Utc = Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}T.*Z$")]


def _utc(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if not value.endswith("Z") or result.utcoffset() is None:
        raise ValueError("an explicit UTC timestamp ending in Z is required")
    return result


class _DossierModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        allow_inf_nan=False,
        validate_default=True,
    )


class DossierIdentityV1(_DossierModel):
    project_id: _Id
    git_commit: _Git
    git_tree: _Git
    library_version: _Id
    library_content_sha256: _Sha
    etabs_version: _Id
    model_file_sha256: _Sha
    model_identity_sha256: _Sha
    catalogue_sha256: _Sha
    demand_sha256: _Sha
    calculation_sha256: _Sha
    report_sha256: _Sha
    workbook_sha256: EvidenceValueV1[str]
    surrogate_sha256: EvidenceValueV1[str]
    calibration_sha256: EvidenceValueV1[str]
    optimization_sha256: EvidenceValueV1[str]
    governing_candidate_sha256: EvidenceValueV1[str]

    @model_validator(mode="after")
    def _optional_hashes(self) -> Self:
        for name in (
            "workbook",
            "surrogate",
            "calibration",
            "optimization",
            "governing_candidate",
        ):
            value = getattr(self, name + "_sha256")
            if value.state is EvidenceStateV1.PRESENT:
                digest = value.value
                if len(digest) != 64 or any(
                    c not in "0123456789abcdef" for c in digest
                ):
                    raise ValueError(f"{name} requires a lowercase SHA-256")
        return self


class DossierArtifactV1(_DossierModel):
    """Hash and source reference; optional JSON is checked, never executed."""

    kind: Literal[
        "MODEL",
        "CATALOGUE",
        "DEMAND",
        "CALCULATION",
        "REPORT",
        "WORKBOOK",
        "SURROGATE",
        "CALIBRATION",
        "OPTIMIZATION",
        "GOVERNING_CANDIDATE",
    ]
    sha256: _Sha
    source_reference: _Text
    canonical_json: EvidenceValueV1[str]


class ProfessionalIdentityV1(_DossierModel):
    """Claimed identity only; a populated credential does not verify eligibility."""

    identity_id: _Id
    person_name: _Text
    organization: _Text
    role: _Id
    jurisdiction: _Text
    credential_type: _Id
    credential_identifier: _Id
    issuing_authority: _Text
    valid_from_utc: EvidenceValueV1[str]
    valid_until_utc: EvidenceValueV1[str]
    credential_evidence: EvidenceValueV1[str]

    @model_validator(mode="after")
    def _validity(self) -> Self:
        start, end = self.valid_from_utc.value, self.valid_until_utc.value
        if start is not None:
            _utc(start)
        if end is not None:
            _utc(end)
        if start is not None and end is not None and _utc(end) < _utc(start):
            raise ValueError("credential validity interval is reversed")
        return self


class ReviewScopeV1(_DossierModel):
    project_id: _Id
    member_ids: tuple[_Id, ...] = Field(min_length=1, max_length=10000)
    scenario_ids: tuple[_Id, ...] = Field(min_length=1, max_length=1000)
    code_editions: tuple[_Text, ...] = Field(min_length=1, max_length=32)
    reviewed_input_hashes: tuple[_Sha, ...] = Field(min_length=1, max_length=64)
    reviewed_result_hashes: tuple[_Sha, ...] = Field(min_length=1, max_length=64)
    assumptions: tuple[_Text, ...] = Field(max_length=1000)
    exclusions: tuple[_Text, ...] = Field(max_length=1000)
    held_checks: tuple[_Text, ...] = Field(max_length=1000)
    independent_check_required: bool

    @model_validator(mode="after")
    def _unique_domains(self) -> Self:
        for field in (
            "member_ids",
            "scenario_ids",
            "code_editions",
            "reviewed_input_hashes",
            "reviewed_result_hashes",
        ):
            values = getattr(self, field)
            if len(set(values)) != len(values):
                raise ValueError(f"{field} contains duplicates")
        return self


class ReviewAttestationV1(_DossierModel):
    attestation_id: _Id
    revision: int = Field(ge=1)
    dossier_sha256: _Sha
    scope_sha256: _Sha
    identity: ProfessionalIdentityV1
    role: Literal["PREPARED", "CHECKED", "APPROVED"]
    decision: Literal["ACCEPTED", "REJECTED", "ACCEPTED_WITH_HOLDS"]
    comments: tuple[_Text, ...] = Field(max_length=1000)
    attested_at_utc: _Utc
    supersedes: EvidenceValueV1[str]

    @model_validator(mode="after")
    def _time(self) -> Self:
        _utc(self.attested_at_utc)
        return self


class CalculationDossierBuildRequestV1(_DossierModel):
    dossier_id: _Id
    revision: int = Field(ge=1)
    created_at_utc: _Utc
    identity: DossierIdentityV1
    scope: ReviewScopeV1
    software_status: Literal["PASS", "FAIL", "HOLD"]
    artifacts: tuple[DossierArtifactV1, ...] = Field(min_length=5, max_length=10)
    supersedes_dossier_sha256: EvidenceValueV1[str]

    @model_validator(mode="after")
    def _time(self) -> Self:
        _utc(self.created_at_utc)
        return self


class CalculationDossierV1(_DossierModel):
    schema_version: Literal["calculation-dossier/v1"] = "calculation-dossier/v1"
    request: CalculationDossierBuildRequestV1
    dossier_sha256: _Sha
    scope_sha256: _Sha
    attestations: tuple[ReviewAttestationV1, ...] = Field(max_length=64)
    state: Literal["REVIEW_READY", "REVIEWED_ACCEPTED", "REVIEWED_REJECTED"]


class DossierIssueV1(_DossierModel):
    code: _Id
    message: _Text


class CalculationDossierBuildResultV1(_DossierModel):
    status: Literal["ACCEPTED", "BLOCKED"]
    dossier: CalculationDossierV1 | None
    issues: tuple[DossierIssueV1, ...]

    @model_validator(mode="after")
    def _complete(self) -> Self:
        if (self.status == "ACCEPTED") != (
            self.dossier is not None and not self.issues
        ):
            raise ValueError(
                "accepted dossier requires one complete value and no issues"
            )
        if self.status == "BLOCKED" and (self.dossier is not None or not self.issues):
            raise ValueError("blocked dossier requires issues and no partial value")
        return self


class AttestedCalculationDossierV1(CalculationDossierV1):
    attestations: tuple[ReviewAttestationV1, ...] = Field(min_length=1, max_length=64)
    attested_sha256: _Sha


class DigitalSignatureEvidenceV1(_DossierModel):
    """Provider-reported evidence, not a library-performed cryptographic check."""

    provider: _Text
    mechanism: _Text
    signed_artifact_sha256: _Sha
    signature_reference: _Text
    signer_identity_id: _Id
    certificate_subject: _Text
    certificate_issuer: _Text
    certificate_serial: _Id
    certificate_thumbprint_sha256: _Sha
    algorithm: _Id
    signed_at_utc: _Utc
    verified_at_utc: _Utc
    evidence_valid_until_utc: _Utc
    signature_valid: EvidenceValueV1[bool]
    certificate_chain_valid: EvidenceValueV1[bool]
    certificate_not_revoked: EvidenceValueV1[bool]
    credential_eligible: EvidenceValueV1[bool]
    verification_report_sha256: _Sha
    verification_report_reference: _Text

    @model_validator(mode="after")
    def _chronology(self) -> Self:
        signed = _utc(self.signed_at_utc)
        verified = _utc(self.verified_at_utc)
        expiry = _utc(self.evidence_valid_until_utc)
        if not signed <= verified <= expiry:
            raise ValueError("signature evidence chronology is inconsistent")
        return self


class SignedCalculationDossierV1(_DossierModel):
    schema_version: Literal["signed-calculation-dossier/v1"] = (
        "signed-calculation-dossier/v1"
    )
    dossier: AttestedCalculationDossierV1
    signature: DigitalSignatureEvidenceV1
    signed_dossier_sha256: _Sha
    state: Literal["SIGNATURE_PENDING"] = "SIGNATURE_PENDING"


class DossierVerificationResultV1(_DossierModel):
    # SIGNED_VERIFIED is reserved for a separately accepted external-trust adapter.
    status: Literal[
        "SIGNATURE_PENDING", "SIGNATURE_INVALID", "STALE_SUPERSEDED", "SIGNED_VERIFIED"
    ]
    checked_at_utc: _Utc
    artifact_hash_valid: bool
    review_scope_valid: bool
    provider_signature: EvidenceValueV1[bool]
    certificate_chain: EvidenceValueV1[bool]
    certificate_revocation: EvidenceValueV1[bool]
    credential_eligibility: EvidenceValueV1[bool]
    provider_trust: EvidenceValueV1[bool]
    issues: tuple[DossierIssueV1, ...]
    software_status: Literal["PASS", "FAIL", "HOLD"]
    professional_approval: Literal["NOT_PROVIDED"] = "NOT_PROVIDED"
    limitations: tuple[_Text, ...]
