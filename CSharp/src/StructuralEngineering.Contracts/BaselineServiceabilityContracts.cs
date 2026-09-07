namespace StructuralEngineering.Contracts;

public enum ServiceDurationBasis { ShortTerm, LongTerm }

public sealed record Figure4TensionFactorRequest(
    string ProfileId,
    string MemberId,
    string StationId,
    string ReinforcementRevisionId,
    string UlsActionRowId,
    double RequiredTensionAreaMm2,
    double ProvidedTensionAreaMm2,
    double SectionWidthMm,
    double EffectiveDepthMm,
    double SteelYieldStrengthNPerMm2,
    string CodeDataRevisionId = "is456-baseline-serviceability-v1");

public sealed record Figure4TensionFactorOutput(
    string MemberId,
    string StationId,
    string ReinforcementRevisionId,
    string UlsActionRowId,
    double TensionSteelPercentage,
    double ServiceSteelStressNPerMm2,
    double BoundingCurveStressNPerMm2,
    double ModificationFactor,
    double ConservativeUpperPercentageBracket,
    string CurveSelectionMethod);

public sealed record AnnexFServiceSectionRequest(
    string ProfileId,
    string MemberId,
    string StationId,
    string ServiceActionRowId,
    string ReinforcementRevisionId,
    double SectionWidthMm,
    double SectionDepthMm,
    double ConcreteStrengthNPerMm2,
    double SteelModulusNPerMm2,
    double SteelYieldStrengthNPerMm2,
    double SignedServiceMomentKnM,
    Face TensionFace,
    IReadOnlyList<BarCoordinate>? Bars,
    ServiceDurationBasis DurationBasis,
    string CodeDataRevisionId = "is456-baseline-serviceability-v1");

public sealed record AnnexFServiceSectionOutput(
    string MemberId,
    string StationId,
    string ServiceActionRowId,
    string ReinforcementRevisionId,
    Face TensionFace,
    double TensionSteelAreaMm2,
    double EffectiveDepthMm,
    double ConcreteModulusNPerMm2,
    double ModularRatio,
    double NeutralAxisDepthMm,
    double CrackedInertiaMm4,
    double ServiceSteelStressNPerMm2,
    double MaximumTensionSteelStressNPerMm2,
    double ElasticSurfaceStrain,
    double MeanSurfaceStrain,
    double TensionConcreteStressNPerMm2,
    bool ZeroMoment,
    string StrainMethod);
