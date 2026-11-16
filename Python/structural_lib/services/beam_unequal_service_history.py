"""Unequal continuous spans with current signed service loads and finite ages."""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import pairwise
from typing import TYPE_CHECKING, Any

from structural_lib.beam.reinforcement import BarPosition, Face
from structural_lib.beam.semantics import (
    EngineeringState,
    ExecutionState,
    OperationResult,
)
from structural_lib.beam.serviceability import (
    DeflectionCriterion,
    DeflectionLimitRequest,
    deflection_limit,
)
from structural_lib.codes.is456.beam.serviceability import calculate_cracking_moment
from structural_lib.codes.is456.beam.torsion_serviceability import (
    cracked_service_section,
)
from structural_lib.core.result_contract import StructuralIssueV1
from structural_lib.services.beam_instantaneous_service import (
    _analyze_line,
    _face_crack,
    _service_bars,
    _service_domain,
    _service_geometry,
)
from structural_lib.services.contracts.beam_continuous import (
    BeamContinuousActionV1,
    BeamContinuousCheckRequestV1,
    BeamContinuousStationV1,
)

if TYPE_CHECKING:
    from structural_lib.services.beam_service_history import BeamServiceHistoryInputV1

_POSITION_TOLERANCE_MM = 1e-6
_ES = 200000.0
_ACTIONS = dict[tuple[str, str], BeamContinuousActionV1]


@dataclass(frozen=True)
class _SpanField:
    """Recover the constant-EI UDL field from the line solver's left station."""

    span_id: str
    start: float
    end: float
    ei: float
    load: float
    moment0: float
    shear0: float
    rotation0: float
    deflection0: float

    def moment(self, s: float) -> float:
        return self.moment0 + self.shear0 * s - self.load * s**2 / 2

    def shear(self, s: float) -> float:
        return self.shear0 - self.load * s

    def rotation(self, s: float) -> float:
        return (
            self.rotation0
            + (self.moment0 * s + self.shear0 * s**2 / 2 - self.load * s**3 / 6)
            / self.ei
        )

    def down(self, s: float) -> float:
        # The line solver's ordinate is positive upward.
        return -(
            self.deflection0
            + self.rotation0 * s
            + (self.moment0 * s**2 / 2 + self.shear0 * s**3 / 6 - self.load * s**4 / 24)
            / self.ei
        )

    def extrema(self) -> list[float]:
        length = self.end - self.start
        discr = self.shear0**2 + 2 * self.load * self.moment0
        # Rotation is monotone between moment roots. Split on them to
        # recover both roots in a span even if one has a small ordinate.
        cuts = [0.0, length]
        if discr > 0:
            r = math.sqrt(discr)
            cuts.extend(
                position
                for position in (
                    (self.shear0 - r) / self.load,
                    (self.shear0 + r) / self.load,
                )
                if 0 < position < length
            )
        roots = []
        for a, b in pairwise(sorted(cuts)):
            ra, rb = self.rotation(a), self.rotation(b)
            if a > 0 and abs(ra) <= 1e-12:
                roots.append(a)
            if ra * rb < 0 and min(abs(ra), abs(rb)) > 1e-12:
                low, high = a, b
                for _ in range(56):
                    mid = (low + high) / 2
                    if self.rotation(mid) * ra > 0:
                        low = mid
                    else:
                        high = mid
                roots.append((low + high) / 2)
        return sorted(roots, key=lambda s: -abs(self.down(s)))


def _fields(
    line: OperationResult, member: BeamContinuousCheckRequestV1, ei: float, load: float
) -> tuple[_SpanField, ...]:
    if line.execution is not ExecutionState.COMPLETED or line.diagnostics:
        return ()
    first: dict[str, dict[str, Any]] = {}
    for station in line.outputs["stations"]:
        first.setdefault(station["physical_span_id"], station)
    spans = []
    for index, (left, right) in enumerate(pairwise(member.supports), 1):
        span_id = f"SPAN-{index}"
        row = first.get(span_id)
        if row is None or not _near(row["x_mm"], left.centre_mm):
            return ()
        spans.append(
            _SpanField(
                span_id,
                left.centre_mm,
                right.centre_mm,
                ei,
                load,
                row["m3_nmm"],
                row["v2_n"],
                row["rotation_rad"],
                row["vertical_displacement_mm"],
            )
        )
    return tuple(spans)


def _near(a: float, b: float) -> bool:
    return math.isclose(a, b, abs_tol=_POSITION_TOLERANCE_MM, rel_tol=0)


def _issue(code: str, path: str, message: str) -> StructuralIssueV1:
    return StructuralIssueV1("BEAM." + code, path, message)


def _mirrored_in_width(bars: tuple[BarPosition, ...], width: float) -> bool:
    # The existing service domain verifies the mirror about mid-depth.
    for face in Face:
        pattern = sorted(
            (bar.y_from_top_mm, bar.diameter_mm, bar.x_from_left_mm)
            for bar in bars
            if bar.face is face
        )
        mirrored = sorted((y, phi, width - x) for y, phi, x in pattern)
        if any(
            not _near(actual[2], reflected[2])
            for actual, reflected in zip(pattern, mirrored, strict=True)
        ):
            return False
    return True


def _case_rows(
    member: BeamContinuousCheckRequestV1,
    cases: tuple[tuple[str, str, tuple[_SpanField, ...]], ...],
) -> _ACTIONS | None:
    stations = {item.station_id: item for item in member.stations}
    combinations = {item.combination_id: item for item in member.combinations}
    middle = member.supports[1].centre_mm
    used = {name for name, _, _ in cases}
    supplied = {
        (row.combination_id, row.station_id): row
        for row in member.actions
        if row.combination_id in used
    }
    for name, kind, fields in cases:
        case = combinations.get(name)
        if (
            case is None
            or case.kind != kind
            or set(case.required_station_ids) != set(stations)
        ):
            return None
        for sid, station in stations.items():
            row = supplied.get((name, sid))
            right = station.x_mm > middle or (
                station.x_mm == middle and station.side == "RIGHT"
            )
            span = fields[int(right)]
            local = station.x_mm - span.start
            if (
                row is None
                or row.tu_knm != 0
                or not (
                    _near(row.mu_knm, span.moment(local) / 1e6)
                    and _near(row.vu_kn, span.shear(local) / 1e3)
                )
            ):
                return None
    return supplied


def _station_at(
    member: BeamContinuousCheckRequestV1,
    x: float,
    side: str = "CONTINUOUS",
) -> BeamContinuousStationV1 | None:
    return next(
        (st for st in member.stations if st.side == side and _near(st.x_mm, x)), None
    )


def _crack_stations(
    member: BeamContinuousCheckRequestV1,
    spans: tuple[_SpanField, ...],
) -> tuple[BeamContinuousStationV1, ...]:
    left, centre, right = member.supports
    evidence = (
        (left.centre_mm, "RIGHT"),
        (left.right_face_mm, "CONTINUOUS"),
        (centre.left_face_mm, "CONTINUOUS"),
        (centre.centre_mm, "LEFT"),
        (centre.centre_mm, "RIGHT"),
        (centre.right_face_mm, "CONTINUOUS"),
        (right.left_face_mm, "CONTINUOUS"),
        (right.centre_mm, "LEFT"),
    )
    stations = [_station_at(member, x, side) for x, side in evidence]
    if any(item is None for item in stations):
        return ()
    selected = {item.station_id: item for item in stations[2:6] if item is not None}
    for span in spans:
        local = span.shear0 / span.load
        positive = _station_at(member, span.start + local)
        if (
            positive is None
            or not 0 < local < span.end - span.start
            or span.moment(local) <= 0
        ):
            return ()
        selected[positive.station_id] = positive
    return tuple(sorted(selected.values(), key=lambda item: (item.x_mm, item.side)))


def _age_state(
    request: BeamServiceHistoryInputV1,
    layers: tuple[tuple[float, float], ...],
    ec: float,
    mcr: float,
    age_days: float,
    creep: float,
    shrinkage: float,
) -> dict[str, float]:
    member = request.member
    modulus = ec / (1 + creep)
    axis, inertia = cracked_service_section(
        member.width_mm, member.depth_mm, layers, modulus, _ES
    )
    return {
        "age_days": age_days,
        "creep_coefficient": creep,
        "shrinkage_strain": shrinkage,
        "concrete_modulus_nmm2": modulus,
        "neutral_axis_mm": axis,
        "cracked_inertia_mm4": inertia,
        "cracking_moment_knm": mcr,
    }


def _ei(state: dict[str, float]) -> float:
    return state["concrete_modulus_nmm2"] * state["cracked_inertia_mm4"]


def _span_extrema(
    member: BeamContinuousCheckRequestV1,
    total: _SpanField,
    sustained: _SpanField,
    finish: dict[str, float],
    assessment: dict[str, float],
    profile: str,
) -> list[dict[str, Any]]:
    length = total.end - total.start
    limit_final = deflection_limit(
        DeflectionLimitRequest(profile, length, DeflectionCriterion.TOTAL_FINAL)
    )
    limit_after = deflection_limit(
        DeflectionLimitRequest(profile, length, DeflectionCriterion.AFTER_FINISHES)
    )
    rows = []
    for local in total.extrema():
        station = _station_at(member, total.start + local)
        if station is None:
            return []
        immediate, g = total.down(local), sustained.down(local)
        at_finishes = g * total.ei / _ei(finish)
        # With a common EI per stage and proportional loads, all age
        # fields have the same shape and their stationary points agree.
        at_assessment = g * total.ei / _ei(assessment) + (immediate - g)
        rows.append(
            {
                "span_id": total.span_id,
                "span_mm": length,
                "station_id": station.station_id,
                "x_mm": total.start + local,
                "initial_total_mm": immediate,
                "initial_sustained_mm": g,
                "at_finishes_mm": at_finishes,
                "at_assessment_mm": at_assessment,
                "after_finishes_mm": at_assessment - at_finishes,
                "shrinkage_deflection_mm": 0.0,
                "total_limit_mm": limit_final.outputs["limit_mm"],
                "after_finishes_limit_mm": limit_after.outputs["limit_mm"],
            }
        )
    return rows


def _crack_summary(
    request: BeamServiceHistoryInputV1,
    bars: tuple[BarPosition, ...],
    station: BeamContinuousStationV1,
    total: BeamContinuousActionV1,
    sustained: BeamContinuousActionV1,
    initial: dict[str, float],
    assessment: dict[str, float],
) -> tuple[dict[str, Any], OperationResult]:
    face = Face.TOP if total.mu_knm < 0 else Face.BOTTOM
    depth = request.member.depth_mm
    k_g = abs(sustained.mu_knm) * 1e6 / _ei(assessment)
    k_q = abs(total.mu_knm - sustained.mu_knm) * 1e6 / _ei(initial)
    curvature = k_g + k_q
    axis = (
        (k_g * assessment["neutral_axis_mm"] + k_q * initial["neutral_axis_mm"])
        / curvature
        if curvature
        else initial["neutral_axis_mm"]
    )
    layers = [
        (
            bar.y_from_top_mm if face is Face.BOTTOM else depth - bar.y_from_top_mm,
            bar.diameter_mm**2,
        )
        for bar in bars
        if bar.face is face
    ]
    d_eff = math.fsum(y * weight for y, weight in layers) / math.fsum(
        weight for _, weight in layers
    )
    strain = curvature * (depth - axis)
    stress = _ES * curvature * (d_eff - axis)
    result = _face_crack(
        request,
        bars,
        station.station_id,
        face,
        axis,
        stress,
        strain,
        service_action_row_id=total.row_id,
    )
    cracked = abs(total.mu_knm) > initial["cracking_moment_knm"]
    return {
        "station_id": station.station_id,
        "x_mm": station.x_mm,
        "tension_face": face.value,
        "assessment_row_id": total.row_id,
        "sustained_row_id": sustained.row_id,
        "cracked": cracked,
        "width_mm": result.outputs.get("calculated_crack_width_mm") if cracked else 0.0,
        "neutral_axis_mm": axis,
        "surface_strain": strain,
        "tensile_steel_stress_nmm2": stress,
        "surface_x_mm": result.effective_inputs["request"]["value"][
            "surface_point_x_from_left_mm"
        ],
        "nearest_steel_mm": result.outputs.get("acr_mm"),
    }, result


def evaluate_unequal_service_history(
    request: BeamServiceHistoryInputV1,
) -> tuple[dict[str, Any] | None, StructuralIssueV1 | None]:
    """Produce an auditable two-span history from the actual signed rows."""
    member, basis = request.member, request.unequal_span_basis
    history, total = request.history, request.service_load
    assert (
        basis is not None
        and history is not None
        and history.sustained_load is not None
        and total is not None
    )
    sustained = history.sustained_load
    bars = _service_bars(request)
    if (
        not isinstance(member, BeamContinuousCheckRequestV1)
        or basis.axial_restraint != "free"
        or basis.shrinkage_profile != "uniform_through_section"
        or not _mirrored_in_width(bars, member.width_mm)
    ):
        return None, _issue(
            "HISTORY_PROFILE_HELD",
            "unequal_span_basis",
            "Supply a mirrored rectangular beam with verified free axial shortening and uniform through-depth shrinkage.",
        )
    if (issue := _service_domain(request, bars, unequal_spans=True)) is not None:
        return None, issue
    if _service_geometry(request, bars).engineering is not EngineeringState.PASS:
        return None, _issue(
            "SERVICE_GEOMETRY_HELD",
            "member.bars",
            "The actual bar positions do not meet the physical section geometry checks.",
        )

    layers = tuple(
        (bar.y_from_top_mm, math.pi * bar.diameter_mm**2 / 4) for bar in bars
    )
    ec = 5000 * math.sqrt(member.fck_nmm2)
    mcr = calculate_cracking_moment(
        b_mm=member.width_mm, D_mm=member.depth_mm, fck_nmm2=member.fck_nmm2
    )
    initial = _age_state(request, layers, ec, mcr, history.loading_age_days, 0.0, 0.0)
    finish, assessment = (
        _age_state(
            request,
            layers,
            ec,
            mcr,
            age.age_days,
            age.creep_coefficient,
            age.shrinkage_strain,
        )
        for age in (history.at_finishes, history.at_assessment)
    )
    total_line = _analyze_line(request, ec, initial["cracked_inertia_mm4"])
    g_line = _analyze_line(
        request.model_copy(update={"service_load": sustained}),
        ec,
        initial["cracked_inertia_mm4"],
    )
    total_fields = _fields(
        total_line, member, _ei(initial), total.uniform_load_kn_per_m
    )
    g_fields = _fields(g_line, member, _ei(initial), sustained.uniform_load_kn_per_m)
    if not total_fields or not g_fields:
        return None, _issue(
            "SERVICE_ANALYSIS_HELD",
            "service_load",
            "The direct-stiffness solution for both load cases is required.",
        )
    rows = _case_rows(
        member,
        (
            (total.combination_id, "SLS", total_fields),
            (sustained.combination_id, "SUSTAINED_SLS", g_fields),
        ),
    )
    if rows is None:
        return None, _issue(
            "SERVICE_ROWS_HELD",
            "member.actions",
            "Supply a complete pair of current signed service rows at every declared station.",
        )

    groups = [
        _span_extrema(member, q, g, finish, assessment, request.schema_version)
        for q, g in zip(total_fields, g_fields, strict=True)
    ]
    crack_stations = _crack_stations(member, total_fields)
    if not all(groups) or not crack_stations:
        return None, _issue(
            "SERVICE_ROWS_HELD",
            "member.stations",
            "Supply the signed sides, physical support faces and exact deflection and moment extrema of both spans.",
        )

    extrema = [row for group in groups for row in group]
    span_deflections = [group[0] for group in groups]
    cracks = []
    crack_checks = {}
    immediate_crack_checks = {}
    for station in crack_stations:
        sid = station.station_id
        total_row = rows[total.combination_id, sid]
        summary, leaf = _crack_summary(
            request,
            bars,
            station,
            total_row,
            rows[sustained.combination_id, sid],
            initial,
            assessment,
        )
        if leaf.execution is not ExecutionState.COMPLETED:
            return None, _issue(
                "HISTORY_CALCULATION_HELD",
                "history.crack_sections",
                f"The Annex F crack check could not resolve station {sid}.",
            )
        cracks.append(summary)
        if summary["cracked"]:
            crack_checks[sid] = leaf.to_dict()
            _, immediate_leaf = _crack_summary(
                request,
                bars,
                station,
                total_row,
                total_row,
                initial,
                initial,
            )
            if immediate_leaf.execution is not ExecutionState.COMPLETED:
                return None, _issue(
                    "HISTORY_CALCULATION_HELD",
                    "instantaneous.crack_sections",
                    f"The instantaneous Annex F check could not resolve station {sid}.",
                )
            immediate_crack_checks[sid] = immediate_leaf.to_dict()

    governing_deflection = max(
        extrema, key=lambda row: abs(row["at_assessment_mm"]) / row["total_limit_mm"]
    )
    governing_after_finishes = max(
        extrema,
        key=lambda row: abs(row["after_finishes_mm"]) / row["after_finishes_limit_mm"],
    )
    governing_crack = min(cracks, key=lambda row: (-row["width_mm"], row["station_id"]))
    limit = request.instantaneous_deflection_limit_mm
    assert limit is not None
    failed = (
        any(abs(row["initial_total_mm"]) > limit for row in extrema)
        or abs(governing_deflection["at_assessment_mm"])
        > governing_deflection["total_limit_mm"]
        or abs(governing_after_finishes["after_finishes_mm"])
        > governing_after_finishes["after_finishes_limit_mm"]
        or any(
            check["engineering"] == "fail"
            for check in (*crack_checks.values(), *immediate_crack_checks.values())
        )
    )
    return {
        "initial": initial,
        "at_finishes": finish,
        "at_assessment": assessment,
        "signed_rows": [row.model_dump(mode="json") for row in rows.values()],
        "deflection_extrema": extrema,
        "span_deflections": span_deflections,
        "crack_sections": cracks,
        "crack_checks": crack_checks,
        "instantaneous_crack_checks": immediate_crack_checks,
        "governing_deflection_station_id": governing_deflection["station_id"],
        "governing_after_finishes_station_id": governing_after_finishes["station_id"],
        "governing_crack_station_id": governing_crack["station_id"],
        "uniform_shrinkage_curvature_per_mm": 0.0,
        "instantaneous_deflection_limit_mm": limit,
        "analysis_result_ids": {
            total.combination_id: total_line.result_id,
            sustained.combination_id: g_line.result_id,
        },
    }, (
        _issue(
            "HISTORY_LIMIT_EXCEEDED",
            "history",
            "At least one serviceability limit is exceeded.",
        )
        if failed
        else None
    )
