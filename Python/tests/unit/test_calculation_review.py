"""W3J Python-to-JavaScript fixture and read-only exporter contract tests."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from structural_lib.core.calculation_dossier import (
    CalculationDossierBuildRequestV1,
    DossierArtifactV1,
)
from structural_lib.services.calculation_dossier import build_calculation_dossier_v1
from tests.unit.test_beam_audit import _evaluate, _request
from tests.unit.test_calculation_dossier import dossier_request, ev

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "review_export", ROOT / "scripts/export_calculation_review.py"
)
assert SPEC is not None and SPEC.loader is not None
EXPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EXPORT)


def review_fixture():
    base = dossier_request.__wrapped__()
    request = _request()
    values = {
        "MODEL": {"fixture": "fictional-model-no-file"},
        "CATALOGUE": request.demand.catalogue.model_dump(mode="json"),
        "DEMAND": {
            "schema_version": "beam-demand-review/v1",
            "request": request.demand.model_dump(mode="json"),
            "snapshot": request.accepted_snapshot.model_dump(mode="json"),
        },
        "CALCULATION": _evaluate(request).model_dump(mode="json"),
        "REPORT": {
            "title": "=Literal + software-only review — मराठी",
            "approval": "NOT_PROVIDED",
        },
    }
    artifacts = tuple(
        DossierArtifactV1(
            kind=kind,
            sha256=hashlib.sha256(EXPORT.canonical(value).encode()).hexdigest(),
            source_reference="fictional:" + kind,
            canonical_json=ev(EXPORT.canonical(value)),
        )
        for kind, value in values.items()
    )
    hashes = {item.kind: item.sha256 for item in artifacts}
    data = base.model_dump(mode="python")
    data["artifacts"] = artifacts
    data["identity"] = base.identity.model_copy(
        update={
            "model_file_sha256": hashes["MODEL"],
            "model_identity_sha256": request.demand.catalogue.model_identity_sha256,
            "catalogue_sha256": hashes["CATALOGUE"],
            "demand_sha256": hashes["DEMAND"],
            "calculation_sha256": hashes["CALCULATION"],
            "report_sha256": hashes["REPORT"],
        }
    )
    data["scope"] = base.scope.model_copy(
        update={
            "member_ids": ("member:1",),
            "scenario_ids": (request.demand.scenario.scenario_id,),
            "reviewed_input_hashes": tuple(
                hashes[k] for k in ("MODEL", "CATALOGUE", "DEMAND")
            ),
            "reviewed_result_hashes": tuple(
                hashes[k] for k in ("CALCULATION", "REPORT")
            ),
        }
    )
    built = build_calculation_dossier_v1(
        CalculationDossierBuildRequestV1.model_validate(data)
    )
    assert built.dossier is not None, built.issues
    return built.dossier


def test_python_export_replays_all_service_identities_and_exact_frozen_node_fixture():
    dossier = review_fixture()
    transport = EXPORT.export_review(dossier)
    fixture = ROOT / "excel_addin/tests/fixtures/calculation-review-v1.json"
    assert transport == json.loads(fixture.read_text(encoding="utf-8"))
    assert (
        hashlib.sha256(transport["dossier_json"].encode()).hexdigest()
        == transport["dossier_content_sha256"]
    )
    assert len(transport["dossier_json"].encode()) == transport["dossier_utf8_bytes"]
    assert transport["professional_approval"] == "NOT_PROVIDED"
    assert transport["signature_verification"] == "NOT_PROVIDED"


@pytest.mark.parametrize(
    "field,value",
    [
        ("dossier_sha256", "0" * 64),
        ("state", "REVIEWED_ACCEPTED"),
        ("scope_sha256", "0" * 64),
    ],
)
def test_export_rejects_stale_dossier(field, value):
    with pytest.raises(ValueError, match="stale"):
        EXPORT.export_review(review_fixture().model_copy(update={field: value}))


def test_missing_canonical_catalogue_cannot_be_published():
    dossier = review_fixture()
    artifacts = tuple(
        (
            a.model_copy(update={"canonical_json": ev(state="UNAVAILABLE")})
            if a.kind == "CATALOGUE"
            else a
        )
        for a in dossier.request.artifacts
    )
    built = build_calculation_dossier_v1(
        dossier.request.model_copy(update={"artifacts": artifacts})
    )
    assert built.dossier is not None
    with pytest.raises(ValueError, match="complete canonical"):
        EXPORT.export_review(built.dossier)


def test_export_command_never_overwrites(tmp_path, monkeypatch):
    source, target = tmp_path / "dossier.json", tmp_path / "review.json"
    source.write_text(review_fixture().model_dump_json(), encoding="utf-8")
    target.write_text("KEEP", encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv", ["export", "--dossier", str(source), "--output", str(target)]
    )
    with pytest.raises(SystemExit):
        EXPORT.main()
    assert target.read_text(encoding="utf-8") == "KEEP"


def test_export_command_writes_one_verified_new_file_without_source_change(
    tmp_path, monkeypatch
):
    source, target = tmp_path / "dossier.json", tmp_path / "review.json"
    text = review_fixture().model_dump_json()
    source.write_text(text, encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv", ["export", "--dossier", str(source), "--output", str(target)]
    )
    assert EXPORT.main() == 0
    assert json.loads(target.read_text(encoding="utf-8")) == EXPORT.export_review(
        review_fixture()
    )
    assert source.read_text(encoding="utf-8") == text
