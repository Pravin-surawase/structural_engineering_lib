using System.Collections.ObjectModel;
using System.Diagnostics;
using System.Security.Cryptography;
using System.Text.Json;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;
using StructuralEngineering.Etabs;
using Xunit;

namespace StructAutomate.Tests;

public sealed class Wp10OperationBrokerTests
{
    private static int _nextProcessId = 90_000;

    [Fact]
    public async Task CompletedOperationUsesStaAndWritesOneValidatedArtifact()
    {
        var testDirectory = NewTestDirectory();
        try
        {
            var processId = NextProcessId();
            var host = new FakeHost(Identity(processId), (_, _) => new EtabsInvocation(6, []));
            var request = Request(processId, Path.Combine(testDirectory, "capture.json"));

            var handle = new EtabsOperationBroker().Start(
                request,
                () => host,
                (ledgerHost, token) => CaptureOneSuccessfulCall(ledgerHost, request.DeadlineUtc, token),
                TestContext.Current.CancellationToken);
            var result = await handle.Completion.WaitAsync(TimeSpan.FromSeconds(10), TestContext.Current.CancellationToken);
            await handle.Quiescence.WaitAsync(TimeSpan.FromSeconds(10), TestContext.Current.CancellationToken);

            Assert.Equal(EtabsBrokerState.Completed, result.State);
            Assert.True(result.CleanupCompleted);
            Assert.True(File.Exists(result.EvidencePath));
            Assert.True(File.Exists(result.JournalPath));
            Assert.Equal(1, host.DisposeCount);
            Assert.Equal(ApartmentState.STA, host.InvocationApartment);
            var artifact = EtabsAcquisitionArtifactCodec.ParseAndValidate(
                File.ReadAllText(result.EvidencePath));
            Assert.Equal("win32-peekmessage/v1", artifact.Content.Cleanup.MessagePump);
            Assert.Equal("STA", artifact.Content.Cleanup.ApartmentState);
            Assert.Equal(2, artifact.Content.CallLedger.RecordCount);
            Assert.Equal(
                [SnapshotCallStage.Started, SnapshotCallStage.Returned],
                artifact.Content.CallLedger.Records.Select(item => item.Stage));
            Assert.All(artifact.Content.CallLedger.Records, record =>
                Assert.Equal(record.RecordSha256, AnalysisSnapshotCodec.CallRecordSha256(record)));
            Assert.Equal(
                artifact.Content.CallLedger.LedgerSha256,
                AnalysisSnapshotCodec.CallLedgerSha256(artifact.Content.CallLedger));
            var artifactJson = File.ReadAllText(result.EvidencePath);
            Assert.Throws<InvalidDataException>(() =>
                EtabsAcquisitionArtifactCodec.ParseAndValidate(
                    artifactJson.Replace(
                        "\"lease_released\":true",
                        "\"lease_released\":false",
                        StringComparison.Ordinal)));
            Assert.Throws<JsonException>(() =>
                EtabsAcquisitionArtifactCodec.ParseAndValidate(
                    "{\"schema_version\":\"duplicate\"," + artifactJson[1..]));
            Assert.Empty(Directory.GetFiles(testDirectory, "*.tmp"));
        }
        finally
        {
            Directory.Delete(testDirectory, recursive: true);
        }
    }

    [Fact]
    public async Task ProcessLeaseRejectsConcurrentAcquisitionWithoutDispatch()
    {
        var testDirectory = NewTestDirectory();
        using var entered = new ManualResetEventSlim();
        using var release = new ManualResetEventSlim();
        try
        {
            var processId = NextProcessId();
            var firstHost = new FakeHost(Identity(processId), (_, _) =>
            {
                entered.Set();
                release.Wait(TestContext.Current.CancellationToken);
                return new EtabsInvocation(6, []);
            });
            var firstRequest = Request(processId, Path.Combine(testDirectory, "first.json"));
            var first = new EtabsOperationBroker().Start(
                firstRequest,
                () => firstHost,
                (host, token) => CaptureOneSuccessfulCall(host, firstRequest.DeadlineUtc, token),
                TestContext.Current.CancellationToken);
            Assert.True(entered.Wait(TimeSpan.FromSeconds(5), TestContext.Current.CancellationToken));

            var secondFactoryCalls = 0;
            var second = new EtabsOperationBroker().Start(
                Request(processId, Path.Combine(testDirectory, "second.json")),
                () =>
                {
                    Interlocked.Increment(ref secondFactoryCalls);
                    return new FakeHost(Identity(processId), (_, _) => new EtabsInvocation(6, []));
                },
                (host, token) => CaptureOneSuccessfulCall(host, DateTimeOffset.UtcNow.AddSeconds(5), token),
                TestContext.Current.CancellationToken);
            var secondResult = await second.Completion;

            Assert.Equal(EtabsBrokerState.LeaseUnavailable, secondResult.State);
            Assert.Equal(0, secondFactoryCalls);
            release.Set();
            Assert.Equal(EtabsBrokerState.Completed, (await first.Completion).State);
            await first.Quiescence;
        }
        finally
        {
            release.Set();
            Directory.Delete(testDirectory, recursive: true);
        }
    }

    [Fact]
    public async Task DeadlineFencesOutputAndHoldsLeaseUntilLateCallIsCleanedUp()
    {
        var testDirectory = NewTestDirectory();
        using var entered = new ManualResetEventSlim();
        using var release = new ManualResetEventSlim();
        try
        {
            var processId = NextProcessId();
            var host = new FakeHost(Identity(processId), (_, _) =>
            {
                entered.Set();
                release.Wait();
                return new EtabsInvocation(6, []);
            });
            var request = Request(
                processId,
                Path.Combine(testDirectory, "timed-out.json"),
                DateTimeOffset.UtcNow.AddMilliseconds(250));
            var handle = new EtabsOperationBroker().Start(
                request,
                () => host,
                (ledgerHost, token) => CaptureOneSuccessfulCall(ledgerHost, request.DeadlineUtc, token),
                TestContext.Current.CancellationToken);
            Assert.True(entered.Wait(TimeSpan.FromSeconds(5), TestContext.Current.CancellationToken));

            var result = await handle.Completion.WaitAsync(TimeSpan.FromSeconds(5), TestContext.Current.CancellationToken);
            Assert.Equal(EtabsBrokerState.TransactionUncertain, result.State);
            Assert.Equal("ETABS.CALL_TIMEOUT", result.DiagnosticCode);
            Assert.False(result.CleanupCompleted);
            Assert.False(File.Exists(result.EvidencePath));

            var blocked = new EtabsOperationBroker().Start(
                Request(processId, Path.Combine(testDirectory, "blocked.json")),
                () => throw new InvalidOperationException("must not dispatch"),
                (_, _) => throw new InvalidOperationException("must not acquire"),
                TestContext.Current.CancellationToken);
            Assert.Equal(EtabsBrokerState.LeaseUnavailable, (await blocked.Completion).State);

            release.Set();
            await handle.Quiescence.WaitAsync(TimeSpan.FromSeconds(5), TestContext.Current.CancellationToken);
            Assert.Equal(1, host.DisposeCount);
            Assert.False(File.Exists(result.EvidencePath));
        }
        finally
        {
            release.Set();
            Directory.Delete(testDirectory, recursive: true);
        }
    }

    [Fact]
    public async Task PostflightIdentityDriftRejectsFinalArtifact()
    {
        var testDirectory = NewTestDirectory();
        try
        {
            var processId = NextProcessId();
            var host = new FakeHost(Identity(processId), (_, _) => new EtabsInvocation(6, []));
            var request = Request(processId, Path.Combine(testDirectory, "drift.json"));
            var handle = new EtabsOperationBroker().Start(
                request,
                () => host,
                (ledgerHost, token) =>
                {
                    var capture = CaptureOneSuccessfulCall(ledgerHost, request.DeadlineUtc, token);
                    host.CurrentIdentity = host.CurrentIdentity with { ModelSha256 = new string('c', 64) };
                    return capture;
                },
                TestContext.Current.CancellationToken);

            var result = await handle.Completion;
            await handle.Quiescence;

            Assert.Equal(EtabsBrokerState.Fenced, result.State);
            Assert.Equal("ETABS.CALL_FAILED", result.DiagnosticCode);
            Assert.False(File.Exists(result.EvidencePath));
            Assert.Equal(1, host.DisposeCount);
        }
        finally
        {
            Directory.Delete(testDirectory, recursive: true);
        }
    }

    [Fact]
    public async Task CleanupFailureIsRestorationUnverifiedAndPublishesNothing()
    {
        var testDirectory = NewTestDirectory();
        try
        {
            var processId = NextProcessId();
            var host = new FakeHost(Identity(processId), (_, _) => new EtabsInvocation(6, []))
            {
                ThrowOnDispose = true
            };
            var request = Request(processId, Path.Combine(testDirectory, "cleanup.json"));
            var handle = new EtabsOperationBroker().Start(
                request,
                () => host,
                (ledgerHost, token) => CaptureOneSuccessfulCall(ledgerHost, request.DeadlineUtc, token),
                TestContext.Current.CancellationToken);

            var result = await handle.Completion;
            await handle.Quiescence;

            Assert.Equal(EtabsBrokerState.Fenced, result.State);
            Assert.Equal("ETABS.RESTORATION_UNVERIFIED", result.DiagnosticCode);
            Assert.False(result.CleanupCompleted);
            Assert.False(File.Exists(result.EvidencePath));
            Assert.Equal(1, host.DisposeCount);
        }
        finally
        {
            Directory.Delete(testDirectory, recursive: true);
        }
    }

    [Fact]
    public async Task ExistingEvidenceRejectsBeforeLeaseOrHostFactory()
    {
        var testDirectory = NewTestDirectory();
        try
        {
            var path = Path.Combine(testDirectory, "existing.json");
            File.WriteAllText(path, "owned evidence");
            var factoryCalls = 0;
            var request = Request(NextProcessId(), path);
            var handle = new EtabsOperationBroker().Start(
                request,
                () =>
                {
                    factoryCalls++;
                    return new FakeHost(Identity(request.ProcessId), (_, _) => new EtabsInvocation(6, []));
                },
                (host, token) => CaptureOneSuccessfulCall(host, request.DeadlineUtc, token),
                TestContext.Current.CancellationToken);

            var result = await handle.Completion;

            Assert.Equal(EtabsBrokerState.Rejected, result.State);
            Assert.Equal("ETABS.EVIDENCE_EXISTS", result.DiagnosticCode);
            Assert.Equal(0, factoryCalls);
            Assert.Equal("owned evidence", File.ReadAllText(path));
        }
        finally
        {
            Directory.Delete(testDirectory, recursive: true);
        }
    }

    [Fact]
    public async Task ExpiredDeadlineRejectsBeforeLeaseOrHostFactory()
    {
        var testDirectory = NewTestDirectory();
        try
        {
            var factoryCalls = 0;
            var request = Request(
                NextProcessId(),
                Path.Combine(testDirectory, "expired.json"),
                DateTimeOffset.UtcNow.AddSeconds(-1));
            var handle = new EtabsOperationBroker().Start(
                request,
                () =>
                {
                    factoryCalls++;
                    return new FakeHost(Identity(request.ProcessId), (_, _) => new EtabsInvocation(6, []));
                },
                (host, token) => CaptureOneSuccessfulCall(host, request.DeadlineUtc, token),
                TestContext.Current.CancellationToken);

            var result = await handle.Completion;

            Assert.Equal(EtabsBrokerState.Rejected, result.State);
            Assert.Equal("ETABS.CALL_TIMEOUT", result.DiagnosticCode);
            Assert.Equal(0, factoryCalls);
            Assert.False(File.Exists(result.EvidencePath));
            Assert.False(File.Exists(result.JournalPath));
        }
        finally
        {
            Directory.Delete(testDirectory, recursive: true);
        }
    }

    [Fact]
    public async Task DeniedMutationCannotDispatchOrPublishBrokerArtifact()
    {
        var testDirectory = NewTestDirectory();
        try
        {
            var processId = NextProcessId();
            var host = new FakeHost(
                Identity(processId),
                (_, _) => throw new InvalidOperationException("must not dispatch"));
            var request = Request(processId, Path.Combine(testDirectory, "denied.json"));
            var handle = new EtabsOperationBroker().Start(
                request,
                () => host,
                (ledgerHost, token) =>
                {
                    var denied = new EtabsGetterAdapter(ledgerHost).Read(
                        "Analyze.RunAnalysis",
                        [],
                        request.DeadlineUtc,
                        token);
                    throw new EtabsLiveGetterProbeException(
                        $"{denied.DiagnosticCode}: {denied.Message}");
                },
                TestContext.Current.CancellationToken);

            var result = await handle.Completion;
            await handle.Quiescence;

            Assert.Equal(EtabsBrokerState.Fenced, result.State);
            Assert.Equal("ETABS.CALL_FAILED", result.DiagnosticCode);
            Assert.Equal(0, host.InvokeCount);
            Assert.Equal(1, host.DisposeCount);
            Assert.False(File.Exists(result.EvidencePath));
            Assert.Equal(0, new FileInfo(result.JournalPath).Length);
        }
        finally
        {
            Directory.Delete(testDirectory, recursive: true);
        }
    }

    [Fact]
    public void RecordedCaptureRequiresExactBytesAndReplaysTypedValuesInOrder()
    {
        var testDirectory = NewTestDirectory();
        try
        {
            var processId = NextProcessId();
            var sourceHost = new FakeHost(Identity(processId), (_, _) => new EtabsInvocation(6, []));
            var capture = CaptureOneSuccessfulCall(
                sourceHost,
                DateTimeOffset.UtcNow.AddSeconds(10),
                TestContext.Current.CancellationToken);
            var path = Path.Combine(testDirectory, "recorded.json");
            File.WriteAllText(path, EtabsLiveGetterProbe.Serialize(capture));
            var sha256 = Sha256File(path);

            using var replay = EtabsRecordedGetterHost.Load(path, sha256);
            var result = new EtabsGetterAdapter(replay).Read(
                "SapModel.GetPresentUnits",
                [],
                DateTimeOffset.UtcNow.AddSeconds(10),
                TestContext.Current.CancellationToken);

            Assert.Equal(EtabsGetterState.Completed, result.State);
            Assert.Equal(6, result.RawCall!.DirectValue);
            replay.AssertComplete();
            File.AppendAllText(path, " ");
            Assert.Throws<InvalidDataException>(() => EtabsRecordedGetterHost.Load(path, sha256));
        }
        finally
        {
            Directory.Delete(testDirectory, recursive: true);
        }
    }

    [Fact]
    public async Task RecordedReplayCannotPublishUntilEverySourceCallIsConsumed()
    {
        var testDirectory = NewTestDirectory();
        try
        {
            var processId = NextProcessId();
            var sourceHost = new FakeHost(Identity(processId), (_, _) => new EtabsInvocation(6, []));
            var deadline = DateTimeOffset.UtcNow.AddSeconds(10);
            var capture = CaptureOneSuccessfulCall(
                sourceHost,
                deadline,
                TestContext.Current.CancellationToken);
            var sourcePath = Path.Combine(testDirectory, "source.json");
            File.WriteAllText(sourcePath, EtabsLiveGetterProbe.Serialize(capture));
            var request = Request(processId, Path.Combine(testDirectory, "incomplete.json"), deadline);
            var handle = new EtabsOperationBroker().Start(
                request,
                () => EtabsRecordedGetterHost.Load(sourcePath, Sha256File(sourcePath)),
                (_, _) => capture,
                TestContext.Current.CancellationToken);

            var result = await handle.Completion;
            await handle.Quiescence;

            Assert.Equal(EtabsBrokerState.Fenced, result.State);
            Assert.Equal("ETABS.CALL_FAILED", result.DiagnosticCode);
            Assert.Contains("unconsumed calls", result.Message, StringComparison.Ordinal);
            Assert.False(File.Exists(result.EvidencePath));
        }
        finally
        {
            Directory.Delete(testDirectory, recursive: true);
        }
    }

    [Fact]
    public async Task ConfiguredAcceptedCaptureReplaysThroughBroker()
    {
        var capturePath = Environment.GetEnvironmentVariable("WP10_REPLAY_CAPTURE_PATH");
        var captureSha = Environment.GetEnvironmentVariable("WP10_REPLAY_CAPTURE_SHA256");
        var evidencePath = Environment.GetEnvironmentVariable("WP10_REPLAY_EVIDENCE_PATH");
        if (string.IsNullOrWhiteSpace(capturePath) ||
            string.IsNullOrWhiteSpace(captureSha) ||
            string.IsNullOrWhiteSpace(evidencePath))
            return;

        using var identitySource = EtabsRecordedGetterHost.Load(capturePath, captureSha);
        var request = identitySource.RecordedRequest with { DeadlineUtc = DateTimeOffset.UtcNow.AddMinutes(2) };
        var brokerRequest = new EtabsBrokerRequest(
            $"wp10-03-offline-replay-{Guid.NewGuid():N}",
            identitySource.Identity.ProcessId,
            request.DeadlineUtc,
            evidencePath);
        EtabsRecordedGetterHost? replaySource = null;
        var handle = new EtabsOperationBroker().Start(
            brokerRequest,
            () => replaySource = EtabsRecordedGetterHost.Load(capturePath, captureSha),
            (host, token) =>
            {
                var result = EtabsLiveGetterProbe.Run(host, request, token);
                return result;
            },
            TestContext.Current.CancellationToken);

        var brokerResult = await handle.Completion.WaitAsync(
            TimeSpan.FromMinutes(2),
            TestContext.Current.CancellationToken);
        await handle.Quiescence.WaitAsync(TimeSpan.FromSeconds(10), TestContext.Current.CancellationToken);

        Assert.True(
            brokerResult.State == EtabsBrokerState.Completed,
            $"{brokerResult.DiagnosticCode}: {brokerResult.Message}");
        Assert.Equal(410, brokerResult.Artifact!.Content.Capture.Calls.Count);
        Assert.Equal(820, brokerResult.Artifact.Content.CallLedger.RecordCount);
        Assert.Equal(
            identitySource.RecordedPreflightSha256,
            brokerResult.Artifact.Content.Capture.Preflight.Sha256);
    }

    [Fact]
    public async Task ConfiguredExactEtabsHostCompletesOneFinalBrokerAcquisition()
    {
        var capturePath = Environment.GetEnvironmentVariable("WP10_LIVE_CAPTURE_PATH");
        var captureSha = Environment.GetEnvironmentVariable("WP10_LIVE_CAPTURE_SHA256");
        var evidencePath = Environment.GetEnvironmentVariable("WP10_LIVE_EVIDENCE_PATH");
        var processText = Environment.GetEnvironmentVariable("WP10_LIVE_PROCESS_ID");
        if (string.IsNullOrWhiteSpace(capturePath) ||
            string.IsNullOrWhiteSpace(captureSha) ||
            string.IsNullOrWhiteSpace(evidencePath) ||
            !int.TryParse(processText, out var processId))
            return;

        using var recorded = EtabsRecordedGetterHost.Load(capturePath, captureSha);
        using var process = Process.GetProcessById(processId);
        var identity = recorded.Identity with
        {
            ProcessId = processId,
            ProcessStartedUtc = new DateTimeOffset(process.StartTime.ToUniversalTime(), TimeSpan.Zero)
        };
        var request = recorded.RecordedRequest with { DeadlineUtc = DateTimeOffset.UtcNow.AddMinutes(2) };
        var handle = new EtabsOperationBroker().StartLive(
            Expectation(identity),
            request,
            $"wp10-03-live-{Guid.NewGuid():N}",
            evidencePath,
            TestContext.Current.CancellationToken);

        var brokerResult = await handle.Completion.WaitAsync(
            TimeSpan.FromMinutes(2),
            TestContext.Current.CancellationToken);
        await handle.Quiescence.WaitAsync(TimeSpan.FromSeconds(10), TestContext.Current.CancellationToken);

        Assert.True(
            brokerResult.State == EtabsBrokerState.Completed,
            $"{brokerResult.DiagnosticCode}: {brokerResult.Message}");
        Assert.Equal(410, brokerResult.Artifact!.Content.Capture.Calls.Count);
        Assert.Equal(820, brokerResult.Artifact.Content.CallLedger.RecordCount);
        Assert.Equal(
            brokerResult.Artifact.Content.Capture.Preflight.Sha256,
            brokerResult.Artifact.Content.Capture.Postflight.Sha256);
    }

    private static EtabsLiveGetterProbeCapture CaptureOneSuccessfulCall(
        IEtabsGetterHost host,
        DateTimeOffset deadline,
        CancellationToken cancellationToken)
    {
        var started = DateTimeOffset.UtcNow;
        var result = new EtabsGetterAdapter(host).Read(
            "SapModel.GetPresentUnits",
            [],
            deadline,
            cancellationToken);
        if (result.State != EtabsGetterState.Completed || result.RawCall is null)
            throw new EtabsLiveGetterProbeException(
                $"{result.DiagnosticCode}: {result.Message}");
        var protectedState = ProtectedState(host.Identity);
        return new(
            "LIVE_GETTER_MATRIX_COMPLETED_NO_GENERAL_COMPATIBILITY_CLAIM",
            started,
            DateTimeOffset.UtcNow,
            EtabsGetterMatrix.Sha256,
            host.Identity,
            new(
                "82",
                "B1",
                "Ground",
                [],
                ["117.(1.5DL+1.5LL)"],
                4,
                0,
                deadline),
            protectedState,
            protectedState,
            ["79", "78"],
            ["82"],
            "B230X450M20",
            "M25FE500",
            1,
            [result.RawCall]);
    }

    private static EtabsProtectedState ProtectedState(EtabsHostIdentity identity) => new(
        new string('f', 64),
        identity.ModelPath,
        identity.ModelBytes,
        identity.ModelModifiedUtc,
        identity.ModelSha256,
        true,
        6,
        6,
        "23.3.1",
        ["DEAD"],
        [4],
        [true],
        new ReadOnlyDictionary<string, bool>(new Dictionary<string, bool> { ["DEAD"] = false }),
        new ReadOnlyDictionary<string, bool>(new Dictionary<string, bool> { ["117.(1.5DL+1.5LL)"] = true }));

    private static EtabsBrokerRequest Request(
        int processId,
        string evidencePath,
        DateTimeOffset? deadline = null) => new(
            $"wp10-03-test-{processId}",
            processId,
            deadline ?? DateTimeOffset.UtcNow.AddSeconds(10),
            evidencePath);

    private static EtabsHostIdentity Identity(int processId) => new(
        processId,
        DateTimeOffset.Parse("2026-09-04T16:14:10.0327597Z"),
        "ETABS.exe",
        "23.3.1.4563",
        269168,
        new string('d', 64),
        "ETABSv1.dll",
        "ETABSv1, Version=1.0.0.0",
        "2.16.0.0",
        new string('a', 64),
        "ETABSv1.tlb",
        316292,
        new string('e', 64),
        "model.EDB",
        703208,
        DateTimeOffset.Parse("2026-09-04T16:23:41.1819254Z"),
        new string('b', 64),
        "23.3.1",
        true,
        6);

    private static EtabsHostExpectation Expectation(EtabsHostIdentity identity) => new(
        identity.ProcessId,
        identity.ProcessStartedUtc,
        identity.ExecutablePath,
        identity.ExecutableFileVersion,
        identity.ExecutableBytes,
        identity.ExecutableSha256,
        identity.ApiAssemblyPath,
        identity.ApiAssemblyIdentity,
        identity.ApiFileVersion,
        identity.ApiSha256,
        identity.TypeLibraryPath,
        identity.TypeLibraryBytes,
        identity.TypeLibrarySha256,
        identity.ModelPath,
        identity.ModelBytes,
        identity.ModelModifiedUtc,
        identity.ModelSha256,
        identity.EtabsApiVersion,
        identity.ModelLocked,
        identity.PresentUnits);

    private static string Sha256File(string path)
    {
        using var stream = File.OpenRead(path);
        return Convert.ToHexStringLower(SHA256.HashData(stream));
    }

    private static int NextProcessId() => Interlocked.Increment(ref _nextProcessId);

    private static string NewTestDirectory()
    {
        var path = Path.Combine(Path.GetTempPath(), $"wp10-03-{Guid.NewGuid():N}");
        Directory.CreateDirectory(path);
        return path;
    }

    private sealed class FakeHost(
        EtabsHostIdentity identity,
        Func<EtabsGetterDefinition, IReadOnlyList<object?>, EtabsInvocation> invoke) : IEtabsGetterHost
    {
        public EtabsHostIdentity CurrentIdentity { get; set; } = identity;
        public EtabsHostIdentity Identity => CurrentIdentity;
        public ApartmentState InvocationApartment { get; private set; } = ApartmentState.Unknown;
        public int DisposeCount { get; private set; }
        public int InvokeCount { get; private set; }
        public bool ThrowOnDispose { get; init; }

        public EtabsHostIdentity InspectIdentity() => CurrentIdentity;

        public EtabsInvocation Invoke(
            EtabsGetterDefinition definition,
            IReadOnlyList<object?> inputs,
            CancellationToken cancellationToken)
        {
            InvocationApartment = Thread.CurrentThread.GetApartmentState();
            InvokeCount++;
            return invoke(definition, inputs);
        }

        public void Dispose()
        {
            DisposeCount++;
            if (ThrowOnDispose)
                throw new InvalidOperationException("bounded cleanup failure");
        }
    }
}
