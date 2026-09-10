using System.Security.Cryptography;
using StructuralEngineering.Contracts;
using StructuralEngineering.Etabs;

internal static class OverviewWorker
{
    internal static async Task<int> Run(string requestFile, string responseFile)
    {
        var requestPath = Path.GetFullPath(requestFile); var responsePath = Path.GetFullPath(responseFile);
        if (File.Exists(responsePath) || File.Exists(responsePath + ".terminal")) return 3;
        EtabsContextWorkerRequest? request = null; var requestSha = new string('0', 64);
        Task? quiescence = null;
        var cleanupCompleted = true;
        using var cancellation = new CancellationTokenSource();
        using var watcher = new Timer(_ => { if (File.Exists(requestPath + ".cancel")) cancellation.Cancel(); }, null, TimeSpan.Zero, TimeSpan.FromMilliseconds(100));
        EtabsContextWorkerResponse response;
        try
        {
            request = EtabsOverviewWorkerCodec.ParseRequest(await Read(requestPath, 1024 * 1024));
            requestSha = EtabsOverviewWorkerCodec.RequestSha256(request);
            if (File.Exists(request.EvidencePath)) throw new IOException("Overview evidence already exists.");
            var rawPath = request.EvidencePath + ".inspection.json";
            var handle = EtabsInspectionBroker.Start(new(request.RequestId, request.Target.ProcessId, request.DeadlineUtc, rawPath),
                () => EtabsReflectionGetterHost.AttachInspection(EtabsHostDiscovery.Discover(request.Target)), false, cancellation.Token, overviewOnly: true);
            quiescence = handle.Quiescence;
            cleanupCompleted = false;
            var result = await handle.Completion;
            cleanupCompleted = result.CleanupCompleted;
            try
            {
                if (result.State != "completed") await Write(responsePath + ".terminal", EtabsOverviewWorkerCodec.CanonicalResponseJsonBytes(
                    Failed(State(result.State), result.Diagnostic ?? "Overview failed.", result.CleanupCompleted, false)));
            }
            finally { await handle.Quiescence; }
            if (result.State != "completed") response = Failed(State(result.State), result.Diagnostic ?? "Overview failed.", result.CleanupCompleted, true);
            else
            {
                CheckActive();
                var rawBytes = await Read(rawPath, 16 * 1024 * 1024);
                if (!result.CleanupCompleted || Convert.ToHexStringLower(SHA256.HashData(rawBytes)) != result.FileSha256)
                    throw new InvalidDataException("The completed overview source evidence changed.");
                var journalPath = rawPath + ".journal.jsonl";
                var artifact = EtabsOverviewProjector.Project(rawBytes, Path.GetFileName(rawPath), await Read(journalPath, 16 * 1024 * 1024),
                    Path.GetFileName(journalPath), request.RequestId, requestSha, request.Target);
                await Write(request.EvidencePath, EtabsOverviewWorkerCodec.CanonicalArtifactJsonBytes(artifact), CheckActive);
                CheckActive();
                response = new(request.RequestId, requestSha, EtabsContextWorkerState.Completed, null, null,
                    request.EvidencePath, artifact.ArtifactSha256, true, true);
            }
        }
        catch (Exception error)
        {
            if (quiescence is not null) await quiescence;
            response = Failed(cancellation.IsCancellationRequested ? EtabsContextWorkerState.Cancelled : EtabsContextWorkerState.Fenced,
                error.Message, cleanupCompleted, true);
        }
        await Write(responsePath, EtabsOverviewWorkerCodec.CanonicalResponseJsonBytes(response));
        return response.State == EtabsContextWorkerState.Completed ? 0 : 1;

        EtabsContextWorkerResponse Failed(EtabsContextWorkerState state, string message, bool cleanup, bool quiet) =>
            new(request?.RequestId ?? "unknown", requestSha, state, "ETABS.OVERVIEW_REJECTED", message, null, null, cleanup, quiet);
        void CheckActive()
        {
            cancellation.Token.ThrowIfCancellationRequested();
            if (DateTimeOffset.UtcNow >= request!.DeadlineUtc) throw new TimeoutException("Overview deadline elapsed before acceptance.");
        }
    }
    private static EtabsContextWorkerState State(string value) => value switch
    {
        "cancelled" => EtabsContextWorkerState.Cancelled,
        "lease_unavailable" => EtabsContextWorkerState.LeaseUnavailable,
        "transaction_uncertain" => EtabsContextWorkerState.TransactionUncertain,
        "rejected" => EtabsContextWorkerState.Rejected,
        _ => EtabsContextWorkerState.Fenced
    };
    private static async Task<byte[]> Read(string path, long limit) => new FileInfo(path).Length <= limit
        ? await File.ReadAllBytesAsync(path) : throw new InvalidDataException("Overview input exceeds its byte budget.");
    private static async Task Write(string path, byte[] bytes, Action? beforePublish = null)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(path))!);
        var temporary = path + "." + Guid.NewGuid().ToString("N") + ".tmp";
        try
        {
            await using (var stream = new FileStream(temporary, FileMode.CreateNew, FileAccess.Write, FileShare.None, 4096, FileOptions.WriteThrough))
            { await stream.WriteAsync(bytes); await stream.FlushAsync(); }
            beforePublish?.Invoke();
            File.Move(temporary, path);
        }
        finally { if (File.Exists(temporary)) File.Delete(temporary); }
    }
}
