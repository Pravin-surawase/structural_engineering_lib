using StructuralEngineering.Contracts;

namespace StructuralEngineering.Etabs;

public sealed record EtabsBatchBrokerResult(EtabsContextWorkerState State, string? DiagnosticCode, string? Message,
    string EvidencePath, bool CleanupCompleted, EtabsBatchArtifact? Artifact);

public sealed class EtabsBatchOperationHandle
{
    internal EtabsBatchOperationHandle(Task<EtabsBatchBrokerResult> completion, Task quiescence) { Completion = completion; Quiescence = quiescence; }
    public Task<EtabsBatchBrokerResult> Completion { get; }
    public Task Quiescence { get; }
}

/// <summary>Shared force acquisition on one leased STA. A deadline ends acceptance, never a running COM call.</summary>
public sealed class EtabsBatchOperationBroker(TimeProvider? timeProvider = null)
{
    private readonly TimeProvider _timeProvider = timeProvider ?? TimeProvider.System;

    public EtabsBatchOperationHandle Start(EtabsBrokerRequest request, Func<IEtabsGetterHost> hostFactory,
        Func<IEtabsGetterHost, CancellationToken, EtabsBatchCapture> acquire, CancellationToken cancellationToken = default,
        string? getterMatrixSha256 = null)
    {
        ArgumentNullException.ThrowIfNull(request); ArgumentNullException.ThrowIfNull(hostFactory); ArgumentNullException.ThrowIfNull(acquire);
        var path = Path.GetFullPath(request.EvidencePath);
        var journalPath = path + ".journal.jsonl";
        if (request.DeadlineUtc <= _timeProvider.GetUtcNow()) return Done(new(EtabsContextWorkerState.Rejected, "ETABS.CALL_TIMEOUT", "The deadline elapsed before dispatch.", path, true, null));
        if (File.Exists(path) || File.Exists(journalPath)) return Done(new(EtabsContextWorkerState.Rejected, "ETABS.EVIDENCE_EXISTS", "The force evidence already exists.", path, true, null));
        if (!EtabsProcessLease.TryAcquire(request.ProcessId, out var lease)) return Done(new(EtabsContextWorkerState.LeaseUnavailable, "ETABS.LEASE_UNAVAILABLE", "The selected ETABS process has an active operation.", path, true, null));

        var completion = new TaskCompletionSource<EtabsBatchBrokerResult>(TaskCreationOptions.RunContinuationsAsynchronously);
        var quiescence = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        var deadline = new CancellationTokenSource();
        var linked = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken, deadline.Token);
        var gate = new object(); var terminal = false;
        void Terminal(EtabsBatchBrokerResult result) { lock (gate) { if (!terminal) { terminal = true; completion.TrySetResult(result); } } }
        _ = Monitor();
        var registration = cancellationToken.Register(() => Terminal(new(EtabsContextWorkerState.Cancelled, "ETABS.CANCELLED", "Cancellation requested; cleanup continues.", path, false, null)));
        var thread = new Thread(Worker) { IsBackground = true, Name = $"ETABS-FORCES-STA-{request.ProcessId}-{request.OperationId}" };
        thread.SetApartmentState(ApartmentState.STA); thread.Start();
        return new(completion.Task, quiescence.Task);

        async Task Monitor()
        {
            try
            {
                var delay = request.DeadlineUtc - _timeProvider.GetUtcNow();
                if (delay > TimeSpan.Zero) await Task.Delay(delay).ConfigureAwait(false);
                if (!quiescence.Task.IsCompleted)
                {
                    deadline.Cancel();
                    Terminal(new(EtabsContextWorkerState.TransactionUncertain, "ETABS.CALL_TIMEOUT", "The force deadline elapsed; cleanup continues and no artifact is accepted.", path, false, null));
                }
            }
            catch (ObjectDisposedException) { }
        }

        void Worker()
        {
            var started = _timeProvider.GetUtcNow();
            IEtabsGetterHost? host = null; EtabsBatchCapture? capture = null; SnapshotCallLedger? ledger = null;
            EtabsHostIdentity? before = null; EtabsHostIdentity? after = null;
            Exception? failure = null; var disposed = false; var released = false;
            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(path) ?? throw new InvalidOperationException("The evidence path has no parent directory."));
                EtabsOperationBroker.StaMessagePump.Drain(); linked.Token.ThrowIfCancellationRequested();
                host = hostFactory(); before = host.InspectIdentity();
                if (before.ProcessId != request.ProcessId) throw new InvalidOperationException("The attached ETABS process differs from the lease.");
                using (var journal = new EtabsOperationBroker.EtabsCallJournal(request.OperationId, journalPath, _timeProvider, getterMatrixSha256 ?? EtabsForceGetterMatrix.Sha256))
                using (var journalHost = new EtabsOperationBroker.LedgerEtabsGetterHost(host, journal))
                {
                    capture = acquire(journalHost, linked.Token);
                    ledger = journal.Build();
                }
                after = host.InspectIdentity();
                if (after != before) throw new InvalidOperationException("The source identity changed during the force capture.");
                linked.Token.ThrowIfCancellationRequested();
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
                if (failure is null && capture is not null && ledger is not null && before is not null && after is not null &&
                    !linked.IsCancellationRequested && _timeProvider.GetUtcNow() < request.DeadlineUtc)
                {
                    var artifact = EtabsBatchArtifactCodec.Create(new(request.OperationId, $"etabs-process:{request.ProcessId}", started,
                        _timeProvider.GetUtcNow(), before, after, ledger, capture,
                        new(disposed, released, EtabsOperationBroker.StaMessagePump.Name, Thread.CurrentThread.GetApartmentState().ToString())));
                    var bytes = EtabsBatchArtifactCodec.CanonicalJsonBytes(artifact);
                    var temporary = path + $".{Guid.NewGuid():N}.tmp";
                    try
                    {
                        using (var stream = new FileStream(temporary, FileMode.CreateNew, FileAccess.Write, FileShare.None, 4096, FileOptions.WriteThrough)) { stream.Write(bytes); stream.Flush(true); }
                        lock (gate)
                        {
                            if (!terminal && !linked.IsCancellationRequested && _timeProvider.GetUtcNow() < request.DeadlineUtc)
                            {
                                File.Move(temporary, path);
                                Terminal(new(EtabsContextWorkerState.Completed, null, null, path, disposed && released, artifact));
                            }
                        }
                    }
                    finally { if (File.Exists(temporary)) File.Delete(temporary); }
                }
                else if (failure is not null && !terminal)
                    Terminal(new(linked.IsCancellationRequested ? EtabsContextWorkerState.TransactionUncertain : EtabsContextWorkerState.Fenced,
                        linked.IsCancellationRequested ? "ETABS.CALL_TIMEOUT" : "ETABS.CALL_FAILED", $"{failure.GetType().Name}: {failure.Message}", path, disposed && released, null));
                Terminal(new(EtabsContextWorkerState.TransactionUncertain, "ETABS.CALL_TIMEOUT", "Force capture completed after cancellation or its deadline; no artifact was accepted.", path, disposed && released, null));
            }
            catch (Exception exception) { Terminal(new(EtabsContextWorkerState.Fenced, "ETABS.EVIDENCE_WRITE_FAILED", $"{exception.GetType().Name}: {exception.Message}", path, disposed && released, null)); }
            finally { registration.Dispose(); linked.Dispose(); deadline.Dispose(); quiescence.TrySetResult(); }
        }
    }

    private static EtabsBatchOperationHandle Done(EtabsBatchBrokerResult result) => new(Task.FromResult(result), Task.CompletedTask);
}
