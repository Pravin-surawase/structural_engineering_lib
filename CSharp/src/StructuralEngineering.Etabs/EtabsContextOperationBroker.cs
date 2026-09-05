using System.Security.Cryptography;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Etabs;

public sealed record EtabsContextBrokerResult(
    EtabsContextWorkerState State,
    string? DiagnosticCode,
    string? Message,
    string EvidencePath,
    bool CleanupCompleted,
    EtabsContextArtifact? Artifact);

public sealed class EtabsContextOperationHandle
{
    internal EtabsContextOperationHandle(Task<EtabsContextBrokerResult> completion, Task quiescence) { Completion = completion; Quiescence = quiescence; }
    public Task<EtabsContextBrokerResult> Completion { get; }
    public Task Quiescence { get; }
}

/// <summary>Context-only sibling of the retained raw-v1 broker. It shares the same PID lease and STA boundary.</summary>
public sealed class EtabsContextOperationBroker(TimeProvider? timeProvider = null)
{
    private readonly TimeProvider _timeProvider = timeProvider ?? TimeProvider.System;

    public EtabsContextOperationHandle StartLive(EtabsHostExpectation expectation, EtabsContextCaptureRequest contextRequest, string operationId, string evidencePath, CancellationToken cancellationToken = default) =>
        Start(new EtabsBrokerRequest(operationId, expectation.ProcessId, contextRequest.DeadlineUtc, evidencePath),
            () => EtabsReflectionGetterHost.AttachContext(expectation),
            (host, token) => EtabsContextCapture.Run(host, contextRequest, token), cancellationToken);

    public EtabsContextOperationHandle Start(EtabsBrokerRequest request, Func<IEtabsGetterHost> hostFactory,
        Func<IEtabsGetterHost, CancellationToken, EtabsContextInventory> acquire, CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(request); ArgumentNullException.ThrowIfNull(hostFactory); ArgumentNullException.ThrowIfNull(acquire);
        var path = Path.GetFullPath(request.EvidencePath);
        if (request.DeadlineUtc <= _timeProvider.GetUtcNow()) return Done(new(EtabsContextWorkerState.Rejected, "ETABS.CALL_TIMEOUT", "The deadline elapsed before dispatch.", path, true, null));
        if (File.Exists(path) || File.Exists(path + ".getters.jsonl")) return Done(new(EtabsContextWorkerState.Rejected, "ETABS.EVIDENCE_EXISTS", "The context evidence already exists.", path, true, null));
        if (!EtabsProcessLease.TryAcquire(request.ProcessId, out var lease)) return Done(new(EtabsContextWorkerState.LeaseUnavailable, "ETABS.LEASE_UNAVAILABLE", "The selected ETABS process has an active operation.", path, true, null));

        var completion = new TaskCompletionSource<EtabsContextBrokerResult>(TaskCreationOptions.RunContinuationsAsynchronously);
        var quiescence = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        var deadline = new CancellationTokenSource();
        var linked = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken, deadline.Token);
        var gate = new object(); var terminal = false;
        void Terminal(EtabsContextBrokerResult result) { lock (gate) { if (!terminal) { terminal = true; completion.TrySetResult(result); } } }
        _ = Monitor();
        var registration = cancellationToken.Register(() => { linked.Cancel(); Terminal(new(EtabsContextWorkerState.Cancelled, "ETABS.CANCELLED", "Cancellation requested; cleanup continues.", path, false, null)); });
        var thread = new Thread(Worker) { IsBackground = true, Name = $"ETABS-CONTEXT-STA-{request.ProcessId}-{request.OperationId}" };
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
                    Terminal(new(EtabsContextWorkerState.TransactionUncertain, "ETABS.CALL_TIMEOUT", "The context deadline elapsed; cleanup continues and no artifact is accepted.", path, false, null));
                }
            }
            catch (ObjectDisposedException)
            {
            }
        }

        void Worker()
        {
            IEtabsGetterHost? host = null; EtabsContextInventory? inventory = null; Exception? failure = null; var disposed = false;
            var journalPath = path + ".getters.jsonl";
            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(path) ?? throw new InvalidOperationException("The evidence path has no parent directory."));
                EtabsOperationBroker.StaMessagePump.Drain();
                linked.Token.ThrowIfCancellationRequested();
                host = hostFactory();
                if (host.InspectIdentity().ProcessId != request.ProcessId) throw new InvalidOperationException("The attached ETABS process differs from the lease.");
                var before = host.InspectIdentity();
                int calls;
                using (var journal = new EtabsContextJournalHost(host, journalPath, request.OperationId))
                {
                    inventory = acquire(journal, linked.Token);
                    calls = journal.ReturnedCalls;
                }
                if (host.InspectIdentity() != before) throw new InvalidOperationException("The source identity changed during context capture.");
                using (var stream = File.OpenRead(journalPath))
                    inventory = inventory with { Provenance = new(EtabsContextGetterMatrix.Sha256, Path.GetFileName(journalPath), Convert.ToHexStringLower(SHA256.HashData(stream)), calls) };
                linked.Token.ThrowIfCancellationRequested();
            }
            catch (Exception exception) { failure = exception; }
            finally
            {
                try { host?.Dispose(); disposed = host is not null; } catch (Exception exception) { failure ??= exception; }
                EtabsOperationBroker.StaMessagePump.Drain();
                try { lease!.Dispose(); } catch (Exception exception) { failure ??= exception; }
            }
            try
            {
                if (failure is null && inventory is not null && !linked.IsCancellationRequested && _timeProvider.GetUtcNow() < request.DeadlineUtc)
                {
                    var artifact = EtabsContextWorkerCodec.CreateArtifact(inventory);
                    var bytes = EtabsContextWorkerCodec.CanonicalArtifactJsonBytes(artifact);
                    var temporary = path + $".{Guid.NewGuid():N}.tmp";
                    try
                    {
                        using (var stream = new FileStream(temporary, FileMode.CreateNew, FileAccess.Write, FileShare.None, 4096, FileOptions.WriteThrough)) { stream.Write(bytes); stream.Flush(true); }
                        lock (gate)
                        {
                            if (!terminal && !linked.IsCancellationRequested && _timeProvider.GetUtcNow() < request.DeadlineUtc)
                            {
                                File.Move(temporary, path);
                                Terminal(new(EtabsContextWorkerState.Completed, null, null, path, disposed, artifact));
                            }
                        }
                    }
                    finally { if (File.Exists(temporary)) File.Delete(temporary); }
                }
                else if (failure is not null && !terminal)
                    Terminal(new(linked.IsCancellationRequested ? EtabsContextWorkerState.TransactionUncertain : EtabsContextWorkerState.Fenced,
                        linked.IsCancellationRequested ? "ETABS.CALL_TIMEOUT" : "ETABS.CALL_FAILED", $"{failure.GetType().Name}: {failure.Message}", path, disposed, null));
                Terminal(new(EtabsContextWorkerState.TransactionUncertain, "ETABS.CALL_TIMEOUT", "Context completed after cancellation or its deadline; no artifact was accepted.", path, disposed, null));
            }
            catch (Exception exception)
            {
                Terminal(new(EtabsContextWorkerState.Fenced, "ETABS.EVIDENCE_WRITE_FAILED", $"{exception.GetType().Name}: {exception.Message}", path, disposed, null));
            }
            finally { registration.Dispose(); linked.Dispose(); deadline.Dispose(); quiescence.TrySetResult(); }
        }
    }

    private static EtabsContextOperationHandle Done(EtabsContextBrokerResult result) => new(Task.FromResult(result), Task.CompletedTask);
}
