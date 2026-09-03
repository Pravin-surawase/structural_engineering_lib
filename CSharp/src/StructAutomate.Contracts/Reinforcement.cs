namespace StructAutomate.Contracts;

public enum TensionFace { Top, Bottom }
public sealed record BarPosition(string Id, string LayerId, double DiameterMm, double XFromLeftMm, double YFromTopMm);
public sealed record ReinforcementGeometryRequest(
    string SchemaVersion, double WidthMm, double DepthMm, double NominalCoverMm,
    double LinkDiameterMm, double MinimumClearSpacingMm, TensionFace TensionFace,
    IReadOnlyList<BarPosition> TensionBars);
public sealed record ReinforcementGeometryResult(
    double AreaMm2, double CentroidXFromLeftMm, double CentroidYFromTopMm,
    double EffectiveDepthMm, double? MinimumActualClearSpacingMm,
    IReadOnlyList<InputProblem> FitProblems)
{
    public bool Fits => FitProblems.Count == 0;
}

// A fabrication path is already resolved to tangent-to-tangent straights and centreline arcs.
// Development, hooks and laps are explicit path pieces, never implicit allowances.
public sealed record StraightPiece(string Purpose, double TangentLengthMm);
public sealed record BendPiece(string Purpose, double AngleDegrees, double InternalRadiusMm);
public sealed record BarPath(
    string Mark, double DiameterMm, int Count, IReadOnlyList<StraightPiece> Straights,
    IReadOnlyList<BendPiece> Bends);
