namespace StructuralEngineering.Contracts;

public sealed record BaselineRequiredSteelRequest(
    string ProfileId, string MemberId, string ActionRowId, Face TensionFace,
    double WidthMm, double EffectiveDepthMm, double ConcreteStrengthNPerMm2,
    double SteelYieldStrengthNPerMm2, double MomentMagnitudeKnM);

public sealed record BaselineRequiredSteelOutput(
    string MemberId, string ActionRowId, Face TensionFace, double EffectiveDepthMm,
    double RequiredAreaMm2, double MinimumAreaMm2, double LimitingMomentKnM,
    double NeutralAxisDepthMm);
