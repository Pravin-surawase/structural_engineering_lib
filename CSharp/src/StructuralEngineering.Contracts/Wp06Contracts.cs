namespace StructuralEngineering.Contracts;

public enum CheckScope
{
    Member,
    Span,
    Station,
    Face,
    Axis,
    BarEnd,
    Arrangement
}

public enum SeismicDesignProfile
{
    OrdinaryIs456,
    Is13920_2016
}

public enum BarPathRole
{
    TopLongitudinal,
    BottomLongitudinal,
    SideLeft,
    SideRight,
    TorsionCorner,
    TransverseLink
}

public enum BendKind
{
    StandardBend,
    Hook,
    Transition
}

public enum PathSegmentKind
{
    TangentStraight,
    BendArc
}

public sealed record StructuralUnitBasis(
    string LengthUnit,
    string ForceUnit,
    string MomentUnit,
    string StressUnit);

public sealed record RevisionBinding(
    string BindingId,
    string RevisionId,
    string SourceReference);

public sealed record DesignCriterion(
    string CriterionId,
    double Value,
    string Unit,
    string SourceReference);

public sealed record DesignCheckRule(
    string RuleId,
    string OperationSemanticId,
    CheckScope Scope,
    ApplicabilityState ExpectedApplicability,
    string SourceReference,
    string? CodeDataBindingId = null);

public sealed record BeamProjectDefinition(
    string ProjectId,
    string Name,
    string RevisionId);

public sealed record BeamDesignProfile(
    string ProfileId,
    string RevisionId,
    string DesignCode,
    SeismicDesignProfile SeismicDesignProfile,
    IReadOnlyList<DesignCheckRule> CheckRules,
    IReadOnlyList<DesignCriterion> Criteria);

public sealed record BeamProjectRequest(
    BeamProjectDefinition Project,
    StructuralUnitBasis UnitBasis,
    IReadOnlyList<RevisionBinding> CodeDataRevisions,
    BeamDesignProfile Profile,
    IReadOnlyList<RevisionBinding>? CatalogueRevisions = null);

public sealed record BeamProject(
    string ProjectBasisId,
    BeamProjectDefinition Project,
    StructuralUnitBasis UnitBasis,
    IReadOnlyList<RevisionBinding> CodeDataRevisions,
    IReadOnlyList<RevisionBinding> CatalogueRevisions,
    BeamDesignProfile Profile);

public sealed record MemberScopeInstance(
    string ScopeId,
    CheckScope Scope,
    string SourceRevisionId);

public sealed record EffectiveDepthIteration(
    int IterationNumber,
    string ReinforcementRevisionId,
    double EffectiveDepthMm,
    IReadOnlyList<string> DependentResultIds,
    bool Converged);

public sealed record MemberLeafExpectation(
    string LeafId,
    string RuleId,
    string OperationSemanticId,
    string ScopeId,
    CheckScope Scope,
    ApplicabilityState ExpectedApplicability,
    string? CodeDataRevisionId);

public sealed record MemberLeafEvidence(
    string LeafId,
    string OperationSemanticId,
    string ResultId,
    ExecutionState Execution,
    ApplicabilityState Applicability,
    EngineeringState Engineering,
    CompletenessState Completeness,
    FreshnessState Freshness,
    string CodeDataRevisionId,
    string MethodRevisionId,
    string NormalizedInputId,
    string CalculationId,
    double? RequiredValue = null,
    double? SelectedValue = null,
    double? SuppliedValue = null,
    string? Unit = null,
    double? GoverningUtilization = null,
    IReadOnlyList<string>? DiagnosticCodes = null);

public sealed record MemberLeafQualification(
    MemberLeafExpectation Expectation,
    MemberLeafEvidence? Evidence,
    bool Qualified,
    IReadOnlyList<string> ReasonCodes);

public sealed record MemberDesignRequest(
    BeamProject Project,
    string MemberId,
    string TopologyRevisionId,
    string ActionRevisionId,
    string ReinforcementRevisionId,
    string DesignScopeRevisionId,
    IReadOnlyList<MemberScopeInstance> ScopeInstances,
    IReadOnlyList<EffectiveDepthIteration> DepthIterations,
    IReadOnlyList<MemberLeafEvidence> LeafResults);

public sealed record MemberDesignOutput(
    string ProjectBasisId,
    string ProfileRevisionId,
    string MemberId,
    string TopologyRevisionId,
    string ActionRevisionId,
    string ReinforcementRevisionId,
    string DesignScopeRevisionId,
    IReadOnlyList<MemberLeafExpectation> ExpectedLeaves,
    IReadOnlyList<MemberLeafQualification> LeafQualifications,
    IReadOnlyList<EffectiveDepthIteration> DepthIterations,
    string? GoverningLeafId,
    string? GoverningResultId,
    double? GoverningUtilization,
    bool Qualified);

public sealed record MemberLocalCoordinateSystem(
    string DatumId,
    string StationAxis,
    string SectionHorizontalAxis,
    string SectionVerticalAxis);

public sealed record MemberLocalVector(
    double StationComponent,
    double SectionHorizontalComponent,
    double SectionVerticalComponent);

public sealed record PathPoint(
    double StationXMm,
    double SectionXFromLeftMm,
    double SectionYFromTopMm);

public sealed record PathNode(
    string NodeId,
    PathPoint Point,
    double? BendRadiusMm = null,
    BendKind? BendKind = null);

public sealed record BarPathSeed(
    string BarId,
    string BarMark,
    BarPathRole Role,
    int Layer,
    double DiameterMm,
    double SteelGradeNPerMm2,
    IReadOnlyList<PathNode> Nodes,
    bool Closed = false,
    int BundleSize = 1,
    IReadOnlyList<string>? AnchorageRequirementIds = null,
    IReadOnlyList<string>? SpliceIds = null);

public sealed record BarPathRequest(
    string ProfileId,
    string ProjectBasisId,
    string CriteriaRevisionId,
    string MemberId,
    string PhysicalSpanId,
    string TopologyRevisionId,
    string DetailRevisionId,
    MemberLocalCoordinateSystem CoordinateSystem,
    double MemberStartXMm,
    double MemberEndXMm,
    double SectionWidthMm,
    double SectionDepthMm,
    IReadOnlyList<BarPathSeed> Paths,
    IReadOnlyList<double> StockLengthsMm,
    double GeometryToleranceMm = 1e-6);

public sealed record ResolvedPathSegment(
    string SegmentId,
    PathSegmentKind Kind,
    PathPoint Start,
    PathPoint End,
    double CentrelineLengthMm,
    PathPoint? BendCentre = null,
    double? BendRadiusMm = null,
    double? BendAngleDegrees = null,
    MemberLocalVector? BendPlaneNormal = null,
    double? BendSweepDegrees = null,
    BendKind? BendKind = null);

public sealed record ResolvedBarPath(
    string BarId,
    string BarMark,
    BarPathRole Role,
    int Layer,
    double DiameterMm,
    double SteelGradeNPerMm2,
    int BundleSize,
    bool Closed,
    IReadOnlyList<string> NodeIds,
    IReadOnlyList<ResolvedPathSegment> Segments,
    double DevelopedCentrelineLengthMm,
    double? CompatibleStockLengthMm,
    IReadOnlyList<string> AnchorageRequirementIds,
    IReadOnlyList<string> SpliceIds);

public sealed record BarMarkSummary(
    string BarMark,
    BarPathRole Role,
    double DiameterMm,
    double SteelGradeNPerMm2,
    int BundleSize,
    bool Closed,
    IReadOnlyList<string> BarIds,
    int Count,
    double DevelopedCentrelineLengthMm,
    double? CompatibleStockLengthMm);

public sealed record BarPathOutput(
    string ProfileId,
    string ProjectBasisId,
    string CriteriaRevisionId,
    string MemberId,
    string PhysicalSpanId,
    string TopologyRevisionId,
    string DetailRevisionId,
    MemberLocalCoordinateSystem CoordinateSystem,
    IReadOnlyList<ResolvedBarPath> Paths,
    IReadOnlyList<BarMarkSummary> Marks,
    bool Passed);
