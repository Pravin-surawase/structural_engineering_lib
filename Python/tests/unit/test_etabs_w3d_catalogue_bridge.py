"""W3D getter-only live catalogue transport tests."""

# ruff: noqa: N802 - fake methods intentionally mirror ETABS COM names.

from __future__ import annotations

from contextlib import nullcontext

import pytest

from structural_lib.core.analysis_contracts import ResultSelectionKindV1
from structural_lib.services import etabs_catalogue_bridge as bridge
from structural_lib.services.contracts.etabs_w3 import (
    W3BuildIssueV1,
    W3BuildStatusV1,
)
from structural_lib.services.etabs_beam_baseline import ETABSModelFileSnapshotV1
from structural_lib.services.etabs_live_bridge import ETABSDataError
from structural_lib.services.etabs_result_catalogue_adapter import (
    ETABSCatalogueAdapterResultV1,
    ETABSCatalogueSelectionRequestV1,
)


def _snapshot(observed_at_utc: str) -> ETABSModelFileSnapshotV1:
    return ETABSModelFileSnapshotV1(
        model_path=r"C:\Models\W3 Authorized Copy.edb",
        model_name="W3 Authorized Copy.edb",
        sha256="a" * 64,
        byte_count=12_345,
        modified_at_utc="2026-08-30T05:00:00Z",
        observed_at_utc=observed_at_utc,
    )


def _request() -> bridge.ETABSLiveCatalogueRunRequestV1:
    snapshot = _snapshot("2026-08-30T05:01:00Z")
    observation = (
        f"model-file-sha256:{snapshot.sha256};"
        f"bytes:{snapshot.byte_count};mtime:{snapshot.modified_at_utc}"
    )
    return bridge.ETABSLiveCatalogueRunRequestV1(
        authorized_model_file=snapshot,
        expected_etabs_version="ETABS 23.3.1",
        expected_etabs_version_number=23.31,
        expected_present_units_enum=6,
        runtime_identity_sha256="b" * 64,
        getter_matrix_sha256="c" * 64,
        model_observation_before=observation,
        model_observation_after=observation,
        observed_at_utc="2026-08-30T05:01:00Z",
        result_selections=[
            ETABSCatalogueSelectionRequestV1(
                kind=ResultSelectionKindV1.COMBINATION,
                name="ULS-1",
            )
        ],
        approved_copy_confirmed=True,
    )


class _FakeAnalyze:
    def GetCaseStatus(self):
        return (1, ("DEAD",), (4,), 0)


class _FakeLoadCases:
    def GetNameList(self):
        return (1, ("DEAD",), 0)


class _FakeRespCombo:
    def GetNameList(self):
        return (1, ("ULS-1",), 0)


class _FakeSetup:
    def GetCaseSelectedForOutput(self, _name):
        return (False, 0)

    def GetComboSelectedForOutput(self, _name):
        return (True, 0)


class _FakeResults:
    Setup = _FakeSetup()

    def FrameForce(self, *_args):
        raise AssertionError("W3D catalogue transport must not call FrameForce")


class _FakeSapModel:
    Analyze = _FakeAnalyze()
    LoadCases = _FakeLoadCases()
    RespCombo = _FakeRespCombo()
    Results = _FakeResults()

    def __init__(self, *, units_after: int = 6) -> None:
        self.units_after = units_after
        self.unit_reads = 0

    def GetModelFilename(self, include_path):
        assert include_path is True
        return r"C:\Models\W3 Authorized Copy.edb"

    def GetVersion(self):
        return ("ETABS 23.3.1", 23.31, 0)

    def GetModelIsLocked(self):
        return True

    def GetPresentUnits(self):
        self.unit_reads += 1
        return 6 if self.unit_reads == 1 else self.units_after

    def RunAnalysis(self):
        raise AssertionError("W3D catalogue transport must not run analysis")

    def SetPresentUnits(self, *_args):
        raise AssertionError("W3D catalogue transport must not call setters")


class _FakeSession:
    def __init__(self, sap_model: _FakeSapModel) -> None:
        self.sap_model = sap_model

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None


class _Observer:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def __call__(self, model_path: str) -> ETABSModelFileSnapshotV1:
        self.calls.append(model_path)
        return _snapshot(f"2026-08-30T05:0{len(self.calls) + 1}:00Z")


def _blocked_adapter_result() -> ETABSCatalogueAdapterResultV1:
    return ETABSCatalogueAdapterResultV1(
        status=W3BuildStatusV1.BLOCKED,
        issues=(
            W3BuildIssueV1(
                code="CASE_FAMILY_NOT_MODELED",
                path="LoadCases.GetTypeOAPI_1",
                message="The selected case family is not modeled.",
            ),
        ),
        operation_evidence=(),
        normalized_request=None,
        catalogue=None,
    )


def test_w3d_transport_brackets_complete_domain_block_without_mutation(
    monkeypatch,
) -> None:
    sap_model = _FakeSapModel()
    observer = _Observer()
    monkeypatch.setattr(bridge, "etabs_com_operation_v1", nullcontext)
    monkeypatch.setattr(
        bridge,
        "extract_etabs_result_catalogue_v1",
        lambda _sap_model, _request: _blocked_adapter_result(),
    )

    result = bridge.run_etabs_live_catalogue_v1(
        _request(),
        session_factory=lambda: _FakeSession(sap_model),
        observe_model_file=observer,
    )

    assert result.adapter_result.status is W3BuildStatusV1.BLOCKED
    assert result.adapter_result.catalogue is None
    assert result.catalogue_hash_basis_json is None
    assert result.live_state_before == result.live_state_after
    assert result.model_file_before.sha256 == result.model_file_after.sha256
    assert observer.calls == [r"C:\Models\W3 Authorized Copy.edb"] * 2
    assert sap_model.unit_reads == 2


def test_w3d_transport_rejects_any_post_read_etabs_state_change(monkeypatch) -> None:
    sap_model = _FakeSapModel(units_after=5)
    monkeypatch.setattr(bridge, "etabs_com_operation_v1", nullcontext)
    monkeypatch.setattr(
        bridge,
        "extract_etabs_result_catalogue_v1",
        lambda _sap_model, _request: _blocked_adapter_result(),
    )

    with pytest.raises(ETABSDataError) as exc_info:
        bridge.run_etabs_live_catalogue_v1(
            _request(),
            session_factory=lambda: _FakeSession(sap_model),
            observe_model_file=_Observer(),
        )

    assert exc_info.value.code == "ETABS_CATALOGUE_STATE_CHANGED"
