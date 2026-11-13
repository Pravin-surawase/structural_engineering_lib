"""Compose IS 456 section and anchorage checks for supplied beam stations."""

from __future__ import annotations

import hashlib
import html
import json
import math
from dataclasses import asdict, dataclass
from typing import Any, Generic, Literal, TypeVar, overload

from structural_lib.beam.detailing import (
    AnchorageCheckRequest,
    AnchorageDirection,
    AnchorageLocation,
    AnchoragePath,
    BarSurface,
    DevelopmentLengthRequest,
    SimpleSupportAnchorageEvidence,
    StressState,
    check_anchorage,
)
from structural_lib.beam.flexure import (
    FlexuralCapacityRequest,
    SectionKind,
    flexural_capacity,
)
from structural_lib.beam.reinforcement import (
    BarPosition,
    Face,
    ReinforcementGeometryRequest,
    evaluate_geometry,
)
from structural_lib.beam.section_shear import (
    SectionShearReinforcement,
    SuppliedSectionShearRequest,
    supplied_section_shear_capacity,
)
from structural_lib.beam.semantics import EngineeringState, OperationResult
from structural_lib.codes.is456.beam.flexure import calculate_effective_flange_width
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
from structural_lib.services.contracts.beam_continuous import (
    BeamCantileverCheckRequestV1,
    BeamContinuousActionV1,
    BeamContinuousCheckRequestV1,
    BeamContinuousStationV1,
    BeamSectionBarV1,
    BeamSectionCheckRequestV1,
    _BeamStationCheckRequest,
)

_COMMON_LIMITATIONS = (
    "Checks only the declared supplied action rows on a prismatic rectangular beam.",
    "Service deflection, cracking, stability and completeness of the source analysis require separate evidence.",
    "Straight anchorage only. Curtailment, lap splices, seismic detailing and fabrication schedules are outside this check.",
)
_CONTINUOUS_LIMITATIONS = (
    _COMMON_LIMITATIONS[0],
    "Support centrelines are diagnostic. Physical support faces and span stations govern.",
    *_COMMON_LIMITATIONS[1:],
)
_CANTILEVER_LIMITATIONS = (
    *_COMMON_LIMITATIONS,
    "The fixed face and both supplied sides of an interior point-load station are physical checks.",
    "The free end has zero moment and shear in the supported profile.",
)
_SECTION_LIMITATIONS = (
    "Checks signed actions at one supplied physical section. Bar coordinates are relative to the web.",
    "Monolithic T and L flanges participate in compression under sagging only. Shear uses the web width.",
    "The report preserves each bar and layer. Member-wide continuity, anchorage, fabrication and serviceability require separate checks.",
)
_Check = Literal["PASS", "FAIL", "HOLD"]
_Request = TypeVar("_Request", bound=_BeamStationCheckRequest)


@dataclass(frozen=True)
class BeamContinuousRowResultV1:
    """Trace one simultaneous supplied action row to its local checks."""

    action: BeamContinuousActionV1
    station: BeamContinuousStationV1
    kind: str
    diagnostic_only: bool
    tension_face: Face | None = None
    shear_face: Face | None = None
    flexure_utilization: float | None = None
    shear_utilization: float | None = None
    section_status: _Check | None = None
    anchorage: OperationResult | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe row with component and provenance identities."""
        return {
            **asdict(self),
            "action": self.action.model_dump(mode="json"),
            "station": self.station.model_dump(mode="json"),
            "anchorage": self.anchorage.to_dict() if self.anchorage else None,
        }


@dataclass(frozen=True)
class _BeamStationCheckResult(Generic[_Request]):
    """Revision-bound checks and a declared-coverage disposition."""

    request: _Request
    ultimate_status: _Check
    serviceability_status: Literal["HOLD", "NOT_EVALUATED"]
    rows: tuple[BeamContinuousRowResultV1, ...]
    geometry: OperationResult | None
    flexural_sections: dict[Face, OperationResult]
    shear_sections: dict[Face, OperationResult]
    governing_rows: dict[str, str]
    result_envelope: StructuralResultEnvelopeV2

    @property
    def _profile(self) -> str:
        if isinstance(self.request, BeamSectionCheckRequestV1):
            return "section"
        return (
            "cantilever"
            if isinstance(self.request, BeamCantileverCheckRequestV1)
            else "continuous"
        )

    @property
    def _limitations(self) -> tuple[str, ...]:
        if self._profile == "section":
            return _SECTION_LIMITATIONS
        return (
            _CANTILEVER_LIMITATIONS
            if self._profile == "cantilever"
            else _CONTINUOUS_LIMITATIONS
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize numeric checks, exact rows and the shared result envelope."""
        return {
            "schema_version": self.request.schema_version.replace(
                "-check/", "-result/"
            ),
            "request": self.request.model_dump(mode="json"),
            "ultimate_status": self.ultimate_status,
            "serviceability_status": self.serviceability_status,
            "rows": [row.to_dict() for row in self.rows],
            "geometry": self.geometry.to_dict() if self.geometry else None,
            "flexural_sections": {
                face.value: result.to_dict()
                for face, result in self.flexural_sections.items()
            },
            "shear_sections": {
                face.value: result.to_dict()
                for face, result in self.shear_sections.items()
            },
            "governing_rows": self.governing_rows,
            "result_envelope": self.result_envelope.to_dict(),
            "limitations": list(self._limitations),
        }


@dataclass(frozen=True)
class BeamContinuousCheckResultV1(
    _BeamStationCheckResult[BeamContinuousCheckRequestV1]
):
    """Revision-bound result for a supplied two-span rectangular beam."""


@dataclass(frozen=True)
class BeamCantileverCheckResultV1(
    _BeamStationCheckResult[BeamCantileverCheckRequestV1]
):
    """Revision-bound result for a supplied rectangular cantilever."""


@dataclass(frozen=True)
class BeamSectionCheckResultV1(_BeamStationCheckResult[BeamSectionCheckRequestV1]):
    """Revision-bound signed checks for an actual physical beam section."""

    @property
    def effective_flange_width_mm(self) -> float | None:
        """Return the flange width used in the section check, if evaluated."""
        sagging = self.flexural_sections.get(Face.BOTTOM)
        if sagging is None:
            return None
        value = sagging.effective_inputs["flange_width_mm"]["value"]
        return float(value) if value is not None else None

    def to_dict(self) -> dict[str, Any]:
        return {
            **super().to_dict(),
            "effective_flange_width_mm": self.effective_flange_width_mm,
        }


@dataclass(frozen=True)
class _SupportFace:
    support_id: str
    support_centre_mm: float
    direction: AnchorageDirection
    location: AnchorageLocation


def _support_faces(request: BeamContinuousCheckRequestV1) -> dict[float, _SupportFace]:
    left, middle, right = request.supports
    simple, continuous = (
        AnchorageLocation.SIMPLE_SUPPORT,
        AnchorageLocation.CONTINUOUS_SUPPORT,
    )
    decreasing, increasing = (
        AnchorageDirection.DECREASING_X,
        AnchorageDirection.INCREASING_X,
    )
    return {
        left.right_face_mm: _SupportFace(
            left.support_id, left.centre_mm, decreasing, simple
        ),
        middle.left_face_mm: _SupportFace(
            middle.support_id, middle.centre_mm, increasing, continuous
        ),
        middle.right_face_mm: _SupportFace(
            middle.support_id, middle.centre_mm, decreasing, continuous
        ),
        right.left_face_mm: _SupportFace(
            right.support_id, right.centre_mm, increasing, simple
        ),
    }


def _input_hash(request: _BeamStationCheckRequest) -> str:
    payload = request.model_dump(mode="json")
    for key, identifier in (
        ("bars", "bar_id"),
        ("stations", "station_id"),
        ("combinations", "combination_id"),
        ("actions", "row_id"),
    ):
        payload[key].sort(key=lambda item: item[identifier])
    for combination in payload["combinations"]:
        combination["required_station_ids"].sort()
    serialized = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    return hashlib.sha256(serialized.encode()).hexdigest()


def _coverage_issues(
    request: (
        BeamContinuousCheckRequestV1
        | BeamCantileverCheckRequestV1
        | BeamSectionCheckRequestV1
    ),
    stations: dict[str, BeamContinuousStationV1],
) -> tuple[list[StructuralIssueV1], list[StructuralIssueV1]]:
    ultimate: list[StructuralIssueV1] = []
    service: list[StructuralIssueV1] = []
    received = {
        (action.combination_id, action.station_id): action for action in request.actions
    }
    continuous = isinstance(request, BeamContinuousCheckRequestV1)
    section = isinstance(request, BeamSectionCheckRequestV1)
    if isinstance(request, BeamContinuousCheckRequestV1):
        left, middle, right = request.supports
        bounds = (left.centre_mm, right.centre_mm)
        required_positions = {
            (position, "CONTINUOUS") for position in _support_faces(request)
        }
        required_positions.update(
            {
                (left.centre_mm, "RIGHT"),
                (middle.centre_mm, "LEFT"),
                (middle.centre_mm, "RIGHT"),
                (right.centre_mm, "LEFT"),
            }
        )
    elif isinstance(request, BeamCantileverCheckRequestV1):
        bounds = (0.0, request.free_end_mm)
        required_positions = {(position, "CONTINUOUS") for position in bounds}
    else:
        bounds = (0.0, 0.0)
        required_positions = set()
    complete_spans = False
    for combination in sorted(
        request.combinations, key=lambda item: item.combination_id
    ):
        cid = combination.combination_id
        is_ultimate = combination.kind == "ULS"
        issues = ultimate if is_ultimate else service
        needed = combination.required_station_ids
        for station_id in sorted(needed):
            if (cid, station_id) not in received:
                issues.append(
                    StructuralIssueV1(
                        "BEAM_ACTION_MISSING",
                        f"combinations.{cid}.{station_id}",
                        "A declared concurrent action row was not supplied.",
                    )
                )
        if not is_ultimate:
            continue
        if section:
            complete_spans = True
            continue
        keys = {(stations[item].x_mm, stations[item].side) for item in needed}
        if isinstance(request, BeamContinuousCheckRequestV1):
            left, middle, right = request.supports
            left_span = any(
                left.right_face_mm < x < middle.left_face_mm for x, _ in keys
            )
            right_span = any(
                middle.right_face_mm < x < right.left_face_mm for x, _ in keys
            )
            complete_spans |= left_span and right_span and required_positions <= keys
        else:
            full_span = required_positions <= keys and any(
                bounds[0] < x < bounds[1] for x, _ in keys
            )
            complete_spans |= full_span
            if not full_span:
                ultimate.append(
                    StructuralIssueV1(
                        "BEAM_MEMBER_COVERAGE_MISSING",
                        f"combinations.{cid}",
                        "Declare the fixed face, an interior station and the free end in each ULS combination.",
                    )
                )
        discontinuities = {
            x
            for x, side in (
                keys if continuous else {(s.x_mm, s.side) for s in stations.values()}
            )
            if side != "CONTINUOUS" and bounds[0] < x < bounds[1]
        }
        if any(not {(x, "LEFT"), (x, "RIGHT")} <= keys for x in discontinuities):
            ultimate.append(
                StructuralIssueV1(
                    "BEAM_STATION_SIDE_MISSING",
                    f"combinations.{cid}",
                    "Declare both sides of each shear discontinuity in the combination.",
                )
            )
    if not complete_spans:
        ultimate.append(
            StructuralIssueV1(
                "BEAM_MEMBER_COVERAGE_MISSING",
                "combinations",
                (
                    "Declare a ULS combination with both spans, all support faces and the required centreline sides."
                    if continuous
                    else (
                        "Declare a ULS combination covering the supplied section."
                        if section
                        else "Declare a ULS combination covering the cantilever."
                    )
                ),
            )
        )
    return ultimate, service


def _centreline_issues(
    request: BeamContinuousCheckRequestV1,
    rows: tuple[BeamContinuousRowResultV1, ...],
) -> list[StructuralIssueV1]:
    left, middle, right = request.supports
    interior: dict[str, float] = {}
    issues = []
    for row in rows:
        if row.kind != "ULS" or not row.diagnostic_only:
            continue
        action = row.action
        path = f"actions.{action.row_id}"
        if row.station.x_mm in (left.centre_mm, right.centre_mm):
            if not math.isclose(action.mu_knm, 0, abs_tol=1e-6):
                issues.append(
                    StructuralIssueV1(
                        "BEAM_OUTER_RESTRAINT_HELD",
                        path,
                        "The outer support must have zero supplied centreline moment for this simple-support profile.",
                    )
                )
        elif row.station.x_mm == middle.centre_mm:
            first = interior.setdefault(action.combination_id, action.mu_knm)
            if not math.isclose(first, action.mu_knm, abs_tol=1e-6):
                issues.append(
                    StructuralIssueV1(
                        "BEAM_CENTRELINE_MOMENT_JUMP_HELD",
                        path,
                        "A moment jump at the internal centreline requires separate support action evidence.",
                    )
                )
    return issues


def _sections(
    request: _BeamStationCheckRequest, bars: tuple[BarPosition, ...]
) -> tuple[OperationResult, dict[Face, OperationResult], dict[Face, OperationResult]]:
    flange = request.flange if isinstance(request, BeamSectionCheckRequestV1) else None
    flange_width = (
        calculate_effective_flange_width(
            bw_mm=request.width_mm,
            span_mm=flange.zero_moment_distance_mm,
            df_mm=flange.thickness_mm,
            flange_overhang_left_mm=flange.left_overhang_mm,
            flange_overhang_right_mm=flange.right_overhang_mm,
            beam_type=flange.kind,
        )
        if flange
        else None
    )
    geometry = evaluate_geometry(
        ReinforcementGeometryRequest(
            request.schema_version,
            request.width_mm,
            request.depth_mm,
            request.clear_cover_mm,
            request.link_diameter_mm,
            max(max(bar.diameter_mm for bar in bars), request.aggregate_size_mm + 5),
            bars,
        )
    )
    flexure = {
        face: flexural_capacity(
            FlexuralCapacityRequest(
                request.schema_version,
                SectionKind(flange.kind) if flange else SectionKind.RECTANGULAR,
                request.width_mm,
                request.depth_mm,
                request.fck_nmm2,
                request.fy_nmm2,
                bars,
                face,
                flange_width_mm=flange_width,
                flange_thickness_mm=flange.thickness_mm if flange else None,
            )
        )
        for face in Face
    }
    links = SectionShearReinforcement(
        "vertical-link-legs",
        2 * math.pi * request.link_diameter_mm**2 / 4,
        request.link_fy_nmm2,
        90,
        request.link_spacing_mm,
    )
    shear = {
        face: supplied_section_shear_capacity(
            SuppliedSectionShearRequest(
                request.schema_version,
                request.width_mm,
                float(result.outputs["effective_depth_mm"]),
                request.fck_nmm2,
                float(result.outputs["tension_steel_area_mm2"]),
                links,
            )
        )
        for face, result in flexure.items()
        if "effective_depth_mm" in result.outputs
    }
    return geometry, flexure, shear


def _flexure_provision_ok(result: OperationResult) -> bool:
    values = result.outputs
    tension = float(values["tension_steel_area_mm2"])
    compression = float(values["compression_steel_area_mm2"])
    return (
        result.engineering == EngineeringState.PASS
        and float(values["minimum_tension_steel_area_mm2"]) - 1e-9
        <= tension
        <= float(values["maximum_tension_steel_area_mm2"]) + 1e-9
        and compression <= float(values["maximum_compression_steel_area_mm2"]) + 1e-9
    )


def _anchor(
    request: _BeamStationCheckRequest,
    bars: tuple[BarPosition, ...],
    row: BeamContinuousActionV1,
    station: BeamContinuousStationV1,
    support_face: _SupportFace,
    face: Face,
    moment_capacity_knm: float,
) -> OperationResult | None:
    extent = request.straight_bars
    if extent is None:
        return None
    simple = support_face.location == AnchorageLocation.SIMPLE_SUPPORT
    if simple and (face != Face.BOTTOM or row.vu_kn == 0):
        return None
    evidence = (
        SimpleSupportAnchorageEvidence(
            moment_capacity_knm * 1e6, abs(row.vu_kn) * 1000, (row.row_id,)
        )
        if simple
        else None
    )
    paths = tuple(
        AnchoragePath(
            bar.bar_id,
            station.station_id,
            support_face.location,
            support_face.direction,
            extent.start_mm,
            extent.end_mm,
            station.x_mm,
            support_face.support_id,
            station.x_mm,
            support_face.support_centre_mm,
            (),
            None,
            DevelopmentLengthRequest(
                request.schema_version,
                bar.diameter_mm,
                0.87 * request.fy_nmm2,
                request.fy_nmm2,
                request.fck_nmm2,
                BarSurface.DEFORMED,
                StressState.TENSION,
            ),
            evidence,
        )
        for bar in bars
        if bar.face == face
    )
    return check_anchorage(
        AnchorageCheckRequest(
            request.schema_version,
            request.member_id,
            request.reinforcement_revision,
            paths,
        )
    )


def _check_row(
    request: _BeamStationCheckRequest,
    bars: tuple[BarPosition, ...],
    action: BeamContinuousActionV1,
    station: BeamContinuousStationV1,
    kind: str,
    diagnostic: bool,
    support_face: _SupportFace | None,
    flexure: dict[Face, OperationResult],
    shear: dict[Face, OperationResult],
) -> BeamContinuousRowResultV1:
    if kind != "ULS" or not flexure:
        return BeamContinuousRowResultV1(action, station, kind, diagnostic)
    if action.tu_knm != 0 or len(shear) != len(Face):
        return BeamContinuousRowResultV1(
            action, station, kind, diagnostic, section_status="HOLD"
        )
    face = Face.TOP if action.mu_knm < 0 else Face.BOTTOM
    shear_face = (
        face
        if action.mu_knm
        else min(
            shear, key=lambda item: float(shear[item].outputs["provided_capacity_kn"])
        )
    )
    m_cap = float(flexure[face].outputs["capacity_knm"])
    v_cap = float(shear[shear_face].outputs["provided_capacity_kn"])
    m_util = abs(action.mu_knm) / m_cap if m_cap > 0 else None
    v_util = abs(action.vu_kn) / v_cap if v_cap > 0 else None
    passed = (
        _flexure_provision_ok(flexure[face])
        and shear[shear_face].engineering == EngineeringState.PASS
        and m_util is not None
        and m_util <= 1 + 1e-12
        and v_util is not None
        and v_util <= 1 + 1e-12
    )
    anchor = (
        _anchor(request, bars, action, station, support_face, face, m_cap)
        if support_face is not None and m_cap > 0
        else None
    )
    return BeamContinuousRowResultV1(
        action,
        station,
        kind,
        diagnostic,
        face if action.mu_knm else None,
        shear_face,
        m_util,
        v_util,
        "PASS" if passed else "FAIL",
        anchor,
    )


def _row_issues(
    rows: tuple[BeamContinuousRowResultV1, ...], faces: dict[float, _SupportFace]
) -> tuple[list[StructuralIssueV1], list[StructuralIssueV1]]:
    failed, held = [], []
    for row in rows:
        path = f"actions.{row.action.row_id}"
        if row.kind != "ULS":
            continue
        if row.section_status == "HOLD":
            held.append(
                StructuralIssueV1(
                    "BEAM_ACTION_SCOPE_HELD",
                    path,
                    "The supplied action or section is outside this profile.",
                )
            )
        if row.diagnostic_only:
            continue
        if row.section_status == "FAIL":
            failed.append(
                StructuralIssueV1(
                    "BEAM_SECTION_FAIL",
                    path,
                    "The supplied section does not satisfy strength or reinforcement provision.",
                )
            )
        if row.station.x_mm not in faces:
            continue
        if row.anchorage is None or row.anchorage.engineering not in (
            EngineeringState.PASS,
            EngineeringState.FAIL,
        ):
            held.append(
                StructuralIssueV1(
                    "BEAM_ANCHORAGE_HELD",
                    path,
                    "A checked straight support anchorage path is required.",
                )
            )
        elif row.anchorage.engineering == EngineeringState.FAIL:
            failed.append(
                StructuralIssueV1(
                    "BEAM_ANCHORAGE_FAIL",
                    path,
                    "The straight support anchorage is shorter than the applicable requirement.",
                )
            )
    return failed, held


def _governing_rows(rows: tuple[BeamContinuousRowResultV1, ...]) -> dict[str, str]:
    candidates = [row for row in rows if row.kind == "ULS" and not row.diagnostic_only]
    checks = {
        "sagging": [
            (row.flexure_utilization, row.action.row_id)
            for row in candidates
            if row.tension_face == Face.BOTTOM and row.flexure_utilization is not None
        ],
        "hogging": [
            (row.flexure_utilization, row.action.row_id)
            for row in candidates
            if row.tension_face == Face.TOP and row.flexure_utilization is not None
        ],
        "shear": [
            (row.shear_utilization, row.action.row_id)
            for row in candidates
            if row.shear_utilization is not None
        ],
    }
    return {
        key: min(items, key=lambda item: (-item[0], item[1]))[1]
        for key, items in checks.items()
        if items
    }


def check_continuous_beam(
    request: BeamContinuousCheckRequestV1,
) -> BeamContinuousCheckResultV1:
    """Check a validated two-span request with exact supplied rows and physical bars."""
    if not isinstance(request, BeamContinuousCheckRequestV1):
        raise TypeError("request must be BeamContinuousCheckRequestV1")
    return _check_station_beam(request)


def check_cantilever_beam(
    request: BeamCantileverCheckRequestV1,
) -> BeamCantileverCheckResultV1:
    """Check a validated cantilever at supplied physical stations."""
    if not isinstance(request, BeamCantileverCheckRequestV1):
        raise TypeError("request must be BeamCantileverCheckRequestV1")
    return _check_station_beam(request)


def check_section_beam(request: BeamSectionCheckRequestV1) -> BeamSectionCheckResultV1:
    """Check a validated physical section against signed supplied actions."""
    if not isinstance(request, BeamSectionCheckRequestV1):
        raise TypeError("request must be BeamSectionCheckRequestV1")
    return _check_station_beam(request)


@overload
def _check_station_beam(
    request: BeamContinuousCheckRequestV1,
) -> BeamContinuousCheckResultV1: ...


@overload
def _check_station_beam(
    request: BeamCantileverCheckRequestV1,
) -> BeamCantileverCheckResultV1: ...


@overload
def _check_station_beam(
    request: BeamSectionCheckRequestV1,
) -> BeamSectionCheckResultV1: ...


def _check_station_beam(
    request: (
        BeamContinuousCheckRequestV1
        | BeamCantileverCheckRequestV1
        | BeamSectionCheckRequestV1
    ),
) -> (
    BeamContinuousCheckResultV1 | BeamCantileverCheckResultV1 | BeamSectionCheckResultV1
):
    stale = request.analysis_revision != request.current_analysis_revision
    bars = tuple(
        BarPosition(
            bar.bar_id,
            bar.diameter_mm,
            bar.x_from_left_mm,
            bar.y_from_top_mm,
            Face(bar.face),
            bar.layer if isinstance(bar, BeamSectionBarV1) else 1,
        )
        for bar in sorted(request.bars, key=lambda bar: bar.bar_id)
    )
    geometry, flexure, shear = (None, {}, {}) if stale else _sections(request, bars)
    stations = {station.station_id: station for station in request.stations}
    kinds = {item.combination_id: item.kind for item in request.combinations}
    centreline: set[float] = set()
    faces: dict[float, _SupportFace] = {}
    if isinstance(request, BeamContinuousCheckRequestV1):
        centreline = {support.centre_mm for support in request.supports}
        faces = _support_faces(request)
    elif isinstance(request, BeamCantileverCheckRequestV1):
        faces = {
            0.0: _SupportFace(
                request.fixed_support_id,
                -request.fixed_support_width_mm / 2,
                AnchorageDirection.DECREASING_X,
                AnchorageLocation.DIRECT_SUPPORT,
            )
        }
    rows = tuple(
        _check_row(
            request,
            bars,
            action,
            stations[action.station_id],
            kinds[action.combination_id],
            stations[action.station_id].x_mm in centreline,
            faces.get(stations[action.station_id].x_mm),
            flexure,
            shear,
        )
        for action in sorted(
            request.actions,
            key=lambda item: (
                item.combination_id,
                stations[item.station_id].x_mm,
                stations[item.station_id].side,
                item.row_id,
            ),
        )
    )
    held, service = _coverage_issues(request, stations)
    if isinstance(request, BeamContinuousCheckRequestV1):
        held.extend(_centreline_issues(request, rows))
    elif isinstance(request, BeamCantileverCheckRequestV1):
        for row in rows:
            if row.station.x_mm == request.free_end_mm and (
                abs(row.action.mu_knm) > 1e-6 or abs(row.action.vu_kn) > 1e-6
            ):
                issues = held if row.kind == "ULS" else service
                issues.append(
                    StructuralIssueV1(
                        "BEAM_FREE_END_ACTION_HELD",
                        f"actions.{row.action.row_id}",
                        "The supported free end requires zero moment and shear.",
                    )
                )
    failed, row_held = _row_issues(rows, faces) if not stale else ([], [])
    if stale:
        held.append(
            StructuralIssueV1(
                "BEAM_ANALYSIS_STALE",
                "analysis_revision",
                "Supply actions from the current analysis revision.",
            )
        )
    if geometry is not None and geometry.engineering != EngineeringState.PASS:
        failed.extend(
            StructuralIssueV1(item.code, item.field_or_location or "bars", item.message)
            for item in geometry.diagnostics
        )
    if "SLS" in kinds.values() and "SUSTAINED_SLS" not in kinds.values():
        service.append(
            StructuralIssueV1(
                "BEAM_SUSTAINED_BASIS_MISSING",
                "combinations",
                "Long-term serviceability requires an explicitly declared sustained combination.",
            )
        )
    if any(kind in ("SLS", "SUSTAINED_SLS") for kind in kinds.values()):
        service.append(
            StructuralIssueV1(
                "BEAM_SERVICEABILITY_NOT_EVALUATED",
                "combinations",
                "Service rows are retained. Deflection and cracking require a separate check.",
            )
        )
    ultimate_status: _Check = (
        "FAIL" if failed else "HOLD" if held or row_held else "PASS"
    )
    envelope = StructuralResultEnvelopeV2(
        intake_status=(
            IntakeStatus.PARTIAL
            if ultimate_status == "HOLD" and not stale
            else IntakeStatus.VALID
        ),
        calculation_status=(
            CalculationStatus.NOT_EVALUATED if stale else CalculationStatus.COMPLETED
        ),
        engineering_status=EngineeringStatus(ultimate_status),
        freshness_status=FreshnessStatus.STALE if stale else FreshnessStatus.CURRENT,
        issues=tuple(failed + held + row_held + service),
        result_identity=ResultIdentityV1(
            request.schema_version,
            get_runtime_version(),
            _input_hash(request),
            request.schema_version.replace("-check/", "-supplied-stations/"),
        ),
    )
    serviceability_status: Literal["HOLD", "NOT_EVALUATED"] = (
        "HOLD" if service else "NOT_EVALUATED"
    )
    fields = (
        ultimate_status,
        serviceability_status,
        rows,
        geometry,
        flexure,
        shear,
        _governing_rows(rows),
        envelope,
    )
    if isinstance(request, BeamContinuousCheckRequestV1):
        return BeamContinuousCheckResultV1(request, *fields)
    if isinstance(request, BeamCantileverCheckRequestV1):
        return BeamCantileverCheckResultV1(request, *fields)
    return BeamSectionCheckResultV1(request, *fields)


def render_station_beam_html(
    result: (
        BeamContinuousCheckResultV1
        | BeamCantileverCheckResultV1
        | BeamSectionCheckResultV1
    ),
) -> str:
    """Render the bound result without performing another design."""

    def number(value: float | None) -> str:
        return "—" if value is None else f"{value:.3f}"

    rows = []
    for item in result.rows:
        action, station = item.action, item.station
        anchor = item.anchorage
        anchor_check = (
            max(
                anchor.outputs.get("checks", ()),
                key=lambda check: (not check["passed"], check["utilization"] or 0),
                default=None,
            )
            if anchor
            else None
        )
        anchor_text = (
            f"{anchor.engineering.value.upper()}, "
            f"{number(anchor_check['required_development_length_mm'])} / "
            f"{number(anchor_check['available_for_criterion_mm'])}"
            if anchor and anchor_check
            else "—"
        )
        cells = (
            action.row_id,
            action.combination_id,
            item.kind,
            station.station_id,
            number(station.x_mm),
            station.side,
            "Diagnostic" if item.diagnostic_only else "Physical",
            number(action.mu_knm),
            number(action.vu_kn),
            number(action.tu_knm),
            item.tension_face.value if item.tension_face else "—",
            item.shear_face.value if item.shear_face else "—",
            number(item.flexure_utilization),
            number(item.shear_utilization),
            item.section_status or "—",
            anchor_text,
        )
        rows.append(
            "<tr>"
            + "".join(f"<td>{html.escape(cell)}</td>" for cell in cells)
            + "</tr>"
        )
    sections = "".join(
        f"<li>{face.value.title()} tension: "
        f"d = {number(float(section.outputs['effective_depth_mm']))} mm, "
        f"xᵤ = {number(float(section.outputs['equilibrium_neutral_axis_depth_mm']))} mm, "
        f"provided tension steel = {number(float(section.outputs['tension_steel_area_mm2']))} mm², "
        f"M resistance = {number(float(section.outputs['capacity_knm']))} kN·m, "
        f"V resistance = {number(float(result.shear_sections[face].outputs['provided_capacity_kn']))} kN.</li>"
        for face, section in result.flexural_sections.items()
        if face in result.shear_sections
    )
    issues = "".join(
        f"<li>{html.escape(issue.code)} · {html.escape(issue.path)} · {html.escape(issue.message)}</li>"
        for issue in result.result_envelope.issues
    )
    governing = "".join(
        f"<li>{check.title()} · {html.escape(row_id)}</li>"
        for check, row_id in result.governing_rows.items()
    )
    limits = "".join(f"<li>{html.escape(limit)}</li>" for limit in result._limitations)
    identity = result.result_envelope.result_identity
    request = result.request
    label = f"{result._profile.title()} beam {html.escape(request.member_id)}"
    geometry_detail = ""
    if isinstance(result, BeamSectionCheckResultV1):
        label = f"Beam section {html.escape(request.member_id)}"
        flange = result.request.flange
        if flange is not None:
            geometry_detail = (
                f"<p>{html.escape(flange.kind)} · "
                f"left/right overhangs {number(flange.left_overhang_mm)} / "
                f"{number(flange.right_overhang_mm)} mm · "
                f"effective flange width {number(result.effective_flange_width_mm)} mm</p>"
            )
        geometry_detail += (
            "<h2>Longitudinal bars</h2><ul>"
            + "".join(
                f"<li>{html.escape(bar.bar_id)} · {bar.face} · layer {bar.layer} · "
                f"Ø{number(bar.diameter_mm)} at ({number(bar.x_from_left_mm)}, "
                f"{number(bar.y_from_top_mm)}) mm</li>"
                for bar in sorted(result.request.bars, key=lambda bar: bar.bar_id)
            )
            + "</ul>"
        )
    return f"""<!doctype html>
<html lang="en"><meta charset="utf-8">
<title>{label}</title>
<style>body{{font:16px system-ui;margin:2rem}}table{{border-collapse:collapse}}
th,td{{border:1px solid #aaa;padding:.35rem;text-align:left}}</style>
<h1>{label}</h1>
<p>Supplied ultimate checks <strong>{result.ultimate_status}</strong> · Serviceability
<strong>{result.serviceability_status}</strong> · Qualified review required</p>
<p>Analysis revision {html.escape(request.analysis_revision)} · Current revision
{html.escape(request.current_analysis_revision)} · Reinforcement revision
{html.escape(request.reinforcement_revision)}</p>
<p>Source {html.escape(request.source_reference)} · Input identity <code>{identity.input_hash if identity else ""}</code></p>
{geometry_detail}
<h2>Section resistance</h2><ul>{sections}</ul>
<h2>Governing physical rows</h2><ul>{governing}</ul>
<h2>Concurrent supplied actions</h2>
<table><thead><tr><th>Row</th><th>Combination</th><th>Kind</th><th>Station</th><th>x (mm)</th>
<th>Side</th><th>Role</th><th>M (kN·m)</th><th>V (kN)</th><th>T (kN·m)</th>
<th>Tension face</th><th>Shear face</th><th>Flexure ratio</th><th>Shear ratio</th>
<th>Section</th><th>Anchorage required / available (mm)</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<h2>Issues and held checks</h2><ul>{issues}</ul>
<h2>Scope</h2><ul>{limits}</ul></html>"""


def render_continuous_beam_html(result: BeamContinuousCheckResultV1) -> str:
    """Render a two-span result without recalculation."""
    return render_station_beam_html(result)
