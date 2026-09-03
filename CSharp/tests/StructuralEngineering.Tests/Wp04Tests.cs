using StructuralEngineering.Codes.IS456;
using StructuralEngineering.Contracts;
using Xunit;

namespace StructuralEngineering.Tests;

public class Wp04Tests
{
    private static DeflectionLimitRequest TotalLimit() =>
        new("IS456-WP04", 6000, DeflectionCriterion.TotalFinal);

    private static DeflectionLimitRequest AfterFinishesLimit() =>
        new("IS456-WP04", 6000, DeflectionCriterion.AfterFinishes);

    private static CalculatedDeflectionBasis CalculatedBasis(
        double? durationDays = 1825) =>
        new(
            "snapshot:SLS-1",
            ["row:total"],
            ["row:sustained"],
            "analysis:SLS-1",
            "reinforcement:R1",
            6000,
            8,
            5,
            1.2,
            1,
            90,
            4,
            28,
            1853,
            durationDays,
            60,
            150,
            "effective-inertia:reviewed",
            "cracked-section:reviewed",
            "creep-factor:reviewed",
            "shrinkage-curvature:reviewed");

    private static DeflectionCheckRequest CalculatedRequest(
        CalculatedDeflectionBasis basis) =>
        new(
            "IS456-WP04",
            DeflectionMethod.CalculatedComponents,
            Calculated: basis,
            TotalLimit: TotalLimit(),
            AfterFinishesLimit: AfterFinishesLimit());

    private static CrackWidthCheckRequest CrackRequest(
        double leftX = 75,
        double rightX = 225,
        ExposureClass exposure = ExposureClass.Mild,
        double? meanStrain = 0.0006) =>
        new(
            "IS456-WP04",
            "M1",
            "S1@2500",
            "action:SLS-1",
            "reinforcement:R1",
            300,
            500,
            200,
            Face.Bottom,
            [
                new("BL", 20, leftX, 450, Face.Bottom),
                new("BR", 20, rightX, 450, Face.Bottom)
            ],
            150,
            200,
            415,
            200_000,
            meanStrain,
            new("IS456-WP04", exposure, exposure != ExposureClass.Mild));

    [Fact]
    public void DeflectionLimitsDistinguishCriteriaAndRejectConflictingSource()
    {
        var total = Serviceability.DeflectionLimit(TotalLimit());
        var afterFinishes = Serviceability.DeflectionLimit(AfterFinishesLimit());
        var conflict = Serviceability.DeflectionLimit(
            new(
                "IS456-WP04",
                6000,
                DeflectionCriterion.TotalFinal,
                LimitSource.Code,
                ProjectLimitMm: 20));

        Assert.Equal(24, total.Outputs!.LimitMm);
        Assert.Equal(17.142857142857142, afterFinishes.Outputs!.LimitMm, 12);
        Assert.Equal(ExecutionState.RejectedInput, conflict.Execution);
        Assert.Equal("INPUT.CONFLICT", conflict.Diagnostics[0].Code);
    }

    [Fact]
    public void LimitSelectionRejectsInvalidEnumAndWeakenedCrackCeiling()
    {
        var invalidSource = Serviceability.DeflectionLimit(
            TotalLimit() with { SelectedSource = (LimitSource)999 });
        var weakenedCrackLimit = Serviceability.CrackWidthLimit(
            new(
                "IS456-WP04",
                ExposureClass.VerySevere,
                true,
                LimitSource.Project,
                ProjectLimitMm: 0.2));

        Assert.Equal("INPUT.ENUM", invalidSource.Diagnostics[0].Code);
        Assert.Equal(ExecutionState.RejectedInput, weakenedCrackLimit.Execution);
        Assert.Equal("LIMIT.EXCEEDS_CODE", weakenedCrackLimit.Diagnostics[0].Code);
    }

    [Fact]
    public void SpanDepthScreeningIsLabeledAndUsesExplicitFactors()
    {
        var result = Serviceability.CheckDeflection(
            new(
                "IS456-WP04",
                DeflectionMethod.SpanDepthScreening,
                new(
                    5000,
                    500,
                    SupportCondition.SimplySupported,
                    1.2,
                    1.1,
                    1,
                    "topology:S1",
                    "reviewed-figure-factors:1")));

        Assert.Equal(EngineeringState.Pass, result.Engineering);
        Assert.Equal(
            "screening_not_calculated_displacement",
            result.Outputs!.ResultKind);
        Assert.Equal(10, result.Outputs.ActualSpanDepthRatio);
        Assert.Equal(26.4, result.Outputs.AllowableSpanDepthRatio!.Value, 12);
        Assert.Null(result.Outputs.TotalFinalDeflectionMm);
    }

    [Fact]
    public void ScreeningRejectsInvalidSupportAndCalculatedLimitInputs()
    {
        var basis = new DeflectionScreeningBasis(
            5000,
            500,
            (SupportCondition)999,
            1.2,
            1.1,
            1,
            "topology:S1",
            "factors:1");
        var invalidSupport = Serviceability.CheckDeflection(
            new(
                "IS456-WP04",
                DeflectionMethod.SpanDepthScreening,
                basis));
        var branchConflict = Serviceability.CheckDeflection(
            new(
                "IS456-WP04",
                DeflectionMethod.SpanDepthScreening,
                basis with { SupportCondition = SupportCondition.SimplySupported },
                TotalLimit: TotalLimit()));

        Assert.Equal("SCREENING.INVALID", invalidSupport.Diagnostics[0].Code);
        Assert.Equal("INPUT.CONFLICT", branchConflict.Diagnostics[0].Code);
    }

    [Fact]
    public void CalculatedDeflectionRetainsComponentsAndEvidenceIdentities()
    {
        var result = Serviceability.CheckDeflection(
            CalculatedRequest(CalculatedBasis()));

        Assert.Equal(EngineeringState.Pass, result.Engineering);
        Assert.Equal(8, result.Outputs!.InstantaneousTotalDeflectionMm);
        Assert.Equal(5, result.Outputs.InstantaneousSustainedDeflectionMm);
        Assert.Equal(6, result.Outputs.CreepAdditionalDeflectionMm);
        Assert.Equal(1, result.Outputs.ShrinkageDeflectionMm);
        Assert.Equal(15, result.Outputs.TotalFinalDeflectionMm);
        Assert.Equal(4, result.Outputs.DeflectionAtFinishInstallationMm);
        Assert.Equal(11, result.Outputs.AfterFinishesDeflectionMm);
        Assert.Equal(24, result.Outputs.TotalLimitMm);
        Assert.Equal(
            17.142857142857142,
            result.Outputs.AfterFinishesLimitMm!.Value,
            12);
        Assert.True(result.Outputs.TotalPass);
        Assert.True(result.Outputs.AfterFinishesPass);
        Assert.Equal("snapshot:SLS-1", result.Outputs.ServiceActionSnapshotId);
        Assert.Equal(["row:total"], result.Outputs.TotalServiceActionRowIds);
        Assert.Equal(["row:sustained"], result.Outputs.SustainedServiceActionRowIds);
        Assert.Equal("analysis:SLS-1", result.Outputs.AnalysisResultId);
        Assert.Equal("reinforcement:R1", result.Outputs.ReinforcementRevisionId);
    }

    [Fact]
    public void MissingCalculatedDurationIsNotEvaluated()
    {
        var result = Serviceability.CheckDeflection(
            CalculatedRequest(CalculatedBasis(durationDays: null)));

        Assert.Equal(ExecutionState.Completed, result.Execution);
        Assert.Equal(EngineeringState.NotEvaluated, result.Engineering);
        Assert.Equal(CompletenessState.Partial, result.Completeness);
        Assert.Equal("EVIDENCE.REQUIRED", result.Diagnostics[0].Code);
    }

    [Fact]
    public void AnnexFUsesActualBarSurfacesAndMatchesReferenceVector()
    {
        var result = Serviceability.CheckCrackWidth(CrackRequest());

        Assert.Equal(EngineeringState.Pass, result.Engineering);
        Assert.Equal(450, result.Outputs!.EffectiveDepthMm, 12);
        Assert.Equal(40, result.Outputs.CminMm, 12);
        Assert.Equal(80.13878188659973, result.Outputs.AcrMm, 12);
        Assert.Equal(1.2675918792439982, result.Outputs.Denominator, 12);
        Assert.Equal(
            0.11379830508373975,
            result.Outputs.CalculatedCrackWidthMm,
            12);
        Assert.Equal("BL", result.Outputs.NearestBarId);
    }

    [Fact]
    public void CrackWidthRespondsToArrangementExposureAndMissingEvidence()
    {
        var wide = Serviceability.CheckCrackWidth(CrackRequest());
        var close = Serviceability.CheckCrackWidth(
            CrackRequest(leftX: 130, rightX: 170));
        var aggressive = Serviceability.CheckCrackWidth(
            CrackRequest(exposure: ExposureClass.VerySevere));
        var missingBars = Serviceability.CheckCrackWidth(
            CrackRequest() with { Bars = [] });
        var missingStrain = Serviceability.CheckCrackWidth(
            CrackRequest(meanStrain: null));

        Assert.True(
            wide.Outputs!.CalculatedCrackWidthMm >
            close.Outputs!.CalculatedCrackWidthMm);
        Assert.Equal(
            0.0769568940449222,
            close.Outputs.CalculatedCrackWidthMm,
            12);
        Assert.Equal(EngineeringState.Fail, aggressive.Engineering);
        Assert.Equal(0.1, aggressive.Outputs!.LimitMm);
        Assert.Equal(
            "CRACK_WIDTH.LIMIT_EXCEEDED",
            aggressive.Diagnostics[0].Code);
        Assert.Equal(EngineeringState.NotEvaluated, missingBars.Engineering);
        Assert.Equal(EngineeringState.NotEvaluated, missingStrain.Engineering);
    }

    [Fact]
    public void CrackWidthRejectsInvalidPhysicalFaceIdentity()
    {
        var invalidTensionFace = Serviceability.CheckCrackWidth(
            CrackRequest() with { TensionFace = (Face)999 });
        var bars = CrackRequest().Bars!.ToArray();
        bars[0] = bars[0] with { Face = (Face)999 };
        var invalidBarFace = Serviceability.CheckCrackWidth(
            CrackRequest() with { Bars = bars });

        Assert.Equal("INPUT.INVALID", invalidTensionFace.Diagnostics[0].Code);
        Assert.Equal("BAR.GEOMETRY", invalidBarFace.Diagnostics[0].Code);
    }
}
