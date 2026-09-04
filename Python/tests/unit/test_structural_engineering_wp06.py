from dataclasses import replace
from math import pi

import pytest

from structural_lib.beam import (
    BarPathRequest,
    BarPathRole,
    BarPathSeed,
    BeamDesignProfile,
    BeamProject,
    BeamProjectDefinition,
    BeamProjectRequest,
    BendKind,
    CheckScope,
    DesignCheckRule,
    DesignCriterion,
    EffectiveDepthIteration,
    MemberDesignRequest,
    MemberLeafEvidence,
    MemberLocalCoordinateSystem,
    MemberScopeInstance,
    PathNode,
    PathPoint,
    RevisionBinding,
    SeismicDesignProfile,
    StructuralUnitBasis,
    create_beam_project,
    design_member,
    resolve_bar_paths,
)
from structural_lib.beam.semantics import (
    ApplicabilityState,
    CompletenessState,
    EngineeringState,
    ExecutionState,
    FreshnessState,
)


def _project_request() -> BeamProjectRequest:
    return BeamProjectRequest(
        BeamProjectDefinition("PROJECT-1", "Office beam design", "project-r1"),
        StructuralUnitBasis("mm", "N", "Nmm", "N/mm2"),
        (RevisionBinding("is456", "is456-r1", "IS 456 project source"),),
        BeamDesignProfile(
            "PROFILE-1",
            "profile-r1",
            "IS 456:2000",
            SeismicDesignProfile.ORDINARY_IS456,
            (
                DesignCheckRule(
                    "flexure",
                    "is456.beam.flexure.check/v1",
                    CheckScope.MEMBER,
                    ApplicabilityState.APPLICABLE,
                    "IS 456 flexure",
                    "is456",
                ),
                DesignCheckRule(
                    "shear",
                    "is456.beam.shear.check/v1",
                    CheckScope.STATION,
                    ApplicabilityState.APPLICABLE,
                    "IS 456 shear",
                    "is456",
                ),
                DesignCheckRule(
                    "seismic",
                    "is456.beam.seismic_detailing.check/v1",
                    CheckScope.MEMBER,
                    ApplicabilityState.NOT_APPLICABLE,
                    "ordinary frame profile",
                    "is456",
                ),
            ),
            (DesignCriterion("nominal-cover", 25, "mm", "project durability basis"),),
        ),
        (RevisionBinding("rebar", "rebar-r1", "project bar catalogue"),),
    )


def _project() -> BeamProject:
    request = _project_request()
    created = create_beam_project(request)
    return BeamProject(
        created.outputs["project"]["project_basis_id"],
        request.project,
        request.unit_basis,
        request.code_data_revisions,
        request.catalogue_revisions,
        request.profile,
    )


def _leaf(
    leaf_id: str,
    operation: str,
    *,
    applicability: ApplicabilityState = ApplicabilityState.APPLICABLE,
    engineering: EngineeringState = EngineeringState.PASS,
    execution: ExecutionState = ExecutionState.COMPLETED,
    completeness: CompletenessState = CompletenessState.COMPLETE_FOR_SCOPE,
    freshness: FreshnessState = FreshnessState.CURRENT,
    utilization: float | None = 0.5,
) -> MemberLeafEvidence:
    return MemberLeafEvidence(
        leaf_id,
        operation,
        f"result:{leaf_id}",
        execution,
        applicability,
        engineering,
        completeness,
        freshness,
        "is456-r1",
        f"method:{leaf_id}",
        f"input:{leaf_id}",
        f"calculation:{leaf_id}" if execution is ExecutionState.COMPLETED else "",
        100,
        110,
        110,
        "Nmm",
        utilization,
    )


def _member_request() -> MemberDesignRequest:
    leaves = (
        _leaf("flexure@B1", "is456.beam.flexure.check/v1", utilization=0.7),
        _leaf("shear@S1", "is456.beam.shear.check/v1", utilization=0.6),
        _leaf(
            "seismic@B1",
            "is456.beam.seismic_detailing.check/v1",
            applicability=ApplicabilityState.NOT_APPLICABLE,
            engineering=EngineeringState.NOT_EVALUATED,
            utilization=None,
        ),
    )
    return MemberDesignRequest(
        _project(),
        "B1",
        "topology-r1",
        "actions-r1",
        "reinforcement-r1",
        "scope-r1",
        (MemberScopeInstance("S1", CheckScope.STATION, "scope-r1"),),
        (
            EffectiveDepthIteration(
                1,
                "reinforcement-r1",
                450,
                tuple(leaf.result_id for leaf in leaves[:2]),
                True,
            ),
        ),
        leaves,
    )


def _axes() -> MemberLocalCoordinateSystem:
    return MemberLocalCoordinateSystem(
        "B1-local",
        "member_station_x",
        "section_x_from_left",
        "section_y_from_top",
    )


def _path_request(
    *paths: BarPathSeed, stock: tuple[float, ...] = (12000,)
) -> BarPathRequest:
    return BarPathRequest(
        "PROFILE-1",
        "project-basis-1",
        "criteria-r1",
        "B1",
        "SPAN-1",
        "topology-r1",
        "detail-r1",
        _axes(),
        0,
        6000,
        300,
        500,
        paths,
        stock,
    )


def _straight(
    bar_id: str,
    mark: str,
    start: float,
    end: float,
    *,
    y_mm: float = 50,
) -> BarPathSeed:
    return BarPathSeed(
        bar_id,
        mark,
        BarPathRole.TOP_LONGITUDINAL,
        1,
        20,
        415,
        (
            PathNode(f"{bar_id}-1", PathPoint(start, 50, y_mm)),
            PathNode(f"{bar_id}-2", PathPoint(end, 50, y_mm)),
        ),
    )


def test_create_project_freezes_profile_units_and_revisions() -> None:
    request = _project_request()
    first = create_beam_project(request)
    second = create_beam_project(request)

    assert first.engineering == "pass"
    assert (
        first.outputs["project"]["project_basis_id"]
        == second.outputs["project"]["project_basis_id"]
    )
    assert first.outputs["project"]["unit_basis"] == {
        "length_unit": "mm",
        "force_unit": "N",
        "moment_unit": "Nmm",
        "stress_unit": "N/mm2",
    }


def test_create_project_rejects_conflicting_profile_and_seismic_rule() -> None:
    request = _project_request()
    duplicate_criteria = replace(
        request.profile,
        criteria=(request.profile.criteria[0], request.profile.criteria[0]),
    )
    conflict_rules = tuple(
        (
            replace(rule, expected_applicability=ApplicabilityState.APPLICABLE)
            if rule.rule_id == "seismic"
            else rule
        )
        for rule in request.profile.check_rules
    )

    duplicate = create_beam_project(replace(request, profile=duplicate_criteria))
    conflict = create_beam_project(
        replace(request, profile=replace(request.profile, check_rules=conflict_rules))
    )

    assert duplicate.execution == "rejected_input"
    assert duplicate.diagnostics[0].code == "PROFILE.CRITERIA"
    assert conflict.execution == "rejected_input"
    assert conflict.diagnostics[0].code == "PROFILE.SEISMIC_CONFLICT"


def test_create_project_rejects_duplicate_revision_and_operation_scope() -> None:
    request = _project_request()
    duplicate_catalogue = replace(
        request,
        catalogue_revisions=(
            RevisionBinding("is456", "catalogue-r1", "conflicting binding"),
        ),
    )
    duplicated_rule = replace(
        request.profile.check_rules[0],
        rule_id="flexure-conflict",
        expected_applicability=ApplicabilityState.NOT_APPLICABLE,
    )
    duplicate_rule = replace(
        request,
        profile=replace(
            request.profile,
            check_rules=(*request.profile.check_rules, duplicated_rule),
        ),
    )

    revision_result = create_beam_project(duplicate_catalogue)
    rule_result = create_beam_project(duplicate_rule)

    assert revision_result.diagnostics[0].code == "REVISION.INVALID"
    assert rule_result.diagnostics[0].code == "PROFILE.CHECK_RULE_CONFLICT"


def test_project_and_member_reject_ambiguous_or_unbound_scope_ids() -> None:
    project_request = _project_request()
    bad_rule = replace(project_request.profile.check_rules[0], rule_id="bad@rule")
    project_result = create_beam_project(
        replace(
            project_request,
            profile=replace(
                project_request.profile,
                check_rules=(bad_rule, *project_request.profile.check_rules[1:]),
            ),
        )
    )
    member_request = _member_request()
    member_result = design_member(
        replace(
            member_request,
            scope_instances=(
                replace(
                    member_request.scope_instances[0], source_revision_id="old-scope"
                ),
            ),
        )
    )

    assert project_result.diagnostics[0].code == "PROFILE.RULE_ID_INVALID"
    assert member_result.diagnostics[0].code == "SCOPE.INVALID"


def test_member_derives_complete_leaf_set_and_accepts_profile_resolved_na() -> None:
    result = design_member(_member_request())
    output = result.outputs["member_design"]

    assert result.engineering == "pass"
    assert output["qualified"] is True
    assert [item["leaf_id"] for item in output["expected_leaves"]] == [
        "flexure@B1",
        "shear@S1",
        "seismic@B1",
    ]
    assert output["governing_leaf_id"] == "flexure@B1"
    assert output["governing_utilization"] == pytest.approx(0.7)


def test_member_rejects_project_changed_after_basis_identity() -> None:
    request = _member_request()
    changed_profile = replace(
        request.project.profile,
        criteria=(replace(request.project.profile.criteria[0], value=40),),
    )
    changed_project = replace(request.project, profile=changed_profile)

    result = design_member(replace(request, project=changed_project))

    assert result.execution == "rejected_input"
    assert result.diagnostics[0].code == "PROJECT.BASIS_INVALID"


@pytest.mark.parametrize(
    ("replacement", "expected_code"),
    [
        (None, "LEAF.MISSING"),
        (
            {"engineering": EngineeringState.NOT_EVALUATED},
            "LEAF.NOT_EVALUATED",
        ),
        ({"freshness": FreshnessState.STALE}, "LEAF.STALE"),
        (
            {"applicability": ApplicabilityState.NOT_APPLICABLE},
            "LEAF.APPLICABILITY_MISMATCH",
        ),
    ],
)
def test_member_keeps_incomplete_required_leaf_visible(
    replacement: dict[str, object] | None,
    expected_code: str,
) -> None:
    request = _member_request()
    leaves = list(request.leaf_results)
    if replacement is None:
        del leaves[1]
    else:
        leaves[1] = replace(leaves[1], **replacement)

    result = design_member(replace(request, leaf_results=tuple(leaves)))

    assert result.execution == "completed"
    assert result.engineering == "not_evaluated"
    assert result.completeness == "partial"
    assert expected_code in {item.code for item in result.diagnostics}
    assert result.outputs["member_design"]["qualified"] is False


def test_member_reports_complete_engineering_failure() -> None:
    request = _member_request()
    leaves = list(request.leaf_results)
    leaves[1] = replace(leaves[1], engineering=EngineeringState.FAIL)

    result = design_member(replace(request, leaf_results=tuple(leaves)))

    assert result.execution == "completed"
    assert result.completeness == "complete_for_scope"
    assert result.engineering == "fail"
    assert result.outputs["member_design"]["qualified"] is False


def test_stale_leaf_cannot_become_governing_member_evidence() -> None:
    request = _member_request()
    leaves = list(request.leaf_results)
    leaves[1] = replace(
        leaves[1], freshness=FreshnessState.STALE, governing_utilization=0.99
    )

    result = design_member(replace(request, leaf_results=tuple(leaves)))

    assert result.outputs["member_design"]["governing_leaf_id"] == "flexure@B1"
    assert result.outputs["member_design"]["governing_utilization"] == pytest.approx(
        0.7
    )


def test_member_requires_current_actual_depth_convergence() -> None:
    request = _member_request()
    unconverged = replace(request.depth_iterations[0], converged=False)

    result = design_member(replace(request, depth_iterations=(unconverged,)))

    assert result.completeness == "partial"
    assert "DEPTH.NOT_CONVERGED" in {item.code for item in result.diagnostics}


def test_member_depth_iteration_must_bind_every_applicable_leaf() -> None:
    request = _member_request()
    incomplete_binding = replace(
        request.depth_iterations[0],
        dependent_result_ids=(request.leaf_results[0].result_id,),
    )

    result = design_member(replace(request, depth_iterations=(incomplete_binding,)))

    assert result.completeness == "partial"
    assert "DEPTH.RESULT_BINDING" in {item.code for item in result.diagnostics}


def test_open_bar_resolves_tangent_straights_and_exact_bend_arc() -> None:
    seed = BarPathSeed(
        "BAR-1",
        "M1",
        BarPathRole.TOP_LONGITUDINAL,
        1,
        20,
        415,
        (
            PathNode("N1", PathPoint(0, 50, 50)),
            PathNode(
                "N2",
                PathPoint(1000, 50, 50),
                100,
                BendKind.HOOK,
            ),
            PathNode("N3", PathPoint(1000, 50, 250)),
        ),
    )

    result = resolve_bar_paths(_path_request(seed))
    resolved = result.outputs["reinforcement_schedule"]["paths"][0]

    assert result.engineering == "pass"
    assert [segment["kind"] for segment in resolved["segments"]] == [
        "tangent_straight",
        "bend_arc",
        "tangent_straight",
    ]
    bend_centre = resolved["segments"][1]["bend_centre"]
    assert bend_centre["station_x_mm"] == pytest.approx(900)
    assert bend_centre["section_x_from_left_mm"] == pytest.approx(50)
    assert bend_centre["section_y_from_top_mm"] == pytest.approx(150)
    assert resolved["segments"][1]["centreline_length_mm"] == pytest.approx(50 * pi)
    assert resolved["segments"][1]["bend_plane_normal"] == {
        "station_component": 0,
        "section_horizontal_component": -1,
        "section_vertical_component": 0,
    }
    assert resolved["segments"][1]["bend_sweep_degrees"] == pytest.approx(90)
    assert resolved["developed_centreline_length_mm"] == pytest.approx(1000 + 50 * pi)


def test_closed_link_is_continuous_and_has_four_bend_arcs() -> None:
    seed = BarPathSeed(
        "LINK-1",
        "L1",
        BarPathRole.TRANSVERSE_LINK,
        1,
        8,
        415,
        (
            PathNode("N1", PathPoint(1000, 50, 50), 20, BendKind.STANDARD_BEND),
            PathNode("N2", PathPoint(1000, 250, 50), 20, BendKind.STANDARD_BEND),
            PathNode("N3", PathPoint(1000, 250, 450), 20, BendKind.STANDARD_BEND),
            PathNode("N4", PathPoint(1000, 50, 450), 20, BendKind.STANDARD_BEND),
        ),
        closed=True,
    )

    result = resolve_bar_paths(_path_request(seed))
    segments = result.outputs["reinforcement_schedule"]["paths"][0]["segments"]

    assert len(segments) == 8
    assert sum(item["kind"] == "bend_arc" for item in segments) == 4
    assert sum(item["centreline_length_mm"] for item in segments) == pytest.approx(
        1040 + 40 * pi
    )
    for index, segment in enumerate(segments):
        assert segment["end"] == segments[(index + 1) % len(segments)]["start"]


def test_one_mark_can_count_translated_equal_paths() -> None:
    result = resolve_bar_paths(
        _path_request(
            _straight("BAR-1", "M1", 0, 1000, y_mm=50),
            _straight("BAR-2", "M1", 0, 1000, y_mm=80),
        )
    )

    mark = result.outputs["reinforcement_schedule"]["marks"][0]
    assert mark["bar_ids"] == ["BAR-1", "BAR-2"]
    assert mark["count"] == 2


def test_one_mark_rejects_different_fabrication_geometry() -> None:
    result = resolve_bar_paths(
        _path_request(
            _straight("BAR-1", "M1", 0, 1000),
            _straight("BAR-2", "M1", 0, 1100),
        )
    )

    assert result.execution == "rejected_input"
    assert result.diagnostics[0].code == "MARK.GEOMETRY_CONFLICT"


def test_one_mark_rejects_different_relative_bend_planes() -> None:
    first = BarPathSeed(
        "BAR-1",
        "M1",
        BarPathRole.TOP_LONGITUDINAL,
        1,
        20,
        415,
        (
            PathNode("A1", PathPoint(0, 50, 50)),
            PathNode("A2", PathPoint(1000, 50, 50), 50, BendKind.HOOK),
            PathNode("A3", PathPoint(1000, 50, 250), 50, BendKind.HOOK),
            PathNode("A4", PathPoint(1200, 50, 250)),
        ),
    )
    second = replace(
        first,
        bar_id="BAR-2",
        nodes=(
            PathNode("B1", PathPoint(0, 50, 50)),
            PathNode("B2", PathPoint(1000, 50, 50), 50, BendKind.HOOK),
            PathNode("B3", PathPoint(1000, 50, 250), 50, BendKind.HOOK),
            PathNode("B4", PathPoint(1000, 250, 250)),
        ),
    )

    result = resolve_bar_paths(_path_request(first, second))

    assert result.execution == "rejected_input"
    assert result.diagnostics[0].code == "MARK.GEOMETRY_CONFLICT"


def test_path_requires_bend_evidence_and_reports_stock_failure() -> None:
    no_bend = BarPathSeed(
        "BAR-1",
        "M1",
        BarPathRole.TOP_LONGITUDINAL,
        1,
        20,
        415,
        (
            PathNode("N1", PathPoint(0, 50, 50)),
            PathNode("N2", PathPoint(1000, 50, 50)),
            PathNode("N3", PathPoint(1000, 50, 250)),
        ),
    )
    rejected = resolve_bar_paths(_path_request(no_bend))
    stock_fail = resolve_bar_paths(
        _path_request(_straight("BAR-2", "M2", 0, 1000), stock=(900,))
    )

    assert rejected.execution == "rejected_input"
    assert rejected.diagnostics[0].code == "BEND.EVIDENCE_REQUIRED"
    assert stock_fail.execution == "completed"
    assert stock_fail.engineering == "fail"
    assert stock_fail.diagnostics[0].code == "PATH.STOCK_LENGTH_EXCEEDED"
