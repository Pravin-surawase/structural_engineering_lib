using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace StructuralEngineering.Contracts;

/// <summary>Immutable user-selected process binding.  It never discovers or launches ETABS.</summary>
public sealed record EtabsProcessTarget(
    int ProcessId,
    DateTimeOffset ProcessStartedUtc,
    string ExecutablePath,
    string ExecutableSha256);

/// <summary>Exact installed API files required for a read-only ETABS context worker.</summary>
public enum EtabsContextWorkerState
{
    Completed,
    Rejected,
    LeaseUnavailable,
    TransactionUncertain,
    Fenced,
    Cancelled
}

/// <summary>Pure worker request. The worker discovers the saved model only after exact PID binding.</summary>
public sealed record EtabsContextWorkerRequest(
    string RequestId,
    EtabsProcessTarget Target,
    DateTimeOffset DeadlineUtc,
    string EvidencePath);

/// <summary>
/// Pure worker response. A completed response is emitted only after ETABS cleanup and lease quiescence.
/// Non-completed states carry no accepted artifact.
/// </summary>
public sealed record EtabsContextWorkerResponse(
    string RequestId,
    string RequestSha256,
    EtabsContextWorkerState State,
    string? DiagnosticCode,
    string? Message,
    string? ArtifactPath,
    string? ArtifactSha256,
    bool CleanupCompleted,
    bool Quiesced);

public enum EtabsFrameDesignOrientation
{
    Column = 1,
    Beam = 2,
    Brace = 3,
    Null = 4,
    Other = 5
}

public sealed record EtabsContextSourceIdentity(
    int ProcessId,
    DateTimeOffset ProcessStartedUtc,
    string ExecutablePath,
    string ExecutableSha256,
    string ModelPath,
    long ModelBytes,
    DateTimeOffset ModelModifiedUtc,
    string ModelSha256,
    string EtabsApiVersion,
    bool ModelLocked,
    int PresentUnits,
    int DatabaseUnits);

public sealed record EtabsContextPoint(string SourcePointId, double Xmm, double Ymm, double Zmm);

public sealed record EtabsContextSection(string SourceSectionId, string SourceMaterialId);

public sealed record EtabsContextFrame(
    string SourceFrameId,
    string SourceSectionId,
    string SourceStoryId,
    string SourcePoint1Id,
    string SourcePoint2Id,
    EtabsFrameDesignOrientation DesignOrientation);

/// <summary>
/// Source geometry only. Supports, spans, releases, offsets, loads, analysis and material strengths are absent.
/// Coordinates are global source coordinates converted once to mm from the qualified kN-m-C unit profile.
/// </summary>
public sealed record EtabsContextInventory(
    string RequestSha256,
    DateTimeOffset CapturedUtc,
    EtabsContextSourceIdentity Source,
    IReadOnlyList<EtabsContextPoint> Points,
    IReadOnlyList<EtabsContextFrame> Frames,
    IReadOnlyList<EtabsContextSection> Sections,
    string Coverage,
    EtabsContextProvenance? Provenance = null);

public sealed record EtabsContextProvenance(string GetterMatrixSha256, string JournalFileName, string JournalSha256, int GetterCalls);

public sealed record EtabsContextArtifact(string SchemaVersion, string ArtifactSha256, EtabsContextInventory Inventory);

public static class EtabsContextWorkerCodec
{
    public const string RequestSchemaVersion = "structural.etabs_context_worker_request/v1";
    public const string ResponseSchemaVersion = "structural.etabs_context_worker_response/v1";
    public const string ArtifactSchemaVersion = "structural.etabs_context_inventory/v1";

    public static string RequestSha256(EtabsContextWorkerRequest request)
    {
        Validate(request);
        return Convert.ToHexStringLower(SHA256.HashData(CanonicalBytes(new Envelope<EtabsContextWorkerRequest>(RequestSchemaVersion, request))));
    }

    public static byte[] CanonicalRequestJsonBytes(EtabsContextWorkerRequest request)
    {
        Validate(request);
        return CanonicalBytes(new Envelope<EtabsContextWorkerRequest>(RequestSchemaVersion, request));
    }

    public static byte[] CanonicalResponseJsonBytes(EtabsContextWorkerResponse response)
    {
        ArgumentNullException.ThrowIfNull(response);
        if (string.IsNullOrWhiteSpace(response.RequestId) || string.IsNullOrWhiteSpace(response.RequestSha256))
            throw new ArgumentException("A response requires request identity.", nameof(response));
        if (response.State == EtabsContextWorkerState.Completed &&
            (!response.CleanupCompleted || !response.Quiesced || string.IsNullOrWhiteSpace(response.ArtifactPath) || string.IsNullOrWhiteSpace(response.ArtifactSha256)))
            throw new ArgumentException("A completed response requires a quiesced, cleanup-complete artifact.", nameof(response));
        if (response.State != EtabsContextWorkerState.Completed && response.ArtifactPath is not null)
            throw new ArgumentException("A non-completed response cannot expose an artifact.", nameof(response));
        return CanonicalBytes(new Envelope<EtabsContextWorkerResponse>(ResponseSchemaVersion, response));
    }

    public static EtabsContextWorkerRequest ParseRequest(ReadOnlySpan<byte> utf8)
    {
        var envelope = JsonSerializer.Deserialize<Envelope<EtabsContextWorkerRequest>>(utf8)
            ?? throw new InvalidDataException("The context worker request is empty.");
        if (envelope.SchemaVersion != RequestSchemaVersion || envelope.Value is null)
            throw new InvalidDataException("The context worker request schema is unsupported.");
        Validate(envelope.Value);
        return envelope.Value;
    }

    public static EtabsContextWorkerResponse ParseAndValidateResponse(ReadOnlySpan<byte> utf8, string expectedRequestId, string expectedRequestSha256)
    {
        var envelope = JsonSerializer.Deserialize<Envelope<EtabsContextWorkerResponse>>(utf8)
            ?? throw new InvalidDataException("The context worker response is empty.");
        if (envelope.SchemaVersion != ResponseSchemaVersion || envelope.Value is null)
            throw new InvalidDataException("The context worker response schema is unsupported.");
        var response = envelope.Value;
        if (!string.Equals(response.RequestId, expectedRequestId, StringComparison.Ordinal) || !string.Equals(response.RequestSha256, expectedRequestSha256, StringComparison.Ordinal))
            throw new InvalidDataException("The context worker response belongs to a different request.");
        CanonicalResponseJsonBytes(response);
        return response;
    }

    public static EtabsContextArtifact CreateArtifact(EtabsContextInventory inventory)
    {
        ValidateInventory(inventory);
        var basis = new ArtifactBasis(ArtifactSchemaVersion, inventory);
        var hash = Convert.ToHexStringLower(SHA256.HashData(CanonicalBytes(basis)));
        return new(ArtifactSchemaVersion, hash, inventory);
    }

    public static byte[] CanonicalArtifactJsonBytes(EtabsContextArtifact artifact)
    {
        ArgumentNullException.ThrowIfNull(artifact);
        if (artifact.SchemaVersion != ArtifactSchemaVersion || artifact.Inventory is null ||
            artifact.ArtifactSha256 != CreateArtifact(artifact.Inventory).ArtifactSha256)
            throw new InvalidDataException("The context artifact identity is invalid.");
        return CanonicalBytes(artifact);
    }

    public static EtabsContextArtifact ParseAndValidateArtifact(ReadOnlySpan<byte> utf8, EtabsProcessTarget? expectedTarget = null, string? expectedRequestSha256 = null)
    {
        var artifact = JsonSerializer.Deserialize<EtabsContextArtifact>(utf8)
            ?? throw new InvalidDataException("The context artifact is empty.");
        if (artifact.SchemaVersion != ArtifactSchemaVersion || artifact.Inventory is null ||
            artifact.ArtifactSha256 != CreateArtifact(artifact.Inventory).ArtifactSha256)
            throw new InvalidDataException("The context artifact identity is invalid.");
        if (expectedTarget is not null && (artifact.Inventory.Source.ProcessId != expectedTarget.ProcessId ||
            artifact.Inventory.Source.ProcessStartedUtc != expectedTarget.ProcessStartedUtc ||
            !string.Equals(artifact.Inventory.Source.ExecutablePath, expectedTarget.ExecutablePath, StringComparison.OrdinalIgnoreCase) ||
            !string.Equals(artifact.Inventory.Source.ExecutableSha256, expectedTarget.ExecutableSha256, StringComparison.Ordinal)))
            throw new InvalidDataException("The context artifact belongs to a different selected process.");
        if (expectedRequestSha256 is not null && !string.Equals(artifact.Inventory.RequestSha256, expectedRequestSha256, StringComparison.Ordinal))
            throw new InvalidDataException("The context artifact belongs to a different request.");
        return artifact;
    }

    private static void Validate(EtabsContextWorkerRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);
        if (string.IsNullOrWhiteSpace(request.RequestId) || request.Target is null ||
            request.Target.ProcessId <= 0 || request.Target.ProcessStartedUtc == default || request.DeadlineUtc == default ||
            string.IsNullOrWhiteSpace(request.Target.ExecutablePath) || string.IsNullOrWhiteSpace(request.Target.ExecutableSha256) || string.IsNullOrWhiteSpace(request.EvidencePath))
            throw new ArgumentException("The context worker request has incomplete target or runtime identity.", nameof(request));
    }

    private static void ValidateInventory(EtabsContextInventory inventory)
    {
        ArgumentNullException.ThrowIfNull(inventory);
        if (inventory.Source is null || string.IsNullOrWhiteSpace(inventory.RequestSha256) || inventory.CapturedUtc == default ||
            inventory.Source.ProcessId <= 0 || string.IsNullOrWhiteSpace(inventory.Source.ModelSha256) ||
            inventory.Source.PresentUnits != 6 || inventory.Source.DatabaseUnits != 6 ||
            inventory.Points is null || inventory.Frames is null || inventory.Sections is null ||
            inventory.Points.GroupBy(item => item.SourcePointId, StringComparer.Ordinal).Any(group => string.IsNullOrWhiteSpace(group.Key) || group.Count() != 1) ||
            inventory.Frames.GroupBy(item => item.SourceFrameId, StringComparer.Ordinal).Any(group => string.IsNullOrWhiteSpace(group.Key) || group.Count() != 1) ||
            inventory.Sections.GroupBy(item => item.SourceSectionId, StringComparer.Ordinal).Any(group => string.IsNullOrWhiteSpace(group.Key) || group.Count() != 1) ||
            inventory.Points.Any(item => !double.IsFinite(item.Xmm) || !double.IsFinite(item.Ymm) || !double.IsFinite(item.Zmm)) ||
            inventory.Frames.Any(item => string.IsNullOrWhiteSpace(item.SourceSectionId) || string.IsNullOrWhiteSpace(item.SourceStoryId) ||
                string.IsNullOrWhiteSpace(item.SourcePoint1Id) || string.IsNullOrWhiteSpace(item.SourcePoint2Id) || item.SourcePoint1Id == item.SourcePoint2Id) ||
            inventory.Frames.Any(frame => !inventory.Points.Any(point => point.SourcePointId == frame.SourcePoint1Id) ||
                !inventory.Points.Any(point => point.SourcePointId == frame.SourcePoint2Id)) ||
            inventory.Frames.Any(frame => !inventory.Sections.Any(section => section.SourceSectionId == frame.SourceSectionId)) ||
            inventory.Sections.Any(item => string.IsNullOrWhiteSpace(item.SourceMaterialId)) ||
            !string.Equals(inventory.Coverage, "source_geometry_only;supports=absent;spans=absent;offsets=absent;releases=absent;loads=absent;analysis=absent;strengths=absent", StringComparison.Ordinal))
            throw new InvalidDataException("The context inventory is incomplete or outside its source-geometry-only coverage.");
        if (inventory.Provenance is { } proof &&
            (proof.GetterMatrixSha256.Length != 64 || proof.JournalSha256.Length != 64 || proof.GetterCalls <= 0 ||
             string.IsNullOrWhiteSpace(proof.JournalFileName) || Path.GetFileName(proof.JournalFileName) != proof.JournalFileName))
            throw new InvalidDataException("The context provenance reference is invalid.");
    }

    private static byte[] CanonicalBytes<T>(T value) => Encoding.UTF8.GetBytes(Canonical(JsonSerializer.SerializeToElement(value)));

    private static string Canonical(JsonElement value) => value.ValueKind switch
    {
        JsonValueKind.Object => "{" + string.Join(',', value.EnumerateObject().OrderBy(property => property.Name, StringComparer.Ordinal)
            .Select(property => Canonical(JsonSerializer.SerializeToElement(property.Name)) + ":" + Canonical(property.Value))) + "}",
        JsonValueKind.Array => "[" + string.Join(',', value.EnumerateArray().Select(Canonical)) + "]",
        JsonValueKind.String => JsonSerializer.Serialize(value.GetString()),
        _ => value.GetRawText()
    };

    private sealed record Envelope<T>(string SchemaVersion, T Value);
    private sealed record ArtifactBasis(string SchemaVersion, EtabsContextInventory Inventory);
}
