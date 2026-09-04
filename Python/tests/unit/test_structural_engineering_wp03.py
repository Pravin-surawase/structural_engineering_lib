import pytest

from structural_lib.beam import (
    ActionConcurrency,
    AnalysisElementMapping,
    BeamElement,
    BeamLineRequest,
    BeamNode,
    BeamPointLoad,
    BeamTopologyRequest,
    ForceUnit,
    LengthUnit,
    LocalAxes,
    MomentUnit,
    PhysicalSpan,
    PhysicalSupport,
    RawActionRow,
    RawActionSnapshot,
    SectionRegion,
    Vector3,
    define_beam_topology,
    normalize_action_snapshot,
    solve_beam_line,
)


def _axes() -> LocalAxes:
    return LocalAxes(
        "local-123",
        Vector3(1, 0, 0),
        Vector3(0, 1, 0),
        Vector3(0, 0, 1),
    )


def _action_snapshot(axes: LocalAxes | None = None) -> RawActionSnapshot:
    return RawActionSnapshot(
        "source-1",
        "model-1",
        "analysis-epoch-1",
        "result-epoch-1",
        ForceUnit.KN,
        MomentUnit.KN_M,
        LengthUnit.M,
        (axes or _axes(),),
        (
            RawActionRow(
                "source-row-1",
                "member-1",
                "span-1",
                "object-1",
                "element-1",
                "local-123",
                2.5,
                0.5,
                "ULS-1",
                "maximum",
                1,
                ActionConcurrency.COMPONENT_ENVELOPE,
                1,
                2,
                3,
                4,
                5,
                6,
            ),
        ),
    )


def test_action_snapshot_normalizes_units_and_preserves_same_row_identity() -> None:
    result = normalize_action_snapshot(_action_snapshot())

    assert result.execution == "completed"
    row = result.outputs["rows"][0]
    assert row["concurrency"] == "component_envelope"
    assert row["object_station_mm"] == 2500
    assert row["element_station_mm"] == 500
    assert (row["p_n"], row["v2_n"], row["v3_n"]) == (1000, 2000, 3000)
    assert (row["t_nmm"], row["m2_nmm"], row["m3_nmm"]) == (
        4_000_000,
        5_000_000,
        6_000_000,
    )
    assert row["source_row_id"] == "source-row-1"
    assert row["analysis_element_id"] == "element-1"
    assert row["row_id"].startswith("action_row_id:pf4-canonical-json-v1:")
    assert result.outputs["snapshot_id"].startswith(
        "action_snapshot_id:pf4-canonical-json-v1:"
    )


def test_action_snapshot_rejects_left_handed_axes() -> None:
    axes = LocalAxes(
        "local-123",
        Vector3(1, 0, 0),
        Vector3(0, 1, 0),
        Vector3(0, 0, -1),
    )
    result = normalize_action_snapshot(_action_snapshot(axes))

    assert result.execution == "rejected_input"
    assert result.diagnostics[0].code == "AXIS.INVALID"


def _topology(*, gap: bool = False) -> BeamTopologyRequest:
    supports = (
        PhysicalSupport("A", 0, -200, 200),
        PhysicalSupport("B", 5000, 4800, 5200),
        PhysicalSupport("C", 10000, 9800, 10200),
    )
    spans = (
        PhysicalSpan(
            "S1",
            "A",
            "B",
            300,
            (SectionRegion("R1", "SEC-1", 10 if gap else 0, 5000),),
        ),
        PhysicalSpan(
            "S2",
            "B",
            "C",
            450,
            (SectionRegion("R2", "SEC-2", 5000, 10000),),
        ),
    )
    mappings = (
        AnalysisElementMapping("E1", "S1", 0, 5000),
        AnalysisElementMapping("E2", "S2", 5000, 10000),
    )
    return BeamTopologyRequest("M1", _axes(), supports, spans, mappings)


def test_topology_binds_support_faces_design_spans_and_analysis_elements() -> None:
    result = define_beam_topology(_topology())

    assert result.execution == "completed"
    first, second = result.outputs["spans"]
    assert first["clear_span_mm"] == 4600
    assert first["centreline_span_mm"] == 5000
    assert first["effective_span_mm"] == 4900
    assert second["effective_span_mm"] == 5000
    assert first["analysis_elements"][0]["analysis_element_id"] == "E1"
    assert result.outputs["topology_id"].startswith(
        "beam_topology_id:pf4-canonical-json-v1:"
    )


def test_topology_rejects_section_region_gap() -> None:
    result = define_beam_topology(_topology(gap=True))

    assert result.execution == "rejected_input"
    assert result.diagnostics[0].code == "REGION.COVERAGE"


def _simple_request(
    *,
    uniform_load_n_per_mm: float = -10,
    points: tuple[BeamPointLoad, ...] = (),
) -> BeamLineRequest:
    return BeamLineRequest(
        "model-1",
        "service-1",
        (
            BeamNode("A", 0, True, False),
            BeamNode("B", 5000, True, False),
        ),
        (
            BeamElement(
                "E1",
                "S1",
                "A",
                "B",
                200_000,
                1_000_000_000,
                uniform_load_n_per_mm,
            ),
        ),
        points,
        10,
    )


def test_simply_supported_udl_matches_closed_form_and_equilibrium() -> None:
    result = solve_beam_line(_simple_request())

    assert result.execution == "completed"
    nodes = {item["node_id"]: item for item in result.outputs["nodes"]}
    assert nodes["A"]["vertical_reaction_n"] == pytest.approx(25_000)
    assert nodes["B"]["vertical_reaction_n"] == pytest.approx(25_000)
    mid = next(
        item
        for item in result.outputs["stations"]
        if item["x_mm"] == 2500 and item["side"] == "continuous"
    )
    assert mid["m3_nmm"] == pytest.approx(31_250_000)
    assert mid["vertical_displacement_mm"] == pytest.approx(
        -5 * 10 * 5000**4 / (384 * 200_000 * 1_000_000_000)
    )
    assert result.outputs["equilibrium"]["force_residual_n"] == pytest.approx(0)
    assert result.outputs["equilibrium"]["moment_residual_nmm"] == pytest.approx(0)


def test_point_load_has_explicit_left_and_right_shear_jump() -> None:
    result = solve_beam_line(
        _simple_request(
            uniform_load_n_per_mm=0,
            points=(BeamPointLoad("E1", 2500, -10_000),),
        )
    )

    rows = [item for item in result.outputs["stations"] if item["x_mm"] == 2500]
    assert [(item["side"], item["v2_n"]) for item in rows] == [
        ("left", pytest.approx(5000)),
        ("right", pytest.approx(-5000)),
    ]


def test_solver_applies_prescribed_support_settlement() -> None:
    request = BeamLineRequest(
        "settlement-model",
        "settlement-case",
        (
            BeamNode("A", 0, True, False),
            BeamNode("B", 5000, True, False, -10),
            BeamNode("C", 10000, True, False),
        ),
        (
            BeamElement("E1", "S1", "A", "B", 200_000, 1_000_000_000),
            BeamElement("E2", "S2", "B", "C", 200_000, 1_000_000_000),
        ),
        station_intervals=10,
    )

    result = solve_beam_line(request)

    assert result.execution == "completed"
    middle = next(item for item in result.outputs["nodes"] if item["node_id"] == "B")
    assert middle["vertical_displacement_mm"] == -10
    assert sum(
        item["vertical_reaction_n"] for item in result.outputs["nodes"]
    ) == pytest.approx(0)


def test_solver_rejects_unstable_beam() -> None:
    request = _simple_request()
    unstable = BeamLineRequest(
        request.model_id,
        request.load_case_id,
        tuple(
            BeamNode(node.node_id, node.x_mm, False, False) for node in request.nodes
        ),
        request.elements,
        request.point_loads,
        request.station_intervals,
    )

    result = solve_beam_line(unstable)

    assert result.execution == "rejected_input"
    assert result.diagnostics[0].code == "ANALYSIS.UNSTABLE"
