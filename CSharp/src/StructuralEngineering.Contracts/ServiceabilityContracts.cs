namespace StructuralEngineering.Contracts;

public enum LimitSource { Code, Project, Supplied }
public enum DeflectionCriterion { TotalFinal, AfterFinishes }
public enum SupportCondition { Cantilever, SimplySupported, Continuous }
public enum DeflectionMethod { SpanDepthScreening, CalculatedComponents }
public enum ExposureClass { Mild, Moderate, Severe, VerySevere, Extreme }

public sealed record DeflectionLimitRequest(
    string ProfileId,
    double SpanMm,
    DeflectionCriterion Criterion,
    LimitSource SelectedSource = LimitSource.Code,
    double? ProjectLimitMm = null,
    double? SuppliedLimitMm = null,
    string CodeDataRevisionId = "is456-wp04-v1");

public sealed record DeflectionLimitOutput(
    DeflectionCriterion Criterion,
    double LimitMm,
    double CodeLimitMm,
    string SelectedSource);

public sealed record CrackWidthLimitRequest(
    string ProfileId,
    ExposureClass ExposureClass,
    bool CrackingHarmful,
    LimitSource SelectedSource = LimitSource.Code,
    double? ProjectLimitMm = null,
    double? SuppliedLimitMm = null,
    string CodeDataRevisionId = "is456-wp04-v1");

public sealed record CrackWidthLimitOutput(
    ExposureClass ExposureClass,
    bool CrackingHarmful,
    double LimitMm,
    double CodeCeilingMm,
    string SelectedSource);

public sealed record DeflectionScreeningBasis(
    double EffectiveSpanMm,
    double EffectiveDepthMm,
    SupportCondition SupportCondition,
    double TensionSteelModificationFactor,
    double CompressionSteelModificationFactor,
    double FlangedSectionModificationFactor,
    string SpanSupportReference,
    string ModificationFactorsReference);

public sealed record CalculatedDeflectionBasis(
    string ServiceActionSnapshotId,
    IReadOnlyList<string>? TotalServiceActionRowIds,
    IReadOnlyList<string>? SustainedServiceActionRowIds,
    string AnalysisResultId,
    string ReinforcementRevisionId,
    double EffectiveSpanMm,
    double InstantaneousTotalDeflectionMm,
    double InstantaneousSustainedDeflectionMm,
    double CreepMultiplier,
    double ShrinkageDeflectionMm,
    double? FinishInstallationAgeDays,
    double? DeflectionAtFinishInstallationMm,
    double? AgeAtLoadingDays,
    double? AssessmentAgeDays,
    double? SustainedDurationDays,
    double? RelativeHumidityPercent,
    double? NotionalSizeMm,
    string? StiffnessMethod,
    string? CrackingMethod,
    string? CreepMethod,
    string? ShrinkageMethod);

public sealed record DeflectionCheckRequest(
    string ProfileId,
    DeflectionMethod Method,
    DeflectionScreeningBasis? Screening = null,
    CalculatedDeflectionBasis? Calculated = null,
    DeflectionLimitRequest? TotalLimit = null,
    DeflectionLimitRequest? AfterFinishesLimit = null,
    string CodeDataRevisionId = "is456-wp04-v1");

public sealed record DeflectionCheckOutput(
    DeflectionMethod Method,
    string ResultKind,
    bool Passed,
    double? ActualSpanDepthRatio = null,
    double? BasicSpanDepthRatio = null,
    double? AllowableSpanDepthRatio = null,
    double? InstantaneousTotalDeflectionMm = null,
    double? InstantaneousSustainedDeflectionMm = null,
    double? CreepAdditionalDeflectionMm = null,
    double? ShrinkageDeflectionMm = null,
    double? TotalFinalDeflectionMm = null,
    double? DeflectionAtFinishInstallationMm = null,
    double? AfterFinishesDeflectionMm = null,
    double? TotalLimitMm = null,
    double? AfterFinishesLimitMm = null,
    bool? TotalPass = null,
    bool? AfterFinishesPass = null,
    string? ServiceActionSnapshotId = null,
    IReadOnlyList<string>? TotalServiceActionRowIds = null,
    IReadOnlyList<string>? SustainedServiceActionRowIds = null,
    string? AnalysisResultId = null,
    string? ReinforcementRevisionId = null);

public sealed record CrackWidthCheckRequest(
    string ProfileId,
    string MemberId,
    string StationId,
    string ServiceActionRowId,
    string ReinforcementRevisionId,
    double SectionWidthMm,
    double SectionDepthMm,
    double NeutralAxisDepthFromCompressionFaceMm,
    Face TensionFace,
    IReadOnlyList<BarCoordinate>? Bars,
    double SurfacePointXFromLeftMm,
    double ServiceSteelStressNPerMm2,
    double SteelYieldStrengthNPerMm2,
    double SteelModulusNPerMm2,
    double? MeanStrainAtTensionSurface,
    CrackWidthLimitRequest? Limit,
    string CodeDataRevisionId = "is456-wp04-v1");

public sealed record CrackWidthCheckOutput(
    string MemberId,
    string StationId,
    string ServiceActionRowId,
    string ReinforcementRevisionId,
    Face TensionFace,
    string NearestBarId,
    double EffectiveDepthMm,
    double AcrMm,
    double CminMm,
    double NeutralAxisDepthMm,
    double ServiceSteelStressNPerMm2,
    double ElasticSurfaceStrain,
    double MeanStrainAtTensionSurface,
    double Denominator,
    double CalculatedCrackWidthMm,
    double LimitMm,
    double Utilization,
    bool Passed);
