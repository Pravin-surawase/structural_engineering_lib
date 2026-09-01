"""Fail-closed Windows ETABS-to-canonical-beam pilot service.

This module keeps COM access optional and isolated at the service boundary.  The
pilot attaches to an already-open ETABS process, reads one exact result selection,
and restores the user's present-unit setting before returning.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import math
import platform
from collections.abc import Callable, Iterator, Sequence
from contextlib import AbstractContextManager, contextmanager
from enum import StrEnum
from importlib.util import find_spec
from pathlib import PureWindowsPath
from threading import Lock
from typing import Any, Literal, Protocol

from pydantic import Field, model_validator

from structural_lib.core.analysis_contracts import (
    BeamActionRowV1,
    EvidenceStateV1,
    EvidenceValueV1,
    ResultSelectionKindV1,
)
from structural_lib.core.errors import InputContractError
from structural_lib.services.common_api import get_library_version
from structural_lib.services.contracts.beam import (
    BeamActionsV1,
    BeamCalculationBasisV1,
    BeamDesignInputV1,
    BeamDetailingOptionsV1,
    EffectiveDepthBasisRequestV1,
    IS456MaterialsV1,
    MemberIdentityV1,
    RectangularBeamSectionV1,
)
from structural_lib.services.contracts.common import StrictPublicModel
from structural_lib.services.evidence import get_library_content_identity

__all__ = [
    "ETABSBridgeError",
    "ETABSBridgeStatusV1",
    "ETABSConnectionError",
    "ETABSConnectionV1",
    "ETABSDataError",
    "ETABSPilotAuditProvenanceV1",
    "ETABSPilotDesignBasisV1",
    "ETABSPilotRequestV1",
    "ETABSPilotResultV1",
    "ETABSResultSelectionKind",
    "ETABSResultSelectionV1",
    "ETABSUnavailableError",
    "InputContractError",
    "connect_etabs_v1",
    "etabs_com_operation_v1",
    "get_etabs_bridge_status_v1",
    "run_etabs_beam_pilot_v1",
]


ETABS_BRIDGE_SCHEMA_VERSION: Literal["etabs-live-bridge/v1"] = "etabs-live-bridge/v1"
ETABS_PILOT_SCHEMA_VERSION: Literal["etabs-beam-pilot/v1"] = "etabs-beam-pilot/v1"
ETABS_OBJECT_ITEM_TYPE = 0
ETABS_KN_MM_C_UNITS = 5
MAX_RESULT_ROWS_PER_BEAM = 2_000
HORIZONTAL_TOLERANCE_MM = 1.0
_ETABS_COM_OPERATION_LOCK = Lock()


class ETABSResultSelectionKind(StrEnum):
    """Exact ETABS result source requested by the caller."""

    CASE = "CASE"
    COMBINATION = "COMBINATION"


class ETABSResultSelectionV1(StrictPublicModel):
    """One exact ETABS case or response combination."""

    kind: ETABSResultSelectionKind = Field(strict=False)
    name: str = Field(min_length=1, max_length=80)


class ETABSPilotAuditProvenanceV1(StrictPublicModel):
    """Accepted identities and signed M3-to-physical-face mapping for B0."""

    model_identity_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    baseline_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    catalogue_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    selection_id: str = Field(min_length=1, max_length=160)
    scenario_id: str = Field(min_length=1, max_length=160)
    local_axis_basis: str = Field(min_length=1, max_length=500)
    factored_action_basis: str = Field(min_length=1, max_length=500)
    max_abs_axial_kn: float = Field(ge=0)
    max_abs_minor_shear_kn: float = Field(ge=0)
    max_abs_minor_moment_knm: float = Field(ge=0)
    positive_m3_tension_face: Literal["TOP", "BOTTOM"]
    negative_m3_tension_face: Literal["TOP", "BOTTOM"]
    source_references: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_faces(self) -> ETABSPilotAuditProvenanceV1:
        if self.positive_m3_tension_face == self.negative_m3_tension_face:
            raise ValueError("opposite M3 signs require opposite physical faces")
        return self


class ETABSPilotDesignBasisV1(StrictPublicModel):
    """Explicit caller-owned design and detailing choices for every pilot beam."""

    materials: IS456MaterialsV1
    effective_depth_basis: EffectiveDepthBasisRequestV1
    d_dash_mm: float = Field(gt=0)
    detailing: BeamDetailingOptionsV1
    pt_percent: float | None = Field(default=None, gt=0)
    ast_mm2_for_shear: float | None = Field(default=None, gt=0)
    audit_provenance: ETABSPilotAuditProvenanceV1 | None = None


class ETABSPilotRequestV1(StrictPublicModel):
    """Bounded read-and-design request for no more than five ETABS beams."""

    schema_version: Literal["etabs-beam-pilot/v1"] = ETABS_PILOT_SCHEMA_VERSION
    result_selection: ETABSResultSelectionV1
    design_basis: ETABSPilotDesignBasisV1
    limit: int = Field(default=5, ge=1, le=5)


class ETABSModelIdentityV1(StrictPublicModel):
    """Identity of the ETABS model actually attached by COM."""

    model_name: str
    model_path: str
    etabs_version: str
    etabs_version_number: float


class ETABSBridgeStatusV1(StrictPublicModel):
    """Non-calculation availability and library identity."""

    schema_version: Literal["etabs-live-bridge/v1"] = ETABS_BRIDGE_SCHEMA_VERSION
    bridge_status: Literal[
        "READY_TO_CONNECT",
        "CONNECTED",
        "PLATFORM_UNSUPPORTED",
        "DEPENDENCY_MISSING",
    ]
    platform: str
    com_dependency: Literal["INSTALLED", "MISSING", "NOT_APPLICABLE"]
    library_version: str
    library_content_identity: str
    model: ETABSModelIdentityV1 | None = None
    issues: tuple[str, ...] = ()


class ETABSConnectionV1(StrictPublicModel):
    """Successful attachment proof without analysis or model mutation."""

    schema_version: Literal["etabs-live-bridge/v1"] = ETABS_BRIDGE_SCHEMA_VERSION
    bridge_status: Literal["CONNECTED"] = "CONNECTED"
    library_version: str
    library_content_identity: str
    model: ETABSModelIdentityV1


class ETABSFrameGeometryV1(StrictPublicModel):
    """ETABS frame identity and rectangular section geometry in millimetres."""

    frame_name: str
    story: str
    section_name: str
    material_property: str
    point_i: str
    point_j: str
    x_i_mm: float
    y_i_mm: float
    z_i_mm: float
    x_j_mm: float
    y_j_mm: float
    z_j_mm: float
    span_mm: float = Field(gt=0)
    b_mm: float = Field(gt=0)
    D_mm: float = Field(gt=0)


class ETABSFrameForceStationV1(StrictPublicModel):
    """One untruncated ETABS FrameForce row converted to canonical units."""

    row_index: int = Field(ge=0)
    object_name: str
    object_station_mm: float
    element_name: str
    element_station_mm: float
    load_case: str
    step_type: str
    step_number: float
    p_kn: float
    v2_kn: float
    v3_kn: float
    t_knm: float
    m2_knm: float
    m3_knm: float


class ETABSForceExtremeV1(StrictPublicModel):
    """Signed governing value retained alongside its absolute magnitude."""

    component: Literal["V2", "T", "M3"]
    signed_value: float
    absolute_value: float = Field(ge=0)
    row_index: int = Field(ge=0)
    object_station_mm: float
    load_case: str
    step_type: str
    step_number: float


class ETABSFrameForcesV1(StrictPublicModel):
    """Complete returned rows plus the three pilot governing actions."""

    selection: ETABSResultSelectionV1
    result_row_count: int = Field(gt=0, le=MAX_RESULT_ROWS_PER_BEAM)
    stations: tuple[ETABSFrameForceStationV1, ...]
    governing_v2: ETABSForceExtremeV1
    governing_t: ETABSForceExtremeV1
    governing_m3: ETABSForceExtremeV1


class ETABSPilotBeamResultV1(StrictPublicModel):
    """Extracted ETABS beam and canonical library design result."""

    geometry: ETABSFrameGeometryV1
    forces: ETABSFrameForcesV1
    design_result: dict[str, Any]


class ETABSPilotResultV1(StrictPublicModel):
    """Completed bounded ETABS read and canonical beam-design proof."""

    schema_version: Literal["etabs-beam-pilot/v1"] = ETABS_PILOT_SCHEMA_VERSION
    pilot_status: Literal["COMPLETED", "HELD"]
    model: ETABSModelIdentityV1
    result_selection: ETABSResultSelectionV1
    units: dict[str, str]
    candidate_beam_count: int = Field(ge=1)
    designed_beam_count: int = Field(ge=0, le=5)
    held_beam_count: int = Field(ge=0, le=5)
    beams: tuple[ETABSPilotBeamResultV1, ...]
    library_version: str
    library_content_identity: str
    calculation_owner: Literal["beam-audit-row/v1"] = "beam-audit-row/v1"
    legacy_transport_status: Literal["DEPRECATED_PENDING_A1"] = "DEPRECATED_PENDING_A1"
    qualified_review_required: Literal[True] = True
    limitations: tuple[str, ...]

    @model_validator(mode="after")
    def validate_counts(self) -> ETABSPilotResultV1:
        if self.designed_beam_count + self.held_beam_count != len(self.beams):
            raise ValueError("delegated plus held counts must equal beam results")
        if (self.pilot_status == "COMPLETED") != (self.held_beam_count == 0):
            raise ValueError("pilot status must reflect held compatibility rows")
        return self


class ETABSBridgeError(RuntimeError):
    """Base error carrying a stable problem code across the REST boundary."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code

    def to_problem(self) -> dict[str, str]:
        return {"code": self.code, "message": str(self)}


class ETABSUnavailableError(ETABSBridgeError):
    """The current host cannot provide the optional ETABS capability."""


class ETABSConnectionError(ETABSBridgeError):
    """ETABS is supported locally but no usable open model was attached."""


class ETABSDataError(ETABSBridgeError):
    """The attached model or requested result is outside the pilot contract."""


class _ETABSSession(Protocol):
    sap_model: Any

    def __enter__(self) -> _ETABSSession: ...

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None: ...

    def normalized_kn_mm_units(self) -> AbstractContextManager[None]: ...


SessionFactory = Callable[[], _ETABSSession]


def _library_identity() -> tuple[str, str]:
    return get_library_version(), get_library_content_identity()


def get_etabs_bridge_status_v1() -> ETABSBridgeStatusV1:
    """Report readiness without starting or attaching to ETABS."""

    host = platform.system()
    library_version, content_identity = _library_identity()
    if host != "Windows":
        return ETABSBridgeStatusV1(
            bridge_status="PLATFORM_UNSUPPORTED",
            platform=host,
            com_dependency="NOT_APPLICABLE",
            library_version=library_version,
            library_content_identity=content_identity,
            issues=("Live ETABS COM access is supported only on Windows.",),
        )
    if find_spec("comtypes") is None:
        return ETABSBridgeStatusV1(
            bridge_status="DEPENDENCY_MISSING",
            platform=host,
            com_dependency="MISSING",
            library_version=library_version,
            library_content_identity=content_identity,
            issues=(
                "Install the optional Python package extra: structural-lib-is456[etabs].",
            ),
        )
    return ETABSBridgeStatusV1(
        bridge_status="READY_TO_CONNECT",
        platform=host,
        com_dependency="INSTALLED",
        library_version=library_version,
        library_content_identity=content_identity,
    )


def _require_zero_return(operation: str, value: object) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value != 0:
        raise ETABSDataError(
            "ETABS_API_CALL_FAILED",
            f"{operation} returned {value!r}; expected ETABS return code 0.",
        )


def _decode_com_outputs(
    operation: str, value: object, *, output_count: int
) -> tuple[Any, ...]:
    """Normalize ETABS COM out values followed by the native return code."""

    if not isinstance(value, (list, tuple)) or len(value) != output_count + 1:
        raise ETABSDataError(
            "ETABS_COM_SIGNATURE_MISMATCH",
            f"{operation} returned an unexpected COM result shape.",
        )
    _require_zero_return(operation, value[-1])
    return tuple(value[:-1])


@contextmanager
def etabs_com_operation_v1() -> Iterator[None]:
    """Serialize access to the singleton ETABS process across worker threads."""

    with _ETABS_COM_OPERATION_LOCK:
        yield


class _ComtypesETABSSession:
    """One worker-thread COM apartment attached to an open ETABS process."""

    def __init__(self) -> None:
        if platform.system() != "Windows":
            raise ETABSUnavailableError(
                "ETABS_PLATFORM_UNSUPPORTED",
                "Live ETABS COM access is supported only on Windows.",
            )
        try:
            comtypes = importlib.import_module("comtypes")
            com_client = importlib.import_module("comtypes.client")
        except ImportError as exc:
            raise ETABSUnavailableError(
                "ETABS_COM_DEPENDENCY_MISSING",
                "Install structural-lib-is456[etabs] in the FastAPI Python environment.",
            ) from exc

        self._comtypes = comtypes
        self._closed = False
        comtypes.CoInitialize()
        try:
            helper = com_client.CreateObject("ETABSv1.Helper")
            etabs_object = helper.GetObject("CSI.ETABS.API.ETABSObject")
            sap_model = etabs_object.SapModel
        except Exception as exc:
            comtypes.CoUninitialize()
            raise ETABSConnectionError(
                "ETABS_OPEN_INSTANCE_NOT_FOUND",
                "Open ETABS with the copied model before connecting from Excel.",
            ) from exc
        if sap_model is None:
            comtypes.CoUninitialize()
            raise ETABSConnectionError(
                "ETABS_MODEL_NOT_AVAILABLE",
                "The attached ETABS process did not expose an open model.",
            )
        self._helper = helper
        self._etabs_object = etabs_object
        self.sap_model = sap_model

    def __enter__(self) -> _ComtypesETABSSession:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    def close(self) -> None:
        if self._closed:
            return
        self.sap_model = None
        self._etabs_object = None
        self._helper = None
        self._comtypes.CoUninitialize()
        self._closed = True

    @contextmanager
    def normalized_kn_mm_units(self) -> Iterator[None]:
        original_units = self.sap_model.GetPresentUnits()
        if isinstance(original_units, bool) or not isinstance(original_units, int):
            raise ETABSDataError(
                "ETABS_PRESENT_UNITS_INVALID",
                "ETABS did not return a valid present-unit enumeration.",
            )
        _require_zero_return(
            "SapModel.SetPresentUnits(kN_mm_C)",
            self.sap_model.SetPresentUnits(ETABS_KN_MM_C_UNITS),
        )
        try:
            yield
        finally:
            _require_zero_return(
                "SapModel.SetPresentUnits(restore)",
                self.sap_model.SetPresentUnits(original_units),
            )


def _default_session_factory() -> _ETABSSession:
    return _ComtypesETABSSession()


def _model_identity(sap_model: Any) -> ETABSModelIdentityV1:
    model_path = str(sap_model.GetModelFilename(True) or "").strip()
    if not model_path:
        raise ETABSConnectionError(
            "ETABS_MODEL_PATH_MISSING",
            "Save the copied ETABS model before running the Excel pilot.",
        )
    parsed_path = PureWindowsPath(model_path)
    if not parsed_path.is_absolute() or parsed_path.suffix.casefold() != ".edb":
        raise ETABSConnectionError(
            "ETABS_MODEL_PATH_INVALID",
            "ETABS did not return the full path of a saved .edb model.",
        )
    version, version_number = _decode_com_outputs(
        "SapModel.GetVersion", sap_model.GetVersion(), output_count=2
    )
    return ETABSModelIdentityV1(
        model_name=parsed_path.name,
        model_path=model_path,
        etabs_version=str(version),
        etabs_version_number=float(version_number),
    )


def connect_etabs_v1(
    *, session_factory: SessionFactory = _default_session_factory
) -> ETABSConnectionV1:
    """Attach to ETABS and return the exact open-model identity."""

    with etabs_com_operation_v1():
        with session_factory() as session:
            model = _model_identity(session.sap_model)
    library_version, content_identity = _library_identity()
    return ETABSConnectionV1(
        library_version=library_version,
        library_content_identity=content_identity,
        model=model,
    )


def _checked_sequence(
    operation: str, name: str, value: object, *, expected_count: int
) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ETABSDataError(
            "ETABS_COM_SIGNATURE_MISMATCH",
            f"{operation} did not return the expected {name} array.",
        )
    if len(value) < expected_count:
        raise ETABSDataError(
            "ETABS_RESULT_ARRAY_MISMATCH",
            f"{operation} returned {len(value)} {name} values for {expected_count} rows.",
        )
    return value


def _frame_inventory(sap_model: Any) -> list[dict[str, Any]]:
    outputs = _decode_com_outputs(
        "FrameObj.GetAllFrames",
        sap_model.FrameObj.GetAllFrames(),
        output_count=20,
    )
    number = int(outputs[0])
    if number <= 0:
        raise ETABSDataError(
            "ETABS_FRAME_INVENTORY_EMPTY",
            "The attached ETABS model has no frame objects.",
        )
    names = (
        "frame_name",
        "section_name",
        "story",
        "point_i",
        "point_j",
        "x_i",
        "y_i",
        "z_i",
        "x_j",
        "y_j",
        "z_j",
    )
    arrays = {
        name: _checked_sequence(
            "FrameObj.GetAllFrames", name, outputs[index], expected_count=number
        )
        for index, name in enumerate(names, start=1)
    }
    frames: list[dict[str, Any]] = []
    for index in range(number):
        frame = {name: values[index] for name, values in arrays.items()}
        dx = float(frame["x_j"]) - float(frame["x_i"])
        dy = float(frame["y_j"]) - float(frame["y_i"])
        dz = float(frame["z_j"]) - float(frame["z_i"])
        span = math.sqrt(dx * dx + dy * dy + dz * dz)
        if span <= 0:
            raise ETABSDataError(
                "ETABS_FRAME_LENGTH_INVALID",
                f"Frame {frame['frame_name']} has zero or invalid length.",
            )
        if abs(dz) <= HORIZONTAL_TOLERANCE_MM:
            frame["span_mm"] = span
            frames.append(frame)
    if not frames:
        raise ETABSDataError(
            "ETABS_BEAM_CANDIDATES_EMPTY",
            "No horizontal frame objects were found within the 1 mm pilot tolerance.",
        )
    return sorted(
        frames, key=lambda item: (str(item["story"]), str(item["frame_name"]))
    )


def _rectangular_geometry(
    sap_model: Any, frame: dict[str, Any]
) -> ETABSFrameGeometryV1:
    section_name = str(frame["section_name"])
    try:
        outputs = _decode_com_outputs(
            "PropFrame.GetRectangle",
            sap_model.PropFrame.GetRectangle(section_name),
            output_count=7,
        )
    except ETABSDataError as exc:
        raise ETABSDataError(
            "ETABS_SECTION_NOT_RECTANGULAR",
            f"Frame {frame['frame_name']} section {section_name} is not a supported rectangle.",
        ) from exc
    _file_name, material, t3, t2, _color, _notes, _guid = outputs
    return ETABSFrameGeometryV1(
        frame_name=str(frame["frame_name"]),
        story=str(frame["story"]),
        section_name=section_name,
        material_property=str(material),
        point_i=str(frame["point_i"]),
        point_j=str(frame["point_j"]),
        x_i_mm=float(frame["x_i"]),
        y_i_mm=float(frame["y_i"]),
        z_i_mm=float(frame["z_i"]),
        x_j_mm=float(frame["x_j"]),
        y_j_mm=float(frame["y_j"]),
        z_j_mm=float(frame["z_j"]),
        span_mm=float(frame["span_mm"]),
        b_mm=float(t2),
        D_mm=float(t3),
    )


def _select_results(sap_model: Any, selection: ETABSResultSelectionV1) -> None:
    setup = sap_model.Results.Setup
    _require_zero_return(
        "Results.Setup.DeselectAllCasesAndCombosForOutput",
        setup.DeselectAllCasesAndCombosForOutput(),
    )
    if selection.kind is ETABSResultSelectionKind.CASE:
        result = setup.SetCaseSelectedForOutput(selection.name, True)
    else:
        result = setup.SetComboSelectedForOutput(selection.name, True)
    if isinstance(result, bool) or not isinstance(result, int) or result != 0:
        raise ETABSDataError(
            "ETABS_RESULT_SELECTION_NOT_FOUND",
            f"ETABS did not accept {selection.kind.value} {selection.name!r} for output.",
        )


def _force_extreme(
    stations: tuple[ETABSFrameForceStationV1, ...],
    *,
    component: Literal["V2", "T", "M3"],
    attribute: str,
) -> ETABSForceExtremeV1:
    station = max(stations, key=lambda item: abs(float(getattr(item, attribute))))
    value = float(getattr(station, attribute))
    return ETABSForceExtremeV1(
        component=component,
        signed_value=value,
        absolute_value=abs(value),
        row_index=station.row_index,
        object_station_mm=station.object_station_mm,
        load_case=station.load_case,
        step_type=station.step_type,
        step_number=station.step_number,
    )


def _frame_forces(
    sap_model: Any,
    frame_name: str,
    selection: ETABSResultSelectionV1,
) -> ETABSFrameForcesV1:
    outputs = _decode_com_outputs(
        "Results.FrameForce",
        sap_model.Results.FrameForce(frame_name, ETABS_OBJECT_ITEM_TYPE),
        output_count=14,
    )
    count = int(outputs[0])
    if count <= 0:
        raise ETABSDataError(
            "ETABS_FRAME_RESULTS_EMPTY",
            f"No frame-force rows were returned for frame {frame_name} and {selection.name}.",
        )
    if count > MAX_RESULT_ROWS_PER_BEAM:
        raise ETABSDataError(
            "ETABS_FRAME_RESULTS_TOO_LARGE",
            f"Frame {frame_name} returned {count} rows; the pilot limit is {MAX_RESULT_ROWS_PER_BEAM}.",
        )
    array_names = (
        "object_name",
        "object_station_mm",
        "element_name",
        "element_station_mm",
        "load_case",
        "step_type",
        "step_number",
        "p_kn",
        "v2_kn",
        "v3_kn",
        "t_knmm",
        "m2_knmm",
        "m3_knmm",
    )
    arrays = {
        name: _checked_sequence(
            "Results.FrameForce", name, outputs[index], expected_count=count
        )
        for index, name in enumerate(array_names, start=1)
    }
    stations = tuple(
        ETABSFrameForceStationV1(
            row_index=index,
            object_name=str(arrays["object_name"][index]),
            object_station_mm=float(arrays["object_station_mm"][index]),
            element_name=str(arrays["element_name"][index]),
            element_station_mm=float(arrays["element_station_mm"][index]),
            load_case=str(arrays["load_case"][index]),
            step_type=str(arrays["step_type"][index]),
            step_number=float(arrays["step_number"][index]),
            p_kn=float(arrays["p_kn"][index]),
            v2_kn=float(arrays["v2_kn"][index]),
            v3_kn=float(arrays["v3_kn"][index]),
            t_knm=float(arrays["t_knmm"][index]) / 1_000.0,
            m2_knm=float(arrays["m2_knmm"][index]) / 1_000.0,
            m3_knm=float(arrays["m3_knmm"][index]) / 1_000.0,
        )
        for index in range(count)
    )
    if selection.name not in {station.load_case for station in stations}:
        raise ETABSDataError(
            "ETABS_RESULT_IDENTITY_MISMATCH",
            f"Frame {frame_name} results do not identify the selected result {selection.name!r}.",
        )
    return ETABSFrameForcesV1(
        selection=selection,
        result_row_count=count,
        stations=stations,
        governing_v2=_force_extreme(stations, component="V2", attribute="v2_kn"),
        governing_t=_force_extreme(stations, component="T", attribute="t_knm"),
        governing_m3=_force_extreme(stations, component="M3", attribute="m3_knm"),
    )


def _design_beam(
    geometry: ETABSFrameGeometryV1,
    forces: ETABSFrameForcesV1,
    basis: ETABSPilotDesignBasisV1,
) -> dict[str, Any]:
    # Lazy import avoids the legacy baseline -> live bridge dependency cycle.
    audit = importlib.import_module("structural_lib.services.beam_audit")
    provenance = basis.audit_provenance
    if provenance is None:
        return {
            "compatibility_status": "HELD",
            "delegated_to": "evaluate_beam_audit_row_v1",
            "issues": [
                {
                    "code": "ETABS_PILOT_FACE_PROVENANCE_REQUIRED",
                    "message": (
                        "Signed M3-to-physical-face mapping and accepted source "
                        "identities are required; the legacy pilot will not infer them."
                    ),
                }
            ],
            "limitations": [
                "No design result is emitted without explicit signed-face provenance.",
                "Use the complete W3 beam audit for accepted demand-domain evidence.",
            ],
        }
    governing_station = next(
        (
            station
            for station in forces.stations
            if station.row_index == forces.governing_m3.row_index
        ),
        None,
    )
    if governing_station is None:
        raise ETABSDataError(
            "ETABS_GOVERNING_ROW_MISSING",
            "The signed governing M3 reference does not identify a retained station.",
        )
    if (
        abs(governing_station.p_kn) > provenance.max_abs_axial_kn
        or abs(governing_station.v3_kn) > provenance.max_abs_minor_shear_kn
        or abs(governing_station.m2_knm) > provenance.max_abs_minor_moment_knm
    ):
        return {
            "compatibility_status": "HELD",
            "delegated_to": "evaluate_beam_audit_row_v1",
            "issues": [
                {
                    "code": "ETABS_PILOT_APPLICABILITY_EXCEEDED",
                    "message": "A same-row excluded action exceeds the caller-owned bound.",
                }
            ],
            "limitations": [
                "No partial major-axis strength result is emitted outside applicability."
            ],
        }
    tension_face: Literal["TOP", "BOTTOM", "ZERO_MOMENT"] = "ZERO_MOMENT"
    if governing_station.m3_knm > 0:
        tension_face = provenance.positive_m3_tension_face
    elif governing_station.m3_knm < 0:
        tension_face = provenance.negative_m3_tension_face
    source_identity = {
        "member_id": geometry.frame_name,
        "story": geometry.story,
        "selection_id": provenance.selection_id,
        "selection_kind": forces.selection.kind.value,
        "selection_name": forces.selection.name,
        "row_index": governing_station.row_index,
        "object_station_mm": governing_station.object_station_mm,
        "element_name": governing_station.element_name,
        "element_station_mm": governing_station.element_station_mm,
        "step_type": governing_station.step_type,
        "step_number": governing_station.step_number,
    }
    source_json = json.dumps(
        source_identity, sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    station_id = (
        f"etabs-pilot-row:{hashlib.sha256(source_json.encode()).hexdigest()[:24]}"
    )
    selection_kind = (
        ResultSelectionKindV1.CASE
        if forces.selection.kind is ETABSResultSelectionKind.CASE
        else ResultSelectionKindV1.COMBINATION
    )
    provisional_action = BeamActionRowV1(
        row_id=station_id,
        model_identity_sha256=provenance.model_identity_sha256,
        baseline_sha256=provenance.baseline_sha256,
        catalogue_sha256=provenance.catalogue_sha256,
        member_id=geometry.frame_name,
        source_frame_name=geometry.frame_name,
        station_id=station_id,
        selection_id=provenance.selection_id,
        selection_kind=selection_kind,
        selection_name=forces.selection.name,
        output_case_name=governing_station.load_case,
        object_name=governing_station.object_name,
        object_station_mm=governing_station.object_station_mm,
        element_name=governing_station.element_name,
        element_station_mm=governing_station.element_station_mm,
        step_type=governing_station.step_type,
        step_number=governing_station.step_number,
        source_row_index=governing_station.row_index,
        p_kn=governing_station.p_kn,
        v2_kn=governing_station.v2_kn,
        v3_kn=governing_station.v3_kn,
        t_knm=governing_station.t_knm,
        m2_knm=governing_station.m2_knm,
        m3_knm=governing_station.m3_knm,
        local_axis_basis=provenance.local_axis_basis,
        row_sha256="0" * 64,
    )
    action = provisional_action.model_copy(
        update={
            "row_sha256": audit.canonical_beam_action_row_sha256_v1(provisional_action)
        }
    )
    section = RectangularBeamSectionV1(
        span_mm=geometry.span_mm,
        b_mm=geometry.b_mm,
        D_mm=geometry.D_mm,
        d_mm=None,
        effective_depth_basis=basis.effective_depth_basis,
    )
    calculation_basis = BeamCalculationBasisV1(
        d_dash_mm=basis.d_dash_mm,
        asv_mm2=basis.detailing.asv_mm2,
        pt_percent=basis.pt_percent,
        ast_mm2_for_shear=basis.ast_mm2_for_shear,
    )
    canonical = BeamDesignInputV1(
        identity=MemberIdentityV1(
            member_id=geometry.frame_name,
            story=geometry.story,
            case_id=provenance.selection_id,
        ),
        section=section,
        materials=basis.materials,
        actions=BeamActionsV1(
            mu_knm=abs(action.m3_knm),
            vu_kn=abs(action.v2_kn),
            tu_knm=abs(action.t_knm),
            primary_tension_face=(
                tension_face if tension_face != "ZERO_MOMENT" else None
            ),
        ),
        calculation_basis=calculation_basis,
        detailing=basis.detailing,
        serviceability=None,
        source_provenance=f"beam-audit-compat:{action.row_sha256}",
    )
    serviceability = EvidenceValueV1[str](
        state=EvidenceStateV1.NOT_REQUESTED,
        value=None,
        reason_code="ETABS_PILOT_SERVICEABILITY_NOT_REQUESTED",
        message="Legacy pilot compatibility is bounded to strength.",
        source_references=provenance.source_references,
    )
    row = audit.BeamAuditRowInputV1(
        action=action,
        canonical_request=canonical,
        tension_face=tension_face,
        demand_governing_reference_ids=(action.row_id,),
        basis_source_references=provenance.source_references,
        assumptions=(
            provenance.factored_action_basis,
            "Same-row actions are retained; independent extrema are references only.",
        ),
        serviceability_basis=serviceability,
    )
    context_payload = {
        "provenance": provenance.model_dump(mode="json"),
        "geometry": geometry.model_dump(mode="json"),
        "action_row_sha256": action.row_sha256,
    }
    context_sha256 = hashlib.sha256(
        json.dumps(
            context_payload,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()
    evaluation = audit.evaluate_beam_audit_row_v1(
        audit.BeamAuditRowEvaluationRequestV1(
            row=row,
            scenario_id=provenance.scenario_id,
            context_sha256=context_sha256,
            require_serviceability=False,
        )
    )
    if evaluation.row is None:
        return {
            "compatibility_status": "HELD",
            "delegated_to": "evaluate_beam_audit_row_v1",
            "tension_face": tension_face,
            "action_row_sha256": action.row_sha256,
            "audit_evaluation": evaluation.model_dump(mode="json"),
            "issues": [issue.model_dump(mode="json") for issue in evaluation.issues],
            "limitations": list(evaluation.limitations),
        }
    return {
        "compatibility_status": "DELEGATED",
        "delegated_to": "evaluate_beam_audit_row_v1",
        "tension_face": tension_face,
        "action_row_sha256": action.row_sha256,
        "same_row_actions": {
            "p_kn": action.p_kn,
            "v2_kn": action.v2_kn,
            "v3_kn": action.v3_kn,
            "t_knm": action.t_knm,
            "m2_knm": action.m2_knm,
            "m3_knm": action.m3_knm,
        },
        "audit_evaluation": evaluation.model_dump(mode="json"),
        "canonical_result": json.loads(evaluation.row.canonical_result_json),
        "limitations": list(evaluation.limitations),
    }


def run_etabs_beam_pilot_v1(
    request: ETABSPilotRequestV1,
    *,
    session_factory: SessionFactory = _default_session_factory,
) -> ETABSPilotResultV1:
    """Extract and design the first bounded set of deterministic beam candidates."""

    with etabs_com_operation_v1():
        with session_factory() as session:
            model = _model_identity(session.sap_model)
            with session.normalized_kn_mm_units():
                inventory = _frame_inventory(session.sap_model)
                _select_results(session.sap_model, request.result_selection)
                results: list[ETABSPilotBeamResultV1] = []
                for frame in inventory[: request.limit]:
                    geometry = _rectangular_geometry(session.sap_model, frame)
                    forces = _frame_forces(
                        session.sap_model,
                        geometry.frame_name,
                        request.result_selection,
                    )
                    results.append(
                        ETABSPilotBeamResultV1(
                            geometry=geometry,
                            forces=forces,
                            design_result=_design_beam(
                                geometry, forces, request.design_basis
                            ),
                        )
                    )
    library_version, content_identity = _library_identity()
    delegated_count = sum(
        item.design_result.get("compatibility_status") == "DELEGATED"
        for item in results
    )
    held_count = len(results) - delegated_count
    return ETABSPilotResultV1(
        pilot_status="HELD" if held_count else "COMPLETED",
        model=model,
        result_selection=request.result_selection,
        units={
            "length": "mm",
            "force": "kN",
            "moment": "kN.m",
            "stress": "N/mm2",
        },
        candidate_beam_count=len(inventory),
        designed_beam_count=delegated_count,
        held_beam_count=held_count,
        beams=tuple(results),
        library_version=library_version,
        library_content_identity=content_identity,
        limitations=(
            "Legacy live transport is deprecated and remains disabled pending A1 acceptance.",
            "Only frame objects horizontal within 1 mm and using rectangular sections are supported.",
            "The signed governing M3 row retains its concurrent P, V2, V3, T and M2 values; independent extrema are references only.",
            "Calculation ownership is delegated to the canonical beam-audit row evaluator.",
            "Materials and reinforcement/detailing choices are explicit caller inputs, not inferred from ETABS material names.",
            "Serviceability, adjacent-member continuity, joint congestion, constructability optimization, and whole-building iteration are not evaluated.",
            "Every result requires qualified structural-engineer review.",
        ),
    )
