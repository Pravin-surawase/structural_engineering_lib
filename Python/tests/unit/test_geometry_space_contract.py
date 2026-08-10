"""GeometrySpaceV1 golden contract fixture checks."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURE = Path(__file__).parents[3] / "tests" / "fixtures" / "geometry-space-v1.json"


def _renderer(point: dict[str, float]) -> tuple[float, float, float]:
    return (point["x"], point["z"], -point["y"])


def _local_beam_renderer(point: dict[str, float]) -> tuple[float, float, float]:
    return (point["x"] * 0.001, point["z"] * 0.001, point["y"] * 0.001)


def test_geometry_space_v1_fixture_preserves_identity_and_global_source_metres() -> (
    None
):
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    transport = fixture["global"]

    assert transport["schemaVersion"] == "GeometrySpaceV1"
    assert transport["frame"] == "GlobalSourceSpaceV1"
    assert transport["units"] == "m"
    assert transport["axes"] == "x=east,y=north,z=up"
    assert [member["memberId"] for member in transport["members"]] == [
        member["sourceId"] for member in transport["members"]
    ]
    assert len({member["memberId"] for member in transport["members"]}) == len(
        transport["members"]
    )
    assert all(member["inputHash"] for member in transport["members"])
    assert all(member["projectRevision"] == 3 for member in transport["members"])
    assert all(member["memberRevision"] == 7 for member in transport["members"])
    assert transport["members"][0]["end"]["x"] == 6


def test_geometry_space_v1_fixture_transform_bounds_and_detail_placement() -> None:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    transport = fixture["global"]
    points = [
        point
        for member in transport["members"]
        for point in (member["start"], member["end"])
    ]

    bounds = {
        "minX": min(point["x"] for point in points),
        "maxX": max(point["x"] for point in points),
        "minY": min(point["y"] for point in points),
        "maxY": max(point["y"] for point in points),
        "minZ": min(point["z"] for point in points),
        "maxZ": max(point["z"] for point in points),
    }
    assert bounds == transport["bounds"]
    assert _renderer(transport["members"][1]["end"]) == tuple(
        transport["rendererCoordinates"]["ETABS-Frame-201"]["end"]
    )

    detail = fixture["detail"]
    assert detail["frame"] == "LocalBeamSpaceV1"
    assert detail["route"] == "/api/v1/geometry/beam/full"
    assert detail["origin"] == "left-support,center-width,soffit"
    assert _local_beam_renderer(detail["rebar"]["end"]) == pytest.approx(
        (6.0, 0.056, -0.096)
    )
    assert detail["stirrup"]["positionX"] == 150
