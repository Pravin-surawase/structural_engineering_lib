namespace StructuralEngineering.Contracts;

/// <summary>Exact read-only source scope; these identities never select or alter ETABS results.</summary>
public sealed record EtabsSourceScope(IReadOnlyList<string> FrameNames,
    IReadOnlyList<string> CaseNames, IReadOnlyList<string> CombinationNames);

public sealed record EtabsSourceRestriction(string Code, string Subject, string Message);
public sealed record EtabsSourceUnitBasis(int PresentUnits, int DatabaseUnits,
    string NativeLength, string NativeForce, double LengthToMm, double StressToNPerMm2);
public sealed record EtabsSourceConnection(int ObjectType, string ObjectName, int PointNumber);
public sealed record EtabsSourcePoint(string Name, IReadOnlyList<double>? NativeGlobalCoordinates,
    IReadOnlyList<double>? GlobalCoordinatesMm, IReadOnlyList<bool>? LocalRestraints,
    IReadOnlyList<double>? GlobalTransformation, IReadOnlyList<EtabsSourceConnection> Connections);
public sealed record EtabsSourceMaterial(string Name, int? MaterialType, double? NativeElasticModulus,
    double? ElasticModulusNPerMm2, double? NativeConcreteFc, double? ConcreteFcNPerMm2, bool? IsLightweight);
public sealed record EtabsSourceElement(string Name, string? ReverseObjectName, int? ReverseObjectType,
    double? ProviderRdi, double? ProviderRdj, string? AnalysisPointI, string? AnalysisPointJ,
    IReadOnlyList<double>? GlobalTransformation, string MappingSource);
public sealed record EtabsSourceStations(int Type, double NativeMaximumSpacing, double MaximumSpacingMm,
    int MinimumStations, bool OmitElementEnds, bool OmitPointLoads);
public sealed record EtabsSourceAssignments(bool? AutomaticEndOffsets, double? EndOffsetIMm,
    double? EndOffsetJMm, double? RigidZoneFactor, int? CardinalPoint, bool? Mirror2, bool? Mirror3,
    bool? StiffnessTransform, string? InsertionCoordinateSystem,
    IReadOnlyList<double>? InsertionOffsetIMm, IReadOnlyList<double>? InsertionOffsetJMm,
    IReadOnlyList<bool>? ReleasesI, IReadOnlyList<bool>? ReleasesJ,
    IReadOnlyList<double>? NativePartialFixityI, IReadOnlyList<double>? NativePartialFixityJ,
    double? LocalAxisAngleDegrees, bool? AdvancedLocalAxes);
public sealed record EtabsSourceMember(string Name, string? Story, int? DesignOrientation,
    string? SectionName, int? SectionType, string? AutoSelectList,
    string? SectionMaterial, string? MaterialOverwrite, string? EffectiveMaterial,
    double? WidthMm, double? DepthMm, IReadOnlyList<string> EndpointNames,
    IReadOnlyList<EtabsSourceElement> Elements, EtabsSourceStations? Stations,
    EtabsSourceAssignments Assignments, IReadOnlyList<EtabsSourceRestriction> Restrictions,
    string MaterialResolutionBasis);

/// <summary>Factors and provider types are retained, including unsupported nodes; no result synthesis.</summary>
public sealed record EtabsSourceLoadTerm(string Kind, string Name, double Factor);
public sealed record EtabsSourceLoadNode(string Kind, string Name, int? ProviderType,
    int? CaseStatus, bool? SelectedForOutput, string? InitialCase,
    IReadOnlyList<EtabsSourceLoadTerm> Terms, IReadOnlyList<EtabsSourceRestriction> Restrictions,
    double? SelfWeightMultiplier = null, int? CaseSubtype = null);
public sealed record EtabsSourceLoadClosure(string Kind, string Name, string State,
    IReadOnlyList<string> DependencyIds, IReadOnlyList<EtabsSourceRestriction> Restrictions);
public sealed record EtabsSourceTableSummary(string Key, int Version, int SourceRecords,
    int AcceptedRows, int ContextOnlyRows);
public sealed record EtabsSourceFacts(string SchemaVersion, EtabsSourceUnitBasis Units,
    EtabsSourceScope Scope, IReadOnlyList<EtabsSourceMember> Members,
    IReadOnlyList<EtabsSourcePoint> Points, IReadOnlyList<EtabsSourceMaterial> Materials,
    IReadOnlyList<EtabsSourceLoadNode> LoadNodes, IReadOnlyList<EtabsSourceLoadClosure> SelectedLoads,
    string ClaimBoundary, IReadOnlyList<EtabsSourceTableSummary> Tables);
