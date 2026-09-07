using StructuralEngineering.Codes.IS456;
using StructuralEngineering.Contracts;
using Xunit;

namespace StructuralEngineering.Tests;

public class BaselineStirrupTests
{
    private static readonly TransverseLink Link = new("L1", 8, 2, 2, 150, 415, true, 242, 442);
    private static readonly BarCoordinate[] StandardBars =
    [new("TL", 20, 49, 49, Face.Top), new("TR", 20, 251, 49, Face.Top),
     new("BL", 20, 49, 451, Face.Bottom), new("BR", 20, 251, 451, Face.Bottom)];

    [Fact]
    public void StandardClosedLinkReportsTheFrozen135DegreeSixPhiTemplate()
    {
        var result = BaselineStirrupAnchorage.Check(new("P", "M", "R", 300, 500, 25, Link, StandardBars));

        Assert.Equal(EngineeringState.Pass, result.Engineering);
        Assert.Equal(135, result.Outputs!.HookAngleDegrees);
        Assert.Equal(48, result.Outputs.ActualTailLengthMm, 12);
        Assert.Equal(2, result.Outputs.HookTailEnvelopes.Count);
        var hook = result.Outputs.HookTailEnvelopes[0];
        Assert.Equal(49, hook.BendCentreXFromLeftMm, 12);
        Assert.Equal(63.14213562373095, hook.TailStartXFromLeftMm, 10);
        Assert.Equal(97.08326112068522, hook.TailEndXFromLeftMm, 10);
        Assert.Equal(68.79898987322333, hook.TailEndYFromTopMm, 10);
    }

    [Fact]
    public void LinkWithoutActualBarsIsNotEvaluated()
    {
        var result = BaselineStirrupAnchorage.Check(new("P", "M", "R", 300, 500, 25, Link, null));

        Assert.Equal(EngineeringState.NotEvaluated, result.Engineering);
        Assert.Equal(CompletenessState.Partial, result.Completeness);
    }

    [Fact]
    public void InnerBarInHookTailEnvelopeFailsTheTemplate()
    {
        var bars = StandardBars.Concat([new BarCoordinate("INNER", 16, 80, 49, Face.Top)]).ToArray();
        var result = BaselineStirrupAnchorage.Check(new("P", "M", "R", 300, 500, 25, Link, bars));

        Assert.Equal(EngineeringState.Fail, result.Engineering);
        Assert.Contains(result.Diagnostics, diagnostic => diagnostic.Code == "LINK.HOOK_TAIL_CLEARANCE");
    }
}
