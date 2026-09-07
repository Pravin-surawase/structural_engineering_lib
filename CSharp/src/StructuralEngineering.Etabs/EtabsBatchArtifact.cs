using System.Security.Cryptography;
using System.Text.Json;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Etabs;

public sealed record EtabsBatchAcquisitionContent(
    string OperationId, string LeaseKey, DateTimeOffset StartedUtc, DateTimeOffset CompletedUtc,
    EtabsHostIdentity HostIdentityBefore, EtabsHostIdentity HostIdentityAfter,
    SnapshotCallLedger CallLedger, EtabsBatchCapture Capture, EtabsCleanupEvidence Cleanup);

public sealed record EtabsBatchArtifact(string SchemaVersion, string ArtifactSha256, EtabsBatchAcquisitionContent Content);

/// <summary>A separately versioned shared capture; retained single-member artifact bytes keep their original contract.</summary>
public static class EtabsBatchArtifactCodec
{
    public const string SchemaVersion = "structural.etabs_batch_artifact/v1";
    private static readonly JsonSerializerOptions Options = EtabsAcquisitionArtifactCodec.CreateOptions();

    public static EtabsBatchArtifact Create(EtabsBatchAcquisitionContent content) =>
        new(SchemaVersion, Convert.ToHexStringLower(SHA256.HashData(
            AnalysisSnapshotCodec.CanonicalJsonBytes(new { SchemaVersion, Content = content }))), content);

    public static byte[] CanonicalJsonBytes(EtabsBatchArtifact artifact) => AnalysisSnapshotCodec.CanonicalJsonBytes(artifact);

    public static EtabsBatchArtifact ParseAndValidate(string json)
    {
        using (var document = JsonDocument.Parse(json)) EtabsAcquisitionArtifactCodec.EnsureNoDuplicateProperties(document.RootElement);
        var artifact = JsonSerializer.Deserialize<EtabsBatchArtifact>(json, Options)
            ?? throw new JsonException("A batch artifact cannot be null.");
        if (artifact.SchemaVersion != SchemaVersion || artifact.Content is null ||
            artifact.ArtifactSha256 != Create(artifact.Content).ArtifactSha256)
            throw new InvalidDataException("The batch artifact identity is invalid.");
        var content = artifact.Content;
        var capture = content.Capture;
        var ledger = content.CallLedger;
        var matrixSha = capture?.ProfileId == EtabsBulkGetterMatrix.ProfileId ? EtabsBulkGetterMatrix.Sha256 : EtabsForceGetterMatrix.Sha256;
        if (string.IsNullOrWhiteSpace(content.OperationId) || string.IsNullOrWhiteSpace(content.LeaseKey) ||
            content.StartedUtc >= content.CompletedUtc || capture is null || ledger is null ||
            capture.ProfileId is not (EtabsForceGetterMatrix.ProfileId or EtabsBulkGetterMatrix.ProfileId) || capture.GetterMatrixSha256 != matrixSha ||
            content.HostIdentityBefore != content.HostIdentityAfter || capture.HostIdentity != content.HostIdentityBefore ||
            content.StartedUtc > capture.StartedUtc || capture.StartedUtc > capture.CompletedUtc || capture.CompletedUtc > content.CompletedUtc ||
            capture.Preflight.Sha256 != capture.Postflight.Sha256 ||
            !content.Cleanup.HostDisposed || !content.Cleanup.LeaseReleased || content.Cleanup.ApartmentState != "STA" ||
            content.Cleanup.MessagePump != EtabsOperationBroker.StaMessagePump.Name ||
            capture.Members.Count is < 1 or > 1000 || capture.Members.Sum(member => (long)member.FrameForceRows) > 100_000 ||
            capture.Members.Any(member => member.FrameForceRows < 1) ||
            capture.Members.Select(member => member.ObjectName).Distinct(StringComparer.Ordinal).Count() != capture.Members.Count ||
            ledger.OperationId != content.OperationId || ledger.RecordCount != ledger.Records.Count ||
            ledger.Records.Count != capture.Calls.Count * 2 || ledger.Records.Count == 0 ||
            !ledger.Records.Select(record => record.Sequence).SequenceEqual(Enumerable.Range(1, ledger.Records.Count)))
            throw new InvalidDataException("The batch is incomplete or not postflight-clean.");
        string? previous = null;
        for (var index = 0; index < capture.Calls.Count; index++)
        {
            var start = ledger.Records[index * 2]; var end = ledger.Records[index * 2 + 1]; var call = capture.Calls[index];
            if (start.Stage != SnapshotCallStage.Started || end.Stage != SnapshotCallStage.Returned ||
                start.CallId != end.CallId || start.Method != call.Operation || end.Method != call.Operation ||
                start.OperationId != content.OperationId || end.OperationId != content.OperationId ||
                start.Effect != SnapshotCallEffect.Getter || end.Effect != SnapshotCallEffect.Getter ||
                start.PreviousRecordSha256 != previous || end.PreviousRecordSha256 != start.RecordSha256 ||
                start.ReturnCode is not null || start.RawShape is not null || end.ReturnCode != 0 || string.IsNullOrWhiteSpace(end.RawShape) ||
                start.ArgumentsSha256 != end.ArgumentsSha256 ||
                start.SignatureAuthoritySha256 != matrixSha || end.SignatureAuthoritySha256 != matrixSha ||
                start.RecordSha256 != AnalysisSnapshotCodec.CallRecordSha256(start) || end.RecordSha256 != AnalysisSnapshotCodec.CallRecordSha256(end))
                throw new InvalidDataException("The batch ledger is unpaired, failed, or hash-invalid.");
            previous = end.RecordSha256;
        }
        if (ledger.HeadRecordSha256 != previous || ledger.LedgerSha256 != AnalysisSnapshotCodec.CallLedgerSha256(ledger))
            throw new InvalidDataException("The batch ledger digest is invalid.");
        return artifact;
    }
}
