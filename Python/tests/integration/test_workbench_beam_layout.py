"""Exercise the installed Quick Beam layout and export replay owner."""

import pytest

from structural_lib.services.contracts.beam import BeamDesignInputV1
from structural_lib.services.project_beam import ProjectBeamDesignInputV1
from structural_lib.services.workbench_beam import (
    replay_workbench_layout,
    workbench_projection,
)


@pytest.mark.parametrize(
    ("width", "depth", "fck", "moment", "expected"),
    [
        (271, 350, 20, 142, "PASS"),  # One middle bar at exactly 75 mm.
        (271.1, 350, 20, 142, "HOLD"),  # One middle bar at 75.05 mm.
        (321, 350, 20, 194, "HOLD"),  # Two adjacent unrestrained bars.
        (350, 450, 25, 325, "HOLD"),  # Reproduced middle bar at 114.5 mm.
    ],
)
def test_workbench_requires_restraint_before_export(
    width, depth, fck, moment, expected
):
    project = ProjectBeamDesignInputV1(
        schema_version="project-beam-design/v1",
        member_id="B-WIDE",
        b_mm=width,
        D_mm=depth,
        d_mm=depth - 60.5,
        mu_knm=moment,
        vu_kn=80,
        fck_nmm2=fck,
        fy_nmm2=500,
        source_metadata={
            "span_mm": 6000,
            "workbench_detailing": {
                "clear_cover_mm": 40,
                "stirrup_diameter_mm": 8,
                "tension_bar_diameter_mm": 25,
                "story": "Quick Beam",
            },
        },
    )
    projection = workbench_projection(project)
    assert projection is not None and projection["status"] == expected
    if expected == "HOLD":
        assert (
            "compression bars require intermediate lateral restraint"
            in projection["reason"]
        )
        assert "checked_request" not in projection
        assert "checked_layout_id" not in projection
        return

    request = BeamDesignInputV1.model_validate(projection["checked_request"])
    replay = replay_workbench_layout(request, projection["checked_layout_id"])
    assert replay.is_ok
    assert projection["schedule_steel_weight_kg"] > 0
    assert {zone["compression"]["count"] for zone in projection["zones"]} == {3}
    assert all(
        len(stations) > 0
        for stations in replay.detailing.detailing.stirrup_stations_by_zone_mm
    )
    with pytest.raises(ValueError, match="layout is stale"):
        replay_workbench_layout(request, "0" * 64)
