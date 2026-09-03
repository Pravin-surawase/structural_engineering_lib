namespace StructAutomate.Contracts;

// Positive displacement/load is downward; rotation is dw/dx; moment is sagging positive.
// A null prescribed displacement/rotation is free, zero is restrained at zero.
public sealed record BeamNode(
    string Id, double XMm, double? PrescribedDisplacementMm = null,
    double? PrescribedRotationRad = null, double VerticalSpringNPerMm = 0,
    double RotationalSpringNmmPerRad = 0, double ForceKn = 0, double MomentKnM = 0);
public sealed record BeamElement(
    string Id, string StartNodeId, string EndNodeId, double ElasticModulusMpa,
    double SecondMomentMm4, double UniformLoadKnPerM,
    IReadOnlyList<double> StationsFromStartMm);
public sealed record BeamLineRequest(string SchemaVersion, IReadOnlyList<BeamNode> Nodes, IReadOnlyList<BeamElement> Elements);
public sealed record NodeResponse(
    string Id, double DisplacementMm, double RotationRad,
    double SupportForceKn, double SupportMomentKnM);
public sealed record StationResponse(
    string ElementId, double FromStartMm, double GlobalXMm,
    double ShearKn, double SaggingMomentKnM, double DisplacementMm);
public sealed record BeamLineResult(
    IReadOnlyList<NodeResponse> Nodes, IReadOnlyList<StationResponse> Stations,
    double ForceEquilibriumResidualKn, double MomentEquilibriumResidualKnM);
