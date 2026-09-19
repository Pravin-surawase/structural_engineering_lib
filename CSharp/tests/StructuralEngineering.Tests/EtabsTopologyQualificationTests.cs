using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;
using Xunit;

namespace StructuralEngineering.Tests;

public sealed class EtabsTopologyQualificationTests
{
    [Theory]
    [InlineData(0, false, 300)]
    [InlineData(0, true, 300)]
    [InlineData(45, false, 282.842712474619)]
    [InlineData(45, true, 282.842712474619)]
    public void RectangularColumnRayUsesExitRatherThanProjectedBoundingWidth(double rotation, bool reverse, double expected)
    {
        var (source, geometry) = Example(false, rotation, reverse);
        var result = Assert.Single(EtabsTopologyQualification.Interpret(source, geometry).Members);
        Assert.Equal("qualified_global_axes", result.AxisState);
        Assert.Equal(expected, result.EndI!.ModelledFaceDistanceMm!.Value, 8);
        Assert.Equal(expected, result.EndJ!.ModelledFaceDistanceMm!.Value, 8);
        Assert.Equal(6000 - 2 * expected, result.ModelledClearLengthMm!.Value, 8);
        Assert.Equal(150 - expected, result.EndI.ReportedMinusModelledMm!.Value, 8);
        Assert.Equal(reverse ? 6000 - expected : expected, result.EndI.ModelledFaceGlobalMm![0], 8);
        Assert.Contains(result.Restrictions, r => r.Code == "TOPOLOGY.ENGINEERING_ROLE_REQUIRED");
    }

    [Fact]
    public void WallReferenceEnvelopesPreserveFacesAndReportedAutomaticOffsetsSeparately()
    {
        var (source, geometry) = Example(true);
        var result = Assert.Single(EtabsTopologyQualification.Interpret(source, geometry).Members);
        Assert.Equal(5800, result.ModelledClearLengthMm);
        Assert.Equal(100, result.EndI!.ModelledFaceDistanceMm);
        Assert.Equal(150, result.EndI.ReportedEndOffsetMm);
        Assert.Equal(50, result.EndI.ReportedMinusModelledMm);
        Assert.Equal(new double[] { 100, 0, 3000 }, result.EndI.ModelledFaceGlobalMm);
        Assert.Equal("project_intent_required", result.Role.State);
    }

    [Fact]
    public void OmittedCurvatureRequiresACompleteCollinearMeshAndRejectsBentOrMissingSegments()
    {
        var (source, geometry) = Example(false);
        geometry = geometry with
        {
            Frames = geometry.Frames.Select(f => f.Name == "B1" ? f with { CurveType = null } : f).ToArray(),
            AnalysisPoints = [new("a", [0, 0, 3000]), new("b", [3000, 0, 3000]), new("c", [6000, 0, 3000])]
        };
        source = source with
        {
            Members = [source.Members[0] with
        {
            Elements = [new("e1", "B1", 0, null, null, "a", "b", null, "Objects and Elements - Frames/v1"),
                new("e2", "B1", 0, null, null, "b", "c", null, "Objects and Elements - Frames/v1")]
        }]
        };
        var complete = Assert.Single(EtabsTopologyQualification.Interpret(source, geometry).Members);
        Assert.Equal("collinear_complete_analysis_mesh", complete.ReferenceLineBasis);
        Assert.Equal(5400, complete.ModelledClearLengthMm);
        var bent = geometry with { AnalysisPoints = [geometry.AnalysisPoints[0], new("b", [3000, 10, 3000]), geometry.AnalysisPoints[2]] };
        Assert.Null(Assert.Single(EtabsTopologyQualification.Interpret(source, bent).Members).ModelledClearLengthMm);
        var missing = source with { Members = [source.Members[0] with { Elements = [source.Members[0].Elements[0]] }] };
        Assert.Null(Assert.Single(EtabsTopologyQualification.Interpret(missing, geometry).Members).ModelledClearLengthMm);
    }

    [Fact]
    public void ABeamBeginningOnAWallEndFaceHasZeroInwardExtentRatherThanAMissingSupportFact()
    {
        var (source, geometry) = Example(true);
        // First wall extends behind the beam along X; its end face is at the reference endpoint.
        geometry = geometry with
        {
            Points = geometry.Points.Select(p => p.Name switch
        {
            "I0" => p with { GlobalCoordinatesMm = [0, 0, 0] },
            "I1" => p with { GlobalCoordinatesMm = [-1000, 0, 0] },
            "I2" => p with { GlobalCoordinatesMm = [-1000, 0, 3000] },
            _ => p
        }).ToArray()
        };
        var result = Assert.Single(EtabsTopologyQualification.Interpret(source, geometry).Members);
        Assert.Equal(0, result.EndI!.ModelledFaceDistanceMm);
        Assert.Equal(5900, result.ModelledClearLengthMm);
    }

    [Fact]
    public void WallPlacementGapAndOpeningDoNotBecomeSupportsOrEraseTheBeam()
    {
        var (source, geometry) = Example(true);
        geometry = geometry with { Areas = [geometry.Areas[0] with { PlacementBasis = "unqualified" }, geometry.Areas[1] with { IsOpening = true }] };
        var result = Assert.Single(EtabsTopologyQualification.Interpret(source, geometry).Members);
        Assert.Null(result.ModelledClearLengthMm);
        Assert.Equal("restricted", Assert.Single(result.EndI!.Envelopes).State);
        Assert.Equal("connection_context", Assert.Single(result.EndJ!.Envelopes).State);
    }

    [Fact]
    public void ZeroMassAndWeightAreRoleEvidenceEvenWhenASectionHasAnOrdinaryName()
    {
        var (source, geometry) = Example(false);
        geometry = geometry with
        {
            Frames = geometry.Frames.Select(f => f.Name == "B1" ? f with
            { SectionName = "Ordinary", SectionModifiers = [1, 1, 1, 1, 1, 1, 0, 0] } : f).ToArray()
        };
        var result = Assert.Single(EtabsTopologyQualification.Interpret(source, geometry).Members);
        Assert.True(result.Role.ZeroMassModifier); Assert.True(result.Role.ZeroWeightModifier);
        Assert.Equal("project_intent_required", result.Role.State);
        Assert.Contains(result.Restrictions, r => r.Code == "TOPOLOGY.ZERO_MODIFIER_REVIEW");
    }

    [Fact]
    public void InvalidAxesOrActualJointOffsetsFenceClearLength()
    {
        var (source, geometry) = Example(false);
        var beam = geometry.Frames[0];
        foreach (var altered in new[]
        {
            beam with { GlobalTransformation = [1, 0, 0, 0, 0, 1, 0, 1, 0] },
            beam with { Assignments = beam.Assignments with { InsertionOffsetIMm = [0, 10, 0] } },
            beam with { CurveType = 1 }
        })
        {
            var result = Assert.Single(EtabsTopologyQualification.Interpret(source, geometry with { Frames = [altered, .. geometry.Frames.Skip(1)] }).Members);
            Assert.Null(result.ModelledClearLengthMm);
            Assert.Contains(result.Restrictions, r => r.Code == "TOPOLOGY.BEAM_LINE_UNQUALIFIED");
        }
    }

    [Fact]
    public void MissingConnectionAndReverseIdentityConflictRemainExplicit()
    {
        var (source, geometry) = Example(false);
        geometry = geometry with { Frames = [geometry.Frames[0], geometry.Frames[1] with { EndpointNames = ["CIbase", "J"] }] };
        var result = Assert.Single(EtabsTopologyQualification.Interpret(source, geometry).Members);
        Assert.Null(result.ModelledClearLengthMm);
        Assert.Contains(result.EndI!.Envelopes.SelectMany(e => e.Restrictions), r => r.Code == "TOPOLOGY.CONNECTIVITY_CONFLICT");
        Assert.Contains(result.EndJ!.Envelopes.SelectMany(e => e.Restrictions), r => r.Code == "TOPOLOGY.CONNECTION_UNAVAILABLE");
    }

    [Fact]
    public void OverlappingEnvelopesNeverProduceANegativeUsableSpan()
    {
        var (source, geometry) = Example(false);
        geometry = geometry with { Frames = geometry.Frames.Select(f => f.DesignOrientation == 1 ? f with { DepthMm = 7000 } : f).ToArray() };
        var result = Assert.Single(EtabsTopologyQualification.Interpret(source, geometry).Members);
        Assert.Null(result.ModelledClearLengthMm);
        Assert.Contains(result.Restrictions, r => r.Code == "TOPOLOGY.ENVELOPES_OVERLAP");
    }

    private static (EtabsSourceFacts, EtabsTopologyGeometry) Example(bool wall, double rotation = 0, bool reverse = false)
    {
        double[] ones = [1, 1, 1, 1, 1, 1, 1, 1];
        var assignment = new EtabsSourceAssignments(true, 150, 150, .5, 8, false, false, false, "Global",
            [0, 0, 0], [0, 0, 0], [false, false, false, false, false, false], [false, false, false, false, false, false],
            [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], 0, false);
        var beam = new EtabsTopologyFrame("B1", 2, "R", 8, 300, 600, reverse ? ["J", "I"] : ["I", "J"], 0,
            reverse ? [-1, 0, 0, 0, 0, 1, 0, 1, 0] : [1, 0, 0, 0, 0, -1, 0, 1, 0], ones, ones, assignment);
        var frames = new List<EtabsTopologyFrame> { beam }; var areas = new List<EtabsTopologyArea>();
        var points = new List<EtabsTopologyPoint> { new("I", [0, 0, 3000]), new("J", [6000, 0, 3000]) };
        var sourcePoints = new List<EtabsSourcePoint>();
        var c = Math.Cos(rotation * Math.PI / 180); var s = Math.Sin(rotation * Math.PI / 180);
        foreach (var (end, x, ordinal) in new[] { ("I", 0d, reverse ? 2 : 1), ("J", 6000d, reverse ? 1 : 2) })
        {
            if (wall)
            {
                points.AddRange(new[] { new EtabsTopologyPoint(end + "0", [x, 0, 0]), new(end + "1", [x, 1000, 0]), new(end + "2", [x, 1000, 3000]) });
                areas.Add(new("W" + end, 1, false, "W200", [end + "0", end + "1", end + "2", end], 1, 1, 200, [0, 0, 0, 0], "centred_uniform_no_overwrites"));
            }
            else
            {
                points.Add(new("C" + end + "base", [x, 0, 0]));
                frames.Add(new("C" + end, 1, "C400x600", 8, 400, 600, ["C" + end + "base", end], 0,
                    [0, c, -s, 0, s, c, 1, 0, 0], ones, ones, assignment with { CardinalPoint = 10 }));
            }
            sourcePoints.Add(new(end, [x, 0, 3000], [x, 0, 3000], [], [],
                [new(2, "B1", ordinal), new(wall ? 5 : 2, (wall ? "W" : "C") + end, wall ? 4 : 2)]));
        }
        var member = new EtabsSourceMember("B1", "L1", 2, "R", 8, "", "C30", null, "C30", 300, 600,
            beam.EndpointNames, [], null, assignment, [], "fixture");
        var source = new EtabsSourceFacts(EtabsSourceQualification.SchemaVersion, EtabsSourceQualification.Units(9, 9),
            new(["B1"], ["Dead"], []), [member], sourcePoints, [], [], [], "authored_geometry_example", []);
        return (source, new(frames, areas, points, []));
    }
}
