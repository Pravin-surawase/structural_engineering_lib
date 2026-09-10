using System.Security.Cryptography;
using System.Text.Json;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Etabs;

public sealed record EtabsInspectionArtifact(string SchemaVersion, string GetterMatrixSha256, EtabsHostIdentity Source,
    EtabsInspectionCapture Capture, SnapshotCallLedger Ledger, EtabsCleanupEvidence Cleanup);
public sealed record EtabsInspectionResult(string State, string? Diagnostic, string EvidencePath, string? FileSha256, bool CleanupCompleted);
public sealed record EtabsInspectionHandle(Task<EtabsInspectionResult> Completion, Task Quiescence);

/// <summary>Inspection uses the existing process lease, STA pump and durable call-journal owners.</summary>
public static class EtabsInspectionBroker
{
    public static EtabsInspectionHandle Start(EtabsBrokerRequest request, Func<IEtabsGetterHost> hostFactory,
        bool includeSample, CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(request); ArgumentNullException.ThrowIfNull(hostFactory);
        var path = Path.GetFullPath(request.EvidencePath);
        var journalPath = path + ".journal.jsonl";
        if (request.ProcessId <= 0 || string.IsNullOrWhiteSpace(request.OperationId) || request.DeadlineUtc <= DateTimeOffset.UtcNow ||
            request.DeadlineUtc > DateTimeOffset.UtcNow.AddMinutes(3))
            return Done("rejected", "An exact operation/PID and a future deadline no more than three minutes away are required.");
        if (File.Exists(path) || File.Exists(journalPath)) return Done("rejected", "Evidence already exists.");
        if (!EtabsProcessLease.TryAcquire(request.ProcessId, out var lease)) return Done("lease_unavailable", "The selected ETABS process has an active operation.");

        var completion = new TaskCompletionSource<EtabsInspectionResult>(TaskCreationOptions.RunContinuationsAsynchronously);
        var quiescence = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        var stop = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        var gate = new object();
        void Terminal(string state, string diagnostic)
        {
            lock (gate) completion.TrySetResult(new(state, diagnostic, path, null, false));
        }
        var registration = cancellationToken.Register(() => Terminal("cancelled", "Cancellation requested; the lease remains held until provider cleanup finishes."));
        _ = Monitor();
        var thread = new Thread(Worker) { IsBackground = true, Name = $"ETABS-INSPECTION-STA-{request.ProcessId}" };
        thread.SetApartmentState(ApartmentState.STA); thread.Start();
        return new(completion.Task, quiescence.Task);

        async Task Monitor()
        {
            if (await EtabsOperationBroker.WaitForDeadlineAsync(request.DeadlineUtc - DateTimeOffset.UtcNow, quiescence.Task).ConfigureAwait(false))
            {
                lock (gate)
                {
                    if (completion.Task.IsCompleted) return;
                    stop.Cancel();
                    Terminal("transaction_uncertain", "Inspection deadline elapsed. No artifact is accepted; cleanup continues under the held lease.");
                }
            }
        }

        void Worker()
        {
            IEtabsGetterHost? host = null; EtabsInspectionArtifact? artifact = null;
            Exception? failure = null; var disposed = false; var released = false;
            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(path)!);
                using var journal = new EtabsOperationBroker.EtabsCallJournal(request.OperationId, journalPath, TimeProvider.System, EtabsInspectionGetterMatrix.Sha256);
                EtabsOperationBroker.StaMessagePump.Drain(); stop.Token.ThrowIfCancellationRequested();
                host = hostFactory();
                var before = host.InspectIdentity();
                if (before.ProcessId != request.ProcessId) throw new InvalidOperationException("Attached process differs from the lease.");
                using var journalHost = new EtabsOperationBroker.LedgerEtabsGetterHost(host, journal);
                var capture = EtabsInspectionReader.Read(journalHost, request.DeadlineUtc, includeSample, stop.Token);
                if (host.InspectIdentity() != before) throw new InvalidOperationException("Source file or process identity changed during inspection.");
                stop.Token.ThrowIfCancellationRequested();
                artifact = new("structural.etabs_inspection/v1", EtabsInspectionGetterMatrix.Sha256, before, capture,
                    journal.Build(), new(false, false, "win32-peekmessage/v1", Thread.CurrentThread.GetApartmentState().ToString()));
            }
            catch (Exception exception) { failure = exception; }
            finally
            {
                try { host?.Dispose(); disposed = host is not null; } catch (Exception exception) { failure ??= exception; }
                EtabsOperationBroker.StaMessagePump.Drain();
                try { lease!.Dispose(); released = true; } catch (Exception exception) { failure ??= exception; }
            }
            try
            {
                lock (gate)
                {
                    if (completion.Task.IsCompleted) return;
                    if (failure is not null || artifact is null || stop.IsCancellationRequested || DateTimeOffset.UtcNow >= request.DeadlineUtc)
                    {
                        completion.TrySetResult(new("fenced", failure?.ToString() ?? "Inspection ended outside its acceptance deadline.", path, null, disposed && released));
                        return;
                    }
                    artifact = artifact with { Cleanup = artifact.Cleanup with { HostDisposed = disposed, LeaseReleased = released } };
                    var bytes = JsonSerializer.SerializeToUtf8Bytes(artifact);
                    var temporary = path + "." + Guid.NewGuid().ToString("N") + ".tmp";
                    try
                    {
                        using (var stream = new FileStream(temporary, FileMode.CreateNew, FileAccess.Write, FileShare.None, 4096, FileOptions.WriteThrough))
                        { stream.Write(bytes); stream.Flush(true); }
                        if (DateTimeOffset.UtcNow >= request.DeadlineUtc || stop.IsCancellationRequested)
                            throw new TimeoutException("Inspection evidence completed after its deadline.");
                        File.Move(temporary, path);
                        completion.TrySetResult(new("completed", null, path, Convert.ToHexStringLower(SHA256.HashData(bytes)), disposed && released));
                    }
                    finally { if (File.Exists(temporary)) File.Delete(temporary); }
                }
            }
            catch (Exception exception) { completion.TrySetResult(new("fenced", exception.ToString(), path, null, disposed && released)); }
            finally { registration.Dispose(); quiescence.TrySetResult(); stop.Dispose(); }
        }

        EtabsInspectionHandle Done(string state, string diagnostic) => new(Task.FromResult(new EtabsInspectionResult(state, diagnostic, path, null, true)), Task.CompletedTask);
    }
}
