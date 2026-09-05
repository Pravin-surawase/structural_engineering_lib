using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;

namespace StructuralEngineering.Etabs;

public enum EtabsBrokerState
{
    Completed,
    Rejected,
    Fenced,
    TransactionUncertain,
    Cancelled,
    LeaseUnavailable
}

public sealed record EtabsBrokerRequest(
    string OperationId,
    int ProcessId,
    DateTimeOffset DeadlineUtc,
    string EvidencePath);

public sealed record EtabsCleanupEvidence(
    bool HostDisposed,
    bool LeaseReleased,
    string MessagePump,
    string ApartmentState);

public sealed record EtabsRawAcquisitionContent(
    string OperationId,
    string LeaseKey,
    DateTimeOffset StartedUtc,
    DateTimeOffset CompletedUtc,
    string GetterMatrixSha256,
    EtabsHostIdentity HostIdentityBefore,
    EtabsHostIdentity HostIdentityAfter,
    SnapshotCallLedger CallLedger,
    EtabsLiveGetterProbeCapture Capture,
    EtabsCleanupEvidence Cleanup);

public sealed record EtabsDurableRawArtifact(
    string SchemaVersion,
    string ArtifactSha256,
    EtabsRawAcquisitionContent Content);

public sealed record EtabsBrokerResult(
    EtabsBrokerState State,
    string? DiagnosticCode,
    string? Message,
    string EvidencePath,
    string JournalPath,
    bool CleanupCompleted,
    EtabsDurableRawArtifact? Artifact);

public sealed class EtabsOperationHandle
{
    internal EtabsOperationHandle(Task<EtabsBrokerResult> completion, Task quiescence)
    {
        Completion = completion;
        Quiescence = quiescence;
    }

    public Task<EtabsBrokerResult> Completion { get; }
    public Task Quiescence { get; }
}

public static class EtabsAcquisitionArtifactCodec
{
    private const string SchemaVersion = "structural.etabs_durable_raw_artifact/v1";
    private static readonly JsonSerializerOptions JsonOptions = CreateOptions();

    public static EtabsDurableRawArtifact Create(EtabsRawAcquisitionContent content)
    {
        ArgumentNullException.ThrowIfNull(content);
        var sha256 = Convert.ToHexStringLower(SHA256.HashData(
            CanonicalArtifactBytes(new ArtifactHashBasis(SchemaVersion, content))));
        return new(
            SchemaVersion,
            sha256,
            content);
    }

    public static EtabsDurableRawArtifact ParseAndValidate(string json)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(json);
        using (var document = JsonDocument.Parse(json))
            EnsureNoDuplicateProperties(document.RootElement);
        var artifact = JsonSerializer.Deserialize<EtabsDurableRawArtifact>(json, JsonOptions)
            ?? throw new JsonException("The durable ETABS artifact cannot be null.");
        if (artifact.SchemaVersion != SchemaVersion ||
            artifact.Content is null ||
            artifact.ArtifactSha256 != Create(artifact.Content).ArtifactSha256)
            throw new InvalidDataException("The durable ETABS artifact identity is invalid.");
        ValidateContent(artifact.Content);
        return artifact;
    }

    public static byte[] CanonicalJsonBytes(EtabsDurableRawArtifact artifact) =>
        CanonicalArtifactBytes(artifact);

    // Durable artifact v1 predates portable numeric normalization. Keep its exact
    // numeric spelling so already retained captures remain verifiable by their hashes.
    private static byte[] CanonicalArtifactBytes(object value)
    {
        var element = JsonSerializer.SerializeToElement(value, JsonOptions);
        string Canonical(JsonElement item) => item.ValueKind switch
        {
            JsonValueKind.Object => "{" + string.Join(',', item.EnumerateObject().OrderBy(property => property.Name, StringComparer.Ordinal)
                .Select(property => Canonical(JsonSerializer.SerializeToElement(property.Name)) + ":" + Canonical(property.Value))) + "}",
            JsonValueKind.Array => "[" + string.Join(',', item.EnumerateArray().Select(Canonical)) + "]",
            JsonValueKind.Number => item.GetDouble() == 0 ? "0" : item.GetRawText(),
            JsonValueKind.String => Encoding.UTF8.GetString(AnalysisSnapshotCodec.CanonicalJsonBytes(item.GetString()!)),
            _ => item.GetRawText()
        };
        return Encoding.UTF8.GetBytes(Canonical(element));
    }

    private static void ValidateContent(EtabsRawAcquisitionContent content)
    {
        var ledger = content.CallLedger;
        if (string.IsNullOrWhiteSpace(content.OperationId) ||
            string.IsNullOrWhiteSpace(content.LeaseKey) ||
            content.StartedUtc >= content.CompletedUtc ||
            content.GetterMatrixSha256 != EtabsGetterMatrix.Sha256 ||
            content.HostIdentityBefore != content.HostIdentityAfter ||
            content.Capture is null ||
            content.Capture.HostIdentity != content.HostIdentityBefore ||
            content.Capture.GetterMatrixSha256 != content.GetterMatrixSha256 ||
            content.Capture.Preflight.Sha256 != content.Capture.Postflight.Sha256 ||
            !content.Cleanup.HostDisposed ||
            !content.Cleanup.LeaseReleased ||
            content.Cleanup.ApartmentState != "STA" ||
            content.Cleanup.MessagePump != "win32-peekmessage/v1" ||
            ledger is null ||
            ledger.OperationId != content.OperationId ||
            ledger.RecordCount != ledger.Records.Count ||
            ledger.Records.Count == 0 ||
            ledger.Records.Count % 2 != 0 ||
            !ledger.Records.Select(item => item.Sequence).SequenceEqual(
                Enumerable.Range(1, ledger.Records.Count)))
            throw new InvalidDataException("The durable ETABS artifact is incomplete or not postflight-clean.");

        string? previous = null;
        for (var index = 0; index < ledger.Records.Count; index += 2)
        {
            var started = ledger.Records[index];
            var returned = ledger.Records[index + 1];
            if (started.Stage != SnapshotCallStage.Started ||
                returned.Stage != SnapshotCallStage.Returned ||
                started.CallId != returned.CallId ||
                started.Method != returned.Method ||
                started.OperationId != content.OperationId ||
                returned.OperationId != content.OperationId ||
                started.Effect != SnapshotCallEffect.Getter ||
                returned.Effect != SnapshotCallEffect.Getter ||
                started.PreviousRecordSha256 != previous ||
                returned.PreviousRecordSha256 != started.RecordSha256 ||
                started.ReturnCode is not null ||
                started.RawShape is not null ||
                returned.ReturnCode != 0 ||
                string.IsNullOrWhiteSpace(returned.RawShape) ||
                started.ArgumentsSha256 != returned.ArgumentsSha256 ||
                started.SignatureAuthoritySha256 != EtabsGetterMatrix.Sha256 ||
                returned.SignatureAuthoritySha256 != EtabsGetterMatrix.Sha256 ||
                started.RecordSha256 != AnalysisSnapshotCodec.CallRecordSha256(started) ||
                returned.RecordSha256 != AnalysisSnapshotCodec.CallRecordSha256(returned))
                throw new InvalidDataException("The durable ETABS call ledger is unpaired, failed, or hash-invalid.");
            previous = returned.RecordSha256;
        }
        if (ledger.HeadRecordSha256 != previous ||
            ledger.LedgerSha256 != AnalysisSnapshotCodec.CallLedgerSha256(ledger))
            throw new InvalidDataException("The durable ETABS call-ledger head or digest is invalid.");

        var returnedMethods = ledger.Records
            .Where(item => item.Stage == SnapshotCallStage.Returned)
            .Select(item => item.Method);
        if (!returnedMethods.SequenceEqual(
                content.Capture.Calls.Select(item => item.Operation),
                StringComparer.Ordinal))
            throw new InvalidDataException("The durable ledger and raw getter capture disagree.");
    }

    private static JsonSerializerOptions CreateOptions()
    {
        var options = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
            PropertyNameCaseInsensitive = false,
            UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow
        };
        options.Converters.Add(new JsonStringEnumConverter(JsonNamingPolicy.SnakeCaseLower));
        return options;
    }

    private static void EnsureNoDuplicateProperties(JsonElement value)
    {
        if (value.ValueKind == JsonValueKind.Object)
        {
            var names = new HashSet<string>(StringComparer.Ordinal);
            foreach (var property in value.EnumerateObject())
            {
                if (!names.Add(property.Name))
                    throw new JsonException($"Duplicate JSON property {property.Name} is not allowed.");
                EnsureNoDuplicateProperties(property.Value);
            }
        }
        else if (value.ValueKind == JsonValueKind.Array)
        {
            foreach (var item in value.EnumerateArray())
                EnsureNoDuplicateProperties(item);
        }
    }

    private sealed record ArtifactHashBasis(
        string SchemaVersion,
        EtabsRawAcquisitionContent Content);
}

public sealed class EtabsOperationBroker
{
    private readonly TimeProvider _timeProvider;

    public EtabsOperationBroker(TimeProvider? timeProvider = null) =>
        _timeProvider = timeProvider ?? TimeProvider.System;

    public EtabsOperationHandle StartLive(
        EtabsHostExpectation expectation,
        EtabsLiveGetterProbeRequest probeRequest,
        string operationId,
        string evidencePath,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(expectation);
        ArgumentNullException.ThrowIfNull(probeRequest);
        if (probeRequest.DeadlineUtc <= _timeProvider.GetUtcNow())
            throw new ArgumentException("The live acquisition deadline has already elapsed.", nameof(probeRequest));
        return Start(
            new(operationId, expectation.ProcessId, probeRequest.DeadlineUtc, evidencePath),
            () => EtabsReflectionGetterHost.Attach(expectation),
            (host, token) => EtabsLiveGetterProbe.Run(host, probeRequest, token),
            cancellationToken);
    }

    public EtabsOperationHandle Start(
        EtabsBrokerRequest request,
        Func<IEtabsGetterHost> hostFactory,
        Func<IEtabsGetterHost, CancellationToken, EtabsLiveGetterProbeCapture> acquire,
        CancellationToken cancellationToken = default)
    {
        Validate(request, hostFactory, acquire);
        var evidencePath = Path.GetFullPath(request.EvidencePath);
        var journalPath = evidencePath + ".journal.jsonl";
        if (request.DeadlineUtc <= _timeProvider.GetUtcNow())
            return CompletedHandle(new(
                EtabsBrokerState.Rejected,
                "ETABS.CALL_TIMEOUT",
                "The acquisition deadline elapsed before the process lease; no host call was issued.",
                evidencePath,
                journalPath,
                true,
                null));
        if (File.Exists(evidencePath) || File.Exists(journalPath))
            return CompletedHandle(new(
                EtabsBrokerState.Rejected,
                "ETABS.EVIDENCE_EXISTS",
                "The final artifact or durable journal already exists; no host call was issued.",
                evidencePath,
                journalPath,
                true,
                null));

        if (!EtabsProcessLease.TryAcquire(request.ProcessId, out var processLease))
            return CompletedHandle(new(
                EtabsBrokerState.LeaseUnavailable,
                "ETABS.LEASE_UNAVAILABLE",
                $"Process {request.ProcessId} already has an active acquisition lease.",
                evidencePath,
                journalPath,
                true,
                null));

        var completion = new TaskCompletionSource<EtabsBrokerResult>(TaskCreationOptions.RunContinuationsAsynchronously);
        var quiescence = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        var deadlineCancellation = new CancellationTokenSource();
        var linkedCancellation = CancellationTokenSource.CreateLinkedTokenSource(
            cancellationToken,
            deadlineCancellation.Token);
        var completionGate = new object();
        var terminalChosen = false;

        void ChooseTerminal(EtabsBrokerResult result)
        {
            lock (completionGate)
            {
                if (terminalChosen)
                    return;
                terminalChosen = true;
                completion.TrySetResult(result);
            }
        }

        _ = MonitorDeadlineAsync();
        var cancellationRegistration = cancellationToken.Register(() =>
        {
            linkedCancellation.Cancel();
            ChooseTerminal(new(
                EtabsBrokerState.Cancelled,
                "ETABS.CANCELLED",
                "The caller cancelled the acquisition; cleanup continues under the held process lease.",
                evidencePath,
                journalPath,
                false,
                null));
        });

        var thread = new Thread(RunWorker)
        {
            IsBackground = true,
            Name = $"ETABS-STA-{request.ProcessId}-{request.OperationId}"
        };
        thread.SetApartmentState(ApartmentState.STA);
        thread.Start();
        return new(completion.Task, quiescence.Task);

        async Task MonitorDeadlineAsync()
        {
            var delay = request.DeadlineUtc - _timeProvider.GetUtcNow();
            if (delay > TimeSpan.Zero)
                await Task.Delay(delay).ConfigureAwait(false);
            deadlineCancellation.Cancel();
            ChooseTerminal(new(
                EtabsBrokerState.TransactionUncertain,
                "ETABS.CALL_TIMEOUT",
                "The acquisition deadline elapsed; no final artifact is accepted and cleanup continues under the held process lease.",
                evidencePath,
                journalPath,
                false,
                null));
        }

        void RunWorker()
        {
            var started = _timeProvider.GetUtcNow();
            var apartment = Thread.CurrentThread.GetApartmentState().ToString();
            IEtabsGetterHost? host = null;
            EtabsHostIdentity? before = null;
            EtabsHostIdentity? after = null;
            EtabsLiveGetterProbeCapture? capture = null;
            SnapshotCallLedger? ledger = null;
            Exception? operationError = null;
            Exception? cleanupError = null;
            var hostDisposed = false;
            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(evidencePath)
                    ?? throw new InvalidOperationException("The evidence path has no parent directory."));
                using var journal = new EtabsCallJournal(request.OperationId, journalPath, _timeProvider);
                StaMessagePump.Drain();
                linkedCancellation.Token.ThrowIfCancellationRequested();
                host = hostFactory() ?? throw new InvalidOperationException("The ETABS host factory returned null.");
                before = host.InspectIdentity();
                if (before.ProcessId != request.ProcessId)
                    throw new InvalidOperationException("The attached ETABS process differs from the leased process.");
                var ledgerHost = new LedgerEtabsGetterHost(host, journal);
                capture = acquire(ledgerHost, linkedCancellation.Token);
                linkedCancellation.Token.ThrowIfCancellationRequested();
                if (host is IEtabsGetterHostCompletionVerifier completionVerifier)
                    completionVerifier.AssertComplete();
                after = host.InspectIdentity();
                ValidateCompletedCapture(capture, before, after);
                ledger = journal.Build();
            }
            catch (Exception exception)
            {
                operationError = exception;
            }
            finally
            {
                try
                {
                    host?.Dispose();
                    hostDisposed = host is not null;
                }
                catch (Exception exception)
                {
                    cleanupError = exception;
                }
                StaMessagePump.Drain();
            }

            EtabsDurableRawArtifact? artifact = null;
            string? temporaryPath = null;
            EtabsBrokerResult workerResult;
            if (cleanupError is not null)
            {
                workerResult = Failure(
                    EtabsBrokerState.Fenced,
                    "ETABS.RESTORATION_UNVERIFIED",
                    cleanupError,
                    false);
            }
            else if (operationError is not null)
            {
                var cancelled = operationError is OperationCanceledException || linkedCancellation.IsCancellationRequested;
                workerResult = Failure(
                    cancelled ? EtabsBrokerState.TransactionUncertain : EtabsBrokerState.Fenced,
                    cancelled ? "ETABS.CALL_TIMEOUT" : "ETABS.CALL_FAILED",
                    operationError,
                    host is null || hostDisposed);
            }
            else
            {
                try
                {
                    var content = new EtabsRawAcquisitionContent(
                        request.OperationId,
                        $"etabs-process:{request.ProcessId}",
                        started,
                        _timeProvider.GetUtcNow(),
                        EtabsGetterMatrix.Sha256,
                        before!,
                        after!,
                        ledger!,
                        capture!,
                        new(hostDisposed, true, StaMessagePump.Name, apartment));
                    artifact = EtabsAcquisitionArtifactCodec.Create(content);
                    temporaryPath = WriteTemporary(evidencePath, artifact);
                    workerResult = new(
                        EtabsBrokerState.Completed,
                        null,
                        null,
                        evidencePath,
                        journalPath,
                        true,
                        artifact);
                }
                catch (Exception exception)
                {
                    operationError = exception;
                    workerResult = Failure(
                        EtabsBrokerState.Fenced,
                        "ETABS.EVIDENCE_WRITE_FAILED",
                        exception,
                        hostDisposed);
                }
            }

            processLease!.Dispose();
            try
            {
                lock (completionGate)
                {
                    if (!terminalChosen && _timeProvider.GetUtcNow() < request.DeadlineUtc && !linkedCancellation.IsCancellationRequested)
                    {
                        if (temporaryPath is not null)
                        {
                            try
                            {
                                File.Move(temporaryPath, evidencePath);
                            }
                            catch (Exception exception)
                            {
                                workerResult = Failure(
                                    EtabsBrokerState.Fenced,
                                    "ETABS.EVIDENCE_WRITE_FAILED",
                                    exception,
                                    hostDisposed);
                                DeleteTemporary(temporaryPath);
                            }
                        }
                        terminalChosen = true;
                        completion.TrySetResult(workerResult);
                    }
                    else if (temporaryPath is not null && File.Exists(temporaryPath))
                    {
                        DeleteTemporary(temporaryPath);
                    }
                }
            }
            finally
            {
                cancellationRegistration.Dispose();
                linkedCancellation.Dispose();
                quiescence.TrySetResult();
            }

            EtabsBrokerResult Failure(
                EtabsBrokerState state,
                string code,
                Exception exception,
                bool cleanupCompleted) => new(
                    state,
                    code,
                    $"{exception.GetType().Name}: {exception.Message}",
                    evidencePath,
                    journalPath,
                    cleanupCompleted,
                    null);
        }
    }

    private static string WriteTemporary(string evidencePath, EtabsDurableRawArtifact artifact)
    {
        var temporaryPath = evidencePath + $".{Guid.NewGuid():N}.tmp";
        try
        {
            var bytes = EtabsAcquisitionArtifactCodec.CanonicalJsonBytes(artifact);
            using var stream = new FileStream(
                temporaryPath,
                FileMode.CreateNew,
                FileAccess.Write,
                FileShare.None,
                4096,
                FileOptions.WriteThrough);
            stream.Write(bytes);
            stream.Flush(flushToDisk: true);
            return temporaryPath;
        }
        catch
        {
            DeleteTemporary(temporaryPath);
            throw;
        }
    }

    private static void DeleteTemporary(string path)
    {
        try
        {
            if (File.Exists(path))
                File.Delete(path);
        }
        catch (IOException)
        {
        }
        catch (UnauthorizedAccessException)
        {
        }
    }

    private static void ValidateCompletedCapture(
        EtabsLiveGetterProbeCapture capture,
        EtabsHostIdentity before,
        EtabsHostIdentity after)
    {
        ArgumentNullException.ThrowIfNull(capture);
        if (capture.Verdict != "LIVE_GETTER_MATRIX_COMPLETED_NO_GENERAL_COMPATIBILITY_CLAIM" ||
            capture.GetterMatrixSha256 != EtabsGetterMatrix.Sha256 ||
            capture.Preflight.Sha256 != capture.Postflight.Sha256 ||
            capture.HostIdentity != before ||
            before != after)
            throw new InvalidOperationException("The acquisition failed its exact identity or postflight fence.");
    }

    private static void Validate(
        EtabsBrokerRequest request,
        Func<IEtabsGetterHost> hostFactory,
        Func<IEtabsGetterHost, CancellationToken, EtabsLiveGetterProbeCapture> acquire)
    {
        ArgumentNullException.ThrowIfNull(request);
        ArgumentNullException.ThrowIfNull(hostFactory);
        ArgumentNullException.ThrowIfNull(acquire);
        if (string.IsNullOrWhiteSpace(request.OperationId))
            throw new ArgumentException("The operation identity is required.", nameof(request));
        if (request.ProcessId <= 0)
            throw new ArgumentException("The exact ETABS process identity is required.", nameof(request));
        if (request.DeadlineUtc == default)
            throw new ArgumentException("The acquisition deadline is required.", nameof(request));
        if (string.IsNullOrWhiteSpace(request.EvidencePath))
            throw new ArgumentException("The evidence path is required.", nameof(request));
    }

    private static EtabsOperationHandle CompletedHandle(EtabsBrokerResult result) =>
        new(Task.FromResult(result), Task.CompletedTask);

    private sealed class LedgerEtabsGetterHost(
        IEtabsGetterHost inner,
        EtabsCallJournal journal) : IEtabsGetterHost
    {
        public EtabsHostIdentity Identity => inner.Identity;
        public EtabsHostIdentity InspectIdentity() => inner.InspectIdentity();

        public EtabsInvocation Invoke(
            EtabsGetterDefinition definition,
            IReadOnlyList<object?> inputs,
            CancellationToken cancellationToken)
        {
            var callId = journal.WriteStarted(definition, inputs);
            try
            {
                StaMessagePump.Drain();
                var invocation = inner.Invoke(definition, inputs, cancellationToken);
                var returnCode = definition.ReturnSemantics == EtabsReturnSemantics.FinalCsiReturnCode
                    ? invocation.ReturnValue as int?
                    : 0;
                journal.WriteReturned(
                    definition,
                    callId,
                    returnCode ?? int.MinValue,
                    RawShape(definition, invocation));
                return invocation;
            }
            catch (Exception exception)
            {
                journal.WriteReturned(
                    definition,
                    callId,
                    int.MinValue,
                    $"exception:{exception.GetType().FullName}");
                throw;
            }
            finally
            {
                StaMessagePump.Drain();
            }
        }

        public void Dispose()
        {
        }

        private static string RawShape(EtabsGetterDefinition definition, EtabsInvocation invocation)
        {
            static string Shape(object? value) => value switch
            {
                null => "null",
                Array array => $"{value.GetType().GetElementType()?.FullName ?? "array"}[{array.Length}]",
                _ => value.GetType().FullName ?? value.GetType().Name
            };
            return string.Join(
                ';',
                $"return={Shape(invocation.ReturnValue)}",
                definition.OutputNames.Select((name, index) => $"{name}={Shape(invocation.Outputs[index])}"));
        }
    }

    private sealed class EtabsCallJournal : IDisposable
    {
        private readonly string _operationId;
        private readonly FileStream _stream;
        private readonly TimeProvider _timeProvider;
        private readonly List<SnapshotCallRecord> _records = [];
        private string? _head;
        private string? _pendingCallId;

        public EtabsCallJournal(string operationId, string path, TimeProvider timeProvider)
        {
            _operationId = operationId;
            _timeProvider = timeProvider;
            _stream = new FileStream(
                path,
                FileMode.CreateNew,
                FileAccess.Write,
                FileShare.Read,
                4096,
                FileOptions.WriteThrough);
        }

        public string WriteStarted(EtabsGetterDefinition definition, IReadOnlyList<object?> inputs)
        {
            if (_pendingCallId is not null)
                throw new InvalidOperationException("A getter start cannot overlap another getter call.");
            var callId = $"{_operationId}:call:{(_records.Count / 2) + 1:D6}";
            var argumentsSha = Convert.ToHexStringLower(SHA256.HashData(
                AnalysisSnapshotCodec.CanonicalJsonBytes(inputs)));
            Append(new(
                "structural.analysis_call_record/v1",
                _operationId,
                callId,
                _records.Count + 1,
                _head,
                SnapshotCallStage.Started,
                definition.Operation,
                EtabsGetterMatrix.Sha256,
                SnapshotCallEffect.Getter,
                argumentsSha,
                null,
                null,
                _timeProvider.GetUtcNow().ToString("O"),
                new string('0', 64)));
            _pendingCallId = callId;
            return callId;
        }

        public void WriteReturned(
            EtabsGetterDefinition definition,
            string callId,
            int returnCode,
            string rawShape)
        {
            if (_pendingCallId != callId)
                throw new InvalidOperationException("The getter return does not match the pending getter start.");
            var started = _records[^1];
            Append(new(
                "structural.analysis_call_record/v1",
                _operationId,
                callId,
                _records.Count + 1,
                _head,
                SnapshotCallStage.Returned,
                definition.Operation,
                EtabsGetterMatrix.Sha256,
                SnapshotCallEffect.Getter,
                started.ArgumentsSha256,
                returnCode,
                rawShape,
                _timeProvider.GetUtcNow().ToString("O"),
                new string('0', 64)));
            _pendingCallId = null;
        }

        public SnapshotCallLedger Build()
        {
            if (_pendingCallId is not null)
                throw new InvalidOperationException("The durable getter journal has an unmatched start record.");
            var ledger = new SnapshotCallLedger(
                "structural.analysis_call_ledger/v1",
                _operationId,
                _records.Count,
                _head,
                new string('0', 64),
                _records.ToArray());
            return ledger with { LedgerSha256 = AnalysisSnapshotCodec.CallLedgerSha256(ledger) };
        }

        public void Dispose()
        {
            _stream.Flush(flushToDisk: true);
            _stream.Dispose();
        }

        private void Append(SnapshotCallRecord record)
        {
            var finalized = record with { RecordSha256 = AnalysisSnapshotCodec.CallRecordSha256(record) };
            var bytes = AnalysisSnapshotCodec.CanonicalJsonBytes(finalized);
            _stream.Write(bytes);
            _stream.WriteByte((byte)'\n');
            _stream.Flush(flushToDisk: true);
            _records.Add(finalized);
            _head = finalized.RecordSha256;
        }
    }

    internal static class StaMessagePump
    {
        private const uint RemoveMessage = 0x0001;
        public const string Name = "win32-peekmessage/v1";

        public static void Drain()
        {
            if (!OperatingSystem.IsWindows())
                return;
            while (PeekMessage(out var message, IntPtr.Zero, 0, 0, RemoveMessage))
            {
                TranslateMessage(in message);
                DispatchMessage(in message);
            }
        }

        [DllImport("user32.dll")]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool PeekMessage(
            out Message message,
            IntPtr window,
            uint minimum,
            uint maximum,
            uint remove);

        [DllImport("user32.dll")]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool TranslateMessage(in Message message);

        [DllImport("user32.dll")]
        private static extern IntPtr DispatchMessage(in Message message);

        [StructLayout(LayoutKind.Sequential)]
        private struct Message
        {
            public IntPtr Window;
            public uint Id;
            public nuint WParam;
            public nint LParam;
            public uint Time;
            public Point Position;
            public uint Private;
        }

        [StructLayout(LayoutKind.Sequential)]
        private struct Point
        {
            public int X;
            public int Y;
        }
    }
}
