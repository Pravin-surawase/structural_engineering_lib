using System.Security.Cryptography;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;
using StructuralEngineering.Etabs;

internal static class ForceWorker
{
    internal static async Task<int> Run(string requestFile, string responseFile)
    {
        var requestPath = Path.GetFullPath(requestFile); var responsePath = Path.GetFullPath(responseFile);
        if (File.Exists(responsePath)) return 3;
        EtabsForceWorkerRequest request; string requestSha;
        try
        {
            request = EtabsForceWorkerCodec.ParseRequest(await ReadBounded(requestPath, 1024 * 1024));
            requestSha = EtabsForceWorkerCodec.RequestSha256(request);
        }
        catch (Exception error) when (error is IOException or ArgumentException or System.Text.Json.JsonException or InvalidOperationException)
        {
            await Write(responsePath, EtabsForceWorkerCodec.CanonicalResponseJsonBytes(Failed("unknown", new('0', 64),
                EtabsContextWorkerState.Rejected, "ETABS.REQUEST_INVALID", error.Message, true, true)));
            return 1;
        }
        using var cancellation = new CancellationTokenSource();
        using var watcher = new Timer(_ => { if (File.Exists(requestPath + ".cancel")) cancellation.Cancel(); }, null, TimeSpan.Zero, TimeSpan.FromMilliseconds(100));
        EtabsForceWorkerResponse response;
        Task? activeQuiescence = null;
        EtabsBatchBrokerResult? acquisitionResult = null;
        try
        {
            var context = EtabsContextWorkerCodec.ParseAndValidateArtifact(await ReadBounded(request.ContextPath, 16 * 1024 * 1024), request.Target);
            if (context.ArtifactSha256 != request.ContextArtifactSha256) throw new InvalidDataException("The connected context changed before force capture.");
            var proof = context.Inventory.Provenance ?? throw new InvalidDataException("The connected context lacks source getter evidence.");
            var journal = Path.Combine(Path.GetDirectoryName(request.ContextPath)!, proof.JournalFileName);
            if (Sha(await ReadBounded(journal, 256 * 1024 * 1024)) != proof.JournalSha256)
                throw new InvalidDataException("The connected context's source evidence has changed.");
            CheckActive();
            PublishProgress(EtabsForceStage.Capturing, 0);
            var handle = new EtabsBatchOperationBroker().Start(new(request.RequestId, request.Target.ProcessId, request.DeadlineUtc, request.EvidencePath),
                () => EtabsReflectionGetterHost.AttachBulk(EtabsHostDiscovery.Discover(request.Target)),
                (host, token) => EtabsLiveGetterProbe.RunBulk(host, new(requestSha, context.Inventory, request.MemberObjectNames, request.DeadlineUtc), token,
                    (completed, _) => PublishProgress(EtabsForceStage.Capturing, completed)), cancellation.Token, EtabsBulkGetterMatrix.Sha256);
            activeQuiescence = handle.Quiescence;
            var result = acquisitionResult = await handle.Completion;
            try
            {
                if (result.State != EtabsContextWorkerState.Completed)
                    await Write(responsePath + ".terminal", EtabsForceWorkerCodec.CanonicalResponseJsonBytes(Failed(request.RequestId, requestSha,
                        result.State, result.DiagnosticCode, result.Message, result.CleanupCompleted, false)));
            }
            finally { await handle.Quiescence; }
            if (result.State != EtabsContextWorkerState.Completed || result.Artifact is null)
                response = Failed(request.RequestId, requestSha, result.State, result.DiagnosticCode, result.Message, result.CleanupCompleted, true);
            else
            {
                CheckActive();
                if (!result.Artifact.Content.Capture.Members.Select(member => member.ObjectName).SequenceEqual(request.MemberObjectNames))
                    throw new InvalidDataException("The acquired members differ from the complete requested scope.");
                PublishProgress(EtabsForceStage.Normalizing, request.MemberObjectNames.Count);
                var rawBytes = await ReadBounded(result.EvidencePath, 256 * 1024 * 1024);
                var normalized = EtabsCaptureProjector.Normalize(result.Artifact, rawBytes, Sha(rawBytes), new(request.ProjectId,
                    "wp10-force-worker/v1", result.EvidencePath, new Dictionary<string, SnapshotMaterialClassification>()));
                if (normalized.Snapshot is not { } snapshot)
                    response = Failed(request.RequestId, requestSha, EtabsContextWorkerState.Fenced, "ETABS.NORMALIZATION_REJECTED",
                        string.Join("; ", normalized.Diagnostics.Select(item => item.Message)), true, true);
                else
                {
                    CheckActive();
                    byte[] bytes;
                    if (request.AdmissionLimits.SnapshotTransport == EtabsForceWorkerCodec.GzipSnapshotTransport)
                    {
                        using var encoded = new MemoryStream();
                        AnalysisSnapshotTransport.Write(encoded, snapshot);
                        bytes = encoded.ToArray();
                    }
                    else bytes = AnalysisSnapshotCodec.CanonicalJsonBytes(snapshot);
                    var limits = request.AdmissionLimits;
                    if (bytes.Length > limits.MaximumBytes || snapshot.ActionRows.Count > limits.MaximumRows || snapshot.Members.Count > limits.MaximumMembers)
                        response = Failed(request.RequestId, requestSha, EtabsContextWorkerState.Fenced, "ETABS.SNAPSHOT_LIMIT",
                            "This capture exceeds the current qualified snapshot limits. Its source evidence was retained; no partial snapshot was loaded.", true, true);
                    else
                    {
                        PublishProgress(EtabsForceStage.Saving, request.MemberObjectNames.Count);
                        CheckActive();
                        await Write(request.SnapshotPath, bytes, beforePublish: CheckActive);
                        CheckActive();
                        response = new(request.RequestId, requestSha, EtabsContextWorkerState.Completed, null, null,
                            result.EvidencePath, result.Artifact.ArtifactSha256, request.SnapshotPath, Sha(bytes), snapshot.SnapshotId,
                            snapshot.SnapshotSha256, snapshot.Members.Count, snapshot.ActionRows.Count, true, true);
                    }
                }
            }
        }
        catch (Exception error)
        {
            if (activeQuiescence is not null) await activeQuiescence;
            var cancelled = cancellation.IsCancellationRequested || DateTimeOffset.UtcNow >= request.DeadlineUtc;
            response = Failed(request.RequestId, requestSha, cancelled ? EtabsContextWorkerState.Cancelled : EtabsContextWorkerState.Fenced,
                cancelled ? "ETABS.CANCELLED" : "ETABS.WORKER_FAILED", error.Message,
                acquisitionResult?.CleanupCompleted ?? activeQuiescence is null, true);
        }
        await Write(responsePath, EtabsForceWorkerCodec.CanonicalResponseJsonBytes(response));
        return response.State == EtabsContextWorkerState.Completed ? 0 : 1;

        void CheckActive()
        {
            cancellation.Token.ThrowIfCancellationRequested();
            if (DateTimeOffset.UtcNow >= request.DeadlineUtc) throw new TimeoutException("The force operation deadline elapsed.");
        }
        void PublishProgress(EtabsForceStage stage, int completed)
        {
            CheckActive();
            Write(responsePath + ".progress", EtabsForceWorkerCodec.CanonicalProgressJsonBytes(new(request.RequestId, requestSha, stage, completed, request.MemberObjectNames.Count)),
                overwrite: true).GetAwaiter().GetResult();
        }
    }

    private static EtabsForceWorkerResponse Failed(string id, string sha, EtabsContextWorkerState state, string? code, string? message, bool cleanup, bool quiesced) =>
        new(id, sha, state, code, message, null, null, null, null, null, null, 0, 0, cleanup, quiesced);
    private static string Sha(byte[] bytes) => Convert.ToHexStringLower(SHA256.HashData(bytes));
    private static async Task<byte[]> ReadBounded(string path, int maximum)
    {
        using var file = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read);
        if (file.Length > maximum) throw new InvalidDataException("The source file exceeds the qualified reader limit.");
        var bytes = new byte[checked((int)file.Length)];
        await file.ReadExactlyAsync(bytes);
        return bytes;
    }
    private static async Task Write(string path, byte[] bytes, bool overwrite = false, Action? beforePublish = null)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(path) ?? throw new InvalidOperationException("The output has no parent directory."));
        var temporary = path + $".{Guid.NewGuid():N}.tmp";
        try
        {
            await using (var stream = new FileStream(temporary, FileMode.CreateNew, FileAccess.Write, FileShare.None, 4096, FileOptions.WriteThrough))
            { await stream.WriteAsync(bytes); stream.Flush(true); }
            beforePublish?.Invoke();
            File.Move(temporary, path, overwrite);
        }
        finally { if (File.Exists(temporary)) File.Delete(temporary); }
    }
}
