namespace StructuralEngineering.Contracts;

public sealed record BaselineStirrupAnchorageRequest(string ProfileId, string MemberId, string ReinforcementRevisionId,
    double SectionWidthMm, double SectionDepthMm, double NominalCoverMm, TransverseLink? Link,
    IReadOnlyList<BarCoordinate>? Bars, string CodeDataRevisionId = "is456-baseline-stirrup-v1");
public sealed record StirrupHookEnvelope(double BendCentreXFromLeftMm, double BendCentreYFromTopMm,
    double TailStartXFromLeftMm, double TailStartYFromTopMm, double TailEndXFromLeftMm,
    double TailEndYFromTopMm, double MinimumClearanceMm, double MinimumXFromLeftMm,
    double MaximumXFromLeftMm, double MinimumYFromTopMm, double MaximumYFromTopMm);
public sealed record BaselineStirrupAnchorageOutput(string TemplateId, string LinkId, int HookAngleDegrees,
    double ActualTailLengthMm, double RequiredTailLengthMm, double InternalBendRadiusMm,
    IReadOnlyList<string> CornerBarIds, double MaximumCornerBarDiameterMm,
    IReadOnlyList<StirrupHookEnvelope> HookTailEnvelopes, bool Passed);
