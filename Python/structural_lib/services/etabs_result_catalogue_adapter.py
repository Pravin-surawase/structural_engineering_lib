# SPDX-License-Identifier: MIT
"""Transport-neutral ETABS result-catalogue adapter.

The adapter consumes an already-supplied ``SapModel``-shaped object and never
imports COM, attaches to ETABS, opens a model, changes result selection, or runs
analysis/design.  W3C implements only the getter shapes statically proved by
the accepted W3B installed-signature packet.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from enum import StrEnum
from functools import partial
from hashlib import sha256
from typing import Any, Literal, Self

from pydantic import Field, ValidationError, model_validator

from structural_lib.core.analysis_contracts import (
    AnalysisStateV1,
    AnalysisStatusIdentityV1,
    EvidenceStateV1,
    EvidenceValueV1,
    LinearStaticCaseParametersV1,
    LinearStaticInitialConditionV1,
    LinearStaticLoadItemV1,
    LoadCaseDefinitionV1,
    LoadPatternDefinitionV1,
    ResponseCombinationDefinitionV1,
    ResponseCombinationFactorV1,
    ResponseCombinationSourceKindV1,
    ResultSelectionIdentityV1,
    ResultSelectionKindV1,
    UnsupportedCaseParametersV1,
)
from structural_lib.services.contracts.common import StrictPublicModel
from structural_lib.services.contracts.etabs_w3 import (
    ETABSResultCatalogueBuildRequestV1,
    ETABSResultCatalogueV1,
    W3BuildIssueV1,
    W3BuildStatusV1,
    build_etabs_result_catalogue_v1,
)

__all__ = [
    "ETABSCatalogueAdapterRequestV1",
    "ETABSCatalogueAdapterResultV1",
    "ETABSCatalogueSelectionRequestV1",
    "ETABSGetterCallEvidenceV1",
    "ETABSGetterContainerKindV1",
    "ETABSGetterOutcomeV1",
    "extract_etabs_result_catalogue_v1",
]

_SHA256_PATTERN = r"^[0-9a-f]{64}$"
_UTC_PATTERN = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
_MAX_CATALOGUE_ROWS = 100_000
_LINEAR_STATIC_CASE_TYPE = 1
_CASE_SOURCE_KIND = 0
_COMBINATION_SOURCE_KIND = 1

_LOAD_PATTERN_TYPES = {
    1: "DEAD",
    2: "SUPER_DEAD",
    3: "LIVE",
    4: "REDUCIBLE_LIVE",
    5: "QUAKE",
    6: "WIND",
    7: "SNOW",
    8: "OTHER",
    9: "MOVE",
    10: "TEMPERATURE",
    11: "ROOF_LIVE",
    12: "NOTIONAL",
    13: "PATTERN_LIVE",
    14: "WAVE",
    15: "BRAKING",
    16: "CENTRIFUGAL",
    17: "FRICTION",
    18: "ICE",
    19: "WIND_ON_LIVE_LOAD",
    20: "HORIZONTAL_EARTH_PRESSURE",
    21: "VERTICAL_EARTH_PRESSURE",
    22: "EARTH_SURCHARGE",
    23: "DOWN_DRAG",
    24: "VEHICLE_COLLISION",
    25: "VESSEL_COLLISION",
    26: "TEMPERATURE_GRADIENT",
    27: "SETTLEMENT",
    28: "SHRINKAGE",
    29: "CREEP",
    30: "WATER_LOAD_PRESSURE",
    31: "LIVE_LOAD_SURCHARGE",
    32: "LOCKED_IN_FORCES",
    33: "PEDESTRIAN_LL",
    34: "PRESTRESS",
    35: "HYPERSTATIC",
    36: "BOUYANCY",
    37: "STREAM_FLOW",
    38: "IMPACT",
    39: "CONSTRUCTION",
}

_ANALYSIS_STATES = {
    1: AnalysisStateV1.NOT_RUN,
    2: AnalysisStateV1.COULD_NOT_START,
    3: AnalysisStateV1.NOT_FINISHED,
    4: AnalysisStateV1.FINISHED,
}


class ETABSGetterContainerKindV1(StrEnum):
    LIST = "LIST"
    TUPLE = "TUPLE"
    UNAVAILABLE = "UNAVAILABLE"


class ETABSGetterOutcomeV1(StrEnum):
    ACCEPTED = "ACCEPTED"
    BLOCKED = "BLOCKED"


class ETABSCatalogueSelectionRequestV1(StrictPublicModel):
    kind: ResultSelectionKindV1 = Field(strict=False)
    name: str = Field(min_length=1, max_length=160)


class ETABSCatalogueAdapterRequestV1(StrictPublicModel):
    schema_version: Literal["etabs-catalogue-adapter-request/v1"] = (
        "etabs-catalogue-adapter-request/v1"
    )
    model_identity_sha256: str = Field(pattern=_SHA256_PATTERN)
    runtime_identity_sha256: str = Field(pattern=_SHA256_PATTERN)
    getter_matrix_sha256: str = Field(pattern=_SHA256_PATTERN)
    model_observation_before: str = Field(min_length=1, max_length=500)
    model_observation_after: str = Field(min_length=1, max_length=500)
    observed_at_utc: str = Field(pattern=_UTC_PATTERN)
    result_selections: tuple[ETABSCatalogueSelectionRequestV1, ...] = Field(
        min_length=1,
        max_length=1_000,
    )
    capacity_limit: int = Field(default=_MAX_CATALOGUE_ROWS, ge=1, le=100_000)

    @model_validator(mode="after")
    def validate_selection_identity(self) -> Self:
        identities = tuple(
            (selection.kind.value, selection.name)
            for selection in self.result_selections
        )
        if len(identities) != len(set(identities)):
            raise ValueError("result selections must be unique and ordered")
        return self


class ETABSGetterCallEvidenceV1(StrictPublicModel):
    call_index: int = Field(ge=0)
    operation: str = Field(min_length=1, max_length=160)
    target: str = Field(min_length=1, max_length=160)
    signature_verdict: Literal["PROVED"] = "PROVED"
    source_identity_sha256: str = Field(pattern=_SHA256_PATTERN)
    outcome: ETABSGetterOutcomeV1 = Field(strict=False)
    outer_container: ETABSGetterContainerKindV1 = Field(strict=False)
    decoded_output_count: int | None = Field(default=None, ge=0)
    csi_return_code: int | None = None
    reason_code: str | None = Field(default=None, min_length=1, max_length=120)
    evidence_reference: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def validate_outcome(self) -> Self:
        if self.outcome is ETABSGetterOutcomeV1.ACCEPTED:
            if (
                self.outer_container is ETABSGetterContainerKindV1.UNAVAILABLE
                or self.decoded_output_count is None
                or self.csi_return_code != 0
                or self.reason_code is not None
            ):
                raise ValueError(
                    "accepted getter evidence requires decoded zero-return data"
                )
        elif self.reason_code is None:
            raise ValueError("blocked getter evidence requires a stable reason code")
        return self


class ETABSCatalogueAdapterResultV1(StrictPublicModel):
    schema_version: Literal["etabs-catalogue-adapter-result/v1"] = (
        "etabs-catalogue-adapter-result/v1"
    )
    status: W3BuildStatusV1 = Field(strict=False)
    issues: tuple[W3BuildIssueV1, ...]
    operation_evidence: tuple[ETABSGetterCallEvidenceV1, ...]
    normalized_request: ETABSResultCatalogueBuildRequestV1 | None
    catalogue: ETABSResultCatalogueV1 | None

    @model_validator(mode="after")
    def validate_outcome(self) -> Self:
        indexes = tuple(item.call_index for item in self.operation_evidence)
        if indexes != tuple(range(len(indexes))):
            raise ValueError("getter call indexes must be contiguous from zero")
        if self.status is W3BuildStatusV1.ACCEPTED:
            if self.issues or self.normalized_request is None or self.catalogue is None:
                raise ValueError("accepted adapter results require complete values")
            if any(
                item.outcome is not ETABSGetterOutcomeV1.ACCEPTED
                for item in self.operation_evidence
            ):
                raise ValueError("accepted adapter results forbid blocked getter calls")
        elif (
            not self.issues
            or self.normalized_request is not None
            or self.catalogue is not None
        ):
            raise ValueError(
                "blocked adapter results require issues and no partial values"
            )
        return self


class _AdapterError(Exception):
    def __init__(self, issue: W3BuildIssueV1) -> None:
        super().__init__(issue.message)
        self.issue = issue


def _canonical_json(value: Mapping[str, Any] | Sequence[Any]) -> str:
    return json.dumps(value, allow_nan=False, separators=(",", ":"), sort_keys=True)


def _sha(value: Mapping[str, Any] | Sequence[Any]) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _stable_id(prefix: str, value: Mapping[str, Any]) -> str:
    return f"{prefix}:{_sha(value)[:24]}"


def _definition_sha(
    value: LoadCaseDefinitionV1 | ResponseCombinationDefinitionV1,
) -> str:
    payload = value.model_dump(mode="json")
    payload.pop("definition_sha256", None)
    return _sha(payload)


def _issue(code: str, path: str, message: str) -> W3BuildIssueV1:
    return W3BuildIssueV1(code=code, path=path, message=message)


def _evidence_reference(operation: str, target: str) -> str:
    return f"etabs-w3c:{operation}:{target}"


def _present(value: Any, reference: str) -> EvidenceValueV1[Any]:
    return EvidenceValueV1(
        state=EvidenceStateV1.PRESENT,
        value=value,
        source_references=(reference,),
    )


def _not_applicable(reference: str) -> EvidenceValueV1[Any]:
    return EvidenceValueV1(
        state=EvidenceStateV1.NOT_APPLICABLE,
        value=None,
        reason_code="FIELD_NOT_APPLICABLE",
        message="The declared selection kind does not use this field.",
        source_references=(reference,),
    )


def _unavailable(code: str, message: str, reference: str) -> EvidenceValueV1[Any]:
    return EvidenceValueV1(
        state=EvidenceStateV1.UNAVAILABLE,
        value=None,
        reason_code=code,
        message=message,
        source_references=(reference,),
    )


class _GetterReader:
    def __init__(self, source_identity_sha256: str) -> None:
        self.source_identity_sha256 = source_identity_sha256
        self.evidence: list[ETABSGetterCallEvidenceV1] = []

    def _record(
        self,
        *,
        operation: str,
        target: str,
        outcome: ETABSGetterOutcomeV1,
        container: ETABSGetterContainerKindV1,
        output_count: int | None,
        return_code: int | None,
        reason_code: str | None,
    ) -> None:
        self.evidence.append(
            ETABSGetterCallEvidenceV1(
                call_index=len(self.evidence),
                operation=operation,
                target=target,
                source_identity_sha256=self.source_identity_sha256,
                outcome=outcome,
                outer_container=container,
                decoded_output_count=output_count,
                csi_return_code=return_code,
                reason_code=reason_code,
                evidence_reference=_evidence_reference(operation, target),
            )
        )

    def call(
        self,
        operation: str,
        target: str,
        output_count: int,
        provider: Callable[[], object],
    ) -> tuple[object, ...]:
        try:
            value = provider()
        except Exception as exc:
            self._record(
                operation=operation,
                target=target,
                outcome=ETABSGetterOutcomeV1.BLOCKED,
                container=ETABSGetterContainerKindV1.UNAVAILABLE,
                output_count=None,
                return_code=None,
                reason_code="ETABS_PROVIDER_EXCEPTION",
            )
            raise _AdapterError(
                _issue(
                    "ETABS_PROVIDER_EXCEPTION",
                    operation,
                    f"{operation} raised {type(exc).__name__}: {exc}",
                )
            ) from exc

        if isinstance(value, list):
            container = ETABSGetterContainerKindV1.LIST
        elif isinstance(value, tuple):
            container = ETABSGetterContainerKindV1.TUPLE
        else:
            self._record(
                operation=operation,
                target=target,
                outcome=ETABSGetterOutcomeV1.BLOCKED,
                container=ETABSGetterContainerKindV1.UNAVAILABLE,
                output_count=None,
                return_code=None,
                reason_code="ETABS_COM_SHAPE_INVALID",
            )
            raise _AdapterError(
                _issue(
                    "ETABS_COM_SHAPE_INVALID",
                    operation,
                    f"{operation} returned {type(value).__name__}; expected list or tuple.",
                )
            )

        expected = output_count + 1
        return_code = value[-1] if value else None
        if len(value) != expected:
            self._record(
                operation=operation,
                target=target,
                outcome=ETABSGetterOutcomeV1.BLOCKED,
                container=container,
                output_count=max(len(value) - 1, 0),
                return_code=(
                    return_code
                    if isinstance(return_code, int)
                    and not isinstance(return_code, bool)
                    else None
                ),
                reason_code="ETABS_COM_SHAPE_INVALID",
            )
            raise _AdapterError(
                _issue(
                    "ETABS_COM_SHAPE_INVALID",
                    operation,
                    f"{operation} returned {len(value)} values; expected {expected} including the CSI return code.",
                )
            )
        if (
            isinstance(return_code, bool)
            or not isinstance(return_code, int)
            or return_code != 0
        ):
            self._record(
                operation=operation,
                target=target,
                outcome=ETABSGetterOutcomeV1.BLOCKED,
                container=container,
                output_count=output_count,
                return_code=(
                    return_code
                    if isinstance(return_code, int)
                    and not isinstance(return_code, bool)
                    else None
                ),
                reason_code="ETABS_API_CALL_FAILED",
            )
            raise _AdapterError(
                _issue(
                    "ETABS_API_CALL_FAILED",
                    operation,
                    f"{operation} returned CSI code {return_code!r}; expected zero.",
                )
            )
        self._record(
            operation=operation,
            target=target,
            outcome=ETABSGetterOutcomeV1.ACCEPTED,
            container=container,
            output_count=output_count,
            return_code=0,
            reason_code=None,
        )
        return tuple(value[:-1])


def _exact_int(operation: str, label: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise _AdapterError(
            _issue(
                "ETABS_VALUE_INVALID",
                operation,
                f"{operation} {label} must be an exact integer; got {value!r}.",
            )
        )
    return value


def _finite_float(operation: str, label: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _AdapterError(
            _issue(
                "ETABS_VALUE_INVALID",
                operation,
                f"{operation} {label} must be numeric; got {value!r}.",
            )
        )
    decoded = float(value)
    if decoded != decoded or decoded in (float("inf"), float("-inf")):
        raise _AdapterError(
            _issue(
                "ETABS_VALUE_INVALID",
                operation,
                f"{operation} {label} must be finite.",
            )
        )
    return decoded


def _nonblank(operation: str, label: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise _AdapterError(
            _issue(
                "ETABS_VALUE_INVALID",
                operation,
                f"{operation} {label} must be a nonblank string.",
            )
        )
    return value.strip()


def _exact_array(
    operation: str,
    label: str,
    value: object,
    *,
    expected_count: int,
) -> tuple[object, ...]:
    if not isinstance(value, (list, tuple)):
        raise _AdapterError(
            _issue(
                "ETABS_ARRAY_SHAPE_INVALID",
                operation,
                f"{operation} {label} must be a list or tuple.",
            )
        )
    if len(value) != expected_count:
        raise _AdapterError(
            _issue(
                "ETABS_ARRAY_COUNT_MISMATCH",
                operation,
                f"{operation} {label} has {len(value)} values; expected {expected_count}.",
            )
        )
    return tuple(value)


def _name_list(
    reader: _GetterReader,
    operation: str,
    provider: Callable[[], object],
) -> tuple[str, ...]:
    number, raw_names = reader.call(operation, "<inventory>", 2, provider)
    count = _exact_int(operation, "count", number)
    if count < 0:
        raise _AdapterError(
            _issue("ETABS_VALUE_INVALID", operation, f"{operation} count is negative.")
        )
    names = tuple(
        _nonblank(operation, "name", item)
        for item in _exact_array(operation, "names", raw_names, expected_count=count)
    )
    if len(names) != len(set(names)):
        raise _AdapterError(
            _issue(
                "ETABS_NAME_LIST_DUPLICATE",
                operation,
                f"{operation} returned duplicate names.",
            )
        )
    return names


def _pattern_type_label(raw_value: int) -> str:
    return _LOAD_PATTERN_TYPES.get(raw_value, f"ELOADPATTERNTYPE_{raw_value}")


def _case_type_label(raw_value: int) -> str:
    if raw_value == _LINEAR_STATIC_CASE_TYPE:
        return "LINEAR_STATIC"
    return f"ELOADCASETYPE_{raw_value}"


def _combo_type_label(raw_value: int) -> str:
    return f"ECOMBOTYPE_{raw_value}"


def _blocked_result(
    reader: _GetterReader,
    *issues: W3BuildIssueV1,
) -> ETABSCatalogueAdapterResultV1:
    return ETABSCatalogueAdapterResultV1(
        status=W3BuildStatusV1.BLOCKED,
        issues=tuple(issues),
        operation_evidence=tuple(reader.evidence),
        normalized_request=None,
        catalogue=None,
    )


def extract_etabs_result_catalogue_v1(
    sap_model: Any,
    request: ETABSCatalogueAdapterRequestV1,
    /,
) -> ETABSCatalogueAdapterResultV1:
    """Read the proved getter matrix and build one complete W3A catalogue.

    The supplied provider is not opened or attached here.  Any provider
    exception, outer/inner shape mismatch, nonzero CSI code, unknown nested
    target, unsupported selected case family, nonblank linear-static initial
    case, or W3A validation issue returns ``BLOCKED`` with no partial normalized
    request or catalogue.
    """

    reader = _GetterReader(request.getter_matrix_sha256)
    try:
        pattern_names = _name_list(
            reader,
            "LoadPatterns.GetNameList",
            sap_model.LoadPatterns.GetNameList,
        )
        patterns: list[LoadPatternDefinitionV1] = []
        for ordinal, name in enumerate(pattern_names):
            operation = "LoadPatterns.GetLoadType"
            (raw_type_value,) = reader.call(
                operation,
                name,
                1,
                partial(sap_model.LoadPatterns.GetLoadType, name),
            )
            raw_type = _exact_int(operation, "type", raw_type_value)
            multiplier_operation = "LoadPatterns.GetSelfWTMultiplier"
            (raw_multiplier,) = reader.call(
                multiplier_operation,
                name,
                1,
                partial(sap_model.LoadPatterns.GetSelfWTMultiplier, name),
            )
            label = _pattern_type_label(raw_type)
            patterns.append(
                LoadPatternDefinitionV1(
                    pattern_id=_stable_id("load-pattern", {"name": name}),
                    name=name,
                    raw_type=f"eLoadPatternType:{raw_type}",
                    normalized_type=label,
                    self_weight_multiplier=_finite_float(
                        multiplier_operation,
                        "self-weight multiplier",
                        raw_multiplier,
                    ),
                    source_ordinal=ordinal,
                    evidence_reference=_evidence_reference(operation, name),
                )
            )

        case_names = _name_list(
            reader,
            "LoadCases.GetNameList",
            sap_model.LoadCases.GetNameList,
        )
        status_operation = "Analyze.GetCaseStatus"
        status_count_raw, raw_status_names, raw_status_values = reader.call(
            status_operation,
            "<inventory>",
            3,
            sap_model.Analyze.GetCaseStatus,
        )
        status_count = _exact_int(status_operation, "count", status_count_raw)
        if status_count < 0:
            raise _AdapterError(
                _issue(
                    "ETABS_VALUE_INVALID",
                    status_operation,
                    "Analyze.GetCaseStatus count is negative.",
                )
            )
        status_names = tuple(
            _nonblank(status_operation, "case name", value)
            for value in _exact_array(
                status_operation,
                "case names",
                raw_status_names,
                expected_count=status_count,
            )
        )
        status_values = tuple(
            _exact_int(status_operation, "status", value)
            for value in _exact_array(
                status_operation,
                "statuses",
                raw_status_values,
                expected_count=status_count,
            )
        )
        if len(status_names) != len(set(status_names)):
            raise _AdapterError(
                _issue(
                    "ETABS_CASE_STATUS_DUPLICATE",
                    status_operation,
                    "Analyze.GetCaseStatus returned duplicate case names.",
                )
            )
        statuses_by_name = dict(zip(status_names, status_values, strict=True))

        cases: list[LoadCaseDefinitionV1] = []
        statuses: list[AnalysisStatusIdentityV1] = []
        case_type_by_name: dict[str, int] = {}
        for ordinal, name in enumerate(case_names):
            operation = "LoadCases.GetTypeOAPI_1"
            (
                raw_case_type_value,
                raw_subtype_value,
                raw_design_type_value,
                raw_design_type_option_value,
                raw_auto_value,
            ) = reader.call(
                operation,
                name,
                5,
                partial(sap_model.LoadCases.GetTypeOAPI_1, name),
            )
            case_type = _exact_int(operation, "case type", raw_case_type_value)
            subtype = _exact_int(operation, "subtype", raw_subtype_value)
            design_type = _exact_int(operation, "design type", raw_design_type_value)
            design_type_option = _exact_int(
                operation,
                "design type option",
                raw_design_type_option_value,
            )
            auto = _exact_int(operation, "auto", raw_auto_value)
            is_auto = (
                _present(bool(auto), _evidence_reference(operation, name))
                if auto in (0, 1)
                else _unavailable(
                    "ETABS_AUTO_FLAG_SEMANTICS_UNDOCUMENTED",
                    "The installed ETABS getter returned an exact integer outside "
                    "the documented 0/1 mapping; the raw value is retained without "
                    "guessing its Boolean meaning.",
                    _evidence_reference(operation, name),
                )
            )
            case_type_by_name[name] = case_type
            status_code = statuses_by_name.get(name)
            if status_code is None:
                raise _AdapterError(
                    _issue(
                        "ANALYSIS_STATUS_IDENTITY_MISSING",
                        status_operation,
                        f"Load case {name!r} is absent from Analyze.GetCaseStatus.",
                    )
                )
            status_id = _stable_id("analysis-status", {"case_name": name})
            case_id = _stable_id("load-case", {"name": name})
            status_state = _ANALYSIS_STATES.get(status_code, AnalysisStateV1.UNKNOWN)
            statuses.append(
                AnalysisStatusIdentityV1(
                    status_id=status_id,
                    case_id=case_id,
                    raw_status_code=status_code,
                    state=status_state,
                    getter_identity=status_operation,
                    signature_identity=request.getter_matrix_sha256,
                    model_observation_before=request.model_observation_before,
                    model_observation_after=request.model_observation_after,
                    observed_at_utc=request.observed_at_utc,
                    evidence_reference=_evidence_reference(status_operation, name),
                )
            )

            raw_case_type = f"eLoadCaseType:{case_type}"
            raw_subtype = f"SubType:{subtype}"
            raw_design_type = (
                f"eLoadPatternType:{design_type};"
                f"DesignTypeOption:{design_type_option};"
                f"Normalized:{_pattern_type_label(design_type)}"
            )
            parameters: LinearStaticCaseParametersV1 | UnsupportedCaseParametersV1
            if case_type == _LINEAR_STATIC_CASE_TYPE:
                initial_operation = "LoadCases.StaticLinear.GetInitialCase"
                (raw_initial_case,) = reader.call(
                    initial_operation,
                    name,
                    1,
                    partial(sap_model.LoadCases.StaticLinear.GetInitialCase, name),
                )
                if not isinstance(raw_initial_case, str):
                    raise _AdapterError(
                        _issue(
                            "ETABS_VALUE_INVALID",
                            initial_operation,
                            f"Linear-static case {name!r} returned a non-string initial case.",
                        )
                    )
                if raw_initial_case.strip().casefold() not in {"", "none"}:
                    raise _AdapterError(
                        _issue(
                            "LINEAR_STATIC_INITIAL_CASE_UNSUPPORTED",
                            initial_operation,
                            f"Linear-static case {name!r} has prior initial case {raw_initial_case!r}; the accepted zero-state contract does not model prior-case stiffness semantics.",
                        )
                    )
                loads_operation = "LoadCases.StaticLinear.GetLoads"
                (
                    raw_load_count,
                    raw_load_types,
                    raw_load_names,
                    raw_scale_factors,
                ) = reader.call(
                    loads_operation,
                    name,
                    4,
                    partial(sap_model.LoadCases.StaticLinear.GetLoads, name),
                )
                load_count = _exact_int(loads_operation, "count", raw_load_count)
                if load_count <= 0:
                    raise _AdapterError(
                        _issue(
                            "LINEAR_STATIC_LOADS_EMPTY",
                            loads_operation,
                            f"Linear-static case {name!r} requires at least one ordered load item.",
                        )
                    )
                load_types = _exact_array(
                    loads_operation,
                    "load types",
                    raw_load_types,
                    expected_count=load_count,
                )
                load_names = _exact_array(
                    loads_operation,
                    "load names",
                    raw_load_names,
                    expected_count=load_count,
                )
                scale_factors = _exact_array(
                    loads_operation,
                    "scale factors",
                    raw_scale_factors,
                    expected_count=load_count,
                )
                parameters = LinearStaticCaseParametersV1(
                    initial_condition=LinearStaticInitialConditionV1(
                        raw_initial_case=raw_initial_case,
                        evidence_reference=_evidence_reference(
                            initial_operation,
                            name,
                        ),
                    ),
                    load_items=tuple(
                        LinearStaticLoadItemV1(
                            ordinal=index,
                            load_type=_nonblank(
                                loads_operation,
                                "load type",
                                load_types[index],
                            ),
                            load_name=_nonblank(
                                loads_operation,
                                "load name",
                                load_names[index],
                            ),
                            scale_factor=_finite_float(
                                loads_operation,
                                "scale factor",
                                scale_factors[index],
                            ),
                            evidence_reference=_evidence_reference(
                                loads_operation,
                                f"{name}:{index}",
                            ),
                        )
                        for index in range(load_count)
                    ),
                )
            else:
                parameters = UnsupportedCaseParametersV1(
                    raw_type=raw_case_type,
                    raw_subtype=raw_subtype,
                    parameter_evidence=_unavailable(
                        "CASE_FAMILY_NOT_MODELED",
                        "The installed case-family identity is retained, but W3A has no typed parameter contract for it.",
                        _evidence_reference(operation, name),
                    ),
                )
            provisional_case = LoadCaseDefinitionV1(
                case_id=case_id,
                name=name,
                raw_type=raw_case_type,
                raw_subtype=raw_subtype,
                raw_design_type=raw_design_type,
                raw_auto_flag=auto,
                is_auto=is_auto,
                parameters=parameters,
                analysis_status_id=status_id,
                source_ordinal=ordinal,
                evidence_reference=_evidence_reference(operation, name),
                definition_sha256="0" * 64,
            )
            cases.append(
                provisional_case.model_copy(
                    update={"definition_sha256": _definition_sha(provisional_case)}
                )
            )

        if set(statuses_by_name) != set(case_names):
            extras = sorted(set(statuses_by_name) - set(case_names))
            raise _AdapterError(
                _issue(
                    "ANALYSIS_STATUS_INVENTORY_MISMATCH",
                    status_operation,
                    f"Analyze.GetCaseStatus contains cases absent from LoadCases.GetNameList: {extras!r}.",
                )
            )

        combination_names = _name_list(
            reader,
            "RespCombo.GetNameList",
            sap_model.RespCombo.GetNameList,
        )
        combinations: list[ResponseCombinationDefinitionV1] = []
        for ordinal, name in enumerate(combination_names):
            type_operation = "RespCombo.GetTypeOAPI"
            (raw_combo_type_value,) = reader.call(
                type_operation,
                name,
                1,
                partial(sap_model.RespCombo.GetTypeOAPI, name),
            )
            combo_type = _exact_int(
                type_operation, "combination type", raw_combo_type_value
            )
            factors_operation = "RespCombo.GetCaseList"
            (
                raw_factor_count,
                raw_source_kinds,
                raw_source_names,
                raw_scale_factors,
            ) = reader.call(
                factors_operation,
                name,
                4,
                partial(sap_model.RespCombo.GetCaseList, name),
            )
            factor_count = _exact_int(
                factors_operation,
                "factor count",
                raw_factor_count,
            )
            if factor_count <= 0:
                raise _AdapterError(
                    _issue(
                        "RESPONSE_COMBINATION_FACTORS_EMPTY",
                        factors_operation,
                        f"Response combination {name!r} requires at least one factor.",
                    )
                )
            source_kinds = _exact_array(
                factors_operation,
                "source kinds",
                raw_source_kinds,
                expected_count=factor_count,
            )
            source_names = _exact_array(
                factors_operation,
                "source names",
                raw_source_names,
                expected_count=factor_count,
            )
            scale_factors = _exact_array(
                factors_operation,
                "scale factors",
                raw_scale_factors,
                expected_count=factor_count,
            )
            factors: list[ResponseCombinationFactorV1] = []
            for factor_ordinal in range(factor_count):
                source_kind_value = _exact_int(
                    factors_operation,
                    "source kind",
                    source_kinds[factor_ordinal],
                )
                source_name = _nonblank(
                    factors_operation,
                    "source name",
                    source_names[factor_ordinal],
                )
                if source_kind_value == _CASE_SOURCE_KIND:
                    source_kind = ResponseCombinationSourceKindV1.CASE
                    source_id = _stable_id("load-case", {"name": source_name})
                elif source_kind_value == _COMBINATION_SOURCE_KIND:
                    source_kind = ResponseCombinationSourceKindV1.COMBINATION
                    source_id = _stable_id(
                        "response-combination",
                        {"name": source_name},
                    )
                else:
                    raise _AdapterError(
                        _issue(
                            "RESPONSE_COMBINATION_SOURCE_KIND_INVALID",
                            factors_operation,
                            f"Response combination {name!r} returned source kind {source_kind_value!r}; exact case=0 or combination=1 is required.",
                        )
                    )
                factors.append(
                    ResponseCombinationFactorV1(
                        ordinal=factor_ordinal,
                        source_kind=source_kind,
                        source_id=source_id,
                        source_name=source_name,
                        scale_factor=_finite_float(
                            factors_operation,
                            "scale factor",
                            scale_factors[factor_ordinal],
                        ),
                        evidence_reference=_evidence_reference(
                            factors_operation,
                            f"{name}:{factor_ordinal}",
                        ),
                    )
                )
            provisional_combo = ResponseCombinationDefinitionV1(
                combination_id=_stable_id(
                    "response-combination",
                    {"name": name},
                ),
                name=name,
                raw_type=f"eComboType:{combo_type}",
                normalized_type=_combo_type_label(combo_type),
                factors=tuple(factors),
                design_purpose=_unavailable(
                    "DESIGN_PURPOSE_NOT_EXPOSED_BY_PROVED_GETTERS",
                    "The proved installed getter matrix exposes combination type and ordered factors, not an engineering design-purpose classification.",
                    _evidence_reference(type_operation, name),
                ),
                source_ordinal=ordinal,
                evidence_reference=_evidence_reference(type_operation, name),
                definition_sha256="0" * 64,
            )
            combinations.append(
                provisional_combo.model_copy(
                    update={"definition_sha256": _definition_sha(provisional_combo)}
                )
            )

        case_by_name = {item.name: item for item in cases}
        combo_by_name = {item.name: item for item in combinations}
        status_by_case_id = {item.case_id: item for item in statuses}
        selections: list[ResultSelectionIdentityV1] = []
        for selection in request.result_selections:
            reference = _evidence_reference(
                (
                    "Results.Setup.GetCaseSelectedForOutput"
                    if selection.kind is ResultSelectionKindV1.CASE
                    else "Results.Setup.GetComboSelectedForOutput"
                ),
                selection.name,
            )
            if selection.kind is ResultSelectionKindV1.CASE:
                case = case_by_name.get(selection.name)
                if case is None:
                    raise _AdapterError(
                        _issue(
                            "RESULT_SELECTION_NOT_AVAILABLE",
                            "result_selections",
                            f"Requested case {selection.name!r} is absent from the case inventory.",
                        )
                    )
                if not isinstance(case.parameters, LinearStaticCaseParametersV1):
                    raise _AdapterError(
                        _issue(
                            "SELECTED_CASE_FAMILY_UNSUPPORTED",
                            "result_selections",
                            f"Requested case {selection.name!r} has unsupported type {case.raw_type!r}.",
                        )
                    )
                selection_operation = "Results.Setup.GetCaseSelectedForOutput"
                (selected_raw,) = reader.call(
                    selection_operation,
                    selection.name,
                    1,
                    partial(
                        sap_model.Results.Setup.GetCaseSelectedForOutput,
                        selection.name,
                    ),
                )
                status = status_by_case_id[case.case_id]
                case_status_id = _present(status.status_id, reference)
                combo_definition_id = _not_applicable(reference)
            else:
                combo = combo_by_name.get(selection.name)
                if combo is None:
                    raise _AdapterError(
                        _issue(
                            "RESULT_SELECTION_NOT_AVAILABLE",
                            "result_selections",
                            f"Requested combination {selection.name!r} is absent from the combination inventory.",
                        )
                    )
                selection_operation = "Results.Setup.GetComboSelectedForOutput"
                (selected_raw,) = reader.call(
                    selection_operation,
                    selection.name,
                    1,
                    partial(
                        sap_model.Results.Setup.GetComboSelectedForOutput,
                        selection.name,
                    ),
                )
                case_status_id = _not_applicable(reference)
                combo_definition_id = _present(combo.combination_id, reference)
            if not isinstance(selected_raw, bool):
                raise _AdapterError(
                    _issue(
                        "ETABS_VALUE_INVALID",
                        selection_operation,
                        f"Output-selection getter for {selection.name!r} did not return a boolean.",
                    )
                )
            selections.append(
                ResultSelectionIdentityV1(
                    selection_id=_stable_id(
                        "result-selection",
                        {"kind": selection.kind.value, "name": selection.name},
                    ),
                    kind=selection.kind,
                    name=selection.name,
                    selected_for_output=_present(selected_raw, reference),
                    case_status_id=case_status_id,
                    combination_definition_id=combo_definition_id,
                    model_identity_sha256=request.model_identity_sha256,
                    runtime_identity_sha256=request.runtime_identity_sha256,
                    getter_identity_sha256=request.getter_matrix_sha256,
                    model_observation_before=request.model_observation_before,
                    model_observation_after=request.model_observation_after,
                    evidence_reference=reference,
                )
            )

        normalized_request = ETABSResultCatalogueBuildRequestV1(
            model_identity_sha256=request.model_identity_sha256,
            runtime_identity_sha256=request.runtime_identity_sha256,
            getter_matrix_sha256=request.getter_matrix_sha256,
            load_patterns=tuple(patterns),
            load_cases=tuple(cases),
            analysis_statuses=tuple(statuses),
            response_combinations=tuple(combinations),
            result_selections=tuple(selections),
            capacity_limit=request.capacity_limit,
        )
        build = build_etabs_result_catalogue_v1(normalized_request)
        if build.status is W3BuildStatusV1.BLOCKED or build.catalogue is None:
            return _blocked_result(reader, *build.issues)
        return ETABSCatalogueAdapterResultV1(
            status=W3BuildStatusV1.ACCEPTED,
            issues=(),
            operation_evidence=tuple(reader.evidence),
            normalized_request=normalized_request,
            catalogue=build.catalogue,
        )
    except _AdapterError as exc:
        return _blocked_result(reader, exc.issue)
    except ValidationError as exc:
        return _blocked_result(
            reader,
            _issue(
                "ETABS_NORMALIZATION_VALIDATION_FAILED",
                "normalized_request",
                "Decoded ETABS values did not satisfy the accepted W3 contracts: "
                f"{exc.errors(include_url=False)!r}",
            ),
        )
