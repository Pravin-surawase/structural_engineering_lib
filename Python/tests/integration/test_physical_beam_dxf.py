"""Actual DXF entities must preserve the accepted physical schedule and state."""

from __future__ import annotations

import json
import runpy
from dataclasses import replace
from pathlib import Path

import pytest

from structural_lib.services.dxf_export import generate_physical_beam_dxf

ez = pytest.importorskip("ezdxf")


@pytest.fixture(scope="module")
def make_workflow():
    return runpy.run_path(
        str(
            Path(__file__).resolve().parents[2] / "examples/complete_member_workflow.py"
        )
    )["run_workflow"]


def metadata(doc):
    return json.loads(
        "".join(
            tag.value
            for tag in doc.rootdict["STRUCTLIB_PHYSICAL_METADATA"].tags
            if tag.code == 1000
        )
    )


def bar_id(entity):
    return entity.get_xdata("STRUCTLIB_PHYSICAL")[1].value


@pytest.mark.parametrize("multilayer,bars", [(False, 39), (True, 43)])
def test_physical_paths_section_layers_and_quantities_match_package(
    make_workflow, tmp_path, multilayer, bars
):
    w = make_workflow(multilayer=multilayer)
    target = tmp_path / "physical.dxf"
    generate_physical_beam_dxf(w.results["paths"], w.results["package"], target)
    doc = ez.readfile(target)
    meta = metadata(doc)
    schedule = w.package_request.schedule
    assert doc.units == 4
    assert meta["issue_state"] == w.package["issue_state"] == "issue_ready"
    assert meta["active_approval"] is False
    assert meta["package_id"] == w.package["calculation_package_id"]
    assert set(meta["source_path_ids"]) == {p.bar_id for p in schedule.paths}
    entities = list(doc.modelspace().query('POLYLINE[layer=="PHYSICAL_3D"]'))
    assert (
        len(entities)
        == bars
        == sum(row.scheduled_bar_count for row in w.package_request.bbs.rows)
    )
    by_id = {bar_id(e): e for e in entities}
    for path in schedule.paths:
        actual = by_id[path.bar_id]
        first = actual.vertices[0].dxf.location
        last = actual.vertices[-1].dxf.location
        start = path.segments[0].start
        end = path.segments[-1].end
        assert tuple(first) == pytest.approx(
            (
                start.station_x_mm,
                start.section_x_from_left_mm,
                500 - start.section_y_from_top_mm,
            )
        )
        assert tuple(last) == pytest.approx(
            (
                end.station_x_mm,
                end.section_x_from_left_mm,
                500 - end.section_y_from_top_mm,
            )
        )
    circles = {
        bar_id(e): e
        for e in doc.modelspace().query('CIRCLE[layer=="LONGITUDINAL_SECTION"]')
    }
    expected = {
        p.bar_id: p for p in schedule.paths if p.role.value != "transverse_link"
    }
    assert set(circles) == set(expected)
    depth_area = []
    for key, path in expected.items():
        circle = circles[key]
        point = path.segments[0].start
        scale = meta["section_view_scale"]
        assert circle.dxf.center.x == pytest.approx(
            meta["section_origin_x_mm"] + point.section_x_from_left_mm * scale
        )
        assert circle.dxf.center.y == pytest.approx(
            (500 - point.section_y_from_top_mm) * scale
        )
        assert circle.dxf.radius == pytest.approx(path.diameter_mm * scale / 2)
        if path.role.value == "bottom_longitudinal":
            depth_area.append((point.section_y_from_top_mm, path.diameter_mm**2))
    actual_centroid = sum(d * a for d, a in depth_area) / sum(a for _, a in depth_area)
    assert actual_centroid == pytest.approx(412.5 if multilayer else 450)
    if multilayer:
        assert {
            p.bar_id: p.layer
            for p in schedule.paths
            if p.bar_id in ("B1", "B3", "T1", "T3")
        } == {"B1": 1, "B3": 2, "T1": 1, "T3": 2}
        assert len(circles) == 8
    assert (
        len(list(doc.modelspace().query('LWPOLYLINE[layer=="LINK_PATH_PROJECTION"]')))
        == 1
    )
    texts = [e.dxf.text for e in doc.modelspace().query("TEXT")]
    assert any(
        f"Steel total {w.package_request.bbs.scheduled_steel_mass_kg:.3f} kg" in s
        for s in texts
    )


@pytest.mark.parametrize(
    "probe", [{"omit_checks": ("crack",)}, {"ultimate_load_n_per_mm": 100}]
)
def test_draft_member_cannot_acquire_accepted_drawing_state(
    make_workflow, tmp_path, probe
):
    w = make_workflow(**probe)
    assert w.package["issue_state"] == "draft"
    target = tmp_path / "draft.dxf"
    generate_physical_beam_dxf(w.results["paths"], w.results["package"], target)
    doc = ez.readfile(target)
    assert metadata(doc)["issue_state"] == "draft"
    assert metadata(doc)["active_approval"] is False
    assert any("DRAFT" in e.dxf.text for e in doc.modelspace().query("TEXT"))


def test_mismatched_paths_and_changed_physical_inputs_reject_before_output(
    make_workflow, tmp_path
):
    ordinary, multi = make_workflow(), make_workflow(multilayer=True)
    target = tmp_path / "wrong.dxf"
    with pytest.raises(ValueError, match="bind"):
        generate_physical_beam_dxf(
            ordinary.results["paths"], multi.results["package"], target
        )
    assert not target.exists()
    original = ordinary.results["paths"]
    inputs = {
        **original.effective_inputs,
        "request": {
            **original.effective_inputs["request"],
            "value": {
                **original.effective_inputs["request"]["value"],
                "section_depth_mm": 600,
            },
        },
    }
    with pytest.raises(ValueError, match="input identity"):
        generate_physical_beam_dxf(
            replace(original, effective_inputs=inputs),
            ordinary.results["package"],
            target,
        )
    assert not target.exists()


def test_single_row_elevation_includes_the_link_and_rejects_unknown_layers():
    from structural_lib.codes.is456.beam.detailing import (
        BarArrangement,
        StirrupArrangement,
    )
    from structural_lib.services.dxf_export import draw_beam_elevation

    # Use the existing immutable detail records, with exact geometric inputs.
    bottom = BarArrangement(
        count=2, diameter=16, area_provided=402, spacing=100, layers=1
    )
    top = BarArrangement(count=2, diameter=12, area_provided=226, spacing=100, layers=1)
    link = StirrupArrangement(diameter=8, spacing=150, legs=2, zone_length=5000)
    doc = ez.new("R2010")
    draw_beam_elevation(
        doc.modelspace(), 5000, 500, 300, 40, [top] * 3, [bottom] * 3, [link] * 3
    )
    horizontals = [
        e
        for e in doc.modelspace().query('LINE[layer=="REBAR_MAIN"]')
        if abs(e.dxf.end.x - e.dxf.start.x) > 1000
    ]
    assert {round(e.dxf.start.y, 8) for e in horizontals} == {56, 446}
    with pytest.raises(ValueError, match="resolved physical bar paths"):
        draw_beam_elevation(
            doc.modelspace(),
            5000,
            500,
            300,
            40,
            [top] * 3,
            [replace(bottom, layers=2)] * 3,
            [link] * 3,
        )


def test_legacy_multilayer_export_rejects_instead_of_writing_a_single_row(tmp_path):
    from structural_lib.core.errors import InputContractError
    from structural_lib.detailing import create_beam_detailing
    from structural_lib.services.api import compute_dxf
    from structural_lib.services.dxf_export import generate_beam_dxf

    # The former mark-only smoke specimen has two layers at each support.
    detail = create_beam_detailing(
        beam_id="B1",
        story="S1",
        b=230,
        D=450,
        span=5000,
        cover=25,
        fck=25,
        fy=415,
        ast_start=900,
        ast_mid=700,
        ast_end=900,
        asc_start=0,
        asc_mid=0,
        asc_end=0,
        stirrup_dia=8,
        stirrup_spacing_start=100,
        stirrup_spacing_mid=150,
        stirrup_spacing_end=100,
        is_seismic=False,
    )
    assert detail.bottom_bars[0].layers == 2
    target = tmp_path / "unresolved.dxf"
    with pytest.raises(ValueError, match="resolved physical bar paths"):
        generate_beam_dxf(detail, str(target))
    assert not target.exists()
    with pytest.raises(InputContractError, match="resolved physical bar paths") as exc:
        compute_dxf([detail], output=str(target))
    assert exc.value.issues[0].path == "detailing_list"
    assert not target.exists()
