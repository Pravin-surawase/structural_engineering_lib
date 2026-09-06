using System.Security.Cryptography;
using System.Text.Json;

namespace StructuralEngineering.Contracts;

public sealed record EtabsForceAdmissionLimits(int MaximumBytes, int MaximumRows, int MaximumMembers);

/// <summary>A force read is bound to an accepted context, explicit members and the caller's qualified store limits.</summary>
public sealed record EtabsForceWorkerRequest(
    string RequestId, EtabsProcessTarget Target, DateTimeOffset DeadlineUtc,
    string ContextPath, string ContextArtifactSha256, string ProjectId,
    IReadOnlyList<string> MemberObjectNames, string EvidencePath, string SnapshotPath,
    EtabsForceAdmissionLimits AdmissionLimits);

public sealed record EtabsForceWorkerResponse(
    string RequestId, string RequestSha256, EtabsContextWorkerState State,
    string? DiagnosticCode, string? Message, string? ArtifactPath, string? ArtifactSha256,
    string? SnapshotPath, string? SnapshotFileSha256, string? SnapshotId, string? SnapshotSha256,
    int MemberCount, int ActionRowCount, bool CleanupCompleted, bool Quiesced);

public enum EtabsForceStage { Capturing, Normalizing, Saving }
public sealed record EtabsForceProgress(string RequestId, string RequestSha256, EtabsForceStage Stage, int CompletedMembers, int TotalMembers);

public static class EtabsForceWorkerCodec
{
    public const string RequestSchemaVersion = "structural.etabs_force_worker_request/v1";
    public const string ResponseSchemaVersion = "structural.etabs_force_worker_response/v1";
    public const string ProgressSchemaVersion = "structural.etabs_force_worker_progress/v1";

    public static byte[] CanonicalRequestJsonBytes(EtabsForceWorkerRequest request)
    {
        Validate(request);
        return EtabsContextWorkerCodec.CanonicalBytes(new Envelope<EtabsForceWorkerRequest>(RequestSchemaVersion, request));
    }
    public static string RequestSha256(EtabsForceWorkerRequest request) =>
        Convert.ToHexStringLower(SHA256.HashData(CanonicalRequestJsonBytes(request)));

    public static EtabsForceWorkerRequest ParseRequest(ReadOnlySpan<byte> bytes)
    {
        var request = Read<EtabsForceWorkerRequest>(bytes, RequestSchemaVersion);
        Validate(request);
        return request;
    }

    public static byte[] CanonicalResponseJsonBytes(EtabsForceWorkerResponse response)
    {
        ValidateIdentity(response.RequestId, response.RequestSha256);
        if (response.State == EtabsContextWorkerState.Completed)
        {
            if (!response.CleanupCompleted || !response.Quiesced || string.IsNullOrWhiteSpace(response.ArtifactPath) ||
                !Sha(response.ArtifactSha256) || string.IsNullOrWhiteSpace(response.SnapshotPath) || !Sha(response.SnapshotFileSha256) ||
                string.IsNullOrWhiteSpace(response.SnapshotId) || !Sha(response.SnapshotSha256) || response.MemberCount is < 1 or > 1000 ||
                response.ActionRowCount is < 1 or > 100_000)
                throw new InvalidDataException("A completed force response requires a cleanup-complete snapshot and acquisition.");
        }
        else if (response.ArtifactPath is not null || response.ArtifactSha256 is not null || response.SnapshotPath is not null ||
            response.SnapshotFileSha256 is not null || response.SnapshotId is not null || response.SnapshotSha256 is not null || response.MemberCount != 0 || response.ActionRowCount != 0)
            throw new InvalidDataException("An incomplete force response cannot publish accepted data.");
        return EtabsContextWorkerCodec.CanonicalBytes(new Envelope<EtabsForceWorkerResponse>(ResponseSchemaVersion, response));
    }

    public static EtabsForceWorkerResponse ParseAndValidateResponse(ReadOnlySpan<byte> bytes, string requestId, string requestSha256)
    {
        var response = Read<EtabsForceWorkerResponse>(bytes, ResponseSchemaVersion);
        if (response.RequestId != requestId || response.RequestSha256 != requestSha256) throw new InvalidDataException("The force response belongs to another request.");
        CanonicalResponseJsonBytes(response);
        return response;
    }

    public static byte[] CanonicalProgressJsonBytes(EtabsForceProgress progress)
    {
        ValidateIdentity(progress.RequestId, progress.RequestSha256);
        if (progress.TotalMembers is < 1 or > 1000 || progress.CompletedMembers < 0 || progress.CompletedMembers > progress.TotalMembers ||
            !Enum.IsDefined(progress.Stage)) throw new InvalidDataException("Invalid force progress counts or stage.");
        return EtabsContextWorkerCodec.CanonicalBytes(new Envelope<EtabsForceProgress>(ProgressSchemaVersion, progress));
    }

    public static EtabsForceProgress ParseProgress(ReadOnlySpan<byte> bytes, string requestId, string requestSha256)
    {
        var progress = Read<EtabsForceProgress>(bytes, ProgressSchemaVersion);
        if (progress.RequestId != requestId || progress.RequestSha256 != requestSha256) throw new InvalidDataException("The progress belongs to another request.");
        CanonicalProgressJsonBytes(progress);
        return progress;
    }

    private static T Read<T>(ReadOnlySpan<byte> bytes, string schema) where T : class
    {
        var envelope = JsonSerializer.Deserialize<Envelope<T>>(bytes) ?? throw new InvalidDataException("The worker envelope is empty.");
        if (envelope.SchemaVersion != schema || envelope.Value is null) throw new InvalidDataException("The force worker schema is unsupported.");
        return envelope.Value;
    }
    private static void Validate(EtabsForceWorkerRequest request)
    {
        ArgumentNullException.ThrowIfNull(request);
        if (string.IsNullOrWhiteSpace(request.RequestId) || request.Target is null || request.Target.ProcessId <= 0 ||
            request.Target.ProcessStartedUtc == default || string.IsNullOrWhiteSpace(request.Target.ExecutablePath) || !Sha(request.Target.ExecutableSha256) ||
            request.DeadlineUtc == default || string.IsNullOrWhiteSpace(request.ContextPath) || !Sha(request.ContextArtifactSha256) ||
            string.IsNullOrWhiteSpace(request.ProjectId) || string.IsNullOrWhiteSpace(request.EvidencePath) || string.IsNullOrWhiteSpace(request.SnapshotPath) ||
            request.MemberObjectNames is null || request.MemberObjectNames.Count is < 1 or > 1000 || request.MemberObjectNames.Any(string.IsNullOrWhiteSpace) ||
            !request.MemberObjectNames.SequenceEqual(request.MemberObjectNames.Distinct(StringComparer.Ordinal).Order(StringComparer.Ordinal)) ||
            request.AdmissionLimits is null || request.AdmissionLimits.MaximumBytes is < 1 or > 25_000_000 ||
            request.AdmissionLimits.MaximumRows is < 1 or > 100_000 || request.AdmissionLimits.MaximumMembers is < 1 or > 1000 ||
            request.MemberObjectNames.Count > request.AdmissionLimits.MaximumMembers)
            throw new InvalidDataException("The force request has incomplete scope, identity or qualified admission limits.");
    }
    private static void ValidateIdentity(string id, string sha)
    {
        if (string.IsNullOrWhiteSpace(id) || !Sha(sha)) throw new InvalidDataException("The worker record requires a bound request identity.");
    }
    private static bool Sha(string? text) => text is { Length: 64 } && text.All(character => character is >= '0' and <= '9' or >= 'a' and <= 'f');
    private sealed record Envelope<T>(string SchemaVersion, T Value);
}
