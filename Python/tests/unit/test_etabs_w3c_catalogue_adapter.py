"""W3C transport-neutral ETABS result-catalogue adapter tests."""

# ruff: noqa: N802 - fake methods intentionally mirror ETABS COM names.

from __future__ import annotations

import pytest

from structural_lib.core.analysis_contracts import (
    AnalysisStateV1,
    LinearStaticCaseParametersV1,
    ResponseCombinationSourceKindV1,
    ResultSelectionKindV1,
)
from structural_lib.services.contracts.etabs_w3 import W3BuildStatusV1
from structural_lib.services.etabs_result_catalogue_adapter import (
    ETABSCatalogueAdapterRequestV1,
    ETABSCatalogueSelectionRequestV1,
    ETABSGetterContainerKindV1,
    ETABSGetterOutcomeV1,
    extract_etabs_result_catalogue_v1,
)


def _request(
    *,
    selection_kind: ResultSelectionKindV1 = ResultSelectionKindV1.COMBINATION,
    selection_name: str = "ULS-NESTED",
    capacity_limit: int = 100_000,
) -> ETABSCatalogueAdapterRequestV1:
    return ETABSCatalogueAdapterRequestV1(
        model_identity_sha256="a" * 64,
        runtime_identity_sha256="b" * 64,
        getter_matrix_sha256="c" * 64,
        model_observation_before="fake:model:before",
        model_observation_after="fake:model:after",
        observed_at_utc="2026-08-30T00:00:00Z",
        result_selections=(
            ETABSCatalogueSelectionRequestV1(
                kind=selection_kind,
                name=selection_name,
            ),
        ),
        capacity_limit=capacity_limit,
    )


class _FakeLoadPatterns:
    def __init__(self, pack) -> None:
        self.pack = pack

    def GetNameList(self):
        return self.pack((2, self.pack(("DEAD", "LIVE")), 0))

    def GetLoadType(self, name):
        return self.pack((1 if name == "DEAD" else 3, 0))

    def GetSelfWTMultiplier(self, name):
        return self.pack((1.0 if name == "DEAD" else 0.0, 0))


class _FakeStaticLinear:
    def __init__(self, pack, *, initial_case: str = "") -> None:
        self.pack = pack
        self.initial_case = initial_case

    def GetInitialCase(self, name):
        return self.pack((self.initial_case if name == "DEAD" else "", 0))

    def GetLoads(self, name):
        return self.pack(
            (1, self.pack(("Load",)), self.pack((name,)), self.pack((1.0,)), 0)
        )


class _FakeLoadCases:
    def __init__(
        self,
        pack,
        *,
        auto: int = 0,
        initial_case: str = "None",
        unsupported_live: bool = False,
    ) -> None:
        self.pack = pack
        self.auto = auto
        self.unsupported_live = unsupported_live
        self.StaticLinear = _FakeStaticLinear(pack, initial_case=initial_case)
        self.insufficient_getter_calls = 0

    def GetNameList(self):
        return self.pack((2, self.pack(("DEAD", "LIVE")), 0))

    def GetTypeOAPI(self, name):
        self.insufficient_getter_calls += 1
        raise AssertionError("W3C must never call the insufficient overload")

    def GetTypeOAPI_1(self, name):
        case_type = 2 if name == "LIVE" and self.unsupported_live else 1
        design_type = 1 if name == "DEAD" else 3
        return self.pack((case_type, 1, design_type, 0, self.auto, 0))


class _FakeAnalyze:
    def __init__(
        self,
        pack,
        *,
        extra_status: bool = False,
        status_code: int = 4,
    ) -> None:
        self.pack = pack
        self.extra_status = extra_status
        self.status_code = status_code

    def GetCaseStatus(self):
        names = ("DEAD", "LIVE", "EXTRA") if self.extra_status else ("DEAD", "LIVE")
        return self.pack(
            (
                len(names),
                self.pack(names),
                self.pack((self.status_code,) * len(names)),
                0,
            )
        )


class _FakeRespCombo:
    def __init__(
        self,
        pack,
        *,
        bad_return: int = 0,
        count_mismatch: bool = False,
    ) -> None:
        self.pack = pack
        self.bad_return = bad_return
        self.count_mismatch = count_mismatch

    def GetNameList(self):
        return self.pack((2, self.pack(("ULS-BASE", "ULS-NESTED")), 0))

    def GetTypeOAPI(self, name):
        return self.pack((0, 0))

    def GetCaseList(self, name):
        if name == "ULS-BASE":
            count = 2
            kinds = (0, 0)
            names = ("DEAD", "LIVE")
            factors = (1.5, 1.5)
        else:
            count = 2
            kinds = (1, 0)
            names = ("ULS-BASE", "LIVE")
            factors = (1.0, -0.25)
        if self.count_mismatch:
            factors = factors[:1]
        return self.pack(
            (
                count,
                self.pack(kinds),
                self.pack(names),
                self.pack(factors),
                self.bad_return,
            )
        )


class _FakeSetup:
    def __init__(self, pack, *, selected: bool = True) -> None:
        self.pack = pack
        self.selected = selected
        self.calls: list[tuple[str, str]] = []

    def GetCaseSelectedForOutput(self, name):
        self.calls.append(("CASE", name))
        return self.pack((self.selected, 0))

    def GetComboSelectedForOutput(self, name):
        self.calls.append(("COMBINATION", name))
        return self.pack((self.selected, 0))


class _FakeResults:
    def __init__(self, pack, *, selected: bool = True) -> None:
        self.Setup = _FakeSetup(pack, selected=selected)

    def FrameForce(self, *_args):
        raise AssertionError("W3C catalogue extraction must not call FrameForce")


class _FakeSapModel:
    def __init__(
        self,
        pack=tuple,
        *,
        auto: int = 0,
        initial_case: str = "None",
        unsupported_live: bool = False,
        extra_status: bool = False,
        status_code: int = 4,
        combo_return: int = 0,
        combo_count_mismatch: bool = False,
        selected: bool = True,
    ) -> None:
        self.LoadPatterns = _FakeLoadPatterns(pack)
        self.LoadCases = _FakeLoadCases(
            pack,
            auto=auto,
            initial_case=initial_case,
            unsupported_live=unsupported_live,
        )
        self.Analyze = _FakeAnalyze(
            pack,
            extra_status=extra_status,
            status_code=status_code,
        )
        self.RespCombo = _FakeRespCombo(
            pack,
            bad_return=combo_return,
            count_mismatch=combo_count_mismatch,
        )
        self.Results = _FakeResults(pack, selected=selected)

    def RunAnalysis(self):
        raise AssertionError("W3C must not run analysis")

    def SetPresentUnits(self, *_args):
        raise AssertionError("W3C must not change units")


@pytest.mark.parametrize("pack", [tuple, list])
def test_w3c_accepts_proved_list_and_tuple_shapes_losslessly(pack) -> None:
    sap_model = _FakeSapModel(pack)

    result = extract_etabs_result_catalogue_v1(sap_model, _request())

    assert result.status is W3BuildStatusV1.ACCEPTED
    assert result.issues == ()
    assert result.catalogue is not None
    assert result.normalized_request is not None
    assert result.catalogue.capacity.load_pattern_count == 2
    assert result.catalogue.capacity.load_case_count == 2
    assert result.catalogue.capacity.response_combination_count == 2
    assert result.catalogue.capacity.combination_factor_count == 4
    assert result.catalogue.capacity.result_selection_count == 1
    assert result.catalogue.analysis_statuses[0].state is AnalysisStateV1.FINISHED
    assert all(
        isinstance(case.parameters, LinearStaticCaseParametersV1)
        for case in result.catalogue.load_cases
    )
    assert {
        case.parameters.initial_condition.raw_initial_case
        for case in result.catalogue.load_cases
        if isinstance(case.parameters, LinearStaticCaseParametersV1)
    } == {"None", ""}
    nested = result.catalogue.response_combinations[1]
    assert tuple(factor.source_kind for factor in nested.factors) == (
        ResponseCombinationSourceKindV1.COMBINATION,
        ResponseCombinationSourceKindV1.CASE,
    )
    assert tuple(factor.scale_factor for factor in nested.factors) == (1.0, -0.25)
    assert sap_model.LoadCases.insufficient_getter_calls == 0
    assert sap_model.Results.Setup.calls == [("COMBINATION", "ULS-NESTED")]
    assert len(result.operation_evidence) == 19
    assert tuple(item.call_index for item in result.operation_evidence) == tuple(
        range(19)
    )
    assert all(
        item.outer_container
        is (
            ETABSGetterContainerKindV1.LIST
            if pack is list
            else ETABSGetterContainerKindV1.TUPLE
        )
        for item in result.operation_evidence
    )
    assert all(
        item.outcome is ETABSGetterOutcomeV1.ACCEPTED
        for item in result.operation_evidence
    )


def test_w3c_list_and_tuple_catalogue_hashes_are_identical() -> None:
    tuple_result = extract_etabs_result_catalogue_v1(_FakeSapModel(tuple), _request())
    list_result = extract_etabs_result_catalogue_v1(_FakeSapModel(list), _request())

    assert tuple_result.catalogue is not None
    assert list_result.catalogue is not None
    assert (
        tuple_result.catalogue.catalogue_sha256
        == list_result.catalogue.catalogue_sha256
    )


@pytest.mark.parametrize(
    ("sap_model", "adapter_request", "reason_code"),
    [
        (
            _FakeSapModel(auto=2),
            _request(),
            "ETABS_AUTO_FLAG_INVALID",
        ),
        (
            _FakeSapModel(initial_case="PREVIOUS"),
            _request(),
            "LINEAR_STATIC_INITIAL_CASE_UNSUPPORTED",
        ),
        (
            _FakeSapModel(combo_return=7),
            _request(),
            "ETABS_API_CALL_FAILED",
        ),
        (
            _FakeSapModel(combo_count_mismatch=True),
            _request(),
            "ETABS_ARRAY_COUNT_MISMATCH",
        ),
        (
            _FakeSapModel(extra_status=True),
            _request(),
            "ANALYSIS_STATUS_INVENTORY_MISMATCH",
        ),
        (
            _FakeSapModel(status_code=-1),
            _request(),
            "ETABS_NORMALIZATION_VALIDATION_FAILED",
        ),
        (
            _FakeSapModel(unsupported_live=True),
            _request(
                selection_kind=ResultSelectionKindV1.CASE,
                selection_name="LIVE",
            ),
            "SELECTED_CASE_FAMILY_UNSUPPORTED",
        ),
        (
            _FakeSapModel(selected=False),
            _request(),
            "RESULT_SELECTION_NOT_ACTIVE",
        ),
    ],
)
def test_w3c_fail_closed_vectors_return_no_partial_catalogue(
    sap_model: _FakeSapModel,
    adapter_request: ETABSCatalogueAdapterRequestV1,
    reason_code: str,
) -> None:
    result = extract_etabs_result_catalogue_v1(sap_model, adapter_request)

    assert result.status is W3BuildStatusV1.BLOCKED
    assert result.normalized_request is None
    assert result.catalogue is None
    assert reason_code in {issue.code for issue in result.issues}


def test_w3c_provider_exception_is_evidenced_and_blocked() -> None:
    sap_model = _FakeSapModel()

    def _raise():
        raise RuntimeError("fake provider failure")

    sap_model.LoadPatterns.GetNameList = _raise
    result = extract_etabs_result_catalogue_v1(sap_model, _request())

    assert result.status is W3BuildStatusV1.BLOCKED
    assert {issue.code for issue in result.issues} == {"ETABS_PROVIDER_EXCEPTION"}
    assert len(result.operation_evidence) == 1
    call = result.operation_evidence[0]
    assert call.outcome is ETABSGetterOutcomeV1.BLOCKED
    assert call.outer_container is ETABSGetterContainerKindV1.UNAVAILABLE
    assert call.reason_code == "ETABS_PROVIDER_EXCEPTION"


def test_w3c_rejects_non_sequence_outer_shape() -> None:
    sap_model = _FakeSapModel()
    sap_model.LoadPatterns.GetNameList = lambda: "not-a-sequence"

    result = extract_etabs_result_catalogue_v1(sap_model, _request())

    assert result.status is W3BuildStatusV1.BLOCKED
    assert {issue.code for issue in result.issues} == {"ETABS_COM_SHAPE_INVALID"}
    assert result.operation_evidence[0].reason_code == "ETABS_COM_SHAPE_INVALID"


def test_w3c_capacity_overflow_blocks_without_partial_request() -> None:
    result = extract_etabs_result_catalogue_v1(
        _FakeSapModel(),
        _request(capacity_limit=1),
    )

    assert result.status is W3BuildStatusV1.BLOCKED
    assert result.normalized_request is None
    assert result.catalogue is None
    assert {issue.code for issue in result.issues} == {"CATALOGUE_CAPACITY_EXCEEDED"}
