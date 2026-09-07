namespace StructuralEngineering.Contracts;

/// <summary>Read-only interpretation request for one captured ETABS source inventory.</summary>
public sealed record EtabsModelInterpretationRequest(
    EtabsContextArtifact Context,
    AnalysisSnapshot? Snapshot = null,
    IReadOnlyList<string>? RequestedBeamIds = null);

public enum EtabsBeamReadinessDisposition
{
    NeedsSupportFacesAndPhysicalSpanMapping,
    RequestedBeamMissing
}

/// <summary>
/// Source-only connectivity. A shared source point proves connectivity only; it does not prove a support,
/// physical span, construction group, release, offset, or fixity.
/// </summary>
public sealed record EtabsSourcePointAdjacency(
    string SourcePointId,
    IReadOnlyList<string> ConnectedFrameIds);

public sealed record EtabsBeamSourceConnectivity(
    string SourceBeamId,
    string StartPointId,
    string EndPointId,
    IReadOnlyList<string> NeighbourBeamIds,
    IReadOnlyList<string> ConnectedColumnIds);

public sealed record EtabsBeamReadiness(
    string SourceBeamId,
    EtabsBeamReadinessDisposition Disposition,
    IReadOnlyList<string> MissingFacts);

public sealed record EtabsModelInterpretation(
    string InterpretationId,
    string ContextArtifactSha256,
    string SourceRevisionId,
    string? SnapshotId,
    string? SnapshotSha256,
    IReadOnlyList<EtabsSourcePointAdjacency> PointAdjacency,
    IReadOnlyList<EtabsBeamSourceConnectivity> Beams,
    IReadOnlyList<EtabsBeamReadiness> BeamReadiness,
    IReadOnlyList<EtabsContextFrame> Frames);
