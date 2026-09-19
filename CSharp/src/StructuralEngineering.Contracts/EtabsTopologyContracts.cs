namespace StructuralEngineering.Contracts;

public sealed record EtabsTopologyPoint(string Name, IReadOnlyList<double>? GlobalCoordinatesMm);
public sealed record EtabsTopologyFrame(string Name, int? DesignOrientation, string? SectionName,
    int? SectionType, double? WidthMm, double? DepthMm, IReadOnlyList<string> EndpointNames,
    int? CurveType, IReadOnlyList<double>? GlobalTransformation,
    IReadOnlyList<double>? ObjectModifiers, IReadOnlyList<double>? SectionModifiers,
    EtabsSourceAssignments Assignments, string CurveBasis = "explicit_getter");
public sealed record EtabsTopologyArea(string Name, int? DesignOrientation, bool? IsOpening,
    string? PropertyName, IReadOnlyList<string> PointNames, int? WallPropertyType, int? ShellType,
    double? ThicknessMm, IReadOnlyList<double>? ProviderOffsets,
    string PlacementBasis, string? CardinalPoint = null, bool? StiffnessTransform = null);
public sealed record EtabsTopologyGeometry(IReadOnlyList<EtabsTopologyFrame> Frames,
    IReadOnlyList<EtabsTopologyArea> Areas, IReadOnlyList<EtabsTopologyPoint> Points,
    IReadOnlyList<EtabsTopologyPoint> AnalysisPoints);

public sealed record EtabsMemberRoleEvidence(int? DesignOrientation,
    IReadOnlyList<double>? ObjectModifiers, IReadOnlyList<double>? SectionModifiers,
    bool? ZeroMassModifier, bool? ZeroWeightModifier, string State);
public sealed record EtabsSupportEnvelope(string ObjectKind, string ObjectName, string State,
    double? InwardExitMm, IReadOnlyList<double>? FaceGlobalMm,
    IReadOnlyList<EtabsSourceRestriction> Restrictions);
public sealed record EtabsEndpointTopology(string PointName, IReadOnlyList<EtabsSourceConnection> Connections,
    IReadOnlyList<EtabsSupportEnvelope> Envelopes, double? ModelledFaceDistanceMm,
    IReadOnlyList<double>? ModelledFaceGlobalMm, double? ReportedEndOffsetMm,
    double? ReportedMinusModelledMm, string State);
public sealed record EtabsMemberTopology(string Name, EtabsMemberRoleEvidence Role,
    string AxisState, string ReferenceLineBasis, double? ReferenceLengthMm, EtabsEndpointTopology? EndI,
    EtabsEndpointTopology? EndJ, double? ModelledClearLengthMm,
    IReadOnlyList<EtabsSourceRestriction> Restrictions);
public sealed record EtabsTopologyFacts(string ProfileId, IReadOnlyList<EtabsMemberTopology> Members,
    string ClaimBoundary);
