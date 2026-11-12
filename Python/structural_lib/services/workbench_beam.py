"""Check imported beam layouts and bind inspection outputs to their inputs."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import replace
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from structural_lib.codes.is456.beam.detailing import BeamDetailingWithStirrupStations
from structural_lib.core.errors import InputContractError, StructuralLibError
from structural_lib.services.canonical_beam import (
    BeamDesignAndDetailResultV1,
    design,
    design_and_detail,
)
from structural_lib.services.contracts.beam import (
    BeamDesignInputV1,
    BeamDetailingOptionsV1,
    DetailingStandard,
)
from structural_lib.services.project_beam import ProjectBeamDesignInputV1

_DIAMETERS = (8, 10, 12, 16, 20, 25, 32)


class WorkbenchDetailingOptions(BaseModel):
    """Declared member options for the imported rectangular workflow."""

    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)
    clear_cover_mm: float = Field(ge=20, le=75)
    stirrup_diameter_mm: float = Field(ge=6, le=16)
    tension_bar_diameter_mm: float | None = Field(default=None, ge=8, le=32)
    tension_bar_count: int | None = Field(default=None, ge=2, le=100)
    stirrup_spacing_mm: float | None = Field(default=None, gt=0, le=300)
    story: str = Field(default="Imported", min_length=1, max_length=80)


def _payload_hash(data: dict[str, Any]) -> str:
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def _layout_id(result: BeamDesignAndDetailResultV1) -> str:
    """Bind the request, calculated decisions and actual detailing together."""
    return _payload_hash(result.to_dict())


def _bind_stirrup_stations(
    result: BeamDesignAndDetailResultV1,
) -> BeamDesignAndDetailResultV1:
    """Use one centred, uniform tie run across the three workbench zones."""
    layout = result.detailing.detailing
    stirrups = layout.stirrups
    spacing = stirrups[0].spacing
    if any(
        stirrup.spacing != spacing or stirrup.diameter != stirrups[0].diameter
        for stirrup in stirrups
    ):
        raise ValueError("The workbench requires one stirrup size and spacing.")
    centre_cover = layout.cover + stirrups[0].diameter / 2
    count = math.floor((layout.span - 2 * centre_cover) / spacing) + 1
    if count < 3 or count > 2000:
        raise ValueError("The workbench could not place a bounded stirrup run.")
    first = (layout.span - (count - 1) * spacing) / 2
    if first > spacing:
        raise ValueError("The stirrup run leaves too much space at the member ends.")
    stations = (first + index * spacing for index in range(count))
    start_end = stirrups[0].zone_length
    mid_end = start_end + stirrups[1].zone_length
    zones: tuple[list[float], list[float], list[float]] = ([], [], [])
    for station in stations:
        zone = 0 if station < start_end else 1 if station < mid_end else 2
        zones[zone].append(station)
    if not all(zones):
        raise ValueError("The stirrup run requires a link in each workbench zone.")
    stationed = BeamDetailingWithStirrupStations(
        **vars(layout), stirrup_stations_by_zone_mm=tuple(map(tuple, zones))
    )
    return replace(result, detailing=replace(result.detailing, detailing=stationed))


def _check_request(
    project: ProjectBeamDesignInputV1, options: WorkbenchDetailingOptions
) -> BeamDesignAndDetailResultV1:
    metadata = project.source_metadata or {}
    span = metadata.get("span_mm")
    if (
        isinstance(span, bool)
        or not isinstance(span, (float, int))
        or not math.isfinite(span)
        or span <= 0
    ):
        raise ValueError("Provide a finite positive span before checking detailing.")
    cover = options.clear_cover_mm
    stirrup = options.stirrup_diameter_mm
    depth = project.resolved_d_mm
    candidate = 2 * (project.D_mm - depth - cover - stirrup)
    diameter = next(
        (
            value
            for value in _DIAMETERS
            if math.isclose(value, candidate, rel_tol=0, abs_tol=1e-6)
        ),
        None,
    )
    if diameter is None or (
        options.tension_bar_diameter_mm is not None
        and diameter != options.tension_bar_diameter_mm
    ):
        raise ValueError(
            "The supplied effective depth and cover do not match a supported single-layer bar diameter."
        )
    if stirrup not in (6, 8, 10, 12, 16):
        raise ValueError("Use a standard workbench stirrup diameter.")
    area = 2 * math.pi * stirrup**2 / 4
    source = project.to_dict()
    source["source_metadata"].pop("request_id", None)
    request = BeamDesignInputV1.model_validate(
        {
            "identity": {
                "member_id": project.member_id,
                "story": options.story,
                "case_id": project.member_id,
            },
            "section": {
                "span_mm": span,
                "b_mm": project.b_mm,
                "D_mm": project.D_mm,
                "d_mm": depth,
            },
            "materials": {"fck_nmm2": project.fck_nmm2, "fy_nmm2": project.fy_nmm2},
            "actions": {"mu_knm": project.mu_knm, "vu_kn": project.vu_kn},
            "calculation_basis": {
                "d_dash_mm": cover + stirrup + diameter / 2,
                "asv_mm2": area,
            },
            "source_provenance": f"project-beam/v1:{_payload_hash(source)}",
        }
    )
    preliminary = design(request)
    if not preliminary.is_ok:
        raise ValueError(
            "The beam does not pass with the supplied reinforcement basis."
        )
    spacing = (
        math.floor(preliminary.calculation.shear.spacing)
        if options.stirrup_spacing_mm is None
        else options.stirrup_spacing_mm
    )
    if spacing != int(spacing) or spacing < 1:
        raise ValueError(
            "Stirrup spacing must be a positive whole number of millimetres."
        )
    detail = BeamDetailingOptionsV1(
        standard=DetailingStandard.IS456,
        clear_cover_mm=cover,
        tension_bar_diameter_mm=diameter,
        compression_bar_diameter_mm=diameter,
        nominal_top_steel_ratio=0.25,
        stirrup_diameter_mm=stirrup,
        stirrup_legs=2,
        stirrup_spacing_support_mm=spacing,
        stirrup_spacing_mid_mm=spacing,
    )
    result = design_and_detail(request.model_copy(update={"detailing": detail}))
    if not result.is_ok:
        raise ValueError("The member did not produce an accepted reinforcement layout.")
    layout = result.detailing.detailing
    if any(bar.layers != 1 for bar in (*layout.bottom_bars, *layout.top_bars)):
        raise ValueError(
            "The imported workbench requires a single bar layer on each face."
        )
    if options.tension_bar_count is not None and any(
        bar.count != options.tension_bar_count for bar in layout.bottom_bars
    ):
        raise ValueError(
            "The requested bar count does not match the checked layout. Clear the request or use the calculated count."
        )
    return _bind_stirrup_stations(result)


def workbench_projection(project: ProjectBeamDesignInputV1) -> dict[str, Any] | None:
    """Return the exact checked arrangement, or a visible HOLD for this caller."""
    metadata = project.source_metadata or {}
    raw = metadata.get("workbench_detailing")
    if raw is None:
        return None
    try:
        options = WorkbenchDetailingOptions.model_validate(raw)
        result = _check_request(project, options)
    except InputContractError as exc:
        return {"status": "HOLD", "reason": exc.issues[0].message}
    except ValueError as exc:
        return {"status": "HOLD", "reason": str(exc)}
    except StructuralLibError:
        return {
            "status": "HOLD",
            "reason": "The supplied inputs could not produce a checked layout.",
        }

    layout = result.detailing.detailing
    assert isinstance(layout, BeamDetailingWithStirrupStations)
    calculation = result.design.calculation
    return {
        "status": "PASS",
        "checked_request": result.request.model_dump(mode="json"),
        "checked_layout_id": _layout_id(result),
        "effective_depth_mm": result.request.section.resolved_d_mm(),
        "utilization": calculation.governing_utilization,
        "ast_required_mm2": calculation.flexure.Ast_required,
        "asc_required_mm2": calculation.flexure.Asc_required,
        "shear_spacing_limit_mm": calculation.shear.spacing,
        "zones": [
            {
                "zone": zone,
                "tension": {
                    "count": bottom.count,
                    "diameter_mm": bottom.diameter,
                    "area_mm2": bottom.area_provided,
                    "layers": bottom.layers,
                },
                "compression": {
                    "count": top.count,
                    "diameter_mm": top.diameter,
                    "area_mm2": top.area_provided,
                    "layers": top.layers,
                },
                "stirrup": {
                    "diameter_mm": stir.diameter,
                    "spacing_mm": stir.spacing,
                    "legs": stir.legs,
                    "count": len(stations),
                },
            }
            for zone, bottom, top, stir, stations in zip(
                ("start", "mid", "end"),
                layout.bottom_bars,
                layout.top_bars,
                layout.stirrups,
                layout.stirrup_stations_by_zone_mm,
                strict=True,
            )
        ],
    }


def replay_workbench_layout(
    checked_request: BeamDesignInputV1, checked_layout_id: str
) -> BeamDesignAndDetailResultV1:
    """Recalculate the checked layout and require the exact expected identity."""
    try:
        result = design_and_detail(checked_request)
        if result.is_ok:
            result = _bind_stirrup_stations(result)
    except (StructuralLibError, ValueError) as exc:
        raise ValueError(
            "The beam layout must be checked again before export."
        ) from exc
    if not result.is_ok or _layout_id(result) != checked_layout_id:
        raise ValueError("The checked beam layout is stale. Recalculate before export.")
    return result
