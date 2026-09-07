using StructuralEngineering.Codes.IS456;
using StructuralEngineering.Contracts;
using Xunit;

namespace StructuralEngineering.Tests;

public class BaselineEligibilityTests
{
    private static readonly BarCoordinate[] Bars =
    [new("B1", 20, 50, 450, Face.Bottom), new("B2", 20, 250, 450, Face.Bottom),
     new("T1", 20, 50, 50, Face.Top), new("T2", 20, 250, 50, Face.Top)];
    private static readonly TransverseLink Link = new("L1", 8, 2, 2, 150, 415, true, 252, 452);

    [Fact]
    public void DurabilityReportsBothGradeAndActualOuterLinkCoverFailure()
    {
        var result = BaselineEligibility.CheckDurability(new("P", "M", "R", ExposureClass.Moderate,
            20, 20, 300, 500, Bars, Link));

        Assert.Equal(EngineeringState.Fail, result.Engineering);
        Assert.Equal(25, result.Outputs!.MinimumConcreteStrengthNPerMm2);
        Assert.Equal(30, result.Outputs.TableNominalCoverMm);
        Assert.Equal(20, result.Outputs.CoverChecks.Single(check => check.ReinforcementId == "L1").ActualCoverMm, 12);
        Assert.Contains(result.Diagnostics, diagnostic => diagnostic.Code == "DURABILITY.GRADE");
        Assert.Contains(result.Diagnostics, diagnostic => diagnostic.Code == "DURABILITY.COVER");
    }

    [Fact]
    public void LateralStabilityUsesTheLesserClause233Limit()
    {
        var result = BaselineEligibility.CheckLateralStability(new("P", "M", "R", 300, 450, 4500, "restraint:r1"));

        Assert.Equal(18_000, result.Outputs!.LimitByWidthMm, 12);
        Assert.Equal(50_000, result.Outputs.LimitByWidthSquaredOverDepthMm, 12);
        Assert.Equal(18_000, result.Outputs.GoverningLimitMm, 12);
        Assert.Equal(EngineeringState.Pass, result.Engineering);
    }

    [Fact]
    public void LateralStabilityRequiresPhysicalRestraintEvidence()
    {
        var result = BaselineEligibility.CheckLateralStability(new("P", "M", "R", 300, 450, 4500, null));

        Assert.Equal(EngineeringState.NotEvaluated, result.Engineering);
        Assert.Equal(CompletenessState.Partial, result.Completeness);
    }
}
