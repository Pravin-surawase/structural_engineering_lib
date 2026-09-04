using System.Text.Json;

namespace StructuralEngineering.Contracts;

/// <summary>Explicit caller-supplied classification; it never implies a strength grade.</summary>
public sealed record SnapshotMaterialClassification(string MaterialKind, string EvidenceReference);

public sealed record SnapshotNormalizationContext(
    string ProjectId,
    string ModelName,
    string SourceVersion,
    string AdapterBuildId,
    string RuntimeFingerprint,
    string CreatedAtUtc,
    PortableOptionalText ProcessIdentity,
    PortableOptionalText ModelFileSha256,
    IReadOnlyDictionary<string, SnapshotMaterialClassification> MaterialClassifications,
    string PolicyId,
    string EvidenceReference);

public sealed record SnapshotGetterEvidence(
    int Ordinal, string CallId, string Operation, string SignatureAuthoritySha256,
    string TargetSourceRecordId, JsonElement Inputs, JsonElement DirectValue,
    JsonElement Outputs, int? CsiReturnCode,
    string StartedUtc, string CompletedUtc, string HostIdentitySha256);

public sealed record SnapshotProjectionRecord(string SourceRecordId, RawModelRecordKind RecordKind);

public sealed record SnapshotProjectionManifest(
    string ArtifactSha256,
    string ArtifactFileSha256,
    JsonElement AcquisitionEvidence,
    IReadOnlyList<SnapshotProjectionRecord> ModelRecords,
    IReadOnlyList<string> ForceRowIds,
    IReadOnlyList<SnapshotGetterEvidence> GetterEvidence);

public sealed record SourceSnapshotMetadata(
    bool ModelLocked, SnapshotAnalysisCaseStatus AnalysisStatus,
    SnapshotNormalizationContext Context, SnapshotProjectionManifest Projection);

// Dimensional values below are in RawAnalysisCapture.SourceUnits, never canonical units.
public sealed record SourceSnapshotPoint(string Id, string Name, double X, double Y, double Z, string Story);
public sealed record SourceSnapshotMaterial(string Id, string Name, double ElasticModulus, double PoissonRatio, double MassDensity);
public sealed record SourceSnapshotSection(
    string Id, string Name, string MaterialId, double Area, double Torsion,
    double Inertia2, double Inertia3, double Width, double Depth,
    IReadOnlyList<double> Modifiers);

public sealed record SourceSnapshotElement(
    string Id, string ObjectId, string PointIId, string PointJId,
    double RelativeI, double RelativeJ, IReadOnlyList<double> LocalToGlobal);

public sealed record SourceSnapshotInsertion(
    int CardinalPoint, bool Mirror2, bool Mirror3, bool StiffnessTransformed,
    IReadOnlyList<double> OffsetI, IReadOnlyList<double> OffsetJ, string CoordinateSystem);

public sealed record SourceSnapshotMember(
    string Id, string ObjectId, string Label, string Story, string PointIId, string PointJId,
    string SectionId, string? AutoSelectListId, IReadOnlyList<double> Modifiers,
    bool AutomaticOffsets, double EndOffsetI, double EndOffsetJ, double RigidZoneFactor,
    IReadOnlyList<bool> ReleasesI, IReadOnlyList<bool> ReleasesJ,
    IReadOnlyList<double> SpringsI, IReadOnlyList<double> SpringsJ,
    SourceSnapshotInsertion Insertion, IReadOnlyList<SourceSnapshotElement> Elements);

public sealed record SourceSnapshotLoadCase(
    string Id, string Name, SnapshotLoadCaseKind Kind,
    SnapshotAnalysisCaseStatus Status, string? InitialCase);
public sealed record SourceSnapshotCombination(
    string Id, string Name, SnapshotCombinationKind Kind,
    IReadOnlyList<SnapshotCombinationFactor> Factors);
public sealed record SourceSnapshotSelection(
    string Id, SnapshotResultSelectionKind Kind, string SourceId, string Name, bool Selected);
public sealed record SourceSnapshotStation(
    string Id, string MemberId, string ObjectId, string ElementId,
    double ObjectStation, double ElementStation);
