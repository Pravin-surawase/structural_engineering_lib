using System.Security.Cryptography;
using System.Text.Json;

namespace StructuralEngineering.Contracts;

public sealed record EtabsOverviewProvenance(string GetterMatrixSha256, string InspectionFileName,
    string InspectionSha256, string JournalFileName, string JournalSha256, int GetterCalls);
public sealed record EtabsModelOverview(string RequestSha256, DateTimeOffset CapturedUtc, EtabsContextSourceIdentity Source,
    int FrameCount, int PointCount, int AreaCount, int StoryCount, int CaseCount, int CompletedCaseCount, int CombinationCount,
    string? ConcreteDesignCode, bool? ConcreteDesignResultsAvailable, IReadOnlyList<string> Gaps, EtabsOverviewProvenance Provenance);
public sealed record EtabsOverviewArtifact(string SchemaVersion, string ArtifactSha256, EtabsModelOverview Overview);

/// <summary>Counts and availability only; this envelope cannot be accepted as a geometry or force artifact.</summary>
public static class EtabsOverviewWorkerCodec
{
    public const string RequestSchemaVersion = "structural.etabs_overview_worker_request/v1";
    public const string ResponseSchemaVersion = "structural.etabs_overview_worker_response/v1";
    public const string ArtifactSchemaVersion = "structural.etabs_model_overview/v1";

    public static byte[] CanonicalRequestJsonBytes(EtabsContextWorkerRequest request)
    {
        _ = EtabsContextWorkerCodec.CanonicalRequestJsonBytes(request);
        return EtabsContextWorkerCodec.CanonicalBytes(new Envelope<EtabsContextWorkerRequest>(RequestSchemaVersion, request));
    }
    public static string RequestSha256(EtabsContextWorkerRequest request) => Sha(CanonicalRequestJsonBytes(request));
    public static EtabsContextWorkerRequest ParseRequest(ReadOnlySpan<byte> bytes)
    {
        var request = Parse<EtabsContextWorkerRequest>(bytes, RequestSchemaVersion);
        _ = CanonicalRequestJsonBytes(request);
        return request;
    }
    public static byte[] CanonicalResponseJsonBytes(EtabsContextWorkerResponse response)
    {
        _ = EtabsContextWorkerCodec.CanonicalResponseJsonBytes(response);
        return EtabsContextWorkerCodec.CanonicalBytes(new Envelope<EtabsContextWorkerResponse>(ResponseSchemaVersion, response));
    }
    public static EtabsContextWorkerResponse ParseAndValidateResponse(ReadOnlySpan<byte> bytes, string requestId, string requestSha)
    {
        var response = Parse<EtabsContextWorkerResponse>(bytes, ResponseSchemaVersion);
        if (response.RequestId != requestId || response.RequestSha256 != requestSha)
            throw new InvalidDataException("The overview response belongs to a different request.");
        _ = CanonicalResponseJsonBytes(response);
        return response;
    }
    public static EtabsOverviewArtifact CreateArtifact(EtabsModelOverview overview)
    {
        var source = overview.Source; var proof = overview.Provenance;
        if (source is null || proof is null || overview.CapturedUtc == default || !Hash(overview.RequestSha256) ||
            source.ProcessId <= 0 || source.ProcessStartedUtc == default || string.IsNullOrWhiteSpace(source.ExecutablePath) ||
            !Hash(source.ExecutableSha256) || string.IsNullOrWhiteSpace(source.ModelPath) || source.ModelBytes <= 0 ||
            source.ModelModifiedUtc == default || !Hash(source.ModelSha256) || string.IsNullOrWhiteSpace(source.EtabsApiVersion) ||
            source.PresentUnits <= 0 || source.DatabaseUnits <= 0 ||
            new[] { overview.FrameCount, overview.PointCount, overview.AreaCount, overview.StoryCount, overview.CaseCount,
                overview.CompletedCaseCount, overview.CombinationCount }.Any(count => count < 0) ||
            overview.CompletedCaseCount > overview.CaseCount || overview.Gaps is null ||
            !Hash(proof.GetterMatrixSha256) || !Hash(proof.InspectionSha256) || !Hash(proof.JournalSha256) ||
            !FileName(proof.InspectionFileName) || !FileName(proof.JournalFileName) || proof.GetterCalls <= 0)
            throw new InvalidDataException("The model overview has incomplete identity, counts or provenance.");
        return new(ArtifactSchemaVersion, Sha(EtabsContextWorkerCodec.CanonicalBytes(new Envelope<EtabsModelOverview>(ArtifactSchemaVersion, overview))), overview);
    }
    public static byte[] CanonicalArtifactJsonBytes(EtabsOverviewArtifact artifact)
    {
        if (artifact.SchemaVersion != ArtifactSchemaVersion || artifact.ArtifactSha256 != CreateArtifact(artifact.Overview).ArtifactSha256)
            throw new InvalidDataException("The overview artifact identity is invalid.");
        return EtabsContextWorkerCodec.CanonicalBytes(artifact);
    }
    public static EtabsOverviewArtifact ParseAndValidateArtifact(ReadOnlySpan<byte> bytes, EtabsProcessTarget? target = null, string? requestSha = null)
    {
        var artifact = JsonSerializer.Deserialize<EtabsOverviewArtifact>(bytes) ?? throw new InvalidDataException("The overview is empty.");
        _ = CanonicalArtifactJsonBytes(artifact);
        var source = artifact.Overview.Source;
        if (target is not null && (source.ProcessId != target.ProcessId || source.ProcessStartedUtc != target.ProcessStartedUtc ||
            !string.Equals(source.ExecutablePath, target.ExecutablePath, StringComparison.OrdinalIgnoreCase) || source.ExecutableSha256 != target.ExecutableSha256) ||
            requestSha is not null && artifact.Overview.RequestSha256 != requestSha)
            throw new InvalidDataException("The overview belongs to a different process or request.");
        return artifact;
    }
    public static void ValidateDetailedSource(EtabsOverviewArtifact overview, EtabsContextArtifact context)
    {
        if (overview.Overview.Source != context.Inventory.Source)
            throw new InvalidDataException("The model changed after its overview. Connect again before loading details.");
    }
    private static T Parse<T>(ReadOnlySpan<byte> bytes, string schema) where T : class
    {
        var envelope = JsonSerializer.Deserialize<Envelope<T>>(bytes);
        return envelope?.SchemaVersion == schema && envelope.Value is not null ? envelope.Value
            : throw new InvalidDataException("The overview envelope schema is unsupported.");
    }
    private static bool Hash(string? value) => value is { Length: 64 } && value.All(char.IsAsciiHexDigit);
    private static bool FileName(string? value) => !string.IsNullOrWhiteSpace(value) && Path.GetFileName(value) == value;
    private static string Sha(byte[] bytes) => Convert.ToHexStringLower(SHA256.HashData(bytes));
    private sealed record Envelope<T>(string SchemaVersion, T Value);
}
