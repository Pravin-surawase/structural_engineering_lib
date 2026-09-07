namespace StructuralEngineering.Contracts;

public sealed record BaselineDurabilityRequest(string ProfileId, string MemberId, string ReinforcementRevisionId,
    ExposureClass Exposure, double ConcreteStrengthNPerMm2, double NominalCoverMm,
    double SectionWidthMm, double SectionDepthMm, IReadOnlyList<BarCoordinate>? Bars, TransverseLink? Link,
    string CodeDataRevisionId = "is456-baseline-eligibility-v1");
public sealed record BaselineCoverCheck(string ReinforcementId, string Kind, double ActualCoverMm,
    double RequiredCoverMm, bool Passed);
public sealed record BaselineDurabilityOutput(ExposureClass Exposure, double ConcreteStrengthNPerMm2,
    double MinimumConcreteStrengthNPerMm2, double TableNominalCoverMm, IReadOnlyList<BaselineCoverCheck> CoverChecks,
    bool Passed);

public sealed record BaselineLateralStabilityRequest(string ProfileId, string MemberId, string ReinforcementRevisionId,
    double WidthMm, double EffectiveDepthMm, double UnrestrainedLengthMm, string? RestraintEvidenceReference,
    string CodeDataRevisionId = "is456-baseline-eligibility-v1");
public sealed record BaselineLateralStabilityOutput(double UnrestrainedLengthMm, double WidthMm,
    double EffectiveDepthMm, double LimitByWidthMm, double LimitByWidthSquaredOverDepthMm,
    double GoverningLimitMm, string RestraintEvidenceReference, bool Passed);
