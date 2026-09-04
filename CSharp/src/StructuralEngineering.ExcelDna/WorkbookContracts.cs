using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.ExcelDna;

/// <summary>Host-free contract for the versioned workbook tables owned by WP09.</summary>
public static class WorkbookContract
{
    public const string TemplateId = "structural-excel-workbook/v1";
    public const string CalculationEngineRevision = "structural-engineering-excel-dna/wp09-r1";
    public const string ProjectTable = "StructuralProject";
    public const string MembersTable = "StructuralMembers";
    public const string OperationsTable = "StructuralOperations";
    public const string ResultsTable = "StructuralResults";
    public const string FreshnessTable = "StructuralFreshness";
    public const string ReceiptTable = "StructuralReceipts";
    public const string BenchmarkTable = "StructuralBenchmark";
    public const string HostEffectsTable = "StructuralHostEffects";

    internal static readonly JsonSerializerOptions Json = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
        PropertyNameCaseInsensitive = false,
        UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow,
        RespectRequiredConstructorParameters = true,
        RespectNullableAnnotations = true,
        Converters = { new JsonStringEnumConverter(JsonNamingPolicy.SnakeCaseLower, false) }
    };

    public static string HashBytes(byte[] bytes) =>
        Convert.ToHexStringLower(SHA256.HashData(bytes));

    public static string HashJson<T>(T value) => HashBytes(JsonSerializer.SerializeToUtf8Bytes(value, Json));

    public static string HashTables(IEnumerable<WorkbookTable> tables) =>
        HashJson(tables.OrderBy(table => table.TableId, StringComparer.Ordinal).ToArray());
}

public enum WorkbookCommandKind { CreateValidate, Calculate, Optimize, ExportPackage, MeasureDiagnose }
public enum WorkbookReceiptState { Completed, RejectedInput, Cancelled, Restored, RestorationUnverified, NotRun }

public sealed record WorkbookOperationRow(
    string RowId,
    string OperationSemanticId,
    string RequestJson,
    string? TableId = null,
    string? RuleId = null,
    string? ScopeId = null,
    CheckScope? Scope = null,
    ApplicabilityState? ExpectedApplicability = null,
    string? CodeDataBindingId = null);

/// <summary>AO17 seed; evidence identifiers and states are always derived from dispatched leaf envelopes.</summary>
public sealed record WorkbookMemberDesignSeed(
    string MemberId,
    string TopologyRevisionId,
    string ActionRevisionId,
    string ReinforcementRevisionId,
    string DesignScopeRevisionId,
    IReadOnlyList<MemberScopeInstance> ScopeInstances,
    IReadOnlyList<WorkbookEffectiveDepthSeed> DepthIterations);

/// <summary>
/// Caller-owned physical iteration data. Dependent result identifiers are deliberately
/// absent and are bound to the just-dispatched applicable leaf envelopes by the adapter.
/// </summary>
public sealed record WorkbookEffectiveDepthSeed(
    int IterationNumber,
    string ReinforcementRevisionId,
    double EffectiveDepthMm,
    bool Converged);

/// <summary>
/// Compact, user-authored AO18 input. The reader expands each declared transverse
/// placement into the native BarPathRequest before dispatch; no resolved output is
/// stored in a workbook cell.
/// </summary>
public sealed record WorkbookBarPathSeed(
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
    IReadOnlyList<BarPathSeed> LongitudinalPaths,
    WorkbookTransverseLinkPattern? TransverseLinks,
    IReadOnlyList<double> StockLengthsMm,
    double GeometryToleranceMm = 1e-6);

public sealed record WorkbookTransverseLinkPattern(
    string BarMark,
    int Layer,
    double DiameterMm,
    double SteelGradeNPerMm2,
    double StartStationXMm,
    double EndStationXMm,
    double SpacingMm,
    double LeftXFromLeftMm,
    double RightXFromLeftMm,
    double TopYFromTopMm,
    double BottomYFromTopMm,
    double BendRadiusMm,
    BendKind BendKind = BendKind.StandardBend);

public sealed record WorkbookBbsSeed(
    string ProfileId, string ProjectBasisId, string MemberId, string DetailRevisionId,
    ShapeConvention ShapeConvention, CuttingStockPolicy StockPolicy,
    double SteelDensityKgPerM3, IReadOnlyList<SpliceRecord>? SpliceRecords = null,
    IReadOnlyList<LinkPlacementZone>? LinkZones = null, double StationToleranceMm = 1e-6);

public sealed record WorkbookQuantitySeed(
    string ProfileId, string ProjectBasisId, string MemberId, string DetailRevisionId,
    string ConcreteOverlapPolicyId, string FormworkMeasurementPolicyId,
    IReadOnlyList<ConcreteNetSegment> ConcreteSegments,
    IReadOnlyList<FormworkContactFace> FormworkFaces);

public sealed record WorkbookCostSeed(
    string ProfileId, string ProjectBasisId, string MemberId, string DetailRevisionId,
    MeasuredRateProfile RateProfile);

public sealed record WorkbookCalculationPackageSeed(
    CalculationPackageMetadata Metadata, CalculationPackageProfile PackageProfile,
    IReadOnlyList<string> Assumptions, IReadOnlyList<WorkbookCalculationTraceSeed> Traces,
    IReadOnlyList<DrawingView> Drawings, IReadOnlyList<string> Limitations,
    IReadOnlyList<HumanAction>? HumanActions = null);

/// <summary>Stable trace description; result values and governing state come from AO17.</summary>
public sealed record WorkbookCalculationTraceSeed(
    string TraceId,
    string LeafId,
    string RuleReference,
    string FormulaReference,
    string NormalizedSubstitution);

/// <summary>
/// Fixed-action workbook search seed. WP09 binds the one supplied current physical
/// candidate to the just-calculated member and quantity outputs; coupled candidates
/// remain outside the standalone workbook boundary.
/// </summary>
public sealed record WorkbookOptimizationSeed(
    string SearchId,
    DiscreteCandidateDomain Domain,
    CandidateObjectiveProfile ObjectiveProfile,
    int EvaluationBudget,
    SearchStopReason StopReason = SearchStopReason.Completed);

/// <summary>
/// Values are immutable workbook-table snapshots. Operation rows include topology and
/// leaf checks; the member request remains explicit so AO17 derives its own leaf set.
/// </summary>
public sealed record WorkbookInputSnapshot(
    string TemplateId,
    string WorkbookId,
    string ProjectId,
    string MemberId,
    string RequestId,
    string ProjectRequestJson,
    IReadOnlyList<WorkbookOperationRow> TopologyRows,
    IReadOnlyList<WorkbookOperationRow> LeafOperationRows,
    string? MemberDesignRequestJson = null,
    string? BarPathRequestJson = null,
    string? BbsRequestJson = null,
    string? QuantityRequestJson = null,
    string? CostRequestJson = null,
    string? CalculationPackageRequestJson = null,
    string? OptimizationRequestJson = null,
    WorkbookBenchmarkRequest? Benchmark = null)
{
    public IReadOnlyList<WorkbookOperationRow> AllOperationRows =>
        TopologyRows.Concat(LeafOperationRows).ToArray();
}

public sealed record WorkbookDiagnostic(
    string Code,
    string Severity,
    string Message,
    string? RowId = null,
    string? Field = null);

public sealed record WorkbookOperationResult(
    string RowId,
    string OperationSemanticId,
    ExecutionState Execution,
    ApplicabilityState Applicability,
    EngineeringState Engineering,
    CompletenessState Completeness,
    FreshnessState Freshness,
    string? ResultId,
    string? NormalizedInputId,
    string? CalculationId,
    string? ProvenanceCodeDataRevisionId,
    string? ProvenanceMethodRevisionId,
    string? OutputJson,
    IReadOnlyList<WorkbookDiagnostic> Diagnostics);

public sealed record WorkbookFreshnessLedger(
    string WorkbookId,
    string ProjectId,
    string MemberId,
    string InputRevisionSha256,
    string? OutputRevisionSha256,
    bool IsCurrent,
    IReadOnlyList<string> ResultIds,
    string UpdatedAtUtc,
    string Reason);

public sealed record WorkbookCommandReceipt(
    string ReceiptId,
    WorkbookCommandKind Command,
    WorkbookReceiptState State,
    string WorkbookId,
    string ProjectId,
    string MemberId,
    string RequestId,
    string InputRevisionSha256,
    string? OutputRevisionSha256,
    string IssuedAtUtc,
    IReadOnlyList<string> DeclaredOutputTables,
    string? ArtifactSha256,
    IReadOnlyList<WorkbookDiagnostic> Diagnostics);

public sealed record WorkbookCommandResult(
    IReadOnlyList<WorkbookOperationResult> Results,
    WorkbookFreshnessLedger Freshness,
    WorkbookCommandReceipt Receipt,
    IReadOnlyList<WorkbookTable> OutputTables,
    WorkbookBenchmarkSummary? Benchmark = null);

public sealed record WorkbookCell(string? Value);
public sealed record WorkbookTable(string TableId, IReadOnlyList<IReadOnlyList<WorkbookCell>> Rows);

public interface IWorkbookTableStore
{
    bool TryRead(string tableId, out WorkbookTable table);
    void BulkWrite(IReadOnlyList<WorkbookTable> tables);
    void Remove(string tableId);
}

public interface IWorkbookArtifactSink
{
    void Stage(string artifactName, byte[] bytes);
    void Commit(string artifactName);
    void Rollback(string artifactName);
}

public sealed record WorkbookBenchmarkRequest(
    string EnvironmentFingerprint,
    IReadOnlyList<double> SamplesMilliseconds,
    string WorkloadRevision);

public sealed record WorkbookBenchmarkSummary(
    string EnvironmentFingerprint,
    string WorkloadRevision,
    int SampleCount,
    double P50Milliseconds,
    double P95Milliseconds,
    double MaximumMilliseconds);
