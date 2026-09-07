using StructuralEngineering.Codes.IS456;
using StructuralEngineering.Beam;
using StructuralEngineering.Contracts;
using Xunit;

namespace StructuralEngineering.Tests;

public class BaselineServiceabilityTests
{
    private static readonly BarCoordinate[] BottomBars =
    [new("B1", 20, 75, 450, Face.Bottom), new("B2", 20, 225, 450, Face.Bottom)];

    [Fact]
    public void CriticalSurfacePointsIncludeBothEdgesAndTheTwoBarVoronoiCrossing()
    {
        var points = BaselineServiceChecks.CriticalSurfacePoints(
            [new("B1", 20, 50, 450, Face.Bottom), new("B2", 20, 250, 450, Face.Bottom)],
            300, 500, Face.Bottom);

        Assert.Equal([0d, 150d, 300d], points);
    }

    [Fact]
    public void Figure4UsesDerivedStressAndConservativeHigherPercentageBracket()
    {
        var result = BaselineServiceability.Figure4TensionFactor(new(
            "ORDINARY-RECTANGULAR", "B1", "S1", "reinforcement:r1", "uls:S1",
            500, 600, 300, 450, 415));

        Assert.Equal(EngineeringState.Pass, result.Engineering);
        Assert.Equal(0.4444444444444444, result.Outputs!.TensionSteelPercentage, 12);
        Assert.Equal(200.58333333333333, result.Outputs.ServiceSteelStressNPerMm2, 12);
        Assert.Equal(290, result.Outputs.BoundingCurveStressNPerMm2, 12);
        Assert.Equal(.6, result.Outputs.ConservativeUpperPercentageBracket, 12);
        Assert.Equal(.9, result.Outputs.ModificationFactor, 12);
    }

    [Fact]
    public void Figure4DoesNotClampOutsideTheFrozenSourceDomain()
    {
        var result = BaselineServiceability.Figure4TensionFactor(new(
            "ORDINARY-RECTANGULAR", "B1", "S1", "reinforcement:r1", "uls:S1",
            500, 50, 300, 450, 415));

        Assert.Equal(EngineeringState.NotEvaluated, result.Engineering);
        Assert.Contains(result.Diagnostics, item => item.Code == "FIGURE4.OUTSIDE_PROFILE");
    }

    [Fact]
    public void Figure4UsesTheConservativeBoundingCurveForLowActualStress()
    {
        var result = BaselineServiceability.Figure4TensionFactor(new(
            "ORDINARY-RECTANGULAR", "B1", "S1", "reinforcement:r1", "uls:S1",
            50, 600, 300, 450, 415));

        Assert.Equal(EngineeringState.Pass, result.Engineering);
        Assert.Equal(20.05833333333333, result.Outputs!.ServiceSteelStressNPerMm2, 12);
        Assert.Equal(290, result.Outputs.BoundingCurveStressNPerMm2, 12);
        Assert.Equal(.9, result.Outputs.ModificationFactor, 12);
    }

    [Fact]
    public void AnnexFDerivesCrackedSectionAndExactShortTermMeanStrain()
    {
        var result = BaselineServiceability.AnnexFServiceSection(new(
            "ORDINARY-RECTANGULAR", "B1", "S1", "sls:S1", "reinforcement:r1",
            300, 500, 25, 200_000, 415, 20, Face.Bottom, BottomBars, ServiceDurationBasis.ShortTerm));

        Assert.Equal(EngineeringState.Pass, result.Engineering);
        Assert.Equal(107.181839916335, result.Outputs!.NeutralAxisDepthMm, 9);
        Assert.Equal(713871445.743607, result.Outputs.CrackedInertiaMm4, 3);
        Assert.Equal(76.8358307933871, result.Outputs.ServiceSteelStressNPerMm2, 9);
        Assert.Equal(0.000440211651468406, result.Outputs.ElasticSurfaceStrain, 15);
        Assert.Equal(0.000082024972340066, result.Outputs.MeanSurfaceStrain, 15);
        Assert.Equal(1, result.Outputs.TensionConcreteStressNPerMm2, 12);
    }

    [Fact]
    public void AnnexFAllowsOppositeFaceHangersWithoutCompressionCredit()
    {
        var withHangers = BottomBars.Concat([new BarCoordinate("T1", 16, 75, 50, Face.Top)]).ToArray();
        var withoutHangers = BaselineServiceability.AnnexFServiceSection(new(
            "ORDINARY-RECTANGULAR", "B1", "S1", "sls:S1", "reinforcement:r1",
            300, 500, 25, 200_000, 415, 20, Face.Bottom, BottomBars, ServiceDurationBasis.LongTerm));
        var result = BaselineServiceability.AnnexFServiceSection(new(
            "ORDINARY-RECTANGULAR", "B1", "S1", "sls:S1", "reinforcement:r1",
            300, 500, 25, 200_000, 415, 20, Face.Bottom, withHangers, ServiceDurationBasis.LongTerm));

        Assert.Equal(EngineeringState.Pass, result.Engineering);
        Assert.Equal(withoutHangers.Outputs!.NeutralAxisDepthMm, result.Outputs!.NeutralAxisDepthMm, 12);
        Assert.Equal(withoutHangers.Outputs.MeanSurfaceStrain, result.Outputs.MeanSurfaceStrain, 12);
        Assert.Equal(.55, result.Outputs.TensionConcreteStressNPerMm2, 12);
    }

    [Fact]
    public void AnnexFUsesEachActualTensionLayerInCrackedInertia()
    {
        BarCoordinate[] layers =
        [new("B1", 20, 75, 400, Face.Bottom), new("B2", 20, 225, 450, Face.Bottom)];
        var result = BaselineServiceability.AnnexFServiceSection(new(
            "ORDINARY-RECTANGULAR", "B1", "S1", "sls:S1", "reinforcement:r1",
            300, 500, 25, 200_000, 415, 20, Face.Bottom, layers, ServiceDurationBasis.ShortTerm));

        Assert.Equal("annex_f_tension_stiffening", result.Outputs!.StrainMethod);
        Assert.Equal(425, result.Outputs.EffectiveDepthMm, 12);
        Assert.Equal(103.754681560426, result.Outputs.NeutralAxisDepthMm, 9);
        Assert.Equal(633566373.241116, result.Outputs.CrackedInertiaMm4, 3);
        Assert.Equal(81.1268607697569, result.Outputs.ServiceSteelStressNPerMm2, 9);
        Assert.Equal(87.4403271545609, result.Outputs.MaximumTensionSteelStressNPerMm2, 9);
    }

    [Fact]
    public void AnnexFZeroMomentProducesAVisibleZeroDemand()
    {
        var result = BaselineServiceability.AnnexFServiceSection(new(
            "ORDINARY-RECTANGULAR", "B1", "S1", "sls:S1", "reinforcement:r1",
            300, 500, 25, 200_000, 415, 0, Face.Bottom, BottomBars, ServiceDurationBasis.ShortTerm));

        Assert.True(result.Outputs!.ZeroMoment);
        Assert.Equal("zero_service_moment", result.Outputs.StrainMethod);
        Assert.Equal(0, result.Outputs.ServiceSteelStressNPerMm2, 12);
        Assert.Equal(0, result.Outputs.MeanSurfaceStrain, 12);
    }

    [Fact]
    public void AnnexFLowMomentUsesFullyCrackedElasticUpperBoundWhenReductionIsNegative()
    {
        var result = BaselineServiceability.AnnexFServiceSection(new(
            "ORDINARY-RECTANGULAR", "B1", "S1", "sls:S1", "reinforcement:r1",
            300, 500, 25, 200_000, 415, 1, Face.Bottom, BottomBars, ServiceDurationBasis.ShortTerm));

        Assert.Equal("fully_cracked_no_tension_stiffening_upper_bound", result.Outputs!.StrainMethod);
        Assert.False(result.Outputs.ZeroMoment);
        Assert.Equal(result.Outputs.ElasticSurfaceStrain, result.Outputs.MeanSurfaceStrain, 12);
        Assert.Equal(1, result.Outputs.TensionConcreteStressNPerMm2, 12);
    }

    [Fact]
    public void AnnexFRejectsSignedMomentAndPhysicalFaceMismatch()
    {
        var result = BaselineServiceability.AnnexFServiceSection(new(
            "ORDINARY-RECTANGULAR", "B1", "S1", "sls:S1", "reinforcement:r1",
            300, 500, 25, 200_000, 415, -20, Face.Bottom, BottomBars, ServiceDurationBasis.ShortTerm));

        Assert.Equal(ExecutionState.RejectedInput, result.Execution);
        Assert.Contains(result.Diagnostics, item => item.Code == "FACE.MOMENT_MISMATCH");
    }
}
