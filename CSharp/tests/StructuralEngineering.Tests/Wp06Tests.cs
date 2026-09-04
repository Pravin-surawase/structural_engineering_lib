using StructuralEngineering.Beam;
using StructuralEngineering.Contracts;
using StructuralEngineering.Core;
using StructuralEngineering.Reinforcement;
using Xunit;

namespace StructuralEngineering.Tests;

public class Wp06Tests
{
    [Fact]
    public void ProjectFixtureHasCrossLanguageIdentity()
    {
        var first = BeamProjectOperations.Create(ProjectRequest());
        var second = BeamProjectOperations.Create(ProjectRequest());

        Assert.Equal(EngineeringState.Pass, first.Engineering);
        Assert.Equal(
            "beam_project_basis_id:pf4-canonical-json-v1:" +
            "c112392e106832684e3eb9f948c1864093eb781ad1ee3e1a338a6b29bacd5edc",
            first.Outputs!.ProjectBasisId);
        Assert.Equal(first.Outputs.ProjectBasisId, second.Outputs!.ProjectBasisId);
    }

    [Fact]
    public void ProjectRejectsInvalidUnitsAndConflictingRules()
    {
        var request = ProjectRequest();
        var invalidUnits = BeamProjectOperations.Create(request with
        {
            UnitBasis = request.UnitBasis with { LengthUnit = "m" }
        });
        var duplicateRule = request.Profile.CheckRules[0] with
        {
            RuleId = "flexure-conflict",
            ExpectedApplicability = ApplicabilityState.NotApplicable
        };
        var conflict = BeamProjectOperations.Create(request with
        {
            Profile = request.Profile with
            {
                CheckRules = [.. request.Profile.CheckRules, duplicateRule]
            }
        });

        Assert.Equal(ExecutionState.RejectedInput, invalidUnits.Execution);
        Assert.Equal("UNITS.UNSUPPORTED", invalidUnits.Diagnostics[0].Code);
        Assert.Equal(ExecutionState.RejectedInput, conflict.Execution);
        Assert.Equal("PROFILE.CHECK_RULE_CONFLICT", conflict.Diagnostics[0].Code);
    }

    [Fact]
    public void ProjectRejectsCrossCatalogueBindingAndSeismicConflict()
    {
        var request = ProjectRequest();
        var duplicateBinding = BeamProjectOperations.Create(request with
        {
            CatalogueRevisions =
            [new RevisionBinding("is456", "catalogue-r1", "conflict")]
        });
        var seismicConflict = request.Profile.CheckRules
            .Select(item => item.RuleId == "seismic"
                ? item with { ExpectedApplicability = ApplicabilityState.Applicable }
                : item)
            .ToArray();
        var conflict = BeamProjectOperations.Create(request with
        {
            Profile = request.Profile with { CheckRules = seismicConflict }
        });

        Assert.Equal("REVISION.INVALID", duplicateBinding.Diagnostics[0].Code);
        Assert.Equal("PROFILE.SEISMIC_CONFLICT", conflict.Diagnostics[0].Code);
    }

    [Fact]
    public void MemberDerivesCompleteLeafSetAndAcceptsExpectedNotApplicable()
    {
        var result = MemberDesignOperations.Design(MemberRequest());

        Assert.Equal(EngineeringState.Pass, result.Engineering);
        Assert.True(result.Outputs!.Qualified);
        Assert.Equal(
            ["flexure@B1", "shear@S1", "seismic@B1"],
            result.Outputs.ExpectedLeaves.Select(item => item.LeafId));
        Assert.Equal("flexure@B1", result.Outputs.GoverningLeafId);
        Assert.Equal(0.7, result.Outputs.GoverningUtilization!.Value, 12);
    }

    [Fact]
    public void MemberKeepsMissingAndStaleLeavesVisibleButNotGoverning()
    {
        var request = MemberRequest();
        var missing = MemberDesignOperations.Design(request with
        {
            LeafResults = request.LeafResults
                .Where(item => item.LeafId != "shear@S1")
                .ToArray()
        });
        var stale = MemberDesignOperations.Design(request with
        {
            LeafResults = request.LeafResults
                .Select(item => item.LeafId == "shear@S1"
                    ? item with
                    {
                        Freshness = FreshnessState.Stale,
                        GoverningUtilization = 0.99
                    }
                    : item)
                .ToArray()
        });

        Assert.Equal(CompletenessState.Partial, missing.Completeness);
        Assert.Contains(missing.Diagnostics, item => item.Code == "LEAF.MISSING");
        Assert.Equal(CompletenessState.Partial, stale.Completeness);
        Assert.Equal(FreshnessState.Stale, stale.Freshness);
        Assert.Equal("flexure@B1", stale.Outputs!.GoverningLeafId);
        Assert.Equal(0.7, stale.Outputs.GoverningUtilization!.Value, 12);
    }

    [Fact]
    public void MemberDistinguishesFailureDepthBindingAndAlteredProject()
    {
        var request = MemberRequest();
        var failed = MemberDesignOperations.Design(request with
        {
            LeafResults = request.LeafResults
                .Select(item => item.LeafId == "shear@S1"
                    ? item with { Engineering = EngineeringState.Fail }
                    : item)
                .ToArray()
        });
        var unboundDepth = MemberDesignOperations.Design(request with
        {
            DepthIterations =
            [request.DepthIterations[0] with
            {
                DependentResultIds = [request.LeafResults[0].ResultId]
            }]
        });
        var noDepth = MemberDesignOperations.Design(request with
        {
            DepthIterations = []
        });
        var changedProject = request.Project with
        {
            Profile = request.Project.Profile with
            {
                Criteria =
                [request.Project.Profile.Criteria[0] with { Value = 40 }]
            }
        };
        var altered = MemberDesignOperations.Design(request with
        {
            Project = changedProject
        });

        Assert.Equal(EngineeringState.Fail, failed.Engineering);
        Assert.Equal(CompletenessState.CompleteForScope, failed.Completeness);
        Assert.Equal(CompletenessState.Partial, unboundDepth.Completeness);
        Assert.Contains(unboundDepth.Diagnostics,
            item => item.Code == "DEPTH.RESULT_BINDING");
        Assert.Contains(noDepth.Diagnostics,
            item => item.Code == "DEPTH.NOT_CONVERGED");
        Assert.Equal(ExecutionState.RejectedInput, altered.Execution);
        Assert.Equal("PROJECT.BASIS_INVALID", altered.Diagnostics[0].Code);
    }

    [Fact]
    public void InvalidEnumsAndUnboundScopesAreRejected()
    {
        var projectRequest = ProjectRequest();
        var invalidRule = projectRequest.Profile.CheckRules[0] with
        {
            Scope = (CheckScope)999
        };
        var project = BeamProjectOperations.Create(projectRequest with
        {
            Profile = projectRequest.Profile with
            {
                CheckRules = [invalidRule, .. projectRequest.Profile.CheckRules.Skip(1)]
            }
        });
        var memberRequest = MemberRequest();
        var member = MemberDesignOperations.Design(memberRequest with
        {
            ScopeInstances =
            [memberRequest.ScopeInstances[0] with { SourceRevisionId = "old-scope" }]
        });
        var path = BarPathOperations.Resolve(PathRequest(
            Straight("BAR-1", "M1", 0, 1000, 50) with
            {
                Role = (BarPathRole)999
            }));

        Assert.Equal("PROFILE.CHECK_RULE_INVALID", project.Diagnostics[0].Code);
        Assert.Equal("SCOPE.INVALID", member.Diagnostics[0].Code);
        Assert.Equal("PATH.SEED_INVALID", path.Diagnostics[0].Code);
    }

    [Fact]
    public void OpenPathReportsExactTangentArcGeometry()
    {
        var seed = new BarPathSeed(
            "BAR-1",
            "M1",
            BarPathRole.TopLongitudinal,
            1,
            20,
            415,
            [
                new PathNode("N1", new PathPoint(0, 50, 50)),
                new PathNode("N2", new PathPoint(1000, 50, 50), 100, BendKind.Hook),
                new PathNode("N3", new PathPoint(1000, 50, 250))
            ]);

        var result = BarPathOperations.Resolve(PathRequest(seed));
        var path = result.Outputs!.Paths[0];
        var bend = path.Segments[1];

        Assert.Equal(EngineeringState.Pass, result.Engineering);
        Assert.Equal(
            [
                PathSegmentKind.TangentStraight,
                PathSegmentKind.BendArc,
                PathSegmentKind.TangentStraight
            ],
            path.Segments.Select(item => item.Kind));
        Assert.Equal(900, bend.BendCentre!.StationXMm, 12);
        Assert.Equal(50, bend.BendCentre.SectionXFromLeftMm, 12);
        Assert.Equal(150, bend.BendCentre.SectionYFromTopMm, 12);
        Assert.Equal(0, bend.BendPlaneNormal!.StationComponent, 12);
        Assert.Equal(-1, bend.BendPlaneNormal.SectionHorizontalComponent, 12);
        Assert.Equal(0, bend.BendPlaneNormal.SectionVerticalComponent, 12);
        Assert.Equal(90, bend.BendSweepDegrees!.Value, 12);
        Assert.Equal(50 * Math.PI, bend.CentrelineLengthMm, 12);
        Assert.Equal(1000 + 50 * Math.PI, path.DevelopedCentrelineLengthMm, 12);
    }

    [Fact]
    public void ClosedLinkIsContinuousThroughFourArcs()
    {
        var seed = new BarPathSeed(
            "LINK-1",
            "L1",
            BarPathRole.TransverseLink,
            1,
            8,
            415,
            [
                new PathNode("N1", new PathPoint(1000, 50, 50), 20,
                    BendKind.StandardBend),
                new PathNode("N2", new PathPoint(1000, 250, 50), 20,
                    BendKind.StandardBend),
                new PathNode("N3", new PathPoint(1000, 250, 450), 20,
                    BendKind.StandardBend),
                new PathNode("N4", new PathPoint(1000, 50, 450), 20,
                    BendKind.StandardBend)
            ],
            Closed: true);

        var path = BarPathOperations.Resolve(PathRequest(seed)).Outputs!.Paths[0];

        Assert.Equal(8, path.Segments.Count);
        Assert.Equal(4, path.Segments.Count(item =>
            item.Kind == PathSegmentKind.BendArc));
        Assert.Equal(1040 + 40 * Math.PI,
            path.DevelopedCentrelineLengthMm, 12);
        for (var index = 0; index < path.Segments.Count; index++)
        {
            Assert.Equal(
                path.Segments[index].End,
                path.Segments[(index + 1) % path.Segments.Count].Start);
        }
    }

    [Fact]
    public void MarksRequireMatchingGeometryButAllowTranslatedPlacement()
    {
        var first = Straight("BAR-1", "M1", 0, 1000, 50);
        var translated = Straight("BAR-2", "M1", 0, 1000, 80);
        var grouped = BarPathOperations.Resolve(PathRequest(first, translated));
        var conflict = BarPathOperations.Resolve(PathRequest(
            first,
            Straight("BAR-2", "M1", 0, 1100, 80)));

        Assert.Equal(2, grouped.Outputs!.Marks[0].Count);
        Assert.Equal(["BAR-1", "BAR-2"], grouped.Outputs.Marks[0].BarIds);
        Assert.Equal(ExecutionState.RejectedInput, conflict.Execution);
        Assert.Equal("MARK.GEOMETRY_CONFLICT", conflict.Diagnostics[0].Code);
    }

    [Fact]
    public void MarksRejectDifferentRelativeBendPlanes()
    {
        var first = new BarPathSeed(
            "BAR-1",
            "M1",
            BarPathRole.TopLongitudinal,
            1,
            20,
            415,
            [
                new PathNode("A1", new PathPoint(0, 50, 50)),
                new PathNode("A2", new PathPoint(1000, 50, 50), 50, BendKind.Hook),
                new PathNode("A3", new PathPoint(1000, 50, 250), 50, BendKind.Hook),
                new PathNode("A4", new PathPoint(1200, 50, 250))
            ]);
        var second = first with
        {
            BarId = "BAR-2",
            Nodes =
            [
                new PathNode("B1", new PathPoint(0, 50, 50)),
                new PathNode("B2", new PathPoint(1000, 50, 50), 50, BendKind.Hook),
                new PathNode("B3", new PathPoint(1000, 50, 250), 50, BendKind.Hook),
                new PathNode("B4", new PathPoint(1000, 250, 250))
            ]
        };

        var result = BarPathOperations.Resolve(PathRequest(first, second));

        Assert.Equal(ExecutionState.RejectedInput, result.Execution);
        Assert.Equal("MARK.GEOMETRY_CONFLICT", result.Diagnostics[0].Code);
    }

    [Fact]
    public void PathRequiresBendEvidenceAndReportsStockFailure()
    {
        var missingBend = new BarPathSeed(
            "BAR-1",
            "M1",
            BarPathRole.TopLongitudinal,
            1,
            20,
            415,
            [
                new PathNode("N1", new PathPoint(0, 50, 50)),
                new PathNode("N2", new PathPoint(1000, 50, 50)),
                new PathNode("N3", new PathPoint(1000, 50, 250))
            ]);
        var rejected = BarPathOperations.Resolve(PathRequest(missingBend));
        var stockFailure = BarPathOperations.Resolve(PathRequest(
            [900],
            Straight("BAR-2", "M2", 0, 1000, 50)));

        Assert.Equal(ExecutionState.RejectedInput, rejected.Execution);
        Assert.Equal("BEND.EVIDENCE_REQUIRED", rejected.Diagnostics[0].Code);
        Assert.Equal(ExecutionState.Completed, stockFailure.Execution);
        Assert.Equal(EngineeringState.Fail, stockFailure.Engineering);
        Assert.Equal("PATH.STOCK_LENGTH_EXCEEDED",
            stockFailure.Diagnostics[0].Code);
    }

    private static BeamProjectRequest ProjectRequest() => new(
        new BeamProjectDefinition("PROJECT-1", "Office beam design", "project-r1"),
        new StructuralUnitBasis("mm", "N", "Nmm", "N/mm2"),
        [new RevisionBinding("is456", "is456-r1", "IS 456 project source")],
        new BeamDesignProfile(
            "PROFILE-1",
            "profile-r1",
            "IS 456:2000",
            SeismicDesignProfile.OrdinaryIs456,
            [
                new DesignCheckRule(
                    "flexure",
                    "is456.beam.flexure.check/v1",
                    CheckScope.Member,
                    ApplicabilityState.Applicable,
                    "IS 456 flexure",
                    "is456"),
                new DesignCheckRule(
                    "shear",
                    "is456.beam.shear.check/v1",
                    CheckScope.Station,
                    ApplicabilityState.Applicable,
                    "IS 456 shear",
                    "is456"),
                new DesignCheckRule(
                    "seismic",
                    "is456.beam.seismic_detailing.check/v1",
                    CheckScope.Member,
                    ApplicabilityState.NotApplicable,
                    "ordinary frame profile",
                    "is456")
            ],
            [new DesignCriterion(
                "nominal-cover",
                25,
                "mm",
                "project durability basis")]),
        [new RevisionBinding("rebar", "rebar-r1", "project bar catalogue")]);

    private static BeamProject Project() =>
        BeamProjectOperations.Create(ProjectRequest()).Outputs!;

    private static MemberLeafEvidence Leaf(
        string leafId,
        string operation,
        ApplicabilityState applicability = ApplicabilityState.Applicable,
        EngineeringState engineering = EngineeringState.Pass,
        FreshnessState freshness = FreshnessState.Current,
        double? utilization = 0.5) => new(
            leafId,
            operation,
            $"result:{leafId}",
            ExecutionState.Completed,
            applicability,
            engineering,
            CompletenessState.CompleteForScope,
            freshness,
            "is456-r1",
            $"method:{leafId}",
            $"input:{leafId}",
            $"calculation:{leafId}",
            100,
            110,
            110,
            "Nmm",
            utilization,
            []);

    private static MemberDesignRequest MemberRequest()
    {
        var leaves = new[]
        {
            Leaf("flexure@B1", "is456.beam.flexure.check/v1", utilization: 0.7),
            Leaf("shear@S1", "is456.beam.shear.check/v1", utilization: 0.6),
            Leaf(
                "seismic@B1",
                "is456.beam.seismic_detailing.check/v1",
                ApplicabilityState.NotApplicable,
                EngineeringState.NotEvaluated,
                utilization: null)
        };
        return new MemberDesignRequest(
            Project(),
            "B1",
            "topology-r1",
            "actions-r1",
            "reinforcement-r1",
            "scope-r1",
            [new MemberScopeInstance("S1", CheckScope.Station, "scope-r1")],
            [new EffectiveDepthIteration(
                1,
                "reinforcement-r1",
                450,
                leaves.Take(2).Select(item => item.ResultId).ToArray(),
                true)],
            leaves);
    }

    private static BarPathSeed Straight(
        string barId,
        string mark,
        double start,
        double end,
        double y) => new(
            barId,
            mark,
            BarPathRole.TopLongitudinal,
            1,
            20,
            415,
            [
                new PathNode($"{barId}-1", new PathPoint(start, 50, y)),
                new PathNode($"{barId}-2", new PathPoint(end, 50, y))
            ]);

    private static BarPathRequest PathRequest(params BarPathSeed[] paths) =>
        PathRequest([12000], paths);

    private static BarPathRequest PathRequest(
        IReadOnlyList<double> stockLengths,
        params BarPathSeed[] paths) => new(
            "PROFILE-1",
            "project-basis-1",
            "criteria-r1",
            "B1",
            "SPAN-1",
            "topology-r1",
            "detail-r1",
            new MemberLocalCoordinateSystem(
                "B1-local",
                "member_station_x",
                "section_x_from_left",
                "section_y_from_top"),
            0,
            6000,
            300,
            500,
            paths,
            stockLengths);
}
