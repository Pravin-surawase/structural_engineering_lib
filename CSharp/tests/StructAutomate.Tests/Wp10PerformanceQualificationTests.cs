using System.Diagnostics;
using System.Security.Cryptography;
using System.Text.Json;
using StructuralEngineering.Analysis;
using StructuralEngineering.Contracts;
using StructuralEngineering.Etabs;
using Xunit;

namespace StructAutomate.Tests;

/// <summary>Opt-in PF9 evidence generator.  It never creates rows or substitutes a replay for a live getter.</summary>
public sealed class Wp10PerformanceQualificationTests
{
    [Fact]
    public void RetainedPf9SamplePreservesSnapshot()
    {
        var sample = Environment.GetEnvironmentVariable("WP10_PF9_REPLAY_SAMPLE");
        var output = Environment.GetEnvironmentVariable("WP10_PF9_REPLAY_DIRECTORY");
        Assert.SkipWhen(string.IsNullOrWhiteSpace(sample) || string.IsNullOrWhiteSpace(output), "Requires an exact retained PF9 sample and new external replay directory.");
        Assert.False(Directory.Exists(output)); Directory.CreateDirectory(output!);
        using var original = JsonDocument.Parse(File.ReadAllBytes(Path.Combine(sample!, "receipt.json")));
        var path = Path.Combine(sample!, "raw-capture.json"); var raw = File.ReadAllBytes(path);
        var watch = Stopwatch.StartNew();
        var result = EtabsCaptureProjector.Normalize(raw, Sha(raw), new("wp10-pf9", "wp10-shared-capture/v1", path,
            new Dictionary<string, SnapshotMaterialClassification>()));
        watch.Stop();
        Assert.True(result.Snapshot is not null, string.Join("; ", result.Diagnostics.Select(item => item.Message)));
        Assert.Equal(original.RootElement.GetProperty("canonical_snapshot_sha256").GetString(), result.Snapshot!.SnapshotSha256);
        File.WriteAllBytes(Path.Combine(output!, "receipt.json"), AnalysisSnapshotCodec.CanonicalJsonBytes(new
        {
            source_sample = sample, raw_file_sha256 = Sha(raw), snapshot_sha256 = result.Snapshot.SnapshotSha256,
            snapshot_identity_unchanged = true, normalization_ms = watch.Elapsed.TotalMilliseconds,
            members = result.Snapshot.Members.Count, rows = result.Snapshot.ActionRows.Count, pf9_acceptance = false
        }));
    }

    [Fact]
    public async Task ExactOwnedWorkloadRetainsEveryPerformanceSample()
    {
        var targetPath = Environment.GetEnvironmentVariable("WP10_PF9_TARGET_PATH");
        var directory = Environment.GetEnvironmentVariable("WP10_PF9_DIRECTORY");
        Assert.SkipWhen(string.IsNullOrWhiteSpace(targetPath) || string.IsNullOrWhiteSpace(directory),
            "Requires an exact owned ETABS target and a new external PF9 evidence directory.");
        Assert.False(Directory.Exists(directory));
        Directory.CreateDirectory(directory!);

        var size = (Environment.GetEnvironmentVariable("WP10_PF9_SIZE") ?? "").ToLowerInvariant();
        var workload = size switch { "small" => new Workload("SMALL", 100, 10_000, 5_000), "medium" => new Workload("MEDIUM", 1_000, 100_000, 30_000), _ => throw new ArgumentException("WP10_PF9_SIZE must be small or medium.") };
        var samples = ParseSamples(Environment.GetEnvironmentVariable("WP10_PF9_SAMPLES"));
        var profile = (Environment.GetEnvironmentVariable("WP10_PF9_PROFILE") ?? "bulk").ToLowerInvariant();
        Assert.True(profile is "batch" or "bulk" or "group", "WP10_PF9_PROFILE must be batch, bulk or group.");
        var transport = (Environment.GetEnvironmentVariable("WP10_PF9_TRANSPORT") ?? "gzip").ToLowerInvariant();
        Assert.True(transport is "gzip" or "rows", "WP10_PF9_TRANSPORT must be gzip or rows.");
        var targetBytes = File.ReadAllBytes(targetPath!);
        var target = JsonSerializer.Deserialize<EtabsProcessTarget>(targetBytes) ?? throw new InvalidDataException("PF9 target is invalid.");
        var targetSha = Sha(targetBytes);
        var token = TestContext.Current.CancellationToken;

        // Context acquisition is deliberately outside the PF9 timer and happens before the timed force acquisitions.
        var context = await ConnectContext(target, targetSha, directory!, token);
        var contextReadyWorkingSet = Process.GetCurrentProcess().WorkingSet64;
        var memberIds = context.Inventory.Frames.Where(frame => frame.DesignOrientation == EtabsFrameDesignOrientation.Beam)
            .Select(frame => frame.SourceFrameId).Order(StringComparer.Ordinal).ToArray();
        Assert.Equal(workload.Members, memberIds.Length);
        var frozen = new { schema_version = "wp10-pf9-frozen-input/v1", target_sha256 = targetSha,
            model_sha256 = context.Inventory.Source.ModelSha256, context_sha256 = context.ArtifactSha256,
            profile, transport, normalization_path = "durable-bound-memory/v1", required_members = workload.Members, required_rows = workload.Rows, samples };
        File.WriteAllBytes(Path.Combine(directory!, "frozen-input.json"), AnalysisSnapshotCodec.CanonicalJsonBytes(frozen));

        var baseline = await CaptureSample("baseline", 0, target, context.Inventory, memberIds, targetSha, profile, transport, directory!, contextReadyWorkingSet, token);
        var baselineFingerprint = baseline.PayloadFingerprint;
        var outcomes = new List<SampleOutcome> { baseline };
        if (baseline.Qualifies(workload))
            for (var index = 1; index <= samples; index++)
                outcomes.Add(await CaptureSample("sample", index, target, context.Inventory, memberIds, targetSha, profile, transport, directory!, contextReadyWorkingSet, token));

        var timed = outcomes.Skip(1).ToArray();
        double? p95 = timed.Length == samples ? timed.OrderBy(item => item.Pf9TotalMilliseconds).ElementAt((int)Math.Ceiling(timed.Length * .95) - 1).Pf9TotalMilliseconds : null;
        var payloadsMatchBaseline = outcomes.All(item => item.PayloadFingerprint == baselineFingerprint);
        var correctness = payloadsMatchBaseline && outcomes.All(item => item.Qualifies(workload));
        var memoryDelta = outcomes.Max(item => item.PeakContextReadyWorkingSetDeltaBytes);
        var acceptance = samples >= 10 && correctness && p95.HasValue && p95.Value <= workload.BudgetMilliseconds &&
            (workload.Name != "MEDIUM" || memoryDelta <= 512L * 1024 * 1024);
        File.WriteAllBytes(Path.Combine(directory!, "qualification-receipt.json"), AnalysisSnapshotCodec.CanonicalJsonBytes(new
        {
            schema_version = "wp10-pf9-performance-qualification/v1", pf9_acceptance = acceptance,
            pilot = samples < 10, workload = workload.Name, workload.Members, workload.Rows,
            samples_requested = samples, samples_retained = timed.Length, percentile_rule = "nearest-rank-ceil(n*0.95)",
            p95_total_ms = p95, budget_ms = workload.BudgetMilliseconds,
            maximum_incremental_working_set_bytes = memoryDelta,
            medium_workingset_budget_bytes = 512L * 1024 * 1024, baseline_payload_fingerprint = baselineFingerprint,
            source_target_sha256 = targetSha, context_sha256 = context.ArtifactSha256, profile, transport, normalization_path = "durable-bound-memory/v1",
            payloads_match_baseline = payloadsMatchBaseline, sample_directories = outcomes.Select(item => item.Directory).ToArray(), engineering_state = "not_evaluated"
        }));
        Assert.True(acceptance, "PF9 evidence was retained, but the workload did not meet the complete qualification acceptance rule.");
    }

    private static async Task<EtabsContextArtifact> ConnectContext(EtabsProcessTarget target, string targetSha, string directory, CancellationToken token)
    {
        var path = Path.Combine(directory, "context.json");
        var deadline = DateTimeOffset.UtcNow.AddMinutes(8);
        var handle = new EtabsContextOperationBroker().Start(new("pf9-context", target.ProcessId, deadline, path),
            () => EtabsReflectionGetterHost.AttachContext(EtabsHostDiscovery.Discover(target)),
            (host, cancellationToken) => EtabsContextCapture.Run(host, new(targetSha, deadline), cancellationToken), token);
        var result = await handle.Completion; await handle.Quiescence;
        Assert.True(result.State == EtabsContextWorkerState.Completed && result.Artifact is not null, result.Message);
        return result.Artifact!;
    }

    private static async Task<SampleOutcome> CaptureSample(string kind, int index, EtabsProcessTarget target, EtabsContextInventory context,
        IReadOnlyList<string> members, string targetSha, string profile, string transport, string root, long contextReadyWorkingSet, CancellationToken token)
    {
        var name = kind == "baseline" ? "baseline" : $"sample-{index:D2}";
        var directory = Path.Combine(root, name); Directory.CreateDirectory(directory);
        var evidencePath = Path.Combine(directory, "raw-capture.json");
        using var process = Process.GetCurrentProcess(); var workingSetBaseline = process.WorkingSet64; var peak = workingSetBaseline;
        using var samplingStop = new CancellationTokenSource();
        var sampler = Task.Run(async () => { while (!samplingStop.IsCancellationRequested) { process.Refresh(); peak = Math.Max(peak, process.WorkingSet64); await Task.Delay(10); } });
        EtabsBatchBrokerResult? result = null; EtabsSnapshotResult? normalized = null; string? encodedSnapshotSha = null; string? canonicalSnapshotSha = null;
        string? fingerprint = null; string? captureException = null; double? rawReadShaMilliseconds = null; double? normalizeMilliseconds = null; double? persistMilliseconds = null;
        var invocationTimings = new Dictionary<string, (int Count, double Milliseconds)>(StringComparer.Ordinal);
        var pf9Watch = Stopwatch.StartNew(); var brokerWatch = new Stopwatch();
        try
        {
            var deadline = DateTimeOffset.UtcNow.AddMinutes(8);
            brokerWatch.Start();
            var handle = new EtabsBatchOperationBroker().Start(new($"pf9-{name}", target.ProcessId, deadline, evidencePath),
                () => new MeasuredHost(profile == "group" ? EtabsReflectionGetterHost.AttachGroup(EtabsHostDiscovery.Discover(target))
                    : profile == "bulk" ? EtabsReflectionGetterHost.AttachBulk(EtabsHostDiscovery.Discover(target)) : EtabsReflectionGetterHost.AttachForces(EtabsHostDiscovery.Discover(target)), invocationTimings),
                (host, cancellationToken) => profile == "group"
                    ? EtabsLiveGetterProbe.RunGroup(host, new(targetSha, context, members, deadline), cancellationToken)
                    : profile == "bulk"
                    ? EtabsLiveGetterProbe.RunBulk(host, new(targetSha, context, members, deadline), cancellationToken)
                    : EtabsLiveGetterProbe.RunBatch(host, new(targetSha, context, members, deadline), cancellationToken), token,
                profile == "group" ? EtabsGroupGetterMatrix.Sha256 : profile == "bulk" ? EtabsBulkGetterMatrix.Sha256 : null);
            result = await handle.Completion; await handle.Quiescence; brokerWatch.Stop();
            if (result.Artifact is not null)
            {
                var rawWatch = Stopwatch.StartNew();
                var raw = File.ReadAllBytes(result.EvidencePath);
                var rawSha = Sha(raw); rawWatch.Stop(); rawReadShaMilliseconds = rawWatch.Elapsed.TotalMilliseconds;
                var normalizeWatch = Stopwatch.StartNew();
                normalized = EtabsCaptureProjector.Normalize(result.Artifact, raw, rawSha, new("wp10-pf9", "wp10-shared-capture/v1", result.EvidencePath,
                    new Dictionary<string, SnapshotMaterialClassification>()));
                normalizeWatch.Stop(); normalizeMilliseconds = normalizeWatch.Elapsed.TotalMilliseconds;
                if (normalized.Snapshot is not null)
                {
                    var snapshotPath = Path.Combine(directory, "snapshot.sasnap");
                    var persistWatch = Stopwatch.StartNew();
                    canonicalSnapshotSha = normalized.Snapshot.SnapshotSha256;
                    using (var stream = new FileStream(snapshotPath, FileMode.CreateNew, FileAccess.Write, FileShare.None, 1024 * 1024, FileOptions.WriteThrough))
                    {
                        if (transport == "rows") AnalysisSnapshotTransport.WriteCompact(stream, normalized.Snapshot);
                        else AnalysisSnapshotTransport.Write(stream, normalized.Snapshot);
                        stream.Flush(true);
                    }
                    using (var stored = File.OpenRead(snapshotPath))
                        encodedSnapshotSha = Convert.ToHexStringLower(SHA256.HashData(stored));
                    persistWatch.Stop(); persistMilliseconds = persistWatch.Elapsed.TotalMilliseconds;
                }
            }
        }
        catch (Exception exception) { captureException = $"{exception.GetType().Name}: {exception.Message}"; result ??= new(EtabsContextWorkerState.Fenced, "PF9.HARNESS_EXCEPTION", captureException, evidencePath, false, null); }
        finally { samplingStop.Cancel(); await sampler; process.Refresh(); peak = Math.Max(peak, process.WorkingSet64); }
        pf9Watch.Stop();
        var artifact = result?.Artifact;
        if (artifact is not null) fingerprint = PayloadFingerprint(artifact.Content.Capture.Calls);
        var postflight = artifact is not null && artifact.Content.Capture.Preflight.Sha256 == artifact.Content.Capture.Postflight.Sha256 && artifact.Content.HostIdentityBefore == artifact.Content.HostIdentityAfter;
        var outcome = new SampleOutcome(directory, fingerprint ?? "unavailable", pf9Watch.Elapsed.TotalMilliseconds, brokerWatch.Elapsed.TotalMilliseconds,
            rawReadShaMilliseconds, normalizeMilliseconds, persistMilliseconds, peak - workingSetBaseline, peak - contextReadyWorkingSet,
            captureException, result?.State == EtabsContextWorkerState.Completed, normalized?.Snapshot is not null, artifact?.Content.Capture.Members.Count ?? 0,
            normalized?.Snapshot?.ActionRows.Count ?? 0, result?.CleanupCompleted ?? false, postflight, canonicalSnapshotSha, encodedSnapshotSha);
        File.WriteAllBytes(Path.Combine(directory, "receipt.json"), AnalysisSnapshotCodec.CanonicalJsonBytes(new
        {
            schema_version = "wp10-pf9-performance-sample/v1", kind, index, pf9_acceptance = false,
            pf9_total_ms = outcome.Pf9TotalMilliseconds, production_broker_getter_com_total_ms = outcome.BrokerGetterComMilliseconds,
            raw_read_and_sha_ms = outcome.RawReadShaMilliseconds, offline_normalization_ms = outcome.NormalizeMilliseconds, encoded_snapshot_persistence_ms = outcome.PersistMilliseconds,
            host_invoke_and_com_transfer_ms = invocationTimings.Values.Sum(item => item.Milliseconds),
            getter_boundaries_including_durable_journal_ms = artifact?.Content.Capture.Calls.Sum(call => (call.CompletedUtc - call.StartedUtc).TotalMilliseconds),
            host_invocations = invocationTimings.OrderBy(item => item.Key, StringComparer.Ordinal).Select(item => new { operation = item.Key, count = item.Value.Count, milliseconds = item.Value.Milliseconds }).ToArray(),
            timing_note = "PF9 total includes the complete broker acquisition, raw evidence read/SHA-256, offline normalization, WriteThrough persistence, Flush(true), and encoded snapshot SHA-256.",
            working_set_baseline_bytes = workingSetBaseline, peak_process_working_set_bytes = peak, incremental_working_set_bytes = outcome.PeakWorkingSetDeltaBytes,
            context_ready_working_set_bytes = contextReadyWorkingSet, context_ready_incremental_working_set_bytes = outcome.PeakContextReadyWorkingSetDeltaBytes,
            payload_fingerprint = outcome.PayloadFingerprint, canonical_snapshot_sha256 = outcome.CanonicalSnapshotSha256, encoded_snapshot_sha256 = outcome.EncodedSnapshotSha256, normalized = outcome.Normalized,
            members = outcome.Members, rows = outcome.Rows, completed = outcome.Completed, cleanup_completed = outcome.CleanupCompleted,
            postflight_unchanged = outcome.PostflightUnchanged, capture_exception = outcome.CaptureException, result?.State, result?.DiagnosticCode, result?.Message,
            normalization_diagnostics = normalized?.Diagnostics, raw_evidence_path = result?.EvidencePath
        }));
        return outcome;
    }

    private static string PayloadFingerprint(IReadOnlyList<EtabsRawGetterCall> calls) => AnalysisSnapshotCodec.CanonicalDigest(calls.Select(call => new
    {
        operation = call.Operation, inputs = call.Inputs, direct_value = call.DirectValue, outputs = call.Outputs, return_code = call.CsiReturnCode
    }).ToArray());
    private static int ParseSamples(string? value) => string.IsNullOrWhiteSpace(value) ? 10 : int.TryParse(value, out var parsed) && parsed >= 1 ? parsed : throw new ArgumentException("WP10_PF9_SAMPLES must be a positive integer.");
    private static string Sha(byte[] bytes) => Convert.ToHexStringLower(SHA256.HashData(bytes));
    private sealed class MeasuredHost(IEtabsGetterHost inner, Dictionary<string, (int Count, double Milliseconds)> timings) : IEtabsGetterHost
    {
        public EtabsHostIdentity Identity => inner.Identity;
        public EtabsHostIdentity InspectIdentity() => inner.InspectIdentity();
        public EtabsInvocation Invoke(EtabsGetterDefinition definition, IReadOnlyList<object?> inputs, CancellationToken token)
        {
            var watch = Stopwatch.StartNew();
            try { return inner.Invoke(definition, inputs, token); }
            finally
            {
                watch.Stop(); timings.TryGetValue(definition.Operation, out var prior);
                timings[definition.Operation] = (prior.Count + 1, prior.Milliseconds + watch.Elapsed.TotalMilliseconds);
            }
        }
        public void Dispose() => inner.Dispose();
    }
    private sealed record Workload(string Name, int Members, int Rows, int BudgetMilliseconds);
    private sealed record SampleOutcome(string Directory, string PayloadFingerprint, double Pf9TotalMilliseconds, double BrokerGetterComMilliseconds,
        double? RawReadShaMilliseconds, double? NormalizeMilliseconds, double? PersistMilliseconds, long PeakWorkingSetDeltaBytes, long PeakContextReadyWorkingSetDeltaBytes,
        string? CaptureException, bool Completed, bool Normalized, int Members, int Rows, bool CleanupCompleted, bool PostflightUnchanged,
        string? CanonicalSnapshotSha256, string? EncodedSnapshotSha256)
    {
        public bool Qualifies(Workload workload) => CaptureException is null && Completed && Normalized && Members == workload.Members && Rows == workload.Rows &&
            CleanupCompleted && PostflightUnchanged && !string.IsNullOrWhiteSpace(CanonicalSnapshotSha256) && !string.IsNullOrWhiteSpace(EncodedSnapshotSha256);
    }
}
