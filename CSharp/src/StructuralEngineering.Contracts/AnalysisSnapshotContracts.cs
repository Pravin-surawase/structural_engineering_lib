using System.Text.Json;
using System.Text.Json.Serialization;

namespace StructuralEngineering.Contracts;

public enum OptionalEvidenceState { Supplied, NotRequested, Unavailable, NotApplicable }
public enum MemberSelectionMode { AllBeams, Explicit }
public enum StationSelectionMode { AllAvailable, Explicit }
public enum SnapshotResultKind { FrameForce }
public enum SnapshotCallStage { Started, Returned }
public enum SnapshotCallEffect { Getter }
public enum RawModelRecordKind { ModelMetadata, Point, Material, Section, Member, LoadCase, LoadCombination, ResultSelection, Station }
public enum SnapshotSectionShape { Rectangular, General }
public enum SectionAssignmentKind { Direct, AutoSelect }
public enum SnapshotLocal2Face
{
    [JsonStringEnumMemberName("positive_local_2")]
    PositiveLocal2,
    [JsonStringEnumMemberName("negative_local_2")]
    NegativeLocal2
}
public enum SnapshotLocal3Face
{
    [JsonStringEnumMemberName("positive_local_3")]
    PositiveLocal3,
    [JsonStringEnumMemberName("negative_local_3")]
    NegativeLocal3
}
public enum SnapshotLoadCaseKind { LinearStatic, Modal, ResponseSpectrum, Other }
public enum SnapshotAnalysisCaseStatus { Finished, NotFinished }
public enum SnapshotCombinationKind { LinearAdd, Envelope, Other }
public enum SnapshotResultSelectionKind { LoadCase, LoadCombination }
public enum SnapshotActionBasis { StaticConcurrent, StagedStep, ResponseResult, ComponentEnvelope, DesignEnvelope }
public enum SnapshotStationSide { Continuous, Before, After }
public enum SnapshotRowDisposition { Accepted, ApprovedExclusion, Blocked }
public enum SnapshotOperationState { PreflightAccepted, Completed, PreflightRejected, Fenced, TransactionUncertain, Cancelled }

public sealed record PortableOptionalText(
    OptionalEvidenceState State,
    string? Value,
    string? ReasonCode);

public sealed record EtabsSourceExpectation(
    string SourceSystem,
    string SourceVersion,
    string ModelRevisionId,
    PortableOptionalText ProcessIdentity,
    PortableOptionalText ModelFileSha256);

public sealed record SnapshotMemberSelection(
    MemberSelectionMode Mode,
    IReadOnlyList<string> MemberIds);

public sealed record SnapshotStationSelection(
    StationSelectionMode Mode,
    IReadOnlyList<string> StationIds);

public sealed record EtabsImportScope(
    string ProjectId,
    SnapshotMemberSelection Members,
    IReadOnlyList<string> ResultSelectionIds,
    IReadOnlyList<SnapshotResultKind> ResultKinds,
    SnapshotStationSelection Stations);

public sealed record EtabsImportRequest(
    string SchemaVersion,
    string OperationSemanticId,
    string RequestId,
    EtabsSourceExpectation SourceExpectation,
    EtabsImportScope Scope,
    IReadOnlyList<string> RequiredProvenance,
    string DeadlineUtc);

public sealed record SnapshotSourceUnits(
    string Length,
    string Force,
    string Moment,
    string Stress,
    string MassDensity);

public sealed record SnapshotUnitConversion(
    double LengthToMm,
    double ForceToKn,
    double MomentToKnm,
    double StressToNPerMm2,
    double MassDensityToKgPerM3);

public sealed record SnapshotUnitBasis(
    string Length,
    string Force,
    string Moment,
    string Stress,
    string MassDensity,
    SnapshotSourceUnits OriginalSourceUnits,
    SnapshotUnitConversion ConversionToCanonical);

public sealed record SnapshotCallRecord(
    string SchemaVersion,
    string OperationId,
    string CallId,
    int Sequence,
    string? PreviousRecordSha256,
    SnapshotCallStage Stage,
    string Method,
    string SignatureAuthoritySha256,
    SnapshotCallEffect Effect,
    string ArgumentsSha256,
    int? ReturnCode,
    string? RawShape,
    string RecordedAtUtc,
    string RecordSha256);

public sealed record SnapshotCallLedger(
    string SchemaVersion,
    string OperationId,
    int RecordCount,
    string? HeadRecordSha256,
    string LedgerSha256,
    IReadOnlyList<SnapshotCallRecord> Records);

public sealed record RawSnapshotModelRecord(
    RawModelRecordKind RecordKind,
    string SourceRecordId,
    IReadOnlyDictionary<string, JsonElement> Fields);

public sealed record RawSnapshotForceRow(
    string SourceRowId,
    int SourceRowIndex,
    string ObjectId,
    string AnalysisElementId,
    double ObjectStation,
    double ElementStation,
    string OutputCaseName,
    string StepType,
    double? StepNumber,
    double P,
    double V2,
    double V3,
    double T,
    double M2,
    double M3);

public sealed record RawAnalysisCapture(
    string SchemaVersion,
    string RawCaptureId,
    string RawCaptureSha256,
    string AcquisitionId,
    string ModelRevisionId,
    string AnalysisRevisionId,
    string ResultEpochId,
    SnapshotSourceUnits SourceUnits,
    SnapshotCallLedger CallLedger,
    IReadOnlyList<RawSnapshotModelRecord> ModelRecords,
    IReadOnlyList<RawSnapshotForceRow> ForceRows);

public sealed record SnapshotSourceIdentity(
    string SourceSystem,
    string SourceVersion,
    string AdapterSemanticId,
    string AdapterBuildId,
    string AcquisitionId,
    string RawCaptureId,
    string RawCaptureSha256,
    string ModelRevisionId,
    string AnalysisRevisionId,
    string ResultEpochId,
    string RuntimeFingerprint,
    PortableOptionalText ProcessIdentity,
    PortableOptionalText ModelFileSha256);

public sealed record SnapshotMetadata(
    string ProjectId,
    string ModelName,
    PortableOptionalText ModelGuid,
    bool ModelLocked,
    SnapshotAnalysisCaseStatus AnalysisStatus,
    string EvidenceReference);

public sealed record SnapshotVector3(double X, double Y, double Z);

public sealed record SnapshotMatrix3(
    [property: JsonPropertyName("row_1")]
    IReadOnlyList<double> Row1,
    [property: JsonPropertyName("row_2")]
    IReadOnlyList<double> Row2,
    [property: JsonPropertyName("row_3")]
    IReadOnlyList<double> Row3);

public sealed record SnapshotAxis(
    string AxisId,
    SnapshotVector3 E1,
    SnapshotVector3 E2,
    SnapshotVector3 E3,
    SnapshotMatrix3 SourceToCommon,
    SnapshotLocal2Face PhysicalTopFace,
    SnapshotLocal3Face PhysicalLeftFace,
    string EvidenceReference);

public sealed record SnapshotPoint(
    string PointId,
    string SourceName,
    double XMm,
    double YMm,
    double ZMm,
    string StoryId,
    string EvidenceReference);

public sealed record SnapshotMaterial(
    string MaterialId,
    string SourceName,
    string MaterialKind,
    double ElasticModulusNPerMm2,
    double PoissonRatio,
    double MassDensityKgPerM3,
    string EvidenceReference);

public sealed record SnapshotSection(
    string SectionId,
    string SourceName,
    SnapshotSectionShape Shape,
    string MaterialId,
    double AreaMm2,
    double TorsionalConstantMm4,
    [property: JsonPropertyName("inertia_2_mm4")]
    double Inertia2Mm4,
    [property: JsonPropertyName("inertia_3_mm4")]
    double Inertia3Mm4,
    double? WidthMm,
    double? DepthMm,
    string EvidenceReference);

public sealed record SnapshotModifiers(
    double AxialArea,
    [property: JsonPropertyName("shear_area_2")]
    double ShearArea2,
    [property: JsonPropertyName("shear_area_3")]
    double ShearArea3,
    double Torsion,
    [property: JsonPropertyName("inertia_2")]
    double Inertia2,
    [property: JsonPropertyName("inertia_3")]
    double Inertia3,
    double Mass,
    double Weight);

public sealed record SnapshotOffsets(
    bool Automatic,
    double EndIMm,
    double EndJMm,
    double RigidZoneFactor);

public sealed record SnapshotEndReleases(
    bool U1,
    bool U2,
    bool U3,
    bool R1,
    bool R2,
    bool R3);

public sealed record SnapshotReleases(
    SnapshotEndReleases EndI,
    SnapshotEndReleases EndJ);

public sealed record SnapshotMember(
    string MemberId,
    string ObjectId,
    string SourceLabel,
    string StoryId,
    string PointIId,
    string PointJId,
    string SectionId,
    string AxisId,
    SectionAssignmentKind AssignmentKind,
    string? AutoSelectListId,
    SnapshotModifiers Modifiers,
    SnapshotOffsets Offsets,
    SnapshotReleases Releases,
    IReadOnlyList<string> AnalysisElementIds,
    string EvidenceReference);

public sealed record SnapshotLoadCase(
    string CaseId,
    string SourceName,
    SnapshotLoadCaseKind CaseKind,
    SnapshotAnalysisCaseStatus Status,
    string EvidenceReference);

public sealed record SnapshotCombinationFactor(
    int Ordinal,
    SnapshotResultSelectionKind SourceKind,
    string SourceId,
    double ScaleFactor);

public sealed record SnapshotLoadCombination(
    string CombinationId,
    string SourceName,
    SnapshotCombinationKind CombinationKind,
    IReadOnlyList<SnapshotCombinationFactor> Factors,
    string EvidenceReference);

public sealed record SnapshotResultSelection(
    string SelectionId,
    SnapshotResultSelectionKind Kind,
    string SourceId,
    string SourceName,
    bool SelectedForOutput,
    SnapshotActionBasis ActionBasis,
    string ResultEpochId,
    string EvidenceReference);

public sealed record SnapshotStation(
    string StationId,
    string MemberId,
    string ObjectId,
    string AnalysisElementId,
    double PhysicalStationMm,
    double ObjectStationMm,
    double ElementStationMm,
    double NormalizedRatio,
    SnapshotStationSide Side,
    string EvidenceReference);

public sealed record SnapshotForceResultProvenance(
    string GetterMethod,
    string SignatureAuthoritySha256,
    string CallId,
    int SourceRowIndex,
    string ConcurrencyBasis,
    string EvidenceReference);

public sealed record SnapshotActionRow(
    string RowId,
    string SourceRowId,
    string MemberId,
    string ObjectId,
    string AnalysisElementId,
    string StationId,
    string SelectionId,
    string OutputCaseName,
    string StepType,
    double? StepNumber,
    SnapshotActionBasis ActionBasis,
    double PKn,
    double V2Kn,
    double V3Kn,
    double TKnm,
    double M2Knm,
    double M3Knm,
    string ForceUnit,
    string MomentUnit,
    SnapshotForceResultProvenance Provenance);

public sealed record SnapshotRowDispositionRecord(
    string SourceRecordId,
    string RecordKind,
    SnapshotRowDisposition Disposition,
    string? CanonicalId,
    string? ReasonCode,
    string? ApprovalReference,
    IReadOnlyList<string> DiagnosticCodes);

public sealed record SnapshotRowLedger(
    int SourceRowCount,
    int AcceptedCount,
    int ApprovedExclusionCount,
    int BlockedCount,
    IReadOnlyList<SnapshotRowDispositionRecord> Rows);

public sealed record SnapshotNormalization(
    string RuleId,
    bool ConversionPerformedOnce,
    string SourceUnitsSha256);

public sealed record SnapshotFreshness(
    FreshnessState State,
    string ModelRevisionId,
    string AnalysisRevisionId,
    string ResultEpochId,
    IReadOnlyList<string> SelectionIds);

public sealed record SnapshotDiagnostic(
    string Code,
    string Severity,
    string FieldOrLocation,
    string Message,
    string? Remediation);

public sealed record SnapshotProvenance(
    string ContractRevisionId,
    IReadOnlyList<string> SourceReferences,
    IReadOnlyList<string> Limitations);

public sealed record AnalysisSnapshot(
    string SchemaVersion,
    string OperationSemanticId,
    string SnapshotId,
    string SnapshotSha256,
    string CreatedAtUtc,
    SnapshotSourceIdentity SourceIdentity,
    SnapshotMetadata Metadata,
    SnapshotUnitBasis Units,
    IReadOnlyList<SnapshotAxis> Axes,
    IReadOnlyList<SnapshotPoint> Points,
    IReadOnlyList<SnapshotMaterial> Materials,
    IReadOnlyList<SnapshotSection> Sections,
    IReadOnlyList<SnapshotMember> Members,
    IReadOnlyList<SnapshotLoadCase> LoadCases,
    IReadOnlyList<SnapshotLoadCombination> LoadCombinations,
    IReadOnlyList<SnapshotResultSelection> ResultSelections,
    IReadOnlyList<SnapshotStation> Stations,
    IReadOnlyList<SnapshotActionRow> ActionRows,
    SnapshotRowLedger RowLedger,
    SnapshotNormalization Normalization,
    SnapshotFreshness Freshness,
    IReadOnlyList<SnapshotDiagnostic> Diagnostics,
    SnapshotProvenance Provenance,
    string EvidenceManifestSha256,
    RawAnalysisCapture RawCapture);

public sealed record EtabsSnapshotResult(
    string SchemaVersion,
    string OperationSemanticId,
    SnapshotOperationState OperationState,
    ExecutionState Execution,
    ApplicabilityState Applicability,
    EngineeringState Engineering,
    CompletenessState Completeness,
    FreshnessState Freshness,
    ApprovalState Approval,
    string? RequestId,
    AnalysisSnapshot? Snapshot,
    IReadOnlyList<SnapshotDiagnostic> Diagnostics,
    SnapshotProvenance Provenance);
