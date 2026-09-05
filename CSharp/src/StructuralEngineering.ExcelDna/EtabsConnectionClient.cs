using System.Collections.Concurrent;
using System.Diagnostics;
using System.Security.Cryptography;
using System.Text.Json;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.ExcelDna;

public sealed record EtabsProcessChoice(int ProcessId, DateTimeOffset StartedUtc, string ExecutablePath, string WindowTitle);
public sealed record EtabsConnectionResult(EtabsContextWorkerResponse Response, EtabsContextArtifact? Artifact, string OperationDirectory);

/// <summary>File/process I/O only. No Excel or CSI object is touched by this background client.</summary>
public static class EtabsConnectionClient
{
    private static readonly ConcurrentDictionary<int, byte> ActiveProcesses = new();
    public static int ActiveWorkerCount => ActiveProcesses.Count;

    public static IReadOnlyList<EtabsProcessChoice> FindRunningModels()
    {
        var choices = new List<EtabsProcessChoice>();
        foreach (var process in Process.GetProcessesByName("ETABS"))
        {
            using (process)
            {
                try
                {
                    if (process.MainModule?.FileName is { } path)
                        choices.Add(new(process.Id, new DateTimeOffset(process.StartTime.ToUniversalTime()), path, process.MainWindowTitle.Trim()));
                }
                catch (Exception error) when (error is InvalidOperationException or System.ComponentModel.Win32Exception) { }
            }
        }
        return choices.OrderBy(item => item.ProcessId).ToArray();
    }

    public static async Task<EtabsConnectionResult> ConnectAsync(string packageDirectory, string operationsRoot,
        EtabsProcessChoice choice, string requestId, CancellationToken cancellationToken)
    {
        if (!ActiveProcesses.TryAdd(choice.ProcessId, 0)) throw new InvalidOperationException("This ETABS process still has a reader running or cleaning up. Wait for it to finish.");
        Process? worker = null;
        var releaseHere = true;
        try
        {
            cancellationToken.ThrowIfCancellationRequested();
            var executable = ValidateWorkerPackage(packageDirectory);
            var target = new EtabsProcessTarget(choice.ProcessId, choice.StartedUtc, choice.ExecutablePath, Sha256File(choice.ExecutablePath));
            var directory = Path.Combine(Path.GetFullPath(operationsRoot), requestId);
            Directory.CreateDirectory(directory);
            var requestPath = Path.Combine(directory, "request.json");
            var responsePath = Path.Combine(directory, "response.json");
            var request = new EtabsContextWorkerRequest(requestId, target, DateTimeOffset.UtcNow.AddMinutes(2), Path.Combine(directory, "context.json"));
            var requestSha = EtabsContextWorkerCodec.RequestSha256(request);
            await using (var file = new FileStream(requestPath, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                await file.WriteAsync(EtabsContextWorkerCodec.CanonicalRequestJsonBytes(request), cancellationToken).ConfigureAwait(false);
            cancellationToken.ThrowIfCancellationRequested();
            var start = new ProcessStartInfo(executable) { UseShellExecute = false, CreateNoWindow = true, WorkingDirectory = packageDirectory };
            start.ArgumentList.Add("--request"); start.ArgumentList.Add(requestPath);
            start.ArgumentList.Add("--response"); start.ArgumentList.Add(responsePath);
            worker = Process.Start(start) ?? throw new InvalidOperationException("The packaged ETABS reader did not start.");
            using var cancel = cancellationToken.Register(() => WriteCancellation(requestPath));
            while (true)
            {
                if (File.Exists(responsePath) || File.Exists(responsePath + ".terminal"))
                {
                    var final = File.Exists(responsePath);
                    var response = EtabsContextWorkerCodec.ParseAndValidateResponse(
                        await ReadBoundedAsync(final ? responsePath : responsePath + ".terminal", 64 * 1024).ConfigureAwait(false), requestId, requestSha);
                    EtabsContextArtifact? artifact = null;
                    if (response.State == EtabsContextWorkerState.Completed)
                    {
                        if (!final || !response.Quiesced || !response.CleanupCompleted ||
                            !string.Equals(Path.GetFullPath(response.ArtifactPath!), request.EvidencePath, StringComparison.OrdinalIgnoreCase))
                            throw new InvalidDataException("The ETABS reader returned an incomplete or unexpected artifact.");
                        artifact = EtabsContextWorkerCodec.ParseAndValidateArtifact(
                            await ReadBoundedAsync(request.EvidencePath, 16 * 1024 * 1024).ConfigureAwait(false), target, requestSha);
                        if (artifact.ArtifactSha256 != response.ArtifactSha256) throw new InvalidDataException("The context and worker response digests differ.");
                        ValidateProvenance(artifact, directory);
                        await worker.WaitForExitAsync().WaitAsync(TimeSpan.FromSeconds(10)).ConfigureAwait(false);
                        if (worker.ExitCode != 0) throw new InvalidDataException("The ETABS reader did not exit successfully.");
                    }
                    if (!worker.HasExited)
                    {
                        releaseHere = false;
                        _ = ObserveCleanup(worker, choice.ProcessId);
                        worker = null;
                    }
                    return new(response, artifact, directory);
                }
                if (worker.HasExited) throw new InvalidOperationException("The ETABS reader exited without a valid response. Its evidence folder has been retained.");
                if (DateTimeOffset.UtcNow > request.DeadlineUtc.AddSeconds(5) || cancellationToken.IsCancellationRequested)
                {
                    WriteCancellation(requestPath);
                    var state = cancellationToken.IsCancellationRequested ? EtabsContextWorkerState.Cancelled : EtabsContextWorkerState.TransactionUncertain;
                    releaseHere = false;
                    _ = ObserveCleanup(worker, choice.ProcessId);
                    worker = null;
                    return new(new(requestId, requestSha, state, "ETABS.CLEANUP_PENDING", "Reader cancellation requested. Cleanup is still pending; another read cannot start yet.", null, null, false, false), null, directory);
                }
                await Task.Delay(100).ConfigureAwait(false);
            }
        }
        catch
        {
            if (worker is { HasExited: false })
            {
                WriteCancellation(Path.Combine(Path.GetFullPath(operationsRoot), requestId, "request.json"));
                releaseHere = false;
                _ = ObserveCleanup(worker, choice.ProcessId);
                worker = null;
            }
            throw;
        }
        finally
        {
            worker?.Dispose();
            if (releaseHere) ActiveProcesses.TryRemove(choice.ProcessId, out _);
        }
    }

    public static string ValidateWorkerPackage(string packageDirectory)
    {
        using var document = JsonDocument.Parse(File.ReadAllBytes(Path.Combine(packageDirectory, "manifest.json")));
        var entry = document.RootElement.GetProperty("worker");
        var name = entry.GetProperty("name").GetString();
        if (name != "StructAutomate.EtabsWorker.exe") throw new InvalidDataException("The installed package has no supported ETABS reader. Repair the add-in package.");
        var path = Path.Combine(packageDirectory, name);
        if (!File.Exists(path) || Sha256File(path) != entry.GetProperty("sha256").GetString())
            throw new InvalidDataException("The installed ETABS reader is missing or differs from the package manifest. Repair the add-in package.");
        return path;
    }

    public static void ValidateProvenance(EtabsContextArtifact artifact, string directory)
    {
        var proof = artifact.Inventory.Provenance ?? throw new InvalidDataException("The context has no retained getter evidence.");
        var path = Path.Combine(directory, proof.JournalFileName);
        if (!File.Exists(path) || new FileInfo(path).Length > 256L * 1024 * 1024 || Sha256File(path) != proof.JournalSha256)
            throw new InvalidDataException("The retained context getter evidence is missing or has changed.");
    }

    private static async Task ObserveCleanup(Process worker, int processId)
    {
        try { await worker.WaitForExitAsync().ConfigureAwait(false); }
        finally { worker.Dispose(); ActiveProcesses.TryRemove(processId, out _); }
    }
    private static void WriteCancellation(string requestPath)
    {
        try { File.WriteAllText(requestPath + ".cancel", "cancel"); }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException) { }
    }
    private static async Task<byte[]> ReadBoundedAsync(string path, long limit)
    {
        if (new FileInfo(path).Length > limit) throw new InvalidDataException("The reader response exceeds the supported input size.");
        return await File.ReadAllBytesAsync(path).ConfigureAwait(false);
    }
    private static string Sha256File(string path)
    {
        using var stream = File.OpenRead(path);
        return Convert.ToHexStringLower(SHA256.HashData(stream));
    }
}
