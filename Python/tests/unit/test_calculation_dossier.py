"""Independent W3J identity/claim tests; fictional data, no signing or I/O."""

from __future__ import annotations

import hashlib
import inspect
import json

import pytest
from pydantic import ValidationError

import structural_lib as lib
from structural_lib.core.calculation_dossier import (
    CalculationDossierBuildRequestV1,
    DigitalSignatureEvidenceV1,
    DossierArtifactV1,
    DossierIdentityV1,
    ProfessionalIdentityV1,
    ReviewAttestationV1,
    ReviewScopeV1,
)


def ev(value=None, state="PRESENT"):
    if state == "PRESENT":
        return lib.EvidenceValueV1(
            state=state, value=value, source_references=("fictional-test",)
        )
    return lib.EvidenceValueV1(
        state=state,
        value=None,
        reason_code="TEST_STATE",
        message="Explicit fictional test state.",
        source_references=("fictional-test",),
    )


def sha(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


@pytest.fixture
def dossier_request():
    artifacts = tuple(
        DossierArtifactV1(
            kind=kind,
            sha256=sha({"kind": kind}),
            source_reference="fictional:" + kind,
            canonical_json=ev(
                json.dumps({"kind": kind}, sort_keys=True, separators=(",", ":"))
            ),
        )
        for kind in ("MODEL", "CATALOGUE", "DEMAND", "CALCULATION", "REPORT")
    )
    hashes = {a.kind: a.sha256 for a in artifacts}
    identity = DossierIdentityV1(
        project_id="software-only",
        git_commit="1" * 40,
        git_tree="2" * 40,
        library_version="0.24.0",
        library_content_sha256="3" * 64,
        etabs_version="fictional-23.3.1",
        model_file_sha256=hashes["MODEL"],
        model_identity_sha256="4" * 64,
        catalogue_sha256=hashes["CATALOGUE"],
        demand_sha256=hashes["DEMAND"],
        calculation_sha256=hashes["CALCULATION"],
        report_sha256=hashes["REPORT"],
        workbook_sha256=ev(state="NOT_REQUESTED"),
        surrogate_sha256=ev(state="UNAVAILABLE"),
        calibration_sha256=ev(state="UNAVAILABLE"),
        optimization_sha256=ev(state="NOT_REQUESTED"),
        governing_candidate_sha256=ev(state="NOT_APPLICABLE"),
    )
    scope = ReviewScopeV1(
        project_id="software-only",
        member_ids=("B1",),
        scenario_ids=("ULS",),
        code_editions=("IS456:2000; software fixture only",),
        reviewed_input_hashes=tuple(
            hashes[k] for k in ("MODEL", "CATALOGUE", "DEMAND")
        ),
        reviewed_result_hashes=tuple(hashes[k] for k in ("CALCULATION", "REPORT")),
        assumptions=("Fictional contract test, not an engineering basis.",),
        exclusions=(
            "No actual model, calculations, signature or professional approval.",
        ),
        held_checks=("SERVICEABILITY",),
        independent_check_required=True,
    )
    return CalculationDossierBuildRequestV1(
        dossier_id="D1",
        revision=1,
        created_at_utc="2026-08-31T00:00:00Z",
        identity=identity,
        scope=scope,
        software_status="HOLD",
        artifacts=artifacts,
        supersedes_dossier_sha256=ev(state="NOT_APPLICABLE"),
    )


def identity(name="fixture-reviewer"):
    return ProfessionalIdentityV1(
        identity_id=name,
        person_name=name,
        organization="FICTIONAL",
        role="Reviewer",
        jurisdiction="NOT_A_REAL_JURISDICTION",
        credential_type="TEST",
        credential_identifier="NOT_A_CREDENTIAL",
        issuing_authority="FICTIONAL",
        valid_from_utc=ev("2026-01-01T00:00:00Z"),
        valid_until_utc=ev("2027-01-01T00:00:00Z"),
        credential_evidence=ev(state="UNAVAILABLE"),
    )


def attest(
    dossier, *, role="PREPARED", name="fixture-reviewer", decision="ACCEPTED", **changes
):
    data = {
        "attestation_id": name + "-" + role,
        "revision": 1,
        "dossier_sha256": dossier.dossier_sha256,
        "scope_sha256": dossier.scope_sha256,
        "identity": identity(name),
        "role": role,
        "decision": decision,
        "comments": ("Fictional test decision",),
        "attested_at_utc": "2026-08-31T00:01:00Z",
        "supersedes": ev(state="NOT_APPLICABLE"),
    }
    data.update(changes)
    return ReviewAttestationV1(**data)


def sign(dossier, **changes):
    data = {
        "provider": "FICTIONAL UNTRUSTED PROVIDER",
        "mechanism": "detached-test-evidence",
        "signed_artifact_sha256": dossier.attested_sha256,
        "signature_reference": "external:fictional",
        "signer_identity_id": dossier.attestations[-1].identity.identity_id,
        "certificate_subject": "FICTIONAL",
        "certificate_issuer": "FICTIONAL",
        "certificate_serial": "TEST",
        "certificate_thumbprint_sha256": "a" * 64,
        "algorithm": "EXTERNAL_TEST_ONLY",
        "signed_at_utc": "2026-08-31T00:02:00Z",
        "verified_at_utc": "2026-08-31T00:03:00Z",
        "evidence_valid_until_utc": "2026-08-31T01:00:00Z",
        "signature_valid": ev(True),
        "certificate_chain_valid": ev(True),
        "certificate_not_revoked": ev(True),
        "credential_eligible": ev(True),
        "verification_report_sha256": "b" * 64,
        "verification_report_reference": "external:unverified-test-report",
    }
    data.update(changes)
    return lib.attach_digital_signature_evidence_v1(
        dossier, DigitalSignatureEvidenceV1(**data)
    )


@pytest.fixture
def built(dossier_request):
    result = lib.build_calculation_dossier_v1(dossier_request)
    assert result.status == "ACCEPTED"
    return result.dossier


@pytest.fixture
def attested(built):
    return lib.record_review_attestation_v1(built, attest(built))


def test_exact_planned_signatures():
    names = (
        "build_calculation_dossier_v1",
        "record_review_attestation_v1",
        "attach_digital_signature_evidence_v1",
        "verify_signed_calculation_dossier_v1",
    )
    for name in names:
        assert name in lib.__all__
        params = list(inspect.signature(getattr(lib, name)).parameters.values())
        expected = (
            inspect.Parameter.POSITIONAL_OR_KEYWORD
            if name == "verify_signed_calculation_dossier_v1"
            else inspect.Parameter.POSITIONAL_ONLY
        )
        assert params[0].kind is expected
        assert all(p.default is inspect.Parameter.empty for p in params)
    assert (
        list(
            inspect.signature(
                lib.verify_signed_calculation_dossier_v1
            ).parameters.values()
        )[1].kind
        is inspect.Parameter.KEYWORD_ONLY
    )


def test_deterministic_complete_hashes(dossier_request, built):
    request = dossier_request
    assert built.dossier_sha256 == sha(request.model_dump(mode="json"))
    assert built.scope_sha256 == sha(request.scope.model_dump(mode="json"))
    assert built == lib.build_calculation_dossier_v1(request).dossier
    assert built.state == "REVIEW_READY" and built.attestations == ()
    with pytest.raises(ValidationError):
        built.state = "REVIEWED_ACCEPTED"
    restored = CalculationDossierBuildRequestV1.model_validate_json(
        request.model_dump_json()
    )
    assert restored == request


@pytest.mark.parametrize(
    "change",
    [
        "project",
        "artifact_hash",
        "duplicate",
        "missing_scope",
        "canonical",
        "revision",
        "blocked_optional",
    ],
)
def test_blocked_build_returns_no_partial(dossier_request, change):
    request = dossier_request
    if change == "project":
        request = request.model_copy(
            update={"scope": request.scope.model_copy(update={"project_id": "wrong"})}
        )
    elif change == "artifact_hash":
        request = request.model_copy(
            update={
                "artifacts": (
                    request.artifacts[0].model_copy(update={"sha256": "a" * 64}),
                    *request.artifacts[1:],
                )
            }
        )
    elif change == "duplicate":
        request = request.model_copy(
            update={"artifacts": (*request.artifacts, request.artifacts[0])}
        )
    elif change == "missing_scope":
        request = request.model_copy(
            update={
                "scope": request.scope.model_copy(
                    update={
                        "reviewed_input_hashes": (request.identity.model_file_sha256,)
                    }
                )
            }
        )
    elif change == "canonical":
        request = request.model_copy(
            update={
                "artifacts": (
                    request.artifacts[0].model_copy(
                        update={"canonical_json": ev('{ "kind": "MODEL" }')}
                    ),
                    *request.artifacts[1:],
                )
            }
        )
    elif change == "revision":
        request = request.model_copy(update={"revision": 2})
    else:
        request = request.model_copy(
            update={
                "identity": request.identity.model_copy(
                    update={"calibration_sha256": ev(state="BLOCKED")}
                )
            }
        )
    result = lib.build_calculation_dossier_v1(request)
    assert result.status == "BLOCKED" and result.dossier is None and result.issues


def test_optional_present_artifact_requires_matching_bytes(dossier_request):
    request = dossier_request
    text = '{"workbook":"fictional"}'
    digest = hashlib.sha256(text.encode()).hexdigest()
    request = request.model_copy(
        update={
            "identity": request.identity.model_copy(
                update={"workbook_sha256": ev(digest)}
            ),
            "artifacts": (
                *request.artifacts,
                DossierArtifactV1(
                    kind="WORKBOOK",
                    sha256=digest,
                    source_reference="test",
                    canonical_json=ev(text),
                ),
            ),
        }
    )
    assert lib.build_calculation_dossier_v1(request).status == "ACCEPTED"


@pytest.mark.parametrize(
    "field,value",
    [
        ("dossier_sha256", "a" * 64),
        ("scope_sha256", "b" * 64),
        ("attested_at_utc", "2026-08-30T00:00:00Z"),
    ],
)
def test_wrong_attestation_binding_fails(built, field, value):
    with pytest.raises(ValueError):
        lib.record_review_attestation_v1(built, attest(built, **{field: value}))


def test_independent_review_and_rejection_are_separate_from_software(built):
    prepared = lib.record_review_attestation_v1(built, attest(built))
    self_approved = lib.record_review_attestation_v1(
        prepared, attest(built, role="APPROVED")
    )
    assert self_approved.state == "REVIEW_READY"
    checked = lib.record_review_attestation_v1(
        self_approved, attest(built, role="CHECKED", name="other")
    )
    assert checked.state == "REVIEWED_ACCEPTED"
    rejected = lib.record_review_attestation_v1(
        checked, attest(built, role="CHECKED", name="third", decision="REJECTED")
    )
    assert rejected.state == "REVIEWED_REJECTED"
    assert rejected.request.software_status == "HOLD"
    assert built.attestations == ()


def test_append_history_supersedes_only_exact_prior_role(attested):
    old = attested.attestations[0]
    successor = attest(
        attested,
        attestation_id="revision-2",
        revision=2,
        supersedes=ev(old.attestation_id),
        decision="REJECTED",
    )
    result = lib.record_review_attestation_v1(attested, successor)
    assert len(result.attestations) == 2 and result.state == "REVIEWED_REJECTED"
    assert result.attested_sha256 == sha(
        {
            k: v
            for k, v in result.model_dump(mode="json").items()
            if k != "attested_sha256"
        }
    )
    with pytest.raises(ValueError):
        lib.record_review_attestation_v1(result, successor)
    with pytest.raises(ValueError):
        lib.record_review_attestation_v1(
            result, successor.model_copy(update={"attestation_id": "another"})
        )
    with pytest.raises(ValueError):
        lib.record_review_attestation_v1(
            attested, successor.model_copy(update={"role": "APPROVED"})
        )


def test_checker_may_also_approve_but_cannot_be_the_preparer(built):
    prepared = lib.record_review_attestation_v1(built, attest(built))
    checked = lib.record_review_attestation_v1(
        prepared, attest(built, role="CHECKED", name="other")
    )
    approved = lib.record_review_attestation_v1(
        checked, attest(built, role="APPROVED", name="other")
    )
    assert approved.state == "REVIEWED_ACCEPTED"


@pytest.mark.parametrize(
    "changes",
    [
        {"signed_artifact_sha256": "a" * 64},
        {"signer_identity_id": "not-an-attestor"},
        {"signed_at_utc": "2026-08-31T00:00:30Z"},
    ],
)
def test_wrong_signature_binding_fails(attested, changes):
    with pytest.raises(ValueError):
        sign(attested, **changes)


def test_all_positive_untrusted_provider_never_creates_approval(attested):
    signed = sign(attested)
    result = lib.verify_signed_calculation_dossier_v1(
        signed, verification_time_utc="2026-08-31T00:04:00Z"
    )
    assert result.status == "SIGNATURE_PENDING"
    assert result.artifact_hash_valid and result.review_scope_valid
    assert result.provider_signature.value is True
    assert result.provider_trust.state is lib.EvidenceStateV1.UNAVAILABLE
    assert result.professional_approval == "NOT_PROVIDED"
    assert result.software_status == "HOLD"


@pytest.mark.parametrize(
    "state", ["UNAVAILABLE", "NOT_REQUESTED", "NOT_APPLICABLE", "BLOCKED"]
)
def test_missing_provider_evidence_preserves_all_states(attested, state):
    signed = sign(attested, certificate_not_revoked=ev(state=state))
    result = lib.verify_signed_calculation_dossier_v1(
        signed, verification_time_utc="2026-08-31T00:04:00Z"
    )
    assert result.certificate_revocation.state.value == state
    assert result.status == "SIGNATURE_PENDING"


@pytest.mark.parametrize(
    "field",
    [
        "signature_valid",
        "certificate_chain_valid",
        "certificate_not_revoked",
        "credential_eligible",
    ],
)
def test_provider_reported_false_is_not_a_pass(attested, field):
    result = lib.verify_signed_calculation_dossier_v1(
        sign(attested, **{field: ev(False)}),
        verification_time_utc="2026-08-31T00:04:00Z",
    )
    assert result.status == "SIGNATURE_INVALID"


@pytest.mark.parametrize("time", ["2026-08-31T00:02:30Z", "2026-08-31T01:00:01Z"])
def test_stale_or_future_evidence(attested, time):
    result = lib.verify_signed_calculation_dossier_v1(
        sign(attested), verification_time_utc=time
    )
    assert result.status == "STALE_SUPERSEDED"


def test_byte_tampering_rejected_without_changing_original(attested):
    signed = sign(attested)
    result = lib.verify_signed_calculation_dossier_v1(
        signed.model_copy(update={"signed_dossier_sha256": "0" * 64}),
        verification_time_utc="2026-08-31T00:04:00Z",
    )
    assert result.status == "SIGNATURE_INVALID" and not result.artifact_hash_valid
    assert result.review_scope_valid
    bad = attested.model_copy(update={"scope_sha256": "0" * 64})
    with pytest.raises(ValueError):
        lib.record_review_attestation_v1(bad, attest(bad))
    assert lib.verify_signed_calculation_dossier_v1(
        signed, verification_time_utc="2026-08-31T00:04:00Z"
    ).artifact_hash_valid


def test_typed_name_and_invalid_credential_interval_are_not_approval(built):
    person = identity().model_copy(
        update={"valid_until_utc": ev("2026-08-30T00:00:00Z")}
    )
    reviewed = lib.record_review_attestation_v1(built, attest(built, identity=person))
    result = lib.verify_signed_calculation_dossier_v1(
        sign(reviewed), verification_time_utc="2026-08-31T00:04:00Z"
    )
    assert result.status == "SIGNATURE_INVALID"
    assert result.professional_approval == "NOT_PROVIDED"


def test_no_hidden_default_or_extra_field(dossier_request):
    request = dossier_request
    with pytest.raises(ValidationError):
        CalculationDossierBuildRequestV1(
            **request.model_dump(mode="python"), approved=True
        )
    with pytest.raises(ValidationError):
        request.identity.model_copy(
            update={"workbook_sha256": ev("wrong")}
        ).__class__.model_validate(
            request.identity.model_copy(
                update={"workbook_sha256": ev("wrong")}
            ).model_dump(mode="python")
        )
