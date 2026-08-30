"""Independent W3G closed forms and contract tests, not ETABS calibration.

References: TU Delft CIEM5000 Euler-Bernoulli derivation (theta sign reversed
to w'); Clemson Strength of Materials and Design, beam-deflection table.
Continuous-span and spring references below follow moment-area/compatibility,
not a second call to the implementation's stiffness matrix.
"""

from __future__ import annotations

import hashlib
import inspect
import json

import pytest
from pydantic import ValidationError

from structural_lib.core.analysis_contracts import EvidenceValueV1
from structural_lib.core.beam_line import (
    BeamLineAnalysisBuildResultV1,
    BeamLineAnalysisRequestV1,
    BeamLineCombinationV1,
    BeamLineFactorV1,
    BeamLineLoadCaseV1,
    BeamLineNodalLoadV1,
    BeamLineNodeV1,
    BeamLineNumericsV1,
    BeamLinePointLoadV1,
    BeamLineScenarioV1,
    BeamLineSpanV1,
    BeamLineSupportSpringV1,
    BeamLineSupportV1,
    BeamLineUniformLoadV1,
)
from structural_lib.services.beam_line import solve_beam_line_linear_v1


def no_spring():
    return EvidenceValueV1[BeamLineSupportSpringV1](
        state="NOT_APPLICABLE",
        reason_code="EXPLICIT_NO_SPRING",
        message="Reference boundary has no spring",
        source_references=("closed-form-reference",),
    )


def request(n=1, *, length=6.0, q=-10.0, release=False, offset=0.0):
    nodes = tuple(BeamLineNodeV1(node_id=f"N{i}", x_m=i * length) for i in range(n + 1))
    spans = tuple(
        BeamLineSpanV1(
            span_id=f"S{i}",
            start_node_id=f"N{i}",
            end_node_id=f"N{i+1}",
            elastic_modulus_nmm2=30000.0,
            second_moment_mm4=800000000.0,
            stiffness_modifier=1.0,
            area_mm2=180000.0,
            density_kg_m3=2500.0,
            release_start_rotation=release,
            release_end_rotation=release,
            rigid_offset_start_m=offset,
            rigid_offset_end_m=offset,
            load_domain="FLEXIBLE_LENGTH_ONLY",
        )
        for i in range(n)
    )
    case = BeamLineLoadCaseV1(
        case_id="G",
        uniform_loads=tuple(
            BeamLineUniformLoadV1(span_id=span.span_id, vertical_kn_per_m=q)
            for span in spans
        ),
        point_loads=(),
        nodal_loads=(),
        self_weight_factor=0.0,
    )
    return BeamLineAnalysisRequestV1(
        model_definition_sha256="1" * 64,
        catalogue_sha256="2" * 64,
        scenario_definition_sha256="3" * 64,
        source_basis="SYNTHETIC_REFERENCE",
        nodes=nodes,
        spans=spans,
        supports=tuple(
            BeamLineSupportV1(
                node_id=node.node_id,
                vertical="FIXED",
                rotation="FREE",
                spring=no_spring(),
            )
            for node in nodes
        ),
        load_cases=(case,),
        combinations=(),
        scenario=BeamLineScenarioV1(
            scenario_id="reference",
            purpose="COMPARISON",
            result_kind="CASE",
            result_id="G",
            assumptions=("Prismatic linear elastic horizontal beam",),
        ),
        gravity_m_per_s2=9.81,
        station_intervals_per_span=20,
        numerics=BeamLineNumericsV1(),
        unit_basis="M_KN_KNM_RAD_E_NMM2_I_MM4",
    )


def accepted(req):
    build = solve_beam_line_linear_v1(req)
    assert build.status == "ACCEPTED", build.issues
    assert build.result is not None and not build.issues
    result = build.result
    assert result.capability == "SURROGATE_ONLY"
    assert result.independent_frame_analysis == "HELD_NOT_SUPPORTED"
    assert result.torsion == "HELD_NOT_DERIVED"
    assert result.calibration == "NOT_CALIBRATED_W3H_REQUIRED"
    assert (
        abs(result.equilibrium.force_residual_kn)
        <= result.equilibrium.force_tolerance_kn
    )
    assert (
        abs(result.equilibrium.moment_residual_knm)
        <= result.equilibrium.moment_tolerance_knm
    )
    for span in result.spans:
        last = span.stations[-1]
        assert last.vertical_displacement_m == pytest.approx(
            span.end_displacements_m_rad[2], abs=1e-11
        )
        assert last.rotation_rad == pytest.approx(
            span.end_displacements_m_rad[3], abs=1e-11
        )
        assert last.moment_knm == pytest.approx(span.end_actions_kn_knm[3], abs=1e-9)
        assert last.shear_kn == pytest.approx(-span.end_actions_kn_knm[2], abs=1e-9)
    return result


def blocked(req, code):
    result = solve_beam_line_linear_v1(req)
    assert result.status == "BLOCKED"
    assert result.result is None
    assert result.issues[0].reason_code == code


@pytest.mark.parametrize("length", [0.6, 6.0, 60.0])
@pytest.mark.parametrize("q", [-10.0, 10.0, 0.0])
def test_simply_supported_udl_closed_form(length, q):
    result = accepted(request(length=length, q=q))
    ei = 24000.0
    span = result.spans[0]
    assert span.effective_ei_knm2 == ei
    assert result.nodes[0].vertical_reaction_kn == pytest.approx(-q * length / 2)
    for row in span.stations:
        x = row.distance_from_flexible_start_m
        assert row.moment_knm == pytest.approx(-q * x * (length - x) / 2, abs=1e-9)
        assert row.shear_kn == pytest.approx(q * (x - length / 2), abs=1e-9)
        assert row.vertical_displacement_m == pytest.approx(
            q * x * (length**3 - 2 * length * x**2 + x**3) / (24 * ei),
            rel=1e-9,
            abs=1e-12,
        )


@pytest.mark.parametrize("a", [1.2, 3.0, 4.8])
def test_point_load_closed_form_and_both_shear_sides(a):
    req = request(q=0.0)
    point = BeamLinePointLoadV1(
        span_id="S0", distance_from_flexible_start_m=a, vertical_kn=-12.0
    )
    req = req.model_copy(
        update={
            "load_cases": (
                req.load_cases[0].model_copy(update={"point_loads": (point,)}),
            )
        }
    )
    result = accepted(req)
    length, b, p, ei = 6.0, 6.0 - a, 12.0, 24000.0
    assert result.nodes[0].vertical_reaction_kn == pytest.approx(p * b / length)
    assert result.nodes[1].vertical_reaction_kn == pytest.approx(p * a / length)
    jump = [
        row
        for row in result.spans[0].stations
        if row.distance_from_flexible_start_m == a
    ]
    assert [row.side for row in jump] == ["LEFT", "RIGHT"]
    assert jump[1].shear_kn - jump[0].shear_kn == pytest.approx(-p)
    assert jump[0].vertical_displacement_m == pytest.approx(
        -p * a**2 * b**2 / (3 * ei * length)
    )
    for row in result.spans[0].stations:
        x = row.distance_from_flexible_start_m
        expected = (
            -p * b * x * (length**2 - b**2 - x**2) / (6 * length * ei)
            if x <= a
            else -p
            * a
            * (length - x)
            * (length**2 - a**2 - (length - x) ** 2)
            / (6 * length * ei)
        )
        assert row.vertical_displacement_m == pytest.approx(expected, abs=1e-12)


def test_fixed_fixed_udl():
    req = request()
    req = req.model_copy(
        update={
            "supports": tuple(
                s.model_copy(update={"rotation": "FIXED"}) for s in req.supports
            )
        }
    )
    result = accepted(req)
    mid = result.spans[0].stations[10]
    assert mid.vertical_displacement_m == pytest.approx(-10 * 6**4 / (384 * 24000))
    assert result.spans[0].stations[0].moment_knm == pytest.approx(-10 * 6**2 / 12)
    assert mid.moment_knm == pytest.approx(10 * 6**2 / 24)


def test_cantilever_nodal_load_and_couple():
    req = request(q=0.0)
    supports = (
        req.supports[0].model_copy(update={"rotation": "FIXED"}),
        req.supports[1].model_copy(update={"vertical": "FREE"}),
    )
    case = req.load_cases[0].model_copy(
        update={
            "nodal_loads": (
                BeamLineNodalLoadV1(node_id="N1", vertical_kn=-12.0, moment_knm=5.0),
            )
        }
    )
    result = accepted(
        req.model_copy(update={"supports": supports, "load_cases": (case,)})
    )
    assert result.nodes[1].vertical_displacement_m == pytest.approx(
        -12 * 6**3 / (3 * 24000) + 5 * 6**2 / (2 * 24000)
    )
    assert result.nodes[1].rotation_rad.value == pytest.approx(
        -12 * 6**2 / (2 * 24000) + 5 * 6 / 24000
    )
    assert result.nodes[0].reaction_moment_knm == pytest.approx(67.0)


@pytest.mark.parametrize("n", [2, 3, 4, 5])
def test_continuous_symmetry_equilibrium(n):
    result = accepted(request(n))
    assert [node.vertical_reaction_kn for node in result.nodes] == pytest.approx(
        [node.vertical_reaction_kn for node in reversed(result.nodes)]
    )
    for left, right in zip(result.spans, reversed(result.spans), strict=True):
        assert [row.moment_knm for row in left.stations] == pytest.approx(
            [row.moment_knm for row in reversed(right.stations)], abs=1e-9
        )
    if n == 2:
        assert [node.vertical_reaction_kn for node in result.nodes] == pytest.approx(
            [22.5, 75.0, 22.5]
        )
        assert result.spans[0].stations[-1].moment_knm == pytest.approx(-45.0)
    if n == 3:
        assert result.spans[0].stations[-1].moment_knm == pytest.approx(-36.0)


def test_released_spans_and_disconnected_rotation_not_zero_evidence():
    result = accepted(request(2, release=True))
    assert [node.vertical_reaction_kn for node in result.nodes] == pytest.approx(
        [30.0, 60.0, 30.0]
    )
    assert all(node.rotation_rad.state == "NOT_APPLICABLE" for node in result.nodes)
    assert all(
        abs(span.end_actions_kn_knm[1]) < 1e-9
        and abs(span.end_actions_kn_knm[3]) < 1e-9
        for span in result.spans
    )
    assert result.spans[0].stations[10].vertical_displacement_m == pytest.approx(
        -5 * 10 * 6**4 / (384 * 24000)
    )


def test_single_release_splits_continuity():
    req = request(2)
    spans = (
        req.spans[0].model_copy(update={"release_end_rotation": True}),
        req.spans[1],
    )
    result = accepted(req.model_copy(update={"spans": spans}))
    assert [node.vertical_reaction_kn for node in result.nodes] == pytest.approx(
        [30, 60, 30]
    )
    assert abs(result.spans[0].end_actions_kn_knm[3]) < 1e-9


def test_rigid_offsets_match_shorter_fixed_beam():
    req = request(offset=0.5)
    req = req.model_copy(
        update={
            "supports": tuple(
                s.model_copy(update={"rotation": "FIXED"}) for s in req.supports
            )
        }
    )
    result = accepted(req)
    assert result.spans[0].flexible_length_m == 5.0
    assert result.spans[0].stations[10].vertical_displacement_m == pytest.approx(
        -10 * 5**4 / (384 * 24000)
    )
    assert result.nodes[0].reaction_moment_knm == pytest.approx(
        10 * 5**2 / 12 + 25 * 0.5
    )


@pytest.mark.parametrize("stiffness", [0.0, 100.0, 10000.0, 1e8])
def test_rotational_spring_compatibility(stiffness):
    req = request()
    spring = EvidenceValueV1[BeamLineSupportSpringV1](
        state="PRESENT",
        value=BeamLineSupportSpringV1(rotational_stiffness_knm_per_rad=stiffness),
        source_references=("moment-area-reference",),
    )
    supports = (
        req.supports[0].model_copy(update={"rotation": "SPRING", "spring": spring}),
        req.supports[1],
    )
    result = accepted(req.model_copy(update={"supports": supports}))
    # Moment-area: theta_left = theta_simple/(1 + kL/(3EI)).
    expected = -10 * 6**3 / (24 * 24000) / (1 + stiffness * 6 / (3 * 24000))
    assert result.nodes[0].rotation_rad.value == pytest.approx(expected)
    assert result.nodes[0].reaction_moment_knm == pytest.approx(-stiffness * expected)


def test_self_weight_modifiers_and_signed_nested_combination():
    req = request(q=0.0)
    case = req.load_cases[0].model_copy(update={"self_weight_factor": 1.0})
    combos = (
        BeamLineCombinationV1(
            combination_id="C1",
            factors=(BeamLineFactorV1(source_kind="CASE", source_id="G", factor=2.0),),
        ),
        BeamLineCombinationV1(
            combination_id="C2",
            factors=(
                BeamLineFactorV1(
                    source_kind="COMBINATION", source_id="C1", factor=-0.5
                ),
                BeamLineFactorV1(source_kind="CASE", source_id="G", factor=0.25),
            ),
        ),
    )
    req = req.model_copy(
        update={
            "load_cases": (case,),
            "combinations": combos,
            "spans": (req.spans[0].model_copy(update={"stiffness_modifier": 0.5}),),
            "scenario": req.scenario.model_copy(
                update={"result_kind": "COMBINATION", "result_id": "C2"}
            ),
        }
    )
    result = accepted(req)
    q = 0.75 * 2500 * 0.18 * 9.81 / 1000
    assert result.spans[0].uniform_vertical_kn_per_m == pytest.approx(q)
    assert result.spans[0].stations[10].vertical_displacement_m == pytest.approx(
        5 * q * 6**4 / (384 * 12000)
    )


def test_patterned_load_changes_continuous_actions():
    req = request(2)
    case = req.load_cases[0].model_copy(
        update={"uniform_loads": req.load_cases[0].uniform_loads[:1]}
    )
    result = accepted(req.model_copy(update={"load_cases": (case,)}))
    assert result.spans[0].stations[-1].moment_knm == pytest.approx(-10 * 6**2 / 16)
    assert result.nodes[-1].vertical_reaction_kn < 0  # uplift is retained, not hidden


@pytest.mark.parametrize("support_mode", ["FREE", "ONE_PIN"])
def test_unstable_systems_are_typed_blocked(support_mode):
    req = request()
    supports = tuple(s.model_copy(update={"vertical": "FREE"}) for s in req.supports)
    if support_mode == "ONE_PIN":
        supports = (req.supports[0], supports[1])
    blocked(req.model_copy(update={"supports": supports}), "SINGULAR_OR_UNSTABLE")


@pytest.mark.parametrize(
    "state", ["UNAVAILABLE", "NOT_REQUESTED", "NOT_APPLICABLE", "BLOCKED"]
)
def test_missing_spring_never_defaults_to_zero(state):
    req = request()
    spring = EvidenceValueV1[BeamLineSupportSpringV1](
        state=state,
        reason_code="NO_EVIDENCE",
        message="Not supplied",
        source_references=("source",),
    )
    supports = (
        req.supports[0].model_copy(update={"rotation": "SPRING", "spring": spring}),
        req.supports[1],
    )
    blocked(req.model_copy(update={"supports": supports}), "SPRING_EVIDENCE_REQUIRED")


def test_complete_graph_and_geometry_guards():
    req = request()
    blocked(
        req.model_copy(update={"supports": (req.supports[0], req.supports[0])}),
        "DUPLICATE_IDENTITY",
    )
    blocked(
        req.model_copy(
            update={
                "spans": (
                    req.spans[0].model_copy(update={"rigid_offset_start_m": 6.0}),
                )
            }
        ),
        "INVALID_FLEXIBLE_LENGTH",
    )
    cycle = BeamLineCombinationV1(
        combination_id="C",
        factors=(
            BeamLineFactorV1(source_kind="COMBINATION", source_id="C", factor=1.0),
        ),
    )
    blocked(req.model_copy(update={"combinations": (cycle,)}), "COMBINATION_CYCLE")
    missing = cycle.model_copy(
        update={
            "factors": (
                BeamLineFactorV1(source_kind="CASE", source_id="missing", factor=1.0),
            )
        }
    )
    blocked(req.model_copy(update={"combinations": (missing,)}), "MISSING_CASE")
    blocked(req.model_copy(update={"max_station_rows": 3}), "CAPACITY_EXCEEDED")


@pytest.mark.parametrize(
    "field,value",
    [
        ("gravity_m_per_s2", float("nan")),
        ("gravity_m_per_s2", 0.0),
        ("station_intervals_per_span", 201),
        ("unit_basis", "IMPLICIT"),
    ],
)
def test_revalidate_untrusted_model_copy(field, value):
    blocked(request().model_copy(update={field: value}), "INVALID_OR_NONFINITE_INPUT")


def test_deterministic_serialization_hash_and_public_signature():
    req = request(5)
    first = solve_beam_line_linear_v1(req)
    second = solve_beam_line_linear_v1(req)
    assert first.model_dump_json() == second.model_dump_json()
    assert first == BeamLineAnalysisBuildResultV1.model_validate_json(
        first.model_dump_json()
    )
    result = accepted(req)
    basis = json.dumps(
        result.model_dump(mode="json", exclude={"result_sha256"}),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    assert hashlib.sha256(basis.encode()).hexdigest() == result.result_sha256
    assert (
        inspect.signature(solve_beam_line_linear_v1).parameters["request"].kind
        == inspect.Parameter.POSITIONAL_ONLY
    )
    with pytest.raises(ValidationError):
        BeamLineAnalysisRequestV1.model_validate({**req.model_dump(), "extra": 1})


def test_public_root_projection():
    import structural_lib

    assert structural_lib.solve_beam_line_linear_v1 is solve_beam_line_linear_v1
    assert structural_lib.BeamLineAnalysisRequestV1 is BeamLineAnalysisRequestV1
