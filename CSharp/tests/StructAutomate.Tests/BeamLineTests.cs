using StructAutomate.Contracts;
using StructAutomate.Engineering;
using Xunit;

namespace StructAutomate.Tests;

public class BeamLineTests
{
    private const double E = 25000;
    private const double I = 3125000000;
    private static void Near(double expected, double actual) => Assert.InRange(actual, expected - 1e-7 * Math.Max(1, Math.Abs(expected)), expected + 1e-7 * Math.Max(1, Math.Abs(expected)));

    [Fact]
    public void SimplySupportedUdlMatchesClosedFormsIncludingInteriorDeflection()
    {
        var result = BeamLineSolver.Solve(new("1.0.0", [new("A",0,0),new("B",6000,0)],
            [new("AB","A","B",E,I,10,[3000])]));
        Near(-30, result.Nodes[0].SupportForceKn);
        Near(-30, result.Nodes[1].SupportForceKn);
        var mid = result.Stations.Single(s => s.FromStartMm == 3000);
        Near(45, mid.SaggingMomentKnM);
        Near(2.16, mid.DisplacementMm); // 5qL^4 / (384EI), independently evaluated.
        Near(0, result.ForceEquilibriumResidualKn);
        Near(0, result.MomentEquilibriumResidualKnM);
    }

    [Fact]
    public void CantileverUdlMatchesTipAndFixedEndClosedForms()
    {
        var result = BeamLineSolver.Solve(new("1.0.0", [new("A",0,0,0),new("B",3000)],
            [new("AB","A","B",E,I,10,[1500])]));
        Near(-30, result.Nodes[0].SupportForceKn);
        Near(-45, result.Nodes[0].SupportMomentKnM);
        Near(1.296, result.Nodes[1].DisplacementMm); // qL^4 / (8EI).
        Near(-45, result.Stations.Single(s => s.FromStartMm == 0).SaggingMomentKnM);
        Near(0, result.Stations.Single(s => s.FromStartMm == 3000).SaggingMomentKnM);
    }

    [Fact]
    public void MidspanPointLoadRetainsBothSidesOfShearJump()
    {
        var result = BeamLineSolver.Solve(new("1.0.0", [new("A",0,0),new("C",3000,ForceKn:60),new("B",6000,0)],
            [new("AC","A","C",E,I,0,[]),new("CB","C","B",E,I,0,[])]));
        Near(3.456, result.Nodes[1].DisplacementMm); // PL^3 / (48EI).
        var sides = result.Stations.Where(s => s.GlobalXMm == 3000).ToArray();
        Assert.Equal(2, sides.Length);
        Near(90, sides[0].SaggingMomentKnM);
        Near(90, sides[1].SaggingMomentKnM);
        Near(30, sides[0].ShearKn);
        Near(-30, sides[1].ShearKn);
    }

    [Fact]
    public void TwoEqualContinuousSpansRetainHoggingSupportMoment()
    {
        var result = BeamLineSolver.Solve(new("1.0.0", [new("A",0,0),new("B",4000,0),new("C",8000,0)],
            [new("AB","A","B",E,I,10,[]),new("BC","B","C",E,I,10,[])]));
        Near(-15, result.Nodes[0].SupportForceKn);
        Near(-50, result.Nodes[1].SupportForceKn);
        Near(-15, result.Nodes[2].SupportForceKn);
        foreach (var s in result.Stations.Where(s => s.GlobalXMm == 4000)) Near(-20, s.SaggingMomentKnM);
    }

    [Fact]
    public void SupportSettlementProducesRigidSlopeWithoutArtificialBending()
    {
        var result = BeamLineSolver.Solve(new("1.0.0", [new("A",0,0),new("B",6000,6)],
            [new("AB","A","B",E,I,0,[3000])]));
        Near(.001, result.Nodes[0].RotationRad);
        Near(.001, result.Nodes[1].RotationRad);
        Near(3, result.Stations.Single(s => s.FromStartMm == 3000).DisplacementMm);
        foreach (var s in result.Stations) Near(0, s.SaggingMomentKnM);
    }

    [Fact]
    public void ElasticSupportsIncludeSettlementInDeflectionAndReaction()
    {
        var result = BeamLineSolver.Solve(new("1.0.0", [new("A",0,VerticalSpringNPerMm:10000),new("B",6000,VerticalSpringNPerMm:10000)],
            [new("AB","A","B",E,I,10,[3000])]));
        Near(3, result.Nodes[0].DisplacementMm);
        Near(-30, result.Nodes[0].SupportForceKn);
        Near(5.16, result.Stations.Single(s => s.FromStartMm == 3000).DisplacementMm);
    }

    [Fact]
    public void UnrestrainedBeamCannotProduceAResult()
    {
        var error = Assert.Throws<InputValidationException>(() => BeamLineSolver.Solve(new("1.0.0", [new("A",0),new("B",6000)],
            [new("AB","A","B",E,I,10,[])])));
        Assert.Equal("unstable_beam", error.Problems[0].Code);
    }
}
