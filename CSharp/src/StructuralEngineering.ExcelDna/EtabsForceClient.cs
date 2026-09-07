using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;
using System.Diagnostics;

namespace StructuralEngineering.ExcelDna;

public sealed record EtabsForceLoadResult(EtabsForceWorkerResponse Response, OfflineSnapshotSession? Session, string OperationDirectory);

public static partial class EtabsConnectionClient
{
    /// <summary>Shares connection/force PID ownership; all large reads and admission run outside Excel's UI thread.</summary>
    public static async Task<EtabsForceLoadResult> GetForcesAsync(string packageDirectory, string operationsRoot, string snapshotStoreDirectory,
        EtabsConnectionSession context, string projectId, string requestId, CancellationToken cancellationToken,
        IProgress<EtabsForceProgress>? progress = null, IReadOnlyList<string>? memberObjectNames = null)
    {
        var source = context.Artifact.Inventory.Source;
        if (!ActiveProcesses.TryAdd(source.ProcessId, 0)) throw new InvalidOperationException("This ETABS process still has a reader running or cleaning up. Wait for it to finish.");
        Process? worker = null; var releaseHere = true;
        var directory = Path.Combine(Path.GetFullPath(operationsRoot), requestId);
        var requestPath = Path.Combine(directory, "request.json");
        try
        {
            cancellationToken.ThrowIfCancellationRequested();
            var executable = ValidateWorkerPackage(packageDirectory);
            var members = (memberObjectNames ?? context.Frames.Values.Where(frame => frame.DesignOrientation == EtabsFrameDesignOrientation.Beam)
                .Select(frame => frame.SourceFrameId).ToArray()).Order(StringComparer.Ordinal).ToArray();
            if (members.Any(name => !context.Frames.TryGetValue(name, out var frame) || frame.DesignOrientation != EtabsFrameDesignOrientation.Beam))
                throw new InvalidDataException("Every requested member must be a beam in the connected model context.");
            var request = new EtabsForceWorkerRequest(requestId,
                new(source.ProcessId, source.ProcessStartedUtc, source.ExecutablePath, source.ExecutableSha256), DateTimeOffset.UtcNow.AddMinutes(8),
                Path.Combine(context.OperationDirectory, "context.json"), context.Artifact.ArtifactSha256, projectId, members,
                Path.Combine(directory, "capture.json"), Path.Combine(directory, "snapshot.sasnap"),
                new(OfflineSnapshotStore.MaximumInputBytes, OfflineSnapshotStore.MaximumActionRows, OfflineSnapshotStore.MaximumMembers,
                    EtabsForceWorkerCodec.RowsSnapshotTransport));
            var requestSha = EtabsForceWorkerCodec.RequestSha256(request);
            Directory.CreateDirectory(directory);
            await using (var file = new FileStream(requestPath, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                await file.WriteAsync(EtabsForceWorkerCodec.CanonicalRequestJsonBytes(request), cancellationToken).ConfigureAwait(false);
            var responsePath = Path.Combine(directory, "response.json");
            cancellationToken.ThrowIfCancellationRequested();
            var start = new ProcessStartInfo(executable) { UseShellExecute = false, CreateNoWindow = true, WorkingDirectory = packageDirectory };
            start.ArgumentList.Add("--forces-request"); start.ArgumentList.Add(requestPath);
            start.ArgumentList.Add("--response"); start.ArgumentList.Add(responsePath);
            worker = Process.Start(start) ?? throw new InvalidOperationException("The packaged force reader did not start.");
            using var cancel = cancellationToken.Register(() => WriteCancellation(requestPath));
            EtabsForceProgress? previous = null;
            while (true)
            {
                if (DateTimeOffset.UtcNow > request.DeadlineUtc.AddSeconds(5) || cancellationToken.IsCancellationRequested)
                {
                    WriteCancellation(requestPath);
                    releaseHere = false; _ = ObserveCleanup(worker, source.ProcessId); worker = null;
                    return new(new(requestId, requestSha, cancellationToken.IsCancellationRequested ? EtabsContextWorkerState.Cancelled : EtabsContextWorkerState.TransactionUncertain,
                        "ETABS.CLEANUP_PENDING", "The force read stopped. Reader cleanup is still pending; another read cannot start yet.",
                        null, null, null, null, null, null, 0, 0, false, false), null, directory);
                }
                if (File.Exists(responsePath) || File.Exists(responsePath + ".terminal"))
                {
                    var final = File.Exists(responsePath);
                    var response = EtabsForceWorkerCodec.ParseAndValidateResponse(await ReadBoundedAsync(final ? responsePath : responsePath + ".terminal", 64 * 1024).ConfigureAwait(false), requestId, requestSha);
                    OfflineSnapshotSession? session = null;
                    if (response.State == EtabsContextWorkerState.Completed)
                    {
                        if (!final || !PathsEqual(response.ArtifactPath!, request.EvidencePath) || !PathsEqual(response.SnapshotPath!, request.SnapshotPath))
                            throw new InvalidDataException("The force reader returned unexpected evidence paths.");
                        await worker.WaitForExitAsync().WaitAsync(TimeSpan.FromSeconds(10)).ConfigureAwait(false);
                        if (worker.ExitCode != 0) throw new InvalidDataException("The force reader did not exit successfully.");
                        cancellationToken.ThrowIfCancellationRequested();
                        var store = new OfflineSnapshotStore(snapshotStoreDirectory);
                        var imported = store.ImportWithSnapshot(request.SnapshotPath, response.SnapshotFileSha256);
                        var snapshot = imported.Snapshot;
                        if (snapshot.Metadata.ProjectId != projectId || snapshot.SourceIdentity.AcquisitionId != requestId ||
                            snapshot.SnapshotId != response.SnapshotId || snapshot.SnapshotSha256 != response.SnapshotSha256 ||
                            snapshot.Members.Count != response.MemberCount || snapshot.ActionRows.Count != response.ActionRowCount ||
                            !snapshot.Members.Select(member => member.ObjectId).Order(StringComparer.Ordinal).SequenceEqual(members) ||
                            snapshot.SourceIdentity.ModelFileSha256.Value != source.ModelSha256 ||
                            snapshot.SourceIdentity.ProcessIdentity.Value != $"{source.ProcessId}@{source.ProcessStartedUtc.UtcDateTime:O}")
                            throw new InvalidDataException("The force snapshot differs from its workbook, model, request or required member scope.");
                        var metadata = snapshot.RawCapture.ModelRecords.Single(record => record.RecordKind == RawModelRecordKind.ModelMetadata);
                        if (AnalysisSnapshotNormalizer.Digest(metadata.Fields["data"].GetProperty("projection").GetProperty("acquisition_evidence").GetProperty("capture").GetProperty("context")) !=
                            AnalysisSnapshotNormalizer.Digest(context.Artifact.Inventory))
                            throw new InvalidDataException("The force snapshot belongs to a different connected context.");
                        if (metadata.Fields["data"].GetProperty("projection").GetProperty("artifact_sha256").GetString() != response.ArtifactSha256 ||
                            metadata.Fields["data"].GetProperty("projection").GetProperty("artifact_file_sha256").GetString() != Sha256File(request.EvidencePath))
                            throw new InvalidDataException("The source acquisition does not match the accepted force snapshot.");
                        cancellationToken.ThrowIfCancellationRequested();
                        session = new(imported.Reference, snapshot);
                    }
                    if (!worker.HasExited) { releaseHere = false; _ = ObserveCleanup(worker, source.ProcessId); worker = null; }
                    return new(response, session, directory);
                }
                if (File.Exists(responsePath + ".progress"))
                {
                    byte[]? bytes = null;
                    try
                    {
                        // Windows ReplaceFile can briefly make this optional status unavailable to new readers.
                        await using var file = new FileStream(responsePath + ".progress", FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete);
                        if (file.Length > 64 * 1024) throw new InvalidDataException("Force progress exceeds its input limit.");
                        bytes = new byte[checked((int)file.Length)]; await file.ReadExactlyAsync(bytes).ConfigureAwait(false);
                    }
                    catch (Exception error) when (error is IOException or UnauthorizedAccessException && (error.HResult & 0xffff) is 2 or 5 or 32)
                    {
                        bytes = null;
                        // Retry on the next bounded poll; final response, cancellation and deadline checks still run.
                    }
                    if (bytes is not null)
                    {
                        var current = EtabsForceWorkerCodec.ParseProgress(bytes, requestId, requestSha);
                        if (current != previous) { previous = current; progress?.Report(current); }
                    }
                }
                if (worker.HasExited)
                {
                    if (File.Exists(responsePath) || File.Exists(responsePath + ".terminal")) continue;
                    throw new InvalidOperationException("The force reader exited without a valid response. Its evidence folder was retained.");
                }
                await Task.Delay(100).ConfigureAwait(false);
            }
        }
        catch
        {
            if (worker is { HasExited: false }) { WriteCancellation(requestPath); releaseHere = false; _ = ObserveCleanup(worker, source.ProcessId); worker = null; }
            throw;
        }
        finally { worker?.Dispose(); if (releaseHere) ActiveProcesses.TryRemove(source.ProcessId, out _); }
    }

    private static bool PathsEqual(string first, string second) => string.Equals(Path.GetFullPath(first), Path.GetFullPath(second), StringComparison.OrdinalIgnoreCase);
}
