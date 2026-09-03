namespace StructuralEngineering.Contracts;

public enum ExecutionState { Completed, RejectedInput, NotRun, SoftwareError, Cancelled }
public enum ApplicabilityState { Applicable, NotApplicable, Unknown }
public enum EngineeringState { Pass, Fail, NotEvaluated }
public enum CompletenessState { CompleteForScope, Partial }
public enum FreshnessState { Current, Stale, Unbound }
public enum ApprovalState { Unreviewed, Checked, Approved, Rejected }
public enum Face { Top, Bottom }
public enum SectionKind { Rectangular, TBeam, LBeam }

public sealed record Diagnostic(
    string Code,
    string Severity,
    string Message,
    string OperationSemanticId,
    string? FieldOrLocation = null,
    string Source = "operation",
    string? Remediation = null);

public sealed record Provenance(
    string CodeDataRevisionId,
    string MethodRevisionId,
    IReadOnlyList<string> SourceReferences);

public sealed record EffectiveValue(
    object? Value,
    string State = "supplied",
    string Origin = "caller",
    IReadOnlyList<string>? Dependencies = null,
    string? Rule = null);

public sealed record ResultEnvelope<TOutput>(
    string SchemaVersion,
    string OperationSemanticId,
    ExecutionState Execution,
    ApplicabilityState Applicability,
    EngineeringState Engineering,
    CompletenessState Completeness,
    FreshnessState Freshness,
    ApprovalState Approval,
    IReadOnlyDictionary<string, EffectiveValue> EffectiveInputs,
    TOutput? Outputs,
    IReadOnlyList<Diagnostic> Diagnostics,
    Provenance Provenance,
    string NormalizedInputId,
    string CalculationId,
    string ResultId);

public sealed record BarCoordinate(
    string BarId,
    double DiameterMm,
    double XFromLeftMm,
    double YFromTopMm,
    Face Face,
    int Layer = 1);

public sealed record GeometryRequest(
    string ProfileId,
    double WidthMm,
    double DepthMm,
    double NominalCoverMm,
    double LinkDiameterMm,
    double MinimumClearSpacingMm,
    IReadOnlyList<BarCoordinate> Bars,
    string CodeDataRevisionId = "is456-wp01-v1");

public sealed record FaceGeometryOutput(
    Face Face,
    double AreaMm2,
    double CentroidXFromLeftMm,
    double CentroidYFromTopMm,
    double EffectiveDepthMm,
    IReadOnlyList<string> BarIds);

public sealed record GeometryOutput(
    IReadOnlyDictionary<string, FaceGeometryOutput> Faces,
    double? MinimumClearSpacingMm,
    IReadOnlyList<string>? GoverningSpacingPair,
    int BarCount);

public sealed record BarAreaRequest(
    string ProfileId,
    double DiameterMm,
    string CodeDataRevisionId = "is456-wp01-v1");

public sealed record MassPerLengthRequest(
    string ProfileId,
    double DiameterMm,
    double DensityKgPerM3,
    string CodeDataRevisionId = "is456-wp01-v1");

public sealed record ScalarOutput(double Value, string Unit);

public sealed record FlexuralCapacityRequest(
    string ProfileId,
    SectionKind SectionKind,
    double WebWidthMm,
    double DepthMm,
    double ConcreteStrengthNPerMm2,
    double SteelYieldStrengthNPerMm2,
    IReadOnlyList<BarCoordinate> Bars,
    Face TensionFace,
    double? FlangeWidthMm = null,
    double? FlangeThicknessMm = null,
    double AxialForceKn = 0,
    string CodeDataRevisionId = "is456-wp01-v1");

public sealed record FlexuralCapacityOutput(
    Face TensionFace,
    double CapacityKnM,
    double EquilibriumNeutralAxisDepthMm,
    double LimitingNeutralAxisDepthMm,
    double CapacityNeutralAxisDepthMm,
    double EffectiveDepthMm,
    double? CompressionSteelDepthMm,
    double TensionSteelAreaMm2,
    double CompressionSteelAreaMm2,
    double MinimumTensionSteelAreaMm2,
    double MaximumTotalSteelAreaMm2,
    double ConcreteCompressionForceN,
    double CompressionSteelForceN,
    bool IsOverReinforced,
    bool UsesCompressionFlange);

public sealed record FlexureCheckRequest(
    FlexuralCapacityRequest Capacity,
    double? PositiveDesignMomentKnM = null,
    double? NegativeDesignMomentKnM = null);

public sealed record FlexureSignCheck(
    string Sign,
    Face TensionFace,
    double DemandKnM,
    double CapacityKnM,
    double Utilization,
    bool MinimumSteelPass,
    bool MaximumSteelPass,
    string CapacityResultId,
    EngineeringState Engineering);

public sealed record FlexureCheckOutput(
    IReadOnlyList<FlexureSignCheck> Checks,
    double GoverningUtilization);
